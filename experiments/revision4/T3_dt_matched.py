"""T3 runs: the time-step probe of E3 at the matched noise level sigma = 0.07 m/s.

Snapshots, condition, restart and escape rule: those of experiments/E3/e3_dt.py (the 20 E3 snapshots of
data/derived/selection.json, condition "full", restart C1 from the frozen snapshot with CF union arm flags, escape =
blocker centre crosses x >= 10, runlib.escape). Only the noise level changes: sigma = 0.07 m/s for every snapshot
(E3 set sigma_i per snapshot for beta_ref = 1.5 or 2.5 at dt = 0.01 s).
  per_step   C1 + sigma = 0.07 m/s at dt in {0.005, 0.01, 0.02} s (sigma fixed per step, k_B T_eff varies with dt);
  dt_scaled  C1 + w2_noise = dt_scaled, base sigma 0.07 m/s at dt = 0.01 s (per-step sigma 0.07 sqrt(dt / 0.01)),
             at the same three dt (at dt = 0.01 s the two arms have the same per-step sigma and differ in seeds).
20 restarts per (snapshot, arm, dt) with E3's noise seeds 51000 + 1000 k + 10 round(1000 dt) + rep (+500 for
dt_scaled), k = index in the E3 list; censored at 300 s, 900 s for per_step at dt = 0.02 s (E3's rules).
Each row carries beta = dU_i / k_B T_eff(sigma, dt, tau_b) (experiments/lib/teff.py) and the predicted
ell_i = dU_i (1/k_B T_eff(0.02) - 1/k_B T_eff(0.005)).
Output: data/revision4/T3/t3_dt.jsonl (job_id "<tag>|dt<dt>|<mode>|<rep>"), resumable.
Usage: T3_dt_matched.py [--workers W]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import CF, run_jobs  # noqa: E402
import e3_dt as E3  # noqa: E402
from runlib import escape  # noqa: E402
from teff import kT_eff  # noqa: E402

SIGMA = 0.07
OUT = os.path.join(rev4lib.data_dir("T3"), "t3_dt.jsonl")


def jobs():
    J = []
    for k, (tag, snap, b, npar) in enumerate(E3.snapshots()):
        tau_b, dU = npar["tau_b"], npar["dU_i"]
        ell = {m: dU * (1.0 / kT_eff(SIGMA, 0.02, tau_b, mode=m) - 1.0 / kT_eff(SIGMA, 0.005, tau_b, mode=m))
               for m in E3.MODES}
        meta = {"tau_b": tau_b, "dU_i": dU, "dU_rank": npar["dU_rank"], "k": k, "sigma_E3": npar["sigma_i"],
                "ell_pred_per_step": ell["per_step"], "ell_pred_dt_scaled": ell["dt_scaled"]}
        for dtv in E3.DTS:
            for mode in E3.MODES:
                kT = kT_eff(SIGMA, dtv, tau_b, mode=mode)
                tc = E3.T_CENS_LONG if (mode == "per_step" and dtv == 0.02) else E3.T_CENS
                for rep in range(E3.N_REP):
                    J.append({"job_id": f"{tag}|dt{dtv}|{mode}|{rep}", "snap": snap, "blocker": b, "cond": "full",
                              "config": "C1", "flags": {**CF, "w2_noise": mode}, "sigma": SIGMA, "dt": dtv,
                              "mode": mode, "rep": rep, "t_cens": tc, **meta, "kT_eff": kT, "beta": dU / kT,
                              "noise_seed": 51000 + 1000 * k + 10 * int(round(1000 * dtv)) + rep
                              + (500 if mode == "dt_scaled" else 0)})
    return J


if __name__ == "__main__":
    print("wall", run_jobs(jobs(), escape, OUT, workers=rev4lib.workers(sys.argv), log_every=100))
