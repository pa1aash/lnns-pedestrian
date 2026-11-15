"""T1 analysis: whole-run attribution of force-coupled ORCA's completions to its drive part.

Inputs (read only)
  data/revision4/T1/t1_whole.jsonl     drive (C3 + drive_only), tauprime (C1 + sfm_tau_prime), sfm seeds 342-427
                                       and 242-246 (reproduction check); experiments/revision4/T1_whole.py
  data/revision4/T1/t1_keystone.jsonl  keystone tests on the rebuilt final states (T1_keystone.py)
  data/velorca/whole.jsonl             SFM (variant sfm), seeds 242-341, same recorder and flags
  data/E6/e6a.jsonl, data/E6/keystone.jsonl   force-coupled ORCA (RVO2), seeds 242-427, and its final-state classes
Sets: 186 spawns (run seeds 242-427) per arm; SFM = velorca 242-341 + T1 342-427 (T1's reruns of 242-246 must equal
the velorca records: completion, t_end, exit times).
Statistics: completion k/186 with Wilson 95% intervals; paired exact two-sided McNemar tests on the same spawns
(drive vs force-coupled ORCA, tauprime vs force-coupled ORCA, drive vs SFM, tauprime vs SFM; Holm over these four);
agreement of drive and tauprime run by run (same outcome, discordant counts and McNemar p, and among runs both
complete the evacuation-time difference). Failure classes at 600 s (classify of experiments/E6/analyze.py: K1 freed
-> collective (group standoff); K1 held and K2 all exit -> lone keystone; K1 held and K2 leaves agents -> second
trap), split by whether the run was at rest at the end (deadlock stop) or still moving at 600 s; class tables
against force-coupled ORCA's by the chi-square permutation test of E6 (perm_table_test, 10 000 permutations), and
at rest / still moving against force-coupled ORCA by Fisher's exact test (two-sided).
Output: data/derived/rev4_T1.json.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import DATA, ROOT, holm, load_runs, mcnemar_exact, np, pdisp, wilson  # noqa: E402

SEEDS = list(range(242, 428))
CL = ("lone_keystone", "lone_keystone_second_trap", "collective")
_spec = importlib.util.spec_from_file_location("e6_analyze", os.path.join(ROOT, "experiments", "E6", "analyze.py"))
E6A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E6A)


def by_seed(R):
    return {r["seed"]: r for r in R}


def main():
    T = load_runs(os.path.join(DATA, "revision4", "T1", "t1_whole.jsonl"))
    KS = {x["job_id"]: x for x in load_runs(os.path.join(DATA, "revision4", "T1", "t1_keystone.jsonl"))}
    KE6 = {x["job_id"]: x for x in load_runs(os.path.join(DATA, "E6", "keystone.jsonl"))}
    vel = by_seed([r for r in load_runs(os.path.join(DATA, "velorca", "whole.jsonl")) if r["variant"] == "sfm"])
    tsfm = by_seed([r for r in T if r["variant"] == "sfm"])
    repro = []
    for s in range(242, 247):
        a, b = tsfm[s], vel[s]
        same = (a["complete"] == b["complete"] and abs(a["t_end"] - b["t_end"]) < 1e-9 and a["exit_t"] == b["exit_t"])
        repro.append({"seed": s, "identical": bool(same)})
    arms = {"drive": by_seed([r for r in T if r["variant"] == "drive"]),
            "tauprime": by_seed([r for r in T if r["variant"] == "tauprime"]),
            "sfm": {s: (vel[s] if s < 342 else tsfm[s]) for s in SEEDS},
            "orca_rvo2": by_seed(load_runs(os.path.join(DATA, "E6", "e6a.jsonl")))}
    for a, d in arms.items():
        assert sorted(d) == SEEDS or a != "orca_rvo2" or set(SEEDS) <= set(d), a
        assert all(s in d for s in SEEDS), (a, len(d))
    c = {a: np.array([bool(arms[a][s]["complete"]) for s in SEEDS]) for a in arms}
    out = {"script": "experiments/revision4/T1_analyze.py", "doc": __doc__, "n": len(SEEDS), "reproduction_sfm": repro,
           "completion": {}, "tests": {}, "agreement_drive_tauprime": {}, "failure": {}}
    for a in arms:
        k = int(c[a].sum())
        p, lo, hi = wilson(k, len(SEEDS))
        out["completion"][a] = {"k": k, "n": len(SEEDS), "frac": p, "ci95": [lo, hi],
                                "deadlock": int(sum(bool(arms[a][s]["deadlock"]) for s in SEEDS)),
                                "capped": int(sum((not arms[a][s]["complete"]) and not arms[a][s]["deadlock"] for s in SEEDS))}
    pairs = [("drive", "orca_rvo2"), ("tauprime", "orca_rvo2"), ("drive", "sfm"), ("tauprime", "sfm")]
    for a, b in pairs:
        b1, c1 = int((c[a] & ~c[b]).sum()), int((c[b] & ~c[a]).sum())
        p = mcnemar_exact(b1, c1)
        out["tests"][f"{a}_vs_{b}"] = {"disc_first_only": b1, "disc_second_only": c1, "p": p, "p_disp": pdisp(p),
                                       "diff": (int(c[a].sum()) - int(c[b].sum())) / len(SEEDS)}
    for (k, v), q in zip(out["tests"].items(), holm([v["p"] for v in out["tests"].values()])):
        v["p_holm"], v["p_holm_disp"] = q, pdisp(q)
    a, b = c["drive"], c["tauprime"]
    both = [s for s in SEEDS if arms["drive"][s]["complete"] and arms["tauprime"][s]["complete"]]
    dtv = np.array([arms["tauprime"][s]["evacuation_time"] - arms["drive"][s]["evacuation_time"] for s in both])
    same_t = sum(abs(arms["tauprime"][s]["t_end"] - arms["drive"][s]["t_end"]) < 1e-9 for s in SEEDS)
    b1, c1 = int((a & ~b).sum()), int((b & ~a).sum())
    out["agreement_drive_tauprime"] = {
        "same_outcome": int((a == b).sum()), "both_complete": int((a & b).sum()), "both_fail": int((~a & ~b).sum()),
        "drive_only_complete": b1, "tauprime_only_complete": c1, "mcnemar_p": mcnemar_exact(b1, c1),
        "mcnemar_p_disp": pdisp(mcnemar_exact(b1, c1)), "identical_t_end": int(same_t),
        "evac_diff_tauprime_minus_drive_s": {"n": len(both), "median": float(np.median(dtv)) if len(dtv) else None,
                                             "mean": float(dtv.mean()) if len(dtv) else None,
                                             "abs_max": float(np.abs(dtv).max()) if len(dtv) else None}}
    labels = {}
    for a in ("drive", "tauprime", "sfm", "orca_rvo2"):
        res = KE6 if a == "orca_rvo2" else KS
        pre = "E6a" if a == "orca_rvo2" else a
        rows = []
        for s in SEEDS:
            r = arms[a][s]
            if r["complete"]:
                continue
            if a == "sfm" and s < 342:
                rows.append({"seed": s, "rest": bool(r["deadlock"]), "class": None, "n_res": r["n_remaining"]})
                continue
            rows.append({"seed": s, "rest": bool(r["deadlock"]), "class": E6A.classify(res, f"{pre}|seed{s}"),
                         "n_res": r["n_remaining"], "end_speed_max": max(x["speed"] for x in r["residual"])})
        f = {"n_fail": len(rows), "at_rest": sum(x["rest"] for x in rows), "moving_at_600s": sum(not x["rest"] for x in rows),
             "classified": sum(x["class"] is not None for x in rows),
             "at_rest_classes": {k: sum(x["rest"] and x["class"] == k for x in rows) for k in CL},
             "moving_classes": {k: sum((not x["rest"]) and x["class"] == k for x in rows) for k in CL},
             "end_speed_max_moving": [float(x["end_speed_max"]) for x in rows if not x["rest"] and "end_speed_max" in x],
             "n_res_counts": {str(k): sum(x["n_res"] == k for x in rows) for k in sorted({x["n_res"] for x in rows})},
             "rows": rows}
        if a == "sfm":
            f["note"] = "classes only for the T1 seeds 342-427 (velorca 242-341 have no keystone test)"
        out["failure"][a] = f
        labels[a] = [x["class"] for x in rows if x["class"] is not None]
    from scipy.stats import fisher_exact
    fo = out["failure"]["orca_rvo2"]
    for a in ("drive", "tauprime"):
        fa = out["failure"][a]
        pf = fisher_exact([[fa["at_rest"], fa["moving_at_600s"]], [fo["at_rest"], fo["moving_at_600s"]]])[1]
        fa["rest_vs_moving_fisher_vs_orca_rvo2"] = {"table": [[fa["at_rest"], fa["moving_at_600s"]],
                                                              [fo["at_rest"], fo["moving_at_600s"]]],
                                                    "p": float(pf), "p_disp": pdisp(float(pf))}
        if labels[a] and labels["orca_rvo2"]:
            out["failure"][a]["class_test_vs_orca_rvo2"] = E6A.perm_table_test(labels[a], labels["orca_rvo2"])
    print(rev4lib.out_json("T1", out))
    brief(out)


def brief(o):
    print("repro", o["reproduction_sfm"])
    for a, v in o["completion"].items():
        print(a, v["k"], "/", v["n"], [round(x, 3) for x in v["ci95"]], "deadlock", v["deadlock"], "capped", v["capped"])
    for k, v in o["tests"].items():
        print(k, v["disc_first_only"], ":", v["disc_second_only"], "p", v["p_disp"], "holm", v["p_holm_disp"])
    print("agree", {k: v for k, v in o["agreement_drive_tauprime"].items()})
    for a, f in o["failure"].items():
        print(a, {k: v for k, v in f.items() if k not in ("rows", "end_speed_max_moving")})


if __name__ == "__main__":
    main()
