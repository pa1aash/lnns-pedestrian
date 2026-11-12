"""B2: time step. SFM (C1), CF flags, default walls, dt = 0.005 s, widths {0.80, 0.88, 0.96} m, 100 agents,
seeds 42-141, 600 s, deadlock stop (StationaryDetector: time-based, 10 s hold, checked every 10 steps);
runner experiments/revision/B2_width.run, unchanged. dt = 0.01 s counterparts: E1b (0.80), B2 (0.88, 0.96).
Output data/revision2/B2/b2dt.jsonl.  Usage: B2_dt.py [qargs options]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import CF, run_jobs  # noqa: E402
import qargs  # noqa: E402
import B2_width  # noqa: E402

WIDTHS = (0.80, 0.88, 0.96)


def jobs():
    return [{"job_id": f"w{w:.2f}|seed{s}", "seed": s, "width": w, "flags": {**CF, "dt": 0.005}, "t_max": 600.0}
            for w in WIDTHS for s in range(42, 142)]


if __name__ == "__main__":
    a = qargs.parse()
    out = a.out or os.path.join(rev2lib.data_dir("B2"), "b2dt.jsonl")
    run_jobs(qargs.select(jobs(), a), B2_width.run, out, workers=a.workers, log_every=10)
