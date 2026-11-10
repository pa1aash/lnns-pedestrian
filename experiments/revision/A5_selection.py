"""A5: snapshot selection traced from the data, and a balance check of the 26 second traps drawn for E2.

Inputs (existing data only; no simulation):
  data/E1/E1_runs.jsonl              E1b whole runs (200, run seeds 42-241): complete / deadlock, snapshot
                                     path, per-agent attributes (r, v0, tau, margin_C1), residual positions
  data/E1/library/E1b_seed<N>.pkl    saved snapshots (existence checked)
  data/derived/E1_keystone.json      keystone test per E1b deadlock (class, blocker, n_resid, margin, K1b)
  data/derived/selection.json        E2 / BAR / E3 / E4 selections (experiments/selection.py)
  data/E7b/e7b_static.jsonl, e7b_barrier.jsonl   pair library (46) and pair barriers (12)
  data/E2/e2_quench.jsonl            wall time per E2 quench (cost estimate)
  data/revision/A5/smoke_timing.json wall times of the A5_extra_second_traps.py smoke test (if present)
Output: data/derived/rev_A5.json

Computes
  funnel     whole runs -> deadlocks -> saved snapshots -> keystone classes -> E2 strata; the PCG64(2026) draw
             re-run and checked against selection.json.
  bar_e3_e4  BAR validity gate on the 60 (C15a), then E3 (collective Delta U >= 3 J among gate-accepted;
             20 at ranks round(linspace(0, n-1, 20)) of (Delta U, seed)) and E4 (n_resid >= 2 among
             gate-accepted, n_resid counting the blocker; 10 at ranks round(linspace(0, n-1, 10))),
             with the counts split by stratum and the ranks re-derived.
  pair       E7b: 46 library snapshots sorted by mu1 (smallest Hessian eigenvalue, key lambda1), the 12 at
             ranks round(linspace(0, 45, 12)); channels accepted by the gate; re-derived.
  balance    the 26 drawn second traps against the 134 not drawn, on covariates fixed before any quench:
             blocker margin_C1, n_resid, blocker r / v0 / tau, blocker lateral offset |y - 5| and distance
             to the door centre, deadlock detection time, number of agents held when the blocker is
             removed (K2), the second trap's own margin and radius, whether the second trap is stuck alone
             (K1b held), run seed. Continuous / ordinal: two-sided Mann-Whitney U and two-sample KS;
             binary: two-sided Fisher exact. Holm over the Mann-Whitney / Fisher p-values. Standardised
             mean difference (pooled SD). Omnibus: the largest |SMD| over the covariates compared with
             its distribution over 20000 random draws of 26 of the 160 (PCG64(12345)).
  cost       per-snapshot cost of the A5 arm set (noise 0.07 x 5, C3_rvo2 + 5 replays, drive_only,
             frozen_plus) from the mean E2 wall time of each arm on the 26 second traps, times 134.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

D = revlib.DERIVED
CLS_A, CLS_B = "lone_keystone", "lone_keystone_second_trap"
DOOR = np.array([10.0, 5.0])


def jl(path):
    return [json.loads(x) for x in open(path) if x.strip()]


def funnel():
    runs = [r for r in jl(os.path.join(revlib.DATA, "E1", "E1_runs.jsonl")) if r["mode"] == "E1b"]
    dead = [r for r in runs if r["deadlock"]]
    lib = os.path.join(revlib.DATA, "E1", "library")
    saved = [r for r in dead if r.get("snapshot") and os.path.exists(os.path.join(lib, f"E1b_seed{r['seed']}.pkl"))]
    ks = json.load(open(os.path.join(D, "E1_keystone.json")))["modes"]["E1b"]
    per = ks["per_snapshot"]
    cls = {c: sorted(x["seed"] for x in per if x["class"] == c) for c in (CLS_A, CLS_B, "collective")}
    rng = np.random.Generator(np.random.PCG64(2026))
    drawn = sorted(int(s) for s in rng.choice(cls[CLS_B], 26, replace=False))
    sel = json.load(open(os.path.join(D, "selection.json")))
    e2 = sel["E2"]["snapshots"]
    e2b = sorted(s["seed"] for s in e2 if s["class"] == CLS_B)
    e2a = sorted(s["seed"] for s in e2 if s["class"] == CLS_A)
    assert drawn == e2b and e2a == cls[CLS_A]
    st = ks["second_trap"]
    return {
        "runs": len(runs), "complete": sum(r["complete"] for r in runs), "deadlocks": len(dead),
        "snapshots_saved": len(saved), "classified": len(per),
        "lone_keystone": len(cls[CLS_A]), "second_trap": len(cls[CLS_B]), "group_standoff": len(cls["collective"]),
        "group_standoff_seeds": cls["collective"],
        "second_trap_held_alone": st["K1b_held"], "second_trap_freed_alone": st["K1b_freed"],
        "e2_lone_keystone": len(e2a), "e2_second_trap": len(e2b), "e2_total": len(e2),
        "second_trap_pool": len(cls[CLS_B]), "second_trap_not_drawn": len(cls[CLS_B]) - len(e2b),
        "pool_equals_population": True, "pool_missing_pickle": len(cls[CLS_B]) - sum(
            os.path.exists(os.path.join(lib, f"E1b_seed{s}.pkl")) for s in cls[CLS_B]),
        "draw_reproduced": drawn == e2b, "drawn_seeds": drawn,
        "rule": "E2 = all 34 lone keystones + numpy Generator(PCG64(2026)).choice(160 second-trap seeds ascending, 26, replace=False)",
    }


def spread_idx(n, k):
    return [int(i) for i in np.round(np.linspace(0, n - 1, k)).astype(int)] if n > k else list(range(n))


def bar_e3_e4():
    sel = json.load(open(os.path.join(D, "selection.json")))
    cls = {s["tag"]: s["class"] for s in sel["E2"]["snapshots"]}
    B = sel["BAR"]["per_snapshot"]
    exc = sel["BAR"]["gate_excluded"]

    def by(rows):
        return {"lone_keystone": sum(cls[r["tag"]] == CLS_A for r in rows),
                "second_trap": sum(cls[r["tag"]] == CLS_B for r in rows)}

    q3 = sorted([r for r in B if r["dU"] >= 3.0], key=lambda r: (r["dU"], int(r["tag"].split("seed")[1])))
    q4 = sorted([r for r in B if r["n_resid"] >= 2], key=lambda r: (r["dU"], int(r["tag"].split("seed")[1])))
    i3, i4 = spread_idx(len(q3), 20), spread_idx(len(q4), 10)
    assert [q3[i]["tag"] for i in i3] == [s["tag"] for s in sel["E3"]["snapshots"]]
    assert [q4[i]["tag"] for i in i4] == [s["tag"] for s in sel["E4"]["snapshots"]]
    both = [r for r in B if r["dU"] >= 3.0 and r["n_resid"] >= 2]
    e3s = [s for s in sel["E3"]["snapshots"]]
    e4s = [s for s in sel["E4"]["snapshots"]]
    return {
        "bar_input": len(sel["E2"]["snapshots"]), "gate_fail": len(exc),
        "gate_fail_tags": [e["tag"] for e in exc], "gate_fail_classes": [cls[e["tag"]] for e in exc],
        "gate_fail_second_trap": sum(cls[e["tag"]] == CLS_B for e in exc),
        "gate_fail_reasons": {e["tag"]: e["reasons"] for e in exc},
        "gate_accepted": len(B), "gate_accepted_by_class": by(B),
        "e3": {"rule": "gate-accepted and collective (full, all residual agents mobile) Delta U >= 3 J; "
                       "20 at ranks round(linspace(0, n_q - 1, 20)) of the qualifying list sorted by (Delta U, seed)",
               "qualifying": len(q3), "qualifying_by_class": by(q3), "below_3J": len(B) - len(q3),
               "ranks": i3, "n": len(e3s), "by_class": by(e3s),
               "dU_min_J": revlib.sig(min(r["dU"] for r in e3s), 2), "dU_max_J": revlib.sig(max(r["dU"] for r in e3s), 2)},
        "e4": {"rule": "gate-accepted and n_resid >= 2 (blocker plus at least one neighbour); "
                       "10 at ranks round(linspace(0, n_q - 1, 10)) of the qualifying list sorted by (Delta U, seed)",
               "qualifying": len(q4), "qualifying_by_class": by(q4), "single_agent": len(B) - len(q4),
               "ranks": i4, "n": len(e4s), "by_class": by(e4s),
               "dU_min_J": revlib.sig(min(r["dU"] for r in e4s), 2), "dU_max_J": revlib.sig(max(r["dU"] for r in e4s), 2)},
        "e3_and_e4_qualifying": len(both),
        "e3_e4_overlap": len({s["tag"] for s in e3s} & {s["tag"] for s in e4s}),
    }


def pair():
    S = {r["job_id"]: r for r in jl(os.path.join(revlib.DATA, "E7b", "e7b_static.jsonl"))}
    Bt = jl(os.path.join(revlib.DATA, "E7b", "e7b_barrier.jsonl"))
    order = sorted(S, key=lambda t: S[t]["lambda1"])
    idx = sorted(set(spread_idx(len(order), 12)))
    assert sorted(order[i] for i in idx) == sorted(r["job_id"] for r in Bt)
    ch = [c for r in Bt for c in r["channels"].values()]
    lam = np.array([S[t]["lambda1"] for t in order])
    lam_sel = np.array([S[order[i]]["lambda1"] for i in idx])
    return {"library": len(order), "n": len(idx), "ranks": idx,
            "rule": "the 46 pair snapshots sorted by mu1 (smallest Hessian eigenvalue, key lambda1); "
                    "12 at ranks round(linspace(0, 45, 12))",
            "accepted": sum(r.get("dU") is not None for r in Bt),
            "channels_total": len(ch), "channels_accepted": sum(bool(c.get("accepted")) for c in ch),
            "mu1_library_min": revlib.sig(float(lam.min()), 3), "mu1_library_max": revlib.sig(float(lam.max()), 3),
            "mu1_selected_min": revlib.sig(float(lam_sel.min()), 3), "mu1_selected_max": revlib.sig(float(lam_sel.max()), 3)}


def covariates():
    ks = json.load(open(os.path.join(D, "E1_keystone.json")))["modes"]["E1b"]["per_snapshot"]
    R = {r["seed"]: r for r in jl(os.path.join(revlib.DATA, "E1", "E1_runs.jsonl")) if r["mode"] == "E1b"}
    sel = json.load(open(os.path.join(D, "selection.json")))
    drawn = {s["seed"] for s in sel["E2"]["snapshots"] if s["class"] == CLS_B}
    rows = []
    for x in sorted((x for x in ks if x["class"] == CLS_B), key=lambda x: x["seed"]):
        r = R[x["seed"]]
        A = {a["id"]: a for a in r["attrs"]}
        pos = {p["id"]: np.array(p["pos"]) for p in r["residual"]}
        b, t = x["blocker"], x["K1b"]["target"]
        rows.append({
            "seed": x["seed"], "drawn": x["seed"] in drawn,
            "blocker_margin_C1": x["blocker_margin_C1"], "n_resid": x["n_resid"],
            "blocker_r": A[b]["r"], "blocker_v0": A[b]["v0"], "blocker_tau": A[b]["tau"],
            "blocker_lateral_offset": abs(pos[b][1] - DOOR[1]),
            "blocker_door_distance": float(np.linalg.norm(pos[b] - DOOR)),
            "t_deadlock": r["t_end"], "n_held_without_blocker": len(x["K2_held"]),
            "second_margin_C1": x["K1b"]["target_margin_C1"], "second_r": A[t]["r"],
            "second_held_alone": bool(x["K1b"]["held"]),
        })
    return rows


CONT = ("blocker_margin_C1", "n_resid", "blocker_r", "blocker_v0", "blocker_tau", "blocker_lateral_offset",
        "blocker_door_distance", "t_deadlock", "n_held_without_blocker", "second_margin_C1", "second_r", "seed")
BIN = ("second_held_alone",)


def smd(a, b):
    s = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    return float((np.mean(a) - np.mean(b)) / s) if s > 0 else 0.0


def balance(rows):
    d = np.array([r["drawn"] for r in rows])
    X = {k: np.array([float(r[k]) for r in rows]) for k in CONT + BIN}
    out, ps, names = {}, [], []
    for k in CONT:
        a, b = X[k][d], X[k][~d]
        mw = stats.mannwhitneyu(a, b, alternative="two-sided")
        ksr = stats.ks_2samp(a, b)
        out[k] = {"test": "Mann-Whitney", "median_drawn": revlib.sig(float(np.median(a)), 3),
                  "median_rest": revlib.sig(float(np.median(b)), 3), "mean_drawn": float(np.mean(a)),
                  "mean_rest": float(np.mean(b)), "smd": revlib.sig(smd(a, b), 2), "smd_raw": smd(a, b),
                  "p_mw": float(mw.pvalue), "p_mw_disp": revlib.pdisp(float(mw.pvalue)),
                  "p_ks": float(ksr.pvalue), "p_ks_disp": revlib.pdisp(float(ksr.pvalue))}
        ps.append(float(mw.pvalue)); names.append(k)
    for k in BIN:
        a, b = X[k][d].astype(int), X[k][~d].astype(int)
        tab = [[a.sum(), len(a) - a.sum()], [b.sum(), len(b) - b.sum()]]
        p = float(stats.fisher_exact(tab)[1])
        out[k] = {"test": "Fisher", "k_drawn": int(a.sum()), "n_drawn": len(a), "k_rest": int(b.sum()),
                  "n_rest": len(b), "smd": revlib.sig(smd(a, b), 2), "smd_raw": smd(a, b),
                  "p_fisher": p, "p_fisher_disp": revlib.pdisp(p)}
        ps.append(p); names.append(k)
    hol = revlib.holm(ps)
    for k, h in zip(names, hol):
        out[k]["p_holm"] = h
        out[k]["p_holm_disp"] = revlib.pdisp(h)
    # omnibus: max |SMD| against random 26-of-160 draws
    keys = list(CONT + BIN)
    M = np.column_stack([X[k] for k in keys])
    obs = max(abs(smd(M[d, j], M[~d, j])) for j in range(M.shape[1]))
    rng = np.random.Generator(np.random.PCG64(12345))
    n, m, B = len(rows), int(d.sum()), 20000
    null = np.empty(B)
    for i in range(B):
        z = np.zeros(n, bool)
        z[rng.choice(n, m, replace=False)] = True
        null[i] = max(abs(smd(M[z, j], M[~z, j])) for j in range(M.shape[1]))
    p_omni = float((1 + np.sum(null >= obs)) / (B + 1))
    p_min = min(ps)
    return {"n_drawn": m, "n_rest": n - m, "covariates": out,
            "min_p_raw": p_min, "min_p_raw_disp": revlib.pdisp(p_min), "min_p_raw_covariate": names[int(np.argmin(ps))],
            "min_p_holm": min(hol), "min_p_holm_disp": revlib.pdisp(min(hol)),
            "max_abs_smd": revlib.sig(obs, 2), "max_abs_smd_covariate": keys[int(np.argmax(
                [abs(smd(M[d, j], M[~d, j])) for j in range(M.shape[1])]))],
            "omnibus_p": p_omni, "omnibus_p_disp": revlib.pdisp(p_omni), "omnibus_draws": B,
            "n_tests": len(ps), "any_holm_below_0p05": bool(min(hol) < 0.05),
            "any_raw_below_0p05": [k for k, p in zip(names, ps) if p < 0.05]}


def cost(n_snap):
    sel = {s["tag"]: s for s in json.load(open(os.path.join(D, "selection.json")))["E2"]["snapshots"]}
    w = {}
    for r in jl(os.path.join(revlib.DATA, "E2", "e2_quench.jsonl")):
        tag = r["job_id"].split("|")[0]
        if sel.get(tag, {}).get("class") == CLS_B:
            w.setdefault(r["arm"], []).append(r["wall_s"])
    counts = {"noise0.07": 5, "C3_rvo2": 6, "drive_only": 1, "frozen_plus": 1}
    per = {a: float(np.mean(w[a])) for a in counts}
    per_snap = sum(per[a] * c for a, c in counts.items())
    full_arms = sum(float(np.mean(v)) * (6 if not a.startswith("noise") else 5) for a, v in w.items())
    out = {"arms_jobs_per_snapshot": counts, "jobs_per_snapshot": sum(counts.values()),
           "n_snapshots": n_snap, "n_jobs": n_snap * sum(counts.values()),
           "mean_wall_s_per_job_E2": {a: revlib.sig(v, 2) for a, v in per.items()},
           "per_snapshot_s": revlib.sig(per_snap, 2), "cpu_hours": revlib.sig(per_snap * n_snap / 3600, 2),
           "cpu_hours_4_workers_wall": revlib.sig(per_snap * n_snap / 3600 / 4, 2),
           "full_E2_arm_set_per_snapshot_s": revlib.sig(full_arms, 2),
           "full_E2_arm_set_cpu_hours": revlib.sig(full_arms * n_snap / 3600, 2),
           "source": "mean wall_s per arm over the 26 E2 second-trap snapshots (data/E2/e2_quench.jsonl)"}
    sm = os.path.join(revlib.DATA, "revision", "A5", "smoke_timing.json")
    if os.path.exists(sm):
        out["smoke"] = json.load(open(sm))
    return out


def main():
    f = funnel()
    rows = covariates()
    res = {"funnel": f, "bar_e3_e4": bar_e3_e4(), "pair": pair(), "balance": balance(rows),
           "cost": cost(f["second_trap_not_drawn"]),
           "covariate_rows": rows}
    print(revlib.out_json("A5", res))
    b = res["balance"]
    print("balance min raw p", b["min_p_raw_disp"], b["min_p_raw_covariate"], "min holm", b["min_p_holm_disp"],
          "max|SMD|", b["max_abs_smd"], b["max_abs_smd_covariate"], "omnibus", b["omnibus_p_disp"])
    for k, v in b["covariates"].items():
        print(f"  {k:26s} smd {v['smd']:>6} p {v.get('p_mw', v.get('p_fisher')):.3f} holm {v['p_holm']:.3f}")
    print(json.dumps({k: v for k, v in res.items() if k not in ("covariate_rows", "balance")}, indent=0, default=float)[:3000])


if __name__ == "__main__":
    main()
