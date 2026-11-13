#!/usr/bin/env python3
"""Chart v3: Q1 2025 vs Q1 2026 coffee sales by drink, revised per critiques/critique_v2.md."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: write a PNG, no window
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import StrMethodFormatter

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "coffee_sales_q1.csv"
OUT = ROOT / "charts" / "chart_v3.png"
BASE, CURRENT = "Q1 2025", "Q1 2026"

df = pd.read_csv(DATA)
days = df.groupby("quarter")["date"].nunique()
assert days.nunique() == 1, f"quarters cover different day counts: {days.to_dict()}"  # issue 3

totals = df.pivot_table(index="drink", columns="quarter", values="units_sold", aggfunc="sum")
assert list(totals.columns) == [BASE, CURRENT], totals.columns
totals = totals.sort_values(CURRENT, ascending=False)
pct = (totals[CURRENT] / totals[BASE] - 1) * 100
base_sum, cur_sum = totals[BASE].sum(), totals[CURRENT].sum()
overall = (cur_sum / base_sum - 1) * 100

if (pct > 0).all():
    headline = f"Every drink sold more in {CURRENT} than in {BASE}"
else:
    headline = f"Coffee units sold by drink, {BASE} vs {CURRENT}"

fig, ax = plt.subplots(figsize=(9, 5.5))
totals.plot(kind="bar", ax=ax, color=["#b0b0b0", "#1f77b4"], width=0.75, edgecolor="white")

# issues 2 + 4: value and % change anchored to each CURRENT bar; declines in red
for bar, p in zip(ax.containers[1], pct):
    x, h = bar.get_x() + bar.get_width() / 2, bar.get_height()
    ax.annotate(f"{h:,.0f}", (x, h), xytext=(0, 3), textcoords="offset points",
                ha="center", fontsize=8, color="#555555")
    ax.annotate(f"{p:+.1f}%", (x, h), xytext=(0, 15), textcoords="offset points",
                ha="center", fontsize=10, fontweight="bold",
                color="#c0392b" if p < 0 else "black")

# issue 1: headline and subtitle share the axes' left edge
ax.text(0, 1.13, headline, transform=ax.transAxes, ha="left", fontsize=14, fontweight="bold")
# issue 5: subtitle carries new information instead of repeating the y-label
ax.text(0, 1.05, f"All drinks combined: {base_sum:,.0f} → {cur_sum:,.0f} units ({overall:+.1f}%)",
        transform=ax.transAxes, ha="left", fontsize=10, color="#555555")

ax.set_xlabel("")
ax.set_ylabel("Units sold")
ax.tick_params(axis="x", rotation=0)
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, totals.values.max() * 1.15)  # issue 7: explicit zero baseline + label headroom
# issue 6 (optional) declined: a frameless legend is kept so identity never relies on position alone
ax.legend(title=None, frameon=False, loc="upper right")

OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, bbox_inches="tight", dpi=150)
print(f"wrote {OUT}")
