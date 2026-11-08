"""E5a analysis: completion against noise amplitude in published-reproduction mode.

Input:  data/E5/e5a.jsonl (experiments/E5/e5_sweep.py E5a; all flags default, w = 0.8 m, 100 agents,
        seeds 42-141, 600 s), data/E1/E1_runs.jsonl (sigma = 0: E1a, same seeds 42-141).
Output: data/derived/E5a_analysis.json.

Same definitions as experiments/E5/analyze.py (Wilson 95% per sigma; binomial logit with a profile-likelihood
interval for sigma50). The fit uses sigma in [0.02, 0.07] (the levels around sigma50; 0.10 and 0.20 are at or
near 100% completion), and again over all eight levels. Reference: conference sigma50 = 0.049 m/s (n = 25).
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import fit, wilson, ROOT, E1, SEEDS, CONF_SIGMA50  # noqa: E402

IN = os.path.join(ROOT, "data", "E5", "e5a.jsonl")
OUT = os.path.join(ROOT, "data", "derived", "E5a_analysis.json")
B = os.path.join(ROOT, "data", "derived", "E5_analysis.json")


def main():
    R = [json.loads(ln) for ln in open(IN)]
    c = defaultdict(lambda: [0, 0])
    for r in R:
        c[r["sigma"]][0] += bool(r["complete"])
        c[r["sigma"]][1] += 1
    z = [json.loads(ln) for ln in open(E1)]
    z = [r for r in z if r["mode"] == "E1a" and r["seed"] in SEEDS]
    c0 = [sum(bool(r["complete"]) for r in z), len(z)]
    sig = sorted(c)
    per = {f"s{s:g}".replace(".", "p"): {"sigma": s, "k": c[s][0], "n": c[s][1], "wilson": wilson(*c[s])}
           for s in sig}
    per["s0"] = {"sigma": 0.0, "k": c0[0], "n": c0[1], "wilson": wilson(*c0), "source": "E1a seeds 42-141"}
    core = [s for s in sig if s <= 0.07 + 1e-12]
    fc = fit(core, [c[s][0] for s in core], [c[s][1] for s in core])
    fa = fit(sig, [c[s][0] for s in sig], [c[s][1] for s in sig])
    b = json.load(open(B))["logistic_noise_levels"]
    out = {"mode": "published-reproduction", "width_m": 0.8, "n_agents": 100, "seeds": "42-141", "t_max_s": 600,
           "per_sigma": per, "logistic_core": fc, "logistic_all_levels": fa,
           "conference_sigma50": CONF_SIGMA50,
           "conference_inside_ci": fc["ci95_profile"][0] <= CONF_SIGMA50 <= fc["ci95_profile"][1],
           "corrected_sigma50": b["sigma50"],
           "corrected_over_published": b["sigma50"] / fc["sigma50"],
           "ci_overlap_with_corrected": not (b["ci95_profile"][1] < fc["ci95_profile"][0]
                                             or fc["ci95_profile"][1] < b["ci95_profile"][0])}
    json.dump(out, open(OUT, "w"), indent=1)
    for k in sorted(per, key=lambda k: per[k]["sigma"]):
        print(k, per[k]["k"], "/", per[k]["n"], [round(v, 3) for v in per[k]["wilson"]])
    print("fit core", fc)
    print("fit all", fa)
    print({k: out[k] for k in ("conference_inside_ci", "corrected_over_published", "ci_overlap_with_corrected")})


if __name__ == "__main__":
    main()
