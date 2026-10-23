import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from .core import canonical, deduplicate, make_record, sha256, VERSION


def build(state, output, selected_hashes=None, exclusions=None):
    import pyarrow as pa
    import pyarrow.parquet as pq
    state, output = Path(state), Path(output)
    context = state / "inventory-context.json"
    if context.exists():
        original = Path(json.loads(context.read_text())["original_root"]).resolve()
        if output.resolve() == original or original in output.resolve().parents or output.resolve() in original.parents:
            raise ValueError("Output must be outside original collection and must not contain it")
    if output.resolve() == state.resolve() or state.resolve() in output.resolve().parents or output.resolve() in state.resolve().parents:
        raise ValueError("Private state and public output must be separate non-nested directories")
    if state.is_symlink() or (state.exists() and any(p.is_symlink() for p in state.rglob("*"))):
        raise ValueError("Private state must not contain symlinks")
    if output.is_symlink() or (output.exists() and any(p.is_symlink() for p in output.rglob("*"))):
        raise ValueError("Public output must not contain symlinks")
    state.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    (output / "data").mkdir(exist_ok=True)
    manifests = [json.loads(x) for x in (state / "manifest.jsonl").read_text().splitlines()]
    selected = set(json.loads(Path(selected_hashes).read_text())) if selected_hashes else None
    exclusion_rows = json.loads(Path(exclusions).read_text()) if exclusions else []
    excluded = {e["source_file_sha256"]: e for e in exclusion_rows}
    records, seen_files, seen_text, decisions = [], set(), set(), []
    for row in manifests:
        row.update(disposition="deferred", reason="out_of_selected_scope")
        if row["source_family"] in ("hadith_books", "religious_texts_excluded", "aaoifi", "private_standards_excluded"):
            row.update(disposition="rejected", reason="explicit_source_family_exclusion")
        elif row["source_family"] == "boe" and not row["relative_local_path"].startswith("BOE_text_json/"):
            row.update(reason="companion_or_legacy_extraction_not_selected")
        elif row["source_family"] in ("moj_cases", "grievances"):
            row.update(reason="judgment_rights_provenance_privacy_unresolved")
        elif row["availability"] != "local":
            row.update(reason="source_content_unavailable")
        if not row["relative_local_path"].startswith("BOE_text_json/"):
            continue
        if row["parse_status"] != "json_parsed" or not row["sha256"]:
            continue
        try:
            raw = (state / "source-json" / f"{row['sha256']}.json").read_bytes()
            if sha256(raw) != row["sha256"]:
                raise ValueError("private_checkpoint_hash_mismatch")
            if row["sha256"] in excluded:
                row.update(disposition="deferred", reason=excluded[row["sha256"]]["reason"])
                decisions.append({"source_file_sha256": row["sha256"], "disposition": row["disposition"], "reason": row["reason"]})
                continue
            if selected is not None and row["sha256"] not in selected:
                row.update(reason="not_in_frozen_release_input")
                continue
            r = make_record(json.loads(raw), row["sha256"])
            if "source_refers_to_omitted_illustration" in r["quality_flags"]:
                row.update(disposition="deferred", reason="source_illustration_not_captured")
                decisions.append({"source_file_sha256": row["sha256"], "disposition": row["disposition"], "reason": row["reason"]})
                continue
            if row["sha256"] in seen_files or r["text_sha256"] in seen_text:
                row.update(disposition="duplicate", reason="exact_file_or_legal_text")
            else:
                row.update(disposition="accepted", reason="validated_official_body")
            seen_files.add(row["sha256"])
            seen_text.add(r["text_sha256"])
            records.append(r)
        except (ValueError, OSError) as exc:
            row.update(disposition="rejected", reason=str(exc) if isinstance(exc, ValueError) else "checkpoint_read_error")
        decisions.append({"source_file_sha256": row["sha256"], "disposition": row["disposition"], "reason": row["reason"]})
    unique = deduplicate(records)
    if selected is not None:
        observed = {r["source_file_sha256"] for r in records}
        if selected != observed:
            raise ValueError("Frozen selected input hashes are missing or newly ineligible; refusing a partial rebuild")
    if not unique:
        raise ValueError("No eligible records; no empty dataset will be packaged")
    # Exact duplicates retain all provenance in the canonical record.
    # Near duplicates are diagnostic only; never removed or merged.
    near = []
    for i, a in enumerate(unique):
        ta = set(a["text_search_ar"].split())
        for b in unique[i+1:]:
            tb = set(b["text_search_ar"].split())
            sim = len(ta & tb) / max(1, len(ta | tb))
            if sim >= .8:
                near.append({"document_id_a": a["document_id"], "document_id_b": b["document_id"], "token_set_jaccard": round(sim, 5), "action": "retain_separately_review_flag_only"})
    # Explicit nullable schema prevents unknown article/date values becoming null-type fields.
    types = {k: pa.string() for k in unique[0]}
    for k in ("transformations", "quality_flags"):
        types[k] = pa.list_(pa.string())
    types["article_count"] = pa.int32()
    types["removed_amendment_control_count"] = pa.int32()
    types["provenance"] = pa.list_(pa.struct([(k, pa.string()) for k in ("source_url", "capture_timestamp_utc", "source_file_sha256", "source_text_sha256")]))
    schema = pa.schema(list(types.items()))
    for old in (output / "data").glob("laws-*.parquet"):
        old.unlink()
    for n, start in enumerate(range(0, len(unique), 100)):
        table = pa.Table.from_pylist(unique[start:start+100], schema=schema)
        pq.write_table(table, output / "data" / f"laws-{n:05d}.parquet", compression="zstd", row_group_size=32, write_page_index=True)
    (output / "preview.jsonl").write_text("".join(canonical(r) for r in unique[:3]), encoding="utf-8")
    sizes = {r["sha256"]: r.get("file_size") for r in manifests if r["sha256"]}
    public_manifest = [{"document_id": r["document_id"], "source_family": r["source_family"], "source_id": r["source_id"], "source_url": r["source_url"], "capture_timestamp_utc": r["capture_timestamp_utc"], "source_file_sha256": r["source_file_sha256"], "source_file_size": sizes.get(r["source_file_sha256"]), "source_text_sha256": r["source_text_sha256"], "text_sha256": r["text_sha256"], "parquet_path": f"data/laws-{i//100:05d}.parquet", "row_index_in_shard": i % 100, "text_characters": len(r["text_ar"]), "parse_status": "validated_official_body"} for i, r in enumerate(unique)]
    (output / "document-manifest.jsonl").write_text("".join(canonical(r) for r in public_manifest), encoding="utf-8")
    (state / "records.jsonl").write_text("".join(canonical(r) for r in unique), encoding="utf-8")
    (state / "manifest.jsonl").write_text("".join(canonical(r) for r in manifests), encoding="utf-8")
    selected_hash_list = sorted(r["source_file_sha256"] for r in records)
    (output / "input-hashes.json").write_text(json.dumps(sorted(set(selected_hash_list)), indent=2) + "\n")
    (output / "decisions.jsonl").write_text("".join(canonical(d) for d in decisions))
    (output / "near-duplicates.jsonl").write_text("".join(canonical(d) for d in near))
    (output / "quality-exclusions.json").write_text(json.dumps(exclusion_rows, ensure_ascii=False, indent=2) + "\n")
    statuses = Counter(r["disposition"] for r in manifests)
    summary = {"pipeline_version": VERSION, "discovered_files": len(manifests), "dispositions": dict(sorted(statuses.items())), "reconciliation_valid": sum(statuses.values()) == len(manifests), "disposition_reasons": dict(sorted(Counter(r["reason"] for r in manifests).items())), "records": len(unique), "eligible_input_json_files": len(records), "exact_duplicate_text_or_file_inputs": len(records)-len(unique), "near_duplicate_pairs_flagged": len(near), "availability": dict(Counter(r["availability"] for r in manifests)), "hashed_files": sum(r["sha256"] is not None for r in manifests), "source_family_file_counts": dict(sorted(Counter(r["source_family"] for r in manifests).items())), "candidate_quality_flags": dict(sorted(Counter(f for r in unique for f in r["quality_flags"]).items())), "metadata_non_null": {k: sum(r[k] is not None for r in unique) for k in unique[0]}, "source_status_at_capture": dict(Counter(str(r["source_reported_status_at_capture"]) for r in unique)), "capture_min": min(r["capture_timestamp_utc"] for r in unique), "capture_max": max(r["capture_timestamp_utc"] for r in unique)}
    (output / "metrics.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    return summary


def verify(output):
    import datasets
    import pyarrow.parquet as pq
    import yaml
    output = Path(output)
    card = (output / "README.md").read_text()
    meta = yaml.safe_load(card.split("---", 2)[1])
    config = next(c for c in meta["configs"] if c["config_name"] == "laws")
    spec = config["data_files"][0]
    files = sorted(output.glob(spec["path"]))
    if not files:
        raise ValueError("README config resolves to no Parquet files")
    all_ids = []
    for f in files:
        pf = pq.ParquetFile(f)
        if not pf.metadata.num_rows:
            raise ValueError("Empty shard")
        ds = datasets.load_dataset("parquet", data_files={spec["split"]: str(f)}, split=spec["split"])
        for r in ds:
            if sha256(r["text_ar"].encode()) != r["text_sha256"]:
                raise ValueError("Text hash mismatch")
            if not r["provenance"]:
                raise ValueError("Lost provenance")
            all_ids.append(r["document_id"])
    metrics = json.loads((output / "metrics.json").read_text())
    if len(set(all_ids)) != len(all_ids) or len(all_ids) != metrics["records"]:
        raise ValueError("IDs or record count mismatch")
    # Exercise native local repository loading and its card-defined configuration too.
    native = datasets.load_dataset(str(output.resolve()), name="laws", split="corpus")
    if len(native) != len(all_ids):
        raise ValueError("Native card loading count mismatch")
    return {"verified_shards": len(files), "verified_rows": len(all_ids), "datasets_version": datasets.__version__, "card_config_native_load": True}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inventory")
    p.add_argument("--root", required=True); p.add_argument("--state", required=True)
    p.add_argument("--timeout", type=float, default=3); p.add_argument("--workers", type=int, default=4)
    p = sub.add_parser("build")
    p.add_argument("--state", required=True); p.add_argument("--output", required=True); p.add_argument("--selected-hashes"); p.add_argument("--exclusions")
    p = sub.add_parser("verify"); p.add_argument("--output", required=True)
    p = sub.add_parser("audit-capture")
    p.add_argument("--json-folder",required=True); p.add_argument("--pdf-folder",required=True);p.add_argument("--output",required=True)
    p.add_argument("--timeout",type=float,default=20);p.add_argument("--workers",type=int,default=4);p.add_argument("--pdftotext",default="pdftotext");p.add_argument("--original-root")
    p = sub.add_parser("prepare-public")
    p.add_argument("--records",required=True);p.add_argument("--decisions",required=True);p.add_argument("--output",required=True)
    p = sub.add_parser("catalogue")
    p.add_argument("--records",required=True);p.add_argument("--audit",required=True);p.add_argument("--output",required=True)
    p = sub.add_parser("capture-text")
    p.add_argument("--text-file",required=True);p.add_argument("--title",required=True);p.add_argument("--source-url",required=True)
    p.add_argument("--captured-at",required=True);p.add_argument("--output",required=True);p.add_argument("--body-only",action="store_true")
    p = sub.add_parser("refine-capture")
    p.add_argument("--records",required=True);p.add_argument("--audit",required=True);p.add_argument("--pdf-text-folder",required=True)
    p.add_argument("--reviews",required=True);p.add_argument("--output",required=True)
    p = sub.add_parser("capture-moj-supreme")
    p.add_argument("--response-file",required=True);p.add_argument("--source-url",required=True)
    p.add_argument("--captured-at",required=True);p.add_argument("--output",required=True)
    p = sub.add_parser("capture-moj-legislation")
    p.add_argument("--response-file",required=True);p.add_argument("--source-url",required=True)
    p.add_argument("--captured-at",required=True);p.add_argument("--output",required=True)
    p = sub.add_parser("capture-moj-case")
    p.add_argument("--response-file",required=True);p.add_argument("--source-url",required=True)
    p.add_argument("--captured-at",required=True);p.add_argument("--output",required=True)
    p = sub.add_parser("prepare-text-release",aliases=["prepare-moj-text"])
    p.add_argument("--laws");p.add_argument("--spans");p.add_argument("--judgments")
    p.add_argument("--boe");p.add_argument("--boe-spans")
    p.add_argument("--decisions",required=True);p.add_argument("--output",required=True)
    p = sub.add_parser("_inspect"); p.add_argument("path")
    args = parser.parse_args()
    if args.cmd == "_inspect":
        from .inventory import inspect_file
        print(canonical(inspect_file(Path(args.path))), end="")
    elif args.cmd == "inventory":
        from .inventory import run_inventory
        print(run_inventory(args.root, args.state, args.timeout, args.workers))
    elif args.cmd == "build":
        print(json.dumps(build(args.state, args.output, args.selected_hashes, args.exclusions), indent=2))
    elif args.cmd == "audit-capture":
        from .audit import audit_capture
        print(json.dumps(audit_capture(args.json_folder,args.pdf_folder,args.output,args.timeout,args.workers,args.pdftotext,args.original_root),ensure_ascii=False,indent=2))
    elif args.cmd == "catalogue":
        from .catalogue import export_catalogue
        print(json.dumps(export_catalogue(args.records,args.audit,args.output),ensure_ascii=False,indent=2))
    elif args.cmd == "capture-text":
        from .inputs import capture_text
        print(json.dumps(capture_text(args.text_file,args.title,args.source_url,args.captured_at,args.output,args.body_only),ensure_ascii=False,indent=2))
    elif args.cmd == "prepare-public":
        from .rights_gate import prepare_public
        print(json.dumps(prepare_public(args.records,args.decisions,args.output),ensure_ascii=False,indent=2))
    elif args.cmd == "refine-capture":
        from .refine import refine_capture
        print(json.dumps(refine_capture(args.records,args.audit,args.pdf_text_folder,args.reviews,args.output),ensure_ascii=False,indent=2))
    elif args.cmd == "capture-moj-supreme":
        from .moj import capture_supreme
        print(json.dumps(capture_supreme(args.response_file,args.source_url,args.captured_at,args.output),ensure_ascii=False,indent=2))
    elif args.cmd == "capture-moj-legislation":
        from .moj_legislation import capture_legislation
        print(json.dumps(capture_legislation(args.response_file,args.source_url,args.captured_at,args.output),ensure_ascii=False,indent=2))
    elif args.cmd == "capture-moj-case":
        from .moj import capture_case
        print(json.dumps(capture_case(args.response_file,args.source_url,args.captured_at,args.output),ensure_ascii=False,indent=2))
    elif args.cmd in ("prepare-moj-text","prepare-text-release"):
        from .text_release import prepare_moj_text
        print(json.dumps(prepare_moj_text(args.laws,args.spans,args.judgments,args.decisions,args.output,args.boe,args.boe_spans),ensure_ascii=False,indent=2))
    else:
        print(json.dumps(verify(args.output), indent=2))


if __name__ == "__main__":
    main()
