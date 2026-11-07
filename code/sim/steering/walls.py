"""Wall forces: social repulsion, body compression, and friction against walls.

Same SFM structure as agent-agent but using agent-to-segment distance.
Wall is stationary so friction uses agent velocity directly.
"""

import numpy as np

from sim.core.agent import AgentState
from sim.core.helpers import check_forces
from sim.core.world import Wall, agents_to_walls


class WallForces:
    """Wall interaction forces using the SFM formulation.

    Forces per wall:
        f_iw = A*exp((r_i - d_iw)/B) * n_iw              [social]
             + k * g(r_i - d_iw) * n_iw                   [body]
             + kappa * g(r_i - d_iw) * dot(v_i, t_iw) * t_iw  [friction]

    Args:
        A: Social repulsion strength (N).
        B: Social repulsion range (m).
        k: Body compression coefficient (kg/s^2).
        kappa: Sliding friction coefficient (kg/(m*s)).
    """

    def __init__(
        self,
        A: float = 2000.0,
        B: float = 0.08,
        k: float = 120000.0,
        kappa: float = 240000.0,
        B_edge: float | None = None,
        edge_zone: tuple[float, float] = (0.5, 1.0),
        corner: str = "segment_sum",
    ):
        self.A = A
        self.B = B
        self.k = k
        self.kappa = kappa
        # Wave 2b flag B_w_edge (default None = published): on jamb segments
        # (Wall.door_edge set) the social range is B_edge where the closest wall point
        # lies within edge_zone[0] of the door edge, blending linearly to B at edge_zone[1].
        self.B_edge = B_edge
        self.edge_zone = edge_zone
        # Execution flag w2_wall_corner: "segment_sum" (published: the law is summed over
        # every segment's closest point) | "convex_union" (see _corner_keep).
        if corner not in ("segment_sum", "convex_union"):
            raise ValueError(f"w2_wall_corner must be 'segment_sum' or 'convex_union', got {corner!r}")
        self.corner = corner
        self._junction_cache: tuple | None = None

    # ------------------------------------------------------------ corner rule
    SHARED_TOL = 1e-9

    @classmethod
    def shared_endpoints(cls, walls: list[Wall]) -> list[tuple[np.ndarray, list[tuple[int, int]]]]:
        """Junctions: points where >= 2 zero-thickness, non-degenerate segments end.

        Returns a list of (P, [(wall index, end flag), ...]) with end flag 0 if P is the
        segment's start and 1 if it is its end. Endpoints closer than SHARED_TOL are merged.
        Capsule walls (radius > 0) and zero-length segments are excluded.
        """
        ends = []
        for w_idx, wall in enumerate(walls):
            ab = wall.end - wall.start
            if wall.radius != 0.0 or np.dot(ab, ab) < 1e-12:
                continue
            ends.append((w_idx, 0, np.asarray(wall.start, float)))
            ends.append((w_idx, 1, np.asarray(wall.end, float)))
        groups: list[tuple[np.ndarray, list[tuple[int, int]]]] = []
        for w_idx, flag, pt in ends:
            for P, members in groups:
                if np.linalg.norm(pt - P) <= cls.SHARED_TOL:
                    members.append((w_idx, flag))
                    break
            else:
                groups.append((pt, [(w_idx, flag)]))
        return [(P, m) for P, m in groups if len({w for w, _ in m}) >= 2]

    def _junctions(self, walls: list[Wall]):
        key = tuple((wall.start.tobytes(), wall.end.tobytes(), wall.radius) for wall in walls)
        if self._junction_cache is None or self._junction_cache[0] != key:
            self._junction_cache = (key, self.shared_endpoints(walls))
        return self._junction_cache[1]

    def _corner_keep(self, positions: np.ndarray, walls: list[Wall], junctions) -> np.ndarray:
        """(N, W) mask of segment contributions kept under the convex_union rule.

        At a junction P shared by segments S_P, a segment whose closest point to the agent
        is P itself ("at P") is dropped when another segment of S_P has its closest point
        elsewhere: that point is strictly nearer than P, so the nearest point on the union
        is not P. If every segment of S_P is at P (agent in the exterior wedge of a convex
        corner), the force from P is counted once (lowest wall index kept). Segments whose
        closest point is not P are never dropped at P. For two segments this is: if the
        closest point on at least one is P, only the nearer of the two closest points
        contributes; otherwise both contribute (concave corners unchanged; a collinear
        split wall gives the unsplit force).
        """
        n = len(positions)
        keep = np.ones((n, len(walls)), dtype=bool)
        for _P, members in junctions:
            at_p = np.empty((n, len(members)), dtype=bool)
            for c, (w_idx, flag) in enumerate(members):
                wall = walls[w_idx]
                ab = wall.end - wall.start
                t = np.clip(np.dot(positions - wall.start, ab) / np.dot(ab, ab), 0.0, 1.0)
                at_p[:, c] = (t == 0.0) if flag == 0 else (t == 1.0)
            any_off = ~at_p.all(axis=1)          # some segment's closest point is not P
            first = True
            for c, (w_idx, _flag) in enumerate(members):
                drop = at_p[:, c] & (any_off | (not first))
                keep[:, w_idx] &= ~drop
                first = False
        return keep

    def compute_wall_forces(
        self,
        agent_state: AgentState,
        walls: list[Wall],
    ) -> np.ndarray:
        """Compute wall interaction forces for all agents.

        Vectorized over agents, loops over walls.

        Args:
            agent_state: Current state of all agents.
            walls: List of wall segments.

        Returns:
            Forces array of shape (N, 2).
        """
        n = agent_state.n
        if not walls:
            return check_forces(np.zeros((n, 2)), "walls")

        # Get distances and normals for all agents to all walls
        distances, normals = agents_to_walls(agent_state.positions, walls)
        # distances: (N, W), normals: (N, W, 2)

        forces = np.zeros((n, 2))
        radii = agent_state.radii
        vel = agent_state.velocities
        active = agent_state.active

        # Corner rule: per-agent mask of kept segment contributions (None = keep all,
        # the published segment sum; also when the geometry has no shared endpoints).
        keep = None
        if self.corner == "convex_union":
            junctions = self._junctions(walls)
            if junctions:
                keep = self._corner_keep(agent_state.positions, walls, junctions)

        for w_idx in range(len(walls)):
            d_iw = distances[:, w_idx]              # (N,)
            n_iw = normals[:, w_idx]                # (N, 2)

            # Tangent: 90-degree rotation of normal
            t_iw = np.empty_like(n_iw)
            t_iw[:, 0] = -n_iw[:, 1]
            t_iw[:, 1] = n_iw[:, 0]

            # Overlap
            overlap = np.maximum(0.0, radii - d_iw)  # (N,)

            # Only compute for active agents
            amask = active.astype(float)  # (N,)
            if keep is not None:
                amask = amask * keep[:, w_idx]   # convex_union: drop duplicated corner terms

            # Social repulsion (always active)
            B_eff = self.B
            wall = walls[w_idx]
            if self.B_edge is not None and wall.door_edge is not None:
                ab = wall.end - wall.start
                t = np.clip(np.dot(agent_state.positions - wall.start, ab) / np.dot(ab, ab), 0.0, 1.0)
                s_edge = np.linalg.norm(wall.start + t[:, None] * ab - wall.door_edge, axis=1)
                z0, z1 = self.edge_zone
                B_eff = self.B_edge + (self.B - self.B_edge) * np.clip((s_edge - z0) / (z1 - z0), 0.0, 1.0)
            exp_term = np.exp((radii - d_iw) / B_eff)  # (N,)
            f_social = (self.A * exp_term * amask)[:, None] * n_iw  # (N, 2)

            # Body compression (contact only)
            f_body = (self.k * overlap * amask)[:, None] * n_iw  # (N, 2)

            # Sliding friction: wall stationary, use -v_i (Helbing 2000 Eq.3)
            vt = np.sum(vel * t_iw, axis=1)  # dot(v_i, t_iw), (N,)
            f_friction = -(self.kappa * overlap * vt * amask)[:, None] * t_iw  # (N, 2)

            forces += f_social + f_body + f_friction

        return check_forces(forces, "walls")
