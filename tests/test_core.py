from copy import deepcopy
import hashlib
import json
import unicodedata

import pytest

from saudi_legal.core import canonical, clean_body, deduplicate, make_record, normalize_search, source_id
from conftest import changed


def record(data, file_hash="f" * 64):
    return make_record(data, file_hash)


def test_faithful_arabic_body_matches_independent_expected_fixture(sample_data, expected_body):
    result = record(sample_data)
    assert result["text_ar"] == expected_body
    assert unicodedata.is_normalized("NFC", result["text_ar"])
    assert "عدد مرات التصفح" not in result["text_ar"]
    assert result["text_sha256"] == hashlib.sha256(expected_body.encode("utf-8")).hexdigest()


@pytest.mark.parametrize("literal", [
    "لا يجوز", "ولا تُحذف", "1234", "١٢٣٤٥", "1440/01/02", "03/04/2019",
    "المادة (12)", "الفقرة (٣)", "98.50", "0 أو ٠",
])
def test_roundtrip_keeps_numbers_dates_references_and_negation(sample_data, literal):
    result = record(sample_data)
    roundtrip = json.loads(canonical(result))
    assert literal in roundtrip["text_ar"]
    assert literal in result["text_ar"]


def test_search_normalization_is_separate_and_documented(sample_data):
    result = record(sample_data)
    assert "أُنشئ" in result["text_ar"]
    assert "قـانون" in result["text_ar"]
    assert "أُنشئ" not in result["text_search_ar"]
    assert "قانون" in result["text_search_ar"]
    assert result["text_search_ar"] != result["text_ar"]
    assert normalize_search("إِنَّ أَحْمَدَ قـال 123 و١٢٣") == "ان احمد قال 123 و١٢٣"
    assert "1234" in result["text_search_ar"]
    assert "1440/01/02" in result["text_search_ar"]


def test_dates_remain_source_strings_and_unknowns_stay_null(sample_data):
    result = record(sample_data)
    assert result["issued_hijri_raw"] == "1440/01/02"
    assert result["issued_gregorian_raw"] == "03/04/2019"
    assert result["published_hijri_raw"] == "1440/02/03"
    assert result["published_gregorian_raw"] == "04/05/2019"
    unknown = changed(sample_data, replacement=("تاريخ الإصدار", "عنوان اصطناعي"))
    result_unknown = record(unknown)
    assert result_unknown["issued_hijri_raw"] is None
    assert result_unknown["issued_gregorian_raw"] is None
    assert "issue_date_unknown" in result_unknown["quality_flags"]
    assert result_unknown["article_count"] is None


def test_id_is_deterministic_and_changes_with_legal_text(sample_data):
    baseline = record(sample_data)
    assert canonical(baseline) == canonical(record(deepcopy(sample_data)))
    version = record(changed(sample_data, replacement=("98.50", "98.51")))
    assert baseline["source_id"] == version["source_id"]
    assert baseline["document_id"] != version["document_id"]
    assert baseline["text_sha256"] != version["text_sha256"]
    later_capture = record(changed(sample_data, capture="2025-08-10T12:00:00Z"), "a" * 64)
    assert baseline["document_id"] == later_capture["document_id"]
    assert baseline["provenance"] != later_capture["provenance"]


@pytest.mark.parametrize("url", [
    None, "", "http://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1",
    "https://example.org/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1",
    "https://laws.boe.gov.sa.evil.invalid/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1",
    "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/2",
    "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/not-a-uuid/1",
    "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1?tracking=1",
    "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1#section",
])
def test_official_source_validation_rejects_ambiguous_or_untrusted_urls(url):
    assert source_id(url) is None


def test_valid_official_url_and_hash_mismatch(sample_data):
    assert source_id(sample_data["source"]["url"]) == "00000000-0000-4000-8000-000000000001"
    sample_data["full_text"] += " تغيير لم يُحدّث له المصدر"
    with pytest.raises(ValueError, match="captured_text_hash_mismatch"):
        record(sample_data)


@pytest.mark.parametrize("timestamp", [None, "not-a-date", "2025-08-09T12:00:00"])
def test_capture_requires_parseable_timezone(sample_data, timestamp):
    sample_data["source"]["captured_at_utc"] = timestamp
    with pytest.raises(ValueError, match="invalid_capture_timestamp"):
        record(sample_data)


@pytest.mark.parametrize("raw", ["نص بلا حد مثبت", "ن ص النظ ام نص ن ص النظ ام نص آخر"])
def test_missing_or_ambiguous_boundaries_are_rejected(raw):
    with pytest.raises(ValueError, match="missing_or_ambiguous_legal_body_marker"):
        clean_body(raw)


def test_exact_dedup_keeps_distinct_provenance_without_mutating_inputs(sample_data):
    first = record(sample_data, "1" * 64)
    second = record(changed(sample_data, source_number=2, capture="2025-08-10T12:00:00Z"), "2" * 64)
    before = canonical([first, second])
    merged = deduplicate([second, first, first])
    assert len(merged) == 1
    assert len(merged[0]["provenance"]) == 2
    assert {p["source_url"] for p in merged[0]["provenance"]} == {
        first["source_url"], second["source_url"],
    }
    assert canonical([first, second]) == before
    assert canonical(merged) == canonical(deduplicate([first, second]))


def test_near_versions_are_not_deduplicated(sample_data):
    original = record(sample_data)
    amended = record(changed(sample_data, replacement=("98.50", "98.51")))
    assert len(deduplicate([original, amended])) == 2


def test_malformed_source_is_an_explicit_per_file_rejection(sample_data):
    sample_data["source"] = ["malformed metadata"]
    with pytest.raises(ValueError, match="unverified_official_source_url"):
        record(sample_data)
