"""E4: escape statistics on the E4 snapshots (data/derived/selection.json; read when the step starts).

Conditions (as experiments/pilot/w23_escape.py): full (all residual agents mobile, noise on all);
frozen (other residual agents present but reset to their snapshot positions with zero velocity every
step: static obstacles); alone (other residual agents deactivated). Corrected-forward flags (CF),
C1 + sigma in {0.04, 0.05, 0.07} m/s (the pilot's sigma set), dt = 0.01 s, censored at 300 s.
Escape = the blocker's centre crossing x >= 10. Noise seeds 11000 + 1000 k + 100 * round(100 sigma) + rep.
Restarts: 20 per (snapshot, condition, sigma). Extension: a condition with fewer than 105 escapes in
total (all snapshots and sigmas) is extended to 40 and then 60 restarts; target and reached counts are
written to data/E4/e4_extension.json.
Output: data/E4/e4_escape.jsonl (job_id "<tag>|<cond>|s<sigma>|<rep>"), resumable.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, ROOT, load_runs, run_jobs  # noqa: E402
from runlib import escape  # noqa: E402

OUT = os.path.join(DATA, "E4", "e4_escape.jsonl")
EXT = os.path.join(DATA, "E4", "e4_extension.json")
CONDS = ("full", "frozen", "alone")
SIGMAS = (0.04, 0.05, 0.07)
N0, N_MAX, STEP, TARGET, T_CENS = 20, 60, 20, 105, 300.0


def snapshots():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    if "E4" not in sel:
        return None
    return [(s["tag"], os.path.join(ROOT, s["snap"]), s["blocker"]) for s in sel["E4"]["snapshots"]]


def make_jobs(nrep):
    S = snapshots()
    if S is None:
        return None
    J = []
    for k, (tag, snap, b) in enumerate(S):
        for cond in CONDS:
            for sg in SIGMAS:
                for rep in range(nrep[cond]):
                    J.append({"job_id": f"{tag}|{cond}|s{sg}|{rep}", "snap": snap, "blocker": b, "cond": cond,
                              "config": "C1", "flags": dict(CF), "sigma": sg, "rep": rep, "t_cens": T_CENS,
                              "noise_seed": 11000 + 1000 * k + 100 * int(round(100 * sg)) + rep})
    return J


def current_nrep():
    if os.path.exists(EXT):
        return json.load(open(EXT))["n_restarts"]
    return {c: N0 for c in CONDS}


def jobs():
    return make_jobs(current_nrep())


def events(out):
    ev = {c: 0 for c in CONDS}
    if os.path.exists(out):
        for r in load_runs(out):
            if not r["censored"]:
                ev[r["cond"]] += 1
    return ev


def main(out=OUT, workers=4, n0=N0, n_max=N_MAX, step=STEP):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    nrep = {c: n0 for c in CONDS}
    if out == OUT and os.path.exists(EXT):
        nrep = json.load(open(EXT))["n_restarts"]
    wall = 0.0
    while True:
        wall += run_jobs(make_jobs(nrep), escape, out, workers=workers, log_every=100)
        ev = events(out)
        grow = [c for c in CONDS if ev[c] < TARGET and nrep[c] < n_max]
        rec = {"target_events": TARGET, "n_restarts": nrep, "events": ev, "max_restarts": n_max}
        if out == OUT:
            json.dump(rec, open(EXT, "w"), indent=1)
        print("E4 events", ev, "restarts", nrep, flush=True)
        if not grow:
            return wall
        for c in grow:
            nrep[c] = min(nrep[c] + step, n_max)


if __name__ == "__main__":
    print("wall", main())
