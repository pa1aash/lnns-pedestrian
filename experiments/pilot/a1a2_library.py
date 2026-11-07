"""W2b A1/A2. C1, corrected-forward numerics (numerics=fixed, spawn=rejection), w=0.8,
100 agents, 600 s cap, recorder = wave2/scripts/w21_library.run (stops at deadlock:
all |v|<0.01 m/s for 10 s, no exit; snapshot saved to wave2b/data/library).
A2: B_w_edge=0.04 (jamb segments only, zone 0.5-1.0 m), seeds 42-66.
A1: B_w=0.04 (all walls), seeds 67.. in batches of 40 until >=30 pair snapshots
    (counting the 5 W2.5 pair snapshots, seeds 42-66) or 200 seeds used (42-241).
Outputs: wave2b/data/a2_edge_only.jsonl, wave2b/data/a1_library.jsonl"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2blib import *  # noqa
import w21_library
w21_library.LIB = LIB2B


def n_pairs(path):
    k = 0
    if os.path.exists(path):
        for r in load_jsonl(path):
            if r.get("deadlock") and r["n_remaining"] == 2:
                k += 1
    return k


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "A2":
        jobs = [{"job_id": f"edge0.04|seed{s}", "seed": s, "width": 0.8,
                 "flags": {**CF, "B_w_edge": 0.04}, "tag": "a2_edge0.04"} for s in range(42, 67)]
        print("wall", run_jobs(jobs, w21_library.run, os.path.join(DATA2B, "a2_edge_only.jsonl"), workers=4, log_every=5))
    else:
        out = os.path.join(DATA2B, "a1_library.jsonl")
        prior = 5   # W2.5 B0.04 pair snapshots, seeds 42-66 (wave2/data/library/w25_B0.04_*)
        s0 = 67
        while s0 < 242:
            if prior + n_pairs(out) >= 30:
                break
            s1 = min(s0 + 40, 242)
            jobs = [{"job_id": f"B0.04|seed{s}", "seed": s, "width": 0.8,
                     "flags": {**CF, "B_w": 0.04}, "tag": "a1_B0.04"} for s in range(s0, s1)]
            print("batch", s0, s1, "wall", run_jobs(jobs, w21_library.run, out, workers=4, log_every=10), flush=True)
            s0 = s1
        print("pairs", prior + n_pairs(out), "last seed", s0 - 1)
