"""A13 (small facts): the two short re-runs needed for items 5 and 6. One worker, deterministic.

Part 1, creep (item 5). The legacy-solver replay flips of E2 (data/E2/e2_quench.jsonl, arm C3_pub; listed in
experiments/fixan/fix_a4.py): E1b_seed174 (blocker 72; unperturbed freed at 50.91 s, replays 901-904 held) and
E1b_seed187 (blocker 47; unperturbed held, replay 903 freed at 109.11 s). Each of the 2 unperturbed runs and the
5 flipping replays is re-run exactly as experiments/lib/runlib.py quench (config C3, flags CF + w2_orca =
published, 1e-9 m Gaussian displacement of every active position from numpy default_rng(perturb seed), 120 s,
dt = 0.01 s; no stationary stop is reached in these runs). Every 0.1 s the blocker's position, velocity and
the largest speed of any active agent are recorded. The blocker exit time is checked against e2_quench.jsonl.

Part 2, arch peaks (item 6). The run holding the largest arch body force of experiments/arch/arch.py
(data/arch/arch.jsonl: seed 61, v0 mean 5 m/s, dt = 0.01 s, 108.0 kN at t = 1.4 s) and of the N5 fine cell
(data/N5/n5.jsonl, dt0.0025_v5: seed 60, 22.2 kN at t = 1.7-1.9 s) are re-run from spawn with the same build
(C1, CF + speed_mean 5, w = 0.8 m) up to 2.5 s. At every 0.1 s check the arch of arch.arch_check is
recomputed (same contact graph, jamb test and largest-size component) and, for that component, the summed
body force k * sum(overlap) (must equal the stored value), the number of contacts, the largest single
agent-agent overlap r_ij - d_ij, the largest single-contact force k (r_ij - d_ij) + A exp((r_ij - d_ij)/B), the
largest agent-jamb overlap r_i - d_iW and the members' radii.
Output: data/revision/A13/creep.jsonl, data/revision/A13/arch_peak.jsonl (one record per run).
"""
import json
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import revlib  # noqa: E402
from revlib import CF, ROOT, np  # noqa: E402
from w2lib import build, restore  # noqa: E402
from scipy.sparse.csgraph import connected_components  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402

OUTD = revlib.data_dir("A13")
CREEP = [("E1b_seed174", 72, None), ("E1b_seed174", 72, 901), ("E1b_seed174", 72, 902),
         ("E1b_seed174", 72, 903), ("E1b_seed174", 72, 904), ("E1b_seed187", 47, None), ("E1b_seed187", 47, 903)]
K, A, B = 120000.0, 2000.0, 0.08


def creep_run(tag, b, ps):
    snap = pickle.load(open(os.path.join(ROOT, "data", "E1", "library", f"{tag}.pkl"), "rb"))
    sim = restore(snap, "C3", flags={**CF, "w2_orca": "published"})
    st = sim.state
    if ps is not None:
        rng = np.random.default_rng(ps)
        a = st.active_indices
        st.positions[a] += rng.normal(0, 1e-9, (len(a), 2))
    t0 = sim.time
    rec, exit_t = [], None
    for k in range(12000):
        sim.step()
        st = sim.state
        if exit_t is None and not st.active[b]:
            exit_t = sim.time - t0
        if (k + 1) % 10 == 0:
            a = st.active_indices
            rec.append([sim.time - t0, *(st.positions[b].tolist() if st.active[b] else [None, None]),
                        *(st.velocities[b].tolist() if st.active[b] else [None, None]),
                        float(np.max(np.linalg.norm(st.velocities[a], axis=1))) if len(a) else 0.0])
        if st.n_active == 0:
            break
    return {"job_id": f"{tag}|{'u' if ps is None else ps}", "tag": tag, "blocker": b, "perturb": ps,
            "blocker_exit_t": exit_t, "cols": ["t", "x", "y", "vx", "vy", "max_speed_any"], "rows": rec}


def arch_detail(sim):
    st = sim.state
    a = st.active_indices
    P = st.positions[a]
    m = (np.linalg.norm(P - [10.0, 5.0], axis=1) < 1.5) & (P[:, 0] < 10.3)
    ids = a[m]
    if len(ids) == 0:
        return None
    P, r = st.positions[ids], st.radii[ids]
    D = np.linalg.norm(P[:, None] - P[None], axis=2)
    ov = (r[:, None] + r[None]) - D
    np.fill_diagonal(ov, -1.0)
    C = ov > 0
    d, _ = agents_to_walls(P, [sim.world.walls[3], sim.world.walls[4]])
    lo, up = d[:, 0] < r, d[:, 1] < r
    n, lab = connected_components(C, directed=False)
    best = None
    for k in range(n):
        comp = lab == k
        if (lo & comp).any() and (up & comp).any():
            cc = np.ix_(comp, comp)
            o = np.triu(np.maximum(ov[cc], 0.0), 1)
            rec = {"size": int(comp.sum()), "body_force_N": float(K * np.sum(np.maximum(ov[cc], 0.0)) / 2),
                   "n_contacts": int((o > 0).sum()), "max_overlap_m": float(o.max()),
                   "max_contact_force_N": float(K * o.max() + A * np.exp(o.max() / B)),
                   "max_jamb_overlap_m": float(np.max(np.maximum(r[comp] - d[comp].min(axis=1), 0.0))),
                   "radii_m": r[comp].tolist()}
            if best is None or rec["size"] > best["size"]:
                best = rec
    return best


def arch_run(seed, dt, t_end=2.5):
    sim = build("C1", seed=seed, width=0.8, noise=0.0, flags={**CF, "speed_mean": 5.0, "dt": dt})
    every = int(round(0.1 / sim.params["dt"]))
    checks = []
    while sim.time < t_end - 1e-9:
        sim.step()
        if sim.step_count % every == 0:
            a = arch_detail(sim)
            if a:
                checks.append({"t": sim.time, **a})
    return {"job_id": f"arch|seed{seed}|dt{dt}", "seed": seed, "dt": dt, "checks": checks}


def main():
    w0 = time.process_time()
    for path, jobs in ((os.path.join(OUTD, "creep.jsonl"), [lambda c=c: creep_run(*c) for c in CREEP]),
                       (os.path.join(OUTD, "arch_peak.jsonl"),
                        [lambda: arch_run(61, 0.01), lambda: arch_run(60, 0.0025)])):
        if os.path.exists(path):
            continue
        with open(path, "w") as f:
            for j in jobs:
                r = j()
                f.write(json.dumps(r) + "\n")
                f.flush()
                print(r["job_id"], r.get("blocker_exit_t"), round(time.process_time() - w0), "s", flush=True)
    print("cpu s", time.process_time() - w0)


if __name__ == "__main__":
    main()
