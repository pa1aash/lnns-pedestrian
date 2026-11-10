"""D3: rerun of the E10 CroMa model runs with the agent number of each human run set to the participants who passed
the entrance and with the documented bottleneck length 0.2 m (E10 used the track-ID count and 0.21 m).

Run set: the four Sect. 7 variants of experiments/E10/e10_croma.py, unchanged (C1_cf, C1_cf_edge = CF + B_w_edge
0.04, C3_rvo2_cf = C3 with RVO2 ORCA, CF; C1_cf_sig = CF + per-step velocity noise sigma = 0.0467 m/s, the value
E10 used), seeds 42-66, run type RUNS[(seed - 42) % 5] (five model runs per human run), dt = 0.01 s, 600 s cap,
deadlock stop as E10 (every active |v| < 0.01 m/s for 10 s, no exit). The run function, trajectory recording and
estimator are E10's run() (imported, unchanged).
Agent numbers (participants who passed, experiments/revision/D_croma_integrity.py, participant rule):
  4D030 135 (E10 135), 4D040 135 (E10 136), 4D110 129 (E10 131), 4D120 129 (E10 129), 4D130 128 (E10 128).
Bottleneck length: 2.0 m (4D030, 4D040) and 0.2 m (4D110, 4D120, 4D130; E10 0.21 m).
Output: data/revision/D3/d3_croma.jsonl (job_id "<cell>|seed<seed>"), resumable; trajectories data/revision/D3/raw.
Usage: D3_croma_rerun.py [qargs options: --out --limit --every --scale --workers]
Cost: 100 runs; E10 wall times of the same cells sum to about 6.6 CPU-h (C1_cf 0.67, C1_cf_edge 0.54,
C3_rvo2_cf 2.85, C1_cf_sig 2.57 h).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402
import qargs  # noqa: E402

sys.path.insert(0, os.path.join(revlib.ROOT, "experiments", "E10"))
import e10_croma as E10  # noqa: E402  (importable by name, so worker processes can unpickle E10.run)

RUNS = [("4D030", 135, 2.0), ("4D040", 135, 2.0), ("4D110", 129, 0.2), ("4D120", 129, 0.2), ("4D130", 128, 0.2)]
SIGMA = 0.0467
CELLS = {c: E10.CELLS[c] for c in ("C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig")}
OUTDIR = os.path.join(revlib.DATA, "revision", "D3")
OUT = os.path.join(OUTDIR, "d3_croma.jsonl")


def jobs(raw_dir):
    J = []
    for cell, (cfg, fl) in CELLS.items():
        for s in E10.SEEDS:
            run_id, N, L = RUNS[(s - 42) % 5]
            J.append({"job_id": f"{cell}|seed{s}", "cell": cell, "run": run_id, "N": N, "L": L, "seed": s,
                      "config": cfg, "flags": fl, "sigma": SIGMA if cell == "C1_cf_sig" else 0.0,
                      "t_max": E10.T_MAX, "raw_dir": raw_dir})
    return J


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    raw = os.path.join(os.path.dirname(out), "raw")
    J = qargs.select(jobs(raw), a)
    return revlib.run_jobs(J, E10.run, out, workers=a.workers, log_every=5)


if __name__ == "__main__":
    print("wall", main())
