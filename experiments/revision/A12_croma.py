"""A12: CroMa comparison (paper Sect. 7): per-run flow table, censored longest gap, noise-variant flow ratio.

Inputs (read only):
  data/E10/e10_croma.jsonl         per model run: cell, matched human run, N, seed, t_end, complete, deadlock, npz
  E10 raw trajectories (*.npz)     located by experiments/fixan/fix_a7.py raw_dir()
  data/ext/croma/*_w080_*.txt      the five CroMa 2021 runs at w = 0.8 m (PeTrack export, 25 fps)
  data/ext/croma/README.md         dataset naming (DOI 10.34735/ped.2021.9)
  data/derived/fix_a7.json, data/derived/E10_analysis.json   cross-check only
Passage rule, flow and gap definitions are those of fix_a7.py (imported, unchanged): passage = first frame with
x >= x_e for a track that starts before the line; flow = (n - 1)/(last - first passage); gaps = differences of the
sorted passage times.

Computed:
  1 per-run table: for each human run (run id, file, corridor length L, motivation code h, tracks, passages, flow)
    the five matched model runs per variant (seed, status, flow) and their mean; for the four paper variants
    C1_cf (SFM), C1_cf_edge (SFM, jamb range B_w,edge), C3_rvo2_cf (force-coupled ORCA, RVO2), C1_cf_sig
    (SFM + noise sigma*), plus C1_pub (published parameters, not in the Sect. 7 text) for completeness.
  2 longest gap per run with the terminal gap of an incomplete run (deadlocked: stopped 10 s after all
    |v| < 0.01 m/s; capped: t = 600 s) right-censored: the run's longest gap G satisfies G >= c = max(longest
    interior gap, t_end - last passage), so incomplete runs enter as censored at c, complete runs as events at
    their longest interior gap. Per variant: censoring counts, Kaplan-Meier median of G (or "not reached",
    reported as > the largest censoring time), KM restricted mean to the largest observation (a lower bound of
    the mean when the last observation is censored), the mean of c over runs (also a lower bound), against the
    uncensored mean of the interior longest gap (the paper's EtenXGap).
  3 flow ratio model/human for every variant: ratio of mean flows, 95% interval exp(log r +- t se) with Welch df
    (fix_a7.ratio_means, same as FixAseven*FlowRatio), and the matched version.
Output: data/derived/rev_A12.json; markdown tables printed for the note.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
import numpy as np  # noqa: E402

import fix_a7 as F  # noqa: E402  (experiments/fixan on sys.path via revlib)

ROOT = revlib.ROOT
CELLS = ["C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig", "C1_pub"]
LABEL = {"C1_cf": "SFM", "C1_cf_edge": "SFM, jamb range B_w,edge", "C3_rvo2_cf": "force-coupled ORCA (RVO2)",
         "C1_cf_sig": "SFM + noise sigma*", "C1_pub": "SFM, published parameters (not in Sect. 7)"}
sig = revlib.sig


def km_curve(times, events):
    """Kaplan-Meier steps [(t, S(t))] at event times; events 1 = observed, 0 = right-censored."""
    t, e = np.asarray(times, float), np.asarray(events, int)
    s, steps = 1.0, []
    for u in np.unique(t[e == 1]):
        at = int((t >= u).sum())
        d = int(((t == u) & (e == 1)).sum())
        s *= 1 - d / at
        steps.append((float(u), float(s)))
    return steps


def km_summary(times, events):
    steps = km_curve(times, events)
    tau = float(max(times))
    med = next((u for u, s in steps if s <= 0.5 + 1e-12), None)
    # restricted mean: area under S from 0 to tau
    area, prev_t, prev_s = 0.0, 0.0, 1.0
    for u, s in steps:
        area += prev_s * (u - prev_t)
        prev_t, prev_s = u, s
    area += prev_s * (tau - prev_t)
    last_censored = bool(np.asarray(events)[int(np.argmax(times))] == 0)
    s_end = steps[-1][1] if steps else 1.0
    return {"median": med, "median_reached": med is not None,
            "median_lower_bound": None if med is not None else tau,
            "restricted_mean_to_tau": float(area), "tau": tau, "S_at_tau": float(s_end),
            "restricted_mean_is_lower_bound": last_censored, "steps": steps}


def main():
    rd = F.raw_dir()
    H = [F.per_run_stats(F.croma_run(f)) for f in sorted(glob.glob(os.path.join(F.CROMA, "*_w080_*.txt")))]
    R = [json.loads(l) for l in open(F.IN) if l.strip()]
    M = {c: [F.per_run_stats(F.model_run(r, rd)) for r in R if r["cell"] == c] for c in CELLS}
    fa7 = json.load(open(F.OUT))
    e10 = json.load(open(F.E10))
    hflow = [u["flow"] for u in H]
    hgap = [u["max_gap"] for u in H]

    # human run identifiers as in the files
    hrows = []
    for u, path in zip(H, sorted(glob.glob(os.path.join(F.CROMA, "*_w080_*.txt")))):
        hdr = [l.strip() for l in open(path) if l.startswith("#")][:3]
        hrows.append({"run": u["run"], "file": u["file"], "petrack_project": hdr[0].split(":", 1)[1].strip(),
                      "raw_trajectory_file": hdr[1].split(":", 1)[1].strip(), "width_m": u["width_m"], "L_m": u["L"],
                      "corridor": "2.0 m corridor" if u["L"] > 1 else "0.21 m (door in a wall)",
                      "h_code": u["h"], "motivation": F.MOTIV[u["h"]][0], "start_lineup": F.MOTIV[u["h"]][2],
                      "N_tracks": u["N"], "n_pass": u["n_pass"], "duration_s": u["t_end"],
                      "flow": u["flow"], "flow_2sf": sig(u["flow"], 3), "max_gap_s": u["max_gap"]})

    o = {"script": "experiments/revision/A12_croma.py",
         "dataset": {"doi": "10.34735/ped.2021.9", "title": "Bottleneck experiments with varying motivation levels",
                     "series": "CroMa 2021 (FZJ pedestrian data archive)", "licence": "CC BY 4.0",
                     "file_pattern": "<run>_w<width cm>_l<corridor length cm>_h<motivation code>.txt",
                     "note": "the run id inside each file is the PeTrack project name (header line 1), identical "
                             "to the file stem; the trajectory rows carry only track ids, no run id"},
         "humans": {"runs": hrows, "flow": F.tci(hflow), "longest_gap": F.tci(hgap)},
         "cells": {}, "check": {}}

    dev = []
    for c in CELLS:
        X = M[c]
        runs = []
        for u in X:
            st = "complete" if u["complete"] else ("deadlock" if u["deadlock"] else "capped")
            term = None if u["complete"] else float(u["t_end"] - u["tp"][-1])
            c_time = u["max_gap"] if u["complete"] else max(u["max_gap"], term)
            runs.append({"seed": u["seed"], "human_run": u["run"], "N": u["N"], "status": st, "t_end": u["t_end"],
                         "n_pass": u["n_pass"], "flow": u["flow"], "max_gap_interior": u["max_gap"],
                         "terminal_open": term, "longest_gap_obs_or_cens": c_time,
                         "event": int(u["complete"]), "terminal_is_longest": bool(term is not None and term > u["max_gap"])})
        per_h = {}
        for h in hrows:
            rr = sorted([r for r in runs if r["human_run"] == h["run"]], key=lambda r: r["seed"])
            per_h[h["run"]] = {"seeds": [r["seed"] for r in rr], "status": [r["status"] for r in rr],
                               "flows": [r["flow"] for r in rr], "mean": float(np.mean([r["flow"] for r in rr])),
                               "ratio_to_human": float(np.mean([r["flow"] for r in rr]) / h["flow"])}
        fl = [r["flow"] for r in runs]
        times = [r["longest_gap_obs_or_cens"] for r in runs]
        ev = [r["event"] for r in runs]
        kms = km_summary(times, ev)
        fr = F.ratio_means(fl, hflow)
        mr = F.matched_ratio([{"run": r["human_run"], "f": r["flow"]} for r in runs],
                             {h["run"]: h["flow"] for h in hrows}, "f")
        inc = [r for r in runs if not r["event"]]
        d = {"label": LABEL[c], "n": len(runs), "complete": sum(ev), "deadlock": sum(r["status"] == "deadlock" for r in runs),
             "capped": sum(r["status"] == "capped" for r in runs),
             "flow": F.tci(fl), "per_human_run": per_h, "runs": runs,
             "flow_ratio": {"ratio": fr["ratio"], "ci95": fr["ci95"], "welch_df": fr["welch_df"],
                            "fieller_ci95": fr["fieller_ci95"], "ratio_2sf": sig(fr["ratio"]),
                            "ci95_2sf": [sig(v) for v in fr["ci95"]]},
             "flow_ratio_matched": {"geo_ratio": mr["geo_ratio"], "ci95": mr["ci95"]},
             "longest_gap": {
                 "uncensored_interior_mean": float(np.mean([r["max_gap_interior"] for r in runs])),
                 "uncensored_interior_median": float(np.median([r["max_gap_interior"] for r in runs])),
                 "n_censored": len(inc), "n_censored_deadlock": sum(r["status"] == "deadlock" for r in inc),
                 "n_censored_capped": sum(r["status"] == "capped" for r in inc),
                 "n_terminal_is_longest": sum(r["terminal_is_longest"] for r in runs),
                 "terminal_open": F.tci([r["terminal_open"] for r in inc]) if len(inc) >= 2 else
                 {"n": len(inc), "mean": inc[0]["terminal_open"] if inc else None},
                 "with_terminal_mean_lower_bound": float(np.mean(times)),
                 "with_terminal_median_lower_bound": float(np.median(times)),
                 "km_median": kms["median"], "km_median_reached": kms["median_reached"],
                 "km_restricted_mean": kms["restricted_mean_to_tau"], "km_tau": kms["tau"],
                 "km_S_at_tau": kms["S_at_tau"], "km_restricted_mean_is_lower_bound": kms["restricted_mean_is_lower_bound"],
                 "km_steps": kms["steps"]}}
        lg = d["longest_gap"]
        for k in ("uncensored_interior_mean", "with_terminal_mean_lower_bound", "with_terminal_median_lower_bound",
                  "km_restricted_mean", "km_median"):
            lg[k + "_2sf"] = sig(lg[k]) if lg[k] is not None else None
        o["cells"][c] = d
        dev.append(abs(d["flow_ratio"]["ratio"] - fa7["cells"][c]["flow_ratio"]["ratio"]))
        dev.append(abs(lg["uncensored_interior_mean"] - e10["cells"][c]["longest_gap"]["mean"]))
    o["check"]["max_abs_dev_vs_fix_a7_ratio_and_E10_gap"] = float(max(dev))
    s = o["cells"]["C1_cf_sig"]["flow_ratio"]
    o["sig_flow_ratio"] = {"ratio": s["ratio"], "lo": s["ci95"][0], "hi": s["ci95"][1],
                           "existing_macros": "FixAsevenCSigFlowRatio {0.40}, ...Lo {0.33}, ...Hi {0.48} in "
                                              "paper/numbers.tex (fix_a7.json:cells.C1_cf_sig.flow_ratio)"}
    print(revlib.out_json("A12", o))
    print("check", o["check"])
    tables(o)


def tables(o):
    H = o["humans"]["runs"]
    print("\n| run (file) | corridor | motivation | N tracks / passed | human flow | "
          + " | ".join(LABEL[c] for c in CELLS[:4]) + " |")
    print("|---" * 9 + "|")
    for h in H:
        cells = []
        for c in CELLS[:4]:
            p = o["cells"][c]["per_human_run"][h["run"]]
            tag = {"complete": "", "deadlock": "d", "capped": "c"}
            fs = ", ".join(f"{f:.2f}{tag[s]}" for f, s in zip(p["flows"], p["status"]))
            cells.append(f"{fs} (**{p['mean']:.2f}**)")
        print(f"| {h['run']} ({h['file']}) | {h['L_m']} m | {h['h_code']} {h['motivation']} | {h['N_tracks']} / "
              f"{h['n_pass']} | {h['flow']:.2f} | " + " | ".join(cells) + " |")
    print("| mean | | | | %.2f | " % o["humans"]["flow"]["mean"]
          + " | ".join("%.2f" % o["cells"][c]["flow"]["mean"] for c in CELLS[:4]) + " |")
    print()
    for c in CELLS:
        d = o["cells"][c]
        lg = d["longest_gap"]
        print(c, "k/dl/cap", d["complete"], d["deadlock"], d["capped"], "ratio", sig(d["flow_ratio"]["ratio"]),
              [sig(v) for v in d["flow_ratio"]["ci95"]], "gap unc", sig(lg["uncensored_interior_mean"]),
              "cens", lg["n_censored"], "term>int", lg["n_terminal_is_longest"],
              "term mean", sig(lg["terminal_open"].get("mean") or 0), "LB mean", sig(lg["with_terminal_mean_lower_bound"]),
              "LB med", sig(lg["with_terminal_median_lower_bound"]), "KM med", lg["km_median"],
              "KM rmean", sig(lg["km_restricted_mean"]), "tau", sig(lg["km_tau"]), "S(tau)", sig(lg["km_S_at_tau"]))


if __name__ == "__main__":
    main()
