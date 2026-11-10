"""Cluster-bootstrap cache for Fig 6 (lone-trap quench): figures/data/fig6_boot.json.

Input:  data/E2/e2_quench.jsonl, data/derived/selection.json (as experiments/E2/analyze.py).
Freed:  the blocker exits within 120 s. Deterministic arms: the unperturbed run ("u") per snapshot; noise arms:
        the five seeds per snapshot, every run counted once.
Intervals: 95% percentile intervals from B = 10 000 cluster-bootstrap resamples of snapshots (snapshots drawn
        with replacement, all runs of a drawn snapshot kept; one index matrix per stratum, PCG64(12345), shared by
        every arm so that arms are resampled jointly). With one run per snapshot (deterministic arms) the cluster
        bootstrap is an ordinary snapshot bootstrap.
Right panel: lone keystones, cumulative fraction freed against time. Held runs either reach a stationary rest
        state (deterministic arms, stopped early) or run to 120 s (noise), so every held run is censored at the
        120 s horizon; the Kaplan-Meier estimate is then the empirical fraction freed by t, and its pointwise
        interval comes from the same resamples.
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "data" / "fig6_boot.json"
SOURCES = [ROOT / "data" / "E2" / "e2_quench.jsonl", ROOT / "data" / "derived" / "selection.json"]
T_Q = 120.0
B = 10_000
SEED = 12345
STRATA = ["lone_keystone", "lone_keystone_second_trap"]
DET = ["C1", "C2", "C3_pub", "C3_rvo2", "drive_only", "constraint_only_pub", "constraint_only_rvo2",
       "frozen_plus", "frozen_minus", "bias0.05", "bias0.1", "bias0.2", "bias0.5"]
NOISE = ["noise0.03", "noise0.05", "noise0.07"]
CURVES = ["C3_pub", "C3_rvo2", "drive_only", "frozen_plus", "noise0.03", "noise0.05", "noise0.07"]


def key(arm):
    return arm.replace(".", "p")


def boot_idx(n, seed=SEED, b=B):
    return np.random.Generator(np.random.PCG64(seed)).integers(0, n, (b, n))


def cluster_rate(k, n, idx):
    """k, n: freed and run counts per snapshot. Returns point estimate and 95% percentile interval."""
    k, n = np.asarray(k, float), np.asarray(n, float)
    bs = k[idx].sum(1) / n[idx].sum(1)
    return [float(k.sum() / n.sum()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def cluster_curve(times, n, idx):
    """times: per snapshot, the list of freed times; n: runs per snapshot. Cumulative fraction freed on the grid
    of distinct freed times (0 and the horizon added), with pointwise 95% percentile intervals."""
    grid = np.unique(np.concatenate([[0.0], np.round(np.concatenate([np.asarray(t, float) for t in times] +
                                                                    [np.zeros(0)]), 2), [T_Q]]))
    C = np.array([[np.sum(np.round(np.asarray(t, float), 2) <= g) for g in grid] for t in times], float)
    n = np.asarray(n, float)
    F = C.sum(0) / n.sum()
    bs = C[idx].sum(1) / n[idx].sum(1)[:, None]
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
    return {"t": grid.tolist(), "F": F.tolist(), "lo": lo.tolist(), "hi": hi.tolist()}


def load():
    sel = json.load(open(ROOT / "data" / "derived" / "selection.json"))["E2"]["snapshots"]
    snaps = {s["tag"]: s for s in sel}
    runs = defaultdict(dict)
    for line in open(SOURCES[0]):
        r = json.loads(line)
        tag, arm, rep = r["job_id"].split("|")
        t = r["exits"].get(str(snaps[tag]["blocker"]))
        runs[(tag, arm)][rep] = t if (t is not None and t <= T_Q + 1e-9) else None
    return sel, runs


def build():
    sel, runs = load()
    out = {"doc": __doc__.strip(), "resamples": B, "rng": f"PCG64({SEED})", "level": 95, "t_max_s": T_Q,
           "strata": {}, "curves_lone_keystone": {}}
    for st in STRATA:
        tags = [s["tag"] for s in sel if s["class"] == st]
        idx = boot_idx(len(tags))
        cell = {"n_snapshots": len(tags), "rates": {}}
        for arm in DET + NOISE:
            reps = ["u"] if arm in DET else sorted(runs[(tags[0], arm)])
            per = [[runs[(t, arm)][r] for r in reps] for t in tags]
            k = [sum(x is not None for x in p) for p in per]
            n = [len(p) for p in per]
            p, lo, hi = cluster_rate(k, n, idx)
            cell["rates"][key(arm)] = {"k": int(sum(k)), "n": int(sum(n)), "runs_per_snapshot": len(reps),
                                       "p": p, "lo": lo, "hi": hi}
            if st == "lone_keystone" and arm in CURVES:
                out["curves_lone_keystone"][key(arm)] = cluster_curve(
                    [[x for x in p_ if x is not None] for p_ in per], n, idx)
        out["strata"][st] = cell
    OUT.parent.mkdir(exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    return out


def get():
    """Cached result; rebuilt when missing or older than its inputs or this script."""
    if not OUT.exists() or OUT.stat().st_mtime < max(p.stat().st_mtime for p in SOURCES + [Path(__file__)]):
        return build()
    return json.load(open(OUT))


if __name__ == "__main__":
    o = build()
    for st, c in o["strata"].items():
        print("==", st, c["n_snapshots"])
        for a, r in c["rates"].items():
            print(f"  {a:22s} {r['k']:3d}/{r['n']:3d} {r['p']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]")
