"""run-N2: E6b repeated with an independent noise stream (the noise-versus-noise reference for whole runs).

C1 + sigma* (data/derived/sigma_star.json, the value E6b used), corrected-forward flags (CF), room
bottleneck w = 0.8 m, 100 agents, the E6 seeds 242-427 (186), 600 s, stop at deadlock or completion
(experiments/lib/runlib.whole_run, unchanged). The spawn is drawn from the run seed exactly as in E6b;
the velocity-noise generator is then reseeded with 50000 + seed (PCG64), so the spawns are identical and
the noise is independent of E6b's. The simulator draws from this generator only for velocity noise.
Output: data/N2/n2.jsonl (job_id "N2|seed<seed>"), resumable.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3 import CF, DERIVED, out_dir, qargs, run_jobs  # noqa: E402
import numpy as np  # noqa: E402
import runlib  # noqa: E402
import w2lib  # noqa: E402

OUT = os.path.join(out_dir("N2"), "n2.jsonl")
SEEDS = range(242, 428)
NOISE_BASE = 50000


def _build_indep(config="C1", seed=42, width=0.8, noise=0.0, flags=None, **kw):
    sim = w2lib.build(config, seed=seed, width=width, noise=noise, flags=flags, **kw)
    sim._rng = np.random.Generator(np.random.PCG64(NOISE_BASE + seed))
    return sim


runlib.build = _build_indep   # whole_run calls runlib.build; forked workers inherit this


def jobs(sigma):
    return [{"job_id": f"N2|seed{s}", "variant": "N2", "seed": s, "noise_seed": NOISE_BASE + s, "width": 0.8,
             "flags": dict(CF), "sigma": sigma, "t_max": 600.0, "config": "C1"} for s in SEEDS]


def main(argv=None):
    a = qargs.parse(argv)
    rec = json.load(open(os.path.join(DERIVED, "sigma_star.json")))
    assert rec.get("status") == "ok", rec
    return run_jobs(qargs.select(jobs(rec["sigma_star"]), a), runlib.whole_run, a.out or OUT,
                    workers=a.workers, log_every=10)


if __name__ == "__main__":
    print("wall", main())
