from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from saudi_legal.cli import build, verify
from conftest import changed


def write_card(output, path="data/laws-*.parquet"):
    (output / "README.md").write_text(
        "---\nlanguage:\n- ar\nlicense: other\nconfigs:\n"
        "- config_name: laws\n  default: true\n  data_files:\n"
        f"  - split: corpus\n    path: {path}\n---\n"
        "# Synthetic test dataset\nAll records are fabricated test fixtures.\n",
        encoding="utf-8",
    )


def extra_row(path, *, status="not_parsed", availability="local"):
    return {
        "relative_local_path": path, "sha256": None, "parse_status": status,
        "source_family": "moj_cases" if path.startswith("cases/") else "boe",
        "availability": availability, "disposition": "deferred", "reason": "out_of_selected_scope",
    }


def test_build_reconciles_inputs_and_preserves_duplicate_provenance(stage, sample_data, tmp_path):
    duplicate = changed(sample_data, source_number=2)
    amendment = changed(sample_data, replacement=("98.50", "98.51"))
    invalid = deepcopy(sample_data)
    invalid["source"]["hash_sha256"] = "0" * 64
    state, _ = stage(
        [sample_data, duplicate, amendment, invalid],
        extra_rows=[extra_row("cases/private-case.pdf"), extra_row(
            "BOE_text_json/unavailable.json", status="unavailable_not_read", availability="cloud_placeholder",
        )],
    )
    output = tmp_path / "dataset"
    summary = build(state, output)
    assert summary["discovered_files"] == 6
    assert summary["dispositions"] == {"accepted": 2, "deferred": 2, "duplicate": 1, "rejected": 1}
    assert sum(summary["dispositions"].values()) == 6
    assert summary["reconciliation_valid"] is True
    assert summary["eligible_input_json_files"] == 3
    assert summary["records"] == 2
    assert summary["exact_duplicate_text_or_file_inputs"] == 1
    assert summary["near_duplicate_pairs_flagged"] == 1
    rows = pq.read_table(output / "data" / "laws-00000.parquet").to_pylist()
    assert sorted(len(row["provenance"]) for row in rows) == [1, 2]
    assert len({row["document_id"] for row in rows}) == 2
    assert {row["article_count"] for row in rows} == {None}
    assert pq.read_schema(output / "data" / "laws-00000.parquet").field("article_count").type == pa.int32()
    assert all("ن ص النظ ام" not in row["text_ar"] for row in rows)
    assert "private-case" not in (output / "preview.jsonl").read_text()


def test_build_is_byte_deterministic_and_idempotent(stage, sample_data, tmp_path):
    state, _ = stage([sample_data, changed(sample_data, source_number=2)])
    output = tmp_path / "dataset"
    first = build(state, output)
    before = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    second = build(state, output)
    after = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    assert first == second
    assert before == after


def test_parquet_and_native_hf_card_loading(stage, sample_data, expected_body, tmp_path):
    state, _ = stage([sample_data])
    output = tmp_path / "dataset"
    build(state, output)
    write_card(output)
    result = verify(output)
    assert result["verified_shards"] == 1
    assert result["verified_rows"] == 1
    assert result["card_config_native_load"] is True
    import datasets
    corpus = datasets.load_dataset(str(output.resolve()), name="laws", split="corpus")
    assert corpus[0]["text_ar"] == expected_body
    assert corpus[0]["source_url"] == sample_data["source"]["url"]
    assert corpus[0]["text_sha256"] == hashlib.sha256(expected_body.encode("utf-8")).hexdigest()
    assert corpus.features["article_count"].dtype == "int32"


def test_card_path_mismatch_is_a_verification_error(stage, sample_data, tmp_path):
    state, _ = stage([sample_data])
    output = tmp_path / "dataset"
    build(state, output)
    write_card(output, "data/missing-*.parquet")
    with pytest.raises(ValueError, match="README config resolves to no Parquet files"):
        verify(output)


def test_verify_rejects_shard_text_tampering(stage, sample_data, tmp_path):
    state, _ = stage([sample_data])
    output = tmp_path / "dataset"
    build(state, output)
    write_card(output)
    shard = output / "data" / "laws-00000.parquet"
    original = pq.read_table(shard)
    values = original.to_pylist()
    values[0]["text_ar"] = values[0]["text_ar"].replace("98.50", "99.50")
    pq.write_table(pa.Table.from_pylist(values, schema=original.schema), shard)
    with pytest.raises(ValueError, match="Text hash mismatch"):
        verify(output)


def test_checkpoint_hash_failure_rejects_one_file_and_continues(stage, sample_data, tmp_path):
    state, rows = stage([sample_data, changed(sample_data, source_number=2, replacement=("98.50", "98.51"))])
    checkpoint = state / "source-json" / f"{rows[1]['sha256']}.json"
    checkpoint.write_bytes(checkpoint.read_bytes() + b" ")
    output = tmp_path / "dataset"
    summary = build(state, output)
    assert summary["records"] == 1
    assert summary["dispositions"] == {"accepted": 1, "rejected": 1}
    decisions = [json.loads(line) for line in (output / "decisions.jsonl").read_text().splitlines()]
    assert any(row["reason"] == "private_checkpoint_hash_mismatch" for row in decisions)


def test_frozen_selection_recomputes_dispositions_after_a_previous_build(stage, sample_data, tmp_path):
    state, rows = stage([sample_data, changed(sample_data, replacement=("98.50", "98.51"))])
    output = tmp_path / "dataset"
    assert build(state, output)["records"] == 2
    selected = tmp_path / "selected.json"
    selected.write_text(json.dumps([rows[0]["sha256"]]))
    summary = build(state, output, selected)
    assert summary["records"] == 1
    assert summary["dispositions"] == {"accepted": 1, "deferred": 1}
    manifest = [json.loads(line) for line in (state / "manifest.jsonl").read_text().splitlines()]
    excluded = next(row for row in manifest if row["sha256"] == rows[1]["sha256"])
    assert excluded["disposition"] == "deferred"
    assert excluded["reason"] == "not_in_frozen_release_input"


def test_empty_candidate_is_not_packaged(stage, sample_data, tmp_path):
    invalid = deepcopy(sample_data)
    invalid["source"]["hash_sha256"] = "0" * 64
    state, _ = stage([invalid])
    output = tmp_path / "dataset"
    with pytest.raises(ValueError, match="No eligible records"):
        build(state, output)
    assert not list(output.glob("data/*.parquet"))


def test_manual_exclusion_defers_exact_input_hash_and_records_reason(stage, sample_data, tmp_path):
    state, rows = stage([sample_data, changed(sample_data, replacement=("98.50", "98.51"))])
    exclusions = tmp_path / "exclusions.json"
    exclusions.write_text(json.dumps([{
        "source_file_sha256": rows[1]["sha256"], "reason": "synthetic_manual_review_deferral",
    }]))
    output = tmp_path / "dataset"
    summary = build(state, output, exclusions=exclusions)
    assert summary["records"] == 1
    assert summary["dispositions"] == {"accepted": 1, "deferred": 1}
    decisions = [json.loads(line) for line in (output / "decisions.jsonl").read_text().splitlines()]
    excluded = next(row for row in decisions if row["source_file_sha256"] == rows[1]["sha256"])
    assert excluded["disposition"] == "deferred"
    assert excluded["reason"] == "synthetic_manual_review_deferral"
    assert json.loads((output / "input-hashes.json").read_text()) == [rows[0]["sha256"]]


@pytest.mark.parametrize("failure", ["missing", "corrupted", "manually_excluded"])
def test_frozen_selection_refuses_partial_rebuild(stage, sample_data, tmp_path, failure):
    state, rows = stage([sample_data, changed(sample_data, replacement=("98.50", "98.51"))])
    selected = tmp_path / "selected.json"
    selected_values = [row["sha256"] for row in rows]
    exclusions = None
    if failure == "missing":
        selected_values.append("f" * 64)
    elif failure == "corrupted":
        checkpoint = state / "source-json" / f"{rows[1]['sha256']}.json"
        checkpoint.write_bytes(checkpoint.read_bytes() + b" ")
    else:
        exclusions = tmp_path / "exclusions.json"
        exclusions.write_text(json.dumps([{
            "source_file_sha256": rows[1]["sha256"], "reason": "synthetic_manual_review_deferral",
        }]))
    selected.write_text(json.dumps(selected_values))
    output = tmp_path / "dataset"
    with pytest.raises(ValueError, match="refusing a partial rebuild"):
        build(state, output, selected, exclusions)
    assert not list(output.glob("data/*.parquet"))


def test_cli_build_and_verify_are_runnable_offline(stage, sample_data, tmp_path):
    state, rows = stage([sample_data, changed(sample_data, replacement=("98.50", "98.51"))])
    exclusions = tmp_path / "exclusions.json"
    exclusions.write_text(json.dumps([{
        "source_file_sha256": rows[1]["sha256"], "reason": "synthetic_manual_review_deferral",
    }]))
    output = tmp_path / "dataset"
    built = subprocess.run(
        [sys.executable, "-m", "saudi_legal.cli", "build", "--state", str(state),
         "--output", str(output), "--exclusions", str(exclusions)],
        capture_output=True, text=True, timeout=30, check=True,
    )
    assert json.loads(built.stdout)["records"] == 1
    assert json.loads(built.stdout)["dispositions"] == {"accepted": 1, "deferred": 1}
    write_card(output)
    verified = subprocess.run(
        [sys.executable, "-m", "saudi_legal.cli", "verify", "--output", str(output)],
        capture_output=True, text=True, timeout=30, check=True,
    )
    assert json.loads(verified.stdout)["verified_rows"] == 1
