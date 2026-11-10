"""A15: table of every stillness threshold, horizon, censoring time and event rule behind the paper's numbers.

What it does
  1. Rows. Each row is one quantity (value, unit, where it acts, where the paper states it). The code location
     of every row is found by a regular expression on the source file at run time, so each file:line in the
     output is the line as it stands in this worktree; the script fails if a pattern no longer matches.
  2. Stop-rule audit on the stored runs (no new simulation):
       quench   E2 (data/E2/e2_quench.jsonl), E7b (data/E7b/e7b_quench.jsonl), velocity coupling
                (data/velorca/lone.jsonl, pair.jsonl): deterministic runs that hold, split into "stopped by the
                stationary detector" (|v| < 1e-3 m/s for 10 s) and "ran to 120 s" (still moving), also per arm; latest freeing time among the
                freed runs (blocker exit for E2 and velocity-coupled lone runs, first member exit for pairs).
       escape   E3 (data/E3/e3_dt.jsonl), E4 (data/E4/e4_escape.jsonl), N3 (data/N3/n3.jsonl): runs censored at
                each censoring time; latest escape time.
       whole    E6 (data/E6/e6a.jsonl, e6b.jsonl): runs ended by the deadlock detector, by completion and by
                the 600 s cap.
Output: data/derived/rev_A15.json (rows + audit); the LaTeX table is experiments/revision/notes/A15_table.tex
(written by this script).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revlib  # noqa: E402

R = revlib.ROOT


def loc(path, pattern, nth=0):
    """'path:line' of the nth line of path (relative to the worktree) matching the regex pattern."""
    hits = []
    with open(os.path.join(R, path)) as f:
        for i, line in enumerate(f, 1):
            if re.search(pattern, line):
                hits.append(i)
    if len(hits) <= nth:
        raise SystemExit(f"pattern not found: {path} /{pattern}/")
    return f"{path}:{hits[nth]}"


W2 = "experiments/lib/w2lib.py"
RL = "experiments/lib/runlib.py"
SIM = "code/sim/core/simulation.py"

# id, group, quantity, value, code locations (list of (path, regex)), paper statement, flag
ROWS = [
    # ---------------- model-level
    ("M1", "model", "Exit (agent removed)", "$|\\mathbf x-\\mathbf g|<0.5$ m, $\\mathbf g=(11,5)$ m",
     [(SIM, r'"goal_reached_dist": 0\.5'), (SIM, r"dists_to_goal < self\.params\[\"goal_reached_dist\"\]")],
     "Table 1", ""),
    ("M2", "model", "TTC relative-speed cutoff", "$|\\Delta\\mathbf v|\\ge10^{-4}$ m/s (coded $|\\Delta\\mathbf v|^2\\ge10^{-8}$)",
     [("code/sim/steering/ttc.py", r"valid = \(a >= 1e-8\)")], "Sects. 3.1, 4.3", ""),
    ("M3", "model", "TTC look-ahead", "$0<\\tau_{ij}\\le\\tau_{\\max}=8$ s",
     [("code/sim/steering/ttc.py", r"tau_max: float = 8\.0"), ("code/sim/steering/ttc.py", r"tau <= self\.tau_max")],
     "Sect. 3.1, Table 1", ""),
    ("M4", "model", "ORCA horizon", "$\\tau_h=5$ s", [("code/sim/steering/orca.py", r"time_horizon: float = 5\.0")],
     "Sect. 3.2, Table 1", ""),
    ("M5", "model", "Neighbour / density radius", "$R=3$ m", [(SIM, r'"neighbor_radius": 3\.0')], "Sect. 3.1", ""),
    # ---------------- detectors
    ("D1", "detector", "Deadlock (whole runs, snapshot)",
     "all active $|\\mathbf v|<0.01$ m/s for 10 s, no exit; checked every 10 steps; timer reset at any exit",
     [(W2, r"def __init__\(self, hold=10\.0, v_thr=0\.01, every=10\)"), (W2, r"if self\.n_prev is None or n != self\.n_prev"),
      (RL, r"det = StationaryDetector\(\)"), ("experiments/E1/e1_library.py", r"det = StationaryDetector\(\)")],
     "Table 1; Sect. 3.4 (no exit)", "check interval (0.1 s at 0.01 s) not stated"),
    ("D2", "detector", "Quench stationary stop (deterministic arms)", "all active $|\\mathbf v|<10^{-3}$ m/s for 10 s, no exit",
     [(RL, r"StationaryDetector\(hold=10\.0, v_thr=1e-3\) if job\.get\(\"deterministic\"\)"),
      ("experiments/E7b/e7b_quench.py", r"StationaryDetector\(hold=10\.0, v_thr=1e-3\)"),
      ("experiments/velorca/velorca.py", r"StationaryDetector\(hold=10\.0, v_thr=1e-3\)"),
      ("experiments/E1/keystone.py", r"det = StationaryDetector\(hold=10\.0, v_thr=1e-3\)"),
      ("experiments/E6/keystone_e6.py", r"StationaryDetector\(hold=10\.0, v_thr=1e-3\)")],
     "Sect. 3.4", "noise arms have no stop (stated implicitly: 'Deterministic perturbations stop')"),
    ("D3", "detector", "Arch recorder", "contact component touching both jambs, among agents within 1.5 m of (10,5) with $x<10.3$ m; checked every 0.1 s; persistent if $\\ge10$ s",
     [("experiments/arch/arch.py", r"^PERSIST = 10\.0"), ("experiments/arch/arch.py", r"^EVERY = 10"),
      ("experiments/arch/arch.py", r"< 1\.5\) & \(P\[:, 0\] < 10\.3\)"), ("experiments/runs3/N5.py", r"^CHECK_S = 0\.1")],
     "Sect. 5.4 (0.1 s, 10 s)", "spatial window (1.5 m, x<10.3 m) not stated"),
    ("D4", "detector", "Stall (whole runs, CroMa not)", "interval $\\ge10$ s between exits; the first interval (walk to the door) excluded; open stall at 600 s censored",
     [("experiments/E6/analyze.py", r"^STALL = 10\.0"), ("experiments/E6/analyze.py", r"if b - a >= STALL and a > 0")],
     "Sects. 4.1, 6.2", "exclusion of the first interval not stated"),
    ("D5", "detector", "Door-zone arrival (arrival deciles)", "first step with $x>9.4$ m and $|y-5|<0.6$ m",
     [("experiments/E1/e1_library.py", r"x > 9\.4\) & \(np\.abs\(y - 5\.0\) < 0\.6"), (RL, r"x > 9\.4\) & \(np\.abs\(y - 5\.0\) < 0\.6")],
     "not stated (Sect. 5.1 'deciles of arrivals')", ""),
    # ---------------- events
    ("V1", "event", "Freed (lone-trap quench)", "the blocker exits (rule M1) within 120 s",
     [("experiments/E2/e2_quench.py", r'r\["blocker_freed"\] = t is not None and t <= T_Q'),
      ("experiments/E2/analyze.py", r'r\["_freed"\] = t is not None and t <= T_Q')],
     "Sect. 6.1", ""),
    ("V2", "event", "Freed (pair quench)", "any member exits (rule M1) within 120 s",
     [("experiments/E7b/analyze.py", r'r\["_t"\] = r\["first_t"\] if r\["freed"\]')],
     "Fig. 7 caption ('freed within 120 s'); rule not stated", "any member, not both"),
    ("V3", "event", "Escape (E3, E4, N3)", "blocker centre crosses $x\\ge10$ m (door plane) or exits",
     [(RL, r"if x >= 10\.0 or not st\.active\[b\]")], "not stated (Sects. 5.2, 6.1)",
     "differs from the quench event M1/V1 (exit at $|\\mathbf x-\\mathbf g|<0.5$ m, about 0.5 m further)"),
    ("V4", "event", "Static pair prediction (overdamped relaxation)", "freed if a member reaches $x>10.3$ m; held if $\\max|F|<0.05$ N; else undecided at 120 s (counted held)",
     [("experiments/lib/pairlib.py", r"def relax\(snap, cfg, flags, T=120\.0"), ("experiments/lib/pairlib.py", r"np\.abs\(F\)\.max\(\) < 0\.05"),
      ("experiments/lib/pairlib.py", r"st\.positions\[i, 0\] > 10\.3")], "not stated (Sect. 5.3)", ""),
    ("V5", "event", "Barrier end points (string method)", "trapped minimum restricted to $x<9.95$ m; exit column $x=10.35$ m; exit state $x\\ge10$ m",
     [("experiments/BAR/bar.py", r"xs < 9\.95"), ("experiments/BAR/gate.py", r"^X_EXIT = 10\.35")], "not stated", ""),
    ("V6", "event", "Abreast (second trap)", "neighbour on the other side of the axis and blocker $>0.3$ m from it",
     [("experiments/fixan/fix_reg.py", r'g\["opposite_sides"\] and g\["axis_dist_b_m"\] > 0\.3')], "not stated (Sect. 6.1)", ""),
    ("V7", "event", "A-4 velocity jump / twin stop", "$|\\Delta\\mathbf v_{\\rm ORCA}|>10^{-3}$ m/s; twins followed to separation $10^{-3}$ m",
     [("experiments/fixan/fix_a4.py", r"^JUMP = 1e-3"), ("experiments/fixan/fix_a4.py", r"sep_stop=1e-3")], "not stated (Sect. 6.1)", ""),
    ("V8", "event", "Replay", "$10^{-9}$ m Gaussian per coordinate, 5 replays (seeds 900--904)",
     [(RL, r"rng\.normal\(0, 1e-9"), ("experiments/E2/e2_quench.py", r"PERTURB_SEEDS = \(900, 901, 902, 903, 904\)")],
     "Sect. 3.5", ""),
    # ---------------- horizons
    ("H1", "horizon", "Quench window (E2, E7b, velocity coupling, N1, A-1/A-2/A-6)", "120 s",
     [("experiments/E2/e2_quench.py", r"^T_Q = 120\.0"), ("experiments/E7b/e7b_quench.py", r"^T_Q = 120\.0"),
      ("experiments/velorca/velorca.py", r"^T_Q = 120\.0"), ("experiments/runs3/N1.py", r"e2_quench\.T_Q"), (RL, r'job\.get\("t_q", 120\.0\)')],
     "Sect. 3.4; Sects. 5.3, 6.1, 6.3; Figs. 6, 7; Table 3",
     "every held force-coupled ORCA pair run (either solver) still moves at 120 s (audit)"),
    ("H2", "horizon", "Keystone test (K1, K2, K1b; E1 library, E6 and velocity-coupling failures)", "120 s with stop D2",
     [("experiments/E1/keystone.py", r"^T_Q = 120\.0"), ("experiments/E6/keystone_e6.py", r"^T_Q = 120\.0")],
     "not stated (Sect. 5.1)", ""),
    ("H3", "horizon", "Second-trap force trace", "20 s (or blocker exit)", [("experiments/E2/second_trap.py", r"^T_TRACE = 20\.0")],
     "not stated (Sect. 6.1 'In held runs')", ""),
    ("H4", "horizon", "Static pair relaxation (fold prediction)", "120 s", [("experiments/E7b/e7b_static.py", r'"t_q": 120\.0')],
     "Sect. 5.3 (only the quench's 120 s)", ""),
    ("H5", "horizon", "N6 near-fold quench", "300 s, no stationary stop", [("experiments/runs3/N6.py", r"^T_Q = 300\.0")],
     "not in the text (RunNSixQuench* macros unused)", "longer than every other quench"),
    ("H6", "horizon", "Whole runs (E1 library, E5, E6, E7, E7b library, N2, velocity coupling)", "600 s cap",
     [("experiments/E1/e1_library.py", r"^T_MAX = 600\.0"), (RL, r'job\.get\("t_max", 600\.0\)'),
      ("experiments/E5/e5_sweep.py", r'"t_max": 600\.0'), ("experiments/E6/e6.py", r'"t_max": 600\.0'),
      ("experiments/E7/e7_cells.py", r'"t_max": 600\.0'), ("experiments/E7b/e7b_lib.py", r'"t_max": 600\.0'),
      ("experiments/runs3/N2.py", r'"t_max": 600\.0'), ("experiments/velorca/velorca.py", r'"t_max": 600\.0')],
     "Sects. 6.2, 8 (600 s); not stated for E1, E5, E7 (Sects. 5.1, 5.2)", ""),
    ("H7", "horizon", "Arch runs (arch.py, N5)", "600 s cap, stop D1", [("experiments/arch/arch.py", r"^T_MAX = 600\.0"),
                                                                 ("experiments/runs3/N5.py", r"^T_MAX = 600\.0")], "Sect. 5.4", ""),
    ("H8", "horizon", "CroMa model runs (E10)", "600 s cap, stop D1", [("experiments/E10/e10_croma.py", r"^T_MAX = 600\.0")],
     "Sect. 7", ""),
    ("H9", "horizon", "E4 escape censoring (and N3)", "300 s at $\\beta=1.5$, 2.5; 900 s at 3.5",
     [("experiments/E4/e4_escape.py", r"^T_CENS = \{1\.5: 300\.0, 2\.5: 300\.0, 3\.5: 900\.0\}"), ("experiments/runs3/N3.py", r"import e4_escape")],
     "Sect. 5.2", ""),
    ("H10", "horizon", "E3 escape censoring", "300 s; 900 s for per-step noise at $\\Delta t=0.02$ s; ORCA (RVO2) 300 s",
     [("experiments/E3/e3_dt.py", r"N_REP, T_CENS, T_CENS_LONG, DT_REF = 20, 300\.0, 900\.0"),
      ("experiments/E3/e3_dt.py", r'tc = T_CENS_LONG if \(mode == "per_step" and dtv == 0\.02\)')],
     "not stated (Sect. 6.1)", "censoring differs by cell; ORCA 'frees the same snapshots at every dt' holds within 300 s"),
    ("H11", "horizon", "Escape runner default", "300 s", [(RL, r'job\.get\("t_cens", 300\.0\)')], "---", ""),
    ("H12", "horizon", "Velocity-moment window (T3 check, stored moments)", "after 2 s burn-in while $x<9.95$ m; T3 runs 60 s at $\\beta=6$; cells with $\\ge200$ samples",
     [(RL, r"if sim\.time - t0 > 2\.0 and x < 9\.95"), ("experiments/E3/t3_variance.py", r"^BETA, T_RUN, BURN = 6\.0, 60\.0, 2\.0")],
     "not stated (Sect. 4.4)", ""),
    ("H13", "horizon", "E4 noise-setting floor", "$\\Delta U\\ge0.1$ J", [("experiments/E4/e4_escape.py", r"DU_FLOOR = 20, 60, 20, 105, 0\.01, 0\.1")],
     "Sect. 5.2", ""),
    # ---------------- CroMa estimator
    ("C1", "CroMa", "Waiting zone", "0.3--2.5 m before the entrance, $|y-y_c|<2$ m",
     [("experiments/pilot/w28_croma.py", r"zone = \(dx > 0\.3\) & \(dx < 2\.5\) & \(np\.abs\(P\[:, 1\] - y_c\) < 2\.0\)")], "Sect. 7", ""),
    ("C2", "CroMa", "Slow-sample cut", "local-mean speed (self and neighbours within 0.74 m) $<0.3$ m/s",
     [("experiments/pilot/w28_croma.py", r"mean\(axis=0\)\) >= 0\.3"), ("experiments/pilot/w28_croma.py", r"nb = \(d < 0\.74\) & \(d > 0\)")],
     "Sect. 7", ""),
    ("C3", "CroMa", "Velocity smoothing", "Savitzky--Golay, 37 frames (1.48 s) at 25 Hz", [("experiments/pilot/w28_croma.py", r"^WIN = 37")],
     "not stated (Sect. 7)", ""),
    ("C4", "CroMa", "Long gap", "gap between passages $>2$ s", [("experiments/E10/analyze.py", r"gaps > 2 s")], "Sect. 7", ""),
]


def audit():
    sel = {s["tag"]: s for s in json.load(open(os.path.join(revlib.DERIVED, "selection.json")))["E2"]["snapshots"]}

    def rows(path):
        p = os.path.join(revlib.DATA, path)
        return [json.loads(x) for x in open(p)] if os.path.exists(p) else []

    out = {}

    def quench_audit(name, rr, ev):
        det = [r for r in rr if r.get("deterministic") and r.get("perturb") is None]
        held = [r for r in det if ev(r) is None]
        freed_t = [ev(r) for r in det if ev(r) is not None]
        out[name] = {"n_det_unperturbed": len(det), "n_held": len(held),
                     "held_stationary_stop": sum(bool(r.get("stationary_stop")) for r in held),
                     "held_ran_to_window": sum(not r.get("stationary_stop") for r in held),
                     "n_freed": len(freed_t), "latest_free_s": max(freed_t) if freed_t else None,
                     "freed_after_100s": sum(t > 100 for t in freed_t), "by_arm": {}}
        for r in held:
            a = r.get("arm", r.get("perturbation"))
            c = out[name]["by_arm"].setdefault(a, {"held": 0, "held_ran_to_window": 0})
            c["held"] += 1
            c["held_ran_to_window"] += int(not r.get("stationary_stop"))

    def blocker_t(r, key="snap"):
        tag = r[key].replace(".pkl", "")
        b = r.get("blocker", sel.get(tag, {}).get("blocker"))
        t = r["exits"].get(str(b), r["exits"].get(b))
        return t if t is not None and t <= 120.0 + 1e-9 else None

    def first_t(r):
        t = r.get("first_t")
        return t if r.get("freed", r.get("n_freed", 0) > 0) and t is not None and t <= 120.0 + 1e-9 else None

    quench_audit("E2", rows("E2/e2_quench.jsonl"), blocker_t)
    quench_audit("E7b", rows("E7b/e7b_quench.jsonl"), first_t)
    quench_audit("velorca_lone", rows("velorca/lone.jsonl"), blocker_t)
    quench_audit("velorca_pair", rows("velorca/pair.jsonl"), first_t)

    for name, path in (("E3", "E3/e3_dt.jsonl"), ("E4", "E4/e4_escape.jsonl"), ("N3", "N3/n3.jsonl")):
        rr = rows(path)
        by = {}
        for r in rr:
            c = by.setdefault(f"t{int(r['t_cens'])}", {"n": 0, "censored": 0, "latest_escape_s": 0.0})
            c["n"] += 1
            c["censored"] += int(r["censored"])
            if r["escape_t"] is not None:
                c["latest_escape_s"] = max(c["latest_escape_s"], r["escape_t"])
        for c in by.values():
            c["censored_frac"] = revlib.sig(c["censored"] / c["n"], 2) if c["n"] else None
        out[name] = by

    for name, path in (("E6a_C3_rvo2", "E6/e6a.jsonl"), ("E6b_noise", "E6/e6b.jsonl")):
        rr = rows(path)
        out[name] = {"n": len(rr), "complete": sum(r["complete"] for r in rr), "deadlock": sum(r["deadlock"] for r in rr),
                     "capped_600s": sum(r["capped"] for r in rr)}
    return out


def tex_escape(s):
    return s.replace("_", "\\_").replace("&", "\\&")


def write_tex(rows, path):
    L = ["% A15 thresholds table (generated by experiments/revision/A15_thresholds.py; not \\input anywhere)",
         "\\begin{tabular}{@{}l>{\\raggedright\\arraybackslash}p{3.2cm}>{\\raggedright\\arraybackslash}p{4.6cm}"
         ">{\\raggedright\\arraybackslash}p{3.4cm}>{\\raggedright\\arraybackslash}p{2.6cm}@{}}",
         "\\toprule", "ID & Quantity & Value and rule & Code & Paper \\\\", "\\midrule"]
    grp = None
    for r in rows:
        if r["group"] != grp:
            if grp is not None:
                L.append("\\addlinespace")
            grp = r["group"]
        code = "; ".join("\\texttt{" + tex_escape(c.replace("experiments/", "").replace("code/sim/", "sim/")) + "}"
                         for c in r["code"][:3]) + ("; \\ldots" if len(r["code"]) > 3 else "")
        paper = tex_escape(r["paper"]) + (" \\textbf{[!]}" if r["flag"] else "")
        L.append(f"{r['id']} & {tex_escape(r['quantity'])} & {r['value']} & {code} & {paper} \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    with open(path, "w") as f:
        f.write("\n".join(L))


def main():
    rows = []
    for (i, g, q, v, locs, paper, flag) in ROWS:
        rows.append({"id": i, "group": g, "quantity": q, "value": v, "code": [loc(p, rx) for p, rx in locs],
                     "paper": paper, "flag": flag})
    out = {"n_rows": len(rows), "rows": rows, "audit": audit()}
    print(revlib.out_json("A15", out))
    write_tex(rows, os.path.join(R, "experiments", "revision", "notes", "A15_table.tex"))
    for r in rows:
        print(r["id"], r["code"][0], "|", r["paper"])
    print(json.dumps(out["audit"], indent=1))


if __name__ == "__main__":
    main()
