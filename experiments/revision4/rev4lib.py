"""Shared helpers for the revision-4 evidence (session C3, experiments/revision4/).

Reuses experiments/revision/revlib.py (paths, statistics; w2lib sets cwd to code/) and adds:
  out_json(name, obj)   write data/derived/rev4_<name>.json (registry source of notes/C3_items/*.yaml)
  data_dir(name)        data/revision4/<name>/ for raw JSONL of new runs
  WORKERS               default worker count: all CPU cores but two
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "revision"))
import revlib  # noqa: E402
from revlib import (CF, DATA, DERIVED, ROOT, holm, load_runs, mcnemar_exact, np, pdisp, run_jobs, sig,  # noqa: E402,F401
                    stats, wilson)

WORKERS = max(1, (os.cpu_count() or 4) - 2)


def data_dir(name):
    d = os.path.join(DATA, "revision4", name)
    os.makedirs(d, exist_ok=True)
    return d


def out_json(name, obj):
    path = os.path.join(DERIVED, f"rev4_{name}.json")
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    return path


def workers(argv):
    return int(argv[argv.index("--workers") + 1]) if "--workers" in argv else WORKERS
