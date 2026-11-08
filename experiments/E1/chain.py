"""End-of-queue chain re-analysis (plan change C16b): the end of the queue as a chain of stuck-alone agents.

Input:  data/E1/E1_runs.jsonl (both modes, 200 seeds each), data/derived/E1_keystone.json (second-trap class).
Output: data/derived/E1_chain.json.

Definitions (as experiments/E1/e1_analyze.py)
  stuck-alone   margin_C1 = g_max(r) - m v0 / tau > 0; passable = margin_C1 <= 0.
  arrival       first entry into the door zone (field "arrive": t, n_active, behind_1m, order).
  active at t   spawned and not exited by t (exit_t[j] > t, or never exited).
  exited        the agent exits before the run stops (completion, deadlock or 600 s cap).
(a) per run: the arrival sequence (stuck-alone flags in arrival order); stuck-alone fraction by arrival decile
    (decile of the arrival rank within the run, over agents that arrived); the length of the final run of
    consecutive stuck-alone arrivals (deadlocked runs and all runs); the margin of the k-th last arrival;
    succession in the second-trap class: K1b target held alone, its margin and arrival order relative to the
    blocker.
(b) for each stuck-alone agent at its door-zone arrival, predictors of exit, each by ROC AUC (Mann-Whitney, ties
    1/2; positive class = exited) with a 95% CI from 2000 resamples of seeds (percentile, PCG64(12345)):
      others_active         n_active - 1 (the k = 3 rule's score);
      behind_1m             agents within 1 m behind (recorded at arrival);
      passable_active       other agents with margin <= 0 still active;
      stuck_active          other stuck-alone agents still active.
    Also: the best single-threshold accuracy of each count score (exit iff score >= k), the exit rate by
    (passable_active, stuck_active) cell, and the all-exit baseline.
(c) the physical reading tested, with its numbers (field "c_reading").
"""
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "E1_chain.json")
N_BOOT = 2000
RNG_SEED = 12345
SCORES = ("others_active", "behind_1m", "passable_active", "stuck_active")


def auc(score, label):
    score, label = np.asarray(score, float), np.asarray(label, bool)
    pos, neg = score[label], score[~label]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum()
    eq = (pos[:, None] == neg[None, :]).sum()
    return float((gt + 0.5 * eq) / (len(pos) * len(neg)))


def load_runs():
    R = {"E1a": [], "E1b": []}
    for line in open(os.path.join(DATA, "E1", "E1_runs.jsonl")):
        r = json.loads(line)
        R[r["mode"]].append(r)
    for m in R:
        R[m].sort(key=lambda r: r["seed"])
    return R


def blocker_of(r):
    if not r.get("residual"):
        return None
    pos = {x["id"]: np.array(x["pos"]) for x in r["residual"]}
    return min(pos, key=lambda i: np.linalg.norm(pos[i] - [10.0, 5.0]))


def per_run(r):
    margin = {a["id"]: a["margin_C1"] for a in r["attrs"]}
    exit_t = {int(k): v for k, v in r["exit_t"].items()}
    arr = sorted(((int(k), v) for k, v in r["arrive"].items()), key=lambda kv: kv[1]["order"])
    seq = [margin[i] > 0 for i, _ in arr]
    tail = 0
    for s in reversed(seq):
        if not s:
            break
        tail += 1
    rows = []
    for i, a in arr:
        if margin[i] <= 0:
            continue
        t = a["t"]
        act = [j for j in margin if j != i and (j not in exit_t or exit_t[j] > t)]
        pa = sum(margin[j] <= 0 for j in act)
        sa = sum(margin[j] > 0 for j in act)
        rows.append({"seed": r["seed"], "id": i, "margin": margin[i], "exited": i in exit_t,
                     "others_active": a["n_active"] - 1, "behind_1m": a["behind_1m"],
                     "passable_active": pa, "stuck_active": sa, "count_check": pa + sa == a["n_active"] - 1,
                     "order": a["order"]})
    return {"seed": r["seed"], "complete": r["complete"], "deadlock": r["deadlock"], "n_arrived": len(arr),
            "seq": seq, "tail_stuck_run": tail, "margins_in_order": [margin[i] for i, _ in arr],
            "blocker": blocker_of(r), "arrival_order": {i: a["order"] for i, a in arr}}, rows


def analyse(R, ks_mode):
    rng = np.random.Generator(np.random.PCG64(RNG_SEED))
    runs, rows = [], []
    for r in R:
        pr, rw = per_run(r)
        runs.append(pr)
        rows += rw
    out = {"n_runs": len(runs), "n_deadlock": sum(p["deadlock"] for p in runs)}

    # (a) decile profile
    dec = np.zeros(10)
    dec_n = np.zeros(10)
    for p in runs:
        n = p["n_arrived"]
        for k, s in enumerate(p["seq"]):
            d = min(int(10 * k / n), 9)
            dec[d] += s
            dec_n[d] += 1
    out["a_stuck_fraction_by_arrival_decile"] = {"frac": (dec / dec_n).tolist(), "n": dec_n.astype(int).tolist()}
    dl = [p for p in runs if p["deadlock"]]
    tails = np.array([p["tail_stuck_run"] for p in dl])
    out["a_final_stuck_run_length"] = {
        "deadlocked_runs": len(dl), "median": float(np.median(tails)), "p25": float(np.percentile(tails, 25)),
        "p75": float(np.percentile(tails, 75)), "min": int(tails.min()), "max": int(tails.max()),
        "hist": {str(k): int((tails == k).sum()) for k in range(int(tails.max()) + 1)},
        "completed_runs_tail_median": float(np.median([p["tail_stuck_run"] for p in runs if p["complete"]]))
        if any(p["complete"] for p in runs) else None}
    # margin of the last arrivals vs the rest
    last5 = [m for p in runs for m in p["margins_in_order"][-5:]]
    rest = [m for p in runs for m in p["margins_in_order"][:-5]]
    out["a_margin_last5_vs_rest"] = {"last5_median_N": float(np.median(last5)), "rest_median_N": float(np.median(rest)),
                                     "last5_stuck_frac": float(np.mean(np.array(last5) > 0)),
                                     "rest_stuck_frac": float(np.mean(np.array(rest) > 0))}
    # blocker = last arrival?
    bl = [p for p in dl if p["blocker"] is not None and p["blocker"] in p["arrival_order"]]
    ranks_from_end = [p["n_arrived"] - 1 - p["arrival_order"][p["blocker"]] for p in bl]
    out["a_blocker_arrival_rank_from_end"] = {
        "n": len(bl), "median": float(np.median(ranks_from_end)),
        "within_last_3": int(sum(x <= 2 for x in ranks_from_end)),
        "within_last_5": int(sum(x <= 4 for x in ranks_from_end))}
    # succession in the second-trap class
    st = [s for s in ks_mode["per_snapshot"] if s["class"] == "lone_keystone_second_trap"]
    byseed = {p["seed"]: p for p in runs}
    succ = {"n": len(st), "K1b_held": 0, "K1b_held_target_stuck_alone": 0, "K1b_freed": 0,
            "K1b_freed_target_stuck_alone": 0, "target_arrived_before_blocker": 0, "target_arrived_after_blocker": 0,
            "target_not_arrived": 0, "target_margin_held_median_N": None}
    hm = []
    for s in st:
        k = s["K1b"]
        held = bool(k and k["held"])
        tm = k["target_margin_C1"] if k else None
        if held:
            succ["K1b_held"] += 1
            succ["K1b_held_target_stuck_alone"] += int(tm > 0)
            hm.append(tm)
        else:
            succ["K1b_freed"] += 1
            succ["K1b_freed_target_stuck_alone"] += int(tm is not None and tm > 0)
        ao = byseed[s["seed"]]["arrival_order"]
        tgt, b = (k["target"] if k else None), s["blocker"]
        if tgt is None or tgt not in ao or b not in ao:
            succ["target_not_arrived"] += 1
        elif ao[tgt] < ao[b]:
            succ["target_arrived_before_blocker"] += 1
        else:
            succ["target_arrived_after_blocker"] += 1
    succ["target_margin_held_median_N"] = float(np.median(hm)) if hm else None
    out["a_second_trap_succession"] = succ

    # (b) predictors
    lab = np.array([x["exited"] for x in rows])
    seeds = sorted({x["seed"] for x in rows})
    seed_of = np.array([x["seed"] for x in rows])
    idx = {s: np.where(seed_of == s)[0] for s in seeds}
    boot = rng.integers(0, len(seeds), (N_BOOT, len(seeds)))
    bidx = [np.concatenate([idx[seeds[j]] for j in b]) for b in boot]
    pred = {}
    for sc in SCORES:
        v = np.array([x[sc] for x in rows], float)
        bs = np.array([auc(v[ii], lab[ii]) for ii in bidx])
        bs = bs[np.isfinite(bs)]
        accs = {k: float(np.mean((v >= k) == lab)) for k in range(0, 31)}
        kb = max(accs, key=lambda k: (accs[k], -k))
        pred[sc] = {"auc": auc(v, lab), "ci95_seed_bootstrap": [float(np.percentile(bs, 2.5)),
                                                                 float(np.percentile(bs, 97.5))],
                    "best_threshold_k": kb, "best_threshold_accuracy": accs[kb],
                    "accuracy_at_k3": accs[3], "accuracy_at_k1": accs[1]}
    out["b_predictors"] = {"n_stuck_alone_arrived": len(rows), "exited": int(lab.sum()),
                           "all_exit_baseline": float(lab.mean()),
                           "counts_consistent_with_n_active": int(sum(x["count_check"] for x in rows)),
                           "scores": pred}
    cells = {}
    for x in rows:
        key = (min(x["passable_active"], 3), min(x["stuck_active"], 3))
        c = cells.setdefault(key, [0, 0])
        c[0] += x["exited"]
        c[1] += 1
    out["b_exit_rate_by_passable_x_stuck"] = {
        "note": "keys 'p<passable_active>|s<stuck_active>', each capped at 3 (3 = 3 or more); value [exited, n]",
        "cells": {f"p{k[0]}|s{k[1]}": v for k, v in sorted(cells.items())}}
    # direct test: with no passable agent left, does any stuck-alone agent exit?
    p0 = [x for x in rows if x["passable_active"] == 0]
    p1 = [x for x in rows if x["passable_active"] >= 1]
    out["b_passable_zero_vs_positive"] = {
        "passable0": {"n": len(p0), "exited": sum(x["exited"] for x in p0),
                      "stuck_active_median": float(np.median([x["stuck_active"] for x in p0])) if p0 else None},
        "passable_ge1": {"n": len(p1), "exited": sum(x["exited"] for x in p1)}}
    # others-active errors explained by passable count
    k3_wrong = [x for x in rows if (x["others_active"] >= 3) != x["exited"]]
    out["b_k3_errors"] = {"n": len(k3_wrong),
                          "of_which_passable0_not_exited": sum((x["passable_active"] == 0) and not x["exited"]
                                                              for x in k3_wrong)}
    return out


def reading(res):
    lines = []
    for m in ("E1a", "E1b"):
        o = res[m]
        P = o["b_predictors"]["scores"]
        z = o["b_passable_zero_vs_positive"]
        d = o["a_stuck_fraction_by_arrival_decile"]["frac"]
        s = o["a_second_trap_succession"]
        lines.append(
            f"{m}: stuck-alone fraction rises from {d[0]:.2f} in the first arrival decile to {d[-1]:.2f} in the last; "
            f"the last five arrivals have median margin {o['a_margin_last5_vs_rest']['last5_median_N']:.0f} N "
            f"(rest {o['a_margin_last5_vs_rest']['rest_median_N']:.0f} N). Exit AUC: passable_active "
            f"{P['passable_active']['auc']:.3f} [{P['passable_active']['ci95_seed_bootstrap'][0]:.3f}, "
            f"{P['passable_active']['ci95_seed_bootstrap'][1]:.3f}], others_active {P['others_active']['auc']:.3f}, "
            f"stuck_active {P['stuck_active']['auc']:.3f}, behind_1m {P['behind_1m']['auc']:.3f}. With no passable "
            f"agent left, {z['passable0']['exited']}/{z['passable0']['n']} stuck-alone arrivals exit; with at least one, "
            f"{z['passable_ge1']['exited']}/{z['passable_ge1']['n']}. Second trap: K1b held in {s['K1b_held']}/{s['n']}, "
            f"target stuck alone in {s['K1b_held_target_stuck_alone']} of those.")
    o = res["E1b"]
    P = o["b_predictors"]["scores"]
    z = o["b_passable_zero_vs_positive"]
    c = o["b_exit_rate_by_passable_x_stuck"]["cells"]["p0|s3"]
    d = o["a_stuck_fraction_by_arrival_decile"]["frac"]
    b = o["a_blocker_arrival_rank_from_end"]
    lines.append(
        "Verdict (E1b). Supported: passable agents drain first, so the last arrivals are enriched in stuck-alone "
        f"agents ({d[-1]:.2f} in the last arrival decile against {min(d[:8]):.2f}-{max(d[:8]):.2f} in the first eight; "
        f"the final blocker is among the last three arrivals in {b['within_last_3']}/{b['n']} deadlocked runs). "
        "Not supported: that only passable agents can push a stuck-alone agent through. With no passable agent left, "
        f"{z['passable0']['exited']}/{z['passable0']['n']} stuck-alone arrivals still exit ({c[0]}/{c[1]} when three or "
        f"more stuck-alone agents are still in the room), and stuck-alone pushers predict exit at least as well (AUC "
        f"{P['stuck_active']['auc']:.3f} against {P['passable_active']['auc']:.3f} for passable ones). Cleanest "
        "statement: a stuck-alone agent is pushed through by whoever is still in the room, whether or not those agents "
        f"could pass alone; the total count is the best single predictor (AUC {P['others_active']['auc']:.3f}, "
        f"[{P['others_active']['ci95_seed_bootstrap'][0]:.3f}, {P['others_active']['ci95_seed_bootstrap'][1]:.3f}]), "
        "and the chain ends when fewer than about three others are still in the room as the last stuck-alone agent arrives.")
    return lines


def main():
    R = load_runs()
    ks = json.load(open(os.path.join(DATA, "derived", "E1_keystone.json")))["modes"]
    res = {"script": "experiments/E1/chain.py", "doc": __doc__}
    for m in ("E1a", "E1b"):
        res[m] = analyse(R[m], ks[m])
    res["second_trap_both_modes"] = {
        "n": sum(res[m]["a_second_trap_succession"]["n"] for m in ("E1a", "E1b")),
        "K1b_held": sum(res[m]["a_second_trap_succession"]["K1b_held"] for m in ("E1a", "E1b"))}
    res["c_reading"] = reading(res)
    json.dump(res, open(OUT, "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    r = main()
    for m in ("E1a", "E1b"):
        o = r[m]
        print("==", m)
        for k, v in o.items():
            if k != "b_exit_rate_by_passable_x_stuck":
                print(" ", k, v)
        print("  cells", o["b_exit_rate_by_passable_x_stuck"]["cells"])
    print(r["second_trap_both_modes"])
    print(*r["c_reading"], sep="\n")
