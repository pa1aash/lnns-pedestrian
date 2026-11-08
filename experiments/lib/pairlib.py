"""Pair-standoff physics helpers for E7b (ported from experiments/pilot/a3_pair_stability.py and
experiments/pilot/a5_predict.py; the BAR field of experiments/BAR/bar.py with the run's wall range).

PairField(snap, ids)    rest-state C1 potential of the residual agents, density frozen at the snapshot
                        value (a3 Field, unchanged except that A_w, B_w are read from the snapshot params):
    U = sum_i c_i |x_i - g| + sum_{i,w} A_w B_w exp((r_i - d_iw)/B_w) + sum_{i<j} A B exp((r_ij - d_ij)/B)
        + body terms 0.5 k overlap^2,  c_i = m v0_i f_W(rho_i) / tau_i,  g = (11, 5), A = 2000, B = 0.08.
code_force(...)         the code's force at v = 0 (HybridSteeringModel C1, snapshot params) for the check
                        max |F_code + grad U| (a3).
relax(...)              a5 static prediction: overdamped relaxation dx/dt = (tau_i/m_i) F_i(x) of the code's
                        rest-state force (v = 0, density frozen, other agents inactive), Euler step 0.01 s, up
                        to 120 s; freed if a residual agent reaches x > 10.3 m, held if max |F| < 0.05 N.
                        Arm flags are applied on top of the snapshot params (which carry CF and B_w).
PairBarField            bar.Field with the wall terms at the snapshot's B_w (BAR hard-codes B = 0.08 for walls).
The room door has no shared wall end points, so the corner rule (convex_union) does not enter.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "BAR"))
from w2lib import BottleneckScenario, HybridSteeringModel, get_config, weidmann_factor  # noqa: E402
import numpy as np  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402
import bar  # noqa: E402

A, B, K = 2000.0, 0.08, 120000.0
G = np.array([11.0, 5.0])


def residual_ids(snap):
    """Residual agents ordered by y (lower first)."""
    st = snap["state"]
    return sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])


def snapshot_rho(snap, ids):
    st = snap["state"]
    act = st.active_indices
    P = st.positions
    return np.array([(np.linalg.norm(P[act] - P[i], axis=1) < 3.0).sum() - 1 for i in ids]) / (9 * np.pi)


class PairField:
    def __init__(self, snap, ids):
        st = snap["state"]
        self.world, _ = BottleneckScenario(1, snap["width"]).build(seed=0)
        self.ids = list(ids)
        self.r, self.tau, self.v0, self.m = (st.radii[ids], st.taus[ids], st.desired_speeds[ids], st.masses[ids])
        self.rho = snapshot_rho(snap, ids)
        self.c = self.m * self.v0 * np.array([weidmann_factor(x) for x in self.rho]) / self.tau
        self.A_w = float(snap["params"].get("A_w", 2000.0))
        self.B_w = float(snap["params"].get("B_w", 0.08))

    def parts(self, X):
        P = X.reshape(-1, 2)
        n = len(P)
        u_drive = float(np.sum(self.c * np.linalg.norm(P - G, axis=1)))
        d, _ = agents_to_walls(P, self.world.walls)
        rr = self.r[:, None]
        u_wall = float(np.sum(self.A_w * self.B_w * np.exp((rr - d) / self.B_w))
                       + np.sum(0.5 * K * np.maximum(0, rr - d) ** 2))
        u_pair = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                dij = np.linalg.norm(P[i] - P[j])
                rij = self.r[i] + self.r[j]
                u_pair += A * B * np.exp((rij - dij) / B) + 0.5 * K * max(0.0, rij - dij) ** 2
        return u_drive, u_wall, u_pair

    def U(self, X):
        return sum(self.parts(X))

    def grad(self, X, h=1e-6, which=None):
        f = (lambda Y: self.parts(Y)[which]) if which is not None else self.U
        g = np.zeros_like(X)
        for k in range(len(X)):
            e = np.zeros_like(X); e[k] = h
            g[k] = (f(X + e) - f(X - e)) / (2 * h)
        return g

    def hess(self, X, h=1e-4):
        n = len(X)
        H = np.zeros((n, n))
        U0 = self.U(X)
        for a in range(n):
            for b in range(a, n):
                ea = np.zeros(n); ea[a] = h
                eb = np.zeros(n); eb[b] = h
                if a == b:
                    H[a, a] = (self.U(X + ea) - 2 * U0 + self.U(X - ea)) / h ** 2
                else:
                    H[a, b] = H[b, a] = (self.U(X + ea + eb) - self.U(X + ea - eb) - self.U(X - ea + eb)
                                         + self.U(X - ea - eb)) / (4 * h * h)
        return H


def code_force(snap, ids, field):
    st = copy.deepcopy(snap["state"])
    st.velocities[:] = 0
    act = st.active_indices
    hm = HybridSteeringModel(get_config("C1"), snap["params"])
    nl = [[] for _ in range(st.n)]
    for i in act:
        nl[i] = [int(j) for j in act if j != i and np.linalg.norm(st.positions[j] - st.positions[i]) <= 3.0]
    dens = np.zeros(st.n)
    dens[ids] = field.rho
    return hm.compute_forces(st, nl, field.world.walls, dens)[ids]


def relax(snap, cfg, flags, T=120.0, h=0.01):
    st = copy.deepcopy(snap["state"])
    st.velocities[:] = 0
    ids = residual_ids(snap)
    side = {i: ("lower" if st.positions[i, 1] < 5.0 else "upper") for i in ids}
    params = dict(snap["params"])
    params.update(flags)
    world, _ = BottleneckScenario(1, snap["width"]).build(seed=0)
    hm = HybridSteeringModel(get_config(cfg), params)
    dens = np.zeros(st.n)
    dens[ids] = snapshot_rho(snap, ids)
    k = np.array(ids)
    gain = (st.taus[k] / st.masses[k])[:, None]
    t = 0.0
    F = np.zeros((len(ids), 2))
    while t < T - 1e-9:
        nl = [[] for _ in range(st.n)]
        for i in ids:
            if st.active[i]:
                nl[i] = [j for j in ids if j != i and st.active[j]]
        F = hm.compute_forces(st, nl, world.walls, dens)[k]
        F[~st.active[k]] = 0
        if np.abs(F).max() < 0.05:
            return {"pred_freed": False, "t": t, "pos": st.positions[k].tolist()}
        st.positions[k] += h * gain * F
        t += h
        out = [i for i in ids if st.active[i] and st.positions[i, 0] > 10.3]
        if out:
            return {"pred_freed": True, "t": t, "first": out[0], "first_side": side[out[0]],
                    "pos": st.positions[k].tolist()}
    return {"pred_freed": None, "t": t, "pos": st.positions[k].tolist(), "maxF": float(np.abs(F).max())}


class PairBarField(bar.Field):
    """bar.Field (mobile agents first) with wall terms at the snapshot's A_w, B_w."""

    def __init__(self, snap, mobile, fixed=(), rho_mode="snapshot"):
        super().__init__(snap, mobile, list(fixed), rho_mode=rho_mode)
        self.A_w = float(snap["params"].get("A_w", 2000.0))
        self.B_w = float(snap["params"].get("B_w", 0.08))

    def U(self, X):
        P = self.all_pos(X)
        u = np.sum(self.c[: self.nm] * np.linalg.norm(P[: self.nm] - G, axis=1))
        d, _ = agents_to_walls(P[: self.nm], self.world.walls)
        rr = self.r[: self.nm, None]
        u += np.sum(self.A_w * self.B_w * np.exp((rr - d) / self.B_w)) + np.sum(0.5 * K * np.maximum(0, rr - d) ** 2)
        if len(self.I):
            dij = np.linalg.norm(P[self.I] - P[self.J], axis=1)
            m = dij < 3.0
            ov = self.rij[m] - dij[m]
            u += np.sum(A * B * np.exp(ov / B) + 0.5 * K * np.maximum(0.0, ov) ** 2)
        return float(u)
