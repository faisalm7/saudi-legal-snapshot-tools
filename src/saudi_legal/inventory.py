"""Metadata-first inventory with isolated reads and explicit cloud placeholders."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
from .core import canonical, sha256, source_id, VERSION

FOLDERS = ("cases", "grievances", "BOE_pdfs", "BOE_text_json", "BOE_text_md", "processed", "processed_repaired", "repaired", "legislation", "published_laws", "published_laws_json", "qadha_pdfs", "sama_circulars_pdf", "sama_laws", "books", "aaoifi")
DATALLESS = 0x40000000  # macOS SF_DATALESS, absent on other systems


def family(rel):
    parts = Path(rel).parts
    if parts[0] in ("processed", "processed_repaired") and len(parts) > 1:
        return parts[1]
    return {"cases": "moj_cases", "grievances": "grievances", "BOE_pdfs": "boe", "BOE_text_json": "boe", "BOE_text_md": "boe", "legislation": "moj_legislation", "qadha_pdfs": "qadha_folder_unverified", "books": "religious_texts_excluded", "aaoifi": "private_standards_excluded"}.get(parts[0], parts[0])


def inspect_file(path):
    """Executed in a subprocess; raw text returned only to private local state."""
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    result = {"sha256": digest.hexdigest(), "parse_status": "not_parsed"}
    if path.suffix.lower() == ".json":
        if path.stat().st_size > 32 * 1024 * 1024:
            result["parse_status"] = "json_size_limit_deferred"
            return result
        try:
            data = path.read_bytes()
            obj = json.loads(data)
            if not isinstance(obj, dict):
                raise ValueError()
            s = obj.get("source") or {}
            if not isinstance(s, dict):
                s = {}
            url = s.get("url") or obj.get("source_url")
            result.update(parse_status="json_parsed", source_url=url if isinstance(url, str) else None, source_id=source_id(url), observed_capture_date=s.get("captured_at_utc"), document_type="official_legal_instrument" if source_id(url) else None)
            if path.parent.name == "BOE_text_json":
                result["private_source_json"] = data.decode("utf-8")
        except (ValueError, TypeError, UnicodeError):
            result["parse_status"] = "json_parse_error"
    elif path.suffix.lower() == ".pdf":
        with path.open("rb") as stream:
            signature = stream.read(5)
        result["parse_status"] = "pdf_signature_verified_not_extracted" if signature == b"%PDF-" else "invalid_pdf_signature"
    else:
        result["parse_status"] = "hashed_not_parsed"
    return result


def run_inventory(root, state, timeout=3., workers=4):
    root, state = Path(root).resolve(), Path(state).resolve()
    if state == root or root in state.parents or state in root.parents:
        raise ValueError("Private state must be outside original collection and must not contain it")
    if state.exists() and any(p.is_symlink() for p in state.rglob("*")):
        raise ValueError("Private state must not contain symlinks")
    state.mkdir(parents=True, exist_ok=True)
    context_path = state / "inventory-context.json"
    if context_path.exists():
        prior_root = Path(json.loads(context_path.read_text())["original_root"]).resolve()
        if prior_root != root:
            raise ValueError("Private checkpoint state belongs to a different original collection")
    elif (state / "inventory-checkpoint.jsonl").exists():
        raise ValueError("Checkpoint root cannot be verified; use a fresh private state directory")
    context_path.write_text(canonical({"original_root": str(root), "pipeline_version": VERSION}))
    (state / "source-json").mkdir(exist_ok=True)
    checkpoint = state / "inventory-checkpoint.jsonl"
    cached = {}
    if checkpoint.exists():
        for line in checkpoint.read_text().splitlines():
            try:
                entry = json.loads(line)
                cached[entry["relative_local_path"]] = entry
            except (ValueError, KeyError):
                # An interrupted final line is safely retried.
                continue
    files = []
    for folder in FOLDERS:
        base = root / folder
        if base.exists():
            files.extend(p for p in base.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix.lower() in (".json", ".pdf", ".md", ".txt"))
    files.sort(key=lambda p: p.relative_to(root).as_posix())

    def one(path):
        rel = path.relative_to(root).as_posix()
        st = path.stat()
        signature = [st.st_size, st.st_mtime_ns, getattr(st, "st_flags", 0), getattr(st, "st_blocks", None)]
        if rel in cached and cached[rel].get("stat_signature") == signature and cached[rel]["parse_status"] not in ("read_timeout", "read_failure"):
            old = cached[rel].copy()
            if not rel.startswith("BOE_text_json/") or (state / "source-json" / f"{old['sha256']}.json").exists() or not old["sha256"]:
                return old
        row = {"source_family": family(rel), "relative_local_path": rel, "file_size": st.st_size, "sha256": None, "parse_status": None, "source_id": None, "source_url": None, "observed_capture_date": None, "document_type": None, "availability": "local", "disposition": "deferred", "reason": "out_of_selected_scope", "allocated_blocks": getattr(st, "st_blocks", None), "stat_signature": signature}
        if getattr(st, "st_flags", 0) & DATALLESS:
            row.update(availability="cloud_placeholder", parse_status="unavailable_not_read", reason="cloud_placeholder_no_local_content")
            return row
        try:
            proc = subprocess.run([sys.executable, "-m", "saudi_legal.cli", "_inspect", str(path)], capture_output=True, timeout=timeout)
            if proc.returncode:
                row.update(parse_status="read_failure", reason="isolated_read_failed")
                return row
            info = json.loads(proc.stdout)
            raw = info.pop("private_source_json", None)
            row.update(info)
            if raw is not None:
                (state / "source-json" / f"{row['sha256']}.json").write_text(raw, encoding="utf-8")
        except subprocess.TimeoutExpired:
            row.update(availability="read_timeout", parse_status="read_timeout", reason="isolated_read_timeout")
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        with (state / "manifest.jsonl.tmp").open("w", encoding="utf-8") as out, checkpoint.open("a", encoding="utf-8") as journal:
            for i, row in enumerate(pool.map(one, files)):
                out.write(canonical(row))
                journal.write(canonical(row))
                if i % 100 == 0:
                    journal.flush()
                if i % 5000 == 0:
                    out.flush()
                    print(f"inventory {i}/{len(files)}", flush=True)
    (state / "manifest.jsonl.tmp").replace(state / "manifest.jsonl")
    return len(files)
