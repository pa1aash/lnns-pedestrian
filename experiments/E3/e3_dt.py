"""E3: time-step scaling on the E3 snapshots (data/derived/selection.json; read when the step starts).

Corrected-forward, all residual agents mobile (condition "full"), restart from the frozen snapshot with
CF union arm flags (pattern: experiments/pilot/w23_escape.py, kind "dtpilot" / "c3dt"):
  noise   C1 + sigma = 0.05 m/s, w2_noise in {per_step (default), dt_scaled (sigma sqrt(dt/0.01))},
          dt in {0.005, 0.01, 0.02} s, 20 restarts each (noise seeds
          51000 + 1000 k + 10 * round(1000 dt) + rep (+500 for dt_scaled)), censored at 300 s;
  C3_rvo2 deterministic, one run per dt, 300 s.
Escape (first-exit) time = the blocker's centre crossing the door plane x >= 10; the first exit of any
agent is recorded as well.
Output: data/E3/e3_dt.jsonl (job_id "<tag>|dt<dt>|<mode>|<rep>" / "<tag>|dt<dt>|C3_rvo2"), resumable.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, ROOT, run_jobs  # noqa: E402
from runlib import escape  # noqa: E402

OUT = os.path.join(DATA, "E3", "e3_dt.jsonl")
DTS = (0.005, 0.01, 0.02)
MODES = ("per_step", "dt_scaled")
N_REP, SIGMA, T_CENS = 20, 0.05, 300.0


def snapshots():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    if "E3" not in sel:
        return None
    return [(s["tag"], os.path.join(ROOT, s["snap"]), s["blocker"]) for s in sel["E3"]["snapshots"]]


def jobs():
    S = snapshots()
    if S is None:
        return None
    J = []
    for k, (tag, snap, b) in enumerate(S):
        for dtv in DTS:
            for mode in MODES:
                for rep in range(N_REP):
                    J.append({"job_id": f"{tag}|dt{dtv}|{mode}|{rep}", "snap": snap, "blocker": b, "cond": "full",
                              "config": "C1", "flags": {**CF, "w2_noise": mode}, "sigma": SIGMA, "dt": dtv,
                              "mode": mode, "rep": rep, "t_cens": T_CENS,
                              "noise_seed": 51000 + 1000 * k + 10 * int(round(1000 * dtv)) + rep
                              + (500 if mode == "dt_scaled" else 0)})
            J.append({"job_id": f"{tag}|dt{dtv}|C3_rvo2", "snap": snap, "blocker": b, "cond": "full",
                      "config": "C3", "flags": {**CF, "w2_orca": "rvo2"}, "sigma": 0.0, "dt": dtv,
                      "mode": "C3_rvo2", "t_cens": T_CENS})
    return J


def main(out=OUT, J=None, workers=4):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(jobs() if J is None else J, escape, out, workers=workers, log_every=50)


if __name__ == "__main__":
    print("wall", main())
