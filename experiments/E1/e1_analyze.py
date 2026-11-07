"""E1 analysis, each mode separately. Input data/E1/E1_runs.jsonl(.gz); output data/derived/E1_analysis.json.

Definitions follow wave2/scripts/w21_analyze.py:
  stuck-alone agent   margin_C1 = g_max(r) - m v0 / tau > 0 (rest state on the door axis, rho = 0);
  blocker             residual agent nearest the door centre (10, 5) in a run that did not complete;
  end-of-queue rule   a stuck-alone agent is predicted to exit iff at least k other agents are active
                      when it first reaches the door zone (others = n_active at arrival - 1); only
                      stuck-alone agents that reached the door zone enter the rule.
Leave-one-seed-out: for each seed, k in 1..29 is chosen to maximise pooled agent-level accuracy on the
other seeds (ties: smallest k) and applied to that seed's stuck-alone agents. Confidence intervals
from 2000 resamples of seeds (with replacement; percentile intervals; numpy PCG64 seed 12345).
ROC AUC: score = others active at arrival, positive class = exited (Mann-Whitney, ties count 1/2).
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import DERIVED, Passability, load_runs, runs_path, weidmann_factor, wilson
import numpy as np

K_RANGE = range(1, 30)
N_BOOT = 2000
RNG_SEED = 12345
M, TAU_ORCA = 80.0, 0.5
W_O_REST = 1.0 - 1.0 / (1.0 + np.exp(-2.0 * (0.0 - 4.0)))   # ORCA gate at rho = 0 (Passability)


def q(a, ps=(0, 5, 25, 50, 75, 95, 100)):
    a = np.asarray(a, float)
    return {f"p{p}": float(np.percentile(a, p)) for p in ps} if len(a) else None


def auc(score, label):
    score, label = np.asarray(score, float), np.asarray(label, bool)
    pos, neg = score[label], score[~label]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum()
    eq = (pos[:, None] == neg[None, :]).sum()
    return float((gt + 0.5 * eq) / (len(pos) * len(neg)))


def confusion(rows, k):
    tp = sum((x["others"] >= k) and x["exited"] for x in rows)
    fp = sum((x["others"] >= k) and not x["exited"] for x in rows)
    fn = sum((x["others"] < k) and x["exited"] for x in rows)
    tn = sum((x["others"] < k) and not x["exited"] for x in rows)
    n = tp + fp + fn + tn
    return {"k": k, "accuracy": (tp + tn) / n if n else float("nan"),
            "TP_pred_exit_obs_exit": tp, "FP_pred_exit_obs_stuck": fp,
            "FN_pred_stuck_obs_exit": fn, "TN_pred_stuck_obs_stuck": tn, "n": n}


def analyse(R, PASS):
    out = {"n_runs": len(R), "seeds": [min(r["seed"] for r in R), max(r["seed"] for r in R)]}
    n_c = sum(r["complete"] for r in R)
    n_d = sum(r["deadlock"] for r in R)
    out["completion"] = {"k": n_c, "n": len(R), "rate_wilson95": wilson(n_c, len(R))}
    out["deadlock"] = {"k": n_d, "n": len(R),
                       "capped_600s_without_deadlock": sum((not r["complete"]) and not r["deadlock"] for r in R)}
    out["deadlock_time_s"] = q([r["t_end"] for r in R if r["deadlock"]])
    out["completion_time_s"] = q([r["t_end"] for r in R if r["complete"]])
    out["exits_per_run"] = q([r["n_exits"] for r in R])
    out["wall_s_per_run"] = q([r["wall_s"] for r in R])
    types = [r["deadlock_type"]["type"] for r in R if r["deadlock"]]
    out["deadlock_type_counts"] = {t: types.count(t) for t in ("lone", "pair", "triple", "larger", "none_at_door")}
    out["n_remaining_hist"] = {str(k): sum(r["n_remaining"] == k for r in R if r["deadlock"])
                               for k in sorted({r["n_remaining"] for r in R if r["deadlock"]})}

    # stuck-alone population
    allm = np.array([a["margin_C1"] for r in R for a in r["attrs"]])
    allm3 = np.array([a["margin_C3"] for r in R for a in r["attrs"]])
    out["stuck_alone_frac_C1"] = {"k": int((allm > 0).sum()), "n": len(allm), "frac": float((allm > 0).mean())}
    out["stuck_alone_frac_C3_rest"] = {"k": int((allm3 > 0).sum()), "n": len(allm3), "frac": float((allm3 > 0).mean())}

    rows, blockers = [], []
    for r in R:
        at = {a["id"]: a for a in r["attrs"]}
        exits = {int(k) for k in r["exit_t"]}
        arrive = {int(k): v for k, v in r["arrive"].items()}
        for i, a in at.items():
            if a["margin_C1"] > 0 and i in arrive:
                rows.append({"seed": r["seed"], "id": i, "margin": a["margin_C1"], "exited": i in exits,
                             "others": arrive[i]["n_active"] - 1, "order": arrive[i]["order"]})
        if r.get("residual"):
            pos = {x["id"]: np.array(x["pos"]) for x in r["residual"]}
            b = min(pos, key=lambda i: np.linalg.norm(pos[i] - [10.0, 5.0]))
            blockers.append({"seed": r["seed"], "blocker": b, "margin_C1": at[b]["margin_C1"],
                             "margin_C3": at[b]["margin_C3"], "r": at[b]["r"], "v0": at[b]["v0"],
                             "tau": at[b]["tau"], "pos": pos[b].tolist(), "n_resid": len(pos),
                             "deadlock_type": r.get("deadlock_type", {}).get("type"),
                             "others_at_arrival": arrive[b]["n_active"] - 1 if b in arrive else None})
    n_stuck_never_arrived = int((allm > 0).sum()) - len(rows)
    out["stuck_alone_agents"] = {"n_reached_door_zone": len(rows), "n_never_reached": n_stuck_never_arrived,
                                 "exited": sum(x["exited"] for x in rows),
                                 "not_exited": sum(not x["exited"] for x in rows)}
    out["blockers"] = {"n": len(blockers), "stuck_alone": sum(b["margin_C1"] > 0 for b in blockers),
                       "stuck_alone_C3_rest": sum(b["margin_C3"] > 0 for b in blockers),
                       "list": blockers}

    # end-of-queue rule, pooled
    out["k_rule_pooled"] = [confusion(rows, k) for k in range(1, 7)]
    acc_all = {k: confusion(rows, k)["accuracy"] for k in K_RANGE}
    out["k_rule_pooled_best_k"] = min(K_RANGE, key=lambda k: (-acc_all[k], k))

    # leave one seed out
    seeds = sorted({r["seed"] for r in R})
    by_seed = {s: [x for x in rows if x["seed"] == s] for s in seeds}
    tot = {k: np.array([sum(((x["others"] >= k) == x["exited"]) for x in by_seed[s]) for s in seeds]) for k in K_RANGE}
    cnt = np.array([len(by_seed[s]) for s in seeds])
    chosen, correct = [], np.zeros(len(seeds))
    for j, s in enumerate(seeds):
        acc_k = {k: (tot[k].sum() - tot[k][j]) / max(cnt.sum() - cnt[j], 1) for k in K_RANGE}
        kj = min(K_RANGE, key=lambda k: (-acc_k[k], k))
        chosen.append(kj)
        correct[j] = tot[kj][j]
    rng = np.random.Generator(np.random.PCG64(RNG_SEED))
    boot_idx = rng.integers(0, len(seeds), (N_BOOT, len(seeds)))
    boot = correct[boot_idx].sum(1) / np.maximum(cnt[boot_idx].sum(1), 1)
    out["k_rule_leave_one_seed_out"] = {
        "heldout_accuracy": float(correct.sum() / cnt.sum()), "n_agents": int(cnt.sum()),
        "ci95_seed_bootstrap": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        "chosen_k_counts": {str(k): chosen.count(k) for k in sorted(set(chosen))}}

    # AUC of others-active-at-arrival
    sc = np.array([x["others"] for x in rows], float)
    lb = np.array([x["exited"] for x in rows], bool)
    seed_of = np.array([x["seed"] for x in rows])
    idx_by_seed = {s: np.where(seed_of == s)[0] for s in seeds}
    boots = []
    for b in boot_idx:
        ii = np.concatenate([idx_by_seed[seeds[j]] for j in b])
        boots.append(auc(sc[ii], lb[ii]))
    boots = np.array(boots)
    boots = boots[np.isfinite(boots)]
    out["auc_others_active"] = {"auc": auc(sc, lb), "n_pos": int(lb.sum()), "n_neg": int((~lb).sum()),
                                "ci95_seed_bootstrap": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}

    # inputs for the lone-trap physics figure
    v0 = np.array([a["v0"] for r in R for a in r["attrs"]])
    tau = np.array([a["tau"] for r in R for a in r["attrs"]])
    d_arr = np.array([v["drive_C1"] for r in R for v in r["arrive"].values()])
    out["drives_N"] = {
        "C1_free_m_v0_over_tau": q(M * v0 / tau),
        "C1_at_arrival_m_veff_over_tau": q(d_arr),
        "C3_rest_orca_drive_w_o_m_v0_over_tau_orca": q(W_O_REST * M * v0 / TAU_ORCA),
        "C3_rest_total": q(M * v0 / tau + W_O_REST * M * v0 / TAU_ORCA),
        "hist_edges_N": list(np.arange(0, 1201, 20.0)),
        "hist_C1_free": np.histogram(M * v0 / tau, np.arange(0, 1201, 20.0))[0].tolist(),
        "hist_C1_arrival": np.histogram(d_arr, np.arange(0, 1201, 20.0))[0].tolist(),
        "hist_C3_orca_rest": np.histogram(W_O_REST * M * v0 / TAU_ORCA, np.arange(0, 1201, 20.0))[0].tolist()}
    out["arrival_veff_over_v0"] = q([v["v_eff"] / at_v0 for r in R for k, v in r["arrive"].items()
                                     for at_v0 in [r["attrs"][int(k)]["v0"]]])
    return out


if __name__ == "__main__":
    R_all = load_runs(runs_path())
    PASS = Passability(0.8)
    res = {"script": "experiments/E1/e1_library.py + e1_analyze.py", "doc": __doc__,
           "setup": "C1, room bottleneck w=0.8 m, 100 agents, dt=0.01 s, sigma=0, cap 600 s, stop at deadlock "
                    "(all active |v|<0.01 m/s for 10 s, no exit) or completion, w2_metrics=light; seeds 42-241"}
    for mode in ("E1a", "E1b"):
        R = sorted([r for r in R_all if r["mode"] == mode], key=lambda r: r["seed"])
        if R:
            res[mode] = analyse(R, PASS)
    # wall law (identical in both modes: corner rule inert on the room axis)
    res["gmax_N"] = {f"{r:.2f}": PASS.gmax(r) for r in (0.20, 0.25, 0.30, 0.35)}
    res["gmax_curve"] = {"r_m": PASS.rs.tolist(), "gmax_N": PASS.g.tolist()}
    rs = PASS.rs
    res["stuck_alone_boundary"] = {
        "note": "C1: stuck alone iff v0/tau < g_max(r)/m. C3 rest state: iff m v0 (1/tau + w_o/tau_ORCA) < g_max(r); "
                "in the (r, v0/tau) plane this depends on tau, given for tau = 0.4, 0.5, 0.6 s.",
        "r_m": rs.tolist(),
        "C1_v0_over_tau_star": (PASS.g / M).tolist(),
        "C3_v0_over_tau_star": {f"tau={t}": (PASS.g / (M * (1 + W_O_REST * t / TAU_ORCA))).tolist()
                                for t in (0.4, 0.5, 0.6)},
        "w_o_rest": W_O_REST, "m_kg": M, "tau_orca_s": TAU_ORCA}
    json.dump(res, open(os.path.join(DERIVED, "E1_analysis.json"), "w"), indent=1, default=float)
    for mode in ("E1a", "E1b"):
        if mode not in res:
            continue
        o = res[mode]
        print(mode, "runs", o["n_runs"], "completion", o["completion"], "deadlock", o["deadlock"])
        print("  types", o["deadlock_type_counts"], "deadlock t", o["deadlock_time_s"])
        print("  stuck frac", o["stuck_alone_frac_C1"], "C3", o["stuck_alone_frac_C3_rest"])
        print("  blockers", o["blockers"]["n"], "stuck", o["blockers"]["stuck_alone"], "agents", o["stuck_alone_agents"])
        for c in o["k_rule_pooled"]:
            print("   ", c)
        print("  LOSO", o["k_rule_leave_one_seed_out"], "AUC", o["auc_others_active"])
    print("gmax", res["gmax_N"])
