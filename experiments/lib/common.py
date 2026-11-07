"""Hash helpers ported from the pilot scan/probes/common.py (build, state_hash)."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2lib  # noqa: F401,E402  (chdir into code/, sys.path)

from sim.scenarios.bottleneck import BottleneckScenario  # noqa: E402
from sim.core.simulation import Simulation  # noqa: E402

import numpy as np  # noqa: E402


def build(config="C1", seed=46, width=0.8, n_agents=100, noise=0.0, param_overrides=None):
    """Exactly the construction used by new_experiments/c1_epsilon_control.py:38-40."""
    sc = BottleneckScenario(n_agents=n_agents, exit_width=width)
    sim = Simulation.from_scenario(sc, config, seed=seed, param_overrides=param_overrides)
    sim.velocity_noise_std = noise
    return sim


def state_hash(sim):
    s = sim.state
    h = hashlib.sha256()
    for a in (s.positions, s.velocities, s.active):
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]
