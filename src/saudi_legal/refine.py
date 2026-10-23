"""Apply explicit source-backed reviews to existing private capture checkpoints.

This command does not infer publication permission or fetch/modify source files.
Every correction binds the original JSON, body and paired PDF fingerprints.
"""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from datetime import datetime
import re
from urllib.parse import urlparse

from .articles import segment_with_pdf_evidence
from .core import canonical, normalize_search, sha256, source_id


def refine_record(record, audit, pdf_text, review=None):
    r=deepcopy(record)
    if not source_id(r.get('source_url')) or source_id(r['source_url'])!=r.get('source_id'):
        raise ValueError('Invalid official source identity')
    if sha256(r['text_ar'].encode())!=r['text_sha256']:
        raise ValueError('Captured body fingerprint mismatch')
    if r['document_id']!=f"sa-boe-{r['source_id']}-ar-{r['text_sha256'][:16]}":
        raise ValueError('Captured version identity mismatch')
    if audit.get('document_id')!=r['document_id'] or audit.get('source_file_sha256')!=r['source_file_sha256']:
        raise ValueError('Source audit does not bind this record')
    if not r.get('source_pdf_sha256') or r['source_pdf_sha256']!=audit.get('pdf_sha256'):
        raise ValueError('Paired PDF fingerprint mismatch')
    original_id=r['document_id'];original_hash=r['text_sha256'];patches=[];exclusions=[]
    if review is not None:
        for key,expected in (('document_id',original_id),('source_file_sha256',r['source_file_sha256']),
                             ('text_sha256',original_hash),('pdf_sha256',r['source_pdf_sha256'])):
            if review.get(key)!=expected:
                raise ValueError('Review must bind the exact JSON, body and PDF fingerprints')
        if not review.get('reason') or not review.get('source_url')==r['source_url']:
            raise ValueError('Review needs an official locator and explicit reason')
        exclusions=review.get('exclude_pdf_headings',[])
        previous_end=-1
        for patch in sorted(review.get('text_patches',[]),key=lambda p:p['start_char']):
            start,end=patch['start_char'],patch['end_char']
            if type(start) is not int or type(end) is not int or not 0<=start<end<=len(r['text_ar']) or start<previous_end:
                raise ValueError('Invalid or overlapping source correction offsets')
            if r['text_ar'][start:end]!=patch.get('before') or not isinstance(patch.get('after'),str) or not patch['after']:
                raise ValueError('Correction does not match exact captured characters')
            paired_page=(type(patch.get('evidence_pdf_page')) is int and 1<=patch['evidence_pdf_page']<=r['source_pdf_pages'])
            image=False
            if patch.get('source_image_url'):
                parsed=urlparse(patch['source_image_url'])
                try:
                    stamp=datetime.fromisoformat(patch.get('source_image_capture_timestamp_utc','').replace('Z','+00:00'))
                    utc=stamp.tzinfo is not None and stamp.utcoffset().total_seconds()==0
                except (TypeError,ValueError):utc=False
                image=(parsed.scheme=='https' and parsed.netloc=='laws.boe.gov.sa'
                    and parsed.path=='/BoeLaws/Laws/GetViewerImage/' and not parsed.fragment
                    and bool(re.fullmatch(r'imageFileName=[A-Za-z0-9_-]+_Page_[0-9]+\.jpg',parsed.query))
                    and bool(re.fullmatch('[0-9a-f]{64}',patch.get('source_image_sha256','')))
                    and utc and bool(patch.get('version_notice')))
                if not image:raise ValueError('Image correction needs an official image locator, fingerprint, UTC capture and version notice')
            if not (paired_page or image) or not patch.get('reason'):
                raise ValueError('Correction needs reviewed PDF-page or official source-image evidence')
            previous_end=end;patches.append(patch)
        for patch in reversed(patches):
            r['text_ar']=r['text_ar'][:patch['start_char']]+patch['after']+r['text_ar'][patch['end_char']:]
    r['text_sha256']=sha256(r['text_ar'].encode())
    r['text_search_ar']=normalize_search(r['text_ar'])
    r['document_id']=f"sa-boe-{r['source_id']}-ar-{r['text_sha256'][:16]}"
    if patches:
        r['transformations']=r['transformations']+['apply_hash_bound_reviewed_source_text_patches']
        r['quality_flags']=sorted(set(r['quality_flags'])|{'source_backed_text_correction'})
    r['processing_version']='0.4.0'
    articles,evidence=segment_with_pdf_evidence(r,pdf_text,r['source_pdf_sha256'],exclusions)
    r['article_count']=len(articles) if articles else None
    r['quality_flags']=[f for f in r['quality_flags'] if f not in ('article_heading_spans_pdf_evidenced','article_boundaries_unverified')]
    r['quality_flags'].append('article_heading_spans_pdf_evidenced' if articles else 'article_boundaries_unverified')
    receipt={'baseline_document_id':original_id,'document_id':r['document_id'],'source_id':r['source_id'],
             'source_url':r['source_url'],'source_file_sha256':r['source_file_sha256'],
             'baseline_text_sha256':original_hash,'text_sha256':r['text_sha256'],'pdf_sha256':r['source_pdf_sha256'],
             'text_patches':patches,'reviewed_excluded_pdf_headings':evidence.get('reviewed_excluded_pdf_headings',[]),
             'structure_status':evidence['status'],'article_rows':len(articles),'permission_inferred':False}
    return r,articles,{**audit,'document_id':r['document_id'],'segmentation_status':evidence['status'],
                       'segmentation_evidence':evidence,'article_rows':len(articles)},receipt


def refine_capture(records_path,audit_path,pdf_text_folder,reviews_path,output):
    paths=[Path(p) for p in (records_path,audit_path,pdf_text_folder,reviews_path)]
    out=Path(output)
    if out.is_symlink():raise ValueError('Refinement output must not be a symlink')
    resolved=out.resolve()
    for p in paths:
        source=p.resolve()
        if resolved==source or resolved in source.parents or source in resolved.parents:
            raise ValueError('Refinement output must be separate from inputs')
    if out.exists() and (not (out/'RUN.json').is_file() or any(p.is_symlink() for p in out.rglob('*'))):
        raise ValueError('Resume only a matching refinement checkpoint, never unrelated existing work')
    records_bytes=paths[0].read_bytes();audit_bytes=paths[1].read_bytes();review_bytes=paths[3].read_bytes()
    run={'records_sha256':sha256(records_bytes),'audit_sha256':sha256(audit_bytes),'reviews_sha256':sha256(review_bytes),'version':'0.4.0'}
    if out.exists() and json.loads((out/'RUN.json').read_text())!=run:
        raise ValueError('Checkpoint inputs changed; choose a new output')
    records=[json.loads(s) for s in records_bytes.splitlines() if s.strip()]
    audits=[json.loads(s) for s in audit_bytes.splitlines() if s.strip()]
    reviews=json.loads(review_bytes).get('reviews',[])
    ab={a['document_id']:a for a in audits if a.get('parse_status')=='parsed'}
    rb={r['document_id']:r for r in reviews}
    ids=[r['document_id'] for r in records]
    if len(ab)!=len(records) or len(set(ids))!=len(ids) or set(ab)!=set(ids) or len(rb)!=len(reviews) or not set(rb)<=set(ab):
        raise ValueError('Duplicate, missing or extraneous source/review identities')
    out.mkdir(parents=True,exist_ok=True);(out/'checkpoints').mkdir(exist_ok=True)
    (out/'RUN.json').write_text(canonical(run))
    results=[]
    for r in records:
        if source_id(r.get('source_url'))!=r.get('source_id') or source_id(r.get('source_url')) is None:
            raise ValueError('Invalid official source identity')
        a=ab[r['document_id']];pdf=paths[2]/f"{a['pdf_sha256']}.layout.txt"
        raw_pdf=pdf.read_bytes();proof=pdf.with_suffix('.sha256')
        if not proof.is_file() or sha256(raw_pdf)!=proof.read_text().strip():
            raise ValueError('Extracted PDF evidence checkpoint fingerprint mismatch')
        signature=sha256(canonical({'run':run,'document_id':r['document_id'],'pdf_text_sha256':sha256(raw_pdf)}).encode())
        checkpoint=out/'checkpoints'/f"{r['source_id']}.json"
        if checkpoint.is_file():
            saved=json.loads(checkpoint.read_text())
            if saved.get('signature')!=signature or saved.get('payload_sha256')!=sha256(canonical(saved['payload']).encode()):
                raise ValueError('Refinement checkpoint integrity mismatch')
            payload=saved['payload']
        else:
            rr,ars,aa,receipt=refine_record(r,a,raw_pdf.decode('utf-8'),rb.get(r['document_id']))
            payload={'record':rr,'articles':ars,'audit':aa,'receipt':receipt}
            temp=checkpoint.with_suffix('.tmp');temp.write_text(canonical({'signature':signature,'payload':payload,'payload_sha256':sha256(canonical(payload).encode())}));temp.replace(checkpoint)
        results.append(payload)
    outputs={'records.jsonl':[p['record'] for p in results],
             'article-spans.jsonl':[a for p in results for a in p['articles']],
             'audit.jsonl':[p['audit'] for p in results],'review-receipts.jsonl':[p['receipt'] for p in results]}
    for name,rows in outputs.items():
        temp=out/(name+'.tmp');temp.write_text(''.join(canonical(r) for r in rows));temp.replace(out/name)
    summary={'records':len(results),'article_spans':len(outputs['article-spans.jsonl']),
             'structure_status':dict(Counter(p['receipt']['structure_status'] for p in results)),
             'records_with_text_correction':sum(bool(p['receipt']['text_patches']) for p in results),
             'records_with_reviewed_heading_exclusion':sum(bool(p['receipt']['reviewed_excluded_pdf_headings']) for p in results),
             'permission_inferred':False}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
