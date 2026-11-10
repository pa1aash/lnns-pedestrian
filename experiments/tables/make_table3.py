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


def jind(cell, ind):
    """J cell followed by its expectation for independent sets of the same sizes (A-1), in parentheses."""
    return "{} ({})".format(cell, m(ind)[0])


def one(n):
    return m(n)[0]


def rvo2_pair_jaccard():
    """The RVO2 pair freed sets are disjoint (J = 0, interval [0, 0]): print "0 (disjoint)"; else value [CI]."""
    j = json.loads((ROOT / "data" / "derived" / "E7b_analysis.json").read_text())["s3_matched"]["rvo2"]["jaccard_freed"]
    if j["value"] == 0 and max(j["ci95"]) == 0:
        # J = 0: the bootstrap interval is degenerate; the upper bound is the Clopper-Pearson bound on the
        # shared fraction converted to J (experiments/fixan/fix_a1.py).
        return jind("{} [0, {}]".format(*m("TabThreePairRvoJacFInt", "FixAonePairRvoJHi")), "FixAonePairRvoJInd")
    return ci("TabThreePairRvoJacF", "TabThreePairRvoJacFLo", "TabThreePairRvoJacFHi")


PAIR_T = r"$>$120"  # Kaplan--Meier median not reached within the 120 s window (fewer than half freed)

BLOCKS = [
    (r"Lone-trap snapshots: " + one("EtwoNLK") + r" lone keystones, 120\,s", [
        (r"noise $\sigma=0.07$\,m/s",
         frac("EtwoLKNoiseCFreed", "EtwoLKNoiseCN"),
         diff("TabThreeLKDiff", "TabThreeLKDiffLo", "TabThreeLKDiffHi"),
         jind(ci("FixAoneLoneJ", "FixAoneLoneJLo", "FixAoneLoneJHi"), "FixAoneLoneJInd"),
         one("TabThreeLKNoiseMed"), NA,
         frac("TabThreeLKNoiseDisagree", "TabThreeLKNoiseSnaps"), NA),
        ("ORCA (RVO2)",
         frac("EtwoLKCThreeRVOFreed", "EtwoLKCThreeRVON"), "", "",
         one("TabThreeLKRvoMed"), NA,
         frac("TabThreeLKRvoReplayDis", "TabThreeLKRvoReplays"), NA),
    ]),
    # K5: ell was measured on the time-step set, not at sigma = 0.07 on the lone keystones.
    (r"Time-step test: " + one("EthreeN") + r" lone-trap snapshots", [
        (r"noise, $\beta_{\rm ref}=1.5$", NA, NA, NA, NA, NA, NA,
         "{} ({})".format(*m("EthreeEllBA", "EthreeEllBAPred"))),
        ("ORCA (RVO2)", frac("EthreeCThreeFreed", "EthreeN"), NA, NA, NA, NA, NA,
         "$" + one("EthreeCThreeLnRatioFix") + "$"),
    ]),
    (r"Whole runs: " + one("EsixN") + r" seeds, 600\,s", [
        (r"noise $\sigma^\ast$",
         frac("EsixNoiseK", "EsixN"),
         diff("EsixDiff", "EsixDiffLo", "EsixDiffHi"),
         jind(ci("EsixJaccard", "EsixJaccardLo", "EsixJaccardHi"), "FixAoneWholeJInd"),
         one("EsixKMNoise"), NA, NA, NA),
        ("ORCA (RVO2)", frac("EsixCThreeK", "EsixN"), "", "", one("EsixKMCThree"), NA, NA, NA),
    ]),
    (r"Pair standoffs: " + one("PairN") + r" snapshots, 120\,s", [
        (r"bias $b^\ast_{\rm legacy}=" + one("PairBstarPub") + "$",
         frac("PairBsPubFreed", "PairN"),
         diff("TabThreePairPubDiff", "TabThreePairPubDiffLo", "TabThreePairPubDiffHi"),
         jind(ci("PairBsPubJac", "PairBsPubJacLo", "PairBsPubJacHi"), "FixAonePairPubJInd"),
         PAIR_T, frac("PairBsPubHand", "PairBsPubN"),
         frac("TabThreePairBsPubReplayDis", "TabThreePairBsReplays"), NA),
        ("ORCA (legacy)",
         frac("PairPubFreed", "PairN"), "", "", PAIR_T,
         frac("PairPubLower", "TabThreePairPubOrcaN"),
         frac("TabThreePairPubReplayDis", "TabThreePairOrcaReplays"), NA),
        (r"bias $b^\ast_{\rm RVO2}=" + one("PairBstarRvo") + "$",
         frac("PairBsRvoFreed", "PairN"),
         diff("TabThreePairRvoDiff", "TabThreePairRvoDiffLo", "TabThreePairRvoDiffHi"),
         rvo2_pair_jaccard(),
         PAIR_T, frac("TabThreePairRvoHand", "TabThreePairRvoHandN"),
         frac("TabThreePairBsRvoReplayDis", "TabThreePairBsReplays"), NA),
        ("ORCA (RVO2)",
         frac("PairRvoFreed", "PairN"), "", "", PAIR_T,
         frac("TabThreePairRvoOrcaLower", "TabThreePairRvoOrcaN"),
         frac("TabThreePairRvoReplayDis", "TabThreePairOrcaReplays"), NA),
    ]),
    # velocity coupling of ORCA (Sect. 6.4): runs in progress; the whole row is pending until they are analysed.
    (r"Velocity coupling", [
        (r"ORCA (RVO2), velocity coupling",
         r"\multicolumn{7}{c}{\pending{results of Sect.~\ref{sec:velorca}}}"),
    ]),
]

CAPTION = (
    r"Rate-matched surrogates against ORCA under force coupling (last block: velocity coupling): freed (whole runs: completed), paired difference $\Delta$ from ORCA, $J$ of "
    r"the unresolved sets (pair: freed; disjoint sets: exact 95\% upper bound; expected if independent in parentheses), Kaplan--Meier median $t_{1/2}$ (s), first exits "
    r"by the lower member, outcome changes in $10^{-9}$\,m replays (noise: snapshots whose seeds disagree), $\ell$ of "
    r"Eq.~\eqref{eq:ell} (prediction in parentheses). Noise rows are SFM + noise; lone-trap noise rows count runs, five seeds per snapshot; whole-run rows count seeds."
)


def main():
    lines = [
        "% generated by experiments/tables/make_table3.py from paper/registry/*.yaml macros; do not edit",
        r"\begin{table}[t]",
        r"\caption{" + CAPTION + "}",
        r"\label{tab:matched}",
        r"\centering\scriptsize\setlength{\tabcolsep}{1.5pt}",
        r"\resizebox{\textwidth}{!}{\begin{tabular}{@{}lccccccc@{}}",
        r"\toprule",
        r"Perturbation & Freed & $\Delta$ [CI] & $J$ [CI] & $t_{1/2}$ & Lower & Replay & $\ell$ \\",
    ]
    nrows = 0
    for title, rows in BLOCKS:
        lines += [r"\midrule", r"\multicolumn{8}{@{}l}{\emph{" + title + r"}} \\"]
        for r in rows:
            lines.append(" & ".join(r) + r" \\")
            nrows += 1
    lines += [r"\bottomrule", r"\end{tabular}}", r"\end{table}"]
    text = "\n".join(lines) + "\n"
    OUT.write_text(text)
    print(f"wrote {OUT} ({nrows} rows, 8 columns, {len(BLOCKS)} blocks)")


if __name__ == "__main__":
    if sys.argv[1:] == ["derive"]:
        derive()
    else:
        main()
