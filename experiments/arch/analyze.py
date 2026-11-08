"""Contact-arch analysis (paper Sect. 5.3): data/arch/arch.jsonl -> data/derived/arch_analysis.json.

Counts per run and pooled: runs with any jamb-to-jamb contact chain, episodes (all sizes and size >= 3),
episode lifetimes, the fraction of checks (every 0.1 s) with a chain present, the largest total body force in a
chain, the largest relative tangential speed between contacting members, and persistent arches (episodes of
>= 10 s) with a Wilson 95% interval on the fraction of runs that show one. Run outcomes (completion, deadlock)
and, for deadlocked runs, the residual size and whether any two residual agents touch.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IN = os.path.join(ROOT, "data", "arch", "arch.jsonl")
OUT = os.path.join(ROOT, "data", "derived", "arch_analysis.json")
PERSIST = 10.0


def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def touching(res):
    for i in range(len(res)):
        for j in range(i + 1, len(res)):
            a, b = res[i], res[j]
            if math.dist(a["pos"], b["pos"]) < a["r"] + b["r"]:
                return True
    return False


def main():
    R = [json.loads(l) for l in open(IN) if l.strip()]
    eps = [e for r in R for e in r["episodes"]]
    life = np.array([e["t1"] - e["t0"] for e in eps]) if eps else np.array([])
    n = len(R)
    pers = sum(r["n_persistent"] > 0 for r in R)
    checks = sum(r["n_checks"] for r in R)
    dl = [r for r in R if r["deadlock"]]
    o = {"script": "experiments/arch/analyze.py", "n_runs": n, "v0_mean": R[0]["v0_mean"],
         "seeds": sorted(r["seed"] for r in R), "flags": R[0]["flags"],
         "complete": sum(r["complete"] for r in R), "deadlock": len(dl),
         "capped": sum((not r["complete"]) and (not r["deadlock"]) for r in R),
         "evac_time_median": float(np.median([r["evacuation_time"] for r in R if r["complete"]]))
         if any(r["complete"] for r in R) else None,
         "runs_with_arch": sum(r["n_episodes"] > 0 for r in R),
         "runs_with_arch3": sum(r["n_episodes_size3"] > 0 for r in R),
         "episodes": len(eps), "episodes_size3": sum(e["size"] >= 3 for e in eps),
         "max_lifetime_s": float(life.max()) if len(life) else 0.0,
         "median_lifetime_s": float(np.median(life)) if len(life) else 0.0,
         "p95_lifetime_s": float(np.percentile(life, 95)) if len(life) else 0.0,
         "lifetimes_ge_1s": int((life >= 1.0).sum()), "lifetimes_ge_5s": int((life >= 5.0).sum()),
         "persistent_def_s": PERSIST, "persistent_runs": pers, "persistent_wilson95": wilson(pers, n),
         "persistent_episodes": int((life >= PERSIST).sum()),
         "time_frac_arch_pct": 100.0 * sum(r["frac_checks_arch"] * r["n_checks"] for r in R) / max(checks, 1),
         "peak_body_force_kN": max((e["body_force_N"] for e in eps), default=0.0) / 1000.0,
         "max_rel_vt": max((e["max_rel_vt"] for e in eps), default=0.0),
         "censored_episodes": sum(bool(e.get("censored")) for e in eps),
         "deadlocks": [{"seed": r["seed"], "n_res": r["n_remaining"], "contact": touching(r.get("residual", []))}
                       for r in dl],
         "deadlocks_with_contact": sum(touching(r.get("residual", [])) for r in dl),
         "size_max": max((e["size"] for e in eps), default=0)}
    with open(OUT, "w") as f:
        json.dump(o, f, indent=1, default=float)
    print({k: v for k, v in o.items() if k not in ("seeds", "flags", "deadlocks")})


if __name__ == "__main__":
    main()
