> The comparison below is the preserved v0.4.0 evidence. Current coverage and additions are generated separately in [coverage.json](coverage.json); no new benchmark or blanket superiority claim is inferred from expansion.

# Contribution and comparison

Primary comparison evidence checked 23 October2026 against all 468 recovered legacy BOE JSON captures, before the final 454-body selection and the education-image completion. The comparison is a capture/body diagnostic, not a novelty or final-release accuracy score.

| Pinned resource | Relevant distinction |
| --- | --- |
| [BOE corpus ·17dfb792d8eb4c21f6d61f9a088496e7119701db](https://huggingface.co/datasets/endomorphosis/ipfs_saudiarabia_laws/tree/17dfb792d8eb4c21f6d61f9a088496e7119701db) |827 instrument/language rows and 21,536 extractive article rows; content hashes and archive capture provenance already exist |
| [ALARB ·e64bfdc867146294a65434c5ca16c2c4c5288ca2](https://huggingface.co/datasets/THIQAH-RD/ALARB/tree/e64bfdc867146294a65434c5ca16c2c4c5288ca2) |13,341 case-derived benchmark rows; [paper v1](https://arxiv.org/html/2510.00694v1#S3.SS1) distinguishes model restructuring/anonymization/citation linking from scraped statute text |
| [ArabLegalEval ·7e9530039324a45cf7b585b618663e3359ed589c](https://github.com/Thiqah/ArabLegalEval/tree/7e9530039324a45cf7b585b618663e3359ed589c) |Official-text/FAQ inputs differ from generated MCQs and translated tasks; benchmark rows are not original-law/case counts |

Exact BOE UUID plus Arabic `/1` links 413 local records to 414 public peers. Fifty-five source keys are absent from that pinned Arabic catalogue; three have normalized-title peers under other IDs/sources. These are **source-key gaps, not 55 proven novel laws**. IDs/titles do not prove same legal version.

Unique entire-body matching under NFC, whitespace/tatweel and literal UI-control handling, with ordered number/negation checks, yields 238 comparable pairs across 237 local documents. The other 176 peer pairs remain content/version-unresolved. One compacted match fails on an internally split local word; no silent repair is assumed. Public `retrieved_at` is not the archive capture date.

The local cleanup excludes portal view-count/description and report-form material while retaining matched body characters. It also loses structure: all 237 comparable legacy bodies are flattened while peers preserve lines. PDF-evidenced exact heading spans add explicit boundaries where alignment is unique; they do not restore missing paragraphs, list numbers or integral attachments.

The public comparator's article text is extractively consistent with its parents, but boundaries can contain report-selector fragments or miss separate boundaries after article 11. Within the 238 comparable pairs, 4,106 of 5,109 article rows fall inside the matched body, 882 outside and 121 cross it. These are interval diagnostics with targeted examples, not a global segmentation-error percentage or proof our boundaries are uniformly superior.

ALARB is not described as all paraphrase or wholly generated law: its paper separates scraped statute text from model-assisted case restructuring/citation selection. Missing original case IDs/URLs/capture times in its public schema limits direct same-case matching; it does not prove our court records novel. Neither benchmark's task design establishes new substantive coverage here.

The defensible contribution is selected source-version-labelled text, exact native/evidence-backed structure, explicit corrections/deferrals and reusable local adapters/review gates. Existing coverage and capture losses remain acknowledged. No first/largest, unique provenance, overall-superior extraction, complete/current law or expert-benchmark claim is made.
