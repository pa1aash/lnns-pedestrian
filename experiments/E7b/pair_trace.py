"""C26 link: ORCA's constraint part on each member of the E7b pair standoffs, measured as in the E2
second-trap diagnosis (experiments/E2/second_trap.py, split_at), so the two can be compared directly.

For each of the 46 pair snapshots and each member b (lower, upper), the snapshot is restored under C3 with
CF union {B_w: 0.04} union {w2_orca: rvo2} and integrated for 20 s (dt = 0.01 s, or until b exits). At every
step ORCA's force on b splits into drive m (v_pref - v)/tau_ORCA and constraint m (v_ORCA - v_pref)/tau_ORCA;
the door-ward (+x) components are recorded, with the part due to the partner's half-plane (v_ORCA with and
without the partner). Summaries as in E2: time-mean and extreme door-ward constraint force, time-mean
cancellation fraction -F_cons,x / F_drive,x, fraction of steps with cancellation > 0.5, and whether b exits.
Geometry at the snapshot: member positions, centre distance, surface gap, |y - 5|, x offset of the partner.
Output: data/E7b/e7b_pair_trace.jsonl (job_id "<tag>|<member side>"), resumable.
"""
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(HERE), "lib")
sys.path.insert(0, LIB)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "E2"))
from e1lib import CF, DATA, run_jobs  # noqa: E402
from w2lib import restore  # noqa: E402
import numpy as np  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402
from second_trap import split_at  # noqa: E402

OUT = os.path.join(DATA, "E7b", "e7b_pair_trace.jsonl")
T_TRACE = 20.0
FLAGS = {**CF, "B_w": 0.04, "w2_orca": "rvo2"}


def run(job):
    w0 = time.perf_counter()
    snap = pickle.load(open(job["snap"], "rb"))
    sim = restore(snap, "C3", flags=dict(FLAGS))
    st = sim.state
    ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
    b = ids[0] if job["member"] == "lower" else ids[-1]
    o = [i for i in ids if i != b][0]
    P = st.positions
    d = float(np.linalg.norm(P[b] - P[o]))
    geom = {"pos": P[b].tolist(), "partner_pos": P[o].tolist(), "dist_m": d,
            "gap_m": d - float(st.radii[b] + st.radii[o]), "axis_dist_m": float(abs(P[b, 1] - 5.0)),
            "partner_dx_m": float(P[o, 0] - P[b, 0])}
    x0 = float(P[b, 0])
    T = []
    n_max = int(round(T_TRACE / sim.params["dt"]))
    for _ in range(n_max):
        T.append(split_at(sim, b, "rvo2"))
        sim.step()
        if not sim.state.active[b] or sim.state.positions[b, 0] >= 10.0:
            break
    dr = np.array([t["drive_x"] for t in T])
    co = np.array([t["cons_x"] for t in T])
    tr = np.array([t["trapped_dFx"] for t in T])
    ok = np.abs(dr) > 1e-6
    cf = np.where(ok, -co / np.where(ok, dr, 1.0), 0.0)
    return {"job_id": job["job_id"], "tag": job["tag"], "member": job["member"], "id": b, "partner": o,
            "geom": geom, "steps": len(T), "exited": len(T) < n_max,
            "cons_x_t0": float(co[0]), "cons_x_mean": float(co.mean()), "cons_x_min": float(co.min()),
            "t_cons_min": int(np.argmin(co)) * 0.01, "drive_x_mean": float(dr.mean()),
            "partner_dFx_mean": float(tr.mean()), "cancel_frac_mean": float(cf.mean()),
            "cancel_frac_max": float(cf.max()), "frac_steps_cancel_gt_half": float((cf > 0.5).mean()),
            "dx": float(sim.state.positions[b, 0] - x0), "wall_s": time.perf_counter() - w0}


def jobs():
    return [{"job_id": f"{p['tag']}|{m}", "tag": p["tag"], "snap": p["snap"], "member": m}
            for p in pairs() for m in ("lower", "upper")]


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(qargs.select(jobs(), a), run, out, workers=a.workers, log_every=10)


if __name__ == "__main__":
    print("wall", main())
