"""Fig 3 (paper Fig. 4 before the geometry figure is inserted): completion against exit width and against wall-law
variant. Left from data/derived/rev_B2.json (rev_data.rev_width()), right from figures/data/fig3.json (experiments/E7/analyze.py).
Left: fraction of SFM runs completed against w with Wilson 95% intervals (1100 runs, 100 per width, w = 0.9 m once), the
fitted logistic with its pointwise 95% band, and the bracket on the critical width (grey bracket below the axis).
No prediction curves (ruling R2).
Right: w = 0.8 m, one wall-law variant per row: horizontal stacked bar of all runs by outcome (white completed, light
grey pair or group standoff, dark grey lone trap) with the Wilson 95% interval of the completed fraction drawn as a
whisker at the completed boundary."""
import json

import matplotlib.patheffects as pe
import numpy as np

from common import ARM_COLOURS, HERE, fig_full, qa, save
from rev_data import rev_width

d = json.load(open(HERE / "data" / "fig3.json"))
REV = rev_width()
assert REV is not None, 'data/derived/rev_B2.json missing'
C1 = ARM_COLOURS["C1"]
DARK, LIGHT = "#3a3a3a", "#c4c4c4"

fig = fig_full(4.4)
axL, axR = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.3]})

# ---- left: completion against exit width, SFM, default walls (rev_B2.json: 1100 runs, 11 widths, each run once)
W = REV["points"]
w = np.array([r["w"] for r in W]); p = np.array([r["p"] for r in W])
lo = np.array([r["lo"] for r in W]); hi = np.array([r["hi"] for r in W])
g = REV["logistic"]
axL.fill_between(g["w"], g["lo"], g["hi"], color="0.86", lw=0, zorder=0)
axL.plot(g["w"], g["mid"], color=C1, lw=0.8, zorder=1)
b_lo, b_hi = REV["bracket"]
yb = -0.075                                                       # bracket on w50, below the data
axL.plot([b_lo, b_lo, b_lo, b_hi, b_hi, b_hi], [yb - 0.025, yb + 0.025, yb, yb, yb + 0.025, yb - 0.025], color="0.35",
         lw=0.8, solid_joinstyle="miter", clip_on=False, zorder=2)
axL.vlines(w, lo, hi, color=C1, lw=0.7, zorder=2)
axL.plot(w, p, marker="o", ms=2.8, ls="none", color=C1, zorder=3)
axL.set_xlim(0.68, 1.02)
axL.set_ylim(-0.115, 1.03)
axL.set_xticks([0.7, 0.8, 0.9, 1.0])
axL.spines['left'].set_bounds(0, 1)
axL.set_yticks([0, 0.25, 0.5, 0.75, 1])
axL.set_yticklabels(["0", "0.25", "0.5", "0.75", "1"])
axL.set_xlabel("exit width $w$ (m)")
axL.set_ylabel("runs completed")

# ---- right: w = 0.8 m, one wall-law variant per row
LAB = {"default": "default", "B0.04": "all walls 0.04", "B0.02": "all walls 0.02", "Bedge0.04": "jambs 0.04",
       "rounded": "rounded", "line": "line goal", "line_rounded": "line + rounded"}
V = d["variants"]
for i, r in enumerate(V):
    y = -i
    n = r["n"]
    done, coll, lone = r["k"] / n, r["collective"] / n, r["lone"] / n
    kw = dict(height=0.62, edgecolor=DARK, lw=0.5, zorder=1)
    axR.barh(y, done, left=0, color="white", **kw)
    axR.barh(y, coll, left=done, color=LIGHT, **kw)
    axR.barh(y, lone, left=done + coll, color=DARK, **kw)
    halo = [pe.Stroke(linewidth=2.1, foreground="white"), pe.Normal()]   # stays visible over the dark segment
    axR.plot([r["lo"], r["lo"], r["lo"], r["hi"], r["hi"], r["hi"]], [y - 0.14, y + 0.14, y, y, y + 0.14, y - 0.14],
             color=C1, lw=0.9, solid_joinstyle="miter", path_effects=halo, zorder=3)
axR.set_yticks([-i for i in range(len(V))])
axR.set_yticklabels([LAB[r["cell"]] for r in V])
axR.tick_params(axis="y", length=0, pad=2)
axR.set_ylim(-len(V) + 0.45, 0.55)
axR.set_xlim(0, 1)
axR.set_xticks([0, 0.25, 0.5, 0.75, 1])
axR.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
axR.set_xlabel("fraction of runs at $w=0.8$ m")
axR.spines["left"].set_visible(False)

save(fig, "fig3_width_walls")
qa("fig3_width_walls")
