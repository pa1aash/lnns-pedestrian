"""A10: full-space Hessians of the rest-state potential U at the 60 E2 lone-trap snapshots.

Inputs: data/derived/selection.json ("E2": 34 lone keystones + 26 second-trap snapshots, blocker per
snapshot), snapshots data/E1/library/<tag>.pkl. No dynamics is run.

Rest field. Each snapshot is restored under config C1 with the corrected-forward flags CF
(w2lib.restore, as every E2 quench). The rest field is the code's own force at zero velocity,
F0(x) = HybridSteeringModel.compute_forces(state with v = 0, x), on all residual (active) agents, with the
neighbour lists (KD-tree radius 3 m) and the grid densities (count / 9 pi) frozen at their snapshot
values, and helpers.CLIP_MODE = "none" as set by Simulation.step under w2_numerics = "fixed". With the
densities frozen F0 = -grad U, U of Eq. (U) in 04_protocol.tex.

Hessian. H = -dF0/dx in all 2n residual-agent coordinates by central differences of F0,
H[:, k] = -(F0(x + h e_k) - F0(x - h e_k)) / 2h, at h = 1e-5 m (reported) and h = 5e-6 m (step check:
max |H_h - H_h/2| / max |H|). Asymmetry ||H - H^T||_F / ||H||_F is reported before symmetrising
H_s = (H + H^T)/2. Cross-check: the Hessian of the independently coded potential U of
experiments/BAR/bar.py (Field, all agents mobile, snapshot densities; central second differences of U,
h = 1e-4 m), max |H_s - H_U| / max |H_s|.

Per snapshot: residual max |F0| at the snapshot (rest-state tolerance), eigenvalues of H_s (ascending),
strict minimum (all eigenvalues > 0), softest eigenvector: weight of each agent p_a = |e_a|^2, the
blocker's weight, the agent carrying the largest weight, participation ratio 1 / sum p_a^2, and the
blocker's axial (x) / lateral (y) share of its own component. Blocker-only 2x2 block of H_s (the
"blocker alone with neighbours frozen" stiffness) for comparison with the full softest eigenvalue.
Output: data/derived/rev_A10.json.
"""
import copy
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import CF, DERIVED, ROOT, np  # noqa: E402
import json  # noqa: E402
from w2lib import restore  # noqa: E402
from sim.core import helpers as _helpers  # noqa: E402
import bar  # noqa: E402

H1, H2 = 1e-5, 5e-6


class RestField:
    """F0(x) of the code (C1, CF), densities and neighbour lists frozen at the snapshot."""

    def __init__(self, snap, config="C1", flags=None):
        self.sim = restore(snap, config, flags={**CF, **(flags or {})})
        _helpers.CLIP_MODE = "none"
        self.st = copy.deepcopy(self.sim.state)
        self.st.velocities[:] = 0.0
        self.ids = [int(i) for i in self.st.active_indices]
        P = self.st.positions
        self.nl = [[] for _ in range(self.st.n)]
        for i in self.ids:
            self.nl[i] = [j for j in self.ids if j != i and np.linalg.norm(P[j] - P[i]) <= 3.0]
        self.dens = np.array([len(n) / (np.pi * 9.0) for n in self.nl])
        self.X0 = P[self.ids].ravel().copy()

    def F(self, X):
        self.st.positions[self.ids] = X.reshape(-1, 2)
        f = self.sim.steering.compute_forces(self.st, self.nl, self.sim.world.walls, self.dens)[self.ids]
        self.st.positions[self.ids] = self.X0.reshape(-1, 2)
        return f.ravel()


def fd_hessian(F, X, h):
    n = len(X)
    H = np.zeros((n, n))
    for k in range(n):
        e = np.zeros(n); e[k] = h
        H[:, k] = -(F(X + e) - F(X - e)) / (2 * h)
    return H


def u_hessian(f, X, h=1e-4):
    n = len(X)
    H = np.zeros((n, n))
    E = np.eye(n) * h
    for i in range(n):
        for j in range(i, n):
            H[i, j] = H[j, i] = (f.U(X + E[i] + E[j]) - f.U(X + E[i] - E[j]) - f.U(X - E[i] + E[j])
                                 + f.U(X - E[i] - E[j])) / (4 * h * h)
    return H


def analyse(s):
    snap = pickle.load(open(os.path.join(ROOT, s["snap"]), "rb"))
    rf = RestField(snap)
    ids, X = rf.ids, rf.X0
    b = int(s["blocker"])
    ib = ids.index(b)
    F0 = rf.F(X)
    Ha, Hb = fd_hessian(rf.F, X, H1), fd_hessian(rf.F, X, H2)
    scale = float(np.max(np.abs(Ha)))
    asym = float(np.linalg.norm(Ha - Ha.T) / np.linalg.norm(Ha))
    Hs = 0.5 * (Ha + Ha.T)
    ev, V = np.linalg.eigh(Hs)
    # independent potential (bar.Field) cross-check, agents in rf.ids order
    fld = bar.Field(snap, ids, [])
    HU = u_hessian(fld, X)
    v1 = V[:, 0]
    p = (v1.reshape(-1, 2) ** 2).sum(1)
    top = int(np.argmax(p))
    eb = v1.reshape(-1, 2)[ib]
    Bk = Hs[2 * ib:2 * ib + 2, 2 * ib:2 * ib + 2]
    evb = np.linalg.eigvalsh(Bk)
    P = X.reshape(-1, 2)
    E1 = v1.reshape(-1, 2)
    lat_share = float(np.sum(E1[:, 1] ** 2))
    order = np.argsort(-p)
    if len(ids) > 1:
        a1, a2 = order[0], order[1]
        cos12 = float(E1[a1] @ E1[a2] / (np.linalg.norm(E1[a1]) * np.linalg.norm(E1[a2])))
        second = ids[a2]
    else:
        cos12, second = None, None
    if len(ids) == 1:
        mtype = "lateral" if lat_share > 0.5 else "axial"
    elif lat_share > 0.5 and cos12 is not None and p[order[1]] > 0.2:
        mtype = "common_lateral" if cos12 > 0 else "opposed_lateral"
    else:
        mtype = ("lateral_" if lat_share > 0.5 else "axial_") + ("one_agent" if p[order[0]] > 0.8 else "shared")
    row = {"tag": s["tag"], "stratum": s["class"], "n_resid": len(ids), "ids": ids, "blocker": b,
           "pos": P.tolist(),
           "resid_F0_max_N": float(np.max(np.abs(F0))),
           "resid_F0_per_agent_N": np.linalg.norm(F0.reshape(-1, 2), axis=1).tolist(),
           "snapshot_max_speed": float(np.linalg.norm(snap["state"].velocities[ids], axis=1).max()),
           "fd_step_rel_change": float(np.max(np.abs(Ha - Hb)) / scale),
           "asym_rel_frobenius": asym, "asym_max_abs_N_per_m": float(np.max(np.abs(Ha - Ha.T))),
           "bar_U_rel_diff": float(np.max(np.abs(Hs - HU)) / scale),
           "eig_N_per_m": ev.tolist(), "mu1": float(ev[0]), "mu2": float(ev[1]) if len(ev) > 1 else None,
           "strict_min": bool(ev[0] > 0),
           "soft_weights": p.tolist(), "soft_blocker_weight": float(p[ib]), "soft_top_agent": ids[top],
           "soft_top_is_blocker": bool(top == ib), "soft_pr": float(1 / np.sum(p ** 2)),
           "soft_top_agent_dir": (v1.reshape(-1, 2)[top] / np.linalg.norm(v1.reshape(-1, 2)[top])).tolist(),
           "soft_top_agent_pos": P[top].tolist(),
           "soft_blocker_lateral_share": float(eb[1] ** 2 / max(eb @ eb, 1e-300)),
           "blocker_block_eig_N_per_m": evb.tolist(),
           "soft_lateral_share": lat_share, "soft_second_agent": second, "soft_cos_top2": cos12,
           "soft_type": mtype}
    return row


def summ(v):
    v = np.asarray(v, float)
    return {"n": int(len(v)), "min": float(v.min()), "median": float(np.median(v)), "max": float(v.max())}


def main():
    t0 = time.process_time()
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]
    rows = []
    for s in sel:
        r = analyse(s)
        rows.append(r)
        print(f"{r['tag']:14s} {r['stratum'][:14]:14s} n={r['n_resid']} |F0|={r['resid_F0_max_N']:.1e} "
              f"mu1={r['mu1']:8.2f} pb={r['soft_blocker_weight']:.2f} top={r['soft_top_agent']} "
              f"asym={r['asym_rel_frobenius']:.1e} fd={r['fd_step_rel_change']:.1e} U={r['bar_U_rel_diff']:.1e}",
              flush=True)
    out = {"doc": __doc__, "n": len(rows), "fd_h_m": H1, "fd_h_check_m": H2, "rows": rows, "strata": {}}
    for name, sub in (("all", rows), ("lone_keystone", [r for r in rows if r["stratum"] == "lone_keystone"]),
                      ("second_trap", [r for r in rows if r["stratum"] == "lone_keystone_second_trap"])):
        mu1 = [r["mu1"] for r in sub]
        out["strata"][name] = {
            "n": len(sub), "strict_min": int(sum(r["strict_min"] for r in sub)),
            "mu1": summ(mu1), "mu1_sig": {k: revlib.sig(v, 2) for k, v in summ(mu1).items() if k != "n"},
            "soft_on_blocker": int(sum(r["soft_top_is_blocker"] for r in sub)),
            "soft_blocker_weight": summ([r["soft_blocker_weight"] for r in sub]),
            "soft_pr": summ([r["soft_pr"] for r in sub]),
            "soft_blocker_lateral_share": summ([r["soft_blocker_lateral_share"] for r in sub
                                                if r["soft_top_is_blocker"]] or [np.nan]),
            "resid_F0_max_N": float(max(r["resid_F0_max_N"] for r in sub)),
            "asym_rel_max": float(max(r["asym_rel_frobenius"] for r in sub)),
            "fd_step_rel_max": float(max(r["fd_step_rel_change"] for r in sub)),
            "bar_U_rel_max": float(max(r["bar_U_rel_diff"] for r in sub)),
            "soft_type_counts": {t: sum(r["soft_type"] == t for r in sub) for t in sorted({r["soft_type"] for r in sub})},
            "multi_agent_n": int(sum(r["n_resid"] > 1 for r in sub)),
            "multi_soft_on_blocker": int(sum(r["soft_top_is_blocker"] for r in sub if r["n_resid"] > 1)),
        }
    out["not_strict"] = [r["tag"] for r in rows if not r["strict_min"]]
    ab = [r for r in rows if r["stratum"] == "lone_keystone_second_trap" and r["n_resid"] == 2
          and r["soft_type"] == "common_lateral"]
    one = [r for r in rows if r["n_resid"] == 1]
    A, LK, ST = out["strata"]["all"], out["strata"]["lone_keystone"], out["strata"]["second_trap"]
    out["headline"] = {
        "n": A["n"], "strict": A["strict_min"], "resid_max": A["resid_F0_max_N"],
        "resid_med": float(np.median([r["resid_F0_max_N"] for r in rows])),
        "asym_max": A["asym_rel_max"], "fd_max": A["fd_step_rel_max"], "barU_max": A["bar_U_rel_max"],
        "mu1_min": A["mu1"]["min"], "mu1_med": A["mu1"]["median"], "mu1_max": A["mu1"]["max"],
        "lk_mu1_min": LK["mu1"]["min"], "lk_mu1_med": LK["mu1"]["median"], "lk_mu1_max": LK["mu1"]["max"],
        "st_mu1_min": ST["mu1"]["min"], "st_mu1_med": ST["mu1"]["median"], "st_mu1_max": ST["mu1"]["max"],
        "alone_n": len(one), "alone_axial": int(sum(r["soft_type"] == "axial" for r in one)),
        "alone_mu1_med": float(np.median([r["mu1"] for r in one])),
        "alone_mu2_med": float(np.median([r["mu2"] for r in one])),
        "lk_soft_on_blocker": LK["soft_on_blocker"], "st_soft_on_blocker": ST["soft_on_blocker"],
        "lk_multi": LK["multi_agent_n"], "lk_multi_soft_on_blocker": LK["multi_soft_on_blocker"],
        "st_common_lateral": ST["soft_type_counts"].get("common_lateral", 0),
        "st_blocker_weight_med": ST["soft_blocker_weight"]["median"],
        "abreast_n": len(ab), "abreast_mu1_min": min(r["mu1"] for r in ab), "abreast_mu1_max": max(r["mu1"] for r in ab),
        "abreast_mu1_med": float(np.median([r["mu1"] for r in ab])),
        "abreast_ratio_min": min(r["mu2"] / r["mu1"] for r in ab), "abreast_ratio_max": max(r["mu2"] / r["mu1"] for r in ab),
        "multi_blockerblock_stiffer": int(sum(r["blocker_block_eig_N_per_m"][0] > r["mu1"] for r in rows if r["n_resid"] > 1)),
        "multi_n": A["multi_agent_n"]}
    out["cpu_s"] = time.process_time() - t0
    print(revlib.out_json("A10", out), out["cpu_s"])


if __name__ == "__main__":
    main()
