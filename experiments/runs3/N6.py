"""run-N6: the loss of the pair minimum under a lateral bias, by continuation, and quenches just past it.

static  For each E7b pair snapshot (experiments/E7b/e7b_pairs.py, 46) and each bias sign s = +1, -1: the
        rest-state equilibria of the code's C1 force on the two members (v = 0, density frozen at the
        snapshot, the snapshot's params = CF union {B_w: 0.04}, plus w2_noise = lateral_bias, w2_bias_b = s b;
        the force of experiments/lib/pairlib.relax) are followed in b from the snapshot (b = 0) by
        pseudo-arclength continuation (Newton corrector, central-difference Jacobian, h = 1e-7 m) until
        the branch turns back (the fold, b_f). b_f is refined on the extended system F = 0, J v = 0,
        |v| = 1. Then at b = b_f (1 - delta), delta in {0.3, 0.1, 0.03, 0.01, 0.003, 0.001}, the minimum
        and the saddle are solved by Newton from X_f -/+ c sqrt(delta) v and recorded: mu1 (smallest
        eigenvalue of -J, the softest stiffness; -J is the Hessian where the force is a gradient), the
        minimum-saddle distance, and the work W = -int F . dX on the straight segment from the minimum to
        the saddle (16-point Gauss-Legendre). Normal form of a saddle-node: mu1 and the distance scale as
        delta^(1/2), W as delta^(3/2). The bisection threshold b*_s of experiments/E7b/fold_threshold.py
        is recorded beside b_f.
        Output: data/N6/n6_static.jsonl (job_id "<tag>|<sign>"), resumable.
quench  C1 + lateral bias s b_f (1 + eps), eps in {0.01, 0.03, 0.1, 0.3}, from the snapshot, unperturbed,
        dt 0.01 s, flags CF union {B_w: 0.04}, 300 s, no stationary stop (passage near the fold is slow);
        runner experiments/E7b/e7b_quench.run (unchanged). Where the continuation failed, b_f is the
        bisection b*_s and the row says so. Passage time = first exit; normal form: ~ eps^(-1/2).
        Output: data/N6/n6_quench.jsonl (job_id "<tag>|<sign>|eps<eps>"), resumable.
Usage: N6.py static | quench  [qargs options]
"""
import copy
import json
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3 import CF, DATA, load_runs, out_dir, qargs, run_jobs  # noqa: E402
import numpy as np  # noqa: E402
import pairlib  # noqa: E402
from e7b_pairs import pairs  # noqa: E402
import e7b_quench  # noqa: E402

D = out_dir("N6")
OUT_S = os.path.join(D, "n6_static.jsonl")
OUT_Q = os.path.join(D, "n6_quench.jsonl")
FOLD = os.path.join(DATA, "E7b_bstar", "fold_threshold.jsonl")
DELTAS = (0.3, 0.1, 0.03, 0.01, 0.003, 0.001)
EPS = (0.01, 0.03, 0.1, 0.3)
H = 1e-7
BSCALE = 10.0      # b is continued as b' = BSCALE b so that its steps are comparable to metres
T_Q = 300.0


class Field:
    """Rest-state C1 force on the members (pairlib.relax), as a function of (X, b)."""

    def __init__(self, snap, sign):
        self.st = copy.deepcopy(snap["state"])
        self.st.velocities[:] = 0
        self.ids = pairlib.residual_ids(snap)
        self.k = np.array(self.ids)
        self.sign = sign
        self.base = dict(snap["params"])
        self.world, _ = pairlib.BottleneckScenario(1, snap["width"]).build(seed=0)
        self.dens = np.zeros(self.st.n)
        self.dens[self.ids] = pairlib.snapshot_rho(snap, self.ids)
        self.nl = [[] for _ in range(self.st.n)]
        for i in self.ids:
            self.nl[i] = [j for j in self.ids if j != i]
        self._hm = {}
        self.n_eval = 0

    def model(self, b):
        key = round(b, 15)
        if key not in self._hm:
            if len(self._hm) > 64:
                self._hm.clear()
            p = dict(self.base)
            if b != 0.0:
                p.update({"w2_noise": "lateral_bias", "w2_bias_b": self.sign * b})
            self._hm[key] = pairlib.HybridSteeringModel(pairlib.get_config("C1"), p)
        return self._hm[key]

    def F(self, X, b):
        self.n_eval += 1
        self.st.positions[self.k] = X.reshape(-1, 2)
        return self.model(b).compute_forces(self.st, self.nl, self.world.walls, self.dens)[self.k].ravel()

    def J(self, X, b):
        n = len(X)
        M = np.zeros((n, n))
        for a in range(n):
            e = np.zeros(n); e[a] = H
            M[:, a] = (self.F(X + e, b) - self.F(X - e, b)) / (2 * H)
        return M

    def Fb(self, X, b):
        hb = 1e-8
        return (self.F(X, b + hb) - self.F(X, max(b - hb, 0.0))) / (b + hb - max(b - hb, 0.0))


def newton_X(f, X, b, tol=1e-9, it=30):
    for _ in range(it):
        Fx = f.F(X, b)
        if np.abs(Fx).max() < tol:
            return X, True
        dX = np.linalg.lstsq(f.J(X, b), -Fx, rcond=None)[0]
        X = X + dX
        if np.abs(dX).max() > 0.2:
            return X, False
    return X, np.abs(f.F(X, b)).max() < 1e-6


def soft(f, X, b):
    ev = np.linalg.eigvals(-f.J(X, b))
    i = np.argmin(ev.real)
    return float(ev.real[i]), float(abs(ev.imag[i]))


def continue_branch(f, X0, ds=2e-4, max_steps=4000):
    """Pseudo-arclength in Y = (X, b'), b' = BSCALE b. Returns branch points and the index where b' peaks."""
    n = len(X0)
    Y = np.append(X0, 0.0)
    def tangent(Y, t_prev):
        X, b = Y[:n], Y[n] / BSCALE
        A = np.column_stack([f.J(X, b), f.Fb(X, b) / BSCALE])
        t = np.linalg.svd(A)[2][-1]
        if t_prev is not None and t @ t_prev < 0:
            t = -t
        return t
    t = tangent(Y, None)
    if t[n] < 0:
        t = -t
    pts = [Y.copy()]
    for _ in range(max_steps):
        Yp = Y + ds * t
        Z = Yp.copy()
        ok = False
        for _ in range(20):
            X, b = Z[:n], Z[n] / BSCALE
            if b < 0:
                break
            G = np.append(f.F(X, b), t @ (Z - Yp))
            if np.abs(G[:n]).max() < 1e-9:
                ok = True
                break
            A = np.vstack([np.column_stack([f.J(X, b), f.Fb(X, b) / BSCALE]), t])
            Z = Z - np.linalg.solve(A, G)
        if not ok:
            ds *= 0.5
            if ds < 1e-8:
                return pts, None, "corrector failed"
            continue
        t_new = tangent(Z, t)
        Y, t = Z, t_new
        pts.append(Y.copy())
        if t[n] < 0:                    # b' started to decrease: past the fold
            return pts, len(pts) - 2, "ok"
        ds = min(ds * 1.3, 5e-3)
        if Y[n] / BSCALE > 0.5:
            return pts, None, "no fold below b = 0.5"
    return pts, None, "max steps"


def refine_fold(f, X, b, v):
    """Newton on F(X, b) = 0, J(X, b) v = 0, v . v0 = 1 (unknowns X, v, b)."""
    n = len(X)
    v0 = v / np.linalg.norm(v)
    Z = np.concatenate([X, v0, [b]])
    def G(Z):
        X, v, b = Z[:n], Z[n:2 * n], Z[2 * n]
        return np.concatenate([f.F(X, b), f.J(X, b) @ v, [v0 @ v - 1.0]])
    for _ in range(30):
        g = G(Z)
        if np.abs(g).max() < 1e-8:
            break
        m = len(Z)
        A = np.zeros((m, m))
        for a in range(m):
            e = np.zeros(m); e[a] = 1e-7
            A[:, a] = (G(Z + e) - G(Z - e)) / 2e-7
        Z = Z - np.linalg.lstsq(A, g, rcond=None)[0]
    X, v, b = Z[:n], Z[n:2 * n], Z[2 * n]
    return X, v / np.linalg.norm(v), float(b), float(np.abs(G(Z)).max())


def work(f, Xa, Xb, b):
    xg, wg = np.polynomial.legendre.leggauss(16)
    d = Xb - Xa
    s = 0.0
    for x, w in zip(xg, wg):
        u = 0.5 * (x + 1)
        s += 0.5 * w * f.F(Xa + u * d, b) @ d
    return float(-s)


def geometry(f, X):
    """Per member: walls within 0.5 m with distance d - r and the unclipped projection parameter t of the
    closest point (0 < t < 1: facing the segment; otherwise its end point); pair gap d_ij - r_i - r_j."""
    P = X.reshape(-1, 2)
    r = f.st.radii[f.k]
    out = []
    for m, p in enumerate(P):
        near = []
        for w, wall in enumerate(f.world.walls):
            ab = wall.end - wall.start
            t = float((p - wall.start) @ ab / max(ab @ ab, 1e-12))
            q = wall.start + min(max(t, 0.0), 1.0) * ab
            d = float(np.linalg.norm(p - q))
            if d < 0.5:
                near.append({"wall": w, "gap": d - float(r[m]), "t": t})
        out.append(near)
    gap = float(np.linalg.norm(P[1] - P[0]) - r[0] - r[1]) if len(P) == 2 else None
    return {"walls": out, "pair_gap": gap}


def static_run(job):
    w0 = time.perf_counter()
    snap = pickle.load(open(job["snap"], "rb"))
    f = Field(snap, job["sign"])
    X0 = snap["state"].positions[f.k].ravel().copy()
    X0, ok0 = newton_X(f, X0, 0.0)
    row = {k: v for k, v in job.items() if k != "snap"}
    row.update({"members": f.ids, "start_converged": bool(ok0)})
    pts, i, status = continue_branch(f, X0) if ok0 else ([], None, "no equilibrium at b = 0")
    row.update({"branch_points": len(pts), "status": status})
    if i is not None:
        n = len(X0)
        P = np.array(pts)
        j = int(np.argmax(P[:, n]))
        Xf, bf = P[j, :n], P[j, n] / BSCALE
        ev, V = np.linalg.eig(f.J(Xf, bf))
        v = np.real(V[:, np.argmin(np.abs(ev))])
        Xf, v, bf, res = refine_fold(f, Xf, bf, v)
        # orient v from the minimum branch to the saddle branch and set the sqrt-law coefficient
        lo = P[max(j - 3, 0)]
        cX = (lo[:n] - Xf) @ v
        if cX > 0:
            v = -v
            cX = -cX
        c = abs(cX) / np.sqrt(max(bf - lo[n] / BSCALE, 1e-15))
        rows = []
        for dl in DELTAS:
            b = bf * (1 - dl)
            Xm, okm = newton_X(f, Xf - c * np.sqrt(dl * bf) * v, b)
            Xs, oks = newton_X(f, Xf + c * np.sqrt(dl * bf) * v, b)
            r = {"delta": dl, "b": b, "converged": bool(okm and oks)}
            if okm and oks:
                mm, mi = soft(f, Xm, b)
                ms, _ = soft(f, Xs, b)
                dist = float(np.linalg.norm(Xs - Xm))
                Jm, Js = f.J(Xm, b), f.J(Xs, b)
                r.update({"mu1_min": mm, "mu1_min_imag": mi, "mu1_saddle": ms, "dist": dist,
                          "distinct": dist > 1e-6, "W": work(f, Xm, Xs, b),
                          "eig_min": sorted(np.linalg.eigvals(-Jm).real.tolist()),
                          "eig_saddle": sorted(np.linalg.eigvals(-Js).real.tolist()),
                          "jac_jump": float(np.linalg.norm(Jm - Js) / max(np.linalg.norm(Jm), 1e-12))})
                if dl == DELTAS[-1]:
                    r.update({"geom_min": geometry(f, Xm), "geom_saddle": geometry(f, Xs)})
            rows.append(r)
        row.update({"geom_fold": geometry(f, Xf), "b_f": bf, "fold_residual": res, "fold_vector": v.tolist(), "X_f": Xf.tolist(),
                    "sqrt_coeff": float(c), "scan": rows})
    row.update({"b_star_bisection": job.get("b_star_bisection"), "n_force_evals": f.n_eval,
                "wall_s": time.perf_counter() - w0})
    return row


def bisection():
    return {r["job_id"]: r for r in load_runs(FOLD)} if os.path.exists(FOLD) else {}


def static_jobs():
    B = bisection()
    J = []
    for p in pairs():
        for s in (1, -1):
            jid = f"{p['tag']}|{s:+d}"
            J.append({"job_id": jid, "tag": p["tag"], "snap": p["snap"], "sign": s,
                      "b_star_bisection": B.get(jid, {}).get("b_star")})
    return J


def quench_jobs(static_path=OUT_S):
    S = {r["job_id"]: r for r in load_runs(static_path)} if os.path.exists(static_path) else {}
    base = {**CF, "B_w": 0.04}
    J = []
    for j in static_jobs():
        r = S.get(j["job_id"], {})
        bf, src = r.get("b_f"), "continuation"
        if bf is None:
            bf, src = j["b_star_bisection"], "bisection"
        if bf is None:
            continue
        for e in EPS:
            b = j["sign"] * bf * (1 + e)
            J.append({"job_id": f"{j['job_id']}|eps{e:g}", "tag": j["tag"], "snap": j["snap"], "sign": j["sign"],
                      "eps": e, "b_f": bf, "b_f_source": src, "arm": f"fold_eps{e:g}", "config": "C1",
                      "flags": {**base, "w2_noise": "lateral_bias", "w2_bias_b": b}, "deterministic": False,
                      "perturb": None, "t_q": T_Q})
    return J


def main(argv=None):
    a = qargs.parse(argv)
    what = a.rest[0]
    if what == "static":
        return run_jobs(qargs.select(static_jobs(), a), static_run, a.out or OUT_S, workers=a.workers, log_every=4)
    sp = a.rest[a.rest.index("--static") + 1] if "--static" in a.rest else OUT_S
    return run_jobs(qargs.select(quench_jobs(sp), a), e7b_quench.run, a.out or OUT_Q, workers=a.workers,
                    log_every=20)


if __name__ == "__main__":
    print("wall", main())
