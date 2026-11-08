"""Choose the hero pair snapshot from the production E7b library (corrected-forward, B_w = 0.04, convex_union).

Candidates: exactly two residual agents. For each: stuck-alone margins, force balance at the frozen state,
Hessian eigenvalues of the rest-state potential (strict minimum at b = 0), and the lateral-bias fold b* =
smallest b for which the relaxed potential along the common lateral shift has no local minimum.
Compared with the pilot snapshot w25_B0.04_seed43 (positions (9.610, 4.557), (9.595, 5.444), radii 0.281, 0.296,
Hessian eigenvalues 85 / 1124 / 3192 / 3285 N/m, fold between b = 0.01 and 0.03).

    PYTHONPATH=code <plan python> experiments/hero/select_pair.py
Writes data/derived/hero/pair_selection.json.
"""
import glob
import json
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import hero_phys as hp  # noqa: E402
from w2lib import Passability  # noqa: E402

REPO = hp.REPO
PILOT = dict(pos=[[9.610, 4.557], [9.595, 5.444]], r=[0.281, 0.296], eig=[85, 1124, 3192, 3285])


def hessian(f, X, h=1e-4):
    n = len(X)
    H = np.zeros((n, n))
    U0 = f.U(X)
    for a in range(n):
        for b in range(a, n):
            ea = np.zeros(n); ea[a] = h
            eb = np.zeros(n); eb[b] = h
            H[a, b] = H[b, a] = ((f.U(X + ea) - 2 * U0 + f.U(X - ea)) / h ** 2 if a == b else
                                 (f.U(X + ea + eb) - f.U(X + ea - eb) - f.U(X - ea + eb) + f.U(X - ea - eb)) / (4 * h * h))
    return H


def has_min(snap, ids, b, cs):
    U, _ = hp.pair_ribbon(snap, ids, b, cs)
    d = np.diff(U) / np.diff(cs)
    return bool(np.any((d[:-1] < 0) & (d[1:] > 0))), U


def fold(snap, ids, cs, lo=0.0, hi=0.12, n=7):
    if not has_min(snap, ids, hi, cs)[0] is False:
        return None
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if has_min(snap, ids, mid, cs)[0]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    cs = np.linspace(-0.12, 0.12, 25)
    rows = []
    for f in sorted(glob.glob(str(REPO / "data/E7b/library/*.pkl"))):
        snap = pickle.load(open(f, "rb"))
        st = snap["state"]
        ids = sorted((int(i) for i in st.active_indices), key=lambda i: st.positions[i, 1])
        if len(ids) != 2:
            continue
        P, r = st.positions[ids], st.radii[ids]
        sym = float(P[:, 1].mean() - 5.0)
        if abs(sym) > 0.035 or abs(r[0] - r[1]) > 0.04 or not 0.84 < P[1, 1] - P[0, 1] < 0.91:
            continue
        pas = Passability(width=snap["width"], **{k: snap["params"][k] for k in ("A_w", "B_w") if k in snap["params"]})
        rho = hp.frozen_rho(st, ids)
        margin = [float(pas.margin(st.radii[i], st.desired_speeds[i], st.taus[i], rho[k])) for k, i in enumerate(ids)]
        F = hp.forces_at(snap, ids)
        fld = hp.RestField(snap, ids)
        ev = np.linalg.eigvalsh(hessian(fld, fld.X0))
        b_fold = fold(snap, ids, cs) if min(ev) > 0 and max(margin) < 0 else None
        rows.append({"snap": Path(f).name, "pos": P.round(3).tolist(), "r": r.round(3).tolist(), "sym_m": round(sym, 3),
                     "margin_N": np.round(margin, 1).tolist(), "max_force_balance_N": float(np.abs(F["total"]).max()),
                     "hess_eig": np.round(ev, 1).tolist(), "fold_b": b_fold,
                     "dist_to_pilot": float(np.abs(P - np.array(PILOT["pos"])).max() + np.abs(r - np.array(PILOT["r"])).max())})
        print(rows[-1], flush=True)
    json.dump(rows, open(REPO / "data/derived/hero/pair_selection.json", "w"), indent=1)
