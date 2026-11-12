"""A9: CroMa comparison of Sect. 7 by bottleneck length, the 10%-90% passage flow, the headline ratio, and the
participant facts of the data paper.

Inputs (read only):
  data/revision/D3/d3_croma.jsonl      the 100 model runs of D3 (4 variants x 25; agent number = participants who
                                       passed; bottleneck 2.0 m for 4D030/4D040, 0.2 m for 4D110/4D120/4D130)
  D3 raw trajectories (*.npz)          data/revision/D3/raw/, else $D3_RAW, else the session-C worktree copy
  data/ext/croma/*_w080_*.txt          human trajectories (PeTrack, 25 fps), participant rule of D2
                                       (duplicate track IDs dropped: experiments/revision/D_croma_integrity.py)
  data/derived/rev_D.json              D3.rerun (for the check that the headline ratios are reproduced)
Method.
  Passage = first frame with x >= x_e (0 m humans, 10 m model) of a track that starts before the line.
  Flow of a run = (n - 1)/(last - first passage), n = passages observed (E10/D3 estimator).
  (i) and (iii) Ratio of arithmetic means model/human, 95% interval from the delta method on the log ratio with
  Welch df (fix_a7.ratio_means, the estimator of the headline). Per bottleneck length the model runs of the two
  (2.0 m) or three (0.2 m) human runs are set against those human runs. Secondary interval: percentile bootstrap,
  model and human runs resampled independently within the length, 20000 draws, numpy default_rng(2026); with 2 or 3
  human runs it understates the human spread and is reported only for comparison. Per human run: mean of its 5
  model runs over the human value, t interval over the 5 model runs (human value taken as fixed).
  (ii) 10%-90% passage flow over the N agents (participants): k10 = ceil(0.1 N) - 1, k90 = ceil(0.9 N) - 1 (0-based
  passage ranks), flow = (k90 - k10)/(t[k90] - t[k10]) (fix_a7.window_flow, form b). Humans: every participant
  passes. Model run with fewer than k90 + 1 passages (90% never pass by its end): censored. Rule UB: its window
  flow is set to the upper bound (k90 - k10)/(600 s - t[k10]) (the 90th-percentile passage lies after the 600 s
  horizon); rule LB: set to 0 (a deadlock at rest never resolves in the deterministic model). The two rules bracket
  the ratio; both use the delta-method interval. Pooled and per length.
  By motivation (iv): the same ratio over the two normal (h0) and the two hurry (h1) runs; full commitment (h2) has
  one human run, given by the per-human-run ratio of 4D130.
  (iii) Headline: per variant, mean over its 25 runs of the run flow, over the mean of the 5 corrected human flows;
  the range is the min and max of the four point ratios.
  (iv)-(vi) Facts read from Boomers et al., arXiv:2303.02319v2 (= Collective Dynamics 8, A141, 2023), stored as
  constants with page references (arXiv v2 pagination).
Output: data/derived/rev2_A9.json. Registry: notes/C2_items/A9.yaml.
Usage: A9_croma_compare.py
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib as L  # noqa: E402
from rev2lib import ROOT, np, stats  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments", "revision"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "fixan"))
import fix_a7 as F  # noqa: E402
import D_croma_integrity as DI  # noqa: E402

IN = os.path.join(ROOT, "data", "revision", "D3", "d3_croma.jsonl")
CROMA = os.path.join(ROOT, "data", "ext", "croma")
REV_D = os.path.join(ROOT, "data", "derived", "rev_D.json")
CELLS = ["C1_cf", "C1_cf_edge", "C3_rvo2_cf", "C1_cf_sig"]
LONG = ("4D030", "4D040")
SHORT = ("4D110", "4D120", "4D130")
GEOM = {"long": LONG, "short": SHORT, "pooled": LONG + SHORT}
MOTIV = {"normal": ("4D030", "4D110"), "hurry": ("4D040", "4D120")}   # h0, h1; full commitment (h2) is 4D130 alone
T_HOR = 600.0
SEED = 2026
B = 20000


def raw_dir():
    for d in (os.path.join(ROOT, "data", "revision", "D3", "raw"), os.environ.get("D3_RAW"),
              "/Users/palaash/Developer/lnns-wt/C/data/revision/D3/raw"):
        if d and os.path.isdir(d) and glob.glob(os.path.join(d, "*.npz")):
            return d
    raise SystemExit("D3 raw trajectories not found; set D3_RAW")


def humans():
    out = {}
    for p in sorted(glob.glob(os.path.join(CROMA, "*_w080_*.txt"))):
        run = os.path.basename(p)[:5]
        D = DI.read_txt(p)
        T = DI.tracks(D)
        drop = {d["drop"] for d in DI.duplicates(T)}
        tp = np.sort([v for v in (DI.first_cross(t) for i, t in T.items() if i not in drop) if v is not None])
        out[run] = {"run": run, "N": len(tp), "tp": tp, "flow": (len(tp) - 1) / (tp[-1] - tp[0]),
                    "h": os.path.basename(p)[-6:-4]}
    return out


def window(tp, N):
    k10, k90 = int(math.ceil(0.1 * N)) - 1, int(math.ceil(0.9 * N)) - 1
    if len(tp) > k90:
        return {"value": (k90 - k10) / (tp[k90] - tp[k10]), "censored": False, "k10": k10, "k90": k90}
    return {"value": None, "censored": True, "ub": (k90 - k10) / (T_HOR - tp[k10]), "k10": k10, "k90": k90,
            "n_pass": int(len(tp))}


def boot_ratio(m, h, rng):
    m, h = np.asarray(m, float), np.asarray(h, float)
    bm = m[rng.integers(0, len(m), (B, len(m)))].mean(1)
    bh = h[rng.integers(0, len(h), (B, len(h)))].mean(1)
    r = bm / bh
    return [float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))]


def ratio(m, h, rng=None):
    r = F.ratio_means(m, h)
    o = {"ratio": r["ratio"], "ci95": r["ci95"], "welch_df": r["welch_df"], "n_model": len(m), "n_human": len(h),
         "model_mean": float(np.mean(m)), "human_mean": float(np.mean(h))}
    if rng is not None:
        o["boot_ci95"] = boot_ratio(m, h, rng)
    return o


def per_run_ratio(mv, hv):
    mv = np.asarray(mv, float)
    n = len(mv)
    hw = stats.t.ppf(0.975, n - 1) * mv.std(ddof=1) / math.sqrt(n)
    return {"ratio": float(mv.mean() / hv), "ci95": [float((mv.mean() - hw) / hv), float((mv.mean() + hw) / hv)],
            "n_model": n}


PAPER = {
    "source": "Boomers et al., Pedestrian Crowd Management Experiments: A Data Guidance Paper, arXiv:2303.02319v2 "
              "(10 Mar 2023); published in Collective Dynamics 8 (2023) A141, DOI 10.17815/CD.2023.141. Page numbers "
              "are those of the arXiv v2 PDF.",
    "motivation": {
        "levels": "Sect. 3.7 (p. 20): motivation normal, hurry, full commitment; Table 19 (App. A.9, p. A19 = PDF "
                  "p. 57) codes h0 normal, h1 hurry, h2 full commitment (he normal-hurry, not used here)",
        "runs": {"4D030": "h0", "4D040": "h1", "4D110": "h0", "4D120": "h1", "4D130": "h2"},
        "n_normal": 2, "n_hurry": 2, "n_full": 1,
        "lineup": {"4D030": "2 m semi-circle", "4D040": "2 m semi-circle", "4D110": "2 m semi-circle",
                   "4D120": "2 m semi-circle", "4D130": "directly at bottleneck"}},
    "shoulder": {"mean_m": 0.45, "sd_m": 0.04, "page": "p. 7, Sect. 2.4 (Test Person Sample)",
                 "population": "all 1038 participants of the four days (measured during the registration course); "
                               "day-4 values only as histograms (App. A.1, Fig. 19, no numbers)"},
    "ethics": {"page": "p. 34 (Ethical Review statement, end matter)",
               "bottleneck_committee": "ethical review committee of the University of Wuppertal (Bergische "
                                       "Universitaet Wuppertal)",
               "bottleneck_applicant": "A. Seyfried", "bottleneck_approved": "January 2020",
               "bottleneck_file_reference": "MS/BBL 191213 Seyfried",
               "other_experiments": "Crowd Management, Single-File, Personal-Space, Train Platform, Boarding and "
                                    "Alighting: German Psychological Society (DGPs), approved December 2019, file "
                                    "reference SiebenAnna2019-10-22VA",
               "consent": "p. 5, Sect. 2.3: at registration participants signed that they consented to the "
                          "conditions of participation and received a declaration of informed consent with the "
                          "questionnaires; its signature was checked before the experiments"},
}


def main():
    rng = np.random.default_rng(SEED)
    H = humans()
    rd = raw_dir()
    R = [json.loads(l) for l in open(IN) if l.strip()]
    M = {c: [] for c in CELLS}
    for r in R:
        D = np.load(os.path.join(rd, os.path.basename(r["npz"])))["data"]
        tp = F.first_crossings(D[:, 1].astype(int), D[:, 0], D[:, 2], 10.0)
        st = "complete" if r["complete"] else ("deadlock" if r["deadlock"] else "capped")
        M[r["cell"]].append({"run": r["run"], "seed": r["seed"], "N": r["N"], "status": st, "n_pass": int(len(tp)),
                             "flow": (len(tp) - 1) / (tp[-1] - tp[0]), "w": window(tp, r["N"])})
    o = {"script": "experiments/revision2/A9_croma_compare.py", "inputs": {"model": os.path.relpath(IN, ROOT),
         "raw": rd, "humans": os.path.relpath(CROMA, ROOT)}, "seed": SEED, "n_boot": B, "paper": PAPER}

    # humans
    hw = {k: window(v["tp"], v["N"]) for k, v in H.items()}
    o["humans"] = {k: {"N": v["N"], "h": v["h"], "flow": v["flow"], "window_flow": hw[k]["value"]} for k, v in H.items()}
    o["humans_geom"] = {g: {"flow_mean": float(np.mean([H[k]["flow"] for k in runs])),
                            "window_mean": float(np.mean([hw[k]["value"] for k in runs])), "n": len(runs)}
                        for g, runs in GEOM.items()}

    # (iii) headline and (i) per geometry
    o["headline"] = {"definition": "per variant: arithmetic mean over its 25 model runs of the run flow (n - 1)/(last "
                                   "- first passage), n = passages observed up to the end of the run (deadlocked and "
                                   "capped runs included with the passages they made), divided by the arithmetic mean "
                                   "of the 5 human run flows (participant rule); 95% interval: delta method on the log "
                                   "ratio, Welch df (fix_a7.ratio_means). Range: min and max of the four point ratios.",
                     "per_variant": {}}
    o["per_geometry"] = {}
    for c in CELLS:
        X = M[c]
        o["per_geometry"][c] = {}
        for g, runs in GEOM.items():
            mv = [u["flow"] for u in X if u["run"] in runs]
            o["per_geometry"][c][g] = ratio(mv, [H[k]["flow"] for k in runs], rng)
        o["per_geometry"][c]["per_human_run"] = {k: per_run_ratio([u["flow"] for u in X if u["run"] == k],
                                                                  H[k]["flow"]) for k in GEOM["pooled"]}
        for g, runs in MOTIV.items():
            o["per_geometry"][c][g] = ratio([u["flow"] for u in X if u["run"] in runs], [H[k]["flow"] for k in runs])
        o["headline"]["per_variant"][c] = {k: o["per_geometry"][c]["pooled"][k] for k in ("ratio", "ci95")}
    rs = {c: v["ratio"] for c, v in o["headline"]["per_variant"].items()}
    o["headline"].update({"min": min(rs.values()), "max": max(rs.values()), "min_cell": min(rs, key=rs.get),
                          "max_cell": max(rs, key=rs.get)})
    d3 = json.load(open(REV_D))["D3"]["rerun"]
    o["headline"]["D3_range"] = d3["range"]
    o["headline"]["reproduces_D3"] = bool(abs(d3["range"]["min"] - o["headline"]["min"]) < 1e-12
                                          and abs(d3["range"]["max"] - o["headline"]["max"]) < 1e-12)
    o["headline"]["range_display"] = f"{L.sig(o['headline']['min'])}-{L.sig(o['headline']['max'])}"
    o["headline"]["changes"] = o["headline"]["range_display"] != "0.40-0.60"

    # (ii) 10-90% passage flow
    o["window"] = {"rule": "k10 = ceil(0.1 N) - 1, k90 = ceil(0.9 N) - 1 over the N agents; censored run (fewer than "
                           "k90 + 1 passages): UB = (k90 - k10)/(600 s - t[k10]), LB = 0", "per_variant": {}}
    for c in CELLS:
        X = M[c]
        d = {"status_counts": {s: sum(u["status"] == s for u in X) for s in ("complete", "deadlock", "capped")}}
        for g, runs in GEOM.items():
            Y = [u for u in X if u["run"] in runs]
            hv = [hw[k]["value"] for k in runs]
            ub = [u["w"]["ub"] if u["w"]["censored"] else u["w"]["value"] for u in Y]
            lb = [0.0 if u["w"]["censored"] else u["w"]["value"] for u in Y]
            cens = [u for u in Y if u["w"]["censored"]]
            e = {"n": len(Y), "n_censored": len(cens),
                 "n_censored_deadlock": sum(u["status"] == "deadlock" for u in cens),
                 "n_censored_capped": sum(u["status"] == "capped" for u in cens),
                 "n_reached_not_complete": sum(u["status"] != "complete" and not u["w"]["censored"] for u in Y),
                 "model_mean_ub": float(np.mean(ub)), "model_mean_lb": float(np.mean(lb)),
                 "ub": ratio(ub, hv), "lb": ratio(lb, hv) if np.mean(lb) > 0 and min(lb) > 0 else
                 {"ratio": float(np.mean(lb) / np.mean(hv)), "ci95": None, "note": "zeros: no log-ratio interval"}}
            if cens:
                e["censored_runs"] = [{"run": u["run"], "seed": u["seed"], "status": u["status"], "n_pass": u["n_pass"],
                                       "k90": u["w"]["k90"], "ub": u["w"]["ub"]} for u in cens]
            d[g] = e
        o["window"]["per_variant"][c] = d
    wr = {c: v["pooled"]["ub"]["ratio"] for c, v in o["window"]["per_variant"].items()}
    o["window"]["range_ub"] = {"min": min(wr.values()), "max": max(wr.values()), "min_cell": min(wr, key=wr.get),
                               "max_cell": max(wr, key=wr.get)}
    o["window"]["n_censored_total"] = sum(v["pooled"]["n_censored"] for v in o["window"]["per_variant"].values())

    # (v) radius vs shoulder width
    sw = PAPER["shoulder"]
    o["radius"] = {"model_radius_mean_m": 0.25, "model_radius_sd_m": 0.03, "model_radius_floor_m": 0.15,
                   "model_diameter_mean_m": 0.50, "model_diameter_sd_m": 0.06,
                   "shoulder_mean_m": sw["mean_m"], "shoulder_sd_m": sw["sd_m"],
                   "shoulder_half_m": sw["mean_m"] / 2, "diameter_over_shoulder": 0.50 / sw["mean_m"],
                   "diameter_minus_shoulder_m": 0.50 - sw["mean_m"],
                   "diameter_minus_shoulder_in_sd": (0.50 - sw["mean_m"]) / sw["sd_m"],
                   "source": "code/sim/core/agent.py (radius_mean 0.25, radius_std 0.03, floor 0.15 m); " + sw["page"]}
    print(L.out_json("A9", o))
    print("headline", {c: (L.sig(v["ratio"]), [L.sig(x) for x in v["ci95"]]) for c, v in o["headline"]["per_variant"].items()},
          o["headline"]["range_display"], "reproduces D3:", o["headline"]["reproduces_D3"])
    for c in CELLS:
        print(c, {g: (L.sig(o["per_geometry"][c][g]["ratio"]), [L.sig(x) for x in o["per_geometry"][c][g]["ci95"]],
                      [L.sig(x) for x in o["per_geometry"][c][g]["boot_ci95"]]) for g in GEOM})
        w = o["window"]["per_variant"][c]
        print("   window", {g: (w[g]["n_censored"], L.sig(w[g]["ub"]["ratio"]), [L.sig(x) for x in w[g]["ub"]["ci95"]],
                                L.sig(w[g]["lb"]["ratio"])) for g in GEOM})
    print("humans", {k: (v["h"], round(v["flow"], 3), round(v["window_flow"], 3)) for k, v in o["humans"].items()})
    print("humans geom", o["humans_geom"])


if __name__ == "__main__":
    main()
