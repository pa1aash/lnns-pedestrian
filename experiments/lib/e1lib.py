"""Execution helpers (ported from the pilot exec/scripts/e1lib.py): reuse w2lib.

E1 runs and snapshots live in data/E1; derived summaries in data/derived.
"""
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2lib import *  # noqa: F401,F403,E402
import w2lib  # noqa: F401,E402
from w2lib import DATA, REPO, ROOT  # noqa: F401,E402

EDATA = os.path.join(DATA, "E1")
ELIB = os.path.join(EDATA, "library")
DERIVED = os.path.join(DATA, "derived")
# Corrected-forward mode (Plan v1.1): numerics, spawn, RVO2 ORCA, crush off, convex corner rule.
CF = {"w2_numerics": "fixed", "spawn": "rejection", "w2_orca": "rvo2",
      "w2_crush": "off", "w2_wall_corner": "convex_union"}
PUB = {}
MODE_FLAGS = {"E1a": PUB, "E1b": CF}


def runs_path(name="E1_runs.jsonl", d=EDATA):
    """Path of a JSONL file, falling back to its gzipped copy (name.gz)."""
    p = os.path.join(d, name)
    return p if os.path.exists(p) or not os.path.exists(p + ".gz") else p + ".gz"


def load_runs(path):
    """load_jsonl that also reads .gz files."""
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [json.loads(l) for l in f if l.strip()]


def snap_path(rel):
    """Absolute path of a snapshot recorded in a runs file. Pilot-era records point at
    exec/data/library/<name>.pkl in the plan root; their copies live in data/E1/library."""
    name = os.path.basename(rel)
    return os.path.join(ELIB, name)
