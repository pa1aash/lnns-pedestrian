"""Fig. geometry: to-scale schematic of the two simulation geometries.

Left: the room bottleneck (BottleneckScenario, w = 0.8 m) with an enlarged door-region inset.
Right: the rebuilt CroMa entrance (CromaBottleneckScenario, w = 0.8 m, corridor L = 2.0 m as in two of the five runs; the dotted line J marks the 0.2 m
bottleneck of the other three, the code default and the archive value).
The wall segments, door edges and goals are taken from the scenario builders in code/sim, the
goal capture radius from code/config/params.yaml, the B_w,edge zone from WallForces.edge_zone and
the waiting zone from experiments/pilot/w28_croma.py (fluct). Both main panels share one scale.
Letter keys are defined in the caption."""
import sys

import numpy as np
import yaml
from matplotlib.patches import Circle, Rectangle

from common import CM, HERE, fig_full, qa, save

sys.path.insert(0, str(HERE.parent / "code"))
from sim.scenarios.bottleneck import BottleneckScenario  # noqa: E402
from sim.scenarios.croma import CromaBottleneckScenario  # noqa: E402
from sim.steering.walls import WallForces  # noqa: E402

PARAMS = yaml.safe_load(open(HERE.parent / "code" / "config" / "params.yaml"))
R_GOAL = PARAMS["simulation"]["goal_reached_dist"]          # exit at |x - g| < 0.5 m
Z0, Z1 = WallForces().edge_zone                               # B_w,edge within 0.5 m, blended to B_w by 1.0 m
R_AGENT = PARAMS["agent"]["radius"]                           # mean radius 0.25 m
L_CROMA = 2.0                                                 # long-corridor CroMa runs (4D030, 4D040)
L_SHORT = CromaBottleneckScenario().length                    # code default; the Part D rerun and the archive use 0.2 m
assert abs(L_SHORT - 0.2) < 1e-12
WZ = (0.3, 2.5, 2.0)                                          # waiting zone: 0.3 < x_e - x < 2.5, |y - y_c| < 2

room, room_state = BottleneckScenario(n_agents=1, exit_width=0.8).build(seed=0)
croma_sc = CromaBottleneckScenario(n_agents=1, exit_width=0.8, length=L_CROMA)
croma, croma_state = croma_sc.build(seed=0)
g_room = room_state.goals[0]
g_croma = croma_state.goals[0]

WALL = dict(color="black", lw=1.0, solid_capstyle="butt", zorder=4)
THIN = dict(color="black", lw=0.6)
GREY_L, GREY_M = "0.86", "0.55"
KEY = dict(fontsize=8, ha="center", va="center", zorder=6)

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


def goal(ax, g):
    ax.add_patch(Circle(g, R_GOAL, fc=GREY_L, ec="black", lw=0.6, ls=(0, (2, 1.5)), zorder=2))
    ax.plot(*g, marker="+", ms=4, mew=0.6, color="black", zorder=3)


def scalebar(ax, x0, y0, length, label, tick=0.18, above=False):
    ax.plot([x0, x0 + length], [y0, y0], color="black", lw=1.0, solid_capstyle="butt")
    for x in (x0, x0 + length):
        ax.plot([x, x], [y0 - tick, y0 + tick], **THIN)
    if above:
        ax.text(x0 + length / 2, y0 + 2 * tick, label, fontsize=7, ha="center", va="bottom")
    else:
        ax.text(x0 + length + 0.25, y0, label, fontsize=7, ha="left", va="center")


# ---------------------------------------------------------------- left: room bottleneck
axR, x_end = axes_at(0.0, XL_ROOM)
walls(axR, room)
goal(axR, g_room)
edges = [w.door_edge for w in room.walls if w.door_edge is not None]       # (10, 4.6), (10, 5.4)
axR.text(9.48, 5.0, "A", **KEY)                                             # door
axR.text(g_room[0], g_room[1] + R_GOAL + 0.45, "B", **KEY)                 # goal + capture disc
scalebar(axR, 0.0, -0.55, 2.0, "2\\,m")

# inset: door region, magnified
IX, IY = (9.0, 10.6), (3.35, 6.65)
axR.add_patch(Rectangle((IX[0], IY[0]), IX[1] - IX[0], IY[1] - IY[0], fill=False, lw=0.5, ec="0.35", zorder=5))
MAG = 2.6
ins_x0, ins_y0 = 0.7, 5.0 - (IY[1] - IY[0]) * MAG / 2       # inset placed inside the room (data metres)
pos = axR.transData.transform  # placement in figure fraction via data coordinates of axR
fx0, fy0 = fig.transFigure.inverted().transform(pos((ins_x0, ins_y0)))
fx1, fy1 = fig.transFigure.inverted().transform(pos((ins_x0 + (IX[1] - IX[0]) * MAG, ins_y0 + (IY[1] - IY[0]) * MAG)))
axI = fig.add_axes([fx0, fy0, fx1 - fx0, fy1 - fy0])
# thin connectors from the outlined door region to the inset's right-hand corners (magnification cue)
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

# B_w,edge zone along each jamb face (room side): closest wall point within Z0 of the door edge,
# blended linearly to B_w at Z1 (walls.py: s_edge, edge_zone). Drawn as a strip on the face.
STRIP = 0.10
for w in room.walls:
    if w.door_edge is None:
        continue
    e = w.door_edge
    far = w.start if np.allclose(e, w.end) else w.end
    u = (far - e) / np.linalg.norm(far - e)                                 # along the jamb, away from the edge
    sgn = u[1]
    axI.add_patch(Rectangle((e[0] - STRIP, min(e[1], e[1] + sgn * Z0)), STRIP, Z0,
                            fc=GREY_M, ec="none", zorder=2))
    nstep = 24
    for k in range(nstep):
        s0 = Z0 + (Z1 - Z0) * k / nstep
        lev = 0.55 + 0.45 * (k + 0.5) / nstep
        axI.add_patch(Rectangle((e[0] - STRIP, min(e[1] + sgn * s0, e[1] + sgn * (s0 + (Z1 - Z0) / nstep))),
                                STRIP, (Z1 - Z0) / nstep, fc=str(lev), ec="none", zorder=2))
    # thin boundary ticks at s = Z0 and s = Z1
    for s in (Z0, Z1):
        axI.plot([e[0] - STRIP - 0.06, e[0]], [e[1] + sgn * s] * 2, color="0.35", lw=0.4, zorder=3)
for w in room.walls:
    axI.plot([w.start[0], w.end[0]], [w.start[1], w.end[1]], **WALL)
for e in edges:
    axI.plot(*e, marker="o", ms=2.6, mfc="white", mec="black", mew=0.6, zorder=5)
# one agent of radius 0.25 m on the door axis, to scale
axI.add_patch(Circle((9.70, 5.0), R_AGENT, fc="white", ec="black", lw=0.6, zorder=4))
axI.add_patch(Circle(g_room, R_GOAL, fc=GREY_L, ec="black", lw=0.6, ls=(0, (2, 1.5)), zorder=1))

axI.text(10.30, 5.75, "C", **KEY)
axI.plot([10.04, 10.20], [5.43, 5.65], **THIN)
axI.text(9.62, 4.35, "D", **KEY)
axI.text(9.62, 3.85, "E", **KEY)
axI.text(9.70, 5.0, "F", **KEY)
scalebar(axI, 9.15, 6.15, 0.5, "0.5\\,m", tick=0.05, above=True)

# ---------------------------------------------------------------- right: CroMa entrance
axC, _ = axes_at(x_end + 0.15, XL_CROMA)
x_e, y_c = 10.0, 5.0
axC.add_patch(Rectangle((x_e - WZ[1], y_c - WZ[2]), WZ[1] - WZ[0], 2 * WZ[2],
                        fc=GREY_L, ec="0.35", lw=0.5, zorder=1))
walls(axC, croma)
goal(axC, g_croma)
junc = [P for P, _m in WallForces.shared_endpoints(croma.walls)
        if abs(P[0] - 10.0) < 1e-9 and abs(P[1] - 5.0) < 1.0]               # door edges (convex corners)
for P in junc:
    axC.plot(*P, marker="o", ms=2.6, mfc="white", mec="black", mew=0.6, zorder=5)
x0 = 10.0 - croma_sc.D
axC.text(x0 + 1.3, 5.0 + croma_sc.H / 2 - 0.9, "G", **KEY)                 # holding area
axC.text(x_e - 1.4, y_c, "H", **KEY)                                        # waiting zone
axC.text(x_e + L_CROMA / 2, y_c + 0.4 + 0.45, "I", **KEY)                  # corridor
axC.text(x_e + 0.45, y_c - 0.4 - 0.75, "C", **KEY)                          # door edges = convex junctions
axC.plot([x_e + 0.05, x_e + 0.32], [y_c - 0.45, y_c - 0.95], **THIN)
axC.text(g_croma[0], g_croma[1] + R_GOAL + 0.45, "B", **KEY)
axC.plot([x_e + L_SHORT] * 2, [y_c - 0.4 - 0.25, y_c + 0.4 + 1.45], color="black", lw=0.6, ls=(0, (1.5, 1.5)), zorder=3)
axC.text(x_e + L_SHORT, y_c + 0.4 + 1.45 + 0.4, "J", **KEY)                 # end of the 0.2 m bottleneck (3 of 5 runs)
scalebar(axC, x0, -0.55, 2.0, "2\\,m")

save(fig, "fig_geometry")
qa("fig_geometry")
