"""Flat headline numbers of revision 7 (session C5) from the rev7_*.json task outputs, read by the macro registry
notes/C5_items/revision7.yaml (prefix Rz). Output: data/derived/rev7_headline.json."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)


def D(n):
    return json.load(open(f"data/derived/rev7_{n}.json"))


t1, t2, t3, t4, t5, t10, w = D("T1"), D("T2"), D("T3"), D("T4"), D("T5"), D("T10"), D("whole")
H = {}
pa, e4 = t2["pooled_all"], t2["pooled_E4_ten"]
H.update(t2_ratio=pa["ratio"], t2_lo=pa["ci95"][0], t2_hi=pa["ci95"][1], t2_n=pa["n"], t2_events=pa["events"],
         t2_restarts=pa["restarts"], t2_cover1=pa["n_ci_covers_1"], t2_cover_theory=pa["n_ci_covers_theory"],
         t2_nu_langer_med=pa["nu_over_langer_median"], t2_theory_med=pa["theory_ratio_median"],
         t2_e4_ratio=e4["ratio"], t2_e4_lo=e4["ci95"][0], t2_e4_hi=e4["ci95"][1],
         t2_new_ratio=t2["pooled_new_46"]["ratio"])
H.update(t3_tst=t3["pooled_ratio_tst"], t3_kappa=t3["pooled_ratio_kappa"], t3_full=t3["pooled_ratio_full"])
for k, lv in t4["levels"].items():
    s = k.replace(".", "p")
    H.update({f"t4_{s}_a": lv["pred_a"], f"t4_{s}_c": lv["pred_c_T2"], f"t4_{s}_obs": lv["obs"],
              f"t4_{s}_lo": lv["obs_lo"], f"t4_{s}_hi": lv["obs_hi"]})
lo = t5["lone"]
H.update(t5_heldout_med=lo["logit_heldout_error"]["median"], t5_heldout_lo=lo["logit_heldout_error"]["lo95"],
         t5_heldout_hi=lo["logit_heldout_error"]["hi95"])
for a in ("C3_pub", "C3_rvo2", "drive_only", "C1", "constraint_only_rvo2"):
    H[f"t1_{a}_freed"] = t1["arms"][a]["freed_end"]
    H[f"t1_{a}_moving600"] = t1["arms"][a]["moving_600"]
H["t1_legacy_rvo2_p"] = t1["tests"]["legacy_vs_rvo2"]["at_end"]["p"]
H["t1_drive_rvo2_p"] = t1["tests"]["drive_vs_rvo2"]["at_end"]["p"]
for a in ("drive", "tauprime", "rvo2", "sfm"):
    H[f"t7_{a}_changes"] = w["T7"][a]["outcome_changes"]
    H[f"t7_{a}_replay_k"] = w["T7"][a]["replay_k"]
c8 = w["T8"]["completion"]
H.update(t8_k=c8["k"], t8_n=c8["n"], t8_lo=c8["ci95"][0], t8_hi=c8["ci95"][1], t8_rest=c8["at_rest"])
for s in ("lone_keystone", "lone_keystone_second_trap", "other_second_trap"):
    r = t10["strata"][s]["R1"]
    H[f"t10_{s}_freed"], H[f"t10_{s}_disagree"], H[f"t10_{s}_n"] = r["freed"], r["n_disagree"], r["n_done"]
H["t10_pairs_freed"] = t10["pairs"]["R1_u"]["freed"]
c11 = w["T11"]["completion"]["R1"]
H.update(t11_n=c11["n"], t11_k=c11["k"], t11_hi=c11["ci95"][1], t11_moving=c11["moving_600"])
json.dump(H, open("data/derived/rev7_headline.json", "w"), indent=1, default=float)
print(len(H))
