#!/usr/bin/env python3
"""fix_a1: references for the Jaccard identity signature of Table 3 (referee issue S1.1).

Input:  data/E2/e2_quench.jsonl, data/derived/selection.json, data/E1/E1_runs.jsonl (blocker rest-state
        margins), data/BAR/barriers_gated.json (gated string-method barriers of the 60 E2 snapshots),
        data/E6/e6a.jsonl + e6b.jsonl (whole runs), data/E7b/e7b_quench.jsonl +
        data/E7b_bstar/bstar_quench.jsonl (pair standoffs).
Output: data/derived/fix_a1.json.

Rules (identical to experiments/E2/analyze.py, experiments/E6/analyze.py, experiments/E7b/analyze.py):
  lone trap   blocker exits within 120 s; C3 RVO2 judged on its unperturbed run; a snapshot is
              noise-unresolved when fewer than half of its noise seeds free it (5 seeds: k <= 2).
              A half-sample of m seeds uses the same rule within the half (m = 2: k = 0; m = 3: k <= 1).
  whole runs  a seed fails when the run is not complete at 600 s (C3 RVO2, E6a; C1 + sigma*, E6b).
  pair block  freed within 120 s on the unperturbed run; Table 3 compares the freed sets.
  J           |A & B| / |A | B| of the minority outcome sets.
Independence  both minority sets drawn uniformly at random with their observed sizes a, b from the same N
              snapshots/seeds: the overlap X is hypergeometric(N, a, b) and J = X / (a + b - X); its exact
              mean, 95% range and tail probabilities are reported.
Intervals     95% percentile intervals; snapshot (or seed) bootstrap with multiplicity, B = 10000; the lone
              trap also has a two-level bootstrap (snapshots, then the 5 seeds within each snapshot).
RNG           numpy default_rng(20261109) for everything.
"""
import itertools
import json
import os
from collections import defaultdict

import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "fix_a1.json")
T_Q = 120.0
B = 10000
RNG = np.random.default_rng(20261109)
NOISE_ARMS = ["noise0.03", "noise0.05", "noise0.07"]
MAIN_NOISE = "noise0.07"


# ----------------------------------------------------------------------------- helpers
def jac(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else float("nan")


def jac_w(a, b, w):
    """Jaccard with multiplicity weights w (bootstrap counts)."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    u = (w * (a | b)).sum()
    return float((w * (a & b)).sum() / u) if u else float("nan")


def pct(v, lo=2.5, hi=97.5):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return [float(np.percentile(v, lo)), float(np.percentile(v, hi))] if len(v) else None


def summary(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return {"n_draws_finite": int(len(v)), "mean": float(v.mean()), "median": float(np.median(v)),
            "range95": pct(v)}


def hyper_j(N, a, b, j_obs=None):
    """Exact distribution of J when sets of sizes a and b are drawn independently from N."""
    rv = stats.hypergeom(N, a, b)
    xs = np.arange(max(0, a + b - N), min(a, b) + 1)
    p = rv.pmf(xs)
    js = np.array([x / (a + b - x) if (a + b - x) else np.nan for x in xs])
    cdf = np.cumsum(p)
    out = {"N": int(N), "size_a": int(a), "size_b": int(b), "expected_overlap": float(a * b / N),
           "expected_J": float(np.nansum(p * js)),
           "J_range95": [float(js[np.searchsorted(cdf, 0.025)]), float(js[np.searchsorted(cdf, 0.975)])],
           "method": "exact hypergeometric overlap X ~ H(N, a, b), J = X/(a+b-X)"}
    if j_obs is not None:
        out["p_J_ge_observed"] = float(p[js >= j_obs - 1e-12].sum())
        out["p_J_le_observed"] = float(p[js <= j_obs + 1e-12].sum())
    return out


def boot_seed_level(a, b, n_boot=B):
    """Bootstrap of units (snapshots or seeds) with multiplicity."""
    n = len(a)
    w = RNG.multinomial(n, np.full(n, 1 / n), size=n_boot)
    return [jac_w(a, b, wi) for wi in w]


def auc(score, label):
    """P(score of a positive > score of a negative), ties 1/2 (Mann-Whitney)."""
    s, y = np.asarray(score, float), np.asarray(label, bool)
    pos, neg = s[y], s[~y]
    if not len(pos) or not len(neg):
        return float("nan")
    g = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(g / (len(pos) * len(neg)))


def boot_stat(f, n, n_boot=B):
    v = []
    for _ in range(n_boot):
        x = f(RNG.integers(0, n, n))
        if x is not None and np.isfinite(x):
            v.append(x)
    return pct(v)


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(stats.spearmanr(x, y).statistic)


def perm_p_two_sided(f, x, y, n_perm=B):
    """Permutation p for a statistic centred at the null value: |f(x, perm y) - c| >= |f(x, y) - c|."""
    s0 = f(x, y)
    c = 0.5 if f is auc else 0.0
    cnt = 0
    for _ in range(n_perm):
        s = f(x, RNG.permutation(y))
        cnt += abs(s - c) >= abs(s0 - c) - 1e-12
    return float((cnt + 1) / (n_perm + 1))


# ----------------------------------------------------------------------------- lone trap (E2)
def load_e2():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))["E2"]["snapshots"]
    snaps = {s["tag"]: s for s in sel}
    e1 = {}
    for line in open(os.path.join(DATA, "E1", "E1_runs.jsonl")):
        r = json.loads(line)
        if r["mode"] == "E1b":
            e1[r["seed"]] = r
    for s in sel:
        a = e1[s["seed"]]["attrs"][s["blocker"]]
        assert a["id"] == s["blocker"]
        s["margin_C3"] = a["margin_C3"]
    bar = json.load(open(os.path.join(DATA, "BAR", "barriers_gated.json")))["barriers"]
    runs = defaultdict(dict)
    for line in open(os.path.join(DATA, "E2", "e2_quench.jsonl")):
        r = json.loads(line)
        tag, arm, rep = r["job_id"].split("|")
        t = r["exits"].get(str(snaps[tag]["blocker"]))
        runs[(tag, arm)][rep] = t is not None and t <= T_Q + 1e-9
    return sel, snaps, bar, runs


def lone_block(sel, snaps, bar, runs, stratum_classes, label):
    T = [s["tag"] for s in sel if s["class"] in stratum_classes]
    n = len(T)
    orca_fail = np.array([not runs[(t, "C3_rvo2")]["u"] for t in T])
    res = {"n_snapshots": n, "orca_arm": "C3_rvo2", "orca_unresolved": int(orca_fail.sum()),
           "orca_unresolved_tags": [t for t, f in zip(T, orca_fail) if f]}
    F = {arm: np.array([[runs[(t, arm)][str(i)] for i in range(5)] for t in T]) for arm in NOISE_ARMS}
    out_arms = {}
    for arm in NOISE_ARMS:
        Fa = F[arm]
        k = Fa.sum(1)
        U = k < 2.5
        o = {"noise_freed_runs": int(k.sum()), "noise_runs": int(Fa.size), "noise_unresolved": int(U.sum()),
             "noise_unresolved_tags": [t for t, f in zip(T, U) if f], "shared": int((U & orca_fail).sum()),
             "J_observed": jac(U, orca_fail)}
        o["J_observed_method"] = "minority (unresolved) sets, noise by majority of 5 seeds (k <= 2), ORCA unperturbed"
        # observed-J intervals
        o["J_ci95_snapshot_boot"] = pct(boot_seed_level(U, orca_fail))
        two = []
        for _ in range(B):
            idx = RNG.integers(0, n, n)
            seeds = RNG.integers(0, 5, (n, 5))
            kk = Fa[idx[:, None], seeds].sum(1)
            two.append(jac(kk < 2.5, orca_fail[idx]))
        o["J_ci95_two_level_boot"] = pct(two)
        o["J_ci_method"] = ("snapshot bootstrap with multiplicity; two-level: resample snapshots, then 5 seeds "
                            "with replacement within each, majority rule recomputed; 10000 draws, percentile")
        o["independence"] = hyper_j(n, int(orca_fail.sum()), int(U.sum()), o["J_observed"])

        # (1a) seed-split pseudo-replicates: 2 seeds against 3 seeds, majority rule within each half
        splits = list(itertools.combinations(range(5), 2))

        def half_sets(Fh_a, Fh_b):
            ua = Fh_a.mean(1) < 0.5
            ub = Fh_b.mean(1) < 0.5
            return ua, ub

        glob = []
        for sa in splits:
            sb = [i for i in range(5) if i not in sa]
            ua, ub = half_sets(Fa[:, list(sa)], Fa[:, sb])
            glob.append({"seeds_2": list(sa), "J_noise2_noise3": jac(ua, ub), "J_noise2_orca": jac(ua, orca_fail),
                         "J_noise3_orca": jac(ub, orca_fail), "size_2": int(ua.sum()), "size_3": int(ub.sum())})
        rnd_nn, rnd_n2o, rnd_n3o, d_nn_minus_no = [], [], [], []
        for _ in range(B):
            perm = np.argsort(RNG.random((n, 5)), axis=1)
            Fp = np.take_along_axis(Fa, perm, 1)
            ua, ub = half_sets(Fp[:, :2], Fp[:, 2:])
            a, b_, c = jac(ua, ub), jac(ua, orca_fail), jac(ub, orca_fail)
            rnd_nn.append(a), rnd_n2o.append(b_), rnd_n3o.append(c)
            d_nn_minus_no.append(a - 0.5 * (b_ + c))
        d = np.asarray(d_nn_minus_no)
        o["split_2v3"] = {
            "rule": ("split each snapshot's 5 seeds into 2 and 3; within each half a snapshot is noise-unresolved "
                     "when fewer than half its seeds free it (2 seeds: none frees; 3 seeds: at most one frees); "
                     "the same halves are also compared with ORCA, so both comparisons use equally few seeds"),
            "global_splits": glob,
            "global_J_noise_noise_median": float(np.nanmedian([g["J_noise2_noise3"] for g in glob])),
            "global_J_noise_noise_range": [float(np.nanmin([g["J_noise2_noise3"] for g in glob])),
                                           float(np.nanmax([g["J_noise2_noise3"] for g in glob]))],
            "random_per_snapshot_splits": {
                "J_noise_noise": summary(rnd_nn), "J_noise2_orca": summary(rnd_n2o),
                "J_noise3_orca": summary(rnd_n3o),
                "J_noise_noise_minus_J_noise_orca": summary(d),
                "frac_J_noise_noise_gt_J_noise_orca": float(np.mean(d[np.isfinite(d)] > 0)),
                "method": "10000 independent random 2|3 splits per snapshot; difference = J(n2,n3) - mean(J(n2,O), J(n3,O))"}}

        # (1b) parametric 5-seed replicates
        def sim_sets(p, m=5):
            return RNG.binomial(m, p) < m / 2

        par = {}
        for name in ("plugin", "jeffreys"):
            nn, no, obs_rep = [], [], []
            for _ in range(B):
                p = k / 5 if name == "plugin" else RNG.beta(k + 0.5, 5 - k + 0.5)
                r1, r2 = sim_sets(p), sim_sets(p)
                nn.append(jac(r1, r2))
                no.append(jac(r1, orca_fail))
                obs_rep.append(jac(U, r1))
            nn = np.asarray(nn)
            par[name] = {"J_noise5_noise5": summary(nn), "J_noise5_orca": summary(no),
                         "J_observed_noise_vs_replicate": summary(obs_rep),
                         "p_J_noise_noise_le_observed_J_noise_orca": float(
                             np.mean(nn[np.isfinite(nn)] <= o["J_observed"] + 1e-12))}
        par["method"] = ("two independent 5-seed replicates per snapshot drawn as Binomial(5, p_i), majority rule; "
                         "plugin: p_i = k_i/5; jeffreys: p_i ~ Beta(k_i + 1/2, 5 - k_i + 1/2) per draw; 10000 draws")
        o["replicate_5seed_parametric"] = par

        # (3) association of noise freeing fraction with ORCA outcome
        frac = k / 5
        nf, nn_ = orca_fail.sum(), (~orca_fail).sum()
        a_fail = auc(-frac, orca_fail)  # lower noise freeing among ORCA-unresolved
        mw = stats.mannwhitneyu(frac[orca_fail], frac[~orca_fail], alternative="two-sided")
        kf, kn = int(k[orca_fail].sum()), int(k[~orca_fail].sum())
        nf5, nn5 = int(5 * nf), int(5 * nn_)
        lor = float(np.log(((kf + 0.5) / (nf5 - kf + 0.5)) / ((kn + 0.5) / (nn5 - kn + 0.5))))

        def lor_idx(i):
            of, kk = orca_fail[i], k[i]
            if of.sum() == 0 or (~of).sum() == 0:
                return None
            a1, n1 = kk[of].sum(), 5 * of.sum()
            a0, n0 = kk[~of].sum(), 5 * (~of).sum()
            return float(np.log(((a1 + 0.5) / (n1 - a1 + 0.5)) / ((a0 + 0.5) / (n0 - a0 + 0.5))))
        perm_cnt = 0
        for _ in range(B):
            pf = RNG.permutation(orca_fail)
            perm_cnt += auc(-frac, pf) >= a_fail - 1e-12
        fisher = stats.fisher_exact([[kf, nf5 - kf], [kn, nn5 - kn]], alternative="less")
        o["association_with_orca"] = {
            "noise_freed_runs_on_orca_unresolved": [kf, nf5], "noise_freed_runs_on_orca_freed": [kn, nn5],
            "mean_freeing_fraction_orca_unresolved": float(frac[orca_fail].mean()) if nf else None,
            "mean_freeing_fraction_orca_freed": float(frac[~orca_fail].mean()),
            "auc_low_noise_freeing_for_orca_unresolved": a_fail,
            "auc_ci95_snapshot_boot": boot_stat(lambda i: auc(-frac[i], orca_fail[i]), n),
            "mannwhitney_two_sided_p": float(mw.pvalue),
            "perm_p_one_sided_auc": float((perm_cnt + 1) / (B + 1)),
            "log_odds_ratio": lor, "odds_ratio": float(np.exp(lor)),
            "log_odds_ratio_ci95_cluster_boot": boot_stat(lor_idx, n),
            "fisher_runs_one_sided_p": float(fisher.pvalue),
            "method": ("AUC = Mann-Whitney P(noise freeing fraction k_i/5 lower on an ORCA-unresolved snapshot), "
                       "ties 1/2; permutation p (ORCA labels across snapshots, 10000, one-sided); log odds ratio "
                       "of a noise run freeing on ORCA-unresolved vs ORCA-freed snapshots = the binomial logistic "
                       "regression coefficient on the ORCA-outcome indicator (+1/2 per cell), interval by snapshot "
                       "(cluster) bootstrap; Fisher exact on runs ignores clustering and is given for reference")}
        out_arms[arm.replace(".", "p")] = o
    res["noise"] = out_arms

    # (4) predictors: barrier dU (gated, full condition) and C3 rest-state margin
    dU = np.array([bar[t]["full"]["dU"] if bar[t]["full"]["accepted"] else np.nan for t in T])
    dUa = np.array([bar[t]["alone"]["dU"] if bar[t]["alone"]["accepted"] else np.nan for t in T])
    mC3 = np.array([snaps[t]["margin_C3"] for t in T])
    mC1 = np.array([snaps[t]["blocker_margin_C1"] for t in T])
    ok = np.isfinite(dU)
    pred = {"n_matched": int(ok.sum()), "n_barrier_failed_gate": int((~ok).sum()),
            "barrier": "data/BAR/barriers_gated.json, condition full (all agents mobile), accepted values only",
            "margin": "blocker rest-state margin under C3 (data/E1/E1_runs.jsonl attrs.margin_C3, as E2 uses)",
            "spearman_dU_margin_C3": spearman(dU[ok], mC3[ok]),
            "spearman_dU_margin_C3_ci95": boot_stat(lambda i: spearman(dU[ok][i], mC3[ok][i]), int(ok.sum())),
            "spearman_dU_margin_C1": spearman(dU[ok], mC1[ok]),
            "spearman_dU_alone_margin_C3": spearman(dUa[np.isfinite(dUa)], mC3[np.isfinite(dUa)])}
    of = orca_fail[ok]
    x_dU, x_m = dU[ok], mC3[ok]
    nok = int(ok.sum())
    pred["orca_fail_auc_margin_C3"] = auc(x_m, of)
    pred["orca_fail_auc_margin_C3_ci95"] = boot_stat(lambda i: auc(x_m[i], of[i]), nok)
    pred["orca_fail_auc_dU"] = auc(x_dU, of)
    pred["orca_fail_auc_dU_ci95"] = boot_stat(lambda i: auc(x_dU[i], of[i]), nok)
    pred["orca_fail_auc_margin_minus_dU_ci95"] = boot_stat(lambda i: auc(x_m[i], of[i]) - auc(x_dU[i], of[i]), nok)
    pred["orca_fail_perm_p_auc_dU"] = perm_p_two_sided(auc, x_dU, of)
    for arm in NOISE_ARMS:
        fr = F[arm].sum(1)[ok] / 5
        un = fr < 0.5
        q = {"n_snapshots_not_always_freed": int((fr < 1).sum()), "n_unresolved_majority": int(un.sum()),
             "spearman_freeing_dU": spearman(fr, x_dU),
             "spearman_freeing_dU_ci95": boot_stat(lambda i: spearman(fr[i], x_dU[i]), nok),
             "spearman_freeing_dU_perm_p": perm_p_two_sided(spearman, x_dU, fr),
             "spearman_freeing_margin_C3": spearman(fr, x_m),
             "spearman_freeing_margin_C3_ci95": boot_stat(lambda i: spearman(fr[i], x_m[i]), nok),
             "spearman_freeing_margin_C3_perm_p": perm_p_two_sided(spearman, x_m, fr),
             "spearman_dU_minus_margin_ci95": boot_stat(
                 lambda i: spearman(fr[i], x_dU[i]) - spearman(fr[i], x_m[i]), nok),
             "auc_dU_for_noise_unresolved": auc(x_dU, un),
             "auc_dU_for_noise_unresolved_ci95": boot_stat(lambda i: auc(x_dU[i], un[i]), nok),
             "auc_margin_C3_for_noise_unresolved": auc(x_m, un),
             "auc_margin_C3_for_noise_unresolved_ci95": boot_stat(lambda i: auc(x_m[i], un[i]), nok)}
        pred[arm.replace(".", "p")] = q
    pred["method"] = ("Spearman rank correlation of the per-snapshot noise freeing fraction k_i/5 with dU and with "
                      "the C3 margin; AUC (Mann-Whitney, ties 1/2) of each predictor for ORCA's unresolved "
                      "snapshots and for noise's majority-unresolved snapshots; snapshot bootstrap 95% intervals "
                      "(10000), two-sided permutation p (10000)")
    res["predictors"] = pred
    res["label"] = label
    return res


# ----------------------------------------------------------------------------- whole runs (E6)
def whole_runs():
    A = {json.loads(l)["seed"]: json.loads(l) for l in open(os.path.join(DATA, "E6", "e6a.jsonl"))}
    Bn = {json.loads(l)["seed"]: json.loads(l) for l in open(os.path.join(DATA, "E6", "e6b.jsonl"))}
    seeds = sorted(A)
    assert seeds == sorted(Bn)
    fa = np.array([not A[s]["complete"] for s in seeds])
    fb = np.array([not Bn[s]["complete"] for s in seeds])
    n = len(seeds)
    J = jac(fa, fb)
    perm = [jac(fa, RNG.permutation(fb)) for _ in range(B)]
    e5_seeds = {json.loads(l)["seed"] for l in open(os.path.join(DATA, "E5", "e5b.jsonl"))}
    return {"n_seeds": n, "C3_rvo2_fail": int(fa.sum()), "noise_sigma_star_fail": int(fb.sum()),
            "both_fail": int((fa & fb).sum()), "discordant": int((fa ^ fb).sum()),
            "union": int((fa | fb).sum()), "J_observed": J,
            "J_ci95_seed_boot": pct(boot_seed_level(fa, fb)),
            "J_ci_method": "seed bootstrap with multiplicity, 10000 draws, percentile",
            "independence": hyper_j(n, int(fa.sum()), int(fb.sum()), J),
            "independence_perm_mean": float(np.mean(perm)), "independence_perm_range95": pct(perm),
            "noise_replicates_per_seed": 1,
            "seeds_shared_with_E5b": len(set(seeds) & e5_seeds),
            "noise_noise_J": None,
            "noise_noise_note": ("E6b has one noise stream per start (seeds 242-427) and no other whole-run noise "
                                 "data share these starts (E5b uses seeds 42-141); J(noise, noise') needs run-N2")}


# ----------------------------------------------------------------------------- pair block (E7b)
def pair_block():
    freed = {}
    for p in (os.path.join(DATA, "E7b", "e7b_quench.jsonl"), os.path.join(DATA, "E7b_bstar", "bstar_quench.jsonl")):
        for ln in open(p):
            if not ln.strip():
                continue
            r = json.loads(ln)
            tag, arm, rep = r["job_id"].split("|")
            if rep == "u":
                freed[(tag, arm)] = bool(r["freed"] and r["first_t"] <= T_Q + 1e-9)
    tags = sorted({t for t, _ in freed}, key=lambda t: int(t.rsplit("seed", 1)[1]))
    out = {}
    for k, (a, b) in {"pub": ("bstar_pub+", "C3_pub"), "rvo2": ("bstar_rvo2+", "C3_rvo2")}.items():
        x = np.array([freed[(t, a)] for t in tags])
        y = np.array([freed[(t, b)] for t in tags])
        n = len(tags)
        J = jac(x, y)
        o = {"bias_arm": a, "orca_arm": b, "n_snapshots": n, "bias_freed": int(x.sum()), "orca_freed": int(y.sum()),
             "both_freed": int((x & y).sum()), "union": int((x | y).sum()), "J_observed": J,
             "J_ci95_snapshot_boot": pct(boot_seed_level(x, y)),
             "independence": hyper_j(n, int(x.sum()), int(y.sum()), J),
             "same_resolver_reference": "both resolvers deterministic (0 of 230 replays change the outcome): J = 1"}
        if (x & y).sum() == 0:
            m = int(min(x.sum(), y.sum()))
            q_hi = float(1 - 0.025 ** (1 / m))  # Clopper-Pearson upper end for 0 of m, two-sided 95%
            X_hi = q_hi * m
            o["J_upper95_cp"] = float(X_hi / (x.sum() + y.sum() - X_hi))
            o["J_upper95_method"] = (f"0 of the {m} snapshots of the smaller freed set are shared; Clopper-Pearson "
                                     f"upper end (two-sided 95%) of the shared fraction, {q_hi:.3f}, converted to J "
                                     "with the observed set sizes")
            o["J_interval95"] = [0.0, o["J_upper95_cp"]]
        out[k] = o
    return out


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main():
    sel, snaps, bar, runs = load_e2()
    out = {"script": "experiments/fixan/fix_a1.py", "doc": __doc__, "rng": "numpy default_rng(20261109)",
           "n_boot": B,
           "lone_keystone": lone_block(sel, snaps, bar, runs, ["lone_keystone"], "lone keystones (Table 3)"),
           "pooled_60": lone_block(sel, snaps, bar, runs, ["lone_keystone", "lone_keystone_second_trap"],
                                   "both lone strata (60 snapshots), supplementary"),
           "whole_runs": whole_runs(), "pair": pair_block()}
    lk = out["lone_keystone"]["noise"]["noise0p07"]
    out["headline"] = {
        "lone_J_noise_orca": lk["J_observed"],
        "lone_J_noise_noise_split_median": lk["split_2v3"]["random_per_snapshot_splits"]["J_noise_noise"]["median"],
        "lone_J_noise_noise_split_range95": lk["split_2v3"]["random_per_snapshot_splits"]["J_noise_noise"]["range95"],
        "lone_J_noise_orca_split_median": lk["split_2v3"]["random_per_snapshot_splits"]["J_noise2_orca"]["median"],
        "lone_J_independent": lk["independence"]["expected_J"],
        "whole_J": out["whole_runs"]["J_observed"], "whole_J_independent": out["whole_runs"]["independence"]["expected_J"],
        "pair_pub_J": out["pair"]["pub"]["J_observed"],
        "pair_pub_J_independent": out["pair"]["pub"]["independence"]["expected_J"],
        "pair_rvo2_J": out["pair"]["rvo2"]["J_observed"],
        "pair_rvo2_J_independent": out["pair"]["rvo2"]["independence"]["expected_J"]}
    json.dump(clean(out), open(OUT, "w"), indent=1)
    print(f"wrote {OUT}")
    print(json.dumps(out["headline"], indent=1))


if __name__ == "__main__":
    main()
