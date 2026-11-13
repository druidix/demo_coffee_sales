#!/usr/bin/env python3
"""Chart v2: Q1 2025 vs Q1 2026 coffee sales by drink, revised per critiques/critique_v1.md."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: write a PNG, no window
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import StrMethodFormatter

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "coffee_sales_q1.csv"
OUT = ROOT / "charts" / "chart_v2.png"

df = pd.read_csv(DATA)
totals = df.pivot_table(index="drink", columns="quarter", values="units_sold", aggfunc="sum")
assert list(totals.columns) == ["Q1 2025", "Q1 2026"], totals.columns
totals = totals.sort_values("Q1 2026", ascending=False)  # issue 2: order carries meaning
pct = (totals["Q1 2026"] / totals["Q1 2025"] - 1) * 100
overall = (totals["Q1 2026"].sum() / totals["Q1 2025"].sum() - 1) * 100

# issue 3: takeaway title, only claimed when the data supports it
if (pct > 0).all():
    headline = "Every drink sold more in Q1 2026 than in Q1 2025"
else:
    headline = "Coffee units sold by drink, Q1 2025 vs Q1 2026"

fig, ax = plt.subplots(figsize=(9, 5.5))
# issue 6: grey baseline, strong color for the current period
totals.plot(kind="bar", ax=ax, color=["#b0b0b0", "#1f77b4"], width=0.75, edgecolor="white")

# issue 2: quantify the change above each pair
for i, (drink, p) in enumerate(pct.items()):
    ax.annotate(f"{p:+.1f}%", xy=(i, totals.loc[drink].max()), xytext=(0, 6),
                textcoords="offset points", ha="center", fontsize=10, fontweight="bold")

fig.suptitle(headline, x=0.08, ha="left", fontsize=14, fontweight="bold")
ax.set_title(f"Units sold per quarter; all drinks combined {overall:+.1f}% year over year",
             loc="left", fontsize=10, color="#555555")
ax.set_xlabel("")  # drink names are self-explanatory
ax.set_ylabel("Units sold")
ax.tick_params(axis="x", rotation=0)  # issue 1: no clipped names
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))  # issue 5
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.margins(y=0.12)  # headroom for the % labels
ax.legend(title=None, frameon=False)  # issue 4

OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, bbox_inches="tight", dpi=150)  # issue 1
print(f"wrote {OUT}")
