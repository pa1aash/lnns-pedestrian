"""Task 4: predicted log rate ratio l (Eq. 11) of the time-step set at beta0 = 1.5 and 2.5 under three barrier choices.

sigma per snapshot was set in E3 (experiments/E3/e3_dt.py noise_params, selection.json E3 "dU") from the full-condition
saddle height dU_i (BAR all-mobile barrier accepted by the gate, = dU_rep) and the blocker's tau, so that
dU_i / k_B T_eff(0.01 s) = beta0. Eq. (11) is linear in the barrier at fixed sigma: l = dU (1/kT(0.02) - 1/kT(0.005)).
  (a) dU = saddle height dU_i (as run)            l_a = ell_pred_per_step of E3
  (b) dU = energy span (rev5_X1 paths[tag|full])  l_b = l_a dU_span / dU_i (differs only for E1b_seed237)
  (c) (b) times the measured alone slope ratio r  l_c = r l_b; r = the pooled alone ratio of A3 (0.89, rev2_A3
      pooled) and, when data/derived/rev7_T2.json exists, the task-2 pooled ratio over all 56 snapshots
Observed: E3_analysis.json per-step l per snapshot and the level means with their snapshot-bootstrap intervals.
Eq. (10) alone with beta0 exact: l = beta0 kT(0.01) (1/kT(0.02) - 1/kT(0.005)) per snapshot (identical to (a)).
Output: data/derived/rev7_T4.json"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import np  # noqa: E402
from teff import kT_eff  # noqa: E402


def main():
    E3 = json.load(open(os.path.join(L.DERIVED, "E3_analysis.json")))
    X1 = json.load(open(os.path.join(L.DERIVED, "rev5_X1.json")))["paths"]
    A3 = json.load(open(os.path.join(L.DERIVED, "rev2_A3.json")))
    r_a3 = A3["pooled"]["ratio"] if isinstance(A3["pooled"], dict) and "ratio" in A3["pooled"] else None
    t2p = os.path.join(L.DERIVED, "rev7_T2.json")
    r_t2 = json.load(open(t2p))["pooled_all"]["ratio"] if os.path.exists(t2p) else None
    rows = []
    for tag, s in E3["snapshots"].items():
        span = X1[f"{tag}|full"]["dU_span"]
        la = s["ell_pred_per_step"]
        sg, tb, b0 = s["sigma_i"], s["tau_b"], s["beta_ref"]
        k1, k2, k05 = kT_eff(sg, 0.01, tb), kT_eff(sg, 0.02, tb), kT_eff(sg, 0.005, tb)
        eq10 = b0 * k1 * (1 / k2 - 1 / k05)
        obs = s["ell"]["per_step"].get("obs")
        rows.append({"tag": tag, "beta0": b0, "dU_saddle": s["dU_i"], "dU_span": span, "l_a": la, "l_eq10": eq10,
                     "l_b": la * span / s["dU_i"], "beta0_span": b0 * span / s["dU_i"], "obs": obs,
                     "obs_ci95": s["ell"]["per_step"].get("ci95")})
    out = {"doc": __doc__, "r_alone_A3": r_a3, "r_alone_T2": r_t2, "rows": rows, "levels": {}}
    hl = E3["headline"]
    for b0, key in ((1.5, "b1p5"), (2.5, "b2p5")):
        R = [r for r in rows if r["beta0"] == b0 and r["obs"] is not None]
        lev = {"n": len(R), "pred_a": float(np.mean([r["l_a"] for r in R])),
               "pred_eq10": float(np.mean([r["l_eq10"] for r in R])),
               "pred_b": float(np.mean([r["l_b"] for r in R])),
               "obs": hl[f"ell_ps_{key}_obs"], "obs_lo": hl[f"ell_ps_{key}_lo"], "obs_hi": hl[f"ell_ps_{key}_hi"],
               "e3_pred_check": hl[f"ell_ps_{key}_pred"]}
        if r_a3:
            lev["pred_c_A3"] = r_a3 * lev["pred_b"]
        if r_t2:
            lev["pred_c_T2"] = r_t2 * lev["pred_b"]
        for k in [k for k in lev if k.startswith("pred_") and k != "pred_eq10"]:
            lev[f"inside_{k}"] = bool(lev["obs_lo"] <= lev[k] <= lev["obs_hi"])
        out["levels"][f"{b0:g}"] = lev
    print(json.dumps(out["levels"], indent=1), r_a3, r_t2)
    print(L.out_json("T4", out))


if __name__ == "__main__":
    main()
