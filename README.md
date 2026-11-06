# Saudi legal snapshot tools

Search Arabic legal wording, read the matching passage in its source context and follow the official citation. The downloadable dataset contains **14,621 parent-level legal-text records from 14,620 source-publication parents**: 468 BOE snapshots, 76 MOJ instruments and 14,077 court contexts from 14,076 court publication parents. The article tables contain **13,863 spans**, separately from their parent documents. Ninety-six official annex image pages preserve useful material that would be lost in plain text.

I collected the original material in 2025 for an earlier legal AI project, and I directed this release to make that collection useful to other developers. Codex assisted with extraction, source comparisons, contextual assessment, code and documentation. Independent review here means a separate AI-agent pass; it is not a claim that I manually read every source or that a lawyer certified the data.

[Get the text dataset](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots) · [Coverage and quality](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots/blob/13ce24c48786bfb39582c8a743a540522dc02d1a/QUALITY.md) · [Rights and source conditions](docs/source-rights.md)

## Try the real data

Use CPython 3.12 from this repository:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps .
.venv/bin/python examples/texts.py --config article_spans --query 'لا يجوز' --show-parent --limit 1
.venv/bin/python examples/texts.py --config judgments --query 'المحرر العادي' --court 'التجارية' --city 'الرياض' --limit 2
```

The first command prints the actual matching article wording, its offset in the complete parent, parent metadata and the official article citation. The second searches court text after filtering the source's court and city fields. Add `--open-source` to open the first official citation. `--captured-from` and `--captured-before` filter capture dates, not legal commencement dates; unknown dates do not match. Search folds Arabic diacritics, tatweel and alef variants while preserving the displayed original wording.

[Executed examples](docs/text-examples.md) include actual outputs and source links. Loading needs no login, private corpus, model service, training or Poppler. The example is a small lexical search demonstration, without a retrieval-accuracy claim.

```python
from datasets import load_dataset
cases = load_dataset("Faisal73/saudi-legal-text-snapshots",
                     name="judgments", split="corpus", token=False)
print(len(cases), cases[0]["source_url"])
```

These counts describe public Hugging Face commit `13ce24c48786bfb39582c8a743a540522dc02d1a`. Its data files are byte-identical to `877d3d17e37d54396b9553988723bbe150cc37d3`, anonymously verified on 5 November 2026 UTC; the successor changes only dataset-card, inventory and checksum metadata. Use `--revision 13ce24c48786bfb39582c8a743a540522dc02d1a` with the example, or the same value for `revision=` with `load_dataset`, to reproduce that snapshot. The [executed examples](docs/text-examples.md) add the three observed outputs from unchanged public example functions during six complete anonymous streams of `877d3d17e37d54396b9553988723bbe150cc37d3`. This was a function-level check with the recorded options and default 150-character context, not a separate direct CLI rerun. Earlier pinned CLI and checkpoint outputs remain below that section. Local candidates and unfinished reviews are excluded from these public totals.

At `877d3d17e37d54396b9553988723bbe150cc37d3`, fresh anonymous downloads of all 292 exported files and all six complete streaming configurations passed. All 30,089 text hashes, 14,621 review projections, parent/span bindings and 96 annex asset bindings passed. All 175 committed Parquets were downloaded and checked directly. One bounded viewer round at that revision returned HTTP 200 for the split and Parquet indexes with all six configurations pending and zero failed; no rows were ready. All six first-row endpoints returned HTTP 500 `ResponseNotReady`. No viewer samples were verified and no polling followed; direct downloads and complete loading passed.

## What's included

| Configuration · split `corpus` | Rows | What a row means |
| --- | ---: | --- |
| `boe_documents` | 468 | A selected BOE publication snapshot |
| `boe_article_spans` | 9,358 | An exact source-evidenced slice of a BOE parent |
| `laws` | 76 | A MOJ legislative or other official instrument publication |
| `article_spans` | 4,505 | An explicit article unit in the MOJ hierarchy |
| `source_sections` | 1,605 | Another useful MOJ source unit |
| `judgments` | 14,077 | A reviewed court context; two rows share one captured source-publication parent |

The court rows contain 16,507 populated source body components. BOE spans are verified in 352 parents; 116 parents have no verified article table. Those unknown boundaries do not produce empty article rows. The current dataset documents twelve selections of complete judicial contexts: six historical appeals and six API or derived contexts. The separate historical trial contexts remain private after five specific privacy holds and one quality hold.

**Historical selection note (RC43):** Eight documented court selections retain complete judicial contexts. Five earlier API selections omit unrelated, repeated or inconsistent surrounding fields. One historical PDF publication retains its complete appeal correction decision while its separate complete trial context stays private for a specific privacy issue. A second historical PDF retains its complete reconsideration appeal while its separate trial stays private for a specific source-context quality issue. An eighth selection recovers a complete gold-workshop judgment from an existing mixed capture; its separate cinema judgment was already included. The mixed wrapper remains a quality hold. See the exact ranges in the dataset's `source-context-selections-v0.5.0.jsonl`. Trial-only selections do not assert an appeal outcome. The 96 annex pages belong to six BOE parents and are listed in the dataset's `boe-annex-pages.jsonl`; they are separate historical source assets, not OCR text or additional laws.

The latest public data update adds nine historical court-publication contexts since RC48: seven complete editions and two complete selected appeals, with 90,331 body characters and thirteen components. Since v0.4.0, the public data adds 13,158 court-publication parents, one further complete context within an already counted parent, eleven BOE publications and 208 BOE spans. Current counts are generated from the actual Parquet artifacts in [coverage.json](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots/blob/13ce24c48786bfb39582c8a743a540522dc02d1a/coverage.json). The separate [468-row metadata catalogue](https://huggingface.co/datasets/Faisal73/saudi-legal-source-catalogue-2025) remains available.

**Historical RC43 addition:** This checkpoint adds three separately reviewed complete historical court editions, with 32,349 body characters and five populated components, since the previous published checkpoint. Compared with v0.4.0, the published snapshot adds 13,127 court publication parents, one further complete context within an already counted parent, 11 BOE publications and 208 BOE spans. Counts are generated from the actual Parquet artifacts in [coverage.json](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots/blob/fac6f65a57b69392d844454d3fe6dd968f6433d7/coverage.json). The separate [468-row metadata catalogue](https://huggingface.co/datasets/Faisal73/saudi-legal-source-catalogue-2025) remains available.

These are captured versions, with overlap between sources and proceedings. File copies, article chunks and annex pages are not extra documents. Distinct publication identifiers do not establish a count of unique laws or cases. The data is useful for text access, source inspection and experiments that account for its limits; it is not a current consolidated statement of Saudi law.

Publisher wording, masks, dates, numbers, negations and source inconsistencies are preserved. Some source publications themselves contain contradictory amounts, clipped phrases or inconsistent metadata; those limitations are flagged rather than silently repaired. Historical versions and later annex evidence have explicit scope notices. Publisher masks do not guarantee anonymity. Specific unresolved records stay private.

The fixed recovery queue contains **720 source-version work items: 283 with final dispositions and 437 pending**. The completed dispositions comprise 241 supported public versions, 20 holds and 22 alternate versions. Five active proposals remain private pending further source-fidelity review; five more items are reserved for repair/publication work that has not started, and 427 are unassigned. These queue items are separate from the published record counts. Unreviewed items remain pending, and processing of the original collection remains incomplete.

## Use your own captures

The CLI processes files you supply. `capture-moj-case` and `capture-moj-legislation` accept saved supported official API responses; `capture-text` accepts a supplied BOE page or isolated body. `audit-capture` and `refine-capture` preserve source evidence and apply explicit source-backed decisions. `prepare-text-release` exports only exact projections with supported rights, quality and privacy review bindings. It validates the supplied decisions; it cannot establish that their claims are true.

See [commands and input requirements](docs/reproducibility.md). PDF extraction needs separately installed Poppler. Historical acquisition scripts, the private 2025 captures, raw responses/PDFs and contextual review notes are not distributed. A new official download can be a different version, so the full historical collection cannot be reconstructed from this toolkit alone.

```bash
.venv/bin/python scripts/verify_text_release.py --dataset Faisal73/saudi-legal-text-snapshots
.venv/bin/python -m pytest -q -p no:cacheprovider -o pythonpath=
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 .venv/bin/python scripts/fixture_demo.py --output demo-work
```

The verifier checks every public text/projection hash, exact article/component slice, native hierarchy and annex asset binding. It does not fetch original source bytes or certify legal correctness. The offline fixture uses clearly invented Arabic and a synthetic identifier that is never fetched; it demonstrates extraction separately from the real-data example.

MIT covers new code, original documentation and invented fixtures. Official text and the narrowly selected normative annex facsimiles use the [separate statutory/policy basis](docs/source-rights.md), not an MIT or CC0 relicensing. Third-party notices remain. [Historical comparisons](docs/comparison.md) and [processing evidence for earlier checkpoints](docs/court-audit.md) explain the contribution without assuming it is novel or more accurate than other datasets.
