"""Strict factual projection. Never exports legal bodies, article rows or private paths."""
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import unicodedata
from .core import canonical, sha256, source_id

CATALOGUE_VERSION = '0.3.0'
STRING_FIELDS = (
    'catalogue_id document_id version_id source_id source_url title language document_type '
    'source_family capture_timestamp_utc issued_hijri_raw issued_gregorian_raw '
    'published_hijri_raw published_gregorian_raw source_reported_status_at_capture '
    'source_file_sha256 source_text_sha256 text_sha256 source_pdf_sha256 '
    'structure_status analysis_pipeline_version catalogue_version quality_assessment_scope'
).split()
INT_FIELDS = ['source_pdf_pages', 'captured_text_characters', 'verified_article_span_count']
LIST_FIELDS = ['quality_flags', 'content_review_flags']
FIELDS = STRING_FIELDS + INT_FIELDS + LIST_FIELDS
SCOPE = 'automated_processing_and_limited_diagnostic_sample_not_complete_fidelity_review'
STRUCTURE = {'aligned','deferred_no_isolated_pdf_headings','deferred_ambiguous_or_mismatched_heading_sequence',
             'deferred_empty_article_body','deferred_missing_pdf','deferred_pdf_extraction_failure',
             'deferred_pdf_extraction_timeout','deferred_pdf_read_failure','deferred_pdf_read_timeout'}


def bounded_line(value, maximum):
    return isinstance(value,str) and 0 < len(value) <= maximum and all(
        not unicodedata.category(c).startswith('C') and c not in '\r\n\u2028\u2029' for c in value)


def catalogue_schema():
    import pyarrow as pa
    return pa.schema([(k,pa.string()) for k in STRING_FIELDS] +
                     [(k,pa.int32()) for k in INT_FIELDS] +
                     [(k,pa.list_(pa.string())) for k in LIST_FIELDS])


def project_records(records, audits):
    audit_by_id = {}
    for a in audits:
        if a.get('parse_status') != 'parsed':
            continue
        key = a.get('document_id')
        if key in audit_by_id:
            raise ValueError('Duplicate audit document ID')
        audit_by_id[key] = a
    rows=[];seen=set()
    for r in records:
        sid=source_id(r.get('source_url'))
        if not sid or sid!=r.get('source_id') or r.get('source_family')!='boe' or r.get('document_type')!='official_legal_instrument':
            raise ValueError('Only verified BOE instrument provenance is supported')
        if sid in seen:
            raise ValueError('This catalogue exports one capture per distinct BOE source; duplicate source ID')
        seen.add(sid)
        a=audit_by_id.get(r.get('document_id'))
        if not a or a.get('source_file_sha256')!=r.get('source_file_sha256') or a.get('source_id')!=sid:
            raise ValueError('Missing or mismatched hash-bound source audit')
        for key in ('source_file_sha256','source_text_sha256','text_sha256'):
            if not isinstance(r.get(key),str) or not re.fullmatch('[0-9a-f]{64}',r[key]):
                raise ValueError('Missing exact SHA-256 provenance')
        if r.get('document_id') != f"sa-boe-{sid}-ar-{r['text_sha256'][:16]}":
            raise ValueError('Version ID must be derived from the verified source and body hash')
        pdf_hash=r.get('source_pdf_sha256')
        if pdf_hash is not None and (not isinstance(pdf_hash,str) or not re.fullmatch('[0-9a-f]{64}',pdf_hash)):
            raise ValueError('Invalid PDF SHA-256 provenance')
        pages=r.get('source_pdf_pages')
        if pages is not None and (type(pages) is not int or not 0 < pages < 2**31):
            raise ValueError('PDF page count must be a positive int32 or null')
        for key in ('issued_hijri_raw','issued_gregorian_raw','published_hijri_raw','published_gregorian_raw'):
            value=r.get(key)
            if value is not None and (not isinstance(value,str) or not re.fullmatch('[0-9٠-٩/ ]{1,32}',value)):
                raise ValueError('Date metadata must contain only bounded date characters or null')
        historic_status=r.get('source_reported_status_at_capture')
        if historic_status is not None and not bounded_line(historic_status,64):
            raise ValueError('Historical status must be a bounded single line or null')
        if not isinstance(r.get('processing_version'),str) or not re.fullmatch(r'[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}',r['processing_version']):
            raise ValueError('Analysis pipeline version must be a semantic version')
        if sha256(r['text_ar'].encode())!=r['text_sha256']:
            raise ValueError('Private body hash mismatch before factual projection')
        title=r.get('title')
        if not bounded_line(title,250) or not title.strip():
            raise ValueError('Review descriptive title before catalogue export')
        if not bounded_line(r.get('capture_timestamp_utc'),64):
            raise ValueError('Capture timestamp must be a bounded ISO timestamp')
        dt=datetime.fromisoformat(r['capture_timestamp_utc'].replace('Z','+00:00'))
        if dt.tzinfo is None or dt.utcoffset().total_seconds()!=0:
            raise ValueError('Capture timestamp needs timezone')
        if r.get('language')!='ar':
            raise ValueError('Only Arabic source instruments are supported')
        status=a.get('segmentation_status')
        if status not in STRUCTURE:
            raise ValueError('Undefined structure status')
        count=r.get('article_count')
        if status=='aligned':
            if not isinstance(count,int) or isinstance(count,bool) or count<=0 or count!=a.get('article_rows'):
                raise ValueError('Article span count is not supported by aligned audit')
        elif count is not None:
            raise ValueError('Uncertain structure must remain null, not zero articles')
        flags={k:list(r.get(k,[])) if k=='quality_flags' else list(a.get(k,[])) for k in LIST_FIELDS}
        if any(not isinstance(f,str) or not re.fullmatch('[a-z][a-z0-9_]{0,100}',f) for fs in flags.values() for f in fs):
            raise ValueError('Quality metadata must be controlled codes, never free-text excerpts')
        row={k:r.get(k) for k in STRING_FIELDS}
        row.update(catalogue_id=f"sa-boe-capture-{sid}-{r['source_file_sha256'][:16]}",
                   document_id=f'sa-boe-{sid}-ar',version_id=r['document_id'],
                   structure_status=status,analysis_pipeline_version=r.get('processing_version'),
                   catalogue_version=CATALOGUE_VERSION,quality_assessment_scope=SCOPE,
                   source_pdf_pages=r.get('source_pdf_pages'),captured_text_characters=len(r['text_ar']),
                   verified_article_span_count=count,**flags)
        for k in STRING_FIELDS:
            if row[k] is not None and not isinstance(row[k],str):
                raise ValueError('Unexpected metadata field type')
        rows.append({k:row[k] for k in FIELDS})
    if not rows:
        raise ValueError('No catalogue records; refusing empty publication')
    return sorted(rows,key=lambda r:r['catalogue_id'])


def export_catalogue(records_path,audit_path,output):
    import pyarrow.parquet as pq
    out=Path(output)
    if out.exists() or out.is_symlink():
        raise ValueError('Choose a new catalogue directory; existing work is preserved')
    records=[json.loads(s) for s in Path(records_path).read_text().splitlines() if s.strip()]
    audits=[json.loads(s) for s in Path(audit_path).read_text().splitlines() if s.strip()]
    rows=project_records(records,audits)
    import pyarrow as pa
    table=pa.Table.from_pylist(rows,schema=catalogue_schema())
    out.mkdir(parents=True)
    pq.write_table(table,out/'documents.parquet',compression='zstd',row_group_size=128,write_page_index=True)
    (out/'preview.jsonl').write_text(''.join(canonical(r) for r in rows[:3]))
    summary={'catalogue_version':CATALOGUE_VERSION,'catalogue_rows':len(rows),
             'distinct_documents':len({r['document_id'] for r in rows}),
             'distinct_captured_content_versions':len({r['version_id'] for r in rows}),
             'exported_legal_text_rows':0,'exported_article_span_rows':0,
             'documents_with_verified_span_count':sum(r['verified_article_span_count'] is not None for r in rows),
             'span_count_sum_private_analysis_only':sum(r['verified_article_span_count'] or 0 for r in rows),
             'structure_status':dict(sorted(Counter(r['structure_status'] for r in rows).items())),
             'content_review_flags':dict(sorted(Counter(f for r in rows for f in r['content_review_flags']).items())),
             'metadata_non_null':{k:sum(r[k] is not None for r in rows) for k in FIELDS},
             'capture_min':min((r['capture_timestamp_utc'] for r in rows),key=datetime.fromisoformat),
             'capture_max':max((r['capture_timestamp_utc'] for r in rows),key=datetime.fromisoformat),
             'snapshot_not_current_or_complete':True}
    (out/'quality.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    schema={'version':CATALOGUE_VERSION,'unit':'one historical capture of one BOE Arabic source instrument',
            'config':'documents','split':'catalogue','contains_legal_text':False,
            'fields':[{'name':f.name,'type':str(f.type),'nullable':f.nullable} for f in catalogue_schema()]}
    (out/'SCHEMA.json').write_text(json.dumps(schema,indent=2)+'\n')
    return summary
