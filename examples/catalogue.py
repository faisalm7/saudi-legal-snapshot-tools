"""Load real metadata, filter titles/structure and inspect or open official citations."""
import argparse
import json
import webbrowser
from datasets import load_dataset
from saudi_legal.core import normalize_search,source_id


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',default='Faisal73/saudi-legal-source-catalogue-2025')
    p.add_argument('--revision',help='Optional immutable Hugging Face commit')
    p.add_argument('--query',default='الأحداث')
    p.add_argument('--source-id')
    p.add_argument('--structure')
    p.add_argument('--limit',type=int,default=3)
    p.add_argument('--open-source',action='store_true',help='Open the first matching official URL in your browser')
    args=p.parse_args()
    ds=load_dataset(args.dataset,name='documents',split='catalogue',revision=args.revision,token=False)
    query=normalize_search(args.query)
    hits=[]
    for r in ds:
        if query and query not in normalize_search(r['title']):continue
        if args.source_id and args.source_id!=r['source_id']:continue
        if args.structure and args.structure!=r['structure_status']:continue
        if source_id(r['source_url'])!=r['source_id']:raise ValueError('Unverified citation; refusing to open URL')
        hits.append(r)
    for r in hits[:args.limit]:
        print(json.dumps({k:r[k] for k in ('title','source_id','source_url','capture_timestamp_utc','structure_status','verified_article_span_count')},ensure_ascii=False))
    print(f'{len(hits)} matching catalogue records out of {len(ds)}; legal text is not included.')
    if args.open_source and hits:webbrowser.open(hits[0]['source_url'])


if __name__=='__main__':main()
