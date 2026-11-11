"""Fig 8 (paper Fig. 9): CroMa-geometry model cells (Part D rerun: agents = participants who passed, bottleneck 0.2 m or
2.0 m as in the archive) against the five human runs at w = 0.8 m. Data: figures/data/fig8_runs.json
(figures/build_fig8_cache.py from data/derived/rev_D.json).
Categories on a shared y-axis; three observables side by side: flow, longest gap between passages (log scale, the 600 s
horizon drawn), waiting-zone velocity fluctuation. Per category the runs as small markers and the mean with its
Student-t 95% interval for flow and fluctuation. Open markers: runs that did not complete (deadlocked or still running at
the 600 s horizon); in the gap panel the final gap of such a run is open, so its value is the right-censored lower bound
max(longest closed gap, last passage to 600 s) (ruling R4). Filled markers: longest gap of completed runs.
Category tick labels only."""
import json

import numpy as np

from common import ARM_COLOURS, HERE, fig_full, qa, save

runs = json.load(open(HERE / "data" / "fig8_runs.json"))
COL = {"humans": "#555555", "C1_cf": ARM_COLOURS["C1"], "C1_cf_edge": ARM_COLOURS["C1"],
       "C3_rvo2_cf": ARM_COLOURS["C3 RVO2"], "C1_cf_sig": ARM_COLOURS["noise"]}
LABEL = {"humans": "humans", "C1_cf": "SFM", "C1_cf_edge": r"SFM, $B_{w,\mathrm{edge}}$",
         "C3_rvo2_cf": "force-coupled ORCA", "C1_cf_sig": r"SFM + noise $\sigma^\ast$"}
XLAB = {"flow": "flow (ped/s)", "gap": "longest gap (s)", "fluct": "fluctuation (m/s)"}
SUMKEY = {"flow": "flow", "fluct": "fluct"}
order = ["humans", "C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]
T_MAX = runs["t_max_s"]

fig = fig_full(4.6)
axes = fig.subplots(1, 3, sharey=True, gridspec_kw={"width_ratios": [1, 1.15, 1]})
rng = np.random.default_rng(1)
for ax, m in zip(axes, ("flow", "gap", "fluct")):
    for i, c in enumerate(order):
        y0 = -i
        col = COL[c]
        R = runs["cells"][c]["runs"]
        v = np.array([r[m] for r in R], float)
        done = ~np.array([r["censored"] if m == "gap" else not r["complete"] for r in R])
        jit = y0 + 0.13 + rng.uniform(-0.13, 0.13, len(v))
        ax.plot(v[done], jit[done], ls="none", marker="o", ms=2.3, mfc=col, mec=col, mew=0, alpha=0.6, zorder=2)
        ax.plot(v[~done], jit[~done], ls="none", marker="o", ms=2.3, mfc="white", mec=col, mew=0.5, zorder=2)
        if m in SUMKEY:
            s = runs["cells"][c][SUMKEY[m]]
            lo, hi = s["ci95"]
            ax.plot([lo, hi], [y0 - 0.24] * 2, color=col, lw=0.9, solid_capstyle="butt", zorder=3)
            ax.plot([s["mean"]], [y0 - 0.24], ls="none", marker="o", ms=3.4, mfc=col, mec=col, zorder=4)
    ax.set_xlabel(XLAB[m])
    if m == "gap":
        ax.axvline(T_MAX, color="0.6", lw=0.6, zorder=1)
        ax.set_xscale("log")
        ax.set_xlim(1, 1000)
        ax.set_xticks([1, 10, 100, 1000])
        ax.set_xticklabels(["1", "10", "100", "1000"])
        ax.minorticks_off()
    else:
        ax.set_xlim(left=0)
    ax.tick_params(axis="y", length=0)
axes[0].set_yticks([-i for i in range(len(order))])
axes[0].set_yticklabels([LABEL[c] for c in order])
axes[0].set_ylim(-len(order) + 0.5, 0.5)
axes[2].set_xlim(0, 0.12)
axes[2].set_xticks([0, 0.05, 0.1])
axes[2].set_xticklabels(["0", "0.05", "0.1"])
axes[0].set_xticks([0, 0.5, 1, 1.5])
axes[0].set_xticklabels(["0", "0.5", "1", "1.5"])

save(fig, "fig8_croma")
qa("fig8_croma")
