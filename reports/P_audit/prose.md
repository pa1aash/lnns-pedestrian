# Prose audit: Mechanism Screening for Deadlock Resolution in a Social Force Model

Standard: `lnns-launch/waveA/prose_prompt.md` (16 categories) plus the house rules. Source state: commit 515c372, `paper/main.pdf` as built.

Anchors: `NN_name.tex:L` means `paper/sections/NN_name.tex` line L. `table*.tex:L` is in `paper/tables/`. `fig1_caption.tex:L` is `figures/fig1_caption.tex` (read-only for this audit, so its fixes go to whoever owns the figure). `fig_protocol.tex:L` is `figures/fig_protocol.tex`. Quotes are LaTeX source. Where a macro matters, the rendered value is given in brackets.

Entry format: `file:line | category | quote | replacement | severity | taste-or-error`

---

## 0. Leverage order (read this first)

Each entry appears once below under its category. This list ranks them by how much each fix changes a skeptical reviewer's reading.

1. **16-1** `06_screening.tex:21` "So does the time step": after the bias sentence was inserted, the elliptical opener now refers to the wrong sentence.
2. **12-1** "Rest drive of force-coupled ORCA" means the added term (215 N) in Sect. 5.1 and Fig. 4, and the total (1.8 to 2.2 times the SFM drive) in the abstract and Sect. 3.2.
3. **8-1** The Table 3a caption calls every row fraction-matched, but `06_screening.tex:24` says the second-trap noise is not fraction-matched.
4. **13-1** "56 of 60 lone-trap snapshots pass" the barrier gate (`04_protocol.tex:48`), but "10 of the 32 gate-accepted snapshots" (`05_deadlock_physics.tex:39`).
5. **13-2** In `07_experiments.tex:12`, `\;` renders as a space, so the PDF reads "128 duplicate track IDs merged".
6. **11-1** Red `\pending` placeholders appear in the rendered back matter (DOI, acknowledgements, disclosure).
7. **13-3** In `05_deadlock_physics.tex:16`, "20000" should read "20\,000" (house rule).
8. **13-4** In `06_screening.tex:45`, "these 28 standoffs" has no antecedent.
9. **9-2** In `05_deadlock_physics.tex:41`, the three slope ratios cannot be mapped to the three barriers.
10. **4-1** In `01_introduction.tex:13`, the "here force-coupled ORCA (legacy), beside force-coupled ORCA (RVO2)" naming sentence does not parse.
11. **9-1** The worst sentence in the paper is `06_screening.tex:31`. **9-3** at `06_screening.tex:24` comes close.
12. **13-5** The pair standoff "needs a short wall range" (abstract, 5, 5.3), yet the default walls give 2 of 98 pair or group standoffs. Relatedly, "each wall law gives one deadlock type".
13. **12-2** Bare "ORCA" stands in for force-coupled ORCA in seven places (house rule).
14. **12-3** Class names appear in six notations (house rule).
15. **14-1 and 14-2** The abstract's first sentence is repeated verbatim as the introduction's first sentence, the CroMa ratio appears four times, and "a deadlock count describes the wall law" appears twice.
16. **8-2** In the Fig. 1 caption, `k_BT` is set with an italic B (house rule).
17. **13-6 to 13-9** Precision breaks the stated two-significant-figure rule (Table 3a/b ΔRMST, Sect. 7 gaps). Quartiles also appear in CI brackets.
18. **1-1 to 1-3** The tic "so overlap does not separate X from ORCA. Y does" occurs three times.

---

## 1. Rhetorical negation (9)

1-1 | `06_screening.tex:19` | 1 | "Two halves of the noise seeds overlap as much ($J=\RunNOneJNoiseNoise$), so overlap does not separate noise from ORCA. Replay separates them:" | "Two halves of the noise seeds overlap as much as noise and force-coupled ORCA (RVO2) do ($J=\RunNOneJNoiseNoise$ and \RevAnineLKNHalfJ). Replay separates noise from force-coupled ORCA:" | medium | error (not-X-but-Y; "as much" has no comparand; tic 1 of 3)

1-2 | `06_screening.tex:29` | 1 | "Two independent noise streams overlap as much as noise and ORCA do ($J=\RevAnineWholeNNJ$ against \RevAnineWholeNNEJ\ for independent sets; Table~\ref{tab:matched-noise}), so overlap does not separate them." | "Two independent noise streams overlap as much as noise and force-coupled ORCA (RVO2) do ($J=\RevAnineWholeNNJ$ against \RevAnineWholeNNEJ\ for independent sets; Table~\ref{tab:matched-noise})." Delete the "so overlap does not separate them" clause, because the next paragraph states what does separate them. | medium | taste (tic 2 of 3)

1-3 | `06_screening.tex:48` | 1 | "so overlap does not separate bias and ORCA. Handedness does:" | "(Table~\ref{tab:matched-bias}). Handedness separates the bias from force-coupled ORCA:" | medium | taste (tic 3 of 3)

1-4 | `07_experiments.tex:25` | 1 | "every variant passes \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow at this width; removing the deadlocks does not make the model realistic." | "every variant, including the three that free most deadlocks, reaches \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow at this width." | medium | error ("realistic" is undefined and the number already carries the claim; mirrored in 1-5 and 1-7)

1-5 | `01_introduction.tex:31` | 1 | "every model variant passes \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow (Sect.~\ref{sec:validity}), so removing the deadlocks leaves the model unrealistic." | "every model variant, with uncalibrated default parameters and with or without deadlocks, reaches \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow (Sect.~\ref{sec:validity})." | medium | error (also an overreach: Sect. 7 qualifies the claim with "uncalibrated default parameters" and the contribution drops that qualifier)

1-6 | `09_conclusions.tex:2` | 1 | "free them through three mechanisms that a matched freed fraction does not distinguish and the probes do." | "free them through three mechanisms that reach the same freed fraction and that the probes separate." | medium | taste

1-7 | `09_conclusions.tex:2` | 1 | "Freeing the deadlocks does not bring the model to the human data: in the CroMa bottleneck every variant passes \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow." | "In the CroMa bottleneck every variant, including those that free the deadlocks, reaches \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow." | medium | taste

1-8 | `00_abstract.tex:3` | 1 | "free deadlocks by other physics." | "free deadlocks by activated escape (noise) and by tilting the pair minimum until it is lost (bias)." | high | error (the abstract defines a finding only by contrast; the positive mechanism exists and fits in eleven words)

1-9 | `01_introduction.tex:13` | 1 | "surrogates matched to ORCA's outcome at one horizon free deadlocks by other physics" | "surrogates matched to ORCA's outcome at one horizon free deadlocks by activated escape and by a lateral tilt" | medium | error

Mirrored pair: `02_related_work.tex:12` reads "resolved them with a provably correct switching controller rather than with additive perturbations", and `08_discussion.tex:7` reads "resolve with a switching controller because additive perturbations carry no guarantee". This is the same contrast stated twice. Fix it at 14-5.

Kept as genuine technical contrasts (they carry information):
- `03_pedestrian_model.tex:33` "as a force magnitude ... instead of its gradient": it states the model's deviation from the cited law.
- `02_related_work.tex:9` "unlike the Grønbech-Jensen–Farago scheme": it names the scheme that does sample correctly.
- `06_screening.tex:16` "earlier than force-coupled ORCA (RVO2) but in the same class": the time differs and the class agrees, and both halves carry information.
- `07_experiments.tex:14` "whereas in the archive its second metre widens": it is a geometry discrepancy, although 4-11 moves it.
- `04_protocol.tex:45` "absent for a deterministic resolver": it is the prediction for the third case.

No cascade of three or more consecutive rule-outs was found. The nearest is `06_screening.tex:19`, where the overlap rule-out is followed by the bias rule-out.

## 2. Sentences that announce their own significance (1)

2-1 | `05_deadlock_physics.tex:41` | 2 | "The time-step signature confirms this independently (Sect.~\ref{sec:att-lone}, Fig.~\ref{fig:escape}(c))." | "The time-step probe gives the same barrier scaling (Sect.~\ref{sec:att-lone}, Fig.~\ref{fig:escape}(c))." | low | taste ("independently" is emphasis)

Also checked for "notably", "crucially", "importantly", "it is worth", "the key point", "what matters" and "significantly". None were found.

## 3. Sentences that announce what a section will do (4)

3-1 | `08_discussion.tex:4` | 3 | The whole paragraph of Sect. 8.1, "In this social force model three mechanisms reach the same freed fraction ... agrees with it on every defining probe (Table~\ref{tab:signatures})." Its first and third sentences restate Sect. 6 and Table 2. Only the second sentence and the rest-drive-push clause are unique. | "In this social force model a matched freed fraction is weak evidence of a shared mechanism: force-coupled ORCA, noise and the lateral bias reach it through Reshape (axial), Heat and Reshape (lateral) (Sect.~\ref{sec:attribution}), while the rest-drive push, of the same class as force-coupled ORCA, agrees with it on every defining probe (Table~\ref{tab:signatures})." | medium | error (restated paragraph)

3-2 | `03_pedestrian_model.tex:4` | 3 | "The social force model takes a TTC-inspired force or ORCA as optional terms (Table~\ref{tab:params})." | "This social force model takes a TTC-inspired force or force-coupled ORCA as optional terms (Table~\ref{tab:params})." | low | error (the definite article makes it a claim about every social force model, which breaks the house rule; Eq. (1) and line 11 repeat the content, so deletion is also acceptable)

3-3 | `04_protocol.tex:4` | 3 | "Probes on frozen deadlocks sort perturbations into four mechanism classes (Table~\ref{tab:signatures})." | "Probes on snapshots sort perturbations into four mechanism classes (Table~\ref{tab:signatures})." Keep it as the scope opener the house rule requires, and fix only the term (12-4). | low | taste

3-4 | `06_screening.tex:2` | 3 | "Force-coupled ORCA frees the lone trap and the pair standoff by Reshape; its fraction-matched surrogates are Heat and Reshape (lateral), the legacy solver adds a Glitch, and the ORCA velocity filter frees no deadlock." | "Force-coupled ORCA frees the lone trap and the pair standoff by Reshape; noise is Heat, the lateral bias Reshape, lateral, the legacy solver Glitch, and the ORCA velocity filter at most Prevent." | low | taste (the finding-first opener is house style; this version gives every class in one notation and drops "adds a Glitch")

## 4. Trailing appositive qualifications (13)

4-1 | `01_introduction.tex:13` | 4 | "All ORCA results of~\cite{gang2026} used the legacy linear-program solver, here force-coupled ORCA (legacy), beside force-coupled ORCA (RVO2)." | "All ORCA results of~\cite{gang2026} used the legacy linear-program solver. Force coupling with this solver is labelled force-coupled ORCA (legacy), and with the RVO2 solver force-coupled ORCA (RVO2)." | high | error (the trailing appositives do not parse, and "beside" has no clear meaning)

4-2 | `01_introduction.tex:9` | 4 | ", and a simulation that plans such a place is as trustworthy as the mechanism behind its bottleneck behaviour." | Make it a sentence of its own: "Planning such a place with a simulation requires that its bottleneck behaviour come from an identified mechanism." | medium | taste (editorial tail; aphorism 1 of 9)

4-3 | `06_screening.tex:31` | 4 | ", so this prediction extrapolates the Arrhenius law below the tested range $\beta\ge1.5$, outside the Kramers regime." | End the sentence at "have $\beta<1$." Then add to the Limitations paragraph (`08_discussion.tex:10`): "The whole-run stall prediction extrapolates the Arrhenius law below the tested range $\beta\ge1.5$, outside the Kramers regime." | medium | error (a confession in a results tail; move it to Limitations)

4-4 | `05_deadlock_physics.tex:20` | 4 | "; the best-fitting group size, \RevBtwoNbest, is a descriptive parameter." | "Fitting the exponent instead gives a group size of \RevBtwoNbest, which describes the data and is not predicted." | low | taste

4-5 | `05_deadlock_physics.tex:43` | 4 | ", consistent with a turnover factor below 1 at moderate damping~\cite{melnikov1986}." | ". A turnover factor below 1, expected at the damping $m/\tau$ of this model~\cite{melnikov1986}, accounts for this." | low | taste

4-6 | `05_deadlock_physics.tex:52` | 4 | "the \PairFoldFN\ others escape at most \PairFoldMissGap\% below $b_f$, carried over by the members' inertia." | "the \PairFoldFN\ others escape at most \PairFoldMissGap\% below $b_f$, where the members' inertia carries them over." | low | taste (as written, the participle dangles from "others")

4-7 | `06_screening.tex:24` | 4 | "The SFM restart frees \RevAfiveXPoolSFMFreed, each still creeping below the deadlock criterion's 0.01\,m/s." | "The SFM quench frees \RevAfiveXPoolSFMFreed; both blockers were still moving at the snapshot, below the deadlock criterion's 0.01\,m/s." | medium | error ("creeping" falls under the banned "slow creep"; the tail also dangles)

4-8 | `06_screening.tex:26` | 4 | "and the copies part when a leg normal changes sign (\FixAfourDiscLegFlip\ of \FixAfourDiscN\ first switches), shifting the exit by up to \EtwoReplayCThreePubMaxDt\,s: Glitch." | "The copies part when a leg normal changes sign (\FixAfourDiscLegFlip\ of \FixAfourDiscN\ first switches), and the exit shifts by up to \EtwoReplayCThreePubMaxDt\,s. The legacy solver is therefore Glitch." | medium | error (the participle has no subject, and the bare one-word verdict is aphorism 2 of 9)

4-9 | `06_screening.tex:16` | 4 | ": its rest drive removes the fixed point, which is Reshape (axial)." | ". Its rest drive removes the fixed point, so force-coupled ORCA is Reshape, axial, at the lone keystone." | low | error ("which" attaches to "fixed point")

4-10 | `00_abstract.tex:3` | 4 | "at rest this force-coupled ORCA equals the model with relaxation time $\tau'=\tau\tau_{\rm orca}/(\tau+\tau_{\rm orca})$, a drive \RevAoneDriveRatioLo--\RevAoneDriveRatioHi\ times larger." | "at rest this force-coupled ORCA equals the model with relaxation time $\tau'=\tau\tau_{\rm orca}/(\tau+\tau_{\rm orca})$, whose rest drive is \RevAoneDriveRatioLo--\RevAoneDriveRatioHi\ times that of the model." | medium | error (as written, the appositive attaches to $\tau'$)

4-11 | `07_experiments.tex:14` | 4 | "; the model builds the 2.0\,m bottleneck straight, whereas in the archive its second metre widens." | Move it to Limitations (`08_discussion.tex:10`): "The model's 2.0\,m CroMa bottleneck is straight, whereas the experimental one widens in its second metre." | low | taste

4-12 | `03_pedestrian_model.tex:40` | 4 | "Native ORCA, which sets velocities directly and treats walls as obstacles, has no wall social force and is not tested here." | Delete. `08_discussion.tex:10` already states the limitation. Keep "has no wall social force" by adding it there: "native ORCA, which sets velocities, treats walls as obstacles and has no wall social force, is untested." | low | error (duplicate limitation)

4-13 | `05_deadlock_physics.tex:45` | 4 | ", so the Arrhenius test does not cover the matched level directly." | ". The Arrhenius test, run at $\beta\ge1.5$, does not reach this level." | low | taste ("directly" is a hedge)

## 5. Softening adverbs and undefined evaluative words (9)

5-1 | `05_deadlock_physics.tex:39` | 5 | "over an effective barrier about 0.9 of the computed one." | "over an effective barrier \RevBthreeAllDeep--\RevBthreeAllMid\ of the computed one." | medium | error (approximate here, exact in the abstract)

5-2 | `00_abstract.tex:3` | 5 | "needs sharp door-edge segment ends and a short wall range." | "needs sharp door-edge segment ends and a wall range of 0.04\,m." | medium | error ("short" is undefined; the threshold is 0.04 m)

5-3 | `05_deadlock_physics.tex:2` | 5 | "the pair standoff at sharp door edges under a short wall range." | "the pair standoff at sharp segment ends with $B_w=0.04$\,m." | medium | error

5-4 | `05_deadlock_physics.tex:48` | 5 | "The pair standoff requires sharp segment ends at the door edges and a short wall range." | "The pair standoff requires sharp segment ends at the door edges and forms in most runs with $B_w=0.04$\,m." See also 13-5. | medium | error

5-5 | `04_protocol.tex:7` | 5 | "\emph{Glitch} changes the outcome under a displacement far below physical scales," | "\emph{Glitch} changes the outcome under a $10^{-9}$\,m displacement," | medium | error ("physical scales" is undefined, and the number is the definition)

5-6 | `08_discussion.tex:10` | 5 | "the \PairN\ pair snapshots give wide 95\% intervals for differences in freed fraction (Table~\ref{tab:matched-bias})." | "the \PairN\ pair snapshots give 95\% intervals up to 0.37 wide for differences in freed fraction (Table~\ref{tab:matched-bias})." | medium | error (state the width; [−0.15, 0.22] is 0.37)

5-7 | `01_introduction.tex:9` | 5 | "A surrogate tuned to the same outcome shows that a simpler cause suffices." | "A surrogate tuned to the same outcome shows that a cause of another kind suffices for that outcome." | medium | error ("simpler" is undefined; a lateral bias is not obviously simpler than ORCA)

5-8 | `02_related_work.tex:6` | 5 | "and hardly on update scheme or time step~\cite{xu2021}." | "and little on update scheme or time step~\cite{xu2021}." | low | taste (reported speech from the source; the hedge belongs to Xu et al.)

5-9 | `08_discussion.tex:10` | 5 | "Force-coupled ORCA is a non-standard coupling;" | "Force coupling is not ORCA's published form;" | low | taste ("non-standard" is evaluative where a fact is available)

Kept: "weak evidence" (`08_discussion.tex:4`) is the claim itself. "on average" (`06_screening.tex:19,24`) names a statistic. "near zero" (`04_protocol.tex:45`) is a prediction, and the equation defines it.

## 6. Sentences beginning with "What", and clefts (0)

Checked for "What ...", "It is X that", "There is/are X which/that", "The thing that ...", "This is what ...". None were found. The one inverted emphatic construction, "So does the time step", is at 16-1.

## 7. Headers and bold paragraph leads (6)

7-1 | `04_protocol.tex:1` | 7 | "\section{Mechanism Classes and the Screening Protocol}" | "\section{Screening Protocol and Methods}" | medium | error (the section also holds rest-state theory, $T_{\rm eff}$, string-method barriers and statistics, and a reader scanning the contents will not look for them here)

7-2 | `04_protocol.tex:17` | 7 | "\subsection{Terms That Vanish at Rest}" | "\subsection{Rest States and Their Stability}" | low | taste (the heading names a step of the argument; the content is Remark 1)

7-3 | `05_deadlock_physics.tex:31` | 7 | "\subsection{Noise as Activated Escape}" | "\subsection{Escape of the Lone Trap Under Noise}" | low | taste (the heading states the result)

7-4 | `05_deadlock_physics.tex:47` | 7 | "\subsection{The Pair Standoff at Sharp Door Edges}" | "\subsection{The Pair Standoff}" | low | taste (the heading embeds a result; it also parallels 5.1, which is fine)

7-5 | `06_screening.tex:23` | 7 | "\subsubsection{Second Trap and the Legacy Solver.}" | Split at the paragraph break into "\subsubsection{Second Trap.}" (line 24) and "\subsubsection{Legacy Solver.}" (line 26). | low | taste (two topics in one lead)

7-6 | `07_experiments.tex:18` | 7 | "\subsubsection{Results.}" | "\subsubsection{Flow, Gaps and Velocity Fluctuation.}" | low | taste (the generic lead does not help scanning)

## 8. Figure and table captions (7)

House limit: two sentences. Every caption except Fig. 1 complies (Fig. 1 has three sentences and is exempt). No caption carries a measurement that appears nowhere else. Fig. 1's colour-scale limits are plotting conventions, and Fig. 6's "dashed: 0.9" is a reference line.

8-1 | `table3a_noise.tex:4` | 8 | "\caption{Per-step noise fraction-matched to force-coupled ORCA (RVO2); each row $p$ tests the noise row above it.}" | "\caption{Per-step noise against force-coupled ORCA (RVO2), fraction-matched at the lone keystones and in whole runs; each row $p$ tests the noise row above it.}" | high | error (`06_screening.tex:24` says the second-trap noise "is not fraction-matched here", and the table's own second-trap row has Δ = +0.25 [0.08, 0.44])

8-2 | `fig1_caption.tex:2` | 8 | "the vermilion band is $k_BT_{\mathrm{eff}}$." | "the vermilion band is $k_{\mathrm{B}}T_{\mathrm{eff}}$." | high | error (house rule: k_B upright; this is the only italic B in the paper)

8-3 | `fig1_caption.tex:2` | 8 | "Right: rest-state energy relative to the ball (the rest state) along the door axis" | "Right: energy relative to the rest state (ball) along the door axis" | medium | error (the parenthetical gloss is reversed, so the reader meets "the ball" before knowing it is a marker)

8-4 | `fig1_caption.tex:2` | 8 | "dark magma, wall and partner" | "dark purple, wall and partner" | low | error (a plotting-library colormap name in a caption; process leakage)

8-5 | `table2_signatures.tex:5` | 8 | "Observed cells report the lone traps, the tilt column and pair rows the pair standoff." | "Observed cells refer to the lone traps, except the tilt column and the pair rows, which refer to the pair standoff." | medium | error (the gapped sentence parses as a list of three things reported)

8-6 | `05_deadlock_physics.tex:35` | 8 | Fig. 6 caption, about 70 words: "(full, circles; pinned, squares; alone, triangles; black, restarts at $\beta=5$--7 and fits over $\beta=1.5$--7)". | Keep the legend and move "fits over $\beta=1.5$--7" to the text at line 41, which already states it ("the slope ratio over $\beta=1.5$--7"). That brings the caption under 60 words. | low | taste

8-7 | `06_screening.tex:8` and `06_screening.tex:37` | 8 | "(none where every snapshot has the same outcome)" appears in both captions. | Delete it from both captions and add to `04_protocol.tex:51`: "A bootstrap interval is omitted where every snapshot has the same outcome." | low | taste (a plotting convention repeated in two captions belongs in Methods)

## 9. Run-on and over-nested sentences (12)

**Worst sentence in the paper: 9-1** (`06_screening.tex:31`). It runs to six clauses, with a parenthetical, a colon and a "while" contrast. **9-3** (`06_screening.tex:24`) comes close, with a three-item parenthetical nested inside the subject.

9-1 | `06_screening.tex:31` | 9 | "Force-coupled ORCA (RVO2) is faster on all \EsixPairedCThreeFaster\ seeds where both complete (median lead \EsixPairedDelay\,s), and the final states at 600\,s differ in class (Holm $p\RevAsevenWholeEsixClassPHolmRel$): its \EsixCThreeFailRest\ failures at rest are lone keystones and \EsixCThreeMovingSecond\ of its \EsixCThreeFailMoving\ moving failures hold a second trap, while noise failures never come to rest and hold \EsixNoiseLone\ lone keystones, \EsixNoiseSecond\ second traps and \EsixNoiseCollective\ group standoffs." | "Force-coupled ORCA (RVO2) is faster on all \EsixPairedCThreeFaster\ seeds where both complete (median lead \EsixPairedDelay\,s). The final states at 600\,s differ in class (Holm $p\RevAsevenWholeEsixClassPHolmRel$). The \EsixCThreeFailRest\ failures of force-coupled ORCA that end at rest are lone keystones, and \EsixCThreeMovingSecond\ of its \EsixCThreeFailMoving\ moving failures hold a second trap. Noise failures never come to rest; they hold \EsixNoiseLone\ lone keystones, \EsixNoiseSecond\ second traps and no group standoff." | high | error

9-2 | `05_deadlock_physics.tex:41` | 9 | "Extended to $\beta=5$, 6 and 7 (\RevBthreeRuns\ alone restarts at $\Delta U=\RevBthreeDUShallow$, \RevBthreeDUMid\ and \RevBthreeDUDeep\,J), the slope ratio over $\beta=1.5$--7 is \RevBthreeAllShallow\ [...], \RevBthreeAllMid\ [...] and \RevBthreeAllDeep\ [...]." | "Extended to $\beta=5$, 6 and 7 (\RevBthreeRuns\ restarts in the alone condition), the slope ratio over $\beta=1.5$--7 is \RevBthreeAllShallow\ [...] at $\Delta U=\RevBthreeDUShallow$\,J, \RevBthreeAllMid\ [...] at \RevBthreeDUMid\,J and \RevBthreeAllDeep\ [...] at \RevBthreeDUDeep\,J." | high | error (a reader maps the three ratios to the three β values, which is wrong)

9-3 | `06_screening.tex:24` | 9 | "On all \RevAfiveXPoolN\ second traps (the screen's \RevAfiveXEtwoN\ and \RevAfiveXNewN\ drawn at random, alike in every arm, Holm $p\RevAfiveXVsEtwoMinPHolmRel$) the drive part frees \RevAfiveXPoolDriveFreed\ blockers and force-coupled ORCA (RVO2) \RevAfiveXPoolOrcaFreed\ (McNemar $p\RevAfiveXPoolDriveOrcaPDisp$)." | "The second-trap pool adds \RevAfiveXNewN\ snapshots drawn at random to the screen's \RevAfiveXEtwoN; the two sets respond alike under every perturbation (Holm $p\RevAfiveXVsEtwoMinPHolmRel$). On all \RevAfiveXPoolN, the drive part frees \RevAfiveXPoolDriveFreed\ blockers and force-coupled ORCA (RVO2) frees \RevAfiveXPoolOrcaFreed\ (McNemar $p\RevAfiveXPoolDriveOrcaPDisp$)." | high | error ("arm" is undefined trial jargon; see 11-5)

9-4 | `06_screening.tex:26` | 9 | "In these replays the blocker jitters at \RevAthirteenCreepSpeedMin--\RevAthirteenCreepSpeedMax\,m/s (net axial drift ...), and the copies part when a leg normal changes sign (...), shifting the exit by up to ...\,s: Glitch." | "In these replays the blocker jitters at \RevAthirteenCreepSpeedMin--\RevAthirteenCreepSpeedMax\,m/s with a net axial drift of $\RevAthirteenCreepDriftMin$ to $+\RevAthirteenCreepDriftMax$\,mm/s." The second half follows 4-8. | medium | error

9-5 | `07_experiments.tex:23` | 9 | "The deficit persists between the 10\% and the 90\% passage (SFM \RevDThreeCOneWindowFlow, humans \RevDHumanWindowFlow\,ped/s) and at both bottleneck lengths (2.0\,m: humans \EtenLongHumanFlow, model \RevDThreeCSigLongFlow--\RevDThreeCThreeLongFlow\,ped/s; 0.2\,m: \RevDShortHumanFlow\ and \RevDThreeCSigShortFlow--\RevDThreeCThreeShortFlow\,ped/s)." | "Between the 10\% and the 90\% passage the SFM passes \RevDThreeCOneWindowFlow\,ped/s and humans \RevDHumanWindowFlow\,ped/s. With the 2.0\,m bottleneck humans pass \EtenLongHumanFlow\,ped/s and the model \RevDThreeCSigLongFlow--\RevDThreeCThreeLongFlow\,ped/s; with the 0.2\,m bottleneck, \RevDShortHumanFlow\ and \RevDThreeCSigShortFlow--\RevDThreeCThreeShortFlow\,ped/s." | medium | error (nested parentheticals with semicolons)

9-6 | `07_experiments.tex:25` | 9 | "Completed runs have a longest gap of at most \RevDThreeCOneGapCompleteMax\,s (SFM), ... and \RevDThreeCSigGapCompleteMax\,s (noise), and \RevDThreeCOneCens, \RevDThreeCEdgeCens, \RevDThreeCThreeCens\ and \RevDThreeCSigCens\ of 25 runs are censored." | "Completed runs have a longest gap of at most \RevDThreeCOneGapCompleteMax\,s (SFM), \RevDThreeCEdgeGapCompleteMax\,s (jamb range), \RevDThreeCThreeGapCompleteMax\,s (force-coupled ORCA) and \RevDThreeCSigGapCompleteMax\,s (noise). Of 25 runs, \RevDThreeCOneCens\ (SFM), \RevDThreeCEdgeCens\ (jamb range), \RevDThreeCThreeCens\ (force-coupled ORCA) and \RevDThreeCSigCens\ (noise) are censored." | medium | error (a "respectively" list without labels)

9-7 | `06_screening.tex:16` | 9 | "The constraint part alone frees \EtwoLKConstrRVOFreed\ (RVO2) and \EtwoLKConstrPubFreed\ (legacy); the rest-drive push frees \EtwoLKFrozenPlusFreed\ towards the door and \EtwoLKFrozenMinusFreed\ away, earlier than force-coupled ORCA (RVO2) but in the same class ($\Delta$RMST ..., Holm $p$...)." | "The constraint part alone frees none with either solver. The rest-drive push frees \EtwoLKFrozenPlusFreed\ towards the door and none away; it frees them earlier than force-coupled ORCA (RVO2) ($\Delta$RMST $\RevAsevenPushLoneTimeEff$\,s, Holm $p\RevAsevenPushLoneTimePHolmRel$) and has the same class." | medium | error

9-8 | `06_screening.tex:45` | 9 | "Alone the constraint part frees \PairConsPubFreed\ (legacy) and \PairConsRvoFreed\ (RVO2); added to the drive part it cancels the drive's squeeze towards the axis, and force-coupled ORCA (RVO2) frees fewer standoffs than the drive part alone ($p\PairDriveRvoPRel$)." | "Alone, the constraint part frees \PairConsPubFreed\ (legacy) and \PairConsRvoFreed\ (RVO2). Added to the drive part, it cancels the drive's squeeze towards the axis, so force-coupled ORCA (RVO2) frees fewer standoffs than the drive part alone ($p\PairDriveRvoPRel$)." | medium | error

9-9 | `03_pedestrian_model.tex:63` | 9 | "In CroMa (...) a holding area opens through a 0.8\,m entrance into a bottleneck 0.2 or 2.0\,m long; its door edges are convex junctions of jamb and corridor wall, both with $B_{w,\rm edge}$; there the nearest point of the two walls acts once." | "In CroMa (...) a holding area opens through a 0.8\,m entrance into a bottleneck 0.2 or 2.0\,m long. Its door edges are convex junctions of jamb and corridor wall, both with $B_{w,\rm edge}$, and an agent at a junction feels the nearer of the two walls once." | medium | error ("there the nearest point of the two walls acts once" is opaque)

9-10 | `05_deadlock_physics.tex:20` | 9 | "The parameter-free prediction $(1-f)^{100}$, with $f(w)$ the stuck-alone fraction at width $w$, misses $w_{50}$ by \RevBtwoPredHundredOffset\,m because the crowd pushes stuck-alone agents through (those held arrived with at most \RevBtwoHeldActiveMax\ agents still active); the best-fitting group size, \RevBtwoNbest, is a descriptive parameter." | "The parameter-free prediction $(1-f)^{100}$, with $f(w)$ the stuck-alone fraction at width $w$, misses $w_{50}$ by \RevBtwoPredHundredOffset\,m because the crowd pushes stuck-alone agents through. Agents held arrived with at most \RevBtwoHeldActiveMax\ others still active." Follow with 4-4. | medium | error

9-11 | `04_protocol.tex:13` | 9 | "Noise keeps freeing, so its surrogate matches from a horizon on: at the lone keystone from \RevAeightLKNoiseCMatchFrom\,s ($\sigma=0.07$\,m/s) and \RevAeightLKNoiseNoneMatchFrom\,s ($\sigma=0.0717$\,m/s), in whole runs from \RevAeightWholeNoiseMatchFrom\,s." | "Noise keeps freeing after force-coupled ORCA has stopped, so the noise surrogate is fraction-matched from a horizon on: from \RevAeightLKNoiseCMatchFrom\,s ($\sigma=0.07$\,m/s) and \RevAeightLKNoiseNoneMatchFrom\,s ($\sigma=0.0717$\,m/s) at the lone keystone, and from \RevAeightWholeNoiseMatchFrom\,s in whole runs." | low | taste

9-12 | `02_related_work.tex:12` | 9 | "Grover et al.\ showed that multi-robot systems avoiding collisions through control barrier functions deadlock at force-balance equilibria, which symmetric configurations approach, and resolved them with a provably correct switching controller rather than with additive perturbations~\cite{grover2023,grover2020}; breaking symmetry helps avoid deadlock~\cite{grover2020symmetry}." | "Grover et al.\ showed that multi-robot systems avoiding collisions through control barrier functions deadlock at force-balance equilibria, which symmetric configurations approach~\cite{grover2023,grover2020}. They resolved them with a provably correct switching controller, and breaking symmetry helps avoid deadlock~\cite{grover2020symmetry}." | low | taste (also removes the rather-than half of the mirrored pair)

Comma-spliced result lists: `01_introduction.tex:28` (contribution 1) joins four findings, and `06_screening.tex:2` joins four verdicts. The second is covered by 3-4. For the first, split after "(Sect.~\ref{sec:lone})." This is low and taste, and is not counted separately.

## 10. Aphoristic paragraph endings (9 found; 1 kept)

Count: 9. That is above the threshold of two to three, and together they set an overclaiming voice. The one that earns its place is `08_discussion.tex:4`, "A matched freed fraction is therefore weak evidence of a shared mechanism." It is the paper's thesis. Keep it in the form given in 3-1.

10-1 | `01_introduction.tex:9` | 10 | "a simulation that plans such a place is as trustworthy as the mechanism behind its bottleneck behaviour." | See 4-2. | medium | taste

10-2 | `02_related_work.tex:6` | 10 | "Without static friction, this model deadlocks in rest states of a driven, damped system." | "This model has no static friction (Sect.~\ref{sec:arches}), so its deadlocks are rest states of a driven, damped system (Sect.~\ref{sec:physics})." | low | taste (also a result placed in Related Work; see 14-3)

10-3 | `02_related_work.tex:12` | 10 | "The pair standoff (Sect.~\ref{sec:pair}) is a pedestrian analogue." | "The pair standoff (Sect.~\ref{sec:pair}) is such a force-balance equilibrium between two pedestrians." | low | taste

10-4 | `02_related_work.tex:15` | 10 | "; here the rival is a fraction-matched surrogate and the patterns are snapshot responses to probes." | ". This paper applies the idea with a fraction-matched surrogate as the rival mechanism and the snapshots' responses to probes as the patterns." | low | taste

10-5 | `06_screening.tex:26` | 10 | ": Glitch." | See 4-8. | medium | taste

10-6 | `06_screening.tex:16` | 10 | ", which is Reshape (axial)." | See 4-9. | low | taste

10-7 | `07_experiments.tex:25` | 10 | "removing the deadlocks does not make the model realistic." | See 1-4. | medium | taste

10-8 | `085_recommendations.tex:2` | 10 | "A narrow-door deadlock count of this social force model describes its wall law and steering terms." | "In this social force model the number of deadlocks at a narrow door is set by the wall range, the shape of the segment ends and the steering terms (Sects.~\ref{sec:physics} and~\ref{sec:attribution})." | medium | taste (near-duplicate of the paper's last sentence; see 14-2)

10-9 | `09_conclusions.tex:2` | 10 | "A narrow-door deadlock count describes the wall law and steering terms until the probes have named its mechanism and matched experiments have tested its flow and gaps (Sect.~\ref{sec:recommend})." | "A narrow-door deadlock count can be read as crowd behaviour once probes have named its mechanism and matched experiments have tested the model's flow and passage gaps (Sect.~\ref{sec:recommend})." | medium | taste ("its flow" also refers to the count, which has no flow)

## 11. Process-record and internal-code leakage (9)

11-1 | `10_back_matter.tex:4,6,8` | 11 | "(DOI \pending{Zenodo DOI})", "\pending{acknowledgements, written by the authors}", "\pending{disclosure of interests, written by the authors}" | Use the minted DOI. Write acknowledgements text, or delete the subsection if there is none. For disclosure, use the LNCS standard sentence: "The authors have no competing interests to declare that are relevant to the content of this article." | high | error (rendered in red in `main.pdf`)

11-2 | `06_screening.tex:26` | 11 | "(repository pedestrian-abs, commits \texttt{\RevAfourteenCommitConf}..\texttt{\PscrCommitConfHead}, tag \texttt{r2.0-baseline}). Line \RevAfourteenDefectLine\ of \texttt{sim/steering/orca.py}, introduced in commit \texttt{\RevAfourteenCommitIntro}," | "The legacy solver is the ORCA code of the conference paper~\cite{gang2026}; its repository, commits and the defective line are given under Data and Code Availability. It takes the normal of a leg half-plane along $\mathbf u$, ..." Then add the hashes, tag and file path to `10_back_matter.tex:4`. | medium | taste (the competing convention is an inline bug provenance, which reviewers of software defects sometimes want; as running prose it reads as a code log)

11-3 | `01_introduction.tex:13` | 11 | "This work revises that reading:" | "Under the probes of this paper," followed by the rest of the sentence with 1-9 applied: "surrogates matched to ORCA's outcome at one horizon free deadlocks by activated escape and by a lateral tilt, and force-coupled ORCA frees them through its rest drive." | medium | taste (narrated revision of one's own published claim; the citation already makes the relation explicit)

11-4 | `01_introduction.tex:13` | 11 | "Its model also took densities from Voronoi cells with calibrated Weidmann coefficients." | "The model of~\cite{gang2026} also took densities from Voronoi cells with calibrated Weidmann coefficients, where this model counts neighbours within $R$ (Eq.~\eqref{eq:des})." | medium | error ("Its" is ambiguous between the paper and the solver, and the sentence does not say why the reader needs it)

11-5 | `06_screening.tex:24` | 11 | "alike in every arm" | "alike under every perturbation" (see 9-3) | medium | error (clinical-trial jargon that is never defined)

11-6 | `04_protocol.tex:48` | 11 | "A barrier passes the gate when its string converges" and "the \RevAfiveEthreeQual\ with full $\Delta U\ge3$\,J form the time-step pool." | "A barrier is accepted when its string converges" and "the \RevAfiveEthreeQual\ with full $\Delta U\ge3$\,J are eligible for the time-step probe." | medium | error (internal labels; "gate" also clashes with the density gate, see 12-8)

11-7 | `05_deadlock_physics.tex:39` | 11 | "gate-accepted snapshots" | "snapshots with accepted barriers" | medium | error (see also 13-1)

11-8 | `06_screening.tex:13,24,26` | 11 | "The screen holds \EtwoNAll\ snapshots", "the screen's \RevAfiveXEtwoN", "on the screen" | Define the term at line 13: "The screening set holds \EtwoNAll\ snapshots ...". Then use "the screening set's" and "on the screening set". | medium | error (an undefined internal label)

11-9 | `05_deadlock_physics.tex:45,48`; `06_screening.tex:31`; `08_discussion.tex:10` | 11 | "library barriers", "library snapshots", "library seeds", "\EsixBarrierN\ library barriers", "the pair library" | Define it at `03_pedestrian_model.tex:65`: "The saved snapshots form the snapshot library." Keep the uses. | medium | error ("library" is defined only inside the Fig. 3 box)

## 12. Terminology and notation drift (18)

### Concept table

| Concept | Names used (where) | Recommend |
|---|---|---|
| Goal-directed force at rest added by force-coupled ORCA, versus the total | "rest drive of force-coupled ORCA (RVO2, median \DriveORCAMedian\,N)" = added term (`05:16`, Fig. 4 caption `05:8`, Fig. 1 "force-coupled ORCA's rest drive", "added drive"); "with its rest drive added" (`06:16`); "a drive 1.8–2.2 times larger" = total (`00:3`); "its rest drive, the first term, is ... times the SFM's" = total (`03:47`) | "rest drive" for the total goal-directed force at **v**=0 (glossary); "ORCA's added rest drive" for the increment |
| Restart under a perturbation | quench (glossary, `03:65`, Sect. 6); "restarted" (`05:18`, `05:39`); "restarts" (`05:39`, `05:41`, `05:43`, Fig. 6); "SFM restart" (`06:24`); "escape run" (`04:48`) | "quench"; define "escape run" in 4.5 as a noise quench run to the blocker's exit |
| Saved rest state | snapshot; "frozen deadlock(s)" (`04:4`, Table 2 caption, Fig. 3 caption and box, `06:51`); "rest state" | "snapshot" |
| Rounded door-edge geometry | "rounded segment ends" (`01:28`); "Rounded jamb ends" (`05:22`); "jamb ends rounded" (`05:48`); "rounds each jamb into a capsule" (`03:63`); "rounded door edges" (`08:10`); "round the door edges" (`085:6`); "corner radius" (Table 1); "rounded" (Fig. 5) | "rounded segment ends (radius $r_c$)" |
| Wall-force variant | "wall law" (`05:22`, `085:2`, `09:2`); "wall variant" (Fig. 5 caption); "wall force" (Table 1); "wall range" | "wall range" for $B_w$; "wall-range variant" for the set of variants; drop "wall law" |
| Agent held without neighbours | "stuck alone" (`05:16`ff); "held alone" (`00:3`, Fig. 1); "held at rest by the door-edge wall force alone" (`01:19`) | "stuck alone" (it has a defined margin) |
| Mechanism being screened | "resolver" (`04:13`, `04:45`); "the tested mechanism" (`01:20`); "the mechanism under test" (Fig. 3); "the mechanism credited with resolving deadlocks" (`04:13`) | "resolver", defined once in 4.2, with the glossary updated |
| Lateral bias versus its probe | "lateral bias $b$, a deterministic tilt" (`03:18`); "Tilt $\pm b$" (Table 2); "lateral tilt $\pm b$" (Fig. 1, Fig. 3); "tilt probe" (`085:2`); "bias $b^\ast$"; "reversed bias" | "lateral bias" for the perturbation, "tilt probe ($\pm b$)" for the probe |
| Mechanism classes | "Reshape (axial)" (`06:16`); "Reshape (lateral)" (`06:2`); "Reshape (axial, lateral)" (`01:22`); "Reshape, axial subtype" and "Reshape, lateral subtype" (`08:4`); "Reshape, axial" (`04:9`, Table 2, Fig. 3); "a Glitch" (`06:2`); "Reshape at the pair" (`06:45`); "Reshape, solver-dependent" (Table 2 note) | "Reshape, axial" and "Reshape, lateral"; class names without articles |
| Force-coupled ORCA | bare "ORCA" for it (`06:19` twice, `06:29`, `06:48`, Table 2 note "(ORCA)", Table 3a note "(ORCA)" twice); "(force-coupled ORCA)" without solver (`07:25`) | "force-coupled ORCA (RVO2)" |
| Legacy solver | "legacy linear-program solver" (`01:13`, `03:36`); "legacy ORCA solver" (`00:3`); "the ORCA code of the conference paper" (`06:26`) | "legacy linear-program solver" at first use, then "legacy solver" |
| Horizon | horizon $T$ (house term); "time horizon" $\tau_h$ of ORCA (`02:3`, `03:36`, Table 1) | keep "horizon $T$"; call $\tau_h$ "ORCA look-ahead time" |
| Fraction-matching horizon | "a named horizon $T$" (`01:11`); "a stated horizon" (`00:3`, `08:4`); "at horizon $T$" (glossary) | "at horizon $T$" |
| Freed or completed | freed fraction; "completion fraction" (`04:13`); "completed fraction" (Fig. 5 caption); "same outcome" (`01:9`) | "freed fraction at horizon $T$"; "completed fraction" only for whole runs, defined once at `04:13` |
| Door | door; "exit" (`01:13` "0.8 m exit"; Fig. 5 axis "exit width w"); "opening" (glossary) | "door"; "door width $w$" on the Fig. 5 axis |
| Held or unresolved | "held" (throughout); "unresolved" (`04:51`, `06:19`, Table 3a note) | "held"; define "unresolved set = held snapshots" in 4.6 |
| Response pattern | "signature(s)" (`05:41`, Fig. 3 step 3, label `tab:signatures`); "Response" (Table 2 caption) | "response" in text; the labels can stay |

### Entries

12-1 | `05_deadlock_physics.tex:16` | 12 | "The rest drive of force-coupled ORCA (RVO2, median \DriveORCAMedian\,N) lowers this to \StuckAloneFracCThree" | "The added rest drive of force-coupled ORCA (RVO2, median \DriveORCAMedian\,N), which raises the total \RevAoneDriveRatioLo--\RevAoneDriveRatioHi-fold, lowers this to \StuckAloneFracCThree" | high | error (as rendered, a reader sees "SFM drive (median 214 N)" and "rest drive of force-coupled ORCA (median 215 N)" and cannot reconcile that with "1.8–2.2 times larger" in the abstract). Apply the same fix to the Fig. 4 caption at `05_deadlock_physics.tex:8`: "rest drives of SFM (grey) and the added rest drive of force-coupled ORCA (RVO2, hatched)".

12-2 | `06_screening.tex:19,29,48`; `table2_signatures.tex:31`; `table3a_noise.tex:30` | 12 | "noise from ORCA", "the ORCA replays", "noise and ORCA do", "bias and ORCA", "+$b$ (ORCA)", "snapshots (ORCA)", "outcome (ORCA)" | "force-coupled ORCA (RVO2)" in text (or "force-coupled ORCA" where both solvers are meant); in the table notes "(force-coupled ORCA)" | medium | error (house rule)

12-3 | `06_screening.tex:2,16,45`; `08_discussion.tex:4`; `01_introduction.tex:22`; `table2_signatures.tex:31` | 12 | "Reshape (lateral)", "a Glitch", "Reshape (axial)", "Force-coupled ORCA is Reshape at the pair", "(Reshape, axial subtype)", "(Reshape, lateral subtype)", "Reshape (axial, lateral)", "Reshape, solver-dependent" | "Reshape, lateral"; "Glitch"; "Reshape, axial"; "Force-coupled ORCA is Reshape, axial, at the pair"; "(Reshape, axial)"; "(Reshape, lateral)"; "Reshape, axial or lateral"; "Reshape, axial, with solver-dependent freed fraction" | medium | error (house rule)

12-4 | `04_protocol.tex:4`; `table2_signatures.tex:5`; `04_protocol.tex:12`; `06_screening.tex:51`; `fig_protocol.tex:28,36` | 12 | "frozen deadlocks", "a frozen deadlock", "the same frozen deadlocks", "At a frozen deadlock" | "snapshots", "a snapshot", "the same snapshots", "At a snapshot" | low | error (house rule: one name)

12-5 | `05_deadlock_physics.tex:18,39,41,43`; `06_screening.tex:24`; `05_deadlock_physics.tex:35`; `04_protocol.tex:48` | 12 | "restarted with the blocker alone", "We restarted", "restarts per level", "alone restarts", "restarts never escape", "The SFM restart", "restarts at $\beta=5$--7", "An escape run ends" | "quenched with the blocker alone", "We quenched", "quenches per level", "quenches in the alone condition", "quenches never escape", "The SFM quench", "quenches at $\beta=5$--7"; at 4.5 add "An escape run is a noise quench that ends ..." | medium | error (house rule: one name for quench)

12-6 | `05_deadlock_physics.tex:22`; `01_introduction.tex:28`; `05_deadlock_physics.tex:48`; `08_discussion.tex:10`; `085_recommendations.tex:6`; `03_pedestrian_model.tex:63` | 12 | "Rounded jamb ends", "rounded segment ends", "jamb ends rounded", "rounded door edges remove the standoff", "round the door edges", "rounds each jamb into a capsule" | Use "rounded segment ends ($r_c=0.1$\,m)" in every place. In 3.4 write "rounds each segment end into a capsule of radius $r_c$". | medium | error (four names for one variant)

12-7 | `05_deadlock_physics.tex:22`; `085_recommendations.tex:2`; `09_conclusions.tex:2` | 12 | "Each wall law gives", "describes its wall law and steering terms", "describes the wall law and steering terms" | "Each wall-range variant gives", "is set by its wall range, segment ends and steering terms", "is set by the wall range, segment ends and steering terms" | medium | error ("wall law" is undefined)

12-8 | `04_protocol.tex:48`; `05_deadlock_physics.tex:39` vs `03_pedestrian_model.tex:36,40` | 12 | "passes the gate", "gate-accepted" vs "density gate", "The gate is at least" | Keep "gate" for $w_{o,i}$, and use "accepted" or "acceptance test" for barriers (11-6) | medium | error (overloaded term)

12-9 | `05_deadlock_physics.tex:57` | 12 | "no contact arch persists at the tested drives", "at 2\,m/s and the default drive none form, and all \RunNFiveDefaultN\ default-drive runs" | "at the tested desired speeds", "at 2\,m/s and at the default desired speed none form, and all \RunNFiveDefaultN\ runs at the default desired speed" | medium | error ("drive" means a force everywhere else)

12-10 | `05_deadlock_physics.tex:48` | 12 | "a minimum survives when the overhang exceeds $r_c$" | Define it where it first appears: "the inner member's centre lies \RevBfiveOverhangMin--\RevBfiveOverhangMax\,mm beyond the door edge (the overhang)" | medium | error (a term used with a threshold and never defined)

12-11 | `05_deadlock_physics.tex:52` | 12 | "for the lower of the two signs, $b_f=$" | "taking the sign with the smaller threshold, $b_f=$" | medium | error (clashes with "lower member", which in 6.3 means the member at $y<5$ m)

12-12 | `02_related_work.tex:3` | 12 | "The TTC law makes the interaction energy fall off" | "The time-to-collision (TTC) law makes the interaction energy fall off" | medium | error (acronym used before definition)

12-13 | `06_screening.tex:16` | 12 | "($\Delta$RMST $\RevAsevenPushLoneTimeEff$\,s," | Define it in `04_protocol.tex:51`: "times to free are compared by the restricted mean survival time up to $T$ (RMST)". The text use can stay. | medium | error (RMST is never expanded; the Table 3a note gives a paraphrase only)

12-14 | `02_related_work.tex:9` | 12 | "the BBK scheme is off by $O(\Delta t)$" | "the Brünger–Brooks–Karplus (BBK) scheme is off by $O(\Delta t)$" | low | error

12-15 | `00_abstract.tex:3`; `01_introduction.tex:11`; `08_discussion.tex:4` | 12 | "at a stated horizon", "at a named horizon $T$", "at a stated horizon $T$" | "at horizon $T$" in all three | low | taste

12-16 | `02_related_work.tex:9`; `04_protocol.tex:48`; `table1_params.tex:30`; `05_deadlock_physics.tex:35` (Fig. 6 axes) | 12 | Symbols: $T$ as temperature in "$\exp(-\Delta U/k_{\rm B}T)$" and as horizon; "$\beta_{\mathrm{ref}}=3.5$" vs "$\beta=3.5$"; axis "$\Delta U_{\rm cond}$" vs text "$\Delta U$"; axis "$-s/\Delta U$" ($s$ as slope) vs sigmoid $s(x;x_0,c)$ (`03:40`); $J$ as Jaccard index and as joule; $\sigma$ as noise SD and in $\mathcal N(\mu,\sigma)$ (Table 1); $\mu_1$ eigenvalue vs $\mu$ mean (Table 1) | Write $T_{\rm b}$ (bath temperature) at `02:9`; use "$\beta=3.5$" at `04:48`; use $\Delta U$ on Fig. 6; rename the sigmoid to $\varsigma$ or the slope to $a$; keep $J$ but never write "$J$" next to joules without "J =" (taste); write $\mathcal N(\text{mean},\text{SD})$ in the Table 1 caption | low | error for $T$ and $\beta_{\rm ref}$; taste for the rest

12-17 | `03_pedestrian_model.tex:4,47`; `02_related_work.tex:9`; `04_protocol.tex:28`; `06_screening.tex:16`; `085_recommendations.tex:7` | 12 | "The social force model takes", "The drive part is therefore the SFM with relaxation time", "The equilibrium form applies to SFM with additive noise", "the SFM rest field is $-\nabla U$", "the drive part at rest is the SFM with relaxation time $\tau'$", "force-coupled ORCA at rest is the SFM with relaxation time $\tau'$" | "This social force model takes"; "The drive part is therefore this social force model with relaxation time"; "The Arrhenius–Kramers form applies to this social force model with additive noise"; "the rest field of this social force model is $-\nabla U$"; "the drive part at rest is this social force model with relaxation time $\tau'$"; "force-coupled ORCA at rest is this social force model with relaxation time $\tau'$" | medium | error (house rule: "this social force model" when the claim is general; "SFM" stays as a variant label in 5–7)

12-18 | `01_introduction.tex:13`; Fig. 5 x-axis label (`figures/fig3_width_walls.pdf`) | 12 | "at a 0.8\,m exit"; "exit width w (m)" | "at a 0.8\,m door"; "door width $w$ (m)" | low | error

## 13. Numbers and internal consistency (13)

13-1 | `05_deadlock_physics.tex:39` vs `04_protocol.tex:48` | 13 | "We restarted \EfourN\ of the \FixAthreeEfourQual\ gate-accepted snapshots" [10 of the 32] vs "\LoneBarN\ of \FinBarLibN\ lone-trap snapshots pass" [56 of 60] | State the criterion that reduces 56 to 32. If the 32 are those accepted in all three conditions, write: "We quenched \EfourN\ of the \FixAthreeEfourQual\ snapshots whose barriers are accepted in all three conditions". | high | error (two counts for the same accepted set)

13-2 | `07_experiments.tex:12` | 13 | "\RevDFourDonethirtyPassed\; duplicate track IDs merged" | "\RevDFourDonethirtyPassed; duplicate track IDs merged" | high | error (`\;` is a math thick space, so the PDF reads "and 128 duplicate track IDs merged in 4D040 and 4D110")

13-3 | `05_deadlock_physics.tex:16` (macro `\StuckAloneN` in `numbers.tex:537`) | 13 | "of the \StuckAloneN\ spawned agents" [renders "20000"] | "of the 20\,000 spawned agents". Set the macro to `20\,000`. | high | error (house rule)

13-4 | `06_screening.tex:45` | 13 | "The rest field accounts for \RevAelevenPairDiscStatic\ of these \RevAelevenPairDisc\ standoffs;" [13 of these 28] | "Of the \RevAelevenPairDisc\ standoffs on which the drive part and force-coupled ORCA (RVO2) disagree, the rest field accounts for \RevAelevenPairDiscStatic;". Confirm that 28 is that discordant count, since 33 − 7 = 26 net. | high | error (no antecedent with 28 members)

13-5 | `00_abstract.tex:3`; `05_deadlock_physics.tex:2,48` vs `05_deadlock_physics.tex:22` | 13 | "the pair standoff ... needs ... a short wall range" vs "With the default walls \EsevenDefaultCollective\ of \EsevenDefaultClassified\ classified deadlocks are pair or group standoffs" [2 of 98]; also "Each wall law gives one deadlock type" | Abstract: "the pair standoff needs sharp door-edge segment ends and dominates when the wall range is lowered to 0.04\,m." Line 22: "Each wall-range variant has one dominant deadlock type". | medium | error (generalisation contradicted two sentences later)

13-6 | `05_deadlock_physics.tex:45` | 13 | "$\beta$ has median \RevAthreeSevenMed\ [\RevAthreeSevenQone, \RevAthreeSevenQthree]" | "$\beta$ has median \RevAthreeSevenMed\ (quartiles \RevAthreeSevenQone\ and \RevAthreeSevenQthree)" | medium | error (square brackets mean a 95% interval everywhere else)

13-7 | `table3a_noise.tex:12,14,19,24`; `table3b_bias.tex:13,18` | 13 | ΔRMST "19.3 [9.1, 29.1]", "19.4 [11.2, 27.3]", "−16.0 [−35.8, 3.1]", "71.9 [33.2, 110.1]", "−2.1 [−21.2, 17.5]", "−1.3 [−20.2, 18.1]" | "19 [9.1, 29]", "19 [11, 27]", "−16 [−36, 3.1]", "72 [33, 110]", "−2.1 [−21, 18]", "−1.3 [−20, 18]" | medium | error (Sect. 4.6 states that derived quantities carry two significant figures)

13-8 | `07_experiments.tex:21,25` | 13 | "\RevDThreeCThreeGapsTwo--\RevDThreeCSigGapsTwo\ gaps" [10.1–18.2], "\RevDThreeCOneGapCompleteMax\,s" [20.4], "\RevDThreeCEdgeGapCompleteMax" [15.6], "\RevDThreeCSigGapCompleteMax" [237.2], "\RevDThreeCSigGapKMMedian" [95.9], "\RevDThreeCOneGapLowerMedian\ and \RevDThreeCThreeGapLowerMedian" [416, 432], "\RevDThreeCThreeOpenMean" [446] | "10–18", "20", "16", "240", "96", "420 and 430", "450" | medium | error (two-significant-figure rule; "2.04 s" at line 19 stays because it is compared with 2 s)

13-9 | `05_deadlock_physics.tex:16`; `04_protocol.tex:41`; `table3b_bias.tex:13`; `04_protocol.tex:32` | 13 | "\EOneBStuckAloneFrac" [0.234]; "\TthreeRatioMean\ times" [1.00]; "$+b^\ast_{\rm legacy}=\PairBstarPub$" [0.0223] next to "$b^\ast_{\rm RVO2}$" [0.0091]; "\RevAtenMuMax" [1115 N/m] | "0.23"; "1.0"; "0.022"; "1100" | low | error (mixed precision; $w_{50}=0.878$ [0.874, 0.883] is kept at three figures because its interval needs them, which is taste)

13-10 | `table2_signatures.tex:23` vs `table3a_noise.tex:16` | 13 | "$|\ell|\le\EthreeCThreeLnRatioMax$" [≤ 0.018] vs force-coupled ORCA $\ell$ "\EthreeCThreeLnRatioFix" [−0.005] | Label both. In Table 2 write "flat, $\ell=\EthreeCThreeLnRatioFix$ (per snapshot $|\ell|\le\EthreeCThreeLnRatioMax$)", or whatever the two statistics are. | medium | error (two values for one quantity with nothing to tell them apart)

13-11 | `04_protocol.tex:48` vs `06_screening.tex:21`, `table3a_noise.tex:30` | 13 | "the \RevAfiveEthreeQual\ with full $\Delta U\ge3$\,J form the time-step pool" [36] vs "(\EthreeN\ snapshots; ...)" [20] | "the \RevAfiveEthreeQual\ with full $\Delta U\ge3$\,J are eligible, and \EthreeN\ of them, drawn at random, enter the time-step probe" (state the actual selection) | medium | error

13-12 | `00_abstract.tex:3`; `01_introduction.tex:29` vs `04_protocol.tex:15` | 13 | Abstract: "Replay, time-step dependence, time to free and whole-run final states separate noise from force-coupled ORCA". Introduction: "Four probes separate noise (Heat) and the lateral bias ...". Sect. 4.2: "the other probes are empirical, and time to free, overlap $J$ and final-state class serve as paired effect sizes" | `01:29`: "Replay, the time-step probe, time to free and the whole-run final state separate noise (Heat) from force-coupled ORCA, and handedness under the tilt probe separates the lateral bias (Reshape, lateral)". `04:15`: "Replay, per-step $\Delta t$ dependence and bias sign separate the classes by definition (${}^\dagger$); time to free, overlap $J$ and final-state class are compared by paired tests." | medium | error ("four probes" is not enumerated anywhere, and 4.2 calls two of the abstract's separators effect sizes rather than probes)

13-13 | `06_screening.tex:51` | 13 | "frees no deadlock, as the identity of Sect.~\ref{sec:identity} requires." | "frees no deadlock: at a snapshot it adds no rest drive." | medium | error (subject and verb mismatch semantically; Eq. (7) concerns force coupling, and the filter's argument is the slack bound in the next sentence)

## 14. Structural and framing problems (6)

14-1 | `00_abstract.tex:3` and `01_introduction.tex:9` | 14 | The abstract's first sentence, "Crowd simulations credit how often agents deadlock at narrow doors, and how the deadlocks clear, to the steering terms a model adds.", is repeated verbatim in the introduction and supported there only by "~\cite{gang2026}". | Introduction opener: "Simulation studies attribute how often agents deadlock at a narrow door, and how the deadlocks clear, to the steering terms a model adds~\cite{gang2026,xu2021}." Add any further practice-level citation available. | medium | error (verbatim repetition; a field-wide claim resting on one self-citation)

14-2 | `00_abstract.tex:3`; `01_introduction.tex:28-31`; `06_screening.tex:2`; `08_discussion.tex:4`; `09_conclusions.tex:2`; `085_recommendations.tex:2`; `07_experiments.tex:25` | 14 | The CroMa flow ratio "\RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow" appears four times (abstract, contribution 4, Sect. 7 end, Conclusions). The three-mechanism claim appears five times (abstract, contributions 2, 6 opener, 8.1, Conclusions). "deadlock count ... describes ... wall law and steering terms" appears twice (`085:2`, `09:2`). | The contributions should name the result type and point to its section without numbers: for example, "In the CroMa bottleneck experiments every model variant falls short of the human flow (Sect.~\ref{sec:validity})". Sect. 8.1 shrinks to 3-1. `085:2` takes 10-8, which leaves the Conclusions as the only place for the reading rule. | medium | error

14-3 | `02_related_work.tex:3,6,9` | 14 | Results and model statements inside Related Work: "This model adds TTC and ORCA as force terms, each switchable at a snapshot." (3); "Without static friction, this model deadlocks in rest states of a driven, damped system." (6); "Our fixed per-step noise has a $\Delta t$-dependent effective temperature (Sect.~\ref{sec:teff}), which we use as a probe. The equilibrium form applies to SFM with additive noise, whose rest field at frozen densities is a gradient. The constraint part of force-coupled ORCA makes the pair rest field non-gradient," (9) | Move the line-3 sentence to `03_pedestrian_model.tex:4`. Move the line-6 sentence to `05_deadlock_physics.tex:2`. Move the three line-9 sentences to the head of `04_protocol.tex:36` (4.4) and to `04_protocol.tex:34`, which already says the ORCA rest field is non-gradient, so that sentence can be deleted. Keep "for self-propelled noise the rate depends on the whole barrier shape~\cite{woillez2019}" in Related Work as "For self-propelled noise the escape rate depends on the whole barrier shape~\cite{woillez2019}." | medium | error (a reviewer reading Related Work for context meets unsupported claims about this model)

14-4 | `03_pedestrian_model.tex:40` and `08_discussion.tex:10` | 14 | Native ORCA is called untested twice | See 4-12 | low | error

14-5 | `08_discussion.tex:7` | 14 | "Multi-robot deadlocks are also closed-loop equilibria, which Grover et al.\ resolve with a switching controller because additive perturbations carry no guarantee~\cite{grover2023}." | "The pair standoff is a closed-loop equilibrium of the kind Grover et al.\ resolve with a switching controller~\cite{grover2023}; here the lateral bias frees it past $b_f$ and noise at $\beta<1$ (Sect.~\ref{sec:pair})." | low | taste (Discussion repeats Related Work; the replacement ties it to this paper's result)

14-6 | `09_conclusions.tex:2` | 14 | "The deadlocks of this social force model at a narrow door are rest states made by the door-edge geometry," | "The deadlocks of this social force model at a narrow door are rest states set by the wall range and the shape of the door-edge segment ends," | medium | error (the conclusion contradicts Sect. 5.1, which says the wall range, a force parameter, sets the lone trap)

Checked and fine: the paper ends with Conclusions, not Limitations. A Recommendations section exists and is actionable. No result needs a later repair sentence; forward references (`03:36` to 6.1, `05:41` to 6.1) are single pointers.

## 15. Spelling and convention consistency (8)

Spelling is British throughout ("modelling", "behaviour", "neighbour", "centre", "discretised", "normalised", "idealises", "favoured"). The one exception comes from the class file.

15-1 | `10_back_matter.tex:5` (llncs `\ackname`) | 15 | "\subsubsection*{\ackname}" [renders "Acknowledgments."] | Put `\renewcommand{\ackname}{Acknowledgements.}` in `main.tex` | low | taste (the competing convention is the publisher default; Springer accepts either)

15-2 | `085_recommendations.tex:9` | 15 | "completion, flow, and passage gaps" | "completion, flow and passage gaps" | low | error (the only serial comma in the paper; the other lists, such as the abstract's "Replay, time-step dependence, time to free and whole-run final states", omit it)

15-3 | `05_deadlock_physics.tex:8,16,27`; `06_screening.tex:16,51` vs `07_experiments.tex:14,21,23,25`; `03_pedestrian_model.tex:47`; `085_recommendations.tex:7` | 15 | "of SFM", "The SFM drive", "SFM runs", "SFM and SFM+TTC", "under SFM", "that SFM also holds" vs "the SFM", "The SFM deadlocks", "for the SFM" | Use the bare label "SFM" for the variant, as in "SFM and SFM+TTC": "SFM deadlocks in", "for SFM". Use "this social force model" for the model (12-17). | low | taste

15-4 | `02_related_work.tex:9`; `05_deadlock_physics.tex:39`; `06_screening.tex:31` vs `04_protocol.tex:7,37,39,41,43,48` | 15 | "k_{\rm B}" vs "k_{\mathrm{B}}" (they render the same) | Define `\newcommand{\kB}{k_{\mathrm B}}` and use it everywhere, including `fig1_caption.tex` (8-2) | low | taste

15-5 | Fig. 4 y-axis (`figures/fig2_lone_trap.pdf`); `05_deadlock_physics.tex:57`; `05_deadlock_physics.tex:48`; `06_screening.tex:26` | 15 | "$v_0/\tau$ (m s$^{-2}$)" vs solidus everywhere in the text ("m/s", "N/m", "kg/s$^2$"); overlaps "4.0\,cm", "26\,cm" vs "0.26--59\,mm" and "mm/s" vs "m" elsewhere | "$v_0/\tau$ (m/s$^2$)"; overlaps "40\,mm" and "260\,mm", or "0.040\,m" and "0.26\,m" | medium | error (house rule: units in one style)

15-6 | `07_experiments.tex:12`; `03_pedestrian_model.tex:50`; `05_deadlock_physics.tex:20` vs `06_screening.tex:29`, `07_experiments.tex:19` | 15 | "$w_{50}=\RevBtwoWfifty$\,m [\RevBtwoWfiftyLo, \RevBtwoWfiftyHi]" (unit before interval) vs "$\sigma_{50}=\EfiveSigmaFifty$ [\FixAsixSigFiftyClLo, \FixAsixSigFiftyClHi]\,m/s" and "\RevDHumanFlow\ [...]\,ped/s" (unit after) | "$w_{50}=\RevBtwoWfifty$ [\RevBtwoWfiftyLo, \RevBtwoWfiftyHi]\,m", here and at `01_introduction.tex:28` | low | error

15-7 | `01_introduction.tex:28`; `05_deadlock_physics.tex:22`; `06_screening.tex:16`, `06_screening.tex:31` | 15 | "forms in \RevBfiveGenPair\ of \RevBfiveGenN\ runs" [0 of 320]; "rounding leaves \EsevenRoundCollective\ pair or group standoffs" [0]; "frees \EtwoLKConstrRVOFreed\ (RVO2) and \EtwoLKConstrPubFreed\ (legacy)" [0 and 0]; "\EsixNoiseCollective\ group standoffs" [0] | "forms in none of \RevBfiveGenN\ runs"; "rounding removes every pair and group standoff"; see 9-7; "no group standoff" | low | taste (the paper elsewhere writes "none of 200 agents", "free none of the 60 snapshots")

15-8 | `07_experiments.tex:14,21` vs `03_pedestrian_model.tex:11` | 15 | "SFM + noise $\sigma^\ast$" vs "SFM+TTC" | "SFM+noise $\sigma^\ast$" | low | taste

## 16. Anything else (14)

16-1 | `06_screening.tex:21` | 16 | "So does the time step (\EthreeN\ snapshots; Fig.~\ref{fig:escape}(c), column $\ell$):" | "The time step also separates noise from force-coupled ORCA (\EthreeN\ snapshots; Fig.~\ref{fig:escape}(c); Table~\ref{tab:matched-noise}, column $\ell$):". Move the bias sentence at the end of line 19 ("The lateral bias frees no lone keystone ...") to the end of this paragraph. | high | error (the elliptical opener now follows "The lateral bias frees no lone keystone", so it says the time step frees no lone keystone; "column $\ell$" also points at a figure, which has no columns)

16-2 | `01_introduction.tex:9` | 16 | "Under equifinality, where many mechanisms reproduce one observable~\cite{beven2006}, it cannot show that the two act alike." | "Under equifinality, where many mechanisms reproduce one observable~\cite{beven2006}, a matched outcome cannot show that the surrogate and the steering term act alike." | medium | error ("it" and "the two" have no antecedent pair in the sentence before)

16-3 | `01_introduction.tex:11` | 16 | "Probes from the rest-state physics screen force-coupled ORCA on the same snapshots against two fraction-matched surrogates," | "Probes derived from the rest-state physics (Sect.~\ref{sec:signatures}) test force-coupled ORCA and two fraction-matched surrogates on the same snapshots:" | medium | error (it is not clear what "probes from the physics" are, and "on the same snapshots" has no prior set)

16-4 | `03_pedestrian_model.tex:50` | 16 | "Noise $\boldsymbol\xi$ has independent Gaussian components of standard deviation $\sigma$, per step or $\sigma\sqrt{\Delta t/0.01\,{\rm s}}$." | "Noise $\boldsymbol\xi$ has independent Gaussian components of standard deviation $\sigma$ per step (per-step noise) or $\sigma\sqrt{\Delta t/0.01\,{\rm s}}$ ($\sqrt{\Delta t}$-scaled noise)." | medium | error (the two noise types are used as named probes later and are named nowhere else)

16-5 | `00_abstract.tex:3`; `01_introduction.tex:31`; `07_experiments.tex:25`; `09_conclusions.tex:2` | 16 | "the model passes \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow" (and "every variant passes" ×3) | "the model's flow is \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow" | medium | taste (agents pass a door; a model does not pass a fraction of a flow)

16-6 | `00_abstract.tex:3` | 16 | "The lone trap, a blocker held alone by the door-edge wall force, is set by the wall range;" | "The lone trap, a blocker held at rest by the door-edge wall force without help from neighbours, is set by the wall range;" | low | error ("alone" can attach to "held" or to "force")

16-7 | `00_abstract.tex:3` | 16 | "separate noise from force-coupled ORCA, and handedness the bias." | "separate noise from force-coupled ORCA, and handedness separates the bias." | low | taste (the gapped verb across a comma makes the reader parse it twice)

16-8 | `05_deadlock_physics.tex:45` | 16 | "At the noise fraction-matched at the lone trap at $T=120$\,s ($\sigma=0.07$\,m/s, Sect.~\ref{sec:att-lone}), $\beta$ has" | "For the noise level fraction-matched at the lone trap ($\sigma=0.07$\,m/s, $T=120$\,s; Sect.~\ref{sec:att-lone}), $\beta$ has" | low | error (three stacked "at" phrases)

16-9 | `05_deadlock_physics.tex:22` | 16 | "With $B_{w,\rm edge}=0.04$\,m on the jambs \EsevenBjambCollective\ of \EsevenBjambClassified\ are," | "With $B_{w,\rm edge}=0.04$\,m on the jambs, \EsevenBjambCollective\ of \EsevenBjambClassified\ classified deadlocks are pair or group standoffs," | low | error (an elliptical predicate across sentences)

16-10 | `03_pedestrian_model.tex:63` | 16 | "A third rounds each jamb into a capsule" | "A third variant rounds each segment end into a capsule" | low | error ("A third" after two verb clauses has no noun to count)

16-11 | `04_protocol.tex:41` | 16 | "$\propto1/\Delta t$ at fixed per-step $\sigma$ up to the last factor, which alone remains for $\sqrt{\Delta t}$-scaled noise." | "This is proportional to $1/\Delta t$ at fixed per-step $\sigma$, apart from the last factor; for $\sqrt{\Delta t}$-scaled noise the last factor is the whole $\Delta t$ dependence." | low | taste (a sentence opening with a symbol)

16-12 | `06_screening.tex:48` | 16 | "Read off the thresholds $b_f$ of the same snapshots, $b^\ast$ reproduces each solver's freed fraction" | "The bias $b^\ast$, read off the thresholds $b_f$ of the same snapshots, reproduces each solver's freed fraction" | low | taste (an inverted participial opener)

16-13 | `table2_signatures.tex:24` | 16 | "\tl{flips}{vanish}" | "\tl{flips}{vanish (RVO2)}" | low | taste (the cell reads as a two-word clause)

16-14 | Section openers (house rule: open with the finding or the scope) | 16 | `04_protocol.tex:18` "Stack the $n$ residual agents into $\mathbf{x},\mathbf{v}\in\mathbb R^{2n}$, freeze the densities and split the force as"; `08_discussion.tex:7` "Granular and pedestrian clogging is read through arches and clog-lifetime statistics~\cite{zuriguel2014,nicolas2018trap};" | `04:18`: "With densities frozen, the force on the $n$ residual agents, stacked into $\mathbf{x},\mathbf{v}\in\mathbb R^{2n}$, splits as". `08:7`: "Here noise frees the lone trap by activated escape over the model's own barriers, with the attempt rate fitted as in trap models; granular and pedestrian clogging is read through arches and clog-lifetime statistics~\cite{zuriguel2014,nicolas2018trap}." | low | taste

Also checked under this category, with nothing further to report: a heading or opener phrased as a question (none); the banned words "exact" (only "Fisher's exact test", a proper name, which stays), "comparable", "shallow", "hard-driven", "slow creep" (one "creeping", at 4-7), "like for like" and "usual" (none); "only" (`04_protocol.tex:7` "acts only while the crowd moves", see H-1; `fig_protocol.tex:36` "share a mechanism only if no probe separates them" is a logical condition and stays); "if and only if" appears once (`05_deadlock_physics.tex:12`, Sect. 5.1, allowed); "rate" is used only for escape quantities (escape rate, attempt rate, log rate ratio), which complies.

## House-rule items not covered above (1)

H-1 | `04_protocol.tex:7` | house rule ("only") | "\emph{Prevent} acts only while the crowd moves: it changes how often deadlocks form and leaves a snapshot held." | "\emph{Prevent} acts while the crowd moves and vanishes at rest: it changes how often deadlocks form and leaves a snapshot held." | medium | error

---

## Entry counts

| Category | Entries |
|---|---|
| 1 Rhetorical negation | 9 |
| 2 Self-announcing significance | 1 |
| 3 Roadmap / restated paragraphs | 4 |
| 4 Trailing appositives | 13 |
| 5 Softening adverbs / undefined evaluatives | 9 |
| 6 "What" and clefts | 0 |
| 7 Headings | 6 |
| 8 Captions | 7 |
| 9 Run-ons | 12 |
| 10 Aphoristic endings | 9 (1 kept) |
| 11 Process leakage | 9 |
| 12 Terminology / notation | 18 (plus the concept table) |
| 13 Numbers / consistency | 13 |
| 14 Structure / framing | 6 |
| 15 Conventions | 8 |
| 16 Other | 14 |
| House rule ("only") | 1 |
| **Total** | **139** |

## Triage: the five changes that most improve a skeptical reviewer's reading

1. **Settle the rest-drive terminology (12-1, with 4-10 and the Fig. 4 caption).** Today the 214 N SFM drive and the 215 N "rest drive of force-coupled ORCA" in Sect. 5.1 read as contradicting the abstract's "1.8–2.2 times larger", and that is the paper's central identity. This takes about 20 minutes.
2. **Fix the three count contradictions: Table 3a caption vs Sect. 6.1 second traps (8-1), 56 vs 32 accepted barriers (13-1), and 36 vs 20 time-step snapshots (13-11), plus "these 28" (13-4).** A reviewer who checks one number and finds it inconsistent stops trusting the rest. This takes about 45 minutes, including checking which selection each macro reflects.
3. **Repair the broken references and render defects: "So does the time step" (16-1), the `\;` in Sect. 7 (13-2), the `\pending` placeholders (11-1), "20000" (13-3) and the italic k_B in Fig. 1 (8-2).** These are mechanical, visible in the PDF and read as carelessness. This takes about 20 minutes, plus whatever time the acknowledgements text needs.
4. **Split the worst sentences in Sect. 6 and 5.2 (9-1, 9-2, 9-3, 9-7, 9-8) and remove the "overlap does not separate" tic (1-1 to 1-3).** Section 6 carries the evidence, and these sentences are where a reviewer loses the thread. This takes about 40 minutes.
5. **Cut the repetition and unify the names: the abstract/intro verbatim opener and the four CroMa restatements (14-1, 14-2, 3-1), bare "ORCA" and the class notation (12-2, 12-3), and "this social force model" (12-17).** This frees about a third of a page under the 25-page limit and removes the impression of a paper restating itself. This takes about 60 minutes.
