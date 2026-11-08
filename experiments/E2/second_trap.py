"""Second-trap diagnosis: ORCA's force on the blocker at restart, split into drive and constraint parts.

For each of the 60 E2 snapshots (data/derived/selection.json), the snapshot is restored under C3 with the
corrected-forward flags and w2_orca in {rvo2, published} (CF union arm flags), and at t = 0 (no step taken)
the blocker's ORCA velocity is computed exactly as in sim/steering/orca.py (_velocity_rvo2 /
_velocity_published), with the neighbour lists and grid density of Simulation.step (KDTree radius 3 m among
active agents; density = count / (pi 3^2)). The force splits by the identity
    m (v_ORCA - v) / tau_ORCA = m (v_pref - v) / tau_ORCA  [drive]  +  m (v_ORCA - v_pref) / tau_ORCA  [constraint],
v_pref = v0 * (goal - x) / |goal - x|, tau_ORCA = 0.5 s. Components: door-ward (+x) and lateral (toward the door
axis y = 5 positive). The density fade w_ORCA = 1 - sigmoid(rho; 4, 2) that multiplies the ORCA force in the
hybrid sum is recorded and applied in the *_weighted fields.
Binding neighbour: the neighbour whose removal from the blocker's neighbour list changes the door-ward ORCA
velocity most (leave-one-out); its half-plane's contribution to the door-ward force is
    dFx_j = m (v_ORCA,x - v_ORCA,x without j) / tau_ORCA  (negative = the half-plane against j holds the blocker back).
"Trapped neighbour" = another residual agent of the snapshot (all residual agents are trapped at rest).
Cancellation fraction = -Fx_constraint / Fx_drive (1 = the constraint part cancels the whole door-ward drive).
Outcomes come from data/E2/e2_quench.jsonl (unperturbed runs): blocker freed within 120 s and its time.
Trace (second-trap stratum, C3 RVO2 only): at restart the blocker is at rest and the constraint part is
nearly zero, so the run is integrated for T_TRACE = 20 s (dt = 0.01 s, or until the blocker exits) and at
every step the same split is computed on the blocker, together with the door-ward force of the half-planes
of all trapped neighbours (v_ORCA with and without them) and the leave-one-out binding neighbour at the step
of strongest cancellation. Summaries: time-mean and extreme door-ward constraint force, time-mean
cancellation fraction, fraction of steps with cancellation > 0.5, blocker displacement along +x.
Output: data/derived/E2_second_trap.json.
"""
import json
import math
import os
import pickle
import sys

import numpy as np
from scipy import stats
from scipy.spatial import KDTree

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, ROOT  # noqa: E402
from w2lib import restore  # noqa: E402
from sim.core.helpers import safe_normalize  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "E3"))
from survival import km  # noqa: E402

OUT = os.path.join(DATA, "derived", "E2_second_trap.json")
QUENCH = os.path.join(DATA, "E2", "e2_quench.jsonl")
VARIANTS = ("rvo2", "published")
STRATA = ("lone_keystone", "lone_keystone_second_trap")
T_Q = 120.0
T_TRACE = 20.0


def neighbours(st, r=3.0):
    a = st.active_indices
    tree = KDTree(st.positions[a])
    nl = [[] for _ in range(st.n)]
    for li, nb in enumerate(tree.query_ball_point(st.positions[a], r=r)):
        nl[a[li]] = [int(a[j]) for j in nb if a[j] != a[li]]
    return nl, np.array([len(n) / (math.pi * r * r) for n in nl])


def v_orca(orca, variant, i, st, nl, v_pref, vmax):
    f = orca._velocity_rvo2 if variant == "rvo2" else orca._velocity_published
    return np.asarray(f(i, st, nl, v_pref, vmax), float)


def decompose(snap_path, b, variant):
    snap = pickle.load(open(snap_path, "rb"))
    sim = restore(snap, "C3", flags={**CF, "w2_orca": variant})
    st = sim.state
    orca = sim.steering.orca
    p = sim.steering.params
    nl, rho = neighbours(st)
    w = 1.0 - 1.0 / (1.0 + math.exp(-p.get("k_orca_fade", 2.0) * (rho[b] - p.get("rho_orca_fade", 4.0))))
    x, v, m = st.positions[b], st.velocities[b], float(st.masses[b])
    e = safe_normalize(st.goals[b] - x)
    v_pref = float(st.desired_speeds[b]) * e
    vmax = 2.0 * float(st.desired_speeds[b])
    vo = v_orca(orca, variant, b, st, nl, v_pref, vmax)
    tau = orca.tau_orca
    drive = m * (v_pref - v) / tau
    cons = m * (vo - v_pref) / tau
    lat_sign = -1.0 if x[1] > 5.0 else 1.0
    resid = [int(i) for i in st.active_indices if i != b]
    loo = {}
    for j in nl[b]:
        nl2 = list(nl)
        nl2[b] = [k for k in nl[b] if k != j]
        vj = v_orca(orca, variant, b, st, nl2, v_pref, vmax)
        loo[j] = {"dFx": m * (vo[0] - vj[0]) / tau, "dFlat": lat_sign * m * (vo[1] - vj[1]) / tau,
                  "dist": float(np.linalg.norm(st.positions[j] - x)), "residual": j in resid}
    bind = min(loo, key=lambda j: loo[j]["dFx"]) if loo else None
    # all trapped neighbours removed at once
    nl3 = list(nl)
    nl3[b] = [k for k in nl[b] if k not in resid]
    v3 = v_orca(orca, variant, b, st, nl3, v_pref, vmax)
    comp = lambda F: {"x": float(F[0]), "lat": float(lat_sign * F[1])}  # noqa: E731
    return {"w_orca": w, "rho": float(rho[b]), "speed": float(np.linalg.norm(v)), "pos": x.tolist(),
            "v_pref": v_pref.tolist(), "v_orca": vo.tolist(),
            "drive": comp(drive), "constraint": comp(cons), "total": comp(drive + cons),
            "total_weighted": comp(w * (drive + cons)),
            "cancel_frac": float(-cons[0] / drive[0]) if abs(drive[0]) > 1e-9 else None,
            "n_neighbours": len(nl[b]), "n_trapped_neighbours": len(resid),
            "binding": ({"id": int(bind), **loo[bind]} if bind is not None else None),
            "no_trapped_total_x": float(m * (v3[0] - v[0]) / tau),
            "trapped_halfplanes_dFx": float(m * (vo[0] - v3[0]) / tau)}


def split_at(sim, b, variant, loo=False):
    st = sim.state
    orca = sim.steering.orca
    nl, _ = neighbours(st)
    x, v, m = st.positions[b], st.velocities[b], float(st.masses[b])
    v_pref = float(st.desired_speeds[b]) * safe_normalize(st.goals[b] - x)
    vmax = 2.0 * float(st.desired_speeds[b])
    vo = v_orca(orca, variant, b, st, nl, v_pref, vmax)
    tau = orca.tau_orca
    resid = [int(i) for i in st.active_indices if i != b]
    nl3 = list(nl)
    nl3[b] = [k for k in nl[b] if k not in resid]
    v3 = v_orca(orca, variant, b, st, nl3, v_pref, vmax)
    r = {"drive_x": m * (v_pref[0] - v[0]) / tau, "cons_x": m * (vo[0] - v_pref[0]) / tau,
         "trapped_dFx": m * (vo[0] - v3[0]) / tau, "vx": float(v[0])}
    if loo:
        best = None
        for j in nl[b]:
            nl2 = list(nl)
            nl2[b] = [k for k in nl[b] if k != j]
            d = m * (vo[0] - v_orca(orca, variant, b, st, nl2, v_pref, vmax)[0]) / tau
            if best is None or d < best[1]:
                best = (int(j), float(d), j in resid, float(np.linalg.norm(st.positions[j] - x)),
                        float(st.positions[j, 0] - x[0]))
        r["binding"] = None if best is None else {"id": best[0], "dFx": best[1], "residual": best[2],
                                                  "dist": best[3], "dx_ahead": best[4]}
    return r


def trace(snap_path, b, variant="rvo2", t_max=T_TRACE):
    snap = pickle.load(open(snap_path, "rb"))
    sim = restore(snap, "C3", flags={**CF, "w2_orca": variant})
    x0 = float(sim.state.positions[b, 0])
    T = []
    for _ in range(int(round(t_max / sim.params["dt"]))):
        T.append(split_at(sim, b, variant))
        sim.step()
        if not sim.state.active[b] or sim.state.positions[b, 0] >= 10.0:
            break
    dr = np.array([t["drive_x"] for t in T])
    co = np.array([t["cons_x"] for t in T])
    tr = np.array([t["trapped_dFx"] for t in T])
    cf = np.where(np.abs(dr) > 1e-6, -co / np.where(np.abs(dr) > 1e-6, dr, 1.0), 0.0)
    k = int(np.argmin(co))
    dxb = float(sim.state.positions[b, 0] - x0)
    # binding neighbour at the step of strongest cancellation (replay to that step)
    sim = restore(snap, "C3", flags={**CF, "w2_orca": variant})
    for _ in range(k):
        sim.step()
    bnd = split_at(sim, b, variant, loo=True)["binding"]
    return {"steps": len(T), "exited": len(T) < int(round(t_max / 0.01)),
            "cons_x_mean": float(co.mean()), "cons_x_min": float(co.min()), "t_cons_min": k * 0.01,
            "drive_x_mean": float(dr.mean()), "trapped_dFx_mean": float(tr.mean()),
            "trapped_share_of_cons": float(tr.sum() / co.sum()) if abs(co.sum()) > 1e-9 else None,
            "cancel_frac_mean": float(cf.mean()), "frac_steps_cancel_gt_half": float((cf > 0.5).mean()),
            "dx_blocker": dxb,
            "binding_at_min": bnd}


def outcomes(sel):
    O = {}
    blk = {s["tag"]: s["blocker"] for s in sel}
    for ln in open(QUENCH):
        r = json.loads(ln)
        if r.get("perturb") is not None or r["arm"] not in ("C3_rvo2", "C3_pub", "drive_only"):
            continue
        tag = r["job_id"].split("|")[0]
        t = r["exits"].get(str(blk[tag]))
        O.setdefault(tag, {})[r["arm"]] = {"freed": t is not None and t <= T_Q, "t": t}
    return O


def summarise(rows, key_fn):
    a = np.array([key_fn(r) for r in rows if key_fn(r) is not None], float)
    return {"n": len(a), "median": float(np.median(a)) if len(a) else None,
            "q25": float(np.percentile(a, 25)) if len(a) else None, "q75": float(np.percentile(a, 75)) if len(a) else None}


def main():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))["E2"]["snapshots"]
    O = outcomes(sel)
    rows = []
    for s in sel:
        r = {"tag": s["tag"], "class": s["class"], "blocker": s["blocker"], "outcome": O[s["tag"]]}
        for var in VARIANTS:
            r[var] = decompose(os.path.join(ROOT, s["snap"]), s["blocker"], var)
        if s["class"] == STRATA[1]:
            r["trace_rvo2"] = trace(os.path.join(ROOT, s["snap"]), s["blocker"])
            r["trace_published"] = trace(os.path.join(ROOT, s["snap"]), s["blocker"], "published")
        rows.append(r)
        print(s["tag"], s["class"][:22], "rvo2 Fx drive %.1f cons %.1f binding %s (dFx %.1f, trapped %s) freed %s | pub cons %.1f" % (
            r["rvo2"]["drive"]["x"], r["rvo2"]["constraint"]["x"],
            r["rvo2"]["binding"]["id"] if r["rvo2"]["binding"] else None,
            r["rvo2"]["binding"]["dFx"] if r["rvo2"]["binding"] else float("nan"),
            r["rvo2"]["binding"]["residual"] if r["rvo2"]["binding"] else None,
            r["outcome"]["C3_rvo2"]["freed"], r["published"]["constraint"]["x"]), flush=True)
    out = {"n": len(rows), "rows": rows, "strata": {}}
    for st in STRATA:
        R = [r for r in rows if r["class"] == st]
        d = {"n": len(R)}
        for var in VARIANTS:
            arm = "C3_rvo2" if var == "rvo2" else "C3_pub"
            g = {}
            for lab, sub in (("freed", [r for r in R if r["outcome"][arm]["freed"]]),
                             ("held", [r for r in R if not r["outcome"][arm]["freed"]])):
                g[lab] = {"n": len(sub),
                          "drive_x": summarise(sub, lambda r: r[var]["drive"]["x"]),
                          "constraint_x": summarise(sub, lambda r: r[var]["constraint"]["x"]),
                          "total_x": summarise(sub, lambda r: r[var]["total"]["x"]),
                          "total_lat": summarise(sub, lambda r: r[var]["total"]["lat"]),
                          "cancel_frac": summarise(sub, lambda r: r[var]["cancel_frac"]),
                          "trapped_halfplanes_dFx": summarise(sub, lambda r: r[var]["trapped_halfplanes_dFx"]),
                          "binding_is_trapped": sum(1 for r in sub if r[var]["binding"] and r[var]["binding"]["residual"]
                                                    and r[var]["binding"]["dFx"] < -1e-6)}
            fx_f = [r[var]["total"]["x"] for r in R if r["outcome"][arm]["freed"]]
            fx_h = [r[var]["total"]["x"] for r in R if not r["outcome"][arm]["freed"]]
            if fx_f and fx_h:
                u = stats.mannwhitneyu(fx_f, fx_h, alternative="two-sided")
                g["total_x_auc_freed_vs_held"] = float(u.statistic / (len(fx_f) * len(fx_h)))
                g["total_x_mwu_p"] = float(u.pvalue)
            g["constraint_against_drive"] = sum(1 for r in R if r[var]["constraint"]["x"] < -1e-6)
            g["trapped_halfplane_holds_back"] = sum(1 for r in R if r[var]["trapped_halfplanes_dFx"] < -1e-6)
            d[var] = g
        # time to free: drive only vs C3 (unperturbed runs), Kaplan-Meier and paired
        tt = {}
        for arm in ("drive_only", "C3_rvo2", "C3_pub"):
            t = [r["outcome"][arm]["t"] if r["outcome"][arm]["freed"] else T_Q for r in R]
            e = [r["outcome"][arm]["freed"] for r in R]
            k = km(t, e, T_Q)
            tt[arm] = {"freed": int(sum(e)), "n": len(R), "km_median": k["median"],
                       "t_freed": summarise([r for r in R if r["outcome"][arm]["freed"]], lambda r, a=arm: r["outcome"][a]["t"])}
        both = [r for r in R if r["outcome"]["drive_only"]["freed"] and r["outcome"]["C3_rvo2"]["freed"]]
        if both:
            dif = [r["outcome"]["C3_rvo2"]["t"] - r["outcome"]["drive_only"]["t"] for r in both]
            tt["paired_C3rvo2_minus_drive"] = {"n": len(both), "median_s": float(np.median(dif)),
                                               "C3_slower": sum(1 for x in dif if x > 0.005),
                                               "equal": sum(1 for x in dif if abs(x) <= 0.005)}
        d["time_to_free"] = tt
        if st == STRATA[1]:
            nt = lambda r: r["rvo2"]["n_trapped_neighbours"]  # noqa: E731
            tab = [[sum(1 for r in R if nt(r) == 1 and r["outcome"]["C3_rvo2"]["freed"] == f) for f in (True, False)],
                   [sum(1 for r in R if nt(r) >= 2 and r["outcome"]["C3_rvo2"]["freed"] == f) for f in (True, False)]]
            d["pair_vs_cluster"] = {"rows": ["one trapped neighbour", ">= 2 trapped neighbours"],
                                    "cols": ["C3 RVO2 freed", "held"], "table": tab,
                                    "fisher_p": float(stats.fisher_exact(tab)[1])}
            tr = {}
            for var in VARIANTS:
                arm = "C3_rvo2" if var == "rvo2" else "C3_pub"
                tv = {}
                for lab, f in (("freed", True), ("held", False)):
                    sub = [r for r in R if r["outcome"][arm]["freed"] == f]
                    key = "trace_" + var
                    tv[lab] = {"n": len(sub),
                               "cons_x_mean": summarise(sub, lambda r: r[key]["cons_x_mean"]),
                               "cons_x_min": summarise(sub, lambda r: r[key]["cons_x_min"]),
                               "cancel_frac_mean": summarise(sub, lambda r: r[key]["cancel_frac_mean"]),
                               "frac_steps_cancel_gt_half": summarise(sub, lambda r: r[key]["frac_steps_cancel_gt_half"]),
                               "trapped_share_of_cons": summarise(sub, lambda r: r[key]["trapped_share_of_cons"]),
                               "binding_trapped": sum(1 for r in sub if r[key]["binding_at_min"]
                                                      and r[key]["binding_at_min"]["residual"]),
                               "binding_ahead": sum(1 for r in sub if r[key]["binding_at_min"]
                                                    and r[key]["binding_at_min"]["dx_ahead"] > 0)}
                tr[var] = tv
            d["trace"] = tr
        out["strata"][st] = d
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    st2 = out["strata"][STRATA[1]]
    print(json.dumps({"pair_vs_cluster": st2["pair_vs_cluster"], "trace": st2["trace"], "time_to_free": st2["time_to_free"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
