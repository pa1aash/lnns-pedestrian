"""P4: the stall prediction, the time-step prediction and the escape figure with energy-span barriers.

Barrier list. The 56 accepted full-condition library barriers (experiments/E6/analyze.py reported_barriers), with
each affected path's reported barrier replaced by its energy span (data/derived/rev5_X1.json paths[<snap>|full]
dU_span where affected, as in experiments/revision5/X1_analyze.py rean_E4); 8 of the 56 change.

Outputs (data/derived/rev6_P4.json):
  stall      experiments/E6/analyze.barrier_picture(sigma*, nu, barriers) with the span list; nu is the median
             full-condition attempt rate of E4 (identical with the span: X1 per_condition_span.full.nu_hat_median).
             The agreement statistic is the one in E6_analysis.json lifetimes.pred_vs_obs.max_abs_diff: the maximum,
             over t = 30, 60, 120 and 300 s, of |S_pred(t) - S_KM(t)|, with S_KM the Kaplan-Meier survival of the
             observed noise stalls (unchanged; read from E6_analysis.json) and S_pred the barrier mixture
             conditioned on lasting >= 10 s. The reported-barrier values are recomputed alongside and must equal
             the published ones exactly.
  E3         experiments/E3/analyze.py re-run with the span (X1_analyze.rean_E3): predicted and observed pooled ell
             at beta_0 = 1.5 and 2.5.
  E4         experiments/E4/analyze.py re-run with the span (X1_analyze.rean_E4): the inputs of fig_escape_dt.
Scratch outputs of the re-runs (E4_analysis_span.json, fig4_span.json, E3_analysis_span.json, fig5_span.json) go to
data/revision6/P4/; figures/fig_escape_dt.py reads E4_analysis_span.json and fig5_span.json from there.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DER = os.path.join(ROOT, "data", "derived")
OUTDIR = os.path.join(ROOT, "data", "revision6", "P4")
OUT = os.path.join(DER, "rev6_P4.json")


def load_e6():
    spec = importlib.util.spec_from_file_location("E6analyze", os.path.join(ROOT, "experiments", "E6", "analyze.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def span_barriers(e6=None):
    """The reported list with the energy span in place of the reported barrier for the affected full paths."""
    e6 = e6 or load_e6()
    X1 = json.load(open(os.path.join(DER, "rev5_X1.json")))["paths"]
    out, changed = [], []
    for snap, dU in e6.reported_barriers():
        p = X1[f"{snap}|full"]
        assert abs(p["dU_published"] - dU) <= 1e-12 * max(1.0, abs(dU)), (snap, dU, p["dU_published"])
        if p["affected"]:
            changed.append({"snap": snap, "dU_rep": dU, "dU_span": p["dU_span"]})
            dU = p["dU_span"]
        out.append((snap, dU))
    return out, changed


def stall(e6):
    E6 = json.load(open(os.path.join(DER, "E6_analysis.json")))
    L = E6["lifetimes"]
    sigma, nu = L["barrier_picture"]["sigma"], L["barrier_picture"]["nu_full_median"]
    S_obs = dict(zip(map(str, L["pred_vs_obs"]["t"]), L["pred_vs_obs"]["S_obs_km"]))
    res = {}
    span, changed = span_barriers(e6)
    for name, bl in (("reported", None), ("span", span)):
        bp = e6.barrier_picture(sigma, nu, bl)
        diffs = {t: bp["pred_S_at"][t] - S_obs[t] for t in S_obs}
        res[name] = {k: v for k, v in bp.items() if k != "rows"}
        res[name]["diff_pred_minus_obs"] = diffs
        res[name]["max_abs_diff"] = max(abs(v) for v in diffs.values())
        res[name]["argmax_t"] = max(diffs, key=lambda t: abs(diffs[t]))
        res[name]["median_obs_km_s"] = L["pred_vs_obs"]["median_obs_km_s"]
    rep, pub = res["reported"], L["barrier_picture"]
    assert rep["pred_S_at"] == pub["pred_S_at"] and rep["max_abs_diff"] == L["pred_vs_obs"]["max_abs_diff"]
    res["changed"] = changed
    res["S_obs_km"] = S_obs
    res["statistic"] = ("max over t in {30, 60, 120, 300} s of |S_pred(t) - S_KM(t)| (E6_analysis.json "
                        "lifetimes.pred_vs_obs.max_abs_diff)")
    return res


def fix_fig5_pred(sub3):
    """Predicted curves of fig5_span.json, normalised at dt = 0.01 s.

    E3/analyze.fig5_cache writes ln(pred) = beta_ref - dU_i / k_BT_eff(sigma_i, dt), which equals
    dU_i (1/k_BT_eff(0.01) - 1/k_BT_eff(dt)) only while beta_ref = dU_i / k_BT_eff(0.01). With the span substituted
    that identity fails for the substituted snapshot, so beta_ref is replaced by beta_ref * dU_span / dU_rep for it.
    Check: the same formula with no substitution reproduces figures/data/fig5.json to 1e-12.
    """
    import numpy as np
    sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
    from teff import kT_eff
    path = os.path.join(OUTDIR, "fig5_span.json")
    d = json.load(open(path))
    pub = json.load(open(os.path.join(ROOT, "figures", "data", "fig5.json")))
    S = json.load(open(os.path.join(OUTDIR, "E3_analysis_span.json")))["snapshots"]
    grid = np.array(d["grid"])
    maxdev = 0.0
    for mode in ("per_step", "dt_scaled"):
        for L in (1.5, 2.5):
            key = f"b{L:g}".replace(".", "p")
            T = [t for t in S if S[t]["beta_ref"] == L]
            P, P0 = [], []
            for t in T:
                f = sub3[t][1] / sub3[t][0] if t in sub3 else 1.0
                dU0 = S[t]["dU_i"] / f
                P.append([L * f - S[t]["dU_i"] / kT_eff(S[t]["sigma_i"], g, S[t]["tau_b"], mode=mode) for g in grid])
                P0.append([L - dU0 / kT_eff(S[t]["sigma_i"], g, S[t]["tau_b"], mode=mode) for g in grid])
            maxdev = max(maxdev, float(np.max(np.abs(np.exp(np.mean(P0, 0)) - np.array(pub[mode][key]["pred"])))))
            d[mode][key]["pred"] = np.exp(np.mean(P, 0)).tolist()
    assert maxdev < 1e-12, maxdev
    json.dump(d, open(path, "w"), indent=1)
    return maxdev


def reanalyses():
    sys.path.insert(0, os.path.join(ROOT, "experiments", "revision5"))
    import X1_analyze as X
    os.makedirs(OUTDIR, exist_ok=True)
    X.REAN = OUTDIR
    _, P = X.load_paths()
    e4s, sub4 = X.rean_E4(P)
    e3s, sub3 = X.rean_E3(P)
    dev = fix_fig5_pred(sub3)
    h = e3s["headline"]
    E3p = json.load(open(os.path.join(DER, "E3_analysis.json")))["headline"]
    keys = ("ell_ps_b1p5_obs", "ell_ps_b1p5_lo", "ell_ps_b1p5_hi", "ell_ps_b1p5_pred",
            "ell_ps_b2p5_obs", "ell_ps_b2p5_lo", "ell_ps_b2p5_hi", "ell_ps_b2p5_pred", "ell_ds_obs", "ell_ds_pred")
    return {"E3": {"substituted": sub3, "published": {k: E3p[k] for k in keys}, "span": {k: h[k] for k in keys},
                   "fig5_pred_reproduction_maxdev": dev},
            "E4": {"substituted": sub4, "ratio_med_full_span": e4s["per_condition"]["full"]["ratio_median"],
                   "nu_full_median_span": e4s["per_condition"]["full"]["nu_hat_median"]}}


def main():
    e6 = load_e6()
    o = {"doc": __doc__, "stall": stall(e6)}
    o.update(reanalyses())
    s = o["stall"]
    o["headline"] = {"stall_max_abs_diff_rep": s["reported"]["max_abs_diff"],
                     "stall_max_abs_diff_span": s["span"]["max_abs_diff"],
                     "stall_argmax_t_span": s["span"]["argmax_t"],
                     "stall_pred_median_span": s["span"]["pred_median_lifetime_s"],
                     "stall_pred_median_rep": s["reported"]["pred_median_lifetime_s"],
                     "stall_obs_median": s["span"]["median_obs_km_s"],
                     "stall_n_changed": len(s["changed"]),
                     "ell_b1p5_pred_span": o["E3"]["span"]["ell_ps_b1p5_pred"],
                     "ell_b1p5_pred_rep": o["E3"]["published"]["ell_ps_b1p5_pred"],
                     "ell_b2p5_pred_span": o["E3"]["span"]["ell_ps_b2p5_pred"]}
    with open(OUT, "w") as f:
        json.dump(o, f, indent=1, default=float)
    for k, v in o["headline"].items():
        print(k, v)
    print("S_pred span", s["span"]["pred_S_at"], "S_obs", s["S_obs_km"])


if __name__ == "__main__":
    main()
