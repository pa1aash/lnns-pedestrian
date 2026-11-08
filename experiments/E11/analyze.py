"""E11 analysis: persistence-filtered agent-agent overlaps at the room bottleneck (CF, 50 agents, 300 s cap).

  python3 experiments/E11/analyze.py        write data/derived/E11_analysis.json

Input: data/E11/e11_overlap.jsonl (experiments/E11/e11_overlap.py; override the directory with E11_SRC=<dir>).
Cells: C1, C2, C3_rvo2, C4_rvo2 at w in {1.0, 1.2, 1.8} m, plus C3_pub at w = 1.0 m; 25 seeds (42-66) per cell, the
same seeds in every cell, so arms are paired by seed at each width.

Definitions (from the run script): an overlap is an active pair with |x_i - x_j| < r_i + r_j at the end of a step;
zone of a pair = zone of its midpoint (upstream x < 8, throat 8 <= x <= 10.5, downstream x > 10.5 m). An episode is a
maximal run of consecutive overlapping steps of one pair (zone at its first step); a persistent episode lasts >= 0.1 s
(>= 10 steps at dt = 0.01 s). "Overlap timesteps" (steps with at least one overlapping pair in the zone, unfiltered) is
the conference paper's metric and is reported for comparison.

Method, per cell (arm x width):
  n runs, completions, deadlocks, runs with open persistent episodes at the end;
  per zone: runs with >= 1 persistent episode, Wilson 95% interval; mean persistent episodes per run with a 95%
  percentile bootstrap interval (2000 resamples of seeds, numpy PCG64(12345), one generator for the whole script,
  consumed in a fixed cell/zone order); total persistent episodes; median / max persistent duration (s) and max depth
  (m), null when there are none; unfiltered episodes (all durations) and overlap timesteps (mean, SD with ddof = 1).
Paired comparisons at each width (C2, C4_rvo2, C3_rvo2 each against C1, matched on seed): on persistent throat
  episodes per run (primary) and on unfiltered throat overlap timesteps (conference metric, secondary): Wilcoxon
  signed-rank (scipy.stats.wilcoxon, zero_method = 'wilcox', two-sided; p is null when every paired difference is
  zero, since the test is then undefined) with the number of non-zero pairs, and the paired mean difference (arm - C1)
  with a 95% percentile bootstrap interval (2000 resamples of seed pairs).
Verdict: the conference claim (rejection-sampled, 50 agents, 300 s, w = 1.0 m: C1 throat 1.20 +- 1.96 overlap
  timesteps, C2 = C4 = 0, C3 0.80 +- 2.87, Wilcoxon C1 vs C4 p = 0.011; "TTC (arms C2, C4) eliminates throat overlaps at
  narrow exits") is checked with the persistence filter: do the TTC arms have zero persistent throat episodes at each
  width, does C1 have any; status confirmed / revised / withdrawn.
Keys in the JSON avoid '.' (registry key paths split on '.'): cell "C1|w1.0" is stored as cells.C1.w1p0.
python3 with numpy and scipy (system python3).
"""
import json
import os

import numpy as np
from scipy.stats import wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.environ.get("E11_SRC", os.path.join(ROOT, "data", "E11"))
RUNS = os.path.join(SRC, "e11_overlap.jsonl")
OUT = os.path.join(ROOT, "data", "derived", "E11_analysis.json")

ARMS = ("C1", "C2", "C3_rvo2", "C4_rvo2")
WIDTHS = (1.0, 1.2, 1.8)
CELLS = [(a, w) for w in WIDTHS for a in ARMS] + [("C3_pub", 1.0)]
SEEDS = list(range(42, 67))
ZONES = ("upstream", "throat", "downstream")
TTC = ("C2", "C4_rvo2")
NBOOT = 2000
RNG = np.random.Generator(np.random.PCG64(12345))
CONFERENCE = {"setting": "rejection-sampled spawn, 50 agents, 300 s, w = 1.0 m",
              "metric": "throat overlap timesteps per run (unfiltered)",
              "C1_mean": 1.20, "C1_sd": 1.96, "C2_mean": 0.0, "C4_mean": 0.0, "C3_mean": 0.80, "C3_sd": 2.87,
              "wilcoxon_C1_vs_C4_p": 0.011,
              "claim": "time-to-collision (TTC, arms C2 and C4) eliminates throat overlaps at narrow exits"}


def wkey(w):
    return f"w{w:.1f}".replace(".", "p")


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [float(max(0.0, c - h)), float(min(1.0, c + h))]


def boot_mean(x):
    x = np.asarray(x, float)
    idx = RNG.integers(0, len(x), size=(NBOOT, len(x)))
    m = x[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def msd(x):
    x = np.asarray(x, float)
    return {"mean": float(x.mean()), "sd": float(x.std(ddof=1)) if len(x) > 1 else None, "total": int(x.sum())}


def paired(a, b):
    """Arm a against reference b (same seed order): Wilcoxon and mean difference a - b with bootstrap CI."""
    d = np.asarray(a, float) - np.asarray(b, float)
    nz = int(np.count_nonzero(d))
    p = stat = None
    if nz:
        res = wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
        p, stat = float(res.pvalue), float(res.statistic)
    return {"n_pairs": len(d), "n_nonzero_pairs": nz, "wilcoxon_stat": stat, "wilcoxon_p": p,
            "mean_diff": float(d.mean()), "mean_diff_ci95": boot_mean(d),
            "note": None if nz else "all paired differences are zero; Wilcoxon undefined (p = null)"}


def main():
    R = [json.loads(l) for l in open(RUNS) if l.strip()]
    by = {}
    for r in R:
        by.setdefault((r["arm"], float(r["width"])), {})[r["seed"]] = r
    anomalies = []
    cells, series = {}, {}
    for arm, w in CELLS:
        Rc = by.get((arm, w), {})
        missing = [s for s in SEEDS if s not in Rc]
        if missing:
            anomalies.append(f"{arm}|w{w}: missing seeds {missing}")
        rows = [Rc[s] for s in SEEDS if s in Rc]
        n = len(rows)
        row = {"arm": arm, "width_m": w, "n": n, "missing_seeds": missing,
               "k_complete": sum(bool(r["complete"]) for r in rows),
               "k_deadlock": sum(bool(r["deadlock"]) for r in rows),
               "open_persistent_episodes_at_end": sum(r["zones"][z]["open_at_end_ge_0.1s"] for r in rows for z in ZONES),
               "evacuation_time_s": msd([r["evacuation_time"] for r in rows if r["complete"]]) if any(
                   r["complete"] for r in rows) else None,
               "zones": {}}
        for z in ZONES:
            Z = [r["zones"][z] for r in rows]
            pe = [x["episodes_ge_0.1s"] for x in Z]
            durs = [d for x in Z for d in x["episode_dur_s_ge_0.1s"]]
            deps = [d for x in Z for d in x["episode_max_depth_m_ge_0.1s"]]
            k = sum(v > 0 for v in pe)
            row["zones"][z] = {
                "persistent": {"runs_with": k, "runs_with_wilson95": wilson(k, n), "mean_per_run": float(np.mean(pe)),
                               "mean_per_run_ci95": boot_mean(pe), "total": int(sum(pe)),
                               "pairs_total": int(sum(x["pairs_with_episode_ge_0.1s"] for x in Z)),
                               "dur_s_median": float(np.median(durs)) if durs else None,
                               "dur_s_max": float(max(durs)) if durs else None,
                               "depth_m_max": float(max(deps)) if deps else None},
                "unfiltered": {"episodes": msd([x["episodes_all"] for x in Z]),
                               "runs_with_episode": sum(x["episodes_all"] > 0 for x in Z),
                               "overlap_timesteps": msd([x["overlap_timesteps"] for x in Z]),
                               "pair_steps": msd([x["pair_steps"] for x in Z])}}
            series[(arm, w, z)] = (pe, [x["overlap_timesteps"] for x in Z])
        if row["k_deadlock"]:
            anomalies.append(f"{arm}|w{w}: {row['k_deadlock']} deadlocks")
        if row["open_persistent_episodes_at_end"]:
            anomalies.append(f"{arm}|w{w}: {row['open_persistent_episodes_at_end']} open persistent episodes at end")
        cells.setdefault(arm, {})[wkey(w)] = row

    comps = {}
    for w in WIDTHS:
        ref_p, ref_t = series[("C1", w, "throat")]
        for arm in ("C2", "C4_rvo2", "C3_rvo2"):
            ap_, at_ = series[(arm, w, "throat")]
            comps.setdefault(wkey(w), {})[f"{arm}_vs_C1"] = {
                "persistent_throat_episodes": paired(ap_, ref_p),
                "throat_overlap_timesteps": paired(at_, ref_t)}
    ap_, at_ = series[("C3_pub", 1.0, "throat")]
    ref_p, ref_t = series[("C1", 1.0, "throat")]
    comps["w1p0"]["C3_pub_vs_C1"] = {"persistent_throat_episodes": paired(ap_, ref_p),
                                     "throat_overlap_timesteps": paired(at_, ref_t)}

    # verdict
    th = lambda a, w: cells[a][wkey(w)]["zones"]["throat"]
    ttc_zero = {wkey(w): all(th(a, w)["persistent"]["total"] == 0 for a in TTC) for w in WIDTHS}
    c1_pers = {wkey(w): th("C1", w)["persistent"]["total"] for w in WIDTHS}
    c1_unf = {wkey(w): th("C1", w)["unfiltered"]["overlap_timesteps"]["total"] for w in WIDTHS}
    ttc_unf_zero = {wkey(w): all(th(a, w)["unfiltered"]["overlap_timesteps"]["total"] == 0 for a in TTC) for w in WIDTHS}
    any_pers = sum(z["persistent"]["total"] for a in cells.values() for c in a.values() for z in c["zones"].values())
    if all(ttc_zero.values()) and sum(c1_pers.values()) > 0:
        status, reason = "confirmed", "C1 has persistent throat overlaps and the TTC arms have none at every width."
    elif not all(ttc_zero.values()):
        status, reason = "withdrawn", "TTC arms show persistent throat overlaps."
    else:
        status = "revised"
        reason = ("No arm has any persistent (>= 0.1 s) overlap episode at any width or zone, so the C1 overlaps that "
                  "TTC 'eliminates' are all sub-0.1 s transients: TTC removes transient contacts, not persistent "
                  "interpenetration, and 'eliminates throat overlaps' holds only for the unfiltered metric.")
    c1t = th("C1", 1.0)["unfiltered"]["overlap_timesteps"]
    c3t = th("C3_rvo2", 1.0)["unfiltered"]["overlap_timesteps"]
    verdict = {
        "conference": CONFERENCE,
        "reproduction_w1p0_unfiltered": {
            "C1_mean": c1t["mean"], "C1_sd": c1t["sd"], "C1_total": c1t["total"],
            "C1_runs_with": th("C1", 1.0)["unfiltered"]["runs_with_episode"],
            "C2_mean": th("C2", 1.0)["unfiltered"]["overlap_timesteps"]["mean"],
            "C4_rvo2_mean": th("C4_rvo2", 1.0)["unfiltered"]["overlap_timesteps"]["mean"],
            "C3_rvo2_mean": c3t["mean"], "C3_rvo2_sd": c3t["sd"],
            "C3_pub_mean": th("C3_pub", 1.0)["unfiltered"]["overlap_timesteps"]["mean"],
            "C3_pub_sd": th("C3_pub", 1.0)["unfiltered"]["overlap_timesteps"]["sd"],
            "wilcoxon_C4_vs_C1_p": comps["w1p0"]["C4_rvo2_vs_C1"]["throat_overlap_timesteps"]["wilcoxon_p"],
            "wilcoxon_C2_vs_C1_p": comps["w1p0"]["C2_vs_C1"]["throat_overlap_timesteps"]["wilcoxon_p"]},
        "ttc_zero_persistent_throat": ttc_zero,
        "ttc_zero_unfiltered_throat": ttc_unf_zero,
        "C1_persistent_throat_total": c1_pers,
        "C1_unfiltered_throat_timesteps_total": c1_unf,
        "persistent_episodes_all_cells_all_zones": int(any_pers),
        "status": status, "reason": reason,
        "table_cell": ("0 persistent (>= 0.1 s) overlaps in every arm, w = 1.0-1.8 m; TTC removes only sub-0.1 s "
                       "transients" if status == "revised" else reason)}
    out = {"script": "experiments/E11/analyze.py", "doc": __doc__, "source": os.path.relpath(RUNS, ROOT),
           "seeds": [SEEDS[0], SEEDS[-1]], "n_bootstrap": NBOOT, "rng": "PCG64(12345)",
           "persistence_threshold_s": 0.1, "cells": cells, "paired": comps, "verdict": verdict,
           "anomalies": anomalies}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)

    for arm, w in CELLS:
        c = cells[arm][wkey(w)]
        t = c["zones"]["throat"]
        p, u = t["persistent"], t["unfiltered"]["overlap_timesteps"]
        print(f"{arm:8s} w={w:.1f} n={c['n']} compl={c['k_complete']} dl={c['k_deadlock']} | persistent throat "
              f"runs={p['runs_with']}/{c['n']} total={p['total']} mean={p['mean_per_run']:.2f} "
              f"[{p['mean_per_run_ci95'][0]:.2f},{p['mean_per_run_ci95'][1]:.2f}] | unfiltered timesteps "
              f"{u['mean']:.2f}+-{u['sd']:.2f} (eps {t['unfiltered']['episodes']['total']})")
    for wk, d in comps.items():
        for k, v in d.items():
            a, b = v["persistent_throat_episodes"], v["throat_overlap_timesteps"]
            print(f"{wk} {k:14s} persistent: nz={a['n_nonzero_pairs']} p={a['wilcoxon_p']} | timesteps: "
                  f"nz={b['n_nonzero_pairs']} p={b['wilcoxon_p']} diff={b['mean_diff']:.2f} {b['mean_diff_ci95']}")
    print("verdict:", status, "-", reason)
    print("anomalies:", anomalies or "none")


if __name__ == "__main__":
    main()
