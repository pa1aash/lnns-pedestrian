"""T3 check: realised velocity variance of a trapped blocker against k_B T_eff = m sigma^2 / (1 - (1 - dt/tau)^2).

Three E3 lone-keystone snapshots spanning the barrier range (E1b seed80, seed114, seed83; one residual agent),
C1 with corrected-forward flags and per-step noise, sigma set so that dU / k_B T_eff = 6 at dt = 0.01 s (the
blocker stays trapped), dt in {0.005, 0.01, 0.02} s, one 60 s run each (noise seed 31000 + k), 1 worker.
Blocker velocity moments are accumulated after a 2 s burn-in while x < 9.95 (as runlib.escape).

Predictions per component (a = 1 - dt/tau):
  free       <v^2> = sigma^2 / (1 - a^2)                              (T3 formula, no position coupling)
  harmonic   <v^2> = 2 sigma^2 / ((1 - a)(2 + 2a - w^2 dt^2))          (fixed order: noise before the position
             update; w^2 = eigenvalue of the rest-state Hessian / m along that component's eigen-direction,
             from central differences of the code's C1 force at v = 0, h = 1e-5 m)
  published order (clamp, then noise, position from the pre-noise velocity) gives
             <v^2> = sigma^2 (2 - (1 - a) w^2 dt^2) / ((1 - a)(2 + 2a - w^2 dt^2)); both reduce to the free form
             as w dt -> 0. Configurational temperature (fixed order): K <x^2> = m sigma^2 (1 + a) / ((1 - a)(2 + 2a - w^2 dt^2)),
             i.e. (1 - dt / 2 tau) times the kinetic one at w dt -> 0.
Output: data/derived/T3_variance.json.
"""
import json
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from e1lib import CF, DATA, ROOT  # noqa: E402
from teff import M, kT_eff, sigma_for  # noqa: E402
from w2lib import restore  # noqa: E402

OUT = os.path.join(DATA, "derived", "T3_variance.json")
TAGS = ("E1b_seed80", "E1b_seed114", "E1b_seed83")
DTS = (0.005, 0.01, 0.02)
BETA, T_RUN, BURN = 6.0, 60.0, 2.0


def force_on(sim, b, x):
    st = sim.state
    old = st.positions[b].copy()
    st.positions[b] = x
    v_old = st.velocities.copy()
    st.velocities[:] = 0.0
    a = st.active_indices
    nl = [[int(j) for j in a if j != i] if i in a else [] for i in range(st.n)]
    rho = np.array([len(n) / (np.pi * 9.0) for n in nl])
    F = sim.steering.compute_forces(st, nl, sim.world.walls, rho)[b].copy()
    st.positions[b] = old
    st.velocities[:] = v_old
    return F


def hessian(sim, b, h=1e-5):
    x0 = sim.state.positions[b].copy()
    H = np.zeros((2, 2))
    for k in range(2):
        e = np.zeros(2)
        e[k] = h
        H[:, k] = -(force_on(sim, b, x0 + e) - force_on(sim, b, x0 - e)) / (2 * h)
    return 0.5 * (H + H.T)


def main():
    sel = {s["tag"]: s for s in json.load(open(os.path.join(DATA, "derived", "selection.json")))["E3"]["snapshots"]}
    rows = []
    for k, tag in enumerate(TAGS):
        s = sel[tag]
        snap = pickle.load(open(os.path.join(ROOT, s["snap"]), "rb"))
        b = s["blocker"]
        tau = float(snap["state"].taus[b])
        sigma = sigma_for(s["dU"] / BETA, 0.01, tau)
        sim0 = restore(snap, "C1", flags=dict(CF))
        H = hessian(sim0, b)
        lam, vec = np.linalg.eigh(H)
        for dt in DTS:
            sim = restore(snap, "C1", flags={**CF, "w2_noise": "per_step"}, noise=sigma, noise_seed=31000 + k, dt=dt)
            st = sim.state
            vs = []
            escaped = False
            for n in range(int(round(T_RUN / dt))):
                sim.step()
                st = sim.state
                if not st.active[b] or st.positions[b, 0] >= 10.0:
                    escaped = True
                    break
                if (n + 1) * dt > BURN and st.positions[b, 0] < 9.95:
                    vs.append(st.velocities[b].copy())
            V = np.array(vs)
            Vp = V @ vec                                   # components along the Hessian eigen-directions
            a = 1.0 - dt / tau
            free = sigma ** 2 / (1 - a * a)
            harm = [2 * sigma ** 2 / ((1 - a) * (2 + 2 * a - (l / M) * dt * dt)) for l in lam]
            var_xy = V.var(0)
            var_eig = Vp.var(0)
            r = {"tag": tag, "blocker": b, "dU": s["dU"], "tau": tau, "sigma": sigma, "dt": dt,
                 "samples": len(V), "escaped": escaped, "kT_formula": kT_eff(sigma, dt, tau),
                 "kT_measured": float(M * var_xy.mean()), "ratio_measured_formula": float(var_xy.mean() / free),
                 "hessian_eig_N_per_m": lam.tolist(), "w_dt": [float(np.sqrt(max(l, 0) / M) * dt) for l in lam],
                 "var_eig_measured": var_eig.tolist(), "var_eig_harmonic": harm,
                 "ratio_eig_measured_harmonic": (var_eig / np.array(harm)).tolist(),
                 "ratio_harmonic_free": [h_ / free for h_ in harm],
                 "rel_se": float(np.sqrt(2.0 / max(len(V) * dt / tau, 1)))}
            rows.append(r)
            print(f"{tag} dt={dt} n={len(V)} esc={escaped} measured/formula={r['ratio_measured_formula']:.3f} "
                  f"eig measured/harmonic={[round(x, 3) for x in r['ratio_eig_measured_harmonic']]} "
                  f"harmonic/free={[round(x, 4) for x in r['ratio_harmonic_free']]} w*dt={[round(x, 3) for x in r['w_dt']]}",
                  flush=True)
    rat = np.array([r["ratio_measured_formula"] for r in rows])
    out = {"rows": rows, "ratio_measured_formula_mean": float(rat.mean()),
           "ratio_measured_formula_range": [float(rat.min()), float(rat.max())]}
    # stored-moment check over all E3/E4 escape runs (per cell, cells with >= 200 trapped samples)
    cells = []
    for f, key in ((os.path.join(DATA, "E3", "e3_dt.jsonl"), lambda r: (r["job_id"].split("|")[0], r["mode"], r["dt"])),
                   (os.path.join(DATA, "E4", "e4_escape.jsonl"), lambda r: (r["snap"], r["cond"], r["beta_ref"]))):
        acc, kt = {}, {}
        for ln in open(f):
            r = json.loads(ln)
            if r.get("mode") == "C3_rvo2":
                continue
            kk = key(r)
            acc[kk] = acc.get(kk, 0) + np.array(r["v_moments"])
            kt[kk] = r["kT_eff"] / r["m"]
        for kk, s in acc.items():
            if s[0] >= 200:
                v = 0.5 * ((s[3] / s[0] - (s[1] / s[0]) ** 2) + (s[4] / s[0] - (s[2] / s[0]) ** 2))
                cells.append(v / kt[kk])
    c = np.array(cells)
    out["stored_moments"] = {"cells": len(c), "median": float(np.median(c)), "iqr": np.percentile(c, [25, 75]).tolist(),
                             "min": float(c.min()), "max": float(c.max())}
    json.dump(out, open(OUT, "w"), indent=1)
    print("measured/formula mean", out["ratio_measured_formula_mean"], out["ratio_measured_formula_range"])
    print("stored moments", out["stored_moments"])


if __name__ == "__main__":
    main()
