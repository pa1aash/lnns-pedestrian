"""A4 (revision 3): beta span of the time-step probe (E3).

Inputs
  data/E3/e3_dt.jsonl              E3 rows (20 snapshots x 2 arms x 3 time steps x 20 restarts + C3_rvo2 rows); every
                                   noise row carries sigma_i, beta_ref, tau_b, dU_i, its own k_B T_eff and beta
  data/derived/E3_analysis.json    per-snapshot cells (cross-check)
  experiments/lib/teff.py          k_B T_eff = m s^2 / (1 - (1 - dt/tau)^2), s = sigma (per_step) or
                                   sigma sqrt(dt/0.01) (dt_scaled)

Method
  Noise level per snapshot (experiments/E3/e3_dt.py): sigma_i is set so that beta = dU_i / k_B T_eff = beta_ref at
  dt = 0.01 s with the blocker's tau_b; beta_ref = 1.5 for even dU rank, 2.5 for odd (10 snapshots each).
  beta at dt = 0.005, 0.01, 0.02 s is recomputed with teff.kT_eff for both arms
    per_step   sigma fixed at sigma_i (the arm that carries the time-step signature, Fig. escape(c), ell);
    dt_scaled  sigma_i sqrt(dt/0.01) (k_B T_eff about fixed),
  checked against the stored row values, and reported per snapshot, per beta_ref level and overall (min, max).

Output data/derived/rev2_A4.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rev2lib import ROOT, out_json  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments", "lib"))
from teff import kT_eff  # noqa: E402

DTS = (0.005, 0.01, 0.02)
ARMS = ("per_step", "dt_scaled")


def tag(dt):
    return "dt" + f"{dt:g}".replace(".", "p")


def main():
    snaps, maxdev = {}, 0.0
    with open(os.path.join(ROOT, "data", "E3", "e3_dt.jsonl")) as f:
        for line in f:
            x = json.loads(line)
            if x.get("mode") not in ARMS:
                continue
            s = snaps.setdefault(x["job_id"].split("|")[0], {k: x[k] for k in
                                                             ("sigma_i", "beta_ref", "tau_b", "dU_i", "dU_rank")})
            b = s["dU_i"] / kT_eff(s["sigma_i"], x["dt"], s["tau_b"], mode=x["mode"])
            maxdev = max(maxdev, abs(b - x["beta"]))
    an = json.load(open(os.path.join(ROOT, "data", "derived", "E3_analysis.json")))["snapshots"]
    assert set(an) == set(snaps) and len(snaps) == 20
    per, allb = {}, {a: [] for a in ARMS}
    lev = {}
    for name, s in sorted(snaps.items(), key=lambda kv: kv[1]["dU_rank"]):
        row = {"dU_rank": s["dU_rank"], "dU_J": s["dU_i"], "tau_b_s": s["tau_b"], "sigma_i_m_s": s["sigma_i"],
               "beta_ref": s["beta_ref"]}
        for a in ARMS:
            bs = {tag(dt): s["dU_i"] / kT_eff(s["sigma_i"], dt, s["tau_b"], mode=a) for dt in DTS}
            for k, v in bs.items():
                maxdev = max(maxdev, abs(v - an[name]["cells"][a][k]["beta"]))
            row[a] = bs
            allb[a] += list(bs.values())
            L = lev.setdefault(f"b{s['beta_ref']:g}".replace(".", "p"), {}).setdefault(a, {tag(dt): [] for dt in DTS})
            for k, v in bs.items():
                L[k].append(v)
        row["per_step_span"] = [row["per_step"]["dt0p005"], row["per_step"]["dt0p02"]]
        per[name] = row
    out = {"n_snapshots": len(per), "max_abs_dev_vs_stored": maxdev, "per_snapshot": per,
           "by_level": {lv: {a: {k: {"min": min(v), "max": max(v)} for k, v in d.items()} for a, d in A.items()}
                        for lv, A in lev.items()},
           "overall": {a: {"min": min(allb[a]), "max": max(allb[a])} for a in ARMS}}
    ps = [r["per_step"] for r in per.values()]
    out["per_step_ratio_005"] = {"min": min(p["dt0p005"] / p["dt0p01"] for p in ps),
                                 "max": max(p["dt0p005"] / p["dt0p01"] for p in ps)}
    out["per_step_ratio_02"] = {"min": min(p["dt0p02"] / p["dt0p01"] for p in ps),
                                "max": max(p["dt0p02"] / p["dt0p01"] for p in ps)}
    out["cells_below_1p5"] = {a: sum(v < 1.5 - 1e-9 for v in allb[a]) for a in ARMS}
    out["cells_below_1"] = {a: sum(v < 1.0 for v in allb[a]) for a in ARMS}
    out["n_cells_per_arm"] = len(allb["per_step"])
    out["n_per_level"] = {lv: len(A["per_step"]["dt0p01"]) for lv, A in lev.items()}
    assert maxdev < 1e-9, maxdev
    print(json.dumps({k: v for k, v in out.items() if k != "per_snapshot"}, indent=1))
    for n, r in per.items():
        print(n, r["beta_ref"], round(r["dU_J"], 2), [round(r["per_step"][tag(d)], 3) for d in DTS],
              [round(r["dt_scaled"][tag(d)], 3) for d in DTS])
    print(out_json("A4", out))


if __name__ == "__main__":
    main()
