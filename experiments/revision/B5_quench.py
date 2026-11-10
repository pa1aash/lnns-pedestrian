"""B5 quench: pair quenches with rounded jamb ends (dynamics; queued run set).

Every run restarts a pair snapshot of experiments/E7b/e7b_pairs.py with C1 and the full flag set
CF union {B_w: 0.04} union {edge: rounded, edge_radius: r_c} union arm flags, dt = 0.01 s. Arms:
  b0     r_c = 0.1 m, b = 0, from the sharp-edge snapshot positions (the dynamic counterpart of the static
         re-equilibration in B5_static.py reequil, where no member pair is held); 120 s, deterministic
         stationary stop (every active |v| < 1e-3 m/s for 10 s, no exit), as experiments/E7b/e7b_quench.py.
  fold   r_c = RC_CONT (0.02 m), for every (snapshot, sign) whose rounded rest state is a strict minimum:
         lateral bias b = sign b_f (1 + eps), eps in {0.01, 0.03, 0.1, 0.3}, b_f the continuation fold of
         B5_static.py cont (natural-continuation loss point b_last where the corrector failed; the source is
         recorded); from the rounded minimum (members placed at B5_static's re-equilibrated positions, v = 0);
         300 s, no stationary stop (as runs3/N6.py quench). Passage time = first exit.
  grid   r_c = RC_CONT, the same strict minima, the E7b bias values b in {+-0.01, +-0.02, +-0.03, 0.05, 0.1},
         from the rounded minimum, 120 s, deterministic stationary stop: static (|b| beyond the bisection
         threshold b*_s of B5_static.py bisect frees) against quench agreement.
Recorded as e7b_quench.run: exits, first member and side, stationary stop, final positions.
Output: data/revision/B5/quench.jsonl (job_id "<arm>|rc<r_c>|<tag>|<b or sign|eps>"), resumable.
Usage: B5_quench.py [qargs options]   (needs data/revision/B5/{reequil,cont,bisect}.jsonl)
"""
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402
import B5_static as S  # noqa: E402
import numpy as np  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402
from w2lib import StationaryDetector, restore  # noqa: E402

OUT = os.path.join(S.D, "quench.jsonl")
BASE = {**revlib.CF, "B_w": 0.04}
EPS = (0.01, 0.03, 0.1, 0.3)
BGRID = (-0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.05, 0.1)


def run(job):
    snap = pickle.load(open(job["snap"], "rb"))
    sim = restore(snap, "C1", flags=dict(job["flags"]))
    st = sim.state
    ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
    side = {i: ("lower" if st.positions[i, 1] < 5.0 else "upper") for i in ids}
    if job.get("X0") is not None:
        st.positions[ids] = np.array(job["X0"]).reshape(-1, 2)
        st.velocities[ids] = 0.0
    t0, w0 = sim.time, time.perf_counter()
    exits = {}
    det = StationaryDetector(hold=10.0, v_thr=1e-3) if job["deterministic"] else None
    stationary = False
    for _ in range(int(round(job["t_q"] / sim.params["dt"]))):
        prev = st.active.copy()
        sim.step()
        st = sim.state
        for i in np.where(prev & ~st.active)[0]:
            exits[int(i)] = sim.time - t0
        if st.n_active == 0:
            break
        if det is not None and det.update(sim):
            stationary = True
            break
    first = min(exits, key=exits.get) if exits else None
    out = {k: v for k, v in job.items() if k not in ("snap", "X0")}
    out.update({"snap": os.path.basename(job["snap"]), "members": ids, "side": side, "exits": exits,
                "n_freed": len(exits), "freed": bool(exits), "all_freed": len(exits) == len(ids),
                "first_side": side.get(first), "first_t": exits.get(first), "stationary_stop": stationary,
                "t_run": sim.time - t0, "wall_s": time.perf_counter() - w0,
                "final_pos": {int(i): st.positions[i].tolist() for i in ids if st.active[i]}})
    return out


def jobs():
    J = []
    rnd = {"edge": "rounded", "edge_radius": S.RC_MAIN}
    for p in pairs():
        J.append({"job_id": f"b0|rc{S.RC_MAIN:g}|{p['tag']}", "arm": "b0", "tag": p["tag"], "snap": p["snap"],
                  "rc": S.RC_MAIN, "b": 0.0, "flags": {**BASE, **rnd}, "deterministic": True, "t_q": 120.0})
    load = lambda n: {r["job_id"]: r for r in revlib.load_runs(os.path.join(S.D, n))} \
        if os.path.exists(os.path.join(S.D, n)) else {}
    C, B = load("cont.jsonl"), load("bisect.jsonl")
    for rc in S.RC_CONT:
        K = S.kept_rest(rc)
        rnd = {"edge": "rounded", "edge_radius": rc}
        for p in pairs():
            if p["tag"] not in K:
                continue
            X0 = K[p["tag"]]["X"]
            for s in (1, -1):
                key = f"rc{rc:g}|{p['tag']}|{s:+d}"
                c = C.get(key, {})
                bf, src = c.get("b_f"), "continuation"
                if bf is None and c.get("natural"):
                    bf, src = c["natural"]["b_last"], "natural"
                if bf is None:
                    continue
                for e in EPS:
                    b = s * bf * (1 + e)
                    J.append({"job_id": f"fold|{key}|eps{e:g}", "arm": "fold", "tag": p["tag"], "snap": p["snap"],
                              "rc": rc, "sign": s, "eps": e, "b_f": bf, "b_f_source": src, "b": b, "X0": X0,
                              "flags": {**BASE, **rnd, "w2_noise": "lateral_bias", "w2_bias_b": b},
                              "deterministic": False, "t_q": 300.0})
            for b in BGRID:
                s = 1 if b > 0 else -1
                bs = B.get(f"rc{rc:g}|{p['tag']}|{s:+d}", {}).get("b_star")
                J.append({"job_id": f"grid|rc{rc:g}|{p['tag']}|b{b:g}", "arm": "grid", "tag": p["tag"],
                          "snap": p["snap"], "rc": rc, "b": b, "sign": s, "b_star": bs,
                          "static_freed": None if bs is None else bool(abs(b) > bs), "X0": X0,
                          "flags": {**BASE, **rnd, "w2_noise": "lateral_bias", "w2_bias_b": b},
                          "deterministic": True, "t_q": 120.0})
    return J


def main(argv=None):
    a = qargs.parse(argv)
    return revlib.run_jobs(qargs.select(jobs(), a), run, a.out or OUT, workers=a.workers, log_every=20)


if __name__ == "__main__":
    print("wall", main())
