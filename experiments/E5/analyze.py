"""E5b analysis: completion against noise amplitude in corrected-forward mode.

Input:  data/E5/e5b.jsonl (experiments/E5/e5_sweep.py; CF, w = 0.8 m, 100 agents, seeds 42-141, 600 s),
        data/E1/E1_runs.jsonl (sigma = 0: E1b, same seeds 42-141).
Output: data/derived/E5_analysis.json.

Definitions
  completion   all 100 agents out within 600 s; Wilson 95% interval per sigma.
  logistic     binomial logit(p) = b (sigma - sigma50), maximum likelihood; 95% profile-likelihood interval
               for sigma50 (b profiled out; drop of chi2_1(0.95)/2 in log-likelihood). Fitted on the five
               noise levels, and again with sigma = 0 included.
  reference    conference value sigma50 = 0.049 m/s (published-reproduction mode, n = 25 per level).
"""
import json
import math
import os
from collections import defaultdict

import numpy as np
from scipy import optimize, stats

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IN = os.path.join(ROOT, "data", "E5", "e5b.jsonl")
E1 = os.path.join(ROOT, "data", "E1", "E1_runs.jsonl")
OUT = os.path.join(ROOT, "data", "derived", "E5_analysis.json")
SEEDS = range(42, 142)
CONF_SIGMA50 = 0.049


def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [p, max(0.0, c - h), min(1.0, c + h)]


def nll(b, s50, x, k, n):
    eta = b * (x - s50)
    return -float(np.sum(k * eta - n * np.logaddexp(0, eta)))


def fit(x, k, n):
    x, k, n = map(np.asarray, (x, k, n))
    r = optimize.minimize(lambda p: nll(p[0], p[1], x, k, n), [40.0, 0.05], method="Nelder-Mead",
                          options={"xatol": 1e-10, "fatol": 1e-10, "maxiter": 20000})
    b, s50 = r.x
    ll = -r.fun

    def prof(s):
        return -optimize.minimize_scalar(lambda bb: nll(bb, s, x, k, n), bounds=(0.1, 1000), method="bounded",
                                         options={"xatol": 1e-9}).fun
    tgt = ll - stats.chi2.ppf(0.95, 1) / 2
    lo = optimize.brentq(lambda s: prof(s) - tgt, s50 - 0.05, s50)
    hi = optimize.brentq(lambda s: prof(s) - tgt, s50, s50 + 0.05)
    p = 1 / (1 + np.exp(-b * (x - s50)))
    dev = 2 * float(np.sum(stats.binom.logpmf(k, n, k / n) - stats.binom.logpmf(k, n, p)))
    return {"sigma50": float(s50), "ci95_profile": [float(lo), float(hi)], "slope_b": float(b),
            "deviance": dev, "dof": int(len(x) - 2), "gof_p": float(stats.chi2.sf(dev, len(x) - 2))}


def main():
    R = [json.loads(ln) for ln in open(IN)]
    c = defaultdict(lambda: [0, 0])
    for r in R:
        c[r["sigma"]][0] += bool(r["complete"])
        c[r["sigma"]][1] += 1
    z = [json.loads(ln) for ln in open(E1)]
    z = [r for r in z if r["mode"] == "E1b" and r["seed"] in SEEDS]
    c0 = [sum(bool(r["complete"]) for r in z), len(z)]
    sig = sorted(c)
    per = {f"s{s:g}".replace(".", "p"): {"sigma": s, "k": c[s][0], "n": c[s][1], "wilson": wilson(*c[s])}
           for s in sig}
    per["s0"] = {"sigma": 0.0, "k": c0[0], "n": c0[1], "wilson": wilson(*c0), "source": "E1b seeds 42-141"}
    f5 = fit(sig, [c[s][0] for s in sig], [c[s][1] for s in sig])
    f6 = fit([0.0] + sig, [c0[0]] + [c[s][0] for s in sig], [c0[1]] + [c[s][1] for s in sig])
    out = {"mode": "corrected-forward", "width_m": 0.8, "n_agents": 100, "seeds": "42-141", "t_max_s": 600,
           "per_sigma": per, "logistic_noise_levels": f5, "logistic_with_sigma0": f6,
           "conference_sigma50": CONF_SIGMA50,
           "conference_inside_ci": f5["ci95_profile"][0] <= CONF_SIGMA50 <= f5["ci95_profile"][1],
           "deadlocked_or_capped": {k: v["n"] - v["k"] for k, v in per.items()}}
    json.dump(out, open(OUT, "w"), indent=1)
    for k in sorted(per, key=lambda k: per[k]["sigma"]):
        print(k, per[k]["k"], "/", per[k]["n"], [round(v, 3) for v in per[k]["wilson"]])
    print("fit (noise levels)", f5)
    print("fit (with sigma 0)", f6)


if __name__ == "__main__":
    main()
