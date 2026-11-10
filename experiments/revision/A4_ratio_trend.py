"""A4: does the Arrhenius slope ratio r = s / (-Delta U) of Fig. 4 (right) trend with Delta U?

Input: data/derived/E4_analysis.json (experiments/E4/analyze.py). Per (snapshot, condition) with an Arrhenius
fit (28 fits: full 8, pinned = "frozen" 10, alone 10; 10 snapshots), the ratio r = -s / dU_cond, s the
event-weighted least-squares slope of ln lambda_hat on 1 / k_B T_eff over the three levels
Delta U_cond / k_B T_eff = 1.5, 2.5, 3.5, and its 95% interval (parametric Poisson resampling of the counts).
The regressor is x = ln(dU_cond / 1 J), dU_cond the barrier in that condition (the abscissa of Fig. 4 right).

Models (slope b of r on x is the quantity of interest):
  per_condition    r = a_c + b_c x, separately for full, pinned, alone
  pooled_cond_int  r = a_c + b x  (one intercept per condition, common slope)
  pooled_common    r = a + b x
Interval methods for b:
  ols_boot_snap    ordinary least squares; 95% percentile interval from 4000 bootstrap resamples of the
                   10 snapshots with replacement (each draw carries all of that snapshot's fits); draws with a
                   degenerate design (fewer than 3 distinct x in a condition fit) are discarded
  wls              weighted least squares, weight 1 / se^2 with se = (hi - lo) / 3.92 from the per-fit
                   interval; interval b +- t_{0.975, dof} * se_b with se_b scaled by sqrt(chi2 / dof)
                   (residual scatter beyond the per-fit errors), and the unscaled (known-variance, z) interval;
                   chi2 / dof reported
  poisson_boot     measurement error only: 4000 parametric resamples of every cell's event count (Poisson at
                   the observed count, exposure fixed), every ratio refitted as in E4 (fits with a zero count
                   in a draw are dropped from that draw), OLS slope b refitted; percentile interval
Diagnostic (realised temperature): per (snapshot, condition, level) cell the blocker's realised velocity variance
from the stored moments v_moments of data/E4/e4_escape.jsonl (as experiments/E3/t3_variance.py), c = m var / k_B T_eff;
the ratio is refitted with 1 / (c k_B T_eff) as abscissa (same event-weighted fit), r_real, and r_real is regressed
on x as above (OLS, snapshot bootstrap). Fits whose cells have fewer than 200 moment samples keep c = 1.
Leave-one-snapshot-out range of the OLS slope (influence check). Also: Spearman rank correlation of r with dU_cond (pooled and per condition), and the predicted size of a
ratio offset from a prefactor nu proportional to (k_B T)^alpha, r = 1 + alpha <1/beta> (independent of Delta U
at fixed beta levels).
Output: data/derived/rev_A4.json
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import DERIVED, pdisp, sig  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

CONDS = ("full", "frozen", "alone")
LV = ("b1p5", "b2p5", "b3p5")
NB = 4000
RNG = 20261110


def fits():
    E4 = json.load(open(os.path.join(DERIVED, "E4_analysis.json")))
    out = []
    for tag, s in E4["snapshots"].items():
        for c in CONDS:
            cc = s["conds"].get(c)
            if not cc or not cc.get("arrhenius"):
                continue
            a = cc["arrhenius"]
            L = [cc["levels"][k] for k in LV]
            out.append({"snap": tag, "cond": c, "dU": cc["dU"], "x": math.log(cc["dU"]), "r": a["ratio"],
                        "lo": a["ratio_ci95"][0], "hi": a["ratio_ci95"][1],
                        "se": (a["ratio_ci95"][1] - a["ratio_ci95"][0]) / 3.92,
                        "d": [l["events"] for l in L], "T": [l["exposure_s"] for l in L],
                        "ikT": [1.0 / l["kT_eff"] for l in L]})
    return out


def design(F, model, cond=None):
    if model == "per_condition":
        F = [f for f in F if f["cond"] == cond]
        X = np.column_stack([np.ones(len(F)), [f["x"] for f in F]])
    elif model == "pooled_cond_int":
        X = np.column_stack([np.array([f["cond"] == c for f in F], float) for c in CONDS] + [[f["x"] for f in F]])
    else:
        X = np.column_stack([np.ones(len(F)), [f["x"] for f in F]])
    return F, X


def ols_b(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(beta[-1]), beta


def wls(X, y, se):
    w = 1.0 / se ** 2
    Xw = X * np.sqrt(w)[:, None]
    yw = y * np.sqrt(w)
    beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
    cov = np.linalg.inv(Xw.T @ Xw)
    res = yw - Xw @ beta
    dof = len(y) - X.shape[1]
    chi2 = float(res @ res)
    se_b0 = math.sqrt(cov[-1, -1])
    se_b = se_b0 * math.sqrt(max(chi2 / dof, 1.0)) if dof > 0 else float("nan")
    se_bs = se_b0 * math.sqrt(chi2 / dof)
    t = stats.t.ppf(0.975, dof)
    b = float(beta[-1])
    p = 2 * stats.t.sf(abs(b / se_bs), dof)
    return {"b": b, "ci95_scaled": [b - t * se_bs, b + t * se_bs], "ci95_known_var": [b - 1.96 * se_b0, b + 1.96 * se_b0],
            "se_scaled": se_bs, "se_known_var": se_b0, "chi2_dof": chi2 / dof, "dof": dof, "p_scaled": p,
            "p_scaled_disp": pdisp(p), "intercepts": [float(v) for v in beta[:-1]]}


def ratio_from_counts(f, d):
    x = np.array(f["ikT"])
    T = np.array(f["T"])
    y = np.log(d / T)
    W = d.sum()
    xm, ym = (d * x).sum() / W, (d * y).sum() / W
    s = (d * (x - xm) * (y - ym)).sum() / (d * (x - xm) ** 2).sum()
    return -s / f["dU"]


def analyse(F, model, cond=None, rng=None):
    G, X = design(F, model, cond)
    y = np.array([f["r"] for f in G])
    se = np.array([f["se"] for f in G])
    b, beta = ols_b(X, y)
    o = {"n_fits": len(G), "ols_b": b, "ols_intercepts": [float(v) for v in beta[:-1]], "wls": wls(X, y, se)}
    # leave one snapshot out
    loo = {}
    for s_ in sorted({f["snap"] for f in G}):
        Gl, Xl = design([f for f in F if f["snap"] != s_], model, cond)
        loo[s_] = ols_b(Xl, np.array([f["r"] for f in Gl]))[0]
    o["loo_snap"] = {"b_min": min(loo.values()), "b_max": max(loo.values()),
                     "argmin": min(loo, key=loo.get), "argmax": max(loo, key=loo.get)}
    # bootstrap over snapshots
    snaps = sorted({f["snap"] for f in F})
    bs = []
    for _ in range(NB):
        pick = rng.choice(snaps, len(snaps), replace=True)
        Fb = [f for s in pick for f in F if f["snap"] == s]
        Gb, Xb = design(Fb, model, cond)
        if len(Gb) < 3:
            continue
        xs = [f["x"] for f in Gb]
        if len(set(np.round(xs, 12))) < 3:
            continue
        if model == "pooled_cond_int" and np.linalg.matrix_rank(Xb) < Xb.shape[1]:
            continue
        bs.append(ols_b(Xb, np.array([f["r"] for f in Gb]))[0])
    o["ols_boot_snap"] = {"ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                          "n_draws": len(bs), "frac_b_below_0": float(np.mean(np.array(bs) < 0))}
    # parametric Poisson bootstrap of the ratios
    pb = []
    for _ in range(NB):
        keep, rr = [], []
        for f in G:
            d = rng.poisson(np.array(f["d"], float)).astype(float)
            if (d > 0).all():
                keep.append(f)
                rr.append(ratio_from_counts(f, d))
        Gk, Xk = design(keep, model, cond)
        if len(Gk) < 3 or np.linalg.matrix_rank(Xk) < Xk.shape[1]:
            continue
        pb.append(ols_b(Xk, np.array(rr))[0])
    o["poisson_boot"] = {"ci95": [float(np.percentile(pb, 2.5)), float(np.percentile(pb, 97.5))], "n_draws": len(pb)}
    rho, p = stats.spearmanr([f["dU"] for f in G], y)
    o["spearman"] = {"rho": float(rho), "p": float(p), "p_disp": pdisp(float(p))}
    o["dU_range"] = [min(f["dU"] for f in G), max(f["dU"] for f in G)]
    o["r_range"] = [float(y.min()), float(y.max())]
    # implied change of r over the observed Delta U range (one decade = b ln 10)
    o["per_decade"] = b * math.log(10)
    o["over_range"] = b * (math.log(o["dU_range"][1]) - math.log(o["dU_range"][0]))
    for k in ("ols_b", "per_decade", "over_range"):
        o[k + "_2sf"] = sig(o[k], 2)
    o["ols_boot_snap"]["ci95_2sf"] = [sig(v, 2) for v in o["ols_boot_snap"]["ci95"]]
    o["wls"]["b_2sf"] = sig(o["wls"]["b"], 2)
    o["wls"]["ci95_scaled_2sf"] = [sig(v, 2) for v in o["wls"]["ci95_scaled"]]
    o["poisson_boot"]["ci95_2sf"] = [sig(v, 2) for v in o["poisson_boot"]["ci95"]]
    return o


def realised_c():
    acc, kt = {}, {}
    for ln in open(os.path.join(revlib.ROOT, "data", "E4", "e4_escape.jsonl")):
        r = json.loads(ln)
        kk = (r["snap"][:-4], r["cond"], r["beta_ref"])
        acc[kk] = acc.get(kk, 0) + np.array(r["v_moments"])
        kt[kk] = r["kT_eff"] / r["m"]
    out = {}
    for kk, s in acc.items():
        if s[0] >= 200:
            v = 0.5 * ((s[3] / s[0] - (s[1] / s[0]) ** 2) + (s[4] / s[0] - (s[2] / s[0]) ** 2))
            out[kk] = float(v / kt[kk])
    return out


def realised(F, rng):
    C = realised_c()
    G = []
    for f in F:
        c = [C.get((f["snap"], f["cond"], b), 1.0) for b in (1.5, 2.5, 3.5)]
        g = dict(f, c=c, ikT=[i / ci for i, ci in zip(f["ikT"], c)])
        g["r"] = ratio_from_counts(g, np.array(f["d"], float))
        G.append(g)
    o = {"n_cells_with_moments": len(C), "c_median": float(np.median(list(C.values()))),
         "c_range": [min(C.values()), max(C.values())]}
    for name, model, cond in (("full", "per_condition", "full"), ("frozen", "per_condition", "frozen"),
                              ("alone", "per_condition", "alone"), ("pooled_cond_int", "pooled_cond_int", None),
                              ("pooled_common", "pooled_common", None)):
        H, X = design(G, model, cond)
        b = ols_b(X, np.array([h["r"] for h in H]))[0]
        snaps = sorted({f["snap"] for f in G})
        bs = []
        for _ in range(NB):
            pick = rng.choice(snaps, len(snaps), replace=True)
            Hb, Xb = design([f for s_ in pick for f in G if f["snap"] == s_], model, cond)
            if len(Hb) < 3 or len(set(np.round(Xb[:, -1], 12))) < 3 or np.linalg.matrix_rank(Xb) < Xb.shape[1]:
                continue
            bs.append(ols_b(Xb, np.array([h["r"] for h in Hb]))[0])
        o[name] = {"ols_b": b, "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                   "r_median": float(np.median([h["r"] for h in H])), "ols_b_2sf": sig(b, 2)}
    # c against level and dU in the alone condition
    o["c_alone_by_fit"] = [{"snap": g["snap"], "dU": g["dU"], "c": g["c"], "r_real": g["r"]} for g in G if g["cond"] == "alone"]
    rho, p = stats.spearmanr([g["dU"] for g in G], [float(np.mean(g["c"])) for g in G])
    o["spearman_c_dU"] = {"rho": float(rho), "p": float(p)}
    return o


def main():
    rng = np.random.default_rng(RNG)
    F = fits()
    o = {"n_fits": len(F), "n_snapshots": len({f["snap"] for f in F}),
         "n_per_condition": {c: sum(f["cond"] == c for f in F) for c in CONDS},
         "regressor": "ln(dU_cond / J)", "response": "Arrhenius slope / (-dU_cond)",
         "per_condition": {c: analyse(F, "per_condition", c, rng) for c in CONDS},
         "pooled_cond_int": analyse(F, "pooled_cond_int", None, rng),
         "pooled_common": analyse(F, "pooled_common", None, rng)}
    inv_beta = float(np.mean([1 / 1.5, 1 / 2.5, 1 / 3.5]))
    o["prefactor_T_power"] = {"mean_inv_beta": inv_beta,
                              "note": "nu ~ (kT)^alpha gives r = 1 + alpha kT/dU averaged over the levels; at fixed "
                                      "beta levels the offset alpha <1/beta> does not depend on dU",
                              "alpha_for_r_minus_1": {str(a): a * inv_beta for a in (-1.0, -0.5, 0.5, 1.0)}}
    o["realised_T"] = realised(F, rng)
    o["fits"] = [{k: f[k] for k in ("snap", "cond", "dU", "r", "lo", "hi", "se")} for f in F]
    revlib.out_json("A4", o)
    for k in ("full", "frozen", "alone"):
        p = o["per_condition"][k]
        print(k, p["n_fits"], "b %.3f" % p["ols_b"], "boot", np.round(p["ols_boot_snap"]["ci95"], 3),
              "wls %.3f" % p["wls"]["b"], np.round(p["wls"]["ci95_scaled"], 3), "chi2/dof %.2f" % p["wls"]["chi2_dof"],
              "pois", np.round(p["poisson_boot"]["ci95"], 3), "spearman %.2f p %.3f" % (p["spearman"]["rho"], p["spearman"]["p"]))
    for k in ("pooled_cond_int", "pooled_common"):
        p = o[k]
        print(k, p["n_fits"], "b %.3f" % p["ols_b"], "boot", np.round(p["ols_boot_snap"]["ci95"], 3),
              "wls %.3f" % p["wls"]["b"], np.round(p["wls"]["ci95_scaled"], 3), np.round(p["wls"]["ci95_known_var"], 3),
              "chi2/dof %.2f" % p["wls"]["chi2_dof"], "pois", np.round(p["poisson_boot"]["ci95"], 3),
              "spearman %.2f p %.3f" % (p["spearman"]["rho"], p["spearman"]["p"]), "frac<0", p["ols_boot_snap"]["frac_b_below_0"])


    print("realised", {k: v for k, v in o["realised_T"].items() if k != "c_alone_by_fit"})


if __name__ == "__main__":
    main()
