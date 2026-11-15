"""T6f analysis: lone release 1 m upstream for the 200 positive-margin agents (data/revision4/T6f/t6f.jsonl) and the
energy balance against the outcome. Rule tested: pass iff KE at x_rest (entry into the region where the wall force
exceeds the drive) exceeds the adverse work A = int (back - D) dx over that region (drag inside the region ignored).
Also the B1 rest-state release (data/derived/rev_B1.json pos_rest: 0 of 200 pass) for reference.
Output: data/derived/rev4_T6f.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import DATA, DERIVED, np, wilson  # noqa: E402


def main():
    R = sorted([json.loads(l) for l in open(os.path.join(DATA, "revision4", "T6f", "t6f.jsonl"))], key=lambda r: r["margin"])
    b1 = json.load(open(os.path.join(DERIVED, "rev_B1.json")))["pos_rest"]
    k = sum(r["passed"] for r in R)
    p, lo, hi = wilson(k, len(R))
    ke = np.array([r["at_x_rest"]["KE_J"] if r["at_x_rest"] else 0.0 for r in R])
    A = np.array([r["adverse_work_J"] for r in R])
    ps = np.array([r["passed"] for r in R])
    rule = ke > A
    low = R[:10]
    out = {"script": "experiments/revision4/T6f_analyze.py", "doc": __doc__, "n": len(R), "passed": k, "frac": p,
           "ci95": [lo, hi], "rest_release_B1": {"n": b1["n"], "passed": b1["passed"], "margin_range_N": b1["margin_range_N"]},
           "smallest_positive_margin_N": R[0]["margin"], "largest_margin_N": R[-1]["margin"],
           "max_margin_passed_N": max(r["margin"] for r in R if r["passed"]),
           "min_margin_held_N": min(r["margin"] for r in R if not r["passed"]),
           "rule_ke_gt_A": {"agree": int((rule == ps).sum()), "n": len(R),
                            "pass_but_rule_no": int((ps & ~rule).sum()), "held_but_rule_yes": int((~ps & rule).sum())},
           "KE_at_x_rest_J": {"min": float(ke.min()), "median": float(np.median(ke)), "max": float(ke.max())},
           "smallest_margins": [{"margin_N": r["margin"], "passed": r["passed"], "r": r["r"], "v0": r["v0"], "tau": r["tau"],
                                 "drive_N": r["D_N"], "x0": r["x0"], "x_rest": r["x_rest"], "x_peak": r["x_peak_grid"],
                                 "speed_at_x_rest": r["at_x_rest"]["speed"] if r["at_x_rest"] else None,
                                 "KE_at_x_rest_J": r["at_x_rest"]["KE_J"] if r["at_x_rest"] else None,
                                 "speed_at_x_peak": r["at_x_peak"]["speed"] if r["at_x_peak"] else None,
                                 "KE_at_x_peak_J": r["at_x_peak"]["KE_J"] if r["at_x_peak"] else None,
                                 "adverse_work_J": r["adverse_work_J"], "dUw_release_to_peak_J": r["dUw_x0_to_peak_J"],
                                 "ledger_to_xmax": r["ledger_to_xmax"]} for r in low]}
    lw = out["smallest_margins"]
    for key in ("speed_at_x_peak", "KE_at_x_peak_J", "dUw_release_to_peak_J"):
        v = [x[key] for x in lw if x[key] is not None]
        out[f"smallest10_{key}_range"] = [min(v), max(v)]
    print(rev4lib.out_json("T6f", out))
    print({k2: v for k2, v in out.items() if k2 not in ("doc", "smallest_margins")})


if __name__ == "__main__":
    main()
