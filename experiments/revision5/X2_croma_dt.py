"""X2 runs: CroMa time-step check completed to the 25-run sets (seeds 42-66) of the four Sect. 7 variants.

C3 (experiments/revision4/T4_croma_dt.py, data/revision4/T4/t4_croma.jsonl) ran seeds 42-51 at dt = 0.005 s and
dt = 0.01 s. This script runs the remaining seeds 52-66 (the rest of E10's / D3's 25 spawns, run type
RUNS[(seed - 42) % 5], same noise seeds) with C3's unchanged run function (T4_croma_dt.run: E10 run with a dt override,
trajectory stride round(0.04 / dt), per-step agent and wall overlap record) and job set (D3_croma_rerun.jobs):
  dt0.005  60 runs at dt = 0.005 s (per-step sigma* = 0.0467 m/s unchanged for C1_cf_sig);
  dt0.01   the same 60 runs at dt = 0.01 s, a reproduction of data/revision/D3/d3_croma.jsonl (end time, completion,
           passages must agree) that adds the overlap record the D3 runs lack.
Order: all dt0.005 jobs first, then dt0.01, each by seed. Budget: the queue stops submitting once the summed process
CPU of finished runs reaches 10 h (C4 rule); unfinished seeds are reported.
Output: data/revision5/X2/x2_croma.jsonl (job_id "<dtkey>|<cell>|seed<seed>"), trajectories data/revision5/X2/raw/.
Usage: X2_croma_dt.py [--workers W] [--only dt0.005|dt0.01]
"""
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev5lib  # noqa: E402
from rev5lib import ROOT  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments", "revision4"))
import T4_croma_dt as T4  # noqa: E402

OUTDIR = rev5lib.data_dir("X2")
OUT = os.path.join(OUTDIR, "x2_croma.jsonl")
RAW = os.path.join(OUTDIR, "raw")
SEEDS = range(52, 67)
BUDGET_CPU_S = 10 * 3600.0


def jobs(only=None):
    J = []
    for dk, dt in T4.DTS.items():
        if only and dk != only:
            continue
        for j in T4.D3.jobs(RAW):
            if j["seed"] not in SEEDS:
                continue
            J.append({**j, "job_id": f"{dk}|{j['job_id']}", "dtkey": dk, "dt": dt})
    J.sort(key=lambda j: (j["dtkey"] != "dt0.005", j["seed"], j["cell"]))
    return J


def main(only=None, workers=rev5lib.WORKERS):
    done, used = set(), 0.0
    if os.path.exists(OUT):
        for l in open(OUT):
            r = json.loads(l)
            done.add(r["job_id"])
            used += r["cpu_s"]
    todo = [j for j in jobs(only) if j["job_id"] not in done]
    print(f"[X2] {len(todo)} to run, {len(done)} done, cpu used {used / 3600:.2f} h", flush=True)
    ctx = mp.get_context("fork")
    t0 = time.perf_counter()
    with ctx.Pool(workers) as pool, open(OUT, "a") as f:
        pending = []
        it = iter(todo)
        stopped = False

        def submit():
            j = next(it, None)
            if j is not None:
                pending.append(pool.apply_async(T4.run, (j,)))
        for _ in range(workers):
            submit()
        while pending:
            time.sleep(2)
            for a in [a for a in pending if a.ready()]:
                pending.remove(a)
                r = a.get()
                f.write(json.dumps(r, default=float) + "\n")
                f.flush()
                used += r["cpu_s"]
                print(f"  {r['job_id']} cpu={r['cpu_s']:.0f}s total={used / 3600:.2f} h "
                      f"wall={time.perf_counter() - t0:.0f}s", flush=True)
                if used >= BUDGET_CPU_S:
                    stopped = True
                if not stopped:
                    submit()
    print("stopped at budget" if stopped else "all done", f"cpu {used / 3600:.2f} h", flush=True)


if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    main(only, rev5lib.workers(sys.argv))
