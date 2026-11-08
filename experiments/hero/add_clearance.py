"""Add the signed wall clearance of the floor probe to data/derived/hero/{lone,pair}.npz (all other arrays unchanged).

    PYTHONPATH=code .venv/bin/python experiments/hero/add_clearance.py      (repository root, after make venv-sim)
"""
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import export_hero as eh  # noqa: E402

for name, snap_path in (("lone", eh.LONE_SNAP), ("pair", eh.PAIR_SNAP)):
    f = eh.OUT / f"{name}.npz"
    D = dict(np.load(f, allow_pickle=True))
    ff, _, _ = eh.floor_field(pickle.load(open(snap_path, "rb")))
    assert np.array_equal(ff["feasible"], D["feasible"]) and np.allclose(ff["wall_back_N"], D["wall_back_N"])
    assert np.array_equal(ff["feasible"], ff["clearance"] >= 0)
    D["clearance"] = ff["clearance"]
    np.savez_compressed(f, **D)
    print(name, "clearance", ff["clearance"].min(), ff["clearance"].max())
