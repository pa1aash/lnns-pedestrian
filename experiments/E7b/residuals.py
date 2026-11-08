"""Conservative-field residuals: max |F_code + grad U| for the rest-state C1 potentials used in the paper.

The barriers and pair landscapes assume that the code's C1 force at v = 0, with the local density frozen
at the snapshot value, is the negative gradient of U (experiments/BAR/bar.py, experiments/lib/pairlib.py).
Each producer stores the check it ran; this script collects them, with the source file of each:

  pair     E7b_static (experiments/E7b/e7b_static.py): both pair members mobile, 46 pair snapshots,
           field check_max_abs_F_plus_gradU_N in data/E7b/e7b_static.jsonl;
  lone     BAR (experiments/BAR/bar.py): blocker mobile, other residual agents pinned (the frozen /
           lone condition), field force_check_frozen_maxabs_N in data/BAR/barriers.jsonl;
  collective  BAR: every residual agent mobile (the collective barrier used by E3/E4), field
           force_check_all_maxabs_N in data/BAR/barriers.jsonl.
Lone and collective are reported over all BAR snapshots and over the E4 subset
(data/derived/selection.json, E4.snapshots).

Output: data/derived/field_residuals.json. Run: python3 experiments/E7b/residuals.py
"""
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "derived", "field_residuals.json")


def jsonl(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return [json.loads(l) for l in f if l.strip()]


def summary(vals, source, field, script, doc):
    v = np.asarray(vals, float)
    return {"n": int(v.size), "max_N": float(v.max()), "median_N": float(np.median(v)),
            "source": source, "field": field, "script": script, "doc": doc}


def main():
    pair_src = "data/E7b/e7b_static.jsonl"
    pair = jsonl(pair_src)
    bar_src = "data/BAR/barriers.jsonl"
    bar = {r["job_id"]: r for r in jsonl(bar_src)}
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    e4 = [s["tag"] for s in sel["E4"]["snapshots"]]
    missing = [t for t in e4 if t not in bar]
    if missing:
        raise SystemExit(f"E4 snapshots without a BAR record: {missing}")
    lone_f, coll_f = "force_check_frozen_maxabs_N", "force_check_all_maxabs_N"
    out = {"script": "experiments/E7b/residuals.py",
           "doc": "max |F_code + grad U| (N) of the rest-state C1 potential, density frozen at the snapshot.",
           "pair": summary([r["check_max_abs_F_plus_gradU_N"] for r in pair], pair_src,
                           "check_max_abs_F_plus_gradU_N", "experiments/E7b/e7b_static.py",
                           "E7b_static pair snapshots, both members mobile"),
           "lone": summary([r[lone_f] for r in bar.values()], bar_src, lone_f, "experiments/BAR/bar.py",
                           "BAR, blocker mobile, neighbours pinned (all barrier snapshots)"),
           "collective": summary([r[coll_f] for r in bar.values()], bar_src, coll_f, "experiments/BAR/bar.py",
                                 "BAR, every residual agent mobile (all barrier snapshots)"),
           "lone_E4": summary([bar[t][lone_f] for t in e4], bar_src, lone_f, "experiments/BAR/bar.py",
                              "as lone, E4 snapshots only (data/derived/selection.json)"),
           "collective_E4": summary([bar[t][coll_f] for t in e4], bar_src, coll_f, "experiments/BAR/bar.py",
                                    "as collective, E4 snapshots only")}
    out["overall_max_N"] = max(out[k]["max_N"] for k in ("pair", "lone", "collective"))
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
