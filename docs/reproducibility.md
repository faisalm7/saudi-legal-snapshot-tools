# Reproduction and input requirements

The public tools reproduce software behavior through invented fixtures. The companion catalogue exposes factual source metadata and diagnostics for 468 historical BOE captures. It does not supply the captured bodies or PDFs needed to repeat that historical processing run.

## Supported local inputs

`capture-text` accepts an already acquired UTF-8 BOE page-text dump, a title, a canonical `https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/<UUID>/1` URL and a timezone-aware ISO capture timestamp. It writes a new JSON file with a SHA-256 binding to the supplied text. Page mode requires exactly one expected portal marker, `ن ص النظ ام`, followed by a sufficiently long Arabic body. `--body-only` accepts a user-isolated body and wraps it for the existing parser; unavailable issuance/publication metadata remains unknown. Both modes apply the source/body validation. Their input-method metadata distinguishes user-supplied page text from user-supplied body text rather than claiming an observed browser capture. The adapter does not fetch the URL, establish that the text came from it or reconstruct missing layout.

`audit-capture` reads compatible JSONs and same-basename PDFs from separate folders. Install Poppler's `pdftotext` executable outside pip and keep output separate from inputs and originals. Missing PDFs, failed extraction and non-unique heading mappings yield documented deferrals. PDF text supplies heading evidence; it never automatically replaces the captured DOM body. Outputs include source text, PDF extracts and detailed private evidence and should remain private pending a separate review.

`catalogue` needs the document and audit JSONL outputs from compatible processing and emits only its specified metadata columns. Capture timestamps for catalogue export must be UTC, expressed with `Z` or `+00:00`. Although `capture-text` accepts other timezone-aware timestamps for local processing, express the same instant in UTC before using that input for a catalogue; the exporter does not silently convert it. The exporter writes `documents.parquet`, `SCHEMA.json`, `quality.json` and `preview.jsonl`; a reviewed README dataset card, license notice and checksums are separate packaging steps.

`prepare-public` instead needs a substantiated, exact-hash-bound rights/quality/privacy registry and prepares text only for supported records. Its generated card is a starting point for review, not a source license. `inventory`, `build` and `verify` retain the legacy BOE collection workflow; `verify` expects that workflow's laws/metrics layout rather than every possible export configuration.

## What was verified and what is absent

The completed v0.2 baseline used a normal wheel install on CPython 3.12.14, `datasets` 5.1.0 and PyArrow 26.0.0. Its 129 installed-package tests passed with repository source injection disabled, and installed source modules matched the candidate. Those tests and the synthetic demo were carried into v0.3; they are software evidence, not certification of actual legal content or every platform. The historical PDF run used Poppler 25.08.0.

Exact historical reproduction requires the private August 2025 JSON/PDF pairs. The original scraper, recovery/staging investigation scripts, raw captures, current HTML/Viewer/image probes, comparator downloads and matching scripts, private decision registry and detailed QA receipts are not shipped. An outside developer can inspect the implementation, run invented examples and process their own compatible captures; they cannot reconstruct the historical acquisition and comparison investigation from this repository alone. A fresh download can represent a different legal version.

Stable text, hashes and offsets are narrower reproducibility claims than byte-identical timing/checkpoint journals. The catalogue's source-file, raw-text, processed-text and PDF hashes distinguish those layers; a hash does not certify correct capture, current law, source permission or completeness. The private audit's Parquet configurations are `laws` and `article_spans`; the public catalogue's configuration is `documents`, split `catalogue`.

The fixture citation uses a synthetic BOE-shaped identifier. No test or demo fetches it. `examples/catalogue.py` searches factual metadata and can open a recorded live source URL; it is distinct from the invented extraction demonstration and from a verified legal retrieval system.
