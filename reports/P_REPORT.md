# P report: revision against the referee report (2026-11-11)

Published to main: changelog C94 (rulings R1-R5), 34c02bc (text rewrite), 515c372 (integration, page pass), 19ec25d (audits and fixes), and this report with the submission notes.
Build: `make numbers`, `make paper`, `make submission` green. **25 pages**, 0 errors, 0 undefined references, 0 overfull boxes; Overleaf package compiled from scratch in /tmp gives the same 25 pages with 0/0/0.
Outputs: ~/Desktop/LNNS_overleaf/ and LNNS_overleaf.zip (one main.tex with literal numbers, refs.bib with the 49 cited entries, figures/, unmodified llncs.cls and splncs04.bst, README.txt); ~/Desktop/LNNS_final.pdf.

## Referee resolution (reports/P_RESOLUTION.md, 87 items)
71 resolved, 3 partly resolved (D2 a few long sentences remain; D7 Sect. 4 keeps protocol-defining outcomes such as the match horizons; F-14 Weidmann values unchecked), 1 not resolved (C11 per-run CroMa table, cut for pages), 12 not checkable (F1, m3-m7, m9-m14: the referee report is not on disk and the revision sources do not state their content).

## Claims that changed meaning
- Scope: every claim is about this social force model (title, abstract, contributions), not pedestrian steering models.
- Stuck-alone: "exact, if and only if g_max > m v0/tau" became an on-axis equilibrium condition g_max >= m v_eff/tau, tested in both directions (released agents).
- Critical width 0.88 m became 0.878 [0.874, 0.883] m from 1100 runs; the parameter-free (1 - f)^100 prediction misses it by 0.041 m; the fitted group size (19) is descriptive.
- Pair standoff: formerly a short-range-wall-law deadlock; now it needs sharp segment ends (0 of 320 runs with rounded edges) and survives a line goal. "Rounded corners leave the trap in place" now holds for the lone trap only. Barrier-under-bias exponent dropped.
- Activated escape: slope ratio near 1 became an effective barrier 0.86-0.93 of the computed one (alone condition, beta 1.5-7); at the fraction-matched noise level the median beta is 0.64, so the Arrhenius test does not cover it and the whole-run stall prediction extrapolates.
- Force-coupled ORCA: its rest drive is the social force model with tau' = 0.22-0.27 s (drive 1.8-2.2 times); its constraint part acts at rest and makes the pair rest field non-gradient, so the old Proposition is now a standard Remark that does not cover force-coupled ORCA at the pair; class at the pair is Reshape, solver-dependent.
- "Rate-matched" became "fraction-matched at T", horizon-specific; noise is not matched at the second trap.
- Overlap J at the lone trap: the 5-seed 0.20 became the 20-seed value; overlap separates nothing, handedness separates the bias.
- "SFM frees none" and "5 of 300 replays" are scoped to the 26-snapshot screen; on all 160 second traps the SFM quench frees 2 and the legacy solver flips 13 of 800 replays.
- ORCA velocity filter: "class P, as predicted" became a consistency check (at most Prevent).
- Decision rule: interval exclusion became paired tests with Holm's correction; definitional separations (replay, per-step time step) named.
- Arches: peak compression 108 kN at dt = 0.01 s became the converged values (summed at most 18 kN, single contact at most 4.8 kN); absence at lower drives scoped to dt = 0.01 s.
- CroMa: flow ratio 0.40-0.59 became 0.40-0.60; force-coupled ORCA deadlocks in 1 of 25 runs ("never deadlocks" withdrawn); bottleneck lengths 2.0 and 0.2 m; final gaps right-censored at 600 s.
- Classes: five lettered classes became four named ones (Prevent; Reshape, axial or lateral; Heat; Glitch).

## Audits (reports/P_audit/)
Prose 139 findings, numbers 58 flagged of 470 macros (2 wrong bounds, 7 unsupported, 4 literal, 45 imprecise), compliance 15 violations, referee recheck 27 disputes: 239 in all. Six fix passes applied them; 72 entries were declined or deferred with a reason in fixlog_*.md (mostly page budget, ownership or ruling conflicts). Tooling: p-values two significant figures (half up) down to 10^-3, then p < 10^-k, with relation macros for running text; thin-space thousands.

## Remaining \pending (3)
Zenodo DOI (Data and Code Availability), Acknowledgments, Disclosure of Interests.

## [NEEDS PALAASH]
- Weidmann check: gamma = 1.913 and rho_max = 5.4 against the original table of Weidmann 1993 (scripted access blocked).
- Acknowledgments and Disclosure of Interests, the disclosure consistent with the AI-use statement of the conference paper.
- Corresponding-author marking: confirm Palaash Gang and the email in the author block.
- Zenodo DOI after the framework sync (steps in paper/SUBMISSION_NOTES.md).
- Bibliography numbering: the conference paper is the first citation but splncs04 sorts alphabetically, so it prints as [14], not [11].
- Figure owner items: Fig. 1 caption sets k_B in italic; the protocol figure calls the push "the rest drive of force-coupled ORCA" (text: the ORCA term's drive part at rest).
