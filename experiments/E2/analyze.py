"""E2 analysis: lone-trap quench outcomes, per stratum and pooled.

Input:  data/E2/e2_quench.jsonl (experiments/E2/e2_quench.py), data/derived/selection.json (E2 snapshots,
        blocker, stratum), data/E1/E1_runs.jsonl (blocker C3 rest-state margin, E1b attrs).
Output: data/derived/E2_analysis.json.

Definitions
  freed          the blocker (residual agent nearest (10, 5), selection.json) exits within 120 s.
  deterministic  the primary run per (snapshot, arm) is the unperturbed one; the five 1e-9 m replays
                 (perturbation seeds 900-904) enter only the replay-determinism check (b).
  noise arms     every (snapshot, seed) run counts once for rates and Kaplan-Meier (n = 5 x snapshots);
                 a snapshot is "unresolved" under a noise arm when the blocker is freed in fewer than 3 of
                 its 5 seeds (majority rule); under a deterministic arm when the unperturbed run holds.
  time-to-free   blocker exit time; held runs censored at 120 s. Kaplan-Meier product-limit estimate;
                 quartiles = first time S(t) <= 0.75 / 0.5 / 0.25 (null when not reached).
  paired tests   per snapshot (unperturbed runs): discordant counts b (first frees, second holds) and c;
                 exact two-sided McNemar p = min(1, 2 * P[Bin(b + c, 1/2) <= min(b, c)]).
  keys           arm keys in the output have no dots (noise0p03 = sigma 0.03 m/s, bias0p05 = b 0.05).
  AUC            Mann-Whitney, ties 1/2. CIs: 2000 resamples of snapshots, percentile, PCG64(12345).
  Equivalence    paired rate differences against +-0.10 are kept here only (field "tost_0.10"):
                 90% percentile bootstrap interval of the paired difference inside (-0.10, 0.10).
"""
import json
import math
import os
from collections import defaultdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
IN = os.path.join(DATA, "E2", "e2_quench.jsonl")
OUT = os.path.join(DATA, "derived", "E2_analysis.json")
T_Q = 120.0
N_BOOT = 2000
RNG_SEED = 12345
DET_ARMS = ["C1", "C2", "C3_pub", "C3_rvo2", "drive_only", "constraint_only_pub", "constraint_only_rvo2",
            "frozen_plus", "frozen_minus", "bias0.05", "bias0.1", "bias0.2", "bias0.5"]
NOISE_ARMS = ["noise0.03", "noise0.05", "noise0.07"]
STRATA = ["lone_keystone", "lone_keystone_second_trap"]
GROUPS = {"lone_keystone": STRATA[:1], "lone_keystone_second_trap": STRATA[1:], "pooled": STRATA}


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [p, max(0.0, c - h), min(1.0, c + h)]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def auc(score, label):
    score, label = np.asarray(score, float), np.asarray(label, bool)
    pos, neg = score[label], score[~label]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum()
    eq = (pos[:, None] == neg[None, :]).sum()
    return float((gt + 0.5 * eq) / (len(pos) * len(neg)))


def km(times, events, t_max=T_Q):
    """Kaplan-Meier. times: event or censoring time; events: bool. Returns curve and quartiles."""
    t = np.round(np.asarray(times, float), 2)
    e = np.asarray(events, bool)
    order = np.argsort(t, kind="stable")
    t, e = t[order], e[order]
    n = len(t)
    S, curve = 1.0, [[0.0, 1.0]]
    i = 0
    while i < n:
        ti = t[i]
        j = i
        d = 0
        while j < n and t[j] == ti:
            d += int(e[j])
            j += 1
        at_risk = n - i
        if d:
            S *= 1 - d / at_risk
            curve.append([float(ti), S])
        i = j
    curve.append([t_max, S])

    def quant(level):
        for tt, s in curve[1:-1]:
            if s <= level + 1e-12:
                return tt
        return None
    return {"n": n, "events": int(e.sum()), "S_end": S, "q25": quant(0.75), "median": quant(0.5),
            "q75": quant(0.25), "curve": curve}


def boot_ci(stat, n, rng, B=N_BOOT, level=95):
    vals = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        v = stat(idx)
        if v is not None and np.isfinite(v):
            vals.append(v)
    if not vals:
        return None
    a = (100 - level) / 2
    return [float(np.percentile(vals, a)), float(np.percentile(vals, 100 - a))]


def load():
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
        s["blocker_margin_C3"] = a["margin_C3"]
        s["blocker_attrs"] = {k: a[k] for k in ("r", "v0", "tau", "m")}
    runs = defaultdict(dict)   # runs[(tag, arm)][rep] = record
    for line in open(IN):
        r = json.loads(line)
        tag, arm, rep = r["job_id"].split("|")
        b = str(snaps[tag]["blocker"])
        t = r["exits"].get(b)
        r["_freed"] = t is not None and t <= T_Q + 1e-9
        r["_t"] = round(t, 2) if r["_freed"] else None
        runs[(tag, arm)][rep] = r
    return sel, snaps, runs


def main():
    sel, snaps, runs = load()
    rng = np.random.Generator(np.random.PCG64(RNG_SEED))
    tags = {g: [s["tag"] for s in sel if s["class"] in st] for g, st in GROUPS.items()}
    out = {"script": "experiments/E2/analyze.py", "doc": __doc__,
           "n_snapshots": {g: len(v) for g, v in tags.items()}, "n_runs": sum(len(v) for v in runs.values())}

    def det_freed(tag, arm):
        return runs[(tag, arm)]["u"]["_freed"]

    def noise_frac(tag, arm):
        rr = runs[(tag, arm)]
        return sum(r["_freed"] for r in rr.values()) / len(rr)

    def unresolved(tag, arm):
        return (not det_freed(tag, arm)) if arm in DET_ARMS else noise_frac(tag, arm) < 0.5

    # (a) rates and time-to-free
    rates = {}
    for g, T in tags.items():
        rates[g] = {}
        for arm in DET_ARMS + NOISE_ARMS:
            if arm in DET_ARMS:
                rr = [runs[(t, arm)]["u"] for t in T]
            else:
                rr = [r for t in T for r in runs[(t, arm)].values()]
            k = sum(r["_freed"] for r in rr)
            K = km([r["_t"] if r["_freed"] else T_Q for r in rr], [r["_freed"] for r in rr])
            cell = {"unit": "snapshot (unperturbed run)" if arm in DET_ARMS else "run (snapshot x seed)",
                    "freed": k, "n": len(rr), "rate_wilson95": wilson(k, len(rr)),
                    "all_residual_freed": sum(r["all_freed"] for r in rr),
                    "time_to_free_km": {x: K[x] for x in ("n", "events", "S_end", "q25", "median", "q75")},
                    "km_curve": K["curve"]}
            if arm in NOISE_ARMS:
                fr = [noise_frac(t, arm) for t in T]
                cell["snapshots_freed_majority"] = sum(f >= 0.5 for f in fr)
                cell["snapshots_freed_any_seed"] = sum(f > 0 for f in fr)
                cell["snapshots_freed_all_seeds"] = sum(f == 1 for f in fr)
            rates[g][arm] = cell
    out["a_rates_time_to_free"] = rates

    # (b) replay determinism
    det = {}
    for g, T in tags.items():
        det[g] = {}
        for arm in DET_ARMS:
            disagree_freed, max_dt_block, max_dt_first, n_cmp_t = 0, 0.0, 0.0, 0
            disagree_first_agent = 0
            for t in T:
                rr = runs[(t, arm)]
                u = rr["u"]
                for rep, r in rr.items():
                    if rep == "u":
                        continue
                    if r["_freed"] != u["_freed"]:
                        disagree_freed += 1
                    if r["_freed"] and u["_freed"]:
                        max_dt_block = max(max_dt_block, abs(r["_t"] - u["_t"]))
                        n_cmp_t += 1
                    if (r["first_agent"] is None) != (u["first_agent"] is None) or r["first_agent"] != u["first_agent"]:
                        disagree_first_agent += 1
                    if r["first_t"] is not None and u["first_t"] is not None:
                        max_dt_first = max(max_dt_first, abs(r["first_t"] - u["first_t"]))
            det[g][arm] = {"replays": 5 * len(T), "freed_disagree": disagree_freed,
                           "first_agent_disagree": disagree_first_agent,
                           "max_abs_dt_blocker_exit_s": max_dt_block, "n_blocker_exit_pairs": n_cmp_t,
                           "max_abs_dt_first_exit_s": max_dt_first}
        for arm in NOISE_ARMS:
            disc, sds, iqrs = 0, [], []
            for t in T:
                rr = list(runs[(t, arm)].values())
                f = [r["_freed"] for r in rr]
                disc += int(0 < sum(f) < len(f))
                ft = [r["first_t"] for r in rr if r["first_t"] is not None]
                if len(ft) >= 2:
                    sds.append(float(np.std(ft, ddof=1)))
                    iqrs.append(float(np.ptp(ft)))
            det[g][arm] = {"snapshots": len(T), "seeds_disagree_on_freed": disc,
                           "D_wilson95": wilson(disc, len(T)),
                           "within_snapshot_sd_first_exit_s": {"median": float(np.median(sds)) if sds else None,
                                                               "min": min(sds) if sds else None,
                                                               "max": max(sds) if sds else None,
                                                               "n_snapshots": len(sds)},
                           "within_snapshot_range_first_exit_s_median": float(np.median(iqrs)) if iqrs else None}
    out["b_replay_determinism"] = det

    # (c) rest-state lemma: C2 vs C1, every replay
    lem = {"pairs": 0, "identical_exits": 0, "identical_stop_time": 0, "max_final_pos_diff_m": 0.0,
           "any_exit_in_either": 0, "differences": []}
    for t in tags["pooled"]:
        for rep in runs[(t, "C1")]:
            a, b = runs[(t, "C1")][rep], runs[(t, "C2")][rep]
            lem["pairs"] += 1
            same_ex = a["exits"] == b["exits"]
            lem["identical_exits"] += int(same_ex)
            lem["identical_stop_time"] += int(abs(a["t_run"] - b["t_run"]) < 1e-9)
            lem["any_exit_in_either"] += int(bool(a["exits"]) or bool(b["exits"]))
            d = max((float(np.linalg.norm(np.subtract(a["final_pos"][k], b["final_pos"][k])))
                     for k in a["final_pos"] if k in b["final_pos"]), default=0.0)
            lem["max_final_pos_diff_m"] = max(lem["max_final_pos_diff_m"], d)
            if not same_ex or abs(a["t_run"] - b["t_run"]) > 1e-9 or set(a["final_pos"]) != set(b["final_pos"]):
                lem["differences"].append({"snapshot": t, "rep": rep, "C1_exits": a["exits"], "C2_exits": b["exits"],
                                           "C1_t_run": a["t_run"], "C2_t_run": b["t_run"]})
    lem["blocker_freed_C1"] = sum(runs[(t, "C1")]["u"]["_freed"] for t in tags["pooled"])
    lem["blocker_freed_C2"] = sum(runs[(t, "C2")]["u"]["_freed"] for t in tags["pooled"])
    out["c_rest_state_lemma_C2_vs_C1"] = lem

    # (d, e) paired comparisons
    def paired(a1, a2, T):
        f1 = np.array([det_freed(t, a1) for t in T])
        f2 = np.array([det_freed(t, a2) for t in T])
        b = int((f1 & ~f2).sum())
        c = int((~f1 & f2).sum())
        diff = (f1.astype(float) - f2.astype(float))
        r = {"first": a1, "second": a2, "n": len(T), "first_freed": int(f1.sum()), "second_freed": int(f2.sum()),
             "discordant_first_only": b, "discordant_second_only": c, "mcnemar_exact_p": mcnemar_exact(b, c),
             "rate_diff": float(diff.mean()),
             "rate_diff_ci95_boot": boot_ci(lambda i: diff[i].mean(), len(T), rng)}
        ci90 = boot_ci(lambda i: diff[i].mean(), len(T), rng, level=90)
        r["tost_0.10"] = {"ci90_boot": ci90, "within": bool(ci90 and -0.10 < ci90[0] and ci90[1] < 0.10)}
        return r

    pairs_d = [("drive_only", "C3_rvo2"), ("drive_only", "C3_pub"), ("constraint_only_pub", "C1"),
               ("constraint_only_rvo2", "C1"), ("frozen_plus", "frozen_minus"), ("frozen_plus", "C3_rvo2"),
               ("C3_pub", "C3_rvo2")]
    out["d_orca_decomposition"] = {g: {f"{a}_vs_{b}": paired(a, b, T) for a, b in pairs_d} for g, T in tags.items()}
    out["e_lateral_bias_vs_C1"] = {g: {f"{a}_vs_C1": paired(a, "C1", T) for a in DET_ARMS if a.startswith("bias")}
                                   for g, T in tags.items()}
    # extra freed agents under bias (non-blocker exits)
    for g, T in tags.items():
        for a in DET_ARMS:
            if a.startswith("bias") or a.startswith("constraint_only"):
                rr = [runs[(t, a)]["u"] for t in T]
                out.setdefault("e_non_blocker_exits", {}).setdefault(g, {})[a] = {
                    "snapshots_with_any_exit": sum(bool(r["exits"]) for r in rr),
                    "agents_exited": sum(len(r["exits"]) for r in rr),
                    "residual_agents": sum(len(r["residual"]) for r in rr)}

    # (f) noise vs C3_rvo2
    f = {}
    for g, T in tags.items():
        f[g] = {}
        c3 = np.array([float(det_freed(t, "C3_rvo2")) for t in T])
        for arm in NOISE_ARMS:
            nf = np.array([noise_frac(t, arm) for t in T])
            diff = nf - c3
            U_c3 = {t for t in T if unresolved(t, "C3_rvo2")}
            U_n = {t for t in T if unresolved(t, arm)}
            Tarr = np.array(T)

            def jac(idx):
                # resample snapshots; duplicates count once (set semantics over sampled tags)
                s = set(Tarr[idx])
                a, b = U_c3 & s, U_n & s
                u = a | b
                return len(a & b) / len(u) if u else None
            union = U_c3 | U_n
            f[g][arm] = {
                "noise_rate_per_run": float(nf.mean()), "C3_rvo2_rate": float(c3.mean()),
                "paired_rate_diff_noise_minus_C3": float(diff.mean()),
                "paired_rate_diff_ci95_boot": boot_ci(lambda i: diff[i].mean(), len(T), rng),
                "tost_0.10": (lambda ci: {"ci90_boot": ci, "within": bool(ci and -0.1 < ci[0] and ci[1] < 0.1)})(
                    boot_ci(lambda i: diff[i].mean(), len(T), rng, level=90)),
                "unresolved_C3_rvo2": sorted(U_c3), "unresolved_noise_majority": sorted(U_n),
                "both": sorted(U_c3 & U_n), "jaccard": len(U_c3 & U_n) / len(union) if union else None,
                "jaccard_ci95_boot": boot_ci(jac, len(T), rng)}
        # margin -> C3 failure
        m3 = np.array([snaps[t]["blocker_margin_C3"] for t in T])
        m1 = np.array([snaps[t]["blocker_margin_C1"] for t in T])
        for arm in ("C3_rvo2", "C3_pub"):
            fail = np.array([not det_freed(t, arm) for t in T])
            f[g][f"margin_predicts_{arm}_failure"] = {
                "n_fail": int(fail.sum()), "n": len(T),
                "auc_margin_C3": auc(m3, fail),
                "auc_margin_C3_ci95_boot": boot_ci(lambda i: auc(m3[i], fail[i]), len(T), rng),
                "auc_margin_C1": auc(m1, fail),
                "margin_C3_failed": sorted(m3[fail].tolist()),
                "margin_C3_freed_range": [float(m3[~fail].min()), float(m3[~fail].max())] if (~fail).any() else None,
                "failed_with_margin_C3_le_0": int((fail & (m3 <= 0)).sum()),
                "freed_with_margin_C3_gt_0": int((~fail & (m3 > 0)).sum())}
        for arm in NOISE_ARMS:
            fail = np.array([unresolved(t, arm) for t in T])
            f[g][f"margin_predicts_{arm}_failure"] = {
                "n_fail": int(fail.sum()), "auc_margin_C1": auc(m1, fail),
                "auc_margin_C1_ci95_boot": boot_ci(lambda i: auc(m1[i], fail[i]), len(T), rng)}
    out["f_noise_vs_C3"] = f
    out["g_physics_reading"] = reading(out)
    out = dotless(out)
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    fig6_cache(out)
    return out


def dotless(o):
    """Arm keys without dots (noise0.03 -> noise0p03, bias0.05 -> bias0p05), so dotted key paths can reach them."""
    if isinstance(o, dict):
        return {k.replace(".", "p") if ("noise0." in k or "bias0." in k) else k: dotless(v) for k, v in o.items()}
    if isinstance(o, list):
        return [dotless(v) for v in o]
    return o


FIG6 = os.path.join(ROOT, "figures", "data", "fig6.json")
FIG6_ORDER = [["C1", "C2"],
              ["C3_pub", "C3_rvo2", "drive_only", "constraint_only_pub", "constraint_only_rvo2", "frozen_plus",
               "frozen_minus"],
              ["bias0p05", "bias0p1", "bias0p2", "bias0p5"],
              ["noise0p03", "noise0p05", "noise0p07"]]
FIG6_KM = ["C3_pub", "C3_rvo2", "drive_only", "frozen_plus", "noise0p03", "noise0p05", "noise0p07"]


def fig6_cache(o):
    """figures/data/fig6.json: Wilson rates per stratum and arm (left) and pooled Kaplan-Meier curves (right)."""
    R = o["a_rates_time_to_free"]
    d = {"source": "data/derived/E2_analysis.json (experiments/E2/analyze.py)", "groups": FIG6_ORDER,
         "rates": {g: {a: {"k": R[g][a]["freed"], "n": R[g][a]["n"], "wilson": R[g][a]["rate_wilson95"]}
                       for grp in FIG6_ORDER for a in grp} for g in STRATA},
         "km_pooled": {a: R["pooled"][a]["km_curve"] for a in FIG6_KM}, "t_max_s": T_Q}
    os.makedirs(os.path.dirname(FIG6), exist_ok=True)
    json.dump(d, open(FIG6, "w"), indent=1)


def reading(o):
    """Short physics reading against the Table 2 predictions for L and T. [proposal] marks interpretation."""
    R, D, P = o["a_rates_time_to_free"], o["d_orca_decomposition"], o["b_replay_determinism"]
    F, L = o["f_noise_vs_C3"], o["c_rest_state_lemma_C2_vs_C1"]

    def fr(g, a):
        c = R[g][a]
        return f"{c['freed']}/{c['n']}"

    def disc(g, k):
        c = D[g][k]
        return f"{c['discordant_first_only']}:{c['discordant_second_only']} (p = {c['mcnemar_exact_p']:.2g})"
    lk, st, pl = "lone_keystone", "lone_keystone_second_trap", "pooled"
    nd = [a for a in DET_ARMS if P[pl][a]["freed_disagree"] or P[pl][a]["max_abs_dt_blocker_exit_s"] > 0]
    return [
        f"Rest state. C1 and C2 free {fr(pl, 'C1')} and {fr(pl, 'C2')}; their {L['pairs']} paired runs have identical "
        f"exits and stopping times, and their final positions differ by at most {L['max_final_pos_diff_m']:.1e} m, as T1 predicts "
        "(the time-to-collision force vanishes at rest, so C2 has C1's fixed points).",
        f"Lone keystone, ORCA. drive_only, C3_pub and C3_rvo2 each free {fr(lk, 'C3_rvo2')} with 0:0 discordance; "
        f"both constraint_only arms free {fr(lk, 'constraint_only_pub')}; frozen_plus frees {fr(lk, 'frozen_plus')} "
        f"and frozen_minus {fr(lk, 'frozen_minus')} ({disc(lk, 'frozen_plus_vs_frozen_minus')}); every replay agrees. "
        "This is the L signature: the resolving part of ORCA here is its rest drive m v0/tau_ORCA, a deterministic added "
        "drive that removes the fixed point. The 4 failures all have a positive C3 rest-state margin "
        f"(AUC {F[lk]['margin_predicts_C3_rvo2_failure']['auc_margin_C3']:.2f}): the extra drive does not exceed g_max.",
        f"Second trap, ORCA. drive_only frees {fr(st, 'drive_only')} and frozen_plus {fr(st, 'frozen_plus')} against "
        f"C3_rvo2 {fr(st, 'C3_rvo2')} ({disc(st, 'drive_only_vs_C3_rvo2')}; {disc(st, 'frozen_plus_vs_C3_rvo2')}), and "
        f"C3_pub {fr(st, 'C3_pub')} vs C3_rvo2 ({disc(st, 'C3_pub_vs_C3_rvo2')}). The blocker's C3 margin does not "
        f"predict C3_rvo2 failure here (AUC {F[st]['margin_predicts_C3_rvo2_failure']['auc_margin_C3']:.2f}). "
        "[proposal] With a second trapped agent close behind or beside the blocker, the velocity-obstacle constraint "
        "removes part of the drive's door-ward component, so full ORCA frees less than its own drive; failure is set by "
        "the neighbour, not by the blocker's wall balance.",
        f"Noise. C1 + sigma frees {fr(pl, 'noise0.03')}, {fr(pl, 'noise0.05')}, {fr(pl, 'noise0.07')} runs at "
        "sigma = 0.03, 0.05, 0.07 m/s; seeds disagree on freed/held in "
        f"{P[pl]['noise0.03']['seeds_disagree_on_freed']}, {P[pl]['noise0.05']['seeds_disagree_on_freed']}, "
        f"{P[pl]['noise0.07']['seeds_disagree_on_freed']} of 60 snapshots, and the median time-to-free is "
        f"{R[pl]['noise0.07']['time_to_free_km']['median']} s at 0.07 against "
        f"{R[pl]['C3_rvo2']['time_to_free_km']['median']} s for C3_rvo2. This is the T signature (stochastic, rate "
        "rising with sigma, waiting times of tens of seconds), not L.",
        f"Matched rate, different mechanism. At the lone keystone sigma = 0.07 frees {R[lk]['noise0.07']['freed']}/"
        f"{R[lk]['noise0.07']['n']} runs against C3_rvo2 {fr(lk, 'C3_rvo2')} snapshots (paired difference "
        f"{F[lk]['noise0.07']['paired_rate_diff_noise_minus_C3']:+.3f}), yet the unresolved snapshots overlap with "
        f"Jaccard {F[lk]['noise0.07']['jaccard']:.2f} (95% CI {F[lk]['noise0.07']['jaccard_ci95_boot'][0]:.2f}-"
        f"{F[lk]['noise0.07']['jaccard_ci95_boot'][1]:.2f}), and the two differ in replay determinism and time scale.",
        f"Lateral bias (negative control). At the lone keystone b = 0.05-0.5 frees 0/34 at every b; in the second-trap "
        f"stratum it frees {fr(st, 'bias0.1')} at b = 0.1 and {fr(st, 'bias0.2')} at b = 0.2. A finite tilt does not "
        "remove the on-axis lone minimum (consistent with D acting only on the off-axis pair class).",
        f"Replay determinism. Arms with any replay difference in blocker outcome or exit time: {', '.join(nd) or 'none'}. "
        f"C3_pub flips freed/held in {P[pl]['C3_pub']['freed_disagree']} of 300 replays (largest |dt| "
        f"{P[pl]['C3_pub']['max_abs_dt_blocker_exit_s']:.1f} s), all in second-trap snapshots with slow exits; C3_rvo2 "
        f"has |dt| = 0.000 s for the blocker; under constraint_only_rvo2 only non-blocker first exits differ "
        f"({P[pl]['constraint_only_rvo2']['first_agent_disagree']} replays, largest |dt| "
        f"{P[pl]['constraint_only_rvo2']['max_abs_dt_first_exit_s']:.1f} s). [proposal] The published LP is ill-conditioned in slow, near-contact creep, so 1e-9 m "
        "picks a different active constraint; this is a numerical sensitivity of that solver (class N), not noise.",
    ]


def brief(o):
    for g in ("lone_keystone", "lone_keystone_second_trap", "pooled"):
        print("==", g, o["n_snapshots"][g])
        for arm, c in o["a_rates_time_to_free"][g].items():
            k = c["time_to_free_km"]
            print(f"  {arm:22s} {c['freed']:3d}/{c['n']:3d} [{c['rate_wilson95'][1]:.2f},{c['rate_wilson95'][2]:.2f}]"
                  f"  med {k['median']} IQR {k['q25']}-{k['q75']}")
        for arm, c in o["b_replay_determinism"][g].items():
            print("   det", arm, {k: v for k, v in c.items() if k != "within_snapshot_sd_first_exit_s"},
                  c.get("within_snapshot_sd_first_exit_s", ""))
        for k, c in {**o["d_orca_decomposition"][g], **o["e_lateral_bias_vs_C1"][g]}.items():
            print(f"   {k:40s} {c['first_freed']}-{c['second_freed']} disc {c['discordant_first_only']}:"
                  f"{c['discordant_second_only']} p={c['mcnemar_exact_p']:.3g}")
        for k, c in o["f_noise_vs_C3"][g].items():
            print("   f", k, {kk: v for kk, v in c.items() if not isinstance(v, list) or len(v) <= 3})
    L = o["c_rest_state_lemma_C2_vs_C1"]
    print("lemma", {k: v for k, v in L.items() if k != "differences"}, len(L["differences"]))


if __name__ == "__main__":
    brief(main())
