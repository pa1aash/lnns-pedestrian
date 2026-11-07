"""Wave 2 flag orca="rvo2": agent-agent ORCA lines and LP in the RVO2 convention.

Algorithm logic ported from the RVO2 Library v2.0.3 (C++), src/Agent.cpp:
``Agent::computeNewVelocity`` (agent part only; no obstacles) and the
``linearProgram1`` / ``linearProgram2`` / ``linearProgram3`` routines
(van den Berg, Guy, Snape, Lin, Manocha; Apache-2.0). Ported as logic only.

Differences from the published repo implementation (sim/steering/orca.py):
- leg-region constraint: line direction along the leg, permitted side to the
  left of the direction (repo uses normal = u/|u|, which is sign-flipped when
  v_rel lies outside the VO, sim/steering/orca.py:113);
- left/right leg chosen by det(relPos, w) with w = v_rel - relPos/tau_h
  (RVO2), not det(relPos, v_rel);
- collision branch: w = v_rel - relPos/dt, cut-off circle of radius R/dt
  (identical to the repo at v_rel = 0);
- when the 2-D LP is infeasible, linearProgram3 minimises the maximum
  constraint violation instead of silently skipping constraints
  (sim/steering/orca.py:178-200);
- neighbours are processed nearest-first (RVO2 keeps them sorted by distance).
The neighbour set itself (all agents within the 3 m KD-tree radius) is the
repo's, not RVO2's maxNeighbors / neighborDist.
Pure-Python floats are used deliberately (small-vector numpy is slower).
"""

import math

RVO_EPSILON = 1e-5


def _det(ax, ay, bx, by):
    return ax * by - ay * bx


def orca_lines(px, py, vx, vy, nbrs, r_i, tau_h, dt):
    """Return ORCA lines [(pt_x, pt_y, dir_x, dir_y)] for one agent.

    nbrs: iterable of (px_j, py_j, vx_j, vy_j, r_j), already sorted nearest-first.
    """
    inv_th = 1.0 / tau_h
    lines = []
    for (qx, qy, ux, uy, r_j) in nbrs:
        rpx, rpy = qx - px, qy - py          # relativePosition
        rvx, rvy = vx - ux, vy - uy          # relativeVelocity
        dist_sq = rpx * rpx + rpy * rpy
        R = r_i + r_j
        R_sq = R * R
        if dist_sq > R_sq:
            wx, wy = rvx - inv_th * rpx, rvy - inv_th * rpy
            w_len_sq = wx * wx + wy * wy
            dot1 = wx * rpx + wy * rpy
            if dot1 < 0.0 and dot1 * dot1 > R_sq * w_len_sq:
                # cut-off circle
                w_len = math.sqrt(w_len_sq)
                uwx, uwy = wx / w_len, wy / w_len
                dx, dy = uwy, -uwx
                s = R * inv_th - w_len
                ux_, uy_ = s * uwx, s * uwy
            else:
                leg = math.sqrt(dist_sq - R_sq)
                if _det(rpx, rpy, wx, wy) > 0.0:
                    dx = (rpx * leg - rpy * R) / dist_sq
                    dy = (rpx * R + rpy * leg) / dist_sq
                else:
                    dx = -(rpx * leg + rpy * R) / dist_sq
                    dy = -(-rpx * R + rpy * leg) / dist_sq
                dot2 = rvx * dx + rvy * dy
                ux_, uy_ = dot2 * dx - rvx, dot2 * dy - rvy
        else:
            inv_ts = 1.0 / dt
            wx, wy = rvx - inv_ts * rpx, rvy - inv_ts * rpy
            w_len = math.sqrt(wx * wx + wy * wy)
            if w_len < 1e-12:
                uwx, uwy = 1.0, 0.0
            else:
                uwx, uwy = wx / w_len, wy / w_len
            dx, dy = uwy, -uwx
            s = R * inv_ts - w_len
            ux_, uy_ = s * uwx, s * uwy
        lines.append((vx + 0.5 * ux_, vy + 0.5 * uy_, dx, dy))
    return lines


def _lp1(lines, no, radius, ox, oy, dir_opt):
    px, py, dx, dy = lines[no]
    dot = px * dx + py * dy
    disc = dot * dot + radius * radius - (px * px + py * py)
    if disc < 0.0:
        return None
    sq = math.sqrt(disc)
    t_left, t_right = -dot - sq, -dot + sq
    for i in range(no):
        qx, qy, ex, ey = lines[i]
        denom = _det(dx, dy, ex, ey)
        numer = _det(ex, ey, px - qx, py - qy)
        if abs(denom) <= RVO_EPSILON:
            if numer < 0.0:
                return None
            continue
        t = numer / denom
        if denom >= 0.0:
            t_right = min(t_right, t)
        else:
            t_left = max(t_left, t)
        if t_left > t_right:
            return None
    if dir_opt:
        t = t_right if (ox * dx + oy * dy) > 0.0 else t_left
    else:
        t = dx * (ox - px) + dy * (oy - py)
        if t < t_left:
            t = t_left
        elif t > t_right:
            t = t_right
    return (px + t * dx, py + t * dy)


def _lp2(lines, radius, ox, oy, dir_opt):
    """Returns (index_of_failure_or_len, result)."""
    if dir_opt:
        res = (ox * radius, oy * radius)
    elif ox * ox + oy * oy > radius * radius:
        n = math.hypot(ox, oy)
        res = (ox / n * radius, oy / n * radius)
    else:
        res = (ox, oy)
    for i, (px, py, dx, dy) in enumerate(lines):
        if _det(dx, dy, px - res[0], py - res[1]) > 0.0:
            new = _lp1(lines, i, radius, ox, oy, dir_opt)
            if new is None:
                return i, res
            res = new
    return len(lines), res


def _lp3(lines, begin, radius, res):
    distance = 0.0
    for i in range(begin, len(lines)):
        px, py, dx, dy = lines[i]
        if _det(dx, dy, px - res[0], py - res[1]) > distance:
            proj = []
            for j in range(i):
                qx, qy, ex, ey = lines[j]
                determinant = _det(dx, dy, ex, ey)
                if abs(determinant) <= RVO_EPSILON:
                    if dx * ex + dy * ey > 0.0:
                        continue
                    lpx, lpy = 0.5 * (px + qx), 0.5 * (py + qy)
                else:
                    t = _det(ex, ey, px - qx, py - qy) / determinant
                    lpx, lpy = px + t * dx, py + t * dy
                ldx, ldy = ex - dx, ey - dy
                n = math.hypot(ldx, ldy)
                if n > 0.0:
                    ldx, ldy = ldx / n, ldy / n
                proj.append((lpx, lpy, ldx, ldy))
            temp = res
            fail, new = _lp2(proj, radius, -dy, dx, True)
            res = temp if fail < len(proj) else new
            distance = _det(dx, dy, px - res[0], py - res[1])
    return res


def solve(lines, pref_x, pref_y, max_speed):
    """RVO2 computeNewVelocity LP stage. Returns (vx, vy, used_lp3)."""
    fail, res = _lp2(lines, max_speed, pref_x, pref_y, False)
    if fail < len(lines):
        return _lp3(lines, fail, max_speed, res) + (True,)
    return res + (False,)
