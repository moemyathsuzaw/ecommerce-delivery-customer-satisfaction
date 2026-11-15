# E-commerce Delivery and Customer Satisfaction Analysis

## Purpose and learning roadmap

Build a reproducible analysis that helps an operations manager understand delivery performance and its relationship with customer review scores. Work in small stages, with a learner decision before progressing.

1. Inventory existing work and frame the business question (current stage).
2. Verify what one row represents, identifier uniqueness, missing data, date validity and review relationships.
3. Agree KPI definitions, eligibility rules and how to handle multiple reviews per order.
4. Prepare analysis data using Python, with SQL practice where useful.
5. Calculate KPIs and compare delivery groups using charts and appropriate uncertainty measures.
6. Communicate findings, limitations and recommendations to a nontechnical manager.

## Source and preservation

- Original: `Ecommerce_Delivery_Analysis.xlsx`. Never overwrite it.
- The `~$` file is an Excel temporary owner file and is not an analysis input.
- External dataset source, collection method, coverage and permission details are not yet documented. Do not assume the data represents all e-commerce customers.
- No files have been committed or pushed. GitHub setup was awaiting browser authentication before the mentoring task began; it is not required for this learning stage.

## Existing work observed

Inventory of the saved workbook on 2026-11-15:

| Sheet / table | Table range | Rows below header | Existing content |
| --- | --- | ---: | --- |
| Orders / OrdersData | A1:K99442 | 99,441 | Order identifiers, status, purchase and delivery dates, plus Delivery Status, Days Late and Review_Score columns |
| Reviews / ReviewsData | A1:G99225 | 99,224 | Review identifiers, order identifiers, scores, comments and timestamps |

These are table row counts, not verified distinct order or review counts.

The workbook already has structured Excel tables and delivery calculations. Delivery Status compares calendar dates, classifying missing dates separately. Days Late uses the positive calendar-day difference, capped at zero for early/on-time delivery. Preserve this work and validate it before changing its definitions.

OrdersData has saved filters for delivered status and a delivery-date condition. Visible Excel rows may therefore differ from the full stored table. Future analytical filters must be explicit in code.

Items requiring investigation, not yet repaired:

- Orders!K2 (Review_Score) stores `=COUNTIF(ReviewsData[order_id],[@order_id])` as text rather than an evaluated formula. COUNTIF would count review rows, not retrieve a satisfaction score. K3 is blank in the inspected sample.
- Days Late sample cells J2 and J3 are stored as date values (`1899-12-30`), although the column is meant to be a duration. Inspect cell types and formatting before converting them into numbers.
- Four review comment cells contain formulas with cached `#NAME?` errors: E33620, E59237, E64415 and D77434. Their expressions resemble comments beginning with a minus sign. Verify intended text before any correction in a derived copy.
- No embedded charts or PivotTables were found. No pre-existing README or analysis scripts were found in the project.

## Stage 1: define the question and the row meaning

Candidate stakeholder question, awaiting learner choice: **Do late-delivered orders receive lower review scores than on-time orders?** This could help an operations manager prioritize a delivery-service investigation.

Working hypothesis: Orders contains one row per order, and Reviews contains one row per review record. This must be tested using identifiers. Do not assume one review per order. Joining reviews directly could repeat orders and distort order-level rates.

Alternative first question: **What proportion of delivered orders arrived after the promised calendar date?** This is a simpler operational baseline and does not require review matching.

Provisional definition inherited from the existing delivery formula: arriving on the estimated calendar date counts as on time. Confirm this business rule before publishing a KPI. No KPI population or multiple-review rule has been approved yet.

Even if late orders have lower scores, that would establish an association, not prove delay caused dissatisfaction. Product quality, seller service and which customers submit reviews could affect the comparison. Missing reviews must not be treated as zero scores.

Learner decision: start with question A, delivery lateness, to establish a baseline before investigating weaknesses. Overall lateness alone will not identify the source of the weakness; later comparisons will need suitable grouping fields.

## Stage 2: order grain and date coverage

Selected question: **What proportion of delivered orders arrived after the promised calendar date?**

The expanded inventory script profiles all saved Orders rows, including those hidden by Excel filters. It checks the expected column headers before applying the mapping and trims whitespace for profiling only. Source values remain unchanged.

Results from the current saved source:

- 99,441 populated order rows and 99,441 distinct nonblank order IDs.
- No missing order IDs and no repeated order IDs after whitespace trimming. This supports one row per order in this file; it does not verify completeness against the original business system.
- 96,478 orders have status `delivered`. The other 2,963 have other statuses.
- Of delivered orders, 96,470 have both actual and estimated delivery dates present. Eight lack an actual customer delivery date. No delivered orders have a missing estimated date in this presence check.
- Presence does not establish date validity. Parsing dates, chronological checks and comparison with existing formulas are deferred until the next stage.

Validation: status counts sum to order rows; delivered date-coverage groups sum to delivered orders; distinct IDs plus duplicate excess rows plus missing IDs reconcile to order rows. The source SHA-256 remained unchanged during the run.

Implementation: `Counter` counts occurrences of each order ID and status. A duplicate-excess count sums occurrences beyond the first. Date-coverage groups separate missing evidence from dates available for assessment. These checks are in `scripts/inspect_workbook.py`, and results are under `order_profile` in `reports/workbook_inventory.json`.

Pending business decision: do not automatically call delivered orders with missing actual dates late or on time. Proposed reporting is a late rate among assessable delivered orders, accompanied by the number of delivered orders with unknown lateness. Dates must pass validity checks before that population is final. Excluding missing dates can bias a rate if missingness is related to delay, so report coverage alongside the KPI.

Learner decision: missing actual delivery dates are **unknown**, not automatically late. Customer evidence could resolve a case only if it reliably establishes the arrival date. The learner approved calculating the late rate among delivered orders with valid actual and promised dates, reporting unknown cases separately.

## Stage 3: validated delivery baseline

Business purpose: establish an overall delivery-service baseline before investigating where delays occur.

Definition: an order marked `delivered` is late if its actual customer delivery calendar date is strictly after its estimated delivery calendar date. Arrival on the promised day is on time, following the existing workbook rule. This remains an analytical convention until confirmed against an actual service-level agreement. Time-of-day and timezone conversion are not used. Missing or unparseable required dates are unknown.

The script parses the source ISO date/timestamp values with `datetime.fromisoformat(...).date()` and compares dates. It stops KPI publication if order IDs repeat, are missing, or required purchase chronology checks fail. It does not use the Days Late column, whose source date storage needs separate review.

| Classification among delivered orders | Count |
| --- | ---: |
| Late | 6,534 |
| On time (including early) | 89,936 |
| Unknown: missing dates | 8 |
| Unknown: invalid actual/estimated dates | 0 |
| Total delivered | 96,478 |

Late rate = 6,534 / (6,534 + 89,936) = **6.77%**. The denominator is 96,470 assessable delivered orders, not all 99,441 source orders. Assessment coverage = 96,470 / 96,478 = **99.9917%**.

Validation performed:

- Date parsing succeeded for both required dates on all 96,470 assessable delivered orders.
- Actual and promised calendar dates were on or after the purchase date for all assessed orders, and all assessed purchase timestamps parsed successfully. This is a targeted chronology check, not a complete audit of every timestamp.
- All 96,470 computed Late/On time labels matched the saved Excel Delivery Status values. Cached labels were not recalculated in Excel.
- Classifications reconcile: 6,534 + 89,936 + 8 = 96,478 delivered orders.
- SHA-256 before and after inspection was unchanged.

Reproduce with the same inventory command above; results are in the `delivery_kpi` section of the JSON report. Rates are stored as proportions (0.06773...), with multiplication by 100 only for percentage presentation.

Manager-facing statement: "In this saved dataset, 6.77% of delivered orders with usable dates arrived after the promised day. Eight delivered orders could not be assessed because their arrival dates were missing. We have established a baseline; we have not yet identified what drives delays."

Uncertainty: this describes the saved records, not all e-commerce activity or current performance. No sampling frame or source-system completeness evidence has been established, so a population confidence interval is not supplied. Unknown cases could bias the assessable-only rate. Counting none versus all of the eight unknown cases as late would bound the full-delivered rate at approximately 6.7725% to 6.7808%; this is a missing-case sensitivity range, not a confidence interval. Overall lateness does not establish root causes or its effect on satisfaction.

Learner response: 96,470 are the assessable delivered orders. The learner then chose to investigate how many days late delayed orders arrive, before exploring time trends.

## Stage 4: severity among late orders

Stakeholder question: when delivery is late, how long do customers wait beyond the promised day? This helps operations distinguish frequent short delays from a smaller set of prolonged delays and frame an investigation or customer-support response.

Population: the 6,534 assessed delivered orders with positive calendar days late. Exclude on-time/early orders and eight unknown cases. Including on-time zeroes would instead measure delay averaged across all assessable deliveries and obscure the experience of late-order customers. This is days after the promise, not days since purchase.

| Metric | Calendar days late |
| --- | ---: |
| Mean | 10.62 |
| Median | 7 |
| 90th percentile | 22 |
| Minimum | 1 |
| Maximum | 188 |

Median is the middle of the sorted delay values (the average of the two middle values for even counts). At least half of late orders were no more than seven days late. The mean is 69,392 total days late divided by 6,534 late orders. The mean exceeding the median indicates that longer delays pull the average upward. The 90th percentile uses nearest rank: sorted observation at position ceiling(0.90 × 6,534) = 5,881, counting from one. At least 90% of late orders were no more than 22 days late. Other percentile algorithms can give different answers, so the method is explicit.

| Delay band | Late orders | Share of late orders |
| --- | ---: | ---: |
| 1–3 days | 1,870 | 28.62% |
| 4–7 days | 1,802 | 27.58% |
| 8–14 days | 1,478 | 22.62% |
| 15–30 days | 1,039 | 15.90% |
| 31+ days | 345 | 5.28% |

These are exploratory reporting bands, not company-agreed severity thresholds. All extreme observations remain included. The 188-day maximum requires source verification before operational conclusions; a parseable date does not prove the event was recorded correctly.

Implementation extends the existing script rather than redoing source preparation. Positive delays are appended to `late_delays`; `statistics.mean` and `statistics.median` summarize them. Results are saved under `delay_severity` in `reports/workbook_inventory.json` using the same reproduction command.

Validation: the severity list contains exactly 6,534 orders, sums to the existing 69,392 days late, and its mutually exclusive bands sum to 6,534. Existing date, identifier, classification, reconciliation and source-preservation checks also pass. Band percentages use late orders as the denominator. No source data was changed.

Manager-facing statement: "Among late orders, the median delay was seven days and the average was 10.6 days. At least 90% arrived within 22 days after the promised date. A small group had much longer recorded delays, which we should verify and investigate."

Limitations: these figures describe the recorded late deliveries, not undelivered orders, unknown cases or present-day company performance. They do not establish causes or the effect on satisfaction. Customer harm and acceptable thresholds require business context; do not infer them from these bands alone.

Learner demonstrated understanding using a five-order teaching example: the median better described typical delays when one very long delay pulled the mean upward. The learner then chose to investigate unusually long recorded delays before visualization.

## Stage 5: review the longest recorded delays

Purpose: prepare a short case list for operations and the data owner to investigate before deciding whether extreme values reflect real service failures or recording issues.

Scope: the ten longest delays among assessed late orders, ordered by days late descending, with order ID as a deterministic tie-break. This is a focused case review, not a representative sample or a company definition of an outlier. All cases remain included in the KPI.

The existing script now retains the source row, order ID and recorded purchase, approval, carrier handoff, promised and actual delivery dates for these cases. `sorted(late_records, key=lambda r: (-r["days_late"], r["order_id"]))[:10]` selects the review list. Source XML strings are retained in the report; display dates below use calendar dates only.

| Orders sheet row | Days late | Purchase to handoff days | Handoff to delivery days | Recorded delivery date |
| --- | ---: | ---: | ---: | --- |
| 55621 | 188 | 3 | 205 | 2018-09-19 |
| 19592 | 181 | 15 | 195 | 2017-09-19 |
| 11401 | 175 | 34 | 157 | 2018-07-13 |
| 81403 | 167 | 4 | 186 | 2017-09-19 |
| 89132 | 166 | 1 | 194 | 2017-09-19 |
| 61612 | 165 | 8 | 188 | 2017-09-19 |
| 68771 | 162 | 6 | 182 | 2017-09-19 |
| 38511 | 161 | 13 | 181 | 2017-09-19 |
| 40849 | 161 | 4 | 171 | 2017-12-04 |
| 54482 | 159 | 1 | 187 | 2017-09-19 |

Longest case (order `1b3190b2dfa9d789e1f14c05b647a14a`, Orders row 55621): purchased 2018-02-23, handed to carrier 2018-02-26, promised 2018-03-15, recorded delivered 2018-09-19. Actual minus promised is 188 days. Purchase to handoff is three calendar days, and handoff to recorded delivery is 205 days. Handoff-to-delivery duration is not the same measure as days late.

Seven of the ten cases share a recorded delivery date of **2017-09-19**. The maximum case is **2018-09-19**, a different year, and is not part of that seven-case cluster. The cluster is a reason to investigate, not proof of an error. Possible explanations include real delivery events or a source-system record update process. Neither explanation is established by this workbook.

Validation performed: all five dates in each of the ten cases parsed; calendar-date ordering purchase → approval → handoff → actual delivery had no reversals. Each actual-minus-promised difference matched days late; purchase-to-handoff plus handoff-to-delivery reconciled to purchase-to-delivery. Existing source-preservation and KPI checks passed. Checks operate at calendar-day resolution, not within-day timestamp resolution. Passing these checks establishes internal consistency, not real-world accuracy.

Recommended workplace follow-up (not executed): give the order IDs to the data owner and request carrier tracking events, proof of delivery and event/update history, especially for the seven cases recorded delivered on 2017-09-19. Determine whether the field records physical delivery or an administrative update. The long recorded intervals after handoff identify a stage to investigate; they do not establish carrier fault. No external messages were sent.

Do not delete extremes simply because they are large. Retain and flag them until evidence supports a correction or an explicit exclusion policy. Any later sensitivity analysis must label exclusions and show their effect alongside the unchanged baseline.

Manager-facing statement: "Our longest recorded delay is 188 days. Seven of the ten longest cases share one delivery date. The date sequences are internally consistent, but we need tracking and record-history evidence to confirm what those dates represent before assigning a cause."

Reproduce with `python3 scripts/inspect_workbook.py`. Full case records are in `longest_delay_review` in `reports/workbook_inventory.json`.

Learner exercise: seven extreme cases share one delivery date. Does this prove the records are wrong, or give us a reason to investigate? Explain briefly. Pause before proceeding.

Learner follow-up: reliable dated proof matching an order would support correcting its delivery date in a derived analysis, while preserving the source and correction evidence. No such external proof is available for the actual cases, so the records remain flagged and included. The learner chose to visualize the distribution next.

## Stage 6: visualize delay severity

Purpose: show an operations manager how late-order volume is distributed across shorter and longer recorded delays.

Chart: `reports/figures/delay_distribution.png` (presentation image) and `.svg` (scalable export). The five ordered bars reuse the validated delay bands, with counts and shares of the 6,534 late orders. All extremes are included. The first two bands contain 3,672 orders, or 56.20% of late orders. The 31+ day band contains 345 orders (5.28%). These percentages do not use all deliveries as their denominator.

Design decision: an ordered categorical bar chart keeps the existing groups readable without compressing short delays along a 188-day continuous axis. These ranges have unequal widths and an open-ended final band. Bar heights show counts in categories, not probability density or counts per day. Grouping sacrifices exact daily detail and can conceal patterns within a band. The 31+ band spans through the maximum recorded 188-day delay. Thresholds are exploratory, not approved company severity categories.

Reproduce after the inventory:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/inspect_workbook.py
python3 scripts/plot_delay_distribution.py
```

The installed plotting dependency used for this stage is Matplotlib 3.8.0. No additional packages were installed during this stage. The chart script reads the existing JSON report, checks that its SHA-256 still matches the original workbook, validates that counts and proportions reconcile, and writes only derived chart files. A changed source requires refreshing the inventory before plotting.

Key code: `ax.bar(labels, counts)` encodes counts as heights; `ax.annotate(...)` adds counts and percentages. The vertical axis starts at zero so bar-length comparisons are honest. The same color is used across all bands because no business-approved alert threshold has been established.

Validation: band counts sum to 6,534 and each share matches count / 6,534. Source fingerprint matches the report. Both chart exports were produced; the PNG was visually inspected for readable labels, unclipped annotations and clear source/population notes.

Manager-facing statement: "Among recorded late deliveries, 56.2% arrived within seven days after the promise. Another 345 orders arrived 31 days or more after it. Those longer-delay cases warrant investigation, but the chart does not explain their causes."

Learner exercise: the 31+ day bar says 5.3%. Is that 5.3% of all orders, or 5.3% of late orders? Pause here before proceeding.

Learner correctly identified late orders as the denominator and chose to explore whether longer delays are associated with lower review scores.

## Stage 7: validate review linkage before comparing scores

Business purpose: prepare a fair order-level comparison of delay length and customer review scores. A score is a proxy for the customer's overall experience, not a direct measure of delivery satisfaction alone.

Scope for this stage: audit the relationship between Orders and Reviews. No association estimates or causal claims are produced yet. Use the original Reviews score field, not the unfinished Orders Review_Score column.

The existing inspection script now collects review ID, order ID and score from all populated Reviews rows, with header checks. `Counter(order_id)` establishes how many review rows would match each order. Existing order uniqueness, source fingerprint and reconciliation checks remain in place.

Observed in the saved workbook:

- 99,224 review rows refer to 98,673 distinct nonblank order IDs. No order IDs or review IDs are missing, and all review order IDs match the Orders table.
- 547 orders have more than one review row, with a maximum of three rows per order. Across all orders, 202 have multiple distinct recorded score values.
- There are 98,410 distinct review IDs; 789 review IDs occur more than once. Repeated IDs must not be treated as automatically identical records. Record-level duplicate investigation remains pending.
- All stored score values are integers from 1 through 5. This is the observed range; the original questionnaire or dataset documentation has not been supplied to verify the scale definition.

| Coverage among the 6,534 late orders | Orders |
| --- | ---: |
| No review | 153 |
| Exactly one review row | 6,353 |
| Multiple review rows | 28 |
| Total | 6,534 |

A raw left join (preserving orders even when no review matches) would produce 6,562 rows for the 6,534 late orders. It would overrepresent orders with multiple review rows in later calculations. Validation: coverage categories sum to 6,534; review counts grouped by order reconcile to 99,224; no unmatched nonblank review order keys were found. The existing source-preservation and KPI checks passed.

Pending learner decision on an order-level score rule:

- Average the available scores for each order after investigating duplicate records: simple exploratory summary, preserves multiple recorded opinions and gives each order one final value. It treats score steps as equally spaced and may hide changes in opinion.
- Choose the latest reliably dated review per order: focuses on the latest recorded opinion, but requires validating review timestamps and an explicit tie-break rule. It can discard earlier opinions and does not prove the review describes the delivered experience.

Neither rule has been implemented. Missing reviews remain unavailable, never zero. Before comparison, inspect duplicate records and review timing relative to delivery; report review availability by delay group, since customers who review may differ from those who do not. Future comparisons must state their reviewed-order population and sample sizes. An observed association could reflect product quality, seller service or review selection, and would not establish that delay caused the score.

Reproduce the audit using `python3 scripts/inspect_workbook.py`; output is under `review_linkage_profile` in the existing JSON report. No raw data or existing charts changed.

Learner decision exercise: should one order's analysis score summarize its available ratings with an average, or represent its latest recorded opinion? Choose a rule and explain the purpose briefly. Pause here before further implementation.

Learner selected the latest recorded opinion per order.

## Stage 8: select latest reviews and inspect review timing

Business purpose: attach at most one recorded opinion to each order and establish whether it was recorded before or after delivery. This affects what we can tell a manager about customer experience.

Working timestamp definition: use `review_answer_timestamp` (Reviews column G), interpreted from its label as when the customer response was recorded. This is not assumed to be the last edit time. Original dataset documentation has not been supplied to confirm event semantics. Do not use row order or review ID as evidence of recency.

Implemented selection in the existing script: group review records by order ID, parse response timestamps, find `max(timestamp)`, then select that record. If a timestamp is missing/invalid, leave the order unresolved. Latest-time ties with different scores are unresolved; equal-time/equal-score ties use review ID then source row for deterministic provenance without changing the score. Python parses timestamps to microsecond precision; extra fractional digits in the source are truncated. Calendar-day comparisons are used for the timing audit, preserving the existing date convention.

Results:

- All 99,224 response timestamps parsed. Review creation timestamps also parsed, and no response preceded its recorded creation timestamp.
- No latest-response timestamp ties were found. One latest score could be selected for each of the 98,673 reviewed orders.
- No fully identical rows were found across the seven extracted, whitespace-trimmed stored review fields. Previously found repeated review IDs therefore do not justify dropping records solely by review ID. This is a stored-field duplicate check, not verification of original text or business-event uniqueness.
- Among 6,534 late orders, 6,381 have a selected latest review and 153 have none. None are unresolved under the timestamp rules.

| Latest response timing versus recorded delivery day, late orders only | Orders |
| --- | ---: |
| Before delivery day | 4,086 |
| On delivery day | 576 |
| After delivery day | 1,719 |
| Selected review total | 6,381 |

About 64% of selected reviews for late orders were recorded before the delivery day. Same-day responses are kept separate; the calendar-day audit does not establish whether they preceded delivery within that day. Example: Orders row 22 records delivery on 2017-10-09, but its latest response at Reviews row 34819 was recorded on 2017-10-01 (score 2). This may reflect the waiting experience, timestamp definitions or recording issues; it is not proof that a date is wrong.

Validation: timing groups sum to 6,381 selected late-order reviews; selected, unresolved and unreviewed categories sum to 6,534. Header, date, ID, source-fingerprint and prior KPI checks passed. No external evidence was added and no source records were corrected. The existing delay chart is unchanged.

Pending population decision before association analysis:

1. Include all latest reviews to study recorded opinions, including the waiting experience, with timing clearly reported. This retains more reviewed orders but is not a purely post-delivery satisfaction measure. Final delay length may not yet have been known when the opinion was submitted.
2. Restrict to latest reviews recorded after the delivery day to study later opinions. This changes the question and excludes many reviewed late orders. It can introduce selection bias; same-day responses require a finer timestamp audit before deciding whether they belong.

Recommendation for the original broad association question: start with all latest reviews, label them as recorded customer opinions rather than post-delivery satisfaction, then use timing groups for a later sensitivity check. Either approach must report review availability by delay range. No score-by-delay comparison has been calculated yet.

Manager-facing statement: "We can select one latest recorded review per order, but around 64% of reviewed late orders had that review recorded before delivery day. We need to decide whether we are studying the overall waiting experience or opinions recorded after delivery."

Reproduce using `python3 scripts/inspect_workbook.py`; see `latest_review_audit` in the JSON report. The stage records selection counts and examples, not a final joined analysis dataset.

Learner decision: include all latest reviews for the overall recorded experience, or restrict to reviews after delivery day for later opinions? Pause before association analysis.

Learner selected latest reviews recorded strictly after delivery day.

## Stage 9: compare later review scores across delay ranges

Business question: among late delivered orders whose latest recorded review response occurred after the delivery calendar day, how do review scores vary with delay length? This is narrower than all late orders or all customer experiences.

Implementation: select the latest response using the existing rule, retain it only when `review["answer"].date() > actual_delivery_date`, check that its score is an integer 1–5, and assign the order to its existing delay band. Same-day responses are excluded even if later by clock time. Each included order contributes exactly one score. The original workbook, delivery baseline and delay chart are preserved.

Eligibility: 1,719 of 6,534 late orders included (26.31%). Exclude 4,662 whose latest response was on/before delivery day and 153 with no review. There are no unresolved latest reviews or invalid scores among otherwise eligible orders in this file.

| Days late | Included orders | All late orders in band | Coverage | Mean score | Median score |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1–3 | 1,339 | 1,870 | 71.6% | 3.76 | 4 |
| 4–7 | 323 | 1,802 | 17.9% | 3.79 | 4 |
| 8–14 | 40 | 1,478 | 2.7% | 3.53 | 4 |
| 15–30 | 11 | 1,039 | 1.1% | 3.36 | 3 |
| 31+ | 6 | 345 | 1.7% | 2.00 | 1 |

Coverage denominator is all assessed late orders in the band. Score means/medians use only included orders. A missing or excluded opinion is not a zero score. Means treat differences between consecutive score categories as equally spaced; medians and the complete score counts are retained in the JSON report to avoid relying only on that assumption.

Interpretation: the longer-delay bands have lower descriptive mean scores than the first two groups, but the pattern is not strictly decreasing (4–7 days is slightly higher than 1–3). The longest groups are very small: six orders determine the 31+ day mean. Those six scores are four 1s, one 3 and one 5. A one-point change in one of six scores would shift that mean by about 0.17, illustrating its sensitivity. No population inference, significance test or confidence interval is claimed.

The coverage imbalance is substantial: the after-delivery-day rule retains 71.6% of the shortest-delay group and under 3% of every band above seven days. This is evidence of selection, not proof of its cause. We cannot assume excluded customers would give the same scores as included customers. The comparison does not establish a reliable monotonic relationship for all late orders or that delay caused dissatisfaction. Product experience, seller service, recorded event accuracy and who responds may also matter. The flagged extreme delivery cases remain included whenever eligible; their uncertain source accuracy is unresolved.

Validation: inclusion/exclusion counts sum to 6,534; band included counts sum to 1,719; unique included order IDs also total 1,719; each band's 1–5 score frequencies sum to its included order count. All existing ID, timestamp, delivery classification and source fingerprint checks passed. Results are in `post_delivery_score_comparison` in `reports/workbook_inventory.json`, reproduced by the existing inventory command.

Manager-facing statement: "Among the selected reviews recorded after delivery day, the longest-delay groups had lower average scores. However, only six orders qualify in the 31+ day group and review coverage differs sharply by delay length, so this is an exploratory signal, not a conclusion about all customers or proof that delay caused the scores."

Learner exercise: the 31+ day group has mean score 2.00, but only six of 345 orders qualify. Should we tell a manager that all customers with month-long delays give low ratings? Explain briefly. Pause here before further analysis.

Learner identified comments as useful evidence of a customer's stated problem and agreed to inspect the six qualifying reviews. A comment adds context but does not establish the sole cause of its score.

## Stage 10: inspect comments for the six long-delay cases

Business purpose: understand the stated experience behind scores before making an operational recommendation.

Implemented a reproducible extraction of the six selected latest review titles/messages, scores, source row numbers and relevant dates into `long_delay_comment_cases` in the existing JSON report. The extraction is performed only after applying the established latest-review, strictly-after-delivery-day and 31+ day rules. It uses the matched selected record, not an arbitrary review on the order. Comments were inspected manually; interpretations are documented separately in `reports/review_comment_audit.md`.

Findings: two comments explicitly describe slow delivery, including one that also reports a product-size/description issue. A separate comment claims nonreceipt despite an earlier recorded delivery. One criticizes service without explicitly naming delay, one praises speed despite a 42-day recorded delay, and one is blank. The six cases therefore do not establish delivery delay as the sole or main explanation of all low scores.

Data limitations: some Portuguese accented characters are garbled in the stored strings. English summaries are approximate paraphrases, and no original text was repaired. The nonreceipt response date is 2018-03-27, after its recorded delivery on 2018-03-11; that disagreement warrants verification, not an automatic correction. Positive speed feedback on a recorded late order also requires context. Missing text gives no reason for a score.

Validation: extracted case count is six; score frequencies match the existing 31+ day comparison (four 1s, one 3, one 5). Case membership remains one row per order. Existing eligibility, source fingerprint and KPI checks passed. Raw extracted strings remain in the JSON report; manual themes and summaries are a separate interpretation layer. Source files remain unchanged.

Workplace application: share a case list with the data owner and operations team when authorized, request supporting event records, and distinguish delivery, product and service topics. Do not force a single complaint category onto a multi-topic comment or interpret a blank as an absence of problems. No external messages were sent.

Learner exercise: a low-rating comment mentions both slow delivery and incorrect product dimensions. Can we confidently attribute its low score only to delivery delay? Pause here before further analysis.

Learner correctly identified that a multi-topic complaint does not establish delay as the sole reason for its rating, then requested a short findings draft.

## Stage 11: draft findings for a manager

Draft saved in `reports/findings_summary.md`. Its structure is baseline delivery performance, severity, customer-review evidence with sample sizes, limitations and an actionable verification step. It introduces no new calculations and preserves the existing population definitions.

Validation: figures were checked against the previously validated delivery baseline, severity bands, selected-review comparison and manual six-case comment audit. Association is distinguished from causation, review coverage accompanies score comparisons, and suspected data issues are not described as confirmed errors. Recommendations are proposed follow-up work, not actions already completed.

Communication lesson: lead with what happened and its scale; explain what the evidence supports; state limitations that affect a decision; propose a concrete next step. Avoid claiming the main cause of low ratings from a small selected group.

Learner exercise: which action should the manager take first based on this draft—verify the flagged records, or conclude that delays are the main cause of low ratings? Pause here before further work.

Learner chose to verify flagged records and requested a checklist before moving to robustness checks or final packaging.

## Stage 12: prepare a data-owner verification checklist

Draft: `reports/data_owner_verification_checklist.md`. It covers field definitions, the ten longest delays, two review/delivery disagreements, missing arrival dates, review-event timing and traceable outcomes. Case IDs and source-row references were checked against the existing JSON report. The checklist is not evidence that any source value is wrong.

Business purpose: turn analytical concerns into specific, answerable evidence requests. Approach: prioritize field meanings because a definition error can affect the whole analysis, then inspect identified cases. Use IDs rather than row numbers as stable lookup keys. Request event evidence without assuming a complaint, extreme value or date cluster proves an error.

Tradeoff: a targeted case list is manageable and actionable, but does not certify every record. Original source-system evidence may be unavailable; record unresolved limitations instead of inventing corrections. The draft includes an outcome template and rerun checks for supported changes. No external messages were sent, no data was corrected, and no Git commits or pushes were made.

Learner exercise: if the data owner cannot provide reliable proof for an extreme delivery date, should we delete the record or retain it with an unresolved flag? Pause before further work.

Learner chose to retain unresolved records with a flag and approved checking sensitivity to review timing.

## Stage 13: test sensitivity to review timing

Business purpose: determine whether our score comparison depends materially on a population choice. A manager should see this dependency before making a recommendation.

Implemented a separate `review_timing_sensitivity` output in the existing inspection script. The primary after-delivery-day comparison is preserved. The added comparison includes all selected latest reviews, including before-day and same-day responses, and breaks out all three timing groups. It uses the same 6,534 late orders, five delay bands, latest-score rule and score-validity checks. No extreme cases were removed.

Results and tradeoffs are documented in `reports/review_timing_sensitivity.md`; the findings summary was updated. Coverage rises from 1,719 to 6,381 orders, but the broader question includes the waiting experience. The 4–7 day mean changes from 3.79 to 2.10. Broader band means are 3.29, 2.10, 1.67, 1.61 and 2.06, so they are not consistently decreasing. Differences between timing groups are not within-customer changes or evidence of causation. Original event definitions, selection and source accuracy remain limitations.

Key code idea: `timing_scores[band][timing].append(score)` collects one score into its timing group; the same selected score also contributes to its band's all-latest summary. Broader means are calculated from individual scores, not by taking an unweighted average of timing-group means.

Validation: timing strata reconcile exactly to each band's full score frequencies; after-day frequencies match the unchanged primary population; unique included orders plus exclusions reconcile to 6,534; means were independently reconstructed from frequencies. Existing ID, date, source-preservation and delivery checks passed. Original files were not changed; nothing was committed or pushed.

Learner exercise: if the 4–7 day mean changes from 3.79 to 2.10 when earlier reviews are included, does that mean the same customers lowered their scores, or that we included a different group of orders? Pause before further work.

Learner identified the population change and requested project packaging.

## Stage 14: package the portfolio

Business purpose: let a manager or hiring reviewer quickly understand the question, evidence, methods and limitations, while another analyst can reproduce the outputs with the original source.

The prior README was preserved as this learning log. A new concise README is the entry point, linking to findings, charts, method definitions and the pending verification checklist. Existing important decisions are summarized there and detailed in `docs/data_dictionary.md`. The original workbook remains in place; a local archive omits it and documents the required source fingerprint and unavailable external provenance.

Implementation: `scripts/run_analysis.py` runs the existing analysis and both plot scripts in sequence. A second chart visualizes the already-computed timing sensitivity with explicit population counts; no new analysis or exclusions were introduced. `scripts/package_portfolio.py` uses an explicit asset list and SHA-256 manifest to build a ZIP, omitting Git metadata, source workbook, temporary owner file, caches and environment directories. `.gitignore` keeps those local-only files out of accidental staging. No commit, push or publication occurred.

Tradeoff: the archive is easy to review without the workbook, but rebuilding calculations requires the original local source. Automated outputs regenerate; human-authored findings and comment interpretations require review when the source changes. The local package is not proof that external source records are verified.

Validation: the complete runner was executed, baseline figures checked, figures visually reviewed, README links checked, and archive bytes checked against the file manifest. A clean extracted copy with the preserved source supplied was used to verify the documented run sequence. External data-owner verification remains pending.

Learner exercise: if a reviewer asks why the two review-score comparisons differ, explain the population difference in one sentence. Pause here before further work.

## GitHub publication decision

After reviewing the package and correctly explaining the review-population change, the learner authorized GitHub publication. The intended repository is private and named `ecommerce-delivery-customer-satisfaction`. The original workbook, Excel owner file, local ZIP, caches and environment directories remain excluded by `.gitignore`. External source verification is still pending; GitHub hosting does not resolve those analytical limitations.

## Reproduce the inventory

Requires Python 3, standard library only:

```sh
python3 scripts/inspect_workbook.py
```

The script reads the workbook XML without opening or saving it in Excel. It writes `reports/workbook_inventory.json` with sheet ranges, stored row counts, formula counts, first-row samples, table metadata and object inventory. It supports Strict and Transitional OOXML namespaces. Samples contain stored values, not recalculated or formatted Excel results.

Validation performed: checked table ranges against worksheet extents and counted rows with stored cells. SHA-256 is checked before and after inspection to detect source changes. This establishes an inventory, not complete data quality or formula correctness. If Excel is open, save changes and rerun for a consistent snapshot.

Important code: `ZipFile` reads the XLSX archive; `ET.iterparse` walks worksheet rows; `element.clear()` releases parsed row contents; `hashlib.sha256` checks that the source stayed unchanged. Future stages will add identifier checks and documented business decisions before any aggregation.
