"""E1 follow-up: keystone test (plan change C12). Residual geometry classified by snapshot surgery.

For each E1 deadlock snapshot (data/E1/library, 393 = 197 E1a + 196 E1b), restarted in its own
mode's flags (E1a: all default; E1b: corrected-forward), C1, sigma = 0, dt = 0.01 s, window 120 s,
stopped early once stationary (StationaryDetector(hold=10, v_thr=1e-3): every active |v| < 1e-3 m/s
for 10 s with no exit), as in the pilot quench (experiments/pilot/w22_quench.py).

  blocker  residual agent nearest the door centre (10, 5) (same definition as e1_analyze.py).
  K1  "blocker alone": every residual agent except the blocker is deactivated (removed from the
      world exactly as an exited agent is). held = the blocker has not exited at the end of the run.
  K2  "blocker removed": only the blocker is deactivated. Records which other residual agents exit
      within the window and which do not.
  K1b (only when K1 held and K2 left agents behind): K1 repeated on the K2-held agent nearest the
      door centre ("second trap").

Classes:
  lone_keystone             K1 held and K2 all exit;
  lone_keystone_second_trap K1 held and K2 some held (K1b result recorded);
  collective                K1 freed: the blocker is not held when alone (e.g. a pair standoff).

At the end of K1 the blocker's rest-state force balance is recorded: the code's wall force and the
C1 goal drive m v_eff / tau at the alone density (rho = 0 -> Weidmann factor at rho = 0.01).

Output: data/E1/keystone.jsonl (job_id "<mode>_seed<N>|K1" / "|K2" / "|K1b"); resumable.
Summary: data/derived/E1_keystone.json (written by summarise(); run with --summary to redo only that).
"""
import json
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import (DERIVED, EDATA, MODE_FLAGS, StationaryDetector, load_runs, restore,  # noqa: E402
                   run_jobs, runs_path, snap_path, weidmann_factor, wilson)
import numpy as np  # noqa: E402

T_Q = 120.0
DOOR = np.array([10.0, 5.0])
OUT = os.path.join(EDATA, "keystone.jsonl")


def nearest(st, ids):
    return min(ids, key=lambda i: float(np.linalg.norm(st.positions[i] - DOOR)))


def blocker_balance(sim, b):
    """Wall force and C1 goal drive on agent b at the current state (agent assumed alone)."""
    st = sim.state
    Fw = sim.steering.wall_forces.compute_wall_forces(st, sim.world.walls)[b]
    e = st.goals[b] - st.positions[b]
    e = e / np.linalg.norm(e)
    fac = weidmann_factor(0.0, sim.params.get("weidmann_gamma", 1.913), sim.params.get("weidmann_rho_max", 5.4))
    Fd = st.masses[b] * st.desired_speeds[b] * fac / st.taus[b] * e
    return {"F_wall": Fw.tolist(), "F_drive_rest": Fd.tolist(), "F_net_rest": (Fw + Fd).tolist()}


def run(job):
    snap = pickle.load(open(job["snap"], "rb"))
    sim = restore(snap, "C1", flags=MODE_FLAGS[job["mode"]])
    st = sim.state
    resid = [int(i) for i in st.active_indices]
    b = nearest(st, resid)
    if job["test"] == "K1":
        keep = [b]
    elif job["test"] == "K1b":
        keep = [job["target"]]
    else:
        keep = [i for i in resid if i != b]
    drop = [i for i in resid if i not in keep]
    if drop:
        st.deactivate(np.array(drop, int))
    t0, w0 = sim.time, time.perf_counter()
    exits = {}
    det = StationaryDetector(hold=10.0, v_thr=1e-3)
    stationary = False
    for _ in range(int(round(T_Q / sim.params["dt"]))):
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
    held = [i for i in keep if i not in exits]
    out = {k: v for k, v in job.items() if k != "snap"}
    out.update({"snap": os.path.basename(job["snap"]), "residual": resid, "blocker": b, "kept": keep,
                "exits": exits, "held": held, "stationary_stop": stationary, "t_run": sim.time - t0,
                "max_speed_end": float(np.linalg.norm(st.velocities[st.active], axis=1).max()) if st.n_active else 0.0,
                "final_pos": {int(i): st.positions[i].tolist() for i in keep if st.active[i]},
                "wall_s": time.perf_counter() - w0})
    if job["test"] in ("K1", "K1b") and held:
        out["balance_end"] = blocker_balance(sim, keep[0])
    return out


def snapshots():
    R = load_runs(runs_path())
    return sorted([r for r in R if r.get("snapshot")], key=lambda r: (r["mode"], r["seed"]))


def phase1_jobs(R):
    return [{"job_id": f"{r['mode']}_seed{r['seed']}|{t}", "mode": r["mode"], "seed": r["seed"],
             "snap": snap_path(r["snapshot"]), "test": t} for r in R for t in ("K1", "K2")]


def phase2_jobs(R, res):
    jobs = []
    for r in R:
        tag = f"{r['mode']}_seed{r['seed']}"
        k1, k2 = res.get(tag + "|K1"), res.get(tag + "|K2")
        if k1 and k2 and k1["held"] and k2["held"]:
            pos = {int(x["id"]): np.array(x["pos"]) for x in r["residual"]}
            tgt = min(k2["held"], key=lambda i: float(np.linalg.norm(pos[i] - DOOR)))
            jobs.append({"job_id": tag + "|K1b", "mode": r["mode"], "seed": r["seed"],
                         "snap": snap_path(r["snapshot"]), "test": "K1b", "target": int(tgt)})
    return jobs


def load_res():
    if not os.path.exists(OUT):
        return {}
    return {x["job_id"]: x for x in load_runs(OUT)}


def geometry(r, b):
    """Residual geometry at the snapshot: positions relative to the door, surface gaps to the blocker."""
    at = {a["id"]: a for a in r["attrs"]}
    pos = {int(x["id"]): np.array(x["pos"]) for x in r["residual"]}
    rows = []
    for i, p in sorted(pos.items(), key=lambda kv: float(np.linalg.norm(kv[1] - DOOR))):
        gap = None if i == b else float(np.linalg.norm(p - pos[b]) - at[i]["r"] - at[b]["r"])
        rows.append({"id": i, "x": float(p[0]), "dy": float(p[1] - 5.0), "d_door": float(np.linalg.norm(p - DOOR)),
                     "r": at[i]["r"], "margin_C1": at[i]["margin_C1"], "gap_to_blocker": gap})
    return rows


def summarise():
    R = snapshots()
    res = load_res()
    out = {"script": "experiments/E1/keystone.py", "doc": __doc__, "T_Q_s": T_Q,
           "stop": "StationaryDetector(hold=10 s, v_thr=1e-3 m/s)", "modes": {}}
    for mode in ("E1a", "E1b"):
        Rm = [r for r in R if r["mode"] == mode]
        cls, rows = {"lone_keystone": [], "lone_keystone_second_trap": [], "collective": [], "incomplete": []}, []
        for r in Rm:
            tag = f"{mode}_seed{r['seed']}"
            k1, k2, k1b = res.get(tag + "|K1"), res.get(tag + "|K2"), res.get(tag + "|K1b")
            if not (k1 and k2):
                cls["incomplete"].append(r["seed"])
                continue
            b = k1["blocker"]
            at = {a["id"]: a for a in r["attrs"]}
            if not k1["held"]:
                c = "collective"
            elif not k2["held"]:
                c = "lone_keystone"
            else:
                c = "lone_keystone_second_trap"
            cls[c].append(r["seed"])
            rows.append({"seed": r["seed"], "class": c, "blocker": b, "n_resid": len(k1["residual"]),
                         "blocker_margin_C1": at[b]["margin_C1"], "blocker_r": at[b]["r"],
                         "K1_held": bool(k1["held"]), "K1_exit_t": k1["exits"].get(str(b), k1["exits"].get(b)),
                         "K1_stationary": k1["stationary_stop"], "K1_balance_end": k1.get("balance_end"),
                         "K1_final_pos": k1["final_pos"].get(str(b), k1["final_pos"].get(b)),
                         "K2_held": k2["held"], "K2_n_others": len(k2["kept"]),
                         "K1b": None if not k1b else {"target": k1b["target"], "held": bool(k1b["held"]),
                                                      "target_margin_C1": at[k1b["target"]]["margin_C1"]},
                         "geometry": geometry(r, b)})
        n = sum(len(v) for k, v in cls.items() if k != "incomplete")
        summ = {"n_snapshots": len(Rm), "n_classified": n,
                "class_counts": {k: {"k": len(v), "wilson95": list(wilson(len(v), n))} for k, v in cls.items()
                                 if k != "incomplete"},
                "incomplete": cls["incomplete"]}
        coll = [x for x in rows if x["class"] == "collective"]
        summ["collective"] = {
            "n_resid_hist": {str(k): sum(x["n_resid"] == k for x in coll) for k in sorted({x["n_resid"] for x in coll})},
            "cases": [{k: x[k] for k in ("seed", "n_resid", "blocker_margin_C1", "K1_exit_t", "K2_held", "geometry")}
                      for x in coll]}
        st = [x for x in rows if x["class"] == "lone_keystone_second_trap"]
        summ["second_trap"] = {"K1b_held": sum(x["K1b"]["held"] for x in st if x["K1b"]),
                               "K1b_freed": sum(not x["K1b"]["held"] for x in st if x["K1b"]),
                               "K1b_missing": sum(x["K1b"] is None for x in st),
                               "cases": [{k: x[k] for k in ("seed", "n_resid", "K2_held", "K1b")} for x in st]}
        summ["negative_margin_blockers"] = [x for x in rows if x["blocker_margin_C1"] <= 0]
        summ["held_without_stationary_stop"] = [x["seed"] for x in rows
                                                if x["K1_held"] and not x["K1_stationary"]]
        summ["per_snapshot"] = [{k: x[k] for k in ("seed", "class", "blocker", "n_resid", "blocker_margin_C1",
                                                   "K1_held", "K2_held", "K1b")} for x in rows]
        out["modes"][mode] = summ
    json.dump(out, open(os.path.join(DERIVED, "E1_keystone.json"), "w"), indent=1, default=float)
    for mode, s in out["modes"].items():
        print(mode, s["n_classified"], {k: (v["k"], [round(z, 3) for z in v["wilson95"]])
                                         for k, v in s["class_counts"].items()},
              "second trap", {k: s["second_trap"][k] for k in ("K1b_held", "K1b_freed", "K1b_missing")},
              "collective n_resid", s["collective"]["n_resid_hist"])
        for x in s["negative_margin_blockers"]:
            print("   neg-margin", mode, x["seed"], x["class"], f"margin={x['blocker_margin_C1']:.1f}",
                  "K1 exit", x["K1_exit_t"], "K2 held", x["K2_held"])
    return out


if __name__ == "__main__":
    if "--summary" not in sys.argv:
        R = snapshots()
        lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
        out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else OUT
        R = R[:lim] if lim else R
        w1 = run_jobs(phase1_jobs(R), run, out, workers=4, log_every=50)
        res = {x["job_id"]: x for x in load_runs(out)}
        w2 = run_jobs(phase2_jobs(R, res), run, out, workers=4, log_every=10)
        print("wall phase1", w1, "phase2", w2)
        if out != OUT:
            sys.exit(0)
    summarise()
