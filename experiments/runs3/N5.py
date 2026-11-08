"""run-N5: contact-arch test at a finer time step and at lower drives.

Arch recorder of experiments/arch/arch.py (arch_check, unchanged: contact graph among agents within 1.5 m
of the door, jamb contacts, arch = contact component touching both jambs; checks every 0.1 s; episode
lifetime; persistent >= 10 s), C1, corrected-forward flags (CF), w = 0.8 m, 100 agents, seeds 42-66 (25,
as arch.py), up to 600 s, stop at completion or stationary deadlock (every active |v| < 0.01 m/s for 10 s).
Cells (25 runs each):
  dt0.0025_v5   mean desired speed 5 m/s (as arch.py), dt = 0.0025 s
  v3, v2        mean desired speed 3 and 2 m/s, dt = 0.01 s
  default       the default desired-speed distribution, dt = 0.01 s
At a stationary deadlock the residual agents near the door are checked once more for an arch (contact
at the stop).
Output: data/N5/n5.jsonl (job_id "<cell>|seed<N>"), resumable.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3 import CF, out_dir, qargs, run_jobs  # noqa: E402
import arch  # noqa: E402
from w2lib import StationaryDetector, build  # noqa: E402

OUT = os.path.join(out_dir("N5"), "n5.jsonl")
CELLS = {"dt0.0025_v5": (5.0, 0.0025), "v3": (3.0, 0.01), "v2": (2.0, 0.01), "default": (None, 0.01)}
SEEDS = range(42, 67)
T_MAX = 600.0
CHECK_S = 0.1


def run(job):
    w0 = time.perf_counter()
    fl = dict(CF, dt=job["dt"])
    if job["v0_mean"] is not None:
        fl["speed_mean"] = job["v0_mean"]
    sim = build("C1", seed=job["seed"], width=0.8, noise=0.0, flags=fl)
    every = int(round(CHECK_S / sim.params["dt"]))
    det = StationaryDetector(hold=10.0, v_thr=0.01, every=every)
    eps, cur, deadlock = [], None, False
    n_checks = n_arch = n_arch3 = 0
    while sim.time < job["t_max"] - 1e-9 and sim.state.n_active > 0:
        sim.step()
        if sim.step_count % every == 0:
            n_checks += 1
            a = arch.arch_check(sim)
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
    out = {**job, "flags": fl, "complete": st.n_active == 0, "deadlock": deadlock, "t_end": sim.time,
           "n_remaining": int(st.n_active), "evacuation_time": sim.time if st.n_active == 0 else None,
           "n_checks": n_checks, "frac_checks_arch": n_arch / max(n_checks, 1),
           "frac_checks_arch3": n_arch3 / max(n_checks, 1), "n_episodes": len(eps),
           "n_episodes_size3": sum(e["size"] >= 3 for e in eps), "max_lifetime_s": max(life) if life else 0.0,
           "n_persistent": sum(x >= arch.PERSIST for x in life), "episodes": eps,
           "arch_at_stop": arch.arch_check(sim) if deadlock else None, "wall_s": time.perf_counter() - w0}
    if st.n_active:
        out["residual"] = [{"id": int(i), "pos": st.positions[i].tolist(), "r": float(st.radii[i])}
                           for i in st.active_indices]
    return out


def jobs():
    return [{"job_id": f"{c}|seed{s}", "cell": c, "seed": s, "v0_mean": v0, "dt": dt, "t_max": T_MAX}
            for c, (v0, dt) in CELLS.items() for s in SEEDS]


def main(argv=None):
    a = qargs.parse(argv)
    return run_jobs(qargs.select(jobs(), a), run, a.out or OUT, workers=a.workers, log_every=5)


if __name__ == "__main__":
    print("wall", main())
