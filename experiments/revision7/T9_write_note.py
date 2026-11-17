"""Task 9: writes notes/C5_items/prereg_replace.md from data/derived/rev7_T9_prereg.json (T9_prereg.py) and adds the
static margins of the 134 other second traps of the deadlock set (E1 library attributes, same rule)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402

os.chdir(L.ROOT)
J = "data/derived/rev7_T9_prereg.json"
d = json.load(open(J))
ks = json.load(open("data/derived/E1_keystone.json"))["modes"]["E1b"]["per_snapshot"]
sel = {s["seed"] for s in json.load(open("data/derived/selection.json"))["E2"]["snapshots"]}
e1 = {r["seed"]: r for r in L.load_runs("data/E1/E1_runs.jsonl") if r["mode"] == "E1b"}
M, c0 = 80.0, d["chi0"]
oth = []
for x in ks:
    if x["class"] != "lone_keystone_second_trap" or x["seed"] in sel:
        continue
    a = e1[x["seed"]]["attrs"][x["blocker"]]
    g = a["margin_C1"] + M * a["v0"] / a["tau"]
    D1 = (1 - c0) * M * a["v0"] / a["tau"] + c0 * M * a["v0"] / 0.5
    oth.append({"seed": x["seed"], "tag": f"E1b_seed{x['seed']}", "blocker": x["blocker"], "tau": a["tau"],
                "margin_SFM": g - M * a["v0"] / a["tau"], "margin_R": g - D1, "pred_freed": bool(g - D1 < 0)})
assert len(oth) == 134
nfree = sum(o["pred_freed"] for o in oth)
sm = sorted(oth, key=lambda o: o["margin_R"])[:5]
d["other134"] = oth
d["pred"]["second_trap_other134"] = {"n": 134, "R1_static_freed": nfree, "R2_static_freed": nfree, "smallest": sm}
json.dump(d, open(J, "w"), indent=1, default=float)

P, rows = d["pred"], d["rows"]
lk, st = P["lone_keystone"], P["lone_keystone_second_trap"]
bind = [x for x in rows if abs(x["lp_rest"]["R1"]["constraint_lateral_N"]) + abs(x["lp_rest"]["R1"]["constraint_axial_N"]) > 1e-6]
maxlat = max(abs(x["lp_rest"]["R1"]["constraint_lateral_N"]) for x in rows)
maxax = max(abs(x["lp_rest"]["R1"]["constraint_axial_N"]) for x in rows)
held = sorted((x for x in rows if not x["pred_freed"]["R1"]), key=lambda x: x["margin"]["R1"])
fr = [x for x in rows if x["pred_freed"]["R1"]]
taus = [x["tau"] for x in rows]
rat = [x["drive"]["R1"] / x["drive"]["SFM"] for x in rows]
L_ = []
A = L_.append
A("# Pre-registration: replace couplings R1 and R2 (session C5, task 9)")
A("")
A("Written and committed before any R1 or R2 run. Scripts experiments/revision7/T9_prereg.py and T9_write_note.py; "
  "numbers data/derived/rev7_T9_prereg.json. No snapshot dynamics was run to make this prediction.")
A("")
A("## Couplings")
A("Both replace the goal-directed drive instead of adding to it (simulator flag `orca_replace = on`, RVO2 solver):")
A("")
A("F = (1 − χ) F_des + χ m (v_ORCA − v)/τ_ORCA + agent forces + wall forces,  F_des = m (v_eff e − v)/τ,")
A("")
A("χ = w_o(ρ) the ORCA density gate, τ_ORCA = 0.5 s, v_ORCA the RVO2 velocity nearest v_pref.")
A("- **R1**: v_pref = v_eff e (`orca_pref = veff`: the density throttle of Eq. 2 applied to ORCA's preferred speed).")
A("- **R2**: v_pref = v0 e (`orca_pref = v0`).")
A("")
A("Force-coupled ORCA is F_des + χ m (v_ORCA − v)/τ_ORCA; at rest its drive part adds m v0/τ_ORCA to m v_eff/τ. "
  "R1 and R2 keep only (1 − χ) ≈ 3e-4 of F_des, so the rest drive is about m v_pref/τ_ORCA.")
A("")
A("## Rest drive and stuck-alone margin (primary rule)")
A(f"Convention of Eq. (stuck): blocker alone at rest on the door axis, ρ = 0, so v_eff = v0 and χ = χ(0) = {c0:.5f}.")
A("- SFM: D_S = m v0/τ.")
A("- R1: D_1 = (1 − χ) m v_eff/τ + χ m v_eff/τ_ORCA; R2: D_2 = (1 − χ) m v_eff/τ + χ m v0/τ_ORCA (equal at ρ = 0).")
A("- margin = g_max(r) − D, with g_max from the E1 library (margin_C1 + m v0/τ).")
A("- **Prediction: a blocker is freed within 120 s iff its margin is negative, held if positive.**")
A("")
A(f"D_R/D_S = χ τ/τ_ORCA + (1 − χ); with τ in {min(taus):.2f}–{max(taus):.2f} s this is {min(rat):.2f}–{max(rat):.2f}. "
  "Replacing the drive therefore changes the rest drive by at most ±20%, and only a blocker with τ > 0.5 s and an SFM "
  "margin below m v0 (1/τ_ORCA − 1/τ) can be freed. All 60 blockers are held under SFM (positive SFM margin).")
A("")
A("## Predicted counts")
A("| set | n | R1 freed | R2 freed | force-coupled ORCA (RVO2), paper | drive part, paper |")
A("|---|---|---|---|---|---|")
A(f"| lone keystones | 34 | **{lk['R1']['static_freed']}** ({', '.join(lk['R1']['static_freed_tags'])}) | "
  f"**{lk['R2']['static_freed']}** | 30 | 30 |")
A(f"| second traps, screening set | 26 | **{st['R1']['static_freed']}** | **{st['R2']['static_freed']}** | 17 | 24 |")
A(f"| other second traps, deadlock set | 134 | **{nfree}** | **{nfree}** | 121 − 17 = 104 (of 160 − 26) | 149 − 24 = 125 |")
A("")
A("R1 and R2 are predicted identical at every snapshot: the snapshot densities are at most "
  f"{max(x['rho_snap'] for x in rows):.2f} m⁻² (agents within 3 m), where the throttle factor is 1 to 1e-8. "
  "They can differ only in dense crowds (whole runs, task 11).")
A("")
A("## Expected exceptions (stated in advance)")
A(f"1. **Constraint part.** At the rest snapshot the RVO2 velocity equals v_pref for {60 - len(bind)} of the 60 blockers. "
  f"At {len(bind)} ({', '.join(x['tag'] for x in bind)}) a neighbour's half-plane binds and adds a mainly lateral force "
  f"of up to {maxlat:.0f} N with an axial part of at most {maxax:.1f} N; including it changes no predicted outcome "
  "(column LP). In motion the half-planes of agents behind the blocker depend on their velocities, so a moving neighbour "
  "can add or remove axial drive of order tens of newtons. Exceptions, if any, are expected at second traps whose "
  "neighbours move during the quench, not at lone keystones.")
A("2. **Pushes from behind.** Under R1/R2 each agent's own drive changes by its factor χτ/τ_ORCA + (1 − χ). Where an "
  "agent behind is in contact with the blocker, the contact force on the blocker changes with it, so a blocker with a "
  "margin of a few tens of newtons could be pushed through. Expected direction: frees, rarely.")
A("3. **Run-up.** A quench starts at the SFM rest point, where the wall force equals D_S. Under R the blocker moves to "
  "where it equals D_R; with damping ≈ χ m v/τ_ORCA it does not overshoot the peak. A 1-D on-axis integration from the "
  "SFM rest point (code wall force, convex_union rule; diagnostic (c)) frees exactly the statically predicted blocker "
  "and no other. Run-up exceptions are not expected (the 1 m run-up of C3 task 6f does not arise in a quench).")
A(f"4. **Margins near zero.** The only predicted free ({fr[0]['tag']}, R margin {fr[0]['margin']['R1']:+.1f} N, SFM "
  f"{fr[0]['margin']['SFM']:+.1f} N) and the smallest held margin ({held[0]['tag']}, {held[0]['margin']['R1']:+.1f} N) "
  "bound the sensitivity.")
A("")
A("**Falsification criterion.** The rest-drive account holds if at most 2 of the 60 screening-set snapshots disagree "
  "with the prediction (unperturbed run) and each disagreement is traced to exception 1 or 2 in its run record. "
  "Replays (5 per snapshot, 1e-9 m) are compared with the unperturbed outcome. For the 134 other second traps the same rule allows at most 5 disagreements (about 4%, as 2 of 60); margins within ±1 N (E1b_seed85, −0.7 N) are too close to call and are reported separately.")
A("")
A("## Per-snapshot table (screening set)")
A("Forces in N. LP = R1 margin with the RVO2 velocity at the snapshot (constraint part included); constraint = its "
  "axial / lateral force at rest under R1; ρ_s from the agents within 3 m.")
A("")
A("| snapshot | class | τ (s) | v0 (m/s) | g_max | D_S | D_1 = D_2 | margin SFM | margin R1 | margin R2 | LP | "
  "constraint ax / lat | ρ_s (m⁻²) | predicted R1 / R2 |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for x in sorted(rows, key=lambda x: (x["class"] != "lone_keystone", x["margin"]["R1"])):
    cl = "lone keystone" if x["class"] == "lone_keystone" else "second trap"
    p = "freed" if x["pred_freed"]["R1"] else "held"
    lp = x["lp_rest"]["R1"]
    A(f"| {x['tag']} | {cl} | {x['tau']:.3f} | {x['v0']:.2f} | {x['g_max']:.1f} | {x['drive']['SFM']:.1f} | "
      f"{x['drive']['R1']:.1f} | {x['margin']['SFM']:.1f} | {x['margin']['R1']:.1f} | {x['margin']['R2']:.1f} | "
      f"{lp['margin']:.1f} | {lp['constraint_axial_N']:.1f} / {lp['constraint_lateral_N']:.1f} | {x['rho_snap']:.2f} | "
      f"{p} / {p} |")
A("")
A("Other 134 second traps: smallest R margins " + ", ".join(f"{o['tag']} {o['margin_R']:+.1f} N" for o in sm)
  + f"; {nfree} negative, so **{nfree} of 134** are predicted freed under R1 and R2.")
A("")
A("No prediction is made for the 46 pair standoffs: the stuck-alone criterion does not apply there (the pair is held "
  "by the members' contact and the lateral wall forces). Whole runs (task 11): no numerical prediction; because R "
  "removes the extra drive at the lone trap, completions are expected near the SFM's and far below force-coupled ORCA's.")
os.makedirs("notes/C5_items", exist_ok=True)
open("notes/C5_items/prereg_replace.md", "w").write("\n".join(L_) + "\n")
print(nfree, [(o["tag"], round(o["margin_R"], 1)) for o in sm], len(bind))
