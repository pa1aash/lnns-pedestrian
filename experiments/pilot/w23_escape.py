"""W2.3 activated escape from 5 library snapshots (C1, w=0.8).
Conditions: full (all residual agents mobile, noise on all), alone (others deactivated),
frozen (others present but reset to their frozen state every step: static obstacles).
Escape = blocker centre crosses the door plane x >= 10. Censor at T_CENS.
Also records the blocker's realised velocity moments while trapped (after 2 s burn-in,
x < 9.95) for the T_eff check, and runs the dt pilot (per_step vs dt_scaled; C3 quench).
Output: wave2/data/w23_escape.jsonl
"""
import os, pickle, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from w2lib import DATA, restore, run_jobs

T_CENS = 300.0


def run(job):
    snap = pickle.load(open(job["snap"], "rb"))
    b = job["blocker"]
    flags = dict(job.get("flags", {}))
    sim = restore(snap, job.get("config", "C1"), flags=flags, noise=job.get("sigma", 0.0),
                  noise_seed=job.get("noise_seed"), dt=job.get("dt"))
    st = sim.state
    others = [int(i) for i in st.active_indices if i != b]
    if job["cond"] == "alone":
        st.active[others] = False
    frozen_pos = st.positions[others].copy()
    t0 = sim.time
    dt = sim.params["dt"]
    w0 = time.perf_counter()
    mom = np.zeros(5)  # n, sum vx, sum vy, sum vx^2, sum vy^2
    t_cens = job.get("t_cens", T_CENS)
    esc = None
    other_exit_first = False
    nsteps = int(round(t_cens / dt))
    for k in range(nsteps):
        sim.step()
        st = sim.state
        if job["cond"] == "frozen":
            st.positions[others] = frozen_pos
            st.velocities[others] = 0.0
            st.active[others] = True
        x = st.positions[b, 0]
        if x >= 10.0 or not st.active[b]:
            esc = sim.time - t0
            break
        if job["cond"] == "full" and not other_exit_first and not st.active[others].all():
            other_exit_first = True
        if sim.time - t0 > 2.0 and x < 9.95:
            v = st.velocities[b]
            mom += (1.0, v[0], v[1], v[0] * v[0], v[1] * v[1])
    out = {k: v for k, v in job.items() if k != "snap"}
    out.update({"snap": os.path.basename(job["snap"]), "escape_t": esc, "censored": esc is None,
                "t_run": sim.time - t0, "dt": dt, "other_exit_first": other_exit_first,
                "v_moments": mom.tolist(), "wall_s": time.perf_counter() - w0})
    return out


def make_jobs(sel):
    jobs = []
    for k, (snap, b) in enumerate(sel):
        tag = os.path.basename(snap)[:-4]
        for cond in ("full", "alone", "frozen"):
            for sg in (0.04, 0.05, 0.07):
                for rep in range(20):
                    jobs.append({"job_id": f"{tag}|{cond}|s{sg}|{rep}", "kind": "restart", "snap": snap,
                                 "blocker": b, "cond": cond, "sigma": sg,
                                 "noise_seed": 11000 + 1000 * k + 100 * int(sg * 100) + rep})
        for dtv in (0.005, 0.01, 0.02):
            for mode in ("per_step", "dt_scaled"):
                for rep in range(10):
                    jobs.append({"job_id": f"{tag}|dt{dtv}|{mode}|{rep}", "kind": "dtpilot", "snap": snap,
                                 "blocker": b, "cond": "full", "sigma": 0.05, "dt": dtv,
                                 "flags": {"w2_noise": mode},
                                 "noise_seed": 51000 + 1000 * k + int(dtv * 1000) * 10 + rep + (500 if mode == "dt_scaled" else 0)})
            jobs.append({"job_id": f"{tag}|dt{dtv}|C3", "kind": "c3dt", "snap": snap, "blocker": b,
                         "cond": "full", "config": "C3", "dt": dtv, "t_cens": 120.0})
    return jobs


if __name__ == "__main__":
    import json
    sel = json.load(open(os.path.join(DATA, "w23_selected.json")))
    jobs = make_jobs([(s["snap"], s["blocker"]) for s in sel])
    if len(sys.argv) > 1:
        jobs = [j for j in jobs if j["kind"] == sys.argv[1]]
    wall = run_jobs(jobs, run, os.path.join(DATA, "w23_escape.jsonl"), workers=4, log_every=50)
    print("wall", wall)
