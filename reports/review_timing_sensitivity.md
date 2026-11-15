# Sensitivity to review timing

## Question and method

Does the score-by-delay pattern change if we relax the requirement that a review response be recorded after delivery day?

The original comparison remains the primary analysis: one selected latest score per late order, response recorded strictly after delivery calendar day. The sensitivity comparison uses the same order IDs, latest-review selection, score validity rules and calendar-day delay bands, but admits responses before, on and after delivery day. Extreme values remain included. No source records were corrected.

## Results

| Days late | After-delivery orders | After-delivery mean | All latest-review orders | All latest mean | All latest coverage of band |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1–3 | 1,339 | 3.76 | 1,852 | 3.29 | 99.0% |
| 4–7 | 323 | 3.79 | 1,748 | 2.10 | 97.0% |
| 8–14 | 40 | 3.53 | 1,446 | 1.67 | 97.8% |
| 15–30 | 11 | 3.36 | 1,006 | 1.61 | 96.8% |
| 31+ | 6 | 2.00 | 329 | 2.06 | 95.4% |

The broader population contains 6,381 reviewed late orders, versus 1,719 in the primary analysis. The same 153 late orders lack a usable selected review; no invalid-score exclusions were needed. Higher coverage does not establish that reviewed orders represent unreviewed orders.

The averages change substantially in several bands. The broader pattern is not strictly decreasing: the 31+ day mean (2.06) is higher than the 15–30 day mean (1.61). We should not state that every additional delay range has a lower average score.

Timing-specific results help explain the population change:

| Days late | Before-day n / mean | Same-day n / mean | After-day n / mean |
| --- | --- | --- | --- |
| 1–3 | 205 / 1.54 | 308 / 2.41 | 1,339 / 3.76 |
| 4–7 | 1,196 / 1.60 | 229 / 2.33 | 323 / 3.79 |
| 8–14 | 1,370 / 1.59 | 36 / 2.78 | 40 / 3.53 |
| 15–30 | 993 / 1.59 | 2 / 2.00 | 11 / 3.36 |
| 31+ | 322 / 2.05 | 1 / 5.00 | 6 / 2.00 |

Here, n is the number of included orders, not review rows. Do not emphasize a mean based on one or two orders. Same-day means are not established post-delivery opinions because the audit compares calendar days only.

## Interpretation for a manager

"Review timing materially changes the results. Including opinions recorded while customers were still waiting lowers average scores in most delay groups. The broader comparison shows lower averages for 4–30-day delays than for 1–3-day delays, but the longest-delay group rises again. These are different reviewed populations, so we cannot claim a universal or causal relationship between delay length and rating."

The before-delivery groups generally have lower averages than after-delivery groups, but they are different customers/orders. This is not a before-and-after change in the same customer's score, and it does not show that receiving an order improves a rating. Earlier opinions may reflect waiting, other product/service experiences or source-event semantics. Final recorded delay length may not have been known when those earlier opinions were recorded. Field definitions and flagged cases remain unverified.

## Validation and reproduction

Run `python3 scripts/inspect_workbook.py`. Outputs are in `review_timing_sensitivity` in `reports/workbook_inventory.json`.

- One selected latest score per included order; 6,381 unique included orders plus 153 exclusions reconcile to 6,534 late orders.
- Within each delay band, before-day + same-day + after-day score frequencies reconcile exactly to all latest-review frequencies.
- After-day score frequencies match the unchanged primary analysis exactly.
- Means can be independently reconstructed from score frequencies: sum(score × count) / included orders. All 20 timing/band combinations were checked.
- Existing source fingerprint, ID, date and delivery checks passed. Source workbook and earlier chart remain unchanged.

This is a descriptive sensitivity check, not a replacement selected because it produces a preferred result, a causal analysis, or a proof that one timing population is correct for every business question.
