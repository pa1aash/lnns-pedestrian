"""Shared runners for batch-2 experiments.

whole_run(job)   one bottleneck run from spawn (recorder of experiments/E1/e1_library.py: stop at deadlock,
                 i.e. every active |v| < 0.01 m/s for 10 s with no exit, or completion, or T_MAX),
                 optional velocity noise, optional snapshot at deadlock. Used by E5a, E5b, E7, E7b_lib.
quench(job)      restart a library snapshot under an arm (pattern of experiments/pilot/w22_quench.py).
escape(job)      noisy restart until the blocker escapes (pattern of experiments/pilot/w23_escape.py).

Every restart passes the full flag set (mode flags union arm flags): w2lib.restore drops the snapshot's
w2_*, A_w and B_w params and re-applies only what it is given.
"""
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2lib import (ROOT, Passability, StationaryDetector, build, restore, snapshot,  # noqa: E402
                   weidmann_factor)
import numpy as np  # noqa: E402

DOOR = np.array([10.0, 5.0])
_PASS = {}


def get_pass(width, flags):
    """Passability for the run's wall model. B_w_edge has the same on-axis profile as B_w at the
    jambs (pilot wave2b CODE_CHANGES), so it is keyed as B_w there."""
    bw = flags.get("B_w", flags.get("B_w_edge", 0.08))
    key = (width, flags.get("A_w", 2000.0), bw, flags.get("edge", "sharp"))
    if key not in _PASS:
        _PASS[key] = Passability(width, A_w=key[1], B_w=key[2], edge=key[3])
    return _PASS[key]


def whole_run(job):
    """job: job_id, seed, width, flags, sigma, t_max, config (C1), lib (dir or None), tag."""
    seed, width, flags = job["seed"], job.get("width", 0.8), dict(job.get("flags", {}))
    sigma, t_max = job.get("sigma", 0.0), job.get("t_max", 600.0)
    w0 = time.perf_counter()
    P = get_pass(width, flags)
    sim = build(job.get("config", "C1"), seed=seed, width=width, noise=sigma, flags=flags)
    st = sim.state
    margin = [P.margin(st.radii[i], st.desired_speeds[i], st.taus[i]) for i in range(st.n)]
    exit_t, arrive = {}, {}
    det = StationaryDetector()
    deadlock = False
    while sim.time < t_max - 1e-9 and st.n_active > 0:
        prev = st.active.copy()
        sim.step()
        st = sim.state
        x, y = st.positions[:, 0], st.positions[:, 1]
        for i in np.where(st.active & (x > 9.4) & (np.abs(y - 5.0) < 0.6))[0]:
            if int(i) not in arrive:
                arrive[int(i)] = {"t": sim.time, "n_active": st.n_active, "order": len(arrive)}
        for i in np.where(prev & ~st.active)[0]:
            exit_t[int(i)] = sim.time
        if det.update(sim):
            deadlock = True
            break
    res = {k: v for k, v in job.items() if k != "lib"}
    res.update({"dt": sim.params["dt"], "t_end": sim.time, "complete": st.n_active == 0,
                "deadlock": deadlock, "capped": (not deadlock) and st.n_active > 0,
                "n_exits": len(exit_t), "n_remaining": st.n_active,
                "evacuation_time": sim.time if st.n_active == 0 else None,
                "exit_t": exit_t, "arrive": arrive, "margin": margin,
                "attrs": [{"id": i, "r": float(st.radii[i]), "v0": float(st.desired_speeds[i]),
                           "tau": float(st.taus[i])} for i in range(st.n)]})
    if st.n_active:
        act = st.active_indices
        res["residual"] = [{"id": int(i), "pos": st.positions[i].tolist(),
                            "speed": float(np.linalg.norm(st.velocities[i]))} for i in act]
        res["max_speed"] = float(np.linalg.norm(st.velocities[act], axis=1).max())
    if deadlock and job.get("lib"):
        os.makedirs(job["lib"], exist_ok=True)
        path = os.path.join(job["lib"], f"{job['tag']}_seed{seed}.pkl")
        with open(path, "wb") as f:
            pickle.dump(snapshot(sim), f)
        res["snapshot"] = os.path.relpath(path, ROOT)
    res["wall_s"] = time.perf_counter() - w0
    return res


def quench(job):
    """job: snap (abs path), config, flags (full set), sigma, noise_seed, perturb, deterministic, t_q."""
    snap = pickle.load(open(job["snap"], "rb"))
    sim = restore(snap, job["config"], flags=dict(job.get("flags", {})), noise=job.get("sigma", 0.0),
                  noise_seed=job.get("noise_seed"))
    st = sim.state
    if job.get("perturb") is not None:
        rng = np.random.default_rng(job["perturb"])
        a = st.active_indices
        st.positions[a] += rng.normal(0, 1e-9, (len(a), 2))
    resid = [int(i) for i in st.active_indices]
    t0, w0 = sim.time, time.perf_counter()
    exits = {}
    det = StationaryDetector(hold=10.0, v_thr=1e-3) if job.get("deterministic") else None
    stationary = False
    for _ in range(int(round(job.get("t_q", 120.0) / sim.params["dt"]))):
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
                "stationary_stop": stationary, "t_run": sim.time - t0, "dt": sim.params["dt"],
                "wall_s": time.perf_counter() - w0,
                "final_pos": {int(i): st.positions[i].tolist() for i in resid if st.active[i]}})
    return out


def escape(job):
    """job: snap, blocker, cond (full / alone / frozen), config, flags (full set), sigma, noise_seed,
    dt, t_cens. Escape = blocker centre crosses the door plane x >= 10 (or exits). Also records the
    first exit of any agent and the blocker's velocity moments while trapped (2 s burn-in, x < 9.95)."""
    snap = pickle.load(open(job["snap"], "rb"))
    b = job["blocker"]
    sim = restore(snap, job.get("config", "C1"), flags=dict(job.get("flags", {})), noise=job.get("sigma", 0.0),
                  noise_seed=job.get("noise_seed"), dt=job.get("dt"))
    st = sim.state
    others = [int(i) for i in st.active_indices if i != b]
    if job["cond"] == "alone":
        st.active[others] = False
    frozen_pos = st.positions[others].copy()
    t0, dt, w0 = sim.time, sim.params["dt"], time.perf_counter()
    mom = np.zeros(5)
    esc, first_exit, first_agent = None, None, None
    other_exit_first = False
    for _ in range(int(round(job.get("t_cens", 300.0) / dt))):
        prev = st.active.copy()
        sim.step()
        st = sim.state
        if job["cond"] == "frozen":
            st.positions[others] = frozen_pos
            st.velocities[others] = 0.0
            st.active[others] = True
        gone = np.where(prev & ~st.active)[0]
        if first_exit is None and len(gone):
            first_exit, first_agent = sim.time - t0, int(gone[0])
        x = st.positions[b, 0]
        if x >= 10.0 or not st.active[b]:
            esc = sim.time - t0
            break
        if job["cond"] == "full" and not other_exit_first and others and not st.active[others].all():
            other_exit_first = True
        if sim.time - t0 > 2.0 and x < 9.95:
            v = st.velocities[b]
            mom += (1.0, v[0], v[1], v[0] * v[0], v[1] * v[1])
    out = {k: v for k, v in job.items() if k != "snap"}
    out.update({"snap": os.path.basename(job["snap"]), "escape_t": esc, "censored": esc is None,
                "first_exit_t": first_exit, "first_exit_agent": first_agent,
                "t_run": sim.time - t0, "dt": dt, "other_exit_first": other_exit_first,
                "v_moments": mom.tolist(), "wall_s": time.perf_counter() - w0})
    return out
