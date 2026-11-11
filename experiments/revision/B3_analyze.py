"""B3 analysis: Arrhenius slope ratio over beta = 1.5-7 in the alone condition.

Inputs: data/E4/e4_escape.jsonl (alone, beta 1.5, 2.5, 3.5; censored 300/300/900 s) and
data/revision/B3/b3.jsonl (alone, beta 5, 6, 7; censoring per experiments/revision/B3_highbeta.py) for the three
B3 snapshots. Per (snapshot, beta): censored-exponential rate (experiments/E3/survival.exp_rate), events,
Weibull shape. Per snapshot: the E4 Arrhenius fit (weighted least squares of ln lambda on 1/k_B T_eff, weights =
events; ratio = -slope / dU_alone; 95% interval from 2000 parametric Poisson resamples of the event counts,
PCG64(12345)) over (i) beta 1.5-3.5 (E4), (ii) 5-7 (new), (iii) 1.5-7 (all six). Prediction: ratio 1.
Also the local slope ratio between consecutive levels. Output: data/derived/rev_B3.json.
"""
import json
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import DATA, np  # noqa: E402
from survival import exp_rate, weibull_pool  # noqa: E402

N_BOOT = 2000


def wls(x, y, w):
    W = w.sum()
    xm, ym = (w * x).sum() / W, (w * y).sum() / W
    s = (w * (x - xm) * (y - ym)).sum() / (w * (x - xm) ** 2).sum()
    return s, ym - s * xm


def fit(cells, dU, rng):
    d = np.array([c["events"] for c in cells], float)
    T = np.array([c["exposure_s"] for c in cells])
    x = 1.0 / np.array([c["kT_eff"] for c in cells])
    if (d < 3).any():
        return None
    sl, a = wls(x, np.log(d / T), d)
    bs = []
    for _ in range(N_BOOT):
        db = rng.poisson(d)
        if (db > 0).all():
            bs.append(-wls(x, np.log(db / T), db)[0] / dU)
    return {"ratio": -sl / dU, "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            "intercept": a, "levels": [c["beta"] for c in cells]}


def main():
    new = revlib.load_runs(os.path.join(DATA, "revision", "B3", "b3.jsonl"))
    tags = sorted({r["tag"] for r in new})
    old = [r for r in revlib.load_runs(os.path.join(DATA, "E4", "e4_escape.jsonl"))
           if r["cond"] == "alone" and r["snap"][:-4] in tags]
    by = defaultdict(list)
    for r in old:
        by[(r["snap"][:-4], r["beta_ref"])].append(r)
    for r in new:
        by[(r["tag"], r["beta_ref"])].append(r)
    rng = np.random.default_rng(12345)
    out = {"doc": __doc__, "snapshots": {}}
    for tag in tags:
        betas = sorted(b for (t, b) in by if t == tag)
        cells = []
        for b in betas:
            R = by[(tag, b)]
            c = exp_rate([r["t_run"] for r in R], [r["censored"] for r in R])
            c.update({"beta": b, "kT_eff": R[0]["kT_eff"], "t_cens": R[0]["t_cens"],
                      "weibull": weibull_pool([([r["t_run"] for r in R], [r["censored"] for r in R])])})
            cells.append(c)
        dU = by[(tag, betas[0])][0]["dU_cond"]
        lo = [c for c in cells if c["beta"] <= 3.5]
        hi = [c for c in cells if c["beta"] >= 5]
        local = []
        for c1, c2 in zip(cells[:-1], cells[1:]):
            if c1["events"] and c2["events"]:
                local.append({"betas": [c1["beta"], c2["beta"]],
                              "ratio": -(math.log(c2["lam"]) - math.log(c1["lam"])) / (c2["beta"] - c1["beta"])})
        out["snapshots"][tag] = {"dU_alone_J": dU, "cells": cells, "fit_1p5_3p5": fit(lo, dU, rng),
                                 "fit_5_7": fit(hi, dU, rng), "fit_1p5_7": fit(cells, dU, rng), "local": local,
                                 "events_new": {f"{c['beta']:g}": c["events"] for c in hi},
                                 "censored_new": {f"{c['beta']:g}": c["n"] - c["events"] for c in hi}}
    S = out["snapshots"]
    out["summary"] = {
        "n_snapshots": len(S),
        "ratio_1p5_7": {t: S[t]["fit_1p5_7"]["ratio"] if S[t]["fit_1p5_7"] else None for t in S},
        "ratio_5_7": {t: S[t]["fit_5_7"]["ratio"] if S[t]["fit_5_7"] else None for t in S},
        "ratio_1p5_3p5": {t: S[t]["fit_1p5_3p5"]["ratio"] if S[t]["fit_1p5_3p5"] else None for t in S},
        "covers_1_1p5_7": sum(1 for t in S if S[t]["fit_1p5_7"] and S[t]["fit_1p5_7"]["ci95"][0] <= 1 <= S[t]["fit_1p5_7"]["ci95"][1]),
        "min_events_new": min(c["events"] for t in S for c in S[t]["cells"] if c["beta"] >= 5),
        "censored_new_total": sum(c["n"] - c["events"] for t in S for c in S[t]["cells"] if c["beta"] >= 5),
        "runs_new": len(new), "cpu_h_new": sum(r["wall_s"] for r in new) / 3600.0,
        "sim_h_new": sum(r["t_run"] for r in new) / 3600.0}
    revlib.out_json("B3", out)
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
