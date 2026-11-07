"""W2.1(b) C1 published flags, w=0.8, 100 agents, up to 600 s, seeds 42-141.
Stops at deadlock (StationaryDetector: all active |v|<0.01 m/s for 10 s, no exit).
Records per-agent attributes, door-arrival and door-crossing events (with the number
of agents within 1 m behind), exit times, and a full snapshot at detection
(wave2/data/library/C1_w0.8_seed<seed>.pkl). Output: wave2/data/w21_runs.jsonl
Flags: all published (w2_metrics=light: collision counting skipped, dynamics identical).
"""
import os, pickle, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from w2lib import (DATA, LIB, Passability, StationaryDetector, build, p1_condition,
                   run_jobs, snapshot)

WIDTH = float(os.environ.get("W21_WIDTH", 0.8))
T_MAX = 600.0
_PASS = {}


def get_pass(width, flags):
    key = (width, flags.get("A_w", 2000.0), flags.get("B_w", 0.08), flags.get("edge", "sharp"))
    if key not in _PASS:
        _PASS[key] = Passability(width, A_w=key[1], B_w=key[2], edge=key[3])
    return _PASS[key]


def behind_count(st, i, radius=1.0):
    act = st.active_indices
    d = np.linalg.norm(st.positions[act] - st.positions[i], axis=1)
    m = (act != i) & (d < radius) & (st.positions[act, 0] < st.positions[i, 0])
    return int(m.sum())


def run(job):
    seed = job["seed"]
    flags = job.get("flags", {})
    w0 = time.perf_counter()
    width = job.get("width", WIDTH)
    PASS = get_pass(width, flags)
    sim = build("C1", seed=seed, width=width, flags=flags)
    st = sim.state
    n = st.n
    attrs = [{"id": i, "r": float(st.radii[i]), "v0": float(st.desired_speeds[i]),
              "tau": float(st.taus[i]),
              "margin_C1": PASS.margin(st.radii[i], st.desired_speeds[i], st.taus[i]),
              "margin_C3": PASS.margin(st.radii[i], st.desired_speeds[i], st.taus[i], kind="C3")}
             for i in range(n)]
    arrive = {}
    cross = {}
    exit_t = {}
    det = StationaryDetector()
    deadlock = False
    while sim.time < T_MAX - 1e-9 and st.n_active > 0:
        prev_active = st.active.copy()
        sim.step()
        st = sim.state
        x, y = st.positions[:, 0], st.positions[:, 1]
        near = np.where(st.active & (x > 9.4) & (np.abs(y - 5.0) < 0.6))[0]
        for i in near:
            if i not in arrive:
                arrive[int(i)] = {"t": sim.time, "n_active": st.n_active,
                                  "behind_1m": behind_count(st, i)}
        for i in np.where(prev_active & (x >= 10.0))[0]:
            if int(i) not in cross:
                cross[int(i)] = {"t": sim.time, "n_active": int(prev_active.sum()),
                                 "behind_1m": behind_count(st, i) if st.active[i] else None}
        for i in np.where(prev_active & ~st.active)[0]:
            exit_t[int(i)] = sim.time
        if det.update(sim):
            deadlock = True
            break
    res = {"job_id": job["job_id"], "seed": seed, "width": width, "flags": flags,
           "T_MAX": T_MAX, "dt": sim.params["dt"], "t_end": sim.time,
           "complete": st.n_active == 0, "deadlock": deadlock,
           "n_remaining": st.n_active, "attrs": attrs, "arrive": arrive, "cross": cross,
           "exit_t": exit_t, "wall_s": time.perf_counter() - w0}
    if st.n_active > 0:
        act = st.active_indices
        res["residual"] = [{"id": int(i), "pos": st.positions[i].tolist(),
                            "speed": float(np.linalg.norm(st.velocities[i]))} for i in act]
        res["max_speed"] = float(np.linalg.norm(st.velocities[act], axis=1).max())
        res["p1_n_within_1m"] = p1_condition(st)
    if deadlock:
        tag = job.get("tag", "C1_w%.1f" % width)
        path = os.path.join(LIB, f"{tag}_seed{seed}.pkl")
        with open(path, "wb") as f:
            pickle.dump(snapshot(sim), f)
        res["snapshot"] = os.path.relpath(path, os.path.dirname(DATA))
    return res


if __name__ == "__main__":
    seeds = range(int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else range(42, 142)
    jobs = [{"job_id": f"seed{s}", "seed": s} for s in seeds]
    wall = run_jobs(jobs, run, os.path.join(DATA, "w21_runs.jsonl"), workers=4, log_every=5)
    print("wall", wall)
