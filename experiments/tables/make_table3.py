#!/usr/bin/env python3
r"""Write paper/tables/table3_matched.tex: the thesis table (C53).

Three matched-control blocks, each a control matched to ORCA on rate against the ORCA arm it matches:
  lone-trap snapshots (E2, lone-keystone stratum): C1 + noise at sigma = 0.07 m/s (the level whose rate
      matches C3 RVO2 there) vs C3 RVO2;
  whole runs (E6): C1 + sigma* vs C3 RVO2;
  pair standoffs (E7b, S9g): bias +b*_pub vs C3 published and +b*_RVO2 vs C3 RVO2.
Columns are the signatures that separate them: rate, paired difference (95% interval), identity (Jaccard
index of the minority outcome set of each block: the unresolved sets for the lone-trap and whole-run blocks,
where most runs free, and the freed sets for the pair block, where fewer than half free), median time to
free, handedness, replay, and the time-step ratio ell (E3).

`make_table3.py derive` writes data/derived/table3_pair.json: the 95% percentile bootstrap interval of the
pair-block paired rate difference (bias +b* minus ORCA, unperturbed runs, per snapshot), 2000 resamples of
the 46 snapshots, PCG64(12345). It replaces the 90% (equivalence-margin) interval of E7b_analysis.json, so
every interval in the table is 95%. The freed-set Jaccard indices and their 95% intervals are read from
E7b_analysis.json (s3_matched.*.jaccard_freed). Run it when data/E7b*/ change, before `make numbers`.

Every number is a numbers.tex macro defined in paper/registry/*.yaml (values from data/derived/*.json);
this script only lays them out and fails if a macro it uses is not in the registry. Cells an experiment
did not measure are "---". Design constants (sigma = 0.07, the 120 s window) are written as such.
"""
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper" / "tables" / "table3_matched.tex"
DERIVED = ROOT / "data" / "derived" / "table3_pair.json"
T_Q, N_BOOT, RNG_SEED = 120.0, 2000, 12345
PAIR_ARMS = {"pub": ("bstar_pub+", "C3_pub"), "rvo2": ("bstar_rvo2+", "C3_rvo2")}


def derive():
    """Pair-block paired rate difference with a 95% bootstrap interval (see module doc)."""
    freed = {}
    for p in (ROOT / "data" / "E7b" / "e7b_quench.jsonl", ROOT / "data" / "E7b_bstar" / "bstar_quench.jsonl"):
        for ln in p.read_text().splitlines():
            if not ln.strip():
                continue
            r = json.loads(ln)
            tag, arm, rep = r["job_id"].split("|")
            if rep == "u":
                freed[(tag, arm)] = bool(r["freed"] and r["first_t"] <= T_Q + 1e-9)
    tags = sorted({t for t, _ in freed}, key=lambda t: int(t.rsplit("seed", 1)[1]))
    rng = np.random.Generator(np.random.PCG64(RNG_SEED))
    out = {"script": "experiments/tables/make_table3.py derive", "doc": __doc__, "n_snapshots": len(tags),
           "n_boot": N_BOOT, "rng": f"PCG64({RNG_SEED})"}
    for k, (a, b) in PAIR_ARMS.items():
        x = np.array([freed[(t, a)] for t in tags], float)
        y = np.array([freed[(t, b)] for t in tags], float)
        n = len(tags)
        v = [float(x[i].mean() - y[i].mean()) for i in (rng.integers(0, n, n) for _ in range(N_BOOT))]
        out[k] = {"bias_arm": a, "orca_arm": b, "freed_bias": int(x.sum()), "freed_orca": int(y.sum()),
                  "diff": float(x.mean() - y.mean()),
                  "diff_ci95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]}
    DERIVED.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {DERIVED}: " + "; ".join(f"{k} {out[k]['diff']:+.3f} {out[k]['diff_ci95']}" for k in PAIR_ARMS))


REG = {}
for f in sorted((ROOT / "paper" / "registry").glob("*.yaml")):
    REG.update(yaml.safe_load(f.read_text()) or {})

NA = "---"


def m(*names):
    for n in names:
        if n not in REG:
            raise SystemExit(f"make_table3: macro '{n}' is not in paper/registry/*.yaml")
    return tuple("\\" + n + "{}" for n in names)


def frac(a, b):
    return "{}/{}".format(*m(a, b))


def diff(d, lo, hi):
    d, lo, hi = m(d, lo, hi)
    return f"${d}$ [${lo}$, ${hi}$]"


def ci(v, lo, hi):
    v, lo, hi = m(v, lo, hi)
    return f"{v} [{lo}, {hi}]"


def one(n):
    return m(n)[0]


def rvo2_pair_jaccard():
    """The RVO2 pair freed sets are disjoint (J = 0, interval [0, 0]): print "0 (disjoint)"; else value [CI]."""
    j = json.loads((ROOT / "data" / "derived" / "E7b_analysis.json").read_text())["s3_matched"]["rvo2"]["jaccard_freed"]
    if j["value"] == 0 and max(j["ci95"]) == 0:
        return one("TabThreePairRvoJacFInt") + " (disjoint)"
    return ci("TabThreePairRvoJacF", "TabThreePairRvoJacFLo", "TabThreePairRvoJacFHi")


PAIR_T = r"$>$120"  # Kaplan--Meier median not reached within the 120 s window (fewer than half freed)

BLOCKS = [
    (r"Lone-trap snapshots (E2): " + one("EtwoNLK") + r" lone keystones, 120\,s", [
        (r"C1 + noise $\sigma=0.07$",
         frac("EtwoLKNoiseCFreed", "EtwoLKNoiseCN"),
         diff("TabThreeLKDiff", "TabThreeLKDiffLo", "TabThreeLKDiffHi"),
         ci("EtwoLKJaccardC", "EtwoLKJaccardCLo", "EtwoLKJaccardCHi"),
         one("TabThreeLKNoiseMed"), NA,
         frac("TabThreeLKNoiseDisagree", "TabThreeLKNoiseSnaps"),
         "{} ({})".format(*m("EthreeEllBA", "EthreeEllBAPred"))),
        ("C3 RVO2",
         frac("EtwoLKCThreeRVOFreed", "EtwoLKCThreeRVON"), "", "",
         one("TabThreeLKRvoMed"), NA,
         frac("TabThreeLKRvoReplayDis", "TabThreeLKRvoReplays"),
         "$" + one("EthreeCThreeLnRatio") + "$"),
    ]),
    (r"Whole runs (E6): " + one("EsixN") + r" seeds, 600\,s", [
        (r"C1 + noise $\sigma^\ast$",
         frac("EsixNoiseK", "EsixN"),
         diff("EsixDiff", "EsixDiffLo", "EsixDiffHi"),
         ci("EsixJaccard", "EsixJaccardLo", "EsixJaccardHi"),
         one("EsixKMNoise"), NA, NA, NA),
        ("C3 RVO2", frac("EsixCThreeK", "EsixN"), "", "", one("EsixKMCThree"), NA, NA, NA),
    ]),
    (r"Pair standoffs (E7b): " + one("PairN") + r" snapshots, 120\,s", [
        (r"bias $b^\ast_{\rm pub}=" + one("PairBstarPub") + "$",
         frac("PairBsPubFreed", "PairN"),
         diff("TabThreePairPubDiff", "TabThreePairPubDiffLo", "TabThreePairPubDiffHi"),
         ci("PairBsPubJac", "PairBsPubJacLo", "PairBsPubJacHi"),
         PAIR_T, frac("PairBsPubHand", "PairBsPubN"),
         frac("TabThreePairBsPubReplayDis", "TabThreePairBsReplays"), NA),
        ("C3 published",
         frac("PairPubFreed", "PairN"), "", "", PAIR_T,
         frac("PairPubLower", "TabThreePairPubOrcaN"),
         frac("TabThreePairPubReplayDis", "TabThreePairOrcaReplays"), NA),
        (r"bias $b^\ast_{\rm RVO2}=" + one("PairBstarRvo") + "$",
         frac("PairBsRvoFreed", "PairN"),
         diff("TabThreePairRvoDiff", "TabThreePairRvoDiffLo", "TabThreePairRvoDiffHi"),
         rvo2_pair_jaccard(),
         PAIR_T, frac("TabThreePairRvoHand", "TabThreePairRvoHandN"),
         frac("TabThreePairBsRvoReplayDis", "TabThreePairBsReplays"), NA),
        ("C3 RVO2",
         frac("PairRvoFreed", "PairN"), "", "", PAIR_T,
         frac("TabThreePairRvoOrcaLower", "TabThreePairRvoOrcaN"),
         frac("TabThreePairRvoReplayDis", "TabThreePairOrcaReplays"), NA),
    ]),
]

CAPTION = (
    r"Controls matched to ORCA on rate, against the signatures that separate them: freed (whole runs: completed) "
    r"count, paired difference $\Delta$ from ORCA, Jaccard index $J$ of the minority outcome sets (unresolved; "
    r"pairs: freed), Kaplan--Meier median $t_{1/2}$, first exits by the lower member, $10^{-9}$\,m replays that "
    r"change the outcome (noise: snapshots whose seeds disagree), and $\ell=\ln\hat\lambda(0.005)/\hat\lambda(0.02)$ "
    r"with its Arrhenius prediction (E3). Intervals are 95\%. Noise counts runs, five seeds per snapshot; --- is not measured."
)


def main():
    lines = [
        "% generated by experiments/tables/make_table3.py from paper/registry/*.yaml macros; do not edit",
        r"\begin{table}[t]",
        r"\caption{" + CAPTION + "}",
        r"\label{tab:matched}",
        r"\centering\scriptsize\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{@{}lccccccc@{}}",
        r"\toprule",
        r"Arm & Freed & $\Delta$ [CI] & $J$ [CI] & $t_{1/2}$ (s) & Lower first & Replay & $\ell$ \\",
    ]
    nrows = 0
    for title, rows in BLOCKS:
        lines += [r"\midrule", r"\multicolumn{8}{@{}l}{\emph{" + title + r"}} \\"]
        for r in rows:
            lines.append(" & ".join(r) + r" \\")
            nrows += 1
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    text = "\n".join(lines) + "\n"
    OUT.write_text(text)
    print(f"wrote {OUT} ({nrows} rows, 8 columns, 3 blocks)")


if __name__ == "__main__":
    if sys.argv[1:] == ["derive"]:
        derive()
    else:
        main()
