"""Tier 3 run queue (session C5, tasks 10-11): the replace couplings R1 and R2 (rev7lib.ARMS), RVO2 solver.
Run only after notes/C5_items/prereg_replace.md was committed (2ac5353). Priority order:
  T10a screening set (34 lone keystones + 26 second traps, data/derived/selection.json E2): quench as E2
       (e2_quench.quench_e2: CF + arm flags, dt 0.01 s, 120 s, stationary stop |v| < 1e-3 m/s for 10 s), once
       unperturbed and 5 replays (perturb seeds 900-904, 1e-9 m on every residual agent).
  T11  whole runs R1, R2 on seeds 242-301 (60), unperturbed, runlib.whole_run (as E6 / C3 task 1).
  T10b the 134 other second traps of the deadlock set (A5_extra_second_traps.pool), as T10a.
  T10c the 46 pair standoffs (e7b_quench.run, flags CF + B_w 0.04 + arm flags), unperturbed + 5 replays, horizon
       600 s with E7b's stopping rule (to rest: every |v| < 1e-3 m/s for 10 s), as task 1.
Outputs data/revision7/T10/t10_quench.jsonl, t10_pair.jsonl, data/revision7/T11/t11_whole.jsonl.
Usage: queue_q3.py [--workers W] [--only T10a,T11,T10b,T10c]"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402

RARMS = ("R1", "R2")
Q_OUT = os.path.join(L.data_dir("T10"), "t10_quench.jsonl")
P_OUT = os.path.join(L.data_dir("T10"), "t10_pair.jsonl")
W_OUT = os.path.join(L.data_dir("T11"), "t11_whole.jsonl")
SEEDS_T11 = list(range(242, 272))  # reduced from 242-301 (session C5 cost rule: R runs reach the 600 s cap, ~15 min
#                                     wall each under load; 60 seeds = ~30 CPU-h does not fit the 6 h tier-3 limit)


def _qjob(tag, snap, blk, cls, arm, ps, extra=None):
    cfg, fl = L.arm_cfg(arm)
    j = {"job_id": f"{tag}|{arm}|{'u' if ps is None else ps}", "snap": snap, "arm": arm, "config": cfg, "flags": fl,
         "deterministic": True, "perturb": ps, "t_q": 120.0, "blocker": blk, "stratum": cls}
    j.update(extra or {})
    return j


def t10a():
    sys.path.insert(0, os.path.join(L.ROOT, "experiments", "E2"))
    import e2_quench
    return [_qjob(t, s, b, c, a, ps) for t, s, b, c in e2_quench.snapshots() for a in RARMS
            for ps in (None,) + L.PERTURB_SEEDS]


def t10b():
    import A5_extra_second_traps as A5
    return [_qjob(t, s, b, A5.CLS, a, ps, {"pool_k": k}) for k, seed, t, s, b, in_e2 in A5.pool() if not in_e2
            for a in RARMS for ps in (None,) + L.PERTURB_SEEDS]


def t10c():
    sys.path.insert(0, os.path.join(L.ROOT, "experiments", "E7b"))
    import e7b_quench
    from e7b_pairs import pairs
    J = []
    for p in pairs():
        for a in RARMS:
            cfg, fl = L.ARMS[a]
            for ps in (None,) + L.PERTURB_SEEDS:
                J.append({"job_id": f"{p['tag']}|{a}|{'u' if ps is None else ps}", "snap": p["snap"], "arm": a,
                          "config": cfg, "flags": {**e7b_quench.BASE, **fl}, "deterministic": True, "perturb": ps,
                          "delta": None, "t_q": 600.0})
    return J


def t11():
    return [L.whole_job(a, s) for s in SEEDS_T11 for a in RARMS]


if __name__ == "__main__":
    assert os.path.exists(os.path.join(L.ROOT, "notes", "C5_items", "prereg_replace.md"))
    w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 2
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else ["T10a", "T11", "T10b", "T10c"]
    # priority (cost rule, session C5): every unperturbed run first, then the replays
    def U(f):
        return lambda: [j for j in f() if j["perturb"] is None]

    def P(f):
        return lambda: [j for j in f() if j["perturb"] is not None]
    T = {"T10a": (Q_OUT, "quench", U(t10a)), "T11": (W_OUT, "whole", t11), "T10b": (Q_OUT, "quench", U(t10b)),
         "T10c": (P_OUT, "pair", U(t10c)), "T10ar": (Q_OUT, "quench", P(t10a)), "T10cr": (P_OUT, "pair", P(t10c)),
         "T10br": (Q_OUT, "quench", P(t10b))}
    if "--only" not in sys.argv:
        only = ["T10a", "T10b", "T10c", "T11", "T10ar", "T10cr", "T10br"]
    print("wall", L.run_queue([(T[k][0], T[k][1], T[k][2]()) for k in only], w))
