"""Export the physics data behind the hero figure (Fig. 1) as .npz files.

Run with the plan root's interpreter, read-only against the plan root:

    PYTHONDONTWRITEBYTECODE=1 \\
    /Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python experiments/hero/export_hero.py

Every number comes from the simulator's own state and force routines:
  * lone-trap scene: a published-mode C1 deadlock snapshot (wave2 library), agent state,
    stuck-alone margins from w2lib.Passability, wall segments, and a floor grid of the
    wall force on a lone r = 0.25 m agent at rest from the code's WallForces object built
    by HybridSteeringModel with the snapshot's own parameters;
  * pair scene: a corrected-forward B_w = 0.04 pair snapshot (wave2b A4 selection), and the
    rest-state potential U (density frozen; wave2b/scripts/a3_pair_stability.Field) on a grid
    of the two members' lateral displacements, at b = 0 and at the first bias the static
    relaxation (wave2b/data/a5_predict.json) predicts to free the pair.

Pilot data. Production swaps in an E1b corrected-forward snapshot (LONE_SNAP / PAIR_SNAP).
"""
import argparse
import copy
import json
import os
import pickle
import sys
import time
from pathlib import Path

PLAN = Path("/Users/palaash/Developer/pedestrian-abs-plan")
OUT = Path(__file__).resolve().parents[2] / "data" / "derived" / "hero"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PLAN / "wave2b" / "scripts"))
sys.path.insert(0, str(PLAN / "wave2" / "scripts"))

import numpy as np  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

import w2lib  # noqa: E402  (chdir to pedestrian-abs; library dirs already exist)
from w2lib import DOOR, BottleneckScenario, Passability, get_config, HybridSteeringModel  # noqa: E402
from a3_pair_stability import Field, code_force  # noqa: E402
from sim.core.agent import AgentState  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402

LONE_SNAP = PLAN / "wave2/data/library/C1_w0.8_seed108.pkl"
PAIR_SNAP = PLAN / "wave2/data/library/w25_B0.04_seed43.pkl"   # listed in wave2b/data/a4_selected_snaps.txt
G = np.array([11.0, 5.0])


def frozen_rho(st, ids):
    act = st.active_indices
    P = st.positions
    return np.array([(np.linalg.norm(P[act] - P[i], axis=1) < 3.0).sum() - 1 for i in ids]) / (9 * np.pi)


def walls_array(world):
    return np.array([[*w.start, *w.end] for w in world.walls], float)


# ------------------------------------------------------------------ floor field
def floor_field(params, world, r_probe=0.25, step=0.01, x=(8.4, 10.6), y=(3.2, 6.8)):
    """Wall force on a lone probe agent of radius r_probe at rest at every grid point, from the
    WallForces instance HybridSteeringModel builds from `params` (same law, parameters, corner rule)."""
    wf = HybridSteeringModel(get_config("C1"), params).wall_forces
    xs = np.arange(x[0], x[1] + 1e-9, step)
    ys = np.arange(y[0], y[1] + 1e-9, step)
    X, Y = np.meshgrid(xs, ys, indexing="xy")          # shape (ny, nx)
    pts = np.column_stack([X.ravel(), Y.ravel()])
    n = len(pts)
    probe = AgentState(pts.copy(), np.zeros((n, 2)), np.tile(G, (n, 1)), np.full(n, r_probe), np.ones(n),
                       np.full(n, 80.0), np.full(n, 0.5), np.ones(n, bool))
    F = wf.compute_wall_forces(probe, world.walls)
    d, _ = agents_to_walls(pts, world.walls)
    feasible = (d.min(axis=1) >= r_probe).reshape(X.shape)  # probe disc does not overlap a wall
    Fx = F[:, 0].reshape(X.shape)
    Fy = F[:, 1].reshape(X.shape)
    back = np.maximum(0.0, -Fx)
    jy = int(np.argmin(np.abs(ys - 5.0)))
    wp = {"A_w": wf.A, "B_w": wf.B, "k": wf.k, "kappa": wf.kappa, "corner": wf.corner, "B_edge": wf.B_edge}
    return dict(grid_x=xs, grid_y=ys, r_probe=r_probe, wall_Fx_N=Fx, wall_Fy_N=Fy, wall_back_N=back,
                feasible=feasible, wall_params=json.dumps(wp)), float(back[jy][feasible[jy]].max()), wp


# ------------------------------------------------------------------ lone trap
def export_lone(path, r_probe=0.25, step=0.01):
    snap = pickle.load(open(path, "rb"))
    st, params = snap["state"], snap["params"]
    width = snap["width"]
    world, _ = BottleneckScenario(1, width, **snap["scen"]).build(seed=0)
    ids = np.array(sorted(int(i) for i in st.active_indices))
    rho = frozen_rho(st, ids)
    wall_kw = {k: params[k] for k in ("A_w", "B_w") if k in params}   # published: none -> A, B defaults
    pas = Passability(width=width, **wall_kw)
    margin = np.array([pas.margin(st.radii[i], st.desired_speeds[i], st.taus[i], rho[k]) for k, i in enumerate(ids)])
    gmax = np.array([pas.gmax(st.radii[i]) for i in ids])
    drive = gmax - margin
    blocker = int(ids[np.argmin(np.linalg.norm(st.positions[ids] - DOOR, axis=1))])

    ff, on_axis_max, wp = floor_field(params, world, r_probe, step)
    # check: on-axis maximum of the backward force equals Passability.gmax(r_probe)
    check = {"gmax_probe_passability_N": pas.gmax(r_probe), "gmax_probe_grid_N": on_axis_max}

    np.savez_compressed(
        OUT / "lone_trap.npz",
        snapshot=str(path.relative_to(PLAN)), ids=ids, blocker=blocker,
        pos=st.positions[ids], radius=st.radii[ids], vel=st.velocities[ids],
        v0=st.desired_speeds[ids], tau=st.taus[ids], mass=st.masses[ids], rho_frozen=rho,
        gmax_N=gmax, drive_N=drive, margin_N=margin,
        walls=walls_array(world), width=width, **ff)
    return {"snapshot": str(path.relative_to(PLAN)), "time_s": snap["time"], "n_active": int(len(ids)),
            "blocker": blocker, "agents": [{"id": int(i), "pos": np.round(st.positions[i], 4).tolist(),
                                            "r": round(float(st.radii[i]), 4), "speed": float(np.linalg.norm(st.velocities[i])),
                                            "gmax_N": round(float(g), 1), "drive_N": round(float(dr), 1),
                                            "margin_N": round(float(m), 1)}
                                           for i, g, dr, m in zip(ids, gmax, drive, margin)],
            "wall_params": wp, "check": check, "grid_shape": list(ff["wall_back_N"].shape)}


# ------------------------------------------------------------------ pair
class BiasField(Field):
    """Field.U plus a lateral-bias tilt of the goal drive.

    Code (hybrid.py:138-142): desired direction (e + b e_perp)/|.|, e = unit(g - x),
    e_perp = e rotated +90 deg, magnitude unchanged. The tilted field is not exactly
    conservative (e_perp turns with x); U_b uses e_perp frozen at the snapshot position:
        U_b = sum_i c_i/sqrt(1+b^2) [ |x_i - g| - b e_perp,i0 . (x_i - x_i0) ] + wall + pair.
    The residual |F_code + grad U_b| is measured on the grid and reported."""

    def __init__(self, snap, ids, b, **kw):
        super().__init__(snap, ids, **kw)
        self.b = b
        P0 = snap["state"].positions[ids]
        e = (G - P0) / np.linalg.norm(G - P0, axis=1)[:, None]
        self.eperp0 = np.column_stack([-e[:, 1], e[:, 0]])
        self.X0 = P0.copy()

    def parts(self, X):
        u_drive, u_wall, u_pair = super().parts(X)
        if self.b == 0.0:
            return u_drive, u_wall, u_pair
        P = X.reshape(-1, 2)
        s = 1.0 / np.sqrt(1.0 + self.b ** 2)
        tilt = np.sum(self.c * np.einsum("ij,ij->i", self.eperp0, P - self.X0))
        return s * u_drive - s * self.b * tilt, u_wall, u_pair


def code_force_bias(snap, ids, field, b, X):
    """The code's rest-state force at configuration X (v = 0, density frozen, others inactive)."""
    st = copy.deepcopy(snap["state"])
    st.velocities[:] = 0
    st.positions[ids] = X.reshape(-1, 2)
    others = [i for i in st.active_indices if i not in ids]
    st.active[others] = False
    params = dict(snap["params"])
    if b:
        params.update({"w2_noise": "lateral_bias", "w2_bias_b": b})
    hm = HybridSteeringModel(get_config("C1"), params)
    nl = [[] for _ in range(st.n)]
    for i in ids:
        nl[i] = [j for j in ids if j != i]
    dens = np.zeros(st.n)
    dens[ids] = field.rho
    return hm.compute_forces(st, nl, field.world.walls, dens)[ids].ravel()


def surfaces(snap, ids, b, dy, dx_bounds=(-0.3, 0.3)):
    """U on the (dy_lo, dy_hi) grid: slice (x held at the snapshot) and x-relaxed profile
    min over (dx_lo, dx_hi) within dx_bounds. Values relative to U at the snapshot (b = 0)."""
    f = BiasField(snap, ids, b, B_w=snap["params"].get("B_w", 0.08))
    X0 = snap["state"].positions[ids].ravel().copy()
    n = len(dy)
    U_slice = np.empty((n, n))
    U_relax = np.empty((n, n))
    DX = np.zeros((n, n, 2))
    hit = np.zeros((n, n), bool)
    order = sorted(range(n), key=lambda k: abs(dy[k]))
    for a in order:                 # dy_lo index (rows)
        prev = np.zeros(2)
        for c in order:             # dy_hi index (cols)
            X = X0.copy()
            X[1] += dy[a]
            X[3] += dy[c]
            U_slice[a, c] = f.U(X)

            def obj(z, X=X):
                Y = X.copy()
                Y[0] += z[0]
                Y[2] += z[1]
                return f.U(Y)
            res = minimize(obj, prev, method="L-BFGS-B", bounds=[dx_bounds, dx_bounds],
                           options={"ftol": 1e-12, "gtol": 1e-8})
            U_relax[a, c] = res.fun
            DX[a, c] = res.x
            hit[a, c] = bool(np.any(np.isclose(res.x, dx_bounds[1], atol=1e-6)))
            prev = res.x
    return f, U_slice, U_relax, DX, hit


def fit_quadratic(dy, U, half=3):
    """Least-squares quadratic on the (2 half + 1)^2 points around the grid centre -> 2x2 Hessian."""
    c = len(dy) // 2
    s = slice(c - half, c + half + 1)
    A_, B_ = np.meshgrid(dy[s], dy[s], indexing="ij")
    a, b_, u = A_.ravel(), B_.ravel(), U[s, s].ravel()
    M = np.column_stack([np.ones_like(a), a, b_, a * a, a * b_, b_ * b_])
    coef, *_ = np.linalg.lstsq(M, u, rcond=None)
    return np.array([[2 * coef[3], coef[4]], [coef[4], 2 * coef[5]]]), coef[1:3]


def barrier_on_grid(U, escaped, c):
    """Lowest level at which the sublevel set {U < level} connects the grid centre to an
    escaped point (forward displacement at its bound): a grid estimate of the escape barrier."""
    from scipy.ndimage import label
    if not escaped.any():
        return None
    levels = np.unique(U[np.isfinite(U)])
    lo, hi = 0, len(levels) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        lab, _ = label(U <= levels[mid])
        k = lab[c, c]
        if k and np.any(escaped & (lab == k)):
            hi = mid
        else:
            lo = mid + 1
    return float(levels[lo] - U[c, c])


def export_pair(path, n_grid=101, half_range=0.5):
    snap = pickle.load(open(path, "rb"))
    st = snap["state"]
    ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
    assert len(ids) == 2, "pair snapshot expected"
    key = os.path.basename(path)
    pred = json.load(open(PLAN / "wave2b/data/a5_predict.json"))[key]
    biases = sorted(float(k[4:]) for k in pred if k.startswith("bias"))
    held = [b for b in biases if pred[f"bias{b}"]["pred_freed"] is False]
    freed = [b for b in biases if pred[f"bias{b}"]["pred_freed"] is True]
    b_fold = min(freed)
    b_held = max([b for b in held if b < b_fold], default=0.0)
    stored = next(r for r in json.load(open(PLAN / "wave2b/data/a3_pair_stability.json"))
                  if os.path.basename(r["snap"]) == key)

    dy = np.linspace(-half_range, half_range, n_grid)
    out = {}
    for tag, b in (("b0", 0.0), ("bfold", b_fold)):
        t0 = time.perf_counter()
        f, Us, Ur, DX, hit = surfaces(snap, ids, b, dy)
        out[tag] = (f, Us, Ur, DX, hit, time.perf_counter() - t0)

    f0 = out["b0"][0]
    X0 = st.positions[ids].ravel().copy()
    U0 = f0.U(X0)
    H = f0.hess(X0)                       # same routine and step as the stored A3 result
    ev = np.linalg.eigvalsh(H)
    lat, lon = [1, 3], [0, 2]
    H_lat = H[np.ix_(lat, lat)]
    H_schur = H_lat - H[np.ix_(lat, lon)] @ np.linalg.solve(H[np.ix_(lon, lon)], H[np.ix_(lon, lat)])
    _, Us0, Ur0, DX0, _, _ = out["b0"]
    # curvature check on a dedicated fine stencil (step 1 mm) around the snapshot
    dyf = np.linspace(-0.01, 0.01, 21)
    _, Usf, Urf, _, _ = surfaces(snap, ids, 0.0, dyf)
    Hs_fit, g_s = fit_quadratic(dyf, Usf, half=10)
    Hr_fit, g_r = fit_quadratic(dyf, Urf, half=10)
    c = n_grid // 2

    def strict_min(U):
        """Local: centre below its 8 neighbours on the export grid, and PD on the fine stencil."""
        nb = U[c - 1:c + 2, c - 1:c + 2].copy()
        nb[1, 1] = np.inf
        return bool(U[c, c] < nb.min())

    def local_minima(U, escaped=None):
        """Interior grid points below all 8 neighbours, excluding points whose relaxed forward
        displacement sits at its bound (those belong to the escape channel, not to a rest state)."""
        from scipy.ndimage import minimum_filter
        lm = U == minimum_filter(U, size=3, mode="nearest")
        lm[0, :] = lm[-1, :] = lm[:, 0] = lm[:, -1] = False
        if escaped is not None:
            lm &= ~escaped
        return [[round(float(dy[i]), 3), round(float(dy[j]), 3), round(float(U[i, j] - U0), 4)] for i, j in zip(*np.nonzero(lm))]

    # conservative-field checks against the code's own force
    chk = {}
    for tag, b in (("b0", 0.0), ("bfold", b_fold)):
        f = out[tag][0]
        res, clamped = [], 0
        q = lambda fr: c + int(round(fr * c))  # noqa: E731
        for a_, c_ in [(c, c), (q(.25), q(-.25)), (q(-.4), q(.1)), (q(.5), q(.5)), (q(-.5), q(-.5)), (q(.9), q(-.9))]:
            X = X0.copy()
            X[1] += dy[a_]
            X[3] += dy[c_]
            Fc = code_force_bias(snap, ids, f, b, X)
            if np.abs(Fc).max() >= 1e5:   # code clamps |F| at 1e6 N (deep overlap): not comparable
                clamped += 1
                continue
            res.append(float(np.max(np.abs(Fc + f.grad(X)))))
        chk[tag] = max(res)
        chk[tag + "_clamped_points_skipped"] = clamped
    # density-frozen check exactly as A3 (all residual agents active, snapshot state)
    chk["a3_style_snapshot"] = float(np.max(np.abs(code_force(snap, ids, f0).ravel() + f0.grad(X0))))

    params = snap["params"]
    pas = Passability(width=snap["width"], **{k: params[k] for k in ("A_w", "B_w") if k in params})
    margin = np.array([pas.margin(st.radii[i], st.desired_speeds[i], st.taus[i], f0.rho[k]) for k, i in enumerate(ids)])
    ff, on_axis_max, wp = floor_field(params, f0.world)
    save = {"snapshot": str(Path(os.path.normpath(path)).relative_to(PLAN)), "ids": np.array(ids),
            "margin_N": margin, "gmax_N": np.array([pas.gmax(st.radii[i]) for i in ids]), **ff,
            "pos": st.positions[ids], "radius": st.radii[ids], "vel": st.velocities[ids],
            "rho_frozen": f0.rho, "drive_c_N": f0.c, "walls": walls_array(f0.world), "width": snap["width"],
            "dy": dy, "b_fold": b_fold, "b_held": b_held, "U_ref_J": U0}
    for tag in ("b0", "bfold"):
        _, Us, Ur, DX, hit, _ = out[tag]
        save[f"U_slice_{tag}_J"] = Us - U0
        save[f"U_relax_{tag}_J"] = Ur - U0
        save[f"dx_relax_{tag}_m"] = DX
        save[f"dx_at_bound_{tag}"] = hit
    np.savez_compressed(OUT / "pair_landscape.npz", **save)

    return {"snapshot": save["snapshot"], "ids": ids, "pos": np.round(st.positions[ids], 4).tolist(),
            "radius": np.round(st.radii[ids], 4).tolist(), "max_speed": float(np.linalg.norm(st.velocities[ids], axis=1).max()),
            "b_held": b_held, "b_fold": b_fold, "grid": {"n": n_grid, "half_range_m": half_range},
            "hessian_eig_recomputed_N_per_m": np.round(ev, 2).tolist(),
            "hessian_eig_stored_N_per_m": np.round(stored["hess_eig_N_per_m"], 2).tolist(),
            "H_lateral_block": np.round(H_lat, 2).tolist(), "H_lateral_schur": np.round(H_schur, 2).tolist(),
            "fit_slice_H": np.round(Hs_fit, 2).tolist(), "fit_slice_grad": np.round(g_s, 4).tolist(),
            "fit_relax_H": np.round(Hr_fit, 2).tolist(), "fit_relax_grad": np.round(g_r, 4).tolist(),
            "eig_fit_slice": np.round(np.linalg.eigvalsh(Hs_fit), 2).tolist(),
            "eig_H_lateral": np.round(np.linalg.eigvalsh(H_lat), 2).tolist(),
            "eig_fit_relax": np.round(np.linalg.eigvalsh(Hr_fit), 2).tolist(),
            "eig_H_schur": np.round(np.linalg.eigvalsh(H_schur), 2).tolist(),
            "strict_min_b0_slice": strict_min(Us0) and bool(np.all(np.linalg.eigvalsh(Hs_fit) > 0)),
            "strict_min_b0_relax": strict_min(Ur0) and bool(np.all(np.linalg.eigvalsh(Hr_fit) > 0)),
            "strict_min_bfold_relax_at_snapshot": strict_min(out["bfold"][2]),
            "barrier_relax_b0_J": barrier_on_grid(Ur0 - U0, out["b0"][4], c),
            "barrier_relax_bfold_J": barrier_on_grid(out["bfold"][2] - U0, out["bfold"][4], c),
            "local_minima_b0_slice": local_minima(out["b0"][1]),
            "local_minima_b0_relax": local_minima(out["b0"][2], out["b0"][4]),
            "local_minima_bfold_slice": local_minima(out["bfold"][1]),
            "local_minima_bfold_relax": local_minima(out["bfold"][2], out["bfold"][4]),
            "relax_hits_dx_bound_bfold": int(out["bfold"][4].sum()), "relax_hits_dx_bound_b0": int(out["b0"][4].sum()),
            "max_abs_Fcode_plus_gradU_N": chk,
            "stuck_alone_margin_N": np.round(margin, 1).tolist(), "floor_wall_params": wp,
            "floor_gmax_probe_grid_N": on_axis_max, "floor_gmax_probe_passability_N": pas.gmax(0.25),
            "grid_seconds": {t: round(out[t][5], 1) for t in out}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-grid", type=int, default=101)
    ap.add_argument("--half-range", type=float, default=0.5)
    ap.add_argument("--only", choices=["lone", "pair"], default=None, help="re-export one scene, keep the other")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    rp = OUT / "export_report.json"
    rep = json.load(open(rp)) if a.only and rp.exists() else {}
    if a.only in (None, "lone"):
        rep["lone"] = export_lone(LONE_SNAP)
    if a.only in (None, "pair"):
        rep["pair"] = export_pair(PAIR_SNAP, a.n_grid, a.half_range)
    rep["seconds"] = round(time.perf_counter() - t0, 1)
    json.dump(rep, open(OUT / "export_report.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))
