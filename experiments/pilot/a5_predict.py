"""W2b A5 static predictions for the pair class. For each pair snapshot and deterministic
arm, overdamped relaxation of the code's rest-state force (v = 0, density frozen at the
snapshot value, other agents inactive): dx/dt = (tau_i / m_i) F_i(x), Euler step 0.01 s,
up to 120 s. Predicted 'freed' if any residual agent reaches x > 10.3 m; 'held' if max |F| < 0.05 N.
Arms: C1; frozen_plus (= drive_only at rest: C3 with w2_orca_split=drive_only);
frozen_minus; lateral_bias b (C1, w2_noise=lateral_bias). Full C3 is not predicted (its LP
depends on v). Output: wave2b/data/a5_predict.json"""
import copy, glob, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2blib import *  # noqa
from sim.steering.hybrid import HybridSteeringModel
from sim.experiments.configs import get_config

ARMS = {"C1": ("C1", {}), "frozen_plus": ("C3", {"w2_orca_split": "frozen_mean"}),
        "frozen_minus": ("C3", {"w2_orca_split": "frozen_mean", "w2_orca_transform": "reverse_parallel"})}
for b in (0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5):
    ARMS[f"bias{b}"] = ("C1", {"w2_noise": "lateral_bias", "w2_bias_b": b})


def relax(snap, cfg, flags, T=120.0, h=0.01):
    st = copy.deepcopy(snap["state"])
    st.velocities[:] = 0
    ids = [int(i) for i in st.active_indices]
    params = {k: v for k, v in snap["params"].items()}
    params.update({"w2_numerics": "fixed", "B_w": 0.04, **flags})
    world, _ = BottleneckScenario(1, snap["width"]).build(seed=0)
    hm = HybridSteeringModel(get_config(cfg), params)
    P = st.positions
    act = st.active_indices
    dens = np.zeros(st.n)
    for i in ids:
        dens[i] = ((np.linalg.norm(P[act] - P[i], axis=1) < 3.0).sum() - 1) / (9 * np.pi)
    k = np.array(ids)
    gain = (st.taus[k] / st.masses[k])[:, None]
    t = 0.0
    while t < T:
        nl = [[] for _ in range(st.n)]
        for i in ids:
            if st.active[i]:
                nl[i] = [j for j in ids if j != i and st.active[j]]
        F = hm.compute_forces(st, nl, world.walls, dens)[k]
        F[~st.active[k]] = 0
        if np.abs(F).max() < 0.05:
            return {"pred_freed": False, "t": t, "pos": st.positions[k].tolist()}
        st.positions[k] += h * gain * F
        t += h
        out = [i for i in ids if st.active[i] and st.positions[i, 0] > 10.3]
        if out:
            return {"pred_freed": True, "t": t, "first": out[0], "first_is_lower": out[0] == min(ids, key=lambda i: snap["state"].positions[i, 1])}
    return {"pred_freed": None, "t": t, "pos": st.positions[k].tolist(), "maxF": float(np.abs(F).max())}


if __name__ == "__main__":
    snaps = [l.strip() for l in open(os.path.join(DATA2B, "a4_selected_snaps.txt")) if l.strip()]
    out = {}
    for s in snaps:
        snap = pickle.load(open(s, "rb"))
        out[os.path.basename(s)] = {a: relax(snap, c, f) for a, (c, f) in ARMS.items()}
        print(os.path.basename(s), {a: (r["pred_freed"], round(r["t"], 1)) for a, r in out[os.path.basename(s)].items()}, flush=True)
    json.dump(out, open(os.path.join(DATA2B, "a5_predict.json"), "w"), indent=1)
