"""Task 2 analysis: alone-condition Arrhenius on the 56 barrier-set snapshots (data/revision7/T2/t2_alone.jsonl plus the
reused E4 and B3 cells, T2_alone.records).

Per snapshot (cells beta = 1.5, 2.5, 3.5, 5, 7; 20 restarts each, right-censored at the cell horizon):
  slope ratio r  censored-exponential likelihood prod lambda^d exp(-lambda E) (Poisson regression of the events d on
                 offset ln E), ln lambda = a - r beta, beta = dU_alone / k_B T_eff (the A3 estimator of rev2_A3);
                 95% interval by 1000 bootstrap resamples of the restarts within every cell (PCG64(2026)).
  attempt freq.  nu_hat = exp(event-weighted mean of ln lambda_cell + beta) (E4 definition, slope held at -dU), and
                 nu_free = exp(a) of the free fit.
  Hessians       A3_arrhenius.theory on the alone potential (bar.Field, rho 0): minimum x_min and saddle of
                 data/BAR/barriers.jsonl (alone), central differences; omega_0 = sqrt(mu_1 / m) and sqrt(mu_2 / m) at the
                 minimum, omega_b = sqrt(|H_sad,xx| / m) (as A3); gamma = 1 / tau_blocker; kappa (Kramers), A(Delta)
                 (Mel'nikov-Meshkov) and the exact 2-D k_TST per level.
  Langer         nu_L = (lambda_+ / 2 pi) sqrt(det H_min / |det H_sad|), lambda_+ = sqrt(gamma^2 / 4 + omega_u^2) - gamma / 2,
                 omega_u^2 = |negative eigenvalue of H_sad| / m
                 (the damped multidimensional Langer prefactor, as fix_a3). Predicted range of nu_hat / nu_L:
                 [min, max] over the five levels of A(Delta) (as rev2_A2, which used beta 1.5-3.5), and of the full
                 theory A kappa k_TST e^beta / nu_L (anharmonic TST included).
  Weibull        censored Weibull shape per cell with >= 10 events (survival.weibull_pool, one group).
Pooled: the same likelihood with one r and an intercept per snapshot, bootstrap as above; also without the three B3
snapshots (E1b seeds 72, 162, 192) and over the 10 E4 snapshots. Fits need >= 1 event in at least 3 levels.
Output: data/derived/rev7_T2.json"""
import json
import math
import os
import pickle
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import np  # noqa: E402
import T2_alone as T  # noqa: E402
sys.path.insert(0, os.path.join(L.ROOT, "experiments", "revision2"))
import A3_arrhenius as A3  # noqa: E402
import bar  # noqa: E402
from survival import weibull_pool  # noqa: E402

B3_TAGS = ("E1b_seed72", "E1b_seed162", "E1b_seed192")
NB = 1000
M = 80.0


def cells_of(R, tag):
    out = []
    for b in T.BETAS:
        rows = R.get((tag, b), [])
        if rows:
            t = np.array([r["t_run"] for r in rows], float)
            c = np.array([bool(r["censored"]) for r in rows])
            out.append({"beta": b, "t": t, "c": c, "n": len(rows)})
    return out


def fit(cells_by_snap, rng=None, nb=0):
    """cells_by_snap: list of cell lists. Returns r, intercepts, bootstrap interval."""
    S = len(cells_by_snap)
    flat = [(j, c) for j, cs in enumerate(cells_by_snap) for c in cs]
    X = np.array([[1.0 if j == k else 0.0 for k in range(S)] + [-c["beta"]] for j, c in flat])

    def de(idx=None):
        d = np.array([float((~(c["c"] if idx is None else c["c"][idx[i]])).sum()) for i, (j, c) in enumerate(flat)])
        E = np.array([float((c["t"] if idx is None else c["t"][idx[i]]).sum()) for i, (j, c) in enumerate(flat)])
        return d, E

    def solve(d, E):
        b = np.zeros(S + 1)
        for j in range(S):
            m = np.array([f[0] == j for f in flat])
            b[j] = math.log(max(d[m].sum(), 0.5) / E[m].sum()) + 3.0
        b[-1] = 1.0
        for _ in range(200):
            mu = E * np.exp(X @ b)
            g = X.T @ (d - mu)
            H = X.T @ (X * mu[:, None]) + 1e-12 * np.eye(S + 1)
            st = np.linalg.solve(H, g)
            b += np.clip(st, -5, 5)
            if np.max(np.abs(st)) < 1e-10:
                break
        return b
    d, E = de()
    b = solve(d, E)
    out = {"ratio": float(b[-1]), "intercepts": b[:-1].tolist(), "events": int(d.sum()), "restarts": int(sum(c["n"] for _, c in flat)),
           "censored": int(sum(c["c"].sum() for _, c in flat))}
    if nb:
        bs = []
        for _ in range(nb):
            idx = [rng.integers(0, c["n"], c["n"]) for _, c in flat]
            dd, EE = de(idx)
            ok = True
            for j in range(S):
                if dd[[f[0] == j for f in flat]].sum() == 0:
                    ok = False
            if ok:
                bs.append(solve(dd, EE)[-1])
        out["ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        out["n_boot"] = len(bs)
    return out


def main():
    S = T.snapshots()
    R = T.records()
    rows_bar = {json.loads(l)["job_id"]: json.loads(l) for l in open(os.path.join(L.DATA, "BAR", "barriers.jsonl"))}
    A3.BETAS = T.BETAS
    rng = np.random.Generator(np.random.PCG64(2026))
    per, fitted = {}, []
    for s in S:
        tag = s["tag"]
        cs = cells_of(R, tag)
        rec = {"class": s["class"], "n_resid": s["n_resid"], "dU": s["dU"], "tau": s["tau_b"], "in_E4": s["in_E4"],
               "in_B3": tag in B3_TAGS, "cells": []}
        for c in cs:
            d = int((~c["c"]).sum())
            Ecell = float(c["t"].sum())
            cell = {"beta": c["beta"], "n": c["n"], "events": d, "exposure_s": Ecell, "lam": d / Ecell,
                    "t_cens_max": float(c["t"].max()), "censored": int(c["c"].sum())}
            if d >= 10:
                w = weibull_pool([(c["t"], c["c"])])
                cell["weibull_k"], cell["weibull_ci95"] = w["k"], w["ci95"]
            rec["cells"].append(cell)
        ev = [c for c in rec["cells"] if c["events"] > 0]
        if len(ev) >= 3:
            f = fit([cs], rng, NB)
            rec["fit"] = f
            dd = np.array([c["events"] for c in ev], float)
            rec["nu_hat"] = math.exp(float((dd * (np.log([c["lam"] for c in ev]) + np.array([c["beta"] for c in ev]))).sum() / dd.sum()))
            rec["nu_free"] = math.exp(f["intercepts"][0])
            fitted.append(tag)
        snap = pickle.load(open(os.path.join(L.ROOT, "data", "E1", "library", tag + ".pkl"), "rb"))
        fld = bar.Field(snap, [s["blocker"]], [], rho_mode="zero")
        th = A3.theory(tag, s, fld, rows_bar[tag])
        g, wb = th["gamma"], th["omega_b"]
        em, es = th["Hmin_eig"], th["Hsad_eig"]
        wu = math.sqrt(abs(es[0]) / M)  # unstable eigenvalue of H_sad (fix_a3 definition)
        lam_p = math.sqrt(g * g / 4 + wu * wu) - g / 2
        nuL = lam_p / (2 * math.pi) * math.sqrt(em[0] * em[1] / abs(es[0] * es[1]))
        lv = th["levels"]
        Arng = [lv[f"{b:g}"]["A_mm"] for b in T.BETAS]
        full = [lv[f"{b:g}"]["lam"] * math.exp(b) / nuL for b in T.BETAS]
        rec.update({"omega_0": [math.sqrt(em[0] / M), math.sqrt(em[1] / M)], "omega_b": wb, "gamma": g,
                    "gamma_over_omega_b": g / wb, "kappa": th["kappa"], "nu_langer": nuL, "dU_theory": th["U_saddle_minus_min"],
                    "A_by_beta": dict(zip(map(str, T.BETAS), Arng)), "A_range": [min(Arng), max(Arng)],
                    "theory_over_langer_range": [min(full), max(full)],
                    "theory_ratio": float(-np.polyfit(T.BETAS, [math.log(lv[f"{b:g}"]["lam"]) for b in T.BETAS], 1)[0]),
                    "tst_ratio": float(-np.polyfit(T.BETAS, [math.log(lv[f"{b:g}"]["k_tst"]) for b in T.BETAS], 1)[0])})
        if "nu_hat" in rec:
            rec["nu_hat_over_langer"] = rec["nu_hat"] / nuL
            rec["inside_A_range"] = bool(rec["A_range"][0] <= rec["nu_hat_over_langer"] <= rec["A_range"][1])
            rec["inside_theory_range"] = bool(rec["theory_over_langer_range"][0] <= rec["nu_hat_over_langer"]
                                              <= rec["theory_over_langer_range"][1])
        per[tag] = rec
        print(tag, round(s["dU"], 2), "r", round(rec["fit"]["ratio"], 3) if "fit" in rec else None,
              rec.get("fit", {}).get("ci95"), "nu/nuL", round(rec.get("nu_hat_over_langer", float("nan")), 3),
              "g/wb %.2f" % rec["gamma_over_omega_b"], flush=True)
    out = {"doc": __doc__, "snapshots": per, "n_snapshots": len(S), "n_fitted": len(fitted)}

    def pooled(tags):
        return fit([cells_of(R, t) for t in tags], rng, NB)
    sets = {"all": fitted, "without_B3": [t for t in fitted if t not in B3_TAGS], "E4_ten": [t for t in fitted if per[t]["in_E4"]],
            "new_46": [t for t in fitted if not per[t]["in_E4"]]}
    for k, tags in sets.items():
        p = pooled(tags)
        r = [per[t]["fit"]["ratio"] for t in tags]
        nl = [per[t]["nu_hat_over_langer"] for t in tags]
        out[f"pooled_{k}"] = {**p, "n": len(tags), "ratio_median_per_snapshot": float(np.median(r)),
                              "ratio_range": [min(r), max(r)],
                              "n_ci_covers_1": int(sum(per[t]["fit"]["ci95"][0] <= 1 <= per[t]["fit"]["ci95"][1] for t in tags)),
                              "n_ci_covers_theory": int(sum(per[t]["fit"]["ci95"][0] <= per[t]["theory_ratio"] <= per[t]["fit"]["ci95"][1] for t in tags)),
                              "nu_over_langer_median": float(np.median(nl)), "nu_over_langer_range": [min(nl), max(nl)],
                              "n_inside_A_range": int(sum(per[t]["inside_A_range"] for t in tags)),
                              "n_inside_theory_range": int(sum(per[t]["inside_theory_range"] for t in tags)),
                              "gamma_over_omega_b_median": float(np.median([per[t]["gamma_over_omega_b"] for t in tags])),
                              "gamma_over_omega_b_range": [min(per[t]["gamma_over_omega_b"] for t in tags), max(per[t]["gamma_over_omega_b"] for t in tags)],
                              "theory_ratio_median": float(np.median([per[t]["theory_ratio"] for t in tags])),
                              "tst_ratio_median": float(np.median([per[t]["tst_ratio"] for t in tags]))}
        print(k, json.dumps({a: b for a, b in out[f"pooled_{k}"].items() if a != "intercepts"}, default=float))
    wk = [c["weibull_k"] for t in fitted for c in per[t]["cells"] if "weibull_k" in c and c["beta"] >= 5]
    out["weibull_beta5_7"] = {"n_cells": len(wk), "median": float(np.median(wk)) if wk else None,
                              "range": [min(wk), max(wk)] if wk else None}
    out["cap_censored_cells"] = [(t, c["beta"]) for t in per for c in per[t]["cells"] if c["t_cens_max"] >= T.T_CAP - 1]
    out["pooled_all"]["ratio"] = out["pooled_all"]["ratio"]
    print(L.out_json("T2", out))


if __name__ == "__main__":
    main()
