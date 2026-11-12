"""A7: Arrhenius slope ratios with a temperature taken along the unstable mode instead of the blocker's.

Inputs (existing data only; no dynamics is run):
  data/derived/E4_analysis.json   per (snapshot, condition, level) rates, events, sigma, blocker k_BT_eff, fits
  data/derived/fix_a3.json        unit unstable eigenvector of the saddle Hessian of U (full condition), agent
                                  weights p_i = |e_i|^2 (2 components per agent; equal masses, so mass weighting
                                  does not change it), and the dynamic (Langer) unstable mode's weights
  data/derived/selection.json + data/E1/library/<tag>.pkl   per-agent tau_i (agent order [blocker] + others,
                                  as fix_a3 and experiments/BAR/bar.py)
  experiments/revision/A4_ratio_trend.py   the fit list and the regressions of the ratio on ln dU (A4)
  data/derived/rev_B3.json        B3 ratios (alone condition)

Rule. Every agent receives the same per-step sigma, so its effective temperature (experiments/lib/teff.py,
Eq. (10), dt = 0.01 s, m = 80 kg) is k_BT_eff(tau_i) = m sigma^2 / (1 - (1 - dt/tau_i)^2). Along the unstable
mode the temperature is the weighted sum
    k_BT_mode = sum_i p_i k_BT_eff(tau_i),   p_i = e_{i,x}^2 + e_{i,y}^2,  sum_i p_i = 1,
(the variance of the projection of independent agent velocities on the unit unstable direction, times m).
Since sigma is common, k_BT_mode = c k_BT_blocker with c = sum_i p_i k_BT_eff(tau_i) / k_BT_eff(tau_b), the same
at every level of a fit. The abscissa 1/k_BT of the E4 fit becomes (1/c) / k_BT_blocker, so the slope and the
ratio r = -slope / dU scale exactly by c (r_mode = c r, interval likewise), and the levels become
beta_mode = beta / c.
Conditions: full (all residual agents mobile): c from the Hessian eigenvector (headline) and from the dynamic
Langer mode (check). Pinned ("frozen"): only the blocker is mobile (the neighbours are reset to their snapshot
positions every step, so their noise does not enter), p_b = 1 and c = 1 exactly. Alone: one agent, c = 1. B3 is
the alone condition: unchanged.
Then the per-condition and pooled median ratios and the A4 regressions of r on ln(dU / J) (OLS, snapshot bootstrap
4000 draws, PCG64(20261110) as A4; pooled with common intercept and with one intercept per condition; full alone)
are recomputed with r_mode, next to the blocker-temperature values (reproduced from A4).
Output: data/derived/rev2_A7.json
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import DERIVED, ROOT, np, sig  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
from teff import kT_eff  # noqa: E402
import A4_ratio_trend as A4  # noqa: E402  (experiments/revision on the path via rev2lib)

DT = 0.01
CONDS = ("full", "frozen", "alone")


def summ(v):
    v = np.asarray(v, float)
    return {"n": int(len(v)), "min": float(v.min()), "median": float(np.median(v)), "max": float(v.max())}


def regressions(F):
    rng = np.random.default_rng(A4.RNG)
    out = {}
    for name, model, cond in (("full", "per_condition", "full"), ("pooled_cond_int", "pooled_cond_int", None),
                              ("pooled_common", "pooled_common", None)):
        o = A4.analyse(F, model, cond, rng)
        out[name] = {"n_fits": o["n_fits"], "b": o["ols_b"], "b_ci95": o["ols_boot_snap"]["ci95"],
                     "frac_b_below_0": o["ols_boot_snap"]["frac_b_below_0"],
                     "spearman_rho": o["spearman"]["rho"], "spearman_p": o["spearman"]["p"],
                     "per_decade": o["per_decade"]}
    return out


def main():
    t0 = time.process_time()
    E4 = json.load(open(os.path.join(DERIVED, "E4_analysis.json")))["snapshots"]
    FA = json.load(open(os.path.join(DERIVED, "fix_a3.json")))["langer"]["per_snapshot"]
    sel = {s["tag"]: s for s in json.load(open(os.path.join(DERIVED, "selection.json")))["E4"]["snapshots"]}
    G = {r["job_id"]: r for r in rev2lib.revlib.load_runs(os.path.join(ROOT, "data", "BAR", "gate.jsonl"))}
    rows = {}
    for tag, s in E4.items():
        st = pickle.load(open(os.path.join(ROOT, sel[tag]["snap"]), "rb"))["state"]
        b = G[tag]["blocker"]
        ids = [b] + [i for i in G[tag]["resid"] if i != b]
        taus = st.taus[ids].astype(float)
        sg = s["conds"]["full"]["levels"]["b1p5"]["sigma"] if "full" in s["conds"] else 0.05
        kti = np.array([kT_eff(sg, DT, t) for t in taus])
        row = {"ids": ids, "taus_s": taus.tolist(), "kT_rel_to_blocker": (kti / kti[0]).tolist()}
        fl = FA[tag]["full"]
        for mode in ("unstable_mode_hessian", "unstable_mode_dynamic"):
            p = np.array(fl[mode]["weights"]) if mode in fl else None
            row["c_" + mode.split("_")[-1]] = float(p @ kti / kti[0]) if p is not None else None
            row["p_" + mode.split("_")[-1]] = p.tolist() if p is not None else None
        for c in CONDS:
            cc = s["conds"].get(c)
            a = cc.get("arrhenius") if cc else None
            fac = row["c_hessian"] if c == "full" else 1.0
            row[c] = {"c": fac, "dU": cc["dU"] if cc else None,
                      "beta_mode_levels": [L / fac for L in (1.5, 2.5, 3.5)] if fac else None,
                      "ratio_blocker": a["ratio"] if a else None,
                      "ratio_mode": a["ratio"] * fac if a else None,
                      "ratio_mode_dynamic": a["ratio"] * row["c_dynamic"] if (a and c == "full") else (a["ratio"] if a else None),
                      "ci_blocker": a["ratio_ci95"] if a else None,
                      "ci_mode": [v * fac for v in a["ratio_ci95"]] if a else None}
            # check: the fit recomputed with 1/k_BT_mode reproduces c * r
            if a:
                L = [cc["levels"][k] for k in ("b1p5", "b2p5", "b3p5")]
                d = np.array([x["events"] for x in L], float)
                T = np.array([x["exposure_s"] for x in L])
                x = 1.0 / (fac * np.array([x["kT_eff"] for x in L]))
                sl, _ = _wls(x, np.log(d / T), d)
                row[c]["ratio_mode_refit"] = -sl / cc["dU"]
        rows[tag] = row
    out = {"doc": __doc__, "rows": rows}
    full = [r["full"] for r in rows.values() if r["full"]["ratio_blocker"] is not None]
    cs = [r["c_hessian"] for r in rows.values() if r["c_hessian"] is not None]
    csf = [r["c"] for r in full]
    allb = [r[c]["ratio_blocker"] for r in rows.values() for c in CONDS if r[c]["ratio_blocker"] is not None]
    allm = [r[c]["ratio_mode"] for r in rows.values() for c in CONDS if r[c]["ratio_mode"] is not None]
    cover_b = sum(r["ci_blocker"][0] <= 1 <= r["ci_blocker"][1] for r in full)
    cover_m = sum(r["ci_mode"][0] <= 1 <= r["ci_mode"][1] for r in full)
    # A4 regressions, blocker temperature (reproduces A4) and mode temperature
    F = A4.fits()
    Fm = []
    for f in F:
        g = dict(f)
        if f["cond"] == "full":
            k = rows[f["snap"]]["c_hessian"]
            g.update(r=f["r"] * k, lo=f["lo"] * k, hi=f["hi"] * k, se=f["se"] * k, ikT=[v / k for v in f["ikT"]])
        Fm.append(g)
    reg_b, reg_m = regressions(F), regressions(Fm)
    A4o = json.load(open(os.path.join(DERIVED, "rev_A4.json")))
    out["regressions"] = {"blocker": reg_b, "mode": reg_m,
                          "check_A4_pooled_common_b": A4o["pooled_common"]["ols_b"],
                          "check_A4_full_b": A4o["per_condition"]["full"]["ols_b"]}
    B3 = json.load(open(os.path.join(DERIVED, "rev_B3.json")))["snapshots"]
    out["b3"] = {t: {"ratio_1p5_7": v["fit_1p5_7"]["ratio"], "c": 1.0, "ratio_mode": v["fit_1p5_7"]["ratio"]}
                 for t, v in B3.items()}
    out["summary"] = {
        "c_all_snapshots": summ(cs), "c_fitted_full": summ(csf),
        "c_dynamic_fitted_full": summ([rows[t]["c_dynamic"] for t in rows if rows[t]["full"]["ratio_blocker"] is not None]),
        "beta_mode_full_min": float(min(1.5 / r["c"] for r in full)), "beta_mode_full_max": float(max(3.5 / r["c"] for r in full)),
        "full_ratio_blocker": summ([r["ratio_blocker"] for r in full]),
        "full_ratio_mode": summ([r["ratio_mode"] for r in full]),
        "full_ratio_mode_dynamic": summ([r["ratio_mode_dynamic"] for r in full]),
        "full_cover1_blocker": int(cover_b), "full_cover1_mode": int(cover_m), "n_full_fits": len(full),
        "all_ratio_blocker": summ(allb), "all_ratio_mode": summ(allm),
        "max_refit_dev": float(max(abs(r[c]["ratio_mode_refit"] - r[c]["ratio_mode"]) for r in rows.values()
                                   for c in CONDS if r[c]["ratio_blocker"] is not None)),
    }
    S, Rb, Rm = out["summary"], reg_b, reg_m
    out["headline"] = {
        "c_min": S["c_fitted_full"]["min"], "c_med": S["c_fitted_full"]["median"], "c_max": S["c_fitted_full"]["max"],
        "cdyn_min": S["c_dynamic_fitted_full"]["min"], "cdyn_max": S["c_dynamic_fitted_full"]["max"],
        "n_full": len(full),
        "full_med_b": S["full_ratio_blocker"]["median"], "full_med_m": S["full_ratio_mode"]["median"],
        "full_min_m": S["full_ratio_mode"]["min"], "full_max_m": S["full_ratio_mode"]["max"],
        "full_cover_b": int(cover_b), "full_cover_m": int(cover_m),
        "all_med_b": S["all_ratio_blocker"]["median"], "all_med_m": S["all_ratio_mode"]["median"],
        "n_all": S["all_ratio_mode"]["n"],
        "pool_b_b": Rb["pooled_common"]["b"], "pool_b_m": Rm["pooled_common"]["b"],
        "pool_b_m_lo": Rm["pooled_common"]["b_ci95"][0], "pool_b_m_hi": Rm["pooled_common"]["b_ci95"][1],
        "pool_b_b_lo": Rb["pooled_common"]["b_ci95"][0], "pool_b_b_hi": Rb["pooled_common"]["b_ci95"][1],
        "condint_b_b": Rb["pooled_cond_int"]["b"], "condint_b_m": Rm["pooled_cond_int"]["b"],
        "condint_b_m_lo": Rm["pooled_cond_int"]["b_ci95"][0], "condint_b_m_hi": Rm["pooled_cond_int"]["b_ci95"][1],
        "fullreg_b_b": Rb["full"]["b"], "fullreg_b_m": Rm["full"]["b"],
        "fullreg_b_m_lo": Rm["full"]["b_ci95"][0], "fullreg_b_m_hi": Rm["full"]["b_ci95"][1],
    }
    out["cpu_s"] = time.process_time() - t0
    for t, r in rows.items():
        print(f"{t:12s} taus={np.round(r['taus_s'], 3).tolist()} p={np.round(r['p_hessian'], 2).tolist()} "
              f"c={r['c_hessian']:.3f} cdyn={r['c_dynamic']:.3f} r_full={r['full']['ratio_blocker']} -> {r['full']['ratio_mode']}")
    print(json.dumps(out["headline"], indent=0))
    print(rev2lib.out_json("A7", out), out["cpu_s"])


def _wls(x, y, w):
    W = w.sum()
    xm, ym = (w * x).sum() / W, (w * y).sum() / W
    s = (w * (x - xm) * (y - ym)).sum() / (w * (x - xm) ** 2).sum()
    return s, ym - s * xm


if __name__ == "__main__":
    main()
