# v0.3 scope and architecture

The release separates reusable tools, an original factual source catalogue and actual source text. The catalogue describes 468 August 2025 BOE captures through an explicit metadata projection; it contains no legal bodies, article text, PDF extracts or case facts. No examined legal-text subset has passed the current combined publication review. This temporary text hold does not assert that official texts are categorically copyrighted or prohibited.

The local flow is: independently acquired page text → hash-bound capture JSON → validated body and optional PDF heading evidence → exact captured-text article spans → private records/Parquet. Existing compatible capture JSON can enter directly. A separate `catalogue` projection emits allowed metadata. A substantiated hash-specific rights/quality/privacy registry is required before `prepare-public` can select actual text for a different candidate.

The historical private run processed all 468 BOE JSON/PDF pairs. It produced 468 document records, 350 uniquely aligned heading sequences and 9,305 spans; structure remains deferred for 118. Catalogue diagnostics describe those processing outcomes without supplying the private evidence needed to rerun them. Source summaries, source bodies, case facts and unknown-origin third-party materials are outside the public release.

## Three tradeoffs

| Choice | Practical benefit | Material limit |
| --- | --- | --- |
| Preserve captured body; store search normalization separately | Legal characters, numbers and negations remain auditable against their captured source | Broken spacing, missing list numbering and omitted capture content can remain; source preservation does not certify a complete law |
| Require isolated PDF headings and a unique ordered DOM mapping | Article rows have exact source offsets and source-evidence hashes | Ambiguous, absent or empty mappings yield no table; PDF evidence does not by itself verify every article's substance or attachments |
| Publish a whitelisted source catalogue separately from private bodies and supported text selection | Source discovery and reproducible metadata export can be useful while text eligibility is unresolved | Catalogue facts and diagnostics cannot reconstruct the historical body, establish its completeness or grant permission to reuse it |

Implementation and review were AI assisted. The tools make no claim to source-document authorship, government affiliation, legal interpretation or expert-validated retrieval performance. Exact historical reproduction requires the private capture inputs and compatible extraction dependencies; invented fixtures reproduce software behavior independently. Current website content is not assumed equivalent to the 2025 captures.
