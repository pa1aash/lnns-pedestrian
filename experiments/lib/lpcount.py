"""Observer counters for the ORCA linear programs (E8, E9). Importing this module wraps
sim.steering.orca.solve_2d_lp (published LP) and sim.steering.orca_rvo2.solve (RVO2 LP); the wrapped
functions return exactly what the originals return.
  published  calls, and 'violated': the returned velocity violates at least one ORCA half-plane by more
             than 1e-9 m/s, i.e. the LP was infeasible and constraints were dropped silently
             (sim/steering/orca.py:178-200);
  rvo2       calls, and 'lp3': the 2-D LP was infeasible and linearProgram3 was used.
Infeasibility rate = violated / calls (published) or lp3 / calls (RVO2), per agent-step with ORCA.
"""
import numpy as np
import sim.steering.orca as _orca
import sim.steering.orca_rvo2 as _rvo2

C = {"pub_calls": 0, "pub_violated": 0, "rvo2_calls": 0, "rvo2_lp3": 0}
_pub, _rv = _orca.solve_2d_lp, _rvo2.solve


def _pub_counted(halfplanes, v_pref, max_speed):
    r = _pub(halfplanes, v_pref, max_speed)
    C["pub_calls"] += 1
    for p, n in halfplanes:
        if np.dot(r - p, n) < -1e-9:
            C["pub_violated"] += 1
            break
    return r


def _rv_counted(*a, **k):
    out = _rv(*a, **k)
    C["rvo2_calls"] += 1
    C["rvo2_lp3"] += int(bool(out[2]))
    return out


_orca.solve_2d_lp = _pub_counted
_rvo2.solve = _rv_counted


def reset():
    for k in C:
        C[k] = 0


def snapshot():
    d = dict(C)
    d["pub_infeasible_rate"] = d["pub_violated"] / d["pub_calls"] if d["pub_calls"] else None
    d["rvo2_infeasible_rate"] = d["rvo2_lp3"] / d["rvo2_calls"] if d["rvo2_calls"] else None
    return d
