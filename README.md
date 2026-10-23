# Saudi legal snapshot tools · v0.4.0

Load and inspect source-traceable Arabic legal text from the [Saudi legal text snapshots dataset](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots). The release contains **1,451 source publication records**: 457 BOE bodies, 76 MOJ legislative/instrument publications and 918 court publications. Article and section tables are separate. These are selected captured versions, with overlap between sources; the total is not a count of unique laws or cases or a complete/current statement of Saudi law.

| Dataset configuration · split `corpus` | Rows | Meaning |
| --- | ---: | --- |
| `boe_documents` | 457 | Selected historical BOE bodies; four parents have documented source-backed completions |
| `boe_article_spans` | 9,150 | Exact source-evidenced slices in 346 BOE bodies; 111 bodies have no verified article table |
| `laws` | 76 | Current MOJ legislative/instrument publication records; not all are statutes |
| `article_spans` | 4,505 | Explicit MOJ source article units |
| `source_sections` | 1,605 | Useful other MOJ source units, including enactment/structural content |
| `judgments` | 918 | Reviewed court publication records containing 920 populated source body components |

## Load and inspect real text

From this repository, use CPython 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps .
.venv/bin/python examples/texts.py --config boe_documents --query 'لا يجوز' --limit 2
.venv/bin/python scripts/verify_text_release.py --dataset Faisal73/saudi-legal-text-snapshots
```

The example loads real published text without authentication, searches it lexically and prints genuine official citations. Add `--open-source` to open a matching source. The verifier checks published text/projection hashes, native structure, membership and exact offsets. Neither evaluates legal correctness or retrieval accuracy, nor retrieves the original official source bytes. Add `--revision COMMIT_SHA` to either command to pin a dataset commit. Loading this release needs no private inputs, Poppler or model service.

You can also load the Parquet-backed dataset directly:

```python
from datasets import load_dataset
rows = load_dataset("Faisal73/saudi-legal-text-snapshots",
                    name="judgments", split="corpus", token=False)
print(len(rows), rows[0]["source_url"])
```

## Process your own compatible captures

The CLI operates on files you already acquired; it does not scrape or publish:

- `capture-text`: wrap a supplied UTF-8 BOE page/body with a source URL and aware capture timestamp.
- `audit-capture`, then `refine-capture`: preserve captured bodies, align isolated PDF headings to exact offsets, and apply only documented source-backed refinement decisions. Poppler `pdftotext` is required for PDF extraction.
- `capture-moj-case` / `capture-moj-legislation`: validate saved official API responses, preserve complete populated body fields or the native legislative hierarchy, and record source hashes.
- `prepare-text-release`: export only projections supported by exact rights, privacy, quality and metadata/structure review bindings. The gate validates supplied evidence fields; it cannot establish that their claims are true.

[Reproduction commands and limits](docs/reproducibility.md) describe the inputs. Historical acquisition/recovery scripts, raw API responses/PDFs, private contexts and original 2025 captures are not shipped. A current download can be a different source version. The earlier [468-row factual catalogue](https://huggingface.co/datasets/Faisal73/saudi-legal-source-catalogue-2025) remains a separate metadata resource.

## Quality, rights and development

BOE captures can omit rendered numbering or flatten tables. Eleven materially incomplete bodies are withheld; remaining limitations are flagged. Four original-base instruments have five separately dated official-image passage completions with explicit version/correction provenance. Court contexts were reviewed individually; 71 reviewed current source versions remain private and six duplicate aliases supply body-free relations. All 38,011 original court-family files were byte/native/JSON processed; most are not contextually cleared for publication. A source body component is a publisher field or PDF body, not necessarily one semantic judgment. Publisher masks are preserved; this is not an anonymity certificate. See [quality](docs/quality.md), [court review](docs/court-audit.md) and [comparison](docs/comparison.md).

MIT covers new code, documentation and invented test fixtures. Actual official text uses the [source-specific statutory/policy basis and conditions](docs/source-rights.md), also recorded in the dataset's `RIGHTS.md`; it is not relicensed under MIT or the catalogue's CC0 dedication. No synthetic fixture or original PDF is included in the text dataset.

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider -o pythonpath=
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 .venv/bin/python scripts/fixture_demo.py --output demo-work
```

The offline fixture uses invented Arabic and a synthetic BOE-shaped identifier that is never fetched; it demonstrates software behavior separately from the real dataset example. Development, source assessment, testing and independent agent review were AI assisted. No government affiliation, human/legal-expert certification or expert accuracy benchmark is claimed. [Architecture and tradeoffs](docs/decision-record.md).
