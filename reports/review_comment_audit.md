# Manual review of six selected long-delay comments

## Scope and interpretation

These are the six orders in the 31+ calendar-day delay band whose selected latest response was recorded strictly after recorded delivery day. They are not representative of all 345 orders in the band. Scores and case membership reconcile to the prior comparison: four scores of 1, one of 3, one of 5; mean 2.00.

Source: `Ecommerce_Delivery_Analysis.xlsx`, Reviews columns D (title) and E (message), with rows below. Source IDs, raw extracted title/message strings, response timestamps and Orders row references are in `long_delay_comment_cases` in `workbook_inventory.json`. Regenerate the extraction with `python3 scripts/inspect_workbook.py`. This document is a human interpretation layer and should be revisited if the source fingerprint or selection changes.

The Portuguese text contains garbled accented characters and, in one record, an Excel `_x000D_` escape. No source text has been repaired. English summaries below are approximate paraphrases, not verbatim translations or verified customer explanations of the numerical score. Multi-topic comments may have multiple themes. Categories are provisional manual interpretations for these cases only; do not infer causes from an omitted topic.

| Days late | Score | Orders row | Reviews row | Approximate English summary of title/message | Provisional themes |
| --- | ---: | ---: | ---: | --- | --- |
| 42 | 5 | 42458 | 9795 | Very high praise in the title; message says fast and efficient. | Positive speed/service; apparent tension with recorded delay |
| 36 | 3 | 33674 | 16260 | Product is excellent and as described, but delivery took too long and disappointed. | Explicit slow delivery; positive product experience |
| 35 | 1 | 50888 | 3597 | Product took about two months to arrive, and its dimensions do not match the advertisement; does not recommend. | Explicit slow delivery; product description/size issue |
| 32 | 1 | 23498 | 35101 | Poor service; lack of respect and consideration for customers; no longer recommends. | Service complaint; delivery delay not explicitly identified |
| 31 | 1 | 23936 | 38253 | Purchase was over three months ago and the product still has not arrived. | Nonreceipt claim; conflicts with recorded delivery timing |
| 31 | 1 | 79395 | 20107 | Both title and message are blank. | Reason unavailable |

## Specific verification flags

- Reviews row 38253 reports nonreceipt. Its recorded response date is 2018-03-27, whereas Orders row 23936 records delivery on 2018-03-11. The 16-calendar-day gap is internally calculated; neither source establishes which event is accurate. Possible issues include delivery evidence, response-event semantics, stale text or record linkage. Seek original tracking and review-event records rather than overwriting either date.
- Reviews row 9795 praises speed although the recorded order is 42 days late. This is not proof of an error or a false review. The comment's target and actual event records require verification.
- Reviews row 20107 has no comment. Its score cannot identify the reason for dissatisfaction. The response timestamp is 2018-09-29 and recorded delivery is 2018-03-05; a later response alone does not explain the score.

## What the evidence supports

Two of six cases explicitly describe slow delivery; one of these also describes a product issue. A separate case reports nonreceipt. The other cases describe poor service, praise speed, or provide no comment. These are overlapping/distinct observations, not a population estimate of complaint causes. Comments add context to the scores but do not identify a single main cause for this group or all long-delay orders.

Manager-facing explanation: "Some comments support delivery-related dissatisfaction, but the cases also mention product and service issues, include positive feedback, and reveal conflicts needing verification. We cannot attribute every low score to delay."

Validation: six unique order IDs; all cases satisfy the existing 31+ day and later-response rules; case scores reconcile to the previous group frequency counts. Manual interpretations were checked against stored title/message text. No inferred text repairs, source corrections, exclusions, or external messages were made.
