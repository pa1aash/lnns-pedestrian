"""T6: fact look-ups from existing data and code (no new runs), each with its source; recomputed from the source
files so that every value has a registry key. Facts g (how 186 was fixed) and h (Welch or Student) are statements
about code and planning documents and are kept as text with their file:line sources.
Output: data/derived/rev4_T6.json.
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import DATA, DERIVED, load_runs, np  # noqa: E402


def a_standoffs():
    ks = json.load(open(os.path.join(DERIVED, "E1_keystone.json")))["modes"]["E1b"]["per_snapshot"]
    coll = [x for x in ks if x["class"] == "collective"]
    runs = [r for r in load_runs(os.path.join(DATA, "E1", "E1_runs.jsonl")) if r["mode"] == "E1b"]
    d98 = [r for r in runs if 42 <= r["seed"] <= 141 and r["deadlock"]]
    e7 = json.load(open(os.path.join(DERIVED, "E7_analysis.json")))["cells"]["default"]["classes"]
    return {"source": "data/derived/E1_keystone.json (modes.E1b.per_snapshot, class collective); data/E1/E1_runs.jsonl",
            "n_deadlocks_196": len(ks), "n_deadlocks_seeds_42_141": len(d98),
            "E7_default_cell_classified": e7["n_classified"], "E7_default_cell_collective": e7["counts"]["collective"],
            "standoffs": [{"seed": x["seed"], "members": x["n_resid"], "kind": "pair" if x["n_resid"] == 2 else "group",
                           "blocker": x["blocker"], "K1_blocker_alone_held": x["K1_held"],
                           "K2_held_without_blocker": x["K2_held"], "in_seeds_42_141": 42 <= x["seed"] <= 141}
                          for x in coll],
            "members_min": min(x["n_resid"] for x in coll), "members_max": max(x["n_resid"] for x in coll),
            "same_two_in_both_sets": all(42 <= x["seed"] <= 141 for x in coll)}


def b_alone_quenches():
    d = json.load(open(os.path.join(DERIVED, "rev2_A3.json")))
    cells = d["cells"]
    snaps = sorted({c["tag"] for c in cells})
    betas = sorted({c["beta"] for c in cells})
    return {"source": "data/derived/rev2_A3.json (cells; inputs data/E4/e4_escape.jsonl alone and data/revision/B3/b3.jsonl)",
            "snapshots": snaps, "dU_alone_J": {s: d["snapshots"][s]["dU_alone_J"] for s in snaps}, "betas": betas, "n_snapshots": len(snaps),
            "n_betas": len(betas), "restarts_per_cell": sorted({c["n"] for c in cells}),
            "total": sum(c["n"] for c in cells), "events": d["pooled"]["events"], "censored": d["pooled"]["censored"],
            "from_E4": sum(c["n"] for c in cells if c["beta"] <= 3.5), "from_B3": sum(c["n"] for c in cells if c["beta"] >= 5),
            "t_cens_s": {f"{c['tag']}|{c['beta']}": c["t_cens"] for c in cells},
            "seeds": "E4: noise seed 11000 + 1000 k + 100 level + rep (k = E4 index, level 0-2); "
                     "B3: 51000 + 1000 k + 100 level + rep (level 0-2 for beta 5, 6, 7), rep 0-19"}


def c_roc():
    f = json.load(open(os.path.join(DERIVED, "E2_analysis.json")))["f_noise_vs_C3"]["lone_keystone"]["margin_predicts_C3_rvo2_failure"]
    return {"source": "data/derived/E2_analysis.json f_noise_vs_C3.lone_keystone.margin_predicts_C3_rvo2_failure "
                      "(experiments/E2/analyze.py:311-323)",
            "n": f["n"], "positives_held": f["n_fail"], "negatives_freed": f["n"] - f["n_fail"], "auc": f["auc_margin_C3"],
            "auc_ci95_boot": f["auc_margin_C3_ci95_boot"], "score": "stuck-alone margin with the C3 rest drive (g_max - drive, N)",
            "held_margins_N": f["margin_C3_failed"], "freed_margin_range_N": f["margin_C3_freed_range"],
            "freed_with_positive_margin": f["freed_with_margin_C3_gt_0"], "held_with_nonpositive_margin": f["failed_with_margin_C3_le_0"]}


def d_bias():
    sel = {s["tag"]: s for s in json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]}
    cnt = defaultdict(lambda: {"runs": 0, "freed": 0, "snaps": set(), "reps": set()})
    for r in load_runs(os.path.join(DATA, "E2", "e2_quench.jsonl")):
        if not r["arm"].startswith("bias"):
            continue
        tag, arm, rep = r["job_id"].split("|")
        s = sel[tag]
        if s["class"] != "lone_keystone":
            continue
        c = cnt[arm]
        c["runs"] += 1
        c["freed"] += str(s["blocker"]) in {str(x) for x in r["exits"]}
        c["snaps"].add(tag)
        c["reps"].add(rep)
    arms = {a: {"b": float(a[4:]), "runs": v["runs"], "blocker_freed": v["freed"], "snapshots": len(v["snaps"]),
                "runs_per_snapshot": v["runs"] // len(v["snaps"]), "reps": sorted(v["reps"])} for a, v in sorted(cnt.items())}
    a = json.load(open(os.path.join(DERIVED, "E2_analysis.json")))["a_rates_time_to_free"]["lone_keystone"]["bias0p5"]
    return {"source": "data/E2/e2_quench.jsonl (arms bias0.05-bias0.5; experiments/E2/e2_quench.py:42-43, 44)",
            "b_values": sorted(v["b"] for v in arms.values()), "b_max": max(v["b"] for v in arms.values()),
            "angle_max_deg": float(np.degrees(np.arctan(max(v["b"] for v in arms.values())))),
            "handedness": "one (e_perp = e rotated +90 deg, b > 0 only)", "arms": arms,
            "n_snapshots": 34, "total_runs": sum(v["runs"] for v in arms.values()),
            "total_freed": sum(v["blocker_freed"] for v in arms.values()),
            "noise_seeds": "none (deterministic arm); perturbation seeds 900-904 (1e-9 m) plus one unperturbed run",
            "wilson_upper_bias0p5_snapshots": a["rate_wilson95"][2]}


def e_stalls():
    L = json.load(open(os.path.join(DERIVED, "E6_analysis.json")))["lifetimes"]
    pv = L["pred_vs_obs"]
    diffs = [abs(a - b) for a, b in zip(pv["S_pred"], pv["S_obs_km"])]
    return {"source": "data/derived/E6_analysis.json lifetimes (experiments/E6/analyze.py:122-136 stalls, :170-202 "
                      "barrier_picture, :365-368 max_abs_diff; CHECK_T :49)",
            "statistic": "max over t in {30, 60, 120, 300} s of |S_pred(t) - S_KM(t)|",
            "value": pv["max_abs_diff"], "argmax_t_s": pv["t"][int(np.argmax(diffs))], "diffs": diffs,
            "S_pred": pv["S_pred"], "S_obs_km": pv["S_obs_km"],
            "sample": {"runs": "E6b, C1 + sigma* = 0.0467 m/s, seeds 242-427 (186)", "n_stalls": L["n_stalls"],
                       "ended_by_exit": L["n_escaped"], "censored_at_600s": L["n_open_at_end"],
                       "runs_with_stall": L["runs_with_stall"],
                       "stall": "interval >= 10 s between exits (the first, approach gap excluded); open at 600 s censored"},
            "prediction": {"n_barriers": L["barrier_picture"]["n_barriers"], "nu": L["barrier_picture"]["nu_full_median"],
                           "kT_eff_median": L["barrier_picture"]["kT_eff_median"],
                           "form": "S(t) = mean_i exp(-lambda_i t) / mean_i exp(-lambda_i 10 s), lambda_i = nu exp(-dU_i / kT_eff(sigma*, tau_b,i))"},
            "test": "none: a descriptive maximum distance at four times; S_KM is the Kaplan-Meier estimate, no p-value or band"}


def i_overhang():
    d = json.load(open(os.path.join(DERIVED, "rev_B5.json")))["overhang_mm"]
    return {"source": "experiments/revision/B5_analyze.py:9, :36 (W_HALF = 0.4), :104-112; data/derived/rev_B5.json overhang_mm",
            "definition": "min over the two pair members of |y_i - 5| - w/2, w/2 = 0.4 m, at the saved snapshot positions",
            "sign": "positive when the member's centre lies laterally beyond the door edge (|y - 5| > w/2, behind the jamb's "
                    "flat face); negative would be a centre inside the opening",
            "n": d["n"], "min_mm": d["raw_min"] * 1e3, "max_mm": d["raw_max"] * 1e3, "median_mm": d["raw_median"] * 1e3,
            "all_positive": d["raw_min"] > 0}


def main():
    out = {"script": "experiments/revision4/T6_facts.py", "doc": __doc__,
           "a": a_standoffs(), "b": b_alone_quenches(), "c": c_roc(), "d": d_bias(), "e": e_stalls(), "i": i_overhang(),
           "g": {"answer": "planned before the runs: the TOST sample size n = z^2 2p(1-p)/delta^2 with z = 2.927 "
                           "(alpha 0.05 each side, power 0.80), p = 0.575, delta = 0.15 gives 186 per arm",
                 "check": 2.927 ** 2 * 2 * 0.575 * 0.425 / 0.15 ** 2,
                 "sources": ["pedestrian-abs-plan wave2/SIGNATURES.md:6 and :18 (S7, 186 per arm at +-0.15)",
                             "pedestrian-abs-plan plan/FINAL_PLAN.md:257, :270, :338 (E6 186 per arm, TOST-sized)",
                             "pedestrian-abs-plan wave2/COMPUTE_PLAN.md:30, :41; plan/CORRECTIONS_TABLE.md:29",
                             "experiments/E6/e6.py:29 SEEDS range(242, 428), first commit a48a386 (2026-11-08) before any E6 run",
                             "reports/B4B_REPORT.md:13 (E6a 186 jobs queued)"],
                 "not_a_stopping_rule": "no launcher, log or commit shows a compute-window or stopping rule; seeds 242-427 are "
                                        "the first 186 after the E1 seeds 42-241"},
           "h": {"flow_ratio": "Welch: delta-method interval of the log ratio of means with Welch-Satterthwaite df "
                               "(experiments/fixan/fix_a7.py:103-118, ratio_means; used by D_croma_integrity.d4 :268)",
                 "means": "Student t with n - 1 df (fix_a7.tci :85-92; E10/analyze.py tci :59-67) for flow, fluctuation, gaps",
                 "matched_ratio": "Student t on the logs over human runs (fix_a7.matched_ratio :135)"}}
    print(rev4lib.out_json("T6", out))


if __name__ == "__main__":
    main()
