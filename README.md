# Saudi legal snapshot tools · v0.3

Local tools for inspecting historical Saudi legal captures, preserving source hashes, and mapping PDF-evidenced headings to exact captured-text offsets. The companion [468-row source catalogue](https://huggingface.co/datasets/Faisal73/saudi-legal-source-catalogue-2025) describes the examined BOE captures from August 2025 through factual metadata, source links, hashes and processing diagnostics. It contains **no legal bodies, article text, PDF extracts or judgment facts**. See the [catalogue schema](docs/catalogue-schema.md).

The catalogue is a historical discovery and audit resource. It is not a complete or current statement of Saudi law, and it does not establish new substantive coverage. Actual source texts remain private: zero examined legal-text records pass the current publication review. [Rights and license scope](docs/source-rights.md) distinguishes catalogue contributions, MIT tools and the underlying sources.

## Install and try the invented example

Use CPython 3.12 from the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps .
.venv/bin/python -m pytest -q -p no:cacheprovider -o pythonpath=
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 .venv/bin/python scripts/fixture_demo.py --output demo-work
```

The demo inventories invented Arabic text, makes a local sample, checks native Parquet loading and prints an illustrative lexical-search citation. Its synthetic BOE-shaped identifier and example.org rights URL are never fetched. They do not demonstrate real legal retrieval. Dependency installation requires package downloads; the demo needs no private inputs, Poppler, paid API or model service.

## Find a historical source

Run the metadata search example:

```bash
.venv/bin/python examples/catalogue.py \
  --dataset Faisal73/saudi-legal-source-catalogue-2025 \
  --query 'الأحداث'
```

The example searches catalogue metadata and prints the real recorded BOE URL. Add `--open-source` to open a result in your browser. The live page may have changed since the recorded capture. This example does not retrieve, reconstruct or license the historical legal body.

## Process source files you acquired yourself

`capture-text` wraps an already acquired UTF-8 BOE page-text dump in the supported JSON format. Supply the title, canonical Arabic BOE URL and timezone-aware capture timestamp yourself:

```bash
.venv/bin/python -m saudi_legal.cli capture-text \
  --text-file "$ACQUIRED_UTF8_TEXT" --title "$DOCUMENT_TITLE" \
  --source-url "$CANONICAL_BOE_URL" --captured-at "$CAPTURE_TIME_ISO8601" \
  --output "$NEW_CAPTURE_JSON"
```

For a page-text dump, include the expected portal body marker. For an already isolated legal body, add `--body-only`. Both paths must pass validation. This command is not a scraper and does not authenticate your capture time or the page's completeness; its input-method metadata records user-supplied text. See [input and reproduction requirements](docs/reproducibility.md).

For article alignment, install Poppler's `pdftotext` separately. Use JSON/PDF folders with matching file basenames and a separate private output tree:

```bash
.venv/bin/python -m saudi_legal.cli audit-capture \
  --json-folder "$CAPTURE_JSON_DIR" --pdf-folder "$CAPTURE_PDF_DIR" \
  --original-root "$ORIGINAL_COLLECTION_ROOT" --output "$PRIVATE_AUDIT_DIR" \
  --pdftotext pdftotext --timeout 20 --workers 4
```

This writes private captured text, exact article spans, extracted PDF evidence and native Parquet configurations `laws` and `article_spans`. It can defer ambiguous structure; it does not repair missing provisions. Keep this output private unless it passes its own rights, quality and privacy review. The historical run processed 468 JSON/PDF pairs, yielding **9,305 spans across 350 documents**, with structure deferred for 118. These are processing results, not complete-law or accuracy claims. See [quality limits](docs/quality.md) and [architecture](docs/decision-record.md).

## Export metadata or separately cleared text

The catalogue command projects an explicit metadata allowlist from private audit records. It writes four structured files: `documents.parquet`, `SCHEMA.json`, `quality.json` and `preview.jsonl`. It does not export bodies or article rows or author a dataset card:

```bash
.venv/bin/python -m saudi_legal.cli catalogue \
  --records "$PRIVATE_AUDIT_DIR/records.jsonl" \
  --audit "$PRIVATE_AUDIT_DIR/audit.jsonl" --output "$NEW_CATALOGUE_DIR"
```

For a new publication, review the projected metadata and separately author an appropriate README dataset card, license scope and checksums. Catalogue timestamps must express UTC (`Z` or `+00:00`); the text adapter can accept other aware timezones for local processing. The existing catalogue's CC0 dedication does not clear arbitrary inputs supplied to the tool.

Legal-text preparation uses a **separate** gate:

```bash
.venv/bin/python -m saudi_legal.cli prepare-public \
  --records "$PRIVATE_AUDIT_DIR/records.jsonl" \
  --decisions "$REVIEWED_RIGHTS_REGISTRY" --output "$NEW_TEXT_CANDIDATE_DIR"
```

The registry must bind supported rights, quality and privacy decisions to exact source and text hashes. The gate checks fields, not the truth of the decision. The supplied [empty example](docs/rights-decisions.example.json) selects nothing; the examined actual legal texts likewise remain withheld. `build` and `verify` support legacy local processing and the synthetic demo; technical acceptance is not publication eligibility. None of these commands creates remote repositories or uploads files.

## Reproduction and attribution

Anyone can run the fixtures and process compatible inputs they supply. Reproducing the historical results requires the exact private 2025 JSON/PDF captures and compatible extraction dependencies; those captures, recovery scripts and comparator downloads are not distributed. Current website downloads are not assumed equivalent. [Reproduction limits](docs/reproducibility.md) explain the distinction.

Development, testing and evidence review were AI assisted. No government affiliation, source-document authorship, human/legal-expert approval or retrieval benchmark is claimed. MIT covers the new code, documentation and invented fixtures. CC0 covers the publisher's original catalogue compilation and analytic contributions only; neither license grants rights over underlying legal texts, source websites or dependencies. The [comparison](docs/comparison.md) acknowledges substantial existing coverage and capture losses, alongside the conservative tooling contribution.
