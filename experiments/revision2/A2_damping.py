"""A2: damping regime of the lone-trap escapes, and the Kramers-Grote-Hynes and Mel'nikov-Meshkov factors.

Inputs (existing data only; no dynamics is run):
  data/derived/selection.json        E4 snapshots (10) and their snapshot files data/E1/library/<tag>.pkl
  data/BAR/gate.jsonl                accepted climbing-image saddles (all mobile coordinates), per condition
  data/derived/fix_a3.json           multidimensional Langer rate nu_L and the measured nu_hat / nu_L
  data/derived/E4_analysis.json      per-cell rates lambda (beta 1.5, 2.5, 3.5) and events
  data/derived/rev_B3.json           per-cell rates of the alone condition at beta 5, 6, 7 (3 snapshots)

Field and dynamics. The rest-state potential U of experiments/BAR/bar.py (Field; conditions full = all residual
agents mobile, pinned = "frozen" = blocker mobile with the neighbours fixed, alone = blocker only, density 0), the
same U as the gate and fix_a3. Near rest the code integrates m x'' = -grad U - (m / tau_i) x' + noise (Euler,
dt = 0.01 s); all masses are 80 kg, so the mass-weighted Hessian is H / m.

Per (snapshot, condition):
  minimum   bar.relax from the snapshot positions (as fix_a3); saddle = the gate's accepted climbing image
  Hessians  central second differences of U, h = 1e-5 m (as fix_a3), at the minimum and the saddle
  omega_b   sqrt(|lambda_u| / m), lambda_u the one negative eigenvalue of H_sad
  omega_a   sqrt(mu_1 / m) (softest eigenvalue of H_min) and sqrt(t.H_min.t / m) along the path tangent t at the
            minimum (the reaction-coordinate frequency)
  gamma     1 / tau of the blocker; also gamma_u = sum_i p_i / tau_i, p_i = |e_i|^2 the agent weights of the
            unit unstable eigenvector (equals gamma for one mobile agent)
  kappa     spatial-diffusion (Kramers-Grote-Hynes, Markovian) factor kappa = sqrt(1 + (gamma/2 omega_b)^2)
            - gamma / (2 omega_b); its multidimensional form lambda_+ / omega_b (lambda_+ the Langer growth rate)
  path      minimum-energy path from the saddle to the minimum by gradient flow X' = -grad U (equal masses, so
            mass-weighted steepest descent), started 1e-4 m from the saddle along the unstable eigenvector on the
            minimum's side, explicit steps alpha = 0.5 / lambda_max(H_sad) with each agent's step capped at 1 mm,
            stopped when U - U_min < 1e-4 dU; the remainder to the minimum is a straight segment. Back branch:
            the straight line from the minimum in the direction -t (t = path tangent at the minimum, pointing
            uphill to the saddle), 0.25 mm steps, up to the inner turning point U = U_sad (cap 3 m).
  action    S(E_b) = 2 int sqrt(2 m (E_b - U(l))) dl over back branch + path, E_b = U_sad (the undamped orbit at
            the barrier energy, from the inner turning point to the saddle and back). Approximation stated: the
            orbit is taken along the one-dimensional path (string direction uphill, straight line on the far
            side of the minimum), transverse motion neglected. Checks: harmonic S_h = 2 pi dU / omega_a,path and
            the mirror value (twice the uphill part); A is also given with S_low = the smallest of the three
            (a lower bound on A over the action estimates).
  Delta     energy loss per oscillation over k_BT: Delta = gamma S / k_BT with k_BT = dU / beta;
            also Delta_path = (2 / k_BT) int gamma_t(l) sqrt(2 m (E_b - U)) dl with gamma_t = sum_k t_k^2 / tau_k
            (per-coordinate friction projected on the path tangent).
  A(Delta)  Mel'nikov-Meshkov / Pollak-Grabert-Hanggi depopulation factor
            A(Delta) = exp[(1/pi) int_0^inf ln(1 - exp(-Delta (x^2 + 1/4))) dx / (x^2 + 1/4)]
            (= (1/2pi) over the whole line; limits A -> Delta for Delta -> 0 and A -> 1 for Delta -> inf, checked)
            (scipy quad); the turnover rate is k = A(Delta) k_Langer, so A is the prediction for the measured
            nu_hat / nu_L and kappa A for nu_hat / nu_TST.
  levels    beta = 1.5, 2.5, 3.5 (E4, every condition), 5, 6, 7 (B3, alone, 3 snapshots). Per fit the
            prediction comparable to nu_hat (slope held at -dU, event-weighted mean of ln lambda + beta over the
            levels) is A_fit = exp(sum_L d_L ln A(Delta_L) / sum_L d_L). Per cell the measured ratio is
            lambda_L exp(beta_L) / nu_L.
Output: data/derived/rev2_A2.json
"""
import json
import math
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import DERIVED, ROOT, np, sig  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments", "BAR"))
import bar  # noqa: E402
from scipy import integrate  # noqa: E402

CONDS = ("full", "frozen", "alone")
LEVELS_E4 = (1.5, 2.5, 3.5)
LEVELS_B3 = (5.0, 6.0, 7.0)
LK = {1.5: "b1p5", 2.5: "b2p5", 3.5: "b3p5"}
H_FD = 1e-5
M = 80.0


def hessian(f, X, h=H_FD):
    n = len(X)
    H = np.zeros((n, n))
    E = np.eye(n) * h
    for i in range(n):
        for j in range(i, n):
            H[i, j] = H[j, i] = (f.U(X + E[i] + E[j]) - f.U(X + E[i] - E[j]) - f.U(X - E[i] + E[j])
                                 + f.U(X - E[i] - E[j])) / (4 * h * h)
    return H


def capped(d, cap):
    v = d.reshape(-1, 2)
    n = np.linalg.norm(v, axis=1, keepdims=True)
    return (v * np.minimum(1.0, cap / np.maximum(n, 1e-300))).ravel()


def mep(f, Xs, XA, Hs, max_steps=60000):
    """Gradient-flow path saddle -> minimum; returns points (saddle first) and U along them."""
    w, V = np.linalg.eigh(Hs)
    e = V[:, 0]
    if e @ (XA - Xs) < 0:
        e = -e
    alpha = 0.5 / float(w[-1])
    UA, Us = f.U(XA), f.U(Xs)
    dU = Us - UA
    X = Xs + 1e-4 * e
    P, E = [Xs.copy(), X.copy()], [Us, f.U(X)]
    for _ in range(max_steps):
        X = X - capped(alpha * f.grad(X), 1e-3)
        u = f.U(X)
        P.append(X.copy())
        E.append(u)
        if u - UA < 1e-4 * dU:
            break
    P.append(XA.copy())
    E.append(UA)
    return np.array(P), np.array(E), int(len(P))


def back_branch(f, XA, t, Us, ds=2.5e-4, umax=3.0):
    P, E = [XA.copy()], [f.U(XA)]
    u = 0.0
    while u < umax:
        u += ds
        X = XA - u * t
        e = f.U(X)
        P.append(X)
        E.append(e)
        if e >= Us:
            break
    return np.array(P), np.array(E), bool(E[-1] >= Us)


def action(P, E, Eb, gam_t=None):
    """2 * int sqrt(2 m (Eb - U)) dl along the polyline P (trapezoid); optionally with weight gam_t."""
    dl = np.linalg.norm(np.diff(P, axis=0), axis=1)
    p = np.sqrt(2 * M * np.maximum(Eb - E, 0.0))
    if gam_t is not None:
        p = p * gam_t
    return float(2 * np.sum(0.5 * (p[1:] + p[:-1]) * dl))


def gamma_tangent(P, inv_tau2):
    """sum_k t_k^2 / tau_k at each vertex (tangent from neighbouring vertices)."""
    T = np.gradient(P, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-300)
    return (T ** 2) @ inv_tau2


def A_mm(D):
    if D <= 0:
        return 0.0
    g = lambda x: math.log(-math.expm1(-D * (x * x + 0.25))) / (x * x + 0.25)  # noqa: E731
    val, _ = integrate.quad(g, 0, np.inf, limit=400)
    return math.exp(val / math.pi)  # (1/pi) int_0^inf = (1/2pi) int_-inf^inf


def kappa_kgh(g, wb):
    z = g / (2 * wb)
    return math.sqrt(1 + z * z) - z


def summ(v):
    v = np.asarray([x for x in v if x is not None], float)
    if not len(v):
        return None
    return {"n": int(len(v)), "min": float(v.min()), "median": float(np.median(v)), "max": float(v.max())}


def main():
    t0 = time.process_time()
    sel = {s["tag"]: s for s in json.load(open(os.path.join(DERIVED, "selection.json")))["E4"]["snapshots"]}
    G = {r["job_id"]: r for r in rev2lib.revlib.load_runs(os.path.join(ROOT, "data", "BAR", "gate.jsonl"))}
    FA = json.load(open(os.path.join(DERIVED, "fix_a3.json")))["langer"]["per_snapshot"]
    E4 = json.load(open(os.path.join(DERIVED, "E4_analysis.json")))["snapshots"]
    B3 = json.load(open(os.path.join(DERIVED, "rev_B3.json")))["snapshots"]
    rows = []
    for tag in E4:
        g = G[tag]
        snap = pickle.load(open(os.path.join(ROOT, sel[tag]["snap"]), "rb"))
        st = snap["state"]
        b = g["blocker"]
        others = [i for i in g["resid"] if i != b]
        xb = st.positions[b].copy()
        fields = {"alone": bar.Field(snap, [b], [], rho_mode="zero"), "frozen": bar.Field(snap, [b], others),
                  "full": bar.Field(snap, [b] + others, [])}
        mob = {"alone": [b], "frozen": [b], "full": [b] + others}
        for c in CONDS:
            f, gc, fa = fields[c], g[c], FA[tag][c]
            X0 = xb.copy() if c != "full" else st.positions[[b] + others].ravel()
            XA = bar.relax(f, X0)
            Xs = np.array(gc["n%d" % gc["resolution_pair"][1]]["saddle"])
            UA, Us = f.U(XA), f.U(Xs)
            dU = Us - UA
            row = {"tag": tag, "cond": c, "n_mobile": len(mob[c]), "dU_J": dU, "accepted": bool(gc["accepted"])}
            if dU < 0.1:  # E4 skips barriers below 0.1 J (no temperature set)
                row["skipped"] = "dU < 0.1 J"
                rows.append(row)
                continue
            Hm, Hs = hessian(f, XA), hessian(f, Xs)
            em, (es, Vs) = np.linalg.eigvalsh(Hm), np.linalg.eigh(Hs)
            taus = st.taus[mob[c]]
            inv_tau2 = np.repeat(1.0 / taus, 2)
            eu = Vs[:, 0]
            p = (eu.reshape(-1, 2) ** 2).sum(1)
            wb = math.sqrt(-es[0] / M)
            gam = 1.0 / float(taus[0])
            gam_u = float(p @ (1.0 / taus))
            P, E, nsteps = mep(f, Xs, XA, Hs)
            Pf, Ef = P[::-1], E[::-1]  # minimum -> saddle
            k_t = min(len(Pf) - 1, 1 + int(np.argmax(np.linalg.norm(Pf - XA, axis=1) > 2e-3)))
            t = (Pf[k_t] - XA) / np.linalg.norm(Pf[k_t] - XA)
            Pb, Eb_, reached = back_branch(f, XA, t, Us)
            wa_path = math.sqrt(max(float(t @ Hm @ t), 0.0) / M)
            S_up = action(Pf, Ef, Us)
            S_back = action(Pb, Eb_, Us)
            S = S_up + S_back
            Sg = (action(Pf, Ef, Us, gamma_tangent(Pf, inv_tau2)) + action(Pb, Eb_, Us, gamma_tangent(Pb, inv_tau2)))
            S_h = 2 * math.pi * dU / wa_path if wa_path > 0 else None
            S_low = min(x for x in (S, 2 * S_up, S_h) if x)
            kap = kappa_kgh(gam, wb)
            kap_u = kappa_kgh(gam_u, wb)
            lam_p = fa.get("lambda_plus_s")
            row.update({
                "U_path_end_minus_min_J": float(E[-2] - UA), "mep_points": nsteps,
                "path_saddle_max_dev_J": float(Us - E.max()), "path_length_m": float(np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1))),
                "back_length_m": float(np.linalg.norm(Pb[-1] - XA)), "back_reached_Eb": reached,
                "lambda_u_N_per_m": float(es[0]), "lambda_u_fix_a3": fa.get("kappa_u_N_per_m"),
                "mu1_min_N_per_m": float(em[0]),
                "omega_b_s": wb, "omega_a_soft_s": math.sqrt(em[0] / M), "omega_a_path_s": wa_path,
                "gamma_s": gam, "gamma_u_s": gam_u, "unstable_weights": p.tolist(), "taus_s": taus.tolist(),
                "gamma_over_omega_b": gam / wb, "gamma_over_omega_a_path": gam / wa_path,
                "gamma_u_over_omega_b": gam_u / wb, "omega_b_dt": wb * 0.01,
                "kappa_kgh": kap, "kappa_kgh_gamma_u": kap_u,
                "kappa_langer_multid": (lam_p / wb) if lam_p else None,
                "S_Js": S, "S_up_Js": S_up, "S_back_Js": S_back, "S_mirror_Js": 2 * S_up, "S_harmonic_Js": S_h, "S_low_Js": S_low,
                "S_gamma_J": Sg, "gamma_S_over_dU": gam * S / dU, "gammaS_path_over_dU": Sg / dU,
                "nu_L": fa.get("nu_langer"), "nu_tst": fa.get("nu_tst"), "nu_hat": fa.get("nu_hat"),
                "measured_over_langer": fa.get("nu_hat_over_langer"),
                "measured_over_tst": (fa["nu_hat"] / fa["nu_tst"]) if fa.get("nu_hat") else None})
            levels = {}
            cells = E4[tag]["conds"][c]["levels"]
            for L in LEVELS_E4:
                D = gam * S * L / dU
                Dp = Sg * L / dU
                cl = cells[LK[L]]
                levels[f"{L:g}"] = {"beta": L, "Delta": D, "Delta_path": Dp, "A": A_mm(D), "A_path": A_mm(Dp),
                                    "A_lowS": A_mm(gam * S_low * L / dU),
                                    "events": cl["events"], "lam": cl["lam"],
                                    "measured_cell_over_langer": (cl["lam"] * math.exp(L) / fa["nu_langer"]
                                                                  if cl["events"] > 0 else None)}
            if c == "alone" and tag in B3:
                for cl in B3[tag]["cells"]:
                    L = cl["beta"]
                    if L in LEVELS_B3:
                        D, Dp = gam * S * L / dU, Sg * L / dU
                        levels[f"{L:g}"] = {"beta": L, "Delta": D, "Delta_path": Dp, "A": A_mm(D), "A_path": A_mm(Dp),
                                            "events": cl["events"], "lam": cl["lam"], "source": "B3",
                                            "measured_cell_over_langer": cl["lam"] * math.exp(L) / fa["nu_langer"]}
            row["levels"] = levels
            d = np.array([levels[f"{L:g}"]["events"] for L in LEVELS_E4], float)
            if d.sum() > 0:
                lnA = np.array([math.log(levels[f"{L:g}"]["A"]) for L in LEVELS_E4])
                lnAp = np.array([math.log(levels[f"{L:g}"]["A_path"]) for L in LEVELS_E4])
                row["A_fit"] = float(math.exp((d * lnA).sum() / d.sum()))
                row["A_fit_path"] = float(math.exp((d * lnAp).sum() / d.sum()))
                row["kappaA_fit"] = kap * row["A_fit"]
            row["A_range_E4"] = [levels["3.5"]["A"], levels["1.5"]["A"]]
            row["A_range_beta7"] = [A_mm(gam * S * 7.0 / dU), levels["1.5"]["A"]]
            rows.append(row)
            print(f"{tag:12s} {c:6s} dU={dU:7.2f} g/wb={gam / wb:.3f} kap={kap:.3f} S={S:.1f} (h {S_h:.1f}, mir {2 * S_up:.1f}) "
                  f"gS/dU={gam * S / dU:.2f} A(1.5..3.5)={levels['1.5']['A']:.3f}..{levels['3.5']['A']:.3f} "
                  f"Afit={row.get('A_fit', float('nan')):.3f} meas={row['measured_over_langer']} pts={nsteps} "
                  f"lu={es[0]:.1f}/{fa.get('kappa_u_N_per_m'):.1f}", flush=True)
    ok = [r for r in rows if "skipped" not in r]
    fit = [r for r in ok if r.get("measured_over_langer") is not None]
    out = {"doc": __doc__, "rows": rows, "n_rows": len(rows), "n_valid": len(ok), "n_fitted": len(fit)}
    S_ = {}
    for name, sub in (("all", ok), *((c, [r for r in ok if r["cond"] == c]) for c in CONDS)):
        sf = [r for r in sub if r.get("measured_over_langer") is not None]
        allA = [lv["A"] for r in sub for lv in r["levels"].values()]
        e4A = [r["levels"][f"{L:g}"]["A"] for r in sub for L in LEVELS_E4]
        e4Al = [r["levels"][f"{L:g}"]["A_lowS"] for r in sub for L in LEVELS_E4]
        S_[name] = {
            "n": len(sub), "gamma_over_omega_b": summ([r["gamma_over_omega_b"] for r in sub]),
            "gamma_u_over_omega_b": summ([r["gamma_u_over_omega_b"] for r in sub]),
            "gamma_over_omega_a_path": summ([r["gamma_over_omega_a_path"] for r in sub]),
            "omega_b_s": summ([r["omega_b_s"] for r in sub]), "omega_a_path_s": summ([r["omega_a_path_s"] for r in sub]),
            "omega_a_soft_s": summ([r["omega_a_soft_s"] for r in sub]),
            "kappa_kgh": summ([r["kappa_kgh"] for r in sub]),
            "kappa_langer_multid": summ([r["kappa_langer_multid"] for r in sub]),
            "gamma_S_over_dU": summ([r["gamma_S_over_dU"] for r in sub]),
            "S_over_S_harmonic": summ([r["S_Js"] / r["S_harmonic_Js"] for r in sub if r["S_harmonic_Js"]]),
            "S_over_S_mirror": summ([r["S_Js"] / r["S_mirror_Js"] for r in sub]),
            "A_E4_levels": summ(e4A), "A_E4_levels_lowS": summ(e4Al), "A_all_levels": summ(allA),
            "A_fit": summ([r["A_fit"] for r in sf]), "A_fit_path": summ([r["A_fit_path"] for r in sf]),
            "kappaA_fit": summ([r["kappaA_fit"] for r in sf]),
            "measured_over_langer": summ([r["measured_over_langer"] for r in sf]),
            "measured_over_tst": summ([r["measured_over_tst"] for r in sf]),
            "measured_over_A_fit": summ([r["measured_over_langer"] / r["A_fit"] for r in sf]),
            "n_fit_inside_A_range": int(sum(r["A_range_E4"][0] <= r["measured_over_langer"] <= r["A_range_E4"][1]
                                            for r in sf)),
            "n_fit": len(sf),
        }
    out["summary"] = S_
    a = S_["all"]
    med = a["measured_over_langer"]["median"]
    # 0.69 against the predicted range of A over the levels actually used
    out["headline"] = {
        "measured_median": med, "n_fits": a["n_fit"],
        "g_wb_min": a["gamma_over_omega_b"]["min"], "g_wb_med": a["gamma_over_omega_b"]["median"],
        "g_wb_max": a["gamma_over_omega_b"]["max"],
        "g_wb_full_med": S_["full"]["gamma_over_omega_b"]["median"],
        "g_wb_frozen_med": S_["frozen"]["gamma_over_omega_b"]["median"],
        "g_wb_alone_med": S_["alone"]["gamma_over_omega_b"]["median"],
        "gu_wb_full_max": S_["full"]["gamma_u_over_omega_b"]["max"],
        "g_wa_med": a["gamma_over_omega_a_path"]["median"],
        "wb_min": a["omega_b_s"]["min"], "wb_max": a["omega_b_s"]["max"],
        "wa_min": a["omega_a_path_s"]["min"], "wa_max": a["omega_a_path_s"]["max"],
        "kappa_min": a["kappa_kgh"]["min"], "kappa_med": a["kappa_kgh"]["median"], "kappa_max": a["kappa_kgh"]["max"],
        "kappa_md_min": a["kappa_langer_multid"]["min"], "kappa_md_max": a["kappa_langer_multid"]["max"],
        "gS_dU_min": a["gamma_S_over_dU"]["min"], "gS_dU_med": a["gamma_S_over_dU"]["median"],
        "gS_dU_max": a["gamma_S_over_dU"]["max"],
        "beta_delta_one_med": 1.0 / a["gamma_S_over_dU"]["median"],  # beta at which Delta = 1 (turnover)
        "A_at_delta_one": A_mm(1.0),
        "S_harm_ratio_min": a["S_over_S_harmonic"]["min"], "S_harm_ratio_max": a["S_over_S_harmonic"]["max"],
        "A_E4_min": a["A_E4_levels"]["min"], "A_E4_med": a["A_E4_levels"]["median"], "A_E4_max": a["A_E4_levels"]["max"],
        "A_E4_lowS_min": a["A_E4_levels_lowS"]["min"], "A_E4_lowS_med": a["A_E4_levels_lowS"]["median"],
        "A_all_min": a["A_all_levels"]["min"], "A_all_max": a["A_all_levels"]["max"],
        "A_fit_min": a["A_fit"]["min"], "A_fit_med": a["A_fit"]["median"], "A_fit_max": a["A_fit"]["max"],
        "kA_fit_med": a["kappaA_fit"]["median"],
        "meas_tst_med": a["measured_over_tst"]["median"],
        "meas_over_Afit_med": a["measured_over_A_fit"]["median"],
        "inside_A_range": a["n_fit_inside_A_range"],
        "median_inside_A_E4": bool(a["A_E4_levels"]["min"] <= med <= a["A_E4_levels"]["max"]),
    }
    # does the slope offset explain the prefactor deficit? nu_hat absorbs exp((1 - r) beta_bar) when the slope
    # ratio r differs from 1; compare with the free-slope intercept nu_free and rank-correlate with r
    from scipy import stats as _st
    rr, mm, ff = [], [], []
    for r in fit:
        a = E4[r["tag"]]["conds"][r["cond"]]["arrhenius"]
        rr.append(a["ratio"])
        mm.append(r["measured_over_langer"])
        ff.append(a["nu_free"] / r["nu_L"])
    rho, pv = _st.spearmanr(rr, mm)
    out["slope_offset_check"] = {"free_intercept_over_langer": summ(ff), "spearman_ratio_vs_measured": float(rho),
                                 "spearman_p": float(pv), "ratio_median": float(np.median(rr))}
    out["headline"].update({"free_over_langer_med": float(np.median(ff)), "rho_r_meas": float(rho), "rho_p": float(pv)})
    out["headline_2sf"] = {k: sig(v, 2) for k, v in out["headline"].items() if isinstance(v, float)}
    # B3 per-level comparison (alone, beta 1.5-7): A(Delta) against lambda e^beta / nu_L
    b3 = []
    for r in ok:
        if r["cond"] == "alone" and r["tag"] in B3:
            for k, lv in sorted(r["levels"].items(), key=lambda kv: kv[1]["beta"]):
                b3.append({"tag": r["tag"], "dU_J": r["dU_J"], "beta": lv["beta"], "A": lv["A"],
                           "measured_cell_over_langer": lv["measured_cell_over_langer"]})
    out["b3_levels"] = b3
    hi = [x for x in b3 if x["beta"] >= 5]
    out["b3_summary"] = {"A_beta5_7": summ([x["A"] for x in hi]),
                         "measured_beta5_7": summ([x["measured_cell_over_langer"] for x in hi]),
                         "measured_over_A_beta5_7": summ([x["measured_cell_over_langer"] / x["A"] for x in hi])}
    out["cpu_s"] = time.process_time() - t0
    print(json.dumps(out["headline"], indent=0))
    print(json.dumps(out["b3_summary"], indent=0))
    print(rev2lib.out_json("A2", out), out["cpu_s"])


if __name__ == "__main__":
    main()
