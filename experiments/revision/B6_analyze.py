"""B6 analysis: the pair standoff under a line goal (w2_goal = "line").

Inputs (data/revision/B6/): static.jsonl (B6_static.py), quench.jsonl (B6_quench.py), and when present
gen_line.jsonl (B6_gen.py); data/E7b/e7b_lib.jsonl (point-goal generation, same seeds).
Output: data/derived/rev_B6.json.
  static   strict minima kept under the line goal (Hessian -sym(J) positive definite, contact-free, x < 10,
           opposite sides), flowed out, other; displacement from the point-goal snapshot; mu1 against the
           point-goal mu1; asymmetry of J (gradient check).
  quench   per arm (line, point): unperturbed runs held for 120 s (no exit; stationary stop or censored);
           line-goal replays (1e-9 m) held; Wilson 95% intervals on the held fractions.
  gen      completion, deadlock, pair standoff (experiments/E7b/e7b_lib.qualifies), pair-or-group standoff
           (deadlock whose blocker, the residual agent nearest (10, 5), has negative stuck-alone margin), with
           the point-goal runs of the same seeds; exact McNemar p on each seed-paired indicator; fractions of the
           320 runs with Wilson 95% intervals; lone = deadlock not collective; share of deadlocks that are pair
           standoffs; overhang of the generated pairs (min over members of |y - 5| - w/2).
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402
import numpy as np  # noqa: E402
from revlib import sig  # noqa: E402

D = os.path.join(revlib.DATA, "revision", "B6")
DOOR = np.array([10.0, 5.0])
W_HALF = 0.4


def jl(p):
    return revlib.load_runs(p) if os.path.exists(p) else []


def summ(v, n=2):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {"median": sig(float(np.median(v)), n), "min": sig(float(min(v)), n), "max": sig(float(max(v)), n),
            "n": len(v), "raw_median": float(np.median(v)), "raw_min": float(min(v)), "raw_max": float(max(v))}


def classify(r):
    import e7b_lib
    pair = e7b_lib.qualifies(r)["qualifies"]
    coll = False
    if r.get("deadlock") and r.get("residual"):
        bl = min(r["residual"], key=lambda x: float(np.linalg.norm(np.array(x["pos"]) - DOOR)))
        coll = r["margin"][bl["id"]] < 0
    over = None
    if pair:
        over = float(min(abs(x["pos"][1] - 5.0) for x in r["residual"]) - W_HALF)
    dead = bool(r.get("deadlock"))
    return {"complete": bool(r["complete"]), "deadlock": dead, "capped": bool(r.get("capped")),
            "pair": bool(pair), "collective": bool(coll), "lone": dead and not coll, "overhang": over}


def gen_summary(G):
    base = {r["seed"]: r for r in revlib.load_runs(os.path.join(revlib.DATA, "E7b", "e7b_lib.jsonl"))}
    rows = []
    for r in G:
        if r["seed"] in base:
            rows.append((classify(r), classify(base[r["seed"]])))
    n = len(rows)
    out = {"n": n}
    for k in ("complete", "deadlock", "capped", "pair", "collective", "lone"):
        a = sum(x[k] for x, _ in rows)
        b = sum(y[k] for _, y in rows)
        bb = sum(x[k] and not y[k] for x, y in rows)
        cc = sum(y[k] and not x[k] for x, y in rows)
        p = revlib.mcnemar_exact(bb, cc)
        out[k] = {"cell": int(a), "reference": int(b), "only_cell": int(bb), "only_reference": int(cc),
                  "mcnemar_p": p, "mcnemar_p_disp": revlib.pdisp(p)}
        for side, m in (("cell", a), ("reference", b)):
            f, lo, hi = revlib.wilson(m, n)
            out[k][side + "_frac"], out[k][side + "_ci95"] = float(f), [float(lo), float(hi)]
    # share of deadlocks that are pair standoffs, and the geometry of the generated pairs
    # (overhang = min over the two members of |y - 5| - w/2, as B5_analyze.py)
    for side, j in (("cell", 0), ("reference", 1)):
        nd = sum(r[j]["deadlock"] for r in rows)
        npair = sum(r[j]["pair"] for r in rows)
        f, lo, hi = revlib.wilson(npair, nd) if nd else (None, None, None)
        out["pair_of_deadlocks_" + side] = {"n": int(nd), "pair": int(npair), "frac": f, "ci95": [lo, hi]}
        ov = [r[j]["overhang"] for r in rows if r[j]["pair"]]
        s_ov = summ([1e3 * x for x in ov], 2)
        if s_ov:
            s_ov.update({"above_100mm": int(sum(x > 0.1 for x in ov)), "above_20mm": int(sum(x > 0.02 for x in ov))})
        out["pair_overhang_mm_" + side] = s_ov
    out["n_resid_deadlocks"] = dict(Counter(r["n_remaining"] for r in G if r.get("deadlock")))
    return out


def main():
    o = {"script": "experiments/revision/B6_analyze.py", "doc": __doc__}
    S = jl(os.path.join(D, "static.jsonl"))
    if S:
        kept = [r for r in S if r["kept"]]
        freed = [r for r in S if r["relax_freed"]]
        o["static"] = {"n": len(S), "kept": len(kept), "freed": len(freed),
                       "other": len(S) - len(kept) - len(freed),
                       "move_m": summ([r["move_max"] for r in kept]),
                       "mu1": summ([r["eig"][0] for r in kept], 3),
                       "mu1_point": summ([r["point_eig"][0] for r in S], 3),
                       "mu1_ratio_line_over_point": summ([r["eig"][0] / r["point_eig"][0] for r in kept], 3),
                       "asym": summ([r["asym"] for r in kept]),
                       "contact_free": int(sum(r.get("contact_free", False) for r in S)),
                       "front_of_jambs": int(sum(r.get("front_of_jambs", False) for r in kept)),
                       "point_strict_min": int(sum(r["point_strict_min"] for r in S))}
    Q = jl(os.path.join(D, "quench.jsonl"))
    if Q:
        q = {}
        for arm in ("line", "point"):
            u = [r for r in Q if r["arm"] == arm and r["perturb"] is None]
            nh = int(sum(not r["freed"] for r in u))
            q[arm] = {"n": len(u), "held": nh, "held_ci95": list(revlib.wilson(nh, len(u))[1:]),
                      "stationary_stop": int(sum(r["stationary_stop"] for r in u))}
        rp = [r for r in Q if r["arm"] == "line" and r["perturb"] is not None]
        nh = int(sum(not r["freed"] for r in rp))
        q["line_replays"] = {"n": len(rp), "held": nh, "held_ci95": list(revlib.wilson(nh, len(rp))[1:])}
        q["wall_s_total"] = float(sum(r["wall_s"] for r in Q))
        o["quench"] = q
    G = jl(os.path.join(D, "gen_line.jsonl"))
    if G:
        o["gen"] = gen_summary(G)
    revlib.out_json("B6", o)
    return o


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: v for k, v in o.items() if k != "doc"}, indent=1, default=float))
