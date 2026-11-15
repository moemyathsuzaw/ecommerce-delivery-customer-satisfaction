"""Read workbook structure without changing Excel files. Python standard library only."""
import hashlib
import json
import posixpath
from collections import Counter, defaultdict
from datetime import datetime
from math import ceil
from statistics import mean, median
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Ecommerce_Delivery_Analysis.xlsx"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def calendar_date(value):
    """Parse the source's ISO date/timestamp; ignore time for promised-day comparison."""
    return datetime.fromisoformat(value.strip()).date()


def inspect():
    fingerprint = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    with ZipFile(SOURCE) as archive:
        names = archive.namelist()
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        NS["s"] = workbook.tag.split("}")[0].lstrip("{")
        strings = []
        if "xl/sharedStrings.xml" in names:
            for _, element in ET.iterparse(archive.open("xl/sharedStrings.xml")):
                if element.tag == "{" + NS["s"] + "}si":
                    strings.append("".join(element.itertext()))
                    element.clear()
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.attrib["Id"]: r.attrib["Target"] for r in relationships}
        sheets = []
        order_ids = Counter()
        status_counts = Counter()
        delivered_date_coverage = Counter()
        missing_order_ids = 0
        order_rows = 0
        delivery_results = Counter()
        formula_comparisons = Counter()
        chronology_checks = Counter()
        late_day_total = 0
        late_delays = []
        late_records = []
        review_rows = []
        review_records = []
        for sheet in workbook.find("s:sheets", NS):
            relationship_id = next(v for k, v in sheet.attrib.items() if k.endswith("}id"))
            target = targets[relationship_id]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            rows, formulas, preview = 0, 0, []
            dimension = None
            with archive.open(target) as stream:
                for _, element in ET.iterparse(stream):
                    if element.tag == "{" + NS["s"] + "}dimension":
                        dimension = element.attrib.get("ref")
                    if element.tag != "{" + NS["s"] + "}row":
                        continue
                    cells = element.findall("s:c", NS)
                    if cells:
                        rows += 1
                        values = {}
                        row_values = {}
                        for cell in cells:
                            formula = cell.find("s:f", NS)
                            formulas += formula is not None
                            value = cell.findtext("s:v", default="", namespaces=NS)
                            if cell.attrib.get("t") == "s" and value:
                                value = strings[int(value)]
                            elif cell.attrib.get("t") == "inlineStr":
                                value = "".join(cell.find("s:is", NS).itertext())
                            column = "".join(c for c in cell.attrib["r"] if c.isalpha())
                            row_values[column] = value
                            if len(preview) < 3:
                                values[cell.attrib["r"]] = {"value": value, "stored_type": cell.attrib.get("t", "n"), "formula": formula.text if formula is not None else None}
                        if len(preview) < 3:
                            preview.append(values)
                        if sheet.attrib["name"] == "Orders":
                            if element.attrib["r"] == "1":
                                expected = {"A": "order_id", "B": "customer_id", "C": "order_status",
                                            "E": "order_approved_at", "F": "order_delivered_carrier_date",
                                            "D": "order_purchase_timestamp", "I": "Delivery Status",
                                            "G": "order_delivered_customer_date",
                                            "H": "order_estimated_delivery_date"}
                                if any(row_values.get(k) != v for k, v in expected.items()):
                                    raise ValueError("Orders layout changed; review column mapping before profiling.")
                            elif any(row_values.get(c, "").strip() for c in "ABCDEFGH"):
                                order_rows += 1
                                order_id = row_values.get("A", "").strip()
                                if order_id:
                                    order_ids[order_id] += 1
                                else:
                                    missing_order_ids += 1
                                status = row_values.get("C", "").strip() or "(missing)"
                                status_counts[status] += 1
                                if status == "delivered":
                                    actual = bool(row_values.get("G", "").strip())
                                    estimated = bool(row_values.get("H", "").strip())
                                    coverage = ("both_present" if actual and estimated else
                                                "actual_missing" if estimated else
                                                "estimated_missing" if actual else "both_missing")
                                    delivered_date_coverage[coverage] += 1
                                    if not (actual and estimated):
                                        delivery_results["unknown_missing_dates"] += 1
                                    else:
                                        try:
                                            actual_day = calendar_date(row_values["G"])
                                            promised_day = calendar_date(row_values["H"])
                                        except ValueError:
                                            delivery_results["unknown_invalid_dates"] += 1
                                        else:
                                            days_late = max(0, (actual_day - promised_day).days)
                                            label = "Late" if days_late > 0 else "On time"
                                            delivery_results[label] += 1
                                            late_day_total += days_late
                                            if days_late > 0:
                                                late_delays.append(days_late)
                                                late_records.append({"excel_row": int(element.attrib["r"]),
                                                                     "order_id": order_id, "days_late": days_late,
                                                                     "purchase": row_values.get("D", ""),
                                                                     "approved": row_values.get("E", ""),
                                                                     "carrier_handoff": row_values.get("F", ""),
                                                                     "actual_delivery": row_values["G"],
                                                                     "estimated_delivery": row_values["H"]})
                                            saved_label = row_values.get("I", "").strip()
                                            formula_comparisons["match" if saved_label == label else "mismatch"] += 1
                                            try:
                                                purchase_day = calendar_date(row_values.get("D", ""))
                                            except ValueError:
                                                chronology_checks["purchase_date_unavailable_or_invalid"] += 1
                                            else:
                                                chronology_checks["actual_before_purchase" if actual_day < purchase_day
                                                                  else "actual_on_or_after_purchase"] += 1
                                                chronology_checks["promised_before_purchase" if promised_day < purchase_day
                                                                  else "promised_on_or_after_purchase"] += 1
                        elif sheet.attrib["name"] == "Reviews":
                            if element.attrib["r"] == "1":
                                expected = {"A": "review_id", "B": "order_id", "C": "review_score",
                                            "D": "review_comment_title", "E": "review_comment_message",
                                            "F": "review_creation_date", "G": "review_answer_timestamp"}
                                if any(row_values.get(k) != v for k, v in expected.items()):
                                    raise ValueError("Reviews layout changed; review mapping before profiling.")
                            elif any(row_values.get(c, "").strip() for c in "ABCDEFG"):
                                review_rows.append(tuple(row_values.get(c, "").strip() for c in "ABC"))
                                review_records.append({"excel_row": int(element.attrib["r"]),
                                                       "values": tuple(row_values.get(c, "").strip() for c in "ABCDEFG")})
                    element.clear()
            sheets.append({"name": sheet.attrib["name"], "dimension": dimension,
                           "rows_with_cells": rows, "formula_cells": formulas, "first_rows": preview})
        objects = {kind: [n for n in names if n.startswith(prefix) and n.endswith(".xml")]
                   for kind, prefix in {"tables": "xl/tables/table", "charts": "xl/charts/chart",
                                        "pivot_tables": "xl/pivotTables/pivotTable"}.items()}
        table_details = []
        for path in objects["tables"]:
            table = ET.fromstring(archive.read(path))
            filters = table.find("s:autoFilter", NS)
            table_details.append({"name": table.attrib["name"], "range": table.attrib["ref"],
                                  "filter_xml": ET.tostring(filters, encoding="unicode") if filters is not None else None})
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != fingerprint:
        raise RuntimeError("Source changed during inspection. Close Excel and rerun.")
    duplicate_excess = sum(count - 1 for count in order_ids.values())
    if sum(status_counts.values()) != order_rows:
        raise ValueError("Order status counts do not reconcile.")
    if sum(delivered_date_coverage.values()) != status_counts["delivered"]:
        raise ValueError("Delivered date coverage does not reconcile.")
    if len(order_ids) + duplicate_excess + missing_order_ids != order_rows:
        raise ValueError("Order identifier counts do not reconcile.")
    if sum(delivery_results.values()) != status_counts["delivered"]:
        raise ValueError("Delivery classifications do not reconcile to delivered orders.")
    assessed = delivery_results["Late"] + delivery_results["On time"]
    if sum(formula_comparisons.values()) != assessed:
        raise ValueError("Formula comparison counts do not reconcile to assessed orders.")
    if duplicate_excess or missing_order_ids:
        raise ValueError("Resolve missing/repeated order IDs before calculating an order-level KPI.")
    if (chronology_checks["actual_before_purchase"] or chronology_checks["promised_before_purchase"]
            or chronology_checks["purchase_date_unavailable_or_invalid"]):
        raise ValueError("Investigate chronology issues before publishing this KPI.")
    delivery_kpi = {"population": "Orders with status delivered and parseable actual and estimated dates",
                    "late_definition": "Actual calendar date is after estimated calendar date; same day is on time",
                    "counts": dict(sorted(delivery_results.items())), "assessed_delivered_orders": assessed,
                    "late_rate": delivery_results["Late"] / assessed if assessed else None,
                    "assessment_coverage": assessed / status_counts["delivered"] if status_counts["delivered"] else None,
                    "calendar_days_late_total": late_day_total,
                    "saved_delivery_status_comparison": dict(formula_comparisons),
                    "chronology_checks": dict(chronology_checks),
                    "limitations": ["Descriptive rate for this saved dataset, not proof of causes or current performance.",
                                    "Saved Excel labels were compared, not recalculated in Excel.",
                                    "Dates use the source calendar with no timezone conversion."]}
    # Severity uses late orders only. Including on-time zeroes answers a different question.
    late_delays.sort()
    bands = [("1–3 days", 1, 3), ("4–7 days", 4, 7), ("8–14 days", 8, 14),
             ("15–30 days", 15, 30), ("31+ days", 31, None)]
    delay_bands = [{"band": label,
                    "orders": sum(low <= days and (high is None or days <= high) for days in late_delays)}
                   for label, low, high in bands]
    if len(late_delays) != delivery_results["Late"] or sum(late_delays) != late_day_total:
        raise ValueError("Delay severity does not reconcile to the late-order KPI.")
    if sum(band["orders"] for band in delay_bands) != len(late_delays):
        raise ValueError("Delay bands do not reconcile to late orders.")
    for band in delay_bands:
        band["share_of_late_orders"] = band["orders"] / len(late_delays) if late_delays else None
    severity = {"population": "Assessed delivered orders with strictly positive calendar days late",
                "late_orders": len(late_delays),
                "mean_days_late": mean(late_delays) if late_delays else None,
                "median_days_late": median(late_delays) if late_delays else None,
                "p90_days_late": late_delays[ceil(0.90 * len(late_delays)) - 1] if late_delays else None,
                "p90_method": "Nearest rank: sorted value at ceiling(0.90 * n), using one-based positions",
                "min_days_late": min(late_delays) if late_delays else None,
                "max_days_late": max(late_delays) if late_delays else None,
                "delay_bands": delay_bands,
                "band_note": "Exploratory calendar-day bands, not agreed company service thresholds",
                "limitations": ["Extreme delays retained; valid date parsing does not verify business accuracy.",
                                "Severity describes late orders only, excluding on-time and unknown orders."]}
    longest_delays = sorted(late_records, key=lambda r: (-r["days_late"], r["order_id"]))[:10]
    for record in longest_delays:
        dates = {}
        flags = []
        for field in ("purchase", "approved", "carrier_handoff", "actual_delivery", "estimated_delivery"):
            try:
                dates[field] = calendar_date(record[field])
            except ValueError:
                flags.append(f"missing_or_invalid_{field}")
        for earlier, later in (("purchase", "approved"), ("approved", "carrier_handoff"),
                               ("carrier_handoff", "actual_delivery")):
            if earlier in dates and later in dates and dates[later] < dates[earlier]:
                flags.append(f"{later}_before_{earlier}")
        for label, earlier, later in (("purchase_to_handoff_days", "purchase", "carrier_handoff"),
                                      ("handoff_to_delivery_days", "carrier_handoff", "actual_delivery"),
                                      ("purchase_to_promised_days", "purchase", "estimated_delivery")):
            record[label] = (dates[later] - dates[earlier]).days if earlier in dates and later in dates else None
        record["calendar_date_flags"] = flags
        if "carrier_handoff" in dates:
            total = (dates["actual_delivery"] - dates["purchase"]).days
            if record["purchase_to_handoff_days"] + record["handoff_to_delivery_days"] != total:
                raise ValueError("Timeline intervals do not reconcile.")
        if (dates["actual_delivery"] - dates["estimated_delivery"]).days != record["days_late"]:
            raise ValueError("Outlier lateness does not reconcile.")
    order_profile = {"data_rows": order_rows, "distinct_nonblank_order_ids": len(order_ids),
                     "missing_order_ids": missing_order_ids,
                     "order_ids_appearing_more_than_once": sum(n > 1 for n in order_ids.values()),
                     "duplicate_excess_rows": duplicate_excess,
                     "status_counts": dict(sorted(status_counts.items())),
                     "delivered_date_coverage": dict(sorted(delivered_date_coverage.items())),
                     "limitations": ["Date presence only; validity and chronological consistency not yet checked.",
                                     "Order IDs and statuses are whitespace-trimmed for profiling only.",
                                     "All stored rows are read, including rows hidden by Excel filters."]}
    review_ids = Counter(r[0] for r in review_rows if r[0])
    reviews_per_order = Counter(r[1] for r in review_rows if r[1])
    scores_per_order = {}
    for _, order_id, score in review_rows:
        if order_id:
            scores_per_order.setdefault(order_id, set()).add(score)
    late_ids = {r["order_id"] for r in late_records}
    late_coverage = Counter(min(reviews_per_order[oid], 2) for oid in late_ids)
    review_profile = {
        "review_rows": len(review_rows), "distinct_nonblank_review_ids": len(review_ids),
        "missing_review_ids": sum(not r[0] for r in review_rows),
        "repeated_review_ids": sum(n > 1 for n in review_ids.values()),
        "distinct_nonblank_order_ids_in_reviews": len(reviews_per_order),
        "missing_order_ids": sum(not r[1] for r in review_rows),
        "review_rows_with_unmatched_nonblank_order_id": sum(bool(r[1]) and r[1] not in order_ids for r in review_rows),
        "orders_with_multiple_review_rows": sum(n > 1 for n in reviews_per_order.values()),
        "orders_with_multiple_distinct_score_values": sum(len(s) > 1 for s in scores_per_order.values()),
        "maximum_review_rows_per_order": max(reviews_per_order.values(), default=0),
        "score_value_counts": dict(sorted(Counter(r[2] or "(missing)" for r in review_rows).items())),
        "late_order_review_coverage": {"no_review": late_coverage[0], "one_review": late_coverage[1],
                                       "multiple_reviews": late_coverage[2]},
        "late_order_rows_after_unaggregated_left_join": sum(max(1, reviews_per_order[oid]) for oid in late_ids),
        "limitations": ["No review deduplication or order-level score rule has been selected.",
                        "Review dates relative to delivery have not yet been validated.",
                        "Repeated review IDs are not necessarily identical records."]}
    if sum(late_coverage.values()) != len(late_delays):
        raise ValueError("Late-order review coverage does not reconcile.")
    if sum(reviews_per_order.values()) + review_profile["missing_order_ids"] != len(review_rows):
        raise ValueError("Review order-key counts do not reconcile.")
    # Score timestamps use the answer field, not the review-creation/invitation field.
    # This is a working interpretation of field labels, pending source documentation.
    review_groups = defaultdict(list)
    timestamp_quality = Counter()
    for record in review_records:
        values = record["values"]
        try:
            answer = datetime.fromisoformat(values[6])
        except ValueError:
            answer = None
            timestamp_quality["missing_or_invalid_answer_timestamp"] += 1
        else:
            timestamp_quality["valid_answer_timestamp"] += 1
        try:
            creation = datetime.fromisoformat(values[5])
        except ValueError:
            timestamp_quality["missing_or_invalid_creation_timestamp"] += 1
        else:
            if answer is not None and answer < creation:
                timestamp_quality["answer_before_creation"] += 1
        review_groups[values[1]].append({**record, "answer": answer})
    selected_reviews = {}
    selection_audit = Counter()
    for order_id, records in review_groups.items():
        if any(r["answer"] is None for r in records):
            selection_audit["unresolved_order_invalid_timestamp"] += 1
            continue
        latest_time = max(r["answer"] for r in records)
        latest = [r for r in records if r["answer"] == latest_time]
        if len(latest) > 1:
            selection_audit["orders_with_latest_timestamp_tie"] += 1
        if len({r["values"][2] for r in latest}) > 1:
            selection_audit["unresolved_order_conflicting_latest_scores"] += 1
            continue
        # For equal-time/equal-score records this selects reproducible provenance only.
        chosen = min(latest, key=lambda r: (r["values"][0], r["excel_row"]))
        selected_reviews[order_id] = chosen
        selection_audit["orders_with_selected_score"] += 1
    late_selection = Counter()
    pre_delivery_examples = []
    for order in late_records:
        order_id = order["order_id"]
        selected = selected_reviews.get(order_id)
        if order_id not in review_groups:
            late_selection["no_review"] += 1
        elif selected is None:
            late_selection["unresolved_latest_review"] += 1
        else:
            late_selection["selected_latest_review"] += 1
            difference = (selected["answer"].date() - calendar_date(order["actual_delivery"])).days
            timing = "before_delivery_day" if difference < 0 else "on_delivery_day" if difference == 0 else "after_delivery_day"
            late_selection[timing] += 1
            if difference < 0 and len(pre_delivery_examples) < 3:
                pre_delivery_examples.append({"order_id": order_id, "orders_excel_row": order["excel_row"],
                                              "reviews_excel_row": selected["excel_row"],
                                              "answer_timestamp": selected["values"][6],
                                              "actual_delivery": order["actual_delivery"],
                                              "score": selected["values"][2]})
    if sum(late_selection[k] for k in ("no_review", "unresolved_latest_review", "selected_latest_review")) != len(late_records):
        raise ValueError("Latest-review coverage does not reconcile to late orders.")
    if sum(late_selection[k] for k in ("before_delivery_day", "on_delivery_day", "after_delivery_day")) != late_selection["selected_latest_review"]:
        raise ValueError("Selected review timing does not reconcile.")
    latest_review_audit = {
        "working_timestamp": "review_answer_timestamp (column G), interpreted as the recorded review response time",
        "timestamp_precision": "Python datetime microseconds; source fractional digits beyond microseconds are truncated",
        "exact_duplicate_excess_rows_all_seven_stored_fields": sum(n - 1 for n in Counter(r["values"] for r in review_records).values()),
        "timestamp_quality": dict(timestamp_quality), "order_selection": dict(selection_audit),
        "late_order_selection_and_timing": dict(late_selection),
        "pre_delivery_examples": pre_delivery_examples,
        "rules": ["If any answer timestamp is invalid/missing, leave that order unresolved.",
                  "Latest timestamp ties with conflicting scores remain unresolved.",
                  "Equal-time/equal-score ties use review ID then source row for provenance only.",
                  "Timing groups compare calendar days; same-day timing is not treated as proven post-delivery.",
                  "No review timing exclusions applied and no association estimate calculated yet."]}
    # Learner-selected population: late orders whose latest response is after delivery day.
    score_groups = {label: [] for label, _, _ in bands}
    eligibility = Counter()
    eligible_order_ids = set()
    long_delay_comments = []
    for order in late_records:
        review = selected_reviews.get(order["order_id"])
        if review is None:
            eligibility["no_review_or_unresolved"] += 1
            continue
        if review["answer"].date() <= calendar_date(order["actual_delivery"]):
            eligibility["latest_response_on_or_before_delivery_day"] += 1
            continue
        try:
            score = int(review["values"][2])
        except ValueError:
            eligibility["invalid_score"] += 1
            continue
        if not 1 <= score <= 5:
            eligibility["invalid_score"] += 1
            continue
        eligibility["included"] += 1
        eligible_order_ids.add(order["order_id"])
        if order["days_late"] >= 31:
            long_delay_comments.append({"order_id": order["order_id"],
                                        "review_id": review["values"][0],
                                        "orders_excel_row": order["excel_row"],
                                        "reviews_excel_row": review["excel_row"],
                                        "days_late": order["days_late"], "score": score,
                                        "actual_delivery": order["actual_delivery"],
                                        "answer_timestamp": review["values"][6],
                                        "title_stored": review["values"][3],
                                        "comment_stored": review["values"][4]})
        for label, low, high in bands:
            if low <= order["days_late"] and (high is None or order["days_late"] <= high):
                score_groups[label].append(score)
                break
    score_comparison = []
    for band in delay_bands:
        scores = score_groups[band["band"]]
        score_comparison.append({"delay_band": band["band"], "all_late_orders": band["orders"],
                                 "eligible_reviewed_orders": len(scores),
                                 "eligible_share_of_band": len(scores) / band["orders"] if band["orders"] else None,
                                 "mean_score": mean(scores) if scores else None,
                                 "median_score": median(scores) if scores else None,
                                 "score_counts": {str(s): scores.count(s) for s in range(1, 6)}})
    included = eligibility["included"]
    if sum(eligibility.values()) != len(late_records):
        raise ValueError("Score-analysis inclusion/exclusion counts do not reconcile.")
    if sum(len(scores) for scores in score_groups.values()) != included or len(eligible_order_ids) != included:
        raise ValueError("Score groups do not reconcile to unique included orders.")
    for group in score_comparison:
        if sum(group["score_counts"].values()) != group["eligible_reviewed_orders"]:
            raise ValueError("Score frequencies do not reconcile.")
    if len(long_delay_comments) != len(score_groups["31+ days"]):
        raise ValueError("Comment case list does not reconcile to the selected 31+ day group.")
    if Counter(r["score"] for r in long_delay_comments) != Counter(score_groups["31+ days"]):
        raise ValueError("Comment case scores do not reconcile to the selected group's scores.")
    post_delivery_comparison = {
        "population": "Late delivered orders with a valid latest score recorded strictly after actual delivery calendar day",
        "eligibility_counts": dict(eligibility), "bands": score_comparison,
        "limitations": ["Excludes same-day and pre-delivery reviews, unknown dates and non-late orders.",
                        "Eligibility may differ with delay length; these groups may be selectively reviewed.",
                        "Mean scores treat the steps between integer ratings as equally spaced.",
                        "Association is descriptive, unadjusted and does not establish causation."]}
    # Sensitivity only: retain the chosen after-delivery-day analysis above unchanged.
    timing_scores = {label: defaultdict(list) for label, _, _ in bands}
    sensitivity_ids = set()
    sensitivity_exclusions = Counter()
    for order in late_records:
        review = selected_reviews.get(order["order_id"])
        if review is None:
            sensitivity_exclusions["no_review_or_unresolved"] += 1
            continue
        try:
            score = int(review["values"][2])
        except ValueError:
            sensitivity_exclusions["invalid_score"] += 1
            continue
        if not 1 <= score <= 5:
            sensitivity_exclusions["invalid_score"] += 1
            continue
        lag = (review["answer"].date() - calendar_date(order["actual_delivery"])).days
        timing = "before_delivery_day" if lag < 0 else "on_delivery_day" if lag == 0 else "after_delivery_day"
        for label, low, high in bands:
            if low <= order["days_late"] and (high is None or order["days_late"] <= high):
                timing_scores[label][timing].append(score)
                timing_scores[label]["all_latest_reviews"].append(score)
                sensitivity_ids.add(order["order_id"])
                break
    sensitivity_bands = []
    timing_names = ("before_delivery_day", "on_delivery_day", "after_delivery_day")
    for band, primary in zip(delay_bands, score_comparison):
        groups = timing_scores[band["band"]]
        all_scores = groups["all_latest_reviews"]
        if Counter(all_scores) != Counter(s for name in timing_names for s in groups[name]):
            raise ValueError("Review timing strata do not reconcile to all latest scores.")
        if Counter(groups["after_delivery_day"]) != Counter(score_groups[band["band"]]):
            raise ValueError("Sensitivity changed the primary after-delivery population.")
        summaries = {}
        for name in (*timing_names, "all_latest_reviews"):
            values = groups[name]
            summaries[name] = {"orders": len(values), "coverage_of_all_late_orders_in_band":
                                len(values) / band["orders"] if band["orders"] else None,
                                "mean_score": mean(values) if values else None,
                                "median_score": median(values) if values else None,
                                "score_counts": {str(s): values.count(s) for s in range(1, 6)}}
        sensitivity_bands.append({"delay_band": band["band"], "all_late_orders": band["orders"],
                                  "review_timing_groups": summaries})
    sensitivity_included = sum(b["review_timing_groups"]["all_latest_reviews"]["orders"] for b in sensitivity_bands)
    if sensitivity_included != len(sensitivity_ids) or sensitivity_included + sum(sensitivity_exclusions.values()) != len(late_records):
        raise ValueError("Sensitivity inclusion counts do not reconcile to unique late orders.")
    timing_sensitivity = {"status": "Sensitivity comparison; primary analysis remains strictly after delivery day",
                          "included_all_latest_orders": sensitivity_included,
                          "exclusions": dict(sensitivity_exclusions), "bands": sensitivity_bands,
                          "limitations": ["Broader timing includes waiting-period opinions, not purely post-delivery experiences.",
                                          "Final recorded delay may not yet have been known when an earlier review was submitted.",
                                          "Higher review coverage does not establish representativeness or causality.",
                                          "No source verification or extreme-case exclusion was performed."]}
    return {"source": SOURCE.name, "sha256": fingerprint, "sheets": sheets, "objects": objects,
            "order_profile": order_profile,
            "delivery_kpi": delivery_kpi,
            "delay_severity": severity,
            "review_linkage_profile": review_profile,
            "latest_review_audit": latest_review_audit,
            "post_delivery_score_comparison": post_delivery_comparison,
            "review_timing_sensitivity": timing_sensitivity,
            "long_delay_comment_cases": sorted(long_delay_comments, key=lambda r: (-r["days_late"], r["order_id"])),
            "longest_delay_review": {"selection": "Top 10 assessed late orders by days late; ties ordered by order ID",
                                     "records": longest_delays,
                                     "recorded_delivery_date_counts": dict(sorted(Counter(
                                         calendar_date(r["actual_delivery"]).isoformat() for r in longest_delays).items())),
                                     "limitations": ["Calendar-date checks only; no within-day chronology validation.",
                                                     "Selection prioritizes extremes and is not representative of all late orders.",
                                                     "Intervals reflect recorded timestamps, not verified operational responsibility."]},
            "tables": table_details,
            "notes": ["Rows with cells may include formatting-only rows.",
                      "First rows show stored values, not recalculated results.",
                      "Excel numeric dates require interpretation using cell formats."]}


if __name__ == "__main__":
    report = inspect()
    destination = ROOT / "reports" / "workbook_inventory.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
