"""Matched lateral bias b* for the pair class (plan section 9, S9g) and its held-out runs.

  fit   b* is fitted on rate only. The target is the number of pair snapshots that ORCA frees in the E7b quench
        (unperturbed runs, 120 s): C3 published (b*_pub, the paradigm as published, as in pilot A6) and C3 RVO2
        (b*_rvo2, forward claims). The freed fraction under C1 + bias b > 0 is interpolated between the coarse
        quench grid points with the per-snapshot static fold thresholds b*_i (fold_threshold.py): the static
        curve F(b) = #{i : b*_i <= b} / 46 reproduces the quench at the grid points to within the static
        prediction's disagreements (reported by analyze.py). b* is the midpoint of the interval of b on which
        F(b) equals the ORCA count k (so the static prediction frees exactly k); if no such interval exists,
        the midpoint between the k-th and (k+1)-th smallest thresholds. The fit uses the positive sign only
        (b > 0 tilts toward +y); -b* is a held-out reversal. Written to data/E7b_bstar/bstar.json.
  run   held-out quench at +b*, -b* for both fits on all 46 snapshots, each unperturbed and with 5 x 1e-9 m
        perturbations (seeds 900-904), 120 s, dt 0.01 s, flags CF union {B_w: 0.04} union
        {w2_noise: lateral_bias, w2_bias_b}, stationary stop as E7b_quench (run function reused unchanged).
        Output: data/E7b_bstar/bstar_quench.jsonl (job_id "<tag>|<arm>|<rep>"), resumable.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
sys.path.insert(0, HERE)
from e1lib import DATA, run_jobs  # noqa: E402
import numpy as np  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402
from e7b_quench import BASE, PERTURB_SEEDS, T_Q, run  # noqa: E402

DIR = os.path.join(DATA, "E7b_bstar")
BSTAR = os.path.join(DIR, "bstar.json")
OUT = os.path.join(DIR, "bstar_quench.jsonl")
QUENCH = os.path.join(DATA, "E7b", "e7b_quench.jsonl")
FOLD = os.path.join(DIR, "fold_threshold.jsonl")
TARGETS = {"pub": "C3_pub", "rvo2": "C3_rvo2"}


def fit():
    k = {a: 0 for a in TARGETS.values()}
    n = 0
    for ln in open(QUENCH):
        r = json.loads(ln)
        if r["arm"] in k and r["perturb"] is None:
            k[r["arm"]] += r["freed"]
            n += r["arm"] == "C3_pub"
    th = sorted(json.loads(ln)["b_star"] or np.inf for ln in open(FOLD) if json.loads(ln)["sign"] == 1)
    N = len(th)
    assert N == n == 46, (N, n)
    out = {"script": "experiments/E7b/matched_b.py fit", "doc": __doc__, "n": N, "thresholds_plus": th, "fits": {}}
    for key, arm in TARGETS.items():
        kk = int(k[arm])
        lo = th[kk - 1] if kk > 0 else 0.0
        hi = th[kk] if kk < N else lo
        out["fits"][key] = {"arm": arm, "k_target": kk, "interval": [lo, hi], "b_star": 0.5 * (lo + hi),
                            "static_fraction_at_b_star": sum(t <= 0.5 * (lo + hi) for t in th) / N}
    os.makedirs(DIR, exist_ok=True)
    json.dump(out, open(BSTAR, "w"), indent=1, default=float)
    print(json.dumps(out["fits"], indent=1))


def jobs():
    fits = json.load(open(BSTAR))["fits"]
    J = []
    for p in pairs():
        for key, f in fits.items():
            for s in (1, -1):
                b = s * f["b_star"]
                arm = f"bstar_{key}{'+' if s > 0 else '-'}"
                for ps in (None,) + PERTURB_SEEDS:
                    J.append({"job_id": f"{p['tag']}|{arm}|{'u' if ps is None else ps}", "snap": p["snap"],
                              "arm": arm, "config": "C1",
                              "flags": {**BASE, "w2_noise": "lateral_bias", "w2_bias_b": b},
                              "deterministic": True, "perturb": ps, "delta": None, "t_q": T_Q})
    return J


def main(argv=None):
    a = qargs.parse(argv)
    if "fit" in a.rest:
        return fit()
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(qargs.select(jobs(), a), run, out, workers=min(a.workers, 2), log_every=50)


if __name__ == "__main__":
    print("wall", main())
