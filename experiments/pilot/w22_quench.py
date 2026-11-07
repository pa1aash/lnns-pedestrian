"""W2.2 common-library quench. Each arm is switched on at a frozen W2.1 deadlock
snapshot (C1, w=0.8, published flags); run up to 120 s; record each residual agent's
exit time. Deterministic arms stop early once the state is stationary
(all |v| < 1e-3 m/s for 10 s, no exit) and are then censored at 120 s.
Output: wave2/data/w22_quench.jsonl
"""
import glob, os, pickle, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from w2lib import DATA, LIB, StationaryDetector, restore, run_jobs

T_Q = 120.0
ARMS = {
    "C1": ("C1", {}), "C2": ("C2", {}),
    "C3_pub": ("C3", {}), "C3_rvo2": ("C3", {"w2_orca": "rvo2"}),
    "drive_only": ("C3", {"w2_orca_split": "drive_only"}),
    "constraint_only": ("C3", {"w2_orca_split": "constraint_only"}),
    "C3_rev_par": ("C3", {"w2_orca_transform": "reverse_parallel"}),
    "C3_rev_lat": ("C3", {"w2_orca_transform": "reverse_lateral"}),
    "frozen_plus": ("C3", {"w2_orca_split": "frozen_mean"}),
    "frozen_minus": ("C3", {"w2_orca_split": "frozen_mean", "w2_orca_transform": "reverse_parallel"}),
}
NOISE = (0.03, 0.05, 0.07)
BIAS = (0.05, 0.1, 0.2, 0.3, 0.5)


def run(job):
    snap = pickle.load(open(job["snap"], "rb"))
    cfg, flags = job["config"], dict(job.get("flags", {}))
    sim = restore(snap, cfg, flags=flags, noise=job.get("sigma", 0.0),
                  noise_seed=job.get("noise_seed"))
    st = sim.state
    if job.get("perturb"):
        rng = np.random.default_rng(job["perturb"])
        a = st.active_indices
        st.positions[a] += rng.normal(0, 1e-9, (len(a), 2))
    resid = [int(i) for i in st.active_indices]
    t0 = sim.time
    w0 = time.perf_counter()
    exits = {}
    det = StationaryDetector(hold=10.0, v_thr=1e-3) if job.get("deterministic") else None
    stationary = False
    nsteps = int(round(T_Q / sim.params["dt"]))
    for _ in range(nsteps):
        prev = st.active.copy()
        sim.step()
        st = sim.state
        for i in np.where(prev & ~st.active)[0]:
            exits[int(i)] = sim.time - t0
        if st.n_active == 0:
            break
        if det is not None and det.update(sim):
            stationary = True
            break
    first = min(exits, key=exits.get) if exits else None
    out = {k: v for k, v in job.items() if k != "snap"}
    out.update({"snap": os.path.basename(job["snap"]), "residual": resid, "exits": exits,
                "n_freed": len(exits), "all_freed": len(exits) == len(resid),
                "first_agent": first, "first_t": exits.get(first) if first is not None else None,
                "stationary_stop": stationary, "t_run": sim.time - t0,
                "dt": sim.params["dt"], "wall_s": time.perf_counter() - w0,
                "final_pos": {int(i): st.positions[i].tolist() for i in resid if st.active[i]}})
    return out


def make_jobs(snaps):
    jobs = []
    for k, s in enumerate(snaps):
        tag = os.path.basename(s)[:-4]
        for arm, (cfg, fl) in ARMS.items():
            jobs.append({"job_id": f"{tag}|{arm}", "snap": s, "arm": arm, "config": cfg,
                         "flags": fl, "deterministic": True})
        for sg in NOISE:
            for rep in range(3):
                jobs.append({"job_id": f"{tag}|noise{sg}|{rep}", "snap": s, "arm": f"noise{sg}",
                             "config": "C1", "sigma": sg, "noise_seed": 7000 + 100 * k + rep,
                             "rep": rep})
        if k < 10:
            for b in BIAS:
                jobs.append({"job_id": f"{tag}|bias{b}", "snap": s, "arm": f"bias{b}", "config": "C1",
                             "flags": {"w2_noise": "lateral_bias", "w2_bias_b": b},
                             "deterministic": True})
            for rep in range(3):
                jobs.append({"job_id": f"{tag}|C3_perturb|{rep}", "snap": s, "arm": "C3_perturb",
                             "config": "C3", "perturb": 900 + rep, "rep": rep, "deterministic": True})
    return jobs


if __name__ == "__main__":
    sel = os.path.join(DATA, "w22_selected_snaps.txt")
    snaps = [l.strip() for l in open(sel) if l.strip()]
    jobs = make_jobs(snaps)
    wall = run_jobs(jobs, run, os.path.join(DATA, "w22_quench.jsonl"), workers=4, log_every=25)
    print("wall", wall)
