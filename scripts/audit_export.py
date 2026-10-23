"""Inspect exact public file trees and all Parquet strings. No remote services."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import pyarrow.parquet as pq

PRIVATE_PATH = re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+")
SECRETS = re.compile(r"(?<![A-Za-z0-9_])(?:hf_[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
BAD_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", "vectorstore", "build", "dist"}
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+966|00966|05)\d{8,9}(?!\d)")


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def audit(dataset, code):
    findings = []
    files = []
    for kind, root in (("dataset", Path(dataset)), ("code", Path(code))):
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            files.append({"candidate": kind, "path": rel, "bytes": p.stat().st_size})
            if p.is_symlink() or set(p.relative_to(root).parts) & BAD_PARTS or ".egg-info" in rel or p.suffix.lower() in (".pdf", ".log", ".pyc") or p.name.startswith(".env"):
                findings.append({"candidate": kind, "path": rel, "type": "unintended_file"})
                continue
            if p.suffix == ".parquet":
                values = strings(pq.read_table(p).to_pylist())
            else:
                try:
                    values = [p.read_text(encoding="utf-8")]
                except UnicodeError:
                    findings.append({"candidate": kind, "path": rel, "type": "unrecognized_binary"})
                    continue
            for value in values:
                if PRIVATE_PATH.search(value):
                    findings.append({"candidate": kind, "path": rel, "type": "private_absolute_path"})
                if SECRETS.search(value):
                    findings.append({"candidate": kind, "path": rel, "type": "credential_pattern"})
    contacts = Counter()
    rows = 0
    for p in sorted(Path(dataset).rglob("*.parquet")):
        for row in pq.read_table(p).to_pylist():
            if "text_ar" not in row:
                continue
            rows += 1
            contacts["documents_with_email_pattern"] += bool(EMAIL.search(row["text_ar"]))
            contacts["documents_with_saudi_mobile_pattern"] += bool(PHONE.search(row["text_ar"]))
            contacts["documents_with_long_digit_runs"] += bool(re.search(r"(?<!\d)\d{10,}(?!\d)", row["text_ar"]))
    return {"files": len(files), "total_bytes": sum(f["bytes"] for f in files), "rows_scanned": rows, "findings": findings, "contact_pattern_triage": dict(contacts), "limitations": "Pattern checks are triage, not anonymization, permission clearance or legal review."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True); p.add_argument("--code", required=True); p.add_argument("--report", required=True)
    args = p.parse_args()
    result = audit(args.dataset, args.code)
    Path(args.report).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if result["findings"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
