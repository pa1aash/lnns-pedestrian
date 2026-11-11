# P audit: numbers

Scope: paper/sections/*.tex, paper/tables/*.tex, figures/fig1_caption.tex, figures/fig_protocol.tex (as input by paper/main.tex).
Method: `tools/make_numbers.py` was rerun into a scratch file, and the output was identical to paper/numbers.tex (3401 macros). Every macro used in the text was re-read from its data/derived JSON key through the registry spec and re-formatted, and each rendered value was checked against the claim sentence that uses it. Supersessions were checked against reports/C_REPORT.md, experiments/revision/notes/*.md and notes/D_changes.md, and figure-only numbers against reports/F_REPORT.md.

**Summary: 470 macro names checked (incl. Rel/Unit variants); 0 undefined; 0 value mismatches against the JSON; 0 superseded macros or claims in use; 58 flagged rows (2 WRONG, 7 UNSUPPORTED, 4 LITERAL, 45 IMPRECISE) in the findings table, plus 1 IMPRECISE figure row.**

Supersession status (all clean):
- Esevenwcrit, FixAeightWfiftyPred, ArchPeakForce, ArchEpisodes, ArchPNinetyFive and ArchEvacMedian: not used. RevBtwo* and RevBfour* are used instead.
- The A4 alone trend is gone, and Sect. 5.2 and the abstract use B3 (RevBthreeAll*).
- Table 3a's lone J is the 20-seed A9 value (RevAnineLKNHalfJ = 0.75).
- The old E10, FixAseven and RevAtwelve macros (all listed as changed in D_changes.md) do not appear. Eten* is used only for the macros D_changes.md lists as unchanged (EtenHuman*, EtenLongHumanFlow).
- No "never deadlocks" claim.
- "SFM ... free none" is scoped to the 60-snapshot screen (06:16). The 160 second traps get RevAfiveXPoolSFMFreed = 2 (06:24).
- "5 of 300" is scoped "on the screen", next to 13/800 on the 160 (06:26).
- At sigma = 0.07, 36/56 barriers have beta < 1 (05:45). The sigma* count of 23/56 is used at 06:31.
- C_REPORT A3 itself still says "23 of 56" at sigma = 0.07. The report is wrong, not the paper.

## Findings

| file:line | macro or literal | rendered | source value | verdict | fix |
|---|---|---|---|---|---|
| sections/03_pedestrian_model.tex:40 | RevAtwoRunsWMin ("at least") | 0.958 | 0.95768 (rev_A2 runs.w_min) | WRONG | Rounding up breaks the lower bound (0.95768 < 0.958). Use 0.957 (floor) or 0.96 with "about"; better, 1 − w ≤ 0.043. |
| sections/05_deadlock_physics.tex:16 | FinTermWeidMin ("v_eff/v0 ≥") | 0.997 | 0.99650 (final_corrected terminal.weidmann_min) | WRONG | Rounding up breaks the "≥" bound. Use 0.996 (floor), or "> 0.99". |
| sections/05_deadlock_physics.tex:52 | PairBstarMin | 0.001 | 0.000508 | IMPRECISE | The {:.3f} format doubles the value. Use sci/2 sf: 0.00051 (5.1×10⁻⁴). |
| sections/04_protocol.tex:13 | RevAeightSTRvoLatest ("Quenches run to T = 120 s ... force-coupled ORCA reaches its final outcome within 14 s") | 14 | 13.99 s, key snapshots.lone_keystone_second_trap only (lone keystones 6.95 s) | UNSUPPORTED | False for pair quenches: every held standoff under ORCA still moves at 120 s (06:42, 39/39 and 25/25). Scope it: "at the lone trap within 14 s". |
| tables/table3a_noise.tex:4 | caption "Per-step noise fraction-matched to force-coupled ORCA (RVO2)" | – | second-trap row Δ = +0.25 [0.085, 0.44] (rev_A6) | UNSUPPORTED | The second-trap row is not fraction-matched (A6; the text at 06:24 says so). The caption should say "fraction-matched at the lone keystones and in whole runs; at the second trap σ = 0.07 m/s is not matched (Δ excludes 0)". |
| tables/table2_signatures.tex:25 | "matched at 120 s" (Noise σ = 0.07, observed cells "report the lone traps") | – | matched at lone keystones (TabThreeLKDiff CI covers 0); not at second traps (RevAsixSTDiff +0.25 [0.085, 0.44]) | UNSUPPORTED | Lone traps include second traps (glossary). Write "matched at 120 s (lone keystones)". |
| sections/06_screening.tex:8 | Fig. quench caption "open, second traps" | – | arms exist for E2's 26 of 160 second traps only (F_REPORT Fig. 7, R5) | UNSUPPORTED | Scope it: "open, the screen's 26 second traps". |
| sections/07_experiments.tex:21 | RevDThreeCThreeOpenMean ("stalls in 14 (mean 446 s without passage at the end)") | 446 | 445.76, n = 15 (14 capped + 1 deadlock; rev_D D3.rerun.per_variant.C3_rvo2_cf.final_open_to_600.n) | UNSUPPORTED | The mean is over the 15 censored runs, not the 14 stalls. Say "(mean 446 s without passage at the end over its 15 censored runs)" or recompute over the 14 capped runs. |
| sections/06_screening.tex:24 | StHeldCancel ("cancels on average 0.27 of the drive") | 0.27 | 0.2688, key cancel_frac_mean.median (median over snapshots of per-snapshot means) | UNSUPPORTED | Wording: "cancels a median 0.27 of the drive". |
| tables/table3b_bias.tex:18 | TabThreePairRvoDiffLo | −0.13 | −0.1304 (table3_pair.json, PCG64(12345)); rev_A8 pair.delta.bstar_rvo2_plus_vs_C3_rvo2.T120.ci95.0 = −0.1522 (−0.15) | UNSUPPORTED | Two 95% bootstraps of the same paired difference disagree by one snapshot (1/46). Use one source for Table 3b and A8. The legacy row agrees (−0.15, 0.22). |
| sections/05_deadlock_physics.tex:39 | literal "about 0.9 of the computed one" | 0.9 | B3 ratios 0.86–0.93 | LITERAL | Use \RevBthreeAllDeep--\RevBthreeAllMid, as in the abstract. |
| sections/07_experiments.tex:23 | literal "Each of the 100 model runs has a lower flow than its human run" | 100 | supported: max model run flow 0.995 (C3_rvo2_cf.flow.max) < min human run 1.154 (EtenHumanFlowMin) | LITERAL | Add a registry macro for the maximum model run flow (rev_D D3.rerun.per_variant.*.flow.max) and cite it. 100 = 4×25 is a design count. |
| sections/05_deadlock_physics.tex:57 | literal "every run completes" | – | rev_B4 by_dt.dt0p001.complete = 10, dt0p0025 = 10 | LITERAL | Use \RevBfourCompleteFine\ of \RevBfourN. |
| sections/06_screening.tex:51 | literal "no replay changes an outcome" | – | velorca replay_disagree_total = 0 | LITERAL | Use \VelLoneReplayDis\ and \VelPairReplayDis\ (defined, unused). |
| sections/05_deadlock_physics.tex:18 | RevBonePosMarginMin | 0.008 | 0.008080 | IMPRECISE | Use 2 sf: 0.0081. |
| sections/05_deadlock_physics.tex:18 | RevBoneNegMarginMax ("to −0.007") | −0.007 | −0.006894 | IMPRECISE | Use 2 sf: −0.0069. The rendered bound overstates the margin. |
| sections/05_deadlock_physics.tex:43 | EfourSkippedDU | 0.02 | 0.02091 | IMPRECISE | 0.021 |
| sections/05_deadlock_physics.tex:52 | PairFoldMissGap ("at most 2%") | 2 | 1.727 | IMPRECISE | 1.7 |
| sections/05_deadlock_physics.tex:54 | PairBarMin | 0.06 | 0.05709 | IMPRECISE | 0.057 |
| sections/05_deadlock_physics.tex:57 | RunNFiveVThreeLifeMax | 0.1 | 0.09999 | IMPRECISE | 0.10 |
| sections/05_deadlock_physics.tex:57 | RevBfourBodyMid ("at most 18 kN") | 18 | 18.14 | IMPRECISE | As an upper bound use 19 (ceil) or 18.1. |
| sections/05_deadlock_physics.tex:57 | RevBfourContactMid (maximum) | 4.8 | 4.819 | IMPRECISE | Minor: as a maximum, 4.9 (ceil) or 4.82. |
| sections/06_screening.tex:26 | RevAthirteenCreepSpeedMin | 0.09 | 0.091 | IMPRECISE | 0.091 |
| sections/06_screening.tex:26 | EtwoReplayCThreePubMaxDt | 80.8 | 80.77 | IMPRECISE | 3 sf; use 81. |
| sections/06_screening.tex:31 | EsixStallMaxDiff | 0.05 | 0.04509 | IMPRECISE | 0.045 |
| sections/06_screening.tex:45 | RevAelevenJacAsymMin | 0.08 | 0.07702 | IMPRECISE | 0.077 |
| sections/06_screening.tex:45 | RevAelevenRatioMin | 0.19 | 0.1861 | IMPRECISE | Minor: the range lower end is rounded up; 0.18 (floor) or 0.186. |
| sections/05_deadlock_physics.tex:16 | EOneBStuckAloneFrac | 0.234 | 0.2343 | IMPRECISE | 3 sf; use 0.23. |
| sections/05_deadlock_physics.tex:41 | EfourRatioFull | 1.15 | 1.1507 | IMPRECISE | 3 sf next to 0.95 and 0.87; use 1.2. |
| sections/04_protocol.tex:32 | RevAtenMuMax | 1115 | 1115.4 | IMPRECISE | 4 sf; use 1100 (or 1.1×10³). |
| sections/04_protocol.tex:41 | TthreeRatioMean | 1.00 | 1.0027 | IMPRECISE | 3 sf; use 1.0. |
| sections/03_pedestrian_model.tex:40 | RevAtwoLoneWMin | 0.9994 | 0.99941 | IMPRECISE | 4 sf; state 1 − w ≤ 6×10⁻⁴ (2 sf of the deviation). |
| sections/01_introduction.tex:28; 05_deadlock_physics.tex:20; 09_conclusions.tex:2 | RevBtwoWfifty [Lo, Hi] | 0.878 [0.874, 0.883] | 0.8782 [0.8739, 0.8826] | IMPRECISE | 3 sf are needed to resolve the CI. Either keep it and state the exception in Sect. 4.4 ("widths to 1 mm"), or give 0.88 m with CI ±0.005. |
| tables/table2_signatures.tex:25; tables/table3a_noise.tex:12 | EthreeEllBA (EthreeEllBAPred) | 2.16 (2.22) | 2.1638 (2.2162) | IMPRECISE | 3 sf; use 2.2 (2.2). |
| tables/table3a_noise.tex:12 | TabThreeLKDiff, TabThreeLKDiffHi | −0.01, 0.08 | −0.01176, 0.08235 | IMPRECISE | −0.012 [−0.10, 0.082] |
| tables/table3a_noise.tex:14 | RunNOneDiff, RunNOneDiffLo, RunNOneDiffHi | −0.02 [−0.07, 0.04] | −0.01765 [−0.07353, 0.04412] | IMPRECISE | −0.018 [−0.074, 0.044] |
| tables/table3a_noise.tex:14 | RevAnineLKNHalfEJ | 0.06 | 0.06100 | IMPRECISE | 0.061 |
| tables/table3a_noise.tex:16 | EthreeCThreeLnRatioFix | −0.005 | −0.004804 | IMPRECISE | −0.0048 |
| tables/table3a_noise.tex:19 | RevAsixSTDiffLo | 0.08 | 0.08462 | IMPRECISE | 0.085 |
| tables/table3a_noise.tex:24 | EsixDiff, EsixDiffHi | −0.01, 0.08 | −0.01075, 0.07850 | IMPRECISE | −0.011 [−0.10, 0.078] |
| tables/table3a_noise.tex:12,14,19,24 | RevAseven*TimeEff/Lo/Hi (ΔRMST) | 19.3 [9.1, 29.1]; 19.4 [11.2, 27.3]; −16.0 [−35.8, 3.1]; 71.9 [33.2, 110.1] | as rendered (0.1 s) | IMPRECISE | Use 2 sf: 19 [9.1, 29]; 19 [11, 27]; −16 [−36, 3.1]; 72 [33, 110]. |
| tables/table3b_bias.tex:13,18 | RevAsevenPair*TimeEff/Lo/Hi | −2.1 [−21.2, 17.5]; −1.3 [−20.2, 18.1] | as rendered | IMPRECISE | −2.1 [−21, 18]; −1.3 [−20, 18] |
| tables/table3a_noise.tex:20 | RevAsevenSecondTimePHolm, RevAsevenSecondReplayPHolm | 0.12, 0.12 | 0.125 exactly | IMPRECISE | Python half-even rounding; conventional 2 sf is 0.13. Change pfmt to Decimal ROUND_HALF_UP. |
| tables/table3b_bias.tex:13 | PairBstarPub | 0.0223 | 0.022344 | IMPRECISE | 3 sf; use 0.022 (RVO2 row already 0.0091). |
| tables/table3b_bias.tex:13 | TabThreePairPubDiff | +0.02 | 0.02174 | IMPRECISE | +0.022 (rev_A8 delta_disp also gives 0.022) |
| tables/table3b_bias.tex:18 | TabThreePairRvoDiff | +0.02 | 0.02174 | IMPRECISE | +0.022 |
| tables/table3b_bias.tex:18 | RevAninePairRvoEJ | 0.09 | 0.09357 | IMPRECISE | 0.094 |
| sections/07_experiments.tex:19 | RevDHumanFlow [Lo, Hi]; EtenHumanFlowMin–Max; EtenHumanGapMax | 1.47 [1.21, 1.73]; 1.15–1.71; 2.04 | as rendered | IMPRECISE | 3 sf; use 1.5 [1.2, 1.7]; 1.2–1.7; 2.0 (or declare flows to 0.01 ped/s). |
| sections/07_experiments.tex:23 | RevDHumanWindowFlow, EtenLongHumanFlow, RevDShortHumanFlow | 1.48, 1.32, 1.57 | as rendered | IMPRECISE | 1.5, 1.3, 1.6 (model flows are already 2 sf) |
| sections/07_experiments.tex:25 | RevDThreeCThreeGapsTwo–RevDThreeCSigGapsTwo | 10.1–18.2 | 10.12–18.16 (min ORCA, max noise; SFM 18.12) | IMPRECISE | Use 10–18. The order is right (D_changes labels the max "SFM"; the noise value 18.16 is the true max). |
| sections/07_experiments.tex:25 | RevDThreeCOneGapCompleteMax, RevDThreeCEdgeGapCompleteMax, RevDThreeCSigGapCompleteMax ("at most") | 20.4, 15.6, 237.2 | 20.36, 15.60, 237.16 | IMPRECISE | 2 sf with upward rounding for the bound: 21, 16, 240. Use 7.6 as is. |
| sections/07_experiments.tex:25 | RevDThreeCSigGapKMMedian | 95.9 | 95.92 | IMPRECISE | 96 |
| sections/07_experiments.tex:25 | RevDThreeCOneGapLowerMedian, RevDThreeCThreeGapLowerMedian ("at least") | 416, 432 | 415.92, 431.80 | IMPRECISE | Rounding up breaks "at least". Use floor (415, 431) or 2 sf floor (410, 430). |
| sections/07_experiments.tex:25 | RevDThreeCOneFluct–RevDThreeCSigFluct | 0.092–0.108 | 0.0924–0.1079 (min SFM, max noise; edge 0.094, ORCA 0.100) | IMPRECISE | The order is right; use 0.092–0.11. |
| sections/05_deadlock_physics.tex:16 | DriveCOneMedian, DriveORCAMedian, RevAthirteenGmaxMeanR | 214, 215, 156 | 214.45, 214.63, 156.0 | IMPRECISE | Integer rendering keeps 3 sf; at 2 sf both drives are 210 N. "214 vs 215" is a rounding split of 0.2 N. Use 2 sf or say "both medians 214 N". |
| sections/05_deadlock_physics.tex:12 | RevAthirteenGmaxThirty, GmaxThirtyFive | 291, 543 | 291.0, 543.26 | IMPRECISE | Low: 290, 540 under the 2-sf rule (or exempt force-law values, which are not statistics). |
| sections/06_screening.tex:29; 04_protocol.tex:13 | EsixCThreeMaxT, RevAeightWholeRvoLatest ("by 161 s") | 161 | 160.97 | IMPRECISE | Low: a 3-digit integer bound is fine as a bound. Exempt it, or use 170 under 2 sf. |
| sections/05_deadlock_physics.tex:50,52 | PairLamOneMax, RunNSixMuLossMax | 121 | 121.0, 120.98 | IMPRECISE | Low: 120 under 2 sf. The ranges coincide after rounding (65–121), as the text implies. |

Claims checked and found consistent (not flagged):
- Brackets: 0.75 < w50 < 0.92 (RevBtwoWlo 0.754, Whi 0.920).
- Prediction offset: 0.919 − 0.878 = 0.041.
- 194 + 2 = 196; 34 + 160 = 194.
- 30/34, 24/26, discordant 0:0.
- 149 − 121 = 28 drive/ORCA discordant.
- 2 of 160 SFM; 13/800 legacy, 0/800 RVO2.
- 64 of 64 paired faster.
- Failures: ORCA 31 + 54 = 85 (186 − 101); noise 56 + 31 + 0 = 87 (186 − 99), stationary 0.
- 39/39 and 25/25 still moving.
- Reversal discordant 13:14: a = −b* (21 freed), b = +b* (22 freed), both = 8.
- RVO2 −b* upper first 5/5.
- Velocity filter 0/360, 0/276 with both solvers.
- Gate at every snapshot ≥ 0.9994: pair min is 0.99964.
- Hessian strict 60/60.
- Arch persistence 0/10 at both fine Δt, Wilson hi 0.28.
- CroMa censored 23/4/15/7, flow ratios 0.40–0.60, model flows < human.
- p-values follow the stated rule (2 sf ≥ 10⁻³, "<10^{-k}" with k = floor(−log10 p)), apart from the 0.125 rounding above.

Other literal numbers were checked and are model parameters, design constants or definitions, so they are not flagged: 0.8 m, 0.08/0.04 m, 100 agents, 120/600/300/900 s, 10⁻⁹ m, five/20 seeds, σ = 0.07/0.01 m/s, β = 1.5–7, 11 widths 0.70–1.00 m, r = 0.20–0.35 m, 25 runs, 2 s, 0.74 m, 0.3 m/s, 0.1 J floor, 3 and 2 m/s, the 5 N / 1% gate, the Fig. 1 colour scales.

## Figure-only numbers and figure–registry conflicts (F_REPORT.md)

| figure (file) | figure-only number | text / registry | verdict | fix |
|---|---|---|---|---|
| Fig. pair (06_screening.tex:37, fig7_pair.pdf) | noise σ = 0.02–0.05: 230/230 freed | 05_deadlock_physics.tex:54 PairNoiseLowFreed/N = 224/230 at σ = 0.01 (E7b b_quench.noise0p01) | no conflict | The two count different arms: runs of 46 snapshots × 5 seeds at σ = 0.01 against σ = 0.02–0.05 (E7b noise0p02/0p03/0p05 freed = 230). The σ = 0.01 arm is not drawn. Either add "and all 230 at σ = 0.02–0.05 (Fig. pair)" with registry macros for b_quench.noise0p02..0p05.freed, or draw σ = 0.01. |
| Fig. pair | ORCA 21/46 = 0.457, 7/46 = 0.152; push − 1/46; −b* RVO2 5/46; push + 34/46 | PairPubFreed 21, PairRvoFreed 7, PairFrozenMinusFreed 1, PscrPairBsRvoMinusFreed 5, PairFrozenPlusFreed 34 | OK | – |
| Fig. quench (fig6_quench.pdf) | second traps: legacy 22/26, noise σ = 0.07 0.90 [0.82, 0.98], push + 25/26; keystones σ = 0.03 0.41, σ = 0.05 0.69, push + 0.91 | 117/130 = 0.90 (RevAsixSTNoiseFreed/N) matches | OK (scope) | The open markers are E2's 26 of 160 (see the caption row above). The sigma 0.03/0.05 rates are figure-only. |
| Fig. width (fig3_width_walls.pdf) | completions 0, 2, 6, 15, 42, 52, 70, 82, 93, 96, 100 of 100; band ±0.045 at w50; 10–90% width 0.105 m; bracket 0.754–0.920 | RevBtwoNRuns 1100, 11 widths; RevBtwoWlo/Whi 0.75/0.92 | OK | The pointwise band is not the CI of w50 (the text gives the bootstrap CI 0.874–0.883), as the F report requires. |
| Fig. escape (fig_escape_dt.pdf) | B3 ΔU 5.8, 20.8, 56.3 J; ratios 0.91/0.93/0.86 with CIs; ln(λ/ν) −4.4 to −6.7 at β = 5–7; 14–19 escapes of 20 | RevBthreeDU* 5.8, 21, 56; RevBthreeAll* match | OK | Text 05:39 "about 0.9" should become a macro range (above). |
| Fig. lone trap (fig2_lone_trap.pdf) | 2000-agent cloud; 5th–95th percentile drive bands and medians | text: StuckAloneN = 20000 spawned agents | IMPRECISE | The caption says "spawned agents" and the panel shows a 2000 subsample. Write "2000 of the 20000 spawned agents". |
| Fig. CroMa (fig8_croma.pdf) | fluctuation means 0.092, 0.094, 0.100, 0.108 (humans 0.074); jamb-range flow 0.83 [0.81, 0.85]; noise flow 0.59 [0.52, 0.66]; censored lower bounds 404–465, 430–451, 416–472, 2.4–446 s; human longest gaps 1.4–2.04 s | RevDThreeCOneFluct–CSigFluct 0.092–0.108; ratios 0.56 = 0.83/1.47 and 0.40 = 0.59/1.47; human gap max 2.04 | OK | The ORCA censored-gap range 416–472 s is the n = 15 set behind RevDThreeCThreeOpenMean, so the text should say 15 runs (row above). |
| Fig. 1 (fig1_hero) | k_BT_eff = 10.22 J; lone barrier 21.27 J at 9.940 m; minimum 9.659 m; pair maximum 0.405 J at 0.094 m | none | OK | Figure-only; no registry counterpart. |
| Fig. geometry (fig_geometry.pdf) | waiting zone 0.3–2.5 m, \|y − 5\| < 2 m; 7.8 × 8.6 m holding area | 07:16 cites the zone by letter only | OK | – |
