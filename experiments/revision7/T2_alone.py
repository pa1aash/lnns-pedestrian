"""Task 2 runs: alone-condition escape on every barrier-set snapshot at beta = 1.5, 2.5, 3.5, 5, 7 (20 restarts each).

Barrier set: the 56 screening-set snapshots (data/derived/selection.json E2, 60) whose full barrier passes the gate
(data/BAR/barriers_gated.json); k = index in that order (0-55). Barrier: the gate's accepted alone barrier dU_alone
(the alone energy span equals it for all 56, rev5_X1.json). Noise and protocol exactly as E4 / B3: condition
alone (other residual agents deactivated), C1, CF flags, dt = 0.01 s, sigma = teff.sigma_for(dU / beta, 0.01 s,
tau_blocker), escape = blocker centre x >= 10 m; integrated by alonebatch.run_multi (bit-identical to
runlib.escape, validated on 400 E4 restarts). Censoring: beta 1.5 and 2.5 at 300 s, 3.5 at 900 s (E4); beta 5 and 7
by the B3 rule T = ln(20 / 4.5) / lambda_slow, lambda_slow = min of the free Arrhenius fit (E4 estimator, all three
levels >= 3 events) and the fixed-slope prefactor fit nu_hat exp(-beta) extrapolated from beta 1.5-3.5 (when the
free fit is not defined, the fixed-slope one alone; nu_hat over the levels with events), capped at 40 000 s.
Reuse: the E4 alone cells (10 snapshots, beta 1.5-3.5, data/E4/e4_escape.jsonl) and the B3 cells at beta 5 and 7
(3 snapshots, data/revision/B3/b3.jsonl) are taken as they are, not rerun.
Noise seeds of new restarts: 200000 + 1000 k + 100 level + rep (level 0-4 for beta 1.5, 2.5, 3.5, 5, 7; rep 0-19),
disjoint from every seed range in experiments/SEEDS.md (all below 106000).
Output: data/revision7/T2/t2_alone.jsonl (one record per restart, job_id "<tag>|alone|b<beta>|<rep>").
Usage: T2_alone.py A | B   (phase A: beta 1.5-3.5; phase B: beta 5, 7; each in 3 parallel processes)"""
import json
import math
import multiprocessing as mp
import os
import pickle
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import np  # noqa: E402
import alonebatch as AB  # noqa: E402
from teff import M, sigma_for  # noqa: E402

BETAS = (1.5, 2.5, 3.5, 5.0, 7.0)
T_CENS_A = {1.5: 300.0, 2.5: 300.0, 3.5: 900.0}
N_REP, SEED0, T_CAP = 20, 200000, 40000.0
OUT = os.path.join(L.data_dir("T2"), "t2_alone.jsonl")


def snapshots():
    G = json.load(open(os.path.join(L.DATA, "BAR", "barriers_gated.json")))["barriers"]
    sel = json.load(open(os.path.join(L.DERIVED, "selection.json")))
    e4 = {s["tag"] for s in sel["E4"]["snapshots"]}
    S = []
    for s in sel["E2"]["snapshots"]:
        g = G[s["tag"]]
        if not g["full"]["accepted"]:
            continue
        assert g["alone"]["accepted"]
        path = os.path.join(L.ROOT, s["snap"])
        st = pickle.load(open(path, "rb"))["state"]
        S.append({"tag": s["tag"], "k": len(S), "snap": path, "blocker": s["blocker"], "class": s["class"],
                  "n_resid": s["n_resid"], "tau_b": float(st.taus[s["blocker"]]), "v0_b": float(st.desired_speeds[s["blocker"]]),
                  "r_b": float(st.radii[s["blocker"]]), "dU": float(g["alone"]["dU"]), "in_E4": s["tag"] in e4})
    assert len(S) == 56
    return S


def existing():
    """{(tag, beta): [records]} from E4 (alone) and B3, in the T2 record format."""
    out = defaultdict(list)
    for r in L.load_runs(os.path.join(L.DATA, "E4", "e4_escape.jsonl")):
        if r["cond"] == "alone":
            out[(r["snap"][:-4], r["beta_ref"])].append({"escape_t": r["escape_t"], "t_run": r["t_run"],
                                                          "censored": r["censored"], "source": "E4", "sigma": r["sigma"],
                                                          "t_cens": r["t_cens"], "noise_seed": r["noise_seed"]})
    for r in L.load_runs(os.path.join(L.DATA, "revision", "B3", "b3.jsonl")):
        if r["beta_ref"] in (5.0, 7.0):
            out[(r["tag"], r["beta_ref"])].append({"escape_t": r["escape_t"], "t_run": r["t_run"],
                                                    "censored": r["censored"], "source": "B3", "sigma": r["sigma"],
                                                    "t_cens": r["t_cens"], "noise_seed": r["noise_seed"]})
    return out


def records():
    R = defaultdict(list)
    for (tag, b), v in existing().items():
        R[(tag, b)] += v
    if os.path.exists(OUT):
        for r in L.load_runs(OUT):
            R[(r["tag"], r["beta_ref"])].append(r)
    return R


def wls(x, y, w):
    W = w.sum()
    xm, ym = (w * x).sum() / W, (w * y).sum() / W
    s = (w * (x - xm) * (y - ym)).sum() / (w * (x - xm) ** 2).sum()
    return s, ym - s * xm


def lam_slow(s, R, beta):
    """B3 censoring rule from the beta 1.5-3.5 cells of snapshot s."""
    d, T, x = [], [], []
    for b in (1.5, 2.5, 3.5):
        rows = R[(s["tag"], b)]
        d.append(sum(not r["censored"] for r in rows))
        T.append(sum(r["t_run"] for r in rows))
        x.append(b / s["dU"])                 # 1 / k_B T_eff
    d, T, x = np.array(d, float), np.array(T), np.array(x)
    lf = None
    if (d >= 3).all():
        sl, a = wls(x, np.log(d / T), d)
        lf = math.exp(a + sl * beta / s["dU"])
    m = d > 0
    nu = math.exp(float((d[m] * (np.log(d[m] / T[m]) + s["dU"] * x[m])).sum() / d[m].sum())) if m.any() else None
    lx = nu * math.exp(-beta) if nu else None
    lam = min(v for v in (lf, lx) if v is not None) if (lf or lx) else None
    return lam, lf, lx


def specs(phase):
    S, R = snapshots(), records()
    have = {(t, b) for (t, b) in R}
    out = []
    for s in S:
        for lv, beta in enumerate(BETAS):
            if (phase == "A") != (beta < 4):
                continue
            if (s["tag"], beta) in have and any(r.get("source") in ("E4", "B3") for r in R[(s["tag"], beta)]):
                continue
            if beta < 4:
                T, lf, lx = T_CENS_A[beta], None, None
            else:
                lam, lf, lx = lam_slow(s, R, beta)
                T = min(T_CAP, math.log(N_REP / 4.5) / lam) if lam else T_CAP
            sg = sigma_for(s["dU"] / beta, 0.01, s["tau_b"])
            for rep in range(N_REP):
                out.append({"key": f"{s['tag']}|alone|b{beta:g}|{rep}", "tag": s["tag"], "k": s["k"], "snap": s["snap"],
                            "blocker": s["blocker"], "sigma": sg, "beta_ref": beta, "dU_cond": s["dU"],
                            "tau_b": s["tau_b"], "kT_eff": s["dU"] / beta, "m": M, "rep": rep, "t_cens": round(T, 1),
                            "noise_seed": SEED0 + 1000 * s["k"] + 100 * lv + rep, "lam_pred_free": lf,
                            "lam_pred_fixed": lx})
    done = {r["job_id"] for r in L.load_runs(OUT)} if os.path.exists(OUT) else set()
    return [x for x in out if x["key"] not in done]


def _work(chunk):
    res = AB.run_multi(chunk)
    recs = []
    for x in chunk:
        e, tr = res[x["key"]]
        r = {k: v for k, v in x.items() if k not in ("snap", "key")}
        r.update({"job_id": x["key"], "cond": "alone", "escape_t": e, "censored": e is None, "t_run": tr,
                  "snap": os.path.basename(x["snap"]), "source": "rev7"})
        recs.append(r)
    return recs


def main(phase, nproc=3):
    J = specs(phase)
    print(f"T2 phase {phase}: {len(J)} restarts", flush=True)
    if not J:
        return
    # chunks: by level, the slowest level split further, balanced by t_cens sum
    by = defaultdict(list)
    for x in J:
        by[x["beta_ref"]].append(x)
    chunks = []
    for b, xs in sorted(by.items()):
        n = 1 if len(by) >= nproc else max(1, nproc - len(by) + 1) if b == max(by) else 1
        tags = sorted({x["tag"] for x in xs})
        for i in range(n):
            sub = set(tags[i::n])
            chunks.append([x for x in xs if x["tag"] in sub])
    with mp.get_context("fork").Pool(nproc) as pool, open(OUT, "a") as f:
        for recs in pool.imap_unordered(_work, chunks):
            for r in recs:
                f.write(json.dumps(r, default=float) + "\n")
            f.flush()
            print(f"  chunk done: {len(recs)} restarts, beta {recs[0]['beta_ref']}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
