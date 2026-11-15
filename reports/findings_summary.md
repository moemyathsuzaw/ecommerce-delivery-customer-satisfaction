# Delivery performance and customer reviews

In this saved dataset, **6.77% of assessable delivered orders arrived after the promised calendar date** (6,534 of 96,470). Eight additional delivered orders lacked an arrival date and could not be assessed.

Among late orders, the median delay was **7 days**, the average was **10.6 days**, and 345 orders arrived at least 31 days after the promise. Seven of the ten longest recorded delays share one delivery date, warranting verification against tracking and source-system records.

Among selected latest reviews recorded after delivery day, average scores were 3.76 for 1–3-day delays and 2.00 for delays of 31+ days. However, only **six of 345** orders qualified in the longest-delay group, versus 1,339 of 1,870 in the shortest group. The selected reviews are not necessarily representative of all delayed orders. These figures suggest a possible association and do not establish that delays caused lower ratings.

A review-timing sensitivity check includes 6,381 late orders with a latest review, compared with 1,719 in the primary after-delivery-day analysis. Average scores change materially: for example, the 4–7-day mean falls from 3.79 to 2.10. The broader means are 3.29, 2.10, 1.67, 1.61 and 2.06 across increasing delay bands. The pattern is not consistently decreasing, and the broader population includes opinions recorded while customers were still waiting. This makes review timing a material limitation, not evidence that a later review changes a customer's opinion.

The six longest-band comments provide mixed evidence: two explicitly mention slow delivery, including one that also mentions a product issue. Other cases describe service problems, claim nonreceipt, praise speed, or contain no comment. Some text has garbled characters, and English interpretations are approximate.

**Recommended next step:** verify the flagged delivery records and review-event definitions with the data owner before assigning causes or changing records. Agree whether the stakeholder wants waiting-period opinions or later opinions, and report the corresponding coverage and group sizes alongside scores. Retain both timing comparisons so the effect of the population choice is visible.

Source: `Ecommerce_Delivery_Analysis.xlsx`, Orders and Reviews. Reproduce calculations with `python3 scripts/inspect_workbook.py`; supporting results and comment interpretations are in `reports/workbook_inventory.json` and `reports/review_comment_audit.md`. These are descriptive findings from the saved records, not estimates of current company performance. Original records remain unchanged.
