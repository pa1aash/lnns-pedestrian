"""Per-run cache for the CroMa figure (figures/fig8_croma.py): completion, flow, fluctuation and the longest gap with
the terminal gap of runs that did not complete treated as right-censored (a lower bound to the 600 s horizon).

Inputs: data/E10/e10_croma.jsonl (per-run estimator of experiments/pilot/w28_croma.py) and the trajectories
data/E10/raw/<cell>_seed<k>.npz (columns t, id, x, ...); RAW_ROOT overrides the repository root that holds data/E10/raw
(the trajectories are not in every checkout). Humans: figures/data/fig8.json (experiments/E10/analyze.py); every human run
empties the waiting area.
Output: figures/data/fig8_runs.json.

Longest gap of a run that did not complete: its terminal gap from the last passage is still open, so the longest gap is
right-censored and stored as a lower bound with censored = true. Runs capped at 600 s end there. A run stopped as a
deadlock (every active |v| < 0.01 m/s for 10 s, experiments/E10/e10_croma.py) is a rest state of a deterministic model
(only SFM cells are stopped this way), which does not move again, so its terminal gap is taken to the 600 s horizon too;
the gap at the stop time (t_end - last passage) is kept as terminal_gap_at_stop. Passage time of an agent: its first sample with x >= 10 m (the entrance plane), as in
experiments/E10/analyze.py final_stall().
"""
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW_ROOT = Path(os.environ.get("RAW_ROOT", ROOT))
T_MAX = 600.0
CELLS = ["C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]


def last_passage(npz):
    D = np.load(npz)["data"]
    ids = D[:, 1].astype(int)
    last = None
    for i in np.unique(ids):
        t, x = D[ids == i, 0], D[ids == i, 2]
        c = np.where(x - 10.0 >= 0)[0]
        if len(c) and c[0] > 0:
            last = t[c[0]] if last is None else max(last, t[c[0]])
    return last


def fl(e):
    f = e.get("fluct") or {}
    if f.get("sd_x") is None:
        return None
    return math.sqrt((f["sd_x"] ** 2 + f["sd_y"] ** 2) / 2)


def main():
    R = [json.loads(l) for l in open(ROOT / "data" / "E10" / "e10_croma.jsonl") if l.strip()]
    fig8 = json.load(open(HERE / "data" / "fig8.json"))
    out = {"source": "figures/build_fig8_cache.py", "t_max_s": T_MAX, "cells": {}}
    h = fig8["runs"]["humans"]
    out["cells"]["humans"] = [{"complete": True, "deadlock": False, "flow": f, "gap": g, "gap_censored": False, "fluct": u}
                              for f, g, u in zip(h["flow"], h["longest_gap"], h["fluct"])]
    for c in CELLS:
        rows = []
        for r in sorted((r for r in R if r["cell"] == c), key=lambda r: r["seed"]):
            e = r["estimator"]
            gap, cens, term = e.get("max_gap_s"), False, None
            if not r["complete"]:
                last = last_passage(RAW_ROOT / r["npz"])
                term = None if last is None else float(r["t_end"] - last)
                assert r["deadlock"] or abs(r["t_end"] - T_MAX) < 0.1, r["job_id"]
                assert not (r["deadlock"] and r["sigma"] > 0), r["job_id"]
                horizon = None if last is None else float(T_MAX - last)
                gap = max(gap or 0.0, horizon or 0.0)
                cens = True
            rows.append({"seed": r["seed"], "run": r["run"], "complete": r["complete"], "deadlock": r["deadlock"],
                         "t_end": r["t_end"], "flow": e.get("flow_per_s"), "gap": gap, "gap_censored": cens,
                         "terminal_gap_at_stop": term, "fluct": fl(e)})
        out["cells"][c] = rows
        print(c, "n", len(rows), "complete", sum(x["complete"] for x in rows),
              "censored", sum(x["gap_censored"] for x in rows),
              "gap range", round(min(x["gap"] for x in rows), 1), round(max(x["gap"] for x in rows), 1))
    json.dump(out, open(HERE / "data" / "fig8_runs.json", "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
