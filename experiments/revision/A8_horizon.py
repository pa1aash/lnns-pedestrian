"""A8: horizon dependence of the freed fraction and of the fraction match (surrogate minus force-coupled ORCA).

Inputs (existing data only; an outcome at horizon T is read off the recorded exit time, exit time <= T):
  data/E2/e2_quench.jsonl + data/derived/selection.json   lone-trap snapshots (34 lone keystones, 26 second
        traps); arms noise0.03, noise0.05, noise0.07 (5 seeds per snapshot), C3_rvo2, C3_pub, drive_only,
        frozen_plus, frozen_minus (unperturbed run per snapshot). Freed: blocker exit time <= T.
  data/N1/n1.jsonl     lone keystones only, sigma = 0.0717 m/s, 20 seeds per snapshot.
  data/E7b/e7b_quench.jsonl + data/E7b_bstar/bstar_quench.jsonl   46 pair standoffs; C3_pub, C3_rvo2,
        bstar_pub+ (b*_legacy), bstar_rvo2+ (b*_RVO2), unperturbed runs. Freed: freed and first member exit
        time first_t <= T (make_tables45.py derive rule).
  data/E6/e6a.jsonl (C3 RVO2), data/E6/e6b.jsonl (C1 + sigma*), data/N2/n2.jsonl (C1 + sigma*, second
        noise stream on the same spawns); 186 seeds. Completed by T: complete and evacuation_time <= T.
Horizons: snapshots 60 s and 120 s (the quench window is 120 s); whole runs 300 s and 600 s (t_max 600 s).
Output: data/derived/rev_A8.json

  freed fraction   noise arms over runs (k/(5n) or k/(20n)); deterministic arms over snapshots; whole runs over seeds.
  Delta            mean over units of (surrogate freed fraction of the unit minus ORCA outcome of the unit):
                   per snapshot k_i/m - c_i for noise, c'_i - c_i for deterministic arms, per seed for whole runs.
                   95% percentile bootstrap over units, 2000 resamples, a fresh PCG64(12345) per comparison
                   (the E2 analyze.py / make_tables45.py rule). Whole runs also carry the Newcombe paired interval
                   (method 10, the Esix rule).
  fraction-matched at T   the 95% interval of Delta covers 0.
  horizon-specific        fraction-matched at one horizon of the pair and not at the other.
  scans            Delta(T) of every noise arm against ORCA (RVO2) for T = 10, 15, ..., 120 s (snapshots) and
                   T = 150, 175, ..., 600 s (whole runs), same bootstrap; matched_T_s lists the T where the 95%
                   interval covers 0. latest_exit_s: the latest blocker (pair: first member) exit of each
                   deterministic arm, showing where its freed fraction stops changing.
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
import numpy as np  # noqa: E402
import stats3  # noqa: E402  (experiments/runs3, on sys.path via revlib)

H_SNAP = (60.0, 120.0)
H_WHOLE = (300.0, 600.0)
SCAN_SNAP = [float(x) for x in range(10, 121, 5)]
SCAN_WHOLE = [float(x) for x in range(150, 601, 25)]
N_BOOT, RNG_SEED = 2000, 12345
E2_ARMS = ["noise0.03", "noise0.05", "noise0.07", "C3_rvo2", "C3_pub", "drive_only", "frozen_plus", "frozen_minus"]
NOISE = {"noise0.03": 0.03, "noise0.05": 0.05, "noise0.07": 0.07}
STRATA = ["lone_keystone", "lone_keystone_second_trap"]


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def key(a):
    return a.replace(".", "p").replace("+", "_plus")


def load_lone():
    sel = json.load(open(os.path.join(revlib.DERIVED, "selection.json")))["E2"]["snapshots"]
    snaps = {s["tag"]: s for s in sel}
    ex = defaultdict(dict)  # ex[(tag, arm)][rep] = blocker exit time or None
    for r in jl(os.path.join(revlib.DATA, "E2", "e2_quench.jsonl")):
        tag, arm, rep = r["job_id"].split("|")
        if arm in E2_ARMS:
            ex[(tag, arm)][rep] = r["exits"].get(str(snaps[tag]["blocker"]))
    for r in jl(os.path.join(revlib.DATA, "N1", "n1.jsonl")):
        tag = r["job_id"].split("|")[0]
        ex[(tag, "noiseN1")][str(r["rep"])] = r["exits"].get(str(snaps[tag]["blocker"]))
    return sel, ex


def boot(v, rng):
    n = len(v)
    b = [v[rng.integers(0, n, n)].mean() for _ in range(N_BOOT)]
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def frac_matrix(ex, T, arm, H):
    """Per-unit freed fraction at horizon H (noise: over seeds; deterministic: the unperturbed run)."""
    out = []
    for t in T:
        rr = ex[(t, arm)]
        if arm.startswith("noise"):
            v = [x is not None and x <= H + 1e-9 for x in rr.values()]
        else:
            x = rr["u"]
            v = [x is not None and x <= H + 1e-9]
        out.append((sum(v), len(v)))
    return out


def cmp(sur, orc, rng_seed=RNG_SEED):
    d = np.asarray(sur, float) - np.asarray(orc, float)
    rng = np.random.Generator(np.random.PCG64(rng_seed))
    ci = boot(d, rng)
    return {"delta": float(d.mean()), "ci95": ci, "matched": bool(ci[0] <= 0 <= ci[1]),
            "delta_disp": revlib.sig(float(d.mean())), "lo_disp": revlib.sig(ci[0]), "hi_disp": revlib.sig(ci[1])}


def lone_block(sel, ex):
    out = {}
    for st in STRATA:
        T = [s["tag"] for s in sel if s["class"] == st]
        arms = E2_ARMS + (["noiseN1"] if st == "lone_keystone" else [])
        o = {"n_snapshots": len(T), "arms": {}, "delta": {}}
        for H in H_SNAP:
            h = f"T{int(H)}"
            fm = {a: frac_matrix(ex, T, a, H) for a in arms}
            for a in arms:
                k = sum(x[0] for x in fm[a])
                n = sum(x[1] for x in fm[a])
                w = revlib.wilson(k, n)
                o["arms"].setdefault(key(a), {})[h] = {"freed": int(k), "n": int(n), "fraction": k / n,
                                                       "wilson95": [float(w[1]), float(w[2])]}
            for orca in ("C3_rvo2", "C3_pub"):
                c = [x[0] for x in fm[orca]]
                for a in arms:
                    if a.startswith("C3"):
                        continue
                    p = [x[0] / x[1] for x in fm[a]]
                    o["delta"].setdefault(f"{key(a)}_vs_{orca}", {})[h] = cmp(p, c)
        for k_, v in o["delta"].items():
            v["horizon_specific"] = v["T60"]["matched"] != v["T120"]["matched"]
        o["latest_exit_s"] = {key(a): max([x for t in T for x in ex[(t, a)].values() if x is not None] or [None])
                              for a in arms if not a.startswith("noise")}
        # horizon scan: Delta(T) of the noise arms against ORCA (RVO2), T = 10, 15, ..., 120 s
        c_all = {H: [x[0] for x in frac_matrix(ex, T, "C3_rvo2", H)] for H in SCAN_SNAP}
        o["scan_vs_C3_rvo2"] = {}
        for a in [x for x in arms if x.startswith("noise")]:
            sc = {}
            for H in SCAN_SNAP:
                p = [x[0] / x[1] for x in frac_matrix(ex, T, a, H)]
                c = cmp(p, c_all[H])
                sc[str(int(H))] = [c["delta"], c["ci95"][0], c["ci95"][1], c["matched"]]
            o["scan_vs_C3_rvo2"][key(a)] = {"T_s": sc, "matched_T_s": [int(H) for H in SCAN_SNAP if sc[str(int(H))][3]]}
        out[st] = o
    return out


def pair_block():
    first = {}
    for p in (os.path.join(revlib.DATA, "E7b", "e7b_quench.jsonl"),
              os.path.join(revlib.DATA, "E7b_bstar", "bstar_quench.jsonl")):
        for r in jl(p):
            tag, arm, rep = r["job_id"].split("|")
            if rep == "u" and arm in ("C3_pub", "C3_rvo2", "bstar_pub+", "bstar_rvo2+"):
                first[(tag, arm)] = r["first_t"] if r["freed"] else None
    tags = sorted({t for t, _ in first}, key=lambda t: int(t.rsplit("seed", 1)[1]))
    o = {"n_snapshots": len(tags), "arms": {}, "delta": {}}
    for H in H_SNAP:
        h = f"T{int(H)}"
        F = {a: np.array([first[(t, a)] is not None and first[(t, a)] <= H + 1e-9 for t in tags])
             for a in ("C3_pub", "C3_rvo2", "bstar_pub+", "bstar_rvo2+")}
        for a, v in F.items():
            w = revlib.wilson(int(v.sum()), len(v))
            o["arms"].setdefault(key(a), {})[h] = {"freed": int(v.sum()), "n": len(v), "fraction": float(v.mean()),
                                                   "wilson95": [float(w[1]), float(w[2])]}
        for b, orca in (("bstar_pub+", "C3_pub"), ("bstar_rvo2+", "C3_rvo2")):
            o["delta"].setdefault(f"{key(b)}_vs_{orca}", {})[h] = cmp(F[b], F[orca])
    for v in o["delta"].values():
        v["horizon_specific"] = v["T60"]["matched"] != v["T120"]["matched"]
    o["latest_first_exit_s"] = {key(a): max([first[(t, a)] for t in tags if first[(t, a)] is not None] or [None])
                                for a in ("C3_pub", "C3_rvo2", "bstar_pub+", "bstar_rvo2+")}
    return o


def whole_block():
    S = {k: {r["seed"]: r for r in jl(p)} for k, p in
         (("E6a_C3_rvo2", os.path.join(revlib.DATA, "E6", "e6a.jsonl")),
          ("E6b_noise_sigma_star", os.path.join(revlib.DATA, "E6", "e6b.jsonl")),
          ("N2_noise_sigma_star", os.path.join(revlib.DATA, "N2", "n2.jsonl")))}
    seeds = sorted(S["E6a_C3_rvo2"])
    assert seeds == sorted(S["E6b_noise_sigma_star"]) == sorted(S["N2_noise_sigma_star"])
    o = {"n_seeds": len(seeds), "sigma_star": S["E6b_noise_sigma_star"][seeds[0]]["sigma"], "arms": {}, "delta": {}}
    for H in H_WHOLE:
        h = f"T{int(H)}"
        C = {k: np.array([bool(v[s]["complete"]) and v[s]["evacuation_time"] <= H + 1e-9 for s in seeds])
             for k, v in S.items()}
        for k, v in C.items():
            w = revlib.wilson(int(v.sum()), len(v))
            o["arms"].setdefault(k, {})[h] = {"completed": int(v.sum()), "n": len(v), "fraction": float(v.mean()),
                                              "wilson95": [float(w[1]), float(w[2])]}
        y = C["E6a_C3_rvo2"]
        for k in ("E6b_noise_sigma_star", "N2_noise_sigma_star"):
            x = C[k]
            c = cmp(x, y)
            nw = stats3.newcombe_paired(int((x & y).sum()), int((x & ~y).sum()), int((~x & y).sum()),
                                        int((~x & ~y).sum()))
            c["newcombe95"] = nw["ci95"]
            c["matched_newcombe"] = bool(nw["ci95"][0] <= 0 <= nw["ci95"][1])
            c["discordant_noise_only"] = int((x & ~y).sum())
            c["discordant_orca_only"] = int((~x & y).sum())
            c["mcnemar_p"] = revlib.mcnemar_exact(c["discordant_noise_only"], c["discordant_orca_only"])
            c["mcnemar_p_disp"] = revlib.pdisp(c["mcnemar_p"])
            o["delta"].setdefault(f"{k}_vs_E6a_C3_rvo2", {})[h] = c
    for v in o["delta"].values():
        v["horizon_specific"] = v["T300"]["matched"] != v["T600"]["matched"]
    # latest completion under ORCA (all completions happen before 300 s?)
    ev = [S["E6a_C3_rvo2"][s]["evacuation_time"] for s in seeds if S["E6a_C3_rvo2"][s]["complete"]]
    o["C3_rvo2_latest_completion_s"] = float(max(ev))
    o["scan_vs_E6a_C3_rvo2"] = {}
    y_all = {H: np.array([bool(S["E6a_C3_rvo2"][s]["complete"]) and S["E6a_C3_rvo2"][s]["evacuation_time"] <= H + 1e-9
                          for s in seeds]) for H in SCAN_WHOLE}
    for k in ("E6b_noise_sigma_star", "N2_noise_sigma_star"):
        sc = {}
        for H in SCAN_WHOLE:
            x = np.array([bool(S[k][s]["complete"]) and S[k][s]["evacuation_time"] <= H + 1e-9 for s in seeds])
            c = cmp(x, y_all[H])
            sc[str(int(H))] = [c["delta"], c["ci95"][0], c["ci95"][1], c["matched"]]
        o["scan_vs_E6a_C3_rvo2"][k] = {"T_s": sc, "matched_T_s": [int(H) for H in SCAN_WHOLE if sc[str(int(H))][3]]}
    return o


def summary(o):
    """Compact verdict table: matched at each horizon, per comparison."""
    rows = []
    for st in STRATA:
        for k, v in o["snapshots"][st]["delta"].items():
            rows.append({"block": st, "comparison": k,
                         **{h: [v[h]["delta_disp"], v[h]["lo_disp"], v[h]["hi_disp"], v[h]["matched"]]
                            for h in ("T60", "T120")}, "horizon_specific": v["horizon_specific"]})
    for k, v in o["pair"]["delta"].items():
        rows.append({"block": "pair", "comparison": k,
                     **{h: [v[h]["delta_disp"], v[h]["lo_disp"], v[h]["hi_disp"], v[h]["matched"]]
                        for h in ("T60", "T120")}, "horizon_specific": v["horizon_specific"]})
    for k, v in o["whole"]["delta"].items():
        rows.append({"block": "whole", "comparison": k,
                     **{h: [v[h]["delta_disp"], v[h]["lo_disp"], v[h]["hi_disp"], v[h]["matched"]]
                        for h in ("T300", "T600")}, "horizon_specific": v["horizon_specific"]})
    return rows


def main():
    sel, ex = load_lone()
    out = {"script": "experiments/revision/A8_horizon.py", "doc": __doc__,
           "snapshots": lone_block(sel, ex), "pair": pair_block(), "whole": whole_block()}
    out["summary"] = summary(out)
    print(revlib.out_json("A8", out))
    for r in out["summary"]:
        print(r)
    for st in STRATA:
        print(st, out["snapshots"][st]["latest_exit_s"])
        for a, v in out["snapshots"][st]["scan_vs_C3_rvo2"].items():
            print("  scan", a, v["matched_T_s"])
    print("pair latest", out["pair"]["latest_first_exit_s"])
    for a, v in out["whole"]["scan_vs_E6a_C3_rvo2"].items():
        print("  whole scan", a, v["matched_T_s"])


if __name__ == "__main__":
    main()
