"""Regression guard: C1 seed 42, w=0.8, 100 agents, 500 steps, all flags default.
Must reproduce the hash e381b49dc24acccd (ported from the pilot wave2/scripts/regress.py
and scan/probes/common.py). Mac only: the hash is not portable across platforms."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from common import build, state_hash  # noqa: E402

s = build("C1", seed=42)
for _ in range(500):
    s.step()
h = state_hash(s)
print(h, "OK" if h == "e381b49dc24acccd" else "MISMATCH")
sys.exit(0 if h == "e381b49dc24acccd" else 1)
