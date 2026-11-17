"""Benchmark: wall time of one run of each type in the current code (session C5 planning).
Usage: bench.py <kind>   kind in {alone, quench_rvo2, whole_sfm, whole_rvo2, whole_drive}"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "E2"))
from e1lib import CF, ROOT  # noqa
from runlib import whole_run, quench, escape  # noqa
import e2_quench  # noqa

kind = sys.argv[1]
t0 = time.perf_counter()
S = e2_quench.snapshots()
if kind == "alone":
    tag, snap, blk, _ = S[0]
    r = escape({"job_id": "b", "snap": snap, "blocker": blk, "cond": "alone", "config": "C1", "flags": dict(CF),
                "sigma": 1e-9, "noise_seed": 1, "t_cens": 60.0})
    out = {"sim_s": r["t_run"], "wall_s": r["wall_s"], "per_sim_s": r["wall_s"] / r["t_run"]}
elif kind == "quench_rvo2":
    tag, snap, blk, _ = S[0]
    r = quench({"snap": snap, "config": "C3", "flags": {**CF, "w2_orca": "rvo2"}, "deterministic": True, "t_q": 120.0})
    out = {"sim_s": r["t_run"], "wall_s": r["wall_s"], "n_resid": len(r["residual"])}
else:
    cfg, fl = {"whole_sfm": ("C1", dict(CF)), "whole_rvo2": ("C3", dict(CF)),
               "whole_drive": ("C3", {**CF, "w2_orca_split": "drive_only"})}[kind]
    r = whole_run({"job_id": "b", "seed": 242, "width": 0.8, "config": cfg, "flags": fl, "sigma": 0.0, "t_max": 600.0})
    out = {"sim_s": r["t_end"], "wall_s": r["wall_s"], "complete": r["complete"]}
out["kind"] = kind
print(json.dumps(out), flush=True)
