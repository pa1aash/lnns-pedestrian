"""A7: paired difference tests replace the interval-overlap decision rule of protocol step 5.

For every comparison (rate-matched surrogate or reference perturbation against force-coupled ORCA) and every
probe, one paired test on the DIFFERENCE between the two perturbations on the same snapshots (or spawn seeds),
with Holm's step-down correction across the probes of each comparison (revlib.holm). Existing data only.

Inputs (read only)
  data/E2/e2_quench.jsonl, data/derived/selection.json   lone-trap quenches (34 lone keystones, 26 second traps)
  data/N1/n1.jsonl                                      noise sigma = 0.0717 m/s, 20 seeds per lone keystone
  data/E3/e3_dt.jsonl                                   time-step test (20 lone-trap snapshots)
  data/E6/e6a.jsonl, e6b.jsonl, data/N2/n2.jsonl         whole runs (186 spawn seeds): ORCA (RVO2), noise sigma*,
                                                        noise sigma* with an independent stream
  data/derived/E6_analysis.json (via experiments/fixan/fix_a6.part_class)   final-state class of failed runs
  data/E7b/e7b_quench.jsonl, data/E7b_bstar/bstar_quench.jsonl              pair standoffs (46 snapshots)
Output: data/derived/rev_A7.json.

Comparisons (surrogate first, ORCA second; differences are surrogate minus ORCA)
  lone_E2   noise sigma = 0.07 m/s (E2, 5 seeds) vs force-coupled ORCA (RVO2), 34 lone keystones
  lone_N1   noise sigma = 0.0717 m/s (N1, 20 seeds) vs ORCA (RVO2), same 34 lone keystones
  second    noise sigma = 0.07 m/s (E2) vs ORCA (RVO2), 26 second traps
  whole_E6  noise sigma* (E6b) vs ORCA (RVO2) (E6a), 186 seeds, 600 s
  whole_N2  noise sigma*, independent stream (N2) vs ORCA (RVO2) (E6a)
  pair_pub  bias +b*_legacy vs ORCA (legacy), 46 pair standoffs, 120 s
  pair_rvo2 bias +b*_RVO2 vs ORCA (RVO2)
  push_lone rest-drive push + (E2 arm frozen_plus) vs ORCA (RVO2), lone keystones
  push_second  the same at the second traps

Unit of a deterministic arm: the unperturbed run ("u") per snapshot. Unit of a noise arm: the snapshot with all
its seeds (snapshot = resampling unit); whole runs: the spawn seed.

Probes and tests
  freed       paired freed fraction at T (the match). Noise: per-snapshot freed fraction p_i (over seeds) minus
              ORCA's outcome c_i in {0, 1}; effect = mean(p_i - c_i), 95% percentile bootstrap over snapshots;
              p from the paired sign-flip permutation test of mean(p_i - c_i) (exact enumeration when at most 20
              differences are non-zero, else 200 000 random sign flips, p = (count + 1)/(B + 1)). The
              majority-rule McNemar (freed in more than half the seeds) is stored beside it. Deterministic pairs
              and whole runs: exact McNemar on the discordant counts; effect = paired difference of proportions
              with the bootstrap interval.
  replay      outcome changes. Noise: snapshot "changes" when its seeds disagree on freed (0 < k < n_seeds);
              whole-run noise: seed changes when the two noise streams (E6b, N2) disagree on completion;
              deterministic: snapshot changes when any of its five 1e-9 m replays changes the freed outcome.
              Exact McNemar on the paired indicators (surrogate changes, ORCA changes). Effect = difference of
              the fractions of units that change. Whole runs have no ORCA replays: not tested there.
  time        time to free, restricted mean up to the horizon T (RMST_T): per unit the mean of min(t_free, T)
              over its runs, a held run counting T. Every run is observed to T, so RMST_T has no censoring.
              Effect = mean paired difference (s), bootstrap CI; p from the paired sign-flip test. Kaplan-Meier
              medians with a cluster bootstrap of their difference are stored as a secondary summary.
  ell         per-step Delta t dependence (E3): per snapshot freed by ORCA at all three Delta t, ell_i(noise,
              per step, beta_ref = 1.5 or 2.5) minus ell_i(ORCA) = ln t_esc(0.02)/t_esc(0.005); exact sign-flip.
              Shared by the two lone-keystone noise comparisons (E3 sets sigma per snapshot from beta_ref), listed
              under lone_E2 only.
  overlap     identity of the outcome sets. Stochastic surrogate: per unit, the disagreement indicator of
              (noise, ORCA) against that of (noise, independent noise); lone keystones (N1): seed halves 0-9 and
              10-19, unresolved = freed in fewer than 5 of 10, disagreement of ORCA averaged over the two halves;
              whole runs: [E6a != E6b] against [N2 != E6b] (and [E6a != N2] against [E6b != N2] for whole_N2).
              Paired sign-flip test (or exact McNemar for 0/1 indicators). Effect = excess disagreement rate.
              Deterministic pairs: [surrogate != ORCA] against [ORCA's replays != ORCA] (the replay reference),
              exact McNemar. Jaccard indices stored beside.
  handed      pair only: first member out on the lower side among freed standoffs, bias +b* against ORCA,
              Fisher's exact test (the freed sets differ, so the comparison is unpaired); exact binomial against
              1/2 per arm and the paired McNemar on standoffs both free stored beside.
  class       whole runs (E6 only): final-state class of failed runs, within-seed permutation test of
              experiments/fixan/fix_a6.part_class (10 000 permutations, this script's generator).
Holm: within each comparison over its probes. "separates" = Holm-adjusted p < 0.05.
Kind: "definitional" when the difference follows from the construction of the surrogate (stochastic against
deterministic for replay; per-step noise amplitude for ell; the bias sign for handedness) and only ORCA's side is
measured; "empirical" otherwise.
Bootstrap: 10 000 resamples, percentile; generator numpy default_rng(20261110).
"""
import itertools
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import DATA, DERIVED, holm, mcnemar_exact, pdisp, sig  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

import fix_a6  # noqa: E402  (experiments/fixan, on sys.path through revlib)

B = 10000
B_FLIP = 200000
SEED = 20261110
T_Q = 120.0
T_W = 600.0
rng = np.random.default_rng(SEED)


def jl(p):
    return [json.loads(ln) for ln in open(p) if ln.strip()]


# ------------------------------------------------------------------ statistics
def boot_mean(d):
    d = np.asarray(d, float)
    idx = rng.integers(0, len(d), (B, len(d)))
    m = d[idx].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def signflip(d):
    """Two-sided paired sign-flip test of mean(d) = 0. Exact for <= 20 non-zero d, else Monte Carlo."""
    d = np.asarray([x for x in d if abs(x) > 1e-12], float)
    n = len(d)
    if n == 0:
        return 1.0, "sign-flip (all differences zero)"
    s0 = abs(d.sum()) - 1e-9
    if n <= 20:
        signs = np.array(list(itertools.product((-1.0, 1.0), repeat=n)))
        return float(np.mean(np.abs(signs @ d) >= s0)), f"exact sign-flip, {n} non-zero"
    cnt = 0
    for _ in range(B_FLIP // 20000):
        s = rng.choice((-1.0, 1.0), size=(20000, n))
        cnt += int(np.sum(np.abs(s @ d) >= s0))
    return (cnt + 1) / (B_FLIP + 1), f"sign-flip, {B_FLIP} random flips, {n} non-zero"


def mcn(x, y):
    """Paired 0/1 vectors: exact McNemar, effect mean(x) - mean(y) with bootstrap CI."""
    x, y = np.asarray(x, bool), np.asarray(y, bool)
    b, c = int((x & ~y).sum()), int((~x & y).sum())
    d = x.astype(float) - y.astype(float)
    return {"test": "exact McNemar", "b_first_only": b, "c_second_only": c, "n": len(x),
            "first": int(x.sum()), "second": int(y.sum()),
            "effect": float(d.mean()), "ci95": boot_mean(d), "p": mcnemar_exact(b, c)}


def paired_cont(d, label):
    p, how = signflip(d)
    return {"test": label, "method": how, "n": len(d), "effect": float(np.mean(d)), "ci95": boot_mean(d), "p": p}


def jaccard(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else None


def km_median(t, e):
    t, e = np.asarray(t, float), np.asarray(e, bool)
    o = np.argsort(t, kind="stable")
    t, e = t[o], e[o]
    S, n = 1.0, len(t)
    for i, (ti, ei) in enumerate(zip(t, e)):
        if ei:
            S *= 1 - 1 / (n - i)
            if S <= 0.5 + 1e-12:
                return float(ti)
    return None


def km_median_diff(times_a, times_b, T):
    """times_*: list per unit of the run times (None = held). Cluster bootstrap of median_a - median_b."""
    def med(ts, idx):
        tt = [x for i in idx for x in ts[i]]
        return km_median([T if x is None else x for x in tt], [x is not None for x in tt])
    n = len(times_a)
    full = np.arange(n)
    ma, mb = med(times_a, full), med(times_b, full)
    v = []
    for _ in range(2000):
        i = rng.integers(0, n, n)
        a, b = med(times_a, i), med(times_b, i)
        v.append((T if a is None else a) - (T if b is None else b))
    return {"median_first_s": ma, "median_second_s": mb,
            "diff_s_held_as_T": (T if ma is None else ma) - (T if mb is None else mb),
            "cluster_boot95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))],
            "note": "median not reached is set to T for the difference"}


def rmst(ts, T):
    return float(np.mean([T if x is None else min(x, T) for x in ts]))


# ------------------------------------------------------------------ loading
def load_lone():
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]
    snaps = {s["tag"]: s for s in sel}
    runs = defaultdict(dict)       # (tag, arm) -> rep -> exit time or None
    for r in jl(os.path.join(DATA, "E2", "e2_quench.jsonl")):
        tag, arm, rep = r["job_id"].split("|")
        t = r["exits"].get(str(snaps[tag]["blocker"]))
        runs[(tag, arm)][rep] = t if (t is not None and t <= T_Q + 1e-9) else None
    tags = {"lone": [s["tag"] for s in sel if s["class"] == "lone_keystone"],
            "second": [s["tag"] for s in sel if s["class"] == "lone_keystone_second_trap"]}
    n1 = defaultdict(dict)
    for r in jl(os.path.join(DATA, "N1", "n1.jsonl")):
        tag = r["job_id"].split("|")[0]
        t = r["exits"].get(str(snaps[tag]["blocker"]))
        n1[tag][r["rep"]] = t if (t is not None and t <= T_Q + 1e-9) else None
    return snaps, runs, tags, n1


def det_u(runs, tag, arm):
    return runs[(tag, arm)]["u"]


def det_replay_changes(runs, tag, arm):
    rr = runs[(tag, arm)]
    f0 = rr["u"] is not None
    return any((v is not None) != f0 for k, v in rr.items() if k != "u")


# ------------------------------------------------------------------ comparison builders
def noise_vs_orca_lone(runs, T, noise_times, label):
    """noise_times: tag -> list of exit times (None held). ORCA (RVO2) from E2."""
    c = np.array([det_u(runs, t, "C3_rvo2") is not None for t in T])
    p = np.array([np.mean([x is not None for x in noise_times[t]]) for t in T])
    nseed = len(noise_times[T[0]])
    P = {}
    fr = paired_cont(p - c, "paired sign-flip on per-snapshot freed fraction")
    maj = p > 0.5
    fr["majority_mcnemar"] = mcn(maj, c)
    fr["noise_freed_runs"] = int(sum(sum(x is not None for x in noise_times[t]) for t in T))
    fr["noise_runs"] = nseed * len(T)
    fr["orca_freed"] = int(c.sum())
    P["freed"] = fr
    ch_n = np.array([0 < sum(x is not None for x in noise_times[t]) < nseed for t in T])
    ch_o = np.array([det_replay_changes(runs, t, "C3_rvo2") for t in T])
    P["replay"] = mcn(ch_n, ch_o)
    P["replay"]["definition"] = (f"noise: seeds disagree on freed ({nseed} seeds); ORCA: any of five 1e-9 m "
                                 "replays changes the outcome")
    rn = np.array([rmst(noise_times[t], T_Q) for t in T])
    ro = np.array([rmst([det_u(runs, t, "C3_rvo2")], T_Q) for t in T])
    P["time"] = paired_cont(rn - ro, "paired sign-flip on RMST(120 s)")
    P["time"]["rmst_first_s"], P["time"]["rmst_second_s"] = float(rn.mean()), float(ro.mean())
    P["time"]["km"] = km_median_diff([noise_times[t] for t in T], [[det_u(runs, t, "C3_rvo2")] for t in T], T_Q)
    return P, c, p


def ell_probe():
    R = jl(os.path.join(DATA, "E3", "e3_dt.jsonl"))
    by = defaultdict(list)
    for r in R:
        by[(r["job_id"].split("|")[0], r["mode"], r["dt"])].append(r)
    tags = sorted({k[0] for k in by})
    rows = []
    for t in tags:
        def lam(dt):
            rr = by[(t, "per_step", dt)]
            d = sum(not r["censored"] for r in rr)
            return d / sum(r["t_run"] for r in rr) if d else None
        la, lb = lam(0.005), lam(0.02)
        c3 = {dt: by[(t, "C3_rvo2", dt)][0] for dt in (0.005, 0.01, 0.02)}
        freed = all(not r["censored"] for r in c3.values())
        ell_n = np.log(la / lb) if la and lb else None
        ell_o = float(np.log(c3[0.02]["escape_t"] / c3[0.005]["escape_t"])) if freed else None
        rows.append({"tag": t, "beta_ref": by[(t, "per_step", 0.01)][0]["beta_ref"], "ell_noise": ell_n,
                     "ell_orca": ell_o, "orca_freed_all_dt": freed})
    use = [r for r in rows if r["ell_noise"] is not None and r["ell_orca"] is not None]
    d = np.array([r["ell_noise"] - r["ell_orca"] for r in use])
    o = paired_cont(d, "exact sign-flip on per-snapshot ell(noise) - ell(ORCA)")
    o["n_snapshots_E3"] = len(tags)
    o["orca_held_all_dt"] = sum(not r["orca_freed_all_dt"] for r in rows)
    o["ell_noise_mean"] = float(np.mean([r["ell_noise"] for r in use]))
    o["ell_orca_mean"] = float(np.mean([r["ell_orca"] for r in use]))
    o["ell_orca_maxabs"] = float(np.max(np.abs([r["ell_orca"] for r in use])))
    o["rows"] = rows
    return o


def overlap_N1(runs, T, n1):
    """Disagreement of unresolved sets: noise half vs ORCA (mean of both halves) against half vs half."""
    Uc = np.array([det_u(runs, t, "C3_rvo2") is None for t in T])
    k1 = np.array([sum(n1[t][i] is not None for i in range(10)) for t in T])
    k2 = np.array([sum(n1[t][i] is not None for i in range(10, 20)) for t in T])
    U1, U2 = k1 < 5, k2 < 5
    e = ((U1 != Uc).astype(float) + (U2 != Uc).astype(float)) / 2
    r = (U1 != U2).astype(float)
    o = paired_cont(e - r, "paired sign-flip on disagreement (noise half vs ORCA) - (noise half vs half)")
    kall = k1 + k2
    o.update({"J_noise_orca": jaccard(kall < 10, Uc), "J_half_half": jaccard(U1, U2),
              "J_half_orca": [jaccard(U1, Uc), jaccard(U2, Uc)],
              "disagree_rate_noise_orca": float(e.mean()), "disagree_rate_half_half": float(r.mean())})
    return o


def whole():
    A = {r["seed"]: r for r in jl(os.path.join(DATA, "E6", "e6a.jsonl"))}
    Bn = {r["seed"]: r for r in jl(os.path.join(DATA, "E6", "e6b.jsonl"))}
    N2 = {r["seed"]: r for r in jl(os.path.join(DATA, "N2", "n2.jsonl"))}
    seeds = sorted(A)
    assert seeds == sorted(Bn) == sorted(N2)
    comp = {k: np.array([bool(D[s]["complete"]) for s in seeds]) for k, D in (("A", A), ("B", Bn), ("N", N2))}
    tim = {k: np.array([D[s]["evacuation_time"] if D[s]["complete"] else T_W for s in seeds])
           for k, D in (("A", A), ("B", Bn), ("N", N2))}
    out = {}
    for name, k, ref in (("whole_E6", "B", "N"), ("whole_N2", "N", "B")):
        P = {}
        P["freed"] = mcn(comp[k], comp["A"])
        P["freed"]["test"] = "exact McNemar on completion"
        fa, fk, fr = ~comp["A"], ~comp[k], ~comp[ref]
        P["overlap"] = mcn(fa != fr, fk != fr)
        P["overlap"]["test"] = "exact McNemar: [ORCA != ref noise] vs [noise != ref noise]"
        P["overlap"].update({"J_noise_orca": jaccard(fk, fa), "J_noise_noise": jaccard(fk, fr),
                             "reference_stream": {"N": "N2", "B": "E6b"}[ref]})
        d = tim[k] - tim["A"]
        P["time"] = paired_cont(d, "paired sign-flip on RMST(600 s)")
        P["time"]["rmst_first_s"], P["time"]["rmst_second_s"] = float(tim[k].mean()), float(tim["A"].mean())
        both = comp[k] & comp["A"]
        nf = int(np.sum(tim["A"][both] < tim[k][both]))
        P["time"]["both_complete"] = int(both.sum())
        P["time"]["orca_faster_on_both"] = nf
        P["time"]["sign_test_both_p"] = float(stats.binomtest(nf, int(both.sum()), 0.5).pvalue)
        P["time"]["km"] = {"median_first_s": km_median(tim[k], comp[k]), "median_second_s": km_median(tim["A"], comp["A"])}
        out[name] = P
    # replay analogue for noise only (no ORCA whole-run replays exist)
    ch = comp["B"] != comp["N"]
    out["whole_noise_stream_changes"] = {"seeds_changed": int(ch.sum()), "n": len(seeds),
                                         "note": "E6b vs N2 completion differs; ORCA has no whole-run replays, "
                                                 "so replay is not a paired probe here"}
    cls = fix_a6.part_class(rng)
    out["whole_E6"]["class"] = {"test": "within-seed permutation of final-state class (chi-square)",
                                "p": cls["p_within_seed_perm"], "chi2": cls["chi2_all"],
                                "effect": None, "ci95": None,
                                "n_fail_orca": cls["n_fail_C3_rvo2"], "n_fail_noise": cls["n_fail_C1_sigma"],
                                "shared_failed_seeds": cls["n_shared_seeds"],
                                "p_shared_seeds_only": cls["shared_seeds_only"]["p_within_seed_perm"],
                                "p_single_solver_failures_only": cls["single_solver_failures_only"]["p_perm"]}
    return out


def pair():
    fr = defaultdict(dict)
    side = {}
    for p in (os.path.join(DATA, "E7b", "e7b_quench.jsonl"), os.path.join(DATA, "E7b_bstar", "bstar_quench.jsonl")):
        for r in jl(p):
            tag, arm, rep = r["job_id"].split("|")
            ok = bool(r["freed"] and r["first_t"] is not None and r["first_t"] <= T_Q + 1e-9)
            fr[(tag, arm)][rep] = r["first_t"] if ok else None
            if rep == "u":
                side[(tag, arm)] = r["first_side"] if ok else None
    S = {r["job_id"]: r for r in jl(os.path.join(DATA, "E7b", "e7b_static.jsonl"))}
    tags = sorted(S, key=lambda t: S[t]["seed"])
    out = {}
    for name, xa, ya in (("pair_pub", "bstar_pub+", "C3_pub"), ("pair_rvo2", "bstar_rvo2+", "C3_rvo2")):
        x = np.array([fr[(t, xa)]["u"] is not None for t in tags])
        y = np.array([fr[(t, ya)]["u"] is not None for t in tags])
        P = {"freed": mcn(x, y)}
        rx = np.array([det_replay_changes(fr, t, xa) for t in tags])
        ry = np.array([det_replay_changes(fr, t, ya) for t in tags])
        P["replay"] = mcn(rx, ry)
        P["replay"]["replays_per_arm"] = 5 * len(tags)
        ref = rx | ry
        P["overlap"] = mcn(x != y, ref)
        P["overlap"]["test"] = "exact McNemar: [bias != ORCA] vs [replay != unperturbed]"
        P["overlap"]["J_freed"] = jaccard(x, y)
        tx = np.array([rmst([fr[(t, xa)]["u"]], T_Q) for t in tags])
        ty = np.array([rmst([fr[(t, ya)]["u"]], T_Q) for t in tags])
        P["time"] = paired_cont(tx - ty, "paired sign-flip on RMST(120 s)")
        P["time"]["rmst_first_s"], P["time"]["rmst_second_s"] = float(tx.mean()), float(ty.mean())
        lx = [side[(t, xa)] == "lower" for t in tags if x[tags.index(t)]]
        ly = [side[(t, ya)] == "lower" for t in tags if y[tags.index(t)]]
        tab = [[sum(lx), len(lx) - sum(lx)], [sum(ly), len(ly) - sum(ly)]]
        both = [t for i, t in enumerate(tags) if x[i] and y[i]]
        bl = np.array([side[(t, xa)] == "lower" for t in both], bool)
        ol = np.array([side[(t, ya)] == "lower" for t in both], bool)
        fx, fy = sum(lx) / len(lx), sum(ly) / len(ly)
        P["handed"] = {"test": "Fisher exact, lower-first fraction", "p": float(stats.fisher_exact(tab)[1]),
                       "table": tab, "effect": fx - fy, "ci95": None,
                       "bias_lower_first": [sum(lx), len(lx)], "orca_lower_first": [sum(ly), len(ly)],
                       "bias_binom_p": float(stats.binomtest(sum(lx), len(lx), 0.5).pvalue),
                       "orca_binom_p": float(stats.binomtest(sum(ly), len(ly), 0.5).pvalue),
                       "paired_on_both_freed": (mcn(bl, ol) if len(both) else None)}
        # Newcombe-free bootstrap CI of the lower-first difference (freed sets resampled within arm)
        lxa, lya = np.array(lx, float), np.array(ly, float)
        bx = lxa[rng.integers(0, len(lxa), (B, len(lxa)))].mean(1)
        by_ = lya[rng.integers(0, len(lya), (B, len(lya)))].mean(1)
        P["handed"]["ci95"] = [float(np.percentile(bx - by_, 2.5)), float(np.percentile(bx - by_, 97.5))]
        out[name] = P
    return out


def push(runs, tags):
    out = {}
    for name, g in (("push_lone", "lone"), ("push_second", "second")):
        T = tags[g]
        x = np.array([det_u(runs, t, "frozen_plus") is not None for t in T])
        y = np.array([det_u(runs, t, "C3_rvo2") is not None for t in T])
        P = {"freed": mcn(x, y)}
        rx = np.array([det_replay_changes(runs, t, "frozen_plus") for t in T])
        ry = np.array([det_replay_changes(runs, t, "C3_rvo2") for t in T])
        P["replay"] = mcn(rx, ry)
        P["overlap"] = mcn(x != y, rx | ry)
        P["overlap"]["test"] = "exact McNemar: [push != ORCA] vs [replay != unperturbed]"
        tx = np.array([rmst([det_u(runs, t, "frozen_plus")], T_Q) for t in T])
        ty = np.array([rmst([det_u(runs, t, "C3_rvo2")], T_Q) for t in T])
        P["time"] = paired_cont(tx - ty, "paired sign-flip on RMST(120 s)")
        P["time"]["rmst_first_s"], P["time"]["rmst_second_s"] = float(tx.mean()), float(ty.mean())
        both = x & y
        P["time"]["median_paired_dt_both_freed_s"] = float(np.median(tx[both] - ty[both])) if both.any() else None
        P["time"]["both_freed_n"] = int(both.sum())
        P["time"]["push_faster_n"] = int(np.sum(tx[both] < ty[both]))
        P["time"]["paired_dt_range_s"] = ([float(np.min(tx[both] - ty[both])), float(np.max(tx[both] - ty[both]))]
                                          if both.any() else None)
        out[name] = P
    return out


KIND = {"freed": "empirical", "replay": "definitional", "time": "empirical", "ell": "definitional",
        "overlap": "empirical", "handed": "definitional", "class": "empirical"}
KIND_DET = {"replay": "empirical"}     # two deterministic perturbations: replay equality is measured


def finish(C, deterministic):
    names = list(C)
    adj = holm([C[k]["p"] for k in names])
    for k, a in zip(names, adj):
        P = C[k]
        P["p_holm"] = a
        P["separates"] = bool(a < 0.05)
        P["kind"] = (KIND_DET.get(k, KIND[k]) if deterministic else KIND[k])
        P["p_disp"], P["p_holm_disp"] = pdisp(P["p"]), pdisp(a)
        if P.get("effect") is not None:
            P["effect_2sf"] = sig(P["effect"], 2)
        if P.get("ci95"):
            P["ci95_2sf"] = [sig(v, 2) for v in P["ci95"]]
    return C


def main():
    snaps, runs, tags, n1 = load_lone()
    res = {"script": "experiments/revision/A7_paired.py", "doc": __doc__, "n_boot": B, "rng": f"default_rng({SEED})"}
    T = tags["lone"]
    e2n = {t: [runs[(t, "noise0.07")][str(i)] for i in range(5)] for t in T}
    P, _, _ = noise_vs_orca_lone(runs, T, e2n, "E2")
    P["ell"] = ell_probe()
    res["lone_E2"] = finish(P, False)
    n1t = {t: [n1[t][i] for i in range(20)] for t in T}
    P, _, _ = noise_vs_orca_lone(runs, T, n1t, "N1")
    P["overlap"] = overlap_N1(runs, T, n1)
    res["lone_N1"] = finish(P, False)
    T2 = tags["second"]
    e2s = {t: [runs[(t, "noise0.07")][str(i)] for i in range(5)] for t in T2}
    P, _, _ = noise_vs_orca_lone(runs, T2, e2s, "E2 second")
    res["second"] = finish(P, False)
    W = whole()
    res["whole_noise_stream_changes"] = W.pop("whole_noise_stream_changes")
    for k, v in W.items():
        res[k] = finish(v, False)
    for k, v in pair().items():
        res[k] = finish(v, True)
    for k, v in push(runs, tags).items():
        res[k] = finish(v, True)
    res["n_units"] = {"lone": len(T), "second": len(T2), "whole": 186, "pair": 46}
    # summary counts
    rows = [(c, p) for c in COMPS for p in res[c] if isinstance(res[c][p], dict) and "p_holm" in res[c][p]]
    res["summary"] = {"tests": len(rows), "separating": sum(res[c][p]["separates"] for c, p in rows),
                      "separating_empirical": sum(res[c][p]["separates"] and res[c][p]["kind"] == "empirical"
                                                  for c, p in rows)}
    write_tables(res)
    path = revlib.out_json("A7", res)
    return res, path


COMPS = ["lone_E2", "lone_N1", "second", "whole_E6", "whole_N2", "pair_pub", "pair_rvo2", "push_lone",
         "push_second"]
CLAB = {"lone_E2": "Lone keystone: noise $\\sigma=0.07$ (E2, 5 seeds) vs ORCA (RVO2)",
        "lone_N1": "Lone keystone: noise $\\sigma=0.0717$ (N1, 20 seeds) vs ORCA (RVO2)",
        "second": "Second trap: noise $\\sigma=0.07$ (E2) vs ORCA (RVO2)",
        "whole_E6": "Whole runs: noise $\\sigma^\\ast$ (E6b) vs ORCA (RVO2)",
        "whole_N2": "Whole runs: noise $\\sigma^\\ast$, independent stream (N2) vs ORCA (RVO2)",
        "pair_pub": "Pair standoff: bias $+b^\\ast_{\\rm legacy}$ vs ORCA (legacy)",
        "pair_rvo2": "Pair standoff: bias $+b^\\ast_{\\rm RVO2}$ vs ORCA (RVO2)",
        "push_lone": "Lone keystone: rest-drive push $+$ vs ORCA (RVO2)",
        "push_second": "Second trap: rest-drive push $+$ vs ORCA (RVO2)"}
PLAB = {"freed": "freed fraction", "replay": "replay changes", "time": "time to free (RMST)",
        "ell": "$\\Delta t$ dependence $\\ell$", "overlap": "outcome identity", "handed": "handedness (lower first)",
        "class": "final-state class"}
TLAB = {"exact McNemar": "McNemar", "exact McNemar on completion": "McNemar",
        "Fisher exact, lower-first fraction": "Fisher"}


def tshort(P):
    t = P["test"]
    if t.startswith("exact McNemar"):
        return "McNemar"
    if t.startswith("Fisher"):
        return "Fisher"
    if t.startswith("within-seed"):
        return "perm. (within seed)"
    return "sign-flip"


def eff_str(c, k, P, tex):
    def g(v):
        return "0" if v == 0 else f"{sig(v, 2):+g}"

    def f(v, unit=""):
        return g(v) + unit
    if k == "class":
        return f"$\\chi^2={P['chi2']:.1f}$" if tex else f"chi2 = {P['chi2']:.1f}"
    u = " s" if k == "time" else ""
    s = f(P["effect"], u)
    if P.get("ci95"):
        s += f" [{g(P['ci95'][0])}, {g(P['ci95'][1])}]"
    if "b_first_only" in P:
        s += f" ({P['b_first_only']}:{P['c_second_only']})"
    if tex:
        s = "$" + s.replace("[", "[").replace(" s", "\\,{\\rm s}") + "$"
    return s


def ptex(p):
    d = pdisp(p)
    return f"${d}$" if d.startswith("<") else d


def write_tables(res):
    md = ["| Comparison | Probe | Test | Effect [95% CI] (discordant) | raw p | Holm p | Separates | Kind |",
          "|---|---|---|---|---|---|---|---|"]
    tex = ["% A7: paired difference tests (experiments/revision/A7_paired.py -> data/derived/rev_A7.json); not \\input",
           "\\begin{tabular}{@{}llllllll@{}}", "\\toprule",
           "Comparison & Probe & Test & Effect [95\\% CI] & $p$ & $p_{\\rm Holm}$ & Sep. & Kind \\\\", "\\midrule"]
    for ci, c in enumerate(COMPS):
        C = res[c]
        ks = [k for k in C if isinstance(C[k], dict) and "p_holm" in C[k]]
        if ci:
            tex.append("\\midrule")
        tex.append(f"\\multicolumn{{8}}{{@{{}}l}}{{\\emph{{{CLAB[c]}}}}} \\\\")
        for k in ks:
            P = C[k]
            md.append(f"| {CLAB[c].replace('$', '').replace(chr(92), '')} | {PLAB[k].replace('$', '').replace(chr(92), '')} | "
                      f"{tshort(P)} | {eff_str(c, k, P, False)} | {pdisp(P['p'])} | {pdisp(P['p_holm'])} | "
                      f"{'yes' if P['separates'] else 'no'} | {P['kind']} |")
            tex.append(f" & {PLAB[k]} & {tshort(P)} & {eff_str(c, k, P, True)} & {ptex(P['p'])} & "
                       f"{ptex(P['p_holm'])} & {'yes' if P['separates'] else 'no'} & "
                       f"{'def.' if P['kind'] == 'definitional' else 'emp.'} \\\\")
    tex += ["\\bottomrule", "\\end{tabular}"]
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes")
    open(os.path.join(d, "A7_table.tex"), "w").write("\n".join(tex) + "\n")
    res["_markdown_table"] = "\n".join(md)


if __name__ == "__main__":
    r, path = main()
    for c in COMPS:
        for k, P in r[c].items():
            if isinstance(P, dict) and "p_holm" in P:
                print(f"{c:12s} {k:8s} eff={P.get('effect')} ci={P.get('ci95')} p={P['p']:.3g} "
                      f"holm={P['p_holm']:.3g} sep={P['separates']} {P['kind']}")
    print(r["_markdown_table"])
    print(r["summary"], path)
