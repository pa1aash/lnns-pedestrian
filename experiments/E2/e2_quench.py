"""E2: lone-trap quench on the E2 snapshots (data/derived/selection.json, corrected-forward E1b).

Every arm runs from the frozen deadlock snapshot with the full flag set CF union arm flags, C1-C3,
dt = 0.01 s, window 120 s (pattern: experiments/pilot/w22_quench.py). Deterministic arms stop early
once stationary (every active |v| < 1e-3 m/s for 10 s, no exit; StationaryDetector(hold=10,
v_thr=1e-3)) and are censored at 120 s; noise arms run the full window.
Deterministic arms: each once unperturbed and 5 times with 1e-9 m Gaussian position perturbations
of every residual agent (numpy default_rng seeds 900-904).
Noise arms: C1 + sigma in {0.03, 0.05, 0.07} m/s x 5 noise seeds (7000 + 100 k + rep, k = snapshot
index in selection order; the same seeds at every sigma).
Recorded: per-agent exit times, first agent out and its time, stationary stop, final positions.
Primary outcome (C15): "blocker freed within 120 s", blocker = residual agent nearest (10, 5) (the
keystone-test blocker, carried in selection.json); recorded alongside per-agent exits and all-freed.
Snapshots: 60 (C15), the 34 lone-keystone snapshots first (job_ids and seeds as in batch 2A), then 26
from the lone-keystone-with-second-trap class; the class is the stratum in the summary.
Output: data/E2/e2_quench.jsonl (job_id "<tag>|<arm>|<rep>"), resumable;
        data/E2/e2_summary.json (blocker-freed, all-freed and exit fractions per stratum and arm, Wilson
        95% intervals; rows from before C15 get the blocker from selection.json).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, ROOT, load_runs, run_jobs  # noqa: E402
from runlib import quench  # noqa: E402
from w2lib import wilson  # noqa: E402

OUT = os.path.join(DATA, "E2", "e2_quench.jsonl")
SUMMARY = os.path.join(DATA, "E2", "e2_summary.json")
DET_ARMS = {
    "C1": ("C1", {}),
    "C2": ("C2", {}),
    "C3_pub": ("C3", {"w2_orca": "published"}),
    "C3_rvo2": ("C3", {"w2_orca": "rvo2"}),
    "drive_only": ("C3", {"w2_orca_split": "drive_only"}),
    "constraint_only_pub": ("C3", {"w2_orca": "published", "w2_orca_split": "constraint_only"}),
    "constraint_only_rvo2": ("C3", {"w2_orca": "rvo2", "w2_orca_split": "constraint_only"}),
    "frozen_plus": ("C3", {"w2_orca_split": "frozen_mean"}),
    "frozen_minus": ("C3", {"w2_orca_split": "frozen_mean", "w2_orca_transform": "reverse_parallel"}),
}
for _b in (0.05, 0.1, 0.2, 0.5):
    DET_ARMS[f"bias{_b}"] = ("C1", {"w2_noise": "lateral_bias", "w2_bias_b": _b})
PERTURB_SEEDS = (900, 901, 902, 903, 904)
SIGMAS = (0.03, 0.05, 0.07)
N_NOISE = 5
T_Q = 120.0


def snapshots():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    return [(s["tag"], os.path.join(ROOT, s["snap"]), s["blocker"], s["class"]) for s in sel["E2"]["snapshots"]]


def jobs():
    J = []
    for k, (tag, snap, blk, cls) in enumerate(snapshots()):
        for arm, (cfg, fl) in DET_ARMS.items():
            for rep, ps in enumerate((None,) + PERTURB_SEEDS):
                J.append({"job_id": f"{tag}|{arm}|{'u' if ps is None else ps}", "snap": snap, "arm": arm,
                          "config": cfg, "flags": {**CF, **fl}, "deterministic": True, "perturb": ps,
                          "t_q": T_Q, "blocker": blk, "stratum": cls})
        for sg in SIGMAS:
            for rep in range(N_NOISE):
                J.append({"job_id": f"{tag}|noise{sg}|{rep}", "snap": snap, "arm": f"noise{sg}", "config": "C1",
                          "flags": dict(CF), "sigma": sg, "noise_seed": 7000 + 100 * k + rep, "rep": rep,
                          "deterministic": False, "t_q": T_Q,
                          "blocker": blk, "stratum": cls})
    return J


def quench_e2(job):
    r = quench(job)
    t = r["exits"].get(job["blocker"])
    r["blocker_freed"] = t is not None and t <= T_Q + 1e-9
    r["blocker_exit_t"] = t
    return r


def summary(out=OUT, path=SUMMARY):
    sel = {s["tag"]: s for s in json.load(open(os.path.join(DATA, "derived", "selection.json")))["E2"]["snapshots"]}
    cells = {}
    for r in load_runs(out):
        tag = r["job_id"].split("|")[0]
        if tag not in sel:
            continue
        s = sel[tag]
        t = r["exits"].get(str(s["blocker"]))
        c = cells.setdefault((s["class"], r["arm"]), {"n": 0, "blocker_freed": 0, "all_freed": 0, "exit_frac": [],
                                                       "snaps": set()})
        c["n"] += 1
        c["blocker_freed"] += int(t is not None and t <= T_Q + 1e-9)
        c["all_freed"] += int(r["all_freed"])
        c["exit_frac"].append(r["n_freed"] / len(r["residual"]))
        c["snaps"].add(tag)
    res = []
    for (cls, arm), c in sorted(cells.items()):
        p, lo, hi = wilson(c["blocker_freed"], c["n"])
        res.append({"stratum": cls, "arm": arm, "n_runs": c["n"], "n_snapshots": len(c["snaps"]),
                    "blocker_freed": c["blocker_freed"], "blocker_freed_rate": p, "ci95": [lo, hi],
                    "all_freed": c["all_freed"], "mean_exit_fraction": sum(c["exit_frac"]) / c["n"]})
    json.dump({"script": "experiments/E2/e2_quench.py", "primary": "blocker freed within 120 s",
               "cells": res}, open(path, "w"), indent=1, default=float)
    return res


def main(out=OUT, J=None, workers=4):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    wall = run_jobs(jobs() if J is None else J, quench_e2, out, workers=workers, log_every=50)
    if out == OUT:
        summary()
    return wall


if __name__ == "__main__":
    print("wall", main())
