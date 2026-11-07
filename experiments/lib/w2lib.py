"""Shared experiment helpers (ported from the pilot wave2/scripts/w2lib.py; behaviour unchanged).

All flags are passed as param_overrides keys (w2_numerics, w2_noise, w2_bias_b,
w2_goal, w2_orca, w2_orca_split, w2_orca_transform, A_w, B_w, w2_metrics) plus
scenario options (spawn, edge). Defaults reproduce published behaviour.
"""
import copy
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))      # repository root
REPO = os.path.join(ROOT, "code")                  # simulator
DATA = os.path.join(ROOT, "data")
PILOT = os.path.join(DATA, "pilot")                # pilot (wave2 / wave2b) inputs
LIB = os.path.join(PILOT, "library")
# Simulation.from_scenario opens "config/params.yaml" relative to cwd, so the
# simulator needs cwd = code/. All other paths in this library are absolute.
os.chdir(REPO)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

from sim.core.integrator import EulerIntegrator  # noqa: E402
from sim.core.simulation import Simulation  # noqa: E402
from sim.experiments.configs import get_config  # noqa: E402
from sim.scenarios.bottleneck import BottleneckScenario  # noqa: E402
from sim.steering.hybrid import HybridSteeringModel  # noqa: E402
from sim.steering.walls import WallForces  # noqa: E402

DOOR = np.array([10.0, 5.0])
SCEN_KEYS = ("spawn", "edge", "edge_radius", "speed_mean")


def split_flags(flags):
    flags = dict(flags or {})
    scen = {k: flags.pop(k) for k in list(flags) if k in SCEN_KEYS}
    return scen, flags


def build(config="C1", seed=42, width=0.8, n_agents=100, noise=0.0, flags=None, light=True):
    scen, params = split_flags(flags)
    if light:
        params.setdefault("w2_metrics", "light")
    sc = BottleneckScenario(n_agents=n_agents, exit_width=width, **scen)
    sim = Simulation.from_scenario(sc, config, seed=seed, param_overrides=params)
    sim.velocity_noise_std = noise
    return sim


def snapshot(sim):
    return {"state": copy.deepcopy(sim.state), "time": sim.time, "step_count": sim.step_count,
            "rng_state": copy.deepcopy(sim._rng.bit_generator.state),
            "params": dict(sim.params), "width": sim._scenario.exit_width,
            "scen": {k: getattr(sim._scenario, k) for k in SCEN_KEYS}}


def restore(snap, config="C1", flags=None, noise=0.0, noise_seed=None, dt=None, light=True):
    """Fresh Simulation from a library snapshot, with steering `config` and wave-2 flags.
    Geometry (width, spawn/edge) is the snapshot's unless overridden in flags."""
    scen_over, p_over = split_flags(flags)
    scen = dict(snap.get("scen", {}))
    scen.update(scen_over)
    sc = BottleneckScenario(n_agents=snap["state"].n, exit_width=snap["width"], **scen)
    world, _ = sc.build(seed=0)
    params = dict(snap["params"])
    for k in [k for k in params if k.startswith("w2_") or k in ("A_w", "B_w")]:
        params.pop(k)
    params.update(p_over)
    if light:
        params.setdefault("w2_metrics", "light")
    if dt is not None:
        params["dt"] = dt
    steering = HybridSteeringModel(get_config(config), params)
    sim = Simulation(world, copy.deepcopy(snap["state"]), steering, EulerIntegrator(), params,
                     seed=0 if noise_seed is None else noise_seed)
    sim._scenario = sc
    sim.periodic_length = None
    sim.time = snap["time"]
    sim.step_count = snap["step_count"]
    if noise_seed is None:
        sim._rng.bit_generator.state = copy.deepcopy(snap["rng_state"])
    sim.velocity_noise_std = noise
    return sim


# ---------------------------------------------------------------- passability
def wall_backward_profile(r, width=0.8, A_w=2000.0, B_w=0.08, edge="sharp", edge_radius=0.1,
                          xs=None):
    """Backward (-x) wall force on a lone agent of radius r on the door axis y = 5, v = 0,
    computed with the code's WallForces and actual wall geometry. Returns (xs, Fx_wall)."""
    from sim.core.agent import AgentState
    if xs is None:
        xs = np.linspace(9.0, 10.6, 1601)
    sc = BottleneckScenario(1, width, edge=edge, edge_radius=edge_radius)
    world, _ = sc.build(seed=0)
    n = len(xs)
    st = AgentState(np.column_stack([xs, np.full(n, 5.0)]), np.zeros((n, 2)),
                    np.tile([11.0, 5.0], (n, 1)), np.full(n, r), np.ones(n), np.full(n, 80.0),
                    np.full(n, 0.5), np.ones(n, bool))
    F = WallForces(A=A_w, B=B_w).compute_wall_forces(st, world.walls)
    return xs, F[:, 0]


def max_backward(r, **kw):
    xs, fx = wall_backward_profile(r, **kw)
    return float(np.max(-fx))


def weidmann_factor(rho, gamma=1.913, rho_max=5.4):
    rho = max(rho, 0.01)
    return float(np.clip(1.0 - np.exp(-gamma * (1.0 / rho - 1.0 / rho_max)), 0.05, 1.0))


def drive(v0, tau, rho=0.0, mass=80.0, kind="C1", tau_orca=0.5):
    """Goal drive at rest on the door axis. C1: m v_eff / tau. C3: + w_o m v0 / tau_orca."""
    d = mass * v0 * weidmann_factor(rho) / tau
    if kind in ("C3", "drive_only"):
        w_o = 1.0 - 1.0 / (1.0 + np.exp(-2.0 * (rho - 4.0)))
        d += w_o * mass * v0 / tau_orca
    return float(d)


class Passability:
    """Cache of max backward wall force vs radius for a given wall model."""

    def __init__(self, width=0.8, **wall_kw):
        self.rs = np.linspace(0.12, 0.45, 331)
        self.g = np.array([max_backward(r, width=width, **wall_kw) for r in self.rs])

    def gmax(self, r):
        return float(np.interp(r, self.rs, self.g))

    def stuck(self, r, v0, tau, rho=0.0, kind="C1"):
        return self.gmax(r) > drive(v0, tau, rho, kind=kind)

    def margin(self, r, v0, tau, rho=0.0, kind="C1"):
        """gmax - drive (N). > 0 means stuck alone."""
        return self.gmax(r) - drive(v0, tau, rho, kind=kind)


# ---------------------------------------------------------------- detection
class StationaryDetector:
    """Deadlock = no exit and every active agent |v| < v_thr for >= hold s (checked
    every `every` steps). Generalises the P1 detector (scan/probes/p0_p1_arch.py),
    which also required >= 3 agents within 1 m of the door; that flag is recorded."""

    def __init__(self, hold=10.0, v_thr=0.01, every=10):
        self.hold, self.v_thr, self.every = hold, v_thr, every
        self.t0 = None
        self.n_prev = None

    def update(self, sim):
        if sim.step_count % self.every:
            return False
        st = sim.state
        n = st.n_active
        if n == 0:
            return False
        if self.n_prev is None or n != self.n_prev:
            self.n_prev = n
            self.t0 = None
        sp = np.linalg.norm(st.velocities[st.active], axis=1)
        if sp.max() < self.v_thr:
            if self.t0 is None:
                self.t0 = sim.time
            return sim.time - self.t0 >= self.hold - 1e-9
        self.t0 = None
        return False


def p1_condition(state):
    act = state.active_indices
    d = np.linalg.norm(state.positions[act] - DOOR, axis=1)
    return int((d < 1.0).sum())


# ---------------------------------------------------------------- job runner
def done_ids(path):
    ids = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                try:
                    ids.add(json.loads(line)["job_id"])
                except Exception:
                    pass
    return ids


def run_jobs(jobs, fn, out_path, workers=4, log_every=1):
    """jobs: list of dicts with 'job_id'. fn(job) -> dict. Results appended as JSONL;
    already-done job_ids are skipped (crash resume)."""
    import multiprocessing as mp
    done = done_ids(out_path)
    todo = [j for j in jobs if j["job_id"] not in done]
    print(f"[run_jobs] {len(todo)} to run, {len(done)} done -> {out_path}", flush=True)
    t0 = time.perf_counter()
    if not todo:
        return 0.0
    ctx = mp.get_context("fork")
    with ctx.Pool(min(workers, len(todo))) as pool, open(out_path, "a") as f:
        for k, r in enumerate(pool.imap_unordered(fn, todo), 1):
            f.write(json.dumps(r, default=float) + "\n")
            f.flush()
            if k % log_every == 0:
                print(f"  {k}/{len(todo)} {r.get('job_id')} wall={time.perf_counter() - t0:.0f}s", flush=True)
    return time.perf_counter() - t0


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)
