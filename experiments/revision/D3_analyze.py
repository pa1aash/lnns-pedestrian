"""D3 analysis: the CroMa rerun (experiments/revision/D3_croma_rerun.py: agent number = participants who passed,
bottleneck length 0.2 m) evaluated exactly as D4 evaluates E10, plus the paired change from E10 per variant.

Inputs (read only):
  data/revision/D3/d3_croma.jsonl   rerun records (E10 run(): cell, run, N, L, seed, t_end, complete, deadlock, npz,
                                    estimator); trajectories data/revision/D3/raw/*.npz
  data/E10/e10_croma.jsonl + E10 raw trajectories (fix_a7.raw_dir())   the original runs, paired by (cell, seed)
  data/derived/rev_D.json           corrected human runs (humans_corrected; participant rule, D2)
Per variant (C1_cf, C1_cf_edge, C3_rvo2_cf, C1_cf_sig), with D_croma_integrity.d4 unchanged: complete / deadlock /
capped counts; per-run flow (n - 1)/(last - first passage) and its Student-t mean; flow ratio model/human with the
log-ratio Welch-t interval (fix_a7.ratio_means) and the matched ratio, against the corrected human flows; longest
interior gap of completed runs; the final open gap of every incomplete run right-censored at 600 s, Kaplan-Meier
median and restricted mean, median of c. Also gaps > 2 s per run and the waiting-zone fluctuation (E10 estimator,
RMS of sd_x, sd_y), Student-t over runs.
Paired change from E10 (same cell and seed, hence the same human run type and start sampling seed): mean difference
of flow, of gaps > 2 s and of fluctuation with paired t 95% intervals; geometric mean of the per-seed flow ratio
rerun/E10 with a t interval on the logs; completion 2x2 table with the exact McNemar p.
Output: key "D3"."rerun" of data/derived/rev_D.json (or --out PATH for a test). Registry: notes/D3.yaml.
Usage: D3_analyze.py [--in JSONL] [--out JSON]
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

import fix_a7 as F  # noqa: E402

IN = os.path.join(revlib.DATA, "revision", "D3", "d3_croma.jsonl")
REV_D = os.path.join(revlib.DERIVED, "rev_D.json")
CELLS = ["C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]


def fl(est):
    f = (est or {}).get("fluct")
    return None if not f else math.sqrt((f["sd_x"] ** 2 + f["sd_y"] ** 2) / 2)


def load_run(r, raw):
    p = os.path.join(revlib.ROOT, r["npz"])
    if not os.path.exists(p):
        p = os.path.join(raw, os.path.basename(r["npz"]))
    D = np.load(p)["data"]
    tp = F.first_crossings(D[:, 1].astype(int), D[:, 0], D[:, 2], 10.0)
    u = {"run": r["run"], "N": r["N"], "t_end": float(r["t_end"]), "tp": tp, "complete": bool(r["complete"]),
         "deadlock": bool(r["deadlock"]), "est": r["estimator"], "seed": r["seed"]}
    return F.per_run_stats(u) if len(tp) >= 2 else None


def paired(a, b):
    d = np.asarray(b, float) - np.asarray(a, float)
    n = len(d)
    if n < 2:
        return {"n": n, "mean_diff": float(d.mean()) if n else None}
    h = float(stats.t.ppf(0.975, n - 1) * d.std(ddof=1) / math.sqrt(n))
    return {"n": n, "mean_diff": float(d.mean()), "ci95": [float(d.mean() - h), float(d.mean() + h)]}


def analyze(path=IN):
    import D_croma_integrity as DI
    rev = json.load(open(REV_D))
    H = rev["humans_corrected"]["runs"]
    hflow = [h["flow_per_s"] for h in H]
    hb = {h["run"]: h["flow_per_s"] for h in H}
    raw = os.path.join(os.path.dirname(path), "raw")
    R3 = [json.loads(l) for l in open(path) if l.strip()]
    R0 = [json.loads(l) for l in open(F.IN) if l.strip()]
    rd0 = F.raw_dir()
    M3 = {c: [u for u in (load_run(r, raw) for r in R3 if r["cell"] == c) if u] for c in CELLS}
    present = [c for c in CELLS if len(M3[c]) >= 2]
    o = {"input": os.path.relpath(path, revlib.ROOT) if path.startswith(revlib.ROOT) else path,
         "n_records": len(R3), "N_L_used": sorted({(r["run"], r["N"], r["L"]) for r in R3}),
         "cells_analysed": present, "per_variant": {}, "paired_vs_E10": {}}
    d4 = DI.d4({c: M3[c] for c in present}, hflow, hb) if present else {}
    for c in present:
        X = M3[c]
        d = d4[c]
        d["gaps_gt_2s"] = F.tci([u["n_gt2"] for u in X])
        d["fluct"] = F.tci([fl(u["est"]) for u in X])
        d["n_leaked_runs"] = sum(r.get("n_leaked", 0) > 0 for r in R3 if r["cell"] == c)
        # E10 / fix_a7 estimators: Wilson interval of completion, 10-90% window flow over the observed passages,
        # longest gap of every run (up to the stop), flow by bottleneck length (2.0 m: 4D030, 4D040; 0.2 m: the rest)
        d["complete_wilson"] = F.wilson(sum(u["complete"] for u in X), len(X))
        d["window_flow"] = F.tci([u["flow_w_obs"] for u in X])
        d["longest_gap_all"] = F.tci([u["max_gap"] for u in X])
        lng = [u["flow"] for u in X if u["run"] in ("4D030", "4D040")]
        sht = [u["flow"] for u in X if u["run"] not in ("4D030", "4D040")]
        d["flow_long"] = float(np.mean(lng)) if lng else None
        d["flow_short"] = float(np.mean(sht)) if sht else None
        o["per_variant"][c] = d
        # paired change from E10
        e0 = {r["seed"]: r for r in R0 if r["cell"] == c}
        u0 = {}
        for u in X:
            if u["seed"] in e0:
                v = F.model_run(e0[u["seed"]], rd0)
                u0[u["seed"]] = F.per_run_stats(v)
        seeds = sorted(u0)
        new = {u["seed"]: u for u in X}
        b = sum(u0[s]["complete"] and not new[s]["complete"] for s in seeds)
        cc = sum((not u0[s]["complete"]) and new[s]["complete"] for s in seeds)
        lr = np.log([new[s]["flow"] / u0[s]["flow"] for s in seeds])
        g = None
        if len(lr) >= 2:
            h = stats.t.ppf(0.975, len(lr) - 1) * lr.std(ddof=1) / math.sqrt(len(lr))
            g = {"geo_ratio": float(math.exp(lr.mean())), "ci95": [float(math.exp(lr.mean() - h)),
                                                                   float(math.exp(lr.mean() + h))]}
        o["paired_vs_E10"][c] = {
            "n_pairs": len(seeds), "seeds": seeds,
            "flow": paired([u0[s]["flow"] for s in seeds], [new[s]["flow"] for s in seeds]),
            "flow_ratio_rerun_over_E10": g,
            "gaps_gt_2s": paired([u0[s]["n_gt2"] for s in seeds], [new[s]["n_gt2"] for s in seeds]),
            "fluct": paired([fl(u0[s]["est"]) for s in seeds], [fl(new[s]["est"]) for s in seeds]),
            "complete_E10": sum(u0[s]["complete"] for s in seeds), "complete_rerun": sum(new[s]["complete"] for s in seeds),
            "completion_discordant": {"E10_only": int(b), "rerun_only": int(cc)},
            "mcnemar_p": revlib.mcnemar_exact(b, cc), "mcnemar_p_disp": revlib.pdisp(revlib.mcnemar_exact(b, cc)),
            "flow_ratio_to_human_E10_corrected": rev["D4"][c]["flow_ratio"]}
    if d4:
        rs = {c: d4[c]["flow_ratio"]["ratio"] for c in present}
        o["range"] = {"min": min(rs.values()), "max": max(rs.values()), "min_cell": min(rs, key=rs.get),
                      "max_cell": max(rs, key=rs.get)}
    o["complete_set"] = len(R3) == 100 and all(len(M3[c]) == 25 for c in CELLS)
    return o


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=IN)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    o = analyze(a.inp)
    if a.out:
        json.dump({"D3": {"rerun": o}}, open(a.out, "w"), indent=1, default=float)
        print(a.out)
    else:
        rev = json.load(open(REV_D))
        rev.setdefault("D3", {})["rerun"] = o
        print(revlib.out_json("D", rev))
    for c, d in o["per_variant"].items():
        p = o["paired_vs_E10"][c]
        print(c, "n", d["n"], "k/dl/cap", d["complete"], d["deadlock"], d["capped"], "ratio",
              revlib.sig(d["flow_ratio"]["ratio"]), [revlib.sig(v) for v in d["flow_ratio"]["ci95"]],
              "KM med", d["km_median"], "cens", d["n_censored"], "paired dflow", p["flow"], "McNemar", p["mcnemar_p_disp"])


if __name__ == "__main__":
    main()
