"""D: CroMa integrity check (paper Sect. 7): participants vs track IDs vs passages, corrected human numbers,
agent number and bottleneck length of the model runs, censored longest gap and flow ratios.

Inputs (read only):
  data/ext/croma/*_w080_*.txt      the five CroMa 2021 runs used in E10 (PeTrack text export, 25 fps;
                                   columns id, frame, x, y, z, markerID; entrance plane x = 0)
  data/E10/e10_croma.jsonl         model runs (cell, matched human run, N, L, seed, t_end, complete, deadlock)
  E10 raw trajectories (*.npz)     located by experiments/fixan/fix_a7.py raw_dir()
  data/derived/rev_A12.json        A12 values (comparison only)
  paper/numbers.tex                current macro values (comparison only)
  optional --archive-dir DIR       the archive's hdf5 release (2021bottleneck_trajectories_hdf5.zip, unpacked):
                                   per-run metadata (number_participants, wkt_geometry, notes) and the revised
                                   trajectories; used for the cross-run N-vs-track table and the 4D120 sensitivity.
Archive documentation (ARCHIVE below) was read on 2026-11-10 from: the run overview PDF
(ped.fz-juelich.de/experiments/2021.10.08_Duesseldorf_MEH_CroMa/data/2021bottleneck/2021bottleneck_run_overview.pdf;
start/end timecodes hh:mm:ss:ff at 25 fps, N, w, l, h, line-up), Boomers et al. 2023 (Collective Dynamics 8,
DOI 10.17815/CD.2023.141, Sect. 3.7 and App. A.9 Table 19: same N, w, l, h; note "mix up: first row queue behind" for
4D110), the hdf5 metadata (number_participants identical; wkt_geometry; notes) and the landing page
ped.fz-juelich.de/da/2021bottleneck (DOI 10.34735/ped.2021.9).

D1 per run: track IDs, distinct marker IDs (one marker per participant), duplicate tracks (two IDs carrying the same
marker at the same place), tracks starting after frame 0 or beyond the entrance, tracks ending before the entrance,
largest frame-to-frame step (ID-swap check), near-coincident pairs of distinct markers (merge check), frame range
against the documented run duration, start state (distance of the nearest head to the entrance centre, mean speed
in the first 2 s), passages by the E10 track rule (first frame with x >= 0 of a track that starts before the line;
one per track) and by the participant rule (the same, one per marker ID: duplicate tracks of one participant count
once). Two tests for passages missing from the file: (i) headway thinning: if N_archive participants passed and only
the tracked ones are in the file, about (N_archive - n)/N_archive of the observed headways would span two or more
true headways; statistic S = number of observed headways > 2 x median; Monte Carlo (20 000) of S under that
hypothesis (true headways resampled from the observed ones and rescaled to the observed duration, the untracked
passages placed at random); p = P(S_sim <= S_obs). (ii) crowd holes at frame 0: area inside the convex hull of the
heads (outside 2.2 m of the entrance centre) farther than 0.7 m from every head.
D2 human metrics with the E10 estimator (experiments/pilot/w28_croma.py, unchanged) on (a) the files as used,
(b) the files with duplicate tracks removed (keep the longer track of a duplicate pair, the lower ID on a tie);
flow = (n - 1)/(last - first passage), gaps > 2 s, longest gap, waiting-zone fluctuation, and the fix_a7 10-90%
window flow; means with Student-t 95% intervals over runs; by bottleneck length.
D3 agent numbers used by e10_croma.py against tracks / participants who passed / archive N; how L enters the model.
D4 per variant (C1_cf, C1_cf_edge, C3_rvo2_cf, C1_cf_sig): longest interior gap of completed runs; the final open gap
of every incomplete run right-censored at the 600 s horizon (deadlocked runs: the rest state is absorbing, so the
gap lasts at least to 600 s; capped runs end at 600 s): c = max(longest interior gap, 600 - last passage);
Kaplan-Meier median and restricted mean (A12's km_summary) and the median of c; flow ratio model/human with the
log-ratio Welch-t interval (fix_a7.ratio_means) and the matched ratio, with the corrected human flows; the E10
bootstrap ratios (experiments/E10/analyze.py ratio_ci, same RNG sequence) recomputed with the corrected humans.
Every number that changes against paper/numbers.tex (Eten*, FixAseven*) and rev_A12.json (RevAtwelve*) is listed.
Output: data/derived/rev_D.json.
"""
import argparse
import ast
import glob
import importlib.util
import json
import math
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
import numpy as np  # noqa: E402
from scipy.spatial import ConvexHull, Delaunay, cKDTree  # noqa: E402

import fix_a7 as F  # noqa: E402
import A12_croma as A12  # noqa: E402

ROOT = revlib.ROOT
FPS = 25.0
T_HOR = 600.0
CELLS = ["C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]
ALLC = ["C1_pub"] + CELLS
LABEL = A12.LABEL
sig = revlib.sig


def _load(name, rel):
    s = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


W28 = _load("w28_croma", "experiments/pilot/w28_croma.py")
E10A = _load("e10_analyze", "experiments/E10/analyze.py")

# Archive documentation, read 2026-11-10 (sources in the module docstring). Timecodes hh:mm:ss:ff at 25 fps.
ARCHIVE = {
    "4D030": {"N": 161, "w": 0.8, "l": 2.0, "h": "h0", "lineup": "2 m semi-circle", "start": "10:56:50:10",
              "end": "10:58:54:24", "note": None},
    "4D040": {"N": 160, "w": 0.8, "l": 2.0, "h": "h1", "lineup": "2 m semi-circle", "start": "11:00:10:23",
              "end": "11:01:47:24", "note": None},
    "4D110": {"N": 132, "w": 0.8, "l": 0.2, "h": "h0", "lineup": "2 m semi-circle", "start": "11:53:34:24",
              "end": "11:55:13:00", "note": "Table 19: mix up: first row queue behind"},
    "4D120": {"N": 132, "w": 0.8, "l": 0.2, "h": "h1", "lineup": "2 m semi-circle", "start": "11:56:17:08",
              "end": "11:57:43:08", "note": None},
    "4D130": {"N": 129, "w": 0.8, "l": 0.2, "h": "h2", "lineup": "directly at bottleneck", "start": "12:00:15:08",
              "end": "12:01:35:15", "note": "hdf5 metadata: Possibility was given for people to sit out the high "
                                            "motivation run."},
}
SOURCES = {"run_overview_pdf": "https://ped.fz-juelich.de/experiments/2021.10.08_Duesseldorf_MEH_CroMa/data/"
                               "2021bottleneck/2021bottleneck_run_overview.pdf",
           "guidance_paper": "Boomers et al. 2023, Collective Dynamics 8, DOI 10.17815/CD.2023.141, Sect. 3.7, "
                             "App. A.9, Table 19 (journal PDF collective-dynamics.eu/index.php/cod/article/download/"
                             "A141/238)",
           "landing_page": "https://ped.fz-juelich.de/da/2021bottleneck (DOI 10.34735/ped.2021.9)",
           "hdf5_release": "2021bottleneck_trajectories_hdf5.zip (metadata date_modified 2025-05-07, status "
                           "'data revised')",
           "fetched": "2026-11-10"}


def tc(s):
    h, m, sec, f = (int(v) for v in s.split(":"))
    return h * 3600 + m * 60 + sec + f / FPS


def read_txt(path):
    d = np.loadtxt(path, comments="#")
    return {"id": d[:, 0].astype(int), "fr": d[:, 1].astype(int), "x": d[:, 2], "y": d[:, 3], "z": d[:, 4],
            "mk": d[:, 5].astype(int)}


def subset(D, keep_ids):
    m = np.isin(D["id"], list(keep_ids))
    return {k: v[m] for k, v in D.items()}


def tracks(D):
    out = {}
    for i in np.unique(D["id"]):
        m = D["id"] == i
        out[int(i)] = {"fr": D["fr"][m], "x": D["x"][m], "y": D["y"][m], "mk": int(D["mk"][m][0]),
                       "z": float(D["z"][m][0])}
    return out


def first_cross(t):
    c = np.where(t["x"] >= 0)[0]
    return float(t["fr"][c[0]] / FPS) if len(c) and c[0] > 0 else None


def duplicates(T):
    """Tracks sharing a marker ID: overlap frames and median distance; the copy to drop (shorter, then higher ID)."""
    bym = defaultdict(list)
    for i, t in T.items():
        bym[t["mk"]].append(i)
    out = []
    for mk, ids in bym.items():
        if len(ids) < 2:
            continue
        ids = sorted(ids, key=lambda i: (-len(T[i]["fr"]), i))
        keep = ids[0]
        for j in ids[1:]:
            a, b = T[keep], T[j]
            com = np.intersect1d(a["fr"], b["fr"])
            ia, ib = np.isin(a["fr"], com), np.isin(b["fr"], com)
            d = np.hypot(a["x"][ia] - b["x"][ib], a["y"][ia] - b["y"][ib])
            out.append({"marker": mk, "keep": keep, "drop": j, "frames_keep": len(a["fr"]), "frames_drop": len(b["fr"]),
                        "overlap_frames": int(len(com)), "dist_median_m": float(np.median(d)) if len(d) else None,
                        "dist_max_m": float(d.max()) if len(d) else None,
                        "keep_passes_s": first_cross(a), "drop_passes_s": first_cross(b),
                        "drop_x_last_m": float(b["x"][-1])})
    return out


def near_pairs(D, r=0.1, min_frames=25):
    """Pairs of distinct marker IDs closer than r in at least min_frames frames (merge / mislabel check)."""
    cnt = defaultdict(int)
    for f in np.unique(D["fr"]):
        m = D["fr"] == f
        P = np.column_stack([D["x"][m], D["y"][m]])
        mk = D["mk"][m]
        for a, b in cKDTree(P).query_pairs(r):
            if mk[a] != mk[b]:
                cnt[tuple(sorted((int(mk[a]), int(mk[b]))))] += 1
    return {f"{a}-{b}": n for (a, b), n in cnt.items() if n >= min_frames}


def thinning_test(tp, n_arch, rng, n_sim=20000):
    tp = np.sort(tp)
    g = np.diff(tp)
    med = float(np.median(g))
    s_obs = int((g > 2 * med).sum())
    n = len(tp)
    miss = n_arch - n
    if miss <= 0:
        return {"S_obs": s_obs, "median_headway_s": med, "n_missing_hyp": 0}
    S = np.empty(n_sim, int)
    for k in range(n_sim):
        h = rng.choice(g, n_arch - 1) * (n - 1) / (n_arch - 1)   # true headways, same total duration on average
        t = np.r_[0.0, np.cumsum(h)]
        keep = np.sort(np.r_[0, n_arch - 1, 1 + rng.choice(n_arch - 2, n - 2, replace=False)])
        go = np.diff(t[keep])
        S[k] = int((go > 2 * np.median(go)).sum())
    return {"S_obs": s_obs, "median_headway_s": med, "n_missing_hyp": int(miss), "S_sim_mean": float(S.mean()),
            "S_sim_p2_5": float(np.percentile(S, 2.5)), "p_le_obs": float((S <= s_obs).mean()),
            "p_disp": revlib.pdisp(max((S <= s_obs).mean(), 1.0 / n_sim)), "n_sim": n_sim}


def crowd_holes(D):
    m = D["fr"] == 0
    P = np.column_stack([D["x"][m], D["y"][m]])
    hull = Delaunay(P[ConvexHull(P).vertices])
    xs, ys = np.meshgrid(np.arange(-12, 0, 0.05), np.arange(-7, 7, 0.05))
    G = np.column_stack([xs.ravel(), ys.ravel()])
    G = G[(hull.find_simplex(G) >= 0) & (np.hypot(G[:, 0], G[:, 1]) > 2.2)]
    d, _ = cKDTree(P).query(G)
    area = len(G) * 0.0025
    return {"n_frame0": int(len(P)), "hull_area_m2": float(area), "density_per_m2": float(len(P) / area),
            "hole_area_m2": float((d > 0.7).sum() * 0.0025), "x_min_frame0": float(P[:, 0].min())}


def human_metrics(D, run, L, n_persons):
    T = tracks(D)
    raw = {i: (t["fr"] / FPS, t["x"]) for i, t in T.items()}
    p = W28.passages(raw, 0.0)
    fl = W28.fluct(W28.tracks_from_rows(D["id"], D["fr"], D["x"], D["y"]), 0.0, 0.0)
    tp = np.sort([v for v in (first_cross(t) for t in T.values()) if v is not None])
    a, _ = F.window_flow(tp, n_persons)
    return {"run": run, "L": L, "n_tracks": len(T), "n_pass": p["n_pass"], "flow_per_s": p["flow_per_s"],
            "n_gaps_gt_2s": p["n_gaps_gt_2s"], "max_gap_s": p["max_gap_s"], "median_gap_s": p["median_gap_s"],
            "fluct": fl, "fluct_rms": E10A.fl({"fluct": fl}), "window_obs": a, "tp": tp}


def summarize_h(H):
    return {"flow": F.tci([h["flow_per_s"] for h in H]), "longest_gap": F.tci([h["max_gap_s"] for h in H]),
            "longest_gap_max": max(h["max_gap_s"] for h in H), "gaps_gt_2s_mean": float(np.mean([h["n_gaps_gt_2s"] for h in H])),
            "gaps_gt_2s_total": int(sum(h["n_gaps_gt_2s"] for h in H)),
            "fluct": F.tci([h["fluct_rms"] for h in H]), "window_obs": F.tci([h["window_obs"] for h in H]),
            "flow_range": [min(h["flow_per_s"] for h in H), max(h["flow_per_s"] for h in H)],
            "flow_long": float(np.mean([h["flow_per_s"] for h in H if h["L"] > 1])),
            "flow_short": float(np.mean([h["flow_per_s"] for h in H if h["L"] < 1])),
            "longest_gap_geo": F.geo([h["max_gap_s"] for h in H])}


def e10_bootstrap(R, H):
    """Replicates experiments/E10/analyze.py's ratio_ci sequence (RNG 2026) with the human runs H."""
    E10A.RNG = np.random.default_rng(2026)
    hf = [h["flow_per_s"] for h in H]
    out = {}
    for c in ALLC:
        E = [r["estimator"] for r in R if r["cell"] == c]
        out[c] = {"flow": E10A.ratio_ci([e.get("flow_per_s") for e in E], hf)}
        E10A.ratio_ci([e.get("max_gap_s") for e in E], [h["max_gap_s"] for h in H])
        E10A.ratio_ci([E10A.fl(e) for e in E], [h["fluct_rms"] for h in H])
    for L, key in ((2.0, "L2p0"), (0.21, "L0p21")):
        hL = [h["flow_per_s"] for h in H if abs(h["L"] - L) < 1e-9 or (L < 1 and h["L"] < 1)]
        for c in ALLC:
            E = [r["estimator"] for r in R if r["cell"] == c and E10A.RUNS_L[r["run"]] == L]
            out[c][key] = E10A.ratio_ci([e.get("flow_per_s") for e in E], hL)
    return out


def d4(M, hflow, hflow_by_run):
    o = {}
    for c in CELLS:
        X = M[c]
        runs = []
        for u in X:
            st = "complete" if u["complete"] else ("deadlock" if u["deadlock"] else "capped")
            open_600 = None if u["complete"] else float(T_HOR - u["tp"][-1])
            open_end = None if u["complete"] else float(u["t_end"] - u["tp"][-1])
            cval = u["max_gap"] if u["complete"] else max(u["max_gap"], open_600)
            runs.append({"seed": u["seed"], "run": u["run"], "status": st, "t_end": u["t_end"], "flow": u["flow"],
                         "max_gap_interior": u["max_gap"], "final_open_to_600": open_600, "final_open_to_end": open_end,
                         "c": cval, "event": int(u["complete"])})
        comp = [r["max_gap_interior"] for r in runs if r["event"]]
        inc = [r for r in runs if not r["event"]]
        kms = A12.km_summary([r["c"] for r in runs], [r["event"] for r in runs])
        fr = F.ratio_means([r["flow"] for r in runs], hflow)
        mr = F.matched_ratio([{"run": r["run"], "f": r["flow"]} for r in runs], hflow_by_run, "f")
        o[c] = {"label": LABEL[c], "n": len(runs), "complete": len(comp),
                "deadlock": sum(r["status"] == "deadlock" for r in runs),
                "capped": sum(r["status"] == "capped" for r in runs),
                "gap_complete": {"n": len(comp), "mean": float(np.mean(comp)) if comp else None,
                                 "median": float(np.median(comp)) if comp else None,
                                 "max": float(max(comp)) if comp else None},
                "n_censored": len(inc), "n_censored_deadlock": sum(r["status"] == "deadlock" for r in inc),
                "n_censored_capped": sum(r["status"] == "capped" for r in inc),
                "final_open_to_600": F.tci([r["final_open_to_600"] for r in inc]) if len(inc) >= 2 else
                {"n": len(inc), "mean": inc[0]["final_open_to_600"] if inc else None},
                "c_median_lower_bound": float(np.median([r["c"] for r in runs])),
                "c_mean_lower_bound": float(np.mean([r["c"] for r in runs])),
                "km_median": kms["median"], "km_median_reached": kms["median_reached"],
                "km_median_lower_bound": kms["median_lower_bound"],
                "km_restricted_mean": kms["restricted_mean_to_tau"], "km_tau": kms["tau"], "km_S_at_tau": kms["S_at_tau"],
                "km_restricted_mean_is_lower_bound": kms["restricted_mean_is_lower_bound"],
                "uncensored_interior_mean": float(np.mean([r["max_gap_interior"] for r in runs])),
                "flow": F.tci([r["flow"] for r in runs]),
                "flow_ratio": {"ratio": fr["ratio"], "ci95": fr["ci95"], "welch_df": fr["welch_df"],
                               "fieller_ci95": fr["fieller_ci95"]},
                "flow_ratio_matched": {"geo_ratio": mr["geo_ratio"], "ci95": mr["ci95"]},
                "runs": runs}
    return o


def macro_values(path):
    return dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", open(path).read()))


def fmt_like(old, v):
    if v is None:
        return None
    m = re.fullmatch(r"-?\d+(?:\.(\d+))?", old.strip())
    if not m:
        return None
    dec = len(m.group(1) or "")
    return f"{v:.{dec}f}" if dec else f"{int(round(v))}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive-dir", default=None)
    a = ap.parse_args()
    rng = np.random.default_rng(20261110)
    files = sorted(glob.glob(os.path.join(F.CROMA, "*_w080_*.txt")))
    o = {"script": "experiments/revision/D_croma_integrity.py", "sources": SOURCES, "archive": ARCHIVE,
         "rules": {
             "track_rule": "E10/fix_a7: passage = first frame with x >= 0 of a track that starts before the line; one "
                           "per track ID",
             "participant_rule": "the same crossing, counted once per marker ID (participant); a track whose marker "
                                 "is carried by a longer track at the same place is a duplicate and is dropped",
             "censoring": "final open gap of an incomplete run right-censored at the 600 s horizon: c = max(longest "
                          "interior gap, 600 s - last passage)"},
         "runs": {}}
    H_old, H_new, persons = [], [], {}
    for p in files:
        D = read_txt(p)
        run = os.path.basename(p)[:5]
        L = int(re.search(r"_l(\d{3})_", p).group(1)) / 100
        T = tracks(D)
        dup = duplicates(T)
        drop = {d["drop"] for d in dup}
        keep = [i for i in T if i not in drop]
        Tk = {i: T[i] for i in keep}
        n_mk = len({t["mk"] for t in T.values()})
        tp_track = [v for v in (first_cross(t) for t in T.values()) if v is not None]
        tp_part = [v for v in (first_cross(t) for t in Tk.values()) if v is not None]
        not_passing = [{"id": i, "marker": t["mk"], "x_last_m": float(t["x"][-1]), "last_s": float(t["fr"][-1] / FPS),
                        "is_duplicate": i in drop} for i, t in T.items() if first_cross(t) is None]
        late = [{"id": i, "start_s": float(t["fr"][0] / FPS), "x0_m": float(t["x"][0])} for i, t in T.items() if t["fr"][0] > 0]
        start_past = [i for i, t in T.items() if t["x"][0] >= 0]
        step = max(float(np.hypot(np.diff(t["x"]), np.diff(t["y"])).max()) for t in T.values())
        dur_doc = tc(ARCHIVE[run]["end"]) - tc(ARCHIVE[run]["start"])
        m0 = D["fr"] == 0
        v2 = []
        for t in T.values():
            k = t["fr"] <= 50
            if k.sum() > 40:
                v2.append(np.hypot(np.diff(t["x"][k]), np.diff(t["y"][k])).sum() / ((k.sum() - 1) / FPS))
        n_persons = len(Tk)
        persons[run] = n_persons
        rec = {"file": os.path.basename(p), "L_file_code_m": L, "L_archive_m": ARCHIVE[run]["l"],
               "N_archive": ARCHIVE[run]["N"], "n_track_ids": len(T), "n_markers": n_mk, "n_participants_tracked": n_persons,
               "duplicates": dup, "n_pass_track_rule": len(tp_track), "n_pass_participant_rule": len(tp_part),
               "tracks_not_passing": not_passing, "late_starts": {"n": len(late), "x0_range_m": [min(l["x0_m"] for l in late), max(l["x0_m"] for l in late)] if late else None,
                                                                  "start_s_range": [min(l["start_s"] for l in late), max(l["start_s"] for l in late)] if late else None},
               "tracks_starting_past_entrance": len(start_past),
               "tracks_ending_in_field_at_last_frame": int((D["fr"] == D["fr"].max()).sum()),
               "x_end_of_tracks_range_m": [float(min(t["x"][-1] for t in Tk.values())), float(max(t["x"][-1] for t in Tk.values()))],
               "max_step_per_frame_m": step, "near_pairs_distinct_markers_lt_0p1m_ge_1s": near_pairs(D),
               "frames": [int(D["fr"].min()), int(D["fr"].max())], "file_duration_s": float(D["fr"].max() / FPS),
               "documented_duration_s": float(dur_doc), "documented_minus_file_s": float(dur_doc - D["fr"].max() / FPS),
               "first_passage_s": float(min(tp_part)), "last_passage_s": float(max(tp_part)),
               "frame0_min_dist_to_entrance_m": float(np.hypot(D["x"][m0], D["y"][m0]).min()),
               "frame0_n_tracked": int(m0.sum()), "mean_speed_first_2s": float(np.mean(v2)),
               "missing_vs_archive": ARCHIVE[run]["N"] - n_persons,
               "thinning_test": thinning_test(np.array(tp_part), ARCHIVE[run]["N"], rng),
               "crowd_holes_frame0": crowd_holes(D)}
        o["runs"][run] = rec
        H_old.append(human_metrics(D, run, L, len(T)))
        H_new.append(human_metrics(subset(D, keep), run, L, n_persons))
        H_old[-1]["n_persons"] = H_new[-1]["n_persons"] = n_persons

    # cross-run table from the hdf5 release (optional)
    if a.archive_dir and os.path.isdir(a.archive_dir):
        rows = []
        for p in sorted(glob.glob(os.path.join(a.archive_dir, "*.h5"))):
            import h5py
            f = h5py.File(p, "r")
            r = ast.literal_eval(f.attrs["metadata"])["experiment"]["run"][0]
            Tr = f["trajectory"][:]
            ids = np.unique(Tr["id"])
            pd = f["personal_details"][:]
            rows.append({"run": r["run_name"], "N_archive": r["number_participants"], "n_ids": int(len(ids)),
                         "n_markers": int(len(np.unique(pd["marker_id"]))), "notes": r["notes"],
                         "wkt_geometry": r["wkt_geometry"]})
        o["archive_hdf5_runs"] = rows
        o["archive_hdf5_summary"] = {
            "n_runs": len(rows), "n_equal": sum(r["N_archive"] == r["n_ids"] for r in rows),
            "n_N_gt_ids_by_ge_20": sum(r["N_archive"] - r["n_ids"] >= 20 for r in rows),
            "runs_N_gt_ids_by_ge_20": [r["run"][:5] for r in rows if r["N_archive"] - r["n_ids"] >= 20]}
        # 4D120 sensitivity: revised trajectories (33 tracks start at x ~ -4.1 m instead of being extended to frame 0)
        p120 = glob.glob(os.path.join(a.archive_dir, "4D120*.h5"))
        if p120:
            import h5py
            f = h5py.File(p120[0], "r")
            Tr = f["trajectory"][:]
            mk = {int(i): int(m) for i, m in f["personal_details"][:]}
            D = {"id": Tr["id"].astype(int), "fr": Tr["frame"].astype(int), "x": Tr["x"], "y": Tr["y"], "z": Tr["z"],
                 "mk": np.array([mk[int(i)] for i in Tr["id"]])}
            txt = read_txt(glob.glob(os.path.join(F.CROMA, "4D120*.txt"))[0])
            hv = human_metrics(D, "4D120", 0.21, len(np.unique(D["id"])))
            hv["n_persons"] = hv["n_tracks"]
            H_rev = [hv if h["run"] == "4D120" else h for h in H_new]
            o["sensitivity_4D120_revised"] = {
                "rows_txt": int(len(txt["id"])), "rows_hdf5": int(len(D["id"])),
                "run": {k: v for k, v in hv.items() if k != "tp"}, "humans": summarize_h(H_rev)}
            o["archive_geometry"] = {r["run"][:5]: r["wkt_geometry"] for r in rows if r["run"][:5] in ARCHIVE}

    strip = lambda H: [{k: v for k, v in h.items() if k != "tp"} for h in H]  # noqa: E731
    o["humans_as_used"] = {"runs": strip(H_old), **summarize_h(H_old)}
    o["humans_corrected"] = {"runs": strip(H_new), **summarize_h(H_new)}

    # model runs
    rd = F.raw_dir()
    R = [json.loads(l) for l in open(F.IN) if l.strip()]
    M = {c: [F.per_run_stats(F.model_run(r, rd)) for r in R if r["cell"] == c] for c in ALLC}
    hb_new = {h["run"]: h["flow_per_s"] for h in H_new}
    hb_old = {h["run"]: h["flow_per_s"] for h in H_old}
    o["D4"] = d4(M, [h["flow_per_s"] for h in H_new], hb_new)
    o["D4_as_used_humans"] = {c: {"flow_ratio": v["flow_ratio"], "flow_ratio_matched": v["flow_ratio_matched"]}
                              for c, v in d4(M, [h["flow_per_s"] for h in H_old], hb_old).items()}
    rs = [o["D4"][c]["flow_ratio"]["ratio"] for c in CELLS]
    o["D4_range"] = {"min": min(rs), "max": max(rs), "min_cell": CELLS[int(np.argmin(rs))],
                     "max_cell": CELLS[int(np.argmax(rs))]}
    # window ratios (fix_a7 window_obs) with corrected humans
    hw = [h["window_obs"] for h in H_new]
    o["window_ratio_corrected"] = {c: F.ratio_means([u["flow_w_obs"] for u in M[c] if u["flow_w_obs"] is not None], hw)
                                   for c in ALLC}
    o["fix_a7_ratio_corrected_pub"] = F.ratio_means([u["flow"] for u in M["C1_pub"]], [h["flow_per_s"] for h in H_new])
    o["fix_a7_matched_corrected_pub"] = F.matched_ratio([{"run": u["run"], "f": u["flow"]} for u in M["C1_pub"]], hb_new, "f")
    o["E10_bootstrap_as_used"] = e10_bootstrap(R, H_old)
    o["E10_bootstrap_corrected"] = e10_bootstrap(R, H_new)

    # D3: agent number and length used by e10_croma.py
    used = {}
    for r in R:
        used[r["run"]] = (r["N"], r["L"])
    o["D3"] = {run: {"N_used": used[run][0], "L_used_m": used[run][1], "n_track_ids": o["runs"][run]["n_track_ids"],
                     "n_participants_passed": o["runs"][run]["n_pass_participant_rule"], "N_archive": ARCHIVE[run]["N"],
                     "L_archive_m": ARCHIVE[run]["l"], "N_used_minus_passed": used[run][0] - o["runs"][run]["n_pass_participant_rule"],
                     "N_used_equals_track_ids": used[run][0] == o["runs"][run]["n_track_ids"]} for run in ARCHIVE}
    o["D3_summary"] = {"N_source": "track-ID count of each file (n_ids of w28_croma.croma)",
                       "runs_off": {k: v["N_used_minus_passed"] for k, v in o["D3"].items() if v["N_used_minus_passed"]},
                       "max_rel_offset": max(abs(v["N_used_minus_passed"]) / v["n_participants_passed"] for v in o["D3"].values())}

    # changed macros
    nt = macro_values(os.path.join(ROOT, "paper", "numbers.tex"))
    hc, hu = o["humans_corrected"], o["humans_as_used"]
    new = {"EtenHumanFlow": hc["flow"]["mean"], "EtenHumanFlowLo": hc["flow"]["ci95"][0], "EtenHumanFlowHi": hc["flow"]["ci95"][1],
           "EtenHumanFlowMin": hc["flow_range"][0], "EtenHumanFlowMax": hc["flow_range"][1],
           "EtenHumanGap": hc["longest_gap"]["mean"], "EtenHumanGapMax": hc["longest_gap_max"],
           "EtenHumanGapsTwo": hc["gaps_gt_2s_mean"], "EtenHumanFluct": hc["fluct"]["mean"],
           "EtenHumanFluctLo": hc["fluct"]["ci95"][0], "EtenHumanFluctHi": hc["fluct"]["ci95"][1],
           "EtenLongHumanFlow": hc["flow_long"], "EtenShortHumanFlow": hc["flow_short"],
           "FixAsevenHumanFlow": hc["flow"]["mean"], "FixAsevenHumanFlowLo": hc["flow"]["ci95"][0],
           "FixAsevenHumanFlowHi": hc["flow"]["ci95"][1], "FixAsevenHumanWindowFlow": hc["window_obs"]["mean"],
           "FixAsevenHumanWindowFlowLo": hc["window_obs"]["ci95"][0], "FixAsevenHumanWindowFlowHi": hc["window_obs"]["ci95"][1],
           "FixAsevenHumanGapGeo": hc["longest_gap_geo"]["geo_mean"]}
    tag = {"C1_pub": "CPub", "C1_cf": "COne", "C1_cf_edge": "CEdge", "C3_rvo2_cf": "CThree", "C1_cf_sig": "CSig"}
    for c in ALLC:
        t = tag[c]
        b = o["E10_bootstrap_corrected"][c]["flow"]
        new.update({f"Eten{t}FlowRatio": b["ratio"], f"Eten{t}FlowRatioLo": b["ci95"][0], f"Eten{t}FlowRatioHi": b["ci95"][1]})
        fr = o["D4"][c]["flow_ratio"] if c in CELLS else o["fix_a7_ratio_corrected_pub"]
        mr = o["D4"][c]["flow_ratio_matched"] if c in CELLS else o["fix_a7_matched_corrected_pub"]
        w = o["window_ratio_corrected"][c]
        new.update({f"FixAseven{t}FlowRatio": fr["ratio"], f"FixAseven{t}FlowRatioLo": fr["ci95"][0],
                    f"FixAseven{t}FlowRatioHi": fr["ci95"][1], f"FixAseven{t}FiellerLo": fr["fieller_ci95"][0],
                    f"FixAseven{t}FiellerHi": fr["fieller_ci95"][1], f"FixAseven{t}MatchedRatio": mr["geo_ratio"],
                    f"FixAseven{t}MatchedRatioLo": mr["ci95"][0], f"FixAseven{t}MatchedRatioHi": mr["ci95"][1],
                    f"FixAseven{t}WindowRatio": w["ratio"], f"FixAseven{t}WindowRatioLo": w["ci95"][0],
                    f"FixAseven{t}WindowRatioHi": w["ci95"][1]})
    chg = []
    for k, v in new.items():
        if k not in nt:
            continue
        nv = fmt_like(nt[k], v)
        chg.append({"macro": k, "old": nt[k], "new": nv, "changed": nv != nt[k]})
    a12 = json.load(open(os.path.join(revlib.DERIVED, "rev_A12.json")))
    a12map = {"FlowRatio": ("flow_ratio", "ratio", "{:.2f}"), "FlowRatioLo": ("flow_ratio", "lo", "{:.2f}"),
              "FlowRatioHi": ("flow_ratio", "hi", "{:.2f}"),
              "GapCens": ("longest_gap", "n_censored", "{:d}"), "GapLowerMedian": ("longest_gap", "with_terminal_median_lower_bound", "{:.0f}"),
              "GapLowerMean": ("longest_gap", "with_terminal_mean_lower_bound", "{:.0f}"),
              "GapKMRmean": ("longest_gap", "km_restricted_mean", "{:.0f}"), "GapKMTau": ("longest_gap", "km_tau", "{:.0f}"),
              "GapKMSTau": ("longest_gap", "km_S_at_tau", "{:.2f}"), "GapTermMean": ("longest_gap", "terminal_open", "{:.0f}")}
    dmap = {"FlowRatio": lambda d: d["flow_ratio"]["ratio"], "FlowRatioLo": lambda d: d["flow_ratio"]["ci95"][0],
            "FlowRatioHi": lambda d: d["flow_ratio"]["ci95"][1], "GapCens": lambda d: d["n_censored"],
            "GapLowerMedian": lambda d: d["c_median_lower_bound"], "GapLowerMean": lambda d: d["c_mean_lower_bound"],
            "GapKMRmean": lambda d: d["km_restricted_mean"], "GapKMTau": lambda d: d["km_tau"],
            "GapKMSTau": lambda d: d["km_S_at_tau"], "GapTermMean": lambda d: d["final_open_to_600"].get("mean")}
    for c in CELLS:
        t = tag[c]
        A = a12["cells"][c]
        for suf, (grp, key, fm) in a12map.items():
            if grp == "flow_ratio":
                ov = A["flow_ratio"]["ratio"] if key == "ratio" else A["flow_ratio"]["ci95"][0 if key == "lo" else 1]
            elif key == "terminal_open":
                ov = A["longest_gap"]["terminal_open"].get("mean")
            else:
                ov = A["longest_gap"][key]
            nv = dmap[suf](o["D4"][c])
            if ov is None or nv is None:
                continue
            os_, ns_ = fm.format(int(ov) if fm == "{:d}" else ov), fm.format(int(nv) if fm == "{:d}" else nv)
            chg.append({"macro": f"RevAtwelve{t}{suf}", "old": os_, "new": ns_, "changed": os_ != ns_})
        if A["longest_gap"]["km_median"] is not None or o["D4"][c]["km_median"] is not None:
            ov, nv = A["longest_gap"]["km_median"], o["D4"][c]["km_median"]
            chg.append({"macro": f"RevAtwelve{t}GapKMMedian", "old": None if ov is None else f"{ov:.1f}",
                        "new": None if nv is None else f"{nv:.1f}", "changed": ov != nv})
    o["macro_changes"] = [c for c in chg if c["changed"]]
    o["macro_checked_unchanged"] = [c["macro"] for c in chg if not c["changed"]]
    # check: the as-used recomputation reproduces the current macros
    chk = {"EtenHumanFlow": hu["flow"]["mean"], "EtenHumanFluct": hu["fluct"]["mean"],
           "EtenCOneFlowRatio": o["E10_bootstrap_as_used"]["C1_cf"]["flow"]["ratio"],
           "EtenCOneFlowRatioLo": o["E10_bootstrap_as_used"]["C1_cf"]["flow"]["ci95"][0],
           "FixAsevenCSigFlowRatioLo": o["D4_as_used_humans"]["C1_cf_sig"]["flow_ratio"]["ci95"][0],
           "FixAsevenHumanWindowFlow": hu["window_obs"]["mean"]}
    o["check_as_used_reproduces_macros"] = {k: {"macro": nt[k], "recomputed": fmt_like(nt[k], v),
                                                "ok": fmt_like(nt[k], v) == nt[k]} for k, v in chk.items()}
    print(revlib.out_json("D", o))
    # D3 rerun (experiments/revision/D3_analyze.py) once its data exist; it reads the humans just written
    import D3_analyze
    if os.path.exists(D3_analyze.IN):
        o["D3"]["rerun"] = D3_analyze.analyze()
        revlib.out_json("D", o)
    report(o)


def report(o):
    print("check", {k: v["ok"] for k, v in o["check_as_used_reproduces_macros"].items()})
    print("| run | N archive | track IDs | markers | passages (track rule) | passages (participant rule) | dup | late | doc-file s |")
    for run, r in o["runs"].items():
        print(f"| {run} | {r['N_archive']} | {r['n_track_ids']} | {r['n_markers']} | {r['n_pass_track_rule']} | "
              f"{r['n_pass_participant_rule']} | {[(d['keep'], d['drop']) for d in r['duplicates']]} | {r['late_starts']['n']} | "
              f"{r['documented_minus_file_s']:.2f} | thin {r['thinning_test']} | holes {r['crowd_holes_frame0']} | near {r['near_pairs_distinct_markers_lt_0p1m_ge_1s']}")
    for k in ("humans_as_used", "humans_corrected"):
        h = o[k]
        print(k, "flow", h["flow"]["mean"], h["flow"]["ci95"], "short", h["flow_short"], "fluct", h["fluct"]["mean"],
              h["fluct"]["ci95"], "window", h["window_obs"]["mean"])
        for r in h["runs"]:
            print("   ", r["run"], r["n_pass"], round(r["flow_per_s"], 4), r["max_gap_s"], round(r["fluct_rms"], 5), round(r["window_obs"], 4))
    if "sensitivity_4D120_revised" in o:
        s = o["sensitivity_4D120_revised"]
        print("4D120 revised", s["run"]["flow_per_s"], s["run"]["fluct_rms"], "humans flow", s["humans"]["flow"]["mean"],
              "fluct", s["humans"]["fluct"]["mean"])
    for c, d in o["D4"].items():
        print(c, "k/dl/cap", d["complete"], d["deadlock"], d["capped"], "gap complete", d["gap_complete"],
              "cens", d["n_censored"], "c med", sig(d["c_median_lower_bound"]), "KM med", d["km_median"],
              "KM rmean", sig(d["km_restricted_mean"]), "tau", sig(d["km_tau"]), "S", sig(d["km_S_at_tau"]),
              "ratio", sig(d["flow_ratio"]["ratio"]), [sig(v) for v in d["flow_ratio"]["ci95"]],
              "matched", sig(d["flow_ratio_matched"]["geo_ratio"]), [sig(v) for v in d["flow_ratio_matched"]["ci95"]])
    print("range", o["D4_range"])
    print("D3", o["D3_summary"])
    print("changed macros:")
    for c in o["macro_changes"]:
        print("  ", c["macro"], c["old"], "->", c["new"])


if __name__ == "__main__":
    main()
