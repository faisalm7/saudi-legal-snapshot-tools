# Saudi legal snapshot tools

Search Arabic legal wording, read the matching passage in its source context and follow the official citation. The downloadable dataset contains **14,590 parent-level legal-text records from 14,589 source-publication parents**: 468 BOE snapshots, 76 MOJ instruments and 14,046 court contexts from 14,045 court publication parents. The article tables contain **13,863 spans**, separately from their parent documents. Ninety-six official annex image pages preserve useful material that would be lost in plain text.

I collected the original material in 2025 for an earlier legal AI project, and I directed this release to make that collection useful to other developers. Codex assisted with extraction, source comparisons, contextual assessment, code and documentation. Independent review here means a separate AI-agent pass; it is not a claim that I manually read every source or that a lawyer certified the data.

[Get the text dataset](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots) · [Coverage and quality](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots/blob/fac6f65a57b69392d844454d3fe6dd968f6433d7/QUALITY.md) · [Rights and source conditions](docs/source-rights.md)

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

These counts describe the public Hugging Face commit `fac6f65a57b69392d844454d3fe6dd968f6433d7`, verified on 3 November 2026 UTC. Use `--revision fac6f65a57b69392d844454d3fe6dd968f6433d7` with the example, or the same value for `revision=` with `load_dataset`, to reproduce that snapshot. The [executed examples](docs/text-examples.md) preserve the earlier `f07cd16c3a39fb6099a352b4e5d9b3c40c5ab2a1` CLI outputs and add checks of the same public example functions on this snapshot during fresh anonymous streaming verification. The current check used the recorded options and defaults; it was not a separate direct CLI rerun. Local candidates and unfinished reviews are excluded from these public totals.

Fresh anonymous downloads of all 285 exported files and all six complete streaming configurations pass. All 30,058 text hashes, 14,590 review projections, parent/span bindings and 96 annex asset bindings passed. All 168 committed Parquets were downloaded and checked directly. One bounded viewer round returned HTTP 500 `ResponseNotReady` for all eight split, Parquet and first-row endpoints. No viewer samples or listing pending/failed counts were available; direct downloads and complete loading passed.

## What's included

| Configuration · split `corpus` | Rows | What a row means |
| --- | ---: | --- |
| `boe_documents` | 468 | A selected BOE publication snapshot |
| `boe_article_spans` | 9,358 | An exact source-evidenced slice of a BOE parent |
| `laws` | 76 | A MOJ legislative or other official instrument publication |
| `article_spans` | 4,505 | An explicit article unit in the MOJ hierarchy |
| `source_sections` | 1,605 | Another useful MOJ source unit |
| `judgments` | 14,046 | A reviewed court context; two rows share one captured source-publication parent |

The court rows contain 16,459 populated source body components. BOE spans are verified in 352 parents; 116 parents have no verified article table. Those unknown boundaries do not produce empty article rows. Eight documented court selections retain complete judicial contexts. Five earlier API selections omit unrelated, repeated or inconsistent surrounding fields. One historical PDF publication retains its complete appeal correction decision while its separate complete trial context stays private for a specific privacy issue. A second historical PDF retains its complete reconsideration appeal while its separate trial stays private for a specific source-context quality issue. An eighth selection recovers a complete gold-workshop judgment from an existing mixed capture; its separate cinema judgment was already included. The mixed wrapper remains a quality hold. See the exact ranges in the dataset's `source-context-selections-v0.5.0.jsonl`. Trial-only selections do not assert an appeal outcome. The 96 annex pages belong to six BOE parents and are listed in the dataset's `boe-annex-pages.jsonl`; they are separate historical source assets, not OCR text or additional laws.

This checkpoint adds three separately reviewed complete historical court editions, with 32,349 body characters and five populated components, since the previous published checkpoint. Compared with v0.4.0, the published snapshot adds 13,127 court publication parents, one further complete context within an already counted parent, 11 BOE publications and 208 BOE spans. Counts are generated from the actual Parquet artifacts in [coverage.json](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots/blob/fac6f65a57b69392d844454d3fe6dd968f6433d7/coverage.json). The separate [468-row metadata catalogue](https://huggingface.co/datasets/Faisal73/saudi-legal-source-catalogue-2025) remains available.

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

MIT covers new code, original documentation and invented fixtures. Official text and the narrowly selected normative annex facsimiles use the [separate statutory/policy basis](docs/source-rights.md), not an MIT or CC0 relicensing. Third-party notices remain. [Historical comparisons](docs/comparison.md) and [processing evidence for earlier checkpoints](docs/court-audit.md) explain the contribution without assuming it is novel or more accurate than other datasets.
