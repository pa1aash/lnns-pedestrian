"""BAR: string-method barriers for the 60 E2 snapshots (selection rule, experiments/selection.py).

Ported from the pilot experiments/pilot/w23_barrier.py; the energy, gradient, relaxation, string
method and climbing refinement are unchanged except for two points: the agent-agent sum in U is
evaluated with numpy over the same pairs (i mobile, j > i, d_ij < 3 m) instead of a Python loop, and
(C15) every gradient step (relaxation, string images, climbing) moves each agent by at most
STEP_CAP = 2 mm. Without the cap a body overlap (k = 1.2e5 N/m) on the initial straight path gives
steps of order 0.1-1 m at alpha = 4e-5 and the string does not converge (pair snapshots with both
jambs occupied); where the cap does not bind the iteration is the pilot's.

Rest-state C1 field with density frozen at the snapshot value is conservative:
U = sum_i c_i |x_i - g| + sum_{i,w} A B exp((r_i - d_iw)/B) + sum_{i<j} A B exp((r_ij - d_ij)/B)
    (+ 0.5 k overlap^2 body terms), c_i = m v_eff,i / tau_i, g = (11, 5).
The residual max |F_code + grad U| is checked against the code's C1 force at v = 0 with the
snapshot's own (corrected-forward) parameters, as in the pilot.
Conditions per snapshot (blocker = residual agent nearest (10, 5)):
  alone        blocker only, density 0 (1-D on-axis integral and 2-D string);
  frozen       blocker mobile, other residual agents fixed, snapshot density;
  all_mobile   every residual agent mobile, snapshot density (the collective barrier, Delta U used
               by the E3 / E4 selection rules: all_mobile.dU_climb).
Output: data/BAR/barriers.jsonl (resumable, one line per snapshot), data/BAR/barriers.json.
"""
import copy
import functools
import json
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import DATA, load_runs, run_jobs, weidmann_factor  # noqa: E402
import numpy as np  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402
from sim.scenarios.bottleneck import BottleneckScenario  # noqa: E402
from sim.steering.hybrid import HybridSteeringModel  # noqa: E402
from sim.experiments.configs import get_config  # noqa: E402

A, B, K = 2000.0, 0.08, 120000.0
STEP_CAP = 0.002


def capped(d):
    """Gradient step d (flat, 2 per agent) with each agent's displacement capped at STEP_CAP."""
    v = d.reshape(-1, 2)
    n = np.linalg.norm(v, axis=1, keepdims=True)
    return (v * np.minimum(1.0, STEP_CAP / np.maximum(n, 1e-300))).ravel()
G = np.array([11.0, 5.0])
OUTD = os.path.join(DATA, "BAR")
OUT = os.path.join(OUTD, "barriers.jsonl")


class Field:
    def __init__(self, snap, mobile, fixed, rho_mode="snapshot"):
        st = snap["state"]
        self.world, _ = BottleneckScenario(1, snap["width"]).build(seed=0)
        self.mobile, self.fixed = list(mobile), list(fixed)
        ids = self.mobile + self.fixed
        self.r = st.radii[ids]
        self.tau = st.taus[ids]
        self.v0 = st.desired_speeds[ids]
        self.m = st.masses[ids]
        self.fixed_pos = st.positions[self.fixed].copy()
        act = st.active_indices
        if rho_mode == "snapshot":
            P = st.positions
            rho = np.array([(np.linalg.norm(P[act] - P[i], axis=1) < 3.0).sum() - 1 for i in ids]) / (9 * np.pi)
        else:
            rho = np.zeros(len(ids))
        self.rho = rho
        self.c = self.m * self.v0 * np.array([weidmann_factor(x) for x in rho]) / self.tau
        self.nm = len(self.mobile)
        n = len(ids)
        I, J = np.triu_indices(n, 1)
        keep = I < self.nm
        self.I, self.J = I[keep], J[keep]
        self.rij = self.r[self.I] + self.r[self.J]

    def all_pos(self, X):
        return np.vstack([X.reshape(-1, 2), self.fixed_pos]) if self.fixed else X.reshape(-1, 2)

    def U(self, X):
        P = self.all_pos(X)
        u = np.sum(self.c[: self.nm] * np.linalg.norm(P[: self.nm] - G, axis=1))
        d, _ = agents_to_walls(P[: self.nm], self.world.walls)
        rr = self.r[: self.nm, None]
        u += np.sum(A * B * np.exp((rr - d) / B)) + np.sum(0.5 * K * np.maximum(0, rr - d) ** 2)
        if len(self.I):
            dij = np.linalg.norm(P[self.I] - P[self.J], axis=1)
            m = dij < 3.0
            ov = self.rij[m] - dij[m]
            u += np.sum(A * B * np.exp(ov / B) + 0.5 * K * np.maximum(0.0, ov) ** 2)
        return float(u)

    def grad(self, X, h=1e-6):
        g = np.zeros_like(X)
        for k in range(len(X)):
            e = np.zeros_like(X); e[k] = h
            g[k] = (self.U(X + e) - self.U(X - e)) / (2 * h)
        return g


def code_force_check(snap, mobile, field):
    """-grad U versus the code's C1 force at v = 0 (frozen grid density) for mobile agents."""
    st = copy.deepcopy(snap["state"])
    st.velocities[:] = 0
    keep = set(field.mobile + field.fixed)
    st.active[:] = False
    st.active[list(keep)] = True
    hm = HybridSteeringModel(get_config("C1"), snap["params"])
    act = st.active_indices
    nl = [[] for _ in range(st.n)]
    for i in act:
        nl[i] = [int(j) for j in act if j != i and np.linalg.norm(st.positions[j] - st.positions[i]) <= 3.0]
    dens = np.zeros(st.n)
    dens[[*field.mobile, *field.fixed]] = field.rho
    F = hm.compute_forces(st, nl, field.world.walls, dens)[field.mobile]
    X = st.positions[field.mobile].ravel()
    return float(np.max(np.abs(F.ravel() + field.grad(X))))


def relax(field, X, fix_idx=(), steps=4000, alpha=5e-5):
    X = X.copy()
    for _ in range(steps):
        g = field.grad(X)
        for k in fix_idx:
            g[k] = 0
        X -= capped(alpha * g)
        if np.max(np.abs(g)) < 1e-3:
            break
    return X


def string_method(field, XA, XB, n_img=31, iters=1500, alpha=4e-5):
    s = np.linspace(0, 1, n_img)[:, None]
    path = (1 - s) * XA + s * XB
    for it in range(iters):
        for k in range(1, n_img - 1):
            path[k] -= capped(alpha * field.grad(path[k]))
        seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
        L = np.concatenate([[0], np.cumsum(seg)])
        t = np.linspace(0, L[-1], n_img)
        path = np.column_stack([np.interp(t, L, path[:, d]) for d in range(path.shape[1])])
    E = np.array([field.U(p) for p in path])
    k = int(np.argmax(E))
    X = path[k].copy()
    for _ in range(3000):
        tan = path[min(k + 1, n_img - 1)] - path[max(k - 1, 0)]
        tan /= np.linalg.norm(tan)
        g = field.grad(X)
        X -= capped(alpha * (g - 2 * np.dot(g, tan) * tan))
        if np.linalg.norm(g) < 1e-2:
            break
    return path, E, float(field.U(X)), X, float(np.linalg.norm(field.grad(X)))


def axis_1d(field):
    xs = np.linspace(9.0, 10.4, 1401)
    E = np.array([field.U(np.array([x, 5.0])) for x in xs])
    i_min = int(np.argmin(np.where(xs < 9.95, E, np.inf)))
    i_max = i_min + int(np.argmax(E[i_min:]))
    return float(E[i_max] - E[i_min]), float(xs[i_min]), float(xs[i_max])


def run(job, iters=1500):
    w0 = time.perf_counter()
    snap = pickle.load(open(job["snap"], "rb"))
    b = job["blocker"]
    resid = [int(i) for i in snap["state"].active_indices]
    others = [i for i in resid if i != b]
    xb = snap["state"].positions[b].copy()
    row = {"job_id": job["job_id"], "snap": os.path.basename(job["snap"]), "blocker": b, "resid": resid,
           "blocker_pos": xb.tolist()}
    fa = Field(snap, [b], [], rho_mode="zero")
    row["dU_1d_axis_alone"], row["x_min_1d"], row["x_top_1d"] = axis_1d(fa)
    XA = relax(fa, xb.copy())
    XB = np.array([10.35, 5.0])
    path, E, Esad, Xs, gs = string_method(fa, XA, XB, iters=iters)
    row["alone"] = {"U_min": fa.U(XA), "dU_string": float(E.max() - fa.U(XA)),
                    "dU_climb": Esad - fa.U(XA), "saddle": Xs.tolist(), "grad_norm_saddle": gs,
                    "x_min": XA.tolist()}
    ff = Field(snap, [b], others)
    row["force_check_frozen_maxabs_N"] = code_force_check(snap, [b], ff)
    XA = relax(ff, xb.copy())
    path, E, Esad, Xs, gs = string_method(ff, XA, XB, iters=iters)
    row["frozen"] = {"dU_string": float(E.max() - ff.U(XA)), "dU_climb": Esad - ff.U(XA),
                     "saddle": Xs.tolist(), "grad_norm_saddle": gs, "x_min": XA.tolist()}
    fm = Field(snap, [b] + others, [])
    X0 = snap["state"].positions[[b] + others].ravel()
    row["force_check_all_maxabs_N"] = code_force_check(snap, [b] + others, fm)
    XA = relax(fm, X0)
    XBf = XA.copy(); XBf[0:2] = [10.35, 5.0]
    XBf = relax(fm, XBf, fix_idx=(0, 1))
    path, E, Esad, Xs, gs = string_method(fm, XA, XBf, n_img=31, iters=iters)
    row["all_mobile"] = {"dU_string": float(E.max() - fm.U(XA)), "dU_climb": Esad - fm.U(XA),
                         "saddle_blocker": Xs[:2].tolist(), "grad_norm_saddle": gs,
                         "max_displacement_others_at_saddle": float(np.max(np.linalg.norm(
                             (Xs - XA).reshape(-1, 2)[1:], axis=1))) if others else 0.0}
    row["wall_s"] = time.perf_counter() - w0
    return row


def jobs():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    return [{"job_id": s["tag"], "snap": os.path.join(os.path.dirname(DATA), s["snap"]), "blocker": s["blocker"]}
            for s in sel["E2"]["snapshots"]]


def total():
    return len(jobs())


if __name__ == "__main__":
    os.makedirs(OUTD, exist_ok=True)
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else OUT
    J = jobs()
    if "--limit" in sys.argv:
        J = J[: int(sys.argv[sys.argv.index("--limit") + 1])]
    if "--iters" in sys.argv:
        it = int(sys.argv[sys.argv.index("--iters") + 1])
        fn = functools.partial(run, iters=it)  # smoke tests only
    else:
        fn = run
    wall = run_jobs(J, fn, out, workers=4, log_every=4)
    if out == OUT:
        rows = sorted(load_runs(OUT), key=lambda r: r["job_id"])
        json.dump({"script": "experiments/BAR/bar.py", "doc": __doc__, "n": len(rows), "barriers": rows},
                  open(os.path.join(OUTD, "barriers.json"), "w"), indent=1, default=float)
    print("wall", wall)
