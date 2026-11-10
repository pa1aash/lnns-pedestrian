"""Readers for the revision analyses (data/derived/rev_*.json). Each returns None while the file is absent, so the
figures build before and after the revision data land."""
import json
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


def _trend_band(fits, ref):
    """Pooled common-intercept WLS of the slope ratio r on ln dU (weights 1/se^2, covariance scaled by chi2/dof), as in
    experiments/revision/A4_ratio_trend.py; returns callables for the line and its pointwise 95% band. The slope is
    checked against the published fit `ref` (rev_A4.json pooled_common.wls)."""
    x = np.log([f["dU"] for f in fits]); y = np.array([f["r"] for f in fits]); se = np.array([f["se"] for f in fits])
    X = np.column_stack([np.ones_like(x), x]); W = 1 / se ** 2
    A = X.T @ (X * W[:, None]); beta = np.linalg.solve(A, X.T @ (W * y))
    res = (y - X @ beta) / se; dof = len(y) - 2; chi2 = float(res @ res)
    cov = np.linalg.inv(A) * chi2 / dof
    assert abs(beta[1] - ref["b"]) < 1e-9 and abs(beta[0] - ref["intercepts"][0]) < 1e-9, (beta, ref)
    t = stats.t.ppf(0.975, dof)

    def mid(u):
        return beta[0] + beta[1] * np.log(u)

    def half(u):
        g = np.column_stack([np.ones_like(u), np.log(u)])
        return t * np.sqrt(np.einsum("ij,jk,ik->i", g, cov, g))
    return {"mid": mid, "lo": lambda u: mid(u) - half(u), "hi": lambda u: mid(u) + half(u), "b": beta[1],
            "ci95": ref["ci95_scaled"]}


def rev_arrhenius():
    """Slope-ratio trend (session C, A4: rev_A4.json) and the high-beta restarts (B3; collapse points, when present)."""
    a4 = _load("rev_A4.json")
    if a4 is None:
        return None
    out = {"trend": _trend_band(a4["fits"], a4["pooled_common"]["wls"]), "collapse": None}
    return out


def rev_width():
    """Width grid 0.82-0.96 m, logistic fit with band, parameter-free prediction(s) (session C, B2). Not yet available.
    Shape: {"points": [{"w", "p", "lo", "hi"}], "logistic": {"w", "mid", "lo", "hi"}, "predictions": {name: {"w", "p"}}}."""
    return None
