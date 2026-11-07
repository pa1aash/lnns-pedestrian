"""Execution flag w2_wall_corner ("segment_sum" default = published, "convex_union").

convex_union: at an endpoint P shared by wall segments, a segment whose closest point to
the agent is P contributes only if no other segment meeting at P has a nearer closest
point, and P itself is counted once. Concave corners and split collinear walls are
unchanged; the exterior wedge of a convex corner feels the corner once instead of twice.
"""

import numpy as np
import pytest

from sim.core.agent import AgentState
from sim.core.world import Wall
from sim.scenarios.bottleneck import BottleneckScenario
from sim.scenarios.croma import CromaBottleneckScenario
from sim.steering.walls import WallForces

P = lambda x, y: np.array([x, y], float)  # noqa: E731


def agents(pos, r=0.25, vel=None):
    pos = np.atleast_2d(np.asarray(pos, float))
    n = len(pos)
    vel = np.zeros((n, 2)) if vel is None else np.asarray(vel, float)
    return AgentState(pos, vel, np.tile([11.0, 5.0], (n, 1)), np.full(n, r), np.ones(n),
                      np.full(n, 80.0), np.full(n, 0.5), np.ones(n, bool))


def both(st, walls, **kw):
    a = WallForces(**kw).compute_wall_forces(st, walls)
    b = WallForces(corner="convex_union", **kw).compute_wall_forces(st, walls)
    return a, b


def random_agents(n, box, seed, r=0.25):
    rng = np.random.default_rng(seed)
    pos = np.column_stack([rng.uniform(box[0], box[1], n), rng.uniform(box[2], box[3], n)])
    return agents(pos, r=r, vel=rng.normal(0, 0.8, (n, 2)))


def test_flag_value_checked():
    with pytest.raises(ValueError):
        WallForces(corner="union")


def test_no_shared_endpoints_bitwise():
    walls = [Wall(P(0, 0), P(4, 0)), Wall(P(4.5, 0), P(9, 1)), Wall(P(2, 3), P(2, 6))]
    assert WallForces.shared_endpoints(walls) == []
    st = random_agents(500, (-1, 10, -1, 7), seed=1)
    a, b = both(st, walls)
    np.testing.assert_array_equal(a, b)


def test_rounded_room_jambs_not_junctions():
    world, _ = BottleneckScenario(1, 0.8, edge="rounded").build(seed=0)
    pts = [tuple(np.round(Pt, 9)) for Pt, _ in WallForces.shared_endpoints(world.walls)]
    assert sorted(pts) == [(0.0, 0.0), (0.0, 10.0)]   # capsule jambs excluded


def croma_backward_max(r, L, corner):
    world, _ = CromaBottleneckScenario(1, 0.8, length=L).build(seed=0)
    xs = np.linspace(9.0, 10.6, 1601)
    st = agents(np.column_stack([xs, np.full_like(xs, 5.0)]), r=r)
    F = WallForces(corner=corner).compute_wall_forces(st, world.walls)
    return float(np.max(-F[:, 0]))


def room_backward_max(r, corner):
    world, _ = BottleneckScenario(1, 0.8).build(seed=0)
    xs = np.linspace(9.0, 10.6, 1601)
    st = agents(np.column_stack([xs, np.full_like(xs, 5.0)]), r=r)
    return WallForces(corner=corner).compute_wall_forces(st, world.walls)


@pytest.mark.parametrize("L", [2.0, 0.21])
def test_croma_door_edge_counted_once(L):
    for r, seg, uni in ((0.25, 311.0, 156.0), (0.30, 582.0, 291.0)):
        f_seg = croma_backward_max(r, L, "segment_sum")
        f_uni = croma_backward_max(r, L, "convex_union")
        assert abs(f_seg - seg) < 1.0
        assert abs(f_uni - uni) < 1.0
        # the union force equals the published room's single-edge force
        f_room = float(np.max(-room_backward_max(r, "segment_sum")[:, 0]))
        assert abs(f_uni - f_room) < 1e-9 * f_room


def test_room_axis_profile_unchanged():
    for r in (0.20, 0.25, 0.30, 0.35):
        a = room_backward_max(r, "segment_sum")
        b = room_backward_max(r, "convex_union")
        np.testing.assert_allclose(a, b, rtol=0, atol=1e-12)


def test_concave_room_corner_unchanged():
    world, _ = BottleneckScenario(1, 0.8).build(seed=0)
    # agents inside the room, near all four corners, some in contact with both walls
    rng = np.random.default_rng(2)
    pos = np.vstack([rng.uniform(0.05, 1.0, (200, 2)) * s + o
                     for s, o in (((1, 1), (0, 0)), ((-1, 1), (10, 0)),
                                  ((1, -1), (0, 10)), ((-1, -1), (10, 10)))])
    st = agents(pos, vel=rng.normal(0, 0.8, (len(pos), 2)))
    a, b = both(st, world.walls)
    np.testing.assert_array_equal(a, b)


def test_collinear_split_equals_unsplit():
    whole = [Wall(P(0, 0), P(10, 0))]
    split = [Wall(P(0, 0), P(4, 0)), Wall(P(4, 0), P(10, 0))]
    rng = np.random.default_rng(3)
    pos = np.column_stack([rng.uniform(-1, 11, 2000), rng.uniform(-0.6, 0.6, 2000)])
    pos[:50, 0] = 4.0                        # projection exactly on the split point
    st = agents(pos, vel=rng.normal(0, 0.8, (2000, 2)))
    F_whole = WallForces().compute_wall_forces(st, whole)
    F_split = WallForces(corner="convex_union").compute_wall_forces(st, split)
    # Same physics; only the floating-point rounding of the closest point differs between
    # a segment of length 10 and one of length 4 or 6. Agreement: |dF| <= 1e-12 |F| for
    # every agent, and |dF| < 1e-12 N wherever |F| < 100 N.
    dF = np.linalg.norm(F_split - F_whole, axis=1)
    mag = np.linalg.norm(F_whole, axis=1)
    assert (dF <= 1e-12 * mag + 1e-15).all()
    assert dF[mag < 100.0].max() < 1e-12
    # the published sum double counts near the split point
    F_sum = WallForces().compute_wall_forces(st, split)
    assert np.abs(F_sum - F_whole).max() > 1.0


def test_convex_corner_exterior_wedge_halved():
    # L-shaped solid corner at the origin; free space is everything except x>0, y<0
    walls = [Wall(P(0, -3), P(0, 0)), Wall(P(0, 0), P(3, 0))]
    st = agents([[-0.2, 0.2], [-0.1, 0.25]], vel=[[0.3, -0.1], [0.0, 0.5]])
    a, b = both(st, walls)
    np.testing.assert_allclose(b, 0.5 * a, rtol=1e-14, atol=0)


def test_three_segment_junction():
    # T junction: straight wall split at P = (0, 0) plus a stub P -> (0, 1)
    walls = [Wall(P(-2, 0), P(0, 0)), Wall(P(0, 0), P(2, 0)), Wall(P(0, 0), P(0, 1))]
    whole_wall = [Wall(P(-2, 0), P(2, 0))]
    stub = [Wall(P(0, 0), P(0, 1))]
    # below the straight wall: only the straight wall acts (as if unsplit, stub's end dropped)
    st = agents([[-0.3, -0.2], [0.2, -0.25], [0.0, -0.3]])
    F = WallForces(corner="convex_union").compute_wall_forces(st, walls)
    ref = WallForces().compute_wall_forces(st, whole_wall)
    assert (np.linalg.norm(F - ref, axis=1) <= 1e-12 * np.linalg.norm(ref, axis=1) + 1e-15).all()
    # in the concave corner between the left half and the stub: both faces act
    st = agents([[-0.2, 0.3]])
    F = WallForces(corner="convex_union").compute_wall_forces(st, walls)
    ref = (WallForces().compute_wall_forces(st, [walls[0]])
           + WallForces().compute_wall_forces(st, stub))
    np.testing.assert_allclose(F, ref, atol=1e-12)
