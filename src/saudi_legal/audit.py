"""Resumable private capture audit and PDF-evidenced heading segmentation."""
from collections import Counter
import concurrent.futures
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from .core import canonical, make_record, sha256, document_arrow_schema
from .articles import segment_with_pdf_evidence


def audit_capture(json_folder, pdf_folder, output, timeout=20, workers=4, pdftotext="pdftotext", original_root=None):
    if Path(output).is_symlink():
        raise ValueError("Audit output must not be a symlink")
    jf,pf,out=map(lambda p:Path(p).resolve(),(json_folder,pdf_folder,output))
    for src in (jf,pf):
        if out==src or src in out.parents or out in src.parents:
            raise ValueError("Audit output must be separate from capture inputs")
    if original_root:
        original=Path(original_root).resolve()
        if out==original or original in out.parents or out in original.parents:
            raise ValueError("Audit output must not overlap original collection")
    if out.exists() and any(p.is_symlink() for p in out.rglob('*')):
        raise ValueError("Audit output must not contain symlinks")
    out.mkdir(parents=True,exist_ok=True);(out/'pdf-text').mkdir(exist_ok=True)
    paths=sorted(jf.glob('*.json'))
    def one(path):
        started=time.monotonic()
        if path.is_symlink():
            return None,[],{"filename_private":path.name,"parse_status":"deferred_symlink"}
        # Isolate reads as well as PDF extraction: macOS cloud reads can block.
        # The caller may use staged captures, but the CLI does not assume it.
        try:
            result=subprocess.run([sys.executable,'-c',
                'import sys; f=open(sys.argv[1],"rb"); b=f.read(33554433); sys.exit(2) if len(b)>33554432 else sys.stdout.buffer.write(b)',str(path)],
                capture_output=True,timeout=timeout)
            if result.returncode:
                return None,[],{"filename_private":path.name,"parse_status":"deferred_read_failure_or_size_limit"}
            raw=result.stdout
        except subprocess.TimeoutExpired:
            return None,[],{"filename_private":path.name,"parse_status":"deferred_read_timeout"}
        digest=sha256(raw)
        info={"source_file_sha256":digest,"filename_private":path.name,"source_bytes":len(raw),"parse_status":None}
        try:
            rec=make_record(json.loads(raw),digest)
        except (ValueError,TypeError) as e:
            return None,[],{**info,"parse_status":"rejected","reason":str(e)}
        info.update(parse_status='parsed',document_id=rec['document_id'],source_id=rec['source_id'],source_url=rec['source_url'])
        rec['source_pdf_sha256']=None
        rec['source_pdf_pages']=None
        pdf=pf/path.with_suffix('.pdf').name
        if not pdf.exists() or pdf.is_symlink():
            return rec,[],{**info,"segmentation_status":"deferred_missing_pdf"}
        try:
            hashed=subprocess.run([sys.executable,'-c',
                'import hashlib,sys; h=hashlib.sha256(); f=open(sys.argv[1],"rb"); '
                '[(h.update(b)) for b in iter(lambda:f.read(1048576),b"")]; print(h.hexdigest())',str(pdf)],
                capture_output=True,text=True,timeout=timeout)
            if hashed.returncode:
                return rec,[],{**info,"segmentation_status":"deferred_pdf_read_failure"}
            ph=hashed.stdout.strip()
        except subprocess.TimeoutExpired:
            return rec,[],{**info,"segmentation_status":"deferred_pdf_read_timeout"}
        cache=out/'pdf-text'/f'{ph}.layout.txt'
        cache_hash=cache.with_suffix('.sha256')
        if cache.exists() and cache_hash.exists() and sha256(cache.read_bytes())==cache_hash.read_text().strip():
            text=cache.read_text();extract_status='checkpoint_available'
        else:
            try:
                result=subprocess.run([pdftotext,'-layout',str(pdf),'-'],capture_output=True,text=True,timeout=timeout)
                if result.returncode:
                    return rec,[],{**info,"segmentation_status":"deferred_pdf_extraction_failure","pdf_sha256":ph}
                text=result.stdout;cache.write_text(text);cache_hash.write_text(sha256(cache.read_bytes())+'\n');extract_status='extracted'
            except subprocess.TimeoutExpired:
                return rec,[],{**info,"segmentation_status":"deferred_pdf_extraction_timeout","pdf_sha256":ph}
        articles,evidence=segment_with_pdf_evidence(rec,text,ph)
        info.update(pdf_sha256=ph,pdf_bytes=pdf.stat().st_size,pdf_pages=len(text.split('\f'))-int(text.endswith('\f')),pdf_extract_status=extract_status,pdf_extract_characters=len(text),segmentation_status=evidence.pop('status'),segmentation_evidence=evidence,elapsed_s=round(time.monotonic()-started,4))
        # Structural spans preserve source text exactly. They are not an assertion
        # of completeness or source legal validity and do not imply permissions.
        info['article_rows']=len(articles)
        rec['source_pdf_sha256']=ph
        rec['source_pdf_pages']=info['pdf_pages']
        if articles:
            rec['article_count']=len(articles)
            rec['quality_flags']=[f for f in rec['quality_flags'] if f!='article_boundaries_unverified']+['article_heading_spans_pdf_evidenced']
        checks={
            'illustration_reference':bool(re.search('أصل الوثيقة',rec['text_ar'])),
            'article_attachment_control':bool(re.search('مرفق المادة',rec['text_ar'])),
            'promised_list_then_next_article':bool(re.search(r'(?:على النحو (?:الآتي|التالي)|كما يلي|ما يلي)\s*:\s*المادة',rec['text_ar'])),
            'annex_reference':bool(re.search(r'ملحق|ملاحق',rec['text_ar'])),
            'broken_negation_word':bool(re.search(r'(?<!\w)غ\s+ير(?!\w)',rec['text_ar'])),
        }
        info['content_review_flags']=[k for k,v in checks.items() if v]
        return rec,articles,info
    records,articles,audits=[],[],[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool,(out/'checkpoint.jsonl').open('a') as checkpoint:
        for i,(rec,ar,info) in enumerate(pool.map(one,paths),1):
            if rec:records.append(rec)
            articles.extend(ar);audits.append(info);checkpoint.write(canonical(info));checkpoint.flush()
            if i%50==0 or i==len(paths):print(f'capture audit {i}/{len(paths)}',flush=True)
    for name,rows in [('records.jsonl',records),('article-spans.jsonl',articles),('audit.jsonl',audits)]:
        (out/name).write_text(''.join(canonical(r) for r in rows))
    # A real locally loadable processing artifact, explicitly PRIVATE while its
    # source-content permission remains unresolved. The public gate is separate.
    import pyarrow as pa
    import pyarrow.parquet as pq
    for config,rows in [('laws',records),('article_spans',articles)]:
        folder=out/'data'/config;folder.mkdir(parents=True,exist_ok=True)
        for old in folder.glob('part-*.parquet'):old.unlink()
        shard_size=100 if config=='laws' else 2000
        for n,start in enumerate(range(0,len(rows),shard_size)):
            table=pa.Table.from_pylist(rows[start:start+shard_size],schema=document_arrow_schema() if config=='laws' else None)
            if 'article_count' in table.column_names:
                idx=table.column_names.index('article_count');table=table.set_column(idx,'article_count',table['article_count'].cast(pa.int32()))
            pq.write_table(table,folder/f'part-{n:05d}.parquet',compression='zstd',row_group_size=32,write_page_index=True)
    (out/'README.md').write_text('---\nlanguage:\n- ar\nlicense: other\nconfigs:\n- config_name: laws\n  default: true\n  data_files:\n  - split: corpus\n    path: data/laws/*.parquet\n- config_name: article_spans\n  data_files:\n  - split: corpus\n    path: data/article_spans/*.parquet\n---\n# PRIVATE captured-source processing artifact\n\nNot cleared for public redistribution. Source copyright/contract/circulation questions remain unresolved. Article rows are exact source-text spans aligned to captured PDF heading lines; ambiguity is deferred. Original paragraphs remain flattened in DOM text, and source completeness/legal status is not certified. Raw inputs, extracted PDF text and private audit paths must not be uploaded. A separate reviewed hash-specific rights/quality/privacy gate is required before preparing any public data candidate.\n')
    summary={'input_json_files':len(paths),'parsed_records':len(records),'unique_source_ids':len({r['source_id'] for r in records}),'unique_exact_texts':len({r['text_sha256'] for r in records}),'parse_status':dict(Counter(r['parse_status'] for r in audits)),'segmentation_status':dict(Counter(r.get('segmentation_status','not_attempted') for r in audits)),'article_span_rows':len(articles),'content_flags':dict(Counter(f for r in audits for f in r.get('content_review_flags',[]))),'pdf_pages':sum(r.get('pdf_pages',0) for r in audits),'source_file_sha256_verified':len(records),'captured_text_sha256_verified':len(records),'public_permission_not_inferred':True,'rights_basis_non_null':sum(r['rights_basis'] is not None for r in records)}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary
