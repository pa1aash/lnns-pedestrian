"""B1 analysis: the density-throttle ablation (veff_throttle = "off", experiments/revision2/B1_throttle.py)
against the throttle-on runs with the same spawns.

a  Completion against width, throttle off: binomial-logit MLE, w50 = -a/b with the 95% bootstrap interval of
   experiments/revision/B2_analyze.w50_fit (runs resampled within width, 2000 resamples, PCG64(7)). Throttle on:
   the same fit on the same five widths and seeds (E1b at 0.80 m, B2 at 0.84-0.96 m), and the published
   eleven-width w50 (rev_B2.json fit_all, 0.878 m). Per width: completion off / on, paired by seed (McNemar exact).
   HEADLINE CHANGE if the throttle-off w50 lies outside the published 95% interval.
b  w = 0.8 m, seeds 242-341: completion of SFM and force-coupled ORCA (RVO2), off against on (velorca "sfm",
   E6a), Wilson intervals, paired McNemar; final state (deadlock / capped).
c  CroMa (D3 cells C1_cf, C3_rvo2_cf; agent numbers of the participants who passed; 2.0 / 0.2 m): per-run flow,
   flow ratio to the corrected human flows, gaps right-censored at 600 s, completions, with the D3 estimator
   (D_croma_integrity.d4 unchanged), against D3 (throttle on) paired by seed. HEADLINE CHANGE if the range of
   flow ratios over the four Sect. 7 variants (three from D3 for the variants not rerun) leaves 0.40-0.60.
Output: data/derived/rev2_B1.json.  Usage: B1_analyze.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import DATA, mcnemar_exact, np, pdisp, stats, wilson  # noqa: E402
import B2_analyze as B2A  # noqa: E402  (experiments/revision)
import fix_a7 as F  # noqa: E402
import D3_analyze as D3A  # noqa: E402
import D_croma_integrity as DI  # noqa: E402

B1 = os.path.join(DATA, "revision2", "B1")


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []


def wil(k, n):
    p, lo, hi = wilson(k, n)
    return {"k": int(k), "n": int(n), "p": float(p), "ci95": [float(lo), float(hi)]}


def part_a():
    off = [{"w": round(x["width"], 2), "seed": x["seed"], "complete": bool(x["complete"]), "deadlock": bool(x["deadlock"])}
           for x in jl(os.path.join(B1, "b1a.jsonl"))]
    on_all = B2A.runs()
    on_all, _ = B2A.dedupe(on_all)
    W = sorted({r["w"] for r in off})
    on = [{"w": round(r["w"], 2), "seed": r["seed"], "complete": r["complete"]} for r in on_all if round(r["w"], 2) in W]
    o = {"widths": W, "n_runs": len(off)}
    if len(W) >= 3:
        B2A.RNG = np.random.default_rng(7)
        o["off"] = B2A.w50_fit(off)
        B2A.RNG = np.random.default_rng(7)
        o["on_same_widths"] = B2A.w50_fit(on)
        pub = json.load(open(os.path.join(rev2lib.DERIVED, "rev_B2.json")))
        o["on_published"] = {k: pub["fit_all"][k] for k in ("w50_m", "w50_ci95")}
        o["dw50_off_minus_on_m"] = o["off"]["w50_m"] - o["on_same_widths"]["w50_m"]
        o["dw50_off_minus_published_m"] = o["off"]["w50_m"] - o["on_published"]["w50_m"]
        lo, hi = o["on_published"]["w50_ci95"]
        o["headline_change"] = not (lo <= o["off"]["w50_m"] <= hi)
    per = []
    for w in W:
        a = {r["seed"]: r["complete"] for r in off if r["w"] == w}
        b = {r["seed"]: r["complete"] for r in on if r["w"] == w}
        s = sorted(set(a) & set(b))
        n10 = sum(a[x] and not b[x] for x in s)
        n01 = sum(b[x] and not a[x] for x in s)
        p = mcnemar_exact(n10, n01)
        per.append({"w": w, "off": wil(sum(a.values()), len(a)), "on": wil(sum(b[x] for x in s), len(s)),
                    "off_only": n10, "on_only": n01, "mcnemar_p": p, "mcnemar_p_disp": pdisp(p),
                    "off_deadlock": sum(r["deadlock"] for r in off if r["w"] == w)})
    o["per_width"] = per
    b, c = sum(p["off_only"] for p in per), sum(p["on_only"] for p in per)
    o["pooled_paired"] = {"n": sum(p["off"]["n"] for p in per), "off_only": b, "on_only": c,
                          "mcnemar_p": mcnemar_exact(b, c), "mcnemar_p_disp": pdisp(mcnemar_exact(b, c))}
    return o


def part_b():
    R = jl(os.path.join(B1, "b1b.jsonl"))
    on = {"sfm": {r["seed"]: r for r in jl(os.path.join(DATA, "velorca", "whole.jsonl")) if r["variant"] == "sfm"},
          "orca": {r["seed"]: r for r in jl(os.path.join(DATA, "E6", "e6a.jsonl")) if 242 <= r["seed"] <= 341}}
    o = {}
    for v in ("sfm", "orca"):
        off = {r["seed"]: r for r in R if r["variant"] == v}
        if not off:
            continue
        s = sorted(set(off) & set(on[v]))
        n10 = sum(off[x]["complete"] and not on[v][x]["complete"] for x in s)
        n01 = sum(on[v][x]["complete"] and not off[x]["complete"] for x in s)
        p = mcnemar_exact(n10, n01)
        ev = [off[x]["evacuation_time"] for x in s if off[x]["complete"]]
        o[v] = {"off": wil(sum(off[x]["complete"] for x in s), len(s)),
                "on": wil(sum(on[v][x]["complete"] for x in s), len(s)),
                "off_deadlock": sum(off[x]["deadlock"] for x in s), "off_capped": sum(off[x]["capped"] for x in s),
                "off_only": n10, "on_only": n01, "mcnemar_p": p, "mcnemar_p_disp": pdisp(p),
                "off_median_evac_s": float(np.median(ev)) if ev else None,
                "off_median_remaining": float(np.median([off[x]["n_remaining"] for x in s if not off[x]["complete"]]))
                if any(not off[x]["complete"] for x in s) else 0.0}
    return o


def part_c():
    path = os.path.join(B1, "b1c.jsonl")
    R = jl(path)
    cells = [c for c in ("C1_cf", "C3_rvo2_cf") if sum(r["cell"] == c for r in R) >= 2]
    if not cells:
        return {}
    rev = json.load(open(D3A.REV_D))
    H = rev["humans_corrected"]["runs"]
    hflow = [h["flow_per_s"] for h in H]
    hb = {h["run"]: h["flow_per_s"] for h in H}
    raw = os.path.join(B1, "raw_c")
    M = {c: [u for u in (D3A.load_run(r, raw) for r in R if r["cell"] == c) if u] for c in cells}
    DI.CELLS = cells
    d = DI.d4(M, hflow, hb)
    on = rev["D3"]["rerun"]["per_variant"]
    R3 = {(r["cell"], r["seed"]): r for r in jl(D3A.IN)}
    raw3 = os.path.join(os.path.dirname(D3A.IN), "raw")
    o = {"cells": cells, "per_variant": {}}
    for c in cells:
        X = {u["seed"]: u for u in M[c]}
        Y = {s: D3A.load_run(R3[(c, s)], raw3) for s in X if (c, s) in R3}
        s = sorted(k for k in X if Y.get(k))
        lr = np.log([X[k]["flow"] / Y[k]["flow"] for k in s])
        h = stats.t.ppf(0.975, len(lr) - 1) * lr.std(ddof=1) / math.sqrt(len(lr)) if len(lr) >= 2 else float("nan")
        n10 = sum(X[k]["complete"] and not Y[k]["complete"] for k in s)
        n01 = sum(Y[k]["complete"] and not X[k]["complete"] for k in s)
        dd = d[c]
        lng = [X[k]["flow"] for k in X if X[k]["run"] in ("4D030", "4D040")]
        sht = [X[k]["flow"] for k in X if X[k]["run"] not in ("4D030", "4D040")]
        o["per_variant"][c] = {
            "n": dd["n"], "complete": dd["complete"], "deadlock": dd["deadlock"], "capped": dd["capped"],
            "flow": dd["flow"], "flow_ratio": dd["flow_ratio"], "flow_ratio_matched": dd["flow_ratio_matched"],
            "window_flow": F.tci([u["flow_w_obs"] for u in M[c]]),
            "flow_long": float(np.mean(lng)) if lng else None, "flow_short": float(np.mean(sht)) if sht else None,
            "n_censored": dd["n_censored"], "gap_complete": dd["gap_complete"], "km_median": dd["km_median"],
            "km_median_reached": dd["km_median_reached"], "km_median_lower_bound": dd["km_median_lower_bound"],
            "c_median_lower_bound": dd["c_median_lower_bound"],
            "on": {k: on[c][k] for k in ("complete", "deadlock", "capped", "n_censored")} |
                  {"flow_ratio": on[c]["flow_ratio"]["ratio"], "flow_ratio_ci95": on[c]["flow_ratio"]["ci95"],
                   "gap_complete_max": on[c]["gap_complete"]["max"]},
            "paired_flow_ratio_off_over_on": {"n": len(s), "geo": float(math.exp(lr.mean())) if len(lr) else None,
                                              "ci95": [float(math.exp(lr.mean() - h)), float(math.exp(lr.mean() + h))]
                                              if len(lr) >= 2 else None},
            "completion_off_only": n10, "completion_on_only": n01, "mcnemar_p": mcnemar_exact(n10, n01),
            "mcnemar_p_disp": pdisp(mcnemar_exact(n10, n01))}
    if len(cells) == 2:
        rs = {c: on[c]["flow_ratio"]["ratio"] for c in on}
        rs.update({c: o["per_variant"][c]["flow_ratio"]["ratio"] for c in cells})
        o["range_with_off"] = {"min": min(rs.values()), "max": max(rs.values()), "ratios": rs}
        o["range_on"] = {"min": rev["D3"]["rerun"]["range"]["min"], "max": rev["D3"]["rerun"]["range"]["max"]}
        o["headline_change"] = (round(o["range_with_off"]["min"], 2) != round(o["range_on"]["min"], 2)
                                or round(o["range_with_off"]["max"], 2) != round(o["range_on"]["max"], 2))
    return o


def main():
    o = {"a": part_a(), "b": part_b(), "c": part_c()}
    print(rev2lib.out_json("B1", o))
    a = o["a"]
    if "off" in a:
        print("a w50 off", round(a["off"]["w50_m"], 3), a["off"]["w50_ci95"], "on", round(a["on_same_widths"]["w50_m"], 3),
              a["on_same_widths"]["w50_ci95"], "HEADLINE CHANGE" if a["headline_change"] else "")
    for p in a["per_width"]:
        print(" w", p["w"], "off", p["off"]["k"], "/", p["off"]["n"], "on", p["on"]["k"], "/", p["on"]["n"], "McNemar", p["mcnemar_p_disp"])
    for v, d in o["b"].items():
        print("b", v, "off", d["off"]["k"], "/", d["off"]["n"], "on", d["on"]["k"], "/", d["on"]["n"], "p", d["mcnemar_p_disp"])
    for c, d in o["c"].get("per_variant", {}).items():
        print("c", c, "n", d["n"], "k", d["complete"], "ratio", round(d["flow_ratio"]["ratio"], 3), "on", round(d["on"]["flow_ratio"], 3))
    if "range_with_off" in o["c"]:
        print("c range", o["c"]["range_with_off"], "HEADLINE CHANGE" if o["c"]["headline_change"] else "")


if __name__ == "__main__":
    main()
