"""T4 analysis: CroMa time-step check (experiments/revision4/T4_croma_dt.py; 10 runs per variant, seeds 42-51).

Per variant (C1_cf, C1_cf_edge, C3_rvo2_cf, C1_cf_sig) and time step (0.005, 0.01 s), with the estimators of the
published CroMa numbers unchanged (D3_analyze.load_run -> fix_a7.per_run_stats; D_croma_integrity.d4): complete /
deadlock / still-moving (capped) counts; flow ratio model/human (ratio of mean run flow to the mean of the five
corrected human flows, delta-method log-ratio interval with Welch df, fix_a7.ratio_means); waiting-zone velocity
fluctuation (E10 estimator, RMS of sd_x and sd_y; Student-t mean over runs); the largest agent-agent overlap h over all
runs and steps (also for t >= 1 s), and the explicit-friction factor 2 kappa h dt / m (kappa = 2.4e5 kg/(m s), m of the
overlapping pair, 80 kg) at that overlap, which must be below 2 for the explicit tangential-friction update to be
stable. Check: whether each ratio at dt = 0.005 s lies inside the 95% interval at dt = 0.01 s on the same 10 seeds
and inside the published 25-run interval (rev_D.json D3.rerun). Paired by seed: geometric mean of the flow ratio
dt 0.005 / 0.01 with a t interval on the logs, completion discordance with exact McNemar. Reproduction: the dt = 0.01
records must equal data/revision/D3/d3_croma.jsonl (t_end, completion, passages and flow).
Output: data/derived/rev4_T4.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import DATA, DERIVED, ROOT, mcnemar_exact, np, pdisp, stats  # noqa: E402
import D3_analyze as D3A  # noqa: E402
import D_croma_integrity as DI  # noqa: E402
import fix_a7 as F  # noqa: E402

IN = os.path.join(DATA, "revision4", "T4", "t4_croma.jsonl")
RAW = os.path.join(DATA, "revision4", "T4", "raw")
KAPPA = 240000.0
CELLS = ["C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]


def main():
    rev = json.load(open(os.path.join(DERIVED, "rev_D.json")))
    H = rev["humans_corrected"]["runs"]
    hflow = [h["flow_per_s"] for h in H]
    hb = {h["run"]: h["flow_per_s"] for h in H}
    R = [json.loads(l) for l in open(IN) if l.strip()]
    D3 = {json.loads(l)["job_id"]: json.loads(l) for l in open(os.path.join(DATA, "revision", "D3", "d3_croma.jsonl"))}
    out = {"script": "experiments/revision4/T4_analyze.py", "doc": __doc__, "n_records": len(R), "per_dt": {},
           "reproduction_dt0p01": {}, "comparison": {}}
    per = {}
    for dk in ("dt0.005", "dt0.01"):
        Rd = [r for r in R if r["dtkey"] == dk]
        M = {c: [D3A.load_run(r, RAW) for r in Rd if r["cell"] == c] for c in CELLS}
        if not all(len(M[c]) >= 2 for c in CELLS):
            continue
        d4 = DI.d4(M, hflow, hb)
        per[dk] = {}
        for c in CELLS:
            rows = [r for r in Rd if r["cell"] == c]
            mx = max(rows, key=lambda r: r["max_agent_overlap_m"])
            ml = max(r["max_agent_overlap_late_m"] for r in rows)
            dt = rows[0]["dt"]
            m = float(np.mean(mx["max_agent"]["masses"]))
            per[dk][c] = {"n": d4[c]["n"], "complete": d4[c]["complete"], "deadlock": d4[c]["deadlock"],
                          "capped": d4[c]["capped"], "flow": d4[c]["flow"], "flow_ratio": d4[c]["flow_ratio"],
                          "flow_ratio_matched": d4[c]["flow_ratio_matched"],
                          "fluct": F.tci([D3A.fl(u["est"]) for u in M[c]]),
                          "max_overlap_m": mx["max_agent_overlap_m"], "max_overlap_job": mx["job_id"],
                          "max_overlap_at": mx["max_agent"], "max_overlap_late_m": ml,
                          "max_wall_overlap_m": max(r["max_wall_overlap_m"] for r in rows),
                          "steps_gt5cm": int(sum(r["steps_ov_gt5cm"] for r in rows)),
                          "friction_factor": 2 * KAPPA * mx["max_agent_overlap_m"] * dt / m,
                          "friction_factor_late": 2 * KAPPA * ml * dt / m,
                          "cpu_h": sum(r["cpu_s"] for r in rows) / 3600, "dt": dt,
                          "seeds": sorted(r["seed"] for r in rows), "per_seed_flow": {u["seed"]: u["flow"] for u in M[c]},
                          "per_seed_complete": {u["seed"]: u["complete"] for u in M[c]}}
        out["per_dt"][dk.replace(".", "p")] = per[dk]
    # reproduction of D3 at dt = 0.01
    mism = []
    for r in R:
        if r["dtkey"] != "dt0.01":
            continue
        ref = D3[r["job_id"].split("|", 1)[1]]
        if abs(ref["t_end"] - r["t_end"]) > 1e-6 or ref["complete"] != r["complete"] or \
                abs(ref["estimator"].get("flow_per_s", 0) - r["estimator"].get("flow_per_s", 0)) > 1e-9:
            mism.append(r["job_id"])
    out["reproduction_dt0p01"] = {"n": sum(r["dtkey"] == "dt0.01" for r in R), "mismatch": mism}
    pub = rev["D3"]["rerun"]["per_variant"]
    if "dt0.005" in per and "dt0.01" in per:
        for c in CELLS:
            a, b = per["dt0.005"][c], per["dt0.01"][c]
            ra, cb, cp = a["flow_ratio"]["ratio"], b["flow_ratio"]["ci95"], pub[c]["flow_ratio"]["ci95"]
            seeds = sorted(set(a["per_seed_flow"]) & set(b["per_seed_flow"]))
            lr = np.log([a["per_seed_flow"][s] / b["per_seed_flow"][s] for s in seeds])
            h = stats.t.ppf(0.975, len(lr) - 1) * lr.std(ddof=1) / math.sqrt(len(lr))
            x1 = sum(a["per_seed_complete"][s] and not b["per_seed_complete"][s] for s in seeds)
            x2 = sum(b["per_seed_complete"][s] and not a["per_seed_complete"][s] for s in seeds)
            out["comparison"][c] = {
                "ratio_dt0p005": ra, "ci95_dt0p01_same_seeds": cb, "inside_dt0p01_same_seeds": bool(cb[0] <= ra <= cb[1]),
                "ratio_published_25": pub[c]["flow_ratio"]["ratio"], "ci95_published_25": cp,
                "inside_published_25": bool(cp[0] <= ra <= cp[1]),
                "paired_flow_ratio_geo": float(math.exp(lr.mean())),
                "paired_flow_ratio_ci95": [float(math.exp(lr.mean() - h)), float(math.exp(lr.mean() + h))],
                "completion_disc": [int(x1), int(x2)], "completion_mcnemar_p": mcnemar_exact(x1, x2),
                "completion_mcnemar_p_disp": pdisp(mcnemar_exact(x1, x2))}
    print(rev4lib.out_json("T4", out))
    for dk, d in out["per_dt"].items():
        for c, v in d.items():
            print(dk, c, v["complete"], v["deadlock"], v["capped"], "ratio %.3f [%.3f, %.3f]" % (v["flow_ratio"]["ratio"], *v["flow_ratio"]["ci95"]),
                  "fluct %.4f" % v["fluct"]["mean"], "ov %.4f late %.4f" % (v["max_overlap_m"], v["max_overlap_late_m"]),
                  "ff %.3f" % v["friction_factor"], "cpu %.2f" % v["cpu_h"])
    print(out["reproduction_dt0p01"])
    for c, v in out["comparison"].items():
        print(c, {k: v[k] for k in v})


if __name__ == "__main__":
    main()
