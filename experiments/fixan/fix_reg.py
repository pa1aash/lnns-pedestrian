"""Derived counts quoted in the text that the experiment analyses do not store directly.

Reads only data/derived/*.json and writes data/derived/fix_reg.json.
Run from the repository root: python experiments/fixan/fix_reg.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "derived"


def load(name):
    return json.loads((D / name).read_text())


def main():
    out = {}

    # 05-1 (a): blockers with positive stuck-alone margin (all of them stayed held).
    crit = load("E1_chain.json")["stuck_alone_criterion_check"]
    out["criterion"] = {
        "n": crit["n_deadlocks"],
        "agree": crit["agree"],
        "negative_margin": crit["negative_margin_blockers"],
        "positive_margin": crit["n_deadlocks"] - crit["negative_margin_blockers"],
        "method": "positive-margin count = deadlocks minus negative-margin blockers (E1_chain.json)",
    }

    # 05-1 (b): the negative-margin blockers by deadlock size (E1_keystone.json group cases).
    ks = load("E1_keystone.json")
    sizes = []
    for mode in ks.get("modes", {}).values():
        for c in mode.get("collective", {}).get("cases", []):
            n = c.get("n_resid")
            sizes.append(n)
    out["criterion"]["negative_margin_sizes"] = sizes
    out["criterion"]["negative_margin_two_agent"] = sum(1 for s in sizes if s == 2)

    # 06-3: one-neighbour second-trap snapshots in which the two stand abreast across the axis.
    geo = load("E7b_analysis.json")["e_c26"]["second_trap_one_neighbour"]["geometry"]
    abreast = [g for g in geo if g["opposite_sides"] and g["axis_dist_b_m"] > 0.3]
    dists = [g["axis_dist_b_m"] for g in abreast] + [g["axis_dist_o_m"] for g in abreast]
    other = [g for g in geo if g not in abreast]
    out["second_trap_geometry"] = {
        "n": len(geo),
        "abreast": len(abreast),
        "axis_min_m": min(dists),
        "axis_max_m": max(dists),
        "other_behind_m": [abs(g["x_b"] - g["x_o"]) for g in other],
        "other_blocker_axis_m": [g["axis_dist_b_m"] for g in other],
        "method": "abreast = members on opposite sides of the axis with the blocker > 0.3 m from it",
    }

    # 06-5: whole-run failure overlap (E6 identity block).
    idt = load("E6_analysis.json")["identity"]
    out["whole_run_failures"] = {
        "any": idt["both_fail"] + idt["C3_only_fail"] + idt["sigma_only_fail"],
        "one_only": idt["C3_only_fail"] + idt["sigma_only_fail"],
        "both": idt["both_fail"],
        "perm_p": idt["p_perm_jaccard_above_independent"],
        "indep_95": idt["jaccard_independent_95"],
    }

    # 07-1: human gaps longer than 2 s, total over the five runs.
    runs = load("E10_analysis.json")["humans"]["runs"]
    out["human"] = {
        "gaps_over_two_total": sum(r["n_gaps_gt_2s"] for r in runs),
        "unpassed": sum(r["n_ids"] - r["n_pass"] for r in runs),
    }

    (D / "fix_reg.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
