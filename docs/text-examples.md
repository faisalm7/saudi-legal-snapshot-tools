# Search Arabic legal text and follow its sources

Load real records, search Arabic passages, inspect their parent documents and follow official citations. No private corpus, model, paid API or account is required.

These commands were executed online with Python 3.12, a fresh noneditable installation of toolkit commit `895bb29769a4b49674c05add2532d40d6e5608b5` and public dataset commit `f07cd16c3a39fb6099a352b4e5d9b3c40c5ab2a1`. This pinned snapshot contains **13,977 court publications, 468 BOE publications and 76 MOJ instrument publications**. Later additions cannot change these results.

## Set up once

```bash
git clone https://github.com/faisalm7/saudi-legal-snapshot-tools.git
cd saudi-legal-snapshot-tools
git checkout 895bb29769a4b49674c05add2532d40d6e5608b5
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

The first run downloads public Parquet data. These three checks used an empty loading cache and explicit anonymous downloads from the dataset ID and revision below. A separate check downloaded and verified all 274 allowlisted files in that revision. No historical private capture or local data directory was substituted for the public dataset.

## Find a BOE article and inspect its parent

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision f07cd16c3a39fb6099a352b4e5d9b3c40c5ab2a1 --config boe_article_spans --query 'مجلس الإدارة' --show-parent --limit 1
```

Actual selected fields, flattened for readability:

```json
{
  "source_sequence": "المادة السادسة عشرة:",
  "parent_title": "تنظيم مؤسسة البريد السعودي",
  "matched_text": "مجلس الإدارة",
  "passage": "المادة السادسة عشرة: ينشر هذا التنظيم في الجريدة الرسمية، ويعمل به بعد 180 يوما من تاريخ نشره، باستثناء الأحكام المتعلقة بتشكيل مجلس الإدارة واختصاصاته، فتعد نافذة من تاريخ نشره.",
  "start_in_source_row": 128,
  "source_id": "0041fa37-4a6d-4b68-a9ab-a9a700f2e88f",
  "capture_timestamp_utc": "2025-08-09T10:54:01.306341Z",
  "text_sha256": "db99890ae7a06d69764217e5aac54eeb374cd8eefd6e178039c98b9a5890fd8f",
  "source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1",
  "start_in_parent": 10026,
  "parent_text_sha256": "1be04a14b054330548e154daa039597d4cf8b6a927eefa80063527bc3a14a63f"
}
```

```text
232 matching boe_article_spans rows from 54 parent documents; 9358 rows passed metadata filters out of 9358. Capture dates do not establish legal force.
```

The match is in Article 16 of the Saudi Post Corporation regulation. The example checks exact article membership before printing its parent passage. [Open the official citation](https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1).

## Search without stripping the source's diacritics

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision f07cd16c3a39fb6099a352b4e5d9b3c40c5ab2a1 --config article_spans --query 'التعويض' --show-parent --limit 1
```

Actual selected fields, flattened for readability:

```json
{
  "source_sequence": "المادة الحادية والأربعون",
  "parent_title": "نظام المعاملات المدنية",
  "matched_text": "التَّعويض",
  "passage": "لك على أطراف التفاوض التزاماً بإبرام هذا العقد، ومع ذلك يكون من يتفاوض أو يُنهي التفاوض بسوء نية مسؤولاً عن الضرر الذي أصاب الطرف الآخر، ولا يشمل ذلك التَّعويض عمَّا فاته من كسب متوقع من العقد محل التفاوض.\n\n٢- يُعدُّ من سوء النية عدم الجدية في التفاوض، أو تعمد عدم الإدلاء ببيانٍ جوهريٍّ مؤثرٍ في العقد.",
  "start_in_source_row": 188,
  "source_id": "PBbHmywh1XMp-Kyv3NtQLg",
  "capture_timestamp_utc": "2026-10-23T17:31:39.161567+00:00",
  "text_sha256": "9e027b0671ca1ef6094fafcc5923b54ffd9d8cd4607cf67cd300fe778e7c3332",
  "source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-3qT8mn_EacHdNUebd3SrYw",
  "start_in_parent": 8706,
  "parent_text_sha256": "5345a5ce8b50f94d9a9028030c4539086ec1450b76d0d5eabaa0592591f21b57"
}
```

```text
126 matching article_spans rows from 23 parent documents; 4505 rows passed metadata filters out of 4505. Capture dates do not establish legal force.
```

The query matches `التَّعويض` in Article 41 of the Civil Transactions Law. Search normalizes the query and index, then maps offsets back to preserved source wording. [Open the official citation](https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-3qT8mn_EacHdNUebd3SrYw).

## Filter court publications before searching

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision f07cd16c3a39fb6099a352b4e5d9b3c40c5ab2a1 --config judgments --query 'التحكيم' --court 'التجارية' --city 'الرياض' --limit 1
```

Actual selected fields, flattened for readability:

```json
{
  "source_sequence": null,
  "parent_title": "القضية رقم 439014012 لعام 1443هـ",
  "matched_text": "التحكيم",
  "passage": "ير الدائرة بعدم وجود مذكرة المدعى عليها بالنظام والمؤرخ في 09/09/1443ه ، وفي الجلسة المرئية في 09/10/1443هـ اكد وكيل المدعى عليها على دفعة السابق شرط التحكيم والذي دفع به في مذكرته بتاريخ 9/9/1443هـ المقدمة عن طريق النظام وبعرض ذلك على وكيل المدعي ذكر ان اول دفع قام به المدعى عليه كان بتاريخ 28/7/1443هـ وق",
  "start_in_source_row": 15151,
  "source_id": "0056f44d-a4c8-496d-a526-d6823f9e32c1",
  "capture_timestamp_utc": "2026-10-24T08:28:54.317470Z",
  "text_sha256": "085806df8878d99202f69c5985716d120350c0784c36504aeac560f981e78408",
  "source_url": "https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/7Rn08HAPxYpRR_kgFndyadfPahpOJjkFwp2LNZBTh5JHMDFD-3nAMF20m3aZJwPO"
}
```

```text
179 matching judgments rows from 179 parent documents; 5770 rows passed metadata filters out of 13977. Capture dates do not establish legal force.
```

Court rows are already parent publications. This match reports a party's arbitration defence and the other party's response; a text match does not establish the court's outcome. [Open the official citation](https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/7Rn08HAPxYpRR_kgFndyadfPahpOJjkFwp2LNZBTh5JHMDFD-3nAMF20m3aZJwPO).

Use `--source-id 0056f44d-a4c8-496d-a526-d6823f9e32c1` with the court command to inspect that publication alone. Other filters are `--document-type` for an exact type and `--captured-from YYYY-MM-DD` / `--captured-before YYYY-MM-DD` for capture dates. Unknown capture dates do not match those date filters. Add `--open-source` to open the first citation in your default browser; official sites may be unavailable.

Passages are fixed character windows around a match and can start or end inside a word. Increase `--context-chars` or inspect the full parent to read the surrounding argument. A clipped example passage does not mean that the stored parent text is clipped.

All rows expose `text_ar`. Parent configurations `laws`, `boe_documents` and `judgments` expose `quality_flags`; court parents additionally expose `source_version_notice` and `source_components_json`. For article or section rows, inspect the corresponding parent for its quality flags. A court publication can contain multiple decision bodies; it is still one parent row.

This is normalized lexical search, not semantic search or a retrieval benchmark. Source-reported status and capture dates do not establish current legal force, finality or a count of unique cases. Keep the code commit, dataset commit, source citation and version notices when citing results.

## Current snapshot check · 2 November 2026

The existing public `examples/texts.py` functions at code commit `895bb29769a4b49674c05add2532d40d6e5608b5` were applied to freshly streamed anonymous data from dataset commit `c67e21ae4b868cfed00cef51ab358b99b576b105` during verification of all six complete configurations. This was a function-level check during streaming, not another direct CLI invocation or download. The earlier CLI runs and their outputs above remain unchanged. Matching used the same queries, metadata filters and default `--context-chars 150`.

| Configuration | Matching rows | Parent documents | Rows after metadata filters | Full configuration rows |
| --- | ---: | ---: | ---: | ---: |
| `boe_article_spans` | 232 | 54 | 9358 | 9358 |
| `article_spans` | 126 | 23 | 4505 | 4505 |
| `judgments` | 179 | 179 | 5787 | 14013 |

The following CLI commands reproduce the recorded query options for this revision; they are not claimed as separately executed by this check. Use the installation above.

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision c67e21ae4b868cfed00cef51ab358b99b576b105 --config boe_article_spans --query 'مجلس الإدارة' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision c67e21ae4b868cfed00cef51ab358b99b576b105 --config article_spans --query 'التعويض' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision c67e21ae4b868cfed00cef51ab358b99b576b105 --config judgments --query 'التحكيم' --court 'التجارية' --city 'الرياض' --limit 1
```

Actual first-result fields follow. Parent offsets and hashes refer to the stored complete parent; court results are already parent rows. The fixed windows can begin or end inside a word. These matches do not establish legal force, a court outcome or retrieval accuracy.

### `boe_article_spans`

```json
{
  "configuration": "boe_article_spans",
  "query": "مجلس الإدارة",
  "source_sequence": "المادة السادسة عشرة:",
  "parent_title": "تنظيم مؤسسة البريد السعودي",
  "matched_text": "مجلس الإدارة",
  "passage": "المادة السادسة عشرة: ينشر هذا التنظيم في الجريدة الرسمية، ويعمل به بعد 180 يوما من تاريخ نشره، باستثناء الأحكام المتعلقة بتشكيل مجلس الإدارة واختصاصاته، فتعد نافذة من تاريخ نشره.",
  "start_in_source_row": 128,
  "source_id": "0041fa37-4a6d-4b68-a9ab-a9a700f2e88f",
  "capture_timestamp_utc": "2025-08-09T10:54:01.306341Z",
  "text_sha256": "db99890ae7a06d69764217e5aac54eeb374cd8eefd6e178039c98b9a5890fd8f",
  "source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1",
  "start_in_parent": 10026,
  "parent_text_sha256": "1be04a14b054330548e154daa039597d4cf8b6a927eefa80063527bc3a14a63f",
  "parent_source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1"
}
```

[Official source citation](https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1).

### `article_spans`

```json
{
  "configuration": "article_spans",
  "query": "التعويض",
  "source_sequence": "المادة الحادية والأربعون",
  "parent_title": "نظام المعاملات المدنية",
  "matched_text": "التَّعويض",
  "passage": "لك على أطراف التفاوض التزاماً بإبرام هذا العقد، ومع ذلك يكون من يتفاوض أو يُنهي التفاوض بسوء نية مسؤولاً عن الضرر الذي أصاب الطرف الآخر، ولا يشمل ذلك التَّعويض عمَّا فاته من كسب متوقع من العقد محل التفاوض.\n\n٢- يُعدُّ من سوء النية عدم الجدية في التفاوض، أو تعمد عدم الإدلاء ببيانٍ جوهريٍّ مؤثرٍ في العقد.",
  "start_in_source_row": 188,
  "source_id": "PBbHmywh1XMp-Kyv3NtQLg",
  "capture_timestamp_utc": "2026-10-23T17:31:39.161567+00:00",
  "text_sha256": "9e027b0671ca1ef6094fafcc5923b54ffd9d8cd4607cf67cd300fe778e7c3332",
  "source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-3qT8mn_EacHdNUebd3SrYw",
  "start_in_parent": 8706,
  "parent_text_sha256": "5345a5ce8b50f94d9a9028030c4539086ec1450b76d0d5eabaa0592591f21b57",
  "parent_source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg"
}
```

[Official source citation](https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-3qT8mn_EacHdNUebd3SrYw).

### `judgments`

```json
{
  "configuration": "judgments",
  "query": "التحكيم",
  "source_sequence": null,
  "parent_title": "القضية رقم 439014012 لعام 1443هـ",
  "matched_text": "التحكيم",
  "passage": "ير الدائرة بعدم وجود مذكرة المدعى عليها بالنظام والمؤرخ في 09/09/1443ه ، وفي الجلسة المرئية في 09/10/1443هـ اكد وكيل المدعى عليها على دفعة السابق شرط التحكيم والذي دفع به في مذكرته بتاريخ 9/9/1443هـ المقدمة عن طريق النظام وبعرض ذلك على وكيل المدعي ذكر ان اول دفع قام به المدعى عليه كان بتاريخ 28/7/1443هـ وق",
  "start_in_source_row": 15151,
  "source_id": "0056f44d-a4c8-496d-a526-d6823f9e32c1",
  "capture_timestamp_utc": "2026-10-24T08:28:54.317470Z",
  "text_sha256": "085806df8878d99202f69c5985716d120350c0784c36504aeac560f981e78408",
  "source_url": "https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/7Rn08HAPxYpRR_kgFndyadfPahpOJjkFwp2LNZBTh5JHMDFD-3nAMF20m3aZJwPO"
}
```

[Official source citation](https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/7Rn08HAPxYpRR_kgFndyadfPahpOJjkFwp2LNZBTh5JHMDFD-3nAMF20m3aZJwPO).
