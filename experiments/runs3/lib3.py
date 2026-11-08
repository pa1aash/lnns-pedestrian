"""Shared set-up for the queue-3 runs (experiments/runs3/; queue file experiments/queue3.yaml).

Puts experiments/lib and the experiment folders on sys.path (w2lib changes cwd to code/), and gives
each run its output folder data/<N>/. Every run script takes the qargs options (--out, --limit,
--every, --scale, --workers) for smoke tests; the queue passes none.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
for d in ("lib", "E2", "E4", "E7b", "arch"):
    p = os.path.join(EXP, d)
    if p not in sys.path:
        sys.path.insert(0, p)
from e1lib import CF, DATA, DERIVED, ROOT, load_runs, run_jobs  # noqa: E402,F401
import qargs  # noqa: E402,F401


def out_dir(name):
    d = os.path.join(DATA, name)
    os.makedirs(d, exist_ok=True)
    return d
