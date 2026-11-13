#!/usr/bin/env python3
"""First-draft chart: Q1 2025 vs Q1 2026 coffee sales by drink."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: write a PNG, no window
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "coffee_sales_q1.csv"
OUT = ROOT / "charts" / "chart_v1.png"

df = pd.read_csv(DATA)
totals = df.pivot_table(index="drink", columns="quarter", values="units_sold", aggfunc="sum")
assert list(totals.columns) == ["Q1 2025", "Q1 2026"], totals.columns

ax = totals.plot(kind="bar", figsize=(8, 5))
ax.set_title("Coffee Sales Q1 2025 vs Q1 2026")
ax.set_xlabel("Drink")
ax.set_ylabel("Units sold")

OUT.parent.mkdir(exist_ok=True)
plt.savefig(OUT)
print(f"wrote {OUT}")
