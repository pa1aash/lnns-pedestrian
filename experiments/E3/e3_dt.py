"""E3: time-step scaling on the E3 snapshots (data/derived/selection.json; read when the step starts).

Corrected-forward, all residual agents mobile (condition "full"), restart from the frozen snapshot with
CF union arm flags (pattern: experiments/pilot/w23_escape.py, kind "dtpilot" / "c3dt").
Noise per snapshot (C15): for snapshot i with collective barrier dU_i (BAR all_mobile.dU_climb) and
blocker relaxation time tau_b, beta_ref = dU_i / k_B T_eff at dt = 0.01 s is 1.5 for even dU rank and
2.5 for odd (rank within the E3 set, 0 = smallest dU); k_B T_target = dU_i / beta_ref and
sigma_i = sqrt(k_B T_target (1 - (1 - 0.01 / tau_b)^2) / m), m = 80 kg (T3, experiments/lib/teff.py).
  per_step   C1 + sigma_i at dt in {0.005, 0.01, 0.02} s (sigma fixed, k_B T_eff varies with dt);
  dt_scaled  C1 + w2_noise = dt_scaled with base sigma_i (sigma_i sqrt(dt / 0.01); k_B T_eff about fixed);
  20 restarts per (snapshot, arm, dt), noise seeds 51000 + 1000 k + 10 * round(1000 dt) + rep
  (+500 for dt_scaled), k = index in the E3 list; censored at 300 s, 900 s for per_step at dt = 0.02 s;
  C3_rvo2   deterministic, one run per dt, 300 s.
Every row carries sigma_i, beta_ref, tau_b, dU_i, the exact discrete k_B T_eff and beta at its own dt,
and the predicted per-step slope ell_i = dU_i (1/k_B T_eff(0.02) - 1/k_B T_eff(0.005)) (per_step arm;
the dt_scaled value is stored as well).
Escape (first-exit) time = the blocker's centre crossing the door plane x >= 10; the first exit of any
agent is recorded as well.
Output: data/E3/e3_dt.jsonl (job_id "<tag>|dt<dt>|<mode>|<rep>" / "<tag>|dt<dt>|C3_rvo2"), resumable.
"""
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, ROOT, run_jobs  # noqa: E402
from runlib import escape  # noqa: E402
from teff import M, kT_eff, sigma_for  # noqa: E402

OUT = os.path.join(DATA, "E3", "e3_dt.jsonl")
DTS = (0.005, 0.01, 0.02)
MODES = ("per_step", "dt_scaled")
N_REP, T_CENS, T_CENS_LONG, DT_REF = 20, 300.0, 900.0, 0.01
BETA_EVEN, BETA_ODD = 1.5, 2.5


def noise_params(dU, rank, tau_b):
    beta_ref = BETA_EVEN if rank % 2 == 0 else BETA_ODD
    kT = dU / beta_ref
    sigma = sigma_for(kT, DT_REF, tau_b)
    ell = {m: dU * (1.0 / kT_eff(sigma, 0.02, tau_b, mode=m) - 1.0 / kT_eff(sigma, 0.005, tau_b, mode=m))
           for m in MODES}
    return {"sigma_i": sigma, "beta_ref": beta_ref, "tau_b": tau_b, "dU_i": dU, "dU_rank": rank, "m": M,
            "kT_target": kT, "ell_pred_per_step": ell["per_step"], "ell_pred_dt_scaled": ell["dt_scaled"]}


def snapshots():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    if "E3" not in sel:
        return None
    S = []
    for s in sel["E3"]["snapshots"]:
        path = os.path.join(ROOT, s["snap"])
        tau_b = float(pickle.load(open(path, "rb"))["state"].taus[s["blocker"]])
        S.append((s["tag"], path, s["blocker"], noise_params(s["dU"], s["dU_rank"], tau_b)))
    return S


def jobs():
    S = snapshots()
    if S is None:
        return None
    J = []
    for k, (tag, snap, b, npar) in enumerate(S):
        for dtv in DTS:
            for mode in MODES:
                kT = kT_eff(npar["sigma_i"], dtv, npar["tau_b"], mode=mode)
                tc = T_CENS_LONG if (mode == "per_step" and dtv == 0.02) else T_CENS
                for rep in range(N_REP):
                    J.append({"job_id": f"{tag}|dt{dtv}|{mode}|{rep}", "snap": snap, "blocker": b, "cond": "full",
                              "config": "C1", "flags": {**CF, "w2_noise": mode}, "sigma": npar["sigma_i"], "dt": dtv,
                              "mode": mode, "rep": rep, "t_cens": tc, **npar, "kT_eff": kT, "beta": npar["dU_i"] / kT,
                              "noise_seed": 51000 + 1000 * k + 10 * int(round(1000 * dtv)) + rep
                              + (500 if mode == "dt_scaled" else 0)})
            J.append({"job_id": f"{tag}|dt{dtv}|C3_rvo2", "snap": snap, "blocker": b, "cond": "full",
                      "config": "C3", "flags": {**CF, "w2_orca": "rvo2"}, "sigma": 0.0, "dt": dtv,
                      "mode": "C3_rvo2", "t_cens": T_CENS, **npar})
    return J


def main(out=OUT, J=None, workers=4):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(jobs() if J is None else J, escape, out, workers=workers, log_every=50)


if __name__ == "__main__":
    print("wall", main())
