# P2 compliance and consistency audit (paper/main.pdf built 12:11:48, 26 pages)

Inputs read: paper/main.tex, paper/sections/*.tex, paper/tables/*.tex, figures/fig1_caption.tex, figures/fig_protocol.tex,
paper/numbers.tex (macro values), paper/main.log, paper/main.blg, paper/main.bbl, `pdftotext paper/main.pdf`.
The log (12:11:48) is newer than every source file (latest 12:11:35), so it describes the current sources.
`%C2:` placeholder lines were ignored. No paper file was edited.

| # | Item | Verdict | Fixes |
|---|------|---------|-------|
| 1 | LNCS/LNNS layout | PASS | 0 |
| 2 | Captions and float order | FAIL | 2 |
| 3 | Vocabulary v4 | FAIL | 5 |
| 4 | R11 (activated escape / by fluctuations) | FAIL (minor) | 2 |
| 5 | Cross-section consistency and pointers | FAIL | 7 |
| 6 | Citations | PASS | 0 |
| 7 | Build log and page count | PASS | 0 |

Total fixes: 16.

---

## 1. LNCS/LNNS layout — PASS

- Class: `\documentclass[runningheads,a4paper]{llncs}`; paper/llncs/llncs.cls is the unmodified Springer v2.24 (paper/llncs/SOURCE.txt), and main.fls loads it from there.
- Title "Mechanism Screening for Deadlock Resolution in a Social Force Model" (matches ruling); `\titlerunning` is the full title and fits the odd-page head; `\authorrunning{P. Gang and A. Veluri}`.
- Author block: both authors with `\orcidID{...}` (print as superscript brackets), `\institute{Indus International School, Pune, India}` with both `\email`s.
- Abstract: 248 words in the PDF (count of tokens containing a letter or digit, without the "Abstract." label; 258 if every math symbol counts as a word). At the limit: any addition to the abstract must be paid for by a cut (see fix 5.C1c).
- Keywords: exactly six, separated by `\and`, matching the required list verbatim (00_abstract.tex l.4).
- Headings: all section, subsection and run-in headings are in title case; every `\subsubsection` (Contributions., Steering Models., ..., Flow, Gaps and Velocity Fluctuation.) ends with a period. Numbering 1-10 and 3.1-6.4 sequential.
- `credits` environment present (10_back_matter.tex) with Data and Code Availability., Acknowledgments. (`\ackname`), Disclosure of Interests. (`\discintname`).
- `\bibliographystyle{splncs04}`; `\usepackage{cite}` loaded (main.tex l.12).
- No `\vspace`, `\vskip`, `\enlargethispage`, `\linespread`, `\looseness` or font-size change of body text in main.tex or sections. Notes (not failures): main.tex redefines float fractions (`\topfraction` etc.) and `\emergencystretch`, and loads `placeins[section]`; these do not touch the text block. The only `\scriptsize` outside a float is the inline CroMa tabular in Sect. 7 (see 2.F2).
- Outstanding for the final build (not a format failure): three red `\pending` placeholders in the credits (Zenodo DOI sentence, Acknowledgments, Disclosure of Interests); `\finaltrue` is commented out in main.tex, so they compile.

## 2. Captions and float order — FAIL (2 fixes)

Placement: all five tables carry `\caption` above the tabular; all nine figures carry it below. PASS.

Float order in the PDF (page: float; first reference):
- Fig. 1 hero p2 (ref p2), Fig. 2 geometry p7 (p7), Fig. 3 protocol p9 (p8), Fig. 4 lone trap p12 (p11), Fig. 5 width/walls p13 (p12), Fig. 6 escape p13 (p13), Fig. 7 quench p17 (p15), Fig. 8 pair p19 (p18), Fig. 9 CroMa p21 (p21).
- Table 1 tab:params p5 (p3), Table 2 tab:signatures p9 (p8), Table 3 tab:observed p16 (p9 in Table 2's note, p15 in text), Table 4 tab:matched-noise p18 (p15), Table 5 tab:matched-bias p19 (p19).
- Order of first reference = numbering order for figures and tables; Tables 1-5 are tab:params, tab:signatures, tab:observed, tab:matched-noise, tab:matched-bias as required. PASS.
- Advisory: Fig. 7 (p17) and Table 4 (p18) sit two and three pages after their first reference (p15); they are referenced before the float, so the rule is met, but moving `\input{tables/table4_noise}` below the "Fraction-Matched Noise." paragraph in 06_screening.tex would bring it closer.

Caption length (at most two sentences, Fig. 1 exempt): Figs. 2, 3, 4, 5, 7, 8, 9 and Tables 1-5 have one or two. Fig. 1 (figures/fig1_caption.tex) has three, allowed.

- **F1** Fig. 6 caption has three sentences. 05_deadlock_physics.tex l.36: replace
  `(dashed, 0.9). (c) Relative to $\Delta t=0.01$\,s` with `(dashed, 0.9); (c) relative to $\Delta t=0.01$\,s`.
- **F2** Sect. 7 contains an uncaptioned, unnumbered table set in `\scriptsize` in running text (07_experiments.tex l.22-31, `\begin{center}\scriptsize ... \end{center}`) followed by its note as a body paragraph (l.32 "Running: still moving at 600\,s; ..."). Fix: make it a float `\begin{table}[t]\caption{Outcomes of the 25 CroMa model runs per variant.}\label{tab:croma} ... \end{table}` with the "Running: ...; censored: ...; max. gap: ..." line as its table note, and replace "(Fig.~\ref{fig:croma}; 25 runs per variant):" by "(Fig.~\ref{fig:croma}, Table~\ref{tab:croma}).". It becomes Table 6 and leaves Tables 1-5 in order.

## 3. Vocabulary v4 — FAIL (5 fixes)

Clean (0 hits outside allowed places): "four classes", "four mechanism", "class P/L/T/D/N", "rate-matched", "snapshot library", "library barriers", `\varsigma` (logistic is $S(x;x_0,c)$, Eq. 6), tau_ij (collision time is $t_c$, Eq. 5 and Sect. 2), J for the overlap (overlap is `\Omega`, Sect. 4.6, 6.1, 6.2, Tables 4-5; every remaining J is the joule). "Glitch" appears once, at the definition in Sect. 4.1 (04_protocol.tex l.5). Class names Prevent/Reshape/Heat appear only in Sect. 4.1, Tables 2-3 and the protocol figure; none as bare nouns in running text. "screening set" is used consistently with Sect. 3.4 (03 l.67; 06 l.16, 25, 31; Table 3 note). "drive plus drive part" is used where the tau' model is meant (abstract, contributions, Sect. 3.2 l.48); "drive part alone" in 6.1 l.16 and 6.3 l.51 means the drive-part-only quench, correct.

- **V1** "rate" for a non-escape-rate quantity. Fig. 6 caption, 05_deadlock_physics.tex l.36: "fitted escape rate over the fitted attempt rate" -> "fitted escape rate over the fitted attempt frequency" (the text and Sect. 2 call $\nu$ the attempt frequency).
- **V2** Bare "ORCA" naming the configuration's part. Abstract, 00_abstract.tex l.3: "the drive plus ORCA's drive part is the model" -> "the drive plus its drive part is the model" (subject is force-coupled ORCA; one word shorter).
- **V3** Bare "ORCA" naming a configuration. 01_introduction.tex l.13: "its social force model with ORCA and its noise surrogate" -> "its social force model with force-coupled ORCA and its noise surrogate".
- **V4** "rest drive" used for the drive part, against its definition (Sect. 3.2: the rest drive is the total goal-directed force at rest, for force-coupled ORCA the drive plus the drive part). figures/fig1_caption.tex: "blue, force-coupled ORCA's rest drive, its drive part;" -> "blue, the drive part that force-coupled ORCA adds to the rest drive;". (Also for the figure owner: the Fig. 1 graphic carries a bare "ORCA" label next to the added-drive arrow.)
- **V5** Set name. 04_protocol.tex l.20: "positive definite at all \RevAtenStrict\ lone-trap snapshots" (60 = the screening set, which includes 26 second traps) -> "positive definite at all \RevAtenStrict\ screening-set snapshots".

## 4. R11 — FAIL, minor (2 fixes)

"Activated escape" is claimed only with the blocker alone at beta >= 1.5: abstract l.3, contributions (01 l.21), Sect. 4.1 (high-barrier limit, tested at beta >= 1.5), Sect. 5.2 l.42, conclusions; keyword list. Sect. 6.2 l.37 and 8.2 l.14 state that the whole-run prediction extrapolates below that range. The matched noise acts "by fluctuations" in the abstract, contributions (01 l.22), Sect. 4.1 (Heat definition), 5.2 l.45, 6.1 l.19, 6.2 l.37 and 10. Remaining gaps:

- **R1** Sect. 8.1 (08_discussion.tex l.4) does not say how the matched noise acts ("free deadlocks through different forces"). Replace with: "force-coupled ORCA frees deadlocks through its rest drive, the matched noise by fluctuations and the lateral bias by tilting the pair standoff out of its minimum (Tables~\ref{tab:signatures} and~\ref{tab:observed}), while ...".
- **R2** Table 2 Heat row, Quench cell "frees, exp. times" (table2_signatures.tex l.20) states the activated-escape prediction for the whole class, and Table 3 assigns Heat to the matched noise at median beta 0.64. Change the cell to `\tl{frees; exp.\ times}{at $\beta\ge1.5$}` (or add to the note: "exp. times: activated escape, $\beta\ge1.5$").

## 5. Consistency and pointers — FAIL (7 fixes)

References: main.log has 0 undefined references, 0 multiply-defined labels, 0 LaTeX warnings. Every Sect./Eq./Fig./Table pointer was opened and checked against the content of its target (e.g. Sect. 6.1 for the sign defect, 5.3 for rounded ends, 4.2 for the horizon window, 4.4 for the blocker's tau, Fig. 6(c) for the time step, Eq. (2) for the throttle, Eq. (7) for the identity, Eq. (11) for ell; the waiting zone referenced to Fig. 2 is labelled in the graphic). All correct.

Headline numbers (required in abstract, contributions, conclusions and the one establishing results place only):

| Number | Abstract | Contributions | Conclusions | Establishing place | Elsewhere |
|---|---|---|---|---|---|
| Flow ratio 0.40-0.60 | yes | yes | yes | Sect. 7 last para | none |
| Arrhenius slope 0.85-0.93 | yes | **no** | **no** | Sect. 5.2 | none |
| Drive ratio 1.8-2.2 | yes | yes | **no** | Sect. 3.2 | none |
| tau' 0.22-0.27 s | **formula only** | yes | **no** | Sect. 3.2 | none |
| w50 = 0.878 m | **no** | yes | yes | Sect. 5.1 | none |

(The brief's "0.86-0.93" is now 0.85-0.93: `\RvAthreeRatioDeep` = 0.85.)

- **C1a** Contributions bullet 1 (01 l.21): "noise at $\beta\ge1.5$ frees it by activated escape (Sect.~\ref{sec:escape})" -> "noise at $\beta\ge1.5$ frees it by activated escape with an Arrhenius slope \RvAthreeRatioDeep--\RvAthreeRatioMid\ of the computed barrier (Sect.~\ref{sec:escape})".
- **C1b** Conclusions (09 l.2): "Force-coupled ORCA frees the lone trap through the rest drive that its drive part adds." -> "Force-coupled ORCA frees the lone trap through the rest drive that its drive part adds: the drive plus the drive part is this model with $\tau'=\RevAoneTauPrimeLo$--$\RevAoneTauPrimeHi$\,s and \RevAoneDriveRatioLo--\RevAoneDriveRatioHi\ times the rest drive." and "activated escape is established only with the blocker alone at $\beta\ge1.5$" -> "activated escape, with an Arrhenius slope \RvAthreeRatioDeep--\RvAthreeRatioMid\ of the computed barrier, is established only with the blocker alone at $\beta\ge1.5$".
- **C1c (with C2)** Abstract (00 l.3), word-neutral: replace "At a wall range of 0.04\,m, \EsevenBallK--\EsevenBjambK\ of \EsevenN\ runs complete and \EsevenBjambCollective\ of \EsevenBjambClassified\ deadlocks (jambs only) are pair or group standoffs." with "Half the runs complete at a door width $w_{50}=\RevBtwoWfifty$\,m; with a jamb range of 0.04\,m, \EsevenBjambK\ of \EsevenN\ complete and all \EsevenBjambClassified\ deadlocks are pair or group standoffs." and replace the formula "$\tau'=\tau\tau_{\rm orca}/(\tau+\tau_{\rm orca})$" with "$\tau'=\RevAoneTauPrimeLo$--$\RevAoneTauPrimeHi$\,s". Recount after the edit (limit 250).
- **C2** (resolved by C1c, or alternatively) the abstract number \EsevenBallK\ = 85 (wall range 0.04 m on every wall) is not reported anywhere in the text; Sect. 5.1 l.25 lists the default, jamb, rounded and line-goal variants but not the all-walls variants shown in Fig. 5 (right). If the abstract keeps 85, add to Sect. 5.1: "With $B_w=0.04$\,m on every wall \EsevenBallK\ runs complete."
- **C3** Limitations contradict the results. 08_discussion.tex l.12: "All runs use $\Delta t=0.01$\,s; only the arches at \ArchVZero\,m/s were checked at finer steps." The time-step probes run at 0.005 and 0.02 s (Sects. 4.4, 5.2 "the time step raises the ratio by under 1%", 6.1, Fig. 6(c), Table 4) and the arches at 0.0025, 0.001 and 0.01 s. Replace with: "Apart from the time-step probes ($\Delta t=0.005$ and 0.02\,s, Sects.~\ref{sec:teff} and~\ref{sec:att-lone}) and the arch runs (Sect.~\ref{sec:arches}), all runs use $\Delta t=0.01$\,s."
- **C4** Sect. 5.1 l.17: "the \FinCritNegN\ others belong to pair standoffs" vs Sect. 3.4 l.67 "\FinCritNegN\ group standoffs" (and reports/C_REPORT.md l.28: "group standoff (2)"). Replace with "the \FinCritNegN\ others are group standoffs".
- **C5** Sect. 7 l.20: "The flow ratio is \RvAnineCOneLongRatio\ (SFM) to \RvAnineCThreeLongRatio\ (force-coupled ORCA) with the 2.0\,m bottleneck and \RvAnineCOneShortRatio\ to \RvAnineCThreeShortRatio\ with the 0.2\,m one" reads as the range over variants, but the noise variant (0.40 overall, inline table) lies below both lower ends, contradicting "every variant passes 0.40-0.60". Replace with "The flow ratios of SFM and force-coupled ORCA are \RvAnineCOneLongRatio\ and \RvAnineCThreeLongRatio\ with the 2.0\,m bottleneck and \RvAnineCOneShortRatio\ and \RvAnineCThreeShortRatio\ with the 0.2\,m one" (or add the per-geometry noise and jamb-range ratios if the registry has them).
- **C7** Sect. 8.1 (08 l.4): "the rest-drive push agrees with force-coupled ORCA on every defining probe" holds at the lone keystone only: at the pair the push frees \PairFrozenPlusFreed\ = 34 of 46 against \PairRvoFreed\ = 7 (RVO2) and 21 (legacy) (Sect. 6.3, Table 3 footnote e). Scope it: "while at the lone keystone the rest-drive push agrees with force-coupled ORCA on every defining probe".

Checked and consistent: abstract, contributions, Sects. 8-10 on the three classes and defect flag, the velocity filter ("frees no deadlock"; whole-run 1 of 100 equals SFM), replay/time-step separation, the sign defect, five CroMa runs with no participant deadlock, rounded ends (0 of 320 against 46) in contributions, 5.3 and Recommendation (ii), the throttle in 3.1, 8.2 and 9(vi), margin 0.10 in 4.2 and 6.1-6.3, set sizes (60/56/20/10/46; 4 rejected strings = 4 failing second traps), Table 5 and 8.2 interval [-0.15, 0.22] (different macros, equal values).

## 6. Citations — PASS

- First citation in reading order: `\cite{gang2026}` in the first paragraph of Sect. 1 ("The conference paper [13]"); abstract and Fig. 1 caption carry none. It prints as **[13]**, not [14] as the common brief states (splncs04 sorts alphabetically: fzj, vandenberg x3, beven, boomers, chraibi x2, cornes, dergachev, e x2, gang). No literal "[14]" or "[13]" is typed in the sources.
- 44 distinct keys cited; all exist in refs.bib (refs.bib holds 167 further uncited entries, which BibTeX ignores).
- Grouped citations print sorted and compressed: [1, 6], [9, 36], [11, 12], [17, 18], [19, 30, 31], [20, 22] (twice), [24, 39].
- main.blg: 44 entries, `warning$ -- 0`, no warnings or errors.

## 7. Build — PASS

main.log: 0 errors, 0 Overfull boxes, 0 Underfull boxes, 0 undefined references or citations, 0 LaTeX warnings. pdfinfo: 26 pages, A4 (595.276 x 841.89 pt), at the 26-page target and under the 28-page cap. Fix F2 (CroMa table as a float) may move floats; rebuild and recheck the page count.
