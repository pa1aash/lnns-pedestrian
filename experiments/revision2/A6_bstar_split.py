"""A6: split-half fit of the lateral bias b* (pair standoffs): held-out error of the fraction match.

Inputs (existing data only, no new runs)
  data/E7b/e7b_quench.jsonl            46 pair standoffs, 120 s quench, unperturbed runs: ORCA arms C3_pub (legacy),
                                       C3_rvo2 (RVO2); the SFM (C1, b = 0) and the bias grid b = +0.01, +0.02, +0.03,
                                       +0.05, +0.1 (arms bias<b>; b is the dimensionless tilt of the desired
                                       direction, e -> (e + b e_perp)/|.|)
  data/E7b_bstar/bstar_quench.jsonl    the bias arms at the full-sample fits, bstar_rvo2+ (b = +0.0090625) and
                                       bstar_pub+ (b = +0.02234375)
  data/E7b_bstar/fold_threshold.jsonl  per-snapshot static fold thresholds b*_i (sign +1), the fitting input of
                                       experiments/E7b/matched_b.py
  data/E7b_bstar/bstar.json            the full-sample fits (reproduced here as a check)
Output: data/derived/rev2_A6.json

Fitting rule (experiments/E7b/matched_b.py fit, applied to a subset S of snapshots)
  k = number of snapshots in S that ORCA frees (unperturbed run, freed and first exit <= 120 s); th = sorted
  thresholds b*_i of S (None -> inf); b*_S = midpoint of [th[k-1], th[k]] (th[-1] := 0 when k = 0; th[k] := th[k-1]
  when k = |S|). The fit needs no simulation: it uses the static thresholds, as matched_b does.
Prediction on the held-out half H (the bias arm's freed fraction at b*_S, 120 s)
  quench (primary): the per-snapshot quench outcome q_i(b) in {0, 1} is known on the simulated grid
    b in {0, 0.0090625, 0.01, 0.02, 0.02234375, 0.03, 0.05, 0.1}; at b*_S it is linearly interpolated between the
    two grid points that bracket b*_S (a snapshot whose outcome is the same at both counts 0 or 1; one that changes
    counts the interpolation weight). Held-out freed fraction = mean over H.
  static (secondary): #{i in H : b*_i <= b*_S} / |H|, the static prediction matched_b uses for the fit.
  held-out error e = predicted bias freed fraction on H minus ORCA's freed fraction on H.
Splits: 200 random splits of the 46 snapshots into halves of 23, numpy Generator(PCG64(2026)), permutation per
  split; the first 23 are the fitting half. The same splits serve both solvers (legacy, RVO2).
Reference spread: the split alone, ORCA's freed fraction on H minus that on S (what a perfect predictor that
  matches the fitting half exactly would still miss), is stored beside.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev2lib  # noqa: E402
from rev2lib import DATA, sig  # noqa: E402
import numpy as np  # noqa: E402

T_Q = 120.0
N_SPLIT = 200
SEED = 2026
SOLVERS = {"legacy": ("C3_pub", "pub"), "rvo2": ("C3_rvo2", "rvo2")}


def jl(p):
    return [json.loads(ln) for ln in open(p) if ln.strip()]


def load():
    bst = json.load(open(os.path.join(DATA, "E7b_bstar", "bstar.json")))["fits"]
    grid_arms = {0.0: "C1", 0.01: "bias0.01", 0.02: "bias0.02", 0.03: "bias0.03", 0.05: "bias0.05", 0.1: "bias0.1",
                 bst["rvo2"]["b_star"]: "bstar_rvo2+", bst["pub"]["b_star"]: "bstar_pub+"}
    want = set(grid_arms.values()) | {"C3_pub", "C3_rvo2"}
    out = {}
    for p in (os.path.join(DATA, "E7b", "e7b_quench.jsonl"), os.path.join(DATA, "E7b_bstar", "bstar_quench.jsonl")):
        for r in jl(p):
            tag, arm, rep = r["job_id"].split("|")
            if rep == "u" and arm in want:
                out[(tag, arm)] = bool(r["freed"] and r["first_t"] is not None and r["first_t"] <= T_Q + 1e-9)
    th = {}
    for r in jl(os.path.join(DATA, "E7b_bstar", "fold_threshold.jsonl")):
        if r["sign"] == 1:
            th[r["tag"]] = np.inf if r["b_star"] is None else float(r["b_star"])
    tags = sorted(th, key=lambda t: int(t.rsplit("seed", 1)[1]))
    assert len(tags) == 46
    grid = np.array(sorted(grid_arms))
    Q = np.array([[out[(t, grid_arms[b])] for b in grid] for t in tags], float)       # (46, n_grid)
    O = {s: np.array([out[(t, a)] for t in tags], float) for s, (a, _) in SOLVERS.items()}
    TH = np.array([th[t] for t in tags])
    return tags, grid, Q, O, TH, bst


def fit(th, k):
    th = np.sort(th)
    N = len(th)
    lo = th[k - 1] if k > 0 else 0.0
    hi = th[k] if k < N else lo
    return 0.5 * (lo + hi)


def quench_pred(Q, grid, b):
    """Per-snapshot linear interpolation of the 0/1 quench outcome over the b grid."""
    b = min(max(b, grid[0]), grid[-1])
    return np.array([np.interp(b, grid, q) for q in Q])


def summ(v):
    v = np.asarray(v, float)
    return {"median": float(np.median(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
            "lo95": float(np.percentile(v, 2.5)), "hi95": float(np.percentile(v, 97.5)),
            "min": float(v.min()), "max": float(v.max()),
            "frac_abs_le_0p10": float(np.mean(np.abs(v) <= 0.10 + 1e-12))}


def main():
    tags, grid, Q, O, TH, bst = load()
    n = len(tags)
    # monotonicity of the quench outcome in b, per snapshot
    nonmono = [tags[i] for i in range(n) if np.any(np.diff(Q[i]) < 0)]
    # static prediction against the quench at the grid points
    static_dis = {f"{b:g}": int(np.sum((TH <= b + 1e-15) != Q[:, j].astype(bool))) for j, b in enumerate(grid)}
    res = {"script": "experiments/revision2/A6_bstar_split.py", "doc": __doc__, "n_snapshots": n,
           "n_splits": N_SPLIT, "n_half": 23, "rng": f"numpy Generator(PCG64({SEED}))", "b_grid": [float(b) for b in grid],
           "quench_freed_on_grid": {f"{b:g}": int(Q[:, j].sum()) for j, b in enumerate(grid)},
           "quench_nonmonotone_snapshots": nonmono, "n_quench_nonmonotone": len(nonmono),
           "static_vs_quench_disagreements_on_grid": static_dis, "solvers": {}}
    rng = np.random.Generator(np.random.PCG64(SEED))
    splits = [rng.permutation(n) for _ in range(N_SPLIT)]
    for s, (arm, key) in SOLVERS.items():
        o = O[s]
        # full-sample check against data/E7b_bstar/bstar.json
        b_full = fit(TH, int(o.sum()))
        assert abs(b_full - bst[key]["b_star"]) < 1e-15, (s, b_full, bst[key]["b_star"])
        rows = []
        for perm in splits:
            S, H = perm[:23], perm[23:]
            kS = int(o[S].sum())
            b = fit(TH[S], kS)
            qh = quench_pred(Q[H], grid, b).mean()
            sh = float(np.mean(TH[H] <= b))
            qs = quench_pred(Q[S], grid, b).mean()
            rows.append({"b_fit": float(b), "k_fit_half": kS, "orca_fit_half": kS / 23, "orca_held": float(o[H].mean()),
                         "pred_held_quench": float(qh), "pred_held_static": sh,
                         "err_held_quench": float(qh - o[H].mean()), "err_held_static": float(sh - o[H].mean()),
                         "err_fit_quench": float(qs - kS / 23),
                         "split_ref": float(o[H].mean() - kS / 23)})
        col = lambda k: [r[k] for r in rows]  # noqa: E731
        R = {"orca_arm": arm, "orca_freed_full": int(o.sum()), "b_star_full": float(b_full),
             "b_fit": summ(col("b_fit")),
             "err_held_quench": summ(col("err_held_quench")), "err_held_static": summ(col("err_held_static")),
             "err_fit_quench": summ(col("err_fit_quench")), "split_ref": summ(col("split_ref")),
             "n_b_differs_from_full": int(sum(abs(r["b_fit"] - b_full) > 0 for r in rows)),
             "splits": rows}
        e = np.array(col("err_held_quench"))
        R["err_held_quench"]["n_le_minus_0p10"] = int(np.sum(e < -0.10 - 1e-12))
        R["err_held_quench"]["n_ge_plus_0p10"] = int(np.sum(e > 0.10 + 1e-12))
        R["err_held_quench"]["median_abs"] = float(np.median(np.abs(e)))
        R["err_held_quench"]["rmse"] = float(np.sqrt(np.mean(e ** 2)))
        R["split_ref"]["rmse"] = float(np.sqrt(np.mean(np.array(col("split_ref")) ** 2)))
        R["b_fit"]["median_2sf"] = sig(R["b_fit"]["median"], 2)
        res["solvers"][s] = R
        print(s, "b_full", b_full, "b_fit", {k: round(v, 5) for k, v in R["b_fit"].items() if isinstance(v, float)})
        for k in ("err_held_quench", "err_held_static", "err_fit_quench", "split_ref"):
            print("  ", k, {kk: round(v, 3) for kk, v in R[k].items() if isinstance(v, float)})
    print("nonmonotone", nonmono, "static vs quench", static_dis, res["quench_freed_on_grid"])
    print(rev2lib.out_json("A6", res))


if __name__ == "__main__":
    main()
