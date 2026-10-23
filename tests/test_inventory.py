import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from saudi_legal.inventory import family, inspect_file, run_inventory


@pytest.mark.parametrize("path,expected", [
    ("cases/example.pdf", "moj_cases"),
    ("BOE_text_json/example.json", "boe"),
    ("processed/hadith_books/example.json", "hadith_books"),
    ("processed_repaired/moj_cases/example.json", "moj_cases"),
    ("qadha_pdfs/example.pdf", "qadha_folder_unverified"),
    ("books/example.pdf", "religious_texts_excluded"),
    ("aaoifi/example.pdf", "private_standards_excluded"),
])
def test_inventory_family_does_not_infer_unverified_provenance(path, expected):
    assert family(path) == expected


def test_inspect_hashes_bytes_and_recovers_source_metadata(tmp_path, sample_data):
    root = tmp_path / "BOE_text_json"
    root.mkdir()
    path = root / "fixture.json"
    raw = (json.dumps(sample_data, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(raw)
    result = inspect_file(path)
    assert result["sha256"] == hashlib.sha256(raw).hexdigest()
    assert result["source_url"] == sample_data["source"]["url"]
    assert result["source_id"] == "00000000-0000-4000-8000-000000000001"
    assert result["observed_capture_date"] == "2025-08-09T12:00:00Z"
    assert result["parse_status"] == "json_parsed"
    assert result["private_source_json"].encode("utf-8") == raw


@pytest.mark.parametrize("data,status", [(b"{broken", "json_parse_error"), (b"[]", "json_parse_error")])
def test_malformed_json_is_logged_not_raised(tmp_path, data, status):
    path = tmp_path / "invalid.json"
    path.write_bytes(data)
    result = inspect_file(path)
    assert result["parse_status"] == status
    assert result["sha256"] == hashlib.sha256(data).hexdigest()


@pytest.mark.parametrize("data,status", [
    (b"%PDF-1.4\nsynthetic test bytes only", "pdf_signature_verified_not_extracted"),
    (b"not a PDF", "invalid_pdf_signature"),
])
def test_pdf_signature_status_does_not_claim_successful_extraction(tmp_path, data, status):
    path = tmp_path / "fixture.pdf"
    path.write_bytes(data)
    assert inspect_file(path)["parse_status"] == status


def test_inventory_is_resumable_and_keeps_source_untouched(tmp_path, sample_data):
    source = tmp_path / "source"
    folder = source / "BOE_text_json"
    folder.mkdir(parents=True)
    file = folder / "fixture.json"
    raw = (json.dumps(sample_data, ensure_ascii=False) + "\n").encode("utf-8")
    file.write_bytes(raw)
    (folder / "invalid.json").write_text("{broken")
    (source / "cases").mkdir()
    (source / "cases" / "fixture.pdf").write_bytes(b"%PDF-1.4\nsynthetic")
    # A linked fixture must not cause another source entry or a hidden read.
    (folder / "alias.json").symlink_to(file)
    state = tmp_path / "private-state"
    assert run_inventory(source, state, timeout=60, workers=2) == 3
    first = (state / "manifest.jsonl").read_bytes()
    rows = [json.loads(line) for line in first.decode().splitlines()]
    assert sorted(row["parse_status"] for row in rows) == [
        "json_parse_error", "json_parsed", "pdf_signature_verified_not_extracted",
    ]
    assert all(not Path(row["relative_local_path"]).is_absolute() for row in rows)
    assert all(row["disposition"] == "deferred" for row in rows)
    assert file.read_bytes() == raw
    assert not any("private_source_json" in row for row in rows)
    staged = list((state / "source-json").glob("*.json"))
    assert len(staged) == 1
    assert staged[0].read_bytes() == raw
    # A partial final journal line cannot invalidate earlier completed checkpoints.
    with (state / "inventory-checkpoint.jsonl").open("a") as handle:
        handle.write('{"interrupted":')
    assert run_inventory(source, state, timeout=60, workers=2) == 3
    assert (state / "manifest.jsonl").read_bytes() == first
    assert file.read_bytes() == raw


@pytest.mark.parametrize("relative_state", [".", "private-state"])
def test_inventory_refuses_state_inside_original_collection(tmp_path, relative_state):
    root = tmp_path / "source"
    root.mkdir()
    with pytest.raises(ValueError, match="outside original collection"):
        run_inventory(root, root / relative_state)


def test_timed_out_file_does_not_stop_inventory_and_is_retried_on_resume(tmp_path, sample_data, monkeypatch):
    root = tmp_path / "source"
    folder = root / "BOE_text_json"
    folder.mkdir(parents=True)
    raw = json.dumps(sample_data, ensure_ascii=False)
    (folder / "slow.json").write_text(raw)
    (folder / "available.json").write_text(raw)
    state = tmp_path / "private-state"
    original_run = subprocess.run
    attempts = []

    # Failure is injected below; allow cold installed-Python startup for the
    # unrelated successful file rather than testing a machine-speed threshold.
    def simulated_timeout(command, **kwargs):
        attempts.append(Path(command[-1]).name)
        if Path(command[-1]).name == "slow.json":
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return original_run(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", simulated_timeout)
    assert run_inventory(root, state, timeout=60, workers=1) == 2
    rows = [json.loads(line) for line in (state / "manifest.jsonl").read_text().splitlines()]
    assert {row["parse_status"] for row in rows} == {"json_parsed", "read_timeout"}
    slow = next(row for row in rows if row["relative_local_path"].endswith("slow.json"))
    assert slow["sha256"] is None
    assert slow["reason"] == "isolated_read_timeout"
    monkeypatch.setattr(subprocess, "run", original_run)
    assert run_inventory(root, state, timeout=60, workers=1) == 2
    resumed = [json.loads(line) for line in (state / "manifest.jsonl").read_text().splitlines()]
    assert {row["parse_status"] for row in resumed} == {"json_parsed"}
    assert attempts == ["available.json", "slow.json"]


def test_transient_read_failure_is_retried_without_source_stat_change(tmp_path, sample_data, monkeypatch):
    root = tmp_path / "source"
    folder = root / "BOE_text_json"
    folder.mkdir(parents=True)
    source = folder / "fixture.json"
    source.write_text(json.dumps(sample_data, ensure_ascii=False))
    before = source.stat()
    state = tmp_path / "private-state"
    original_run = subprocess.run

    def transient_failure(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, stdout=b"", stderr=b"synthetic transient read failure")

    monkeypatch.setattr(subprocess, "run", transient_failure)
    assert run_inventory(root, state, timeout=60, workers=1) == 1
    failed = json.loads((state / "manifest.jsonl").read_text())
    assert failed["parse_status"] == "read_failure"
    assert failed["sha256"] is None
    after = source.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)

    monkeypatch.setattr(subprocess, "run", original_run)
    assert run_inventory(root, state, timeout=60, workers=1) == 1
    recovered = json.loads((state / "manifest.jsonl").read_text())
    assert recovered["parse_status"] == "json_parsed"
    assert recovered["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert (state / "source-json" / f"{recovered['sha256']}.json").is_file()


def test_existing_state_root_mismatch_is_rejected_before_cache_or_overwrite(tmp_path, sample_data, monkeypatch):
    first_root, other_root = tmp_path / "first-source", tmp_path / "other-source"
    raw = json.dumps(sample_data, ensure_ascii=False)
    for root in (first_root, other_root):
        (root / "BOE_text_json").mkdir(parents=True)
        (root / "BOE_text_json" / "fixture.json").write_text(raw)
    first_file = first_root / "BOE_text_json" / "fixture.json"
    other_file = other_root / "BOE_text_json" / "fixture.json"
    # Even matching relative names, bytes, and mtime cannot authorize cross-root cache reuse.
    st = first_file.stat()
    os.utime(other_file, ns=(st.st_atime_ns, st.st_mtime_ns))
    state = tmp_path / "private-state"
    assert run_inventory(first_root, state, timeout=60, workers=1) == 1
    before = {path.relative_to(state).as_posix(): path.read_bytes()
              for path in state.rglob("*") if path.is_file()}
    context = json.loads((state / "inventory-context.json").read_text())
    assert Path(context["original_root"]).resolve() == first_root.resolve()

    def no_inspection_allowed(*args, **kwargs):
        pytest.fail("A mismatched private context must fail before any file inspection")

    monkeypatch.setattr(subprocess, "run", no_inspection_allowed)
    with pytest.raises(ValueError, match="root|collection|context"):
        run_inventory(other_root, state, timeout=60, workers=1)
    after = {path.relative_to(state).as_posix(): path.read_bytes()
             for path in state.rglob("*") if path.is_file()}
    assert after == before
