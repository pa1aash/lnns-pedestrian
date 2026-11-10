"""B1: converse of the stuck-alone criterion g_max(r) > m v0/tau (Eq. (stuck)).

Population: the spawned agents of the E1b whole runs (data/E1/E1_runs.jsonl, mode E1b; attrs r, v0, tau,
m = 80 kg), with the stuck-alone margin g_max(r) - m v0/tau of experiments/lib/w2lib.Passability (default
walls A_w = 2000 N, B_w = 0.08 m, sharp edges, w = 0.8 m, rho = 0 so v_eff = v0).
Samples: 200 agents with negative margin and 200 with positive margin, each spread over the margin: the
agents of that sign sorted by (margin, run seed, id), ranks round(linspace(0, n - 1, 200)).
Placement (alone, at rest, on the door axis y = 5, goal (11, 5) as in the bottleneck scenario):
  positive margin  at the rest state: the first x upstream of the door plane where the backward wall force
                   equals the drive (the stable equilibrium on the rising side of the profile);
  negative margin  no rest state exists on the axis; the agent is placed at the axial position of g_max(r),
                   where the backward force is largest, and (start "upstream") 1.0 m upstream of it.
Run: C1, CF flags, dt = 0.01 s, 60 s, one agent active; "pass" = the agent's centre reaches x >= 10 (door
plane) or the agent exits. Output data/revision/B1/b1.jsonl (job_id "<sign>|<rank>|<start>"), resumable.
Usage: B1_converse.py [qargs options]   |   B1_converse.py analyse
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import CF, np, run_jobs  # noqa: E402
import qargs  # noqa: E402
from e1lib import load_runs, runs_path  # noqa: E402
from w2lib import Passability, build, wall_backward_profile  # noqa: E402

OUT = os.path.join(revlib.data_dir("B1"), "b1.jsonl")
N_S, T_RUN, M = 200, 60.0, 80.0
P = Passability(0.8)


def population():
    rows = []
    for r in load_runs(runs_path()):
        if r["mode"] != "E1b":
            continue
        for a in r["attrs"]:
            rows.append({"seed": r["seed"], "id": a["id"], "r": a["r"], "v0": a["v0"], "tau": a["tau"],
                         "margin": P.margin(a["r"], a["v0"], a["tau"])})
    return rows


def sample(rows, sign):
    S = sorted([x for x in rows if (x["margin"] > 0) == (sign > 0)], key=lambda x: (x["margin"], x["seed"], x["id"]))
    idx = np.round(np.linspace(0, len(S) - 1, N_S)).astype(int)
    return [S[i] for i in idx], len(S)


def placement(r, drive):
    xs, fx = wall_backward_profile(r, xs=np.linspace(9.0, 10.0, 20001))
    back = -fx
    k = int(np.argmax(back))
    if back[k] > drive:
        j = int(np.argmax(back >= drive))      # first crossing from upstream
        return float(xs[j]), float(xs[k])
    return None, float(xs[k])


def jobs():
    rows = population()
    J = []
    for sign, name in ((-1, "neg"), (1, "pos")):
        S, n_pool = sample(rows, sign)
        for k, a in enumerate(S):
            drive = M * a["v0"] / a["tau"]
            x_rest, x_peak = placement(a["r"], drive)
            starts = {"rest": x_rest} if sign > 0 else {"peak": x_peak, "upstream": x_peak - 1.0}
            for st, x0 in starts.items():
                J.append({"job_id": f"{name}|{k}|{st}", "sign": name, "rank": k, "start": st, "x0": x0,
                          "x_peak": x_peak, "n_pool": n_pool, "t_max": T_RUN, **a, "drive_N": drive})
    return J


def run(job):
    w0 = time.perf_counter()
    sim = build("C1", seed=0, width=0.8, n_agents=1, flags=dict(CF))
    st = sim.state
    st.positions[0] = [job["x0"], 5.0]
    st.velocities[0] = 0.0
    st.radii[0], st.desired_speeds[0], st.taus[0], st.masses[0] = job["r"], job["v0"], job["tau"], M
    t_pass, xmax = None, job["x0"]
    for _ in range(int(round(job["t_max"] / sim.params["dt"]))):
        sim.step()
        st = sim.state
        if not st.active[0] or st.positions[0, 0] >= 10.0:
            t_pass = sim.time
            break
        xmax = max(xmax, float(st.positions[0, 0]))
    out = dict(job)
    out.update({"passed": t_pass is not None, "t_pass": t_pass, "x_final": float(st.positions[0, 0]),
                "y_final": float(st.positions[0, 1]), "x_max": xmax,
                "speed_final": float(np.linalg.norm(st.velocities[0])), "wall_s": time.perf_counter() - w0})
    return out


def analyse():
    R = revlib.load_runs(OUT)
    out = {"doc": __doc__}
    for sign in ("neg", "pos"):
        for st in sorted({r["start"] for r in R if r["sign"] == sign}):
            Q = [r for r in R if r["sign"] == sign and r["start"] == st]
            k = sum(r["passed"] for r in Q)
            p, lo, hi = revlib.wilson(k, len(Q))
            tp = [r["t_pass"] for r in Q if r["passed"]]
            fail = [r for r in Q if r["passed"] != (sign == "neg")]
            out[f"{sign}_{st}"] = {"n": len(Q), "passed": k, "frac": p, "ci95": [lo, hi], "n_pool": Q[0]["n_pool"],
                                   "margin_range_N": [min(r["margin"] for r in Q), max(r["margin"] for r in Q)],
                                   "t_pass_median_s": float(np.median(tp)) if tp else None,
                                   "t_pass_max_s": max(tp) if tp else None,
                                   "exceptions": [{k2: r[k2] for k2 in ("job_id", "margin", "r", "v0", "tau", "x0",
                                                                        "x_final", "x_max")} for r in fail]}
    revlib.out_json("B1", out)
    print(json.dumps({k: {a: b for a, b in v.items() if a != "exceptions"} | {"n_exc": len(v["exceptions"])}
                      for k, v in out.items() if k != "doc"}, indent=1))


if __name__ == "__main__":
    if sys.argv[1:2] == ["analyse"]:
        analyse()
    else:
        a = qargs.parse()
        run_jobs(qargs.select(jobs(), a), run, a.out or OUT, workers=a.workers, log_every=50)
