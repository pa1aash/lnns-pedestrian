"""T4 runs: CroMa time-step check of the four Sect. 7 variants.

Run set: experiments/revision/D3_croma_rerun.py jobs (cells C1_cf, C1_cf_edge = CF + B_w_edge 0.04,
C3_rvo2_cf = force-coupled ORCA with the RVO2 solver, C1_cf_sig = CF + per-step velocity noise sigma* = 0.0467 m/s;
seeds 42-51 = two runs per human run (run type RUNS[(seed - 42) % 5]); the full 25 per variant at both time steps
would cost about 17 CPU-h (11.4 at dt = 0.005 s incl. the overlap record, 5.7 at dt = 0.01 s), above the 12 CPU-h
limit of the request, so 10 per variant are run and compared with the same 10 seeds at dt = 0.01 s; passed-participant N, L = 2.0 / 0.2 m, 600 s cap, deadlock stop as E10),
at two time steps:
  dt0.005  the 100 runs at dt = 0.005 s (same spawns and noise seeds; sigma* per step unchanged);
  dt0.01   the same 100 runs at dt = 0.01 s, a reproduction of data/revision/D3/d3_croma.jsonl (t_end, completion and
           passage times must agree) that adds the overlap record.
The run function is E10's run() (experiments/E10/e10_croma.py) with two additions: trajectories are sampled every
round(0.04 / dt) steps (25 Hz at both dt; E10 samples every 4 steps of dt = 0.01 s, the rate the estimator
w28_croma.sim assumes), and after every step the largest agent-agent overlap max_{i<j} (r_i + r_j - d_ij) and wall
overlap (experiments/revision2/A12_overlap.overlaps) are recorded, with the time, pair and radii of the maximum, the
maximum over t >= 1 s (spawn transient left out), and the step counts with overlap > 1 cm and > 5 cm.
Output: data/revision4/T4/t4_croma.jsonl (job_id "<dtkey>|<cell>|seed<seed>"), trajectories data/revision4/T4/raw/.
Usage: T4_croma_dt.py [--workers W] [--only dt0.005|dt0.01]
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import ROOT, np, run_jobs  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments", "revision2"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "revision"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "E10"))
import D3_croma_rerun as D3  # noqa: E402
import e10_croma as E10  # noqa: E402
from A12_overlap import overlaps  # noqa: E402
from w2lib import Simulation, StationaryDetector  # noqa: E402
from sim.scenarios.croma import CromaBottleneckScenario  # noqa: E402

OUTDIR = rev4lib.data_dir("T4")
OUT = os.path.join(OUTDIR, "t4_croma.jsonl")
RAW = os.path.join(OUTDIR, "raw")
DTS = {"dt0.005": 0.005, "dt0.01": 0.01}
SEEDS = range(42, 52)
T_LATE = 1.0


def run(job):
    w0, c0 = time.perf_counter(), time.process_time()
    sc = CromaBottleneckScenario(job["N"], 0.8, job["L"])
    sim = Simulation.from_scenario(sc, job["config"], seed=job["seed"],
                                   param_overrides={**job["flags"], "w2_metrics": "light", "dt": job["dt"]})
    sim.velocity_noise_std = job.get("sigma", 0.0)
    stride = int(round(0.04 / job["dt"]))
    det = StationaryDetector()
    traj, deadlock = [], False
    best = {"ov": -np.inf}
    best_late = -np.inf
    max_wall, n1, n5, nsteps = -np.inf, 0, 0, 0
    st = sim.state
    while sim.time < job["t_max"] - 1e-9 and st.n_active > 0:
        sim.step()
        st = sim.state
        nsteps += 1
        if sim.step_count % stride == 0:
            for i in np.where(st.active & (st.positions[:, 0] > 6.5))[0]:
                traj.append((sim.time, i, st.positions[i, 0], st.positions[i, 1]))
        oa, ow, pair = overlaps(sim)
        max_wall = max(max_wall, ow)
        n1 += oa > 0.01
        n5 += oa > 0.05
        if oa > best["ov"]:
            best = {"ov": float(oa), "t": sim.time, "pair": pair, "radii": [float(st.radii[i]) for i in pair],
                    "masses": [float(st.masses[i]) for i in pair], "n_active": int(st.n_active)}
        if sim.time >= T_LATE - 1e-9:
            best_late = max(best_late, oa)
        if det.update(sim):
            deadlock = True
            break
    os.makedirs(job["raw_dir"], exist_ok=True)
    p = os.path.join(job["raw_dir"], f"{job['dtkey']}_{job['cell']}_seed{job['seed']}.npz")
    np.savez_compressed(p, data=np.array(traj, float).reshape(-1, 4))
    est = E10.w28.sim(p) if len(traj) else {"n_pass": 0}
    out = {k: v for k, v in job.items() if k != "raw_dir"}
    out.update({"dt": sim.params["dt"], "t_end": sim.time, "complete": st.n_active == 0, "deadlock": deadlock,
                "n_remaining": int(st.n_active), "n_leaked": len(sim.leaked), "leaked": sorted(sim.leaked),
                "r1_used": sc.r1_used, "npz": os.path.relpath(p, ROOT), "estimator": est, "sample_stride": stride,
                "n_steps": nsteps, "max_agent_overlap_m": best["ov"], "max_agent": best,
                "max_agent_overlap_late_m": float(best_late), "max_wall_overlap_m": float(max_wall),
                "steps_ov_gt1cm": int(n1), "steps_ov_gt5cm": int(n5),
                "cpu_s": time.process_time() - c0, "wall_s": time.perf_counter() - w0})
    return out


def jobs(only=None):
    J = []
    for dk, dt in DTS.items():
        if only and dk != only:
            continue
        for j in D3.jobs(RAW):
            if j["seed"] not in SEEDS:
                continue
            J.append({**j, "job_id": f"{dk}|{j['job_id']}", "dtkey": dk, "dt": dt})
    return J


if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    print("wall", run_jobs(jobs(only), run, OUT, workers=rev4lib.workers(sys.argv), log_every=5))
