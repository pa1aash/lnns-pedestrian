# Numbers audit (worktree W, paper as of 2026-11-10 06:17)

Scope: paper/main.tex, paper/sections/*.tex, paper/tables/*.tex, figures/fig1_caption.tex (plus figures/fig_protocol.tex, figures/fig1_hero.tex, which hold no number macros).
Scripts: `/private/tmp/claude-501/-Users-palaash-Developer-lnns-wt-W/59b080e8-6f12-4028-af21-b8ed89e76e68/scratchpad/numaudit/audit.py` (resolution and recomputation), `render.py` (text with macro values filled in), `used.tsv` (macro, value, file:key, where it is used).
Paper files were only read. Findings are anchored by quoted text because another agent is editing the prose.

**Totals: WRONG 0, IMPRECISE 11, OK-note 9.**

## 1. Macro resolution

- OK. 429 distinct number macros are used in the paper, and every one is defined in paper/numbers.tex. No CamelCase control sequence is undefined; the only CamelCase names not defined in numbers.tex are the LaTeX primitives `\RequirePackage`, `\DeclareRobustCommand` and `\IfFileExists`, plus `\FigOneCaption`, which is defined locally. The registry and numbers.tex match one to one: no registry entry is missing from numbers.tex and no numbers.tex macro is missing from the registry.
- OK. `grep -n "undefined" paper/main.log` finds nothing, so there are no undefined references, citations or control sequences.
- OK-note: main.log (06:17:02) is 5 s older than numbers.tex (06:17:07). All values recompute identically (Sect. 2), but recompile once more before the final check.
- OK-note: four `\pending{...}` items remain. They are not numbers and are listed only so they are not forgotten: velocity-coupling results (Sect. 6.4 and the last row of Table 3), the Zenodo DOI, the acknowledgements and the disclosure of interests. `\finaltrue` will turn each one into a compile error.

## 2. Macro values against data/derived

- OK. All 429 used macros were recomputed from their registry entries (file, key, fmt/sci/p/digits, unit) with tools/make_numbers.py's own `lookup`/`sci`/`pfmt`. **There are 0 mismatches** with numbers.tex.
- OK. final.yaml / final_corrected.json (library "E1b"; derive_final.py filters `mode == "E1b"`) is cross-consistent with the other E1b sources:
  - FinCritN = ChainBlockerN = 196 = 200 − EOneBCompletionK (4).
  - FinCritPosN + FinCritNegN = 194 + 2 = 196, and hessian.n = 194.
  - FinSecondTrapN = 160 = KeystoneBSecondTrap.
  - KeystoneBLone + KeystoneBSecondTrap + KeystoneBCollective = 34 + 160 + 2 = 196.
  - FinPushBoth + FinPushOnly = 31 = EtwoLKFrozenPlusFreed, and FinPushBoth + FinOrcaOnly = 30 = EtwoLKCThreeRVOFreed.
  - FinBarLibN − FinBarGateFail = 60 − 4 = 56 = LoneBarN = EsixBarrierN. None of the 4 gate-failed snapshots (E1b seeds 75, 172, 174, 209) is in the E3 or E4 selection.
  - FinTermRhoMax = 9/(9π) = 0.318, consistent with FinTermNbMax = 9.
- OK. **No used macro pools E1a and E1b, or refers to E1a, the published-reproduction mode, the conference paper or Table 4.** None of these is used anywhere: TermN*, Criterion*, KeystoneA*, EOneA*, second_trap_both_modes, FixAfive*, EtenCPub*, FixAsevenCPub*, EfiveA*, EfiveConfSigmaFifty, FixAsixSigFiftyPub*, Esixp*, Eeight*, Enine*, Eeleven*, TabFour*, or anything sourced from E5a/E6p/E8/E9/E11/table4_conference.json or the E10 `C1_pub` cell. The 82 registry entries of that kind are still defined in numbers.tex but unused. Removing them is optional.
- OK. Every room-bottleneck count in the paper comes from E1b or from runs made only with the corrected update. Checked in two ways:
  - Doc strings: selection.json says the E2/BAR/E3/E4 snapshots are E1b. E5_analysis has `mode: corrected-forward`. E7 uses CF with the E1b default cell. The E7b doc and E6a/E6b are corrected-forward.
  - Raw flags: `w2_numerics: fixed` in data/E2, E3, E4, E6a, E6b, E7b, N1, N2, N3, N5, N6 and in arch_analysis.
  - Mode-independent quantities: fix_a8 (wall-law closed form over the spawns), gmax_curve (geometry) and fix_reg.second_trap_geometry / whole_run_failures (E2 snapshots and E6). The fix_reg.criterion block, which pools n = 393 over E1a and E1b, is not used.
- OK-note: the "Pub" macros that are used all mean the legacy ORCA *solver* inside the corrected model, not the published mode. They are:
  - E2 `C3_pub`: EtwoReplayCThreePub*, EtwoLKDriveVsPubDisc*.
  - E7b `C3_pub` / `constraint_only_pub` / `s3_matched.pub`: PairPub*, PairConsPubFreed, PairBsPub*, PairBstarPub, TabThreePair*Pub*.
  - fix_a1 / fix_a2 `pair.pub`: FixAonePairPubJInd, FixAtwoPairPub*.
  - fix_a4 (published LP solver on E2 corrected runs).
  - table3_pair `pub`.
  
  These are legitimate. The E2 keys called `pooled` (EtwoNAll, EtwoReplay*) pool the two E2 *strata* (lone keystone + second trap), not the two libraries.
- OK-note (fragile, not wrong): "All \FinCritPosN\ blockers with positive margin stayed held" uses the count of positive margins, not the count of held ones. The two are equal now (194 = n_pos_held). Fix: use `\FinCritPosHeld` for the "stayed held" count (it is defined but unused).

## 3. Claims against values

All "all/none/every/of the N", range and interval statements were checked against the values. **None is false.** Specific checks:
- Ranges and maxima:
  - "0.14--0.20 over the first eight deciles": the decile fractions are 0.198, 0.187, 0.173, 0.164, 0.165, 0.140, 0.157, 0.171.
  - "\FixAsevenCSigFlowRatio--\FixAsevenCThreeFlowRatio (0.40--0.59) of the human flow" covers all four cf variants: 0.40, 0.51, 0.57, 0.59.
  - The CroMa ranges hold for all four variants: gaps 11--19 (10.7, 18.7, 13.4, 17.9); longest gap 5.7--6.6 for the three deterministic variants (5.72, 6.60, 6.22); fluctuation 0.094--0.109; long-corridor flow 0.54--0.81; short-corridor flow 0.62--0.91.
  - "0.30--0.33 for independent sets": the third value, 0.32, lies inside.
- Counts that must add up:
  - 17 + 8 = 25, 10 + 15 = 25, 24 + 1 = 25.
  - 35 + 37 = 72, 72 + 50 = 122, 186 − 122 = 64 = "all 64 seeds where both complete".
  - ORCA failures 54 + 31 = 85 = 186 − 101. Noise failures 56 + 31 + 0 = 87 = 186 − 99.
  - The "31 failures ... at rest are all lone keystones" and "51 of its 54 moving failures" agree with the per-row tabulation.
  - Pair: 13/30 = 0.43; 22 + 21 − 13 = 30; RVO2 7 + 8 = 15 with 0 shared; 33 − 28 + 2 = 7.
  - "363 of 368" leaves 5 = "All 5 disagreeing". 66 + 26 = 92. "202 freed runs" = 202 favoured-first.
  - "5 of 300" = 60 × 5 replays. "360 of 360" = 60 × 6 runs. 80 = 4 × 20 runs.
- Every interval contains its estimate and every interval and range is written low before high (30 automatic triples plus the intervals built from differently named macros: σ50, the noise rate, PairFoldLo). The claims "excludes −1", "prediction outside the interval at 2.5" and "shape exceeds 1" hold.
- Singular and plural agree with the values: "1 ... lies", "1 remains", "1 track is lost", "1 gap ... exceeds", "the 2 blockers ... belong".

IMPRECISE:
1. **Sect. 4 (T_eff)**: "The blocker's realised velocity variance is \TthreeRatioMean\ times Eq.~\eqref{eq:teff} in separate runs (median \TthreeCellsMedian\ over the \TthreeCells\ noise settings of the escape experiments)." The 1.00 is the mean over 9 separate runs (range 0.87--1.10), while the median 0.99 is over 207 stored cells, a different set. The parenthesis reads as if it describes the same set. Fix: "... is \TthreeRatioMean\ times Eq. (teff) in 9 separate runs, and a median \TthreeCellsMedian\ times it over the \TthreeCells\ noise settings of the escape experiments."
2. **Sect. 3 Statistics**: "with a profile-likelihood and a seed-resampled bootstrap interval". Sect. 5.2 reports only the seed-cluster bootstrap: "$\sigma_{50}=\EfiveSigmaFifty$ [\FixAsixSigFiftyClLo, \FixAsixSigFiftyClHi]". The profile interval [0.041, 0.047] exists in E5_analysis.logistic_noise_levels.ci95_profile. Fix: either drop "a profile-likelihood and" or add the profile interval.
3. **Sect. 6.1**: "matches that rate (Table~\ref{tab:matched}; interval [\FixAsixLKNoiseCClLo, \FixAsixLKNoiseCClHi])". The interval [0.79, 0.94] is a snapshot-cluster bootstrap of the noise freed fraction (148/170 = 0.87). It is not in Table 3, so the sentence leaves open whose interval it is. Fix: "(\EtwoLKNoiseCFreed/\EtwoLKNoiseCN\ runs, snapshot-cluster interval [..]; ORCA \EtwoLKCThreeRVOFreed/\EtwoLKCThreeRVON)".
4. **Sect. 6.3**: "the two signs free different standoffs (discordant \PairBsPubRevA:\PairBsPubRevB)". The data's order is a = −b*, b = +b*: 13 freed by −b* only, 14 by +b* only. Elsewhere the convention is first-named:second-named. Fix: "(discordant \PairBsPubRevA:\PairBsPubRevB, $-b^\ast$ only : $+b^\ast$ only)".
5. **Sect. 7**: "Every participant passes the entrance in every run (\EtenHumanUnpassed\ track is lost before it)." The lost track cannot be shown to pass. Fix: "Every tracked participant passes the entrance (\EtenHumanUnpassed\ track is lost before it)."

## 4. Removed results

- OK. There are no conference numbers, Table 4, `tab:conf` references, open counterflow/crossing/throat-overlap runs or published-reproduction mode anywhere in the sections, tables or captions. The only table labels and references are tab:params, tab:signatures and tab:matched.
- OK-note: Sect. 1 still cites the earlier paper: "Our earlier work tested such a credit at the level of rates ... \cite{gang2026}; the present work supersedes that reading." It quotes no number from it, which is fine.
- OK-note: "Only the legacy linear-program solver changes outcome under $10^{-9}$\,m replays, in \EtwoReplayCThreePubFlips\ of \EtwoReplayN". The legacy constraint-only arm also flips 5/300. That is the same solver, so the sentence holds.

## 5. Precision consistency

IMPRECISE:
6. **The same quantity is quoted with different values.**
   - Sect. 1: "contact arches break within \RunNFiveFineLifeMax\,s" (3.3 s, the Δt = 0.0025 s cell).
   - Sect. 5.4: "break within \ArchMaxLife\,s" (2.9 s, Δt = 0.01 s) and "none outlasts \RunNFiveFineLifeMax\,s".
   
   Both are true, but the intro headline differs from the main-text "break within". Fix: in Sect. 1, "break within \ArchMaxLife\,s (\RunNFiveFineLifeMax\,s at $\Delta t=0.0025$\,s)", or say "within a few seconds".
7. **Sect. 7**: "The longest gap between passages averages \EtenHumanGap\,s (at most \EtenHumanGapMax\,s)" prints 1.7 against 2.04. Fix: set EtenHumanGap to `{:.2f}` (1.71) or EtenHumanGapMax to `{:.1f}` (2.0). Keep 2.04 if the point is "> 2 s", and then make the mean 1.71.
8. **Sect. 5.3**: "pair barriers of \PairBarMin--\PairBarMax\,J (median \PairBarMed\,J)" prints 0.06--1.1 (0.21), mixing 2 dp and 1 dp. Fix: PairBarMax `{:.2f}` (1.11).
9. **Sect. 6.3 against Table 3, sign style.** The text writes "[\FixAtwoPairPubDeltaLo, \FixAtwoPairPubDeltaHi]" = [−0.35, +0.35] with an explicit +. The Table writes "$\TabThreePairPubDiff$ [$\TabThreePairPubDiffLo$, $\TabThreePairPubDiffHi$]" = +0.02 [−0.15, 0.22] with no + on the upper bound, and the lone and whole-run rows print −0.01 [−0.10, 0.08]. Fix: one convention, either `{:+.2f}` for all Δ bounds in both places or drop the + everywhere.
10. **Sect. 5.3 / Table 3 (b values).** "$b_f=\PairBstarMin$--\PairBstarMax\ (median \PairBstarMed)" prints 3 dp (0.001--0.038, 0.016), while Table 3 prints $b^\ast_{\rm legacy}=0.0223$ and $b^\ast_{\rm RVO2}=0.0091$ at 4 dp. Fix: b* at `{:.3f}` (0.022, 0.009), or the b_f range at 4 dp.
11. **Sect. 5.2**: "\EfourWeibAlone\ [\EfourWeibAloneLo, \EfourWeibAloneHi]" prints 1.07 [1.002, 1.15], mixed precision inside one interval. The 3 dp is needed to show the bound exceeds 1 (at 2 dp it would read 1.00 and contradict "exceeds 1"). Fix: keep it, or print this interval at 3 dp throughout (1.073 [1.002, 1.149]).

OK-note:
- The Table 3 $t_{1/2}$ column mixes 19.8, 1.5, 469 and 132. The precisions differ but each suits its magnitude.
- The same quantity from two sources agrees where it is printed twice:
  - Whole-run J: EsixJaccard 0.41 [0.32, 0.50] = RunNTwoJOrcaOld 0.41.
  - Independence J: FixAoneWholeJInd = RunNTwoJOrcaOldIndep = 0.30.
  - σ50 = 0.044 in both sources.
  - The μ1 range 65--121 equals RunNSixMuLoss 65--121.
  - \EfourRatioFull\ is printed twice as 1.15.
- Hard-coded counts in Sect. 7 ("deadlocks in \EtenCOneDeadlock\ of 25 runs", "(25 per variant)") and Sect. 8 ("100 per room run") are correct (E10 n = 25 per cell; 100 agents). They could be macros for robustness.
