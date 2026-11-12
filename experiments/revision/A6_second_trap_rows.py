"""A6: second-trap rows for Table 4 (noise sigma = 0.07 m/s against force-coupled ORCA, RVO2 solver).

Inputs (existing data only):
  data/E2/e2_quench.jsonl            E2 lone-trap quench library (arms noise0.07, C3_rvo2, C3_pub)
  data/derived/selection.json        E2 snapshots: tag, blocker id, stratum (class)
  data/derived/E2_analysis.json      the published Table 4 lone-keystone row (experiments/E2/analyze.py)
  experiments/fixan/fix_a1.py        lone_block(): J of the unresolved sets, two-level bootstrap, independence
Output: data/derived/rev_A6.json

Every definition is the one of the lone-keystone row of Table 4 (macros EtwoLKNoiseC*, TabThreeLK*,
FixAoneLoneJ*), applied to the 26 snapshots of stratum lone_keystone_second_trap:
  freed       the blocker (selection.json) exits within 120 s.
  noise       every (snapshot, seed) run counts once (5 seeds per snapshot, 130 runs).
  ORCA        the unperturbed run per snapshot (26 runs); the five 1e-9 m replays (perturb seeds 900-904,
              130 replays) enter only the replay column.
  Delta       mean over snapshots of (noise per-snapshot freed fraction k_i/5 minus ORCA outcome c_i);
              95% percentile bootstrap over snapshots, 2000 resamples, PCG64(12345) (E2 analyze.py rule).
              The value printed in the table is the one stored by E2 analyze.py (same code, same data);
              this script recomputes it from the raw runs and checks the point value.
  t_1/2       Kaplan-Meier median time to free (held runs censored at 120 s; product-limit; first time
              S(t) <= 0.5), over runs (noise) or unperturbed runs (ORCA).
  replay      ORCA: replays whose freed/held outcome differs from the unperturbed run (of 130); also the
              largest |exit-time shift|. Noise: snapshots whose five runs disagree on freed/held (of 26).
  J           Jaccard index of the unresolved sets: noise unresolved when fewer than half of its 5 seeds
              free it (k <= 2), ORCA unresolved when the unperturbed run holds. Two-level bootstrap interval
              (snapshots, then seeds within snapshot; 10000) and the exact independence expectation of J
              (hypergeometric overlap of sets of the observed sizes), both from fix_a1.lone_block, so the
              second-trap J is computed by the very function that produced FixAoneLoneJ*.
The legacy-solver ORCA (C3_pub) outcome is given beside it for reference.
"""
import importlib.util
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
import numpy as np  # noqa: E402

T_Q = 120.0
STRATUM = "lone_keystone_second_trap"
N_BOOT, RNG_SEED = 2000, 12345


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E2A = _load_module("e2_analyze", os.path.join(revlib.ROOT, "experiments", "E2", "analyze.py"))
FIXA1 = _load_module("fix_a1_mod", os.path.join(revlib.ROOT, "experiments", "fixan", "fix_a1.py"))


def load_runs():
    sel = json.load(open(os.path.join(revlib.DERIVED, "selection.json")))["E2"]["snapshots"]
    snaps = {s["tag"]: s for s in sel}
    runs = defaultdict(dict)
    for line in open(os.path.join(revlib.DATA, "E2", "e2_quench.jsonl")):
        r = json.loads(line)
        tag, arm, rep = r["job_id"].split("|")
        if arm not in ("noise0.07", "C3_rvo2", "C3_pub"):
            continue
        t = r["exits"].get(str(snaps[tag]["blocker"]))
        f = t is not None and t <= T_Q + 1e-9
        runs[(tag, arm)][rep] = (f, round(t, 2) if f else None)
    return sel, runs


def boot(stat, n, rng):
    v = [stat(rng.integers(0, n, n)) for _ in range(N_BOOT)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def block(sel, runs, stratum):
    T = [s["tag"] for s in sel if s["class"] == stratum]
    rng = np.random.Generator(np.random.PCG64(RNG_SEED))
    noise = [[runs[(t, "noise0.07")][str(i)] for i in range(5)] for t in T]
    k = np.array([sum(f for f, _ in row) for row in noise])
    c3 = np.array([runs[(t, "C3_rvo2")]["u"][0] for t in T])
    pub = np.array([runs[(t, "C3_pub")]["u"][0] for t in T])
    diff = k / 5 - c3.astype(float)
    nruns = [x for row in noise for x in row]
    Kn = E2A.km([x[1] if x[0] else T_Q for x in nruns], [x[0] for x in nruns])
    Ko = E2A.km([runs[(t, "C3_rvo2")]["u"][1] if c3[i] else T_Q for i, t in enumerate(T)], list(c3))
    # replays
    rep_dis, max_dt, n_rep = 0, 0.0, 0
    for t in T:
        u = runs[(t, "C3_rvo2")]["u"]
        for rep, x in runs[(t, "C3_rvo2")].items():
            if rep == "u":
                continue
            n_rep += 1
            rep_dis += int(x[0] != u[0])
            if x[0] and u[0]:
                max_dt = max(max_dt, abs(x[1] - u[1]))
    pub_dis = sum(int(x[0] != runs[(t, "C3_pub")]["u"][0]) for t in T
                  for rep, x in runs[(t, "C3_pub")].items() if rep != "u")
    noise_dis = int(sum(0 < kk < 5 for kk in k))
    w = revlib.wilson(int(k.sum()), int(5 * len(T)))
    wo = revlib.wilson(int(c3.sum()), len(T))
    return {
        "n_snapshots": len(T),
        "noise0p07": {"freed": int(k.sum()), "n_runs": int(5 * len(T)), "fraction": float(k.mean() / 5),
                      "wilson95": [float(w[1]), float(w[2])],
                      "km_median_s": Kn["median"], "km_q25_s": Kn["q25"], "km_q75_s": Kn["q75"],
                      "S_end": Kn["S_end"],
                      "snapshots_runs_disagree": noise_dis, "snapshots_freed_all_seeds": int((k == 5).sum()),
                      "snapshots_freed_no_seed": int((k == 0).sum()),
                      "per_snapshot_k": {t: int(kk) for t, kk in zip(T, k)}},
        "C3_rvo2": {"freed": int(c3.sum()), "n": len(T), "fraction": float(c3.mean()),
                    "wilson95": [float(wo[1]), float(wo[2])],
                    "km_median_s": Ko["median"], "km_q25_s": Ko["q25"], "km_q75_s": Ko["q75"], "S_end": Ko["S_end"],
                    "replays": n_rep, "replays_outcome_differs": rep_dis,
                    "replay_max_abs_exit_shift_s": max_dt,
                    "unresolved_tags": [t for t, f in zip(T, c3) if not f]},
        "C3_pub_reference": {"freed": int(pub.sum()), "n": len(T), "replays_outcome_differs": int(pub_dis),
                             "replays": n_rep},
        "delta": {"value": float(diff.mean()), "ci95": boot(lambda i: diff[i].mean(), len(T), rng),
                  "definition": "mean_i (k_i/5 - c_i), bootstrap over snapshots, 2000, PCG64(12345)"},
    }


def main():
    sel, runs = load_runs()
    E2 = json.load(open(os.path.join(revlib.DERIVED, "E2_analysis.json")))
    out = {"script": "experiments/revision/A6_second_trap_rows.py", "doc": __doc__}
    for st in ("lone_keystone", STRATUM):
        b = block(sel, runs, st)
        f = E2["f_noise_vs_C3"][st]["noise0p07"]
        b["delta"]["E2_analysis_value"] = f["paired_rate_diff_noise_minus_C3"]
        b["delta"]["E2_analysis_ci95"] = f["paired_rate_diff_ci95_boot"]
        assert abs(b["delta"]["value"] - f["paired_rate_diff_noise_minus_C3"]) < 1e-12
        assert b["noise0p07"]["freed"] == E2["a_rates_time_to_free"][st]["noise0p07"]["freed"]
        assert b["noise0p07"]["km_median_s"] == E2["a_rates_time_to_free"][st]["noise0p07"]["time_to_free_km"]["median"]
        out[st] = b
    # J of the unresolved sets: the very function behind FixAoneLoneJ* (fix_a1.lone_block), second-trap stratum
    s1, snaps, bar, r1 = FIXA1.load_e2()
    lb = FIXA1.clean(FIXA1.lone_block(s1, snaps, bar, r1, [STRATUM], "second traps (A6)"))
    o = lb["noise"]["noise0p07"]
    ind = o["independence"]
    J = {"value": o["J_observed"], "ci95_two_level_boot": o["J_ci95_two_level_boot"],
         "ci95_snapshot_boot": o["J_ci95_snapshot_boot"],
         "noise_unresolved": o["noise_unresolved"], "noise_unresolved_tags": o["noise_unresolved_tags"],
         "orca_unresolved": lb["orca_unresolved"], "orca_unresolved_tags": lb["orca_unresolved_tags"],
         "shared": o["shared"],
         "independence_expected_J": ind["expected_J"], "independence_J_range95": ind["J_range95"],
         "independence_expected_overlap": ind["expected_overlap"],
         "p_J_ge_observed": ind["p_J_ge_observed"], "p_J_ge_observed_disp": revlib.pdisp(ind["p_J_ge_observed"]),
         "noise_freed_runs_on_orca_unresolved": o["association_with_orca"]["noise_freed_runs_on_orca_unresolved"],
         "noise_freed_runs_on_orca_freed": o["association_with_orca"]["noise_freed_runs_on_orca_freed"],
         "auc_low_noise_freeing_for_orca_unresolved": o["association_with_orca"]["auc_low_noise_freeing_for_orca_unresolved"],
         "auc_ci95": o["association_with_orca"]["auc_ci95_snapshot_boot"],
         "auc_perm_p_one_sided": o["association_with_orca"]["perm_p_one_sided_auc"],
         "rule": "noise unresolved: k <= 2 of 5 seeds free; ORCA unresolved: unperturbed run holds (fix_a1.lone_block)"}
    out[STRATUM]["J"] = J
    st = out[STRATUM]
    d = st["delta"]
    out["headline"] = {
        "noise_freed": st["noise0p07"]["freed"], "noise_runs": st["noise0p07"]["n_runs"],
        "orca_freed": st["C3_rvo2"]["freed"], "orca_n": st["C3_rvo2"]["n"],
        "delta": revlib.sig(d["value"]), "delta_lo": revlib.sig(d["ci95"][0]), "delta_hi": revlib.sig(d["ci95"][1]),
        "delta_ci_covers_0": bool(d["ci95"][0] <= 0 <= d["ci95"][1]),
        "J": J["value"], "J_lo": J["ci95_two_level_boot"][0], "J_hi": J["ci95_two_level_boot"][1],
        "J_ind": J["independence_expected_J"], "J_p": J["p_J_ge_observed"],
        "noise_km_median": st["noise0p07"]["km_median_s"], "orca_km_median": st["C3_rvo2"]["km_median_s"],
        "noise_disagree": st["noise0p07"]["snapshots_runs_disagree"], "snapshots": st["n_snapshots"],
        "orca_replay_dis": st["C3_rvo2"]["replays_outcome_differs"], "orca_replays": st["C3_rvo2"]["replays"]}
    print(revlib.out_json("A6", out))
    print(json.dumps(out["headline"], indent=1))


if __name__ == "__main__":
    main()
