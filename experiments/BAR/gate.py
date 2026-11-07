"""Barrier validity gate (plan change C15a): re-checks every BAR result before E3 / E4 use it.

For each E2 snapshot and condition (alone, frozen, full = all_mobile) the minimum-energy path is
recomputed with the BAR field, end points and step cap (experiments/BAR/bar.py), and the barrier is
accepted only if:
  (i)   the string has converged: F_perp_max, the largest norm over the uphill interior images (trapped
        minimum to one image past the top) of the gradient component perpendicular to the path (all
        mobile coordinates; upwind tangent), is below F_TOL = 5 N (about 2.5% of the blocker's drive);
        the sum over those images is recorded. Resolution rule (v2): the string at 62 images must pass
        this test and the climbing-image barrier must change by less than 1% from 31 to 62 images; if
        not, the string is computed once more at 124 images and the same rule is applied to 62 -> 124;
        otherwise the barrier fails. The finer string of the accepted pair gives the barrier. Its
        climbing image must reach |grad U| < 1e-2 N and must be the maximum of U over the whole path
        (no higher hump on the downhill part);
  (ii)  the final image is an exit state (blocker centre past the door plane, x >= 10) and the saddle
        has no agent-agent overlap deeper than 2 cm;
  (iii) alone only (v2): the barrier agrees to 2% with the minimum-energy-path barrier of the single
        agent's rest-state potential (same wall law and drive, density 0) on a 2-D grid, computed as
        the lowest level at which the trapped minimum connects to the exit column x >= 10.35
        (8-connected sublevel sets, bisection). The grid is evaluated at 5 mm and 2.5 mm spacing; the
        halving must change the grid barrier by less than 1%, and the 2.5 mm value is compared. The
        1-D on-axis integral (equal to the grid value for on-axis blockers) stays in the log.
Convergence schedule: BAR's 1500 string iterations at alpha = 4e-5, then, while F_perp_max >= F_TOL,
up to two blocks of 500 iterations at alpha = 1e-5. The climbing image is
refined as in BAR (|grad U| < 1e-2 N), with alpha / 4 if that does not converge.
Frozen barrier more than 1.5x the alone barrier: recomputed from a second initial path (blocker from its
minimum straight onto the door axis y = 5, then along the axis to x = 10.35), relaxed first with the
pinned neighbours displaced off that path (initial guess only) and then in the true field; the lower of
the accepted values is kept. For frozen and full the saddle's squeeze geometry is recorded (the other
residual agent with the smallest surface gap to the blocker, its position, the gap, and the blocker's
clearance to the nearest wall).
A failed (snapshot, condition) gets no noise amplitude: E3 / E4 skip it (selection.py, e4_escape.py).
One-agent snapshots: the three conditions are the same field (density 0 either way), computed once.
Re-use (v2): string results already computed by the first gate pass (data/BAR/gate_v1.jsonl, same
fields, end points and schedule) are taken over; only the 124-image strings, the grid check and the
second frozen path where it was not stored are computed.
Output: data/BAR/gate.jsonl (resumable, one line per snapshot), data/BAR/barriers_gated.json.
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
sys.path.insert(0, HERE)
from e1lib import DATA, ROOT, load_runs, run_jobs  # noqa: E402
import numpy as np  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402
import bar  # noqa: E402

OUTD = os.path.join(DATA, "BAR")
OUT = os.path.join(OUTD, "gate.jsonl")
PREV = os.path.join(OUTD, "gate_v1.jsonl")
GATED = os.path.join(OUTD, "barriers_gated.json")
CONDS = ("alone", "frozen", "full")
F_TOL = 5.0            # N, on F_perp_max: about 2.5% of the blocker's drive m v0 / tau (~200 N)
DOUBLE_TOL = 0.01      # relative change of the barrier, 31 -> 62 images
OVERLAP_MAX = 0.02     # m, deepest agent-agent overlap at the saddle
GRID_TOL = 0.02        # relative, alone barrier vs 2-D grid minimum-energy path
GRID_RES_TOL = 0.01    # relative change of the grid barrier when the spacing is halved
GRID_H = (0.005, 0.0025)
GRID_BOX = (8.9, 10.4, 3.8, 6.2)
GUARD_TOL = 1e-4       # J: the climbing image may not lie below the highest image
RESOLUTIONS = (31, 62, 124)
FROZEN_RATIO = 1.5
SCHEDULE = [(1500, 4e-5), (500, 1e-5), (500, 1e-5)]
MAX_ITERS = sum(n for n, _ in SCHEDULE)
X_EXIT = 10.35


def string_iter(field, path, iters, alpha):
    n = len(path)
    for _ in range(iters):
        for k in range(1, n - 1):
            path[k] -= bar.capped(alpha * field.grad(path[k]))
        seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
        L = np.concatenate([[0], np.cumsum(seg)])
        t = np.linspace(0, L[-1], n)
        path = np.column_stack([np.interp(t, L, path[:, d]) for d in range(path.shape[1])])
    return path


def tangent(path, E, k):
    """Upwind (energy-weighted) tangent at image k (Henkelman and Jonsson 2000). A central difference
    misreads the large along-path gradient on the downhill side (|grad U| up to ~650 N) as
    perpendicular force."""
    tp, tm = path[k + 1] - path[k], path[k] - path[k - 1]
    if E[k + 1] > E[k] > E[k - 1]:
        t = tp
    elif E[k + 1] < E[k] < E[k - 1]:
        t = tm
    else:
        dmax = max(abs(E[k + 1] - E[k]), abs(E[k - 1] - E[k]))
        dmin = min(abs(E[k + 1] - E[k]), abs(E[k - 1] - E[k]))
        t = tp * dmax + tm * dmin if E[k + 1] > E[k - 1] else tp * dmin + tm * dmax
    return t / np.linalg.norm(t)


def f_perp(field, path):
    """Perpendicular force on the uphill segment: interior images from the trapped minimum up to one
    image past the highest image. Past the saddle the path runs downhill to an end point that is not a
    minimum (the goal attraction continues beyond the door plane), so the string there is not a
    converged object and does not enter the barrier."""
    E = np.array([field.U(p) for p in path])
    top = int(np.argmax(E))
    out = []
    for k in range(1, min(top + 2, len(path) - 1)):
        t = tangent(path, E, k)
        g = field.grad(path[k])
        out.append(float(np.linalg.norm(g - np.dot(g, t) * t)))
    return np.array(out) if out else np.zeros(1)


def converge(field, path, schedule=SCHEDULE):
    it = 0
    fp = None
    for n, alpha in schedule:
        path = string_iter(field, path, n, alpha)
        it += n
        fp = f_perp(field, path)
        if fp.max() < F_TOL:
            break
    return path, it, fp


def climb(field, path, alpha=4e-5):
    E = np.array([field.U(p) for p in path])
    k = int(np.argmax(E))
    n = len(path)
    tan = path[min(k + 1, n - 1)] - path[max(k - 1, 0)]
    tan = tan / np.linalg.norm(tan)
    for a in (alpha, alpha / 4):
        X = path[k].copy()
        for _ in range(3000):
            g = field.grad(X)
            X -= bar.capped(a * (g - 2 * np.dot(g, tan) * tan))
            if np.linalg.norm(g) < 1e-2:
                break
        gn = float(np.linalg.norm(field.grad(X)))
        if gn < 1e-2:
            break
    return E, X, gn


def max_pair_overlap(field, X):
    P = field.all_pos(X)
    if len(P) < 2:
        return 0.0
    I, J = np.triu_indices(len(P), 1)
    d = np.linalg.norm(P[I] - P[J], axis=1)
    return float(max(0.0, np.max(field.r[I] + field.r[J] - d)))


def squeeze(field, X, ids):
    """Neighbour with the smallest surface gap to the blocker (index 0) at configuration X."""
    P = field.all_pos(X)
    if len(P) < 2:
        return None
    gaps = np.linalg.norm(P[1:] - P[0], axis=1) - field.r[1:] - field.r[0]
    j = int(np.argmin(gaps)) + 1
    dw, _ = agents_to_walls(P[:1], field.world.walls)
    return {"neighbour": int(ids[j]), "neighbour_pos": P[j].tolist(), "gap_m": float(gaps[j - 1]),
            "blocker_saddle_pos": P[0].tolist(), "blocker_wall_clearance_m": float(np.min(dw[0]) - field.r[0])}


def resample(poly, n):
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    L = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, L[-1], n)
    return np.column_stack([np.interp(t, L, poly[:, d]) for d in range(poly.shape[1])])


def one(field, XA, XB, n, init=None):
    if init is None:
        s = np.linspace(0, 1, n)[:, None]
        path = (1 - s) * XA + s * XB
    else:
        path = init(n)
    path, it, fp = converge(field, path)
    E, X, gn = climb(field, path)
    u0 = field.U(XA)
    return {"n_img": n, "dU_climb": float(field.U(X) - u0), "dU_string": float(E.max() - u0),
            "iters": it, "F_perp_max": float(fp.max()), "F_perp_sum": float(fp.sum()), "grad_norm_saddle": gn,
            "final_x": float(path[-1][0]), "saddle": X.tolist(), "max_pair_overlap_m": max_pair_overlap(field, X)}


def conv_reasons(res, n0, n1):
    rel = abs(res[n0]["dU_climb"] - res[n1]["dU_climb"]) / max(abs(res[n1]["dU_climb"]), 1e-12)
    why = []
    if res[n1]["F_perp_max"] >= F_TOL:
        why.append("string at %d images not converged (F_perp_max %.3g N)" % (n1, res[n1]["F_perp_max"]))
    if rel >= DOUBLE_TOL:
        why.append("barrier changes by %.2g%% from %d to %d images" % (100 * rel, n0, n1))
    return why, rel


def grid_barrier(field, XA, h):
    """Minimum-energy-path barrier of the single mobile agent's potential on a 2-D grid of spacing h."""
    from scipy import ndimage
    x0, x1, y0, y1 = GRID_BOX
    xs = np.arange(x0, x1 + h / 2, h)
    ys = np.arange(y0, y1 + h / 2, h)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    P = np.column_stack([X.ravel(), Y.ravel()])
    r = field.r[0]
    U = field.c[0] * np.linalg.norm(P - bar.G, axis=1)
    for k in range(0, len(P), 200000):
        d, _ = agents_to_walls(P[k:k + 200000], field.world.walls)
        U[k:k + 200000] += np.sum(bar.A * bar.B * np.exp((r - d) / bar.B) + 0.5 * bar.K * np.maximum(0, r - d) ** 2,
                                  axis=1)
    U = U.reshape(X.shape)
    i0 = int(np.argmin(np.abs(xs - XA[0])))
    j0 = int(np.argmin(np.abs(ys - XA[1])))
    tgt = xs >= X_EXIT - 1e-9
    st = np.ones((3, 3), bool)

    def connected(level):
        lab, _ = ndimage.label(U <= level, structure=st)
        L0 = lab[i0, j0]
        return L0 > 0 and np.any(lab[tgt] == L0)
    lo, hi = float(U[i0, j0]), float(U.max())
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if connected(mid):
            hi = mid
        else:
            lo = mid
    return hi - field.U(XA)


def grid_check(field, XA):
    v = [grid_barrier(field, XA, h) for h in GRID_H]
    rel = abs(v[0] - v[1]) / max(abs(v[1]), 1e-12)
    return {"h_m": list(GRID_H), "dU": v, "rel_change_halving": rel}


def check(field, XA, XB, ids, init=None, prev=None, grid=None):
    res = {}
    for n in RESOLUTIONS[:2]:
        key = "n%d" % n
        res[n] = prev[key] if prev and key in prev else one(field, XA, XB, n, init)
    first, rel = conv_reasons(res, 31, 62)
    pair = (31, 62)
    why = list(first)
    if first:
        res[124] = prev["n124"] if prev and "n124" in prev else one(field, XA, XB, 124, init)
        why, rel = conv_reasons(res, 62, 124)
        pair = (62, 124)
    f = res[pair[1]]
    if f["dU_climb"] < f["dU_string"] - GUARD_TOL:
        why.append("climbing image below the path maximum (%.4g < %.4g J)" % (f["dU_climb"], f["dU_string"]))
    if f["grad_norm_saddle"] >= 1e-2:
        why.append("climbing image not converged")
    if f["final_x"] < 10.0:
        why.append("final image not an exit state")
    if f["max_pair_overlap_m"] > OVERLAP_MAX:
        why.append("saddle overlap %.3f m" % f["max_pair_overlap_m"])
    if grid is not None:
        if grid["rel_change_halving"] >= GRID_RES_TOL:
            why.append("grid barrier changes by %.2g%% on halving the spacing" % (100 * grid["rel_change_halving"]))
        rg = abs(f["dU_climb"] - grid["dU"][1]) / max(abs(grid["dU"][1]), 1e-12)
        grid = dict(grid, rel_diff_string=rg)
        if rg >= GRID_TOL:
            why.append("alone vs 2-D grid path differs by %.2g%% (%.4g vs %.4g J)" % (100 * rg, f["dU_climb"], grid["dU"][1]))
    out = {"accepted": not why, "reasons": why, "dU": f["dU_climb"], "resolution_pair": list(pair),
           "first_pair_reasons": first, "rel_change_doubling": rel,
           "squeeze": squeeze(field, np.array(f["saddle"]), ids)}
    out.update({"n%d" % n: v for n, v in res.items()})
    if grid is not None:
        out["grid"] = grid
    return out


def axis_init(field, XA, ids):
    """Second initial path for the frozen condition: blocker onto the door axis, then along it.
    Neighbours are pushed off the path in y for the initial relaxation only."""
    poly = np.array([XA, [XA[0], 5.0], [X_EXIT, 5.0]])
    disp = field.fixed_pos.copy()
    rb = field.r[0]
    for j in range(len(disp)):
        rj = field.r[1 + j]
        for _ in range(2000):
            dense = resample(poly, 400)
            if np.min(np.linalg.norm(dense - disp[j], axis=1)) >= rb + rj + 0.02:
                break
            disp[j, 1] += 0.001 if disp[j, 1] >= 5.0 else -0.001
    true_pos = field.fixed_pos

    def init(n):
        field.fixed_pos = disp
        try:
            p = string_iter(field, resample(poly, n), SCHEDULE[0][0], SCHEDULE[0][1])
        finally:
            field.fixed_pos = true_pos
        return p
    return init, {int(ids[1 + j]): disp[j].tolist() for j in range(len(disp))
                  if not np.allclose(disp[j], true_pos[j])}


def run(job):
    w0 = time.perf_counter()
    prev = job.get("prev") or {}
    snap = pickle.load(open(job["snap"], "rb"))
    b = job["blocker"]
    resid = [int(i) for i in snap["state"].active_indices]
    others = [i for i in resid if i != b]
    xb = snap["state"].positions[b].copy()
    XB = np.array([X_EXIT, 5.0])
    row = {"job_id": job["job_id"], "blocker": b, "resid": resid, "dU_bar": job["dU_bar"],
           "dU_1d_axis_alone": job["dU_1d"], "F_TOL_N": F_TOL, "gate_version": 2,
           "reused_from_v1": bool(prev)}
    fa = bar.Field(snap, [b], [], rho_mode="zero")
    XA = bar.relax(fa, xb.copy())
    row["alone"] = check(fa, XA, XB, [b], prev=prev.get("alone"), grid=grid_check(fa, XA))
    if not others:
        row["frozen"] = dict(row["alone"], same_as="alone")
        row["full"] = dict(row["alone"], same_as="alone")
    else:
        ff = bar.Field(snap, [b], others)
        XA = bar.relax(ff, xb.copy())
        pf = prev.get("frozen")
        pf_path = (pf or {}).get("path", "straight")
        fr = check(ff, XA, XB, [b] + others, prev=pf if pf_path == "straight" else None)
        fr["path"] = "straight"
        if fr["dU"] > FROZEN_RATIO * row["alone"]["dU"]:
            init, disp = axis_init(ff, XA, [b] + others)
            fr2 = check(ff, XA, XB, [b] + others, init=init, prev=pf if pf_path == "axis" else None)
            fr2["path"] = "axis"
            fr2["displaced_for_initial_guess"] = disp
            cands = [x for x in (fr, fr2) if x["accepted"]]
            best = min(cands, key=lambda x: x["dU"]) if cands else min((fr, fr2), key=lambda x: x["dU"])
            best = dict(best, alternatives=[{k: x[k] for k in ("path", "accepted", "reasons", "dU", "squeeze",
                                                                "n31", "n62") if k in x}
                                            for x in (fr, fr2)])
            fr = best
        row["frozen"] = fr
        fm = bar.Field(snap, [b] + others, [])
        X0 = snap["state"].positions[[b] + others].ravel()
        XA = bar.relax(fm, X0)
        XBf = XA.copy()
        XBf[0:2] = XB
        XBf = bar.relax(fm, XBf, fix_idx=(0, 1))
        row["full"] = check(fm, XA, XBf, [b] + others, prev=prev.get("full"))
    row["wall_s"] = time.perf_counter() - w0
    return row


def jobs():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    B = {r["job_id"]: r for r in load_runs(os.path.join(OUTD, "barriers.jsonl"))}
    V1 = {r["job_id"]: r for r in load_runs(PREV)} if os.path.exists(PREV) else {}
    J = []
    for s in sel["E2"]["snapshots"]:
        if s["tag"] not in B:  # no BAR row: no gate row, treated as failed downstream
            continue
        r = B[s["tag"]]
        J.append({"job_id": s["tag"], "snap": os.path.join(ROOT, s["snap"]), "blocker": s["blocker"],
                  "dU_1d": r["dU_1d_axis_alone"],
                  "dU_bar": {c: r[k]["dU_climb"] for c, k in (("alone", "alone"), ("frozen", "frozen"),
                                                              ("full", "all_mobile"))},
                  "prev": {c: V1[s["tag"]][c] for c in CONDS} if s["tag"] in V1 else None})
    return J


def gated_table(out=OUT):
    rows = sorted(load_runs(out), key=lambda r: r["job_id"])
    tab = {}
    for r in rows:
        tab[r["job_id"]] = {c: {"accepted": r[c]["accepted"], "dU": r[c]["dU"], "reasons": r[c]["reasons"],
                                "dU_bar": r["dU_bar"][c], "squeeze": r[c].get("squeeze"),
                                "path": r[c].get("path")} for c in CONDS}
    fails = [{"tag": t, "cond": c, "reasons": v[c]["reasons"]} for t, v in tab.items() for c in CONDS
             if not v[c]["accepted"]]
    return {"script": "experiments/BAR/gate.py", "doc": __doc__, "n": len(tab), "failed": fails,
            "barriers": tab}


def main(out=OUT, workers=4, J=None):
    os.makedirs(OUTD, exist_ok=True)
    wall = run_jobs(jobs() if J is None else J, run, out, workers=workers, log_every=4)
    if out == OUT:
        json.dump(gated_table(out), open(GATED, "w"), indent=1, default=float)
    return wall


if __name__ == "__main__":
    print("wall", main())
