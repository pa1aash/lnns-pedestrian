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
Output: data/E2/e2_quench.jsonl (job_id "<tag>|<arm>|<rep>"), resumable.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, ROOT, run_jobs  # noqa: E402
from runlib import quench  # noqa: E402

OUT = os.path.join(DATA, "E2", "e2_quench.jsonl")
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
    return [(s["tag"], os.path.join(ROOT, s["snap"])) for s in sel["E2"]["snapshots"]]


def jobs():
    J = []
    for k, (tag, snap) in enumerate(snapshots()):
        for arm, (cfg, fl) in DET_ARMS.items():
            for rep, ps in enumerate((None,) + PERTURB_SEEDS):
                J.append({"job_id": f"{tag}|{arm}|{'u' if ps is None else ps}", "snap": snap, "arm": arm,
                          "config": cfg, "flags": {**CF, **fl}, "deterministic": True, "perturb": ps,
                          "t_q": T_Q})
        for sg in SIGMAS:
            for rep in range(N_NOISE):
                J.append({"job_id": f"{tag}|noise{sg}|{rep}", "snap": snap, "arm": f"noise{sg}", "config": "C1",
                          "flags": dict(CF), "sigma": sg, "noise_seed": 7000 + 100 * k + rep, "rep": rep,
                          "deterministic": False, "t_q": T_Q})
    return J


def main(out=OUT, J=None, workers=4):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(jobs() if J is None else J, quench, out, workers=workers, log_every=50)


if __name__ == "__main__":
    print("wall", main())
