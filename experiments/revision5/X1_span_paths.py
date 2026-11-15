"""X1 runs: converged string paths of the barrier library, kept image by image, for the energy-span check.

The gate (experiments/BAR/gate.py, v2) stored only the barrier, the saddle and the convergence numbers of each string,
not the images. This script recomputes, for each of the 60 E2 snapshots and each condition (alone, frozen = pinned,
full = all mobile), the string the gate accepted (or, for the 4 rejected full strings, the string the gate rejected),
with the gate's own code and settings: gate.converge (1500 iterations at alpha 4e-5, then up to two blocks of 500 at
1e-5 while F_perp_max >= 5 N), gate.climb (climbing image to |grad U| < 1e-2 N), the same end points (relaxed snapshot
minimum; blocker at (10.35, 5) with the others relaxed for full) and the same initial path (straight, or the gate's
axis path where the accepted frozen string used it), at the finer resolution of the gate's accepted pair (62 or 124
images). The computation is deterministic, so the recomputed climbing-image barrier is compared with the stored one
(gate.jsonl <cond>.n<N>.dU_climb) and the difference recorded.
Kept per path: U(s_k) - U(s_0) for every image, the image coordinates (mobile agents, 1e-7 m), the climbing-image
energy and position.
Exit: the path is taken from s_0 to the first image with the blocker centre at x >= 10 m (door plane, the escape
event of the runs); past it the string descends towards the goal and rises to the fixed end image (not a minimum).
Second strings: every interior local minimum of the image energies (zigzag extrema with swing >= 0.05 J on both
sides) is relaxed (bar.relax, 20000 steps) to a rest state M, and the gate's full check (gate.check: 31 / 62 images,
124 if the doubling rule fails; F_perp, climbing image, exit state, overlap) is run from M to the same exit end point,
giving the exit barrier from M with the gate's acceptance verdict (for C3's E1b_seed170 this reproduces 2.82 J).
One-agent snapshots: the three conditions are the same field (gate: same_as alone), computed once as "alone".
Output: data/revision5/X1/x1_paths.jsonl (job_id "<tag>|<cond>").
Usage: X1_span_paths.py [--workers W] [--only TAG] [--skip JOB_ID,...] (skip: a job running in another process)
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev5lib  # noqa: E402
from rev5lib import DATA, ROOT, np, run_jobs  # noqa: E402
import bar  # noqa: E402
import gate  # noqa: E402

OUTD = rev5lib.data_dir("X1")
OUT = os.path.join(OUTD, "x1_paths.jsonl")
SWING = 0.05      # J, interior-minimum threshold on both sides
MAX_SECOND = 4    # interior minima followed per path (deepest first)
X_DOOR = 10.0     # m, door plane: the path is taken from the snapshot minimum to the first image with blocker x >= 10


def zigzag(E, h=SWING):
    """Alternating extrema of E with every swing >= h. Returns [(index, 'min'|'max'), ...]; the first entry is image 0
    and the last the final image (their type set by the direction of the first / last swing)."""
    n = len(E)
    ext = []
    mode, cand = None, 0
    for k in range(1, n):
        if mode is None:
            if E[k] - E[0] >= h:
                ext.append((0, "min")); mode, cand = "up", k
            elif E[0] - E[k] >= h:
                ext.append((0, "max")); mode, cand = "down", k
        elif mode == "up":
            if E[k] > E[cand]:
                cand = k
            elif E[cand] - E[k] >= h:
                ext.append((cand, "max")); mode, cand = "down", k
        else:
            if E[k] < E[cand]:
                cand = k
            elif E[k] - E[cand] >= h:
                ext.append((cand, "min")); mode, cand = "up", k
    if mode is None:
        return [(0, "flat")]
    ext.append((cand, "max" if mode == "up" else "min"))
    return ext


def interior_minima(E, h=SWING):
    ext = zigzag(E, h)
    return [k for (k, t) in ext[1:-1] if t == "min"]


def span(E):
    """Largest rise from any image to any later image: (dU_span, i, j)."""
    best, bi, bj = -np.inf, 0, 0
    imin = 0
    for j in range(1, len(E)):
        if E[j - 1] < E[imin]:
            imin = j - 1
        if E[j] - E[imin] > best:
            best, bi, bj = E[j] - E[imin], imin, j
    return float(best), int(bi), int(bj)


def setup(job):
    snap = pickle.load(open(job["snap"], "rb"))
    b = job["blocker"]
    resid = [int(i) for i in snap["state"].active_indices]
    others = [i for i in resid if i != b]
    xb = snap["state"].positions[b].copy()
    XB = np.array([gate.X_EXIT, 5.0])
    cond = job["cond"]
    init = None
    if cond == "alone":
        f = bar.Field(snap, [b], [], rho_mode="zero")
        ids = [b]
        XA = bar.relax(f, xb.copy())
        XE = XB
    elif cond == "frozen":
        f = bar.Field(snap, [b], others)
        ids = [b] + others
        XA = bar.relax(f, xb.copy())
        XE = XB
        if job["path"] == "axis":
            init, _ = gate.axis_init(f, XA, ids)
    else:
        f = bar.Field(snap, [b] + others, [])
        ids = [b] + others
        X0 = snap["state"].positions[[b] + others].ravel()
        XA = bar.relax(f, X0)
        XE = XA.copy()
        XE[0:2] = XB
        XE = bar.relax(f, XE, fix_idx=(0, 1))
    return snap, f, ids, XA, XE, init


def run(job):
    w0, c0 = time.perf_counter(), time.process_time()
    snap, f, ids, XA, XE, init = setup(job)
    n = job["n_img"]
    if init is None:
        s = np.linspace(0, 1, n)[:, None]
        path = (1 - s) * XA + s * XE
    else:
        path = init(n)
    path, it, fp = gate.converge(f, path)
    Eabs, Xc, gn = gate.climb(f, path)
    u0 = f.U(XA)
    E = Eabs - u0
    dU_climb = float(f.U(Xc) - u0)
    # the exit: first image with the blocker centre at or past the door plane x = 10 m (the escape event of the runs).
    # Beyond it the string keeps descending towards the goal and rises again to the fixed end image, which is not a
    # minimum; that part is not on the path to the exit and is left out of minima and span.
    k_exit = int(next((k for k in range(len(path)) if path[k, 0] >= X_DOOR), len(path) - 1))
    Et = E[:k_exit + 1]
    mins = interior_minima(Et)
    sp, si, sj = span(Et)
    out = {k: v for k, v in job.items() if k != "snap"}
    out.update({"agents": ids, "n_mobile": f.nm, "iters": it, "F_perp_max": float(fp.max()),
                "U0_abs_J": float(u0), "E_J": E.tolist(), "dU_climb": dU_climb, "grad_norm_saddle": gn,
                "k_top": int(np.argmax(E)), "climb_X": Xc.tolist(),
                "dU_climb_stored": job["dU_stored"], "rel_diff_vs_stored": abs(dU_climb - job["dU_stored"]) /
                max(abs(job["dU_stored"]), 1e-12),
                "path_X": np.round(path, 7).tolist(), "blocker_x": path[:, 0].tolist(),
                "k_exit": k_exit, "zigzag": zigzag(Et), "zigzag_whole": zigzag(E), "interior_minima": mins, "span_img": [sp, si, sj]})
    sec = []
    for k in sorted(mins, key=lambda k: E[k])[:MAX_SECOND]:
        M = bar.relax(f, path[k].copy(), steps=20000)
        uM = f.U(M) - u0
        res = gate.check(f, M, XE, ids)
        sec.append({"from_image": int(k), "E_image_J": float(E[k]), "U_M_minus_U0_J": float(uM),
                    "grad_norm_M": float(np.linalg.norm(f.grad(M))),
                    "M_shift_from_image_m": float(np.max(np.linalg.norm((M - path[k]).reshape(-1, 2), axis=1))),
                    "M": M.tolist(), "img_exit_barrier_J": float(Et[k:].max() - Et[k]),
                    "accepted": res["accepted"], "reasons": res["reasons"], "dU_exit_from_M": res["dU"],
                    "resolution_pair": res["resolution_pair"],
                    "strings": {key: {kk: v for kk, v in res[key].items() if kk != "saddle"}
                                for key in ("n31", "n62", "n124") if key in res},
                    "exit_saddle_X": res["n%d" % res["resolution_pair"][1]]["saddle"]})
    out.update({"second": sec, "cpu_s": time.process_time() - c0, "wall_s": time.perf_counter() - w0})
    return out


def jobs(only=None):
    G = {r["job_id"]: r for r in rev5lib.load_runs(os.path.join(DATA, "BAR", "gate.jsonl"))}
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    J = []
    for s in sel["E2"]["snapshots"]:
        tag = s["tag"]
        if tag not in G or (only and tag != only):
            continue
        g = G[tag]
        for c in gate.CONDS:
            r = g[c]
            if r.get("same_as"):
                continue
            nfine = r["resolution_pair"][1]
            J.append({"job_id": f"{tag}|{c}", "tag": tag, "cond": c, "snap": os.path.join(ROOT, s["snap"]),
                      "blocker": s["blocker"], "n_img": nfine, "path": r.get("path") or "straight",
                      "gate_accepted": r["accepted"], "gate_reasons": r["reasons"],
                      "dU_gate": r["dU"], "dU_stored": r["n%d" % nfine]["dU_climb"]})
    # longest first (more mobile agents, finer strings)
    J.sort(key=lambda j: -(j["n_img"] * (1 + 3 * (j["cond"] == "full"))))
    return J


if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    skip = sys.argv[sys.argv.index("--skip") + 1].split(",") if "--skip" in sys.argv else []
    J = [j for j in jobs(only) if j["job_id"] not in skip]
    print("wall", run_jobs(J, run, OUT, workers=rev5lib.workers(sys.argv), log_every=1))
