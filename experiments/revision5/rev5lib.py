"""Shared helpers for the revision-5 evidence (session C4, experiments/revision5/).

Reuses experiments/revision4/rev4lib.py (paths, statistics, run_jobs; w2lib sets cwd to code/) and adds:
  out_json(name, obj)   write data/derived/rev5_<name>.json (registry source of notes/C4_items/*.yaml)
  data_dir(name)        data/revision5/<name>/ for raw JSONL of new runs
  WORKERS               default worker count: all CPU cores but two
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
for d in ("revision4", "revision", "BAR", "lib"):
    p = os.path.join(EXP, d)
    if p not in sys.path:
        sys.path.insert(0, p)
import rev4lib  # noqa: E402
from rev4lib import (CF, DATA, DERIVED, ROOT, holm, load_runs, mcnemar_exact, np, pdisp, run_jobs, sig,  # noqa: E402,F401
                     stats, wilson)

WORKERS = max(1, (os.cpu_count() or 4) - 2)


def data_dir(name):
    d = os.path.join(DATA, "revision5", name)
    os.makedirs(d, exist_ok=True)
    return d


def out_json(name, obj):
    path = os.path.join(DERIVED, f"rev5_{name}.json")
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    return path


def workers(argv):
    return int(argv[argv.index("--workers") + 1]) if "--workers" in argv else WORKERS
