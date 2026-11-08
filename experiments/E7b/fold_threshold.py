"""Static fold threshold per pair snapshot, by bisection of the a5 overdamped relaxation (pairlib.relax).

For each of the 46 E7b pair snapshots and each sign s = +1, -1 of the lateral bias, the threshold
b*_s = inf{ |b| : relax(C1 + lateral bias s|b|) frees a member } is bracketed by the E7b_static grid
|b| in {0, 0.01, 0.02, 0.03, 0.05, 0.1} (the grid outcomes are recomputed here, not read) and then bisected
to a bracket width of 1e-4 (C1 at b = 0 holds in 46/46). Undecided relaxations (no exit and max |F| >= 0.05 N
at 120 s) count as held and are recorded. The side of the member that exits first at the upper bracket end
is recorded.
Flags: snapshot params (CF union {B_w: 0.04}) plus {w2_noise: lateral_bias, w2_bias_b}, as E7b_static.
Output: data/E7b_bstar/fold_threshold.jsonl (job_id "<tag>|<sign>"), resumable.
"""
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
sys.path.insert(0, HERE)
from e1lib import DATA, run_jobs  # noqa: E402
import pairlib  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402

OUT = os.path.join(DATA, "E7b_bstar", "fold_threshold.jsonl")
GRID = (0.0, 0.01, 0.02, 0.03, 0.05, 0.1)
TOL = 1e-4


def run(job):
    w0 = time.perf_counter()
    snap = pickle.load(open(job["snap"], "rb"))
    s = job["sign"]
    calls = []

    def freed(b):
        if b == 0.0:
            r = pairlib.relax(snap, "C1", {})
        else:
            r = pairlib.relax(snap, "C1", {"w2_noise": "lateral_bias", "w2_bias_b": s * b})
        calls.append({"b": s * b, "pred": r["pred_freed"], "t": r["t"], "first_side": r.get("first_side")})
        return bool(r["pred_freed"]), r
    grid = {}
    lo = hi = None
    r_hi = None
    for b in GRID:
        f, r = freed(b)
        grid[f"{b:g}"] = f
        if f:
            hi, r_hi = b, r
            break
        lo = b
    nonmono = None
    if hi is not None:
        while hi - lo > TOL:
            mid = 0.5 * (lo + hi)
            f, r = freed(mid)
            if f:
                hi, r_hi = mid, r
            else:
                lo = mid
        # monotonicity spot check on the remaining grid points above the threshold
        nonmono = [b for b in GRID if b > hi and not freed(b)[0]]
    return {"job_id": job["job_id"], "tag": job["tag"], "sign": s, "grid_freed": grid,
            "b_lo": lo, "b_hi": hi, "b_star": None if hi is None else 0.5 * (lo + hi),
            "first_side_at_hi": None if r_hi is None else r_hi.get("first_side"),
            "undecided_calls": sum(c["pred"] is None for c in calls), "nonmonotone_above": nonmono,
            "calls": calls, "wall_s": time.perf_counter() - w0}


def jobs():
    return [{"job_id": f"{p['tag']}|{s:+d}", "tag": p["tag"], "snap": p["snap"], "sign": s}
            for p in pairs() for s in (1, -1)]


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(qargs.select(jobs(), a), run, out, workers=a.workers, log_every=4)


if __name__ == "__main__":
    print("wall", main())
