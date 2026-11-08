"""Shared statistics for the open-geometry analyses (experiments/E8/analyze.py, experiments/E9/analyze.py).

Pure numpy / scipy (system python3); does not import the simulator. Input rows are the records written by
experiments/lib/opengeo.open_run (one JSON line per run, job_id "<arm>|L<L>|seed<seed>").

Per cell (arm x start-block length L), cell():
  n, missing seeds; throughput_per_s (n_sunk / t_end, as recorded) mean, SD, 95% percentile bootstrap interval
  (NBOOT resamples of seeds); n_sunk mean; runs that ended before the window (every agent sunk); mean zone speed
  (mean over runs of mean_speed_zone); wall leaks (total agents, runs with >= 1, Wilson 95%); stall/standoff
  episodes (opengeo.events: >= 2 agents below 0.05 m/s, 1.0 m single linkage, in the zone, >= 2 s): runs with >= 1
  (Wilson 95%), episodes per run (mean, bootstrap 95%), total, formation rate per zone-occupied second (total
  episodes / total occupied s), median and max lifetime (s), fraction of episodes censored at the window end,
  median and max of the per-episode maximum size; LP infeasibility for ORCA arms: pooled rate (sum of infeasible
  LPs / sum of LP calls over the cell's runs, i.e. per agent-step with ORCA), the mean of the per-run rates with a
  bootstrap 95% interval, and the totals (published LP: 'pub_violated' / 'pub_calls' = constraints silently
  dropped; RVO2: 'rvo2_lp3' / 'rvo2_calls' = linearProgram3 used).
Gridlock (per run): the run used the whole window (t_end >= T - 0.05 s, so agents remain) AND either
  (a) a censored episode (still open at the window end) lasting >= GRID_S = 20 s, or
  (b) no agent sunk in the last GRID_S = 20 s of the window (throughput collapse; also true when nothing sank).
  Reported as the run count with Wilson 95%, and the counts of (a) and (b) separately.
Paired comparisons (paired()): arm against C1 on the same seed and L: mean difference arm - C1 with a bootstrap
  95% interval over seed pairs, ratio of means mean(arm) / mean(C1) with a paired bootstrap 95% interval (the same
  resampled seed pairs; resamples whose C1 mean is 0 are dropped), Wilcoxon signed-rank p (two-sided,
  zero_method 'wilcox'; null when every difference is 0). Pooled over L (pooled()): stratified bootstrap
  (seed pairs resampled within each L), difference = mean over all pairs, ratio = sum(arm) / sum(C1) over all pairs
  (equal n per level, so this is the ratio of the level-averaged means).
All intervals 95%. One generator numpy PCG64(12345) per script, consumed in the script's fixed cell / comparison
order; cells and comparisons without data consume nothing and report null (keys are always present, so the JSON
structure does not depend on which runs exist).
"""
import json

import numpy as np
from scipy.stats import wilcoxon

NBOOT = 2000
GRID_S = 20.0
SEEDS = list(range(42, 67))
RNG = np.random.Generator(np.random.PCG64(12345))


def lkey(L):
    return f"L{L:g}".replace(".", "p")


def load(path):
    """Rows keyed (arm, L) -> {seed: row}; duplicate job_ids keep the last line. Returns (by, n_lines, dup_ids)."""
    by, seen, dups, n = {}, set(), [], 0
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            if r["job_id"] in seen:
                dups.append(r["job_id"])
            seen.add(r["job_id"])
            by.setdefault((r["arm"], float(r["L"])), {})[int(r["seed"])] = r
    return by, n, dups


def wilson(k, n, z=1.96):
    if not n:
        return [None, None]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [float(max(0.0, c - h)), float(min(1.0, c + h))]


def boot_mean(x):
    x = np.asarray(x, float)
    if not len(x):
        return [None, None]
    idx = RNG.integers(0, len(x), size=(NBOOT, len(x)))
    m = x[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def _f(x):
    return None if x is None else float(x)


def gridlock(r):
    """(gridlock, censored_long, flow_stopped) for one run (definition in the module docstring)."""
    full = r["t_end"] >= r["T"] - 0.05
    cens_long = any(e["censored"] and e["dur"] >= GRID_S for e in r["events"])
    last = max((s[0] for s in r["sink_log"]), default=-np.inf)
    stopped = last < r["t_end"] - GRID_S
    return full and (cens_long or stopped), full and cens_long, full and stopped


def lp_fields(rows, kind):
    """kind: 'pub' (published LP, dropped constraints) | 'rvo2' (linearProgram3) | None (no ORCA)."""
    if kind is None:
        return None
    num, den = ("pub_violated", "pub_calls") if kind == "pub" else ("rvo2_lp3", "rvo2_calls")
    calls = sum(r["lp"][den] for r in rows)
    bad = sum(r["lp"][num] for r in rows)
    per = [r["lp"][num] / r["lp"][den] for r in rows if r["lp"][den]]
    return {"kind": "published_dropped_constraints" if kind == "pub" else "rvo2_linearProgram3",
            "rate": bad / calls if calls else None, "rate_pct": 100 * bad / calls if calls else None,
            "run_rate_mean": float(np.mean(per)) if per else None, "run_rate_ci95": boot_mean(per),
            "calls_total": int(calls), "infeasible_total": int(bad), "n_runs_with_calls": len(per)}


def cell(Rc, arm, L, lp_kind, ev_name):
    """Summary of one cell; Rc = {seed: row}. ev_name names the episode block ('stalls' or 'standoffs')."""
    missing = [s for s in SEEDS if s not in Rc]
    rows = [Rc[s] for s in SEEDS if s in Rc]
    n = len(rows)
    tp = [r["throughput_per_s"] for r in rows]
    sp = [r["mean_speed_zone"] for r in rows if r["mean_speed_zone"] is not None]
    lk = [r["n_leaked"] for r in rows]
    ev = [e for r in rows for e in r["events"]]
    nev = [len(r["events"]) for r in rows]
    durs = [e["dur"] for e in ev]
    sizes = [e["max_size"] for e in ev]
    occ = sum(r["zone_occupied_s"] for r in rows)
    k_ev = sum(v > 0 for v in nev)
    g = [gridlock(r) for r in rows]
    kg = sum(x[0] for x in g)
    return {
        "arm": arm, "L_m": L, "n": n, "missing_seeds": missing,
        "start_density_per_m2": rows[0]["start_density_per_m2"] if rows else None,
        "throughput": {"mean": float(np.mean(tp)) if n else None,
                       "sd": float(np.std(tp, ddof=1)) if n > 1 else None, "ci95": boot_mean(tp),
                       "min": _f(min(tp)) if n else None, "max": _f(max(tp)) if n else None},
        "n_sunk_mean": float(np.mean([r["n_sunk"] for r in rows])) if n else None,
        "runs_all_sunk_before_window": sum(r["t_end"] < r["T"] - 0.05 for r in rows),
        "mean_speed_zone": {"mean": float(np.mean(sp)) if sp else None,
                            "sd": float(np.std(sp, ddof=1)) if len(sp) > 1 else None, "n": len(sp)},
        "leaks": {"total": int(sum(lk)), "runs_with": sum(v > 0 for v in lk), "runs_with_wilson95": wilson(
            sum(v > 0 for v in lk), n)},
        ev_name: {"runs_with": k_ev, "runs_with_wilson95": wilson(k_ev, n),
                  "per_run_mean": float(np.mean(nev)) if n else None, "per_run_ci95": boot_mean(nev),
                  "total": int(sum(nev)),
                  "formation_rate_per_occupied_s": sum(nev) / occ if occ else None,
                  "lifetime_median_s": float(np.median(durs)) if durs else None,
                  "lifetime_max_s": float(max(durs)) if durs else None,
                  "n_censored": sum(bool(e["censored"]) for e in ev),
                  "frac_censored": sum(bool(e["censored"]) for e in ev) / len(ev) if ev else None,
                  "size_median": float(np.median(sizes)) if sizes else None,
                  "size_max": int(max(sizes)) if sizes else None},
        "gridlock": {"runs": kg, "wilson95": wilson(kg, n), "runs_censored_ge_20s": sum(x[1] for x in g),
                     "runs_no_sink_last_20s": sum(x[2] for x in g)},
        "lp": lp_fields(rows, lp_kind),
        "_tp": {s: Rc[s]["throughput_per_s"] for s in SEEDS if s in Rc},
    }


NULL_CMP = {"n_pairs": 0, "arm_mean": None, "c1_mean": None, "diff": None, "diff_ci95": [None, None],
            "ratio": None, "ratio_ci95": [None, None], "wilcoxon_p": None, "levels": []}


def _boot_pairs(strata):
    """strata: list of (a, b) arrays (paired). Stratified bootstrap of (pooled diff, pooled ratio)."""
    D, Q = np.empty(NBOOT), np.empty(NBOOT)
    idx = [RNG.integers(0, len(a), size=(NBOOT, len(a))) for a, _ in strata]
    sa = sum(a[i].sum(axis=1) for (a, _), i in zip(strata, idx))
    sb = sum(b[i].sum(axis=1) for (_, b), i in zip(strata, idx))
    npair = sum(len(a) for a, _ in strata)
    D = (sa - sb) / npair
    with np.errstate(divide="ignore", invalid="ignore"):
        Q = np.where(sb > 0, sa / np.where(sb > 0, sb, 1), np.nan)
    Q = Q[np.isfinite(Q)]
    pct = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) else [None, None]  # noqa
    return pct(D), pct(Q)


def compare(cells_by_L, arm, ref="C1"):
    """cells_by_L: {L: {arm: cell}}. Paired comparison arm vs ref per L and pooled over the L with pairs."""
    per, strata, lv = {}, [], []
    for L, cs in cells_by_L.items():
        A, B = cs[arm]["_tp"], cs[ref]["_tp"]
        s = sorted(set(A) & set(B))
        if not s:
            per[lkey(L)] = dict(NULL_CMP)
            continue
        a, b = np.array([A[k] for k in s]), np.array([B[k] for k in s])
        dci, qci = _boot_pairs([(a, b)])
        d = a - b
        p = float(wilcoxon(a, b, zero_method="wilcox").pvalue) if np.count_nonzero(d) else None
        per[lkey(L)] = {"n_pairs": len(s), "arm_mean": float(a.mean()), "c1_mean": float(b.mean()),
                        "diff": float(d.mean()), "diff_ci95": dci,
                        "ratio": float(a.sum() / b.sum()) if b.sum() > 0 else None, "ratio_ci95": qci,
                        "wilcoxon_p": p, "levels": [L]}
        strata.append((a, b))
        lv.append(L)
    if not strata:
        return per, dict(NULL_CMP)
    dci, qci = _boot_pairs(strata)
    a, b = np.concatenate([x for x, _ in strata]), np.concatenate([y for _, y in strata])
    d = a - b
    pooled = {"n_pairs": len(a), "arm_mean": float(a.mean()), "c1_mean": float(b.mean()), "diff": float(d.mean()),
              "diff_ci95": dci, "ratio": float(a.sum() / b.sum()) if b.sum() > 0 else None, "ratio_ci95": qci,
              "wilcoxon_p": float(wilcoxon(a, b, zero_method="wilcox").pvalue) if np.count_nonzero(d) else None,
              "levels": lv}
    return per, pooled


def strip(cells):
    for cs in cells.values():
        for c in cs.values():
            c.pop("_tp", None)
    return cells
