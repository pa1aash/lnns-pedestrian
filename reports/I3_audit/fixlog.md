# I3 audit fixes (numbers.md, compliance.md, consistency.md)

## Numbers (12 findings: 1 wrong, 11 rule)
- 1 applied: arch compression and single-contact force now the maximum over both fine time steps (rev_B4 dt0p001: 18 kN, 4.8 kN; PphysBodyFine, PphysContactFine).
- 2-5 applied: Sect. 7 two-figure macros (Pend*GapCompleteMax 20, 16, 7.6, 240 s with "reaches"; PendCThreeOpenMean 450 s; lower bounds rounded down, 410 and 430 s).
- 6, 7 applied: lower bounds rounded down (PphysWeidMinFloor 0.99; PmodRunsWMinTwo 0.95, PmodLoneWMinTwo 0.99). tools/make_numbers.py gains fmt "sig" and "floor".
- 8 declined: median drives 214 and 215 N kept at three figures (two figures give 210 and 210 beside the total 430, which reads as an arithmetic error); covered by the amended rule.
- 9, 10 applied: g_max 540, 290, 160 N; mu_1 maxima 120 N/m.
- 11, 12 applied as proposed: w50 interval and the 2.04 s human gap keep three figures; Sect. 4.6 rule now reads "two significant figures (three where an interval or a threshold needs them)".

## Compliance (6 findings)
- F1 applied: protocol figure exponent set at text size ($10^{\textstyle -9}$), 7 pt.
- F2 applied: "attempt rate" -> "attempt frequency" (Fig. 6 caption, Sects. 5.2, 6.2, 8.1).
- F3 applied: abstract "a fraction-matched lateral bias".
- Advisory not applied: bare "ORCA" in Sect. 1 refers to the conference paper's ORCA in general; "(RVO2)" omissions where the solver is clear; scaled Tables 3a/3b (tables, not figures; the 7 pt rule is for figures). Abstract trimmed to 248 words after the consistency fixes.

## Consistency (14 findings)
- 1, 2 applied: legacy defect -> Sect. 6.1; recommendation (iii) cites Sects. 3.2 and 6.1-6.4 (covers the pair solver difference).
- 3, 4 applied: abstract "at rest its drive part is the model ..."; "with uncalibrated default parameters" before the flow ratio.
- 5 applied (shorter wording): conclusions say noise and bias, fraction-matched at T, free deadlocks by activated escape and a lateral tilt, and the probes separate all three.
- 6, 7, 8, 10 applied: discussion quotes the effective barrier 0.86-0.93; limitations name the matched-noise medians (0.64, 1.4) below beta = 1.5; interval in math mode; short wall range with sharp ends.
- 9 declined: Table 2 note a classes force-coupled ORCA at the pair as Reshape, axial (solver-dependent), so "Reshape, axial" holds.
- 11, 12, 13 applied: "against 46 with sharp ends"; "at the tested desired speeds"; CroMa contribution gives 0.40-0.60.
- 14 applied: "five" runs in running text (abstract, Sect. 7); "Door width also sets the lone trap".
- Not changed: the mean open time of censored ORCA runs (450 s) describes observed time without passage, not a gap estimate.
