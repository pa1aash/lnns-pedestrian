"""Shared wall endpoints (junctions) and their convex / concave status, seen from free space,
for the scenarios used in execution; CroMa door-edge forces under both corner rules.
Output: data/derived/corner_inventory.json

A junction's status is read from the free-space arcs on a circle of radius 0.05 m around P:
walls leaving P separate arcs. An arc of 90 deg is a concave corner (agent inside a room corner), 270 deg a convex corner
(agent outside a solid corner), 180 deg a flat (collinear) joint. Free space per scenario:
room bottleneck = the whole plane minus the walls (the room exterior is reachable only by
agents past the door plane); CroMa and
open geometries = complement of the scenario's outside_walkable().
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import DERIVED, REPO  # noqa: F401  (chdir into the simulator, sys.path)
import numpy as np
from sim.core.agent import AgentState
from sim.scenarios.bottleneck import BottleneckScenario
from sim.scenarios.croma import CromaBottleneckScenario
from sim.scenarios.open_geometries import OpenBidirectionalScenario, OpenCrossingScenario
from sim.steering.walls import WallForces


def room_free(pos):
    # the room's walls are zero-thickness and nothing bounds the outside, so geometrically
    # the whole plane minus the walls is free; the exterior is reachable only past the door
    return np.ones(len(pos), bool)


def arcs(P, free_fn, walls, n=3600, rad=0.05):
    a = (np.arange(n) + 0.5) * 2 * np.pi / n
    free = free_fn(P + rad * np.column_stack([np.cos(a), np.sin(a)]))
    # zero-thickness walls leaving P separate free arcs: mark the sample nearest each
    for w in walls:
        for e0, e1 in ((w.start, w.end), (w.end, w.start)):
            if np.linalg.norm(e0 - P) <= 1e-9:
                ang = np.arctan2(*(e1 - e0)[::-1]) % (2 * np.pi)
                free[int(ang / (2 * np.pi) * n) % n] = False
    if free.all():
        return [360.0]
    k0 = int(np.argmin(free))          # start the scan on a solid sample
    f = np.roll(free, -k0)
    out, run = [], 0
    for v in f:
        if v:
            run += 1
        elif run:
            out.append(run); run = 0
    if run:
        out.append(run)
    return [round(r * 360.0 / n, 1) for r in out]


def status(arc_list):
    names = {90.0: "concave", 270.0: "convex", 180.0: "flat"}
    return [names.get(float(round(a)), f"{a} deg") for a in arc_list]


def inventory(name, sc, free_fn):
    world, _ = sc.build(seed=0)
    rows = []
    for P, members in WallForces.shared_endpoints(world.walls):
        a = arcs(P, free_fn, world.walls)
        rows.append({"P": [round(float(v), 6) for v in P], "segments": [m[0] for m in members],
                     "free_arcs_deg": a, "status": status(a)})
    free_ends = []
    shared = {tuple(np.round(r["P"], 6)) for r in rows}
    for w in world.walls:
        for e in (w.start, w.end):
            if tuple(np.round(e, 6)) not in shared:
                free_ends.append([round(float(v), 6) for v in e])
    return {"scenario": name, "n_walls": len(world.walls), "junctions": rows, "free_ends": free_ends}


def axis_max_backward(world, r, corner, xs=np.linspace(9.0, 10.6, 1601)):
    n = len(xs)
    st = AgentState(np.column_stack([xs, np.full(n, 5.0)]), np.zeros((n, 2)),
                    np.tile([11.0, 5.0], (n, 1)), np.full(n, r), np.ones(n), np.full(n, 80.0),
                    np.full(n, 0.5), np.ones(n, bool))
    F = WallForces(corner=corner).compute_wall_forces(st, world.walls)
    i = int(np.argmax(-F[:, 0]))
    return {"max_backward_N": round(float(-F[i, 0]), 2), "at_x": round(float(xs[i]), 4)}


if __name__ == "__main__":
    out = {"note": __doc__, "inventory": [
        inventory("room bottleneck w=0.8", BottleneckScenario(1, 0.8), room_free),
        inventory("CroMa L=2.0", CromaBottleneckScenario(1, 0.8, length=2.0),
                  lambda p, s=CromaBottleneckScenario(1, 0.8, length=2.0): ~s.outside_walkable(p)),
        inventory("CroMa L=0.21", CromaBottleneckScenario(1, 0.8, length=0.21),
                  lambda p, s=CromaBottleneckScenario(1, 0.8, length=0.21): ~s.outside_walkable(p)),
        inventory("open bidirectional corridor", OpenBidirectionalScenario(),
                  lambda p, s=OpenBidirectionalScenario(): ~s.outside_walkable(p)),
        inventory("open crossing", OpenCrossingScenario(),
                  lambda p, s=OpenCrossingScenario(): ~s.outside_walkable(p)),
    ]}
    edge = {}
    for name, sc in (("room w=0.8", BottleneckScenario(1, 0.8)),
                     ("CroMa L=2.0", CromaBottleneckScenario(1, 0.8, length=2.0)),
                     ("CroMa L=0.21", CromaBottleneckScenario(1, 0.8, length=0.21))):
        world, _ = sc.build(seed=0)
        edge[name] = {f"r={r}": {c: axis_max_backward(world, r, c) for c in ("segment_sum", "convex_union")}
                      for r in (0.20, 0.25, 0.30, 0.35)}
    out["door_edge_axis_force"] = edge
    json.dump(out, open(os.path.join(DERIVED, "corner_inventory.json"), "w"), indent=1)
    for inv in out["inventory"]:  # noqa
        print(inv["scenario"])
        for j in inv["junctions"]:
            print("   ", j["P"], "segs", j["segments"], j["free_arcs_deg"], j["status"])
    print(json.dumps(edge, indent=1))
