# Compliance check: paper/ (LNCS/LNNS)

Scope: paper/main.tex, paper/sections/*.tex, paper/tables/*.tex, ../figures/fig1_caption.tex, paper/refs.bib, main.pdf, main.log, main.blg.
Build state: numbers.tex and tables 1, 3a and 3b are dated 16:47, one minute after main.pdf, main.log and submission/main.tex (16:46). A clean rebuild of a scratch copy (pdflatex, bibtex, pdflatex x2 with the llncs/ class) gives the same PDF text, the same 25 pages and the same 3 overfull boxes, so the findings below hold for the current sources. paper/submission/main.tex should still be regenerated (`make submission`) before upload.

## Summary

| Area | Result |
|---|---|
| Violations | **7 groups, 15 instances** (V1-V7) |
| Borderline / advisory | 8 (B1-B8) |
| Checks passed | 20 (list at the end) |

## Violations

### V1. Overfull boxes: 3 (requirement: 0)
main.log lines 980, 988 and 1002.

| # | Location | Overfull | Fix (each fix below was tested on the scratch copy; with all three applied, main.log has 0 overfull boxes and the PDF stays at 25 pages) |
|---|---|---|---|
| 1 | sections/01_introduction.tex:20 (glossary, "Protocol" item) | 0.63 pt | Change "a perturbation matching the tested mechanism's freed fraction" to "a perturbation that matches the tested mechanism's freed fraction". |
| 2 | sections/03_pedestrian_model.tex:18 (unbreakable `$\rho_i=\max(N_i/\pi R^2,\,0.01\,{\rm m}^{-2})$`) | 35.6 pt | Allow a break after the comma: `$\rho_i=\max(N_i/\pi R^2,$ $0.01\,{\rm m}^{-2})$`. Another option is to reword the sentence so the formula does not fall at the end of a line. |
| 3 | tables/table2_signatures.tex:12-29 (`tabular*` wider than `\textwidth`) | 39.8 pt | Change line 9 to `\setlength{\tabcolsep}{0pt}` (the `\extracolsep{\fill}` still spreads the columns). In lines 17, 18, 26 and 27, split the row labels: `\tl{Reshape,}{axial}`, `\tl{Reshape,}{lateral}`, `\tl{Bias $b^\ast$,}{pair}`, `\tl{ORCA velocity}{filter}`. In line 19, shorten `exponential times` to `exp.\ times`. Splitting the labels alone still leaves 20.5 pt, so all of these changes are needed. Check the table visually after the change. |

### V2. Fig. 1 is never referenced in the text
- sections/01_introduction.tex:2-7 defines `fig:hero` (Fig. 1, page 2), but no `\ref{fig:hero}` appears anywhere in the paper.
- Fix: cite it at its first mention. For example, in 01_introduction.tex:11 write "We study the deadlocks of the last agents at a 0.8\,m evacuation door (Fig.~\ref{fig:hero}) in one social force model ...". Another option is the glossary "Deadlocks" item at line 19.

### V3. Fig. 8 is referenced before Fig. 7 and far from its float
- sections/05_deadlock_physics.tex:52 "(Fig.~\ref{fig:pair}, left)" is the only reference to Fig. 8. It appears in Sect. 5.3 (around page 14), before the first reference to Fig. 7 (06_screening.tex:13), and the float itself is in Sect. 6.4 on page 18.
- Fix: at 05:52, replace "(Fig.~\ref{fig:pair}, left)" with "(Sect.~\ref{sec:att-pair})". Then add the figure reference in Sect. 6.4: at 06_screening.tex:42, "Every held standoff under force-coupled ORCA still moves at 120\,s (Fig.~\ref{fig:pair}; ...)". Alternatively, add it to the static-rule sentence when it is restated at 06:48.
- The other first references are in order: Fig. 2 at 01:18, Fig. 3 at 04:13, Fig. 4 at 05:12, Fig. 5 at 05:20, Fig. 6 at 05:41, Fig. 7 at 06:13, Fig. 9 at 07:25; Table 1 at 01:26, Table 2 at 04:4, Table 3a at 06:13, Table 3b at 06:48.

### V4. The first citation, gang2026, is numbered [14], not [11]
- In reading order, the first `\cite` is gang2026 at 01_introduction.tex:9 (the Fig. 1 caption and the abstract cite nothing). splncs04 sorts the bibliography alphabetically, which puts it at **[14]** (main.bbl item 14). Thirteen entries sort before it: Adrian (fzj_ped20219), Arrhenius, three van den Berg, Beven, Boomers, Chraibi, Cornes, Dergachev, E (2002), E (2007), Fiorini. Entry [11] is e2002.
- Fix: no source change can produce [11] while keeping alphabetical order and the current reference list. Update the [11] expectation to [14]. Alternatively, it would take dropping three of the entries listed above, which is not recommended.

### V5. Bare "ORCA" names a configuration (8 instances)
The vocabulary requires "force-coupled ORCA (RVO2/legacy)" or "the ORCA velocity filter".
| Location | Text | Fix |
|---|---|---|
| sections/06_screening.tex:19 | "so overlap does not separate noise from ORCA" | "... from force-coupled ORCA" |
| sections/06_screening.tex:19 | "the ORCA replays on none" | "the replays of force-coupled ORCA (RVO2) on none" |
| sections/06_screening.tex:29 | "overlap as much as noise and ORCA do" | "... as noise and force-coupled ORCA do" |
| sections/06_screening.tex:48 | "does not separate bias and ORCA" | "... bias and force-coupled ORCA" |
| tables/table2_signatures.tex:31 | "$+b$ (ORCA) exits first" | "$+b$ (force-coupled ORCA) exits first" |
| tables/table3a_noise.tex:30 | "snapshots (ORCA)" | "snapshots (force-coupled ORCA)" |
| tables/table3a_noise.tex:30 | "noise minus ORCA" | "noise minus force-coupled ORCA" |
| tables/table3a_noise.tex:30 | "changes the outcome (ORCA)" | "(force-coupled ORCA)" |

Table 3a is generated by experiments/tables/make_table3.py, so make the note fix in the generator and regenerate the table.

### V6. "matched" used without "fraction-matched at T" (2 instances)
| Location | Text | Fix |
|---|---|---|
| sections/01_introduction.tex:13 | "surrogates matched to ORCA's outcome at one horizon free deadlocks by other physics" | "surrogates fraction-matched to force-coupled ORCA at one horizon $T$ free deadlocks by other physics". This also removes a bare "ORCA" naming a configuration. |
| tables/table2_signatures.tex:25 | `\tl{frees;}{matched at 120\,s}` | `\tl{frees;}{fraction-matched at $T=120$\,s}`. Check the width after the V1 fix; `fraction-matched, $T=120$\,s` is shorter. |

### V7. Out-of-vocabulary term for a quench (1 instance)
- sections/06_screening.tex:24: "The SFM restart frees ...". This is a quench of the snapshot under SFM.
- Fix: "The SFM quench frees ...".
- The "restart(s)" wording in 05_deadlock_physics.tex:18, 39 and 41 and in the Fig. 6 caption (05:35) describes the released-alone tests and the escape experiments, not quenches. It is acceptable there, but see B2.

## Borderline / advisory (not counted)
- **B1. "rate" other than the escape rate.** "attempt rate" appears at 02_related_work.tex:9, 05_deadlock_physics.tex:35 (Fig. 6 caption) and 05:43, 06_screening.tex:31 and 08_discussion.tex:7. The attempt rate is the prefactor $\nu$ of the escape rate $\lambda$ (standard Kramers terminology). Keep it if the rule allows the named prefactor of $\lambda$. Otherwise write "attempt frequency $\nu$". Every other use of "rate" refers to $\lambda$.
- **B2. "restart" vs "quench".** The glossary (01:20) and 03:65 define a quench as "restarts a snapshot". The escape experiments (05:39 "We restarted ... snapshots", "restarts per level") are not quenches. Consider "escape runs" to keep "restart" out of the glossary vocabulary.
- **B3. File paths in source comments.** tables/table1_params.tex:1, table3a_noise.tex:1 and table3b_bias.tex:1 contain generator paths (`experiments/tables/make_table1.py`, `data/params/model.yaml`, `data/derived/rev_A15.json`, `paper/registry/*.yaml`). They are LaTeX comments and do not render, but they are inlined into submission/main.tex. Strip comments in the submission build if the source will be uploaded.
- **B4. Allowed path (no action).** The only rendered file path is `sim/steering/orca.py` in 06_screening.tex:26. It is part of the legacy-solver identification in Sect. 6.1, which the rules allow.
- **B5. CroMa run identifiers.** 07_experiments.tex:12 lists 4D030, 4D040, 4D110, 4D120 and 4D130 (also "4D130: full commitment" and "4D040 and 4D110"). These are the published dataset's run names, not internal run labels, so they are needed for attribution. Keep them unless the rule is meant to cover dataset identifiers too.
- **B6. Table 3a font size.** `\resizebox{\textwidth}` scales Table 3a's `\scriptsize` body to about 6.2 pt, and Table 3b's small notes to about 4.7 pt (PDF pages 16-17). This is below the usual LNCS legibility floor (about 7 pt). Consider removing `\resizebox` and shortening column heads, or using `\tiny`-free abbreviations.
- **B7. Dataset reference [1] (fzj_ped20219).** splncs04 drops the `publisher` of a `@misc` entry, so the rendered reference has no "Forschungszentrum Jülich". The year shows as 2026: DataCite returns 2026 although the DOI is PED.2021.9. Consider `howpublished = {Forschungszentrum J{\"u}lich}`, and confirm the year is intended.
- **B8. "(corresponding author)" in `\institute`.** This is not the standard LNCS marking. Springer accepts it, but the usual form marks the corresponding author's name. No change is required.

Note: the title of gang2026 in refs.bib ("A Diagnostic Methodology ...") is the published title of the cited work, not prose, so it is not a vocabulary violation.

## Checks passed
1. Class: `\documentclass[runningheads,a4paper]{llncs}`. The class in paper/llncs is unmodified Springer v2.24 and identical to submission/llncs.cls; splncs04.bst is identical as well.
2. Title is exactly "Mechanism Screening for Deadlock Resolution in a Social Force Model", and `\titlerunning` is identical (main.tex:25, 27).
3. Two authors with `\orcidID`, `\authorrunning{P. Gang and A. Veluri}`, an institute, and two `\email`s.
4. Abstract: about 231 rendered words (`pdftotext`, page 1, excluding "Abstract." and the keywords), within 150-250.
5. Keywords exactly: Pedestrian dynamics · Social force model · Reciprocal collision avoidance · Activated escape · Bottleneck deadlock · Model validation.
6. `\section`/`\subsection` headings are all in title case. All run-in `\subsubsection` headings end with a period, including `\ackname` and `\discintname`, which the class defines with a period.
7. Length: 25 pages, including references (at the limit; page 25 is about half full).
8. main.log has 0 undefined references or citations and no multiply defined labels. The only warning is the class-standard amsmath `\vec` notice.
9. Figure captions sit below the figures and table captions above the tables (Tables 1, 2, 3a, 3b).
10. All tables use booktabs (`\toprule`/`\midrule`/`\bottomrule`) and have no vertical rules.
11. All 47 bibliography entries are formatted by splncs04 and every one has a DOI.
12. The credits environment (10_back_matter.tex) contains Data and Code Availability, Acknowledgments and Disclosure of Interests, with `\pending` kept for the Zenodo DOI (line 4), the Acknowledgments (line 6) and the Disclosure (line 8).
13. Captions: every caption except Fig. 1 has at most two sentences. Fig. 1 (fig1_caption.tex) has three, which is allowed.
14. Numbering is in order (Figs. 1-9; Tables 1, 2, 3a, 3b), apart from the reference-order issues in V2 and V3.
15. Classes are always named by word (Prevent, Reshape (axial/lateral), Heat, Glitch), never by letter.
16. "SFM+ORCA" and "velocity coupling" never appear.
17. No section or subsection opens with a question, and there is no "?" anywhere in the sections.
18. No clinical or process vocabulary (diagnostic, symptom, pathology, audit, session, wave, batch) and no internal run labels (E2, E10, N1, ...) in the rendered text or the section sources.
19. No mention of any AI tool, assistant, model name or vendor anywhere under paper/ (the sources, notes, registry and submission/).
20. Every cited key exists in refs.bib. BibTeX reports 47 entries and 0 warnings (main.blg `warning$ -- 0`, no warning lines).
