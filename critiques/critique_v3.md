<!-- critic: claude-fable-5-1 -->

**Verdict**
The chart achieves its goal: the headline states the finding, the labels back it up, the arithmetic checks out (per-drink values sum to the subtitle totals, % changes match the bar ratios), and sorting/colour direct the eye correctly. What remains is polish and one wording/robustness concern.

**Issues**

1. **Medium — "sales" vs "units".** The goal says "compare coffee sales" and the data has a `revenue_usd` column. The headline "sold more" is true for units but could be read as revenue, which may differ if `unit_price_usd` changed between years. Either make the headline explicit (`f"Every drink sold more units in {CURRENT} than in {BASE}"`) or add a one-line check in code (`rev = df.pivot_table(index="drink", columns="quarter", values="revenue_usd", aggfunc="sum")`) and mention revenue in the subtitle so the reader knows both move the same way.

2. **Medium — Q1 2025 bars carry no values.** The reader sees 6,656 and +9.3% but must back-compute ~6,090 for the grey bar; for Black coffee vs Latte in 2025 the grey bars are visually identical (≈6,090 vs ≈6,100) and the reader can't tell. Add small grey labels to `ax.containers[0]` with `ax.bar_label(ax.containers[0], fmt="{:,.0f}", fontsize=8, color="#777777", padding=2)`, or if that feels crowded, put the base value inside the top of the grey bar (`label_type="center"` is too low; use an `annotate` at `h - 150` in white).

3. **Low — annotation order is positional, not keyed.** `zip(ax.containers[1], pct)` works only because `pct` was derived from the already-sorted `totals`. A later reorder would silently mislabel bars. Iterate with the index instead: `for drink, bar in zip(totals.index, ax.containers[1]): p = pct[drink]`.

4. **Low — missing-drink guard.** If a drink appears in only one quarter, `pivot_table` yields NaN, `(pct > 0).all()` falls back to the neutral headline, and the bar gets a literal `nan%` label. Add `assert totals.notna().all().all(), totals` after the pivot.

5. **Low — visual bar differences are subtle.** With +5.6% to +9.3% changes, the grouped bars look almost equal; the message is carried entirely by the labels. That's acceptable for a "compare both years" brief, but if the % change is the point, a secondary small panel of `pct.plot(kind="barh")` or simply making the `+x.x%` labels the only bold element (already done) is enough. No redesign required — just be aware the bars themselves don't tell the story.

6. **Low — y-label and tick typography.** The y-axis label "Units sold" (10 pt) is noticeably smaller than the x tick labels (~11 pt) and sits far from the ticks. Set `ax.set_ylabel("Units sold", fontsize=11)` and `ax.tick_params(axis="both", labelsize=10)` so the two axes match.

7. **Low — headroom slightly generous.** `ylim` at 1.15× max leaves a gap between the +9.3% label and the top; 1.12 would tighten it without clipping the two-line annotation (3 pt + 15 pt offsets). Purely cosmetic.
