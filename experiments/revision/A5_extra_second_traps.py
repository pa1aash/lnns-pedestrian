"""A5: job builder for screening the second-trap snapshots that E2 did not draw (revision queue step A5x).

Population: the 160 E1b snapshots of class lone_keystone_second_trap in data/derived/E1_keystone.json
(keystone test, experiments/E1/keystone.py), sorted by seed ascending; k = index in that sorted list
(0-159). The 26 drawn for E2 (data/derived/selection.json, stratum lone_keystone_second_trap) are left
out, so the default job list covers the remaining 134. Every snapshot has a saved pickle in
data/E1/library (asserted).

Arms (the E2 arm definitions of experiments/E2/e2_quench.py, imported unchanged: full flag set
CF union arm flags, C1-C3, dt = 0.01 s, 120 s window, deterministic arms stop once stationary):
  noise0.07  C1 + per-step velocity noise sigma = 0.07 m/s, 5 noise seeds 90000 + 100 k + rep (rep 0-4).
             E2 used 7000 + 100 k' + rep with k' < 60 (7000-12904); E3, E4, E7b and N1 stay below
             71000; the range 90000-105904 is disjoint from every simulation seed in experiments/SEEDS.md.
  C3_rvo2    force-coupled ORCA, RVO2 solver: once unperturbed and 5 replays (perturb seeds 900-904,
             1e-9 m Gaussian displacement of every residual agent), as in E2.
  C3_pub     force-coupled ORCA, legacy linear-program solver: unperturbed and 5 replays, as C3_rvo2.
  drive_only ORCA's drive part alone, unperturbed.
  constraint_only_rvo2  ORCA's constraint part alone (RVO2), unperturbed.
  frozen_plus the rest-drive push towards the door (+), unperturbed.
  C1         the SFM restart, unperturbed (the control).
21 jobs per snapshot; job_id "<tag>|<arm>|<rep>" exactly as in E2 (rep = 'u', perturb seed, or noise
rep). Outcome: blocker (keystone-test blocker, residual agent nearest (10, 5)) exits within 120 s,
computed by e2_quench.quench_e2.

Output: data/revision/A5/a5_quench.jsonl (resumable through run_jobs; done job_ids are skipped).
Usage:  A5_extra_second_traps.py --dry                 print job and snapshot counts only
        A5_extra_second_traps.py [--limit N] [--workers W] [--out PATH] [--include-e2]
          --limit N      only the first N snapshots of the list (smoke tests)
          --include-e2   also the 26 E2 snapshots (a check that the arm set reproduces E2)
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
import e2_quench  # noqa: E402

CLS = "lone_keystone_second_trap"
NOISE_BASE, SIGMA, N_NOISE = 90000, 0.07, 5
ARMS = ("C3_rvo2", "C3_pub", "drive_only", "frozen_plus", "constraint_only_rvo2", "C1")
REPLAY_ARMS = ("C3_rvo2", "C3_pub")
OUT = os.path.join(revlib.DATA, "revision", "A5", "a5_quench.jsonl")


def pool():
    """All second-trap snapshots, seed ascending: list of (k, seed, tag, snap path, blocker, in_E2)."""
    ks = json.load(open(os.path.join(revlib.DERIVED, "E1_keystone.json")))["modes"]["E1b"]["per_snapshot"]
    sel = json.load(open(os.path.join(revlib.DERIVED, "selection.json")))["E2"]["snapshots"]
    e2 = {s["seed"] for s in sel if s["class"] == CLS}
    rows = sorted((x for x in ks if x["class"] == CLS), key=lambda x: x["seed"])
    out = []
    for k, x in enumerate(rows):
        tag = f"E1b_seed{x['seed']}"
        snap = os.path.join(revlib.DATA, "E1", "library", tag + ".pkl")
        assert os.path.exists(snap), snap
        out.append((k, x["seed"], tag, snap, x["blocker"], x["seed"] in e2))
    assert len(out) == 160 and sum(r[5] for r in out) == 26
    return out


def jobs(include_e2=False, limit=None):
    P = [r for r in pool() if include_e2 or not r[5]]
    if limit is not None:
        P = P[:limit]
    J = []
    for k, seed, tag, snap, blk, _ in P:
        for arm in ARMS:
            cfg, fl = e2_quench.DET_ARMS[arm]
            reps = (None,) + (e2_quench.PERTURB_SEEDS if arm in REPLAY_ARMS else ())
            for ps in reps:
                J.append({"job_id": f"{tag}|{arm}|{'u' if ps is None else ps}", "snap": snap, "arm": arm,
                          "config": cfg, "flags": {**revlib.CF, **fl}, "deterministic": True, "perturb": ps,
                          "t_q": e2_quench.T_Q, "blocker": blk, "stratum": CLS, "pool_k": k})
        for rep in range(N_NOISE):
            J.append({"job_id": f"{tag}|noise{SIGMA}|{rep}", "snap": snap, "arm": f"noise{SIGMA}",
                      "config": "C1", "flags": dict(revlib.CF), "sigma": SIGMA,
                      "noise_seed": NOISE_BASE + 100 * k + rep, "rep": rep, "deterministic": False,
                      "t_q": e2_quench.T_Q, "blocker": blk, "stratum": CLS, "pool_k": k})
    e2_seeds = {7000 + 100 * k + r for k in range(60) for r in range(N_NOISE)}
    assert not e2_seeds & {j["noise_seed"] for j in J if "noise_seed" in j}
    assert len({j["job_id"] for j in J}) == len(J)
    return J


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--include-e2", action="store_true")
    a = ap.parse_args(argv)
    J = jobs(a.include_e2, a.limit)
    n_snap = len({j["job_id"].split("|")[0] for j in J})
    print(f"A5: {len(J)} jobs on {n_snap} snapshots ({len(J) // max(n_snap, 1)} per snapshot)", flush=True)
    if a.dry:
        return
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    print("wall", revlib.run_jobs(J, e2_quench.quench_e2, os.path.abspath(a.out), workers=a.workers, log_every=1))


if __name__ == "__main__":
    main()
