"""A12 (revision 3): largest body overlaps in default-speed room runs and in the CroMa runs (dt = 0.01 s).

No stored run (E1b, E7, B2, E10, D3) logs overlaps, so a sample is rerun in one process with a per-step recorder.
  room   C1, CF flags (the E1b mode: w2_numerics fixed, spawn rejection, corner rule convex_union), w = 0.8 m,
         100 agents, default desired speeds, seeds 42-51, built with experiments/lib/w2lib.build, 600 s cap, stop at
         stationary deadlock (w2lib.StationaryDetector), as experiments/E1/e1_library.py.
  croma  D3 cells C1_cf and C3_rvo2_cf (force-coupled ORCA, RVO2), seeds 42-46 (one run of each CroMa run type
         4D030 ... 4D130), jobs from experiments/revision/D3_croma_rerun.py (passed-participant N, L = 2.0 / 0.2 m),
         scenario and stop rule of experiments/E10/e10_croma.py run() (trajectory file and estimator left out).
After every step, over active agents:
  agent-agent overlap  max_{i<j} (r_i + r_j - d_ij)
  wall overlap         max_i (r_i - min_W (d_iW - rad_W)), d_iW the distance to wall segment W (sim.core.world)
Per run: the maximum over steps of each (and when / which radii), the agent-agent maximum over t >= 1 s (spawn
transient left out: the closest pair at the start is the rejection-sampled spawn), the number of steps with an agent-agent overlap
> 0, > 0.01 m, > 0.05 m, and the median and 99th percentile of the per-step maxima. Reproduction check: t_end and
completion / deadlock equal the stored E1b and D3 records.
Summary per set: max, 99th percentile and median of the per-run maxima (numpy linear percentile).
CPU time: time.process_time() per run.
Output: data/revision2/A12/a12.jsonl (resumable), data/derived/rev2_A12.json.
Usage: A12_overlap.py run | A12_overlap.py analyse
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rev2lib import CF, ROOT, data_dir, np, out_json  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments", "revision"))
import D3_croma_rerun as D3  # noqa: E402
from w2lib import Simulation, StationaryDetector, build  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402
from sim.scenarios.croma import CromaBottleneckScenario  # noqa: E402

OUT = os.path.join(data_dir("A12"), "a12.jsonl")
ROOM_SEEDS = range(42, 52)
CROMA_SEEDS = range(42, 47)
T_MAX = 600.0
T_LATE = 1.0


def overlaps(sim):
    st = sim.state
    a = st.active_indices
    if len(a) == 0:
        return -np.inf, -np.inf, None
    P, r = st.positions[a], st.radii[a]
    if len(a) > 1:
        D = np.linalg.norm(P[:, None] - P[None], axis=2)
        ov = r[:, None] + r[None] - D
        iu = np.triu_indices(len(a), 1)
        k = int(np.argmax(ov[iu]))
        oa, pair = float(ov[iu][k]), (int(a[iu[0][k]]), int(a[iu[1][k]]))
    else:
        oa, pair = -np.inf, None
    d, _ = agents_to_walls(P, sim.world.walls)
    d = d - np.array([w.radius for w in sim.world.walls])[None]
    ow = float(np.max(r - d.min(axis=1)))
    return oa, ow, pair


def record(sim, det, t_max):
    st = sim.state
    per_a, per_w = [], []
    best = {"ov": -np.inf}
    deadlock = False
    while sim.time < t_max - 1e-9 and st.n_active > 0:
        sim.step()
        st = sim.state
        oa, ow, pair = overlaps(sim)
        per_a.append(oa)
        per_w.append(ow)
        if oa > best["ov"]:
            best = {"ov": oa, "t": sim.time, "pair": pair, "radii": [float(st.radii[i]) for i in pair],
                    "pos": [st.positions[i].tolist() for i in pair], "n_active": int(st.n_active)}
        if det.update(sim):
            deadlock = True
            break
    A = np.array([x for x in per_a if np.isfinite(x)])
    W = np.array(per_w)
    k1 = int(round(T_LATE / sim.params["dt"]))  # steps with t >= T_LATE (the spawn transient left out)
    AL = np.array([x for x in per_a[k1 - 1:] if np.isfinite(x)])
    return {"t_end": sim.time, "complete": st.n_active == 0, "deadlock": deadlock, "n_remaining": int(st.n_active),
            "n_steps": len(per_a), "max_agent_overlap_m": float(A.max()), "max_agent": best,
            "max_wall_overlap_m": float(W.max()),
            "max_agent_overlap_late_m": float(AL.max()) if len(AL) else None,
            "t_max_agent_late": float(sim.params["dt"]) * (k1 + int(np.argmax(per_a[k1 - 1:]))) if len(AL) else None, "t_max_wall": float(sim.params["dt"]) * (1 + int(np.argmax(W))),
            "steps_ov_gt0": int((A > 0).sum()), "steps_ov_gt1cm": int((A > 0.01).sum()),
            "steps_ov_gt5cm": int((A > 0.05).sum()),
            "per_step_max_median_m": float(np.median(A)), "per_step_max_p99_m": float(np.percentile(A, 99)),
            "wall_per_step_max_median_m": float(np.median(W)), "dt": sim.params["dt"]}


def room(seed):
    sim = build("C1", seed=seed, width=0.8, flags=dict(CF))
    return record(sim, StationaryDetector(), T_MAX)


def croma(job):
    sc = CromaBottleneckScenario(job["N"], 0.8, job["L"])
    sim = Simulation.from_scenario(sc, job["config"], seed=job["seed"],
                                   param_overrides={**job["flags"], "w2_metrics": "light"})
    sim.velocity_noise_std = job.get("sigma", 0.0)
    return record(sim, StationaryDetector(), job["t_max"])


def jobs():
    J = [{"job_id": f"room|seed{s}", "set": "room", "seed": s} for s in ROOM_SEEDS]
    for j in D3.jobs("unused"):
        if j["cell"] in ("C1_cf", "C3_rvo2_cf") and j["seed"] in CROMA_SEEDS:
            J.append({**{k: v for k, v in j.items() if k != "raw_dir"}, "set": j["cell"]})
    return J


def run():
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["job_id"] for l in open(OUT)}
    for j in jobs():
        if j["job_id"] in done:
            continue
        c0, w0 = time.process_time(), time.perf_counter()
        res = room(j["seed"]) if j["set"] == "room" else croma(j)
        res.update({k: j[k] for k in ("job_id", "set", "seed")}, cpu_s=time.process_time() - c0,
                   wall_s=time.perf_counter() - w0)
        for k in ("run", "N", "L", "cell", "config"):
            if k in j:
                res[k] = j[k]
        with open(OUT, "a") as f:
            f.write(json.dumps(res, default=float) + "\n")
        print(j["job_id"], round(res["max_agent_overlap_m"], 4), round(res["max_wall_overlap_m"], 4),
              round(res["cpu_s"]), flush=True)


def stored():
    ref = {}
    for l in open(os.path.join(ROOT, "data", "E1", "E1_runs.jsonl")):
        x = json.loads(l)
        if x["mode"] == "E1b" and x["seed"] in ROOM_SEEDS:
            ref[f"room|seed{x['seed']}"] = x
    for l in open(os.path.join(ROOT, "data", "revision", "D3", "d3_croma.jsonl")):
        x = json.loads(l)
        ref[x["job_id"]] = x
    return ref


def summ(v):
    v = np.asarray(v, float)
    return {"n": len(v), "max": float(v.max()), "p99": float(np.percentile(v, 99)), "median": float(np.median(v)),
            "min": float(v.min())}


def analyse():
    R = [json.loads(l) for l in open(OUT)]
    ref = stored()
    out = {"sets": {}, "cpu_s_total": sum(r["cpu_s"] for r in R), "n_runs": len(R)}
    out["cpu_h_total"] = out["cpu_s_total"] / 3600.0
    mism = []
    for r in R:
        s = ref[r["job_id"]]
        if abs(s["t_end"] - r["t_end"]) > 1e-6 or bool(s["complete"]) != r["complete"] or \
                bool(s["deadlock"]) != r["deadlock"]:
            mism.append(r["job_id"])
    out["reproduction_mismatch"] = mism
    for name in ("room", "C1_cf", "C3_rvo2_cf"):
        S = [r for r in R if r["set"] == name]
        if not S:
            continue
        mx = max(S, key=lambda r: r["max_agent_overlap_m"])
        out["sets"][name] = {
            "agent_overlap_run_max_m": summ([r["max_agent_overlap_m"] for r in S]),
            "agent_overlap_run_max_cm": {k: (100 * v if k != "n" else v) for k, v in
                                         summ([r["max_agent_overlap_m"] for r in S]).items()},
            "agent_overlap_late_run_max_cm": {k: (100 * v if k != "n" else v) for k, v in
                                              summ([r["max_agent_overlap_late_m"] for r in S]).items()},
            "wall_overlap_run_max_m": summ([r["max_wall_overlap_m"] for r in S]),
            "wall_overlap_run_max_cm": {k: (100 * v if k != "n" else v) for k, v in
                                        summ([r["max_wall_overlap_m"] for r in S]).items()},
            "per_step_max_median_cm": float(np.median([100 * r["per_step_max_median_m"] for r in S])),
            "per_step_p99_max_cm": float(max(100 * r["per_step_max_p99_m"] for r in S)),
            "n_runs_contact": int(sum(r["max_agent_overlap_m"] > 0 for r in S)),
            "n_runs_wall_contact": int(sum(r["max_wall_overlap_m"] > 0 for r in S)),
            "steps_gt5cm_total": int(sum(r["steps_ov_gt5cm"] for r in S)),
            "steps_gt1cm_total": int(sum(r["steps_ov_gt1cm"] for r in S)),
            "steps_total": int(sum(r["n_steps"] for r in S)),
            "largest": {k: mx[k] for k in ("job_id", "max_agent")},
            "largest_over_radius_sum": mx["max_agent"]["ov"] / sum(mx["max_agent"]["radii"]),
            "cpu_s": sum(r["cpu_s"] for r in S),
            "runs": {r["job_id"]: {k: r[k] for k in ("max_agent_overlap_m", "max_agent_overlap_late_m", "max_wall_overlap_m", "t_end", "complete",
                                                       "deadlock", "steps_ov_gt5cm", "cpu_s")} for r in S}}
    print(json.dumps({k: v for k, v in out.items()}, indent=1, default=float)[:6000])
    print(out_json("A12", out))


if __name__ == "__main__":
    {"run": run, "analyse": analyse}[sys.argv[1] if len(sys.argv) > 1 else "run"]()
