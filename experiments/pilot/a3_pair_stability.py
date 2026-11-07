"""W2b A1 (per-snapshot record) + A3 (stability of the pair state).
Snapshots: B_w = 0.04 (all walls) corrected-forward deadlocks with 2+ residual agents:
wave2/data/library/w25_B0.04_seed*.pkl (seeds 42-66) and wave2b/data/library/a1_B0.04_seed*.pkl.
Static rest-state C1 field with density frozen at the snapshot value (as Wave 1 P6, W2.3):
U = sum_i c_i |x_i - g| + sum_{i,w} A_w B_w exp((r_i - d_iw)/B_w) + sum_{i<j} A B exp((r_ij - d_ij)/B)
    + body terms 0.5 k overlap^2,  c_i = m v0_i f_W(rho_i) / tau_i,  A_w = 2000, B_w = 0.04, A = 2000, B = 0.08.
Check: max |F_code(v=0) + grad U| over the residual agents (code = HybridSteeringModel C1 with the
snapshot params). Hessian: central second differences of U (h = 1e-4 m) in the 2N residual
coordinates. Eigenvalues (N/m); softest eigenvector (agent order: lower y first; components
dx_lo, dy_lo, dx_hi, dy_hi). Output: wave2b/data/a3_pair_stability.json"""
import copy, glob, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2blib import *  # noqa
from sim.core.world import agents_to_walls
from sim.steering.hybrid import HybridSteeringModel
from sim.experiments.configs import get_config

A, B, K = 2000.0, 0.08, 120000.0
G = np.array([11.0, 5.0])


class Field:
    def __init__(self, snap, ids, A_w=2000.0, B_w=0.04):
        st = snap["state"]
        self.world, _ = BottleneckScenario(1, snap["width"]).build(seed=0)
        self.ids = list(ids)
        self.r, self.tau, self.v0, self.m = (st.radii[ids], st.taus[ids], st.desired_speeds[ids], st.masses[ids])
        act = st.active_indices
        P = st.positions
        # grid-free count density within 3 m, as wave2/scripts/w23_barrier.py (verified vs code there)
        self.rho = np.array([(np.linalg.norm(P[act] - P[i], axis=1) < 3.0).sum() - 1 for i in ids]) / (9 * np.pi)
        self.c = self.m * self.v0 * np.array([weidmann_factor(x) for x in self.rho]) / self.tau
        self.A_w, self.B_w = A_w, B_w

    def parts(self, X):
        P = X.reshape(-1, 2)
        n = len(P)
        u_drive = float(np.sum(self.c * np.linalg.norm(P - G, axis=1)))
        d, _ = agents_to_walls(P, self.world.walls)
        rr = self.r[:, None]
        u_wall = float(np.sum(self.A_w * self.B_w * np.exp((rr - d) / self.B_w)) + np.sum(0.5 * K * np.maximum(0, rr - d) ** 2))
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
                    H[a, b] = H[b, a] = (self.U(X + ea + eb) - self.U(X + ea - eb) - self.U(X - ea + eb) + self.U(X - ea - eb)) / (4 * h * h)
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


def analyse(path):
    snap = pickle.load(open(path, "rb"))
    st = snap["state"]
    ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
    f = Field(snap, ids, B_w=snap["params"].get("B_w", 0.08))
    X = st.positions[ids].ravel()
    P = X.reshape(-1, 2)
    Fc = code_force(snap, ids, f)
    gU = f.grad(X)
    H = f.hess(X)
    ev, V = np.linalg.eigh(H)
    v0 = V[:, 0] * np.sign(V[np.argmax(np.abs(V[:, 0])), 0])
    rec = {"snap": os.path.relpath(path, PLAN), "n_resid": len(ids), "ids": ids,
           "pos": P.tolist(), "y_rel": (P[:, 1] - 5.0).tolist(), "radii": f.r.tolist(),
           "rho_frozen": f.rho.tolist(), "drive_c_N": f.c.tolist(),
           "max_speed": float(np.linalg.norm(st.velocities[ids], axis=1).max()),
           "check_max_abs_F_plus_gradU_N": float(np.max(np.abs(Fc.ravel() + gU))),
           "force_parts_N": {nm: (-f.grad(X, which=k)).reshape(-1, 2).tolist() for k, nm in enumerate(("drive", "wall", "pair"))},
           "hess_eig_N_per_m": ev.tolist(), "softest_vec": v0.tolist()}
    if len(ids) >= 2:
        lo, hi = P[0], P[-1]
        d = float(np.linalg.norm(hi - lo))
        rec.update({"asym_axis_dist_m": float(abs(abs(lo[1] - 5) - abs(hi[1] - 5))),
                    "asym_x_m": float(abs(lo[0] - hi[0])),
                    "asym_drive_N": float(abs(f.c[0] - f.c[-1])),
                    "asym_radius_m": float(abs(f.r[0] - f.r[-1])),
                    "pair_dist_m": d, "pair_gap_m": d - float(f.r[0] + f.r[-1]),
                    "contact": bool(d < f.r[0] + f.r[-1])})
        # wall distance (surface gap) of each agent
        dw, _ = agents_to_walls(P, f.world.walls)
        rec["wall_gap_m"] = (dw.min(axis=1) - f.r).tolist()
    # softest-mode type for pairs: lateral components share sign -> 'antisymmetric (common shift)'
    if len(ids) == 2:
        dy_lo, dy_hi = v0[1], v0[3]
        rec["softest_type"] = ("common_lateral" if dy_lo * dy_hi > 0 and abs(dy_lo) + abs(dy_hi) > abs(v0[0]) + abs(v0[2])
                               else "opposed_lateral" if abs(dy_lo) + abs(dy_hi) > abs(v0[0]) + abs(v0[2])
                               else "longitudinal")
    rec["strict_min"] = bool(ev[0] > 0)
    # lone-agent stuck check under the snapshot wall model (passability, rho as frozen)
    return rec


if __name__ == "__main__":
    paths = sorted(glob.glob(os.path.join(PLAN, "wave2/data/library/w25_B0.04_seed*.pkl"))) + \
            sorted(glob.glob(os.path.join(LIB2B, "a1_B0.04_seed*.pkl")))
    out = [analyse(p) for p in paths]
    json.dump(out, open(os.path.join(DATA2B, "a3_pair_stability.json"), "w"), indent=1)
    for r in out:
        print(os.path.basename(r["snap"]), r["n_resid"], np.round(r["y_rel"], 3), "chk", "%.1e" % r["check_max_abs_F_plus_gradU_N"],
              "eig", np.round(r["hess_eig_N_per_m"], 1), r.get("softest_type"), np.round(r["softest_vec"], 2),
              "asym", round(r.get("asym_axis_dist_m", 0), 4), round(r.get("asym_drive_N", 0), 1), "gap", round(r.get("pair_gap_m", 0), 3))
