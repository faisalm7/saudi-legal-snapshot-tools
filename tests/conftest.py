"""Offline synthetic inputs; tests never inspect the user's source collection."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture(autouse=True)
def offline_hugging_face(monkeypatch):
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("HF_DATASETS_OFFLINE", "1")
    monkeypatch.setenv("HF_DATASETS_DISABLE_PROGRESS_BARS", "1")


@pytest.fixture
def sample_data():
    return json.loads((FIXTURES / "synthetic_boe.json").read_text(encoding="utf-8"))


@pytest.fixture
def expected_body():
    return (FIXTURES / "expected_body.txt").read_text(encoding="utf-8").rstrip("\n")


def changed(data, *, replacement=None, source_number=None, capture=None):
    """Create another synthetic capture and independently recompute its input hash."""
    value = deepcopy(data)
    if replacement:
        value["full_text"] = value["full_text"].replace(*replacement)
    if source_number is not None:
        value["source"]["url"] = (
            "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/"
            f"00000000-0000-4000-8000-{source_number:012d}/1"
        )
    if capture:
        value["source"]["captured_at_utc"] = capture
    value["source"]["hash_sha256"] = hashlib.sha256(value["full_text"].encode("utf-8")).hexdigest()
    return value


@pytest.fixture
def stage(tmp_path):
    """A private-state fixture with realistic per-file decisions and no raw export."""
    def create(inputs, *, extra_rows=()):
        state = tmp_path / "private-state"
        state.mkdir(exist_ok=True)
        (state / "source-json").mkdir(exist_ok=True)
        rows = []
        for index, data in enumerate(inputs):
            raw = (json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
            digest = hashlib.sha256(raw).hexdigest()
            (state / "source-json" / f"{digest}.json").write_bytes(raw)
            rows.append({
                "relative_local_path": f"BOE_text_json/synthetic-{index:03d}.json",
                "sha256": digest, "parse_status": "json_parsed", "source_family": "boe",
                "availability": "local", "disposition": "deferred", "reason": "out_of_selected_scope",
                "file_size": len(raw), "source_id": None, "source_url": None,
                "observed_capture_date": None, "document_type": None,
            })
        rows.extend(deepcopy(list(extra_rows)))
        (state / "manifest.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
        return state, rows
    return create
