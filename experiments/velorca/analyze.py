"""Velocity-coupled ORCA: analysis of data/velorca/*.jsonl -> data/derived/velorca_analysis.json.

lone, pair   freed fraction per solver (lone: blocker freed within 120 s; pair: any member out), Wilson
             95% intervals, per stratum (lone); paired by run (snapshot x replay seed) against force-coupled
             ORCA with the same solver (E2 and E7b records C3_rvo2 / C3_pub) and against
             SFM (records C1): discordant counts, exact McNemar p, Newcombe paired 95% interval of the
             difference; replay agreement (snapshots whose 6 runs disagree on the outcome); identity with
             the SFM restart (same exits, run length and final positions, bit for bit).
whole        completion k/100 with Wilson intervals for velocity coupling (vel), force-coupled ORCA (E6a,
             seeds 242-341) and SFM (sfm); paired differences (Newcombe, McNemar); completion time (Kaplan-
             Meier median, failures censored at 600 s; medians over completed runs; paired times on seeds
             both complete, Wilcoxon signed-rank); how failures end (deadlock, or still moving at 600 s) and
             the keystone class of the final state (data/velorca/keystone.jsonl; E6a: data/E6/keystone.jsonl);
             K0 (SFM holds the rebuilt residual), K0v (velocity coupling holds it).
verdict      the prediction of experiments/velorca/PREDICTION.md, item by item, and the Table 2 class.
"""
import importlib.util
import json
import math
import os
import sys
from collections import Counter

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "velorca_analysis.json")
sys.path.insert(0, os.path.join(ROOT, "experiments", "E3"))
from survival import km  # noqa: E402

_spec = importlib.util.spec_from_file_location("e6an", os.path.join(ROOT, "experiments", "E6", "analyze.py"))
e6an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e6an)
wilson, newcombe, mcnemar, classify = e6an.wilson, e6an.newcombe_paired, e6an.mcnemar_exact, e6an.classify
Z95 = 1.959963984540054
T_MAX = 600.0
SEEDS = range(242, 342)
PERTURBATIONS = ("vel_rvo2", "vel_pub")
FORCE = {"vel_rvo2": "C3_rvo2", "vel_pub": "C3_pub"}


def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def rate(k, n):
    lo, hi = wilson(k, n) if n else (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else lo
    return {"k": k, "n": n, "rate": k / n if n else float("nan"), "ci95": [lo, hi]}


def paired(a, b):
    """a, b: dicts key -> bool on the same keys. Difference p_a - p_b."""
    keys = sorted(set(a) & set(b))
    t = Counter((a[k], b[k]) for k in keys)
    both, only_a, only_b, neither = t[(True, True)], t[(True, False)], t[(False, True)], t[(False, False)]
    n = len(keys)
    if n == 0:
        return {"n": 0}
    d, lo, hi = newcombe(both, only_a, only_b, neither, Z95)
    return {"n": n, "both": both, "only_first": only_a, "only_second": only_b, "neither": neither,
            "diff": d, "ci95": [lo, hi], "mcnemar_p": mcnemar(only_a, only_b)}


def same_run(r, s, ids):
    """Bitwise identity of two quench records: exits, run length, final positions."""
    return (r["exits"] == s["exits"] and r["t_run"] == s["t_run"]
            and all(r["final_pos"].get(str(i)) == s["final_pos"].get(str(i)) for i in ids))


def quench_part(V, REF, outcome, ids_key, strata=None):
    """V: velorca records; REF: source experiment records (C1, C3_rvo2, C3_pub)."""
    ref = {r["job_id"]: r for r in REF}
    res = {}
    for pert in PERTURBATIONS:
        R = [r for r in V if r["perturbation"] == pert]
        o = {f"{r['job_id'].split('|')[0]}|{r['job_id'].split('|')[2]}": outcome(r) for r in R}
        rec = {f"{r['job_id'].split('|')[0]}|{r['job_id'].split('|')[2]}": r for r in R}
        e = {"all": rate(sum(o.values()), len(o))}
        if strata:
            for s in sorted(set(strata.values())):
                ks = [k for k in o if strata[k.split("|")[0]] == s]
                e[s] = rate(sum(o[k] for k in ks), len(ks))
        by_snap = {}
        for k, v in o.items():
            by_snap.setdefault(k.split("|")[0], set()).add(v)
        e["replay"] = {"n_snapshots": len(by_snap), "snapshots_disagree": sum(len(v) > 1 for v in by_snap.values()),
                       "runs_per_snapshot": len(o) / max(1, len(by_snap))}
        cmp = {}
        for name, src in (("force", FORCE[pert]), ("sfm", "C1")):
            other = {}
            for k in o:
                tag, rep = k.split("|")
                x = ref.get(f"{tag}|{src}|{rep}")
                if x is not None:
                    other[k] = outcome(x)
            cmp[name] = paired(o, other)
            cmp[name]["reference_arm"] = src
            cmp[name]["reference"] = rate(sum(other.values()), len(other))
        e["paired"] = cmp
        ident = [same_run(rec[k], ref[f"{k.split('|')[0]}|C1|{k.split('|')[1]}"], rec[k][ids_key])
                 for k in rec if f"{k.split('|')[0]}|C1|{k.split('|')[1]}" in ref]
        e["identical_to_sfm"] = {"n": len(ident), "identical": int(sum(ident))}
        e["stationary_stop"] = sum(bool(r["stationary_stop"]) for r in R)
        res[pert] = e
    return res


def km_med(R):
    t = [r["evacuation_time"] if r["complete"] else T_MAX for r in R]
    k = km(t, [bool(r["complete"]) for r in R], T_MAX)
    k.pop("curve", None)
    return k


def end_state(R, KS, variant):
    res = {x["job_id"]: x for x in KS}
    fails = [r for r in R if not r["complete"]]
    cls = Counter()
    k0 = k0v = k0n = k0vn = 0
    for r in fails:
        tag = f"{variant}|seed{r['seed']}"
        c = classify(res, tag)
        cls[c or "missing"] += 1
        if tag + "|K0" in res:
            k0n += 1
            k0 += int(len(res[tag + "|K0"]["held"]) == len(res[tag + "|K0"]["kept"]))
        for t in ("|K0v", "|K0c"):
            if tag + t in res:
                k0vn += 1
                k0v += int(len(res[tag + t]["held"]) == len(res[tag + t]["kept"]))
    return {"failures": len(fails), "deadlock": sum(bool(r["deadlock"]) for r in fails),
            "moving_at_600s": sum(bool(r["capped"]) for r in fails),
            "residual_size_median": float(np.median([r["n_remaining"] for r in fails])) if fails else None,
            "keystone_class": dict(cls), "K0_all_held": k0, "K0_n": k0n,
            "own_coupling_all_held": k0v, "own_coupling_n": k0vn}


def whole_part():
    W = jl(os.path.join(DATA, "velorca", "whole.jsonl"))
    E6a = [r for r in jl(os.path.join(DATA, "E6", "e6a.jsonl")) if r["seed"] in SEEDS]
    KSv = jl(os.path.join(DATA, "velorca", "keystone.jsonl")) if os.path.exists(
        os.path.join(DATA, "velorca", "keystone.jsonl")) else []
    KS6 = jl(os.path.join(DATA, "E6", "keystone.jsonl"))
    runs = {"vel": [r for r in W if r["variant"] == "vel"], "force": E6a, "sfm": [r for r in W if r["variant"] == "sfm"]}
    comp = {v: {r["seed"]: bool(r["complete"]) for r in R} for v, R in runs.items()}
    out = {"completion": {v: rate(sum(c.values()), len(c)) for v, c in comp.items()},
           "paired": {"vel_minus_force": paired(comp["vel"], comp["force"]),
                      "vel_minus_sfm": paired(comp["vel"], comp["sfm"]),
                      "force_minus_sfm": paired(comp["force"], comp["sfm"])},
           "time": {}, "end_state": {}}
    fset = {v: {s for s, c in comp[v].items() if not c} for v in comp}
    out["failure_jaccard"] = {"vel_force": e6an.jaccard(fset["vel"], fset["force"]),
                              "vel_sfm": e6an.jaccard(fset["vel"], fset["sfm"])}
    for v, R in runs.items():
        if not R:
            continue
        ct = [r["evacuation_time"] for r in R if r["complete"]]
        out["time"][v] = {"km": km_med(R), "completed_median": float(np.median(ct)) if ct else None,
                          "completed_iqr": [float(np.percentile(ct, 25)), float(np.percentile(ct, 75))] if ct else None}
    tv = {r["seed"]: r["evacuation_time"] for r in runs["vel"] if r["complete"]}
    for other in ("force", "sfm"):
        to = {r["seed"]: r["evacuation_time"] for r in runs[other] if r["complete"]}
        both = sorted(set(tv) & set(to))
        if len(both) >= 5:
            d = np.array([tv[s] - to[s] for s in both])
            out["time"][f"paired_vel_minus_{other}"] = {"n": len(both), "median_diff": float(np.median(d)),
                                                        "frac_vel_faster": float(np.mean(d < 0)),
                                                        "wilcoxon_p": float(stats.wilcoxon(d).pvalue) if np.any(d) else 1.0}
    out["end_state"]["vel"] = end_state(runs["vel"], KSv, "vel")
    out["end_state"]["sfm"] = end_state(runs["sfm"], KSv, "sfm")
    out["end_state"]["force"] = end_state(runs["force"], KS6, "E6a")
    return out


def main():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))["E2"]["snapshots"]
    strata = {s["tag"]: s["class"] for s in sel}
    E2 = [r for r in jl(os.path.join(DATA, "E2", "e2_quench.jsonl")) if r["arm"] in ("C1", "C3_rvo2", "C3_pub")]
    E7 = [r for r in jl(os.path.join(DATA, "E7b", "e7b_quench.jsonl")) if r["arm"] in ("C1", "C3_rvo2", "C3_pub")]
    VL = jl(os.path.join(DATA, "velorca", "lone.jsonl"))
    VP = jl(os.path.join(DATA, "velorca", "pair.jsonl"))
    blocker = {s["tag"]: s["blocker"] for s in sel}

    def lone_out(r):  # blocker freed within 120 s; blocker from selection.json (older E2 rows carry none)
        t = r["exits"].get(str(blocker[r["job_id"].split("|")[0]]))
        return t is not None and t <= 120.0 + 1e-9
    o = {"script": "experiments/velorca/analyze.py", "prediction": "experiments/velorca/PREDICTION.md",
         "lone": quench_part(VL, E2, lone_out, "residual", strata),
         "pair": quench_part(VP, E7, lambda r: bool(r["freed"]), "members"),
         "whole": whole_part()}
    dtp = os.path.join(DATA, "velorca", "dtprobe.jsonl")
    o["dtprobe"] = {"runs": len(jl(dtp)) if os.path.exists(dtp) else 0}
    q_freed = sum(o[p][a]["all"]["k"] for p in ("lone", "pair") for a in PERTURBATIONS)
    q_ident = all(o[p][a]["identical_to_sfm"]["identical"] == o[p][a]["identical_to_sfm"]["n"]
                  for p in ("lone", "pair") for a in PERTURBATIONS)
    ev = o["whole"]["end_state"]["vel"]
    d = o["whole"]["paired"]["vel_minus_sfm"]
    o["verdict"] = {
        "quench_freed_total": q_freed,
        "quench_identical_to_sfm": q_ident,
        "replay_disagree_total": sum(o[p][a]["replay"]["snapshots_disagree"] for p in ("lone", "pair") for a in PERTURBATIONS),
        "whole_final_states_held_by_own_coupling": ev["own_coupling_all_held"] == ev["own_coupling_n"],
        "whole_final_states_held_by_sfm": ev["K0_all_held"] == ev["K0_n"],
        "whole_moving_at_600s": ev["moving_at_600s"],
        "whole_differs_from_sfm": d["ci95"][0] > 0 or d["ci95"][1] < 0,
    }
    v = o["verdict"]
    v["prediction_held"] = bool(q_freed == 0 and q_ident and v["whole_final_states_held_by_own_coupling"]
                                and v["whole_final_states_held_by_sfm"] and v["whole_moving_at_600s"] == 0)
    v["table2_class"] = ("P" if v["prediction_held"] else "not P: see the failing items")
    v["table2_class_note"] = ("held under quench and every replay; whole-run completion "
                              + ("differs" if v["whole_differs_from_sfm"] else "does not differ detectably")
                              + " from SFM at the same seeds")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(o, open(OUT, "w"), indent=1, default=float)
    return o


def brief(o):
    for p in ("lone", "pair"):
        for a in PERTURBATIONS:
            e = o[p][a]
            print(p, a, e["all"], "replay", e["replay"], "ident", e["identical_to_sfm"])
            for n, c in e["paired"].items():
                print("   vs", n, {k: c.get(k) for k in ("n", "diff", "ci95", "mcnemar_p")}, c["reference"])
    w = o["whole"]
    print("completion", w["completion"])
    for k, c in w["paired"].items():
        print(" ", k, {x: c.get(x) for x in ("diff", "ci95", "mcnemar_p", "only_first", "only_second")})
    print("time", json.dumps(w["time"], default=float))
    print("end", json.dumps(w["end_state"]))
    print("verdict", o["verdict"])


if __name__ == "__main__":
    brief(main())
