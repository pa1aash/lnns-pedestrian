"""A10: replay of the E2 noise quench with the noise stream held fixed.

Inputs: the 34 lone-keystone snapshots of E2 (data/derived/selection.json, class lone_keystone, selection order
k = 0..33, from experiments/selection.py), their blocker, and the stored E2 noise runs (data/E2/e2_quench.jsonl,
arm noise0.07) for the reference check.
Method: each E2 noise quench (C1 + CF flags, sigma = 0.07 m/s per-step velocity noise, noise seed
7000 + 100 k + rep, rep 0-4, dt = 0.01 s, full 120 s window, runner experiments/lib/runlib.quench) is run twice:
  ref     exactly as E2 (no perturbation); checked against the stored E2 record (exits, final positions, t_run)
  replay  every residual agent displaced by 1e-9 m Gaussian (numpy default_rng(900 + rep), as runlib.quench does
          for the deterministic replays), with the SAME noise seed.
The noise stream lives in the simulation's own generator (seeded by the noise seed in w2lib.restore); the
displacement uses a separate generator, so both runs draw the same noise sequence.
Recorded per run: blocker freed within 120 s, blocker exit time, all exits; for ref the bit-for-bit match flag.
Output: data/revision2/A10/a10.jsonl (job_id "<snap>|rep<r>|<ref|replay>"), resumable.
Analysis: experiments/revision2/A10_analyze.py.  Usage: A10_noise_replay.py [qargs options]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import CF, DATA, ROOT, load_runs, run_jobs  # noqa: E402
import qargs  # noqa: E402
from runlib import quench  # noqa: E402

SIGMA, T_Q, N_REP, PERTURB0 = 0.07, 120.0, 5, 900
E2_OUT = os.path.join(DATA, "E2", "e2_quench.jsonl")
_E2 = {}


def snapshots():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))["E2"]["snapshots"]
    out = [(k, s) for k, s in enumerate(sel) if s["class"] == "lone_keystone"]
    assert len(out) == 34 and [k for k, _ in out] == list(range(34))
    return out


def jobs():
    J = []
    for k, s in snapshots():
        for rep in range(N_REP):
            for kind in ("ref", "replay"):
                J.append({"job_id": f"{s['tag']}|rep{rep}|{kind}", "tag": s["tag"], "kind": kind, "rep": rep,
                          "snap": os.path.join(ROOT, s["snap"]), "config": "C1", "flags": dict(CF),
                          "sigma": SIGMA, "noise_seed": 7000 + 100 * k + rep,
                          "perturb": PERTURB0 + rep if kind == "replay" else None,
                          "deterministic": False, "t_q": T_Q, "blocker": s["blocker"]})
    return J


def e2_ref(tag, rep):
    if not _E2:
        for r in load_runs(E2_OUT):
            if r["arm"] == f"noise{SIGMA}":
                _E2[r["job_id"]] = r
    return _E2.get(f"{tag}|noise{SIGMA}|{rep}")


def run(job):
    r = quench(job)
    t = r["exits"].get(job["blocker"])
    r["blocker_freed"] = t is not None and t <= T_Q + 1e-9
    r["blocker_exit_t"] = t
    r["ref_match"] = None
    if job["kind"] == "ref" and abs(job["t_q"] - T_Q) < 1e-9:
        e = e2_ref(job["tag"], job["rep"])
        if e is not None:
            # JSON round trip gives the stored form (string keys) for an exact comparison
            mine = json.loads(json.dumps({"exits": r["exits"], "final_pos": r["final_pos"], "t_run": r["t_run"]}))
            r["ref_match"] = (mine["exits"] == e["exits"] and mine["final_pos"] == e["final_pos"]
                              and mine["t_run"] == e["t_run"] and e["noise_seed"] == job["noise_seed"])
    return r


if __name__ == "__main__":
    a = qargs.parse()
    out = a.out or os.path.join(rev2lib.data_dir("A10"), "a10.jsonl")
    run_jobs(qargs.select(jobs(), a), run, out, workers=a.workers, log_every=10)
