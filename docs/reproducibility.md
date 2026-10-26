# Load, verify and reproduce

## Public loading

CPython 3.12, `requirements.lock` and a normal `pip install --no-deps .` are sufficient for the README's real text example and `scripts/verify_text_release.py`. Both accept `--dataset` (Hub ID or local dataset folder) and `--revision` (immutable Hub commit). No private collection, Poppler, authentication or model service is required to load/check the published six Parquet configurations, all split `corpus`, plus separately indexed normative annex assets. The verifier checks public structure and review hashes; it cannot reconstruct or authenticate unavailable original response/PDF bytes. See official [loading](https://huggingface.co/docs/datasets/loading), [card](https://huggingface.co/docs/hub/datasets-cards) and [configuration](https://huggingface.co/docs/hub/datasets-data-files-configuration) documentation.

## Compatible files supplied by a user

```bash
saudi-legal capture-moj-case --response-file "$SAVED_RESPONSE_JSON"   --source-url "$OFFICIAL_CASE_URL" --captured-at "$UTC_CAPTURE_TIME" --output "$NEW_PRIVATE_CAPTURE"
saudi-legal capture-moj-legislation --response-file "$SAVED_RESPONSE_JSON"   --source-url "$OFFICIAL_LEGISLATION_URL" --captured-at "$UTC_CAPTURE_TIME" --output "$NEW_PRIVATE_CAPTURE"
```

These adapters validate an already acquired supported official API response and URL; they do not acquire it or authenticate a supplied capture time. Case fields are complete source components; instrument units retain source hierarchy/IDs and HTML-derived tables/text. Use a separate new destination and your own source evidence and review.

For BOE, `capture-text --text-file FILE --title TITLE --source-url URL --captured-at ISO --output NEW_JSON` accepts a supplied full page with the expected body marker; add `--body-only` for a user-isolated body. It preserves supplied bytes and records the input method rather than claiming browser capture. `audit-capture --json-folder DIR --pdf-folder DIR --original-root DIR --output NEW_DIR --pdftotext pdftotext` uses same-basename JSON/PDF pairs and separately installed Poppler. `refine-capture --records JSONL --audit JSONL --pdf-text-folder DIR --reviews JSON --output NEW_DIR` requires exact source-backed decisions; it does not guess missing material.

```bash
saudi-legal prepare-text-release --laws "$INSTRUMENTS_JSONL" --spans "$UNITS_JSONL"   --judgments "$COURTS_JSONL" --boe "$BOE_JSONL" --boe-spans "$BOE_SPANS_JSONL"   --decisions "$EXACT_REVIEW_REGISTRY_JSON" --output "$NEW_DATASET_DIR"
```

Supply only relevant optional family inputs. The final gate requires supported rights/quality/privacy and metadata/structure projection hashes and writes structured data/card scaffolding to a fresh directory. A reviewed card, source-specific rights/quality notices, correction/relationship receipts and checksums are separate packaging steps. The supplied empty rights example is not actual permission. `prepare-public` and `build`/`verify` retain older local workflows; legacy `verify` is not the six-configuration release verifier. `catalogue` remains metadata-only and requires UTC timestamps (`Z`/`+00:00`); local text capture can accept other aware offsets.

## Exact historical reconstruction limits

Published hashes, source URLs, capture/version labels, structure and correction receipts make the public artifact inspectable. Exact historical acquisition still needs the private 2025 JSON/PDF captures and the separately captured current responses/images, matching Poppler behavior, source investigations and private contextual decisions. Original scraper/recovery/comparator scripts, raw captures, source PDFs and private identifying review contexts are not distributed. The public CLI is an input adapter/exporter, not a turnkey recreation of that acquisition investigation. Current official downloads can differ in wording, masking or version.

The offline synthetic fixture reproduces software behavior independently and never fetches its synthetic BOE-shaped identifier. Tests are regression evidence, not legal-content accuracy or platform-universal certification. Stable text/hash/offset results do not imply byte-identical timing journals. Use a pinned release and dataset revision when citing results.

Case conversion accepts only checked paragraph/line-break formatting attribute-free unordered lists, exactly observed paragraph alignment, and inherited vertical-alignment or transparent 14pt spans; unknown/active markup is rejected rather than stripped blindly. Source HTML/text hashes and all populated fields remain evidenced. This validation cannot establish that a supplied official-looking response was truly acquired from the publisher.
