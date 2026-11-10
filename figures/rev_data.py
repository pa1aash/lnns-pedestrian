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


def _wilson(k, n, z=1.959963984540054):
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def rev_width():
    """Width grid, logistic fit and parameter-free predictions from rev_B2.json (session C, B2).
    points: every width of fit_all.table not among the E7 widths (0.7, 0.8, 0.9, 1.0 m), Wilson 95%.
    logistic: completion = 1 / (1 + exp(-k (w - w50))) with the ML slope k; the band spans the logistic with w50 at the
    ends of its 95% bootstrap interval (slope held), i.e. it shows the uncertainty of the critical width.
    predictions: (1 - f(w))^N for N = 100 and N = N_eff, f(w) the stuck-alone fraction (f_at, interpolated
    monotonically in log f)."""
    b2 = _load("rev_B2.json")
    if b2 is None:
        return None
    from scipy.interpolate import PchipInterpolator
    fa = b2["fit_all"]
    old = {0.7, 0.8, 0.9, 1.0}
    pts = []
    for r in fa["table"]:
        if round(r["w"], 3) in old:
            continue
        lo, hi = _wilson(r["k"], r["n"])
        pts.append({"w": r["w"], "p": r["k"] / r["n"], "lo": lo, "hi": hi})
    w = np.linspace(0.68, 1.02, 300)
    k, w50 = fa["slope_per_m"], fa["w50_m"]
    lg = lambda c: 1 / (1 + np.exp(-k * (w - c)))
    a_, b_ = fa["w50_ci95"]
    logistic = {"w": w, "mid": lg(w50), "lo": lg(b_), "hi": lg(a_), "w50": w50, "w50_ci95": fa["w50_ci95"]}
    ws = np.array(sorted(float(x) for x in b2["f_at"])); fs = np.array([b2["f_at"][f"{x:.2f}"] for x in ws])
    lf = PchipInterpolator(ws, np.log(fs))
    wp = np.linspace(ws[0], ws[-1], 300)
    preds = {name: {"w": wp, "p": (1 - np.exp(lf(wp))) ** b2["prediction"][key]["N"], "N": b2["prediction"][key]["N"]}
             for name, key in (("N = 100", "N100"), ("N_eff", "Neff"))}
    return {"points": pts, "logistic": logistic, "predictions": preds}
