"""T5 diagnostic (no re-fit): the full-condition E4 snapshot E1b_seed170 (barrier 0.128 J, no escape in 60 restarts
at beta 1.5-3.5, 300 / 900 s).

Part "string": the BAR string method (experiments/BAR/bar.py: Field, relax, string_method, unchanged; 31 and 62 images,
1500 iterations, climbing refinement) for the all-mobile condition, re-run with the path kept. Reported along the
path: U - U_min per image, every agent's position and displacement from the relaxed minimum, the blocker's x, every
pair gap d_ij - (r_i + r_j) and wall clearance; at the snapshot, the relaxed minimum and the climbed saddle: the code's
C1 force at v = 0 against -grad U (bar.code_force_check, also evaluated at the saddle), the Hessian eigenvalues
(central differences of grad U) and the harmonic transition-state escape time (Vineyard, masses of the state, times
the Kramers-Grote-Hynes / Langer factor lambda+/omega_b with friction 1/tau of the mode-weighted agents).
Part "second": the all-mobile string passes an intermediate minimum (U far below the snapshot) before the
blocker leaves. The deepest image before the path rises again is relaxed (bar.relax) to the intermediate rest state
M2; M2 is checked (gradient norm, Hessian eigenvalues, code force vs -grad U); a string (31 and 62 images, 1500
iterations, climbing) runs from M2 to the exit state (blocker at x = 10.35 m, others relaxed), giving the barrier of
the exit from M2. The same is repeated from that string's own intermediate minima until a path without an interior
rise above 0.05 J remains (at most 3 rounds).
Part "runs": the E4 escape restart (runlib.escape, condition full, C1 + per-step noise, CF, dt 0.01 s), extended:
  beta_ref in {0.25, 0.5, 1.0} at 300 s and beta_ref 1.5 at 3600 s, 20 restarts each (sigma from experiments/lib/teff.py
  for k_B T = dU_full / beta_ref and the blocker's tau, as E4), noise seeds 600000 + 1000 level + rep (disjoint from
  every seed in experiments/SEEDS.md and from the revision ranges), and beta_ref 5.0 at 300 s (10 restarts);
  frozen and alone conditions are not rerun (E4: 60/60 and 53/60 escape there).
  Each run also records the blocker's largest x, every agent's largest displacement from the snapshot and the
  per-agent velocity variance (the realised k_B T).
Output: data/revision4/T5/t5_string.json, data/revision4/T5/t5_runs.jsonl.
Output (second): data/revision4/T5/t5_second.json.
Usage: T5_seed170.py string | second | runs [--workers W]
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import CF, DATA, np, run_jobs  # noqa: E402
import bar  # noqa: E402
from teff import kT_eff, sigma_for  # noqa: E402
from w2lib import restore  # noqa: E402

TAG, BLOCKER = "E1b_seed170", 82
SNAP = os.path.join(DATA, "E1", "library", TAG + ".pkl")
OUTD = rev4lib.data_dir("T5")


def hessian(field, X, h=1e-5):
    n = len(X)
    H = np.zeros((n, n))
    for k in range(n):
        e = np.zeros(n); e[k] = h
        H[:, k] = (field.grad(X + e, h=1e-6) - field.grad(X - e, h=1e-6)) / (2 * h)
    return 0.5 * (H + H.T)


def gaps(field, X, names):
    P = field.all_pos(X)
    out = {}
    for a in range(len(P)):
        for b in range(a + 1, len(P)):
            out[f"{names[a]}-{names[b]}"] = float(np.linalg.norm(P[a] - P[b]) - field.r[a] - field.r[b])
    from sim.core.world import agents_to_walls
    d, _ = agents_to_walls(P, field.world.walls)
    d = d - np.array([w.radius for w in field.world.walls])[None]
    wall = {f"{names[a]}": float(d[a].min() - field.r[a]) for a in range(len(P))}
    return out, wall


def string_part():
    t0 = time.perf_counter()
    snap = pickle.load(open(SNAP, "rb"))
    st = snap["state"]
    resid = [int(i) for i in st.active_indices]
    others = [i for i in resid if i != BLOCKER]
    ids = [BLOCKER] + others
    fm = bar.Field(snap, ids, [])
    X0 = st.positions[ids].ravel()
    out = {"tag": TAG, "blocker": BLOCKER, "agents": ids, "radii": fm.r.tolist(), "tau": fm.tau.tolist(),
           "v0": fm.v0.tolist(), "mass": fm.m.tolist(), "rho": fm.rho.tolist(), "drive_c_N": fm.c.tolist(),
           "snapshot_speeds": [float(np.linalg.norm(st.velocities[i])) for i in ids],
           "force_check_snapshot_N": bar.code_force_check(snap, ids, fm)}
    XA = bar.relax(fm, X0)
    out["relaxed_minus_snapshot_m"] = np.linalg.norm((XA - X0).reshape(-1, 2), axis=1).tolist()
    out["grad_norm_min_N"] = float(np.linalg.norm(fm.grad(XA)))
    XBf = XA.copy(); XBf[0:2] = [10.35, 5.0]
    XBf = bar.relax(fm, XBf, fix_idx=(0, 1))
    out["end_state"] = XBf.reshape(-1, 2).tolist()
    out["U_end_minus_min_J"] = fm.U(XBf) - fm.U(XA)
    res = {}
    for n_img in (31, 62):
        path, E, Esad, Xs, gs = bar.string_method(fm, XA, XBf, n_img=n_img, iters=1500)
        U0 = fm.U(XA)
        disp = [np.linalg.norm((p - XA).reshape(-1, 2), axis=1).tolist() for p in path]
        g_path = [gaps(fm, p, ids)[0] for p in path]
        res[str(n_img)] = {"U_minus_min_J": (E - U0).tolist(), "dU_string": float(E.max() - U0),
                           "dU_climb": float(Esad - U0), "k_max": int(np.argmax(E)),
                           "positions": [p.reshape(-1, 2).tolist() for p in path], "displacement_m": disp,
                           "pair_gaps_m": g_path, "saddle": Xs.reshape(-1, 2).tolist(), "grad_norm_saddle": gs,
                           "saddle_disp_m": np.linalg.norm((Xs - XA).reshape(-1, 2), axis=1).tolist()}
        if n_img == 62:
            Xsad = Xs
    out["string"] = res
    pg, wg = gaps(fm, XA, ids)
    out["min_pair_gaps_m"], out["min_wall_clear_m"] = pg, wg
    pg, wg = gaps(fm, Xsad, ids)
    out["saddle_pair_gaps_m"], out["saddle_wall_clear_m"] = pg, wg
    # code force against -grad U at the saddle
    s2 = {"state": __import__("copy").deepcopy(st), "params": snap["params"], "width": snap["width"]}
    s2["state"].positions[ids] = Xsad.reshape(-1, 2)
    out["force_check_saddle_N"] = bar.code_force_check(s2, ids, fm)
    # Hessians and harmonic TST
    Hm, Hs = hessian(fm, XA), hessian(fm, Xsad)
    M = np.repeat(fm.m, 2)
    Wm = np.linalg.eigvalsh(Hm / np.sqrt(np.outer(M, M)))
    Ws, Vs = np.linalg.eigh(Hs / np.sqrt(np.outer(M, M)))
    out["hess_min_eig_per_kg"] = Wm.tolist()
    out["hess_saddle_eig_per_kg"] = Ws.tolist()
    out["hess_min_eig_N_per_m"] = np.linalg.eigvalsh(Hm).tolist()
    out["hess_saddle_eig_N_per_m"] = np.linalg.eigvalsh(Hs).tolist()
    neg = Ws < 0
    out["n_negative_saddle"] = int(neg.sum())
    if Wm.min() > 0 and neg.sum() == 1:
        wb = float(np.sqrt(-Ws[0]))
        nu_tst = float(np.sqrt(np.prod(Wm)) / np.sqrt(np.prod(Ws[1:])) / (2 * np.pi))
        u = Vs[:, 0] ** 2
        w_agent = u.reshape(-1, 2).sum(1)
        gam = float(np.sum(w_agent / fm.tau))
        lam = -gam / 2 + np.sqrt(gam * gam / 4 + wb * wb)
        out["unstable_mode_weights"] = w_agent.tolist()
        out["omega_b"] = wb
        out["gamma_mode"] = gam
        out["nu_tst"] = nu_tst
        out["kgh_factor"] = float(lam / wb)
        dU = res["62"]["dU_climb"]
        tau_b = float(st.taus[BLOCKER])
        pred = {}
        for b in (0.25, 0.5, 1.0, 1.5, 2.5, 3.5, 5.0):
            pred[str(b)] = {"rate_per_s": nu_tst * lam / wb * np.exp(-b), "mean_time_s": 1 / (nu_tst * lam / wb * np.exp(-b)),
                            "sigma": sigma_for(dU / b, 0.01, tau_b)}
        out["harmonic_prediction"] = pred
    # frozen-condition saddle for comparison (blocker mobile, others fixed)
    ff = bar.Field(snap, [BLOCKER], others)
    XAf = bar.relax(ff, st.positions[BLOCKER].copy())
    path, E, Esad, Xs_f, gs = bar.string_method(ff, XAf, np.array([10.35, 5.0]), iters=1500)
    out["frozen"] = {"dU_climb": float(Esad - ff.U(XAf)), "saddle": Xs_f.tolist()}
    out["wall_s"] = time.perf_counter() - t0
    json.dump(out, open(os.path.join(OUTD, "t5_string.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("string",)}, default=float, indent=0)[:4000])


def interior_min(E, tol=0.05):
    """Index of the deepest image before the first rise of more than tol J after it (None if the path has none)."""
    best = 0
    for k in range(1, len(E)):
        if E[k] < E[best]:
            best = k
        elif E[k] - E[best] > tol and best > 0:
            return best
    return None


def second_part():
    t0 = time.perf_counter()
    snap = pickle.load(open(SNAP, "rb"))
    st = snap["state"]
    resid = [int(i) for i in st.active_indices]
    others = [i for i in resid if i != BLOCKER]
    ids = [BLOCKER] + others
    fm = bar.Field(snap, ids, [])
    XA = bar.relax(fm, st.positions[ids].ravel())
    U0 = fm.U(XA)
    XB = XA.copy(); XB[0:2] = [10.35, 5.0]
    XB = bar.relax(fm, XB, fix_idx=(0, 1))
    first = json.load(open(os.path.join(OUTD, "t5_string.json")))["string"]["62"]
    E = np.array(first["U_minus_min_J"])
    path = np.array([np.ravel(p) for p in first["positions"]])
    rounds = []
    for rnd in range(3):
        k = interior_min(E)
        if k is None:
            break
        M2 = bar.relax(fm, path[k], steps=20000)
        g = float(np.linalg.norm(fm.grad(M2)))
        Hm = hessian(fm, M2)
        s2 = {"state": __import__("copy").deepcopy(st), "params": snap["params"], "width": snap["width"]}
        s2["state"].positions[ids] = M2.reshape(-1, 2)
        fc = bar.code_force_check(s2, ids, fm)
        res = {"from_image": k, "U_image_minus_U0": float(E[k]), "U_M2_minus_U0": fm.U(M2) - U0, "grad_norm_M2": g,
               "hess_M2_eig_N_per_m": np.linalg.eigvalsh(Hm).tolist(), "force_check_M2_N": fc,
               "M2": M2.reshape(-1, 2).tolist(),
               "M2_disp_from_min_m": np.linalg.norm((M2 - XA).reshape(-1, 2), axis=1).tolist(),
               "M2_pair_gaps_m": gaps(fm, M2, ids)[0], "M2_wall_clear_m": gaps(fm, M2, ids)[1]}
        for n_img in (31, 62):
            P, E2, Es, Xs, gs = bar.string_method(fm, M2, XB, n_img=n_img, iters=1500)
            UM = fm.U(M2)
            res[str(n_img)] = {"dU_string": float(E2.max() - UM), "dU_climb": float(Es - UM), "k_max": int(np.argmax(E2)),
                               "U_minus_M2_J": (E2 - UM).tolist(), "blocker_x": P[:, 0].tolist(),
                               "saddle": Xs.reshape(-1, 2).tolist(), "grad_norm_saddle": gs,
                               "saddle_disp_from_M2_m": np.linalg.norm((Xs - M2).reshape(-1, 2), axis=1).tolist(),
                               "saddle_pair_gaps_m": gaps(fm, Xs, ids)[0]}
            if n_img == 62:
                Hs = hessian(fm, Xs)
                res["62"]["hess_saddle_eig_N_per_m"] = np.linalg.eigvalsh(Hs).tolist()
                E, path = E2 - UM + (UM - U0), P
        res["rel_change_doubling"] = abs(res["62"]["dU_climb"] - res["31"]["dU_climb"]) / max(abs(res["62"]["dU_climb"]), 1e-12)
        rounds.append(res)
        print("round", rnd, {k2: v for k2, v in res.items() if k2 not in ("31", "62", "hess_M2_eig_N_per_m", "M2")},
              "dU31", res["31"]["dU_climb"], "dU62", res["62"]["dU_climb"], flush=True)
    out = {"tag": TAG, "U0_note": "U relative to the relaxed snapshot minimum", "rounds": rounds,
           "wall_s": time.perf_counter() - t0}
    json.dump(out, open(os.path.join(OUTD, "t5_second.json"), "w"), indent=1, default=float)


def escape_diag(job):
    """runlib.escape with the extra record (blocker max x, agents' max displacement, velocity variance)."""
    snap = pickle.load(open(SNAP, "rb"))
    b = BLOCKER
    sim = restore(snap, "C1", flags=dict(CF), noise=job["sigma"], noise_seed=job["noise_seed"], dt=0.01)
    st = sim.state
    ids = [int(i) for i in st.active_indices]
    p0 = st.positions[ids].copy()
    t0, w0 = sim.time, time.perf_counter()
    xmax, dmax = float(st.positions[b, 0]), np.zeros(len(ids))
    s1, s2, cnt = np.zeros((len(ids), 2)), np.zeros((len(ids), 2)), 0
    esc, first_other = None, None
    for k in range(int(round(job["t_cens"] / 0.01))):
        prev = st.active.copy()
        sim.step()
        st = sim.state
        gone = [i for i in np.where(prev & ~st.active)[0] if i != b]
        if gone and first_other is None:
            first_other = sim.time - t0
        x = st.positions[b, 0]
        if x >= 10.0 or not st.active[b]:
            esc = sim.time - t0
            break
        xmax = max(xmax, float(x))
        act = st.active[ids]
        dmax = np.maximum(dmax, np.where(act, np.linalg.norm(st.positions[ids] - p0, axis=1), 0))
        if sim.time - t0 > 2.0:
            v = st.velocities[ids]
            s1 += v; s2 += v * v; cnt += 1
    var = (s2 / max(cnt, 1) - (s1 / max(cnt, 1)) ** 2).mean(1)
    m = st.masses[ids]
    out = {k: v for k, v in job.items()}
    out.update({"escape_t": esc, "censored": esc is None, "t_run": sim.time - t0, "blocker_xmax": xmax,
                "x0": float(p0[ids.index(b), 0]), "agents": ids, "max_disp_m": dmax.tolist(),
                "kT_realised_J": (m * var).tolist(), "first_other_exit_t": first_other,
                "wall_s": time.perf_counter() - w0})
    return out


def run_jobs_list():
    snap = pickle.load(open(SNAP, "rb"))
    tau_b = float(snap["state"].taus[BLOCKER])
    dU = json.load(open(os.path.join(DATA, "BAR", "barriers.json")))
    dU = next(r for r in dU["barriers"] if r["job_id"] == TAG)["all_mobile"]["dU_climb"]
    plan = [(0.25, 300.0, 20), (0.5, 300.0, 20), (1.0, 300.0, 20), (1.5, 3600.0, 20), (5.0, 300.0, 10)]
    J = []
    for lv, (b, tc, n) in enumerate(plan):
        s = sigma_for(dU / b, 0.01, tau_b)
        for rep in range(n):
            J.append({"job_id": f"{TAG}|b{b}|T{int(tc)}|{rep}", "beta_ref": b, "sigma": s, "t_cens": tc, "rep": rep,
                      "dU_full": dU, "tau_b": tau_b, "kT_target": dU / b, "kT_eff": kT_eff(s, 0.01, tau_b),
                      "noise_seed": 600000 + 1000 * lv + rep})
    return J


if __name__ == "__main__":
    if sys.argv[1] == "string":
        string_part()
    elif sys.argv[1] == "second":
        second_part()
    else:
        print("wall", run_jobs(run_jobs_list(), escape_diag, os.path.join(OUTD, "t5_runs.jsonl"),
                               workers=rev4lib.workers(sys.argv), log_every=10))
