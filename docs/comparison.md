# Contribution and comparison

Primary evidence checked 23 October 2026. The comparison covers all 468 recovered legacy BOE JSON captures. Its body-matching diagnostic precedes the new PDF-evidenced article mapping and does not establish publication eligibility.

| Pinned resource | Relevant distinction |
| --- | --- |
| [BOE corpus, `17dfb792d8eb4c21f6d61f9a088496e7119701db`](https://huggingface.co/datasets/endomorphosis/ipfs_saudiarabia_laws/tree/17dfb792d8eb4c21f6d61f9a088496e7119701db) | 827 instrument/language rows and 21,536 extractive article rows; existing content hashes and archive captures already provide provenance |
| [ALARB, `e64bfdc867146294a65434c5ca16c2c4c5288ca2`](https://huggingface.co/datasets/THIQAH-RD/ALARB/tree/e64bfdc867146294a65434c5ca16c2c4c5288ca2) | Published 13,341 case-derived benchmark rows; [paper v1](https://arxiv.org/html/2510.00694v1#S3.SS1) describes LLM restructuring/anonymization of facts/reasoning and citation linking, rather than a verbatim judgment archive |
| [ArabLegalEval, `7e9530039324a45cf7b585b618663e3359ed589c`](https://github.com/Thiqah/ArabLegalEval/tree/7e9530039324a45cf7b585b618663e3359ed589c) | Official-text/FAQ inputs are distinct from generated MCQs and translated benchmark tasks; task rows are not original-law/case counts |

Exact BOE UUID plus Arabic `/1` links **413 local records to 414 public peers**. Tracking queries and route case are normalized only for lookup; original URLs stay intact. Fifty-five keys are absent from that pinned Arabic key catalogue; three have normalized-title peers under another ID or source. These are source-key gaps and version candidates, not a proven novel-coverage count.

Source IDs and titles do not establish identical legal versions. A unique entire-body match under NFC, whitespace/tatweel and the literal UI-control handling, followed by ordered number/negation checks, yields **238 comparable pairs across 237 local documents**. The other 176 peer pairs remain content/version-unresolved. One compacted match fails because a local word is split internally by whitespace; it is not silently repaired. Public `retrieved_at` is not the original archive-capture date.

The comparison demonstrates cleaner whole-body retrieval input: portal view-count/description and report-form material can be excluded while retaining the comparable body characters. It also shows a loss: all 237 comparable legacy bodies are flattened, while the public peers retain line structure. The new mapper adds exact PDF-evidenced heading spans where unique alignment is possible; it does not restore lost paragraphs or prove complete law content.

The public article table is extractively consistent: every article text is an NFC/whitespace substring of its parent, with no orphan rows. Boundaries still have specific defects. In the 238 comparable pairs, 4,106 of 5,109 public article rows fall inside the matched body, 882 outside it, and 121 cross its boundary. Targeted inspection finds report-form selector fragments and missing separate boundaries after article eleven; other examples have useful correct mappings. These are interval results and targeted examples, not a global segmentation-error percentage.

ALARB's article-text linking must not be described as wholly model-generated: the paper distinguishes scraped statute text from model-assisted citation selection. Its public schema lacks original case IDs/URLs/capture times, limiting direct original-case matching. Neither this limitation nor synthetic ArabLegalEval tasks establishes novelty for our local judgments.

The defensible contribution is reusable conservative processing and review tooling, plus an original factual catalogue exposing source/version identifiers, capture hashes and bounded processing outcomes for the examined snapshots. These metadata rows do not add public legal bodies or prove new substantive coverage. No first/largest, unique-provenance, overall-superior extraction, complete/current law or expert-benchmark claim is made. Actual source-text eligibility remains unresolved, so the legal bodies and article text stay private.
