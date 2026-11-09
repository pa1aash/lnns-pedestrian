"""Analysis of run-N5 (contact arches at dt = 0.0025 s and at lower drives).

Inputs: data/N5/n5.jsonl; data/derived/arch_analysis.json (the v0 = 5 m/s, dt = 0.01 s cell) for comparison.
Output: data/derived/N5_analysis.json. Per cell: completed, deadlocked and capped runs; runs with an arch and Cell names with "." written with "p" (dt0p0025_v5).
with an arch of size >= 3; episodes; lifetime median, 95th percentile and maximum; episodes lasting >= 1 s and
>= 5 s; persistent runs (an episode >= 10 s) with Wilson interval; share of 0.1 s checks with an arch; peak
body force and largest relative tangential speed; deadlocks with an arch at the stop.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "N5_analysis.json")


def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [float(max(0.0, c - h)), float(min(1.0, c + h))]


def main():
    R = [json.loads(l) for l in open(os.path.join(DATA, "N5", "n5.jsonl")) if l.strip()]
    cells = {}
    for c in sorted({r["cell"] for r in R}):
        rr = [r for r in R if r["cell"] == c]
        eps = [e for r in rr for e in r["episodes"]]
        life = np.array([e["t1"] - e["t0"] for e in eps]) if eps else np.zeros(0)
        n = len(rr)
        pers = sum(r["n_persistent"] > 0 for r in rr)
        dl = [r for r in rr if r["deadlock"]]
        cells[c.replace(".", "p")] = {"n": n, "v0_mean": rr[0]["v0_mean"], "dt": rr[0]["dt"],
                    "complete": sum(r["complete"] for r in rr), "deadlock": len(dl),
                    "capped": sum((not r["complete"]) and (not r["deadlock"]) for r in rr),
                    "runs_with_arch": sum(r["n_episodes"] > 0 for r in rr),
                    "runs_with_arch3": sum(r["n_episodes_size3"] > 0 for r in rr),
                    "episodes": len(eps), "episodes_size3": sum(e["size"] >= 3 for e in eps),
                    "lifetime_median_s": float(np.median(life)) if len(life) else None,
                    "lifetime_p95_s": float(np.percentile(life, 95)) if len(life) else None,
                    "lifetime_max_s": float(life.max()) if len(life) else 0.0,
                    "lifetimes_ge_1s": int((life >= 1).sum()), "lifetimes_ge_5s": int((life >= 5).sum()),
                    "persistent_runs": int(pers), "persistent_wilson95": wilson(pers, n),
                    "time_frac_arch_pct": 100 * float(np.mean([r["frac_checks_arch"] for r in rr])),
                    "peak_body_force_kN": max([e["body_force_N"] for e in eps], default=0.0) / 1000,
                    "max_rel_vt": max([e["max_rel_vt"] for e in eps], default=0.0),
                    "censored_episodes": sum(bool(e.get("censored")) for e in eps),
                    "deadlocks_with_arch_at_stop": sum(r.get("arch_at_stop") is not None for r in dl),
                    "evac_time_median": float(np.median([r["evacuation_time"] for r in rr if r["complete"]]))
                    if any(r["complete"] for r in rr) else None}
    ref = json.load(open(os.path.join(DATA, "derived", "arch_analysis.json")))
    o = {"script": "experiments/runs3/analyze_N5.py", "doc": __doc__, "cells": cells,
         "reference_v5_dt0.01": {k: ref[k] for k in ("n_runs", "complete", "runs_with_arch", "episodes",
                                                     "max_lifetime_s", "median_lifetime_s", "p95_lifetime_s",
                                                     "persistent_runs", "peak_body_force_kN", "max_rel_vt")}}
    json.dump(o, open(OUT, "w"), indent=1, default=float)
    return o


if __name__ == "__main__":
    o = main()
    for c, v in o["cells"].items():
        print(c, {k: v[k] for k in ("n", "complete", "deadlock", "runs_with_arch", "episodes", "lifetime_max_s",
                                    "persistent_runs", "peak_body_force_kN", "max_rel_vt", "deadlocks_with_arch_at_stop")})
