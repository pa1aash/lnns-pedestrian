"""B5 static: the E7b pair standoff with rounded jamb ends, its loss under a lateral bias, and the work
across the biased rest field.

Inputs: the 46 E7b pair snapshots (experiments/E7b/e7b_pairs.py; sharp door, C1, CF union {B_w: 0.04});
data/N6/n6_static.jsonl (sharp-edge folds, for the 'barrier' phase). Force: experiments/revision/B5_lib.PairRest
(the code's C1 rest-state force on the two members, v = 0, density frozen at the snapshot, the snapshot params,
other agents inactive). Rounded jamb ends: BottleneckScenario edge = "rounded", r_c = edge_radius (capsule jambs,
room-side face x = 10, clear width w unchanged); the wall law and B_w = 0.04 m are unchanged on every wall.

Phases (python experiments/revision/B5_static.py <phase> [qargs options]):
  reequil   per snapshot and r_c in RC_SCAN (primary r_c = 0.1 m): relax the two members from the sharp-edge
            positions at b = 0 (B5_lib.relax = pairlib.relax: dx/dt = (tau/m) F, Euler 0.01 s, 120 s; freed at
            x > 10.3 m, held at max |F| < 0.05 N), Newton polish (tol 1e-9 N), then B5_lib.rest_checks:
            Hessian -sym(J) positive definite, contact-free, both x < 10, opposite sides, front of jambs.
            Out: data/revision/B5/reequil.jsonl (job_id "rc<r_c>|<tag>").
  cont      for r_c in RC_CONT and each (snapshot, sign) whose rounded rest state is a strict minimum: the
            continuation of runs3/N6.py (pseudo-arclength in b, fold refined on F = 0, J v = 0) and, where the
            corrector fails, natural-parameter continuation in b with step halving down to 1e-6 (the loss
            point b_last). At b = b_f (1 - delta), delta in DELTAS: minimum and saddle by Newton, mu1 (softest
            eigenvalue of -J at the minimum), minimum-saddle distance, Jacobian jump, geometry, and the
            barrier quantities of `scan`. Out: data/revision/B5/cont.jsonl (job_id "rc<r_c>|<tag>|<sign>").
  bisect    for the same cases: bisection of the relaxation threshold b* as experiments/E7b/fold_threshold.py
            (grid 0, 0.01, 0.02, 0.03, 0.05, 0.1, then bisection to 1e-4), relaxing from the rounded minimum.
            Out: data/revision/B5/bisect.jsonl.
  barrier   the sharp-edge folds of data/N6/n6_static.jsonl (66 (snapshot, sign) cases): minimum and saddle
            re-solved at the six delta from the stored fold point (as N6), then `scan`.
            Out: data/revision/B5/barrier_sharp.jsonl.
scan quantities (bias b != 0; the field is not a gradient):
  curl      per member, curl_i = dF_yi/dx_i - dF_xi/dy_i at the minimum (from J), against the drive-only
            prediction -c_i b / (sqrt(1 + b^2) rho_i), c_i = m v0 f_W / tau, rho_i = |x_i - g| (the tilt
            c b e_perp / sqrt(1 + b^2) with e_perp rotating with the goal direction is an azimuthal field
            about g, curl -1/rho); cross-member antisymmetry max |J_ij - J_ji| over member blocks.
  W_line    W = -int F . dX on the straight segment minimum -> saddle (16-point Gauss-Legendre; as N6).
  W_flow    the same integral along the saddle's unstable manifold, the heteroclinic flow line of the
            overdamped dynamics dX/dt = M F (M = diag(tau/m)) from the saddle to the minimum (the path on which
            the force is tangent to the path, the fixed point of the string method on a non-gradient field):
            W_flow = int F . M F dt, integrated by RK45 from X_s + 1e-4 d u (u the unstable eigenvector of M J,
            d the minimum-saddle distance) until |X - X_m| < 1e-3 d; endpoint recorded.
  W_rel     (W_line - W_flow) / W_flow: the path dependence of the work.
"""
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402
import B5_lib as L  # noqa: E402
import N6  # noqa: E402
import numpy as np  # noqa: E402
import pairlib  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

D = revlib.data_dir("B5")
RC_MAIN = 0.1
RC_SCAN = (0.1, 0.05, 0.02, 0.01, 0.003, 0.001)
RC_CONT = (0.02,)
DELTAS = N6.DELTAS
GRID = (0.0, 0.01, 0.02, 0.03, 0.05, 0.1)
TOL = 1e-4
G = np.array([11.0, 5.0])


def load(snap_path):
    return pickle.load(open(snap_path, "rb"))


# ------------------------------------------------------------------ reequil
def reequil_run(job):
    w0 = time.perf_counter()
    snap = load(job["snap"])
    f = L.PairRest(snap, edge="rounded", edge_radius=job["rc"])
    X, r, ok = L.equilibrate(f, f.X_snap)
    row = {k: v for k, v in job.items() if k != "snap"}
    mv = np.linalg.norm((X - f.X_snap).reshape(-1, 2), axis=1)
    row.update({"members": f.ids, "relax_freed": r["pred_freed"], "relax_t": r["t"],
                "first_side": r.get("first_side"), "newton_ok": ok, "X": X.tolist(),
                "move": mv.tolist(), "move_max": float(mv.max())})
    if ok:
        c = L.rest_checks(f, X)
        c["kept"] = bool(c["strict_min"] and c["contact_free"] and c["before_door"] and c["opposite"])
        row.update(c)
    else:
        row["kept"] = False
    row["wall_s"] = time.perf_counter() - w0
    return row


def reequil_jobs():
    return [{"job_id": f"rc{rc:g}|{p['tag']}", "tag": p["tag"], "snap": p["snap"], "rc": rc}
            for rc in RC_SCAN for p in pairs()]


# ------------------------------------------------------------------ scan (barrier quantities)
def curl(f, J, X, b):
    P = X.reshape(-1, 2)
    st = f.st
    fw = np.array([pairlib.weidmann_factor(x) for x in f.dens])
    c = st.masses * st.desired_speeds * fw / st.taus
    rho = np.linalg.norm(P - G, axis=1)
    meas = [float(J[2 * i + 1, 2 * i] - J[2 * i, 2 * i + 1]) for i in range(2)]
    pred = [float(-c[i] * f.sign * b / np.sqrt(1 + b * b) / rho[i]) for i in range(2)]
    cross = float(np.abs(J[0:2, 2:4] - J[2:4, 0:2].T).max())
    return {"curl": meas, "curl_pred": pred, "cross_asym": cross, "sym_scale": float(np.abs(J).max())}


def w_flow(f, Xm, Xs, b):
    M = np.repeat(f.gain.ravel(), 2)
    Js = f.J(Xs, b)
    ev, V = np.linalg.eig(M[:, None] * Js)
    i = int(np.argmax(ev.real))
    u = np.real(V[:, i]); u /= np.linalg.norm(u)
    d = float(np.linalg.norm(Xm - Xs))
    if u @ (Xm - Xs) < 0:
        u = -u

    def rhs(t, Y):
        F = f.F(Y[:-1], b)
        return np.append(M * F, F @ (M * F))

    def hit(t, Y):
        return np.linalg.norm(Y[:-1] - Xm) - 1e-3 * d
    hit.terminal = True
    Y0 = np.append(Xs + 1e-4 * d * u, 0.0)
    T = 50.0 / max(float(ev.real[i]), 1e-6) + 200.0
    s = solve_ivp(rhs, (0, T), Y0, events=hit, rtol=1e-8, atol=1e-12, max_step=T / 50)
    Xe = s.y[:-1, -1]
    return {"W_flow": float(s.y[-1, -1]), "flow_end_err": float(np.linalg.norm(Xe - Xm) / d),
            "flow_reached": bool(s.status == 1), "flow_t": float(s.t[-1]), "unstable_rate": float(ev.real[i])}


def scan(f, Xf, v, bf, c, deltas=DELTAS, flow=True):
    rows = []
    for dl in deltas:
        b = bf * (1 - dl)
        Xm, okm = N6.newton_X(f, Xf - c * np.sqrt(dl * bf) * v, b)
        Xs, oks = N6.newton_X(f, Xf + c * np.sqrt(dl * bf) * v, b)
        r = {"delta": dl, "b": b, "converged": bool(okm and oks)}
        if okm and oks:
            Jm, Js = f.J(Xm, b), f.J(Xs, b)
            evm = np.linalg.eigvals(-Jm)
            evs = np.linalg.eigvals(-Js)
            dist = float(np.linalg.norm(Xs - Xm))
            r.update({"mu1_min": float(evm.real.min()), "mu1_saddle": float(evs.real.min()),
                      "eig_min": sorted(evm.real.tolist()), "eig_saddle": sorted(evs.real.tolist()),
                      "dist": dist, "distinct": dist > 1e-6,
                      "jac_jump": float(np.linalg.norm(Jm - Js) / max(np.linalg.norm(Jm), 1e-12)),
                      "W_line": N6.work(f, Xm, Xs, b), **curl(f, Jm, Xm, b)})
            if flow and dist > 1e-6:
                r.update(w_flow(f, Xm, Xs, b))
                r["W_rel"] = (r["W_line"] - r["W_flow"]) / r["W_flow"] if r["W_flow"] else None
            if dl == deltas[-1]:
                gm, gs = L.geometry(f, Xm), L.geometry(f, Xs)
                r.update({"geom_min": gm, "geom_saddle": gs, "end_min": L.at_end(gm), "end_saddle": L.at_end(gs)})
        rows.append(r)
    return rows


def fold_and_scan(f, X0):
    """N6.static_run's fold location and delta scan on field f from the b = 0 minimum X0."""
    pts, i, status = N6.continue_branch(f, X0)
    out = {"branch_points": len(pts), "status": status}
    if i is None:
        return out
    n = len(X0)
    P = np.array(pts)
    j = int(np.argmax(P[:, n]))
    Xf, bf = P[j, :n], P[j, n] / N6.BSCALE
    ev, V = np.linalg.eig(f.J(Xf, bf))
    v = np.real(V[:, np.argmin(np.abs(ev))])
    Xf, v, bf, res = N6.refine_fold(f, Xf, bf, v)
    lo = P[max(j - 3, 0)]
    cX = (lo[:n] - Xf) @ v
    if cX > 0:
        v, cX = -v, -cX
    c = abs(cX) / np.sqrt(max(bf - lo[n] / N6.BSCALE, 1e-15))
    gf = L.geometry(f, Xf)
    out.update({"b_f": bf, "fold_residual": res, "X_f": Xf.tolist(), "fold_vector": v.tolist(), "sqrt_coeff": c,
                "geom_fold": gf, "end_at_fold": L.at_end(gf), "scan": scan(f, Xf, v, bf, c)})
    return out


def natural(f, X0, b_max=0.2, db0=2e-3, db_min=1e-6):
    """Natural-parameter continuation of the minimum in b with step halving; last b with a converged
    minimum whose mu1 > 0."""
    X, b, db = X0.copy(), 0.0, db0
    mu0, _ = N6.soft(f, X0, 0.0)
    mu = mu0
    while db >= db_min and b < b_max:
        Xn, ok = N6.newton_X(f, X, b + db)
        if ok:
            mun, _ = N6.soft(f, Xn, b + db)
            if mun > 0 and np.linalg.norm(Xn - X) < 0.05:
                X, b, mu = Xn, b + db, mun
                continue
        db *= 0.5
    g = L.geometry(f, X)
    return {"b_last": b, "mu1_b0": mu0, "mu1_last": mu, "geom_last": g, "end_last": L.at_end(g), "X_last": X.tolist()}


def cont_run(job):
    w0 = time.perf_counter()
    f = L.PairRest(load(job["snap"]), sign=job["sign"], edge="rounded", edge_radius=job["rc"])
    X0 = np.array(job["X0"])
    row = {k: v for k, v in job.items() if k not in ("snap", "X0")}
    row.update(fold_and_scan(f, X0))
    row["natural"] = natural(f, X0)
    row.update({"n_force_evals": f.n_eval, "wall_s": time.perf_counter() - w0})
    return row


def kept_rest(rc):
    p = os.path.join(D, "reequil.jsonl")
    R = revlib.load_runs(p) if os.path.exists(p) else []
    return {r["tag"]: r for r in R if abs(r["rc"] - rc) < 1e-12 and r["kept"]}


def cont_jobs():
    J = []
    for rc in RC_CONT:
        K = kept_rest(rc)
        for p in pairs():
            if p["tag"] in K:
                for s in (1, -1):
                    J.append({"job_id": f"rc{rc:g}|{p['tag']}|{s:+d}", "tag": p["tag"], "snap": p["snap"],
                              "rc": rc, "sign": s, "X0": K[p["tag"]]["X"]})
    return J


# ------------------------------------------------------------------ bisect
def bisect_run(job):
    w0 = time.perf_counter()
    f = L.PairRest(load(job["snap"]), sign=job["sign"], edge="rounded", edge_radius=job["rc"])
    X0 = np.array(job["X0"])
    calls = []

    def freed(b):
        r = L.relax(f, X0, b)
        calls.append({"b": job["sign"] * b, "pred": r["pred_freed"], "t": r["t"], "first_side": r.get("first_side")})
        return bool(r["pred_freed"]), r
    grid, lo, hi, r_hi = {}, None, None, None
    for b in GRID:
        fr, r = freed(b)
        grid[f"{b:g}"] = fr
        if fr:
            hi, r_hi = b, r
            break
        lo = b
    if hi is not None and lo is not None:
        while hi - lo > TOL:
            mid = 0.5 * (lo + hi)
            fr, r = freed(mid)
            if fr:
                hi, r_hi = mid, r
            else:
                lo = mid
    row = {k: v for k, v in job.items() if k not in ("snap", "X0")}
    row.update({"grid_freed": grid, "b_lo": lo, "b_hi": hi,
                "b_star": None if (hi is None or lo is None) else 0.5 * (lo + hi),
                "first_side_at_hi": None if r_hi is None else r_hi.get("first_side"),
                "undecided_calls": sum(c["pred"] is None for c in calls), "calls": calls,
                "wall_s": time.perf_counter() - w0})
    return row


# ------------------------------------------------------------------ barrier (sharp edges, N6 folds)
def barrier_run(job):
    w0 = time.perf_counter()
    f = L.PairRest(load(job["snap"]), sign=job["sign"], edge="sharp")
    row = {k: v for k, v in job.items() if k not in ("snap", "X_f", "fold_vector")}
    row["scan"] = scan(f, np.array(job["X_f"]), np.array(job["fold_vector"]), job["b_f"], job["sqrt_coeff"])
    row["wall_s"] = time.perf_counter() - w0
    return row


def barrier_jobs():
    S = revlib.load_runs(os.path.join(revlib.DATA, "N6", "n6_static.jsonl"))
    snap = {p["tag"]: p["snap"] for p in pairs()}
    return [{"job_id": r["job_id"], "tag": r["tag"], "sign": r["sign"], "snap": snap[r["tag"]], "b_f": r["b_f"],
             "X_f": r["X_f"], "fold_vector": r["fold_vector"], "sqrt_coeff": r["sqrt_coeff"]}
            for r in S if r.get("b_f") is not None]


PHASES = {"reequil": (reequil_jobs, reequil_run, "reequil.jsonl"),
          "cont": (cont_jobs, cont_run, "cont.jsonl"),
          "bisect": (cont_jobs, bisect_run, "bisect.jsonl"),
          "barrier": (barrier_jobs, barrier_run, "barrier_sharp.jsonl")}


def main(argv=None):
    a = qargs.parse(argv)
    jobs, fn, name = PHASES[a.rest[0]]
    return revlib.run_jobs(qargs.select(jobs(), a), fn, a.out or os.path.join(D, name), workers=a.workers,
                           log_every=4)


if __name__ == "__main__":
    print("wall", main())
