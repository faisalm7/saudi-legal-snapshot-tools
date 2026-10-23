"""Load published Arabic text, search it and inspect official source citations.

Simple lexical matching demonstrates access, not retrieval accuracy or legal advice.
"""
import argparse
import json
from urllib.parse import urlparse
import webbrowser

from datasets import load_dataset
from saudi_legal.core import normalize_search, source_id


def valid_citation(row):
    boe_id=source_id(row["source_url"])
    if boe_id is not None and boe_id==row["source_id"]:return True
    parsed=urlparse(row["source_url"])
    if parsed.scheme!="https" or parsed.netloc!="laws.moj.gov.sa" or parsed.query:return False
    parts=parsed.path.strip("/").split("/")
    if len(parts)==3 and parts[:2]==["ar","legislation"]:
        fragment="content-card-"+row["source_section_id"] if row.get("source_section_id") else ""
        return parts[2]==row["source_id"] and parsed.fragment==fragment
    if len(parts)==4 and parts[:2]==["ar","JudicialDecisionsList"] and parts[2] in ("0","1","2","3"):
        return not parsed.fragment and parts[3]==row.get("opaque_route_id")
    return False


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset",default="Faisal73/saudi-legal-text-snapshots")
    parser.add_argument("--revision",help="An immutable Hugging Face commit is recommended")
    parser.add_argument("--config",choices=["laws","judgments","article_spans","source_sections","boe_documents","boe_article_spans"],default="boe_documents")
    parser.add_argument("--query",default="لا يجوز")
    parser.add_argument("--source-id");parser.add_argument("--limit",type=int,default=3)
    parser.add_argument("--open-source",action="store_true",help="Open the first matching official citation")
    args=parser.parse_args()
    if args.limit<1:parser.error("--limit must be positive")
    rows=load_dataset(args.dataset,name=args.config,split="corpus",revision=args.revision,token=False)
    query=normalize_search(args.query).strip();hits=[]
    for row in rows:
        if args.source_id and row["source_id"]!=args.source_id:continue
        body=normalize_search(row["text_ar"])
        if query in body:
            if not valid_citation(row):raise ValueError("Citation does not match the recorded source identity")
            hits.append(row)
    for row in hits[:args.limit]:
        print(json.dumps({"document_id":row["document_id"],"title":row.get("title"),
            "source_sequence":row.get("source_sequence",row.get("heading_raw")),"source_id":row["source_id"],
            "capture_timestamp_utc":row["capture_timestamp_utc"],"text_sha256":row["text_sha256"],
            "text_excerpt":row["text_ar"][:400],"source_url":row["source_url"]},ensure_ascii=False))
    print(f"{len(hits)} matching {args.config} rows out of {len(rows)}. Source status and capture dates are in the data.")
    if args.open_source and hits:webbrowser.open(hits[0]["source_url"])


if __name__=="__main__":main()
