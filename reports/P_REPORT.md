# P report: consistency sweep, floats, page pass (2026-11-09)
Published to main: 54357c8 (Step 1 + float settings), 61cbf5e (page pass + self-audit fixes). make numbers, make paper, make submission green (24 pp, 0 errors, 0 undefined, 0 overfull); overlap check 0 shared runs ≥ 8 words.

**Real page count: 24** (real fractional 24.00; page_map --pinned 24.01; agree within 0.01).
## Pages per section, pinned (before → now, budget)
title+abstract+back 1.40→1.04 (1.0) · §1 2.00→1.79 (1.8) · §2 1.41→1.41 (1.5) · §3 2.93→2.56 (2.6) · §4 2.87→2.55 (2.6) · §5 4.67→4.20 (3.8) · §6 5.21→5.00 incl. §6.3+Table 4 unchanged (4.8) · §7 1.81→1.68 (1.8) · §8 1.33→1.02 (1.0) · §9 0.43→0.36 (0.4) · references 2.45→2.41 (2.3) · **total 26.52→24.01 (23.6)**. Over: §5 +0.40, §6 +0.20, refs +0.11; queue-3 room is 0 against 24, 1.0 against the 25-page cap.
## Floats (Step 2)
placeins [section] barriers + float fractions in main.tex. Tables 1–4 no longer stranded at the end: every table and figure now sits on the page of, or the page after, its first reference within its section.
## Cut, per section
- Abstract 284→~180 words; §1 contribution bullets lost the numbers whose home is §5–§7 (word statements + section refs; critical width kept); equifinality paragraph 4→2 sentences. Back matter "Main Differences" to three sentences. §9 one paragraph, only the CroMa ratio.
- §3: Table 1 nine parameter rows → four, six mode rows → three, caption one sentence; formula/gate/TTC cut duplicated from Eqs; two "differs as listed" sentences removed; RVO2 introduced in the ORCA paragraph.
- §4: probe list removed (Table 2 headers carry it); Table 2 headers and cells shortened (Corrected numerics kept; row N "set by solver details / outcome flips / effect vanishes"); lemma hypotheses and T_eff prose tightened.
- §5: keystone, outcomes and arrival-order paragraphs merged (each count once); slope medians/coverage in one sentence; left-out snapshots one sentence; §5.4 granular background dropped (in §2); Fig. 2 caption to two sentences.
- §6: counts shown in Table 3 replaced by pointers; J defined once (Table 3 caption); Table 3 caption 3→2 sentences; Fig. 5/6 captions shortened; duplicate RVO2-reference sentence removed.
- §7: method paragraph tightened (all conditions/estimators kept); repeated human values and "Removing deadlocks" duplicates cut. §8: calibration + mechanisms paragraphs merged, numbers by reference to §6/Table 3; checklist items tightened.
- refs.bib: two URL fields that duplicate DOIs (CroMa, Weidmann) removed.
- Prose self-audit (cats 1–11, 16) on every changed paragraph: 3 auditors, 65 fixes applied (run-ons from merges, compression damage, dangling modifiers, "lever arm" → "usable range").
## Decisions 1–7, where applied
1. Activated escape: abstract, §1 Physics bullet, §4.3 (Kramers prediction), §5.2 heading "Noise as Activated Escape" + blocker PR / neighbours-lower-barrier sentences (\EfourSaddleRatio = 0.30, 10/10), back matter; "collective" gone from all my files.
2. Collapse slope kept in §5.2 as excluding −1, partly built in by fitted attempt rates; Fig. 4 caption rewritten for the slope-ratio panel (F3's own proposed caption not yet published: swap when it lands).
3. §6.3 matched bias: in-sample by construction, split-half range [−0.35, +0.35] (RVO2 [−0.22, +0.26]), weak calibration target at n = 46; handedness and identity separate. §8 matching sentence; abstract/§1 "partly different standoffs".
4. Class N: Table 1 ORCA mode row (sign defect = source of replay flips), Table 2 row N, §6.1 closing sentence; §4 class text consistent.
5. Critical width: §5.1, 0.88 m between 0.75 m and 0.92 m.
6. No new "fold"; §5.3 \pending for the N6 verdict kept.
7. CroMa DataCite BibTeX (re-fetched 2026-11-09) gives **year = 2026**; entry unchanged at 2026, source comment updated (F2 had proposed 2021; the record says 2026).
## Remaining \pending (mine)
§3 E8/E9 + Table 4; §5.3 N6 fold; §5.4 N5 resolution run; §6.1 N1; §6.2 N2; back matter Zenodo DOI, acknowledgements, disclosure. (S3: §6.3 ×3, Table 4 ×3.)
## Changelog entries proposed
- Cxx Activated escape restated (A-3): blocker carries the unstable mode (PR 1.2); neighbours lower the barrier through their configuration (10/10, median 0.30); "collective escape" retired; §5.2 heading "Noise as Activated Escape".
- Cxx Pair bias stated as an in-sample match by construction; split-half ±0.35 makes the rate a weak calibration target at n = 46 (A-2).
- Cxx Class N aligned on the leg-normal sign defect in Table 1, Table 2, §6 (A-4). Critical width bracketed by 0.75 and 0.92 m (A-8).
- Cxx Float placement (placeins section barriers, float fractions); page pass 26.5→24.0 pinned; Tables 1–3 compressed; refs: duplicate-DOI URLs removed.
## [NEEDS PALAASH]
- 0.4 pp over the 23.6 target (§5 +0.40, §6 +0.20). Section agents found no further cut without dropping single-occurrence numbers. Options: (a) Figs 2–4, 6, 7 at 0.9\textwidth (≈ −0.25 pp; F3 to check legibility); (b) move §5.1 arrival-order statistics and §5.2 per-condition coverage counts to the repository; (c) accept 24.0 + queue 3 ≈ 24.4 (under the 25 cap).
- Fig. 4 caption: replace with F3's proposed caption when published.
- CroMa year: DataCite now says 2026 (dataset record), not 2021; confirm, or cite the 2021 experiment paper alongside.
