# Selected text and quality limits · v0.4.0

The six public configurations contain 1,010 source publication records and their separately counted source units. `metrics.json`, `schema.json`, `record-reviews.jsonl` and the dataset's correction/relationship receipts describe the exact export. Counts establish structure and selection, not a single accuracy percentage.

## BOE

All 468 recovered inputs were refined and hash/span checked. Select 454 bodies: 343 with 9,091 exact source-evidenced article spans and 111 with unverified structure and **no guessed article rows**. Fourteen material body/annex/formula/model/schedule gaps are withheld. Exact offsets mean Python Unicode-character slices into `text_ar`; a correct slice does not prove upstream capture completeness. Search normalization is stored separately.

The captured bodies can be flattened, omit rendered list markers or linearize tables without certified cell relations. At least 12 documents in the purposive diagnostic sample lost rendered numbering; flags preserve this limitation. The earlier diagnostic covered 50 new documents through 150 paired text windows and 15 PDF page images across new/old cases, with additional targeted source checks. It is not full glyph inspection or a population accuracy estimate. All-body screening plus 76 bounded contexts across 50 flagged BOE records found no concrete privacy deferral; it is not 468 complete manual reads or universal absence of personal data.

One education-authority original-base 1434 Article 6 has a **715-character official-image-backed completion**, not the 1437 amended membership. Existing heading/PDF evidence was retained with rebased exact offsets; no new PDF segmentation was invented. Its new body hash is `2c79d44da0773105ed05ce9be0923a2d79b83c586267ee3fb84eedfe4e06f94a`. The [official image](https://laws.boe.gov.sa/BoeLaws/Laws/GetViewerImage/?imageFileName=a16d6d7d-15c3-41e9-b3af-1dbdbc6d47e8_Page_004.jpg), separately captured evidence and version witnesses are recorded in the dataset's `REPAIRS.json`. The original 2025 timestamp alone must not imply that completion was present then.

## MOJ instruments

The 76 records preserve 7,014 native source units: 4,505 explicit articles, 1,605 useful other units, 873 empty structural nodes and 31 punctuation-only structural nodes. The last two groups remain in the parent native hierarchy but are omitted from article/section tables. The exporter reconstructs labels, order, hierarchy, HTML-derived text, offsets and source IDs; it does not split enactment wording into manufactured articles. Source status, cancellation/parent cancellation and raw dates remain source fields, not an assertion of present operative law. Tables/line order and current-versus-historical PDF differences require source-specific caution.

The source entry for [نظام التنفيذ ١٤٤٧هـ](https://laws.moj.gov.sa/ar/legislation/Cl5QbqZSJlZ1EfYkT6d83A) reports `ValidFrom` 2026-10-28, after the 2026-10-23 capture. Its [implementing-regulation publication](https://laws.moj.gov.sa/ar/legislation/x_FJkA-Ltfan7NZMbMf60Q) is also included; availability on the portal does not establish commencement. Neither is silently labelled operative at capture.

## Courts and verification

The 480 court records retain 481 complete body components. Every proposed context was independently read; 30 current contexts remain private and three duplicate aliases have metadata relations only. Current API bodies, historical PDF transcriptions and the one newly retrieved current PDF are explicitly distinguished. [Court review](court-audit.md) explains masks, professional/public-role names, cross-format differences and historical byte-recheck limits.

`verify_text_release.py` checks the published text/projection hashes, exact article/component slices, source-unit membership and evidence bindings using public files. It does not fetch original official bytes or certify substantive legal correctness, completeness or anonymity. Invented tests cover transforms, Arabic/numbers/negations, directory safety and review gates; passing them does not cure a missing annex or legal provision.
