# Court processing and publication · v0.5.0

The current candidate contains **8,764 court publication records and 9,006 populated source body components**, an addition of 7,846 publication records since v0.4.0. [Coverage](coverage.json) is computed from the actual Parquet files; the [review summary](review-summary-v0.5.0.json) separates completed contexts, specific holds and duplicate publications. Remaining frozen queues are still in progress, not rejected.

## Preserved v0.4.0 inventory and review evidence

The following section reports the previous release and its frozen checkpoint. Its counts are historical; the original file inventory is unchanged.

Publish 918 source publication body records/920 populated source components, after retaining 479 initial records, excluding one independently confirmed initial alias, and adding 439 individually approved current API records. Six duplicate bodies in total are excluded with source relations. All selected source IDs are distinct, but a component can contain multiple judicial decisions and source republications can share a dispute; semantic unique-case coverage is not asserted.

## Complete original inventory

All 38,011 original court-family files were byte-hashed and processed as native text/JSON: 4,962,953,045 bytes, 37,832 distinct file hashes, zero unavailable files, zero size/mtime changes. The case family has 32,896 PDFs (32,717 byte-distinct; 77,385 pages). Its 21,114 exact raw native groups include one shared portal-shell group, leaving 21,113 substantive raw groups. File dispositions do not overlap: 15,562 primary substantive groups with strict publisher identity; 5,551 without unique current identity; 11,603 secondary exact raw-text copies; 179 secondary exact file copies; one primary low/empty group. The 365 portal-shell files collapse into that low group. These units are not semantic judgments.

All 4,926 derived case JSON files point to distinct existing PDF paths and add no separate document coverage (4,017 raw-text groups/909 copies). The 86 Qadha PDFs plus 86 derived JSONs contain third-party authored journals/studies/books; official-text versus commentary boundaries/reuse remain unresolved. The 17 grievance volumes have 8,866 pages and no usable native Arabic. A bounded six-page OCR/date-anchor benchmark failed, so no blind OCR scale-up or blanket legal-rights rejection follows.

## Source tracing and resumable processing

Strict mapping recovered 15,649 publisher locators from 23,203 case-PDF paths: 15,143 commercial, 20 general, 486 Supreme. Non-Supreme extraction resolved 15,344 locator+native versions across 15,163 locators/22,523 PDFpaths: 15,090 complete outer bodies/18,301 populated components, 254 unresolved outer boundaries, zero missing native caches. An early private extractor selected internal operative headings; it was corrected before public export. No truncated pilot body was published.

The short complete-body refresh queue has 7,125 locators. Acquisition stopped at a frozen checkpoint containing 1,624 main plus 6 separately repaired current API bodies: 1,630 unique publisher UUIDs/1,636 body fields. Existing source-version matches are reused exactly; these are not all new coverage. The durable private checkpoint/raw captures and review inputs can resume remaining work without changing originals. `docs/automated-quality.json` embeds the nonoverlapping refresh/review counts and definitions.

## Actual selection and fidelity

The initial 514 source-version contexts/513 locators and later 486 distinct current source/body contexts are overlapping cohorts; they are not summed into an inflated unique-document claim. Every published context received independent full-context source/privacy review. The focused original-hold consistency check corrects overbroad private-home/inheritance/finance assumptions where exact text actually describes business succession, professional fees, procedural roles or masked business dealings. It does not turn privacy flags into automatic approvals. 71 reviewed current source versions remain private for specific personal financial, family, home, criminal or identifying or unresolved-role issues; source clipping/actual corruption and unreviewed contexts remain separate quality/pending queues. No reviewer-created redactions or replacement legal wording were used.

All populated API judgment/appeal fields and their exact hashes/offsets are retained. Inactive-level source metadata and placeholder titles stay null with flags; display dates from an absent component are not promoted. Current API and PDF wording can differ in masking, metadata, signatures, clipped lines or glyph/numeric order. PDF-only private details are never appended. An unavailable PDF remains null/flagged. The full selected body/projection/structure registry was checked; diagnostic comparisons and selected whole facsimiles support review without claiming all-page glyph inspection.

All 29 initial historical sources/30 pages were read/visually checked and transcription ledgers replayed. Twenty original PDF byte hashes were independently rechecked; nine bounded cloud-unavailable rechecks explicitly use primary builder hash/native/render receipts plus independent complete-page inspection. Historical capture time remains null. The one new current PDF body has separate full-page/source proof. Four later historical-native pilot versions passed review but add zero coverage because current API canonicals are already selected; body-free relations preserve version evidence.

Official judges and clearly professional/business-role names can remain after contextual assessment. Source masks are preserved but do not certify anonymity. No original PDFs, private identifying contexts, raw judicial API HTML, rejected/duplicate bodies or private recovery logs are public. The [MOJ source-wide grant](source-rights.md) is separate from these quality/privacy decisions. These reviews were AI assisted, not human/legal-expert certification. Full native processing is complete; full contextual clearance of the collection is not.
