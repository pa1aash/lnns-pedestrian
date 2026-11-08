"""E8 analysis: open bidirectional corridor (counterflow), corrected-forward (CF), 50 + 50 agents, 60 s window.

  python3 experiments/E8/analyze.py [--in data/E8/e8_counterflow.jsonl] [--out data/derived/E8_analysis.json]

Input: experiments/E8/e8_counterflow.py (opengeo.open_run records). Arms C1, C2, C3_pub (published ORCA), C3_rvo2,
C4_rvo2 (crush off); start-block lengths L in {12, 18, 30} m (start densities 1.39, 0.93, 0.56 m^-2); seeds 42-66,
the same seeds in every cell, so arms are paired by seed at each L. Partial input is allowed: every cell and
comparison of the full design is present in the JSON, with n = 0 / null where runs are missing.

Method (experiments/lib/openstats.py, which carries the full definitions):
  per cell: n; throughput (sunk agents / t_end, per s) mean with a 95% percentile bootstrap interval (2000
  resamples of seeds, numpy PCG64(12345), one generator, consumed in the fixed cell then comparison order); mean
  speed in the measurement section x in [0, 20] m; wall leaks (total, runs with >= 1); stall episodes (>= 2 agents
  below 0.05 m/s within 1.0 m single linkage in the section, persisting >= 2 s): runs with >= 1 (Wilson 95%),
  episodes per run (bootstrap 95%), median / max lifetime, fraction censored at the window end, median / max size;
  LP infeasibility per agent-step with ORCA (C3_pub: the published LP returned a velocity violating a half-plane,
  i.e. constraints were dropped; C3_rvo2, C4_rvo2: RVO2 linearProgram3 used); gridlock runs = the window ran to the
  end with agents left AND (a censored stall >= 20 s OR no agent sunk in the last 20 s).
  paired by seed and L: C3_rvo2, C3_pub, C4_rvo2, C2 each against C1: mean throughput difference (arm - C1) with a
  bootstrap 95% interval over seed pairs, ratio of means arm / C1 with a paired bootstrap 95% interval, Wilcoxon
  signed-rank p; pooled over L by a stratified bootstrap (seed pairs resampled within each L; ratio = sum / sum).
Verdict on the conference claim "ORCA (C3) gridlocks counterflow / reduces counterflow throughput (coefficient
  -5.0, p_HS = 0.598)", evaluated on the pooled comparison for C3_pub (the published LP, the solver the conference
  used, here in the corrected leak-free geometry; headline, decision C64) and, as the solver check, for C3_rvo2;
  "solvers_agree" records whether the two statuses match. Two parts: (i) reduction = the pooled C3 - C1 difference interval lies below 0;
  (ii) gridlock = C3 has >= 1 gridlock run and more gridlock runs than C1 (pooled over L).
  confirmed: (i) and (ii). withdrawn: C3 pooled mean >= C1 pooled mean, or neither (i) nor (ii).
  revised: exactly one of (i), (ii) holds with the C3 mean below C1. null (pending) when the pairs are absent.
Keys avoid '.' (registry key paths split on '.'): L = 12 is stored as L12; comparison "<arm>_over_c1".
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import openstats as S  # noqa: E402

IN = os.path.join(ROOT, "data", "E8", "e8_counterflow.jsonl")
OUT = os.path.join(ROOT, "data", "derived", "E8_analysis.json")
ARMS = ("C1", "C2", "C3_rvo2", "C4_rvo2", "C3_pub")
LP = {"C1": None, "C2": None, "C3_rvo2": "rvo2", "C4_rvo2": "rvo2", "C3_pub": "pub"}
LENGTHS = (12.0, 18.0, 30.0)
COMPARE = ("C3_rvo2", "C3_pub", "C4_rvo2", "C2")
CONFERENCE = {"claim": "ORCA (C3) gridlocks counterflow / reduces counterflow throughput",
              "coefficient": -5.0, "p_HS": 0.598}


def verdict_one(pooled, cells, arm):
    if not pooled["n_pairs"]:
        return {"status": None, "reduction_significant": None, "gridlock_excess": None,
                "gridlock_runs_c3": None, "gridlock_runs_c1": None, "evidence": f"{arm}: no paired runs yet"}
    lv = [S.lkey(L) for L in pooled["levels"]]
    g3 = sum(cells[arm][k]["gridlock"]["runs"] for k in lv)
    g1 = sum(cells["C1"][k]["gridlock"]["runs"] for k in lv)
    red = pooled["diff_ci95"][1] is not None and pooled["diff_ci95"][1] < 0
    grid = g3 >= 1 and g3 > g1
    if pooled["diff"] >= 0 or not (red or grid):
        st = "withdrawn"
    elif red and grid:
        st = "confirmed"
    else:
        st = "revised"
    lo, hi = pooled["diff_ci95"]
    q, (qlo, qhi) = pooled["ratio"], pooled["ratio_ci95"]
    n1 = sum(cells["C1"][k]["n"] for k in lv)
    ev = (f"{arm}/C1 throughput {q:.2f} [{qlo:.2f}, {qhi:.2f}] pooled over L = "
          f"{', '.join(f'{L:g}' for L in pooled['levels'])} m (diff {pooled['diff']:+.3f} [{lo:+.3f}, {hi:+.3f}] "
          f"sunk/s, {pooled['n_pairs']} seed pairs); gridlock runs {arm} {g3} vs C1 {g1} of {n1}")
    return {"status": st, "reduction_significant": red, "gridlock_excess": grid,
            "gridlock_runs_c3": g3, "gridlock_runs_c1": g1, "evidence": ev}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=IN)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    by, n_lines, dups = S.load(a.inp)
    anomalies = [f"duplicate job_id {d}" for d in dups]
    extra = sorted(k for k in by if k[0] not in ARMS or k[1] not in LENGTHS)
    if extra:
        anomalies.append(f"cells outside the design ignored: {extra}")
    cells, by_L = {}, {}
    for L in LENGTHS:
        for arm in ARMS:
            c = S.cell(by.get((arm, L), {}), arm, L, LP[arm], "stalls")
            cells.setdefault(arm, {})[S.lkey(L)] = c
            by_L.setdefault(L, {})[arm] = c
            if c["n"] and c["missing_seeds"]:
                anomalies.append(f"{arm}|L{L:g}: {len(c['missing_seeds'])} seeds missing")
            if c["leaks"]["total"]:
                anomalies.append(f"{arm}|L{L:g}: {c['leaks']['total']} wall leaks")
    paired, pooled = {S.lkey(L): {} for L in LENGTHS}, {}
    for arm in COMPARE:
        per, pool = S.compare(by_L, arm)
        name = f"{arm.lower()}_over_c1"
        for k, v in per.items():
            paired[k][name] = v
        pooled[name] = pool
    v_rvo2 = verdict_one(pooled["c3_rvo2_over_c1"], cells, "C3_rvo2")
    v_pub = verdict_one(pooled["c3_pub_over_c1"], cells, "C3_pub")
    agree = None if v_pub["status"] is None or v_rvo2["status"] is None else v_pub["status"] == v_rvo2["status"]
    verdict = {"conference": CONFERENCE, "status": v_pub["status"], "evidence": v_pub["evidence"],
               "headline_arm": "C3_pub", "solver_check_arm": "C3_rvo2", "c3_pub": v_pub, "c3_rvo2": v_rvo2,
               "solvers_agree": agree,
               "rule": ("(i) pooled C3 - C1 throughput interval below 0; (ii) C3 gridlock runs >= 1 and > C1. "
                        "confirmed: (i) and (ii); withdrawn: C3 mean >= C1 or neither; revised: exactly one."),
               "gridlock_definition": (f"window ran to the end with agents left AND (censored stall >= {S.GRID_S:g} s "
                                       f"OR no agent sunk in the last {S.GRID_S:g} s)")}
    tot = lambda arm, f: sum(f(cells[arm][S.lkey(L)]) for L in LENGTHS)  # noqa: E731
    totals = {arm: {"n": tot(arm, lambda c: c["n"]), "leaks": tot(arm, lambda c: c["leaks"]["total"]),
                    "runs_with_stall": tot(arm, lambda c: c["stalls"]["runs_with"]),
                    "stalls": tot(arm, lambda c: c["stalls"]["total"]),
                    "gridlock_runs": tot(arm, lambda c: c["gridlock"]["runs"])} for arm in ARMS}
    for arm in ARMS:      # LP infeasibility pooled over L: sum of infeasible LPs / sum of LP calls
        ls = [cells[arm][S.lkey(L)]["lp"] for L in LENGTHS]
        calls = sum(x["calls_total"] for x in ls) if LP[arm] else 0
        totals[arm]["lp_rate_pct"] = 100 * sum(x["infeasible_total"] for x in ls) / calls if calls else None
    totals["all"] = {"n": sum(t["n"] for t in totals.values()), "leaks": sum(t["leaks"] for t in totals.values())}
    complete = all(cells[arm][S.lkey(L)]["n"] == len(S.SEEDS) for arm in ARMS for L in LENGTHS)
    out = {"script": "experiments/E8/analyze.py", "doc": __doc__, "source": os.path.abspath(a.inp),
           "n_lines": n_lines, "complete": complete, "seeds": [S.SEEDS[0], S.SEEDS[-1]], "n_bootstrap": S.NBOOT,
           "rng": "PCG64(12345)", "window_s": 60.0, "gridlock_s": S.GRID_S, "cells": S.strip(cells),
           "totals": totals, "paired": paired, "pooled": pooled, "verdict": verdict, "anomalies": anomalies}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)

    fm = lambda x, f="{:.3f}": "-" if x is None else f.format(x)  # noqa: E731
    for L in LENGTHS:
        for arm in ARMS:
            c = cells[arm][S.lkey(L)]
            t, st, lp = c["throughput"], c["stalls"], c["lp"]
            print(f"L={L:4.0f} {arm:8s} n={c['n']:2d} tp={fm(t['mean'])} [{fm(t['ci95'][0])},{fm(t['ci95'][1])}] "
                  f"v={fm(c['mean_speed_zone']['mean'])} leaks={c['leaks']['total']} stalls runs={st['runs_with']} "
                  f"tot={st['total']} med={fm(st['lifetime_median_s'], '{:.1f}')} max={fm(st['lifetime_max_s'], '{:.1f}')} "
                  f"cens={st['n_censored']} grid={c['gridlock']['runs']} "
                  f"lp={fm(lp['rate'] if lp else None, '{:.4f}')}")
    for k, d in list(paired.items()) + [("pooled", pooled)]:
        for name, v in d.items():
            if v["n_pairs"]:
                print(f"{k:6s} {name:16s} n={v['n_pairs']:2d} diff={v['diff']:+.3f} {fm(v['diff_ci95'][0])},"
                      f"{fm(v['diff_ci95'][1])} ratio={fm(v['ratio'])} [{fm(v['ratio_ci95'][0])},"
                      f"{fm(v['ratio_ci95'][1])}] p={fm(v['wilcoxon_p'], '{:.3g}')}")
    print("verdict:", verdict["status"], "-", verdict["evidence"], "| C3_pub:", v_pub["status"])
    print("anomalies:", anomalies or "none")


if __name__ == "__main__":
    main()
