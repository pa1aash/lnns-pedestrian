"""E7 analysis: wall-model validity cells (CF, C1, seeds 42-141, 600 s cap).

  python experiments/E7/analyze.py keystone [--workers 2]   K1/K2/K1b surgery on the E7 deadlock snapshots (resumable)
  python experiments/E7/analyze.py summary                   write data/derived/E7_analysis.json

Inputs: data/E7/e7_cells.jsonl and data/E7/library (override the directory with E7_SRC=<dir containing e7_cells.jsonl and
library/>), data/E1/E1_runs.jsonl (E1b, seeds 42-141 = the w = 0.8 m default cell) and data/derived/E1_keystone.json
(its keystone classes). Keystone surgery restarts each snapshot with the cell's own wall flags and the snapshot's width.

Classes (experiments/E1/keystone.py): lone_keystone (blocker alone held, everyone else exits once it is removed),
lone_keystone_second_trap (blocker alone held, but others stay behind when it is removed), collective (blocker alone is
freed: a pair or group standoff).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "E1"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import keystone as K  # noqa: E402  (imports e1lib: chdir to code/)
from e1lib import CF, DATA, DERIVED, load_runs, run_jobs, wilson  # noqa: E402
import numpy as np  # noqa: E402

SRC = os.environ.get("E7_SRC", os.path.join(DATA, "E7"))
RUNS = os.path.join(SRC, "e7_cells.jsonl")
LIBD = os.path.join(SRC, "library")
KOUT = os.path.join(os.environ.get("E7_KOUT", os.path.join(DATA, "E7")), "keystone.jsonl")
sys.path.insert(0, os.path.join(HERE))
import e7_cells as E  # noqa: E402  (cell definitions: width and flags)

ORDER = ["w0.7", "default", "w0.9", "w1.0", "B0.04", "B0.02", "Bedge0.04", "rounded", "line", "line_rounded"]
WIDTH = {"w0.7": 0.7, "default": 0.8, "w0.9": 0.9, "w1.0": 1.0}
SEEDS = range(42, 142)
for c, (w, fl) in E.CELLS.items():          # keystone.run looks the restart flags up by job["mode"]
    K.MODE_FLAGS[c] = {**CF, **fl}


def runs():
    R = [r for r in load_runs(RUNS)]
    base = [dict(r, cell="default") for r in load_runs(K.runs_path()) if r["mode"] == "E1b" and r["seed"] in SEEDS]
    return R + base


def snaps():
    return sorted([r for r in load_runs(RUNS) if r.get("snapshot")], key=lambda r: (r["cell"], r["seed"]))


def kjobs(phase2=None):
    out = []
    if phase2 is None:
        for r in snaps():
            for t in ("K1", "K2"):
                out.append({"job_id": f"{r['cell']}_seed{r['seed']}|{t}", "mode": r["cell"], "seed": r["seed"],
                            "snap": os.path.join(LIBD, os.path.basename(r["snapshot"])), "test": t})
        return out
    res = phase2
    for r in snaps():
        tag = f"{r['cell']}_seed{r['seed']}"
        k1, k2 = res.get(tag + "|K1"), res.get(tag + "|K2")
        if k1 and k2 and k1["held"] and k2["held"]:
            pos = {int(x["id"]): np.array(x["pos"]) for x in r["residual"]}
            tgt = min(k2["held"], key=lambda i: float(np.linalg.norm(pos[i] - K.DOOR)))
            out.append({"job_id": tag + "|K1b", "mode": r["cell"], "seed": r["seed"],
                        "snap": os.path.join(LIBD, os.path.basename(r["snapshot"])), "test": "K1b", "target": int(tgt)})
    return out


def run_keystone(workers):
    workers = min(workers, 2)
    os.makedirs(os.path.dirname(KOUT), exist_ok=True)
    run_jobs(kjobs(), K.run, KOUT, workers=workers, log_every=50)
    res = {x["job_id"]: x for x in load_runs(KOUT)}
    run_jobs(kjobs(res), K.run, KOUT, workers=workers, log_every=50)


def cls_of(k1, k2):
    if not k1["held"]:
        return "collective"
    return "lone_keystone" if not k2["held"] else "lone_keystone_second_trap"


def classes():
    """cell -> {seed: class, K1b held?} for the E7 cells (own surgery) and the default cell (E1 keystone file)."""
    out = {}
    if os.path.exists(KOUT):
        res = {x["job_id"]: x for x in load_runs(KOUT)}
        for r in snaps():
            tag = f"{r['cell']}_seed{r['seed']}"
            k1, k2, k1b = res.get(tag + "|K1"), res.get(tag + "|K2"), res.get(tag + "|K1b")
            if k1 and k2:
                out.setdefault(r["cell"], {})[r["seed"]] = {
                    "class": cls_of(k1, k2), "n_resid": len(k1["residual"]),
                    "K1b_held": None if not k1b else bool(k1b["held"])}
    ks = json.load(open(os.path.join(DERIVED, "E1_keystone.json")))["modes"]["E1b"]["per_snapshot"]
    out["default"] = {x["seed"]: {"class": x["class"], "n_resid": x["n_resid"],
                                  "K1b_held": None if not x["K1b"] else bool(x["K1b"]["held"])}
                      for x in ks if x["seed"] in SEEDS}
    return out


def fisher(a, b, c, d):
    """Two-sided Fisher exact p for [[a, b], [c, d]] (hypergeometric, no scipy dependency)."""
    from math import comb
    n1, n2, k = a + b, c + d, a + c
    tot = comb(n1 + n2, k)
    pr = lambda x: comb(n1, x) * comb(n2, k - x) / tot
    p0 = pr(a)
    return float(sum(pr(x) for x in range(max(0, k - n2), min(n1, k) + 1) if pr(x) <= p0 * (1 + 1e-9)))


def logit_fit(w, k, n):
    """Binomial-logit fit of completion against w (Newton); returns (a, b) with p = 1/(1+exp(-(a + b w)))."""
    w, k, n = map(np.asarray, (w, k, n))
    th = np.array([0.0, 0.0])
    X = np.column_stack([np.ones_like(w), w])
    for _ in range(100):
        p = 1 / (1 + np.exp(-X @ th))
        g = X.T @ (k - n * p)
        H = (X * (n * p * (1 - p))[:, None]).T @ X + 1e-9 * np.eye(2)
        step = np.linalg.solve(H, g)
        th = th + step
        if np.abs(step).max() < 1e-10:
            break
    return th


def critical_width(cells):
    """w50 from the default-wall completions: logit fit (bootstrap CI) and the linear interpolation of the 50% crossing."""
    ws = np.array([0.7, 0.8, 0.9, 1.0])
    k = np.array([cells[c]["k_complete"] for c in ("w0.7", "default", "w0.9", "w1.0")])
    n = np.array([cells[c]["n"] for c in ("w0.7", "default", "w0.9", "w1.0")])
    # 0.5 crossing by linear interpolation between neighbouring widths
    p = k / n
    lin = None
    for i in range(3):
        if p[i] < 0.5 <= p[i + 1]:
            lin = float(ws[i] + (0.5 - p[i]) / (p[i + 1] - p[i]) * (ws[i + 1] - ws[i]))
    # logit fit on pseudo-counts (+0.5) so that the exact 0/100 and 100/100 cells do not make the fit diverge
    kk, nn = k + 0.5, n + 1.0
    a, b = logit_fit(ws, kk, nn)
    w50 = float(-a / b)
    rng = np.random.default_rng(7)
    bs = []
    for _ in range(2000):
        kb = rng.binomial(n, p)
        a_, b_ = logit_fit(ws, kb + 0.5, n + 1.0)
        bs.append(-a_ / b_ if b_ > 0 else np.nan)
    bs = np.array(bs)
    return {"widths_m": ws.tolist(), "completion": p.tolist(), "w50_logit": w50,
            "w50_logit_ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
            "w50_linear": lin, "logit_slope_per_m": float(b), "pseudo_count": 0.5}


def summary():
    R = runs()
    cl = classes()
    cells = {}
    for c in ORDER:
        Rc = [r for r in R if r["cell"] == c]
        n = len(Rc)
        kc = sum(bool(r["complete"]) for r in Rc)
        kd = sum(bool(r["deadlock"]) for r in Rc)
        kcap = sum(bool(r.get("capped")) for r in Rc if "capped" in r) if c != "default" else 0
        p, lo, hi = wilson(kc, n) if n else (float("nan"),) * 3
        td = np.array([r["t_end"] for r in Rc if r["deadlock"]])
        row = {"n": n, "k_complete": kc, "k_deadlock": kd, "k_capped": kcap,
               "completion": p, "wilson95": [lo, hi],
               "deadlock_time_s": None if not len(td) else {
                   "median": float(np.median(td)), "q25": float(np.percentile(td, 25)),
                   "q75": float(np.percentile(td, 75)), "min": float(td.min()), "max": float(td.max())},
               "mean_remaining_at_deadlock": None if not kd else float(np.mean([r["n_remaining"] for r in Rc if r["deadlock"]])),
               "width_m": WIDTH.get(c, 0.8)}
        cc = cl.get(c, {})
        cnt = {k: sum(v["class"] == k for v in cc.values())
               for k in ("lone_keystone", "lone_keystone_second_trap", "collective")}
        row["classes"] = {"n_classified": len(cc), "counts": cnt,
                          "frac_collective": (cnt["collective"] / len(cc)) if cc else None,
                          "frac_collective_wilson95": list(wilson(cnt["collective"], len(cc))[1:]) if cc else None,
                          "n_resid_hist": {str(m): sum(v["n_resid"] == m for v in cc.values())
                                           for m in sorted({v["n_resid"] for v in cc.values()})},
                          "second_trap_K1b_held": sum(v["K1b_held"] is True for v in cc.values()),
                          "second_trap_K1b_freed": sum(v["K1b_held"] is False for v in cc.values())}
        cells[c] = row
    out = {"script": "experiments/E7/analyze.py", "doc": __doc__, "cells": cells}
    ok = all(cells[c]["n"] == 100 for c in ORDER)
    if ok:
        out["critical_width"] = critical_width(cells)
        d, e = cells["B0.04"], cells["Bedge0.04"]
        out["locality"] = {
            "all_walls_B0.04_vs_jamb_only": {
                "k_complete": [d["k_complete"], e["k_complete"]],
                "fisher_p": fisher(d["k_complete"], 100 - d["k_complete"], e["k_complete"], 100 - e["k_complete"])},
            "jamb_only_vs_default": {"k_complete": [e["k_complete"], cells["default"]["k_complete"]],
                                     "fisher_p": fisher(e["k_complete"], 100 - e["k_complete"],
                                                        cells["default"]["k_complete"], 100 - cells["default"]["k_complete"])},
            "B0.02_vs_B0.04": {"k_complete": [cells["B0.02"]["k_complete"], d["k_complete"]],
                               "fisher_p": fisher(cells["B0.02"]["k_complete"], 100 - cells["B0.02"]["k_complete"],
                                                  d["k_complete"], 100 - d["k_complete"])}}
        for c in ("B0.04", "B0.02", "Bedge0.04", "rounded", "line", "line_rounded"):
            r = cells[c]
            out["locality"][f"{c}_vs_default"] = {
                "k_complete": [r["k_complete"], cells["default"]["k_complete"]],
                "fisher_p": fisher(r["k_complete"], 100 - r["k_complete"], cells["default"]["k_complete"],
                                   100 - cells["default"]["k_complete"])}
        # class composition shift: collective share in the jamb-only and all-walls B_w = 0.04 cells against default
        cd, ce = cells["default"]["classes"], cells["Bedge0.04"]["classes"]
        if cd["n_classified"] and ce["n_classified"]:
            out["locality"]["collective_default_vs_jamb_only"] = {
                "k_collective": [cd["counts"]["collective"], ce["counts"]["collective"]],
                "n_classified": [cd["n_classified"], ce["n_classified"]],
                "fisher_p": fisher(cd["counts"]["collective"], cd["n_classified"] - cd["counts"]["collective"],
                                   ce["counts"]["collective"], ce["n_classified"] - ce["counts"]["collective"])}
    def undot(o):      # registry key paths split on '.', so cell names such as B0.04 are stored as B0p04
        if isinstance(o, dict):
            return {(k.replace(".", "p") if isinstance(k, str) else k): undot(v) for k, v in o.items()}
        return o
    json.dump(undot(out), open(os.path.join(DERIVED, "E7_analysis.json"), "w"), indent=1, default=float)
    if ok:        # figure cache (figures/fig3_width_walls.py reads only this file)
        def pt(c):
            r = cells[c]
            cc = r["classes"]["counts"]
            return {"cell": c, "k": r["k_complete"], "n": r["n"], "p": r["completion"], "lo": r["wilson95"][0],
                    "hi": r["wilson95"][1], "lone": cc["lone_keystone"] + cc["lone_keystone_second_trap"],
                    "collective": cc["collective"], "unclassified": r["k_deadlock"] - r["classes"]["n_classified"]}
        fig = {"width": [dict(pt(c), w=WIDTH[c]) for c in ("w0.7", "default", "w0.9", "w1.0")],
               "variants": [pt(c) for c in ("default", "B0.04", "B0.02", "Bedge0.04", "rounded", "line", "line_rounded")],
               "w50": out["critical_width"]["w50_logit"], "source": "data/derived/E7_analysis.json"}
        json.dump(fig, open(os.path.join(os.path.dirname(HERE), "..", "figures", "data", "fig3.json"), "w"), indent=1)
    for c in ORDER:
        r = cells[c]
        print(f"{c:13s} n={r['n']:3d} complete={r['k_complete']:3d} deadlock={r['k_deadlock']:3d} "
              f"p={r['completion']:.2f} CI=[{r['wilson95'][0]:.2f},{r['wilson95'][1]:.2f}] classes={r['classes']['counts']}")
    if "critical_width" in out:
        print(json.dumps(out["critical_width"]), json.dumps(out["locality"], default=float)[:600])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["keystone", "summary"])
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    run_keystone(a.workers) if a.cmd == "keystone" else summary()
