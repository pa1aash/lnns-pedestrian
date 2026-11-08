"""Binomial-logit fit of completion against noise amplitude, and its inversion (used by E6b).

fit_logit(x, k, n): maximum-likelihood fit of P(complete) = 1 / (1 + exp(-(a + b x))) to k successes
out of n at each x (Newton-Raphson on the binomial log-likelihood); returns a, b, their covariance
(inverse Fisher information) and the deviance.
invert(fit, p): x* with P(x*) = p, and its delta-method standard error from the (a, b) covariance plus
the binomial variance of p when n_p (the size of the sample p was estimated from) is given.
"""
import math

import numpy as np


def fit_logit(x, k, n, iters=100):
    x, k, n = (np.asarray(v, float) for v in (x, k, n))
    X = np.column_stack([np.ones_like(x), x])
    beta = np.zeros(2)
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(X @ beta)))
        W = n * p * (1 - p)
        g = X.T @ (k - n * p)
        H = X.T @ (X * W[:, None])
        step = np.linalg.solve(H, g)
        beta += step
        if np.max(np.abs(step)) < 1e-12:
            break
    p = 1.0 / (1.0 + np.exp(-(X @ beta)))
    W = n * p * (1 - p)
    cov = np.linalg.inv(X.T @ (X * W[:, None]))
    with np.errstate(divide="ignore", invalid="ignore"):
        dev = 2 * np.nansum(np.where(k > 0, k * np.log(k / (n * p)), 0)
                            + np.where(n - k > 0, (n - k) * np.log((n - k) / (n * (1 - p))), 0))
    return {"a": float(beta[0]), "b": float(beta[1]), "cov": cov.tolist(), "deviance": float(dev),
            "dof": int(len(x) - 2), "x": x.tolist(), "k": k.tolist(), "n": n.tolist()}


def predict(fit, x):
    return 1.0 / (1.0 + math.exp(-(fit["a"] + fit["b"] * x)))


def invert(fit, p, n_p=None):
    a, b = fit["a"], fit["b"]
    lp = math.log(p / (1 - p))
    xs = (lp - a) / b
    C = np.array(fit["cov"])
    g = np.array([-1.0 / b, -(lp - a) / b ** 2])          # d x* / d(a, b)
    var = float(g @ C @ g)
    if n_p:
        var += (1.0 / (b * p * (1 - p))) ** 2 * p * (1 - p) / n_p   # d x*/dp = 1 / (b p (1 - p))
    return {"x_star": xs, "se": math.sqrt(var), "logit_p": lp}
