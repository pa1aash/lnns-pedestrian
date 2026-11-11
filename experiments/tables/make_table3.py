#!/usr/bin/env python3
r"""Write Table 3 of Sect. 6 as two floats: paper/tables/table3a_noise.tex (Table 3a, tab:matched-noise) and
paper/tables/table3b_bias.tex (Table 3b, tab:matched-bias).

Table 3a: per-step noise fraction-matched to force-coupled ORCA (RVO2) at the lone keystone (sigma = 0.07 m/s,
five seeds, E2; sigma = 0.0717 m/s, 20 seeds, N1; T = 120 s), at the second trap (sigma = 0.07 m/s, E2, A6) and
in whole runs (sigma*, E6; T = 600 s). Table 3b: the lateral bias +b* fraction-matched to force-coupled ORCA with
the same solver at the pair standoff (E7b, T = 120 s). Each surrogate row is followed by a row of p-values:
the Holm-adjusted p of the paired test of each probe (revision item A7) and, under J, the hypergeometric p of
the overlap against independent sets of the same sizes (A9). J is given once per comparison (A9: the
20-seed lone-keystone value; the five-seed value is not shown). The ORCA velocity filter is not in the table
(Sect. 6.4 text).

Columns: Freed (blockers freed or runs completed), Delta (surrogate minus ORCA freed fraction, 95% interval),
dRMST (difference of the restricted mean time to free up to T, s, 95% interval; A7), Replay (noise: snapshots
whose seeds disagree; deterministic arms: 1e-9 m replays that change the outcome), J (Jaccard index of the
unresolved sets, pair: freed sets; independence expectation in parentheses), ell (Eq. ell, time-step set) and,
in 3b, Lower (first exits by the member at y < 5 m, below the door axis; A13).

`make_table3.py derive` writes data/derived/table3_pair.json: the 95% percentile bootstrap interval of the
pair-block paired rate difference (bias +b* minus ORCA, unperturbed runs, per snapshot), 2000 resamples of
the 46 snapshots, PCG64(12345). Run it when data/E7b*/ change, before `make numbers`.

Every number is a numbers.tex macro defined in paper/registry/*.yaml (values from data/derived/*.json);
this script only lays them out and fails if a macro it uses is not in the registry. Cells an experiment
did not measure are "---"; design constants (sigma = 0.07, the 120 s and 600 s horizons) are written as such.
"""
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT_A = ROOT / "paper" / "tables" / "table3a_noise.tex"
OUT_B = ROOT / "paper" / "tables" / "table3b_bias.tex"
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


def dpm(d, lo, hi):
    """Effect with its 95% interval, all in math mode."""
    d, lo, hi = m(d, lo, hi)
    return f"${d}$ [${lo}$, ${hi}$]"


def jcell(j, ind):
    j, ind = m(j, ind)
    return f"{j} ({ind})"


def prow(*cells):
    """The p-value row under a surrogate row: label, then one cell per column."""
    return (r"\quad $p$",) + cells


E = ""
PROW_FREED = 1  # column index of Freed (empty in p rows)

# Table 3a: Perturbation | Freed | Delta [CI] | dRMST [CI] | Replay | J (indep.) | ell (pred.)
COLS_A = r"Perturbation & Freed & $\Delta$ [95\%] & $\Delta$RMST (s) [95\%] & Replay & $J$ (indep.) & $\ell$ (pred.)"
BLOCKS_A = [
    (r"Lone keystones: " + one("EtwoNLK") + r" snapshots, $T=120$\,s", [
        (r"noise $\sigma=0.07$\,m/s, 5 seeds",
         frac("EtwoLKNoiseCFreed", "EtwoLKNoiseCN"),
         dpm("TabThreeLKDiff", "TabThreeLKDiffLo", "TabThreeLKDiffHi"),
         dpm("RevAsevenLoneEtwoTimeEff", "RevAsevenLoneEtwoTimeLo", "RevAsevenLoneEtwoTimeHi"),
         frac("TabThreeLKNoiseDisagree", "TabThreeLKNoiseSnaps"), NA,
         "{} ({})".format(*m("EthreeEllBA", "EthreeEllBAPred"))),
        prow(E, one("RevAsevenLoneEtwoFreedPHolm"), one("RevAsevenLoneEtwoTimePHolm"),
             one("RevAsevenLoneEtwoReplayPHolm"), E, one("RevAsevenLoneEtwoEllPHolm")),
        (r"noise $\sigma=" + one("RunNOneSigma") + r"$\,m/s, 20 seeds",
         frac("RunNOneFreed", "RunNOneRunsN"),
         dpm("RunNOneDiff", "RunNOneDiffLo", "RunNOneDiffHi"),
         dpm("RevAsevenLoneNoneTimeEff", "RevAsevenLoneNoneTimeLo", "RevAsevenLoneNoneTimeHi"),
         "{}/{}".format(*m("RevAsevenLoneNoneReplayDiscA", "EtwoNLK")),
         jcell("RevAnineLKNHalfJ", "RevAnineLKNHalfEJ"), NA),
        prow(E, one("RevAsevenLoneNoneFreedPHolm"), one("RevAsevenLoneNoneTimePHolm"),
             one("RevAsevenLoneNoneReplayPHolm"), one("RevAnineLKNHalfP"), E),
        ("force-coupled ORCA (RVO2)",
         frac("EtwoLKCThreeRVOFreed", "EtwoLKCThreeRVON"), E, E,
         frac("TabThreeLKRvoReplayDis", "TabThreeLKRvoReplays"), E,
         "$" + one("EthreeCThreeLnRatioFix") + "$"),
    ]),
    (r"Second traps: " + one("RevAsixSTSnaps") + r" snapshots, $T=120$\,s", [
        (r"noise $\sigma=0.07$\,m/s, 5 seeds",
         frac("RevAsixSTNoiseFreed", "RevAsixSTNoiseN"),
         dpm("RevAsixSTDiff", "RevAsixSTDiffLo", "RevAsixSTDiffHi"),
         dpm("RevAsevenSecondTimeEff", "RevAsevenSecondTimeLo", "RevAsevenSecondTimeHi"),
         frac("RevAsixSTNoiseDisagree", "RevAsixSTSnaps"),
         jcell("RevAsixSTJ", "RevAsixSTJInd"), NA),
        prow(E, one("RevAsevenSecondFreedPHolm"), one("RevAsevenSecondTimePHolm"),
             one("RevAsevenSecondReplayPHolm"), one("RevAsixSTJIndP"), E),
        ("force-coupled ORCA (RVO2)",
         frac("RevAsixSTOrcaFreed", "RevAsixSTOrcaN"), E, E,
         frac("RevAsixSTOrcaReplayDis", "RevAsixSTOrcaReplays"), E, NA),
    ]),
    (r"Whole runs: " + one("EsixN") + r" spawn seeds, $T=600$\,s", [
        (r"noise $\sigma^\ast=" + one("EsixSigmaStar") + r"$\,m/s",
         frac("EsixNoiseK", "EsixN"),
         dpm("EsixDiff", "EsixDiffLo", "EsixDiffHi"),
         dpm("RevAsevenWholeEsixTimeEff", "RevAsevenWholeEsixTimeLo", "RevAsevenWholeEsixTimeHi"),
         NA, jcell("RevAnineWholeEJ", "RevAnineWholeEEJ"), NA),
        prow(E, one("RevAsevenWholeEsixFreedPHolm"), one("RevAsevenWholeEsixTimePHolm"), E,
             one("RevAnineWholeEP"), E),
        ("force-coupled ORCA (RVO2)", frac("EsixCThreeK", "EsixN"), E, E, NA, E, NA),
    ]),
]

# Table 3b: Perturbation | Freed | Delta [CI] | dRMST [CI] | Replay | J (indep.) | Lower
COLS_B = r"Perturbation & Freed & $\Delta$ [95\%] & $\Delta$RMST (s) [95\%] & Replay & $J$ (indep.) & Lower"
BLOCKS_B = [
    (r"Legacy solver: " + one("PairN") + r" pair standoffs, $T=120$\,s", [
        (r"bias $+b^\ast_{\rm legacy}=" + one("PairBstarPub") + "$",
         frac("PairBsPubFreed", "PairN"),
         dpm("TabThreePairPubDiff", "TabThreePairPubDiffLo", "TabThreePairPubDiffHi"),
         dpm("RevAsevenPairPubTimeEff", "RevAsevenPairPubTimeLo", "RevAsevenPairPubTimeHi"),
         frac("TabThreePairBsPubReplayDis", "TabThreePairBsReplays"),
         jcell("RevAninePairPubJ", "RevAninePairPubEJ"),
         frac("PairBsPubHand", "PairBsPubN")),
        prow(E, one("RevAsevenPairPubFreedPHolm"), one("RevAsevenPairPubTimePHolm"),
             one("RevAsevenPairPubReplayPHolm"), one("RevAninePairPubP"), one("RevAsevenPairPubHandPHolm")),
        ("force-coupled ORCA (legacy)",
         frac("PairPubFreed", "PairN"), E, E,
         frac("TabThreePairPubReplayDis", "TabThreePairOrcaReplays"), E,
         frac("PairPubLower", "TabThreePairPubOrcaN")),
    ]),
    (r"RVO2 solver: " + one("PairN") + r" pair standoffs, $T=120$\,s", [
        (r"bias $+b^\ast_{\rm RVO2}=" + one("PairBstarRvo") + "$",
         frac("PairBsRvoFreed", "PairN"),
         dpm("TabThreePairRvoDiff", "TabThreePairRvoDiffLo", "TabThreePairRvoDiffHi"),
         dpm("RevAsevenPairRvoTimeEff", "RevAsevenPairRvoTimeLo", "RevAsevenPairRvoTimeHi"),
         frac("TabThreePairBsRvoReplayDis", "TabThreePairBsReplays"),
         jcell("RevAninePairRvoJ", "RevAninePairRvoEJ"),
         frac("TabThreePairRvoHand", "TabThreePairRvoHandN")),
        # J = 0: the informative tail is P(X <= 0) (A9), marked with a dagger in the note
        prow(E, one("RevAsevenPairRvoFreedPHolm"), one("RevAsevenPairRvoTimePHolm"),
             one("RevAsevenPairRvoReplayPHolm"), one("RevAninePairRvoPLe") + r"$^\dagger$",
             one("RevAsevenPairRvoHandPHolm")),
        ("force-coupled ORCA (RVO2)",
         frac("PairRvoFreed", "PairN"), E, E,
         frac("TabThreePairRvoReplayDis", "TabThreePairOrcaReplays"), E,
         frac("TabThreePairRvoOrcaLower", "TabThreePairRvoOrcaN")),
    ]),
]

CAPTION_A = (
    r"Per-step noise fraction-matched to force-coupled ORCA (RVO2); each row $p$ tests the noise row above it."
)
NOTE_A = (
    r"Freed: runs freed by $T$ (noise), snapshots (ORCA), runs completed (whole runs). "
    r"$\Delta$: freed fraction, noise minus ORCA. "
    r"$\Delta$RMST: difference of the mean time to free, capped at $T$. "
    r"Replay: snapshots whose seeds disagree (noise) or whose $10^{-9}$\,m replay changes the outcome (ORCA). "
    r"$J$: Jaccard index of the unresolved sets (noise: freed in fewer than half the seeds); in parentheses, "
    r"for independent sets. "
    r"$\ell$: Eq.~\eqref{eq:ell} on " + one("EthreeN") + r" snapshots (prediction). "
    r"$p$: Holm-adjusted paired test; under $J$, hypergeometric."
)
CAPTION_B = (
    r"Lateral bias $+b^\ast$ fraction-matched to force-coupled ORCA with the same solver at the pair standoff."
)
NOTE_B = (
    r"Columns as in Table~\ref{tab:matched-noise}; $J$ compares the freed sets. "
    r"Lower: freed standoffs first left by the member at $y<5$\,m. "
    r"$^\dagger$$J=0$: $p$ of an overlap this small or smaller."
)


def render(rows_blocks, cols, caption, note, label, suffix):
    ncol = cols.count("&") + 1
    lines = [
        "% generated by experiments/tables/make_table3.py from paper/registry/*.yaml macros; do not edit",
        r"\begin{table}[t]",
        r"\renewcommand{\thetable}{\arabic{table}" + suffix + "}",
    ]
    if suffix == "b":
        lines.append(r"\addtocounter{table}{-1}")
    lines += [
        r"\caption{" + caption + "}",
        r"\label{" + label + "}",
        r"\centering\scriptsize\setlength{\tabcolsep}{2pt}",
        r"\resizebox{\textwidth}{!}{\begin{tabular}{@{}l" + "c" * (ncol - 1) + "@{}}",
        r"\toprule",
        cols + r" \\",
    ]
    nrows = 0
    for title, rows in rows_blocks:
        lines += [r"\midrule", r"\multicolumn{" + str(ncol) + r"}{@{}l}{\emph{" + title + r"}} \\"]
        for r in rows:
            assert len(r) == ncol, (title, r)
            lines.append(" & ".join(r) + r" \\")
            nrows += 1
    lines += [r"\bottomrule", r"\end{tabular}}", r"\par\smallskip",
              r"\parbox{\textwidth}{\scriptsize " + note + "}", r"\end{table}"]
    return "\n".join(lines) + "\n", nrows


def main():
    for out, blocks, cols, cap, note, label, suf in (
            (OUT_A, BLOCKS_A, COLS_A, CAPTION_A, NOTE_A, "tab:matched-noise", "a"),
            (OUT_B, BLOCKS_B, COLS_B, CAPTION_B, NOTE_B, "tab:matched-bias", "b")):
        text, n = render(blocks, cols, cap, note, label, suf)
        out.write_text(text)
        print(f"wrote {out} ({n} rows)")


if __name__ == "__main__":
    if sys.argv[1:] == ["derive"]:
        derive()
    else:
        main()
