"""Invented data only: strict absolute native pieces, never fetched or published."""
from copy import deepcopy
import json
import pytest
from saudi_legal.core import sha256
from saudi_legal.moj import validate_case_components
from saudi_legal.rights_gate import select_supported
from saudi_legal.text_release import schemas


def _record(disjoint=True):
    # Geometry includes a 62-character excluded interval. No real source wording.
    native='P'*186+'ج'*8209+'G'*88+'د'*130+'U'*62+'ذ'*3155+'T'*3
    segments=[[[186,8395]],[[8483,8613],[8675,11830]]] if disjoint else [[[186,8395]],[[8483,11830]]]
    ranges=[(0,186,None),(186,8395,1),(8395,8483,None),(8483,8613,2),
            (8613,8675,None),(8675,11830,2),(11830,11833,None)] if disjoint else [
            (0,186,None),(186,8395,1),(8395,8483,None),(8483,11830,2),(11830,11833,None)]
    texts=['حكم اصطناعي مخترع للاختبار فقط','استئناف اصطناعي مخترع للاختبار فقط']
    body='\n\n'.join(texts);body_hash=sha256(body.encode())
    pdf_hash=sha256(b'SYNTHETIC PDF; NOT A REAL JUDGMENT')
    doc='sa-moj-historical-pdf-'+pdf_hash
    components=[];derivations=[];stored=[];raw_parts=[];offset=0
    for i,(text,pieces) in enumerate(zip(texts,segments)):
        if i:offset+=2
        raw=''.join(native[a:b]for a,b in pieces);raw_parts.append(raw)
        envelope=[pieces[0][0],pieces[-1][1]]
        c=dict(decision_level='appeal'if i else'judgment',start_char=offset,
            end_char=offset+len(text),text_characters=len(text),text_sha256=sha256(text.encode()),
            number='SYNTHETIC_APPEAL'if i else'SYNTHETIC_TRIAL',
            court_name='محكمة اصطناعية',city='مدينة اصطناعية',hijri_date_raw='1400-01-02',
            gregorian_date_raw=None,source_pdf_pages=[2,3]if i else[1,2],
            complete_document_pages_inspected=[1,2,3])
        d=dict(decision_level=c['decision_level'],raw_body_sha256=sha256(raw.encode()),
            proposed_body_sha256=c['text_sha256'],proposed_offsets=[c['start_char'],c['end_char']],
            source_pdf_pages=c['source_pdf_pages'])
        n=dict(decision_level=c['decision_level'],raw_body_characters=len(raw),raw_body_sha256=d['raw_body_sha256'])
        if disjoint:
            for item in (d,n):
                item.update(native_container_offsets=envelope,native_segments=pieces,
                    native_segment_sha256=[sha256(native[a:b].encode())for a,b in pieces])
        else:
            d['native_offsets']=envelope
            n.update(source_native_start_char=envelope[0],source_native_end_char=envelope[1])
        components.append(c);derivations.append(d);stored.append(n);offset=c['end_char']
    raw='\n\n'.join(raw_parts)
    corrections=dict(source_pdf_sha256=pdf_hash,transcription_sha256=body_hash,
        stored_native_body_sha256=sha256(raw.encode()),complete_source_pages_reviewed=3,
        blank_pages=[],active_component_body_derivations=derivations,stored_native_body_components=stored)
    if disjoint:
        corrections.update(native_component_source_basis='explicit_absolute_disjoint_native_segments_v1',
            whole_native_sha256=sha256(native.encode()),whole_native_characters=len(native),
            selected_native_body_characters=len(raw),
            stored_native_body_container_offsets=[[p[0][0],p[-1][1]]for p in segments],
            stored_native_body_segments=segments,
            native_full_source_coverage=[dict(native_offsets=[a,b],role='SYNTHETIC_JUDICIAL'if i else'SYNTHETIC_EXCLUDED_UI',
                sha256=sha256(native[a:b].encode()),selected_component_index=i)for a,b,i in ranges])
    else:
        corrections['stored_native_body_offsets']=[[p[0][0],p[-1][1]]for p in segments]
    return dict(document_id=doc,version_id=doc+'-'+body_hash[:16],source_id='SYNTHETIC_DISJOINT_NOT_FETCHED',
        opaque_route_id='SYNTHETIC_DISJOINT_NOT_FETCHED',
        source_url='https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/SYNTHETIC_DISJOINT_NOT_FETCHED',
        source_family='moj_judgments',document_type='commercial_court_historical_judgment_and_appeal',
        source_pdf_sha256=pdf_hash,source_file_sha256=pdf_hash,source_pdf_pages=3,
        source_api_url=None,source_body_html_sha256=None,capture_timestamp_utc=None,
        extraction_method='official_historical_pdf_complete_visual_transcription_v1',
        source_identity_kind='frozen_official_opaque_route_and_exact_historical_PDF_no_model_UUID',
        source_capture_kind='historical_official_PDF_capture_date_unknown',
        source_component_count=2,has_judgment=True,has_appeal=True,text_ar=body,text_sha256=body_hash,
        judgment_number='SYNTHETIC_TRIAL',court_name='محكمة اصطناعية',city='مدينة اصطناعية',
        judgment_hijri_date_raw='1400-01-02',judgment_gregorian_date_raw=None,
        appeal_number='SYNTHETIC_APPEAL',appeal_court_name='محكمة اصطناعية',appeal_city='مدينة اصطناعية',
        appeal_hijri_date_raw='1400-01-02',appeal_gregorian_date_raw=None,
        native_body_text_sha256=sha256(raw.encode()),source_components_json=json.dumps(components,ensure_ascii=False),
        source_corrections_json=json.dumps(corrections,ensure_ascii=False))


def _changed(case):
    row=_record();c=json.loads(row['source_corrections_json'])
    changes={
        'missing_mode':lambda:c.pop('native_component_source_basis'),
        'unknown_mode':lambda:c.__setitem__('native_component_source_basis','unknown'),
        'virtual_alias':lambda:c.__setitem__('stored_native_body_offsets',[[0,8209],[8211,11496]]),
        'legacy_derivation_alias':lambda:c['active_component_body_derivations'][1].__setitem__('native_offsets',[8483,11830]),
        'legacy_source_alias':lambda:c['stored_native_body_components'][1].__setitem__('source_native_start_char',8483),
        'missing_segments':lambda:c.pop('stored_native_body_segments'),
        'empty_component':lambda:c['stored_native_body_segments'].__setitem__(1,[]),
        'zero_piece':lambda:c['stored_native_body_segments'][1].__setitem__(0,[8483,8483]),
        'bool_offset':lambda:c['stored_native_body_segments'][0].__setitem__(0,[True,8395]),
        'reversed_pieces':lambda:c['stored_native_body_segments'][1].reverse(),
        'overlap':lambda:c['stored_native_body_segments'][1].__setitem__(1,[8600,11830]),
        'truncated_opening':lambda:c['stored_native_body_segments'][1].__setitem__(0,[8484,8613]),
        'cross_component':lambda:c['stored_native_body_container_offsets'].__setitem__(1,[8000,11830]),
        'coverage_gap':lambda:c['native_full_source_coverage'][2].__setitem__('native_offsets',[8396,8483]),
        'coverage_overlap':lambda:c['native_full_source_coverage'][2].__setitem__('native_offsets',[8394,8483]),
        'coverage_incomplete':lambda:c.__setitem__('whole_native_characters',11834),
        'bool_length':lambda:c.__setitem__('whole_native_characters',True),
        'UI_as_selected':lambda:c['native_full_source_coverage'][4].__setitem__('selected_component_index',2),
        'selected_as_UI':lambda:c['native_full_source_coverage'][3].__setitem__('selected_component_index',None),
        'unknown_component':lambda:c['native_full_source_coverage'][3].__setitem__('selected_component_index',3),
        'bool_component':lambda:c['native_full_source_coverage'][3].__setitem__('selected_component_index',True),
        'bad_coverage_hash':lambda:c['native_full_source_coverage'][3].__setitem__('sha256','bad'),
        'unreviewed_coverage_key':lambda:c['native_full_source_coverage'][3].__setitem__('extra','bad'),
        'bad_whole_hash':lambda:c.__setitem__('whole_native_sha256','bad'),
        'envelope_width_as_raw':lambda:c['stored_native_body_components'][1].__setitem__('raw_body_characters',3347),
        'raw_hash_mismatch':lambda:c['stored_native_body_components'][1].__setitem__('raw_body_sha256','f'*64),
        'piece_hash_mismatch':lambda:c['active_component_body_derivations'][1]['native_segment_sha256'].__setitem__(0,'f'*64),
        'aggregate_length':lambda:c.__setitem__('selected_native_body_characters',11558),
        'proposed_hash':lambda:c['active_component_body_derivations'][1].__setitem__('proposed_body_sha256','f'*64),
        'proposed_offsets':lambda:c['active_component_body_derivations'][1].__setitem__('proposed_offsets',[1,4]),
        'component_level':lambda:c['active_component_body_derivations'][1].__setitem__('decision_level','judgment'),
        'component_pages':lambda:c['active_component_body_derivations'][1].__setitem__('source_pdf_pages',[1]),
    }
    changes[case]();row['source_corrections_json']=json.dumps(c,ensure_ascii=False);return row


def test_explicit_disjoint_native_segments_are_absolute_and_schema_compatible():
    row=_record();validate_case_components(row)
    import pyarrow as pa
    assert pa.Table.from_pylist([row],schema=schemas()['judgments']).num_rows==1
    c=json.loads(row['source_corrections_json'])
    assert c['stored_native_body_container_offsets'][1]==[8483,11830]
    assert c['stored_native_body_segments'][1]==[[8483,8613],[8675,11830]]
    assert c['stored_native_body_components'][1]['raw_body_characters']==3285
    assert c['selected_native_body_characters']==11496


@pytest.mark.parametrize('case',[
    'missing_mode','unknown_mode','virtual_alias','legacy_derivation_alias','legacy_source_alias',
    'missing_segments','empty_component','zero_piece','bool_offset','reversed_pieces','overlap',
    'truncated_opening','cross_component','coverage_gap','coverage_overlap','coverage_incomplete',
    'bool_length','UI_as_selected','selected_as_UI','unknown_component','bool_component',
    'bad_coverage_hash','unreviewed_coverage_key','bad_whole_hash','envelope_width_as_raw',
    'raw_hash_mismatch','piece_hash_mismatch','aggregate_length','proposed_hash',
    'proposed_offsets','component_level','component_pages'])
def test_explicit_disjoint_native_segments_reject_unbound_claims(case):
    with pytest.raises(ValueError):
        validate_case_components(_changed(case))


def test_contiguous_native_offset_width_remains_strict():
    row=_record(False);validate_case_components(row)
    c=json.loads(row['source_corrections_json'])
    assert c['stored_native_body_offsets']==[[186,8395],[8483,11830]]
    c['stored_native_body_components'][1]['raw_body_characters']=3285
    row['source_corrections_json']=json.dumps(c)
    with pytest.raises(ValueError):
        validate_case_components(row)


def test_disjoint_native_provenance_does_not_authorize_changed_source_words():
    original=_record();row=deepcopy(original)
    row['text_ar']=row['text_ar'].replace('حكم','قول',1)
    row['text_sha256']=sha256(row['text_ar'].encode())
    row['version_id']=row['document_id']+'-'+row['text_sha256'][:16]
    c=json.loads(row['source_corrections_json']);c['transcription_sha256']=row['text_sha256']
    row['source_corrections_json']=json.dumps(c)
    with pytest.raises(ValueError):
        validate_case_components(row)
    # Even fully self-consistent source claims cannot reuse an old exact decision.
    components=json.loads(row['source_components_json'])
    components[0]['text_sha256']=sha256(row['text_ar'][:components[0]['end_char']].encode())
    row['source_components_json']=json.dumps(components)
    c['active_component_body_derivations'][0]['proposed_body_sha256']=components[0]['text_sha256']
    row['source_corrections_json']=json.dumps(c);validate_case_components(row)
    decision=dict(document_id=original['document_id'],decision='supported',
        text_sha256=original['text_sha256'],source_file_sha256=original['source_file_sha256'],
        quality_review='pass',privacy_review='pass',rights_basis='SYNTHETIC TEST ONLY',
        evidence_urls=['https://example.invalid/NEVER_FETCHED'],reason='SYNTHETIC TEST ONLY')
    with pytest.raises(ValueError):
        select_supported([row],dict(decisions=[decision]))
