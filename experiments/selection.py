"""Selection rules for E2, BAR, E3 and E4 (Step 4 of batch 2A). Fixed before any of these runs.

  E2   60 corrected-forward (E1b) snapshots drawn uniformly without replacement from the
       lone-keystone class (data/derived/E1_keystone.json), numpy Generator(PCG64(2026)).choice over
       the class's seeds in ascending order. If the class has fewer than 60, all are taken.
  BAR  for the 60 E2 snapshots: string-method barriers (experiments/BAR/bar.py); the collective
       barrier Delta U is all_mobile.dU_climb (every residual agent mobile, density frozen).
  E3   the 20 E2 snapshots with the largest collective Delta U, all with Delta U >= 3 J. If fewer
       than 20 qualify, every qualifying snapshot is taken.
  E4   10 snapshots from the E3 set spread across its Delta U range: for q = 0.05, 0.15, ..., 0.95 the
       snapshot (not yet chosen) whose Delta U is nearest the q-quantile (numpy linear) of the E3
       Delta U values; ties to the smaller Delta U. If E3 has <= 10 snapshots, all are taken.

Usage: selection.py e2        (needs the keystone summary)
       selection.py e3e4      (needs data/BAR/barriers.json; adds E3 and E4 to selection.json)
Output: data/derived/selection.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from e1lib import DATA, DERIVED, ELIB, ROOT, load_runs, runs_path  # noqa: E402
import numpy as np  # noqa: E402

OUT = os.path.join(DERIVED, "selection.json")
N_E2, SEED_E2, N_E3, DU_MIN, N_E4 = 60, 2026, 20, 3.0, 10


def e2():
    ks = json.load(open(os.path.join(DERIVED, "E1_keystone.json")))["modes"]["E1b"]
    pool = sorted(x["seed"] for x in ks["per_snapshot"] if x["class"] == "lone_keystone")
    rng = np.random.Generator(np.random.PCG64(SEED_E2))
    chosen = sorted(int(s) for s in rng.choice(pool, N_E2, replace=False)) if len(pool) > N_E2 else list(pool)
    blk = {x["seed"]: x for x in ks["per_snapshot"]}
    R = {r["seed"]: r for r in load_runs(runs_path()) if r["mode"] == "E1b"}
    snaps = [{"tag": f"E1b_seed{s}", "seed": s,
              "snap": os.path.relpath(os.path.join(ELIB, f"E1b_seed{s}.pkl"), ROOT),
              "blocker": blk[s]["blocker"], "n_resid": blk[s]["n_resid"],
              "blocker_margin_C1": blk[s]["blocker_margin_C1"]} for s in chosen]
    assert all(R[s]["snapshot"] for s in chosen)
    sel = {"doc": __doc__, "E2": {"pool_class": "lone_keystone", "pool_size": len(pool), "n": len(snaps),
                                  "rng": "numpy Generator(PCG64(2026)).choice(pool ascending, 60, replace=False)",
                                  "short": len(pool) < N_E2, "snapshots": snaps}}
    json.dump(sel, open(OUT, "w"), indent=1, default=float)
    print("E2: pool", len(pool), "chosen", len(snaps))


def e3e4():
    sel = json.load(open(OUT))
    bar = {b["job_id"]: b for b in json.load(open(os.path.join(DATA, "BAR", "barriers.json")))["barriers"]}
    rows = []
    for s in sel["E2"]["snapshots"]:
        b = bar[s["tag"]]
        rows.append(dict(s, dU=b["all_mobile"]["dU_climb"], dU_string=b["all_mobile"]["dU_string"],
                         force_check_all_maxabs_N=b["force_check_all_maxabs_N"]))
    q = [r for r in rows if r["dU"] >= DU_MIN]
    e3 = sorted(q, key=lambda r: (-r["dU"], r["seed"]))[:N_E3]
    if len(e3) <= N_E4:
        e4 = list(e3)
    else:
        vals = np.array([r["dU"] for r in e3])
        left, e4 = list(e3), []
        for qq in np.arange(0.05, 1.0, 0.1):
            target = float(np.quantile(vals, qq))
            pick = min(left, key=lambda r: (abs(r["dU"] - target), r["dU"]))
            e4.append(pick)
            left.remove(pick)
    du = np.array([r["dU"] for r in rows])
    sel["BAR"] = {"n": len(rows), "dU_all_mobile_J": {f"p{p}": float(np.percentile(du, p)) for p in (0, 10, 25, 50, 75, 90, 100)},
                  "n_dU_ge_3J": len(q), "max_force_check_N": max(r["force_check_all_maxabs_N"] for r in rows),
                  "per_snapshot": [{k: r[k] for k in ("tag", "dU", "dU_string", "force_check_all_maxabs_N")} for r in rows]}
    sel["E3"] = {"n": len(e3), "short": len(e3) < N_E3, "snapshots": sorted(e3, key=lambda r: r["seed"])}
    sel["E4"] = {"n": len(e4), "snapshots": sorted(e4, key=lambda r: r["dU"])}
    json.dump(sel, open(OUT, "w"), indent=1, default=float)
    print("BAR", sel["BAR"]["dU_all_mobile_J"], "E3", len(e3), "E4", len(e4))


if __name__ == "__main__":
    {"e2": e2, "e3e4": e3e4}[sys.argv[1]]()
