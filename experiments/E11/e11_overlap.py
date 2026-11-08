"""E11: persistence-filtered agent-agent overlap, room bottleneck, corrected-forward (CF), 50 agents,
300 s cap, full metrics (w2_metrics = full: the code's per-step collision count is kept as a cross-check).
Cells: C1, C2, C3_rvo2, C4_rvo2 (CF: RVO2 ORCA, crush off) at w in {1.0, 1.2, 1.8} m, plus C3_pub (CF
numerics, published ORCA) at w = 1.0 m; 25 seeds per cell (42-66, the same seeds in every cell).
dt = 0.01 s; the run stops at completion, at deadlock (every active |v| < 0.01 m/s for 10 s, no exit;
recorded, overlaps then frozen) or at 300 s.
Overlap: an active pair (i, j) with |x_i - x_j| < r_i + r_j at the end of a step. Zone of a pair = zone of
its midpoint: upstream x < 8, throat 8 <= x <= 10.5, downstream x > 10.5 m.
Recorded per run and zone: overlap pair-steps; overlap timesteps (steps with at least one overlapping pair
in the zone); episodes (maximal runs of consecutive overlapping steps of one pair; zone at the episode's
first step), all and those lasting >= 0.1 s (>= 10 steps), with their durations and maximum depth; open
episodes at the end of the run are closed there and flagged. Also completion, evacuation time, exits.
Output: data/E11/e11_overlap.jsonl (job_id "<cell>|seed<seed>"), resumable.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
from e1lib import CF, DATA, run_jobs  # noqa: E402
from w2lib import StationaryDetector, build  # noqa: E402
import numpy as np  # noqa: E402
import qargs  # noqa: E402

OUT = os.path.join(DATA, "E11", "e11_overlap.jsonl")
ARMS = {"C1": ("C1", {}), "C2": ("C2", {}), "C3_rvo2": ("C3", {"w2_orca": "rvo2"}),
        "C4_rvo2": ("C4", {"w2_orca": "rvo2", "w2_crush": "off"})}
WIDTHS = (1.0, 1.2, 1.8)
SEEDS = range(42, 67)
ZONES = ("upstream", "throat", "downstream")
MIN_STEPS = 10   # 0.1 s at dt = 0.01 s


def zone_of(x):
    return 0 if x < 8.0 else (1 if x <= 10.5 else 2)


def run(job):
    w0 = time.perf_counter()
    sim = build(job["config"], seed=job["seed"], width=job["width"], n_agents=50, flags=job["flags"], light=False)
    st = sim.state
    dt = sim.params["dt"]
    r = st.radii
    pair_steps = np.zeros(3, int)
    ov_steps = np.zeros(3, int)
    open_ep = {}          # (i, j) -> [start_step, zone, max_depth, length]
    eps = []
    code_coll = 0
    det = StationaryDetector()
    deadlock = False
    exits = {}
    k = 0
    while sim.time < job["t_max"] - 1e-9 and st.n_active > 0:
        prev = st.active.copy()
        m = sim.step()
        k += 1
        st = sim.state
        code_coll += m.get("collision_count", 0)
        for i in np.where(prev & ~st.active)[0]:
            exits[int(i)] = sim.time
        a = st.active_indices
        now = set()
        if len(a) > 1:
            P = st.positions[a]
            D = np.linalg.norm(P[:, None] - P[None], axis=2)
            I, J = np.where(np.triu(D < (r[a][:, None] + r[a][None]), 1))
            if len(I):
                mid = 0.5 * (P[I, 0] + P[J, 0])
                z = np.array([zone_of(x) for x in mid])
                pair_steps += np.bincount(z, minlength=3)
                ov_steps += np.bincount(np.unique(z), minlength=3)
                depth = r[a][I] + r[a][J] - D[I, J]
                for ii, jj, zz, dd in zip(a[I], a[J], z, depth):
                    key = (int(ii), int(jj))
                    now.add(key)
                    e = open_ep.get(key)
                    if e is None:
                        open_ep[key] = [k, int(zz), float(dd), 1]
                    else:
                        e[2] = max(e[2], float(dd)); e[3] += 1
        for key in [q for q in open_ep if q not in now]:
            s0, zz, dd, n = open_ep.pop(key)
            eps.append((key, s0, zz, dd, n, False))
        if det.update(sim):
            deadlock = True
            break
    for key, (s0, zz, dd, n) in open_ep.items():
        eps.append((key, s0, zz, dd, n, True))
    by = {}
    for zi, zn in enumerate(ZONES):
        E = [e for e in eps if e[2] == zi]
        L = [e for e in E if e[4] >= MIN_STEPS]
        by[zn] = {"pair_steps": int(pair_steps[zi]), "overlap_timesteps": int(ov_steps[zi]),
                  "episodes_all": len(E), "episodes_ge_0.1s": len(L),
                  "pairs_with_episode_ge_0.1s": len({e[0] for e in L}),
                  "episode_dur_s_ge_0.1s": [round(e[4] * dt, 2) for e in L],
                  "episode_max_depth_m_ge_0.1s": [round(e[3], 4) for e in L],
                  "open_at_end_ge_0.1s": sum(e[5] for e in L)}
    out = dict(job)
    out.update({"dt": dt, "t_end": sim.time, "complete": st.n_active == 0, "deadlock": deadlock,
                "n_remaining": int(st.n_active), "evacuation_time": sim.time if st.n_active == 0 else None,
                "exit_t": exits, "zones": by, "overlap_pair_steps_total": int(pair_steps.sum()),
                "code_collision_count_total": int(code_coll), "steps": k, "wall_s": time.perf_counter() - w0})
    return out


def jobs():
    cells = [(f"{a}|w{w}", a, w) for w in WIDTHS for a in ARMS] + [("C3_pub|w1.0", "C3_pub", 1.0)]
    J = []
    for cell, arm, w in cells:
        cfg, fl = ("C3", {"w2_orca": "published"}) if arm == "C3_pub" else ARMS[arm]
        for s in SEEDS:
            J.append({"job_id": f"{cell}|seed{s}", "cell": cell, "arm": arm, "width": w, "seed": s,
                      "config": cfg, "flags": {**CF, **fl}, "t_max": 300.0})
    return J


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run_jobs(qargs.select(jobs(), a), run, out, workers=a.workers, log_every=10)


if __name__ == "__main__":
    print("wall", main())
