"""E4: escape statistics on the E4 snapshots (data/derived/selection.json; read when the step starts).

Conditions (as experiments/pilot/w23_escape.py): full (all residual agents mobile, noise on all);
frozen (other residual agents present but reset to their snapshot positions with zero velocity every
step: static obstacles); alone (other residual agents deactivated).
Barriers per condition (C15) are the string-method barriers of experiments/BAR/bar.py (the port of
experiments/pilot/w23_barrier.py): full = all_mobile.dU_climb, frozen = frozen.dU_climb (blocker mobile,
neighbours pinned), alone = alone.dU_climb (others removed, density 0), with the 1-D on-axis integral
dU_1d_axis_alone stored as the check. Noise per (snapshot, condition): three sigma giving
dU_cond / k_B T_eff in {1.5, 2.5, 3.5} at dt = 0.01 s with the blocker's tau (T3, experiments/lib/teff.py),
C1, corrected-forward flags (CF). Censored at 300 s, 900 s at the 3.5 level.
A (snapshot, condition) with dU_cond < 0.1 J has no barrier to set a temperature from and is skipped
(listed in data/E4/e4_extension.json).
Escape = the blocker's centre crossing x >= 10. Noise seeds 11000 + 1000 k + 100 * level + rep
(level 0, 1, 2 for 1.5, 2.5, 3.5).
Restarts: 20 per (snapshot, condition, level). Extension: a condition with fewer than 105 escapes in
total (all snapshots and levels) is extended to 40 and then 60 restarts; target and reached counts are
written to data/E4/e4_extension.json.
Output: data/E4/e4_escape.jsonl (job_id "<tag>|<cond>|b<level>|<rep>"), resumable.
"""
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, ROOT, load_runs, run_jobs  # noqa: E402
from runlib import escape  # noqa: E402
from teff import M, sigma_for  # noqa: E402

OUT = os.path.join(DATA, "E4", "e4_escape.jsonl")
EXT = os.path.join(DATA, "E4", "e4_extension.json")
BARRIERS = os.path.join(DATA, "BAR", "barriers.json")
CONDS = ("full", "frozen", "alone")
BAR_KEY = {"full": "all_mobile", "frozen": "frozen", "alone": "alone"}
BETAS = (1.5, 2.5, 3.5)
N0, N_MAX, STEP, TARGET, DT_REF, DU_FLOOR = 20, 60, 20, 105, 0.01, 0.1
T_CENS = {1.5: 300.0, 2.5: 300.0, 3.5: 900.0}


def barriers(row):
    return {c: float(row[BAR_KEY[c]]["dU_climb"]) for c in CONDS}


def snapshots(bar_path=BARRIERS):
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    if "E4" not in sel or not os.path.exists(bar_path):
        return None
    bar = {b["job_id"]: b for b in json.load(open(bar_path))["barriers"]}
    S = []
    for s in sel["E4"]["snapshots"]:
        path = os.path.join(ROOT, s["snap"])
        tau_b = float(pickle.load(open(path, "rb"))["state"].taus[s["blocker"]])
        b = bar[s["tag"]]
        S.append({"tag": s["tag"], "snap": path, "blocker": s["blocker"], "tau_b": tau_b, "dU": barriers(b),
                  "dU_1d_alone": b["dU_1d_axis_alone"], "dU_collective": s["dU"]})
    return S


def make_jobs(nrep, S=None):
    S = snapshots() if S is None else S
    if S is None:
        return None
    J = []
    for k, s in enumerate(S):
        for cond in CONDS:
            dU = s["dU"][cond]
            if dU < DU_FLOOR:
                continue
            for lv, beta in enumerate(BETAS):
                sg = sigma_for(dU / beta, DT_REF, s["tau_b"])
                for rep in range(nrep[cond]):
                    J.append({"job_id": f"{s['tag']}|{cond}|b{beta}|{rep}", "snap": s["snap"], "blocker": s["blocker"],
                              "cond": cond, "config": "C1", "flags": dict(CF), "sigma": sg, "rep": rep,
                              "beta_ref": beta, "dU_cond": dU, "tau_b": s["tau_b"], "m": M, "kT_eff": dU / beta,
                              "dU_1d_alone": s["dU_1d_alone"], "dU_collective": s["dU_collective"],
                              "t_cens": T_CENS[beta], "noise_seed": 11000 + 1000 * k + 100 * lv + rep})
    return J


def skipped(S):
    return [{"tag": s["tag"], "cond": c, "dU": s["dU"][c]} for s in S for c in CONDS if s["dU"][c] < DU_FLOOR]


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


def main(out=OUT, ext=EXT, workers=4, n0=N0, n_max=N_MAX, step=STEP, S=None):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    S = snapshots() if S is None else S
    nrep = {c: n0 for c in CONDS}
    if ext and os.path.exists(ext):
        nrep = json.load(open(ext))["n_restarts"]
    wall = 0.0
    while True:
        wall += run_jobs(make_jobs(nrep, S), escape, out, workers=workers, log_every=100)
        ev = events(out)
        grow = [c for c in CONDS if ev[c] < TARGET and nrep[c] < n_max]
        rec = {"target_events": TARGET, "n_restarts": nrep, "events": ev, "max_restarts": n_max,
               "skipped_no_barrier": skipped(S)}
        if ext:
            json.dump(rec, open(ext, "w"), indent=1)
        print("E4 events", ev, "restarts", nrep, flush=True)
        if not grow:
            return wall
        for c in grow:
            nrep[c] = min(nrep[c] + step, n_max)


if __name__ == "__main__":
    print("wall", main())
