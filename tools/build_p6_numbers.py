#!/usr/bin/env python3
"""Numbers for paper session P6 that the revision-7 headline file (data/derived/rev7_headline.json) does not hold.

Reads only stored outputs: the rev7_*.json task files, the run records and earlier derived files. Runs no simulation.
Writes data/derived/p6_numbers.json, read by paper/registry/p6.yaml (prefix Rz).

Sources, by block:
  t2     rev7_T2.json: attempt frequency over the damped Langer prefactor (nu_hat_over_langer), gamma/omega_b and the
         Weibull shapes of the beta = 5 and 7 cells (weibull_beta5_7), over the 56 snapshots.
  t4     rev7_T4.json: time-step prediction at beta_0 = 2.5 with the span barrier scaled by the three-snapshot slope 0.89.
  t1     rev7_T1.json (freed counts, Wilson intervals, McNemar legacy vs RVO2) and the displacement of the members of
         held pairs between 120 s (data/E7b/e7b_quench.jsonl, unperturbed) and 600 s (data/revision7/T1/t1_pair_rest.jsonl).
  t5     rev7_T5.json: split-sample held-out error (freed or completed fraction), lone keystones and whole runs.
  t7     rev7_whole.json T7: largest change of a completion count between original and replay.
  t8     rev7_whole.json T8: throttled drive part, McNemar counts and failure classes.
  t10    rev7_T10.json: R1/R2 quenches against the rest-drive criterion; the eight "predicted held, freed" cases split
         into neighbour left first (first exit not the blocker), small margin (< 5 N) and the rest.
  t11    rev7_whole.json T11: R1/R2 whole runs against force-coupled ORCA (RVO2) on the same seeds.
  b      sample size of the whole-run equivalence test, n = z^2 2p(1-p)/delta^2 with the plan's z = 1.645 + 1.282,
         p = 0.575, delta = 0.15 (pedestrian-abs-plan wave2/SIGNATURES.md:6; plan/FINAL_PLAN.md:257).
  d      selection.json E2: lone keystones with only the blocker left (n_resid = 1).
  g      combined target speed of drive plus drive part, v_t/v0 = (tau + W tau_o)/(tau + tau_o), Weidmann W at
         rho = 2.3 m^-2 with the model's gamma and rho_max (data/params/model.yaml), tau_o = 0.5 s, tau 0.4-0.6 s.
  h      data/E7/e7_cells.jsonl and data/E7/keystone.jsonl: the lone keystone of the all-walls B_w = 0.04 m cell and
         the member counts of the jamb-range deadlocks.
  c      data/E4/e4_extension.json (skipped full-condition barrier, seed 60) and e7b_barrier.jsonl (smallest pair barrier).
  misc   absolute value of the seed-170 adjacent rest state (rev5_X1.json); friction factors (rev5_X2.json).
  sets   seeds and sizes of the run sets in the run-set table, from the run records.
"""
import json
import math
import statistics as st
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
DER = D / "derived"


def jl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def jd(name):
    return json.loads((DER / name).read_text())


out = {}

# ---- t2: attempt frequency, friction ratio, Weibull shapes (56 snapshots)
t2 = jd("rev7_T2.json")
snaps = [s for s in t2["snapshots"].values() if s.get("nu_hat_over_langer") is not None]
nl = [s["nu_hat_over_langer"] for s in snaps]
go = [s["gamma_over_omega_b"] for s in snaps]
out["t2"] = {"n": len(snaps), "nu_langer_med": st.median(nl), "nu_langer_min": min(nl), "nu_langer_max": max(nl),
             "gamma_omega_med": st.median(go),
             "weibull_med": t2["weibull_beta5_7"]["median"], "weibull_min": t2["weibull_beta5_7"]["range"][0],
             "weibull_max": t2["weibull_beta5_7"]["range"][1], "weibull_cells": t2["weibull_beta5_7"]["n_cells"]}

# ---- t4: prediction at beta_0 = 2.5 with the three-snapshot slope ratio
t4 = jd("rev7_T4.json")
out["t4"] = {"b2p5_pred_c_A3": t4["levels"]["2.5"]["pred_c_A3"], "b1p5_pred_c_A3": t4["levels"]["1.5"]["pred_c_A3"]}

# ---- t1: pair standoffs at 600 s
t1 = jd("rev7_T1.json")
arms = {"legacy": "C3_pub", "rvo2": "C3_rvo2", "drive": "drive_only", "constraint": "constraint_only_rvo2",
        "constraint_legacy": "constraint_only_pub", "sfm": "C1"}
t1o = {}
for k, a in arms.items():
    r = t1["arms"][a]
    t1o[k] = {"freed": r["freed_end"], "lo": r["wilson95_end"][1], "hi": r["wilson95_end"][2],
              "freed_after_120": len(r["freed_after_120"]), "rest_end": r["rest_end"], "moving_600": r["moving_600"]}
t1o["freed_after_120_all"] = sum(len(r["freed_after_120"]) for r in t1["arms"].values())
t1o["came_to_rest_after_120_all"] = sum(r["rest_end"] - r["rest_120"] for r in t1["arms"].values())
lt = t1["tests"]["legacy_vs_rvo2"]["at_end"]
t1o["legacy_rvo2"] = {"a": lt["a_only"], "b": lt["b_only"], "p": lt["p"]}
q120 = {}
for r in jl(D / "E7b" / "e7b_quench.jsonl"):
    if r.get("perturb") is None and r.get("arm") in ("C3_pub", "C3_rvo2") and r.get("final_pos"):
        q120[(r["snap"], r["arm"])] = r["final_pos"]
disp = {}
for r in jl(D / "revision7" / "T1" / "t1_pair_rest.jsonl"):
    if r.get("perturb") is not None or r["freed"] or not r.get("final_pos"):
        continue
    a = q120.get((r["snap"], r["arm"]))
    if a is None:
        continue
    disp.setdefault(r["arm"], []).append(max(math.dist(a[m], r["final_pos"][m]) for m in r["final_pos"] if m in a))
t1o["disp_cm"] = {"legacy_med": 100 * st.median(disp["C3_pub"]), "rvo2_med": 100 * st.median(disp["C3_rvo2"]),
                  "max": 100 * max(max(v) for v in disp.values()), "n": sum(len(v) for v in disp.values())}
out["t1"] = t1o

# ---- t5: split-sample matching
t5 = jd("rev7_T5.json")
out["t5"] = {"lone_med": t5["lone"]["logit_heldout_error"]["median"], "lone_lo": t5["lone"]["logit_heldout_error"]["lo95"],
             "lone_hi": t5["lone"]["logit_heldout_error"]["hi95"], "lone_sigma": t5["lone"]["logit_full"]["sigma"],
             "whole_med": t5["whole"]["heldout_error"]["median"], "whole_lo": t5["whole"]["heldout_error"]["lo95"],
             "whole_hi": t5["whole"]["heldout_error"]["hi95"], "lone_orca_freed": t5["lone"]["orca_freed"],
             "lone_n": t5["lone"]["n"]}

# ---- t7, t8, t11: whole runs
w = jd("rev7_whole.json")
t7 = w["T7"]
out["t7"] = {"max_k_shift": max(abs(t7[a]["replay_k"] - t7[a]["orig_k"]) for a in ("drive", "tauprime", "rvo2", "sfm")),
             "drive_tau_agree": t7["drive_vs_tauprime"]["orig_agree_186"]}
t8 = w["T8"]
out["t8"] = {"k": t8["completion"]["k"], "n": t8["completion"]["n"], "lo": t8["completion"]["ci95"][0],
             "hi": t8["completion"]["ci95"][1], "at_rest": t8["completion"]["at_rest"],
             "lone": t8["classes"]["at_rest"]["lone_keystone"],
             "second": t8["classes"]["at_rest"]["lone_keystone_second_trap"],
             "collective": t8["classes"]["at_rest"]["collective"] + sum(t8["classes"]["moving"].values())}
for k in ("veff_vs_drive", "veff_vs_tauprime", "veff_vs_rvo2"):
    x = t8["tests"][k]
    out["t8"][k] = {"a": x["first_only"], "b": x["second_only"], "p": x["p"]}
t11 = w["T11"]
out["t11"] = {"n": t11["n_seeds"], "k": t11["completion"]["R1"]["k"], "k2": t11["completion"]["R2"]["k"],
              "hi": t11["completion"]["R1"]["ci95"][1], "moving": t11["completion"]["R1"]["moving_600"]
              + t11["completion"]["R2"]["moving_600"], "rvo2_k": t11["ref"]["rvo2"]["k"],
              "vs_rvo2_a": t11["tests"]["R1_vs_rvo2"]["first_only"], "vs_rvo2_b": t11["tests"]["R1_vs_rvo2"]["second_only"],
              "vs_rvo2_p": t11["tests"]["R1_vs_rvo2"]["p"]}
seeds11 = sorted({r["seed"] for r in jl(D / "revision7" / "T11" / "t11_whole.jsonl")})
out["t11"]["seed_lo"], out["t11"]["seed_hi"] = seeds11[0], seeds11[-1]

# ---- t10: R1/R2 quenches against the rest-drive criterion
t10 = jd("rev7_T10.json")["strata"]
lk, st2, ot = t10["lone_keystone"]["R1"], t10["lone_keystone_second_trap"]["R1"], t10["other_second_trap"]["R1"]
held_freed = [d for d in ot["disagreements"] if not d["pred_freed"] and d["obs_freed"]]
neigh = [d for d in held_freed if d["first_agent"] != d["blocker"]]
small = [d for d in held_freed if d["first_agent"] == d["blocker"] and d["margin_R"] < 5.0]
rest = [d for d in held_freed if d not in neigh and d not in small]
c = ot["confusion"]
out["t10"] = {"lone_freed": lk["freed"], "lone_n": t10["lone_keystone"]["n"], "lone_disagree": lk["n_disagree"],
              "lone_orca_freed": lk["vs"]["C3_rvo2"]["arm_freed"], "lone_drive_freed": lk["vs"]["drive_only"]["arm_freed"],
              "lone_tau_freed": lk["vs"]["tauprime"]["arm_freed"],
              "screen_n": t10["lone_keystone"]["n"] + t10["lone_keystone_second_trap"]["n"],
              "screen_disagree": lk["n_disagree"] + st2["n_disagree"],
              "other_n": t10["other_second_trap"]["n"], "other_disagree": ot["n_disagree"], "other_freed": ot["freed"],
              "other_pred_freed": c["pred_freed_obs_freed"] + c["pred_freed_obs_held"],
              "other_held_freed": len(held_freed), "other_neigh_first": len(neigh), "other_small_margin": len(small),
              "other_small_margin_min": min(d["margin_R"] for d in small), "other_small_margin_max": max(d["margin_R"] for d in small),
              "other_unexplained": len(rest),
              "r1_r2_identical": all(t10[s]["R1_R2_identical_outcome"] == t10[s]["n"] for s in t10)}

# ---- b: sample size of the whole-run equivalence test
z, p, delta = 1.645 + 1.282, 0.575, 0.15
e6 = sorted(r["seed"] for r in jl(D / "E6" / "e6a.jsonl"))
vel = sorted({r["seed"] for r in jl(D / "velorca" / "whole.jsonl") if r["variant"] == "vel"})
out["b"] = {"z": z, "p": p, "delta": delta, "n_formula": z * z * 2 * p * (1 - p) / delta ** 2, "n": len(e6),
            "seed_lo": e6[0], "seed_hi": e6[-1], "vel_seed_lo": vel[0], "vel_seed_hi": vel[-1], "vel_n": len(vel)}

# ---- d: lone keystones with the blocker alone left
sel = jd("selection.json")["E2"]["snapshots"]
lks = [s for s in sel if s["class"] == "lone_keystone"]
out["d"] = {"lone_n": len(lks), "lone_blocker_only": sum(s["n_resid"] == 1 for s in lks)}

# ---- g: combined target speed of drive plus drive part
prm = yaml.safe_load((D / "params" / "model.yaml").read_text())


def find(o, key):
    if isinstance(o, dict):
        if key in o:
            return o[key]
        for v in o.values():
            r = find(v, key)
            if r is not None:
                return r
    return None


gam, rmax, tau_o = find(prm, "weidmann_gamma")["value"], find(prm, "weidmann_rho_max")["value"], find(prm, "tau_orca")["value"]
rho = 2.3
W = min(1.0, max(0.05, 1 - math.exp(-gam * (1 / rho - 1 / rmax))))


def vt(tau):
    return (tau + W * tau_o) / (tau + tau_o)


out["g"] = {"rho": rho, "W": W, "tau": 0.5, "ratio": vt(0.5), "ratio_lo": vt(0.4), "ratio_hi": vt(0.6), "tau_o": tau_o}

# ---- h: wall-range cells
cells = jl(D / "E7" / "e7_cells.jsonl")
ks = {r["job_id"]: r for r in jl(D / "E7" / "keystone.jsonl")}
lone_b004 = [r["seed"] for r in cells if r["cell"] == "B0.04" and r["deadlock"]
             and ks.get(f"B0.04_seed{r['seed']}|K1", {}).get("held")]
jamb = [r for r in cells if r["cell"] == "Bedge0.04" and r["deadlock"]]
three = sorted(r["seed"] for r in jamb if r["n_remaining"] == 3)
assert len(lone_b004) == 1 and len(three) == 2
out["h"] = {"b004_lone_seed": lone_b004[0], "jamb_deadlocks": len(jamb),
            "jamb_two": sum(r["n_remaining"] == 2 for r in jamb), "jamb_three": len(three),
            "jamb_three_seed_a": three[0], "jamb_three_seed_b": three[1]}

# ---- c: barrier thresholds
e4x = json.loads((D / "E4" / "e4_extension.json").read_text())["skipped_no_barrier"]
sk = [x for x in e4x if x["cond"] == "full"]
assert len(sk) == 1
bar = []
for r in jl(D / "E7b" / "e7b_barrier.jsonl"):
    acc = [ch["dU"] for ch in r["channels"].values() if ch.get("accepted") and ch.get("dU") is not None]
    if acc:
        bar.append({"dU": min(acc), "snap": r["snap"]})
bmin = min(bar, key=lambda r: r["dU"])
out["c"] = {"skip_seed": int(sk[0]["tag"].split("seed")[1]), "skip_dU": sk[0]["dU"],
            "pair_min_dU": bmin["dU"], "pair_min_seed": int(bmin["snap"].split("seed")[1].split(".")[0]), "pair_n": len(bar)}

# ---- misc
x1 = jd("rev5_X1.json")["paths"]["E1b_seed170|full"]
x2 = jd("rev5_X2.json")["per_dt"]
out["misc"] = {"s170_rest_below": abs(x1["deepest_min_E_M_J"]),
               "friction_dt01": x2["dt0p01"]["C1_cf_sig"]["friction_factor"],
               "friction_dt005": x2["dt0p005"]["C1_cf_sig"]["friction_factor"],
               "friction_dt01_overlap_m": x2["dt0p01"]["C1_cf_sig"]["max_overlap_m"]}

# ---- sets: seeds and sizes of the run sets in the table
def span(rows):
    s = sorted({r["seed"] for r in rows})
    return {"lo": s[0], "hi": s[-1], "n": len(s)}


e1 = jl(D / "E1" / "E1_runs.jsonl")
e5 = [r for r in jl(D / "E5" / "e5b.jsonl")]
sets = {
    "deadlock": span([r for r in e1 if r["mode"] == "E1b"]),
    "cells": span([r for r in cells]),
    "pairlib": span(jl(D / "E7b" / "e7b_lib.jsonl")),
    "whole": span(jl(D / "E6" / "e6a.jsonl")),
    "first100": span([r for r in jl(D / "velorca" / "whole.jsonl") if r["variant"] == "vel"]),
    "legacy": span(jl(D / "E6" / "e6p.jsonl")),
    "noise": span(e5),
    "croma": span(jl(D / "revision" / "D3" / "d3_croma.jsonl")),
    "replace": {"lo": out["t11"]["seed_lo"], "hi": out["t11"]["seed_hi"], "n": out["t11"]["n"]},
}
sets["noise"]["levels"] = len({r["sigma"] for r in e5})
sets["cells"]["n_cells"] = len({r["cell"] for r in cells})
sets["pairlib"]["runs"] = len(jl(D / "E7b" / "e7b_lib.jsonl"))
out["sets"] = sets

(DER / "p6_numbers.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print("wrote", DER / "p6_numbers.json")
