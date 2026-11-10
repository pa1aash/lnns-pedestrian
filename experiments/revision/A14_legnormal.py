"""A14: identification and static check of the leg-normal sign defect of the legacy ORCA solver.

Inputs: code only (no simulation, no data files).
  legacy half-plane builder  code/sim/steering/orca.py:_halfplane_normal (identical, lines 1-255, to the
                             conference code, repository pedestrian-abs, blob 71bb509 at commit 9762177)
  RVO2 port                  code/sim/steering/orca_rvo2.py:orca_lines (RVO2 v2.0.3 Agent::computeNewVelocity)

What it computes, on random non-colliding agent pairs (relative position x = p_j - p_i with |x| in
(R, 3 m], relative velocity v = v_i - v_j with |v| <= 2.7 m/s, R = r_i + r_j, tau_h = 5 s):
  1. branch: cap (cut-off circle) or leg, by the shared test w.x < 0 and (w.x)^2 > R^2 |w|^2,
     w = v - x/tau_h;
  2. for legs: the RVO2 outward normal n = (-d_y, d_x) of the RVO2 line direction d (permitted side to
     the left of d) and the legacy normal n_leg = u/|u|, u = (v.d) d - v; sign s = sign(n_leg . n);
  3. whether v lies inside the truncated velocity obstacle, by direct geometry: some t in (0, tau_h]
     with |x - v t| < R (independent of both codes);
  4. agreement of the left/right choice: legacy det(x, v) > 0 against RVO2 det(x, w) > 0;
  5. for caps: the angle between the two normals and the distance between the two points;
  6. that the corrected legacy normal (+-90 deg rotation of the leg direction) equals the RVO2 normal;
  7. whether the current velocity v_i satisfies each half-plane (legacy: (v_i - p).n_leg >= 0; RVO2:
     (v_i - p).n >= 0).
A second sample draws v near zero (|v| <= 0.02 m/s, the creep regime of the second trap).
Output: data/derived/rev_A14.json (counts, fractions, identifiers of the defective code).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402

from sim.steering import orca, orca_rvo2  # noqa: E402

TAU_H = 5.0
RNG = np.random.default_rng(14)


def inside_vo(x, v, R, tau):
    vv = float(np.dot(v, v))
    t = 0.0 if vv == 0 else float(np.clip(np.dot(x, v) / vv, 0.0, tau))
    t = max(t, 1e-12)
    return float(np.linalg.norm(x - v * t)) < R


def leg_direction(x, R, left):
    """Leg direction exactly as in orca.py:_halfplane_normal lines 95-106."""
    d2 = float(np.dot(x, x))
    leg = np.sqrt(d2 - R * R)
    if left:
        return np.array([x[0] * leg - x[1] * R, x[0] * R + x[1] * leg]) / d2
    return np.array([x[0] * leg + x[1] * R, -x[0] * R + x[1] * leg]) / d2


def sample(n, vmax):
    rec = {"n": 0, "cap": 0, "leg": 0, "leg_inside": 0, "leg_outside": 0,
           "leg_inside_agree": 0, "leg_outside_flipped": 0, "leg_side_agree": 0,
           "leg_legacy_vi_violates": 0, "leg_rvo2_vi_violates_outside": 0, "leg_rvo2_vi_violates_inside": 0,
           "leg_skipped_legacy": 0, "leg_fix_agree": 0, "cap_max_angle_rad": 0.0, "cap_max_point_diff": 0.0, "point_max_diff": 0.0}
    for _ in range(n):
        ri, rj = RNG.uniform(0.15, 0.35, 2)
        R = ri + rj
        d = RNG.uniform(R * 1.0001, 3.0)
        a = RNG.uniform(0, 2 * np.pi)
        x = d * np.array([np.cos(a), np.sin(a)])
        pi_ = RNG.uniform(0, 10, 2)
        pj = pi_ + x
        vi = RNG.uniform(-1, 1, 2) * vmax / np.sqrt(2)
        vj = RNG.uniform(-1, 1, 2) * vmax / np.sqrt(2)
        v = vi - vj
        rec["n"] += 1
        w = v - x / TAU_H
        wx = float(np.dot(w, x))
        is_cap = wx < 0 and wx * wx > R * R * float(np.dot(w, w))
        hp = orca._halfplane_normal(pi_, pj, vi, vj, R, TAU_H)
        ln = orca_rvo2.orca_lines(float(pi_[0]), float(pi_[1]), float(vi[0]), float(vi[1]),
                                  [(float(pj[0]), float(pj[1]), float(vj[0]), float(vj[1]), 0.0)],
                                  float(R), TAU_H, 0.01)[0]
        p_r = np.array(ln[:2])
        n_r = np.array([-ln[3], ln[2]])
        if hp is None:
            rec["leg_skipped_legacy"] += int(not is_cap)
            continue
        p_l, n_l = hp
        rec["point_max_diff"] = max(rec["point_max_diff"], float(np.linalg.norm(p_l - p_r)))
        if is_cap:
            rec["cap"] += 1
            ang = float(np.arccos(np.clip(np.dot(n_l, n_r), -1, 1)))
            rec["cap_max_angle_rad"] = max(rec["cap_max_angle_rad"], ang)
            rec["cap_max_point_diff"] = max(rec["cap_max_point_diff"], float(np.linalg.norm(p_l - p_r)))
            continue
        rec["leg"] += 1
        s = float(np.dot(n_l, n_r))
        ins = inside_vo(x, v, R, TAU_H)
        side_leg = (x[0] * v[1] - x[1] * v[0]) > 0
        side_rvo = (x[0] * w[1] - x[1] * w[0]) > 0
        rec["leg_side_agree"] += int(side_leg == side_rvo)
        # corrected legacy line: outward normal of the leg direction (left leg: rotate +90 deg;
        # right leg, whose legacy direction lacks RVO2's minus sign: rotate -90 deg)
        dl = leg_direction(x, R, side_leg)
        n_fix = np.array([-dl[1], dl[0]]) if side_leg else np.array([dl[1], -dl[0]])
        rec["leg_fix_agree"] += int(np.dot(n_fix, n_r) > 0.999999)
        rec["leg_legacy_vi_violates"] += int(np.dot(vi - p_l, n_l) < 0)
        if ins:
            rec["leg_inside"] += 1
            rec["leg_inside_agree"] += int(s > 0.999999)
            rec["leg_rvo2_vi_violates_inside"] += int(np.dot(vi - p_r, n_r) < 0)
        else:
            rec["leg_outside"] += 1
            rec["leg_outside_flipped"] += int(s < -0.999999)
            rec["leg_rvo2_vi_violates_outside"] += int(np.dot(vi - p_r, n_r) < 0)
    return rec


def main():
    out = {
        "identity": {
            "repository": "pedestrian-abs (origin https://github.com/pa1aash/pedestrian-abs.git), local clone "
                          "/Users/palaash/Developer/pedestrian-abs-plan/pedestrian-abs",
            "file": "sim/steering/orca.py",
            "function": "_halfplane_normal (leg branch); LP: solve_2d_lp",
            "defect_line": "normal = safe_normalize(u)",
            "defect_lineno_conference": 113,
            "defect_lineno_worktree": 113,
            "introduced_commit": "c43af1600db845b51b02d31a6d7da805caa5d605",
            "introduced_commit_short": "c43af16",
            "introduced_date": "2026-04-02",
            "conference_commit_short": "9762177",
            "conference_blob_short": "71bb509",
            "conference_head_short": "e05d8f6",
            "worktree_blob_short": "ee81620",
            "rvo2_port": "code/sim/steering/orca_rvo2.py:orca_lines, lines 59-68 (leg), 80 (line)",
        },
    }
    out["random_pairs"] = sample(200000, 2.7)
    out["creep_pairs"] = sample(200000, 0.02)
    for k in ("random_pairs", "creep_pairs"):
        r = out[k]
        r["frac_leg_inside_agree"] = r["leg_inside_agree"] / max(r["leg_inside"], 1)
        r["frac_leg_outside_flipped"] = r["leg_outside_flipped"] / max(r["leg_outside"], 1)
        r["frac_leg_legacy_vi_violates"] = r["leg_legacy_vi_violates"] / max(r["leg"], 1)
        r["frac_leg_outside"] = r["leg_outside"] / max(r["leg"], 1)
        r["frac_leg_fix_agree"] = r["leg_fix_agree"] / max(r["leg"], 1)
        r["frac_side_agree"] = r["leg_side_agree"] / max(r["leg"], 1)
    print(revlib.out_json("A14", out))
    for k in ("random_pairs", "creep_pairs"):
        print(k, {a: b for a, b in out[k].items()})


if __name__ == "__main__":
    main()
