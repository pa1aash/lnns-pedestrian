"""Fig 4: noise as collective escape. Runs from figures/data/fig4.json (written by experiments/E4/analyze.py)."""
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

# ---- right: barrier-scaled collapse
xs = np.array([p["x"] for p in d["collapse"]])
axR.plot([1.2, 3.8], [-1.2, -3.8], color="0.55", lw=0.7, zorder=1)
for c in ("full", "frozen", "alone"):
    P = [p for p in d["collapse"] if p["cond"] == c]
    off = {"full": -0.09, "frozen": 0.0, "alone": 0.09}[c]
    axR.plot([p["x"] + off for p in P], [p["y"] for p in P], ls="none", marker=MK[c], ms=3.0,
             mfc=FILL[c], mec=V, mew=0.7, alpha=0.9, zorder=3)
axR.set_xlim(1.1, 3.9)
axR.set_xticks([1.5, 2.5, 3.5])
axR.set_xticklabels(["1.5", "2.5", "3.5"])
axR.set_ylim(-4.5, -0.8)
axR.set_yticks([-4, -3, -2, -1])
axR.set_xlabel(r"$\Delta U_{\mathrm{cond}} / k_B T_{\mathrm{eff}}$")
axR.set_ylabel(r"$\ln(\hat\lambda / \hat\nu)$")

save(fig, "fig4_escape")
qa("fig4_escape")
