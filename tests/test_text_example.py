import argparse
from pathlib import Path
import runpy
import pytest

EXAMPLE=runpy.run_path(str(Path(__file__).parents[1]/"examples/texts.py"))

def test_matching_context_preserves_original_diacritics_tatweel_and_offsets():
    text="تمهيد "*100+"لَا يـَجُوز\nحذف النص."
    hit=EXAMPLE['matching_passage'](text,"لا يجوز",12)
    assert hit['matched_text']=="لَا يـَجُوز"
    assert text[hit['start_char']:hit['end_char']]==hit['matched_text']
    assert hit['passage']==text[hit['start_char']-12:hit['end_char']+12]
    assert hit['start_char']>400
    assert EXAMPLE['matching_passage']("نص آخر","لا يجوز") is None

@pytest.mark.parametrize("offset_fields", [("start_char", "end_char"), ("start", "end")])
def test_parent_inspection_checks_exact_source_membership(offset_fields):
    url="https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/00000000-0000-4000-8000-000000000001/1"
    body="افتتاح. المادة الأولى: لا يجوز الحذف. ختام."
    unit="المادة الأولى: لا يجوز الحذف."
    start=body.index(unit)
    row={'document_id':'synthetic','text_ar':unit,offset_fields[0]:start,offset_fields[1]:start+len(unit)}
    parent={'document_id':'synthetic','title':'مثال اصطناعي','source_url':url,'source_id':'00000000-0000-4000-8000-000000000001','text_ar':body,'text_sha256':'synthetic-test-only'}
    hit=EXAMPLE['matching_passage'](unit,'لا يجوز')
    result=EXAMPLE['parent_context'](row,parent,hit)
    assert result['matched_start_in_parent']==body.index('لا يجوز')
    assert result['passage']==body
    with pytest.raises(ValueError,match='parent slice'):
        EXAMPLE['parent_context'](dict(row,**{offset_fields[1]:row[offset_fields[1]]-1}),parent,hit)

def test_metadata_filters_keep_unknown_dates_unknown_and_use_active_court_fields():
    args=argparse.Namespace(source_id=None,document_type=None,court='التجارية',city='الرياض',captured_from='2026-10-01',captured_before='2026-11-01')
    row={'source_id':'invented','court_name':None,'appeal_court_name':'محكمة الاستئناف التجارية','appeal_city':'الرياض','capture_timestamp_utc':'2026-10-23T00:00:00Z'}
    assert EXAMPLE['metadata_matches'](row,args)
    assert not EXAMPLE['metadata_matches'](dict(row,capture_timestamp_utc=None),args)
    assert not EXAMPLE['metadata_matches'](dict(row,appeal_city='جدة'),args)

@pytest.mark.parametrize('bad_date',['20261024','2026-W43-6','2026-02-30'])
def test_capture_filter_rejects_dates_that_would_break_literal_comparison(monkeypatch,capsys,bad_date):
    import sys
    monkeypatch.setattr(sys,'argv',['texts.py','--captured-from',bad_date])
    with pytest.raises(SystemExit) as error:
        EXAMPLE['main']()
    assert error.value.code==2
    assert 'Capture dates must use YYYY-MM-DD' in capsys.readouterr().err
