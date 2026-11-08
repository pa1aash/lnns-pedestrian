"""E6 analysis: matched completion of whole runs and the signatures that separate the matched pair.

Inputs: data/E6/e6a.jsonl (C3 RVO2, CF), data/E6/e6b.jsonl (C1 + sigma*, CF), same seeds 242-427;
data/E6/keystone.jsonl (experiments/E6/keystone_e6.py: keystone surgery on the rebuilt final states);
data/derived/sigma_star.json; data/BAR/gate.jsonl and data/E1/E1_runs.jsonl (barrier picture);
data/derived/E4_analysis.json (attempt rate).

Output: data/derived/E6_analysis.json.
  completion     per arm k/n with Wilson 95% intervals; paired difference (C1 + sigma* minus C3 RVO2) with the
                 Newcombe paired score interval (method 10) at 95% and 90%; internal agreement check against the
                 +-0.15 margin that set n = 186 (90% interval inside the margin; kept in the JSON only).
  identity       paired 2x2 table of failures, exact McNemar p, Jaccard of the two failure sets with a seed
                 bootstrap 95% interval (10 000 resamples), and the Jaccard expected if failures were independent
                 at the observed rates (seed permutation of one arm, 10 000 permutations).
  time           Kaplan-Meier of completion time per arm (failures censored at 600 s), log-rank test; on seeds
                 both complete: paired times, Wilcoxon signed-rank, fraction where C3 RVO2 is faster.
  failure_state  how each failure ended (stationary deadlock or still moving at 600 s, speed at the end), the
                 residual size, and the keystone class of the rebuilt final state (lone keystone, with a second
                 trap, collective); whether the residual is a C1 fixed point (K0) and whether C3 RVO2 holds its own
                 residual from rest (K0c); class table compared between arms by a permutation test.
  lifetimes      C1 + sigma*: stalls = intervals of >= 10 s without an exit (10 s is the deadlock detector's
                 hold time); lifetime = interval length; the stall still open at 600 s is censored. Kaplan-Meier,
                 censored Weibull shape. Barrier picture (Sect. 5.4): each accepted collective (full) barrier of the
                 60 corrected-forward library snapshots (data/BAR/gate.jsonl) with k_BT_eff from sigma* and its
                 blocker's tau and the median full-condition attempt rate of E4 gives an exponential lifetime;
                 their mixture, conditioned on lasting >= 10 s, predicts the fraction of stalls still open at 600 s
                 and the median lifetime.
"""
import json
import math
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "E3"))
from survival import km, weibull_pool  # noqa: E402
from teff import kT_eff  # noqa: E402

DATA = os.path.join(ROOT, "data")
DER = os.path.join(DATA, "derived")
OUT = os.path.join(DER, "E6_analysis.json")
T_MAX = 600.0
STALL = 10.0
CHECK_T = (30, 60, 120, 300)
MARGIN = 0.15
B = 10000
RNG = np.random.default_rng(2026)
DOOR = np.array([10.0, 5.0])


def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def newcombe_paired(a, b, c, d, z):
    """Newcombe (1998) method 10: CI for p1 - p2 from a paired 2x2 table.
    a = both succeed, b = arm 1 only, c = arm 2 only, d = neither; p1 = (a+b)/n, p2 = (a+c)/n."""
    n = a + b + c + d
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, z)
    l2, u2 = wilson(a + c, n, z)
    dd = p1 - p2
    num = a * d - b * c
    den = (a + b) * (c + d) * (a + c) * (b + d)
    phi = 0.0 if den == 0 else (max(num - n / 2, 0) if num > 0 else num) / math.sqrt(den)
    lo = dd - math.sqrt(max((p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2, 0))
    hi = dd + math.sqrt(max((u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2, 0))
    return dd, lo, hi


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def jaccard(fa, fb):
    u = fa | fb
    return len(fa & fb) / len(u) if u else float("nan")


def logrank(t1, e1, t2, e2):
    t = np.concatenate([t1, t2])
    e = np.concatenate([e1, e2]).astype(bool)
    g = np.concatenate([np.zeros(len(t1)), np.ones(len(t2))])
    O = E = V = 0.0
    for ti in np.unique(t[e]):
        at = t >= ti
        n, n1 = at.sum(), (at & (g == 0)).sum()
        d = ((t == ti) & e).sum()
        d1 = ((t == ti) & e & (g == 0)).sum()
        O += d1
        E += d * n1 / n
        if n > 1:
            V += d * (n1 / n) * (1 - n1 / n) * (n - d) / (n - 1)
    chi2 = (O - E) ** 2 / V
    return {"chi2": float(chi2), "p": float(stats.chi2.sf(chi2, 1)), "observed_C3": float(O), "expected_C3": float(E)}


def km_summary(times, events):
    k = km(times, events, T_MAX)
    k.pop("curve", None)
    return k


def stalls(r):
    """Intervals >= STALL s without an exit; returns (lifetimes, censored flags)."""
    t = sorted(r["exit_t"].values())
    edges = [0.0] + t
    life, cens = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        if b - a >= STALL and a > 0:          # the first gap (walking to the door) is not a stall
            life.append(b - a)
            cens.append(False)
    if not r["complete"]:
        a = edges[-1]
        if r["t_end"] - a >= STALL:
            life.append(r["t_end"] - a)
            cens.append(True)
    return life, cens


def classify(res, tag):
    k1, k2 = res.get(tag + "|K1"), res.get(tag + "|K2")
    if not k1 or not k2:
        return None
    if not k1["held"]:
        return "collective"
    return "lone_keystone_second_trap" if k2["held"] else "lone_keystone"


def geometry(r, b):
    pos = {int(x["id"]): np.array(x["pos"]) for x in r["residual"]}
    p = pos[b]
    return {"blocker_dx_door": float(p[0] - 10.0), "blocker_dy": float(p[1] - 5.0),
            "n_within_1m": int(sum(np.linalg.norm(q - DOOR) < 1.0 for q in pos.values()))}


def perm_table_test(labels_a, labels_b, n_perm=B):
    cats = sorted(set(labels_a) | set(labels_b))
    allv = np.array(labels_a + labels_b)
    na = len(labels_a)

    def stat(x):
        A, Bb = x[:na], x[na:]
        tab = np.array([[np.sum(A == c) for c in cats], [np.sum(Bb == c) for c in cats]], float)
        exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
        return float(np.sum((tab - exp) ** 2 / np.where(exp > 0, exp, 1)))
    s0 = stat(allv)
    cnt = sum(stat(RNG.permutation(allv)) >= s0 - 1e-12 for _ in range(n_perm))
    return {"chi2": s0, "p_perm": (cnt + 1) / (n_perm + 1), "categories": cats}


def barrier_picture(sigma, nu):
    G = jl(os.path.join(DATA, "BAR", "gate.jsonl"))
    E1 = {f"{r['mode']}_seed{r['seed']}": r for r in jl(os.path.join(DATA, "E1", "E1_runs.jsonl"))}
    rows = []
    for g in G:
        f = g.get("full", {})
        if not f.get("accepted") or f.get("dU") is None or f["dU"] <= 0:
            continue
        run = E1.get(g["job_id"])
        tau = None
        if run and run.get("attrs"):
            tau = next((a["tau"] for a in run["attrs"] if a["id"] == g["blocker"]), None)
        tau = tau or 0.5
        kT = kT_eff(sigma, 0.01, tau)
        rows.append({"snap": g["job_id"], "dU": f["dU"], "tau": tau, "kT": kT, "beta": f["dU"] / kT,
                     "rate": nu * math.exp(-f["dU"] / kT)})
    lam = np.array([x["rate"] for x in rows])

    def S(t):                                   # survival conditioned on lasting >= STALL
        return float(np.mean(np.exp(-lam * t)) / np.mean(np.exp(-lam * STALL)))
    lo, hi = STALL, 1e7
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        lo, hi = (mid, hi) if S(mid) > 0.5 else (lo, mid)
    return {"n_barriers": len(rows), "nu_full_median": nu, "sigma": sigma,
            "kT_eff_median": float(np.median([x["kT"] for x in rows])),
            "dU_median": float(np.median([x["dU"] for x in rows])),
            "beta_median": float(np.median([x["beta"] for x in rows])),
            "pred_S_at": {str(t): S(t) for t in CHECK_T},
            "pred_median_lifetime_s": float(math.sqrt(lo * hi)) if S(T_MAX * 100) < 0.5 else None,
            "pred_frac_rate_below_1_per_600s": float(np.mean(lam * T_MAX < 1)),
            "rows": rows}


def main():
    A = {r["seed"]: r for r in jl(os.path.join(DATA, "E6", "e6a.jsonl"))}
    Bn = {r["seed"]: r for r in jl(os.path.join(DATA, "E6", "e6b.jsonl"))}
    seeds = sorted(A)
    assert seeds == sorted(Bn) and len(seeds) == 186
    S = json.load(open(os.path.join(DER, "sigma_star.json")))
    sigma = S["sigma_star"]
    ca = np.array([A[s]["complete"] for s in seeds], bool)
    cb = np.array([Bn[s]["complete"] for s in seeds], bool)
    n = len(seeds)
    o = {"script": "experiments/E6/analyze.py", "n": n, "seeds": [seeds[0], seeds[-1]], "sigma_star": sigma,
         "arms": {"C3_rvo2": "E6a: C3, RVO2 ORCA, corrected-forward", "C1_sigma": "E6b: C1 + sigma*, corrected-forward"}}

    # --- completion
    comp = {}
    for nm, c in (("C3_rvo2", ca), ("C1_sigma", cb)):
        k = int(c.sum())
        lo, hi = wilson(k, n)
        comp[nm] = {"k": k, "n": n, "rate": k / n, "wilson95": [lo, hi]}
    a = int((cb & ca).sum())
    b_ = int((cb & ~ca).sum())
    c_ = int((~cb & ca).sum())
    d = int((~cb & ~ca).sum())
    d95 = newcombe_paired(a, b_, c_, d, 1.959963984540054)
    d90 = newcombe_paired(a, b_, c_, d, 1.6448536269514722)
    comp["diff_sigma_minus_C3"] = {"diff": d95[0], "ci95": [d95[1], d95[2]], "ci90": [d90[1], d90[2]],
                                   "method": "Newcombe paired score interval (method 10)"}
    comp["agreement_check_internal"] = {"margin": MARGIN, "ci90_inside_margin": bool(-MARGIN < d90[1] and d90[2] < MARGIN),
                                        "note": "internal only (sets n = 186); the text states the agreement plainly"}
    o["completion"] = comp

    # --- identity
    fa = {s for s in seeds if not A[s]["complete"]}
    fb = {s for s in seeds if not Bn[s]["complete"]}
    J = jaccard(fa, fb)

    bs = []
    for _ in range(B):
        idx = RNG.integers(0, n, n)
        # resampled seeds keep their multiplicity: count over the resampled index list
        fa_i, fb_i = ~ca[idx], ~cb[idx]
        u = (fa_i | fb_i).sum()
        bs.append((fa_i & fb_i).sum() / u if u else np.nan)
    perm = []
    for _ in range(B):
        pb = RNG.permutation(~cb)
        u = ((~ca) | pb).sum()
        perm.append(((~ca) & pb).sum() / u)
    o["identity"] = {"both_fail": len(fa & fb), "C3_only_fail": len(fa - fb), "sigma_only_fail": len(fb - fa),
                     "both_complete": a, "mcnemar_exact_p": mcnemar_exact(len(fa - fb), len(fb - fa)),
                     "jaccard": J, "jaccard_ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
                     "jaccard_independent_mean": float(np.mean(perm)),
                     "jaccard_independent_95": [float(np.percentile(perm, 2.5)), float(np.percentile(perm, 97.5))],
                     "p_perm_jaccard_above_independent": float((np.sum(np.array(perm) >= J) + 1) / (B + 1)),
                     "seeds_fail_C3": sorted(fa), "seeds_fail_sigma": sorted(fb)}


    # --- time
    ta = np.array([A[s]["evacuation_time"] if A[s]["complete"] else T_MAX for s in seeds])
    tb = np.array([Bn[s]["evacuation_time"] if Bn[s]["complete"] else T_MAX for s in seeds])
    both = ca & cb
    w = stats.wilcoxon(ta[both], tb[both])
    o["time"] = {"km_C3_rvo2": km_summary(ta, ca), "km_C1_sigma": km_summary(tb, cb),
                 "logrank": logrank(ta, ca, tb, cb),
                 "completed_median_C3_rvo2": float(np.median(ta[ca])), "completed_median_C1_sigma": float(np.median(tb[cb])),
                 "completed_iqr_C3_rvo2": [float(np.percentile(ta[ca], 25)), float(np.percentile(ta[ca], 75))],
                 "completed_iqr_C1_sigma": [float(np.percentile(tb[cb], 25)), float(np.percentile(tb[cb], 75))],
                 "paired_both_complete_n": int(both.sum()),
                 "paired_median_diff_sigma_minus_C3": float(np.median(tb[both] - ta[both])),
                 "paired_frac_C3_faster": float(np.mean(ta[both] < tb[both])),
                 "paired_C3_faster_n": int(np.sum(ta[both] < tb[both])),
                 "wilcoxon_p": float(w.pvalue),
                 "completed_max_C3_rvo2": float(ta[ca].max()), "completed_max_C1_sigma": float(tb[cb].max()),
                 "completed_after_300s_C3_rvo2": int(np.sum(ta[ca] > 300)),
                 "completed_after_300s_C1_sigma": int(np.sum(tb[cb] > 300))}

    # --- failure state and keystone class
    ksp = os.path.join(DATA, "E6", "keystone.jsonl")
    res = {x["job_id"]: x for x in jl(ksp)} if os.path.exists(ksp) else {}
    fs = {}
    labels = {}
    for nm, D, v in (("C3_rvo2", A, "E6a"), ("C1_sigma", Bn, "E6b")):
        F = [D[s] for s in seeds if not D[s]["complete"]]
        cls, rows = [], []
        for r in F:
            tag = f"{v}|seed{r['seed']}"
            c = classify(res, tag)
            k0, k0c = res.get(tag + "|K0"), res.get(tag + "|K0c")
            spd = max(x["speed"] for x in r["residual"])
            row = {"seed": r["seed"], "n_res": r["n_remaining"], "deadlock": r["deadlock"], "end_speed_max": spd,
                   "class": c, "K0_held_all": (None if not k0 else len(k0["held"]) == len(k0["kept"])),
                   "K0_held_any": (None if not k0 else len(k0["held"]) > 0),
                   "K0c_held_any": (None if not k0c else len(k0c["held"]) > 0)}
            if res.get(tag + "|K1"):
                row.update(geometry(r, res[tag + "|K1"]["blocker"]))
            rows.append(row)
            if c:
                cls.append(c)
        labels[nm] = cls
        cnt = {k: cls.count(k) for k in ("lone_keystone", "lone_keystone_second_trap", "collective")}
        nres = [x["n_res"] for x in rows]
        fs[nm] = {"n_fail": len(F), "stationary_deadlock": sum(x["deadlock"] for x in rows),
                  "moving_at_600s": sum(not x["deadlock"] for x in rows),
                  "end_speed_median_moving": float(np.median([x["end_speed_max"] for x in rows if not x["deadlock"]] or [np.nan])),
                  "n_res_counts": {str(k): nres.count(k) for k in sorted(set(nres))},
                  "n_res_median": float(np.median(nres)),
                  "classified": len(cls), "class_counts": cnt,
                  "K0_C1_held_any": sum(bool(x["K0_held_any"]) for x in rows),
                  "K0c_C3_holds_own_residual": sum(bool(x["K0c_held_any"]) for x in rows if x["K0c_held_any"] is not None),
                  "K0c_tested": sum(x["K0c_held_any"] is not None for x in rows),
                  "rows": rows}
        if v == "E6a":
            dl = [x for x in rows if x["deadlock"]]
            mv = [x for x in rows if not x["deadlock"]]
            fs[nm]["class_counts_deadlock"] = {k: sum(x["class"] == k for x in dl) for k in cnt}
            fs[nm]["class_counts_moving"] = {k: sum(x["class"] == k for x in mv) for k in cnt}
            fs[nm]["n_res_two_moving"] = sum(x["n_res"] == 2 for x in mv)
    if labels["C3_rvo2"] and labels["C1_sigma"]:
        fs["class_test"] = perm_table_test(labels["C3_rvo2"], labels["C1_sigma"])
        for nm in ("C3_rvo2", "C1_sigma"):
            n_ = len(labels[nm])
            for k in ("lone_keystone", "lone_keystone_second_trap", "collective"):
                kk = labels[nm].count(k)
                fs[nm].setdefault("class_frac", {})[k] = {"k": kk, "n": n_, "rate": kk / n_, "wilson95": list(wilson(kk, n_))}
    # same-seed failures: does the class agree?
    sh = [s for s in seeds if s in fa and s in fb]
    agree = [(classify(res, f"E6a|seed{s}"), classify(res, f"E6b|seed{s}")) for s in sh]
    agree = [x for x in agree if None not in x]
    fs["shared_seed_class_agree"] = {"n": len(agree), "agree": sum(x == y for x, y in agree)}
    o["failure_state"] = fs

    # --- lifetimes (C1 + sigma*) and the barrier picture
    L, Cn, per_run = [], [], []
    for s in seeds:
        l, c = stalls(Bn[s])
        L += l
        Cn += c
        per_run.append(len(l))
    L, Cn = np.array(L), np.array(Cn, bool)
    k = km(L, ~Cn, T_MAX)
    curve = k.pop("curve")
    k["S_at"] = {str(t): [sv for tt, sv in curve if tt <= t][-1] for t in CHECK_T}
    wb = weibull_pool([(L, Cn)])
    # same stall definition for C3 RVO2 (deterministic): stalls end in an exit or never
    LA, CA = [], []
    for s in seeds:
        l, c = stalls(A[s])
        LA += l
        CA += c
    nu = json.load(open(os.path.join(DER, "E4_analysis.json")))["per_condition"]["full"]["nu_hat_median"]
    bp = barrier_picture(sigma, nu)
    o["lifetimes"] = {"stall_def_s": STALL, "n_stalls": int(len(L)), "n_escaped": int((~Cn).sum()),
                      "n_open_at_end": int(Cn.sum()), "frac_open_at_end": float(Cn.mean()),
                      "runs_with_stall": int(sum(x > 0 for x in per_run)),
                      "km": k, "weibull": wb,
                      "escaped_median_s": float(np.median(L[~Cn])),
                      "escaped_iqr_s": [float(np.percentile(L[~Cn], 25)), float(np.percentile(L[~Cn], 75))],
                      "escaped_max_s": float(L[~Cn].max()),
                      "C3_rvo2_stalls": int(len(LA)), "C3_rvo2_escaped": int(len(LA) - sum(CA)),
                      "C3_rvo2_escaped_median_s": float(np.median([x for x, c in zip(LA, CA) if not c])) if len(LA) > sum(CA) else None,
                      "barrier_picture": bp}
    o["lifetimes"]["pred_vs_obs"] = {"t": list(CHECK_T), "S_pred": [bp["pred_S_at"][str(t)] for t in CHECK_T],
                                     "S_obs_km": [k["S_at"][str(t)] for t in CHECK_T],
                                     "median_pred_s": bp["pred_median_lifetime_s"], "median_obs_km_s": k["median"],
                                     "max_abs_diff": float(max(abs(bp["pred_S_at"][str(t)] - k["S_at"][str(t)]) for t in CHECK_T))}
    with open(OUT, "w") as f:
        json.dump(o, f, indent=1, default=float)
    brief(o)


def brief(o):
    c = o["completion"]
    print("completion C3", c["C3_rvo2"]["k"], c["C3_rvo2"]["wilson95"], "sigma", c["C1_sigma"]["k"], c["C1_sigma"]["wilson95"])
    print("diff", c["diff_sigma_minus_C3"], c["agreement_check_internal"])
    i = o["identity"]
    print("identity", {k: v for k, v in i.items() if not k.startswith("seeds")})
    t = o["time"]
    print("time", {k: v for k, v in t.items() if not k.startswith("km")})
    print("km", t["km_C3_rvo2"], t["km_C1_sigma"])
    for nm in ("C3_rvo2", "C1_sigma"):
        f = o["failure_state"][nm]
        print(nm, {k: v for k, v in f.items() if k != "rows"})
    print("class test", o["failure_state"].get("class_test"), o["failure_state"]["shared_seed_class_agree"])
    L = o["lifetimes"]
    print("lifetimes", {k: v for k, v in L.items() if k != "barrier_picture"})
    print("barrier", {k: v for k, v in L["barrier_picture"].items() if k != "rows"})


if __name__ == "__main__":
    main()
