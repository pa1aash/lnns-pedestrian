# Execution-phase code changes (branch exec-v1, from plan-wave2b e75af1f)

Every change is behind a flag whose default reproduces published behaviour.
Regression: `.venv/bin/python wave2/scripts/regress.py` (plan root) must print `e381b49dc24acccd OK`.
Test suite baseline: 115 passed / 5 failed (known cross-platform bit-identity tests).

## 1. `w2_crush` ∈ {`on` (default), `off`}

- **Files:** sim/steering/hybrid.py:66-78 (flag read, value check, crush model built only when `on`).
  The gate w_c enters at hybrid.py:126-133 (w_c = σ(ρ; 5.5, 3.0) if a crush model exists, else 0),
  hybrid.py:153 (`(1 − w_c)·F_des`), hybrid.py:174-177 (`w_c·F_crush`), and in the force-logging
  path `compute_forces_decomposed` at hybrid.py:242-255. All four sites key on `self.crush is not None`,
  so `off` sets w_c ≡ 0 at every site; no other module reads the crush gate (grep of sim/).
- **Physics:** in C4 the crush gate both adds w_c·F^crush and scales the desired drive by (1 − w_c).
  `off` removes both, so C4 = F^des + ΣF^sfm + F^ttc + w_o·F^orca + F^wall. Configs without crush
  (C1-C3) are unaffected by the flag.
- **Tests:** tests/test_exec_crush_flag.py
  - value check (`ValueError` on anything but on/off); default is `on`;
  - dense hexagonal cluster (200 agents, 0.22 m spacing, ρ > 5.5 for every agent so w_c > 0.5):
    `off` equals a C4 model with no crush component bitwise; `on − off` = w_c·(F^crush − F^des) to 1e-9;
  - C4 short run (seed 42, w = 0.8, 100 agents, 300 steps; scratch script using scan/probes/common.py):
    before the change `7520dd0926a006e2`; after, default and `w2_crush=on` `7520dd0926a006e2` (bitwise
    unchanged); `w2_crush=off` `9e8bf28a07dfd7ce` (differs: the small w_c ≤ 0.003 at the disk densities reached (ρ ≤ 3.5) already changes the
    trajectory through the chaotic dynamics).
- **Regression:** `e381b49dc24acccd OK` after the change.

## 2. `w2_wall_corner` ∈ {`segment_sum` (default), `convex_union`}

- **Files:** sim/steering/walls.py:37 (constructor argument), :48-53 (value check), :55-117
  (`shared_endpoints`, `_junctions` cache, `_corner_keep` mask), :148-154 (mask built only when
  `convex_union` and the geometry has a shared endpoint), :170-171 (mask applied to all three wall
  terms through the active-agent weight); sim/steering/hybrid.py:87 (`params["w2_wall_corner"]`).
- **Physics:** the published wall force sums the law over every segment's closest point. Where two
  segments share an endpoint P and the agent's closest point on both is P, the same force is felt
  twice. For a solid convex corner the physical distance field is the distance to the union of its faces.
- **Rule (convex_union):** shared endpoints are detected from the wall list (endpoints merged within
  1e-9 m; capsule walls with radius > 0 and zero-length segments excluded) and cached per geometry.
  For every agent and every junction P with incident segments S_P: a segment whose closest point is
  P ("at P", i.e. its clipped projection parameter is exactly 0 or 1 at that end) is dropped when
  some other segment of S_P has its closest point elsewhere; if every segment of S_P is at P, only
  the lowest-index segment is kept (P counted once). Segments whose closest point is not P are never
  dropped at P. For two segments this is exactly C4: if the closest point on at least one is P, only
  the nearer of the two closest points contributes (an interior closest point on a segment through P
  is strictly nearer than P), otherwise both contribute. All three terms (exponential repulsion, body
  compression, sliding friction) are evaluated at the kept segment's closest point.
- **More than two segments at P:** the rule above is applied to the whole set S_P. It differs from a
  literal "nearest point on the union of all segments at P" when two or more segments through P have
  interior closest points (agent in a concave corner formed by two of them, a third ending at P):
  the literal union would keep only one face of a concave corner, which contradicts the two-segment
  rule; the implemented rule keeps both faces and drops only the duplicated terms evaluated at P.
  Tested on a T junction (tests below). No scenario used in the paper has a junction of more than
  two segments.
- **Tests:** tests/test_exec_wall_corner.py (10 tests, all pass):
  (i) geometry without shared endpoints: bitwise identical to segment_sum (500 random agents with
  velocities); capsule jambs are not junctions;
  (ii) CroMa door edge, lone agent on the door axis (x ∈ [9, 10.6], y = 5), max backward force:
  L = 2.0 and L = 0.21 m identical: r = 0.25 m 311.30 → 155.65 N; r = 0.30 m 581.58 → 290.79 N
  (r = 0.20: 166.62 → 83.31; r = 0.35: 1086.53 → 543.26); convex_union equals the published room's
  single-edge value to 1e-9 relative;
  (iii) 800 agents inside the four concave room corners (with velocities, many in contact): bitwise
  identical;
  (iv) wall (0,0)-(10,0) split at x = 4: equals the unsplit wall to |ΔF| ≤ 1e-12·|F| for every agent
  and |ΔF| < 1e-12 N wherever |F| < 100 N (2000 agents, 50 projecting exactly onto the split point;
  max |ΔF| = 2.7e-8 N at |F| ≈ 1.3e5 N in deep contact, floating-point rounding of the closest point
  on segments of different length); the published sum double counts there (> 1 N);
  (v) exterior wedge of an L corner: exactly half the segment_sum force; T junction as above.
- **Shared-endpoint inventory** (exec/scripts/corner_inventory.py → exec/data/corner_inventory.json):
  room bottleneck w = 0.8: 4 junctions, the room corners (0,0), (0,10), (10,0), (10,10); each is
  concave from the room interior and convex from the exterior; the door edges (10, 4.6), (10, 5.4)
  are free ends. CroMa (L = 2.0 and 0.21 m): 4 concave holding-area corners and 2 convex door edges
  (10, 4.6), (10, 5.4) (front wall + corridor wall). Open bidirectional corridor: 4 concave corners.
  Open crossing: 4 concave arm-end corners and 4 convex corners of the crossing zone (3.2/6.8, 3.2/6.8).
- **Room bottleneck:** for an agent inside the room every closest point on a corner-sharing segment
  is interior (bottom/top: 0 < x < 10; jamb segments: closest point interior or at the door edge,
  which is a free end), so nothing is dropped. Only an agent past the door plane (x ≥ 10) has the
  bottom/top wall's closest point at the outer corner (10,0)/(10,10); that term is dropped, at
  distance ≥ 4.6 − 0.45 m: ≤ 2000·exp(−4.15/0.08) ≈ 6e-20 N, below one ulp of any drive force.
  The on-axis g_max(r) profile is identical (to 1e-12 N, test). So the flag cannot change
  room-bottleneck dynamics beyond floating-point noise; checked empirically per seed in E1 (Step 6).
- **Regression:** `e381b49dc24acccd OK` after the change.
