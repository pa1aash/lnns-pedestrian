# Prose audit (W): whole paper

Standard: waveA/prose_prompt.md plus the common brief (vocabulary v2, PRE register, no \paragraph leads). Read from the sources and from the compiled text (pdftotext of paper/main.pdf). Anchors are file:line in the sources as they stood before this pass (paper/sections/ unless noted). Every applied entry keeps its meaning and every number; the build stays at 24 pages, with no overfull boxes or undefined references (checked with make paper, pdfinfo and a grep of main.log); the text ends where it ended before, and the Conclusions are one line shorter.

Status: **applied** = defect, fixed in the source. **declined** = taste, or a fix outside the files of this pass (registry, figures, table bodies), with the reason. **kept / none** = checked; nothing to change.

## Counts

| Category | Entries | Applied | Declined |
|---|---|---|---|
| 1. Rhetorical negation | 4 | 0 | 0 |
| 2. Sentences that announce their own significance | 1 | 0 | 0 |
| 3. Sentences that announce what a section will do | 5 | 3 | 2 |
| 4. Trailing appositive qualifications | 4 | 3 | 1 |
| 5. Softening adverbs on binary claims | 4 | 0 | 3 |
| 6. Sentences beginning with "What" and other clefts | 1 | 0 | 0 |
| 7. Headers and bold paragraph leads | 2 | 1 | 0 |
| 8. Figure and table captions | 6 | 2 | 3 |
| 9. Run-on and over-nested sentences | 9 | 9 | 0 |
| 10. Aphoristic paragraph endings | 1 | 0 | 0 |
| 11. Process-record and internal-code leakage | 3 | 1 | 1 |
| 12. Terminology and notation drift | 16 | 12 | 3 |
| 13. Numbers and internal consistency | 4 | 1 | 3 |
| 14. Structural and framing problems | 5 | 4 | 1 |
| 15. Spelling and convention consistency | 6 | 5 | 0 |
| 16. Anything else | 11 | 9 | 1 |

## 1. Rhetorical negation

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| K1 | 03_pedestrian_model.tex:35 | `(with $v_0$, not $v_{\rm eff}$)` | `keep` | kept / none | Kept: technical contrast; the preferred velocity of ORCA differs from the drive's target speed of Eq. (2) and the contrast carries that information. |
| K2 | 07_experiments.tex:23 | `Removing deadlocks does not restore capacity.` | `keep` | kept / none | Kept: a negative result with its numbers in the next sentence (0.57 of the human flow), not a 'not X but Y' frame. |
| K3 | 05_deadlock_physics.tex:45 | `The computed path of the latter is not its dynamical escape route.` | `keep` | kept / none | Kept: the plain negative is the finding (20 restarts never escape); no Y is withheld. |
| K4 | 06_screening.tex:25 | `The data give no evidence that identity separates them` | `applied as S3 for the term; negation kept` | kept / none | Kept as negation: the overlap intervals are [0.00, 1.00], so 'no evidence' is the exact statement; 'does not separate' would overclaim. |

## 2. Sentences that announce their own significance

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| K5 | whole paper | `(searched: notably, crucially, importantly, worth, significant(ly), key point, what matters)` | `none` | kept / none | No instance found. |

## 3. Sentences that announce what a section will do

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| M5 | 03_pedestrian_model.tex:46 | `is the permitted velocity nearest to the preferred velocity $\mathbf u$. Velocity coupling has no rest drive.` | `is the permitted velocity nearest to the preferred velocity $\mathbf u$.` | applied | Result stated in the model section before its derivation in Sect. 6.4, where it is stated again; deleted here. |
| P5 | 04_protocol.tex:7 | `A perturbation acts on a deadlock in one of five ways. \textbf{P}` | `A perturbation acts on a deadlock in one of five ways (responses to each probe in Table~\ref{tab:signatures}). \textbf{P}` | applied | Table pointer moved into the sentence that introduces the classes (see P6). |
| P6 | 04_protocol.tex:8 | ` Table~\ref{tab:signatures} gives each class's response to each probe. The Jaccard index` | ` The Jaccard index` | applied | Sentence that only announces a table; folded into P5. |
| K6 | 05:2, 06:2, 07:9, 08:2; subsection openings 05:12, 05:39, 05:50, 05:61 | `This section determines ... / This subsection tests whether ...` | `keep` | declined | Declined: these openings state the question each section answers, as the register (common brief, decision 7) requires; they do not summarise the paragraphs beneath them. |
| K7 | 01_introduction.tex:15 | `The contributions are:` | `keep` | declined | Taste: standard lead-in to the contribution list; the competing convention runs the list without a lead. |

## 4. Trailing appositive qualifications

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| I1 | 01_introduction.tex:9 | `Our earlier work tested such a credit at the level of rates, with a surrogate tuned to a mechanism's headline rate~\cite{gang2026}; the present work supersedes that reading.` | `Our earlier work tested such a credit with a surrogate tuned to a mechanism's headline rate~\cite{gang2026}; here we test the mechanism.` | applied | Trailing clause with an unclear antecedent ('that reading') that narrates a revision; replaced by the claim it stands for. Shortened form of I1 ('at the level of rates' is carried by 'headline rate'). |
| S5 | 06_screening.tex:36 | `the completion fit of Sect.~\ref{sec:escape} inverted at the completion of ORCA (RVO2), on the same spawns.` | `the completion fit of Sect.~\ref{sec:escape} inverted at the completion of ORCA (RVO2), run on the same spawns.` | applied | Dangling trailing modifier: 'on the same spawns' attaches to 'the completion of ORCA'; it describes the surrogate runs. |
| X5 | 07_experiments.tex:12 | `two with a 2.0\,m corridor behind the entrance and three with a 0.21\,m one, a door in a wall.` | `two with a 2.0\,m corridor behind the entrance and three with a 0.21\,m one (a door in a wall).` | applied | Trailing appositive reads as a third corridor type; it glosses the 0.21 m corridor. |
| K8 | 05_deadlock_physics.tex:61 | `..., soft-core analogues of one- and two-grain arches held by repulsion of range $B_w$ without contact or friction.` | `keep` | declined | Taste: the appositive is the interpretive claim of the paragraph, not a hedge; promoting it to its own sentence adds a line. |

## 5. Softening adverbs on binary claims

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| K9 | 05_deadlock_physics.tex:16 | `The SFM drive (median \DriveCOneMedian\,N) is comparable to $g_{\max}$ at the mean radius` | `lies between $g_{\max}$ at $r=0.25$ and $0.35$\,m` | declined | Declined: 'comparable' is undefined, but the precise replacement hard-codes an ordering of three registry values (156 < 214 < 543 N) that the macros may change; the numbers beside it already let the reader judge. |
| K10 | 04_protocol.tex:48 | `negligible in our snapshots` | `give the size of $(\omega\Delta t)^2$` | declined | Declined: no registry value for $(\omega\Delta t)^2$ exists and the text may not carry hand-typed results; flag for the authors. |
| K11 | 05_deadlock_physics.tex:58 | `the pair needs a few seconds of deterministic run-out` | `give the run-out time` | declined | Declined: no registry value; flag for the authors. |
| K12 | 05_deadlock_physics.tex:12; 05:18; 06:54 | `grows steeply; rarely complete; constrains $b^\ast$ weakly` | `keep` | kept / none | Kept: each adverb sits next to the numbers that define it (83/156/543 N; 4 of 200; interval widths). |

## 6. Sentences beginning with "What" and other clefts

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| K13 | whole paper | `(searched: sentence-initial What, It is, There is/are)` | `none` | kept / none | No cleft or expletive found. |

## 7. Headers and bold paragraph leads

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| Q2 | 08_discussion.tex:7 | `\subsection{Deadlocks, Clogging and Robot Deadlock}` | `\subsection{Relation to Clogging and Robot Deadlock}` | applied | Heading lists three topics joined by a comma and 'and'; the subsection relates the deadlocks to two literatures. Not in the author-set title list; no label. |
| K14 | section and subsection titles | `Sect. 1-9 and 5.1-6.4 titles` | `keep` | kept / none | Not audited for change: set by the authors (common brief, decision 6). |

## 8. Figure and table captions

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| F7 | 06_screening.tex:14 | `drive and constraint parts reddish purple, push $\pm$ reddish purple,` | `drive and constraint parts and push $\pm$ reddish purple,` | applied | Fig. 7 caption names the same colour twice in adjacent items; merged (shorter). |
| P7 | 04_protocol.tex:21 | `\caption{Screening protocol. The mechanism under test and its rate-matched surrogate are probed on the same frozen deadlocks, and each is assigned the class whose signatures it shows (Table~\ref{tab:signatures}).}` | `\caption{Screening protocol: the mechanism under test and its rate-matched surrogate are probed on the same frozen deadlocks and each is assigned a class.}` | applied | Fig. 2 caption restates step 4 of the protocol verbatim ('the class whose signatures it shows (Table 2)'); reduced to what the diagram shows. |
| K15 | figures/fig1_caption.tex:2 | `Fig. 1 caption, 2 sentences, about 95 words` | `keep` | declined | Declined: over 60 words, but every clause is a reading key (colour map, floor shading, arrow colours) found nowhere else; nothing restates the body. |
| K16 | 05_deadlock_physics.tex:8 | `Fig. 3 caption, 2 sentences, about 75 words` | `keep` | declined | Declined: legend content only (line styles, colours, panels); no claim or result. |
| K17 | make_table3.py:171 (Table 3 caption) | `3 sentences, about 95 words` | `keep` | declined | Declined: a column key for a table whose headers are one word each; cutting it moves the key into the text and adds length. No result appears only in the caption. |
| K18 | 05_deadlock_physics.tex:35 | `Fig. 5 caption` | `keep` | kept / none | Three sentences, plotting key only; compliant. |

## 9. Run-on and over-nested sentences

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| I2 | 01_introduction.tex:15 | `We then screen ORCA against rate-matched surrogates, perturbations of other mechanism classes tuned to ORCA's rate, by probes that the physics predicts, applied to the same frozen deadlocks.` | `We then screen ORCA against rate-matched surrogates, perturbations of other mechanism classes tuned to ORCA's rate, with probes predicted by the physics on the same frozen deadlocks.` | applied | Four comma-joined clauses; two trailing modifiers collapsed into one. |
| M1 | 03_pedestrian_model.tex:9 | `Three configurations switch terms on: SFM keeps the desired, social and wall forces, SFM+TTC adds $\mathbf F^{\rm ttc}_i$ and SFM+ORCA adds $w_{o,i}\mathbf F^{\rm orca}_i$.` | `Three configurations switch terms on: SFM keeps the desired, social and wall forces; SFM+TTC adds $\mathbf F^{\rm ttc}_i$; SFM+ORCA adds $w_{o,i}\mathbf F^{\rm orca}_i$.` | applied | Comma list nested in a comma list ('social and wall forces, SFM+TTC adds'); semicolons separate the three configurations. |
| M4 | 03_pedestrian_model.tex:35 | `Two solvers are used: the legacy linear-program solver, the original implementation, whose leg-normal sign defect is studied in Sect.~\ref{sec:att-lone}, and the RVO2 solver,` | `Two solvers are used: the legacy linear-program solver of the original implementation, which has a leg-normal sign defect (Sect.~\ref{sec:att-lone}), and the RVO2 solver,` | applied | Appositive inside an appositive inside a two-item list; the inner one folded into the noun phrase. |
| D3 | 05_deadlock_physics.tex:22 | `to \EsevenBjambK\ ($p=\EsevenJambVsDefaultP$ against the default); adding the other walls makes no detectable difference.` | `to \EsevenBjambK\ ($p=\EsevenJambVsDefaultP$ against the default). Adding the other walls makes no detectable difference.` | applied | Four clauses joined by commas and a semicolon; split. |
| D6 | 05_deadlock_physics.tex:43 | `The Weibull shape of the escape times exceeds 1 pooled over the three conditions, \EfourWeib\ [\EfourWeibLo, \EfourWeibHi], and when pinned or alone, \EfourWeibFrozen\ [\EfourWeibFrozenLo, \EfourWeibFrozenHi] and \EfourWeibAlone\ [\EfourWeibAloneLo, \EfourWeibAloneHi]; in the full condition it is` | `The Weibull shape of the escape times exceeds 1 pooled over the three conditions (\EfourWeib\ [\EfourWeibLo, \EfourWeibHi]), pinned (\EfourWeibFrozen\ [\EfourWeibFrozenLo, \EfourWeibFrozenHi]) and alone (\EfourWeibAlone\ [\EfourWeibAloneLo, \EfourWeibAloneHi]). In the full condition it is` | applied | Worst sentence of the paper: five comma/semicolon-joined clauses with three appositive values whose referents are recovered only by position. Split into one claim and one exception. |
| D8 | 05_deadlock_physics.tex:61 | `(\ArchEpisodes\ episodes of up to \ArchSizeMax\ agents) and carry up to \ArchPeakForce\,kN of body compression, and break within` | `(\ArchEpisodes\ episodes of up to \ArchSizeMax\ agents), carry up to \ArchPeakForce\,kN of body compression and break within` | applied | 'X and Y, and Z' with a doubled conjunction; made a three-item predicate. |
| X7 | 07_experiments.tex:14 | `The velocity fluctuation is the standard deviation, root-mean-squared over both components, of each agent's smoothed velocity relative to its neighbours within 0.74\,m, in the waiting zone (0.3--2.5\,m in front of the entrance, within 2\,m of its axis) while the local mean speed is below 0.3\,m/s.` | `In the waiting zone (0.3--2.5\,m in front of the entrance, within 2\,m of its axis), while the local mean speed is below 0.3\,m/s, the velocity fluctuation is the standard deviation, root-mean-squared over both components, of each agent's smoothed velocity relative to its neighbours within 0.74\,m.` | applied | Five comma-joined clauses with the subject's definition split around an appositive and the conditions trailing; conditions moved first so the definition ends the sentence. |
| Q1 | 08_discussion.tex:5 | `A matched rate is therefore weak evidence of a shared mechanism; the probes separate each surrogate from ORCA, while the rest-drive push, of ORCA's class, agrees with it on every probe at the lone keystone.` | `A matched rate is therefore weak evidence of a shared mechanism. The probes separate each surrogate from ORCA, and the rest-drive push, of ORCA's class, agrees with it on every probe at the lone keystone.` | applied | Four clauses across a semicolon and 'while'; split. |
| C1 | 09_conclusions.tex:2 | `and a tilt of the pair minimum (bias), and the probes separate them; replays expose` | `and a tilt of the pair minimum (bias). The probes separate them, and replays expose` | applied | Four clauses across commas and a semicolon; split. |

## 10. Aphoristic paragraph endings

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| K19 | 01_introduction.tex:11 | `That reading is a claim about mechanism.` | `keep` | kept / none | Aphoristic endings counted: 4 (this one; 'The rate match is calibration only' (fixed, P2); 07:23 'its deadlocks are not human behaviour at this width'; 05:45 'The computed path of the latter ...'). This is the one that earns its place: it states the thesis the paper tests. The other two kept are ordinary result sentences. |

## 11. Process-record and internal-code leakage

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| S10 | 06_screening.tex:57 | `The results enter the pending row of Table~\ref{tab:matched}.` | `The results enter the last row of Table~\ref{tab:matched}.` | applied | 'pending row' is a drafting state, not a property of the table. |
| K20 | 06_screening.tex:57; 10_back_matter.tex | `\pending{...} placeholders` | `keep` | kept / none | Not prose: draft markers for results and back matter still to come; they fail the final build by design. |
| K21 | make_table1.py:58 (Table 1 'Update' row) | `speed cap $2v_0$ before the position update; rejection-sampled spawns; convex-union wall corners` | `remove the duplicate 'speed cap $2v_0$' from the 'Other forces' row` | declined | Declined: table body, generated from the parameter file by code I was not asked to change; the row repeats the speed cap of the 'Other forces' row. Flag for the authors. |

## 12. Terminology and notation drift

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| M2 | 03_pedestrian_model.tex:16 | `replaces $\hat{\mathbf e}_i$ in Eq.~\eqref{eq:des} by $(\hat{\mathbf e}_i+b\,\hat{\mathbf e}^{\perp}_i)/\|\hat{\mathbf e}_i+b\,\hat{\mathbf e}^{\perp}_i\|$.` | `replaces $\hat{\mathbf e}_i$ in Eq.~\eqref{eq:des} by $(\hat{\mathbf e}_i+b\,\hat{\mathbf e}^{\perp}_i)/\|\hat{\mathbf e}_i+b\,\hat{\mathbf e}^{\perp}_i\|$, with $\hat{\mathbf e}^{\perp}_i$ the unit normal to $\hat{\mathbf e}_i$.` | applied | Symbols b-hat-perp and b used without definition; e-perp defined at first use (b is defined by the sentence itself as the bias strength). |
| M2b | 03_pedestrian_model.tex:16 | `The lateral bias, a deterministic tilt of fixed handedness, replaces` | `The lateral bias $b$, a deterministic tilt of fixed handedness, replaces` | applied | The bias strength b is used in Sects. 4-6 but never named at first use. |
| M3 | 03_pedestrian_model.tex:18 | `tangent $\mathbf t_{ij}$ and $g(x)=\max(0,x)$,` | `tangent $\mathbf t_{ij}$ and $h(x)=\max(0,x)$,` | applied | Overloaded symbol: g is the goal (bold g), the ramp max(0,x) and, with subscript, g_max(r). Ramp renamed h. |
| M3b | 03_pedestrian_model.tex:20 | `\mathbf f^{\rm sfm}_{ij}=\bigl[A\,e^{(r_{ij}-d_{ij})/B}+k\,g(r_{ij}-d_{ij})\bigr]\mathbf n_{ij}+\kappa\,g(r_{ij}-d_{ij})` | `\mathbf f^{\rm sfm}_{ij}=\bigl[A\,e^{(r_{ij}-d_{ij})/B}+k\,h(r_{ij}-d_{ij})\bigr]\mathbf n_{ij}+\kappa\,h(r_{ij}-d_{ij})` | applied | Same rename in Eq. (3). |
| M3c | 03_pedestrian_model.tex:24 | `\mathbf f^{\rm wall}_{iW}=\bigl[A_w\,e^{(r_i-d_{iW})/B_w}+k\,g(r_i-d_{iW})\bigr]\mathbf n_{iW}-\kappa\,g(r_i-d_{iW})` | `\mathbf f^{\rm wall}_{iW}=\bigl[A_w\,e^{(r_i-d_{iW})/B_w}+k\,h(r_i-d_{iW})\bigr]\mathbf n_{iW}-\kappa\,h(r_i-d_{iW})` | applied | Same rename in Eq. (4). |
| P1 | 04_protocol.tex:14 | `the lateral tilt $\pm b$ and the corrected implementation. The rest-drive push` | `the lateral tilt $\pm b$ and the corrected implementation (here the RVO2 solver). The rest-drive push` | applied | 'corrected implementation' is a probe and a Table 2 column but is never identified; defined at first use. |
| P3 | 04_protocol.tex:24 | `Stack the $n$ remaining agents into` | `Stack the $n$ residual agents into` | applied | Terminology drift: 'remaining agents' here, 'residual agents' in Sects. 4.5 and 5.2. |
| P4 | 04_protocol.tex:28 | `with the rest-state field $\mathbf F_0(\mathbf x)=\mathbf F(\mathbf x,\mathbf 0)$,` | `with the rest field $\mathbf F_0(\mathbf x)=\mathbf F(\mathbf x,\mathbf 0)$,` | applied | Terminology drift: 'rest-state field' once, 'rest field' everywhere else. |
| S3 | 06_screening.tex:25 | `The data give no evidence that identity separates them at the lone trap:` | `The data give no evidence that the overlap separates them at the lone trap:` | applied | 'identity' as a signature name is never defined; Sect. 3.5 defines the overlap J. |
| S4 | 06_screening.tex:31 | `At the second trap full ORCA (RVO2) frees fewer blockers than its drive part,` | `At the second trap ORCA (RVO2) frees fewer blockers than its drive part alone,` | applied | Overloaded 'full': the full barrier condition (all residual agents mobile) and here ORCA with both parts. |
| S6 | 06_screening.tex:36 | `so identity gives no separation.` | `so the overlap gives no separation.` | applied | As S3. |
| S9 | 06_screening.tex:54 | `Identity and handedness separate bias and ORCA.` | `Overlap and handedness separate bias and ORCA.` | applied | As S3. |
| K22 | Fig. 4 axis vs 05:22 | `'exit width' (figure axis, caption) vs 'door width' (text); 'exit' (abstract, Sect. 9) vs 'door'` | `keep` | declined | Declined: the figure axis says 'exit width' and the caption must match it; figures are out of scope. Recommend 'door' throughout at the next figure build. |
| K23 | 07_experiments.tex; Fig. 9; Table 3 | `'SFM + noise $\sigma^\ast$' (spaced) vs 'SFM+ORCA', 'SFM+TTC'` | `keep` | declined | Declined: the spaced form matches the Fig. 9 labels; change both together. |
| K24 | 03:37 vs 08 (table), 05:22 | `$w$ door width vs $w_{o,i}$ ORCA gate weight` | `keep` | declined | Declined: distinguished by subscript; renaming the gate weight touches Eq. (1), (6) and Table 1 and changes nothing a reader can confuse. |
| K25 | 05_deadlock_physics.tex:16, Fig. 3 | `'stuck alone' (criterion) vs 'held alone' (Fig. 3, 05:22)` | `keep` | kept / none | Kept: 'stuck alone' names the criterion and the margin; 'held' is the verb used for every trap. Both are defined at 05:16. |

## 13. Numbers and internal consistency

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| S2 | 06_screening.tex:25 | `differs from ORCA's by \FixAtwoLoneDelta\ [\FixAtwoLoneDeltaLo, \FixAtwoLoneDeltaHi].` | `differs from ORCA's by $\FixAtwoLoneDelta$ [$\FixAtwoLoneDeltaLo$, $\FixAtwoLoneDeltaHi$].` | applied | Compiled text prints '-0.01 [-0.09, 0.07]' with hyphens for minus signs (macros in text mode); every other signed value is in math mode. |
| K26 | 05_deadlock_physics.tex:43; 07:17; Table 3 | `1.07 [1.002, 1.15]; 1.7 s (at most 2.04 s); 0 [0, 0.24] vs 0.20 [0.00, 0.70]` | `uniform precision` | declined | Declined: mixed precision comes from registry formats (paper/registry, numbers.tex), which are out of scope. Flag for the registry owner. |
| K27 | 06_screening.tex:54 | `$[\FixAtwoPairPubDeltaLo, \FixAtwoPairPubDeltaHi]$ prints [−0.35, +0.35]` | `drop '+'` | declined | Declined: the explicit plus sign is in the registry format. |
| K28 | 00_abstract.tex:3; 01_introduction.tex:18 | `Replay, time-step dependence, time to free, final state and handedness separate them` | `add 'overlap'` | declined | Declined: at the pair standoff the overlap J and handedness both separate bias from ORCA (06:54); the list is incomplete, not wrong, since handedness is listed. Adding a word risks a line in the abstract. |

## 14. Structural and framing problems

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| P2 | 04_protocol.tex:19 | `The rate match is calibration only. The rest-drive push is the reference perturbation of known class L: at the lone keystone it frees \FinPushBoth\ of the blockers SFM+ORCA (RVO2) frees (\FinPushOnly\ by the push only, \FinOrcaOnly\ by ORCA only), replays exactly and, reversed, frees none (\EtwoLKFrozenMinusFreed\ of \EtwoNLK; Sect.~\ref{sec:att-lone}).` | `The rate match only calibrates the surrogate. The rest-drive push is the reference perturbation of known class L (Sect.~\ref{sec:att-lone}).` | applied | Aphoristic 'calibration only' made literal. The push results (paired counts, reversed push) are restated verbatim in Sect. 6.1 and are results inside the method section, with a garden-path 'frees 30 of the blockers SFM+ORCA (RVO2) frees'; the one fact not repeated in 6.1, exact replay, is moved there (S1). Every number survives in Sect. 6.1 (EtwoNLK appears in 6.1 and Table 3). |
| S1 | 06_screening.tex:22 | `The rest-drive push frees \EtwoLKFrozenPlusFreed\ towards the door and \EtwoLKFrozenMinusFreed\ away.` | `The rest-drive push frees \EtwoLKFrozenPlusFreed\ towards the door and \EtwoLKFrozenMinusFreed\ away, and replays exactly.` | applied | Receives the one push result moved out of Sect. 4.2 (P2). |
| D9 | 05_deadlock_physics.tex:18 | `Whole runs rarely complete (\EOneBCompletionK\ of \EOneBCompletionN).  Agents that can pass alone leave first:` | `Whole runs rarely complete (\EOneBCompletionK\ of \EOneBCompletionN). Agents that can pass alone leave first:` | applied | One-sentence paragraph that continues the stuck-alone stack finding of the paragraph above; merged. |
| C2 | 09_conclusions.tex:2 | ` The open framework deadlock-screen implements the screening protocol. In the CroMa` | ` In the CroMa` | applied | Fourth verbatim statement of the same sentence (abstract, introduction, Sect. 8.3 one page earlier, here); deleted here, where Sect. 8.3 gives the URL. |
| K29 | 00_abstract.tex / 01:17-20 / 09:2 | `Abstract, contribution list and Conclusions state the same findings in the same order` | `keep` | declined | Declined except for C2: the repetition is the conventional abstract/contributions/conclusions triple; restructuring the introduction is beyond a length-neutral prose pass. |

## 15. Spelling and convention consistency

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| X1 | 07_experiments.tex:11 | `\subsubsection{Experiments and Model Runs.}` | `\subsubsection{Experiments and model runs.}` | applied | Run-in heads are in sentence case in Sects. 2 and 6, title case here. |
| X2 | 07_experiments.tex:16 | `\subsubsection{Human Runs.}` | `\subsubsection{Human runs.}` | applied | As X1. |
| X3 | 07_experiments.tex:19 | `\subsubsection{Model Variants.}` | `\subsubsection{Model variants.}` | applied | As X1. |
| X4 | 07_experiments.tex:22 | `\subsubsection{Removing Deadlocks.}` | `\subsubsection{Removing deadlocks.}` | applied | As X1. |
| X6 | 07_experiments.tex:12 | `(a walled holding area of $7.8\times8.6$\,m, the entrance, and corridor walls of the run's length)` | `(a walled holding area of $7.8\times8.6$\,m, the entrance and corridor walls of the run's length)` | applied | The only serial comma in the paper; the paper omits it elsewhere ('grains, colloids, sheep and people'). |
| K30 | whole paper | `British spelling` | `keep` | kept / none | Checked: behaviour, modelling, discretised, characterised, realised, coloured, neighbour, favoured, centre, towards; no -ize/-or/-er American form found. 'Acknowledgments' is printed by llncs (\ackname), not the source. |

## 16. Anything else

| ID | Anchor | Quoted text | Replacement | Status | Reason |
|---|---|---|---|---|---|
| I3 | 01_introduction.tex:18 | `Velocity-coupled ORCA has no rest drive and is predicted to be class P at most (Sect.~\ref{sec:velorca}).` | `Velocity-coupled ORCA has no rest drive (Sect.~\ref{sec:velorca}).` | applied | 'class P' used before the classes are defined (Sect. 4); stated physically. Final form of I3: the class-P prediction needs the classes of Sect. 4 and is stated in Sect. 6.4 and the Conclusions. |
| D1 | 05_deadlock_physics.tex:12 | `With the blocker's Weidmann factor at least \FinTermWeidMin\ at rest, its drive is $m v_0/\tau$,` | `With $v_{\rm eff}/v_0\ge\FinTermWeidMin$ for the blocker at rest, its drive is $m v_0/\tau$,` | applied | 'Weidmann factor' is never defined; replaced by the defined ratio of Eq. (2). |
| D2 | 05_deadlock_physics.tex:18 | `All \FinCritPosN\ blockers with positive margin stayed held, on the axis and stiffer sideways than along it` | `All \FinCritPosN\ blockers with positive margin stayed held on the axis, in a minimum stiffer sideways than along it` | applied | Dangling comparative: the agents are not 'stiffer'; the rest state is. |
| D4 | 05_deadlock_physics.tex:39 | `spread over the full barrier (\FixAthreeEfourUsed\ of \FixAthreeEfourQual),` | `spread over the full barrier (of \FixAthreeEfourQual\ that qualify),` | applied | '(10 of 32)' repeats the 10 of the same sentence and leaves 32 unexplained; phrased as in Sect. 6.1 ('of 36 that qualify'). Both macros print 10; the number survives as EfourN. |
| D5 | 05_deadlock_physics.tex:41 | `The fitted slope of $\ln\lambda$ against $1/k_BT_{\rm eff}$ over $-\Delta U$ has median` | `The fitted Arrhenius slope divided by $-\Delta U$ has median` | applied | 'slope ... against ... over ...' reads as two prepositions of the same kind; 'over' means division. Matches the Fig. 5 caption. |
| D7 | 05_deadlock_physics.tex:54 | `The signs differ because the members stand at unequal distances from the axis (rank correlation \PairAsymCorr).` | `The two thresholds differ because the members stand at unequal distances from the axis (rank correlation of the two differences \PairAsymCorr).` | applied | 'The signs differ' (signs of what?) and a rank correlation with no named variables. The registry key correlates the distance asymmetry with the threshold asymmetry. |
| S7 | 06_screening.tex:51 | `so a result for ORCA at the pair holds for one solver.` | `so results for ORCA at the pair are specific to the solver.` | applied | 'holds for one solver' reads as 'holds for at least one solver'; the claim is solver specificity. |
| S8 | 06_screening.tex:51 | `Combined with the drive part it acts against it: full ORCA (RVO2) frees fewer standoffs than its drive part` | `Combined with the drive part it opposes that part: ORCA (RVO2) frees fewer standoffs than its drive part alone` | applied | Two pronouns 'it ... it' with different antecedents; overloaded 'full' as in S4. |
| Q3 | 08_discussion.tex:8 | `there a surrogate matched to the resolver's success rate can be probed with it at the equilibria.` | `there a resolver and a surrogate matched to its success rate can be probed together at the equilibria.` | applied | Unclear antecedent: 'probed with it' (with the rate? with the resolver?). |
| K31 | 04_protocol.tex:48 | `The blocker's realised velocity variance is \TthreeRatioMean\ times Eq.~\eqref{eq:teff}` | `times the value of Eq. (10)` | declined | Taste: Eq. (10) gives $k_BT_{\rm eff}$, not a variance; the reading is recoverable from the preceding sentence ($m_i\langle v^2\rangle=k_BT_{\rm eff}$). Declined for length. |
| K32 | 05_deadlock_physics.tex:43 | `the Langer prefactor` | `keep` | kept / none | Kept: standard term of the cited reaction-rate review [16]. |

## Triage

1. D6 (Weibull sentence, 05:43): the worst sentence in the paper, now one claim plus one exception. 2 min.
2. P2/S1 (rest-drive push results duplicated in Sect. 4.2 with a garden-path clause): results now live only in Sect. 6.1. 3 min.
3. S3/S6/S9 and S4/S8 (undefined 'identity'; overloaded 'full'): the defined terms 'overlap' and 'drive part alone' are used instead. 3 min.
4. M3 (g overloaded as goal, ramp and g_max): the ramp is now h. 2 min.
5. S2 (hyphens for minus signs in the compiled text of Sect. 6.1). 1 min.

Open for the authors: registry precision (K26, K27), the 'exit'/'door' axis label (K22), the duplicated speed cap in Table 1 (K21), and numbers for 'negligible' and 'a few seconds' (K10, K11).
