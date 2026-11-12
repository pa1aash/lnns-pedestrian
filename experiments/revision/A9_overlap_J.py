"""A9: reconciliation of the overlap J of the unresolved sets (Table 4 J = 0.20 against text J = 0.75).

Inputs (existing data only):
  data/E2/e2_quench.jsonl, data/derived/selection.json   lone-trap snapshots; noise0.07 (5 seeds), C3_rvo2
  data/N1/n1.jsonl                                       lone keystones, sigma = 0.0717 m/s, 20 seeds
  data/E6/e6a.jsonl, data/E6/e6b.jsonl, data/N2/n2.jsonl whole runs (C3 RVO2; C1 + sigma*, two noise streams)
  data/E7b/e7b_quench.jsonl, data/E7b_bstar/bstar_quench.jsonl   pair standoffs (C3 both solvers, +b* both)
Output: data/derived/rev_A9.json

Set definitions
  ORCA (deterministic)  unresolved: the unperturbed run holds (blocker not out within 120 s; whole run not
                        complete at 600 s). Pair: freed = freed and first exit <= 120 s.
  noise, m seeds        a snapshot with k of its m seeds freeing is unresolved under rule
                          half : k < m/2   (the rule of E2 analyze.py, fix_a1.py and analyze_N1.py; 5 seeds: k <= 2)
                          none : k = 0
                          all  : k < m     (fewer than all seeds free it)
  whole runs            one run per seed and stream; with the two streams (E6b, N2) combined, m = 2.
  pair                  both arms deterministic; Table 5 uses the minority (freed) sets; the held sets are given too.
J = |S1 & S2| / |S1 | S2| on the universe of N units.
Independence: with set sizes a = |S1|, b = |S2| fixed, the overlap X is hypergeometric(N, a, b):
  p_ge = P(X >= x_obs) = sum_{k >= x_obs} C(a,k) C(N-a,b-k) / C(N,b) (exact; scipy.stats.hypergeom.sf);
  p_le = P(X <= x_obs) for the lower tail; E X = ab/N; J at E X = (ab/N) / (a + b - ab/N);
  E J = sum_k P(X=k) k/(a+b-k) (the value Tables 4 and 5 print in parentheses, fix_a1.hyper_j).
Reconciliation (lone keystones)
  per_snapshot   k of 5 (E2, sigma 0.07), k of 20 (N1, sigma 0.0717) and the ORCA outcome, for every snapshot
                 that is not freed by all seeds of both or that ORCA does not free.
  subsets5       J(noise, ORCA) recomputed from every 5-seed subset of the 20 N1 seeds (C(20,5) = 15504), half rule:
                 distribution of the J a five-seed experiment would report at sigma = 0.0717.
  binomial5      10000 parametric five-seed replicates k_i ~ Binomial(5, p_i), p_i = k_i/20 from N1, half rule;
                 P(J <= 0.20) and the median J. RNG numpy default_rng(20261110).
"""
import itertools
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

T_Q = 120.0
RNG = np.random.default_rng(20261110)
RULES = {"half": lambda k, m: k < m / 2, "none": lambda k, m: k == 0, "all": lambda k, m: k < m}


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def jac(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else float("nan")


def hyper(N, a, b, x):
    rv = stats.hypergeom(N, a, b)
    ks = np.arange(max(0, a + b - N), min(a, b) + 1)
    pk = rv.pmf(ks)
    js = np.array([k / (a + b - k) if a + b - k else np.nan for k in ks])
    ex = a * b / N
    p_ge = float(rv.sf(x - 1)) if x > 0 else 1.0
    p_le = float(rv.cdf(x))
    return {"N": int(N), "a": int(a), "b": int(b), "x_obs": int(x), "E_overlap": ex,
            "J_at_E_overlap": ex / (a + b - ex) if a + b - ex > 0 else None,
            "E_J": float(np.nansum(pk * js)) if a + b else None,
            "p_ge": p_ge, "p_ge_disp": revlib.pdisp(p_ge), "p_le": p_le, "p_le_disp": revlib.pdisp(p_le)}


def compare(s1, s2, label1, label2, units):
    s1, s2 = np.asarray(s1, bool), np.asarray(s2, bool)
    x = int((s1 & s2).sum())
    J = jac(s1, s2)
    h = hyper(len(units), int(s1.sum()), int(s2.sum()), x)
    return {"sets": [label1, label2], "J": J, "J_disp": revlib.sig(J) if J == J else None, **h,
            "S1": [u for u, f in zip(units, s1) if f], "S2": [u for u, f in zip(units, s2) if f]}


def load_lone():
    sel = json.load(open(os.path.join(revlib.DERIVED, "selection.json")))["E2"]["snapshots"]
    snaps = {s["tag"]: s for s in sel}
    F = defaultdict(dict)
    for r in jl(os.path.join(revlib.DATA, "E2", "e2_quench.jsonl")):
        tag, arm, rep = r["job_id"].split("|")
        if arm in ("noise0.07", "C3_rvo2", "C3_pub"):
            t = r["exits"].get(str(snaps[tag]["blocker"]))
            F[(tag, arm)][rep] = t is not None and t <= T_Q + 1e-9
    for r in jl(os.path.join(revlib.DATA, "N1", "n1.jsonl")):
        tag = r["job_id"].split("|")[0]
        t = r["exits"].get(str(snaps[tag]["blocker"]))
        F[(tag, "N1")][str(r["rep"])] = t is not None and t <= T_Q + 1e-9
    return sel, F


def lone(sel, F):
    out = {}
    for st, arms in (("lone_keystone", ("noise0.07", "N1")), ("lone_keystone_second_trap", ("noise0.07",))):
        T = [s["tag"] for s in sel if s["class"] == st]
        orca = np.array([not F[(t, "C3_rvo2")]["u"] for t in T])
        o = {"n_snapshots": len(T), "orca_unresolved": [t for t, f in zip(T, orca) if f]}
        for arm in arms:
            m = 5 if arm == "noise0.07" else 20
            M = np.array([[F[(t, arm)][str(i)] for i in range(m)] for t in T])
            k = M.sum(1)
            o[arm.replace(".", "p")] = {"seeds": m, "rules": {
                r: compare(fn(k, m), orca, f"noise unresolved ({r})", "ORCA (RVO2) unresolved", T)
                for r, fn in RULES.items()}}
        out[st] = o
    # reconciliation, lone keystones
    T = [s["tag"] for s in sel if s["class"] == "lone_keystone"]
    orca = np.array([not F[(t, "C3_rvo2")]["u"] for t in T])
    k5 = np.array([sum(F[(t, "noise0.07")].values()) for t in T])
    M20 = np.array([[F[(t, "N1")][str(i)] for i in range(20)] for t in T])
    k20 = M20.sum(1)
    out["per_snapshot"] = {t: {"k5_sigma0p07": int(a), "k20_sigma0p0717": int(b), "orca_freed": bool(not c),
                               "unres_5_half": bool(a < 2.5), "unres_20_half": bool(b < 10)}
                           for t, a, b, c in zip(T, k5, k20, orca) if a < 5 or b < 20 or c}
    js = []
    for sub in itertools.combinations(range(20), 5):
        js.append(jac(M20[:, list(sub)].sum(1) < 2.5, orca))
    js = np.array(js)
    out["subsets5"] = {"n_subsets": len(js), "median": float(np.median(js)), "mean": float(js.mean()),
                       "range95": [float(np.percentile(js, 2.5)), float(np.percentile(js, 97.5))],
                       "frac_le_0p20": float(np.mean(js <= 0.2 + 1e-12)), "frac_ge_0p75": float(np.mean(js >= 0.75 - 1e-12)),
                       "values_count": {str(round(v, 3)): int(c) for v, c in zip(*np.unique(np.round(js, 3), return_counts=True))}}
    p = k20 / 20
    jb = np.array([jac(RNG.binomial(5, p) < 2.5, orca) for _ in range(10000)])
    out["binomial5"] = {"median": float(np.median(jb)), "range95": [float(np.percentile(jb, 2.5)), float(np.percentile(jb, 97.5))],
                        "frac_le_0p20": float(np.mean(jb <= 0.2 + 1e-12))}
    # probability that the 5-seed majority call differs from the 20-seed call, given p_i (N1)
    pm = stats.binom.sf(2, 5, p)  # P(k5 >= 3)
    flip = np.where(k20 < 10, pm, 1 - pm)
    out["misclassification_5seed"] = {"expected_snapshots_misclassified": float(flip.sum()),
                                      "per_snapshot": {t: float(f) for t, f in zip(T, flip) if f > 0.01}}
    # exchangeability of the E2 five and the N1 twenty seeds: per snapshot, draw which 5 of the 25 pooled
    # outcomes are the "E2" ones (hypergeometric), 10000 draws; P(J5 <= observed 0.20) and a heterogeneity
    # statistic H = sum_i (k5_i - E k5_i)^2 / Var k5_i (hypergeometric moments), permutation p of H >= observed.
    k25 = k5 + k20
    ek = 5 * k25 / 25
    vk = 5 * (k25 / 25) * (1 - k25 / 25) * (20 / 24)
    ok = vk > 0
    H_obs = float((((k5 - ek) ** 2)[ok] / vk[ok]).sum())
    jp, Hp = [], []
    for _ in range(10000):
        kk = RNG.hypergeometric(k25, 25 - k25, 5)
        jp.append(jac(kk < 2.5, orca))
        Hp.append(float((((kk - ek) ** 2)[ok] / vk[ok]).sum()))
    jp, Hp = np.array(jp), np.array(Hp)
    J5_obs = jac(k5 < 2.5, orca)
    out["exchangeability_E2_vs_N1"] = {
        "J5_observed": J5_obs, "P_J5_le_observed": float(np.mean(jp <= J5_obs + 1e-12)),
        "P_J5_le_observed_disp": revlib.pdisp(float(np.mean(jp <= J5_obs + 1e-12))),
        "J5_perm_median": float(np.median(jp)), "J5_perm_range95": [float(np.percentile(jp, 2.5)), float(np.percentile(jp, 97.5))],
        "H_observed": H_obs, "H_perm_p": float((np.sum(Hp >= H_obs - 1e-12) + 1) / (len(Hp) + 1)),
        "n_snapshots_informative": int(ok.sum()),
        "method": ("per snapshot the 25 outcomes (5 E2 at 0.07 + 20 N1 at 0.0717) are split at random into 5 and 20, "
                   "10000 draws; J5 = J(half rule on the 5, ORCA); H = sum (k5 - 5 k25/25)^2 / hypergeometric variance")}
    # pooled 25 seeds (E2 at 0.07 + N1 at 0.0717, nearly the same level), supplementary
    out["pooled25_supplementary"] = {r: compare(fn(k25, 25), orca, f"noise unresolved ({r}, 25 seeds)",
                                                "ORCA (RVO2) unresolved", T) for r, fn in RULES.items()}
    return out


def whole():
    S = {k: {r["seed"]: r for r in jl(os.path.join(revlib.DATA, *p))} for k, p in
         (("E6a", ("E6", "e6a.jsonl")), ("E6b", ("E6", "e6b.jsonl")), ("N2", ("N2", "n2.jsonl")))}
    seeds = sorted(S["E6a"])
    fail = {k: np.array([not v[s]["complete"] for s in seeds]) for k, v in S.items()}
    kdone = (~fail["E6b"]).astype(int) + (~fail["N2"]).astype(int)
    o = {"n_seeds": len(seeds),
         "E6b_vs_orca": compare(fail["E6b"], fail["E6a"], "E6b noise fails", "ORCA (RVO2) fails", seeds),
         "N2_vs_orca": compare(fail["N2"], fail["E6a"], "N2 noise fails", "ORCA (RVO2) fails", seeds),
         "E6b_vs_N2_noise_noise": compare(fail["E6b"], fail["N2"], "E6b noise fails", "N2 noise fails", seeds),
         "two_streams": {r: compare(fn(kdone, 2), fail["E6a"], f"noise unresolved ({r}, 2 streams)",
                                    "ORCA (RVO2) fails", seeds) for r, fn in RULES.items()}}
    return o


def pair():
    fr = {}
    for p in (("E7b", "e7b_quench.jsonl"), ("E7b_bstar", "bstar_quench.jsonl")):
        for r in jl(os.path.join(revlib.DATA, *p)):
            tag, arm, rep = r["job_id"].split("|")
            if rep == "u":
                fr[(tag, arm)] = bool(r["freed"] and r["first_t"] <= T_Q + 1e-9)
    tags = sorted({t for t, _ in fr}, key=lambda t: int(t.rsplit("seed", 1)[1]))
    o = {"n_snapshots": len(tags)}
    for k, (b, c) in {"pub": ("bstar_pub+", "C3_pub"), "rvo2": ("bstar_rvo2+", "C3_rvo2")}.items():
        x = np.array([fr[(t, b)] for t in tags])
        y = np.array([fr[(t, c)] for t in tags])
        o[k] = {"freed_sets": compare(x, y, f"{b} freed", f"{c} freed", tags),
                "held_sets": compare(~x, ~y, f"{b} held", f"{c} held", tags)}
    return o


def main():
    sel, F = load_lone()
    out = {"script": "experiments/revision/A9_overlap_J.py", "doc": __doc__, "lone": lone(sel, F),
           "whole": whole(), "pair": pair()}
    L = out["lone"]
    hl = {}
    for name, c in (("lk_0p07_half", L["lone_keystone"]["noise0p07"]["rules"]["half"]),
                    ("lk_N1_half", L["lone_keystone"]["N1"]["rules"]["half"]),
                    ("st_0p07_half", L["lone_keystone_second_trap"]["noise0p07"]["rules"]["half"]),
                    ("whole_E6b", out["whole"]["E6b_vs_orca"]), ("whole_N2", out["whole"]["N2_vs_orca"]),
                    ("pair_pub_freed", out["pair"]["pub"]["freed_sets"]),
                    ("pair_rvo2_freed", out["pair"]["rvo2"]["freed_sets"])):
        hl[name] = {k: c[k] for k in ("J", "N", "a", "b", "x_obs", "E_overlap", "J_at_E_overlap", "E_J", "p_ge", "p_le")}
    out["headline"] = hl
    print(revlib.out_json("A9", out))
    for k, v in hl.items():
        print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
    for st in ("lone_keystone", "lone_keystone_second_trap"):
        for arm in ("noise0p07", "N1"):
            if arm in L[st]:
                for r, c in L[st][arm]["rules"].items():
                    print(st, arm, r, c["a"], c["b"], c["x_obs"], round(c["J"], 3), round(c["E_J"], 3), c["p_ge_disp"])
    for r, c in out["whole"]["two_streams"].items():
        print("whole 2 streams", r, c["a"], c["b"], c["x_obs"], round(c["J"], 3), round(c["E_J"], 3), c["p_ge_disp"])
    for r, c in L["pooled25_supplementary"].items():
        print("pooled25", r, c["a"], c["b"], c["x_obs"], round(c["J"], 3), c["p_ge_disp"])
    print("subsets5", {k: v for k, v in L["subsets5"].items() if k != "values_count"}, L["subsets5"]["values_count"])
    print("exch", L["exchangeability_E2_vs_N1"])
    print("binomial5", L["binomial5"], L["misclassification_5seed"])
    for t, v in L["per_snapshot"].items():
        print(t, v)
    for k in ("pub", "rvo2"):
        c = out["pair"][k]["held_sets"]
        print("pair held", k, c["a"], c["b"], c["x_obs"], round(c["J"], 3), round(c["E_J"], 3), c["p_ge_disp"])


if __name__ == "__main__":
    main()
