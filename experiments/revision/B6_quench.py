"""B6 quench: the 46 E7b pair snapshots restarted with the line goal.

Every run restarts the frozen pair snapshot (experiments/E7b/e7b_pairs.py) with C1 and the full flag set
CF union {B_w: 0.04} union {w2_goal: line}, dt = 0.01 s, 120 s, deterministic: unperturbed, stationary stop
(every active |v| < 1e-3 m/s for 10 s, no exit) as the deterministic arms of experiments/E7b/e7b_quench.py,
whose runner (e7b_quench.run, unchanged) is used. Arms: "line" (w2_goal = line) and, as the in-file control,
"point" (C1 with the point goal, the E7b C1 arm). Replays: also 5 runs per snapshot with 1e-9 m Gaussian
position perturbations of both members (seeds 900-904, as E7b) for the line arm.
Output: data/revision/B6/quench.jsonl (job_id "<tag>|<arm>|<rep>"), resumable.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402
import e7b_quench  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402

D = revlib.data_dir("B6")
OUT = os.path.join(D, "quench.jsonl")
BASE = {**revlib.CF, "B_w": 0.04}
ARMS = {"line": {"w2_goal": "line"}, "point": {}}
T_Q = 120.0


def jobs():
    J = []
    for p in pairs():
        for arm, fl in ARMS.items():
            for ps in (None,) + (e7b_quench.PERTURB_SEEDS if arm == "line" else ()):
                J.append({"job_id": f"{p['tag']}|{arm}|{'u' if ps is None else ps}", "tag": p["tag"],
                          "snap": p["snap"], "arm": arm, "config": "C1", "flags": {**BASE, **fl},
                          "deterministic": True, "perturb": ps, "t_q": T_Q})
    return J


def main(argv=None):
    a = qargs.parse(argv)
    return revlib.run_jobs(qargs.select(jobs(), a), e7b_quench.run, a.out or OUT, workers=a.workers,
                           log_every=20)


if __name__ == "__main__":
    print("wall", main())
