"""E10: CroMa geometry, like-for-like human validity (port of experiments/pilot/b2_croma_pilot.py).

Scenario: CromaBottleneckScenario (code/sim/scenarios/croma.py), w = 0.8 m, N and corridor length L matched
to the five CroMa 0.8 m runs (data/ext/croma): 4D030 (135, 2.0), 4D040 (136, 2.0), 4D110 (131, 0.21),
4D120 (129, 0.21), 4D130 (128, 0.21). 25 runs per cell, seeds 42-66; run type = RUNS[(seed - 42) % 5]
(5 per run type). Start positions: the scenario's rejection sampling in every cell.
dt = 0.01 s, cap 600 s, stop at deadlock (every active |v| < 0.01 m/s for 10 s, no exit) or completion.
Cells:
  C1_pub      C1, published-reproduction (all flags default; corner rule = segment sum);
  C1_cf       C1, corrected-forward (CF; corner rule convex_union);
  C1_cf_edge  C1, CF + B_w_edge = 0.04 (jamb and corridor-wall ends at the door edge);
  C3_rvo2_cf  C3 with RVO2 ORCA, CF;
  C1_cf_sig   C1, CF + per-step velocity noise sigma* (data/derived/sigma_star.json, set by E6b).
CF's scenario key (spawn) does not apply: the CroMa scenario always uses rejection sampling.
Recorded per run: completion, t_end, deadlock, remaining, wall leaks (agents whose centre ever left the
walkable region), and from the trajectories (agents with x > 6.5 m, every 4 steps = 25 Hz, saved to
data/E10/raw/<cell>_seed<seed>.npz) the human estimator of experiments/pilot/w28_croma.py, unchanged
(its sim() function): passages through the entrance plane x = 10, flow, gaps > 2 s, longest gap, median
gap, and the waiting-zone velocity fluctuation (Savitzky-Golay 1.48 s, minus the mean of neighbours within
0.74 m, zone 0.3-2.5 m before the entrance, local-mean speed < 0.3 m/s).
Human reference: the same estimator (w28_croma.croma) on the five CroMa files -> data/E10/human.json.
If sigma_star.json is missing or not "ok", the C1_cf_sig cell is not run and the script exits with code 3
after the other cells (the step stays open; rerunning it resumes).
Output: data/E10/e10_croma.jsonl (job_id "<cell>|seed<seed>"), resumable.
"""
import glob
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(EXP, "lib"))
from e1lib import CF, DATA, DERIVED, ROOT, run_jobs  # noqa: E402
from w2lib import SCEN_KEYS, Simulation, StationaryDetector  # noqa: E402
import numpy as np  # noqa: E402
import qargs  # noqa: E402
from sim.scenarios.croma import CromaBottleneckScenario  # noqa: E402

_spec = importlib.util.spec_from_file_location("w28_croma", os.path.join(EXP, "pilot", "w28_croma.py"))
w28 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w28)

OUT = os.path.join(DATA, "E10", "e10_croma.jsonl")
RAW = os.path.join(DATA, "E10", "raw")
HUMAN = os.path.join(DATA, "E10", "human.json")
CROMA = os.path.join(DATA, "ext", "croma")
SIGMA_STAR = os.path.join(DERIVED, "sigma_star.json")
RUNS = [("4D030", 135, 2.0), ("4D040", 136, 2.0), ("4D110", 131, 0.21), ("4D120", 129, 0.21),
        ("4D130", 128, 0.21)]
CFP = {k: v for k, v in CF.items() if k not in SCEN_KEYS}
CELLS = {"C1_pub": ("C1", {}), "C1_cf": ("C1", dict(CFP)), "C1_cf_edge": ("C1", {**CFP, "B_w_edge": 0.04}),
         "C3_rvo2_cf": ("C3", {**CFP, "w2_orca": "rvo2"}), "C1_cf_sig": ("C1", dict(CFP))}
SEEDS = range(42, 67)
T_MAX = 600.0


def run(job):
    w0 = time.perf_counter()
    sc = CromaBottleneckScenario(job["N"], 0.8, job["L"])
    sim = Simulation.from_scenario(sc, job["config"], seed=job["seed"],
                                   param_overrides={**job["flags"], "w2_metrics": "light"})
    sim.velocity_noise_std = job.get("sigma", 0.0)
    det = StationaryDetector()
    traj, deadlock = [], False
    st = sim.state
    while sim.time < job["t_max"] - 1e-9 and st.n_active > 0:
        sim.step()
        st = sim.state
        if sim.step_count % 4 == 0:
            for i in np.where(st.active & (st.positions[:, 0] > 6.5))[0]:
                traj.append((sim.time, i, st.positions[i, 0], st.positions[i, 1]))
        if det.update(sim):
            deadlock = True
            break
    os.makedirs(job["raw_dir"], exist_ok=True)
    p = os.path.join(job["raw_dir"], f"{job['cell']}_seed{job['seed']}.npz")
    np.savez_compressed(p, data=np.array(traj, float).reshape(-1, 4))
    est = w28.sim(p) if len(traj) else {"n_pass": 0}
    out = {k: v for k, v in job.items() if k != "raw_dir"}
    out.update({"dt": sim.params["dt"], "t_end": sim.time, "complete": st.n_active == 0, "deadlock": deadlock,
                "n_remaining": int(st.n_active), "n_leaked": len(sim.leaked), "leaked": sorted(sim.leaked),
                "r1_used": sc.r1_used, "npz": os.path.relpath(p, ROOT), "estimator": est,
                "wall_s": time.perf_counter() - w0})
    return out


def jobs(sigma=None, raw_dir=RAW):
    J = []
    for cell, (cfg, fl) in CELLS.items():
        if cell == "C1_cf_sig" and sigma is None:
            continue
        for s in SEEDS:
            run_id, N, L = RUNS[(s - 42) % 5]
            J.append({"job_id": f"{cell}|seed{s}", "cell": cell, "run": run_id, "N": N, "L": L, "seed": s,
                      "config": cfg, "flags": fl, "sigma": sigma if cell == "C1_cf_sig" else 0.0,
                      "t_max": T_MAX, "raw_dir": raw_dir})
    return J


def human(path=HUMAN):
    files = sorted(f for f in glob.glob(os.path.join(CROMA, "*.txt")) if "_w080_" in f)
    res = {"estimator": "experiments/pilot/w28_croma.py croma(), unchanged", "runs": [w28.croma(f) for f in files]}
    json.dump(res, open(path, "w"), indent=1, default=float)
    return res


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sp = a.rest[a.rest.index("--sigma-star") + 1] if "--sigma-star" in a.rest else SIGMA_STAR
    sigma = None
    if os.path.exists(sp):
        rec = json.load(open(sp))
        sigma = rec.get("sigma_star") if rec.get("status") == "ok" else None
    raw = os.path.join(os.path.dirname(out), "raw") if a.out else RAW
    J = qargs.select(jobs(sigma, raw), a)
    wall = run_jobs(J, run, out, workers=a.workers, log_every=5)
    if a.out is None and not os.path.exists(HUMAN):
        human()
    if sigma is None:
        print("E10: sigma* not available; C1_cf_sig not run", flush=True)
        sys.exit(3)
    return wall


if __name__ == "__main__":
    print("wall", main())
