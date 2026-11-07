"""W2b A4: pair-class quench. Each arm is switched on at a frozen pair-deadlock snapshot
(C1, corrected-forward numerics, rejection spawn, w = 0.8, B_w = 0.04 all walls); up to 120 s;
records each residual agent's exit time (job code = wave2/scripts/w22_quench.run, which keeps
the snapshot's B_w / numerics flags: restore() drops w2_* and A_w/B_w from the snapshot params
and re-applies the arm flags, so every arm below re-adds CF + B_w = 0.04).
Deterministic arms stop once stationary (all |v| < 1e-3 m/s for 10 s, no exit), censored at 120 s.
Arms: C1, C2, C3_pub (orca=published), C3_rvo2, drive_only, constraint_only, frozen_plus,
frozen_minus; lateral_bias b in BIAS; C1 + noise sigma in {0.02, 0.03, 0.05} x 3 seeds;
C1 + 1e-9 m isotropic perturbation (3 seeds, first 10 snapshots);
C1 + deterministic lateral displacement of the lower agent toward the axis by delta in DELTA.
Snapshot list: wave2b/data/a4_selected_snaps.txt (pair snapshots, <= 30).
Output: wave2b/data/a4_quench.jsonl"""
import os, pickle, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2blib import *  # noqa
import w22_quench

BASEF = {"w2_numerics": "fixed", "B_w": 0.04}
ARMS = {
    "C1": ("C1", {}), "C2": ("C2", {}),
    "C3_pub": ("C3", {}), "C3_rvo2": ("C3", {"w2_orca": "rvo2"}),
    "drive_only": ("C3", {"w2_orca_split": "drive_only"}),
    "constraint_only": ("C3", {"w2_orca_split": "constraint_only"}),
    "frozen_plus": ("C3", {"w2_orca_split": "frozen_mean"}),
    "frozen_minus": ("C3", {"w2_orca_split": "frozen_mean", "w2_orca_transform": "reverse_parallel"}),
}
NOISE = (0.02, 0.03, 0.05)
BIAS = (0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5)
DELTA = (1e-6, 1e-3, 1e-2)


def run(job):
    if "delta" not in job:
        return w22_quench.run(job)
    # displacement arm: shift the lower-y residual agent toward the axis by delta, then C1
    snap = pickle.load(open(job["snap"], "rb"))
    st = snap["state"]
    a = st.active_indices
    lo = int(a[np.argmin(st.positions[a, 1])])
    st.positions[lo, 1] += job["delta"]
    tmp = job["snap"].replace(".pkl", f".d{job['delta']:g}.tmp.pkl")
    tmp = os.path.join(DATA2B, "tmp_" + os.path.basename(tmp))
    pickle.dump(snap, open(tmp, "wb"))
    j2 = dict(job); j2["snap"] = tmp
    out = w22_quench.run(j2)
    os.remove(tmp)
    out["snap"] = os.path.basename(job["snap"])
    out["displaced_agent"] = lo
    return out


def make_jobs(snaps):
    jobs = []
    for k, s in enumerate(snaps):
        tag = os.path.basename(s)[:-4]
        for arm, (cfg, fl) in ARMS.items():
            jobs.append({"job_id": f"{tag}|{arm}", "snap": s, "arm": arm, "config": cfg,
                         "flags": {**BASEF, **fl}, "deterministic": True})
        for b in BIAS:
            jobs.append({"job_id": f"{tag}|bias{b}", "snap": s, "arm": f"bias{b}", "config": "C1",
                         "flags": {**BASEF, "w2_noise": "lateral_bias", "w2_bias_b": b}, "deterministic": True})
        for sg in NOISE:
            for rep in range(3):
                jobs.append({"job_id": f"{tag}|noise{sg}|{rep}", "snap": s, "arm": f"noise{sg}", "config": "C1",
                             "flags": dict(BASEF), "sigma": sg, "noise_seed": 8000 + 100 * k + rep, "rep": rep})
        for d in DELTA:
            jobs.append({"job_id": f"{tag}|delta{d:g}", "snap": s, "arm": f"delta{d:g}", "config": "C1",
                         "flags": dict(BASEF), "delta": d, "deterministic": True})
        if k < 10:
            for rep in range(3):
                jobs.append({"job_id": f"{tag}|C1_perturb|{rep}", "snap": s, "arm": "C1_perturb", "config": "C1",
                             "flags": dict(BASEF), "perturb": 900 + rep, "rep": rep, "deterministic": True})
    return jobs


if __name__ == "__main__":
    snaps = [l.strip() for l in open(os.path.join(DATA2B, "a4_selected_snaps.txt")) if l.strip()]
    if len(sys.argv) > 1:
        snaps = snaps[: int(sys.argv[1])]
    jobs = make_jobs(snaps)
    print("wall", run_jobs(jobs, run, os.path.join(DATA2B, "a4_quench.jsonl"), workers=4, log_every=50))
