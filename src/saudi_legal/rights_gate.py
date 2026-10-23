"""Prepare a data-only local public candidate from explicit reviewed decisions.

This validates a decision record, not the law. A publisher's approval cannot
replace third-party permissions. No remote publication is implemented here.
"""
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from .core import canonical, sha256, document_arrow_schema


def select_supported(records, registry):
    decisions=registry.get('decisions')
    if not isinstance(decisions,list):
        raise ValueError('Rights registry must contain a decisions list')
    by_id={}
    for d in decisions:
        if not isinstance(d,dict) or not isinstance(d.get('document_id'),str):
            raise ValueError('Malformed rights decision')
        if d['document_id'] in by_id:
            raise ValueError('Duplicate or conflicting rights decisions')
        by_id[d['document_id']]=d
    selected=[];seen=set()
    for r in records:
        if r['document_id'] in seen:
            raise ValueError('Duplicate document ID in input')
        seen.add(r['document_id'])
        d=by_id.get(r['document_id'])
        if not d or d.get('decision')!='supported':
            continue
        if not isinstance(r.get('source_file_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',r['source_file_sha256']):
            raise ValueError('Supported record requires an exact SHA-256 source-file hash')
        if sha256(r['text_ar'].encode())!=r['text_sha256']:
            raise ValueError('Candidate text hash mismatch')
        if d.get('text_sha256')!=r['text_sha256'] or d.get('source_file_sha256')!=r['source_file_sha256']:
            raise ValueError('Rights decision does not bind exact input and output hashes')
        if d.get('quality_review')!='pass' or d.get('privacy_review') not in ('pass','not_personal_data'):
            raise ValueError('Supported rights do not replace quality or privacy review')
        urls=d.get('evidence_urls')
        if not isinstance(d.get('rights_basis'),str) or not d['rights_basis'].strip() or not isinstance(urls,list) or not urls:
            raise ValueError('Positive rights basis and evidence are required')
        if any(not isinstance(u,str) or urlparse(u).scheme!='https' or not urlparse(u).netloc for u in urls):
            raise ValueError('Rights evidence must identify HTTPS source URLs')
        if not isinstance(d.get('reason'),str) or not d['reason'].strip():
            raise ValueError('Rights decision needs an explicit reasoning note')
        row=r.copy();row['rights_basis']=d['rights_basis'];row['rights_evidence_urls']=list(urls)
        selected.append(row)
    return sorted(selected,key=lambda r:r['document_id'])


def prepare_public(records_path,decisions_path,output):
    import pyarrow as pa
    import pyarrow.parquet as pq
    import yaml
    records_path,decisions_path,output=Path(records_path),Path(decisions_path),Path(output)
    # Validate everything before creating output. Empty selection is a blocker,
    # never an empty supposedly completed legal dataset.
    records=[json.loads(line) for line in records_path.read_text().splitlines()]
    registry_bytes=decisions_path.read_bytes();registry=json.loads(registry_bytes)
    selected=select_supported(records,registry)
    if not selected:
        raise ValueError('No records have supported rights, quality and privacy decisions; no public text dataset prepared')
    if output.exists() or output.is_symlink():
        raise ValueError('Public candidate destination must be new; existing work is never overwritten')
    configs={'official_legal_instrument':'laws','judgment':'judgments','circular':'circulars'}
    groups={}
    for r in selected:
        if r['document_type'] not in configs:
            raise ValueError('Unreviewed document type; keep distinct types separate')
        if set(r)-set(document_arrow_schema(public=True).names):
            raise ValueError('Unrecognized public record fields; review the export schema before publication')
        groups.setdefault(configs[r['document_type']],[]).append(r)
    output.mkdir(parents=True)
    config_yaml=[]
    for config,rows in sorted(groups.items()):
        folder=output/'data'/config;folder.mkdir(parents=True)
        for n,start in enumerate(range(0,len(rows),100)):
            table=pa.Table.from_pylist(rows[start:start+100],schema=document_arrow_schema(public=True))
            if 'article_count' in table.column_names:
                idx=table.column_names.index('article_count')
                table=table.set_column(idx,'article_count',table['article_count'].cast(pa.int32()))
            pq.write_table(table,folder/f'part-{n:05d}.parquet',compression='zstd',row_group_size=32,write_page_index=True)
        config_yaml.append({'config_name':config,'data_files':[{'split':'corpus','path':f'data/{config}/*.parquet'}]})
    config_yaml[0]['default']=True
    meta={'language':['ar'],'license':'other','configs':config_yaml}
    (output/'README.md').write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n# Locally prepared data candidate\n\nOnly hash-bound supported rights/quality/privacy decisions were selected. This machine gate does not certify those legal judgments. Add the reviewed source-specific data-rights notice, provenance, counts, quality and limitations before any publication. Code licensing does not license the source content. No remote publication was performed.\n')
    (output/'preview.jsonl').write_text(''.join(canonical(r) for r in selected[:3]))
    (output/'rights-decisions.json').write_text(json.dumps({'registry_sha256':sha256(registry_bytes),'decisions':[d for d in registry['decisions'] if d['document_id'] in {r['document_id'] for r in selected}]},ensure_ascii=False,indent=2)+'\n')
    summary={'records':len(selected),'configurations':{k:len(v) for k,v in sorted(groups.items())},'rights_registry_sha256':sha256(registry_bytes),'remote_publication':False}
    (output/'metrics.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
