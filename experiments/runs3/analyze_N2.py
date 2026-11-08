"""Analysis of run-N2 (E6b repeated with an independent noise stream, same spawns).

Inputs: data/N2/n2.jsonl, data/E6/e6a.jsonl (C3 RVO2), data/E6/e6b.jsonl (C1 + sigma*).
Output: data/derived/N2_analysis.json.
  completion  per resolver, Wilson; paired difference N2 - E6b and N2 - E6a (Newcombe).
  identity    failure set = runs not completed in 600 s. J(E6b, N2) is the noise-versus-noise reference;
              J(E6a, N2) and J(E6a, E6b) beside it; each with its bootstrap interval over seeds and the
              independence reference (labels permuted).
  association odds ratio (conditional MLE, exact interval, Fisher p) that a seed fails under one resolver
              given it fails under the other: E6b-N2, E6a-N2, E6a-E6b.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import stats3  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "N2_analysis.json")


def jl(p):
    return {r["seed"]: r for r in (json.loads(l) for l in open(p) if l.strip())}


def main():
    S = {"E6a": jl(os.path.join(DATA, "E6", "e6a.jsonl")), "E6b": jl(os.path.join(DATA, "E6", "e6b.jsonl")),
         "N2": jl(os.path.join(DATA, "N2", "n2.jsonl"))}
    seeds = sorted(S["N2"])
    assert all(s in S["E6a"] and s in S["E6b"] for s in seeds)
    n = len(seeds)
    c = {k: np.array([bool(v[s]["complete"]) for s in seeds]) for k, v in S.items()}
    fail = {k: {s for s, ok in zip(seeds, v) if not ok} for k, v in c.items()}
    rng = np.random.default_rng(stats3.SEED)
    o = {"script": "experiments/runs3/analyze_N2.py", "doc": __doc__, "n": n, "sigma": S["N2"][seeds[0]]["sigma"],
         "completion": {k: {"k": int(v.sum()), "n": n, "wilson95": stats3.wilson(int(v.sum()), n)} for k, v in c.items()},
         "identity": {}, "association": {}}
    for a, b in (("E6b", "N2"), ("E6a", "N2"), ("E6a", "E6b")):
        x, y = c[b], c[a]
        o["completion"][f"diff_{b}_minus_{a}"] = stats3.newcombe_paired(int((x & y).sum()), int((x & ~y).sum()),
                                                                       int((~x & y).sum()), int((~x & ~y).sum()))
        o["identity"][f"{a}_vs_{b}"] = stats3.jaccard_stats(fail[a], fail[b], seeds, rng)
        fa, fb = ~c[a], ~c[b]
        o["association"][f"{a}_vs_{b}"] = stats3.odds_ratio(int((fa & fb).sum()), int((fa & ~fb).sum()),
                                                           int((~fa & fb).sum()), int((~fa & ~fb).sum()))
    o["outcomes"] = {k: {"deadlock": int(sum(bool(v[s]["deadlock"]) for s in seeds)),
                         "capped_moving": int(sum(bool(v[s].get("capped")) for s in seeds))} for k, v in S.items()}
    json.dump(o, open(OUT, "w"), indent=1, default=float)
    return o


if __name__ == "__main__":
    o = main()
    print({k: v["k"] for k, v in o["completion"].items() if "k" in v})
    for k, v in o["identity"].items():
        print(k, round(v["jaccard"], 3), [round(x, 3) for x in v["ci95"]], "indep", round(v["independent_mean"], 3))
    for k, v in o["association"].items():
        print(k, round(v["odds_ratio"], 2), [round(x, 2) for x in v["ci95"]], v["fisher_p"])
