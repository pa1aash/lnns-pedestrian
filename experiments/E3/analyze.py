"""E3 analysis: the time-step signature of noise-activated escape.

Input:  data/E3/e3_dt.jsonl (experiments/E3/e3_dt.py; 20 snapshots, condition "full").
Output: data/derived/E3_analysis.json, figures/data/fig5.json.

Definitions
  lambda_hat    censored-exponential escape rate per (snapshot, arm, dt), 20 restarts, exact Poisson 95% CI
                (experiments/E3/survival.py).
  ell_i         ln lambda_hat(0.005) / lambda_hat(0.02) per snapshot and noise arm; 95% CI from the delta
                method, sd = sqrt(1/d_0.005 + 1/d_0.02).
  prediction    Arrhenius with the exact discrete k_B T_eff (experiments/lib/teff.py) and a dt-independent
                prefactor: ell_pred = dU_i (1/k_B T_eff(0.02) - 1/k_B T_eff(0.005)), stored per row by e3_dt.py;
                normalised rate lambda(dt) / lambda(0.01) = exp(beta_ref - dU_i / k_B T_eff(dt)).
  slope         observed on predicted ell over the 20 snapshots (per-step arm): OLS with intercept and the
                through-origin ratio sum(obs) / sum(pred). CIs: 2000 resamples of snapshots, percentile,
                PCG64(12345).
  C3 RVO2       deterministic, one run per dt: ln t_esc(0.02) / t_esc(0.005) (same sign convention as ell,
                rate = 1 / t_esc); snapshots never freed within 300 s are counted separately.
  Weibull       censored Weibull shape per (arm, dt), shape shared over snapshots with a scale per snapshot,
                95% profile-likelihood CI; also per (snapshot, arm, dt).
"""
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from survival import Z95, boot_ci, exp_rate, weibull_pool  # noqa: E402
from teff import kT_eff  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IN = os.path.join(ROOT, "data", "E3", "e3_dt.jsonl")
OUT = os.path.join(ROOT, "data", "derived", "E3_analysis.json")
FIG5 = os.path.join(ROOT, "figures", "data", "fig5.json")
DTS = (0.005, 0.01, 0.02)
MODES = ("per_step", "dt_scaled")
LEVELS = (1.5, 2.5)
N_BOOT, RNG_SEED = 2000, 12345


def dkey(dt):
    return f"dt{dt:g}".replace(".", "p")


def load():
    R = [json.loads(ln) for ln in open(IN)]
    by = defaultdict(list)
    meta = {}
    for r in R:
        tag = r["job_id"].split("|")[0]
        by[(tag, r["mode"], r["dt"])].append(r)
        meta.setdefault(tag, {k: r[k] for k in ("blocker", "beta_ref", "tau_b", "dU_i", "dU_rank", "sigma_i",
                                                "ell_pred_per_step", "ell_pred_dt_scaled")})
    return by, meta


def main():
    by, meta = load()
    tags = sorted(meta, key=lambda t: meta[t]["dU_rank"])
    snaps = {}
    for tag in tags:
        m = meta[tag]
        s = {**m, "cells": {}, "ell": {}}
        for mode in MODES:
            s["cells"][mode] = {}
            for dt in DTS:
                rows = by[(tag, mode, dt)]
                t = [r["t_run"] for r in rows]
                c = [r["censored"] for r in rows]
                cell = exp_rate(t, c)
                cell["t_cens"] = rows[0]["t_cens"]
                cell["kT_eff"] = rows[0]["kT_eff"]
                cell["beta"] = rows[0]["beta"]
                cell["other_exit_first"] = int(sum(r["other_exit_first"] for r in rows))
                w = weibull_pool([(t, c)])
                cell["weibull_k"] = w["k"] if w else None
                s["cells"][mode][dkey(dt)] = cell
            a, b = s["cells"][mode]["dt0p005"], s["cells"][mode]["dt0p02"]
            if a["events"] and b["events"]:
                ell = math.log(a["lam"] / b["lam"])
                sd = math.sqrt(1 / a["events"] + 1 / b["events"])
                s["ell"][mode] = {"obs": ell, "ci95": [ell - Z95 * sd, ell + Z95 * sd], "sd": sd,
                                  "pred": m[f"ell_pred_{mode}"]}
            else:
                s["ell"][mode] = {"obs": None, "pred": m[f"ell_pred_{mode}"]}
            ref = s["cells"][mode]["dt0p01"]["lam"]
            s["cells"][mode]["norm"] = {dkey(dt): s["cells"][mode][dkey(dt)]["lam"] / ref for dt in DTS}
        c3 = {dkey(dt): by[(tag, "C3_rvo2", dt)][0] for dt in DTS}
        tt = {k: (None if r["censored"] else r["escape_t"]) for k, r in c3.items()}
        s["C3_rvo2"] = {"t_esc": tt, "freed": all(v is not None for v in tt.values()),
                        "ln_ratio": (math.log(tt["dt0p02"] / tt["dt0p005"]) if all(tt.values()) else None),
                        "norm_inv_t": ({k: tt["dt0p01"] / v for k, v in tt.items()} if all(tt.values()) else None)}
        snaps[tag] = s

    rng = np.random.default_rng(RNG_SEED)
    out = {"n_snapshots": len(tags), "restarts_per_cell": 20, "snapshots": snaps}

    # censoring fraction and pooled Weibull shape per (arm, dt)
    cens, weib = {}, {}
    for mode in MODES:
        cens[mode], weib[mode] = {}, {}
        for dt in DTS:
            rows = [r for tag in tags for r in by[(tag, mode, dt)]]
            cens[mode][dkey(dt)] = {"censored": int(sum(r["censored"] for r in rows)), "n": len(rows),
                                    "frac": float(np.mean([r["censored"] for r in rows])),
                                    "t_cens": rows[0]["t_cens"],
                                    "per_snapshot_max": max(snaps[t]["cells"][mode][dkey(dt)]["censored_frac"]
                                                            for t in tags)}
            weib[mode][dkey(dt)] = weibull_pool([([r["t_run"] for r in by[(t, mode, dt)]],
                                                  [r["censored"] for r in by[(t, mode, dt)]]) for t in tags])
    out["censoring"] = cens
    out["weibull_pooled"] = weib

    # ell by beta_ref level and the slope of observed on predicted
    summ = {}
    for mode in MODES:
        T = [t for t in tags if snaps[t]["ell"][mode]["obs"] is not None]
        obs = np.array([snaps[t]["ell"][mode]["obs"] for t in T])
        pred = np.array([snaps[t]["ell"][mode]["pred"] for t in T])
        lev = np.array([snaps[t]["beta_ref"] for t in T])
        d = {"n": len(T), "mean_obs": float(obs.mean()), "mean_pred": float(pred.mean()),
             "mean_obs_ci95_boot": boot_ci(lambda i: obs[i].mean(), len(T), rng, N_BOOT),
             "mean_obs_ci95_t": [float(obs.mean() - 2.093 * obs.std(ddof=1) / math.sqrt(len(T))),
                                 float(obs.mean() + 2.093 * obs.std(ddof=1) / math.sqrt(len(T)))],
             "by_level": {}}
        for L in LEVELS:
            k = lev == L
            o, p = obs[k], pred[k]
            d["by_level"][f"b{L:g}".replace(".", "p")] = {
                "n": int(k.sum()), "mean_obs": float(o.mean()), "mean_pred": float(p.mean()),
                "sd_obs": float(o.std(ddof=1)),
                "mean_obs_ci95_boot": boot_ci(lambda i: o[i].mean(), int(k.sum()), rng, N_BOOT),
                "ratio_obs_pred": float(o.mean() / p.mean()) if abs(p.mean()) > 0.1 else None}
        if mode == "per_step":
            A = np.vstack([pred, np.ones_like(pred)]).T

            def ols(i):
                if np.ptp(pred[i]) < 1e-9:
                    return None
                return float(np.linalg.lstsq(A[i], obs[i], rcond=None)[0][0])
            coef = np.linalg.lstsq(A, obs, rcond=None)[0]
            d["slope_ols"] = {"slope": float(coef[0]), "intercept": float(coef[1]),
                              "slope_ci95_boot": boot_ci(ols, len(T), rng, N_BOOT)}
            d["slope_origin"] = {"slope": float(obs.sum() / pred.sum()),
                                 "ci95_boot": boot_ci(lambda i: obs[i].sum() / pred[i].sum(), len(T), rng, N_BOOT)}
            d["snapshot_ci_covers_pred"] = int(sum(snaps[t]["ell"][mode]["ci95"][0] <= snaps[t]["ell"][mode]["pred"]
                                                   <= snaps[t]["ell"][mode]["ci95"][1] for t in T))
        summ[mode] = d
    out["ell"] = summ

    # C3 RVO2
    fr = [t for t in tags if snaps[t]["C3_rvo2"]["freed"]]
    lr = np.array([snaps[t]["C3_rvo2"]["ln_ratio"] for t in fr])
    out["C3_rvo2"] = {"n_freed": len(fr), "n_held_300s": len(tags) - len(fr),
                      "held": [t for t in tags if t not in fr],
                      "ln_ratio_mean": float(lr.mean()), "ln_ratio_maxabs": float(np.abs(lr).max()),
                      "ln_ratio_ci95_boot": boot_ci(lambda i: lr[i].mean(), len(fr), rng, N_BOOT),
                      "t_esc_median_dt0p01": float(np.median([snaps[t]["C3_rvo2"]["t_esc"]["dt0p01"] for t in fr]))}
    out["other_exit_first_total"] = int(sum(snaps[t]["cells"][m][dkey(dt)]["other_exit_first"]
                                            for t in tags for m in MODES for dt in DTS))
    # headline numbers as flat keys for the registry
    ps, ds = summ["per_step"], summ["dt_scaled"]
    out["headline"] = {
        "ell_ps_b1p5_obs": ps["by_level"]["b1p5"]["mean_obs"], "ell_ps_b1p5_pred": ps["by_level"]["b1p5"]["mean_pred"],
        "ell_ps_b1p5_lo": ps["by_level"]["b1p5"]["mean_obs_ci95_boot"][0],
        "ell_ps_b1p5_hi": ps["by_level"]["b1p5"]["mean_obs_ci95_boot"][1],
        "ell_ps_b2p5_obs": ps["by_level"]["b2p5"]["mean_obs"], "ell_ps_b2p5_pred": ps["by_level"]["b2p5"]["mean_pred"],
        "ell_ps_b2p5_lo": ps["by_level"]["b2p5"]["mean_obs_ci95_boot"][0],
        "ell_ps_b2p5_hi": ps["by_level"]["b2p5"]["mean_obs_ci95_boot"][1],
        "slope": ps["slope_ols"]["slope"], "slope_lo": ps["slope_ols"]["slope_ci95_boot"][0],
        "slope_hi": ps["slope_ols"]["slope_ci95_boot"][1],
        "slope_origin": ps["slope_origin"]["slope"], "slope_origin_lo": ps["slope_origin"]["ci95_boot"][0],
        "slope_origin_hi": ps["slope_origin"]["ci95_boot"][1],
        "ell_ds_obs": ds["mean_obs"], "ell_ds_lo": ds["mean_obs_ci95_boot"][0], "ell_ds_hi": ds["mean_obs_ci95_boot"][1],
        "ell_ds_pred": ds["mean_pred"],
        "c3_ln_ratio": out["C3_rvo2"]["ln_ratio_mean"], "c3_ln_ratio_maxabs": out["C3_rvo2"]["ln_ratio_maxabs"],
        "c3_n_freed": out["C3_rvo2"]["n_freed"], "c3_n_held": out["C3_rvo2"]["n_held_300s"],
        "cens_ps_dt0p02": cens["per_step"]["dt0p02"]["frac"], "cens_ps_dt0p005": cens["per_step"]["dt0p005"]["frac"],
        "weib_ps_dt0p005": weib["per_step"]["dt0p005"]["k"], "weib_ps_dt0p01": weib["per_step"]["dt0p01"]["k"],
        "weib_ps_dt0p02": weib["per_step"]["dt0p02"]["k"],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    fig5_cache(out, tags, rng)
    brief(out)


def fig5_cache(o, tags, rng):
    """Normalised rates per level (geometric mean over snapshots, bootstrap CI), per-snapshot points,
    predicted curves (exact T_eff, geometric mean of the per-snapshot prediction) and C3 RVO2."""
    S = o["snapshots"]
    grid = np.geomspace(0.0045, 0.022, 60)
    d = {"dts": list(DTS), "grid": grid.tolist(), "per_step": {}, "dt_scaled": {}, "C3_rvo2": {}}
    for mode in MODES:
        for L in LEVELS:
            T = [t for t in tags if S[t]["beta_ref"] == L]
            M = np.log(np.array([[S[t]["cells"][mode]["norm"][dkey(dt)] for dt in DTS] for t in T]))
            mean = np.exp(M.mean(0))
            ci = [boot_ci(lambda i, j=j: float(np.exp(M[i, j].mean())), len(T), rng, N_BOOT) for j in range(3)]
            P = np.array([[L - S[t]["dU_i"] / kT_eff(S[t]["sigma_i"], g, S[t]["tau_b"], mode=mode) for g in grid]
                          for t in T])
            d[mode][f"b{L:g}".replace(".", "p")] = {"mean": mean.tolist(), "ci95": ci,
                                                    "points": np.exp(M).tolist(),
                                                    "pred": np.exp(P.mean(0)).tolist()}
    F = [t for t in tags if S[t]["C3_rvo2"]["freed"]]
    M = np.log(np.array([[S[t]["C3_rvo2"]["norm_inv_t"][dkey(dt)] for dt in DTS] for t in F]))
    d["C3_rvo2"] = {"mean": np.exp(M.mean(0)).tolist(), "points": np.exp(M).tolist(), "n": len(F)}
    os.makedirs(os.path.dirname(FIG5), exist_ok=True)
    json.dump(d, open(FIG5, "w"), indent=1)


def brief(o):
    h = o["headline"]
    print("per-step ell  b1.5 obs %.2f [%.2f, %.2f] pred %.2f | b2.5 obs %.2f [%.2f, %.2f] pred %.2f" % (
        h["ell_ps_b1p5_obs"], h["ell_ps_b1p5_lo"], h["ell_ps_b1p5_hi"], h["ell_ps_b1p5_pred"],
        h["ell_ps_b2p5_obs"], h["ell_ps_b2p5_lo"], h["ell_ps_b2p5_hi"], h["ell_ps_b2p5_pred"]))
    print("slope OLS %.2f [%.2f, %.2f] intercept %.2f; origin %.2f [%.2f, %.2f]; snapshot CIs covering pred %d/%d" % (
        h["slope"], h["slope_lo"], h["slope_hi"], o["ell"]["per_step"]["slope_ols"]["intercept"],
        h["slope_origin"], h["slope_origin_lo"], h["slope_origin_hi"],
        o["ell"]["per_step"]["snapshot_ci_covers_pred"], o["ell"]["per_step"]["n"]))
    print("dt-scaled ell %.3f [%.3f, %.3f] pred %.3f" % (h["ell_ds_obs"], h["ell_ds_lo"], h["ell_ds_hi"], h["ell_ds_pred"]))
    print("C3 RVO2 ln ratio %.4f (max |.| %.4f), freed %d, held %d" % (
        h["c3_ln_ratio"], h["c3_ln_ratio_maxabs"], h["c3_n_freed"], h["c3_n_held"]))
    for m in MODES:
        print(m, "censored", {k: round(v["frac"], 3) for k, v in o["censoring"][m].items()},
              "Weibull k", {k: (round(v["k"], 2), [round(x, 2) for x in v["ci95"]]) for k, v in o["weibull_pooled"][m].items()})
    print("other agent exited first (full condition):", o["other_exit_first_total"])


if __name__ == "__main__":
    main()
