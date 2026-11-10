"""B5 analysis: the pair standoff with rounded jamb ends, and the work across the biased rest field.

Inputs (data/revision/B5/): reequil.jsonl, cont.jsonl, bisect.jsonl, barrier_sharp.jsonl (B5_static.py), and when
present quench.jsonl (B5_quench.py) and gen_rounded.jsonl (B5_gen.py); data/N6/n6_static.jsonl and
data/derived/N6_analysis.json (sharp-edge reference); data/E7b_bstar/fold_threshold.jsonl (sharp b*).
Output: data/derived/rev_B5.json.
  reequil    per r_c: strict minima kept (Hessian positive definite, contact-free, x < 10, opposite sides),
             flowed out (relaxation frees a member), converged elsewhere / undecided; displacement of the kept
             minima; the geometric rule "kept iff overhang > r_c", overhang = min over members of |y - 5| - w/2
             (how far the inner member's centre lies beyond the door edge, behind the flat jamb face), checked on
             every (snapshot, r_c).
  cont       r_c = 0.02 m: fold cases, log-log slopes against delta = 1 - b/b_f (delta 0.3 ... 0.001) of the
             minimum-saddle distance, mu1 at the minimum, W_line and W_flow; member at a segment end at the
             fold (face / cap transition); b_f against the bisection b*.
  barrier    curl of the biased rest field (measured / predicted -c b / (sqrt(1+b^2) rho)), cross-member
             antisymmetry, path dependence W_rel = (W_line - W_flow)/W_flow, for the sharp folds and r_c = 0.02.
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revlib  # noqa: E402
import numpy as np  # noqa: E402
import stats3  # noqa: E402
from revlib import sig  # noqa: E402

D = os.path.join(revlib.DATA, "revision", "B5")
W_HALF = 0.4


def jl(p):
    return revlib.load_runs(p) if os.path.exists(p) else []


def summ(v, n=2):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {"median": sig(float(np.median(v)), n), "min": sig(float(min(v)), n), "max": sig(float(max(v)), n),
            "n": len(v), "raw_median": float(np.median(v)), "raw_min": float(min(v)), "raw_max": float(max(v))}


def slopes(sc, key, pos=True):
    x = [s for s in sc if s.get("converged") and s.get("distinct") and s.get(key) is not None]
    if pos and not all(s[key] > 0 for s in x):
        return None
    r = stats3.loglog_slope([s["delta"] for s in x], [s[key] for s in x])
    return None if r is None else r["slope"]


def scan_summary(rows):
    sl = defaultdict(list)
    curl_ratio, cross, wrel, wrel_small, flow_ok, mu_ratio, jj, wbig, w03, curl_mu = [], [], [], [], [], [], [], [], [], []
    for r in rows:
        sc = r["scan"]
        for k in ("dist", "mu1_min", "W_line", "W_flow"):
            s = slopes(sc, k)
            if s is not None:
                sl[k].append(s)
        good = [s for s in sc if s.get("converged") and s.get("distinct")]
        for s in good:
            curl_ratio += [m / p for m, p in zip(s["curl"], s["curl_pred"]) if p]
            cross.append(s["cross_asym"] / s["sym_scale"])
            if s.get("W_rel") is not None:
                wrel.append(abs(s["W_rel"]))
                wbig.append((abs(s["W_rel"]), s["W_flow"]))
            flow_ok.append(bool(s.get("flow_reached")) and s.get("flow_end_err", 1) < 2e-3)
        if good:
            w03.append(good[0]["W_flow"] if good[0].get("W_flow") is not None else None)
            curl_mu.append(max(abs(c) for c in good[-1]["curl"]) / good[-1]["mu1_min"])
            mu_ratio.append(good[-1]["mu1_min"] / good[0]["mu1_min"])
            jj.append(good[-1]["jac_jump"])
            if good[-1].get("W_rel") is not None:
                wrel_small.append(abs(good[-1]["W_rel"]))
    out = {"n": len(rows), "slopes": {k: summ(v, 3) for k, v in sl.items()},
           "dist_within_0p1_of_1": int(sum(abs(x - 1) <= 0.1 for x in sl["dist"])),
           "dist_within_0p1_of_0p5": int(sum(abs(x - 0.5) <= 0.1 for x in sl["dist"])),
           "mu1_slope_abs_below_0p01": int(sum(abs(x) < 0.01 for x in sl["mu1_min"])),
           "mu1_ratio_smallest_to_largest_delta": summ(mu_ratio, 4), "jac_jump_smallest_delta": summ(jj),
           "curl_over_pred": summ(curl_ratio, 3), "cross_asym_rel": summ(cross),
           "W_rel_abs": summ(wrel), "W_rel_abs_smallest_delta": summ(wrel_small),
           "flow_reached_min": int(sum(flow_ok)), "flow_n": len(flow_ok),
           "W_rel_le_0p01": int(sum(x <= 0.01 for x, _ in wbig)),
           "W_rel_gt_0p01_max_W_flow_J": max([w for x, w in wbig if x > 0.01], default=None),
           "W_flow_delta0p3_J": summ(w03), "curl_over_mu1_smallest_delta": summ(curl_mu)}
    return out


def main():
    o = {"script": "experiments/revision/B5_analyze.py", "doc": __doc__}
    # ---------------- reequil
    R = jl(os.path.join(D, "reequil.jsonl"))
    from e7b_pairs import pairs
    import pickle
    over = {}
    for p in pairs():
        snap = pickle.load(open(p["snap"], "rb"))
        st = snap["state"]
        ids = [int(i) for i in st.active_indices]
        over[p["tag"]] = float(min(abs(st.positions[ids, 1] - 5.0)) - W_HALF)
    ov = list(over.values())
    o["overhang_mm"] = {k: (sig(v * 1e3, 2) if k in ("median", "min", "max") else v)
                        for k, v in summ(ov, 6).items()}
    o["overhang_mm"]["below_100mm"] = int(sum(x < 0.1 for x in ov))
    by = defaultdict(list)
    for r in R:
        by[f"{r['rc']:g}"].append(r)
    re = {}
    for rc, v in sorted(by.items(), key=lambda kv: -float(kv[0])):
        kept = [r for r in v if r["kept"]]
        freed = [r for r in v if r["relax_freed"]]
        mism = sum((over[r["tag"]] > r["rc"]) != r["kept"] for r in v)
        re["rc" + rc.replace(".", "p")] = {"n": len(v), "kept": len(kept), "freed": len(freed),
                  "elsewhere_or_undecided": len(v) - len(kept) - len(freed),
                  "freed_first_side": dict(Counter(r["first_side"] for r in freed)),
                  "freed_time_s": summ([r["relax_t"] for r in freed]),
                  "move_kept_m": summ([r["move_max"] for r in kept]),
                  "mu1_kept": summ([r["eig"][0] for r in kept], 3),
                  "rule_mismatch": int(mism)}
    o["reequil"] = re
    main_rc = re.get("rc0p1", {})
    o["main"] = {"rc": 0.1, "n": main_rc.get("n"), "kept": main_rc.get("kept"), "lost": (main_rc.get("n") or 0) - (main_rc.get("kept") or 0),
                 "freed": main_rc.get("freed"), "rule_mismatch_total": int(sum(x["rule_mismatch"] for x in re.values())),
                 "n_checked": len(R)}
    # sharp reference at b = 0 (same field, sharp edge): from N6 analysis
    # ---------------- cont / bisect
    C = jl(os.path.join(D, "cont.jsonl"))
    Bi = {r["job_id"]: r for r in jl(os.path.join(D, "bisect.jsonl"))}
    Fs = {r["job_id"]: r for r in jl(os.path.join(revlib.DATA, "E7b_bstar", "fold_threshold.jsonl"))}
    if C:
        fold = [r for r in C if r.get("b_f") is not None]
        cs = scan_summary(fold)
        nat = [r for r in C if r.get("b_f") is None]
        cs.update({"n_jobs": len(C), "n_snapshots": len({r["tag"] for r in C}), "n_fold": len(fold),
                   "status": dict(Counter(r["status"] for r in C)),
                   "end_at_fold": int(sum(r["end_at_fold"] for r in fold)),
                   "end_at_scan_min": int(sum(bool(r["scan"][-1].get("end_min")) for r in fold)),
                   "end_at_scan_saddle": int(sum(bool(r["scan"][-1].get("end_saddle")) for r in fold)),
                   "natural_end_last_all": int(sum(r["natural"]["end_last"] for r in C)),
                   "natural_b_last_over_b_f": summ([r["natural"]["b_last"] / r["b_f"] for r in fold], 4),
                   "mu1_at_loss": summ([r["scan"][-1]["mu1_min"] for r in fold if r["scan"][-1].get("converged")]
                                       + [r["natural"]["mu1_last"] for r in nat], 3),
                   "mu1_last_over_b0_natural": summ([r["natural"]["mu1_last"] / r["natural"]["mu1_b0"] for r in nat], 3),
                   "b_f_over_bstar": summ([r["b_f"] / Bi[r["job_id"]]["b_star"] for r in fold
                                          if Bi.get(r["job_id"], {}).get("b_star")], 3)})
        o["cont_rc0p02"] = cs
    if Bi:
        lowb = defaultdict(dict)
        for r in Bi.values():
            if r["b_star"] is not None:
                lowb[r["tag"]][r["sign"]] = r["b_star"]
        lower = [min(v.values()) for v in lowb.values() if len(v) == 2]
        ratio = []
        for jid, r in Bi.items():
            sj = jid.split("|", 1)[1]
            if r["b_star"] and Fs.get(sj, {}).get("b_star"):
                ratio.append(r["b_star"] / Fs[sj]["b_star"])
        o["bisect_rc0p02"] = {"n": len(Bi), "decided": int(sum(r["b_star"] is not None for r in Bi.values())),
                              "lower_sign_bstar": summ(lower, 2), "bstar_over_sharp_bstar": summ(ratio, 3),
                              "undecided_calls": int(sum(r["undecided_calls"] for r in Bi.values())),
                              "first_side": dict(Counter(r["first_side_at_hi"] for r in Bi.values()))}
    # ---------------- barrier (sharp)
    Bs = jl(os.path.join(D, "barrier_sharp.jsonl"))
    if Bs:
        bs = scan_summary(Bs)
        n6 = json.load(open(os.path.join(revlib.DERIVED, "N6_analysis.json")))
        bs["N6_reference_slopes"] = {k: n6["slopes"][k]["median"] for k in ("dist", "W", "mu1")}
        o["barrier_sharp"] = bs
    # ---------------- quench (queued)
    Q = jl(os.path.join(D, "quench.jsonl"))
    if Q:
        q = {}
        b0 = [r for r in Q if r["arm"] == "b0"]
        q["b0"] = {"n": len(b0), "freed": int(sum(r["freed"] for r in b0)),
                   "all_freed": int(sum(r["all_freed"] for r in b0)), "first_t": summ([r["first_t"] for r in b0 if r["freed"]])}
        fo = [r for r in Q if r["arm"] == "fold"]
        eps = sorted({r["eps"] for r in fo})
        q["fold"] = {f"{e:g}": {"n": sum(r["eps"] == e for r in fo), "freed": int(sum(r["freed"] for r in fo if r["eps"] == e)),
                                "passage_s": summ([r["first_t"] for r in fo if r["eps"] == e and r["freed"]])} for e in eps}
        gr = [r for r in Q if r["arm"] == "grid" and r["static_freed"] is not None]
        agree = sum(r["static_freed"] == r["freed"] for r in gr)
        p, lo, hi = revlib.wilson(agree, len(gr)) if gr else (None, None, None)
        q["grid"] = {"n": len(gr), "agree": int(agree), "wilson_lo": lo,
                     "freed_below_static": int(sum(r["freed"] and not r["static_freed"] for r in gr)),
                     "held_above_static": int(sum(r["static_freed"] and not r["freed"] for r in gr))}
        o["quench"] = q
    if Bs:
        b = o["barrier_sharp"]
        o["report"] = {"W_rel_median_pct": sig(100 * b["W_rel_abs"]["raw_median"], 2),
                       "W_rel_median_pct_rc0p02": sig(100 * o["cont_rc0p02"]["W_rel_abs"]["raw_median"], 2)
                       if "cont_rc0p02" in o else None,
                       "curl_over_mu1_median_pct": sig(100 * b["curl_over_mu1_smallest_delta"]["raw_median"], 2)}
    G = jl(os.path.join(D, "gen_rounded.jsonl"))
    if G:
        import B6_analyze
        o["gen"] = B6_analyze.gen_summary(G)
    revlib.out_json("B5", o)
    return o


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: v for k, v in o.items() if k != "doc"}, indent=1, default=float)[:6000])
