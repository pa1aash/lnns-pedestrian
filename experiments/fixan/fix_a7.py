"""A-7: CroMa comparison at w = 0.8 m (paper Sect. 7) with small-sample intervals.

Inputs (read only):
  data/E10/e10_croma.jsonl            per model run: cell, matched human run, N, t_end, complete, deadlock, npz name
  E10 raw trajectories (*.npz)        t, id, x, y at 25 Hz; directory from $E10_RAW, else data/E10/raw in this
                                      tree, else /Users/palaash/Developer/lnns-pedestrian/data/E10/raw
  data/ext/croma/*_w080_*.txt         the five CroMa 2021 runs (PeTrack export, 25 fps)
  data/derived/E10_analysis.json      cross-check only
Passage rule as in experiments/pilot/w28_croma.py: first frame with x >= x_e (x_e = 0 for CroMa, 10 for the
model), counted only if the track starts before the line.

Quantities (all intervals 95%):
  1 flow ratio model/human: ratio of mean flows (first to last passage) with a delta-method interval on the log
    ratio, Welch-Satterthwaite df; Fieller interval with the same df; ratio of geometric means (Welch t on logs);
    and a matched version: per human run, mean of its five model runs over the human flow, t on the logs (n = 5).
  2 longest gap on the log scale: geometric mean with a t interval of log values; ratio to humans (Welch t on logs);
    human mean, maximum and number of gaps > 2 s recomputed from the trajectories.
  3 flow over the 10-90% passage window: (a) of the passages observed in the run, (b) of the N agents in the run
    (only runs whose 90% passage is reached); t interval over runs and log-ratio interval to humans.
  4 time-lapse survival: pooled time lapses between successive passages, S(t) = fraction > t (plain) and
    Kaplan-Meier with the final open interval of an incomplete run (last passage to end of run) right-censored;
    per-run survival of the longest gap, with and without the final open interval.
  5 completion k/n with Wilson intervals.
  6 human run conditions (motivation h, start line-up, corridor length) and the unmatched track in 4D040.
Output: data/derived/fix_a7.json
"""
import glob
import json
import math
import os
import re

import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
IN = os.path.join(DATA, "E10", "e10_croma.jsonl")
CROMA = os.path.join(DATA, "ext", "croma")
E10 = os.path.join(DATA, "derived", "E10_analysis.json")
OUT = os.path.join(DATA, "derived", "fix_a7.json")
CELLS = ["C1_pub", "C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]
FPS = 25.0
Z = 1.959963984540054
RNG = np.random.default_rng(20261109)  # not used for any interval; kept for a fixed state
GRID = [float(v) for v in np.round(np.r_[np.arange(0.0, 2.0, 0.1), np.arange(2.0, 10.0, 0.25),
                                         np.arange(10.0, 60.0, 2.0), np.arange(60.0, 601.0, 20.0)], 4)]

# CroMa 2021 documentation (dataset page, DOI 10.34735/ped.2021.9; Boomers et al. 2023, Collective Dynamics 8):
# h = 0 normal ("move purposefully, but without haste"), h = 0.5 normal-hurried, h = 1 hurried ("moving briskly"),
# h = 2 full commitment ("pushes their way through"); at h = 2 participants lined up directly in front of the
# bottleneck, at lower levels they kept a marked 2 m semicircle in front of it clear before the start signal.
# Bottleneck length l takes two levels, 0.2 m and 2.0 m; the file code l021 is the short one (0.21 m).
MOTIV = {"h0": ("normal", 0.0, "2 m semicircle kept clear"),
         "h1": ("hurried", 1.0, "2 m semicircle kept clear"),
         "h2": ("full commitment", 2.0, "lined up directly at the bottleneck")}


def raw_dir():
    for d in (os.environ.get("E10_RAW"), os.path.join(DATA, "E10", "raw"),
              "/Users/palaash/Developer/lnns-pedestrian/data/E10/raw"):
        if d and os.path.isdir(d):
            return d
    raise SystemExit("E10 raw trajectories not found; set E10_RAW")


def first_crossings(ids, t, x, x_e):
    out = []
    for i in np.unique(ids):
        m = ids == i
        c = np.where(x[m] - x_e >= 0)[0]
        if len(c) and c[0] > 0:
            out.append(t[m][c[0]])
    return np.sort(np.asarray(out, float))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def tci(x):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    n = len(x)
    if n < 2:
        return {"n": n, "mean": float(x.mean()) if n else None, "ci95": [None, None]}
    m, s = float(x.mean()), float(x.std(ddof=1))
    h = float(stats.t.ppf(0.975, n - 1) * s / math.sqrt(n))
    return {"n": n, "mean": m, "sd": s, "ci95": [m - h, m + h], "min": float(x.min()), "max": float(x.max())}


def geo(x):
    lx = np.log(np.asarray(x, float))
    n = len(lx)
    m, s = float(lx.mean()), float(lx.std(ddof=1))
    h = float(stats.t.ppf(0.975, n - 1) * s / math.sqrt(n))
    return {"n": n, "geo_mean": math.exp(m), "ci95": [math.exp(m - h), math.exp(m + h)], "log_sd": s}


def welch_df(a, na, b, nb):
    return (a + b) ** 2 / (a * a / (na - 1) + b * b / (nb - 1))


def ratio_means(model, human):
    """Ratio of arithmetic means: delta method on the log ratio and Fieller, both with Welch df."""
    m, h = np.asarray(model, float), np.asarray(human, float)
    nm, nh = len(m), len(h)
    mm, mh = m.mean(), h.mean()
    vm, vh = m.var(ddof=1) / nm, h.var(ddof=1) / nh
    r = mm / mh
    a, b = vm / mm ** 2, vh / mh ** 2
    df = welch_df(a, nm, b, nh)
    t = stats.t.ppf(0.975, df)
    se = math.sqrt(a + b)
    log_ci = [r * math.exp(-t * se), r * math.exp(t * se)]
    A, B, C = mh ** 2 - t * t * vh, -2 * mm * mh, mm ** 2 - t * t * vm
    disc = B * B - 4 * A * C
    fieller = sorted([(-B - math.sqrt(disc)) / (2 * A), (-B + math.sqrt(disc)) / (2 * A)]) if A > 0 and disc >= 0 \
        else [None, None]
    lm, lh = np.log(m), np.log(h)
    am, ah = lm.var(ddof=1) / nm, lh.var(ddof=1) / nh
    dfg = welch_df(am, nm, ah, nh)
    tg = stats.t.ppf(0.975, dfg)
    g = math.exp(lm.mean() - lh.mean())
    sg = math.sqrt(am + ah)
    return {"n_model": nm, "n_human": nh, "ratio": float(r), "ci95": [float(v) for v in log_ci],
            "welch_df": float(df), "fieller_ci95": [float(v) if v is not None else None for v in fieller],
            "geo_ratio": float(g), "geo_ratio_ci95": [g * math.exp(-tg * sg), g * math.exp(tg * sg)],
            "geo_welch_df": float(dfg)}


def matched_ratio(model_rows, human_by_run, key):
    """Per human run: mean of the matched model runs over the human value; t interval of the logs over runs."""
    lr = []
    per = {}
    for run, hv in human_by_run.items():
        mv = [r[key] for r in model_rows if r["run"] == run and r[key] is not None]
        q = float(np.mean(mv)) / hv
        per[run] = q
        lr.append(math.log(q))
    lr = np.asarray(lr)
    n = len(lr)
    h = stats.t.ppf(0.975, n - 1) * lr.std(ddof=1) / math.sqrt(n)
    return {"n_human_runs": n, "geo_ratio": float(math.exp(lr.mean())),
            "ci95": [float(math.exp(lr.mean() - h)), float(math.exp(lr.mean() + h))], "per_run": per}


def window_flow(tp, n_agents, lo=0.1, hi=0.9):
    """(a) over the observed passages, (b) over the N agents (None if the hi passage is not reached)."""
    n = len(tp)
    a = b = None
    if n >= 3:
        ka, kb = int(round(lo * (n - 1))), int(round(hi * (n - 1)))
        if kb > ka and tp[kb] > tp[ka]:
            a = (kb - ka) / (tp[kb] - tp[ka])
    ka, kb = int(math.ceil(lo * n_agents)) - 1, int(math.ceil(hi * n_agents)) - 1
    if n > kb and tp[kb] > tp[ka]:
        b = (kb - ka) / (tp[kb] - tp[ka])
    return a, b


def km(times, events, grid):
    """Kaplan-Meier survival on a grid; events 1 = observed, 0 = right-censored."""
    t = np.asarray(times, float)
    e = np.asarray(events, int)
    ut = np.unique(t[e == 1])
    s, surv = 1.0, []
    steps = []
    for u in ut:
        at = (t >= u).sum()
        d = ((t == u) & (e == 1)).sum()
        s *= 1 - d / at
        steps.append((u, s))
    j, cur = 0, 1.0
    for g in grid:
        while j < len(steps) and steps[j][0] <= g:
            cur = steps[j][1]
            j += 1
        surv.append(float(cur))
    return surv


def ecdf_surv(x, grid):
    x = np.asarray(x, float)
    return [float((x > g).mean()) for g in grid]


def croma_run(path):
    d = np.loadtxt(path, comments="#", usecols=(0, 1, 2, 3))
    ids, fr, x, y = d[:, 0].astype(int), d[:, 1].astype(int), d[:, 2], d[:, 3]
    tp = first_crossings(ids, fr / FPS, x, 0.0)
    m = re.search(r"(4D\d{3})_w(\d{3})_l(\d{3})_(h\w+)", os.path.basename(path))
    un = []
    for i in np.unique(ids):
        k = ids == i
        c = np.where(x[k] >= 0)[0]
        if not (len(c) and c[0] > 0):
            # nearest other track at this track's last frame (track swap / duplicate check)
            lf = fr[k].max()
            s = (fr == lf) & (ids != i)
            dd = np.hypot(x[s] - x[k][-1], y[s] - y[k][-1])
            j = int(np.argmin(dd))
            un.append({"id": int(i), "first_s": float(fr[k].min() / FPS), "last_s": float(lf / FPS),
                       "x_last_m": float(x[k][-1]), "y_last_m": float(y[k][-1]),
                       "dist_to_line_m": float(-x[k][-1]), "nearest_other_id": int(ids[s][j]),
                       "nearest_other_dist_m": float(dd[j])})
    return {"run": m.group(1), "file": os.path.basename(path), "width_m": int(m.group(2)) / 100,
            "L": int(m.group(3)) / 100, "h": m.group(4), "N": int(len(np.unique(ids))),
            "t_end": float(fr.max() / FPS), "tp": tp, "complete": True, "unmatched": un}


def model_run(r, rd):
    D = np.load(os.path.join(rd, os.path.basename(r["npz"])))["data"]
    tp = first_crossings(D[:, 1].astype(int), D[:, 0], D[:, 2], 10.0)
    return {"run": r["run"], "N": r["N"], "t_end": float(r["t_end"]), "tp": tp, "complete": bool(r["complete"]),
            "deadlock": bool(r["deadlock"]), "est": r["estimator"], "seed": r["seed"]}


def per_run_stats(u):
    tp = u["tp"]
    g = np.diff(tp)
    a, b = window_flow(tp, u["N"])
    u.update({"n_pass": len(tp), "flow": (len(tp) - 1) / (tp[-1] - tp[0]), "gaps": g,
              "max_gap": float(g.max()), "n_gt2": int((g > 2.0).sum()), "flow_w_obs": a, "flow_w_N": b,
              "final_open": None if u["complete"] else float(u["t_end"] - tp[-1])})
    return u


def main():
    rd = raw_dir()
    H = [per_run_stats(croma_run(f)) for f in sorted(glob.glob(os.path.join(CROMA, "*_w080_*.txt")))]
    R = [json.loads(l) for l in open(IN) if l.strip()]
    M = {c: [per_run_stats(model_run(r, rd)) for r in R if r["cell"] == c] for c in CELLS}
    e10 = json.load(open(E10))

    # cross-check against the stored estimator output
    dev = max(max(abs(u["flow"] - u["est"]["flow_per_s"]), abs(u["max_gap"] - u["est"]["max_gap_s"]))
              for c in CELLS for u in M[c])
    hj = {h["file"]: h for h in e10["humans"]["runs"]}
    devh = max(max(abs(u["flow"] - hj[u["file"]]["flow_per_s"]), abs(u["max_gap"] - hj[u["file"]]["max_gap_s"]))
               for u in H)

    hflow = [u["flow"] for u in H]
    hgap = [u["max_gap"] for u in H]
    h_by_run_flow = {u["run"]: u["flow"] for u in H}
    h_by_run_gap = {u["run"]: u["max_gap"] for u in H}
    o = {"script": "experiments/fixan/fix_a7.py", "raw_dir": rd,
         "check": {"max_abs_dev_model_vs_E10_estimator": float(dev), "max_abs_dev_human_vs_E10": float(devh)},
         "method": {
             "flow": "passages through the entrance plane, (n-1)/(last-first) per run; Student-t 95% over runs",
             "flow_ratio": "ratio of mean flows model/human; 95% interval exp(log r +- t*se), se^2 = s_m^2/(n_m m_m^2)"
                           " + s_h^2/(n_h m_h^2), Welch-Satterthwaite df; Fieller interval with the same df; ratio "
                           "of geometric means with Welch t on log flows",
             "flow_ratio_matched": "per human run, mean flow of its 5 matched model runs over the human flow; "
                                   "geometric mean of the 5 ratios with a t interval (4 df) on the logs",
             "longest_gap": "longest time between successive passages per run; geometric mean with a t interval of"
                            " log values; ratio to humans with Welch t on logs",
             "window": "10-90% passage window: obs = passages k=round(0.1(n-1)) to round(0.9(n-1)) of the n observed"
                       " passages; N = passages ceil(0.1N) to ceil(0.9N) of the N agents, runs not reaching the "
                       "ceil(0.9N)-th passage excluded; flow = passages/time between them; t interval over runs; "
                       "ratio as flow_ratio",
             "survival": "pooled time lapses between successive passages; plain = fraction > t; km = Kaplan-Meier "
                         "with the final open interval of an incomplete run (last passage to end of run) "
                         "right-censored; runs_longest = fraction of runs whose longest gap > t (with_final: the "
                         "final open interval counted as a gap, a lower bound for incomplete runs)",
             "completion": "k of n runs with every agent through; Wilson 95% interval"},
         "humans": {}, "cells": {}, "survival": {"grid_s": GRID, "groups": {}}}

    # human block
    gaps_all = np.concatenate([u["gaps"] for u in H])
    o["humans"] = {
        "n_runs": len(H),
        "runs": [{"run": u["run"], "file": u["file"], "L_m": u["L"], "h_code": u["h"],
                  "motivation": MOTIV[u["h"]][0], "motivation_level_h": MOTIV[u["h"]][1],
                  "start_lineup": MOTIV[u["h"]][2], "N_tracks": u["N"], "n_pass": u["n_pass"],
                  "flow": u["flow"], "flow_w_obs": u["flow_w_obs"], "flow_w_N": u["flow_w_N"],
                  "max_gap_s": u["max_gap"], "n_gaps_gt_2s": u["n_gt2"]} for u in H],
        "flow": tci(hflow), "flow_geo": geo(hflow),
        "longest_gap": {**tci(hgap), "log": geo(hgap), "max": float(max(hgap)),
                        "max_run": H[int(np.argmax(hgap))]["run"]},
        "gaps_gt_2s_total": int(sum(u["n_gt2"] for u in H)),
        "gaps_gt_2s_runs": [u["run"] for u in H if u["n_gt2"] > 0],
        "n_gaps_total": int(len(gaps_all)),
        "window_obs": tci([u["flow_w_obs"] for u in H]), "window_N": tci([u["flow_w_N"] for u in H]),
        "by_motivation": {k: {"runs": [u["run"] for u in H if u["h"] == k],
                              "flow": [u["flow"] for u in H if u["h"] == k]} for k in ("h0", "h1", "h2")},
        "unmatched_tracks": {u["run"]: u["unmatched"] for u in H if u["unmatched"]},
        "notes": {
            "motivation": "file code h0 = normal, h1 = hurried, h2 = full commitment (CroMa 2021 dataset page, "
                          "DOI 10.34735/ped.2021.9; Boomers et al. 2023); at h2 participants lined up directly at "
                          "the bottleneck, otherwise a 2 m semicircle in front of it was kept clear at the start",
            "corridor": "the experiment varied the bottleneck length at two levels, 0.2 m and 2.0 m; the files of "
                        "the short level carry l021 (0.21 m), i.e. a door in a wall without a corridor behind it",
            "4D040": "136 tracks, 135 passages; track id 35 (marker 717, head height 1.57 m) is followed for 9.3 s "
                     "and ends 0.16 m before the entrance plane on top of track id 30 (0.005 m apart at its last "
                     "frame), which then passes; a lost or swapped track at the entrance, not a participant left "
                     "behind (no track remains in the holding area at the end of the run)"}}
    o["humans"]["window_obs_ratio_to_full"] = float(o["humans"]["window_obs"]["mean"] / o["humans"]["flow"]["mean"])

    sg = o["survival"]["groups"]
    sg["humans"] = {"n_runs": len(H), "n_lapses": int(len(gaps_all)), "n_censored": 0,
                    "plain": ecdf_surv(gaps_all, GRID), "km": ecdf_surv(gaps_all, GRID),
                    "runs_longest": ecdf_surv(hgap, GRID), "runs_longest_with_final": ecdf_surv(hgap, GRID)}

    for c in CELLS:
        X = M[c]
        n = len(X)
        k = sum(u["complete"] for u in X)
        fl = [u["flow"] for u in X]
        gp = [u["max_gap"] for u in X]
        wo = [u["flow_w_obs"] for u in X if u["flow_w_obs"] is not None]
        wn = [u["flow_w_N"] for u in X if u["flow_w_N"] is not None]
        hwo = [u["flow_w_obs"] for u in H]
        hwn = [u["flow_w_N"] for u in H]
        d = {"n": n, "complete": int(k), "completion_wilson95": wilson(k, n),
             "deadlock": int(sum(u["deadlock"] for u in X)),
             "capped": int(sum((not u["complete"]) and (not u["deadlock"]) for u in X)),
             "flow": tci(fl), "flow_geo": geo(fl),
             "flow_ratio": ratio_means(fl, hflow),
             "flow_ratio_matched": matched_ratio([{"run": u["run"], "f": u["flow"]} for u in X], h_by_run_flow, "f"),
             "flow_ratio_E10_bootstrap": e10["cells"][c]["flow_ratio_to_human"],
             "longest_gap": {**tci(gp), "log": geo(gp), "max": float(max(gp))},
             "longest_gap_ratio_log": {k2: v for k2, v in ratio_means(gp, hgap).items()
                                       if k2.startswith("geo") or k2.startswith("n_")},
             "gaps_gt_2s_per_run": tci([u["n_gt2"] for u in X]),
             "window_obs": {"flow": tci(wo), "ratio": ratio_means(wo, hwo),
                            "ratio_to_full_flow": float(np.mean(wo) / np.mean(fl))},
             "window_N": {"n_reached": len(wn), "flow": tci(wn) if len(wn) >= 2 else {"n": len(wn)},
                          "ratio": ratio_means(wn, hwn) if len(wn) >= 2 else None},
             "final_open_interval_incomplete": tci([u["final_open"] for u in X if u["final_open"] is not None])}
        o["cells"][c] = d
        lap, ev = [], []
        for u in X:
            lap += list(u["gaps"])
            ev += [1] * len(u["gaps"])
            if u["final_open"] is not None:
                lap.append(u["final_open"])
                ev.append(0)
        withf = [max(u["max_gap"], u["final_open"] or 0.0) for u in X]
        sg[c] = {"n_runs": n, "n_lapses": int(sum(ev)), "n_censored": int(len(ev) - sum(ev)),
                 "plain": ecdf_surv([v for v, e in zip(lap, ev) if e], GRID), "km": km(lap, ev, GRID),
                 "runs_longest": ecdf_surv(gp, GRID), "runs_longest_with_final": ecdf_surv(withf, GRID)}
        for th in (2.0, 5.0):
            j = GRID.index(th)
            d[f"lapse_frac_gt_{int(th)}s"] = sg[c]["plain"][j]
    for th in (2.0, 5.0):
        o["humans"][f"lapse_frac_gt_{int(th)}s"] = sg["humans"]["plain"][GRID.index(th)]

    with open(OUT, "w") as f:
        json.dump(o, f, indent=1, default=float)
    brief(o)


def brief(o):
    h = o["humans"]
    print("check", o["check"])
    print("humans flow", h["flow"]["mean"], h["flow"]["ci95"], "gap", h["longest_gap"]["mean"], h["longest_gap"]["max"],
          h["longest_gap"]["max_run"], "gaps>2", h["gaps_gt_2s_total"], "window obs", h["window_obs"]["mean"],
          h["window_obs"]["ci95"], "window N", h["window_N"]["mean"], h["window_N"]["ci95"])
    print("geo gap human", h["longest_gap"]["log"])
    for r in h["runs"]:
        print("  ", r["run"], r["h_code"], r["L_m"], round(r["flow"], 3), round(r["flow_w_obs"], 3), r["n_pass"], r["N_tracks"])
    print("unmatched", h["unmatched_tracks"])
    for c, d in o["cells"].items():
        fr = d["flow_ratio"]
        print(c, "k", d["complete"], [round(v, 3) for v in d["completion_wilson95"]],
              "flow", round(d["flow"]["mean"], 3), "ratio", round(fr["ratio"], 3), [round(v, 3) for v in fr["ci95"]],
              "fieller", [round(v, 3) for v in fr["fieller_ci95"]], "geo", round(fr["geo_ratio"], 3),
              [round(v, 3) for v in fr["geo_ratio_ci95"]], "matched", round(d["flow_ratio_matched"]["geo_ratio"], 3),
              [round(v, 3) for v in d["flow_ratio_matched"]["ci95"]])
        g = d["longest_gap"]["log"]
        print("    gap geo", round(g["geo_mean"], 2), [round(v, 2) for v in g["ci95"]], "ratio",
              round(d["longest_gap_ratio_log"]["geo_ratio"], 2),
              [round(v, 2) for v in d["longest_gap_ratio_log"]["geo_ratio_ci95"]])
        w = d["window_obs"]
        print("    window obs", round(w["flow"]["mean"], 3), [round(v, 3) for v in w["flow"]["ci95"]], "ratio",
              round(w["ratio"]["ratio"], 3), [round(v, 3) for v in w["ratio"]["ci95"]],
              "N-based reached", d["window_N"]["n_reached"],
              round(d["window_N"]["flow"].get("mean") or 0, 3),
              None if not d["window_N"]["ratio"] else [round(v, 3) for v in d["window_N"]["ratio"]["ci95"]],
              "lapse>2", round(d["lapse_frac_gt_2s"], 3))


if __name__ == "__main__":
    main()
