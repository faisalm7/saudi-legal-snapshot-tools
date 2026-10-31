# Search Arabic legal text and follow its sources

Load real records, search Arabic passages, inspect their parent documents and follow official citations. No private corpus, model, paid API or account is required.

These commands were executed with Python 3.12, toolkit commit `8efb511aec8da512a98a9a2742e74e923a31ed99` and public dataset commit `69e5ee3c229e9eadca8f3ea27915e72d914a766a`. That snapshot contains **12,885 court publications, 468 BOE publications and 76 MOJ instrument publications**. Newer private candidates are not included in these results.

## Set up once

```bash
git clone https://github.com/faisalm7/saudi-legal-snapshot-tools.git
cd saudi-legal-snapshot-tools
git checkout 8efb511aec8da512a98a9a2742e74e923a31ed99
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

The first run downloads public Parquet data. These checks used fresh Datasets loading caches and previously verified anonymous Hub downloads. They do not claim a new download of every file.

## Find a BOE article and inspect its parent

```bash
python examples/texts.py --revision 69e5ee3c229e9eadca8f3ea27915e72d914a766a --config boe_article_spans --query 'مجلس الإدارة' --show-parent --context-chars 110 --limit 1
```

Actual selected fields, flattened for readability:

```json
{
  "source_sequence": "المادة السادسة عشرة:",
  "parent_title": "تنظيم مؤسسة البريد السعودي",
  "matched_text": "مجلس الإدارة",
  "passage": "ة: ينشر هذا التنظيم في الجريدة الرسمية، ويعمل به بعد 180 يوما من تاريخ نشره، باستثناء الأحكام المتعلقة بتشكيل مجلس الإدارة واختصاصاته، فتعد نافذة من تاريخ نشره.",
  "start_in_source_row": 128,
  "source_id": "0041fa37-4a6d-4b68-a9ab-a9a700f2e88f",
  "source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1",
  "start_in_parent": 10026
}
```

```text
232 matching boe_article_spans rows from 54 parent documents; 9358 rows passed metadata filters out of 9358. Capture dates do not establish legal force.
```

The match is in Article 16 of the Saudi Post Corporation regulation. The example checks exact article membership before printing its parent passage. [Open the official BOE citation](https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1).

## Search without stripping the source's diacritics

```bash
python examples/texts.py --revision 69e5ee3c229e9eadca8f3ea27915e72d914a766a --config article_spans --query 'التعويض' --show-parent --context-chars 110 --limit 1
```

Actual selected fields:

```json
{
  "source_sequence": "المادة الحادية والأربعون",
  "parent_title": "نظام المعاملات المدنية",
  "matched_text": "التَّعويض",
  "passage": " العقد، ومع ذلك يكون من يتفاوض أو يُنهي التفاوض بسوء نية مسؤولاً عن الضرر الذي أصاب الطرف الآخر، ولا يشمل ذلك التَّعويض عمَّا فاته من كسب متوقع من العقد محل التفاوض.\n\n٢- يُعدُّ من سوء النية عدم الجدية في التفاوض، أو تعمد عدم الإد",
  "start_in_source_row": 188,
  "source_id": "PBbHmywh1XMp-Kyv3NtQLg",
  "source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-3qT8mn_EacHdNUebd3SrYw",
  "start_in_parent": 8706
}
```

```text
126 matching article_spans rows from 23 parent documents; 4505 rows passed metadata filters out of 4505. Capture dates do not establish legal force.
```

The query matches `التَّعويض` in Article 41 of the Civil Transactions Law. Search normalizes the query and index, then maps offsets back to preserved source wording. [Open the official article](https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-3qT8mn_EacHdNUebd3SrYw).

## Filter court publications before searching

```bash
python examples/texts.py --revision 69e5ee3c229e9eadca8f3ea27915e72d914a766a --config judgments --query 'التحكيم' --court 'التجارية' --city 'الرياض' --context-chars 110 --limit 1
```

Actual selected fields:

```json
{
  "source_sequence": null,
  "parent_title": "القضية رقم 439382277 لعام 1443 هـ",
  "matched_text": "التحكيم",
  "passage": "هـ، والمرفوعة ضد مُوكلتنا المُدَّعى عليهِا شركة / سعدي علي حبيب آل قريش؛ وذلك على النحو التالي:\n1 – وُجود شرط التحكيم:\nإنَّ القضيَّة المنظورة أمام فضيلتكم ناشئة عن عقد مُبرم بينَ شركة أيه هاك بايبليدنجين السعُوديَّة المحدودة شر",
  "start_in_source_row": 3386,
  "source_id": "057d4ec7-d262-4647-a1cc-243d888dae81",
  "source_url": "https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/27havKi3MQBhJkH8h6uSvMg0EpmRzNWHE83Zgc6q4jlFa7F-OLSfk-El9AHx7hpN"
}
```

```text
159 matching judgments rows from 159 parent documents; 5213 rows passed metadata filters out of 12885. Capture dates do not establish legal force.
```

Court rows are already parent publications. This first match is a party submission mentioning an arbitration clause; a text match does not establish the court's outcome. [Open this official court citation](https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/27havKi3MQBhJkH8h6uSvMg0EpmRzNWHE83Zgc6q4jlFa7F-OLSfk-El9AHx7hpN).

Use `--source-id 057d4ec7-d262-4647-a1cc-243d888dae81` with the court command to inspect that publication alone. Other filters are `--document-type` for an exact type and `--captured-from YYYY-MM-DD` / `--captured-before YYYY-MM-DD` for capture dates. Unknown capture dates do not match those date filters. Add `--open-source` to open the first citation in your default browser; official sites may be unavailable.

Full output includes row text hashes, parent text hashes when requested, capture timestamps, source identifiers and citations. All rows expose `text_ar`. Parent configurations `laws`, `boe_documents` and `judgments` expose `quality_flags`; court parents additionally expose `source_version_notice` and `source_components_json`. For article or section rows, inspect the corresponding parent for its quality flags. A court publication can contain multiple decision bodies; it is still one parent row.

This is normalized lexical search, not semantic search or a retrieval benchmark. Source-reported status and capture dates do not establish current legal force, finality or a count of unique cases. Keep the code commit, dataset commit, source citation and version notices when citing results.
