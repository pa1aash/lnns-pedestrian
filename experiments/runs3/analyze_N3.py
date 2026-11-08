"""Analysis of run-N3 (E4 full condition at equal temperature across agents).

Inputs: data/N3/n3.jsonl; data/derived/E4_analysis.json (E4 full, blocker-only temperature) for comparison.
Output: data/derived/N3_analysis.json.
Definitions as experiments/E4/analyze.py: lambda_hat per (snapshot, level), censored exponential, exact
Poisson 95% interval (experiments/E3/survival.exp_rate); Arrhenius weighted least squares of ln lambda_hat
on 1 / k_B T_eff over the three levels (weights = events), ratio r = -slope / dU_full, 95% interval from
2000 parametric resamples (Poisson, PCG64(12345)); fitted where every level has >= 3 events; prefactor nu_hat
with the slope held at -dU_full; Weibull shape shared over the (snapshot, level) groups with a scale per group
(experiments/E3/survival.weibull_pool). Paired with E4: per snapshot, r(N3) - r(E4); the sign of the
difference over snapshots (sign test).
"""
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "E3"))
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402
from survival import exp_rate, weibull_pool  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "N3_analysis.json")
LEVELS = (1.5, 2.5, 3.5)
N_BOOT, MIN_EV = 2000, 3


def lk(L):
    return f"b{L:g}".replace(".", "p")


def wls(x, y, w):
    W = w.sum()
    xm, ym = (w * x).sum() / W, (w * y).sum() / W
    s = (w * (x - xm) * (y - ym)).sum() / (w * (x - xm) ** 2).sum()
    return s, ym - s * xm


def main():
    R = [json.loads(l) for l in open(os.path.join(DATA, "N3", "n3.jsonl")) if l.strip()]
    E4 = json.load(open(os.path.join(DATA, "derived", "E4_analysis.json")))
    by = defaultdict(list)
    for r in R:
        by[(r["snap"][:-4], r["beta_ref"])].append(r)
    tags = sorted({k[0] for k in by})
    rng = np.random.default_rng(12345)
    snaps, groups, ratios, diffs = {}, [], [], []
    for tag in tags:
        cells = []
        s = {"levels": {}}
        for L in LEVELS:
            rows = by[(tag, L)]
            cell = exp_rate([r["t_run"] for r in rows], [r["censored"] for r in rows])
            cell.update({"sigma_blocker": rows[0]["sigma"], "kT_eff": rows[0]["kT_eff"], "t_cens": rows[0]["t_cens"],
                         "other_exit_first": int(sum(r["other_exit_first"] for r in rows))})
            s["levels"][lk(L)] = cell
            cells.append(cell)
            groups.append(([r["t_run"] for r in rows], [r["censored"] for r in rows]))
        dU = by[(tag, LEVELS[0])][0]["dU_cond"]
        s["dU"] = dU
        d = np.array([c["events"] for c in cells], float)
        T = np.array([c["exposure_s"] for c in cells])
        x = 1.0 / np.array([c["kT_eff"] for c in cells])
        s["arrhenius"] = None
        if (d >= MIN_EV).all():
            y = np.log(d / T)
            sl, a = wls(x, y, d)
            bs = []
            for _ in range(N_BOOT):
                db = rng.poisson(d)
                if (db > 0).all():
                    bs.append(-wls(x, np.log(db / T), db)[0] / dU)
            nu = math.exp(float((d * (y + dU * x)).sum() / d.sum()))
            s["arrhenius"] = {"slope": sl, "intercept": a, "ratio": -sl / dU,
                              "ratio_ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                              "nu_hat": nu}
            ratios.append(-sl / dU)
            e4 = E4["snapshots"].get(tag, {}).get("conds", {}).get("full", {}).get("arrhenius")
            if e4:
                s["E4_ratio"] = e4["ratio"]
                diffs.append(-sl / dU - e4["ratio"])
        snaps[tag] = s
    try:
        wb = weibull_pool(groups)
    except Exception as e:  # noqa: BLE001
        wb = {"error": str(e)}
    cover = sum(1 for t in tags if snaps[t]["arrhenius"] and
                snaps[t]["arrhenius"]["ratio_ci95"][0] <= 1 <= snaps[t]["arrhenius"]["ratio_ci95"][1])
    pos = sum(1 for x in diffs if x > 0)
    o = {"script": "experiments/runs3/analyze_N3.py", "doc": __doc__, "n_snapshots": len(tags), "n_runs": len(R),
         "events": int(sum(not r["censored"] for r in R)), "snapshots": snaps, "weibull": wb,
         "n_arrhenius_fits": len(ratios), "ratio_median": float(np.median(ratios)) if ratios else None,
         "ratio_min": float(min(ratios)) if ratios else None, "ratio_max": float(max(ratios)) if ratios else None,
         "ratio_ci_covers_1": int(cover),
         "ratio_above_1": int(sum(r > 1 for r in ratios)),
         "paired_vs_E4": {"n": len(diffs), "median_diff": float(np.median(diffs)) if diffs else None,
                          "n_N3_above_E4": pos,
                          "sign_test_p": float(stats.binomtest(pos, len(diffs)).pvalue) if diffs else None},
         "E4_full": {"ratio_median": E4["per_condition"]["full"]["ratio_median"],
                     "weibull_k": E4["per_condition"]["full"]["weibull"]["k"],
                     "n_fits": E4["per_condition"]["full"]["n_arrhenius_fits"],
                     "ratio_ci_covers_1": E4["per_condition"]["full"]["ratio_ci_covers_1"]},
         "ratio_sign_test_vs_1": {"above": int(sum(r > 1 for r in ratios)), "n": len(ratios),
                                  "p": float(stats.binomtest(int(sum(r > 1 for r in ratios)), len(ratios)).pvalue)
                                  if ratios else None}}
    json.dump(o, open(OUT, "w"), indent=1, default=float)
    return o


if __name__ == "__main__":
    o = main()
    print("fits", o["n_arrhenius_fits"], "ratio median", o["ratio_median"], "covers1", o["ratio_ci_covers_1"],
          "above1", o["ratio_above_1"], "weibull", o["weibull"].get("k"), o["weibull"].get("ci95"),
          "paired", o["paired_vs_E4"], "E4", o["E4_full"])
