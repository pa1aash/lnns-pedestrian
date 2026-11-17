"""Task 3: which rate theory gives the 0.90 slope ratio. Alone condition, the 10 Arrhenius-set snapshots (E4).

For each snapshot, as a function of beta = dU / k_B T_eff (dU = the alone barrier, saddle minus minimum of U):
  k_TST(beta)  exact 2-D transition-state rate from the configurational integral of U on a 4 mm grid
               (experiments/revision2/A3_arrhenius.theory: k_TST = sqrt(kT / 2 pi m) Z_saddle-line / Z_well, the
               well being x < x_saddle; anharmonic well and saddle line included, not their harmonic approximation)
  kappa        Kramers (spatial-diffusion) factor sqrt(1 + (gamma / 2 omega_b)^2) - gamma / 2 omega_b, gamma = 1/tau
  A(Delta)     Mel'nikov-Meshkov depopulation factor, Delta = gamma S(E_b) / k_B T (S the axial action at the
               saddle energy)
Slope ratio r of a model rate k(beta): least squares of ln k on beta over beta = 1.5, 2.5, 3.5, 5, 7 (unweighted,
one snapshot) and, pooled over snapshots, with snapshot intercepts; r = -slope (beta is in units of dU). The
prefactor nu(beta) = k e^beta; its temperature dependence d ln nu / d ln T = -d ln nu / d ln beta is reported at
the ends of the range and as the ratio nu(1.5) / nu(7). Also the harmonic-TST (Vineyard) prefactor for reference.
Output: data/derived/rev7_T3.json"""
import json
import math
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
from rev7lib import np  # noqa: E402
sys.path.insert(0, os.path.join(L.ROOT, "experiments", "revision2"))
import A3_arrhenius as A3  # noqa: E402
import bar  # noqa: E402
import e4_escape  # noqa: E402

GRID = (1.5, 2.5, 3.5, 5.0, 7.0)
FINE = tuple(np.round(np.arange(1.5, 7.0001, 0.25), 2))


def slope(b, y):
    return float(-np.polyfit(np.asarray(b), np.asarray(y), 1)[0])


def main():
    A3.BETAS = tuple(sorted(set(GRID) | set(FINE)))
    rows = {json.loads(l)["job_id"]: json.loads(l) for l in open(os.path.join(L.DATA, "BAR", "barriers.jsonl"))}
    out = {"doc": __doc__, "snapshots": {}}
    pooled = {"tst": [], "kappa": [], "full": []}
    for k, s in enumerate(e4_escape.snapshots()):
        tag = s["tag"]
        snap = pickle.load(open(s["snap"], "rb"))
        f = bar.Field(snap, [s["blocker"]], [], rho_mode="zero")
        th = A3.theory(tag, s, f, rows[tag])
        lv = th["levels"]
        rec = {"dU": th["U_saddle_minus_min"], "dU_gate": s["dU"]["alone"], "kappa": th["kappa"],
               "gamma_over_omega_b": th["gamma"] / th["omega_b"], "omega_b": th["omega_b"], "action_S": th["action_S"],
               "nu_harmonic_tst": th["nu_harmonic_tst"], "levels": {}}
        for b in A3.BETAS:
            L_ = lv[f"{b:g}"]
            rec["levels"][f"{b:g}"] = {"k_tst": L_["k_tst"], "kappa_k_tst": L_["kappa"] * L_["k_tst"],
                                       "A_kappa_k_tst": L_["lam"], "A": L_["A_mm"], "Delta": L_["Delta"],
                                       "nu_tst": L_["nu_tst"], "nu_tst_over_harmonic": L_["nu_tst"] / th["nu_harmonic_tst"]}
        for name, key in (("tst", "k_tst"), ("kappa", "kappa_k_tst"), ("full", "A_kappa_k_tst")):
            y = [math.log(rec["levels"][f"{b:g}"][key]) for b in GRID]
            rec[f"ratio_{name}"] = slope(GRID, y)
            pooled[name] += [(k, b, yy) for b, yy in zip(GRID, y)]
            yf = [math.log(rec["levels"][f"{b:g}"][key]) + b for b in FINE]  # ln nu
            dl = np.gradient(yf, np.log(FINE))
            rec[f"prefactor_{name}"] = {"nu_1p5": math.exp(yf[0]), "nu_7": math.exp(yf[-1]),
                                       "nu_1p5_over_nu_7": math.exp(yf[0] - yf[-1]),
                                       "dlnnu_dlnT_at_1p5": float(-dl[0]), "dlnnu_dlnT_at_7": float(-dl[-1])}
        rec["A_at"] = {f"{b:g}": rec["levels"][f"{b:g}"]["A"] for b in GRID}
        out["snapshots"][tag] = rec
        print(tag, round(rec["dU"], 2), "r_tst %.3f r_kappa %.3f r_full %.3f  A(1.5) %.3f A(7) %.3f  nu1.5/nu7 tst %.3f full %.3f" % (
            rec["ratio_tst"], rec["ratio_kappa"], rec["ratio_full"], rec["A_at"]["1.5"], rec["A_at"]["7"],
            rec["prefactor_tst"]["nu_1p5_over_nu_7"], rec["prefactor_full"]["nu_1p5_over_nu_7"]), flush=True)
    tags = list(out["snapshots"])
    for name, pts in pooled.items():
        X = np.array([[1.0 if p[0] == j else 0.0 for j in range(len(tags))] + [-p[1]] for p in pts])
        y = np.array([p[2] for p in pts])
        out[f"pooled_ratio_{name}"] = float(np.linalg.lstsq(X, y, rcond=None)[0][-1])
        v = [out["snapshots"][t][f"ratio_{name}"] for t in tags]
        out[f"ratio_{name}_range"] = [min(v), max(v)]
        out[f"ratio_{name}_median"] = float(np.median(v))
        pf = [out["snapshots"][t][f"prefactor_{name}"]["nu_1p5_over_nu_7"] for t in tags]
        out[f"nu_ratio_{name}_range"] = [min(pf), max(pf)]
    print({k: v for k, v in out.items() if k.startswith(("pooled", "ratio", "nu_ratio"))})
    print(L.out_json("T3", out))


if __name__ == "__main__":
    main()
