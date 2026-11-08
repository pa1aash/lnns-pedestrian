"""E6 failures: keystone test (plan change C12) on the residual geometry of every run that did not complete.

The E6 runs saved no snapshots, only the final positions of the residual agents (and every agent's r, v0,
tau). The final state is rebuilt: the run's own spawn (same seed, corrected-forward flags) with every agent
not in the residual deactivated (removed as an exited agent is), the residual agents at their saved
positions, all velocities zero. For E6a deadlocks (every |v| < 0.01 m/s for 10 s) this is the saved rest
state; for runs that reached 600 s while still moving (C3 RVO2 oscillating, or noise) it is the rest state
at the same positions.

Tests, each restarted with C1, sigma = 0, dt = 0.01 s, window 120 s, stopped once stationary
(|v| < 1e-3 m/s for 10 s), as experiments/E1/keystone.py:
  K0   all residual agents kept: is the residual a C1 fixed point (held)?
  K0c  (E6a only) all residual agents kept, C3 RVO2: does the arm hold its own residual from rest?
  K1   blocker (residual agent nearest the door centre) alone.
  K2   blocker removed.
  K1b  (when K1 held and K2 left agents behind) K1 on the K2-held agent nearest the door.
Classes: lone_keystone (K1 held, K2 all exit), lone_keystone_second_trap (K1 held, K2 some held),
collective (K1 freed).
Output: data/E6/keystone.jsonl (job_id "<variant>|seed<N>|<test>"), resumable.
Usage: keystone_e6.py [--workers 2]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
from e1lib import CF, DATA, StationaryDetector, build, load_runs, run_jobs  # noqa: E402
import numpy as np  # noqa: E402

DOOR = np.array([10.0, 5.0])
T_Q = 120.0
OUT = os.path.join(DATA, "E6", "keystone.jsonl")


def failures():
    R = []
    for v in ("e6a", "e6b"):
        R += [r for r in load_runs(os.path.join(DATA, "E6", f"{v}.jsonl")) if not r["complete"]]
    return R


def rebuild(r, config):
    sim = build(config, seed=r["seed"], width=0.8, noise=0.0, flags=dict(CF))
    st = sim.state
    pos = {int(x["id"]): np.array(x["pos"]) for x in r["residual"]}
    drop = [i for i in range(st.n) if i not in pos]
    st.deactivate(np.array(drop, int))
    for i, p in pos.items():
        st.positions[i] = p
    st.velocities[:] = 0.0
    return sim, pos


def blocker_of(pos):
    return min(pos, key=lambda i: float(np.linalg.norm(pos[i] - DOOR)))


def run(job):
    w0 = time.perf_counter()
    r = job["run"]
    sim, pos = rebuild(r, "C3" if job["test"] == "K0c" else "C1")
    st = sim.state
    resid = sorted(pos)
    b = blocker_of(pos)
    keep = {"K0": resid, "K0c": resid, "K1": [b], "K1b": [job.get("target")],
            "K2": [i for i in resid if i != b]}[job["test"]]
    drop = [i for i in resid if i not in keep]
    if drop:
        st.deactivate(np.array(drop, int))
    exits, stationary = {}, False
    det = StationaryDetector(hold=10.0, v_thr=1e-3)
    for _ in range(int(round(T_Q / sim.params["dt"]))):
        prev = st.active.copy()
        sim.step()
        st = sim.state
        for i in np.where(prev & ~st.active)[0]:
            exits[int(i)] = sim.time
        if st.n_active == 0:
            break
        if det.update(sim):
            stationary = True
            break
    out = {k: v for k, v in job.items() if k != "run"}
    out.update({"residual": resid, "blocker": b, "kept": keep, "exits": exits,
                "held": [i for i in keep if i not in exits], "stationary_stop": stationary,
                "wall_s": time.perf_counter() - w0})
    return out


def jobs_phase1(R):
    J = []
    for r in R:
        tag = f"{r['variant']}|seed{r['seed']}"
        tests = ["K0", "K1", "K2"] + (["K0c"] if r["variant"] == "E6a" else [])
        J += [{"job_id": f"{tag}|{t}", "variant": r["variant"], "seed": r["seed"], "test": t, "run": r}
              for t in tests]
    return J


def jobs_phase2(R, res):
    J = []
    for r in R:
        tag = f"{r['variant']}|seed{r['seed']}"
        k1, k2 = res.get(tag + "|K1"), res.get(tag + "|K2")
        if k1 and k2 and k1["held"] and k2["held"]:
            pos = {int(x["id"]): np.array(x["pos"]) for x in r["residual"]}
            tgt = min(k2["held"], key=lambda i: float(np.linalg.norm(pos[i] - DOOR)))
            J.append({"job_id": tag + "|K1b", "variant": r["variant"], "seed": r["seed"], "test": "K1b",
                      "target": int(tgt), "run": r})
    return J


def load_res():
    return {x["job_id"]: x for x in load_runs(OUT)} if os.path.exists(OUT) else {}


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 2
    R = failures()
    run_jobs(jobs_phase1(R), run, OUT, workers=workers, log_every=50)
    run_jobs(jobs_phase2(R, load_res()), run, OUT, workers=workers, log_every=50)


if __name__ == "__main__":
    main()
