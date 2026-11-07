"""W2b B2: CroMa-geometry pilot (sim/scenarios/croma.py; geometry INFERRED in B1).
w = 0.8 m; N and corridor length matched to the five CroMa 0.8 m runs:
  (135, 2.0) 4D030 h0, (136, 2.0) 4D040 h1, (131, 0.21) 4D110 h0, (129, 0.21) 4D120 h1,
  (128, 0.21) 4D130 h2  -> one model run per CroMa run (n = 5 per cell), seeds 42-46.
Cells: pub = C1 published-reproduction flags; cf = C1 corrected-forward (numerics=fixed;
spawn is CroMa-rejection in every cell); cf_edge = cf + B_w_edge=0.04; c3 = C3 cf orca=rvo2.
No noise (sigma = 0) in any cell. c3 runs carry a 900 s wall-time cap (censored if hit). dt = 0.01 s; cap 600 s; stop at deadlock (all |v| < 0.01
m/s for 10 s, no exit). Trajectories (t, id, x, y) of agents with x > 6.5 every 4 steps
(25 Hz) -> wave2b/data/raw/b2_<cell>_<run>.npz. Output: wave2b/data/b2_croma.jsonl"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2blib import *  # noqa
from sim.scenarios.croma import CromaBottleneckScenario

RUNS = [("4D030", 135, 2.0), ("4D040", 136, 2.0), ("4D110", 131, 0.21), ("4D120", 129, 0.21),
        ("4D130", 128, 0.21)]
CELLS = {"pub": ("C1", {}), "cf": ("C1", {"w2_numerics": "fixed"}),
         "cf_edge": ("C1", {"w2_numerics": "fixed", "B_w_edge": 0.04}),
         # cf_edge was run before the corridor-wall tag fix (croma.py, commit after ae466a0):
         # its corridor-wall ends kept B = 0.08 at the door edge. cf_edge_fix is the corrected cell.
         "cf_edge_fix": ("C1", {"w2_numerics": "fixed", "B_w_edge": 0.04}),
         "c3": ("C3", {"w2_numerics": "fixed", "w2_orca": "rvo2"})}
RAW = os.path.join(DATA2B, "raw")
os.makedirs(RAW, exist_ok=True)
T_MAX = 600.0


def run(job):
    cfg, fl = CELLS[job["cell"]]
    sc = CromaBottleneckScenario(job["N"], 0.8, job["L"])
    sim = Simulation.from_scenario(sc, cfg, seed=job["seed"], param_overrides={**fl, "w2_metrics": "light"})
    w0 = time.perf_counter()
    det = StationaryDetector()
    traj, deadlock = [], False
    st = sim.state
    while sim.time < T_MAX - 1e-9 and st.n_active > 0:
        sim.step()
        st = sim.state
        if sim.step_count % 4 == 0:
            a = np.where(st.active & (st.positions[:, 0] > 6.5))[0]
            for i in a:
                traj.append((sim.time, i, st.positions[i, 0], st.positions[i, 1]))
        if det.update(sim):
            deadlock = True
            break
        if job.get("time_limit") and time.perf_counter() - w0 > job["time_limit"]:
            break
    p = os.path.join(RAW, f"b2_{job['cell']}_{job['run']}.npz")
    np.savez_compressed(p, data=np.array(traj, float))
    return {"job_id": job["job_id"], **{k: v for k, v in job.items() if k != "job_id"},
            "config": cfg, "flags": fl, "dt": sim.params["dt"], "t_end": sim.time,
            "complete": st.n_active == 0, "deadlock": deadlock, "n_remaining": int(st.n_active),
            "leaked": len(sim.leaked), "r1_used": sc.r1_used, "npz": os.path.relpath(p, DATA2B),
            "wall_s": time.perf_counter() - w0}


if __name__ == "__main__":
    cells = sys.argv[1:] or ["pub", "cf", "cf_edge"]
    jobs = [{"job_id": f"{c}|{r}", "cell": c, "run": r, "N": N, "L": L, "seed": 42 + k,
             **({"time_limit": 900.0} if c == "c3" else {})}
            for c in cells for k, (r, N, L) in enumerate(RUNS)]
    print("wall", run_jobs(jobs, run, os.path.join(DATA2B, "b2_croma.jsonl"), workers=4, log_every=1))
