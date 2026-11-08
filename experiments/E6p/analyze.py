#!/usr/bin/env python3
"""E6p analysis: published ORCA in the published mode, whole runs, against the conference's printed count.

Input: data/E6/e6p.jsonl (experiments/E6/e6.py E6p: room bottleneck w = 0.8 m, 100 agents, 600 s cap,
published-reproduction flags, C3 with the published ORCA, seeds 428-477, n = 50; a run stops at completion
or at deadlock, every active |v| < 0.01 m/s for 10 s with no exit).
Optional: data/E6/e6a.jsonl (C3 RVO2, corrected-forward, n = 186) for the cross-mode comparison.

Output: data/derived/E6p_analysis.json:
  completion        k/n, Wilson 95% interval; final states (deadlocked / capped while moving)
  evacuation        median and range of evacuation time over completed runs; Kaplan-Meier is not needed
                    because every censored run is censored at the same 600 s cap (median from the empirical
                    distribution with incomplete runs at +inf)
  conference        the printed 13/25 (camera-ready CR:15, CR:780; data/derived/table4_conference.json):
                    whether its rate lies inside the Wilson interval, and a two-sided Fisher exact test of
                    13/25 against k/n
  vs_e6a            two-sided Fisher exact test of E6p against E6a completion (different modes and seeds;
                    descriptive)
  verdict           confirmed when the printed rate lies inside the 95% interval and Fisher p >= 0.05,
                    revised otherwise; evidence line
"""
import argparse
import json
import math
from pathlib import Path

from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[2]


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def load(p):
    rows = {}
    for ln in Path(p).read_text().splitlines():
        if ln.strip():
            r = json.loads(ln)
            rows[r["job_id"]] = r
    return list(rows.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=str(ROOT / "data" / "E6" / "e6p.jsonl"))
    ap.add_argument("--e6a", default=str(ROOT / "data" / "E6" / "e6a.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "data" / "derived" / "E6p_analysis.json"))
    a = ap.parse_args()

    runs = sorted(load(a.inp), key=lambda r: r["seed"])
    n = len(runs)
    k = sum(bool(r["complete"]) for r in runs)
    dead = sum(bool(r.get("deadlock")) and not r["complete"] for r in runs)
    capped = n - k - dead
    lo, hi = wilson(k, n)
    times = sorted(r["evacuation_time"] for r in runs if r["complete"])
    all_t = sorted([r["evacuation_time"] if r["complete"] else math.inf for r in runs])
    med_all = all_t[(n - 1) // 2] if n % 2 else 0.5 * (all_t[n // 2 - 1] + all_t[n // 2])
    rem = [r["n_remaining"] for r in runs if not r["complete"]]

    conf = json.loads((ROOT / "data" / "derived" / "table4_conference.json").read_text())["c3_complete"]
    ck, cn = conf["k"], conf["n"]
    p_conf = fisher_exact([[ck, cn - ck], [k, n - k]])[1]
    inside = lo <= ck / cn <= hi

    vs = None
    if Path(a.e6a).is_file():
        e6a = load(a.e6a)
        ka, na = sum(bool(r["complete"]) for r in e6a), len(e6a)
        vs = {"k": ka, "n": na, "rate": ka / na, "fisher_p": fisher_exact([[k, n - k], [ka, na - ka]])[1]}

    status = "confirmed" if inside and p_conf >= 0.05 else "revised"
    out = {
        "script": "experiments/E6p/analyze.py", "doc": __doc__, "input": str(Path(a.inp).relative_to(ROOT))
        if Path(a.inp).is_relative_to(ROOT) else a.inp,
        "seeds": [runs[0]["seed"], runs[-1]["seed"]] if runs else None,
        "completion": {"k": k, "n": n, "rate": k / n if n else None, "wilson95": [lo, hi],
                       "deadlocked": dead, "capped_moving": capped,
                       "remaining_median": sorted(rem)[len(rem) // 2] if rem else None,
                       "remaining_max": max(rem) if rem else None},
        "evacuation": {"median_completed": times[(len(times) - 1) // 2] if times else None,
                       "min_completed": times[0] if times else None,
                       "max_completed": times[-1] if times else None,
                       "median_all": med_all if math.isfinite(med_all) else None},
        "conference": {"k": ck, "n": cn, "rate": ck / cn, "inside_wilson95": inside, "fisher_p": p_conf},
        "vs_e6a": vs,
        "verdict": {"status": status,
                    "evidence": f"{k}/{n} [{lo:.2f}, {hi:.2f}] in the published mode; printed {ck}/{cn} "
                                f"{'inside' if inside else 'outside'} the interval (Fisher p = {p_conf:.3f})"},
    }
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k_: out[k_] for k_ in ("completion", "evacuation", "conference", "vs_e6a", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
