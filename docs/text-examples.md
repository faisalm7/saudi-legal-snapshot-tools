# Search real Arabic text and inspect its sources

These commands were independently executed with a normal CPython 3.12 installation, no authentication and a fresh cache against published dataset commit `9a2ad812e5b12654b815d993aff6d94f9f88598b`. They load actual legal records, not fixtures. This pinned snapshot contains 5,188 court publications; later commits can add individually reviewed material.

## Find an article and its parent

```bash
python examples/texts.py --revision 9a2ad812e5b12654b815d993aff6d94f9f88598b --config article_spans --query 'لا يجوز' --show-parent --context-chars 60 --limit 1
```

Actual selected fields from the output:

```json
{
  "source_sequence": "المادة الحادية عشرة",
  "parent_title": "نظام المعاملات المدنية",
  "matched_text": "لا يجوز",
  "passage": "ما لم يُشترط صراحةً قصر هذا الموطن على أعمالٍ دون أخرى.\n\n٢- لا يجوز إثبات وجود الموطن المختار إلا بالكتابة.",
  "start_in_article": 142,
  "start_in_parent": 1978,
  "source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-QyZK_iXS5KaxGqaCU-WTew"
}
```

```text
275 matching article_spans rows from 52 parent documents; 4505 rows passed metadata filters out of 4505. Capture dates do not establish legal force.
```

The parent slice was checked before printing. The match is in the Civil Transactions Law, Article 11: [open the official article](https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-QyZK_iXS5KaxGqaCU-WTew). Capture and source-reported status fields are available in the parent; they do not establish current legal force.

## Filter court records before searching

```bash
python examples/texts.py --revision 9a2ad812e5b12654b815d993aff6d94f9f88598b --config judgments --query 'المحرر العادي' --court 'التجارية' --city 'الرياض' --context-chars 60 --limit 1
```

Actual selected fields:

```json
{
  "title": "القضية رقم 4471096668 لعام 1444 هـ",
  "source_id": "001b61f3-e24d-42ef-9afb-31c0b066ab7e",
  "matched_text": "المحرر العادي",
  "passage": "ف حساب وكما نصت المادة (1/29) من نظام الإثبات على أنه: (يعد المحرر العادي صادر ممن وقعه وحجة عليه، ما لم ينكر صراحة ما هو منسوب إليه ",
  "start_in_document": 1729,
  "source_url": "https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/RWasqmqc-0KuLmREzAmOcS-in51g7rwtfccNjWKUDr3wj2X_0EsDyxbfSmZ-Vhux"
}
```

```text
200 matching judgments rows from 200 parent documents; 1939 rows passed metadata filters out of 5188. Capture dates do not establish legal force.
```

[Open this official court citation](https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/RWasqmqc-0KuLmREzAmOcS-in51g7rwtfccNjWKUDr3wj2X_0EsDyxbfSmZ-Vhux). Court rows are already parent publications; article/section rows use `--show-parent` to load their complete parent. Use `--source-id` to inspect one publication, `--document-type` for an exact type, and `--captured-from YYYY-MM-DD` / `--captured-before YYYY-MM-DD` for capture-date filters. Add `--open-source` to either command to open its first citation in a browser.

Search is normalized lexical matching with offsets mapped back to untouched source text. It is not a semantic search system or a measured retrieval benchmark. The full output includes text hashes and capture timestamps. Pin both the code release and dataset revision when reproducing counts; selection and source versions change between releases.
