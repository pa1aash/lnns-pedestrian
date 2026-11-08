"""Export the physics data behind the hero figure (Fig. 1) for the Blender render and the LaTeX overlay.

    PYTHONPATH=code /Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python experiments/hero/export_hero.py

Writes data/derived/hero/{lone.npz, pair.npz, inset.json, hero_physics.json}. Every number comes from the
simulator's own routines (experiments/hero/hero_phys.py): corrected-forward flags (w2_numerics = fixed,
spawn = rejection, w2_orca = rvo2, w2_crush = off, w2_wall_corner = convex_union).

  * lone scene: data/E1/library/E1b_seed52.pkl (lone keystone, blocker 19);
  * pair scene: PAIR_SNAP, a production E7b pair (B_w = 0.04), chosen by experiments/hero/select_pair.py;
  * inset: the whole room for seed 52 (walls, the 100 initial positions rebuilt with the simulator).
"""
import copy
import json
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import hero_phys as hp  # noqa: E402
import teff  # noqa: E402
from w2lib import DOOR, Passability, build  # noqa: E402
from sim.core.agent import AgentState  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402
from sim.steering.hybrid import HybridSteeringModel  # noqa: E402

REPO = hp.REPO
OUT = REPO / "data" / "derived" / "hero"
LONE_SNAP = REPO / "data/E1/library/E1b_seed52.pkl"
# Pair: nearest production analogue of the pilot w25_B0.04_seed43 (see data/derived/hero/pair_selection.json):
# members at the jamb faces, near-symmetric, both passable alone, strict minimum at b = 0, fold at b = 0.031.
PAIR_SNAP = REPO / "data/E7b/library/E7b_B0.04_seed397.pkl"
B_TILT = 0.035            # the tilt of the "tilted" pair ribbon: just past the snapshot's fold
SIGMA_T = 0.07            # m/s, per-step noise whose rate matches C3 RVO2 on the lone keystones (E2)
G = hp.G
LUTS = np.load(REPO / "data/derived/hero/luts.npz")


def rel(p):
    return str(Path(p).relative_to(REPO))


def hexcol(name, v, lo, hi):
    t = float(np.clip((v - lo) / (hi - lo), 0, 1))
    r, g, b = (LUTS[name][int(round(t * 255))] * 255).round().astype(int)
    return "#%02X%02X%02X" % (r, g, b)


def floor_field(snap, r_probe=0.25, step=0.005, x=(8.8, 11.0), y=(3.6, 6.4)):
    """Backward wall force on a lone probe agent of radius r_probe at rest at every grid point, from the
    WallForces the simulator builds for this snapshot (same law, parameters, corner rule)."""
    hm, _ = hp.model_of(snap)
    wf = hm.wall_forces
    world = hp.world_of(snap)
    xs = np.arange(x[0], x[1] + 1e-9, step)
    ys = np.arange(y[0], y[1] + 1e-9, step)
    X, Y = np.meshgrid(xs, ys, indexing="xy")
    pts = np.column_stack([X.ravel(), Y.ravel()])
    n = len(pts)
    probe = AgentState(pts.copy(), np.zeros((n, 2)), np.tile(G, (n, 1)), np.full(n, r_probe), np.ones(n),
                       np.full(n, 80.0), np.full(n, 0.5), np.ones(n, bool))
    F = wf.compute_wall_forces(probe, world.walls)
    d, _ = agents_to_walls(pts, world.walls)
    feasible = (d.min(axis=1) >= r_probe).reshape(X.shape)
    back = np.maximum(0.0, -F[:, 0]).reshape(X.shape)
    jy = int(np.argmin(np.abs(ys - 5.0)))
    clearance = (d.min(axis=1) - r_probe).reshape(X.shape)      # signed distance to the excluded zone (m); >= 0 is feasible
    return dict(grid_x=xs, grid_y=ys, wall_back_N=back, feasible=feasible, clearance=clearance), float(back[jy][feasible[jy]].max()), \
        {"A_w": wf.A, "B_w": wf.B, "corner": wf.corner}


def walls_array(world):
    return np.array([[*w.start, *w.end] for w in world.walls], float)


# ------------------------------------------------------------------ lone
def export_lone(rep):
    snap = pickle.load(open(LONE_SNAP, "rb"))
    st = snap["state"]
    ids = sorted(int(i) for i in st.active_indices)
    blocker = int(ids[np.argmin(np.linalg.norm(st.positions[ids] - DOOR, axis=1))])
    pas = Passability(width=snap["width"], **{k: snap["params"][k] for k in ("A_w", "B_w") if k in snap["params"]})
    rho = hp.frozen_rho(st, ids)
    margin = np.array([pas.margin(st.radii[i], st.desired_speeds[i], st.taus[i], rho[k]) for k, i in enumerate(ids)])
    F = hp.forces_at(snap, ids)
    k_b = ids.index(blocker)
    e_hat = (G - st.positions[blocker]) / np.linalg.norm(G - st.positions[blocker])
    m, v0, tau = st.masses[blocker], st.desired_speeds[blocker], st.taus[blocker]
    w_o = 1.0 - HybridSteeringModel._sigmoid(rho[k_b], 4.0, 2.0)
    F_orca = float(w_o * m * v0 / 0.5) * e_hat
    # force balance on the held agents (C1: drive + partner + wall) and the lone-blocker forces
    bal = {"max_abs_total_N": float(np.abs(F["total"]).max()),
           "max_abs_parts_minus_total_N": float(np.abs(F["sum_parts"] - F["total"]).max()),
           "per_agent_total_N": {int(i): np.round(F["total"][k], 6).tolist() for k, i in enumerate(ids)},
           "blocker": {"drive_N": F["drive"][k_b].round(3).tolist(), "wall_N": F["wall"][k_b].round(3).tolist(),
                       "partner_N": F["partner"][k_b].round(3).tolist(), "orca_rest_N": F_orca.round(3).tolist()}}
    # ribbons
    rb = hp.lone_ribbon(snap, blocker)
    x, Uo, Ua = rb["x"], rb["U_own"], rb["U_added"]            # both with the neighbours pinned (batch HF)
    mins_o, maxs_o = hp.stationary_points(x, Uo)
    mins_oa, maxs_oa = hp.stationary_points(x, rb["U_own_alone"])
    mins_a, maxs_a = hp.stationary_points(x, Ua)
    mins_aa, maxs_aa = hp.stationary_points(x, rb["U_added_alone"])
    vs_model = hp.check_ribbon_vs_model(snap, blocker, rb)
    xf = float(st.positions[blocker, 0])
    U0o = float(np.interp(mins_o[0], x, Uo))
    barrier = float(np.interp(maxs_o[0], x, Uo)) - U0o
    gate = [json.loads(l) for l in open(REPO / "data/BAR/gate.jsonl") if '"E1b_seed52"' in l][0]
    kT = teff.kT_eff(SIGMA_T, 0.01, float(tau))
    dimple = None
    if mins_a:
        dimple = {"x_min": mins_a, "x_max": maxs_a,
                  "depth_J": float(np.interp(maxs_a[0], x, Ua) - np.interp(mins_a[0], x, Ua))}
    ribbon_checks = {
        "own_has_minimum_and_barrier": bool(len(mins_o) == 1 and len(maxs_o) == 1),
        "own_x_min": mins_o, "own_x_barrier": maxs_o, "own_barrier_J": barrier,
        "own_alone_x_min": mins_oa, "own_alone_x_barrier": maxs_oa,
        "own_alone_barrier_J": float(np.interp(maxs_oa[0], x, rb["U_own_alone"]) - np.interp(mins_oa[0], x, rb["U_own_alone"])),
        "gate_alone_barrier_J": gate["dU_bar"]["alone"], "gate_1d_axis_alone_J": gate["dU_1d_axis_alone"],
        "barrier_vs_gate_frozen_rel": abs(barrier / gate["dU_bar"]["frozen"] - 1),
        "frozen_x": xf, "own_min_minus_frozen_m": mins_o[0] - xf,
        "own_U_frozen_above_min_J": float(np.interp(xf, x, Uo) - U0o),
        "gate_frozen_neighbours_barrier_J": gate["dU_bar"]["frozen"],
        "net_force_alone_at_frozen_N": float(rb["c"] + np.interp(xf, x, rb["wall_Fx"])),
        "added_has_no_stationary_point": bool(not mins_a and not maxs_a),
        "added_dimple": dimple,
        "added_alone_dimple": {"x_min": mins_aa, "x_max": maxs_aa,
                               "depth_J": float(np.interp(maxs_aa[0], x, rb["U_added_alone"]) - np.interp(mins_aa[0], x, rb["U_added_alone"])) if mins_aa else 0.0},
        "neighbour_push_Fx_N_at_frozen_and_along": [float(np.interp(v, x, rb["push_Fx"])) for v in (xf, 9.75, 9.79, 9.86)],
        "ribbon_vs_code_force": vs_model,
        "added_U_drop_frozen_to_x_end_J": float(np.interp(xf, x, Ua) - Ua[-1]),
        "kT_eff_J": kT, "sigma_m_s": SIGMA_T, "tau_s": float(tau), "kT_over_barrier": kT / barrier,
        "c_own_N": rb["c"], "c_orca_N": rb["c_orca"], "w_o": rb["w_o"], "tau_orca_s": 0.5,
        "c_v_eff_N": float(F["drive"][k_b] @ e_hat), "rho_frozen": float(rho[k_b])}
    # added-drive ball: where it ends up (no stationary point -> the lower end of the drawn range)
    ff, on_axis, wp = floor_field(snap)
    # whole-room data for the inset: the 100 initial positions rebuilt with the simulator (seed 52, CF flags)
    flags = dict(hp.CF, spawn="rejection")
    sim = build("C1", seed=52, flags=flags)
    s0 = sim.state
    chk = {}
    for i in ids:
        chk[int(i)] = {"d_radius": float(abs(s0.radii[i] - st.radii[i])), "d_v0": float(abs(s0.desired_speeds[i] - st.desired_speeds[i])),
                       "d_tau": float(abs(s0.taus[i] - st.taus[i]))}
    world = hp.world_of(snap)
    wall_all = walls_array(world)
    inset = {"walls": wall_all.round(4).tolist(), "initial_positions": s0.positions.round(4).tolist(),
             "residual": [{"id": int(i), "pos": st.positions[i].round(4).tolist(), "r": round(float(st.radii[i]), 4),
                           "margin_N": round(float(margin[k]), 2), "colour": hexcol("cividis", margin[k], -150, 150)}
                          for k, i in enumerate(ids)],
             "n_initial": int(len(s0.positions)), "check_initial_vs_snapshot": chk,
             "initial_inside_room": bool(np.all((s0.positions > 0) & (s0.positions < 10)))}
    json.dump(inset, open(OUT / "inset.json", "w"))
    np.savez_compressed(OUT / "lone.npz", snapshot=rel(LONE_SNAP), ids=np.array(ids), blocker=blocker,
                        pos=st.positions[ids], radius=st.radii[ids], margin_N=margin,
                        drive_N=F["drive"], wall_N=F["wall"], partner_N=F["partner"], orca_N=F_orca,
                        walls=walls_array(world), width=snap["width"],
                        rib_x=x, rib_Uown=Uo, rib_Uadd=Ua, rib_Uadd_alone=rb["U_added_alone"], rib_y=rb["y"],
                        kT_J=kT, frozen_x=xf, x_min_own=mins_o[0], x_top_own=maxs_o[0], **ff)
    rep["lone"] = {"snapshot": rel(LONE_SNAP), "time_s": snap["time"], "ids": ids, "blocker": blocker,
                   "pos": st.positions[ids].round(4).tolist(), "r": st.radii[ids].round(4).tolist(),
                   "margin_N": margin.round(2).tolist(), "wall_params": wp,
                   "floor_gmax_probe_grid_N": on_axis, "floor_gmax_probe_passability_N": pas.gmax(0.25),
                   "force_balance": bal, "ribbon": ribbon_checks, "initial_position_check": chk}


# ------------------------------------------------------------------ pair
def relax_dynamic(snap, ids, bias, T=120.0, h=0.01):
    """Overdamped relaxation of the code's rest-state force (as pilot A5): freed if a member passes x > 10.3 m."""
    hm, _ = hp.model_of(snap, bias)
    st = copy.deepcopy(snap["state"])
    st.velocities[:] = 0
    world = hp.world_of(snap)
    rho = hp.frozen_rho(st, ids)
    dens = np.zeros(st.n)
    dens[ids] = rho
    k = np.array(ids)
    gain = (st.taus[k] / st.masses[k])[:, None]
    nl = [[] for _ in range(st.n)]
    for i in ids:
        nl[i] = [j for j in ids if j != i]
    t = 0.0
    while t < T:
        F = hm.compute_forces(st, nl, world.walls, dens)[k]
        if np.abs(F).max() < 0.05:
            return {"freed": False, "t": t}
        st.positions[k] += h * gain * F
        t += h
        if (st.positions[k, 0] > 10.3).any():
            return {"freed": True, "t": t}
    return {"freed": None, "t": t}


def hessian(f, X, h=1e-4):
    n = len(X)
    H = np.zeros((n, n))
    U0 = f.U(X)
    for a in range(n):
        for b in range(a, n):
            ea = np.zeros(n); ea[a] = h
            eb = np.zeros(n); eb[b] = h
            H[a, b] = H[b, a] = ((f.U(X + ea) - 2 * U0 + f.U(X - ea)) / h ** 2 if a == b else
                                 (f.U(X + ea + eb) - f.U(X + ea - eb) - f.U(X - ea + eb) + f.U(X - ea - eb)) / (4 * h * h))
    return H


def export_pair(rep):
    snap = pickle.load(open(PAIR_SNAP, "rb"))
    st = snap["state"]
    ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
    assert len(ids) == 2
    pas = Passability(width=snap["width"], **{k: snap["params"][k] for k in ("A_w", "B_w") if k in snap["params"]})
    rho = hp.frozen_rho(st, ids)
    margin = np.array([pas.margin(st.radii[i], st.desired_speeds[i], st.taus[i], rho[k]) for k, i in enumerate(ids)])
    F0 = hp.forces_at(snap, ids)
    Fb = hp.forces_at(snap, ids, bias=B_TILT)
    bias_inc = Fb["drive"] - F0["drive"]            # lateral-bias increment of the drive, per member
    # potential checks
    f0 = hp.RestField(snap, ids)
    H = hessian(f0, f0.X0)
    ev = np.linalg.eigvalsh(H)
    res0 = float(np.abs(hp.forces_at(snap, ids)["total"].ravel() + f0.grad(f0.X0)).max())
    # ribbons: common lateral shift c, relaxed over the opposed coordinate and the forward positions
    cs = np.linspace(-0.25, 0.25, 101)
    t0 = time.perf_counter()
    U0, arg0 = hp.pair_ribbon(snap, ids, 0.0, cs)
    Ub, argb = hp.pair_ribbon(snap, ids, B_TILT, cs)
    mn0, mx0 = hp.stationary_points(cs, U0)
    mnb, mxb = hp.stationary_points(cs, Ub)
    # bracket the fold with the same ribbon criterion and with the code's relaxation
    fold_lo, fold_hi = 0.0, 0.12
    cf = np.linspace(-0.12, 0.12, 25)
    for _ in range(9):
        mid = 0.5 * (fold_lo + fold_hi)
        Um, _ = hp.pair_ribbon(snap, ids, mid, cf)
        d = np.diff(Um) / np.diff(cf)
        if np.any((d[:-1] < 0) & (d[1:] > 0)):
            fold_lo = mid
        else:
            fold_hi = mid
    b_fold = 0.5 * (fold_lo + fold_hi)
    dyn = {str(b): relax_dynamic(snap, ids, b) for b in (0.0, 0.5 * b_fold, 0.9 * b_fold, B_TILT, 0.05)}
    # residual of the tilted potential against the code's tilted force
    fb = hp.RestField(snap, ids, B_TILT)
    resb = []
    for dc in (0.0, 0.05, -0.05, 0.1):
        X = f0.X0.copy()
        X[1] += dc
        X[3] += dc
        Fc = hp.forces_at(snap, ids, bias=B_TILT, X=X.reshape(-1, 2))["total"].ravel()
        resb.append(float(np.abs(Fc + fb.grad(X)).max()))
    ff, on_axis, wp = floor_field(snap)
    world = hp.world_of(snap)
    np.savez_compressed(OUT / "pair.npz", snapshot=rel(PAIR_SNAP), ids=np.array(ids), pos=st.positions[ids],
                        radius=st.radii[ids], margin_N=margin, drive_N=F0["drive"], wall_N=F0["wall"],
                        partner_N=F0["partner"], bias_N=bias_inc, walls=walls_array(world), width=snap["width"],
                        rib_c=cs, rib_U0=U0, rib_Ub=Ub, b_tilt=B_TILT, b_fold=b_fold, **ff)
    rep["pair"] = {"snapshot": rel(PAIR_SNAP), "time_s": snap["time"], "ids": ids, "pos": st.positions[ids].round(4).tolist(),
                   "r": st.radii[ids].round(4).tolist(), "margin_N": margin.round(2).tolist(), "wall_params": wp,
                   "force_balance_b0": {"max_abs_total_N": float(np.abs(F0["total"]).max()),
                                        "max_abs_parts_minus_total_N": float(np.abs(F0["sum_parts"] - F0["total"]).max()),
                                        "member0_drive_wall_partner_N": [F0["drive"][0].round(3).tolist(), F0["wall"][0].round(3).tolist(),
                                                                         F0["partner"][0].round(3).tolist()]},
                   "bias": {"b_tilt": B_TILT, "b_fold_ribbon": b_fold, "increment_N_per_member": bias_inc.round(4).tolist(),
                            "drive_tilted_total_N": Fb["drive"].round(3).tolist()},
                   "hessian_eig_N_per_m": ev.round(2).tolist(), "strict_min_b0_hessian": bool((ev > 0).all()),
                   "ribbon_b0_minima": mn0, "ribbon_b0_maxima": mx0, "ribbon_tilt_minima": mnb, "ribbon_tilt_maxima": mxb,
                   "ribbon_b0_strict_min_at_0": bool(len(mn0) == 1 and abs(mn0[0]) < 2e-3),
                   "ribbon_tilt_has_no_minimum": bool(len(mnb) == 0),
                   "ribbon_U_range_J": {"b0": [float(U0.min()), float(U0.max())], "tilt": [float(Ub.min()), float(Ub.max())]},
                   "ribbon_U_at_c": {str(c): [float(np.interp(c, cs, U0)), float(np.interp(c, cs, Ub))] for c in (-0.2, -0.1, 0.1, 0.2)},
                   "relax_dynamic": dyn, "residual_force_plus_gradU_b0_N": res0, "residual_tilted_N": resb,
                   "ribbon_seconds": round(time.perf_counter() - t0, 1)}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    rep = {}
    t0 = time.perf_counter()
    export_lone(rep)
    export_pair(rep)
    rep["seconds"] = round(time.perf_counter() - t0, 1)
    json.dump(rep, open(OUT / "hero_physics.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))
