"""veff_throttle (revision 3): "on" (default) is bit-identical to leaving the flag out; "off" sets
v_eff = v0 in the desired force and changes the trajectory; other values are rejected."""

import numpy as np
import pytest

from sim.core.simulation import Simulation
from sim.scenarios.bottleneck import BottleneckScenario


def _positions(overrides, steps=200):
    sim = Simulation.from_scenario(BottleneckScenario(n_agents=50, exit_width=0.8), "C1", seed=42,
                                   param_overrides=overrides)
    for _ in range(steps):
        sim.step()
    return sim.state.positions.copy()


def test_default_is_on_bitwise():
    assert np.array_equal(_positions({}), _positions({"veff_throttle": "on"}))


def test_off_changes_dynamics():
    assert not np.array_equal(_positions({}), _positions({"veff_throttle": "off"}))


def test_bad_value_rejected():
    with pytest.raises(ValueError):
        _positions({"veff_throttle": "maybe"}, steps=1)
