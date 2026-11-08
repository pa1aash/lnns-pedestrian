"""E9: open 90-degree crossing (Table 4 only), corrected-forward (CF), 100 + 100 agents, line goals
(w2_goal = line, as the pilot W2.7).
Scenario: OpenCrossingScenario (code/sim/scenarios/open_geometries.py) with the start blocks L in
{17, 25, 34} m long (start densities 1.96, 1.33, 0.98 m^-2; L = 17 is the scenario and the pilot), via
experiments/lib/opengeo.CrossDensity. Arms: C1, C2, C3_rvo2, C4_rvo2 (crush off). 25 seeds per arm and
level (42-66). Window 60 s (the pilot's), dt = 0.01 s, or until every agent is sunk.
Recorded: throughput (sunk / window; the C2/C1 ratio is formed in the analysis, paired by seed and level),
sinks per stream and the sink log, wall leaks, mean speed in the crossing zone [3.2, 6.8]^2, standoffs
(experiments/lib/opengeo.events in the crossing zone: count, lifetimes, sizes, censoring; formation rate
per zone-occupied second), and the RVO2 LP infeasibility rate.
Output: data/E9/e9_crossing.jsonl (job_id "<arm>|L<L>|seed<seed>"), resumable.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
from e1lib import CF, DATA, run_jobs  # noqa: E402
import qargs  # noqa: E402
from opengeo import open_run  # noqa: E402

OUT = os.path.join(DATA, "E9", "e9_crossing.jsonl")
ARMS = {"C1": ("C1", {}), "C2": ("C2", {}), "C3_rvo2": ("C3", {"w2_orca": "rvo2"}),
        "C4_rvo2": ("C4", {"w2_orca": "rvo2", "w2_crush": "off"})}
LENGTHS = (17.0, 25.0, 34.0)
SEEDS = range(42, 67)


def jobs():
    return [{"job_id": f"{a}|L{L:g}|seed{s}", "arm": a, "scen": "cross", "n": 100, "L": L, "config": c,
             "flags": {**CF, **f, "w2_goal": "line"}, "seed": s, "T": 60.0}
            for a, (c, f) in ARMS.items() for L in LENGTHS for s in SEEDS]


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(qargs.select(jobs(), a), open_run, out, workers=a.workers, log_every=10)


if __name__ == "__main__":
    print("wall", main())
