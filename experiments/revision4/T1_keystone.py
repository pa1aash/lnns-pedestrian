"""T1 failure classes: the E6 keystone test (experiments/E6/keystone_e6.py run(), unchanged) on the rebuilt final state
of every T1 run that did not complete (variants drive, tauprime; and the new SFM runs, seeds 342-427).

Rebuild: the run's own spawn (same seed, CF flags), agents not in the residual deactivated, residual agents at their
saved final positions, velocities zero. Tests (C1 restart, sigma = 0, dt = 0.01 s, 120 s, stationary stop):
K0 all residual kept, K1 blocker alone, K2 blocker removed, K1b (when K1 held and K2 left agents) the K2-held agent
nearest the door alone. Classes as E6: lone_keystone (K1 held, K2 all exit), lone_keystone_second_trap (K1 held,
K2 some held), collective (K1 freed). Whether the run was at rest at 600 s comes from the run record (deadlock flag)
and is kept beside the class.
Output: data/revision4/T1/t1_keystone.jsonl (job_id "<variant>|seed<N>|<test>"), resumable.
Usage: T1_keystone.py [--workers W]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import load_runs, run_jobs  # noqa: E402
import keystone_e6 as K  # noqa: E402

IN = os.path.join(rev4lib.data_dir("T1"), "t1_whole.jsonl")
OUT = os.path.join(rev4lib.data_dir("T1"), "t1_keystone.jsonl")


def failures():
    R = [r for r in load_runs(IN) if not r["complete"]]
    return [r for r in R if r["variant"] in ("drive", "tauprime") or (r["variant"] == "sfm" and r["seed"] >= 342)]


def phase1(R):
    return [{"job_id": f"{r['variant']}|seed{r['seed']}|{t}", "variant": r["variant"], "seed": r["seed"], "test": t,
             "run": r} for r in R for t in ("K0", "K1", "K2")]


def load_res():
    return {x["job_id"]: x for x in load_runs(OUT)} if os.path.exists(OUT) else {}


def phase2(R, res):
    J = []
    for r in R:
        tag = f"{r['variant']}|seed{r['seed']}"
        k1, k2 = res.get(tag + "|K1"), res.get(tag + "|K2")
        if k1 and k2 and k1["held"] and k2["held"]:
            pos = {int(x["id"]): K.np.array(x["pos"]) for x in r["residual"]}
            tgt = min(k2["held"], key=lambda i: float(K.np.linalg.norm(pos[i] - K.DOOR)))
            J.append({"job_id": tag + "|K1b", "variant": r["variant"], "seed": r["seed"], "test": "K1b",
                      "target": int(tgt), "run": r})
    return J


if __name__ == "__main__":
    w = rev4lib.workers(sys.argv)
    R = failures()
    run_jobs(phase1(R), K.run, OUT, workers=w, log_every=50)
    run_jobs(phase2(R, load_res()), K.run, OUT, workers=w, log_every=50)
