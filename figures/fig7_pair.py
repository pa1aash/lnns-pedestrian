"""Fig 7: the pair class. Runs from figures/data/fig7.json (experiments/E7b/analyze.py: static curve, ORCA
reference rates, arm order) and figures/data/fig7_boot.json (build_fig7_boot.py: cluster-bootstrap intervals over
pair snapshots, rebuilt from data/E7b when missing or stale)."""
import json

import build_fig7_boot
from common import ARM_COLOURS, HERE, fig_full, qa, save
from dotplot import dotplot

d = json.load(open(HERE / "data" / "fig7.json"))
bt = build_fig7_boot.get()
YEL = ARM_COLOURS["lateral bias"]
EDGE = "#000000"
STATIC = "#8c8c8c"
BS = r"b^{\textstyle\ast}"
LABEL = {"C1": "SFM", "C2": "SFM+TTC", "C3_pub": "legacy", "C3_rvo2": "RVO2", "drive_only": "drive part",
         "constraint_only_pub": "constraint part, legacy", "constraint_only_rvo2": "constraint part, RVO2",
         "frozen_plus": "rest-drive push $+$", "frozen_minus": "rest-drive push $-$",
         "bstarpubp": f"${{+}}{BS}$, legacy", "bstarpubm": f"${{-}}{BS}$, legacy",
         "bstarrvo2p": f"${{+}}{BS}$, RVO2", "bstarrvo2m": f"${{-}}{BS}$, RVO2"}
for s in ("0p01", "0p02", "0p03", "0p05"):
    LABEL[f"noise{s}"] = f"$\\sigma={s.replace('p', '.')}$"
HEADERS = ["baselines", "force-coupled ORCA", "bias", "noise"]

# the two reference lines are the force-coupled ORCA rates of fig7.json; the bootstrap cache must agree
for ref in ("C3_pub", "C3_rvo2"):
    assert abs(d["ref"][ref] - bt["rates"][ref]["p"]) < 1e-12, ref

fig = fig_full(6.8)
axL, axR = fig.subplots(1, 2, gridspec_kw={"width_ratios": [0.85, 1.4]})

# ---- left: freed fraction against signed lateral bias b (95% snapshot bootstrap), static prediction, ORCA rates
sc = d["static_curve"]
axL.plot(sc["b"], sc["frac"], color=STATIC, lw=0.8, zorder=2, drawstyle="steps-post")
axL.axhline(d["ref"]["C3_pub"], color=ARM_COLOURS["C3 published"], lw=1.0, ls="-.", zorder=1)   # legacy
axL.axhline(d["ref"]["C3_rvo2"], color=ARM_COLOURS["C3 RVO2"], lw=1.0, ls="-", zorder=1)        # RVO2
for p in bt["bias_curve"]:
    axL.plot([p["b"]] * 2, [p["lo"], p["hi"]], color=EDGE, lw=0.8, solid_capstyle="butt", zorder=3)
    axL.plot([p["b"]], [p["p"]], marker="o", ms=3.4, ls="none", mfc=YEL, mec=EDGE, mew=0.5, zorder=4)
axL.set_xlim(-0.035, 0.105)
axL.set_xticks([-0.03, 0, 0.03, 0.06, 0.09])
axL.set_xticklabels(["$-0.03$", "0", "0.03", "0.06", "0.09"])
axL.set_ylim(-0.03, 1.03)
axL.set_yticks([0, 0.25, 0.5, 0.75, 1])
axL.set_yticklabels(["0", "0.25", "0.5", "0.75", "1"])
axL.set_xlabel("lateral bias $b$")
axL.set_ylabel("pairs freed within 120 s")

# ---- right: freed fraction per perturbation, 95% cluster bootstrap over pair snapshots
groups = [(h, [(a, LABEL[a]) for a in g]) for h, g in zip(HEADERS, d["groups"])]
dotplot(axR, groups, [{"values": {a: (r["p"], r["lo"], r["hi"]) for a, r in bt["rates"].items()}}])
axR.set_xticks([0, 0.25, 0.5, 0.75, 1])
axR.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
axR.grid(axis="x", color="#e2e2e2", lw=0.5, zorder=0)
axR.set_axisbelow(True)
axR.set_xlabel("pairs freed within 120 s")

save(fig, "fig7_pair")
qa("fig7_pair")
