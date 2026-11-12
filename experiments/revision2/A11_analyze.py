"""A11: does the conference headline reproduce under this model's whole-run setup?

Conference [gang2026] (scan/probe_data/camera_ready.txt of the plan repository, Abstract and Sect. 4.6; plan/
CORRECTIONS_TABLE.md rows A1-A4): room bottleneck w = 0.8 m, 100 agents, 600 s, n = 25 (seeds 42-66), published
code: C1 (SFM) 0/25, C2 (SFM + TTC) 0/25, C3 (SFM + ORCA) 13/25, C4 (full blend) 14/25; noise control C1 + sigma,
sigma in {0, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.10, 0.20} m/s: {0, 1, 3, 9, 13, 18, 23, 24, 25}/25.
Headline: "0/25 for SFM and SFM+TTC vs 13-14/25 for ORCA-enabled configurations"; the gap is "categorical".

Inputs (existing whole runs, w = 0.8 m, 100 agents, 600 s, deadlock stop):
  C1  published flags  data/E1/E1_runs.jsonl mode E1a, seeds 42-241 (also the subset 42-66 = conference seeds)
  C1  CF               E1b, seeds 42-241, and data/velorca/whole.jsonl variant sfm, seeds 242-341
  C3  published (legacy ORCA)  data/E6/e6p.jsonl, seeds 428-477
  C3  CF (RVO2 ORCA)   data/E6/e6a.jsonl, seeds 242-427
  C1 + sigma  published flags data/E5/e5a.jsonl, CF data/E5/e5b.jsonl, seeds 42-141
  C2, C4  CF           data/revision2/A11/a11.jsonl (experiments/revision2/A11_whole.py), when present
Method: completion k/n with Wilson 95% intervals per configuration and flag set; against the conference k/25 by
Fisher's exact test (two-sided). Paired checks where seeds coincide: C2 vs C1 (CF, seeds 42-141, E1b) and C4 vs
C3 (CF, seeds 242-341, E6a), exact McNemar. Headline gap: the pooled no-ORCA cells against the ORCA cells, as the
difference of completion fractions (Newcombe hybrid score interval, unpaired).
Output: data/derived/rev2_A11.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import DATA, load_runs, mcnemar_exact, out_json, pdisp, sig, stats, wilson  # noqa: E402

CONF = {"C1": 0, "C2": 0, "C3": 13, "C4": 14}
CONF_SWEEP = dict(zip((0.0, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.10, 0.20), (0, 1, 3, 9, 13, 18, 23, 24, 25)))
A11_RUNS = os.path.join(DATA, "revision2", "A11", "a11.jsonl")


def P(*a):
    return os.path.join(DATA, *a)


def cell(R, label, src):
    k, n = sum(bool(r["complete"]) for r in R), len(R)
    p, lo, hi = wilson(k, n)
    seeds = sorted(r["seed"] for r in R)
    return {"label": label, "source": src, "k": k, "n": n, "frac": p, "ci95": [lo, hi], "pct": 100 * p,
            "pct_2sf": sig(100 * p), "ci95_pct_2sf": [sig(100 * lo), sig(100 * hi)],
            "seeds": f"{seeds[0]}-{seeds[-1]}" if n else None,
            "_by_seed": {r["seed"]: bool(r["complete"]) for r in R}}


def vs_conf(c, k_conf, n_conf=25):
    p = float(stats.fisher_exact([[c["k"], c["n"] - c["k"]], [k_conf, n_conf - k_conf]])[1])
    pc, lo, hi = wilson(k_conf, n_conf)
    return {"conf_k": k_conf, "conf_n": n_conf, "conf_frac": pc, "conf_ci95": [lo, hi],
            "diff": c["frac"] - pc, "fisher_p": p, "fisher_p_disp": pdisp(p)}


def newcombe(k1, n1, k2, n2):
    p1, l1, u1 = wilson(k1, n1)
    p2, l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def paired(a, b, la, lb):
    s = sorted(set(a["_by_seed"]) & set(b["_by_seed"]))
    x = [a["_by_seed"][i] for i in s]
    y = [b["_by_seed"][i] for i in s]
    bb = sum(u and not v for u, v in zip(x, y))
    cc = sum(v and not u for u, v in zip(x, y))
    p = mcnemar_exact(bb, cc)
    return {"first": la, "second": lb, "n_seeds": len(s), "both": sum(u and v for u, v in zip(x, y)),
            "first_only": bb, "second_only": cc, "p": p, "p_disp": pdisp(p)}


def main():
    E1 = load_runs(P("E1", "E1_runs.jsonl"))
    vel = load_runs(P("velorca", "whole.jsonl"))
    C = {}
    C["C1_pub"] = cell([r for r in E1 if r["mode"] == "E1a"], "C1 SFM, published flags", "E1a")
    C["C1_pub_conf_seeds"] = cell([r for r in E1 if r["mode"] == "E1a" and 42 <= r["seed"] <= 66],
                                  "C1 SFM, published flags, seeds 42-66", "E1a")
    C["C1_cf"] = cell([r for r in E1 if r["mode"] == "E1b"] + [r for r in vel if r["variant"] == "sfm"],
                      "C1 SFM, CF", "E1b + velorca sfm")
    C["C1_cf_E1b"] = cell([r for r in E1 if r["mode"] == "E1b"], "C1 SFM, CF, seeds 42-241", "E1b")
    C["C3_pub"] = cell(load_runs(P("E6", "e6p.jsonl")), "C3 SFM + ORCA (legacy), published flags", "E6p")
    C["C3_cf"] = cell(load_runs(P("E6", "e6a.jsonl")), "C3 SFM + force-coupled ORCA (RVO2), CF", "E6a")
    have = {}
    if os.path.exists(A11_RUNS):
        for r in load_runs(A11_RUNS):
            if abs(r["t_max"] - 600.0) < 1e-9:
                have.setdefault(r["config"], []).append(r)
    pending = []
    for v, lab in (("C2", "C2 SFM + TTC, CF"), ("C4", "C4 SFM + TTC + ORCA (RVO2), CF (crush off)")):
        R = have.get(v, [])
        if len(R) == 100:
            C[f"{v}_cf"] = cell(R, lab, "A11")
        else:
            pending.append({"cell": f"{v}_cf", "have": len(R), "need": 100})
    comp = {}
    for name, c in C.items():
        base = name.split("_")[0]
        if name.endswith("conf_seeds") or name == "C1_cf_E1b":
            comp[name] = vs_conf(c, CONF[base])
        elif base in CONF:
            comp[name] = vs_conf(c, CONF[base])
    pairs = {}
    if "C2_cf" in C:
        pairs["C2_vs_C1_cf"] = paired(C["C2_cf"], C["C1_cf_E1b"], "C2", "C1")
    if "C4_cf" in C:
        pairs["C4_vs_C3_cf"] = paired(C["C4_cf"], C["C3_cf"], "C4", "C3")
    # headline gap: ORCA-enabled minus no-ORCA cells, per flag set
    gap = {}
    for fs, no, yes in (("pub", ["C1_pub"], ["C3_pub"]), ("cf", ["C1_cf", "C2_cf"], ["C3_cf", "C4_cf"])):
        no = [x for x in no if x in C]
        yes = [x for x in yes if x in C]
        k0, n0 = sum(C[x]["k"] for x in no), sum(C[x]["n"] for x in no)
        k1, n1 = sum(C[x]["k"] for x in yes), sum(C[x]["n"] for x in yes)
        d, lo, hi = newcombe(k1, n1, k0, n0)
        gap[fs] = {"no_orca": no, "orca": yes, "k_no": k0, "n_no": n0, "k_orca": k1, "n_orca": n1,
                   "diff": d, "ci95": [lo, hi], "diff_pct_2sf": sig(100 * d),
                   "ci95_pct_2sf": [sig(100 * lo), sig(100 * hi)]}
    dc, lc, hc = newcombe(27, 50, 0, 50)
    gap["conference"] = {"k_no": 0, "n_no": 50, "k_orca": 27, "n_orca": 50, "diff": dc, "ci95": [lc, hc],
                         "diff_pct_2sf": sig(100 * dc), "ci95_pct_2sf": [sig(100 * lc), sig(100 * hc)]}
    # noise sweep
    sweep = {}
    for fs, f in (("pub", "e5a.jsonl"), ("cf", "e5b.jsonl")):
        R = load_runs(P("E5", f))
        for s in sorted({r["sigma"] for r in R}):
            c = cell([r for r in R if r["sigma"] == s], f"C1 + sigma {s}, {fs}", f)
            c.update(vs_conf(c, CONF_SWEEP[s]) if s in CONF_SWEEP else {})
            c.pop("_by_seed")
            sweep[f"{fs}_s{int(round(1000 * s))}"] = c
    for c in C.values():
        c.pop("_by_seed")
    cpu = {"wall_s_per_run": {}}
    for name, f in (("C1_cf_E1b", None), ("C3_pub", P("E6", "e6p.jsonl")), ("C3_cf", P("E6", "e6a.jsonl"))):
        R = [r for r in E1 if r["mode"] == "E1b"] if f is None else load_runs(f)
        cpu["wall_s_per_run"][name] = sum(r["wall_s"] for r in R) / len(R)
    cpu["estimate_cpu_h_per_100"] = {
        "C2_cf": 100 * 1.3 * cpu["wall_s_per_run"]["C1_cf_E1b"] / 3600,
        "C4_cf": 100 * 1.06 * cpu["wall_s_per_run"]["C3_cf"] / 3600,
        "C4_pub": 100 * 1.0 * cpu["wall_s_per_run"]["C3_pub"] / 3600}
    cpu["rule"] = ("E1b, E6a, E6p mean wall time per run times the per-simulated-second cost ratio of the "
                   "configuration in E11 (w = 1.0-1.8 m, CF): C2/C1 about 1.3, C4/C3 (RVO2) about 1.0-1.06; "
                   "C4 with published flags taken equal to E6p (legacy ORCA dominates)")
    res = {"script": "experiments/revision2/A11_analyze.py", "doc": __doc__, "conference": {
        "completion": {k: {"k": v, "n": 25} for k, v in CONF.items()},
        "sweep": {str(k): {"k": v, "n": 25} for k, v in CONF_SWEEP.items()}},
        "cells": C, "vs_conference": comp, "paired": pairs, "gap": gap, "sweep": sweep, "pending": pending,
        "cost": cpu}
    print("wrote", out_json("A11", res))
    for n, c in C.items():
        x = comp.get(n, {})
        print(f"{n:20s} {c['k']:4d}/{c['n']:<4d} {100 * c['frac']:5.1f}% [{100 * c['ci95'][0]:.1f}, "
              f"{100 * c['ci95'][1]:.1f}]  conf {x.get('conf_k')}/25 p={x.get('fisher_p_disp')}")
    for k, s in sweep.items():
        print(f"{k:10s} {s['k']:3d}/{s['n']}  conf {s.get('conf_k')}/25  p={s.get('fisher_p_disp')}")
    print("gap", json.dumps(gap))
    print("pairs", json.dumps(pairs))
    print("pending", pending, "cost", json.dumps(cpu["estimate_cpu_h_per_100"]))


if __name__ == "__main__":
    main()
