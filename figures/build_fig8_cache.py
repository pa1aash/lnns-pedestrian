"""Per-run cache for the CroMa figure (figures/fig8_croma.py), from the Part D rerun of session C
(data/derived/rev_D.json: key D3.rerun, 100 runs, agent number = participants who passed, bottleneck lengths as in the
archive: 2.0 m for 4D030 and 4D040, 0.2 m for 4D110, 4D120 and 4D130) and the corrected human runs (humans_corrected).

Per run: flow, waiting-zone fluctuation and the longest gap between passages. The final gap of a run that did not complete
(deadlocked, or still running at the 600 s horizon) is open and right-censored at the horizon: its plotted value is the
lower bound c = max(longest closed gap, last passage to 600 s), as in D4; `censored` is true. Counts are asserted against
notes/D_changes.md (experiments/revision/notes/D_changes.md).
Output: figures/data/fig8_runs.json."""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = json.load(open(HERE.parent / "data" / "derived" / "rev_D.json"))
T_MAX = 600.0
JSONL = HERE.parent / "data" / "revision" / "D3" / "d3_croma.jsonl"     # per-run waiting-zone fluctuation (E10 estimator)
FL = {}
for _l in open(JSONL):
    if _l.strip():
        _r = json.loads(_l); _f = _r["estimator"]["fluct"]
        FL[(_r["cell"], _r["seed"])] = math.sqrt((_f["sd_x"] ** 2 + _f["sd_y"] ** 2) / 2)
CELLS = ["C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]
# D_changes.md: complete / deadlock / capped, flow mean, longest gap of completed runs (max), censored runs
EXPECT = {"C1_cf": (2, 23, 0, 0.73, 20.4, 23), "C1_cf_edge": (21, 4, 0, None, 15.6, 4),
          "C3_rvo2_cf": (10, 1, 14, 0.88, 7.6, 15), "C1_cf_sig": (18, 0, 7, None, 237.0, 7)}


def main():
    H = D["humans_corrected"]
    out = {"source": "figures/build_fig8_cache.py from data/derived/rev_D.json", "t_max_s": T_MAX, "cells": {}}
    out["cells"]["humans"] = {
        "runs": [{"run": r["run"], "complete": True, "censored": False, "flow": r["flow_per_s"],
                  "gap": r["max_gap_s"], "fluct": r["fluct_rms"]} for r in H["runs"]],
        "flow": H["flow"], "fluct": H["fluct"], "n_censored": 0}
    assert abs(H["flow"]["mean"] - 1.47) < 0.005
    rr = D["D3"]["rerun"]["per_variant"]
    fl = {r["run"]: None for r in H["runs"]}
    for c in CELLS:
        v = rr[c]
        runs = [{"seed": r["seed"], "run": r["run"], "status": r["status"], "complete": r["status"] == "complete",
                 "censored": r["event"] == 0, "flow": r["flow"], "gap": r["c"],
                 "fluct": FL[(c, r["seed"])]} for r in v["runs"]]
        fluct = v["fluct"]
        assert abs(sum(r["fluct"] for r in runs) / 25 - fluct["mean"]) < 1e-9, c
        out["cells"][c] = {"runs": runs, "flow": v["flow"], "fluct": fluct, "n_censored": v["n_censored"],
                           "gap_complete_max": v["gap_complete"]["max"], "complete": v["complete"],
                           "deadlock": v["deadlock"], "capped": v["capped"]}
        nc, nd, ncap, fm, gm, ncen = EXPECT[c]
        assert (v["complete"], v["deadlock"], v["capped"], v["n_censored"]) == (nc, nd, ncap, ncen), c
        assert abs(v["gap_complete"]["max"] - gm) < 0.5, c
        assert fm is None or abs(v["flow"]["mean"] - fm) < 0.005, c
        assert sum(r["censored"] for r in runs) == ncen and len(runs) == 25
        print(c, "complete", nc, "deadlock", nd, "capped", ncap, "censored", ncen, "longest gap of completed runs",
              round(gm, 1), "flow", round(v["flow"]["mean"], 3), [round(x, 3) for x in v["flow"]["ci95"]],
              "fluct", round(fluct["mean"], 4))
    json.dump(out, open(HERE / "data" / "fig8_runs.json", "w"), indent=1)


if __name__ == "__main__":
    main()
