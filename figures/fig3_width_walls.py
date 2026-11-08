"""Fig 3: completion against exit width and against wall-law variant (E7). Runs from figures/data/fig3.json
(written by experiments/E7/analyze.py summary)."""
import json

import numpy as np

from common import ARM_COLOURS, HERE, fig_full, qa, save

d = json.load(open(HERE / "data" / "fig3.json"))
C1 = ARM_COLOURS["C1"]
DARK, LIGHT = "#3a3a3a", "#c4c4c4"        # deadlock classes: lone trap (blocker alone held) / pair or group standoff

fig = fig_full(4.4)
axL, axR = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.45]})

# ---- left: completion against exit width, C1, default walls
W = d["width"]
w = np.array([r["w"] for r in W]); p = np.array([r["p"] for r in W])
lo = np.array([r["lo"] for r in W]); hi = np.array([r["hi"] for r in W])
axL.plot(w, p, color=C1, lw=0.6, zorder=2)
axL.vlines(w, lo, hi, color=C1, lw=0.8, zorder=2)
axL.plot(w, p, marker="o", ms=3.4, ls="none", color=C1, zorder=3)
axL.set_xlim(0.66, 1.04)
axL.set_ylim(-0.03, 1.03)
axL.set_xticks([0.7, 0.8, 0.9, 1.0])
axL.set_yticks([0, 0.25, 0.5, 0.75, 1])
axL.set_xlabel("exit width $w$ (m)")
axL.set_ylabel("runs completed")

# ---- right: w = 0.8 m, one wall-law variant per column. Point and Wilson CI: completion. Bar: all runs by outcome
# (white completed, light grey standoff of two or more, dark grey lone trap)
LAB = {"default": "default", "B0.04": "all walls 0.04", "B0.02": "all walls 0.02", "Bedge0.04": "jambs 0.04",
       "rounded": "rounded", "line": "line goal", "line_rounded": "line + rounded"}
V = d["variants"]
xs = np.arange(len(V), dtype=float)
for x, r in zip(xs, V):
    n = r["n"]
    done, coll, lone = r["k"] / n, r["collective"] / n, r["lone"] / n
    bx = x + 0.2
    axR.bar(bx, done, width=0.26, bottom=0, color="white", edgecolor=DARK, lw=0.5, zorder=1)
    axR.bar(bx, coll, width=0.26, bottom=done, color=LIGHT, edgecolor=DARK, lw=0.5, zorder=1)
    axR.bar(bx, lone, width=0.26, bottom=done + coll, color=DARK, edgecolor=DARK, lw=0.5, zorder=1)
    axR.vlines(x - 0.14, r["lo"], r["hi"], color=C1, lw=0.8, zorder=2)
    axR.plot([x - 0.14], [r["p"]], marker="o", ms=3.4, ls="none", color=C1, zorder=3)
axR.set_xticks(xs)
axR.set_xticklabels([LAB[r["cell"]] for r in V], rotation=90)
axR.tick_params(axis="x", length=0, pad=2)
axR.set_xlim(-0.55, xs[-1] + 0.55)
axR.set_ylim(-0.03, 1.03)
axR.set_yticks([0, 0.25, 0.5, 0.75, 1])
axR.set_ylabel("runs completed")

save(fig, "fig3_width_walls")
qa("fig3_width_walls")
