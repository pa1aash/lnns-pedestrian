"""Wave 2 spawn option: rejection-sampled, non-overlapping placement.

Logic mirrors scripts/regen_zonal.py:57-82 (sample_no_overlap); the RNG is a fresh
PCG64(seed) as in scripts/regen_zonal.py:101-104. Agent attributes (radii, speeds,
taus) are untouched, so the same seed gives the same agents as the uniform spawn.
"""

import numpy as np


def sample_no_overlap(n, radii, spawn_area, rng, max_tries=20_000):
    """Place n disks of the given radii uniformly in spawn_area without overlap."""
    x0, x1, y0, y1 = spawn_area
    positions = np.zeros((n, 2))
    lo = np.array([x0, y0])
    hi = np.array([x1, y1])
    for i in range(n):
        placed = False
        for _ in range(max_tries):
            cand = rng.uniform(lo, hi)
            if i == 0:
                positions[i] = cand
                placed = True
                break
            diffs = positions[:i] - cand
            d = np.sqrt((diffs ** 2).sum(axis=1))
            if (d >= radii[:i] + radii[i]).all():
                positions[i] = cand
                placed = True
                break
        if not placed:
            raise RuntimeError(f"Rejection sampling failed at agent {i}/{n}")
    return positions


def respawn_rejection(state, spawn_area, seed, index=None):
    """Replace positions of `state` (or of the rows in `index`) by rejection samples."""
    rng = np.random.Generator(np.random.PCG64(seed))
    idx = np.arange(state.n) if index is None else np.asarray(index)
    state.positions[idx] = sample_no_overlap(len(idx), state.radii[idx], spawn_area, rng)
    return state
