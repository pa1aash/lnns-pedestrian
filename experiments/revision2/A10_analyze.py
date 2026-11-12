"""A10 analysis: does a 1e-9 m replay change the outcome of a noise quench when the noise stream is held fixed?

Inputs: data/revision2/A10/a10.jsonl (experiments/revision2/A10_noise_replay.py: 34 lone keystones x 5 noise seeds,
each as the E2 reference and as a 1e-9 m replay with the same noise seed); data/E2/e2_quench.jsonl (the ordinary
1e-9 m replays of the deterministic arms, perturb seeds 900-904, and the five independent noise seeds at
sigma = 0.07 m/s); data/derived/rev_A7.json (the replay-change counts of A7: E2 9:0, N1 14:0).
Method:
  reference check   every ref run must reproduce the stored E2 record bit for bit (exits, final positions, t_run).
  run level         a flip = blocker freed within 120 s in one of (ref, replay) and not in the other; flips split
                    into ref-only (b) and replay-only (c); exact McNemar on b, c; Wilson interval of the flip
                    fraction over the 170 pairs. Among pairs freed in both: exit-time shifts |t_replay - t_ref|.
  snapshot level    a snapshot "changes under fixed-stream replay" when any of its five pairs flips (the rule A7
                    uses for deterministic replays). Compared, on the same 34 snapshots, with
                    (i) ordinary replays of each deterministic E2 arm (any of five 1e-9 m replays changes the
                    unperturbed outcome; force-coupled ORCA (RVO2) is arm C3_rvo2), and
                    (ii) independent noise seeds (the five E2 seeds disagree on freed; A7's replay probe),
                    by exact McNemar on the paired snapshot indicators.
  independent-seed  per run pair, the chance that two different E2 seeds of the same snapshot disagree,
  baseline          mean over snapshots of 2 k (5 - k) / 20 (k = seeds that free), against the run-level flip
                    fraction.
Output: data/derived/rev2_A10.json.  Usage: A10_analyze.py [--in PATH] [--partial]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import DATA, DERIVED, load_runs, mcnemar_exact, np, out_json, pdisp, sig, wilson  # noqa: E402
import A10_noise_replay as A10  # noqa: E402

T_Q = 120.0


def freed(r, blk):
    t = r["exits"].get(str(blk))
    return t is not None and t <= T_Q + 1e-9, t


def wil(k, n):
    p, lo, hi = wilson(k, n)
    return {"k": int(k), "n": int(n), "frac": p, "ci95": [lo, hi], "frac_2sf": sig(p), "ci95_2sf": [sig(lo), sig(hi)]}


def mcn(x, y, lab_x, lab_y):
    x, y = np.asarray(x, bool), np.asarray(y, bool)
    b, c = int((x & ~y).sum()), int((~x & y).sum())
    p = mcnemar_exact(b, c)
    return {"test": "exact McNemar", "first": lab_x, "second": lab_y, "n_first": int(x.sum()),
            "n_second": int(y.sum()), "b_first_only": b, "c_second_only": c, "p": p, "p_disp": pdisp(p)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=os.path.join(DATA, "revision2", "A10", "a10.jsonl"))
    ap.add_argument("--partial", action="store_true", help="analyse an incomplete file (preview only)")
    a = ap.parse_args()
    snaps = A10.snapshots()
    tags = [s["tag"] for _, s in snaps]
    blk = {s["tag"]: s["blocker"] for _, s in snaps}
    R = {}
    for r in load_runs(a.inp):
        if abs(r["t_q"] - T_Q) < 1e-9:
            R[(r["tag"], r["rep"], r["kind"])] = r
    need = {(t, rep, k) for t in tags for rep in range(A10.N_REP) for k in ("ref", "replay")}
    missing = need - set(R)
    if missing and not a.partial:
        sys.exit(f"A10: {len(missing)} of {len(need)} runs missing in {a.inp}; run the queue step A10 first")

    # reference check
    refs = [r for (t, rep, k), r in R.items() if k == "ref"]
    n_match = sum(bool(r.get("ref_match")) for r in refs)

    # run level
    pairs = [(t, rep) for t in tags for rep in range(A10.N_REP) if (t, rep, "ref") in R and (t, rep, "replay") in R]
    fr, fp, shifts = [], [], []
    per_snap = {t: [] for t in tags}
    for t, rep in pairs:
        a_f, a_t = freed(R[(t, rep, "ref")], blk[t])
        b_f, b_t = freed(R[(t, rep, "replay")], blk[t])
        fr.append(a_f)
        fp.append(b_f)
        per_snap[t].append(a_f != b_f)
        if a_f and b_f:
            shifts.append(abs(b_t - a_t))
    fr, fp = np.array(fr, bool), np.array(fp, bool)
    run_mc = mcn(fr, fp, "ref freed", "replay freed")
    flips = int((fr != fp).sum())
    shifts = np.array(shifts)
    run = {"n_pairs": len(pairs), "ref_freed": int(fr.sum()), "replay_freed": int(fp.sum()),
           "flips": flips, "flip": wil(flips, len(pairs)), "mcnemar": run_mc,
           "n_both_freed": int(len(shifts)),
           "n_same_exit_time": int((shifts < 0.5 * 0.01).sum()) if len(shifts) else 0,
           "shift_median_s": float(np.median(shifts)) if len(shifts) else None,
           "shift_max_s": float(shifts.max()) if len(shifts) else None}

    # E2 comparators on the same snapshots
    E2 = {}
    for r in load_runs(A10.E2_OUT):
        t = r["job_id"].split("|")[0]
        if t in blk:
            E2[r["job_id"]] = r
    ch_fixed = np.array([any(per_snap[t]) for t in tags])
    k_seed = {t: sum(freed(E2[f"{t}|noise0.07|{rep}"], blk[t])[0] for rep in range(A10.N_REP)) for t in tags}
    ch_seed = np.array([0 < k_seed[t] < A10.N_REP for t in tags])
    indep = float(np.mean([2 * k * (A10.N_REP - k) / (A10.N_REP * (A10.N_REP - 1)) for k in k_seed.values()]))
    import e2_quench as e2q  # noqa: E402  (experiments/E2 is on sys.path via revlib)
    det = {}
    for arm in e2q.DET_ARMS:
        ch = []
        for t in tags:
            f0 = freed(E2[f"{t}|{arm}|u"], blk[t])[0]
            ch.append(any(freed(E2[f"{t}|{arm}|{ps}"], blk[t])[0] != f0 for ps in e2q.PERTURB_SEEDS))
        det[arm] = {"changed": int(sum(ch)), "n": len(tags), "_ind": ch}
    a7 = json.load(open(os.path.join(DERIVED, "rev_A7.json")))
    snap = {"n": len(tags), "changed_fixed_stream": wil(int(ch_fixed.sum()), len(tags)),
            "changed_seeds_E2": int(ch_seed.sum()),
            "a7_replay_E2": [a7["lone_E2"]["replay"]["b_first_only"], a7["lone_E2"]["replay"]["c_second_only"]],
            "a7_replay_N1": [a7["lone_N1"]["replay"]["b_first_only"], a7["lone_N1"]["replay"]["c_second_only"]],
            "det_replay_changed": {k: {"changed": v["changed"], "n": v["n"]} for k, v in det.items()},
            "vs_orca_rvo2": mcn(ch_fixed, det["C3_rvo2"]["_ind"], "fixed-stream replay", "ORCA (RVO2) replay"),
            "vs_seeds_E2": mcn(ch_fixed, ch_seed, "fixed-stream replay", "independent E2 seeds"),
            "changed_tags": [t for t, c in zip(tags, ch_fixed) if c]}
    run["indep_seed_disagree"] = indep
    run["indep_seed_disagree_2sf"] = sig(indep)
    res = {"script": "experiments/revision2/A10_analyze.py", "doc": __doc__, "input": os.path.relpath(a.inp, rev2lib.ROOT),
           "complete": not missing, "n_missing": len(missing),
           "ref_check": {"n_ref": len(refs), "n_match": n_match, "all_match": n_match == len(refs)},
           "run": run, "snapshot": snap}
    if a.partial and missing:
        print(json.dumps(res, indent=1, default=float))
        return
    print("wrote", out_json("A10", res))
    print(json.dumps({"ref": res["ref_check"], "flips": run["flips"], "b:c": [run_mc["b_first_only"], run_mc["c_second_only"]],
                      "snap_changed": int(ch_fixed.sum()), "seed_changed": int(ch_seed.sum()),
                      "orca_changed": det["C3_rvo2"]["changed"]}))


if __name__ == "__main__":
    main()
