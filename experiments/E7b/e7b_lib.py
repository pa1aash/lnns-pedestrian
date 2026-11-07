"""E7b_lib: pair-standoff library, corrected-forward union {B_w: 0.04} (all walls), C1, w = 0.8 m,
100 agents, 600 s cap, stop at deadlock (snapshot saved), seeds from 242 upward in batches of 40,
until at least 40 snapshots qualify or seed 641 is reached.

Provenance: the pilot's 26 pair snapshots (data/pilot/library/w25_B0.04_*, a1_B0.04_*) were made with
{w2_numerics: fixed, spawn: rejection, B_w: 0.04} only (their params carry no w2_orca, w2_crush,
w2_wall_corner) on the pre-exec simulator branch, so they are not exactly CF union {B_w: 0.04}; all
40 are built fresh here and the pilot ones are kept as reference only.

Qualification, ported from the pilot (wave2b select_pairs.py and the configuration checked in
a3_pair_stability.py):
  deadlock          the run stopped at a deadlock: every active |v| < 0.01 m/s for 10 s, no exit (at rest);
  pair              exactly two residual agents (select_pairs.py: n_remaining == 2);
  front of jambs    each member at 9.3 < x < 10.0 and 0.25 < |y - 5| < 0.75 m, the two on opposite sides
                    of the door axis (pilot members: x = 9.54-9.65, |y - 5| = 0.40-0.51);
  contact-free      surface gap d - r1 - r2 > 0;
  each passes alone stuck-alone margin < 0 for both members under the run's wall law (B_w = 0.04).
The pilot rule was the first two conditions; the other three held for 26/26 pilot pairs (a3) and are
checked here so that a qualifying snapshot satisfies the stated pair criterion.
Output: data/E7b/e7b_lib.jsonl (job_id "seed<N>"), snapshots data/E7b/library/E7b_B0.04_seed<N>.pkl.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, load_runs, run_jobs  # noqa: E402
from runlib import whole_run  # noqa: E402
import numpy as np  # noqa: E402

OUT = os.path.join(DATA, "E7b", "e7b_lib.jsonl")
LIBD = os.path.join(DATA, "E7b", "library")
FLAGS = {**CF, "B_w": 0.04}
S0, S_CAP, BATCH, TARGET = 242, 641, 40, 40


def qualifies(r):
    chk = {"deadlock": bool(r.get("deadlock")), "pair": r.get("n_remaining") == 2}
    if chk["deadlock"] and chk["pair"]:
        res = r["residual"]
        at = {a["id"]: a for a in r["attrs"]}
        p = [np.array(x["pos"]) for x in res]
        ids = [x["id"] for x in res]
        dy = [q[1] - 5.0 for q in p]
        chk["front_of_jambs"] = all(9.3 < q[0] < 10.0 and 0.25 < abs(d) < 0.75 for q, d in zip(p, dy)) \
            and dy[0] * dy[1] < 0
        chk["contact_free"] = float(np.linalg.norm(p[0] - p[1]) - at[ids[0]]["r"] - at[ids[1]]["r"]) > 0
        chk["each_passes_alone"] = all(r["margin"][i] < 0 for i in ids)
    chk["qualifies"] = all(chk.get(k, False) for k in
                           ("deadlock", "pair", "front_of_jambs", "contact_free", "each_passes_alone"))
    return chk


def job(s):
    return {"job_id": f"seed{s}", "seed": s, "width": 0.8, "flags": dict(FLAGS), "sigma": 0.0, "t_max": 600.0,
            "config": "C1", "lib": LIBD, "tag": "E7b_B0.04"}


def state(out=OUT):
    R = load_runs(out) if os.path.exists(out) else []
    q = sorted(r["seed"] for r in R if qualifies(r)["qualifies"])
    return R, q


def jobs():
    """Jobs up to the current batch boundary (for status)."""
    R, q = state()
    s1 = max([r["seed"] for r in R], default=S0 - 1) + 1
    s1 = S0 + BATCH * -(-(s1 - S0) // BATCH) if s1 > S0 else S0 + BATCH
    return [job(s) for s in range(S0, min(s1, S_CAP + 1))]


def main(out=OUT, workers=4, s0=S0, s_cap=S_CAP, batch=BATCH, target=TARGET):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    wall, s = 0.0, s0
    while s <= s_cap:
        R, q = state(out)
        if len(q) >= target:
            break
        s1 = min(s + batch, s_cap + 1)
        wall += run_jobs([job(k) for k in range(s, s1)], whole_run, out, workers=workers, log_every=10)
        s = s1
    R, q = state(out)
    print("E7b_lib qualifying", len(q), "of", len(R), "runs; seeds", q, flush=True)
    return wall


if __name__ == "__main__":
    print("wall", main())
