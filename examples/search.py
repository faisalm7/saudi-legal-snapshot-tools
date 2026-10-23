"""Offline lexical demonstration, not an expert-validated retrieval benchmark."""
import argparse
from pathlib import Path
import re
from datasets import load_dataset
from saudi_legal.core import normalize_search


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True, help="Local dataset candidate directory")
    p.add_argument("--query", default="مصانع المياه")
    p.add_argument("--config", default="laws", help="Keep laws, judgments and circulars distinct")
    p.add_argument("--top-k", type=int, default=3)
    args = p.parse_args()
    ds = load_dataset(str(Path(args.dataset).resolve()), name=args.config, split="corpus")
    terms = set(re.findall(r"\w+", normalize_search(args.query)))
    scores = []
    for row in ds:
        words = set(re.findall(r"\w+", row["text_search_ar"]))
        score = len(terms & words)
        if score:
            scores.append((score, row["document_id"], row))
    for score, _, r in sorted(scores, key=lambda item: (-item[0], item[1]))[:args.top_k]:
        print(r["title"])
        print(f"Matched query terms: {score}; captured {r['capture_timestamp_utc']}")
        print(r["text_ar"][:240])
        print(f"Source citation: {r['source_url']} (source ID {r['source_id']})")
        print(f"Version ID: {r['document_id']}\n")


if __name__ == "__main__":
    main()
