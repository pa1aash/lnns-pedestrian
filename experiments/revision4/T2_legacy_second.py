"""T2: force-coupled ORCA with the legacy solver at the second traps (no new runs).

Inputs (read only): data/E2/e2_quench.jsonl (the 26 screening-set second traps) and data/revision/A5/a5_quench.jsonl
(the other 134 of the 160 deadlock-set second traps). Both use the same quench protocol for every arm (E2 arm
definitions, experiments/E2/e2_quench.py: CF union arm flags, dt = 0.01 s, 120 s window, deterministic arms stop once
stationary, unperturbed run per snapshot): C3_pub (force-coupled ORCA, legacy solver), C3_rvo2 (RVO2 solver) and
drive_only (ORCA's drive part). Outcome: the keystone-test blocker exits within 120 s (A5x_analyze.load, unchanged).
Per set (screening 26, deadlock 160): freed counts with Wilson 95% intervals; paired exact McNemar tests legacy vs
RVO2 and legacy vs drive part (two-sided, discordant counts), Holm over the two tests within each set; replay changes
(5 replays, perturbation seeds 900-904) are copied from the same records. Every count is asserted equal to
data/derived/rev_A5x.json.
Output: data/derived/rev4_T2.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402
from rev4lib import DERIVED, holm, mcnemar_exact, pdisp, wilson  # noqa: E402
import A5x_analyze as A  # noqa: E402


def main():
    runs, tags = A.load()
    ref = json.load(open(os.path.join(DERIVED, "rev_A5x.json")))
    out = {"script": "experiments/revision4/T2_legacy_second.py", "doc": __doc__, "sets": {}}
    for name, g in (("screening", "E2"), ("deadlock", "pooled")):
        T = tags[g]
        f = {a: {t: runs[(t, a)]["u"] for t in T} for a in ("C3_pub", "C3_rvo2", "drive_only")}
        d = {"n": len(T)}
        for a in f:
            k = sum(f[a].values())
            p, lo, hi = wilson(k, len(T))
            d[a] = {"freed": k, "frac": p, "ci95": [lo, hi]}
            assert k == ref["rates"][g][a]["freed"], (g, a)
        tests = {}
        for nm, a, b in (("legacy_vs_rvo2", "C3_pub", "C3_rvo2"), ("legacy_vs_drive", "C3_pub", "drive_only")):
            b1 = sum(f[a][t] and not f[b][t] for t in T)
            c1 = sum(f[b][t] and not f[a][t] for t in T)
            p = mcnemar_exact(b1, c1)
            tests[nm] = {"first": a, "second": b, "disc_first_only": int(b1), "disc_second_only": int(c1), "p": p,
                         "p_disp": pdisp(p), "effect": (sum(f[a].values()) - sum(f[b].values())) / len(T)}
        ph = holm([tests[k]["p"] for k in tests])
        for (k, v), q in zip(tests.items(), ph):
            v["p_holm"], v["p_holm_disp"] = q, pdisp(q)
        r1 = ref["paired"][g]["C3_pub_vs_C3_rvo2"]
        assert (r1["disc_first_only"], r1["disc_second_only"]) == (tests["legacy_vs_rvo2"]["disc_first_only"],
                                                                   tests["legacy_vs_rvo2"]["disc_second_only"])
        r2 = ref["paired"][g]["drive_only_vs_C3_pub"]
        assert (r2["disc_first_only"], r2["disc_second_only"]) == (tests["legacy_vs_drive"]["disc_second_only"],
                                                                   tests["legacy_vs_drive"]["disc_first_only"])
        d["tests"] = tests
        d["legacy_replay"] = {k2: ref["rates"][g]["C3_pub"][k2] for k2 in ("replays", "replays_changed", "snapshots_changed")}
        out["sets"][name] = d
    print(rev4lib.out_json("T2", out))
    for n, d in out["sets"].items():
        print(n, d["n"], {a: d[a]["freed"] for a in ("C3_pub", "C3_rvo2", "drive_only")},
              {k: (v["disc_first_only"], v["disc_second_only"], round(v["p"], 4), round(v["p_holm"], 4)) for k, v in d["tests"].items()})


if __name__ == "__main__":
    main()
