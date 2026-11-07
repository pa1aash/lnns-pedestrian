"""Execution flag w2_crush ("on" default = published, "off").

"off" sets the crush gate w_c = sigma(rho; 5.5, 3.0) to zero everywhere, which removes
both the w_c * F_crush term and the (1 - w_c) factor on the desired force. C4 then
reduces to desired + SFM + TTC + w_o * ORCA + walls.
"""

import numpy as np
import pytest

from sim.core.agent import AgentState
from sim.core.world import Wall
from sim.steering.desired import compute_desired_force
from sim.steering.hybrid import HybridSteeringModel

C4 = {"sfm": True, "ttc": True, "orca": True, "crush": True}
C4_NO_CRUSH = {"sfm": True, "ttc": True, "orca": True, "crush": False}


def dense_cluster(n=200, spacing=0.22, radius=0.12, seed=3):
    """n agents on a hexagonal lattice (spacing 0.22 m, radius 0.12 m, so neighbouring
    bodies overlap by 0.02 m), moving slowly; the n lattice sites nearest the centre."""
    rng = np.random.default_rng(seed)
    ij = np.array([(i, j) for i in range(-20, 21) for j in range(-20, 21)], float)
    pts = np.column_stack([ij[:, 0] + 0.5 * ij[:, 1], ij[:, 1] * np.sqrt(3) / 2]) * spacing
    pts = pts[np.argsort(np.linalg.norm(pts, axis=1), kind="stable")[:n]]
    pos = pts + np.array([5.0, 5.0])
    vel = rng.normal(0, 0.1, (n, 2))
    st = AgentState(pos, vel, np.tile([11.0, 5.0], (n, 1)), np.full(n, radius),
                    np.full(n, 1.34), np.full(n, 80.0), np.full(n, 0.5), np.ones(n, bool))
    # neighbours and density exactly as Simulation.step builds them (fixed 3 m disk count)
    d = np.linalg.norm(pos[:, None] - pos[None], axis=2)
    nbrs = [[j for j in np.where(d[i] < 3.0)[0] if j != i] for i in range(n)]
    rho = np.array([len(x) for x in nbrs], float) / (np.pi * 9.0)
    walls = [Wall(np.array([0.0, 0.0]), np.array([10.0, 0.0])),
             Wall(np.array([0.0, 10.0]), np.array([10.0, 10.0]))]
    return st, nbrs, walls, rho


def test_flag_value_checked():
    with pytest.raises(ValueError):
        HybridSteeringModel(C4, {"w2_crush": "maybe"})


def test_default_is_on():
    assert HybridSteeringModel(C4, {}).crush is not None
    assert HybridSteeringModel(C4, {"w2_crush": "on"}).crush is not None
    assert HybridSteeringModel(C4, {"w2_crush": "off"}).crush is None


def test_dense_cluster_gate():
    st, nbrs, walls, rho = dense_cluster()
    assert rho.min() > 5.5            # dense enough that the gate is mostly open
    w_c = HybridSteeringModel._sigmoid(rho, 5.5, 3.0)
    assert w_c.min() > 0.5

    F_on = HybridSteeringModel(C4, {}).compute_forces(st, nbrs, walls, rho)
    F_off = HybridSteeringModel(C4, {"w2_crush": "off"}).compute_forces(st, nbrs, walls, rho)
    F_ref = HybridSteeringModel(C4_NO_CRUSH, {}).compute_forces(st, nbrs, walls, rho)
    # off == C4 with no crush component at all (w_c = 0 identically), bitwise
    np.testing.assert_array_equal(F_off, F_ref)

    # on - off == -w_c F_des + w_c F_crush (w_c > 0 with "on")
    m = HybridSteeringModel(C4, {})
    F_des = compute_desired_force(st.positions, st.velocities, st.goals, st.desired_speeds,
                                  st.masses, st.taus, local_densities=rho,
                                  weidmann_gamma=1.913, weidmann_rho_max=5.4)
    F_cr = m.crush.compute_crush_forces(st, nbrs)
    assert np.abs(F_cr).max() > 1e3   # bodies overlap, so the crush term is large
    assert np.abs(F_on).max() < 1e6 and np.abs(F_off).max() < 1e6   # no force clipping
    np.testing.assert_allclose(F_on - F_off, w_c[:, None] * (F_cr - F_des), rtol=1e-9, atol=1e-6)
