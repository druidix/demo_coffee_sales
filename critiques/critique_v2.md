<!-- critic: claude-fable-5-1 -->

**Verdict**
The chart does its job: the takeaway is in the title, the data supports it (I checked the four ratios and the +7.7% aggregate against the bar heights), and the grey/blue encoding makes "then vs. now" obvious at a glance. Remaining issues are polish and robustness, not correctness.

**Issues**

1. **Medium – Title and subtitle left edges don't line up.** `fig.suptitle(x=0.08)` is a figure-fraction guess; the subtitle is anchored to the axes left edge (~0.10), so the headline sticks out ~60 px to the left. Fix: drop `suptitle` and put the headline in axes coordinates so both share the same anchor, e.g. `ax.text(0, 1.10, headline, transform=ax.transAxes, ha="left", fontsize=14, fontweight="bold")`, or call `fig.canvas.draw()` and set `x=ax.get_position().x0` for the suptitle.

2. **Medium – Percent labels float over the gap between bars, and the placement logic assumes 2026 is the taller bar.** `xy=(i, totals.loc[drink].max())` centres the label on the pair, so it sits in the whitespace between grey and blue rather than above either bar. If a drink ever declines, the label would hover above the grey bar while visually "belonging" to neither. Fix: anchor each label to the 2026 bar using the patch geometry: `for bar, p in zip(ax.containers[1], pct): ax.annotate(f"{p:+.1f}%", (bar.get_x() + bar.get_width()/2, bar.get_height()), xytext=(0, 4), textcoords="offset points", ha="center", ...)`. Also colour declines red (`color="#c0392b" if p < 0`) so the headline/else-branch and the labels stay consistent.

3. **Low – No guard that both quarters have equal coverage.** The pivot sums whatever rows exist; a few missing days in one year would silently inflate or deflate the % change the title asserts. Add before the pivot: `days = df.groupby("quarter")["date"].nunique(); assert days.nunique() == 1, days` (Q1 2025 and Q1 2026 are both 90 days, so this should pass).

4. **Low – Absolute levels require reading the axis.** For a business reader, "+5.6%" of what? Consider `ax.bar_label(ax.containers[1], fmt="{:,.0f}", padding=2, fontsize=8, color="#555555")` for the 2026 bars only (keep the % label above it), or state the 2026 totals in the subtitle. Don't label both series—that would clutter.

5. **Low – Subtitle duplicates the y-label.** "Units sold per quarter" repeats "Units sold". Make the subtitle carry new information: `f"Q1 2025 vs Q1 2026, all drinks combined {overall:+.1f}% ({totals['Q1 2025'].sum():,.0f} → {totals['Q1 2026'].sum():,.0f} units)"`.

6. **Low – Legend could be replaced by direct labels.** With only two series and plenty of room, `ax.text` of "Q1 2025" / "Q1 2026" in the series colour above the first pair (or `ax.bar_label` on the first container with the series name) removes an eye-movement. Optional; the current `frameon=False` legend is acceptable.

7. **Low – `ax.margins(y=0.12)` relies on sticky edges to keep the baseline at 0.** It works for bars today, but if someone adds a line or scatter later the y-axis will float below zero. Make it explicit: `ax.set_ylim(0, totals.values.max() * 1.15)`.
