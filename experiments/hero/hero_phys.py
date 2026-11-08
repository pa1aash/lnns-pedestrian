"""Rest-state physics behind the hero figure (Fig. 1), from the simulator's own routines.

Run with the plan interpreter:  /Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python
Imports the repository's experiments/lib (which puts code/ on the path and changes the cwd to code/),
so every path used here is absolute.

Contents
  * forces_at: the code's rest-state force on every active agent split into drive, wall, partner and
    (if a lateral bias is set) the bias increment, all from the HybridSteeringModel components;
  * RestField: the rest-state potential of a residual set (drive + the code's wall law with its corner
    rule + agent-agent law), density frozen, optional lateral-bias tilt (as in the pilot BiasField);
  * lone_ribbon: potential of one agent along a line parallel to the door axis (own drive / added drive);
  * pair_ribbon: potential along the common lateral shift of two members, relaxed over the opposed
    coordinate and the forward positions.
"""
import copy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "experiments" / "lib"))

import numpy as np  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

import w2lib  # noqa: E402,F401  (chdir to code/, simulator on sys.path)
from w2lib import BottleneckScenario, HybridSteeringModel, get_config, weidmann_factor  # noqa: E402
from sim.core.agent import AgentState  # noqa: E402
from sim.core.helpers import safe_normalize  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402
from sim.steering.desired import compute_desired_force  # noqa: E402

G = np.array([11.0, 5.0])
K_BODY = 120000.0
A_AA, B_AA = 2000.0, 0.08
CF = {"w2_numerics": "fixed", "w2_orca": "rvo2", "w2_crush": "off", "w2_wall_corner": "convex_union"}


def world_of(snap):
    return BottleneckScenario(1, snap["width"], **snap["scen"]).build(seed=0)[0]


def frozen_rho(st, ids):
    act = st.active_indices
    P = st.positions
    return np.array([(np.linalg.norm(P[act] - P[i], axis=1) < 3.0).sum() - 1 for i in ids]) / (9 * np.pi)


def model_of(snap, bias=0.0):
    params = dict(snap["params"])
    params.update(CF)
    if bias:
        params.update({"w2_noise": "lateral_bias", "w2_bias_b": float(bias)})
    return HybridSteeringModel(get_config("C1"), params), params


def forces_at(snap, ids, bias=0.0, X=None):
    """Rest-state force components on `ids` (velocities zero, density frozen at the snapshot value).
    X: optional (len(ids), 2) positions to evaluate at. Returns dict of (len(ids), 2) arrays."""
    hm, params = model_of(snap, bias)
    st = copy.deepcopy(snap["state"])
    st.velocities[:] = 0
    world = world_of(snap)
    rho = frozen_rho(st, ids)
    if X is not None:
        st.positions[ids] = X
    act = st.active_indices
    nl = [[] for _ in range(st.n)]
    for i in act:
        nl[i] = [int(j) for j in act if j != i and np.linalg.norm(st.positions[j] - st.positions[i]) <= 3.0]
    dens = np.zeros(st.n)
    dens[ids] = rho
    goals = st.goals
    if bias:
        e = safe_normalize(st.goals - st.positions)
        e_perp = np.column_stack([-e[:, 1], e[:, 0]])
        goals = st.positions + e + bias * e_perp
    k = np.asarray(ids)
    F_des = compute_desired_force(st.positions, st.velocities, goals, st.desired_speeds, st.masses, st.taus,
                                  local_densities=dens, weidmann_gamma=params.get("weidmann_gamma", 1.913),
                                  weidmann_rho_max=params.get("weidmann_rho_max", 5.4))
    F_sfm = hm.sfm.compute_agent_forces(st, nl)
    F_wall = hm.wall_forces.compute_wall_forces(st, world.walls)
    F_tot = hm.compute_forces(st, nl, world.walls, dens)
    out = {"drive": F_des[k], "partner": F_sfm[k], "wall": F_wall[k], "total": F_tot[k], "rho": rho}
    out["sum_parts"] = out["drive"] + out["partner"] + out["wall"]
    return out


class RestField:
    """U(X) for the residual agents `ids` (X flattened (x1, y1, x2, y2, ...)), density frozen:
         U = sum c_i |x_i - g| + sum_{i,w} keep_iw [A_w B_w e^{(r_i-d_iw)/B_w} + k/2 (r_i-d_iw)_+^2]
             + sum_{i<j} [A B e^{(r_ij-d_ij)/B} + k/2 (r_ij-d_ij)_+^2]
       with c_i = m v0 f_W(rho_i)/tau_i and the wall sum following the code's corner rule (keep mask).
       bias b: desired direction (e + b e_perp)/|e + b e_perp| with e_perp frozen at the snapshot position,
       U_b = (U_drive - b tilt)/sqrt(1+b^2) + U_wall + U_pair (the pilot BiasField), approximately conservative;
       the residual against the code force is reported by the caller."""

    def __init__(self, snap, ids, bias=0.0, c_override=None):
        st = snap["state"]
        self.snap, self.ids, self.b = snap, list(ids), bias
        self.world = world_of(snap)
        self.walls = self.world.walls
        hm, params = model_of(snap)
        self.wf = hm.wall_forces
        self.A_w, self.B_w = self.wf.A, self.wf.B
        self.r, self.tau, self.v0, self.m = st.radii[ids], st.taus[ids], st.desired_speeds[ids], st.masses[ids]
        self.rho = frozen_rho(st, ids)
        self.c = (self.m * self.v0 * np.array([weidmann_factor(x) for x in self.rho]) / self.tau
                  if c_override is None else np.asarray(c_override, float))
        P0 = st.positions[ids]
        self.X0 = P0.copy().ravel()
        e = (G - P0) / np.linalg.norm(G - P0, axis=1)[:, None]
        self.eperp0 = np.column_stack([-e[:, 1], e[:, 0]])
        self.junctions = self.wf._junctions(self.walls) if self.wf.corner == "convex_union" else []

    def wall_energy(self, P):
        d, _ = agents_to_walls(P, self.walls)
        rr = self.r[:, None]
        e = self.A_w * self.B_w * np.exp((rr - d) / self.B_w) + 0.5 * K_BODY * np.maximum(0.0, rr - d) ** 2
        if self.junctions:
            e = e * self.wf._corner_keep(P, self.walls, self.junctions)
        return float(e.sum())

    def parts(self, X):
        P = X.reshape(-1, 2)
        n = len(P)
        u_drive = float(np.sum(self.c * np.linalg.norm(P - G, axis=1)))
        if self.b:
            s = 1.0 / np.sqrt(1.0 + self.b ** 2)
            tilt = np.sum(self.c * np.einsum("ij,ij->i", self.eperp0, P - self.X0.reshape(-1, 2)))
            u_drive = s * u_drive - s * self.b * tilt
        u_wall = self.wall_energy(P)
        u_pair = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                dij = np.linalg.norm(P[i] - P[j])
                rij = self.r[i] + self.r[j]
                u_pair += A_AA * B_AA * np.exp((rij - dij) / B_AA) + 0.5 * K_BODY * max(0.0, rij - dij) ** 2
        return u_drive, u_wall, u_pair

    def U(self, X):
        return sum(self.parts(X))

    def grad(self, X, h=1e-6):
        g = np.zeros_like(X)
        for k in range(len(X)):
            e = np.zeros_like(X)
            e[k] = h
            g[k] = (self.U(X + e) - self.U(X - e)) / (2 * h)
        return g


def lone_ribbon(snap, i, tau_orca=0.5, x0=9.30, x1=10.40, step=0.0005):
    """Potential of agent i alone along the line y = y_i (parallel to the door axis), r, v0, tau its own,
    density frozen at the snapshot value, wall energy = minus the line integral of the code's wall force.
    own: c = m v0/tau (spec; the Weidmann factor is >= 0.99 at rest). added: c + w_o m v0/tau_ORCA."""
    st = snap["state"]
    hm, params = model_of(snap)
    world = world_of(snap)
    ids = sorted(int(j) for j in st.active_indices)
    rho = frozen_rho(st, ids)[ids.index(i)]
    r, v0, tau, m = float(st.radii[i]), float(st.desired_speeds[i]), float(st.taus[i]), float(st.masses[i])
    y = float(st.positions[i, 1])
    xs = np.arange(x0, x1 + 1e-9, step)
    n = len(xs)
    pr = AgentState(np.column_stack([xs, np.full(n, y)]), np.zeros((n, 2)), np.tile(G, (n, 1)), np.full(n, r),
                    np.ones(n), np.full(n, m), np.full(n, tau), np.ones(n, bool))
    Fw = hm.wall_forces.compute_wall_forces(pr, world.walls)[:, 0]
    Uw = -np.concatenate([[0.0], np.cumsum(0.5 * (Fw[1:] + Fw[:-1]) * np.diff(xs))])
    c = m * v0 / tau
    w_o = 1.0 - 1.0 / (1.0 + np.exp(-2.0 * (rho - 4.0)))
    co = w_o * m * v0 / tau_orca
    dist = np.hypot(G[0] - xs, G[1] - y)
    # neighbours' push: the agent-agent force from the other held agents pinned at their frozen positions, x component
    # along the same line (4C found a 0.53 J dimple without it; the push, 17.5 -> 25 N, is larger than the 11 N shortfall)
    st2 = copy.deepcopy(st)
    st2.velocities[:] = 0
    act = [int(j) for j in st.active_indices]
    nl = [[] for _ in range(st2.n)]
    for a in act:
        nl[a] = [j for j in act if j != a and np.linalg.norm(st.positions[j] - st.positions[a]) <= 3.0]
    xc = xs[::10]
    Fc = np.empty(len(xc))
    for k, xv in enumerate(xc):
        st2.positions[i, 0] = xv
        Fc[k] = hm.sfm.compute_agent_forces(st2, nl)[i, 0]
    Fp = np.interp(xs, xc, Fc)
    Up = -np.concatenate([[0.0], np.cumsum(0.5 * (Fp[1:] + Fp[:-1]) * np.diff(xs))])
    return {"x": xs, "y": y, "r": r, "v0": v0, "tau": tau, "m": m, "rho": float(rho), "c": c, "c_orca": co, "w_o": float(w_o),
            "U_own": c * dist + Uw, "U_added_alone": (c + co) * dist + Uw, "U_added": (c + co) * dist + Uw + Up,
            "wall_Fx": Fw, "push_Fx": Fp}


def check_ribbon_vs_model(snap, i, rb, config="C3", x_from=9.55):
    """The code's full hybrid (C3, rvo2) force on agent i along the ribbon line at rest, density frozen, against the
    ribbon's force (-dU/dx): alone (others inactive) and with the neighbours pinned. Returns max |difference| (N) and the
    minimum x force along the line for each case."""
    st = snap["state"]
    params = dict(snap["params"])
    params.update(CF)
    hm = HybridSteeringModel(get_config(config), params)
    world = world_of(snap)
    ids = sorted(int(j) for j in st.active_indices)
    rho = frozen_rho(st, ids)[ids.index(i)]
    xs = rb["x"][::40]
    e_x = (G[0] - xs) / np.hypot(G[0] - xs, G[1] - rb["y"])
    pred_alone = (rb["c"] + rb["c_orca"]) * e_x + np.interp(xs, rb["x"], rb["wall_Fx"])
    pred_nb = pred_alone + np.interp(xs, rb["x"], rb["push_Fx"])
    out = {}
    for name, nb, pred in (("alone", False, pred_alone), ("neighbours_pinned", True, pred_nb)):
        Fx = np.empty(len(xs))
        for k, xv in enumerate(xs):
            s = copy.deepcopy(st)
            s.velocities[:] = 0
            s.positions[i, 0] = xv
            act = [i] + ([j for j in ids if j != i] if nb else [])
            for j in ids:
                if j not in act:
                    s.active[j] = False
            nl = [[] for _ in range(s.n)]
            for a in act:
                nl[a] = [j for j in act if j != a]
            dens = np.zeros(s.n)
            dens[act] = rho
            Fx[k] = hm.compute_forces(s, nl, world.walls, dens)[i, 0]
        d = np.abs(Fx - pred)
        keep = xs >= x_from                       # the drawn range; left of it the blocker is beside the neighbours (ORCA constraints)
        out[name] = {"max_abs_diff_N": float(d[keep].max()), "max_abs_diff_N_all_x": float(d.max()),
                     "x_of_max_diff_all": float(xs[d.argmax()]), "min_Fx_N": float(Fx[keep].min()),
                     "sign_changes": int(np.sum(np.sign(Fx[keep][1:]) != np.sign(Fx[keep][:-1]))), "x_from": x_from}
    return out


def stationary_points(x, U):
    """Local minima and maxima of the sampled U(x): (x_min list, x_max list) by sign change of dU/dx."""
    d = np.gradient(U, x)
    s = np.sign(d)
    idx = np.where(np.diff(s) != 0)[0]
    mins, maxs = [], []
    for j in idx:
        xz = x[j] - d[j] * (x[j + 1] - x[j]) / (d[j + 1] - d[j])
        (mins if d[j] < 0 < d[j + 1] else maxs).append(float(xz))
    return mins, maxs


def pair_ribbon(snap, ids, bias, cs, do_bound=0.15, dx_bound=0.30):
    """U along the common lateral shift c of the two members (dy_lo = dy_hi = c), minimised over the opposed
    coordinate o (dy_hi - dy_lo = 2 o) and both forward positions (relaxed), continuing outward from c = 0.
    Returns (U relative to the snapshot's U at b = 0, relaxed o, dx_lo, dx_hi at every c)."""
    f = RestField(snap, ids, bias)
    f0 = RestField(snap, ids, 0.0)
    X0 = f.X0
    U_ref = f0.U(X0)
    out = np.empty(len(cs))
    arg = np.zeros((len(cs), 3))
    order0 = int(np.argmin(np.abs(cs)))
    for sweep in (range(order0, len(cs)), range(order0 - 1, -1, -1)):
        prev = np.zeros(3)
        for k in sweep:
            c = cs[k]

            def obj(z, c=c):
                X = X0.copy()
                X[1] += c - z[0]
                X[3] += c + z[0]
                X[0] += z[1]
                X[2] += z[2]
                return f.U(X)
            res = minimize(obj, prev, method="L-BFGS-B", bounds=[(-do_bound, do_bound), (-dx_bound, dx_bound), (-dx_bound, dx_bound)],
                           options={"ftol": 1e-13, "gtol": 1e-9})
            out[k], arg[k], prev = res.fun - U_ref, res.x, res.x
    return out, arg
