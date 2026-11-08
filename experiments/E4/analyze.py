"""E4 analysis: noise-activated escape as a collective process.

Input:  data/E4/e4_escape.jsonl, data/E4/e4_extension.json (experiments/E4/e4_escape.py),
        data/derived/selection.json (E4 snapshots, class, residual count).
Output: data/derived/E4_analysis.json, figures/data/fig4.json.

Definitions
  lambda_hat   censored-exponential escape rate per (snapshot, condition, level), exact Poisson 95% CI
               (experiments/E3/survival.py); level = dU_cond / k_B T_eff at dt = 0.01 s in {1.5, 2.5, 3.5}.
  Arrhenius    per (snapshot, condition): weighted least squares of ln lambda_hat on 1 / k_B T_eff over the
               three levels (weights = events, var ln lambda = 1/d); slope s. Ratio r = -s / dU_cond (1 = the
               escape is activated over the computed barrier); 95% CI from 2000 parametric resamples of the
               event counts (Poisson at the observed counts, exposure fixed), percentile, PCG64(12345).
               Fitted only where all three levels have at least 3 events.
  prefactor    nu_hat = exp(weighted mean of ln lambda_hat + dU_cond / k_B T_eff), i.e. the attempt rate with
               the slope held at -dU_cond; also the free-slope intercept exp(a).
  collapse     ln(lambda_hat / nu_hat) against dU_cond / k_B T_eff for every (snapshot, condition, level).
  Weibull      censored Weibull shape shared over all (snapshot, level) groups of a condition, a scale per
               group (per-snapshot scale normalisation), 95% profile-likelihood CI; also over all conditions.
  KM           Kaplan-Meier of the escape time, pooled over snapshots, per condition, at level 2.5 (300 s).
  saddle       per snapshot: dU_alone - dU_full and dU_full / dU_alone (accepted gate barriers).
"""
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "E3"))
from survival import exp_rate, km, weibull_pool  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IN = os.path.join(ROOT, "data", "E4", "e4_escape.jsonl")
EXT = os.path.join(ROOT, "data", "E4", "e4_extension.json")
SEL = os.path.join(ROOT, "data", "derived", "selection.json")
OUT = os.path.join(ROOT, "data", "derived", "E4_analysis.json")
FIG4 = os.path.join(ROOT, "figures", "data", "fig4.json")
CONDS = ("full", "frozen", "alone")
LEVELS = (1.5, 2.5, 3.5)
KM_LEVEL = 2.5
N_BOOT, RNG_SEED, MIN_EV = 2000, 12345, 3


def lk(L):
    return f"b{L:g}".replace(".", "p")


def wls(x, y, w):
    W = w.sum()
    xm, ym = (w * x).sum() / W, (w * y).sum() / W
    s = (w * (x - xm) * (y - ym)).sum() / (w * (x - xm) ** 2).sum()
    return s, ym - s * xm


def main():
    R = [json.loads(ln) for ln in open(IN)]
    sel = {s["tag"]: s for s in json.load(open(SEL))["E4"]["snapshots"]}
    ext = json.load(open(EXT))
    by = defaultdict(list)
    for r in R:
        by[(r["snap"][:-4], r["cond"], r["beta_ref"])].append(r)
    tags = sorted({k[0] for k in by}, key=lambda t: sel[t]["dU"])
    rng = np.random.default_rng(RNG_SEED)
    snaps, collapse = {}, []
    for tag in tags:
        s = {"class": sel[tag]["class"], "n_resid": sel[tag]["n_resid"], "conds": {}}
        for c in CONDS:
            if (tag, c, LEVELS[0]) not in by:
                continue
            cc = {"levels": {}}
            for L in LEVELS:
                rows = by[(tag, c, L)]
                cell = exp_rate([r["t_run"] for r in rows], [r["censored"] for r in rows])
                cell.update({"sigma": rows[0]["sigma"], "kT_eff": rows[0]["kT_eff"], "t_cens": rows[0]["t_cens"],
                             "other_exit_first": int(sum(r["other_exit_first"] for r in rows))})
                cc["levels"][lk(L)] = cell
            cc["dU"] = by[(tag, c, LEVELS[0])][0]["dU_cond"]
            cells = [cc["levels"][lk(L)] for L in LEVELS]
            d = np.array([x["events"] for x in cells], float)
            T = np.array([x["exposure_s"] for x in cells])
            x = 1.0 / np.array([x["kT_eff"] for x in cells])
            if (d >= MIN_EV).all():
                y = np.log(d / T)
                sl, a = wls(x, y, d)
                bs = []
                for _ in range(N_BOOT):
                    db = rng.poisson(d)
                    if (db > 0).all():
                        bs.append(-wls(x, np.log(db / T), db)[0] / cc["dU"])
                nu = math.exp(float((d * (y + cc["dU"] * x)).sum() / d.sum()))
                cc["arrhenius"] = {"slope": sl, "intercept": a, "ratio": -sl / cc["dU"],
                                   "ratio_ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                                   "nu_hat": nu, "nu_free": math.exp(a)}
                for L, cell in zip(LEVELS, cells):
                    collapse.append({"tag": tag, "cond": c, "level": L, "x": cc["dU"] / cell["kT_eff"],
                                     "y": math.log(cell["lam"] / nu), "events": cell["events"]})
            else:
                cc["arrhenius"] = None
            s["conds"][c] = cc
        dUa, dUf = sel[tag]["dU_alone"], sel[tag]["dU"]
        s["saddle"] = {"dU_alone": dUa, "dU_frozen": sel[tag]["dU_frozen"], "dU_full": dUf,
                       "alone_minus_full": dUa - dUf, "full_over_alone": dUf / dUa}
        snaps[tag] = s

    out = {"n_snapshots": len(tags), "extension": ext, "snapshots": snaps, "collapse": collapse}
    # events per condition, Weibull, ratios pooled per condition
    pc = {}
    allg = []
    for c in CONDS:
        G = [([r["t_run"] for r in by[(t, c, L)]], [r["censored"] for r in by[(t, c, L)]])
             for t in tags for L in LEVELS if (t, c, L) in by]
        allg += G
        ratios = [snaps[t]["conds"][c]["arrhenius"]["ratio"] for t in tags
                  if c in snaps[t]["conds"] and snaps[t]["conds"][c]["arrhenius"]]
        fitted = [t for t in tags if c in snaps[t]["conds"] and snaps[t]["conds"][c]["arrhenius"]]
        cover = sum(snaps[t]["conds"][c]["arrhenius"]["ratio_ci95"][0] <= 1 <= snaps[t]["conds"][c]["arrhenius"]["ratio_ci95"][1]
                    for t in fitted)
        nus = [snaps[t]["conds"][c]["arrhenius"]["nu_hat"] for t in fitted]
        pc[c] = {"events": int(sum((~np.asarray(cn, bool)).sum() for _, cn in G)),
                 "runs": int(sum(len(cn) for _, cn in G)), "snapshots": sum(c in snaps[t]["conds"] for t in tags),
                 "weibull": weibull_pool(G), "n_arrhenius_fits": len(ratios),
                 "ratio_median": float(np.median(ratios)) if ratios else None,
                 "ratio_min": float(min(ratios)) if ratios else None, "ratio_max": float(max(ratios)) if ratios else None,
                 "ratio_ci_covers_1": int(cover), "nu_hat_median": float(np.median(nus)) if nus else None,
                 "nu_hat_range": [float(min(nus)), float(max(nus))] if nus else None}
    out["per_condition"] = pc
    out["weibull_all"] = weibull_pool(allg)
    X = np.array([p["x"] for p in collapse])
    Y = np.array([p["y"] for p in collapse])
    W = np.array([p["events"] for p in collapse], float)
    sl, a = wls(X, Y, W)
    out["collapse_fit"] = {"slope": sl, "intercept": a, "n_points": len(collapse),
                           "rms_resid_about_minus1": float(np.sqrt(np.average((Y + X) ** 2, weights=W)))}
    sad = [snaps[t]["saddle"] for t in tags]
    out["saddle"] = {"full_below_alone": int(sum(s["alone_minus_full"] > 0 for s in sad)), "n": len(sad),
                     "alone_minus_full_median": float(np.median([s["alone_minus_full"] for s in sad])),
                     "full_over_alone_median": float(np.median([s["full_over_alone"] for s in sad])),
                     "full_over_alone_range": [float(min(s["full_over_alone"] for s in sad)),
                                               float(max(s["full_over_alone"] for s in sad))]}
    # rate ordering: full vs alone at the same level, normalised by the level
    out["km_level"] = KM_LEVEL
    kmd = {}
    for c in CONDS:
        rows = [r for t in tags for r in by.get((t, c, KM_LEVEL), [])]
        kmd[c] = km([r["t_run"] for r in rows], [not r["censored"] for r in rows], 300.0)
    out["km"] = {c: {k: v for k, v in kmd[c].items() if k != "curve"} for c in CONDS}
    pf, pa = pc["full"], pc["alone"]
    out["headline"] = {
        "events_full": pf["events"], "events_frozen": pc["frozen"]["events"], "events_alone": pa["events"],
        "weib_all": out["weibull_all"]["k"], "weib_all_lo": out["weibull_all"]["ci95"][0],
        "weib_all_hi": out["weibull_all"]["ci95"][1],
        "weib_full": pf["weibull"]["k"], "weib_frozen": pc["frozen"]["weibull"]["k"], "weib_alone": pa["weibull"]["k"],
        "ratio_med_full": pf["ratio_median"], "ratio_med_frozen": pc["frozen"]["ratio_median"],
        "ratio_med_alone": pa["ratio_median"],
        "ratio_cover_full": pf["ratio_ci_covers_1"], "nfit_full": pf["n_arrhenius_fits"],
        "ratio_cover_frozen": pc["frozen"]["ratio_ci_covers_1"], "nfit_frozen": pc["frozen"]["n_arrhenius_fits"],
        "ratio_cover_alone": pa["ratio_ci_covers_1"], "nfit_alone": pa["n_arrhenius_fits"],
        "collapse_slope": sl, "saddle_below": out["saddle"]["full_below_alone"], "saddle_n": len(sad),
        "saddle_ratio_med": out["saddle"]["full_over_alone_median"],
    }
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    fig = {"km_level": KM_LEVEL, "km": {c: kmd[c]["curve"] for c in CONDS},
           "collapse": [{k: p[k] for k in ("cond", "level", "x", "y")} for p in collapse]}
    json.dump(fig, open(FIG4, "w"), indent=1)
    brief(out, tags)


def brief(o, tags):
    for t in tags:
        s = o["snapshots"][t]
        line = [f"{t:12s} n={s['n_resid']} sad={s['saddle']['full_over_alone']:.2f}"]
        for c in CONDS:
            if c not in s["conds"]:
                line.append(f"{c}: -")
                continue
            cc = s["conds"][c]
            ev = "/".join(str(cc["levels"][lk(L)]["events"]) for L in LEVELS)
            a = cc["arrhenius"]
            line.append(f"{c} dU={cc['dU']:.1f} ev={ev} r=" + (f"{a['ratio']:.2f}[{a['ratio_ci95'][0]:.2f},{a['ratio_ci95'][1]:.2f}] nu={a['nu_hat']:.3f}" if a else "-"))
        print(" | ".join(line))
    for c, p in o["per_condition"].items():
        print(c, "events", p["events"], "Weibull", round(p["weibull"]["k"], 3), p["weibull"]["ci95"],
              "ratio median", p["ratio_median"], "covers1", p["ratio_ci_covers_1"], "/", p["n_arrhenius_fits"],
              "nu median", p["nu_hat_median"])
    print("Weibull all", o["weibull_all"], "collapse", o["collapse_fit"], "saddle", o["saddle"])
    print("KM medians", {c: v["median"] for c, v in o["km"].items()})


if __name__ == "__main__":
    main()
