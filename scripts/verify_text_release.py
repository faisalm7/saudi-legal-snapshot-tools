"""Verify public hashes, source structure and exact article offsets without private inputs.

This checks release integrity, not legal correctness or the fidelity of unavailable
original API bytes. It neither fetches official sources nor changes any records.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from datasets import load_dataset
from huggingface_hub import hf_hub_download
from saudi_legal.core import sha256, canonical
from saudi_legal.text_release import _expected_native_units, projection_sha256


def read_annex_asset(dataset, name, revision=None):
    if Path(name).name != name or not name.endswith('.jpg'):
        raise ValueError('Unexpected annex asset path')
    local = Path(dataset).is_dir()
    path = Path(dataset)/name if local else Path(hf_hub_download(
        dataset, name, repo_type='dataset', revision=revision, token=False))
    # Local export files must be ordinary files. The Hub's own snapshot cache
    # normally uses symlinks to content-addressed blobs, whose bytes we hash.
    if local and path.is_symlink():
        raise ValueError('Annex asset must be an ordinary file')
    return path.read_bytes()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset",default="Faisal73/saudi-legal-text-snapshots")
    parser.add_argument("--revision",help="Pin an immutable dataset commit")
    args=parser.parse_args();local=Path(args.dataset).is_dir()
    def read(name):
        path=Path(args.dataset)/name if local else Path(hf_hub_download(args.dataset,name,repo_type="dataset",revision=args.revision,token=False))
        return path.read_text()
    def asset_bytes(name):
        return read_annex_asset(args.dataset, name, args.revision)
    metrics=json.loads(read("metrics.json"))
    reviews={r["document_id"]:r for r in map(json.loads,read("record-reviews.jsonl").splitlines())}
    counts={};parents={};boe_parents={};boe_units={};actual_articles=Counter();all_unit_ids=set();unit_ids={"article_spans":set(),"source_sections":set()}
    for config in ("laws","judgments","boe_documents","article_spans","source_sections","boe_article_spans"):
        if config not in metrics["configuration_rows"]:continue
        data=load_dataset(args.dataset,name=config,split="corpus",revision=args.revision,token=False)
        counts[config]=len(data)
        if len(data)!=metrics["configuration_rows"][config]:raise ValueError("Row count mismatch")
        for r in data:
            if sha256(r["text_ar"].encode())!=r["text_sha256"]:raise ValueError("Text hash mismatch")
            if config in ("laws","judgments","boe_documents"):
                d=reviews[r["document_id"]]
                if d["projection_sha256"]!=projection_sha256(r):raise ValueError("Reviewed metadata/structure hash mismatch")
                if config=="laws":
                    if sha256(r["source_sections_json"].encode())!=r["source_text_sha256"]:raise ValueError("Native hierarchy hash mismatch")
                    parents[r["document_id"]]=(r,_expected_native_units(r))
                elif config=="boe_documents":boe_parents[r["document_id"]]=r;boe_units[r["document_id"]]=[]
                elif r.get("source_components_json"):
                    components=json.loads(r["source_components_json"]);parts=[]
                    if len(components)!=r["source_component_count"]:raise ValueError("Judicial component count mismatch")
                    for c in components:
                        text=r["text_ar"][c["start_char"]:c["end_char"]];parts.append(text)
                        if sha256(text.encode())!=c["text_sha256"]:raise ValueError("Judicial component hash mismatch")
                    if "\n\n".join(parts)!=r["text_ar"]:raise ValueError("Judicial component boundaries mismatch")
            elif config=="boe_article_spans":
                p=boe_parents[r["document_id"]]
                if (p["text_ar"][r["start_char"]:r["end_char"]]!=r["text_ar"]
                    or p["text_ar"][r["start_char"]:r["body_start_char"]]!=r["heading_raw"]
                    or r["evidence_pdf_sha256"]!=p["source_pdf_sha256"] or r["source_url"]!=p["source_url"]
                    or r["source_id"]!=p["source_id"] or r["capture_timestamp_utc"]!=p["capture_timestamp_utc"]):
                    raise ValueError("BOE source/heading/span mismatch")
                original={k:v for k,v in r.items() if k not in ("span_id","source_id","source_url","capture_timestamp_utc")}
                boe_units[r["document_id"]].append(original)
            else:
                if r["span_id"] in all_unit_ids:raise ValueError("Duplicate source span")
                all_unit_ids.add(r["span_id"]);p,units=parents[r["document_id"]]
                unit_ids[config].add(r["span_id"])
                expected=units[r["source_section_id"]]
                if any(r[k]!=v for k,v in expected.items()):raise ValueError("Unit metadata/source/offset mismatch")
                if p["text_ar"][r["start"]:r["end"]]!=r["text_ar"]:raise ValueError("Article slice mismatch")
                if (config=="article_spans")!=(r["unit_kind"]=="article"):raise ValueError("Unit kind/configuration mismatch")
                if config=="article_spans":actual_articles[r["document_id"]]+=1
    for did,(r,_) in parents.items():
        if actual_articles[did]!=r["article_count"]:raise ValueError("Per-document article count mismatch")
    expected_ids={"article_spans":set(),"source_sections":set()}
    for _,units in parents.values():
        for unit in units.values():
            if not unit["text_ar"].strip():continue
            if unit["unit_kind"]=="structural" and not any(c.isalnum() for c in unit["text_ar"]):continue
            config="article_spans" if unit["unit_kind"]=="article" else "source_sections"
            expected_ids[config].add(unit["span_id"])
    if unit_ids!=expected_ids:raise ValueError("Published source-unit membership differs from native hierarchy")
    for did,parent in boe_parents.items():
        units=boe_units[did]
        if (parent["article_count"] is None and units) or (parent["article_count"] is not None and len(units)!=parent["article_count"]):
            raise ValueError("BOE article count mismatch")
        if [a["article_position"] for a in units]!=list(range(1,len(units)+1)):raise ValueError("BOE article position mismatch")
        if sha256("".join(canonical(u) for u in units).encode())!=reviews[did]["article_spans_sha256"]:
            raise ValueError("BOE article evidence projection differs from reviewed source")
    assets_verified=0
    annexes=metrics.get('annex_facsimiles')
    if annexes:
        pages=[json.loads(line) for line in read('boe-annex-pages.jsonl').splitlines()]
        if len(pages)!=annexes['pages']:raise ValueError('Annex page count mismatch')
        seen_assets=set()
        for page in pages:
            parent=boe_parents[page['document_id']]
            if (page['source_id']!=parent['source_id'] or page['parent_text_sha256']!=parent['text_sha256']
                or page['parent_source_url']!=parent['source_url']):
                raise ValueError('Annex parent/source binding mismatch')
            name=page['asset_path']
            if name in seen_assets:raise ValueError('Repeated annex asset')
            seen_assets.add(name);raw=asset_bytes(name)
            if len(raw)!=page['bytes'] or sha256(raw)!=page['source_image_sha256'] or not raw.startswith(b'\xff\xd8'):
                raise ValueError('Annex asset bytes/hash mismatch')
            assets_verified+=1
    print(json.dumps({"configuration_rows":counts,"reviewed_document_projections_verified":len(reviews),
        "published_source_units_verified":len(all_unit_ids)+sum(len(v) for v in boe_units.values()),
        "annex_image_assets_verified":assets_verified,
        "source_byte_retrieval_or_accuracy_certificate":False},indent=2))


if __name__=="__main__":main()
