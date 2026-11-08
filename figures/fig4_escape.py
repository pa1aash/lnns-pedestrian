"""Fig 4: noise as collective activated escape. Left: Kaplan-Meier curves from figures/data/fig4.json
(experiments/E4/analyze.py). Right: per (snapshot, condition) ratio of the fitted Arrhenius slope to -dU_cond
with its 95% interval, from data/derived/E4_analysis.json; markers by condition (full o, pinned s, alone ^)."""
import json

import numpy as np

from common import ARM_COLOURS, HERE, fig_full, qa, save

d = json.load(open(HERE / "data" / "fig4.json"))
V = ARM_COLOURS["noise"]
LS = {"full": "-", "frozen": "--", "alone": ":"}
MK = {"full": "o", "frozen": "s", "alone": "^"}
FILL = {"full": V, "frozen": "white", "alone": V}

fig = fig_full(5.4)
axL, axR = fig.subplots(1, 2)

# ---- left: Kaplan-Meier escape curves at dU/kT = 2.5, pooled over snapshots
for c in ("full", "frozen", "alone"):
    t = np.array([p[0] for p in d["km"][c]])
    F = 1 - np.array([p[1] for p in d["km"][c]])
    axL.step(t, F, where="post", color=V, ls=LS[c], lw=1.0)
axL.set_xlim(0, 300)
axL.set_xticks([0, 100, 200, 300])
axL.set_ylim(0, 1)
axL.set_yticks([0, 0.25, 0.5, 0.75, 1])
axL.set_yticklabels(["0", "0.25", "0.5", "0.75", "1"])
axL.set_xlabel("time after restart (s)")
axL.set_ylabel("fraction escaped")

# ---- right: Arrhenius slope over -dU per (snapshot, condition), 95% intervals (data/derived/E4_analysis.json)
E4 = json.load(open(HERE.parent / "data" / "derived" / "E4_analysis.json"))
OFF = {"full": 0.94, "frozen": 1.0, "alone": 1.06}
axR.axhline(1.0, color="0.55", lw=0.7, zorder=1)
for c in ("full", "frozen", "alone"):
    P = [(cc["dU"], cc["arrhenius"]) for s in E4["snapshots"].values() for k, cc in s["conds"].items()
         if k == c and cc.get("arrhenius")]
    x = np.array([u for u, _ in P]) * OFF[c]
    r = np.array([a["ratio"] for _, a in P])
    lo = np.array([a["ratio_ci95"][0] for _, a in P])
    hi = np.array([a["ratio_ci95"][1] for _, a in P])
    axR.errorbar(x, r, yerr=[r - lo, hi - r], ls="none", marker=MK[c], ms=3.0, mfc=FILL[c], mec=V, mew=0.7,
                 ecolor=V, elinewidth=0.6, capsize=0, zorder=3)
axR.set_xscale("log")
axR.set_xlim(0.5, 150)
axR.set_xticks([1, 10, 100])
axR.set_xticklabels(["1", "10", "100"])
axR.set_ylim(0, 2.2)
axR.set_yticks([0, 0.5, 1, 1.5, 2])
axR.set_yticklabels(["0", "0.5", "1", "1.5", "2"])
axR.set_xlabel(r"$\Delta U_{\mathrm{cond}}$ (J)")
axR.set_ylabel(r"Arrhenius slope / $(-\Delta U_{\mathrm{cond}})$")

save(fig, "fig4_escape")
qa("fig4_escape")
