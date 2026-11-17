"""Tasks 7, 8, 11: whole-run analyses (w = 0.8 m, 100 agents, 600 s; runlib.whole_run; seeds 242-427).

Originals (as rev4_T1): drive (C3 + drive_only) and tauprime (C1 + sfm_tau_prime) from data/revision4/T1/t1_whole.jsonl,
SFM = data/velorca/whole.jsonl (242-341) + revision4 T1 (342-427), force-coupled ORCA (RVO2) = data/E6/e6a.jsonl.
T7 replays (data/revision7/T7/t7_replay.jsonl): the same spawn with a 1e-9 m Gaussian displacement of every agent
  (perturb seed 900). Outcome change = completion differs from the original; also changes of t_end > 1e-6 s among runs
  with the same completion. Drive vs tauprime agreement in the replays against the originals' 151/186.
T8 drive_veff (data/revision7/T8/t8_whole.jsonl): C3 + drive_only with ORCA's preferred velocity v_eff e (the density
  throttle applied to the drive part's target). Completion k/n, Wilson 95%; exact McNemar against drive, tauprime and
  force-coupled ORCA on the same seeds (Holm over the three); failure classes at 600 s (keystone_q.py).
T11 R1, R2 (data/revision7/T11/t11_whole.jsonl), seeds 242-301 (or the completed prefix): completion, Wilson,
  McNemar vs SFM and force-coupled ORCA (Holm over four), failure classes.
Output: data/derived/rev7_whole.json"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import holm, mcnemar_exact, np, pdisp, wilson  # noqa: E402
import keystone_q as KQ  # noqa: E402

SEEDS = list(range(242, 428))
CL = ("lone_keystone", "lone_keystone_second_trap", "collective")


def by_seed(R):
    return {r["seed"]: r for r in R}


def originals():
    T = L.load_runs(os.path.join(L.DATA, "revision4", "T1", "t1_whole.jsonl"))
    vel = by_seed([r for r in L.load_runs(os.path.join(L.DATA, "velorca", "whole.jsonl")) if r["variant"] == "sfm"])
    ts = by_seed([r for r in T if r["variant"] == "sfm"])
    return {"drive": by_seed([r for r in T if r["variant"] == "drive"]),
            "tauprime": by_seed([r for r in T if r["variant"] == "tauprime"]),
            "sfm": {s: (vel[s] if s < 342 else ts[s]) for s in SEEDS},
            "rvo2": by_seed(L.load_runs(os.path.join(L.DATA, "E6", "e6a.jsonl")))}


def comp(arm, seeds):
    k = sum(bool(arm[s]["complete"]) for s in seeds)
    p, lo, hi = wilson(k, len(seeds))
    return {"k": k, "n": len(seeds), "frac": p, "ci95": [lo, hi],
            "at_rest": sum((not arm[s]["complete"]) and bool(arm[s]["deadlock"]) for s in seeds),
            "moving_600": sum((not arm[s]["complete"]) and not arm[s]["deadlock"] for s in seeds)}


def mc(a, b, seeds):
    x = sum(a[s]["complete"] and not b[s]["complete"] for s in seeds)
    y = sum(b[s]["complete"] and not a[s]["complete"] for s in seeds)
    p = mcnemar_exact(x, y)
    return {"first_only": x, "second_only": y, "p": p, "p_disp": pdisp(p)}


def classes(arm, seeds, cls):
    rows = [{"seed": s, "rest": bool(arm[s]["deadlock"]), "class": cls.get(arm[s]["job_id"]), "n_res": arm[s]["n_remaining"]}
            for s in seeds if not arm[s]["complete"]]
    return {"n_fail": len(rows), "classified": sum(r["class"] is not None for r in rows),
            "at_rest": {k: sum(r["rest"] and r["class"] == k for r in rows) for k in CL},
            "moving": {k: sum((not r["rest"]) and r["class"] == k for r in rows) for k in CL},
            "unclassified": sum(r["class"] is None for r in rows), "rows": rows}


def main():
    O = originals()
    out = {"doc": __doc__}
    p7 = os.path.join(L.data_dir("T7"), "t7_replay.jsonl")
    R7 = list(L.load_ok(p7).values()) if os.path.exists(p7) else []
    T7 = {}
    rep = {}
    for a in ("drive", "tauprime", "rvo2", "sfm"):
        rp = by_seed([r for r in R7 if r["job_id"].startswith(a + "|")])
        rep[a] = rp
        S = sorted(rp)
        ch = [s for s in S if bool(rp[s]["complete"]) != bool(O[a][s]["complete"])]
        tch = [s for s in S if s not in ch and abs(rp[s]["t_end"] - O[a][s]["t_end"]) > 1e-6]
        T7[a] = {"n": len(S), "outcome_changes": len(ch), "changed_seeds": ch,
                 "changes_to_complete": sum(bool(rp[s]["complete"]) for s in ch), "t_end_changes_same_outcome": len(tch),
                 "orig_k": sum(bool(O[a][s]["complete"]) for s in S), "replay_k": sum(bool(rp[s]["complete"]) for s in S),
                 "wilson95_change": list(wilson(len(ch), len(S))[1:]) if S else None}
    both = sorted(set(rep["drive"]) & set(rep["tauprime"]))
    T7["drive_vs_tauprime"] = {"n": len(both),
                               "replay_agree": sum(bool(rep["drive"][s]["complete"]) == bool(rep["tauprime"][s]["complete"]) for s in both),
                               "orig_agree_same_seeds": sum(bool(O["drive"][s]["complete"]) == bool(O["tauprime"][s]["complete"]) for s in both),
                               "orig_agree_186": sum(bool(O["drive"][s]["complete"]) == bool(O["tauprime"][s]["complete"]) for s in SEEDS)}
    out["T7"] = T7
    print("T7", {k: {a: b for a, b in v.items() if a != "changed_seeds"} for k, v in T7.items()})
    cls = KQ.classify(KQ.failures())
    p8 = os.path.join(L.data_dir("T8"), "t8_whole.jsonl")
    if os.path.exists(p8):
        V = by_seed(L.load_ok(p8).values())
        S = sorted(V)
        t = {f"veff_vs_{b}": mc(V, O[b], S) for b in ("drive", "tauprime", "rvo2")}
        for (k, v), q in zip(t.items(), holm([v["p"] for v in t.values()])):
            v["p_holm"] = q
        out["T8"] = {"seeds": [S[0], S[-1]] if S else None, "completion": comp(V, S),
                     "ref": {b: comp(O[b], S) for b in ("drive", "tauprime", "rvo2", "sfm")}, "tests": t,
                     "classes": classes(V, S, cls)}
        print("T8", out["T8"]["completion"], {k: (v["first_only"], v["second_only"], v["p_disp"]) for k, v in t.items()})
    p11 = os.path.join(L.data_dir("T11"), "t11_whole.jsonl")
    if os.path.exists(p11):
        R = list(L.load_ok(p11).values())
        A = {a: by_seed([r for r in R if r["job_id"].startswith(a + "|")]) for a in ("R1", "R2")}
        S = sorted(set(A["R1"]) & set(A["R2"]))
        t = {f"{a}_vs_{b}": mc(A[a], O[b], S) for a in ("R1", "R2") for b in ("sfm", "rvo2")}
        for (k, v), q in zip(t.items(), holm([v["p"] for v in t.values()])):
            v["p_holm"] = q
        t["R1_vs_R2"] = mc(A["R1"], A["R2"], S)
        out["T11"] = {"n_seeds": len(S), "seeds": [S[0], S[-1]] if S else None,
                      "completion": {a: comp(A[a], S) for a in A}, "ref": {b: comp(O[b], S) for b in ("sfm", "rvo2", "drive", "tauprime")},
                      "tests": t, "classes": {a: classes(A[a], S, cls) for a in A},
                      "identical_R1_R2_t_end": sum(abs(A["R1"][s]["t_end"] - A["R2"][s]["t_end"]) < 1e-9 for s in S)}
        print("T11", out["T11"]["completion"], out["T11"]["ref"]["sfm"], {k: (v["first_only"], v["second_only"], v["p_disp"]) for k, v in t.items()})
    print(L.out_json("whole", out))


if __name__ == "__main__":
    main()
