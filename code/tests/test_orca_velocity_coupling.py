"""Flag w2_orca_coupling: "force" (default) and "velocity" (ORCA filters the proposed velocity)."""

import hashlib

import numpy as np
import pytest

from sim.core.agent import AgentState
from sim.core.simulation import Simulation
from sim.experiments.configs import get_config
from sim.scenarios.bottleneck import BottleneckScenario
from sim.steering.hybrid import HybridSteeringModel
from sim.steering.orca import ORCAModel

CF = {"w2_numerics": "fixed", "w2_orca": "rvo2", "w2_crush": "off", "w2_wall_corner": "convex_union"}


def _hash(sim):
    h = hashlib.sha256()
    for a in (sim.state.positions, sim.state.velocities, sim.state.active):
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def _run(config, overrides, steps=200, seed=7):
    sc = BottleneckScenario(n_agents=30, exit_width=0.8, spawn="rejection")
    sim = Simulation.from_scenario(sc, config, seed=seed, param_overrides=dict(overrides))
    for _ in range(steps):
        sim.step()
    return sim


def _state(pos, vel, goals):
    n = len(pos)
    return AgentState(positions=np.array(pos, float), velocities=np.array(vel, float),
                      goals=np.array(goals, float), radii=np.full(n, 0.25),
                      desired_speeds=np.full(n, 1.34), masses=np.full(n, 80.0),
                      taus=np.full(n, 0.5), active=np.ones(n, dtype=bool))


@pytest.mark.parametrize("variant", ["published", "rvo2"])
def test_default_is_force_coupling_bitwise(variant):
    a = _run("C3", {**CF, "w2_orca": variant})
    b = _run("C3", {**CF, "w2_orca": variant, "w2_orca_coupling": "force"})
    assert _hash(a) == _hash(b)


def test_velocity_coupling_changes_c3_but_not_c1():
    assert _hash(_run("C1", CF)) == _hash(_run("C1", {**CF, "w2_orca_coupling": "velocity"}))
    assert _hash(_run("C3", CF)) != _hash(_run("C3", {**CF, "w2_orca_coupling": "velocity"}))


@pytest.mark.parametrize("variant", ["published", "rvo2"])
def test_rest_without_binding_constraint_returns_proposed_velocity_exactly(variant):
    # Three agents at rest, surface gaps 0.3 m: no half-plane binds near v = 0.
    st = _state([[5.0, 5.0], [5.8, 5.0], [5.0, 5.8]], np.zeros((3, 2)), [[10.0, 5.0]] * 3)
    nbrs = [[1, 2], [0, 2], [0, 1]]
    v_prop = np.array([[1e-6, -2e-6], [3e-7, 0.0], [-4e-6, 1e-6]])
    orca = ORCAModel(variant=variant)
    assert np.array_equal(orca.filter_velocities(st, nbrs, v_prop), v_prop)
    hyb = HybridSteeringModel(get_config("C3"), {**CF, "w2_orca": variant, "w2_orca_coupling": "velocity"})
    out = hyb.orca_velocity_filter(st, nbrs, np.full(3, 2.0), v_prop)
    assert np.array_equal(out, v_prop)


@pytest.mark.parametrize("variant", ["published", "rvo2"])
def test_velocity_coupling_has_no_rest_drive(variant):
    # Force coupling: a lone agent at rest feels m v0 e / tau_ORCA; velocity coupling adds no force.
    st = _state([[5.0, 5.0]], [[0.0, 0.0]], [[10.0, 5.0]])
    p = {**CF, "w2_orca": variant}
    f_force = HybridSteeringModel(get_config("C3"), p).compute_forces(st, [[]], [], np.zeros(1))
    f_vel = HybridSteeringModel(get_config("C3"), {**p, "w2_orca_coupling": "velocity"}).compute_forces(
        st, [[]], [], np.zeros(1))
    f_c1 = HybridSteeringModel(get_config("C1"), p).compute_forces(st, [[]], [], np.zeros(1))
    w_o = 1.0 - 1.0 / (1.0 + np.exp(-2.0 * (0.0 - 4.0)))
    np.testing.assert_allclose(f_force - f_c1, [[w_o * 80.0 * 1.34 / 0.5, 0.0]], rtol=1e-12)
    assert np.array_equal(f_vel, f_c1)


def test_head_on_pair_is_deflected_rvo2():
    # Two agents approach head-on, slightly offset in y; RVO2 turns them apart laterally.
    st = _state([[4.0, 5.0], [6.0, 5.05]], [[1.2, 0.0], [-1.2, 0.0]], [[20.0, 5.0], [-10.0, 5.05]])
    v_prop = st.velocities.copy()
    out = ORCAModel(variant="rvo2").filter_velocities(st, [[1], [0]], v_prop)
    assert out[0, 1] < -1e-2 and out[1, 1] > 1e-2          # apart: agent 0 down, agent 1 up
    assert out[0, 0] < v_prop[0, 0] and out[1, 0] > v_prop[1, 0]
    np.testing.assert_allclose(out[0], -out[1], atol=1e-12)  # reciprocal


def test_head_on_pair_is_deflected_legacy():
    st = _state([[4.0, 5.0], [6.0, 5.05]], [[1.2, 0.0], [-1.2, 0.0]], [[20.0, 5.0], [-10.0, 5.05]])
    v_prop = st.velocities.copy()
    out = ORCAModel(variant="published").filter_velocities(st, [[1], [0]], v_prop)
    assert np.all(np.abs(out[:, 1]) > 1e-2)
    np.testing.assert_allclose(out[0], -out[1], atol=1e-12)


def test_velocity_coupling_requires_corrected_numerics_and_plain_split():
    sc = BottleneckScenario(n_agents=5, exit_width=0.8)
    sim = Simulation.from_scenario(sc, "C3", seed=1, param_overrides={"w2_orca_coupling": "velocity"})
    with pytest.raises(ValueError):
        sim.step()
    with pytest.raises(ValueError):
        HybridSteeringModel(get_config("C3"), {**CF, "w2_orca_coupling": "velocity",
                                              "w2_orca_split": "drive_only"})
    with pytest.raises(ValueError):
        HybridSteeringModel(get_config("C3"), {**CF, "w2_orca_coupling": "bogus"})
