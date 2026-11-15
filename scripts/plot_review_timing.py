"""Export the existing review-timing comparison without changing analysis populations."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from decimal import Decimal, ROUND_HALF_UP

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "ecommerce-matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    report = json.loads((ROOT / "reports/workbook_inventory.json").read_text())
    if hashlib.sha256((ROOT / report["source"]).read_bytes()).hexdigest() != report["sha256"]:
        raise ValueError("Source changed; rerun the inventory before plotting.")
    bands = report["review_timing_sensitivity"]["bands"]
    labels = [b["delay_band"] for b in bands]
    groups = [("after_delivery_day", "After delivery day", "#267893", "o", -0.09),
              ("all_latest_reviews", "All latest reviews", "#b35725", "D", 0.09)]
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.subplots_adjust(left=0.12, right=0.96, top=0.77, bottom=0.40)
    fig.text(0.12, 0.93, "Review timing changes the comparison", fontsize=20, weight="bold")
    fig.text(0.12, 0.875, "Mean score among late orders with a selected latest review", fontsize=12)
    fig.text(0.12, 0.835, "All latest reviews includes the after-delivery group; these are overlapping populations.",
             fontsize=10, color="#4b5563")
    counts = []
    for key, label, color, marker, offset in groups:
        summaries = [b["review_timing_groups"][key] for b in bands]
        scores = [s["mean_score"] for s in summaries]
        if any(s["orders"] <= 0 for s in summaries):
            raise ValueError("This chart requires at least one reviewed order in every displayed group.")
        ax.scatter([i + offset for i in range(len(bands))], scores, color=color, marker=marker,
                   label=label, s=65, zorder=3)
        for i, value in enumerate(scores):
            label_value = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ax.annotate(str(label_value), (i + offset, value), xytext=(0, 11 if offset < 0 else -19),
                        textcoords="offset points", ha="center", color=color, fontsize=10)
        counts.append([f'{s["orders"]:,}' for s in summaries])
    ax.set_xticks(range(len(bands)), labels)
    ax.set_xlim(-0.5, len(bands) - 0.5)
    ax.set_ylim(0.8, 5.3)
    ax.set_yticks(range(1, 6))
    ax.set_ylabel("Mean recorded score (1–5)")
    ax.set_xlabel("Calendar days late", labelpad=10)
    ax.grid(axis="y", color="#e5e7eb")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper right", frameon=False, fontsize=10)
    fig.text(0.12, 0.285, "Included orders in each plotted group", fontsize=11, weight="bold")
    table_ax = fig.add_axes([0.12, 0.13, 0.84, 0.13])
    table_ax.axis("off")
    # Put row labels inside the table so they cannot extend beyond the image.
    rows = [[groups[i][1], *counts[i]] for i in range(2)]
    table = table_ax.table(cellText=rows, colLabels=["Review population", *labels],
                           colWidths=[0.28, *([0.144] * 5)], cellLoc="center", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#d1d5db")
        if row == 0:
            cell.set_facecolor("#f3f4f6")
    fig.text(0.12, 0.07, "Descriptive means, not causal effects. Small groups and review selection limit interpretation.",
             fontsize=10, color="#4b5563")
    fig.text(0.12, 0.035, "Source: saved Orders and Reviews tables. Extreme cases retained; event definitions remain unverified.",
             fontsize=9, color="#4b5563")
    destination = ROOT / "reports/figures"
    destination.mkdir(exist_ok=True)
    for extension in ("png", "svg"):
        path = destination / f"review_timing_comparison.{extension}"
        fig.savefig(path, dpi=180, facecolor="white")
        print(path.relative_to(ROOT))
    plt.close(fig)


if __name__ == "__main__":
    main()
