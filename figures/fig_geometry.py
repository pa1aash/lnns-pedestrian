"""Fig. geometry: to-scale schematic of the two simulation geometries, labelled directly.

Left: the room bottleneck (BottleneckScenario, w = 0.8 m) with its spawn rectangle and an
enlarged door-region inset (door edges, B_w,edge zone and blend zone on the jambs, one agent).
Right: the rebuilt CroMa entrance (CromaBottleneckScenario, w = 0.8 m, corridor L = 2.0 m as in
runs 4D030/4D040; the dotted line marks the 0.2 m bottleneck of 4D110/4D120/4D130, the code
default), the waiting zone, and (dashed) the wall of the experiment from the archive polygon of
4D030/4D040 (rev_D.json archive_geometry): straight 2.0 m slot face, a 1 m thick front wall
over the first metre, then the outer face tapers to the slot end.
Sources: wall segments, door edges, goals and spawn area from the scenario builders in code/sim;
goal capture radius and agent radius from code/config/params.yaml; B_w,edge zone from
WallForces.edge_zone; waiting zone from experiments/pilot/w28_croma.py (fluct, sim). Every
dimension printed in the figure is asserted against these sources. Both main panels share one
scale."""
import inspect
import json
import re
import sys

import numpy as np
import yaml
from matplotlib.patches import Circle, Rectangle

from common import HERE, fig_full, qa, save

ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "code"))
from sim.scenarios import bottleneck as _bn_mod  # noqa: E402
from sim.scenarios.bottleneck import BottleneckScenario  # noqa: E402
from sim.scenarios.croma import CromaBottleneckScenario  # noqa: E402
from sim.steering.walls import WallForces  # noqa: E402

PARAMS = yaml.safe_load(open(ROOT / "code" / "config" / "params.yaml"))
R_GOAL = PARAMS["simulation"]["goal_reached_dist"]          # exit at |x - g| < 0.5 m
Z0, Z1 = WallForces().edge_zone                               # B_w,edge within 0.5 m, blended to B_w by 1.0 m
R_AGENT = PARAMS["agent"]["radius"]                           # mean radius 0.25 m
W_DOOR = 0.8
L_CROMA = 2.0                                                 # long-corridor CroMa runs (4D030, 4D040)
L_SHORT = CromaBottleneckScenario().length                    # code default; the Part D rerun and the archive use 0.2 m
D_HOLD, H_HOLD = CromaBottleneckScenario.D, CromaBottleneckScenario.H

# ---------------------------------------------------------------- checks: printed numbers vs code
assert abs(L_SHORT - 0.2) < 1e-12
assert (D_HOLD, H_HOLD) == (7.8, 8.6), (D_HOLD, H_HOLD)       # printed "7.8 m", "8.6 m"
assert abs(R_GOAL - 0.5) < 1e-12 and abs(R_AGENT - 0.25) < 1e-12
assert np.allclose((Z0, Z1), (0.5, 1.0))
SPAWN = (1.0, 8.0, 1.0, 9.0)                                  # room spawn rectangle x0, x1, y0, y1
assert inspect.getsource(_bn_mod).count("(1.0, 8.0, 1.0, 9.0)") == 2   # spawn_area and respawn_rejection
# waiting zone: x_e - 2.5 < x < x_e - 0.3, |y - y_c| < 2 (w28_croma.fluct), entrance (10, 5) in sim()
_w28 = (ROOT / "experiments" / "pilot" / "w28_croma.py").read_text()
assert "zone = (dx > 0.3) & (dx < 2.5) & (np.abs(P[:, 1] - y_c) < 2.0)" in _w28
assert "fluct(tracks_from_rows(ids, fr, D[:, 2], D[:, 3]), 10.0, 5.0)" in _w28
WZ = (0.3, 2.5, 2.0)                                          # printed "2.2 m" x "4.0 m"


# archive polygons (CroMa frame: entrance x = 0, axis y = 0) -> model frame (+10, +5)
def _rings(wkt):
    return [np.array([[float(v) for v in p.split()] for p in r.split(",")])
            for r in re.findall(r"\(([^()]+)\)", wkt)]


ARCH = json.load(open(ROOT / "data" / "derived" / "rev_D.json"))["archive_geometry"]
assert ARCH["4D030"] == ARCH["4D040"]
OBST = [r + (10.0, 5.0) for r in _rings(ARCH["4D030"])[1:]]   # the two obstacles (upper, lower)
for r in OBST:                                                 # slot face y = 5 -+ 0.4 over x in [10, 12]
    face = r[np.isclose(np.abs(r[:, 1] - 5.0), W_DOOR / 2)]
    assert np.isclose(face[:, 0].min(), 10.0) and np.isclose(face[:, 0].max(), 10.0 + L_CROMA)
for k in ("4D110", "4D120", "4D130"):
    for r in _rings(ARCH[k])[1:]:
        face = r[np.isclose(np.abs(r[:, 1]), W_DOOR / 2)]
        assert np.isclose(face[:, 0].max(), L_SHORT)

room, room_state = BottleneckScenario(n_agents=1, exit_width=W_DOOR).build(seed=0)
croma_sc = CromaBottleneckScenario(n_agents=1, exit_width=W_DOOR, length=L_CROMA)
croma, croma_state = croma_sc.build(seed=0)
g_room = room_state.goals[0]
g_croma = croma_state.goals[0]

WALL = dict(color="black", lw=1.0, solid_capstyle="butt", zorder=4)
THIN = dict(color="black", lw=0.5)
DIM = dict(color="0.3", lw=0.4)
GREY_L, GREY_M = "0.86", "0.55"
FS = 7
LAB = dict(fontsize=FS, zorder=7)
BG = dict(boxstyle="square,pad=0.08", fc="white", ec="none")

# ---------------------------------------------------------------- layout (cm, one scale)
S = 0.5                                       # cm per metre in both main panels
YL = (-0.9, 10.3)                             # shared y range (m)
XL_ROOM = (-0.3, 11.75)
XL_CROMA = (10.0 - croma_sc.D - 0.2, 10.0 + L_CROMA + 1.0 + R_GOAL + 0.15)
W_CM, H_CM = 12.2, (YL[1] - YL[0]) * S + 0.1
fig = fig_full(H_CM)
fig.set_layout_engine("none")


def axes_at(x_cm, xl):
    w = (xl[1] - xl[0]) * S
    ax = fig.add_axes([x_cm / W_CM, 0.05 / H_CM, w / W_CM, (YL[1] - YL[0]) * S / H_CM])
    ax.set_xlim(*xl)
    ax.set_ylim(*YL)
    ax.set_aspect("equal")
    ax.set_axis_off()
    return ax, x_cm + w


def walls(ax, world):
    for w in world.walls:
        ax.plot([w.start[0], w.end[0]], [w.start[1], w.end[1]], **WALL)


def goal(ax, g, zorder=2):
    ax.add_patch(Circle(g, R_GOAL, fc=GREY_L, ec="black", lw=0.6, ls=(0, (2, 1.5)), zorder=zorder))
    ax.plot(*g, marker="+", ms=4, mew=0.6, color="black", zorder=zorder + 1)


def scalebar(ax, x0, y0, length, label, tick=0.18):
    ax.plot([x0, x0 + length], [y0, y0], color="black", lw=1.0, solid_capstyle="butt")
    for x in (x0, x0 + length):
        ax.plot([x, x], [y0 - tick, y0 + tick], **THIN)
    ax.text(x0 + length + 0.25, y0, label, ha="left", va="center", **LAB)


def dim(ax, p0, p1, label, tick=0.15, rot=0, text_at=0.5):
    """Dimension line p0-p1 with end ticks and the label on the line (white gap)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    ax.plot(*np.c_[p0, p1], **DIM, zorder=5)
    n = np.array([-(p1 - p0)[1], (p1 - p0)[0]]) / np.linalg.norm(p1 - p0)
    for p in (p0, p1):
        ax.plot(*np.c_[p - tick * n, p + tick * n], **DIM, zorder=5)
    c = p0 + text_at * (p1 - p0)
    ax.text(*c, label, ha="center", va="center", rotation=rot, bbox=BG, **LAB)


def ext(ax, x0, y0, x1, y1):
    ax.plot([x0, x1], [y0, y1], **DIM, zorder=5)


# ---------------------------------------------------------------- left: room bottleneck
axR, x_end = axes_at(0.0, XL_ROOM)
axR.add_patch(Rectangle((SPAWN[0], SPAWN[2]), SPAWN[1] - SPAWN[0], SPAWN[3] - SPAWN[2], fill=False,
                        ec="black", lw=0.6, ls=(0, (3, 2)), zorder=1))
walls(axR, room)
goal(axR, g_room)
axR.text(SPAWN[1] - 0.05, 0.5, "spawn", ha="right", va="center", **LAB)
scalebar(axR, 0.0, -0.55, 2.0, "2\\,m")

# inset: door region, magnified
IX, IY = (8.1, 11.5), (3.35, 6.65)
axR.add_patch(Rectangle((IX[0], IY[0]), IX[1] - IX[0], IY[1] - IY[0], fill=False, lw=0.5, ec="0.35", zorder=5))
MAG = 2.1
ins_x0, ins_y0 = 0.25, 5.0 - (IY[1] - IY[0]) * MAG / 2       # inset placed inside the room (data metres)
pos = axR.transData.transform
fx0, fy0 = fig.transFigure.inverted().transform(pos((ins_x0, ins_y0)))
fx1, fy1 = fig.transFigure.inverted().transform(pos((ins_x0 + (IX[1] - IX[0]) * MAG, ins_y0 + (IY[1] - IY[0]) * MAG)))
axI = fig.add_axes([fx0, fy0, fx1 - fx0, fy1 - fy0])
ix1 = ins_x0 + (IX[1] - IX[0]) * MAG
for yi, yo in ((ins_y0, IY[0]), (ins_y0 + (IY[1] - IY[0]) * MAG, IY[1])):
    axR.plot([ix1, IX[0]], [yi, yo], color="0.6", lw=0.4, zorder=4)
axI.set_xlim(*IX)
axI.set_ylim(*IY)
axI.set_aspect("equal")
axI.set_xticks([])
axI.set_yticks([])
for sp in axI.spines.values():
    sp.set_visible(True)
    sp.set_linewidth(0.5)
    sp.set_edgecolor("0.35")
axI.set_facecolor("white")
axI.set_zorder(6)

# B_w,edge zone along each jamb face (room side): closest wall point within Z0 of the door edge,
# blended linearly to B_w at Z1 (walls.py: s_edge, edge_zone). Drawn as a strip on the face.
STRIP = 0.10
for w in room.walls:
    if w.door_edge is None:
        continue
    e = w.door_edge
    far = w.start if np.allclose(e, w.end) else w.end
    sgn = ((far - e) / np.linalg.norm(far - e))[1]                          # along the jamb, away from the edge
    axI.add_patch(Rectangle((e[0] - STRIP, min(e[1], e[1] + sgn * Z0)), STRIP, Z0,
                            fc=GREY_M, ec="none", zorder=2))
    nstep = 24
    for k in range(nstep):
        s0 = Z0 + (Z1 - Z0) * k / nstep
        lev = 0.55 + 0.45 * (k + 0.5) / nstep
        axI.add_patch(Rectangle((e[0] - STRIP, min(e[1] + sgn * s0, e[1] + sgn * (s0 + (Z1 - Z0) / nstep))),
                                STRIP, (Z1 - Z0) / nstep, fc=str(lev), ec="none", zorder=2))
    for s in (Z0, Z1):
        axI.plot([e[0] - STRIP - 0.06, e[0]], [e[1] + sgn * s] * 2, color="0.35", lw=0.4, zorder=3)
for w in room.walls:
    axI.plot([w.start[0], w.end[0]], [w.start[1], w.end[1]], **WALL)
edges = sorted((w.door_edge for w in room.walls if w.door_edge is not None), key=lambda e: e[1])
assert np.isclose(edges[1][1] - edges[0][1], W_DOOR)
for e in edges:
    axI.plot(*e, marker="o", ms=2.6, mfc="white", mec="black", mew=0.6, zorder=5)
goal(axI, g_room, zorder=1)
A_X = 9.72                                                                  # one agent of radius 0.25 m, to scale
axI.add_patch(Circle((A_X, 5.0), R_AGENT, fc="white", ec="black", lw=0.6, zorder=4))

xe, ylo, yhi = edges[0][0], edges[0][1], edges[1][1]
xl = xe - STRIP - 0.12                                                      # right end of the jamb labels
axI.text(xl, ylo - Z0 / 2, "$B_{w,\\mathrm{edge}}$", ha="right", va="center", **LAB)
axI.text(xl, ylo - (Z0 + Z1) / 2, "blend", ha="right", va="center", **LAB)
axI.text(A_X - R_AGENT - 0.08, 5.0, "agent\n$r = 0.25$\\,m", ha="right", va="center", linespacing=1.0, **LAB)
axI.text(xl - 0.05, yhi + 0.42, "door edge", ha="right", va="center", **LAB)
axI.plot([xl - 0.02, xe - 0.035], [yhi + 0.33, yhi + 0.04], **THIN)
dim(axI, (xe + 0.13, ylo), (xe + 0.13, yhi), "", tick=0.06)                 # door width
axI.text(xe + 0.30, 5.0, "0.8\\,m", rotation=90, ha="center", va="center", **LAB)
axI.text(g_room[0], g_room[1] + R_GOAL + 0.08, "goal", ha="center", va="bottom", **LAB)
axI.text(g_room[0], g_room[1] - R_GOAL - 0.06, "capture\ndisc", ha="center", va="top", linespacing=1.0, **LAB)
scalebar(axI, IX[0] + 0.12, IY[1] - 0.22, 0.5, "0.5\\,m", tick=0.05)

# ---------------------------------------------------------------- right: CroMa entrance
axC, _ = axes_at(x_end + 0.15, XL_CROMA)
x_e, y_c = 10.0, 5.0
x0, y0, y1 = x_e - croma_sc.D, y_c - croma_sc.H / 2, y_c + croma_sc.H / 2
axC.add_patch(Rectangle((x_e - WZ[1], y_c - WZ[2]), WZ[1] - WZ[0], 2 * WZ[2],
                        fc=GREY_L, ec="0.35", lw=0.5, zorder=1))
# wall of the experiment (archive polygon of 4D030/4D040), dashed, where it departs from the model
for r in OBST:
    # ring order: front face (x = 10) -> back face -> taper -> slot face; keep all but the slot face
    path = np.array([p for p in r if not np.isclose(abs(p[1] - y_c), W_DOOR / 2) or np.isclose(p[0], 10.0 + L_CROMA)])
    axC.plot(path[:, 0], path[:, 1], color="black", lw=0.6, ls=(0, (3, 2)), zorder=3)
walls(axC, croma)
goal(axC, g_croma)
junc = [P for P, _m in WallForces.shared_endpoints(croma.walls)
        if abs(P[0] - 10.0) < 1e-9 and abs(P[1] - 5.0) < 1.0]               # door edges (convex corners)
for P in junc:
    axC.plot(*P, marker="o", ms=2.6, mfc="white", mec="black", mew=0.6, zorder=5)

axC.text(x0 + 0.75, y1 - 0.35, "holding area", ha="left", va="top", **LAB)
axC.text(x_e - (WZ[0] + WZ[1]) / 2, y_c, "waiting\nzone", ha="center", va="center", linespacing=1.0, **LAB)
axC.text(g_croma[0], g_croma[1] + R_GOAL + 0.12, "goal", ha="center", va="bottom", **LAB)
axC.text(11.25, 2.6, "experiment", ha="left", va="center", **LAB)
# dimensions: holding area 7.8 x 8.6 m, corridor 2.0 m (top chain), waiting zone 2.2 x 4.0 m
yd = y1 + 0.55
for x in (x0, x_e):
    ext(axC, x, y1 + 0.1, x, yd + 0.2)
ext(axC, x_e + L_CROMA, y_c + W_DOOR / 2 + 0.15, x_e + L_CROMA, yd + 0.2)
dim(axC, (x0, yd), (x_e, yd), f"{croma_sc.D:.1f}\\,m", tick=0)
dim(axC, (x_e, yd), (x_e + L_CROMA, yd), f"{L_CROMA:.1f}\\,m", tick=0)
dim(axC, (x0 + 0.4, y0), (x0 + 0.4, y1), f"{croma_sc.H:.1f}\\,m", tick=0.12, rot=90, text_at=0.4)
wz_x0, wz_x1 = x_e - WZ[1], x_e - WZ[0]
dim(axC, (wz_x0, y_c - WZ[2] - 0.4), (wz_x1, y_c - WZ[2] - 0.4), f"{WZ[1] - WZ[0]:.1f}\\,m", tick=0.12)
dim(axC, (wz_x0 - 0.4, y_c - WZ[2]), (wz_x0 - 0.4, y_c + WZ[2]), f"{2 * WZ[2]:.1f}\\,m", tick=0.12, rot=90)
# 0.2 m bottleneck of 4D110/4D120/4D130
axC.plot([x_e + L_SHORT] * 2, [y_c - W_DOOR / 2, y_c + W_DOOR / 2], color="black", lw=0.6, ls=(0, (1, 1)), zorder=3)
axC.text(x_e + L_SHORT + 0.12, y_c - 0.02, f"{L_SHORT:.1f}\\,m", ha="left", va="center", **LAB)
scalebar(axC, x0, -0.55, 2.0, "2\\,m")

save(fig, "fig_geometry")
qa("fig_geometry")
