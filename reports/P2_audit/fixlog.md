# P2 audit fix log (compliance.md, prose.md, numbers.md finding 6)

Files edited: paper/sections/00-10 (all), paper/tables/table2_signatures.tex, table3_observed.tex, new
paper/tables/table6_croma.tex, experiments/tables/make_tables45.py (regenerated table4_noise.tex; table5_bias.tex
unchanged). make_table1.py not touched (no entry needed it). Every `%C2:` line kept (identical set before/after).
Build: 26 pages, 0 errors, 0 undefined references, 0 overfull boxes. Abstract 249 words (strict count: formula = 1,
macro = 1, number and unit = 2). Length: free space at the end of p. 26 is 23 bib-line heights (HEAD: 17); slack test
(blank lines added before the bibliography until p. 27 appears) gives 20 body lines (HEAD: 18), so the fixes add no net length.

## Decisions taken by the coordinator (all applied)
- Table 6 (tab:croma, tables/table6_croma.tex), captioned float, one-sentence caption, column definitions in a note,
  \input in Sect. 7, referenced "(Fig. 9, Table 6)". Redundant "Censored" column dropped (= Deadlock + Running).
- Defect flag: Sect. 4.1 reads "carries the defect flag (Glitch) when outcomes it produces vanish in the corrected
  implementation"; same wording in contribution 3 and the Fig. 3 caption. Table 3 flag cells state what vanishes:
  lone traps "flips vanish; yes", pair "excess vanish; yes", note c: "Lone traps: replay changes vanish, freed set
  unchanged; pair standoff: 21 freed fall to 7 (McNemar p < 10^-3)". Sect. 6.1 legacy paragraph: replay flips are the
  replay sensitivity; they vanish in the corrected implementation, as do the pair standoffs freed beyond the RVO2
  solver's, so the corrected-implementation probe sets the flag.
- Sect. 5.1 wall variants now report what Fig. 5 shows: default, all walls 0.04 and 0.02 m (\EsevenBallK,
  \EsevenBallTwoK), jambs 0.04 m, rounded, line goal, line + rounded.
- Fig. 8 caption: SFM/SFM+TTC claim dropped; "Noise rows are not shown (Sect. 5.3)".
- Six radii named at the 276 cases (r_c = 0.1, 0.05, 0.02, 0.01, 0.003, 0.001 m).
- Onsets: Sect. 4.2 "equality ... is not rejected only from a horizon on: 70 s ... 85 s ... 425 s"; Sect. 6 keeps
  "equivalent within +-0.10 ... from" (89/86 s) and "only for T from 545 to 600 s".
- SFM statements scoped: "SFM and SFM+TTC free none of the screening set"; "The SFM quench frees 2 blockers, both
  outside the screening set" (checked in data/derived/rev_A5x.json: E2 C1 freed 0/26; freed tags E1b_seed56, seed184).
- Table 4 caption: "excludes 0" clause dropped (note keeps "Intervals are unadjusted").
- Headline numbers: abstract has tau', drive ratio, Arrhenius slope, flow ratio; contributions and conclusions have all
  five; each establishing place keeps its own values (Sect. 3.2, 5.1, 5.2, 7). The repeated range sentence in Sect. 5.2
  removed. w50 NOT in the abstract: adding it costs ~10 words at a 249-word abstract (logged, as allowed).
- Limitations dt sentence scoped ("Apart from the time-step probes (Sects. 4.4, 6.1) and the arch runs (Sect. 5.4),
  all runs use dt = 0.01 s"). Sect. 8.1 rest-drive-push claim scoped to the lone keystone.
- "attempt rate" -> "attempt frequency" (Fig. 6). Bare "ORCA" configurations -> "force-coupled ORCA" (abstract, Sect. 1).

## compliance.md (17 IDs: 15 applied, 1 partly (C1c), 1 passed to the figure session (V4))
- F1 applied (Fig. 6 caption one sentence). F2 applied (Table 6).
- V1 applied. V2 applied ("the drive plus its drive part"). V3 applied. V4 NOT EDITED: figures/fig1_caption.tex
  belongs to the figure session (listed below). V5 applied ("screening-set snapshots").
- R1 applied (Sect. 8 opening names rest drive, fluctuations, tilt). R2 applied (Table 2 Heat: "frees; exp. times at
  beta >= 1.5").
- C1a applied. C1b applied. C1c partly: tau' values replace the formula; w50 left out (word limit); jamb sentence
  already in place. C2 applied (85 gone from abstract; all-walls counts in Sect. 5.1). C3 applied. C4 applied
  ("are group standoffs"). C5 applied. C7 applied.

## numbers.md finding 6 (IMPRECISE), prose-fixable ones
- 18 applied: "is 1.4 times g_max = 160 N" -> "exceeds g_max = 160 N" (printed 214/160 = 1.34 no longer quoted).
- 20 applied: the 1.49 ped/s window flow dropped; the window sentence gives only the ratio 0.54-0.64.
- 21 applied: "(smallest eigenvalue >= 66 N/m)" replaces the mixed-notation range.
- 17, 19, 22 declined: macro precision (digits/rounding in paper/registry), not prose.

## prose.md (about 204 entries: about 158 applied, 9 partly, 16 declined, 6 for the figure session, about 15 kept by ruling or needing no action)
Applied unless marked. "F3" = needs the figure session (figure files/fig1_caption.tex not edited).
1.1 applied (no "not X, but Y"). 1.2 applied. 1.3 applied.
3.1 declined: Sect. 7's range sentence is the establishing place of the flow-ratio headline (coordinator rule); it now
  says "over whole runs" (also 14.5). 3.2 applied. 3.3 applied. 3.4 applied. 3.5 applied. 3.6 applied. 3.7 applied.
4.1 applied. 4.2 applied ("and the resulting bracket is consistent with"). 4.3 applied. 4.4 applied. 4.5 applied
  (symbol N dropped). 4.6 applied in Sect. 5.2 ("two candidate causes ... are untested"); the extra limitations clause
  declined (adds length, no error). 4.7 applied. 4.8 applied. 4.9 applied. 4.10 applied. 4.11 applied (labels defined
  before use). 4.12 applied. 4.13 applied. 4.14 applied. 4.15 applied. 4.16 applied. 4.17 applied. 4.18 applied.
5.1 applied. 5.2 applied. 5.3 declined: naming a building code needs a citation and refs.bib is outside this pass
  (outstanding: cite the code or drop "code-compliant"). 5.4 applied. 5.5 applied. 5.6 applied. 5.7 declined (taste).
  5.8 applied. 5.9 declined (B_w = 0.04 m already in the same sentence). 5.10 kept (ruling).
6: nothing to do.
7.1 partly: subsection 4.2 renamed "Fraction Matching and Separation"; section title kept (taste). 7.2 applied
  ("Second Traps." / "The Legacy Solver."). 7.3 declined (taste). 7.4 applied ("Lone Keystones and Second Traps",
  "Pair Standoffs"). 7.5 applied (heading dropped, Limitations run-in). 7.6 applied ("Rest-State Physics").
  7.7 applied. 7.8 declined (taste).
8.1 F3 (Fig. 1 caption). 8.2 applied. 8.3 applied in caption; box label "frozen deadlocks" -> "snapshots" is F3.
  8.4 applied. 8.5 applied. 8.6 applied ("attempt frequency"; dashed line = transition-state prediction 0.90, from
  figures/fig_escape_dt.py; s defined in the caption); axis relabel is F3. 8.7 applied. 8.8 applied (grid moved to
  Sect. 5.3). 8.9 applied. 8.10 applied (caption "x/y: x of y; x:y: discordant snapshots"). 8.11 applied.
  8.12 applied (clause dropped). 8.13 applied (Table 6).
9.1 applied. 9.2 applied. 9.3 partly (the double predicate fixed; an in-abstract definition of "drive part" declined
  for the word limit). 9.4 applied. 9.5 applied. 9.6 applied. 9.7 declined (itemize costs about two lines; no error).
  9.8 applied. 9.9 applied. 9.10 applied. 9.11 applied. 9.12 applied. 9.13 applied. 9.14 applied. 9.15 applied.
  9.16 applied (math-mode minus). 9.17 applied. 9.18 applied. 9.19 applied. 9.20 applied. 9.21 applied. 9.22 applied.
  9.23 applied. 9.24 F3.
10 refrain at 06:19 applied. 10.1 declined (taste). 10.2 applied. 10.3-10.6 applied. 10.7-10.10 kept.
  10.11 applied. 10.12 applied ("flow deficit"). 10.13, 10.14 kept (rulings).
11.1 applied ("The authors' earlier study"). 11.2 applied. 11.3 applied. 11.4 applied. 11.5 applied. 11.6 kept.
  11.7 run names dropped from the merge note to recover a line. 11.8 n/a.
12 rows: 1 applied in text (Fig. 1 F3). 2 applied (columns "Bias +-b"; Fig. 3 box F3). 3 applied (Fig. 3 box F3).
  4 applied. 5 applied. 6 applied (03:20, 03:33, 04:44, 05:54, 06:51, 06:58). 7 declined (taste). 8 applied
  ("slope ratio"). 9 applied. 10 declined (taste-level; "fraction-matched at T" kept at first use). 11 applied.
  12 applied. 13 applied ("the social force model alone (SFM)" in Sect. 1). 14 applied in Table 6 and text; Fig. 9
  legend F3. 15 applied. 16 applied. 17 applied. 18 applied. 19 F3. 20 F3. 21 applied (line goal defined in Sect.
  3.4; noise floor; noise and width runs; member nearer the axis; "defining probe" removed). 22 partly: N, k/n, a:b,
  10^-k fixed; s defined in Fig. 6 caption; g/c/T kept (taste).
13.1 applied. 13.2 applied for 5.2; Sect. 7 kept as establishing place (see 3.1). 13.3 applied. 13.4 applied.
  13.5 applied. 13.6 applied. 13.7 applied. 13.8 applied. 13.9 applied. 13.10 applied. 13.11 declined: footnote b
  already scopes the 13/800 cell to the 160 second traps. 13.12 applied (coordinator decision). 13.13 applied (9/34).
  13.14 applied. 13.15 applied. 13.16 applied. 13.17 applied (both places, and the line goal). 13.18 applied (1.49
  removed). 13.19 declined (taste; 04:12 already uses \RunNOneSigma). 13.20 applied. 13.21 applied. 13.22 applied.
  13.23 declined (adds note length; no error). 13.24 applied. 13.25 declined: the 101/186 and 5/300 cells come from the
  A11 pool, which no single section reports, so no pointer was added. 13.26 applied. 13.27 applied (all six).
14.1 partly: the duplicated legacy sentence in contribution 2 replaced by the leg-normal statement with Eq. (13); the
  identity sentence keeps tau' and 1.8-2.2 (headline rule). 14.2 applied. 14.3 partly: reorder declined (structural
  risk); pointer to Sect. 4.3 added at "fixed point" and the probe definition moved first (3.6). 14.4 applied.
  14.5 applied ("over whole runs" / "whole-run" in abstract, contributions, Sect. 7, conclusions). 14.6 applied.
  14.7 applied. 14.8 applied via 7.5. 14.9 declined (taste). 14.10 applied (tau_h and neighbour count are in Table 1).
  14.11 applied. 14.12 kept. 14.13 n/a.
15.1 kept. 15.2 applied (Fig. 3 caption, Table 4 note). 15.3 applied. 15.4 partly ("leave no standoff"); "1 gap in
  the five runs" declined (taste). 15.5 F3. 15.6-15.7 n/a. 15.8 applied.
16.1 partly: the abstract keeps "fraction-matched" and "replay" undefined (word limit). 16.2 already fixed.
  16.3-16.5 applied. 16.6 declined (taste). 16.7-16.15 applied. 16.16 applied. 16.17 applied. 16.18 applied.
  16.19-16.21 applied. 16.22-16.26 applied. 16.27 F3.

## Cuts made to pay for the additions (no content change)
Shorter phrasings in Sects. 1-8 and captions of Figs. 3, 4, 7, 9; merged the 4.1 probe paragraph; the pair "still
moving" sentence folded into Sect. 6.3; the 600 s censoring note and the Table 4 note shortened; Sect. 8.1 heading
dropped. The run-in "As bottleneck flow grows with width" keeps its citations.

## For the figure session (not edited here)
- figures/fig1_caption.tex: V4 / 8.1 / 9.24 / 16.27 / 12-1: "blue, force-coupled ORCA's rest drive, its drive part"
  contradicts the definition of rest drive (Sect. 3.2); use "blue, drive part of force-coupled ORCA"; say what the
  grey marker marks; the caption has nested semicolons. Fig. 1 graphic: bare "ORCA" label on the added-drive arrow;
  "held alone"/"passes alone" -> "stuck alone"/"passes alone".
- figures/fig_protocol.tex: box "frozen deadlocks" -> "snapshots"; "lateral tilt" -> "lateral bias +-b";
  "Signatures" -> "Responses".
- Fig. 6 axis "-s/dU_cond": s is now defined in the caption ("s the Arrhenius slope"); relabelling "slope ratio" is
  optional. Fig. 9 legend: "SFM, jamb range" and "SFM, noise sigma*" to match Table 6 and the text.

## Numbers that could not be sourced
None needed. No new literal numbers except design constants (the six r_c radii, the eight bias grid values, the line
goal x = 11 m, "20 converged runs" = 2 x \RevBfourN per brief M15/M17).
