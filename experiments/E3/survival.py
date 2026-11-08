"""Survival helpers shared by the E3 and E4 analyses.

exp_rate      censored-exponential rate: lambda_hat = d / T (d events, T total time at risk, censored runs
              contribute their censoring time); exact Poisson (Garwood) 95% interval
              [chi2(0.025, 2d) / 2T, chi2(0.975, 2d + 2) / 2T].
weibull_pool  censored Weibull with one shape k shared by all groups and a scale per group (each group's
              scale is profiled out: theta_g^k = sum_i t_i^k / d_g); 95% profile-likelihood interval for k
              (drop of chi2_1(0.95) / 2 = 1.92 in log-likelihood). A single group gives the per-cell shape.
km            Kaplan-Meier product-limit estimate (times rounded to 0.01 s), as experiments/E2/analyze.py.
"""
import math

import numpy as np
from scipy import optimize, stats

Z95 = 1.959963984540054


def exp_rate(t, censored):
    t = np.asarray(t, float)
    c = np.asarray(censored, bool)
    d, T = int((~c).sum()), float(t.sum())
    lo = stats.chi2.ppf(0.025, 2 * d) / (2 * T) if d > 0 else 0.0
    hi = stats.chi2.ppf(0.975, 2 * d + 2) / (2 * T)
    return {"lam": d / T if T > 0 else None, "ci95": [float(lo), float(hi)], "events": d, "n": int(len(t)),
            "exposure_s": T, "censored_frac": float(c.mean()) if len(c) else None}


def _profile_ll(k, groups):
    ll = 0.0
    for t, c in groups:
        e = ~c
        d = e.sum()
        if d == 0:
            continue
        s = np.sum(t ** k)
        thk = s / d                     # theta_g^k
        ll += d * math.log(k) - d * math.log(thk) + (k - 1) * np.log(t[e]).sum() - d
    return ll


def weibull_pool(groups):
    """groups: list of (times, censored). Returns shape k, 95% profile CI, events, groups used."""
    G = [(np.asarray(t, float), np.asarray(c, bool)) for t, c in groups]
    G = [(np.maximum(t, 1e-3), c) for t, c in G if (~c).sum() > 0]
    if not G:
        return None
    f = lambda lk: -_profile_ll(math.exp(lk), G)  # noqa: E731
    r = optimize.minimize_scalar(f, bounds=(math.log(0.05), math.log(20.0)), method="bounded",
                                 options={"xatol": 1e-8})
    lk, llmax = r.x, -r.fun
    target = llmax - stats.chi2.ppf(0.95, 1) / 2
    g = lambda x: -f(x) - target  # noqa: E731
    lo = optimize.brentq(g, math.log(0.05), lk) if g(math.log(0.05)) < 0 else None
    hi = optimize.brentq(g, lk, math.log(20.0)) if g(math.log(20.0)) < 0 else None
    return {"k": math.exp(lk), "ci95": [math.exp(lo) if lo is not None else None,
                                        math.exp(hi) if hi is not None else None],
            "events": int(sum((~c).sum() for _, c in G)), "groups": len(G)}


def km(times, events, t_max):
    t = np.round(np.asarray(times, float), 2)
    e = np.asarray(events, bool)
    order = np.argsort(t, kind="stable")
    t, e = t[order], e[order]
    n = len(t)
    S, curve, i = 1.0, [[0.0, 1.0]], 0
    while i < n:
        ti, j, d = t[i], i, 0
        while j < n and t[j] == ti:
            d += int(e[j])
            j += 1
        if d:
            S *= 1 - d / (n - i)
            curve.append([float(ti), S])
        i = j
    curve.append([float(t_max), S])

    def quant(level):
        for tt, s in curve[1:-1]:
            if s <= level + 1e-12:
                return tt
        return None
    return {"n": n, "events": int(e.sum()), "S_end": S, "median": quant(0.5), "curve": curve}


def boot_ci(stat, n, rng, B=2000, level=95):
    vals = []
    for _ in range(B):
        v = stat(rng.integers(0, n, n))
        if v is not None and np.isfinite(v):
            vals.append(v)
    if not vals:
        return None
    a = (100 - level) / 2
    return [float(np.percentile(vals, a)), float(np.percentile(vals, 100 - a))]
