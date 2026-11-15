"""Rebuild analysis and charts in a fixed sequence from the preserved workbook."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "Ecommerce_Delivery_Analysis.xlsx").is_file():
    raise SystemExit("Place the original Ecommerce_Delivery_Analysis.xlsx in the project root, then rerun.")

for name in ("inspect_workbook.py", "plot_delay_distribution.py", "plot_review_timing.py"):
    print(f"Running {name}", flush=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / name)], check=True, stdout=subprocess.DEVNULL)
print("Completed: reports/workbook_inventory.json and both PNG/SVG charts. Narrative reports are manually maintained.")
