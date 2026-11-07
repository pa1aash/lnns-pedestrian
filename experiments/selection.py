"""Selection rules for E2, BAR, E3 and E4 (batch 2A Step 4, revised by plan change C15).

  E2   the 34 lone-keystone E1b snapshots (class lone_keystone in data/derived/E1_keystone.json, all
       of them, seed ascending) followed by 26 drawn uniformly without replacement from the
       lone_keystone_second_trap class with numpy Generator(PCG64(2026)).choice over that class's seeds
       in ascending order (then sorted by seed): 60 in total. The original 34 keep their order, so their
       E2 job_ids and noise seeds are unchanged. Each entry carries its class (the E2 stratum).
  BAR  all 60 E2 snapshots: string-method barriers (experiments/BAR/bar.py); the collective barrier
       Delta U is all_mobile.dU_climb (every residual agent mobile, density frozen).
  E3   20 of the 60 with collective Delta U >= 3 J, spread across Delta U: the qualifying snapshots
       sorted by (Delta U, seed), ranks round(linspace(0, n_q - 1, 20)). If fewer than 20 qualify, all
       are taken. dU_rank (0 = smallest Delta U) sets the noise level in E3 (even 1.5, odd 2.5).
  E4   10 of the 60 with at least 2 residual agents, spread across collective Delta U by the same
       evenly-spaced-rank rule (sorted by (Delta U, seed), ranks round(linspace(0, n - 1, 10))).

Usage: selection.py e2        (needs the keystone summary)
       selection.py e3e4      (needs data/BAR/barriers.json; adds BAR, E3 and E4 to selection.json)
Output: data/derived/selection.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from e1lib import DATA, DERIVED, ELIB, ROOT, load_runs, runs_path  # noqa: E402
import numpy as np  # noqa: E402

OUT = os.path.join(DERIVED, "selection.json")
N_E2_EXTRA, SEED_E2, N_E3, DU_MIN, N_E4, MIN_RESID_E4 = 26, 2026, 20, 3.0, 10, 2
CLS_A, CLS_B = "lone_keystone", "lone_keystone_second_trap"


def e2():
    ks = json.load(open(os.path.join(DERIVED, "E1_keystone.json")))["modes"]["E1b"]
    pool_a = sorted(x["seed"] for x in ks["per_snapshot"] if x["class"] == CLS_A)
    pool_b = sorted(x["seed"] for x in ks["per_snapshot"] if x["class"] == CLS_B)
    rng = np.random.Generator(np.random.PCG64(SEED_E2))
    extra = sorted(int(s) for s in rng.choice(pool_b, N_E2_EXTRA, replace=False))
    blk = {x["seed"]: x for x in ks["per_snapshot"]}
    R = {r["seed"]: r for r in load_runs(runs_path()) if r["mode"] == "E1b"}
    chosen = [(s, CLS_A) for s in pool_a] + [(s, CLS_B) for s in extra]
    snaps = [{"tag": f"E1b_seed{s}", "seed": s, "class": c,
              "snap": os.path.relpath(os.path.join(ELIB, f"E1b_seed{s}.pkl"), ROOT),
              "blocker": blk[s]["blocker"], "n_resid": blk[s]["n_resid"],
              "blocker_margin_C1": blk[s]["blocker_margin_C1"]} for s, c in chosen]
    assert all(R[s]["snapshot"] for s, _ in chosen)
    assert len({s for s, _ in chosen}) == len(chosen)
    sel = {"doc": __doc__, "E2": {
        "n": len(snaps), "strata": {CLS_A: {"pool_size": len(pool_a), "n": len(pool_a), "rule": "all"},
                                    CLS_B: {"pool_size": len(pool_b), "n": len(extra),
                                            "rule": "numpy Generator(PCG64(2026)).choice(pool ascending, 26, replace=False)"}},
        "snapshots": snaps}}
    json.dump(sel, open(OUT, "w"), indent=1, default=float)
    print("E2:", CLS_A, len(pool_a), "+", CLS_B, len(extra), "of", len(pool_b), "=", len(snaps))


def spread(rows, n):
    """Evenly spaced ranks over rows sorted by (dU, seed)."""
    r = sorted(rows, key=lambda x: (x["dU"], x["seed"]))
    if len(r) <= n:
        return r
    idx = np.round(np.linspace(0, len(r) - 1, n)).astype(int)
    assert len(set(idx)) == n
    return [r[i] for i in idx]


def e3e4():
    sel = json.load(open(OUT))
    bar = {b["job_id"]: b for b in json.load(open(os.path.join(DATA, "BAR", "barriers.json")))["barriers"]}
    rows = []
    for s in sel["E2"]["snapshots"]:
        b = bar[s["tag"]]
        rows.append(dict(s, dU=b["all_mobile"]["dU_climb"], dU_string=b["all_mobile"]["dU_string"],
                         dU_frozen=b["frozen"]["dU_climb"], dU_alone=b["alone"]["dU_climb"],
                         dU_1d_alone=b["dU_1d_axis_alone"],
                         force_check_all_maxabs_N=b["force_check_all_maxabs_N"]))
    q = [r for r in rows if r["dU"] >= DU_MIN]
    e3 = spread(q, N_E3)
    for k, r in enumerate(e3):
        r["dU_rank"] = k
    q4 = [r for r in rows if r["n_resid"] >= MIN_RESID_E4]
    e4 = spread(q4, N_E4)
    du = np.array([r["dU"] for r in rows])
    sel["BAR"] = {"n": len(rows), "dU_all_mobile_J": {f"p{p}": float(np.percentile(du, p)) for p in (0, 10, 25, 50, 75, 90, 100)},
                  "n_dU_ge_3J": len(q), "max_force_check_N": max(r["force_check_all_maxabs_N"] for r in rows),
                  "per_snapshot": [{k: r[k] for k in ("tag", "class", "n_resid", "dU", "dU_string", "dU_frozen",
                                                      "dU_alone", "dU_1d_alone", "force_check_all_maxabs_N")}
                                   for r in rows]}
    sel["E3"] = {"n": len(e3), "n_qualifying": len(q), "short": len(e3) < N_E3, "snapshots": e3}
    sel["E4"] = {"n": len(e4), "n_qualifying": len(q4), "snapshots": e4}
    json.dump(sel, open(OUT, "w"), indent=1, default=float)
    print("BAR", sel["BAR"]["dU_all_mobile_J"], "E3", len(e3), "of", len(q), "E4", len(e4), "of", len(q4))


if __name__ == "__main__":
    {"e2": e2, "e3e4": e3e4}[sys.argv[1]]()
