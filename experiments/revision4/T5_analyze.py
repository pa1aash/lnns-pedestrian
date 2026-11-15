"""T5 analysis: E1b_seed170 (full condition, barrier 0.128 J, 0/60 escapes in E4).
Collects the string result (t5_string.json), the second-trap result (t5_second.json, round 0 only: round 1 starts
from an image already past the door, gradient 145 N, and is not a rest state), and the extended restarts
(t5_runs.jsonl). For each beta_ref level: escapes / runs (Wilson 95%), escape times, the blocker's largest x, the
largest displacement of agents 15 and 85 (the two that move 0.69 and 0.81 m into M2), the realised k_B T of the four
string agents, and beta_M2 = dU(M2 -> exit) / k_B T_eff. A harmonic (Vineyard) estimate of the exit rate from M2
uses the M2 and exit-saddle Hessian eigenvalues (N/m); the four agents all have mass 80 kg, so the mass-weighted
eigenvalues are these divided by 80.
Output: data/derived/rev4_T5.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import wilson  # noqa: E402

D = rev4lib.data_dir("T5")
S = json.load(open(os.path.join(D, "t5_string.json")))
SEC = json.load(open(os.path.join(D, "t5_second.json")))
R0 = SEC["rounds"][0]
runs = [json.loads(l) for l in open(os.path.join(D, "t5_runs.jsonl"))]
ag = S["agents"]
masses = np.array(S["mass"], float)
dU_exit = R0["62"]["dU_climb"]

# harmonic exit rate from M2 (equal-mass approximation)
lm = np.array(R0["hess_M2_eig_N_per_m"])
ls = np.array(R0["62"]["hess_saddle_eig_N_per_m"])
assert (lm > 0).all() and (ls < 0).sum() == 1
assert np.ptp(masses) == 0
mbar = float(masses[0])
nu_M2 = math.sqrt(np.prod(lm) / np.prod(ls[ls > 0]) / mbar) / (2 * math.pi)

levels = {}
for b in sorted({r["beta_ref"] for r in runs}):
    rr = [r for r in runs if r["beta_ref"] == b]
    k = sum(not r["censored"] for r in rr)
    _, lo, hi = wilson(k, len(rr))
    idx = {a: rr[0]["agents"].index(a) for a in ag}
    kT = float(rr[0]["kT_eff"])
    disp = {a: [r["max_disp_m"][idx[a]] for r in rr] for a in ag}
    kTr = {a: float(np.mean([r["kT_realised_J"][idx[a]] for r in rr])) for a in ag}
    beta = dU_exit / kT
    levels["b" + str(b).replace(".", "p")] = {
        "n": len(rr), "escaped": k, "ci95": [lo, hi], "t_cens_s": rr[0]["t_cens"], "sigma": rr[0]["sigma"],
        "kT_eff_J": kT, "kT_realised_J_mean": kTr, "beta_vs_0128J": rr[0]["dU_full"] / kT, "beta_M2_exit": beta,
        "escape_t_s": sorted(r["escape_t"] for r in rr if not r["censored"]),
        "blocker_xmax_m": [min(r["blocker_xmax"] for r in rr), float(np.median([r["blocker_xmax"] for r in rr])),
                           max(r["blocker_xmax"] for r in rr)],
        "x0_blocker": rr[0]["x0"],
        "max_disp_m": {str(a): [min(v), float(np.median(v)), max(v)] for a, v in disp.items()},
        "runs_reaching_M2": sum(disp[15][i] > 0.5 and disp[85][i] > 0.5 for i in range(len(rr))),
        "harmonic_mean_exit_from_M2_s": math.exp(beta) / nu_M2 if beta < 700 else None,
        "first_other_exit_t_s_median": (float(np.median([r["first_other_exit_t"] for r in rr
                                                          if r["first_other_exit_t"] is not None]))
                                        if any(r["first_other_exit_t"] is not None for r in rr) else None),
        "cpu_s": float(sum(r["wall_s"] for r in rr)),
    }

out = {"script": "experiments/revision4/T5_analyze.py", "doc": __doc__, "tag": S["tag"], "blocker": S["blocker"],
       "agents": ag,
       "barrier_full_J": S["string"]["62"]["dU_climb"],
       "M2": {k: R0[k] for k in ("U_M2_minus_U0", "grad_norm_M2", "force_check_M2_N", "hess_M2_eig_N_per_m",
                                 "M2_disp_from_min_m", "M2_pair_gaps_m", "M2_wall_clear_m")},
       "exit_from_M2": {"dU_31": R0["31"]["dU_climb"], "dU_62": dU_exit, "rel_change_doubling": R0["rel_change_doubling"],
                        "saddle_blocker_x": R0["62"]["saddle"][0][0],
                        "hess_saddle_eig_N_per_m": R0["62"]["hess_saddle_eig_N_per_m"],
                        "saddle_disp_from_M2_m": R0["62"]["saddle_disp_from_M2_m"]},
       "nu_harmonic_M2_per_s": nu_M2, "mass_mean_kg": mbar, "mass_range_kg": [float(masses.min()), float(masses.max())],
       "round1_discarded": "starts from image 51 (blocker 1.30 m from the minimum, beyond the door), gradient 145 N",
       "levels": levels}
rev4lib.out_json("T5", out)
print(json.dumps({k: {kk: v[kk] for kk in ("n", "escaped", "beta_M2_exit", "runs_reaching_M2", "blocker_xmax_m",
                                         "harmonic_mean_exit_from_M2_s")} for k, v in levels.items()}, indent=1,
                 default=float))
print("nu_M2", nu_M2, "dU_exit", dU_exit)
