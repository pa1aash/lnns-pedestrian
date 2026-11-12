#!/usr/bin/env python3
r"""Write Tables 4 and 5 of Sect. 6: paper/tables/table4_noise.tex (Table 4, tab:matched-noise) and
paper/tables/table5_bias.tex (Table 5, tab:matched-bias).

Table 4: per-step noise fraction-matched to force-coupled ORCA (RVO2) at the lone keystone (sigma = 0.07 m/s,
five seeds, E2; sigma = 0.0717 m/s, 20 seeds, N1; T = 120 s), at the second trap (sigma = 0.07 m/s, E2, A6) and
in whole runs (sigma*, E6; T = 600 s). Table 5: the lateral bias +b* fraction-matched to force-coupled ORCA with
the same solver at the pair standoff (E7b, T = 120 s). Each estimate carries its p in the same cell: the
Holm-adjusted p of the paired test of that probe (A7; Holm over all probes of the comparison, replay included)
and, beside Omega, the unadjusted hypergeometric p of the overlap against independent sets of the same sizes
(A9). The Replay column carries counts only: replay sensitivity of noise holds by construction. Omega (Jaccard
index, formerly J) is given once per comparison (A9: the 20-seed lone-keystone value; the five-seed value is
"n.a."). The ORCA velocity filter is not in the table
(Sect. 6.4 text).

Columns: Freed (blockers freed or runs completed), Delta (surrogate minus ORCA freed fraction, 95% interval),
dRMST (difference of the restricted mean time to free up to T, s, 95% interval; A7), Replay (noise: snapshots
whose seeds disagree; deterministic arms: 1e-9 m replays that change the outcome), J (Jaccard index of the
unresolved sets, pair: freed sets; independence expectation in parentheses), ell (Eq. ell, time-step set) and,
in Table 5, "First exit below axis" (first exits by the member at y < 5 m, below the door axis; A13).

`make_tables45.py derive` writes data/derived/table3_pair.json: the 95% percentile bootstrap interval of the
pair-block paired rate difference (bias +b* minus ORCA, unperturbed runs, per snapshot), 2000 resamples of
the 46 snapshots, PCG64(12345). The table itself reports the rev_A8 interval (PscrPair*Diff*, one fresh
PCG64(12345) per comparison, as the A7/A8 tests), so the derive output is kept for reference only.
Cells shown at two significant figures use the Pscr* macros of paper/registry/p_screen.yaml.

Every number is a numbers.tex macro defined in paper/registry/*.yaml (values from data/derived/*.json);
this script only lays them out and fails if a macro it uses is not in the registry. Cells are "n.a." where a
probe does not apply and "not run" where the experiment was not run; design constants (sigma = 0.07, the 120 s and 600 s horizons) are written as such.
"""
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT_A = ROOT / "paper" / "tables" / "table4_noise.tex"
OUT_B = ROOT / "paper" / "tables" / "table5_bias.tex"
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
    out = {"script": "experiments/tables/make_tables45.py derive", "doc": __doc__, "n_snapshots": len(tags),
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

NA, NR, E = "n.a.", "not run", ""


def m(*names):
    for n in names:
        if n not in REG:
            raise SystemExit(f"make_tables45: macro '{n}' is not in paper/registry/*.yaml")
    return tuple("\\" + n + "{}" for n in names)


def one(n):
    return m(n)[0]


def frac(a, b):
    return "{}/{}".format(*m(a, b))


def pv(name):
    """p with its relation ("=0.90", "<10^-4"): the <name>Rel companion of a fmt-p registry macro."""
    one(name)
    if REG[name].get("fmt") != "p":  # a plain two-decimal p (no Rel companion) prints with "="
        return "$p=\\" + name + "{}$"
    return "$p\\" + name + "Rel{}$"


def st(top, bottom):
    """Two-line cell: the estimate on top, its p (or the second half of a label) below."""
    return r"\st{" + top + "}{" + bottom + "}"


def stl(top, bottom):
    """Two-line row label, left-aligned."""
    return r"\stl{" + top + "}{" + bottom + "}"


def dpm(d, lo, hi, p=None):
    """Effect with its unadjusted 95% interval, its p below it in the same cell."""
    d, lo, hi = m(d, lo, hi)
    cell = f"${d}$ [${lo}$, ${hi}$]"
    return st(cell, pv(p)) if p else cell


def jcell(j, ind, p=None, mark=""):
    """Omega (Jaccard index), its value for independent sets in parentheses, the hypergeometric p below."""
    j, ind = m(j, ind)
    cell = f"{j} ({ind})"
    return st(cell, pv(p) + mark) if p else cell


# Table 4: Perturbation | Freed | Delta [CI], p | dRMST [CI], p | Replay | Omega (indep.), p | ell (pred.), p
COLS_A = (r"Perturbation & Freed & $\Delta$ [95\%] & \hd{$\Delta$RMST (s)}{[95\%]} & Replay & \hd{$\Omega$}{(indep.)} "
          r"& $\ell$ (pred.)")
BLOCKS_A = [
    (r"Lone keystones: " + one("EtwoNLK") + r" snapshots, $T=120$\,s", [
        (stl("noise, 5 seeds", r"$\sigma=0.07$\,m/s"),
         frac("EtwoLKNoiseCFreed", "EtwoLKNoiseCN"),
         dpm("PscrLKDiff", "PscrLKDiffLo", "PscrLKDiffHi", "RevAsevenLoneEtwoFreedPHolm"),
         dpm("PscrTimeLoneEtwoEff", "PscrTimeLoneEtwoLo", "PscrTimeLoneEtwoHi", "RevAsevenLoneEtwoTimePHolm"),
         frac("TabThreeLKNoiseDisagree", "TabThreeLKNoiseSnaps"), NA,
         st("{} ({})".format(*m("PprotEllBA", "PprotEllBAPred")), pv("RevAsevenLoneEtwoEllPHolm"))),
        (stl("noise, 20 seeds", r"$\sigma=" + one("RunNOneSigma") + r"$\,m/s"),
         frac("RunNOneFreed", "RunNOneRunsN"),
         dpm("PscrNOneDiff", "PscrNOneDiffLo", "PscrNOneDiffHi", "RevAsevenLoneNoneFreedPHolm"),
         dpm("PscrTimeLoneNoneEff", "PscrTimeLoneNoneLo", "PscrTimeLoneNoneHi", "RevAsevenLoneNoneTimePHolm"),
         "{}/{}".format(*m("RevAsevenLoneNoneReplayDiscA", "EtwoNLK")),
         jcell("RevAnineLKNHalfJ", "PscrLKNHalfEJ", "RevAnineLKNHalfP"), NA),
        (stl("force-coupled", "ORCA (RVO2)"),
         frac("EtwoLKCThreeRVOFreed", "EtwoLKCThreeRVON"), E, E,
         frac("TabThreeLKRvoReplayDis", "TabThreeLKRvoReplays"), E,
         "$" + one("PscrOrcaLnRatio") + "$"),
    ]),
    (r"Second traps: " + one("RevAsixSTSnaps") + r" snapshots, $T=120$\,s", [
        (stl("noise, 5 seeds", r"$\sigma=0.07$\,m/s"),
         frac("RevAsixSTNoiseFreed", "RevAsixSTNoiseN"),
         dpm("RevAsixSTDiff", "PscrSTDiffLo", "RevAsixSTDiffHi", "RevAsevenSecondFreedPHolm"),
         dpm("PscrTimeSecondEff", "PscrTimeSecondLo", "PscrTimeSecondHi", "RevAsevenSecondTimePHolm"),
         frac("RevAsixSTNoiseDisagree", "RevAsixSTSnaps"),
         jcell("RevAsixSTJ", "RevAsixSTJInd", "RevAsixSTJIndP"), NR),
        (stl("force-coupled", "ORCA (RVO2)"),
         frac("RevAsixSTOrcaFreed", "RevAsixSTOrcaN"), E, E,
         frac("RevAsixSTOrcaReplayDis", "RevAsixSTOrcaReplays"), E, NR),
    ]),
    (r"Whole runs: " + one("EsixN") + r" spawn seeds, $T=600$\,s", [
        (stl("noise", r"$\sigma^\ast=" + one("EsixSigmaStar") + r"$\,m/s"),
         frac("EsixNoiseK", "EsixN"),
         dpm("PscrWholeDiff", "PscrWholeDiffLo", "PscrWholeDiffHi", "RevAsevenWholeEsixFreedPHolm"),
         dpm("PscrTimeWholeEff", "PscrTimeWholeLo", "PscrTimeWholeHi", "RevAsevenWholeEsixTimePHolm"),
         NR, jcell("RevAnineWholeEJ", "RevAnineWholeEEJ", "RevAnineWholeEP"), NR),
        (stl("force-coupled", "ORCA (RVO2)"), frac("EsixCThreeK", "EsixN"), E, E, NR, E, NR),
    ]),
]

# Table 5: Perturbation | Freed | Delta [CI], p | dRMST [CI], p | Replay | Omega (indep.), p | first exit below axis, p
COLS_B = (r"Perturbation & Freed & $\Delta$ [95\%] & \hd{$\Delta$RMST (s)}{[95\%]} & Replay & \hd{$\Omega$}{(indep.)} "
          r"& \hd{First exit}{below axis}")
BLOCKS_B = [
    (r"Legacy solver: " + one("PairN") + r" pair standoffs, $T=120$\,s", [
        (stl("bias", r"$+b^\ast_{\rm legacy}=" + one("PscrPairBstarPub") + "$"),
         frac("PairBsPubFreed", "PairN"),
         dpm("PscrPairPubDiff", "PscrPairPubDiffLo", "PscrPairPubDiffHi", "RevAsevenPairPubFreedPHolm"),
         dpm("PscrTimePairPubEff", "PscrTimePairPubLo", "PscrTimePairPubHi", "RevAsevenPairPubTimePHolm"),
         frac("TabThreePairBsPubReplayDis", "TabThreePairBsReplays"),
         jcell("RevAninePairPubJ", "RevAninePairPubEJ", "RevAninePairPubP"),
         st(frac("PairBsPubHand", "PairBsPubN"), pv("RevAsevenPairPubHandPHolm"))),
        (stl("force-coupled", "ORCA (legacy)"),
         frac("PairPubFreed", "PairN"), E, E,
         frac("TabThreePairPubReplayDis", "TabThreePairOrcaReplays"), E,
         frac("PairPubLower", "TabThreePairPubOrcaN")),
    ]),
    (r"RVO2 solver: " + one("PairN") + r" pair standoffs, $T=120$\,s", [
        (stl("bias", r"$+b^\ast_{\rm RVO2}=" + one("PairBstarRvo") + "$"),
         frac("PairBsRvoFreed", "PairN"),
         dpm("PscrPairRvoDiff", "PscrPairRvoDiffLo", "PscrPairRvoDiffHi", "RevAsevenPairRvoFreedPHolm"),
         dpm("PscrTimePairRvoEff", "PscrTimePairRvoLo", "PscrTimePairRvoHi", "RevAsevenPairRvoTimePHolm"),
         frac("TabThreePairBsRvoReplayDis", "TabThreePairBsReplays"),
         # Omega = 0: the informative tail is P(X <= 0) (A9), marked with a dagger in the note
         jcell("RevAninePairRvoJ", "PscrPairRvoEJ", "RevAninePairRvoPLe", r"$^\dagger$"),
         st(frac("TabThreePairRvoHand", "TabThreePairRvoHandN"), pv("RevAsevenPairRvoHandPHolm"))),
        (stl("force-coupled", "ORCA (RVO2)"),
         frac("PairRvoFreed", "PairN"), E, E,
         frac("TabThreePairRvoReplayDis", "TabThreePairOrcaReplays"), E,
         frac("TabThreePairRvoOrcaLower", "TabThreePairRvoOrcaN")),
    ]),
]

CAPTION_A = (
    r"Per-step noise against force-coupled ORCA (RVO2), fraction-matched at the lone keystones and in whole runs "
    r"(at the second traps $\Delta$ excludes 0)."
)
NOTE_A = (
    r"Freed: runs freed by $T$ (noise), snapshots (force-coupled ORCA), runs completed (whole runs). "
    r"$\Delta$: freed fraction, noise minus force-coupled ORCA. "
    r"$\Delta$RMST: difference of the mean time to free, capped at $T$. "
    r"Replay: snapshots whose seeds disagree (noise, by construction) or whose $10^{-9}$\,m replay changes the "
    r"outcome (force-coupled ORCA). "
    r"$\Omega$: Jaccard index of the unresolved sets (noise: freed in fewer than half the seeds); in parentheses, "
    r"for independent sets. "
    r"$\ell$: Eq.~\eqref{eq:ell} pooled over the " + one("EthreeN") + r" snapshots of the time-step set, noise at "
    r"$\beta=1.5$ (prediction). "
    r"Intervals are unadjusted. $p$ beside $\Delta$, $\Delta$RMST and $\ell$: paired test, Holm-adjusted over the "
    r"probes of the comparison (lone keystones 4: $\Delta$, replay, $\Delta$RMST, and $\ell$ or outcome identity; "
    r"second traps 3; whole runs 4: $\Delta$, outcome identity, $\Delta$RMST, final-state class). "
    r"$p$ beside $\Omega$: hypergeometric, unadjusted. "
    r"n.a.: not applicable; not run: probe not run on this set."
)
CAPTION_B = (
    r"Lateral bias $+b^\ast$ fraction-matched to force-coupled ORCA with the same solver at the pair standoff."
)
NOTE_B = (
    r"Columns as in Table~\ref{tab:matched-noise}; $\Omega$ compares the freed sets. "
    r"First exit below axis: freed standoffs first left by the member at $y<5$\,m, below the door axis. "
    r"Holm family per solver: 5 probes ($\Delta$, replay, outcome identity, $\Delta$RMST, first exit). "
    r"$^\dagger$$\Omega=0$: $p$ of an overlap this small or smaller."
)

def render(rows_blocks, cols, caption, note, label):
    ncol = cols.count("&") + 1
    lines = [
        "% generated by experiments/tables/make_tables45.py from paper/registry/*.yaml macros; do not edit",
        r"\begin{table}[t]",
    ]
    lines += [
        r"\caption{" + caption + "}",
        r"\label{" + label + "}",
        r"\centering\scriptsize\setlength{\tabcolsep}{1pt}",
        r"\def\st#1#2{\begin{tabular}[t]{@{}c@{}}#1\\\relax#2\end{tabular}}%",
        r"\def\stl#1#2{\begin{tabular}[t]{@{}l@{}}#1\\\relax#2\end{tabular}}%",
        r"\def\hd#1#2{\begin{tabular}[b]{@{}c@{}}#1\\\relax#2\end{tabular}}%",
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l" + "c" * (ncol - 1) + "@{}}",
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
    lines += [r"\bottomrule", r"\end{tabular*}", r"\par\smallskip",
              r"\parbox{\textwidth}{\scriptsize " + note + "}", r"\end{table}"]
    return "\n".join(lines) + "\n", nrows


def main():
    for out, blocks, cols, cap, note, label in (
            (OUT_A, BLOCKS_A, COLS_A, CAPTION_A, NOTE_A, "tab:matched-noise"),
            (OUT_B, BLOCKS_B, COLS_B, CAPTION_B, NOTE_B, "tab:matched-bias")):
        text, n = render(blocks, cols, cap, note, label)
        out.write_text(text)
        print(f"wrote {out} ({n} rows)")


if __name__ == "__main__":
    if sys.argv[1:] == ["derive"]:
        derive()
    else:
        main()
