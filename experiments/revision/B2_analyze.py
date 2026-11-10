"""B2 analysis: critical width from all widths, and the parameter-free prediction from the stuck-alone fraction.

Inputs: SFM, CF, default walls, 100 agents, seeds 42-141, 600 s: data/E7/e7_cells.jsonl (w = 0.7, 0.9, 1.0 m),
data/E1/E1_runs.jsonl (E1b, w = 0.8 m, seeds 42-141), data/revision/B2/b2.jsonl (w = 0.82-0.96 m).
1. Completion against w: binomial-logit maximum likelihood on the runs, w50 = -a/b; 95% interval by
   nonparametric bootstrap of runs within each width (2000 resamples, PCG64(7)); also with the E7 pseudo-count
   rule (+0.5 / +1) for comparison with the earlier fit.
2. Stuck-alone fraction f(w): every spawned agent gets the exact width w_c(r, m v0/tau) at which its margin is
   zero (experiments/fixan/fix_a8.py w_crit: two free jamb ends, social wall term, the code's profile to
   <1e-3); f(w) = fraction of agents with w_c > w (stuck alone at width w). Agents pooled over the 100 spawns
   (the spawn of a seed does not depend on w; checked on the attrs).
3. Prediction: completion = (1 - f(w))^N, i.e. none of N agents that face the door alone is stuck alone.
   N = 100 (every agent) and N = N_eff, the number of agents that reach the door last, defined from the
   arrival record: a stuck-alone agent arriving at the door (x > 9.4 m, |y - 5| < 0.6 m) with n agents still
   active passes if the crowd behind pushes it through; P(pass | stuck alone, n) is fitted by a logit in n
   (pooled over widths 0.8-0.96 m); N_eff = n at which P(pass) = 1/2 (bootstrap interval over runs).
   Second choice N_eff_q = 100 q, q the fraction of stuck-alone door arrivals that are not pushed through
   ((1 - f)^(100 q) ~ (1 - q f)^100: each stuck-alone agent blocks with probability q).
   Tested against the observed completion curve (deviance, w50 of each prediction); N_best (the N that fits
   best) is reported as a check, not a prediction.
4. Bracket ends (fix_a8 definitions, restated): w_lo = median over spawned agents of w_c (below it the
   median agent is stuck alone); w_hi = median over runs of the largest w_c in the run (above it the median
   run has no stuck-alone agent).
Output: data/derived/rev_B2.json.
"""
import ast
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import DATA, np  # noqa: E402
from scipy.optimize import brentq  # noqa: E402
import fix_a8  # noqa: E402
from e1lib import runs_path  # noqa: E402

M = 80.0
RNG = np.random.default_rng(7)


def attrs(x):
    return x["attrs"] if isinstance(x["attrs"], list) else ast.literal_eval(x["attrs"])


def runs():
    R = []
    for x in revlib.load_runs(os.path.join(DATA, "E7", "e7_cells.jsonl")):
        if x["cell"] in ("w0.7", "w0.9", "w1.0"):
            R.append({"w": x["width"], "seed": x["seed"], "complete": bool(x["complete"]), "attrs": attrs(x),
                      "arrive": x.get("arrive", {}), "exit_t": x.get("exit_t", {}), "src": "E7"})
    for x in revlib.load_runs(runs_path()):
        if x["mode"] == "E1b" and 42 <= x["seed"] <= 141:
            R.append({"w": 0.8, "seed": x["seed"], "complete": bool(x["complete"]), "attrs": attrs(x),
                      "arrive": x.get("arrive", {}), "exit_t": x.get("exit_t", {}), "src": "E1b"})
    p = os.path.join(DATA, "revision", "B2", "b2.jsonl")
    if os.path.exists(p):
        for x in revlib.load_runs(p):
            R.append({"w": x["width"], "seed": x["seed"], "complete": bool(x["complete"]), "attrs": x["attrs"],
                      "arrive": x["arrive"], "exit_t": x["exit_t"], "src": "B2"})
    return R


def logit_mle(w, y):
    X = np.column_stack([np.ones_like(w), w])
    th = np.zeros(2)
    for _ in range(200):
        p = 1 / (1 + np.exp(-X @ th))
        g = X.T @ (y - p)
        H = (X * (p * (1 - p))[:, None]).T @ X + 1e-9 * np.eye(2)
        st = np.linalg.solve(H, g)
        th += st
        if np.abs(st).max() < 1e-10:
            break
    return th


def w50_fit(R):
    w = np.array([r["w"] for r in R])
    y = np.array([float(r["complete"]) for r in R])
    a, b = logit_mle(w, y)
    ws = sorted(set(w.tolist()))
    idx = {x: np.where(w == x)[0] for x in ws}
    bs = []
    for _ in range(2000):
        I = np.concatenate([RNG.choice(idx[x], len(idx[x])) for x in ws])
        a_, b_ = logit_mle(w[I], y[I])
        bs.append(-a_ / b_ if b_ > 0 else np.nan)
    # E7 rule: pseudo-counts on the per-width table
    k = np.array([y[idx[x]].sum() for x in ws])
    n = np.array([len(idx[x]) for x in ws])
    th = np.zeros(2)
    X = np.column_stack([np.ones(len(ws)), np.array(ws)])
    for _ in range(200):
        p = 1 / (1 + np.exp(-X @ th))
        g = X.T @ ((k + 0.5) - (n + 1.0) * p)
        H = (X * ((n + 1.0) * p * (1 - p))[:, None]).T @ X + 1e-9 * np.eye(2)
        st = np.linalg.solve(H, g)
        th += st
        if np.abs(st).max() < 1e-10:
            break
    return {"w50_m": float(-a / b), "w50_ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
            "slope_per_m": float(b), "w50_pseudocount_m": float(-th[0] / th[1]),
            "table": [{"w": x, "n": int(nn), "k": int(kk), "completion": float(kk / nn)} for x, kk, nn in zip(ws, k, n)]}


def wc_of(a):
    return fix_a8.w_crit(a["r"], M * a["v0"] / a["tau"])


def main():
    R = runs()
    out = {"doc": __doc__}
    out["fit_all"] = w50_fit(R)
    out["fit_E7_widths_only"] = w50_fit([r for r in R if r["src"] != "B2"])
    # spawn independence of w
    base = {r["seed"]: r["attrs"] for r in R if r["w"] == 0.8}
    same = [all(abs(a["r"] - b["r"]) < 1e-12 and abs(a["v0"] - b["v0"]) < 1e-12 for a, b in zip(r["attrs"], base[r["seed"]]))
            for r in R if r["w"] != 0.8]
    out["spawn_independent_of_w"] = {"n_runs": len(same), "identical": int(sum(same))}
    wc = {r["seed"]: np.array([wc_of(a) for a in r["attrs"]]) for r in R if r["w"] == 0.8}
    allwc = np.concatenate(list(wc.values()))
    runmax = np.array([v.max() for v in wc.values()])
    out["bracket"] = {"w_lo_median_agent_wc_m": float(np.median(allwc)),
                      "w_hi_median_run_max_wc_m": float(np.median(runmax)),
                      "definition": "w_lo: median over the 10000 spawned agents (seeds 42-141) of the width at which the "
                                    "agent's stuck-alone margin is zero; w_hi: median over the 100 spawns of the largest such width"}

    def f(w):
        return float((allwc > w).mean())

    # N_eff from the arrival record
    rows = []
    for r in R:
        if r["w"] < 0.8 - 1e-9:
            continue
        for i_s, a in r["arrive"].items():
            i = int(i_s)
            if wc_of(r["attrs"][i]) > r["w"]:
                rows.append((r["seed"], r["w"], a["n_active"], str(i) in r["exit_t"] or i in r["exit_t"]))
    n_act = np.array([x[2] for x in rows], float)
    passed = np.array([x[3] for x in rows], float)
    seeds = np.array([x[0] for x in rows])
    a, b = logit_mle(n_act, passed)
    n_half = -a / b
    us = np.unique(seeds)
    bs = []
    for _ in range(1000):
        S = RNG.choice(us, len(us))
        I = np.concatenate([np.where(seeds == s)[0] for s in S])
        a_, b_ = logit_mle(n_act[I], passed[I])
        bs.append(-a_ / b_ if b_ > 0 else np.nan)
    out["N_eff"] = {"n_stuck_arrivals": len(rows), "passed": int(passed.sum()), "logit_a": float(a), "logit_b": float(b),
                    "N_eff": float(n_half), "ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
                    "pass_by_n_active": {f"{lo}-{hi}": [int(passed[(n_act >= lo) & (n_act <= hi)].sum()),
                                                        int(((n_act >= lo) & (n_act <= hi)).sum())]
                                         for lo, hi in ((1, 2), (3, 5), (6, 10), (11, 20), (21, 40), (41, 100))}}
    table = out["fit_all"]["table"]
    pred = {}
    q = 1.0 - float(passed.mean())
    out["N_eff"]["q_not_pushed"] = q
    out["N_eff"]["N_eff_q"] = 100.0 * q
    for name, N in (("N100", 100.0), ("Neff", n_half), ("Neff_q", 100.0 * q)):
        dev = 0.0
        rows_p = []
        for t in table:
            p = (1 - f(t["w"])) ** N
            pc = min(max(p, 1e-9), 1 - 1e-9)
            dev += -2 * (t["k"] * np.log(pc) + (t["n"] - t["k"]) * np.log(1 - pc))
            rows_p.append({"w": t["w"], "f": f(t["w"]), "pred": p, "obs": t["completion"]})
        g = lambda w: (1 - f(w)) ** N - 0.5
        try:
            w50 = brentq(g, 0.6, 1.2, xtol=1e-4)
        except ValueError:
            w50 = None
        pred[name] = {"N": N, "w50_pred_m": w50, "neg2loglik": float(dev), "rows": rows_p}
    # free N: the N that best matches the observed completion (check, not a prediction)
    Ns = np.linspace(1, 100, 991)
    devs = []
    for N in Ns:
        d = 0.0
        for t in table:
            pc = min(max((1 - f(t["w"])) ** N, 1e-9), 1 - 1e-9)
            d += -2 * (t["k"] * np.log(pc) + (t["n"] - t["k"]) * np.log(1 - pc))
        devs.append(d)
    pred["N_best"] = {"N": float(Ns[int(np.argmin(devs))]), "neg2loglik": float(min(devs))}
    out["prediction"] = pred
    out["f_at"] = {f"{w:.2f}": f(w) for w in (0.7, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9, 0.92, 0.94, 0.96, 1.0)}
    revlib.out_json("B2", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("doc",)}, indent=1, default=float)[:4000])


if __name__ == "__main__":
    main()
