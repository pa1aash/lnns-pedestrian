# P2 audit: numbers of the paper against data/derived

Scope: paper/sections/*.tex, paper/tables/*.tex, figures/fig1_caption.tex (Fig. 1 caption) and the captions inside the
sections. No paper file was edited. Scripts (scratchpad of this session): `audit_macros.py` (macro extraction, registry
lookup, independent re-formatting, rounding and bound checks), `intervals.py` (interval bracketing in context),
`bounds.py` ("at most / within / at least" contexts), `wc_abstract.py` (abstract word count).

## Summary

| Check | Result |
|---|---|
| 1. Macros resolve | 523 distinct number macros used (incl. `Rel` variants); all defined in paper/numbers.tex; `paper/main.log` (12:11:48, after the last source edit at 12:11:35) has no undefined control sequence and no warning. `make numbers` was not needed: `tools/make_numbers.py --out <scratch>` regenerates numbers.tex byte-identical (4172 macros), so numbers.tex is current with the registry and the JSON. |
| 1. Values vs JSON | Every used macro re-read from its JSON key and re-formatted independently: 0 value mismatches, 0 wrong roundings under the declared format. 52 printed intervals checked in context: all bracket their estimate (raw and printed). Floor-formatted lower bounds (`PmodRunsWMinTwo`, `PmodLoneWMinTwo`, `PphysWeidMinFloor`, `PendCOneGapLowerMedianTwo`, `PendCThreeGapLowerMedianTwo`) are correct. Four upper bounds ("at most", "within") are rounded down and are false as printed (WRONG rows). |
| 2. Superseded | No older macro carries a value that a newer item changed, except the 95% intervals of the freed-fraction difference Δ in Tables 4 and 5 and the Discussion, which come from the earlier bootstraps (E2/N1/E6 analyses, rev_A6, rev_A8, table3_pair) while C2 item A5 recomputed them with the primary cluster bootstrap and the text quotes A5's 90% intervals beside them (7 SUPERSEDED rows). The A3 Arrhenius ratios (RvAthree*) are in place; RevBthreeDU* are barrier values that A3 reuses unchanged. |
| 3. Literal result numbers | 5 UNSOURCED (no macro used; 4 have a macro or JSON key available). All other literals are design constants or figure-only numbers confirmed by reports/F3_REPORT.md. |
| 4. Precision / duplicate macros | 6 IMPRECISE rows; duplicate macros for one quantity all carry equal values (OK-with-note). |
| 5. Abstract length | **251 words** under the stated rule (formula = 1, macro = 1, number and unit separated by `\,` = 2): one over the 250 limit. Variants: 248 if `0.08\,m` counts as one word; 247 if a macro range `\A--\B` counts as one word; 244 with both. |

Verdict counts (findings table): **WRONG 4, SUPERSEDED 7, UNSOURCED 5, IMPRECISE 6, OK-with-note 15** (plus the abstract length, check 5).

## Findings

| # | Macro or literal | Location | Printed | Source value | Verdict | Fix |
|---|---|---|---|---|---|---|
| 1 | `PphysBodyFine` ("summed compression ... is at most") | sections/05_deadlock_physics.tex:57 | 18 kN | 18.32 (p_physics.yaml) | WRONG | Upper bound rounded down (sig/2). Print 18.3 (digits 3) or 19 (ceiling). |
| 2 | `PphysContactFine` ("a single contact at most") | sections/05_deadlock_physics.tex:57 | 4.8 kN | 4.848 | WRONG | Upper bound rounded down. Print 4.85 or 4.9. |
| 3 | `PphysFoldMissGap` ("escape at most ...% below $b_f$") | sections/05_deadlock_physics.tex:52 | 1.7 | 1.727 | WRONG | Upper bound rounded down. Print 1.73 or 1.8. |
| 4 | `PscrStallMaxDiff` ("lies within") | sections/06_screening.tex:37 | 0.045 | 0.04509 | WRONG | Bound rounded down (marginal, 9e-5). Print 0.046 or 0.0451. |
| 5 | `PscrLKDiffHi` (Δ, lone keystones, σ = 0.07, 95%) | tables/table4_noise.tex:14 | [−0.10, 0.082] | E2_analysis bootstrap 0.0824; A5 primary cluster bootstrap 0.0765 | SUPERSEDED | Use `\RvAfiveLoneEtwoDiffLo`/`Hi` = [−0.10, 0.076] (the text's 90% interval and TOST at 06:19 come from A5), or state that the table uses the earlier bootstrap. |
| 6 | `PscrNOneDiffHi` (Δ, σ = 0.0717, 95%) | tables/table4_noise.tex:15 | 0.044 | N1_analysis 0.0441; A5 0.0412 | SUPERSEDED | `\RvAfiveLoneNoneDiffHi` = 0.041 (Lo −0.074 unchanged). |
| 7 | `PscrSTDiffLo`, `RevAsixSTDiffHi` (Δ, second traps, 95%) | tables/table4_noise.tex:19 | [0.085, 0.44] | rev_A6 (E2 bootstrap) [0.0846, 0.4385]; A5 [0.0769, 0.4310] | SUPERSEDED | `\RvAfiveSecondEtwoDiffLo`/`Hi` = [0.077, 0.43]. Note: the same JSON key is also registered as `RevAsixSTDiffLo` = 0.08 (unused); C_REPORT quotes [0.08, 0.44]. |
| 8 | `PscrWholeDiffLo`/`Hi` (Δ, whole runs, 95%) | tables/table4_noise.tex:23 | [−0.10, 0.078] | E6_analysis [−0.0997, 0.0785]; A5 [−0.1022, 0.0754] | SUPERSEDED | `\RvAfiveWholeDiffLo`/`Hi` = [−0.10, 0.075]. |
| 9 | `PscrPairPubDiffHi` (Δ, bias vs ORCA legacy, 95%) | tables/table5_bias.tex:14 | [−0.15, 0.22] | rev_A8 0.2174; A5 0.1957 | SUPERSEDED | `\RvAfivePairLegacyDiffLo`/`Hi` = [−0.15, 0.20]. |
| 10 | `PscrPairRvoDiffLo` (Δ, bias vs ORCA RVO2, 95%) | tables/table5_bias.tex:18 | [−0.15, 0.17] | rev_A8 −0.1522; A5 −0.1310 | SUPERSEDED | `\RvAfivePairRvoDiffLo`/`Hi` = [−0.13, 0.17]. |
| 11 | `TabThreePairPubDiffLo`/`Hi` ("intervals as wide as") | sections/08_discussion.tex:14 | [−0.15, 0.22] | table3_pair.json (= rev_A8) 0.2174; A5 0.1957 | SUPERSEDED | [−0.15, 0.20] via `\RvAfivePairLegacyDiffLo`/`Hi`; keep it equal to Table 5 row 1. |
| 12 | literal "13 and 0 of 25" (conference completions) | sections/01_introduction.tex:14 | 13, 0, 25 | rev2_A11.json `conference.completion.C3.k` = 13, `C1.k` = 0, `n` = 25 | UNSOURCED | Add registry entries (e.g. RvAelevenConfCThreeK, RvAelevenConfCOneK, RvAelevenConfN) and use them. |
| 13 | literal "34--46 snapshots" (margin basis) | sections/04_protocol.tex:11 | 34–46 | `EtwoNLK` = 34, `PairN` = 46 (also rev2_A5 n_units) | UNSOURCED | `\EtwoNLK--\PairN`. |
| 14 | literal "$\sigma=0.0717$\,m/s" | sections/04_protocol.tex:12 | 0.0717 | `RunNOneSigma` = 0.0717 (used at 06:19) | UNSOURCED | `\RunNOneSigma`. |
| 15 | literal "raises the ratio by under 1\%" | sections/05_deadlock_physics.tex:42 | < 1% | rev2_A3 discrete_time_bias_range [0.0079, 0.0085] | UNSOURCED | "by \RvAthreeDtBiasMin--\RvAthreeDtBiasMax" (0.0079–0.0085), or keep "under 1%" with `\RvAthreeDtBiasMax` cited in a note. |
| 16 | literal "1.0" (upper end of Mel'nikov–Meshkov factor, "\RvAtwoAMin--1.0") | sections/05_deadlock_physics.tex:43 | 1.0 | rev2_A2 `headline.A_E4_max` = 0.99999999 | UNSOURCED | Register `RvAtwoAMax` (sig/2 gives 1.0) or write "at most 1" (theoretical limit). Value correct. |
| 17 | `RvAthreeRatioShallowHi`, `RvAthreeRatioMidHi` | sections/05_deadlock_physics.tex:42 | 1.0, 1.0 | 1.0012, 1.0279 | IMPRECISE | Whether the interval covers 1 is the point; Sect. 4.6 asks for three figures "where an interval or a threshold needs them". Use digits 3: [0.806, 1.00], [0.826, 1.03]. |
| 18 | `PphysGmaxMeanR` with `RevAthirteenDriveOverGmax` | sections/05_deadlock_physics.tex:14 | 214 N is 1.4 × 160 N | g_max(mean r) 156 (JSON display value, re-rounded to 2 sf); ratio 1.375 | IMPRECISE | Printed numbers give 214/160 = 1.34, not 1.4. Print g_max = 156 N (digits 3), or give the ratio as 1.3x consistent with the printed values. |
| 19 | `EtwoMaxBiasUpperLK` ("upper Wilson bound") | sections/06_screening.tex:22 | 0.10 | 0.1015 | IMPRECISE | An upper bound printed below its value; 0.11 (ceiling) or 0.102. |
| 20 | `RvAnineHumanWindowFlow` beside `PendHumanFlow` | sections/07_experiments.tex:19 | 1.49 ped/s and 1.5 [1.2, 1.7] ped/s | 1.4881; 1.4718 [1.2102, 1.7334] | IMPRECISE | Two human flows in one paragraph at 3 and 2 figures; the 2-sf 1.5 reads as larger than 1.49 although it is smaller (1.47). Print both to 0.01 ped/s (1.47 [1.21, 1.73]) or both to 2 sf. |
| 21 | `PprotMuMax` in "`\RevAtenMuMin`--`\PprotMuMax`" | sections/04_protocol.tex:23 | 66–1.1×10³ N/m | 65.7–1115 | IMPRECISE | Mixed fixed and scientific notation in one range. Print 66–1100 N/m. |
| 22 | `PphysPosMarginMin` ("positive margin (from ...)") | sections/05_deadlock_physics.tex:19 | 0.0081 N | 0.008080 (rev_B1 pos_rest.margin_range_N.0) | IMPRECISE | The smallest positive margin is rounded up; floor gives 0.0080. Minor. |
| 23 | `RevAeightLKNoiseCMatchFrom` (70), `RevAeightLKNoiseNoneMatchFrom` (85), `RevAeightWholeNoiseMatchFrom` (425) | sections/04_protocol.tex:12 | 70, 85, 425 s | rev_A8 matched_T_s (95% interval covers 0) | OK-with-note | Not superseded: a different criterion from A5's equivalence windows used at 06:19 and 06:35 (89, 86, 545 s). The reader meets two "from" horizons for the same comparisons; name the criterion at 04:12 ("not rejected from"). |
| 24 | `RevAeightSTRvoLatest` ("last lone-trap exit comes by") | sections/04_protocol.tex:12 | 14 s | rev_A8 key `lone_keystone_second_trap.latest_exit_s.C3_rvo2` = 13.99 | OK-with-note | Correct for the screening set (E2's 26 second traps; lone keystones within 7 s per A5). On the pooled 160 second traps ORCA's last exit is 36 s (A5 note). |
| 25 | `PphysRatioFull` ("full-condition median") | sections/05_deadlock_physics.tex:42 | 1.2 | 1.1507 | OK-with-note | Blocker temperature, as defined; C2 A7 gives 1.1 (`RvAsevenFullMedMode`) with the mode temperature, which Sect. 4.4 (04:33) introduces. Same value as A7's blocker-temperature median; not superseded. |
| 26 | `EfourRatioAlone` (0.87, β 1.5–3.5, E4) next to `RvAthreeRatio*` (0.85–0.93, β 1.5–7, A3) | sections/05_deadlock_physics.tex:42 | 0.87; 0.85–0.93 | E4 alone median 0.866; A3 per snapshot | OK-with-note | Different β ranges and snapshot sets; both current. |
| 27 | `RevDThreeRatioMin`/`Max` | 00_abstract.tex:3, 01_introduction.tex:24, 07_experiments.tex:36, 09_conclusions.tex:2 | 0.40–0.60 | rev_D range 0.4008–0.5958 | OK-with-note | C2 A9 recomputed the range under the same definition: `RvAnineRatioMin`/`Max` = 0.40–0.60, identical ("does not change"). |
| 28 | duplicate macros, equal values | 03:67 `RevAfiveGateFailSecond` and 04:41 `RvAeightFailed` (4); 03:67 `LoneBarN`, 06:37 `EsixBarrierN`, `RevAthreeBarN` (56); t5:14 `PscrPairPubDiff*` and 08:14 `TabThreePairPubDiff*`; 06:25 `RevAfiveXPoolNoiseOrca*` and `RvAfiveSecondPool*` (+0.13 [0.076, 0.19]) | equal | equal | OK-with-note | No conflict; consolidating on the newest macro would prevent future drift (rows 9 and 11 already differ from A5). |
| 29 | literals "seeds 42--241", "PCG64 seed 2026" | sections/03_pedestrian_model.tex:67 | 42–241; 2026 | `RvAeightEoneLo`/`Hi` (used on line 68), `RvAeightDrawSeed` | OK-with-note | Design constants; correct; macros exist. |
| 30 | literal "$\beta=0.75$ at $\Delta t=0.005$\,s to 3 at 0.02\,s" | sections/04_protocol.tex:34 | 0.75, 3 | F3: 0.75 and 2.97 | OK-with-note | Derived from design constants; 3 is the proportional value, 2.97 with the last factor of Eq. (teff). |
| 31 | Fig. escape caption "(dashed, 0.9)"; Fig. lone-trap caption medians `DriveCOneMedian`, `PphysDriveTotal` | sections/05_deadlock_physics.tex:36, :6 | 0.9; 214 and 430 N | F3_REPORT: reference line 0.9; medians 214 and 430 N | OK-with-note | Figure-only number and caption macros agree with F3. Fig. 1 caption (fig1_caption.tex) has only design numbers (σ, Δt, colour-scale limits ±150 N, 5–1000 N, 0.25 m), as in F3. |
| 32 | `RvAnineCOneLongRatio`–`RvAnineCThreeLongRatio`, `...Short...` ("The flow ratio is ... (SFM) to ... (force-coupled ORCA)") | sections/07_experiments.tex:19 | 0.54–0.62; 0.48–0.58 | A9: correct | OK-with-note | Values correct; the range omits the noise variant (0.41 at 2.0 m, 0.40 at 0.2 m), so it is the deterministic variants' range, not "the flow ratio". |
| 33 | `RevDThreeCOneFluct`–`PendSigFluct` | sections/07_experiments.tex:34 | 0.092–0.11 m/s | 0.0924–0.1079 | OK-with-note | Two figures each as Sect. 4.6 prescribes; D_changes quotes 0.092–0.108. |
| 34 | `KeystoneBLone` of `ChainBlockerN` ("34 of 196 lone keystones") | sections/05_deadlock_physics.tex:19 | 34 of 196 | 34; 196 | OK-with-note | Numbers correct; reads as if 196 were the number of lone keystones ("34 lone keystones among the 196 blockers"). |
| 35 | `RevBtwoWlo`, `RevBtwoWhi` ("below 0.75 m", "above 0.92 m") | sections/05_deadlock_physics.tex:21 | 0.75, 0.92 | 0.7541, 0.9196 | OK-with-note | Rounded outward, so both statements hold. |
| 36 | `PendSigGapsTwo` as the upper end of the gap range | sections/07_experiments.tex:21 | 10–18 | ORCA 10.12, noise 18.16, SFM 18.12 | OK-with-note | Noise is the true maximum (D_changes labels it SFM); correct. |
| 37 | A10 (fixed-stream replay of the noise quench) | Table 2, Table 3 replay column | – | rev2_A10 pending (C2 note) | OK-with-note | No RvAten macro is used, so no pending number is printed; the replay claims rest on independent seeds, as stated. |
| 38 | Abstract length | sections/00_abstract.tex | 251 words | limit 250 | (check 5) | Cut at least one word, e.g. "the open framework deadlock-screen" → "the framework deadlock-screen", or "(jambs only)" → "(jambs)". |

Notes on the verdicts:
- Rows 5–11 change printed digits only in the second decimal; no verdict of the paper changes (all intervals still cover 0 except the second trap, which still excludes 0, and the pair intervals still exceed ±0.10).
- C_REPORT's line "23 of 56 barriers have β < 1" at σ = 0.07 is mislabelled in the report; the paper is right: 36 of 56 at σ = 0.07 (`RevAthreeSevenBelowOneK`, median 0.64) and 23 of 56 at σ* (`RevAthreeStarBelowOneK`, median 1.4), as rev_A3.json shows.
- The literal "positive margin ... none of 200 agents ... at $g_{\max}$ or 1 m upstream" (05:19): rev_B1 places the positive-margin agents at their rest state and only the negative-margin ones at g_max and 1 m upstream (200 agents, 400 runs). Numbers right; the placement wording belongs to the negative sample.

## Appendix: every macro used in the text and tables

Raw value from the JSON key named by the registry, printed text from paper/numbers.tex (identical to an independent
regeneration). "uses" counts occurrences in the scanned sources.

| macro | registry | source (file:key) | fmt | raw | printed | first use | uses |
|---|---|---|---|---|---|---|---|
| ArchVZero | e6_e10.yaml | arch_analysis.json:v0_mean | {:.0f} | 5 | `5` | sections/05_deadlock_physics.tex:57 | 3 |
| ChainBlockerN | core.yaml | E1_chain.json:E1b.a_blocker_arrival_rank_from_end.n | {:d} | 196 | `196` | sections/05_deadlock_physics.tex:19 | 1 |
| CtwsixAbreastN | pair.yaml | fix_reg.json:second_trap_geometry.abreast | {:d} | 9 | `9` | sections/06_screening.tex:25 | 1 |
| CtwsixN | pair.yaml | E7b_analysis.json:e_c26.second_trap_one_neighbour.n | {:d} | 10 | `10` | sections/06_screening.tex:25 | 1 |
| DriveCOneMedian | core.yaml | E1_analysis.json:E1b.drives_N.C1_free_m_v0_over_tau.p50 | {:.0f} | 214.448 | `214` | sections/05_deadlock_physics.tex:6 | 2 |
| DriveORCAMedian | core.yaml | E1_analysis.json:E1b.drives_N.C3_rest_orca_drive_w_o_m_v0_over_tau_orca.p50 | {:.0f} | 214.633 | `215` | sections/05_deadlock_physics.tex:17 | 1 |
| EfiveN | core.yaml | E5_analysis.json:per_sigma.s0p03.n | {:d} | 100 | `100` | sections/06_screening.tex:34 | 1 |
| EfiveSigmaFifty | core.yaml | E5_analysis.json:logistic_noise_levels.sigma50 | {:.3f} | 0.0442538 | `0.044` | sections/06_screening.tex:34 | 1 |
| EfourCoverAlone | core.yaml | E4_analysis.json:headline.ratio_cover_alone | {:d} | 9 | `9` | sections/05_deadlock_physics.tex:42 | 1 |
| EfourCoverFrozen | core.yaml | E4_analysis.json:headline.ratio_cover_frozen | {:d} | 9 | `9` | sections/05_deadlock_physics.tex:42 | 1 |
| EfourCoverFull | core.yaml | E4_analysis.json:headline.ratio_cover_full | {:d} | 7 | `7` | sections/05_deadlock_physics.tex:42 | 1 |
| EfourFitsAlone | core.yaml | E4_analysis.json:headline.nfit_alone | {:d} | 10 | `10` | sections/05_deadlock_physics.tex:42 | 1 |
| EfourFitsFrozen | core.yaml | E4_analysis.json:headline.nfit_frozen | {:d} | 10 | `10` | sections/05_deadlock_physics.tex:42 | 1 |
| EfourFitsFull | core.yaml | E4_analysis.json:headline.nfit_full | {:d} | 8 | `8` | sections/05_deadlock_physics.tex:42 | 1 |
| EfourN | core.yaml | E4_analysis.json:n_snapshots | {:d} | 10 | `10` | sections/03_pedestrian_model.tex:67 | 2 |
| EfourRatioAlone | core.yaml | E4_analysis.json:headline.ratio_med_alone | {:.2f} | 0.866043 | `0.87` | sections/05_deadlock_physics.tex:42 | 1 |
| EfourRatioFrozen | core.yaml | E4_analysis.json:headline.ratio_med_frozen | {:.2f} | 0.948606 | `0.95` | sections/05_deadlock_physics.tex:42 | 1 |
| EfourRestarts | core.yaml | E4_analysis.json:extension.n_restarts.full | {:d} | 20 | `20` | sections/05_deadlock_physics.tex:40 | 1 |
| EfourSeedOneSeventyDU | core.yaml | E4_analysis.json:snapshots.E1b_seed170.conds.full.dU | {:.2f} | 0.128205 | `0.13` | sections/05_deadlock_physics.tex:43 | 1 |
| EsevenBallK | e7.yaml | E7_analysis.json:cells.B0p04.k_complete | {:d} | 85 | `85` | sections/00_abstract.tex:3 | 1 |
| EsevenBjambClassified | e7.yaml | E7_analysis.json:cells.Bedge0p04.classes.n_classified | {:d} | 11 | `11` | sections/00_abstract.tex:3 | 2 |
| EsevenBjambCollective | e7.yaml | E7_analysis.json:cells.Bedge0p04.classes.counts.collective | {:d} | 11 | `11` | sections/00_abstract.tex:3 | 2 |
| EsevenBjambK | e7.yaml | E7_analysis.json:cells.Bedge0p04.k_complete | {:d} | 89 | `89` | sections/00_abstract.tex:3 | 2 |
| EsevenDefaultClassified | e7.yaml | E7_analysis.json:cells.default.classes.n_classified | {:d} | 98 | `98` | sections/05_deadlock_physics.tex:23 | 1 |
| EsevenDefaultCollective | e7.yaml | E7_analysis.json:cells.default.classes.counts.collective | {:d} | 2 | `2` | sections/05_deadlock_physics.tex:23 | 1 |
| EsevenLineK | e7.yaml | E7_analysis.json:cells.line.k_complete | {:d} | 3 | `3` | sections/05_deadlock_physics.tex:23 | 1 |
| EsevenLineRoundK | e7.yaml | E7_analysis.json:cells.line_rounded.k_complete | {:d} | 9 | `9` | sections/05_deadlock_physics.tex:23 | 1 |
| EsevenN | e7.yaml | E7_analysis.json:cells.default.n | {:d} | 100 | `100` | sections/00_abstract.tex:3 | 2 |
| EsevenRoundCollective | e7.yaml | E7_analysis.json:cells.rounded.classes.counts.collective | {:d} | 0 | `0` | sections/05_deadlock_physics.tex:23 | 1 |
| EsevenRoundK | e7.yaml | E7_analysis.json:cells.rounded.k_complete | {:d} | 7 | `7` | sections/05_deadlock_physics.tex:23 | 1 |
| EsevenWEightK | e7.yaml | E7_analysis.json:cells.default.k_complete | {:d} | 2 | `2` | sections/05_deadlock_physics.tex:23 | 1 |
| EsixBarrierN | e6_e10.yaml | E6_analysis.json:lifetimes.barrier_picture.n_barriers | {:d} | 56 | `56` | sections/06_screening.tex:37 | 1 |
| EsixCThreeFailMoving | e6_e10.yaml | E6_analysis.json:failure_state.C3_rvo2.moving_at_600s | {:d} | 54 | `54` | sections/06_screening.tex:37 | 1 |
| EsixCThreeFailRest | e6_e10.yaml | E6_analysis.json:failure_state.C3_rvo2.stationary_deadlock | {:d} | 31 | `31` | sections/06_screening.tex:37 | 1 |
| EsixCThreeK | e6_e10.yaml | E6_analysis.json:completion.C3_rvo2.k | {:d} | 101 | `101` | tables/table4_noise.tex:24 | 1 |
| EsixCThreeMovingSecond | e6_e10.yaml | E6_analysis.json:failure_state.C3_rvo2.class_counts_moving.lone_keystone_second_trap | {:d} | 51 | `51` | sections/06_screening.tex:37 | 1 |
| EsixN | e6_e10.yaml | E6_analysis.json:n | {:d} | 186 | `186` | tables/table4_noise.tex:22 | 3 |
| EsixNoiseCollective | e6_e10.yaml | E6_analysis.json:failure_state.C1_sigma.class_counts.collective | {:d} | 0 | `0` | sections/06_screening.tex:37 | 1 |
| EsixNoiseK | e6_e10.yaml | E6_analysis.json:completion.C1_sigma.k | {:d} | 99 | `99` | tables/table4_noise.tex:23 | 1 |
| EsixNoiseLone | e6_e10.yaml | E6_analysis.json:failure_state.C1_sigma.class_counts.lone_keystone | {:d} | 56 | `56` | sections/06_screening.tex:37 | 1 |
| EsixNoiseSecond | e6_e10.yaml | E6_analysis.json:failure_state.C1_sigma.class_counts.lone_keystone_second_trap | {:d} | 31 | `31` | sections/06_screening.tex:37 | 1 |
| EsixPairedCThreeFaster | e6_e10.yaml | E6_analysis.json:time.paired_C3_faster_n | {:d} | 64 | `64` | sections/06_screening.tex:37 | 1 |
| EsixPairedDelay | e6_e10.yaml | E6_analysis.json:time.paired_median_diff_sigma_minus_C3 | {:.0f} | 65.83 | `66` | sections/06_screening.tex:37 | 1 |
| EsixSigmaStar | e6_e10.yaml | E6_analysis.json:sigma_star | {:.4f} | 0.0467 | `0.0467` | sections/06_screening.tex:34 | 2 |
| EtenHumanFluct | e6_e10.yaml | E10_analysis.json:humans.fluct.mean | {:.3f} | 0.0742766 | `0.074` | sections/07_experiments.tex:34 | 1 |
| EtenHumanFluctHi | e6_e10.yaml | E10_analysis.json:humans.fluct.ci95.1 | {:.3f} | 0.0786297 | `0.079` | sections/07_experiments.tex:34 | 1 |
| EtenHumanFluctLo | e6_e10.yaml | E10_analysis.json:humans.fluct.ci95.0 | {:.3f} | 0.0699236 | `0.070` | sections/07_experiments.tex:34 | 1 |
| EtenHumanGap | e6_e10.yaml | E10_analysis.json:humans.longest_gap.mean | {:.1f} | 1.712 | `1.7` | sections/07_experiments.tex:19 | 1 |
| EtenHumanGapMax | e6_e10.yaml | E10_analysis.json:humans.longest_gap_max | {:.2f} | 2.04 | `2.04` | sections/07_experiments.tex:19 | 1 |
| EtenHumanGapsOverTwoTotal | e6_e10.yaml | fix_reg.json:human.gaps_over_two_total | {:d} | 1 | `1` | sections/07_experiments.tex:19 | 1 |
| EthreeCThreeLnRatioMax | core.yaml | E3_analysis.json:headline.c3_ln_ratio_maxabs | {:.3f} | 0.0176996 | `0.018` | tables/table3_observed.tex:29 | 1 |
| EthreeN | core.yaml | E3_analysis.json:n_snapshots | {:d} | 20 | `20` | sections/03_pedestrian_model.tex:67 | 2 |
| EtwoLKCThreePubFreed | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.C3_pub.freed | {:d} | 30 | `30` | tables/table3_observed.tex:18 | 1 |
| EtwoLKCThreeRVOFreed | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.C3_rvo2.freed | {:d} | 30 | `30` | tables/table3_observed.tex:17 | 2 |
| EtwoLKCThreeRVON | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.C3_rvo2.n | {:d} | 34 | `34` | tables/table3_observed.tex:17 | 3 |
| EtwoLKConstrPubFreed | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.constraint_only_pub.freed | {:d} | 0 | `0` | sections/06_screening.tex:16 | 1 |
| EtwoLKConstrRVOFreed | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.constraint_only_rvo2.freed | {:d} | 0 | `0` | sections/06_screening.tex:16 | 1 |
| EtwoLKFrozenMinusFreed | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.frozen_minus.freed | {:d} | 0 | `0` | sections/06_screening.tex:16 | 2 |
| EtwoLKFrozenPlusFreed | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.frozen_plus.freed | {:d} | 31 | `31` | sections/06_screening.tex:16 | 2 |
| EtwoLKMarginAUC | core.yaml | E2_analysis.json:f_noise_vs_C3.lone_keystone.margin_predicts_C3_rvo2_failure.auc_margin_C3 | {:.2f} | 0.983333 | `0.98` | sections/06_screening.tex:16 | 1 |
| EtwoLKNoiseCFreed | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.noise0p07.freed | {:d} | 148 | `148` | tables/table4_noise.tex:14 | 1 |
| EtwoLKNoiseCN | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.noise0p07.n | {:d} | 170 | `170` | tables/table4_noise.tex:14 | 1 |
| EtwoMaxBiasUpperLK | core.yaml | E2_analysis.json:a_rates_time_to_free.lone_keystone.bias0p5.rate_wilson95.2 | {:.2f} | 0.101518 | `0.10` | sections/06_screening.tex:22 | 1 |
| EtwoNAll | core.yaml | E2_analysis.json:n_snapshots.pooled | {:d} | 60 | `60` | sections/03_pedestrian_model.tex:67 | 1 |
| EtwoNLK | core.yaml | E2_analysis.json:n_snapshots.lone_keystone | {:d} | 34 | `34` | sections/03_pedestrian_model.tex:67 | 5 |
| EtwoNST | core.yaml | E2_analysis.json:n_snapshots.lone_keystone_second_trap | {:d} | 26 | `26` | sections/03_pedestrian_model.tex:67 | 2 |
| EtwoReplayCThreePubFlips | core.yaml | E2_analysis.json:b_replay_determinism.pooled.C3_pub.freed_disagree | {:d} | 5 | `5` | sections/06_screening.tex:31 | 1 |
| EtwoReplayN | core.yaml | E2_analysis.json:b_replay_determinism.pooled.C3_pub.replays | {:d} | 300 | `300` | sections/06_screening.tex:31 | 1 |
| FinCritN | final.yaml | final_corrected.json:criterion.n | {:d} | 196 | `196` | sections/03_pedestrian_model.tex:67 | 1 |
| FinCritNegN | final.yaml | final_corrected.json:criterion.n_neg | {:d} | 2 | `2` | sections/03_pedestrian_model.tex:67 | 2 |
| FinCritPosN | final.yaml | final_corrected.json:criterion.n_pos | {:d} | 194 | `194` | sections/05_deadlock_physics.tex:19 | 1 |
| FixAfourDiscLegFlip | core.yaml | fix_a4.json:headline.first_discontinuity.n_leg_normal_flip | {:d} | 4 | `4` | sections/06_screening.tex:31 | 1 |
| FixAfourDiscN | core.yaml | fix_a4.json:headline.first_discontinuity.n | {:d} | 5 | `5` | sections/06_screening.tex:31 | 1 |
| FixAsixSigFiftyClHi | core.yaml | fix_a6.json:e5.E5b_corrected.seed_cluster_boot95.1 | {:.3f} | 0.0485538 | `0.049` | sections/06_screening.tex:34 | 1 |
| FixAsixSigFiftyClLo | core.yaml | fix_a6.json:e5.E5b_corrected.seed_cluster_boot95.0 | {:.3f} | 0.0399085 | `0.040` | sections/06_screening.tex:34 | 1 |
| FixAthreeCollapseSlope | core.yaml | fix_a3.json:collapse.free_intercepts.slope | {:.2f} | -0.93234 | `-0.93` | sections/05_deadlock_physics.tex:42 | 1 |
| FixAthreeCollapseSlopeHi | core.yaml | fix_a3.json:collapse.free_intercepts.slope_ci95.1 | {:.2f} | -0.878765 | `-0.88` | sections/05_deadlock_physics.tex:42 | 1 |
| FixAthreeCollapseSlopeLo | core.yaml | fix_a3.json:collapse.free_intercepts.slope_ci95.0 | {:.2f} | -0.979295 | `-0.98` | sections/05_deadlock_physics.tex:42 | 1 |
| FixAthreeEfourQual | core.yaml | fix_a3.json:counts.selection.e4_qualifying | {:d} | 32 | `32` | sections/03_pedestrian_model.tex:67 | 1 |
| FixAthreeNuRatioAll | core.yaml | fix_a3.json:langer.summary.all.ratio_nu_hat_over_langer_median | {:.2f} | 0.688871 | `0.69` | sections/05_deadlock_physics.tex:43 | 1 |
| FixAthreePairBelowOne | core.yaml | fix_a3.json:counts.pair.below1_every_level | {:d} | 7 | `7` | sections/05_deadlock_physics.tex:54 | 1 |
| GmaxTwenty | core.yaml | E1_analysis.json:gmax_curve.gmax_N.80 | {:.0f} | 83.3122 | `83` | sections/05_deadlock_physics.tex:10 | 1 |
| KeystoneBLone | core.yaml | E1_chain.json:stuck_alone_criterion_check.class_counts.E1b.lone_keystone | {:d} | 34 | `34` | sections/03_pedestrian_model.tex:67 | 2 |
| KeystoneBSecondTrap | core.yaml | E1_chain.json:stuck_alone_criterion_check.class_counts.E1b.lone_keystone_second_trap | {:d} | 160 | `160` | sections/03_pedestrian_model.tex:67 | 2 |
| LoneBarMed | core.yaml | E6_analysis.json:lifetimes.barrier_picture.dU_median | {:.1f} | 6.41479 | `6.4` | sections/05_deadlock_physics.tex:54 | 1 |
| LoneBarN | core.yaml | E6_analysis.json:lifetimes.barrier_picture.n_barriers | {:d} | 56 | `56` | sections/03_pedestrian_model.tex:67 | 2 |
| PairAxisMax | pair.yaml | E7b_analysis.json:a_statics.axis_dist_m.max | {:.2f} | 0.503206 | `0.50` | sections/05_deadlock_physics.tex:48 | 1 |
| PairAxisMin | pair.yaml | E7b_analysis.json:a_statics.axis_dist_m.min | {:.2f} | 0.40026 | `0.40` | sections/05_deadlock_physics.tex:48 | 1 |
| PairBarMax | pair.yaml | E7b_analysis.json:d_barriers.dU.max | {:.1f} | 1.11166 | `1.1` | sections/05_deadlock_physics.tex:54 | 1 |
| PairBarMed | pair.yaml | E7b_analysis.json:d_barriers.dU.median | {:.2f} | 0.20537 | `0.21` | sections/05_deadlock_physics.tex:54 | 1 |
| PairBarN | pair.yaml | E7b_analysis.json:d_barriers.accepted | {:d} | 12 | `12` | sections/05_deadlock_physics.tex:54 | 2 |
| PairBsPubFreed | pair.yaml | E7b_analysis.json:s3_matched.pub.rate.freed_a | {:d} | 22 | `22` | tables/table3_observed.tex:25 | 2 |
| PairBsPubHand | pair.yaml | E7b_analysis.json:s3_matched.pub.handedness.plus_lower_first | {:d} | 22 | `22` | tables/table3_observed.tex:25 | 2 |
| PairBsPubMinusFreed | pair.yaml | E7b_analysis.json:s3_matched.pub.handedness.minus_n | {:d} | 21 | `21` | sections/06_screening.tex:55 | 3 |
| PairBsPubMinusUpper | pair.yaml | E7b_analysis.json:s3_matched.pub.handedness.minus_upper_first | {:d} | 21 | `21` | tables/table3_observed.tex:25 | 1 |
| PairBsPubN | pair.yaml | E7b_analysis.json:s3_matched.pub.handedness.plus_n | {:d} | 22 | `22` | tables/table3_observed.tex:25 | 2 |
| PairBsPubRevA | pair.yaml | E7b_analysis.json:s3_matched.pub.reversal.disc_a_only | {:d} | 13 | `13` | sections/06_screening.tex:55 | 2 |
| PairBsPubRevB | pair.yaml | E7b_analysis.json:s3_matched.pub.reversal.disc_b_only | {:d} | 14 | `14` | sections/06_screening.tex:55 | 2 |
| PairBsRvoFreed | pair.yaml | E7b_analysis.json:s3_matched.rvo2.rate.freed_a | {:d} | 8 | `8` | tables/table5_bias.tex:18 | 1 |
| PairBstarMax | pair.yaml | E7b_analysis.json:a_statics.fold_threshold.min_both_signs.max | {:.3f} | 0.0383203 | `0.038` | sections/05_deadlock_physics.tex:52 | 1 |
| PairBstarMed | pair.yaml | E7b_analysis.json:a_statics.fold_threshold.min_both_signs.median | {:.3f} | 0.0163672 | `0.016` | sections/05_deadlock_physics.tex:52 | 1 |
| PairBstarRvo | pair.yaml | E7b_analysis.json:s3_matched.rvo2.b_star | {:.4f} | 0.0090625 | `0.0091` | tables/table5_bias.tex:18 | 1 |
| PairConsPubFreed | pair.yaml | E7b_analysis.json:b_quench.constraint_only_pub.freed | {:d} | 45 | `45` | sections/06_screening.tex:51 | 1 |
| PairConsRvoFreed | pair.yaml | E7b_analysis.json:b_quench.constraint_only_rvo2.freed | {:d} | 44 | `44` | sections/06_screening.tex:51 | 1 |
| PairDriveFreed | pair.yaml | E7b_analysis.json:b_quench.drive_only.freed | {:d} | 33 | `33` | sections/06_screening.tex:51 | 1 |
| PairDriveRvoPRel | pair.yaml | E7b_analysis.json:c_decomposition.drive_vs_rvo2.mcnemar_p | p | 8.67993e-07 | `\ensuremath{<10^{-6}}` | sections/06_screening.tex:51 | 1 |
| PairFoldAgree | pair.yaml | E7b_analysis.json:a_statics.fold_prediction.agree | {:d} | 363 | `363` | sections/05_deadlock_physics.tex:52 | 1 |
| PairFoldFN | pair.yaml | E7b_analysis.json:a_statics.fold_prediction.FN | {:d} | 5 | `5` | sections/05_deadlock_physics.tex:52 | 1 |
| PairFoldN | pair.yaml | E7b_analysis.json:a_statics.fold_prediction.n | {:d} | 368 | `368` | sections/05_deadlock_physics.tex:52 | 1 |
| PairFrozenMinusFreed | pair.yaml | E7b_analysis.json:b_quench.frozen_minus.freed | {:d} | 1 | `1` | sections/06_screening.tex:51 | 2 |
| PairFrozenPlusFreed | pair.yaml | E7b_analysis.json:b_quench.frozen_plus.freed | {:d} | 34 | `34` | sections/06_screening.tex:51 | 2 |
| PairLamOneMed | pair.yaml | E7b_analysis.json:a_statics.lambda1.median | {:.0f} | 93.9733 | `94` | sections/05_deadlock_physics.tex:50 | 1 |
| PairLamOneMin | pair.yaml | E7b_analysis.json:a_statics.lambda1.min | {:.0f} | 65.0366 | `65` | sections/05_deadlock_physics.tex:50 | 1 |
| PairLamRatioMax | pair.yaml | E7b_analysis.json:a_statics.lambda2_over_lambda1.max | {:.0f} | 14.0837 | `14` | sections/05_deadlock_physics.tex:50 | 1 |
| PairLamRatioMin | pair.yaml | E7b_analysis.json:a_statics.lambda2_over_lambda1.min | {:.0f} | 12.3005 | `12` | sections/05_deadlock_physics.tex:50 | 1 |
| PairN | pair.yaml | E7b_analysis.json:n_snapshots | {:d} | 46 | `46` | sections/03_pedestrian_model.tex:67 | 16 |
| PairNoiseLowFreed | pair.yaml | E7b_analysis.json:b_quench.noise0p01.freed | {:d} | 224 | `224` | sections/05_deadlock_physics.tex:54 | 1 |
| PairNoiseLowN | pair.yaml | E7b_analysis.json:b_quench.noise0p01.n | {:d} | 230 | `230` | sections/05_deadlock_physics.tex:54 | 1 |
| PairPubFreed | pair.yaml | E7b_analysis.json:b_quench.C3_pub.freed | {:d} | 21 | `21` | sections/06_screening.tex:51 | 5 |
| PairPubLower | pair.yaml | E7b_analysis.json:b_quench.C3_pub.first_lower | {:d} | 11 | `11` | sections/06_screening.tex:55 | 3 |
| PairPubRvoPRel | pair.yaml | E7b_analysis.json:c_decomposition.pub_vs_rvo2.mcnemar_p | p | 0.00012207 | `\ensuremath{<10^{-3}}` | sections/06_screening.tex:51 | 1 |
| PairRvoFreed | pair.yaml | E7b_analysis.json:b_quench.C3_rvo2.freed | {:d} | 7 | `7` | sections/06_screening.tex:51 | 6 |
| PairSoftCommon | pair.yaml | E7b_analysis.json:a_statics.softest_common_lateral | {:d} | 46 | `46` | sections/05_deadlock_physics.tex:50 | 1 |
| PairStrictMin | pair.yaml | E7b_analysis.json:a_statics.strict_min | {:d} | 46 | `46` | sections/05_deadlock_physics.tex:50 | 1 |
| PendCEdgeGapCompleteMax | p_end.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.gap_complete.max | sig | 15.6 | `16` | sections/07_experiments.tex:28 | 1 |
| PendCOneGapCompleteMax | p_end.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.gap_complete.max | sig | 20.36 | `20` | sections/07_experiments.tex:27 | 1 |
| PendCOneGapLowerMedianTwo | p_end.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.c_median_lower_bound | floor | 415.92 | `410` | sections/07_experiments.tex:34 | 1 |
| PendCThreeGapCompleteMax | p_end.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.gap_complete.max | sig | 7.64 | `7.6` | sections/07_experiments.tex:29 | 1 |
| PendCThreeGapLowerMedianTwo | p_end.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.c_median_lower_bound | floor | 431.8 | `430` | sections/07_experiments.tex:34 | 1 |
| PendCThreeGapsTwo | p_end.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.gaps_gt_2s.mean | {:.0f} | 10.12 | `10` | sections/07_experiments.tex:21 | 1 |
| PendHumanFlow | p_end.yaml | rev_D.json:humans_corrected.flow.mean | {:.1f} | 1.47179 | `1.5` | sections/07_experiments.tex:19 | 1 |
| PendHumanFlowHi | p_end.yaml | rev_D.json:humans_corrected.flow.ci95.1 | {:.1f} | 1.73336 | `1.7` | sections/07_experiments.tex:19 | 1 |
| PendHumanFlowLo | p_end.yaml | rev_D.json:humans_corrected.flow.ci95.0 | {:.1f} | 1.21023 | `1.2` | sections/07_experiments.tex:19 | 1 |
| PendHumanFlowMin | p_end.yaml | rev_D.json:humans_corrected.flow_range.0 | {:.1f} | 1.15438 | `1.2` | sections/07_experiments.tex:19 | 1 |
| PendModelFlowMax | p_end.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.flow.max | {:.2f} | 0.994632 | `0.99` | sections/07_experiments.tex:19 | 1 |
| PendSigFluct | p_end.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.fluct.mean | {:.2f} | 0.107884 | `0.11` | sections/07_experiments.tex:34 | 1 |
| PendSigGapCompleteMax | p_end.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.gap_complete.max | sig | 237.16 | `240` | sections/07_experiments.tex:30 | 1 |
| PendSigGapKMMedian | p_end.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.km_median | {:.0f} | 95.92 | `96` | sections/07_experiments.tex:34 | 1 |
| PendSigGapsTwo | p_end.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.gaps_gt_2s.mean | {:.0f} | 18.16 | `18` | sections/07_experiments.tex:21 | 1 |
| PmodLoneWMinTwo | p_model.yaml | rev_A2.json:snapshots.lone.w_min | floor | 0.99941 | `0.99` | sections/03_pedestrian_model.tex:41 | 1 |
| PmodRunsWMinTwo | p_model.yaml | rev_A2.json:runs.w_min | floor | 0.95768 | `0.95` | sections/03_pedestrian_model.tex:41 | 1 |
| PphysBodyFine | p_physics.yaml | rev_B4.json:by_dt.dt0p001.peak_body_force_kN | sig | 18.3239 | `18` | sections/05_deadlock_physics.tex:57 | 1 |
| PphysBstarMin | p_physics.yaml | E7b_analysis.json:a_statics.fold_threshold.min_both_signs.min | {:.5f} | 0.000507813 | `0.00051` | sections/05_deadlock_physics.tex:52 | 1 |
| PphysContactFine | p_physics.yaml | rev_B4.json:by_dt.dt0p001.peak_contact_force_kN | sig | 4.84825 | `4.8` | sections/05_deadlock_physics.tex:57 | 1 |
| PphysDriveTotal | p_physics.yaml | E1_analysis.json:E1b.drives_N.C3_rest_total.p50 | {:.0f} | 430.455 | `430` | sections/05_deadlock_physics.tex:6 | 2 |
| PphysFoldMissGap | p_physics.yaml | E7b_analysis.json:a_statics.fold_prediction.disagree_max_rel_gap_pct | {:.1f} | 1.72745 | `1.7` | sections/05_deadlock_physics.tex:52 | 1 |
| PphysGmaxMeanR | p_physics.yaml | rev_A13.json:drive.gmax_at_mean_r_disp | sig | 156 | `160` | sections/05_deadlock_physics.tex:14 | 1 |
| PphysGmaxThirty | p_physics.yaml | rev_A13.json:gmax.r030_N | sig | 291 | `290` | sections/05_deadlock_physics.tex:10 | 1 |
| PphysGmaxThirtyFive | p_physics.yaml | E1_analysis.json:gmax_curve.gmax_N.230 | sig | 543.264 | `540` | sections/05_deadlock_physics.tex:10 | 1 |
| PphysLamOneMax | p_physics.yaml | E7b_analysis.json:a_statics.lambda1.max | sig | 121.001 | `120` | sections/05_deadlock_physics.tex:50 | 1 |
| PphysNegMarginMax | p_physics.yaml | rev_B1.json:neg_peak.margin_range_N.1 | {:.4f} | -0.00689406 | `-0.0069` | sections/05_deadlock_physics.tex:19 | 1 |
| PphysPairBarMin | p_physics.yaml | E7b_analysis.json:d_barriers.dU.min | {:.3f} | 0.0570923 | `0.057` | sections/05_deadlock_physics.tex:54 | 1 |
| PphysPosMarginMin | p_physics.yaml | rev_B1.json:pos_rest.margin_range_N.0 | {:.4f} | 0.00807958 | `0.0081` | sections/05_deadlock_physics.tex:19 | 1 |
| PphysRatioFull | p_physics.yaml | E4_analysis.json:headline.ratio_med_full | {:.1f} | 1.15073 | `1.2` | sections/05_deadlock_physics.tex:42 | 1 |
| PphysStuckAloneFrac | p_physics.yaml | E1_analysis.json:E1b.stuck_alone_frac_C1.frac | {:.2f} | 0.2343 | `0.23` | sections/05_deadlock_physics.tex:14 | 1 |
| PphysWeidMinFloor | p_physics.yaml | final_corrected.json:terminal.weidmann_min | floor | 0.996502 | `0.99` | sections/05_deadlock_physics.tex:14 | 1 |
| PprotEllBA | p_protocol.yaml | E3_analysis.json:headline.ell_ps_b1p5_obs | {:.1f} | 2.16379 | `2.2` | tables/table3_observed.tex:19 | 2 |
| PprotEllBAPred | p_protocol.yaml | E3_analysis.json:headline.ell_ps_b1p5_pred | {:.1f} | 2.21617 | `2.2` | tables/table4_noise.tex:14 | 1 |
| PprotMuMax | p_protocol.yaml | rev_A10.json:headline.mu1_max | sci/2 | 1115.44 | `\ensuremath{1.1\times10^{3}}` | sections/04_protocol.tex:23 | 1 |
| PprotVarRatio | p_protocol.yaml | T3_variance.json:ratio_measured_formula_mean | {:.1f} | 1.00272 | `1.0` | sections/04_protocol.tex:34 | 1 |
| PscrCommitConfHead | p_screen.yaml | rev_A14.json:identity.conference_head_short | {} | e05d8f6 | `e05d8f6` | sections/10_back_matter.tex:4 | 1 |
| PscrCreepSpeedMin | p_screen.yaml | rev_A13.json:creep.speed_median_min | {:.3f} | 0.091 | `0.091` | sections/06_screening.tex:31 | 1 |
| PscrJacAsymMin | p_screen.yaml | rev_A11.json:headline.jac_asym_min | {:.3f} | 0.0770209 | `0.077` | sections/06_screening.tex:51 | 1 |
| PscrLKDiff | p_screen.yaml | E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.paired_rate_diff_noise_minus_C3 | {:+.3f} | -0.0117647 | `-0.012` | tables/table4_noise.tex:14 | 1 |
| PscrLKDiffHi | p_screen.yaml | E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.paired_rate_diff_ci95_boot.1 | {:.3f} | 0.0823529 | `0.082` | tables/table4_noise.tex:14 | 1 |
| PscrLKDiffLo | p_screen.yaml | E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.paired_rate_diff_ci95_boot.0 | {:.2f} | -0.1 | `-0.10` | tables/table4_noise.tex:14 | 1 |
| PscrLKNHalfEJ | p_screen.yaml | rev_A9.json:lone.lone_keystone.N1.rules.half.E_J | {:.3f} | 0.060996 | `0.061` | tables/table4_noise.tex:15 | 1 |
| PscrNOneDiff | p_screen.yaml | N1_analysis.json:rate.diff_vs_C3_rvo2.diff | {:+.3f} | -0.0176471 | `-0.018` | tables/table4_noise.tex:15 | 1 |
| PscrNOneDiffHi | p_screen.yaml | N1_analysis.json:rate.diff_vs_C3_rvo2.ci95.1 | {:.3f} | 0.0441176 | `0.044` | tables/table4_noise.tex:15 | 1 |
| PscrNOneDiffLo | p_screen.yaml | N1_analysis.json:rate.diff_vs_C3_rvo2.ci95.0 | {:.3f} | -0.0735294 | `-0.074` | tables/table4_noise.tex:15 | 1 |
| PscrOrcaLnRatio | p_screen.yaml | E3_analysis.json:headline.c3_ln_ratio | {:.4f} | -0.00480377 | `-0.0048` | tables/table4_noise.tex:16 | 1 |
| PscrPairBsRvoMinusFreed | p_screen.yaml | E7b_analysis.json:s3_matched.rvo2.reversal.freed_a | {:d} | 5 | `5` | sections/06_screening.tex:55 | 1 |
| PscrPairBstarPub | p_screen.yaml | E7b_analysis.json:s3_matched.pub.b_star | {:.3f} | 0.0223437 | `0.022` | tables/table5_bias.tex:14 | 1 |
| PscrPairPubDiff | p_screen.yaml | rev_A8.json:pair.delta.bstar_pub_plus_vs_C3_pub.T120.delta | {:+.3f} | 0.0217391 | `+0.022` | tables/table5_bias.tex:14 | 1 |
| PscrPairPubDiffHi | p_screen.yaml | rev_A8.json:pair.delta.bstar_pub_plus_vs_C3_pub.T120.ci95.1 | {:.2f} | 0.217391 | `0.22` | tables/table5_bias.tex:14 | 1 |
| PscrPairPubDiffLo | p_screen.yaml | rev_A8.json:pair.delta.bstar_pub_plus_vs_C3_pub.T120.ci95.0 | {:.2f} | -0.152174 | `-0.15` | tables/table5_bias.tex:14 | 1 |
| PscrPairRvoDiff | p_screen.yaml | rev_A8.json:pair.delta.bstar_rvo2_plus_vs_C3_rvo2.T120.delta | {:+.3f} | 0.0217391 | `+0.022` | tables/table5_bias.tex:18 | 1 |
| PscrPairRvoDiffHi | p_screen.yaml | rev_A8.json:pair.delta.bstar_rvo2_plus_vs_C3_rvo2.T120.ci95.1 | {:.2f} | 0.173913 | `0.17` | tables/table5_bias.tex:18 | 1 |
| PscrPairRvoDiffLo | p_screen.yaml | rev_A8.json:pair.delta.bstar_rvo2_plus_vs_C3_rvo2.T120.ci95.0 | {:.2f} | -0.152174 | `-0.15` | tables/table5_bias.tex:18 | 1 |
| PscrPairRvoEJ | p_screen.yaml | rev_A9.json:pair.rvo2.freed_sets.E_J | {:.3f} | 0.0935697 | `0.094` | tables/table5_bias.tex:18 | 1 |
| PscrReplayPubMaxDt | p_screen.yaml | E2_analysis.json:b_replay_determinism.pooled.C3_pub.max_abs_dt_blocker_exit_s | {:.0f} | 80.77 | `81` | sections/06_screening.tex:31 | 1 |
| PscrSTDiffLo | p_screen.yaml | rev_A6.json:lone_keystone_second_trap.delta.E2_analysis_ci95.0 | {:.3f} | 0.0846154 | `0.085` | tables/table4_noise.tex:19 | 1 |
| PscrStallMaxDiff | p_screen.yaml | E6_analysis.json:lifetimes.pred_vs_obs.max_abs_diff | {:.3f} | 0.0450949 | `0.045` | sections/06_screening.tex:37 | 1 |
| PscrTimeLoneEtwoEff | p_screen.yaml | rev_A7.json:lone_E2.time.effect | {:.0f} | 19.3132 | `19` | tables/table4_noise.tex:14 | 1 |
| PscrTimeLoneEtwoHi | p_screen.yaml | rev_A7.json:lone_E2.time.ci95.1 | {:.0f} | 29.142 | `29` | tables/table4_noise.tex:14 | 1 |
| PscrTimeLoneEtwoLo | p_screen.yaml | rev_A7.json:lone_E2.time.ci95.0 | {:.1f} | 9.06115 | `9.1` | tables/table4_noise.tex:14 | 1 |
| PscrTimeLoneNoneEff | p_screen.yaml | rev_A7.json:lone_N1.time.effect | {:.0f} | 19.4491 | `19` | tables/table4_noise.tex:15 | 1 |
| PscrTimeLoneNoneHi | p_screen.yaml | rev_A7.json:lone_N1.time.ci95.1 | {:.0f} | 27.3371 | `27` | tables/table4_noise.tex:15 | 1 |
| PscrTimeLoneNoneLo | p_screen.yaml | rev_A7.json:lone_N1.time.ci95.0 | {:.0f} | 11.1846 | `11` | tables/table4_noise.tex:15 | 1 |
| PscrTimePairPubEff | p_screen.yaml | rev_A7.json:pair_pub.time.effect | {:.1f} | -2.05674 | `-2.1` | tables/table5_bias.tex:14 | 1 |
| PscrTimePairPubHi | p_screen.yaml | rev_A7.json:pair_pub.time.ci95.1 | {:.0f} | 17.5129 | `18` | tables/table5_bias.tex:14 | 1 |
| PscrTimePairPubLo | p_screen.yaml | rev_A7.json:pair_pub.time.ci95.0 | {:.0f} | -21.2093 | `-21` | tables/table5_bias.tex:14 | 1 |
| PscrTimePairRvoEff | p_screen.yaml | rev_A7.json:pair_rvo2.time.effect | {:.1f} | -1.32457 | `-1.3` | tables/table5_bias.tex:18 | 1 |
| PscrTimePairRvoHi | p_screen.yaml | rev_A7.json:pair_rvo2.time.ci95.1 | {:.0f} | 18.0895 | `18` | tables/table5_bias.tex:18 | 1 |
| PscrTimePairRvoLo | p_screen.yaml | rev_A7.json:pair_rvo2.time.ci95.0 | {:.0f} | -20.2109 | `-20` | tables/table5_bias.tex:18 | 1 |
| PscrTimeSecondEff | p_screen.yaml | rev_A7.json:second.time.effect | {:.0f} | -16.0358 | `-16` | tables/table4_noise.tex:19 | 1 |
| PscrTimeSecondHi | p_screen.yaml | rev_A7.json:second.time.ci95.1 | {:.1f} | 3.06699 | `3.1` | tables/table4_noise.tex:19 | 1 |
| PscrTimeSecondLo | p_screen.yaml | rev_A7.json:second.time.ci95.0 | {:.0f} | -35.7751 | `-36` | tables/table4_noise.tex:19 | 1 |
| PscrTimeWholeEff | p_screen.yaml | rev_A7.json:whole_E6.time.effect | {:.0f} | 71.8918 | `72` | tables/table4_noise.tex:23 | 1 |
| PscrTimeWholeHi | p_screen.yaml | rev_A7.json:whole_E6.time.ci95.1 | {:.0f} | 110.098 | `110` | tables/table4_noise.tex:23 | 1 |
| PscrTimeWholeLo | p_screen.yaml | rev_A7.json:whole_E6.time.ci95.0 | {:.0f} | 33.1718 | `33` | tables/table4_noise.tex:23 | 1 |
| PscrWholeDiff | p_screen.yaml | E6_analysis.json:completion.diff_sigma_minus_C3.diff | {:+.3f} | -0.0107527 | `-0.011` | tables/table4_noise.tex:23 | 1 |
| PscrWholeDiffHi | p_screen.yaml | E6_analysis.json:completion.diff_sigma_minus_C3.ci95.1 | {:.3f} | 0.0784992 | `0.078` | tables/table4_noise.tex:23 | 1 |
| PscrWholeDiffLo | p_screen.yaml | E6_analysis.json:completion.diff_sigma_minus_C3.ci95.0 | {:.2f} | -0.0997336 | `-0.10` | tables/table4_noise.tex:23 | 1 |
| ResidAllMax | core.yaml | field_residuals.json:overall_max_N | sci/1 | 4.90264e-07 | `\ensuremath{5\times10^{-7}}` | sections/04_protocol.tex:19 | 1 |
| RevAeightLKNoiseCMatchFrom | revision.yaml | rev_A8.json:snapshots.lone_keystone.scan_vs_C3_rvo2.noise0p07.matched_T_s.0 | {:d} | 70 | `70` | sections/04_protocol.tex:12 | 1 |
| RevAeightLKNoiseNoneMatchFrom | revision.yaml | rev_A8.json:snapshots.lone_keystone.scan_vs_C3_rvo2.noiseN1.matched_T_s.0 | {:d} | 85 | `85` | sections/04_protocol.tex:12 | 1 |
| RevAeightSTRvoLatest | revision.yaml | rev_A8.json:snapshots.lone_keystone_second_trap.latest_exit_s.C3_rvo2 | {:.0f} | 13.99 | `14` | sections/04_protocol.tex:12 | 1 |
| RevAeightWholeNoiseMatchFrom | revision.yaml | rev_A8.json:whole.scan_vs_E6a_C3_rvo2.E6b_noise_sigma_star.matched_T_s.0 | {:d} | 425 | `425` | sections/04_protocol.tex:12 | 1 |
| RevAeightWholeRvoLatest | revision.yaml | rev_A8.json:whole.C3_rvo2_latest_completion_s | {:.0f} | 160.97 | `161` | sections/04_protocol.tex:12 | 1 |
| RevAelevenJacAsymMax | revision.yaml | rev_A11.json:headline.jac_asym_max | {:.2f} | 0.0994776 | `0.10` | sections/06_screening.tex:51 | 1 |
| RevAelevenPairBinds | revision.yaml | rev_A11.json:headline.pair_binds | {:d} | 92 | `92` | sections/06_screening.tex:51 | 1 |
| RevAelevenPairDisc | revision.yaml | rev_A11.json:headline.pair_rvo2_disc | {:d} | 28 | `28` | sections/06_screening.tex:51 | 1 |
| RevAelevenPairDiscStatic | revision.yaml | rev_A11.json:headline.pair_rvo2_disc_explained | {:d} | 13 | `13` | sections/06_screening.tex:51 | 1 |
| RevAelevenRatioMax | revision.yaml | rev_A11.json:headline.pair_ratio_max | {:.2f} | 0.346621 | `0.35` | sections/06_screening.tex:51 | 1 |
| RevAelevenRatioMin | revision.yaml | rev_A11.json:headline.pair_ratio_min | {:.2f} | 0.186081 | `0.19` | sections/06_screening.tex:51 | 1 |
| RevAfifteenPairPubHeld | revision.yaml | rev_A15.json:audit.E7b.by_arm.C3_pub.held | {:d} | 25 | `25` | sections/06_screening.tex:48 | 1 |
| RevAfifteenPairPubMoving | revision.yaml | rev_A15.json:audit.E7b.by_arm.C3_pub.held_ran_to_window | {:d} | 25 | `25` | sections/06_screening.tex:48 | 1 |
| RevAfifteenPairRvoHeld | revision.yaml | rev_A15.json:audit.E7b.by_arm.C3_rvo2.held | {:d} | 39 | `39` | sections/06_screening.tex:48 | 1 |
| RevAfifteenPairRvoMoving | revision.yaml | rev_A15.json:audit.E7b.by_arm.C3_rvo2.held_ran_to_window | {:d} | 39 | `39` | sections/06_screening.tex:48 | 1 |
| RevAfiveEthreeQual | revision.yaml | rev_A5.json:bar_e3_e4.e3.qualifying | {:d} | 36 | `36` | sections/03_pedestrian_model.tex:67 | 1 |
| RevAfiveGateFailSecond | revision.yaml | rev_A5.json:bar_e3_e4.gate_fail_second_trap | {:d} | 4 | `4` | sections/03_pedestrian_model.tex:67 | 1 |
| RevAfiveRuns | revision.yaml | rev_A5.json:funnel.runs | {:d} | 200 | `200` | sections/03_pedestrian_model.tex:67 | 1 |
| RevAfiveXEtwoN | revision.yaml | rev_A5x.json:n_snapshots.E2 | {:d} | 26 | `26` | sections/06_screening.tex:25 | 1 |
| RevAfiveXNewN | revision.yaml | rev_A5x.json:n_snapshots.new | {:d} | 134 | `134` | sections/06_screening.tex:25 | 1 |
| RevAfiveXPoolDriveFreed | revision.yaml | rev_A5x.json:rates.pooled.drive_only.freed | {:d} | 149 | `149` | sections/06_screening.tex:25 | 1 |
| RevAfiveXPoolDriveOrcaPDisp | revision.yaml | rev_A5x.json:paired.pooled.drive_only_vs_C3_rvo2.p_disp | {} | <10^{-8} | `<10^{-8}` | sections/06_screening.tex:25 | 1 |
| RevAfiveXPoolLegacyReplayChanged | revision.yaml | rev_A5x.json:rates.pooled.C3_pub.replays_changed | {:d} | 13 | `13` | sections/06_screening.tex:31 | 2 |
| RevAfiveXPoolLegacyReplays | revision.yaml | rev_A5x.json:rates.pooled.C3_pub.replays | {:d} | 800 | `800` | sections/06_screening.tex:31 | 2 |
| RevAfiveXPoolN | revision.yaml | rev_A5x.json:n_snapshots.pooled | {:d} | 160 | `160` | sections/06_screening.tex:25 | 3 |
| RevAfiveXPoolNoiseOrcaEff | revision.yaml | rev_A5x.json:paired.pooled.noise0p07_vs_C3_rvo2.effect | {:+#.2g} | 0.1325 | `+0.13` | sections/06_screening.tex:25 | 1 |
| RevAfiveXPoolNoiseOrcaHi | revision.yaml | rev_A5x.json:paired.pooled.noise0p07_vs_C3_rvo2.ci95.1 | {:#.2g} | 0.19125 | `0.19` | sections/06_screening.tex:25 | 1 |
| RevAfiveXPoolNoiseOrcaLo | revision.yaml | rev_A5x.json:paired.pooled.noise0p07_vs_C3_rvo2.ci95.0 | {:#.2g} | 0.0762188 | `0.076` | sections/06_screening.tex:25 | 1 |
| RevAfiveXPoolOrcaFreed | revision.yaml | rev_A5x.json:rates.pooled.C3_rvo2.freed | {:d} | 121 | `121` | sections/06_screening.tex:25 | 1 |
| RevAfiveXPoolSFMFreed | revision.yaml | rev_A5x.json:rates.pooled.C1.freed | {:d} | 2 | `2` | sections/06_screening.tex:25 | 1 |
| RevAfiveXVsEtwoMinPHolmRel | revision.yaml | rev_A5x.json:new_vs_E2_min_p_holm | p | 1 | `\ensuremath{=1.0}` | sections/06_screening.tex:25 | 1 |
| RevAfourteenCommitConf | revision.yaml | rev_A14.json:identity.conference_commit_short | {} | 9762177 | `9762177` | sections/10_back_matter.tex:4 | 1 |
| RevAfourteenCommitIntro | revision.yaml | rev_A14.json:identity.introduced_commit_short | {} | c43af16 | `c43af16` | sections/10_back_matter.tex:4 | 1 |
| RevAfourteenDefectLine | revision.yaml | rev_A14.json:identity.defect_lineno_worktree | {:d} | 113 | `113` | sections/10_back_matter.tex:4 | 1 |
| RevAnineLKNHalfA | revision.yaml | rev_A9.json:lone.lone_keystone.N1.rules.half.a | {:d} | 3 | `3` | sections/06_screening.tex:20 | 1 |
| RevAnineLKNHalfB | revision.yaml | rev_A9.json:lone.lone_keystone.N1.rules.half.b | {:d} | 4 | `4` | sections/06_screening.tex:20 | 1 |
| RevAnineLKNHalfJ | revision.yaml | rev_A9.json:lone.lone_keystone.N1.rules.half.J | {:.2f} | 0.75 | `0.75` | sections/06_screening.tex:20 | 2 |
| RevAnineLKNHalfPRel | revision.yaml | rev_A9.json:lone.lone_keystone.N1.rules.half.p_ge | p | 0.000668449 | `\ensuremath{<10^{-3}}` | tables/table4_noise.tex:15 | 1 |
| RevAnineMisclass | revision.yaml | rev_A9.json:lone.misclassification_5seed.expected_snapshots_misclassified | {:.1f} | 1.48875 | `1.5` | sections/06_screening.tex:20 | 1 |
| RevAninePairPubEJ | revision.yaml | rev_A9.json:pair.pub.freed_sets.E_J | {:.2f} | 0.308275 | `0.31` | tables/table5_bias.tex:14 | 1 |
| RevAninePairPubJ | revision.yaml | rev_A9.json:pair.pub.freed_sets.J | {:.2f} | 0.433333 | `0.43` | tables/table5_bias.tex:14 | 1 |
| RevAninePairPubPRel | revision.yaml | rev_A9.json:pair.pub.freed_sets.p_ge | p | 0.0724319 | `\ensuremath{=0.072}` | tables/table5_bias.tex:14 | 1 |
| RevAninePairRvoJ | revision.yaml | rev_A9.json:pair.rvo2.freed_sets.J | {:.2f} | 0 | `0.00` | tables/table5_bias.tex:18 | 1 |
| RevAninePairRvoPLeRel | revision.yaml | rev_A9.json:pair.rvo2.freed_sets.p_le | p | 0.235784 | `\ensuremath{=0.24}` | tables/table5_bias.tex:18 | 1 |
| RevAnineWholeEEJ | revision.yaml | rev_A9.json:whole.E6b_vs_orca.E_J | {:.2f} | 0.301507 | `0.30` | sections/06_screening.tex:34 | 2 |
| RevAnineWholeEJ | revision.yaml | rev_A9.json:whole.E6b_vs_orca.J | {:.2f} | 0.409836 | `0.41` | sections/06_screening.tex:34 | 2 |
| RevAnineWholeEPRel | revision.yaml | rev_A9.json:whole.E6b_vs_orca.p_ge | p | 0.00197769 | `\ensuremath{=0.0020}` | sections/06_screening.tex:34 | 2 |
| RevAoneDiscA | revision.yaml | rev_A1.json:quench.tau_all.sub_only | {:d} | 0 | `0` | sections/06_screening.tex:16 | 1 |
| RevAoneDiscB | revision.yaml | rev_A1.json:quench.tau_all.drive_only | {:d} | 0 | `0` | sections/06_screening.tex:16 | 1 |
| RevAoneDriveRatioHi | revision.yaml | rev_A1.json:drive_ratio_range.1 | {:.1f} | 2.19734 | `2.2` | sections/00_abstract.tex:3 | 3 |
| RevAoneDriveRatioLo | revision.yaml | rev_A1.json:drive_ratio_range.0 | {:.1f} | 1.8052 | `1.8` | sections/00_abstract.tex:3 | 3 |
| RevAoneLoneFreed | revision.yaml | rev_A1.json:quench.exact_lone.freed_sub | {:d} | 30 | `30` | sections/06_screening.tex:16 | 1 |
| RevAoneLoneN | revision.yaml | rev_A1.json:quench.exact_lone.n | {:d} | 34 | `34` | sections/06_screening.tex:16 | 1 |
| RevAoneSecondFreed | revision.yaml | rev_A1.json:quench.exact_second.freed_sub | {:d} | 24 | `24` | sections/06_screening.tex:16 | 1 |
| RevAoneSecondN | revision.yaml | rev_A1.json:quench.exact_second.n | {:d} | 26 | `26` | sections/06_screening.tex:16 | 1 |
| RevAoneTauPrimeHi | revision.yaml | rev_A1.json:tau_prime_range_s.1 | {:.2f} | 0.272452 | `0.27` | sections/01_introduction.tex:22 | 2 |
| RevAoneTauPrimeLo | revision.yaml | rev_A1.json:tau_prime_range_s.0 | {:.2f} | 0.223022 | `0.22` | sections/01_introduction.tex:22 | 2 |
| RevAsevenLoneEtwoEllPHolmRel | revision.yaml | rev_A7.json:lone_E2.ell.p_holm | p | 0.00012207 | `\ensuremath{<10^{-3}}` | tables/table4_noise.tex:14 | 1 |
| RevAsevenLoneEtwoFreedPHolmRel | revision.yaml | rev_A7.json:lone_E2.freed.p_holm | p | 0.902344 | `\ensuremath{=0.90}` | tables/table4_noise.tex:14 | 1 |
| RevAsevenLoneEtwoReplayDiscA | revision.yaml | rev_A7.json:lone_E2.replay.b_first_only | {:d} | 9 | `9` | sections/06_screening.tex:20 | 2 |
| RevAsevenLoneEtwoReplayDiscB | revision.yaml | rev_A7.json:lone_E2.replay.c_second_only | {:d} | 0 | `0` | tables/table3_observed.tex:19 | 1 |
| RevAsevenLoneEtwoTimePHolmRel | revision.yaml | rev_A7.json:lone_E2.time.p_holm | p | 0.00164999 | `\ensuremath{=0.0016}` | tables/table4_noise.tex:14 | 1 |
| RevAsevenLoneNoneFreedPHolmRel | revision.yaml | rev_A7.json:lone_N1.freed.p_holm | p | 1 | `\ensuremath{=1.0}` | tables/table4_noise.tex:15 | 1 |
| RevAsevenLoneNoneReplayDiscA | revision.yaml | rev_A7.json:lone_N1.replay.b_first_only | {:d} | 14 | `14` | tables/table4_noise.tex:15 | 1 |
| RevAsevenLoneNoneTimePHolmRel | revision.yaml | rev_A7.json:lone_N1.time.p_holm | p | 9.99995e-05 | `\ensuremath{<10^{-4}}` | tables/table4_noise.tex:15 | 1 |
| RevAsevenPairPubFreedPHolmRel | revision.yaml | rev_A7.json:pair_pub.freed.p_holm | p | 1 | `\ensuremath{=1.0}` | tables/table5_bias.tex:14 | 1 |
| RevAsevenPairPubHandPHolmRel | revision.yaml | rev_A7.json:pair_pub.handed.p_holm | p | 0.000735846 | `\ensuremath{<10^{-3}}` | tables/table5_bias.tex:14 | 1 |
| RevAsevenPairPubTimePHolmRel | revision.yaml | rev_A7.json:pair_pub.time.p_holm | p | 1 | `\ensuremath{=1.0}` | tables/table5_bias.tex:14 | 1 |
| RevAsevenPairRvoFreedPHolmRel | revision.yaml | rev_A7.json:pair_rvo2.freed.p_holm | p | 1 | `\ensuremath{=1.0}` | tables/table5_bias.tex:18 | 1 |
| RevAsevenPairRvoHandPHolmRel | revision.yaml | rev_A7.json:pair_rvo2.handed.p_holm | p | 0.027972 | `\ensuremath{=0.028}` | tables/table5_bias.tex:18 | 1 |
| RevAsevenPairRvoTimePHolmRel | revision.yaml | rev_A7.json:pair_rvo2.time.p_holm | p | 1 | `\ensuremath{=1.0}` | tables/table5_bias.tex:18 | 1 |
| RevAsevenPushLoneTimeEff | revision.yaml | rev_A7.json:push_lone.time.effect | {:.1f} | -4.01088 | `-4.0` | sections/06_screening.tex:16 | 1 |
| RevAsevenPushLoneTimePHolmRel | revision.yaml | rev_A7.json:push_lone.time.p_holm | p | 1.99999e-05 | `\ensuremath{<10^{-4}}` | sections/06_screening.tex:16 | 1 |
| RevAsevenSecondFreedPHolmRel | revision.yaml | rev_A7.json:second.freed.p_holm | p | 0.0615234 | `\ensuremath{=0.062}` | tables/table4_noise.tex:19 | 1 |
| RevAsevenSecondTimePHolmRel | revision.yaml | rev_A7.json:second.time.p_holm | p | 0.125 | `\ensuremath{=0.13}` | tables/table4_noise.tex:19 | 1 |
| RevAsevenWholeEsixClassPHolmRel | revision.yaml | rev_A7.json:whole_E6.class.p_holm | p | 0.00239976 | `\ensuremath{=0.0024}` | sections/06_screening.tex:37 | 1 |
| RevAsevenWholeEsixFreedPHolmRel | revision.yaml | rev_A7.json:whole_E6.freed.p_holm | p | 1 | `\ensuremath{=1.0}` | tables/table4_noise.tex:23 | 1 |
| RevAsevenWholeEsixTimePHolmRel | revision.yaml | rev_A7.json:whole_E6.time.p_holm | p | 0.00147999 | `\ensuremath{=0.0015}` | tables/table4_noise.tex:23 | 1 |
| RevAsixSTDiff | revision.yaml | rev_A6.json:lone_keystone_second_trap.delta.E2_analysis_value | {:+.2f} | 0.246154 | `+0.25` | tables/table4_noise.tex:19 | 1 |
| RevAsixSTDiffHi | revision.yaml | rev_A6.json:lone_keystone_second_trap.delta.E2_analysis_ci95.1 | {:.2f} | 0.438462 | `0.44` | tables/table4_noise.tex:19 | 1 |
| RevAsixSTJ | revision.yaml | rev_A6.json:lone_keystone_second_trap.J.value | {:.2f} | 0.2 | `0.20` | tables/table4_noise.tex:19 | 1 |
| RevAsixSTJInd | revision.yaml | rev_A6.json:lone_keystone_second_trap.J.independence_expected_J | {:.2f} | 0.100643 | `0.10` | tables/table4_noise.tex:19 | 1 |
| RevAsixSTJIndP | revision.yaml | rev_A6.json:lone_keystone_second_trap.J.p_J_ge_observed | {:.2f} | 0.267692 | `0.27` | tables/table4_noise.tex:19 | 1 |
| RevAsixSTNoiseDisagree | revision.yaml | rev_A6.json:lone_keystone_second_trap.noise0p07.snapshots_runs_disagree | {:d} | 5 | `5` | tables/table4_noise.tex:19 | 1 |
| RevAsixSTNoiseFreed | revision.yaml | rev_A6.json:lone_keystone_second_trap.noise0p07.freed | {:d} | 117 | `117` | tables/table4_noise.tex:19 | 1 |
| RevAsixSTNoiseN | revision.yaml | rev_A6.json:lone_keystone_second_trap.noise0p07.n_runs | {:d} | 130 | `130` | tables/table4_noise.tex:19 | 1 |
| RevAsixSTOrcaFreed | revision.yaml | rev_A6.json:lone_keystone_second_trap.C3_rvo2.freed | {:d} | 17 | `17` | tables/table4_noise.tex:20 | 1 |
| RevAsixSTOrcaN | revision.yaml | rev_A6.json:lone_keystone_second_trap.C3_rvo2.n | {:d} | 26 | `26` | tables/table4_noise.tex:20 | 1 |
| RevAsixSTOrcaReplayDis | revision.yaml | rev_A6.json:lone_keystone_second_trap.C3_rvo2.replays_outcome_differs | {:d} | 0 | `0` | tables/table4_noise.tex:20 | 1 |
| RevAsixSTOrcaReplays | revision.yaml | rev_A6.json:lone_keystone_second_trap.C3_rvo2.replays | {:d} | 130 | `130` | tables/table4_noise.tex:20 | 1 |
| RevAsixSTSnaps | revision.yaml | rev_A6.json:lone_keystone_second_trap.n_snapshots | {:d} | 26 | `26` | tables/table4_noise.tex:18 | 2 |
| RevAtenMuMin | revision.yaml | rev_A10.json:headline.mu1_min | {:.0f} | 65.7291 | `66` | sections/04_protocol.tex:23 | 1 |
| RevAtenStrict | revision.yaml | rev_A10.json:headline.strict | {:d} | 60 | `60` | sections/04_protocol.tex:23 | 1 |
| RevAthirteenCreepDriftMax | revision.yaml | rev_A13.json:creep.vx_mean_max_mm_s | {:.1f} | 3.3 | `3.3` | sections/06_screening.tex:31 | 1 |
| RevAthirteenCreepDriftMin | revision.yaml | rev_A13.json:creep.vx_mean_min_mm_s | {:.2f} | -0.14 | `-0.14` | sections/06_screening.tex:31 | 1 |
| RevAthirteenCreepSpeedMax | revision.yaml | rev_A13.json:creep.speed_median_max | {:.2f} | 0.14 | `0.14` | sections/06_screening.tex:31 | 1 |
| RevAthirteenDriveOverGmax | revision.yaml | rev_A13.json:drive.ratio_drive_over_gmax_mean_r | {:.1f} | 1.4 | `1.4` | sections/05_deadlock_physics.tex:14 | 1 |
| RevAthirteenRadiusMean | revision.yaml | rev_A13.json:drive.r_mean_m_disp | {:.2f} | 0.25 | `0.25` | sections/05_deadlock_physics.tex:14 | 1 |
| RevAthirteenStackMax | revision.yaml | rev_A13.json:stack.stuck_resid_max | {:d} | 9 | `9` | sections/05_deadlock_physics.tex:19 | 1 |
| RevAthirteenStackMedian | revision.yaml | rev_A13.json:stack.stuck_resid_median | {:.0f} | 2 | `2` | sections/05_deadlock_physics.tex:19 | 1 |
| RevAthirteenStackN | revision.yaml | rev_A13.json:stack.n_stacks | {:d} | 194 | `194` | sections/05_deadlock_physics.tex:19 | 1 |
| RevAthirteenStuckFirstEightMax | revision.yaml | rev_A13.json:deciles.first8_max | {:.2f} | 0.2 | `0.20` | sections/05_deadlock_physics.tex:19 | 1 |
| RevAthirteenStuckFirstEightMin | revision.yaml | rev_A13.json:deciles.first8_min | {:.2f} | 0.14 | `0.14` | sections/05_deadlock_physics.tex:19 | 1 |
| RevAthirteenStuckNinthDecile | revision.yaml | rev_A13.json:deciles.ninth | {:.2f} | 0.31 | `0.31` | sections/05_deadlock_physics.tex:19 | 1 |
| RevAthirteenStuckTenthDecile | revision.yaml | rev_A13.json:deciles.tenth | {:.2f} | 0.62 | `0.62` | sections/05_deadlock_physics.tex:19 | 1 |
| RevAthreeBarN | revision.yaml | rev_A3.json:n_barriers | {:d} | 56 | `56` | sections/06_screening.tex:37 | 1 |
| RevAthreeSevenBelowOneK | revision.yaml | rev_A3.json:levels.s0p07.pooled.n_below_1 | {:d} | 36 | `36` | sections/05_deadlock_physics.tex:45 | 1 |
| RevAthreeSevenMed | revision.yaml | rev_A3.json:levels.s0p07.pooled.median | {:.2f} | 0.637942 | `0.64` | sections/05_deadlock_physics.tex:45 | 1 |
| RevAthreeSevenQone | revision.yaml | rev_A3.json:levels.s0p07.pooled.q25 | {:.2f} | 0.154394 | `0.15` | sections/05_deadlock_physics.tex:45 | 1 |
| RevAthreeSevenQthree | revision.yaml | rev_A3.json:levels.s0p07.pooled.q75 | {:.1f} | 1.60609 | `1.6` | sections/05_deadlock_physics.tex:45 | 1 |
| RevAthreeStarBelowOneK | revision.yaml | rev_A3.json:levels.sstar.pooled.n_below_1 | {:d} | 23 | `23` | sections/06_screening.tex:37 | 1 |
| RevAthreeStarMed | revision.yaml | rev_A3.json:levels.sstar.pooled.median | {:.1f} | 1.43332 | `1.4` | sections/06_screening.tex:37 | 1 |
| RevBfiveGenN | revision.yaml | rev_B5.json:gen.n | {:d} | 320 | `320` | sections/01_introduction.tex:21 | 2 |
| RevBfiveGenPair | revision.yaml | rev_B5.json:gen.pair.cell | {:d} | 0 | `0` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBfiveGenPairPDisp | revision.yaml | rev_B5.json:gen.pair.mcnemar_p_disp | {} | <10^{-13} | `<10^{-13}` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBfiveGenPairRef | revision.yaml | rev_B5.json:gen.pair.reference | {:d} | 46 | `46` | sections/01_introduction.tex:21 | 2 |
| RevBfiveKept | revision.yaml | rev_B5.json:main.kept | {:d} | 0 | `0` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBfiveN | revision.yaml | rev_B5.json:main.n | {:d} | 46 | `46` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBfiveOverhangMax | revision.yaml | rev_B5.json:overhang_mm.max | {:.0f} | 59 | `59` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBfiveOverhangMin | revision.yaml | rev_B5.json:overhang_mm.min | {:.2f} | 0.26 | `0.26` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBfiveRuleN | revision.yaml | rev_B5.json:main.n_checked | {:d} | 276 | `276` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBfourLifeMaxFine | revision.yaml | rev_B4.json:by_dt.dt0p001.max_lifetime_s | {:.1f} | 2.4 | `2.4` | sections/05_deadlock_physics.tex:57 | 1 |
| RevBfourN | revision.yaml | rev_B4.json:by_dt.dt0p001.n | {:d} | 10 | `10` | sections/05_deadlock_physics.tex:57 | 2 |
| RevBfourOverlapCoarse | revision.yaml | rev_B4.json:by_dt.dt0p01.max_overlap_arch_cm | {:.0f} | 25.5093 | `26` | sections/05_deadlock_physics.tex:57 | 1 |
| RevBfourOverlapMid | revision.yaml | rev_B4.json:by_dt.dt0p0025.max_overlap_arch_cm | {:.1f} | 4.01579 | `4.0` | sections/05_deadlock_physics.tex:57 | 1 |
| RevBfourPersistentHi | revision.yaml | rev_B4.json:by_dt.dt0p001.persistent_wilson_hi | {:.2f} | 0.27754 | `0.28` | sections/05_deadlock_physics.tex:57 | 1 |
| RevBoneNegN | revision.yaml | rev_B1.json:neg_peak.n | {:d} | 200 | `200` | sections/05_deadlock_physics.tex:19 | 1 |
| RevBonePosN | revision.yaml | rev_B1.json:pos_rest.n | {:d} | 200 | `200` | sections/05_deadlock_physics.tex:19 | 1 |
| RevBsixGenN | revision.yaml | rev_B6.json:gen.n | {:d} | 320 | `320` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBsixGenPair | revision.yaml | rev_B6.json:gen.pair.cell | {:d} | 91 | `91` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBsixGenPairPDisp | revision.yaml | rev_B6.json:gen.pair.mcnemar_p_disp | {} | <10^{-4} | `<10^{-4}` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBsixGenPairRef | revision.yaml | rev_B6.json:gen.pair.reference | {:d} | 46 | `46` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBsixKept | revision.yaml | rev_B6.json:static.kept | {:d} | 46 | `46` | sections/05_deadlock_physics.tex:48 | 1 |
| RevBthreeDUDeep | revision.yaml | rev_B3.json:snapshots.E1b_seed192.dU_alone_J | {:.0f} | 56.3098 | `56` | sections/05_deadlock_physics.tex:42 | 1 |
| RevBthreeDUMid | revision.yaml | rev_B3.json:snapshots.E1b_seed162.dU_alone_J | {:.0f} | 20.7531 | `21` | sections/05_deadlock_physics.tex:42 | 1 |
| RevBthreeDUShallow | revision.yaml | rev_B3.json:snapshots.E1b_seed72.dU_alone_J | {:.1f} | 5.83084 | `5.8` | sections/05_deadlock_physics.tex:42 | 1 |
| RevBtwoHeldActiveMax | revision.yaml | rev_B2.json:arrival_record_B2.stuck_held.n_active_max | {:d} | 9 | `9` | sections/05_deadlock_physics.tex:21 | 1 |
| RevBtwoNRuns | revision.yaml | rev_B2.json:n_runs | {:d} | 1100 | `1100` | sections/05_deadlock_physics.tex:21 | 1 |
| RevBtwoNbest | revision.yaml | rev_B2.json:prediction.N_best.N | {:.0f} | 19.2 | `19` | sections/05_deadlock_physics.tex:21 | 1 |
| RevBtwoPredHundredOffset | revision.yaml | rev_B2.json:prediction.N100.w50_pred_minus_obs_m | {:.3f} | 0.0410589 | `0.041` | sections/05_deadlock_physics.tex:21 | 1 |
| RevBtwoWfifty | revision.yaml | rev_B2.json:fit_all.w50_m | {:.3f} | 0.878209 | `0.878` | sections/01_introduction.tex:21 | 3 |
| RevBtwoWfiftyHi | revision.yaml | rev_B2.json:fit_all.w50_ci95.1 | {:.3f} | 0.88256 | `0.883` | sections/05_deadlock_physics.tex:21 | 1 |
| RevBtwoWfiftyLo | revision.yaml | rev_B2.json:fit_all.w50_ci95.0 | {:.3f} | 0.8739 | `0.874` | sections/05_deadlock_physics.tex:21 | 1 |
| RevBtwoWhi | revision.yaml | rev_B2.json:bracket.w_hi_median_run_max_wc_m | {:.2f} | 0.91961 | `0.92` | sections/05_deadlock_physics.tex:21 | 1 |
| RevBtwoWlo | revision.yaml | rev_B2.json:bracket.w_lo_median_agent_wc_m | {:.2f} | 0.754145 | `0.75` | sections/05_deadlock_physics.tex:21 | 1 |
| RevDFourDonethirtyPassed | revision.yaml | rev_D.json:runs.4D130.n_pass_participant_rule | {:d} | 128 | `128` | sections/07_experiments.tex:11 | 1 |
| RevDFourDthirtyPassed | revision.yaml | rev_D.json:runs.4D030.n_pass_participant_rule | {:d} | 135 | `135` | sections/07_experiments.tex:11 | 1 |
| RevDThreeCEdgeCapped | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.capped | {:d} | 0 | `0` | sections/07_experiments.tex:28 | 1 |
| RevDThreeCEdgeCens | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.n_censored | {:d} | 4 | `4` | sections/07_experiments.tex:28 | 1 |
| RevDThreeCEdgeComplete | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.complete | {:d} | 21 | `21` | sections/07_experiments.tex:28 | 1 |
| RevDThreeCEdgeDeadlock | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.deadlock | {:d} | 4 | `4` | sections/07_experiments.tex:28 | 1 |
| RevDThreeCEdgeFlowRatio | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.flow_ratio.ratio | {:.2f} | 0.56274 | `0.56` | sections/07_experiments.tex:28 | 1 |
| RevDThreeCEdgeFlowRatioHi | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.flow_ratio.ci95.1 | {:.2f} | 0.671074 | `0.67` | sections/07_experiments.tex:28 | 1 |
| RevDThreeCEdgeFlowRatioLo | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.flow_ratio.ci95.0 | {:.2f} | 0.471896 | `0.47` | sections/07_experiments.tex:28 | 1 |
| RevDThreeCEdgeGapKMMedian | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_edge.km_median | {:.1f} | 6.08 | `6.1` | sections/07_experiments.tex:34 | 1 |
| RevDThreeCOneCapped | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.capped | {:d} | 0 | `0` | sections/07_experiments.tex:27 | 1 |
| RevDThreeCOneCens | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.n_censored | {:d} | 23 | `23` | sections/07_experiments.tex:27 | 1 |
| RevDThreeCOneComplete | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.complete | {:d} | 2 | `2` | sections/07_experiments.tex:27 | 1 |
| RevDThreeCOneDeadlock | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.deadlock | {:d} | 23 | `23` | sections/07_experiments.tex:27 | 1 |
| RevDThreeCOneFlowRatio | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.flow_ratio.ratio | {:.2f} | 0.499192 | `0.50` | sections/07_experiments.tex:27 | 1 |
| RevDThreeCOneFlowRatioHi | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.flow_ratio.ci95.1 | {:.2f} | 0.594832 | `0.59` | sections/07_experiments.tex:27 | 1 |
| RevDThreeCOneFlowRatioLo | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.flow_ratio.ci95.0 | {:.2f} | 0.41893 | `0.42` | sections/07_experiments.tex:27 | 1 |
| RevDThreeCOneFluct | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf.fluct.mean | {:.3f} | 0.0924238 | `0.092` | sections/07_experiments.tex:34 | 1 |
| RevDThreeCSigCapped | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.capped | {:d} | 7 | `7` | sections/07_experiments.tex:30 | 1 |
| RevDThreeCSigCens | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.n_censored | {:d} | 7 | `7` | sections/07_experiments.tex:30 | 1 |
| RevDThreeCSigComplete | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.complete | {:d} | 18 | `18` | sections/07_experiments.tex:30 | 1 |
| RevDThreeCSigDeadlock | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.deadlock | {:d} | 0 | `0` | sections/07_experiments.tex:30 | 1 |
| RevDThreeCSigFlowRatio | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.flow_ratio.ratio | {:.2f} | 0.400819 | `0.40` | sections/07_experiments.tex:30 | 1 |
| RevDThreeCSigFlowRatioHi | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.flow_ratio.ci95.1 | {:.2f} | 0.484314 | `0.48` | sections/07_experiments.tex:30 | 1 |
| RevDThreeCSigFlowRatioLo | revision.yaml | rev_D.json:D3.rerun.per_variant.C1_cf_sig.flow_ratio.ci95.0 | {:.2f} | 0.331718 | `0.33` | sections/07_experiments.tex:30 | 1 |
| RevDThreeCThreeCapped | revision.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.capped | {:d} | 14 | `14` | sections/07_experiments.tex:29 | 1 |
| RevDThreeCThreeCens | revision.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.n_censored | {:d} | 15 | `15` | sections/07_experiments.tex:29 | 1 |
| RevDThreeCThreeComplete | revision.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.complete | {:d} | 10 | `10` | sections/07_experiments.tex:29 | 1 |
| RevDThreeCThreeDeadlock | revision.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.deadlock | {:d} | 1 | `1` | sections/07_experiments.tex:29 | 1 |
| RevDThreeCThreeFlowRatio | revision.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.flow_ratio.ratio | {:.2f} | 0.595842 | `0.60` | sections/07_experiments.tex:29 | 1 |
| RevDThreeCThreeFlowRatioHi | revision.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.flow_ratio.ci95.1 | {:.2f} | 0.710063 | `0.71` | sections/07_experiments.tex:29 | 1 |
| RevDThreeCThreeFlowRatioLo | revision.yaml | rev_D.json:D3.rerun.per_variant.C3_rvo2_cf.flow_ratio.ci95.0 | {:.2f} | 0.499995 | `0.50` | sections/07_experiments.tex:29 | 1 |
| RevDThreeRatioMax | revision.yaml | rev_D.json:D3.rerun.range.max | {:.2f} | 0.595842 | `0.60` | sections/00_abstract.tex:3 | 4 |
| RevDThreeRatioMin | revision.yaml | rev_D.json:D3.rerun.range.min | {:.2f} | 0.400819 | `0.40` | sections/00_abstract.tex:3 | 4 |
| RunNFiveDefaultN | runs.yaml | N5_analysis.json:cells.default.n | {:d} | 25 | `25` | sections/05_deadlock_physics.tex:57 | 1 |
| RunNOneFreed | runs.yaml | N1_analysis.json:rate.freed | {:d} | 588 | `588` | tables/table4_noise.tex:15 | 1 |
| RunNOneJNoiseNoise | runs.yaml | N1_analysis.json:identity.noise_vs_noise_halves.jaccard | {:.2f} | 0.75 | `0.75` | sections/06_screening.tex:20 | 1 |
| RunNOneRunsN | runs.yaml | N1_analysis.json:rate.n | {:d} | 680 | `680` | tables/table4_noise.tex:15 | 1 |
| RunNOneSigma | runs.yaml | N1_analysis.json:sigma_n1 | {:.4f} | 0.0717 | `0.0717` | sections/06_screening.tex:19 | 2 |
| RunNSixAtEnd | runs.yaml | N6_analysis.json:all.member_at_segment_end | {:d} | 92 | `92` | sections/05_deadlock_physics.tex:52 | 1 |
| RunNSixN | runs.yaml | N6_analysis.json:n_jobs | {:d} | 92 | `92` | sections/05_deadlock_physics.tex:52 | 1 |
| RvAeightClimbTol | revision2.yaml | rev2_A8.json:macros.climb_tol | {:.2f} | 0.01 | `0.01` | sections/04_protocol.tex:41 | 1 |
| RvAeightComplete | revision2.yaml | rev2_A8.json:macros.complete | {:d} | 4 | `4` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightDeadlocks | revision2.yaml | rev2_A8.json:macros.deadlocks | {:d} | 196 | `196` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightDoubleTol | revision2.yaml | rev2_A8.json:macros.double_tol_pct | {:.0f} | 1 | `1` | sections/04_protocol.tex:41 | 1 |
| RvAeightEfiveHi | revision2.yaml | rev2_A8.json:macros.e5_hi | {:d} | 141 | `141` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightEfiveLo | revision2.yaml | rev2_A8.json:macros.e5_lo | {:d} | 42 | `42` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightEoneHi | revision2.yaml | rev2_A8.json:macros.e1_hi | {:d} | 241 | `241` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightEoneLo | revision2.yaml | rev2_A8.json:macros.e1_lo | {:d} | 42 | `42` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightEsixHi | revision2.yaml | rev2_A8.json:macros.e6_hi | {:d} | 427 | `427` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightEsixLo | revision2.yaml | rev2_A8.json:macros.e6_lo | {:d} | 242 | `242` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightFTol | revision2.yaml | rev2_A8.json:macros.f_tol | {:.0f} | 5 | `5` | sections/04_protocol.tex:41 | 1 |
| RvAeightFailed | revision2.yaml | rev2_A8.json:macros.failed | {:d} | 4 | `4` | sections/04_protocol.tex:41 | 1 |
| RvAeightGridTol | revision2.yaml | rev2_A8.json:macros.grid_tol_pct | {:.0f} | 2 | `2` | sections/04_protocol.tex:41 | 1 |
| RvAeightImgHi | revision2.yaml | rev2_A8.json:macros.img_hi | {:d} | 124 | `124` | sections/04_protocol.tex:41 | 1 |
| RvAeightImgLo | revision2.yaml | rev2_A8.json:macros.img_lo | {:d} | 31 | `31` | sections/04_protocol.tex:41 | 1 |
| RvAeightImgMid | revision2.yaml | rev2_A8.json:macros.img_mid | {:d} | 62 | `62` | sections/04_protocol.tex:41 | 1 |
| RvAeightOrcaHorizon | revision2.yaml | rev2_A8.json:macros.orca_th | {:.0f} | 5 | `5` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightOverlap | revision2.yaml | rev2_A8.json:macros.overlap_cm | {:.0f} | 2 | `2` | sections/04_protocol.tex:41 | 1 |
| RvAeightPertHi | revision2.yaml | rev2_A8.json:macros.pert_hi | {:d} | 904 | `904` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightPertLo | revision2.yaml | rev2_A8.json:macros.pert_lo | {:d} | 900 | `900` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightRuns | revision2.yaml | rev2_A8.json:macros.runs | {:d} | 200 | `200` | sections/03_pedestrian_model.tex:68 | 1 |
| RvAeightRunsPerSnap | revision2.yaml | rev2_A8.json:macros.runs_per_snap | {:d} | 6 | `6` | sections/03_pedestrian_model.tex:68 | 2 |
| RvAeightXExit | revision2.yaml | rev2_A8.json:macros.x_exit | {:.2f} | 10.35 | `10.35` | sections/04_protocol.tex:41 | 1 |
| RvAelevenCOneCfK | revision2.yaml | rev2_A11.json:cells.C1_cf.k | {:d} | 5 | `5` | sections/01_introduction.tex:14 | 1 |
| RvAelevenCOneCfN | revision2.yaml | rev2_A11.json:cells.C1_cf.n | {:d} | 300 | `300` | sections/01_introduction.tex:14 | 1 |
| RvAelevenCOnePubK | revision2.yaml | rev2_A11.json:cells.C1_pub.k | {:d} | 3 | `3` | sections/01_introduction.tex:14 | 1 |
| RvAelevenCOnePubN | revision2.yaml | rev2_A11.json:cells.C1_pub.n | {:d} | 200 | `200` | sections/01_introduction.tex:14 | 1 |
| RvAelevenCThreeCfK | revision2.yaml | rev2_A11.json:cells.C3_cf.k | {:d} | 101 | `101` | sections/01_introduction.tex:14 | 1 |
| RvAelevenCThreeCfN | revision2.yaml | rev2_A11.json:cells.C3_cf.n | {:d} | 186 | `186` | sections/01_introduction.tex:14 | 1 |
| RvAelevenCThreePubK | revision2.yaml | rev2_A11.json:cells.C3_pub.k | {:d} | 29 | `29` | sections/01_introduction.tex:14 | 1 |
| RvAelevenCThreePubN | revision2.yaml | rev2_A11.json:cells.C3_pub.n | {:d} | 50 | `50` | sections/01_introduction.tex:14 | 1 |
| RvAfiveLoneEtwoDiffHiNinety | revision2.yaml | rev2_A5.json:comparisons.lone_E2.boot_ci90.1 | sig/2 | 0.0647059 | `0.065` | sections/06_screening.tex:19 | 1 |
| RvAfiveLoneEtwoDiffLoNinety | revision2.yaml | rev2_A5.json:comparisons.lone_E2.boot_ci90.0 | sig/2 | -0.0823529 | `-0.082` | sections/06_screening.tex:19 | 1 |
| RvAfiveLoneEtwoPTostDisp | revision2.yaml | rev2_A5.json:comparisons.lone_E2.p_tost_t | p/2 | 0.0324501 | `0.032` | sections/06_screening.tex:19 | 1 |
| RvAfiveLoneEtwoWinFrom | revision2.yaml | rev2_A5.json:comparisons.lone_E2.window_at_horizon_from_s | {:.0f} | 89 | `89` | sections/06_screening.tex:19 | 1 |
| RvAfiveLoneNoneDiffHiNinety | revision2.yaml | rev2_A5.json:comparisons.lone_N1.boot_ci90.1 | sig/2 | 0.0308824 | `0.031` | sections/06_screening.tex:19 | 1 |
| RvAfiveLoneNoneDiffLoNinety | revision2.yaml | rev2_A5.json:comparisons.lone_N1.boot_ci90.0 | sig/2 | -0.0647059 | `-0.065` | sections/06_screening.tex:19 | 1 |
| RvAfiveLoneNonePTostDisp | revision2.yaml | rev2_A5.json:comparisons.lone_N1.p_tost_t | p/2 | 0.00476872 | `0.0048` | sections/06_screening.tex:19 | 1 |
| RvAfiveLoneNoneWinFrom | revision2.yaml | rev2_A5.json:comparisons.lone_N1.window_at_horizon_from_s | {:.0f} | 86 | `86` | sections/06_screening.tex:19 | 1 |
| RvAfiveMargin | revision2.yaml | rev2_A5.json:margin | {:.2f} | 0.1 | `0.10` | sections/04_protocol.tex:11 | 5 |
| RvAfivePairLegacyDiffHiNinety | revision2.yaml | rev2_A5.json:comparisons.pair_legacy.boot_ci90.1 | sig/2 | 0.173913 | `0.17` | sections/06_screening.tex:54 | 1 |
| RvAfivePairLegacyDiffLoNinety | revision2.yaml | rev2_A5.json:comparisons.pair_legacy.boot_ci90.0 | sig/2 | -0.130435 | `-0.13` | sections/06_screening.tex:54 | 1 |
| RvAfivePairLegacyPTostDisp | revision2.yaml | rev2_A5.json:comparisons.pair_legacy.p_tost_t | p/2 | 0.196047 | `0.20` | sections/06_screening.tex:54 | 1 |
| RvAfivePairRvoPTostDisp | revision2.yaml | rev2_A5.json:comparisons.pair_rvo2.p_tost_t | p/2 | 0.181233 | `0.18` | sections/06_screening.tex:54 | 1 |
| RvAfiveSecondPoolWinOtherOneFrom | revision2.yaml | rev2_A5.json:comparisons.second_pool.window_equiv90_nontrivial_s.0.0 | {:.0f} | 22 | `22` | sections/06_screening.tex:25 | 1 |
| RvAfiveSecondPoolWinOtherOneTo | revision2.yaml | rev2_A5.json:comparisons.second_pool.window_equiv90_nontrivial_s.0.1 | {:.0f} | 43 | `43` | sections/06_screening.tex:25 | 1 |
| RvAfiveWholeDiffHiNinety | revision2.yaml | rev2_A5.json:comparisons.whole_E6.boot_ci90.1 | sig/2 | 0.0645161 | `0.065` | sections/06_screening.tex:35 | 1 |
| RvAfiveWholeDiffLoNinety | revision2.yaml | rev2_A5.json:comparisons.whole_E6.boot_ci90.0 | sig/2 | -0.0860215 | `-0.086` | sections/06_screening.tex:35 | 1 |
| RvAfiveWholePTostDisp | revision2.yaml | rev2_A5.json:comparisons.whole_E6.p_tost_t | p/2 | 0.0262625 | `0.026` | sections/06_screening.tex:35 | 1 |
| RvAfiveWholeWinFrom | revision2.yaml | rev2_A5.json:comparisons.whole_E6.window_at_horizon_from_s | {:.0f} | 545 | `545` | sections/06_screening.tex:35 | 1 |
| RvAfiveWholeWinTo | revision2.yaml | rev2_A5.json:comparisons.whole_E6.window_at_horizon_to_s | {:.0f} | 600 | `600` | sections/06_screening.tex:35 | 1 |
| RvAnineCOneLongRatio | revision2.yaml | rev2_A9.json:per_geometry.C1_cf.long.ratio | sig/2 | 0.535909 | `0.54` | sections/07_experiments.tex:19 | 1 |
| RvAnineCOneShortRatio | revision2.yaml | rev2_A9.json:per_geometry.C1_cf.short.ratio | sig/2 | 0.478588 | `0.48` | sections/07_experiments.tex:19 | 1 |
| RvAnineCSigNormalRatio | revision2.yaml | rev2_A9.json:per_geometry.C1_cf_sig.normal.ratio | sig/2 | 0.451092 | `0.45` | sections/07_experiments.tex:19 | 1 |
| RvAnineCThreeLongRatio | revision2.yaml | rev2_A9.json:per_geometry.C3_rvo2_cf.long.ratio | sig/2 | 0.616047 | `0.62` | sections/07_experiments.tex:19 | 1 |
| RvAnineCThreeNormalRatio | revision2.yaml | rev2_A9.json:per_geometry.C3_rvo2_cf.normal.ratio | sig/2 | 0.682844 | `0.68` | sections/07_experiments.tex:19 | 1 |
| RvAnineCThreeShortRatio | revision2.yaml | rev2_A9.json:per_geometry.C3_rvo2_cf.short.ratio | sig/2 | 0.584503 | `0.58` | sections/07_experiments.tex:19 | 1 |
| RvAnineDiameterOverShoulder | revision2.yaml | rev2_A9.json:radius.diameter_over_shoulder | sig/2 | 1.11111 | `1.1` | sections/07_experiments.tex:14 | 1 |
| RvAnineHumanWindowFlow | revision2.yaml | rev2_A9.json:humans_geom.pooled.window_mean | {:.2f} | 1.48814 | `1.49` | sections/07_experiments.tex:19 | 1 |
| RvAnineModelDiameter | revision2.yaml | rev2_A9.json:radius.model_diameter_mean_m | {:.2f} | 0.5 | `0.50` | sections/07_experiments.tex:14 | 1 |
| RvAnineShoulderWidth | revision2.yaml | rev2_A9.json:radius.shoulder_mean_m | {:.2f} | 0.45 | `0.45` | sections/07_experiments.tex:14 | 1 |
| RvAnineShoulderWidthSD | revision2.yaml | rev2_A9.json:radius.shoulder_sd_m | {:.2f} | 0.04 | `0.04` | sections/07_experiments.tex:14 | 1 |
| RvAnineWindowRatioMax | revision2.yaml | rev2_A9.json:window.range_ub.max | sig/2 | 0.637951 | `0.64` | sections/07_experiments.tex:19 | 1 |
| RvAnineWindowRatioMin | revision2.yaml | rev2_A9.json:window.range_ub.min | sig/2 | 0.542643 | `0.54` | sections/07_experiments.tex:19 | 1 |
| RvAsevenCMax | revision2.yaml | rev2_A7.json:headline.c_max | sig/2 | 1.16305 | `1.2` | sections/04_protocol.tex:33 | 1 |
| RvAsevenCMed | revision2.yaml | rev2_A7.json:headline.c_med | {:.1f} | 0.995503 | `1.0` | sections/04_protocol.tex:33 | 1 |
| RvAsevenCMin | revision2.yaml | rev2_A7.json:headline.c_min | sig/2 | 0.905652 | `0.91` | sections/04_protocol.tex:33 | 1 |
| RvAsixLegacyErrHi | revision2.yaml | rev2_A6.json:solvers.legacy.err_held_quench.hi95 | sig/2 | 0.298536 | `0.30` | sections/06_screening.tex:54 | 1 |
| RvAsixLegacyErrLo | revision2.yaml | rev2_A6.json:solvers.legacy.err_held_quench.lo95 | sig/2 | -0.289542 | `-0.29` | sections/06_screening.tex:54 | 1 |
| RvAsixLegacyErrMedian | revision2.yaml | rev2_A6.json:solvers.legacy.err_held_quench.median | sig/2 | 0.0443656 | `0.044` | sections/06_screening.tex:54 | 1 |
| RvAsixLegacyRefHi | revision2.yaml | rev2_A6.json:solvers.legacy.split_ref.hi95 | sig/2 | 0.304348 | `0.30` | sections/06_screening.tex:54 | 1 |
| RvAsixLegacyRefLo | revision2.yaml | rev2_A6.json:solvers.legacy.split_ref.lo95 | sig/2 | -0.304348 | `-0.30` | sections/06_screening.tex:54 | 1 |
| RvAsixNHalf | revision2.yaml | rev2_A6.json:n_half | {:d} | 23 | `23` | sections/06_screening.tex:54 | 2 |
| RvAsixNSplits | revision2.yaml | rev2_A6.json:n_splits | {:d} | 200 | `200` | sections/06_screening.tex:54 | 1 |
| RvAsixRvoErrHi | revision2.yaml | rev2_A6.json:solvers.rvo2.err_held_quench.hi95 | sig/2 | 0.401495 | `0.40` | sections/06_screening.tex:54 | 1 |
| RvAsixRvoErrLo | revision2.yaml | rev2_A6.json:solvers.rvo2.err_held_quench.lo95 | sig/2 | -0.189491 | `-0.19` | sections/06_screening.tex:54 | 1 |
| RvAsixRvoErrMedian | revision2.yaml | rev2_A6.json:solvers.rvo2.err_held_quench.median | sig/2 | 0.0434783 | `0.043` | sections/06_screening.tex:54 | 1 |
| RvAthreeCensFracMax | revision2.yaml | rev2_A3.json:censored_frac_5_7_max | sig/2 | 0.3 | `0.30` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeCensored | revision2.yaml | rev2_A3.json:pooled.censored | {:d} | 39 | `39` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeRatioDeep | revision2.yaml | rev2_A3.json:snapshots.E1b_seed192.ratio | sig/2 | 0.845213 | `0.85` | sections/00_abstract.tex:3 | 3 |
| RvAthreeRatioDeepHi | revision2.yaml | rev2_A3.json:snapshots.E1b_seed192.ci95_boot.1 | sig/2 | 0.958997 | `0.96` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeRatioDeepLo | revision2.yaml | rev2_A3.json:snapshots.E1b_seed192.ci95_boot.0 | sig/2 | 0.730478 | `0.73` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeRatioMid | revision2.yaml | rev2_A3.json:snapshots.E1b_seed162.ratio | sig/2 | 0.925442 | `0.93` | sections/00_abstract.tex:3 | 3 |
| RvAthreeRatioMidHi | revision2.yaml | rev2_A3.json:snapshots.E1b_seed162.ci95_boot.1 | sig/2 | 1.02792 | `1.0` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeRatioMidLo | revision2.yaml | rev2_A3.json:snapshots.E1b_seed162.ci95_boot.0 | sig/2 | 0.825844 | `0.83` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeRatioShallow | revision2.yaml | rev2_A3.json:snapshots.E1b_seed72.ratio | sig/2 | 0.900472 | `0.90` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeRatioShallowHi | revision2.yaml | rev2_A3.json:snapshots.E1b_seed72.ci95_boot.1 | sig/2 | 1.00122 | `1.0` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeRatioShallowLo | revision2.yaml | rev2_A3.json:snapshots.E1b_seed72.ci95_boot.0 | sig/2 | 0.806021 | `0.81` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeRestarts | revision2.yaml | rev2_A3.json:pooled.restarts | {:d} | 360 | `360` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeSlopeRatio | revision2.yaml | rev2_A3.json:pooled.ratio | sig/2 | 0.890546 | `0.89` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeSlopeRatioHi | revision2.yaml | rev2_A3.json:pooled.ci95_boot.1 | sig/2 | 0.94983 | `0.95` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeSlopeRatioLo | revision2.yaml | rev2_A3.json:pooled.ci95_boot.0 | sig/2 | 0.83096 | `0.83` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeTheoryRatio | revision2.yaml | rev2_A3.json:theory_pooled_ratio | sig/2 | 0.896568 | `0.90` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeTstSevenOverHarmDeep | revision2.yaml | rev2_A3.json:theory.E1b_seed192.nu_tst_7_over_harmonic | sig/2 | 0.627155 | `0.63` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeWeibullDeep | revision2.yaml | rev2_A3.json:snapshots.E1b_seed192.weibull_6_7.k | sig/2 | 0.663546 | `0.66` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeWeibullDeepHi | revision2.yaml | rev2_A3.json:snapshots.E1b_seed192.weibull_6_7.ci95.1 | sig/2 | 0.870538 | `0.87` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAthreeWeibullDeepLo | revision2.yaml | rev2_A3.json:snapshots.E1b_seed192.weibull_6_7.ci95.0 | sig/2 | 0.487039 | `0.49` | sections/05_deadlock_physics.tex:42 | 1 |
| RvAtwoAFitMed | revision2.yaml | rev2_A2.json:headline.A_fit_med | sig/2 | 0.968421 | `0.97` | sections/05_deadlock_physics.tex:43 | 1 |
| RvAtwoAMin | revision2.yaml | rev2_A2.json:headline.A_E4_min | sig/2 | 0.790659 | `0.79` | sections/05_deadlock_physics.tex:43 | 1 |
| RvAtwoGamOmegaMed | revision2.yaml | rev2_A2.json:headline.g_wb_med | sig/2 | 0.406052 | `0.41` | sections/05_deadlock_physics.tex:43 | 1 |
| RvAtwoLossMed | revision2.yaml | rev2_A2.json:headline.gS_dU_med | sig/2 | 4.48721 | `4.5` | sections/05_deadlock_physics.tex:43 | 1 |
| RvAtwoNFits | revision2.yaml | rev2_A2.json:headline.n_fits | {:d} | 28 | `28` | sections/05_deadlock_physics.tex:43 | 1 |
| StHeldCancel | core.yaml | E2_second_trap.json:strata.lone_keystone_second_trap.trace.rvo2.held.cancel_frac_mean.median | {:.2f} | 0.26881 | `0.27` | sections/06_screening.tex:25 | 1 |
| StuckAloneFracCThree | core.yaml | E1_analysis.json:E1b.stuck_alone_frac_C3_rest.frac | {:.3f} | 0.01275 | `0.013` | sections/05_deadlock_physics.tex:17 | 1 |
| StuckAloneN | core.yaml | E1_analysis.json:E1b.stuck_alone_frac_C1.n | {:,d} | 20000 | `20\,000` | sections/05_deadlock_physics.tex:6 | 2 |
| TabThreeLKNoiseDisagree | core.yaml | E2_analysis.json:b_replay_determinism.lone_keystone.noise0p07.seeds_disagree_on_freed | {:d} | 9 | `9` | tables/table4_noise.tex:14 | 1 |
| TabThreeLKNoiseSnaps | core.yaml | E2_analysis.json:b_replay_determinism.lone_keystone.noise0p07.snapshots | {:d} | 34 | `34` | tables/table4_noise.tex:14 | 1 |
| TabThreeLKRvoReplayDis | core.yaml | E2_analysis.json:b_replay_determinism.lone_keystone.C3_rvo2.freed_disagree | {:d} | 0 | `0` | sections/06_screening.tex:20 | 3 |
| TabThreeLKRvoReplays | core.yaml | E2_analysis.json:b_replay_determinism.lone_keystone.C3_rvo2.replays | {:d} | 170 | `170` | sections/06_screening.tex:20 | 3 |
| TabThreePairBsPubReplayDis | core.yaml | E7b_analysis.json:s3_matched.pub.replay.plus.discordant | {:d} | 0 | `0` | tables/table3_observed.tex:25 | 2 |
| TabThreePairBsReplays | core.yaml | E7b_analysis.json:s3_matched.pub.replay.plus.replays | {:d} | 230 | `230` | tables/table3_observed.tex:25 | 3 |
| TabThreePairBsRvoReplayDis | core.yaml | E7b_analysis.json:s3_matched.rvo2.replay.plus.discordant | {:d} | 0 | `0` | tables/table5_bias.tex:18 | 1 |
| TabThreePairOrcaReplays | core.yaml | E7b_analysis.json:b_quench.C3_rvo2.replays | {:d} | 230 | `230` | tables/table3_observed.tex:23 | 4 |
| TabThreePairPubDiffHi | core.yaml | table3_pair.json:pub.diff_ci95.1 | {:.2f} | 0.217391 | `0.22` | sections/08_discussion.tex:14 | 1 |
| TabThreePairPubDiffLo | core.yaml | table3_pair.json:pub.diff_ci95.0 | {:.2f} | -0.152174 | `-0.15` | sections/08_discussion.tex:14 | 1 |
| TabThreePairPubOrcaN | core.yaml | E7b_analysis.json:s3_matched.pub.handedness.orca_n | {:d} | 21 | `21` | tables/table5_bias.tex:15 | 1 |
| TabThreePairPubReplayDis | core.yaml | E7b_analysis.json:b_quench.C3_pub.replay_discordant_snapshots | {:d} | 0 | `0` | tables/table3_observed.tex:24 | 2 |
| TabThreePairRvoHand | core.yaml | E7b_analysis.json:s3_matched.rvo2.handedness.plus_lower_first | {:d} | 8 | `8` | tables/table5_bias.tex:18 | 1 |
| TabThreePairRvoHandN | core.yaml | E7b_analysis.json:s3_matched.rvo2.handedness.plus_n | {:d} | 8 | `8` | tables/table5_bias.tex:18 | 1 |
| TabThreePairRvoOrcaLower | core.yaml | E7b_analysis.json:s3_matched.rvo2.handedness.orca_lower_first | {:d} | 2 | `2` | sections/06_screening.tex:55 | 3 |
| TabThreePairRvoOrcaN | core.yaml | E7b_analysis.json:s3_matched.rvo2.handedness.orca_n | {:d} | 7 | `7` | tables/table5_bias.tex:19 | 1 |
| TabThreePairRvoReplayDis | core.yaml | E7b_analysis.json:b_quench.C3_rvo2.replay_discordant_snapshots | {:d} | 0 | `0` | tables/table3_observed.tex:23 | 2 |
| VelLoneN | velorca.yaml | velorca_analysis.json:lone.vel_rvo2.all.n | {:d} | 360 | `360` | sections/03_pedestrian_model.tex:68 | 3 |
| VelLoneRvoK | velorca.yaml | velorca_analysis.json:lone.vel_rvo2.all.k | {:d} | 0 | `0` | sections/06_screening.tex:58 | 2 |
| VelPairN | velorca.yaml | velorca_analysis.json:pair.vel_rvo2.all.n | {:d} | 276 | `276` | sections/03_pedestrian_model.tex:68 | 2 |
| VelPairRvoK | velorca.yaml | velorca_analysis.json:pair.vel_rvo2.all.k | {:d} | 0 | `0` | sections/06_screening.tex:58 | 1 |
| VelWholeFail | velorca.yaml | velorca_analysis.json:whole.end_state.vel.failures | {:d} | 99 | `99` | sections/06_screening.tex:58 | 1 |
| VelWholeForceK | velorca.yaml | velorca_analysis.json:whole.completion.force.k | {:d} | 54 | `54` | sections/06_screening.tex:58 | 1 |
| VelWholeForcePRel | velorca.yaml | velorca_analysis.json:whole.paired.vel_minus_force.mcnemar_p | p | 2.22045e-16 | `\ensuremath{<10^{-15}}` | sections/06_screening.tex:58 | 1 |
| VelWholeK | velorca.yaml | velorca_analysis.json:whole.completion.vel.k | {:d} | 1 | `1` | sections/06_screening.tex:58 | 1 |
| VelWholeN | velorca.yaml | velorca_analysis.json:whole.completion.vel.n | {:d} | 100 | `100` | sections/06_screening.tex:58 | 1 |
| VelWholeSfmK | velorca.yaml | velorca_analysis.json:whole.completion.sfm.k | {:d} | 1 | `1` | sections/06_screening.tex:58 | 1 |
