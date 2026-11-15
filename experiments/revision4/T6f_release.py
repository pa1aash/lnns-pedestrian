"""T6f (new computation; the records of B1 do not contain it): energy balance of the lone release 1 m upstream for
the positive-margin agents of B1.

Agents: the 200 positive-margin agents of experiments/revision/B1_converse.py (same sample rule; B1 released them
at their rest state only, 0 of 200 pass). Placement: alone, at rest, on the door axis y = 5, x0 = x_peak - 1.0 m
(x_peak = position of g_max on the axis, B1.placement); run as B1.run (C1, CF flags, dt = 0.01 s, 60 s, one agent).
Recorded per step (on-axis motion): x, v_x; then, with the code's on-axis wall profile back(x) = -F_wall,x
(w2lib.wall_backward_profile, 1e-4 m grid) and the drive D = m v0 / tau (rho = 0, v_eff = v0):
  x_rest, x_exit    first and last x around the peak where back(x) = D (the adverse region back > D)
  speed / KE at x_rest and at x_peak (first crossing; "not reached" if never), x_max, outcome (pass = x >= 10)
  wall potential difference U_w(x_peak) - U_w(x0) = int_{x0}^{x_peak} back dx, and U_w(x_max) - U_w(x0)
  adverse work A = int_{x_rest}^{x_exit} (back - D) dx (energy the agent must bring into the region at least)
  energy ledger from x0 to x_max: drive work D (x_max - x0), drag dissipation int m v^2 / tau dt, wall work,
  KE change (closes to the Euler-step error).
Output: data/revision4/T6f/t6f.jsonl (serial). Usage: T6f_release.py
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import CF, np  # noqa: E402
import B1_converse as B1  # noqa: E402
from w2lib import build, wall_backward_profile  # noqa: E402

OUT = os.path.join(rev4lib.data_dir("T6f"), "t6f.jsonl")
M = 80.0


def jobs():
    J = []
    for j in B1.jobs():
        if j["sign"] == "pos":
            J.append({**j, "job_id": f"pos|{j['rank']}|upstream1m", "start": "upstream1m", "x0": j["x_peak"] - 1.0})
    return J


def run(job):
    w0 = time.perf_counter()
    xs, fx = wall_backward_profile(job["r"], xs=np.linspace(8.0, 10.6, 26001))
    back = -fx
    D = M * job["v0"] / job["tau"]
    Uw = np.concatenate([[0.0], np.cumsum(0.5 * (back[1:] + back[:-1]) * np.diff(xs))])  # U_w(x) - U_w(8.0)
    uw = lambda x: float(np.interp(x, xs, Uw))  # noqa: E731
    k = int(np.argmax(back))
    adverse = np.where(back > D)[0]
    xr, xe = float(xs[adverse[0]]), float(xs[adverse[-1]])
    A = float(np.trapezoid((back - D)[adverse[0]:adverse[-1] + 1], xs[adverse[0]:adverse[-1] + 1]))
    sim = build("C1", seed=0, width=0.8, n_agents=1, flags=dict(CF))
    st = sim.state
    st.positions[0] = [job["x0"], 5.0]
    st.velocities[0] = 0.0
    st.radii[0], st.desired_speeds[0], st.taus[0], st.masses[0] = job["r"], job["v0"], job["tau"], M
    dt = sim.params["dt"]
    X, V = [job["x0"]], [0.0]
    passed = False
    for _ in range(int(round(job["t_max"] / dt))):
        sim.step()
        st = sim.state
        if not st.active[0]:
            passed = True
            break
        X.append(float(st.positions[0, 0])); V.append(float(st.velocities[0, 0]))
        if X[-1] >= 10.0:
            passed = True
            break
    X, V = np.array(X), np.array(V)

    def at(xc):
        i = np.where(X >= xc)[0]
        if not len(i):
            return None
        i = int(i[0])
        v = float(np.interp(xc, X[i - 1:i + 1], V[i - 1:i + 1])) if i > 0 else float(V[i])
        return {"t": float(i * dt), "speed": v, "KE_J": 0.5 * M * v * v}
    im = int(np.argmax(X))
    xm = float(X[im])
    drag = float(np.sum(M * V[:im + 1] ** 2 / job["tau"]) * dt)
    out = {k2: v for k2, v in job.items()}
    out.update({"D_N": D, "g_max_N": float(back[k]), "margin_N": float(back[k] - D), "x_rest": xr, "x_peak_grid": float(xs[k]),
                "x_exit": xe, "adverse_work_J": A, "at_x_rest": at(xr), "at_x_peak": at(float(xs[k])),
                "x_max": xm, "speed_final": float(abs(V[-1])), "x_final": float(X[-1]), "passed": passed,
                "dUw_x0_to_peak_J": uw(float(xs[k])) - uw(job["x0"]), "dUw_x0_to_xmax_J": uw(xm) - uw(job["x0"]),
                "dUw_x0_to_xrest_J": uw(xr) - uw(job["x0"]),
                "ledger_to_xmax": {"drive_work_J": D * (xm - job["x0"]), "drag_dissipation_J": drag,
                                   "wall_work_J": -(uw(xm) - uw(job["x0"])), "KE_at_xmax_J": 0.5 * M * V[im] ** 2},
                "max_KE_J": float(0.5 * M * np.max(V ** 2)), "wall_s": time.perf_counter() - w0})
    return out


if __name__ == "__main__":
    import json
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["job_id"] for l in open(OUT) if l.strip()}
    t0 = time.perf_counter()
    with open(OUT, "a") as f:               # serial, in-process (single-agent runs of seconds)
        for j in jobs():
            if j["job_id"] not in done:
                f.write(json.dumps(run(j), default=float) + "\n")
                f.flush()
    print("wall", time.perf_counter() - t0)
