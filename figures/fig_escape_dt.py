"""Activated escape and the time-step signature, one full-width figure in three panels (replaces fig4_escape and
fig5_dt in the paper; their scripts are kept).
(a) Arrhenius collapse: ln(lambda_hat / nu_hat) against beta = dU_cond / k_B T_eff for every (snapshot, condition,
    level) with an Arrhenius fit, with the line of slope -1 (data/derived/E4_analysis.json; experiments/E4/analyze.py),
    plus the high-beta restarts beta = 5-7 (data/derived/rev_B3.json, black triangles).
(b) Arrhenius slope ratio -s / dU_cond per (snapshot, condition) with its 95% interval against dU_cond (log axis), with
    the B3 fits over beta = 1.5-7 (black triangles, alone condition, three snapshots) and a dashed reference at 0.9.
    The A4 trend is dropped: B3 shows the decline was a beta = 1.5-2.5 effect at the deepest barrier.
(c) Time-step signature, pooled over snapshots: escape rate normalised at dt = 0.01 s for per-step noise (filled),
    sqrt(dt)-scaled noise (open) and force-coupled ORCA (RVO2) (diamonds), with the per-step Arrhenius predictions
    (figures/data/fig5.json; experiments/E3/analyze.py). Conditions within a level are offset horizontally.
Markers by condition: full o, pinned s, alone ^ (filled, open, filled)."""
import json
import math

import matplotlib.colors as mc
import numpy as np

from common import ARM_COLOURS, HERE, fig_full, qa, save
from rev_data import rev_arrhenius

ROOT = HERE.parent
E4 = json.load(open(ROOT / "data" / "derived" / "E4_analysis.json"))
d5 = json.load(open(HERE / "data" / "fig5.json"))
REV = rev_arrhenius()
assert REV is not None, 'data/derived/rev_B3.json missing'
V = ARM_COLOURS["noise"]
V_LIGHT = mc.to_hex(0.55 * np.array(mc.to_rgb(V)) + 0.45)
B = ARM_COLOURS["C3 RVO2"]
MK = {"full": "o", "frozen": "s", "alone": "^"}
FILL = {"full": V, "frozen": "white", "alone": V}
CONDS = ("full", "frozen", "alone")

fig = fig_full(4.7)
axA, axB, axC = fig.subplots(1, 3, gridspec_kw={"width_ratios": [1, 1, 1]})

# ---- (a) Arrhenius collapse
bmax = 4.0
for c in CONDS:
    xs, ys, lo, hi = [], [], [], []
    for s in E4["snapshots"].values():
        cc = s["conds"].get(c)
        if not cc or not cc.get("arrhenius"):
            continue
        nu = cc["arrhenius"]["nu_hat"]
        for L in cc["levels"].values():
            if not L["lam"] or L["lam"] <= 0:
                continue
            beta = cc["dU"] / L["kT_eff"]
            xs.append(beta); ys.append(math.log(L["lam"] / nu))
            lo.append(math.log(L["ci95"][0] / nu)); hi.append(math.log(L["ci95"][1] / nu))
    xs, ys, lo, hi = map(np.array, (xs, ys, lo, hi))
    off = {"full": -0.08, "frozen": 0.0, "alone": 0.08}[c]
    axA.errorbar(xs + off, ys, yerr=[ys - lo, hi - ys], ls="none", marker=MK[c], ms=2.6, mfc=FILL[c], mec=V, mew=0.6,
                 ecolor=V, elinewidth=0.5, alpha=0.8, capsize=0, zorder=3)
for p in REV["collapse"]:                       # B3 restarts at beta = 5-7, alone condition
    axA.errorbar([p["beta"]], [p["y"]], yerr=[[p["y"] - p["lo"]], [p["hi"] - p["y"]]], ls="none", marker="^",
                 ms=2.8, mfc="black", mec="black", mew=0.5, ecolor="black", elinewidth=0.5, capsize=0, zorder=4)
    bmax = max(bmax, p["beta"] + 0.5)
bb = np.array([0, 8])
axA.plot(bb, -bb, color="0.45", lw=0.7, zorder=1)
axA.set_xlim(0.8, bmax + 0.2)
axA.set_ylim(-bmax - 0.8, 0.5)
axA.set_xlabel(r"$\beta=\Delta U_{\mathrm{cond}}/k_{\mathrm{B}}T_{\mathrm{eff}}$")
axA.set_ylabel(r"$\ln(\hat\lambda/\hat\nu)$")

# ---- (b) slope ratio against the barrier
OFF = {"full": 0.94, "frozen": 1.0, "alone": 1.06}
axB.axhline(1.0, color="0.7", lw=0.5, zorder=1)
axB.axhline(0.9, color="0.35", lw=0.8, ls=(0, (3, 2)), zorder=1)          # reference: effective barrier about 0.9 dU
for c in CONDS:
    P = [(cc["dU"], cc["arrhenius"]) for s in E4["snapshots"].values() for k, cc in s["conds"].items()
         if k == c and cc.get("arrhenius")]
    x = np.array([u for u, _ in P]) * OFF[c]
    r = np.array([a["ratio"] for _, a in P])
    lo = np.array([a["ratio_ci95"][0] for _, a in P])
    hi = np.array([a["ratio_ci95"][1] for _, a in P])
    axB.errorbar(x, r, yerr=[r - lo, hi - r], ls="none", marker=MK[c], ms=2.6, mfc=FILL[c], mec=V, mew=0.6,
                 ecolor=V, elinewidth=0.5, capsize=0, zorder=3)
for q in REV["ratio"]:                           # B3: fit over beta = 1.5-7, alone condition
    axB.errorbar([q["dU"] * 1.16], [q["r"]], yerr=[[q["r"] - q["lo"]], [q["hi"] - q["r"]]], ls="none", marker="^",
                 ms=2.8, mfc="black", mec="black", mew=0.5, ecolor="black", elinewidth=0.5, capsize=0, zorder=4)
axB.set_xscale("log")
axB.set_xlim(0.5, 150)
axB.set_xticks([1, 10, 100])
axB.set_xticklabels(["1", "10", "100"])
axB.set_ylim(0, 2.2)
axB.set_yticks([0, 0.5, 1, 1.5, 2])
axB.set_yticklabels(["0", "0.5", "1", "1.5", "2"])
axB.set_xlabel(r"$\Delta U_{\mathrm{cond}}$ (J)")
axB.set_ylabel(r"slope ratio $-s/\Delta U_{\mathrm{cond}}$")

# ---- (c) time-step signature (pooled over snapshots)
MARK = {"b1p5": "o", "b2p5": "s"}
dts = np.array(d5["dts"]); grid = np.array(d5["grid"])
axC.axhline(1.0, color="0.85", lw=0.5, zorder=0)
off = {"b1p5": 0.955, "b2p5": 1.045}
for lv in ("b1p5", "b2p5"):
    ps, ds = d5["per_step"][lv], d5["dt_scaled"][lv]
    axC.plot(grid, ps["pred"], color=V, lw=0.7, zorder=2)
    m = np.array(ds["mean"]); xo = dts / off[lv]
    axC.plot(xo, m, color=V_LIGHT, lw=0.7, zorder=2)
    for x, (lo, hi) in zip(xo, ds["ci95"]):
        axC.plot([x, x], [lo, hi], color=V_LIGHT, lw=0.7, zorder=2)
    axC.plot(xo, m, ls="none", marker=MARK[lv], ms=2.8, mfc="white", mec=V_LIGHT, mew=0.7, zorder=3)
    m = np.array(ps["mean"]); xo = dts * off[lv]
    for x, (lo, hi) in zip(xo, ps["ci95"]):
        axC.plot([x, x], [lo, hi], color=V, lw=0.7, zorder=4)
    axC.plot(xo, m, ls="none", marker=MARK[lv], ms=3.0, mfc=V, mec=V, zorder=5)
c3 = np.array(d5["C3_rvo2"]["mean"])
axC.plot(dts, c3, color=B, lw=0.8, marker="D", ms=2.5, zorder=6)
axC.set_xscale("log"); axC.set_yscale("log")
axC.set_xlim(0.0042, 0.024)
axC.set_xticks(dts); axC.set_xticklabels(["0.005", "0.01", "0.02"])
axC.minorticks_off()
axC.set_ylim(0.05, 6)
axC.set_yticks([0.1, 0.3, 1, 3]); axC.set_yticklabels(["0.1", "0.3", "1", "3"])
axC.set_xlabel(r"time step $\Delta t$ (s)")
axC.set_ylabel(r"rate / rate at $\Delta t=0.01$ s")

save(fig, "fig_escape_dt")
qa("fig_escape_dt")
