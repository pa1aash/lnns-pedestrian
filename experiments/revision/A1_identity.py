"""A1: numerical check of the rest-drive identity of force-coupled ORCA.

With no binding constraint ORCA returns v_pref = v0 e, so the drive part of force-coupled ORCA is
w_o m (v0 e - v)/tau_orca and

    F_des + w_o F_drive = m (v_eff/tau + w_o v0/tau_orca) e - m (1/tau + w_o/tau_orca) v.

For w_o = 1 this is the SFM drive m (v_target e - v)/tau' with
    tau' = tau tau_orca / (tau + tau_orca),   v_target = (v_eff/tau + v0/tau_orca) tau'  (= v0 when v_eff = v0).

Check 1 (forces): on every E2 snapshot (34 lone keystones, 26 second traps) compare the total force of
C3 with w2_orca_split = drive_only against C1 with tau -> tau' and v0 -> v0' (two substitutions:
"tau" keeps v0' = v0; "exact" sets v0' so that W(rho) v0' / tau' equals the C3 drive coefficient at the
snapshot densities, W the Weidmann factor), at v = 0 and at random velocities (|v| ~ 0.3 m/s).
Check 2 (dynamics): quench every snapshot under C1 with each substitution exactly as E2's deterministic
arms (CF flags, dt = 0.01 s, 120 s, stationary stop |v| < 1e-3 m/s for 10 s; unperturbed run) and compare
blocker freed / exit time paired with E2's drive_only arm (data/E2/e2_quench.jsonl, job "<tag>|drive_only|u").

Output: data/revision/A1/a1_quench.jsonl, data/derived/rev_A1.json.
"""
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402
from revlib import CF, DATA, np, run_jobs  # noqa: E402
from runlib import quench  # noqa: E402
from w2lib import restore, weidmann_factor  # noqa: E402

T_ORCA = 0.5
OUT = os.path.join(revlib.data_dir("A1"), "a1_quench.jsonl")


def snapshots():
    sel = json.load(open(os.path.join(DATA, "derived", "selection.json")))
    return [(s["tag"], os.path.join(revlib.ROOT, s["snap"]), s["blocker"], s["class"]) for s in sel["E2"]["snapshots"]]


def densities(sim):
    st = sim.state
    a = st.active_indices
    rho = np.zeros(st.n)
    R = 3.0
    for i in a:
        d = np.linalg.norm(st.positions[a] - st.positions[i], axis=1)
        rho[i] = (np.sum(d <= R) - 1) / (np.pi * R * R)
    return rho


def forces(sim):
    """Total force as in Simulation.step (KDTree neighbours within neighbor_radius, grid-count density)."""
    from scipy.spatial import KDTree
    st = sim.state
    a = st.active_indices
    tree = KDTree(st.positions[a])
    nl = [[] for _ in range(st.n)]
    for li, nb in enumerate(tree.query_ball_point(st.positions[a], r=sim.params["neighbor_radius"])):
        nl[a[li]] = [a[j] for j in nb if a[j] != a[li]]
    R = sim.params["neighbor_radius"]
    dens = np.array([len(n) / (np.pi * R * R) for n in nl], dtype=float)
    return sim.steering.compute_forces(st, nl, sim.world.walls, dens)


def substitute(st, kind, rho=None):
    """In-place tau -> tau', v0 -> v0' on an AgentState."""
    tau, v0 = st.taus.copy(), st.desired_speeds.copy()
    tp = tau * T_ORCA / (tau + T_ORCA)
    st.taus[:] = tp
    if kind == "exact":
        W = np.array([weidmann_factor(r) for r in rho])
        w_o = 1.0 - 1.0 / (1.0 + np.exp(-2.0 * (rho - 4.0)))
        st.desired_speeds[:] = (W * v0 / tau + w_o * v0 / T_ORCA) * tp / W
    return tau, v0


def force_check():
    rows = []
    rng = np.random.default_rng(1)
    for tag, snap, blk, cls in snapshots():
        S = pickle.load(open(snap, "rb"))
        for vkind in ("rest", "moving"):
            vel = None
            for kind in ("tau", "exact"):
                s3 = restore(S, "C3", flags={**CF, "w2_orca_split": "drive_only"})
                s1 = restore(S, "C1", flags=dict(CF))
                a = s3.state.active_indices
                if vkind == "moving":
                    if vel is None:
                        vel = rng.normal(0, 0.3 / np.sqrt(2), (len(a), 2))
                    s3.state.velocities[a] = vel
                    s1.state.velocities[a] = vel
                else:
                    s3.state.velocities[a] = 0.0
                    s1.state.velocities[a] = 0.0
                substitute(s1.state, kind, densities(s1))
                F3, F1 = forces(s3), forces(s1)
                F3, F1 = np.asarray(F3)[a], np.asarray(F1)[a]
                rows.append({"tag": tag, "class": cls, "v": vkind, "kind": kind,
                             "max_abs_dF": float(np.abs(F3 - F1).max()),
                             "max_rel_dF": float((np.linalg.norm(F3 - F1, axis=1) / np.maximum(np.linalg.norm(F3, axis=1), 1e-9)).max()),
                             "max_F": float(np.linalg.norm(F3, axis=1).max())})
    return rows


def run_q(job):
    S = pickle.load(open(job["snap"], "rb"))
    tmp = job["snap"] + f".a1_{job['kind']}_{os.getpid()}.pkl"
    st = S["state"]
    sim = restore(S, "C1", flags=dict(CF))
    substitute(st, job["kind"], densities(sim))
    with open(tmp, "wb") as f:
        pickle.dump(S, f)
    try:
        r = quench(dict(job, snap=tmp))
    finally:
        os.remove(tmp)
    r["snap"] = os.path.basename(job["snap"])
    t = r["exits"].get(str(job["blocker"]), r["exits"].get(job["blocker"]))
    r["blocker_freed"] = t is not None and t <= 120.0 + 1e-9
    r["blocker_exit_t"] = t
    return r


def jobs():
    return [{"job_id": f"{tag}|sfm_tau_{kind}|u", "snap": snap, "kind": kind, "config": "C1", "flags": dict(CF),
             "deterministic": True, "perturb": None, "t_q": 120.0, "blocker": blk, "stratum": cls}
            for tag, snap, blk, cls in snapshots() for kind in ("tau", "exact")]


def analyse(fc):
    e2 = {}
    blockers = {tag: blk for tag, _, blk, _ in snapshots()}
    with open(os.path.join(DATA, "E2", "e2_quench.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r["job_id"].endswith("|drive_only|u"):
                tag = r["job_id"].split("|")[0]
                blk = blockers[tag]
                t = r["exits"].get(str(blk), r["exits"].get(blk))
                r["blocker_freed"] = t is not None and t <= 120.0 + 1e-9
                r["blocker_exit_t"] = t
                e2[tag] = r
    q = [json.loads(l) for l in open(OUT)]
    out = {"doc": __doc__, "force_check": {}, "quench": {}}
    for kind in ("tau", "exact"):
        for v in ("rest", "moving"):
            R = [r for r in fc if r["kind"] == kind and r["v"] == v]
            out["force_check"][f"{kind}_{v}"] = {"max_abs_dF_N": max(r["max_abs_dF"] for r in R),
                                                 "max_rel_dF": max(r["max_rel_dF"] for r in R), "n": len(R)}
        for cls, name in (("lone_keystone", "lone"), ("lone_keystone_second_trap", "second"), (None, "all")):
            Q = [r for r in q if r["kind"] == kind and (cls is None or r["stratum"] == cls)]
            both = sub_only = drive_only = neither = 0
            dts = []
            for r in Q:
                d = e2[r["job_id"].split("|")[0]]
                a, b = bool(r["blocker_freed"]), bool(d["blocker_freed"])
                both += a and b
                sub_only += a and not b
                drive_only += b and not a
                neither += not a and not b
                if a and b:
                    dts.append(abs(r["blocker_exit_t"] - d["blocker_exit_t"]))
            out["quench"][f"{kind}_{name}"] = {
                "n": len(Q), "freed_sub": both + sub_only, "freed_drive": both + drive_only,
                "both": both, "sub_only": sub_only, "drive_only": drive_only, "neither": neither,
                "mcnemar_p": revlib.mcnemar_exact(sub_only, drive_only),
                "max_abs_dt_exit_s": max(dts) if dts else None,
                "median_abs_dt_exit_s": float(np.median(dts)) if dts else None}
    out["tau_prime_range_s"] = None
    taus = []
    for _, snap, _, _ in snapshots():
        st = pickle.load(open(snap, "rb"))["state"]
        taus += list(st.taus[st.active_indices])
    taus = np.array(taus)
    tp = taus * T_ORCA / (taus + T_ORCA)
    out["tau_range_s"] = [float(taus.min()), float(taus.max())]
    out["tau_prime_range_s"] = [float(tp.min()), float(tp.max())]
    out["drive_ratio_range"] = [float((tp.min() and (taus / tp).min())), float((taus / tp).max())]
    revlib.out_json("A1", out)
    print(json.dumps({k: out[k] for k in ("force_check", "quench")}, indent=1))


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "all"
    if a in ("run", "all"):
        run_jobs(jobs(), run_q, OUT, workers=int(os.environ.get("A1_WORKERS", "2")), log_every=10)
    if a in ("analyse", "all"):
        analyse(force_check())
