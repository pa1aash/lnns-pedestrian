"""Open geometries with a variable start density (E8, E9), and the stall-cluster detector of the pilot
(wave2/scripts/w267_analyze.py, unchanged rules).

BidirDensity(n, L)    sim.scenarios.open_geometries.OpenBidirectionalScenario with the two start blocks
                      L m long (3 m wide, front edges fixed at x = 2 and x = 18 as in the scenario) instead
                      of 12 m; the corridor walls are extended to 2 m beyond the blocks when they would not
                      cover them. L = 12 reproduces the scenario exactly (checked in the smoke test).
CrossDensity(n, L)    sim.scenarios.open_geometries.OpenCrossingScenario with the two start blocks L m long
                      (3 m wide, front edges at y = -1 and x = -1) instead of 17 m; the closed south and west
                      arms are extended to 2 m beyond the blocks when needed. L = 17 reproduces the scenario.
Start density = n / (3 L) per block. Sinks, goals, leak polygon and line goals are the scenario's.
events(frames, zone)  stall clusters (>= 2 agents, speed < 0.05 m/s, single linkage within 1.0 m, inside
                      the zone), tracked frame to frame by member overlap; an event is a cluster persisting
                      >= 2 s. Frames every 0.1 s: rows (t, id, x, y, vx, vy).
"""
import numpy as np
from scipy.sparse.csgraph import connected_components
from sim.core.agent import AgentState
from sim.core.world import Wall, World
from sim.scenarios.open_geometries import OpenBidirectionalScenario, OpenCrossingScenario, _merge

V_THR, LINK, MIN_DUR, FRAME = 0.05, 1.0, 2.0, 0.1


class BidirDensity(OpenBidirectionalScenario):
    def __init__(self, n_per_direction=50, L=12.0, spawn="rejection"):
        super().__init__(n_per_direction, spawn)
        self.L = L
        self.X_MIN = min(-12.0, 2.0 - L - 2.0)
        self.X_MAX = max(32.0, 18.0 + L + 2.0)

    def build(self, seed=42):
        walls = [Wall(np.array([self.X_MIN, 0.0]), np.array([self.X_MAX, 0.0])),
                 Wall(np.array([self.X_MAX, self.H]), np.array([self.X_MIN, self.H])),
                 Wall(np.array([self.X_MIN, self.H]), np.array([self.X_MIN, 0.0])),
                 Wall(np.array([self.X_MAX, 0.0]), np.array([self.X_MAX, self.H]))]
        n = self.n_per_direction
        area_r, area_l = (2.0 - self.L, 2.0, 0.3, 3.3), (18.0, 18.0 + self.L, 0.3, 3.3)
        a = AgentState.create(n, spawn_area=area_r, goals=np.array([40.0, 1.8]), seed=seed)
        b = AgentState.create(n, spawn_area=area_l, goals=np.array([-20.0, 1.8]), seed=seed + 1000)
        if self.spawn == "rejection":
            from sim.core.spawn import respawn_rejection
            respawn_rejection(a, area_r, seed)
            respawn_rejection(b, area_l, seed + 1000)
        a.goals[:, 1] = a.positions[:, 1]
        b.goals[:, 1] = b.positions[:, 1]
        self.direction = np.concatenate([np.ones(n), -np.ones(n)])
        return World(walls), _merge(a, b)


class CrossDensity(OpenCrossingScenario):
    def __init__(self, n_per_stream=100, L=17.0, spawn="rejection"):
        super().__init__(n_per_stream, spawn)
        self.L = L
        self.NEAR = min(-20.0, -1.0 - L - 2.0)

    def build(self, seed=42):
        lo, hi, far, near = self.LO, self.HI, self.FAR, self.NEAR
        P = lambda x, y: np.array([x, y], float)  # noqa: E731
        walls = [
            Wall(P(lo, near), P(lo, lo)), Wall(P(lo, lo), P(near, lo)),
            Wall(P(hi, near), P(hi, lo)), Wall(P(hi, lo), P(far, lo)),
            Wall(P(lo, far), P(lo, hi)), Wall(P(lo, hi), P(near, hi)),
            Wall(P(hi, far), P(hi, hi)), Wall(P(hi, hi), P(far, hi)),
            Wall(P(lo, near), P(hi, near)), Wall(P(near, lo), P(near, hi)),
        ]
        n = self.n_per_stream
        area_n, area_e = (3.5, 6.5, -1.0 - self.L, -1.0), (-1.0 - self.L, -1.0, 3.5, 6.5)
        a = AgentState.create(n, spawn_area=area_n, goals=np.array([5.0, 30.0]), seed=seed)
        b = AgentState.create(n, spawn_area=area_e, goals=np.array([30.0, 5.0]), seed=seed + 2000)
        if self.spawn == "rejection":
            from sim.core.spawn import respawn_rejection
            respawn_rejection(a, area_n, seed)
            respawn_rejection(b, area_e, seed + 2000)
        self.stream = np.concatenate([np.zeros(n, int), np.ones(n, int)])
        return World(walls), _merge(a, b)


def _clusters(P):
    if len(P) < 2:
        return []
    D = np.linalg.norm(P[:, None] - P[None], axis=2) < LINK
    n, lab = connected_components(D, directed=False)
    return [np.where(lab == k)[0] for k in range(n) if (lab == k).sum() >= 2]


def events(frames, zone):
    """frames: list of arrays (t, id, x, y, vx, vy), one per 0.1 s frame. Returns (events, occupied_s)."""
    open_ev, done = [], []
    occupied = 0.0
    for F in frames:
        if not len(F):
            continue
        t = F[0, 0]
        z = zone(F[:, 2:4])
        if z.any():
            occupied += FRAME
        sp = np.linalg.norm(F[:, 4:6], axis=1)
        m = z & (sp < V_THR)
        ids = F[m, 1].astype(int)
        cl = [set(ids[c]) for c in _clusters(F[m, 2:4])]
        new_open = []
        for c in cl:
            match = next((e for e in open_ev if e["members"] & c), None)
            if match:
                match["members"] = c; match["t1"] = t; match["max_size"] = max(match["max_size"], len(c))
                new_open.append(match); open_ev.remove(match)
            else:
                new_open.append({"t0": t, "t1": t, "members": c, "max_size": len(c)})
        done.extend(open_ev)
        open_ev = new_open
    for e in open_ev:
        e["censored"] = True
    done.extend(open_ev)
    ev = [{"t0": float(e["t0"]), "dur": float(e["t1"] - e["t0"] + FRAME), "max_size": e["max_size"],
           "censored": e.get("censored", False)} for e in done if e["t1"] - e["t0"] + FRAME >= MIN_DUR]
    return ev, occupied


def open_run(job):
    """One open-geometry run (pattern of the pilot wave2/scripts/w26_w27_open.py): fixed window job["T"]
    (or until every agent is sunk), frames of active agents every 10 steps (0.1 s) kept in memory for the
    stall detector (not saved). job: scen ("bidir" | "cross"), n, L, config, flags (full set), seed, T."""
    import time
    import lpcount
    from w2lib import SCEN_KEYS, Simulation
    w0 = time.perf_counter()
    lpcount.reset()
    if job["scen"] == "bidir":
        sc = BidirDensity(job["n"], job["L"], spawn="rejection")
        zone = lambda P: (P[:, 0] >= 0) & (P[:, 0] <= 20)  # noqa: E731
    else:
        sc = CrossDensity(job["n"], job["L"], spawn="rejection")
        zone = lambda P: (P[:, 0] >= 3.2) & (P[:, 0] <= 6.8) & (P[:, 1] >= 3.2) & (P[:, 1] <= 6.8)  # noqa: E731
    params = {k: v for k, v in job["flags"].items() if k not in SCEN_KEYS}
    params["w2_metrics"] = "light"
    sim = Simulation.from_scenario(sc, job["config"], seed=job["seed"], param_overrides=params)
    frames, speeds = [], []
    for _ in range(int(round(job["T"] / sim.params["dt"]))):
        sim.step()
        if sim.step_count % 10 == 0:
            a = sim.state.active_indices
            F = np.column_stack([np.full(len(a), sim.time), a, sim.state.positions[a], sim.state.velocities[a]])
            frames.append(F)
            z = zone(F[:, 2:4])
            if z.any():
                speeds.append(np.linalg.norm(F[z, 4:6], axis=1))
        if sim.state.n_active == 0:
            break
    ev, occ = events(frames, zone)
    grp = sc.direction if job["scen"] == "bidir" else sc.stream
    sink = [(float(t), int(i), float(grp[i])) for t, i in sim.sink_log]
    groups = sorted(set(float(g) for g in grp))
    out = dict(job)
    out.update({"start_density_per_m2": job["n"] / (3.0 * job["L"]), "dt": sim.params["dt"], "t_end": sim.time,
                "n_sunk": len(sink), "sunk_by_group": {str(g): sum(1 for s in sink if s[2] == g) for g in groups},
                "throughput_per_s": len(sink) / sim.time, "sink_log": sink,
                "n_leaked": len(sim.leaked), "leaked": sorted(sim.leaked),
                "mean_speed_zone": float(np.concatenate(speeds).mean()) if speeds else None,
                "events": ev, "n_events": len(ev), "zone_occupied_s": occ,
                "lifetime_max_s": max((e["dur"] for e in ev), default=None),
                "lp": lpcount.snapshot(), "big_force_events": getattr(sim, "big_force_events", None),
                "wall_s": time.perf_counter() - w0,
                "ms_per_step": 1e3 * (time.perf_counter() - w0) / max(sim.step_count, 1)})
    return out
