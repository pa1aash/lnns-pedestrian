"""Barrier validity gate (plan change C15a): re-checks every BAR result before E3 / E4 use it.

For each E2 snapshot and condition (alone, frozen, full = all_mobile) the minimum-energy path is
recomputed with the BAR field, end points and step cap (experiments/BAR/bar.py), and the barrier is
accepted only if:
  (i)   the string has converged: F_perp_max, the largest norm over the uphill interior images (trapped
        minimum to one image past the top) of the gradient component perpendicular to the path (all
        mobile coordinates; upwind tangent), is below F_TOL = 5 N (about 2.5% of the blocker's drive);
        the sum over those images is recorded; the climbing image reaches |grad U| < 1e-2 N; and the climbing-
        image barrier changes by less than 1% when the number of images is doubled (31 -> 62);
  (ii)  the final image is an exit state (blocker centre past the door plane, x >= 10) and the saddle
        has no agent-agent overlap deeper than 2 cm;
  (iii) alone only: the barrier agrees with the 1-D on-axis integral (BAR dU_1d_axis_alone) to 1%.
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
GATED = os.path.join(OUTD, "barriers_gated.json")
CONDS = ("alone", "frozen", "full")
F_TOL = 5.0            # N, on F_perp_max: about 2.5% of the blocker's drive m v0 / tau (~200 N)
DOUBLE_TOL = 0.01      # relative change of the barrier, 31 -> 62 images
OVERLAP_MAX = 0.02     # m, deepest agent-agent overlap at the saddle
AXIS_TOL = 0.01        # relative, alone barrier vs 1-D on-axis integral
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


def check(field, XA, XB, ids, init=None, dU_1d=None):
    a, b = one(field, XA, XB, 31, init), one(field, XA, XB, 62, init)
    rel = abs(a["dU_climb"] - b["dU_climb"]) / max(abs(b["dU_climb"]), 1e-12)
    why = []
    if a["F_perp_max"] >= F_TOL or b["F_perp_max"] >= F_TOL:
        why.append("string not converged (F_perp_max %.3g / %.3g N)" % (a["F_perp_max"], b["F_perp_max"]))
    if rel >= DOUBLE_TOL:
        why.append("image doubling changes the barrier by %.2g%%" % (100 * rel))
    if a["grad_norm_saddle"] >= 1e-2:
        why.append("climbing image not converged")
    if a["final_x"] < 10.0:
        why.append("final image not an exit state")
    if a["max_pair_overlap_m"] > OVERLAP_MAX:
        why.append("saddle overlap %.3f m" % a["max_pair_overlap_m"])
    if dU_1d is not None:
        r1 = abs(a["dU_climb"] - dU_1d) / max(abs(dU_1d), 1e-12)
        if r1 >= AXIS_TOL:
            why.append("alone vs 1-D on-axis differs by %.2g%%" % (100 * r1))
    return {"accepted": not why, "reasons": why, "dU": a["dU_climb"], "dU_62": b["dU_climb"],
            "rel_change_doubling": rel, "n31": a, "n62": b,
            "squeeze": squeeze(field, np.array(a["saddle"]), ids)}


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
    snap = pickle.load(open(job["snap"], "rb"))
    b = job["blocker"]
    resid = [int(i) for i in snap["state"].active_indices]
    others = [i for i in resid if i != b]
    xb = snap["state"].positions[b].copy()
    XB = np.array([X_EXIT, 5.0])
    row = {"job_id": job["job_id"], "blocker": b, "resid": resid, "dU_bar": job["dU_bar"],
           "dU_1d_axis_alone": job["dU_1d"], "F_TOL_N": F_TOL}
    fa = bar.Field(snap, [b], [], rho_mode="zero")
    XA = bar.relax(fa, xb.copy())
    row["alone"] = check(fa, XA, XB, [b], dU_1d=job["dU_1d"])
    if not others:
        row["frozen"] = dict(row["alone"], same_as="alone")
        row["full"] = dict(row["alone"], same_as="alone")
    else:
        ff = bar.Field(snap, [b], others)
        XA = bar.relax(ff, xb.copy())
        fr = check(ff, XA, XB, [b] + others)
        fr["path"] = "straight"
        if fr["dU"] > FROZEN_RATIO * row["alone"]["dU"]:
            init, disp = axis_init(ff, XA, [b] + others)
            fr2 = check(ff, XA, XB, [b] + others, init=init)
            fr2["path"] = "axis"
            fr2["displaced_for_initial_guess"] = disp
            cands = [x for x in (fr, fr2) if x["accepted"]]
            best = min(cands, key=lambda x: x["dU"]) if cands else min((fr, fr2), key=lambda x: x["dU"])
            best = dict(best, alternatives=[{k: x[k] for k in ("path", "accepted", "reasons", "dU", "squeeze")}
                                            for x in (fr, fr2)])
            fr = best
        row["frozen"] = fr
        fm = bar.Field(snap, [b] + others, [])
        X0 = snap["state"].positions[[b] + others].ravel()
        XA = bar.relax(fm, X0)
        XBf = XA.copy()
        XBf[0:2] = XB
        XBf = bar.relax(fm, XBf, fix_idx=(0, 1))
        row["full"] = check(fm, XA, XBf, [b] + others)
    row["wall_s"] = time.perf_counter() - w0
    return row


def jobs():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    B = {r["job_id"]: r for r in load_runs(os.path.join(OUTD, "barriers.jsonl"))}
    J = []
    for s in sel["E2"]["snapshots"]:
        if s["tag"] not in B:  # no BAR row: no gate row, treated as failed downstream
            continue
        r = B[s["tag"]]
        J.append({"job_id": s["tag"], "snap": os.path.join(ROOT, s["snap"]), "blocker": s["blocker"],
                  "dU_1d": r["dU_1d_axis_alone"],
                  "dU_bar": {c: r[k]["dU_climb"] for c, k in (("alone", "alone"), ("frozen", "frozen"),
                                                              ("full", "all_mobile"))}})
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
