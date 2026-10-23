# Processing evidence and quality limits

The historical private run processed all 468 recovered BOE JSON/PDF pairs. The source catalogue publishes factual metadata and selected analytic status codes for those captures. The code package ships aggregate results and invented tests. Neither supplies actual legal bodies, article text, private audit journals or facsimiles.

| Measured processing result | Count |
| --- | ---: |
| Parsed records / distinct source IDs / distinct exact texts | 468 / 468 / 468 |
| Captured full-text hashes verified | 468 |
| Uniquely aligned PDF-to-DOM heading sequences | 350 |
| Exact DOM article spans emitted | 9,305 |
| Structure deferred: no isolated PDF headings | 59 |
| Structure deferred: ambiguous or mismatched sequence | 57 |
| Structure deferred: empty article body | 2 |
| Examined legal-text records eligible for public release | 0 |

Article positions are Python Unicode-character offsets into the exact `text_ar` string. Each span carries its text hash and PDF hash/page/line evidence. Preamble precedes the first selected heading and is not relabeled an article. Ordinals beyond eleven are supported. A lossy heading key is used only for alignment; it never rewrites the body. Ambiguity causes deferral of the entire table rather than a partial guessed split.

These counts establish processing and source-offset integrity. They do not establish a single extraction-accuracy percentage, full legal article coverage, expert review or complete law capture. The historical DOM bodies are flattened and can omit list numbering, board-composition entries, illustrations, integral annexes or attachment contents. A PDF heading can support a boundary without proving that the following captured paragraph contains every item visible in the PDF. An emitted article row is not a quality acceptance or publication decision. The catalogue's `verified_article_span_count` means software-checked exact spans in this run, not legally validated articles.

The automated content flags include attachment/annex references, illustrations, suspicious promised-list boundaries and a broken negation word. They are triage, not automatic legal defects or automatic repairs. A word broken by a space is preserved pending source-backed correction. Royal/official references and private-party information require different contextual treatment; contact-pattern checks alone cannot justify an anonymization claim.

Tests use invented material to cover Arabic preservation, numbers/dates/negations, separate search normalization, hashes/IDs, deduplication/provenance, deterministic data transformations, checkpoint retries, directory safety, article evidence and the public-selection gate. Passing tests do not remove source-capture omissions. Detailed capture-fidelity and expanded-source inspections remain separate evidence; this package does not represent them as a complete facsimile certificate.

Reproducing historical results requires the exact private inputs and extraction dependencies. Journal timing fields may change between runs; a deterministic text/hash/span result is a narrower claim than byte-identical timing logs. No newly processed body is eligible for publication solely because these checks pass. Catalogue nulls preserve uncertainty: a deferred article count is null, not zero. Raw issue/publication date strings and historical source status are not silently converted into current legal facts.

## Captured-source diagnostic completed for v0.2

A separate AI agent inspected 50 newly recovered BOE documents through 150 paired DOM/PDF-text windows, plus targeted windows for the eight earlier deferrals. Fifteen physical PDF pages from 15 documents received image inspection (seven new sample documents and eight earlier deferrals); most used recorded crops. One additional heading control was checked. Only one new short DOM body was read completely. This is purposive diagnostic sampling, not full glyph-level inspection of 50 documents or a population accuracy estimate.

In the inspected contexts, at least 12 of the 50 new documents omit rendered list markers; three show promised list/formula gaps; one lacks its main instrument after promulgating material; and one has a split negation-related word. These observations can overlap. The two empty-body structural deferrals were traced to wrapped citations. No wrong emitted boundary was established in the inspected boundary contexts of 30 aligned sample documents or the narrow terminal-period/connector diagnostic; that does not validate every emitted boundary.

For all 50 selected documents, source hashes, declared cleanup, ordered DOM numeric runs and selected DOM negation tokens checked successfully. Those DOM-to-output checks do not establish preservation of numbers missing upstream from PDF-to-DOM capture. No whole-corpus extraction-accuracy percentage, anonymity certificate or legal-expert approval follows. Known observations are retained against exact source hashes in a private sidecar; no source text is included here.
