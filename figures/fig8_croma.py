"""Fig 8: CroMa-geometry model cells against the five human runs at w = 0.8 m.
Runs from figures/data/fig8.json (written by experiments/E10/analyze.py).
Three panels: flow, longest gap between passages (log scale), waiting-zone velocity fluctuation. Per category: the runs as
small points and the mean with its Student-t 95% interval. Category tick labels only."""
import json

import numpy as np

from common import ARM_COLOURS, HERE, fig_full, qa, save

d = json.load(open(HERE / "data" / "fig8.json"))
COL = {"humans": ARM_COLOURS["humans"], "C1_cf": ARM_COLOURS["C1"], "C1_cf_edge": ARM_COLOURS["C1"],
       "C3_rvo2_cf": ARM_COLOURS["C3 RVO2"], "C1_cf_sig": ARM_COLOURS["noise"]}
# filled circles; the jamb wall variant as a filled square
MARK = {"humans": ("o", True), "C1_cf": ("o", True), "C1_cf_edge": ("s", True),
        "C3_rvo2_cf": ("o", True), "C1_cf_sig": ("o", True)}
LABEL = {"humans": "humans", "C1_cf": "SFM", "C1_cf_edge": r"SFM with $B_{w,\mathrm{edge}}$",
         "C3_rvo2_cf": "ORCA RVO2", "C1_cf_sig": r"SFM + noise $\sigma^\ast$"}
YLAB = {"flow": "flow (ped/s)", "longest_gap": "longest gap (s)", "fluct": "waiting-zone fluctuation (m/s)"}

order = [c for c in d["order"] if c in LABEL]   # the C1_pub cell in the cache is not plotted
fig = fig_full(6.6)   # 6.2 before the longer vocabulary-v2 tick labels
axes = fig.subplots(1, 3)
rng = np.random.default_rng(1)
for ax, m in zip(axes, d["metrics"]):
    for x, c in enumerate(order):
        col = COL[c]
        v = np.array([u for u in d["runs"][c][m] if u is not None], float)
        ax.plot(x + rng.uniform(-0.18, 0.18, len(v)), v, ls="none", marker=".", ms=2.2, color=col, alpha=0.75 if c == "humans" else 0.35,
                mew=0, zorder=1)
        s = d["summary"][c][m]
        lo, hi = s["ci95"]
        if lo is not None:
            ax.plot([x + 0.32] * 2, [lo, hi], color=col, lw=0.9, solid_capstyle="butt", zorder=2)
        mk, filled = MARK[c]
        ax.plot([x + 0.32], [s["mean"]], marker=mk, ms=3.6, ls="none", zorder=3, mec=col,
                mfc=col if filled else "white", mew=0.9)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([LABEL[c] for c in order], rotation=90)
    ax.tick_params(axis="x", length=0, pad=2)
    ax.set_xlim(-0.6, len(order) - 0.3)
    ax.set_ylabel(YLAB[m])
    if m == "longest_gap":
        ax.set_yscale("log")
        ax.set_ylim(1, 500)
        ax.set_yticks([1, 3, 10, 30, 100, 300])
        ax.set_yticklabels(["1", "3", "10", "30", "100", "300"])
        ax.minorticks_off()
    else:
        ax.set_ylim(bottom=0)

save(fig, "fig8_croma")
qa("fig8_croma")
