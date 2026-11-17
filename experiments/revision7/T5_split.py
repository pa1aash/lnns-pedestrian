"""Task 5: split-sample matching of per-step noise to force-coupled ORCA (RVO2), as rev2_A6 did for the bias b*.

(1) Lone keystones (34, selection.json E2). Noise quenches (C1 + sigma, 120 s): sigma = 0.03, 0.05, 0.07 m/s with 5
    seeds (data/E2/e2_quench.jsonl) and 0.0717 m/s with 20 seeds (data/N1/n1.jsonl); sigma = 0 is the SFM restart,
    which frees no lone keystone. f_i(sigma) = fraction of seeds whose blocker exits within 120 s. ORCA: the
    unperturbed C3_rvo2 quench, freed within 120 s. 200 random halves of 17 (Generator(PCG64(2026)), permutation per
    split; first 17 fit). Primary fit (the rule that gave 0.0717, experiments/runs3/N1.py): binomial-logit fit of the
    per-restart outcomes at sigma = 0.03, 0.05, 0.07 (E2, 5 seeds per snapshot) over S, inverted at ORCA's freed
    fraction on S -> sigma_S; held-out difference e = P_H(sigma_S) - ORCA_H with P_H the same logit fit on H (no
    clipping; sigma_S may lie above 0.07 as 0.0717 does). Secondary (interpolation): sigma_S = the smallest sigma at which the piecewise-linear F_S(sigma) = mean_S f_i
    reaches ORCA's freed fraction on S (grid 0, 0.03, 0.05, 0.07, 0.0717; if never reached, the grid maximum).
    Held-out difference e = F_H(sigma_S) - ORCA_H (F_H interpolated the same way). Reference spread: ORCA_H - ORCA_S.
(2) Whole runs (186 seeds 242-427). Completion against sigma exists only on E5b's seeds 42-141 (C1 + sigma, sigma =
    0.03-0.07, 100 runs each); on the 186 seeds the noise was run at sigma* = 0.0467 only (data/E6/e6b.jsonl). Fit on
    a half S of 93 seeds: sigma_S = logit inversion (experiments/lib/fits.py on E5b, as E6) at ORCA's completion
    rate on S (data/E6/e6a.jsonl). Held-out: noise completion on H at sigma_S, estimated as the observed E6b
    completion on H at sigma* shifted along the E5b logit curve, P_H(sigma_S) = expit(logit(c_H) + b (sigma_S -
    sigma*)); e = P_H(sigma_S) - ORCA_H. Reference: ORCA_H - ORCA_S. 200 random halves, PCG64(2026).
Output: data/derived/rev7_T5.json"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import np  # noqa: E402
import fits  # noqa: E402

GRID = (0.0, 0.03, 0.05, 0.07, 0.0717)
NSPLIT = 200


def summ(e):
    e = np.asarray(e)
    return {"median": float(np.median(e)), "lo95": float(np.percentile(e, 2.5)), "hi95": float(np.percentile(e, 97.5)),
            "mean": float(e.mean()), "mean_abs": float(np.abs(e).mean())}


def fit_sigma(F, target):
    for a in range(len(GRID) - 1):
        f0, f1 = F[a], F[a + 1]
        if f0 <= target <= f1 and f1 > f0:
            return GRID[a] + (target - f0) / (f1 - f0) * (GRID[a + 1] - GRID[a])
        if f0 >= target:
            return GRID[a]
    return GRID[-1]


def interp(F, s):
    return float(np.interp(s, GRID, F))


def lone():
    sel = [s for s in json.load(open(os.path.join(L.DERIVED, "selection.json")))["E2"]["snapshots"]
           if s["class"] == "lone_keystone"]
    blk = {s["tag"]: str(s["blocker"]) for s in sel}
    tags = [s["tag"] for s in sel]
    hits = {(t, g): [] for t in tags for g in GRID[1:]}
    orca = {}
    for r in L.load_runs(os.path.join(L.DATA, "E2", "e2_quench.jsonl")):
        t = r["job_id"].split("|")[0]
        if t not in blk:
            continue
        e = r["exits"].get(blk[t])
        fr = e is not None and e <= 120.0 + 1e-9
        if r["arm"] in ("noise0.03", "noise0.05", "noise0.07"):
            hits[(t, float(r["arm"][5:]))].append(fr)
        elif r["arm"] == "C3_rvo2" and r["perturb"] is None:
            orca[t] = fr
    for r in L.load_runs(os.path.join(L.DATA, "N1", "n1.jsonl")):
        t = r["job_id"].split("|")[0]
        if t in blk:
            e = r["exits"].get(blk[t])
            hits[(t, 0.0717)].append(e is not None and e <= 120.0 + 1e-9)
    f = np.array([[0.0] + [float(np.mean(hits[(t, g)])) for g in GRID[1:]] for t in tags])
    o = np.array([float(orca[t]) for t in tags])
    n_seeds = {f"{g:g}": sorted({len(hits[(t, g)]) for t in tags}) for g in GRID[1:]}
    rng = np.random.Generator(np.random.PCG64(2026))
    E, REF, SIG = [], [], []
    for _ in range(NSPLIT):
        p = rng.permutation(len(tags))
        S, H = p[:17], p[17:]
        s = fit_sigma(f[S].mean(0), o[S].mean())
        SIG.append(s)
        E.append(interp(f[H].mean(0), s) - o[H].mean())
        REF.append(o[H].mean() - o[S].mean())
    full_s = fit_sigma(f.mean(0), o.mean())
    # primary: logit on the E2 levels
    kk = np.array([[sum(hits[(t, g)]) for g in GRID[1:4]] for t in tags], float)
    nn = np.array([[len(hits[(t, g)]) for g in GRID[1:4]] for t in tags], float)

    def lfit(idx):
        return fits.fit_logit(GRID[1:4], kk[idx].sum(0), nn[idx].sum(0))
    Fall = lfit(np.arange(len(tags)))
    s_all = (math.log(o.mean() / (1 - o.mean())) - Fall["a"]) / Fall["b"]
    rng2 = np.random.Generator(np.random.PCG64(2026))
    EL, SL = [], []
    for _ in range(NSPLIT):
        p = rng2.permutation(len(tags))
        S, H = p[:17], p[17:]
        tS = min(max(o[S].mean(), 0.5 / 17), 1 - 0.5 / 17)
        FS, FH = lfit(S), lfit(H)
        sS = (math.log(tS / (1 - tS)) - FS["a"]) / FS["b"]
        SL.append(sS)
        EL.append(1.0 / (1.0 + math.exp(-(FH["a"] + FH["b"] * sS))) - o[H].mean())
    return {"n": len(tags), "orca_freed": int(o.sum()), "logit_full": {"a": Fall["a"], "b": Fall["b"], "sigma": s_all},
            "logit_heldout_error": summ(EL), "logit_sigma_S": summ(SL), "F_full_by_sigma": dict(zip(map(str, GRID), f.mean(0).tolist())),
            "n_seeds": n_seeds, "interp_sigma_full_fit": full_s, "interp_heldout_error": summ(E), "split_alone": summ(REF),
            "interp_sigma_S": summ(SIG), "n_sigma_S_at_grid_max": int(sum(x >= GRID[-1] for x in SIG))}


def whole():
    a = {r["seed"]: bool(r["complete"]) for r in L.load_runs(os.path.join(L.DATA, "E6", "e6a.jsonl"))}
    b = {r["seed"]: bool(r["complete"]) for r in L.load_runs(os.path.join(L.DATA, "E6", "e6b.jsonl"))}
    sstar = json.load(open(os.path.join(L.DERIVED, "sigma_star.json")))
    e5 = sstar["E5b"]
    F = fits.fit_logit(e5["sigma"], e5["k"], e5["n"])
    s_star = 0.0467
    seeds = sorted(a)
    assert len(seeds) == 186 and sorted(b) == seeds
    A = np.array([a[s] for s in seeds], float)
    B = np.array([b[s] for s in seeds], float)
    logit = lambda p: math.log(p / (1 - p))  # noqa: E731
    rng = np.random.Generator(np.random.PCG64(2026))
    E, REF, SIG, Eobs = [], [], [], []
    for _ in range(NSPLIT):
        p = rng.permutation(186)
        S, H = p[:93], p[93:]
        tS = A[S].mean()
        sS = (logit(tS) - F["a"]) / F["b"]
        SIG.append(sS)
        cH = min(max(B[H].mean(), 0.5 / 93), 1 - 0.5 / 93)
        pH = 1.0 / (1.0 + math.exp(-(logit(cH) + F["b"] * (sS - s_star))))
        E.append(pH - A[H].mean())
        Eobs.append(B[H].mean() - A[H].mean())
        REF.append(A[H].mean() - A[S].mean())
    return {"n": 186, "orca_complete": int(A.sum()), "noise_sigma_star_complete": int(B.sum()), "logit_E5b": F,
            "sigma_star": s_star, "heldout_error": summ(E), "heldout_error_at_sigma_star": summ(Eobs),
            "split_alone": summ(REF), "sigma_S": summ(SIG)}


def main():
    out = {"doc": __doc__, "lone": lone(), "whole": whole()}
    A6 = json.load(open(os.path.join(L.DERIVED, "rev2_A6.json")))
    out["bstar_reference_rev2_A6"] = {k: v for k, v in A6.items() if k in ("headline", "summary")}
    print(json.dumps({k: out[k] for k in ("lone", "whole")}, indent=1, default=float)[:3000])
    print(L.out_json("T5", out))


if __name__ == "__main__":
    main()
