"""E10 analysis: CroMa-geometry model cells against the five CroMa 0.8 m runs (paper Sect. 7, Fig. 8).

Inputs: data/E10/e10_croma.jsonl (experiments/E10/e10_croma.py; per run the estimator of
experiments/pilot/w28_croma.py, unchanged) and the trajectories in data/E10/raw; the human runs in data/ext/croma,
put through the same estimator (w28_croma.croma, unchanged).

Per cell and for humans, over runs:
  completion       k/n with a Wilson 95% interval (humans: every run empties the waiting area);
  flow             passages per second through the entrance plane (first to last passage);
  gaps > 2 s       number of time gaps between successive passages longer than 2 s;
  longest gap      longest such gap (s);
  fluctuation      waiting-zone velocity fluctuation: RMS over the two components of the per-component SD of
                   the residual velocity (SG velocity minus the mean of neighbours within 0.74 m, zone 0.3-2.5 m
                   before the entrance, local-mean speed < 0.3 m/s); sd_x and sd_y are kept too;
  wall leaks       agents whose centre left the walkable region (sum, and runs with a leak).
Means with Student-t 95% intervals over runs (25 per cell, 5 human runs). Like-for-like by run type: corridor
L = 2.0 m (4D030, 4D040; 10 model runs per cell) and L = 0.21 m (4D110, 4D120, 4D130; 15 per cell).
Model/human ratio of mean flow and of mean longest gap, with 95% intervals from 10 000 independent bootstrap
resamples of model and human runs. For runs that end in a deadlock the estimator counts the passages before it;
the time from the last passage to the end of the run (final stall) is recorded separately.
Output: data/derived/E10_analysis.json.
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
_spec = importlib.util.spec_from_file_location("w28_croma", os.path.join(ROOT, "experiments", "pilot", "w28_croma.py"))
w28 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w28)

IN = os.path.join(DATA, "E10", "e10_croma.jsonl")
CROMA = os.path.join(DATA, "ext", "croma")
OUT = os.path.join(DATA, "derived", "E10_analysis.json")
FIG = os.path.join(ROOT, "figures", "data", "fig8.json")
CELLS = ["C1_pub", "C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]
RUNS_L = {"4D030": 2.0, "4D040": 2.0, "4D110": 0.21, "4D120": 0.21, "4D130": 0.21}
RNG = np.random.default_rng(2026)
B = 10000


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return [None, None]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def tci(x):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    n = len(x)
    if n == 0:
        return {"n": 0, "mean": None, "ci95": [None, None]}
    m = float(x.mean())
    if n == 1:
        return {"n": 1, "mean": m, "ci95": [None, None], "median": m}
    h = float(stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / math.sqrt(n))
    return {"n": n, "mean": m, "ci95": [m - h, m + h], "median": float(np.median(x)),
            "min": float(x.min()), "max": float(x.max())}


def fl(e):
    f = e.get("fluct")
    if not f:
        return None
    return math.sqrt((f["sd_x"] ** 2 + f["sd_y"] ** 2) / 2)


def metrics(rows):
    """rows: dicts with flow_per_s, n_gaps_gt_2s, max_gap_s, fluct (estimator output)."""
    return {"flow": tci([r.get("flow_per_s") for r in rows]),
            "gaps_gt_2s": tci([r.get("n_gaps_gt_2s") for r in rows]),
            "longest_gap": tci([r.get("max_gap_s") for r in rows]),
            "fluct": tci([fl(r) for r in rows]),
            "fluct_sd_x": tci([(r.get("fluct") or {}).get("sd_x") for r in rows]),
            "fluct_sd_y": tci([(r.get("fluct") or {}).get("sd_y") for r in rows]),
            "n_pass": tci([r.get("n_pass") for r in rows])}


def ratio_ci(model, human):
    model = np.asarray([v for v in model if v is not None], float)
    human = np.asarray([v for v in human if v is not None], float)
    if len(model) == 0 or len(human) == 0:
        return None
    r0 = model.mean() / human.mean()
    bs = [RNG.choice(model, len(model)).mean() / RNG.choice(human, len(human)).mean() for _ in range(B)]
    return {"ratio": float(r0), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}


def final_stall(r):
    """Time from the last passage through the entrance plane to the end of the run (deadlocked runs)."""
    p = os.path.join(ROOT, r["npz"])
    if not os.path.exists(p):
        return None
    D = np.load(p)["data"]
    ids = D[:, 1].astype(int)
    last = None
    for i in np.unique(ids):
        t, x = D[ids == i, 0], D[ids == i, 2]
        c = np.where(x - 10.0 >= 0)[0]
        if len(c) and c[0] > 0:
            last = t[c[0]] if last is None else max(last, t[c[0]])
    return None if last is None else float(r["t_end"] - last)


def main():
    R = [json.loads(l) for l in open(IN) if l.strip()]
    H = [w28.croma(os.path.join(CROMA, f)) for f in sorted(os.listdir(CROMA)) if "_w080_" in f]
    for h in H:
        h["run"] = h["file"][:5]
    o = {"script": "experiments/E10/analyze.py", "estimator": "experiments/pilot/w28_croma.py (unchanged)",
         "ci": "Student-t 95% over runs; Wilson for completion; bootstrap for ratios", "humans": {}, "cells": {},
         "by_L": {}}
    hm = [h for h in H]
    o["humans"] = {"n_runs": len(hm), "runs": [{k: h[k] for k in ("file", "n_ids", "n_pass", "flow_per_s",
                                                                    "n_gaps_gt_2s", "max_gap_s", "median_gap_s")}
                                               | {"fluct": fl(h), "L": RUNS_L[h["run"]]} for h in hm],
                   **metrics(hm)}
    o["humans"]["flow_range"] = [min(h["flow_per_s"] for h in hm), max(h["flow_per_s"] for h in hm)]
    o["humans"]["longest_gap_max"] = max(h["max_gap_s"] for h in hm)
    for c in CELLS:
        X = [r for r in R if r["cell"] == c]
        if not X:
            continue
        E = [dict(r["estimator"], run=r["run"]) for r in X]
        k = sum(r["complete"] for r in X)
        dl = [r for r in X if r["deadlock"]]
        stalls = [final_stall(r) for r in dl]
        d = {"n": len(X), "complete": k, "completion_wilson95": wilson(k, len(X)), "deadlock": len(dl),
             "capped": sum((not r["complete"]) and (not r["deadlock"]) for r in X),
             "remaining_median_incomplete": float(np.median([r["n_remaining"] for r in X if not r["complete"]]))
             if k < len(X) else None,
             "t_end_median": float(np.median([r["t_end"] for r in X])),
             "evac_time_median_complete": float(np.median([r["t_end"] for r in X if r["complete"]])) if k else None,
             "wall_leaks_total": sum(r["n_leaked"] for r in X), "runs_with_leak": sum(r["n_leaked"] > 0 for r in X),
             "runs_with_leak_wilson95": wilson(sum(r["n_leaked"] > 0 for r in X), len(X)),
             "final_stall_deadlocked": tci(stalls),
             **metrics(E)}
        d["flow_ratio_to_human"] = ratio_ci([e.get("flow_per_s") for e in E], [h["flow_per_s"] for h in hm])
        d["longest_gap_ratio_to_human"] = ratio_ci([e.get("max_gap_s") for e in E], [h["max_gap_s"] for h in hm])
        d["fluct_ratio_to_human"] = ratio_ci([fl(e) for e in E], [fl(h) for h in hm])
        o["cells"][c] = d
    for L in (2.0, 0.21):
        hL = [h for h in hm if RUNS_L[h["run"]] == L]
        b = {"humans": {"n_runs": len(hL), **metrics(hL)}}
        for c in CELLS:
            X = [r for r in R if r["cell"] == c and RUNS_L[r["run"]] == L]
            if not X:
                continue
            E = [r["estimator"] for r in X]
            k = sum(r["complete"] for r in X)
            b[c] = {"n": len(X), "complete": k, "completion_wilson95": wilson(k, len(X)), **metrics(E),
                    "flow_ratio_to_human": ratio_ci([e.get("flow_per_s") for e in E], [h["flow_per_s"] for h in hL])}
        o["by_L"][{2.0: "L2p0", 0.21: "L0p21"}[L]] = b
    o["n_runs_total"] = len(R)
    fig = {"order": ["humans"] + [c for c in CELLS if c in o["cells"]], "metrics": ["flow", "longest_gap", "fluct"],
           "runs": {}, "summary": {}}
    per = {"humans": hm, **{c: [r["estimator"] for r in R if r["cell"] == c] for c in o["cells"]}}
    for c, rows in per.items():
        fig["runs"][c] = {"flow": [r.get("flow_per_s") for r in rows], "longest_gap": [r.get("max_gap_s") for r in rows],
                          "fluct": [fl(r) for r in rows]}
        src = o["humans"] if c == "humans" else o["cells"][c]
        fig["summary"][c] = {m: src[m] for m in fig["metrics"]}
    os.makedirs(os.path.dirname(FIG), exist_ok=True)
    with open(FIG, "w") as f:
        json.dump(fig, f, indent=1, default=float)
    with open(OUT, "w") as f:
        json.dump(o, f, indent=1, default=float)
    brief(o)


def brief(o):
    h = o["humans"]
    print("humans", h["n_runs"], "flow", h["flow"], "gap", h["longest_gap"], "fluct", h["fluct"], "gaps>2", h["gaps_gt_2s"])
    for c, d in o["cells"].items():
        print(c, d["n"], "complete", d["complete"], "dl", d["deadlock"], "capped", d["capped"], "leaks", d["wall_leaks_total"])
        for m in ("flow", "gaps_gt_2s", "longest_gap", "fluct"):
            x = d[m]
            print("   ", m, round(x["mean"], 3) if x["mean"] is not None else None,
                  [round(v, 3) if v is not None else None for v in x["ci95"]])
        print("    flow ratio", d["flow_ratio_to_human"], "gap ratio", d["longest_gap_ratio_to_human"],
              "final stall", d["final_stall_deadlocked"].get("median"))
    for L, b in o["by_L"].items():
        print("L", L, {c: (v.get("complete"), round(v["flow"]["mean"] or 0, 2)) for c, v in b.items() if c != "humans"},
              "humans flow", round(b["humans"]["flow"]["mean"], 2))


if __name__ == "__main__":
    main()
