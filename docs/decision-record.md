# Architecture and release decisions · v0.4.0

The public package separates source capture/adapters, faithful text plus independent search normalization, optional evidence-backed structure, contextual review and a hash-bound publication projection. Saved BOE captures or saved official MOJ responses enter locally. MOJ instruments preserve their native hierarchy; courts preserve every populated judgment/appeal body field; BOE headings map only through unique ordered PDF evidence. A final allowlist/gate binds body, metadata and structure to reviewed decisions before writing a new Parquet destination. It does not fetch, interpret, redact or publish on the user's behalf.

| Choice | Benefit | Limit/tradeoff |
| --- | --- | --- |
| Preserve the declared source representation; normalize search separately | Numbers, negations, source masks and text hashes remain inspectable | Source typography, upstream capture omissions and source inconsistencies can remain; faithful DOM is not necessarily complete law |
| Use native MOJ units or unique PDF-evidenced BOE offsets; defer ambiguity | Reconstructable hierarchy and exact source slices |111 selected BOE bodies have no verified article table; article tables overlap parent bodies and must not be counted as more documents |
| Require separate rights, fidelity, privacy and projection bindings | Narrow, reviewable inclusion and explicit source-version differences | The registry validates evidence fields, not their truth; current refetches and hidden private acquisition steps cannot reproduce every historical version |

The release adds selected actual source text and reviewed structure to the earlier tools/catalogue work. The original 468-row factual catalogue remains separate and retains its own narrow CC0 scope. Legal-text source bases and custom conditions do not become MIT merely because the exporter is MIT.

Development, tests and source/context reviews were AI assisted, including a separate agent's court review and independent final artifact review. This is not a claim of human/legal-expert certification, government affiliation, model retrieval performance or source-document authorship. Original source files and earlier frozen releases were preserved. [Reproduction limits](reproducibility.md) and [comparison evidence](comparison.md) constrain the contribution claim.
