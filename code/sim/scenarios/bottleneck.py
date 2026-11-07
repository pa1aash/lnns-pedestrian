"""Bottleneck scenario: 10x10m room with variable-width exit on right wall."""

import numpy as np

from sim.core.agent import AgentState
from sim.core.world import Wall, World
from sim.scenarios.base import Scenario


class BottleneckScenario(Scenario):
    """10x10m room with a gap on the right wall.

    Args:
        n_agents: Number of agents.
        exit_width: Width of exit gap (m), centered at y=5.
    """

    def __init__(self, n_agents: int = 100, exit_width: float = 1.2,
                 spawn: str = "uniform", edge: str = "sharp", edge_radius: float = 0.1,
                 speed_mean: float | None = None):
        self.n_agents = n_agents
        self.exit_width = exit_width
        # Wave 2 flags (defaults reproduce the published scenario exactly)
        self.spawn = spawn            # "uniform" | "rejection"
        self.edge = edge              # "sharp" | "rounded"
        self.edge_radius = edge_radius  # jamb half-thickness for edge="rounded" (m)
        self.speed_mean = speed_mean  # Wave 2 (W2.9): mean desired speed; None = published 1.34

    def build(self, seed: int = 42) -> tuple[World, AgentState]:
        """Build bottleneck world and agents.

        Walls: 10x10 room. Right wall has gap centered at y=5.
        Spawn: x in [1, 8], y in [1, 9].
        Goal: (11, 5).
        """
        half = self.exit_width / 2.0
        walls = [
            Wall(np.array([0.0, 0.0]), np.array([10.0, 0.0])),     # bottom
            Wall(np.array([0.0, 10.0]), np.array([0.0, 0.0])),     # left
            Wall(np.array([10.0, 10.0]), np.array([0.0, 10.0])),   # top
            # right wall with gap
            Wall(np.array([10.0, 0.0]), np.array([10.0, 5.0 - half])),
            Wall(np.array([10.0, 5.0 + half]), np.array([10.0, 10.0])),
        ]
        if self.edge == "rounded":
            # Wave 2: finite-thickness jambs (2*rc deep) with semicircular door edges.
            # Each jamb is a capsule whose room-side face is x = 10 and whose edge
            # reaches y = 5 -+ half, so the clear width stays exit_width.
            rc = self.edge_radius
            walls[3] = Wall(np.array([10.0 + rc, 0.0]), np.array([10.0 + rc, 5.0 - half - rc]), radius=rc)
            walls[4] = Wall(np.array([10.0 + rc, 5.0 + half + rc]), np.array([10.0 + rc, 10.0]), radius=rc)
        # Wave 2b: tag the jamb segments with their door-edge endpoint (metadata only).
        walls[3].door_edge = walls[3].end.copy()
        walls[4].door_edge = walls[4].start.copy()
        world = World(walls)

        state = AgentState.create(
            self.n_agents,
            spawn_area=(1.0, 8.0, 1.0, 9.0),
            goals=np.array([11.0, 5.0]),
            seed=seed,
            **({} if self.speed_mean is None else {"speed_mean": self.speed_mean}),
        )
        if self.spawn == "rejection":
            from sim.core.spawn import respawn_rejection
            respawn_rejection(state, (1.0, 8.0, 1.0, 9.0), seed)
        return world, state

    def line_goals(self, state, x_goal: float = 11.0):
        """Wave 2 goal="line": nearest point on the segment x = x_goal,
        y in [5 - w/2 + r_i, 5 + w/2 - r_i] (the door band shrunk by each radius)."""
        half = self.exit_width / 2.0
        lo = 5.0 - half + state.radii
        hi = 5.0 + half - state.radii
        bad = lo > hi
        lo = np.where(bad, 5.0, lo)
        hi = np.where(bad, 5.0, hi)
        g = np.empty_like(state.goals)
        g[:, 0] = x_goal
        g[:, 1] = np.clip(state.positions[:, 1], lo, hi)
        return g

    def is_complete(self, agent_state: AgentState, time: float) -> bool:
        """Complete when all agents have exited."""
        return agent_state.n_active == 0
