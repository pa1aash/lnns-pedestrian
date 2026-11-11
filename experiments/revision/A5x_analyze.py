"""A5x: the Table 2 probes at the second trap on the 134 second-trap snapshots that E2 did not draw.

Inputs (read only)
  data/revision/A5/a5_quench.jsonl   134 new second traps x 21 jobs (experiments/revision/A5_extra_second_traps.py)
  data/E2/e2_quench.jsonl            the 26 E2 second traps (same arm definitions, experiments/E2/e2_quench.py)
  data/derived/selection.json        E2 snapshots: tag, blocker, class
Output: data/derived/rev_A5x.json

Groups: new (134 not drawn), E2 (the 26 drawn, stratum lone_keystone_second_trap), pooled (all 160).

Definitions (those of experiments/E2/analyze.py)
  freed        the blocker (keystone-test blocker, residual agent nearest (10, 5)) exits within T = 120 s.
               New runs: recomputed from "exits" and asserted equal to the stored "blocker_freed".
  det. arm     C3_rvo2, C3_pub, drive_only, frozen_plus, constraint_only_rvo2, C1: the unperturbed run per
               snapshot is the unit; the five 1e-9 m replays (perturb seeds 900-904; C3_rvo2 and C3_pub only)
               enter only the replay probe.
  noise0.07    C1 + sigma = 0.07 m/s, five seeds per snapshot: every (snapshot, seed) run counts once for the
               freed fraction (as E2); a snapshot is freed by majority when at least 3 of 5 seeds free it.
  Wilson       95% Wilson score interval (revlib.wilson); for noise over runs (clustered by snapshot, so
               the interval is narrower than a snapshot-level one; the majority count is given beside).

Tests
  new vs E2    per arm, two-sided Fisher exact test on the 2x2 table (freed/held x new/E2) of snapshots
               (deterministic arms: unperturbed run; noise: majority outcome; the run-level Fisher p for noise
               is stored beside). Holm over the 7 arms.
  paired       within a group, per snapshot, the contrasts of Sect. 6.1.4, notes/A7.md (push_second, second)
               and E2 analyze.py (d_orca_decomposition), first arm against second:
                 drive_only vs C3_rvo2, frozen_plus vs C3_rvo2, drive_only vs C3_pub, C3_pub vs C3_rvo2,
                 constraint_only_rvo2 vs C1, C3_rvo2 vs C1           exact McNemar (revlib.mcnemar_exact)
                 replay C3_pub vs C3_rvo2: snapshots where any replay changes the outcome   exact McNemar
                 noise0.07 vs C3_rvo2, freed: mean(k_i/5 - c_i), paired sign-flip test (200 000 random
                   flips, p = (count+1)/(B+1); exact enumeration when at most 20 differences are non-zero)
                 noise0.07 vs C3_rvo2, replay: [seeds disagree] vs [any ORCA replay changes]  exact McNemar
               Holm (revlib.holm) over these 9 contrasts within each group. Effects: paired difference of
               freed fractions (first minus second), 95% percentile bootstrap over snapshots (10 000).
Generator: numpy default_rng(20261111).
"""
import itertools
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import DATA, DERIVED, holm, mcnemar_exact, pdisp, sig, wilson  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

T_Q = 120.0
CLS = "lone_keystone_second_trap"
DET = ("C3_rvo2", "C3_pub", "drive_only", "frozen_plus", "constraint_only_rvo2", "C1")
NOISE = "noise0.07"
ARMS = DET + (NOISE,)
KEY = {NOISE: "noise0p07"}           # dotless keys for the registry
REPLAY = ("C3_rvo2", "C3_pub")
B, B_FLIP = 10000, 200000
rng = np.random.default_rng(20261111)
NEW = os.path.join(DATA, "revision", "A5", "a5_quench.jsonl")
E2 = os.path.join(DATA, "E2", "e2_quench.jsonl")


def k(a):
    return KEY.get(a, a)


def load():
    sel = {s["tag"]: s for s in json.load(open(os.path.join(DERIVED, "selection.json")))["E2"]["snapshots"]
           if s["class"] == CLS}
    runs = defaultdict(dict)          # runs[(tag, arm)][rep] = freed
    grp = {}
    for path, src in ((NEW, "new"), (E2, "E2")):
        for line in open(path):
            r = json.loads(line)
            tag, arm, rep = r["job_id"].split("|")
            if arm not in ARMS:
                continue
            if src == "E2":
                if tag not in sel:
                    continue
                blk = sel[tag]["blocker"]
            else:
                blk = r["blocker"]
                assert tag not in sel
            t = r["exits"].get(str(blk))
            f = t is not None and t <= T_Q + 1e-9
            if src == "new":
                assert f == r["blocker_freed"], r["job_id"]
            runs[(tag, arm)][rep] = f
            grp[tag] = src
    tags = {"new": sorted(t for t, g in grp.items() if g == "new"),
            "E2": sorted(t for t, g in grp.items() if g == "E2")}
    tags["pooled"] = tags["new"] + tags["E2"]
    assert len(tags["new"]) == 134 and len(tags["E2"]) == 26
    for t in tags["pooled"]:
        for a in DET:
            assert "u" in runs[(t, a)], (t, a)
            assert len(runs[(t, a)]) == (6 if a in REPLAY else 1) or grp[t] == "E2", (t, a)
        assert len(runs[(t, NOISE)]) == 5, t
    return runs, tags


def boot_mean(d):
    d = np.asarray(d, float)
    m = d[rng.integers(0, len(d), (B, len(d)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def signflip(d):
    d = np.asarray([x for x in d if abs(x) > 1e-12], float)
    n = len(d)
    if n == 0:
        return 1.0, "all differences zero"
    s0 = abs(d.sum()) - 1e-9
    if n <= 20:
        s = np.array(list(itertools.product((-1.0, 1.0), repeat=n)))
        return float(np.mean(np.abs(s @ d) >= s0)), f"exact sign-flip, {n} non-zero"
    cnt = 0
    for _ in range(B_FLIP // 20000):
        s = rng.choice((-1.0, 1.0), size=(20000, n))
        cnt += int(np.sum(np.abs(s @ d) >= s0))
    return (cnt + 1) / (B_FLIP + 1), f"sign-flip, {B_FLIP} random flips, {n} non-zero"


def cell(k_, n):
    p, lo, hi = wilson(k_, n)
    return {"freed": k_, "n": n, "frac": p, "lo": lo, "hi": hi,
            "frac_2sf": sig(p, 2), "lo_2sf": sig(lo, 2), "hi_2sf": sig(hi, 2)}


def main():
    runs, tags = load()
    u = lambda t, a: runs[(t, a)]["u"]                                   # noqa: E731
    nfrac = lambda t: sum(runs[(t, NOISE)].values()) / 5                 # noqa: E731
    maj = lambda t: nfrac(t) >= 0.5                                      # noqa: E731
    chg = lambda t, a: any(v != runs[(t, a)]["u"] for v in runs[(t, a)].values())   # noqa: E731
    ndis = lambda t: 0 < nfrac(t) < 1                                    # noqa: E731

    out = {"script": "experiments/revision/A5x_analyze.py", "doc": __doc__,
           "n_snapshots": {g: len(T) for g, T in tags.items()},
           "n_runs_new": sum(len(runs[(t, a)]) for t in tags["new"] for a in ARMS)}

    # ---- per-arm freed fraction at T, Wilson 95%
    R = {}
    for g, T in tags.items():
        R[g] = {}
        for a in DET:
            c = cell(sum(u(t, a) for t in T), len(T))
            c["unit"] = "snapshot (unperturbed run)"
            if a in REPLAY:
                c["replays"] = 5 * len(T)
                c["replays_changed"] = sum(v != u(t, a) for t in T for r, v in runs[(t, a)].items() if r != "u")
                c["snapshots_changed"] = sum(chg(t, a) for t in T)
            R[g][k(a)] = c
        c = cell(sum(sum(runs[(t, NOISE)].values()) for t in T), 5 * len(T))
        c["unit"] = "run (snapshot x seed)"
        c["snapshots_majority"] = sum(maj(t) for t in T)
        c["snapshots_majority_wilson"] = list(wilson(c["snapshots_majority"], len(T)))
        c["snapshots_seeds_disagree"] = sum(ndis(t) for t in T)
        R[g][k(NOISE)] = c
        R[g]["C1_freed_tags"] = [t for t in T if u(t, "C1")]
    out["rates"] = R

    # ---- new vs E2 per arm: Fisher exact on snapshots
    NV = {}
    for a in ARMS:
        if a == NOISE:
            x1, x2 = sum(maj(t) for t in tags["new"]), sum(maj(t) for t in tags["E2"])
        else:
            x1, x2 = R["new"][a]["freed"], R["E2"][a]["freed"]
        n1, n2 = len(tags["new"]), len(tags["E2"])
        p = float(stats.fisher_exact([[x1, n1 - x1], [x2, n2 - x2]])[1])
        d = {"test": "two-sided Fisher exact, snapshots" + (" (majority of 5 seeds)" if a == NOISE else ""),
             "new": x1, "new_n": n1, "E2": x2, "E2_n": n2, "diff": x1 / n1 - x2 / n2, "p": p}
        if a == NOISE:
            r1, r2 = R["new"][k(a)], R["E2"][k(a)]
            d["p_runs"] = float(stats.fisher_exact([[r1["freed"], r1["n"] - r1["freed"]],
                                                    [r2["freed"], r2["n"] - r2["freed"]]])[1])
        NV[k(a)] = d
    for kk, ph in zip(NV, holm([NV[kk]["p"] for kk in NV])):
        NV[kk]["p_holm"] = ph
        NV[kk]["p_disp"], NV[kk]["p_holm_disp"] = pdisp(NV[kk]["p"]), pdisp(ph)
        NV[kk]["diff_2sf"] = sig(NV[kk]["diff"], 2)
    out["new_vs_E2"] = NV
    out["new_vs_E2_min_p_holm"] = min(v["p_holm"] for v in NV.values())
    out["new_vs_E2_min_p_holm_disp"] = pdisp(out["new_vs_E2_min_p_holm"])

    # ---- paired contrasts within each group
    PAIRS = [("drive_only", "C3_rvo2"), ("frozen_plus", "C3_rvo2"), ("drive_only", "C3_pub"),
             ("C3_pub", "C3_rvo2"), ("constraint_only_rvo2", "C1"), ("C3_rvo2", "C1")]
    C = {}
    for g, T in tags.items():
        C[g] = {}

        def mcn(x, y, test):
            x, y = np.asarray(x, bool), np.asarray(y, bool)
            b, c = int((x & ~y).sum()), int((~x & y).sum())
            d = x.astype(float) - y.astype(float)
            return {"test": test, "n": len(T), "first": int(x.sum()), "second": int(y.sum()),
                    "disc_first_only": b, "disc_second_only": c, "effect": float(d.mean()), "ci95": boot_mean(d),
                    "p": mcnemar_exact(b, c)}
        for a1, a2 in PAIRS:
            C[g][f"{a1}_vs_{a2}"] = mcn([u(t, a1) for t in T], [u(t, a2) for t in T], "exact McNemar")
        C[g]["replay_C3_pub_vs_C3_rvo2"] = mcn([chg(t, "C3_pub") for t in T], [chg(t, "C3_rvo2") for t in T],
                                               "exact McNemar, snapshots with a replay that changes the outcome")
        d = np.array([nfrac(t) - u(t, "C3_rvo2") for t in T])
        p, how = signflip(d)
        C[g]["noise0p07_vs_C3_rvo2"] = {"test": "paired sign-flip on mean(k_i/5 - c_i)", "method": how,
                                        "n": len(T), "effect": float(d.mean()), "ci95": boot_mean(d), "p": p}
        C[g]["replay_noise0p07_vs_C3_rvo2"] = mcn([ndis(t) for t in T], [chg(t, "C3_rvo2") for t in T],
                                                  "exact McNemar, [seeds disagree] vs [an ORCA replay changes]")
        names = list(C[g])
        for nm, ph in zip(names, holm([C[g][nm]["p"] for nm in names])):
            P = C[g][nm]
            P["p_holm"] = ph
            P["p_disp"], P["p_holm_disp"] = pdisp(P["p"]), pdisp(ph)
            P["effect_2sf"] = sig(P["effect"], 2)
            P["ci95_2sf"] = [sig(v, 2) for v in P["ci95"]]
    out["paired"] = C

    # ---- the Table 2 reading at the second trap, per group
    cls = {}
    for g in tags:
        r, c = R[g], C[g]
        cls[g] = {
            "orca_rvo2_frees_vs_C1": c["C3_rvo2_vs_C1"]["p_holm"] < 0.05,
            "orca_rvo2_replays_identical": r["C3_rvo2"]["replays_changed"] == 0,
            "legacy_replay_flips": r["C3_pub"]["replays_changed"],
            "push_plus_frees_more_than_orca": c["frozen_plus_vs_C3_rvo2"]["p_holm"] < 0.05,
            "drive_frees_more_than_orca": c["drive_only_vs_C3_rvo2"]["p_holm"] < 0.05,
            "noise_seeds_disagree": r["noise0p07"]["snapshots_seeds_disagree"]}
    out["table2_reading"] = cls
    out["sfm_freed_snapshot_speed"] = snapshot_speeds(R["pooled"]["C1_freed_tags"])
    path = revlib.out_json("A5x", out)
    return out, path


def snapshot_speeds(freed_tags):
    """Largest speed of an active agent in each saved E1b deadlock snapshot (data/E1/library, all 196), and the
    rank (1 = fastest) of the snapshots in which the SFM restart (C1) frees the blocker."""
    import glob
    import pickle
    v = {}
    for f in glob.glob(os.path.join(DATA, "E1", "library", "E1b_seed*.pkl")):
        st = pickle.load(open(f, "rb"))["state"]
        a = np.asarray(st.active, bool)
        v[os.path.basename(f)[:-4]] = float(np.linalg.norm(np.asarray(st.velocities)[a], axis=1).max())
    order = sorted(v, key=v.get, reverse=True)
    return {"n_library": len(v), "median_max_speed_m_s": float(np.median(list(v.values()))),
            "freed": {t: {"max_speed_m_s": v[t], "max_speed_mm_s_2sf": sig(1e3 * v[t], 2),
                          "rank_fastest": order.index(t) + 1} for t in freed_tags}}


def brief(o):
    for g in ("new", "E2", "pooled"):
        print("==", g, o["n_snapshots"][g])
        for a, c in o["rates"][g].items():
            if isinstance(c, dict):
                print(f"  {a:22s} {c['freed']:4d}/{c['n']:4d} {c['frac']:.3f} [{c['lo']:.3f}, {c['hi']:.3f}]",
                      {x: c[x] for x in ("replays_changed", "snapshots_changed", "snapshots_majority",
                                         "snapshots_seeds_disagree") if x in c})
        print("  C1 freed:", o["rates"][g]["C1_freed_tags"])
        for nm, c in o["paired"][g].items():
            print(f"   {nm:34s} eff {c['effect']:+.3f} [{c['ci95'][0]:+.3f},{c['ci95'][1]:+.3f}]",
                  f"disc {c.get('disc_first_only')}:{c.get('disc_second_only')} p={c['p_disp']} holm={c['p_holm_disp']}")
        print("  reading", o["table2_reading"][g])
    for a, c in o["new_vs_E2"].items():
        print(f"  new vs E2 {a:22s} {c['new']}/{c['new_n']} vs {c['E2']}/{c['E2_n']} p={c['p_disp']} holm={c['p_holm_disp']}",
              c.get("p_runs", ""))


if __name__ == "__main__":
    o, p = main()
    brief(o)
    print("wrote", p)
