"""Tier 1-2 run queue (session C5): task 1 (pair standoffs to rest), task 8 (throttled drive part), task 7 (whole-run
replays). Priority order: task 1, task 8, task 7 (drive, tauprime, rvo2, sfm). Resumable.
  task 1  the E7b deterministic quench jobs (experiments/E7b/e7b_quench.jobs, run function unchanged) of the arms
          C3_pub, C3_rvo2, constraint_only_pub, constraint_only_rvo2, with t_q = 600 s instead of 120 s; the stopping
          rule is E7b's own (every active |v| < 1e-3 m/s for 10 s, or both members out). Arms whose 120 s runs all
          ended freed or at rest by that rule (drive_only, the bias arms and the +-b* runs) are final at 120 s and
          are not rerun. -> data/revision7/T1/t1_pair_rest.jsonl
  task 8  arm drive_veff on seeds 242-427, unperturbed -> data/revision7/T8/t8_whole.jsonl
  task 7  arms drive, tauprime, rvo2, sfm on seeds 242-427 with perturb seed 900 (1e-9 m at spawn)
          -> data/revision7/T7/t7_replay.jsonl
Usage: queue_q12.py [--workers W] [--only T1,T8,T7]"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402

PAIR_ARMS = ("C3_rvo2", "C3_pub", "constraint_only_rvo2", "constraint_only_pub")
T1_OUT = os.path.join(L.data_dir("T1"), "t1_pair_rest.jsonl")
T8_OUT = os.path.join(L.data_dir("T8"), "t8_whole.jsonl")
T7_OUT = os.path.join(L.data_dir("T7"), "t7_replay.jsonl")


def t1_jobs():
    sys.path.insert(0, os.path.join(L.ROOT, "experiments", "E7b"))
    import e7b_quench
    J = [dict(j, t_q=600.0) for j in e7b_quench.jobs() if j["arm"] in PAIR_ARMS and j["deterministic"]]
    J.sort(key=lambda j: PAIR_ARMS.index(j["arm"]))
    return J


def t8_jobs():
    return [L.whole_job("drive_veff", s) for s in L.SEEDS_WHOLE]


def t7_jobs():
    return [L.whole_job(a, s, perturb=900) for a in ("drive", "tauprime", "rvo2", "sfm") for s in L.SEEDS_WHOLE]


if __name__ == "__main__":
    w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 3
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else ["T1", "T8", "T7"]
    T = {"T1": (T1_OUT, "pair", t1_jobs), "T8": (T8_OUT, "whole", t8_jobs), "T7": (T7_OUT, "whole", t7_jobs)}
    print("wall", L.run_queue([(T[k][0], T[k][1], T[k][2]()) for k in only], w))
