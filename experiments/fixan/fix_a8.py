"""Critical door width from the jamb wall law against the E7 critical width (FIX_PLAN A-8, item 05-5).

A lone agent of radius r at rest on the door axis (y = 5) at distance s in front of the door plane x = 10
feels the two door-edge points (10, 5 -+ h), h = w/2, each at distance d = sqrt(s^2 + h^2), through the
social term of the wall law A_w exp((r - d)/B_w) n. The lateral components cancel; the backward (x)
components add: G(s) = 2 A_w exp((r - d)/B_w) s/d. The agent is held alone when max_s G(s) > F, F = m v0/tau.
Run from the worktree root:  .venv/bin/python experiments/fixan/fix_a8.py
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import brentq

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data", "derived", "fix_a8.json")
A_W, B_W, M = 2000.0, 0.08, 80.0
RNG = np.random.default_rng(20261109)


def s_star(h, B=B_W):
    """Maximiser of G: d ln G/ds = 0  <=>  s^2 d = B h^2."""
    return brentq(lambda s: s * s * np.sqrt(s * s + h * h) - B * h * h, 1e-9, 10.0)


def gmax(r, h, A=A_W, B=B_W):
    s = s_star(h, B)
    d = np.hypot(s, h)
    return 2.0 * A * np.exp((r - d) / B) * s / d, s, d


def w_crit(r, F, A=A_W, B=B_W):
    """Exact width 2h at which max_s G = F (G decreases with h)."""
    h = brentq(lambda h: gmax(r, h, A, B)[0] - F, 1e-3, 3.0)
    return 2.0 * h


def w_naive(r, F, A=A_W, B=B_W):
    return 2.0 * (r + B * np.log(2.0 * A / F))


def w_approx(r, F, A=A_W, B=B_W, it=50):
    """Small-B/h expansion: s* ~ sqrt(B h), d* ~ h + B/2, s*/d* ~ sqrt(B/h):
    h = r - B/2 + B ln(2A/F) + (B/2) ln(B/h), solved by fixed-point iteration."""
    h = r + B * np.log(2 * A / F)
    for _ in range(it):
        h = r - B / 2 + B * np.log(2 * A / F) + 0.5 * B * np.log(B / h)
    return 2.0 * h


def check_against_code():
    """Compare the closed-form g_max with the simulator's WallForces profile (all room walls)."""
    sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
    cwd = os.getcwd()
    import w2lib  # chdirs to code/
    os.chdir(cwd)
    rows = []
    for r in (0.20, 0.25, 0.30, 0.35):
        for w in (0.8, 0.9):
            xs = np.linspace(9.0, 10.0, 20001)
            code = w2lib.max_backward(r, width=w, xs=xs)
            rows.append({"r": r, "w": w, "gmax_code_N": code, "gmax_closed_form_N": gmax(r, w / 2)[0]})
    return rows


def boot_median(x, n=2000):
    x = np.asarray(x)
    b = np.median(RNG.choice(x, (n, len(x)), replace=True), axis=1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def load_runs():
    """Spawned agents (r, v0, tau) and completion of the C1 corrected-forward runs at w = 0.7-1.0 m."""
    import ast
    runs = []
    with open(os.path.join(ROOT, "data", "E7", "e7_cells.jsonl")) as f:
        for line in f:
            x = json.loads(line)
            if x["cell"] in ("w0.7", "w0.9", "w1.0"):
                att = x["attrs"] if isinstance(x["attrs"], list) else ast.literal_eval(x["attrs"])
                runs.append({"w": x["width"], "seed": x["seed"], "complete": bool(x["complete"]), "attrs": att})
    with open(os.path.join(ROOT, "data", "E1", "E1_runs.jsonl")) as f:
        for line in f:
            x = json.loads(line)
            if x["mode"] == "E1b" and 42 <= x["seed"] <= 141:
                att = x["attrs"] if isinstance(x["attrs"], list) else ast.literal_eval(x["attrs"])
                runs.append({"w": 0.8, "seed": x["seed"], "complete": bool(x["complete"]), "attrs": att})
    return runs


def main():
    e7 = json.load(open(os.path.join(ROOT, "data", "derived", "E7_analysis.json")))["critical_width"]
    out = {"script": "experiments/fixan/fix_a8.py", "params": {"A_w_N": A_W, "B_w_m": B_W, "m_kg": M}}
    out["method"] = (
        "Wall law (Eq. wall, social term; no contact since d > r at the critical width): a lone agent of radius r on the "
        "door axis at distance s before the door plane sees the two free jamb ends (10, 5 -+ h), h = w/2, at distance "
        "d = sqrt(s^2 + h^2). Lateral parts cancel; the backward force is G(s) = 2 A_w exp((r - d)/B_w) s/d. "
        "d ln G/ds = 1/s - s/(B_w d) - s/d^2 = 0 gives s*^2 d* = B_w h^2. The agent is held alone iff "
        "G(s*) > F = m v0/tau (Weidmann factor 1 at rest alone). The exact critical width w_c = 2h solves "
        "2 A_w exp((r - d*)/B_w) s*/d* = F. For B_w << h, s* ~ sqrt(B_w h), d* ~ h + B_w/2, s*/d* ~ sqrt(B_w/h), so "
        "w_c ~ 2[r + B_w ln(2 A_w/F) - B_w/2 + (B_w/2) ln(B_w/h)]: the effective-diameter form 2[r + B_w ln(2 A_w/F)] "
        "plus a geometric correction -B_w[1 + ln(h/B_w)] (about -0.2 m at w = 0.88 m) from the obliquity s/d of the "
        "edge force. Population: every spawned agent of the 400 C1 corrected-forward runs at w = 0.7, 0.8, 0.9, 1.0 m "
        "(seeds 42-141) gets its own w_c; a run is predicted to complete at width w iff no agent has w_c > w "
        "(no stuck-alone agent), and the predicted half-completion width is the median over runs of max w_c "
        "(bootstrap 95% over runs, 2000 resamples).")
    # reference agent (Table 1 means)
    r0, v0, tau0 = 0.25, 1.34, 0.5
    F0 = M * v0 / tau0
    ref = {"r_m": r0, "v0_mps": v0, "tau_s": tau0, "F_drive_N": F0,
           "w_c_exact_m": w_crit(r0, F0), "w_c_naive_m": w_naive(r0, F0), "w_c_approx_m": w_approx(r0, F0)}
    g, s, d = gmax(r0, ref["w_c_exact_m"] / 2)
    ref.update({"s_star_m": s, "d_star_m": d, "check_gmax_at_wc_N": g})
    out["reference_agent"] = ref
    out["closed_form_vs_code"] = check_against_code()
    out["closed_form_vs_code_max_rel_err"] = max(abs(x["gmax_code_N"] / x["gmax_closed_form_N"] - 1)
                                                 for x in out["closed_form_vs_code"])
    # population
    runs = load_runs()
    allwc, allnaive, runmax, per_w = [], [], [], {}
    for R in runs:
        wc = np.array([w_crit(a["r"], M * a["v0"] / a["tau"]) for a in R["attrs"]])
        R["max_wc"] = float(wc.max())
        R["n_stuck_alone"] = int((wc > R["w"]).sum())
        if R["w"] == 0.8:
            allwc += wc.tolist()
            allnaive += [w_naive(a["r"], M * a["v0"] / a["tau"]) for a in R["attrs"]]
            runmax.append(R["max_wc"])
    allwc, runmax = np.array(allwc), np.array(runmax)
    out["agents"] = {"n_agents": int(len(allwc)), "n_runs": int(len(runmax)),
                     "method": "per-agent exact w_c over the spawned agents of the 100 w = 0.8 m runs (one draw per seed)",
                     "w_c_median_m": float(np.median(allwc)), "w_c_median_ci95": boot_median(allwc),
                     "w_c_p05_m": float(np.percentile(allwc, 5)), "w_c_p95_m": float(np.percentile(allwc, 95)),
                     "w_c_p99_m": float(np.percentile(allwc, 99)), "w_c_max_m": float(allwc.max()),
                     "w_naive_median_m": float(np.median(allnaive)),
                     "frac_wc_above_0p88": float((allwc > 0.88).mean())}
    out["run_level"] = {"method": "median over runs of the largest per-agent w_c (predicted 50% completion width)",
                        "w50_pred_m": float(np.median(runmax)), "w50_pred_ci95": boot_median(runmax),
                        "max_wc_p05_m": float(np.percentile(runmax, 5)), "max_wc_p95_m": float(np.percentile(runmax, 95))}
    for w in (0.7, 0.8, 0.9, 1.0):
        Rw = [R for R in runs if R["w"] == w]
        none = [R for R in Rw if R["n_stuck_alone"] == 0]
        per_w[f"w{w:.1f}".replace(".", "p")] = {
            "w_m": w, "n_runs": len(Rw), "observed_complete": sum(R["complete"] for R in Rw),
            "predicted_complete_no_stuck_alone": len(none),
            "complete_given_no_stuck_alone": sum(R["complete"] for R in none),
            "complete_given_some_stuck_alone": sum(R["complete"] for R in Rw if R["n_stuck_alone"] > 0),
            "n_some_stuck_alone": len(Rw) - len(none),
            "mean_n_stuck_alone": float(np.mean([R["n_stuck_alone"] for R in Rw]))}
    out["by_width"] = per_w
    out["e7_w50"] = {"w50_logit_m": e7["w50_logit"], "ci95": e7["w50_logit_ci95"]}
    out["comparison"] = {
        "naive_minus_e7_m": ref["w_c_naive_m"] - e7["w50_logit"],
        "exact_ref_minus_e7_m": ref["w_c_exact_m"] - e7["w50_logit"],
        "run_level_minus_e7_m": out["run_level"]["w50_pred_m"] - e7["w50_logit"],
        "run_level_ci_overlaps_e7_ci": bool(out["run_level"]["w50_pred_ci95"][0] <= e7["w50_logit_ci95"][1]
                                            and out["run_level"]["w50_pred_ci95"][1] >= e7["w50_logit_ci95"][0])}
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("reference_agent", "closed_form_vs_code_max_rel_err", "agents", "run_level",
                                          "by_width", "e7_w50", "comparison")}, indent=1))


if __name__ == "__main__":
    main()
