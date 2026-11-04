# Changelog

## 0.5.3

- Support an explicitly declared complete unheaded appellate act within one originally stored native field, using the existing combined judgment-and-appeal type. Require all four absent appeal publication-header values to remain null; no header is inferred from body wording.
- Bind the original field, two contiguous absolute native ranges, the literal two-line separator and complete source coverage. Existing known-header, disjoint-source and selected-appeal checks remain strict. These provenance checks do not establish source fidelity, privacy or publication rights.
- Add 96 entirely synthetic regression cases for this opt-in representation and its rejection paths.

## 0.5.2

- Accept `judicial_historical_appeal_context_selection` for a complete selected appeal without inferring a commercial specialty. Preserve the legacy commercial selection type and the same strict source, native-range, page, observed-route and withheld-context checks.
- Exercise both selection types with the same synthetic provenance and reviewed-export regression cases. Source fidelity and contextual privacy still require separate exact-version review.

## 0.5.1

- Support explicit absolute native-source segments for a combined historical judgment and appeal whose judicial text continues around publisher interface text. Bind selected pieces, full-source coverage, source/component hashes and ranges while preserving the existing contiguous-source checks.
- Add entirely synthetic regression cases for this provenance form. Exact source comparisons and reviewed projection decisions remain necessary to establish content fidelity.

## 0.4.0

- Complete the 38,011-file court native inventory and independently reviewed resumable court batches; preserve all pending/private records. Repair four BOE original-base parents from official images with separate version evidence.

- Add selected Arabic text snapshots: 457 BOE bodies, 76 MOJ instrument publications and 918 court publication records, plus separate exact article/section configurations.
- Add saved-response MOJ adapters, source-backed BOE refinement, an exact reviewed-projection export gate and real public text loading/verification examples.
- Document source-specific affirmative rights, source/version and privacy decisions, correction provenance and capture limitations. Preserve earlier tools/catalogue releases and original inputs.

## 0.3.0

- Add a metadata-only catalogue path for 468 historical BOE captures, separate from withheld legal text.
- Add an adapter for already acquired UTF-8 BOE page-text dumps and a source-catalogue discovery example.
- Document supported inputs, exact historical reproduction limits, catalogue identifiers and license boundaries.
- Retain the conservative PDF-heading alignment, private audit workflow, synthetic fixtures and separate text-publication gate from v0.2.

## 0.2.0

Local processing of 468 historical JSON/PDF capture pairs produced 9,305 exact captured-text spans in 350 documents; structure remained deferred for 118. The tools and invented fixtures were verified independently, including 129 installed-package tests. This processing did not clear actual source text for publication.
