"""E7b analysis: the symmetric pair standoff (statics, fold, quench arms, ORCA decomposition, barriers, the
second-trap link C26, and the matched lateral bias b*).

Inputs (data/E7b/ unless stated): e7b_static.jsonl, e7b_quench.jsonl, e7b_barrier.jsonl, e7b_pair_trace.jsonl;
data/E7b_bstar/fold_threshold.jsonl, bstar.json, bstar_quench.jsonl (experiments/E7b/matched_b.py);
data/derived/E2_second_trap.json and data/E1/library (E2 snapshots, for C26); data/derived/field_residuals.json.
Output: data/derived/E7b_analysis.json, figures/data/fig7.json.
Run with the simulation interpreter and PYTHONPATH=code (E2 snapshots are unpickled for the C26 geometry).

Definitions
  freed          a member of the pair exits (crosses the door) within 120 s (any member; "both" = all_freed).
  deterministic  the primary run per (snapshot, arm) is the unperturbed one; the five 1e-9 m replays (seeds
                 900-904) enter the replay-determinism check and S9b only.
  noise          every (snapshot, seed) run counts once (n = 5 x 46 per sigma).
  handedness     side (lower / upper: the member's y at the snapshot relative to y = 5) of the member that
                 exits first. b > 0 tilts the desired direction toward +y, so the bias-favoured member is the
                 lower one for b > 0 and the upper one for b < 0. Exact two-sided binomial test against 1/2.
  fold accuracy  per (snapshot, b): the static overdamped relaxation (E7b_static) predicts freed / held; the
                 120 s quench (unperturbed) decides. Undecided static runs count as "held" predictions.
  static b*_i    per snapshot and sign, the bisected fold threshold (fold_threshold.jsonl), with the grid
                 bracket from E7b_static; the static freed-fraction curve is F(b) = #{b*_i <= |b|} / 46.
  paired tests   unperturbed runs, per snapshot: discordant counts (first arm frees, second holds : the
                 reverse); exact two-sided McNemar p. Equivalence ("tost_0p10"): 90% percentile bootstrap
                 interval of the paired rate difference inside (-0.10, 0.10).
  Jaccard        of the unresolved (held) snapshot sets of two arms; 95% CI from 2000 resamples of snapshots,
                 PCG64(12345).
  time-to-free   first exit time, held runs censored at 120 s; Kaplan-Meier (experiments/E3/survival.py).
  noise rate     censored exponential rate of the first exit per sigma (all runs), exact Poisson CI; Weibull
                 shape shared over snapshots (one scale per snapshot).
  k_B T_eff      m sigma^2 / (1 - (1 - dt/tau)^2), m = 80 kg, dt = 0.01 s, tau of the member whose exit
                 channel gives the pair barrier (experiments/lib/teff.py).
  pair barrier   the lower of the accepted (C15a gate) exit-channel barriers. Arrhenius per barrier snapshot:
                 weighted least squares of ln lambda_hat (5 seeds per sigma) on 1 / k_B T_eff, weights =
                 events; ratio = -slope / dU (1 = activated over the computed barrier).
  C26 link       E2 second-trap snapshots whose blocker has exactly one trapped neighbour against the pair
                 library: geometry (surface gap, distance from the door axis, x offset) and the time-mean
                 cancellation of the door-ward drive by ORCA's constraint part over a 20 s C3 RVO2 trace.
Arm keys have no dots or signs: bias-0.01 -> biasm0p01, bias0.05 -> bias0p05, noise0.01 -> noise0p01,
delta0.001 -> delta0p001, bstar_pub+ -> bstarpubp, bstar_pub- -> bstarpubm.
"""
import json
import math
import os
import pickle
import sys
from collections import defaultdict

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
ROOT = os.path.dirname(EXP)
sys.path.insert(0, os.path.join(EXP, "E3"))
sys.path.insert(0, os.path.join(EXP, "lib"))
from survival import exp_rate, km, weibull_pool  # noqa: E402
from teff import kT_eff  # noqa: E402

DATA = os.path.join(ROOT, "data")
D7 = os.path.join(DATA, "E7b")
DB = os.path.join(DATA, "E7b_bstar")
OUT = os.path.join(DATA, "derived", "E7b_analysis.json")
FIG7 = os.path.join(ROOT, "figures", "data", "fig7.json")
T_Q = 120.0
N_BOOT, RNG_SEED = 2000, 12345
B_GRID = (-0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.05, 0.1)
SIGMAS = (0.01, 0.02, 0.03, 0.05)
DET = ["C1", "C2", "C3_pub", "C3_rvo2", "drive_only", "constraint_only_pub", "constraint_only_rvo2",
       "frozen_plus", "frozen_minus"] + [f"bias{b:g}" for b in B_GRID] + ["delta0.001", "delta0.01", "delta0.03"]


def key(arm):
    return arm.replace("-", "m").replace(".", "p").replace("bstar_", "bstar").replace("+", "p") \
        if arm.startswith("bstar") else arm.replace("-", "m").replace(".", "p")


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [p, max(0.0, c - h), min(1.0, c + h)]


def mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def binom_p(k, n):
    return float(stats.binomtest(k, n, 0.5).pvalue) if n else None


def boot(stat, n, rng, level=95):
    v = []
    for _ in range(N_BOOT):
        x = stat(rng.integers(0, n, n))
        if x is not None and np.isfinite(x):
            v.append(x)
    a = (100 - level) / 2
    return [float(np.percentile(v, a)), float(np.percentile(v, 100 - a))] if v else None


def jl(path):
    return [json.loads(ln) for ln in open(path) if ln.strip()] if os.path.exists(path) else []


def load_runs(path):
    R = defaultdict(dict)
    for r in jl(path):
        tag, arm, rep = r["job_id"].split("|")
        r["_t"] = r["first_t"] if r["freed"] and r["first_t"] <= T_Q + 1e-9 else None
        r["_freed"] = r["_t"] is not None
        R[(tag, arm)][rep] = r
    return R


def summ(a):
    a = np.asarray([x for x in a if x is not None], float)
    if not len(a):
        return None
    return {"n": int(len(a)), "min": float(a.min()), "q25": float(np.percentile(a, 25)),
            "median": float(np.median(a)), "q75": float(np.percentile(a, 75)), "max": float(a.max())}


def main():
    rng = np.random.Generator(np.random.PCG64(RNG_SEED))
    S = {r["job_id"]: r for r in jl(os.path.join(D7, "e7b_static.jsonl"))}
    tags = sorted(S, key=lambda t: S[t]["seed"])
    N = len(tags)
    runs = load_runs(os.path.join(D7, "e7b_quench.jsonl"))
    for k, v in load_runs(os.path.join(DB, "bstar_quench.jsonl")).items():
        runs[k] = v
    out = {"script": "experiments/E7b/analyze.py", "doc": __doc__, "n_snapshots": N}

    def u(tag, arm):
        return runs[(tag, arm)]["u"]

    def freed_vec(arm):
        return np.array([u(t, arm)["_freed"] for t in tags])

    # ---------------- (a) statics
    l1 = [S[t]["lambda1"] for t in tags]
    l2 = [S[t]["eig_N_per_m"][1] for t in tags]
    sv = np.array([S[t]["softest_vec"] for t in tags])
    a = {"strict_min": int(sum(S[t]["strict_min"] for t in tags)), "n": N,
         "strict_min_wilson95": wilson(int(sum(S[t]["strict_min"] for t in tags)), N),
         "lambda1": summ(l1), "lambda2": summ(l2), "lambda2_over_lambda1": summ(np.array(l2) / np.array(l1)),
         "lambda3": summ([S[t]["eig_N_per_m"][2] for t in tags]),
         "softest_common_lateral": sum(S[t]["softest_type"] == "common_lateral" for t in tags),
         "softest_lateral_weight": summ(sv[:, 1] ** 2 + sv[:, 3] ** 2),
         "softest_dy_lo": summ(np.abs(sv[:, 1])), "softest_dy_hi": summ(np.abs(sv[:, 3])),
         "pair_gap_m": summ([S[t]["pair_gap_m"] for t in tags]),
         "wall_gap_m": summ([min(S[t]["wall_gap_m"]) for t in tags]),
         "axis_dist_m": summ([abs(p[1] - 5) for t in tags for p in S[t]["pos"]]),
         "x_m": summ([p[0] for t in tags for p in S[t]["pos"]]),
         "asym_axis_dist_mm": summ([1e3 * S[t]["asym_axis_dist_m"] for t in tags]),
         "asym_drive_N": summ([S[t]["asym_drive_N"] for t in tags]),
         "max_speed": max(S[t]["max_speed"] for t in tags),
         "field_residual_max_N": max(S[t]["check_max_abs_F_plus_gradU_N"] for t in tags),
         "field_residual_median_N": float(np.median([S[t]["check_max_abs_F_plus_gradU_N"] for t in tags]))}
    fp = np.array([S[t]["force_parts_N"]["drive"][0] for t in tags])   # lower member
    a["lower_member_forces_N"] = {nm: {"x": summ([S[t]["force_parts_N"][nm][0][0] for t in tags]),
                                       "y": summ([S[t]["force_parts_N"][nm][0][1] for t in tags])}
                                  for nm in ("drive", "wall", "pair")}
    del fp
    # fold thresholds
    FT = {(r["tag"], r["sign"]): r for r in jl(os.path.join(DB, "fold_threshold.jsonl"))}
    th = {}
    for t in tags:
        for s in (1, -1):
            grid = [b for b in (0.01, 0.02, 0.03, 0.05, 0.1) if S[t]["fold"][f"bias{s * b:g}"]["pred_freed"]] \
                if s > 0 else [b for b in (0.01, 0.02, 0.03) if S[t]["fold"][f"bias{-b:g}"]["pred_freed"]]
            r = FT.get((t, s))
            th[(t, s)] = {"grid_first_freed": min(grid) if grid else None,
                          "b_star": r["b_star"] if r else None, "bracket": [r["b_lo"], r["b_hi"]] if r else None}
    bp = [th[(t, 1)]["b_star"] for t in tags]
    bm = [th[(t, -1)]["b_star"] for t in tags]
    a["fold_threshold"] = {
        "plus": summ(bp), "minus": summ(bm),
        "min_both_signs": summ([min([x for x in (th[(t, 1)]["b_star"], th[(t, -1)]["b_star"]) if x is not None]
                                    or [None]) for t in tags]),
        "n_found_plus": sum(x is not None for x in bp), "n_found_minus": sum(x is not None for x in bm),
        "undecided_calls": sum(r["undecided_calls"] for r in FT.values()),
        "nonmonotone": sum(bool(r["nonmonotone_above"]) for r in FT.values()),
        "corr_lambda1_bstar_spearman": (float(stats.spearmanr(l1, [min(p, m) for p, m in zip(bp, bm)])[0])
                                        if FT and None not in bp + bm else None),
        "corr_asym_bstar_spearman": (float(stats.spearmanr([S[t]["asym_axis_dist_m"] for t in tags],
                                                           [abs(p - m) for p, m in zip(bp, bm)])[0])
                                      if FT and None not in bp + bm else None),
        "per_snapshot": {t: {"plus": th[(t, 1)], "minus": th[(t, -1)]} for t in tags}}
    # fold prediction vs quench
    acc = {}
    tp = tn = fpos = fneg = 0
    for b in B_GRID:
        arm = f"bias{b:g}"
        pr = [bool(S[t]["fold"][arm]["pred_freed"]) for t in tags]
        q = freed_vec(arm)
        c = {"TP": int(sum(p and o for p, o in zip(pr, q))), "TN": int(sum((not p) and (not o) for p, o in zip(pr, q))),
             "FP": int(sum(p and not o for p, o in zip(pr, q))), "FN": int(sum((not p) and o for p, o in zip(pr, q)))}
        c["agree"] = c["TP"] + c["TN"]
        c["n"] = N
        c["pred_freed"] = int(sum(pr))
        c["quench_freed"] = int(q.sum())
        c["disagree_tags"] = [t for t, p, o in zip(tags, pr, q) if p != o]
        acc[key(arm)] = c
        tp += c["TP"]; tn += c["TN"]; fpos += c["FP"]; fneg += c["FN"]  # noqa: E702
    nn = len(B_GRID) * N
    a["fold_prediction"] = {"per_b": acc, "TP": tp, "TN": tn, "FP": fpos, "FN": fneg, "agree": tp + tn, "n": nn,
                            "accuracy_wilson95": wilson(tp + tn, nn)}
    ref = {}
    for arm in ("C1", "frozen_plus", "frozen_minus"):
        pr = [bool(S[t]["fold"][arm]["pred_freed"]) for t in tags]
        q = freed_vec(arm)
        ref[arm] = {"agree": int(sum(p == o for p, o in zip(pr, q))), "n": N, "pred_freed": int(sum(pr)),
                    "quench_freed": int(q.sum()),
                    "undecided": int(sum(S[t]["fold"][arm]["pred_freed"] is None for t in tags))}
    a["fold_prediction"]["reference_arms"] = ref
    # disagreements: distance of b from the snapshot threshold
    if FT:
        dd = []
        for b in B_GRID:
            for t in acc[key(f"bias{b:g}")]["disagree_tags"]:
                bs = th[(t, 1 if b > 0 else -1)]["b_star"]
                dd.append({"tag": t, "b": b, "b_star": bs, "quench_freed": bool(u(t, f"bias{b:g}")["_freed"])})
        a["fold_prediction"]["disagreements"] = dd
        a["fold_prediction"]["disagree_max_rel_gap"] = max(((x["b_star"] - abs(x["b"])) / x["b_star"] for x in dd),
                                                           default=None)
        a["fold_prediction"]["disagree_max_rel_gap_pct"] = (100 * a["fold_prediction"]["disagree_max_rel_gap"]
                                                            if dd else None)
        a["fold_prediction"]["disagree_all_below_threshold"] = all(abs(x["b"]) < x["b_star"] for x in dd)
    out["a_statics"] = a

    # ---------------- (b) quench outcomes
    R = {}
    all_arms = DET + [a_ for a_ in ("bstar_pub+", "bstar_pub-", "bstar_rvo2+", "bstar_rvo2-")
                      if all(len(runs.get((t, a_), {})) == 6 for t in tags)]
    for arm in all_arms:
        U = [u(t, arm) for t in tags]
        k = sum(r["_freed"] for r in U)
        kb = sum(r["all_freed"] and r["_freed"] for r in U)
        kmr = km([r["_t"] if r["_freed"] else T_Q for r in U], [r["_freed"] for r in U], T_Q)
        fr = [r for r in U if r["_freed"]]
        low = sum(r["first_side"] == "lower" for r in fr)
        # replay determinism
        disc, maxdt, nrep = 0, 0.0, 0
        for t in tags:
            rr = runs[(t, arm)]
            o = {rep: r["_freed"] for rep, r in rr.items()}
            if len(set(o.values())) > 1:
                disc += 1
            ts = [r["_t"] for r in rr.values() if r["_freed"]]
            if len(ts) > 1:
                maxdt = max(maxdt, max(ts) - min(ts))
            nrep += len(rr) - 1
        pert = [r for t in tags for rep, r in runs[(t, arm)].items() if rep != "u"]
        R[key(arm)] = {"freed": k, "n": N, "rate_wilson95": wilson(k, N), "both_freed": kb,
                       "km_median_s": kmr["median"], "km_curve": kmr["curve"],
                       "first_lower": low, "first_n": len(fr),
                       "first_lower_frac": low / len(fr) if fr else None, "first_lower_binom_p": binom_p(low, len(fr)),
                       "replay_discordant_snapshots": disc, "replay_max_dt_s": maxdt, "replays": nrep,
                       "perturbed_freed": sum(r["_freed"] for r in pert), "perturbed_n": len(pert),
                       "perturbed_wilson95": wilson(sum(r["_freed"] for r in pert), len(pert))}
    # noise arms
    for sg in SIGMAS:
        arm = f"noise{sg:g}"
        rr = [r for t in tags for r in runs[(t, arm)].values()]
        k = sum(r["_freed"] for r in rr)
        tt = [r["_t"] if r["_freed"] else T_Q for r in rr]
        cc = [not r["_freed"] for r in rr]
        kmr = km(tt, [r["_freed"] for r in rr], T_Q)
        groups = [([r["_t"] if r["_freed"] else T_Q for r in runs[(t, arm)].values()],
                   [not r["_freed"] for r in runs[(t, arm)].values()]) for t in tags]
        wb = weibull_pool(groups)
        fr = [r for r in rr if r["_freed"]]
        low = sum(r["first_side"] == "lower" for r in fr)
        sd = [np.std([r["_t"] for r in runs[(t, arm)].values() if r["_freed"]])
              for t in tags if sum(r["_freed"] for r in runs[(t, arm)].values()) >= 2]
        dis = sum(len({r["_freed"] for r in runs[(t, arm)].values()}) > 1 for t in tags)
        side_mixed = sum(len({r["first_side"] for r in runs[(t, arm)].values() if r["_freed"]}) > 1 for t in tags)
        R[key(arm)] = {"freed": k, "n": len(rr), "rate_wilson95": wilson(k, len(rr)),
                       "snap_majority_freed": sum(sum(r["_freed"] for r in runs[(t, arm)].values()) >= 3 for t in tags),
                       "exp_rate": exp_rate(tt, cc), "weibull": wb, "km_median_s": kmr["median"],
                       "km_curve": kmr["curve"], "first_lower": low, "first_n": len(fr),
                       "first_lower_frac": low / len(fr) if fr else None,
                       "seed_discordant_snapshots": dis, "first_side_mixed_snapshots": side_mixed,
                       "within_snapshot_sd_t_median_s": float(np.median(sd)) if sd else None}
    out["b_quench"] = R
    # handedness (S9e) per bias arm: bias-favoured member first
    H = {}
    for b in B_GRID:
        r = R[key(f"bias{b:g}")]
        fav = r["first_lower"] if b > 0 else r["first_n"] - r["first_lower"]
        H[key(f"bias{b:g}")] = {"b": b, "favoured_first": fav, "freed": r["first_n"],
                                "frac": fav / r["first_n"] if r["first_n"] else None,
                                "binom_p": binom_p(fav, r["first_n"])}
    allfav = sum(h["favoured_first"] for h in H.values())
    alln = sum(h["freed"] for h in H.values())
    H["pooled"] = {"favoured_first": allfav, "freed": alln, "binom_p": binom_p(allfav, alln)}
    # same snapshot under +b and -b: does the first member flip?
    flips = []
    for b in (0.01, 0.02, 0.03):
        n_both = n_flip = 0
        for t in tags:
            p, m = u(t, f"bias{b:g}"), u(t, f"bias{-b:g}")
            if p["_freed"] and m["_freed"]:
                n_both += 1
                n_flip += p["first_agent"] != m["first_agent"]
        flips.append({"b": b, "both_freed": n_both, "first_member_flips": n_flip})
    H["paired_flip"] = flips
    out["b_handedness"] = H
    # freed against signed b (static prediction alongside)
    curve = []
    for b in sorted(B_GRID + (0.0,)):
        arm = "C1" if b == 0 else f"bias{b:g}"
        k = R[key(arm)]["freed"]
        sp = sum(bool(S[t]["fold"][arm]["pred_freed"]) for t in tags)
        curve.append({"b": b, "freed": k, "n": N, "wilson": wilson(k, N), "static_pred_freed": sp})
    out["b_bias_curve"] = curve
    if FT:
        bb = np.linspace(-0.1, 0.1, 801)
        Fs = [(sum(x is not None and x <= b for x in bp) if b > 0 else sum(x is not None and x <= -b for x in bm) if b < 0 else 0) / N for b in bb]
        out["b_static_curve"] = {"b": bb.tolist(), "frac": Fs}
    # S9b
    out["b_s9b"] = {"perturb_1e9_C1": {"freed": R["C1"]["perturbed_freed"], "n": R["C1"]["perturbed_n"],
                                       "wilson95": R["C1"]["perturbed_wilson95"]},
                    **{key(f"delta{d:g}"): {"delta_m": d, "freed": R[key(f"delta{d:g}")]["freed"], "n": N,
                                            "wilson95": R[key(f"delta{d:g}")]["rate_wilson95"],
                                            "perturbed_freed": R[key(f"delta{d:g}")]["perturbed_freed"]}
                       for d in (0.001, 0.01, 0.03)}}
    # does a freeing delta shift sit beyond the static threshold scale? (lambda1 delta vs drive asymmetry)
    if FT:
        fd = [t for t in tags if u(t, "delta0.03")["_freed"]]
        out["b_s9b"]["delta0p03_freed_lambda1"] = summ([S[t]["lambda1"] for t in fd])
        out["b_s9b"]["delta0p03_held_lambda1"] = summ([S[t]["lambda1"] for t in tags if t not in fd])
        out["b_s9b"]["delta0p03_freed_bstar_minus"] = summ([th[(t, -1)]["b_star"] for t in fd])
        out["b_s9b"]["delta0p03_held_bstar_minus"] = summ([th[(t, -1)]["b_star"] for t in tags if t not in fd])

    # ---------------- (c) decomposition
    def paired(a1, a2):
        x, y = freed_vec(a1), freed_vec(a2)
        b_, c_ = int((x & ~y).sum()), int((~x & y).sum())
        diff = boot(lambda i: float(x[i].mean() - y[i].mean()), N, rng, level=90)
        return {"a": a1, "b": a2, "freed_a": int(x.sum()), "freed_b": int(y.sum()), "disc_a_only": b_,
                "disc_b_only": c_, "mcnemar_p": mcnemar(b_, c_), "diff": float(x.mean() - y.mean()),
                "diff_ci90": diff, "tost_0p10": bool(diff and diff[0] > -0.10 and diff[1] < 0.10),
                "identical": int((x == y).sum())}
    C = {"pub_vs_rvo2": paired("C3_pub", "C3_rvo2"),
         "constraint_pub_vs_C1": paired("constraint_only_pub", "C1"),
         "constraint_rvo2_vs_C1": paired("constraint_only_rvo2", "C1"),
         "drive_vs_C1": paired("drive_only", "C1"),
         "drive_vs_rvo2": paired("drive_only", "C3_rvo2"),
         "drive_vs_pub": paired("drive_only", "C3_pub"),
         "constraint_rvo2_vs_rvo2": paired("constraint_only_rvo2", "C3_rvo2"),
         "frozen_plus_vs_minus": paired("frozen_plus", "frozen_minus"),
         "frozen_plus_vs_rvo2": paired("frozen_plus", "C3_rvo2"),
         "C2_vs_C1": paired("C2", "C1")}
    C["replay"] = {key(a_): {"discordant": R[key(a_)]["replay_discordant_snapshots"],
                             "max_dt_s": R[key(a_)]["replay_max_dt_s"], "replays": R[key(a_)]["replays"]}
                   for a_ in all_arms}
    C["replay_all_det_discordant"] = sum(v["discordant"] for v in C["replay"].values())
    C["replay_all_det_n"] = sum(v["replays"] for v in C["replay"].values())
    C["replay_max_dt_s"] = max(v["max_dt_s"] for v in C["replay"].values())
    out["c_decomposition"] = C

    # ---------------- (d) pair barriers
    BR = jl(os.path.join(D7, "e7b_barrier.jsonl"))
    rows = []
    for r in BR:
        t = r["job_id"]
        acc_ch = {m: c for m, c in r["channels"].items() if c["accepted"]}
        if not acc_ch:
            rows.append({"tag": t, "accepted": False})
            continue
        m = min(acc_ch, key=lambda k_: acc_ch[k_]["dU"])
        ids = S[t]["ids"]
        tau = S[t]["tau"][ids.index(int(m))]
        dU = acc_ch[m]["dU"]
        rw = {"tag": t, "accepted": True, "dU": dU, "exit_side": acc_ch[m]["side"], "lambda1": r["lambda1"],
              "channels_accepted": len(acc_ch), "tau": tau, "levels": []}
        for sg in SIGMAS:
            rr = list(runs[(t, f"noise{sg:g}")].values())
            er = exp_rate([x["_t"] if x["_freed"] else T_Q for x in rr], [not x["_freed"] for x in rr])
            kT = kT_eff(sg, 0.01, tau)
            rw["levels"].append({"sigma": sg, "kT": kT, "beta_dU": dU / kT, "lam": er["lam"], "events": er["events"],
                                 "ci95": er["ci95"]})
        L = [lv for lv in rw["levels"] if lv["events"] > 0]
        if len(L) >= 2:
            x = np.array([1 / lv["kT"] for lv in L])
            y = np.log([lv["lam"] for lv in L])
            w = np.array([lv["events"] for lv in L], float)
            W = w.sum()
            xm, ym = (w * x).sum() / W, (w * y).sum() / W
            s = (w * (x - xm) * (y - ym)).sum() / (w * (x - xm) ** 2).sum()
            rw["arrhenius_slope_J"] = float(s)
            rw["ratio"] = float(-s / dU)
        rows.append(rw)
    acc_rows = [x for x in rows if x["accepted"]]
    Dd = {"n": len(rows), "accepted": len(acc_rows), "dU": summ([x["dU"] for x in acc_rows]),
          "lambda1": summ([x["lambda1"] for x in acc_rows]),
          "spearman_lambda1_dU": (float(stats.spearmanr([x["lambda1"] for x in acc_rows],
                                                        [x["dU"] for x in acc_rows])[0]) if len(acc_rows) > 2 else None),
          "spearman_lambda1_dU_p": (float(stats.spearmanr([x["lambda1"] for x in acc_rows],
                                                          [x["dU"] for x in acc_rows])[1]) if len(acc_rows) > 2 else None),
          "channels_failed": sum(not c["accepted"] for r in BR for c in r["channels"].values()),
          "channels_total": sum(len(r["channels"]) for r in BR),
          "beta_dU_at_sigma0p01": summ([x["levels"][0]["beta_dU"] for x in acc_rows]),
          "beta_dU_at_sigma0p02": summ([x["levels"][1]["beta_dU"] for x in acc_rows]),
          "ratio": summ([x.get("ratio") for x in acc_rows]),
          "rows": rows}
    # pooled Arrhenius over snapshots (per-snapshot intercepts): within-snapshot centred WLS
    num = den = 0.0
    for x in acc_rows:
        L = [lv for lv in x["levels"] if lv["events"] > 0]
        if len(L) < 2:
            continue
        xx = np.array([x["dU"] / lv["kT"] for lv in L])
        yy = np.log([lv["lam"] for lv in L])
        w = np.array([lv["events"] for lv in L], float)
        xm, ym = (w * xx).sum() / w.sum(), (w * yy).sum() / w.sum()
        num += (w * (xx - xm) * (yy - ym)).sum()
        den += (w * (xx - xm) ** 2).sum()
    Dd["pooled_slope_vs_beta_dU"] = num / den if den else None
    out["d_barriers"] = Dd

    # ---------------- (e) C26 link
    E2 = json.load(open(os.path.join(DATA, "derived", "E2_second_trap.json")))
    sel = {s["tag"]: s for s in json.load(open(os.path.join(DATA, "derived", "selection.json")))["E2"]["snapshots"]}
    one = [r for r in E2["rows"] if r["class"] == "lone_keystone_second_trap" and r["rvo2"]["n_trapped_neighbours"] == 1]
    geo = []
    try:
        sys.path.insert(0, os.path.join(ROOT, "code"))
        for r in one:
            snap = pickle.load(open(os.path.join(ROOT, sel[r["tag"]]["snap"]), "rb"))
            st = snap["state"]
            b = r["blocker"]
            o = [int(i) for i in st.active_indices if i != b][0]
            d = float(np.linalg.norm(st.positions[b] - st.positions[o]))
            geo.append({"tag": r["tag"], "gap_m": d - float(st.radii[b] + st.radii[o]),
                        "axis_dist_b_m": float(abs(st.positions[b, 1] - 5)),
                        "axis_dist_o_m": float(abs(st.positions[o, 1] - 5)),
                        "x_b": float(st.positions[b, 0]), "x_o": float(st.positions[o, 0]),
                        "opposite_sides": bool((st.positions[b, 1] - 5) * (st.positions[o, 1] - 5) < 0),
                        "B_w": float(snap["params"].get("B_w", 0.08))})
    except Exception as e:  # noqa: BLE001
        geo = [{"error": repr(e)}]
    TR = jl(os.path.join(D7, "e7b_pair_trace.jsonl"))
    q_rv = {t: u(t, "C3_rvo2")["_freed"] for t in tags}
    E = {"second_trap_one_neighbour": {
            "n": len(one), "C3_rvo2_freed": sum(r["outcome"]["C3_rvo2"]["freed"] for r in one),
            "C3_pub_freed": sum(r["outcome"]["C3_pub"]["freed"] for r in one),
            "drive_only_freed": sum(r["outcome"]["drive_only"]["freed"] for r in one),
            "cancel_frac_mean": summ([r["trace_rvo2"]["cancel_frac_mean"] for r in one]),
            "cancel_frac_mean_held": summ([r["trace_rvo2"]["cancel_frac_mean"] for r in one
                                           if not r["outcome"]["C3_rvo2"]["freed"]]),
            "cons_x_mean_held": summ([r["trace_rvo2"]["cons_x_mean"] for r in one if not r["outcome"]["C3_rvo2"]["freed"]]),
            "geometry": geo,
            "gap_m": summ([g.get("gap_m") for g in geo]), "axis_dist_b_m": summ([g.get("axis_dist_b_m") for g in geo]),
            "axis_dist_o_m": summ([g.get("axis_dist_o_m") for g in geo]),
            "opposite_sides": sum(bool(g.get("opposite_sides")) for g in geo),
            "dx_m": summ([g["x_o"] - g["x_b"] for g in geo if "x_o" in g])},
         "pair_library": {"n": N, "C3_rvo2_freed": R["C3_rvo2"]["freed"], "C3_pub_freed": R["C3_pub"]["freed"],
                          "drive_only_freed": R["drive_only"]["freed"],
                          "gap_m": a["pair_gap_m"], "axis_dist_m": a["axis_dist_m"],
                          "dx_m": summ([abs(S[t]["pos"][1][0] - S[t]["pos"][0][0]) for t in tags])}}
    if TR:
        held_tr = [r for r in TR if not q_rv[r["tag"]]]
        E["pair_library"]["trace"] = {
            "n": len(TR), "cons_x_t0": summ([abs(r["cons_x_t0"]) for r in TR]),
            "cancel_frac_mean": summ([r["cancel_frac_mean"] for r in TR]),
            "cancel_frac_mean_held": summ([r["cancel_frac_mean"] for r in held_tr]),
            "cancel_frac_max_held": summ([r["cancel_frac_max"] for r in held_tr]),
            "cons_x_mean_held": summ([r["cons_x_mean"] for r in held_tr]),
            "cons_x_min_held": summ([r["cons_x_min"] for r in held_tr]),
            "partner_share_held": summ([r["partner_dFx_mean"] / r["cons_x_mean"] for r in held_tr
                                        if abs(r["cons_x_mean"]) > 1e-6]),
            "frac_steps_cancel_gt_half_held": summ([r["frac_steps_cancel_gt_half"] for r in held_tr])}
    tab = [[E["second_trap_one_neighbour"]["C3_rvo2_freed"], len(one) - E["second_trap_one_neighbour"]["C3_rvo2_freed"]],
           [R["C3_rvo2"]["freed"], N - R["C3_rvo2"]["freed"]]]
    E["rvo2_rate_fisher_p"] = float(stats.fisher_exact(tab)[1])
    out["e_c26"] = E

    # ---------------- step 3: matched b*
    if os.path.exists(os.path.join(DB, "bstar.json")):
        BS = json.load(open(os.path.join(DB, "bstar.json")))
        M = {"fits": BS["fits"]}
        for kf, f in BS["fits"].items():
            orca = f["arm"]
            ap, am = f"bstar_{kf}+", f"bstar_{kf}-"
            if key(ap) not in R or key(am) not in R:
                continue
            x, y, z = freed_vec(ap), freed_vec(orca), freed_vec(am)
            m = {"b_star": f["b_star"], "interval": f["interval"], "orca_arm": orca,
                 "rate": paired(ap, orca), "reversal": paired(am, ap), "minus_vs_orca": paired(am, orca)}
            uo, ub = ~y, ~x
            jac = lambda i, A=ub, B=uo: (float((A[i] & B[i]).sum() / (A[i] | B[i]).sum())  # noqa: E731
                                         if (A[i] | B[i]).sum() else None)
            m["jaccard_unresolved"] = {"value": jac(np.arange(N)), "ci95": boot(jac, N, rng),
                                       "both_held": int((ub & uo).sum()), "either_held": int((ub | uo).sum())}
            jf = lambda i, A=x, B=y: (float((A[i] & B[i]).sum() / (A[i] | B[i]).sum()) if (A[i] | B[i]).sum() else None)  # noqa: E731
            m["jaccard_freed"] = {"value": jf(np.arange(N)), "ci95": boot(jf, N, rng),
                                  "both_freed": int((x & y).sum()), "either_freed": int((x | y).sum())}
            # handedness: favoured member first at +b* (lower) and -b* (upper); ORCA's lower-first fraction
            rp, rm, ro = R[key(ap)], R[key(am)], R[key(orca)]
            m["handedness"] = {
                "plus_lower_first": rp["first_lower"], "plus_n": rp["first_n"], "plus_binom_p": rp["first_lower_binom_p"],
                "minus_upper_first": rm["first_n"] - rm["first_lower"], "minus_n": rm["first_n"],
                "minus_binom_p": binom_p(rm["first_n"] - rm["first_lower"], rm["first_n"]),
                "orca_lower_first": ro["first_lower"], "orca_n": ro["first_n"], "orca_binom_p": ro["first_lower_binom_p"]}
            # same first member where both bias(+b*) and ORCA free
            same = [u(t, ap)["first_agent"] == u(t, orca)["first_agent"] for t in tags
                    if u(t, ap)["_freed"] and u(t, orca)["_freed"]]
            same_m = [u(t, am)["first_agent"] == u(t, orca)["first_agent"] for t in tags
                      if u(t, am)["_freed"] and u(t, orca)["_freed"]]
            m["handedness"]["same_first_member_plus"] = [sum(same), len(same)]
            m["handedness"]["same_first_member_minus"] = [sum(same_m), len(same_m)]
            # ORCA: does it reverse under the mirror? ORCA has no handedness parameter; its first-out side under
            # the pair's own asymmetry: member nearer the axis first?
            near = []
            for t in tags:
                r_ = u(t, orca)
                if r_["_freed"]:
                    ids = S[t]["ids"]
                    dist = [abs(p[1] - 5) for p in S[t]["pos"]]
                    near.append(ids[int(np.argmin(dist))] == r_["first_agent"])
            m["handedness"]["orca_nearer_axis_first"] = [sum(near), len(near)]
            m["replay"] = {"plus": C["replay"][key(ap)], "minus": C["replay"][key(am)]}
            m["km_median_s"] = {"plus": rp["km_median_s"], "minus": rm["km_median_s"], "orca": ro["km_median_s"]}
            # time-to-free where both free (paired)
            dts = [u(t, ap)["_t"] - u(t, orca)["_t"] for t in tags if u(t, ap)["_freed"] and u(t, orca)["_freed"]]
            m["paired_dt_s"] = summ(dts)
            # constraint dependence: share of the arm's freed snapshots also freed by drive_only / constraint_only
            dr, co = freed_vec("drive_only"), freed_vec("constraint_only_rvo2" if kf == "rvo2" else "constraint_only_pub")
            m["overlap_with_drive_only"] = {"bias": int((x & dr).sum()), "orca": int((y & dr).sum()),
                                            "drive_only": int(dr.sum())}
            m["overlap_with_constraint_only"] = {"bias": int((x & co).sum()), "orca": int((y & co).sum())}
            M[kf] = m
        out["s3_matched"] = M

    json.dump(dotless(out), open(OUT, "w"), indent=1, default=float)
    fig7_cache(out)
    print(json.dumps(brief(out), indent=1, default=float))


def dotless(o):
    if isinstance(o, dict):
        return {(k.replace(".", "p") if isinstance(k, str) and "E7b_B0.04" not in k else k): dotless(v)
                for k, v in o.items()}
    if isinstance(o, list):
        return [dotless(v) for v in o]
    return o


FIG7_GROUPS = [["C1", "C2"],
               ["C3_pub", "C3_rvo2", "drive_only", "constraint_only_pub", "constraint_only_rvo2", "frozen_plus",
                "frozen_minus"],
               ["bstarpubp", "bstarpubm", "bstarrvo2p", "bstarrvo2m"],
               ["noise0p01", "noise0p02", "noise0p03", "noise0p05"]]


def fig7_cache(o):
    R = o["b_quench"]
    groups = [[a for a in g if a in R] for g in FIG7_GROUPS]
    d = {"source": "data/derived/E7b_analysis.json (experiments/E7b/analyze.py)",
         "bias_curve": o["b_bias_curve"], "static_curve": o.get("b_static_curve"),
         "ref": {"C3_pub": R["C3_pub"]["rate_wilson95"][0], "C3_rvo2": R["C3_rvo2"]["rate_wilson95"][0]},
         "groups": groups,
         "rates": {a: {"k": R[a]["freed"], "n": R[a]["n"], "wilson": R[a]["rate_wilson95"]} for g in groups for a in g}}
    os.makedirs(os.path.dirname(FIG7), exist_ok=True)
    json.dump(d, open(FIG7, "w"), indent=1)


def brief(o):
    R = o["b_quench"]
    b = {"statics": {k: o["a_statics"][k] for k in ("strict_min", "lambda1", "lambda2", "softest_common_lateral",
                                                    "field_residual_max_N")},
         "fold_acc": {k: o["a_statics"]["fold_prediction"][k] for k in ("agree", "n", "TP", "TN", "FP", "FN",
                                                                       "accuracy_wilson95")},
         "fold_threshold": {k: o["a_statics"]["fold_threshold"][k] for k in ("plus", "minus")},
         "rates": {a: f"{v['freed']}/{v['n']}" for a, v in R.items()},
         "replay_disc": o["c_decomposition"]["replay_all_det_discordant"],
         "decomp": {k: (v["freed_a"], v["freed_b"], v["disc_a_only"], v["disc_b_only"], v["mcnemar_p"])
                    for k, v in o["c_decomposition"].items() if isinstance(v, dict) and "mcnemar_p" in v},
         "handed": {k: (v.get("favoured_first"), v.get("freed")) for k, v in o["b_handedness"].items() if k != "paired_flip"},
         "barriers": {k: o["d_barriers"][k] for k in ("accepted", "dU", "spearman_lambda1_dU", "ratio",
                                                      "pooled_slope_vs_beta_dU")},
         "c26": {k: v for k, v in o["e_c26"]["second_trap_one_neighbour"].items() if k != "geometry"}}
    if "s3_matched" in o:
        b["s3"] = {k: v for k, v in o["s3_matched"].items() if k != "fits"}
        for v in b["s3"].values():
            for kk in ("rate", "reversal", "minus_vs_orca"):
                v[kk] = {x: v[kk][x] for x in ("freed_a", "freed_b", "disc_a_only", "disc_b_only", "mcnemar_p",
                                               "diff_ci90", "tost_0p10")}
    return b


if __name__ == "__main__":
    main()
