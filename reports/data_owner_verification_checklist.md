# Data owner verification checklist

Draft for review — not sent. All items below are pending verification; none are confirmed source errors.

## Purpose

Confirm whether flagged delivery dates and review timestamps represent the intended business events before changing records, assigning causes or making operational recommendations.

Source snapshot: `Ecommerce_Delivery_Analysis.xlsx`, Orders and Reviews. SHA-256: `659669b7e7a8d0b873de7ea9241efb5ba186113010bd8c4fe02f62d1fb7e651d`.

Use order/review IDs as the primary lookup keys. Excel row numbers below are navigation aids for this saved snapshot and can change after sorting. Evidence should identify the same order and, where relevant, shipment or review event.

## 1. Confirm field meanings first

- [ ] Identify the original dataset/system, extract date, population and known exclusions. Is this operational data, a public historical dataset or another source? If original records are unavailable, document that limitation.
- [ ] Confirm whether `order_delivered_customer_date` records physical receipt, a carrier scan, an administrative closure or another event. Are timestamps ever backfilled or overwritten? Request the field definition and event/update history.
- [ ] Confirm what `order_estimated_delivery_date` means: the original customer promise or a revised estimate? Are original promises available? Confirm whether calendar days, business days or a specific cutoff time define lateness.
- [ ] Confirm timezone and timestamp conversion conventions. Check that source precision or formatting changes did not alter calendar dates.
- [ ] Confirm what `review_creation_date` and `review_answer_timestamp` represent. Does answer time refer to initial submission, later editing, import or another event? Request the review-event definitions and available version history.
- [ ] Confirm the review scale and whether a review covers an entire order, one item, one shipment or another unit. Explain why review IDs can recur across rows and whether multiple responses per order are legitimate events.

Acceptance evidence: a source dictionary, system-owner explanation linked to the relevant field, or original event records. A plausible interpretation of a column name alone is not verification.

## 2. Verify extreme recorded delivery delays

- [ ] For each case below, check the order/shipment mapping, original purchase and promise dates, carrier handoff, delivery tracking events and proof of delivery. Check returns, replacements, split shipments or administrative updates if recorded.
- [ ] Investigate why seven cases have recorded delivery on **2017-09-19**. Check whether this reflects physical deliveries, an import/backfill or a system update. The 188-day maximum is dated **2018-09-19** and is not part of that same-year cluster.
- [ ] Confirm or challenge the recorded arrival date using evidence tied to the same order/shipment. Record unresolved cases explicitly; large values alone do not justify exclusion.

| Order ID | Orders row | Recorded days late | Recorded delivery date |
| --- | ---: | ---: | --- |
| 1b3190b2dfa9d789e1f14c05b647a14a | 55621 | 188 | 2018-09-19 |
| ca07593549f1816d26a572e06dc1eab6 | 19592 | 181 | 2017-09-19 |
| 47b40429ed8cce3aee9199792275433f | 11401 | 175 | 2018-07-13 |
| 2fe324febf907e3ea3f2aa9650869fa5 | 81403 | 167 | 2017-09-19 |
| 285ab9426d6982034523a855f55a885e | 89132 | 166 | 2017-09-19 |
| 440d0d17af552815d15a9e41abe49359 | 61612 | 165 | 2017-09-19 |
| c27815f7e3dd0b926b58552628481575 | 68771 | 162 | 2017-09-19 |
| 0f4519c5f1c541ddec9f21b3bddd533a | 38511 | 161 | 2017-09-19 |
| d24e8541128cea179a11a65176e0a96f | 40849 | 161 | 2017-12-04 |
| 2d7561026d542c8dbd8f0daeadf67a43 | 54482 | 159 | 2017-09-19 |

## 3. Resolve review/delivery disagreements

| Order ID | Review ID | Snapshot rows | Question and requested evidence |
| --- | --- | --- | --- |
| 8b4fc455b9a8cc1559dca8dd2d392ddd | a1c89ee75aad49c3e5633106fe8b8e82 | Orders 23936; Reviews 38253 | Comment reports nonreceipt; recorded response is 2018-03-27, after recorded delivery on 2018-03-11. Verify physical receipt, original review submission/edit history and order/shipment linkage. Do not assume which field is wrong. |
| 814fe5df303b0c72aeddb331dbfe9802 | 8823d39e2b9ef012f2fd6af92d9b11c9 | Orders 42458; Reviews 9795 | Score 5 and praise for speed despite a 42-day recorded delay. Check original text, what the review refers to and original promise/delivery evidence. Positive feedback is not itself an error. |

- [ ] Confirm whether reviews recorded before delivery reflect customers still waiting or a different timestamp meaning. In the current late-order cohort, 4,086 latest responses are before delivery day, 576 on that day and 1,719 after it. Do not silently redefine the selected analysis population.
- [ ] Check original text/encoding against the extract before using translated or automatically categorized comments. Preserve the stored version and any separately verified repair.
- [ ] For blank comments, confirm availability in the source if relevant; do not infer a complaint reason from a score alone. Reviews row 20107 is one such case.

## 4. Investigate missing delivery dates

- [ ] Locate Orders rows where status is `delivered` and the actual customer delivery date is blank. The saved source contains eight such orders.
- [ ] Check whether valid arrival evidence exists and why the extract omitted it. Verify any recovered date against its order/shipment and source history.
- [ ] If no reliable date is available, retain unknown lateness. These cases currently sit outside the assessable late-rate denominator and must not automatically become late or on time.

## 5. Record a reviewable outcome for each item

Copy this entry for each case or field-definition question. Leave unverified information blank rather than guessing.

| Required field | Entry to complete |
| --- | --- |
| Order/review ID or field-definition question | |
| Assigned owner and date reviewed | |
| Original stored field/value and snapshot reference | |
| Evidence reference and event date | |
| Outcome: confirmed as recorded / correction supported / unresolved | |
| Explanation of what the evidence establishes | |
| Proposed derived value or analytical treatment, if any | |
| Reviewer and decision date | |
| Affected metrics and rerun result | |

- [ ] Preserve the original workbook. Apply supported analytical corrections only in a separately documented derived dataset, with old value, new value, reason and evidence reference.
- [ ] For confirmed records, retain them even when unusually large. For unresolved records, retain and flag them in the existing baseline; show any proposed exclusions only as an explicitly labeled sensitivity analysis.
- [ ] After supported changes, rerun order uniqueness, date validity, chronology, review selection, eligibility and reconciliation checks. Compare the late rate, delay statistics, review coverage and score groups with the original baseline, including changed-case counts.
- [ ] Update the README and findings with verified definitions, changes and remaining limitations. An unresolved evidence request can be documented without pretending the dataset is fully verified.

## Review status

Checklist prepared from the saved analysis outputs. No external records have been checked, no data owner has been contacted, and no source corrections have been made. Case IDs and row references were cross-checked against `reports/workbook_inventory.json` before delivery.
