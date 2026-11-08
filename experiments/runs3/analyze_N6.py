"""Analysis of run-N6 (continuation of the pair minimum to its loss under a lateral bias, and quenches past it).

Inputs: data/N6/n6_static.jsonl, data/N6/n6_quench.jsonl. Output: data/derived/N6_analysis.json.
  static   per (snapshot, sign) with a located fold: log-log slopes against delta = 1 - b / b_f of the
           minimum-saddle distance, the work W and mu1 at the minimum (95% t intervals over the six delta);
           normal form of a smooth saddle-node: 1/2, 3/2 and 1/2. Pooled: medians and ranges of the slopes,
           count within 0.1 of each prediction; mu1 at the smallest delta relative to mu1 at delta = 0.3;
           relative Jacobian jump between minimum and saddle at the smallest delta; geometry at the fold
           (member whose closest wall point is a segment end: t <= 1e-3 or t >= 1 - 1e-3); b_f against the
           bisection threshold b*.
  quench   first-exit (passage) time against eps (b = b_f (1 + eps)), freed counts per eps; per (snapshot,
           sign) the log-log slope of passage time on eps; pooled median slope (smooth saddle-node: -1/2).
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import stats3  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "N6_analysis.json")


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []


def summ(v):
    v = [x for x in v if x is not None]
    return {"median": float(np.median(v)), "min": float(min(v)), "max": float(max(v)), "n": len(v)} if v else None


def main():
    S = jl(os.path.join(DATA, "N6", "n6_static.jsonl"))
    Q = jl(os.path.join(DATA, "N6", "n6_quench.jsonl"))
    rows, sl = {}, defaultdict(list)
    at_end = 0
    for r in S:
        if r.get("b_f") is None:
            rows[r["job_id"]] = {"status": r["status"]}
            continue
        sc = [x for x in r["scan"] if x.get("converged") and x.get("distinct")]
        d = [x["delta"] for x in sc]
        e = {"dist": stats3.loglog_slope(d, [x["dist"] for x in sc]),
             "W": stats3.loglog_slope(d, [x["W"] for x in sc]) if all(x["W"] > 0 for x in sc) else None,
             "mu1": stats3.loglog_slope(d, [x["mu1_min"] for x in sc]) if all(x["mu1_min"] > 0 for x in sc) else None}
        g = r["geom_fold"]["walls"]
        end = any(w["t"] <= 1e-3 or w["t"] >= 1 - 1e-3 for m in g for w in m if w["gap"] < 0.2)
        at_end += end
        mu_ratio = sc[-1]["mu1_min"] / sc[0]["mu1_min"] if sc else None
        rows[r["job_id"]] = {"b_f": r["b_f"], "b_star_bisection": r["b_star_bisection"],
                             "b_f_over_bisection": r["b_f"] / r["b_star_bisection"] if r["b_star_bisection"] else None,
                             "slopes": e, "mu1_ratio_smallest_to_largest_delta": mu_ratio,
                             "jac_jump_smallest_delta": sc[-1].get("jac_jump") if sc else None,
                             "member_at_segment_end": bool(end), "n_points": len(sc)}
        for k in ("dist", "W", "mu1"):
            if e[k]:
                sl[k].append(e[k]["slope"])
    pred = {"dist": 0.5, "W": 1.5, "mu1": 0.5}
    st = {k: dict(summ(sl[k]) or {}, prediction_saddle_node=pred[k],
                  within_0p1_of_prediction=int(sum(abs(x - pred[k]) <= 0.1 for x in sl[k]))) for k in pred}
    for k, p in (("dist", 1.0), ("W", 2.0)):
        st[k]["within_0p1_of_" + str(p).replace(".", "p")] = int(sum(abs(x - p) <= 0.1 for x in sl[k]))
    fold_rows = [v for v in rows.values() if "b_f" in v]
    o = {"script": "experiments/runs3/analyze_N6.py", "doc": __doc__, "n_jobs": len(S), "n_fold": len(fold_rows),
         "status_counts": {s: sum(r["status"] == s for r in S) for s in sorted({r["status"] for r in S})},
         "slopes": st, "member_at_segment_end_at_fold": int(at_end),
         "mu1_ratio": summ([v["mu1_ratio_smallest_to_largest_delta"] for v in fold_rows]),
         "jac_jump": summ([v["jac_jump_smallest_delta"] for v in fold_rows]),
         "b_f_over_bisection": summ([v["b_f_over_bisection"] for v in fold_rows]), "per_job": rows}
    if Q:
        by = defaultdict(dict)
        for r in Q:
            by[(r["tag"], r["sign"])][r["eps"]] = r
        eps = sorted({r["eps"] for r in Q})
        qs = []
        for key, m in by.items():
            xs = [e for e in eps if e in m and m[e]["freed"]]
            if len(xs) >= 3:
                f = stats3.loglog_slope(xs, [m[e]["first_t"] for e in xs])
                if f:
                    qs.append(f["slope"])
        o["quench"] = {"n_runs": len(Q), "eps": eps,
                       "freed": {f"{e:g}": int(sum(r["freed"] for r in Q if r["eps"] == e)) for e in eps},
                       "n": {f"{e:g}": int(sum(1 for r in Q if r["eps"] == e)) for e in eps},
                       "passage_median_s": {f"{e:g}": float(np.median([r["first_t"] for r in Q if r["eps"] == e and r["freed"]]))
                                            if any(r["freed"] for r in Q if r["eps"] == e) else None for e in eps},
                       "slope_passage_vs_eps": dict(summ(qs) or {}, prediction_saddle_node=-0.5),
                       "b_f_source": {s: sum(r["b_f_source"] == s for r in Q) for s in ("continuation", "bisection")}}
    json.dump(o, open(OUT, "w"), indent=1, default=float)
    return o


if __name__ == "__main__":
    o = main()
    print("fold", o["n_fold"], "/", o["n_jobs"], o["status_counts"], "at end", o["member_at_segment_end_at_fold"])
    print("slopes", o["slopes"], "mu1 ratio", o["mu1_ratio"], "bf/bis", o["b_f_over_bisection"])
    print("quench", o.get("quench"))
