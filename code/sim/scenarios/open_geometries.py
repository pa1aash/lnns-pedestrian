"""Wave 2 open geometries: open-ended bidirectional corridor and open-exit crossing.

Unlike sim/scenarios/bidirectional.py and sim/scenarios/crossing.py (closed boxes
whose goals lie behind walls), every goal here lies down an open corridor, agents
are removed at a sink line beyond the measurement section, and the scenario
exposes `outside_walkable` so the Simulation can count wall leaks (an agent
centre that ever leaves the walkable polygon).
"""

import numpy as np

from sim.core.agent import AgentState
from sim.core.world import Wall, World
from sim.scenarios.base import Scenario


def _merge(a: AgentState, b: AgentState) -> AgentState:
    return AgentState(
        positions=np.vstack([a.positions, b.positions]),
        velocities=np.vstack([a.velocities, b.velocities]),
        goals=np.vstack([a.goals, b.goals]),
        radii=np.concatenate([a.radii, b.radii]),
        desired_speeds=np.concatenate([a.desired_speeds, b.desired_speeds]),
        masses=np.concatenate([a.masses, b.masses]),
        taus=np.concatenate([a.taus, b.taus]),
        active=np.concatenate([a.active, b.active]),
    )


class OpenBidirectionalScenario(Scenario):
    """20 x 3.6 m measurement section (x in [0, 20]) of a corridor walled on
    y = 0 and y = 3.6 from x = -12 to x = 32. Group R spawns in x in [-10, 2] and
    walks +x; group L spawns in x in [18, 30] and walks -x. Group R is removed
    at x > 21, group L at x < -1. Goals (40, y_i) / (-20, y_i), with y_i the
    spawn y as in sim/scenarios/bidirectional.py:44,53."""

    X_MIN, X_MAX, H = -12.0, 32.0, 3.6

    def __init__(self, n_per_direction: int = 50, spawn: str = "rejection"):
        self.n_per_direction = n_per_direction
        self.spawn = spawn

    def build(self, seed: int = 42):
        walls = [Wall(np.array([self.X_MIN, 0.0]), np.array([self.X_MAX, 0.0])),
                 Wall(np.array([self.X_MAX, self.H]), np.array([self.X_MIN, self.H])),
                 Wall(np.array([self.X_MIN, self.H]), np.array([self.X_MIN, 0.0])),
                 Wall(np.array([self.X_MAX, 0.0]), np.array([self.X_MAX, self.H]))]
        n = self.n_per_direction
        area_r, area_l = (-10.0, 2.0, 0.3, 3.3), (18.0, 30.0, 0.3, 3.3)
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

    def outside_walkable(self, pos):
        return ((pos[:, 1] < 0.0) | (pos[:, 1] > self.H)
                | (pos[:, 0] < self.X_MIN) | (pos[:, 0] > self.X_MAX))

    def sink_indices(self, state):
        x = state.positions[:, 0]
        return ((self.direction > 0) & (x > 21.0)) | ((self.direction < 0) & (x < -1.0))

    def is_complete(self, agent_state, time):
        return agent_state.n_active == 0


class OpenCrossingScenario(Scenario):
    """Plus-shaped 90-degree crossing of two 3.6 m corridors centred on x = 5 and
    y = 5 (crossing zone [3.2, 6.8]^2). Stream N spawns in x in [3.5, 6.5],
    y in [-18, -1] and walks +y; stream E spawns in x in [-18, -1], y in [3.5, 6.5]
    and walks +x. The south and west arms are capped at -20; the north and east
    arms run open to 24. Sinks: stream N at y > 12, stream E at x > 12.
    Line goals (w2_goal="line"): nearest point on y = 30 (resp. x = 30) within
    the corridor band shrunk by the agent radius."""

    LO, HI, FAR, NEAR = 3.2, 6.8, 24.0, -20.0

    def __init__(self, n_per_stream: int = 100, spawn: str = "rejection"):
        self.n_per_stream = n_per_stream
        self.spawn = spawn

    def build(self, seed: int = 42):
        lo, hi, far, near = self.LO, self.HI, self.FAR, self.NEAR
        P = lambda x, y: np.array([x, y], float)  # noqa: E731
        walls = [
            Wall(P(lo, near), P(lo, lo)), Wall(P(lo, lo), P(near, lo)),      # SW
            Wall(P(hi, near), P(hi, lo)), Wall(P(hi, lo), P(far, lo)),       # SE
            Wall(P(lo, far), P(lo, hi)), Wall(P(lo, hi), P(near, hi)),       # NW
            Wall(P(hi, far), P(hi, hi)), Wall(P(hi, hi), P(far, hi)),        # NE
            Wall(P(lo, near), P(hi, near)), Wall(P(near, lo), P(near, hi)),  # caps
        ]
        n = self.n_per_stream
        area_n, area_e = (3.5, 6.5, -18.0, -1.0), (-18.0, -1.0, 3.5, 6.5)
        a = AgentState.create(n, spawn_area=area_n, goals=np.array([5.0, 30.0]), seed=seed)
        b = AgentState.create(n, spawn_area=area_e, goals=np.array([30.0, 5.0]), seed=seed + 2000)
        if self.spawn == "rejection":
            from sim.core.spawn import respawn_rejection
            respawn_rejection(a, area_n, seed)
            respawn_rejection(b, area_e, seed + 2000)
        self.stream = np.concatenate([np.zeros(n, int), np.ones(n, int)])  # 0 = N, 1 = E
        return World(walls), _merge(a, b)

    def line_goals(self, state):
        g = np.empty_like(state.goals)
        r = state.radii
        north = self.stream == 0
        g[north, 0] = np.clip(state.positions[north, 0], self.LO + r[north], self.HI - r[north])
        g[north, 1] = 30.0
        east = ~north
        g[east, 0] = 30.0
        g[east, 1] = np.clip(state.positions[east, 1], self.LO + r[east], self.HI - r[east])
        return g

    def outside_walkable(self, pos):
        x, y = pos[:, 0], pos[:, 1]
        in_v = (x >= self.LO) & (x <= self.HI) & (y >= self.NEAR) & (y <= self.FAR)
        in_h = (y >= self.LO) & (y <= self.HI) & (x >= self.NEAR) & (x <= self.FAR)
        return ~(in_v | in_h)

    def sink_indices(self, state):
        x, y = state.positions[:, 0], state.positions[:, 1]
        return ((self.stream == 0) & (y > 12.0)) | ((self.stream == 1) & (x > 12.0))

    def in_crossing_zone(self, pos):
        return ((pos[:, 0] >= self.LO) & (pos[:, 0] <= self.HI)
                & (pos[:, 1] >= self.LO) & (pos[:, 1] <= self.HI))

    def is_complete(self, agent_state, time):
        return agent_state.n_active == 0
