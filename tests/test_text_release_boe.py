"""Publication projection checks using invented Arabic only."""
import json

import pytest

from saudi_legal.articles import segment_with_pdf_evidence
from saudi_legal.core import canonical, make_record, sha256
from saudi_legal.text_release import prepare_moj_text, projection_sha256


def inputs(tmp_path,sample_data):
    body=("المادة الأولى نص اصطناعي فقط؛ لا يجوز تحويل الرقم 12 أو التاريخ 1440/01/02. "
          "هذه كلمات مخترعة لا تصف قاعدة رسمية. "
          "المادة الثانية نص اصطناعي آخر يحفظ النفي والأرقام والحدود؛ لا يُعد قانوناً أو حكماً، "
          "وكل هذه العبارة مثال برمجي من تأليف صاحب الاختبار.")
    sample_data['full_text']='ن ص النظ ام '+body
    sample_data['source']['hash_sha256']=sha256(sample_data['full_text'].encode())
    r=make_record(sample_data,sha256(json.dumps(sample_data).encode()))
    r.update(source_pdf_sha256='a'*64,source_pdf_pages=1)
    spans,_=segment_with_pdf_evidence(r,'المادة الأولى\nنص اصطناعي\nالمادة الثانية\nنص اصطناعي','a'*64)
    assert len(spans)==2;r['article_count']=len(spans)
    laws=tmp_path/'boe.jsonl';laws.write_text(canonical(r))
    units=tmp_path/'boe-spans.jsonl';units.write_text(''.join(canonical(u) for u in spans))
    d={'document_id':r['document_id'],'source_file_sha256':r['source_file_sha256'],'text_sha256':r['text_sha256'],
        'projection_sha256':projection_sha256(r),'article_spans_sha256':sha256(units.read_bytes()),
        'decision':'supported','quality_review':'pass','privacy_review':'not_personal_data',
        'rights_basis':'Invented test fixture, MIT.','evidence_urls':['https://example.org/invented-fixture'],
        'reason':'Synthetic test only.'}
    registry=tmp_path/'decisions.json';registry.write_text(json.dumps({'decisions':[d]}))
    return r,spans,laws,units,registry


def test_boe_documents_and_spans_keep_source_evidence(tmp_path,sample_data):
    import datasets
    r,spans,laws,units,registry=inputs(tmp_path,sample_data);out=tmp_path/'public'
    summary=prepare_moj_text(None,None,None,registry,out,laws,units)
    assert summary['configuration_rows']=={'boe_documents':1,'boe_article_spans':2}
    ds=datasets.load_dataset(str(out),name='boe_article_spans',split='corpus')
    for a in ds:
        assert r['text_ar'][a['start_char']:a['end_char']]==a['text_ar']
        assert a['source_url']==r['source_url'] and a['evidence_pdf_sha256']==r['source_pdf_sha256']


@pytest.mark.parametrize('field,value',[('evidence_pdf_page',99),('evidence_pdf_line',999),('evidence_heading_raw','UNREVIEWED'),('boundary_method','UNREVIEWED')])
def test_boe_evidence_metadata_must_match_reviewed_projection(tmp_path,sample_data,field,value):
    _,spans,laws,units,registry=inputs(tmp_path,sample_data);spans[0][field]=value
    units.write_text(''.join(canonical(u) for u in spans));out=tmp_path/'public'
    with pytest.raises(ValueError):prepare_moj_text(None,None,None,registry,out,laws,units)
    assert not out.exists()
