"""E7b_quench: pair-class quench on the E7b pair library (experiments/E7b/e7b_pairs.py).

Every arm restarts the frozen pair snapshot with the full flag set CF union {B_w: 0.04} union arm flags,
dt = 0.01 s, window 120 s (pattern of experiments/E2/e2_quench.py and experiments/pilot/a4_quench.py).
Deterministic arms stop early once stationary (every active |v| < 1e-3 m/s for 10 s, no exit; as E2)
and are censored at 120 s; noise arms run the full window (or until both members are out).
Deterministic arms, each run once unperturbed and 5 times with 1e-9 m Gaussian position perturbations of
both members (numpy default_rng seeds 900-904, as E2):
  C1, C2, C3_pub, C3_rvo2, drive_only, constraint_only_pub, constraint_only_rvo2, frozen_plus,
  frozen_minus; C1 + lateral bias b in {+-0.01, +-0.02, +-0.03, 0.05, 0.1} (b > 0 tilts toward +y);
  C1 + common lateral displacement delta in {1e-3, 1e-2, 3e-2} m: both members shifted by +delta in y
  at the restart (applied before the 1e-9 m perturbation).
Noise arms: C1 + per-step velocity noise sigma in {0.01, 0.02, 0.03, 0.05} m/s x 5 noise seeds
(20000 + 100 k + rep, k = snapshot index in library order; the same seeds at every sigma).
Recorded per run: exit time of each member, which member exits first and its side (lower / upper: the
member's y at the snapshot relative to the door axis y = 5), the y at which each member's centre first
reaches the door plane x = 10, stationary stop, final positions.
Output: data/E7b/e7b_quench.jsonl (job_id "<tag>|<arm>|<rep>"), resumable.
"""
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
sys.path.insert(0, HERE)
from e1lib import CF, DATA, run_jobs  # noqa: E402
from w2lib import StationaryDetector, restore  # noqa: E402
import numpy as np  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402

OUT = os.path.join(DATA, "E7b", "e7b_quench.jsonl")
BASE = {**CF, "B_w": 0.04}
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
for _b in (-0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.05, 0.1):
    DET_ARMS[f"bias{_b:g}"] = ("C1", {"w2_noise": "lateral_bias", "w2_bias_b": _b})
DELTAS = (1e-3, 1e-2, 3e-2)
PERTURB_SEEDS = (900, 901, 902, 903, 904)
SIGMAS = (0.01, 0.02, 0.03, 0.05)
N_NOISE = 5
T_Q = 120.0


def run(job):
    snap = pickle.load(open(job["snap"], "rb"))
    sim = restore(snap, job["config"], flags=dict(job["flags"]), noise=job.get("sigma", 0.0),
                  noise_seed=job.get("noise_seed"))
    st = sim.state
    ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
    side = {i: ("lower" if st.positions[i, 1] < 5.0 else "upper") for i in ids}
    if job.get("delta"):
        st.positions[ids, 1] += job["delta"]
    if job.get("perturb") is not None:
        rng = np.random.default_rng(job["perturb"])
        st.positions[ids] += rng.normal(0, 1e-9, (len(ids), 2))
    t0, w0 = sim.time, time.perf_counter()
    exits, cross_y = {}, {}
    det = StationaryDetector(hold=10.0, v_thr=1e-3) if job["deterministic"] else None
    stationary = False
    for _ in range(int(round(job["t_q"] / sim.params["dt"]))):
        prev = st.active.copy()
        sim.step()
        st = sim.state
        for i in ids:
            if i not in cross_y and st.active[i] and st.positions[i, 0] >= 10.0:
                cross_y[i] = float(st.positions[i, 1])
        for i in np.where(prev & ~st.active)[0]:
            exits[int(i)] = sim.time - t0
        if st.n_active == 0:
            break
        if det is not None and det.update(sim):
            stationary = True
            break
    first = min(exits, key=exits.get) if exits else None
    out = {k: v for k, v in job.items() if k != "snap"}
    out.update({"snap": os.path.basename(job["snap"]), "members": ids, "side": side, "exits": exits,
                "n_freed": len(exits), "all_freed": len(exits) == len(ids), "freed": bool(exits),
                "first_agent": first, "first_side": side.get(first), "first_t": exits.get(first),
                "cross_y": cross_y, "stationary_stop": stationary, "t_run": sim.time - t0,
                "dt": sim.params["dt"], "wall_s": time.perf_counter() - w0,
                "final_pos": {int(i): st.positions[i].tolist() for i in ids if st.active[i]}})
    return out


def jobs():
    J = []
    for k, p in enumerate(pairs()):
        tag, snap = p["tag"], p["snap"]
        det = [(a, c, f, None) for a, (c, f) in DET_ARMS.items()] + \
              [(f"delta{d:g}", "C1", {}, d) for d in DELTAS]
        for arm, cfg, fl, d in det:
            for ps in (None,) + PERTURB_SEEDS:
                J.append({"job_id": f"{tag}|{arm}|{'u' if ps is None else ps}", "snap": snap, "arm": arm,
                          "config": cfg, "flags": {**BASE, **fl}, "deterministic": True, "perturb": ps,
                          "delta": d, "t_q": T_Q})
        for sg in SIGMAS:
            for rep in range(N_NOISE):
                J.append({"job_id": f"{tag}|noise{sg}|{rep}", "snap": snap, "arm": f"noise{sg}", "config": "C1",
                          "flags": dict(BASE), "sigma": sg, "noise_seed": 20000 + 100 * k + rep, "rep": rep,
                          "deterministic": False, "t_q": T_Q})
    return J


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    J = qargs.select(jobs(), a)
    return run_jobs(J, run, out, workers=a.workers, log_every=100)


if __name__ == "__main__":
    print("wall", main())
