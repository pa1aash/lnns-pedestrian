"""T1 runs: whole-run attribution of force-coupled ORCA's completions to its drive part.

Room bottleneck w = 0.8 m, 100 agents, dt = 0.01 s, 600 s cap, stop at deadlock (every active |v| < 0.01 m/s for
10 s, no exit) or completion; recorder experiments/lib/runlib.whole_run (as E6). Corrected-forward flags (CF),
default walls, run seeds 242-427 = the spawns of E6a (force-coupled ORCA, RVO2, data/E6/e6a.jsonl).
  drive     config C3 with w2_orca_split = drive_only: the ORCA term is replaced at every step by its drive part
            w_o m (v0 e - v) / tau_orca (Eq. orca with v_orca -> v0 e; at rest m v0 e / tau_orca), under the same
            density gate w_o = chi_i; no linear program is solved, so the solver flag is irrelevant.
  tauprime  config C1 with sfm_tau_prime = on: plain SFM with tau' = tau tau_orca / (tau + tau_orca) and target
            speed tau' (v_eff / tau + v0 / tau_orca) (the identity of Eq. 7; no gate).
  sfm       config C1 (plain SFM), seeds 342-427 (seeds 242-341 exist in data/velorca/whole.jsonl, variant sfm,
            same recorder and flags) and seeds 242-246 again as a reproduction check of those records.
Output: data/revision4/T1/t1_whole.jsonl (job_id "<variant>|seed<seed>"), resumable.
Usage: T1_whole.py [--workers W]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import CF, run_jobs  # noqa: E402
from runlib import whole_run  # noqa: E402

OUT = os.path.join(rev4lib.data_dir("T1"), "t1_whole.jsonl")
VARIANTS = {"drive": ("C3", {**CF, "w2_orca_split": "drive_only"}, range(242, 428)),
            "tauprime": ("C1", {**CF, "sfm_tau_prime": "on"}, range(242, 428)),
            "sfm": ("C1", dict(CF), list(range(342, 428)) + list(range(242, 247)))}


def jobs():
    return [{"job_id": f"{v}|seed{s}", "variant": v, "seed": s, "width": 0.8, "config": cfg, "flags": dict(fl),
             "sigma": 0.0, "t_max": 600.0} for v, (cfg, fl, seeds) in VARIANTS.items() for s in seeds]


if __name__ == "__main__":
    print("wall", run_jobs(jobs(), whole_run, OUT, workers=rev4lib.workers(sys.argv), log_every=10))
