"""Task 1 analysis: the 46 pair standoffs run to rest (600 s horizon).

Outcome of a run at 600 s: freed (a member crosses the door plane; first exit time t_free), at rest (E7b stopping
rule: every agent |v| < 1e-3 m/s for 10 s, without exit) or still moving at 600 s. Sources: the original 120 s runs
(data/E7b/e7b_quench.jsonl, data/E7b_bstar/bstar_quench.jsonl); a run that ended freed or at rest within 120 s keeps
its outcome (deterministic dynamics). Runs still moving at 120 s were rerun from the snapshot to 600 s
(data/revision7/T1/t1_pair_rest.jsonl, queue_q12 T1); check: no rerun frees or stops before 120 s.
Arms: legacy ORCA (C3_pub), RVO2 ORCA (C3_rvo2), constraint part (constraint_only_pub/_rvo2), drive part
(drive_only), lateral bias at the matched b* (+ and - handedness, both solvers).
Tests: exact McNemar (two-sided binomial on discordant pairs) on the unperturbed runs at 120 s and at 600 s.
Replays (perturb 900-904) are summarised where every replay of the arm is available.
Output: data/derived/rev7_T1.json"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import np  # noqa: E402
from scipy import stats  # noqa: E402

ARMS = ("C3_pub", "C3_rvo2", "constraint_only_pub", "constraint_only_rvo2", "drive_only", "bstar_pub+", "bstar_pub-",
        "bstar_rvo2+", "bstar_rvo2-", "C1")
EXT = os.path.join(L.data_dir("T1"), "t1_pair_rest.jsonl")


def outcome(r):
    if r["freed"]:
        return "freed"
    return "rest" if r["stationary_stop"] else "moving"


def mcnemar(a, b):
    ab = sum(x and not y for x, y in zip(a, b))
    ba = sum(y and not x for x, y in zip(a, b))
    p = float(stats.binomtest(ab, ab + ba, 0.5).pvalue) if ab + ba else 1.0
    return {"a_only": ab, "b_only": ba, "p": p}


def main():
    orig = {}
    for p in (os.path.join(L.DATA, "E7b", "e7b_quench.jsonl"), os.path.join(L.DATA, "E7b_bstar", "bstar_quench.jsonl")):
        for r in L.load_runs(p):
            if r["arm"] in ARMS:
                orig[r["job_id"]] = r
    ext = L.load_ok(EXT)
    bad = [k for k, r in ext.items() if (r["freed"] and r["first_t"] <= 120.0) or (r["stationary_stop"] and r["t_run"] < 120.0)]
    need = {k for k, r in orig.items() if outcome(r) == "moving" and r["arm"] in ARMS[:4]}
    tags = sorted({k.split("|")[0] for k in orig})
    out = {"doc": __doc__, "n_snapshots": len(tags), "ext_runs": len(ext), "ext_needed": len(need),
           "ext_missing": sorted(need - set(ext)), "check_rerun_changed_before_120s": bad, "arms": {}}
    final = {}
    for arm in ARMS:
        res = defaultdict(dict)
        complete = {"u": True, "rep": True}
        for t in tags:
            for ps in ("u", "900", "901", "902", "903", "904"):
                k = f"{t}|{arm}|{ps}"
                if k not in orig:
                    continue
                r0 = orig[k]
                o120 = outcome(r0)
                if o120 == "moving" and arm in ARMS[:4]:
                    if k in ext:
                        r1, ofin = ext[k], outcome(ext[k])
                    else:
                        r1, ofin = None, None
                        complete["u" if ps == "u" else "rep"] = False
                else:
                    r1, ofin = r0, o120
                res[ps][t] = {"o120": o120, "ofin": ofin, "t_free": r1["first_t"] if r1 is not None and ofin == "freed" else None,
                              "t_end": r1["t_run"] if r1 is not None else None}
        U = res["u"]
        A = {"n": len(U), "unperturbed_complete": complete["u"],
             "freed_120": sum(v["o120"] == "freed" for v in U.values()),
             "rest_120": sum(v["o120"] == "rest" for v in U.values()),
             "moving_120": sum(v["o120"] == "moving" for v in U.values())}
        if complete["u"]:
            tf = [v["t_free"] for v in U.values() if v["ofin"] == "freed"]
            A.update({"freed_end": sum(v["ofin"] == "freed" for v in U.values()),
                      "rest_end": sum(v["ofin"] == "rest" for v in U.values()),
                      "moving_600": sum(v["ofin"] == "moving" for v in U.values()),
                      "freed_after_120": sorted((t, v["t_free"]) for t, v in U.items() if v["ofin"] == "freed" and v["o120"] != "freed"),
                      "t_free_median": float(np.median(tf)) if tf else None, "t_free_max": max(tf) if tf else None,
                      "t_rest_max_held": max((v["t_end"] for v in U.values() if v["ofin"] == "rest"), default=None),
                      "wilson95_end": L.wilson(sum(v["ofin"] == "freed" for v in U.values()), len(U))})
            final[arm] = {t: U[t]["ofin"] == "freed" for t in tags}
        R = [res[p] for p in ("900", "901", "902", "903", "904") if res[p]]
        if R:
            A["replays_n"] = sum(len(x) for x in R)
            A["replays_complete"] = complete["rep"]
            A["replays_freed_120"] = sum(v["o120"] == "freed" for x in R for v in x.values())
            if complete["rep"]:
                A["replays_freed_end"] = sum(v["ofin"] == "freed" for x in R for v in x.values())
                A["replays_moving_600"] = sum(v["ofin"] == "moving" for x in R for v in x.values())
                A["replay_discordant_snapshots_end"] = sum(
                    len({x[t]["ofin"] for x in R} | {U[t]["ofin"]}) > 1 for t in tags) if complete["u"] else None
        out["arms"][arm] = A
        print(arm, {k: v for k, v in A.items() if k not in ("freed_after_120",)})
    o120 = {a: {t: orig[f"{t}|{a}|u"]["freed"] for t in tags} for a in ARMS}
    T = {}
    for nm, a, b in (("legacy_vs_rvo2", "C3_pub", "C3_rvo2"), ("drive_vs_rvo2", "drive_only", "C3_rvo2"),
                     ("drive_vs_legacy", "drive_only", "C3_pub"), ("bstar_rvo2_vs_rvo2", "bstar_rvo2+", "C3_rvo2"),
                     ("bstar_pub_vs_legacy", "bstar_pub+", "C3_pub"), ("constraint_rvo2_vs_rvo2", "constraint_only_rvo2", "C3_rvo2")):
        T[nm] = {"at_120": mcnemar([o120[a][t] for t in tags], [o120[b][t] for t in tags])}
        if a in final and b in final:
            T[nm]["at_end"] = mcnemar([final[a][t] for t in tags], [final[b][t] for t in tags])
            T[nm]["freed_end"] = [sum(final[a].values()), sum(final[b].values())]
        T[nm]["freed_120"] = [sum(o120[a].values()), sum(o120[b].values())]
        print(nm, T[nm])
    out["tests"] = T
    print(L.out_json("T1", out))


if __name__ == "__main__":
    main()
