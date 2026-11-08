"""Split-sample recalibration of the rate-matched controls (FIX_PLAN A-2, referee issue S1.3).

The paper fits each matched control to ORCA's freed fraction on a snapshot library and then reports the
rate match on the same library, where it holds by construction. Here the library is halved at random
(N_SPLIT seeded halvings) and, for each halving, the control is fitted on one half (fit half) and
evaluated on the other (test half), in both directions (2-fold). Delta is always
  control freed fraction on the test half  -  ORCA freed fraction on the test half.
As a reference, delta_rate_transfer is ORCA's fit-half minus test-half freed fraction: the error of a
control that reproduces the fit-half rate exactly and is otherwise unrelated to the test half. A fixed
canonical split (snapshot index parity, even indices = half 0) is reported as well, with a 95%
percentile bootstrap interval over the test-half snapshots (fit held fixed).

(a) Pair standoffs (E7b, 46 snapshots). Fit rule as experiments/E7b/matched_b.py fit, applied to the fit
    half: with k = ORCA count and t_(1) <= ... the sorted static fold thresholds (+ sign) of the fit half,
    b* = midpoint of [t_(k), t_(k+1)] (t_(0) = 0). Test-half prediction:
      static     freed iff t_i <= b* (the rule the fit uses);
      quench     the unperturbed C1 + bias quench outcome at b*, bracketed from the quench levels that exist
                 per snapshot (+0.01, 0.02, 0.03, 0.05, 0.1 and the two full-library b*): freed if some level
                 <= b* frees, held if some level >= b* holds, else (no bracket or non-monotone) the static
                 prediction is used; the number of fallbacks is reported.
    Targets: C3 published and C3 RVO2. Signatures on the test half from the static prediction: freed-set
    Jaccard against ORCA, and handedness (side of the first-out member at threshold, + sign).
    Replay disagreements and median time to free need runs at b*; they exist only at the full-library b*,
    and are given restricted to the canonical test halves.
(b) Lone keystone (E2, 34 snapshots, 5 noise seeds each). sigma is re-picked on the fit half from the grid
    {0.03, 0.05, 0.07} m/s as the level whose per-run freed fraction is nearest to C3 RVO2's freed fraction
    (ties to the larger sigma). Test half: Delta, unresolved-set Jaccard (majority rule, < 3 of 5 seeds),
    snapshots whose seeds disagree, Kaplan-Meier median time to free, and C3 RVO2 replay disagreements.
(c) Whole runs (E6, 186 spawns, paired seeds). sigma* inverts the E5b logistic completion fit
    (data/derived/sigma_star.json, independent spawns) at C3 RVO2's completion rate. Refit: sigma*_fit from
    the fit half's C3 RVO2 rate. Noise runs exist only at the full-library sigma* = 0.0467 m/s, so the test
    half is evaluated (i) as observed at sigma* = 0.0467 (only the target rate is shared with the test half)
    and (ii) shifted by the logistic fit, P(sigma*_fit) - P(0.0467), added to the observed test-half rate.
"""
import json
import math
import os
from collections import defaultdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "fix_a2.json")
T_Q = 120.0
N_SPLIT = 200
N_BOOT = 2000
SEED = 20261109


def jl(path):
    return [json.loads(ln) for ln in open(path) if ln.strip()]


def pct(v):
    v = np.asarray(v, float)
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def dist(v):
    v = np.asarray(v, float)
    return {"mean": float(v.mean()), "median": float(np.median(v)), "range95": pct(v),
            "min": float(v.min()), "max": float(v.max()), "n": int(len(v))}


def halvings(n, rng):
    out = []
    for _ in range(N_SPLIT):
        p = rng.permutation(n)
        m = np.zeros(n, bool)
        m[p[: n // 2]] = True
        out.append(m)
    return out


def parity(n):
    return np.arange(n) % 2 == 0


def boot_diff(a, b, rng):
    """95% percentile bootstrap of mean(a - b) over units (paired)."""
    d = np.asarray(a, float) - np.asarray(b, float)
    n = len(d)
    v = [d[rng.integers(0, n, n)].mean() for _ in range(N_BOOT)]
    return pct(v)


def jaccard(x, y):
    u = (x | y).sum()
    return float((x & y).sum() / u) if u else None


def km_median(times, events):
    t = np.round(np.asarray(times, float), 2)
    e = np.asarray(events, bool)
    o = np.argsort(t, kind="stable")
    t, e = t[o], e[o]
    S, n, i = 1.0, len(t), 0
    while i < n:
        j, d = i, 0
        while j < n and t[j] == t[i]:
            d += int(e[j])
            j += 1
        if d:
            S *= 1 - d / (n - i)
            if S <= 0.5 + 1e-12:
                return float(t[i])
        i = j
    return None


# ------------------------------------------------------------------ (a) pair standoffs
def pair_block(rng):
    D7, DB = os.path.join(DATA, "E7b"), os.path.join(DATA, "E7b_bstar")
    S = {r["job_id"]: r for r in jl(os.path.join(D7, "e7b_static.jsonl"))}
    tags = sorted(S, key=lambda t: S[t]["seed"])
    N = len(tags)
    th, side = {}, {}
    for r in jl(os.path.join(DB, "fold_threshold.jsonl")):
        if r["sign"] == 1:
            th[r["tag"]] = np.inf if r["b_star"] is None else r["b_star"]
            side[r["tag"]] = r["first_side_at_hi"]
    T = np.array([th[t] for t in tags])
    lowfirst_bias = np.array([side[t] == "lower" for t in tags])
    runs = defaultdict(dict)
    for path in (os.path.join(D7, "e7b_quench.jsonl"), os.path.join(DB, "bstar_quench.jsonl")):
        for r in jl(path):
            tag, arm, rep = r["job_id"].split("|")
            r["_freed"] = bool(r["freed"] and r["first_t"] is not None and r["first_t"] <= T_Q + 1e-9)
            runs[(tag, arm)][rep] = r
    full = json.load(open(os.path.join(DB, "bstar.json")))["fits"]
    levels = {0.01: "bias0.01", 0.02: "bias0.02", 0.03: "bias0.03", 0.05: "bias0.05", 0.1: "bias0.1",
              full["pub"]["b_star"]: "bstar_pub+", full["rvo2"]["b_star"]: "bstar_rvo2+"}
    Q = {lv: np.array([runs[(t, a)]["u"]["_freed"] for t in tags]) for lv, a in levels.items()}

    def fit(mask, k):
        t = np.sort(T[mask])
        n = len(t)
        lo = t[k - 1] if k > 0 else 0.0
        hi = t[k] if k < n else lo
        if not np.isfinite(hi):
            hi = lo
        return 0.5 * (lo + hi)

    def quench_pred(b, idx):
        pred, fb = [], 0
        for i in idx:
            f = any(Q[lv][i] for lv in Q if lv <= b + 1e-12)
            h = any(not Q[lv][i] for lv in Q if lv >= b - 1e-12)
            if f != h:
                pred.append(f)
            else:
                pred.append(T[i] <= b)
                fb += 1
        return np.array(pred, bool), fb

    out = {"n_snapshots": N, "method": "fit b* on one half by the matched_b.py rule, predict the other half; "
           "Delta = control minus ORCA freed fraction on the test half"}
    split_list = halvings(N, rng)
    for key, f in full.items():
        orca_arm = f["arm"]
        y = np.array([runs[(t, orca_arm)]["u"]["_freed"] for t in tags])
        y_low = np.array([runs[(t, orca_arm)]["u"]["first_side"] == "lower" if runs[(t, orca_arm)]["u"]["_freed"]
                          else False for t in tags])
        b_full = f["b_star"]
        static_full = T <= b_full
        bias_arm = f"bstar_{key}+"
        x_full = np.array([runs[(t, bias_arm)]["u"]["_freed"] for t in tags])

        def evaluate(fit_mask):
            test = ~fit_mask
            idx = np.where(test)[0]
            b = fit(fit_mask, int(y[fit_mask].sum()))
            ps = T[test] <= b
            pq, fb = quench_pred(b, idx)
            yt = y[test]
            return {"ref": float(y[fit_mask].mean() - y[test].mean()),
                    "b": float(b), "d_static": float(ps.mean() - yt.mean()), "d_quench": float(pq.mean() - yt.mean()),
                    "fallback": fb, "n_test": int(test.sum()), "k_orca_test": int(yt.sum()),
                    "k_static": int(ps.sum()), "k_quench": int(pq.sum()), "jac": jaccard(ps, yt),
                    "jac_q": jaccard(pq, yt), "pred_static": ps, "pred_quench": pq, "idx": idx,
                    "hand_bias": [int((ps & lowfirst_bias[test]).sum()), int(ps.sum())],
                    "hand_orca": [int((yt & y_low[test]).sum()), int(yt.sum())]}

        R = [evaluate(m) for s in split_list for m in (s, ~s)]
        # cross-fitted: each snapshot predicted from the fold that excludes it
        cf_s, cf_q, cf_j = [], [], []
        for s in split_list:
            ps, pq = np.zeros(N, bool), np.zeros(N, bool)
            for m in (s, ~s):
                e = evaluate(m)
                ps[e["idx"]], pq[e["idx"]] = e["pred_static"], e["pred_quench"]
            cf_s.append(ps.mean() - y.mean())
            cf_q.append(pq.mean() - y.mean())
            cf_j.append(jaccard(ps, y))
        blk = {
            "orca_arm": orca_arm, "b_star_full": b_full, "k_orca_full": int(y.sum()),
            "in_sample": {"static_freed": int(static_full.sum()), "quench_freed_at_full_b": int(x_full.sum()),
                          "delta_static": float(static_full.mean() - y.mean()),
                          "delta_quench": float(x_full.mean() - y.mean()),
                          "jaccard_freed_static": jaccard(static_full, y), "jaccard_freed_quench": jaccard(x_full, y),
                          "method": "full library, fit and evaluation on the same 46 snapshots"},
            "random": {
                "n_halvings": N_SPLIT, "n_folds": len(R), "n_test": R[0]["n_test"],
                "b_star_fit": dist([r["b"] for r in R]),
                "b_star_fit_rel_full": dist([r["b"] / b_full for r in R]),
                "delta_static": dist([r["d_static"] for r in R]),
                "delta_quench": dist([r["d_quench"] for r in R]),
                "delta_rate_transfer": dist([r["ref"] for r in R]),
                "abs_delta_static_mean": float(np.mean([abs(r["d_static"]) for r in R])),
                "frac_delta_static_zero": float(np.mean([abs(r["d_static"]) < 1e-12 for r in R])),
                "quench_fallback_mean": float(np.mean([r["fallback"] for r in R])),
                "jaccard_freed_static": dist([r["jac"] for r in R if r["jac"] is not None]),
                "jaccard_freed_quench": dist([r["jac_q"] for r in R if r["jac_q"] is not None]),
                "handedness_bias_lower_first": float(np.sum([r["hand_bias"][0] for r in R]) /
                                                     max(1, np.sum([r["hand_bias"][1] for r in R]))),
                "handedness_orca_lower_first": float(np.sum([r["hand_orca"][0] for r in R]) /
                                                     max(1, np.sum([r["hand_orca"][1] for r in R]))),
                "cross_fit_delta_static": dist(cf_s), "cross_fit_delta_quench": dist(cf_q),
                "cross_fit_jaccard_static": dist([j for j in cf_j if j is not None]),
                "method": "200 seeded halvings x 2 directions; fit b* on fit half, Delta on test half; "
                          "range95 = 2.5-97.5 percentiles over folds; cross_fit pools both test halves of a halving"},
        }
        canon = {}
        for name, m in (("fit_even", parity(N)), ("fit_odd", ~parity(N))):
            e = evaluate(m)
            test = ~m
            yt = y[test]
            ci = boot_diff(e["pred_static"], yt, rng)
            ciq = boot_diff(e["pred_quench"], yt, rng)
            # runs at the full-library b*, restricted to this test half
            rep_disc = {}
            for arm in (bias_arm, orca_arm):
                rep_disc[arm.replace("+", "plus")] = int(sum(
                    len({r["_freed"] for r in runs[(tags[i], arm)].values()}) > 1 for i in e["idx"]))
            tb = [runs[(tags[i], bias_arm)]["u"]["first_t"] for i in e["idx"] if runs[(tags[i], bias_arm)]["u"]["_freed"]]
            to = [runs[(tags[i], orca_arm)]["u"]["first_t"] for i in e["idx"] if runs[(tags[i], orca_arm)]["u"]["_freed"]]
            canon[name] = {
                "b_star_fit": e["b"], "n_test": e["n_test"], "k_orca_test": e["k_orca_test"],
                "k_static": e["k_static"], "k_quench": e["k_quench"], "quench_fallback": e["fallback"],
                "delta_static": e["d_static"], "delta_static_ci95": ci,
                "delta_quench": e["d_quench"], "delta_quench_ci95": ciq,
                "jaccard_freed_static": e["jac"], "handedness_bias_lower_first": e["hand_bias"],
                "handedness_orca_lower_first": e["hand_orca"],
                "at_full_b_star": {"replay_discordant_snapshots": rep_disc,
                                   "median_first_exit_s_bias": float(np.median(tb)) if tb else None,
                                   "median_first_exit_s_orca": float(np.median(to)) if to else None,
                                   "n_freed_bias": len(tb), "n_freed_orca": len(to),
                                   "method": "existing runs at the full-library b*, test-half snapshots only"},
                "method": "canonical split by snapshot index parity (tags sorted by seed); CI = 2000-resample "
                          "bootstrap of the paired test-half difference, fit held fixed"}
        canon["fit_even"]["delta_static_mean_two_folds"] = 0.5 * (canon["fit_even"]["delta_static"] +
                                                                  canon["fit_odd"]["delta_static"])
        blk["canonical"] = canon
        out[key] = blk
    return out


# ------------------------------------------------------------------ (b) lone keystone
def lone_block(rng):
    sel = [s for s in json.load(open(os.path.join(DATA, "derived", "selection.json")))["E2"]["snapshots"]
           if s["class"] == "lone_keystone"]
    tags = [s["tag"] for s in sel]
    blk = {s["tag"]: str(s["blocker"]) for s in sel}
    N = len(tags)
    runs = defaultdict(dict)
    for r in jl(os.path.join(DATA, "E2", "e2_quench.jsonl")):
        tag, arm, rep = r["job_id"].split("|")
        if tag not in blk:
            continue
        t = r["exits"].get(blk[tag])
        r["_freed"] = t is not None and t <= T_Q + 1e-9
        r["_t"] = round(t, 2) if r["_freed"] else None
        runs[(tag, arm)][rep] = r
    grid = [0.03, 0.05, 0.07]
    c3 = np.array([runs[(t, "C3_rvo2")]["u"]["_freed"] for t in tags], float)
    c3_rep_disc = np.array([len({r["_freed"] for r in runs[(t, "C3_rvo2")].values()}) > 1 for t in tags])
    nf = {s: np.array([np.mean([r["_freed"] for r in runs[(t, f"noise{s}")].values()]) for t in tags]) for s in grid}
    nseed = {s: np.array([len(runs[(t, f"noise{s}")]) for t in tags]) for s in grid}

    def pick(mask):
        d = [abs(nf[s][mask].mean() - c3[mask].mean()) for s in grid]
        best = min(d)
        return max(s for s, x in zip(grid, d) if x <= best + 1e-12)

    def evaluate(fit_mask):
        s = pick(fit_mask)
        te = ~fit_mask
        U_c3 = c3[te] < 0.5
        U_n = nf[s][te] < 0.5
        idx = np.where(te)[0]
        tt, ee = [], []
        for i in idx:
            for r in runs[(tags[i], f"noise{s}")].values():
                tt.append(r["_t"] if r["_freed"] else T_Q)
                ee.append(r["_freed"])
        tc = [runs[(tags[i], "C3_rvo2")]["u"] for i in idx]
        return {"ref": float(c3[fit_mask].mean() - c3[te].mean()),
                "sigma": s, "delta": float(nf[s][te].mean() - c3[te].mean()), "jac": jaccard(U_n, U_c3),
                "seeds_disagree": int(((nf[s][te] > 0) & (nf[s][te] < 1)).sum()),
                "km_median_noise": km_median(tt, ee),
                "km_median_c3": km_median([r["_t"] if r["_freed"] else T_Q for r in tc], [r["_freed"] for r in tc]),
                "c3_replay_disc": int(c3_rep_disc[te].sum()), "n_test": int(te.sum()),
                "k_c3_test": int(c3[te].sum()), "noise_frac_test": float(nf[s][te].mean()),
                "per_snap_noise": nf[s][te], "c3_test": c3[te]}

    splits = halvings(N, rng)
    R = [evaluate(m) for s in splits for m in (s, ~s)]
    full_pick = pick(np.ones(N, bool))
    out = {"n_snapshots": N, "n_seeds_per_snapshot": int(nseed[0.07].min()), "sigma_grid": grid,
           "sigma_full": full_pick,
           "in_sample": {"delta_by_sigma": {f"s{int(round(s * 100)):02d}": float(nf[s].mean() - c3.mean()) for s in grid},
                         "c3_rvo2_freed": int(c3.sum()),
                         "method": "per-run noise freed fraction minus C3 RVO2 freed fraction, all 34 snapshots"},
           "random": {
               "n_halvings": N_SPLIT, "n_folds": len(R), "n_test": R[0]["n_test"],
               "frac_same_sigma": float(np.mean([r["sigma"] == full_pick for r in R])),
               "sigma_counts": {f"s{int(round(s * 100)):02d}": int(sum(r["sigma"] == s for r in R)) for s in grid},
               "delta": dist([r["delta"] for r in R]),
               "delta_rate_transfer": dist([r["ref"] for r in R]),
               "abs_delta_mean": float(np.mean([abs(r["delta"]) for r in R])),
               "jaccard_unresolved": dist([r["jac"] for r in R if r["jac"] is not None]),
               "seeds_disagree": dist([r["seeds_disagree"] for r in R]),
               "km_median_noise_s": dist([r["km_median_noise"] for r in R if r["km_median_noise"] is not None]),
               "km_median_c3_s": dist([r["km_median_c3"] for r in R if r["km_median_c3"] is not None]),
               "c3_replay_disc": dist([r["c3_replay_disc"] for r in R]),
               "method": "200 seeded halvings (17/17) x 2 directions; sigma re-picked on fit half from the grid "
                         "(nearest per-run freed fraction to C3 RVO2's), evaluated on the test half"}}
    canon = {}
    for name, m in (("fit_even", parity(N)), ("fit_odd", ~parity(N))):
        e = evaluate(m)
        canon[name] = {k: v for k, v in e.items() if k not in ("per_snap_noise", "c3_test", "ref")}
        canon[name]["delta_ci95"] = boot_diff(e["per_snap_noise"], e["c3_test"], rng)
        canon[name]["method"] = ("canonical split by index parity in selection.json order; CI = snapshot "
                                 "bootstrap of the test-half paired difference, sigma held fixed")
    out["canonical"] = canon
    return out


# ------------------------------------------------------------------ (c) whole runs
def whole_block(rng):
    ss = json.load(open(os.path.join(DATA, "derived", "sigma_star.json")))
    a, b = ss["fit"]["a"], ss["fit"]["b"]
    s_full = ss["sigma_star"]
    A = {r["seed"]: r["complete"] for r in jl(os.path.join(DATA, "E6", "e6a.jsonl"))}
    B = {r["seed"]: r["complete"] for r in jl(os.path.join(DATA, "E6", "e6b.jsonl"))}
    seeds = sorted(set(A) & set(B))
    assert len(seeds) == len(A) == len(B)
    c3 = np.array([A[s] for s in seeds], float)
    nz = np.array([B[s] for s in seeds], float)
    N = len(seeds)
    P = lambda s: 1 / (1 + math.exp(-(a + b * s)))  # noqa: E731

    def inv(p):
        return (math.log(p / (1 - p)) - a) / b

    def evaluate(fit_mask):
        te = ~fit_mask
        s_fit = inv(c3[fit_mask].mean())
        obs = nz[te].mean() - c3[te].mean()
        return {"sigma": s_fit, "d_obs": float(obs), "d_shift": float(obs + P(s_fit) - P(s_full)),
                "d_fitpred": float(P(s_fit) - c3[te].mean()), "in_range": 0.03 <= s_fit <= 0.07}
    splits = halvings(N, rng)
    R = [evaluate(m) for s in splits for m in (s, ~s)]
    e = evaluate(parity(N))
    te = ~parity(N)
    return {"n_spawns": N, "sigma_star_full": s_full, "fit": "E5b logistic, sigma_star.json",
            "in_sample": {"delta_observed": float(nz.mean() - c3.mean()), "c3_complete": int(c3.sum()),
                          "noise_complete": int(nz.sum())},
            "random": {"n_halvings": N_SPLIT, "n_folds": len(R), "sigma_fit": dist([r["sigma"] for r in R]),
                       "frac_sigma_in_e5b_range": float(np.mean([r["in_range"] for r in R])),
                       "delta_observed_at_full_sigma": dist([r["d_obs"] for r in R]),
                       "delta_fit_shifted": dist([r["d_shift"] for r in R]),
                       "delta_fit_prediction": dist([r["d_fitpred"] for r in R]),
                       "method": "sigma* re-inverted from the fit half's C3 RVO2 completion; test half evaluated "
                                 "observed at sigma* = 0.0467 and shifted by the logistic fit to sigma*_fit"},
            "canonical": {"sigma_fit": e["sigma"], "delta_observed": e["d_obs"], "delta_fit_shifted": e["d_shift"],
                          "delta_observed_ci95": boot_diff(nz[te], c3[te], rng),
                          "method": "canonical split by seed-order parity, fit on even indices"}}


def main():
    rng = np.random.default_rng(SEED)
    out = {"script": "experiments/fixan/fix_a2.py", "doc": __doc__, "rng": f"numpy default_rng({SEED})",
           "pair": pair_block(rng), "lone": lone_block(rng), "whole": whole_block(rng)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return clean(o.tolist())
        return o
    json.dump(clean(out), open(OUT, "w"), indent=1)
    p, lo, w = out["pair"], out["lone"], out["whole"]
    for k in ("pub", "rvo2"):
        r = p[k]["random"]
        print(k, "b*", p[k]["b_star_full"], "fit b*", r["b_star_fit"]["range95"],
              "dS", r["delta_static"]["mean"], r["delta_static"]["range95"],
              "dQ", r["delta_quench"]["mean"], r["delta_quench"]["range95"], "fb", r["quench_fallback_mean"],
              "cf", r["cross_fit_delta_static"]["mean"], r["cross_fit_delta_static"]["range95"],
              "J", r["jaccard_freed_static"]["mean"], "hand", r["handedness_bias_lower_first"],
              r["handedness_orca_lower_first"])
        for c in ("fit_even", "fit_odd"):
            cc = p[k]["canonical"][c]
            print("  ", c, cc["b_star_fit"], cc["k_static"], cc["k_quench"], cc["k_orca_test"],
                  cc["delta_static"], cc["delta_static_ci95"], cc["delta_quench"], cc["jaccard_freed_static"],
                  cc["at_full_b_star"])
    r = lo["random"]
    print("lone", lo["sigma_full"], r["sigma_counts"], r["frac_same_sigma"], r["delta"], r["jaccard_unresolved"]["mean"],
          r["seeds_disagree"]["mean"], r["km_median_noise_s"]["median"], r["km_median_c3_s"]["median"])
    for c in ("fit_even", "fit_odd"):
        print("  ", c, lo["canonical"][c])
    print("whole", w["in_sample"], w["random"]["sigma_fit"]["range95"], w["random"]["frac_sigma_in_e5b_range"],
          w["random"]["delta_observed_at_full_sigma"], w["random"]["delta_fit_shifted"], w["canonical"])


if __name__ == "__main__":
    main()
