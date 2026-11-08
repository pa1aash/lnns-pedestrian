"""Fig 5: the time-step signature. Runs from figures/data/fig5.json (written by experiments/E3/analyze.py)."""
import json

import matplotlib.colors as mc
import numpy as np

from common import ARM_COLOURS, HERE, fig_half, qa, save

d = json.load(open(HERE / "data" / "fig5.json"))
V = ARM_COLOURS["noise"]
V_LIGHT = mc.to_hex(0.55 * np.array(mc.to_rgb(V)) + 0.45)
B = ARM_COLOURS["C3 RVO2"]
MARK = {"b1p5": "o", "b2p5": "s"}
dts = np.array(d["dts"])
grid = np.array(d["grid"])

fig = fig_half(5.6)
ax = fig.subplots()
ax.axhline(1.0, color="0.85", lw=0.5, zorder=0)

off = {"b1p5": 0.965, "b2p5": 1.035}
for lv in ("b1p5", "b2p5"):
    ps, ds = d["per_step"][lv], d["dt_scaled"][lv]
    ax.plot(grid, ps["pred"], color=V, lw=0.7, zorder=2)
    # dt-scaled noise: light vermilion, open markers
    m = np.array(ds["mean"])
    ax.plot(dts * off[lv] ** -1, m, color=V_LIGHT, lw=0.8, zorder=2)
    for x, (lo, hi) in zip(dts * off[lv] ** -1, ds["ci95"]):
        ax.plot([x, x], [lo, hi], color=V_LIGHT, lw=0.8, zorder=2)
    ax.plot(dts * off[lv] ** -1, m, ls="none", marker=MARK[lv], ms=3.2, mfc="white", mec=V_LIGHT, mew=0.8, zorder=3)
    # per-step noise: vermilion, filled markers
    m = np.array(ps["mean"])
    for x, (lo, hi) in zip(dts * off[lv], ps["ci95"]):
        ax.plot([x, x], [lo, hi], color=V, lw=0.8, zorder=4)
    ax.plot(dts * off[lv], m, ls="none", marker=MARK[lv], ms=3.4, mfc=V, mec=V, zorder=5)

c3 = np.array(d["C3_rvo2"]["mean"])
ax.plot(dts, c3, color=B, lw=0.9, marker="D", ms=2.8, zorder=6)

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(0.0042, 0.024)
ax.set_xticks(dts)
ax.set_xticklabels(["0.005", "0.01", "0.02"])
ax.minorticks_off()
ax.set_ylim(0.05, 6)
ax.set_yticks([0.1, 0.3, 1, 3])
ax.set_yticklabels(["0.1", "0.3", "1", "3"])
ax.set_xlabel(r"time step $\Delta t$ (s)")
ax.set_ylabel(r"escape rate / rate at $\Delta t = 0.01$ s")

save(fig, "fig5_dt")
qa("fig5_dt")
