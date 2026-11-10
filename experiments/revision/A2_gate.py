"""A2: size of the ORCA density gate w_o = 1 - s(rho; 4, 2), s(x; x0, c) = 1 / (1 + exp(-c (x - x0))).

Density as the simulator computes it (code/sim/core/simulation.py, step 2): rho_i = N_i / (pi R^2), R = 3 m
(params neighbor_radius), N_i the other active agents within R (scipy KDTree.query_ball_point over the active
positions, self excluded). The gate uses rho_i as is (code/sim/steering/hybrid.py); the 0.01 m^-2 floor in
code/sim/steering/desired.py applies only to the Weidmann factor. The gate parameters are rho_orca_fade = 4.0
and k_orca_fade = 2.0 (code/config/params.yaml).

Computes
  snapshots  w_o of every active agent in the 60 E2 lone-trap snapshots (data/derived/selection.json "E2")
             and the 46 E7b pair snapshots (experiments/E7b/e7b_pairs.py), as at the first step of a quench:
             per library min and max over agents and snapshots, max N_i, and the 1 - w_o of the blocker /
             members (this is the factor by which the gate lowers ORCA's rest drive).
  bound      w_o at N = 99 (all other agents within R; rho = 99 / (9 pi) = 3.50 m^-2), the lowest value a
             100-agent run can reach; w_o at rho = 0.
  runs       summary of data/revision/A2/a2_runs.jsonl (experiments/revision/A2_runs.py: 10 reruns of the
             Sect. 6.2 force-coupled ORCA whole runs, seeds 242-251, per-step minimum of w_o over agents):
             min over runs, per-run minima, time fraction with some agent below 0.99, and a reproduction check
             against data/E6/e6a.jsonl.
Output: data/derived/rev_A2.json
"""
import math
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import DATA, DERIVED, ROOT, load_runs, sig  # noqa: E402
import json  # noqa: E402
import numpy as np  # noqa: E402
from scipy.spatial import KDTree  # noqa: E402
import e7b_pairs  # noqa: E402

R, X0, C = 3.0, 4.0, 2.0
AREA = math.pi * R * R


def w_o(rho):
    return 1.0 - 1.0 / (1.0 + np.exp(-C * (np.asarray(rho, float) - X0)))


def snap_gate(path):
    snap = pickle.load(open(path, "rb"))
    st = snap["state"]
    assert snap["params"]["neighbor_radius"] == R
    idx = np.where(st.active)[0]
    pos = st.positions[idx]
    nb = KDTree(pos).query_ball_point(pos, r=R)
    N = np.array([len(x) - 1 for x in nb])
    w = w_o(N / AREA)
    door = np.array([10.0, 5.0])
    blk = int(np.argmin(np.linalg.norm(pos - door, axis=1)))
    return {"n_active": int(len(idx)), "N_max": int(N.max()), "w_min": float(w.min()), "w_max": float(w.max()),
            "w_blocker": float(w[blk])}


def lib_summary(rows):
    return {"n_snapshots": len(rows), "n_agents": int(sum(r["n_active"] for r in rows)),
            "N_max": int(max(r["N_max"] for r in rows)), "w_min": min(r["w_min"] for r in rows),
            "w_max": max(r["w_max"] for r in rows), "one_minus_w_max": 1.0 - min(r["w_min"] for r in rows),
            "n_active_range": [min(r["n_active"] for r in rows), max(r["n_active"] for r in rows)]}


def main():
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]
    lone = [dict(snap_gate(os.path.join(ROOT, s["snap"])), tag=s["tag"]) for s in sel]
    pair = [dict(snap_gate(p["snap"]), tag=p["tag"]) for p in e7b_pairs.pairs()]
    o = {"definition": "w_o = 1 - 1/(1+exp(-2 (rho - 4))), rho = N/(9 pi) m^-2, N other active agents within 3 m; no floor",
         "w_at_rho0": float(w_o(0.0)), "one_minus_w_at_rho0": float(1 - w_o(0.0)),
         "snapshots": {"lone": lib_summary(lone), "pair": lib_summary(pair),
                       "per_snapshot": {"lone": lone, "pair": pair}}}
    rho_b = 99 / AREA
    o["bound"] = {"N": 99, "rho": rho_b, "rho_2sf": sig(rho_b, 3), "w_min": float(w_o(rho_b)),
                  "w_min_2sf": sig(float(w_o(rho_b)), 2), "s_at_bound": float(1 - w_o(rho_b))}
    # density at which w_o falls to 0.99 and the matching neighbour count
    rho99 = X0 + math.log(0.01 / 0.99) / C
    o["threshold_099"] = {"rho": rho99, "N": rho99 * AREA}
    p = os.path.join(DATA, "revision", "A2", "a2_runs.jsonl")
    if os.path.exists(p) and load_runs(p):
        E = {r["seed"]: r for r in load_runs(os.path.join(DATA, "E6", "e6a.jsonl"))}
        Rr = sorted(load_runs(p), key=lambda r: r["seed"])
        same = [abs(r["t_end"] - E[r["seed"]]["t_end"]) < 1e-9 and r["complete"] == E[r["seed"]]["complete"]
                and r["n_exits"] == E[r["seed"]]["n_exits"] for r in Rr]
        steps = np.array([r["n_steps"] for r in Rr], float)
        fr = {"lt" + c.replace(".", ""): float(np.sum([r["frac_steps_below"][c] * r["n_steps"] for r in Rr]) / steps.sum())
              for c in ("0.99", "0.95", "0.9")}
        # time fraction with w_o < 0.99 over the first 120 s (dense phase) and after, from the 1 s minima
        o["runs"] = {"n_runs": len(Rr), "seeds": [r["seed"] for r in Rr], "reproduce_E6a": int(sum(same)),
                     "complete": int(sum(r["complete"] for r in Rr)),
                     "w_min": min(r["w_min"] for r in Rr), "w_min_per_run": [r["w_min"] for r in Rr],
                     "w_min_run_median": float(np.median([r["w_min"] for r in Rr])),
                     "w_min_run_max": max(r["w_min"] for r in Rr),
                     "t_w_min_s": [r["t_w_min"] for r in Rr], "N_max": max(r["N_max"] for r in Rr),
                     "N_max_per_run": [r["N_max"] for r in Rr],
                     "frac_time_below": fr,
                     "frac_time_below_099_per_run": [r["frac_steps_below"]["0.99"] for r in Rr],
                     "time_below_099_s_per_run": [r["frac_steps_below"]["0.99"] * r["n_steps"] * r["dt"] for r in Rr],
                     "last_t_below_099_s_per_run": [max([i + 1 for i, w in enumerate(r["w_min_per_s"]) if w < 0.99],
                                                        default=0) for r in Rr],
                     "total_time_s": float(sum(r["n_steps"] * r["dt"] for r in Rr)),
                     "cpu_s": float(sum(r["wall_s"] for r in Rr))}
    revlib.out_json("A2", o)
    print(json.dumps({k: v for k, v in o.items() if k != "snapshots"}, indent=1, default=float)[:3000])
    print({k: o["snapshots"][k] for k in ("lone", "pair")})


if __name__ == "__main__":
    main()
