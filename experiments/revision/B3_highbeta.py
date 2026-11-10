"""B3: activated escape at higher beta = dU / k_B T_eff, alone condition.

Snapshots: 3 of the 10 E4 snapshots spread over the alone barrier: sorted by (dU_alone, tag), ranks
round(linspace(0, 9, 3)) = 0, 4 (numpy rounds 4.5 to 4), 9. Barrier dU_alone, the blocker's tau and the noise
mapping exactly as experiments/E4/e4_escape.py (sigma = teff.sigma_for(dU / beta, 0.01 s, tau_b); C1, CF
flags, dt = 0.01 s, condition "alone": the other residual agents deactivated; escape = blocker centre at
x >= 10; runlib.escape unchanged).
Levels beta in {5, 6, 7}, 20 restarts each, noise seeds 51000 + 1000 k + 100 * level_index + rep (disjoint from
E4's 11000 + ...). Censoring per (snapshot, beta): T = ln(20 / 4.5) / lambda_slow, so that at least 15 of 20
escape with probability ~0.9 when the rate is lambda_slow, where lambda_slow is the smaller of the two E4
extrapolations to beta: the free Arrhenius fit (exp(intercept - ratio * beta), slope ratio < 1) and the
fixed-slope prefactor fit (nu_hat exp(-beta), ratio 1).
Output: data/revision/B3/b3.jsonl (job_id "<tag>|alone|b<beta>|<rep>"), resumable.
Usage: B3_highbeta.py [qargs options]  |  B3_highbeta.py plan   (analysis: B3_analyze.py)
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import CF, DERIVED, np, run_jobs  # noqa: E402
import qargs  # noqa: E402
from runlib import escape  # noqa: E402
from teff import M, sigma_for  # noqa: E402
import e4_escape  # noqa: E402

OUT = os.path.join(revlib.data_dir("B3"), "b3.jsonl")
BETAS = (5.0, 6.0, 7.0)
N_REP, DT = 20, 0.01


def chosen():
    S = [s for s in e4_escape.snapshots() if s["dU"]["alone"] is not None]
    S.sort(key=lambda s: (s["dU"]["alone"], s["tag"]))
    idx = np.round(np.linspace(0, len(S) - 1, 3)).astype(int)
    fits = json.load(open(os.path.join(DERIVED, "E4_analysis.json")))["snapshots"]
    out = []
    for k in idx:
        s = dict(S[k])
        s["fit"] = fits[s["tag"]]["conds"]["alone"]["arrhenius"]
        out.append(s)
    return out


def t_cens(fit, beta):
    lam_free = math.exp(fit["intercept"] - fit["ratio"] * beta)
    lam_fix = fit["nu_hat"] * math.exp(-beta)
    lam = min(lam_free, lam_fix)
    return math.log(20 / 4.5) / lam, lam_free, lam_fix


def jobs():
    J = []
    for k, s in enumerate(chosen()):
        dU = s["dU"]["alone"]
        for lv, beta in enumerate(BETAS):
            T, lf, lx = t_cens(s["fit"], beta)
            sg = sigma_for(dU / beta, DT, s["tau_b"])
            for rep in range(N_REP):
                J.append({"job_id": f"{s['tag']}|alone|b{beta:g}|{rep}", "snap": s["snap"], "blocker": s["blocker"],
                          "tag": s["tag"], "cond": "alone", "config": "C1", "flags": dict(CF), "sigma": sg, "rep": rep,
                          "beta_ref": beta, "dU_cond": dU, "tau_b": s["tau_b"], "m": M, "kT_eff": dU / beta,
                          "noise_seed": 51000 + 1000 * k + 100 * lv + rep, "dt": DT, "t_cens": round(T, 1),
                          "lam_pred_free": lf, "lam_pred_fixed": lx})
    J.sort(key=lambda j: -j["t_cens"])      # longest censoring first, so the long runs do not form the tail
    return J


if __name__ == "__main__":
    if sys.argv[1:2] == ["plan"]:
        J = jobs()
        for s in chosen():
            print(s["tag"], round(s["dU"]["alone"], 2), "ratio", round(s["fit"]["ratio"], 3))
        exp_cpu = 0.0
        for j in J:
            if j["rep"] == 0:
                lam = j["lam_pred_free"]
                mean_t = (1 - math.exp(-lam * j["t_cens"])) / lam
                exp_cpu += N_REP * mean_t * 0.061
                print(j["job_id"], "T_cens", j["t_cens"], "lam_free %.2e lam_fix %.2e" % (j["lam_pred_free"], j["lam_pred_fixed"]))
        print("expected CPU-h (free-fit rates, 0.061 s wall per simulated s):", round(exp_cpu / 3600, 2))
        print("worst case CPU-h (all censored):", round(sum(j["t_cens"] for j in J) * 0.061 / 3600, 2))
    else:
        a = qargs.parse()
        run_jobs(qargs.select(jobs(), a), escape, a.out or OUT, workers=a.workers, log_every=5)
