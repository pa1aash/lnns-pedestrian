"""A13: small facts asked by the referee, each traced to code or data (notes: experiments/revision/notes/A13.md).

Inputs: data/E1/E1_runs.jsonl (E1b mode, 200 seeds), data/derived/E1_chain.json, data/derived/E1_keystone.json,
data/derived/E1_analysis.json, data/E3/e3_dt.jsonl, data/E4/e4_escape.jsonl, data/derived/T3_variance.json,
data/derived/E3_analysis.json, data/derived/fix_a3.json, data/derived/fix_a4.json, data/E7b/e7b_static.jsonl,
data/derived/E7b_analysis.json, data/arch/arch.jsonl, data/N5/n5.jsonl, data/revision/A13/{creep,arch_peak}.jsonl
(from A13_sims.py), data/E2/e2_quench.jsonl. Wall law from experiments/lib/w2lib.py (Passability, default walls).

 1 gmax       g_max(r) = max over the door axis of the backward wall force on a lone agent at rest (w2lib
              max_backward, w = 0.8 m, A_w = 2000 N, B_w = 0.08 m, sharp edges), at r = 0.20, 0.25, 0.30, 0.35 m;
              both the direct profile and the Passability interpolation.
 2 deciles    stuck-alone fraction (margin_C1 = g_max(r) - m v0/tau > 0) by arrival decile (experiments/E1/chain.py:
              decile = min(floor(10 k / n_arrived), 9) of arrival rank k within the run), E1b.
 3 stack      for the E1b deadlocks of the two stack classes (lone keystone, second trap; keystone.py), the number
              of residual agents at the deadlock that are stuck alone (margin_C1 > 0), and the number of residual
              agents; also chain.py's final run of consecutive stuck-alone arrivals.
 4 drive      mean and median spawned radius over the 20 000 E1b agents; g_max at those radii; median SFM drive
              m v0 / tau (E1_analysis) divided by g_max(mean r).
 5 creep      blocker speed during the creep of the 7 legacy-solver runs (2 unperturbed + 5 flipping replays):
              median |v| and mean axial velocity vx over [0, T), T = blocker exit - 2 s (freed runs) or 120 s
              (held runs); also over the pre-divergence window [0, 10 s].
 6 arch       arch body force = k sum(r_ij - d_ij) over the contacts of the arch component (arch.py arch_check);
              largest single-contact overlap at the peak check (A13_sims.py).
 7 T3 cells   the 207 cells of t3_variance.py stored_moments: E3 (snapshot, noise mode, dt) and E4 (snapshot,
              condition, beta level), ORCA runs excluded, >= 200 trapped velocity samples pooled over restarts.
 8 ell        dt pair of Eq. ell (E3 analyze.py).
 10 lag       the shared-lag MLE of fix_a3.py against the earliest escape time.
 11 asym      recomputed Spearman correlation of |dist_axis(lower) - dist_axis(upper)| with |b_f(+) - b_f(-)|.
Output: data/derived/rev_A13.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import revlib  # noqa: E402
from revlib import DATA, DERIVED, np, sig, stats  # noqa: E402
from w2lib import Passability, max_backward  # noqa: E402

J = lambda p: json.load(open(os.path.join(DERIVED, p)))  # noqa: E731


def jl(p):
    return [json.loads(x) for x in open(os.path.join(DATA, p)) if x.strip()]


def main():
    out = {}
    PASS = Passability(0.8)
    # 1 ---------------------------------------------------------------- g_max
    g = {f"{r:.2f}": {"direct_N": max_backward(r, width=0.8), "interp_N": PASS.gmax(r)} for r in (0.20, 0.25, 0.30, 0.35)}
    out["gmax"] = {"by_r": g, "r030_N": sig(g["0.30"]["direct_N"], 3),
                   "stored_E1_analysis_r030_N": J("E1_analysis.json")["gmax_N"]["0.30"]}

    # 2 ---------------------------------------------------------------- deciles
    ch = J("E1_chain.json")["E1b"]["a_stuck_fraction_by_arrival_decile"]
    fr = ch["frac"]
    out["deciles"] = {"frac": fr, "n": ch["n"], "first8_min": sig(min(fr[:8]), 2), "first8_max": sig(max(fr[:8]), 2),
                      "ninth": sig(fr[8], 2), "tenth": sig(fr[9], 2), "ninth_raw": fr[8],
                      "first8_argmin_decile": int(np.argmin(fr[:8])) + 1}

    # 3 ---------------------------------------------------------------- stack size
    runs = [r for r in revlib.load_runs(os.path.join(DATA, "E1", "E1_runs.jsonl")) if r["mode"] == "E1b"]
    ks = {s["seed"]: s for s in J("E1_keystone.json")["modes"]["E1b"]["per_snapshot"]}
    rows = []
    for r in runs:
        if not r["deadlock"]:
            continue
        mg = {a["id"]: a["margin_C1"] for a in r["attrs"]}
        res = [x["id"] for x in r["residual"]]
        rows.append({"seed": r["seed"], "cls": ks[r["seed"]]["class"], "n_resid": len(res),
                     "n_stuck": sum(mg[i] > 0 for i in res)})
    st = [x for x in rows if x["cls"] != "collective"]
    ns, nr = np.array([x["n_stuck"] for x in st]), np.array([x["n_resid"] for x in st])
    by = {c: [x["n_stuck"] for x in st if x["cls"] == c] for c in ("lone_keystone", "lone_keystone_second_trap")}
    tail = J("E1_chain.json")["E1b"]["a_final_stuck_run_length"]
    out["stack"] = {
        "n_stacks": len(st), "n_deadlocks": len(rows),
        "stuck_resid_median": float(np.median(ns)), "stuck_resid_iqr": np.percentile(ns, [25, 75]).tolist(),
        "stuck_resid_min": int(ns.min()), "stuck_resid_max": int(ns.max()),
        "stuck_resid_hist": {str(k): int((ns == k).sum()) for k in range(int(ns.max()) + 1)},
        "stuck_resid_le3": int((ns <= 3).sum()), "stuck_resid_le3_frac": sig(float((ns <= 3).mean()), 2),
        "all_resid_stuck": int((ns == nr).sum()),
        "resid_median": float(np.median(nr)), "resid_max": int(nr.max()),
        "stuck_resid_median_by_class": {c: float(np.median(v)) for c, v in by.items()},
        "final_arrival_run_median": tail["median"], "final_arrival_run_iqr": [tail["p25"], tail["p75"]]}

    # 4 ---------------------------------------------------------------- drive vs g_max(mean r)
    rad = np.array([a["r"] for r in runs for a in r["attrs"]])
    drv = J("E1_analysis.json")["E1b"]["drives_N"]["C1_free_m_v0_over_tau"]["p50"]
    gm = PASS.gmax(float(rad.mean()))
    out["drive"] = {"n_agents": len(rad), "r_mean_m": float(rad.mean()), "r_median_m": float(np.median(rad)),
                    "r_mean_m_disp": sig(float(rad.mean()), 3), "gmax_at_mean_r_N": gm,
                    "gmax_at_mean_r_disp": sig(gm, 3), "gmax_at_median_r_N": PASS.gmax(float(np.median(rad))),
                    "drive_median_N": drv, "ratio_drive_over_gmax_mean_r": sig(drv / gm, 2),
                    "ratio_raw": drv / gm}

    # 5 ---------------------------------------------------------------- creep
    e2 = {r["job_id"]: r for r in jl("E2/e2_quench.jsonl") if r["arm"] == "C3_pub"}
    cr = []
    for r in jl("revision/A13/creep.jsonl"):
        A = np.array([[np.nan if v is None else v for v in row] for row in r["rows"]], float)
        t, x, vx, vy = A[:, 0], A[:, 1], A[:, 3], A[:, 4]
        sp = np.hypot(vx, vy)
        T = (r["blocker_exit_t"] - 2.0) if r["blocker_exit_t"] is not None else 120.0
        w, w10 = (t < T) & np.isfinite(sp), (t <= 10.0) & np.isfinite(sp)
        ref = e2[f"{r['tag']}|C3_pub|{'u' if r['perturb'] is None else r['perturb']}"]["exits"].get(str(r["blocker"]))
        cr.append({"run": r["job_id"], "blocker_exit_t": r["blocker_exit_t"], "e2_exit_t": ref,
                   "reproduces_e2": (ref is None and r["blocker_exit_t"] is None) or
                   (ref is not None and r["blocker_exit_t"] is not None and abs(ref - r["blocker_exit_t"]) < 1e-6),
                   "window_s": T, "speed_median": float(np.median(sp[w])), "speed_p90": float(np.percentile(sp[w], 90)),
                   "vx_mean": float((x[w][-1] - x[w][0]) / (t[w][-1] - t[w][0])), "x_start": float(x[0]),
                   "x_end_window": float(x[w][-1]), "speed_median_0_10s": float(np.median(sp[w10])),
                   "max_speed_any_median": float(np.median(A[w, 5]))})
    spm = [c["speed_median"] for c in cr]
    vxm = [c["vx_mean"] for c in cr]
    out["creep"] = {"runs": cr, "all_reproduce_e2": all(c["reproduces_e2"] for c in cr),
                    "speed_median_min": sig(min(spm), 2), "speed_median_max": sig(max(spm), 2),
                    "vx_mean_min_mm_s": sig(1e3 * min(vxm), 2), "vx_mean_max_mm_s": sig(1e3 * max(vxm), 2),
                    "speed_median_0_10_min": sig(min(c["speed_median_0_10s"] for c in cr), 2),
                    "speed_median_0_10_max": sig(max(c["speed_median_0_10s"] for c in cr), 2)}

    # 6 ---------------------------------------------------------------- arch
    arch = jl("arch/arch.jsonl")
    n5 = [r for r in jl("N5/n5.jsonl") if r["cell"] == "dt0.0025_v5"]
    pk = {}
    for name, R in (("arch_dt0p01", arch), ("n5_dt0p0025", n5)):
        f, s, e = max(((e["body_force_N"], r["seed"], e) for r in R for e in r["episodes"]), key=lambda z: z[0])
        pk[name] = {"stored_peak_N": f, "seed": s, "episode_t0": e["t0"], "episode_t1": e["t1"], "episode_size": e["size"]}
    for r in jl("revision/A13/arch_peak.jsonl"):
        name = "arch_dt0p01" if r["dt"] == 0.01 else "n5_dt0p0025"
        c = max(r["checks"], key=lambda z: z["body_force_N"])
        p = pk[name]
        p.update({"rerun_peak_N": c["body_force_N"], "rerun_peak_t": c["t"],
                  "rerun_matches": abs(c["body_force_N"] - p["stored_peak_N"]) < 1e-6 * p["stored_peak_N"],
                  "size_at_peak": c["size"], "n_contacts_at_peak": c["n_contacts"],
                  "summed_overlap_m": c["body_force_N"] / 120000.0, "max_overlap_m": c["max_overlap_m"],
                  "max_overlap_cm_disp": sig(100 * c["max_overlap_m"], 2),
                  "max_contact_force_kN": c["max_contact_force_N"] / 1e3,
                  "max_contact_force_kN_disp": sig(c["max_contact_force_N"] / 1e3, 2),
                  "max_jamb_overlap_m": c["max_jamb_overlap_m"], "radii_m": c["radii_m"],
                  "max_overlap_over_all_checks_m": max(z["max_overlap_m"] for z in r["checks"])})
    out["arch"] = {"definition": "k * sum over agent-agent contacts of the arch component of (r_ij - d_ij), "
                                 "k = 1.2e5 kg/s^2 (experiments/arch/arch.py:64); summed, not per contact; "
                                 "the exponential term and the jamb contacts are not included", **pk}

    # 7 ---------------------------------------------------------------- T3 cells
    cnt = {}
    for f, src, key in (("E3/e3_dt.jsonl", "E3", lambda r: (r["job_id"].split("|")[0], r["mode"], r["dt"])),
                        ("E4/e4_escape.jsonl", "E4", lambda r: (r["snap"], r["cond"], r["beta_ref"]))):
        acc = {}
        for r in jl(f):
            if r.get("mode") == "C3_rvo2":
                continue
            acc[key(r)] = acc.get(key(r), 0) + r["v_moments"][0]
        cnt[src] = {"cells_total": len(acc), "cells_ge200": sum(v >= 200 for v in acc.values()),
                    "snapshots": len({k[0] for k in acc}), "levels": sorted({str(k[1:]) for k in acc})}
    out["t3_cells"] = {"E3": cnt["E3"], "E4": cnt["E4"],
                       "total_ge200": cnt["E3"]["cells_ge200"] + cnt["E4"]["cells_ge200"],
                       "stored": J("T3_variance.json")["stored_moments"]["cells"]}

    # 8 ---------------------------------------------------------------- ell
    out["ell"] = {"dt1_s": 0.005, "dt2_s": 0.02, "dt_ref_s": 0.01, "source": "experiments/E3/analyze.py:9,82-84"}

    # 10 --------------------------------------------------------------- lag
    lg = J("fix_a3.json")["lag"]["all"]
    out["lag"] = {"t0_mle_s": lg["shifted_exponential"]["t0_mle_s"], "earliest_escape_s": lg["earliest_escape_s"],
                  "ci95_s": lg["shifted_exponential"]["t0_ci95_s"], "events": lg["events"], "groups": lg["groups"],
                  "mle_on_boundary": abs(lg["shifted_exponential"]["t0_mle_s"] - lg["earliest_escape_s"]) < 1e-6,
                  "shape_at_lag": lg["shape_at_t0_mle"], "lag_first_cover_1_s": lg["lag_first_cover_1_s"]}

    # 11 --------------------------------------------------------------- asymmetry correlation
    S = {r["job_id"]: r for r in jl("E7b/e7b_static.jsonl")}
    th = J("E7b_analysis.json")["a_statics"]["fold_threshold"]["per_snapshot"]
    tags = sorted(S, key=lambda t: S[t]["seed"])
    ad = [S[t]["asym_axis_dist_m"] for t in tags]
    db = [abs(th[t]["plus"]["b_star"] - th[t]["minus"]["b_star"]) for t in tags]
    # signed: (upper member's axis distance - lower member's) against (b_f(-) - b_f(+))
    def axd(t, side):
        k = [str(i) for i in S[t]["ids"]].index(next(i for i, s in S[t]["side"].items() if s == side))
        return abs(S[t]["pos"][k][1] - 5)
    sd = [axd(t, "upper") - axd(t, "lower") for t in tags]
    sb = [th[t]["minus"]["b_star"] - th[t]["plus"]["b_star"] for t in tags]
    out["asym"] = {"n": len(tags), "spearman_abs": float(stats.spearmanr(ad, db)[0]),
                   "stored": J("E7b_analysis.json")["a_statics"]["fold_threshold"]["corr_asym_bstar_spearman"],
                   "spearman_signed": float(stats.spearmanr(sd, sb)[0]),
                   "sign_agree": int(sum((a > 0) == (b > 0) for a, b in zip(sd, sb)))}
    path = revlib.out_json("A13", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("creep",)}, indent=1, default=float)[:6000])
    print(json.dumps(out["creep"], indent=1)[:4000])
    print(path)


if __name__ == "__main__":
    main()
