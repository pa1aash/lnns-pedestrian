"""Statistics shared by the queue-3 analyses (all intervals 95%).

wilson(k, n)              Wilson score interval.
jaccard_stats(fa, fb, U)  J of two failure sets over the units U, with a bootstrap interval over units
                          (resampled units keep their multiplicity) and the independence reference (the
                          second set's labels permuted over U): mean and 95% range.
newcombe_paired(...)      Newcombe (1998) method 10 interval for a paired difference of proportions.
odds_ratio(a, b, c, d)    Fisher exact test and the conditional MLE odds ratio with its exact interval
                          (scipy.stats.contingency odds_ratio).
mann_whitney(x, y)        two-sided Mann-Whitney U, p and AUC = P(x > y) + P(x = y) / 2.
loglog_slope(x, y)        least-squares slope of ln y on ln x with its 95% t interval.
"""
import math

import numpy as np
from scipy import stats

B = 10000
SEED = 20261109


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return [float("nan"), float("nan")]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def jaccard_stats(fa, fb, U, rng=None):
    rng = rng or np.random.default_rng(SEED)
    U = list(U)
    a = np.array([u in fa for u in U])
    b = np.array([u in fb for u in U])
    n = len(U)

    def J(x, y):
        u = (x | y).sum()
        return float((x & y).sum() / u) if u else float("nan")
    bs = [J(a[i], b[i]) for i in (rng.integers(0, n, n) for _ in range(B))]
    perm = [J(a, rng.permutation(b)) for _ in range(B)]
    j = J(a, b)
    return {"jaccard": j, "ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
            "independent_mean": float(np.nanmean(perm)),
            "independent_95": [float(np.nanpercentile(perm, 2.5)), float(np.nanpercentile(perm, 97.5))],
            "p_perm_above_independent": float((np.sum(np.array(perm) >= j) + 1) / (B + 1)),
            "n_a": int(a.sum()), "n_b": int(b.sum()), "both": int((a & b).sum()), "n_units": n}


def newcombe_paired(a, b, c, d, z=1.959963984540054):
    n = a + b + c + d
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, z)
    l2, u2 = wilson(a + c, n, z)
    dd = p1 - p2
    num = a * d - b * c
    den = (a + b) * (c + d) * (a + c) * (b + d)
    phi = 0.0 if den == 0 else (max(num - n / 2, 0) if num > 0 else num) / math.sqrt(den)
    lo = dd - math.sqrt(max((p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2, 0))
    hi = dd + math.sqrt(max((u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2, 0))
    return {"diff": dd, "ci95": [lo, hi]}


def odds_ratio(a, b, c, d):
    """2x2 [[a, b], [c, d]]: rows = fails under resolver 1 (yes, no), columns = fails under resolver 2."""
    from scipy.stats.contingency import odds_ratio as _or
    t = [[a, b], [c, d]]
    r = _or(t)
    ci = r.confidence_interval(0.95)
    return {"table": t, "odds_ratio": float(r.statistic), "ci95": [float(ci.low), float(ci.high)],
            "fisher_p": float(stats.fisher_exact(t)[1])}


def mann_whitney(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) == 0 or len(y) == 0:
        return None
    r = stats.mannwhitneyu(x, y, alternative="two-sided")
    return {"U": float(r.statistic), "p": float(r.pvalue), "auc": float(r.statistic / (len(x) * len(y))),
            "n_x": len(x), "n_y": len(y)}


def loglog_slope(x, y):
    x, y = np.log(np.asarray(x, float)), np.log(np.asarray(y, float))
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 3:
        return None
    r = stats.linregress(x, y)
    t = stats.t.ppf(0.975, len(x) - 2)
    return {"slope": float(r.slope), "ci95": [float(r.slope - t * r.stderr), float(r.slope + t * r.stderr)],
            "n": int(len(x))}
