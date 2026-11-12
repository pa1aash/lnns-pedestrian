"""A11 runs: whole-run completion of the two conference configurations without data under this model at w = 0.8 m.

Room bottleneck w = 0.8 m, 100 agents, 600 s cap, stop at deadlock (every active |v| < 0.01 m/s for 10 s, no
exit) or completion; recorder experiments/lib/runlib.whole_run (as E1, E6). Corrected-forward flags (CF).
  C2  SFM + TTC (config C2), seeds 42-141: the spawns of E1b (C1, CF), so C2 and C1 pair seed by seed.
  C4  full blend SFM + TTC + ORCA (RVO2) + crush (config C4; CF sets w2_crush = off, so the crush term is
      absent), seeds 242-341: the spawns of E6a (C3, RVO2, CF), so C4 and C3 pair seed by seed.
The published-flag C4 (legacy ORCA, crush on) is not run: its cost from E6p wall times is about 21 CPU-h per 100.
Output: data/revision2/A11/a11.jsonl (job_id "<C2|C4>|seed<seed>"), resumable. Analysis: A11_analyze.py.
Usage: A11_whole.py [qargs options]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import CF, run_jobs  # noqa: E402
import qargs  # noqa: E402
from runlib import whole_run  # noqa: E402

SEEDS = {"C2": range(42, 142), "C4": range(242, 342)}


def jobs():
    return [{"job_id": f"{v}|seed{s}", "variant": v, "seed": s, "width": 0.8, "config": v, "flags": dict(CF),
             "sigma": 0.0, "t_max": 600.0} for v in ("C2", "C4") for s in SEEDS[v]]


if __name__ == "__main__":
    a = qargs.parse()
    out = a.out or os.path.join(rev2lib.data_dir("A11"), "a11.jsonl")
    run_jobs(qargs.select(jobs(), a), whole_run, out, workers=a.workers, log_every=10)
