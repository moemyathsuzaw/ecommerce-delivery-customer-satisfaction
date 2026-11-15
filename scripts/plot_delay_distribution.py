"""Plot the validated delay bands; never edit the source workbook."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "ecommerce-matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

ROOT = Path(__file__).resolve().parents[1]


def main():
    report = json.loads((ROOT / "reports/workbook_inventory.json").read_text())
    source = ROOT / report["source"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != report["sha256"]:
        raise ValueError("Source changed. Run scripts/inspect_workbook.py before plotting.")
    severity = report["delay_severity"]
    bands = severity["delay_bands"]
    total = severity["late_orders"]
    counts = [band["orders"] for band in bands]
    if total <= 0 or sum(counts) != total:
        raise ValueError("Delay bands must reconcile to a positive late-order count.")
    for band in bands:
        if abs(band["share_of_late_orders"] - band["orders"] / total) > 1e-12:
            raise ValueError("Band percentage does not reconcile to its count.")

    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False}):
        fig, ax = plt.subplots(figsize=(10, 6.2))
        fig.subplots_adjust(left=0.12, right=0.97, top=0.76, bottom=0.24)
        fig.text(0.12, 0.92, "How late did delayed orders arrive?", fontsize=20, weight="bold")
        fig.text(0.12, 0.86, f"{total:,} late delivered orders with usable dates · Calendar days after the promise",
                 fontsize=11, color="#4b5563")
        bars = ax.bar([b["band"] for b in bands], counts, color="#267893", width=0.65)
        ax.set_ylabel("Number of late orders")
        ax.set_xlabel("Recorded delay range", labelpad=12)
        ax.set_ylim(0, 2300)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#e5e7eb")
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color("#9ca3af")
        for bar, band in zip(bars, bands):
            ax.annotate(f'{band["orders"]:,}\n{band["share_of_late_orders"]:.1%}',
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 7), textcoords="offset points", ha="center", va="bottom")
        fig.text(0.12, 0.105, "Percentages use late orders only. All extreme cases remain included (maximum: "
                 f'{severity["max_days_late"]} days).', fontsize=10, color="#4b5563")
        fig.text(0.12, 0.065, "Source: saved Orders table. Ranges have unequal widths; bars show category counts, not density.",
                 fontsize=9, color="#4b5563")
        destination = ROOT / "reports/figures"
        destination.mkdir(exist_ok=True)
        for extension in ("png", "svg"):
            path = destination / f"delay_distribution.{extension}"
            fig.savefig(path, dpi=180, facecolor="white")
            print(path.relative_to(ROOT))
        plt.close(fig)


if __name__ == "__main__":
    main()
