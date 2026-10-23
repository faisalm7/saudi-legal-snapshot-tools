# Source catalogue schema

The public [Saudi legal source catalogue 2025](https://huggingface.co/datasets/Faisal73/saudi-legal-source-catalogue-2025) has 468 rows, one per examined historical BOE capture. Native loading uses configuration `documents` and split `catalogue`. It describes the captured source/version and bounded processing outcomes; no legal bodies, article text, PDF extracts, private paths or judgment facts are included.

```python
from datasets import load_dataset
catalogue = load_dataset(
    "Faisal73/saudi-legal-source-catalogue-2025",
    name="documents", split="catalogue",
)
```

Pin a reviewed repository revision when comparing later downloads. Native Parquet files and explicit README configuration paths follow the [Hugging Face dataset-upload](https://huggingface.co/docs/hub/en/datasets-adding) and [dataset-card](https://huggingface.co/docs/hub/en/datasets-cards) conventions. A card's license label does not override the stated source-rights boundaries.

| Fields | Type and meaning |
| --- | --- |
| `catalogue_id` | String; `sa-boe-capture-<UUID>-<first 16 source-file-hash characters>`, identifying this captured file. |
| `document_id` | String; `sa-boe-<UUID>-ar`, stable across captures of that source. It is distinct from a content version. |
| `version_id` | String; the private processing record's content-version identifier, retained for traceability. It does not establish that the legal instrument is current. |
| `source_id`, `source_url` | Strings; observed BOE UUID and recorded canonical Arabic source URL. A current page may differ from the historical capture. |
| `title` | String; recorded source title, normalized to NFC. A title match alone does not establish version identity. |
| `language`, `document_type`, `source_family` | Strings; `ar`, `official_legal_instrument` and `boe` for this release. |
| `capture_timestamp_utc` | String; historical capture timestamp with a UTC/zero offset (`Z` or `+00:00`), distinct from enactment, publication and catalogue release dates. Other aware offsets accepted by the text adapter must be expressed as the same UTC instant before catalogue export. |
| `issued_hijri_raw`, `issued_gregorian_raw`, `published_hijri_raw`, `published_gregorian_raw` | Nullable strings; source date text parsed without calendar conversion or inferred missing dates. |
| `source_reported_status_at_capture` | Nullable string; the portal's historical status label, not an independently verified statement of present law. |
| `source_file_sha256` | String; SHA-256 of the exact historical JSON file. |
| `source_text_sha256` | String; SHA-256 of the captured `full_text` before body selection and cleanup. |
| `text_sha256` | String; SHA-256 of processed body text after the documented transformations. The body itself is withheld. |
| `source_pdf_sha256`, `source_pdf_pages` | Nullable string / nullable 32-bit integer; paired captured PDF hash and recorded extracted-page count. These do not prove that every page was visually inspected. |
| `captured_text_characters` | 32-bit integer; Python Unicode-character length of the processed body, not a token or byte count. |
| `structure_status` | String; historical heading-alignment outcome, including explicit deferral. |
| `verified_article_span_count` | Nullable 32-bit integer; exact captured-text spans emitted and checked by the software. Null means deferred/unknown, not zero legal articles. No spans are distributed in the catalogue. |
| `quality_flags` | List of strings; analytic processing codes, not a quality certificate or instructions to repair text. |
| `content_review_flags` | List of strings; controlled audit codes for possible attachment, illustration, promised-list, annex or split-word issues. These may overlap; a flag alone does not prove a legal defect. |
| `analysis_pipeline_version`, `catalogue_version` | Strings; private processing version and metadata-export version respectively. Historical processing is not relabeled as a fresh source capture. |
| `quality_assessment_scope` | String; `automated_processing_and_limited_diagnostic_sample_not_complete_fidelity_review`. |

The catalogue command uses an explicit field allowlist; it does not copy arbitrary private-record or audit fields. Its facts and original analytic contributions have a separate CC0 scope. That scope does not license source bodies or imply that linked websites permit unrestricted reuse. See [rights](source-rights.md), [quality](quality.md) and [reproduction limits](reproducibility.md).

All exported Arrow fields are nullable in the physical schema; required provenance and aligned-count invariants are checked before export. The machine-readable `SCHEMA.json` in the dataset records exact types. The release contains `aligned` outcomes and explicit `deferred_*` outcomes; do not combine those diagnostic states with rights eligibility or treat all flag sets as disjoint count buckets.

The private run's 350 aligned documents and 9,305 exact spans are processing results. The 118 structural deferrals and known capture omissions prevent treating this catalogue as a completeness or extraction-accuracy benchmark. The catalogue is not a list of every Saudi law, a distinct-instrument census across all versions, or evidence of novel substantive coverage.
