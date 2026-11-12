"""A3: Arrhenius slope ratio of the lone blocker over beta = 1.5-7, censoring-aware, and the causes of its shortfall.

Inputs (existing data): data/E4/e4_escape.jsonl (alone, beta 1.5 / 2.5 / 3.5, 20 restarts, censored at 300 / 300 /
900 s) and data/revision/B3/b3.jsonl (alone, beta 5 / 6 / 7, 20 restarts, censored per cell at 1552-36 715 s) for the
three B3 snapshots E1b_seed72 (dU_alone 5.8 J), E1b_seed162 (21 J), E1b_seed192 (56 J); data/BAR/barriers.jsonl
(alone minimum and saddle); the toy runs data/revision2/A3/toy.json (A3_toy_runs.py).

Method.
(1) Pooled fit. The escape time of a restart is right-censored at the cell's horizon. Under a constant rate per
    cell the censored likelihood is prod lambda^d exp(-lambda E) (d escapes, E total time at risk), i.e. a Poisson
    regression of d with offset ln E. Model ln lambda = a_snapshot - r beta (beta = dU / k_B T_eff exactly, so
    r = -slope / dU, the slope ratio); one r, one intercept per snapshot, 18 cells. MLE; 95% interval from a
    nonparametric bootstrap that resamples the 20 restarts within every cell (2000 replicates, PCG64(2026)),
    which keeps each restart's censoring and does not assume exponential times (the B3 Weibull shapes are
    0.64-1.38); the profile-likelihood interval is given as well. Per snapshot: the same fit with its own r.
    Sensitivity: per cell censored Weibull MLE (shape k, scale theta; experiments/E3/survival.py), mean escape
    time theta Gamma(1 + 1/k), least squares of its log on beta with snapshot intercepts and event weights,
    same bootstrap.
(2)-(3) Censored fraction per cell at beta 5, 6, 7.
(4) Weibull shape per cell at beta 6 and 7 (censored profile likelihood, survival.weibull_pool, which treats the
    censored restarts as survivors to their horizon), and one shape per snapshot over beta 6-7 (scale per cell).
    Early-escape check: escapes before 10 s at beta 6-7.
(5) Causes of r < 1.
  (a) Finite-barrier prefactor. Pooled fits with one extra common term: ln lambda = a_s - r beta + c ln beta and
      ln lambda = a_s - r beta + c / beta. Theory: rate = A(Delta) kappa k_TST(T), with k_TST the exact 2-D
      transition-state rate of the tabulated potential U (A3_toylib grid; dividing line x = x_saddle; anharmonic
      well and saddle line included), kappa = sqrt(1 + (gamma / 2 omega_b)^2) - gamma / (2 omega_b) (Kramers,
      gamma = 1 / tau, omega_b^2 = |U_xx(saddle)| / m) and A(Delta) the Mel'nikov-Meshkov depletion factor of the
      energy-diffusion regime, Delta = gamma S / k_B T, S the action of the axial orbit at the saddle energy.
      Harmonic TST alone has a T-independent prefactor (ratio 1), so the exact-TST and A(Delta) terms carry the
      finite-barrier and friction-regime curvature. Fit of r to the theory curve with the data's event weights.
  (b) Discrete-time temperature. The code's update near a harmonic minimum of curvature k is
      v' = a v - h (k / m) x + sigma xi, x' = x + h v' (a = 1 - h / tau, h = dt), and kT_eff = m sigma^2 / (1 - a^2).
      The stationary covariance of this AR(1) map gives exactly
        T_conf / T_eff = k <x^2> / kT_eff = (2 - gamma h)^2 / (4 - 2 gamma h - h^2 omega^2) = 1 - gamma h / 2 + O(h^2),
        T_kin / T_eff = m <v^2> / kT_eff = 2 (2 - gamma h) / (4 - 2 gamma h - h^2 omega^2) = 1 + h^2 omega^2 / 4 + O(h^3),
      gamma = 1 / tau, omega^2 = k / m. A rate set by exp(-dU / k_B T_conf) fitted against 1 / k_B T_eff gives
      r = T_eff / T_conf; bias (T_eff - T_conf) / T_conf. Evaluated at the alone-minimum Hessian eigenvalues of
      each snapshot and checked by a 1-D simulation (A3_toylib.harmonic_1d, 2000 walkers, 20 000 steps, seed 31).
      Toy: rates at dt = 0.0025 s against 0.01 s (no speed cap), beta 1.5-3.5.
  (c) Speed cap. The update caps the speed at 2 v0 (0.8-1.4 m/s per snapshot gives 1.6-2.8 m/s), which removes
      kinetic energy at high temperature. Measured: the blocker's kinetic temperature in the trap per cell
      (v_moments of runlib.escape, 2 s burn-in, x < 9.95 m). Toy: rates with and without the cap, beta 1.5-3.5;
      the measured rates divided by the toy cap factor and refitted. Barrier end points: string vs 1-D axis
      barrier and the climbing-image barrier.
  Toy reproduction: the toy rates with the code update fitted like the data (r per snapshot and pooled).
Output: data/derived/rev2_A3.json.
"""
import json
import math
import os
import pickle
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import DATA, load_runs, np, sig  # noqa: E402
from scipy import integrate, optimize, special, stats  # noqa: E402
from survival import exp_rate, weibull_pool  # noqa: E402
import bar  # noqa: E402
import e4_escape  # noqa: E402
from A3_toylib import DG, grid_U, harmonic_1d  # noqa: E402

TAGS = ("E1b_seed72", "E1b_seed162", "E1b_seed192")
NAMES = {"E1b_seed72": "Shallow", "E1b_seed162": "Mid", "E1b_seed192": "Deep"}
BETAS = (1.5, 2.5, 3.5, 5.0, 6.0, 7.0)
N_BOOT = 2000
DT = 0.01
TOY = os.path.join(DATA, "revision2", "A3", "toy.json")


# ---------------------------------------------------------------- data
def load_cells():
    new = load_runs(os.path.join(DATA, "revision", "B3", "b3.jsonl"))
    old = [r for r in load_runs(os.path.join(DATA, "E4", "e4_escape.jsonl"))
           if r["cond"] == "alone" and r["snap"][:-4] in TAGS]
    by = defaultdict(list)
    for r in old:
        by[(r["snap"][:-4], float(r["beta_ref"]))].append(r)
    for r in new:
        by[(r["tag"], float(r["beta_ref"]))].append(r)
    cells = []
    for si, tag in enumerate(TAGS):
        for b in BETAS:
            R = sorted(by[(tag, b)], key=lambda r: r["rep"])
            t = np.array([r["t_run"] for r in R])
            c = np.array([r["censored"] for r in R], bool)
            M = np.sum([r["v_moments"] for r in R], 0)
            n = M[0]
            Tk = [80.0 * (M[3] / n - (M[1] / n) ** 2) / R[0]["kT_eff"], 80.0 * (M[4] / n - (M[2] / n) ** 2) / R[0]["kT_eff"]]
            cells.append({"tag": tag, "si": si, "beta": b, "t": t, "c": c, "kT_eff": R[0]["kT_eff"],
                          "dU": R[0]["dU_cond"], "tau": R[0]["tau_b"], "t_cens": R[0]["t_cens"],
                          "Tkin_ratio_xy": Tk, "n": len(R)})
    return cells


# ---------------------------------------------------------------- pooled Poisson (censored exponential) fits
def design(cells, extra=None, per_snap_r=False):
    ns = len(TAGS)
    cols = []
    for c in cells:
        row = [1.0 if c["si"] == k else 0.0 for k in range(ns)]
        if per_snap_r:
            row += [-c["beta"] if c["si"] == k else 0.0 for k in range(ns)]
        else:
            row += [-c["beta"]]
        if extra == "logb":
            row += [math.log(c["beta"])]
        elif extra == "invb":
            row += [1.0 / c["beta"]]
        cols.append(row)
    return np.array(cols)


def poisson_fit(X, d, E, x0=None):
    """MLE of ln lambda = X b with d ~ Poisson(E exp(X b)); Newton iterations."""
    b = np.zeros(X.shape[1]) if x0 is None else x0.copy()
    if x0 is None:
        b[:len(TAGS)] = math.log(max(d.sum(), 1) / E.sum())
    for _ in range(100):
        mu = E * np.exp(X @ b)
        g = X.T @ (d - mu)
        H = X.T @ (X * mu[:, None])
        step = np.linalg.solve(H, g)
        b += step
        if np.max(np.abs(step)) < 1e-10:
            break
    ll = float(np.sum(d * (X @ b + np.log(E)) - E * np.exp(X @ b)))
    return b, ll


def de(cells, idx=None):
    d = np.array([float((~c["c"][idx[k]] if idx is not None else ~c["c"]).sum()) for k, c in enumerate(cells)])
    E = np.array([float((c["t"][idx[k]] if idx is not None else c["t"]).sum()) for k, c in enumerate(cells)])
    return d, E


def boot_indices(cells, rng):
    return [rng.integers(0, c["n"], c["n"]) for c in cells]


def profile_ci_r(cells, X, col):
    d, E = de(cells)
    b, ll = poisson_fit(X, d, E)
    target = ll - stats.chi2.ppf(0.95, 1) / 2

    def pl(r):
        keep = [k for k in range(X.shape[1]) if k != col]
        Xr = X[:, keep]
        off = X[:, col] * r
        bb, _ = poisson_fit(Xr, d, E * np.exp(off), x0=b[keep])
        return float(np.sum(d * (Xr @ bb + off + np.log(E)) - E * np.exp(Xr @ bb + off))) - target

    lo = optimize.brentq(pl, b[col] - 2.0, b[col])
    hi = optimize.brentq(pl, b[col], b[col] + 2.0)
    return [lo, hi]


# ---------------------------------------------------------------- Weibull per cell
def weib_cell(t, c):
    w = weibull_pool([(t, c)])
    tt = np.maximum(np.asarray(t, float), 1e-3)
    k = w["k"]
    thk = np.sum(tt ** k) / (~c).sum()
    theta = thk ** (1.0 / k)
    return w, theta, theta * math.gamma(1 + 1.0 / k)


def weibull_mean_fit(cells, idx=None):
    y, w, X = [], [], []
    for k, c in enumerate(cells):
        t = c["t"] if idx is None else c["t"][idx[k]]
        cc = c["c"] if idx is None else c["c"][idx[k]]
        if (~cc).sum() < 3:
            return None
        _, _, mt = weib_cell(t, cc)
        y.append(math.log(mt))
        w.append(float((~cc).sum()))
        X.append([1.0 if c["si"] == s else 0.0 for s in range(len(TAGS))] + [c["beta"]])
    X, y, w = np.array(X), np.array(y), np.array(w)
    sw = np.sqrt(w)
    b = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
    return float(b[-1])


# ---------------------------------------------------------------- theory (TST x Kramers x Mel'nikov-Meshkov)
def mm_A(Delta):
    f = lambda z: math.log(-math.expm1(-Delta * (0.25 + z * z))) / (0.25 + z * z)  # noqa: E731
    v, _ = integrate.quad(f, -np.inf, np.inf, limit=200)
    return math.exp(v / math.pi)


def theory(tag, s, f, row):
    xs, ys, U = grid_U(f)
    m, tau = float(f.m[0]), float(f.tau[0])
    gam = 1.0 / tau
    xm, xsad = np.array(row["alone"]["x_min"]), np.array(row["alone"]["saddle"])
    Umin, Usad = f.U(xm), f.U(xsad)
    h = 1e-4
    E2 = np.eye(2) * h

    def hess(X):
        H = np.zeros((2, 2))
        for i in range(2):
            for j in range(2):
                H[i, j] = (f.U(X + E2[i] + E2[j]) - f.U(X + E2[i] - E2[j]) - f.U(X - E2[i] + E2[j])
                           + f.U(X - E2[i] - E2[j])) / (4 * h * h)
        return H
    Hm, Hs = hess(xm), hess(xsad)
    ev_m = np.linalg.eigvalsh(Hm)
    wb = math.sqrt(abs(Hs[0, 0]) / m)
    kappa = math.sqrt(1 + (gam / (2 * wb)) ** 2) - gam / (2 * wb)
    # axial action at the saddle energy
    xa = np.linspace(8.0, xsad[0], 20001)
    Ua = np.array([f.U(np.array([x, 5.0])) for x in xa[::20]])
    Ua = np.interp(xa, xa[::20], Ua)
    kin = np.maximum(0.0, Usad - Ua)
    S = 2.0 * np.trapezoid(np.sqrt(2.0 * m * kin), xa)
    isad = int(round((xsad[0] - xs[0]) / DG))
    dU = Usad - Umin
    out = {}
    for b in BETAS:
        kT = dU / b
        W = np.exp(-(U - Usad) / kT)
        Zw = W[:isad + 1].sum() * DG * DG
        Zs = W[isad].sum() * DG
        kTST = math.sqrt(kT / (2 * math.pi * m)) * Zs / Zw
        Delta = gam * S / kT
        A = mm_A(Delta)
        out[f"{b:g}"] = {"k_tst": kTST, "kappa": kappa, "Delta": Delta, "A_mm": A, "lam": A * kappa * kTST,
                         "nu_tst": kTST * math.exp(b)}
    # harmonic TST prefactor (T-independent)
    evs = np.linalg.eigvalsh(Hs)
    nu_h = math.sqrt(np.prod(ev_m) / evs[1]) / (2 * math.pi * math.sqrt(m))   # Vineyard: stable modes only
    return {"Hmin_eig": ev_m.tolist(), "Hsad_eig": np.linalg.eigvalsh(Hs).tolist(), "omega_b": wb, "kappa": kappa,
            "action_S": S, "gamma": gam, "nu_harmonic_tst": nu_h, "levels": out, "U_saddle_minus_min": dU,
            "nu_tst_7_over_harmonic": out["7"]["nu_tst"] / nu_h, "U_x10_minus_saddle": float(f.U(np.array([10.0, 5.0])) - Usad)}


def wls_slope(beta, y, w, si):
    X = np.array([[1.0 if s == k else 0.0 for k in range(len(TAGS))] + [-b] for b, s in zip(beta, si)])
    sw = np.sqrt(np.asarray(w, float))
    return float(np.linalg.lstsq(X * sw[:, None], np.asarray(y) * sw, rcond=None)[0][-1])


# ---------------------------------------------------------------- discrete-time temperature
def tconf_ratio(gam, h, w2):
    return (2 - gam * h) ** 2 / (4 - 2 * gam * h - h * h * w2)


def tkin_ratio(gam, h, w2):
    return 2 * (2 - gam * h) / (4 - 2 * gam * h - h * h * w2)


# ---------------------------------------------------------------- main
def main():
    cells = load_cells()
    rng = np.random.default_rng(2026)
    d, E = de(cells)
    out = {"doc": __doc__, "cells": [], "snapshots": {}}

    # (1) pooled and per-snapshot fits
    X0 = design(cells)
    b0, _ = poisson_fit(X0, d, E)
    Xp = design(cells, per_snap_r=True)
    bp, _ = poisson_fit(Xp, d, E)
    Xl, Xi = design(cells, "logb"), design(cells, "invb")
    bl, _ = poisson_fit(Xl, d, E)
    bi, _ = poisson_fit(Xi, d, E)
    wm0 = weibull_mean_fit(cells)
    hi_cells = [c for c in cells if c["beta"] >= 5]
    lo_cells = [c for c in cells if c["beta"] <= 3.5]
    dh, Eh = de(hi_cells)
    bh, _ = poisson_fit(design(hi_cells), dh, Eh)
    BS = defaultdict(list)
    for _ in range(N_BOOT):
        idx = boot_indices(cells, rng)
        db, Eb = de(cells, idx)
        if (db == 0).any():
            continue
        BS["r"].append(poisson_fit(X0, db, Eb, x0=b0)[0][3])
        BS["rp"].append(poisson_fit(Xp, db, Eb, x0=bp)[0][3:6])
        bb = poisson_fit(Xl, db, Eb, x0=bl)[0]
        BS["rl"].append(bb[3]); BS["cl"].append(bb[4])
        bb = poisson_fit(Xi, db, Eb, x0=bi)[0]
        BS["ri"].append(bb[3]); BS["ci"].append(bb[4])
        ih = [idx[k] for k, c in enumerate(cells) if c["beta"] >= 5]
        dhb, Ehb = de(hi_cells, ih)
        BS["rh"].append(poisson_fit(design(hi_cells), dhb, Ehb, x0=bh)[0][3])
        wmb = weibull_mean_fit(cells, idx)
        if wmb is not None:
            BS["wm"].append(wmb)
    pc = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]  # noqa: E731
    BS = {k: np.array(v) for k, v in BS.items()}
    pooled = {"ratio": float(b0[3]), "ci95_boot": pc(BS["r"]), "ci95_profile": profile_ci_r(cells, X0, 3),
              "n_boot": int(len(BS["r"])), "events": int(d.sum()), "restarts": int(sum(c["n"] for c in cells)),
              "censored": int(sum(c["c"].sum() for c in cells)),
              "intercepts": b0[:3].tolist()}
    pooled["shortfall"] = 1.0 - pooled["ratio"]
    out["pooled"] = pooled
    out["pooled_5_7"] = {"ratio": float(bh[3]), "ci95_boot": pc(BS["rh"])}
    out["pooled_weibull_mean"] = {"ratio": wm0, "ci95_boot": pc(BS["wm"]), "n_boot": int(len(BS["wm"]))}
    out["fit_logbeta"] = {"ratio": float(bl[3]), "ci95_boot": pc(BS["rl"]), "c": float(bl[4]), "c_ci95": pc(BS["cl"]),
                          "model": "ln lambda = a_s - r beta + c ln beta"}
    out["fit_invbeta"] = {"ratio": float(bi[3]), "ci95_boot": pc(BS["ri"]), "c": float(bi[4]), "c_ci95": pc(BS["ci"]),
                          "model": "ln lambda = a_s - r beta + c / beta"}
    # per snapshot
    snap_rows = {}
    for k, tag in enumerate(TAGS):
        sub = [c for c in cells if c["tag"] == tag]
        Xs_ = design(sub)[:, [k, 3]]
        ds, Es = de(sub)
        bs_, _ = poisson_fit(Xs_, ds, Es, x0=np.array([math.log(ds.sum() / Es.sum()), 1.0]))
        snap_rows[tag] = {"name": NAMES[tag], "dU_alone_J": sub[0]["dU"], "tau_b": sub[0]["tau"],
                          "ratio": float(bp[3 + k]), "ratio_single": float(bs_[1]),
                          "ci95_boot": pc(BS["rp"][:, k])}
    # cells: rates, censoring, Weibull
    for c in cells:
        er = exp_rate(c["t"], c["c"])
        w, theta, mt = weib_cell(c["t"], c["c"])
        early = int(((~c["c"]) & (c["t"] < 10.0)).sum())
        out["cells"].append({"tag": c["tag"], "beta": c["beta"], "n": c["n"], "events": er["events"],
                             "censored": int(c["c"].sum()), "censored_frac": float(c["c"].mean()),
                             "t_cens": c["t_cens"], "lam": er["lam"], "lam_ci95": er["ci95"],
                             "exposure_s": er["exposure_s"], "weibull_k": w["k"], "weibull_ci95": w["ci95"],
                             "weibull_mean_s": mt, "early_lt10s": early, "Tkin_ratio_xy": c["Tkin_ratio_xy"]})
    for tag in TAGS:
        S = snap_rows[tag]
        C = {f"{x['beta']:g}": x for x in out["cells"] if x["tag"] == tag}
        S["censored_frac"] = {b: C[b]["censored_frac"] for b in ("5", "6", "7")}
        S["censored"] = {b: C[b]["censored"] for b in ("5", "6", "7")}
        S["weibull"] = {b: {"k": C[b]["weibull_k"], "ci95": C[b]["weibull_ci95"], "events": C[b]["events"],
                            "censored": C[b]["censored"]} for b in ("6", "7")}
        g67 = [(c["t"], c["c"]) for c in cells if c["tag"] == tag and c["beta"] >= 6]
        S["weibull_6_7"] = weibull_pool(g67)
        S["early_lt10s_6_7"] = sum(C[b]["early_lt10s"] for b in ("6", "7"))
        S["Tkin_ratio_axial"] = {b: C[b]["Tkin_ratio_xy"][0] for b in C}
    out["snapshots"] = snap_rows
    out["weibull_6_7_all"] = weibull_pool([(c["t"], c["c"]) for c in cells if c["beta"] >= 6])
    out["censored_frac_5_7_max"] = max(x["censored_frac"] for x in out["cells"] if x["beta"] >= 5)
    out["censored_frac_5_7_min"] = min(x["censored_frac"] for x in out["cells"] if x["beta"] >= 5)

    # (5a) theory and (5b) discrete-time, per snapshot
    Sn = {s["tag"]: s for s in e4_escape.snapshots()}
    rows = {json.loads(l)["job_id"]: json.loads(l) for l in open(os.path.join(DATA, "BAR", "barriers.jsonl"))}
    th_all, dts = {}, {}
    beta_l, y_l, w_l, si_l = [], [], [], []
    for k, tag in enumerate(TAGS):
        s = Sn[tag]
        snap = pickle.load(open(s["snap"], "rb"))
        f = bar.Field(snap, [s["blocker"]], [], rho_mode="zero")
        th = theory(tag, s, f, rows[tag])
        al = rows[tag]["alone"]
        th["dU_string"], th["dU_climb"], th["dU_axis_1d"] = al["dU_string"], al["dU_climb"], rows[tag]["dU_1d_axis_alone"]
        th["dU_used"] = s["dU"]["alone"]
        th["endpoint_rel_spread"] = (max(al["dU_string"], al["dU_climb"], rows[tag]["dU_1d_axis_alone"])
                                     - min(al["dU_string"], al["dU_climb"], rows[tag]["dU_1d_axis_alone"])) / s["dU"]["alone"]
        sub = [c for c in cells if c["tag"] == tag]
        bl_, yl_, wl_ = [], [], []
        for c in sub:
            L = th["levels"][f"{c['beta']:g}"]
            bl_.append(c["beta"]); yl_.append(math.log(L["lam"])); wl_.append(max(1.0, float((~c["c"]).sum())))
        th["ratio_theory"] = wls_slope(bl_, yl_, wl_, [0] * len(bl_))
        th["ratio_tst_only"] = wls_slope(bl_, [math.log(th["levels"][f"{b:g}"]["k_tst"]) for b in bl_], wl_, [0] * len(bl_))
        th["lam_theory_over_measured"] = {f"{c['beta']:g}": th["levels"][f"{c['beta']:g}"]["lam"] / max(
            float((~c["c"]).sum()) / float(c["t"].sum()), 1e-300) for c in sub}
        beta_l += bl_; y_l += yl_; w_l += wl_; si_l += [k] * len(bl_)
        th_all[tag] = th
        gam = 1.0 / float(f.tau[0])
        ev = th["Hmin_eig"]
        dd = {"gamma": gam, "dt": DT, "modes": []}
        for j, kk in enumerate(ev):
            w2 = kk / float(f.m[0])
            tc, tk = tconf_ratio(gam, DT, w2), tkin_ratio(gam, DT, w2)
            nc, nk = harmonic_1d(kk, float(f.m[0]), float(f.tau[0]), 1.0, DT, 20000, 2000, 31 + 10 * k + j)
            dd["modes"].append({"k_N_per_m": kk, "Tconf_over_Teff": tc, "Tkin_over_Teff": tk,
                                "Tconf_over_Teff_sim": nc, "Tkin_over_Teff_sim": nk,
                                "ratio_bias": 1.0 / tc - 1.0})
        dd["first_order_bias"] = gam * DT / 2
        dts[tag] = dd
    out["theory"] = th_all
    out["theory_pooled_ratio"] = wls_slope(beta_l, y_l, w_l, si_l)
    out["discrete_time"] = dts
    allb = [m["ratio_bias"] for t in dts for m in dts[t]["modes"]]
    out["discrete_time_bias_range"] = [min(allb), max(allb)]

    # toy runs
    if os.path.exists(TOY):
        T = json.load(open(TOY))
        toy = {"cells": {}}
        for key, v in T.items():
            t = np.array([np.nan if x is None else x for x in v["t"]])
            cen = np.isnan(t)
            tt = np.where(cen, v["T"], t)
            er = exp_rate(tt, cen)
            toy["cells"][key] = {"lam": er["lam"], "events": er["events"], "N": v["N"], "T": v["T"],
                                 "censored_frac": er["censored_frac"], "wall_s": v["wall_s"],
                                 "weibull_k": weibull_pool([(tt, cen)])["k"] if er["events"] else None,
                                 "_t": tt, "_c": cen}
        TC = toy["cells"]
        meas = {(c["tag"], c["beta"]): c for c in cells}
        have_code = all(f"{t}|{b:g}|code" in TC for t in TAGS for b in BETAS)
        if have_code:
            # toy fitted like the data (code update)
            tc_cells = [{"tag": t, "si": k, "beta": b, "t": TC[f"{t}|{b:g}|code"]["_t"],
                         "c": TC[f"{t}|{b:g}|code"]["_c"], "n": TC[f"{t}|{b:g}|code"]["N"]}
                        for k, t in enumerate(TAGS) for b in BETAS]
            dtc, Etc = de(tc_cells)
            btc, _ = poisson_fit(design(tc_cells), dtc, Etc)
            btp, _ = poisson_fit(design(tc_cells, per_snap_r=True), dtc, Etc)
            rr, rrp = [], []
            for _ in range(500):
                idx = boot_indices(tc_cells, rng)
                db, Eb = de(tc_cells, idx)
                rr.append(poisson_fit(design(tc_cells), db, Eb, x0=btc)[0][3])
                rrp.append(poisson_fit(design(tc_cells, per_snap_r=True), db, Eb, x0=btp)[0][3:6])
            rrp = np.array(rrp)
            toy["code_pooled_ratio"] = {"ratio": float(btc[3]), "ci95_boot": pc(rr)}
            toy["code_snap_ratio"] = {t: {"ratio": float(btp[3 + k]), "ci95_boot": pc(rrp[:, k])}
                                      for k, t in enumerate(TAGS)}
            toy["lam_toy_over_measured"] = {f"{t}|{b:g}": TC[f"{t}|{b:g}|code"]["lam"] / (
                (~meas[(t, b)]["c"]).sum() / meas[(t, b)]["t"].sum()) for t in TAGS for b in BETAS}
            toy["weibull_6_7"] = {t: weibull_pool([(TC[f"{t}|{b:g}|code"]["_t"], TC[f"{t}|{b:g}|code"]["_c"])
                                                   for b in (6.0, 7.0)]) for t in TAGS}
        # cap and dt factors at beta <= 3.5
        fac = {}
        for t in TAGS:
            for b in BETAS:
                kc, kn, kh = f"{t}|{b:g}|code", f"{t}|{b:g}|nocap", f"{t}|{b:g}|nocap_h4"
                if kc in TC and kn in TC:
                    e = {"cap": TC[kn]["lam"] / TC[kc]["lam"]}
                    if kh in TC:
                        e["dt"] = TC[kh]["lam"] / TC[kn]["lam"]
                    fac[f"{t}|{b:g}"] = e
        toy["factors"] = fac
        if all(f"{t}|{b:g}" in fac for t in TAGS for b in BETAS if b <= 3.5):
            for which in ("cap", "cap_dt"):
                corr = np.ones(len(cells))
                for k, c in enumerate(cells):
                    F = fac.get(f"{c['tag']}|{c['beta']:g}")
                    if F:
                        corr[k] = F["cap"] * (F.get("dt", 1.0) if which == "cap_dt" else 1.0)
                bc, _ = poisson_fit(X0, d, E / corr)
                bcp, _ = poisson_fit(Xp, d, E / corr)
                rr, rrp = [], []
                rng2 = np.random.default_rng(2027)
                for _ in range(N_BOOT):
                    idx = boot_indices(cells, rng2)
                    db, Eb = de(cells, idx)
                    if (db == 0).any():
                        continue
                    rr.append(poisson_fit(X0, db, Eb / corr, x0=bc)[0][3])
                    rrp.append(poisson_fit(Xp, db, Eb / corr, x0=bcp)[0][3:6])
                rrp = np.array(rrp)
                toy[f"measured_corrected_{which}"] = {
                    "ratio": float(bc[3]), "ci95_boot": pc(rr),
                    "snap": {t: {"ratio": float(bcp[3 + k]), "ci95_boot": pc(rrp[:, k])} for k, t in enumerate(TAGS)}}
        for v in TC.values():
            v.pop("_t"); v.pop("_c")
        toy["cpu_s"] = sum(v["wall_s"] for v in T.values())
        out["toy"] = toy
    reg = {"A_mm_shallow_b1p5": out["theory"]["E1b_seed72"]["levels"]["1.5"]["A_mm"],
           "A_mm_deep_b1p5": out["theory"]["E1b_seed192"]["levels"]["1.5"]["A_mm"],
           "Tkin_axial_deep_b1p5": out["snapshots"]["E1b_seed192"]["Tkin_ratio_axial"]["1.5"]}
    if "toy" in out:
        out["toy"]["cpu_min"] = out["toy"]["cpu_s"] / 60.0
        F = out["toy"]["factors"]
        if "E1b_seed192|1.5" in F:
            reg["cap_deep_b1p5"] = F["E1b_seed192|1.5"]["cap"]
            reg["cap_deep_b2p5"] = F["E1b_seed192|2.5"]["cap"]
    out["reg"] = reg   # flat aliases for the registry (dotted keys cannot contain "1.5")
    rev2lib.out_json("A3", out)
    P = out["pooled"]
    print("pooled r %.3f boot %s profile %s" % (P["ratio"], np.round(P["ci95_boot"], 3), np.round(P["ci95_profile"], 3)))
    print("5-7 pooled", out["pooled_5_7"], "weibull-mean", out["pooled_weibull_mean"])
    for t in TAGS:
        S = out["snapshots"][t]
        print(t, "r %.3f %s" % (S["ratio"], np.round(S["ci95_boot"], 3)), "cens", S["censored_frac"],
              "W67", {b: (round(S["weibull"][b]["k"], 2), np.round(S["weibull"][b]["ci95"], 2).tolist()) for b in ("6", "7")},
              "W67pool", round(S["weibull_6_7"]["k"], 2), S["weibull_6_7"]["ci95"], "early", S["early_lt10s_6_7"],
              "Tkin_ax", {b: round(v, 3) for b, v in S["Tkin_ratio_axial"].items()})
    print("logb", out["fit_logbeta"]); print("invb", out["fit_invbeta"])
    for t in TAGS:
        th = out["theory"][t]
        print(t, "theory r %.3f tst-only %.3f kappa %.3f" % (th["ratio_theory"], th["ratio_tst_only"], th["kappa"]),
              {b: (round(L["A_mm"], 3), round(L["nu_tst"], 4), round(L["Delta"], 2)) for b, L in th["levels"].items()},
              "th/meas", {b: round(v, 2) for b, v in th["lam_theory_over_measured"].items()},
              "endpoints", round(th["endpoint_rel_spread"], 5), "Hmin", np.round(th["Hmin_eig"], 0))
    print("theory pooled", out["theory_pooled_ratio"])
    print("dt", json.dumps(out["discrete_time"], indent=0)[:1500])
    if "toy" in out:
        print(json.dumps({k: v for k, v in out["toy"].items() if k != "cells"}, indent=1, default=float)[:4000])


if __name__ == "__main__":
    main()
