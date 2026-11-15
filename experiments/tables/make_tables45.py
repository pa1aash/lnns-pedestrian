#!/usr/bin/env python3
r"""Write the merged table of matched comparisons (Sect. 7): paper/tables/table2_matched.tex (Table 2, tab:matched).

Revision 5 (session P3) merged the former Tables 4 (tab:matched-noise) and 5 (tab:matched-bias) into one table of
four columns: Set | Perturbation | Freed | Delta [95%]. The dropped columns (Holm-adjusted p beside Delta, dRMST with
its p, Replay, Omega with its p, ell, first exit with its p) are stated in the text of Sects. 7.1-7.3; their macros
are listed in DROPPED below and the build fails if one of them leaves the registry. The description of the former
two tables follows; it still describes the sources of every cell.

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

`make_tables45.py derive` writes data/derived/table3_pair.json (file name from the earlier numbering): the 95% percentile bootstrap interval of the
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
OUT = ROOT / "paper" / "tables" / "table2_matched.tex"
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


# Merged table: Set | Perturbation | Freed | Delta [95%] (Delta: surrogate minus force-coupled ORCA, unadjusted)
COLS = r"Set & Perturbation & Freed & $\Delta$ [95\%]"


def set_label(name, n, T):
    return name + " (" + n + ", " + T + r"\,s)"


ROWS = [
    (set_label("Lone keystones", one("EtwoNLK"), "120"), r"noise $\sigma=0.07$\,m/s, 5 seeds",
     frac("EtwoLKNoiseCFreed", "EtwoLKNoiseCN"), dpm("RvAfiveLoneEtwoDiff", "RvAfiveLoneEtwoDiffLo", "RvAfiveLoneEtwoDiffHi")),
    ("", r"noise $\sigma=" + one("RunNOneSigma") + r"$\,m/s, 20 seeds",
     frac("RunNOneFreed", "RunNOneRunsN"), dpm("RvAfiveLoneNoneDiff", "RvAfiveLoneNoneDiffLo", "RvAfiveLoneNoneDiffHi")),
    ("", "force-coupled ORCA", frac("EtwoLKCThreeRVOFreed", "EtwoLKCThreeRVON"), E),
    (set_label("Second traps", one("RevAsixSTSnaps"), "120"), r"noise $\sigma=0.07$\,m/s, 5 seeds",
     frac("RevAsixSTNoiseFreed", "RevAsixSTNoiseN"),
     dpm("RvAfiveSecondEtwoDiff", "RvAfiveSecondEtwoDiffLo", "RvAfiveSecondEtwoDiffHi")),
    ("", "force-coupled ORCA", frac("RevAsixSTOrcaFreed", "RevAsixSTOrcaN"), E),
    (set_label("Whole runs", one("EsixN"), "600"), r"noise $\sigma^\ast=" + one("EsixSigmaStar") + r"$\,m/s",
     frac("EsixNoiseK", "EsixN"), dpm("RvAfiveWholeDiff", "RvAfiveWholeDiffLo", "RvAfiveWholeDiffHi")),
    ("", "force-coupled ORCA", frac("EsixCThreeK", "EsixN"), E),
    (set_label("Pair standoffs, legacy", one("PairN"), "120"), r"bias $+b^\ast=" + one("PscrPairBstarPub") + "$",
     frac("PairBsPubFreed", "PairN"), dpm("RvAfivePairLegacyDiff", "RvAfivePairLegacyDiffLo", "RvAfivePairLegacyDiffHi")),
    ("", "force-coupled ORCA (legacy)", frac("PairPubFreed", "PairN"), E),
    (set_label("Pair standoffs, RVO2", one("PairN"), "120"), r"bias $+b^\ast=" + one("PairBstarRvo") + "$",
     frac("PairBsRvoFreed", "PairN"), dpm("RvAfivePairRvoDiff", "RvAfivePairRvoDiffLo", "RvAfivePairRvoDiffHi")),
    ("", "force-coupled ORCA", frac("PairRvoFreed", "PairN"), E),
]

# Macros of the dropped columns of the former Tables 4 and 5, now in the text of Sect. 7 (checked to exist).
DROPPED = [
    "RevAsevenLoneEtwoFreedPHolm", "RevAsevenLoneNoneFreedPHolm", "RevAsevenSecondFreedPHolm",
    "RevAsevenWholeEsixFreedPHolm", "RevAsevenPairPubFreedPHolm", "RevAsevenPairRvoFreedPHolm",
    "PscrTimeLoneEtwoEff", "PscrTimeLoneEtwoLo", "PscrTimeLoneEtwoHi", "RevAsevenLoneEtwoTimePHolm",
    "PscrTimeLoneNoneEff", "PscrTimeLoneNoneLo", "PscrTimeLoneNoneHi", "RevAsevenLoneNoneTimePHolm",
    "PscrTimeSecondEff", "PscrTimeSecondLo", "PscrTimeSecondHi", "RevAsevenSecondTimePHolm",
    "PscrTimeWholeEff", "PscrTimeWholeLo", "PscrTimeWholeHi", "RevAsevenWholeEsixTimePHolm",
    "PscrTimePairPubEff", "PscrTimePairPubLo", "PscrTimePairPubHi", "RevAsevenPairPubTimePHolm",
    "PscrTimePairRvoEff", "PscrTimePairRvoLo", "PscrTimePairRvoHi", "RevAsevenPairRvoTimePHolm",
    "TabThreeLKNoiseDisagree", "TabThreeLKNoiseSnaps", "RevAsevenLoneNoneReplayDiscA", "TabThreeLKRvoReplayDis",
    "TabThreeLKRvoReplays", "RevAsixSTNoiseDisagree", "RevAsixSTOrcaReplayDis", "RevAsixSTOrcaReplays",
    "TabThreePairBsPubReplayDis", "TabThreePairBsRvoReplayDis", "TabThreePairBsReplays", "TabThreePairPubReplayDis",
    "TabThreePairRvoReplayDis", "TabThreePairOrcaReplays",
    "RevAnineLKNHalfJ", "PscrLKNHalfEJ", "RevAnineLKNHalfP", "RevAsixSTJ", "RevAsixSTJInd", "RevAsixSTJIndP",
    "RevAnineWholeEJ", "RevAnineWholeEEJ", "RevAnineWholeEP", "RevAninePairPubJ", "RevAninePairPubEJ",
    "RevAninePairPubP", "RevAninePairRvoJ", "PscrPairRvoEJ", "RevAninePairRvoPLe",
    "PprotEllBA", "PprotEllBAPred", "RevAsevenLoneEtwoEllPHolm", "PscrOrcaLnRatio", "EthreeN",
    "PairBsPubHand", "PairBsPubN", "RevAsevenPairPubHandPHolm", "TabThreePairRvoHand", "TabThreePairRvoHandN",
    "RevAsevenPairRvoHandPHolm", "PairPubLower", "TabThreePairPubOrcaN", "TabThreePairRvoOrcaLower",
    "TabThreePairRvoOrcaN",
]

CAPTION = r"Matched surrogates against force-coupled ORCA: freed fraction at the horizon $T$ and the paired difference."
NOTE = (r"Set: number of snapshots or runs and horizon $T$. Freed: noise quenches freed by $T$ (snapshots times seeds), snapshots freed (force-coupled ORCA, bias), runs "
        r"completed (whole runs). $\Delta$: freed fraction of the surrogate minus that of force-coupled ORCA, with "
        r"its unadjusted 95\% interval.")


def render():
    m(*DROPPED)
    lines = [
        "% generated by experiments/tables/make_tables45.py from paper/registry/*.yaml macros; do not edit",
        r"\begin{table}[t]",
        r"\caption{" + CAPTION + "}",
        r"\label{tab:matched}",
        r"\centering\scriptsize\setlength{\tabcolsep}{2pt}",
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llcc@{}}",
        r"\toprule",
        COLS + r" \\",
        r"\midrule",
    ]
    for i, r in enumerate(ROWS):
        if i and r[0]:
            lines.append(r"\addlinespace[2pt]")
        lines.append(" & ".join(r) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular*}", r"\par\smallskip",
              r"\parbox{\textwidth}{\scriptsize " + NOTE + "}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def main():
    OUT.write_text(render())
    print(f"wrote {OUT} ({len(ROWS)} rows)")


if __name__ == "__main__":
    if sys.argv[1:] == ["derive"]:
        derive()
    else:
        main()
