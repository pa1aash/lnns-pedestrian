"""Wave 2b helpers (ported from the pilot wave2b/scripts/w2blib.py): reuse w2lib.

Pilot inputs live in data/pilot. The CF dict is the full corrected-forward mode
(Plan v1.1): the pilot's numerics + spawn, extended with RVO2 ORCA, crush off and
the convex corner rule.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2lib import *  # noqa: F401,F403,E402
import w2lib  # noqa: F401,E402
from w2lib import DATA, PILOT  # noqa: E402

DATA2B = PILOT
LIB2B = os.path.join(PILOT, "library")
CF = {"w2_numerics": "fixed", "spawn": "rejection", "w2_orca": "rvo2",
      "w2_crush": "off", "w2_wall_corner": "convex_union"}
# The pilot's partial CF (numerics + spawn only), kept for provenance checks.
CF_PILOT = {"w2_numerics": "fixed", "spawn": "rejection"}
