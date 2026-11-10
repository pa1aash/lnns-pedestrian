"""B6 generation: the E7b pair-library runs repeated with the line goal (cell "line"); B5_gen.py reuses this
script for rounded jamb ends (cell "rounded").

Runs: experiments/E7b/e7b_lib.py's whole runs with the same seeds (the 320 seeds 242-561 that E7b_lib ran),
C1, w = 0.8 m, 100 agents, 600 s cap, stop at deadlock (every active |v| < 0.01 m/s for 10 s, no exit;
snapshot saved) or completion, runner experiments/lib/runlib.whole_run (unchanged). Flags CF union
{B_w: 0.04} (every wall) union the cell's flags:
  line      {w2_goal: line}
  rounded   {edge: rounded, edge_radius: 0.1}  (capsule jambs, r_c = 0.1 m; the stuck-alone margin of the
            run record uses the rounded-edge passability, runlib.get_pass)
Per run the analysis (B6_analyze.py / B5_analyze.py) counts: completion; deadlock; pair standoff by the E7b_lib
qualification rule (experiments/E7b/e7b_lib.qualifies: two residual agents at rest, front of jambs on opposite
sides, contact-free, each passes alone); pair-or-group standoff (collective) = deadlock whose blocker (residual
agent nearest the door centre (10, 5)) has negative stuck-alone margin; against the point-goal / sharp-edge
runs of data/E7b/e7b_lib.jsonl, seed-matched.
Output: data/revision/<B6|B5>/gen_<cell>.jsonl (job_id "seed<N>"), snapshots data/revision/<B6|B5>/library/,
resumable. Usage: B6_gen.py [qargs options]   (B5_gen.py for the rounded cell)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402
import qargs  # noqa: E402
from runlib import whole_run  # noqa: E402

E7B = os.path.join(revlib.DATA, "E7b", "e7b_lib.jsonl")
CELLS = {"line": ("B6", {"w2_goal": "line"}), "rounded": ("B5", {"edge": "rounded", "edge_radius": 0.1})}


def seeds():
    return sorted(r["seed"] for r in revlib.load_runs(E7B))


def jobs(cell):
    item, fl = CELLS[cell]
    lib = os.path.join(revlib.data_dir(item), "library")
    return [{"job_id": f"seed{s}", "seed": s, "cell": cell, "width": 0.8, "flags": {**revlib.CF, "B_w": 0.04, **fl},
             "sigma": 0.0, "t_max": 600.0, "config": "C1", "lib": lib, "tag": f"{item}_{cell}"} for s in seeds()]


def out_path(cell):
    return os.path.join(revlib.data_dir(CELLS[cell][0]), f"gen_{cell}.jsonl")


def main(cell="line", argv=None):
    a = qargs.parse(argv)
    return revlib.run_jobs(qargs.select(jobs(cell), a), whole_run, a.out or out_path(cell), workers=a.workers,
                           log_every=10)


if __name__ == "__main__":
    print("wall", main("line"))
