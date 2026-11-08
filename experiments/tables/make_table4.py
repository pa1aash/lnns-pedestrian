#!/usr/bin/env python3
r"""Write paper/tables/table4_conference.tex: the conference findings and their status in this paper.

One row per conference claim of plan/CORRECTIONS_TABLE.md, condensed: claim (with the printed value),
status (confirmed / revised / withdrawn), one line of evidence, and where in this paper the evidence sits
(a section, or the setting of a run reported only in Sect. 6.3).

`make_table4.py derive` writes data/derived/table4_conference.json: the values printed in the conference
paper (Gang & Veluri, SIMULTECH 2026, camera-ready text, line numbers CR:n as in plan/CORRECTIONS_TABLE.md),
so that the claim column is macro-driven like every other number. Run it once (the values are constants);
`make numbers` then defines the TabFourConf* macros of paper/registry/table4.yaml.

Every number is a numbers.tex macro defined in paper/registry/*.yaml. A row whose evidence needs macros that
are not yet registered (its production run has not been analysed) prints \pending in the status and
evidence cells; the script never invents a value.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper" / "tables" / "table4_conference.tex"
DERIVED = ROOT / "data" / "derived" / "table4_conference.json"

CONFERENCE = {
    "source": "Gang & Veluri, SIMULTECH 2026, pp. 474-481, DOI 10.5220/0015190200004094 (camera-ready text)",
    "c1_complete": {"k": 0, "n": 25, "cr": "CR:14, CR:780"},
    "c2_complete": {"k": 0, "n": 25, "cr": "CR:14, CR:780"},
    "c3_complete": {"k": 13, "n": 25, "cr": "CR:15, CR:780"},
    "c4_complete": {"k": 14, "n": 25, "cr": "CR:15, CR:780"},
    "noise_complete": {"sigma": 0.05, "k": 13, "n": 25, "cr": "CR:806"},
    "sigma50": {"value": 0.049, "ci95": [0.044, 0.053], "cr": "CR:17"},
    "ratio": {"value": 1.00, "ci": [0.54, 1.83], "cr": "CR:815-816"},
    "cox_hr": {"c3": 17.2, "c4": 19.6, "cr": "CR:852-853"},
    "arch": {"seeds": 25, "median_stall_s": 457, "agents": 3.2, "cr": "CR:857-860"},
    "throat": {"width": 1.0, "c1_mean": 1.20, "c1_sd": 1.96, "c3_mean": 0.80, "c3_sd": 2.87,
               "wilcoxon_c1_c4_p": 0.011, "cr": "Sec 4.5"},
    "evac_reduction_pct": {"w1p0": 9.3, "w1p2": 7.4, "cr": "CR:775"},
    "counterflow_coef": {"value": -5.0, "p_hs": 0.598, "cr": "Sec 4.5"},
    "crossing": {"c2": 16.1, "c1": 5.9, "irr": 2.72, "cr": "Sec 4.5"},
    "fd": {"rows": 4776, "rmse": [0.235, 0.099], "ood_pct": [26, 43], "cr": "Abstract; 4.2; 4.3"},
}


def derive():
    DERIVED.write_text(json.dumps({"script": "experiments/tables/make_table4.py derive", "doc": __doc__,
                                   **CONFERENCE}, indent=1) + "\n")
    print(f"wrote {DERIVED}")


if __name__ == "__main__" and sys.argv[1:] == ["derive"]:
    derive()
    sys.exit(0)

REG = {}
for f in sorted((ROOT / "paper" / "registry").glob("*.yaml")):
    REG.update(yaml.safe_load(f.read_text()) or {})


def have(*names):
    return all(n in REG for n in names)


def M(n):
    if n not in REG:
        raise KeyError(n)
    return "\\" + n + "{}"


def row(claim, status, evidence, where):
    """evidence is a callable returning the cell text; a missing macro turns the row into \\pending."""
    try:
        claim_t = claim() if callable(claim) else claim
        ev = evidence() if callable(evidence) else evidence
        st = status() if callable(status) else status
    except KeyError as e:
        missing = e.args[0]
        if missing.startswith("TabFourConf"):
            raise SystemExit(f"make_table4: conference macro '{missing}' is not registered; run "
                             "make_table4.py derive and check paper/registry/table4.yaml")
        return (claim_t if "claim_t" in locals() else claim, r"\pending{open}", r"\pending{run in progress}", where)
    return claim_t, st, ev, where


def frac(k, n):
    return f"{M(k)}/{M(n)}"


def ci(lo, hi):
    return f"[{M(lo)}, {M(hi)}]"


# ---- pending-row evidence: filled in as each production run is analysed --------------------------------

def ev_throat():
    return (f"{M('EelevenPersistentAll')} overlaps last 0.1\\,s, any arm, $w=1.0$--$1.8$\\,m; TTC removes shorter "
            f"ones (C1 {M('EelevenCOneTimestepsMean')} steps, C2 and C4 0, $p={M('EelevenCFourVsCOneP')}$)")


def st_throat():
    M("EelevenPersistentAll")
    return "revised"


def ev_counterflow():
    raise KeyError("EeightPending")


def ev_crossing():
    raise KeyError("EninePending")


def ev_published_orca():
    raise KeyError("EsixpPending")


ROWS = [
    row(lambda: f"C1 completes {frac('TabFourConfCOneK', 'TabFourConfN')} at $w=0.8$\\,m",
        "revised",
        lambda: f"{frac('EOneACompletionK', 'EOneACompletionN')} {ci('EOneACompletionLo', 'EOneACompletionHi')} "
                "in the published mode; the printed count is one realisation",
        r"\ref{sec:lone}"),
    row(lambda: f"TTC leaves C1's deadlock in place (C2 {frac('TabFourConfCTwoK', 'TabFourConfN')})",
        "confirmed",
        lambda: f"rest-state lemma: C2 reproduces C1 in {frac('EtwoLemmaIdentical', 'EtwoLemmaPairs')} paired runs",
        r"\ref{sec:att-lone}"),
    row(lambda: f"Published ORCA (C3) completes {frac('TabFourConfCThreeK', 'TabFourConfN')}",
        ev_published_orca, ev_published_orca, r"\ref{sec:att-conf}"),
    row(lambda: f"Noise at $\\sigma={M('TabFourConfNoiseSigma')}$\\,m/s completes {frac('TabFourConfNoiseK', 'TabFourConfN')}",
        "confirmed",
        lambda: f"{frac('TabFourNoiseK', 'TabFourNoiseN')} {ci('TabFourNoiseLo', 'TabFourNoiseHi')} in the published mode",
        r"\ref{sec:escape}"),
    row(lambda: f"$\\sigma_{{50}}={M('EfiveConfSigmaFifty')}$\\,m/s",
        "revised",
        lambda: f"{M('EfiveASigmaFifty')} {ci('EfiveASigmaFiftyLo', 'EfiveASigmaFiftyHi')}\\,m/s, "
                f"{M('EfiveAN')} runs per level, logit fit",
        r"\ref{sec:escape}"),
    row("Noise and ORCA resolve deadlocks alike, by symmetry breaking",
        "withdrawn",
        lambda: f"equal completion, other failures ($J={M('EsixJaccard')}$); ORCA acts as a goal drive",
        r"\ref{sec:attribution}"),
    row(lambda: f"Ratio interval [{M('TabFourConfRatioLo')}, {M('TabFourConfRatioHi')}]; Cox HR {M('TabFourConfCoxHR')}",
        "withdrawn",
        "no code reproduces them; replaced by paired differences and Kaplan--Meier medians",
        r"Table~\ref{tab:matched}"),
    row(lambda: f"Frozen arch of {M('TabFourConfArchAgents')} agents in {M('TabFourConfArchSeeds')} seeds",
        "revised",
        lambda: f"lone wall-law trap (criterion exact in {frac('CriterionAgree', 'CriterionN')}); "
                f"{M('ArchPersistent')} persistent arches",
        r"\ref{sec:lone}, \ref{sec:arches}"),
    row("The deadlock belongs to the steering paradigm",
        "revised",
        lambda: f"critical width {M('EsevenWcrit')}\\,m for default walls; short-range jambs "
                f"complete {frac('EsevenBjambK', 'EsevenN')}",
        r"\ref{sec:lone}"),
    row(lambda: f"TTC removes throat overlaps (C1 {M('TabFourConfThroatCOne')} steps, $w={M('TabFourConfThroatW')}$\\,m)",
        st_throat, ev_throat, r"\ref{sec:att-conf}"),
    row("Zonal overlap counts; evacuation unchanged by spawn cleaning",
        "withdrawn",
        "counts come from overlapping spawn positions; evacuation times do change",
        "---"),
    row(lambda: f"C4 shortens evacuation by {M('TabFourConfEvacRedA')}\\% and {M('TabFourConfEvacRedB')}\\%",
        "withdrawn",
        "no stored computation gives these values or the significance marks",
        "---"),
    row("ORCA gridlocks counterflow", ev_counterflow, ev_counterflow, r"\ref{sec:att-conf}"),
    row(lambda: f"TTC triples crossing throughput (ratio {M('TabFourConfCrossIRR')})",
        ev_crossing, ev_crossing, r"\ref{sec:att-conf}"),
    row(lambda: f"Calibrated fundamental diagram; flow {M('TabFourConfOODLo')}--{M('TabFourConfOODHi')}\\% low",
        "withdrawn",
        lambda: f"like-for-like bottleneck: deadlock, or {M('EtenCSigFlowRatio')}--{M('EtenCThreeFlowRatio')} "
                "of the human flow",
        r"\ref{sec:validity}"),
]

CAPTION = (r"Conference findings~\cite{gang2026} and their status in this paper. Revised findings stand in the "
           r"form given as evidence; withdrawn ones are not repeated.")


def write():
    lines = [
        "% generated by experiments/tables/make_table4.py from paper/registry/*.yaml macros; do not edit",
        r"\begin{table}[t]",
        r"\caption{" + CAPTION + "}",
        r"\label{tab:conference}",
        r"\centering\scriptsize\setlength{\tabcolsep}{3pt}",
        r"\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{4.3cm}l>{\raggedright\arraybackslash}Xl@{}}",
        r"\toprule",
        r"Conference finding & Status & Evidence in this paper & Sect. \\",
        r"\midrule",
    ]
    for claim, st, ev, where in ROWS:
        lines.append(f"{claim} & {st} & {ev} & {where} \\\\")
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}", ""]
    OUT.write_text("\n".join(lines))
    n_pend = sum(1 for r in ROWS if "pending" in r[1])
    print(f"wrote {OUT}: {len(ROWS)} rows, {n_pend} pending")


if __name__ == "__main__":
    write()
