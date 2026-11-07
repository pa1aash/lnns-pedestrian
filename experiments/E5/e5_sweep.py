"""E5: whole-run noise sweeps, room bottleneck w = 0.8 m, 100 agents, C1 + sigma, seeds 42-141,
600 s cap, stop at deadlock (every active |v| < 0.01 m/s for 10 s, no exit) or completion.
  E5a  published-reproduction (all flags default), sigma in {0.02, 0.03, 0.04, 0.05, 0.06, 0.07,
       0.10, 0.20} m/s; sigma = 0 reuses E1a seeds 42-141 (data/E1/E1_runs.jsonl).
  E5b  corrected-forward (CF), sigma in {0.03, 0.04, 0.05, 0.06, 0.07} m/s; sigma = 0 is E1b.
Noise: per-step Gaussian velocity noise (published scheme), seeded by the run seed.
Recorded: completion, exit times, residual state (recorder experiments/lib/runlib.whole_run).
Output: data/E5/e5a.jsonl, data/E5/e5b.jsonl (job_id "<variant>|s<sigma>|seed<seed>"), resumable.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, run_jobs  # noqa: E402
from runlib import whole_run  # noqa: E402

VARIANTS = {"E5a": ({}, (0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.10, 0.20)),
            "E5b": (CF, (0.03, 0.04, 0.05, 0.06, 0.07))}
SEEDS = range(42, 142)


def out_path(v):
    return os.path.join(DATA, "E5", f"{v.lower()}.jsonl")


def jobs(v):
    fl, sig = VARIANTS[v]
    # largest sigma first: shorter runs (completion) land early; order does not affect results
    return [{"job_id": f"{v}|s{s}|seed{seed}", "variant": v, "seed": seed, "width": 0.8, "flags": dict(fl),
             "sigma": s, "t_max": 600.0, "config": "C1"} for seed in SEEDS for s in sig]


def main(v, out=None, J=None, workers=4):
    out = out or out_path(v)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(jobs(v) if J is None else J, whole_run, out, workers=workers, log_every=25)


if __name__ == "__main__":
    print("wall", main(sys.argv[1]))
