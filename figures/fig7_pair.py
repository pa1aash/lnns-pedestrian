"""Fig 7: the pair class. Runs from figures/data/fig7.json (written by experiments/E7b/analyze.py)."""
import json

import numpy as np

from common import ARM_COLOURS, HERE, fig_full, qa, save

d = json.load(open(HERE / "data" / "fig7.json"))
PURPLE = ARM_COLOURS["push / drive"]
YEL = ARM_COLOURS["lateral bias"]
EDGE = "#3a3a3a"
COL = {"C1": ARM_COLOURS["C1"], "C2": ARM_COLOURS["C2"],
       "C3_pub": ARM_COLOURS["C3 published"], "C3_rvo2": ARM_COLOURS["C3 RVO2"],
       "drive_only": PURPLE, "constraint_only_pub": PURPLE, "constraint_only_rvo2": PURPLE,
       "frozen_plus": PURPLE, "frozen_minus": PURPLE}
LABEL = {"C1": "C1", "C2": "C2", "C3_pub": "C3 pub", "C3_rvo2": "C3 RVO2", "drive_only": "drive",
         "constraint_only_pub": "constraint pub", "constraint_only_rvo2": "constraint RVO2",
         "frozen_plus": "push $+$", "frozen_minus": "push $-$",
         "bstarpubp": "$+b^{\\textstyle\\ast}$ pub", "bstarpubm": "$-b^{\\textstyle\\ast}$ pub",
         "bstarrvo2p": "$+b^{\\textstyle\\ast}$ RVO2", "bstarrvo2m": "$-b^{\\textstyle\\ast}$ RVO2"}
for s in ("0p01", "0p02", "0p03", "0p05"):
    COL[f"noise{s}"] = ARM_COLOURS["noise"]
    LABEL[f"noise{s}"] = f"$\\sigma={s.replace('p', '.')}$"
for k in ("bstarpubp", "bstarpubm", "bstarrvo2p", "bstarrvo2m"):
    COL[k] = YEL

fig = fig_full(4.4)
axL, axR = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.45]})

# ---- left: freed fraction against signed lateral bias b
sc = d["static_curve"]
axL.plot(sc["b"], sc["frac"], color=EDGE, lw=0.7, zorder=2, drawstyle="steps-post")
for ref, c in (("C3_pub", ARM_COLOURS["C3 published"]), ("C3_rvo2", ARM_COLOURS["C3 RVO2"])):
    axL.axhline(d["ref"][ref], color=c, lw=0.9, zorder=1)
for p in d["bias_curve"]:
    _, lo, hi = p["wilson"]
    axL.plot([p["b"]] * 2, [lo, hi], color=YEL, lw=1.0, solid_capstyle="butt", zorder=3)
    axL.plot([p["b"]], [p["wilson"][0]], marker="o", ms=3.4, ls="none", mfc=YEL, mec=EDGE, mew=0.4, zorder=4)
axL.set_xlim(-0.035, 0.105)
axL.set_xticks([-0.03, 0, 0.03, 0.06, 0.09])
axL.set_xticklabels(["$-0.03$", "0", "0.03", "0.06", "0.09"])
axL.set_ylim(-0.03, 1.03)
axL.set_yticks([0, 0.25, 0.5, 0.75, 1])
axL.set_xlabel("lateral bias $b$")
axL.set_ylabel("pair freed (120 s)")

# ---- right: freed fraction per intervention, Wilson 95% CI
x, xs, labels = 0.0, [], []
for gi, grp in enumerate(d["groups"]):
    if gi:
        x += 0.6
    for arm in grp:
        xs.append(x)
        labels.append(LABEL[arm])
        c = COL[arm]
        p, lo, hi = d["rates"][arm]["wilson"]
        yel = c == YEL
        axR.plot([x] * 2, [lo, hi], color=c, lw=1.0 if yel else 0.8, solid_capstyle="butt", zorder=2)
        axR.plot([x], [p], marker="o", ms=3.4, ls="none", mfc=c, mec=EDGE if yel else c, mew=0.4, zorder=3)
        x += 1.0
axR.set_xticks(xs)
axR.set_xticklabels(labels, rotation=90)
axR.tick_params(axis="x", length=0, pad=2)
axR.set_xlim(xs[0] - 0.6, xs[-1] + 0.6)
axR.set_ylim(-0.03, 1.03)
axR.set_yticks([0, 0.25, 0.5, 0.75, 1])
axR.set_ylabel("pair freed (120 s)")

save(fig, "fig7_pair")
qa("fig7_pair")
