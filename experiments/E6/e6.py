"""E6: matched completion, room bottleneck w = 0.8 m, 100 agents, 600 s cap, stop at deadlock (every
active |v| < 0.01 m/s for 10 s, no exit) or completion (recorder experiments/lib/runlib.whole_run).
  E6a  C3 with RVO2 ORCA, corrected-forward (CF), seeds 242-427 (186).
  E6b  C1 + sigma*, CF, the same seeds. sigma* is set once, at the start of E6b, by inverting a binomial-
       logit fit of the E5b completions (CF, C1 + sigma, sigma in {0.03, ..., 0.07}, seeds 42-141; data/E5/
       e5b.jsonl; experiments/lib/fits.py) at E6a's completion rate. If E6a is incomplete, E6b exits with
       code 2. If sigma* would lie outside the E5b sigma range, E6b does not extrapolate: it writes the
       record with status "out_of_range" and exits with code 4 (no runs). Record: data/derived/sigma_star.json.
  E6p  published-reproduction (all flags default), C3 with the published ORCA, seeds 428-477 (50).
Noise: per-step Gaussian velocity noise (published scheme), seeded by the run seed (as E5).
Output: data/E6/e6a.jsonl, e6b.jsonl, e6p.jsonl (job_id "<variant>|seed<seed>"), resumable.
Usage: e6.py E6a | E6b | E6p  [qargs options; E6b also --e6a PATH --sigma-star PATH for smoke tests]
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
from e1lib import CF, DATA, DERIVED, load_runs, run_jobs  # noqa: E402
from runlib import whole_run  # noqa: E402
from w2lib import wilson  # noqa: E402
import fits  # noqa: E402
import qargs  # noqa: E402

E5B = os.path.join(DATA, "E5", "e5b.jsonl")
SIGMA_STAR = os.path.join(DERIVED, "sigma_star.json")
SEEDS = {"E6a": range(242, 428), "E6b": range(242, 428), "E6p": range(428, 478)}


def out_path(v):
    return os.path.join(DATA, "E6", f"{v.lower()}.jsonl")


def jobs(v, sigma=0.0):
    cfg, fl = {"E6a": ("C3", dict(CF)), "E6b": ("C1", dict(CF)), "E6p": ("C3", {})}[v]
    return [{"job_id": f"{v}|seed{s}", "variant": v, "seed": s, "width": 0.8, "flags": fl, "sigma": sigma,
             "t_max": 600.0, "config": cfg} for s in SEEDS[v]]


def sigma_star(e6a_path, e5b_path=E5B, path=SIGMA_STAR):
    """Returns (record, exit code). Code 0: sigma* set; 2: E6a incomplete; 4: out of the E5b range."""
    want = {j["job_id"] for j in jobs("E6a")}
    R = [r for r in load_runs(e6a_path) if r["job_id"] in want] if os.path.exists(e6a_path) else []
    if len({r["job_id"] for r in R}) < len(want):
        return {"status": "E6a incomplete", "n": len(R)}, 2
    k = sum(bool(r["complete"]) for r in R)
    n = len(R)
    p = k / n
    E = load_runs(e5b_path)
    sig = sorted({r["sigma"] for r in E})
    kk = [sum(bool(r["complete"]) for r in E if r["sigma"] == s) for s in sig]
    nn = [sum(1 for r in E if r["sigma"] == s) for s in sig]
    f = fits.fit_logit(sig, kk, nn)
    rec = {"script": "experiments/E6/e6.py", "made": datetime.datetime.now().isoformat(timespec="seconds"),
           "E6a": {"file": os.path.relpath(e6a_path, os.path.dirname(DATA)), "k": k, "n": n, "rate": p,
                   "wilson95": list(wilson(k, n))[1:]},
           "E5b": {"file": os.path.relpath(e5b_path, os.path.dirname(DATA)), "sigma": sig, "k": kk, "n": nn},
           "fit": f, "model": "P(complete) = 1 / (1 + exp(-(a + b sigma)))",
           "range_rule": "sigma* must lie within the E5b sigma range [%g, %g] m/s (no extrapolation)" % (sig[0], sig[-1])}
    if k in (0, n):
        rec.update(status="out_of_range", reason="E6a completion rate is %d/%d" % (k, n))
        return rec, 4
    inv = fits.invert(f, p, n_p=n)
    rec["inversion"] = inv
    if not sig[0] <= inv["x_star"] <= sig[-1]:
        rec.update(status="out_of_range", reason="sigma* = %.4f m/s outside [%g, %g]" % (inv["x_star"], sig[0], sig[-1]))
        return rec, 4
    rec.update(status="ok", sigma_star=round(inv["x_star"], 4),
               note="sigma_star (rounded to 1e-4 m/s) is the value used by E6b and E10")
    return rec, 0


def main(argv=None):
    a = qargs.parse(argv)
    v = a.rest[0]
    out = a.out or out_path(v)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sigma = 0.0
    if v == "E6b":
        e6a = a.rest[a.rest.index("--e6a") + 1] if "--e6a" in a.rest else out_path("E6a")
        sp = a.rest[a.rest.index("--sigma-star") + 1] if "--sigma-star" in a.rest else SIGMA_STAR
        if os.path.exists(sp) and json.load(open(sp)).get("status") == "ok":
            rec = json.load(open(sp))          # resume: sigma* is fixed once set
        else:
            rec, code = sigma_star(e6a)
            if code == 2:
                print("E6b: E6a incomplete", rec, flush=True)
                sys.exit(2)
            os.makedirs(os.path.dirname(sp), exist_ok=True)
            json.dump(rec, open(sp, "w"), indent=1, default=float)
            if code:
                print("E6b stopped:", rec["reason"], flush=True)
                sys.exit(code)
        sigma = rec["sigma_star"]
        print("E6b sigma* =", sigma, flush=True)
    J = qargs.select(jobs(v, sigma), a)
    return run_jobs(J, whole_run, out, workers=a.workers, log_every=10)


if __name__ == "__main__":
    print("wall", main())
