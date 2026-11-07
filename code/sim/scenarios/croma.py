"""Wave 2b: CroMa-2021-like bottleneck (Adrian et al., DOI 10.34735/ped.2021.9).

Geometry reconstructed from the 0.8 m trajectory extents (wave2b/data/b1_geom.json;
INFERRED, the archive has no geometry file). Model frame: entrance plane x = 10,
centred on y = 5 (CroMa x = 0, y = 0).
  holding area  x in [10 - D, 10], y in [5 - H/2, 5 + H/2] (D = 7.8 m, H = 8.6 m), walled;
  front wall    x = 10 with a gap of width w centred on y = 5;
  bottleneck    two corridor walls y = 5 -+ w/2, x in [10, 10 + L] (L = 0.2 or 2.0 m);
  start         rejection-sampled non-overlapping positions in the half-annulus
                r in [r0, r1] around (10, 5), x < 10 - 0.3 (default r0 = 1.8, r1 = 7.5 m);
  goal          point (10 + L + 1, 5); agents are removed by the published goal-radius rule;
  leak counter  outside_walkable(): behind the front wall outside the corridor, or outside
                the holding area.
Agent attributes come from AgentState.create (same distributions as the published room).
"""
import numpy as np

from sim.core.agent import AgentState
from sim.core.world import Wall, World
from sim.scenarios.base import Scenario


class CromaBottleneckScenario(Scenario):
    D = 7.8
    H = 8.6

    def __init__(self, n_agents: int = 130, exit_width: float = 0.8, length: float = 0.2,
                 r0: float = 1.8, r1: float = 7.5, speed_mean: float | None = None):
        self.n_agents = n_agents
        self.exit_width = exit_width
        self.length = length
        self.r0, self.r1 = r0, r1
        self.speed_mean = speed_mean
        self.spawn = "rejection"
        self.edge = "sharp"
        self.edge_radius = 0.1

    def build(self, seed: int = 42):
        h = self.exit_width / 2.0
        x0, y0, y1 = 10.0 - self.D, 5.0 - self.H / 2, 5.0 + self.H / 2
        L = self.length
        walls = [
            Wall(np.array([x0, y0]), np.array([10.0, y0])),          # bottom
            Wall(np.array([x0, y1]), np.array([x0, y0])),            # back
            Wall(np.array([10.0, y1]), np.array([x0, y1])),          # top
            Wall(np.array([10.0, y0]), np.array([10.0, 5.0 - h])),   # front, lower jamb
            Wall(np.array([10.0, 5.0 + h]), np.array([10.0, y1])),   # front, upper jamb
            Wall(np.array([10.0, 5.0 - h]), np.array([10.0 + L, 5.0 - h])),  # corridor
            Wall(np.array([10.0, 5.0 + h]), np.array([10.0 + L, 5.0 + h])),
        ]
        walls[3].door_edge = walls[3].end.copy()
        walls[4].door_edge = walls[4].start.copy()
        # The corridor walls start at the door edges: tag them too, so that B_w_edge acts
        # on every wall end at the door edge (Wave 2b fix; without it the corridor-wall
        # ends keep the published range at the edge).
        walls[5].door_edge = walls[5].start.copy()
        walls[6].door_edge = walls[6].start.copy()
        world = World(walls)
        kw = {} if self.speed_mean is None else {"speed_mean": self.speed_mean}
        state = AgentState.create(self.n_agents, spawn_area=(x0 + 0.3, 9.7, y0 + 0.3, y1 - 0.3),
                                  goals=np.array([10.0 + L + 1.0, 5.0]), seed=seed, **kw)
        rng = np.random.Generator(np.random.PCG64(seed))
        pos = np.zeros((state.n, 2))
        r1 = self.r1
        self.r1_used = r1
        for i in range(state.n):
            for k in range(400_000):
                if k and k % 20_000 == 0:   # crowded: widen the start annulus by 0.25 m
                    r1 += 0.25
                    self.r1_used = r1
                r = np.sqrt(rng.uniform(self.r0 ** 2, r1 ** 2))
                a = rng.uniform(0.5 * np.pi, 1.5 * np.pi)
                c = np.array([10.0 + r * np.cos(a), 5.0 + r * np.sin(a)])
                ri = state.radii[i]
                if not (x0 + ri < c[0] < 9.7 and y0 + ri < c[1] < y1 - ri):
                    continue
                if i == 0 or (np.linalg.norm(pos[:i] - c, axis=1) >= state.radii[:i] + ri).all():
                    pos[i] = c
                    break
            else:
                raise RuntimeError(f"CroMa spawn failed at agent {i}")
        state.positions[:] = pos
        return world, state

    def outside_walkable(self, pos):
        x, y = pos[:, 0], pos[:, 1]
        h = self.exit_width / 2.0
        room = (x >= 10.0 - self.D) & (x <= 10.0) & (np.abs(y - 5.0) <= self.H / 2)
        corr = (x >= 10.0) & (x <= 10.0 + self.length) & (np.abs(y - 5.0) <= h)
        beyond = x > 10.0 + self.length
        return ~(room | corr | beyond)

    def line_goals(self, state, x_goal=None):
        return state.goals

    def is_complete(self, agent_state, time):
        return agent_state.n_active == 0
