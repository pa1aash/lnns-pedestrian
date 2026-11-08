"""E9 analysis: open 90-degree crossing, corrected-forward (CF), 100 + 100 agents, line goals, 60 s window.

  python3 experiments/E9/analyze.py [--in data/E9/e9_crossing.jsonl] [--out data/derived/E9_analysis.json]

Input: experiments/E9/e9_crossing.py (opengeo.open_run records). Arms C1, C2, C3_rvo2, C4_rvo2 (crush off);
start-block lengths L in {17, 25, 34} m (start densities 1.96, 1.33, 0.98 m^-2); seeds 42-66, the same seeds in
every cell, so arms are paired by seed at each L. Partial input is allowed: every cell and comparison of the full
design is present in the JSON, with n = 0 / null where runs are missing.

Method (experiments/lib/openstats.py, which carries the full definitions):
  per cell: n; throughput (sunk agents / t_end, per s) mean with a 95% percentile bootstrap interval (2000
  resamples of seeds, numpy PCG64(12345), one generator, consumed in the fixed cell then comparison order); exits
  per run (n_sunk, the conference's "exits per 200 agents in 60 s"); mean speed in the crossing zone [3.2, 6.8]^2;
  wall leaks (total, runs with >= 1); standoffs (>= 2 agents below 0.05 m/s within 1.0 m single linkage in the
  crossing zone, persisting >= 2 s): runs with >= 1 (Wilson 95%), standoffs per run (bootstrap 95%), formation rate
  per zone-occupied second, median / max lifetime, fraction censored at the window end, median / max size; RVO2 LP
  infeasibility per agent-step (linearProgram3 used) for C3_rvo2 and C4_rvo2; gridlock runs = the window ran to
  the end with agents left AND (a censored standoff >= 20 s OR no agent sunk in the last 20 s).
  paired by seed and L: C2, C3_rvo2, C4_rvo2 each against C1: ratio of mean throughputs arm / C1 with a paired
  bootstrap 95% interval over seed pairs, mean difference with a bootstrap 95% interval, Wilcoxon signed-rank p;
  pooled over L by a stratified bootstrap (seed pairs resampled within each L; ratio = sum / sum).
Verdict on the conference claim "TTC (C2) triples crossing throughput (C2 16.1 vs C1 5.9 exits per 200 agents in
  60 s; IRR 2.72)", on the pooled C2/C1 ratio interval [lo, hi]:
  withdrawn if lo <= 1 (interval includes 1) or hi < 1.5; else confirmed if lo <= 2.72 <= hi or lo > 2;
  else revised (an effect above 1 but not a tripling). null (pending) when no C2-C1 pairs exist.
  The per-L verdicts use the same rule on each level's interval.
Keys avoid '.' (registry key paths split on '.'): L = 17 is stored as L17; comparison "<arm>_over_c1".
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import openstats as S  # noqa: E402

IN = os.path.join(ROOT, "data", "E9", "e9_crossing.jsonl")
OUT = os.path.join(ROOT, "data", "derived", "E9_analysis.json")
ARMS = ("C1", "C2", "C3_rvo2", "C4_rvo2")
LP = {"C1": None, "C2": None, "C3_rvo2": "rvo2", "C4_rvo2": "rvo2"}
LENGTHS = (17.0, 25.0, 34.0)
COMPARE = ("C2", "C3_rvo2", "C4_rvo2")
CONFERENCE = {"claim": "TTC (C2) triples crossing throughput", "c2_exits": 16.1, "c1_exits": 5.9,
              "per": "200 agents in 60 s", "irr": 2.72}


def status(cmp):
    lo, hi = cmp["ratio_ci95"]
    if not cmp["n_pairs"] or lo is None:
        return None
    if lo <= 1.0 or hi < 1.5:
        return "withdrawn"
    if lo <= CONFERENCE["irr"] <= hi or lo > 2.0:
        return "confirmed"
    return "revised"


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
    T = {r["T"] for v in by.values() for r in v.values()}
    if T and T != {60.0}:
        anomalies.append(f"window lengths {sorted(T)} s, not 60 s (smoke / scaled input?)")
    cells, by_L = {}, {}
    for L in LENGTHS:
        for arm in ARMS:
            c = S.cell(by.get((arm, L), {}), arm, L, LP[arm], "standoffs")
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
    p = pooled["c2_over_c1"]
    st = status(p)
    if st is None:
        ev = "no C2-C1 seed pairs yet"
    else:
        lv = [S.lkey(L) for L in p["levels"]]
        e1 = sum(cells["C1"][k]["n_sunk_mean"] * cells["C1"][k]["n"] for k in lv) / sum(cells["C1"][k]["n"] for k in lv)
        e2 = sum(cells["C2"][k]["n_sunk_mean"] * cells["C2"][k]["n"] for k in lv) / sum(cells["C2"][k]["n"] for k in lv)
        ev = (f"C2/C1 throughput {p['ratio']:.2f} [{p['ratio_ci95'][0]:.2f}, {p['ratio_ci95'][1]:.2f}] pooled over "
              f"L = {', '.join(f'{L:g}' for L in p['levels'])} m ({p['n_pairs']} seed pairs; exits per run C2 {e2:.1f} "
              f"vs C1 {e1:.1f}; leaks {sum(cells[x][k]['leaks']['total'] for x in ('C1', 'C2') for k in lv)}) "
              f"against the printed 2.72")
    verdict = {"conference": CONFERENCE, "status": st, "evidence": ev,
               # decision C64: Table 4 judges each claim on the conference's model (published ORCA). This claim is
               # C2 (SFM + TTC) against C1 and involves no ORCA, so the solver does not enter; the ORCA arms
               # (C3, C4) were run with RVO2 only and are reported as context.
               "solver": {"headline": "not involved (C2 vs C1)", "orca_arms": "rvo2 only"},
               "per_L": {S.lkey(L): status(paired[S.lkey(L)]["c2_over_c1"]) for L in LENGTHS},
               "rule": ("pooled C2/C1 ratio interval [lo, hi]: withdrawn if lo <= 1 or hi < 1.5; confirmed if "
                        "lo <= 2.72 <= hi or lo > 2; else revised"),
               "gridlock_definition": (f"window ran to the end with agents left AND (censored standoff >= "
                                       f"{S.GRID_S:g} s OR no agent sunk in the last {S.GRID_S:g} s)")}
    tot = lambda arm, f: sum(f(cells[arm][S.lkey(L)]) for L in LENGTHS)  # noqa: E731
    totals = {arm: {"n": tot(arm, lambda c: c["n"]), "leaks": tot(arm, lambda c: c["leaks"]["total"]),
                    "runs_with_standoff": tot(arm, lambda c: c["standoffs"]["runs_with"]),
                    "standoffs": tot(arm, lambda c: c["standoffs"]["total"]),
                    "gridlock_runs": tot(arm, lambda c: c["gridlock"]["runs"])} for arm in ARMS}
    for arm in ARMS:      # LP infeasibility pooled over L: sum of infeasible LPs / sum of LP calls
        ls = [cells[arm][S.lkey(L)]["lp"] for L in LENGTHS]
        calls = sum(x["calls_total"] for x in ls) if LP[arm] else 0
        totals[arm]["lp_rate_pct"] = 100 * sum(x["infeasible_total"] for x in ls) / calls if calls else None
    totals["all"] = {"n": sum(t["n"] for t in totals.values()), "leaks": sum(t["leaks"] for t in totals.values())}
    complete = all(cells[arm][S.lkey(L)]["n"] == len(S.SEEDS) for arm in ARMS for L in LENGTHS)
    out = {"script": "experiments/E9/analyze.py", "doc": __doc__, "source": os.path.abspath(a.inp),
           "n_lines": n_lines, "complete": complete, "seeds": [S.SEEDS[0], S.SEEDS[-1]], "n_bootstrap": S.NBOOT,
           "rng": "PCG64(12345)", "window_s": 60.0, "gridlock_s": S.GRID_S, "cells": S.strip(cells),
           "totals": totals, "paired": paired, "pooled": pooled, "verdict": verdict, "anomalies": anomalies}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)

    fm = lambda x, f="{:.3f}": "-" if x is None else f.format(x)  # noqa: E731
    for L in LENGTHS:
        for arm in ARMS:
            c = cells[arm][S.lkey(L)]
            t, st_, lp = c["throughput"], c["standoffs"], c["lp"]
            print(f"L={L:4.0f} {arm:8s} n={c['n']:2d} tp={fm(t['mean'])} [{fm(t['ci95'][0])},{fm(t['ci95'][1])}] "
                  f"exits={fm(c['n_sunk_mean'], '{:.1f}')} v={fm(c['mean_speed_zone']['mean'])} "
                  f"leaks={c['leaks']['total']} standoffs runs={st_['runs_with']} tot={st_['total']} "
                  f"med={fm(st_['lifetime_median_s'], '{:.1f}')} cens={st_['n_censored']} grid={c['gridlock']['runs']} "
                  f"lp={fm(lp['rate'] if lp else None, '{:.4f}')}")
    for k, d in list(paired.items()) + [("pooled", pooled)]:
        for name, v in d.items():
            if v["n_pairs"]:
                print(f"{k:6s} {name:16s} n={v['n_pairs']:2d} ratio={fm(v['ratio'])} [{fm(v['ratio_ci95'][0])},"
                      f"{fm(v['ratio_ci95'][1])}] diff={v['diff']:+.3f} p={fm(v['wilcoxon_p'], '{:.3g}')}")
    print("verdict:", st, "-", ev)
    print("anomalies:", anomalies or "none")


if __name__ == "__main__":
    main()
