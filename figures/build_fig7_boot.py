"""Cluster-bootstrap cache for Fig 7 (pair standoff, right panel): figures/data/fig7_boot.json.

Input:  data/E7b/e7b_quench.jsonl, data/E7b_bstar/bstar_quench.jsonl, data/E7b/e7b_static.jsonl (the 46 pair
        snapshots), as experiments/E7b/analyze.py.
Freed:  a member of the pair exits within 120 s. Deterministic arms (incl. the matched biases +-b*): the unperturbed
        run ("u") per snapshot; noise arms: the five seeds per snapshot, every run counted once.
Intervals: 95% percentile intervals from B = 10 000 cluster-bootstrap resamples of the pair snapshots (drawn with
        replacement, all seeds of a drawn snapshot kept; one index matrix shared by every arm, PCG64(12345)). With
        one run per snapshot the cluster bootstrap is an ordinary snapshot bootstrap.
Left panel (bias_curve): the deterministic bias arms b = -0.03 ... 0.1 (b = 0: SFM), same resamples.
"""
import json
from collections import defaultdict
from pathlib import Path

from build_fig6_boot import B, SEED, T_Q, boot_idx, cluster_rate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "data" / "fig7_boot.json"
SOURCES = [ROOT / "data" / "E7b" / "e7b_quench.jsonl", ROOT / "data" / "E7b_bstar" / "bstar_quench.jsonl",
           ROOT / "data" / "E7b" / "e7b_static.jsonl"]
DET = ["C1", "C2", "C3_pub", "C3_rvo2", "drive_only", "constraint_only_pub", "constraint_only_rvo2",
       "frozen_plus", "frozen_minus", "bstar_pub+", "bstar_pub-", "bstar_rvo2+", "bstar_rvo2-"]
NOISE = ["noise0.01", "noise0.02", "noise0.03", "noise0.05"]
BIAS = [-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.05, 0.1]   # left panel; b = 0 is the SFM arm C1


def key(arm):
    return arm.replace("bstar_", "bstar").replace("+", "p").replace("-", "m").replace(".", "p")


def build():
    static = [json.loads(ln) for ln in open(SOURCES[2]) if ln.strip()]
    tags = [r["job_id"] for r in sorted(static, key=lambda r: r["seed"])]
    runs = defaultdict(dict)
    for path in SOURCES[:2]:
        for line in open(path):
            if not line.strip():
                continue
            r = json.loads(line)
            tag, arm, rep = r["job_id"].split("|")
            runs[(tag, arm)][rep] = bool(r["freed"] and r["first_t"] <= T_Q + 1e-9)
    idx = boot_idx(len(tags))
    out = {"doc": __doc__.strip(), "resamples": B, "rng": f"PCG64({SEED})", "level": 95,
           "n_snapshots": len(tags), "rates": {}}
    for arm in DET + NOISE:
        reps = ["u"] if arm in DET else sorted(runs[(tags[0], arm)])
        per = [[runs[(t, arm)][r] for r in reps] for t in tags]
        k = [sum(p) for p in per]
        n = [len(p) for p in per]
        p, lo, hi = cluster_rate(k, n, idx)
        out["rates"][key(arm)] = {"k": int(sum(k)), "n": int(sum(n)), "runs_per_snapshot": len(reps),
                                  "p": p, "lo": lo, "hi": hi}
    out["bias_curve"] = []
    for b in BIAS:
        arm = "C1" if b == 0 else f"bias{b:g}"
        k = [int(runs[(t, arm)]["u"]) for t in tags]
        p, lo, hi = cluster_rate(k, [1] * len(tags), idx)
        out["bias_curve"].append({"b": b, "arm": arm, "k": int(sum(k)), "n": len(tags), "p": p, "lo": lo, "hi": hi})
    OUT.parent.mkdir(exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    return out


def get():
    """Cached result; rebuilt when missing or older than its inputs or this script."""
    deps = SOURCES + [Path(__file__), HERE / "build_fig6_boot.py"]
    if not OUT.exists() or OUT.stat().st_mtime < max(p.stat().st_mtime for p in deps):
        return build()
    return json.load(open(OUT))


if __name__ == "__main__":
    o = build()
    for a, r in o["rates"].items():
        print(f"  {a:22s} {r['k']:3d}/{r['n']:3d} {r['p']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]")
    for r in o["bias_curve"]:
        print(f"  b={r['b']:+.2f} {r['k']:3d}/{r['n']:3d} {r['p']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]")
