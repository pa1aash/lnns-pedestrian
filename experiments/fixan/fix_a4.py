"""A-4: is the published ORCA solver's replay sensitivity a discontinuity or smooth amplification?

Context (E2, data/E2/e2_quench.jsonl): under C3 with the published linear program (C3_pub) the blocker's
freed/held outcome changes in 5 of the 300 replays with 1e-9 m Gaussian position perturbations
(E1b_seed174 seeds 901-904: unperturbed freed at 50.9 s, replays held; E1b_seed187 seed 903: unperturbed
held, replay freed at 109.1 s); RVO2 (C3_rvo2) never changes. This script locates the cause without new
simulation campaigns, in one process:

1. Static scan. At a given state, v_ORCA of every active agent is evaluated exactly as in
   sim/steering/orca.py (ORCAModel._velocity_published / _velocity_rvo2, neighbour lists as in
   Simulation.step: KDTree radius 3 m among active agents, index order). Every active agent's position is
   displaced by eps in an independent random direction (16 direction sets per eps, numpy
   default_rng(20261109)); reported per eps: max over directions and agents of |dv_ORCA| (m/s), the
   gain |dv|/eps (1/s), and the fraction of direction sets with a jump (|dv| > 1e-3 m/s). A smooth
   (Lipschitz) response has gain of order 1/dt = 100 1/s or less and |dv| proportional to eps; a jump is
   |dv| of 1e-3 to 1 m/s at eps = 1e-9 m (gain > 1e6 1/s).
2. Read-only instrumentation. The library functions are wrapped (module attributes replaced by wrappers
   that call the originals and return their results unchanged; no library file is edited): each
   half-plane is classified (collision / cap / left leg / right leg / skipped, and for legs whether the
   published normal u/|u| points opposite to the outward normal of the RVO2 line for the same pair, i.e.
   v_rel lies outside the velocity obstacle and the half-plane is sign-flipped); the published LP is
   mirrored step by step (the mirror's result is asserted bit-identical to the library's) recording for
   each constraint whether it was already satisfied, projected onto, or dropped as infeasible (parallel,
   empty interval, or line outside the speed circle), and which constraints the output violates. For
   RVO2: line branch, linearProgram2 failure index, linearProgram3 use. A jump is attributed to the
   signature components that differ between the base and the displaced state for the agent with the
   largest |dv|.
3. Twin runs (short). The unperturbed run and the flipping replay (same perturbation as e2_quench.py:
   default_rng(seed).normal(0, 1e-9) on every active position) are stepped side by side from the
   snapshot until their positions differ by more than 1e-3 m (or a time cap). At every step the twins'
   v_ORCA (all active agents) are compared; the first step where they differ by > 1e-3 m/s while the
   positions still differ by < 1e-6 m is the first discontinuity event. The static scan is repeated at
   the unperturbed state of that step (and 0.5 s before). RVO2 twins of the same snapshots and published
   twins of non-flipping snapshots are the comparisons.
Output: data/derived/fix_a4.json.
"""
import copy
import json
import math
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(WT, "experiments", "lib"))
from e1lib import CF, DATA, ROOT  # noqa: E402
from w2lib import restore, wilson  # noqa: E402
from sim.core.helpers import safe_normalize  # noqa: E402
import sim.steering.orca as O  # noqa: E402
import sim.steering.orca_rvo2 as R  # noqa: E402
from scipy.spatial import KDTree  # noqa: E402

OUT = os.path.join(DATA, "derived", "fix_a4.json")
SEED = 20261109
EPS = (1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6)
N_DIR = 16
JUMP = 1e-3            # m/s
STRICT_TOL = 1e-9      # violation tolerance for "output violates a half-plane"

# ------------------------------------------------------------------ read-only instrumentation
TR = {"hp": [], "lp": None, "rv_br": None, "rv_lp": None}
_coll, _norm, _lp = O._halfplane_collision, O._halfplane_normal, O.solve_2d_lp
_rv_lines, _rv_solve = R.orca_lines, R.solve


def _w_coll(pos_i, pos_j, vel_i, vel_j, r_sum, dt):
    out = _coll(pos_i, pos_j, vel_i, vel_j, r_sum, dt)
    TR["hp"].append("coll")
    return out


def _w_norm(pos_i, pos_j, vel_i, vel_j, r_sum, tau_h):
    out = _norm(pos_i, pos_j, vel_i, vel_j, r_sum, tau_h)
    x_rel, v_rel = pos_j - pos_i, vel_i - vel_j
    w = v_rel - x_rel / tau_h
    wx = np.dot(w, x_rel)
    if out is None:
        TR["hp"].append("none")
    elif wx < 0 and wx * wx > r_sum * r_sum * np.dot(w, w):
        TR["hp"].append("cap")
    else:
        side = "L" if x_rel[0] * v_rel[1] - x_rel[1] * v_rel[0] > 0 else "R"
        ln = _rv_lines(float(pos_i[0]), float(pos_i[1]), float(vel_i[0]), float(vel_i[1]),
                       [(float(pos_j[0]), float(pos_j[1]), float(vel_j[0]), float(vel_j[1]), 0.0)],
                       float(r_sum), tau_h, 0.01)[0]
        n_out = np.array([-ln[3], ln[2]])
        TR["hp"].append("leg" + side + ("flip" if np.dot(out[1], n_out) < 0 else ""))
    return out


def _mirror_lp(halfplanes, v_pref, max_speed):
    """Copy of sim/steering/orca.py solve_2d_lp that records the status of every constraint."""
    st = []
    ps = np.linalg.norm(v_pref)
    result = v_pref * (max_speed / ps) if ps > max_speed else v_pref.copy()
    for k, (pk, nk) in enumerate(halfplanes):
        if np.dot(result - pk, nk) >= 0:
            st.append("s")
            continue
        ld = np.array([-nk[1], nk[0]])
        tl, tr, inf = -1e9, 1e9, False
        for j in range(k):
            pj, nj = halfplanes[j]
            den = np.dot(ld, nj)
            num = np.dot(pj - pk, nj)
            if abs(den) < 1e-10:
                if num > 0:
                    inf = True
                    break
                continue
            t = num / den
            if den > 0:
                tl = max(tl, t)
            else:
                tr = min(tr, t)
        if inf or tl > tr:
            st.append("D")              # dropped: infeasible with earlier constraints
            continue
        a = np.dot(ld, ld)
        b = 2.0 * np.dot(pk, ld)
        c = np.dot(pk, pk) - max_speed * max_speed
        disc = b * b - 4.0 * a * c
        if disc < 0:
            st.append("C")              # dropped: line misses the speed circle
            continue
        sq = np.sqrt(disc)
        tl, tr = max(tl, (-b - sq) / (2 * a)), min(tr, (-b + sq) / (2 * a))
        if tl > tr:
            st.append("C")
            continue
        t = np.clip(np.dot(v_pref - pk, ld), tl, tr)
        result = pk + t * ld
        st.append("p")
    viol = tuple(k for k, (pk, nk) in enumerate(halfplanes) if np.dot(result - pk, nk) < -STRICT_TOL)
    return result, "".join(st), viol


def _w_lp(halfplanes, v_pref, max_speed):
    out = _lp(halfplanes, v_pref, max_speed)
    m, st, viol = _mirror_lp(halfplanes, v_pref, max_speed)
    assert np.array_equal(m, out), "mirror LP differs from library LP"
    TR["lp"] = (st, viol)
    return out


def _w_rv_lines(px, py, vx, vy, nbrs, r_i, tau_h, dt):
    out = _rv_lines(px, py, vx, vy, nbrs, r_i, tau_h, dt)
    br = []
    for (qx, qy, ux, uy, r_j) in nbrs:
        rpx, rpy, rvx, rvy = qx - px, qy - py, vx - ux, vy - uy
        d2, Rs = rpx * rpx + rpy * rpy, (r_i + r_j) ** 2
        if d2 <= Rs:
            br.append("coll")
            continue
        wx, wy = rvx - rpx / tau_h, rvy - rpy / tau_h
        d1 = wx * rpx + wy * rpy
        if d1 < 0 and d1 * d1 > Rs * (wx * wx + wy * wy):
            br.append("cap")
        else:
            br.append("legL" if rpx * wy - rpy * wx > 0 else "legR")
    TR["rv_br"] = tuple(br)
    return out


def _w_rv_solve(lines, pref_x, pref_y, max_speed):
    out = _rv_solve(lines, pref_x, pref_y, max_speed)
    fail, _ = R._lp2(lines, max_speed, pref_x, pref_y, False)
    TR["rv_lp"] = (fail if fail < len(lines) else -1, bool(out[2]))
    return out


O._halfplane_collision, O._halfplane_normal, O.solve_2d_lp = _w_coll, _w_norm, _w_lp
R.orca_lines, R.solve = _w_rv_lines, _w_rv_solve


# ------------------------------------------------------------------ evaluation at a state
def neighbour_lists(st):
    a = st.active_indices
    nl = [[] for _ in range(st.n)]
    for li, nb in enumerate(KDTree(st.positions[a]).query_ball_point(st.positions[a], r=3.0)):
        nl[a[li]] = [int(a[j]) for j in nb if a[j] != a[li]]
    return nl


def eval_state(orca, variant, st):
    """v_ORCA (n_active x 2) and per-agent signatures."""
    nl = neighbour_lists(st)
    V, S = [], []
    for i in st.active_indices:
        v_pref = float(st.desired_speeds[i]) * safe_normalize(st.goals[i] - st.positions[i])
        vmax = 2.0 * float(st.desired_speeds[i])
        TR["hp"] = []
        if variant == "published":
            v = orca._velocity_published(i, st, nl, v_pref, vmax)
            S.append({"hp": tuple(TR["hp"]), "lp": TR["lp"][0], "viol": TR["lp"][1]})
        else:
            v = orca._velocity_rvo2(i, st, nl, v_pref, vmax)
            S.append({"hp": TR["rv_br"], "lp": TR["rv_lp"]})
        V.append(np.asarray(v, float))
    return np.array(V), S


def sig_diff(a, b, variant):
    """Which signature components differ (published: branch, flip, drop, proj, viol; RVO2: branch, lp3)."""
    c = set()
    if variant == "published":
        if len(a["hp"]) != len(b["hp"]):
            c.add("halfplane_count")
        for x, y in zip(a["hp"], b["hp"]):
            if x != y:
                if x.replace("flip", "") == y.replace("flip", ""):
                    c.add("leg_normal_flip")
                else:
                    c.add("halfplane_branch")
        for x, y in zip(a["lp"], b["lp"]):
            if x != y:
                c.add("lp_drop" if ("D" in (x, y) or "C" in (x, y)) else "lp_projection")
        if a["viol"] != b["viol"]:
            c.add("violated_set")
    else:
        if a["hp"] != b["hp"]:
            c.add("halfplane_branch")
        if a["lp"] != b["lp"]:
            c.add("lp3_or_failure_index")
    return sorted(c)


def displaced(st, d):
    s2 = copy.copy(st)
    s2.positions = st.positions.copy()
    s2.positions[st.active_indices] += d
    return s2


def scan(sim, rng_seed=SEED, eps_list=EPS, n_dir=N_DIR):
    st = sim.state
    orca = sim.steering.orca
    a = st.active_indices
    out = {"t": float(sim.time), "n_active": int(len(a)),
           "speeds_max": float(np.max(np.linalg.norm(st.velocities[a], axis=1)))}
    for variant in ("published", "rvo2"):
        V0, S0 = eval_state(orca, variant, st)
        rng = np.random.default_rng(rng_seed)
        rows = {}
        for eps in eps_list:
            dvs, causes, njump, nsig, njump_sig = [], {}, 0, 0, 0
            for _ in range(n_dir):
                th = rng.uniform(0, 2 * np.pi, len(a))
                V, S = eval_state(orca, variant, displaced(st, eps * np.column_stack([np.cos(th), np.sin(th)])))
                dv = np.linalg.norm(V - V0, axis=1)
                k = int(np.argmax(dv))
                dvs.append(float(dv[k]))
                ch = sig_diff(S0[k], S[k], variant)
                anych = any(sig_diff(S0[q], S[q], variant) for q in range(len(a)))
                nsig += int(anych)
                if dv[k] > JUMP:
                    njump += 1
                    njump_sig += int(bool(ch))
                    for cc in ch or ["none"]:
                        causes[cc] = causes.get(cc, 0) + 1
            dvs = np.array(dvs)
            rows[f"{eps:.0e}"] = {"eps_m": eps, "max_dv": float(dvs.max()), "median_dv": float(np.median(dvs)),
                                  "max_gain": float(dvs.max() / eps), "n_dir": n_dir, "n_jump": njump,
                                  "jump_frac": njump / n_dir, "jump_frac_ci95": list(wilson(njump, n_dir)[1:]),
                                  "n_signature_change": nsig, "n_jump_with_signature_change": njump_sig,
                                  "jump_causes": causes}
        e9, e6 = rows["1e-09"]["max_dv"], rows["1e-06"]["max_dv"]
        out[variant] = {"base_v_orca": V0.tolist(), "base_signature": [
            {k: (list(v) if isinstance(v, tuple) else v) for k, v in s.items()} for s in S0],
            "base_n_dropped": int(sum(s["lp"].count("D") + s["lp"].count("C") for s in S0)) if variant == "published"
            else int(sum(s["lp"][1] for s in S0)),
            "by_eps": rows,
            "ratio_dv_1e-6_over_1e-9": (e6 / e9) if e9 > 0 else None,
            "max_gain_all_eps": max(r["max_gain"] for r in rows.values()),
            "classification": ("jump" if e9 > JUMP else
                               ("smooth" if max(r["max_gain"] for r in rows.values()) <= 1e4 else "mixed"))}
    return out


# ------------------------------------------------------------------ twin runs
def load_snap(tag):
    return pickle.load(open(os.path.join(DATA, "E1", "library", tag + ".pkl"), "rb"))


def make(tag, variant, perturb=None):
    sim = restore(load_snap(tag), "C3", flags={**CF, "w2_orca": variant})
    if perturb is not None:
        st = sim.state
        a = st.active_indices
        st.positions[a] += np.random.default_rng(perturb).normal(0, 1e-9, (len(a), 2))
    return sim


def twin(tag, variant, perturb, t_cap, sep_stop=1e-3, blocker=None, keep_states=True):
    A, B = make(tag, variant), make(tag, variant, perturb)
    orca_A, orca_B = A.steering.orca, B.steering.orca
    hist = []           # (step, t, sep, dv_twin)
    first = None
    events = []
    t0s = load_snap(tag)["time"]
    states = {}
    nmax = int(round(t_cap / A.params["dt"]))
    w0 = time.process_time()
    for k in range(nmax):
        sa, sb = A.state, B.state
        if not np.array_equal(sa.active, sb.active):
            sep = float("inf")
            dv, anysig, dropsig = float("nan"), 0, 0
        else:
            sep = float(np.max(np.linalg.norm(sa.positions[sa.active] - sb.positions[sb.active], axis=1))) \
                if sa.n_active else 0.0
            if sa.n_active:
                VA, SA = eval_state(orca_A, variant, sa)
                VB, SB = eval_state(orca_B, variant, sb)
                dvv = np.linalg.norm(VA - VB, axis=1)
                dv = float(dvv.max())
                sch = [sig_diff(SA[q], SB[q], variant) for q in range(len(SA))]
                anysig = int(any(sch))
                dropsig = int(any(("lp_drop" in c or "leg_normal_flip" in c or "halfplane_branch" in c) for c in sch))
            else:
                dv, anysig, dropsig = 0.0, 0, 0
        hist.append((k, float(A.time), sep, dv, anysig, dropsig))
        if np.isfinite(dv) and dv > JUMP and sep <= sep_stop:
            q = int(np.argmax(dvv))
            events.append({"t": float(A.time - t0s), "sep_m": sep, "dv_twin": dv, "gain": dv / max(sep, 1e-300),
                           "agent": int(sa.active_indices[q]),
                           "is_blocker": blocker is not None and int(sa.active_indices[q]) == blocker,
                           "agent_speed": float(np.linalg.norm(sa.velocities[sa.active_indices[q]])),
                           "signature_change": sig_diff(SA[q], SB[q], variant),
                           "dropped_A": SA[q]["lp"].count("D") + SA[q]["lp"].count("C") if variant == "published" else None,
                           "dropped_B": SB[q]["lp"].count("D") + SB[q]["lp"].count("C") if variant == "published" else None,
                           "lp_A": SA[q]["lp"] if variant == "published" else list(SA[q]["lp"]),
                           "lp_B": SB[q]["lp"] if variant == "published" else list(SB[q]["lp"]),
                           "hp_A": list(SA[q]["hp"]), "hp_B": list(SB[q]["hp"])})
            if events[-1]["signature_change"] and "disc" not in states:
                states["disc"] = (copy.deepcopy(sa), A.time)
        if keep_states and k % 50 == 0:
            states[k] = (copy.deepcopy(A.state), A.time)
        if first is None and np.isfinite(dv) and dv > JUMP and sep < 1e-6:
            q = int(np.argmax(dvv))
            first = {"step": k, "t": float(A.time - load_snap(tag)["time"]), "sep_m": sep, "dv_twin": dv,
                     "gain": dv / max(sep, 1e-300), "agent": int(sa.active_indices[q]),
                     "agent_speed": float(np.linalg.norm(sa.velocities[sa.active_indices[q]])),
                     "agent_x": sa.positions[sa.active_indices[q]].tolist(),
                     "is_blocker": blocker is not None and int(sa.active_indices[q]) == blocker,
                     "signature_change": sig_diff(SA[q], SB[q], variant),
                     "sig_A": {k2: (list(v) if isinstance(v, tuple) else v) for k2, v in SA[q].items()},
                     "sig_B": {k2: (list(v) if isinstance(v, tuple) else v) for k2, v in SB[q].items()}}
            states["first"] = (copy.deepcopy(A.state), A.time)
            if k >= 50:
                states["before"] = states[(k - 50) // 50 * 50]
        if sep > sep_stop or sa.n_active == 0:
            break
        A.step()
        B.step()
    H = np.array([h[2:] for h in hist], float)
    sep, dv, sg, sgd = H[:, 0], H[:, 1], H[:, 2] > 0, H[:, 3] > 0
    tt = np.array([h[1] for h in hist]) - load_snap(tag)["time"]
    fin = np.isfinite(sep) & np.isfinite(dv)
    # smooth twin steps: separation small, no jump
    small = fin & (sep > 0) & (sep < 1e-6)
    gains = dv[small] / sep[small]
    n_jump = int(np.sum(small & (dv > JUMP)))
    t0 = load_snap(tag)["time"]
    res = {"snapshot": tag, "variant": variant, "perturb_seed": perturb, "steps": len(hist),
           "t_end": float(hist[-1][1] - t0), "sep_final_m": float(sep[fin][-1]) if fin.any() else None,
           "n_steps_sep_lt_1e-6": int(small.sum()), "n_jump_steps_sep_lt_1e-6": n_jump,
           "median_gain_no_jump": float(np.median(gains[dv[small] <= JUMP])) if np.any(dv[small] <= JUMP) else None,
           "max_dv_twin_sep_lt_1e-6": float(dv[small].max()) if small.any() else None,
           "first_jump": first, "jump_events": events[:20], "n_jump_events": len(events),
           "jump_events_with_signature_change": [e for e in events if e["signature_change"]],
           "first_jump_event_with_signature_change": next((e for e in events if e["signature_change"]), None),
           "first_event_any_sep": events[0] if events else None, "cpu_s": time.process_time() - w0,
           "sep_at_t": {f"{tt:g}": float(sep[min(int(round(tt / 0.01)), len(sep) - 1)])
                        for tt in (0, 1, 2, 5, 10, 20, 40, 60, 100) if int(round(tt / 0.01)) < len(sep)},
           "t_sep_gt_1e-6": next((float(h[1] - t0) for h in hist if h[2] > 1e-6), None),
           "t_sep_gt_1e-3": next((float(h[1] - t0) for h in hist if h[2] > 1e-3), None)}
    allw = fin & (sep > 1e-12) & (sep <= sep_stop)
    g_all = dv[allw] / sep[allw]
    res["all_steps"] = {"n": int(allw.sum()), "max_gain": float(g_all.max()) if allw.any() else None,
                        "p99_gain": float(np.percentile(g_all, 99)) if allw.any() else None,
                        "n_jump_gain_gt_1e4": int(np.sum((dv[allw] > JUMP) & (g_all > 1e4))),
                        "n_steps_signature_differs": int(sg[allw].sum()),
                        "n_steps_branch_drop_or_flip_differs": int(sgd[allw].sum()),
                        "max_dv_on_signature_steps": float(dv[allw & sg].max()) if (allw & sg).any() else None,
                        "method": "twin steps with 1e-12 < separation <= 1e-3 m; gain = |dv_ORCA| / separation"}
    fw = fin & (sep > 1e-8) & (sep < 1e-4)
    if fw.sum() > 20:
        sl, ic = np.polyfit(tt[fw], np.log(sep[fw]), 1)
        res["growth_rate_per_s"] = float(sl)
        res["growth_fit_window"] = "1e-8 < separation < 1e-4 m, least squares of ln(separation) on t"
    else:
        res["growth_rate_per_s"] = None
    return res, states


def scan_at(tag, variant, state_t, eps_list=EPS):
    sim = make(tag, variant)
    sim.state = copy.deepcopy(state_t[0])
    sim.time = state_t[1]
    return scan(sim, eps_list=eps_list)


EPS_WIDE = EPS + (3e-6, 1e-5, 3e-5, 1e-4, 3e-4)


# ------------------------------------------------------------------ main
FLIPS = [("E1b_seed174", 72, s) for s in (901, 902, 903, 904)] + [("E1b_seed187", 47, 903)]
CONTROLS = [("E1b_seed52", "lone_keystone, freed 3.8 s, replays identical"),
            ("E1b_seed230", "second trap, freed 16.8 s, replays identical"),
            ("E1b_seed192", "second trap, held, replays identical")]
TIMING = [("E1b_seed130", 91, 900, "second trap, freed 34.4 s; replay 900 freed 80.8 s later")]


def main():
    c0 = time.process_time()
    out = {"script": "experiments/fixan/fix_a4.py", "seed": SEED, "jump_threshold_m_per_s": JUMP,
           "eps_m": list(EPS), "n_directions": N_DIR,
           "method": ("v_ORCA of every active agent evaluated with the library solvers (published LP, RVO2) at a "
                      "state and at copies with every active position displaced by eps in independent random "
                      "directions; jump = |dv| > 1e-3 m/s; signatures from read-only wrappers (half-plane branch, "
                      "leg-normal sign, LP constraint status, dropped/violated constraints; RVO2 LP2 failure, LP3)")}
    flips = {}
    # 1. static scan at the flipping snapshots (t = 0, agents at rest)
    for tag in sorted({f[0] for f in FLIPS}):
        flips[tag] = {"snapshot_state": scan(make(tag, "published"))}
    # 2. twins of the flipping replays (published) and RVO2 twins of the same replays
    twins = []
    for tag, b, ps in FLIPS:
        cap = 60.0 if tag == "E1b_seed174" else 115.0
        r, S = twin(tag, "published", ps, cap, blocker=b, keep_states=True)
        if "disc" in S:
            r["scan_at_first_discontinuity"] = scan_at(tag, "published", S["disc"], EPS_WIDE)
        if r["first_jump"] is not None and "first" in S:
            r["scan_at_first_jump"] = scan_at(tag, "published", S["first"])
            if "before" in S:
                r["scan_0p5s_before"] = scan_at(tag, "published", S["before"])
        twins.append(r)
        print(tag, ps, "first jump", r["first_jump"] and {k: r["first_jump"][k] for k in
              ("t", "sep_m", "dv_twin", "signature_change", "is_blocker")}, "sep>1e-3 at", r["t_sep_gt_1e-3"],
              "cpu", round(time.process_time() - c0), flush=True)
    out["flip_twins_published"] = twins
    # static scans along the unperturbed published trajectory during the creep (every 1 s)
    creep = {}
    for tag, b, ps in [FLIPS[0], FLIPS[4]]:
        _, S = twin(tag, "published", ps, 20.0, sep_stop=1e9, blocker=b, keep_states=True)
        creep[tag] = [scan_at(tag, "published", S[k]) for k in sorted(x for x in S if isinstance(x, int))
                      if k % 100 == 0 and k > 0]
        print("creep", tag, [(round(c["t"] - load_snap(tag)["time"], 1), c["published"]["by_eps"]["1e-09"]["max_dv"],
                              c["rvo2"]["by_eps"]["1e-09"]["max_dv"]) for c in creep[tag]], flush=True)
    out["creep_scans"] = creep
    rv = []
    for tag, b, ps in FLIPS:
        r, _ = twin(tag, "rvo2", ps, 15.0, blocker=b, keep_states=False)
        rv.append(r)
        print("rvo2", tag, ps, r["first_jump"] is not None, r["max_dv_twin_sep_lt_1e-6"], r["sep_final_m"], flush=True)
    out["flip_twins_rvo2"] = rv
    out["flip_snapshots"] = flips
    # 3. timing-shift case and controls (published twins + static scan at t = 0)
    ctl = []
    for tag, b, ps, note in TIMING:
        r, S = twin(tag, "published", ps, 40.0, blocker=b, keep_states=True)
        r["note"] = note
        if r["first_jump"] is not None and "first" in S:
            r["scan_at_first_jump"] = scan_at(tag, "published", S["first"])
        out["timing_shift_twin_published"] = r
        print("timing", tag, r["first_jump"] and r["first_jump"]["dv_twin"], flush=True)
    for tag, note in CONTROLS:
        r, _ = twin(tag, "published", 901, 20.0, keep_states=False)
        r["note"] = note
        r["snapshot_scan"] = scan(make(tag, "published"))
        ctl.append(r)
        print("control", tag, r["first_jump"] is not None, r["n_jump_steps_sep_lt_1e-6"], r["sep_final_m"], flush=True)
    out["controls_published"] = ctl

    # ---------------------------------------------------------------- headline numbers
    fj = [t["first_jump"] for t in twins if t["first_jump"] is not None]
    sc = [t["scan_at_first_jump"] for t in twins if "scan_at_first_jump" in t]
    pub9 = [s["published"]["by_eps"]["1e-09"] for s in sc]
    rv9 = [s["rvo2"]["by_eps"]["1e-09"] for s in sc]
    rv6 = [s["rvo2"]["by_eps"]["1e-06"] for s in sc]
    causes = {}
    for f in fj:
        for c in f["signature_change"] or ["none"]:
            causes[c] = causes.get(c, 0) + 1
    nj = sum(p["n_jump"] for p in pub9)
    nd = sum(p["n_dir"] for p in pub9)
    out["headline"] = {
        "n_flipping_replays": len(FLIPS), "n_with_jump_found": len(fj),
        "first_jump_t_s": [f["t"] for f in fj],
        "first_jump_dv_twin_m_per_s": {"min": min(f["dv_twin"] for f in fj) if fj else None,
                                       "max": max(f["dv_twin"] for f in fj) if fj else None,
                                       "values": [f["dv_twin"] for f in fj]},
        "first_jump_sep_m": {"max": max(f["sep_m"] for f in fj) if fj else None},
        "first_jump_agent_speed_m_per_s": [f["agent_speed"] for f in fj],
        "first_jump_causes": causes,
        "scan_pub_1e-9_max_dv": {"min": min(p["max_dv"] for p in pub9) if pub9 else None,
                                 "max": max(p["max_dv"] for p in pub9) if pub9 else None},
        "scan_pub_1e-9_jump_frac": {"n_jump": nj, "n": nd, "frac": nj / nd if nd else None,
                                    "ci95": list(wilson(nj, nd)[1:]) if nd else None},
        "scan_rvo2_1e-9_max_dv": max(p["max_dv"] for p in rv9) if rv9 else None,
        "scan_rvo2_1e-6_max_dv": max(p["max_dv"] for p in rv6) if rv6 else None,
        "rvo2_twins_any_jump": any(r["first_jump"] is not None for r in rv),
        "rvo2_twins_max_dv_sep_lt_1e-6": max((r["max_dv_twin_sep_lt_1e-6"] or 0) for r in rv),
        "snapshot_state_pub_1e-9_max_dv": max(flips[t]["snapshot_state"]["published"]["by_eps"]["1e-09"]["max_dv"]
                                              for t in flips),
        "controls_any_jump": [c["first_jump"] is not None for c in ctl],
        "method": ("first_jump: first step of the side-by-side unperturbed / flipping-replay twin at which v_ORCA "
                   "of some agent differs by > 1e-3 m/s while positions differ by < 1e-6 m; scan_*: static "
                   "displacement scan at the unperturbed state of that step, 16 direction sets per eps; "
                   "jump_frac CI Wilson 95%"),
    }
    H = out["headline"]
    fd = [t["first_jump_event_with_signature_change"] for t in twins]
    fd = [e for e in fd if e is not None]
    allsig = [e for t in twins for e in t["jump_events_with_signature_change"]]
    ctl_sig = [e for t in [out["timing_shift_twin_published"]] + ctl for e in t["jump_events_with_signature_change"]]
    def has(e, c):
        return c in e["signature_change"]
    sd = [t["scan_at_first_discontinuity"]["published"]["by_eps"] for t in twins if "scan_at_first_discontinuity" in t]
    sdr = [t["scan_at_first_discontinuity"]["rvo2"]["by_eps"] for t in twins if "scan_at_first_discontinuity" in t]
    H["first_discontinuity"] = {
        "n": len(fd), "t_s": [e["t"] for e in fd], "sep_m": [e["sep_m"] for e in fd],
        "sep_min_m": min(e["sep_m"] for e in fd), "sep_max_m": max(e["sep_m"] for e in fd),
        "dv_m_per_s": [e["dv_twin"] for e in fd],
        "dv_min_m_per_s": min(e["dv_twin"] for e in fd), "dv_max_m_per_s": max(e["dv_twin"] for e in fd),
        "agent_speed_m_per_s": [e["agent_speed"] for e in fd],
        "t_min_s": min(e["t"] for e in fd), "t_max_s": max(e["t"] for e in fd),
        "agent_speed_max_m_per_s": max(e["agent_speed"] for e in fd),
        "n_leg_normal_flip": sum(has(e, "leg_normal_flip") for e in fd),
        "n_halfplane_branch": sum(has(e, "halfplane_branch") for e in fd),
        "n_lp_drop": sum(has(e, "lp_drop") for e in fd),
        "n_dropped_constraint_either_twin": sum(int((e["dropped_A"] or 0) + (e["dropped_B"] or 0) > 0) for e in fd),
        "method": ("first twin step with |dv_ORCA| > 1e-3 m/s at which the agent's half-plane branch, leg-normal "
                   "sign or LP constraint status differs between the twins")}
    H["all_discontinuity_events_flip_twins"] = {
        "n": len(allsig), "n_leg_normal_flip": sum(has(e, "leg_normal_flip") for e in allsig),
        "n_halfplane_branch": sum(has(e, "halfplane_branch") for e in allsig),
        "n_lp_drop": sum(has(e, "lp_drop") for e in allsig),
        "n_dropped_constraint_either_twin": sum(int((e["dropped_A"] or 0) + (e["dropped_B"] or 0) > 0) for e in allsig),
        "dv_min_m_per_s": min(e["dv_twin"] for e in allsig), "dv_max_m_per_s": max(e["dv_twin"] for e in allsig)}
    H["discontinuity_events_timing_and_controls"] = {
        "n": len(ctl_sig), "n_lp_drop": sum(has(e, "lp_drop") for e in ctl_sig),
        "per_snapshot": {t["snapshot"]: len(t["jump_events_with_signature_change"])
                         for t in [out["timing_shift_twin_published"]] + ctl}}
    jumps_before = [e for t in twins for e in t["jump_events"] if not e["signature_change"]]
    H["smooth_phase"] = {
        "first_dv_gt_1e-3_t_s": [t["jump_events"][0]["t"] if t["jump_events"] else None for t in twins],
        "first_dv_gt_1e-3_sep_m": [t["jump_events"][0]["sep_m"] if t["jump_events"] else None for t in twins],
        "first_dv_gt_1e-3_signature_change": [t["jump_events"][0]["signature_change"] if t["jump_events"] else None
                                              for t in twins],
        "method": "first twin step with |dv_ORCA| > 1e-3 m/s (any cause)"}
    if sd:
        H["scan_at_first_discontinuity_published"] = {
            e: {"max_dv": max(x[e]["max_dv"] for x in sd), "n_jump": sum(x[e]["n_jump"] for x in sd),
                "n": sum(x[e]["n_dir"] for x in sd)} for e in sd[0]}
        H["scan_at_first_discontinuity_rvo2"] = {
            e: {"max_dv": max(x[e]["max_dv"] for x in sdr), "n_jump": sum(x[e]["n_jump"] for x in sdr),
                "n": sum(x[e]["n_dir"] for x in sdr)} for e in sdr[0]}
        for nm in ("scan_at_first_discontinuity_published", "scan_at_first_discontinuity_rvo2"):
            for e, x in H[nm].items():
                x["jump_frac_ci95"] = list(wilson(x["n_jump"], x["n"])[1:])
        H["smallest_eps_with_jump_published_m"] = min((float(e) for x in sd for e in x if x[e]["n_jump"] > 0),
                                                       default=None)
    H["flip_twins"] = {
        "n": len(twins),
        "growth_rate_per_s": [t["growth_rate_per_s"] for t in twins],
        "growth_rate_median_per_s": float(np.median([t["growth_rate_per_s"] for t in twins])),
        "growth_rate_min_per_s": float(min(t["growth_rate_per_s"] for t in twins)),
        "growth_rate_max_per_s": float(max(t["growth_rate_per_s"] for t in twins)),
        "t_sep_gt_1e-3_min_s": float(min(t["t_sep_gt_1e-3"] for t in twins)),
        "t_sep_gt_1e-3_max_s": float(max(t["t_sep_gt_1e-3"] for t in twins)),
        "t_sep_gt_1e-6_s": [t["t_sep_gt_1e-6"] for t in twins],
        "t_sep_gt_1e-3_s": [t["t_sep_gt_1e-3"] for t in twins],
        "max_gain_per_s": max(t["all_steps"]["max_gain"] for t in twins),
        "median_gain_per_s": [t["median_gain_no_jump"] for t in twins],
        "n_jump_steps": sum(t["all_steps"]["n_jump_gain_gt_1e4"] for t in twins),
        "n_steps": sum(t["all_steps"]["n"] for t in twins),
        "n_steps_branch_drop_or_flip_differs": sum(t["all_steps"]["n_steps_branch_drop_or_flip_differs"] for t in twins),
        "max_dv_twin_sep_lt_1e-6_m_per_s": max(t["max_dv_twin_sep_lt_1e-6"] for t in twins),
        "method": "side-by-side twins (unperturbed vs flipping replay), published LP, until separation > 1e-3 m"}
    H["rvo2_twins_growth_rate_per_s"] = [r["growth_rate_per_s"] for r in rv]
    H["rvo2_twins_median_gain_per_s"] = [r["median_gain_no_jump"] for r in rv]
    H["controls_growth_rate_per_s"] = {c["snapshot"]: c["growth_rate_per_s"] for c in ctl}
    H["controls_t_sep_gt_1e-3_s"] = {c["snapshot"]: c["t_sep_gt_1e-3"] for c in ctl}
    cs = [c for v in creep.values() for c in v]
    for var in ("published", "rvo2"):
        H[f"creep_scan_{var}"] = {
            "n_states": len(cs),
            "max_dv_by_eps": {e: max(c[var]["by_eps"][e]["max_dv"] for c in cs) for e in cs[0][var]["by_eps"]},
            "max_gain_per_s": max(c[var]["max_gain_all_eps"] for c in cs),
            "n_states_jump_at_1e-9": sum(int(c[var]["by_eps"]["1e-09"]["n_jump"] > 0) for c in cs),
            "n_states_jump_any_eps": sum(int(any(r["n_jump"] > 0 for r in c[var]["by_eps"].values())) for c in cs),
            "n_states_with_dropped_constraint": sum(int(c[var]["base_n_dropped"] > 0) for c in cs),
            "method": "static scan every 1 s on the unperturbed published trajectory (t = 1..19 s) of E1b_seed174 and E1b_seed187"}
    out["cpu_s_total"] = time.process_time() - c0
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    print(json.dumps(out["headline"], indent=1, default=float))


if __name__ == "__main__":
    main()
