"""B2: critical door width, densely sampled, with the arrival record needed for the parameter-free prediction.

Runs: SFM (C1), corrected-forward flags (CF), default walls, 100 agents, spawns as in the width runs of E7
(seeds 42-141, rejection spawn), w in {0.82, 0.84, ..., 0.96} m, 600 s cap, stop at deadlock (every active
|v| < 0.01 m/s for 10 s, no exit) or completion: the recorder of runlib.whole_run, unchanged, plus at each
agent's door arrival (first step with x > 9.4 and |y - 5| < 0.6, as whole_run's "arrive") the number of
other active agents with surface gap below 0.1 m ("n_touch") and with centre within 1.0 m ("n_1m") and the
number of active agents left ("n_active"). No snapshots are saved.
Output: data/revision/B2/b2.jsonl (job_id "w<width>|seed<seed>"), resumable.
Usage: B2_width.py [qargs options]        (analysis: B2_analyze.py)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import CF, np, run_jobs  # noqa: E402
import qargs  # noqa: E402
from runlib import get_pass  # noqa: E402
from w2lib import StationaryDetector, build  # noqa: E402

OUT = os.path.join(revlib.data_dir("B2"), "b2.jsonl")
WIDTHS = tuple(round(0.82 + 0.02 * k, 2) for k in range(8))
SEEDS = range(42, 142)


def run(job):
    seed, width, flags, t_max = job["seed"], job["width"], dict(job["flags"]), job["t_max"]
    w0 = time.perf_counter()
    P = get_pass(width, flags)
    sim = build("C1", seed=seed, width=width, noise=0.0, flags=flags)
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
        new = [int(i) for i in np.where(st.active & (x > 9.4) & (np.abs(y - 5.0) < 0.6))[0] if int(i) not in arrive]
        if new:
            a = st.active_indices
            for i in new:
                o = a[a != i]
                d = np.linalg.norm(st.positions[o] - st.positions[i], axis=1)
                gap = d - st.radii[o] - st.radii[i]
                arrive[i] = {"t": sim.time, "n_active": int(st.n_active), "order": len(arrive),
                             "n_touch": int((gap < 0.1).sum()), "n_1m": int((d < 1.0).sum())}
        for i in np.where(prev & ~st.active)[0]:
            exit_t[int(i)] = sim.time
        if det.update(sim):
            deadlock = True
            break
    res = dict(job)
    res.update({"t_end": sim.time, "complete": st.n_active == 0, "deadlock": deadlock,
                "capped": (not deadlock) and st.n_active > 0, "n_exits": len(exit_t), "n_remaining": int(st.n_active),
                "exit_t": exit_t, "arrive": arrive, "margin": margin,
                "attrs": [{"id": i, "r": float(st.radii[i]), "v0": float(st.desired_speeds[i]),
                           "tau": float(st.taus[i])} for i in range(st.n)],
                "residual": [int(i) for i in st.active_indices], "wall_s": time.perf_counter() - w0})
    return res


def jobs():
    return [{"job_id": f"w{w:.2f}|seed{s}", "seed": s, "width": w, "flags": dict(CF), "t_max": 600.0}
            for w in WIDTHS for s in SEEDS]


if __name__ == "__main__":
    a = qargs.parse()
    run_jobs(qargs.select(jobs(), a), run, a.out or OUT, workers=a.workers, log_every=20)
