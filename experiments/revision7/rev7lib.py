"""Shared helpers for the revision-7 evidence (session C5, experiments/revision7/).

Reuses experiments/revision/revlib.py (paths, statistics; w2lib sets cwd to code/) and adds:
  data_dir(name)          data/revision7/<name>/ for raw JSONL of new runs
  out_json(name, obj)     data/derived/rev7_<name>.json (registry source of notes/C5_items/*.yaml)
  whole_run_p(job)        runlib.whole_run with an optional 1e-9 m Gaussian displacement of every agent at spawn
                          (job["perturb"] = numpy default_rng seed; the paper's replay, applied to a whole run)
  run_queue(tasks, W)     one fork pool over jobs of several tasks, each written to its own JSONL file (resumable:
                          job_ids already in a file are skipped); tasks = [(out_path, fn_name, [jobs])] in priority
                          order
Arms (flags on top of CF, the corrected-forward set):
  sfm        C1                                   rvo2      C3 (w2_orca = rvo2)
  drive      C3, w2_orca_split = drive_only       tauprime  C1, sfm_tau_prime = on
  drive_veff C3, drive_only, orca_pref = veff     (task 8: the drive part with preferred velocity v_eff e)
  R1         C3, orca_replace = on, orca_pref = veff (RVO2)     R2   C3, orca_replace = on (RVO2, v0 e)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "revision"))
import revlib  # noqa: E402
from revlib import (CF, DATA, DERIVED, ROOT, holm, load_runs, mcnemar_exact, np, pdisp, run_jobs, sig,  # noqa: E402,F401
                    stats, wilson)
import runlib  # noqa: E402
from w2lib import done_ids  # noqa: E402

ARMS = {"sfm": ("C1", {}), "rvo2": ("C3", {}), "pub": ("C3", {"w2_orca": "published"}),
        "drive": ("C3", {"w2_orca_split": "drive_only"}), "tauprime": ("C1", {"sfm_tau_prime": "on"}),
        "drive_veff": ("C3", {"w2_orca_split": "drive_only", "orca_pref": "veff"}),
        "R1": ("C3", {"orca_replace": "on", "orca_pref": "veff"}), "R2": ("C3", {"orca_replace": "on"})}
SEEDS_WHOLE = list(range(242, 428))
PERTURB_SEEDS = (900, 901, 902, 903, 904)


def data_dir(name):
    d = os.path.join(DATA, "revision7", name)
    os.makedirs(d, exist_ok=True)
    return d


def out_json(name, obj):
    path = os.path.join(DERIVED, f"rev7_{name}.json")
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    return path


def arm_cfg(arm):
    cfg, fl = ARMS[arm]
    return cfg, {**CF, **fl}


def whole_job(arm, seed, perturb=None, t_max=600.0):
    cfg, fl = arm_cfg(arm)
    return {"job_id": f"{arm}|seed{seed}" + ("" if perturb is None else f"|p{perturb}"), "variant": arm, "seed": seed,
            "width": 0.8, "config": cfg, "flags": fl, "sigma": 0.0, "t_max": t_max, "perturb": perturb}


def whole_run_p(job):
    ps = job.get("perturb")
    if ps is None:
        return runlib.whole_run(job)
    orig = runlib.build

    def build_p(*a, **k):
        sim = orig(*a, **k)
        st = sim.state
        idx = st.active_indices
        st.positions[idx] += np.random.default_rng(ps).normal(0, 1e-9, (len(idx), 2))
        return sim
    runlib.build = build_p
    try:
        return runlib.whole_run(job)
    finally:
        runlib.build = orig


def _fns():
    sys.path.insert(0, os.path.join(ROOT, "experiments", "E7b"))
    sys.path.insert(0, os.path.join(ROOT, "experiments", "E2"))
    import e7b_quench
    import e2_quench
    import keystone_e6
    return {"whole": whole_run_p, "pair": e7b_quench.run, "quench": e2_quench.quench_e2, "keystone": keystone_e6.run}


_F = {}


def _call(item):
    out, fn, job = item
    if not _F:
        _F.update(_fns())
    try:
        r = _F[fn](job)
    except Exception as e:  # keep the queue alive; the failure is recorded and the job is retried on resume
        r = {"job_id": job["job_id"], "error": repr(e)}
    return out, r


def run_queue(tasks, workers, log_every=20):
    import multiprocessing as mp
    items = []
    for out, fn, J in tasks:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        done = {i for i in done_ids(out)}
        if os.path.exists(out):  # error records are retried
            done -= {json.loads(l)["job_id"] for l in open(out) if '"error"' in l}
        items += [(out, fn, j) for j in J if j["job_id"] not in done]
    print(f"[run_queue] {len(items)} jobs", flush=True)
    if not items:
        return 0.0
    t0 = time.perf_counter()
    fh = {}
    with mp.get_context("fork").Pool(min(workers, len(items))) as pool:
        for k, (out, r) in enumerate(pool.imap_unordered(_call, items, chunksize=1), 1):
            if out not in fh:
                fh[out] = open(out, "a")
            fh[out].write(json.dumps(r, default=float) + "\n")
            fh[out].flush()
            if k % log_every == 0 or "error" in r:
                print(f"  {k}/{len(items)} {r.get('job_id')} {'ERROR ' + r['error'] if 'error' in r else ''}"
                      f" wall={time.perf_counter() - t0:.0f}s", flush=True)
    for f in fh.values():
        f.close()
    return time.perf_counter() - t0


def load_ok(path):
    """Records of a JSONL file without error rows; the last record per job_id wins."""
    if not os.path.exists(path):
        return {}
    R = {}
    for r in load_runs(path):
        if "error" not in r:
            R[r["job_id"]] = r
    return R
