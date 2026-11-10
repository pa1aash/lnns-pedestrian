"""A3: beta = Delta U / k_B T_eff of the library barriers at the fraction-matched noise levels.

Barriers: the gate-accepted full (all residual agents mobile) lone-trap barriers, data/BAR/gate.jsonl
(experiments/BAR/gate.py), field full.accepted and full.dU > 0 (the 56 of macro LoneBarN; same rule as
barrier_picture in experiments/E6/analyze.py). Each barrier uses its own blocker's relaxation time tau (the
E1b run record's attrs, data/E1/E1_runs.jsonl; blocker id from gate.jsonl). Stratum (lone keystone, second
trap) from data/derived/selection.json "E2".
Temperature: Eq. (10), k_B T_eff = m sigma^2 / (1 - (1 - dt/tau)^2), dt = 0.01 s, m = 80 kg
(experiments/lib/teff.py kT_eff, per-step noise).
Noise levels: sigma = 0.07 m/s (fraction-matched at T = 120 s, lone trap, Sect. 6.1.2), 0.0717 m/s (refined
level, data/derived/N1_analysis.json sigma_n1) and sigma* = 0.0467 m/s (whole runs, data/derived/
sigma_star.json sigma_star).
Per level: median, quartiles, min, max of beta; fraction with beta < 1 (count and Wilson interval); fraction in
the range beta in [1.5, 3.5] tested by E4 and with beta >= 3.5; pooled and per stratum. Also beta = 1 and
beta = 3 barrier thresholds (Delta U at the median tau) and the fraction of barriers with beta >= 5.
Output: data/derived/rev_A3.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import DATA, DERIVED, load_runs, sig, wilson  # noqa: E402
import numpy as np  # noqa: E402
from teff import kT_eff  # noqa: E402

DT = 0.01


def stats(b):
    b = np.asarray(b, float)
    n = len(b)
    k1 = int((b < 1).sum())
    w = wilson(k1, n)
    return {"n": n, "median": float(np.median(b)), "q25": float(np.percentile(b, 25)),
            "q75": float(np.percentile(b, 75)), "min": float(b.min()), "max": float(b.max()),
            "n_below_1": k1, "frac_below_1": k1 / n, "frac_below_1_ci95": [w[1], w[2]],
            "n_in_1p5_3p5": int(((b >= 1.5) & (b <= 3.5)).sum()), "n_ge_3p5": int((b >= 3.5).sum()),
            "n_ge_5": int((b >= 5).sum()), "frac_ge_5": float((b >= 5).mean()),
            "median_2sf": sig(float(np.median(b)), 2), "q25_2sf": sig(float(np.percentile(b, 25)), 2),
            "q75_2sf": sig(float(np.percentile(b, 75)), 2)}


def main():
    G = load_runs(os.path.join(DATA, "BAR", "gate.jsonl"))
    E1 = {f"{r['mode']}_seed{r['seed']}": r for r in load_runs(os.path.join(DATA, "E1", "E1_runs.jsonl"))}
    cls = {s["tag"]: s["class"] for s in json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]}
    rows = []
    for g in G:
        f = g.get("full", {})
        if not f.get("accepted") or f.get("dU") is None or f["dU"] <= 0:
            continue
        tau = next(a["tau"] for a in E1[g["job_id"]]["attrs"] if a["id"] == g["blocker"])
        rows.append({"snap": g["job_id"], "stratum": cls[g["job_id"]], "dU": f["dU"], "tau": tau})
    levels = {"s0p07": 0.07,
              "s0p0717": json.load(open(os.path.join(DERIVED, "N1_analysis.json")))["sigma_n1"],
              "sstar": json.load(open(os.path.join(DERIVED, "sigma_star.json")))["sigma_star"]}
    o = {"n_barriers": len(rows), "dt": DT, "m": 80.0,
         "dU_median": float(np.median([r["dU"] for r in rows])),
         "tau_median": float(np.median([r["tau"] for r in rows])),
         "tau_range": [min(r["tau"] for r in rows), max(r["tau"] for r in rows)],
         "n_per_stratum": {c: sum(r["stratum"] == c for r in rows) for c in ("lone_keystone", "lone_keystone_second_trap")},
         "levels": {}}
    for name, s in levels.items():
        b = []
        for r in rows:
            kT = kT_eff(s, DT, r["tau"])
            r[f"kT_{name}"] = kT
            r[f"beta_{name}"] = r["dU"] / kT
            b.append(r["dU"] / kT)
        kT_med = kT_eff(s, DT, o["tau_median"])
        L = {"sigma": s, "kT_eff_median": float(np.median([r[f"kT_{name}"] for r in rows])),
             "dU_at_beta1_median_tau": kT_med, "dU_at_beta3_median_tau": 3 * kT_med,
             "pooled": stats(b)}
        for c, lab in (("lone_keystone", "keystone"), ("lone_keystone_second_trap", "second")):
            L[lab] = stats([r[f"beta_{name}"] for r in rows if r["stratum"] == c])
        o["levels"][name] = L
    o["check_E6_beta_median_sstar"] = json.load(open(os.path.join(DERIVED, "E6_analysis.json")))[
        "lifetimes"]["barrier_picture"]["beta_median"]
    o["rows"] = rows
    revlib.out_json("A3", o)
    for name, L in o["levels"].items():
        print(name, L["sigma"], "kT med %.2f" % L["kT_eff_median"],
              {k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in L[k].items()
                   if kk in ("n", "median", "q25", "q75", "n_below_1", "frac_below_1", "n_ge_3p5", "n_ge_5")}
               for k in ("pooled", "keystone", "second")})
    print("E6 check", o["check_E6_beta_median_sstar"], o["levels"]["sstar"]["pooled"]["median"], o["n_per_stratum"])


if __name__ == "__main__":
    main()
