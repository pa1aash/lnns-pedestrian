"""Shared static machinery for B5 (rounded jamb ends) and B6 (line goal) on the E7b pair library.

PairRest(snap, edge, goal, sign)
    The code's C1 rest-state force on the two members of a pair snapshot (v = 0, density frozen at the
    snapshot value, the snapshot's params = CF union {B_w: 0.04}, other agents inactive), the force of
    experiments/lib/pairlib.relax and experiments/runs3/N6.Field, evaluated on a two-agent copy of the
    state (identical forces, checked by check_reduced). Options:
      edge  "sharp" (published door) | "rounded" (BottleneckScenario edge="rounded", r_c = 0.1 m: each jamb
            a capsule of radius r_c around the segment x = 10 + r_c, room-side face x = 10, semicircular door
            edge, clear width unchanged; the wall law A_w exp((r - d)/B_w) with d the distance to the capsule
            surface and B_w = 0.04 m on every wall, the same law as on the sharp walls);
      goal  "point" (g = (11, 5)) | "line" (w2_goal = "line": goal = nearest point of x = 11,
            y in [5 - w/2 + r_i, 5 + w/2 - r_i], recomputed at every evaluation as Simulation.step does);
      b     lateral bias w2_noise = lateral_bias, w2_bias_b = sign * b.
    F(X, b), J(X, b) (central differences, h = 1e-7 m), Fb(X, b): the interface of runs3/N6.py, so its
    continuation, fold refinement, Newton and work routines apply unchanged.
relax(f, X0, b)       pairlib.relax on this force: dx/dt = (tau_i/m_i) F_i, Euler 0.01 s, up to 120 s; freed if a
                      member reaches x > 10.3 m, held if max |F| < 0.05 N, else undecided.
geometry(f, X)        per member: surface gap to every wall within 0.5 m (capsule radius subtracted), the
                      unclipped projection parameter t of the closest point on the wall's segment (t >= 1 on the
                      lower jamb / t <= 0 on the upper jamb: the closest point is the door-edge end, i.e. the
                      round cap for edge = rounded, the corner for sharp); pair surface gap.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402,F401  (paths; w2lib chdirs to code/)
import numpy as np  # noqa: E402
import pairlib  # noqa: E402
from sim.core.agent import AgentState  # noqa: E402

H = 1e-7
RC = 0.1


class PairRest:
    def __init__(self, snap, sign=1, edge="sharp", goal="point", edge_radius=RC):
        st = snap["state"]
        self.ids = pairlib.residual_ids(snap)
        k = np.array(self.ids)
        self.st = AgentState(st.positions[k].copy(), np.zeros((2, 2)), st.goals[k].copy(), st.radii[k].copy(),
                             st.desired_speeds[k].copy(), st.masses[k].copy(), st.taus[k].copy(),
                             np.ones(2, bool))
        self.k = np.array([0, 1])
        self.X_snap = st.positions[k].ravel().copy()
        self.sign, self.edge, self.goal = sign, edge, goal
        self.base = dict(snap["params"])
        self.scen = pairlib.BottleneckScenario(1, snap["width"], edge=edge, edge_radius=edge_radius)
        self.world, _ = self.scen.build(seed=0)
        self.dens = pairlib.snapshot_rho(snap, self.ids).astype(float)
        self.nl = [[1], [0]]
        self.gain = (self.st.taus / self.st.masses)[:, None]
        self._hm = {}
        self.n_eval = 0

    def model(self, b):
        key = round(b, 15)
        if key not in self._hm:
            if len(self._hm) > 64:
                self._hm.clear()
            p = dict(self.base)
            if b != 0.0:
                p.update({"w2_noise": "lateral_bias", "w2_bias_b": self.sign * b})
            self._hm[key] = pairlib.HybridSteeringModel(pairlib.get_config("C1"), p)
        return self._hm[key]

    def F(self, X, b):
        self.n_eval += 1
        self.st.positions[:] = X.reshape(-1, 2)
        if self.goal == "line":
            self.st.goals = self.scen.line_goals(self.st)
        return self.model(b).compute_forces(self.st, self.nl, self.world.walls, self.dens).ravel()

    def J(self, X, b):
        n = len(X)
        M = np.zeros((n, n))
        for a in range(n):
            e = np.zeros(n); e[a] = H
            M[:, a] = (self.F(X + e, b) - self.F(X - e, b)) / (2 * H)
        return M

    def Fb(self, X, b):
        hb = 1e-8
        return (self.F(X, b + hb) - self.F(X, max(b - hb, 0.0))) / (b + hb - max(b - hb, 0.0))


def check_reduced(snap):
    """max |F_reduced - F_full| at the snapshot (sharp, point goal, b = 0), full = pairlib.code_force."""
    f = PairRest(snap)
    full = pairlib.code_force(snap, f.ids, pairlib.PairField(snap, f.ids))
    return float(np.abs(f.F(f.X_snap, 0.0).reshape(-1, 2) - full).max())


def relax(f, X0, b=0.0, T=120.0, h=0.01):
    X = X0.reshape(-1, 2).copy()
    t = 0.0
    while t < T - 1e-9:
        F = f.F(X.ravel(), b).reshape(-1, 2)
        if np.abs(F).max() < 0.05:
            return {"pred_freed": False, "t": t, "X": X.ravel()}
        X += h * f.gain * F
        t += h
        out = np.where(X[:, 0] > 10.3)[0]
        if len(out):
            return {"pred_freed": True, "t": t, "first": int(out[0]),
                    "first_side": "lower" if out[0] == 0 else "upper", "X": X.ravel()}
    return {"pred_freed": None, "t": t, "X": X.ravel(), "maxF": float(np.abs(F).max())}


def geometry(f, X):
    P = X.reshape(-1, 2)
    r = f.st.radii
    out = []
    for m, p in enumerate(P):
        near = []
        for w, wall in enumerate(f.world.walls):
            ab = wall.end - wall.start
            t = float((p - wall.start) @ ab / max(ab @ ab, 1e-12))
            q = wall.start + min(max(t, 0.0), 1.0) * ab
            d = float(np.linalg.norm(p - q)) - float(wall.radius)
            if d - r[m] < 0.5:
                near.append({"wall": w, "gap": d - float(r[m]), "t": t})
        out.append(near)
    return {"walls": out, "pair_gap": float(np.linalg.norm(P[1] - P[0]) - r[0] - r[1])}


def at_end(geom, tol=1e-3, gap_max=0.2):
    """A member whose closest point on a wall within gap_max is that segment's end (t <= tol or t >= 1 - tol)."""
    return any(w["t"] <= tol or w["t"] >= 1 - tol for m in geom["walls"] for w in m if w["gap"] < gap_max)


def rest_checks(f, X):
    """Strict-minimum and standoff checks at an equilibrium X (b = 0, where the force is a gradient):
    Hessian = -sym(J) eigenvalues, asymmetry of J, contact-free (all wall gaps and the pair gap > 0),
    both members before the door plane (x < 10), on opposite sides of the axis, front of jambs
    (9.3 < x < 10, 0.25 < |y - 5| < 0.75, the E7b_lib rule)."""
    J = f.J(X, 0.0)
    Hs = -0.5 * (J + J.T)
    ev, V = np.linalg.eigh(Hs)
    g = geometry(f, X)
    P = X.reshape(-1, 2)
    dy = P[:, 1] - 5.0
    wall_gap = min([w["gap"] for m in g["walls"] for w in m] + [1.0])
    return {"eig": ev.tolist(), "strict_min": bool(ev[0] > 0), "asym": float(np.abs(J - J.T).max() / np.abs(J).max()),
            "soft_vec": V[:, 0].tolist(), "min_wall_gap": float(wall_gap), "pair_gap": g["pair_gap"],
            "contact_free": bool(wall_gap > 0 and g["pair_gap"] > 0), "before_door": bool((P[:, 0] < 10.0).all()),
            "opposite": bool(dy[0] * dy[1] < 0),
            "front_of_jambs": bool(all(9.3 < p[0] < 10.0 and 0.25 < abs(d) < 0.75 for p, d in zip(P, dy))),
            "at_segment_end": at_end(g), "geom": g}


def equilibrate(f, X0, b=0.0):
    """relax from X0, then Newton polish (runs3/N6.newton_X); returns (X, relax result, newton ok)."""
    import N6
    r = relax(f, X0, b)
    if r["pred_freed"]:
        return r["X"], r, False
    X, ok = N6.newton_X(f, r["X"], b)
    return X, r, bool(ok)
