"""Invented metadata projection tests; no private corpus text is used."""
from copy import deepcopy
import hashlib
import json

import pytest
from datasets import load_dataset
from saudi_legal.catalogue import project_records,export_catalogue,FIELDS
from saudi_legal.core import make_record,sha256


@pytest.fixture
def private_record(sample_data):
    raw=json.dumps(sample_data,ensure_ascii=False).encode()
    r=make_record(sample_data,sha256(raw))
    r.update(source_pdf_sha256='a'*64,source_pdf_pages=2)
    return r


def audit(r,status='deferred_missing_pdf'):
    return {'document_id':r['document_id'],'parse_status':'parsed','source_file_sha256':r['source_file_sha256'],
            'source_id':r['source_id'],'segmentation_status':status,'article_rows':r['article_count'],
            'content_review_flags':[],'filename_private':'invented-private-path','segmentation_evidence':{'heading':'private-heading'}}


def test_projection_never_copies_bodies_headings_private_paths_or_arbitrary_keys(private_record):
    r=private_record;r['private_note']='invented-private-sentinel'
    row=project_records([r],[audit(r)])[0]
    assert set(row)==set(FIELDS)
    assert row['document_id']==f"sa-boe-{r['source_id']}-ar"
    assert row['version_id']==r['document_id']
    assert row['verified_article_span_count'] is None
    assert row['captured_text_characters']==len(r['text_ar'])
    serialized=json.dumps(row,ensure_ascii=False)
    for forbidden in ('text_ar','text_search_ar','provenance','invented-private-path','private-heading','invented-private-sentinel'):
        assert forbidden not in serialized
    assert r['text_ar'] not in serialized


def test_hash_mismatch_or_duplicate_source_is_not_exported(private_record):
    r=private_record
    with pytest.raises(ValueError,match='Duplicate source|duplicate source'):
        project_records([r,r],[audit(r)])
    broken=deepcopy(r);broken['text_ar']+='changed'
    with pytest.raises(ValueError,match='body hash'):
        project_records([broken],[audit(broken)])
    bad=audit(r);bad['source_file_sha256']='0'*64
    with pytest.raises(ValueError,match='mismatched'):
        project_records([r],[bad])


def test_uncertainty_and_quality_codes_are_enforced(private_record):
    r=private_record;r['article_count']=0
    with pytest.raises(ValueError,match='remain null'):
        project_records([r],[audit(r)])
    r['article_count']=2;a=audit(r,'aligned');a['article_rows']=1
    with pytest.raises(ValueError,match='not supported'):
        project_records([r],[a])
    r['article_count']=None;a=audit(r);a['content_review_flags']=['Free text is forbidden']
    with pytest.raises(ValueError,match='controlled codes'):
        project_records([r],[a])


@pytest.mark.parametrize('key,value',[
    ('document_id','untrusted-body-as-version'),('source_pdf_sha256','body'*1000),
    ('source_pdf_pages',-1),('source_pdf_pages',True),('source_pdf_pages',2**31),
    ('issued_hijri_raw','body'*1000),('published_gregorian_raw','2025\ntext'),
    ('source_reported_status_at_capture','body'*1000),('source_reported_status_at_capture','x\rtext'),
    ('processing_version','body'*1000),('title','x\u2028text'),
    ('capture_timestamp_utc','2025-08-09T10:00:00+03:00'),('language','en'),
])
def test_projection_rejects_unbounded_or_unsupported_values(private_record,key,value):
    r=deepcopy(private_record);r[key]=value
    with pytest.raises(ValueError):
        project_records([r],[audit(r)])


def test_catalogue_native_load_and_existing_destination_preserved(tmp_path,private_record):
    r=private_record;records=tmp_path/'records.jsonl';audits=tmp_path/'audit.jsonl';out=tmp_path/'catalogue'
    records.write_text(json.dumps(r,ensure_ascii=False)+'\n');audits.write_text(json.dumps(audit(r))+'\n')
    summary=export_catalogue(records,audits,out)
    assert summary['catalogue_rows']==1 and summary['exported_legal_text_rows']==0
    (out/'README.md').write_text('---\nconfigs:\n- config_name: documents\n  data_files:\n  - split: catalogue\n    path: documents.parquet\n---\nInvented fixture metadata only.\n')
    ds=load_dataset(str(out),name='documents',split='catalogue')
    assert len(ds)==1 and ds[0]['source_id']==r['source_id']
    assert ds.features['verified_article_span_count'].dtype=='int32'
    before=(out/'documents.parquet').read_bytes()
    with pytest.raises(ValueError,match='existing work'):
        export_catalogue(records,audits,out)
    assert (out/'documents.parquet').read_bytes()==before
