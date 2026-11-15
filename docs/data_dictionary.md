# Data dictionary and decisions

## Source snapshot and grain

Workbook: `Ecommerce_Delivery_Analysis.xlsx` in the project root, read without modification. Expected source SHA-256 for these reported findings:

`659669b7e7a8d0b873de7ea9241efb5ba186113010bd8c4fe02f62d1fb7e651d`

Original external source URL, collection method, license and field documentation are not supplied. Do not infer them from familiar column names. No raw workbook is included in the portfolio ZIP; a reviewer can inspect supplied derived results without it, but cannot rebuild them without the source. Included reports contain selected raw comment excerpts and record IDs for local traceability; they have not been published.

| Table | Saved range | Observed grain |
| --- | --- | --- |
| Orders / OrdersData | A1:K99442 | 99,441 rows with unique, nonblank order IDs |
| Reviews / ReviewsData | A1:G99225 | 99,224 review records; 98,673 distinct order IDs; up to three records per order |

Orders has saved filters; the script reads all stored rows. The temporary Excel owner file beginning `~$` is not a source. IDs and relevant values are whitespace-trimmed for analytical grouping; original strings are preserved in the workbook.

## Fields used

| Sheet / column | Field | Analytical use and qualification |
| --- | --- | --- |
| Orders A | order_id | Unique order key; join to Reviews B |
| Orders B | customer_id | Present but not used for customer-level inference |
| Orders C | order_status | `delivered` selects the delivery population |
| Orders D | order_purchase_timestamp | Targeted chronology checks and case timelines |
| Orders E | order_approved_at | Case timeline checks; business event definition unverified |
| Orders F | order_delivered_carrier_date | Working carrier-handoff interpretation for case review; not proof of carrier responsibility |
| Orders G | order_delivered_customer_date | Working physical-arrival interpretation; definition requires confirmation |
| Orders H | order_estimated_delivery_date | Working promised calendar date; original versus revised promise unverified |
| Orders I | Delivery Status | Existing Excel label used as a cross-check, not calculation input |
| Orders J | Days Late | Existing calculation not used; sampled duration cells stored as dates |
| Orders K | Review_Score | Unfinished source column not used; K2 contains a COUNTIF expression stored as text |
| Reviews A | review_id | Traceability; repeated IDs alone do not justify deduplication |
| Reviews B | order_id | Order linkage; all nonblank source keys match Orders |
| Reviews C | review_score | Observed integer range 1–5; source scale documentation unverified |
| Reviews D/E | review_comment_title/message | Manual case interpretation; some garbled characters and source formula errors |
| Reviews F | review_creation_date | Chronology audit; invitation/creation meaning unverified |
| Reviews G | review_answer_timestamp | Latest-recorded-opinion selection; submission/edit/import meaning unverified |

## Analytical definitions

- Parse source ISO date/timestamp values using `datetime.fromisoformat`. Compare calendar dates without timezone conversion. Python retains microseconds; finer source fractional digits are truncated.
- Late means actual calendar date > estimated calendar date. On the estimated date counts as on time, following the existing workbook formula. This has not been confirmed against a corporate service agreement.
- Late rate = late assessed delivered orders / all assessed delivered orders. Eight missing-arrival cases remain unknown. Statuses such as canceled and shipped are excluded.
- Delay severity uses strictly positive days late only. Bands are 1–3, 4–7, 8–14, 15–30 and 31+ days: exploratory categories with unequal widths, not approved thresholds.
- Median uses the sorted middle value(s); P90 uses nearest rank at ceiling(0.90 × n). No population confidence interval is claimed.
- Select each order's latest response timestamp before applying the timing filter. Any invalid/missing response timestamp leaves the order unresolved. Conflicting latest-time scores also remain unresolved. Equal-time/equal-score ties use review ID then source row for provenance. No latest-time ties occur in this snapshot.
- Primary score population: late orders with a valid selected score whose response date is strictly after recorded delivery date. Same-day responses are excluded. It contains 1,719 orders.
- Sensitivity population: same late orders and selection rule, admitting all response timing groups. It contains 6,381 orders; 153 have no selected review. Means are calculated from individual scores, not an unweighted average of subgroup means.
- Store full 1–5 score frequencies and medians alongside means. Missing reviews are not zero scores. A mean treats consecutive score steps as equally spaced.
- Narrative tables and score-chart labels display scores to two decimals using half-up rounding; machine-readable results retain full precision. This makes 3.525 display as 3.53.

## Known issues and treatment

- Original delivery calculations are preserved. All 96,470 independently assessed delivery labels match saved Excel labels; Excel itself was not recalculated.
- Four comment cells contain formula errors: Reviews E33620, E59237, E64415 and D77434. Interpretations do not repair these cells. The six-case comment audit uses its separately identified source rows.
- Repeated review IDs are present, but no fully identical records were found across the seven extracted, whitespace-trimmed review fields. No record was deleted based solely on review ID.
- Flagged extreme dates and review/delivery disagreements remain unverified. No correction or outlier exclusion was applied.
- The six comments in the primary 31+ day group do not represent all 345 orders in that band; manual themes can overlap and English paraphrases are approximate.

## Scope of validation

Automated checks cover expected key headers, unique order IDs, count reconciliation, parseable required dates, targeted purchase chronology, case timeline consistency, latest-review coverage, one selected score per included order, and score frequencies across timing groups. A changed or incompatible layout stops relevant checks rather than silently reassigning known key columns. These checks do not establish source-system completeness, field semantics or factual event accuracy.

Use the data-owner checklist for external verification. Confirmed corrections belong in a separately traceable derived layer; preserve old value, new value, supporting evidence and metric changes. Unresolved cases stay in the baseline, with any exclusion analysis separately labeled.
