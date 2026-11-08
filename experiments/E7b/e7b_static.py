"""E7b_static: rest-state stability and static fold prediction for every qualifying pair snapshot
(experiments/E7b/e7b_pairs.py; corrected-forward, C1, B_w = 0.04 all walls).

Per snapshot (ports of experiments/pilot/a3_pair_stability.py and a5_predict.py; helpers in
experiments/lib/pairlib.py):
  field check   max |F_code + grad U| over the two members (code: HybridSteeringModel C1 at v = 0, density
                frozen at the snapshot value; U: pairlib.PairField at the snapshot's A_w, B_w);
  Hessian       central second differences of U, h = 1e-4 m, in the 4 coordinates (lower-y member first:
                x_lo, y_lo, x_hi, y_hi); eigenvalues (N/m, ascending) and eigenvectors (columns);
                lambda1 = smallest eigenvalue; softest-mode type (common_lateral / opposed_lateral /
                longitudinal, a3 rule); force parts (drive, wall, pair) at the snapshot;
  fold          overdamped relaxation of the code's rest-state force (a5) under C1 + lateral bias
                b in {+-0.01, +-0.02, +-0.03, 0.05, 0.1}: freed (a member reaches x > 10.3 m), held
                (max |F| < 0.05 N) or undecided at 120 s; first member out and its side. Reference arms
                (no extra cost): C1 (b = 0), frozen_plus, frozen_minus.
Bias sign: w2_bias_b > 0 tilts the desired direction toward +y (hybrid.py: e_perp = (-e_y, e_x)).
Output: data/E7b/e7b_static.jsonl (job_id = snapshot tag), resumable.
"""
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
sys.path.insert(0, HERE)
from e1lib import DATA, run_jobs  # noqa: E402
import numpy as np  # noqa: E402
import pairlib  # noqa: E402
import qargs  # noqa: E402
from e7b_pairs import pairs  # noqa: E402

OUT = os.path.join(DATA, "E7b", "e7b_static.jsonl")
BIAS = (-0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.05, 0.1)
ARMS = {"C1": ("C1", {}),
        "frozen_plus": ("C3", {"w2_orca_split": "frozen_mean"}),
        "frozen_minus": ("C3", {"w2_orca_split": "frozen_mean", "w2_orca_transform": "reverse_parallel"})}
for _b in BIAS:
    ARMS[f"bias{_b:g}"] = ("C1", {"w2_noise": "lateral_bias", "w2_bias_b": _b})


def run(job):
    w0 = time.perf_counter()
    snap = pickle.load(open(job["snap"], "rb"))
    st = snap["state"]
    ids = pairlib.residual_ids(snap)
    f = pairlib.PairField(snap, ids)
    X = st.positions[ids].ravel()
    Fc = pairlib.code_force(snap, ids, f)
    gU = f.grad(X)
    H = f.hess(X, h=1e-4)
    ev, V = np.linalg.eigh(H)
    v0 = V[:, 0] * np.sign(V[np.argmax(np.abs(V[:, 0])), 0])
    P = X.reshape(-1, 2)
    d = float(np.linalg.norm(P[1] - P[0]))
    lat = abs(v0[1]) + abs(v0[3]) > abs(v0[0]) + abs(v0[2])
    soft = ("common_lateral" if lat and v0[1] * v0[3] > 0 else "opposed_lateral" if lat else "longitudinal")
    dw, _ = pairlib.agents_to_walls(P, f.world.walls)
    row = {"job_id": job["job_id"], "snap": os.path.basename(job["snap"]), "seed": job["seed"], "ids": ids,
           "side": {str(i): ("lower" if st.positions[i, 1] < 5.0 else "upper") for i in ids},
           "pos": P.tolist(), "radii": f.r.tolist(), "v0": f.v0.tolist(), "tau": f.tau.tolist(),
           "rho_frozen": f.rho.tolist(), "drive_c_N": f.c.tolist(), "A_w": f.A_w, "B_w": f.B_w,
           "max_speed": float(np.linalg.norm(st.velocities[ids], axis=1).max()),
           "check_max_abs_F_plus_gradU_N": float(np.max(np.abs(Fc.ravel() + gU))),
           "force_parts_N": {nm: (-f.grad(X, which=k)).reshape(-1, 2).tolist()
                             for k, nm in enumerate(("drive", "wall", "pair"))},
           "hess": H.tolist(), "hess_h_m": 1e-4, "eig_N_per_m": ev.tolist(), "eigvec_columns": V.tolist(),
           "lambda1": float(ev[0]), "softest_vec": v0.tolist(), "softest_type": soft, "strict_min": bool(ev[0] > 0),
           "pair_dist_m": d, "pair_gap_m": d - float(f.r.sum()),
           "wall_gap_m": (dw.min(axis=1) - f.r).tolist(),
           "asym_axis_dist_m": float(abs(abs(P[0, 1] - 5) - abs(P[1, 1] - 5))),
           "asym_x_m": float(abs(P[0, 0] - P[1, 0])), "asym_drive_N": float(abs(f.c[0] - f.c[1]))}
    row["fold"] = {}
    for arm, (cfg, fl) in ARMS.items():
        r = pairlib.relax(snap, cfg, fl, T=job.get("t_q", 120.0))
        row["fold"][arm] = dict(r, b=fl.get("w2_bias_b"))
    row["wall_s"] = time.perf_counter() - w0
    return row


def jobs():
    return [{"job_id": p["tag"], "snap": p["snap"], "seed": p["seed"], "t_q": 120.0} for p in pairs()]


def main(argv=None):
    a = qargs.parse(argv)
    out = a.out or OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    J = qargs.select(jobs(), a)
    print("E7b_static snapshots", len(J), flush=True)
    return run_jobs(J, run, out, workers=a.workers, log_every=5)


if __name__ == "__main__":
    print("wall", main())
