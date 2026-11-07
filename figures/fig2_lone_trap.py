"""Fig 2: lone-trap physics. Runs from figures/data/fig2.json (see tools/build_fig2_cache.py)."""
import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

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
for key, col, a in (("drive_C1_N", C1, 0.18), ("drive_C3_N", C3, 0.30)):
    q = d[key]
    axL.axhspan(q["p5"], q["p95"], color=col, alpha=a, lw=0, zorder=1)
    axL.axhline(q["p50"], color=col, lw=0.9, zorder=2)
axL.set_xlim(-0.6, 0.2)
axL.set_ylim(0, 620)
axL.set_xticks([-0.6, -0.4, -0.2, 0, 0.2])
axL.set_yticks([0, 150, 300, 450, 600])
axL.set_xlabel(r"distance to door plane $x-10$ (m)")
axL.set_ylabel(r"backward wall force (N)")

# ---- right: (r, v0/tau) plane
rg = np.array(d["gmax"]["r_m"]); gm = np.array(d["gmax"]["gmax_N"])
R0, R1, Y0, Y1 = 0.15, 0.37, 0.8, 5.6
rr = np.linspace(R0, R1, 400); yy = np.linspace(Y0, Y1, 400)
G = np.interp(rr, rg, gm)[None, :] - m * yy[:, None]
axR.imshow(G, origin="lower", extent=(R0, R1, Y0, Y1), aspect="auto", cmap="cividis",
           norm=Normalize(-150, 150), interpolation="bilinear", rasterized=True, zorder=0)
a = d["agents"]
axR.scatter(a["r_m"], np.array(a["v0_ms"]) / np.array(a["tau_s"]), s=0.15, c="#ffffff",
            lw=0, alpha=0.35, rasterized=True, zorder=1)
bd = d["boundary"]; br = np.array(bd["r_m"])
lo = np.array(bd["C3"]["tau=0.6"]); hi = np.array(bd["C3"]["tau=0.4"])
axR.fill_between(br, lo, hi, color=C3, alpha=0.55, lw=0, zorder=2)
axR.plot(br, lo, color=C3, lw=0.9, zorder=3); axR.plot(br, hi, color=C3, lw=0.9, zorder=3)
axR.plot(br, bd["C1"], color=C1, lw=1.2, zorder=4)
axR.set_xlim(R0, R1); axR.set_ylim(Y0, Y1)
axR.set_xticks([0.15, 0.20, 0.25, 0.30, 0.35])
axR.set_yticks([1, 2, 3, 4, 5])
axR.set_xlabel(r"agent radius $r$ (m)")
axR.set_ylabel(r"$v_0/\tau$ (m\,s$^{-2}$)")
for ax in (axL, axR):
    ax.spines[["top", "right"]].set_visible(True)

save(fig, "fig2_lone_trap")
qa("fig2_lone_trap")
