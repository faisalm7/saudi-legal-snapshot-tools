"""Invented data only: one stored native field containing two complete acts."""
from copy import deepcopy
import json
import pytest
from saudi_legal.core import sha256
from saudi_legal.moj import validate_case_components
from saudi_legal.rights_gate import select_supported
from saudi_legal.text_release import schemas


HEADER_FIELDS=['appeal_number','appeal_hijri_date_raw','appeal_court_name','appeal_city']


def _record(unheaded=True):
    # One original field; no real PDF, court, publication or judicial wording.
    native='P'*191+'J'*9069+'\n\n'+'A'*3642+'T'*3
    offsets=[[191,9260],[9262,12904]]
    texts=['Invented first act for a synthetic test.','Invented second act for a synthetic test.']
    body='\n\n'.join(texts);pdf_hash=sha256(b'INVENTED PDF; NEVER FETCHED')
    text_hash=sha256(body.encode());doc='sa-moj-historical-pdf-'+pdf_hash
    components=[];derivations=[];stored=[];cursor=0
    for index,(text,span) in enumerate(zip(texts,offsets)):
        if index:cursor+=2
        level='appeal' if index else 'judgment';raw=native[span[0]:span[1]]
        c=dict(decision_level=level,start_char=cursor,end_char=cursor+len(text),
            text_characters=len(text),text_sha256=sha256(text.encode()),
            number=None if index else 'INVENTED_TRIAL',
            hijri_date_raw=None if index else '1400-01-01',
            court_name=None if index else 'INVENTED_COURT',city=None if index else 'INVENTED_CITY',
            gregorian_date_raw=None,source_pdf_pages=[2,3] if index else [1,2],
            complete_document_pages_inspected=[1,2,3])
        d=dict(decision_level=level,native_offsets=span,raw_body_sha256=sha256(raw.encode()),
            proposed_body_sha256=c['text_sha256'],proposed_offsets=[c['start_char'],c['end_char']],
            source_pdf_pages=c['source_pdf_pages'])
        n=dict(decision_level=level,source_native_start_char=span[0],source_native_end_char=span[1],
            raw_body_characters=len(raw),raw_body_sha256=d['raw_body_sha256'])
        components.append(c);derivations.append(d);stored.append(n);cursor=c['end_char']
    raw=native[191:12904]
    corrections=dict(source_pdf_sha256=pdf_hash,transcription_sha256=text_hash,
        stored_native_body_sha256=sha256(raw.encode()),complete_source_pages_reviewed=3,
        blank_pages=[],stored_native_body_offsets=offsets,
        active_component_body_derivations=derivations,stored_native_body_components=stored,
        whole_native_sha256=sha256(native.encode()),whole_native_characters=len(native),
        native_full_source_coverage=[dict(native_offsets=[a,b],role=role,
            sha256=sha256(native[a:b].encode()),selected_component_index=index)
            for a,b,role,index in [(0,191,'publisher_prefix',None),(191,9260,'judgment',1),
                (9260,9262,'inter_act_layout',None),(9262,12904,'appeal',2),
                (12904,12907,'terminal_layout',None)]])
    if unheaded:
        corrections['unheaded_appellate_context']=dict(
            kind='complete_unheaded_appellate_act_within_one_original_native_field_v1',
            absent_header_fields=HEADER_FIELDS.copy(),
            original_stored_fields=[dict(stored_index=0,decision_level='judgment',
                native_offsets=[191,12904],raw_body_characters=len(raw),raw_body_sha256=sha256(raw.encode()))],
            inter_act_separator=dict(native_offsets=[9260,9262],text='\n\n',sha256=sha256(b'\n\n')))
    row=dict(document_id=doc,version_id=doc+'-'+text_hash[:16],source_id='INVENTED_NOT_FETCHED',
        opaque_route_id='INVENTED_NOT_FETCHED',
        source_url='https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/INVENTED_NOT_FETCHED',
        source_family='moj_judgments',document_type='commercial_court_historical_judgment_and_appeal',
        source_pdf_sha256=pdf_hash,source_file_sha256=pdf_hash,source_pdf_pages=3,
        source_api_url=None,source_body_html_sha256=None,capture_timestamp_utc=None,
        extraction_method='official_historical_pdf_complete_visual_transcription_v1',
        source_identity_kind='frozen_official_opaque_route_and_exact_historical_PDF_no_model_UUID',
        source_capture_kind='historical_official_PDF_capture_date_unknown',source_component_count=2,
        has_judgment=True,has_appeal=True,text_ar=body,text_sha256=text_hash,
        judgment_number='INVENTED_TRIAL',judgment_hijri_date_raw='1400-01-01',
        court_name='INVENTED_COURT',city='INVENTED_CITY',judgment_gregorian_date_raw=None,
        appeal_number=None,appeal_hijri_date_raw=None,appeal_court_name=None,appeal_city=None,
        appeal_gregorian_date_raw=None,native_body_text_sha256=sha256(raw.encode()))
    if not unheaded:
        for key,value in zip(HEADER_FIELDS,['INVENTED_APPEAL','1400-01-02','INVENTED_APPEAL_COURT','INVENTED_CITY']):
            row[key]=value
        for child,parent in [('number','appeal_number'),('hijri_date_raw','appeal_hijri_date_raw'),
                             ('court_name','appeal_court_name'),('city','appeal_city')]:
            components[1][child]=row[parent]
    row['source_components_json']=json.dumps(components)
    row['source_corrections_json']=json.dumps(corrections)
    return row


def _changed(case):
    row=_record();c=json.loads(row['source_corrections_json']);cs=json.loads(row['source_components_json'])
    e=c['unheaded_appellate_context'];o=e['original_stored_fields'][0];s=e['inter_act_separator']
    changes={
        'missing_mode':lambda:c.pop('unheaded_appellate_context'),
        'wrong_mode':lambda:e.__setitem__('kind','unknown'),
        'null_mode':lambda:c.__setitem__('unheaded_appellate_context',None),
        'extra_mode_key':lambda:e.__setitem__('extra',True),
        'wrong_absent_headers':lambda:e.__setitem__('absent_header_fields',HEADER_FIELDS[:-1]),
        'reordered_absent_headers':lambda:e['absent_header_fields'].reverse(),
        'no_original_fields':lambda:e.__setitem__('original_stored_fields',[]),
        'two_original_fields':lambda:e['original_stored_fields'].append(deepcopy(o)),
        'wrong_original_level':lambda:o.__setitem__('decision_level','appeal'),
        'wrong_original_index':lambda:o.__setitem__('stored_index',1),
        'bool_original_index':lambda:o.__setitem__('stored_index',False),
        'extra_original_key':lambda:o.__setitem__('inferred',True),
        'wrong_original_start':lambda:o.__setitem__('native_offsets',[190,12904]),
        'wrong_original_end':lambda:o.__setitem__('native_offsets',[191,12903]),
        'wrong_original_length':lambda:o.__setitem__('raw_body_characters',12712),
        'bool_original_length':lambda:o.__setitem__('raw_body_characters',True),
        'wrong_original_hash':lambda:o.__setitem__('raw_body_sha256','f'*64),
        'one_LF':lambda:s.__setitem__('text','\n'),
        'space_separator':lambda:s.__setitem__('text','  '),
        'wrong_separator_hash':lambda:s.__setitem__('sha256','f'*64),
        'wrong_separator_frame':lambda:s.__setitem__('native_offsets',[9260,9263]),
        'extra_separator_key':lambda:s.__setitem__('inferred',True),
        'missing_coverage':lambda:c.pop('native_full_source_coverage'),
        'truncated_coverage':lambda:c['native_full_source_coverage'].pop(),
        'coverage_gap':lambda:c['native_full_source_coverage'][0].__setitem__('native_offsets',[0,190]),
        'coverage_overlap':lambda:c['native_full_source_coverage'][0].__setitem__('native_offsets',[0,192]),
        'coverage_reordered':lambda:c['native_full_source_coverage'].reverse(),
        'coverage_role':lambda:c['native_full_source_coverage'][3].__setitem__('role','publisher_prefix'),
        'coverage_cross_component':lambda:c['native_full_source_coverage'][1].__setitem__('selected_component_index',2),
        'coverage_selected_UI':lambda:c['native_full_source_coverage'][2].__setitem__('selected_component_index',1),
        'coverage_bool_component':lambda:c['native_full_source_coverage'][1].__setitem__('selected_component_index',True),
        'coverage_bad_hash':lambda:c['native_full_source_coverage'][0].__setitem__('sha256','bad'),
        'coverage_raw_hash':lambda:c['native_full_source_coverage'][3].__setitem__('sha256','f'*64),
        'coverage_separator_hash':lambda:c['native_full_source_coverage'][2].__setitem__('sha256','f'*64),
        'coverage_extra_key':lambda:c['native_full_source_coverage'][0].__setitem__('extra',True),
        'whole_bad_hash':lambda:c.__setitem__('whole_native_sha256','bad'),
        'whole_bad_length':lambda:c.__setitem__('whole_native_characters',12906),
        'whole_bool_length':lambda:c.__setitem__('whole_native_characters',True),
        'disjoint_mode_alias':lambda:c.__setitem__('native_component_source_basis','explicit_absolute_disjoint_native_segments_v1'),
        'segments_alias':lambda:c.__setitem__('stored_native_body_segments',[[[191,9260]],[[9262,12904]]]),
        'container_alias':lambda:c.__setitem__('stored_native_body_container_offsets',[[191,9260],[9262,12904]]),
        'raw_hash':lambda:c['stored_native_body_components'][1].__setitem__('raw_body_sha256','f'*64),
        'raw_width':lambda:c['stored_native_body_components'][1].__setitem__('raw_body_characters',3641),
        'raw_absolute_offset':lambda:c['stored_native_body_components'][1].__setitem__('source_native_start_char',0),
        'raw_derived_offset':lambda:c['active_component_body_derivations'][1].__setitem__('native_offsets',[9261,12904]),
        'raw_cross_component':lambda:c['stored_native_body_offsets'].__setitem__(1,[9000,12904]),
        'raw_bool_offset':lambda:c['stored_native_body_offsets'].__setitem__(0,[True,9260]),
        'proposed_hash':lambda:c['active_component_body_derivations'][1].__setitem__('proposed_body_sha256','f'*64),
        'proposed_offsets':lambda:c['active_component_body_derivations'][1].__setitem__('proposed_offsets',[1,3]),
        'proposed_pages':lambda:c['active_component_body_derivations'][1].__setitem__('source_pdf_pages',[1]),
        'proposed_level':lambda:c['active_component_body_derivations'][1].__setitem__('decision_level','judgment'),
        'source_pdf_hash':lambda:row.__setitem__('source_file_sha256','f'*64),
        'source_route':lambda:row.__setitem__('source_url',row['source_url'].replace('/1/','/0/')),
        'source_capture':lambda:row.__setitem__('capture_timestamp_utc','INVENTED_CAPTURE'),
        'source_API':lambda:row.__setitem__('source_api_url','https://example.invalid/NOT_FETCHED'),
        'source_HTML':lambda:row.__setitem__('source_body_html_sha256','f'*64),
        'source_document':lambda:row.__setitem__('document_id','INVENTED_WRONG_ID'),
        'source_version':lambda:row.__setitem__('version_id','INVENTED_WRONG_VERSION'),
        'source_family':lambda:row.__setitem__('source_family','unreviewed'),
        'wrong_type':lambda:row.__setitem__('document_type','commercial_court_historical_judgment'),
        'false_appeal':lambda:row.__setitem__('has_appeal',False),
        'false_judgment':lambda:row.__setitem__('has_judgment',False),
        'count':lambda:row.__setitem__('source_component_count',1),
        'component_level':lambda:cs[1].__setitem__('decision_level','judgment'),
        'component_M':lambda:cs[1].__setitem__('number','INVENTED_FAKE_HEADER'),
        'missing_component_M':lambda:cs[1].pop('city'),
        'component_Gregorian':lambda:cs[1].__setitem__('gregorian_date_raw','2000-01-01'),
        'component_pages':lambda:cs[1].__setitem__('source_pdf_pages',[4]),
        'incomplete_inspection':lambda:cs[1].__setitem__('complete_document_pages_inspected',[2,3]),
        'false_blank':lambda:c.__setitem__('blank_pages',[1]),
        'missing_judgment_header':lambda:row.__setitem__('court_name',None),
        'fake_appeal_Gregorian':lambda:row.__setitem__('appeal_gregorian_date_raw','2000-01-01'),
        'fake_judgment_Gregorian':lambda:row.__setitem__('judgment_gregorian_date_raw','2000-01-01'),
    }
    changes[case]();row['source_corrections_json']=json.dumps(c);row['source_components_json']=json.dumps(cs)
    return row


CASES=['missing_mode','wrong_mode','null_mode','extra_mode_key','wrong_absent_headers','reordered_absent_headers',
    'no_original_fields','two_original_fields','wrong_original_level','wrong_original_index','bool_original_index',
    'extra_original_key','wrong_original_start','wrong_original_end','wrong_original_length','bool_original_length',
    'wrong_original_hash','one_LF','space_separator','wrong_separator_hash','wrong_separator_frame','extra_separator_key',
    'missing_coverage','truncated_coverage','coverage_gap','coverage_overlap','coverage_reordered','coverage_role',
    'coverage_cross_component','coverage_selected_UI','coverage_bool_component','coverage_bad_hash','coverage_raw_hash',
    'coverage_separator_hash','coverage_extra_key','whole_bad_hash','whole_bad_length','whole_bool_length',
    'disjoint_mode_alias','segments_alias','container_alias','raw_hash','raw_width','raw_absolute_offset',
    'raw_derived_offset','raw_cross_component','raw_bool_offset','proposed_hash','proposed_offsets','proposed_pages',
    'proposed_level','source_pdf_hash','source_route','source_capture','source_API','source_HTML','source_document',
    'source_version','source_family','wrong_type','false_appeal','false_judgment','count','component_level','component_M',
    'missing_component_M','component_Gregorian','component_pages','incomplete_inspection','false_blank',
    'missing_judgment_header','fake_appeal_Gregorian','fake_judgment_Gregorian']


def test_unheaded_two_act_one_original_field_is_explicit_and_arrow_compatible():
    row=_record();before=deepcopy(row);validate_case_components(row);assert row==before
    import pyarrow as pa
    assert pa.Table.from_pylist([row],schema=schemas()['judgments']).num_rows==1
    c=json.loads(row['source_corrections_json']);e=c['unheaded_appellate_context']
    assert len(e['original_stored_fields'])==1
    assert c['stored_native_body_offsets']==[[191,9260],[9262,12904]]
    assert e['original_stored_fields'][0]['raw_body_characters']==12713
    assert all(row[k] is None for k in HEADER_FIELDS)


@pytest.mark.parametrize('case',CASES)
def test_unheaded_mode_rejects_unbound_or_fabricated_claims(case):
    with pytest.raises(ValueError):validate_case_components(_changed(case))


@pytest.mark.parametrize('key',HEADER_FIELDS)
@pytest.mark.parametrize('value',['INVENTED_FAKE_HEADER','',False])
def test_unheaded_mode_requires_all_four_explicit_null_headers(key,value):
    row=_record();row[key]=value
    with pytest.raises(ValueError):validate_case_components(row)


@pytest.mark.parametrize('key',HEADER_FIELDS)
def test_unheaded_mode_rejects_missing_instead_of_explicit_null_header(key):
    row=_record();row.pop(key)
    with pytest.raises(ValueError):validate_case_components(row)


def test_legacy_known_headers_and_contiguous_offsets_stay_supported():
    row=_record(False);before=deepcopy(row);validate_case_components(row);assert row==before


@pytest.mark.parametrize('key',HEADER_FIELDS)
def test_legacy_combined_mode_does_not_infer_missing_header_metadata(key):
    row=_record(False);row[key]=None
    with pytest.raises(ValueError):validate_case_components(row)


def test_source_claims_do_not_authorize_arbitrary_changed_words_or_reuse_old_decision():
    original=_record();row=deepcopy(original);row['text_ar']=row['text_ar'].replace('first','other')
    row['text_sha256']=sha256(row['text_ar'].encode());row['version_id']=row['document_id']+'-'+row['text_sha256'][:16]
    c=json.loads(row['source_corrections_json']);c['transcription_sha256']=row['text_sha256']
    row['source_corrections_json']=json.dumps(c)
    with pytest.raises(ValueError):validate_case_components(row)
    # Self-consistent review claims still need a new exact external decision.
    cs=json.loads(row['source_components_json']);cs[0]['text_sha256']=sha256(row['text_ar'][:cs[0]['end_char']].encode())
    c['active_component_body_derivations'][0]['proposed_body_sha256']=cs[0]['text_sha256']
    row['source_components_json']=json.dumps(cs);row['source_corrections_json']=json.dumps(c)
    validate_case_components(row)
    decision=dict(document_id=original['document_id'],decision='supported',text_sha256=original['text_sha256'],
        source_file_sha256=original['source_file_sha256'],quality_review='pass',privacy_review='pass',
        rights_basis='INVENTED TEST ONLY',evidence_urls=['https://example.invalid/NOT_FETCHED'],reason='INVENTED TEST ONLY')
    with pytest.raises(ValueError):select_supported([row],dict(decisions=[decision]))
