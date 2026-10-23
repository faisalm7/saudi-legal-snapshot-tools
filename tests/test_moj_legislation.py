"""Invented native MOJ-shaped fixtures, not legal text or actual source IDs."""
from copy import deepcopy
import json

import pytest

from saudi_legal.core import sha256
from saudi_legal.moj_legislation import capture_legislation, decode_legislation_response, legislation_html_text
from saudi_legal.text_release import prepare_moj_text, projection_sha256


URL="https://laws.moj.gov.sa/ar/legislation/SYNTHETIC_NOT_A_REAL_SOURCE"
TIME="2026-10-23T12:00:00Z"


@pytest.fixture
def response():
    return {"success":True,"model":{"serial":URL.rsplit("/",1)[1],"statuteVersionId":"SYNTHETIC_VERSION",
        "statuteId":"SYNTHETIC_DOCUMENT","name":"مثال اصطناعي لا يمثل تشريعاً","legalType":"مثال اصطناعي",
        "legalStatueName":"اصطناعي","statuteStructure":[
            {"id":"SYNTHETIC_CHAPTER","type":4,"name":"باب اصطناعي","text":"", "isCancelled":True,"isPublished":True,"items":[
                {"id":"SYNTHETIC_ARTICLE","type":1,"sequence":"المادة 1","name":None,
                 "text":"<p>لا يجوز اختلاق نص قانوني؛ 12 و1440/01/02 محفوظة.</p><table><tr><td><p>أ</p><p>ب</p></td><td>ج</td></tr></table>",
                 "isPublished":False,"isCancelled":False,"legalStatus":None}]},
            {"id":"SYNTHETIC_PLACEHOLDER","type":4,"text":".","items":[]},
            {"id":"SYNTHETIC_NOTE","type":1,"name":"قسم اصطناعي","text":"<p>ملاحظة اصطناعية.</p>"}]}}


def project(response):
    return decode_legislation_response(json.dumps(response,ensure_ascii=False).encode(),URL,TIME)


def test_hierarchy_literal_body_table_and_status_are_preserved(response):
    p=project(response);r=p["document"];a=p["article_spans"][0]
    assert "لا يجوز" in r["text_ar"] and "12 و1440/01/02" in r["text_ar"]
    assert "أ  ب\tج" in a["text_ar"] and "<table>" in a["text_html"]
    assert r["text_ar"][a["start"]:a["end"]]==a["text_ar"]
    assert a["source_is_parent_cancelled"] is True and a["source_is_published"] is False
    assert a["source_parent_ids"]==["SYNTHETIC_CHAPTER"]
    assert r["rights_basis"] is None and r["privacy_review"] is None
    assert sha256(r["source_sections_json"].encode())==r["source_text_sha256"]


@pytest.mark.parametrize("mutation",["wrong_locator","duplicate_section","unsupported_type","media","naive_time"])
def test_unknown_structure_or_identity_requires_review(response,mutation):
    stamp=TIME
    if mutation=="wrong_locator":response["model"]["serial"]="OTHER"
    if mutation=="duplicate_section":response["model"]["statuteStructure"].append(deepcopy(response["model"]["statuteStructure"][0]))
    if mutation=="unsupported_type":response["model"]["statuteStructure"][0]["type"]=99
    if mutation=="media":response["model"]["statuteStructure"][0]["text"]='<img src="invented.png">'
    if mutation=="naive_time":stamp="2026-10-23T12:00:00"
    with pytest.raises(ValueError):decode_legislation_response(json.dumps(response).encode(),URL,stamp)


def test_lists_nested_cells_and_negation_survive():
    text,_=legislation_html_text('<ol start="3"><li>لا حذف<ul><li>فرع</li></ul></li><li>نهاية</li></ol>')
    assert "3. لا حذف" in text and "• فرع" in text and "4. نهاية" in text
    with pytest.raises(ValueError,match="unsupported"):legislation_html_text('<math>unsupported</math>')


def test_local_projection_refuses_overwrite(tmp_path,response):
    src=tmp_path/"input.json";raw=json.dumps(response).encode();src.write_bytes(raw);out=tmp_path/"projected.json"
    result=capture_legislation(src,URL,TIME,out);before=out.read_bytes()
    assert result["articles"]==1 and not result["source_fetched"] and not result["publication_permission_inferred"]
    with pytest.raises(ValueError,match="existing"):capture_legislation(src,URL,TIME,out)
    assert src.read_bytes()==raw and out.read_bytes()==before


def package_inputs(tmp_path,response):
    p=project(response);r=p["document"]
    record=tmp_path/"laws.jsonl";record.write_text(json.dumps(r,ensure_ascii=False)+"\n")
    units=tmp_path/"units.jsonl";units.write_text("".join(json.dumps(u,ensure_ascii=False)+"\n" for u in p["source_spans"]))
    d={"document_id":r["document_id"],"text_sha256":r["text_sha256"],"source_file_sha256":r["source_file_sha256"],
       "projection_sha256":projection_sha256(r),
       "decision":"supported","quality_review":"pass","privacy_review":"not_personal_data",
       "rights_basis":"Invented fixture owned by the test author, MIT.","evidence_urls":["https://example.org/synthetic-fixture"],"reason":"Synthetic fixture only."}
    decisions=tmp_path/"decisions.json";decisions.write_text(json.dumps({"decisions":[d]}))
    return p,record,units,decisions


def test_reviewed_package_has_exact_spans_and_no_placeholder_rows(tmp_path,response):
    import datasets
    p,record,units,decisions=package_inputs(tmp_path,response)
    out=tmp_path/"public";result=prepare_moj_text(record,units,None,decisions,out)
    assert result["configuration_rows"]=={"laws":1,"article_spans":1,"source_sections":1}
    assert result["empty_structural_units_omitted_from_rows"]==1
    assert result["punctuation_only_structural_units_omitted_from_rows"]==1
    loaded=datasets.load_dataset(str(out),name="article_spans",split="corpus")
    assert loaded[0]["text_ar"]==p["article_spans"][0]["text_ar"]
    with pytest.raises(ValueError,match="new"):prepare_moj_text(record,units,None,decisions,out)


@pytest.mark.parametrize("fault",["span_offset","span_version","span_citation","span_sequence","span_html","source_hash","parent_citation","parent_title","unreviewed_field","decision_hash"])
def test_package_fails_before_writing_on_material_mismatch(tmp_path,response,fault):
    p,record,units,decisions=package_inputs(tmp_path,response)
    if fault.startswith("span_"):
        rows=p["source_spans"]
        if fault=="span_offset":rows[1]["start"]+=1
        elif fault=="span_version":rows[1]["source_version_id"]="OTHER"
        elif fault=="span_citation":rows[1]["source_url"]="https://example.org/unreviewed"
        elif fault=="span_sequence":rows[1]["source_sequence"]="المادة ألف"
        else:rows[1]["text_html"]="<p>unreviewed</p>"
        units.write_text("".join(json.dumps(u)+"\n" for u in rows))
    elif fault in ("source_hash","parent_citation","parent_title","unreviewed_field"):
        r=p["document"]
        if fault=="source_hash":r["source_sections_json"]="[]"
        elif fault=="parent_citation":r["source_url"]="https://example.org/unreviewed"
        elif fault=="parent_title":r["title"]="unreviewed title"
        else:r["private_local_path"]="SYNTHETIC_PRIVATE_PATH"
        record.write_text(json.dumps(r)+"\n")
    else:
        d=json.loads(decisions.read_text());d["decisions"][0]["text_sha256"]="0"*64;decisions.write_text(json.dumps(d))
    out=tmp_path/"public"
    with pytest.raises(ValueError):prepare_moj_text(record,units,None,decisions,out)
    assert not out.exists()
