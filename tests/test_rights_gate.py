"""A mechanical registry gate is not a substitute for real rights review."""
from copy import deepcopy
import hashlib
import json

import pytest
import yaml

from saudi_legal import core
from saudi_legal.rights_gate import prepare_public, select_supported
from conftest import changed


@pytest.fixture
def synthetic_records(sample_data):
    rows = []
    for number, kind in enumerate(["official_legal_instrument", "judgment", "circular"], 1):
        data = changed(sample_data, source_number=number, replacement=("98.50", f"98.5{number}"))
        raw = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
        row = core.make_record(data, hashlib.sha256(raw).hexdigest())
        row["document_type"] = kind
        rows.append(row)
    return rows


def supported(row):
    """Invented evidence for invented text; this is never an actual legal approval."""
    return {
        "document_id": row["document_id"], "decision": "supported",
        "text_sha256": row["text_sha256"], "source_file_sha256": row["source_file_sha256"],
        "rights_basis": "synthetic_test_fixture_created_for_testing_only",
        "evidence_urls": ["https://example.org/synthetic-fixture-rights-example"],
        "reason": "Entirely invented test text; invented review record exercises the gate only.",
        "quality_review": "pass", "privacy_review": "not_personal_data",
    }


def write_inputs(tmp_path, records, decisions):
    records_path, registry_path = tmp_path / "private-records.jsonl", tmp_path / "private-registry.json"
    records_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records))
    registry_path.write_text(json.dumps({"decisions": decisions}, ensure_ascii=False) + "\n")
    return records_path, registry_path


def test_private_processing_does_not_grant_rights(synthetic_records):
    assert core.VERSION == "0.5.0"
    assert core.RIGHTS is None
    assert all(row["rights_basis"] is None for row in synthetic_records)


def test_supported_selection_is_hash_bound_deterministic_and_does_not_mutate_input(synthetic_records):
    original = deepcopy(synthetic_records)
    decisions = [supported(row) for row in synthetic_records]
    registry_before = deepcopy(decisions)
    first = select_supported(list(reversed(synthetic_records)), {"decisions": list(reversed(decisions))})
    second = select_supported(synthetic_records, {"decisions": decisions})
    assert first == second
    assert [row["document_id"] for row in first] == sorted(row["document_id"] for row in synthetic_records)
    assert all(row["rights_basis"] == "synthetic_test_fixture_created_for_testing_only" for row in first)
    assert all(row["rights_evidence_urls"] == decisions[0]["evidence_urls"] for row in first)
    assert synthetic_records == original
    assert decisions == registry_before


@pytest.mark.parametrize("decision", [None, "unsupported", "pending", "withheld", "requires_permission"])
def test_missing_or_nonpositive_decisions_withhold_text(synthetic_records, decision):
    row = synthetic_records[0]
    entry = supported(row)
    entry["decision"] = decision
    assert select_supported([row], {"decisions": [entry]}) == []
    assert select_supported([row], {"decisions": []}) == []


@pytest.mark.parametrize("registry", [{}, {"decisions": None}, {"decisions": {}}, {"decisions": [None]}, {"decisions": [{}]}])
def test_malformed_registry_is_rejected(synthetic_records, registry):
    with pytest.raises(ValueError, match="decisions list|Malformed rights decision"):
        select_supported(synthetic_records, registry)


def test_duplicate_or_conflicting_decisions_and_input_ids_are_rejected(synthetic_records):
    row = synthetic_records[0]
    entry = supported(row)
    conflict = deepcopy(entry)
    conflict["decision"] = "withheld"
    for decisions in ([entry, entry], [entry, conflict]):
        with pytest.raises(ValueError, match="Duplicate or conflicting rights decisions"):
            select_supported([row], {"decisions": decisions})
    with pytest.raises(ValueError, match="Duplicate document ID"):
        select_supported([row, deepcopy(row)], {"decisions": [entry]})


@pytest.mark.parametrize("field", ["text_sha256", "source_file_sha256"])
def test_supported_decision_must_bind_both_exact_hashes(synthetic_records, field):
    row = synthetic_records[0]
    entry = supported(row)
    entry[field] = "0" * 64
    with pytest.raises(ValueError, match="bind exact input and output hashes"):
        select_supported([row], {"decisions": [entry]})


def test_tampered_body_is_rejected_even_when_registry_matches_stored_hash(synthetic_records):
    row = deepcopy(synthetic_records[0])
    entry = supported(row)
    row["text_ar"] = row["text_ar"].replace("لا يجوز", "يجوز", 1)
    with pytest.raises(ValueError, match="Candidate text hash mismatch"):
        select_supported([row], {"decisions": [entry]})


@pytest.mark.parametrize("field,value", [
    ("quality_review", None), ("quality_review", "not_reviewed"), ("quality_review", "fail"),
    ("privacy_review", None), ("privacy_review", "private"), ("privacy_review", "not_reviewed"),
])
def test_supported_rights_do_not_override_quality_or_privacy(synthetic_records, field, value):
    row = synthetic_records[0]
    entry = supported(row)
    entry[field] = value
    with pytest.raises(ValueError, match="do not replace quality or privacy review"):
        select_supported([row], {"decisions": [entry]})


@pytest.mark.parametrize("field,value", [
    ("rights_basis", None), ("rights_basis", " "),
    ("evidence_urls", None), ("evidence_urls", []),
    ("reason", None), ("reason", " "),
])
def test_positive_basis_evidence_and_reason_are_required(synthetic_records, field, value):
    row = synthetic_records[0]
    entry = supported(row)
    entry[field] = value
    with pytest.raises(ValueError, match="basis and evidence|required|reasoning note"):
        select_supported([row], {"decisions": [entry]})


@pytest.mark.parametrize("urls", [["http://example.org/policy"], ["file:///private-policy"], ["https://"], [7]])
def test_evidence_requires_nonempty_https_source_urls(synthetic_records, urls):
    row = synthetic_records[0]
    entry = supported(row)
    entry["evidence_urls"] = urls
    with pytest.raises(ValueError, match="HTTPS source URLs"):
        select_supported([row], {"decisions": [entry]})


def test_zero_eligible_records_creates_no_empty_public_dataset(tmp_path, synthetic_records):
    records, registry = write_inputs(tmp_path, synthetic_records, [])
    output = tmp_path / "must-not-exist"
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    with pytest.raises(ValueError, match="No records have supported rights"):
        prepare_public(records, registry, output)
    assert not output.exists()
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()} == before


def test_supported_record_with_unreviewed_type_fails_before_output_creation(tmp_path, synthetic_records):
    row = deepcopy(synthetic_records[0])
    row["document_type"] = "synthetic_unknown_family"
    records, registry = write_inputs(tmp_path, [row], [supported(row)])
    output = tmp_path / "must-not-exist"
    with pytest.raises(ValueError, match="Unreviewed document type"):
        prepare_public(records, registry, output)
    assert not output.exists()


@pytest.mark.parametrize("destination_kind", ["existing_directory", "symlink"])
def test_preparation_never_overwrites_existing_destination(tmp_path, synthetic_records, destination_kind):
    records, registry = write_inputs(tmp_path, synthetic_records, [supported(row) for row in synthetic_records])
    target = tmp_path / "existing"
    target.mkdir()
    sentinel = target / "preserve.bin"
    sentinel.write_bytes(b"must remain byte identical")
    output = target
    if destination_kind == "symlink":
        output = tmp_path / "output-link"
        output.symlink_to(target, target_is_directory=True)
    before = sentinel.read_bytes()
    with pytest.raises(ValueError, match="destination must be new"):
        prepare_public(records, registry, output)
    assert sentinel.read_bytes() == before
    assert [p.name for p in target.iterdir()] == ["preserve.bin"]


def test_synthetic_supported_types_load_natively_in_separate_configs(tmp_path, synthetic_records):
    records, registry = write_inputs(tmp_path, synthetic_records, [supported(row) for row in synthetic_records])
    output = tmp_path / "public-synthetic-only"
    summary = prepare_public(records, registry, output)
    assert summary["records"] == 3
    assert summary["configurations"] == {"laws": 1, "judgments": 1, "circulars": 1}
    assert summary["remote_publication"] is False
    assert summary["rights_registry_sha256"] == hashlib.sha256(registry.read_bytes()).hexdigest()
    card = (output / "README.md").read_text()
    meta = yaml.safe_load(card.split("---", 2)[1])
    assert meta["license"] == "other"
    assert sum(bool(config.get("default")) for config in meta["configs"]) == 1
    import datasets
    expected = {"laws": "official_legal_instrument", "judgments": "judgment", "circulars": "circular"}
    by_id = {row["document_id"]: row for row in synthetic_records}
    for config in meta["configs"]:
        name = config["config_name"]
        files = list(output.glob(config["data_files"][0]["path"]))
        assert len(files) == 1
        loaded = datasets.load_dataset(str(output.resolve()), name=name, split="corpus")
        assert len(loaded) == 1
        row = loaded[0]
        assert row["document_type"] == expected[name]
        assert row["text_ar"] == by_id[row["document_id"]]["text_ar"]
        assert row["text_sha256"] == hashlib.sha256(row["text_ar"].encode("utf-8")).hexdigest()
        assert row["rights_basis"] == "synthetic_test_fixture_created_for_testing_only"
        assert loaded.features["article_count"].dtype == "int32"


def test_withheld_record_and_its_registry_note_do_not_leak_into_output(tmp_path, synthetic_records):
    accepted, withheld = synthetic_records[:2]
    hidden = supported(withheld)
    hidden.update(decision="withheld", reason="synthetic-withheld-note-should-remain-private")
    records, registry = write_inputs(tmp_path, [accepted, withheld], [supported(accepted), hidden])
    output = tmp_path / "public-synthetic-only"
    assert prepare_public(records, registry, output)["records"] == 1
    preview = [json.loads(line) for line in (output / "preview.jsonl").read_text().splitlines()]
    assert [row["document_id"] for row in preview] == [accepted["document_id"]]
    exported_registry = json.loads((output / "rights-decisions.json").read_text())
    assert [row["document_id"] for row in exported_registry["decisions"]] == [accepted["document_id"]]
    assert "synthetic-withheld-note-should-remain-private" not in (output / "rights-decisions.json").read_text()


@pytest.mark.parametrize('invalid_hash', [None, '', 'not-a-source-hash', 'a' * 63])
def test_matching_invalid_source_hashes_do_not_establish_provenance(synthetic_records, invalid_hash):
    row = deepcopy(synthetic_records[0])
    row['source_file_sha256'] = invalid_hash
    decision = supported(row)
    with pytest.raises(ValueError, match='exact SHA-256 source-file hash'):
        select_supported([row], {'decisions': [decision]})


def test_null_then_known_date_across_shards_has_consistent_native_schema(tmp_path, synthetic_records):
    from datasets import load_dataset
    rows = []
    for n in range(101):
        r = deepcopy(synthetic_records[0])
        r['document_id'] = f'synthetic-schema-{n:03d}'
        r['published_hijri_raw'] = None if n < 100 else '1440/01/02'
        rows.append(r)
    records, registry = write_inputs(tmp_path, rows, [supported(r) for r in rows])
    out = tmp_path / 'synthetic-only'
    prepare_public(records, registry, out)
    ds = load_dataset(str(out), name='laws', split='corpus')
    assert len(ds) == 101
    assert ds.features['published_hijri_raw'].dtype == 'string'
    assert ds[0]['published_hijri_raw'] is None
    assert ds[100]['published_hijri_raw'] == '1440/01/02'


def test_unknown_private_field_is_rejected_before_any_public_output(tmp_path, synthetic_records):
    r = deepcopy(synthetic_records[0])
    r['private_local_path'] = 'invented-private-placeholder'
    records, registry = write_inputs(tmp_path, [r], [supported(r)])
    out = tmp_path / 'must-not-exist'
    with pytest.raises(ValueError, match='Unrecognized public record fields'):
        prepare_public(records, registry, out)
    assert not out.exists()
