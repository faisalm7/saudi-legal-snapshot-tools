"""Regressions for independently reproduced source-tree mutation hazards."""
import json
import os
from pathlib import Path

import pytest

from saudi_legal.cli import build
from saudi_legal.inventory import run_inventory
from conftest import changed


def snapshot_tree(root):
    """Include directory entries and link targets without dereferencing links."""
    snapshot = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[relative] = ("link", os.readlink(path))
        elif path.is_dir():
            snapshot[relative] = ("directory",)
        else:
            snapshot[relative] = ("file", path.read_bytes())
    return snapshot


def write_context(state, original):
    (state / "inventory-context.json").write_text(json.dumps({
        "original_root": str(original.resolve()), "pipeline_version": "0.1.0",
    }) + "\n")


def test_inventory_state_cannot_be_an_ancestor_of_original(tmp_path, sample_data):
    state = tmp_path / "private"
    original = state / "source-json"
    (original / "BOE_text_json").mkdir(parents=True)
    (original / "BOE_text_json" / "synthetic.json").write_text(json.dumps(sample_data, ensure_ascii=False))
    (original / "preserve.txt").write_bytes(b"original sentinel must remain unchanged")
    before = snapshot_tree(tmp_path)
    with pytest.raises(ValueError, match="outside original|must not contain"):
        run_inventory(original, state, timeout=10, workers=1)
    assert snapshot_tree(tmp_path) == before


def test_build_output_cannot_contain_original_or_delete_its_law_shards(stage, sample_data, tmp_path):
    state, _ = stage([sample_data])
    output = tmp_path / "public-parent"
    original = output / "data"
    original.mkdir(parents=True)
    (original / "laws-original.parquet").write_bytes(b"original source sentinel, not generated output")
    (original / "preserve.txt").write_bytes(b"other original sentinel")
    write_context(state, original)
    before = snapshot_tree(tmp_path)
    with pytest.raises(ValueError, match="outside original|must not contain"):
        build(state, output)
    assert snapshot_tree(tmp_path) == before


def test_build_rejects_output_data_symlink_before_deleting_original_files(stage, sample_data, tmp_path):
    state, _ = stage([sample_data])
    original = tmp_path / "original"
    original.mkdir()
    (original / "laws-original.parquet").write_bytes(b"original source sentinel")
    write_context(state, original)
    output = tmp_path / "public-output"
    output.mkdir()
    (output / "data").symlink_to(original, target_is_directory=True)
    before = snapshot_tree(tmp_path)
    with pytest.raises(ValueError, match="symlink"):
        build(state, output)
    assert snapshot_tree(tmp_path) == before


@pytest.mark.parametrize("operation", ["inventory", "build"])
def test_private_source_json_symlink_is_rejected_before_writes(tmp_path, sample_data, operation):
    original = tmp_path / "original"
    (original / "BOE_text_json").mkdir(parents=True)
    (original / "BOE_text_json" / "synthetic.json").write_text(json.dumps(sample_data, ensure_ascii=False))
    (original / "preserve.txt").write_bytes(b"original sentinel")
    state = tmp_path / "private-state"
    state.mkdir()
    (state / "source-json").symlink_to(original, target_is_directory=True)
    write_context(state, original)
    (state / "manifest.jsonl").write_text("")
    before = snapshot_tree(tmp_path)
    with pytest.raises(ValueError, match="symlink"):
        if operation == "inventory":
            run_inventory(original, state, timeout=10, workers=1)
        else:
            build(state, tmp_path / "public-output")
    assert snapshot_tree(tmp_path) == before


def test_frozen_rebuild_preserves_reviewed_exclusion_decisions_and_all_output_bytes(stage, sample_data, tmp_path):
    state, rows = stage([sample_data, changed(sample_data, replacement=("98.50", "98.51"))])
    exclusions = tmp_path / "exclusions.json"
    exclusions.write_text(json.dumps([{
        "source_file_sha256": rows[1]["sha256"], "reason": "synthetic_reviewed_exclusion",
    }]))
    output = tmp_path / "public-output"
    initial = build(state, output, exclusions=exclusions)
    assert initial["records"] == 1
    before = snapshot_tree(output)
    selected = tmp_path / "selected.json"
    selected.write_text((output / "input-hashes.json").read_text())
    rebuilt = build(state, output, selected_hashes=selected, exclusions=exclusions)
    assert rebuilt == initial
    assert snapshot_tree(output) == before
    decisions = [json.loads(line) for line in (output / "decisions.jsonl").read_text().splitlines()]
    assert len(decisions) == 2
    assert next(row for row in decisions if row["source_file_sha256"] == rows[1]["sha256"]) == {
        "source_file_sha256": rows[1]["sha256"], "disposition": "deferred",
        "reason": "synthetic_reviewed_exclusion",
    }
