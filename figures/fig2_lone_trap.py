"""Fig 2: lone-trap physics. Runs from figures/data/fig2.json (see tools/build_fig2_cache.py)."""
import json

import matplotlib.pyplot as plt
import numpy as np

from common import ARM_COLOURS, HERE, fig_full, save, qa

d = json.load(open(HERE / "data" / "fig2.json"))
m = d["m_kg"]
C1, C3 = ARM_COLOURS["C1"], ARM_COLOURS["C3 RVO2"]
GREY = "#3a3a3a"

fig = fig_full(4.9)
axL, axR = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1]})

# ---- left: backward wall force vs distance to the door plane
for q, ls, lw in zip(("0.20", "0.25", "0.30", "0.35"),
                     (":", "-.", "--", "-"), (1.1, 0.9, 0.9, 0.9)):
    p = d["profiles"][q]
    axL.plot(p["d_m"], p["F_back_N"], color=GREY, ls=ls, lw=lw, zorder=3)
# rest-drive bands (5th-95th percentile of the spawned agents) with their medians: SFM as a grey fill,
# force-coupled ORCA (RVO2) as blue hatching, so the two read apart in greyscale
q = d["drive_C1_N"]
axL.axhspan(q["p5"], q["p95"], facecolor="0.86", edgecolor="none", lw=0, zorder=1)
axL.axhline(q["p50"], color=C1, lw=0.9, zorder=2)
q = d["drive_C3_N"]
plt.rcParams["hatch.linewidth"] = 0.35
axL.axhspan(q["p5"], q["p95"], facecolor="none", edgecolor=C3, hatch="//////", lw=0, zorder=1)
axL.axhline(q["p50"], color=C3, lw=0.9, zorder=2)
axL.set_xlim(-0.6, 0.05)
axL.set_ylim(0, 620)
axL.set_xticks([-0.6, -0.4, -0.2, 0])
axL.set_yticks([0, 150, 300, 450, 600])
axL.set_xlabel(r"distance to door plane $x-10$ (m)")
axL.set_ylabel(r"backward wall force (N)")

# ---- right: (r, v0/tau) plane
R0, R1, Y0, Y1 = 0.15, 0.37, 0.8, 5.6
bd = d["boundary"]; br = np.array(bd["r_m"])
c1 = np.array(bd["C1"])
# stuck side of the SFM margin-zero line (margin g_max(r) - m v0/tau > 0: below the line), lightly shaded
axR.fill_between(br, Y0 - 1, c1, color="0.90", lw=0, zorder=0)
# spawned agents: a random subsample of 2000 at 30 % opacity
a = d["agents"]
ra, ya = np.array(a["r_m"]), np.array(a["v0_ms"]) / np.array(a["tau_s"])
idx = np.random.default_rng(7).choice(len(ra), 2000, replace=False)
axR.scatter(ra[idx], ya[idx], s=0.9, c="black", lw=0, alpha=0.30, rasterized=True, zorder=1)
# force-coupled ORCA (RVO2) margin-zero lines: tau = 0.4 s upper, tau = 0.6 s lower
for k in ("tau=0.4", "tau=0.6"):
    axR.plot(br, bd["C3"][k], color=C3, lw=0.9, zorder=3)
axR.plot(br, c1, color=C1, lw=1.2, zorder=4)
axR.set_xlim(R0, R1); axR.set_ylim(Y0, Y1)
axR.set_xticks([0.15, 0.20, 0.25, 0.30, 0.35])
axR.set_yticks([1, 2, 3, 4, 5])
axR.set_xlabel(r"agent radius $r$ (m)")
axR.set_ylabel(r"$v_0/\tau$ (m/s$^2$)")
for ax in (axL, axR):
    ax.spines[["top", "right"]].set_visible(True)

save(fig, "fig2_lone_trap")
qa("fig2_lone_trap")
