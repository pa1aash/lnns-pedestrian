"""Fig 6: lone-trap quench outcomes. Runs from figures/data/fig6_boot.json (build_fig6_boot.py: cluster-bootstrap
intervals over snapshots, rebuilt from data/E2 when missing or stale); fig6.json (experiments/E2/analyze.py) gives
the arm order."""
import json

import numpy as np

import build_fig6_boot
from common import ARM_COLOURS, HERE, fig_full, qa, save
from dotplot import dotplot

d = json.load(open(HERE / "data" / "fig6.json"))
bt = build_fig6_boot.get()
LABEL = {"C1": "SFM", "C2": "SFM+TTC", "C3_pub": "legacy", "C3_rvo2": "RVO2", "drive_only": "drive part",
         "constraint_only_pub": "constraint part, legacy", "constraint_only_rvo2": "constraint part, RVO2",
         "frozen_plus": "rest-drive push $+$", "frozen_minus": "rest-drive push $-$",
         "bias0p05": "$b=0.05$", "bias0p1": "$b=0.1$", "bias0p2": "$b=0.2$", "bias0p5": "$b=0.5$",
         "noise0p03": "$\\sigma=0.03$", "noise0p05": "$\\sigma=0.05$", "noise0p07": "$\\sigma=0.07$"}
HEADERS = ["baselines", "force-coupled ORCA", "bias", "noise"]
BLUE, VERM, GREY = ARM_COLOURS["C3 RVO2"], ARM_COLOURS["noise"], "#b4b4b4"

fig = fig_full(6.8)
axL, axR = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1]})

# ---- left: blocker freed within 120 s; filled = lone keystone, open = second trap; 95% cluster bootstrap
groups = [(h, [(a, LABEL[a]) for a in g]) for h, g in zip(HEADERS, d["groups"])]
series = [{"values": {a: (r["p"], r["lo"], r["hi"]) for a, r in bt["strata"][st]["rates"].items()},
           "filled": filled, "dy": dy}
          for st, filled, dy in (("lone_keystone", True, -0.17), ("lone_keystone_second_trap", False, 0.17))]
dotplot(axL, groups, series)
axL.set_xticks([0, 0.25, 0.5, 0.75, 1])
axL.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
axL.grid(axis="x", color="#e2e2e2", lw=0.5, zorder=0)
axL.set_axisbelow(True)
axL.set_xlabel("blocker freed within 120 s")

# ---- right: lone keystones, cumulative fraction freed against time (log), pointwise 95% cluster bootstrap
C = bt["curves_lone_keystone"]
T0, TMAX = 0.5, bt["t_max_s"]


def steps(c, k="F"):
    t = np.array(c["t"], float)
    t[0] = T0
    return t, np.array(c[k], float)


for arm in ("noise0p03", "noise0p05", "drive_only", "C3_pub", "frozen_plus"):
    t, F = steps(C[arm])
    axR.step(t, F, where="post", color=GREY, lw=0.7, zorder=1)
for arm, col, ls in (("C3_rvo2", BLUE, "-"), ("noise0p07", VERM, "--")):
    t, F = steps(C[arm])
    _, lo = steps(C[arm], "lo")
    _, hi = steps(C[arm], "hi")
    axR.fill_between(t, lo, hi, step="post", color=col, alpha=0.22, lw=0, zorder=2)
    axR.step(t, F, where="post", color=col, ls=ls, lw=1.1, zorder=4)
axR.axvline(TMAX, color="#6e6e6e", lw=0.6, ls=":", zorder=0)   # 120 s horizon: every held run is censored here
axR.set_xscale("log")
axR.set_xlim(T0, 160)
axR.set_xticks([0.5, 1, 3, 10, 30, 120])
axR.set_xticklabels(["0.5", "1", "3", "10", "30", "120"])
axR.minorticks_off()
axR.set_ylim(0, 1)
axR.set_yticks([0, 0.25, 0.5, 0.75, 1])
axR.set_yticklabels(["0", "0.25", "0.5", "0.75", "1"])
axR.set_xlabel("time after quench start (s)")
axR.set_ylabel("lone keystones freed")

save(fig, "fig6_quench")
qa("fig6_quench")
