# Saudi legal text toolkit

This project pairs a downloadable collection of Arabic Saudi laws and court decisions with Python tools for developers and researchers. Use the dataset directly, or use this toolkit to process your own captures, search matching passages and follow official source citations.

[Download the dataset](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots) · [Read the dataset card](https://huggingface.co/datasets/Faisal73/saudi-legal-text-snapshots#readme) · [See worked examples](docs/text-examples.md)

## Try it

With CPython 3.12 installed, run:

```bash
git clone https://github.com/faisalm7/saudi-legal-snapshot-tools.git
cd saudi-legal-snapshot-tools
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps .
.venv/bin/python examples/texts.py --config article_spans --query 'لا يجوز' --show-parent --limit 1
```

The verified command found 275 matching articles from 52 parent documents. Its first result was Article 11 of the Civil Transactions Law; these are the returned heading and passage, displayed without the surrounding JSON:

```text
المادة الحادية عشرة
١- يجوز اتخاذ موطنٍ مختارٍ لعملٍ معيَّن، ويكون هو الموطن لكل ما يتعلق بهذا العمل؛ ما لم يُشترط صراحةً قصر هذا الموطن على أعمالٍ دون أخرى.

٢- لا يجوز إثبات وجود الموطن المختار إلا بالكتابة.
```

[Open the official article](https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-QyZK_iXS5KaxGqaCU-WTew). The full output also provides the match offset, parent context, source URL and hashes. Add `--open-source` to open the first citation, or filter court results with `--court` and `--city`. Public loading needs no private corpus, model service or account. PDF extraction is a separate workflow requiring supplied captures and Poppler.

## Coverage

| Configuration | Rows | Unit |
| --- | ---: | --- |
| `boe_documents` | 468 | BOE publication snapshots |
| `boe_article_spans` | 9,358 | Article spans linked to BOE parents |
| `laws` | 76 | MOJ instruments |
| `article_spans` | 4,505 | Articles in the MOJ hierarchy |
| `source_sections` | 1,605 | Other MOJ source units |
| `judgments` | 14,077 | Reviewed court-text contexts |

The release has **14,621 parent-level records from 14,620 source-publication snapshots**. Court coverage comprises 14,077 contexts from 14,076 publication parents, with 16,507 body components. Article spans are separate units, not additional parent documents. Ninety-six official annex image pages accompany six BOE parents. These are captured versions; identifiers and row counts do not establish unique laws, cases or disputes.

## How it works

- **Align structure conservatively.** PDF headings and captured page text can encode the same heading differently, while preambles cite article numbers. The [article boundary matcher](src/saudi_legal/articles.py#L64) requires one complete ordered alignment of isolated headings, then keeps exact parent slices and page evidence. Ambiguous boundaries remain unknown.
- **Search without rewriting quotations.** Arabic spelling variants and marks complicate lookup. The [search example](examples/texts.py#L17) folds diacritics, tatweel and alef variants, then maps hits back to the original character spans. Displayed wording stays unchanged; this is lexical search, not a retrieval-accuracy benchmark.
- **Represent difficult source layouts honestly.** One stored native field can contain a complete judgment and an unheaded appellate act. The [judicial validator](src/saudi_legal/moj.py#L384) binds both acts to absolute source intervals and leaves four absent appeal-header values null. It checks declared lineage rather than inventing a court, number or date.
- **Bind review to the exported version.** A text correction can leave old approvals stale. The [exporter](src/saudi_legal/text_release.py#L117) checks source, body and metadata projections against separate rights, quality and privacy decisions. Those checks establish consistency; they cannot establish that a supplied review judgment is true.

I collected the original material in 2025 for an earlier legal AI project and directed this release. Codex assisted with extraction, comparisons, code and documentation. Independent review means a separate AI-agent pass, not a claim of manual reading or legal certification.

## Limits and reuse

Source wording, masks, contradictory amounts, dates and partial marks remain documented. Unknown capture dates and unresolved boundaries stay unknown; publisher masks do not guarantee anonymity. This is neither legal advice nor a current consolidated statement of Saudi law. Processing of the original collection remains incomplete, and unfinished items are not included as completed work.

MIT covers new code and documentation. Official material retains its [separate source conditions](docs/source-rights.md). See [quality limits](docs/quality.md), [input requirements](docs/reproducibility.md) and [verification, structure examples and processing history](docs/release-evidence.md) before building on the data.
