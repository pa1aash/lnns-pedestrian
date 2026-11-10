"""A11: the constraint part of force-coupled ORCA at rest (v = 0), on the pair standoffs and the second traps.

Inputs: the 46 pair snapshots (experiments/E7b/e7b_pairs.py; data/E7b/library; flags CF + B_w = 0.04), the 26
second-trap snapshots of the E2 library (data/derived/selection.json, stratum lone_keystone_second_trap; flags
CF), quench outcomes data/E7b/e7b_quench.jsonl ("freed": a member exits within 120 s) and data/E2/e2_quench.jsonl
(blocker exits within 120 s), unperturbed runs only; the 20 s traces data/E7b/e7b_pair_trace.jsonl.

Static split (part "static"). Each snapshot is restored under C3 with w2_orca in {rvo2, published}; all
velocities are set to zero, neighbour lists (radius 3 m among the residual agents) and grid densities are those
of Simulation.step at the snapshot. For each residual agent i: v_pref = v0_i e_i (e_i unit vector to the goal),
v_ORCA from the code's solver (ORCAModel._velocity_rvo2 / _velocity_published, the code path of the
constraint_only split), the density gate w_o = 1 - s(rho; 4, 2), and
   drive part       D_i = w_o m (v_pref - 0) / tau_ORCA       (magnitude w_o m v0 / tau_ORCA)
   constraint part  C_i = w_o m (v_ORCA - v_pref) / tau_ORCA  (the rest-state value of the constraint_only arm)
C_i is decomposed onto e_i (axial, + = towards the goal), e_perp = (-e_y, e_x) (the code's bias normal), and the
lateral unit vector pointing towards the door axis y = 5 (+ = towards the axis); its angle to the unit vector
n_ij from i to its partner j (pairs: the other member; second traps: the nearest other residual agent) is
reported, with the binding test |v_ORCA - v_pref| > 1e-9 m/s and the leave-one-out binding neighbour. For a
cap-region ORCA line at zero relative velocity the permitted set is v . n_ij <= (d_ij - r_ij) / (2 tau_h), so a
binding constraint is predicted to be C_i = -w_o m (v_pref . n_ij - s_ij) n_ij / tau_ORCA with
s_ij = (d_ij - r_ij) / (2 tau_h); the prediction is compared with C_i.

Rest-field relaxation (part "relax"). The overdamped flow dx_i/dt = (tau_i / m_i) F_i(x, v = 0) of the code's
rest field (velocities held at zero, densities frozen at the snapshot, neighbour lists of the residual agents
recomputed each step), Euler step 0.01 s up to 120 s, as experiments/lib/pairlib.relax; arms C1, drive_only,
constraint_only (rvo2, published), C3 (rvo2, published). Freed: the blocker (second traps) or any member (pairs)
reaches x > 10.3 m; held: max |F| < 0.05 N; otherwise undecided. Agreement with the 120 s quench outcome.

Output: data/derived/rev_A11.json; per-agent rows in data/revision/A11/static.jsonl and relax.jsonl.
"""
import copy
import json
import math
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import CF, DATA, DERIVED, ROOT, np  # noqa: E402
from w2lib import restore  # noqa: E402
from sim.core import helpers as _helpers  # noqa: E402
from sim.core.helpers import safe_normalize  # noqa: E402
from e7b_pairs import pairs  # noqa: E402

SOLVERS = ("rvo2", "published")
QARM = {"rvo2": "C3_rvo2", "published": "C3_pub"}
CARM = {"rvo2": "constraint_only_rvo2", "published": "constraint_only_pub"}
RELAX_ARMS = {"C1": ("C1", {}), "drive_only": ("C3", {"w2_orca_split": "drive_only"}),
              "constraint_only_rvo2": ("C3", {"w2_orca": "rvo2", "w2_orca_split": "constraint_only"}),
              "constraint_only_pub": ("C3", {"w2_orca": "published", "w2_orca_split": "constraint_only"}),
              "C3_rvo2": ("C3", {"w2_orca": "rvo2"}), "C3_pub": ("C3", {"w2_orca": "published"})}
OUTD = revlib.data_dir("A11")


def library():
    L = []
    for p in pairs():
        L.append({"tag": p["tag"], "snap": p["snap"], "kind": "pair", "flags": {"B_w": 0.04}, "focus": None})
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]
    for s in sel:
        if s["class"] == "lone_keystone_second_trap":
            L.append({"tag": s["tag"], "snap": os.path.join(ROOT, s["snap"]), "kind": "second_trap",
                      "flags": {}, "focus": int(s["blocker"])})
    return L


def outcomes():
    O = {}
    for ln in open(os.path.join(DATA, "E7b", "e7b_quench.jsonl")):
        r = json.loads(ln)
        if r.get("perturb") is None and r.get("delta") is None:
            O[(r["snap"][:-4], r["arm"])] = bool(r["freed"] and r["first_t"] is not None and r["first_t"] <= 120 + 1e-9)
    sel = {s["tag"]: s["blocker"] for s in json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]}
    for ln in open(os.path.join(DATA, "E2", "e2_quench.jsonl")):
        r = json.loads(ln)
        if r.get("perturb") is None and r["deterministic"]:
            tag = r["job_id"].split("|")[0]
            t = r["exits"].get(str(sel[tag]))
            O[(tag, r["arm"])] = t is not None and t <= 120 + 1e-9
    return O


def frozen_nl(st, ids):
    P = st.positions
    nl = [[] for _ in range(st.n)]
    for i in ids:
        nl[i] = [j for j in ids if j != i and st.active[j] and np.linalg.norm(P[j] - P[i]) <= 3.0]
    return nl


def static(item, solver):
    snap = pickle.load(open(item["snap"], "rb"))
    sim = restore(snap, "C3", flags={**CF, **item["flags"], "w2_orca": solver})
    _helpers.CLIP_MODE = "none"
    st = copy.deepcopy(sim.state)
    st.velocities[:] = 0.0
    ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
    nl = frozen_nl(st, ids)
    rho = np.array([len(n) / (math.pi * 9.0) for n in nl])
    orca = sim.steering.orca
    p = sim.steering.params
    tau_o, tau_h = orca.tau_orca, orca.time_horizon
    vel = orca._velocity_rvo2 if solver == "rvo2" else orca._velocity_published
    P = st.positions
    rows = []
    for i in ids:
        x, m, v0 = P[i], float(st.masses[i]), float(st.desired_speeds[i])
        e = safe_normalize(st.goals[i] - x)
        ep = np.array([-e[1], e[0]])
        vp = v0 * e
        w = 1.0 - 1.0 / (1.0 + math.exp(-p.get("k_orca_fade", 2.0) * (rho[i] - p.get("rho_orca_fade", 4.0))))
        vo = np.asarray(vel(i, st, nl, vp, 2 * v0), float)
        C = w * m * (vo - vp) / tau_o
        D = w * m * vp / tau_o
        tow = np.array([0.0, 1.0 if x[1] < 5.0 else -1.0])  # lateral unit towards the axis
        tow_perp = ep * np.sign(ep @ tow)
        others = [j for j in ids if j != i]
        j = min(others, key=lambda k: np.linalg.norm(P[k] - x)) if others else None
        r = {"tag": item["tag"], "kind": item["kind"], "solver": solver, "id": i,
             "role": ("blocker" if i == item["focus"] else "other") if item["kind"] == "second_trap"
             else ("lower" if i == ids[0] else "upper"),
             "pos": x.tolist(), "w_o": w, "rho": float(rho[i]), "e": e.tolist(),
             "drive_mag_N": float(np.linalg.norm(D)), "drive_axisward_N": float(D @ tow),
             "cons_N": C.tolist(), "cons_mag_N": float(np.linalg.norm(C)),
             "cons_axial_N": float(C @ e), "cons_eperp_N": float(C @ ep), "cons_lat_towards_axis_N": float(C @ tow_perp),
             "cons_x_N": float(C[0]), "binds": bool(np.linalg.norm(vo - vp) > 1e-9),
             "cons_over_drive": float(np.linalg.norm(C) / np.linalg.norm(D)),
             "n_neighbours": len(nl[i])}
        if j is not None:
            nij = (P[j] - x) / np.linalg.norm(P[j] - x)
            d = float(np.linalg.norm(P[j] - x))
            R = float(st.radii[i] + st.radii[j])
            s = (d - R) / (2 * tau_h)
            pred = -w * m * max(vp @ nij - s, 0.0) * nij / tau_o
            r.update({"partner": j, "partner_dist_m": d, "partner_gap_m": d - R, "slack_m_per_s": s,
                      "vpref_towards_partner_m_per_s": float(vp @ nij),
                      "n_partner": nij.tolist(), "partner_dx_m": float(P[j, 0] - x[0]),
                      "cos_cons_to_partner": float(C @ nij / np.linalg.norm(C)) if np.linalg.norm(C) > 1e-9 else None,
                      "cap_prediction_N": pred.tolist(),
                      "cap_prediction_err_N": float(np.linalg.norm(pred - C)),
                      "drive_towards_partner_N": float(D @ nij)})
            # leave-one-out binding neighbour
            if r["binds"]:
                best = None
                for k in nl[i]:
                    nl2 = list(nl)
                    nl2[i] = [q for q in nl[i] if q != k]
                    vk = np.asarray(vel(i, st, nl2, vp, 2 * v0), float)
                    dd = float(np.linalg.norm(vo - vk))
                    if best is None or dd > best[1]:
                        best = (int(k), dd)
                r["binding_neighbour"] = best[0]
                r["binding_is_partner"] = best[0] == j
        rows.append(r)
    return rows


def relax(item, arm, T=120.0, h=0.01):
    cfg, fl = RELAX_ARMS[arm]
    snap = pickle.load(open(item["snap"], "rb"))
    sim = restore(snap, cfg, flags={**CF, **item["flags"], **fl})
    _helpers.CLIP_MODE = "none"
    st = copy.deepcopy(sim.state)
    st.velocities[:] = 0.0
    ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
    nl = frozen_nl(st, ids)
    dens = np.array([len(n) / (math.pi * 9.0) for n in nl])
    k = np.array(ids)
    gain = (st.taus[k] / st.masses[k])[:, None]
    hm, walls = sim.steering, sim.world.walls
    t, F = 0.0, np.zeros((len(ids), 2))
    while t < T - 1e-9:
        nl = frozen_nl(st, [i for i in ids if st.active[i]])
        F = hm.compute_forces(st, nl, walls, dens)[k]
        F[~st.active[k]] = 0
        if np.abs(F).max() < 0.05:
            return {"pred_freed": False, "t": t}
        st.positions[k] += h * gain * F
        t += h
        out = [i for i in ids if st.active[i] and st.positions[i, 0] > 10.3]
        if item["kind"] == "pair" and out:
            return {"pred_freed": True, "t": t, "first": int(out[0])}
        if item["kind"] == "second_trap":
            if item["focus"] in out:
                return {"pred_freed": True, "t": t, "first": item["focus"]}
            for i in out:
                st.active[i] = False
    return {"pred_freed": None, "t": t, "maxF": float(np.abs(F).max())}


def common_load(S, O, R):
    """Projection of the v = 0 ORCA parts on the pair's softest Hessian mode (E7b_static softest_vec, the
    common lateral shift, sign fixed so that + = shift towards +y), expressed as the equivalent lateral bias
    b_eq = L / L_b with L_b = sum_i c_i e_perp,i . v1_i (the load of the bias per unit b, c_i the SFM drive of
    E7b_static), compared with the static fold threshold b*_s of the same sign (data/E7b_bstar/fold_threshold.jsonl)."""
    V = {json.loads(x)["job_id"]: json.loads(x) for x in open(os.path.join(DATA, "E7b", "e7b_static.jsonl"))}
    B = {}
    for x in open(os.path.join(DATA, "E7b_bstar", "fold_threshold.jsonl")):
        r = json.loads(x)
        B[(r["tag"], r["sign"])] = r["b_star"]
    rel = {(r["tag"], r["arm"]): r for r in (R or [])}
    rows = []
    for tag in sorted({r["tag"] for r in S if r["kind"] == "pair"}):
        d = {r["role"]: r for r in S if r["tag"] == tag and r["solver"] == "rvo2"}
        lo, up = d["lower"], d["upper"]
        v1 = np.array(V[tag]["softest_vec"], float)
        v1 = v1 * np.sign(v1[1] + v1[3])
        c = np.array(V[tag]["drive_c_N"], float)
        ep = [np.array([-np.array(m["e"])[1], np.array(m["e"])[0]]) for m in (lo, up)]
        Lb = float(c[0] * ep[0] @ v1[:2] + c[1] * ep[1] @ v1[2:])
        C = np.r_[lo["cons_N"], up["cons_N"]]
        D = np.r_[np.array(lo["e"]) * lo["drive_mag_N"], np.array(up["e"]) * up["drive_mag_N"]]
        LC, LD = float(C @ v1), float(D @ v1)
        beq = LC / Lb
        sgn = 1 if beq > 0 else -1
        bs = B[(tag, sgn)]
        r = {"tag": tag, "L_cons_N": LC, "L_drive_N": LD, "L_bias_per_b_N": Lb, "b_eq_cons": beq,
             "b_star_same_sign": bs, "cons_exceeds_threshold": bool(abs(beq) > bs),
             "b_eq_drive": LD / Lb, "b_eq_sum": (LC + LD) / Lb,
             "quench_cons_rvo2": O[(tag, "constraint_only_rvo2")], "quench_cons_pub": O[(tag, "constraint_only_pub")],
             "quench_drive": O[(tag, "drive_only")], "quench_c3_rvo2": O[(tag, "C3_rvo2")],
             "quench_c3_pub": O[(tag, "C3_pub")],
             "pred_first_side": "lower" if beq > 0 else "upper"}
        rc = rel.get((tag, "constraint_only_rvo2"))
        if rc and rc.get("first") is not None:
            r["relax_cons_first_side"] = "lower" if rc["first"] == lo["id"] else "upper"
        rows.append(r)
    n = len(rows)
    ex = [r for r in rows if r["cons_exceeds_threshold"]]
    side = [r for r in rows if "relax_cons_first_side" in r]
    return {"rows": rows, "n": n, "cons_exceeds_threshold": len(ex),
            "exceed_and_quench_cons_rvo2_freed": int(sum(r["quench_cons_rvo2"] for r in ex)),
            "not_exceed_quench_cons_rvo2_freed": int(sum(r["quench_cons_rvo2"] for r in rows if not r["cons_exceeds_threshold"])),
            "ratio_beq_over_bstar": summ([abs(r["b_eq_cons"]) / r["b_star_same_sign"] for r in rows]),
            "abs_b_eq_cons": summ([abs(r["b_eq_cons"]) for r in rows]),
            "b_star_same_sign": summ([r["b_star_same_sign"] for r in rows]),
            "abs_b_eq_drive": summ([abs(r["b_eq_drive"]) for r in rows]),
            "first_side_match_relax": int(sum(r["relax_cons_first_side"] == r["pred_first_side"] for r in side)),
            "first_side_n": len(side)}


def jacobian_check(L):
    """Is the v = 0 rest field with ORCA conservative? Jacobian J = -dF0/dx of the code's rest field
    (A10_hessian.RestField, densities and neighbour lists frozen) by central differences (h = 1e-5 m) for C3
    (rvo2) and constraint_only (rvo2) on the 46 pairs and the 26 second traps; asymmetry
    ||J - J^T||_F / ||J||_F (0 for a gradient field) and the smallest eigenvalue of the symmetric part."""
    from A10_hessian import RestField, fd_hessian
    out = {}
    for arm, fl in (("C3_rvo2", {"w2_orca": "rvo2"}), ("constraint_only_rvo2", {"w2_orca": "rvo2", "w2_orca_split": "constraint_only"}),
                    ("drive_only", {"w2_orca_split": "drive_only"})):
        for kind in ("pair", "second_trap"):
            A, M = [], []
            for it in [x for x in L if x["kind"] == kind]:
                rf = RestField(pickle.load(open(it["snap"], "rb")), "C3", {**it["flags"], **fl})
                J = fd_hessian(rf.F, rf.X0, 1e-5)
                A.append(float(np.linalg.norm(J - J.T) / np.linalg.norm(J)))
                M.append(float(np.linalg.eigvalsh(0.5 * (J + J.T))[0]))
            out.setdefault(kind, {})[arm] = {"asym_rel": summ(A), "sym_mu1_N_per_m": summ(M),
                                             "sym_not_pd": int(sum(m <= 0 for m in M))}
    return out


def overlap(R):
    """Per-snapshot cross-tabulation of rest-field relaxation and quench outcomes (pairs and second traps)."""
    o = {}
    by = {(r["tag"], r["arm"]): r for r in R}
    for kind in ("pair", "second_trap"):
        tags = sorted({r["tag"] for r in R if r["kind"] == kind})
        for sv in ("C3_rvo2", "C3_pub"):
            f = lambda t, a, k: (by[(t, a)]["pred_freed"] is True) if k == "relax" else by[(t, a)]["quench_freed"]  # noqa: E731
            o.setdefault(kind, {})[sv] = {
                "drive_freed_full_held_relax": int(sum(f(t, "drive_only", "relax") and not f(t, sv, "relax") for t in tags)),
                "drive_held_full_freed_relax": int(sum(not f(t, "drive_only", "relax") and f(t, sv, "relax") for t in tags)),
                "drive_freed_full_held_quench": int(sum(f(t, "drive_only", "q") and not f(t, sv, "q") for t in tags)),
                "drive_held_full_freed_quench": int(sum(not f(t, "drive_only", "q") and f(t, sv, "q") for t in tags)),
                "quench_discordant_explained_by_relax": int(sum(
                    f(t, "drive_only", "q") and not f(t, sv, "q") and f(t, "drive_only", "relax") and not f(t, sv, "relax")
                    for t in tags)),
                "relax_freed_quench_held": int(sum(f(t, sv, "relax") and not f(t, sv, "q") for t in tags)),
                "relax_held_quench_freed": int(sum(not f(t, sv, "relax") and f(t, sv, "q") for t in tags))}
    return o


def headline(out, S):
    """Flat registry keys."""
    from scipy import stats
    P = [r for r in S if r["kind"] == "pair" and r["solver"] == "rvo2"]
    pr = out["static"]["pair"]["rvo2"]["members"]["all"]
    sb = out["static"]["second_trap"]["rvo2"]["blocker"]
    hb, fb = sb["held_orca"], sb["freed_orca"]
    fp = float(stats.fisher_exact([[hb["binds"], hb["n"] - hb["binds"]], [fb["binds"], fb["n"] - fb["binds"]]])[1])
    sol = max(float(np.max(np.abs(np.array(a["cons_N"]) - np.array(b["cons_N"]))))
              for a in S if a["solver"] == "rvo2"
              for b in S if b["solver"] == "published" and b["tag"] == a["tag"] and b["id"] == a["id"])
    h = {"pair_members": pr["n"], "pair_binds": pr["binds"], "pair_cos_minus_one": int(sum(r["cos_cons_to_partner"] < -0.999999 for r in P)),
         "pair_cons_mag_med": pr["cons_mag_N"]["median"], "pair_cons_mag_min": pr["cons_mag_N"]["min"],
         "pair_cons_mag_max": pr["cons_mag_N"]["max"], "pair_drive_mag_med": pr["drive_mag_N"]["median"],
         "pair_ratio_med": pr["cons_over_drive"]["median"], "pair_ratio_min": pr["cons_over_drive"]["min"],
         "pair_ratio_max": pr["cons_over_drive"]["max"],
         "pair_cons_x_absmax": float(max(abs(r["cons_x_N"]) for r in P)),
         "pair_cons_out_med": -pr["cons_lat_towards_axis_N"]["median"],
         "pair_drive_in_med": pr["drive_axisward_N"]["median"],
         "pair_removed_frac_med": float(np.median([(r["vpref_towards_partner_m_per_s"] - r["slack_m_per_s"])
                                                   / r["vpref_towards_partner_m_per_s"] for r in P])),
         "pair_cap_err_max": pr["cap_prediction_err_N_max"], "solver_diff_max_N": sol,
         "trace_t0_diff_max": out["trace_check"]["max_abs_diff_cons_x_t0_N"],
         "trace_cancel_t0_med": out["trace_check"]["static_cancel_frac_t0"]["median"],
         "trace_cancel_t0_absmax": max(abs(out["trace_check"]["static_cancel_frac_t0"]["min"]),
                                       abs(out["trace_check"]["static_cancel_frac_t0"]["max"])),
         "st_n": sb["all"]["n"], "st_binds": sb["all"]["binds"], "st_held": hb["n"], "st_held_binds": hb["binds"],
         "st_freed": fb["n"], "st_freed_binds": fb["binds"], "st_bind_fisher_p": fp,
         "st_bind_fisher_p_disp": revlib.pdisp(fp),
         "st_held_ratio_med": hb["cons_over_drive"]["median"],
         "st_others_axial_med": out["static"]["second_trap"]["rvo2"]["others"]["all"]["cons_axial_N"]["median"]}
    cl = out["common_load"]
    h.update({"cl_exceeds": cl["cons_exceeds_threshold"], "cl_beq_med": cl["abs_b_eq_cons"]["median"],
              "cl_bstar_med": cl["b_star_same_sign"]["median"], "cl_beq_drive_med": cl["abs_b_eq_drive"]["median"],
              "cl_side_match": cl["first_side_match_relax"], "cl_side_n": cl["first_side_n"]})
    J = out["jacobian"]["pair"]
    h.update({"jac_cons_notpd": J["constraint_only_rvo2"]["sym_not_pd"],
              "jac_cons_mu1_med": J["constraint_only_rvo2"]["sym_mu1_N_per_m"]["median"],
              "jac_c3_mu1_med": J["C3_rvo2"]["sym_mu1_N_per_m"]["median"],
              "jac_c3_mu1_min": J["C3_rvo2"]["sym_mu1_N_per_m"]["min"],
              "jac_c3_notpd": J["C3_rvo2"]["sym_not_pd"],
              "jac_drive_mu1_med": J["drive_only"]["sym_mu1_N_per_m"]["median"],
              "jac_asym_med": J["C3_rvo2"]["asym_rel"]["median"], "jac_asym_min": J["C3_rvo2"]["asym_rel"]["min"],
              "jac_asym_max": J["C3_rvo2"]["asym_rel"]["max"]})
    for kind in ("pair", "second_trap"):
        for arm, v in out.get("relax", {}).get(kind, {}).items():
            h[f"relax_{kind}_{arm}_freed"] = v["pred_freed"]
            h[f"relax_{kind}_{arm}_agree"] = v["agree"]
    if "overlap" in out:
        h["pair_rvo2_relaxfreed_quenchheld"] = out["overlap"]["pair"]["C3_rvo2"]["relax_freed_quench_held"]
        h["pair_rvo2_disc_explained"] = out["overlap"]["pair"]["C3_rvo2"]["quench_discordant_explained_by_relax"]
        h["pair_rvo2_disc"] = out["overlap"]["pair"]["C3_rvo2"]["drive_freed_full_held_quench"]
        h["st_rvo2_disc_explained"] = out["overlap"]["second_trap"]["C3_rvo2"]["quench_discordant_explained_by_relax"]
        h["st_rvo2_disc"] = out["overlap"]["second_trap"]["C3_rvo2"]["drive_freed_full_held_quench"]
    return h


def summ(v):
    v = np.asarray([x for x in v if x is not None], float)
    if not len(v):
        return None
    return {"n": int(len(v)), "min": float(v.min()), "q25": float(np.percentile(v, 25)), "median": float(np.median(v)),
            "q75": float(np.percentile(v, 75)), "max": float(v.max()), "mean": float(v.mean())}


def main(do_relax=True, reuse=False):
    t0 = time.process_time()
    L = library()
    O = outcomes()
    S = []
    for it in L:
        for sv in SOLVERS:
            S.extend(static(it, sv))
    with open(os.path.join(OUTD, "static.jsonl"), "w") as f:
        for r in S:
            f.write(json.dumps(r) + "\n")
    out = {"doc": __doc__, "static": {}, "relax": {}, "trace_check": {}}
    # ---- static summaries
    for kind in ("pair", "second_trap"):
        for sv in SOLVERS:
            rows = [r for r in S if r["kind"] == kind and r["solver"] == sv]
            if kind == "second_trap":
                groups = {"blocker": [r for r in rows if r["role"] == "blocker"],
                          "others": [r for r in rows if r["role"] == "other"]}
            else:
                groups = {"members": rows}
            for gname, G in list(groups.items()):
                for oc_name, oc_arm in (("all", None), ("held_orca", QARM[sv]), ("freed_orca", QARM[sv])):
                    if oc_arm is None:
                        H = G
                    else:
                        want = oc_name == "freed_orca"
                        H = [r for r in G if O[(r["tag"], oc_arm)] == want]
                    key = f"{kind}.{sv}.{gname}.{oc_name}"
                    out["static"].setdefault(kind, {}).setdefault(sv, {}).setdefault(gname, {})[oc_name] = {
                        "n": len(H), "binds": int(sum(r["binds"] for r in H)),
                        "cons_mag_N": summ([r["cons_mag_N"] for r in H]),
                        "cons_axial_N": summ([r["cons_axial_N"] for r in H]),
                        "cons_lat_towards_axis_N": summ([r["cons_lat_towards_axis_N"] for r in H]),
                        "cons_eperp_N": summ([r["cons_eperp_N"] for r in H]),
                        "cons_over_drive": summ([r["cons_over_drive"] for r in H]),
                        "drive_mag_N": summ([r["drive_mag_N"] for r in H]),
                        "drive_axisward_N": summ([r["drive_axisward_N"] for r in H]),
                        "cos_cons_to_partner": summ([r.get("cos_cons_to_partner") for r in H]),
                        "cap_prediction_err_N_max": max([r.get("cap_prediction_err_N", 0.0) for r in H] or [0.0]),
                        "binding_is_partner": int(sum(bool(r.get("binding_is_partner")) for r in H)),
                        "partner_gap_m": summ([r.get("partner_gap_m") for r in H]),
                        "vpref_towards_partner": summ([r.get("vpref_towards_partner_m_per_s") for r in H]),
                        "slack": summ([r.get("slack_m_per_s") for r in H]),
                        "partner_dx_m": summ([r.get("partner_dx_m") for r in H])}
    # per-pair net common lateral load of the constraint part (sum of both members' y components) and opposed load
    for sv in SOLVERS:
        by = {}
        for r in S:
            if r["kind"] == "pair" and r["solver"] == sv:
                by.setdefault(r["tag"], {})[r["role"]] = r
        com, opp = [], []
        for tag, d in by.items():
            lo, up = d["lower"], d["upper"]
            com.append(abs(lo["cons_N"][1] + up["cons_N"][1]))
            opp.append(0.5 * (-lo["cons_N"][1] + up["cons_N"][1]))   # + = members pushed apart
        out["static"]["pair"][sv]["pair_common_lateral_abs_N"] = summ(com)
        out["static"]["pair"][sv]["pair_opposed_lateral_apart_N"] = summ(opp)
    # ---- consistency with the 20 s RVO2 trace at t = 0 (cons_x_t0, unweighted by w_o there; w_o ~ 1)
    T = [json.loads(x) for x in open(os.path.join(DATA, "E7b", "e7b_pair_trace.jsonl"))]
    st_rvo = {(r["tag"], r["role"]): r for r in S if r["kind"] == "pair" and r["solver"] == "rvo2"}
    diffs = [abs(t["cons_x_t0"] - st_rvo[(t["tag"], t["member"])]["cons_x_N"] / st_rvo[(t["tag"], t["member"])]["w_o"])
             for t in T]
    held = [t for t in T if not O[(t["tag"], "C3_rvo2")]]
    out["trace_check"] = {
        "n": len(T), "max_abs_diff_cons_x_t0_N": float(max(diffs)),
        "cons_x_t0": summ([t["cons_x_t0"] for t in T]),
        "cons_x_mean_20s": summ([t["cons_x_mean"] for t in T]),
        "cancel_frac_mean_held": summ([t["cancel_frac_mean"] for t in held]),
        "static_cancel_frac_t0": summ([-t["cons_x_t0"] / st_rvo[(t["tag"], t["member"])]["drive_mag_N"]
                                       * st_rvo[(t["tag"], t["member"])]["w_o"] for t in T])}
    # ---- relaxation of the rest field
    R = None
    if reuse:
        R = [json.loads(x) for x in open(os.path.join(OUTD, "relax.jsonl"))]
    elif do_relax:
        R = []
        for it in L:
            for arm in RELAX_ARMS:
                rr = relax(it, arm)
                rr.update({"tag": it["tag"], "kind": it["kind"], "arm": arm, "quench_freed": O[(it["tag"], arm)]})
                R.append(rr)
            print(it["tag"], " ".join(f"{r['arm']}:{r['pred_freed']}/{r['quench_freed']}" for r in R[-len(RELAX_ARMS):]),
                  flush=True)
        with open(os.path.join(OUTD, "relax.jsonl"), "w") as f:
            for r in R:
                f.write(json.dumps(r) + "\n")
    if R is not None:
        for kind in ("pair", "second_trap"):
            for arm in RELAX_ARMS:
                G = [r for r in R if r["kind"] == kind and r["arm"] == arm]
                out["relax"].setdefault(kind, {})[arm] = {
                    "n": len(G), "pred_freed": int(sum(r["pred_freed"] is True for r in G)),
                    "pred_held": int(sum(r["pred_freed"] is False for r in G)),
                    "undecided": int(sum(r["pred_freed"] is None for r in G)),
                    "quench_freed": int(sum(r["quench_freed"] for r in G)),
                    "agree": int(sum((r["pred_freed"] is True) == r["quench_freed"] for r in G))}
    out["common_load"] = common_load(S, O, R)
    if R is not None:
        out["overlap"] = overlap(R)
    out["jacobian"] = jacobian_check(L)
    out["headline"] = headline(out, S)
    out["cpu_s"] = time.process_time() - t0
    print(revlib.out_json("A11", out), out["cpu_s"])


if __name__ == "__main__":
    main(do_relax="--no-relax" not in sys.argv, reuse="--reuse" in sys.argv)
