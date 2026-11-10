"""B6 static: does the E7b pair minimum survive a line goal (w2_goal = "line")?

Inputs: the 46 E7b pair snapshots (experiments/E7b/e7b_pairs.py; sharp door, C1, CF union {B_w: 0.04}).
For each snapshot: the code's C1 rest-state force on the two members (B5_lib.PairRest, goal = "line": each
member's goal is the nearest point of the segment x = 11, y in [5 - w/2 + r_i, 5 + w/2 - r_i], recomputed at
every evaluation as Simulation.step does; v = 0, density frozen at the snapshot, b = 0), relaxed from the
point-goal snapshot positions (B5_lib.relax: dx/dt = (tau/m) F, Euler 0.01 s, 120 s; freed at x > 10.3 m,
held at max |F| < 0.05 N), Newton polish, then B5_lib.rest_checks (Hessian -sym(J) positive definite,
asymmetry of J, contact-free, both x < 10, opposite sides, front of jambs). The line-goal drive c_i e_i with
e_i = -grad dist(x_i, goal segment) is a gradient, so -sym(J) is the Hessian (the asymmetry is recorded).
Also recorded: the point-goal minimum's mu1 and lateral drive for comparison, and the displacement.
Output: data/revision/B6/static.jsonl (job_id "<tag>"), resumable.
"""
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402
import B5_lib as L  # noqa: E402
import numpy as np  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402

D = revlib.data_dir("B6")
OUT = os.path.join(D, "static.jsonl")


def run(job):
    w0 = time.perf_counter()
    snap = pickle.load(open(job["snap"], "rb"))
    fp = L.PairRest(snap, goal="point")
    Xp, _, okp = L.equilibrate(fp, fp.X_snap)
    cp = L.rest_checks(fp, Xp)
    f = L.PairRest(snap, goal="line")
    X, r, ok = L.equilibrate(f, f.X_snap)
    mv = np.linalg.norm((X - f.X_snap).reshape(-1, 2), axis=1)
    row = {k: v for k, v in job.items() if k != "snap"}
    row.update({"members": f.ids, "point_eig": cp["eig"], "point_strict_min": cp["strict_min"],
                "relax_freed": r["pred_freed"], "relax_t": r["t"], "first_side": r.get("first_side"),
                "newton_ok": ok, "X": X.tolist(), "move": mv.tolist(), "move_max": float(mv.max())})
    if ok:
        c = L.rest_checks(f, X)
        c["kept"] = bool(c["strict_min"] and c["contact_free"] and c["before_door"] and c["opposite"])
        f.st.positions[:] = X.reshape(-1, 2)
        row["line_goals"] = f.scen.line_goals(f.st).tolist()
        row.update(c)
    else:
        row["kept"] = False
    row["wall_s"] = time.perf_counter() - w0
    return row


def jobs():
    return [{"job_id": p["tag"], "tag": p["tag"], "snap": p["snap"], "seed": p["seed"]} for p in pairs()]


def main(argv=None):
    a = qargs.parse(argv)
    return revlib.run_jobs(qargs.select(jobs(), a), run, a.out or OUT, workers=a.workers, log_every=10)


if __name__ == "__main__":
    print("wall", main())
