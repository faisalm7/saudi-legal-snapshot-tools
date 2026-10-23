"""Invented source reviews exercise corrections, evidence and checkpoint safety."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from saudi_legal.articles import pdf_headings, segment_with_pdf_evidence
from saudi_legal.core import MARKER, canonical, make_record, sha256
from saudi_legal.refine import refine_capture, refine_record


@pytest.fixture
def reviewed(sample_data):
    text=('المادة الأولى '+('نص اصطناعي لا يمثل حكما قانونيا. '*9)+
          ' المادة الثانية نص تجريبي غ ير منشور، كما في الفقرة من المادة الأولى. '+
          'المادة الثالثة. نهاية اصطناعية محفوظة للاختبار فقط.')
    data=deepcopy(sample_data);data['full_text']=MARKER+'\n'+text
    data['source']['hash_sha256']=sha256(data['full_text'].encode())
    r=make_record(data,'a'*64);r.update(source_pdf_sha256='b'*64,source_pdf_pages=1)
    a={'parse_status':'parsed','document_id':r['document_id'],'source_id':r['source_id'],
       'source_file_sha256':r['source_file_sha256'],'pdf_sha256':'b'*64}
    pdf='المادة الأولى\nنص تجريبي\nالمادة الثانية\nكما في الفقرة من\nالمادة الأولى.\nالمادة الثالثة.\nنهاية اصطناعية'
    h=pdf_headings(pdf)[2];start=r['text_ar'].index('غ ير')
    review={'document_id':r['document_id'],'source_file_sha256':'a'*64,'text_sha256':r['text_sha256'],
            'pdf_sha256':'b'*64,'source_url':r['source_url'],'reason':'Invented source comparison',
            'text_patches':[{'start_char':start,'end_char':start+4,'before':'غ ير','after':'غير',
                             'evidence_pdf_page':1,'reason':'Invented joined word evidence'}],
            'exclude_pdf_headings':[{k:h[k] for k in ('page','line','heading_pdf_raw')}]}
    return r,a,pdf,review


def test_reviewed_citation_exclusion_and_word_patch_preserve_source(reviewed):
    r,a,pdf,review=reviewed;before=deepcopy(r)
    assert segment_with_pdf_evidence(r,pdf,'b'*64)[1]['status']=='deferred_empty_article_body'
    rr,articles,aa,receipt=refine_record(r,a,pdf,review)
    assert r==before and rr['source_file_sha256']==r['source_file_sha256']
    assert rr['document_id']!=r['document_id'] and rr['text_sha256']==sha256(rr['text_ar'].encode())
    assert rr['text_ar']==r['text_ar'].replace('غ ير','غير')
    assert rr['article_count']==3 and aa['segmentation_status']=='aligned'
    assert articles[-1]['heading_raw']=='المادة الثالثة.'  # genuine terminal period retained
    for ar in articles:
        assert rr['text_ar'][ar['start_char']:ar['end_char']]==ar['text_ar']
        assert sha256(ar['text_ar'].encode())==ar['text_sha256']
    assert receipt['baseline_text_sha256']==r['text_sha256'] and not receipt['permission_inferred']
    assert rr['rights_basis'] is None


@pytest.mark.parametrize('field', ['source_file_sha256','text_sha256','pdf_sha256','source_url'])
def test_review_cannot_apply_to_another_source(reviewed,field):
    r,a,pdf,review=reviewed;review[field]='not-the-reviewed-source'
    with pytest.raises(ValueError):refine_record(r,a,pdf,review)


def test_wrong_patch_overlap_or_heading_locator_rejected(reviewed):
    r,a,pdf,review=reviewed
    wrong=deepcopy(review);wrong['text_patches'][0]['before']='wrong'
    with pytest.raises(ValueError,match='exact captured'):refine_record(r,a,pdf,wrong)
    wrong=deepcopy(review);wrong['text_patches']*=2
    with pytest.raises(ValueError,match='overlapping'):refine_record(r,a,pdf,wrong)
    wrong=deepcopy(review);wrong['exclude_pdf_headings'][0]['line']=999
    with pytest.raises(ValueError,match='exactly once'):refine_record(r,a,pdf,wrong)


def test_refinement_resume_is_deterministic_and_rejects_corruption(tmp_path,reviewed):
    r,a,pdf,review=reviewed;inp=tmp_path/'inputs';inp.mkdir();cache=inp/'pdf-text';cache.mkdir()
    records=inp/'records.jsonl';records.write_text(canonical(r));audits=inp/'audit.jsonl';audits.write_text(canonical(a))
    reviews=inp/'reviews.json';reviews.write_text(json.dumps({'reviews':[review]}))
    pdfpath=cache/('b'*64+'.layout.txt');pdfpath.write_text(pdf);pdfpath.with_suffix('.sha256').write_text(sha256(pdf.encode())+'\n')
    out=tmp_path/'refined'
    args=(records,audits,cache,reviews,out)
    assert refine_capture(*args)['article_spans']==3
    before={p.name:p.read_bytes() for p in out.glob('*.jsonl')}
    refine_capture(*args)
    assert before=={p.name:p.read_bytes() for p in out.glob('*.jsonl')}
    checkpoint=next((out/'checkpoints').glob('*.json'));saved=json.loads(checkpoint.read_text());saved['payload']['record']['text_ar']+='corrupt';checkpoint.write_text(json.dumps(saved))
    with pytest.raises(ValueError,match='integrity mismatch'):refine_capture(*args)
    existing=tmp_path/'unrelated';existing.mkdir();sentinel=existing/'keep.txt';sentinel.write_text('preserve')
    with pytest.raises(ValueError,match='unrelated'):refine_capture(records,audits,cache,reviews,existing)
    assert sentinel.read_text()=='preserve'


def test_path_like_source_identifier_is_not_used_as_checkpoint(tmp_path,reviewed):
    r,a,pdf,review=reviewed;r['source_id']='../../outside'
    with pytest.raises(ValueError,match='source identity'):refine_record(r,a,pdf,review)


def test_reviewed_official_image_evidence_is_explicit_and_versioned(reviewed):
    r,a,pdf,review=reviewed;p=review['text_patches'][0];p.pop('evidence_pdf_page')
    p.update(source_image_url='https://laws.boe.gov.sa/BoeLaws/Laws/GetViewerImage/?imageFileName=00000000-0000-4000-8000-000000000001_Page_004.jpg',
        source_image_sha256='c'*64,source_image_capture_timestamp_utc='2026-10-23T12:00:00Z',
        version_notice='Invented original-base source; this is not a real instrument or fetch')
    rr,_,_,receipt=refine_record(r,a,pdf,review)
    assert rr['text_sha256']!=r['text_sha256'] and receipt['text_patches'][0]['source_image_sha256']=='c'*64
    for key in ('source_image_sha256','source_image_capture_timestamp_utc','version_notice'):
        wrong=deepcopy(review);wrong['text_patches'][0].pop(key)
        with pytest.raises(ValueError):refine_record(r,a,pdf,wrong)
    wrong=deepcopy(review);wrong['text_patches'][0]['source_image_url']='https://example.org/unreviewed.jpg'
    with pytest.raises(ValueError):refine_record(r,a,pdf,wrong)
