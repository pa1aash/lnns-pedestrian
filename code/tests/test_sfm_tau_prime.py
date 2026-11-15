"""sfm_tau_prime (revision 4): "off" (default) is bit-identical to leaving the flag out; "on" gives the SFM drive with
tau' = tau tau_o / (tau + tau_o) and target speed tau' (v_eff / tau + v0 / tau_o), which equals the desired force plus
force-coupled ORCA's drive part m (v0 e - v) / tau_o (gate 1) to rounding; other values are rejected."""

import numpy as np
import pytest

from sim.core.simulation import Simulation
from sim.scenarios.bottleneck import BottleneckScenario
from sim.steering.hybrid import HybridSteeringModel
from sim.experiments.configs import get_config


def _positions(overrides, steps=200):
    sim = Simulation.from_scenario(BottleneckScenario(n_agents=50, exit_width=0.8), "C1", seed=42,
                                   param_overrides=overrides)
    for _ in range(steps):
        sim.step()
    return sim.state.positions.copy()


def test_default_is_off_bitwise():
    assert np.array_equal(_positions({}), _positions({"sfm_tau_prime": "off"}))


def test_on_changes_dynamics():
    assert not np.array_equal(_positions({}), _positions({"sfm_tau_prime": "on"}))


def test_bad_value_rejected():
    with pytest.raises(ValueError):
        _positions({"sfm_tau_prime": "maybe"}, steps=1)


def test_identity_with_drive_part():
    sim = Simulation.from_scenario(BottleneckScenario(n_agents=50, exit_width=0.8), "C1", seed=7)
    st = sim.state
    rng = np.random.default_rng(3)
    st.velocities[:] = rng.normal(0, 0.3, st.velocities.shape)
    rho = rng.uniform(0.5, 3.0, st.n)
    nl = [[] for _ in range(st.n)]
    p = dict(sim.params)
    a = HybridSteeringModel(get_config("C1"), {**p, "sfm_tau_prime": "on"}).compute_forces(st, nl, [], rho)
    # desired force plus the explicit drive part at gate 1, same densities
    c = HybridSteeringModel(get_config("C1"), p).compute_forces(st, nl, [], rho)
    e = (st.goals - st.positions) / np.linalg.norm(st.goals - st.positions, axis=1)[:, None]
    drive = st.masses[:, None] * (st.desired_speeds[:, None] * e - st.velocities) / p.get("tau_orca", 0.5)
    assert np.max(np.abs(a - (c + drive))) < 1e-9
