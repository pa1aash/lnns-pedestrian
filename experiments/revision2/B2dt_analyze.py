"""B2 analysis: time step. SFM, CF flags, default walls, dt = 0.005 s (experiments/revision2/B2_dt.py) against
dt = 0.01 s with the same spawns (E1b at 0.80 m, B2 of session C at 0.88 and 0.96 m), seeds 42-141, 600 s.

Per width: completion k/100 with Wilson intervals at both time steps, paired by seed (exact McNemar).
Width at half completion: binomial-logit MLE on the three widths for each time step (experiments/revision/
B2_analyze.logit_mle); shift dw50 = w50(0.005) - w50(0.01) with a 95% interval from 2000 paired bootstrap
resamples of seeds within width (the same seeds drawn for both time steps, PCG64(11)). Limits stated in the
output: three widths, a two-parameter logistic, so the shift is a location shift under an assumed common shape;
the slope is also reported per time step.
Output: data/derived/rev2_B2.json.  Usage: B2_analyze.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import DATA, mcnemar_exact, np, pdisp, wilson  # noqa: E402
import B2_analyze as OLD  # noqa: E402  (experiments/revision/B2_analyze.py)

W = (0.80, 0.88, 0.96)


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []


def main():
    new = {(round(x["width"], 2), x["seed"]): bool(x["complete"]) for x in jl(os.path.join(DATA, "revision2", "B2", "b2dt.jsonl"))}
    old_runs, _ = OLD.dedupe(OLD.runs())
    old = {(round(r["w"], 2), r["seed"]): bool(r["complete"]) for r in old_runs if round(r["w"], 2) in W}
    keys = sorted(k for k in new if k in old)
    o = {"n_pairs": len(keys), "per_width": []}
    for w in W:
        s = [k for k in keys if k[0] == w]
        if not s:
            continue
        a, b = sum(new[k] for k in s), sum(old[k] for k in s)
        n10 = sum(new[k] and not old[k] for k in s)
        n01 = sum(old[k] and not new[k] for k in s)
        pa, pb = wilson(a, len(s)), wilson(b, len(s))
        p = mcnemar_exact(n10, n01)
        o["per_width"].append({"w": w, "n": len(s), "dt005": {"k": a, "ci95": [pa[1], pa[2]]},
                               "dt01": {"k": b, "ci95": [pb[1], pb[2]]}, "dt005_only": n10, "dt01_only": n01,
                               "mcnemar_p": p, "mcnemar_p_disp": pdisp(p)})
    b, c = sum(p["dt005_only"] for p in o["per_width"]), sum(p["dt01_only"] for p in o["per_width"])
    o["pooled_paired"] = {"dt005_only": b, "dt01_only": c, "mcnemar_p": mcnemar_exact(b, c),
                          "mcnemar_p_disp": pdisp(mcnemar_exact(b, c))}
    ws = sorted({k[0] for k in keys})
    if len(ws) == 3:
        def fit(D, K):
            w = np.array([k[0] for k in K])
            y = np.array([float(D[k]) for k in K])
            a, b = OLD.logit_mle(w, y)
            return -a / b, b
        w50n, bn = fit(new, keys)
        w50o, bo = fit(old, keys)
        rng = np.random.default_rng(11)
        by_w = {w: [k for k in keys if k[0] == w] for w in ws}
        bs = []
        for _ in range(2000):
            K = [by_w[w][i] for w in ws for i in rng.integers(0, len(by_w[w]), len(by_w[w]))]
            x, bx = fit(new, K)
            y, by = fit(old, K)
            bs.append(x - y if bx > 0 and by > 0 else np.nan)
        o["w50"] = {"dt005_m": float(w50n), "dt01_m": float(w50o), "slope_dt005": float(bn), "slope_dt01": float(bo),
                    "shift_m": float(w50n - w50o),
                    "shift_ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
                    "limits": "three widths; two-parameter logistic per time step; paired bootstrap of seeds within width"}
    print(rev2lib.out_json("B2", o))
    for p in o["per_width"]:
        print(p["w"], "dt0.005", p["dt005"]["k"], "dt0.01", p["dt01"]["k"], "of", p["n"], "McNemar", p["mcnemar_p_disp"])
    if "w50" in o:
        print(o["w50"])


if __name__ == "__main__":
    main()
