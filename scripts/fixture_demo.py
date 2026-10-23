"""Reproduce a public one-record synthetic pipeline without private source files."""
import argparse
import json
from pathlib import Path
from saudi_legal.core import sha256
import shutil
import subprocess
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    base = Path(args.output).resolve()
    if base.exists():
        raise SystemExit("Choose a new demo output directory; existing files will not be overwritten")
    code = Path(__file__).resolve().parents[1]
    source = base / "source" / "BOE_text_json"
    source.mkdir(parents=True)
    shutil.copyfile(code / "fixtures" / "synthetic_boe.json", source / "synthetic.json")
    state, intermediate, output = base / "private-state", base / "private-build", base / "dataset"
    def run(*args):
        subprocess.run([sys.executable, "-m", "saudi_legal.cli", *map(str, args)], check=True)
    run("inventory", "--root", source.parent, "--state", state)
    run("build", "--state", state, "--output", intermediate)
    record = json.loads((state / "records.jsonl").read_text().splitlines()[0])
    registry = {"decisions": [{
        "document_id": record["document_id"], "decision": "supported",
        "text_sha256": record["text_sha256"], "source_file_sha256": record["source_file_sha256"],
        "quality_review": "pass", "privacy_review": "not_personal_data",
        "rights_basis": "Invented test fixture licensed with this code under MIT; not a legal text grant",
        "evidence_urls": ["https://example.org/invented-fixture-license"],
        "reason": "All fixture wording and identifiers are invented for this demonstration. The example.org URL is a non-fetched placeholder, not government authority."
    }]}
    decision_path = base / "synthetic-decisions.json"
    decision_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    run("prepare-public", "--records", state / "records.jsonl", "--decisions", decision_path, "--output", output)
    # The gate writes a draft card. Explicitly identify this runnable example.
    card = output / "README.md"
    card.write_text(card.read_text() + "\n## Synthetic demonstration only\nAll text and identifiers are invented. This is not legislation or a public corpus release. The fixture is MIT-licensed with the code.\n")
    from datasets import load_dataset
    loaded = load_dataset(str(output), name="laws", split="corpus")
    assert len(loaded) == 1
    assert sha256(loaded[0]["text_ar"].encode()) == loaded[0]["text_sha256"]
    demo = subprocess.run([sys.executable, str(code / "examples" / "search.py"), "--dataset", str(output), "--query", "البرمجيات"], check=True, capture_output=True, text=True)
    if "Source citation:" not in demo.stdout:
        raise RuntimeError("Synthetic lexical demonstration returned no source citation")
    print(demo.stdout)


if __name__ == "__main__":
    main()
