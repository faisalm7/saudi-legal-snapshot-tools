# Saudi legal snapshot tools · v0.5.0

Search Arabic legal wording, read the matching passage in its source context and follow the official citation. This release provides **9,308 source publication snapshots**: 468 from the Bureau of Experts, 76 MOJ instrument publications and 8,764 court publications. The article tables contain **13,863 spans**, separately from their parent documents. Ninety-six official annex image pages preserve useful material that would be lost in plain text.

I collected the original material in 2025 for an earlier legal AI project, and I directed this release to make that collection useful to other developers. Codex assisted with extraction, source comparisons, contextual assessment, code and documentation. Independent review here means a separate AI-agent pass; it is not a claim that I manually read every source or that a lawyer certified the data.

[Get the text dataset](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots) · [Coverage and quality](docs/quality.md) · [Rights and source conditions](docs/source-rights.md)

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

Use `--revision COMMIT_SHA` with the example or `revision="COMMIT_SHA"` with `load_dataset` to pin a release. Exact published commits are recorded in the release notes.

## What's included

| Configuration · split `corpus` | Rows | What a row means |
| --- | ---: | --- |
| `boe_documents` | 468 | A selected BOE publication snapshot |
| `boe_article_spans` | 9,358 | An exact source-evidenced slice of a BOE parent |
| `laws` | 76 | A MOJ legislative or other official instrument publication |
| `article_spans` | 4,505 | An explicit article unit in the MOJ hierarchy |
| `source_sections` | 1,605 | Another useful MOJ source unit |
| `judgments` | 8,764 | A reviewed court publication, sometimes containing more than one decision field |

The court rows contain 9,006 populated source body components. BOE spans are verified in 352 parents; 116 parents have no verified article table. Those unknown boundaries do not produce empty article rows. The 96 annex pages belong to six BOE parents and are listed in the dataset's `boe-annex-pages.jsonl`; they are separate historical source assets, not OCR text or additional laws.

Compared with v0.4.0, this candidate adds 7,846 court publications, 11 BOE publications and 208 BOE spans. Counts are generated from the actual Parquet artifacts in [coverage.json](docs/coverage.json). The separate [468-row metadata catalogue](https://huggingface.co/datasets/Faisal73/saudi-legal-source-catalogue-2025) remains available.

These are captured versions, with overlap between sources and proceedings. File copies, article chunks and annex pages are not extra documents. Distinct publication identifiers do not establish a count of unique laws or cases. The data is useful for text access, source inspection and experiments that account for its limits; it is not a current consolidated statement of Saudi law.

Publisher wording, masks, dates, numbers, negations and source inconsistencies are preserved. Some source publications themselves contain contradictory amounts, clipped phrases or inconsistent metadata; those limitations are flagged rather than silently repaired. Historical versions and later annex evidence have explicit scope notices. Publisher masks do not guarantee anonymity. Specific unresolved records stay private.

## Use your own captures

The CLI processes files you supply. `capture-moj-case` and `capture-moj-legislation` accept saved supported official API responses; `capture-text` accepts a supplied BOE page or isolated body. `audit-capture` and `refine-capture` preserve source evidence and apply explicit source-backed decisions. `prepare-text-release` exports only exact projections with supported rights, quality and privacy review bindings. It validates the supplied decisions; it cannot establish that their claims are true.

See [commands and input requirements](docs/reproducibility.md). PDF extraction needs separately installed Poppler. Historical acquisition scripts, the private 2025 captures, raw responses/PDFs and contextual review notes are not distributed. A new official download can be a different version, so the full historical collection cannot be reconstructed from this toolkit alone.

```bash
.venv/bin/python scripts/verify_text_release.py --dataset Faisal73/saudi-legal-text-snapshots
.venv/bin/python -m pytest -q -p no:cacheprovider -o pythonpath=
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 .venv/bin/python scripts/fixture_demo.py --output demo-work
```

The verifier checks every public text/projection hash, exact article/component slice, native hierarchy and annex asset binding. It does not fetch original source bytes or certify legal correctness. The offline fixture uses clearly invented Arabic and a synthetic identifier that is never fetched; it demonstrates extraction separately from the real-data example.

MIT covers new code, original documentation and invented fixtures. Official text and the narrowly selected normative annex facsimiles use the [separate statutory/policy basis](docs/source-rights.md), not an MIT or CC0 relicensing. Third-party notices remain. [Historical comparisons](docs/comparison.md) and [processing evidence](docs/court-audit.md) explain the contribution without assuming it is novel or more accurate than other datasets.
