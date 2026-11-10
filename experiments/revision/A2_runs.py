"""A2 (runs): the ORCA density gate w_o = 1 - s(rho; 4, 2) along whole runs of force-coupled ORCA.

Reruns the first 10 seeds (242-251) of the Sect. 6.2 whole runs (experiments/E6/e6.py, variant E6a: config
C3, corrected-forward flags CF, i.e. w2_orca = rvo2, w = 0.8 m, 100 agents, no noise, 600 s cap, stop at
deadlock or completion; recorder experiments/lib/runlib.whole_run) with the steering wrapped, not edited:
HybridSteeringModel.compute_forces is replaced by a wrapper that receives the per-agent densities that
Simulation.step passes (rho_i = N_i / (pi R^2), N_i the other active agents within R = 3 m, no floor in the
gate; desired.py floors rho at 0.01 m^-2 for the Weidmann factor only), evaluates
w_o = 1 - 1/(1 + exp(-k (rho - rho0))) with rho0 = rho_orca_fade, k = k_orca_fade from the run's params
(4.0 m^-2, 2.0 m^2), and records per step the minimum of w_o over the agents active at the start of the
step, the maximum rho and the number of active agents. The wrapped call returns the unchanged forces, so
the run is the E6a run; every record carries a check against data/E6/e6a.jsonl (t_end, completion, exits).

Per run it stores: min w_o and the time at which it occurs, max N_i, the fraction of steps in which some
agent has w_o < 0.99 (and < 0.95, < 0.9), the time-mean of the per-step minimum, and the per-step minimum
w_o down-sampled to 1 s (minimum within each second).

Output: data/revision/A2/a2_runs.jsonl (resumable, job_id "A2|seed<seed>").
Usage: A2_runs.py [n_seeds]   (default 10; one worker)
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import CF, DATA, load_runs, run_jobs  # noqa: E402
import numpy as np  # noqa: E402
import runlib  # noqa: E402
from sim.steering.hybrid import HybridSteeringModel  # noqa: E402

OUT = os.path.join(revlib.data_dir("A2"), "a2_runs.jsonl")
E6A = os.path.join(DATA, "E6", "e6a.jsonl")
SEEDS = list(range(242, 428))
REC = []
_orig = HybridSteeringModel.compute_forces


def _wrapped(self, agent_state, neighbor_lists, walls, local_densities):
    act = agent_state.active
    if self.orca is not None and act.any():
        rho = np.asarray(local_densities)[act]
        x0 = self.params.get("rho_orca_fade", 4.0)
        k = self.params.get("k_orca_fade", 2.0)
        w = 1.0 - 1.0 / (1.0 + np.exp(-k * (rho - x0)))
        REC.append((float(w.min()), float(rho.max()), int(act.sum())))
    return _orig(self, agent_state, neighbor_lists, walls, local_densities)


HybridSteeringModel.compute_forces = _wrapped


def job_fn(job):
    REC.clear()
    res = runlib.whole_run(job)
    w = np.array([r[0] for r in REC])
    rho = np.array([r[1] for r in REC])
    dt = res["dt"]
    i = int(w.argmin())
    nsec = int(math.ceil(len(w) * dt))
    per_s = [float(w[int(round(s / dt)):int(round((s + 1) / dt))].min()) for s in range(nsec)
             if int(round(s / dt)) < len(w)]
    keep = ("job_id", "seed", "config", "flags", "width", "sigma", "t_max", "dt", "t_end", "complete",
            "deadlock", "capped", "n_exits", "n_remaining", "wall_s")
    out = {k: res[k] for k in keep}
    out.update({"n_steps": len(w), "w_min": float(w.min()), "t_w_min": (i + 1) * dt, "rho_max": float(rho.max()),
                "N_max": int(round(rho.max() * math.pi * 9.0)), "n_active_at_w_min": REC[i][2],
                "frac_steps_below": {str(c): float(np.mean(w < c)) for c in (0.99, 0.95, 0.9)},
                "w_min_time_mean": float(w.mean()), "w_min_per_s": per_s})
    return out


def main(n=10):
    E = {r["seed"]: r for r in load_runs(E6A)}
    jobs = [{"job_id": f"A2|seed{s}", "seed": s, "width": 0.8, "flags": dict(CF), "sigma": 0.0,
             "t_max": 600.0, "config": "C3"} for s in SEEDS[:n]]
    wall = run_jobs(jobs, job_fn, OUT, workers=1)
    for r in load_runs(OUT):
        e = E[r["seed"]]
        same = (abs(r["t_end"] - e["t_end"]) < 1e-9 and r["complete"] == e["complete"] and r["n_exits"] == e["n_exits"])
        print(r["seed"], "w_min %.4f" % r["w_min"], "N_max", r["N_max"], "frac<0.99 %.3f" % r["frac_steps_below"]["0.99"],
              "same_as_E6a", same)
    return wall


if __name__ == "__main__":
    print("wall", main(int(sys.argv[1]) if len(sys.argv) > 1 else 10))
