"""W2.3(b) barriers for the 5 W2.3 snapshots. Rest-state C1 force field with density
frozen at the snapshot value is conservative (verified here: -grad U vs code force).
U = sum_i c_i |x_i - g| + sum_{i,w} A B exp((r_i - d_iw)/B) + sum_{i<j} A B exp((r_ij - d_ij)/B)
    (+ 0.5 k overlap^2 body terms), c_i = m v_eff,i / tau_i.
Barriers: 1-D on-axis integral (blocker alone, as P6c), and 2-D/2N-D minimum-energy
paths by the string method (E & Ren) with a climbing refinement of the top image:
(i) blocker alone, (ii) blocker with neighbours frozen, (iii) all residual agents mobile.
Output: wave2/data/w23_barrier.json"""
import copy, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from w2lib import DATA, weidmann_factor
from sim.core.world import agents_to_walls
from sim.core.agent import AgentState
from sim.scenarios.bottleneck import BottleneckScenario
from sim.steering.hybrid import HybridSteeringModel
from sim.experiments.configs import get_config

A, B, K = 2000.0, 0.08, 120000.0
G = np.array([11.0, 5.0])


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

    def all_pos(self, X):
        return np.vstack([X.reshape(-1, 2), self.fixed_pos]) if self.fixed else X.reshape(-1, 2)

    def U(self, X):
        P = self.all_pos(X)
        u = np.sum(self.c[: self.nm] * np.linalg.norm(P[: self.nm] - G, axis=1))
        d, _ = agents_to_walls(P[: self.nm], self.world.walls)
        rr = self.r[: self.nm, None]
        u += np.sum(A * B * np.exp((rr - d) / B)) + np.sum(0.5 * K * np.maximum(0, rr - d) ** 2)
        n = len(P)
        for i in range(self.nm):
            for j in range(i + 1, n):
                dij = np.linalg.norm(P[i] - P[j])
                if dij < 3.0:
                    rij = self.r[i] + self.r[j]
                    u += A * B * np.exp((rij - dij) / B) + 0.5 * K * max(0.0, rij - dij) ** 2
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
        X -= alpha * g
        if np.max(np.abs(g)) < 1e-3:
            break
    return X


def string_method(field, XA, XB, n_img=31, iters=1500, alpha=4e-5):
    s = np.linspace(0, 1, n_img)[:, None]
    path = (1 - s) * XA + s * XB
    for it in range(iters):
        for k in range(1, n_img - 1):
            path[k] -= alpha * field.grad(path[k])
        seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
        L = np.concatenate([[0], np.cumsum(seg)])
        t = np.linspace(0, L[-1], n_img)
        path = np.column_stack([np.interp(t, L, path[:, d]) for d in range(path.shape[1])])
    E = np.array([field.U(p) for p in path])
    k = int(np.argmax(E))
    # climbing refinement: maximise along the local tangent, minimise perpendicular
    X = path[k].copy()
    for _ in range(3000):
        tan = path[min(k + 1, n_img - 1)] - path[max(k - 1, 0)]
        tan /= np.linalg.norm(tan)
        g = field.grad(X)
        X -= alpha * (g - 2 * np.dot(g, tan) * tan)
        if np.linalg.norm(g) < 1e-2:
            break
    return path, E, float(field.U(X)), X, float(np.linalg.norm(field.grad(X)))


def axis_1d(field):
    xs = np.linspace(9.0, 10.4, 1401)
    E = np.array([field.U(np.array([x, 5.0])) for x in xs])
    i_min = int(np.argmin(np.where(xs < 9.95, E, np.inf)))
    i_max = i_min + int(np.argmax(E[i_min:]))
    return float(E[i_max] - E[i_min]), float(xs[i_min]), float(xs[i_max])


def main():
    sel = json.load(open(os.path.join(DATA, "w23_selected.json")))
    res = []
    for s in sel:
        snap = pickle.load(open(s["snap"], "rb"))
        b = s["blocker"]
        resid = [int(i) for i in snap["state"].active_indices]
        others = [i for i in resid if i != b]
        xb = snap["state"].positions[b].copy()
        row = {"snap": os.path.basename(s["snap"]), "blocker": b, "resid": resid,
               "blocker_pos": xb.tolist()}
        # (i) alone (density 0 as in the 'alone' restart condition)
        fa = Field(snap, [b], [], rho_mode="zero")
        row["dU_1d_axis_alone"], row["x_min_1d"], row["x_top_1d"] = axis_1d(fa)
        XA = relax(fa, xb.copy())
        XB = np.array([10.35, 5.0])
        path, E, Esad, Xs, gs = string_method(fa, XA, XB)
        row["alone"] = {"U_min": fa.U(XA), "dU_string": float(E.max() - fa.U(XA)),
                        "dU_climb": Esad - fa.U(XA), "saddle": Xs.tolist(), "grad_norm_saddle": gs,
                        "x_min": XA.tolist()}
        # (ii) frozen neighbours (snapshot density)
        ff = Field(snap, [b], others)
        row["force_check_frozen_maxabs_N"] = code_force_check(snap, [b], ff)
        XA = relax(ff, xb.copy())
        path, E, Esad, Xs, gs = string_method(ff, XA, XB)
        row["frozen"] = {"dU_string": float(E.max() - ff.U(XA)), "dU_climb": Esad - ff.U(XA),
                         "saddle": Xs.tolist(), "grad_norm_saddle": gs, "x_min": XA.tolist()}
        # (iii) all residual mobile (snapshot density)
        fm = Field(snap, [b] + others, [])
        X0 = snap["state"].positions[[b] + others].ravel()
        row["force_check_all_maxabs_N"] = code_force_check(snap, [b] + others, fm)
        XA = relax(fm, X0)
        XBf = XA.copy(); XBf[0:2] = [10.35, 5.0]
        XBf = relax(fm, XBf, fix_idx=(0, 1))
        path, E, Esad, Xs, gs = string_method(fm, XA, XBf, n_img=31, iters=1500)
        row["all_mobile"] = {"dU_string": float(E.max() - fm.U(XA)), "dU_climb": Esad - fm.U(XA),
                             "saddle_blocker": Xs[:2].tolist(), "grad_norm_saddle": gs,
                             "max_displacement_others_at_saddle": float(np.max(np.linalg.norm(
                                 (Xs - XA).reshape(-1, 2)[1:], axis=1))) if others else 0.0}
        print(json.dumps(row, default=float), flush=True)
        res.append(row)
    json.dump(res, open(os.path.join(DATA, "w23_barrier.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
