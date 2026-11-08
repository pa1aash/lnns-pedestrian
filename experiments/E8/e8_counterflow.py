"""E8: open bidirectional corridor (Table 4 only), corrected-forward (CF), 50 + 50 agents.
Scenario: OpenBidirectionalScenario (code/sim/scenarios/open_geometries.py) with the start blocks
L in {12, 18, 30} m long (start densities 1.39, 0.93, 0.56 m^-2; L = 12 is the scenario and the pilot
W2.6), via experiments/lib/opengeo.BidirDensity. Arms: C1, C2, C3_pub (CF numerics, published ORCA),
C3_rvo2, C4_rvo2 (crush off). 25 seeds per arm and density (42-66). Window 60 s (the pilot's), dt =
0.01 s, or until every agent is sunk.
Recorded: throughput (sunk agents / window), sinks per direction and the sink log, wall leaks, mean
speed in the measurement section x in [0, 20], stall episodes (experiments/lib/opengeo.events: >= 2
agents below 0.05 m/s, 1.0 m single linkage, in the section, persisting >= 2 s; durations, sizes,
censoring), and the ORCA LP infeasibility rate (experiments/lib/lpcount: published LP = returned velocity
violates a half-plane, i.e. constraints dropped; RVO2 = linearProgram3 used), per agent-step with ORCA.
Output: data/E8/e8_counterflow.jsonl (job_id "<arm>|L<L>|seed<seed>"), resumable. C3_pub jobs are last.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
from e1lib import CF, DATA, run_jobs  # noqa: E402
import qargs  # noqa: E402
from opengeo import open_run  # noqa: E402

OUT = os.path.join(DATA, "E8", "e8_counterflow.jsonl")
ARMS = {"C1": ("C1", {}), "C2": ("C2", {}), "C3_rvo2": ("C3", {"w2_orca": "rvo2"}),
        "C4_rvo2": ("C4", {"w2_orca": "rvo2", "w2_crush": "off"}),
        "C3_pub": ("C3", {"w2_orca": "published"})}
LENGTHS = (12.0, 18.0, 30.0)
C3_PUB_LENGTHS = LENGTHS
SEEDS = range(42, 67)


def jobs():
    return [{"job_id": f"{a}|L{L:g}|seed{s}", "arm": a, "scen": "bidir", "n": 50, "L": L, "config": c,
             "flags": {**CF, **f}, "seed": s, "T": 60.0}
            for a, (c, f) in ARMS.items() for L in (C3_PUB_LENGTHS if a == "C3_pub" else LENGTHS) for s in SEEDS]


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(qargs.select(jobs(), a), open_run, out, workers=a.workers, log_every=10)


if __name__ == "__main__":
    print("wall", main())
