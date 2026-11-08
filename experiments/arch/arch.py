"""Contact arches at high drive (paper Sect. 5.3; production version of the wave-2 pilot W2.9,
wave2/scripts/w29_contact.py in the plan root, which ran 5 seeds for 300 s).

Corrected-forward (CF) flags, C1, room bottleneck w = 0.8 m, 100 agents, mean desired speed 5 m/s (the pilot's
highest drive; scenario flag speed_mean, std as published), seeds 42-66 (25), up to 600 s, stopped at
completion or at a stationary deadlock (every active |v| < 0.01 m/s for 10 s, no exit).

Every 0.1 s (10 steps), among the active agents within 1.5 m of the door centre (10, 5) and with x < 10.3:
  contact graph   edge i-j if the bodies overlap (r_i + r_j > d_ij);
  jamb contact    distance to the lower / upper jamb segment < r_i;
  arch            a connected contact component that touches both jambs (chain from jamb to jamb),
                  any size >= 1 (a single agent touching both jambs counts); size >= 3 also recorded.
An arch episode is a run of consecutive checks with an arch present; its lifetime is t_last - t_first.
A persistent arch is an episode lasting >= 10 s.
Recorded per episode: start, lifetime, largest size, largest total body force k * sum(overlap) in the
component (k = 1.2e5 kg/s^2), and the largest relative tangential speed between contacting members.
Output: data/arch/arch.jsonl (job_id "v5|seed<N>"), resumable.
Usage: arch.py [--workers 2]
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
from e1lib import CF, DATA, StationaryDetector, build, run_jobs  # noqa: E402
import numpy as np  # noqa: E402
from scipy.sparse.csgraph import connected_components  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402

K = 120000.0
V0 = 5.0
T_MAX = 600.0
EVERY = 10
PERSIST = 10.0
OUT = os.path.join(DATA, "arch", "arch.jsonl")


def arch_check(sim):
    st = sim.state
    a = st.active_indices
    P = st.positions[a]
    m = (np.linalg.norm(P - [10.0, 5.0], axis=1) < 1.5) & (P[:, 0] < 10.3)
    ids = a[m]
    if len(ids) == 0:
        return None
    P, r, V = st.positions[ids], st.radii[ids], st.velocities[ids]
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
            cc = np.ix_(comp, comp)
            load = float(K * np.sum(np.maximum(ov[cc], 0.0)) / 2)
            vt = 0.0
            for i, j in zip(*np.where(np.triu(C[cc], 1))):
                gi, gj = np.where(comp)[0][i], np.where(comp)[0][j]
                nvec = (P[gj] - P[gi]) / D[gi, gj]
                t = np.array([-nvec[1], nvec[0]])
                vt = max(vt, abs(float(np.dot(V[gj] - V[gi], t))))
            rec = {"size": int(comp.sum()), "body_force_N": load, "max_rel_vt": vt}
            if best is None or rec["size"] > best["size"]:
                best = rec
    return best


def run(job):
    w0 = time.perf_counter()
    sim = build("C1", seed=job["seed"], width=0.8, noise=0.0, flags={**CF, "speed_mean": V0})
    det = StationaryDetector(hold=10.0, v_thr=0.01)
    eps, cur, deadlock = [], None, False
    n_checks = n_arch = n_arch3 = 0
    while sim.time < T_MAX - 1e-9 and sim.state.n_active > 0:
        sim.step()
        if sim.step_count % EVERY == 0:
            n_checks += 1
            a = arch_check(sim)
            if a:
                n_arch += 1
                n_arch3 += a["size"] >= 3
                if cur is None:
                    cur = {"t0": sim.time, "t1": sim.time, **a}
                else:
                    cur["t1"] = sim.time
                    cur["size"] = max(cur["size"], a["size"])
                    cur["body_force_N"] = max(cur["body_force_N"], a["body_force_N"])
                    cur["max_rel_vt"] = max(cur["max_rel_vt"], a["max_rel_vt"])
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
    out = {**job, "v0_mean": V0, "flags": {**CF, "speed_mean": V0}, "complete": st.n_active == 0,
           "deadlock": deadlock, "t_end": sim.time, "n_remaining": int(st.n_active),
           "evacuation_time": sim.time if st.n_active == 0 else None,
           "n_checks": n_checks, "frac_checks_arch": n_arch / max(n_checks, 1),
           "frac_checks_arch3": n_arch3 / max(n_checks, 1),
           "n_episodes": len(eps), "n_episodes_size3": sum(e["size"] >= 3 for e in eps),
           "max_lifetime_s": max(life) if life else 0.0,
           "n_persistent": sum(x >= PERSIST for x in life), "episodes": eps,
           "wall_s": time.perf_counter() - w0}
    if st.n_active:
        act = st.active_indices
        out["residual"] = [{"id": int(i), "pos": st.positions[i].tolist(), "r": float(st.radii[i])} for i in act]
    return out


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 2
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    jobs = [{"job_id": f"v5|seed{s}", "seed": s} for s in range(42, 67)]
    print("wall", run_jobs(jobs, run, OUT, workers=workers, log_every=1))


if __name__ == "__main__":
    main()
