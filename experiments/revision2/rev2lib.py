"""Shared helpers for the revision-3 evidence (session C2, experiments/revision2/).

Reuses experiments/revision/revlib.py (paths, statistics) and adds:
  out_json(name, obj)   write data/derived/rev2_<name>.json (registry source of paper/registry/revision2.yaml)
  data_dir(name)        data/revision2/<name>/ for raw JSONL of new runs
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "revision"))
import revlib  # noqa: E402
from revlib import (CF, DATA, DERIVED, ROOT, holm, load_runs, mcnemar_exact, np, pdisp, run_jobs, sig,  # noqa: E402,F401
                    stats, wilson)


def data_dir(name):
    d = os.path.join(DATA, "revision2", name)
    os.makedirs(d, exist_ok=True)
    return d


def out_json(name, obj):
    path = os.path.join(DERIVED, f"rev2_{name}.json")
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    return path
