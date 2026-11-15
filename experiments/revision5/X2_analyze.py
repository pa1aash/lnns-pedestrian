"""X2 analysis: CroMa at dt = 0.005 s and 0.01 s over the full 25-run sets (seeds 42-66) of the four Sect. 7 variants.

Records: seeds 42-51 from C3 (data/revision4/T4/t4_croma.jsonl; trajectories kept on disk in the C3 worktree, not
committed: data/revision4/T4/raw/, looked up under RAW4 when absent here) and seeds 52-66 from X2
(data/revision5/X2/x2_croma.jsonl, trajectories data/revision5/X2/raw/). Estimators unchanged from C3 T4_analyze and
the published CroMa numbers (D3_analyze.load_run -> fix_a7.per_run_stats; D_croma_integrity.d4):
  flow ratio    ratio of the mean run flow to the mean of the five corrected human flows; 95% interval from the delta
                method on the log ratio with Welch-Satterthwaite df (fix_a7.ratio_means "ci95"; the interval the
                paper's Sect. 7 uses, D_croma_integrity.d4 flow_ratio)
  counts        complete / deadlock (stationary detector) / still moving at the 600 s cap
  fluctuation   waiting-zone velocity fluctuation (E10 estimator), Student-t mean over runs (fix_a7.tci)
  overlap       the largest agent-agent overlap h over all runs and steps (and over t >= 1 s), the largest wall
                overlap, and the explicit-friction factor 2 kappa h dt / m at that overlap (kappa = 2.4e5 kg/(m s),
                m the mean mass of the overlapping pair); the explicit tangential-friction update is stable below 2
Checks: each dt = 0.005 s ratio against the dt = 0.01 s interval of the same 25 seeds and the published 25-run
interval (rev_D.json D3.rerun); paired by seed, geometric-mean flow ratio dt 0.005 / 0.01 with a t interval on the
logs and completion discordance (exact McNemar); dt = 0.01 s records reproduce data/revision/D3/d3_croma.jsonl.
Output: data/derived/rev5_X2.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev5lib  # noqa: E402
from rev5lib import DATA, DERIVED, ROOT, mcnemar_exact, np, pdisp, stats  # noqa: E402
import D3_analyze as D3A  # noqa: E402
import D_croma_integrity as DI  # noqa: E402
import fix_a7 as F  # noqa: E402

IN4 = os.path.join(DATA, "revision4", "T4", "t4_croma.jsonl")
IN5 = os.path.join(DATA, "revision5", "X2", "x2_croma.jsonl")
RAW4_CANDIDATES = [os.path.join(DATA, "revision4", "T4", "raw"),
                   os.path.join(os.path.dirname(ROOT), "C3", "data", "revision4", "T4", "raw")]
RAW5 = os.path.join(DATA, "revision5", "X2", "raw")
KAPPA = 240000.0
CELLS = ["C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]
NAMES = {"C1_cf": "SFM", "C1_cf_edge": "jamb range (B_w,edge)", "C3_rvo2_cf": "force-coupled ORCA (RVO2)",
         "C1_cf_sig": "noise sigma*"}


def raw4():
    for p in RAW4_CANDIDATES:
        if os.path.isdir(p) and os.listdir(p):
            return p
    raise FileNotFoundError("C3 T4 trajectories not found: %s" % RAW4_CANDIDATES)


def summarise(Rd, raw_of, hflow, hb):
    M = {c: [D3A.load_run(r, raw_of(r)) for r in Rd if r["cell"] == c] for c in CELLS}
    d4 = DI.d4(M, hflow, hb)
    per = {}
    for c in CELLS:
        rows = [r for r in Rd if r["cell"] == c]
        mx = max(rows, key=lambda r: r["max_agent_overlap_m"])
        ml = max(r["max_agent_overlap_late_m"] for r in rows)
        dt = rows[0]["dt"]
        m = float(np.mean(mx["max_agent"]["masses"]))
        per[c] = {"n": d4[c]["n"], "complete": d4[c]["complete"], "deadlock": d4[c]["deadlock"],
                  "capped": d4[c]["capped"], "flow": d4[c]["flow"], "flow_ratio": d4[c]["flow_ratio"],
                  "fluct": F.tci([D3A.fl(u["est"]) for u in M[c]]),
                  "max_overlap_m": mx["max_agent_overlap_m"], "max_overlap_job": mx["job_id"],
                  "max_overlap_at": mx["max_agent"], "max_overlap_late_m": ml,
                  "max_wall_overlap_m": max(r["max_wall_overlap_m"] for r in rows),
                  "steps_gt5cm": int(sum(r["steps_ov_gt5cm"] for r in rows)),
                  "friction_factor": 2 * KAPPA * mx["max_agent_overlap_m"] * dt / m,
                  "friction_factor_late": 2 * KAPPA * ml * dt / m,
                  "runs_friction_factor_ge2": int(sum(2 * KAPPA * r["max_agent_overlap_m"] * dt /
                                                      float(np.mean(r["max_agent"]["masses"])) >= 2 for r in rows)),
                  "cpu_h": sum(r["cpu_s"] for r in rows) / 3600, "dt": dt,
                  "seeds": sorted(r["seed"] for r in rows),
                  "per_seed_flow": {u["seed"]: u["flow"] for u in M[c]},
                  "per_seed_complete": {u["seed"]: u["complete"] for u in M[c]}}
    return per


def main():
    rev = json.load(open(os.path.join(DERIVED, "rev_D.json")))
    H = rev["humans_corrected"]["runs"]
    hflow = [h["flow_per_s"] for h in H]
    hb = {h["run"]: h["flow_per_s"] for h in H}
    R4 = [json.loads(l) for l in open(IN4) if l.strip()]
    R5 = [json.loads(l) for l in open(IN5) if l.strip()] if os.path.exists(IN5) else []
    for r in R4:
        r["_src"] = "T4"
    for r in R5:
        r["_src"] = "X2"
    R = R4 + R5
    r4dir = raw4()
    raw_of = lambda r: r4dir if r["_src"] == "T4" else RAW5  # noqa: E731
    D3 = {json.loads(l)["job_id"]: json.loads(l) for l in open(os.path.join(DATA, "revision", "D3", "d3_croma.jsonl"))}
    out = {"script": "experiments/revision5/X2_analyze.py", "doc": __doc__, "n_records": len(R),
           "n_records_T4": len(R4), "n_records_X2": len(R5), "raw_T4": os.path.relpath(r4dir, os.path.dirname(ROOT)),
           "interval_method": "delta method on log(mean model flow / mean human flow), Welch-Satterthwaite df "
                              "(fix_a7.ratio_means ci95), as Sect. 7 (D_croma_integrity.d4)",
           "per_dt": {}, "runs_per_variant": {}, "reproduction_dt0p01": {}, "comparison": {}}
    per = {}
    for dk in ("dt0.005", "dt0.01"):
        Rd = [r for r in R if r["dtkey"] == dk]
        out["runs_per_variant"][dk] = {c: sum(r["cell"] == c for r in Rd) for c in CELLS}
        if not all(sum(r["cell"] == c for r in Rd) >= 2 for c in CELLS):
            continue
        per[dk] = summarise(Rd, raw_of, hflow, hb)
        out["per_dt"][dk.replace(".", "p")] = per[dk]
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
                "ratio_dt0p005": ra, "ci95_dt0p005": a["flow_ratio"]["ci95"],
                "ratio_dt0p01": b["flow_ratio"]["ratio"], "ci95_dt0p01": cb,
                "inside_dt0p01": bool(cb[0] <= ra <= cb[1]),
                "ratio_published_25": pub[c]["flow_ratio"]["ratio"], "ci95_published_25": cp,
                "inside_published_25": bool(cp[0] <= ra <= cp[1]),
                "dt0p01_equals_published": bool(abs(b["flow_ratio"]["ratio"] - pub[c]["flow_ratio"]["ratio"]) < 1e-9),
                "n_paired": len(seeds),
                "paired_flow_ratio_geo": float(math.exp(lr.mean())),
                "paired_flow_ratio_ci95": [float(math.exp(lr.mean() - h)), float(math.exp(lr.mean() + h))],
                "completion_disc": [int(x1), int(x2)], "completion_mcnemar_p": mcnemar_exact(x1, x2),
                "completion_mcnemar_p_disp": pdisp(mcnemar_exact(x1, x2))}
    print(rev5lib.out_json("X2", out))
    for dk, d in out["per_dt"].items():
        for c, v in d.items():
            print(dk, c, v["n"], v["complete"], v["deadlock"], v["capped"],
                  "ratio %.3f [%.3f, %.3f]" % (v["flow_ratio"]["ratio"], *v["flow_ratio"]["ci95"]),
                  "fluct %.4f [%.4f, %.4f]" % (v["fluct"]["mean"], *v["fluct"]["ci95"]),
                  "ov %.4f late %.4f wall %.4f" % (v["max_overlap_m"], v["max_overlap_late_m"], v["max_wall_overlap_m"]),
                  "ff %.3f (runs>=2: %d)" % (v["friction_factor"], v["runs_friction_factor_ge2"]), "cpu %.2f" % v["cpu_h"])
    print(out["runs_per_variant"], out["reproduction_dt0p01"])
    for c, v in out["comparison"].items():
        print(c, {k: v[k] for k in v})


if __name__ == "__main__":
    main()
