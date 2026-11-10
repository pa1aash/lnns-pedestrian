# Compliance audit (final rewrite, wt-W, 2026-11-10)

Scope: paper/main.pdf as built at 06:17 IST (newer than every source file), sources paper/main.tex,
paper/sections/*.tex, paper/tables/*.tex, figures/*.tex, figures/*.pdf, figures/ALT_TEXT.md, tools/make_submission.sh.
A snapshot of paper/, figures/ and tools/ was rebuilt and `make_submission.sh` was run in a private scratch directory
outside the repository; nothing in the worktree was edited except this report.

Summary: items 1, 2, 4, 6, 7 PASS (with minor notes); item 3 FAIL (one sentence); item 5 FAIL (one tracked report).

## 1. LNCS format — PASS (minor notes)

| Check | Result |
|---|---|
| llncs.cls unmodified | PASS. paper/llncs/llncs.cls is v2.24 (2024/01/29), added in ff95784 and never changed since (git log); SOURCE.txt records the Springer download. No TeX-distribution copy exists for a byte diff. |
| Class options | PASS. `\documentclass[runningheads,a4paper]{llncs}`. |
| Title / \titlerunning | PASS. Both are "Mechanism Screening for Deadlock Resolution in Pedestrian Steering Models"; the odd-page head fits on one line with the page number (rendered p. 3, 5, 15). |
| Authors, ORCID, institute, e-mail, \authorrunning | PASS. Two authors with \orcidID, one institute, two e-mails, "P. Gang and A. Veluri". |
| Abstract 150–250 words | PASS. About 200 words (pdftotext, 214 words including "Abstract." and keywords). No citation. |
| Keywords | PASS. Exactly: Pedestrian dynamics · Social force model · Reciprocal collision avoidance · Activated escape · Mechanism screening. |
| Headings | PASS. 1 Introduction · 2 Related Work · 3 Pedestrian Model (… 3.5 Statistics) · 4 Mechanism Classes and the Screening Protocol · 5 Deadlock Physics (5.1–5.4 as specified) · 6 Screening Results (6.1 The Lone Trap, 6.2 Whole Runs, 6.3 The Pair Standoff, 6.4 Velocity Coupling of ORCA) · 7 Comparison with Experiments · 8 Discussion (8.3 Using the Framework with the checklist (i)–(v)) · 9 Conclusions. |
| No \paragraph run-ins | PASS. No `\paragraph` anywhere; leads use `\subsubsection{…}`. |
| Caption position | PASS. All 9 figure captions follow the graphic; all 3 table captions precede the tabular. |
| Caption length | PASS. Every caption has <= 3 sentences (Figs. 5 and 9: 3); protocol figure (Fig. 2): 2. |
| Every float referenced | PASS. fig:hero, fig:protocol, fig:lone-trap, fig:width, fig:escape, fig:dt, fig:quench, fig:pair, fig:croma, tab:params, tab:signatures, tab:matched all have >= 1 \ref. |
| Overfull/underfull boxes, undefined references | PASS. paper/main.log has no Overfull, Underfull, undefined or multiply-defined warnings; no "??" in the PDF text. |
| Bibliography style | PASS. `\bibliographystyle{splncs04}`. |
| Page count | PASS, at the limit: 24 pages (pdfinfo). The Sect. 6.4 results and the Table 3 row still to come will push past 24 unless text is cut elsewhere. |
| Protocol flowchart (figures/fig_protocol.tex) | PASS. Rendered p. 8: five boxes fill \textwidth exactly, no overflow, \scriptsize text legible, arrows connect. Boxes 1, 3 and 4 are about half empty because `\bodyh` is fixed at 2.75 cm (cosmetic; reducing it to ~2.3 cm would save ~4 mm). |
| Other figures | PASS. Figs. 1, 3–9 rendered and read; tick labels and legends legible at print size. |

Minor defects found during item 1 (not blocking):

- paper/sections/05_deadlock_physics.tex, Fig. 4 caption: "labelled by the wall range in metres ($B_w$ on all walls,
  $B_{w,\rm edge}$ on the jambs only; right)" — three of the seven tick labels ("rounded", "line goal", "line + rounded")
  are wall-shape variants, not ranges. Fix: "labelled by the wall-law variant (numbers: wall range in metres, $B_w$ on all
  walls or $B_{w,\rm edge}$ on the jambs only; right)".
- paper/sections/06_screening.tex l. 25 prints "differs from ORCA's by -0.01 [-0.09, 0.07]" (PDF p. 15) with a text-mode
  hyphen as minus sign (macros \FixAtwoLoneDelta, \FixAtwoLoneDeltaLo). Fix: wrap in math, `$\FixAtwoLoneDelta$
  [$\FixAtwoLoneDeltaLo$, $\FixAtwoLoneDeltaHi$]`, or have `make numbers` emit `$-$`.
- paper/main.tex, `\pending` definition: the red colour leaks into the following run-in headings, so "Acknowledgments."
  and "Disclosure of Interests." print red (p. 22). Draft-only (disappears when the pendings are filled). Fix:
  `\DeclareRobustCommand{\pending}[1]{\iffinal…\else\leavevmode\textcolor{red}{[#1]}\fi}`.
- Sect. 7 run-in leads use title case ("Experiments and Model Runs.", "Human Runs.", "Model Variants.", "Removing
  Deadlocks.") while Sects. 2 and 6 use sentence case ("Steering models.", "Rate-matched noise."). Fix: sentence case in
  paper/sections/07_experiments.tex ll. 11, 16, 19, 22.

## 2. Vocabulary — PASS

Searched paper/main.tex, paper/sections/*.tex, paper/tables/*.tex, figures/*.tex, the PDF text (pdftotext) and the text
of figures/fig2–fig8 PDFs for: calibrate-then-falsify, control, intervention, arm(s), treatment, trial(s), endpoint,
control group, placebo, efficacy, held out/held-out, pre-registered, decision rule, C1–C4, published, corrected-forward,
mode(s), crush, Main Differences, attribution, conference, what is new.

| Hit | Context | Verdict |
|---|---|---|
| "crowd crushes" (01_introduction.tex l. 9; PDF l. 38) | "Fatal crowd crushes happen where many people press towards a narrow opening" | OK: real-world disasters, not the removed crush term. |
| "control barrier functions" (02_related_work.tex l. 12) | "multi-robot systems that avoid collisions through control barrier functions" | OK: name of a robotics method, not a matched control. |
| "unstable mode", "soft mode", "opposed lateral mode" (05_deadlock_physics.tex ll. 43, 52, 54) | Hessian eigenmodes | OK: physics sense, not code modes. |
| "failure-mode ablation" (bibliography, ref. 11 title) | title of the conference paper | OK: bibliographic title. |
| "Conference" (bibliography refs. 11, 21) | venue names | OK. |
| `\label{sec:attribution}` (06_screening.tex l. 1) | label only, never printed | OK (label names kept by rule). |

No hits in the figure PDFs. No legacy terms (published solver/ORCA, corrected-forward, C1–C4, matched control) remain.

## 3. Conference paper — FAIL (one sentence)

- PASS: `\cite{gang2026}` (printed [11]) is the first citation in the text, in the opening paragraph of the Introduction;
  Fig. 1's caption has no citation and the abstract has none. gang2026 is cited nowhere else.
- PASS: no conference-audit text, no Table 4, no labels sec:conference / tab:conference / sec:att-conf, no removed macros
  (Eeight*, Enine*, Eeleven*, TabFour*, KeystoneA*, EOneA*, EfiveASigmaFifty, FixAsixSigFiftyPub*, Esixp*, EtenCPub*,
  FixAsevenCPub*, EfiveConf*) in any source.
- FAIL: paper/sections/01_introduction.tex l. 9: "Our earlier work tested such a credit at the level of rates, with a
  surrogate tuned to a mechanism's headline rate~\cite{gang2026}; the present work supersedes that reading." The clause
  "the present work supersedes that reading" judges the conference paper against this one (a what-is-new statement).
  Fix: delete "; the present work supersedes that reading" and end the sentence after `\cite{gang2026}.`

## 4. Back matter and \pending — PASS

- Data and Code Availability names https://github.com/pa1aash/deadlock-screen and "Zenodo (DOI \pending{Zenodo DOI})".
- Acknowledgements and Disclosure of Interests are `\pending` (inside `credits`, using \ackname and \discintname).
- Red \pending text in the PDF (PyMuPDF colour scan): exactly 5, as expected.
  1. p. 16, Table 3 row "ORCA (RVO2), velocity coupling": [results of Sect. 6.4] (paper/tables/table3_matched.tex l. 29)
  2. pp. 18–19, Sect. 6.4: [velocity-coupled ORCA results: lone keystones freed, pair standoffs freed, replay, whole-run
     completion] (paper/sections/06_screening.tex l. 57)
  3. p. 22: [Zenodo DOI]
  4. p. 22: [acknowledgements, written by the authors]
  5. p. 22: [disclosure of interests, written by the authors]
  The Fig. 1 fallback `\pending{Fig 1 caption}` in 01_introduction.tex l. 5 is not printed (figures/fig1_caption.tex
  exists). `make_submission.sh` also counts 5.

## 5. No AI-tool mentions in tracked files — FAIL

Case-insensitive `git grep` over all tracked files for the names of AI tools, assistants, models and vendors:

- reports/integration/numbers.md l. 8: a scratch-directory path containing the tool's name ("Check scripts (scratch,
  not committed): `/private/tmp/<tool>-501/…/scratchpad/check_macros.py`"). Fix: replace the line with "Check scripts
  (scratch, not committed): check_macros.py (registry -> recomputed value -> numbers.tex -> usage) and expand.py".
- paper/refs.bib l. 374: the author name of Latombe — OK (substring match only).

The paper sources and the PDF are clean.

## 6. figures/ALT_TEXT.md and hero resolution — PASS

- Nine entries, Fig. 1–9, in paper order, matching the printed numbering: 1 hero (fig1_hero.tex), 2 protocol
  (fig_protocol.tex), 3 fig2_lone_trap, 4 fig3_width_walls, 5 fig4_escape, 6 fig5_dt, 7 fig6_quench, 8 fig7_pair,
  9 fig8_croma. The note on the one-behind script numbering is correct. Content agrees with the rendered figures
  (five protocol boxes and their probes; four biases and three noise levels in Fig. 7; four noise levels in Fig. 8;
  four model variants in Fig. 9).
- Minor: Fig. 4 entry says the dark-grey bar is "lone trap" while the caption says "stack of stuck-alone agents"; use one
  name.
- figures/fig1_hero.png: PIL `.info['dpi']` = (599.9988, 599.9988), i.e. 600 dpi; 2882 x 1523 px.

## 7. `make submission` — PASS

tools/make_submission.sh (read, and run on the scratch snapshot, not in the worktree):

- Section files: latexpand inlines every `\input` of paper/main.tex, so the renamed files sections/00_abstract …
  10_back_matter are taken from main.tex as listed; no file names are hard-coded.
- figures/fig_protocol.tex: `\input{../figures/fig_protocol.tex}` is inlined (by latexpand, else by the Python
  fallback loop, which resolves `../figures/` relative to paper/). It is pure TikZ with no external files, so nothing
  needs copying; the inlined main.tex contains the tikzpicture.
- Fig. 1: `\IfFileExists{../figures/fig1_caption.tex}` is resolved and the overlay `\input{\overlayfile}` is inlined
  by the macro-path fallback (latexpand prints a harmless "Could not find file [\overlayfile]" warning).
- Scratch result: "main.tex written (2064 lines), 8 figure files"; standalone compile OK, 0 errors, 24 pages,
  0 undefined; 5 `\pending` occurrences.
