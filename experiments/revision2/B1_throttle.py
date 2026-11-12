"""B1: ablation of the density throttle of Eq. (2) (flag veff_throttle = "off": v_eff = v0 in the desired force).

Parts (each its own resumable JSONL in data/revision2/B1/, job_id as in the run sets they mirror):
  a  SFM (C1), CF flags, default walls, 100 agents, seeds 42-141 (spawns of the E7/B2 width runs), widths
     {0.80, 0.84, 0.88, 0.92, 0.96} m, 600 s, deadlock stop; runner experiments/revision/B2_width.run (records
     arrivals), unchanged. Throttle-on counterparts: E1b (0.80), B2 (0.82-0.96), E7 (0.9).
  b  w = 0.8 m whole runs, seeds 242-341 (spawns of E6a and velorca's whole runs), 600 s, runlib.whole_run:
     sfm = C1 + CF, orca = C3 + CF (RVO2). Throttle-on counterparts: velorca whole.jsonl "sfm" and E6a.
  c  CroMa: the D3 cells C1_cf (SFM) and C3_rvo2_cf (force-coupled ORCA, RVO2), agent numbers and bottleneck
     lengths of D3 (participants who passed; 2.0 m for 4D030/4D040, 0.2 m otherwise), seeds 42-66, five model
     runs per human run, 600 s; runner E10.run, unchanged. Throttle-on counterpart: D3.
  d  CroMa, the other two Sect. 7 variants of D3 (C1_cf_edge: B_w = 0.04 m on the bottleneck edges; C1_cf_sig:
     per-step noise sigma = 0.0467 m/s), as c, so that the throttle-off range covers all four variants.
Usage: B1_throttle.py a|b|c|d [qargs options]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import CF, run_jobs  # noqa: E402
import qargs  # noqa: E402
import B2_width  # noqa: E402  (experiments/revision)
from runlib import whole_run  # noqa: E402

sys.path.insert(0, os.path.join(rev2lib.ROOT, "experiments", "E10"))
import e10_croma as E10  # noqa: E402
import D3_croma_rerun as D3  # noqa: E402

OFF = {"veff_throttle": "off"}
WIDTHS = (0.80, 0.84, 0.88, 0.92, 0.96)
OUTDIR = rev2lib.data_dir("B1")


def jobs_a():
    return [{"job_id": f"w{w:.2f}|seed{s}", "seed": s, "width": w, "flags": {**CF, **OFF}, "t_max": 600.0}
            for w in WIDTHS for s in range(42, 142)]


def jobs_b():
    V = {"sfm": ("C1", {**CF, **OFF}), "orca": ("C3", {**CF, "w2_orca": "rvo2", **OFF})}
    return [{"job_id": f"{v}|seed{s}", "variant": v, "seed": s, "width": 0.8, "config": cfg, "flags": fl,
             "sigma": 0.0, "t_max": 600.0} for v, (cfg, fl) in V.items() for s in range(242, 342)]


def jobs_c(raw, cells=("C1_cf", "C3_rvo2_cf")):
    J = []
    for j in D3.jobs(raw):
        if j["cell"] in cells:
            J.append(dict(j, flags={**j["flags"], **OFF}))
    return J


if __name__ == "__main__":
    part = sys.argv[1]
    a = qargs.parse(sys.argv[2:])
    out = a.out or os.path.join(OUTDIR, f"b1{part}.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if part == "a":
        J, fn = jobs_a(), B2_width.run
    elif part == "b":
        J, fn = jobs_b(), whole_run
    elif part == "c":
        J, fn = jobs_c(os.path.join(os.path.dirname(out), "raw_c")), E10.run
    elif part == "d":
        J, fn = jobs_c(os.path.join(os.path.dirname(out), "raw_c"), ("C1_cf_edge", "C1_cf_sig")), E10.run
    else:
        sys.exit("part must be a, b, c or d")
    run_jobs(qargs.select(J, a), fn, out, workers=a.workers, log_every=10)
