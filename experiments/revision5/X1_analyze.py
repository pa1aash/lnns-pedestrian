"""X1 analysis: energy span of the barrier-library string paths, and an alternative re-analysis of the Arrhenius (E4)
and time-step (E3) sets and the matched-noise beta with the span in place of the reported barrier.

Input: data/revision5/X1/x1_paths.jsonl (X1_span_paths.py), data/BAR/gate.jsonl, data/derived/selection.json.
Per (snapshot, condition) path with image energies E_k = U(s_k) - U(s_0), s_0 the snapshot minimum, s_N the exit =
the first image with the blocker centre at x >= 10 m (door plane; past it the string descends towards the goal and
rises to the fixed end image, which is not a minimum, so that part is not used):
  dU_rep_img   max_k E_k - E_0 (image maximum; the published barrier dU_rep is the climbing-image refinement of it,
               gate.jsonl <cond>.dU, compared here with the recomputation)
  dU_span_img  max_{i<j} (E_j - E_i), the largest rise from any image to any later image, with (i, j)
  minima       interior local minima of E with a swing >= 0.05 J to the neighbouring maxima on both sides (zigzag);
               for each: E at the image, E at the relaxed rest state M, the swing on each side, and the exit barrier
               from M (gate.check string from M to the same exit end point, climbing image; accepted or not)
  affected     |dU_span_img - dU_rep_img| > 1% of dU_rep_img
  dU_span      the span with the same refinement as dU_rep: dU_rep (published) when the span starts at s_0, else the
               climbing-image exit barrier from the relaxed rest state M at the span's start image (gate rules)
One-agent snapshots: alone = frozen = full (computed once, as in the gate).
Re-analysis (alternative only; published numbers are not replaced):
  E4  experiments/E4/analyze.py main() re-run on data/E4/e4_escape.jsonl with dU_cond replaced by dU_span (rates and
      1/k_B T_eff unchanged; beta = dU_span / k_B T_eff), same estimators, bootstrap seed and MIN_EV exclusion; pooled
      slope = experiments/fixan/fix_a3.py collapse_part (free intercepts, snapshot bootstrap) with a fresh
      PCG64(fix_a3.SEED) for both the published and the span input (the published value is reproduced alongside).
  E3  experiments/E3/analyze.py main() re-run with dU_i replaced by dU_span (predicted ell and beta scale by
      dU_span / dU_rep), same estimators and seed.
  A3  beta at sigma = 0.07 m/s (and 0.0717, sigma*) for the 56 barriers with dU_span (experiments/revision/A3_beta.py
      rows and k_B T_eff).
Output: data/derived/rev5_X1.json; scratch outputs of the re-run analyses under data/revision5/X1/rean/.
"""
import copy
import importlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev5lib  # noqa: E402
from rev5lib import DATA, DERIVED, ROOT, load_runs, np, sig  # noqa: E402

for d in ("E3", "E4", "fixan", "revision"):
    sys.path.insert(0, os.path.join(ROOT, "experiments", d))
from X1_span_paths import SWING, X_DOOR, interior_minima, span, zigzag  # noqa: E402

D = rev5lib.data_dir("X1")
REAN = os.path.join(D, "rean")
os.makedirs(REAN, exist_ok=True)
CONDS = ("alone", "frozen", "full")
REL = 0.01


def swings(E, ext, k):
    """Swing from interior minimum k (index into E) to the neighbouring zigzag maxima on each side."""
    idx = [i for i, _ in ext]
    p = idx.index(k)
    return float(E[idx[p - 1]] - E[k]), float(E[idx[p + 1]] - E[k])


def kind(dU_pub, dU_span, deepest, affected):
    """A: dU_rep is the exit saddle measured from the snapshot, which lies above a deeper rest state M on the path
    (dU_span = dU_rep + depth of M); B: dU_rep is a first saddle into M and the exit saddle from M lies below the
    snapshot energy (dU_span = exit barrier from M); None: span equals the reported barrier."""
    if not affected or deepest is None or deepest["exit_barrier_M_J"] is None:
        return None
    es = deepest["E_M_J"] + deepest["exit_barrier_M_J"]
    return "A" if abs(es - dU_pub) <= 0.02 * max(abs(dU_pub), 0.05) else "B"


def per_path(r, gate_row):
    Ew = np.array(r["E_J"])
    bx = np.array(r["blocker_x"])
    k_exit = int(next((k for k in range(len(bx)) if bx[k] >= X_DOOR), len(bx) - 1))
    E = Ew[:k_exit + 1]                       # snapshot minimum -> first image at the door plane
    ext = [tuple(x) for x in zigzag(E)]
    rep_img = float(E.max() - E[0])
    sp, si, sj = span(E)
    mins = []
    sec = {s["from_image"]: s for s in r["second"]}
    for k in interior_minima(E):
        lft, rgt = swings(E, ext, k)
        s = sec.get(k)
        mins.append({"image": k, "E_image_J": float(E[k]), "swing_left_J": lft, "swing_right_J": rgt,
                     "blocker_x_m": r["blocker_x"][k],
                     "E_M_J": s["U_M_minus_U0_J"] if s else None,
                     "exit_barrier_img_J": float(E[k:].max() - E[k]),
                     "exit_barrier_M_J": s["dU_exit_from_M"] if s else None,
                     "exit_M_accepted": s["accepted"] if s else None,
                     "exit_M_reasons": s["reasons"] if s else None,
                     "exit_M_resolution": s["resolution_pair"] if s else None})
    first_max = next((i for i, t in ext if t == "max"), int(np.argmax(E)))
    deepest = min(mins, key=lambda m: m["E_image_J"]) if mins else None
    dU_pub = gate_row["dU"]
    if si == 0:
        dU_span, span_src = dU_pub, "published (span starts at the snapshot minimum)"
    elif si in sec:
        dU_span, span_src = sec[si]["dU_exit_from_M"], "climbing-image exit barrier from relaxed M at image %d" % si
    else:
        dU_span, span_src = sp, "image span (no second string at image %d)" % si
    return {"tag": r["tag"], "cond": r["cond"], "n_img": r["n_img"], "n_mobile": r["n_mobile"],
            "gate_accepted": r["gate_accepted"], "dU_published": dU_pub,
            "dU_climb_recomputed": r["dU_climb"], "rel_diff_recomputed_vs_stored": r["rel_diff_vs_stored"],
            "dU_rep_img": rep_img, "dU_span_img": sp, "span_i": si, "span_j": sj,
            "span_minus_rep_rel": (sp - rep_img) / max(abs(rep_img), 1e-12),
            "affected": abs(sp - rep_img) > REL * abs(rep_img),
            "first_saddle_img_J": float(E[first_max]), "first_saddle_image": int(first_max),
            "n_interior_minima": len(mins), "minima": mins,
            "deepest_min_E_J": deepest["E_image_J"] if deepest else None,
            "deepest_min_E_M_J": deepest["E_M_J"] if deepest else None,
            "exit_from_deepest_img_J": deepest["exit_barrier_img_J"] if deepest else None,
            "exit_from_deepest_M_J": deepest["exit_barrier_M_J"] if deepest else None,
            "exit_from_deepest_accepted": deepest["exit_M_accepted"] if deepest else None,
            "dU_span": dU_span, "dU_span_source": span_src,
            "exit_saddle_rel_s0_J": (deepest["E_M_J"] + deepest["exit_barrier_M_J"]) if deepest and
            deepest["exit_barrier_M_J"] is not None else None,
            "kind": kind(dU_pub, dU_span, deepest, abs(sp - rep_img) > REL * abs(rep_img)),
            "k_exit": k_exit, "blocker_x_exit": float(bx[k_exit]), "E_exit_J": float(E[-1]),
            "rep_img_whole_path_J": float(Ew.max() - Ew[0]),
            "max_beyond_exit_J": float(Ew[k_exit:].max() - Ew[0]), "F_perp_max": r["F_perp_max"]}


def load_paths():
    G = {g["job_id"]: g for g in load_runs(os.path.join(DATA, "BAR", "gate.jsonl"))}
    R = {r["job_id"]: r for r in load_runs(os.path.join(D, "x1_paths.jsonl"))}
    P = {}
    for tag, g in G.items():
        for c in CONDS:
            src = c if not g[c].get("same_as") else g[c]["same_as"]
            r = R.get(f"{tag}|{src}")
            if r is None:
                continue
            row = per_path(dict(r, cond=c), g[c])
            row["same_as"] = g[c].get("same_as")
            P[(tag, c)] = row
    return G, P


# ---------------------------------------------------------------- re-analyses
def rean_E4(P):
    spec = importlib.util.spec_from_file_location("E4analyze", os.path.join(ROOT, "experiments", "E4", "analyze.py"))
    E4a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E4a)
    rows = [json.loads(l) for l in open(E4a.IN)]
    out_rows, subst = [], {}
    for r in rows:
        tag, c = r["snap"][:-4], r["cond"]
        p = P[(tag, c)]
        r = dict(r)
        if p["affected"]:
            subst[(tag, c)] = (r["dU_cond"], p["dU_span"])
            r["dU_cond"] = p["dU_span"]
        out_rows.append(r)
    tmp_in = os.path.join(REAN, "e4_escape_span.jsonl")
    with open(tmp_in, "w") as f:
        for r in out_rows:
            f.write(json.dumps(r) + "\n")
    E4a.IN, E4a.OUT, E4a.FIG4 = tmp_in, os.path.join(REAN, "E4_analysis_span.json"), os.path.join(REAN, "fig4_span.json")
    E4a.main()
    return json.load(open(E4a.OUT)), {f"{k[0]}|{k[1]}": v for k, v in subst.items()}


def collapse(E4):
    import fix_a3
    return fix_a3.collapse_part(E4, np.random.default_rng(fix_a3.SEED))


def rean_E3(P):
    sys.modules.pop("analyze", None)
    sys.path.insert(0, os.path.join(ROOT, "experiments", "E3"))
    spec = importlib.util.spec_from_file_location("E3analyze", os.path.join(ROOT, "experiments", "E3", "analyze.py"))
    E3a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E3a)
    orig_load = E3a.load
    subst = {}

    def load():
        by, meta = orig_load()
        for tag, m in meta.items():
            p = P[(tag, "full")]
            assert abs(m["dU_i"] - p["dU_published"]) < 1e-6 * max(1, abs(m["dU_i"])), (tag, m["dU_i"], p["dU_published"])
            if p["affected"]:
                f = p["dU_span"] / m["dU_i"]
                subst[tag] = (m["dU_i"], p["dU_span"])
                m["dU_i"] = p["dU_span"]
                m["ell_pred_per_step"] *= f
                m["ell_pred_dt_scaled"] *= f
                for k, rows in by.items():
                    if k[0] == tag:
                        for r in rows:
                            if r.get("beta") is not None:
                                r["beta"] = r["beta"] * f
        return by, meta
    E3a.load = load
    E3a.OUT, E3a.FIG5 = os.path.join(REAN, "E3_analysis_span.json"), os.path.join(REAN, "fig5_span.json")
    E3a.main()
    return json.load(open(E3a.OUT)), subst


def rean_A3(P):
    import A3_beta
    from teff import kT_eff
    G = load_runs(os.path.join(DATA, "BAR", "gate.jsonl"))
    E1 = {f"{r['mode']}_seed{r['seed']}": r for r in load_runs(os.path.join(DATA, "E1", "E1_runs.jsonl"))}
    levels = {"s0p07": 0.07,
              "s0p0717": json.load(open(os.path.join(DERIVED, "N1_analysis.json")))["sigma_n1"],
              "sstar": json.load(open(os.path.join(DERIVED, "sigma_star.json")))["sigma_star"]}
    rows = []
    for g in G:
        f = g["full"]
        if not f.get("accepted") or f.get("dU") is None or f["dU"] <= 0:
            continue
        tau = next(a["tau"] for a in E1[g["job_id"]]["attrs"] if a["id"] == g["blocker"])
        rows.append({"snap": g["job_id"], "dU": f["dU"], "dU_span": P[(g["job_id"], "full")]["dU_span"], "tau": tau})
    out = {"n": len(rows), "levels": {}}
    for name, s in levels.items():
        b_rep = [r["dU"] / kT_eff(s, A3_beta.DT, r["tau"]) for r in rows]
        b_sp = [r["dU_span"] / kT_eff(s, A3_beta.DT, r["tau"]) for r in rows]
        out["levels"][name] = {"sigma": s, "published_recomputed": A3_beta.stats(b_rep), "span": A3_beta.stats(b_sp),
                               "changed": [{"snap": r["snap"], "dU": r["dU"], "dU_span": r["dU_span"],
                                            "beta_rep": a, "beta_span": b}
                                           for r, a, b in zip(rows, b_rep, b_sp) if abs(b - a) > 1e-9]}
    return out


def main():
    G, P = load_paths()
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))
    lib56 = sorted(t for t, g in G.items() if g["full"]["accepted"] and g["full"]["dU"] > 0)
    rejected = sorted(t for t, g in G.items() if not g["full"]["accepted"])
    assert len(lib56) == 56 and len(rejected) == 4, (len(lib56), len(rejected))
    E4set = sorted(s["tag"] for s in sel["E4"]["snapshots"])
    E3set = sorted(s["tag"] for s in sel["E3"]["snapshots"])
    recomp = [p["rel_diff_recomputed_vs_stored"] for p in P.values() if not p["same_as"]]
    out = {"doc": __doc__, "n_paths_computed": len(recomp), "swing_J": SWING, "rel_threshold": REL,
           "recompute_rel_diff_max": float(max(recomp)),
           "recompute_rel_diff_median": float(np.median(recomp)),
           "barrier_set": lib56, "rejected": rejected, "E4_set": E4set, "E3_set": E3set}
    per_cond = {}
    for c in CONDS:
        rows = [P[(t, c)] for t in lib56]
        aff = [p for p in rows if p["affected"]]
        per_cond[c] = {"n": len(rows), "n_affected": len(aff), "affected": [p["tag"] for p in aff],
                       "n_with_interior_minima": sum(p["n_interior_minima"] > 0 for p in rows),
                       "with_interior_minima": [p["tag"] for p in rows if p["n_interior_minima"] > 0]}
    out["per_condition"] = per_cond
    out["rejected_full"] = {t: P[(t, "full")] for t in rejected}
    out["paths"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(P.items())}
    # snapshots whose Kramers rate with dU_rep is not the exit rate: span exceeds rep, or the path has a deeper rest
    # state that the blocker leaves over a barrier different from dU_rep
    out["kramers_not_exit"] = {c: [p["tag"] for p in (P[(t, c)] for t in lib56 + rejected) if p["affected"]]
                               for c in CONDS}
    out["E4_affected"] = {c: [t for t in E4set if P[(t, c)]["affected"]] for c in CONDS}
    out["E3_affected"] = [t for t in E3set if P[(t, "full")]["affected"]]
    # E3 selection rule (gate-accepted full barrier and dU >= 3 J): which snapshots qualify with dU_span instead
    q_pub = sorted(t for t in lib56 if G[t]["full"]["dU"] >= 3.0)
    q_sp = sorted(t for t in lib56 if P[(t, "full")]["dU_span"] >= 3.0)
    out["E3_selection_rule"] = {"n_qualifying_published": len(q_pub), "n_qualifying_span": len(q_sp),
                                "enter_with_span": sorted(set(q_sp) - set(q_pub)),
                                "leave_with_span": sorted(set(q_pub) - set(q_sp)),
                                "check_published_equals_selection": len(q_pub) == sel["E3"].get("n_qualifying", len(q_pub))}
    e4s, e4sub = rean_E4(P)
    e4p = json.load(open(os.path.join(DERIVED, "E4_analysis.json")))
    out["E4"] = {"substituted": e4sub,
                 "published": {k: e4p["headline"][k] for k in e4p["headline"]},
                 "span": {k: e4s["headline"][k] for k in e4s["headline"]},
                 "published_ratios": {f"{t}|{c}": (v["arrhenius"] or {}).get("ratio")
                                      for t, s in e4p["snapshots"].items() for c, v in s["conds"].items()},
                 "span_ratios": {f"{t}|{c}": (v["arrhenius"] or {}).get("ratio")
                                 for t, s in e4s["snapshots"].items() for c, v in s["conds"].items()},
                 "span_ratio_ci": {f"{t}|{c}": (v["arrhenius"] or {}).get("ratio_ci95")
                                   for t, s in e4s["snapshots"].items() for c, v in s["conds"].items()},
                 "per_condition_span": {c: {k: e4s["per_condition"][c][k] for k in
                                            ("n_arrhenius_fits", "ratio_median", "ratio_min", "ratio_max",
                                             "ratio_ci_covers_1", "nu_hat_median")} for c in CONDS}}
    fa3 = json.load(open(os.path.join(DERIVED, "fix_a3.json")))["collapse"]
    cp, cs = collapse(e4p), collapse(e4s)
    out["E4"]["pooled_slope"] = {
        "published_file": fa3["free_intercepts"],
        "published_refit_fresh_rng": cp["free_intercepts"], "span_fresh_rng": cs["free_intercepts"],
        "published_common_intercept_refit": cp["common_intercept"]["slope"],
        "span_common_intercept": cs["common_intercept"]["slope"],
        "span_common_intercept_ci95": cs["common_intercept"]["slope_ci95"],
        "n_points": cs["n_points"],
        "note": "fix_a3.main draws this bootstrap after other bootstraps on the same generator; here collapse_part runs "
                "on a fresh PCG64(fix_a3.SEED) for both inputs, so the published point estimate is reproduced exactly "
                "and its interval to bootstrap resolution"}
    e3s, e3sub = rean_E3(P)
    e3p = json.load(open(os.path.join(DERIVED, "E3_analysis.json")))
    keys = ("slope", "slope_lo", "slope_hi", "slope_origin", "slope_origin_lo", "slope_origin_hi",
            "ell_ps_b1p5_pred", "ell_ps_b2p5_pred", "ell_ds_pred")
    out["E3"] = {"substituted": e3sub, "published": {k: e3p["headline"][k] for k in keys},
                 "span": {k: e3s["headline"][k] for k in keys},
                 "covers_pred_published": e3p["ell"]["per_step"]["snapshot_ci_covers_pred"],
                 "covers_pred_span": e3s["ell"]["per_step"]["snapshot_ci_covers_pred"],
                 "n_ell": e3s["ell"]["per_step"]["n"]}
    out["A3"] = rean_A3(P)
    out["headline"] = headline(out)
    rev5lib.out_json("X1", out)
    brief(out)


def headline(o):
    """Flat scalars for the registry (notes/C4_items/X1.yaml)."""
    h = {"n_barrier_set": len(o["barrier_set"]), "n_rejected": len(o["rejected"]),
         "n_paths": o["n_paths_computed"], "recompute_rel_diff_max": o["recompute_rel_diff_max"],
         "swing_J": o["swing_J"], "rel_threshold_pct": 100 * o["rel_threshold"]}
    for c in CONDS:
        h[f"n_affected_{c}"] = o["per_condition"][c]["n_affected"]
        h[f"n_minima_{c}"] = o["per_condition"][c]["n_with_interior_minima"]
    rj = o["rejected_full"]
    h["n_affected_rejected"] = sum(p["affected"] for p in rj.values())
    aff = [o["paths"][f"{t}|full"] for t in o["per_condition"]["full"]["affected"]]
    h["aff_rep_min"] = min(p["dU_published"] for p in aff)
    h["aff_rep_max"] = max(p["dU_published"] for p in aff)
    h["aff_span_min"] = min(p["dU_span"] for p in aff)
    h["aff_span_max"] = max(p["dU_span"] for p in aff)
    h["aff_depth_min"] = min(-p["deepest_min_E_M_J"] for p in aff)
    h["aff_depth_max"] = max(-p["deepest_min_E_M_J"] for p in aff)
    h["aff_all_exit_accepted"] = all(p["exit_from_deepest_accepted"] for p in aff)
    h["n_minima_unaffected_full"] = h["n_minima_full"] - h["n_affected_full"]
    h["n_kind_A_full"] = sum(p["kind"] == "A" for p in aff)
    h["n_kind_B_full"] = sum(p["kind"] == "B" for p in aff)
    h["kind_A_full"] = [p["tag"] for p in aff if p["kind"] == "A"]
    h["kind_B_full"] = [p["tag"] for p in aff if p["kind"] == "B"]
    h["kind_rejected"] = {t: p["kind"] for t, p in rj.items()}
    for t in ("E1b_seed170", "E1b_seed237", "E1b_seed46", "E1b_seed230"):
        p = o["paths"][f"{t}|full"]
        k = t.replace("E1b_seed", "s")
        h[f"{k}_rep"], h[f"{k}_span"], h[f"{k}_minE"] = p["dU_published"], p["dU_span"], p["deepest_min_E_M_J"]
    e4p, e4s = o["E4"]["published"], o["E4"]["span"]
    for c in CONDS:
        h[f"e4_ratio_med_{c}_pub"] = e4p[f"ratio_med_{c}"]
        h[f"e4_ratio_med_{c}_span"] = e4s[f"ratio_med_{c}"]
        h[f"e4_cover_{c}_span"] = e4s[f"ratio_cover_{c}"]
        h[f"e4_nfit_{c}_span"] = e4s[f"nfit_{c}"]
    h["e4_s237_ratio_pub"] = o["E4"]["published_ratios"]["E1b_seed237|full"]
    h["e4_s237_ratio_span"] = o["E4"]["span_ratios"]["E1b_seed237|full"]
    h["e4_s237_ratio_span_lo"], h["e4_s237_ratio_span_hi"] = o["E4"]["span_ratio_ci"]["E1b_seed237|full"]
    ps = o["E4"]["pooled_slope"]
    h["pool_pub"], (h["pool_pub_lo"], h["pool_pub_hi"]) = ps["published_file"]["slope"], ps["published_file"]["slope_ci95"]
    h["pool_pubrefit"], (h["pool_pubrefit_lo"], h["pool_pubrefit_hi"]) = \
        ps["published_refit_fresh_rng"]["slope"], ps["published_refit_fresh_rng"]["slope_ci95"]
    h["pool_span"], (h["pool_span_lo"], h["pool_span_hi"]) = ps["span_fresh_rng"]["slope"], ps["span_fresh_rng"]["slope_ci95"]
    for k in ("slope", "slope_lo", "slope_hi", "slope_origin", "slope_origin_lo", "slope_origin_hi"):
        h[f"e3_{k}_pub"], h[f"e3_{k}_span"] = o["E3"]["published"][k], o["E3"]["span"][k]
    h["e3_cover_pub"], h["e3_cover_span"] = o["E3"]["covers_pred_published"], o["E3"]["covers_pred_span"]
    h["e3_qual_pub"] = o["E3_selection_rule"]["n_qualifying_published"]
    h["e3_qual_span"] = o["E3_selection_rule"]["n_qualifying_span"]
    for name, v in o["A3"]["levels"].items():
        for arm in ("published_recomputed", "span"):
            a = "pub" if arm == "published_recomputed" else "span"
            h[f"a3_{name}_{a}_below1"] = v[arm]["n_below_1"]
            h[f"a3_{name}_{a}_median"] = v[arm]["median"]
            h[f"a3_{name}_{a}_q25"], h[f"a3_{name}_{a}_q75"] = v[arm]["q25"], v[arm]["q75"]
            h[f"a3_{name}_{a}_below1_lo"], h[f"a3_{name}_{a}_below1_hi"] = v[arm]["frac_below_1_ci95"]
    return h


def brief(o):
    print("recompute rel diff max", o["recompute_rel_diff_max"])
    for c, v in o["per_condition"].items():
        print(c, "affected", v["n_affected"], v["affected"], "with minima", v["n_with_interior_minima"])
    for t, p in o["rejected_full"].items():
        print("rejected", t, "affected", p["affected"], "rep", p["dU_rep_img"], "span", p["dU_span_img"])
    print("E4 affected", o["E4_affected"], "E3 affected", o["E3_affected"])
    print("E4 pub", {k: o["E4"]["published"][k] for k in ("ratio_med_full", "ratio_med_frozen", "ratio_med_alone")})
    print("E4 span", {k: o["E4"]["span"][k] for k in ("ratio_med_full", "ratio_med_frozen", "ratio_med_alone")})
    print("pooled", o["E4"]["pooled_slope"]["published_refit_fresh_rng"], o["E4"]["pooled_slope"]["span_fresh_rng"])
    print("E3", o["E3"]["published"], o["E3"]["span"])
    a = o["A3"]["levels"]["s0p07"]
    print("A3 0.07", a["published_recomputed"]["n_below_1"], a["published_recomputed"]["median"],
          a["span"]["n_below_1"], a["span"]["median"])


if __name__ == "__main__":
    main()
