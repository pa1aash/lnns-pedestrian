"""A1 (revision 3): radius sensitivity of the stuck-alone fraction of the spawned population.

Inputs
  data/E1/E1_runs.jsonl            E1b attributes (r, v0, tau, m) of the 200 x 100 = 20 000 spawned agents, seeds 42-241
  code/sim/core/agent.py           AgentState.create: r = max(N(mu_r, 0.03), 0.15), v0 = max(N(1.34, 0.26), 0.5),
                                   tau ~ U(0.4, 0.6), m = 80 kg, all from one PCG64(seed) stream
  experiments/lib/w2lib.py         Passability(0.8): g_max(r) = max backward wall/jamb force on a lone agent at rest on
                                   the door axis (code's WallForces, A_w = 2000 N, B_w = 0.08 m, sharp jambs), and drive()

Method
  The attributes are regenerated with AgentState.create(seed) for seeds 42-241 (the E1b scenario), once with the paper
  default mu_r = 0.25 m and once with mu_r = 0.225 m (same SD 0.03 m, same clip at 0.15 m). The same PCG64 stream is
  used, so v0 and tau are identical and every raw normal radius draw is shifted by -0.025 m before the clip.
  The regenerated default set is checked against the E1b record (all r, v0, tau equal).
  Stuck alone: g_max(r) > F_rest, with
    (i)  SFM:                F_rest = m v0 / tau                                (drive(kind="C1") at rho = 0)
    (ii) force-coupled ORCA: F_rest = m v0 / tau + w_o(0) m v0 / tau_orca        (drive(kind="C3") at rho = 0;
         w_o(0) = 0.99966, tau_orca = 0.5 s), i.e. the SFM with tau' = tau tau_orca/(tau + tau_orca) and target
         speed (v0/tau + w_o v0/tau_orca) tau' (rev A1 identity).
  g_max(0.225 m) from Passability (interpolated grid) and from w2lib.max_backward directly.
  Fractions with Wilson 95% intervals; paired change by agent (McNemar exact on the discordant agents).

Output data/derived/rev2_A1.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rev2lib import ROOT, mcnemar_exact, np, out_json, wilson  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
cwd = os.getcwd()
import w2lib  # noqa: E402  (chdirs to code/)
os.chdir(cwd)
from sim.core.agent import AgentState  # noqa: E402

SEEDS = range(42, 242)
MU0, MU1, SD = 0.25, 0.225, 0.03


def attrs(seed, mu):
    st = AgentState.create(100, spawn_area=(1.0, 8.0, 1.0, 9.0), goals=np.array([11.0, 5.0]), seed=seed,
                           radius_mean=mu, radius_std=SD)
    return st.radii, st.desired_speeds, st.taus, st.masses


def main():
    rec = {}
    with open(os.path.join(ROOT, "data", "E1", "E1_runs.jsonl")) as f:
        for line in f:
            x = json.loads(line)
            if x["mode"] == "E1b":
                rec[x["seed"]] = x["attrs"]
    assert sorted(rec) == list(SEEDS)
    PASS = w2lib.Passability(0.8)
    out = {"n_agents": 0, "seeds": [42, 241], "width_m": 0.8, "radius_sd_m": SD, "radius_clip_m": 0.15}
    sets = {}
    maxdiff = 0.0
    for mu in (MU0, MU1):
        R, V, T, M = [], [], [], []
        for s in SEEDS:
            r, v, t, m = attrs(s, mu)
            if mu == MU0:
                a = rec[s]
                maxdiff = max(maxdiff, max(abs(a[i]["r"] - r[i]) + abs(a[i]["v0"] - v[i]) + abs(a[i]["tau"] - t[i])
                                           for i in range(100)))
            R.append(r), V.append(v), T.append(t), M.append(m)
        sets[mu] = tuple(np.concatenate(z) for z in (R, V, T, M))
    out["regen_vs_E1b_max_abs_diff"] = maxdiff
    assert maxdiff < 1e-12
    vg = np.vectorize(PASS.gmax)
    res = {}
    for mu, tag in ((MU0, "mu250"), (MU1, "mu225")):
        r, v, t, m = sets[mu]
        assert np.all(m == 80.0)
        g = vg(r)
        f1 = np.array([w2lib.drive(vi, ti, 0.0, kind="C1") for vi, ti in zip(v, t)])
        f3 = np.array([w2lib.drive(vi, ti, 0.0, kind="C3") for vi, ti in zip(v, t)])
        s1, s3 = g > f1, g > f3
        n = len(r)
        res[tag] = {"mu_r": mu, "r_mean": float(r.mean()), "r_sd": float(r.std(ddof=1)),
                    "n_clipped": int((r <= 0.15 + 1e-15).sum()),
                    "gmax_median_N": float(np.median(g)),
                    "sfm": {"k": int(s1.sum()), "n": n, "frac": float(s1.mean()), "wilson95": wilson(int(s1.sum()), n)},
                    "orca": {"k": int(s3.sum()), "n": n, "frac": float(s3.mean()), "wilson95": wilson(int(s3.sum()), n)},
                    "_s1": s1, "_s3": s3}
        out["n_agents"] = n
        out["drive_sfm_median_N"] = float(np.median(f1))
        out["drive_orca_median_N"] = float(np.median(f3))
    for k in ("sfm", "orca"):
        a, b = res["mu250"]["_s1" if k == "sfm" else "_s3"], res["mu225"]["_s1" if k == "sfm" else "_s3"]
        n10, n01 = int((a & ~b).sum()), int((~a & b).sum())
        out[f"change_{k}"] = {"stuck_at_250_only": n10, "stuck_at_225_only": n01, "mcnemar_p": mcnemar_exact(n10, n01),
                              "diff": float(b.mean() - a.mean()),
                              "ratio": float(b.mean() / a.mean()) if a.mean() > 0 else None}
    for tag in res:
        res[tag].pop("_s1"), res[tag].pop("_s3")
    out.update(res)
    out["gmax_N"] = {"r0225": PASS.gmax(0.225), "r0250": PASS.gmax(0.25),
                     "r0225_direct": w2lib.max_backward(0.225, width=0.8),
                     "r0250_direct": w2lib.max_backward(0.25, width=0.8)}
    out["gmax_ratio_225_over_250"] = out["gmax_N"]["r0225"] / out["gmax_N"]["r0250"]
    out["drive_sfm_median_over_gmax225"] = out["drive_sfm_median_N"] / out["gmax_N"]["r0225"]
    out["drive_sfm_median_over_gmax250"] = out["drive_sfm_median_N"] / out["gmax_N"]["r0250"]
    out["paper_check"] = {"E1b_stuck_alone_frac_C1": 0.2343, "E1b_stuck_alone_frac_C3_rest": 0.01275}
    print(json.dumps(out, indent=1, default=float))
    print(out_json("A1", out))


if __name__ == "__main__":
    main()
