"""E7b_barrier: string-method barrier of the pair standoff, through the C15a validity gate.

Snapshots: N_SEL = 12 of the pair library (at least 10 are required), spread over lambda1 (the smallest
Hessian eigenvalue from data/E7b/e7b_static.jsonl): the snapshots at evenly spaced ranks of lambda1
(numpy linspace over the sorted list, rounded). Needs E7b_static to be complete.
Field: rest-state C1 potential with density frozen at the snapshot value, both members mobile
(experiments/lib/pairlib.PairBarField = BAR's field with the wall terms at the run's B_w = 0.04).
Exit channels: for each member m, the path runs from the relaxed pair minimum to the end state with m at
(10.35, 5) and the other member relaxed with m pinned (BAR's all_mobile end point, m in the blocker slot).
Each channel goes through the C15a gate (experiments/BAR/gate.check, unchanged: 31 / 62 image strings,
124 if needed, upwind-tangent perpendicular force below 5 N on the uphill images, climbing image at
|grad U| < 0.01 N and the maximum of U on the path, barrier change < 1% on doubling, final image past the
door plane, saddle overlap <= 2 cm). The alone grid check (iii) and the frozen second path do not apply.
The pair barrier is the lower of the accepted channel barriers; the field check max |F_code + grad U|
(BAR's code_force_check) is recorded.
Output: data/E7b/e7b_barrier.jsonl (job_id = snapshot tag), resumable.
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "BAR"))
sys.path.insert(0, HERE)
from e1lib import DATA, load_runs, run_jobs  # noqa: E402
import numpy as np  # noqa: E402
import bar  # noqa: E402
import gate  # noqa: E402
import pairlib  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402

OUT = os.path.join(DATA, "E7b", "e7b_barrier.jsonl")
STATIC = os.path.join(DATA, "E7b", "e7b_static.jsonl")
N_SEL = 12


def run(job):
    w0 = time.perf_counter()
    snap = pickle.load(open(job["snap"], "rb"))
    ids = pairlib.residual_ids(snap)
    row = {"job_id": job["job_id"], "snap": os.path.basename(job["snap"]), "members": ids,
           "lambda1": job["lambda1"], "lambda1_rank": job["rank"], "F_TOL_N": gate.F_TOL, "channels": {}}
    XB = np.array([gate.X_EXIT, 5.0])
    for m in ids:
        o = [i for i in ids if i != m][0]
        fm = pairlib.PairBarField(snap, [m, o])
        row.setdefault("force_check_maxabs_N", bar.code_force_check(snap, [m, o], fm))
        X0 = snap["state"].positions[[m, o]].ravel()
        XA = bar.relax(fm, X0)
        XBf = XA.copy()
        XBf[0:2] = XB
        XBf = bar.relax(fm, XBf, fix_idx=(0, 1))
        c = gate.check(fm, XA, XBf, [m, o])
        c["side"] = "lower" if snap["state"].positions[m, 1] < 5.0 else "upper"
        c["x_min"] = XA.tolist()
        row["channels"][str(m)] = c
    acc = {m: c for m, c in row["channels"].items() if c["accepted"]}
    row["accepted"] = bool(acc)
    if acc:
        m = min(acc, key=lambda k: acc[k]["dU"])
        row.update({"dU": acc[m]["dU"], "exit_member": int(m), "exit_side": acc[m]["side"]})
    row["wall_s"] = time.perf_counter() - w0
    return row


def jobs(static=STATIC):
    S = {r["job_id"]: r for r in load_runs(static)} if os.path.exists(static) else {}
    P = [p for p in pairs() if p["tag"] in S]
    if not P:
        return []
    P.sort(key=lambda p: S[p["tag"]]["lambda1"])
    sel = sorted(set(int(round(x)) for x in np.linspace(0, len(P) - 1, min(N_SEL, len(P)))))
    return [{"job_id": P[k]["tag"], "snap": P[k]["snap"], "lambda1": S[P[k]["tag"]]["lambda1"], "rank": k}
            for k in sel]


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    if "--iters" in a.rest:   # smoke tests only: shortened string schedule
        n = int(a.rest[a.rest.index("--iters") + 1])
        gate.SCHEDULE = [(n, 4e-5), (n // 3, 1e-5), (n // 3, 1e-5)]
        gate.converge.__defaults__ = (gate.SCHEDULE,)
    static = a.rest[a.rest.index("--static") + 1] if "--static" in a.rest else STATIC
    J = qargs.select(jobs(static), a)
    if len(J) < 10 and a.out is None:
        print("E7b_barrier: fewer than 10 snapshots available (is E7b_static complete?)", len(J), flush=True)
        sys.exit(2)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(J, run, out, workers=a.workers, log_every=1)


if __name__ == "__main__":
    print("wall", main())
