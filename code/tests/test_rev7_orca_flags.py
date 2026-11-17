"""orca_pref / orca_replace (revision 7). Defaults ("v0", "off") are bit-identical to leaving the flags out for
force-coupled ORCA (RVO2 and published) and its drive part; "veff" scales ORCA's preferred velocity by the density
throttle factor (exactly 1 at density 0); "on" replaces the goal drive: F = (1 - w_o) F_desire + w_o F_ORCA + rest."""

import numpy as np
import pytest

from sim.core.simulation import Simulation
from sim.scenarios.bottleneck import BottleneckScenario

CF = {"w2_numerics": "fixed", "spawn": "rejection", "w2_orca": "rvo2", "w2_crush": "off",
      "w2_wall_corner": "convex_union"}


def _positions(overrides, steps=150, config="C3"):
    sim = Simulation.from_scenario(BottleneckScenario(n_agents=40, exit_width=0.8, spawn="rejection"), config,
                                   seed=42, param_overrides={**{k: v for k, v in CF.items() if k != "spawn"},
                                                             **overrides})
    for _ in range(steps):
        sim.step()
    return sim.state.positions.copy()


@pytest.mark.parametrize("base", [{}, {"w2_orca": "published"}, {"w2_orca_split": "drive_only"}])
def test_defaults_bitwise(base):
    ref = _positions(base)
    assert np.array_equal(ref, _positions({**base, "orca_pref": "v0", "orca_replace": "off"}))


def test_flags_change_dynamics():
    ref = _positions({})
    assert not np.array_equal(ref, _positions({"orca_replace": "on"}))


def test_bad_values_rejected():
    with pytest.raises(ValueError):
        _positions({"orca_pref": "x"}, steps=1)
    with pytest.raises(ValueError):
        _positions({"orca_replace": "x"}, steps=1)
    with pytest.raises(ValueError):
        _positions({"orca_replace": "on"}, steps=1, config="C1")


def _forces(overrides, rho):
    sim = Simulation.from_scenario(BottleneckScenario(n_agents=30, exit_width=0.8, spawn="rejection"), "C3",
                                   seed=7, param_overrides={**{k: v for k, v in CF.items() if k != "spawn"},
                                                            **overrides})
    st = sim.state
    rng = np.random.default_rng(3)
    st.velocities[:] = rng.normal(0, 0.3, st.velocities.shape)
    nl = [[j for j in range(st.n) if j != i and np.linalg.norm(st.positions[j] - st.positions[i]) < 3.0]
          for i in range(st.n)]
    return sim.steering, sim.steering.compute_forces(st, nl, sim.world.walls, rho), st, nl


def test_replace_identity():
    rho = np.random.default_rng(5).uniform(0.2, 5.0, 30)
    hm, F0, st, nl = _forces({}, rho)
    _, F1, _, _ = _forces({"orca_replace": "on"}, rho)
    from sim.steering.desired import compute_desired_force
    Fd = compute_desired_force(st.positions, st.velocities, st.goals, st.desired_speeds, st.masses, st.taus,
                               local_densities=rho)
    w = 1.0 - hm._sigmoid(rho, 4.0, 2.0)
    assert np.allclose(F1, F0 - w[:, None] * Fd, atol=1e-9)


def test_veff_at_zero_density_is_v0():
    rho = np.zeros(30)
    _, F0, _, _ = _forces({"w2_orca_split": "drive_only"}, rho)
    _, F1, _, _ = _forces({"w2_orca_split": "drive_only", "orca_pref": "veff"}, rho)
    assert np.array_equal(F0, F1)


def test_veff_drive_part_scales():
    rho = np.random.default_rng(9).uniform(0.5, 5.0, 30)
    hm, F0, st, nl = _forces({"w2_orca_split": "drive_only"}, rho)
    _, F1, _, _ = _forces({"w2_orca_split": "drive_only", "orca_pref": "veff"}, rho)
    from sim.core.helpers import safe_normalize
    e = safe_normalize(st.goals - st.positions)
    W = hm._weidmann(rho, st.n)
    w = 1.0 - hm._sigmoid(rho, 4.0, 2.0)
    expect = F0 + (w * st.masses * st.desired_speeds * (W - 1.0) / 0.5)[:, None] * e
    assert np.allclose(F1, expect, atol=1e-9)
