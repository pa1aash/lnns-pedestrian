"""E7: wall-model validity cells, corrected-forward (CF), C1, 100 agents, seeds 42-141, 600 s cap,
stop at deadlock or completion, snapshot saved at deadlock (data/E7/library/E7_<cell>_seed<N>.pkl).
Cells: w in {0.7, 0.9, 1.0} m (0.8 m reuses E1b); at w = 0.8 m: B_w = 0.04 (all walls), B_w = 0.02
(all walls), B_w_edge = 0.04 (jambs only), edge = rounded (capsule jambs, r = 0.1 m), w2_goal = line,
line + rounded.
Output: data/E7/e7_cells.jsonl (job_id "<cell>|seed<seed>"), resumable.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, run_jobs  # noqa: E402
from runlib import whole_run  # noqa: E402

OUT = os.path.join(DATA, "E7", "e7_cells.jsonl")
LIBD = os.path.join(DATA, "E7", "library")
CELLS = {"w0.7": (0.7, {}), "w0.9": (0.9, {}), "w1.0": (1.0, {}),
         "B0.04": (0.8, {"B_w": 0.04}), "B0.02": (0.8, {"B_w": 0.02}), "Bedge0.04": (0.8, {"B_w_edge": 0.04}),
         "rounded": (0.8, {"edge": "rounded"}), "line": (0.8, {"w2_goal": "line"}),
         "line_rounded": (0.8, {"w2_goal": "line", "edge": "rounded"})}
SEEDS = range(42, 142)


def jobs():
    return [{"job_id": f"{c}|seed{s}", "cell": c, "seed": s, "width": w, "flags": {**CF, **fl}, "sigma": 0.0,
             "t_max": 600.0, "config": "C1", "lib": LIBD, "tag": f"E7_{c}"}
            for c, (w, fl) in CELLS.items() for s in SEEDS]


def main(out=OUT, J=None, workers=4):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(jobs() if J is None else J, whole_run, out, workers=workers, log_every=25)


if __name__ == "__main__":
    print("wall", main())
