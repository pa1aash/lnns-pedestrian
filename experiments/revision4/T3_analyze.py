"""T3 analysis: the time-step probe at the matched noise sigma = 0.07 m/s (experiments/revision4/T3_dt_matched.py).

Estimators are E3's (experiments/E3/analyze.py, survival.exp_rate): per (snapshot, arm, dt) the censored-exponential
escape rate lambda = events / exposure over 20 restarts; per snapshot ell = ln lambda(0.005) / lambda(0.02) (Eq. 11)
with delta-method sd sqrt(1/d_0.005 + 1/d_0.02); a snapshot with no escape at 0.005 or 0.02 s has no ell and is
counted. Pooled ell = mean over snapshots, 95% interval from 2000 bootstrap resamples of snapshots (percentile,
PCG64(12345), as E3) and the Student-t interval beside; predicted ell_i = dU_i (1/k_B T_eff(0.02) - 1/k_B T_eff(0.005))
(exact discrete T_eff, dt-independent prefactor), pooled the same way; OLS slope of observed on predicted (per-step).
Realised beta = dU_i / k_B T_eff(0.07, dt, tau_b) per (snapshot, dt, arm): range, median and the share of snapshots
with beta < 1 (and < 1.5). Censoring per cell. Comparison: E3's per-step and dt-scaled pooled ell at sigma_i
(data/derived/E3_analysis.json).
Output: data/derived/rev4_T3.json.
"""
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import DATA, DERIVED, np, stats  # noqa: E402
from survival import Z95, boot_ci, exp_rate  # noqa: E402

IN = os.path.join(DATA, "revision4", "T3", "t3_dt.jsonl")
DTS = (0.005, 0.01, 0.02)
MODES = ("per_step", "dt_scaled")


def dkey(dt):
    return f"dt{dt:g}".replace(".", "p")


def main():
    R = [json.loads(l) for l in open(IN) if l.strip()]
    by = defaultdict(list)
    meta = {}
    for r in R:
        tag = r["job_id"].split("|")[0]
        by[(tag, r["mode"], r["dt"])].append(r)
        meta.setdefault(tag, {k: r[k] for k in ("blocker", "tau_b", "dU_i", "dU_rank", "sigma_E3",
                                                "ell_pred_per_step", "ell_pred_dt_scaled")})
    tags = sorted(meta, key=lambda t: meta[t]["dU_rank"])
    rng = np.random.default_rng(12345)
    out = {"script": "experiments/revision4/T3_analyze.py", "doc": __doc__, "sigma": 0.07, "n_snapshots": len(tags),
           "n_runs": len(R), "snapshots": {}, "arms": {}}
    for tag in tags:
        s = {**meta[tag], "cells": {}, "ell": {}}
        for mode in MODES:
            s["cells"][mode] = {}
            for dt in DTS:
                rows = by[(tag, mode, dt)]
                assert len(rows) == 20, (tag, mode, dt, len(rows))
                cell = exp_rate([r["t_run"] for r in rows], [r["censored"] for r in rows])
                cell.update(t_cens=rows[0]["t_cens"], beta=rows[0]["beta"], kT_eff=rows[0]["kT_eff"],
                            other_exit_first=int(sum(r["other_exit_first"] for r in rows)))
                s["cells"][mode][dkey(dt)] = cell
            a, b = s["cells"][mode]["dt0p005"], s["cells"][mode]["dt0p02"]
            if a["events"] and b["events"]:
                ell = math.log(a["lam"] / b["lam"])
                sd = math.sqrt(1 / a["events"] + 1 / b["events"])
                s["ell"][mode] = {"obs": ell, "ci95": [ell - Z95 * sd, ell + Z95 * sd], "sd": sd,
                                  "pred": meta[tag][f"ell_pred_{mode}"]}
            else:
                s["ell"][mode] = {"obs": None, "pred": meta[tag][f"ell_pred_{mode}"]}
        out["snapshots"][tag] = s
    for mode in MODES:
        S = out["snapshots"]
        T = [t for t in tags if S[t]["ell"][mode]["obs"] is not None]
        obs = np.array([S[t]["ell"][mode]["obs"] for t in T])
        pred = np.array([S[t]["ell"][mode]["pred"] for t in T])
        n = len(T)
        h = float(stats.t.ppf(0.975, n - 1) * obs.std(ddof=1) / math.sqrt(n))
        d = {"n_with_ell": n, "n_without_ell": len(tags) - n, "without_ell": [t for t in tags if t not in T],
             "ell_mean": float(obs.mean()), "ell_ci95_boot": boot_ci(lambda i: obs[i].mean(), n, rng, 2000),
             "ell_ci95_t": [float(obs.mean() - h), float(obs.mean() + h)], "ell_median": float(np.median(obs)),
             "pred_mean": float(pred.mean()), "pred_ci95_boot": boot_ci(lambda i: pred[i].mean(), n, rng, 2000),
             "snapshot_ci_covers_pred": int(sum(S[t]["ell"][mode]["ci95"][0] <= S[t]["ell"][mode]["pred"]
                                               <= S[t]["ell"][mode]["ci95"][1] for t in T)),
             "obs_minus_pred_mean": float((obs - pred).mean()),
             "obs_minus_pred_ci95_boot": boot_ci(lambda i: (obs[i] - pred[i]).mean(), n, rng, 2000)}
        if mode == "per_step" and np.ptp(pred) > 1e-9:
            A = np.vstack([pred, np.ones_like(pred)]).T
            coef = np.linalg.lstsq(A, obs, rcond=None)[0]
            d["slope_ols"] = {"slope": float(coef[0]), "intercept": float(coef[1]),
                              "slope_ci95_boot": boot_ci(lambda i: float(np.linalg.lstsq(A[i], obs[i], rcond=None)[0][0])
                                                         if np.ptp(pred[i]) > 1e-9 else None, n, rng, 2000)}
        d["beta"] = {}
        d["censoring"] = {}
        for dt in DTS:
            be = np.array([S[t]["cells"][mode][dkey(dt)]["beta"] for t in tags])
            d["beta"][dkey(dt)] = {"min": float(be.min()), "max": float(be.max()), "median": float(np.median(be)),
                                   "n_below_1": int((be < 1).sum()), "share_below_1": float((be < 1).mean()),
                                   "n_below_1p5": int((be < 1.5).sum()), "share_below_1p5": float((be < 1.5).mean())}
            rows = [r for t in tags for r in by[(t, mode, dt)]]
            d["censoring"][dkey(dt)] = {"censored": int(sum(r["censored"] for r in rows)), "n": len(rows),
                                        "frac": float(np.mean([r["censored"] for r in rows])), "t_cens": rows[0]["t_cens"],
                                        "snapshots_no_escape": int(sum(S[t]["cells"][mode][dkey(dt)]["events"] == 0 for t in tags))}
        out["arms"][mode] = d
    e3 = json.load(open(os.path.join(DERIVED, "E3_analysis.json")))
    out["E3_reference"] = {m: {"ell_mean": e3["ell"][m]["mean_obs"], "ci95_boot": e3["ell"][m]["mean_obs_ci95_boot"],
                               "pred_mean": e3["ell"][m]["mean_pred"]} for m in MODES}
    print(rev4lib.out_json("T3", out))
    for m, d in out["arms"].items():
        print(m, "ell", round(d["ell_mean"], 3), [round(x, 3) for x in d["ell_ci95_boot"]], "pred", round(d["pred_mean"], 3),
              "n", d["n_with_ell"], {k: (round(v["min"], 2), round(v["max"], 2), v["n_below_1"]) for k, v in d["beta"].items()},
              {k: v["frac"] for k, v in d["censoring"].items()})


if __name__ == "__main__":
    main()
