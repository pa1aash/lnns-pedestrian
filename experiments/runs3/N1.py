"""run-N1: lone-trap noise at the calibrated sigma, 20 seeds per lone keystone.

sigma_N1 is set once, when the step starts, by inverting a binomial-logit fit (experiments/lib/fits.py)
of "blocker freed within 120 s" against sigma over the E2 noise restarts (sigma in {0.03, 0.05, 0.07} m/s,
5 seeds each) in the lone-keystone stratum (34 snapshots) at the freed fraction of C3 RVO2 (unperturbed
runs) in the same stratum; rounded to 1e-4 m/s and written to data/N1/sigma_n1.json (fixed once set;
the C3 published fraction is recorded beside it). The fit is extrapolated by at most 0.005 m/s; beyond
that the step stops with code 4.
Quench: as E2 (experiments/E2/e2_quench.py, runner quench_e2), C1 + per-step noise sigma_N1, corrected-
forward flags (CF), dt = 0.01 s, 120 s, full window. Seeds 27000 + 100 k + rep, rep = 0..19 (k = the
snapshot's index in the E2 selection order), disjoint from E2's 7000 + 100 k + rep.
Output: data/N1/n1.jsonl (job_id "<tag>|noiseN1|<rep>"), resumable.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3 import CF, DATA, load_runs, out_dir, qargs, run_jobs  # noqa: E402
import e2_quench  # noqa: E402
import fits  # noqa: E402

D = out_dir("N1")
OUT = os.path.join(D, "n1.jsonl")
SIG = os.path.join(D, "sigma_n1.json")
STRATUM = "lone_keystone"
N_SEEDS = 20
MAX_EXTRAP = 0.005


def calibrate(path=SIG):
    if os.path.exists(path):
        return json.load(open(path))
    S = {t: (blk, cls) for t, _, blk, cls in e2_quench.snapshots()}
    R = load_runs(e2_quench.OUT)

    def freed(r):
        blk, _ = S[r["job_id"].split("|")[0]]
        t = r["exits"].get(str(blk))
        return t is not None and t <= e2_quench.T_Q + 1e-9

    lone = [r for r in R if r["job_id"].split("|")[0] in S and S[r["job_id"].split("|")[0]][1] == STRATUM]
    sig = list(e2_quench.SIGMAS)
    k = [sum(freed(r) for r in lone if r["arm"] == f"noise{s}") for s in sig]
    n = [sum(1 for r in lone if r["arm"] == f"noise{s}") for s in sig]
    tgt = {}
    for solver in ("C3_rvo2", "C3_pub"):
        rr = [r for r in lone if r["arm"] == solver and r["job_id"].endswith("|u")]
        tgt[solver] = {"k": sum(map(freed, rr)), "n": len(rr)}
    f = fits.fit_logit(sig, k, n)
    p = tgt["C3_rvo2"]["k"] / tgt["C3_rvo2"]["n"]
    inv = fits.invert(f, p, n_p=tgt["C3_rvo2"]["n"])
    rec = {"script": "experiments/runs3/N1.py", "made": datetime.datetime.now().isoformat(timespec="seconds"),
           "stratum": STRATUM, "E2_noise": {"sigma": sig, "k": k, "n": n}, "targets": tgt, "fit": f,
           "inversion": inv, "model": "P(blocker freed) = 1 / (1 + exp(-(a + b sigma)))"}
    if not sig[0] - MAX_EXTRAP <= inv["x_star"] <= sig[-1] + MAX_EXTRAP:
        rec.update(status="out_of_range")
    else:
        rec.update(status="ok", sigma_n1=round(inv["x_star"], 4))
    json.dump(rec, open(path, "w"), indent=1, default=float)
    return rec


def jobs(sigma):
    J = []
    for k, (tag, snap, blk, cls) in enumerate(e2_quench.snapshots()):
        if cls != STRATUM:
            continue
        for rep in range(N_SEEDS):
            J.append({"job_id": f"{tag}|noiseN1|{rep}", "snap": snap, "arm": "noiseN1", "config": "C1",
                      "flags": dict(CF), "sigma": sigma, "noise_seed": 27000 + 100 * k + rep, "rep": rep,
                      "deterministic": False, "t_q": e2_quench.T_Q, "blocker": blk, "stratum": cls})
    return J


def main(argv=None):
    a = qargs.parse(argv)
    rec = calibrate()
    if rec["status"] != "ok":
        print("N1 stopped: sigma out of range", rec["inversion"], flush=True)
        sys.exit(4)
    print("N1 sigma =", rec["sigma_n1"], flush=True)
    return run_jobs(qargs.select(jobs(rec["sigma_n1"]), a), e2_quench.quench_e2, a.out or OUT,
                    workers=a.workers, log_every=20)


if __name__ == "__main__":
    print("wall", main())
