"""E1 terminal rest state: the blocker's local density and Weidmann factor at deadlock detection.

For every E1 deadlock snapshot (data/E1/library; E1a published, E1b corrected), the blocker is the
residual agent nearest the door centre (10, 5), as in keystone.py and e1_analyze.py. Its local density
is the simulator's default estimate (Simulation.step): active neighbours within neighbor_radius
(self excluded; KDTree query_ball_point, distance <= R) divided by pi R^2, with R from the snapshot's
parameters (3 m). The Weidmann factor v_eff/v0 = clip(1 - exp(-gamma (1/max(rho, 0.01) - 1/rho_max)),
0.05, 1) is computed with the snapshot's gamma and rho_max, as code/sim/steering/desired.py does.

This sources the statement (C16a) that the stuck-alone criterion is evaluated at a terminal rest state
where the local density leaves the drive essentially undiminished (v_eff/v0 >= 0.99).

Output: data/derived/E1_terminal.json. Run: PYTHONPATH=code <plan venv python> experiments/E1/terminal.py
"""
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import DERIVED, load_runs, runs_path, snap_path, weidmann_factor  # noqa: E402
import numpy as np  # noqa: E402

DOOR = np.array([10.0, 5.0])
OUT = os.path.join(DERIVED, "E1_terminal.json")
THRESH = 0.99


def blocker_density(snap):
    st, params = snap["state"], snap["params"]
    R = float(params["neighbor_radius"])
    act = np.asarray(st.active_indices, int)
    pos = st.positions[act]
    b = int(act[np.argmin(np.linalg.norm(pos - DOOR, axis=1))])
    d = np.linalg.norm(pos - st.positions[b], axis=1)
    n_nb = int(((d <= R) & (act != b)).sum())
    rho = n_nb / (np.pi * R * R)
    fac = weidmann_factor(rho, params.get("weidmann_gamma", 1.913), params.get("weidmann_rho_max", 5.4))
    return {"blocker": b, "n_neighbours": n_nb, "rho": rho, "weidmann": fac, "R": R,
            "n_residual": int(len(act))}


def stats(xs):
    xs = np.asarray(xs, float)
    return {"min": float(xs.min()), "median": float(np.median(xs)), "max": float(xs.max())}


def main():
    runs = [r for r in load_runs(runs_path()) if r.get("deadlock")]
    per = []
    for r in sorted(runs, key=lambda r: (r["mode"], r["seed"])):
        with open(snap_path(r["snapshot"]), "rb") as f:
            snap = pickle.load(f)
        rec = blocker_density(snap)
        rec.update({"job_id": r["job_id"], "mode": r["mode"], "seed": r["seed"]})
        per.append(rec)
    fac = [p["weidmann"] for p in per]
    out = {"script": "experiments/E1/terminal.py",
           "source": ["data/E1/E1_runs.jsonl", "data/E1/library/*.pkl"],
           "doc": "Blocker (residual agent nearest the door centre) at deadlock detection: local density "
                  "(active neighbours within neighbor_radius / pi R^2, the simulator's default) and "
                  "Weidmann factor v_eff/v0.",
           "R_m": per[0]["R"], "threshold": THRESH, "n": len(per),
           "by_mode": {m: sum(p["mode"] == m for p in per) for m in ("E1a", "E1b")},
           "rho": stats([p["rho"] for p in per]),
           "n_neighbours": stats([p["n_neighbours"] for p in per]),
           "weidmann": stats(fac),
           "n_ge_threshold": int(sum(f >= THRESH for f in fac)),
           "frac_ge_threshold": float(np.mean([f >= THRESH for f in fac])),
           "runs": per}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
