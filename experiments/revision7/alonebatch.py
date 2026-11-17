"""Batched alone-condition escape (session C5, task 2): R independent restarts of one blocker, integrated together.

Each replica is the blocker of a library snapshot with every other agent deactivated (runlib.escape, cond
"alone"), so it feels only its own desired force (density 0, no neighbours) and the wall forces. The force is the
code's own HybridSteeringModel.compute_forces called on an AgentState that holds the R replicas with empty
neighbour lists and density 0 (no agent-agent term, as alone); the update is Simulation.step's fixed-numerics
branch line by line (clamp to 2 v0, per-step noise, re-clamp, x += v dt, goal deactivation); escape = blocker
centre x >= 10 m or deactivated, as runlib.escape. Noise: replica j owns Generator(PCG64(seed_j)) and draws
normal(0, sigma, (n_total, 2)) per step, of which only the blocker's row is used, exactly as the full simulation
(drawn in blocks of K steps, which yields the same stream). Hence escape times equal runlib.escape's to the step
(checked against data/E4/e4_escape.jsonl by validate()).
"""
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
from e1lib import CF  # noqa: E402
from w2lib import restore  # noqa: E402
import numpy as np  # noqa: E402
from sim.core import helpers as H  # noqa: E402
from sim.core.agent import AgentState  # noqa: E402
from sim.core.helpers import clamp_speed  # noqa: E402

BLOCK = 2000


def run_batch(snap_path, blocker, sigma, seeds, t_cens, dt=None, flags=None, config="C1"):
    snap = pickle.load(open(snap_path, "rb"))
    sim = restore(snap, config, flags=dict(CF if flags is None else flags), noise=sigma, noise_seed=int(seeds[0]),
                  dt=dt)
    st = sim.state
    p = sim.params
    assert p.get("w2_numerics") == "fixed"
    H.CLIP_MODE = "none"
    b, n_tot, R = blocker, st.n, len(seeds)
    dt = p["dt"]
    tile = lambda a: np.repeat(np.asarray(a)[None, b], R, axis=0).copy()  # noqa: E731
    rs = AgentState(tile(st.positions), tile(st.velocities), tile(st.goals), tile(st.radii), tile(st.desired_speeds),
                    tile(st.masses), tile(st.taus), np.ones(R, bool))
    gens = [np.random.Generator(np.random.PCG64(int(s))) for s in seeds]
    alive = np.arange(R)
    esc = np.full(R, np.nan)
    nsteps = int(round(t_cens / dt))
    t0 = sim.time
    t = sim.time
    steer, walls, grd = sim.steering, sim.world.walls, p["goal_reached_dist"]
    noise_on = sigma > 0
    k = 0
    w0 = time.perf_counter()
    while k < nsteps and len(alive):
        K = min(BLOCK, nsteps - k)
        if noise_on:
            NZ = np.stack([gens[j].normal(0, sigma, (K, n_tot, 2))[:, b, :] for j in alive], axis=1)  # (K, A, 2)
        for kk in range(K):
            A = len(alive)
            forces = steer.compute_forces(rs, [[] for _ in range(A)], walls, np.zeros(A))
            maxs = 2.0 * rs.desired_speeds
            nv = clamp_speed(rs.velocities + forces / rs.masses[:, None] * dt, maxs)
            if noise_on:
                nv = nv + NZ[kk]
                nv = clamp_speed(nv, maxs)
            rs.positions = rs.positions + nv * dt
            rs.velocities = nv
            t += dt
            gone = (np.linalg.norm(rs.goals - rs.positions, axis=1) < grd) | (rs.positions[:, 0] >= 10.0)
            if gone.any():
                esc[alive[gone]] = t - t0
                keep = ~gone
                alive = alive[keep]
                if noise_on:
                    NZ = NZ[:, keep]
                rs = AgentState(rs.positions[keep], rs.velocities[keep], rs.goals[keep], rs.radii[keep],
                                rs.desired_speeds[keep], rs.masses[keep], rs.taus[keep], np.ones(int(keep.sum()), bool))
                if not len(alive):
                    break
        k += K
    return {"escape_t": [None if np.isnan(x) else float(x) for x in esc], "t_run_max": t - t0,
            "wall_s": time.perf_counter() - w0, "steps": k}


def validate(n=20, tag="E1b_seed72", beta=1.5):
    """Compare with runlib.escape records of E4 (alone): returns max |dt_escape| and censoring agreement."""
    import json
    from e1lib import DATA, ROOT
    R = [json.loads(l) for l in open(os.path.join(DATA, "E4", "e4_escape.jsonl"))]
    R = [r for r in R if r["cond"] == "alone" and r["job_id"].startswith(tag + "|") and r["beta_ref"] == beta]
    R.sort(key=lambda r: r["rep"])
    R = R[:n]
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    snap = [os.path.join(ROOT, s["snap"]) for s in sel["E4"]["snapshots"] if s["tag"] == tag][0]
    out = run_batch(snap, R[0]["blocker"], R[0]["sigma"], [r["noise_seed"] for r in R], R[0]["t_cens"])
    pairs = list(zip([r["escape_t"] for r in R], out["escape_t"]))
    same_c = all((a is None) == (b_ is None) for a, b_ in pairs)
    d = max((abs(a - b_) for a, b_ in pairs if a is not None and b_ is not None), default=0.0)
    return {"n": len(R), "censor_agree": same_c, "max_abs_diff_s": d, "wall_s": out["wall_s"], "pairs": pairs}


if __name__ == "__main__":
    import json
    print(json.dumps(validate(*(sys.argv[1:2] and [int(sys.argv[1])] or [])), default=float))


_SNAPS = {}


def _load(path):
    if path not in _SNAPS:
        _SNAPS[path] = pickle.load(open(path, "rb"))
    return _SNAPS[path]


def run_multi(specs, dt=0.01, log=None):
    """specs: list of dicts with snap (path), blocker, sigma, noise_seed, t_cens, key. All snapshots must share the
    wall geometry (asserted). Returns {key: (escape_t or None, t_run)}; the escape time of each replica equals
    runlib.escape's for the same (snapshot, blocker, sigma, noise_seed, t_cens) (see run_batch)."""
    sims = {}
    for s in specs:
        if s["snap"] not in sims:
            sims[s["snap"]] = restore(_load(s["snap"]), "C1", flags=dict(CF), noise=s["sigma"], noise_seed=1, dt=dt)
    ref = next(iter(sims.values()))
    wref = [(w.start.tobytes(), w.end.tobytes(), w.radius) for w in ref.world.walls]
    for sm in sims.values():
        assert [(w.start.tobytes(), w.end.tobytes(), w.radius) for w in sm.world.walls] == wref
        assert sm.params["dt"] == ref.params["dt"] and sm.params.get("w2_numerics") == "fixed"
    H.CLIP_MODE = "none"
    steer, walls, grd = ref.steering, ref.world.walls, ref.params["goal_reached_dist"]
    R = len(specs)
    def col(attr):  # noqa: E306
        return np.stack([np.asarray(getattr(sims[s["snap"]].state, attr))[s["blocker"]] for s in specs])
    pos, vel, goals, radii, v0, mass, taus = (col(a) for a in ("positions", "velocities", "goals", "radii",
                                                                  "desired_speeds", "masses", "taus"))
    sig = np.array([s["sigma"] for s in specs], float)
    ntot = [sims[s["snap"]].state.n for s in specs]
    blk = [s["blocker"] for s in specs]
    t0 = np.array([sims[s["snap"]].time for s in specs])
    t = t0.copy()
    nmax = np.array([int(round(s["t_cens"] / dt)) for s in specs])
    gens = [np.random.Generator(np.random.PCG64(int(s["noise_seed"]))) for s in specs]
    alive = np.arange(R)
    esc = np.full(R, np.nan)
    trun = np.zeros(R)
    k = 0
    w0 = time.perf_counter()
    while len(alive):
        K = int(min(BLOCK, nmax[alive].max() - k))
        NZ = np.stack([gens[j].normal(0, sig[j], (K, ntot[j], 2))[:, blk[j], :] for j in alive], axis=1)
        for kk in range(K):
            A = len(alive)
            rs = AgentState(pos, vel, goals, radii, v0, mass, taus, np.ones(A, bool))
            forces = steer.compute_forces(rs, [[] for _ in range(A)], walls, np.zeros(A))
            maxs = 2.0 * v0
            nv = clamp_speed(vel + forces / mass[:, None] * dt, maxs)
            nz = NZ[kk]
            on = sig[alive] > 0
            if on.all():
                nv = clamp_speed(nv + nz, maxs)
            elif on.any():
                nv2 = clamp_speed(nv + nz, maxs)
                nv = np.where(on[:, None], nv2, nv)
            pos = pos + nv * dt
            vel = nv
            ta = t[alive] + dt
            t[alive] = ta
            gone = (np.linalg.norm(goals - pos, axis=1) < grd) | (pos[:, 0] >= 10.0)
            cens = (~gone) & (k + kk + 1 >= nmax[alive])
            if gone.any() or cens.any():
                esc[alive[gone]] = ta[gone] - t0[alive[gone]]
                fin = gone | cens
                trun[alive[fin]] = ta[fin] - t0[alive[fin]]
                keep = ~fin
                alive = alive[keep]
                NZ = NZ[:, keep]
                pos, vel, goals, radii, v0, mass, taus = (a[keep] for a in (pos, vel, goals, radii, v0, mass, taus))
                if not len(alive):
                    break
        k += K
        if log:
            log(f"  step {k} alive {len(alive)} wall {time.perf_counter() - w0:.0f}s")
    return {s["key"]: (None if np.isnan(esc[j]) else float(esc[j]), float(trun[j])) for j, s in enumerate(specs)}
