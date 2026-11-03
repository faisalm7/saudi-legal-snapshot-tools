# Search Arabic legal text and follow its sources

Load real records, search Arabic passages, inspect their parent documents and follow official citations. No private corpus, model, paid API or account is required.

## RC41: current public snapshot · 3 November 2026 UTC

The unchanged public example functions were executed on freshly and anonymously streamed commit `79fd30b30b2827fcedea5292f5d4537e9efcb624` during verification of all six complete configurations. This used the recorded options and default 150-character context; it was a function-level check, not a direct CLI rerun. Earlier pinned CLI and checkpoint outputs remain below.

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision 79fd30b30b2827fcedea5292f5d4537e9efcb624 --config boe_article_spans --query 'مجلس الإدارة' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision 79fd30b30b2827fcedea5292f5d4537e9efcb624 --config article_spans --query 'التعويض' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision 79fd30b30b2827fcedea5292f5d4537e9efcb624 --config judgments --query 'التحكيم' --court 'التجارية' --city 'الرياض' --limit 1
```

| Configuration | Matches | Matching parents | After metadata filter | Entire configuration |
| --- | ---: | ---: | ---: | ---: |
| `boe_article_spans` | 232 | 54 | 9,358 | 9,358 |
| `article_spans` | 126 | 23 | 4,505 | 4,505 |
| `judgments` | 180 | 180 | 5,802 | 14,038 |

Actual selected fields follow. Fixed windows can start inside a word; inspect the complete parent for context. Parent offsets and hashes bind articles to stored parents. Court results are parent-level contexts. Capture dates do not establish legal force; a text match does not establish an outcome.

```json
{
  "revision": "79fd30b30b2827fcedea5292f5d4537e9efcb624",
  "example_code_sha256": "7c164ab5e724f9d42b14d6024c178429e0e35574f898a131d240dea25c1bcf09",
  "examples": [
    {
      "configuration": "boe_article_spans",
      "query": "مجلس الإدارة",
      "matching_rows": 232,
      "matching_parent_documents": 54,
      "metadata_filtered_rows": 9358,
      "total_configuration_rows": 9358,
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
      "parent_source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1",
      "parent_metadata": {
        "document_type": "official_legal_instrument",
        "source_family": "boe",
        "capture_timestamp_utc": "2025-08-09T10:54:01.306341Z",
        "source_reported_status_at_capture": "ساري",
        "court_name": null,
        "appeal_court_name": null,
        "city": null,
        "appeal_city": null
      }
    },
    {
      "configuration": "article_spans",
      "query": "التعويض",
      "matching_rows": 126,
      "matching_parent_documents": 23,
      "metadata_filtered_rows": 4505,
      "total_configuration_rows": 4505,
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
      "parent_source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg",
      "parent_metadata": {
        "document_type": "نظام",
        "source_family": "MOJ_legislation",
        "capture_timestamp_utc": "2026-10-23T17:31:39.161567+00:00",
        "source_reported_status_at_capture": "ساري",
        "court_name": null,
        "appeal_court_name": null,
        "city": null,
        "appeal_city": null
      }
    },
    {
      "configuration": "judgments",
      "query": "التحكيم",
      "matching_rows": 180,
      "matching_parent_documents": 180,
      "metadata_filtered_rows": 5802,
      "total_configuration_rows": 14038,
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
  ]
}
```

These examples require only the public package and dataset. All 283 exported files and 30,050 streamed rows were checked anonymously. In the bounded viewer check, the split and Parquet APIs identified this revision but reported six pending configurations and zero failed jobs. All six first-row requests returned HTTP 500 `ResponseNotReady`; no viewer sample rows were verified for this snapshot. Use `--open-source` to follow a citation or `--source-id` to inspect one publication. No private capture or model service is required.

## RC40: earlier public snapshot · 3 November 2026 UTC

The unchanged public example functions were executed on freshly and anonymously streamed dataset commit `d8949cdb3a81f0a0a8a146d28a046d191165d17e` during verification of all six complete configurations. This used the recorded options and the default 150-character context; it was a function-level check, not another direct CLI run. The earlier pinned CLI and checkpoint outputs below remain historical evidence.

Use the setup below. These commands reproduce the recorded options against this exact snapshot:

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision d8949cdb3a81f0a0a8a146d28a046d191165d17e --config boe_article_spans --query 'مجلس الإدارة' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision d8949cdb3a81f0a0a8a146d28a046d191165d17e --config article_spans --query 'التعويض' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision d8949cdb3a81f0a0a8a146d28a046d191165d17e --config judgments --query 'التحكيم' --court 'التجارية' --city 'الرياض' --limit 1
```

| Configuration | Matches | Matching parents | After metadata filter | Entire configuration |
| --- | ---: | ---: | ---: | ---: |
| `boe_article_spans` | 232 | 54 | 9,358 | 9,358 |
| `article_spans` | 126 | 23 | 4,505 | 4,505 |
| `judgments` | 179 | 179 | 5,797 | 14,030 |

Actual selected output fields follow. Fixed windows can start inside a word; inspect the complete parent for context. Parent offsets and hashes bind each article to its stored parent. Court results are already parent-level text contexts. Capture dates do not establish legal force, and a text match does not establish a court outcome.

```json
{
  "revision": "d8949cdb3a81f0a0a8a146d28a046d191165d17e",
  "example_code_sha256": "7c164ab5e724f9d42b14d6024c178429e0e35574f898a131d240dea25c1bcf09",
  "examples": [
    {
      "configuration": "boe_article_spans",
      "query": "مجلس الإدارة",
      "matching_rows": 232,
      "matching_parent_documents": 54,
      "metadata_filtered_rows": 9358,
      "total_configuration_rows": 9358,
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
      "parent_source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1",
      "parent_metadata": {
        "document_type": "official_legal_instrument",
        "source_family": "boe",
        "capture_timestamp_utc": "2025-08-09T10:54:01.306341Z",
        "source_reported_status_at_capture": "ساري",
        "court_name": null,
        "appeal_court_name": null,
        "city": null,
        "appeal_city": null
      }
    },
    {
      "configuration": "article_spans",
      "query": "التعويض",
      "matching_rows": 126,
      "matching_parent_documents": 23,
      "metadata_filtered_rows": 4505,
      "total_configuration_rows": 4505,
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
      "parent_source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg",
      "parent_metadata": {
        "document_type": "نظام",
        "source_family": "MOJ_legislation",
        "capture_timestamp_utc": "2026-10-23T17:31:39.161567+00:00",
        "source_reported_status_at_capture": "ساري",
        "court_name": null,
        "appeal_court_name": null,
        "city": null,
        "appeal_city": null
      }
    },
    {
      "configuration": "judgments",
      "query": "التحكيم",
      "matching_rows": 179,
      "matching_parent_documents": 179,
      "metadata_filtered_rows": 5797,
      "total_configuration_rows": 14030,
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
  ]
}
```

These examples require only the public package and dataset. All 282 exported files and 30,042 streamed rows were checked anonymously. In the final bounded viewer check, the split and Parquet APIs identified this revision but six configurations were still pending; all six first-row endpoints returned HTTP 500 `ResponseNotReady`. No viewer sample rows were verified for this revision. The CLI supports `--open-source` to follow a citation, `--source-id` for one publication and capture-date filters. No private historical capture or model service is used.

## RC39: earlier public snapshot · 3 November 2026 UTC

The unchanged public example functions were executed on freshly and anonymously streamed dataset commit `dcde27b164f1ea7a1297def3bf82a181c5bcd573` during verification of all six complete configurations. This used the recorded options and the default 150-character context; it was a function-level check, not another direct CLI run. The earlier direct CLI outputs and later historical checkpoint comparisons remain below.

Use the setup below. These commands reproduce the recorded options against this exact snapshot:

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision dcde27b164f1ea7a1297def3bf82a181c5bcd573 --config boe_article_spans --query 'مجلس الإدارة' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision dcde27b164f1ea7a1297def3bf82a181c5bcd573 --config article_spans --query 'التعويض' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision dcde27b164f1ea7a1297def3bf82a181c5bcd573 --config judgments --query 'التحكيم' --court 'التجارية' --city 'الرياض' --limit 1
```

| Configuration | Matches | Matching parents | After metadata filter | Entire configuration |
| --- | ---: | ---: | ---: | ---: |
| `boe_article_spans` | 232 | 54 | 9,358 | 9,358 |
| `article_spans` | 126 | 23 | 4,505 | 4,505 |
| `judgments` | 179 | 179 | 5,794 | 14,025 |

Actual selected output fields follow. Fixed windows can start inside a word; inspect the complete parent for context. Parent offsets/hashes bind the article to its stored complete document. Court results are already parent-level text contexts. Capture dates do not establish legal force, and a text match does not establish a court outcome.

```json
{
  "revision": "dcde27b164f1ea7a1297def3bf82a181c5bcd573",
  "example_code_sha256": "7c164ab5e724f9d42b14d6024c178429e0e35574f898a131d240dea25c1bcf09",
  "examples": [
    {
      "configuration": "boe_article_spans",
      "query": "مجلس الإدارة",
      "matching_rows": 232,
      "matching_parent_documents": 54,
      "metadata_filtered_rows": 9358,
      "total_configuration_rows": 9358,
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
      "parent_source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1",
      "parent_metadata": {
        "document_type": "official_legal_instrument",
        "source_family": "boe",
        "capture_timestamp_utc": "2025-08-09T10:54:01.306341Z",
        "source_reported_status_at_capture": "ساري",
        "court_name": null,
        "appeal_court_name": null,
        "city": null,
        "appeal_city": null
      }
    },
    {
      "configuration": "article_spans",
      "query": "التعويض",
      "matching_rows": 126,
      "matching_parent_documents": 23,
      "metadata_filtered_rows": 4505,
      "total_configuration_rows": 4505,
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
      "parent_source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg",
      "parent_metadata": {
        "document_type": "نظام",
        "source_family": "MOJ_legislation",
        "capture_timestamp_utc": "2026-10-23T17:31:39.161567+00:00",
        "source_reported_status_at_capture": "ساري",
        "court_name": null,
        "appeal_court_name": null,
        "city": null,
        "appeal_city": null
      }
    },
    {
      "configuration": "judgments",
      "query": "التحكيم",
      "matching_rows": 179,
      "matching_parent_documents": 179,
      "metadata_filtered_rows": 5794,
      "total_configuration_rows": 14025,
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
  ]
}
```

These examples require only the public package and dataset. All 281 exported files and 30,037 streamed rows were checked anonymously. The six viewer sample endpoints also passed: 292 rows and 7,556 untruncated fields matched; 152 truncated cells were outside that comparison. Only the separate viewer Parquet-listing endpoint still reported pending jobs. The CLI supports `--open-source` to follow a citation, `--source-id` for one publication and capture-date filters. No private historical capture or model service is used.

## Earlier pinned CLI execution

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

## RC36 snapshot check · 2 November 2026

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

## RC37: earlier public snapshot

The same unchanged example functions were executed during the six complete anonymous streaming loads of commit `b04a43f072fd0cbf9ddedfe0f936d3d2121bdf85`. This was a function-level streaming check; the earlier direct CLI runs and the RC36 results above are preserved. These commands reproduce the recorded options:

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision b04a43f072fd0cbf9ddedfe0f936d3d2121bdf85 --config boe_article_spans --query 'مجلس الإدارة' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision b04a43f072fd0cbf9ddedfe0f936d3d2121bdf85 --config article_spans --query 'التعويض' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision b04a43f072fd0cbf9ddedfe0f936d3d2121bdf85 --config judgments --query 'التحكيم' --court 'التجارية' --city 'الرياض' --limit 1
```

| Configuration | Matches | Matching parents | After metadata filter | Entire configuration |
| --- | ---: | ---: | ---: | ---: |
| `boe_article_spans` | 232 | 54 | 9358 | 9358 |
| `article_spans` | 126 | 23 | 4505 | 4505 |
| `judgments` | 179 | 179 | 5788 | 14014 |

Actual matching passages, parent metadata, offsets, hashes and official citations:

```json
{
  "revision": "b04a43f072fd0cbf9ddedfe0f936d3d2121bdf85",
  "execution_method": "Existing public examples/texts.py functions applied to freshly anonymously streamed complete exact-revision dataset configurations during all6 verification, not a second corpus download or claimed direct CLI invocation.",
  "example_code_sha256": "7c164ab5e724f9d42b14d6024c178429e0e35574f898a131d240dea25c1bcf09",
  "examples": [
    {
      "configuration": "boe_article_spans",
      "query": "مجلس الإدارة",
      "matching_rows": 232,
      "matching_parent_documents": 54,
      "metadata_filtered_rows": 9358,
      "total_configuration_rows": 9358,
      "document_id": "sa-boe-0041fa37-4a6d-4b68-a9ab-a9a700f2e88f-ar-1be04a14b0543305",
      "source_sequence": "المادة السادسة عشرة:",
      "parent_title": "تنظيم مؤسسة البريد السعودي",
      "matched_text": "مجلس الإدارة",
      "passage": " يتعارض معه من أحكام. المادة السادسة عشرة: ينشر هذا التنظيم في الجريدة الرسمية، ويعمل به بعد 180 يوما من تاريخ نشره، باستثناء الأحكام المتعلقة بتشكيل مجلس الإدارة واختصاصاته، فتعد نافذة من تاريخ نشره.",
      "start_in_source_row": 128,
      "start_in_parent": 10026,
      "parent_metadata": {
        "document_type": "official_legal_instrument",
        "source_family": "boe",
        "capture_timestamp_utc": "2025-08-09T10:54:01.306341Z",
        "source_reported_status_at_capture": "ساري",
        "court_name": null,
        "appeal_court_name": null,
        "city": null,
        "appeal_city": null
      },
      "source_id": "0041fa37-4a6d-4b68-a9ab-a9a700f2e88f",
      "capture_timestamp_utc": "2025-08-09T10:54:01.306341Z",
      "text_sha256": "db99890ae7a06d69764217e5aac54eeb374cd8eefd6e178039c98b9a5890fd8f",
      "parent_text_sha256": "1be04a14b054330548e154daa039597d4cf8b6a927eefa80063527bc3a14a63f",
      "source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1"
    },
    {
      "configuration": "article_spans",
      "query": "التعويض",
      "matching_rows": 126,
      "matching_parent_documents": 23,
      "metadata_filtered_rows": 4505,
      "total_configuration_rows": 4505,
      "document_id": "moj-legislation:0927e0880ef0d812a4819a85b2af367eeddcdb0f97ef5bb3734759d35a4fff50",
      "source_sequence": "المادة الحادية والأربعون",
      "parent_title": "نظام المعاملات المدنية",
      "matched_text": "التَّعويض",
      "passage": "لك على أطراف التفاوض التزاماً بإبرام هذا العقد، ومع ذلك يكون من يتفاوض أو يُنهي التفاوض بسوء نية مسؤولاً عن الضرر الذي أصاب الطرف الآخر، ولا يشمل ذلك التَّعويض عمَّا فاته من كسب متوقع من العقد محل التفاوض.\n\n٢- يُعدُّ من سوء النية عدم الجدية في التفاوض، أو تعمد عدم الإدلاء ببيانٍ جوهريٍّ مؤثرٍ في العقد.\n\nالما",
      "start_in_source_row": 188,
      "start_in_parent": 8706,
      "parent_metadata": {
        "document_type": "نظام",
        "source_family": "MOJ_legislation",
        "capture_timestamp_utc": "2026-10-23T17:31:39.161567+00:00",
        "source_reported_status_at_capture": "ساري",
        "court_name": null,
        "appeal_court_name": null,
        "city": null,
        "appeal_city": null
      },
      "source_id": "PBbHmywh1XMp-Kyv3NtQLg",
      "capture_timestamp_utc": "2026-10-23T17:31:39.161567+00:00",
      "text_sha256": "9e027b0671ca1ef6094fafcc5923b54ffd9d8cd4607cf67cd300fe778e7c3332",
      "parent_text_sha256": "5345a5ce8b50f94d9a9028030c4539086ec1450b76d0d5eabaa0592591f21b57",
      "source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-3qT8mn_EacHdNUebd3SrYw"
    },
    {
      "configuration": "judgments",
      "query": "التحكيم",
      "matching_rows": 179,
      "matching_parent_documents": 179,
      "metadata_filtered_rows": 5788,
      "total_configuration_rows": 14014,
      "document_id": "sa-moj-0056f44d-a4c8-496d-a526-d6823f9e32c1-ar",
      "source_sequence": null,
      "parent_title": "القضية رقم 439014012 لعام 1443هـ",
      "matched_text": "التحكيم",
      "passage": "ير الدائرة بعدم وجود مذكرة المدعى عليها بالنظام والمؤرخ في 09/09/1443ه ، وفي الجلسة المرئية في 09/10/1443هـ اكد وكيل المدعى عليها على دفعة السابق شرط التحكيم والذي دفع به في مذكرته بتاريخ 9/9/1443هـ المقدمة عن طريق النظام وبعرض ذلك على وكيل المدعي ذكر ان اول دفع قام به المدعى عليه كان بتاريخ 28/7/1443هـ وق",
      "start_in_source_row": 15151,
      "start_in_parent": 15151,
      "parent_metadata": {
        "document_type": "judgment_and_appeal_publication_record",
        "source_family": "moj_judgments",
        "court_name": "المحكمة التجارية",
        "appeal_court_name": "محكمة الاستئناف",
        "city": "الرياض",
        "appeal_city": "منطقة الرياض",
        "capture_timestamp_utc": "2026-10-24T08:28:54.317470Z"
      },
      "source_id": "0056f44d-a4c8-496d-a526-d6823f9e32c1",
      "capture_timestamp_utc": "2026-10-24T08:28:54.317470Z",
      "text_sha256": "085806df8878d99202f69c5985716d120350c0784c36504aeac560f981e78408",
      "parent_text_sha256": "085806df8878d99202f69c5985716d120350c0784c36504aeac560f981e78408",
      "source_url": "https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/7Rn08HAPxYpRR_kgFndyadfPahpOJjkFwp2LNZBTh5JHMDFD-3nAMF20m3aZJwPO"
    }
  ]
}
```

## RC38: earlier public snapshot

The unchanged example functions were executed during six complete anonymous streaming loads of commit `23c5a1bb3d81ab93e41ebbb75662c6ab3a999bc2`. This is a function-level streaming check; earlier direct CLI and RC36/RC37 outputs above remain unchanged. These commands use the recorded options:

```bash
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision 23c5a1bb3d81ab93e41ebbb75662c6ab3a999bc2 --config boe_article_spans --query 'مجلس الإدارة' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision 23c5a1bb3d81ab93e41ebbb75662c6ab3a999bc2 --config article_spans --query 'التعويض' --show-parent --limit 1
python examples/texts.py --dataset Faisal73/saudi-legal-text-snapshots --revision 23c5a1bb3d81ab93e41ebbb75662c6ab3a999bc2 --config judgments --query 'التحكيم' --court 'التجارية' --city 'الرياض' --limit 1
```

| Configuration | Matches | Matching parents | After metadata filter | Entire configuration |
| --- | ---: | ---: | ---: | ---: |
| `boe_article_spans` | 232 | 54 | 9358 | 9358 |
| `article_spans` | 126 | 23 | 4505 | 4505 |
| `judgments` | 179 | 179 | 5789 | 14016 |

Actual passages, parent offsets, hashes and official citations follow. Court results are parent-level text records; article rows link to a separate parent.

```json
{
  "revision": "23c5a1bb3d81ab93e41ebbb75662c6ab3a999bc2",
  "execution_method": "Existing public examples/texts.py functions applied to freshly anonymously streamed complete exact-revision dataset configurations during all6 verification, queries reuse the same required six-stream verification, with no separate example load or claimed direct CLI invocation.",
  "example_code_sha256": "7c164ab5e724f9d42b14d6024c178429e0e35574f898a131d240dea25c1bcf09",
  "examples": [
    {
      "configuration": "boe_article_spans",
      "query": "مجلس الإدارة",
      "court_filter": null,
      "city_filter": null,
      "matching_rows": 232,
      "matching_parent_documents": 54,
      "metadata_filtered_rows": 9358,
      "total_configuration_rows": 9358,
      "document_id": "sa-boe-0041fa37-4a6d-4b68-a9ab-a9a700f2e88f-ar-1be04a14b0543305",
      "source_sequence": "المادة السادسة عشرة:",
      "title": "تنظيم مؤسسة البريد السعودي",
      "matched_text": "مجلس الإدارة",
      "matching_passage": "المادة السادسة عشرة: ينشر هذا التنظيم في الجريدة الرسمية، ويعمل به بعد 180 يوما من تاريخ نشره، باستثناء الأحكام المتعلقة بتشكيل مجلس الإدارة واختصاصاته، فتعد نافذة من تاريخ نشره.",
      "start_in_source_row": 128,
      "start_in_parent": 10026,
      "parent_passage": " يتعارض معه من أحكام. المادة السادسة عشرة: ينشر هذا التنظيم في الجريدة الرسمية، ويعمل به بعد 180 يوما من تاريخ نشره، باستثناء الأحكام المتعلقة بتشكيل مجلس الإدارة واختصاصاته، فتعد نافذة من تاريخ نشره.",
      "source_id": "0041fa37-4a6d-4b68-a9ab-a9a700f2e88f",
      "text_sha256": "db99890ae7a06d69764217e5aac54eeb374cd8eefd6e178039c98b9a5890fd8f",
      "parent_text_sha256": "1be04a14b054330548e154daa039597d4cf8b6a927eefa80063527bc3a14a63f",
      "capture_timestamp_utc": "2025-08-09T10:54:01.306341Z",
      "source_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/0041fa37-4a6d-4b68-a9ab-a9a700f2e88f/1"
    },
    {
      "configuration": "article_spans",
      "query": "التعويض",
      "court_filter": null,
      "city_filter": null,
      "matching_rows": 126,
      "matching_parent_documents": 23,
      "metadata_filtered_rows": 4505,
      "total_configuration_rows": 4505,
      "document_id": "moj-legislation:0927e0880ef0d812a4819a85b2af367eeddcdb0f97ef5bb3734759d35a4fff50",
      "source_sequence": "المادة الحادية والأربعون",
      "title": "نظام المعاملات المدنية",
      "matched_text": "التَّعويض",
      "matching_passage": "لك على أطراف التفاوض التزاماً بإبرام هذا العقد، ومع ذلك يكون من يتفاوض أو يُنهي التفاوض بسوء نية مسؤولاً عن الضرر الذي أصاب الطرف الآخر، ولا يشمل ذلك التَّعويض عمَّا فاته من كسب متوقع من العقد محل التفاوض.\n\n٢- يُعدُّ من سوء النية عدم الجدية في التفاوض، أو تعمد عدم الإدلاء ببيانٍ جوهريٍّ مؤثرٍ في العقد.",
      "start_in_source_row": 188,
      "start_in_parent": 8706,
      "parent_passage": "لك على أطراف التفاوض التزاماً بإبرام هذا العقد، ومع ذلك يكون من يتفاوض أو يُنهي التفاوض بسوء نية مسؤولاً عن الضرر الذي أصاب الطرف الآخر، ولا يشمل ذلك التَّعويض عمَّا فاته من كسب متوقع من العقد محل التفاوض.\n\n٢- يُعدُّ من سوء النية عدم الجدية في التفاوض، أو تعمد عدم الإدلاء ببيانٍ جوهريٍّ مؤثرٍ في العقد.\n\nالما",
      "source_id": "PBbHmywh1XMp-Kyv3NtQLg",
      "text_sha256": "9e027b0671ca1ef6094fafcc5923b54ffd9d8cd4607cf67cd300fe778e7c3332",
      "parent_text_sha256": "5345a5ce8b50f94d9a9028030c4539086ec1450b76d0d5eabaa0592591f21b57",
      "capture_timestamp_utc": "2026-10-23T17:31:39.161567+00:00",
      "source_url": "https://laws.moj.gov.sa/ar/legislation/PBbHmywh1XMp-Kyv3NtQLg#content-card-3qT8mn_EacHdNUebd3SrYw"
    },
    {
      "configuration": "judgments",
      "query": "التحكيم",
      "court_filter": "التجارية",
      "city_filter": "الرياض",
      "matching_rows": 179,
      "matching_parent_documents": 179,
      "metadata_filtered_rows": 5789,
      "total_configuration_rows": 14016,
      "document_id": "sa-moj-0056f44d-a4c8-496d-a526-d6823f9e32c1-ar",
      "source_sequence": null,
      "title": "القضية رقم 439014012 لعام 1443هـ",
      "matched_text": "التحكيم",
      "matching_passage": "ير الدائرة بعدم وجود مذكرة المدعى عليها بالنظام والمؤرخ في 09/09/1443ه ، وفي الجلسة المرئية في 09/10/1443هـ اكد وكيل المدعى عليها على دفعة السابق شرط التحكيم والذي دفع به في مذكرته بتاريخ 9/9/1443هـ المقدمة عن طريق النظام وبعرض ذلك على وكيل المدعي ذكر ان اول دفع قام به المدعى عليه كان بتاريخ 28/7/1443هـ وق",
      "start_in_source_row": 15151,
      "start_in_parent": 15151,
      "parent_passage": null,
      "source_id": "0056f44d-a4c8-496d-a526-d6823f9e32c1",
      "text_sha256": "085806df8878d99202f69c5985716d120350c0784c36504aeac560f981e78408",
      "parent_text_sha256": "085806df8878d99202f69c5985716d120350c0784c36504aeac560f981e78408",
      "capture_timestamp_utc": "2026-10-24T08:28:54.317470Z",
      "source_url": "https://laws.moj.gov.sa/ar/JudicialDecisionsList/1/7Rn08HAPxYpRR_kgFndyadfPahpOJjkFwp2LNZBTh5JHMDFD-3nAMF20m3aZJwPO"
    }
  ]
}
```
