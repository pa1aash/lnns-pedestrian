"""Stuck-alone margin of the 393 E1 deadlock blockers, their offsets and lone rest-state stiffness
(FIX_PLAN A-5, item 05-1).

Inputs: data/derived/E1_keystone.json (blocker, margin_C1 = g_max(r) - m v0/tau, keystone K1 result per snapshot),
data/E1/keystone.jsonl (K1 final rest positions), data/E1/E1_runs.jsonl (deadlock type), data/E1/library (snapshots,
only for the mode's wall parameters). No simulation is run: the lone rest-state Hessian is a central finite
difference of the static rest field (wall force + goal drive at v = 0) of the simulator's WallForces.
Run from the worktree root:  .venv/bin/python experiments/fixan/fix_a5.py
"""
import json
import os
import pickle
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
import e1lib  # noqa: E402  (chdirs to code/)
from sim.core.agent import AgentState  # noqa: E402

OUT = os.path.join(ROOT, "data", "derived", "fix_a5.json")
RNG = np.random.default_rng(20261109)
GOAL = np.array([11.0, 5.0])
H = 1e-5  # finite-difference step (m)


def wilson(k, n, z=1.959964):
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [float(max(0.0, c - h)), float(min(1.0, c + h))]


def boot_median(x, n=2000):
    x = np.asarray(x)
    b = np.median(RNG.choice(x, (n, len(x)), replace=True), axis=1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def qsum(x):
    x = np.asarray(x, float)
    return {"n": int(len(x)), "min": float(x.min()), "p05": float(np.percentile(x, 5)),
            "median": float(np.median(x)), "median_ci95": boot_median(x), "p95": float(np.percentile(x, 95)),
            "max": float(x.max())}


def rest_field(wf, walls, p, r, v0, tau, m):
    """Force on a lone agent at rest at p: wall force + m v0/tau toward the goal (Weidmann factor 1 alone)."""
    st = AgentState(p[None, :].copy(), np.zeros((1, 2)), GOAL[None, :].copy(), np.array([r]), np.array([v0]),
                    np.array([m]), np.array([tau]), np.ones(1, bool))
    e = GOAL - p
    fac = e1lib.weidmann_factor(0.0)
    return wf.compute_wall_forces(st, walls)[0] + m * v0 * fac / tau * e / np.linalg.norm(e)


def hessian(wf, walls, p, *a):
    """K = -dF/dx (symmetrised), the Hessian of the rest potential."""
    J = np.zeros((2, 2))
    for j in range(2):
        dp = np.zeros(2)
        dp[j] = H
        J[:, j] = (rest_field(wf, walls, p + dp, *a) - rest_field(wf, walls, p - dp, *a)) / (2 * H)
    K = -0.5 * (J + J.T)
    return K, float(np.max(np.abs(J - J.T)))


def main():
    ks = json.load(open(os.path.join(ROOT, "data", "derived", "E1_keystone.json")))["modes"]
    k1 = {x["job_id"]: x for x in e1lib.load_runs(os.path.join(ROOT, "data", "E1", "keystone.jsonl"))
          if x["test"] == "K1"}
    runs = {(x["mode"], x["seed"]): x for x in e1lib.load_runs(os.path.join(ROOT, "data", "E1", "E1_runs.jsonl"))}
    rows = []
    for mode in ("E1a", "E1b"):
        for s in ks[mode]["per_snapshot"]:
            R = runs[(mode, s["seed"])]
            b = s["blocker"]
            at = {a["id"]: a for a in R["attrs"]}
            pos = {int(x["id"]): np.array(x["pos"]) for x in R["residual"]}
            kk = k1[f"{mode}_seed{s['seed']}|K1"]
            fp = kk["final_pos"].get(str(b))
            rows.append({"mode": mode, "seed": s["seed"], "blocker": b, "margin": s["blocker_margin_C1"],
                         "held": bool(s["K1_held"]), "class": s["class"], "n_resid": s["n_resid"],
                         "dtype": R["deadlock_type"]["type"], "snap_dy": float(pos[b][1] - 5.0),
                         "snap_x": float(pos[b][0]), "rest_pos": fp, "r": at[b]["r"], "v0": at[b]["v0"],
                         "tau": at[b]["tau"], "m": at[b].get("m", 80.0), "snap": kk["snap"],
                         "balance": kk.get("balance_end")})
    n = len(rows)
    marg = np.array([x["margin"] for x in rows])
    held = np.array([x["held"] for x in rows])
    out = {"script": "experiments/fixan/fix_a5.py", "n_blockers": n,
           "n_by_mode": {m: sum(x["mode"] == m for x in rows) for m in ("E1a", "E1b")}}
    edges = [-50.0, -25.0, -10.0, 0.0, 10.0, 25.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0]
    lo, hi = min(edges[0], marg.min() - 1), max(edges[-1], marg.max() + 1)
    edges[0], edges[-1] = float(np.floor(lo)), float(np.ceil(hi))
    out["margin_hist"] = {
        "method": "blocker stuck-alone margin margin_C1 = g_max(r) - m v0/tau (N, rest on the door axis, alone), "
                  "blocker = residual agent nearest the door centre; both modes pooled; outer edges = data range",
        "edges_N": edges, "counts": np.histogram(marg, edges)[0].tolist(),
        "counts_E1a": np.histogram(marg[[x["mode"] == "E1a" for x in rows]], edges)[0].tolist(),
        "counts_E1b": np.histogram(marg[[x["mode"] == "E1b" for x in rows]], edges)[0].tolist()}
    out["margin_summary"] = qsum(marg)
    pos = marg > 0
    out["criterion"] = {
        "method": "keystone K1: blocker alone restarted (C1, sigma 0, 120 s); held = not exited",
        "n": n, "n_pos_margin": int(pos.sum()), "n_pos_margin_held": int((pos & held).sum()),
        "n_neg_margin": int((~pos).sum()), "n_neg_margin_held": int((~pos & held).sum()),
        "agree": int((pos == held).sum()), "agree_wilson95": wilson(int((pos == held).sum()), n),
        "n_within_10N": int((np.abs(marg) <= 10).sum()),
        "n_pos_within_10N": int(((marg > 0) & (marg <= 10)).sum()),
        "n_neg_within_10N": int(((marg <= 0) & (marg >= -10)).sum()),
        "n_within_25N": int((np.abs(marg) <= 25).sum()),
        "min_pos_margin_N": float(marg[pos].min()), "max_neg_margin_N": float(marg[~pos].max())}
    neg = [x for x in rows if x["margin"] <= 0]
    out["negative_margin"] = {
        "method": "blockers with margin <= 0; deadlock_type from the E1 detector (agents within reach of the door); "
                  "snapshot lateral offset dy = y - 5 of the blocker and of its nearest partner",
        "n": len(neg), "n_dtype_pair": sum(x["dtype"] == "pair" for x in neg),
        "n_resid_hist": {str(k): sum(x["n_resid"] == k for x in neg) for k in sorted({x["n_resid"] for x in neg})},
        "cases": [{"mode": x["mode"], "seed": x["seed"], "margin_N": x["margin"], "deadlock_type": x["dtype"],
                   "n_resid": x["n_resid"], "class": x["class"], "blocker_dy_m": x["snap_dy"]} for x in neg]}
    # lateral offsets of lone blockers (held alone)
    lone = [x for x in rows if x["held"]]
    sdy = np.abs([x["snap_dy"] for x in lone])
    rdy = np.abs([x["rest_pos"][1] - 5.0 for x in lone if x["rest_pos"]])
    out["lone_offsets"] = {
        "method": "|y - 5| of the held-alone blockers: in the deadlock snapshot (others present) and at the end of "
                  "the K1 restart alone (stationary rest state)",
        "n": len(lone), "snapshot_abs_dy_m": qsum(sdy),
        "snapshot_hist_edges_m": [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5],
        "snapshot_hist_counts": np.histogram(sdy, [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5])[0].tolist(),
        "n_snapshot_beyond_0p5": int((sdy > 0.5).sum()),
        "rest_abs_dy_m": qsum(rdy), "n_rest_dy_above_1mm": int((rdy > 1e-3).sum()),
        "rest_x_m": qsum([x["rest_pos"][0] for x in lone if x["rest_pos"]]),
        "neg_margin_snapshot_abs_dy_m": qsum(np.abs([x["snap_dy"] for x in neg]))}
    # lateral Hessian eigenvalue at the lone rest states
    lam_lat, lam_ax, resid, asym, nonaxis = [], [], [], [], 0
    for x in lone:
        snap = pickle.load(open(os.path.join(e1lib.ELIB, x["snap"]), "rb"))
        sim = e1lib.restore(snap, "C1", flags=e1lib.MODE_FLAGS[x["mode"]])
        wf, walls = sim.steering.wall_forces, sim.world.walls
        p = np.array(x["rest_pos"], float)
        a = (x["r"], x["v0"], x["tau"], x["m"])
        resid.append(float(np.linalg.norm(rest_field(wf, walls, p, *a))))
        K, asy = hessian(wf, walls, p, *a)
        asym.append(asy)
        ev, vec = np.linalg.eigh(K)
        il = int(np.argmax(np.abs(vec[1])))        # eigenvector closest to the lateral (y) direction
        lam_lat.append(float(ev[il]))
        lam_ax.append(float(ev[1 - il]))
        nonaxis += int(abs(vec[1, il]) < 0.99)
    lam_lat, lam_ax = np.array(lam_lat), np.array(lam_ax)
    out["lone_hessian"] = {
        "method": "K = -sym(dF/dx) of the static rest field F = wall force (simulator WallForces, mode's walls) + "
                  "m v0/tau toward the goal (11, 5), at v = 0 and the K1 stationary rest position; central differences, "
                  "h = 1e-5 m; lateral eigenvalue = eigenvector nearest the y direction (N/m)",
        "n": int(len(lam_lat)), "lateral_N_per_m": qsum(lam_lat), "axial_N_per_m": qsum(lam_ax),
        "n_lateral_positive": int((lam_lat > 0).sum()), "n_lateral_negative": int((lam_lat <= 0).sum()),
        "n_axial_positive": int((lam_ax > 0).sum()),
        "ratio_axial_over_lateral": qsum(lam_ax / lam_lat) if (lam_lat > 0).all() else None,
        "n_eigvec_off_axis": nonaxis, "max_field_residual_N": float(max(resid)),
        "max_jacobian_asymmetry_N_per_m": float(max(asym))}
    from scipy.stats import spearmanr
    out["lone_hessian"]["spearman_lateral_vs_margin"] = float(spearmanr([x["margin"] for x in lone], lam_lat)[0])
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "negative_margin"}, indent=1))
    for c in out["negative_margin"]["cases"]:
        print(c)


if __name__ == "__main__":
    main()
