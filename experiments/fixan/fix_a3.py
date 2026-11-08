"""fix_a3: checks of the activated-escape reading of the E4 escape data (Sect. 5.4).

Inputs (all existing; no dynamics is run):
  data/E4/e4_escape.jsonl, data/derived/E4_analysis.json   escape times, fitted rates and attempt rates
  data/BAR/gate.jsonl                                       accepted saddles (all mobile coordinates)
  data/E1/library/<tag>.pkl                                 snapshots (rest-state field of experiments/BAR/bar.py)
  data/derived/E3_analysis.json, selection.json, E6_analysis.json, E7b_analysis.json   counts and keys
Output: data/derived/fix_a3.json

Parts
  langer        Hessians of the BAR rest-state potential U (central finite differences of U, h = 1e-5 m) at
                the relaxed minimum and at the accepted climbing-image saddle, per E4 snapshot and condition.
                Hessians are not stored by BAR or the gate; they are computed here from the stored saddle
                coordinates and the same U (a static evaluation). Dynamics near rest (C1, no contact):
                m x'' = -grad U - (m / tau_i) x', so the multidimensional Kramers-Langer rate is
                  k = nu_L exp(-dU / kT),  nu_L = (lambda_+ / 2 pi) sqrt(det H_min / |det H_sad|),
                lambda_+ the positive root of det(lambda^2 M + lambda Gamma + H_sad) = 0, M = m I,
                Gamma = diag(m / tau_i). Also the overdamped limit (lambda_+ = largest eigenvalue of
                -Gamma^-1 H_sad) and the inertial transition-state value (lambda_+ -> omega_u).
                nu_L is compared with the attempt rate nu_hat of E4_analysis (slope held at -dU).
  participation unstable eigenvector of H_sad in the full condition (equal masses, so mass weighting does
                not change it): agent weights p_i = |e_i|^2, participation ratio PR = 1 / sum p_i^2
                (1 = one agent moves, n = all move equally), blocker weight p_b; the same for the
                displacement from the minimum to the saddle.
  lag           shifted exponential: hazard 0 before a lag t0 shared by all (snapshot, condition, level)
                groups, constant after it with one rate per group; and the pooled Weibull shape of the
                times left-truncated at t0 (runs still trapped at t0, times t - t0), as a function of t0.
  collapse      ln lambda against x = dU / kT_eff over the 84 fitted (snapshot, condition, level) points,
                weights = events: (a) one slope and one intercept for all points, (b) one slope and a free
                intercept per (snapshot, condition); 95% intervals from 2000 bootstrap resamples of snapshots.
  counts        E3 OLS slope, censoring, competing exits, selection counts, saddle ratios, pair and lone
                barrier summaries, read from the existing JSONs and checked against the raw records.
"""
import json
import math
import os
import pickle
import sys
from collections import defaultdict

import numpy as np
from scipy import optimize, stats

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "BAR"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "E3"))
import bar  # noqa: E402  (imports the simulator; changes cwd to code/)
from survival import weibull_pool  # noqa: E402

D = os.path.join(ROOT, "data")
DER = os.path.join(D, "derived")
OUT = os.path.join(DER, "fix_a3.json")
SEED = 20261109
N_BOOT = 2000
CONDS = ("full", "frozen", "alone")
LEVELS = (1.5, 2.5, 3.5)
H_FD = 1e-5


def jl(p):
    return [json.loads(x) for x in open(p)]


def jload(name):
    return json.load(open(os.path.join(DER, name)))


def med(v):
    return float(np.median(v)) if len(v) else None


def rng_(v):
    return [float(min(v)), float(max(v))] if len(v) else None


# ---------------------------------------------------------------- Hessians, Langer, participation
def hessian(f, X, h=H_FD):
    n = len(X)
    H = np.zeros((n, n))
    E = np.eye(n) * h
    for i in range(n):
        for j in range(i, n):
            v = (f.U(X + E[i] + E[j]) - f.U(X + E[i] - E[j]) - f.U(X - E[i] + E[j]) + f.U(X - E[i] - E[j])) / (4 * h * h)
            H[i, j] = H[j, i] = v
    return H


def langer(Hm, Hs, m, tau):
    n = len(Hm)
    mm = np.repeat(m, 2)
    gam = np.repeat(m / tau, 2)
    em, es = np.linalg.eigvalsh(Hm), np.linalg.eigvalsh(Hs)
    out = {"n_coords": n, "eig_min_N_per_m": em.tolist(), "eig_saddle_N_per_m": es.tolist(),
           "n_negative_saddle": int((es < 0).sum()), "n_nonpositive_min": int((em <= 0).sum())}
    if (em <= 0).any() or (es < 0).sum() != 1:
        out["valid"] = False
        return out, None
    A = np.block([[np.zeros((n, n)), np.eye(n)], [-Hs / mm[:, None], -np.diag(gam / mm)]])
    w, V = np.linalg.eig(A)
    k = int(np.argmax(w.real))
    lam_p = float(w[k].real)
    vec = V[:n, k].real
    vec /= np.linalg.norm(vec)
    lam_od = float(np.max(np.linalg.eigvals(-Hs / gam[:, None]).real))
    ku = float(es[0])
    omega_u = math.sqrt(-ku / mm[0])
    root = math.sqrt(np.prod(em / np.abs(es)))      # sqrt(det H_min / |det H_sad|), dimensionless
    out.update({"valid": True, "kappa_u_N_per_m": ku, "lambda_plus_s": lam_p, "lambda_overdamped_s": lam_od,
                "omega_u_s": omega_u, "sqrt_det_ratio": root,
                "nu_langer": lam_p / (2 * math.pi) * root,
                "nu_overdamped": lam_od / (2 * math.pi) * root,
                "nu_tst": omega_u / (2 * math.pi) * root,
                "omega_min_slowest_s": float(math.sqrt(em[0] / mm[0])),
                "gamma_blocker_s": float(1 / tau[0]),
                "damping_ratio_unstable": float((1 / tau[0]) / (2 * omega_u))})
    return out, vec


def participation(vec):
    p = (vec.reshape(-1, 2) ** 2).sum(1)
    p = p / p.sum()
    return {"weights": p.tolist(), "pr": float(1 / (p ** 2).sum()), "blocker_weight": float(p[0]),
            "n_agents": int(len(p))}


def part_langer(E4, sel):
    G = {r["job_id"]: r for r in jl(os.path.join(D, "BAR", "gate.jsonl"))}
    rows = {}
    for tag, s in E4["snapshots"].items():
        g = G[tag]
        snap = pickle.load(open(os.path.join(ROOT, sel[tag]["snap"]), "rb"))
        st = snap["state"]
        b = g["blocker"]
        others = [i for i in g["resid"] if i != b]
        xb = st.positions[b].copy()
        fields = {"alone": bar.Field(snap, [b], [], rho_mode="zero"),
                  "frozen": bar.Field(snap, [b], others),
                  "full": bar.Field(snap, [b] + others, [])}
        mob = {"alone": [b], "frozen": [b], "full": [b] + others}
        r = {"n_resid": len(g["resid"])}
        for c in CONDS:
            gc = g[c]
            f = fields[c]
            X0 = xb.copy() if c != "full" else st.positions[[b] + others].ravel()
            XA = bar.relax(f, X0)
            n = gc["resolution_pair"][1]
            Xs = np.array(gc["n%d" % n]["saddle"])
            dU = f.U(Xs) - f.U(XA)
            Hm, Hs = hessian(f, XA), hessian(f, Xs)
            Hs_check = hessian(f, Xs, h=1e-4)
            lg, vec = langer(Hm, Hs, st.masses[mob[c]], st.taus[mob[c]])
            lg.update({"accepted": bool(gc["accepted"]), "dU_recomputed": float(dU), "dU_gate": float(gc["dU"]),
                       "hessian_fd_rel_change_h1e-4": float(np.max(np.abs(Hs_check - Hs)) / np.max(np.abs(Hs)))})
            arr = s["conds"].get(c, {}).get("arrhenius") if c in s["conds"] else None
            lg["nu_hat"] = arr["nu_hat"] if arr else None
            lg["nu_free"] = arr["nu_free"] if arr else None
            lg["nu_hat_over_langer"] = (arr["nu_hat"] / lg["nu_langer"]) if (arr and lg.get("valid")) else None
            if c == "full" and vec is not None:
                ev = np.linalg.eigh(Hs)[1][:, 0]
                lg["unstable_mode_hessian"] = participation(ev)
                lg["unstable_mode_dynamic"] = participation(vec)
                dx = Xs - XA
                lg["displacement_min_to_saddle"] = participation(dx / np.linalg.norm(dx))
                lg["displacement_min_to_saddle"]["others_max_m"] = float(
                    np.max(np.linalg.norm(dx.reshape(-1, 2)[1:], axis=1))) if others else 0.0
            r[c] = lg
        rows[tag] = r
    return rows


# ---------------------------------------------------------------- lag / shifted exponential
def groups_of(R, conds=CONDS):
    by = defaultdict(list)
    for x in R:
        if x["cond"] in conds:
            by[(x["snap"][:-4], x["cond"], x["beta_ref"])].append(x)
    G = {}
    for k, rows in by.items():
        t = np.array([r["t_run"] for r in rows])
        c = np.array([r["censored"] for r in rows], bool)
        if (~c).sum() > 0:
            G[k] = (t, c)
    return G


def ll_shiftexp(t0, G):
    ll = 0.0
    for t, c in G:
        d = (~c).sum()
        S = np.sum(t - t0)
        ll += d * (math.log(d) - math.log(S) - 1)
    return ll


def truncate(G, t0):
    out = []
    for t, c in G:
        m = t > t0
        tt, cc = t[m] - t0, c[m]
        if (~cc).sum() > 0:
            out.append((np.maximum(tt, 1e-3), cc))
    return out


def lag_part(R, rng):
    out = {}
    for name, conds in (("all", CONDS), ("full", ("full",)), ("frozen", ("frozen",)), ("alone", ("alone",))):
        Gd = groups_of(R, conds)
        G = list(Gd.values())
        tmin = float(min(t[~c].min() for t, c in G))
        tall = float(min(t.min() for t, c in G))
        t0max = min(tmin, tall) - 1e-9
        # shifted exponential: profile log-likelihood in t0, increasing up to the earliest time
        grid = np.linspace(0, t0max, 200)
        prof = np.array([ll_shiftexp(x, G) for x in grid])
        llmax = prof[-1]
        lo_idx = np.where(prof >= llmax - stats.chi2.ppf(0.95, 1) / 2)[0][0]
        w0 = weibull_pool(G)
        # Weibull log-likelihood (scales profiled) at its MLE, for the comparison with the shifted exponential
        def wll(k):
            ll = 0.0
            for t, c in G:
                t = np.maximum(t, 1e-3)
                e = ~c
                d = e.sum()
                ll += d * math.log(k) - d * math.log(np.sum(t ** k) / d) + (k - 1) * np.log(t[e]).sum() - d
            return ll
        ll_w = wll(w0["k"])
        ll_e = wll(1.0)
        # left-truncated Weibull shape against the lag, on a 0.25 s grid
        kt = []
        for L in np.arange(0.0, 15.0 + 1e-9, 0.25):
            Gt = truncate(G, float(L))
            w = weibull_pool(Gt)
            kt.append({"t0_s": float(L), "k": w["k"], "ci95": w["ci95"], "events": w["events"], "groups": w["groups"],
                       "runs_kept": int(sum(len(t) for t, _ in Gt))})
        cov = [x["ci95"][0] <= 1 <= x["ci95"][1] for x in kt]
        first_cover = next((x["t0_s"] for x, c in zip(kt, cov) if c), None)
        stable = None
        for i in range(len(kt)):
            if all(cov[i:]):
                stable = kt[i]["t0_s"]
                break
        at = lambda L: next(x for x in kt if abs(x["t0_s"] - L) < 1e-9)  # noqa: E731
        w_mle = weibull_pool(truncate(G, t0max))
        out[name] = {
            "groups": len(G), "events": int(sum((~c).sum() for _, c in G)),
            "earliest_escape_s": tmin,
            "shifted_exponential": {
                "t0_mle_s": float(grid[-1]), "t0_ci95_s": [float(grid[lo_idx]), float(grid[-1])],
                "loglik": float(llmax), "loglik_t0_0": float(prof[0]),
                "method": "hazard 0 before a lag t0 shared by all groups, then constant with one rate per group; "
                          "the likelihood rises with t0 up to the earliest observed escape, so the MLE sits on that "
                          "boundary; interval = t0 with log-likelihood within 1.92 of the maximum"},
            "shape_at_t0_mle": {"k": w_mle["k"], "ci95": w_mle["ci95"]},
            "weibull_unshifted": {"k": w0["k"], "ci95": w0["ci95"], "loglik": float(ll_w),
                                  "loglik_exponential": float(ll_e)},
            "aic_shiftexp_minus_weibull": float(2 * (ll_w - llmax)),
            "shape_at_1s": at(1.0), "shape_at_2s": at(2.0), "shape_at_5s": at(5.0), "shape_at_10s": at(10.0),
            "lag_first_cover_1_s": first_cover,
            "lag_cover_1_from_s": stable,
            "shape_vs_lag": kt,
            "method": "pooled Weibull shape (one shape, a scale per (snapshot, condition, level) group) of the "
                      "runs still trapped at t0, times measured from t0, on a 0.25 s grid of t0; 95% "
                      "profile-likelihood intervals; first_cover = smallest t0 whose interval contains 1, "
                      "cover_from = smallest t0 from which every larger grid t0 contains 1 (up to 15 s)",
        }
    return out


# ---------------------------------------------------------------- collapse
def wls(x, y, w):
    W = w.sum()
    xm, ym = (w * x).sum() / W, (w * y).sum() / W
    s = (w * (x - xm) * (y - ym)).sum() / (w * (x - xm) ** 2).sum()
    return s, ym - s * xm


def collapse_part(E4, rng):
    P = E4["collapse"]
    nu = {(t, c): E4["snapshots"][t]["conds"][c]["arrhenius"]["nu_hat"] for t, c in {(p["tag"], p["cond"]) for p in P}}
    tag = np.array([p["tag"] for p in P])
    unit = np.array([p["tag"] + "|" + p["cond"] for p in P])
    cond = np.array([p["cond"] for p in P])
    x = np.array([p["x"] for p in P])
    y = np.array([p["y"] for p in P])
    w = np.array([p["events"] for p in P], float)
    lnlam = y + np.array([math.log(nu[(p["tag"], p["cond"])]) for p in P])

    def fe_slope(idx):
        u = unit[idx]
        xx, yy, ww = x[idx], lnlam[idx], w[idx]
        xd, yd = xx.copy(), yy.copy()
        for k in np.unique(u):
            m = u == k
            xd[m] -= np.average(xx[m], weights=ww[m])
            yd[m] -= np.average(yy[m], weights=ww[m])
        return float((ww * xd * yd).sum() / (ww * xd * xd).sum())

    def fits(idx):
        s1, a1 = wls(x[idx], lnlam[idx], w[idx])
        s0, a0 = wls(x[idx], y[idx], w[idx])
        return s1, a1, fe_slope(idx), s0, a0

    allidx = np.arange(len(P))
    s1, a1, sfe, s0, a0 = fits(allidx)
    tags = np.unique(tag)
    B = []
    for _ in range(N_BOOT):
        pick = rng.choice(tags, len(tags), replace=True)
        idx = np.concatenate([np.where(tag == t)[0] for t in pick])
        if len(np.unique(x[idx])) < 2:
            continue
        B.append(fits(idx))
    B = np.array(B)
    ci = lambda j: [float(np.percentile(B[:, j], 2.5)), float(np.percentile(B[:, j], 97.5))]  # noqa: E731
    out = {
        "n_points": len(P), "n_units": int(len(np.unique(unit))), "n_snapshots": int(len(tags)),
        "x_values": sorted({round(v, 6) for v in x}),
        "published_collapse": {"slope": float(s0), "slope_ci95": ci(3), "intercept": float(a0),
                               "intercept_ci95": ci(4),
                               "method": "WLS of ln(lambda / nu_hat) on dU/kT (the paper's collapse), nu_hat fitted "
                                         "per (snapshot, condition) with the slope held at -1, so the intercept is "
                                         "near 0 by construction; snapshot bootstrap"},
        "common_intercept": {"slope": float(s1), "slope_ci95": ci(0), "intercept_ln_nu": float(a1),
                             "intercept_ln_nu_ci95": ci(1), "nu_common": math.exp(a1),
                             "nu_common_ci95": [math.exp(v) for v in ci(1)],
                             "method": "WLS of ln lambda on dU/kT with one slope and one intercept for all points "
                                       "(no per-snapshot attempt rate), weights = events; snapshot bootstrap"},
        "free_intercepts": {"slope": float(sfe), "slope_ci95": ci(2),
                            "method": "WLS of ln lambda on dU/kT with one slope and a free intercept per "
                                      "(snapshot, condition), weights = events; snapshot bootstrap"},
        "boot_n": int(len(B)),
    }
    per = {}
    for c in CONDS:
        m = cond == c
        per[c] = {"common_intercept_slope": float(wls(x[m], lnlam[m], w[m])[0]),
                  "free_intercepts_slope": fe_slope(np.where(m)[0]), "n_points": int(m.sum())}
    out["per_condition"] = per
    return out


# ---------------------------------------------------------------- counts
def counts_part(E4, E3, sel, R4, R3):
    out = {}
    sl = E3["ell"]["per_step"]["slope_ols"]
    out["e3_ols"] = {"slope": sl["slope"], "ci95": sl["slope_ci95_boot"], "intercept": sl["intercept"],
                     "through_origin": E3["ell"]["per_step"]["slope_origin"]["slope"],
                     "through_origin_ci95": E3["ell"]["per_step"]["slope_origin"]["ci95_boot"],
                     "n_snapshots": E3["ell"]["per_step"]["n"],
                     "method": "E3_analysis.json ell.per_step.slope_ols (OLS of observed on predicted ell, "
                               "bootstrap over snapshots)"}
    cps = E3["censoring"]["per_step"]
    c3 = sum(r["censored"] for r in R3 if r["mode"] == "per_step" and abs(r["dt"] - 0.02) < 1e-9)
    n3 = sum(1 for r in R3 if r["mode"] == "per_step" and abs(r["dt"] - 0.02) < 1e-9)
    out["e3_censoring"] = {"per_step_dt0p02_frac": cps["dt0p02"]["frac"], "per_step_dt0p02_censored": cps["dt0p02"]["censored"],
                           "per_step_dt0p02_n": cps["dt0p02"]["n"], "per_step_dt0p02_per_snapshot_max": cps["dt0p02"]["per_snapshot_max"],
                           "per_step_dt0p02_pct": 100 * cps["dt0p02"]["frac"],
                           "per_step_dt0p02_per_snapshot_max_pct": 100 * cps["dt0p02"]["per_snapshot_max"],
                           "raw_check_censored": int(c3), "raw_check_n": int(n3),
                           "all_cells_censored": int(sum(r["censored"] for r in R3)), "all_cells_n": len(R3),
                           "all_cells_frac": float(np.mean([r["censored"] for r in R3]))}
    cens4 = {c: [r["censored"] for r in R4 if r["cond"] == c] for c in CONDS}
    out["e4_censoring"] = {c: {"censored": int(sum(v)), "n": len(v), "frac": float(np.mean(v)), "pct": 100 * float(np.mean(v))}
                          for c, v in cens4.items()}
    out["e4_censoring"]["all"] = {"censored": int(sum(r["censored"] for r in R4)), "n": len(R4),
                                  "frac": float(np.mean([r["censored"] for r in R4])),
                                  "pct": 100 * float(np.mean([r["censored"] for r in R4]))}
    oe4 = [r for r in R4 if r["other_exit_first"]]
    oe3 = [r for r in R3 if r["other_exit_first"]]
    full4 = [r for r in R4 if r["cond"] == "full"]
    full4_fit = [r for r in full4 if r["snap"][:-4] not in ("E1b_seed170",)]
    out["competing_exits"] = {
        "rule": "escape = blocker centre at x >= 10 (or the blocker leaves the simulation); another agent leaving "
                "first neither stops nor censors the run, it is only flagged (experiments/lib/runlib.py escape)",
        "e4_full_flagged": len(oe4), "e4_full_runs": len(full4),
        "e4_full_flagged_frac": len(oe4) / len(full4), "e4_full_flagged_pct": 100 * len(oe4) / len(full4),
        "e4_full_flagged_escaped": int(sum(not r["censored"] for r in oe4)),
        "e4_full_flagged_in_fitted": int(sum(r["other_exit_first"] for r in full4_fit)),
        "e3_flagged": len(oe3), "e3_runs": len(R3), "e3_flagged_frac": len(oe3) / len(R3),
        "e3_total_from_json": E3["other_exit_first_total"]}
    b = sel["BAR"]
    out["selection"] = {"gate_failed": len(b["gate_excluded"]), "gate_total": len(sel["E2"]["snapshots"]),
                        "gate_accepted": b["n"], "e3_used": sel["E3"]["n"], "e3_qualifying": sel["E3"]["n_qualifying"],
                        "e4_used": sel["E4"]["n"], "e4_qualifying": sel["E4"]["n_qualifying"],
                        "gate_failed_tags": [x["tag"] for x in b["gate_excluded"]],
                        "method": "selection.json: BAR.gate_excluded, BAR.n, E3.n / n_qualifying, E4.n / n_qualifying"}
    sad = {t: s["saddle"]["full_over_alone"] for t, s in E4["snapshots"].items()}
    fitted = [t for t, s in E4["snapshots"].items() if s["conds"].get("full", {}).get("arrhenius")]
    v8 = [sad[t] for t in fitted]
    out["saddle_ratio"] = {"median_all": med(list(sad.values())), "n_all": len(sad),
                           "median_fitted": med(v8), "n_fitted": len(v8), "range_fitted": rng_(v8),
                           "fitted_tags": fitted,
                           "method": "dU_full / dU_alone per E4 snapshot; 'fitted' = snapshots with a full-condition "
                                     "Arrhenius fit (seed60 and seed170 have none)"}
    E7 = jload("E7b_analysis.json")["d_barriers"]
    rows = E7["rows"]
    every = [all(l["beta_dU"] < 1 for l in r["levels"]) for r in rows]
    out["pair"] = {"n": E7["accepted"], "dU_min": E7["dU"]["min"], "dU_max": E7["dU"]["max"], "dU_median": E7["dU"]["median"],
                   "below1_every_level": int(sum(every)), "n_levels": len(rows[0]["levels"]),
                   "sigma_levels": [l["sigma"] for l in rows[0]["levels"]],
                   "method": "E7b_analysis.json d_barriers; count of snapshots with dU/kT < 1 at every sigma level"}
    E6 = jload("E6_analysis.json")["lifetimes"]["barrier_picture"]
    lone = [r["dU"] for r in E6["rows"]]
    out["lone"] = {"n": E6["n_barriers"], "dU_median": E6["dU_median"], "n_le_1p1J": int(sum(v <= 1.1 for v in lone)),
                   "n_ge_3J": int(sum(v >= 3 for v in lone)),
                   "selection_p50": sel["BAR"]["dU_all_mobile_J"]["p50"],
                   "method": "E6_analysis.json lifetimes.barrier_picture (56 accepted library barriers, all mobile)"}
    return out


def main():
    rng = np.random.default_rng(SEED)
    E4, E3 = jload("E4_analysis.json"), jload("E3_analysis.json")
    selj = jload("selection.json")
    sel = {s["tag"]: s for s in selj["E4"]["snapshots"]}
    R4 = jl(os.path.join(D, "E4", "e4_escape.jsonl"))
    R3 = jl(os.path.join(D, "E3", "e3_dt.jsonl"))

    L = part_langer(E4, sel)
    summ = {}
    for c in CONDS:
        ok = [L[t][c] for t in L if L[t][c].get("valid")]
        fit = [x for x in ok if x["nu_hat"] is not None]
        summ[c] = {"n_valid": len(ok), "n_with_nu_hat": len(fit),
                   "nu_langer_median": med([x["nu_langer"] for x in fit]),
                   "nu_langer_range": rng_([x["nu_langer"] for x in fit]),
                   "nu_overdamped_median": med([x["nu_overdamped"] for x in fit]),
                   "nu_tst_median": med([x["nu_tst"] for x in fit]),
                   "nu_hat_median": med([x["nu_hat"] for x in fit]),
                   "ratio_nu_hat_over_langer_median": med([x["nu_hat_over_langer"] for x in fit]),
                   "ratio_nu_hat_over_langer_range": rng_([x["nu_hat_over_langer"] for x in fit]),
                   "lambda_plus_median": med([x["lambda_plus_s"] for x in fit]),
                   "sqrt_det_ratio_median": med([x["sqrt_det_ratio"] for x in fit]),
                   "damping_ratio_median": med([x["damping_ratio_unstable"] for x in fit]),
                   "dU_recompute_max_abs_err_J": float(max(abs(x["dU_recomputed"] - x["dU_gate"]) for x in ok)) if ok else None}
        r = [math.log(x["nu_hat_over_langer"]) for x in fit]
        if r:
            bs = [np.median(rng.choice(r, len(r))) for _ in range(N_BOOT)]
            summ[c]["ratio_median_ci95"] = [math.exp(np.percentile(bs, 2.5)), math.exp(np.percentile(bs, 97.5))]
    allfit = [L[t][c] for t in L for c in CONDS if L[t][c].get("valid") and L[t][c]["nu_hat"] is not None]
    summ["all"] = {"n": len(allfit), "ratio_nu_hat_over_langer_median": med([x["nu_hat_over_langer"] for x in allfit]),
                   "ratio_range": rng_([x["nu_hat_over_langer"] for x in allfit]),
                   "nu_langer_median": med([x["nu_langer"] for x in allfit]),
                   "n_ratio_below_1": int(sum(x["nu_hat_over_langer"] < 1 for x in allfit))}
    invalid = [{"tag": t, "cond": c, "n_negative_saddle": L[t][c]["n_negative_saddle"],
                "n_nonpositive_min": L[t][c]["n_nonpositive_min"]} for t in L for c in CONDS if not L[t][c].get("valid")]

    pr_rows = {t: {"n_agents": L[t]["n_resid"],
                   "pr_hessian": L[t]["full"]["unstable_mode_hessian"]["pr"],
                   "blocker_weight_hessian": L[t]["full"]["unstable_mode_hessian"]["blocker_weight"],
                   "pr_dynamic": L[t]["full"]["unstable_mode_dynamic"]["pr"],
                   "blocker_weight_dynamic": L[t]["full"]["unstable_mode_dynamic"]["blocker_weight"],
                   "pr_displacement": L[t]["full"]["displacement_min_to_saddle"]["pr"],
                   "blocker_weight_displacement": L[t]["full"]["displacement_min_to_saddle"]["blocker_weight"],
                   "others_max_displacement_m": L[t]["full"]["displacement_min_to_saddle"]["others_max_m"]}
               for t in L if "unstable_mode_hessian" in L[t]["full"]}
    fitted = [t for t, s in E4["snapshots"].items() if s["conds"].get("full", {}).get("arrhenius")]

    def prsum(keys):
        v = [pr_rows[t] for t in keys if t in pr_rows]
        return {"n": len(v),
                "pr_hessian_median": med([x["pr_hessian"] for x in v]), "pr_hessian_range": rng_([x["pr_hessian"] for x in v]),
                "blocker_weight_hessian_median": med([x["blocker_weight_hessian"] for x in v]),
                "blocker_weight_hessian_range": rng_([x["blocker_weight_hessian"] for x in v]),
                "neighbour_weight_hessian_median": med([1 - x["blocker_weight_hessian"] for x in v]),
                "pr_displacement_median": med([x["pr_displacement"] for x in v]),
                "blocker_weight_displacement_median": med([x["blocker_weight_displacement"] for x in v]),
                "neighbour_weight_displacement_median": med([1 - x["blocker_weight_displacement"] for x in v]),
                "neighbour_weight_displacement_range": rng_([1 - x["blocker_weight_displacement"] for x in v]),
                "n_agents_median": med([x["n_agents"] for x in v])}

    out = {
        "script": "experiments/fixan/fix_a3.py", "seed": SEED,
        "langer": {"per_snapshot": L, "summary": summ, "invalid": invalid,
                   "method": "nu_L = (lambda_+/2pi) sqrt(det H_min/|det H_sad|), lambda_+ the positive root of "
                             "det(lambda^2 m I + lambda diag(m/tau_i) + H_sad) = 0; Hessians by central finite "
                             "differences of the BAR rest-state U at the relaxed minimum and the accepted gate saddle; "
                             "compared with nu_hat of E4_analysis (attempt rate with slope held at -dU); ratio CI = "
                             "bootstrap of the median over (snapshot, condition) fits"},
        "participation": {"per_snapshot": pr_rows, "fitted": prsum(fitted), "all": prsum(list(pr_rows)),
                          "method": "unstable eigenvector of H_sad (full condition), agent weights p_i = |e_i|^2, "
                                    "PR = 1/sum p_i^2; also the dynamic unstable mode of the Langer matrix and the "
                                    "minimum-to-saddle displacement; 'fitted' = snapshots with a full Arrhenius fit"},
        "lag": lag_part(R4, rng),
        "collapse": collapse_part(E4, rng),
        "counts": counts_part(E4, E3, selj, R4, R3),
    }
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    s = out["langer"]["summary"]
    for c in CONDS + ("all",):
        print("langer", c, {k: v for k, v in s[c].items()})
    print("invalid", invalid)
    print("PR fitted", out["participation"]["fitted"])
    for k, v in out["lag"].items():
        print("lag", k, {kk: v[kk] for kk in ("earliest_escape_s", "shifted_exponential", "shape_at_t0_mle",
                                              "weibull_unshifted", "aic_shiftexp_minus_weibull",
                                              "lag_first_cover_1_s", "lag_cover_1_from_s")})
        print("   shape vs lag", [(x["t0_s"], round(x["k"], 3), [round(y, 3) for y in x["ci95"]]) for x in v["shape_vs_lag"][::4]])
    print("collapse", json.dumps(out["collapse"], indent=0)[:2000])
    print("counts", json.dumps(out["counts"], indent=0)[:3000])


if __name__ == "__main__":
    main()
