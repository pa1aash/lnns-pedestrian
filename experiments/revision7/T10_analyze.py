"""Task 10 analysis: R1 / R2 quenches against the pre-registered prediction (notes/C5_items/prereg_replace.md,
data/derived/rev7_T9_prereg.json, committed in 2ac5353 before any R run).

Outcome: blocker freed within 120 s (blocker_freed) in the unperturbed run; replays (perturb 900-904) compared with it.
Confusion matrix (predicted freed / held x observed freed / held) per stratum: 34 lone keystones, 26 screening second
traps, 134 other second traps. Each disagreement is listed with its static margin, its constraint-part data (lp_rest)
and the run's first exit (agent, time) and blocker exit time, to trace it to exception 1 (constraint part in motion) or
2 (pushes from behind). Comparison arms on the same snapshots (unperturbed, 120 s): SFM (C1), force-coupled ORCA
(C3_rvo2), drive part (drive_only), from data/E2/e2_quench.jsonl and data/revision/A5/a5_quench.jsonl; the tau' SFM
(sfm_tau_tau) from data/revision/A1/a1_quench.jsonl (screening set only). Exact McNemar R1 vs each arm per stratum.
Pairs (46): freed by 600 s / at rest / still moving, unperturbed and replays (no prediction was made).
Output: data/derived/rev7_T10.json"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import mcnemar_exact, pdisp  # noqa: E402

Q = os.path.join(L.data_dir("T10"), "t10_quench.jsonl")
P = os.path.join(L.data_dir("T10"), "t10_pair.jsonl")


def freed(r):
    return bool(r.get("blocker_freed"))


def main():
    pre = json.load(open(os.path.join(L.DERIVED, "rev7_T9_prereg.json")))
    pred = {x["tag"]: (x["class"], x["pred_freed"]["R1"], x) for x in pre["rows"]}
    for o in pre["other134"]:
        pred[o["tag"]] = ("other_second_trap", o["pred_freed"], o)
    R = L.load_ok(Q)
    ref = {}
    for p in (os.path.join(L.DATA, "E2", "e2_quench.jsonl"), os.path.join(L.DATA, "revision", "A5", "a5_quench.jsonl")):
        for r in L.load_runs(p):
            t = r["job_id"].split("|")[0]
            if r.get("perturb") is None and r["arm"] in ("C1", "C3_rvo2", "drive_only") and t in pred:
                e = r["exits"].get(str(pred[t][2]["blocker"]))
                ref[(t, r["arm"])] = e is not None and e <= 120.0 + 1e-9
    for r in L.load_runs(os.path.join(L.DATA, "revision", "A1", "a1_quench.jsonl")):
        if r["job_id"].split("|")[1] == "sfm_tau_tau" and r.get("perturb") is None:
            e = r["exits"].get(str(r["blocker"]))
            ref[(r["job_id"].split("|")[0], "tauprime")] = e is not None and e <= 120.0 + 1e-9
    out = {"doc": __doc__, "strata": {}}
    for st in ("lone_keystone", "lone_keystone_second_trap", "other_second_trap"):
        tags = [t for t, v in pred.items() if v[0] == st]
        S = {"n": len(tags)}
        for arm in ("R1", "R2"):
            done = [t for t in tags if f"{t}|{arm}|u" in R]
            cm = {"pred_freed_obs_freed": 0, "pred_freed_obs_held": 0, "pred_held_obs_freed": 0, "pred_held_obs_held": 0}
            dis, rep_disc = [], []
            for t in done:
                r = R[f"{t}|{arm}|u"]
                o, pf = freed(r), pred[t][1]
                cm[f"pred_{'freed' if pf else 'held'}_obs_{'freed' if o else 'held'}"] += 1
                if o != pf:
                    x = pred[t][2]
                    dis.append({"tag": t, "pred_freed": pf, "obs_freed": o, "margin_R": x["margin"]["R1"] if "margin" in x else x["margin_R"],
                                "margin_SFM": x["margin"]["SFM"] if "margin" in x else x["margin_SFM"],
                                "lp_rest": x.get("lp_rest", {}).get("R1"), "blocker_exit_t": r.get("blocker_exit_t"),
                                "first_agent": r["first_agent"], "first_t": r["first_t"], "blocker": r["blocker"],
                                "n_resid": len(r["residual"]), "exits": r["exits"], "stationary_stop": r["stationary_stop"],
                                "t_run": r["t_run"]})
                reps = [R.get(f"{t}|{arm}|{p}") for p in L.PERTURB_SEEDS]
                reps = [x for x in reps if x is not None]
                if reps and any(freed(x) != o for x in reps):
                    rep_disc.append({"tag": t, "u": o, "replays": [freed(x) for x in reps]})
            k = sum(freed(R[f"{t}|{arm}|u"]) for t in done)
            A = {"n_done": len(done), "freed": k, "freed_wilson95": list(L.wilson(k, len(done))[1:]) if done else None,
                 "confusion": cm, "disagreements": dis, "n_disagree": len(dis),
                 "replays_done": sum(f"{t}|{arm}|{p}" in R for t in tags for p in L.PERTURB_SEEDS),
                 "replay_discordant_snapshots": rep_disc, "vs": {}}
            for b in ("C1", "C3_rvo2", "drive_only", "tauprime"):
                tt = [t for t in done if (t, b) in ref]
                if not tt:
                    continue
                x = sum(freed(R[f"{t}|{arm}|u"]) and not ref[(t, b)] for t in tt)
                y = sum(ref[(t, b)] and not freed(R[f"{t}|{arm}|u"]) for t in tt)
                pv = mcnemar_exact(x, y)
                A["vs"][b] = {"n": len(tt), "arm_freed": sum(ref[(t, b)] for t in tt), "R_only": x, "arm_only": y, "p": pv,
                              "p_disp": pdisp(pv)}
            S[arm] = A
        done = [t for t in tags if f"{t}|R1|u" in R and f"{t}|R2|u" in R]
        S["R1_R2_identical_outcome"] = sum(freed(R[f"{t}|R1|u"]) == freed(R[f"{t}|R2|u"]) for t in done)
        S["R1_R2_identical_t_run"] = sum(abs(R[f"{t}|R1|u"]["t_run"] - R[f"{t}|R2|u"]["t_run"]) < 1e-9 for t in done)
        out["strata"][st] = S
        print(st, {a: (S[a]["n_done"], S[a]["freed"], S[a]["confusion"], S[a]["n_disagree"], len(S[a]["replay_discordant_snapshots"]),
                       {b: (v["arm_freed"], v["R_only"], v["arm_only"], v["p_disp"]) for b, v in S[a]["vs"].items()}) for a in ("R1", "R2")})
    if os.path.exists(P):
        PR = list(L.load_ok(P).values())
        pa = {}
        for arm in ("R1", "R2"):
            for kind, sel in (("u", lambda r: r["perturb"] is None), ("rep", lambda r: r["perturb"] is not None)):
                rr = [r for r in PR if r["arm"] == arm and sel(r)]
                pa[f"{arm}_{kind}"] = {"n": len(rr), "freed": sum(r["freed"] for r in rr),
                                       "rest": sum((not r["freed"]) and r["stationary_stop"] for r in rr),
                                       "moving_600": sum((not r["freed"]) and not r["stationary_stop"] for r in rr),
                                       "freed_by_120": sum(r["freed"] and r["first_t"] <= 120 for r in rr)}
        out["pairs"] = pa
        print("pairs", pa)
    print(L.out_json("T10", out))


if __name__ == "__main__":
    main()
