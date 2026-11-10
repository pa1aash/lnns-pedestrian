"""Velocity-coupled ORCA (flag w2_orca_coupling = "velocity"), the corrected model, SFM+ORCA.

Parts (each resumable JSONL in data/velorca/, job_id as in the source experiment):
  lone    the 60 lone-trap snapshots of E2 (data/derived/selection.json), 120 s, deterministic stop as E2
          (every active |v| < 1e-3 m/s for 10 s, no exit), unperturbed and 5 replays at 1e-9 m (seeds
          900-904). Perturbations: vel_rvo2 (RVO2 solver), vel_pub (legacy linear-program solver).
          Runner: experiments/lib/runlib.quench via E2's quench_e2 (blocker freed within 120 s).
  pair    the 46 pair snapshots of E7b (experiments/E7b/e7b_pairs.py), flags as E7b (B_w = 0.04 m), the
          same perturbations, replays and stop. Runner: experiments/E7b/e7b_quench.run.
  whole   room, w = 0.8 m, 100 agents, seeds 242-341 (the spawns of E6a), 600 s, stop at deadlock (every
          active |v| < 0.01 m/s for 10 s, no exit). Variants vel (SFM + velocity-coupled ORCA, RVO2 solver)
          and sfm (SFM alone at the same seeds; E6a has no SFM run). Runner: runlib.whole_run.
  keystone  keystone test on the rebuilt final state (at rest) of every whole run that did not complete
          (as experiments/E6/keystone_e6.py): K0 (SFM holds the residual?), K0v (velocity-coupled ORCA, RVO2,
          holds it?), K1 blocker alone (SFM), K2 blocker removed (SFM), then K1b on the K2-held agent
          nearest the door when K1 and K2 both hold.
  dtprobe the snapshots freed in lone or pair (any perturbation), at dt in {0.005, 0.01, 0.02} s,
          unperturbed. Runs only if something was freed.
Usage: velorca.py lone|pair|whole|keystone|dtprobe  [qargs options]
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(EXP, "lib"))
sys.path.insert(0, os.path.join(EXP, "E2"))
sys.path.insert(0, os.path.join(EXP, "E7b"))
from e1lib import CF, DATA, load_runs, run_jobs  # noqa: E402
from runlib import whole_run  # noqa: E402
from w2lib import StationaryDetector, build, restore  # noqa: E402
import numpy as np  # noqa: E402
import qargs  # noqa: E402
import e2_quench  # noqa: E402
import e7b_quench  # noqa: E402
from e7b_pairs import pairs  # noqa: E402

OUT = os.path.join(DATA, "velorca")
P = {k: os.path.join(OUT, f"{k}.jsonl") for k in ("lone", "pair", "whole", "keystone", "dtprobe")}
VEL = {"w2_orca_coupling": "velocity"}
PERTURBATIONS = {"vel_rvo2": ("C3", {"w2_orca": "rvo2", **VEL}), "vel_pub": ("C3", {"w2_orca": "published", **VEL})}
PERTURB_SEEDS = (900, 901, 902, 903, 904)
T_Q = 120.0
SEEDS = range(242, 342)
DOOR = np.array([10.0, 5.0])
DTS = (0.005, 0.01, 0.02)


def jobs_lone():
    J = []
    for tag, snap, blk, cls in e2_quench.snapshots():
        for pert, (cfg, fl) in PERTURBATIONS.items():
            for ps in (None,) + PERTURB_SEEDS:
                J.append({"job_id": f"{tag}|{pert}|{'u' if ps is None else ps}", "snap": snap, "perturbation": pert,
                          "config": cfg, "flags": {**CF, **fl}, "deterministic": True, "perturb": ps,
                          "t_q": T_Q, "blocker": blk, "stratum": cls})
    return J


def jobs_pair():
    J = []
    for p in pairs():
        for pert, (cfg, fl) in PERTURBATIONS.items():
            for ps in (None,) + PERTURB_SEEDS:
                J.append({"job_id": f"{p['tag']}|{pert}|{'u' if ps is None else ps}", "snap": p["snap"],
                          "perturbation": pert, "config": cfg, "flags": {**e7b_quench.BASE, **fl}, "deterministic": True,
                          "perturb": ps, "delta": None, "t_q": T_Q})
    return J


def jobs_whole():
    V = {"vel": ("C3", {**CF, "w2_orca": "rvo2", **VEL}), "sfm": ("C1", dict(CF))}
    return [{"job_id": f"{v}|seed{s}", "variant": v, "seed": s, "width": 0.8, "flags": fl, "sigma": 0.0,
             "t_max": 600.0, "config": cfg} for v, (cfg, fl) in V.items() for s in SEEDS]


# --- keystone test on whole-run final states (pattern of experiments/E6/keystone_e6.py) ---
def rebuild(r, config, flags):
    sim = build(config, seed=r["seed"], width=0.8, noise=0.0, flags=dict(flags))
    st = sim.state
    pos = {int(x["id"]): np.array(x["pos"]) for x in r["residual"]}
    st.deactivate(np.array([i for i in range(st.n) if i not in pos], int))
    for i, p in pos.items():
        st.positions[i] = p
    st.velocities[:] = 0.0
    return sim, pos


def keystone(job):
    w0 = time.perf_counter()
    r = job["run"]
    if job["test"] == "K0v":
        sim, pos = rebuild(r, "C3", {**CF, "w2_orca": "rvo2", **VEL})
    else:
        sim, pos = rebuild(r, "C1", CF)
    st = sim.state
    resid = sorted(pos)
    b = min(pos, key=lambda i: float(np.linalg.norm(pos[i] - DOOR)))
    keep = {"K0": resid, "K0v": resid, "K1": [b], "K1b": [job.get("target")],
            "K2": [i for i in resid if i != b]}[job["test"]]
    drop = [i for i in resid if i not in keep]
    if drop:
        st.deactivate(np.array(drop, int))
    exits, stationary = {}, False
    det = StationaryDetector(hold=10.0, v_thr=1e-3)
    for _ in range(int(round(T_Q / sim.params["dt"]))):
        prev = st.active.copy()
        sim.step()
        st = sim.state
        for i in np.where(prev & ~st.active)[0]:
            exits[int(i)] = sim.time
        if st.n_active == 0:
            break
        if det.update(sim):
            stationary = True
            break
    out = {k: v for k, v in job.items() if k != "run"}
    out.update({"residual": resid, "blocker": b, "kept": keep, "exits": exits,
                "held": [i for i in keep if i not in exits], "stationary_stop": stationary,
                "wall_s": time.perf_counter() - w0})
    return out


def failures():
    return [r for r in load_runs(P["whole"]) if not r["complete"]] if os.path.exists(P["whole"]) else []


def jobs_keystone_1(R):
    return [{"job_id": f"{r['variant']}|seed{r['seed']}|{t}", "variant": r["variant"], "seed": r["seed"],
             "test": t, "run": r} for r in R for t in (["K0", "K1", "K2"] + (["K0v"] if r["variant"] == "vel"
                                                                               else []))]


def jobs_keystone_2(R, res):
    J = []
    for r in R:
        tag = f"{r['variant']}|seed{r['seed']}"
        k1, k2 = res.get(tag + "|K1"), res.get(tag + "|K2")
        if k1 and k2 and k1["held"] and k2["held"]:
            pos = {int(x["id"]): np.array(x["pos"]) for x in r["residual"]}
            tgt = min(k2["held"], key=lambda i: float(np.linalg.norm(pos[i] - DOOR)))
            J.append({"job_id": tag + "|K1b", "variant": r["variant"], "seed": r["seed"], "test": "K1b",
                      "target": int(tgt), "run": r})
    return J


# --- dt probe on freed snapshots ---
def dt_quench(job):
    snap = pickle.load(open(job["snap"], "rb"))
    sim = restore(snap, job["config"], flags=dict(job["flags"]), dt=job["dt"])
    st = sim.state
    resid = [int(i) for i in st.active_indices]
    t0, w0, exits, stationary = sim.time, time.perf_counter(), {}, False
    det = StationaryDetector(hold=10.0, v_thr=1e-3)
    for _ in range(int(round(job["t_q"] / job["dt"]))):
        prev = st.active.copy()
        sim.step()
        st = sim.state
        for i in np.where(prev & ~st.active)[0]:
            exits[int(i)] = sim.time - t0
        if st.n_active == 0:
            break
        if det.update(sim):
            stationary = True
            break
    out = {k: v for k, v in job.items() if k != "snap"}
    out.update({"snap": os.path.basename(job["snap"]), "residual": resid, "exits": exits,
                "n_freed": len(exits), "stationary_stop": stationary, "t_run": sim.time - t0,
                "wall_s": time.perf_counter() - w0})
    return out


def jobs_dtprobe():
    J = []
    for part in ("lone", "pair"):
        if not os.path.exists(P[part]):
            continue
        src = {j["job_id"]: j for j in (jobs_lone() if part == "lone" else jobs_pair())}
        freed = {}
        for r in load_runs(P[part]):
            ok = r.get("blocker_freed") if part == "lone" else r.get("freed")
            if ok:
                tag, pert, _ = r["job_id"].split("|")
                freed[(tag, pert)] = src[r["job_id"]]
        for (tag, pert), j in sorted(freed.items()):
            for dt in DTS:
                J.append({"job_id": f"{part}|{tag}|{pert}|dt{dt:g}", "part": part, "snap": j["snap"],
                          "perturbation": pert, "config": j["config"], "flags": j["flags"], "dt": dt, "t_q": T_Q})
    return J


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    part, a = argv[0], qargs.parse(argv[1:])
    os.makedirs(OUT, exist_ok=True)
    out = a.out or P[part]
    if part == "lone":
        return run_jobs(qargs.select(jobs_lone(), a), e2_quench.quench_e2, out, workers=a.workers, log_every=40)
    if part == "pair":
        return run_jobs(qargs.select(jobs_pair(), a), e7b_quench.run, out, workers=a.workers, log_every=40)
    if part == "whole":
        return run_jobs(qargs.select(jobs_whole(), a), whole_run, out, workers=a.workers, log_every=5)
    if part == "keystone":
        R = failures()
        run_jobs(qargs.select(jobs_keystone_1(R), a), keystone, out, workers=a.workers, log_every=20)
        res = {x["job_id"]: x for x in load_runs(out)} if os.path.exists(out) else {}
        return run_jobs(qargs.select(jobs_keystone_2(R, res), a), keystone, out, workers=a.workers,
                        log_every=20)
    if part == "dtprobe":
        J = jobs_dtprobe()
        print(f"[dtprobe] {len(J)} jobs (freed snapshot-perturbation pairs x {len(DTS)} dt)", flush=True)
        return run_jobs(qargs.select(J, a), dt_quench, out, workers=a.workers, log_every=10) if J else 0.0
    raise SystemExit(f"unknown part {part}")


if __name__ == "__main__":
    print("wall", main())
