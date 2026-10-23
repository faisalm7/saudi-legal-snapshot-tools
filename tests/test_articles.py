"""Synthetic source-evidence tests: exact body text and conservative boundaries."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from saudi_legal.articles import heading_key, pdf_headings, segment_with_pdf_evidence


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "article_alignment.json"


@pytest.fixture
def alignment_input():
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return {
        "record": {"document_id": value["document_id"], "text_ar": value["dom_body"]},
        "pdf_text": value["pdf_extracted_text"],
        "pdf_hash": hashlib.sha256(value["pdf_extracted_text"].encode("utf-8")).hexdigest(),
    }


def test_pdf_evidence_requires_isolated_lines_and_tracks_page_line(alignment_input):
    headings = pdf_headings(alignment_input["pdf_text"])
    assert [h["heading_pdf_raw"] for h in headings] == [
        "المادة الأولى", "المادة الثانية", "المادة السادسة والثلاثون",
    ]
    assert [(h["page"], h["line"]) for h in headings] == [(1, 2), (1, 4), (2, 2)]
    assert pdf_headings("سطر عام\nالمادة الثانية ليست هنا عنوانًا منفردًا\nسطر آخر") == []


def test_unique_mapping_preserves_exact_offsets_hashes_numbers_and_negations(alignment_input):
    source = alignment_input["record"]
    before = deepcopy(source)
    rows, evidence = segment_with_pdf_evidence(source, alignment_input["pdf_text"], alignment_input["pdf_hash"])
    assert evidence["status"] == "aligned"
    assert evidence["full_ordered_alignment_count_capped_at_two"] == 1
    assert evidence["article_rows"] == len(rows) == 3
    assert source == before
    first_heading = source["text_ar"].index("المادة الأُولى:")
    assert evidence["preamble_end_char"] == first_heading
    assert rows[0]["start_char"] == first_heading
    assert "".join(row["text_ar"] for row in rows) == source["text_ar"][first_heading:]
    assert [row["article_position"] for row in rows] == [1, 2, 3]
    for row in rows:
        assert row["text_ar"] == source["text_ar"][row["start_char"]:row["end_char"]]
        assert row["heading_raw"] == source["text_ar"][row["start_char"]:row["body_start_char"]]
        assert row["start_char"] < row["body_start_char"] < row["end_char"]
        assert row["text_sha256"] == hashlib.sha256(row["text_ar"].encode("utf-8")).hexdigest()
        assert row["evidence_pdf_sha256"] == alignment_input["pdf_hash"]
    for left, right in zip(rows, rows[1:]):
        assert left["end_char"] == right["start_char"]
    combined = "".join(row["text_ar"] for row in rows)
    for literal in ["لا يجوز", "ولا تُحذف", "1234", "١٢٣٤", "1440/01/02", "03/04/2019", "(36)", "(٣)"]:
        assert literal in combined


def test_word_after_heading_is_not_consumed_by_alignment_vocabulary(alignment_input):
    source = alignment_input["record"]
    rows, _ = segment_with_pdf_evidence(source, alignment_input["pdf_text"], alignment_input["pdf_hash"])
    second = rows[1]
    assert second["heading_raw"] == "المادة الثانية"
    body = source["text_ar"][second["body_start_char"]:second["end_char"]]
    assert body.lstrip().startswith("بعد هذا العنوان")
    assert "ولا تُحذف كلمة بعد" in body


def test_ordinal_beyond_eleven_and_alignment_normalization_do_not_rewrite_body(alignment_input):
    rows, _ = segment_with_pdf_evidence(alignment_input["record"], alignment_input["pdf_text"], alignment_input["pdf_hash"])
    assert rows[0]["heading_raw"] == "المادة الأُولى:"
    assert rows[0]["evidence_heading_raw"] == "المادة الأولى"
    assert heading_key(rows[0]["heading_raw"]) == heading_key(rows[0]["evidence_heading_raw"])
    assert rows[2]["heading_raw"] == "المادة السادسة والثلاثون:"
    assert rows[2]["evidence_pdf_page"] == 2
    assert rows[2]["evidence_pdf_line"] == 2
    assert rows[2]["text_ar"].startswith("المادة السادسة والثلاثون: لا يجوز")


def test_citations_remain_body_text_when_full_heading_sequence_is_unique(alignment_input):
    source = alignment_input["record"]["text_ar"]
    rows, evidence = segment_with_pdf_evidence(alignment_input["record"], alignment_input["pdf_text"], alignment_input["pdf_hash"])
    assert evidence["full_ordered_alignment_count_capped_at_two"] == 1
    # Preamble's article-two reference occurs before the first actual heading.
    assert rows[0]["start_char"] > source.index("المادة الثانية")
    # Later references cannot complete a second ordered 1,2,36 mapping.
    assert "الإشارة إلى المادة السادسة والثلاثون مجرد إحالة" in rows[0]["text_ar"]
    assert "الإشارة إلى المادة الأولى كما كُتبت" in rows[1]["text_ar"]
    assert rows[1]["start_char"] == source.index("المادة الثانية بعد")
    assert rows[2]["start_char"] == source.index("المادة السادسة والثلاثون:")


def test_same_key_citation_creating_two_full_mappings_defers_all_rows(alignment_input):
    record = deepcopy(alignment_input["record"])
    record["text_ar"] = record["text_ar"].replace(
        "المادة الثانية بعد", "إحالة إلى المادة الثانية في منتصف الجسم.\nالمادة الثانية بعد",
    )
    rows, evidence = segment_with_pdf_evidence(record, alignment_input["pdf_text"], alignment_input["pdf_hash"])
    assert rows == []
    assert evidence["status"] == "deferred_ambiguous_or_mismatched_heading_sequence"
    assert evidence["full_ordered_alignment_count_capped_at_two"] == 2


@pytest.mark.parametrize("pdf_text", ["", "سطر بلا عنوان مثبت", "المادة الأولى نصها على السطر نفسه"])
def test_no_isolated_pdf_heading_produces_no_invented_article_rows(alignment_input, pdf_text):
    before = deepcopy(alignment_input["record"])
    rows, evidence = segment_with_pdf_evidence(before, pdf_text, alignment_input["pdf_hash"])
    assert rows == []
    assert evidence["status"] == "deferred_no_isolated_pdf_headings"
    assert before == alignment_input["record"]


def test_missing_dom_heading_defers_instead_of_partially_segmenting(alignment_input):
    record = deepcopy(alignment_input["record"])
    record["text_ar"] = record["text_ar"].replace("المادة السادسة والثلاثون:", "عنوان اصطناعي آخر:")
    rows, evidence = segment_with_pdf_evidence(record, alignment_input["pdf_text"], alignment_input["pdf_hash"])
    assert rows == []
    assert evidence["status"] == "deferred_ambiguous_or_mismatched_heading_sequence"


def test_empty_article_body_defers_whole_table():
    record = {"document_id": "synthetic-empty-body", "text_ar": "المادة الأولى المادة الثانية لا يجوز حذف هذه العبارة."}
    rows, evidence = segment_with_pdf_evidence(record, "المادة الأولى\nالمادة الثانية", "a" * 64)
    assert rows == []
    assert evidence["status"] == "deferred_empty_article_body"


def test_same_synthetic_inputs_are_deterministic(alignment_input):
    arguments = (alignment_input["record"], alignment_input["pdf_text"], alignment_input["pdf_hash"])
    assert segment_with_pdf_evidence(*arguments) == segment_with_pdf_evidence(*arguments)
