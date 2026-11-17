"""Task 9: pre-registered prediction for the replace couplings R1 and R2 at the 34 lone keystones and 26 second traps of
the screening set (data/derived/selection.json E2). Computed before any R1/R2 run; no dynamics of the snapshots is run.

Rest drive of the blocker at rest on the door axis (the stuck-alone convention of the paper: Eq. stuck, Passability,
density rho = 0 so v_eff = v0 and the ORCA gate chi = w_o(0) = 1 - 1/(1 + e^8) = 0.99966):
  SFM  D_S  = m v_eff / tau
  R1   D_1  = (1 - chi) m v_eff / tau + chi m v_eff / tau_orca          (v_orca = v_pref = v_eff e alone)
  R2   D_2  = (1 - chi) m v_eff / tau + chi m v0 / tau_orca
  margin g_max(r) - D (g_max from the E1 library: margin_C1 + m v0 / tau, i.e. Passability.gmax(r)).
Prediction rule (primary): blocker freed within 120 s iff margin < 0.
Diagnostics stated in advance (not part of the primary rule):
  (a) snapshot density rho_s (agents within 3 m / (pi 9 m^2)) and the margins with v_eff(rho_s), chi(rho_s);
  (b) constraint part at rest: the RVO2 velocity v_orca at the snapshot (all residual agents, their snapshot
      velocities) for v_pref = v_eff e (R1) and v0 e (R2); axial rest drive with it,
      D_c = (1 - chi) m v_eff e.x / tau + chi m v_orca.x / tau_orca, and its margin g_max - D_c;
  (c) run-up: 1-D on-axis motion from the SFM rest point (first x where the backward wall force equals D_S) under
      D_R with damping m v (chi / tau_orca + (1 - chi) / tau), wall force of the code (convex_union corner rule),
      dt 1e-3 s, 30 s; freed if x passes the force peak.
Output: data/derived/rev7_T9_prereg.json
"""
import json
import math
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import np  # noqa: E402
from w2lib import restore, wall_backward_profile  # noqa: E402
from sim.steering.orca import ORCAModel  # noqa: E402
from sim.steering.walls import WallForces  # noqa: E402
from sim.scenarios.bottleneck import BottleneckScenario  # noqa: E402
from sim.core.agent import AgentState  # noqa: E402

M, TAU_O = 80.0, 0.5
CHI0 = 1.0 - 1.0 / (1.0 + math.exp(-2.0 * (0.0 - 4.0)))


def weid(rho):
    rho = max(rho, 0.01)
    return float(np.clip(1.0 - np.exp(-1.913 * (1.0 / rho - 1.0 / 5.4)), 0.05, 1.0))


def chi(rho):
    return 1.0 - 1.0 / (1.0 + math.exp(-2.0 * (rho - 4.0)))


def drives(v0, tau, W, c):
    ve = W * v0
    return {"SFM": M * ve / tau, "R1": (1 - c) * M * ve / tau + c * M * ve / TAU_O,
            "R2": (1 - c) * M * ve / tau + c * M * v0 / TAU_O}


_PROF = {}


def axis_profile(r):
    """x grid and backward force -F_x of the code's wall force (convex_union) on the door axis, v = 0."""
    if r not in _PROF:
        sc = BottleneckScenario(1, 0.8)
        world, _ = sc.build(seed=0)
        xs = np.linspace(8.5, 10.6, 4201)
        n = len(xs)
        st = AgentState(np.column_stack([xs, np.full(n, 5.0)]), np.zeros((n, 2)), np.tile([11.0, 5.0], (n, 1)),
                        np.full(n, r), np.ones(n), np.full(n, 80.0), np.full(n, 0.5), np.ones(n, bool))
        F = WallForces(corner="convex_union").compute_wall_forces(st, world.walls)
        _PROF[r] = (xs, -F[:, 0])
    return _PROF[r]


def runup(r, D_s, D_r, damp):
    xs, g = axis_profile(r)
    ip = int(np.argmax(g))
    if g[ip] <= D_s:
        return {"x_rest": None, "freed": True, "x_max": None}
    i0 = int(np.argmax(g[:ip + 1] >= D_s))  # first crossing upstream of the peak
    x, v, dt = float(xs[i0]), 0.0, 1e-3
    xmax = x
    for _ in range(30000):
        f = D_r - float(np.interp(x, xs, g)) - M * damp * v
        v += f / M * dt
        x += v * dt
        xmax = max(xmax, x)
        if x > xs[ip] + 0.05:
            return {"x_rest": float(xs[i0]), "x_peak": float(xs[ip]), "freed": True, "x_max": xmax}
    return {"x_rest": float(xs[i0]), "x_peak": float(xs[ip]), "freed": False, "x_max": xmax}


def main():
    sel = json.load(open(os.path.join(L.DERIVED, "selection.json")))["E2"]["snapshots"]
    e1 = {}
    for r in L.load_runs(os.path.join(L.DATA, "E1", "E1_runs.jsonl")):
        if r["mode"] == "E1b":
            e1[r["seed"]] = r
    orca = ORCAModel(time_horizon=5.0, tau_orca=TAU_O, dt=0.01, variant="rvo2")
    rows = []
    for s in sel:
        a = e1[s["seed"]]["attrs"][s["blocker"]]
        v0, tau, r = a["v0"], a["tau"], a["r"]
        gmax = a["margin_C1"] + M * v0 / tau
        D0 = drives(v0, tau, 1.0, CHI0)
        row = {"tag": s["tag"], "class": s["class"], "blocker": s["blocker"], "r": r, "v0": v0, "tau": tau,
               "g_max": gmax, "margin_C1_lib": a["margin_C1"], "margin_C3_lib": a["margin_C3"],
               "drive": D0, "margin": {k: gmax - d for k, d in D0.items()},
               "pred_freed": {k: bool(gmax - D0[k] < 0) for k in ("R1", "R2")}}
        snap = pickle.load(open(os.path.join(L.ROOT, s["snap"]), "rb"))
        st = snap["state"]
        b = s["blocker"]
        act = [int(i) for i in st.active_indices]
        nb = [j for j in act if j != b and np.linalg.norm(st.positions[j] - st.positions[b]) <= 3.0]
        rho = len(nb) / (math.pi * 9.0)
        W, c = weid(rho), chi(rho)
        Ds = drives(v0, tau, W, c)
        e = st.goals[b] - st.positions[b]
        e = e / np.linalg.norm(e)
        lp = {}
        for k, pref in (("R1", W * v0), ("R2", v0)):
            # neighbour list indexed per agent; only the blocker's entry is used
            nl = [[] for _ in range(st.n)]
            nl[b] = nb
            vo = orca._velocity_rvo2(b, st, nl, pref * e, 2.0 * v0)
            Dc = (1 - c) * M * W * v0 * e[0] / tau + c * M * float(vo[0]) / TAU_O
            lp[k] = {"v_orca": vo.tolist(), "v_pref": (pref * e).tolist(), "D_axial": Dc, "margin": gmax - Dc,
                     "constraint_axial_N": c * M * float(vo[0] - pref * e[0]) / TAU_O,
                     "constraint_lateral_N": c * M * float(vo[1] - pref * e[1]) / TAU_O}
        row.update({"rho_snap": rho, "n_nb_3m": len(nb), "W_snap": W, "chi_snap": c, "drive_snap": Ds,
                    "margin_snap": {k: gmax - d for k, d in Ds.items()}, "lp_rest": lp,
                    "blocker_pos": st.positions[b].tolist()})
        ru = {}
        for k in ("R1", "R2"):
            ru[k] = runup(round(r, 6), D0["SFM"], D0[k], CHI0 / TAU_O + (1 - CHI0) / tau)
        row["runup"] = ru
        rows.append(row)
    out = {"doc": __doc__, "chi0": CHI0, "rows": rows, "pred": {}}
    for cls in ("lone_keystone", "lone_keystone_second_trap"):
        sub = [x for x in rows if x["class"] == cls]
        out["pred"][cls] = {"n": len(sub)}
        for k in ("R1", "R2"):
            out["pred"][cls][k] = {
                "static_freed": int(sum(x["pred_freed"][k] for x in sub)),
                "static_freed_tags": [x["tag"] for x in sub if x["pred_freed"][k]],
                "snapdensity_freed": sum(x["margin_snap"][k] < 0 for x in sub),
                "lp_rest_freed": sum(x["lp_rest"][k]["margin"] < 0 for x in sub),
                "runup_freed": sum(x["runup"][k]["freed"] for x in sub),
                "runup_extra_tags": [x["tag"] for x in sub if x["runup"][k]["freed"] and not x["pred_freed"][k]],
                "lp_flip_tags": [x["tag"] for x in sub if (x["lp_rest"][k]["margin"] < 0) != x["pred_freed"][k]]}
        out["pred"][cls]["SFM_static_freed"] = sum(x["margin"]["SFM"] < 0 for x in sub)
    print(json.dumps(out["pred"], indent=1, default=int))
    print(L.out_json("T9_prereg", out))


if __name__ == "__main__":
    main()
