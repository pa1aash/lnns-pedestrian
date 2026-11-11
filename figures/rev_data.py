"""Readers for the revision analyses (data/derived/rev_*.json). Each returns None while the file is absent, so the
figures build before and after the revision data land."""
import json
import math
import os
from pathlib import Path

import numpy as np
from scipy import stats

# REV_DERIVED overrides the directory (for a dry run against another checkout before the data are published)
DERIVED = Path(os.environ.get("REV_DERIVED", Path(__file__).resolve().parent.parent / "data" / "derived"))


def _load(*names):
    for n in names:
        p = DERIVED / n
        if p.exists():
            return json.load(open(p))
    return None


def rev_arrhenius():
    """High-beta restarts of session C, B3 (rev_B3.json): per snapshot the escape rates at beta = 1.5-7 of the alone
    condition and the slope ratio of the fit over all six levels. `collapse`: the beta >= 5 levels as ln(lambda/nu) with
    nu the attempt rate of the same snapshot's alone fit in E4_analysis.json (the other panel-(a) points); the levels
    beta <= 3.5 are those E4 already carries. `ratio`: one entry per snapshot, barrier dU, ratio and 95% interval."""
    b3 = _load("rev_B3.json")
    if b3 is None:
        return None
    e4 = json.load(open(DERIVED / "E4_analysis.json"))
    collapse, ratio = [], []
    for name, s in b3["snapshots"].items():
        alone = e4["snapshots"][name]["conds"]["alone"]
        assert abs(alone["dU"] - s["dU_alone_J"]) < 1e-9
        nu = alone["arrhenius"]["nu_hat"]
        for c in s["cells"]:
            if c["beta"] < 5:
                continue
            collapse.append({"beta": c["beta"], "y": math.log(c["lam"] / nu), "lo": math.log(c["ci95"][0] / nu),
                             "hi": math.log(c["ci95"][1] / nu), "events": c["events"], "n": c["n"]})
        f = s["fit_1p5_7"]
        ratio.append({"dU": s["dU_alone_J"], "r": f["ratio"], "lo": f["ci95"][0], "hi": f["ci95"][1]})
    return {"collapse": collapse, "ratio": ratio}


def _wilson(k, n, z=1.959963984540054):
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def rev_width():
    """Completion against exit width from rev_B2.json (session C, B2: 1100 runs, each run counted once, 11 widths).
    points: every width of fit_all.table with its Wilson 95% interval.
    logistic: completion = 1 / (1 + exp(-k (w - w50))), maximum likelihood on the binomial counts of the table (the
    fit is checked against fit_all: w50 and the slope). The band is the pointwise 95% interval of the fitted curve
    (delta method on the logit, from the Fisher information of the binomial fit).
    bracket: the bounds on w50 of the stuck-alone analysis (median agent / median run maximum of the zero-margin width)."""
    b2 = _load("rev_B2.json")
    if b2 is None:
        return None
    from scipy import optimize
    fa = b2["fit_all"]
    pts = []
    for r in fa["table"]:
        lo, hi = _wilson(r["k"], r["n"])
        pts.append({"w": r["w"], "p": r["k"] / r["n"], "lo": lo, "hi": hi, "k": r["k"], "n": r["n"]})
    W = np.array([r["w"] for r in fa["table"]]); K = np.array([r["k"] for r in fa["table"]], float)
    N = np.array([r["n"] for r in fa["table"]], float)

    def nll(th):
        z = th[0] + th[1] * W
        return float(np.sum(N * np.logaddexp(0, z) - K * z))
    th = optimize.minimize(nll, [-36.0, 41.0], method="BFGS").x
    k, w50 = th[1], -th[0] / th[1]
    assert abs(w50 - fa["w50_m"]) < 2e-4 and abs(k - fa["slope_per_m"]) < 0.05, (w50, k, fa["w50_m"], fa["slope_per_m"])
    pr = 1 / (1 + np.exp(-(th[0] + th[1] * W)))
    X = np.column_stack([np.ones_like(W), W])
    cov = np.linalg.inv(X.T @ (X * (N * pr * (1 - pr))[:, None]))
    w = np.linspace(0.68, 1.02, 300)
    G = np.column_stack([np.ones_like(w), w])
    z = G @ th; se = np.sqrt(np.einsum("ij,jk,ik->i", G, cov, G))
    f = lambda q: 1 / (1 + np.exp(-q))
    br = b2["bracket"]
    logistic = {"w": w, "mid": f(z), "lo": f(z - 1.959964 * se), "hi": f(z + 1.959964 * se), "w50": w50,
                "w50_ci95": fa["w50_ci95"]}
    return {"points": pts, "logistic": logistic,
            "bracket": (br["w_lo_median_agent_wc_m"], br["w_hi_median_run_max_wc_m"])}
