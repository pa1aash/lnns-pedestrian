"""E1: lone-trap library, room bottleneck, both model modes.

C1, w = 0.8 m, 100 agents, dt = 0.01 s, noise sigma = 0, cap 600 s, w2_metrics = light.
Stop at deadlock (StationaryDetector: every active |v| < 0.01 m/s for 10 s, no exit) or at
completion. Seeds 42-241 in each mode:
  E1a  published-reproduction: all flags default;
  E1b  corrected-forward: w2_numerics=fixed, spawn=rejection, w2_orca=rvo2, w2_crush=off,
       w2_wall_corner=convex_union (ORCA and crush flags are inert in C1; recorded for the mode).

Per-agent definitions are those of wave2/scripts/w21_library.py, unchanged:
  stuck-alone margin  w2lib.Passability(w).margin(r, v0, tau) (rho = 0, C1 drive m v0/tau), and the
                      C3 rest-state version (kind="C3");
  door-zone arrival   first step with x > 9.4 and |y - 5| < 0.6 while active;
  n_active at arrival number of active agents after that step (the agent included), so
                      "others active at arrival" = n_active - 1;
  exit                deactivation step (published goal-radius rule).
Added here: arrival order, local density and v_eff = v0 * Weidmann(rho) at arrival, the C1 drive
m v_eff / tau at arrival, and a deadlock-type classification at detection.

Deadlock type (no residual-geometry classifier exists in the wave 2 / 2b scripts; those use the
residual count n_remaining only, which is also recorded): residual agents within 1.0 m of the door
centre (10, 5) are grouped by surface gap d_ij - r_i - r_j < 0.5 m (single linkage). The type is the
size of the group containing the residual agent nearest the door centre: lone (1), pair (2),
triple (3), larger (>= 4); "none_at_door" if no residual agent is within 1.0 m.

Output: data/E1/E1_runs.jsonl (job_id "<mode>_<seed>"), snapshots data/E1/library/<mode>_seed<N>.pkl.
(Records written in the pilot phase carry snapshot paths exec/data/library/...; e1lib.snap_path maps them.)
Re-running the same command resumes (finished job_ids are skipped).
"""
import os, pickle, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, EDATA, ELIB, ROOT, Passability, StationaryDetector, build, p1_condition, \
    run_jobs, snapshot, weidmann_factor
import numpy as np

WIDTH = 0.8
T_MAX = 600.0
MODES = {"E1a": {}, "E1b": dict(CF)}
DOOR = np.array([10.0, 5.0])
_PASS = {}


def get_pass(width, flags):
    # Same cache key and wall model as w21_library.get_pass. The corner rule does not change the
    # on-axis room profile (tests/test_exec_wall_corner.py::test_room_axis_profile_unchanged).
    key = (width, flags.get("A_w", 2000.0), flags.get("B_w", 0.08), flags.get("edge", "sharp"))
    if key not in _PASS:
        _PASS[key] = Passability(width, A_w=key[1], B_w=key[2], edge=key[3])
    return _PASS[key]


def behind_count(st, i, radius=1.0):
    act = st.active_indices
    d = np.linalg.norm(st.positions[act] - st.positions[i], axis=1)
    m = (act != i) & (d < radius) & (st.positions[act, 0] < st.positions[i, 0])
    return int(m.sum())


def local_density(st, i, R=3.0):
    """Fixed-disk density as Simulation.step computes it (neighbours within R, self excluded)."""
    act = st.active_indices
    d = np.linalg.norm(st.positions[act] - st.positions[i], axis=1)
    return float(((d <= R) & (act != i)).sum() / (np.pi * R * R))


def classify(st, radius=1.0, gap=0.5):
    act = st.active_indices
    pos, rad = st.positions[act], st.radii[act]
    dd = np.linalg.norm(pos - DOOR, axis=1)
    near = np.where(dd < radius)[0]
    if len(near) == 0:
        return {"type": "none_at_door", "size": 0, "group_ids": [], "n_near_door": 0}
    lab = {k: k for k in near}

    def find(k):
        while lab[k] != k:
            lab[k] = lab[lab[k]]
            k = lab[k]
        return k
    for a in near:
        for b in near:
            if a < b and np.linalg.norm(pos[a] - pos[b]) - rad[a] - rad[b] < gap:
                lab[find(a)] = find(b)
    k0 = near[np.argmin(dd[near])]
    grp = [int(act[k]) for k in near if find(k) == find(k0)]
    size = len(grp)
    typ = {1: "lone", 2: "pair", 3: "triple"}.get(size, "larger")
    return {"type": typ, "size": size, "group_ids": grp, "n_near_door": int(len(near)),
            "nearest_id": int(act[k0])}


def run(job):
    seed, mode = job["seed"], job["mode"]
    flags = MODES[mode]
    w0 = time.perf_counter()
    PASS = get_pass(WIDTH, flags)
    sim = build("C1", seed=seed, width=WIDTH, flags=flags)
    st = sim.state
    n = st.n
    attrs = [{"id": i, "r": float(st.radii[i]), "v0": float(st.desired_speeds[i]),
              "tau": float(st.taus[i]), "m": float(st.masses[i]),
              "margin_C1": PASS.margin(st.radii[i], st.desired_speeds[i], st.taus[i]),
              "margin_C3": PASS.margin(st.radii[i], st.desired_speeds[i], st.taus[i], kind="C3")}
             for i in range(n)]
    arrive, cross, exit_t = {}, {}, {}
    det = StationaryDetector()
    deadlock = False
    while sim.time < T_MAX - 1e-9 and st.n_active > 0:
        prev_active = st.active.copy()
        sim.step()
        st = sim.state
        x, y = st.positions[:, 0], st.positions[:, 1]
        near = np.where(st.active & (x > 9.4) & (np.abs(y - 5.0) < 0.6))[0]
        for i in near:
            if int(i) not in arrive:
                rho = local_density(st, i)
                v_eff = float(st.desired_speeds[i]) * weidmann_factor(rho)
                arrive[int(i)] = {"t": sim.time, "n_active": st.n_active,
                                  "behind_1m": behind_count(st, i), "order": len(arrive),
                                  "rho": rho, "v_eff": v_eff,
                                  "drive_C1": float(st.masses[i]) * v_eff / float(st.taus[i])}
        for i in np.where(prev_active & (x >= 10.0))[0]:
            if int(i) not in cross:
                cross[int(i)] = {"t": sim.time, "n_active": int(prev_active.sum()),
                                 "behind_1m": behind_count(st, i) if st.active[i] else None}
        for i in np.where(prev_active & ~st.active)[0]:
            exit_t[int(i)] = sim.time
        if det.update(sim):
            deadlock = True
            break
    res = {"job_id": job["job_id"], "mode": mode, "seed": seed, "width": WIDTH, "flags": flags,
           "T_MAX": T_MAX, "dt": sim.params["dt"], "t_end": sim.time,
           "complete": st.n_active == 0, "deadlock": deadlock, "n_exits": len(exit_t),
           "n_remaining": st.n_active, "attrs": attrs, "arrive": arrive, "cross": cross,
           "exit_t": exit_t}
    if st.n_active > 0:
        act = st.active_indices
        res["residual"] = [{"id": int(i), "pos": st.positions[i].tolist(),
                            "speed": float(np.linalg.norm(st.velocities[i]))} for i in act]
        res["max_speed"] = float(np.linalg.norm(st.velocities[act], axis=1).max())
        res["p1_n_within_1m"] = p1_condition(st)
        res["deadlock_type"] = classify(st)
    if deadlock:
        path = os.path.join(ELIB, f"{mode}_seed{seed}.pkl")
        with open(path, "wb") as f:
            pickle.dump(snapshot(sim), f)
        res["snapshot"] = os.path.relpath(path, ROOT)
    res["wall_s"] = time.perf_counter() - w0
    return res


if __name__ == "__main__":
    s0, s1 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (42, 242)
    jobs = [{"job_id": f"{m}_{s}", "mode": m, "seed": s} for s in range(s0, s1) for m in MODES]
    wall = run_jobs(jobs, run, os.path.join(EDATA, "E1_runs.jsonl"), workers=4, log_every=4)
    print("wall", wall)
