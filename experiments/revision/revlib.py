"""Shared helpers for the revision evidence (session C, experiments/revision/).

Puts experiments/lib and the experiment folders on sys.path (w2lib changes cwd to code/), and gives
the conventions every revision script follows:
  out_json(name, obj)   write data/derived/rev_<name>.json (registry source)
  data_dir(name)        data/revision/<name>/ for raw JSONL of new runs
  sig(x, n=2)           round to n significant figures (derived quantities)
  pdisp(p)              display form of a p-value: 3 significant decimals at p >= 1e-3, else "p < 10^{-k}"
                        written as LaTeX "<10^{-k}" with k = floor(-log10 p)
  mcnemar_exact(b, c)   two-sided exact McNemar p from the discordant counts
  holm(ps)              Holm step-down adjusted p-values (same order as ps)
  wilson(k, n)          (p, lo, hi)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
for d in ("lib", "E2", "E3", "E4", "E6", "E7", "E7b", "arch", "runs3", "fixan", "BAR"):
    p = os.path.join(EXP, d)
    if p not in sys.path:
        sys.path.insert(0, p)
from e1lib import CF, DATA, DERIVED, ROOT, load_runs, run_jobs  # noqa: E402,F401
from w2lib import wilson  # noqa: E402,F401
import numpy as np  # noqa: E402,F401
from scipy import stats  # noqa: E402


def data_dir(name):
    d = os.path.join(DATA, "revision", name)
    os.makedirs(d, exist_ok=True)
    return d


def out_json(name, obj):
    path = os.path.join(DERIVED, f"rev_{name}.json")
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    return path


def sig(x, n=2):
    if x is None or x == 0 or not math.isfinite(x):
        return x
    return round(x, n - 1 - int(math.floor(math.log10(abs(x)))))


def pdisp(p):
    if p >= 1e-3:
        return f"{p:.3f}" if p >= 0.01 else f"{sig(p, 2)}"
    k = int(math.floor(-math.log10(p)))
    return f"<10^{{-{k}}}"


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return float(min(1.0, 2 * stats.binom.cdf(min(b, c), n, 0.5)))


def holm(ps):
    ps = list(ps)
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj
