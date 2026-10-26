"""Load published Arabic text, search it and inspect official source citations.

Simple lexical matching demonstrates access, not retrieval accuracy or legal advice.
"""
import argparse
import json
import re
from urllib.parse import urlparse
import webbrowser

from datasets import load_dataset
from saudi_legal.core import normalize_search, source_id

PARENTS = {"boe_article_spans": "boe_documents", "article_spans": "laws", "source_sections": "laws"}


def search_view(text):
    """Map a normalized search string back to exact original character spans."""
    clusters = list(re.finditer(r"[^\u0300-\u036f\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed][\u0300-\u036f\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]*|.", text, re.S))
    chars, spans = [], []
    for cluster in clusters:
        for char in normalize_search(cluster.group()):
            if char.isspace():
                if chars and chars[-1] == " ":
                    spans[-1] = (spans[-1][0], cluster.end())
                    continue
                char = " "
            chars.append(char)
            spans.append((cluster.start(), cluster.end()))
    return "".join(chars), spans


def matching_passage(text, query, context_chars=150):
    normalized, spans = search_view(text)
    needle = re.sub(r"\s+", " ", normalize_search(query)).strip()
    if not needle:
        raise ValueError("Search query must contain visible characters")
    index = normalized.find(needle)
    if index < 0:
        return None
    start, end = spans[index][0], spans[index + len(needle) - 1][1]
    left, right = max(0, start - context_chars), min(len(text), end + context_chars)
    return {"start_char": start, "end_char": end, "matched_text": text[start:end],
            "before": text[left:start], "after": text[end:right], "passage": text[left:right]}


def metadata_matches(row, args):
    if args.source_id and row["source_id"] != args.source_id:
        return False
    if args.document_type and row.get("document_type") != args.document_type:
        return False
    for value, fields in ((args.court, ("court_name", "appeal_court_name")),
                          (args.city, ("city", "appeal_city"))):
        if value and not any(normalize_search(value) in normalize_search(row.get(k) or "") for k in fields):
            return False
    captured = row.get("capture_timestamp_utc")
    if args.captured_from and (not captured or captured[:10] < args.captured_from):
        return False
    if args.captured_before and (not captured or captured[:10] >= args.captured_before):
        return False
    return True


def parent_context(row, parent, passage, context_chars=150):
    if parent["document_id"] != row["document_id"] or not valid_citation(parent):
        raise ValueError("Parent identity/citation does not match the source unit")
    start, end = (row["start_char"], row["end_char"]) if "start_char" in row else (row["start"], row["end"])
    if parent["text_ar"][start:end] != row["text_ar"]:
        raise ValueError("Source unit does not equal its declared parent slice")
    absolute = start + passage["start_char"]
    return {"document_id": parent["document_id"], "title": parent.get("title"),
            "source_url": parent["source_url"], "text_sha256": parent["text_sha256"],
            "matched_start_in_parent": absolute,
            "passage": parent["text_ar"][max(0, absolute-context_chars):min(len(parent["text_ar"]), start+passage["end_char"]+context_chars)],
            "metadata": {k: parent.get(k) for k in ("document_type", "source_family", "capture_timestamp_utc", "source_reported_status_at_capture", "court_name", "appeal_court_name", "city", "appeal_city")}}


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
    parser.add_argument("--document-type", help="Exact documented document_type value")
    parser.add_argument("--court", help="Arabic substring in the observed court or appeal court")
    parser.add_argument("--city", help="Arabic substring in the observed city or appeal city")
    parser.add_argument("--captured-from", help="Inclusive capture date YYYY-MM-DD; unknown dates do not match")
    parser.add_argument("--captured-before", help="Exclusive capture date YYYY-MM-DD; this does not filter legal commencement")
    parser.add_argument("--show-parent",action="store_true",help="For article/section results, load and validate the complete parent document and print its matching context/metadata")
    parser.add_argument("--context-chars",type=int,default=150)
    parser.add_argument("--open-source",action="store_true",help="Open the first matching official citation")
    args=parser.parse_args()
    if args.limit<1:parser.error("--limit must be positive")
    if not 0 <= args.context_chars <= 2000:parser.error("--context-chars must be between 0 and 2000")
    from datetime import date
    for value in (args.captured_from,args.captured_before):
        if value:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",value):
                parser.error("Capture dates must use YYYY-MM-DD")
            try:date.fromisoformat(value)
            except ValueError:parser.error("Capture dates must use YYYY-MM-DD")
    if not re.sub(r"\s+"," ",normalize_search(args.query)).strip():parser.error("--query must contain visible characters")
    rows=load_dataset(args.dataset,name=args.config,split="corpus",revision=args.revision,token=False)
    query=re.sub(r"\s+"," ",normalize_search(args.query)).strip()
    hits=[]; matching_documents=set();filtered=0;matched_rows=0
    for row in rows:
        if not metadata_matches(row,args):continue
        filtered+=1
        if query in re.sub(r"\s+"," ",normalize_search(row["text_ar"])):
            if not valid_citation(row):raise ValueError("Citation does not match the recorded source identity")
            matched_rows+=1
            matching_documents.add(row["document_id"])
            if len(hits)<args.limit:
                passage=matching_passage(row["text_ar"],args.query,args.context_chars)
                if passage is None:raise ValueError("Search normalization could not be mapped to the original text")
                hits.append((row,passage))
    parents={}
    if args.show_parent and args.config in PARENTS:
        wanted={r["document_id"] for r,_ in hits[:args.limit]}
        parents={r["document_id"]:r for r in load_dataset(args.dataset,name=PARENTS[args.config],split="corpus",revision=args.revision,token=False) if r["document_id"] in wanted}
    for row,passage in hits[:args.limit]:
        parent=parent_context(row,parents[row["document_id"]],passage,args.context_chars) if parents else None
        print(json.dumps({"document_id":row["document_id"],"title":row.get("title"),
            "source_sequence":row.get("source_sequence",row.get("heading_raw")),"source_id":row["source_id"],
            "capture_timestamp_utc":row["capture_timestamp_utc"],"text_sha256":row["text_sha256"],
            "match":passage,"parent":parent,"source_url":row["source_url"]},ensure_ascii=False))
    print(f"{matched_rows} matching {args.config} rows from {len(matching_documents)} parent documents; {filtered} rows passed metadata filters out of {len(rows)}. Capture dates do not establish legal force.")
    if args.open_source and hits:webbrowser.open(hits[0][0]["source_url"])


if __name__=="__main__":main()
