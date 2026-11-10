#!/usr/bin/env python3
"""Counts of the room-bottleneck deadlocks for the one model of the paper (corrected update, E1b library).

Several earlier summaries pooled the E1a library (the superseded update) with E1b. This script recomputes them on
E1b only and writes data/derived/final_corrected.json:
  terminal   blocker neighbourhood at deadlock detection (from E1_terminal.json runs)
  criterion  stuck-alone margin against the keystone K1 restart (from E1_keystone.json per_snapshot)
  hessian    lone rest-state Hessian eigenvalues of the held blockers (same method as experiments/fixan/fix_a5.py)
  second     second-trap agents held alone (E1_keystone.json second_trap)
  push       rest-drive push (+) against SFM+ORCA with the RVO2 solver at the lone keystone (E2_analysis.json)
  barriers   lone-trap snapshots sent to the string method and the number failing the convergence gate
             (data/BAR/barriers_gated.json)
Run from the worktree root: .venv/bin/python experiments/tables/derive_final.py
"""
import json
import os
import pickle
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DER = os.path.join(ROOT, "data", "derived")
sys.path.insert(0, os.path.join(ROOT, "experiments", "fixan"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
import fix_a5  # noqa: E402  (imports e1lib, which chdirs to code/)
import e1lib  # noqa: E402

MODE = "E1b"


def load(name):
    return json.load(open(os.path.join(DER, name)))


def main():
    out = {"script": "experiments/tables/derive_final.py", "library": MODE}
    t = [r for r in load("E1_terminal.json")["runs"] if r["mode"] == MODE]
    out["terminal"] = {"n": len(t), "n_neighbours_max": int(max(r["n_neighbours"] for r in t)),
                       "n_neighbours_median": float(np.median([r["n_neighbours"] for r in t])),
                       "rho_max": float(max(r["rho"] for r in t)),
                       "weidmann_min": float(min(r["weidmann"] for r in t))}
    ks = load("E1_keystone.json")["modes"][MODE]
    ps = ks["per_snapshot"]
    marg = np.array([s["blocker_margin_C1"] for s in ps])
    held = np.array([bool(s["K1_held"]) for s in ps])
    pos = marg > 0
    runs = {x["seed"]: x for x in e1lib.load_runs(os.path.join(ROOT, "data", "E1", "E1_runs.jsonl"))
            if x["mode"] == MODE}
    neg_types = [runs[s["seed"]]["deadlock_type"]["type"] for s, p in zip(ps, pos) if not p]
    out["criterion"] = {"n": len(ps), "n_pos": int(pos.sum()), "n_pos_held": int((pos & held).sum()),
                        "n_neg": int((~pos).sum()), "n_neg_held": int((~pos & held).sum()),
                        "n_neg_pair": int(sum(x == "pair" for x in neg_types)),
                        "n_within_10N": int((np.abs(marg) <= 10).sum())}
    k1 = {x["job_id"]: x for x in e1lib.load_runs(os.path.join(ROOT, "data", "E1", "keystone.jsonl"))
          if x["test"] == "K1"}
    lat, ax = [], []
    for s in ps:
        if not s["K1_held"]:
            continue
        R = runs[s["seed"]]
        b = s["blocker"]
        at = {a["id"]: a for a in R["attrs"]}
        kk = k1[f"{MODE}_seed{s['seed']}|K1"]
        fp = kk["final_pos"].get(str(b))
        if not fp:
            continue
        snap = pickle.load(open(os.path.join(e1lib.ELIB, kk["snap"]), "rb"))
        sim = e1lib.restore(snap, "C1", flags=e1lib.MODE_FLAGS[MODE])
        wf, walls = sim.steering.wall_forces, sim.world.walls
        a = (at[b]["r"], at[b]["v0"], at[b]["tau"], at[b].get("m", 80.0))
        K, _ = fix_a5.hessian(wf, walls, np.array(fp, float), *a)
        ev, vec = np.linalg.eigh(K)
        il = int(np.argmax(np.abs(vec[1])))
        lat.append(float(ev[il]))
        ax.append(float(ev[1 - il]))
    out["hessian"] = {"n": len(lat), "lateral_median_N_per_m": float(np.median(lat)),
                      "axial_median_N_per_m": float(np.median(ax))}
    st = ks["second_trap"]
    out["second"] = {"held": int(st["K1b_held"]), "n": int(st["K1b_held"] + st["K1b_freed"] + st["K1b_missing"])}
    fp = load("E2_analysis.json")["d_orca_decomposition"]["lone_keystone"]["frozen_plus_vs_C3_rvo2"]
    out["push"] = {"n": fp["n"], "both": int(fp["second_freed"] - fp["discordant_second_only"]),
                   "push_only": int(fp["discordant_first_only"]), "orca_only": int(fp["discordant_second_only"]),
                   "mcnemar_exact_p": fp["mcnemar_exact_p"]}
    g = json.load(open(os.path.join(ROOT, "data", "BAR", "barriers_gated.json")))
    out["barriers"] = {"n": int(g["n"]), "n_gate_fail": len(g["failed"]),
                       "failed": g["failed"]}
    json.dump(out, open(os.path.join(DER, "final_corrected.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "barriers"}, indent=1))


if __name__ == "__main__":
    main()
