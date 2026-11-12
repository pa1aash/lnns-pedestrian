"""A8: protocol facts (seeds, deadlock library, snapshot selection, string-method gate, ORCA settings, the
deterministic resolver's escape rate in the time-step probe, the 360 / 276 run counts), each re-derived from
the stored data or read from the code at run time.

Inputs (read only): data/E1/E1_runs.jsonl, data/E1/library/, data/derived/E1_keystone.json,
data/derived/selection.json, data/BAR/barriers_gated.json, data/BAR/gate.jsonl, data/E7b/e7b_static.jsonl,
data/E7b/e7b_barrier.jsonl, data/E3/e3_dt.jsonl, data/derived/E3_analysis.json, figures/data/fig5.json,
every run JSONL that carries a run seed, noise seed or perturbation seed (list SEED_FILES), and the code
(experiments/BAR/{bar,gate}.py constants by import; code/sim/steering/orca*.py, hybrid.py, simulation.py by
regular expression for file:line, and by building one C3 simulation of each solver for the values in force).
Method:
  1. Seeds: per file, the set of run seeds, noise seeds and perturbation seeds, written as inclusive ranges.
     Structured noise seeds base + kmult k + extra + rep are decomposed per row; the decomposition must give
     one k per snapshot, distinct over snapshots, and (E2, E3, E4) k = the snapshot's index in its selection
     list. Pairwise intersections of the noise-seed sets of different experiments are listed.
  2. Deadlocks: E1b run outcomes (complete / deadlock / capped), pickles on disk, keystone classes.
  3. Selection: the PCG64(2026) draw of the 26 second traps, the E3 / E4 qualifying sets and evenly spaced
     ranks, the 12 pair-barrier snapshots, each re-derived and asserted equal to the stored selection.
  4. String method: settings from bar.py / gate.py, gate outcome per condition, the 4 rejected strings.
  5. ORCA: parameters in force in a C3 simulation (RVO2 and legacy solvers), neighbour search, walls.
  6. Escape rate of force-coupled ORCA (RVO2) in E3: one deterministic run per (snapshot, dt), rate 1 / t_esc,
     ell = ln t_esc(0.02) / t_esc(0.005); recomputed from e3_dt.jsonl and checked against E3_analysis.json.
  7. Run counts: velocity-coupling quenches per solver (lone, pair), E2 / E7b deterministic runs per arm,
     B5 snapshot-radius cases.
Output: data/derived/rev2_A8.json. Deterministic (no random numbers except the re-derived PCG64(2026) draw).
"""
import glob
import inspect
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import CF, DATA, DERIVED, ROOT, np, out_json  # noqa: E402

EXP = os.path.join(ROOT, "experiments")
sys.path.insert(0, os.path.join(EXP, "lib"))
sys.path.insert(0, os.path.join(EXP, "BAR"))


def rows(rel):
    return [json.loads(ln) for ln in open(os.path.join(ROOT, rel)) if ln.strip()]


def loc(rel, pattern, nth=0):
    """file:line of the nth line of `rel` matching `pattern` (regular expression)."""
    hits = [i + 1 for i, ln in enumerate(open(os.path.join(ROOT, rel))) if re.search(pattern, ln)]
    assert len(hits) > nth, (rel, pattern)
    return f"{rel}:{hits[nth]}"


def ranges(vals):
    v = sorted(set(int(x) for x in vals))
    if not v:
        return ""
    out, a, b = [], v[0], v[0]
    for x in v[1:]:
        if x == b + 1:
            b = x
        else:
            out.append(f"{a}-{b}" if b > a else f"{a}")
            a = b = x
    out.append(f"{a}-{b}" if b > a else f"{a}")
    return ", ".join(out)


# ------------------------------------------------------------------ 1. seeds
# (label, file, filter) for run seeds; perturbation and noise seeds are read from the same rows.
SEED_FILES = [
    ("E1a", "data/E1/E1_runs.jsonl", lambda r: r["mode"] == "E1a"),
    ("E1b", "data/E1/E1_runs.jsonl", lambda r: r["mode"] == "E1b"),
    ("E2", "data/E2/e2_quench.jsonl", None),
    ("E3", "data/E3/e3_dt.jsonl", None),
    ("E4", "data/E4/e4_escape.jsonl", None),
    ("E5a", "data/E5/e5a.jsonl", None),
    ("E5b", "data/E5/e5b.jsonl", None),
    ("E6a", "data/E6/e6a.jsonl", None),
    ("E6b", "data/E6/e6b.jsonl", None),
    ("E6p", "data/E6/e6p.jsonl", None),
    ("E7", "data/E7/e7_cells.jsonl", None),
    ("E7b_lib", "data/E7b/e7b_lib.jsonl", None),
    ("E7b_quench", "data/E7b/e7b_quench.jsonl", None),
    ("E8", "data/E8/e8_counterflow.jsonl", None),
    ("E9", "data/E9/e9_crossing.jsonl", None),
    ("E10", "data/E10/e10_croma.jsonl", None),
    ("E11", "data/E11/e11_overlap.jsonl", None),
    ("arch", "data/arch/arch.jsonl", None),
    ("N1", "data/N1/n1.jsonl", None),
    ("N2", "data/N2/n2.jsonl", None),
    ("N3", "data/N3/n3.jsonl", None),
    ("N5", "data/N5/n5.jsonl", None),
    ("N6_quench", "data/N6/n6_quench.jsonl", None),
    ("velorca_lone", "data/velorca/lone.jsonl", None),
    ("velorca_pair", "data/velorca/pair.jsonl", None),
    ("velorca_whole", "data/velorca/whole.jsonl", None),
    ("A1", "data/revision/A1/a1_quench.jsonl", None),
    ("A2", "data/revision/A2/a2_runs.jsonl", None),
    ("A5x", "data/revision/A5/a5_quench.jsonl", None),
    ("B1", "data/revision/B1/b1.jsonl", None),
    ("B2", "data/revision/B2/b2.jsonl", None),
    ("B3", "data/revision/B3/b3.jsonl", None),
    ("B4", "data/revision/B4/b4.jsonl", None),
    ("B5_gen", "data/revision/B5/gen_rounded.jsonl", None),
    ("B5_quench", "data/revision/B5/quench.jsonl", None),
    ("B6_gen", "data/revision/B6/gen_line.jsonl", None),
    ("B6_quench", "data/revision/B6/quench.jsonl", None),
    ("D3", "data/revision/D3/d3_croma.jsonl", None),
]


def tag_of(r):
    return r["job_id"].split("|")[0]


def beta_of(r):
    m = re.search(r"\|b([0-9.]+)\|", r["job_id"])
    return float(m.group(1))


# Structured noise seeds: base + kmult * k + extra(row) + rep.
NOISE_RULES = {
    "E2": (7000, 100, lambda r: 0, "7000 + 100 k + rep"),
    "E3": (51000, 1000, lambda r: 10 * int(round(1000 * r["dt"])) + (500 if r["mode"] == "dt_scaled" else 0),
           "51000 + 1000 k + 10 round(1000 dt) + rep (+500 dt_scaled)"),
    "E4": (11000, 1000, lambda r: 100 * (1.5, 2.5, 3.5).index(beta_of(r)), "11000 + 1000 k + 100 level + rep"),
    "E7b_quench": (20000, 100, lambda r: 0, "20000 + 100 k + rep"),
    "N1": (27000, 100, lambda r: 0, "27000 + 100 k + rep"),
    "N3": (31000, 1000, lambda r: 100 * (1.5, 2.5, 3.5).index(beta_of(r)), "31000 + 1000 k + 100 level + rep"),
    "B3": (51000, 1000, lambda r: 100 * (5.0, 6.0, 7.0).index(beta_of(r)), "51000 + 1000 k + 100 level + rep"),
    "A5x": (90000, 100, lambda r: 0, "90000 + 100 k + rep"),
}


def decompose(label, R):
    base, km, extra, rule = NOISE_RULES[label]
    ks = defaultdict(set)
    for r in R:
        rest = r["noise_seed"] - base - extra(r) - r["rep"]
        assert rest % km == 0 and rest >= 0, (label, r["job_id"], r["noise_seed"])
        ks[tag_of(r)].add(rest // km)
    assert all(len(v) == 1 for v in ks.values()), label
    kk = {t: next(iter(v)) for t, v in ks.items()}
    assert len(set(kk.values())) == len(kk), label
    return rule, kk


def seeds():
    out, noise_sets = {}, {}
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))
    order = {"E2": [s["tag"] for s in sel["E2"]["snapshots"]], "E3": [s["tag"] for s in sel["E3"]["snapshots"]],
             "E4": [s["tag"] for s in sel["E4"]["snapshots"]]}
    for label, f, flt in SEED_FILES:
        R = [r for r in rows(f) if flt is None or flt(r)]
        run = [r["seed"] for r in R if isinstance(r.get("seed"), int)]
        pert = [r["perturb"] for r in R if r.get("perturb") is not None]
        noise = [r for r in R if r.get("noise_seed") is not None]
        d = {"file": f, "n_rows": len(R)}
        if run:
            d.update(run_seeds=ranges(run), n_run_seeds=len(set(run)))
        if pert:
            d.update(perturb_seeds=ranges(pert),
                     n_unperturbed=sum(1 for r in R if "perturb" in r and r["perturb"] is None))
        if noise:
            ns = [r["noise_seed"] for r in noise]
            noise_sets[label] = set(ns)
            d.update(noise_seed_min=min(ns), noise_seed_max=max(ns), n_noise_seeds=len(set(ns)), n_noise_rows=len(ns),
                     reps=ranges(r["rep"] for r in noise if "rep" in r))
            if label in NOISE_RULES:
                rule, kk = decompose(label, noise)
                d.update(noise_rule=rule, k_range=ranges(kk.values()))
                if label in order:
                    assert all(order[label].index(t) == k for t, k in kk.items()), label
                    d["k_is_selection_index"] = True
                if label in ("E2", "E7b_quench", "A5x"):
                    # the same seeds at every sigma
                    by_s = defaultdict(set)
                    for r in noise:
                        by_s[r["sigma"]].add(r["noise_seed"])
                    d["same_seeds_every_sigma"] = len({frozenset(v) for v in by_s.values()}) == 1
                if label in ("E4", "N3"):
                    # the condition does not enter the seed: one seed per (snapshot, level, rep) over conditions
                    by_c = defaultdict(set)
                    for r in noise:
                        p = r["job_id"].split("|")
                        by_c[(p[0], p[2], r["rep"])].add(r["noise_seed"])
                    d["conditions"] = sorted({r["job_id"].split("|")[1] for r in noise})
                    d["same_seed_every_condition"] = all(len(v) == 1 for v in by_c.values())
            if label == "N2":
                assert all(r["noise_seed"] == 50000 + r["seed"] for r in noise)
                d["noise_rule"] = "50000 + run seed (velocity-noise generator reseeded after the spawn)"
        out[label] = d
    # sigma = 0 cells of E5 are not run (reused from E1)
    out["E5a"]["sigmas"] = sorted({r["sigma"] for r in rows("data/E5/e5a.jsonl")})
    out["E5b"]["sigmas"] = sorted({r["sigma"] for r in rows("data/E5/e5b.jsonl")})
    # pairwise collisions of noise-seed integers between experiments
    labs = sorted(noise_sets)
    coll = []
    for i, a in enumerate(labs):
        for b in labs[i + 1:]:
            c = noise_sets[a] & noise_sets[b]
            if c:
                coll.append({"a": a, "b": b, "n": len(c), "seeds": ranges(c)})
    t3 = {31000, 31001}  # E3/t3_variance.py noise seeds 31000 + k, k = 0, 1 (no stored JSONL)
    for lab in labs:
        c = noise_sets[lab] & t3
        if c:
            coll.append({"a": "E3_t3_variance", "b": lab, "n": len(c), "seeds": ranges(c)})
    out["noise_collisions"] = coll
    out["sources"] = {
        "E1": loc("experiments/E1/e1_library.py", r"else \(42, 242\)"),
        "E2_perturb": loc("experiments/E2/e2_quench.py", r"^PERTURB_SEEDS"),
        "E2_noise": loc("experiments/E2/e2_quench.py", r'"noise_seed": 7000'),
        "perturb_draw": loc("experiments/lib/runlib.py", r"default_rng\(job\[\"perturb\"\]\)"),
        "perturb_size": loc("experiments/lib/runlib.py", r"rng.normal\(0, 1e-9"),
        "E3_noise": loc("experiments/E3/e3_dt.py", r'"noise_seed": 51000'),
        "E3_t3": loc("experiments/E3/t3_variance.py", r"noise_seed=31000"),
        "E4_noise": loc("experiments/E4/e4_escape.py", r'"noise_seed": 11000'),
        "E5": loc("experiments/E5/e5_sweep.py", r"^SEEDS"),
        "E6": loc("experiments/E6/e6.py", r"^SEEDS"),
        "E7": loc("experiments/E7/e7_cells.py", r"^SEEDS"),
        "E7b_lib": loc("experiments/E7b/e7b_lib.py", r"range\(S0, min\(s1, S_CAP"),
        "E7b_perturb": loc("experiments/E7b/e7b_quench.py", r"^PERTURB_SEEDS"),
        "E7b_noise": loc("experiments/E7b/e7b_quench.py", r'"noise_seed": 20000'),
        "E8": loc("experiments/E8/e8_counterflow.py", r"^SEEDS"),
        "E9": loc("experiments/E9/e9_crossing.py", r"^SEEDS"),
        "E10": loc("experiments/E10/e10_croma.py", r"^SEEDS"),
        "E11": loc("experiments/E11/e11_overlap.py", r"^SEEDS"),
        "arch": loc("experiments/arch/arch.py", r"range\(42, 67\)"),
        "N1": loc("experiments/runs3/N1.py", r'"noise_seed": 27000'),
        "N2": loc("experiments/runs3/N2.py", r"PCG64\(NOISE_BASE \+ seed\)"),
        "N3": loc("experiments/runs3/N3.py", r"noise_seed=31000"),
        "N5": loc("experiments/runs3/N5.py", r"^SEEDS"),
        "velorca_perturb": loc("experiments/velorca/velorca.py", r"^PERTURB_SEEDS"),
        "velorca_whole": loc("experiments/velorca/velorca.py", r"^SEEDS"),
        "A5x_noise": loc("experiments/revision/A5_extra_second_traps.py", r'"noise_seed": NOISE_BASE'),
        "B2": loc("experiments/revision/B2_width.py", r"^SEEDS"),
        "B3": loc("experiments/revision/B3_highbeta.py", r'"noise_seed": 51000'),
        "B4": loc("experiments/revision/B4_arch_dt.py", r"^SEEDS"),
        "B5_B6_gen": loc("experiments/revision/B6_gen.py", r"def seeds"),
        "B6_perturb": loc("experiments/revision/B6_quench.py", r"PERTURB_SEEDS if arm"),
        "D3": loc("experiments/revision/D3_croma_rerun.py", r"for s in E10.SEEDS"),
        "run_seed_spawn": loc("code/sim/core/simulation.py", r"PCG64\(seed\)"),
        "noise_seed_restore": loc("experiments/lib/w2lib.py", r"seed=0 if noise_seed is None else noise_seed"),
    }
    return out


# ------------------------------------------------------------------ 2. deadlocks
def deadlocks():
    R = [r for r in rows("data/E1/E1_runs.jsonl") if r["mode"] == "E1b"]
    n_c = sum(r["complete"] for r in R)
    n_d = sum(r["deadlock"] for r in R)
    n_cap = sum((not r["complete"]) and (not r["deadlock"]) for r in R)
    pk = glob.glob(os.path.join(DATA, "E1", "library", "E1b_seed*.pkl"))
    Ra = [r for r in rows("data/E1/E1_runs.jsonl") if r["mode"] == "E1a"]
    ks = json.load(open(os.path.join(DERIVED, "E1_keystone.json")))["modes"]["E1b"]
    cc = {k: v["k"] for k, v in ks["class_counts"].items()}
    assert n_c + n_d + n_cap == len(R) == 200 and n_d == len(pk) == ks["n_snapshots"]
    dl_t = [r["t_end"] for r in R if r["deadlock"]]
    return {"runs": len(R), "complete": n_c, "deadlock": n_d, "capped": n_cap, "pickles": len(pk),
            "deadlock_time_s": {"min": min(dl_t), "median": float(np.median(dl_t)), "max": max(dl_t)},
            "complete_seeds": ranges(r["seed"] for r in R if r["complete"]),
            "E1a": {"runs": len(Ra), "complete": sum(r["complete"] for r in Ra), "deadlock": sum(r["deadlock"] for r in Ra)},
            "classes": cc, "second_trap_K1b_held": ks["second_trap"]["K1b_held"],
            "second_trap_K1b_freed": ks["second_trap"]["K1b_freed"],
            "collective_seeds": [c["seed"] for c in ks["collective"]["cases"]],
            "rule": {"v_thr_m_s": 0.01, "hold_s": 10.0, "check_every_steps": 10, "t_max_s": 600.0, "dt_s": 0.01},
            "sources": {"detector": loc("experiments/lib/w2lib.py", r"def __init__\(self, hold=10.0, v_thr=0.01, every=10\)"),
                        "timer_reset": loc("experiments/lib/w2lib.py", r"if self.n_prev is None or n != self.n_prev"),
                        "cap": loc("experiments/E1/e1_library.py", r"^T_MAX = 600"),
                        "flags": loc("experiments/E1/e1_library.py", r'^MODES = '),
                        "save": loc("experiments/E1/e1_library.py", r"pickle.dump\(snapshot\(sim\)"),
                        "keystone_classes": loc("experiments/E1/keystone.py", r"lone_keystone             K1 held"),
                        "keystone_stop": loc("experiments/E1/keystone.py", r"StationaryDetector\(hold=10, v_thr=1e-3\)"),
                        "keystone_window": loc("experiments/E1/keystone.py", r"^T_Q = 120")}}


# ------------------------------------------------------------------ 3. selection
def selection():
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))
    ks = json.load(open(os.path.join(DERIVED, "E1_keystone.json")))["modes"]["E1b"]["per_snapshot"]
    pa = sorted(x["seed"] for x in ks if x["class"] == "lone_keystone")
    pb = sorted(x["seed"] for x in ks if x["class"] == "lone_keystone_second_trap")
    rng = np.random.Generator(np.random.PCG64(2026))
    extra = sorted(int(s) for s in rng.choice(pb, 26, replace=False))
    stored = [s["seed"] for s in sel["E2"]["snapshots"]]
    assert stored == pa + extra
    G = json.load(open(os.path.join(DATA, "BAR", "barriers_gated.json")))["barriers"]
    cls = {s["tag"]: s["class"] for s in sel["E2"]["snapshots"]}
    nres = {s["tag"]: s["n_resid"] for s in sel["E2"]["snapshots"]}
    acc = [t for t in cls if G[t]["full"]["accepted"]]
    rowsq = [{"tag": t, "dU": G[t]["full"]["dU"], "seed": int(t.split("seed")[1])} for t in acc]

    def spread(q, n):
        r = sorted(q, key=lambda x: (x["dU"], x["seed"]))
        idx = np.round(np.linspace(0, len(r) - 1, n)).astype(int)
        return [r[i]["tag"] for i in idx], idx.tolist()
    q3 = [x for x in rowsq if x["dU"] >= 3.0]
    q4 = [x for x in rowsq if nres[x["tag"]] >= 2]
    e3, i3 = spread(q3, 20)
    e4, i4 = spread(q4, 10)
    assert e3 == [s["tag"] for s in sel["E3"]["snapshots"]] and e4 == [s["tag"] for s in sel["E4"]["snapshots"]]
    cnt = lambda T: dict(Counter(cls[t] for t in T))  # noqa: E731
    du = {t: G[t]["full"]["dU"] for t in acc}
    st = rows("data/E7b/e7b_static.jsonl")
    srt = sorted(st, key=lambda r: r["lambda1"])
    ip = np.round(np.linspace(0, len(srt) - 1, 12)).astype(int)
    pb_tags = [srt[i]["job_id"] for i in ip]
    bar = rows("data/E7b/e7b_barrier.jsonl")
    assert sorted(pb_tags) == sorted(r["job_id"] for r in bar)
    return {
        "E2": {"n": len(stored), "lone_keystone": len(pa), "second_trap_pool": len(pb), "second_trap_drawn": len(extra),
               "drawn_seeds": extra, "rule": "all lone keystones + Generator(PCG64(2026)).choice(160 ascending, 26, replace=False)"},
        "gate_accepted": len(acc), "gate_accepted_by_class": cnt(acc),
        "E3": {"n_qualifying": len(q3), "qualifying_by_class": cnt([x["tag"] for x in q3]), "n": len(e3),
               "by_class": cnt(e3), "ranks": i3, "dU_min_J": min(du[t] for t in e3), "dU_max_J": max(du[t] for t in e3),
               "rule": "gate-accepted, full Delta U >= 3 J; ranks round(linspace(0, n_q - 1, 20)) by (Delta U, seed)"},
        "E4": {"n_qualifying": len(q4), "qualifying_by_class": cnt([x["tag"] for x in q4]), "n": len(e4),
               "by_class": cnt(e4), "ranks": i4, "dU_min_J": min(du[t] for t in e4), "dU_max_J": max(du[t] for t in e4),
               "rule": "gate-accepted, n_resid >= 2 (blocker counted); ranks round(linspace(0, n_q - 1, 10)) by (Delta U, seed)"},
        "both_rules": len({x["tag"] for x in q3} & {x["tag"] for x in q4}), "in_E3_and_E4": len(set(e3) & set(e4)),
        "pair": {"library": len(st), "n": len(pb_tags), "ranks": ip.tolist(),
                 "mu1_min_N_m": srt[0]["lambda1"], "mu1_max_N_m": srt[-1]["lambda1"],
                 "accepted": sum(bool(r["accepted"]) for r in bar),
                 "channels": sum(len(r["channels"]) for r in bar),
                 "channels_accepted": sum(sum(bool(c["accepted"]) for c in (r["channels"].values() if isinstance(r["channels"], dict) else r["channels"])) for r in bar)},
        "sources": {"E2": loc("experiments/selection.py", r"rng.choice\(pool_b"),
                    "spread": loc("experiments/selection.py", r"np.round\(np.linspace\(0, len\(r\) - 1, n\)\)"),
                    "E3_rule": loc("experiments/selection.py", r'q = \[r for r in rows if r\["dU"\] >= DU_MIN\]'),
                    "E4_rule": loc("experiments/selection.py", r"q4 = \[r for r in rows if r\[\"n_resid\"\] >= MIN_RESID_E4\]"),
                    "constants": loc("experiments/selection.py", r"^N_E2_EXTRA"),
                    "pair": loc("experiments/E7b/e7b_barrier.py", r"np.linspace\(0, len\(P\) - 1")}}


# ------------------------------------------------------------------ 4. string method
def strings():
    import bar
    import gate
    G = rows("data/BAR/gate.jsonl")
    sel = json.load(open(os.path.join(DERIVED, "selection.json")))
    cls = {s["tag"]: s["class"] for s in sel["E2"]["snapshots"]}
    fails = []
    acc = {c: 0 for c in gate.CONDS}
    pairs = {c: Counter() for c in gate.CONDS}
    for r in G:
        for c in gate.CONDS:
            acc[c] += bool(r[c]["accepted"])
            pairs[c][tuple(r[c]["resolution_pair"])] += 1
            if not r[c]["accepted"]:
                fails.append({"tag": r["job_id"], "class": cls[r["job_id"]], "cond": c, "reasons": r[c]["reasons"],
                              "n_resid": len(r["resid"])})
    fails.sort(key=lambda x: int(x["tag"].split("seed")[1]))
    return {"n_rows": len(G), "accepted": acc,
            "resolution_pairs_full": {f"{a}-{b}": n for (a, b), n in pairs["full"].items()},
            "failed": fails, "n_failed": len(fails),
            "settings": {"images": list(gate.RESOLUTIONS), "schedule_iters_alpha": [list(x) for x in gate.SCHEDULE],
                         "step_cap_m": bar.STEP_CAP, "F_perp_tol_N": gate.F_TOL, "doubling_tol": gate.DOUBLE_TOL,
                         "climb_grad_tol_N": 1e-2, "climb_max_iters": 3000, "climb_alpha_fallback_factor": 0.25,
                         "guard_tol_J": gate.GUARD_TOL, "overlap_max_m": gate.OVERLAP_MAX, "x_exit_m": gate.X_EXIT,
                         "exit_state_x_m": 10.0, "grid_tol": gate.GRID_TOL, "grid_res_tol": gate.GRID_RES_TOL,
                         "grid_h_m": list(gate.GRID_H), "relax_steps": 4000, "relax_alpha": 5e-5, "relax_grad_tol_N": 1e-3,
                         "fd_h_m": 1e-6, "pair_cutoff_m": 3.0, "frozen_ratio": gate.FROZEN_RATIO},
            "sources": {"step_cap": loc("experiments/BAR/bar.py", r"^STEP_CAP"),
                        "relax": loc("experiments/BAR/bar.py", r"def relax\(field, X, fix_idx=\(\), steps=4000, alpha=5e-5\)"),
                        "relax_stop": loc("experiments/BAR/bar.py", r"if np.max\(np.abs\(g\)\) < 1e-3"),
                        "fd_grad": loc("experiments/BAR/bar.py", r"def grad\(self, X, h=1e-6\)"),
                        "end_alone_frozen": loc("experiments/BAR/bar.py", r"XB = np.array\(\[10.35, 5.0\]\)"),
                        "end_full": loc("experiments/BAR/gate.py", r"XBf = bar.relax\(fm, XBf, fix_idx=\(0, 1\)\)"),
                        "start": loc("experiments/BAR/gate.py", r"XA = bar.relax\(fa, xb.copy\(\)\)"),
                        "reparam": loc("experiments/BAR/gate.py", r"def string_iter"),
                        "tolerances": loc("experiments/BAR/gate.py", r"^F_TOL"),
                        "resolutions": loc("experiments/BAR/gate.py", r"^RESOLUTIONS"),
                        "schedule": loc("experiments/BAR/gate.py", r"^SCHEDULE"),
                        "upwind_tangent": loc("experiments/BAR/gate.py", r"def tangent"),
                        "f_perp_segment": loc("experiments/BAR/gate.py", r"for k in range\(1, min\(top \+ 2"),
                        "climb": loc("experiments/BAR/gate.py", r"def climb"),
                        "gate_checks": loc("experiments/BAR/gate.py", r"def check\(field"),
                        "rule_doc": loc("experiments/BAR/gate.py", r"\(i\)   the string has converged")}}


# ------------------------------------------------------------------ 5. ORCA
def orca():
    from w2lib import build
    from sim.steering.orca import ORCAModel
    vals = {}
    for name, fl in (("rvo2", {**CF, "w2_orca": "rvo2"}), ("legacy", {**CF, "w2_orca": "published"})):
        sim = build("C3", seed=42, width=0.8, flags=fl)
        o = sim.steering.orca
        vals[name] = {"variant": o.variant, "time_horizon_s": o.time_horizon, "tau_orca_s": o.tau_orca,
                      "collision_dt_s": o.dt, "neighbor_radius_m": sim.params["neighbor_radius"],
                      "gate_rho0": sim.steering.params.get("rho_orca_fade", 4.0),
                      "gate_k": sim.steering.params.get("k_orca_fade", 2.0)}
    sig = list(inspect.signature(ORCAModel.compute_orca_forces).parameters)
    import sim.steering.orca_rvo2 as orv
    src = open(inspect.getsourcefile(ORCAModel)).read() + open(orv.__file__).read()
    return {"solvers": vals, "compute_orca_forces_args": sig, "mentions_wall": bool(re.search(r"wall", src, re.I)),
            "max_neighbours": None, "speed_circle_v0": 2.0,
        "sources": {"neighbor_radius": loc("code/sim/core/simulation.py", r'"neighbor_radius": 3.0'),
                    "neighbour_query": loc("code/sim/core/simulation.py", r"query_ball_point\(active_pos", 1),
                    "horizon_default": loc("code/sim/steering/orca.py", r"time_horizon: float = 5.0"),
                    "tau_orca_default": loc("code/sim/steering/orca.py", r"tau_orca: float = 0.5"),
                    "construct": loc("code/sim/steering/hybrid.py", r'time_horizon=params.get\("time_horizon", 5.0\)'),
                    "params_yaml": loc("code/config/params.yaml", r"orca: \{time_horizon"),
                    "force": loc("code/sim/steering/orca.py", r"forces\[i\] = m \* \(v_orca - v\) / self.tau_orca"),
                    "speed_circle": loc("code/sim/steering/orca.py", r"max_speed = 2.0 \* agent_state.desired_speeds\[i\]"),
                    "rvo2_lines_call": loc("code/sim/steering/orca.py", r"lines = orca_rvo2.orca_lines"),
                    "rvo2_no_obstacles": loc("code/sim/steering/orca_rvo2.py", r"agent part only; no obstacles"),
                    "rvo2_neighbour_set": loc("code/sim/steering/orca_rvo2.py", r"The neighbour set itself"),
                    "rvo2_sorted": loc("code/sim/steering/orca.py", r"nb.sort\(key=lambda t: t\[0\]\)"),
                    "legacy_halfplanes": loc("code/sim/steering/orca.py", r"for j in neighbor_lists\[i\]:", 1),
                    "collision_dt": loc("code/sim/steering/orca.py", r"halfplanes.append\(_halfplane_collision"),
                    "gate": loc("code/sim/steering/hybrid.py", r'self.params.get\("rho_orca_fade", 4.0\)'),
                    "added_to_F": loc("code/sim/steering/hybrid.py", r"F \+= w_orca\[:, None\] \* F_orca"),
                    "walls_separate": loc("code/sim/steering/hybrid.py", r"F_orca = self.orca.compute_orca_forces\(agent_state, neighbor_lists\)"),
                    "velocity_filter": loc("code/sim/steering/orca.py", r"def filter_velocities")}}


# ------------------------------------------------------------------ 6. ORCA escape rate in E3
def e3_orca():
    R = [r for r in rows("data/E3/e3_dt.jsonl") if r["mode"] == "C3_rvo2"]
    by = defaultdict(dict)
    for r in R:
        by[tag_of(r)][r["dt"]] = r
    assert all(len(v) == 3 for v in by.values()) and len(by) == 20
    freed = [t for t, v in by.items() if all(not v[d]["censored"] for d in (0.005, 0.01, 0.02))]
    held = [t for t, v in by.items() if all(v[d]["censored"] for d in (0.005, 0.01, 0.02))]
    lr = {t: math.log(by[t][0.02]["escape_t"] / by[t][0.005]["escape_t"]) for t in freed}
    A = json.load(open(os.path.join(DERIVED, "E3_analysis.json")))
    h = A["headline"]
    assert len(freed) == h["c3_n_freed"] and abs(max(abs(x) for x in lr.values()) - h["c3_ln_ratio_maxabs"]) < 1e-12
    t01 = [by[t][0.01]["escape_t"] for t in freed]
    fig = json.load(open(os.path.join(ROOT, "figures", "data", "fig5.json")))["C3_rvo2"]
    return {"n_snapshots": len(by), "runs_per_dt": 1, "n_runs": len(R), "n_freed": len(freed), "n_held_300s": len(held),
            "mixed": len(by) - len(freed) - len(held), "ln_ratio_maxabs": max(abs(x) for x in lr.values()),
            "ln_ratio_mean": float(np.mean(list(lr.values()))), "t_esc_dt0p01_s": {"min": min(t01), "median": float(np.median(t01)), "max": max(t01)},
            "fig_n": fig["n"], "fig_mean": fig["mean"], "t_cens_s": R[0]["t_cens"], "sigma": R[0]["sigma"],
            "perturb": None, "event": "blocker centre x >= 10 m (or blocker exits)",
            "noise_ell_definition": "ln lambda_hat(0.005) / lambda_hat(0.02), lambda_hat = censored-exponential MLE over 20 restarts",
            "sources": {"jobs": loc("experiments/E3/e3_dt.py", r'"mode": "C3_rvo2", "t_cens": T_CENS'),
                        "event": loc("experiments/lib/runlib.py", r"if x >= 10.0 or not st.active\[b\]"),
                        "orca_ell": loc("experiments/E3/analyze.py", r'"ln_ratio": \(math.log\(tt\["dt0p02"\] / tt\["dt0p005"\]\)'),
                        "orca_fig": loc("experiments/E3/analyze.py", r'"norm_inv_t": \(\{k: tt\["dt0p01"\] / v'),
                        "noise_ell": loc("experiments/E3/analyze.py", r'ell = math.log\(a\["lam"\] / b\["lam"\]\)'),
                        "rate_mle": loc("experiments/E3/analyze.py", r"cell = exp_rate\(t, c\)"),
                        "eq_ell": loc("paper/sections/04_protocol.tex", r"\\ell\\equiv"),
                        "table2": loc("paper/tables/table2_signatures.tex", r"EthreeCThreeLnRatioMax"),
                        "fig_caption": loc("paper/sections/05_deadlock_physics.tex", r"force-coupled ORCA \(RVO2, diamonds\)")}}


# ------------------------------------------------------------------ 7. run counts
def counts():
    out = {}
    for part, n_snap in (("lone", 60), ("pair", 46)):
        R = rows(f"data/velorca/{part}.jsonl")
        c = Counter(r["perturbation"] for r in R)
        per = {k: {"runs": v, "unperturbed": sum(1 for r in R if r["perturbation"] == k and r["perturb"] is None),
                   "snapshots": len({tag_of(r) for r in R if r["perturbation"] == k})} for k, v in c.items()}
        assert all(v["runs"] == n_snap * 6 and v["snapshots"] == n_snap and v["unperturbed"] == n_snap for v in per.values())
        out[f"velorca_{part}"] = per
    for lab, f, n_snap in (("E2", "data/E2/e2_quench.jsonl", 60), ("E7b", "data/E7b/e7b_quench.jsonl", 46)):
        R = [r for r in rows(f) if r.get("deterministic")]
        c = Counter(r["arm"] for r in R)
        out[f"{lab}_det_runs_per_arm"] = sorted(set(c.values()))
        out[f"{lab}_det_arms"] = len(c)
        out[f"{lab}_C3_rvo2_runs"] = c["C3_rvo2"]
    B5 = rows("data/revision/B5/reequil.jsonl")
    rc = Counter(r["job_id"].split("|")[0] for r in B5)
    out["B5_reequil"] = {"rows": len(B5), "radii": sorted(rc), "per_radius": sorted(set(rc.values())),
                         "snapshots": len({r["job_id"].split("|")[1] for r in B5})}
    A = json.load(open(os.path.join(DERIVED, "rev_B5.json")))
    out["B5_rule_n_checked"] = A["main"]["n_checked"]
    E2 = json.load(open(os.path.join(DERIVED, "E2_analysis.json")))
    out["E2_lemma_pairs"] = E2["c_rest_state_lemma_C2_vs_C1"]["pairs"]
    out["sources"] = {"velorca_jobs": loc("experiments/velorca/velorca.py", r"for ps in \(None,\) \+ PERTURB_SEEDS", 0),
                      "B5_radii": loc("experiments/revision/B5_static.py", r"^RC_SCAN"),
                      "paper_velorca": loc("paper/sections/06_screening.tex", r"VelLoneN"),
                      "paper_B5": loc("paper/sections/05_deadlock_physics.tex", r"RevBfiveRuleN")}
    return out


def main():
    res = {"seeds": seeds(), "deadlocks": deadlocks(), "selection": selection(), "strings": strings(),
           "orca": orca(), "e3_orca": e3_orca(), "counts": counts()}
    res["macros"] = {
        "deadlocks": res["deadlocks"]["deadlock"], "runs": res["deadlocks"]["runs"],
        "complete": res["deadlocks"]["complete"],
        "lone": res["selection"]["E2"]["lone_keystone"], "second": res["selection"]["E2"]["second_trap_drawn"],
        "second_pool": res["selection"]["E2"]["second_trap_pool"], "collective": res["deadlocks"]["classes"]["collective"],
        "accepted": res["selection"]["gate_accepted"], "failed": res["strings"]["n_failed"],
        "e3_qual": res["selection"]["E3"]["n_qualifying"], "e3_n": res["selection"]["E3"]["n"],
        "e4_qual": res["selection"]["E4"]["n_qualifying"], "e4_n": res["selection"]["E4"]["n"],
        "pair_lib": res["selection"]["pair"]["library"], "pair_bar": res["selection"]["pair"]["n"],
        "img_lo": res["strings"]["settings"]["images"][0], "img_mid": res["strings"]["settings"]["images"][1],
        "img_hi": res["strings"]["settings"]["images"][2],
        "step_cap_mm": 1000 * res["strings"]["settings"]["step_cap_m"],
        "f_tol": res["strings"]["settings"]["F_perp_tol_N"],
        "double_tol_pct": 100 * res["strings"]["settings"]["doubling_tol"],
        "overlap_cm": 100 * res["strings"]["settings"]["overlap_max_m"],
        "grid_tol_pct": 100 * res["strings"]["settings"]["grid_tol"],
        "x_exit": res["strings"]["settings"]["x_exit_m"],
        "orca_R": res["orca"]["solvers"]["rvo2"]["neighbor_radius_m"],
        "orca_th": res["orca"]["solvers"]["rvo2"]["time_horizon_s"],
        "orca_tau": res["orca"]["solvers"]["rvo2"]["tau_orca_s"],
        "e3_orca_freed": res["e3_orca"]["n_freed"], "e3_orca_held": res["e3_orca"]["n_held_300s"],
        "e3_orca_ell_max": res["e3_orca"]["ln_ratio_maxabs"],
        "lone_runs": res["counts"]["velorca_lone"]["vel_rvo2"]["runs"],
        "pair_runs": res["counts"]["velorca_pair"]["vel_rvo2"]["runs"],
        "b5_cases": res["counts"]["B5_reequil"]["rows"], "b5_radii": len(res["counts"]["B5_reequil"]["radii"]),
        "replays": 5,
        "climb_tol": res["strings"]["settings"]["climb_grad_tol_N"],
        "du_min": 3.0, "dl_vthr": res["deadlocks"]["rule"]["v_thr_m_s"], "dl_hold": res["deadlocks"]["rule"]["hold_s"],
        "dl_cap": res["deadlocks"]["rule"]["t_max_s"], "draw_seed": 2026,
        "res_124": res["strings"]["resolution_pairs_full"].get("62-124", 0),
        "e3_orca_cens": res["e3_orca"]["t_cens_s"],
        "lib_n": res["selection"]["E2"]["n"], "e3_orca_n": res["e3_orca"]["n_snapshots"],
        "dl_check_s": res["deadlocks"]["rule"]["check_every_steps"] * res["deadlocks"]["rule"]["dt_s"],
        "ks_window": 120.0, "runs_per_snap": 1 + 5, "replay_disp_m": 1e-9, "width": 0.8,
    }
    S = res["seeds"]

    def lohi(name, lab, field="run_seeds"):
        a, b = S[lab][field].split("-")
        res["macros"][name + "_lo"], res["macros"][name + "_hi"] = int(a), int(b)
    for name, lab in (("e1", "E1b"), ("e5", "E5b"), ("e6", "E6a"), ("e6p", "E6p"), ("pairlib", "E7b_lib"),
                      ("open", "E8"), ("vel", "velorca_whole"), ("b2", "B2"), ("b4", "B4")):
        lohi(name, lab)
    lohi("pert", "E2", "perturb_seeds")
    for lab in ("E7b_quench", "velorca_lone", "velorca_pair", "A5x", "B6_quench"):
        assert S[lab]["perturb_seeds"] == "900-904"
    for lab in ("E9", "E10", "E11", "arch", "N5", "D3"):
        assert S[lab]["run_seeds"] == "42-66"
    for lab in ("E1a",):
        assert S[lab]["run_seeds"] == "42-241"
    for lab in ("E5a", "E7"):
        assert S[lab]["run_seeds"] == "42-141"
    for lab in ("E6b", "N2"):
        assert S[lab]["run_seeds"] == "242-427"
    for lab in ("B5_gen", "B6_gen"):
        assert S[lab]["run_seeds"] == "242-561"
    p = out_json("A8", res)
    print(p)
    print(json.dumps(res["macros"], indent=1))
    print("collisions", res["seeds"]["noise_collisions"])
    print("fails", [(f["tag"], f["cond"], f["reasons"]) for f in res["strings"]["failed"]])
    print("orca", res["orca"]["solvers"], res["orca"]["compute_orca_forces_args"], res["orca"]["mentions_wall"])


if __name__ == "__main__":
    main()
