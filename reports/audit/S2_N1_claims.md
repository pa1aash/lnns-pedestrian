# S2 / N1: Claims and numbers audit

Snapshot: `reports/audit/snapshot/main.tex` (1353 lines), commit `decbdca`. Every line number below is a `main.tex` line; the section source file and its line follow in brackets. Read-only audit: nothing in the repository was edited.

## 0. Summary

- **Number chain.** `tools/make_numbers.py` was re-run against `paper/registry/*.yaml` and `data/derived/*.json` into a scratch file. The 629 regenerated macros are byte-identical to `paper/numbers.tex` and to the inlined block at `main.tex` 22-650. So every macro value is mechanically traceable to a JSON field, and every JSON file has a generating script (Section 6, script map). 376 of the 629 macros are used in the body, tables and captions; 253 are unused.
- **Trace table (Section 7):** 376 macro rows and 47 hard-coded rows, 423 in all.
  - VERIFIED: 414.
  - MISMATCH: 7. The printed value or its wording disagrees with the data, or the value is attached to the wrong population or row.
  - UNTRACEABLE: 2. No stored derived value backs the number.
- **Recomputation (Section 5):** 57 values were recomputed by hand from `data/derived/*.json`: Wilson 95% intervals, exact McNemar, two-sided Fisher, Jaccard, Student-t means and intervals, flow ratios, medians, the inversion for σ*, the Weidmann factor and the force balance of Fig. 1. All 57 agree with the printed values at the printed precision. The disagreements found are of meaning (what the number is said to be), not of arithmetic.
- **Defects (Section 1):** 1 HIGH, 11 MEDIUM, 24 LOW.

## 1. Ranked defects

### HIGH

**H1. Table 3: the ℓ value in the lone-trap noise row was not measured for that row.**
- Where: main.tex 1095, the ℓ cell of the row "C1 + noise σ=0.07". Caption at 1087. Source: `paper/tables/table3_matched.tex:11`, written by `experiments/tables/make_table3.py`.
- Quote: `C1 + noise $\sigma=0.07$ & ... & \EthreeEllBA{} (\EthreeEllBAPred{})`, which renders as "2.16 (2.22)". The row "C3 RVO2" carries `$\EthreeCThreeLnRatio{}$` (−4.8×10⁻³).
- Evidence:
  - `E3_analysis.json:headline.ell_ps_b1p5_obs` comes from E3. That set is 20 snapshots spread over the collective barrier, and its per-step noise is set per snapshot so that β_ref = ΔU/k_BT_eff = 1.5 (main.tex 1117; CHANGELOG C15; `experiments/E3/analyze.py` docstring).
  - The σ = 0.07 m/s arm of the row header was run only in E2, on the 34 lone keystones at Δt = 0.01 s. It was never run at Δt = 0.005 or 0.02 s.
  - The C3 RVO2 ℓ is likewise taken over the 20 E3 snapshots (16 freed), not the 34 lone keystones of the block header ("Lone-trap snapshots (E2): 34 lone keystones").
  - So the thesis table pairs a signature with a control and a snapshot set it was not measured on.
- Fix, caption at 1087: replace "and $\ell=\ln\hat\lambda(0.005)/\hat\lambda(0.02)$ with its Arrhenius prediction (E3)" with "and $\ell=\ln\hat\lambda(0.005)/\hat\lambda(0.02)$ with its Arrhenius prediction, measured in E3 on 20 lone-trap snapshots with per-step noise set to $\Delta U/k_BT_{\rm eff}=1.5$ at $\Delta t=0.01$\,s, not at $\sigma=0.07$\,m/s".
- Better: show ℓ in its own row of the block, "per-step noise, E3 (20 snapshots)", and leave "---" in the σ = 0.07 row.

### MEDIUM

**M1. "in all 10 one-neighbour snapshots" the neighbour sits abreast of the blocker across the axis. That holds for 9 of the 10.**
- Where: main.tex 1120 [`sections/06_attribution.tex:28`].
- Quote: "The cause is a trapped neighbour abreast of the blocker across the axis, \CtwsixGapMin--\CtwsixGapMax\,m away surface to surface in all \CtwsixN\ one-neighbour snapshots: the pair geometry of Sect.~\ref{sec:pair}."
- Evidence: `E7b_analysis.json:e_c26.second_trap_one_neighbour.geometry`.
  - In E1b_seed103 the blocker is 0.017 m from the axis, and the neighbour is 0.735 m from it and 0.30 m behind (dx = −0.300 m).
  - That is not the pair geometry of §5.2, where members stand 0.40-0.50 m from the axis. The same snapshot gives the minimum constraint cancellation of 0.0 (`cancel_frac_mean.min`).
  - In the other 9 snapshots the blocker is 0.40-0.44 m from the axis and the neighbour 0.44-0.52 m, on opposite sides.
- Fix: "The cause is a trapped neighbour across the axis, \CtwsixGapMin--\CtwsixGapMax\,m away surface to surface; in 9 of the \CtwsixN\ one-neighbour snapshots the two stand abreast, 0.40--0.52\,m from the axis on either side, the pair geometry of Sect.~\ref{sec:pair} (in the tenth the blocker is on the axis and its neighbour 0.30\,m behind)." Add registry macros for 9 and 0.40-0.52 rather than hard-coding them.

**M2. Rest-field residual stated as an upper bound that the data exceed.**
- Where: main.tex 1001 [`sections/04_signatures.tex:25`], and the same value at 1049 [`sections/05_deadlock_physics.tex:31`].
- Quote (1001): "in the code $\max|\mathbf F_0+\nabla U|\le\ResidCollMax$\,N over the \ResidBarN\ barrier and $\ResidPairMax$\,N over the \ResidPairN\ pair snapshots". This renders as "≤ 5×10⁻⁷ N ... and 1×10⁻⁷ N".
- Evidence:
  - `field_residuals.json:pair.max_N` = 1.39×10⁻⁷ N, which is above the printed bound of 1×10⁻⁷. The registry uses `fmt: sci, digits: 1`, which rounds the bound down.
  - `collective.max_N` = 4.90×10⁻⁷ N is correctly ≤ 5×10⁻⁷.
  - CHANGELOG C38 also says "1e-7 N" for the pair snapshots.
- Fix: set `digits: 2` for `ResidPairMax`, `ResidCollMax` (`paper/registry/core.yaml:1203` area) and `PairResidMax` (`paper/registry/pair.yaml:10`). The text then reads "≤ 4.9×10⁻⁷ N ... and 1.4×10⁻⁷ N", and at 1049 "largest residual 1.4×10⁻⁷ N". Update the C38 wording.

**M3. "never exceeds 2.0 s" alongside a gap longer than 2 s in the same sentence.**
- Where: main.tex 1154 [`sections/07_validity.tex:13`].
- Quote: "the longest gap between passages averages \EtenHumanGap\,s and never exceeds \EtenHumanGapMax\,s, and a run has on average \EtenHumanGapsTwo\ gaps longer than 2\,s". This renders as "averages 1.7 s and never exceeds 2.0 s, and a run has on average 0.2 gaps longer than 2 s".
- Evidence: `E10_analysis.json:humans.longest_gap_max` = 2.04 s (run 4D120, which also has the single gap over 2 s). The sentence contradicts itself as printed.
- Fix: registry `EtenHumanGapMax` → `fmt: "{:.2f}"`. Text: "the longest gap between passages averages \EtenHumanGap\,s and is at most \EtenHumanGapMax\,s, and only one gap in the five runs exceeds 2\,s".

**M4. Pair barriers "far below the lone-trap barriers".**
- Where: main.tex 1053 [`sections/05_deadlock_physics.tex:35`].
- Quote: "gives gated pair barriers of \PairBarMin--\PairBarMax\,J (median \PairBarMed\,J), far below the lone-trap barriers".
- Evidence:
  - The gated lone-trap library barriers (`E6_analysis.json:lifetimes.barrier_picture.rows`, n = 56) run from 0.021 to 56.9 J, with median 6.4 J.
  - 9 of the 56 are at or below the largest pair barrier (1.1 J): seeds 60, 223, 103, 170, 178, 111, 112, 61 and 100.
  - Two of those (seeds 103 and 111) are themselves one-neighbour second-trap snapshots of the pair-like geometry.
  - The statement holds for the E3 set (≥ 3 J by construction), not for "the lone-trap barriers" in general.
- Fix: "gives gated pair barriers of \PairBarMin--\PairBarMax\,J (median \PairBarMed\,J), well below the typical lone-trap barrier (median 6.4\,J over the 56 gated library barriers; 3\,J and above in the time-step test of Sect.~\ref{sec:att-lone})". Add a registry macro for 6.4 (`E6_analysis.json:lifetimes.barrier_picture.dU_median`).

**M5. "ORCA acts through its constraint part" at the pair is not what the decomposition shows.**
- Where:
  - 1133, paragraph heading [`sections/06_attribution.tex:41`];
  - 836, intro [`sections/01_introduction.tex:20`];
  - 1177, conclusions [`sections/09_conclusions.tex:3`].
- Quotes:
  - "ORCA acts through its constraint part, per solver."
  - "At the pair class ORCA acts through its constraint part, differently in the two solvers"
  - "acts through its constraint part, solver by solver, at the pair".
- Evidence: `E7b_analysis.json:b_quench` and `c_decomposition`.
  - Constraint part alone frees 45 (published) and 44 (RVO2). Drive alone frees 33. Full ORCA frees 21 (published) and 7 (RVO2).
  - Full RVO2 ORCA frees fewer than either part (28:2 against the drive). The text itself says "the parts oppose each other".
  - What the data show: at the pair the constraint part is active (it is inert at the lone trap) and acts against the drive, and the net outcome depends on the solver. They do not show that ORCA's resolutions come through the constraint part.
- Fix:
  - Heading: "ORCA's constraint part acts, against its drive, and the solver decides."
  - Intro: "At the pair class ORCA's constraint part, inert at the lone trap, acts against its drive, with outcomes that differ between the two solvers, and a lateral bias matched to its rate frees partly different standoffs, with a handedness ORCA lacks."
  - Conclusions: "ORCA reshapes the landscape with its rest drive at the lone trap, and at the pair its constraint part acts against that drive, solver by solver."

**M6. Whole-run failure overlap described as near-independent when it is significantly above independence.**
- Where: main.tex 1123 [`sections/06_attribution.tex:31`] and 1163 [`sections/08_discussion.tex:4`].
- Quotes:
  - "The failure sets overlap barely more than independent ones would (Jaccard \EsixJaccard\ against \EsixJaccardIndep; ...)"
  - "The minority outcome sets overlap little (... \EsixJaccard\ in whole runs, against \EsixJaccardIndep\ for independent sets ...)"
- Evidence: `E6_analysis.json:identity.p_perm_jaccard_above_independent` = 0.0023, and the independent-set 95% range is [0.24, 0.37]. The observed 0.41 lies outside that range: failures share seeds more than chance would give. They are still far from identical (35 + 37 of 122 failing seeds fail under one only).
- Fix, 1123: "The failure sets overlap more than independent sets would (Jaccard \EsixJaccard\ against \EsixJaccardIndep, permutation $p=0.002$) but are far from identical: 72 of the 122 failing seeds fail under one of the two only (discordant \EsixCThreeOnlyFail:\EsixNoiseOnlyFail, $p=\EsixMcNemarP$)."
- Fix, 1163: "The minority outcome sets are far from identical (...)".
- Register 0.002 and 72/122 as macros.

**M7. Main-differences paragraph asserts a recomputation that is not complete in this snapshot.**
- Where: main.tex 1179 [`sections/10_back_matter.tex:3`].
- Quote: "every quantity carried over from the conference paper was recomputed from new runs".
- Evidence:
  - The published-solver whole runs (E6p), counterflow (E8), crossing (E9) and overlaps (E11) are still `\pending` at 1139-1143. These are the conference counterflow, crossing, completion and overlap quantities.
  - The Table 1 parameter values are carried over and are read from the code, not recomputed from runs. The camera-ready (CR) Table 1 lists A = 2000 N, B = 0.08 m and k = 1.2×10⁵.
- Fix: "every result carried over from the conference paper was recomputed from new runs, and every parameter value re-read from the code". Re-check the sentence when §6.3 is filled.

**M8. Clinical-trial vocabulary: "arm".**
- Where:
  - 926 ×4 [`sections/03_model.tex:48`];
  - 981 [`sections/04_signatures.tex:5`];
  - 1083, Fig. 6 caption [`sections/06_attribution.tex:13`];
  - 1092, Table 3 column head "Arm" [`tables/table3_matched.tex:8`];
  - 1133 [`sections/06_attribution.tex:42`].
- Quotes:
  - "restarts a snapshot under one intervention (an arm) ... (deterministic arms stop ...), so arms are compared";
  - "(the frozen-mean arm)";
  - "for the arms that free";
  - "Arm";
  - "Every deterministic arm keeps its outcome".
- Evidence: the authors' standing rule and CHANGELOG C6 ("No pre-registration or trial vocabulary in the paper"). ("lever arm" at 1053 is physics and is fine.)
- Fix:
  - 926: "A quench restarts a snapshot under one intervention for at most 120\,s (deterministic runs stop once all speeds stay below $10^{-3}$\,m/s for 10\,s), so interventions are compared snapshot by snapshot."
  - 981: "(the frozen-mean push)".
  - 1083: "for the interventions that free".
  - Table 3 head: "Control".
  - 1133: "Every deterministic intervention keeps its outcome in all \PairReplayN\ replays."

**M9. Equivalence margins in the text.**
- Where: main.tex 1136 [`sections/06_attribution.tex:45`] and 1175 [`sections/08_discussion.tex:16`].
- Quotes: "though \PairN\ standoffs are too few to show equivalence within $\pm0.10$"; "\PairN\ pair standoffs cannot show rate equivalence within $\pm0.10$".
- Evidence: CHANGELOG C6 says "equivalence margins are kept internally only where they set sample sizes"; C57 says all intervals are 95%. The ±0.10 margin is the internal TOST margin (`E7b_analysis.json:s3_matched.*.rate.tost_0p10`).
- Fix:
  - 1136: "though with \PairN\ standoffs the 95\% interval of the difference is wide (Table~\ref{tab:matched})."
  - 1175: "Samples are finite: with \PairN\ pair standoffs a rate difference is known only to about $\pm0.2$ (95\%)."

**M10. Abstract and conclusions list separating probes that do not cover the whole-run match.**
- Where: main.tex 652 [`sections/00_abstract.tex:3`] and 1177 [`sections/09_conclusions.tex:3`].
- Quote: "reproduce the rate, yet free different deadlocks and differ in replay, time-step dependence or handedness".
- Evidence:
  - The whole-run noise control (σ*, E6) was not tested for replay, time step or handedness (Table 3: "---" in those columns).
  - It is separated by failure identity, completion time (64/64 seeds slower, KM medians 469 against 132 s) and final-state class (p = 1.4×10⁻³).
  - At the pair, the published-solver match shares 13 of 30 freed standoffs, so "free different deadlocks" is partial there.
- Fix, abstract: "... reproduce the rate, yet free partly different deadlocks and differ in replay, time-step dependence, time to completion or handedness: ...". Mirror the wording in the conclusions.

**M11. Second-trap and lone-trap claims rest on a noise standard deviation from the pooled library.**
- Where: main.tex 1114 [`sections/06_attribution.tex:22`].
- Quote: "its seeds disagree (within-snapshot standard deviation of the first exit \EtwoNoiseSDC\,s)", which renders 11.2 s.
- Evidence:
  - The registry key is `E2_analysis.json:b_replay_determinism.pooled.noise0p07.within_snapshot_sd_first_exit_s.median`, pooled over 59 snapshots (lone keystone and second trap).
  - The paragraph and Table 3 are about the 34 lone keystones. The lone-keystone value is 13.3 s over 33 snapshots (`...lone_keystone.noise0p07...median`).
- Fix: point `EtwoNoiseSDC` at the lone-keystone key, which prints 13.3. Or keep 11.2 and write "(over all 60 snapshots, within-snapshot standard deviation of the first exit 11.2\,s)".

### LOW

**L1. Hyphen instead of minus sign.**
- Where: main.tex 1067 [`05_deadlock_physics.tex:50`] "a line of slope \EfourCollapseSlope" renders "-0.93". Also 1163 [`08_discussion.tex:4`] "[\EsixDiffLo, \EsixDiffHi]" renders "[-0.10, 0.08]" (main.txt shows the hyphens).
- Fix: "$\EfourCollapseSlope$" and "[$\EsixDiffLo$, $\EsixDiffHi$]".

**L2. "vermilion" in Fig. 1 against "vermillion" in Figs 4, 5, 8 and 6.**
- Where: 822 (`figures/fig1_caption.tex:2`) against 1062, 1077 ×2, 1083 and 1148.
- Fix: one spelling throughout. Okabe-Ito writes "vermillion"; standard English is "vermilion".

**L3. "20\,000" in the Fig. 2 caption against "20000" in the text.**
- Where: 1026 [`05_deadlock_physics.tex:7`] and 1033 [`05_deadlock_physics.tex:15`]. `StuckAloneN` has `fmt: "{:d}"`.
- Fix: print "20\,000" from the macro (a thousands-separator format), or write `\StuckAloneN` in the caption too.

**L4. The seven negative-margin blockers are "pair standoffs at the jamb faces": six of seven are.**
- Where: 1035 [`05_deadlock_physics.tex:17`].
- Evidence: in `E1_keystone.json:modes.*.collective.cases`, six are two-agent standoffs (|dy| = 0.40-0.47 m, gap 0.30-0.32 m). E1a seed156 is a four-agent group.
- Fix: "...; six are two-agent pair standoffs at the jamb faces (Sect.~\ref{sec:pair}) and one is a four-agent group around such a pair."

**L5. "We report this rule descriptively" when no rule is stated, and an AUC set against an accuracy.**
- Where: 1037 [`05_deadlock_physics.tex:19`].
- Evidence: the k = 3 rule was removed from the text. `E1_analysis.json:E1b.k_rule_refined.rule_accuracy` = 0.962 is the quantity comparable to the "all-exit baseline accuracy of 0.931" (CHANGELOG C13 and C16b).
- Fix: "... with an area under the ROC curve of \EOneBAUCOthers\ [..]; the rule `exits if at least three others are active' classifies 0.962 of these agents correctly, against an all-exit baseline of \EOneBAllExitBaseline. We report this rule descriptively; ...". Add a macro for 0.962.

**L6. "the walls away from the door add nothing".**
- Where: 1035.
- Evidence: 89 against 85 of 100 completions, Fisher p = 0.529. That is no detectable difference, not "nothing".
- Fix: "The trap is therefore local to the door edges: shortening the other walls as well makes no detectable difference."

**L7. "the short-range law removes the lone traps".**
- Where: 1035.
- Evidence: `E7_analysis.json:cells.B0p04.classes.counts.lone_keystone` = 1 of the 15 classified deadlocks.
- Fix: "the short-range law removes the lone traps (one of the 15 deadlocks with all walls at 0.04\,m remains one) and leaves the pair standoffs of Sect.~\ref{sec:pair}."

**L8. Weibull shape "close to the exponential value 1" when its 95% interval excludes 1.**
- Where: 1067.
- Evidence: 1.09 [1.05, 1.14] (`E4_analysis.json:headline.weib_all*`).
- Fix: "is \EfourWeib\ [\EfourWeibLo, \EfourWeibHi], slightly above the exponential value 1".

**L9. "the stuck-alone fraction rises from 0.20 in the first decile ... to 0.62 in the last".**
- Where: 1037.
- Evidence: the decile fractions are 0.20, 0.19, 0.17, 0.16, 0.16, 0.14, 0.16, 0.17, 0.31 and 0.62 (`E1_chain.json:E1b.a_stuck_fraction_by_arrival_decile.frac`). The fraction is flat or falling, then jumps; CHANGELOG C22 and `c_reading` say the same.
- Fix: "the stuck-alone fraction is 0.14--0.20 over the first eight deciles of arrivals and 0.62 in the last".

**L10. "Every human run empties the holding area."**
- Where: 1154.
- Evidence: in `E10_analysis.json:humans.runs`, run 4D040 has 136 identified pedestrians and 135 passages.
- Fix: "No human run stops: every participant but one (run 4D040) passes the entrance." Or check the unmatched ID and restate.

**L11. One Wilson bound attached to two completions.**
- Where: 1157 [`07_validity.tex:16`].
- Quote: "(completion \EtenCPubComplete\ and \EtenCOneComplete, upper Wilson bound \EtenCPubCompleteHi, ...)".
- Evidence: 0.13 is the bound for 0/25. For 1/25 it is 0.20 (`cells.C1_cf.completion_wilson95` = [0.007, 0.195]).
- Fix: "(completion 0 and 1 of 25, upper Wilson bounds 0.13 and 0.20, ...)".

**L12. Replay count drawn from the published-solver key in a statement about RVO2.**
- Where: 1111 [`06_attribution.tex:19`].
- Quote: "(largest first-exit shift \EtwoReplayCThreeRVOMaxDt\,s in \EtwoReplayN)".
- Evidence: `EtwoReplayN` ← `b_replay_determinism.pooled.C3_pub.replays`. Its value of 300 equals the RVO2 count, so the printed value is right but the trace is wrong.
- Fix: add `EtwoReplayRvoN` ← `b_replay_determinism.pooled.C3_rvo2.replays` and use it at 1111.

**L13. "a property of the jamb wall law, not of crowding".**
- Where: 1169 [`08_discussion.tex:10`].
- Evidence: §5.1 shows that whether a stuck-alone agent exits depends on how many others are still active (AUC 0.975). Crowding decides when the trap closes.
- Fix: "First, the lone trap is set by the jamb wall law against each agent's own drive (Eq.~\eqref{eq:stuck}; Sects.~\ref{sec:lone} and~\ref{sec:validity}); crowding only decides whether others push a stuck-alone agent through."

**L14. "Noise is thermal at the temperature of Eq. (9)".**
- Where: 1117 [`06_attribution.tex:25`].
- Evidence: at β_ref = 2.5 the prediction lies outside the interval (3.70 against [2.96, 3.52]), and the overall slope is 0.91 [0.83, 1.01].
- Fix: "Noise acts thermally, close to the temperature of Eq.~\eqref{eq:teff}; ORCA is not thermal."

**L15. Conference control renamed.**
- Where: 829 [`01_introduction.tex:14`] and 1179.
- Quote: "with a minimal control".
- Evidence: the CR (abstract, keywords and §1) says "minimum-intervention control".
- Fix: "with a minimum-intervention control" at the first mention.

**L16. Conference configuration C4.**
- Where: 887 [`03_model.tex:9`].
- Quote: "The four configurations of the conference paper ... C4 adds TTC, ORCA and the crush term."
- Evidence: the CR calls C4 "full hybrid" (SFM + TTC + ORCA) and never mentions a crush term. The term is in the published code (CORRECTIONS_TABLE E11).
- Fix: "... and C4 adds TTC, ORCA and, in the published code though not in the conference description, the crush term."

**L17. Pre-registration claims.**
- Where: 1163 [`08_discussion.tex:4`] "The held-out signatures, derived from the physics before the runs, reject that reading each time." Also 854 [`02_background.tex:16`] "predicted from the physics of each mechanism class before they are measured".
- Evidence:
  - CHANGELOG C6: no pre-registration framing.
  - The timing is not documented in the repository, and the matched levels (σ = 0.07, b*) were chosen after the runs (C44, C53).
- Fix: "The held-out signatures, derived from the physics of each class, reject that reading each time." At 854: "predicted from the physics of each mechanism class".

**L18. "marginally stable ... below the resolution of the gate".**
- Where: 1069 [`05_deadlock_physics.tex:52`].
- Evidence:
  - `E6_analysis.json` counts seed60's 0.021 J full barrier among its "56 gated library barriers" (the gate accepted it).
  - E4 skipped it by the separate rule "dU < 0.1 J" (`E4_analysis.json:extension.skipped_no_barrier`).
  - So the text and the data use "gated" differently.
- Fix: "In one, the full barrier, 0.02\,J, is below the 0.1\,J floor used to set noise levels; ...".

**L19. The full-below-alone count includes the two snapshots set aside.**
- Where: 1067.
- Quote: "the full barrier lies below the alone barrier in \EfourSaddleBelow\ of \EfourSaddleN\ snapshots, with median ratio \EfourSaddleRatio".
- Evidence: the 10 include seed60 (ratio 0.003) and seed170 (ratio 0.004, "not the route the dynamics takes"). Over the other 8 the median ratio is 0.32 (range 0.03-0.66). The claim survives; the median should name its population.
- Fix: "... in all 10 snapshots (median ratio 0.32 over the 8 used in the fits) ...".

**L20. In-figure text in Figs 3, 6, 7 and 8.**
- Where: page images p-11, p-15, p-17 and p-18.
- Evidence:
  - Category tick labels ("default", "all walls 0.04", "C3 pub", "constr. RVO2", "±b* pub", "C1 jamb B_w", ...) are text inside the figures.
  - The standing rule says Figs 2-8 carry no in-figure text. FINAL_PLAN §10 says "axis labels only; every series ... identified in the caption".
- Fix: decide whether category tick labels count as axis labels. If not, drop them and give the left-to-right order in each caption.

**L21. Run details in figure captions (CHANGELOG C3).**
- Where:
  - Fig. 2 "with the 20 000 spawned agents" (1026);
  - Figs 6 and 7 "within 120 s" (1083, 1129);
  - Fig. 8 "for the five CroMa runs at w = 0.8 m" (1148).
- Fix: move n and window to the text, for example Fig. 2 "with the spawned agents as points".

**L22. Table 1 edge-range variant incompletely described.**
- Where: 865 [`tables/table1_params.tex:11`].
- Quote: "$B_{w,\rm edge}$ (within 0.5 m of the door edge)".
- Evidence: `data/params/model.yaml:edge_zone` = [0.5, 1.0]. The range applies within 0.5 m and blends linearly to B_w by 1.0 m. The crush coefficients at 868 also lack units (kg/s², kg/(m s)).
- Fix: "$B_{w,\rm edge}$ (within 0.5 m of the door edge, blended linearly to $B_w$ by 1.0 m)", and add units to the crush row.

**L23. Table 1 does not cite the conference source.**
- Where: 857 caption [`tables/table1_params.tex:3`].
- Evidence: FINAL_PLAN §1, invitation rule: "every table or figure taken from the conference paper regenerated and citing its source". Table 1 is the regenerated counterpart of CR Table 1.
- Fix: append to the caption "The values agree with the conference paper~\cite{gang2026}, except where noted."

**L24. Degenerate interval in Table 3.**
- Where: 1105, "0.00 [0.00, 0.00]" for the RVO2 pair J.
- Evidence: the percentile bootstrap of an index that is 0 in every resample is degenerate and is not an informative 95% interval (`s3_matched.rvo2.jaccard_freed`: 0 of 15).
- Fix: print "0 (0/15)" with "---" for the interval, or state in the caption that a bootstrap interval is not defined when no standoff is shared.

## 2. Qualitative claims against results (other than the defects above)

| Claim (main.tex line) | Supporting result | Verdict |
|---|---|---|
| 652 "deadlocks fall into two classes: a lone agent held by the wall force at the door edges, and a symmetric pair standoff, a strict energy minimum that a lateral bias removes at a fold" | E1_chain 393/393 criterion; E7b strict_min 46/46, fold 363/368 | Supported. The pair class is common only with short-range jamb walls (2 of 98 deadlocks collective under default walls, E7). §5.2 states this, the abstract does not. Optional wording: "and, with short-range jamb walls, a symmetric pair standoff". |
| 652 "ORCA adds a goal drive, noise drives activated escape over computed barriers" | E2 drive_only = C3 (0:0), frozen ±; E4 ratio CIs cover 1 in 25/28; E3 ℓ | Supported |
| 652, 837, 1157, 1177 "every model variant either deadlocks or flows at 0.40-0.59 of the human rate" | E10 ratios: pub 0.49, cf 0.51, edge 0.57, C3 0.59, σ* 0.40 | Supported. Every variant, deadlocking or not, lies in the range. |
| 835 "stuck-alone criterion that holds in 393 of 393 deadlocks" | E1_chain agree 393/393 | Supported |
| 835 "contact arches formed at high drive never persist, because the model has no static friction" | arch: 0/25 persistent, max 2.9 s | Supported for v0 = 5 m/s, 25 runs |
| 836 "noise matched to its rate acts thermally; the two differ in which deadlocks they leave unresolved, in replay and in time-to-free" | J 0.20, 9/34 seeds disagree, t½ 19.8 vs 1.5 s | Supported |
| 836 "In whole runs, noise matched ... fails on other seeds, completes later and leaves other final states" | E6 35:37 discordant, 64/64 slower, class p 1.4×10⁻³ | Supported. "other seeds" should read "partly other seeds" (50 shared failures); see M6. |
| 1001 "Hence C2 has exactly C1's fixed points and stability" | lemma; E2 360/360 identical | Supported |
| 1035 "The trap is a property of the door geometry and of the jamb wall law" | E7 width and B_w cells | Supported |
| 1042-1051 strict minimum, softest common lateral, fold | E7b a_statics | Supported |
| 1056 "The model's persistent deadlocks are therefore not contact arches" | arch analysis, deadlocks_with_contact 0 | Supported |
| 1067 "All three predictions of activated escape hold" | ratio medians 1.15/0.95/0.87, CI covers 1 in 25/28; Weibull 1.09; full<alone 10/10 | Mostly supported; see L8 and L19 |
| 1071 "The two modes need the same noise" | 0.044 [0.041, 0.047] vs 0.045 [0.042, 0.047] | Supported |
| 1111 "This is class L: a deterministic drive that removes the fixed point" | 0/170 replay flips; frozen + 31, − 0; ℓ ≈ 0 | Supported |
| 1114 "The lateral bias (class D) frees no lone keystone at any b" | E2 bias0p05-0p5 all 0/34 | Supported (at the second trap b = 0.1 frees 1 and b = 0.2 frees 2 of 26; the sentence is limited to lone keystones, so correct) |
| 1120 "which a replay this small reveals as ill-conditioning of that implementation (class N)" | C3_pub 5/300 flips, all second trap; RVO2 0/300 | Supported (constraint_only_pub also flips 5, consistent with "published linear program") |
| 1136 "Matched on rate, the bias shares ORCA's number, not its mechanism" | J 0.43 / 0.00; handedness 22/22 vs 11/21 | Supported |
| 1157 "C3 RVO2 never deadlocks" | deadlock 0, capped 15 | Supported |
| 1157 "No agent leaves the walkable area in any run" | E10 wall_leaks_total 0 in all cells | Supported |
| 1160 "a deadlock rate may measure only this margin" | §5.1 | Reasoned; acceptable |
| 1163 "in all three of our pairs it does" | Δ −0.01, −0.01, +0.02 / +0.02 | Supported |
| 1166 "different mechanisms reach the same sum from different deadlocks, as the low overlaps show" | J 0.20, 0.41, 0.43, 0.00 | Overstated for whole runs (see M6). Fix: "as the incomplete overlaps show". |
| 1172 "noise frees them by the activated escape that trap models assume" | §5.4 | Supported (lone trap only; at the pair noise is reported descriptively, C45) |
| 1177 "A mechanism claim needs a test where the mechanism acts" | rhetorical | Fine |

## 3. Same quantity across the paper

| Quantity | Abstract | Introduction | Body | Tables/captions | Discussion/Conclusions | Consistent? |
|---|---|---|---|---|---|---|
| Flow ratio to humans | 0.40-0.59 (652) | 0.40-0.59 (837) | 0.40-0.59; C1 cf 0.51 [0.46, 0.58]; C3 0.59 [0.53, 0.67] (1157); edge 0.57 (1160) | Fig. 8 (95% intervals) | 0.40-0.59 (1177) | Yes; 2 decimals throughout; intervals 95% bootstrap |
| Longest gap | n/a | 5.7 s or more vs 1.7 s (837) | 5.7-6.8 s deterministic, 72.2 s noise, humans 1.7 s, max "2.0" (1154, 1157) | Fig. 8 | 72.2 s (1160) | Values consistent; see M3 for max 2.04 |
| Stuck-alone criterion | n/a | 393 of 393 (835) | 393 of 393, 7 negative (1035); TermN 393 (895, 1029) | n/a | n/a | Yes |
| Pair strict minima | "strict energy minimum" | all 46 (835) | 46 of 46 (1049) | Table 3: 46 snapshots | n/a | Yes |
| Lone-trap matched rate | n/a | n/a | 30/34 C3; σ = 0.07 148/170 (1111, 1114) | Table 3 Δ −0.01 [−0.10, 0.08] | Δ = −0.01 (1163) | Yes. Units differ (snapshots against runs; Table 3 caption says so) |
| Whole-run match | n/a | n/a | σ* = 0.0467 m/s; 99/186 vs 101/186 (1123) | Table 3; Fig. 8 "σ*" | Δ −0.01 [−0.10, 0.08] (1163) | Yes |
| Pair match | n/a | n/a | b*_pub 0.0223, b*_RVO2 0.0091; 22 vs 21, 8 vs 7 (1136) | Table 3 | J 0.43 and 0.00 (1163) | Yes |
| Published vs RVO2 at pair | n/a | n/a | 21 vs 7, 14:0 (1133) | Table 3 | 21 and 7 of 46 (1169) | Yes |
| Published-LP replay flips | n/a | n/a | 5 of 300, up to 80.8 s (1120) | n/a | 5 of 300 lone-trap snapshots (1169) | Yes. 1169 says "lone-trap snapshots"; the 300 are replays (60 snapshots × 5), so "5 of 300 replays at lone-trap snapshots" is more exact (LOW). |
| σ50 | n/a | n/a | 0.044 [0.041, 0.047] cf; 0.045 [0.042, 0.047] pub; conference 0.049 (1071) | n/a | n/a | Yes; profile-likelihood 95% (level not printed in the text: add "95%") |
| Human flow | n/a | n/a | 1.48 [1.22, 1.74] ped/s; long 1.32, short 1.58 (1154, 1157) | Fig. 8 | n/a | Yes; Student-t 95% (stated at 1151) |
| Second-trap counts | n/a | n/a | 26 snapshots; 17 vs 24 (1120) | Fig. 6 | n/a | Yes |
| Arrhenius coverage | n/a | n/a | 7/8, 9/10, 9/10 (1067) | Fig. 4 | n/a | Yes = 25/28 (C30) |
| Intervals at 95% | Every bracketed interval was traced to a `ci95`, `wilson95`, `ci95_profile`, `ci95_boot` or `ci95_seed_bootstrap` key or to a 95% routine in the generating script (E3 and E4 doc strings: exact Poisson 95%, 2000-resample percentile, 95% profile). No 90% interval reaches the paper (table3_pair.json replaced the E7b 90% interval, C57). | | | | | Yes |

## 4. Compliance with recorded decisions (plan/CHANGELOG.md, plan/FINAL_PLAN.md)

| Decision | Applies to | Snapshot | Lines |
|---|---|---|---|
| C2 eight figures; Fig. 1 hero | figures | Complies (8 figures) | 656-1148 |
| C3 captions ≤ 2 sentences; run details to text | figure captions | Sentence count complies for all 8 captions; run details partly in captions (L21) | 822, 1026, 1083, 1129, 1148 |
| C4 corner rule wording | §3 | Complies | 906 |
| C6 physics framing, no trial or pre-registration vocabulary; Table 2 title | whole paper | Table 2 complies; "arm" used (M8); equivalence margin in text (M9); "before the runs" (L17) | 926, 981, 1083, 1092, 1133, 1136, 1163, 1175 |
| C7 in-text numbers from numbers.tex | all numbers | Complies: 629 macros regenerate identically. Some numbers in prose are hard-coded (Section 7b) | 22-650 |
| C12 quench stop rule and 120 s window | §3 | Complies | 926 |
| C13 end-of-queue rule against all-exit baseline; rank AUC headline | §5.1 | Complies in substance; the rule itself is not stated (L5) | 1037 |
| C14 Table 2 last column "Corrected numerics"; D "no Δt dependence" | Table 2 | Complies | 929-980 |
| C16 (a) 393/393; 7 negative-margin = collective pair standoffs | §5.1 | Complies; 6 of 7 strictly pairs (L4) | 1035 |
| C16 (b) k = 3 rule descriptive | §5.1 | Complies | 1037 |
| C18 marginally stable barriers reported as physics and kept out of E3/E4 | §5.4 | Reported as physics (complies). seed60 is still in E4 for the frozen and alone conditions and in the saddle count (L19) | 1067-1069 |
| C19 rest-state lemma; C2 = C1 360/360 | §4.1, §6.1 | Complies | 990-1001, 1111 |
| C20 replay reading; published LP 5/300, class N; forward claims on RVO2 | §6.1 | Complies | 1111, 1120 |
| C21 E2 per stratum | §6.1 | Complies | 1111-1120 |
| C22 end of queue | §5.1 | Complies; wording L9 | 1037 |
| C24/C32/C43 Fig. 1: 17 labels at 6.5 pt; Figs 2-8 label-free; caption states white zone | Fig. 1 | 17 labels (lines 67-83 of the TikZ overlay; complies); white-zone sentence present. Figs 3, 6, 7 and 8 carry category tick labels (L20) | 656-822 |
| C25 Fig. 2 fixes | Fig. 2 | Complies (p-10: trimmed x range, light map, dark points, unfilled blue boundary lines) | 1026 |
| C26/C46 second trap pair-like; cancellation 0.27 vs 0.26 | §6.1 | Complies in numbers; geometry 9/10 (M1) | 1120 |
| C27 "initial density", not inflow | §3, §6.3 | Complies | 926, 1141-1142 |
| C28 common shift +δ | §5.2 | Complies | 1049 |
| C29 seed170 reported, excluded from fits | §5.4 | Complies | 1069 |
| C30 T3/T4 numbers | §4.2, §5.4 | Complies (1.00, 0.99, 207; 25/28; −0.93; 1.09; ℓ 3.23 vs 3.70; slope 0.91 [0.83, 1.01]) | 1008, 1067, 1117 |
| C33 single-file submission | build | `paper/submission/main.tex` is identical to the snapshot | n/a |
| C36 σ50 published = corrected; conference 0.049 outside both | §5.4 | Complies ("lies just above both intervals") | 1071 |
| C38 residual wording | §4.1 | Follows C38, but C38's "1e-7 N" pair bound is itself below the data (M2) | 1001 |
| C39 crowd-disaster citations and koster2013 | §1, §3 | Complies | 826, 923 |
| C40 p-value format | all p | Complies (0.529, 0.170, 0.016, 0.906, 1.000; 3.5×10⁻⁴¹, 2.3×10⁻⁴, 1.4×10⁻³, ...) | passim |
| C41 σ* = 0.0467 from E5b fit at E6a rate | §6.1 | Complies; recomputed 0.046658 | 1123 |
| C44 pair matched bias | §6.2, Table 3 | Complies | 1103-1106, 1136 |
| C45 noise at the pair descriptive, not class T | §5.2 | Complies | 1053 |
| C47 E6 reporting | §6.1 | Complies (Δ, J 0.41, 64/64, p 1.4×10⁻³) | 1123 |
| C48 stall lifetimes against no-fit prediction | §6.1 | Complies (0.05) | 1123 |
| C49 §5.3 from production high-drive run | §5.3 | Complies (25 seeds, 600 s, v0 = 5) | 1056 |
| C50 velocity, not density, fluctuation | §7 | Complies ("velocity fluctuation"); the |y − y_c| < 2 m limit and the pooled-component definition are not stated (LOW) | 1151 |
| C52 Zenodo DOI at submission | back matter | Pending (known) | 1182 |
| C53 Table 3 as thesis table with three blocks | Table 3 | Complies in structure; ℓ cell attribution (H1) | 1086-1109 |
| C56 J on minority outcome sets, rule stated once in §6 | §6.1, Table 3 | Complies (1114; repeated in the Table 3 caption, harmless) | 1087, 1114 |
| C57 all intervals 95% | all | Complies (Section 3, last row); degenerate J interval (L24) | 1105 |
| C58 captions below figures | all figures | Complies (Fig. 5 caption below) | 1077 |
| FINAL_PLAN §1 invitation: cite conference in text and references; new title, abstract and conclusions; main-differences statement | front and back matter | Complies; Table 1 not cited to its conference counterpart (L23); differences paragraph M7 | 830, 1179, 857 |
| FINAL_PLAN §10 Okabe-Ito colour map | figures | Complies (C1 black, C2 orange, C3 pub sky blue, C3 RVO2 blue, ORCA parts reddish purple, bias yellow, noise vermillion, humans grey) | captions |
| FINAL_PLAN §10 axis labels only | Figs 2-8 | See L20 | p-11, p-15, p-17, p-18 |
| Standing rule: physics-first framing | whole paper | Complies apart from M8/M9/L17 vocabulary | n/a |

## 4b. Figures: captions and citing prose against cached data and page images

| Figure | Data checked | Result |
|---|---|---|
| Fig. 1 (p-02) | `figures/fig1_hero.json`; `experiments/hero/make_luts.py` | Lone-scene arrows: drive 131.2 N + push 17.5 N = 148.6 N = wall 148.6 N ("black plus grey equals the wall arrow": VERIFIED). Thermal band k_BT = 10.2 J with a 10 J bar; pair bar 0.5 J. Floor log scale 5-1000 N (args force_min/force_max) and margin ±150 N: VERIFIED. 17 labels (C32). The pair scene's B_w = 0.04 m matches the E7b library. |
| Fig. 2 (p-10) | `figures/data/fig2.json`; `E1_analysis.json:gmax_curve` | Curves peak at 83, 156, ~295 and 543 N for r = 0.20, 0.25, 0.30 and 0.35 m. The text's 83/156/543 are VERIFIED (indices 80, 130, 230 ↔ r = 0.20, 0.25, 0.35). C1 band 141-304 N with median 214; C3 blue band median ≈ 430 N = `C3_rest_total.p50` (caption: "rest-state drive for C3 RVO2": consistent). |
| Fig. 3 (p-11) | `figures/data/fig3.json` | Width points 0, 0.02, 0.70, 1.00 with Wilson intervals; variant bars partition all 100 runs (completed / collective / lone) as captioned: VERIFIED. "pair or group standoff" = collective (see L4). Tick labels: L20. |
| Fig. 4 (p-13) | `figures/data/fig4.json`, `E4_analysis.json:km` | KM at β = 2.5: full ends at S = 0.32 (n = 180, including seed170, which is excluded from the Arrhenius fits but not from this panel); frozen 0.04; alone 0.13. The line styles match the caption. Right: 84 points, slope −1 line: VERIFIED. |
| Fig. 5 (p-14) | `figures/data/fig5.json` | β 1.5 points at Δt = 0.005/0.02: 2.02/0.23 → ln ratio 2.17 ≈ ℓ 2.16; β 2.5 → 3.2 ≈ 3.23; C3 flat; √Δt flat: VERIFIED against the text at 1117. |
| Fig. 6 (p-15) | `figures/data/fig6.json` | Freed fractions and Wilson intervals equal `E2_analysis.json` (for example C3 RVO2 lone 30/34 [0.734, 0.953]; second trap 17/26). KM right panel: C3 RVO2 plateau 0.78 = 47/60 pooled ("strata pooled"): VERIFIED. |
| Fig. 7 (p-17) | `figures/data/fig7.json` | Bias curve counts 30/18/7/0/8/17/32/44/46; static step 29/16/6/0/8/16/32/44/46, giving 5 misses = PairFoldFN. C3 lines 0.46 and 0.15 = 21/46 and 7/46; noise σ = 0.01-0.05 near 1: VERIFIED. |
| Fig. 8 (p-18) | `figures/data/fig8.json`, `E10_analysis.json` | Per-run points equal the E10 runs; means and 95% t intervals as in the text: VERIFIED. Caption marker key (published open, cf filled, jamb square) matches the image. |

## 4c. Statements about the conference version (ref/camera_ready_SIMULTECH2026.pdf, text extracted with pdftotext)

| Statement (line) | Camera-ready | Verdict |
|---|---|---|
| 829 "Our conference paper proposed that such statements be tested by pairing a failure-mode ablation with a minimal control: a perturbation of the baseline model that shares none of the paradigm's machinery, tuned until it reproduces the paradigm's headline score." | Abstract: "failure-mode ablations ... should be accompanied by minimum-intervention controls that isolate each paradigm's operative mechanism from trivial alternatives"; §5: "report the noise level matching the paradigm's headline advantage (σ50)" | Accurate in substance; terminology L15 |
| 887 "The four configurations of the conference paper switch terms on: C1 is SFM only, C2 adds TTC, C3 adds ORCA, and C4 adds TTC, ORCA and the crush term." | C1 SFM, C2 SFM+TTC, C3 SFM+ORCA, C4 "full hybrid"; no crush term described | L16 |
| 863 (Table 1) "calibrated values of the conference paper are not applied" | CR Table 1 lists calibrated values (Cal.† column) and the FD calibration | Accurate (CORRECTIONS E2) |
| 1071 "The conference estimate, 0.049 m/s from 25 runs per level, lies just above both intervals." | "σ50 = 0.049 m/s (95% CI [0.044, 0.053])"; "n = 25 seeds per σ" | Accurate; 0.049 > 0.047 (both upper bounds) |
| 1179 "keeps one idea: a paradigm's effect is audited against a minimal control matched to its headline score" | as above | Accurate |
| 1179 "The title, abstract, conclusions, figures and tables are new" | CR title "A Diagnostic Methodology for Failure-Mode Ablation of SFM, TTC, and ORCA Pedestrian Steering Paradigms" | Accurate |
| 1179 "every quantity carried over ... was recomputed from new runs" | n/a | M7 |
| 1179 "The conference reading that noise and ORCA resolve deadlocks alike is replaced" | CR: "within n = 25, passive noise is indistinguishable from ORCA's LP-based velocity selection as a deadlock-breaking mechanism"; "attributable to passive symmetry-breaking" | Accurate |
| 1179 "a like-for-like comparison with human bottleneck data at 0.8 m" is new | CR: OOD comparison with FZJ data at 2.4-5.0 m (Table 3), not at 0.8 m | Accurate |
| 1179 "with ORCA reported for the published solver and for RVO2" is new | CR: "ORCA (van den Berg et al., 2011)", one implementation | Accurate |
| §6.3 framing (1139-1143, pending) | CR claims to revise: C3 13/25 and C4 14/25 (E6p), "ORCA reciprocal yielding gridlocks counterflow" (E8), "C2 roughly triples throughput" (E9), throat overlaps 1.20 ± 1.96 at w = 1.0 (E11) | Pending rows map onto real CR claims. E11 adds w = 1.2 and 1.8 m (code WIDTHS = (1.0, 1.2, 1.8)) |

## 5. Recomputation from data/derived (57 values)

Wilson score 95%, exact two-sided McNemar (binomial on discordant pairs), two-sided Fisher exact and Student-t 95% intervals were coded by hand and evaluated on the counts in the JSON files.

| Quantity | Printed | Recomputed | How |
|---|---|---|---|
| EsevenWNineLo/Hi | 0.60/0.78 | 0.6042/0.7811 | Wilson 70/100 |
| EsevenWTenLo | 0.96 | 0.9630 | Wilson 100/100 |
| E7 default Wilson (Fig3) | (fig) | 0.0055/0.0700 | Wilson 2/100 |
| ArchPersistentHi | 0.13 | 0.1332 | Wilson 0/25 |
| EtenCPubCompleteHi | 0.13 | 0.1332 | Wilson 0/25 |
| EtwoMaxBiasUpperLK | 0.10 | 0.1015 | Wilson 0/34 |
| PairFoldLo | 0.969 | 0.9686 | Wilson 363/368 |
| EOneBCompletion CI (unused) | 0.008/0.050 | 0.0078/0.0503 | Wilson 4/200 |
| EOneACompletion CI (unused) | 0.005/0.043 | 0.0051/0.0432 | Wilson 3/200 |
| EtwoSTDriveVsRVOP | 0.016 | 0.01562 | exact McNemar 7:0 |
| PairPubRvoP | 1.2e-4 | 1.221e-04 | exact McNemar 14:0 |
| PairDriveRvoP | 8.7e-7 | 8.680e-07 | exact McNemar 28:2 |
| EsixMcNemarP | 0.906 | 0.9063 | exact McNemar 35:37 |
| PairBsPubP | 1.000 | 1.0000 | exact McNemar 9:8 |
| PairBsRvoP | 1.000 | 1.0000 | exact McNemar 8:7 |
| E2 LK frozen+ vs - (unused) | - | 9.313e-10 | 31:0 |
| EsevenJambVsDefaultP | 3.5e-41 | 3.479e-41 | Fisher 89/100 vs 2/100 |
| EsevenJambVsAllP | 0.529 | 0.5289 | Fisher 85/100 vs 89/100 |
| EsevenRoundVsDefaultP | 0.170 | 0.1697 | Fisher 7/100 vs 2/100 |
| EsevenCollectiveP | 2.0e-13 | 2.033e-13 | Fisher 2/98 vs 11/11 |
| StPairFisherP | 2.3e-4 | 2.336e-04 | Fisher 2/10 vs 15/16 |
| EsixJaccard | 0.41 | 0.4098 | 50/(50+35+37) |
| EsixJaccard (from seed lists) | 0.41 | 0.4098 |  / C3fail / =85, / sigfail / =87,both=50 |
| EsixCThreeOnlyFail/NoiseOnlyFail | 35/37 | 35/37 | seed lists |
| EsixJaccardIndep | 0.30 | 0.3006 | plug-in expectation, independent sets of sizes 85, 87 in 186 |
| EsixDiff | -0.01 | -0.0108 | 99/186-101/186 |
| EsixPairedCThreeFaster (both complete) | 64 | 64 | 186- / union fail /  |
| TabThreeLKDiff | -0.01 | -0.0118 | 148/170-30/34 |
| EtwoLKJaccardC | 0.20 | 0.2000 |  / {seed83} / / / {203,211,83,87,69} /  |
| PairBsPubJac | 0.43 | 0.4333 | 13/30 |
| TabThreePairPubDiff | +0.02 | 0.0217 | 22/46-21/46 |
| TabThreePairRvoDiff | +0.02 | 0.0217 | 8/46-7/46 |
| EtenHumanFlow [Lo,Hi] | 1.48 [1.22,1.74] | 1.4762 [1.2164,1.7360] | Student-t over 5 runs |
| EtenHumanGap / GapMax | 1.7 / 2.0 | 1.712 / 2.040 | mean/max of per-run longest gap |
| EtenHumanFluct [Lo,Hi] | 0.074 [0.070,0.079] | 0.0743 [0.0699,0.0786] | Student-t |
| EtenHumanGapsTwo | 0.2 | 0.20 | mean count |
| EtenLongHumanFlow | 1.32 | 1.3226 | L=2.0 runs |
| EtenShortHumanFlow | 1.58 | 1.5786 | L=0.21 runs |
| EtenCOneFlowRatio | 0.51 | 0.5092 | C1_cf flow mean / human flow mean |
| EtenCThreeFlowRatio | 0.59 | 0.5882 | C3_rvo2_cf flow mean / human flow mean |
| EtenCSigFlowRatio | 0.40 | 0.3994 | C1_cf_sig flow mean / human flow mean |
| EtenCEdgeFlowRatio | 0.57 | 0.5714 | C1_cf_edge flow mean / human flow mean |
| (C1 pub ratio) | in range | 0.4915 | C1_pub flow mean / human flow mean |
| PairAxisMin/Max | 0.40/0.50 | 0.4003/0.5032 | n=92 members |
| Efour ratio median full | 1.15 | 1.1507 (n=8) | median of per-snapshot slope/(-dU) |
| Efour ratio median frozen | 0.95 | 0.9486 (n=10) | median of per-snapshot slope/(-dU) |
| Efour ratio median alone | 0.87 | 0.8660 (n=10) | median of per-snapshot slope/(-dU) |
| EfourEvents full/frozen/alone | 382/581/554 | 382/581/554 | sum over snapshots and levels (incl. excluded) |
| Weidmann factor at ρ = 10/(9π) | 0.994 | 0.99362 | Weidmann formula |
| σ* | 0.0467 | 0.046658 | (logit(101/186) + 3.17483)/71.74143 |
| σ50 (cf) | 0.044 | 0.044254 | logistic fit inversion at 0.5 |
| ORCA rest drive | 215 (median) | 214.4 | 80 · 1.34 / 0.5 |
| Fig. 1 force balance | equal arrows | 131.16 + 17.47 = 148.63 | fig1_hero.json |
| PairFoldFN | 5 | 5 | fig7.json bias minus static step |
| Handedness total | 202 | 202 | 30+18+7+8+17+32+44+46 |
| Keystone classes | 393 | 196 + 197 | 34+160+2, 38+154+5; second trap 160+154 = 314 |
| g_max at r = 0.20/0.25/0.35 | 83/156/543 | 83.3/155.6/543.3 | gmax_curve indices 80/130/230 |

All 57 agree at the printed precision.

## 6. Script map (JSON in data/derived -> generating script)

| JSON | Script |
|---|---|
| E1_analysis | experiments/E1/e1_analyze.py |
| E1_chain / E1_terminal / E1_keystone | experiments/E1/chain.py / terminal.py / keystone.py |
| E2_analysis / E2_second_trap | experiments/E2/analyze.py / second_trap.py |
| E3_analysis / T3_variance | experiments/E3/analyze.py / t3_variance.py |
| E4_analysis | experiments/E4/analyze.py |
| E5_analysis / E5a_analysis | experiments/E5/analyze.py / analyze_e5a.py |
| E6_analysis / sigma_star | experiments/E6/analyze.py / e6.py |
| E7_analysis | experiments/E7/analyze.py |
| E7b_analysis / field_residuals | experiments/E7b/analyze.py / residuals.py |
| arch_analysis | experiments/arch/analyze.py |
| E10_analysis | experiments/E10/analyze.py (estimator experiments/pilot/w28_croma.py) |
| table3_pair | experiments/tables/make_table3.py (derive) |

## 7. Trace table

### 7a. Macros (376 used in the body, tables and captions)

All rows regenerate byte-identically through `tools/make_numbers.py` (chain macro -> registry -> JSON -> script VERIFIED mechanically); the status column records whether the printed value also says what the text claims.

| # | Macro | Printed | main.tex lines | Registry | JSON:key | Script | Status | Note |
|---|---|---|---|---|---|---|---|---|
| 1 | `EtenCSigFlowRatio` | $0.40$ | 652, 837, 1157, 1177 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf_sig.flow_ratio_to_human.ratio` | `experiments/E10/analyze.py` | VERIFIED |  |
| 2 | `EtenCThreeFlowRatio` | $0.59$ | 652, 837, 1157, 1177 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.flow_ratio_to_human.ratio` | `experiments/E10/analyze.py` | VERIFIED |  |
| 3 | `CriterionAgree` | $393$ | 835, 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.agree` | `experiments/E1/chain.py` | VERIFIED |  |
| 4 | `CriterionN` | $393$ | 835, 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.n_deadlocks` | `experiments/E1/chain.py` | VERIFIED |  |
| 5 | `PairStrictMin` | $46$ | 835, 1049 | pair.yaml | `E7b_analysis.json:a_statics.strict_min` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 6 | `EtenCThreeGap` | $5.7$ | 837, 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.longest_gap.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 7 | `EtenHumanGap` | $1.7$ | 837, 1154, 1157 | e6_e10.yaml | `E10_analysis.json:humans.longest_gap.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 8 | `TermN` | $393$ | 895, 1029 | core.yaml | `E1_terminal.json:n` | `experiments/E1/terminal.py` | VERIFIED |  |
| 9 | `TermNbMax` | $10$ | 895 | core.yaml | `E1_terminal.json:n_neighbours.max` | `experiments/E1/terminal.py` | VERIFIED |  |
| 10 | `TermNbMedian` | $2$ | 895 | core.yaml | `E1_terminal.json:n_neighbours.median` | `experiments/E1/terminal.py` | VERIFIED |  |
| 11 | `TermRhoMax` | $0.35$ | 895 | core.yaml | `E1_terminal.json:rho.max` | `experiments/E1/terminal.py` | VERIFIED |  |
| 12 | `TermWeidMin` | $0.994$ | 895, 1029 | core.yaml | `E1_terminal.json:weidmann.min` | `experiments/E1/terminal.py` | VERIFIED |  |
| 13 | `ResidBarN` | $60$ | 1001 | core.yaml | `field_residuals.json:lone.n` | `experiments/E7b/residuals.py` | VERIFIED |  |
| 14 | `ResidCollMax` | ${5\times10^{-7}}$ | 1001 | core.yaml | `field_residuals.json:collective.max_N` | `experiments/E7b/residuals.py` | VERIFIED |  |
| 15 | `ResidPairMax` | ${1\times10^{-7}}$ | 1001 | core.yaml | `field_residuals.json:pair.max_N` | `experiments/E7b/residuals.py` | MISMATCH | data 1.39e-7 > printed bound 1e-7 (M2) |
| 16 | `ResidPairN` | $46$ | 1001 | core.yaml | `field_residuals.json:pair.n` | `experiments/E7b/residuals.py` | VERIFIED |  |
| 17 | `TthreeCells` | $207$ | 1008 | core.yaml | `T3_variance.json:stored_moments.cells` | `experiments/E3/t3_variance.py` | VERIFIED |  |
| 18 | `TthreeCellsMedian` | $0.99$ | 1008 | core.yaml | `T3_variance.json:stored_moments.median` | `experiments/E3/t3_variance.py` | VERIFIED |  |
| 19 | `TthreeRatioMean` | $1.00$ | 1008 | core.yaml | `T3_variance.json:ratio_measured_formula_mean` | `experiments/E3/t3_variance.py` | VERIFIED |  |
| 20 | `GmaxThirtyFive` | $543$ | 1029 | core.yaml | `E1_analysis.json:gmax_curve.gmax_N.230` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 21 | `GmaxTwenty` | $83$ | 1029 | core.yaml | `E1_analysis.json:gmax_curve.gmax_N.80` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 22 | `GmaxTwentyFive` | $156$ | 1029 | core.yaml | `E1_analysis.json:gmax_curve.gmax_N.130` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 23 | `DriveCOneHi` | $304$ | 1033 | core.yaml | `E1_analysis.json:E1b.drives_N.C1_free_m_v0_over_tau.p95` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 24 | `DriveCOneLo` | $141$ | 1033 | core.yaml | `E1_analysis.json:E1b.drives_N.C1_free_m_v0_over_tau.p5` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 25 | `DriveCOneMedian` | $214$ | 1033 | core.yaml | `E1_analysis.json:E1b.drives_N.C1_free_m_v0_over_tau.p50` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 26 | `DriveORCAMedian` | $215$ | 1033 | core.yaml | `E1_analysis.json:E1b.drives_N.C3_rest_orca_drive_w_o_m_v0_over_tau_orca.p50` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 27 | `EOneBStuckAloneFrac` | $0.234$ | 1033 | core.yaml | `E1_analysis.json:E1b.stuck_alone_frac_C1.frac` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 28 | `StuckAloneFracCThree` | $0.013$ | 1033 | core.yaml | `E1_analysis.json:E1b.stuck_alone_frac_C3_rest.frac` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 29 | `StuckAloneN` | $20000$ | 1033 | core.yaml | `E1_analysis.json:E1b.stuck_alone_frac_C1.n` | `experiments/E1/e1_analyze.py` | VERIFIED | prints 20000 vs caption 20\,000 (L3) |
| 30 | `CriterionNegMargin` | $7$ | 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.negative_margin_blockers` | `experiments/E1/chain.py` | VERIFIED |  |
| 31 | `EOneACompletionK` | $3$ | 1035 | core.yaml | `E1_analysis.json:E1a.completion.k` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 32 | `EOneACompletionN` | $200$ | 1035 | core.yaml | `E1_analysis.json:E1a.completion.n` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 33 | `EOneBCompletionK` | $4$ | 1035 | core.yaml | `E1_analysis.json:E1b.completion.k` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 34 | `EOneBCompletionN` | $200$ | 1035 | core.yaml | `E1_analysis.json:E1b.completion.n` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 35 | `EsevenBallClassified` | $15$ | 1035 | e7.yaml | `E7_analysis.json:cells.B0p04.classes.n_classified` | `experiments/E7/analyze.py` | VERIFIED |  |
| 36 | `EsevenBallCollective` | $14$ | 1035 | e7.yaml | `E7_analysis.json:cells.B0p04.classes.counts.collective` | `experiments/E7/analyze.py` | VERIFIED |  |
| 37 | `EsevenBallK` | $85$ | 1035 | e7.yaml | `E7_analysis.json:cells.B0p04.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 38 | `EsevenBallTwoClassified` | $17$ | 1035 | e7.yaml | `E7_analysis.json:cells.B0p02.classes.n_classified` | `experiments/E7/analyze.py` | VERIFIED |  |
| 39 | `EsevenBallTwoCollective` | $17$ | 1035 | e7.yaml | `E7_analysis.json:cells.B0p02.classes.counts.collective` | `experiments/E7/analyze.py` | VERIFIED |  |
| 40 | `EsevenBallTwoK` | $83$ | 1035 | e7.yaml | `E7_analysis.json:cells.B0p02.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 41 | `EsevenBjambClassified` | $11$ | 1035 | e7.yaml | `E7_analysis.json:cells.Bedge0p04.classes.n_classified` | `experiments/E7/analyze.py` | VERIFIED |  |
| 42 | `EsevenBjambCollective` | $11$ | 1035 | e7.yaml | `E7_analysis.json:cells.Bedge0p04.classes.counts.collective` | `experiments/E7/analyze.py` | VERIFIED |  |
| 43 | `EsevenBjambK` | $89$ | 1035 | e7.yaml | `E7_analysis.json:cells.Bedge0p04.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 44 | `EsevenCollectiveP` | ${2.0\times10^{-13}}$ | 1035 | e7.yaml | `E7_analysis.json:locality.collective_default_vs_jamb_only.fisher_p` | `experiments/E7/analyze.py` | VERIFIED |  |
| 45 | `EsevenDefaultClassified` | $98$ | 1035 | e7.yaml | `E7_analysis.json:cells.default.classes.n_classified` | `experiments/E7/analyze.py` | VERIFIED |  |
| 46 | `EsevenDefaultCollective` | $2$ | 1035 | e7.yaml | `E7_analysis.json:cells.default.classes.counts.collective` | `experiments/E7/analyze.py` | VERIFIED |  |
| 47 | `EsevenJambVsAllP` | $0.529$ | 1035 | e7.yaml | `E7_analysis.json:locality.all_walls_B0p04_vs_jamb_only.fisher_p` | `experiments/E7/analyze.py` | VERIFIED |  |
| 48 | `EsevenJambVsDefaultP` | ${3.5\times10^{-41}}$ | 1035 | e7.yaml | `E7_analysis.json:locality.Bedge0p04_vs_default.fisher_p` | `experiments/E7/analyze.py` | VERIFIED |  |
| 49 | `EsevenLineK` | $3$ | 1035 | e7.yaml | `E7_analysis.json:cells.line.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 50 | `EsevenLineRoundK` | $9$ | 1035 | e7.yaml | `E7_analysis.json:cells.line_rounded.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 51 | `EsevenN` | $100$ | 1035 | e7.yaml | `E7_analysis.json:cells.default.n` | `experiments/E7/analyze.py` | VERIFIED |  |
| 52 | `EsevenRoundK` | $7$ | 1035 | e7.yaml | `E7_analysis.json:cells.rounded.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 53 | `EsevenRoundVsDefaultP` | $0.170$ | 1035 | e7.yaml | `E7_analysis.json:locality.rounded_vs_default.fisher_p` | `experiments/E7/analyze.py` | VERIFIED |  |
| 54 | `EsevenWEightK` | $2$ | 1035 | e7.yaml | `E7_analysis.json:cells.default.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 55 | `EsevenWNineHi` | $0.78$ | 1035 | e7.yaml | `E7_analysis.json:cells.w0p9.wilson95.1` | `experiments/E7/analyze.py` | VERIFIED |  |
| 56 | `EsevenWNineK` | $70$ | 1035 | e7.yaml | `E7_analysis.json:cells.w0p9.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 57 | `EsevenWNineLo` | $0.60$ | 1035 | e7.yaml | `E7_analysis.json:cells.w0p9.wilson95.0` | `experiments/E7/analyze.py` | VERIFIED |  |
| 58 | `EsevenWSevenK` | $0$ | 1035 | e7.yaml | `E7_analysis.json:cells.w0p7.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 59 | `EsevenWTenK` | $100$ | 1035 | e7.yaml | `E7_analysis.json:cells.w1p0.k_complete` | `experiments/E7/analyze.py` | VERIFIED |  |
| 60 | `EsevenWTenLo` | $0.96$ | 1035 | e7.yaml | `E7_analysis.json:cells.w1p0.wilson95.0` | `experiments/E7/analyze.py` | VERIFIED |  |
| 61 | `EsevenWcrit` | $0.88$ | 1035 | e7.yaml | `E7_analysis.json:critical_width.w50_logit` | `experiments/E7/analyze.py` | VERIFIED |  |
| 62 | `EsevenWcritHi` | $0.89$ | 1035 | e7.yaml | `E7_analysis.json:critical_width.w50_logit_ci95.1` | `experiments/E7/analyze.py` | VERIFIED |  |
| 63 | `EsevenWcritLo` | $0.87$ | 1035 | e7.yaml | `E7_analysis.json:critical_width.w50_logit_ci95.0` | `experiments/E7/analyze.py` | VERIFIED |  |
| 64 | `KeystoneACollective` | $5$ | 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.class_counts.E1a.collective` | `experiments/E1/chain.py` | VERIFIED |  |
| 65 | `KeystoneALone` | $38$ | 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.class_counts.E1a.lone_keystone` | `experiments/E1/chain.py` | VERIFIED |  |
| 66 | `KeystoneASecondTrap` | $154$ | 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.class_counts.E1a.lone_keystone_second_trap` | `experiments/E1/chain.py` | VERIFIED |  |
| 67 | `KeystoneBCollective` | $2$ | 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.class_counts.E1b.collective` | `experiments/E1/chain.py` | VERIFIED |  |
| 68 | `KeystoneBLone` | $34$ | 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.class_counts.E1b.lone_keystone` | `experiments/E1/chain.py` | VERIFIED |  |
| 69 | `KeystoneBSecondTrap` | $160$ | 1035 | core.yaml | `E1_chain.json:stuck_alone_criterion_check.class_counts.E1b.lone_keystone_second_trap` | `experiments/E1/chain.py` | VERIFIED |  |
| 70 | `SecondTrapHeld` | $296$ | 1035 | core.yaml | `E1_chain.json:second_trap_both_modes.K1b_held` | `experiments/E1/chain.py` | VERIFIED |  |
| 71 | `SecondTrapN` | $314$ | 1035 | core.yaml | `E1_chain.json:second_trap_both_modes.n` | `experiments/E1/chain.py` | VERIFIED |  |
| 72 | `ChainBlockerLastThree` | $184$ | 1037 | core.yaml | `E1_chain.json:E1b.a_blocker_arrival_rank_from_end.within_last_3` | `experiments/E1/chain.py` | VERIFIED |  |
| 73 | `ChainBlockerN` | $196$ | 1037 | core.yaml | `E1_chain.json:E1b.a_blocker_arrival_rank_from_end.n` | `experiments/E1/chain.py` | VERIFIED |  |
| 74 | `ChainNoPassableExited` | $141$ | 1037 | core.yaml | `E1_chain.json:E1b.b_passable_zero_vs_positive.passable0.exited` | `experiments/E1/chain.py` | VERIFIED |  |
| 75 | `ChainNoPassableN` | $288$ | 1037 | core.yaml | `E1_chain.json:E1b.b_passable_zero_vs_positive.passable0.n` | `experiments/E1/chain.py` | VERIFIED |  |
| 76 | `ChainStuckFirstDecile` | $0.20$ | 1037 | core.yaml | `E1_chain.json:E1b.a_stuck_fraction_by_arrival_decile.frac.0` | `experiments/E1/chain.py` | VERIFIED |  |
| 77 | `ChainStuckLastDecile` | $0.62$ | 1037 | core.yaml | `E1_chain.json:E1b.a_stuck_fraction_by_arrival_decile.frac.9` | `experiments/E1/chain.py` | VERIFIED |  |
| 78 | `EOneBAUCOthers` | $0.975$ | 1037 | core.yaml | `E1_chain.json:E1b.b_predictors.scores.others_active.auc` | `experiments/E1/chain.py` | VERIFIED |  |
| 79 | `EOneBAUCOthersHi` | $0.979$ | 1037 | core.yaml | `E1_chain.json:E1b.b_predictors.scores.others_active.ci95_seed_bootstrap.1` | `experiments/E1/chain.py` | VERIFIED |  |
| 80 | `EOneBAUCOthersLo` | $0.970$ | 1037 | core.yaml | `E1_chain.json:E1b.b_predictors.scores.others_active.ci95_seed_bootstrap.0` | `experiments/E1/chain.py` | VERIFIED |  |
| 81 | `EOneBAllExitBaseline` | $0.931$ | 1037 | core.yaml | `E1_analysis.json:E1b.k_rule_refined.all_exit_baseline_accuracy` | `experiments/E1/e1_analyze.py` | VERIFIED |  |
| 82 | `PairAxisMax` | $0.50$ | 1047 | pair.yaml | `E7b_analysis.json:a_statics.axis_dist_m.max` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 83 | `PairAxisMin` | $0.40$ | 1047 | pair.yaml | `E7b_analysis.json:a_statics.axis_dist_m.min` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 84 | `PairGapMax` | $0.33$ | 1047 | pair.yaml | `E7b_analysis.json:a_statics.pair_gap_m.max` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 85 | `PairGapMin` | $0.28$ | 1047 | pair.yaml | `E7b_analysis.json:a_statics.pair_gap_m.min` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 86 | `PairN` | $46$ | 1047, 1049, 1051, 1102, 1103, 1104, 1105, 1106, 1133, 1136, 1169, 1175 | pair.yaml | `E7b_analysis.json:n_snapshots` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 87 | `PairDeltaOneCmFreed` | $1$ | 1049 | pair.yaml | `E7b_analysis.json:b_s9b.delta0p01.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 88 | `PairDeltaOneMmFreed` | $0$ | 1049 | pair.yaml | `E7b_analysis.json:b_s9b.delta0p001.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 89 | `PairDeltaThreeCmFreed` | $10$ | 1049 | pair.yaml | `E7b_analysis.json:b_s9b.delta0p03.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 90 | `PairLamOneMax` | $121$ | 1049 | pair.yaml | `E7b_analysis.json:a_statics.lambda1.max` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 91 | `PairLamOneMed` | $94$ | 1049 | pair.yaml | `E7b_analysis.json:a_statics.lambda1.median` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 92 | `PairLamOneMin` | $65$ | 1049 | pair.yaml | `E7b_analysis.json:a_statics.lambda1.min` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 93 | `PairLamRatioMax` | $14$ | 1049 | pair.yaml | `E7b_analysis.json:a_statics.lambda2_over_lambda1.max` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 94 | `PairLamRatioMin` | $12$ | 1049 | pair.yaml | `E7b_analysis.json:a_statics.lambda2_over_lambda1.min` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 95 | `PairPerturbN` | $230$ | 1049 | pair.yaml | `E7b_analysis.json:b_s9b.perturb_1e9_C1.n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 96 | `PairResidMax` | ${1\times10^{-7}}$ | 1049 | pair.yaml | `E7b_analysis.json:a_statics.field_residual_max_N` | `experiments/E7b/analyze.py` | MISMATCH | data 1.39e-7, printed 1e-7 (M2) |
| 97 | `PairSoftCommon` | $46$ | 1049 | pair.yaml | `E7b_analysis.json:a_statics.softest_common_lateral` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 98 | `PairAsymCorr` | $0.9996$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_threshold.corr_asym_bstar_spearman` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 99 | `PairBiasOneFreed` | $8$ | 1051 | pair.yaml | `E7b_analysis.json:b_quench.bias0p01.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 100 | `PairBiasTenFreed` | $46$ | 1051 | pair.yaml | `E7b_analysis.json:b_quench.bias0p1.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 101 | `PairBstarMax` | $0.038$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_threshold.min_both_signs.max` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 102 | `PairBstarMed` | $0.016$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_threshold.min_both_signs.median` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 103 | `PairBstarMin` | $0.001$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_threshold.min_both_signs.min` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 104 | `PairFoldAgree` | $363$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_prediction.agree` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 105 | `PairFoldFN` | $5$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_prediction.FN` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 106 | `PairFoldLo` | $0.969$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_prediction.accuracy_wilson95.1` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 107 | `PairFoldMissGap` | $2$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_prediction.disagree_max_rel_gap_pct` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 108 | `PairFoldN` | $368$ | 1051 | pair.yaml | `E7b_analysis.json:a_statics.fold_prediction.n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 109 | `PairHandAll` | $202$ | 1051 | pair.yaml | `E7b_analysis.json:b_handedness.pooled.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 110 | `PairBarMax` | $1.1$ | 1053 | pair.yaml | `E7b_analysis.json:d_barriers.dU.max` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 111 | `PairBarMed` | $0.21$ | 1053 | pair.yaml | `E7b_analysis.json:d_barriers.dU.median` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 112 | `PairBarMin` | $0.06$ | 1053 | pair.yaml | `E7b_analysis.json:d_barriers.dU.min` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 113 | `PairBarN` | $12$ | 1053 | pair.yaml | `E7b_analysis.json:d_barriers.accepted` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 114 | `PairBarSpearman` | $-0.24$ | 1053 | pair.yaml | `E7b_analysis.json:d_barriers.spearman_lambda1_dU` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 115 | `PairNoiseLowFreed` | $224$ | 1053 | pair.yaml | `E7b_analysis.json:b_quench.noise0p01.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 116 | `PairNoiseLowN` | $230$ | 1053 | pair.yaml | `E7b_analysis.json:b_quench.noise0p01.n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 117 | `PairWeibHigh` | $2.8$ | 1053 | pair.yaml | `E7b_analysis.json:b_quench.noise0p05.weibull.k` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 118 | `PairWeibLow` | $2.3$ | 1053 | pair.yaml | `E7b_analysis.json:b_quench.noise0p01.weibull.k` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 119 | `ArchComplete` | $25$ | 1056 | e6_e10.yaml | `arch_analysis.json:complete` | `experiments/arch/analyze.py` | VERIFIED |  |
| 120 | `ArchEpisodes` | $103$ | 1056 | e6_e10.yaml | `arch_analysis.json:episodes` | `experiments/arch/analyze.py` | VERIFIED |  |
| 121 | `ArchEpisodesThree` | $93$ | 1056 | e6_e10.yaml | `arch_analysis.json:episodes_size3` | `experiments/arch/analyze.py` | VERIFIED |  |
| 122 | `ArchMaxLife` | $2.9$ | 1056 | e6_e10.yaml | `arch_analysis.json:max_lifetime_s` | `experiments/arch/analyze.py` | VERIFIED |  |
| 123 | `ArchN` | $25$ | 1056 | e6_e10.yaml | `arch_analysis.json:n_runs` | `experiments/arch/analyze.py` | VERIFIED |  |
| 124 | `ArchPNinetyFive` | $0.6$ | 1056 | e6_e10.yaml | `arch_analysis.json:p95_lifetime_s` | `experiments/arch/analyze.py` | VERIFIED |  |
| 125 | `ArchPeakForce` | $108$ | 1056 | e6_e10.yaml | `arch_analysis.json:peak_body_force_kN` | `experiments/arch/analyze.py` | VERIFIED |  |
| 126 | `ArchPersistent` | $0$ | 1056 | e6_e10.yaml | `arch_analysis.json:persistent_runs` | `experiments/arch/analyze.py` | VERIFIED |  |
| 127 | `ArchPersistentHi` | $0.13$ | 1056 | e6_e10.yaml | `arch_analysis.json:persistent_wilson95.1` | `experiments/arch/analyze.py` | VERIFIED |  |
| 128 | `ArchRunsWithArch` | $22$ | 1056 | e6_e10.yaml | `arch_analysis.json:runs_with_arch` | `experiments/arch/analyze.py` | VERIFIED |  |
| 129 | `ArchSizeMax` | $10$ | 1056 | e6_e10.yaml | `arch_analysis.json:size_max` | `experiments/arch/analyze.py` | VERIFIED |  |
| 130 | `ArchVZero` | $5$ | 1056 | e6_e10.yaml | `arch_analysis.json:v0_mean` | `experiments/arch/analyze.py` | VERIFIED |  |
| 131 | `EfourEventsAlone` | $554$ | 1065 | core.yaml | `E4_analysis.json:headline.events_alone` | `experiments/E4/analyze.py` | VERIFIED |  |
| 132 | `EfourEventsFrozen` | $581$ | 1065 | core.yaml | `E4_analysis.json:headline.events_frozen` | `experiments/E4/analyze.py` | VERIFIED |  |
| 133 | `EfourEventsFull` | $382$ | 1065 | core.yaml | `E4_analysis.json:headline.events_full` | `experiments/E4/analyze.py` | VERIFIED |  |
| 134 | `EfourN` | $10$ | 1065 | core.yaml | `E4_analysis.json:n_snapshots` | `experiments/E4/analyze.py` | VERIFIED |  |
| 135 | `EfourRestarts` | $20$ | 1065 | core.yaml | `E4_analysis.json:extension.n_restarts.full` | `experiments/E4/analyze.py` | VERIFIED |  |
| 136 | `EfourCollapseSlope` | $-0.93$ | 1067 | core.yaml | `E4_analysis.json:headline.collapse_slope` | `experiments/E4/analyze.py` | VERIFIED | renders text hyphen (L1) |
| 137 | `EfourCoverAlone` | $9$ | 1067 | core.yaml | `E4_analysis.json:headline.ratio_cover_alone` | `experiments/E4/analyze.py` | VERIFIED |  |
| 138 | `EfourCoverFrozen` | $9$ | 1067 | core.yaml | `E4_analysis.json:headline.ratio_cover_frozen` | `experiments/E4/analyze.py` | VERIFIED |  |
| 139 | `EfourCoverFull` | $7$ | 1067 | core.yaml | `E4_analysis.json:headline.ratio_cover_full` | `experiments/E4/analyze.py` | VERIFIED |  |
| 140 | `EfourFitsAlone` | $10$ | 1067 | core.yaml | `E4_analysis.json:headline.nfit_alone` | `experiments/E4/analyze.py` | VERIFIED |  |
| 141 | `EfourFitsFrozen` | $10$ | 1067 | core.yaml | `E4_analysis.json:headline.nfit_frozen` | `experiments/E4/analyze.py` | VERIFIED |  |
| 142 | `EfourFitsFull` | $8$ | 1067 | core.yaml | `E4_analysis.json:headline.nfit_full` | `experiments/E4/analyze.py` | VERIFIED |  |
| 143 | `EfourNonCoverA` | $0.54$ | 1067 | core.yaml | `E4_analysis.json:snapshots.E1b_seed61.conds.full.arrhenius.ratio` | `experiments/E4/analyze.py` | VERIFIED |  |
| 144 | `EfourNonCoverB` | $0.69$ | 1067 | core.yaml | `E4_analysis.json:snapshots.E1b_seed192.conds.frozen.arrhenius.ratio` | `experiments/E4/analyze.py` | VERIFIED |  |
| 145 | `EfourNonCoverC` | $0.61$ | 1067 | core.yaml | `E4_analysis.json:snapshots.E1b_seed192.conds.alone.arrhenius.ratio` | `experiments/E4/analyze.py` | VERIFIED |  |
| 146 | `EfourNuAlone` | $0.09$ | 1067 | core.yaml | `E4_analysis.json:per_condition.alone.nu_hat_median` | `experiments/E4/analyze.py` | VERIFIED |  |
| 147 | `EfourNuFull` | $0.13$ | 1067 | core.yaml | `E4_analysis.json:per_condition.full.nu_hat_median` | `experiments/E4/analyze.py` | VERIFIED |  |
| 148 | `EfourRatioAlone` | $0.87$ | 1067 | core.yaml | `E4_analysis.json:headline.ratio_med_alone` | `experiments/E4/analyze.py` | VERIFIED |  |
| 149 | `EfourRatioFrozen` | $0.95$ | 1067 | core.yaml | `E4_analysis.json:headline.ratio_med_frozen` | `experiments/E4/analyze.py` | VERIFIED |  |
| 150 | `EfourRatioFull` | $1.15$ | 1067 | core.yaml | `E4_analysis.json:headline.ratio_med_full` | `experiments/E4/analyze.py` | VERIFIED |  |
| 151 | `EfourSaddleBelow` | $10$ | 1067 | core.yaml | `E4_analysis.json:headline.saddle_below` | `experiments/E4/analyze.py` | VERIFIED |  |
| 152 | `EfourSaddleN` | $10$ | 1067 | core.yaml | `E4_analysis.json:headline.saddle_n` | `experiments/E4/analyze.py` | VERIFIED |  |
| 153 | `EfourSaddleRatio` | $0.30$ | 1067 | core.yaml | `E4_analysis.json:headline.saddle_ratio_med` | `experiments/E4/analyze.py` | VERIFIED | median includes seed60, seed170 (L19) |
| 154 | `EfourWeib` | $1.09$ | 1067 | core.yaml | `E4_analysis.json:headline.weib_all` | `experiments/E4/analyze.py` | VERIFIED |  |
| 155 | `EfourWeibHi` | $1.14$ | 1067 | core.yaml | `E4_analysis.json:headline.weib_all_hi` | `experiments/E4/analyze.py` | VERIFIED |  |
| 156 | `EfourWeibLo` | $1.05$ | 1067 | core.yaml | `E4_analysis.json:headline.weib_all_lo` | `experiments/E4/analyze.py` | VERIFIED | CI excludes 1 (L8) |
| 157 | `EfourSeedOneSeventyDU` | $0.13$ | 1069 | core.yaml | `E4_analysis.json:snapshots.E1b_seed170.conds.full.dU` | `experiments/E4/analyze.py` | VERIFIED |  |
| 158 | `EfourSeedOneSeventyEvents` | $0$ | 1069 | core.yaml | `E4_analysis.json:snapshots.E1b_seed170.conds.full.levels.b1p5.events` | `experiments/E4/analyze.py` | VERIFIED |  |
| 159 | `EfourSeedOneSeventyResid` | $4$ | 1069 | core.yaml | `E4_analysis.json:snapshots.E1b_seed170.n_resid` | `experiments/E4/analyze.py` | VERIFIED |  |
| 160 | `EfourSeedOneSeventyRestarts` | $20$ | 1069 | core.yaml | `E4_analysis.json:snapshots.E1b_seed170.conds.full.levels.b1p5.n` | `experiments/E4/analyze.py` | VERIFIED |  |
| 161 | `EfourSkippedDU` | $0.02$ | 1069 | core.yaml | `E4_analysis.json:extension.skipped_no_barrier.0.dU` | `experiments/E4/analyze.py` | VERIFIED |  |
| 162 | `EfiveASigmaFifty` | $0.045$ | 1071 | core.yaml | `E5a_analysis.json:logistic_core.sigma50` | `experiments/E5/analyze_e5a.py` | VERIFIED |  |
| 163 | `EfiveASigmaFiftyHi` | $0.047$ | 1071 | core.yaml | `E5a_analysis.json:logistic_core.ci95_profile.1` | `experiments/E5/analyze_e5a.py` | VERIFIED |  |
| 164 | `EfiveASigmaFiftyLo` | $0.042$ | 1071 | core.yaml | `E5a_analysis.json:logistic_core.ci95_profile.0` | `experiments/E5/analyze_e5a.py` | VERIFIED |  |
| 165 | `EfiveConfSigmaFifty` | $0.049$ | 1071 | core.yaml | `E5_analysis.json:conference_sigma50` | `experiments/E5/analyze.py` | VERIFIED |  |
| 166 | `EfiveN` | $100$ | 1071 | core.yaml | `E5_analysis.json:per_sigma.s0p03.n` | `experiments/E5/analyze.py` | VERIFIED |  |
| 167 | `EfiveSigmaFifty` | $0.044$ | 1071 | core.yaml | `E5_analysis.json:logistic_noise_levels.sigma50` | `experiments/E5/analyze.py` | VERIFIED |  |
| 168 | `EfiveSigmaFiftyHi` | $0.047$ | 1071 | core.yaml | `E5_analysis.json:logistic_noise_levels.ci95_profile.1` | `experiments/E5/analyze.py` | VERIFIED |  |
| 169 | `EfiveSigmaFiftyLo` | $0.041$ | 1071 | core.yaml | `E5_analysis.json:logistic_noise_levels.ci95_profile.0` | `experiments/E5/analyze.py` | VERIFIED |  |
| 170 | `EtwoNLK` | $34$ | 1094, 1111 | core.yaml | `E2_analysis.json:n_snapshots.lone_keystone` | `experiments/E2/analyze.py` | VERIFIED |  |
| 171 | `EthreeEllBA` | $2.16$ | 1095, 1117 | core.yaml | `E3_analysis.json:headline.ell_ps_b1p5_obs` | `experiments/E3/analyze.py` | MISMATCH | E3 per-step noise at beta_ref 1.5, shown in sigma=0.07 row of Table 3 (H1); correct at 1117 |
| 172 | `EthreeEllBAPred` | $2.22$ | 1095, 1117 | core.yaml | `E3_analysis.json:headline.ell_ps_b1p5_pred` | `experiments/E3/analyze.py` | MISMATCH | as EthreeEllBA (H1); correct at 1117 |
| 173 | `EtwoLKJaccardC` | $0.20$ | 1095, 1163 | core.yaml | `E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.jaccard` | `experiments/E2/analyze.py` | VERIFIED |  |
| 174 | `EtwoLKJaccardCHi` | $0.50$ | 1095 | core.yaml | `E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.jaccard_ci95_boot.1` | `experiments/E2/analyze.py` | VERIFIED |  |
| 175 | `EtwoLKJaccardCLo` | $0.00$ | 1095 | core.yaml | `E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.jaccard_ci95_boot.0` | `experiments/E2/analyze.py` | VERIFIED |  |
| 176 | `EtwoLKNoiseCFreed` | $148$ | 1095 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.noise0p07.freed` | `experiments/E2/analyze.py` | VERIFIED |  |
| 177 | `EtwoLKNoiseCN` | $170$ | 1095 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.noise0p07.n` | `experiments/E2/analyze.py` | VERIFIED |  |
| 178 | `TabThreeLKDiff` | $-0.01$ | 1095, 1163 | core.yaml | `E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.paired_rate_diff_noise_minus_C3` | `experiments/E2/analyze.py` | VERIFIED |  |
| 179 | `TabThreeLKDiffHi` | $0.08$ | 1095 | core.yaml | `E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.paired_rate_diff_ci95_boot.1` | `experiments/E2/analyze.py` | VERIFIED |  |
| 180 | `TabThreeLKDiffLo` | $-0.10$ | 1095 | core.yaml | `E2_analysis.json:f_noise_vs_C3.lone_keystone.noise0p07.paired_rate_diff_ci95_boot.0` | `experiments/E2/analyze.py` | VERIFIED |  |
| 181 | `TabThreeLKNoiseDisagree` | $9$ | 1095 | core.yaml | `E2_analysis.json:b_replay_determinism.lone_keystone.noise0p07.seeds_disagree_on_freed` | `experiments/E2/analyze.py` | VERIFIED |  |
| 182 | `TabThreeLKNoiseMed` | $19.8$ | 1095 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.noise0p07.time_to_free_km.median` | `experiments/E2/analyze.py` | VERIFIED |  |
| 183 | `TabThreeLKNoiseSnaps` | $34$ | 1095 | core.yaml | `E2_analysis.json:b_replay_determinism.lone_keystone.noise0p07.snapshots` | `experiments/E2/analyze.py` | VERIFIED |  |
| 184 | `EthreeCThreeLnRatio` | ${-4.8\times10^{-3}}$ | 1096 | core.yaml | `E3_analysis.json:headline.c3_ln_ratio` | `experiments/E3/analyze.py` | VERIFIED |  |
| 185 | `EtwoLKCThreeRVOFreed` | $30$ | 1096, 1111 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.C3_rvo2.freed` | `experiments/E2/analyze.py` | VERIFIED |  |
| 186 | `EtwoLKCThreeRVON` | $34$ | 1096, 1111 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.C3_rvo2.n` | `experiments/E2/analyze.py` | VERIFIED |  |
| 187 | `TabThreeLKRvoMed` | $1.5$ | 1096 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.C3_rvo2.time_to_free_km.median` | `experiments/E2/analyze.py` | VERIFIED |  |
| 188 | `TabThreeLKRvoReplayDis` | $0$ | 1096 | core.yaml | `E2_analysis.json:b_replay_determinism.lone_keystone.C3_rvo2.freed_disagree` | `experiments/E2/analyze.py` | VERIFIED |  |
| 189 | `TabThreeLKRvoReplays` | $170$ | 1096 | core.yaml | `E2_analysis.json:b_replay_determinism.lone_keystone.C3_rvo2.replays` | `experiments/E2/analyze.py` | VERIFIED |  |
| 190 | `EsixN` | $186$ | 1098, 1099, 1100 | e6_e10.yaml | `E6_analysis.json:n` | `experiments/E6/analyze.py` | VERIFIED |  |
| 191 | `EsixDiff` | $-0.01$ | 1099, 1163 | e6_e10.yaml | `E6_analysis.json:completion.diff_sigma_minus_C3.diff` | `experiments/E6/analyze.py` | VERIFIED |  |
| 192 | `EsixDiffHi` | $0.08$ | 1099, 1163 | e6_e10.yaml | `E6_analysis.json:completion.diff_sigma_minus_C3.ci95.1` | `experiments/E6/analyze.py` | VERIFIED |  |
| 193 | `EsixDiffLo` | $-0.10$ | 1099, 1163 | e6_e10.yaml | `E6_analysis.json:completion.diff_sigma_minus_C3.ci95.0` | `experiments/E6/analyze.py` | VERIFIED | renders text hyphen (L1) |
| 194 | `EsixJaccard` | $0.41$ | 1099, 1123, 1163 | e6_e10.yaml | `E6_analysis.json:identity.jaccard` | `experiments/E6/analyze.py` | VERIFIED | p_perm 0.002 omitted (M6) |
| 195 | `EsixJaccardHi` | $0.50$ | 1099 | e6_e10.yaml | `E6_analysis.json:identity.jaccard_ci95.1` | `experiments/E6/analyze.py` | VERIFIED |  |
| 196 | `EsixJaccardLo` | $0.32$ | 1099 | e6_e10.yaml | `E6_analysis.json:identity.jaccard_ci95.0` | `experiments/E6/analyze.py` | VERIFIED |  |
| 197 | `EsixKMNoise` | $469$ | 1099 | e6_e10.yaml | `E6_analysis.json:time.km_C1_sigma.median` | `experiments/E6/analyze.py` | VERIFIED |  |
| 198 | `EsixNoiseK` | $99$ | 1099 | e6_e10.yaml | `E6_analysis.json:completion.C1_sigma.k` | `experiments/E6/analyze.py` | VERIFIED |  |
| 199 | `EsixCThreeK` | $101$ | 1100 | e6_e10.yaml | `E6_analysis.json:completion.C3_rvo2.k` | `experiments/E6/analyze.py` | VERIFIED |  |
| 200 | `EsixKMCThree` | $132$ | 1100 | e6_e10.yaml | `E6_analysis.json:time.km_C3_rvo2.median` | `experiments/E6/analyze.py` | VERIFIED |  |
| 201 | `PairBsPubFreed` | $22$ | 1103 | pair.yaml | `E7b_analysis.json:s3_matched.pub.rate.freed_a` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 202 | `PairBsPubHand` | $22$ | 1103 | pair.yaml | `E7b_analysis.json:s3_matched.pub.handedness.plus_lower_first` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 203 | `PairBsPubJac` | $0.43$ | 1103, 1136, 1163 | pair.yaml | `E7b_analysis.json:s3_matched.pub.jaccard_freed.value` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 204 | `PairBsPubJacHi` | $0.61$ | 1103, 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.jaccard_freed.ci95.1` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 205 | `PairBsPubJacLo` | $0.26$ | 1103, 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.jaccard_freed.ci95.0` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 206 | `PairBsPubN` | $22$ | 1103 | pair.yaml | `E7b_analysis.json:s3_matched.pub.handedness.plus_n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 207 | `PairBstarPub` | $0.0223$ | 1103 | pair.yaml | `E7b_analysis.json:s3_matched.pub.b_star` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 208 | `TabThreePairBsPubReplayDis` | $0$ | 1103 | core.yaml | `E7b_analysis.json:s3_matched.pub.replay.plus.discordant` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 209 | `TabThreePairBsReplays` | $230$ | 1103, 1105 | core.yaml | `E7b_analysis.json:s3_matched.pub.replay.plus.replays` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 210 | `TabThreePairPubDiff` | $+0.02$ | 1103 | core.yaml | `table3_pair.json:pub.diff` | `experiments/tables/make_table3.py derive` | VERIFIED |  |
| 211 | `TabThreePairPubDiffHi` | $0.22$ | 1103 | core.yaml | `table3_pair.json:pub.diff_ci95.1` | `experiments/tables/make_table3.py derive` | VERIFIED |  |
| 212 | `TabThreePairPubDiffLo` | $-0.15$ | 1103 | core.yaml | `table3_pair.json:pub.diff_ci95.0` | `experiments/tables/make_table3.py derive` | VERIFIED |  |
| 213 | `PairPubFreed` | $21$ | 1104, 1133, 1169 | pair.yaml | `E7b_analysis.json:b_quench.C3_pub.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 214 | `PairPubLower` | $11$ | 1104 | pair.yaml | `E7b_analysis.json:b_quench.C3_pub.first_lower` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 215 | `TabThreePairOrcaReplays` | $230$ | 1104, 1106 | core.yaml | `E7b_analysis.json:b_quench.C3_rvo2.replays` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 216 | `TabThreePairPubOrcaN` | $21$ | 1104 | core.yaml | `E7b_analysis.json:s3_matched.pub.handedness.orca_n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 217 | `TabThreePairPubReplayDis` | $0$ | 1104 | core.yaml | `E7b_analysis.json:b_quench.C3_pub.replay_discordant_snapshots` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 218 | `PairBsRvoFreed` | $8$ | 1105 | pair.yaml | `E7b_analysis.json:s3_matched.rvo2.rate.freed_a` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 219 | `PairBstarRvo` | $0.0091$ | 1105 | pair.yaml | `E7b_analysis.json:s3_matched.rvo2.b_star` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 220 | `TabThreePairBsRvoReplayDis` | $0$ | 1105 | core.yaml | `E7b_analysis.json:s3_matched.rvo2.replay.plus.discordant` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 221 | `TabThreePairRvoDiff` | $+0.02$ | 1105 | core.yaml | `table3_pair.json:rvo2.diff` | `experiments/tables/make_table3.py derive` | VERIFIED |  |
| 222 | `TabThreePairRvoDiffHi` | $0.17$ | 1105 | core.yaml | `table3_pair.json:rvo2.diff_ci95.1` | `experiments/tables/make_table3.py derive` | VERIFIED |  |
| 223 | `TabThreePairRvoDiffLo` | $-0.13$ | 1105 | core.yaml | `table3_pair.json:rvo2.diff_ci95.0` | `experiments/tables/make_table3.py derive` | VERIFIED |  |
| 224 | `TabThreePairRvoHand` | $8$ | 1105 | core.yaml | `E7b_analysis.json:s3_matched.rvo2.handedness.plus_lower_first` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 225 | `TabThreePairRvoHandN` | $8$ | 1105 | core.yaml | `E7b_analysis.json:s3_matched.rvo2.handedness.plus_n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 226 | `TabThreePairRvoJacF` | $0.00$ | 1105, 1163 | core.yaml | `E7b_analysis.json:s3_matched.rvo2.jaccard_freed.value` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 227 | `TabThreePairRvoJacFHi` | $0.00$ | 1105 | core.yaml | `E7b_analysis.json:s3_matched.rvo2.jaccard_freed.ci95.1` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 228 | `TabThreePairRvoJacFLo` | $0.00$ | 1105 | core.yaml | `E7b_analysis.json:s3_matched.rvo2.jaccard_freed.ci95.0` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 229 | `PairRvoFreed` | $7$ | 1106, 1133, 1169 | pair.yaml | `E7b_analysis.json:b_quench.C3_rvo2.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 230 | `TabThreePairRvoOrcaLower` | $2$ | 1106 | core.yaml | `E7b_analysis.json:s3_matched.rvo2.handedness.orca_lower_first` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 231 | `TabThreePairRvoOrcaN` | $7$ | 1106 | core.yaml | `E7b_analysis.json:s3_matched.rvo2.handedness.orca_n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 232 | `TabThreePairRvoReplayDis` | $0$ | 1106 | core.yaml | `E7b_analysis.json:b_quench.C3_rvo2.replay_discordant_snapshots` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 233 | `EtwoLKConstrRVOFreed` | $0$ | 1111 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.constraint_only_rvo2.freed` | `experiments/E2/analyze.py` | VERIFIED |  |
| 234 | `EtwoLKDriveVsPubDiscA` | $0$ | 1111 | core.yaml | `E2_analysis.json:d_orca_decomposition.lone_keystone.drive_only_vs_C3_pub.discordant_first_only` | `experiments/E2/analyze.py` | VERIFIED |  |
| 235 | `EtwoLKDriveVsPubDiscB` | $0$ | 1111 | core.yaml | `E2_analysis.json:d_orca_decomposition.lone_keystone.drive_only_vs_C3_pub.discordant_second_only` | `experiments/E2/analyze.py` | VERIFIED |  |
| 236 | `EtwoLKDriveVsRVODiscA` | $0$ | 1111 | core.yaml | `E2_analysis.json:d_orca_decomposition.lone_keystone.drive_only_vs_C3_rvo2.discordant_first_only` | `experiments/E2/analyze.py` | VERIFIED |  |
| 237 | `EtwoLKDriveVsRVODiscB` | $0$ | 1111 | core.yaml | `E2_analysis.json:d_orca_decomposition.lone_keystone.drive_only_vs_C3_rvo2.discordant_second_only` | `experiments/E2/analyze.py` | VERIFIED |  |
| 238 | `EtwoLKFrozenMinusFreed` | $0$ | 1111 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.frozen_minus.freed` | `experiments/E2/analyze.py` | VERIFIED |  |
| 239 | `EtwoLKFrozenPlusFreed` | $31$ | 1111 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.frozen_plus.freed` | `experiments/E2/analyze.py` | VERIFIED |  |
| 240 | `EtwoLKMarginAUC` | $0.98$ | 1111 | core.yaml | `E2_analysis.json:f_noise_vs_C3.lone_keystone.margin_predicts_C3_rvo2_failure.auc_margin_C3` | `experiments/E2/analyze.py` | VERIFIED |  |
| 241 | `EtwoLemmaIdentical` | $360$ | 1111 | core.yaml | `E2_analysis.json:c_rest_state_lemma_C2_vs_C1.identical_exits` | `experiments/E2/analyze.py` | VERIFIED |  |
| 242 | `EtwoLemmaPairs` | $360$ | 1111 | core.yaml | `E2_analysis.json:c_rest_state_lemma_C2_vs_C1.pairs` | `experiments/E2/analyze.py` | VERIFIED |  |
| 243 | `EtwoNAll` | $60$ | 1111 | core.yaml | `E2_analysis.json:n_snapshots.pooled` | `experiments/E2/analyze.py` | VERIFIED |  |
| 244 | `EtwoNST` | $26$ | 1111 | core.yaml | `E2_analysis.json:n_snapshots.lone_keystone_second_trap` | `experiments/E2/analyze.py` | VERIFIED |  |
| 245 | `EtwoReplayCThreeRVOMaxDt` | $0.000$ | 1111 | core.yaml | `E2_analysis.json:b_replay_determinism.pooled.C3_rvo2.max_abs_dt_blocker_exit_s` | `experiments/E2/analyze.py` | VERIFIED |  |
| 246 | `EtwoReplayN` | $300$ | 1111, 1120, 1169 | core.yaml | `E2_analysis.json:b_replay_determinism.pooled.C3_pub.replays` | `experiments/E2/analyze.py` | VERIFIED | value right; key is C3_pub, used for RVO2 at 1111 (L12) |
| 247 | `EtwoMaxBiasUpperLK` | $0.10$ | 1114 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone.bias0p5.rate_wilson95.2` | `experiments/E2/analyze.py` | VERIFIED |  |
| 248 | `EtwoNoiseSDC` | $11.2$ | 1114 | core.yaml | `E2_analysis.json:b_replay_determinism.pooled.noise0p07.within_snapshot_sd_first_exit_s.median` | `experiments/E2/analyze.py` | MISMATCH | pooled 59 snapshots; lone-keystone value 13.3 (M11) |
| 249 | `EthreeCThreeFreed` | $16$ | 1117 | core.yaml | `E3_analysis.json:headline.c3_n_freed` | `experiments/E3/analyze.py` | VERIFIED |  |
| 250 | `EthreeCThreeLnRatioMax` | $0.018$ | 1117 | core.yaml | `E3_analysis.json:headline.c3_ln_ratio_maxabs` | `experiments/E3/analyze.py` | VERIFIED |  |
| 251 | `EthreeEllBAHi` | $2.70$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ps_b1p5_hi` | `experiments/E3/analyze.py` | VERIFIED |  |
| 252 | `EthreeEllBALo` | $1.80$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ps_b1p5_lo` | `experiments/E3/analyze.py` | VERIFIED |  |
| 253 | `EthreeEllBB` | $3.23$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ps_b2p5_obs` | `experiments/E3/analyze.py` | VERIFIED |  |
| 254 | `EthreeEllBBHi` | $3.52$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ps_b2p5_hi` | `experiments/E3/analyze.py` | VERIFIED |  |
| 255 | `EthreeEllBBLo` | $2.96$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ps_b2p5_lo` | `experiments/E3/analyze.py` | VERIFIED |  |
| 256 | `EthreeEllBBPred` | $3.70$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ps_b2p5_pred` | `experiments/E3/analyze.py` | VERIFIED |  |
| 257 | `EthreeEllScaled` | $-0.09$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ds_obs` | `experiments/E3/analyze.py` | VERIFIED |  |
| 258 | `EthreeEllScaledHi` | $0.05$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ds_hi` | `experiments/E3/analyze.py` | VERIFIED |  |
| 259 | `EthreeEllScaledLo` | $-0.22$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ds_lo` | `experiments/E3/analyze.py` | VERIFIED |  |
| 260 | `EthreeEllScaledPred` | $-0.03$ | 1117 | core.yaml | `E3_analysis.json:headline.ell_ds_pred` | `experiments/E3/analyze.py` | VERIFIED |  |
| 261 | `EthreeN` | $20$ | 1117 | core.yaml | `E3_analysis.json:n_snapshots` | `experiments/E3/analyze.py` | VERIFIED |  |
| 262 | `EthreeSlope` | $0.91$ | 1117 | core.yaml | `E3_analysis.json:headline.slope_origin` | `experiments/E3/analyze.py` | VERIFIED |  |
| 263 | `EthreeSlopeHi` | $1.01$ | 1117 | core.yaml | `E3_analysis.json:headline.slope_origin_hi` | `experiments/E3/analyze.py` | VERIFIED |  |
| 264 | `EthreeSlopeLo` | $0.83$ | 1117 | core.yaml | `E3_analysis.json:headline.slope_origin_lo` | `experiments/E3/analyze.py` | VERIFIED |  |
| 265 | `CtwsixDriveFreed` | $9$ | 1120 | pair.yaml | `E7b_analysis.json:e_c26.second_trap_one_neighbour.drive_only_freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 266 | `CtwsixGapMax` | $0.32$ | 1120 | pair.yaml | `E7b_analysis.json:e_c26.second_trap_one_neighbour.gap_m.max` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 267 | `CtwsixGapMin` | $0.27$ | 1120 | pair.yaml | `E7b_analysis.json:e_c26.second_trap_one_neighbour.gap_m.min` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 268 | `CtwsixN` | $10$ | 1120 | pair.yaml | `E7b_analysis.json:e_c26.second_trap_one_neighbour.n` | `experiments/E7b/analyze.py` | VERIFIED | geometry holds 9/10 (M1) |
| 269 | `EtwoReplayCThreePubFlips` | $5$ | 1120, 1169 | core.yaml | `E2_analysis.json:b_replay_determinism.pooled.C3_pub.freed_disagree` | `experiments/E2/analyze.py` | VERIFIED |  |
| 270 | `EtwoReplayCThreePubMaxDt` | $80.8$ | 1120 | core.yaml | `E2_analysis.json:b_replay_determinism.pooled.C3_pub.max_abs_dt_blocker_exit_s` | `experiments/E2/analyze.py` | VERIFIED |  |
| 271 | `EtwoSTCThreeRVOFreed` | $17$ | 1120 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone_second_trap.C3_rvo2.freed` | `experiments/E2/analyze.py` | VERIFIED |  |
| 272 | `EtwoSTCThreeRVON` | $26$ | 1120 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone_second_trap.C3_rvo2.n` | `experiments/E2/analyze.py` | VERIFIED |  |
| 273 | `EtwoSTDriveFreed` | $24$ | 1120 | core.yaml | `E2_analysis.json:a_rates_time_to_free.lone_keystone_second_trap.drive_only.freed` | `experiments/E2/analyze.py` | VERIFIED |  |
| 274 | `EtwoSTDriveVsRVODiscA` | $7$ | 1120 | core.yaml | `E2_analysis.json:d_orca_decomposition.lone_keystone_second_trap.drive_only_vs_C3_rvo2.discordant_first_only` | `experiments/E2/analyze.py` | VERIFIED |  |
| 275 | `EtwoSTDriveVsRVODiscB` | $0$ | 1120 | core.yaml | `E2_analysis.json:d_orca_decomposition.lone_keystone_second_trap.drive_only_vs_C3_rvo2.discordant_second_only` | `experiments/E2/analyze.py` | VERIFIED |  |
| 276 | `EtwoSTDriveVsRVOP` | $0.016$ | 1120 | core.yaml | `E2_analysis.json:d_orca_decomposition.lone_keystone_second_trap.drive_only_vs_C3_rvo2.mcnemar_exact_p` | `experiments/E2/analyze.py` | VERIFIED |  |
| 277 | `PairTraceCancel` | $0.26$ | 1120 | pair.yaml | `E7b_analysis.json:e_c26.pair_library.trace.cancel_frac_mean_held.median` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 278 | `StClusterFreed` | $15$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.pair_vs_cluster.table.1.0` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 279 | `StClusterHeld` | $1$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.pair_vs_cluster.table.1.1` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 280 | `StHeldCancel` | $0.27$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.trace.rvo2.held.cancel_frac_mean.median` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 281 | `StHeldConsMean` | $-49$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.trace.rvo2.held.cons_x_mean.median` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 282 | `StHeldConsMin` | $-138$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.trace.rvo2.held.cons_x_min.median` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 283 | `StPairFisherP` | ${2.3\times10^{-4}}$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.pair_vs_cluster.fisher_p` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 284 | `StPairFreed` | $2$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.pair_vs_cluster.table.0.0` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 285 | `StPairHeld` | $8$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.pair_vs_cluster.table.0.1` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 286 | `StPairedDelay` | $0.25$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.time_to_free.paired_C3rvo2_minus_drive.median_s` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 287 | `StPairedN` | $17$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.time_to_free.paired_C3rvo2_minus_drive.n` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 288 | `StPairedSlower` | $17$ | 1120 | core.yaml | `E2_second_trap.json:strata.lone_keystone_second_trap.time_to_free.paired_C3rvo2_minus_drive.C3_slower` | `experiments/E2/second_trap.py` | VERIFIED |  |
| 289 | `EsixBarrierN` | $56$ | 1123 | e6_e10.yaml | `E6_analysis.json:lifetimes.barrier_picture.n_barriers` | `experiments/E6/analyze.py` | VERIFIED |  |
| 290 | `EsixCThreeFailMoving` | $54$ | 1123 | e6_e10.yaml | `E6_analysis.json:failure_state.C3_rvo2.moving_at_600s` | `experiments/E6/analyze.py` | VERIFIED |  |
| 291 | `EsixCThreeFailRest` | $31$ | 1123 | e6_e10.yaml | `E6_analysis.json:failure_state.C3_rvo2.stationary_deadlock` | `experiments/E6/analyze.py` | VERIFIED |  |
| 292 | `EsixCThreeMaxT` | $161$ | 1123 | e6_e10.yaml | `E6_analysis.json:time.completed_max_C3_rvo2` | `experiments/E6/analyze.py` | VERIFIED |  |
| 293 | `EsixCThreeMovingSecond` | $51$ | 1123 | e6_e10.yaml | `E6_analysis.json:failure_state.C3_rvo2.class_counts_moving.lone_keystone_second_trap` | `experiments/E6/analyze.py` | VERIFIED |  |
| 294 | `EsixCThreeOnlyFail` | $35$ | 1123 | e6_e10.yaml | `E6_analysis.json:identity.C3_only_fail` | `experiments/E6/analyze.py` | VERIFIED |  |
| 295 | `EsixClassP` | ${1.4\times10^{-3}}$ | 1123 | e6_e10.yaml | `E6_analysis.json:failure_state.class_test.p_perm` | `experiments/E6/analyze.py` | VERIFIED |  |
| 296 | `EsixJaccardIndep` | $0.30$ | 1123, 1163 | e6_e10.yaml | `E6_analysis.json:identity.jaccard_independent_mean` | `experiments/E6/analyze.py` | VERIFIED | p_perm 0.002 omitted (M6) |
| 297 | `EsixMcNemarP` | $0.906$ | 1123 | e6_e10.yaml | `E6_analysis.json:identity.mcnemar_exact_p` | `experiments/E6/analyze.py` | VERIFIED |  |
| 298 | `EsixNoiseCollective` | $0$ | 1123 | e6_e10.yaml | `E6_analysis.json:failure_state.C1_sigma.class_counts.collective` | `experiments/E6/analyze.py` | VERIFIED |  |
| 299 | `EsixNoiseLate` | $25$ | 1123 | e6_e10.yaml | `E6_analysis.json:time.completed_after_300s_C1_sigma` | `experiments/E6/analyze.py` | VERIFIED |  |
| 300 | `EsixNoiseLone` | $56$ | 1123 | e6_e10.yaml | `E6_analysis.json:failure_state.C1_sigma.class_counts.lone_keystone` | `experiments/E6/analyze.py` | VERIFIED |  |
| 301 | `EsixNoiseOnlyFail` | $37$ | 1123 | e6_e10.yaml | `E6_analysis.json:identity.sigma_only_fail` | `experiments/E6/analyze.py` | VERIFIED |  |
| 302 | `EsixNoiseSecond` | $31$ | 1123 | e6_e10.yaml | `E6_analysis.json:failure_state.C1_sigma.class_counts.lone_keystone_second_trap` | `experiments/E6/analyze.py` | VERIFIED |  |
| 303 | `EsixPairedCThreeFaster` | $64$ | 1123 | e6_e10.yaml | `E6_analysis.json:time.paired_C3_faster_n` | `experiments/E6/analyze.py` | VERIFIED |  |
| 304 | `EsixPairedDelay` | $66$ | 1123 | e6_e10.yaml | `E6_analysis.json:time.paired_median_diff_sigma_minus_C3` | `experiments/E6/analyze.py` | VERIFIED |  |
| 305 | `EsixSigmaStar` | $0.0467$ | 1123 | e6_e10.yaml | `E6_analysis.json:sigma_star` | `experiments/E6/analyze.py` | VERIFIED |  |
| 306 | `EsixStallMaxDiff` | $0.05$ | 1123 | e6_e10.yaml | `E6_analysis.json:lifetimes.pred_vs_obs.max_abs_diff` | `experiments/E6/analyze.py` | VERIFIED |  |
| 307 | `EsixStallMedObs` | $59$ | 1123 | e6_e10.yaml | `E6_analysis.json:lifetimes.pred_vs_obs.median_obs_km_s` | `experiments/E6/analyze.py` | VERIFIED |  |
| 308 | `EsixStallMedPred` | $69$ | 1123 | e6_e10.yaml | `E6_analysis.json:lifetimes.pred_vs_obs.median_pred_s` | `experiments/E6/analyze.py` | VERIFIED |  |
| 309 | `EsixStallWeib` | $0.64$ | 1123 | e6_e10.yaml | `E6_analysis.json:lifetimes.weibull.k` | `experiments/E6/analyze.py` | VERIFIED |  |
| 310 | `EsixStallWeibHi` | $0.70$ | 1123 | e6_e10.yaml | `E6_analysis.json:lifetimes.weibull.ci95.1` | `experiments/E6/analyze.py` | VERIFIED |  |
| 311 | `EsixStallWeibLo` | $0.58$ | 1123 | e6_e10.yaml | `E6_analysis.json:lifetimes.weibull.ci95.0` | `experiments/E6/analyze.py` | VERIFIED |  |
| 312 | `EsixStalls` | $349$ | 1123 | e6_e10.yaml | `E6_analysis.json:lifetimes.n_stalls` | `experiments/E6/analyze.py` | VERIFIED |  |
| 313 | `PairConsPubFreed` | $45$ | 1133 | pair.yaml | `E7b_analysis.json:b_quench.constraint_only_pub.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 314 | `PairConsRvoFreed` | $44$ | 1133 | pair.yaml | `E7b_analysis.json:b_quench.constraint_only_rvo2.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 315 | `PairDriveFreed` | $33$ | 1133 | pair.yaml | `E7b_analysis.json:b_quench.drive_only.freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 316 | `PairDriveRvoA` | $28$ | 1133 | pair.yaml | `E7b_analysis.json:c_decomposition.drive_vs_rvo2.disc_a_only` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 317 | `PairDriveRvoB` | $2$ | 1133 | pair.yaml | `E7b_analysis.json:c_decomposition.drive_vs_rvo2.disc_b_only` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 318 | `PairDriveRvoP` | ${8.7\times10^{-7}}$ | 1133 | pair.yaml | `E7b_analysis.json:c_decomposition.drive_vs_rvo2.mcnemar_p` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 319 | `PairPubRvoA` | $14$ | 1133 | pair.yaml | `E7b_analysis.json:c_decomposition.pub_vs_rvo2.disc_a_only` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 320 | `PairPubRvoB` | $0$ | 1133 | pair.yaml | `E7b_analysis.json:c_decomposition.pub_vs_rvo2.disc_b_only` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 321 | `PairPubRvoP` | ${1.2\times10^{-4}}$ | 1133 | pair.yaml | `E7b_analysis.json:c_decomposition.pub_vs_rvo2.mcnemar_p` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 322 | `PairReplayN` | $5520$ | 1133 | pair.yaml | `E7b_analysis.json:c_decomposition.replay_all_det_n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 323 | `PairBsPubBoth` | $13$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.jaccard_freed.both_freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 324 | `PairBsPubEither` | $30$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.jaccard_freed.either_freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 325 | `PairBsPubMinusFreed` | $21$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.handedness.minus_n` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 326 | `PairBsPubMinusUpper` | $21$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.handedness.minus_upper_first` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 327 | `PairBsPubP` | $1.000$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.rate.mcnemar_p` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 328 | `PairBsPubRevA` | $13$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.reversal.disc_a_only` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 329 | `PairBsPubRevB` | $14$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.pub.reversal.disc_b_only` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 330 | `PairBsRvoEither` | $15$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.rvo2.jaccard_freed.either_freed` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 331 | `PairBsRvoP` | $1.000$ | 1136 | pair.yaml | `E7b_analysis.json:s3_matched.rvo2.rate.mcnemar_p` | `experiments/E7b/analyze.py` | VERIFIED |  |
| 332 | `EtenHumanN` | $5$ | 1151, 1157 | e6_e10.yaml | `E10_analysis.json:humans.n_runs` | `experiments/E10/analyze.py` | VERIFIED |  |
| 333 | `EtenHumanFlow` | $1.48$ | 1154 | e6_e10.yaml | `E10_analysis.json:humans.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 334 | `EtenHumanFlowHi` | $1.74$ | 1154 | e6_e10.yaml | `E10_analysis.json:humans.flow.ci95.1` | `experiments/E10/analyze.py` | VERIFIED |  |
| 335 | `EtenHumanFlowLo` | $1.22$ | 1154 | e6_e10.yaml | `E10_analysis.json:humans.flow.ci95.0` | `experiments/E10/analyze.py` | VERIFIED |  |
| 336 | `EtenHumanFlowMax` | $1.71$ | 1154 | e6_e10.yaml | `E10_analysis.json:humans.flow_range.1` | `experiments/E10/analyze.py` | VERIFIED |  |
| 337 | `EtenHumanFlowMin` | $1.15$ | 1154 | e6_e10.yaml | `E10_analysis.json:humans.flow_range.0` | `experiments/E10/analyze.py` | VERIFIED |  |
| 338 | `EtenHumanFluct` | $0.074$ | 1154, 1157 | e6_e10.yaml | `E10_analysis.json:humans.fluct.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 339 | `EtenHumanFluctHi` | $0.079$ | 1154 | e6_e10.yaml | `E10_analysis.json:humans.fluct.ci95.1` | `experiments/E10/analyze.py` | VERIFIED |  |
| 340 | `EtenHumanFluctLo` | $0.070$ | 1154 | e6_e10.yaml | `E10_analysis.json:humans.fluct.ci95.0` | `experiments/E10/analyze.py` | VERIFIED |  |
| 341 | `EtenHumanGapMax` | $2.0$ | 1154 | e6_e10.yaml | `E10_analysis.json:humans.longest_gap_max` | `experiments/E10/analyze.py` | MISMATCH | data 2.04; "never exceeds 2.0" (M3) |
| 342 | `EtenHumanGapsTwo` | $0.2$ | 1154, 1157 | e6_e10.yaml | `E10_analysis.json:humans.gaps_gt_2s.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 343 | `EtenLongHumanFlow` | $1.32$ | 1154, 1157 | e6_e10.yaml | `E10_analysis.json:by_L.L2p0.humans.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 344 | `EtenShortHumanFlow` | $1.58$ | 1154, 1157 | e6_e10.yaml | `E10_analysis.json:by_L.L0p21.humans.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 345 | `EtenCEdgeComplete` | $17$ | 1157, 1160 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf_edge.complete` | `experiments/E10/analyze.py` | VERIFIED |  |
| 346 | `EtenCEdgeDeadlock` | $8$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf_edge.deadlock` | `experiments/E10/analyze.py` | VERIFIED |  |
| 347 | `EtenCOneComplete` | $1$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.complete` | `experiments/E10/analyze.py` | VERIFIED |  |
| 348 | `EtenCOneDeadlock` | $24$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.deadlock` | `experiments/E10/analyze.py` | VERIFIED |  |
| 349 | `EtenCOneFlow` | $0.75$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 350 | `EtenCOneFlowHi` | $0.77$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.flow.ci95.1` | `experiments/E10/analyze.py` | VERIFIED |  |
| 351 | `EtenCOneFlowLo` | $0.73$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.flow.ci95.0` | `experiments/E10/analyze.py` | VERIFIED |  |
| 352 | `EtenCOneFlowRatio` | $0.51$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.flow_ratio_to_human.ratio` | `experiments/E10/analyze.py` | VERIFIED |  |
| 353 | `EtenCOneFlowRatioHi` | $0.58$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.flow_ratio_to_human.ci95.1` | `experiments/E10/analyze.py` | VERIFIED |  |
| 354 | `EtenCOneFlowRatioLo` | $0.46$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.flow_ratio_to_human.ci95.0` | `experiments/E10/analyze.py` | VERIFIED |  |
| 355 | `EtenCOneGapsTwo` | $19$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf.gaps_gt_2s.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 356 | `EtenCPubComplete` | $0$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_pub.complete` | `experiments/E10/analyze.py` | VERIFIED |  |
| 357 | `EtenCPubCompleteHi` | $0.13$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_pub.completion_wilson95.1` | `experiments/E10/analyze.py` | VERIFIED | bound for 0/25 only (L11) |
| 358 | `EtenCPubDeadlock` | $25$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_pub.deadlock` | `experiments/E10/analyze.py` | VERIFIED |  |
| 359 | `EtenCPubFluct` | $0.087$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_pub.fluct.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 360 | `EtenCPubGap` | $6.8$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_pub.longest_gap.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 361 | `EtenCSigComplete` | $14$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf_sig.complete` | `experiments/E10/analyze.py` | VERIFIED |  |
| 362 | `EtenCSigFluct` | $0.109$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf_sig.fluct.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 363 | `EtenCSigGap` | $72.2$ | 1157, 1160 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf_sig.longest_gap.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 364 | `EtenCSigLongFlow` | $0.54$ | 1157 | e6_e10.yaml | `E10_analysis.json:by_L.L2p0.C1_cf_sig.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 365 | `EtenCSigShortFlow` | $0.62$ | 1157 | e6_e10.yaml | `E10_analysis.json:by_L.L0p21.C1_cf_sig.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 366 | `EtenCThreeCapped` | $15$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.capped` | `experiments/E10/analyze.py` | VERIFIED |  |
| 367 | `EtenCThreeComplete` | $10$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.complete` | `experiments/E10/analyze.py` | VERIFIED |  |
| 368 | `EtenCThreeFlow` | $0.87$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 369 | `EtenCThreeFlowHi` | $0.89$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.flow.ci95.1` | `experiments/E10/analyze.py` | VERIFIED |  |
| 370 | `EtenCThreeFlowLo` | $0.84$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.flow.ci95.0` | `experiments/E10/analyze.py` | VERIFIED |  |
| 371 | `EtenCThreeFlowRatioHi` | $0.67$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.flow_ratio_to_human.ci95.1` | `experiments/E10/analyze.py` | VERIFIED |  |
| 372 | `EtenCThreeFlowRatioLo` | $0.53$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.flow_ratio_to_human.ci95.0` | `experiments/E10/analyze.py` | VERIFIED |  |
| 373 | `EtenCThreeGapsTwo` | $11$ | 1157 | e6_e10.yaml | `E10_analysis.json:cells.C3_rvo2_cf.gaps_gt_2s.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 374 | `EtenCThreeLongFlow` | $0.81$ | 1157 | e6_e10.yaml | `E10_analysis.json:by_L.L2p0.C3_rvo2_cf.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 375 | `EtenCThreeShortFlow` | $0.91$ | 1157 | e6_e10.yaml | `E10_analysis.json:by_L.L0p21.C3_rvo2_cf.flow.mean` | `experiments/E10/analyze.py` | VERIFIED |  |
| 376 | `EtenCEdgeFlowRatio` | $0.57$ | 1160 | e6_e10.yaml | `E10_analysis.json:cells.C1_cf_edge.flow_ratio_to_human.ratio` | `experiments/E10/analyze.py` | VERIFIED |  |

### 7b. Hard-coded numbers (typed in the source, not macros)

| # | Number (main.tex line) | Source checked | Status |
|---|---|---|---|
| H1 | Table 1 parameter values (857-870) | `data/params/model.yaml` | VERIFIED |
| H2 | B_w,edge "within 0.5 m of the door edge" (865) | `model.yaml:edge_zone` [0.5, 1.0] | VERIFIED (incomplete, L22) |
| H3 | Quench window 120 s; stop rule 10^-3 m/s for 10 s (926) | quench driver; CHANGELOG C12 | VERIFIED |
| H4 | Replay perturbation 1e-9 m Gaussian (1111) | E2 replay code | VERIFIED |
| H5 | σ = 0.07 m/s matched level (1114) | E2 config, C44 | VERIFIED |
| H6 | Bias levels b = 0.05-0.5 (1114) | E2 config | VERIFIED |
| H7 | E3 Δt = 0.005/0.01/0.02 s (1117) | E3 config | VERIFIED |
| H8 | E4 β levels 1.5/2.5/3.5 (1067) | E4 config | VERIFIED |
| H9 | 0.1 J floor for noise levels (implied 1069) | `E4_analysis.json:extension.skipped_no_barrier` | VERIFIED |
| H10 | "(ωΔt)², negligible in our snapshots" (1008) | no stored value; CHANGELOG C30 "≤0.3%" only | UNTRACEABLE |
| H11 | E7 seeds 42-141, 600 s (1035) | E7 config | VERIFIED |
| H12 | B_w = 0.04 m short-range wall (1035, 1042) | E7/E7b config | VERIFIED |
| H13 | E11 widths 1.0/1.2/1.8 m (1143) | E11 code WIDTHS | VERIFIED |
| H14 | Door width w = 0.8 m (1148, 1151) | E10 config, CroMa | VERIFIED |
| H15 | Holding area 7.8 × 8.6 m (1151) | `code/sim/scenarios/croma.py:24-25` | VERIFIED |
| H16 | "Every human run empties the holding area" (1154) | E10 humans.runs: 4D040 136 ids, 135 passages | MISMATCH (L10) |
| H17 | Estimator 1.48 s (37 frames, 25 fps) (1151) | `experiments/pilot/w28_croma.py:7` | VERIFIED |
| H18 | Neighbour radius 0.74 m (1151) | `w28_croma.py:8,63` | VERIFIED |
| H19 | Waiting zone 0.3-2.5 m (1151) | `w28_croma.py:9,60` (|y-yc|<2 m omitted) | VERIFIED |
| H20 | Local-mean speed < 0.3 m/s (1151) | `w28_croma.py:67` | VERIFIED |
| H21 | "gaps longer than 2 s" threshold (1154) | E10 analyze | VERIFIED |
| H22 | No agent leaves walkable area (1157) | E10 wall_leaks_total 0 | VERIFIED |
| H23 | 25 runs per CroMa cell (1157) | E10 cells n | VERIFIED |
| H24 | Arch run: v0 = 5 m/s, sampled every 0.1 s (1056) | `experiments/arch/arch.py` | VERIFIED |
| H25 | Arch 25 seeds, 600 s (1056) | arch config | VERIFIED |
| H26 | Pair shift δ = 1 mm / 1 cm / 3 cm (1049) | E7b statics | VERIFIED |
| H27 | 8 nonzero bias values in the pair sweep (1129) | `fig7.json` | VERIFIED |
| H28 | Pair noise σ = 0.01-0.05 (1053, 1129) | E7b noise cells | VERIFIED |
| H29 | Conference σ50 0.049, 25 runs per level (1071) | CR §5 | VERIFIED |
| H30 | Conference C1-C4 definitions (887) | CR §3 | VERIFIED (crush term L16) |
| H31 | Fig. 1 force floor 5-1000 N (822) | `experiments/hero/make_luts.py` | VERIFIED |
| H32 | Fig. 1 margin ±150 N (822) | `make_luts.py` | VERIFIED |
| H33 | Fig. 1 lone floor 0.25 m (822) | `make_luts.py` | VERIFIED |
| H34 | Fig. 1 10 J and 0.5 J bars (822) | `fig1_hero.json` | VERIFIED |
| H35 | Fig. 2 "20 000 spawned agents" (1026) | E1 spawn counts | VERIFIED |
| H36 | Figs 6/7 "within 120 s" (1083, 1129) | quench window | VERIFIED |
| H37 | "five CroMa runs" (1148) | E10 humans n = 5 | VERIFIED |
| H38 | Gate-free "1.0" Arrhenius slope reference (1067) | theory | VERIFIED |
| H39 | "exponential value 1" (1067) | theory | VERIFIED |
| H40 | Table 3 "34 lone keystones" (1093) | E2 strata | VERIFIED |
| H41 | Table 3 "46 snapshots" (1103) | E7b library | VERIFIED |
| H42 | Table 3 "186 seeds" (1098) | E6 seeds | VERIFIED |
| H43 | ±0.10 equivalence margin (1136, 1175) | `E7b_analysis.json:s3_matched.*.rate.tost_0p10` | VERIFIED (forbidden by C6, M9) |
| H44 | "2 s" human gap statement "never exceeds" (1154) | see EtenHumanGapMax | VERIFIED (threshold only) |
| H45 | Speed threshold of quench stop 10^-3 m/s (926) | quench driver | VERIFIED |
| H46 | Okabe-Ito colour assignments (captions) | figure scripts | VERIFIED |
| H47 | "before the runs" / "before they are measured" (854, 1163) | no record of timing in the repository; σ = 0.07 and b* chosen after runs | UNTRACEABLE (L17) |

### 7c. Status totals

| Block | Rows | VERIFIED | MISMATCH | UNTRACEABLE |
|---|---|---|---|---|
| Macros | 376 | 370 | 6 | 0 |
| Hard-coded | 47 | 44 | 1 | 2 |
| Total | 423 | 414 | 7 | 2 |

