"""Analysis of run-N1 (lone-trap noise at the calibrated sigma, 20 seeds per lone keystone).

Inputs: data/N1/n1.jsonl, data/N1/sigma_n1.json, data/E2/e2_quench.jsonl (C3 outcomes, E2 noise at 0.07).
Output: data/derived/N1_analysis.json.
  rate        freed fraction over runs (Wilson) and the paired difference noise - C3 RVO2 over snapshots
              (mean of p_i - c_i, bootstrap over snapshots); the same against C3 published.
  per snapshot p_i = k_i / 20; seeds disagree where 0 < k_i < 20.
  identity    unresolved under noise: p_i < 0.5; under C3: not freed in the unperturbed run. J(noise, C3 RVO2),
              J(noise, C3 published) and the noise-versus-noise reference J(noise, noise') from the seed halves
              0-9 and 10-19 (unresolved: k < 5 of 10), each with its bootstrap interval and independence reference.
  association p_i between snapshots that C3 RVO2 frees and does not (Mann-Whitney, AUC); the same for C3 published.
  time        Kaplan-Meier median time to free the blocker over runs (censored at 120 s).
  E2 check    freed fraction at sigma = 0.07 in E2 (5 seeds) beside N1.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "E3"))
import numpy as np  # noqa: E402
import stats3  # noqa: E402
from survival import km  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "N1_analysis.json")
T_Q = 120.0


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def main():
    sig = json.load(open(os.path.join(DATA, "N1", "sigma_n1.json")))
    R = jl(os.path.join(DATA, "N1", "n1.jsonl"))
    sel = {s["tag"]: s for s in json.load(open(os.path.join(DATA, "derived", "selection.json")))["E2"]["snapshots"]}
    E2 = jl(os.path.join(DATA, "E2", "e2_quench.jsonl"))
    tags = sorted({r["job_id"].split("|")[0] for r in R})
    def freed(r):
        t = r["exits"].get(str(sel[r["job_id"].split("|")[0]]["blocker"]))
        return t is not None and t <= T_Q + 1e-9, t
    k = {t: [0] * 20 for t in tags}
    times, events = [], []
    for r in R:
        t = r["job_id"].split("|")[0]
        f, tt = freed(r)
        k[t][r["rep"]] = int(f)
        times.append(tt if f else T_Q)
        events.append(f)
    c3 = {}
    e207 = {}
    for r in E2:
        t, arm, rep = r["job_id"].split("|")
        if t not in k:
            continue
        if arm in ("C3_rvo2", "C3_pub") and rep == "u":
            c3.setdefault(arm, {})[t] = freed(r)[0]
        if arm == "noise0.07":
            e207.setdefault(t, []).append(freed(r)[0])
    n_runs = len(R)
    kk = int(sum(events))
    p = np.array([np.mean(k[t]) for t in tags])
    rng = np.random.default_rng(stats3.SEED)
    o = {"script": "experiments/runs3/analyze_N1.py", "doc": __doc__, "sigma_n1": sig["sigma_n1"],
         "sigma_fit": {"inversion": sig["inversion"], "targets": sig["targets"], "E2_noise": sig["E2_noise"]},
         "n_snapshots": len(tags), "n_runs": n_runs, "seeds_per_snapshot": 20,
         "rate": {"freed": kk, "n": n_runs, "fraction": kk / n_runs, "wilson95": stats3.wilson(kk, n_runs)}}
    for arm in ("C3_rvo2", "C3_pub"):
        c = np.array([float(c3[arm][t]) for t in tags])
        d = p - c
        bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(stats3.B)]
        o["rate"][f"diff_vs_{arm}"] = {"diff": float(d.mean()), "ci95": [float(np.percentile(bs, 2.5)),
                                                                        float(np.percentile(bs, 97.5))],
                                        "C3_freed": int(c.sum()), "C3_n": len(c)}
    U_n = {t for t in tags if np.mean(k[t]) < 0.5}
    U_h1 = {t for t in tags if sum(k[t][:10]) < 5}
    U_h2 = {t for t in tags if sum(k[t][10:]) < 5}
    o["identity"] = {"unresolved_noise": sorted(U_n),
                     "noise_vs_noise_halves": stats3.jaccard_stats(U_h1, U_h2, tags, rng),
                     "halves_unresolved": [sorted(U_h1), sorted(U_h2)]}
    for arm in ("C3_rvo2", "C3_pub"):
        U_c = {t for t in tags if not c3[arm][t]}
        o["identity"][f"noise_vs_{arm}"] = stats3.jaccard_stats(U_n, U_c, tags, rng)
        o["identity"][f"unresolved_{arm}"] = sorted(U_c)
        o.setdefault("association", {})[arm] = stats3.mann_whitney(
            [p[i] for i, t in enumerate(tags) if c3[arm][t]], [p[i] for i, t in enumerate(tags) if not c3[arm][t]])
    o["per_snapshot"] = {t: {"k": sum(k[t]), "n": 20, "C3_rvo2_freed": c3["C3_rvo2"][t], "C3_pub_freed": c3["C3_pub"][t],
                             "E2_sigma0.07_k": int(sum(e207.get(t, []))), "E2_sigma0.07_n": len(e207.get(t, []))}
                         for t in tags}
    dis = sum(0 < sum(k[t]) < 20 for t in tags)
    o["seeds_disagree"] = {"snapshots": int(dis), "n": len(tags)}
    K = km(times, events, T_Q)
    K.pop("curve", None)
    o["time_to_free_km"] = K
    ke = sum(sum(v) for v in e207.values()); ne = sum(len(v) for v in e207.values())
    o["E2_sigma0.07"] = {"freed": int(ke), "n": ne, "wilson95": stats3.wilson(ke, ne)}
    json.dump(o, open(OUT, "w"), indent=1, default=float)
    return o


if __name__ == "__main__":
    o = main()
    I = o["identity"]
    print("sigma", o["sigma_n1"], "rate", o["rate"]["freed"], "/", o["rate"]["n"], "diff rvo2", o["rate"]["diff_vs_C3_rvo2"])
    print("J noise-noise", I["noise_vs_noise_halves"]["jaccard"], I["noise_vs_noise_halves"]["ci95"],
          "J noise-rvo2", I["noise_vs_C3_rvo2"]["jaccard"], I["noise_vs_C3_rvo2"]["ci95"],
          "indep", I["noise_vs_C3_rvo2"]["independent_mean"])
    print("assoc", o["association"], "disagree", o["seeds_disagree"], "KM", o["time_to_free_km"].get("median"))
