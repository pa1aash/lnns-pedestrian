#!/usr/bin/env python3
"""Statistics hygiene for the attribution results (FIX_PLAN WP-AN A-6; item 03-2).

Input (read only): data/E2/e2_quench.jsonl, data/derived/selection.json (E2 lone-trap snapshots),
data/E6/e6a.jsonl, data/E6/e6b.jsonl, data/derived/E6_analysis.json (final-state class per failed run),
data/E7b/e7b_quench.jsonl, data/E7b/e7b_static.jsonl, data/E7b_bstar/bstar_quench.jsonl,
data/E5/e5a.jsonl, data/E5/e5b.jsonl, data/E1/E1_runs.jsonl.
Output: data/derived/fix_a6.json.

Parts
  1 lone_rates      cluster bootstrap (snapshot = resampling unit) of every E2 freed fraction, against the
                    Wilson interval that treats every run as independent; the paired difference noise - C3 RVO2
                    per snapshot with its cluster bootstrap and an exact sign-flip test; per-seed McNemar.
  2 mcnemar         exact McNemar for the paired cells behind every Delta of Table 3 (recomputed from raw runs).
  3 class_test      the final-state class test of the whole runs (E6) with permutations that respect the
                    pairing by spawn seed: within a seed failed by both, the two class labels are swapped
                    with probability 1/2; seeds failed by one solver only are exchanged among themselves.
  4 fold_by_snapshot static fold prediction against the 120 s quench, counted per pair snapshot.
  5 e5              presence of the per-run E5 files and a seed-cluster bootstrap of sigma50.
All intervals 95%. Bootstrap: 10000 resamples, percentile, numpy default_rng(20261109).
"""
import json
import math
from collections import defaultdict
from itertools import product
from pathlib import Path

import numpy as np
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DER = DATA / "derived"
OUT = DER / "fix_a6.json"
T_Q = 120.0
B = 10000
SEED = 20261109
Z = 1.959963984540054


def jl(p):
    return [json.loads(ln) for ln in open(p) if ln.strip()]


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def pct(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def cluster_rate(k, n, rng):
    """k, n: per-cluster freed and run counts. Returns rate, Wilson, cluster-bootstrap CI, design effect."""
    k, n = np.asarray(k, float), np.asarray(n, float)
    m = len(k)
    idx = rng.integers(0, m, (B, m))
    bs = k[idx].sum(1) / n[idx].sum(1)
    K, N = int(k.sum()), int(n.sum())
    p = K / N
    var_bin = p * (1 - p) / N
    # ratio-estimator (linearised) variance with snapshot clusters
    r = k - p * n
    var_cl = m / (m - 1) * float(np.sum(r ** 2)) / N ** 2 if m > 1 else float("nan")
    w = wilson(K, N)
    cb = pct(bs)
    return {"freed": K, "n_runs": N, "n_snapshots": m, "rate": p, "wilson95": w, "cluster_boot95": cb,
            "width_wilson": w[1] - w[0], "width_cluster": cb[1] - cb[0],
            "width_ratio_cluster_over_wilson": (cb[1] - cb[0]) / (w[1] - w[0]) if w[1] > w[0] else None,
            "design_effect": var_cl / var_bin if var_bin > 0 else None}


def signflip_exact(d):
    """Exact two-sided sign-flip (paired permutation) test of sum(d) = 0 over the non-zero d."""
    d = np.asarray([x for x in d if abs(x) > 1e-12], float)
    if len(d) == 0:
        return 1.0, 0
    s0 = abs(d.sum())
    if len(d) <= 20:
        cnt = sum(abs(np.dot(sg, d)) >= s0 - 1e-12 for sg in product((-1, 1), repeat=len(d)))
        return cnt / 2 ** len(d), len(d)
    raise ValueError("too many non-zero differences for exact enumeration")


# ------------------------------------------------------------------ 1. lone-trap rates (E2)
def part_lone(rng):
    sel = json.load(open(DER / "selection.json"))["E2"]["snapshots"]
    snaps = {s["tag"]: s for s in sel}
    runs = defaultdict(dict)
    for r in jl(DATA / "E2" / "e2_quench.jsonl"):
        tag, arm, rep = r["job_id"].split("|")
        t = r["exits"].get(str(snaps[tag]["blocker"]))
        runs[(tag, arm)][rep] = t is not None and t <= T_Q + 1e-9
    arms = sorted({a for _, a in runs})
    groups = {"lone_keystone": ["lone_keystone"], "lone_keystone_second_trap": ["lone_keystone_second_trap"],
              "pooled": ["lone_keystone", "lone_keystone_second_trap"]}
    out = {"method": "freed fraction of the blocker within 120 s; deterministic arms use the unperturbed run "
                     "(one run per snapshot), noise arms every seed (five runs per snapshot); Wilson treats runs "
                     "as independent, the cluster bootstrap resamples snapshots with all their runs "
                     f"({B} resamples, percentile); design effect = linearised cluster variance / binomial variance"}
    for g, cl in groups.items():
        T = [s["tag"] for s in sel if s["class"] in cl]
        og = {}
        for a in arms:
            if a.startswith("noise"):
                k = [sum(runs[(t, a)].values()) for t in T]
                n = [len(runs[(t, a)]) for t in T]
            else:
                k = [int(runs[(t, a)]["u"]) for t in T]
                n = [1] * len(T)
            c = cluster_rate(k, n, rng)
            if not a.startswith("noise"):
                c["note"] = "one run per snapshot: the cluster bootstrap equals the ordinary bootstrap; Wilson is the reported interval"
            og[a.replace(".", "p")] = c
        out[g] = og
    # paired difference noise - C3 RVO2 per snapshot (Table 3 Delta, lone block)
    T = [s["tag"] for s in sel if s["class"] == "lone_keystone"]
    c3 = np.array([float(runs[(t, "C3_rvo2")]["u"]) for t in T])
    pd = {}
    for a in ("noise0.03", "noise0.05", "noise0.07"):
        nf = np.array([np.mean(list(runs[(t, a)].values())) for t in T])
        d = nf - c3
        idx = rng.integers(0, len(T), (B, len(T)))
        p_sf, n_nz = signflip_exact(d)
        per_seed = []
        for s in sorted(runs[(T[0], a)]):
            x = np.array([runs[(t, a)][s] for t in T])
            y = c3.astype(bool)
            b_, c_ = int((x & ~y).sum()), int((~x & y).sum())
            per_seed.append({"seed": s, "noise_only": b_, "C3_only": c_, "mcnemar_exact_p": mcnemar_exact(b_, c_)})
        maj = nf >= 0.5
        y = c3.astype(bool)
        b_, c_ = int((maj & ~y).sum()), int((~maj & y).sum())
        pd[a.replace(".", "p")] = {
            "n_snapshots": len(T), "diff": float(d.mean()), "cluster_boot95": pct(d[idx].mean(1)),
            "signflip_exact_p": p_sf, "n_nonzero": n_nz,
            "per_seed_mcnemar": per_seed,
            "per_seed_mcnemar_p_min": min(x["mcnemar_exact_p"] for x in per_seed),
            "per_seed_mcnemar_p_max": max(x["mcnemar_exact_p"] for x in per_seed),
            "majority_mcnemar": {"noise_only": b_, "C3_only": c_, "mcnemar_exact_p": mcnemar_exact(b_, c_)},
            "method": "per-snapshot difference (fraction of the five noise seeds freed minus the C3 RVO2 unperturbed "
                      "outcome); snapshot bootstrap; exact sign-flip test over snapshots; McNemar per seed index "
                      "and with the majority rule (freed in at least 3 of 5)"}
    out["paired_diff_noise_minus_C3_rvo2_lone_keystone"] = pd
    return out


# ------------------------------------------------------------------ 2. McNemar for paired cells
def part_mcnemar(rng):
    out = {}
    # whole runs E6
    A = {r["seed"]: bool(r["complete"]) for r in jl(DATA / "E6" / "e6a.jsonl")}
    S = {r["seed"]: bool(r["complete"]) for r in jl(DATA / "E6" / "e6b.jsonl")}
    seeds = sorted(A)
    a = np.array([A[s] for s in seeds])
    s_ = np.array([S[s] for s in seeds])
    b_, c_ = int((s_ & ~a).sum()), int((~s_ & a).sum())
    d = s_.astype(float) - a.astype(float)
    idx = rng.integers(0, len(seeds), (B, len(seeds)))
    out["whole_runs_E6"] = {"n": len(seeds), "C3_rvo2_complete": int(a.sum()), "C1_sigma_complete": int(s_.sum()),
                            "sigma_only_complete": b_, "C3_only_complete": c_,
                            "mcnemar_exact_p": mcnemar_exact(b_, c_), "diff": float(d.mean()),
                            "seed_boot95": pct(d[idx].mean(1)),
                            "method": "complete within 600 s, paired by spawn seed; exact McNemar; seed bootstrap of "
                                      "the paired difference (C1 + sigma* minus C3 RVO2)"}
    # pair standoffs E7b
    fr = {}
    for p in (DATA / "E7b" / "e7b_quench.jsonl", DATA / "E7b_bstar" / "bstar_quench.jsonl"):
        for r in jl(p):
            tag, arm, rep = r["job_id"].split("|")
            if rep == "u":
                fr[(tag, arm)] = bool(r["freed"] and r["first_t"] is not None and r["first_t"] <= T_Q + 1e-9)
    tags = sorted({t for t, _ in fr}, key=lambda t: int(t.rsplit("seed", 1)[1]))
    for k, (x_, y_) in {"pub": ("bstar_pub+", "C3_pub"), "rvo2": ("bstar_rvo2+", "C3_rvo2")}.items():
        x = np.array([fr[(t, x_)] for t in tags])
        y = np.array([fr[(t, y_)] for t in tags])
        b_, c_ = int((x & ~y).sum()), int((~x & y).sum())
        d = x.astype(float) - y.astype(float)
        idx = rng.integers(0, len(tags), (B, len(tags)))
        out[f"pair_{k}"] = {"n": len(tags), "bias_freed": int(x.sum()), "orca_freed": int(y.sum()),
                            "bias_only": b_, "orca_only": c_, "mcnemar_exact_p": mcnemar_exact(b_, c_),
                            "diff": float(d.mean()), "snapshot_boot95": pct(d[idx].mean(1)),
                            "method": f"{x_} against {y_}, unperturbed runs per snapshot, freed within 120 s; exact "
                                      "McNemar; snapshot bootstrap of the paired difference"}
    return out


# ------------------------------------------------------------------ 3. final-state class test, pairing kept
def chi2_stat(la, lb, cats):
    tab = np.array([[np.sum(la == c) for c in cats], [np.sum(lb == c) for c in cats]], float)
    tab = tab[:, tab.sum(0) > 0]
    exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
    return float(np.sum((tab - exp) ** 2 / exp))


def part_class(rng):
    fs = json.load(open(DER / "E6_analysis.json"))["failure_state"]
    ca = {r["seed"]: r["class"] for r in fs["C3_rvo2"]["rows"]}
    cb = {r["seed"]: r["class"] for r in fs["C1_sigma"]["rows"]}
    cats = sorted(set(ca.values()) | set(cb.values()))
    shared = sorted(set(ca) & set(cb))
    only_a = sorted(set(ca) - set(cb))
    only_b = sorted(set(cb) - set(ca))
    pa = np.array([ca[s] for s in shared])
    pb = np.array([cb[s] for s in shared])
    ua = np.array([ca[s] for s in only_a])
    ub = np.array([cb[s] for s in only_b])
    s0 = chi2_stat(np.concatenate([pa, ua]), np.concatenate([pb, ub]), cats)
    upool = np.concatenate([ua, ub])
    na = len(ua)
    cnt_strat = cnt_pair = cnt_free = 0
    s0_pair = chi2_stat(pa, pb, cats)
    s0_unp = chi2_stat(ua, ub, cats)
    cnt_unp = 0
    allv = np.concatenate([pa, ua, pb, ub])
    nA = len(pa) + len(ua)
    for _ in range(B):
        sw = rng.random(len(shared)) < 0.5
        qa, qb = np.where(sw, pb, pa), np.where(sw, pa, pb)
        up = rng.permutation(upool)
        if chi2_stat(np.concatenate([qa, up[:na]]), np.concatenate([qb, up[na:]]), cats) >= s0 - 1e-12:
            cnt_strat += 1
        if chi2_stat(qa, qb, cats) >= s0_pair - 1e-12:
            cnt_pair += 1
        if chi2_stat(up[:na], up[na:], cats) >= s0_unp - 1e-12:
            cnt_unp += 1
        fp = rng.permutation(allv)
        if chi2_stat(fp[:nA], fp[nA:], cats) >= s0 - 1e-12:
            cnt_free += 1
    trans = {f"{x}->{y}": int(np.sum((pa == x) & (pb == y))) for x in cats for y in cats
             if np.sum((pa == x) & (pb == y))}
    # exact McNemar on the shared seeds for lone vs not-lone
    b_ = int(np.sum((pa != "lone_keystone") & (pb == "lone_keystone")))
    c_ = int(np.sum((pa == "lone_keystone") & (pb != "lone_keystone")))
    return {
        "n_fail_C3_rvo2": len(ca), "n_fail_C1_sigma": len(cb), "n_shared_seeds": len(shared),
        "n_C3_only": len(only_a), "n_sigma_only": len(only_b), "categories": cats,
        "chi2_all": s0,
        "p_unrestricted_perm": (cnt_free + 1) / (B + 1),
        "p_within_seed_perm": (cnt_strat + 1) / (B + 1),
        "shared_seeds_only": {"chi2": s0_pair, "p_within_seed_perm": (cnt_pair + 1) / (B + 1),
                              "transitions_C3_to_sigma": trans,
                              "lone_mcnemar": {"C3_other_sigma_lone": b_, "C3_lone_sigma_other": c_,
                                               "mcnemar_exact_p": mcnemar_exact(b_, c_)}},
        "single_solver_failures_only": {"chi2": s0_unp, "p_perm": (cnt_unp + 1) / (B + 1)},
        "method": "chi-square statistic of the 2 x classes table of failed runs (C3 RVO2 against C1 + sigma*); "
                  "within-seed permutation: for each seed failed by both, the two labels are swapped with "
                  "probability 1/2, and the failures of seeds failed by one solver only are permuted among "
                  f"themselves; {B} permutations, p = (count + 1)/(B + 1); the unrestricted permutation of the "
                  "original analysis is recomputed for comparison"}


# ------------------------------------------------------------------ 4. fold agreement by snapshot
def part_fold():
    S = {r["job_id"]: r for r in jl(DATA / "E7b" / "e7b_static.jsonl")}
    fr = {}
    for r in jl(DATA / "E7b" / "e7b_quench.jsonl"):
        tag, arm, rep = r["job_id"].split("|")
        if rep == "u":
            fr[(tag, arm)] = bool(r["freed"] and r["first_t"] is not None and r["first_t"] <= T_Q + 1e-9)
    grid = [-0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.05, 0.1]
    per = {}
    for t in S:
        dis = [b for b in grid if bool(S[t]["fold"][f"bias{b:g}"]["pred_freed"]) != fr[(t, f"bias{b:g}")]]
        per[t] = dis
    n_case = len(S) * len(grid)
    agree = n_case - sum(len(v) for v in per.values())
    all_ok = sum(not v for v in per.values())
    n = len(S)
    return {"n_snapshots": n, "b_values_per_snapshot": len(grid), "cases": n_case, "cases_agree": agree,
            "snapshots_all_agree": all_ok, "snapshots_all_agree_wilson95": wilson(all_ok, n),
            "snapshots_with_disagreement": n - all_ok,
            "max_disagreements_one_snapshot": max(len(v) for v in per.values()),
            "disagreements": {t: v for t, v in per.items() if v},
            "case_wilson95": wilson(agree, n_case),
            "method": "static fold prediction (freed iff the bias exceeds the snapshot's static fold) against the "
                      "unperturbed 120 s quench, eight bias values per snapshot; counted per case and per snapshot "
                      "(a snapshot agrees when all eight cases do); Wilson over snapshots"}


# ------------------------------------------------------------------ 5. E5 per-run files, sigma50 by seed
def nll(p, x, k, n):
    eta = p[0] * (x - p[1])
    return -float(np.sum(k * eta - n * np.logaddexp(0, eta)))


def fit50(x, k, n, x0=(60.0, 0.045)):
    r = optimize.minimize(nll, x0, args=(x, k, n), method="Nelder-Mead",
                          options={"xatol": 1e-9, "fatol": 1e-9, "maxiter": 4000})
    return float(r.x[1])


def part_e5(rng):
    out = {}
    for name, f, lv in (("E5b_corrected", "e5b.jsonl", None), ("E5a_published", "e5a.jsonl", 0.07)):
        p = DATA / "E5" / f
        if not p.exists():
            out[name] = {"present": False}
            continue
        R = jl(p)
        levels = sorted({r["sigma"] for r in R if lv is None or r["sigma"] <= lv + 1e-12})
        seeds = sorted({r["seed"] for r in R})
        Y = np.full((len(seeds), len(levels)), np.nan)
        si = {s: i for i, s in enumerate(seeds)}
        for r in R:
            if r["sigma"] in levels:
                Y[si[r["seed"]], levels.index(r["sigma"])] = float(bool(r["complete"]))
        x = np.array(levels)
        s50 = fit50(x, Y.sum(0), np.full(len(levels), len(seeds)))
        bs = []
        for _ in range(B):
            idx = rng.integers(0, len(seeds), len(seeds))
            bs.append(fit50(x, Y[idx].sum(0), np.full(len(levels), len(seeds)), (60.0, s50)))
        # independent-run bootstrap: each level resampled on its own (what the binomial fit assumes)
        bi = []
        for _ in range(2000):
            k = np.array([Y[rng.integers(0, len(seeds), len(seeds)), j].sum() for j in range(len(levels))])
            bi.append(fit50(x, k, np.full(len(levels), len(seeds)), (60.0, s50)))
        # correlation of outcomes across levels within seed
        cc = np.corrcoef(Y.T)
        off = cc[~np.eye(len(levels), dtype=bool)]
        # monotone seeds: completion at sigma implies completion at every larger sigma
        mono = int(sum(all(Y[i, j] <= Y[i, j + 1] for j in range(len(levels) - 1)) for i in range(len(seeds))))
        out[name] = {"present": True, "file": f"data/E5/{f}", "runs": len(R), "seeds": [seeds[0], seeds[-1]],
                     "n_seeds": len(seeds), "sigma_levels_all": sorted({r["sigma"] for r in R}),
                     "sigma_levels_fit": levels, "fields": sorted(R[0].keys()),
                     "completed_per_level": [int(v) for v in Y.sum(0)],
                     "sigma50": s50, "seed_cluster_boot95": pct(bs), "independent_boot95": pct(bi),
                     "mean_between_level_outcome_corr": float(np.mean(off)),
                     "seeds_monotone_in_sigma": mono,
                     "method": "binomial logit fit of completion against sigma, maximum likelihood; seed-cluster "
                               f"bootstrap ({B} resamples of the seeds, each seed with its outcomes at every level) "
                               "against a bootstrap that resamples each level independently (2000 resamples)"}
    return out


def main():
    rng = np.random.default_rng(SEED)
    out = {"script": "experiments/fixan/fix_a6.py", "doc": __doc__, "n_boot": B, "rng": f"default_rng({SEED})"}
    out["lone_rates"] = part_lone(rng)
    out["mcnemar"] = part_mcnemar(rng)
    out["class_test"] = part_class(rng)
    out["fold_by_snapshot"] = part_fold()
    out["e5"] = part_e5(rng)
    OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    L = out["lone_rates"]["lone_keystone"]["noise0p07"]
    print("lone noise0.07", L["freed"], L["n_runs"], L["wilson95"], L["cluster_boot95"], L["design_effect"])
    print(json.dumps(out["lone_rates"]["paired_diff_noise_minus_C3_rvo2_lone_keystone"]["noise0p07"], default=float)[:600])
    print(json.dumps(out["mcnemar"], default=float)[:1500])
    print(json.dumps({k: v for k, v in out["class_test"].items() if k != "method"}, default=float))
    print(json.dumps({k: v for k, v in out["fold_by_snapshot"].items() if k != "method"}, default=float))
    for k, v in out["e5"].items():
        print(k, {kk: vv for kk, vv in v.items() if kk not in ("fields", "method")})


if __name__ == "__main__":
    main()
