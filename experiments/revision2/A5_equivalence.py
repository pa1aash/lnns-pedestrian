"""A5: equivalence (TOST) of the freed fraction, surrogate against force-coupled ORCA, and the window of horizons.

Inputs (existing data only; the outcome at horizon T is read off the recorded exit time, exit time <= T)
  data/E2/e2_quench.jsonl + data/derived/selection.json   34 lone keystones, 26 second traps (E2 arms
        noise0.07 = SFM + sigma 0.07 m/s, 5 seeds; C3_rvo2, C3_pub = force-coupled ORCA, unperturbed run)
  data/N1/n1.jsonl                       lone keystones, sigma = 0.0717 m/s, 20 seeds per snapshot
  data/revision/A5/a5_quench.jsonl       the 134 second traps E2 did not draw (A5x; same arms); pooled with
                                         E2's 26 to 160
  data/E6/e6a.jsonl, data/E6/e6b.jsonl   whole runs, seeds 242-427 (186): ORCA (RVO2) and SFM + sigma* = 0.0467 m/s
  data/E7b/e7b_quench.jsonl, data/E7b_bstar/bstar_quench.jsonl   46 pair standoffs: C3_pub, C3_rvo2 and the
                                         bias arms bstar_pub+ (+b*_legacy), bstar_rvo2+ (+b*_RVO2)
Loaders follow experiments/revision/A7_paired.py and A8_horizon.py (freed: blocker exit time <= T; pairs: freed
and first member exit first_t <= T; whole runs: complete and evacuation_time <= T).
Output: data/derived/rev2_A5.json

Method
  Unit: the snapshot (the spawn seed for whole runs). Per unit i, d_i(T) = p_i(T) - c_i(T), where p_i is the
  surrogate's freed fraction over its seeds (noise; the unperturbed run for the bias) and c_i in {0, 1} is ORCA's
  unperturbed outcome. Delta(T) = mean_i d_i(T): the paired difference in freed fraction, surrogate minus ORCA.
  Intervals: (a) cluster bootstrap over units (whole snapshots with all their seeds resampled together),
  10 000 percentile resamples, a fresh numpy Generator(PCG64(12345)) per comparison, the same resample matrix
  at every T; (b) the paired t interval on the per-unit d_i (df = n - 1). The bootstrap is the primary interval.
  Equivalence: margin +-0.10 in freed fraction. TOST at the 5% level: equivalent when the 90% interval lies inside
  (-0.10, +0.10); the TOST p (the larger of the two one-sided paired t p-values) is stored beside. The 95% interval
  inside the margin is reported as well.
  Margin: 0.10 is about the 95% binomial half-width of ORCA's own freed fraction on the smaller samples (34-46
  snapshots, Wilson half-widths stored per comparison), so a smaller margin asks for a precision the reference
  measurement does not have; it is 3-5 snapshots out of 34-46.
  Horizon scan: T = 1, 2, ..., 120 s (snapshots, pairs) and T = 5, 10, ..., 600 s (whole runs). window_equiv90:
  the T at which the 90% bootstrap interval lies inside the margin, written as closed intervals of the grid;
  the window containing the nominal horizon (120 s or 600 s) is named separately. T at which both arms free
  fewer than 10% of units is flagged as degenerate ("trivial_T_s": equivalence there holds because nothing is
  freed yet). A bound equal to the margin (to 1e-9) counts as outside.
Comparisons (surrogate first): lone_E2, lone_N1, second_E2, second_pool (vs ORCA RVO2); second_E2_legacy,
  second_pool_legacy (the same noise vs ORCA legacy, supplementary); whole_E6 (E6b vs E6a); pair_legacy
  (+b*_legacy vs ORCA legacy), pair_rvo2 (+b*_RVO2 vs ORCA RVO2).
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev2lib  # noqa: E402
from rev2lib import DATA, DERIVED, sig, wilson  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

B = 10000
SEED = 12345
MARGIN = 0.10
T_Q, T_W = 120.0, 600.0
GRID_SNAP = np.arange(1.0, 121.0, 1.0)
GRID_WHOLE = np.arange(5.0, 601.0, 5.0)


def jl(p):
    return [json.loads(ln) for ln in open(p) if ln.strip()]


# ------------------------------------------------------------------ loading (exit times; None = no exit)
def load_snapshots():
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]
    snaps = {s["tag"]: s for s in sel}
    ex = defaultdict(dict)                       # ex[(tag, arm)][rep] = blocker exit time or None
    for r in jl(os.path.join(DATA, "E2", "e2_quench.jsonl")):
        tag, arm, rep = r["job_id"].split("|")
        if arm in ("noise0.07", "C3_rvo2", "C3_pub"):
            ex[(tag, arm)][rep] = r["exits"].get(str(snaps[tag]["blocker"]))
    for r in jl(os.path.join(DATA, "N1", "n1.jsonl")):
        tag = r["job_id"].split("|")[0]
        ex[(tag, "N1")][str(r["rep"])] = r["exits"].get(str(snaps[tag]["blocker"]))
    new = []
    for r in jl(os.path.join(DATA, "revision", "A5", "a5_quench.jsonl")):
        tag, arm, rep = r["job_id"].split("|")
        if arm in ("noise0.07", "C3_rvo2", "C3_pub"):
            assert tag not in snaps
            ex[(tag, arm)][rep] = r["exits"].get(str(r["blocker"]))
            new.append(tag)
    lone = [s["tag"] for s in sel if s["class"] == "lone_keystone"]
    second = [s["tag"] for s in sel if s["class"] == "lone_keystone_second_trap"]
    new = sorted(set(new))
    assert len(lone) == 34 and len(second) == 26 and len(new) == 134
    return ex, lone, second, new


def load_pairs():
    first = {}
    for p in (os.path.join(DATA, "E7b", "e7b_quench.jsonl"), os.path.join(DATA, "E7b_bstar", "bstar_quench.jsonl")):
        for r in jl(p):
            tag, arm, rep = r["job_id"].split("|")
            if rep == "u" and arm in ("C3_pub", "C3_rvo2", "bstar_pub+", "bstar_rvo2+"):
                first[(tag, arm)] = r["first_t"] if r["freed"] else None
    tags = sorted({t for t, _ in first}, key=lambda t: int(t.rsplit("seed", 1)[1]))
    assert len(tags) == 46
    return first, tags


def load_whole():
    A = {r["seed"]: r for r in jl(os.path.join(DATA, "E6", "e6a.jsonl"))}
    Bn = {r["seed"]: r for r in jl(os.path.join(DATA, "E6", "e6b.jsonl"))}
    seeds = sorted(A)
    assert seeds == sorted(Bn) and len(seeds) == 186 and seeds[0] == 242 and seeds[-1] == 427
    t = lambda r: r["evacuation_time"] if r["complete"] else None  # noqa: E731
    return {s: t(A[s]) for s in seeds}, {s: t(Bn[s]) for s in seeds}, Bn[seeds[0]]["sigma"]


# ------------------------------------------------------------------ statistics
def freed_at(times, grid):
    """times: list per unit of lists of exit times (None held) -> per-unit freed fraction, shape (n, len(grid))."""
    out = np.zeros((len(times), len(grid)))
    for i, ts in enumerate(times):
        a = np.array([np.inf if x is None else x for x in ts], float)
        out[i] = (a[:, None] <= grid[None, :] + 1e-9).mean(0)
    return out


def tost_t(d):
    n = len(d)
    m, s = float(np.mean(d)), float(np.std(d, ddof=1))
    if s == 0:
        return {"mean": m, "ci95": [m, m], "ci90": [m, m], "p_tost": 0.0 if abs(m) < MARGIN else 1.0}
    se = s / np.sqrt(n)
    q95, q90 = stats.t.ppf(0.975, n - 1), stats.t.ppf(0.95, n - 1)
    p_lo = 1 - stats.t.cdf((m + MARGIN) / se, n - 1)       # H0: Delta <= -margin
    p_hi = stats.t.cdf((m - MARGIN) / se, n - 1)           # H0: Delta >= +margin
    return {"mean": m, "se": se, "ci95": [m - q95 * se, m + q95 * se], "ci90": [m - q90 * se, m + q90 * se],
            "p_tost": float(max(p_lo, p_hi)), "p_lower": float(p_lo), "p_upper": float(p_hi)}


TOL = 1e-9      # a bound equal to the margin (exactly -0.10 on these grids) counts as outside


def inside(ci):
    return bool(-MARGIN + TOL < ci[0] and ci[1] < MARGIN - TOL)


def intervals(grid, mask):
    out, start = [], None
    for g, m in zip(grid, mask):
        if m and start is None:
            start = g
        if not m and start is not None:
            out.append([float(start), float(prev)])
            start = None
        prev = g
    if start is not None:
        out.append([float(start), float(prev)])
    return out


def compare(sur_times, orca_times, grid, horizon, label):
    P = freed_at(sur_times, grid)
    C = freed_at(orca_times, grid)
    D = P - C                                                   # (n, nT)
    n = D.shape[0]
    rng = np.random.Generator(np.random.PCG64(SEED))
    idx = rng.integers(0, n, (B, n))
    W = np.zeros((B, n))
    np.add.at(W, (np.repeat(np.arange(B), n), idx.ravel()), 1.0)
    M = W @ D / n                                               # (B, nT) bootstrap means
    lo95, hi95 = np.percentile(M, 2.5, 0), np.percentile(M, 97.5, 0)
    lo90, hi90 = np.percentile(M, 5.0, 0), np.percentile(M, 95.0, 0)
    delta = D.mean(0)
    eq90 = (lo90 > -MARGIN + TOL) & (hi90 < MARGIN - TOL)
    eq95 = (lo95 > -MARGIN + TOL) & (hi95 < MARGIN - TOL)
    j = int(np.argmin(np.abs(grid - horizon)))
    tt = tost_t(D[:, j])
    k_orca = int(round(C[:, j].sum()))
    w = wilson(k_orca, n)
    orca_exits = [x for ts in orca_times for x in ts if x is not None and x <= horizon + 1e-9]
    t_first = float(min(orca_exits)) if orca_exits else None
    t_last = float(max(orca_exits)) if orca_exits else None
    trivial = (P.mean(0) < MARGIN) & (C.mean(0) < MARGIN)     # both arms free < 10%: equivalence is degenerate
    w90 = intervals(grid, eq90)
    w95 = intervals(grid, eq95)
    nominal = next((iv for iv in w90 if iv[0] <= horizon <= iv[1]), None)
    nominal95 = next((iv for iv in w95 if iv[0] <= horizon <= iv[1]), None)
    nt = [iv for iv in intervals(grid, eq90 & ~trivial)]
    r = {"label": label, "n_units": n, "horizon_s": horizon,
         "surrogate_fraction": float(P[:, j].mean()), "orca_fraction": float(C[:, j].mean()),
         "orca_freed": k_orca, "orca_wilson95": [float(w[1]), float(w[2])],
         "orca_wilson_halfwidth": float((w[2] - w[1]) / 2),
         "delta": float(delta[j]), "boot_ci95": [float(lo95[j]), float(hi95[j])],
         "boot_ci90": [float(lo90[j]), float(hi90[j])],
         "t_ci95": tt["ci95"], "t_ci90": tt["ci90"], "p_tost_t": tt["p_tost"],
         "equivalent_tost_boot90": bool(eq90[j]), "equivalent_tost_t90": inside(tt["ci90"]),
         "inside_margin_boot95": bool(eq95[j]), "inside_margin_t95": inside(tt["ci95"]),
         "covers_zero_boot95": bool(lo95[j] <= 0 <= hi95[j]),
         "boot95_touches_margin": bool(min(abs(lo95[j] + MARGIN), abs(hi95[j] - MARGIN)) <= TOL),
         "orca_first_exit_s": t_first, "orca_last_exit_s": t_last,
         "trivial_T_s": intervals(grid, trivial),
         "window_equiv90_s": w90, "window_equiv90_nontrivial_s": nt, "window_inside95_s": w95,
         "window_at_horizon_equiv90_s": nominal, "window_at_horizon_inside95_s": nominal95,
         "scan": {f"{g:g}": [float(delta[i]), float(lo90[i]), float(hi90[i]), float(lo95[i]), float(hi95[i])]
                  for i, g in enumerate(grid)}}
    r["window_at_horizon_from_s"] = nominal[0] if nominal else None
    r["window_at_horizon_to_s"] = nominal[1] if nominal else None
    r["window95_at_horizon_from_s"] = nominal95[0] if nominal95 else None
    r["n_windows_equiv90_nontrivial"] = len(nt)
    for kk in ("delta",):
        r[kk + "_2sf"] = sig(r[kk], 2)
    r["p_tost_disp"] = rev2lib.pdisp(r["p_tost_t"])
    return r


def main():
    ex, lone, second, new = load_snapshots()
    pool = second + new

    def noise(tags, arm, reps):
        return [[ex[(t, arm)][str(k)] for k in range(reps)] for t in tags]

    def det(tags, arm):
        return [[ex[(t, arm)]["u"]] for t in tags]

    first, ptags = load_pairs()
    wa, wb, sigma_star = load_whole()
    seeds = sorted(wa)
    C = {}
    C["lone_E2"] = compare(noise(lone, "noise0.07", 5), det(lone, "C3_rvo2"), GRID_SNAP, T_Q,
                           "lone keystone: noise sigma 0.07 (E2, 5 seeds) vs ORCA (RVO2)")
    C["lone_N1"] = compare(noise(lone, "N1", 20), det(lone, "C3_rvo2"), GRID_SNAP, T_Q,
                           "lone keystone: noise sigma 0.0717 (N1, 20 seeds) vs ORCA (RVO2)")
    C["second_E2"] = compare(noise(second, "noise0.07", 5), det(second, "C3_rvo2"), GRID_SNAP, T_Q,
                             "second trap: noise sigma 0.07 (E2, 26) vs ORCA (RVO2)")
    C["second_pool"] = compare(noise(pool, "noise0.07", 5), det(pool, "C3_rvo2"), GRID_SNAP, T_Q,
                               "second trap: noise sigma 0.07 (pooled 160, A5x) vs ORCA (RVO2)")
    C["second_E2_legacy"] = compare(noise(second, "noise0.07", 5), det(second, "C3_pub"), GRID_SNAP, T_Q,
                                    "second trap: noise sigma 0.07 (E2, 26) vs ORCA (legacy), supplementary")
    C["second_pool_legacy"] = compare(noise(pool, "noise0.07", 5), det(pool, "C3_pub"), GRID_SNAP, T_Q,
                                      "second trap: noise sigma 0.07 (pooled 160) vs ORCA (legacy), supplementary")
    C["whole_E6"] = compare([[wb[s]] for s in seeds], [[wa[s]] for s in seeds], GRID_WHOLE, T_W,
                            "whole runs: SFM + sigma* (E6b) vs ORCA (RVO2) (E6a), seeds 242-427")
    C["pair_legacy"] = compare([[first[(t, "bstar_pub+")]] for t in ptags], [[first[(t, "C3_pub")]] for t in ptags],
                               GRID_SNAP, T_Q, "pair standoff: bias +b*_legacy vs ORCA (legacy)")
    C["pair_rvo2"] = compare([[first[(t, "bstar_rvo2+")]] for t in ptags], [[first[(t, "C3_rvo2")]] for t in ptags],
                             GRID_SNAP, T_Q, "pair standoff: bias +b*_RVO2 vs ORCA (RVO2)")
    # checks against the published numbers (A8 / Table 3 at the nominal horizon)
    assert abs(C["lone_E2"]["delta"] - (148 / 170 - 30 / 34)) < 1e-12
    assert C["pair_legacy"]["orca_freed"] == 21 and C["pair_rvo2"]["orca_freed"] == 7
    assert C["second_pool"]["orca_freed"] == 121 and C["whole_E6"]["orca_freed"] == 101
    main_ids = ["lone_E2", "lone_N1", "second_E2", "second_pool", "whole_E6", "pair_legacy", "pair_rvo2"]
    hw = [C[k]["orca_wilson_halfwidth"] for k in main_ids]
    res = {"script": "experiments/revision2/A5_equivalence.py", "doc": __doc__, "margin": MARGIN, "n_boot": B,
           "rng": f"numpy Generator(PCG64({SEED})), fresh per comparison",
           "interval_primary": "cluster bootstrap over units (snapshots with all their seeds; spawn seeds), percentile",
           "sigma_star": sigma_star, "comparisons": C,
           "margin_basis": {"orca_wilson_halfwidth_min": float(min(hw)), "orca_wilson_halfwidth_max": float(max(hw)),
                            "small_sample_halfwidths": {k: C[k]["orca_wilson_halfwidth"] for k in
                                                        ("lone_E2", "second_E2", "pair_legacy", "pair_rvo2")},
                            "one_snapshot_of_34": 1 / 34, "one_snapshot_of_46": 1 / 46},
           "summary": {"equivalent_at_horizon": [k for k in main_ids if C[k]["equivalent_tost_boot90"]],
                       "not_equivalent_at_horizon": [k for k in main_ids if not C[k]["equivalent_tost_boot90"]],
                       "n_equivalent": sum(C[k]["equivalent_tost_boot90"] for k in main_ids),
                       "n_main": len(main_ids)}}
    path = rev2lib.out_json("A5", res)
    for k, v in C.items():
        print(f"{k:20s} n={v['n_units']:3d} sur={v['surrogate_fraction']:.3f} orca={v['orca_fraction']:.3f} "
              f"d={v['delta']:+.3f} b95={np.round(v['boot_ci95'], 3)} b90={np.round(v['boot_ci90'], 3)} "
              f"t90={np.round(v['t_ci90'], 3)} pTOST={v['p_tost_t']:.3g} eq={v['equivalent_tost_boot90']} "
              f"in95={v['inside_margin_boot95']} hw={v['orca_wilson_halfwidth']:.3f}")
        print(f"    trivial={v['trivial_T_s']} eq90={v['window_equiv90_s']} in95={v['window_inside95_s']} "
              f"orca exits {v['orca_first_exit_s']}-{v['orca_last_exit_s']}")
    print(path)


if __name__ == "__main__":
    main()
