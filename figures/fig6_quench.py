"""Fig 6: lone-trap quench outcomes. Runs from figures/data/fig6.json (written by experiments/E2/analyze.py)."""
import json

import numpy as np

from common import ARM_COLOURS, HERE, fig_full, qa, save

d = json.load(open(HERE / "data" / "fig6.json"))
PURPLE = ARM_COLOURS["push / drive"]
COL = {"C1": ARM_COLOURS["C1"], "C2": ARM_COLOURS["C2"],
       "C3_pub": ARM_COLOURS["C3 published"], "C3_rvo2": ARM_COLOURS["C3 RVO2"],
       "drive_only": PURPLE, "constraint_only_pub": PURPLE, "constraint_only_rvo2": PURPLE,
       "frozen_plus": PURPLE, "frozen_minus": PURPLE}
for b in ("0p05", "0p1", "0p2", "0p5"):
    COL[f"bias{b}"] = ARM_COLOURS["lateral bias"]
for s in ("0p03", "0p05", "0p07"):
    COL[f"noise{s}"] = ARM_COLOURS["noise"]
LABEL = {"C1": "C1", "C2": "C2", "C3_pub": "C3 pub", "C3_rvo2": "C3 RVO2", "drive_only": "drive",
         "constraint_only_pub": "constraint pub", "constraint_only_rvo2": "constraint RVO2",
         "frozen_plus": "push $+$", "frozen_minus": "push $-$",
         "bias0p05": "$b=0.05$", "bias0p1": "$b=0.1$", "bias0p2": "$b=0.2$", "bias0p5": "$b=0.5$",
         "noise0p03": "$\\sigma=0.03$", "noise0p05": "$\\sigma=0.05$", "noise0p07": "$\\sigma=0.07$"}
EDGE = "#3a3a3a"

fig = fig_full(5.8)
axL, axR = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.75, 1]})

# ---- left: blocker freed within 120 s, Wilson 95% CI; filled = lone keystone, open = second trap
x, xs, labels = 0.0, [], []
for gi, grp in enumerate(d["groups"]):
    if gi:
        x += 0.6
    for arm in grp:
        xs.append(x)
        labels.append(LABEL[arm])
        c = COL[arm]
        for dx, stratum, filled in ((-0.17, "lone_keystone", True), (0.17, "lone_keystone_second_trap", False)):
            p, lo, hi = d["rates"][stratum][arm]["wilson"]
            axL.plot([x + dx] * 2, [lo, hi], color=c, lw=1.0 if arm.startswith("bias") else 0.8, solid_capstyle="butt", zorder=2)
            axL.plot([x + dx], [p], marker="o", ms=3.4, ls="none", zorder=3,
                     mfc=c if filled else "white", mec=EDGE if (filled and arm.startswith("bias")) else c,
                     mew=0.4 if filled else (1.2 if arm.startswith("bias") else 0.9))
        x += 1.0
axL.set_xticks(xs)
axL.set_xticklabels(labels, rotation=90)
axL.tick_params(axis="x", length=0, pad=2)
axL.set_xlim(xs[0] - 0.6, xs[-1] + 0.6)
axL.set_ylim(-0.03, 1.03)
axL.set_yticks([0, 0.25, 0.5, 0.75, 1])
axL.set_ylabel("blocker freed within 120 s")

# ---- right: pooled Kaplan-Meier cumulative freed fraction, log time
STYLE = {"C3_pub": "-.", "C3_rvo2": "-", "drive_only": "--", "frozen_plus": "-",
         "noise0p03": ":", "noise0p05": "--", "noise0p07": "-"}
for arm, curve in d["km_pooled"].items():
    t = np.array([p[0] for p in curve])
    F = 1 - np.array([p[1] for p in curve])
    t[0] = 0.3
    axR.step(t, F, where="post", color=COL[arm], ls=STYLE[arm], lw=1.0, zorder=3 if arm != "C3_pub" else 2)
axR.set_xscale("log")
axR.set_xlim(0.3, d["t_max_s"])
axR.set_xticks([0.3, 1, 3, 10, 30, 100])
axR.set_xticklabels(["0.3", "1", "3", "10", "30", "100"])
axR.minorticks_off()
axR.set_ylim(0, 1)
axR.set_yticks([0, 0.25, 0.5, 0.75, 1])
axR.set_xlabel("time after quench start (s)")
axR.set_ylabel("fraction freed")

save(fig, "fig6_quench")
qa("fig6_quench")
