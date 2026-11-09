# S3 report: Table 4, Sect. 6.3 and the batch-6 leftovers (2026-11-09)

## Leftovers done
- CHANGELOG C60-C64: E7 text, prose standard (plan/PROSE_STANDARD.md), Table 3 "0 (disjoint)", framing, solver decision C64.
- Table 3 RVO2 pair Jaccard and the framing sentences (critical width under the default wall law) done before the F1-F3 handover.
- Sect. 6.3 and Table 4 written in the glossary terms; labels sec:conference and tab:conference, cross-references only.

## Verdicts (published ORCA in the corrected-forward mode, RVO2 as check, C64)
- Throat overlaps (E11): revised. Unfiltered count reproduces the printed one (C1 1.16 vs 1.20; C2, C4 0; p = 0.011),
  but no overlap under any intervention lasts 0.1 s, with either solver.
- ORCA gridlocks counterflow (E8): withdrawn. Published ORCA keeps 0.99 [0.89, 1.13] of C1's throughput, gridlocks
  1/75 vs C1 4/75; RVO2 agrees (1.12 [1.02, 1.26], 2/75). 0 leaks.
- TTC triples crossing throughput (E9): withdrawn. C2/C1 1.01 [0.96, 1.06] against the printed 2.72; no ORCA involved.
  At the densest start C2 sinks 16.1 (printed 16.1) and C1 15.2 (printed 5.9): the printed C1 value is the outlier.
- Published ORCA completion (E6p, published-reproduction mode, n = 50): confirmed. 29/50 [0.44, 0.71] against the
  printed 13/25, Fisher exact p = 0.632 (11 deadlocked, 10 still moving at the 600 s cap).

## Sizes and build
- Table 4: 15 rows, 0 pending, about 0.45 page (page 18, next to Sect. 6.3).
- Sect. 6.3 (now numbered 6.4): about 26 lines, about 0.57 page, 0 pending.
- make numbers, make paper, make submission green; 24 pages, 0 undefined references. Pushed 3d5ecde.
- CI: green for 3d5ecde (tests and paper).

## \pending left in the paper (none in Table 4 or Sect. 6.3)
- Sect. 3 (03_model.tex:48): "E8, E9 initial-density sweeps; Table~4" (internal labels, hard-coded table number).
- Two in Sect. 5 (continuation run, resolution run); two in Sect. 6 (after run-N1, run-N2).
- Back matter: Zenodo DOI, acknowledgements, disclosure of interests.

## [NEEDS PALAASH]
- Sect. 3 pending above should become the open-geometry settings with \ref{tab:conference}; not my file.
- 10_back_matter.tex still cites sec:att-conf; kept as an alias label in Sect. 6.3, can be dropped once it is changed.
- Sect. 9 conclusions lack the "default wall law" qualifier on the critical width (outside the edited set).
- C4 was run with RVO2 only in the throat rerun and the crossing; no published-LP C4 exists for those rows.
- The crossing ORCA interventions (C3, C4) ran with RVO2 only; the crossing verdict does not depend on them.
- The Mac slept on battery for most of 11:50-17:45 despite caffeinate -i; no data lost, but long queues need AC power.
