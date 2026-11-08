"""The E7b pair library: the qualifying snapshots of E7b_lib (experiments/E7b/e7b_lib.py, rule there),
in seed order. Each entry: tag "E7b_B0.04_seed<N>", absolute snapshot path, seed."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
sys.path.insert(0, HERE)
from e1lib import ROOT  # noqa: E402
import e7b_lib  # noqa: E402


def pairs():
    R, q = e7b_lib.state()
    by = {r["seed"]: r for r in R}
    out = []
    for s in q:
        rel = by[s]["snapshot"]
        out.append({"tag": os.path.basename(rel)[:-4], "snap": os.path.join(ROOT, rel), "seed": s})
    return out
