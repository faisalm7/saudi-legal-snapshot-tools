"""Invented MOJ-shaped responses; no real judgment or source request."""
from copy import deepcopy
import json

import pytest

from saudi_legal.core import sha256
from saudi_legal.moj import capture_supreme, decode_supreme_response, decode_case_response, html_body_text


URL='https://laws.moj.gov.sa/ar/JudicialDecisionsList/3/SYNTHETIC_NOT_A_REAL_SOURCE'
TIME='2025-08-09T12:00:00Z'


@pytest.fixture
def response():
    return {'success':True,'model':{
        'id':'00000000-0000-4000-8000-000000000002','title':'مثال اصطناعي لا يمثل حكماً',
        'hasJudgment':True,'hasAppeal':False,'judgmentCourtName':'المحكمة العليا - مثال اصطناعي',
        'judgmentNumber':'0000','judgmentHijriiDate':None,'judgmentDate':None,'judgmentCityName':None,
        'judgmentTextofRulling':'<p>مثال اصطناعي: لا يجوز اختلاق نص قانوني.</p><p>الأرقام 12 و1440/01/02 محفوظة؛ &lt;اختبار&gt; فقط.</p>'}}


def test_literal_source_nodes_dates_numbers_and_negation_retained(response):
    raw=json.dumps(response,ensure_ascii=False).encode()
    r=decode_supreme_response(raw,URL,TIME)
    assert r['text_ar']=='مثال اصطناعي: لا يجوز اختلاق نص قانوني.\n\nالأرقام 12 و1440/01/02 محفوظة؛ <اختبار> فقط.'
    assert r['source_file_sha256']==sha256(raw)
    assert r['text_sha256']==sha256(r['text_ar'].encode())
    assert r['rights_basis'] is None and r['privacy_review'] is None
    assert r['judgment_hijri_date_raw'] is None


@pytest.mark.parametrize('key,value', [('hasAppeal',True),('hasJudgment',False),('judgmentFacts','extra substantive section'),('judgmentNarrationList',['extra']),('judgmentCourtName','محكمة أخرى')])
def test_different_source_shape_is_not_silently_truncated(response,key,value):
    response['model'][key]=value
    with pytest.raises(ValueError):decode_supreme_response(json.dumps(response).encode(),URL,TIME)


def test_citation_time_and_embedded_media_are_checked(response):
    raw=json.dumps(response).encode()
    with pytest.raises(ValueError,match='canonical'):decode_supreme_response(raw,'https://example.org/private',TIME)
    with pytest.raises(ValueError,match='UTC'):decode_supreme_response(raw,URL,'2025-08-09T12:00:00')
    with pytest.raises(ValueError,match='Embedded'):html_body_text('<p>نص</p><img src="invented.png">')
    assert html_body_text('<table><tr><td>أ</td><td>ب</td></tr><tr><td>ج</td><td>د</td></tr></table>')=='أ\tب\n\n\tج\tد'
    response['model']['judgmentTextofRulling']='<ol start="5"><li>لا يجوز الحذف</li><li>شرط اصطناعي</li></ol>'
    with pytest.raises(ValueError,match='markup'):decode_supreme_response(json.dumps(response).encode(),URL,TIME)


def test_local_adapter_preserves_inputs_and_never_overwrites(tmp_path,response):
    source=tmp_path/'response.json';raw=json.dumps(response,ensure_ascii=False).encode();source.write_bytes(raw)
    out=tmp_path/'capture.json';summary=capture_supreme(source,URL,TIME,out);before=out.read_bytes()
    assert source.read_bytes()==raw and not summary['source_fetched'] and not summary['publication_permission_inferred']
    with pytest.raises(ValueError,match='existing'):capture_supreme(source,URL,TIME,out)
    assert out.read_bytes()==before


def test_complete_dual_body_components_are_kept_with_exact_offsets(response):
    model=response['model'];model['hasAppeal']=True
    model['appealTextofRulling']='<p>مثال استئناف اصطناعي كامل؛ لا يُختصر.</p>'
    model['appealNumber']='SYNTHETIC_APPEAL_NUMBER';model['appealCourtName']='محكمة اصطناعية'
    url=URL.replace('/3/','/1/');raw=json.dumps(response,ensure_ascii=False).encode()
    record=decode_case_response(raw,url,TIME);components=json.loads(record['source_components_json'])
    assert record['source_component_count']==2 and record['document_type']=='judgment_and_appeal_publication_record'
    assert record['appeal_number']=='SYNTHETIC_APPEAL_NUMBER'
    assert record['text_ar']=='\n\n'.join(html_body_text(model[c['source_field']]) for c in components)
    for c in components:
        assert sha256(record['text_ar'][c['start_char']:c['end_char']].encode())==c['text_sha256']
        assert 'source_html' not in c
        assert sha256(model[c['source_field']].encode())==c['source_html_sha256']
    assert record['rights_basis'] is None and record['privacy_review'] is None


@pytest.mark.parametrize('field,value',[('judgmentFacts','extra facts'),('appealNarrationList',['extra']),('judgmentTextofRulling','<ol><li>مثال اصطناعي</li></ol>')])
def test_generic_adapter_rejects_unhandled_source_content(response,field,value):
    response['model'][field]=value
    with pytest.raises(ValueError):decode_case_response(json.dumps(response).encode(),URL,TIME)


def test_worked_example_only_opens_identity_matched_official_citations():
    from pathlib import Path
    import runpy
    validate=runpy.run_path(str(Path(__file__).parents[1]/'examples/texts.py'))['valid_citation']
    assert not validate({'source_url':'https://example.org/unreviewed','source_id':None})
    assert validate({'source_url':URL.replace('/3/','/0/'),'source_id':'00000000-0000-4000-8000-000000000002','opaque_route_id':URL.rsplit('/',1)[1]})
    assert not validate({'source_url':URL,'source_id':'00000000-0000-4000-8000-000000000002','opaque_route_id':'OTHER'})


def test_appeal_only_does_not_promote_inactive_judgment_metadata(response):
    model=response['model'];model.update(hasJudgment=False,hasAppeal=True,title='--',
        judgmentTextofRulling=None,judgmentNumber='STALE',judgmentHijriiDate='1444-01-01',
        appealTextofRulling='<p>مثال استئناف اصطناعي؛ لا تغيير.</p>',
        appealNumber='SYNTHETIC_APPEAL',appealCourtName='محكمة اصطناعية',appealHijriiDate='1444-02-03')
    record=decode_case_response(json.dumps(response,ensure_ascii=False).encode(),URL,TIME)
    assert record['title'] is None
    assert all(record[k] is None for k in ('judgment_number','judgment_hijri_date_raw','judgment_gregorian_date_raw','court_name','city'))
    assert record['appeal_number']=='SYNTHETIC_APPEAL' and record['appeal_hijri_date_raw']=='1444-02-03'
    assert record['text_ar']=='مثال استئناف اصطناعي؛ لا تغيير.'
    assert set(record['quality_flags'])=={'publisher_title_placeholder_retained_as_null','inactive_component_metadata_not_promoted'}
    assert json.loads(record['source_components_json'])[0]['number']=='SYNTHETIC_APPEAL'


def test_transparent_observed_span_preserves_all_words_numbers_negations(response):
    body='<p><span style="vertical-align: inherit;">مثال اصطناعي: لا يجوز </span><span style="vertical-align: inherit;">حذف 12 أو 1444/01/02.</span></p>'
    response['model']['judgmentTextofRulling']=body
    r=decode_case_response(json.dumps(response,ensure_ascii=False).encode(),URL,TIME)
    assert r['text_ar']=='مثال اصطناعي: لا يجوز حذف 12 أو 1444/01/02.'
    assert r['source_body_html_sha256']==sha256(body.encode())
    assert 'transparent_inline_vertical_align_span_removed' in r['quality_flags']
    response['model']['judgmentTextofRulling']='<p><span data-source-note="substantive">نص</span></p>'
    with pytest.raises(ValueError,match='span attributes'):
        decode_case_response(json.dumps(response).encode(),URL,TIME)
