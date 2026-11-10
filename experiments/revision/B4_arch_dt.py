"""B4: contact-arch convergence in the time step.

The hard-driven setting of experiments/arch/arch.py (C1, CF flags, w = 0.8 m, 100 agents, mean desired speed
5 m/s, up to 600 s, stop at completion or stationary deadlock |v| < 0.01 m/s for 10 s), seeds 42-51 (10 runs),
at dt = 0.001 s and, for the comparison on the same seeds with the same recorder, at dt = 0.0025 s and 0.01 s.
Arch definition of arch.py (unchanged): every 0.1 s, among active agents within 1.5 m of (10, 5) with x < 10.3,
a connected component of the body-overlap graph that touches both jamb segments. Recorded per check with an
arch, for the arch component: size; summed body compression k * sum_{i<j} overlap_ij (arch.py's "body force",
k = 1.2e5 kg/s^2); the largest single agent-agent contact force k * overlap_ij; the largest agent-agent
overlap; the largest agent-jamb overlap and its contact force k * (r_i - d_iW). Episodes as in arch.py
(consecutive checks with an arch; lifetime t_last - t_first; persistent >= 10 s). Also, over the whole run,
the largest agent-agent overlap among all active agents.
Output: data/revision/B4/b4.jsonl (job_id "dt<dt>|seed<N>"), resumable.
Usage: B4_arch_dt.py [qargs options]   |   B4_arch_dt.py analyse
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import CF, np, run_jobs  # noqa: E402
import qargs  # noqa: E402
from w2lib import StationaryDetector, build  # noqa: E402
from scipy.sparse.csgraph import connected_components  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402

OUT = os.path.join(revlib.data_dir("B4"), "b4.jsonl")
K, V0, T_MAX, CHECK_S, PERSIST = 120000.0, 5.0, 600.0, 0.1, 10.0
DTS = (0.001, 0.0025, 0.01)
SEEDS = range(42, 52)


def arch_check(sim):
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
    walls = sim.world.walls
    d, _ = agents_to_walls(P, [walls[3], walls[4]])
    lo, up = d[:, 0] < r, d[:, 1] < r
    n, lab = connected_components(C, directed=False)
    best = None
    for k in range(n):
        comp = lab == k
        if (lo & comp).any() and (up & comp).any():
            o = np.maximum(ov[np.ix_(comp, comp)], 0.0)
            wo = np.maximum(r[comp][:, None] - d[comp], 0.0)
            rec = {"size": int(comp.sum()), "body_force_N": float(K * o.sum() / 2),
                   "max_contact_force_N": float(K * o.max()) if o.size else 0.0,
                   "max_overlap_m": float(o.max()) if o.size else 0.0,
                   "max_wall_overlap_m": float(wo.max()), "max_wall_force_N": float(K * wo.max())}
            if best is None or rec["size"] > best["size"]:
                best = rec
    return best


def max_overlap_all(sim):
    st = sim.state
    a = st.active_indices
    if len(a) < 2:
        return 0.0
    P, r = st.positions[a], st.radii[a]
    D = np.linalg.norm(P[:, None] - P[None], axis=2)
    ov = (r[:, None] + r[None]) - D
    np.fill_diagonal(ov, -1.0)
    return float(max(ov.max(), 0.0))


def run(job):
    w0 = time.perf_counter()
    fl = dict(CF, dt=job["dt"], speed_mean=V0)
    sim = build("C1", seed=job["seed"], width=0.8, noise=0.0, flags=fl)
    every = int(round(CHECK_S / sim.params["dt"]))
    det = StationaryDetector(hold=10.0, v_thr=0.01, every=every)
    eps, cur, deadlock, ov_all = [], None, False, 0.0
    n_checks = n_arch = 0
    keys = ("body_force_N", "max_contact_force_N", "max_overlap_m", "max_wall_overlap_m", "max_wall_force_N")
    while sim.time < job["t_max"] - 1e-9 and sim.state.n_active > 0:
        sim.step()
        if sim.step_count % every == 0:
            n_checks += 1
            ov_all = max(ov_all, max_overlap_all(sim))
            a = arch_check(sim)
            if a:
                n_arch += 1
                if cur is None:
                    cur = {"t0": sim.time, "t1": sim.time, **a}
                else:
                    cur["t1"] = sim.time
                    cur["size"] = max(cur["size"], a["size"])
                    for k in keys:
                        cur[k] = max(cur[k], a[k])
            elif cur is not None:
                eps.append(cur)
                cur = None
        if det.update(sim):
            deadlock = True
            break
    if cur is not None:
        cur["censored"] = True
        eps.append(cur)
    life = [e["t1"] - e["t0"] for e in eps]
    st = sim.state
    out = dict(job)
    out.update({"flags": fl, "complete": st.n_active == 0, "deadlock": deadlock, "t_end": sim.time,
                "n_remaining": int(st.n_active), "n_checks": n_checks, "frac_checks_arch": n_arch / max(n_checks, 1),
                "n_episodes": len(eps), "n_episodes_size3": sum(e["size"] >= 3 for e in eps),
                "max_lifetime_s": max(life) if life else 0.0, "n_persistent": sum(x >= PERSIST for x in life),
                "max_size": max((e["size"] for e in eps), default=0), "episodes": eps,
                "max_overlap_all_m": ov_all, "wall_s": time.perf_counter() - w0})
    for k in keys:
        out[f"peak_{k}"] = max((e[k] for e in eps), default=0.0)
    return out


def jobs():
    return [{"job_id": f"dt{dt:g}|seed{s}", "seed": s, "dt": dt, "t_max": T_MAX} for dt in DTS for s in SEEDS]


def analyse():
    R = revlib.load_runs(OUT)
    out = {"doc": __doc__, "by_dt": {}}
    for dt in DTS:
        Q = [r for r in R if abs(r["dt"] - dt) < 1e-12]
        if not Q:
            continue
        out["by_dt"][f"{dt:g}"] = {
            "n": len(Q), "runs_with_arch": sum(r["n_episodes"] > 0 for r in Q),
            "episodes": sum(r["n_episodes"] for r in Q), "episodes_size3": sum(r["n_episodes_size3"] for r in Q),
            "max_size": max(r["max_size"] for r in Q), "max_lifetime_s": max(r["max_lifetime_s"] for r in Q),
            "persistent": sum(r["n_persistent"] for r in Q), "complete": sum(r["complete"] for r in Q),
            "deadlock": sum(r["deadlock"] for r in Q),
            "peak_body_force_kN": max(r["peak_body_force_N"] for r in Q) / 1e3,
            "peak_contact_force_kN": max(r["peak_max_contact_force_N"] for r in Q) / 1e3,
            "peak_wall_force_kN": max(r["peak_max_wall_force_N"] for r in Q) / 1e3,
            "max_overlap_arch_m": max(r["peak_max_overlap_m"] for r in Q),
            "max_wall_overlap_arch_m": max(r["peak_max_wall_overlap_m"] for r in Q),
            "max_overlap_all_m": max(r["max_overlap_all_m"] for r in Q),
            "median_evac_s": float(np.median([r["t_end"] for r in Q if r["complete"]])) if any(r["complete"] for r in Q) else None}
    revlib.out_json("B4", out)
    print(json.dumps(out["by_dt"], indent=1))


if __name__ == "__main__":
    if sys.argv[1:2] == ["analyse"]:
        analyse()
    else:
        a = qargs.parse()
        run_jobs(qargs.select(jobs(), a), run, a.out or OUT, workers=a.workers, log_every=1)
