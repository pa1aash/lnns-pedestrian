# S2 prose audit: merged report

Manuscript: `reports/audit/snapshot/main.tex` (1353 lines) at commit decbdca. Every line number is a line of that file. Rendered values come from `main.txt`; figures and tables were read from `pages/p-*.png`. The audit judges the writing only. The \pending items (Table 4, §6.3, the Zenodo DOI, acknowledgements and disclosure) are known gaps and are not counted as defects.

This report merges four partial audits: S2_P1 (front matter to §3), S2_P2 (§4–§5), S2_P3 (§6–§9 and back matter), all for categories 1–11 and 16, and S2_P4 (categories 12–15 over the whole paper). They are kept in the repository as working files. The categories follow the governing prompt's order. The cross-block reconciliations (category x.0 sections and the duplicate table below) are new to this merge.

**How to read the entry ids.** Each entry keeps the id it had in its block, with a block prefix:

| Prefix | Block | main.tex lines |
|---|---|---|
| **F** | title, running heads, abstract, keywords, §1, §2, §3 (Table 1, Fig. 1 caption) | 13–21, 651–926 |
| **M** | §4, §5 (Table 2, Figs 2–4) | 927–1071 |
| **R** | §6–§9, Main Differences, Data and Code Availability (Table 3, Figs 5–8) | 1072–1183 |
| **W** | whole paper, categories 12–15 only | 13–1352 |

Inside a block, a bare cross-reference such as "per 1.9" or "see 16.3" points to an entry of the same block. In this merge, "F1.4" means entry 1.4 of block F.

**Severity.** H: a skeptical reviewer will misread a result, catch a contradiction or stop reading. M: a visible defect, or a breach of a standing rule. L: polish. Block W used S1/S2/S3 for the same three levels. **[TASTE]** marks a preference, and the competing convention is named with it.

**Source files.** These are the files a fix edits:

| Code (as used in the blocks) | File | main.tex lines |
|---|---|---|
| MAIN | `paper/main.tex` (title block) | 13–21 |
| ABS / abs | `paper/sections/00_abstract.tex` | 651–654 |
| INT / intro | `paper/sections/01_introduction.tex` | 655–839 |
| F1C / F1cap | `figures/fig1_caption.tex` (owned by the hero sessions, plan C32) | 822 |
| BKG / bg | `paper/sections/02_background.tex` | 840–854 |
| MOD / model, T1 | `paper/sections/03_model.tex`, `paper/tables/table1_params.tex` | 855–926 |
| [T2] / T2 | `paper/tables/table2_signatures.tex` | 928–980 |
| [S4] / sig | `paper/sections/04_signatures.tex` | 927, 981–1020 |
| [S5] / phys | `paper/sections/05_deadlock_physics.tex` | 1021–1071 |
| [06] / att | `paper/sections/06_attribution.tex` | 1072–1143 |
| [T3] / T3 | `paper/tables/table3_matched.tex` | 1086–1109 |
| [07] / val | `paper/sections/07_validity.tex` | 1144–1160 |
| [08] / disc | `paper/sections/08_discussion.tex` | 1161–1175 |
| [09] / concl | `paper/sections/09_conclusions.tex` | 1176–1177 |
| [10] / back | `paper/sections/10_back_matter.tex` | 1178–1182 |
| bib | `paper/refs.bib` | 1187–1352 |
| figN | `figures/figN_*.py` (tick and axis text) | — |

---

## 0. Highest-leverage fixes, ranked

The list is de-duplicated across blocks. Each line names the entries that carry the full fix.

1. **H. "class", "collective" and "frozen" each carry several meanings, and the paper says both "two classes" and "three classes" of deadlock.** The two-class claim is at 653, 835 and 1177; the three-class sorting is at 1035. "Five mechanism classes" (834) is set against the four rows of Table 2. Fix: deadlock *types* (lone trap, pair standoff), keystone *outcomes* (lone keystone, second trap, group standoff), mechanism *classes* (P, L, T, D, N), and "pinned" for the neighbours-held barrier condition. Entries W12.1–12.3, W13.1, W14.6.
2. **H. The protocol misstates what is matched.** The abstract and step (2) at 1020 say the control is tuned to the "completion rate", but the lone-trap and pair matches are on the freed fraction of snapshots. Line 981 then says the probes "are not tuned by matching a completion rate", which reads as a contradiction of 1020. Entries W13.2, W12.26, M1.1, M1.2.
3. **H. The thesis is stated in negated form four to six times.** The instances are 652, 828–832 (a four-sentence rule-out cascade), 1020, 1163, 1166 and 1177. The paper both opens and closes on the formula. Entries F1.1–F1.8, R1b, R1.8, R1.9, R1.12, R1.13, W14.4.
4. **H. The worst sentence in the paper (line 1120) carries the class-N verdict on the published solver.** See "Worst sentence" below. Entries R4.1, R9.6, R9.7, W13.14.
5. **H. Abstract sentences 5 and 6.** Sentence 5 runs to 53 words, with three "matched to" subjects and one "the rate" that stands for three different rates. Sentence 6, "either deadlocks or flows at 0.40–0.59", contradicts 1157, where the ratio holds for every variant. ORCA and CroMa are never expanded. Entries F9.1, F16.5, F16.6, F1.6.
6. **H. Seven statements read as wrong as written:**
   - "393 of 393" reads as "all held" (1035). Entry M16.2.
   - The Weibull shape is called "close to the exponential value 1", though its interval excludes 1 (1067). Entry M5.1.
   - "far below the lone-trap barriers" refers to a number the paper never prints (1053). Entries M4.1, W13.9.
   - The human longest gap "never exceeds 2.0 s", yet there are "0.2 gaps longer than 2 s" per run (1154). Entries R9.16, W13.4.
   - "5 of 300 lone-trap snapshots" (1169): the library holds 60 snapshots, and 300 is the replay count. Entry W13.5.
   - An AUC is set against an accuracy (1037). Entry W13.6.
   - "All three predictions … hold" and "Noise is thermal" stand next to listed exceptions (1067, 1117). Entry W13.3.
7. **H. Terms used without definition:**
   - "constraint part" (836, then §6). Entry F16.1.
   - "lower member", which the Table 3 handedness column depends on. Entry R16.1.
   - "the gate" and "gated" (1053, 1069), which collide with the density gate of Eq. (6). Entries M11, W12.7.
   - "the easier sign" (1051). Entry M16.16.
   - "slow creep" (1120). Entry R4.1.
   - "blocker" and the two modes, both used before they are introduced (895, 906). Entries F16.2, F16.3.
8. **H. Overloaded or orphan symbols.**
   - λ is both the escape rate and the softest Hessian eigenvalue (1049 against 1012–1015).
   - b\* is both the per-snapshot fold threshold and the matched bias (1051 against 1136).
   - $B_{w,\rm edge}$ is defined (865) but the jamb-only variant is written $B_w$ throughout.
   Entries W12.4–12.6, W12.13.
9. **H/M. Captions.**
   - Fig. 1 runs to 170 words. Entry F8.1.
   - Table 2 has three sentences. Entry M8.
   - Table 3 and Figs 5, 6 and 8 argue, carry method detail, or exceed the two-sentence rule (C3). Entry R8.
10. **M. Structure.**
   - The protocol paragraph "Calibrate, then falsify" is buried at the end of §4.3. Entries W14.1, M7.4.
   - §5.2 points twice into §5.4, and once to the wrong section (the string method is in §4.3). Entries W14.2, M16.1.
   - The whole-run attribution sits under the heading "6.1 The Lone Trap". Entry W14.3.
   - The practitioner advice appears in §7 and again in §8. Entries W14.5, R1.10.
11. **M. Process and trial vocabulary, and internal codes, in breach of C6.**
   - "declared", "forward claims", "arm", "held-out", "before they are measured" and "stated rather than fixed".
   - Experiment codes E2, E3, E6 and E7b in Table 3.
   - A yaml file path in the Table 1 caption.
   Entries F11, M11, R11, W12.25, W14.8.
12. **M. Headings.**
   - Seven paragraph leads state a result.
   - "ORCA is its rest drive." is contradicted two paragraphs later.
   - "The Symmetric Pair Standoff" is set against "no standoff is exactly symmetric".
   Entries R7, M7.1, W14.12.
13. **M. The 430-word paragraph at 1035.** It carries five results under three topics. Split it into three paragraphs. Entries M (worst paragraph), W14.7.
14. **L. Conventions.**
   - A hyphen is printed for the minus sign of negative macros.
   - Interval notation is mixed.
   - Bibliography fields are inconsistent.
   Entries W15.2, W15.3, W15.12.

### Worst sentence in the paper

**Line 1120 (`paper/sections/06_attribution.tex`)**, the last sentence of "The second trap and the published solver.":

> Only the published linear program changes outcome under $10^{-9}$\,m replays (\EtwoReplayCThreePubFlips\ of \EtwoReplayN, exit times shifted by up to \EtwoReplayCThreePubMaxDt\,s, all at the second trap in slow creep), which a replay this small reveals as ill-conditioning of that implementation (class N) and base forward claims on RVO2.

The coordinated verb "base" has no subject, so as written the relative pronoun "which" both "reveals" and "base[s]". The "which" takes a whole clause as its antecedent. A three-item parenthetical carries an undefined term ("slow creep"). "Forward claims" is project vocabulary. The sentence also delivers one of the paper's verdicts (class N for the published solver). Split:

> Only the published linear program changes outcome under $10^{-9}$\,m replays: 5 of 300, all at the second trap while the agents creep slowly toward the door, with exit times shifted by up to 80.8\,s. An outcome that a $10^{-9}$\,m shift can change marks ill-conditioning of that implementation (class N), and we take RVO2 as the reference ORCA implementation.

It competes with three sentences:
- Abstract sentence 5 (652, F9.1). This is the most consequential, because the abstract is the most-read text. Its split is in F9.1 and should be made together with this one.
- The fold-bisection sentence (1051, M9.16).
- The 75-word estimator sentence (1151, R9.15).

**Worst paragraph:** 1035 (§5.1, about 430 words, 17 sentences). It competes with 1120 (175 words) and 1123 (159 words).

### Duplicates between blocks and how they were resolved

| Defect | Entries | Resolution |
|---|---|---|
| Human longest gap 2.0 s against >2 s | R9.16; W13.4 | Fix once at 1154: print the maximum as 2.04 s, per W13.4. R9.16 also splits the sentence; apply both at the same line. |
| "far below the lone-trap barriers" | M4.1, M9.18; W13.9 | Register the lone-trap barrier range as a macro and quote it (M4.1). W13.9 is the same defect. |
| Line 1120 | R4.1, R9.6, R9.7; W13.14 | One rewrite, given above. |
| Thesis repetition | F1.8; R1b; R1.8, R1.9, R1.12, R1.13; W14.4 | **Conflict.** F proposed keeping the sentences at 1162 and 1177. R, which audited those lines, keeps 652, 830 (as fixed by F1.4) and 1163 sentence 1; deletes the last sentence of 1166; and replaces the first and last sentences of 1177. **R's resolution is adopted**: the paper should not open and close its last section on the same negation. W14.4 agrees. |
| Practitioner advice in §7 and §8 | R1.10, R1b; W14.5 | Keep the operational version at 1160. Cut the clause at 1169 (R1.10). Whether the whole list moves from §7 into §8 (W14.5) is a structural choice and goes to the fix plan. |
| §4.3 and §5.4 cross-reference | M16.1; W14.2 | M16.1 (label §4.3 and point 1053 to it) is needed in any case. W14.2 (reorder §5 as lone trap, noise escape, pair, arches) is optional, and only if the page pass allows it. |
| "Calibrate, then falsify" placement | M7.4; W14.1 | Same fix: move the paragraph to the head of §4. |
| "Symmetric" in the §5.2 heading | M7.1; W14.12; F8.1 | Drop "Symmetric" from the 1046 heading and from 653 and 1177 if those are rephrased. F8.1's Fig. 1 replacement caption keeps "symmetric pair standoff". Use "pair standoff" there as well, because the figure shows a near-symmetric case and the word is not needed. |
| "Lower member" undefined | R16.1; W12.46 | Define it once at 1051 (§5.2), per R16.1. |
| Process and C6 vocabulary | F11.x, M11.x, R11.x; W12.25, W14.8 | The per-line fixes are in the blocks. W12.25 lists the drift globally, as a checklist. |
| Paragraph 1035 | M (worst paragraph), M16.2; W14.7 | Same split, at "Removing the blocker sorts…" and "The trap is a property of the door geometry…". |


---

## 1. Rhetorical negation

### 1.0 Paper-wide reconciliation

**One distinction is stated six times.** "A matched rate shows sufficiency, not mechanism" appears at:
- 652 (abstract);
- 828–832 (§1, a cascade of four rule-outs before the thesis);
- 981 / 1020 (§4: "not tuned by matching a completion rate", "this is calibration, not evidence");
- 1163 (§8);
- 1166 ("The rate is a calibration target, not a test of mechanism.");
- 1177 (the first and last sentences of the Conclusions).

Resolution, applied across the blocks:
- Keep the abstract version as rewritten in F1.6.
- Keep §1 once, at 830, as fixed in F1.4. F1.2, F1.3 and F1.5 turn the other rule-outs into positive statements.
- Keep 1020 step (2), corrected to "rate" (W13.2). M1.1 removes the clash at 981.
- Keep 1163 sentence 1, because it adds "in all three of our pairs it does". Rewrite sentences 3–4 (R1.8).
- Delete the 1166 sentence (R1.9).
- Replace the first and last sentences of 1177 (R1.12, R1.13).

**Mirrored or repeated pairs:**
- Number against mechanism: 1136 / 1177.
- The trap's cause: 1035 "door geometry and jamb wall law" / 1169 "jamb wall law, not crowding".
- The same recommendation: 1160 / 1169.
- No static friction: 835 / 845 / 1056.

The fixes are in F1.8, M (mirrored pairs) and R1b. For each pair, the instance kept is the one that carries a number or a reason.

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

**1.1 [H] Cascade of rule-outs, 828 → 832 (INT).** Four consecutive rule-outs come before the positive claim, which is that physics-derived signatures decide whether a mechanism is shared:
- 828 "That statement is about mechanism, and a completion rate cannot support it on its own."
- 830 "The principle stops short."
- 830 "A matched control shows that a simpler cause suffices for the score, not that the paradigm and the control act in the same way: two physical processes can produce the same completion rate, and one number cannot separate them."
- 832 "Our thesis is that matching a control to a paradigm's headline completion rate is not evidence of a shared mechanism, and that signatures … decide the question."

The reader meets "not" four times before learning what does the work. Fix each one as in 1.2–1.5. The ruling-out survives once, in 830, where it carries its reason.

| # | Line | File | Quoted text | Replacement |
|---|---|---|---|---|
| 1.2 | 828 | INT | "That statement is about mechanism, and a completion rate cannot support it on its own." | "That statement is a claim about mechanism, and testing it takes more than a completion rate." |
| 1.3 | 830 | INT | "The principle stops short." | "The principle tests sufficiency." |
| 1.4 | 830 | INT | "A matched control shows that a simpler cause suffices for the score, not that the paradigm and the control act in the same way: two physical processes can produce the same completion rate, and one number cannot separate them." | "A matched control shows that a simpler cause suffices for the score. Two physical processes can produce the same completion rate, and one number cannot separate them." |
| 1.5 | 832 | INT | "Our thesis is that matching a control to a paradigm's headline completion rate is not evidence of a shared mechanism, and that signatures derived from the physics of the model, measured on the same frozen deadlock states, decide the question." | "Our thesis is that signatures derived from the physics of the model, measured on the same frozen deadlock states, decide whether a paradigm and a control matched to its headline completion rate share a mechanism." |
| 1.6 | 652 S2 | ABS | "A control that shares none of its machinery, tuned to reproduce its completion rate, shows only that a simpler cause would suffice." | "A control that shares none of the paradigm's machinery and is tuned to reproduce its completion rate shows that a simpler cause would suffice for that rate; whether the two act alike needs a separate test." |
| 1.7 | 923 | MOD | "The published-reproduction mode only explains published numbers; every forward claim uses the corrected-forward mode" | "The published-reproduction mode reproduces the conference paper's numbers; all new results use the corrected-forward mode" (see also 16.3, which moves this sentence) |

**1.8 [M] Repeated distinction across the paper.** "A matched rate shows sufficiency, not mechanism" is stated at 652 (abstract), 830 (§1), 1020 ("this is calibration, not evidence"), 1160 ("A matched control shows whether a simpler cause suffices"), 1162 ("The rate is a calibration target, not a test of mechanism.") and 1177 ("shows that a simpler cause would suffice, not that the paradigm uses it"). Every instance points the same way, so this is a sixfold repetition rather than a mirrored pair. Within this range, keep the full statement once, at 830 (as fixed in 1.4), and give the abstract version as 1.6. The out-of-range instances belong to the §4/§8/§9 auditor. Of those, 1162 and 1177 are the strongest candidates to keep.

**1.9 [L][TASTE] Title, 13 (MAIN).** "One Matched Control Is Not Enough: …". The half that carries the claim is a negation, and it holds none of the index terms. Competing convention: physics and simulation venues accept hook titles that state a claim, and this one is memorable. If kept, rename the §6.2 paragraph head at 1135, "One matched bias is not enough.", to "Matched lateral bias at the pair." so the title is not echoed. If changed: "Matched Controls and Physical Signatures: Attributing Deadlock Resolution in Pedestrian Steering Models".

**1.10 [L][TASTE] Running head, 14 (MAIN).** "One Matched Control Is Not Enough" keeps only the negative half on every odd page. Replacement: "Attributing Deadlock Resolution in Steering Models".

**Kept as genuine technical contrasts:**
- 835 "contact arches formed at high drive never persist, because the model has no static friction". The reason is given.
- 845 "The SFM considered here has no static friction, so it cannot hold a frictional arch". Reason given.
- 845 "without invoking a single barrier". This names what the trap model does without, and that is its content.
- 836 "with a handedness ORCA lacks". A measured difference.
- 913 "exactly zero". Literally true below the stated threshold.
- 854 "We have not found an earlier study that tests a matched control in this way." Phrasing the novelty claim positively would overclaim.
- 916 "(not $v_{\rm eff}$)". The distinction matters because $v_{\rm eff}<v_0$ can hold during motion. Only the word "note" goes (2.1).

The no-static-friction point is stated three times (835, 845, out-of-range 1056). At 1056 it takes the form "therefore not contact arches but the contact-free rest states", which is the not-X-but-Y form. That fix belongs to the §5 auditor.

### Block M: §4–§5 (main.tex 927–1071)

| # | Line / file | Quoted text | Replacement | Sev |
|---|---|---|---|---|
| 1.1 | 1020 [S4] | "(2) Tune the control's single parameter to the target's completion rate; this is calibration, not evidence." | "(2) Tune the control's single parameter to the target's completion rate. The matched rate is the starting point of the comparison and counts toward no class assignment." | H |
| 1.2 | 981 [S4] | "Paired by snapshot, they are not tuned by matching a completion rate." | "Every probe compares interventions on the same snapshots, so its outcome does not depend on how any intervention was tuned to a completion rate." (Also fixes the dangling "Paired by snapshot, they"; see 4.11.) | H |
| 1.3 | 1056 [S5] | "The model's persistent deadlocks are therefore not contact arches but the contact-free rest states of Sects.~\ref{sec:lone} and~\ref{sec:pair}." | "The model's persistent deadlocks are therefore the contact-free rest states of Sects.~\ref{sec:lone} and~\ref{sec:pair}." (The preceding two sentences already rule out arches with numbers.) | M |
| 1.4 | 1047 [S5] | "the configuration is a balanced standoff, not a contact jam." | "the configuration is a balanced, contact-free standoff." | M |
| 1.5 | 1047 [S5] | "The second class has no lone agent that is held." | "In the second class every agent would pass the door if it were alone." | M |
| 1.6 | 1035 [S5] | "The \CriterionNegMargin\ blockers with negative margin are exactly the deadlocks that are not lone traps; they are pair standoffs at the jamb faces (Sect.~\ref{sec:pair})." | "The \CriterionNegMargin\ blockers with negative margin are the pair standoffs at the jamb faces (Sect.~\ref{sec:pair})." | M |
| 1.7 | 1037 [S5] | "A stuck-alone agent still exits if others push it through, and they need not be agents that could pass alone: with no such agent left, …" | "Stuck-alone agents push one another through: with no agent that could pass alone still present, \ChainNoPassableExited\ of \ChainNoPassableN\ stuck-alone arrivals exit." The negation "need not be" argues against a reading the reader never saw (the superseded passable-pusher reading, CHANGELOG C22). | M |
| 1.8 | 1001 [S4] | "ORCA's rest drive does not vanish at rest; it enters $\mathbf F_0$ and reshapes the landscape (a candidate for class L)." | "ORCA's rest drive persists at rest, enters $\mathbf F_0$ and reshapes the landscape (a candidate for class L)." | L |
| 1.9 | 1035 [S5] | "The trap is therefore local to the door edges: the walls away from the door add nothing." | "The trap is therefore local to the door edges: shortening the other walls as well leaves completion unchanged (\EsevenBallK\ against \EsevenBjambK\ of \EsevenN, $p=\EsevenJambVsAllP$)." | M |
| 1.10 | 1069 [S5] | "The computed minimum-energy path is then not the route the dynamics takes, and the snapshot is left out of the Arrhenius fits." | "The dynamics then leaves by a route other than the computed minimum-energy path, and the snapshot is left out of the Arrhenius fits." | L |
| 1.11 | 1049 [S5] (cascade) | "no unperturbed C1 restart frees a member, nor any of the \PairPerturbN\ replays perturbed by $10^{-9}$\,m, and a common lateral shift of both members by 1\,mm frees \PairDeltaOneMmFreed\ of \PairN\ and by 1\,cm \PairDeltaOneCmFreed." | This is three consecutive rule-outs. State them as what holds: "the standoff stays held under every unperturbed C1 restart, under all \PairPerturbN\ replays perturbed by $10^{-9}$\,m, and under a common lateral shift of both members by 1\,mm (\PairN\ of \PairN) and 1\,cm (all but \PairDeltaOneCmFreed)." | M |

**Mirrored and repeated pairs**
- **1020 against 830, 832 and 1177 (outside range).** "this is calibration, not evidence" is the fourth statement of the thesis in negated form. Line 832 has "matching … is not evidence of a shared mechanism", line 830 "shows that a simpler cause suffices for the score, not that the paradigm and the control act in the same way", and line 1177 "shows that a simpler cause would suffice, not that the paradigm uses it". With 1.1 applied, 1020 states the procedure and leaves the negated thesis to §1 and §9.
- **1047 against 1056 (and 835, 1177).** "a balanced standoff, not a contact jam" (1047) anticipates "not contact arches but the contact-free rest states" (1056). The same contrast is drawn twice in §5, and again in §1 (835) and §9 (1177). Fixes 1.3 and 1.4 remove both in-range halves.
- **981 against 1020 (a pair that reads as a contradiction).** Line 981 says the probes "are not tuned by matching a completion rate". Line 1020 instructs "Tune the control's single parameter to the target's completion rate". A reader reads these as contradictory. Fix 1.2 makes 981 say what it means: the probe outcome does not depend on the tuning.

**Negations kept, because the contrast carries information:**
- 929 "``---'': the probe does not test that class": a table key.
- 994 "conversely such a state does not move": the converse direction of the proof.
- 1035 "Rounding the jamb corners or replacing the exit by a line goal does not remove it (…)": numbers follow.
- 1053 "$\lambda_1$ does not predict them (rank correlation …)": a number follows.
- 1053 "the escape times are not exponential (pooled Weibull shape …)": a number follows.
- 1029 and 1035 "exactly": see §5.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

#### 1a. Instances to fix

| # | Line, file | Sev | Text | Replacement |
|---|---|---|---|---|
| 1.1 | 1114 [06] | M | "Per-step noise at $\sigma=0.07$\,m/s matches that rate and nothing else (Table~\ref{tab:matched}): it leaves other snapshots unresolved, its seeds disagree (…), and it waits." | "Per-step noise at $\sigma=0.07$\,m/s matches C3 RVO2's lone-keystone rate (Table~\ref{tab:matched}) and differs from it on three signatures: it leaves other snapshots unresolved, its seeds disagree (within-snapshot standard deviation of the first exit \EtwoNoiseSDC\,s), and it is slower (Kaplan--Meier median \TabThreeLKNoiseMed\,s against \TabThreeLKRvoMed\,s)." |
| 1.2 | 1114 [06] | M | "(upper Wilson bound \EtwoMaxBiasUpperLK): nothing is symmetric to break." | "(upper Wilson bound \EtwoMaxBiasUpperLK), because a lone keystone has no symmetric partner for the bias to tilt." |
| 1.3 | 1117 [06] | M | "Noise is thermal at the temperature of Eq.~\eqref{eq:teff}; ORCA is not thermal." | "Noise is thermal at the temperature of Eq.~\eqref{eq:teff}." Delete "ORCA is not thermal": the sentence before it already gives the number ("C3 RVO2 has none ($|\ell|\le$ …)"). |
| 1.4 | 1123 [06] | M | "the two agree on completion and little else (Table~\ref{tab:matched})." | "the two agree on completion (Table~\ref{tab:matched}) and differ in which runs fail, how fast the rest complete and the class of their final states." This is the second use of the "X and nothing/little else" device (with 1.1). Two uses make it a tic. |
| 1.5 | 1151 [07] | M | "Three differences remain and are stated rather than fixed: model agents start at rest, …" | "Three differences remain: model agents start at rest, …" The "rather than" here is a process confession, not a contrast (see also 11.7). |
| 1.6 | 1160 [07] | M | "Third, removing deadlocks is not calibrating capacity: the reduced jamb range …" | "Third, a model that no longer deadlocks can still be far from human capacity: the reduced jamb range …" |
| 1.7 | 1160 [07] | L | "A narrow-door model should be checked against the flow and gap statistics of matched experiments, not against completion alone." | "A narrow-door model should be checked against the completion, flow and gap statistics of matched experiments." |
| 1.8 | 1163 [08] | H | "Read alone, as in the conference protocol~\cite{gang2026}, each match suggests that ORCA does what its control does. The held-out signatures, derived from the physics before the runs, reject that reading each time." These two sentences set up a reading only to knock it down. | "In the conference protocol~\cite{gang2026} a match was read alone, as evidence that ORCA does what its control does. The signatures of Sect.~\ref{sec:signatures}, measured on the same deadlocks, separate each control from ORCA:" Then continue with the content of the paragraph's last sentence (see 3.7). |
| 1.9 | 1166 [08] | M | "The rate is a calibration target, not a test of mechanism." | Delete. It restates line 1020 ("this is calibration, not evidence") and line 1177, sentence 1. The sentence before it already states the claim with its evidence ("as the low overlaps show"). |
| 1.10 | 1169 [08] | M | "First, the lone trap is a property of the jamb wall law, not of crowding (Eq.~\eqref{eq:stuck}; Sect.~\ref{sec:validity}): a deadlock rate at a narrow door should be read against the stuck-alone margin before it is read as crowd behaviour." | "First, the lone trap is set by the jamb wall law: an agent is held alone whenever $g_{\max}(r)$ exceeds $mv_0/\tau$ (Eq.~\eqref{eq:stuck}), with or without a crowd behind it." Drop the clause after the colon, which repeats line 1160 nearly word for word (see 1b). |
| 1.11 | 1169 [08] | L | "Third, noise is not a neutral way to unstick a model: its temperature depends on the time step (Eq.~\eqref{eq:teff}), so a level tuned at one $\Delta t$ is different physics at another." | "Third, the temperature of per-step noise depends on the time step (Eq.~\eqref{eq:teff}), so a noise level tuned at one $\Delta t$ is different physics at another." |
| 1.12 | 1177 [09] | M | "A control matched to a paradigm's completion rate shows that a simpler cause would suffice, not that the paradigm uses it." | Delete, and open with: "In a social-force bottleneck, a matched completion rate leaves the attribution open, and signatures derived from the physics of frozen deadlocks settle it." This is the fourth statement of the sentence (see 1b). |
| 1.13 | 1177 [09] | M | "A mechanism claim needs a test where the mechanism acts, not a second number that matches the first." | "A mechanism claim needs a probe of the mechanism, applied to the same deadlocks as the paradigm." |

#### 1b. Mirrored pairs and repeated distinctions

- **"Simpler cause would suffice, not …" is stated four times.** Line 652 (abstract: "shows only that a simpler cause would suffice"); line 830 ("shows that a simpler cause suffices for the score, not that the paradigm and the control act in the same way"); line 1163, sentence 1 ("shows whether a simpler cause suffices for the paradigm's score"); line 1177, sentence 1 ("shows that a simpler cause would suffice, not that the paradigm uses it"). Keep 652 and 830. Fix 1177 by entry 1.12. Line 1163 sentence 1 can stay, because it carries the new "in all three of our pairs it does".
- **Calibration versus evidence.** Line 1020 has "this is calibration, not evidence". Line 1166 has "The rate is a calibration target, not a test of mechanism". The heading at line 1162 is "What testing adds to calibration". Keep line 1020, which is the method step. Delete the line 1166 sentence (1.9) and rename the 1162 heading (7.12).
- **Number versus mechanism.** Line 1136 has "the bias shares ORCA's number, not its mechanism". Line 1177 has "not a second number that matches the first". Keep 1136 (see 10) and replace 1177 (1.13).
- **The same recommendation twice, two paragraphs apart.** Line 1160: "Before deadlock statistics at a narrow door are read as crowd behaviour, $g_{\max}(r)$ should be compared with $mv_0/\tau$ …". Line 1169: "a deadlock rate at a narrow door should be read against the stuck-alone margin before it is read as crowd behaviour". Keep 1160, which carries the operational test. Cut 1169 per entry 1.10.
- **The trap's cause, stated two ways.** Line 1035 has "The trap is a property of the door geometry and of the jamb wall law". Line 1169 has "a property of the jamb wall law, not of crowding". The door geometry drops out at line 1169. Entry 1.10 removes the "property of" formula. If the authors keep it, use the line 1035 wording.

#### 1c. Cascades

No run of three or more consecutive rule-out sentences occurs in the range. The closest is line 1163, sentences 3–4 (entry 1.8): a set-up followed by a rejection, over two sentences.

#### 1d. Genuine contrasts kept (they carry information)

- 1117: "C3 RVO2 has none ($|\ell|\le$ …)". The negation is quantified.
- 1120: "full ORCA frees fewer blockers than its own drive". This is a measured comparison.
- 1123: "whereas noise failures never come to rest". This is a class difference (but see 9.9).
- 1133: "Unlike at the lone trap the constraint part alone acts". This contrasts two measured results (add the comma, 9.11).
- 1136: "Both are deterministic, so replays do not separate them". This says why a probe is uninformative.
- 1157: "C3 RVO2 never deadlocks but completes only …" and "The deficit does not depend on the corridor". Both are followed by numbers.
- 1160: "counts the edge twice; the nearest point … counts it once". This is the technical point itself.
- 1172: "computed from the model rather than fitted to it". This states that the prediction has no fitted parameter.
- 1175: "describes a deadlock once formed, not its formation". This defines the scope of a limitation.
- 1136: "Matched on rate, the bias shares ORCA's number, not its mechanism." It is kept as the one aphorism that earns its place (section 10).


---

## 2. Sentences that announce their own significance

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

| # | Line | File | Quoted text | Replacement |
|---|---|---|---|---|
| 2.1 [L] | 916 | MOD | "(note $v_0$, not $v_{\rm eff}$)" | "(with $v_0$, not $v_{\rm eff}$)" |

Checked with no other hits in range: notably, crucially, importantly, significantly, it is worth, the key point, what matters, indeed, in fact. "Our thesis is that" (832) states the thesis rather than announcing significance, so it is kept.

### Block M: §4–§5 (main.tex 927–1071)

None in range. I searched lines 927-1071 for "worth", "important", "crucial(ly)", "notabl(y)", "significant(ly)", "key", "what matters" and "the point is", and found no instances.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

No instances. I searched lines 1072–1183 for: it is worth noting, it is important, it is worth pausing, crucially, notably, significantly, importantly, the key point, what matters, remarkably, interestingly, strikingly. Topic sentences that announce what follows appear under category 3.


---

## 3. Sentences that announce what a section will do

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

| # | Line | File | Quoted text | Fix |
|---|---|---|---|---|
| 3.1 [M] | 839 | INT | "Sections~\ref{sec:background}--\ref{sec:signatures} give the background, the model as the code implements it, and the classes and signatures; Sects.~\ref{sec:physics}--\ref{sec:validity} the deadlock physics, the attribution results and the comparison with human data." | Delete. Each contribution bullet (834–837) already ends with its section pointer, and a Background–Model order needs no announcement. The sentence also uses "the code" (see 11.7). |
| 3.2 [L] | 842 | BKG | "Sect.~\ref{sec:model} combines all three in one force-based model, so that single terms can be switched off at a frozen state." | "Our model combines all three as force terms, so that each can be switched off at a frozen state." This keeps the purpose and drops the forward pointer. Alternatively delete it, since 887 shows the terms being switched. |
| 3.3 [L][TASTE] | 832 | INT | "The contributions are:" | Keep. A contribution list is the LNCS convention. The competing convention is to fold the contributions into prose. |

**3.4 Restated paragraph, 834–837 (INT).** The contributions list restates abstract sentences 3–6 in the same order (Method, two classes, matched controls, CroMa), and 1177 states it a third time. Restatement across abstract, introduction and conclusion falls under category 14 (the other auditor). Within category 3, these items are unique to 834–837 and must survive: the five-class count, the probe table pointer, 393/393 for the criterion, 46 strict minima, the no-static-friction reason, the solver dependence at the pair, and the whole-run results (other seeds, later completion, other final states).

**Kept:** 845 "and we ask what each intervention does to those rest states". It bridges to §4 without a pointer. 848 "(Sect.~\ref{sec:teff})" ends a claim rather than announcing one; its "exactly" is treated in 5.1.

### Block M: §4–§5 (main.tex 927–1071)

| # | Line / file | Quoted text | Replacement | Sev |
|---|---|---|---|---|
| 3.1 | 1069 [S5] | "Two snapshots are reported separately." | Delete. The next two sentences open with "In one, …" and "In the other, …". Make the first of them "Two snapshots are outside the fits. In one, …". (See also 16.21: say whether they belong to the \EfourN.) | L |
| 3.2 | 981 [S4] | "An intervention can act on it in five physically distinct ways." | [TASTE] Delete. The five bold leads follow at once. The competing convention keeps a count sentence before an enumerated list in physics prose, and keeping it is defensible. | L |

No paragraph in range is wholly restated by the paragraphs below it. The §4 opening (981) and Table 2 carry the same classes, but the table adds the probe predictions, so both survive.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

| # | Line, file | Sev | Text | Fix |
|---|---|---|---|---|
| 3.1 | 1136 [06] | L | "The signatures separate them." | Delete. The next sentence does the separating. Its subject "They" then needs a noun: "The bias and ORCA free different standoffs" (or apply 9.12). |
| 3.2 | 1160 [07] | L | "Three points follow for practitioners who simulate narrow doors with a social force model." | Delete. With the heading of 7.11 ("Recommendations for narrow-door models"), "First/Second/Third" carry the structure. [TASTE] An enumerating lead is a common convention in recommendation paragraphs. Delete it only if the heading is changed. |
| 3.3 | 1166 [08] | L | "The signatures also say why the rates coincide." | Delete. Open with "At rest ORCA adds …" (see 16.13). The paragraph's second-to-last sentence states the "why". |
| 3.4 | 1177 [09] | L | "Three findings support this." | Delete. The three findings follow at once, as sentences 4–6. |
| 3.5 | 1157 [07] | L | "No model variant reproduces this." | Delete. It restates the heading, and the next sentence gives the numbers. If the heading is changed per 7.10, keep it as the topic sentence. |
| 3.6 | 1151 [07] | M | "The deadlocks of Sects.~\ref{sec:physics} and~\ref{sec:attribution} are properties of the model. Whether real crowds show anything like them at the same width is a separate question, and we ask it like for like." | "We compare the model's deadlocks with human runs at the same width, like for like." |
| 3.7 | 1163 [08] | M | The whole "What testing adds to calibration" paragraph is a summary of §6: every number in it (Δ for lone trap and whole runs; J = 0.20, 0.41, 0.30, 0.43, 0.00) is already in §6.1–§6.2 and Table 3. **Unique and should survive:** sentence 1 ("A matched control shows whether a simpler cause suffices for the paradigm's score, and in all three of our pairs it does.") and sentence 3 (the conference-protocol reading, rewritten per 1.8). **Cut to a pointer:** sentence 2, replaced by "Noise frees lone keystones and completes whole runs at ORCA's rate, and a bias frees pair standoffs at the rate of the matching solver (Table~\ref{tab:matched})." **Rewrite** sentence 5 as "Each control frees different deadlocks from ORCA's (Table~\ref{tab:matched}) and shows the signature of its own class, which ORCA lacks: time-step dependence and seed disagreement for noise, handedness for the bias." |
| 3.8 | 1177 [09] | — | The Conclusions paragraph restates the abstract (652) in the same order. This is reported only as a pointer: it belongs to category 14 (other auditor). Entries 1.12, 1.13, 3.4, 9.27–9.29 fix the sentences inside it. |


---

## 4. Trailing appositive qualifications

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

| # | Line | File | Quoted text | Replacement / action |
|---|---|---|---|---|
| 4.1 [H] | 835 | INT | "and a symmetric pair standoff, a strict minimum of the rest-state energy in all \PairStrictMin\ library cases, softest along the common lateral shift, which a lateral bias breaks at a fold." | Three stacked appositives. **Dangling:** "which" attaches to "the common lateral shift", but the bias breaks the standoff. Split: "… and a symmetric pair standoff. The standoff is a strict minimum of the rest-state energy in all \PairStrictMin\ library cases, softest along the common lateral shift of the pair, and a lateral bias removes it at a fold." |
| 4.2 [M] | 837 | INT | "Rebuilt like for like around the CroMa bottleneck experiments, every model variant passes only …" | **Dangling modifier.** The geometry is rebuilt, not the variant. "In a geometry rebuilt like for like around the CroMa bottleneck experiments, every model variant passes only …". The out-of-range partner at 1177, "Rebuilt like for like around a human bottleneck experiment, no model variant flows like people", has the same defect. |
| 4.3 [M] | 893–895 | MOD | "…,\,0.05,\,1\right],\end{equation} Weidmann's speed--density relation~\cite{weidmann1993}, with $\rho_i=N_i/(\pi R^2)$ and $N_i$ the other active agents within $R$." | **Dangling appositive.** It hangs off the display and grammatically attaches to Eq. 2 as a whole. End Eq. 2 with a full stop and write: "The speed $v_{{\rm eff},i}$ follows Weidmann's speed--density relation~\cite{weidmann1993}, with $\rho_i=N_i/(\pi R^2)$ and $N_i$ the number of other active agents within $R$." |
| 4.4 [M] | 920 | MOD | "The crush term of C4 has the SFM contact form with larger coefficients and gate $w_{c,i}=s(\rho_i;5.5,3)$, almost inert at the disc density." | **Dangling.** It is unclear whether "almost inert" refers to the gate or to the term. "The disc density" is undefined (it could mean the density in the disc of radius $R$, or the density at deadlock). Promote to its own sentence with the number: "The crush term of C4 has the SFM contact form with larger coefficients and gate $w_{c,i}=s(\rho_i;5.5,3)$. At the deadlock densities ($\rho\le\TermRhoMax$\,ped/m$^2$) this gate is below $10^{-6}$." ($s(0.35;5.5,3)\approx2\times10^{-7}$. If "disc density" meant something else, state that density and its gate value instead.) |
| 4.5 [L] | 836 | INT | "At the pair class ORCA acts through its constraint part, differently in the two solvers, and …" | The trailing adverbial defers its content. "At the pair class ORCA acts through its constraint part, and the two solvers free different numbers of standoffs (\PairPubFreed\ and \PairRvoFreed\ of \PairN); a lateral bias matched to its rate frees other standoffs, with a handedness ORCA lacks." |
| 4.6 [L] | 851 | BKG | "…and proposed perturbation strategies to leave them; their safety constraints play the role of ORCA's half-planes here." | Trailing editorial clause whose antecedent ("their") is ambiguous. "…and proposed perturbation strategies to leave them. The safety constraints of those robots play the role that ORCA's half-planes play here." |
| 4.7 [L] | 845 | BKG | "Zuriguel et al.\ proposed that the flow is clogged when the mean duration of the stoppages diverges, a property of the heavy tail of their distribution~\cite{zuriguel2014}." | The appositive attaches to "diverges". "Zuriguel et al.\ proposed that the flow is clogged when the mean duration of the stoppages diverges, which happens when their distribution has a heavy enough tail~\cite{zuriguel2014}." |
| 4.8 [L] | 652 S4 | ABS | "and a symmetric pair standoff, a strict energy minimum that a lateral bias removes at a fold." | "and a symmetric pair standoff, which is a strict energy minimum that a lateral bias removes at a fold." (See also 16.9 for the parallel list.) |
| 4.9 [L] | 923 | MOD | "…by $(\hat{\mathbf e}_i+b\,\hat{\mathbf e}^{\perp}_i)/|\hat{\mathbf e}_i+b\,\hat{\mathbf e}^{\perp}_i|$, a deterministic tilt of fixed handedness." | Lead with the definition: "The lateral-bias control is a deterministic tilt of fixed handedness: it replaces $\hat{\mathbf e}_i$ in Eq.~\eqref{eq:des} by …". Move the sentence as in 7.3. |
| 4.10 [L][TASTE] | 920 | MOD | "…towards the goal, \emph{ORCA's rest drive}." | "…towards the goal, which we call \emph{ORCA's rest drive}." The competing convention, an italic appositive at the point of definition, is common in physics writing and is acceptable here. |
| 4.11 [L] | 822 | F1C | "…and black plus grey equals the wall arrow." | Delete. This is an interpretive tail on the caption (8.1). |
| 4.12 [L] | 906 | MOD | "…(convex-union rule), which removes the double count outside a convex corner and keeps both walls inside a concave one." | Promote to its own sentence (9.6). |

### Block M: §4–§5 (main.tex 927–1071)

| # | Line / file | Quoted text | Action and replacement | Sev |
|---|---|---|---|---|
| 4.1 | 1053 [S5] | "gives gated pair barriers of \PairBarMin--\PairBarMax\,J (median \PairBarMed\,J), far below the lone-trap barriers," | **Dangerous.** No lone-trap barrier appears anywhere in the paper. Replace with the number, registered as a macro: "…gives pair barriers of \PairBarMin--\PairBarMax\,J (median \PairBarMed\,J), against 16--45\,J for the lone traps, and …". The 16--45 J range is from CHANGELOG C15. Register it from the barrier library rather than typing it. | H |
| 4.2 | 1008 [S4] | "A restoring curvature $K$ adds terms of order $(\omega\Delta t)^2$, $\omega^2=K/m_i$, negligible in our snapshots." | Replace the hedge with the number: "A restoring curvature $K$ adds terms of order $(\omega\Delta t)^2$, with $\omega^2=K/m_i$; in our snapshots they change $k_BT_{\rm eff}$ by at most 0.3\%." The 0.3% is CHANGELOG C30. Register it as a macro. | M |
| 4.3 | 1033 [S5] | "The C1 drive has median \DriveCOneMedian\,N (5--95\%: \DriveCOneLo--\DriveCOneHi\,N), comparable to $g_{\max}$ at the mean radius," | Replace with the number: "The C1 drive has median \DriveCOneMedian\,N (5--95\%: \DriveCOneLo--\DriveCOneHi\,N), against $g_{\max}=$\GmaxTwentyFive\,N at $r=0.25$\,m." Use the radius that matches the Table 1 mean. | M |
| 4.4 | 1051 [S5] | "all \PairFoldFN\ disagreements are quenches that escape at a bias at most \PairFoldMissGap\% below the snapshot's static threshold, where the members' inertia carries them over." | Promote it to its own sentence and mark its status. "…below the snapshot's static threshold. We attribute these to the members' inertia, which the static calculation omits." | M |
| 4.5 | 1053 [S5] | "…(pooled Weibull shape \PairWeibLow\ at $\sigma=0.01$ and \PairWeibHigh\ at $0.05$\,m/s): once kicked off the shallow minimum, the pair needs a few seconds of deterministic run-out to clear the door." | Promote to its own sentence with a number: "Once off the minimum, the pair takes [median run-out] s of deterministic motion to clear the door, which makes the escape-time distribution peaked." If no run-out time is measured, delete "a few seconds of" and keep the mechanism sentence. | M |
| 4.6 | 1037 [S5] | "…predicts whether it exits with an area under the ROC curve of \EOneBAUCOthers\ [\EOneBAUCOthersLo, \EOneBAUCOthersHi], against an all-exit baseline accuracy of \EOneBAllExitBaseline." | Promote it to its own sentence; see 16.13 for the full replacement. | M |
| 4.7 | 981 [S4] | "a strict minimum survives small biases and disappears at a fold, at bias $b^\ast$." | "a strict minimum survives small biases and disappears at a fold, at the fold bias $b^\ast$." Alternatively: "… and disappears at the fold bias $b^\ast$." | L |
| 4.8 | 1065 [S5] (dangling) | "…took the values 1.5, 2.5 and 3.5, with \EfourRestarts\ restarts per level, censored at 300\,s (900\,s at 3.5)." | "censored" attaches to "level". Write: "…took the values 1.5, 2.5 and 3.5. Each level had \EfourRestarts\ restarts, each censored at 300\,s (900\,s at 3.5)." | L |
| 4.9 | 1042 caption [S5] (dangling) | "…and at $w=0.8$\,m for each wall-law variant (right), with the range $B_w$ in metres." | "with the range" attaches to the panel, not to the tick labels. Replacement in 8.3. | L |
| 4.10 | 1029 [S5] | "…so $v_{\rm eff}=v_0$, and the agent is held when it is alone if and only if" | Split the trailing conclusion from the approximation; replacement in 5.3. | L |
| 4.11 | 981 [S4] (dangling) | "Paired by snapshot, they are not tuned…" | The participle attaches to "they" (the probes), but the pairing belongs to the interventions. Fixed by 1.2. | M |

**Parenthetical hedges kept:** 1001 "(class P at most)" and "(a candidate for class L)". Both are scoped by the lemma, and Table 2 decides them, so they are honest qualifications.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

| # | Line, file | Sev | Text | Fix |
|---|---|---|---|---|
| 4.1 | 1120 [06] | H | "…, which a replay this small reveals as ill-conditioning of that implementation (class N) and base forward claims on RVO2." | Promote to its own sentence (split given under "Worst sentence"). The trailing clause carries the paragraph's verdict, and its second verb has no subject. |
| 4.2 | 1111 [06] | L | "C1 and C2 free none, C2 reproducing C1 in \EtwoLemmaIdentical\ of \EtwoLemmaPairs\ paired runs (Proposition~\ref{prop:rest})." | "C1 and C2 free none; C2 reproduces C1 in 360 of 360 paired runs, as Proposition~\ref{prop:rest} predicts." Promote. |
| 4.3 | 1123 [06] | M | "have Weibull shape \EsixStallWeib\ […], a mixture over barriers, and their survival …" Grammatically, the appositive "a mixture over barriers" attaches to the shape value 0.64. | "have Weibull shape 0.64 [0.58, 0.70], below 1 because they mix escapes over different barriers. Their survival …" Promote. |
| 4.4 | 1133 [06] | L | "…, so a claim about ORCA here concerns one solver." | Promote: "A claim about ORCA at the pair therefore holds for one solver only." |
| 4.5 | 1136 [06] | M | "…, though \PairN\ standoffs are too few to show equivalence within $\pm0.10$." | Promote, and state it with the intervals already in Table 3: "With 46 standoffs the 95\% intervals of the rate differences are wide ($[-0.15, 0.22]$ and $[-0.13, 0.17]$)." Note on C6: the plan keeps equivalence margins internal, so "within $\pm0.10$" is the internal margin surfacing in prose. CHANGELOG C44 records the wording, so this is the authors' call. The replacement keeps the content and drops the margin. Line 1175 needs the same change (16.28). |
| 4.6 | 1136 [06] | M | "at $-b^\ast_{\rm pub}$ the other member exits first in \PairBsPubMinusUpper\ of \PairBsPubMinusFreed, on largely different standoffs (discordant \PairBsPubRevA:\PairBsPubRevB)." | "at $-b^\ast_{\rm pub}$ the upper member exits first in 21 of 21, and only 8 standoffs are freed at both signs (discordant 13:14)." This promotes the trailing clause, replaces "largely" with the count (22 − 14 = 21 − 13 = 8), and names the member (16.1). |
| 4.7 | 1117 [06] | L | "and \EthreeEllBB\ […] (predicted \EthreeEllBBPred, outside the interval)" | The confession sits inside a parenthesis. Promote: "… and 3.23 [2.96, 3.52] (predicted 3.70). The second prediction lies outside its interval." Combine with 9.5. |
| 4.8 | 1157 [07] | L | "C3 RVO2 never deadlocks but completes only \EtenCThreeComplete\ runs within 600\,s, the other \EtenCThreeCapped\ still moving at the cap, and C1 $+\,\sigma^\ast$ completes \EtenCSigComplete." | "C3 RVO2 never deadlocks but completes only 10 runs within 600\,s; the other 15 are still moving at the cap. C1 $+\,\sigma^\ast$ completes 14." |
| 4.9 | 1157 [07] | L | "the flow, counted up to the deadlock where there is one, is …" | Move the counting rule to the estimator definition at 1151: "the flow (first to last passage, or to the deadlock where there is one)". Then line 1157 reads "the flow is …". |
| 4.10 | 1175 [08] | L | "we studied one family of door geometries, room exits near $w=0.8$\,m, and compared with human data at that width only." The appositive reads as a list item. | "we studied one family of door geometries (room exits with $w$ near 0.8\,m) and compared with human data at $w=0.8$\,m only." |
| 4.11 | 1177 [09] | M | Dangling modifier: "Rebuilt like for like around a human bottleneck experiment, no model variant flows like people". The geometry was rebuilt; the variant was not. | "In a like-for-like rebuild of a human bottleneck experiment, no model variant flows like people: …" The same dangle is at line 837 (§1, "Rebuilt like for like around the CroMa bottleneck experiments, every model variant passes …"), which is out of range and cited as the partner. |


---

## 5. Softening adverbs on binary claims

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

| # | Line | File | Quoted text | Replacement |
|---|---|---|---|---|
| 5.1 [M] | 848 | BKG | "and its effective temperature follows exactly from that recursion (Sect.~\ref{sec:teff})." | "and its effective temperature follows in closed form from that recursion (Sect.~\ref{sec:teff})." In §4.2 the relation holds "nearly" and carries a harmonic correction (1008), so "exactly" conflicts with it. |
| 5.2 [M] | 920 | MOD | "almost inert" | Replace with the gate value (4.4). |
| 5.3 [L] | 851 | BKG | "are the generic perturbations used to leave such equilibria" | "Generic" does argumentative work but is never defined. "The controls we test, noise and a lateral bias, are perturbations of this kind." |
| 5.4 [L][TASTE] | 828 | INT | "Steering models are commonly described by the mechanism each one adds:" | "Steering models are described by the mechanism each one adds:". The claim about usage needs either a citation or no hedge. Competing convention: "commonly" is accepted as background framing. |

**Kept:**
- 913 "exactly zero". Literal.
- 826 "only as trustworthy as". Comparative idiom.
- 837 "passes only \EtenCSigFlowRatio--\EtenCThreeFlowRatio". The number carries it.
- 851 "has long been known". Cited.
- 830 "minimal control". Defined by the colon clause.
- 652/830 "simpler cause". Defined by "shares none of its machinery".
- "only" at 842, 866, 887, 906, 913. Technical restriction.
- 652 "shows only that" is treated in 1.6.

### Block M: §4–§5 (main.tex 927–1071)

| # | Line / file | Quoted text | Replacement | Sev |
|---|---|---|---|---|
| 5.1 | 1067 [S5] | "The pooled Weibull shape of the escape times is \EfourWeib\ [\EfourWeibLo, \EfourWeibHi], close to the exponential value 1," | The interval [1.05, 1.14] excludes 1, so the hedge contradicts the number. Write: "The pooled Weibull shape of the escape times is \EfourWeib\ [\EfourWeibLo, \EfourWeibHi], 9\% above the exponential value 1." | H |
| 5.2 | 1071 [S5] | "The conference estimate, \EfiveConfSigmaFifty\,m/s from 25 runs per level~\cite{gang2026}, lies just above both intervals." | "…lies above both intervals (upper ends \EfiveSigmaFiftyHi\ and \EfiveASigmaFiftyHi\,m/s)." CHANGELOG C36 already records "outside both intervals". | M |
| 5.3 | 1029 [S5] | "the blocker's Weidmann factor is at least \TermWeidMin\ (all \TermN\ deadlocks; Sect.~\ref{sec:model}), so $v_{\rm eff}=v_0$," | The minimum is 0.994, so the equality is approximate. Write: "…is at least \TermWeidMin\ (all \TermN\ deadlocks; Sect.~\ref{sec:model}). We therefore set $v_{\rm eff}=v_0$, and the agent is held when alone if and only if". | M |
| 5.4 | 1008 [S4] | "At fixed per-step $\sigma$, $k_BT_{\rm eff}\propto1/\Delta t$ nearly; $\sqrt{\Delta t}$-scaled noise holds it nearly fixed." | Two uses of "nearly"; Eq. (9) gives the exact correction. Write: "At fixed per-step $\sigma$, $k_BT_{\rm eff}\propto1/\Delta t$ up to the factor $(1-\Delta t/2\tau_i)^{-1}$; $\sqrt{\Delta t}$-scaled noise holds it fixed up to the same factor." | M |
| 5.5 | 1014 [S4] | "positive for $\Delta t_1<\Delta t_2$ at fixed per-step $\sigma$, near zero for $\sqrt{\Delta t}$-scaled noise," | "…, and for $\sqrt{\Delta t}$-scaled noise nonzero only through the factor $(1-\Delta t/2\tau_i)^{-1}$," | L |
| 5.6 | 1047 [S5] | "the corrected-forward mode produces it often enough to build a library of \PairN\ snapshots from independent runs." | "the corrected-forward mode produces it in \EsevenBjambCollective\ of \EsevenN\ runs (Sect.~\ref{sec:lone}); \PairN\ snapshots from independent runs form the pair library." | M |
| 5.7 | 1049 [S5] | "Only a finite shift of 3\,cm carries some standoffs out of the basin (\PairDeltaThreeCmFreed\ of \PairN)." | A 1 cm shift is also finite, so "finite" defines nothing, and "some" is vague next to its own count. Write: "A shift of 3\,cm carries \PairDeltaThreeCmFreed\ of \PairN\ standoffs out of the basin." | M |
| 5.8 | 1053 [S5] | "Here $\Delta U/k_BT_{\rm eff}$ is below 1 at every noise level we ran for most snapshots," | Replace "most" with a count: "Here $\Delta U/k_BT_{\rm eff}$ is below 1 at every noise level for [k] of \PairBarN\ snapshots," | M |
| 5.9 | 1035 [S5] | "so a typical deadlock is a short stack of stuck-alone agents." | "so most deadlocks are short stacks of stuck-alone agents." The count is in the clause before. | L |
| 5.10 | 1035 [S5] | "Completion of whole runs is correspondingly rare:" | "Completion of whole runs is rare:". The link "correspondingly" asserts a causal relation the sentence does not show. | L |
| 5.11 | 1056 [S5] | "we drove the bottleneck hard:" | [TASTE] "we ran the bottleneck at high drive:". The competing convention allows informal register in a methods aside, and the colon list after it is specific. | L |
| 5.12 | 1053 [S5] | "Noise of $\sigma=0.01$\,m/s already frees …" | [TASTE] Delete "already". The competing convention allows "already" to mark a low threshold, and here it does mark one. | L |

**Kept, because each is backed by a binary or exact result:**
- 991 "exactly the states", 1001 "exactly C1's fixed points": mathematical identity.
- 1035 "exactly the cases with positive margin", 1035 "exactly the deadlocks that are not lone traps" (the latter disappears under 1.6): 393 of 393.
- 1051 "no standoff is exactly symmetric": a binary geometric statement.
- 1029 "steeply": three numbers follow.
- 1051 "loads the soft mode directly": it means a projection onto the mode.

**Internally contradictory pairs:** none of the "almost exactly" type. Entry 5.1 is the closest case: a hedge against an interval that excludes the hedged value.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

| # | Line, file | Sev | Text | Fix |
|---|---|---|---|---|
| 5.1 | 1123 [06] | M | "The failure sets overlap barely more than independent ones would (Jaccard \EsixJaccard\ against \EsixJaccardIndep; …)" | "The Jaccard index of the failure sets is 0.41, against 0.30 for independent sets of the same sizes (discordant 35:37, $p=0.906$)." |
| 5.2 | 1136 [06] | M | "on largely different standoffs" | Replaced by the count in 4.6. |
| 5.3 | 1136 [06] | M | "and noise frees nearly every standoff (Sect.~\ref{sec:pair})" | "and noise at $\sigma=0.01$\,m/s already frees \PairNoiseLowFreed\ of \PairNoiseLowN\ runs (Sect.~\ref{sec:pair})" (224 of 230). |
| 5.4 | 1156 [07] | M | Heading "… flows at about half the human rate." | The range is 0.40–0.59 of the human flow. The heading is replaced under 7.10, so no hedge remains. |
| 5.5 | 1163 [08] | L | "The minority outcome sets overlap little (…)" | Use 3.7 (pointer to Table 3). Or, if the numbers stay: "The minority outcome sets have Jaccard indices of 0.20 at the lone trap, 0.41 in whole runs (0.30 for independent sets), and 0.43 and 0.00 at the pair." |
| 5.6 | 1169 [08] | M | "results should name a validated solver." "Validated" is undefined: validated against what? | "results should name the solver and show that its outcomes survive $10^{-9}$\,m replays." |
| 5.7 | 1157 [07] | L | "The model's waiting zone is also more agitated than the human one, …" "Agitated" is an undefined evaluative word for a defined quantity. | "The model's waiting-zone velocity fluctuation is also higher than the human one, …" |
| 5.8 | 1166 [08] | L | "as the low overlaps show" | "as the Jaccard indices of Table~\ref{tab:matched} show" |
| 5.9 | 1117 [06] | L | "On \EthreeN\ snapshots spread over the collective barrier" | "On 20 snapshots chosen to span the range of collective barriers" |
| 5.10 | 1114 [06] | L | "Identity is compared throughout by the Jaccard index" | "Identity is compared in every block of Table~\ref{tab:matched} by the Jaccard index" (or use the split in 9.3). |
| 5.11 | 1120 [06] | L | "The constraint part from its half-plane, negligible at restart, builds up once the agents move" "Negligible" has no number behind it, and none is in the registry. | Delete "negligible at restart" (see 9.6). If a restart value exists, write it in N instead. |
| 5.12 | 1157 [07] | L [TASTE] | "completes only \EtenCThreeComplete\ runs" | Keep. "Only" is backed by the count against 25 and the human 5 of 5. The competing convention is to state the count alone. |
| — | 1111 [06] | keep | "$10^{-9}$\,m replays reproduce C3 RVO2 exactly (largest first-exit shift \EtwoReplayCThreeRVOMaxDt\,s in \EtwoReplayN)" | Keep "exactly": the number (0.000 s) justifies it. |

No internally contradictory pairs ("almost exactly", "essentially always") occur in the range.


---

## 6. Sentences beginning with "What" and other clefts

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

| # | Line | File | Quoted text | Replacement |
|---|---|---|---|---|
| 6.1 [L] | 828 | INT | "When a configuration that includes ORCA empties a room that pure SFM leaves jammed, it is tempting to say that reciprocal avoidance resolved the jam." | "When a configuration that includes ORCA empties a room that pure SFM leaves jammed, the obvious reading is that reciprocal avoidance resolved the jam." |
| 6.2 [L] | 923 | MOD | "Results of social force models depend on the integration scheme~\cite{koster2013}, which is why the forward claims use a corrected update." | "Results of social force models depend on the integration scheme~\cite{koster2013}; all new results therefore use the corrected-forward update (Table~\ref{tab:params}, bottom)." (This merges with 16.18.) |

There are no sentences opening with "What" in the range. Checked for "It is X that", "There is/are … which/that" and "The thing that": only 6.1.

### Block M: §4–§5 (main.tex 927–1071)

| # | Line / file | Quoted text | Replacement | Sev |
|---|---|---|---|---|
| 6.1 | 1037 [S5] | "Why the blocker is a stuck-alone agent follows from the order of arrival." | "The order of arrival explains why the blocker is a stuck-alone agent." | L |

Checked and not cleft: "It is", "it is" at 981, 1029, 1049 and 1069 are ordinary pronoun uses. There are no "There is … which" or "What …" openings.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

| # | Line, file | Sev | Text | Fix |
|---|---|---|---|---|
| 6.1 | 1162 [08] | M | Heading "What testing adds to calibration." | "Calibration and testing." (see 7.12). |
| 6.2 | 1151 [07] | M | "Whether real crowds show anything like them at the same width is a separate question, and we ask it like for like." This is a clause-as-subject construction used for emphasis. | Use 3.6: "We compare the model's deadlocks with human runs at the same width, like for like." |
| 6.3 | 1157 [07] | L | "Whatever the variant, the flow, …, is …" | "For every variant the flow is …" (see 9.19). |

No "It is X that …", "There is X which …" or "The thing that …" constructions occur in the range.


---

## 7. Headers and bold paragraph leads

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

| # | Line | File | Heading | Replacement |
|---|---|---|---|---|
| 7.1 [L][TASTE] | 13, 14 | MAIN | Title and running head built on "Is Not Enough" | See 1.9 and 1.10. |
| 7.2 [L] | 837 | INT | "\emph{Validity.}" | "\emph{Human data.}" The lead names a verdict ("validity") that the bullet then contradicts (every variant flows at about half the human rate). The out-of-range partner is the §7 heading at 1144, "Validity Against Human Data", which could become "Comparison with Human Data". |
| 7.3 [L] | 922 | MOD | "Integration and noise." | Keep the heading and move the lateral-bias sentence ("The lateral-bias control replaces $\hat{\mathbf e}_i$ …", 923) to the end of the "Desired force and density." paragraph (895), because it modifies $\hat{\mathbf e}_i$ in Eq. 2. As it stands, the heading does not name a third topic the paragraph contains. |

Checked and kept (each names its content): Introduction, Background, Model and Scenarios; the paragraph heads "Steering paradigms.", "Clogging at bottlenecks.", "Activated escape.", "Deadlock in multi-agent systems.", "Testing mechanisms in models.", "Desired force and density.", "Social force and walls.", "Time to collision.", "ORCA as a force.", "Scenarios and statistics."; and the bullet leads "Method.", "Physics.", "Attribution.". "Model and Scenarios" does not mention the statistics in 925–926. Adding them would make a three-item heading, so keep it [TASTE].

### Block M: §4–§5 (main.tex 927–1071)

| # | Line / file | Current | Replacement | Reason | Sev |
|---|---|---|---|---|---|
| 7.1 | 1046 [S5] | "The Symmetric Pair Standoff" | "The Pair Standoff at the Jamb Faces" | The body says at 1051 that "no standoff is exactly symmetric". The adjective also recurs at 1177 (§9). | H |
| 7.2 | 1016 [S4] and 1058 [S5] | "Collective Activated Escape" / "Noise as Collective Activated Escape" | 1016: "String-Method Barriers and Kramers Predictions"; 1058: "Escape Under Per-Step Noise" | Near-duplicate headings defeat scanning. §4.3 holds the method and predictions, §5.4 the test, and 1058 also states its result in the heading. | M |
| 7.3 | 1055 [S5] | "No Persistent Contact Arches" | "Contact Arches at High Drive" | The heading states a negative result. The finding belongs in the subsection's last sentence. | M |
| 7.4 | 1019 [S4] | bold lead "Calibrate, then falsify." | "Attribution protocol." | The lead reads as a slogan. The paragraph is also attached to §4.3 (barriers), although it governs §6. Either move it to the end of the §4 opening, after Table 2 is introduced, or give it its own `\subsection{Attribution Protocol}`. | M |
| 7.5 | 981 [S4] | run-in leads "P, prevent:", "L, reshape:", "T, heat:", "D, steer:", "N, glitch:" | [TASTE] "N, artefact:" | "glitch" is colloquial next to four physics verbs. The competing convention keeps a one-word mnemonic verb per class, and "glitch" is used consistently in the Table 2 caption. | L |

Headings checked and kept: 927 "Mechanism Classes and Their Physical Signatures" (the name recorded in CHANGELOG C6), 983 "Terms That Vanish at Rest", 1003 "Effective Temperature of Per-Step Noise", 1021 "Deadlock Physics", 1022 "The Lone-Agent Trap at the Door Edges".

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

Of the 16 headings and run-in leads in the range, seven state a result (1110, 1113, 1132, 1135, 1153, 1156, 1165) and the rest name their content. This mix is itself the defect: a reader scanning §6 cannot tell the two kinds apart. Three of the headings also form a paired device with the paper title ("One Matched Control Is Not Enough"): 1135 "One matched bias is not enough." and 1165 "One rate, different mechanisms."

| # | Line, file | Sev | Heading | Problem | Replacement |
|---|---|---|---|---|---|
| 7.1 | 1110 [06] | H | "ORCA is its rest drive." | States a result. It is also false beyond the lone keystone: 1120 and 1132 show the constraint part acting at the second trap and at the pair. | "ORCA at the lone keystone." |
| 7.2 | 1113 [06] | M | "Matched noise acts differently." | States a result. | "Matched noise at the lone keystone." |
| 7.3 | 1119 [06] | M | "The second trap and the published solver." | Two topics. The replay finding (the last sentence) is unrelated to the second-trap mechanism. | "The second trap." Move the last sentence (rewritten per 4.1) to its own paragraph headed "Replays of the published solver." |
| 7.4 | 1125 [06] | L [TASTE] | "The Pair Class" | Not parallel to 1073 "The Lone Trap" or to §5.2 "The Symmetric Pair Standoff". The competing convention is to name the class, as Table 2 does. | "The Pair Standoff" |
| 7.5 | 1132 [06] | H | "ORCA acts through its constraint part, per solver." | Two results in one heading. | "ORCA at the pair standoff." |
| 7.6 | 1135 [06] | H | "One matched bias is not enough." | An argument, and it echoes the title. | "The matched lateral bias." |
| 7.7 | 1138 [06] | L [TASTE] | "Revisiting the Conference Findings" | Narrates. The competing convention: gerund subsection titles are common in LNCS. The section is pending. | "Conference Findings Revised" |
| 7.8 | 1144 [07] | L [TASTE] | "Validity Against Human Data" | Names a verdict, and the section finds the model fails at this width. The competing convention is the V&V use of "validity" as a section name. | "Comparison with Human Data" |
| 7.9 | 1153 [07] | M | "Humans flow without deadlock." | States a result. | "Human runs." |
| 7.10 | 1156 [07] | H | "Every model variant deadlocks or flows at about half the human rate." | The longest heading in the paper. It states two results and hedges ("about half"). | "Model runs." |
| 7.11 | 1159 [07] | M | "Wall treatment at door edges." | Does not cover the paragraph: its third point is about capacity and noise, not walls. | "Recommendations for narrow-door models." |
| 7.12 | 1162 [08] | M | "What testing adds to calibration." | A "What" clause (category 6). | "Calibration and testing." |
| 7.13 | 1165 [08] | M | "One rate, different mechanisms." | A slogan, and the third "One …" in the paired device. | "Mechanisms behind a shared rate." |

Kept: 1073 "The Lone Trap", 1116 "The time-step signature.", 1122 "Matched completion of whole runs.", 1168 "Implications for model users.", 1171 "Clogging and robot deadlock.", 1174 "Limitations.", 1178 "Main Differences from the Conference Version.", 1181 "Data and Code Availability."


---

## 8. Figure and table captions

### 8.0 Paper-wide reconciliation

Standing rule C3: captions have at most two sentences. The prompt's ceiling is about sixty words.

| Float | Line | Verdict | Entry |
|---|---|---|---|
| Fig. 1 | 822 | 170 words; method specification; interpretive tail | F8.1 |
| Table 1 | 857 | file path; "declared" | F8.2 |
| Table 2 | 929 | three sentences; defines symbols that no cell uses | M8 |
| Figs 2, 3, 4 | 1026, 1042, 1062 | see block M | M8 |
| Fig. 5 | 1077 | see block R | R8 |
| Fig. 6 | 1083 | see block R | R8 |
| Table 3 | 1087 | too long; carries experiment codes and a method rule | R8 |
| Fig. 7 | 1129 | passes | R8 |
| Fig. 8 | 1148 | see block R | R8 |

No caption carries a result that appears nowhere else, except where a block entry says so explicitly.

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

**8.1 [H] Fig. 1 caption, 822 (F1C).** Two sentences, so within the letter of plan C3, but 170 words (sentence 1: 75 words; sentence 2: 94 words), nearly three times the ~60-word ceiling.
- Sentence 1 nests a parenthetical inside a participial clause and then chains "with … before and after … ; the black ball …".
- Sentence 2 packs a four-item parenthetical inside its second clause and ends in a colon list.

Content to cut or move:
- (a) "with every other agent pinned at the snapshot". This is method specification and appears nowhere in the text for Fig. 1. **Move** to §5.1. After the stuck-alone margin is defined (1033), add: "Fig.~\ref{fig:hero} (top) shows a lone-keystone blocker's rest-state energy along the door axis with the other agents pinned, with and without ORCA's rest drive."
- (b) "wall ranges $B_w=0.08$~m above and $0.04$~m below". This specifies the scenes. **Move** to §5.2 at 1047, after the library sentence: "Fig.~\ref{fig:hero} (bottom) shows one of them."
- (c) "background below 5~N, orange to dark purple up to 1000~N". This is the colour key. Keep it, shortened.
- (d) "and black plus grey equals the wall arrow". This interprets the rest-state force balance already stated at 981 ("the forces on it balance"). **Delete.**
- (e) "white next to the walls marks positions an agent centre cannot occupy". Keep: required by plan C43.

Orphan measurements: none. The 10 J and 0.5 J energy scales are approved in-figure labels, and no result appears only in the caption.

Replacement (two sentences, about 85 words):
> "Top: the lone-agent trap at a 0.8~m door; bottom: the symmetric pair standoff; beside each, the rest-state energy along the blocker's door-axis position or the pair's common lateral shift, before and after ORCA's added drive or the tilt, with the frozen state as a black ball and $k_BT_{\mathrm{eff}}$ as a vermilion band. Agents are coloured by stuck-alone margin (cividis, $\pm150$~N), the floor by the backward wall force on a 0.25~m agent (log scale, 5--1000~N; white: no agent centre fits), and arrows, on one force scale, show the drive (black), the neighbours' push (grey) and ORCA's rest drive (blue) against the wall force (dark magma)."

**8.2 [M] Table 1 caption, 857 (MOD).** "Model parameters as used by the simulator (top) and the two declared modes (bottom). Values are read from the code and listed in \texttt{data/params/model.yaml}." The second sentence is process record and contains a file path. **Delete** it; the repository is already named in Data and Code Availability (1180). Sentence 1 uses "declared", which is pre-registration vocabulary (11.2), and does not name the two modes, which the text has not yet introduced (16.3). Replacement: "Model parameters (top) and the differences between the published-reproduction and corrected-forward modes (bottom)."

### Block M: §4–§5 (main.tex 927–1071)

**8.1 Table 2, line 929 [T2] (H).** The caption has three sentences, against the authors' two-sentence rule (CHANGELOG C3).
- Sentence 2, "N (glitch) is tested only by corrected numerics, under which its effect disappears.", repeats 981 ("N, glitch: … vanishes under corrected numerics"). It exists only because N has no row.
- Sentence 3 defines $k_BT_{\rm eff}$ and $\Delta U$. **Neither symbol appears in any table cell** (see p-07); only $b^\ast$ and $\Delta t$ do.

Replacement: "Predicted response of each class to each probe of a frozen deadlock; ``---'': the probe does not test that class; $b^{*}$: fold bias. Class N (glitch) shows only under corrected numerics, where its effect disappears." Alternatively, add an N row ("--- … --- & disappears") and cut the second sentence entirely.

**8.2 Fig. 2, line 1026 [S5] (H).** The caption is about 115 words in two semicolon-chained sentences, almost twice the 60-word ceiling.
- "with the population drive bands" in sentence 1 is explained again in sentence 2.
- "with the 20\,000 spawned agents" duplicates 1033 (\StuckAloneN).
- "the C3 boundary" switches to a shorter name than "C3 RVO2" used earlier in the same caption.
- No measurement in the caption is absent from the text: the $\tau$ values 0.4 and 0.6 s are the Table 1 range.

Replacement: "Left: backward wall force on a lone agent on the door axis ($w=0.8$\,m) against distance to the door plane, for $r=0.20$, 0.25, 0.30, 0.35\,m (dotted, dash-dotted, dashed, solid); bands and lines: 5--95\% range and median of the rest drive for C1 (black) and C3 RVO2 (blue). Right: stuck-alone margin over the $(r,v_0/\tau)$ plane in cividis from $-150$\,N (passes alone) to $+150$\,N (held alone), with the spawned agents as dots and the margin-zero boundaries of C1 (black) and C3 RVO2 at $\tau=0.6$ and 0.4\,s (blue)." This is about 85 words, the floor for this key.

**8.3 Fig. 3, line 1042 [S5] (M).**
- "the cell" is internal jargon (see 11.5).
- "with the range $B_w$ in metres" dangles (see 4.9).
- The outcome names "pair or group standoff" and "lone trap" do not match the body's "collective" and "stuck-alone stacks" (1035). The reader must map them by hand. Pick one vocabulary in both places; the full list belongs to the terminology audit.

Replacement: "Fraction of runs completed (point, Wilson 95\% interval) for C1 against exit width with the default walls (left), and at $w=0.8$\,m for each wall-law variant, labelled with its range $B_w$ in metres (right). Bars split all runs of a setting by outcome: completed (white), collective standoff (light grey), stuck-alone stack (dark grey)."

**8.4 Fig. 4, line 1062 [S5] (M).** The caption is about 80 words.
- "all residual agents mobile is solid with filled circles" is ungrammatical, and it ignores the condition names "full", "frozen" and "alone" defined at 1017.
- "the line of slope $-1$" does not say whether the line is the prediction or a fit. The text reports a fitted slope of $-0.93$ at 1067.
- "All in vermillion (noise)" relies on a cross-figure colour convention that is not stated in this caption.

Replacement: "Left: Kaplan--Meier fraction of deadlock snapshots whose blocker has escaped against time at $\Delta U_{\rm cond}/k_BT_{\rm eff}=2.5$, pooled over snapshots; right: escape rate over the fitted attempt rate against $\Delta U_{\rm cond}/k_BT_{\rm eff}$ for every snapshot, condition and noise level, with the predicted line of slope $-1$. Conditions: full (solid, filled circles), frozen (dashed, open squares), alone (dotted, filled triangles)."

None of the four captions contains a measurement absent from the body.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

The authors' own rule (C3) is at most two sentences: what is shown, then the colour and line key. The prompt caps captions at three sentences or about sixty words.

| # | Caption | Sev | Defects | Cut / move | Replacement |
|---|---|---|---|---|---|
| 8.1 | Fig 5, 1077 [06] (2 sentences, 58 words) | M | **Content found only in this caption (the dangerous case):** "geometric means over snapshots, 95\% bootstrap intervals" is the only place the paper says how Fig 5's points and intervals are computed, and "(inverse escape time)" is the only definition of C3 RVO2's rate in this test. Both are method specifications. "from the exact discrete $k_BT_{\rm eff}$" restates Eq. (9). | Move to line 1117, after the first sentence: "Rates are normalised per snapshot at $\Delta t=0.01$\,s and averaged geometrically over snapshots, with 95\% bootstrap intervals; for C3 RVO2 the rate is the inverse escape time." | "Escape rate against time step, normalised per snapshot at $\Delta t=0.01$\,s (95\% intervals). Per-step noise is vermillion, filled circles at $\beta_{\rm ref}=1.5$ and squares at 2.5, with its Arrhenius prediction from Eq.~\eqref{eq:teff} as lines; $\sqrt{\Delta t}$-scaled noise light vermillion with open markers; C3 RVO2 blue diamonds." |
| 8.2 | Fig 6, 1083 [06] (2 sentences, 75 words) | M | Over sixty words. "strata pooled" is a specification found only here. The figure-only results for noise at $\sigma=0.03$ and 0.05\,m/s are not mentioned in the text. | Move "strata pooled" to 1111: "(Kaplan--Meier curves pool the two strata; Fig.~\ref{fig:quench})". Add to 1114: "Lower noise levels free fewer blockers (Fig.~\ref{fig:quench})." Keep the full colour key, because Fig 7 cites it ("Colours as in Fig. 6"). | "Left: fraction of lone-trap snapshots whose blocker is freed within 120\,s, per intervention (Wilson 95\% intervals; filled lone keystone, open second trap); right: Kaplan--Meier fraction freed against time for the arms that free. C1 black, C2 orange, C3 published sky blue, C3 RVO2 blue, ORCA parts reddish purple, lateral bias yellow, noise vermillion; on the right drive only is dashed, frozen mean $+$ solid, and noise $\sigma=0.03$, 0.05, 0.07\,m/s dotted, dashed and solid." |
| 8.3 | Table 3, 1087 [T3] (3 sentences, 74 words) | M | Three sentences, against C3. "$\ell=\ln\hat\lambda(0.005)/\hat\lambda(0.02)$" restates Eq. (10) at line 1012. "(E3)" is an internal code (11.1). The J-set rule "(unresolved; pairs: freed)" repeats line 1114, while C56 says the rule is stated once in §6. "first exits by the lower member" uses an undefined term (16.1). | Cut the $\ell$ formula (point to Eq. 10), "(E3)", and the J-set parenthetical. | "Controls matched to ORCA on rate, against the signatures that separate them: freed count (whole runs: completed), paired difference $\Delta$ from ORCA, Jaccard index $J$ of the minority outcome sets, Kaplan--Meier median $t_{1/2}$, first exits by the lower member, outcome changes under $10^{-9}$\,m replays (noise: snapshots whose seeds disagree), and $\ell$ of Eq.~\eqref{eq:ell} with its prediction; intervals are 95\%. Noise rows count runs, five seeds per snapshot; --- is not measured." (`eq:ell` is the existing label at line 1012.) |
| 8.4 | Fig 7, 1129 [06] (2 sentences, 40 words) | — | Passes: it says what is plotted and how to read it, with no argument and no specification. | — | — |
| 8.5 | Fig 8, 1148 [07] (2 sentences, 66 words) | M | Over sixty words. "for the five CroMa runs at $w=0.8$\,m and for each model variant in the matched geometry" repeats line 1151. The nested parenthetical "(published mode open, corrected-forward filled, with jamb $B_w=0.04$ square)" misreads as "jamb square". | Cut the repeated run description. Line 1151 already holds it. | "Flow through the entrance, longest gap between successive passages (log scale) and waiting-zone velocity fluctuation for humans and each model variant, with single runs as small points and means with 95\% intervals beside them. Humans grey; C1 black (published mode open circle, corrected-forward filled circle, corrected-forward with jamb range $B_w=0.04$\,m filled square); C3 RVO2 blue; C1 $+\,\sigma^\ast$ vermillion." |

No caption in the range argues or justifies a design decision. Only Fig 5 contains content that appears nowhere else (8.1), and it is a specification, not a measurement.


---

## 9. Run-on and over-nested sentences

### 9.0 Paper-wide reconciliation

The worst sentence in the paper is named and split in section 0 (line 1120). Each block also names the worst sentence in its own range:
- F: 652, abstract sentence 5 (F9.1).
- M: 1051 (M9.16).
- R: 1120 (R worst sentence).

**Count: 64 run-on or over-nested sentences** (F 10, M 25, R 29).

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

**9.1 [H] Worst sentence in the range: abstract sentence 5, 652 (ABS).**
> "Noise matched to ORCA's rate at the lone trap, noise matched to its completion of whole runs and a bias matched to it at the pair reproduce the rate, yet free different deadlocks and differ in replay, time-step dependence or handedness: ORCA adds a goal drive, noise drives activated escape over computed barriers."

It is 53 words long. Its defects:
- It has three coordinated subjects, each carrying its own "matched to" phrase.
- "its" and "it" have to be traced back to ORCA across two noun phrases.
- "the rate" is singular but refers to three different rates (snapshot freeing, whole-run completion, pair freeing).
- After the colon, two independent results are comma-spliced.
- The third control, the bias, gets no mechanism after the colon.
- "noise drives" sits next to "goal drive".
- ORCA appears here unexpanded (16.6).

Split:
> "Three controls reproduce the rate of optimal reciprocal collision avoidance (ORCA): noise matched on lone-trap freeing, noise matched on whole-run completion, and a lateral bias matched on pair freeing. Each frees different deadlocks from ORCA and differs from it in replay, time-step dependence or handedness. ORCA adds a goal drive; noise causes activated escape over computed barriers; the bias removes the pair minimum at its fold."

The runner-up is the second sentence of the Fig. 1 caption (822, 94 words), split in 8.1. It is longer, but it sits in a caption, not the abstract.

| # | Line | File | Quoted text (start) | Split |
|---|---|---|---|---|
| 9.2 [H] | 822 S1, S2 | F1C | "The lone-agent trap at a 0.8~m door (top) and the symmetric pair standoff (bottom), each with its rest-state energy along the coordinate drawn in the scene (the blocker's position …" | See 8.1. |
| 9.3 [M] | 835 S1 | INT | "Narrow-exit deadlocks in the SFM fall into two classes: a lone-agent trap set by the wall force at the door edges, with a stuck-alone criterion that holds in …" (about 70 words) | "Narrow-exit deadlocks in the SFM fall into two classes. The first is a lone-agent trap set by the wall force at the door edges, with a stuck-alone criterion that holds in \CriterionAgree\ of \CriterionN\ deadlocks." Follow with the pair sentences of 4.1. |
| 9.4 [M] | 895 S2 | MOD | "At deadlock detection the blocker has at most \TermNbMax\ other agents within $R$ (median \TermNbMedian), $\rho\le\TermRhoMax$\,ped/m$^2$, so its Weidmann factor is at least \TermWeidMin\ in all \TermN\ deadlocks of both modes and $v_{{\rm eff},i}=v_{0,i}$ to within 1\%." | This is a comma splice of four results. "In all \TermN\ deadlocks of both modes, the blocker, the agent nearest the door, has at most \TermNbMax\ other agents within $R$ at deadlock detection (median \TermNbMedian), so $\rho\le\TermRhoMax$\,ped/m$^2$. Its Weidmann factor is then at least \TermWeidMin, and $v_{{\rm eff},i}=v_{0,i}$ to within 1\%." |
| 9.5 [M] | 923 S2 | MOD | "The corrected update is $\mathbf v'=\Pi(\ldots)$, …, where $\Pi$ caps the speed at $2v_0$ and $\boldsymbol\xi$ has independent Gaussian components of standard deviation $\sigma$, either per step ($\sigma$ fixed) or scaled as …; the published update differs as in Table~\ref{tab:params}." | "The corrected update is $\mathbf v'=\Pi(\mathbf v+\mathbf F\Delta t/m)$, $\mathbf v'\leftarrow\Pi(\mathbf v'+\boldsymbol\xi)$, $\mathbf x'=\mathbf x+\mathbf v'\Delta t$, where $\Pi$ caps the speed at $2v_0$. The noise $\boldsymbol\xi$ has independent Gaussian components of standard deviation $\sigma$, either fixed per step or scaled as $\sigma\sqrt{\Delta t/0.01\,{\rm s}}$. The published update differs as in Table~\ref{tab:params}." |
| 9.6 [M] | 906 S2 | MOD | "The published code sums over segments, so a shared end point can act twice; the corrected mode lets only the nearer closest point act when either closest point is the shared end (convex-union rule), which removes …" | "The published-reproduction mode sums over segments, so a shared end point can act twice. The corrected-forward mode applies a convex-union rule: when either closest point is the shared end, only the nearer one acts. This removes the double count outside a convex corner and keeps both walls inside a concave one." |
| 9.7 [M] | 926 S2 | MOD | "A quench restarts a snapshot under one intervention (an arm) for at most 120\,s (deterministic arms stop once all speeds stay below $10^{-3}$\,m/s for 10\,s), so arms are compared snapshot by snapshot." | There are two parentheticals, and the "so" is a non sequitur: the pairing follows from restarting the same snapshots, not from the stopping rule. "A quench restarts a snapshot under one intervention for at most 120\,s; every intervention is run on the same snapshots, so interventions are compared snapshot by snapshot. Deterministic interventions stop once all speeds stay below $10^{-3}$\,m/s for 10\,s." |
| 9.8 [L] | 916 S1 | MOD | "ORCA builds one half-plane of permitted velocities per neighbour (horizon $\tau_h$) and returns the velocity $\mathbf v^{\rm orca}_i$ nearest to $v_{0,i}\hat{\mathbf e}_i$ (note $v_0$, not $v_{\rm eff}$); the model turns it into a force gated off at high density:" | "ORCA builds one half-plane of permitted velocities per neighbour, with horizon $\tau_h$, and returns the velocity $\mathbf v^{\rm orca}_i$ nearest to $v_{0,i}\hat{\mathbf e}_i$, with $v_0$, not $v_{\rm eff}$. The model turns it into a force gated off at high density:" |
| 9.9 [L] | 836 S1 | INT | "At the lone trap ORCA acts as an added goal drive, deterministic and independent of the time step, whereas noise matched to its rate acts thermally; the two differ in …" | "At the lone trap ORCA acts as an added goal drive, deterministic and independent of the time step. Noise matched to its rate acts thermally, and the two differ in which deadlocks they leave unresolved, in replay and in time to free." |
| 9.10 [L] | 926 S4 | MOD | "Further geometries are a bottleneck rebuilt from the CroMa experiments~\cite{fzj_ped20219}, with agent number and corridor length matched run by run (Sect.~\ref{sec:validity}), and open counterflow and crossing scenarios" | It is ambiguous which noun the final "and" joins. "Two further geometries are used: a bottleneck rebuilt from the CroMa experiments~\cite{fzj_ped20219}, with agent number and corridor length matched run by run (Sect.~\ref{sec:validity}), and an open geometry with counterflow and crossing scenarios" |

Checked and kept: 926 S3 ("Proportions carry Wilson 95\% intervals …, paired … McNemar …, and times to freeing are Kaplan--Meier estimates") is a list of methods, not a splice of results. 848 S1 and 842 S4 are long, but each has one main clause (for the modifier problem in 842 S4, see 16.14).

### Block M: §4–§5 (main.tex 927–1071)

Each entry gives the split. Sentences are quoted by their opening words where the full text appears in an earlier entry.

**9.1, 981 [S4] (M).** "Each class predicts a response (Table~\ref{tab:signatures}) to probes of the same frozen state: a quench under the intervention, a replay perturbed by $10^{-9}$\,m, a time-step change with per-step or $\sqrt{\Delta t}$-scaled noise, a constant goal-parallel push of either sign equal to ORCA's rest drive (the frozen-mean arm), reversal of a lateral tilt, and corrected numerics."
Split: "Each class predicts a response (Table~\ref{tab:signatures}) to six probes of the same frozen state. The probes are a quench under the intervention, a replay perturbed by $10^{-9}$\,m, a time-step change with per-step or with $\sqrt{\Delta t}$-scaled noise, a constant goal-parallel push of either sign equal to ORCA's rest drive, reversal of a lateral tilt, and corrected numerics." The parenthesis is deleted per 11.1.

**9.2, 1004 [S4] (M).** "Near rest and away from contact, one velocity component of agent $i$ under the corrected update and the damping of Eq.~\eqref{eq:des} is the autoregressive process $v_{n+1}=a\,v_n+\xi_n$, $a=1-\Delta t/\tau_i$, $\langle\xi_n\xi_{n'}\rangle=\sigma^2\delta_{nn'}$, with stationary variance $\sigma^2/(1-a^2)$."
Split: "Near rest and away from contact, the corrected update with the damping of Eq.~\eqref{eq:des} makes one velocity component of agent $i$ the autoregressive process $v_{n+1}=a\,v_n+\xi_n$, with $a=1-\Delta t/\tau_i$ and $\langle\xi_n\xi_{n'}\rangle=\sigma^2\delta_{nn'}$. Its stationary variance is $\sigma^2/(1-a^2)$."

**9.3, 1017 [S4] (M).** "We compute it with the string method~\cite{e2007} on all mobile coordinates, from the snapshot minimum to an exit state (blocker past the door plane), with all residual agents mobile (full), neighbours pinned (frozen), or the blocker alone (alone)."
Split: "We compute it with the string method~\cite{e2007} on all mobile coordinates, from the snapshot minimum to an exit state with the blocker past the door plane. Three conditions set what is mobile: all residual agents (full), the blocker with its neighbours pinned (frozen), and the blocker alone (alone)."

**9.4, 1017 [S4] (M).** "A barrier is used only if the string has converged (uphill perpendicular force below 5\,N, climbing image stationary at the path maximum, under 1\% change on doubling the images), ends in an exit, and, when alone, matches a direct two-dimensional path."
Split: "A barrier is used only if the string has converged, ends in an exit and, for the alone condition, matches a direct two-dimensional path. Convergence means an uphill perpendicular force below 5\,N, a climbing image stationary at the path maximum, and under 1\% change on doubling the images."

**9.5, 1017 [S4] (M).** "Kramers theory predicts~\cite{kramers1940,hanggi1990}: escape times are exponential (Weibull shape $k=1$)~\cite{weibull1951}; $\ln\lambda$ is linear in $1/k_BT_{\rm eff}$ with slope $-\Delta U$ for the condition's own barrier; and, since the neighbours can move out of the way, the full barrier lies below the alone barrier."
Split: "Kramers theory~\cite{kramers1940,hanggi1990} predicts exponential escape times (Weibull shape $k=1$~\cite{weibull1951}) and $\ln\lambda$ linear in $1/k_BT_{\rm eff}$ with slope $-\Delta U$ for the condition's own barrier. Because the neighbours can move out of the way, the full barrier should also lie below the alone barrier." This also stops attributing the third prediction to Kramers theory; see 16.8.

**9.6, 1026 caption [S5] (H).** Split given in 8.2.

**9.7, 1033 [S5] (M).** "The C1 drive has median … comparable to $g_{\max}$ at the mean radius, so a fraction \EOneBStuckAloneFrac\ of the \StuckAloneN\ spawned agents are stuck alone; adding ORCA's rest drive (median \DriveORCAMedian\,N) lowers it to \StuckAloneFracCThree\ (Fig.~\ref{fig:lone-trap}, right)."
Split: "The C1 drive has median \DriveCOneMedian\,N (5--95\%: \DriveCOneLo--\DriveCOneHi\,N), against $g_{\max}=$\GmaxTwentyFive\,N at $r=0.25$\,m, and \EOneBStuckAloneFrac\ of the \StuckAloneN\ spawned agents are stuck alone. Adding ORCA's rest drive (median \DriveORCAMedian\,N) lowers the fraction to \StuckAloneFracCThree\ (Fig.~\ref{fig:lone-trap}, right)."

**9.8, 1035 [S5] (H).** "In each of the \CriterionN\ deadlocks of both modes we removed every agent except the blocker, the agent nearest the door, and restarted (the keystone test): it stayed held in exactly the cases with positive margin, \CriterionAgree\ of \CriterionN."
Split, combined with the fix in 16.10: "In each of the \CriterionN\ deadlocks of both modes we removed every agent except the blocker and restarted (the keystone test). Whether the blocker stayed held matched the sign of its margin in \CriterionAgree\ of \CriterionN\ cases."

**9.9, 1035 [S5] (M).** "Removing the blocker sorts the corrected-forward deadlocks into three classes: in \KeystoneBLone\ the others then leave (lone keystone); in \KeystoneBSecondTrap\ another agent takes the blocker's place and is held (lone keystone with a second trap); and \KeystoneBCollective\ are collective (published mode: \KeystoneALone, \KeystoneASecondTrap\ and \KeystoneACollective)."
Split: "Removing the blocker sorts the deadlocks into three types. In a lone keystone the others then leave; in a lone keystone with a second trap another agent takes the blocker's place and is held; the rest are collective. The counts are \KeystoneBLone, \KeystoneBSecondTrap\ and \KeystoneBCollective\ in the corrected-forward mode and \KeystoneALone, \KeystoneASecondTrap\ and \KeystoneACollective\ in the published mode." On "types" for "classes", see 16.11.

**9.10, 1035 [S5] (M).** "With the default walls, completion rises from \EsevenWSevenK\ of \EsevenN\ at $w=0.7$\,m and \EsevenWEightK\ at $0.8$\,m to \EsevenWNineK\ at $0.9$\,m (Wilson 95\%: …) and \EsevenWTenK\ at $1.0$\,m (lower bound \EsevenWTenLo); a logistic fit puts the critical width, where half the runs complete, at \EsevenWcrit\,m (bootstrap 95\%: …)."
Split at the semicolon: "…and \EsevenWTenK\ at $1.0$\,m (lower bound \EsevenWTenLo). Half the runs complete at the critical width \EsevenWcrit\,m (logistic fit; bootstrap 95\%: \EsevenWcritLo--\EsevenWcritHi)."

**9.11, 1035 [S5] (L).** "Shortening the range of every wall to $B_w=0.04$\,m lifts completion to \EsevenBallK\ of \EsevenN, and to \EsevenBallTwoK\ at $0.02$\,m; shortening it on the door jambs alone gives \EsevenBjambK\ (against all walls: $p=\EsevenJambVsAllP$; against the default: $p=\EsevenJambVsDefaultP$)."
Split at the semicolon: "…and to \EsevenBallTwoK\ at $0.02$\,m. Shortening it on the door jambs alone gives \EsevenBjambK, which differs from the default ($p=\EsevenJambVsDefaultP$) but not from all walls ($p=\EsevenJambVsAllP$)."

**9.12, 1035 [S5] (H, comma-splice list of results).** "Under the default walls \EsevenDefaultCollective\ of \EsevenDefaultClassified\ deadlocks are collective and the rest are stuck-alone stacks; with jamb-only short range \EsevenBjambCollective\ of \EsevenBjambClassified\ are collective, with all-walls $0.04$\,m \EsevenBallCollective\ of \EsevenBallClassified, and with all-walls $0.02$\,m \EsevenBallTwoCollective\ of \EsevenBallTwoClassified\ ($p=\EsevenCollectiveP$ for jamb-only against default): the short-range law removes the lone traps and leaves the pair standoffs of Sect.~\ref{sec:pair}."
Split: "Under the default walls \EsevenDefaultCollective\ of \EsevenDefaultClassified\ deadlocks are collective and the rest are stuck-alone stacks. Under the short-range laws nearly all are collective: \EsevenBjambCollective\ of \EsevenBjambClassified\ (jambs only), \EsevenBallCollective\ of \EsevenBallClassified\ (all walls, 0.04\,m) and \EsevenBallTwoCollective\ of \EsevenBallTwoClassified\ (all walls, 0.02\,m); $p=\EsevenCollectiveP$ for jambs only against default. The short-range law removes the lone traps and leaves the pair standoffs of Sect.~\ref{sec:pair}."

**9.13, 1047 [S5] (M).** "Two agents stand in front of the two jamb faces, one on each side of the door axis, at \PairAxisMin--\PairAxisMax\,m from it and with a surface gap of \PairGapMin--\PairGapMax\,m between them; neither touches the other or a wall."
Split: "Two agents stand in front of the two jamb faces, one on each side of the door axis and \PairAxisMin--\PairAxisMax\,m from it. Their surface gap is \PairGapMin--\PairGapMax\,m, and neither touches the other or a wall."

**9.14, 1049 [S5] (M).** "The softest eigenvalue, $\lambda_1=$…\,N/m (median \PairLamOneMed), belongs in all \PairSoftCommon\ to the common lateral shift, both members moving sideways together, and the next one, the opposed lateral mode, is stiffer by a factor of …"
Split: "The softest eigenvalue, $\lambda_1=\PairLamOneMin$--\PairLamOneMax\,N/m (median \PairLamOneMed\,N/m), belongs in all \PairSoftCommon\ snapshots to the common lateral shift, in which both members move sideways together. The next, the opposed lateral mode, is stiffer by a factor of \PairLamRatioMin--\PairLamRatioMax."

**9.15, 1049 [S5] (M).** "Proposition~\ref{prop:rest} then predicts that the standoff survives every small displacement, and it does: …"
Split: "Proposition~\ref{prop:rest} predicts that the standoff survives every small displacement." Then give the replacement of 1.11 as its own sentence. The device "and it does:" is deleted.

**9.16, 1051 [S5] (H, worst sentence).** Quoted in §0.
Split: "We located the fold by overdamped relaxation of the rest field under bias, bisecting in $b$ for each snapshot and each sign. For the sign with the lower threshold, $b^\ast$ lies between \PairBstarMin\ and \PairBstarMax\ (median \PairBstarMed). The two signs differ because no standoff is exactly symmetric: the difference follows the members' unequal distances from the axis (rank correlation \PairAsymCorr)."

**9.17, 1051 [S5] (M).** "The static prediction (freed if $|b|$ exceeds the snapshot's fold, held otherwise) agrees with the 120\,s quench in \PairFoldAgree\ of \PairFoldN\ (snapshot, $b$) cases for the eight bias values $|b|\le0.1$ (Wilson lower bound \PairFoldLo); all … disagreements are quenches that escape … where the members' inertia carries them over."
Split: "The static prediction is that a standoff is freed if $|b|$ exceeds its fold and held otherwise. Over eight bias values $|b|\le0.1$ it agrees with the 120\,s quench in \PairFoldAgree\ of \PairFoldN\ (snapshot, $b$) cases (Wilson lower bound \PairFoldLo)." Then add the two sentences of 4.4.

**9.18, 1053 [S5] (M).** "The string method of Sect.~\ref{sec:escape}, run on \PairBarN\ snapshots spread over $\lambda_1$, gives gated pair barriers of …, far below the lone-trap barriers, and $\lambda_1$ does not predict them (rank correlation $\PairBarSpearman$)."
Split: "On \PairBarN\ snapshots spread over $\lambda_1$, the string method of Sect.~4.3 gives pair barriers of \PairBarMin--\PairBarMax\,J (median \PairBarMed\,J), against 16--45\,J for the lone traps. $\lambda_1$ does not predict them (rank correlation $\PairBarSpearman$)."

**9.19, 1053 [S5] (M).** "Here $\Delta U/k_BT_{\rm eff}$ is below 1 at every noise level we ran for most snapshots, so the Arrhenius test of Sect.~\ref{sec:escape} has no lever arm, and the escape times are not exponential (…): once kicked off …"
Split: "For [k] of \PairBarN\ snapshots $\Delta U/k_BT_{\rm eff}$ is below 1 at every noise level, so the Arrhenius test of Sect.~\ref{sec:escape} has no lever arm. The escape times are not exponential (pooled Weibull shape \PairWeibLow\ at $\sigma=0.01$ and \PairWeibHigh\ at $0.05$\,m/s)." Then the sentence of 4.5.

**9.20, 1056 [S5] (M).** "To see whether contact arches form at all, we drove the bottleneck hard: corrected-forward C1, $w=0.8$\,m, 100 agents with mean desired speed \ArchVZero\,m/s, \ArchN\ runs of up to 600\,s, searching every 0.1\,s for a chain of agents in mutual contact that touches both jambs."
Split: "To see whether contact arches form at all, we ran \ArchN\ corrected-forward C1 runs of up to 600\,s at high drive: $w=0.8$\,m and 100 agents with mean desired speed \ArchVZero\,m/s. Every 0.1\,s we searched for a chain of agents in mutual contact that touches both jambs."

**9.21, 1056 [S5] (M).** "Such chains form in \ArchRunsWithArch\ of \ArchN\ runs (\ArchEpisodes\ episodes, \ArchEpisodesThree\ with three or more agents, up to \ArchSizeMax) and carry up to \ArchPeakForce\,kN of body compression, yet they break within \ArchMaxLife\,s (95\% within \ArchPNinetyFive\,s). None lasts 10\,s (…), and every run completes (…)."
Split and merge: "Such chains form in \ArchRunsWithArch\ of \ArchN\ runs, in \ArchEpisodes\ episodes (\ArchEpisodesThree\ with three or more agents, at most \ArchSizeMax\ agents), and carry up to \ArchPeakForce\,kN of body compression. Every chain breaks within \ArchMaxLife\,s (95\% within \ArchPNinetyFive\,s), so no run holds an arch for 10\,s (upper Wilson bound \ArchPersistentHi), and every run completes (\ArchComplete\ of \ArchN)."

**9.22, 1065 [S5] (L).** "To test whether noise frees the lone trap thermally, we took \EfourN\ corrected-forward snapshots with at least two residual agents, spread over the collective barrier, and computed the barrier in each of the three conditions of Sect.~\ref{sec:signatures}."
Split: "To test whether noise frees the lone trap thermally, we took \EfourN\ corrected-forward snapshots with at least two residual agents, chosen to span the range of collective barriers. For each we computed the barrier in the three conditions of Sect.~4.3."

**9.23, 1065 [S5] (L).** Split given in 4.8.

**9.24, 1067 [S5] (H).** "The fitted slope of $\ln\lambda$ against $1/k_BT_{\rm eff}$, divided by $-\Delta U$ of the same condition, has median \EfourRatioFull\ (full), \EfourRatioFrozen\ (frozen) and \EfourRatioAlone\ (alone), and its confidence interval covers 1 in \EfourCoverFull\ of \EfourFitsFull, \EfourCoverFrozen\ of \EfourFitsFrozen\ and \EfourCoverAlone\ of \EfourFitsAlone\ fits; the three exceptions have ratios \EfourNonCoverA\ (one full condition), \EfourNonCoverB\ and \EfourNonCoverC\ (the frozen and alone conditions of one snapshot)."
Split: "Divide the fitted slope of $\ln\lambda$ against $1/k_BT_{\rm eff}$ by $-\Delta U$ of the same condition. The ratio has median \EfourRatioFull\ (full), \EfourRatioFrozen\ (frozen) and \EfourRatioAlone\ (alone), and its 95\% interval covers 1 in \EfourCoverFull\ of \EfourFitsFull, \EfourCoverFrozen\ of \EfourFitsFrozen\ and \EfourCoverAlone\ of \EfourFitsAlone\ fits. The three exceptions are one full condition (\EfourNonCoverA) and the frozen and alone conditions of one snapshot (\EfourNonCoverB, \EfourNonCoverC)."

**9.25, 1067 [S5] (M, comma splice of two unrelated results).** "The pooled Weibull shape of the escape times is …, close to the exponential value 1, and the median attempt rates are \EfourNuFull\,s$^{-1}$ (full) and \EfourNuAlone\,s$^{-1}$ (alone)."
Split: the first sentence per 5.1, then "The median attempt rates are \EfourNuFull\,s$^{-1}$ (full) and \EfourNuAlone\,s$^{-1}$ (alone)."

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

| # | Line, file | Sev | Sentence (opening words) | Defect | Split |
|---|---|---|---|---|---|
| 9.1 | 1111 [06] | L | "At the lone keystone C3 RVO2 frees … and ORCA's drive alone the same ones (discordant …; … against the published solver); the constraint part alone frees \EtwoLKConstrRVOFreed." | Gapping, plus a semicolon inside a parenthesis inside a semicolon sentence. | "At the lone keystone C3 RVO2 frees 30 of 34 blockers, and ORCA's drive alone frees the same 30 (discordant 0:0, and 0:0 against the published solver). The constraint part alone frees none." |
| 9.2 | 1111 [06] | M | "$10^{-9}$\,m replays reproduce C3 RVO2 exactly (…), and it fails where the rest-state margin … (ROC area …)." | Two unrelated findings joined by a comma. "It" is ambiguous (replays or C3 RVO2). The sentence opens with a numeral. | "Replays perturbed by $10^{-9}$\,m reproduce C3 RVO2 exactly (largest first-exit shift 0.000\,s in 300). C3 RVO2 fails where the rest-state margin with ORCA's drive added stays positive (ROC area 0.98)." |
| 9.3 | 1114 [06] | M | "Identity is compared throughout by the Jaccard index $J$ of the minority outcome sets: the unresolved snapshots or runs where most are freed, and the freed standoffs at the pair, where fewer than half are." | Two nested "where" clauses with elided verbs. It took two readings to recover. | "We compare which deadlocks two arms free by the Jaccard index $J$ of their minority outcome sets. Where most snapshots or runs are freed, these are the unresolved ones; at the pair, where fewer than half are freed, they are the freed standoffs." |
| 9.4 | 1114 [06] | M | "Per-step noise … matches that rate and nothing else (…): it leaves …, its seeds disagree (…), and it waits." | Three findings in a comma list after a colon. | See 1.1. |
| 9.5 | 1117 [06] | M | "On \EthreeN\ snapshots spread over …, with noise set so that … (Fig.~\ref{fig:dt}), per-step noise gives $\ell=$ … (predicted …) and … (predicted …, outside the interval); the slope … is …" | About 70 words, four bracketed or parenthetical groups, and a semicolon list. | "On 20 snapshots chosen to span the range of collective barriers, noise was set so that $\beta_{\rm ref}=\Delta U/k_BT_{\rm eff}$ at $\Delta t=0.01$\,s is 1.5 or 2.5 (Fig.~\ref{fig:dt}). Per-step noise then gives $\ell=2.16$ [1.80, 2.70] (predicted 2.22) and 3.23 [2.96, 3.52] (predicted 3.70); the second prediction lies outside its interval. The slope of observed on predicted $\ell$ through the origin is 0.91 [0.83, 1.01]." |
| 9.6 | 1120 [06] | M | "The constraint part from its half-plane, negligible at restart, builds up once the agents move; in held runs … (down to …) and cancels on average … of the drive, as in held pair standoffs (…)." | Mid-sentence appositive, a semicolon, a nested parenthesis and a trailing comparison. | "The constraint part from the neighbour's half-plane builds up once the agents move. In held runs its door-ward component averages $-49$\,N (down to $-138$\,N) and cancels on average 0.27 of the drive, as in held pair standoffs (0.26)." |
| 9.7 | 1120 [06] | M | "With one such neighbour C3 RVO2 frees … (its drive …), with two or more … (Fisher $p=$ …), and where both free it is slower than its drive in … (median delay …)." | Three findings comma-joined, with gapping. | "With one such neighbour C3 RVO2 frees 2 of 10 blockers, against 9 for its drive; with two or more it frees 15 of 16 (Fisher $p=2.3\times10^{-4}$). Where both free, full ORCA is slower than its drive in 17 of 17 snapshots (median delay 0.25\,s)." |
| 9.8 | 1120 [06] | H | "Only the published linear program changes outcome …, which a replay this small reveals as … and base forward claims on RVO2." | **The worst sentence in the range.** | Split given at the top. |
| 9.9 | 1123 [06] | H | "The final states differ in class (…): C3 RVO2's … failures at rest are all lone keystones and … of its … still moving at 600\,s hold a second trap, whereas noise failures never come to rest (classes \EsixNoiseLone/\EsixNoiseSecond/\EsixNoiseCollective, lone/second trap/collective)." | Slash-encoded counts. As written, failures that "never come to rest" are classed as lone keystones, with no word on how (the classes come from surgery on final states, C47). | "The final states differ in class ($p=1.4\times10^{-3}$). C3 RVO2's 31 failures at rest are all lone keystones, and 51 of its 54 failures still moving at 600\,s hold a second trap. Noise failures never come to rest; removing the blocker from their final states classes 56 as lone keystones, 31 as second traps and none as collective." |
| 9.10 | 1123 [06] | M | "The \EsixStalls\ noise stalls (…) have Weibull shape …, a mixture over barriers, and their survival lies within … of the no-fit prediction from the … gated library barriers, $k_BT_{\rm eff}(\sigma^\ast)$ and the measured attempt rate (median … observed, … predicted)." | Five comma segments, two parentheses, and an appositive that attaches to the wrong noun (4.3). | "The 349 noise stalls (at least 10\,s without an exit) have Weibull shape 0.64 [0.58, 0.70], below 1 because they mix escapes over different barriers. Their survival lies within 0.05 of a prediction with no fitted parameter, built from the 56 lone-trap barriers that pass the checks of Sect.~\ref{sec:escape}, $k_BT_{\rm eff}(\sigma^\ast)$ and the measured attempt rate (median 59\,s observed, 69\,s predicted)." |
| 9.11 | 1133 [06] | L | "Unlike at the lone trap the constraint part alone acts (…; drive alone …), and the parts oppose each other: full RVO2 ORCA frees fewer than its drive (…)." | Two results joined by a comma; the introductory phrase lacks its comma. | "Unlike at the lone trap, the constraint part alone frees standoffs (45 published, 44 RVO2; drive alone 33). The parts oppose each other: full RVO2 ORCA frees fewer than its drive (28:2, $p=8.7\times10^{-7}$)." |
| 9.12 | 1136 [06] | M | "They free different standoffs: \PairBsPubBoth\ of the \PairBsPubEither\ freed by the published solver or its match (Jaccard …), and none of the … freed by RVO2 or its match." | Says "different", then gives the shared count (13). Each clause must be inverted mentally to read it. | "The published solver and its match share 13 of the 30 standoffs either frees (Jaccard 0.43 [0.26, 0.61]); RVO2 and its match share none of 15." |
| 9.13 | 1136 [06] | M | "The bias has a handedness and ORCA none (Table~\ref{tab:matched}); at $-b^\ast_{\rm pub}$ the other member exits first …, on largely different standoffs (…)." | Gapping, a semicolon and a trailing appositive. | "The bias has a handedness and ORCA has none (Table~\ref{tab:matched}). At $-b^\ast_{\rm pub}$ the upper member exits first in 21 of 21, and only 8 standoffs are freed at both signs (discordant 13:14)." |
| 9.14 | 1151 [07] | L | "We built their geometry: …, the entrance, and corridor walls of the run's length, with the number of agents and the corridor length matched run by run (five model runs per human run and variant, 25 per variant)." | A list, then a "with" absolute, then a two-item parenthetical. | "We built their geometry: a walled holding area of $7.8\times8.6$\,m, the entrance, and corridor walls of the run's length. Agent number and corridor length are matched run by run, with five model runs per human run and variant (25 per variant)." |
| 9.15 | 1151 [07] | H | "Model and human trajectories went through the same estimator: passages … give the flow (…) and the time gaps …, and in the waiting zone, 0.3--2.5\,m in front of the entrance, the velocity fluctuation is … (Savitzky--Golay, 1.48\,s) relative to … within 0.74\,m, at local mean speed below 0.3\,m/s." | About 75 words, seven comma-separated segments and two parentheses. It defines three estimators in one sentence. **Second in line for worst sentence.** | "Model and human trajectories went through the same estimator. Passages through the entrance plane give the flow (first to last passage, or to the deadlock where there is one) and the time gaps between successive passages. In the waiting zone, 0.3--2.5\,m in front of the entrance, the velocity fluctuation is the standard deviation of each agent's smoothed velocity (Savitzky--Golay, 1.48\,s) relative to the mean of its neighbours within 0.74\,m, taken where the local mean speed is below 0.3\,m/s." |
| 9.16 | 1154 [07] | H | "The flow is … (runs …), … with the long corridor and … with the short one; the longest gap between passages averages … and never exceeds \EtenHumanGapMax\,s, and a run has on average \EtenHumanGapsTwo\ gaps longer than 2\,s." | A comma-spliced list of results that contradicts itself as printed: the longest gap "never exceeds 2.0 s", yet runs average 0.2 gaps "longer than 2 s". The maximum is 2.04 s (data/derived/E10_analysis.json, humans.longest_gap_max), rounded to 2.0. | "The flow is 1.48 [1.22, 1.74]\,ped/s (runs 1.15--1.71): 1.32 with the long corridor and 1.58 with the short one. The longest gap between passages averages 1.7\,s and is at most 2.04\,s, the only gap longer than 2\,s in the five runs." |
| 9.17 | 1157 [07] | M | "C1 deadlocks in … of 25 runs in the published mode and in … in the corrected-forward mode (completion \EtenCPubComplete\ and \EtenCOneComplete, upper Wilson bound \EtenCPubCompleteHi, against \EtenHumanN\ of \EtenHumanN\ human runs)." | A three-item parenthetical that mixes counts ("0 and 1") with a proportion (0.13) without saying which mode the bound belongs to. | "C1 deadlocks in 25 of 25 runs in the published mode and in 24 of 25 in the corrected-forward mode, against none of the 5 human runs (published-mode completion 0 of 25, upper Wilson bound 0.13)." |
| 9.18 | 1157 [07] | L | "C3 RVO2 never deadlocks but completes only …, the other … still moving at the cap, and C1 $+\,\sigma^\ast$ completes …" | Two findings joined by a comma. | See 4.8. |
| 9.19 | 1157 [07] | M | "Whatever the variant, the flow, counted up to the deadlock where there is one, is … of the human flow: … for corrected-forward C1 (ratio …) and … for C3 RVO2 (ratio …)." | Fronted clause, mid-sentence qualification, and four bracketed groups. | "For every variant the flow is 0.40--0.59 of the human flow: 0.75 [0.73, 0.77]\,ped/s for corrected-forward C1 (ratio 0.51 [0.46, 0.58]) and 0.87 [0.84, 0.89]\,ped/s for C3 RVO2 (ratio 0.59 [0.53, 0.67])." (The counting rule moves to 1151, per 4.9.) |
| 9.20 | 1157 [07] | L | "Passages come in bursts separated by long gaps: … gaps longer than 2\,s per run against …, and a mean longest gap of … for the deterministic variants and … with noise, against … (Fig.~\ref{fig:croma})." | Two comparisons comma-joined after a colon. | "Passages come in bursts separated by long gaps. A model run has 11--19 gaps longer than 2\,s, against 0.2 for humans, and a mean longest gap of 5.7--6.8\,s for the deterministic variants and 72.2\,s with noise, against 1.7\,s (Fig.~\ref{fig:croma})." |
| 9.21 | 1157 [07] | L | "The deficit does not depend on the corridor: with the long one humans reach … and the model variants …, with the short one … and …" | Gapping, which drops both verb and unit in the second half. | "The deficit does not depend on the corridor: with the long corridor humans reach 1.32\,ped/s and the model variants 0.54--0.81\,ped/s; with the short one, 1.58 and 0.62--0.91\,ped/s." |
| 9.22 | 1160 [07] | M | "Third, removing deadlocks is not calibrating capacity: the reduced jamb range lets … complete but leaves …, and matched noise, which reproduces ORCA's completion in the room, turns deadlocks into stalls with …" | A negation lead, then two findings, with a relative clause inside the second. | "Third, a model that no longer deadlocks can still be far from human capacity. The reduced jamb range lets 17 of 25 runs complete but leaves the flow at 0.57 of the human value, and matched noise, which reproduces ORCA's completion in the room, turns deadlocks into stalls with a mean longest gap of 72.2\,s." |
| 9.23 | 1163 [08] | L | "Noise at $\sigma=0.07$\,m/s frees … ($\Delta=$ …), noise at $\sigma^\ast$ completes … at its rate ($\Delta=$ …), and a bias at $b^\ast$ frees …" | Three results in a comma list. | See 3.7 (replace with a pointer to Table 3). |
| 9.24 | 1163 [08] | M | "The minority outcome sets overlap little (…; …, against …; …), and each control fails a probe of its own class: …" | A parenthetical with three semicolon groups, then a second claim. | See 3.7. |
| 9.25 | 1169 [08] | M | "The published linear program and RVO2 free … and … of … pair standoffs, and only the published program changes outcome under … replays (…); results should name a validated solver." | Two findings and a recommendation in one sentence. | "The published linear program and RVO2 free 21 and 7 of 46 pair standoffs, and only the published program changes outcome under $10^{-9}$\,m replays (5 of 300 lone-trap snapshots). Results should name the solver and show that its outcomes survive such replays." |
| 9.26 | 1179 [10] | L | "New in this version are the five mechanism classes …; the deadlock physics (the stuck-alone criterion …, the pair standoff and its fold, the absence of persistent contact arches, the exact effective temperature of per-step noise and collective activated escape over computed barriers); attribution on …; a corrected-forward model mode …; and a like-for-like comparison …" | About 90 words with a five-item parenthetical inside a semicolon list. The missing comma makes the parenthetical read "the exact effective temperature of per-step noise and [of] collective activated escape". | "New in this version are the five mechanism classes with their physical signatures and the rest-state lemma, and the deadlock physics: the stuck-alone criterion at the door edges, the pair standoff and its fold, the absence of persistent contact arches, the exact effective temperature of per-step noise, and collective activated escape over computed barriers. Also new are attribution on a common library of frozen deadlocks with paired statistics, with ORCA reported for the published solver and for RVO2; a corrected-forward model mode beside the published one; and a like-for-like comparison with human bottleneck data at 0.8\,m." |
| 9.27 | 1177 [09] | M | "Narrow-exit deadlocks in the model come in two classes, a lone agent held … and a symmetric pair standoff that is …, and contact arches do not persist." | An appositive list, then an unrelated third clause. | "Narrow-exit deadlocks in the model come in two classes: a lone agent held by the wall force at the door edges, and a symmetric pair standoff that is a strict minimum of the rest-state energy. Contact arches do not persist." |
| 9.28 | 1177 [09] | H | "Controls matched to ORCA's rate, noise at the lone trap and in whole runs and a lateral bias at the pair, reproduce the rate but free other deadlocks and differ from ORCA in replay, time-step dependence or handedness: ORCA reshapes the landscape with its rest drive at the lone trap and acts through its constraint part, solver by solver, at the pair." | About 60 words. An appositive with an internal "and" separates the subject from its verb, and a colon clause follows with its own parenthetical. **Third in line for worst sentence.** | "Controls matched to ORCA's rate (noise at the lone trap and in whole runs, a lateral bias at the pair) reproduce the rate but free other deadlocks, and they differ from ORCA in replay, time-step dependence or handedness. ORCA removes the fixed point with its rest drive at the lone trap; at the pair it acts through its constraint part, differently for each solver." |
| 9.29 | 1177 [09] | M | "Rebuilt like for like around a human bottleneck experiment, no model variant flows like people: …" | Dangling modifier. | See 4.11. |


---

## 10. Aphoristic paragraph endings

### 10.0 Paper-wide reconciliation

**Paper-wide count: 15 aphoristic endings.** That is five times the tolerable two or three.
- Block F, 4: 826, 828, 830, 851.
- Block M, 5: 1020, 1035, 1037, 1056, 1071.
- Block R, 6: 1114, 1117, 1136, 1160, 1166, 1177.

**The one that earns its place is 1136**, "Matched on rate, the bias shares ORCA's number, not its mechanism." It closes the paper's cleanest single demonstration, and every word is backed by the paragraph above it.

**Conflict resolved.** Each block nominated a different keeper:
- F kept 830 within its range and nominated 1177 paper-wide. 830 is kept as an ordinary sentence carrying the thesis's reason (F1.4), not as an ending. 1177 is converted (R1.13), because the paper should not end on the negated formula it has already used five times.
- M kept 1020. 1020 stays because it is the protocol's decision rule ("one disagreement separates them"), which a reader applies, but it should not be counted as rhetoric.

Convert all the others as listed in the blocks.

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

There are four in the range:
- 826 "…and that includes the reasons the model gives for what it does at a bottleneck."
- 828 "That statement is about mechanism, and a completion rate cannot support it on its own."
- 830 "…two physical processes can produce the same completion rate, and one number cannot separate them."
- 851 "…the question of which one a given resolver resembles is the same question in both fields."

Paper-wide, five more continue the voice: 1020 "one disagreement separates them.", 1117 "ORCA is not thermal.", 1136 "Matched on rate, the bias shares ORCA's number, not its mechanism.", 1162 "The rate is a calibration target, not a test of mechanism." and 1177 "A mechanism claim needs a test where the mechanism acts, not a second number that matches the first." That makes nine in total, three times the tolerable number.

The one that earns its place paper-wide is 1177, the last sentence of the paper. Within this range, keep 830, because it carries the reason the thesis needs. Convert the rest:

| # | Line | File | Replacement |
|---|---|---|---|
| 10.1 [M] | 826 | INT | "Simulations used to plan for such places are only as trustworthy as the steering model that moves each agent, including the mechanism credited for the model's behaviour at a bottleneck." (A model "gives" no reasons; the metaphor does not survive.) |
| 10.2 [M] | 828 | INT | Same replacement as 1.2. |
| 10.3 [L] | 851 | BKG | "The controls we test, noise and a lateral bias, are perturbations of this kind." Delete the second clause: the parallel between the fields is already drawn by the half-plane sentence (4.6). |

### Block M: §4–§5 (main.tex 927–1071)

There are five in range, above the two-to-three threshold.

| # | Line / file | Quoted text | Verdict and replacement |
|---|---|---|---|
| 10.1 | 1020 [S4] | "Target and control share a mechanism only if they agree on every probe; one disagreement separates them." | **Keep.** It is the operational form of the title. It is the one ending in range that earns its place. |
| 10.2 | 1035 [S5] | "the walls away from the door add nothing." | Convert per 1.9. |
| 10.3 | 1037 [S5] | "We report this rule descriptively; the mechanism is the chain of stuck-alone agents, and the deadlock forms when the push behind the last of them runs out." | "This predictor is descriptive. The deadlock forms when no agent remains behind the last stuck-alone arrival to push it through." See also 11.6. |
| 10.4 | 1056 [S5] | "The model's persistent deadlocks are therefore not contact arches but the contact-free rest states …" | Convert per 1.3. |
| 10.5 | 1071 [S5] | "The two modes need the same noise." | "The two intervals overlap almost entirely." Alternatively, delete it: the two intervals in the preceding sentence already show it, and "the same" claims an equivalence that was not tested. |

Short topic-sentence openers ("The criterion is exact at the rest state.", "The jamb law decides whether the trap exists at $w=0.8$\,m.", "The minimum is shallow.") are claims followed by evidence, not endings. They are kept.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

There are six in the range. Above two or three per paper they set a voice that reads as overclaiming, and the earlier sections add their own.

| # | Line, file | Closing sentence | Action |
|---|---|---|---|
| 10.1 | 1114 [06] | "…: nothing is symmetric to break." | Convert (1.2). |
| 10.2 | 1117 [06] | "ORCA is not thermal." | Delete (1.3). |
| 10.3 | 1136 [06] | "Matched on rate, the bias shares ORCA's number, not its mechanism." | **Keep: this is the one that earns its place.** It closes the paper's cleanest single demonstration (rate matched, overlap 0 and 0.43, handedness 22/22 against 11/21), and every word is backed by the paragraph above it. |
| 10.4 | 1160 [07] | "A narrow-door model should be checked against the flow and gap statistics of matched experiments, not against completion alone." | Convert (1.7). |
| 10.5 | 1166 [08] | "The rate is a calibration target, not a test of mechanism." | Delete (1.9). |
| 10.6 | 1177 [09] | "A mechanism claim needs a test where the mechanism acts, not a second number that matches the first." | Convert (1.13). |

Not counted: 1111 "This is class L: a deterministic drive that removes the fixed point." (a classification, not a gnome); 1133 "Every deterministic arm keeps its outcome in all \PairReplayN\ replays." (a result); 1172 (an operational recommendation); 1175 (scope of a limitation).


---

## 11. Process-record and internal-code leakage

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

| # | Line | File | Quoted text | Replacement |
|---|---|---|---|---|
| 11.1 [M] | 857 | MOD | "Values are read from the code and listed in \texttt{data/params/model.yaml}." | Delete (8.2). |
| 11.2 [M] | 857 | MOD | "the two declared modes" | "the published-reproduction and corrected-forward modes". "Declared" is pre-registration vocabulary, contrary to plan C6. |
| 11.3 [M] | 923 | MOD | "which is why the forward claims use a corrected update" and "every forward claim uses the corrected-forward mode" | "all new results". "Forward claim" is a project label the reader is never given. The mode name "corrected-forward" carries the same word in 11 places, plus 3 instances of "corrected mode". Renaming the mode is a global change: [TASTE], authors' call. |
| 11.4 [M] | 926 | MOD | "(an arm)", "deterministic arms stop", "so arms are compared", "paired arms are compared" | "Arm" is clinical-trial vocabulary (plan C6). Replace with "intervention": delete "(an arm)", and write "deterministic interventions stop", "so interventions are compared", "paired interventions are compared". Out-of-range instances for the other auditor: 981 ("the frozen-mean arm"), 1053, 1083 ("for the arms that free"), 1133 ("Every deterministic arm") and the Table 3 header "Arm" (1092). The changelog itself uses "arm" (C30), so the authors may consider it settled; it is flagged here as a conflict with C6. |
| 11.5 [M] | 854 | BKG | "predicted from the physics of each mechanism class before they are measured." | "predicted from the physics of each mechanism class." "Before they are measured" is a pre-registration assertion the reader cannot verify. The out-of-range partner is 1160, "derived from the physics before the runs". |
| 11.6 [M] | 652 S3 | ABS | "on held-out signatures measured on a library of frozen deadlock states" | "on signatures, not used in the calibration, measured on a library of frozen deadlock states". "Held-out" is machine-learning and validation vocabulary. Out-of-range partners: 1136 "ran it held out at $\pm b^\ast$" and 1160 "held-out signatures". |
| 11.7 [L] | 906, 839 | MOD, INT | "The published code sums over segments"; "the model as the code implements it" | "The published-reproduction mode sums over segments". For 839, see 3.1 (delete). |
| 11.8 [L] | 863 | MOD | "calibrated values of the conference paper are not applied" | This reference cannot be pinned down: the reader does not know which values. Name them, e.g. "the conference paper's FZJ-calibrated values of $\gamma$ and $\rho_{\max}$ are not used" (the authors should confirm which parameters were calibrated). |
| 11.9 [L] | 870 | MOD | "$\mathrm{d}t=0.01$ s" | "$\Delta t=0.01$ s". "dt" is the code variable; the text uses $\Delta t$ (923, 1004). |

Checked and kept: C1–C4 are defined at 887 on the same page as their first use in Table 1. The `\pending` at 926 names run IDs E8/E9; it is a known gap, but the final text must not carry the IDs.

### Block M: §4–§5 (main.tex 927–1071)

| # | Line / file | Quoted text | Replacement | Sev |
|---|---|---|---|---|
| 11.1 | 981 [S4] | "equal to ORCA's rest drive (the frozen-mean arm)," | Delete "(the frozen-mean arm)". It is an internal arm name used nowhere else in the paper. | M |
| 11.2 | 1069 [S5] | "is below the resolution of the gate" and "the gate accepts a full barrier of …" | "is below the resolution of the barrier computation" and "the barrier passes the checks of Sect.~4.3, at \EfourSeedOneSeventyDU\,J,". "Gate" is undefined in this sense and collides with the crush-term gate of §3 (line 920). | H |
| 11.3 | 1053 [S5] | "gated pair barriers" | "pair barriers" (the checks of §4.3 apply to every barrier). The same word appears at 1123, outside range. | M |
| 11.4 | 1008 [S4] | "is \TthreeRatioMean\ in dedicated runs (median \TthreeCellsMedian\ over the \TthreeCells\ noise cells of the escape experiments)." | "is \TthreeRatioMean\ on average over nine runs on deadlock snapshots at three time steps (median \TthreeCellsMedian\ over the \TthreeCells\ noise settings of the escape experiments)." `data/derived/T3_variance.json` has 9 rows. "Dedicated runs" cannot be identified by a reader, and "cells" is internal jargon. | M |
| 11.5 | 1035 [S5] and 1042 caption | "\EsevenN\ runs per cell" and "all runs of the cell" | "\EsevenN\ runs per setting" and "all runs of a setting". | L |
| 11.6 | 1037 [S5] | "We report this rule descriptively;" | No rule has been stated: the paper gives a predictor and an AUC. The k = 3 end-of-queue rule is internal (CHANGELOG C16b). Write "This predictor is descriptive." | M |
| 11.7 | 1001 [S4] | "in the code $\max|\mathbf F_0+\nabla U|\le$…" | "for the implemented force, $\max|\mathbf F_0+\nabla U|\le$…" | L |
| 11.8 | 1001 [S4] | "over the \ResidBarN\ barrier and $\ResidPairMax$\,N over the \ResidPairN\ pair snapshots" | The reader cannot identify the 60 "barrier" snapshots: §5.4 uses 10, and §6 (1123) 56 library barriers. Write "over the \ResidBarN\ snapshots whose barriers we computed (Sects.~\ref{sec:escape} and~\ref{sec:attribution}) and …". Confirm the set before writing. | M |
| 11.9 | 1035 [S5] | "(Fig.~\ref{fig:width}; \EsevenN\ runs per cell, seeds 42--141, 600\,s)" | [TASTE] Move the seed range to the data and code availability statement and keep "\EsevenN\ runs per setting, 600\,s". The competing convention keeps seeds in the text for reproducibility, which is permitted. | L |

No narrated belief revision, pre-registration phrasing or confessional aside appears in range, apart from the trace of the superseded reading in 1.7.

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

| # | Line, file | Sev | Text | Fix |
|---|---|---|---|---|
| 11.1 | 1087 [T3] | H | "with its Arrhenius prediction (E3)" | Delete "(E3)". The code is defined nowhere in the paper. |
| 11.2 | 1094 [T3] | H | "Lone-trap snapshots (E2): \EtwoNLK{} lone keystones, 120\,s" | "Lone-trap snapshots: 34 lone keystones, 120\,s" |
| 11.3 | 1098 [T3] | H | "Whole runs (E6): \EsixN{} seeds, 600\,s" | "Whole runs: 186 seeds, 600\,s" |
| 11.4 | 1102 [T3] | H | "Pair standoffs (E7b): \PairN{} snapshots, 120\,s" | "Pair standoffs: 46 snapshots, 120\,s" |
| 11.5 | 1163 [08] | H | "The held-out signatures, derived from the physics before the runs," | This is a pre-registration claim phrased as narrative, which C6 bars. Replace with "The signatures of Sect.~\ref{sec:signatures}, derived from the model's rest-state physics," (merged into 1.8). |
| 11.6 | 1136 [06] | M | "and ran it held out at $\pm b^\ast$." "Held out" is train/test or trial vocabulary (C6). In this sentence it is also unclear what was held out. | "and quenched the pair library under $+b^\ast$ and $-b^\ast$." (C44 uses "held-out" internally; this changes only the paper's wording.) |
| 11.7 | 1151 [07] | M | "and are stated rather than fixed" | Delete. It is a confessional aside about process (1.5). |
| 11.8 | 1120 [06] | M | "and base forward claims on RVO2" "Forward claims" is project-log language (C20: "Forward claims use RVO2"). §6.2 then reports both solvers anyway. | "and we take RVO2 as the reference ORCA implementation" (inside the split at the top). |
| 11.9 | 1123 [06] | L | "the \EsixBarrierN\ gated library barriers" "Gated" refers to the barrier validity gate (line 1069, "the gate"), while §3 uses "gate" for the density gate on forces (lines 867, 868, 920). "Library" is internal shorthand. | "the 56 lone-trap barriers that pass the checks of Sect.~\ref{sec:escape}" |
| 11.10 | 1123 [06] | L | "the no-fit prediction" | "a prediction with no fitted parameter" |
| 11.11 | 1133 [06] | L [TASTE] | "Every deterministic arm keeps its outcome …" (also 1083 "for the arms that free"). "Arm" is clinical-trial vocabulary under C6, but the authors define it at line 926 ("under one intervention (an arm)"). | Keep, as a recorded term. If the authors want C6 applied strictly, use "intervention" here and at 1083. |
| — | 1179 [10] | keep | "every quantity carried over from the conference paper was recomputed from new runs" | Keep. It is a factual provenance statement that readers can check against the repository. |
| — | 1139–1143, 1182 | not a defect | `\pending` placeholders carry the run codes E6p, E8, E9, E11. | Exempt as pending. The eventual Table 4 and §6.3 text must not carry these codes (same fix as 11.1–11.4). |


---

## 12. Terminology and notation drift

### Block W: whole paper

#### 12.0 The five worst drifts (S1)

1. **"class" names three taxonomies and a fourth grouping** (table row 12.1). The paper says deadlocks "fall into two classes" (653, 835, 1177), then that blocker removal "sorts the corrected-forward deadlocks into three classes" (1035). It also has "five ... mechanism classes" (834). A reader cannot tell whether there are two deadlock classes or three. This also feeds the count contradiction in 13.1.
2. **"collective" names both a deadlock outcome and a barrier condition** (12.2). In 1035 and 1123 "collective" means the keystone outcome that turns out to be a pair or group standoff. In 835, 1016, 1058, 1065, 1067, 1117 and 1179 it means escape with the neighbours mobile, at a lone trap. Section 5.4's "collective barrier" belongs to lone traps. Section 5.1's "collective" deadlocks are not lone traps.
3. **"frozen" has four meanings** (12.3):
   - the snapshot;
   - the neighbours-pinned barrier condition;
   - frozen densities;
   - the "frozen-mean" arm.
   In 1065 to 1067 "frozen" names a condition in a paper whose subject is "frozen deadlock states".
4. **λ is both the escape rate and the softest Hessian eigenvalue** (12.4). **b\* is both the per-snapshot fold threshold and the matched bias** (12.5). Section 6.2 line 1136 says "reading $b^\ast$ per solver off the fold curve", which uses one symbol for both meanings in a single clause.
5. **The wall-range symbol $B_{w,\rm edge}$ is defined (865) and never used.** The jamb-only variant is then written "$B_w=0.04$" (822, 1047, 1148, 1151, 1157). Table 1 makes $B_w$ the range of every wall, so the text appears to describe the all-walls variant.

#### 12.1 Full drift table

One row per concept. Every instance is line-anchored. "Recommended" gives the single name to keep. The replacement for each non-recommended instance follows the arrow.

| # | Concept | All names / symbols used (line, src) | Recommended single name and replacements | Sev |
|---|---|---|---|---|
| 12.1 | Taxonomy words | **mechanism class (P/L/T/D/N):** 652 abs "a physically defined mechanism class"; 834 intro "five physically defined mechanism classes", "each class predicts"; 929 T2 "each class"; 937 T2 header "Class"; 981 sig "Each class predicts"; 1001 sig "class P at most", "class L"; 1020 sig "a control from a different class", "Assign each to the class"; 1111 att "class L"; 1114 att "(class D)"; 1120 att "(class N)"; 1136 att "class-D control"; 1163 disc "a probe of its own class"; 1166 disc "(class L)", "(class T)", "(class D)"; 1179 back "five mechanism classes". **deadlock class (lone trap / pair):** 652 abs "deadlocks fall into two classes"; 832 intro "In two deadlock classes"; 835 intro "fall into two classes"; 836 intro "At the pair class"; 1047 phys "The second class has no lone agent"; 1125 att heading "The Pair Class"; 1177 concl "come in two classes". **keystone outcome:** 1035 phys "sorts the corrected-forward deadlocks into three classes"; 1035 phys "The class of the remaining deadlocks changes with the law". **final-state category:** 1123 att "The final states differ in class", "(classes 56/31/0, ...)" | Keep **"class"** for the mechanism taxonomy only. Deadlocks get **"type"**; keystone outcomes get **"outcome"**. 652 → "deadlocks are of two types"; 832 → "In two deadlock types"; 835 → "fall into two types"; 836 → "At the pair standoff ORCA acts"; 1047 → "The second type has no lone agent that is held."; 1125 → "Attribution at the Pair Standoff"; 1177 → "come in two types"; 1035 → "sorts the corrected-forward deadlocks by outcome:" and "The type of the remaining deadlocks changes with the law."; 1123 → "The final states differ in type ($p=\EsixClassP$)" and "(lone keystone/second trap/group standoff: 56/31/0)" | S1 |
| 12.2 | "collective" | **keystone outcome = pair or group standoff:** 1035 phys "and \KeystoneBCollective\ are collective"; 1035 "\EsevenDefaultCollective\ of \EsevenDefaultClassified\ deadlocks are collective"; 1035 "with jamb-only short range \EsevenBjambCollective\ of \EsevenBjambClassified\ are collective" (the next two clauses inherit the word); 1123 att "lone/second trap/collective". The same category appears as "pair or group standoff" at 1042 (Fig 3 caption, phys). **escape / barrier with neighbours mobile:** 835 intro "collective activated escape"; 1016 sig heading "Collective Activated Escape"; 1058 phys heading "Noise as Collective Activated Escape"; 1065 phys "spread over the collective barrier"; 1067 phys "The escape is collective"; 1117 att "spread over the collective barrier"; 1179 back "collective activated escape" | Keep **"collective"** for escape. Rename the keystone outcome **"group standoff"**, matching Fig 3's "pair or group standoff". 1035 → "and \KeystoneBCollective\ are group standoffs", "deadlocks are group standoffs", "are group standoffs"; 1123 → "lone/second trap/group standoff". Name the barrier after its condition: 1065 and 1117 "spread over the collective barrier" → "spread over the full barrier" | S1 |
| 12.3 | "frozen" | **the snapshot:** 652 abs "frozen deadlock states"; 822 F1cap "the black ball marks the frozen state"; 832 intro "the same frozen deadlock states"; 834 intro "how a frozen deadlock responds"; 842 bg "at a frozen state"; 854 bg "of a frozen deadlock"; 929 T2 "of a frozen deadlock"; 981 sig "leaving a frozen one as it is", "of the same frozen state"; 1020 sig "frozen snapshots"; 1172 disc "frozen equilibria"; 1177 concl "frozen deadlocks"; 1179 back "frozen deadlocks". **neighbours pinned:** 1017 sig "neighbours pinned (frozen)"; 1062 phys "frozen neighbours dashed"; 1065 phys "in the full, frozen and alone conditions"; 1067 phys "\EfourRatioFrozen\ (frozen)", "the frozen and alone conditions". **densities held fixed:** 984 sig "freeze the densities"; 997 sig "With the densities frozen"; 1049 phys "With the densities frozen"; 1175 disc "freezes the densities". **constant-push arm:** 981 sig "(the frozen-mean arm)"; 1083 att "frozen mean $+$ solid"; Fig 6 and Fig 7 ticks "frozen +", "frozen −" | Keep **"frozen"** for the snapshot and the densities. Rename the condition **"pinned"**: 1017 → "neighbours pinned (pinned)"; 1062 → "pinned neighbours dashed"; 1065 → "in the full, pinned and alone conditions"; 1067 → "(pinned)" and "the pinned and alone conditions". Rename the arm **"rest-drive push"**: 981 → "(the rest-drive push)"; 1083 → "rest-drive push $+$ solid"; ticks → "push +", "push −" (fig6, fig7 scripts) | S1 |
| 12.4 | λ | **escape rate:** 848 bg $\lambda=\nu\exp(\cdot)$; 1010, 1012 sig Eq. 10; 1017 sig "$\ln\lambda$ is linear"; 1067 phys "slope of $\ln\lambda$"; 1087 T3 caption $\hat\lambda$; Fig 4 axis "ln(λ̂/ν̂)". **softest Hessian eigenvalue:** 1049 phys "$\lambda_1=\PairLamOneMin$"; 1051 phys "where $\lambda_1$ reaches zero"; 1053 phys "spread over $\lambda_1$", "$\lambda_1$ does not predict them" | Keep λ for the rate. Write the eigenvalue as **$\mu_1$** (unused elsewhere) at 1049, 1051 and 1053 (×2) | S1 |
| 12.5 | b\* | **per-snapshot fold threshold:** 929 T2 "$b^{*}$: fold bias"; 971 T2 "frees only beyond $b^{*}$"; 981 sig "at bias $b^\ast$"; 1051 phys "the threshold $b^\ast$ lies between". Also called "the snapshot's fold" (1051), "static threshold" (1051) and "fold curve" (1136). **matched control bias:** 1103 and 1105 T3 $b^\ast_{\rm pub}$, $b^\ast_{\rm RVO2}$; 1136 att "reading $b^\ast$ per solver off the fold curve", "$\pm b^\ast$", "$-b^\ast_{\rm pub}$"; 1163 disc "a bias at $b^\ast$"; Fig 7 ticks "+b\* pub" etc. | Keep **$b^\ast$ for the matched bias**, parallel to σ\*. Use **$b_{\rm f}$ (fold threshold)** for the snapshot property: 929 → "$b_{\rm f}$: fold threshold"; 971 → "frees only beyond $b_{\rm f}$"; 981 → "at bias $b_{\rm f}$"; 1051 → "the threshold $b_{\rm f}$ lies between", "exceeds the snapshot's $b_{\rm f}$", "below the snapshot's $b_{\rm f}$"; 1136 → "reading $b^\ast$ per solver off the curve of freed fraction against $b$" | S1 |
| 12.6 | Jamb-only wall range | 865 T1 defines "$B_{w,\rm edge}$ (within 0.5 m of the door edge)" and never uses it. The variant is written: 822 F1cap "wall ranges $B_w=0.08$~m above and $0.04$~m below"; 1035 phys "shortening it on the door jambs alone", "jamb-only short range"; 1047 phys "jamb-face walls of range $B_w=0.04$\,m"; 1148 val "with jamb $B_w=0.04$ square"; 1151 val "the wall range at the jambs reduced to $B_w=0.04$\,m"; 1157 val "With the jamb wall range reduced to $B_w=0.04$\,m"; 1160 val "the reduced jamb range"; Fig 3 tick "jambs 0.04"; Fig 8 tick "C1 jamb Bw" | **$B_{w,\rm edge}$**, with "jamb" defined once in Table 1 as "wall within 0.5 m of a door edge". 1047 → "jamb walls of range $B_{w,\rm edge}=0.04$\,m"; 1148 → "with $B_{w,\rm edge}=0.04$ square"; 1151 → "with $B_{w,\rm edge}=0.04$\,m"; 1157 → "With $B_{w,\rm edge}=0.04$\,m"; 1160 → "the reduced $B_{w,\rm edge}$"; 822 → "$B_w=0.08$~m above and $B_{w,\rm edge}=0.04$~m below" (or all walls, whichever the render used); ticks → "B_w,edge 0.04" (fig3), "C1 B_w,edge" (fig8). Check 1047 against C23 ("CF ∪ {B_w = 0.04}") and FINAL_PLAN E7b ("B_w = 0.04 all walls"). If the pair library used all walls, 1047 is wrong as well as inconsistent | S1 |
| 12.7 | Sigmoid gate | 867 T1 "gate $w_o=1-\sigma(\rho;4,2)$"; 868 T1 "gate $w_c=\sigma(\rho;5.5,3)$"; 918 model $w_{o,i}=1-s(\rho_i;4,2)$; 920 model $s(x;x_0,c)$, $w_{c,i}=s(\rho_i;5.5,3)$. σ is also the noise amplitude everywhere | **$s(\cdot)$**: 867 → "$w_o=1-s(\rho;4,2)$"; 868 → "$w_c=s(\rho;5.5,3)$" | S2 |
| 12.8 | ORCA relaxation time | 867 T1 "$\tau_{\rm ORCA}=0.5$ s"; 918, 920 model "$\tau_{\rm orca}$" | **$\tau_{\rm orca}$** (matches $\mathbf F^{\rm orca}$): 867 → "$\tau_{\rm orca}=0.5$ s" | S2 |
| 12.9 | Time step | 870 T1 "$\mathrm{d}t=0.01$ s"; every other use is Δt (923, 929-981, 1004-1014, 1077, 1117, 1169, Fig 5 axis) | **Δt**: 870 → "$\Delta t=0.01$ s" | S2 |
| 12.10 | g | **goal:** 869 T1 "goal $g=(11,5)$ m"; 890 model $\mathbf g$; 999 sig $|\mathbf x_i-\mathbf g|$. **ramp:** 898 model "$g(x)=\max(0,x)$"; 900, 904 Eqs. 3-4; 997 sig "$-\kappa\,g\,[\ldots]^2$". **wall force maximum:** 1029, 1031, 1033 phys; 1160 val $g_{\max}(r)$ | Keep $\mathbf g$ (goal) and $g_{\max}$. Write the ramp as **$(x)_+$**: 898 → "and $(x)_+=\max(0,x)$"; Eqs. 3-4 → $k\,(r_{ij}-d_{ij})_+$, $\kappa\,(r_{ij}-d_{ij})_+$, $k\,(r_i-d_{iW})_+$, $\kappa\,(r_i-d_{iW})_+$; 997 → "$-\kappa\,(r_{ij}-d_{ij})_+[\ldots]^2$" and "$-\kappa\,(r_i-d_{iW})_+(\ldots)^2$" | S2 |
| 12.11 | k | 864 T1, 900, 904 model: contact stiffness $k$; 1017 sig "(Weibull shape $k=1$)"; Weibull shapes elsewhere carry no symbol (1053, 1067, 1123) | Contact stiffness **k**. 1017 → "(Weibull shape 1)" | S3 |
| 12.12 | r | Agent radius $r$ throughout; 865 T1 "rounded edge $r=0.1$ m" | 865 → "edge rounded to radius 0.1 m" | S3 |
| 12.13 | Barrier-to-temperature ratio | 981 sig "$\Delta U/k_BT_{\rm eff}$"; 1053 phys "$\Delta U/k_BT_{\rm eff}$"; 1062 phys caption "$\Delta U_{\rm cond}/k_BT_{\rm eff}$" (×2; "cond" never defined in text) and Fig 4 axis; 1065 phys "$\Delta U/k_BT_{\rm eff}$"; 1077 att caption "$\beta_{\rm ref}=1.5$" (used before its definition at 1117); 1117 att "$\beta_{\rm ref}=\Delta U/k_BT_{\rm eff}$ at $\Delta t=0.01$\,s"; 1166 disc "$\Delta U/k_BT_{\rm eff}$" | Define **β ≡ ΔU/k_BT_eff** once after Eq. 10 (sig, 1014): "We write $\beta\equiv\Delta U/k_BT_{\rm eff}$ and $\beta_{\rm ref}$ for its value at $\Delta t=0.01$\,s." 1062 → "at $\beta=2.5$" and "against $\beta$"; Fig 4 axis → "β". 1065 → "so that $\beta$ took the values 1.5, 2.5 and 3.5". 1117 → "with noise set so that $\beta_{\rm ref}$ is 1.5 or 2.5". 1053 → "Here $\beta$ is below 1". 981 and 1166 may keep the explicit ratio [TASTE] | S2 |
| 12.14 | Attempt prefactor | 848 bg "$\nu$ an attempt frequency"; 1062 phys "the fitted attempt rate"; 1067 phys "the median attempt rates"; 1123 att "the measured attempt rate"; Fig 4 axis "ν̂" | **attempt rate ν**: 848 → "$\nu$ an attempt rate" | S3 |
| 12.15 | Model modes | **published:** 872 T1 header "published-reproduction"; 923 model "The published-reproduction mode"; 1035, 1071, 1148, 1151, 1157 "published mode"; 906 "The published code"; 923 "the published update". **corrected:** 872 T1 "corrected-forward"; 906 model "the corrected mode"; 923 "corrected update" (×2), "the corrected-forward mode"; 1004 sig "the corrected update"; 1035 phys "in the corrected mode"; 1071 phys "in the corrected mode"; "corrected-forward" at 1035, 1047, 1056, 1065, 1111, 1148, 1151 (×2), 1157 (×2), 1179. Table 1 caption 857 "the two declared modes" | Define once at 923: "the published mode (published-reproduction) and the corrected-forward mode". Then use **"published mode" / "corrected-forward mode"** throughout. 906 → "the corrected-forward mode lets"; 1035 → "in the corrected-forward mode"; 1071 → "in the corrected-forward mode"; 857 → "the two modes". "corrected update" (923, 1004) may stay as the name of the integrator step [TASTE] | S2 |
| 12.16 | ORCA solvers | **published solver:** 920 model, 1111 att, 1119 att heading, 1133 att, 1136 att, 1179 back "published solver"; 1120 att "Only the published linear program"; 1169 disc "The published linear program", "only the published program"; 1140 att (pending) "published-solver ORCA"; 1083 att, 1104 T3 "C3 published"; Fig 6 and Fig 7 ticks "C3 pub", "constr. pub", "+b\* pub". **RVO2:** 842 bg "the RVO2 library"; 877 T1 "line-by-line RVO2 port"; 920 model "a port of the RVO2 library"; 1133 att "RVO2 \PairRvoFreed", "full RVO2 ORCA"; 1136 att "freed by RVO2 or its match"; 1169 disc "and RVO2" | **"published solver" / "RVO2 solver"** for the solvers, and **"C3 published" / "C3 RVO2"** for the configurations. 1120 → "Only the published solver changes outcome"; 1169 → "The published and RVO2 solvers free ..., and only the published solver changes outcome"; 1133 → "full C3 RVO2 frees fewer than its drive"; ticks "C3 pub" → "C3 published" and "constr. pub" → "constr. published" (fig6, fig7) | S2 |
| 12.17 | ORCA rest drive and its arm | 920 model defines "\emph{ORCA's rest drive}". Variants: 653 abs "ORCA adds a goal drive"; 822 F1cap "ORCA's rest drive (blue)" and Fig 1 label "added drive"; 836 intro "an added goal drive"; 981, 1001, 1033 "ORCA's rest drive"; 1026 phys caption "the rest-state drive for C3 RVO2"; 1083 att "drive only"; 1111 att "ORCA's drive alone", "with ORCA's drive added"; 1120 att "its own drive", "(its drive ...)", "slower than its drive"; 1133 att "drive alone", "fewer than its drive"; 1166 disc "a second goal drive"; 1177 concl "its rest drive"; Fig 6 and Fig 7 tick "drive" | Force: **"ORCA's rest drive"**. Intervention: **"drive-only arm"** (or "drive-only intervention" if 12.25 is adopted). 653 → "ORCA adds a constant goal drive at rest"; 836 → "ORCA acts through its rest drive, a constant added goal drive"; 1026 → "of ORCA's rest drive added to it for C3 RVO2"; 1083 → "drive-only dashed"; 1111 → "the drive-only arm frees the same ones" and "with ORCA's rest drive added"; 1120 → "than its drive-only arm", "(drive-only: \CtwsixDriveFreed)", "slower than the drive-only arm"; 1133 → "drive-only \PairDriveFreed" and "fewer than its drive-only arm"; 1166 → "a second, constant goal drive (its rest drive)". The Fig 1 label "added drive" is approved (C32) and stays | S2 |
| 12.18 | Constant goal-parallel push probe | 942 T2 header "Goal push, $+$ vs $-$"; 981 sig "a constant goal-parallel push of either sign equal to ORCA's rest drive (the frozen-mean arm)"; 1083 att "frozen mean $+$"; 1111 att "A constant push equal to the rest drive"; Fig 6 and Fig 7 ticks "frozen +", "frozen −" | **"rest-drive push (±)"**: 942 → "Rest-drive push, $+$ vs $-$"; 981 → "(the rest-drive push)"; 1083 → "rest-drive push $+$"; 1111 → "The rest-drive push frees ... pointed at the door"; ticks → "push +", "push −" | S2 |
| 12.19 | Blocker | Used before definition: 822 F1cap "(the blocker's position on the door axis"; 895 model "At deadlock detection the blocker has at most". Defined at 1035 phys "the blocker, the agent nearest the door" | Define at the first use in the body, in Scenarios (926): "...saved as a snapshot; its blocker is the remaining agent nearest the door." Delete the appositive at 1035 | S2 |
| 12.20 | Stuck alone / passes alone | "stuck alone" / "stuck-alone" at 835, 1033 (×3), 1035 (×3), 1037 (×5), 1160, 1166, 1169, 1179. **held alone:** 1026 phys caption "(held alone)"; Fig 1 label "held alone"; 1029 phys "held when it is alone". **passes alone:** 1026 "(passes alone)"; Fig 1 label "passes alone"; 1037 "can pass alone", "could pass alone" | **"stuck alone" / "passes alone"**. 1026 → "(stuck alone)"; 1029 → "the agent is stuck alone if and only if". The Fig 1 label "held alone" is approved (C32); ask the hero owners to change it to "stuck alone" or accept the one-word mismatch | S3 |
| 12.21 | Lone deadlock type | **lone trap:** Fig 1 label; 836, 1035 (×2 "lone traps"), 1042, 1053, 1065, 1073 heading, 1094, 1163, 1166, 1169 (×2), 1177. **lone-agent trap:** 822 F1cap; 835 intro; 1022 phys heading. Also 653 abs and 1177 concl "a lone agent held by the wall force at the door edges" (description); 1035 "stuck-alone stacks", "a short stack of stuck-alone agents"; 1037 "the chain of stuck-alone agents" (C16 wording) | **"lone trap"**. 822 → "The lone trap at a 0.8~m door (top)"; 835 → "a lone trap set by the wall force"; 1022 → "The Lone Trap at the Door Edges". "Chain" stays the C16 name of the arrival sequence; see 12.22 | S3 |
| 12.22 | "chain" | **arrival sequence:** 1037 phys "the chain of stuck-alone agents" (C16). **contact arch:** 1056 phys "a chain of agents in contact", "a chain of agents in mutual contact", "Such chains form" | Keep "chain" (C16) for 1037. Use **"arch"** at 1056: "an arch of agents in mutual contact that touches both jambs. Such arches form ..."; "so agents in contact can carry a load only while they slide" | S3 |
| 12.23 | Pair deadlock type | **symmetric pair standoff:** 653 abs; 822 F1cap; 835 intro; 1046 phys heading; 1177 concl. **pair standoff(s):** 1035 (×2), 1120 "held pair standoffs", 1163, 1169, 1175. **pair class:** 836 intro; 1125 att heading. **the pair:** 653 abs "at the pair"; 1053 "the pair needs"; 1114 "at the pair"; 1163 "at the pair"; 1177 "at the pair". **bare "standoff(s)":** 1047, 1049 (×3), 1051, 1133, 1136 (×4). **pair or group standoff:** 1042 phys Fig 3 caption. **pair geometry:** 1120 att. "Symmetric" conflicts with 1051 "no standoff is exactly symmetric" | **"pair standoff"**. Drop "symmetric" from the name, because 1051 shows the standoffs are not exactly symmetric: 653 → "a pair standoff, a strict energy minimum"; 822 → "the pair standoff (bottom)"; 835 → "a pair standoff of two near-mirror-image agents"; 1046 → "The Pair Standoff"; 1177 → "a pair standoff that is a strict minimum". 836 → "At the pair standoff"; 1125 → see 12.1. "At the pair" (653, 1114, 1163, 1177) → "at the pair standoff". Bare "standoff" after 1047 is fine. A footnote or Fig 1 change is not needed | S2 |
| 12.24 | Barrier conditions and names | 1017 sig "with all residual agents mobile (full), neighbours pinned (frozen), or the blocker alone (alone)"; 1062 phys "all residual agents mobile", "frozen neighbours", "the blocker alone"; "full barrier" at 1067, 1069 (×2); "collective barrier" at 1065, 1117; "alone barrier" at 1017, 1067; 1017 "the condition's own barrier"; 1062 "$\Delta U_{\rm cond}$"; 1053 "gated pair barriers", "lone-trap barriers"; 1123 "gated library barriers" | Conditions **full / pinned / alone** (12.3). Barriers **"full barrier", "pinned barrier", "alone barrier"**. 1065 and 1117 → "full barrier" (12.2); 1062 → drop "cond" (12.13) | S2 |
| 12.25 | Intervention vocabulary (C6 drift) | **arm** (clinical-trial term, against C6): 926 model "(an arm)", "deterministic arms stop", "so arms are compared"; 981 sig "(the frozen-mean arm)"; 1083 att "for the arms that free"; 1092 T3 header "Arm"; 1133 att "Every deterministic arm". **strata:** 1083 att "strata pooled". **resolver** (undefined): 851 bg "which one a given resolver resembles"; 1014 sig "absent for a deterministic resolver"; 1172 disc "Wherever a resolver is credited". **intervention:** 845, 926, 981 (×2), 1083 | **"intervention"**. 926 → delete "(an arm)", then "(deterministic interventions stop ...)" and "so interventions are compared snapshot by snapshot"; 981 → see 12.18; 1083 → "for the interventions that free" and "lone keystone and second trap pooled"; 1092 → "Intervention"; 1133 → "Every deterministic intervention"; 851 → "which one a given paradigm resembles"; 1014 → "absent for a deterministic intervention"; 1172 → "Wherever a paradigm is credited" | S2 |
| 12.26 | The matched quantity | "headline score": 830, 832, 854, 1179. "headline completion rate": 832. "completion rate": 653, 828, 830, 836, 1020, 1123, 1177. "the paradigm's score": 1163. "success rate": 1172. Bare "rate": 653 "ORCA's rate"; 1087 "on rate"; 1114 "that rate"; 1136 "on rate alone", "reproduce the rate"; 1163 "at ORCA's rate", "at its rate"; 1166 (×3). At the lone trap and the pair the matched quantity is a **freed fraction of snapshots**, not a completion rate (1114, 1136, T3) | **"rate"**, defined once at 830 as "the paradigm's headline rate: completion of whole runs, or the freed fraction of a snapshot library". 653 → "tuned to reproduce its rate of resolving deadlocks"; 1020 → see 13.2; 1172 → "match a control to its rate"; "headline score" at 830, 832, 854 and 1179 → "headline rate" | S1 (13.2) |
| 12.27 | Human comparison quantity | 653 abs "of the human rate"; 837 intro "of the human flow"; 1156 val heading "about half the human rate"; 1157 val "of the human flow"; 1160 val "of the human value"; 1177 concl "of the human flow". Verbs: 653 "flows at"; 837 "passes only"; 1177 "passes"; 1157 "the flow ... is" | **"human flow"**, verb **"flows at"**. 653 → "flows at ... of the human flow"; 837 → "flows at only ... of the human flow"; 1156 → "Every model variant deadlocks or flows at 0.40-0.59 of the human flow."; 1160 → "of the human flow"; 1177 → "each deadlocks or flows at ... of the human flow". "Rate" elsewhere means completion or freed fraction (12.26), so "human rate" in the abstract is ambiguous | S2 |
| 12.28 | Exit width | 653 abs "at a 0.8\,m exit"; 822 F1cap "at a 0.8~m door"; 869 T1 "door $w=0.8$ m"; 1035 "the critical width"; 1042 phys caption "against exit width"; Fig 3 axis "exit width w (m)"; 1151 val "at an entrance width of 0.8\,m" (CroMa term); 1175 disc "room exits near $w=0.8$\,m"; 835, 1177 "Narrow-exit deadlocks"; 1160 "narrow doors" | **"door width w"** in the model. "Entrance" only for CroMa, introduced once at 1151 as "the CroMa entrance (our door)". 653 → "at a 0.8\,m door"; 1042 → "against door width"; Fig 3 axis → "door width w (m)" (fig3); 1175 → "room doors near $w=0.8$\,m" | S3 |
| 12.29 | Door edge / jamb | "door edge(s)": 653, 835, 865, 906, 1022, 1029, 1035, 1151, 1160 (×3), 1177, 1179. "jamb(s)": 1056, 1151. "jamb faces": 1035, 1047 (×2). "door jambs": 1035. "jamb corners": 1035. "jamb wall law" / "jamb law": 1035 (×2), 1169 | Use "door edge" for the segment end point and **"jamb"** for the wall within 0.5 m of it, defined in Table 1 (12.6). 1047 "jamb faces" → "jambs" (×2); 1035 "door jambs alone" → "jambs alone"; 1035 "jamb corners" → "door edges" ("Rounding the door edges") | S3 |
| 12.30 | Rest-state energy / field | 988 sig "the rest-state field"; 997 sig "the C1 rest field"; 1049 phys "the rest field"; 1051 phys "the rest field"; 822, 835, 1177 "rest-state energy"; 835 "energy landscape"; 1001, 1017, 1177 "landscape" | **"rest-state field $\mathbf F_0$"** and **"rest-state energy U"**. 997 → "the C1 rest-state field"; 1049 → "the rest-state field is $-\nabla U$"; 1051 → "relaxation of the rest-state field under bias" | S3 |
| 12.31 | Lemma vs proposition | 834 intro "a rest-state lemma"; 990 sig `\begin{proposition}[rest-state lemma]` (renders "Proposition 1 (rest-state lemma)"); 1001 sig "The lemma covers"; 1049 phys "Proposition~\ref{prop:rest}"; 1111 att "(Proposition~\ref{prop:rest})"; 1179 back "the rest-state lemma" | **Lemma 1 (rest state)**: use `\begin{lemma}[rest state]` at 990, and refer to it as "Lemma~\ref{prop:rest}" at 1049 and 1111. [TASTE]: the alternative is to keep "Proposition" and call it "the rest-state proposition" at 834, 1001 and 1179 | S3 |
| 12.32 | Moment of measurement | 895 model "At deadlock detection the blocker has at most..."; 1029 phys "At the terminal rest state of a deadlock the blocker's Weidmann factor is at least..." (the same 393 measurements) | **"at the snapshot"**: 895 → "In the snapshot the blocker has at most"; 1029 → "In the snapshot the blocker's Weidmann factor is at least" | S3 |
| 12.33 | AUC | 1037 phys "an area under the ROC curve of"; 1111 att "(ROC area \EtwoLKMarginAUC)" | **"AUC"**, defined at 1037: "an area under the ROC curve (AUC) of"; 1111 → "(AUC \EtwoLKMarginAUC)" | S3 |
| 12.34 | "pair(s)" overload | Pair standoff (12.23); 1163 disc "in all three of our pairs" (control–paradigm pairings); "paired" statistics at 926, 1087, 1111 | 1163 → "in all three matches" | S2 |
| 12.35 | Time to freeing | 836 intro "time-to-free"; 926 model "times to freeing"; 1087 T3 "Kaplan--Meier median $t_{1/2}$"; 1111 "first-exit shift"; 1114 "standard deviation of the first exit" | **"time to freeing"** with KM median $t_{1/2}$. 836 → "and in time to freeing" | S3 |
| 12.36 | Outcome words: freed / escaped | Quench outcome "freed" (926, 1083, 1111, 1129, Fig 6 "fraction freed", Fig 7 "pair freed"); noise E4 "escaped" (1062; Fig 4 "fraction escaped"), "escapes" (1065), "escape events" (1069) | [TASTE]: the escape vocabulary carries the Kramers framing. Add one clause at 1017: "an escape is a freeing of the blocker under noise". Keep both words | S3 |
| 12.37 | Restart / quench | 926 defines "quench". "restart(ed)": 1035, 1049 "C1 restart", 1065 "restarts per level", 1069, 1120 "at restart". Fig 4 axis "time after restart (s)"; Fig 6 axis "time after quench start (s)" | "quench" for one run under an intervention, "restart" for one noise repetition. Make the axes match: Fig 6 axis → "time after restart (s)" (fig6), or both "time after quench start (s)" | S3 |
| 12.38 | Fig 6 / Fig 7 y-axis | Fig 6 "blocker freed within 120 s"; Fig 7 "pair freed (120 s)" | Fig 7 → "pair freed within 120 s" (fig7) | S3 |
| 12.39 | Lateral bias / tilt | "lateral bias" (653, 835, 836, 923 "lateral-bias control", 1051, 1114, 1177); 981 sig "a finite directional bias"; 1136 "class-D control"; "tilt": 923 "a deterministic tilt", 942 T2 header "Tilt $b\to-b$", 981 "reversal of a lateral tilt", 1051 "small tilts", 1166 "tilts" (verb), Fig 1 labels "no tilt", "tilted" | **"lateral bias"** for the control. "Tilt" only as the verb for what it does to the landscape (1051, 1166, Fig 1). 942 → "Bias $b\to-b$"; 981 → "reversal of the lateral bias"; 1051 → "it survives small biases" | S3 |
| 12.40 | Replay signature | 939 T2 "Replay, $10^{-9}$\,m"; 981 "a replay perturbed by $10^{-9}$\,m"; 1087, 1111, 1120, 1169 "$10^{-9}$\,m replays"; 1163 disc "the time step and seed replay for noise" (undefined: for noise the probe is that seeds disagree, 1087 and 1114) | 1163 → "the time step and seed-to-seed disagreement for noise" | S3 |
| 12.41 | Corner rule | 879 T1, 906 "convex-union rule"; 1151 val "only the nearer of the two acts"; 1160 val "the nearest point on the union of the walls counts it once" | **"convex-union rule"**: 1160 → "the convex-union rule (Sect.~\ref{sec:model}) counts it once" | S3 |
| 12.42 | Waiting-zone measure (C50) | 1148 val caption "waiting-zone velocity fluctuation"; 1151 "the velocity fluctuation"; 1154 val "The waiting-zone fluctuation is"; Fig 8 axis "waiting-zone fluctuation (m/s)"; 1157 "more agitated" | C50 records **"velocity fluctuation"**. 1154 → "The waiting-zone velocity fluctuation is"; Fig 8 axis → "waiting-zone velocity fluctuation (m/s)" (fig8) | S3 |
| 12.43 | Speed cap | 867 T1 "speed cap $2v_0$"; 870 T1 "speed limit $2v_0$"; 874-875 T1 "clamp", "re-clamped"; 923 "$\Pi$ caps the speed" | **"speed cap"**: 870 → "speed cap $2v_0$" | S3 |
| 12.44 | TTC threshold | 866 T1 "pair counted only if $|\Delta v|^2\ge1\times10^{-8}$ m$^2$/s$^2$"; 913 model "$|\Delta\mathbf v|\ge10^{-4}$\,m/s"; 997 sig "below relative speeds of $10^{-4}$\,m/s" | One form: 866 → "pair counted only if $|\Delta v|\ge10^{-4}$ m/s" | S3 |
| 12.45 | Weidmann factor | 895 model "its Weidmann factor is at least"; 1029 phys "the blocker's Weidmann factor" (never defined; it is the clip term of Eq. 2) | Define at 895: "its Weidmann factor $v_{{\rm eff},i}/v_{0,i}$ is at least" | S3 |
| 12.46 | Undefined labels in Table 3 | 1087 T3 "(E3)"; 1094 "(E2)"; 1098 "(E6)"; 1102 "(E7b)". No experiment code is defined in the prose | Delete the four codes. The block headings already name the data. For 1087, write "with its Arrhenius prediction (Sect.~\ref{sec:att-lone})" | S2 |
| 12.47 | Undefined set names | 1001 sig "over the \ResidBarN\ barrier and ... pair snapshots" (renders "over the 60 barrier and ..."); 1008 sig "over the \TthreeCells\ noise cells" ("cell" also means an E7 grid cell at 1035 and 1042); 1123 "the 56 gated library barriers" | 1001 → "over the 60 snapshots of the quench library"; 1008 → "over the 207 (snapshot, condition, noise level) combinations". 1001 says 60 and 1123 says 56 barriers; state which library each count refers to | S2 |
| 12.48 | Deadlock / jam / stall | 828 intro "empties a room that pure SFM leaves jammed", "resolved the jam"; 1047 "a contact jam"; "stall" defined at 1123 ("at least 10 s without an exit") and used at 1157, 1160; 1169 "unstick" | **"deadlock"**: 828 → "leaves deadlocked" and "resolved the deadlock". Keep "contact jam" (1047) as a contrast and keep "stall" (defined) | S3 |
| 12.49 | Base model | 653 abs "the base model"; 828 intro "pure SFM"; 830 intro "the baseline model"; 887 model "C1 is SFM only" | **"base model"**: 830 → "a perturbation of the base model"; 828 → "that C1 (SFM only) leaves deadlocked" | S3 |
| 12.50 | C3 boundary | 1026 phys caption "the two blue lines the C3 boundary"; elsewhere configurations carry the solver (C3 RVO2, C3 published) | 1026 → "the C3 RVO2 boundary". At rest with no binding constraint both solvers give the same drive (920), so the solver label may be dropped deliberately; say so if that is the intent | S3 |
| 12.51 | Noise names | 835 intro "Velocity noise"; "per-step noise" (941 T2, 981, 1003 heading, 1008, 1065, 1077, 1114, 1117, 1179); "$\sqrt{\Delta t}$-scaled noise" (981, 1008, 1014, 1077); 941 T2 header "$\Delta t$, $\sqrt{\Delta t}$ noise"; 1117 "Noise scaled with $\sqrt{\Delta t}$"; 1113 heading and 1160 "matched noise" | **"per-step noise" / "$\sqrt{\Delta t}$-scaled noise"**: 941 → "$\Delta t$, $\sqrt{\Delta t}$-scaled noise"; 1117 → "$\sqrt{\Delta t}$-scaled noise removes the effect" | S3 |

#### 12.2 Approximate in one place, exact in another

| Line (src) | Approximate | Exact elsewhere | Replacement |
|---|---|---|---|
| 1156 val heading | "flows at about half the human rate" | 653, 837, 1157, 1177 "0.40--0.59" | See 12.27 |
| 1053 phys | "Here $\Delta U/k_BT_{\rm eff}$ is below 1 at every noise level we ran for most snapshots" | No count of the snapshots | "For [k] of the 12 snapshots, $\beta$ is below 1 at every noise level we ran" (needs the count from `E7b_analysis.json` d_barriers) |
| 1136 att | "noise frees nearly every standoff (Sect. 5.2)" | 1053 "224 of 230 runs" | "noise at $\sigma=0.01$\,m/s frees 224 of 230 runs (Sect.~\ref{sec:pair})" |
| 1053 phys | "the pair needs a few seconds of deterministic run-out" | No number | State the median run-out time or delete "a few seconds of" |


---

## 13. Numbers and internal consistency

### Block W: whole paper

Ordered by severity.

**13.1 [S1] Two deadlock classes or three (653 abs, 832 intro, 835 intro, 1177 concl vs 1035 phys).** The abstract, introduction and conclusions say "two classes". Section 5.1 sorts deadlocks "into three classes" (lone keystone, lone keystone with a second trap, collective). Section 6.1 then reports the second trap with pair geometry (1120). The text never reconciles 2 and 3. The cause is the "class" drift in 12.1. After the 12.1 fix, add one sentence at the end of the keystone sentence in 1035: "Lone keystones and second traps are both lone traps; the group standoffs are pair standoffs (Sect.~\ref{sec:pair})."

**13.2 [S1] The protocol says "completion rate", but two of the three matches are on freed fraction.**
- 653 abs: "tuned to reproduce its completion rate".
- 1020 sig, step (2): "Tune the control's single parameter to the target's completion rate".
- What was done: the lone-trap noise is matched on the freed fraction of 34 snapshots (1114, T3 block 1), and the pair bias on the freed fraction of 46 snapshots (1136, T3 block 3).

Replacements:
- 1020: "(2) Tune the control's single parameter until it reproduces the target's rate: completion of whole runs, or the freed fraction of a snapshot library; this is calibration, not evidence."
- 653: "tuned to reproduce its rate of resolving deadlocks".

**13.3 [S1] "All three predictions hold" and "noise is thermal" overstate the stated exceptions.**
- 1067 phys: "All three predictions of activated escape hold". The same paragraph lists 3 of 28 fits whose interval misses 1, and median ratios 1.15 and 0.87.
- 1117 att: "Noise is thermal at the temperature of Eq. (9)". Two sentences earlier the β_ref = 2.5 prediction is "outside the interval" (3.23 [2.96, 3.52] against 3.70), and the slope is 0.91 [0.83, 1.01].

Replacements:
- 1067: "The three predictions of activated escape hold, with the exceptions listed below (Fig.~\ref{fig:escape})."
- 1117: "Per-step noise follows the temperature of Eq.~\eqref{eq:teff} to within the slope above; ORCA shows no time-step dependence."

C30 records reporting the shortfall with its CI, so this keeps that decision and only aligns the summary sentence with it.

**13.4 [S1] Human longest gap: rounding creates a contradiction (1154 val).** The sentence is "the longest gap between passages averages 1.7 s and never exceeds 2.0 s, and a run has on average 0.2 gaps longer than 2 s". If no gap exceeds 2.0 s, no run can have a gap longer than 2 s. `E10_analysis.json` gives humans.longest_gap_max = 2.04 s, which prints as "2.0". Replacement: "...averages 1.7 s and never exceeds 2.04 s, and one of the five runs has a gap longer than 2 s." Print \EtenHumanGapMax with two decimals in `registry/e6_e10.yaml`.

**13.5 [S1] "5 of 300 lone-trap snapshots" (1169 disc).** The library has 60 snapshots. 300 is the number of replays (60 × 5). Replacement: "(5 of 300 replays of the 60 lone-trap snapshots)". Related denominators that need a label:
- 1111 says "in \EtwoReplayN" (300).
- Table 3 row C3 RVO2 (1096) gives "0/170" (34 lone keystones × 5).

Make the caption at 1087 say "replays (five per snapshot)".

**13.6 [S2] AUC compared with an accuracy (1037 phys).** The sentence is "predicts whether it exits with an area under the ROC curve of 0.975 [0.970, 0.979], against an all-exit baseline accuracy of 0.931". An AUC and an accuracy are not on the same scale, so "against" has no parallel. C13 records the baseline. Keep it and add the rule's own accuracy, which `E1_analysis.json` E1b.k_rule_refined.rule_accuracy gives as 0.962. Replacement: "...with an AUC of 0.975 [0.970, 0.979]; the $k=3$ rule is right for 0.962 of arrivals, against 0.931 for the all-exit baseline." This needs a registry macro. The same AUC idea appears at 1111 as "ROC area 0.98" with no interval and at a different precision (12.33). Give 1111 an interval or two decimals in both places.

**13.7 [S2] Identical Δ intervals for two different blocks.** Table 3 rows 1095 (34 lone keystones, five seeds) and 1099 (186 whole-run seeds) both print "−0.01 [−0.10, 0.08]". A paired difference on 34 snapshots and an unpaired one on 186 seeds giving the same interval to two decimals is the first thing a reader will doubt. Ask the number audit to confirm both (`TabThreeLKDiff*` against `EsixDiff*`). Discussion 1163 then reports the lone Δ without its interval ("($\Delta=\TabThreeLKDiff$)") and the whole-run Δ with one ("($\Delta=\EsixDiff$ [\EsixDiffLo, \EsixDiffHi])"). Replacement at 1163: "($\Delta=\TabThreeLKDiff$ [$\TabThreeLKDiffLo$, $\TabThreeLKDiffHi$])".

**13.8 [S2] The pair match is called sufficient, while the paper says equivalence cannot be shown.** 1163 disc says "A matched control shows whether a simpler cause suffices ... and in all three of our pairs it does". But 1136 says "46 standoffs are too few to show equivalence within $\pm0.10$", and 1175 says "46 pair standoffs cannot show rate equivalence within $\pm0.10$". The equivalence margin is also internal-only under C6 ("equivalence margins are kept internally only where they set sample sizes"). Replacements:
- 1163: "...and in all three matches the rates agree within their 95% intervals."
- 1136: "though at 46 standoffs the intervals are wide (Table~\ref{tab:matched})."
- 1175: "Samples are finite: the pair-block differences carry intervals of about $\pm0.17$."

**13.9 [S2] "far below the lone-trap barriers" (1053 phys) is a comparative with no parallel.** No lone-trap barrier value is reported anywhere in the paper. C34 says the 27.96 J alone barrier "is the one quoted for the stuck-alone test", but it is not in the text, and the E4 full and alone ranges are not given either. Add the range: "far below the lone-trap full barriers ([min]-[max] J, Sect.~\ref{sec:escape})". Then report that range in §5.4 at 1065 ("barriers of [min]-[max] J (full) and [min]-[max] J (alone)").

**13.10 [S2] "Exact" claims next to stated approximations.**
- 848 bg: "its effective temperature follows exactly from that recursion". Line 1004 says "Near rest and away from contact", and 1008 says "adds terms of order $(\omega\Delta t)^2$ ... negligible" and "$\propto 1/\Delta t$ nearly".
- 1077 att caption: "from the exact discrete $k_BT_{\rm eff}$".
- 1179 back: "the exact effective temperature of per-step noise".
- 1035 phys: "The criterion is exact at the rest state", which rests on 895 "$v_{{\rm eff},i}=v_{0,i}$ to within 1%".

Replacements:
- 848: "follows in closed form from that recursion".
- 1077: "from the discrete-time $k_BT_{\rm eff}$ of Eq.~\eqref{eq:teff}".
- 1179: "the closed-form effective temperature of per-step noise".
- 1035: "The criterion holds without exception at the rest state."

**13.11 [S2] "survives every small displacement, and it does" (1049 phys), then a 1 cm shift frees 1 of 46.** The next sentence is "Only a finite shift of 3 cm carries some standoffs out". A 1 cm shift is also finite. Replacement: "Proposition 1 then predicts that the standoff survives displacements smaller than its basin. No unperturbed C1 restart frees a member, nor do any of the 230 replays perturbed by $10^{-9}$\,m. A common lateral shift of 1\,mm frees 0 of 46, 1\,cm frees 1, and 3\,cm frees 10."

**13.12 [S2] Noise failures "never come to rest" but are given rest-state types (1123 att).** The sentence is "whereas noise failures never come to rest (classes 56/31/0, lone/second trap/collective)". The method in C47 (surgery on final states rebuilt from saved residual positions) is not stated. Replacement: "...whereas noise failures never come to rest; blocker removal on their final positions gives 56 lone keystones, 31 second traps and no group standoff."

**13.13 [S2] Degenerate interval (1105 T3, Jaccard).** "0.00 [0.00, 0.00]" prints a zero-width bootstrap interval as if it were a measurement. Replacement: "0 (0 of 15 shared)". Discussion 1163 "0.00 at the pair" then needs no change.

**13.14 [S2] Grammatical subject missing (1120 att).** The sentence is "...all at the second trap in slow creep), which a replay this small reveals as ill-conditioning of that implementation (class N) and base forward claims on RVO2." Nothing can serve as the subject of "base". Replacement: "...all at the second trap in slow creep). A replay this small reveals ill-conditioning of that implementation (class N), so forward claims use RVO2."

**13.15 [S2] Precision of σ\*, b\* and the fold threshold.**
- σ\* is printed to four decimals: 1123 "$\sigma^\ast=0.0467$\,m/s". The σ50 it is inverted from carries ±0.003 (1071 "0.044 [0.041, 0.047]").
- b\* is printed to four decimals: 1103 "0.0223" and 1105 "0.0091". The fold range is given to three (1051 "0.001 and 0.038 (median 0.016)").

If these are the values the runs used, say so and keep them [TASTE: a set parameter versus an estimate]. Replacement at 1123: "gives $\sigma^\ast=0.047$\,m/s (runs use 0.0467)". C41 records the value, not the printed precision.

**13.16 [S3] Overprecise or floor values printed as measurements.**
- 1051 phys "rank correlation 0.9996" → "rank correlation above 0.99".
- 1111 att "largest first-exit shift 0.000 s in 300" → "(identical first-exit times in all 300)".
- 1136 att "$p=1.000$ and 1.000" → "$p=1$ for both".
- 1096 T3 "$-4.8\times10^{-3}$". Scientific notation for a non-p quantity, which C40 reserves for small p-values, and inconsistent with the "$|\ell|\le0.018$" form at 1117 → "$-0.005$".

**13.17 [S3] Mixed precision for one kind of bound.** Wilson bounds:
- 1051 phys "(Wilson lower bound 0.969)" has three decimals.
- 1035 "(lower bound 0.96)", 1056 "0.13", 1114 "0.10" and 1157 "0.13" have two.

1051 → "(Wilson lower bound 0.97)".

**13.18 [S3] Counts and proportions mixed in one clause.**
- 1035 phys: "70 at 0.9 m (Wilson 95%: 0.60--0.78) and 100 at 1.0 m (lower bound 0.96)" → "70 of 100 at 0.9 m (0.70 [0.60, 0.78]) and 100 of 100 at 1.0 m (Wilson lower bound 0.96)".
- 1157 val: "(completion 0 and 1, upper Wilson bound 0.13, ...)". The bound belongs to 0/25 only. → "(completion 0 of 25, upper Wilson bound 0.13, and 1 of 25, against 5 of 5 human runs)".
- 1056 phys: "(0 of 25 runs, upper Wilson bound 0.13)" is acceptable.

**13.19 [S3] Mixed significant figures inside one range.** 1053 phys "0.06--1.1 J (median 0.21 J)" → "0.06--1.10 J (median 0.21 J)".

**13.20 [S3] Percentile ranges look like intervals.** The paper's rule is that all intervals are 95%.
- 1033 phys "(5--95%: 141--304 N)" → "(5th--95th percentiles: 141--304 N)".
- 1026 phys caption "bands show the 5--95% range" → "bands show the 5th--95th percentiles".
- 1056 phys "(95% within 0.6 s)" → "(95% of them within 0.6 s)".

**13.21 [S3] Triplets missing a member.**
- 1067 phys: "median attempt rates are 0.13 s$^{-1}$ (full) and 0.09 s$^{-1}$ (alone)". The pinned (frozen) condition is missing; add it or say why it is not reported.
- 1029 phys: "83, 156 and 543 N at r = 0.20, 0.25 and 0.35 m". Fig 2 (1026) plots four radii including 0.30; add the 0.30 value.
- 1053 phys: Weibull shapes "2.3" and "2.8" carry no interval, while 1067 "1.09 [1.05, 1.14]" and 1123 "0.64 [0.58, 0.70]" do. Add intervals.

**13.22 [S3] Units dropped mid-list.**
- 1049 phys "(median 94)" → "(median 94 N/m)".
- 1157 val "the model variants 0.54--0.81, with the short one 1.58 and 0.62--0.91" → "0.54--0.81 ped/s ... 1.58 ped/s and 0.62--0.91 ped/s".

**13.23 [S3] Subjects that do not match their verbs.**
- 1008 sig: "The blocker's realised velocity variance over Eq.~\eqref{eq:teff} is 1.00" reads as a variance taken over an equation. → "The ratio of the blocker's realised velocity variance to Eq.~\eqref{eq:teff} is 1.00".
- 1071 phys: "The same physics sets the noise level a whole run needs." The paragraph only reports a logistic fit and links nothing to the barriers. → "Whole runs need a noise level of the same order."
- 1166 disc: "The signatures also say why the rates coincide." The rates coincide because the controls were tuned to them (1020). → "The signatures also say what each matched rate is made of."
- 1157 val: "Noise turns deadlocks into long stalls and lowers the flow further" (further than what?) → "...and lowers the flow below every deterministic variant (ratio 0.40)".

**13.24 [S3] Quantifier clash (1053 phys).** "below 1 at every noise level we ran for most snapshots". See 12.2 for the replacement.


---

## 14. Structural and framing problems

### Block W: whole paper

**14.1 [S1] The protocol is buried in the wrong subsection.** "Calibrate, then falsify" (1019-1020) is the paper's Method contribution (834). It sits as the last paragraph of §4.3 "Collective Activated Escape", after the string-method gate. A reader looking for the protocol from the contributions list lands in a numerics subsection.

Reordering: move lines 1019-1020 to directly after 981, before §4.1, so §4 opens with classes, then the protocol, then the physics that supplies the predictions. Apply the 13.2 fix to step (2) at the same time. No forward reference is created, because the protocol cites only Table 2.

**14.2 [S1] §5 order forces forward references.** §5.2 (pair standoff) uses §5.4 twice before it exists:
- 1053: "The string method of Sect.~\ref{sec:escape}"
- 1053: "the Arrhenius test of Sect.~\ref{sec:escape}"

§5.4 is about the lone trap (1065: "whether noise frees the lone trap thermally"). Reordering: 5.1 The Lone Trap at the Door Edges; 5.2 Noise as Collective Activated Escape (current 5.4); 5.3 The Pair Standoff (current 5.2); 5.4 No Persistent Contact Arches (current 5.3). After this both 1053 references point backwards, and the lone-trap barriers needed for 13.9 appear before the pair comparison. The two forward pointers in 1035 to the pair section ("(Sect.~\ref{sec:pair})" ×2) remain and are acceptable.

**14.3 [S1] Whole-run attribution sits under "6.1 The Lone Trap".** The paragraph "Matched completion of whole runs" (1122-1123) reports E6 whole runs, which hold lone traps, second traps and group standoffs (1123 classes). Placing it under the lone-trap heading tells the reader it is a lone-trap result.

Reordering:
- 6.1 The Lone Trap (1110-1120);
- 6.2 The Pair Standoff (current 6.2, 1125-1136);
- 6.3 Whole Runs (current 1122-1123);
- 6.4 Revisiting the Conference Findings.

Reorder Table 3's blocks to lone, pair, whole runs to match. "The second trap and the published solver" (1120) then leads straight into the pair subsection, as C26 intends. The back-reference at 1133 ("This is the second-trap response of Sect.~\ref{sec:att-lone}") stays valid.

**14.4 [S1] The thesis is stated four times in near-identical words.**
- 653 abs, sentence 2: "A control that shares none of its machinery, tuned to reproduce its completion rate, shows only that a simpler cause would suffice."
- 830 intro: "A matched control shows that a simpler cause suffices for the score, not that the paradigm and the control act in the same way". 832 restates it immediately ("Our thesis is that matching a control ... is not evidence of a shared mechanism").
- 1163 disc: "A matched control shows whether a simpler cause suffices for the paradigm's score".
- 1177 concl: "A control matched to a paradigm's completion rate shows that a simpler cause would suffice, not that the paradigm uses it."

Fixes:
- Introduction: keep 832 and replace the last two sentences of 830 ("The principle stops short. A matched control shows ... cannot separate them.") with the one fact the thesis needs: "Two physical processes can produce the same completion rate."
- Discussion: open 1163 with the result, not the thesis: "In all three matches the control reproduces ORCA's rate within its interval: ..."
- Conclusions: keep 1177's first sentence. It is the closing statement.

**14.5 [S2] The practitioner advice appears twice and the second copy cites the wrong section.**
- 1160 val (second point): "Before deadlock statistics at a narrow door are read as crowd behaviour, $g_{\max}(r)$ should be compared with $m v_0/\tau$ over the agent population".
- 1169 disc (first point): "a deadlock rate at a narrow door should be read against the stuck-alone margin before it is read as crowd behaviour", citing "(Eq.~\eqref{eq:stuck}; Sect.~\ref{sec:validity})".

The evidence that the trap is a property of the jamb law is §5.1 (Fig 3), not §7.

Reordering: move the whole "Wall treatment at door edges" paragraph (1159-1160) into §8 "Implications for model users" as its first three points. Delete 1169's first point. Renumber 1169's "Second" and "Third" as fourth and fifth. In the moved text, change the citation to "(Eq.~\eqref{eq:stuck}; Sect.~\ref{sec:lone}, Fig.~\ref{fig:width})". §7 then ends on its results paragraph (1157).

**14.6 [S2] "Five mechanism classes" but Table 2 shows four.** The contributions (834) and the back matter (1179) say five classes, each predicting responses "(Table~\ref{tab:signatures})". Table 2 has rows P, L, T, D. N appears only in the caption (929). Add a row after D (T2): `N & --- & --- & --- & --- & --- & --- & disappears \\`. Then delete the caption sentence "N (glitch) is tested only by corrected numerics, under which its effect disappears."

**14.7 [S2] The §5.1 mega-paragraph (1035) carries five results.** They are the criterion test, the keystone outcomes, whole-run completion, the width sweep, and the wall-law sweep with type changes. Split it into three paragraphs:
1. from "The criterion is exact" to "in the published mode";
2. from "The trap is a property of the door geometry" to the critical width (Fig 3 left);
3. from "The jamb law decides" to the end (Fig 3 right).

This needs no new text.

**14.8 [S2] Process and pre-registration framing (drift from C6).**
- 854 bg: "predicted from the physics of each mechanism class before they are measured" → "predicted from the physics of each mechanism class".
- 1163 disc: "The held-out signatures, derived from the physics before the runs, reject that reading each time." → "The signatures derived from the physics reject that reading each time."

C6 bars pre-registration framing. A reader also cannot verify "before".

**14.9 [S2] One paragraph states the forward-claim rule twice (923 model).** First: "Results of social force models depend on the integration scheme~\cite{koster2013}, which is why the forward claims use a corrected update." Last: "The published-reproduction mode only explains published numbers; every forward claim uses the corrected-forward mode (Table~\ref{tab:params}, bottom)." Delete ", which is why the forward claims use a corrected update" from the first sentence. The last sentence carries the claim and the table pointer, and C39 only requires the citation at this point.

**14.10 [S3] The validity result is stated four times with the same numbers** (653 abs, 837 intro, 1157 val, 1177 concl, all "0.40--0.59"). Abstract, section and conclusion are expected. The intro bullet should say what the comparison adds instead: "Rebuilt like for like around the CroMa bottleneck experiments, every model variant flows in bursts separated by gaps of 5.7 s or more, where people never wait longer than about 2 s (Sect.~\ref{sec:validity})."

**14.11 [S3] A result statement in Background (848 bg).** "Our noise is injected into a damped velocity recursion, and its effective temperature follows exactly from that recursion (Sect.~\ref{sec:teff})." This is the paper's own result and is already stated in §4.2. Delete the sentence. The §4.2 subsection title carries it.

**14.12 [S3] The headings of §5.2 and §6.2 name the same object differently** ("The Symmetric Pair Standoff" / "The Pair Class"), while §5.1 and §6.1 differ in a similar way ("The Lone-Agent Trap at the Door Edges" / "The Lone Trap"). Use parallel headings, each naming its job: §5.1 "The Lone Trap at the Door Edges", §5.3 "The Pair Standoff", §6.1 "Attribution at the Lone Trap", §6.2 "Attribution at the Pair Standoff", §6.3 "Attribution in Whole Runs".

Checked with no defect found:
- the paper ends on Conclusions, not limitations;
- a recommendation is stated (1160/1169, 1172);
- the novelty claim (854 "We have not found an earlier study") is phrased as a search result, not overreach;
- there are no results in related-work subsections other than 14.11.


---

## 15. Spelling and convention consistency

### Block W: whole paper

**15.1 Spelling: British is dominant; pick British.**
- British forms used: colour (822), Colours (1129), neighbour(s) (822, 842, 863, 916, 1017 ×2, 1062, 1067, 1120 ×3, 1151), normalised (1077), discretised (848), characterised (851), modelling (854), behaviour (1160, 1169), artefact (981), analysed (851), centre (822, 898), metres (1042), favours (1051), realised (1008), grey (822 ×2, 1026, 1042 ×2, 1129, 1148).
- Deviations to change:
  - 1047 phys "pushed toward the door" → "towards"; "sideways toward the axis" → "towards". The paper uses "towards" at 826, 842, 890 and 920.
  - "vermillion" at 1062 (phys), 1077 (att, ×2), 1083 (att) and 1148 (val) → "vermilion", the dictionary spelling, already used at 822 (F1cap). [TASTE]: the Okabe-Ito palette documentation and FINAL_PLAN l.289 spell it "vermillion". Either way, use one spelling.
- "linear program" (828, 842, 1120, 1169) is the mathematical term in both varieties. Keep it.
- Bibliography titles keep their published spelling (Grimm 2005 "modeling").

**15.2 Minus sign versus hyphen.** Negative macros typeset outside math mode print a hyphen:
- 1067 phys "slope \EfourCollapseSlope\" renders "-0.93" → "$\EfourCollapseSlope$";
- 1163 disc "[\EsixDiffLo, \EsixDiffHi]" renders "[-0.10, 0.08]" → "[$\EsixDiffLo$, $\EsixDiffHi$]".

Every other negative macro is already in math mode.

**15.3 Interval notation: brackets dominate.** Bracket form "[lo, hi]" appears at 1037, 1067, 1071, 1117, 1123, 1154, 1157 and in Table 3. Two instances use the "label: lo--hi" form:
- 1035 phys "(Wilson 95\%: \EsevenWNineLo--\EsevenWNineHi)" → "(0.70 [0.60, 0.78])" (see 13.18);
- 1035 phys "(bootstrap 95\%: \EsevenWcritLo--\EsevenWcritHi)" → "\EsevenWcrit\ [\EsevenWcritLo, \EsevenWcritHi]\,m (bootstrap)".

Keep the en dash for min-max ranges only.

**15.4 Thousands separator.**
- 1033 phys "\StuckAloneN" renders "20000".
- 1026 phys caption "20\,000".

Use "20\,000": format the macro in the registry, or write "20\,000" at 1033.

**15.5 Powers of ten.** Bare powers dominate: $10^{-4}$ (913, 997), $10^{-9}$ (939, 981, 1087, 1111, 1120, 1169), $10^{-3}$ (926), $10^{6}$ (874). A leading "1×" appears at:
- 866 T1 "$1\times10^{-8}$";
- 1001 sig and 1049 phys "\ResidPairMax" (renders "1×10⁻⁷").

866 → "$10^{-8}$" (or the 12.44 replacement). Make \ResidPairMax render "$10^{-7}$".

**15.6 Unit spacing.**
- The body uses a thin space ("0.8\,m").
- Fig 1 caption (822, F1cap) uses a tie: "0.8~m", "0.25~m", "$\pm150$~N", "5~N", "1000~N", "$B_w=0.08$~m", "0.04~m". → "\,".
- Table 1 (862-870, T1) uses a normal space ("$m=80$ kg", "(1.34,0.26) m/s", "0.15", "U(0.4,0.6) s", "ped/m$^2$", "$A=2000$ N", "0.08 m", "kg/s$^2$", "1.5", "3 s", "8 s", "5 s", "0.5 s", "10×10 m", "[1,8]×[1,9] m", "0.8 m", "x=10 m", "(11,5) m", "0.01 s", "0.5 m", "0.01 m/s", "10 s", "±10^6 N") → "\," throughout.

[TASTE]: in a dense table a normal space is defensible. Whichever you choose, use it everywhere.

**15.7 Unit style: solidus versus negative exponent.** The solidus dominates (m/s, ped/s, N/m, kg/s$^2$, kg/(m\,s)). Exceptions:
- 1067 phys "s$^{-1}$" (×2);
- Fig 2 axis "v0/τ (m s⁻²)" (fig2).

→ "/s" and "m/s²". [TASTE]: SI style prefers negative exponents throughout. Choose one.

**15.8 Numerals and words in one sentence.** 1151 val: "The CroMa experiments include \EtenHumanN\ runs" (renders "5 runs") "..., two with a 2.0 m corridor ... and three with a 0.21 m one". → "include five runs". The paper otherwise uses words for design counts (two, three, five seeds, eight bias values) and numerals for measured counts. 1069 "with 4 residual agents" is a measured count; keep it.

**15.9 Serial comma: mixed, mostly omitted.** [TASTE]: Oxford style would add the comma everywhere instead.

Omitted (the dominant form):
- 653 abs (×2)
- 836 intro
- 845 bg
- 851 bg
- 1029 phys
- 1035 phys (×2)
- 1065 phys (×2)
- 1067 phys
- 1083 att (×2)
- 1123 att
- 1148 val
- 1154 val
- 1177 concl
- 1179 back (×2)
- 1182 back

Present:
- 828 intro "..., and a small linear program": keep, because the first item contains "and".
- 926 model "..., and times to freeing are": keep, because the items are clauses.
- 981 sig "..., and corrected numerics" → drop.
- 1017 sig "(frozen), or the blocker alone" → drop.
- 1017 sig "ends in an exit, and, when alone, matches": keep, because a parenthetical follows.
- 1035 phys "..., and with all-walls $0.02$\,m" → drop.
- 1062 phys "..., and the blocker alone dotted" → drop.
- 1087 T3 caption "..., and $\ell=$" → drop.
- 1151 val "..., and the barriers beyond the entrance" → drop.
- 1151 val "the entrance, and corridor walls" → drop.

**15.10 Naming three-author works in the text.**
- "Karamouzas et al." (842, 3 authors) and "Grover et al." (851, 3 authors).
- "Nicolas, Garcimart\'in and Zuriguel" (845, 3 authors) and "H\"anggi, Talkner and Borkovec" (848, 3 authors).

Pick "et al." for three or more: 845 → "Nicolas et al."; 848 → "H\"anggi et al.".

**15.11 Order of numeric citation lists.** The rendered lists are unsorted at:
- 826 "[20, 13]"
- 828 "[12, 11]"
- 1017 "[18, 14]"
- 1172 "[26, 22]"

Add `\usepackage{cite}` (allowed by LNCS) or reorder the keys: 826 `\cite{helbing2012,liang2024}`, 828 `\cite{helbing2000nature,helbing1995}`, 1017 `\cite{hanggi1990,kramers1940}`, 1172 `\cite{nicolas2018trap,zuriguel2014}`.

**15.12 Bibliography (1188-1351, `bib`).**

| Line | Entry | Defect | Fix |
|---|---|---|---|
| 1206 | vandenberg2011 | Title in Title Case ("Reciprocal n-Body Collision Avoidance"); no book or series ("Robotics Research", STAR 70); "p. 3–19" | Sentence case; @incollection with booktitle and series; "pp. 3–19" |
| 1252 | grover2020 | Title in Title Case; no book or series (Algorithmic Foundations of Robotics XIV, SPAR 17); "p. 294–312"; key says 2020, entry 2021 | Sentence case; add booktitle and series; "pp."; rename key (invisible, optional) |
| 1238 | gang2026 | Acronyms lowercased "sfm, ttc, and orca"; "p. 474–481"; "SCITEPRESS - Science" (hyphen) | Brace `{SFM}, {TTC}, and {ORCA}`; "pp."; en dash |
| 1294 | koren1991 | No year printed; "p. 1398–1404" | Add year = 1991; "pp." |
| 1274 | hanggi1990 | "kramers" lowercased | `{K}ramers` |
| 1311 | liang2024 | "seoul halloween" lowercased; author "WONG, S.C." in capitals | `{S}eoul {H}alloween`; "Wong, S.C." |
| 1269 | helbing2012 | "love parade" lowercased; no article number | `{L}ove {P}arade`; add "7" |
| 1213 | vandenberg2011rvo2 | "rvo2 library" lowercased; process notes printed ("library version 2.0.3 (main branch CMakeLists.txt); Zenodo record 7039667 is tagged v2.0.2") | `{RVO2}`; replace the note with "Version 2.0.3" |
| 1200-1202 | arrhenius1889 | German nouns lowercased (reaktionsgeschwindigkeit, inversion, rohrzucker, säuren); volume "4U" | Brace the nouns (Reaktionsgeschwindigkeit, Inversion, Rohrzucker, Säuren); volume "4" |
| 1196 | fzj_ped20219 | Year "(2026)" for the 2021 data record (DOI …PED.2021.9) | Year of the record; add "accessed …" if needed |
| 1220, 1227, 1288, 1307, 1324, 1349 | e2002, e2007, karamouzas2014, koster2013, nicolas2018trap, zuriguel2014 | No article number; liang2024 (1312) has one | Add 052301, 164103, 238701, 063305, 198002, 7324 |
| 1220, 1227, 1248, 1264, 1276, 1288, 1301, 1325, 1349 | e2002 (Aug), e2007 (Apr), grimm2005 (Nov), helbing1995 (May), hanggi1990 (Apr), karamouzas2014 (Dec), kramers1940 (Apr), nicolas2018trap (May), zuriguel2014 (Dec) | Month printed in 9 entries, absent in the rest | Drop `month` from these nine (LNCS style) |
| All 23 entries with `\doi{…}, \url{http://dx.doi.org/…}` | arrhenius1889, vandenberg2011, e2002, e2007, fiorini1998, gang2026, grimm2005, grover2020, helbing2000nature, helbing1995, helbing2012, hanggi1990, kaplanmeier1958, karamouzas2014, koren1991, kramers1940, koster2013, liang2024, mcnemar1947, nicolas2018trap, weibull1951, wilson1927, zuriguel2014 | DOI printed twice, the second time through the legacy dx.doi.org resolver | Delete the `url` field wherever a DOI exists (fzj, rvo2 and weidmann keep their non-DOI URLs) |
| 1335 | weidmann1993 | "ETH Zurich" | "ETH Zürich" [TASTE] |
| 1186 | — | `\nocite{gang2026}` duplicates the `\cite` at 830 | Delete |

**15.13 Capitalisation and hyphenation of defined terms (no change needed).** Checked and consistent: the title case of section headings, the sentence case of run-in paragraph heads, "Kaplan--Meier", "Savitzky--Golay", "Student-$t$", "rest state" (noun) and "rest-state" (adjective), "time step" (noun) and "time-step" (adjective), "like for like" (adverb) and "like-for-like" (adjective, 1179), "Sect."/"Sects." mid-sentence and "Sections" at sentence start (839), "Fig.", "Eq."/"Eqs.". One exception: "time-to-free" (836) is a hyphenated noun (see 12.35).


---

## 16. Anything else

### 16.0 Paper-wide reconciliation

Undefined terms recur across the blocks: "constraint part" (F16.1), "lower member" (R16.1), "easier sign" (M16.16), "the gate" (M11, W12.7), "slow creep" (R4.1). Define each once, at its first use, using the text given in the block entries.

### Block F: title, abstract, keywords, §1–§3 (main.tex 13–21, 651–926)

| # | Line | File | Quoted text | Problem and fix |
|---|---|---|---|---|
| 16.1 [H] | 836 | INT | "ORCA acts through its constraint part" | **Jargon never defined.** §3 defines "ORCA's rest drive" (920) but never the "constraint part", which the paper then uses at 1111, 1120 and 1133. Add at 920, after the rest-drive sentence: "The remainder of $w_{o,i}\mathbf F^{\rm orca}_i$, nonzero only when a half-plane binds or the agent moves, is ORCA's \emph{constraint part}." |
| 16.2 [M] | 822, 895 | F1C, MOD | "the blocker's position"; "At deadlock detection the blocker has …" | **"Blocker" is used before its definition**, which comes only at 1035 ("the blocker, the agent nearest the door"). Define it at 895 (as written in 9.4). The caption can then use it. |
| 16.3 [M] | 895, 906, 923 | MOD | "in all \TermN\ deadlocks of both modes"; "the corrected mode lets …"; final sentence of 923 | **The modes are used before the prose introduces them.** The text first names them in the last sentence of §3. Move that sentence to follow 887: "The model runs in two modes (Table~\ref{tab:params}, bottom): the published-reproduction mode reproduces the conference paper's numbers, and the corrected-forward mode, used for all new results, corrects its update, spawn, ORCA solver and wall corners." Then delete the final sentence of 923. |
| 16.4 [M] | 834 | INT | "a rest-state lemma removes from consideration every force term that vanishes at rest" | This misstates what the lemma does. Per 1001, such terms leave the fixed points and their stability unchanged and so cannot resolve a deadlock. "…and a rest-state lemma shows that no force term that vanishes at rest can resolve a deadlock (Sect.~\ref{sec:signatures})." |
| 16.5 [M] | 652 S6 | ABS | "every model variant either deadlocks or flows at \EtenCSigFlowRatio--\EtenCThreeFlowRatio\ of the human rate." | The "either … or" contradicts 1157 ("Whatever the variant, the flow, counted up to the deadlock where there is one, is …"): deadlocking variants also flow at that ratio. "Rate" has also meant completion rate in sentences 2 and 5. Replacement: "every model variant passes \EtenCSigFlowRatio--\EtenCThreeFlowRatio\ of the human flow, counted up to the deadlock where one forms." The out-of-range partner at 1177, "each deadlocks or passes", has the same defect. |
| 16.6 [M] | 652 | ABS | "ORCA's rate"; "the CroMa experiments" | Both are used unexpanded in the abstract, which must stand alone. Expand ORCA at first use (9.1). Write "the CroMa bottleneck experiments with people". |
| 16.7 [M] | 652 S2 | ABS | "A control that shares none of its machinery, tuned to reproduce its completion rate" | The antecedent of "its" reads as "a control". This is fixed in 1.6 by "the paradigm's machinery". |
| 16.8 [L][TASTE] | 652 S1 | ABS | "When adding a steering paradigm to a pedestrian model clears a deadlock that the base model keeps, is the paradigm the reason?" | "Keeps" is the wrong verb for a deadlock. The rhetorical-question opening is a taste call; the competing convention, a declarative first sentence, is the LNCS norm. Replacement: "Adding a steering paradigm to a pedestrian model can clear a deadlock that the base model cannot; we ask whether the paradigm is the reason." |
| 16.9 [L] | 652 S4 | ABS | "a lone agent held by the wall force at the door edges, and a symmetric pair standoff" | The list is not parallel (an agent against a standoff). Write "a lone-agent trap, set by the wall force at the door edges, and a symmetric pair standoff, …", which matches 835. |
| 16.10 [L] | 830 | INT | "pairing a failure-mode ablation with a minimal control" | "Failure-mode ablation" is the conference paper's term and is undefined here. "pairing a failure-mode ablation, which switches paradigms on and off and records each configuration's failures, with a minimal control". |
| 16.11 [L] | 830 | INT | "The principle stops short." | It is unclear what the principle stops short of. Fixed in 1.3. |
| 16.12 [L] | 851 | BKG | "the question of which one a given resolver resembles is the same question in both fields" | "Question … same question" is a repetition, and the clause adds nothing. Deleted in 10.3. |
| 16.13 [L] | 863, 895 | MOD | "$\rho$ = neighbours within $R=3$ m over $\pi R^2$"; "$N_i$ the other active agents within $R$" | A density is a count over an area. Write "number of neighbours" and "the number of other active agents" (also in 4.3). |
| 16.14 [L] | 842 | BKG | "so that the new velocity is the solution of a two-dimensional linear program nearest to the preferred velocity" | **Misplaced modifier**: as written, "nearest" modifies "program". "…so that the new velocity solves a two-dimensional linear program: it is the permitted velocity nearest to the preferred one~\cite{vandenberg2011}." |
| 16.15 [L] | 923 | MOD | S1 "…which is why the forward claims use a corrected update" and final sentence "…every forward claim uses the corrected-forward mode" | The same point is made twice in one paragraph. Keep one (6.2) and move the other (16.3). |
| 16.16 [L] | 863 | MOD | Table 1 "Speed–density" row repeats Eq. 2 in full | The table and the text both carry the formula. Replace the formula in the table with "Weidmann, Eq.~\eqref{eq:des}; $\gamma=1.913$, …". This saves two table lines toward the page budget (plan C54). |
| 16.17 [L] | 866 vs 913; 870 vs 926 | MOD | "pair counted only if $|\Delta v|^2\ge1\times10^{-8}$" vs "$|\Delta\mathbf v|\ge10^{-4}$\,m/s"; "deadlock: all $|v|<0.01$ m/s for 10 s" vs 926 | The same specifications appear twice, once in squared form. State each once: keep the text forms (913, 926), and in the table refer to them or keep only the table forms. |
| 16.18 [L] | 874 | MOD | "semi-implicit Euler, then clamp; force clip $\pm10^{6}$ N" vs "clamp, then position update; no clip" | The cells are not parallel. Both modes are semi-implicit Euler; they differ in where the clamp sits. Write "velocity and position update, then clamp; force clip $\pm10^{6}$ N" against "velocity update, clamp, then position update; no force clip". |
| 16.19 [L] | 877 | MOD | "leg normal sign-flipped outside the obstacle; infeasible constraints dropped" | "Leg normal" is undefined, code-level geometry. Name the effect, e.g. "half-plane normal reversed when the relative position lies outside the obstacle cone". The authors should confirm the wording against the solver. |

**Handoffs to the categories 12, 13 and 15 auditor** (not counted here):
- $\sigma(\rho;4,2)$ in Table 1 (867–868) vs $s(\rho;4,2)$ in Eq. 6 and at 920, with $\sigma$ also used for the noise standard deviation.
- $\tau$ overloaded across $\tau_i$, $\tau_{ij}$, $\tau_0$, $\tau_h$ and $\tau_{\rm ORCA}$.
- "corrected mode" vs "corrected-forward mode".
- "jammed" (828) vs "deadlocked".
- "time-to-free" (836) vs "times to freeing" (926).
- "social-force bottleneck" (832) vs "social force model".
- "vermilion" (822) vs "vermillion" (1062, 1083, 1097, 1148).
- "to within 1%" (895) where the bound 0.994 gives 0.6%.

### Block M: §4–§5 (main.tex 927–1071)

| # | Line / file | Quoted text | Problem and replacement | Sev |
|---|---|---|---|---|
| 16.1 | 1053 [S5] | "The string method of Sect.~\ref{sec:escape}" | This points to §5.4, but the method is defined in §4.3 (1017), which has no label. Add `\label{sec:barrier}` to §4.3 and write "The string method of Sect.~\ref{sec:barrier}". | H |
| 16.2 | 1035 [S5] | "it stayed held in exactly the cases with positive margin, \CriterionAgree\ of \CriterionN." | "393 of 393" reads as "all stayed held", which the next sentence (7 negative margins) seems to contradict. Write: "the blocker's outcome matched the sign of its margin in \CriterionAgree\ of \CriterionN: the [386] with positive margin stayed held and the \CriterionNegMargin\ with negative margin did not." | H |
| 16.3 | 988 [S4] | "and the rest $\mathbf G$, with $\mathbf G(\mathbf x,\mathbf 0)=\mathbf 0$." | In a subsection about rest states, "the rest" reads as "the at-rest term", the opposite of what $\mathbf G$ is. Write "and the remainder $\mathbf G$, which vanishes at rest, $\mathbf G(\mathbf x,\mathbf 0)=\mathbf 0$." | M |
| 16.4 | 1008, 1017, 1029 [S4/S5] | "The blocker's realised velocity variance", "(blocker past the door plane)", "the blocker's Weidmann factor" | "Blocker" is used from 1008 on (and at 822 and 895) but defined only at 1035 ("the blocker, the agent nearest the door"). Move the definition to its first use in §3 (line 895) and delete it at 1035. | M |
| 16.5 | 1035 [S5] | "Rounding the jamb corners or replacing the exit by a line goal does not remove it (\EsevenRoundK, \EsevenLineK\ and \EsevenLineRoundK\ of \EsevenN; …)" | Three numbers follow two named variants, so the reader cannot map the third. Write "Rounding the jamb corners, replacing the exit by a line goal, or both does not remove it (\EsevenRoundK, \EsevenLineK\ and \EsevenLineRoundK\ of \EsevenN\ complete; rounded against default $p=\EsevenRoundVsDefaultP$)." | M |
| 16.6 | 1037 [S5] | "predicts whether it exits with an area under the ROC curve of …, against an all-exit baseline accuracy of …" | This is a garden path ("exits with an area"), and it compares an AUC with an accuracy. Write "…predicts whether it exits (area under the ROC curve \EOneBAUCOthers\ [\EOneBAUCOthersLo, \EOneBAUCOthersHi]). Predicting that every stuck-alone agent exits is right for \EOneBAllExitBaseline\ of them." | M |
| 16.7 | 1037 [S5] | "with no such agent left," | The antecedent of "such" is two clauses back. Fixed by 1.7. | L |
| 16.8 | 1017 [S4] | "Kramers theory predicts…: …; and, since the neighbours can move out of the way, the full barrier lies below the alone barrier." | The third prediction is a property of the landscape, not of Kramers theory. Fixed by 9.5. | M |
| 16.9 | 1014 [S4] | "and absent for a deterministic resolver." | $\ell$ is a number; "absent" has no value. Write "and zero for a deterministic resolver, whose rate does not depend on $\Delta t$," to match Table 2, row L. | M |
| 16.10 | 981 [S4] | "T, heat: it adds fluctuations; the fixed point survives and is left over a barrier $\Delta U$" | The fixed point cannot "be left" in the passive voice with the subject unstated. Write "the fixed point survives, and the crowd leaves it over a barrier $\Delta U$ at a rate set by $\Delta U/k_BT_{\rm eff}$." | L |
| 16.11 | 1035 [S5] | "sorts the corrected-forward deadlocks into three classes" and "The class of the remaining deadlocks changes with the law." | "Class" already means mechanism class (P, L, T, D, N) from 981. Use "type" for deadlock geometry here. The full term table is for the terminology audit. | M |
| 16.12 | 990 and 1001 [S4] | "\begin{proposition}[rest-state lemma]" and "The lemma covers the noise-free model only." | A Proposition is titled "lemma" and then called "the lemma". Either retitle it "[rest-state proposition]" and write "Proposition~\ref{prop:rest} covers the noise-free model only.", or make it a `lemma` environment. | L |
| 16.13 | 1001 and 1049 [S4/S5] | "$\ResidPairMax$\,N over the \ResidPairN\ pair snapshots" and "(largest residual \PairResidMax\,N)" | The same residual is stated twice. Keep it at 1049, where it is used, and drop the pair clause from 1001. | L |
| 16.14 | 1008 [S4] | "realised velocity variance over Eq.~\eqref{eq:teff}" | "over" means "divided by". Write "the ratio of the blocker's realised velocity variance to Eq.~\eqref{eq:teff}". | L |
| 16.15 | 1049 [S5] | "(median \PairLamOneMed)" and "by 1\,cm \PairDeltaOneCmFreed." | A unit is missing (N/m), and the gapped "by 1 cm 1" forces a reread. Fixed by 9.14 and 1.11. | L |
| 16.16 | 1051 [S5] | "for the easier sign" | Undefined. Write "for the sign with the lower threshold". Fixed by 9.16. | M |
| 16.17 | 1056 [S5] | "up to \ArchSizeMax)" | The unit is missing; "up to 10" does not say ten what. Write "at most \ArchSizeMax\ agents". Fixed by 9.21. | L |
| 16.18 | 1056 [S5] | "None lasts 10\,s (…)" | Redundant after "they break within \ArchMaxLife\,s". Merged by 9.21. | L |
| 16.19 | 1065 [S5] | "spread over the collective barrier" | Snapshots cannot be spread over one barrier. Write "chosen to span the range of collective barriers". The same phrase recurs at 822 in §6, outside range. | L |
| 16.20 | 1067 [S5] | "a line of slope \EfourCollapseSlope\ against" | The macro is in text mode and renders a hyphen ("-0.93"; p-13). Line 1053 renders a true minus ($\PairBarSpearman$ gives −0.24). Write "$\EfourCollapseSlope$". | L |
| 16.21 | 1069 [S5] | "Two snapshots are reported separately. In one, the full barrier, \EfourSkippedDU\,J, …" | The paragraph does not say whether these two are among the \EfourN\ of 1065. CHANGELOG C18 and C29 suggest the first is not and the second is, which is why the full condition has \EfourFitsFull\ fits rather than 10. State it: "One of the \EfourN\ snapshots, and one candidate that was not admitted, are outside the fits." Also delete "(\EfourSeedOneSeventyEvents\ events)", which repeats "none … escapes". | M |
| 16.22 | 1071 [S5] | "The same physics sets the noise level a whole run needs." | "The same physics" has no clear antecedent, and the paragraph measures $\sigma_{50}$; it does not derive it from barriers (that link is in §6, line 1123). Delete the sentence and open with "For whole runs, the noise amplitude at which half of the runs complete is …". | M |
| 16.23 | 1035 [S5] | "(published mode: \KeystoneALone, \KeystoneASecondTrap\ and \KeystoneACollective)" | A parenthetical inside a list clause, carrying a second dataset. Fixed by 9.9. | L |
| 16.24 | 1051 [S5] | "Because the minimum is strict, it survives small tilts and disappears at a fold" | [TASTE] This repeats 981 nearly verbatim ("a strict minimum survives small biases and disappears at a fold"). The competing convention restates a definition at the point of application, which is defensible. If kept, say "As class D predicts (Sect.~\ref{sec:signatures}), …" so the echo reads as intended. | L |
| 16.25 | 1019-1020 [S4] | placement of "Calibrate, then falsify." | The protocol paragraph sits inside §4.3 (barriers), so a reader looking for the attribution method will not find it under that heading. See 7.4. | M |

Also checked, with nothing to report: equation-adjacent prose of Eqs. (7)-(11) (variables defined before or at use, apart from 16.3 and 16.12); the proof text (994); in-figure text (Figs. 2-4 carry only axis and tick labels, consistent with the no-in-figure-text rule); and the Table 2 cell wording (consistent with 981, apart from 8.1).

### Block R: §6–§9, Main Differences, Data and Code Availability (main.tex 1072–1183)

| # | Line, file | Sev | Text | Problem | Fix |
|---|---|---|---|---|---|
| 16.1 | 1087, 1092 [T3]; 1136 [06] | H | "first exits by the lower member" / column "Lower first" / "at $-b^\ast_{\rm pub}$ the other member exits first" | "Lower member" is never defined. "The other member" has no antecedent. The handedness signature, which is one of the paper's three separating probes, cannot be read. | Name the members where they are introduced, at line 1047 (§5.2): "Two agents stand in front of the two jamb faces, one on each side of the door axis (the lower and the upper member), …". Then write at 1136: "Under $+b^\ast_{\rm pub}$ the lower member exits first in 22 of 22 freed standoffs; at $-b^\ast_{\rm pub}$ the upper member exits first in 21 of 21." |
| 16.2 | 1120 [06] | M | "all at the second trap in slow creep" | "Slow creep" is undefined. | "all at the second trap, while the agents creep slowly toward the door" |
| 16.3 | 1120 [06] | M | "The constraint part from its half-plane" | "Its" could be the neighbour's, the blocker's or ORCA's. | "The constraint part from the neighbour's half-plane" |
| 16.4 | 1114 [06] | L | "matches that rate" | "That rate" refers back across a paragraph break. | "matches C3 RVO2's lone-keystone rate" (in 1.1). |
| 16.5 | 1114 [06] | M | "and it waits." | Vague. It means a slower Kaplan–Meier median, a number given only in Table 3. | "and it is slower (Kaplan--Meier median 19.8\,s against 1.5\,s)" (in 1.1). |
| 16.6 | 1120 [06] | L | "a trapped neighbour abreast of the blocker across the axis, \CtwsixGapMin--\CtwsixGapMax\,m away surface to surface" | "Abreast … across" stacks two spatial prepositions, and "away surface to surface" is clipped. | "a trapped neighbour beside the blocker on the other side of the door axis, with a surface gap of 0.27--0.32\,m" |
| 16.7 | 1133 [06] | L | "This is the second-trap response of Sect.~\ref{sec:att-lone}." | "Response" is vague. | "The same opposition holds ORCA back at the second trap (Sect.~\ref{sec:att-lone})." |
| 16.8 | 1136 [06] | L | "Both matches reproduce the rate (Table~\ref{tab:matched}; $p=\PairBsPubP$ and \PairBsRvoP)" | The test is unnamed, and "1.000 and 1.000" reads as a typo. | "Both matches reproduce the rate (exact McNemar $p=1.000$ for both; Table~\ref{tab:matched})" |
| 16.9 | 1136 [06] | L | "reading $b^\ast$ per solver off the fold curve" | "Fold curve" is a new name for the static fold prediction of §5.2. | "reading $b^\ast$ per solver off the static fold prediction of Sect.~\ref{sec:pair} (the step line of Fig.~\ref{fig:pair})" |
| 16.10 | 1163 [08] | M | "noise at $\sigma^\ast$ completes whole runs at its rate" and "a bias at $b^\ast$ frees pair standoffs at the rate of either solver" | "Its" refers to ORCA, two clauses back. "At $b^\ast$ … either solver" suggests one bias matches both solvers, but there are two $b^\ast$ values. | "at ORCA's rate"; "a bias at $b^\ast_{\rm pub}$ or $b^\ast_{\rm RVO2}$ frees pair standoffs at the rate of the matching solver" (or the pointer in 3.7). |
| 16.11 | 1163 [08] | M | "each control fails a probe of its own class" | This inverts the meaning: the control passes its own class's signature, and ORCA lacks it. | "each control shows the signature of its own class, which ORCA lacks" (in 3.7). |
| 16.12 | 1163 [08] | L | "($\Delta=\TabThreeLKDiff$)" and "($\Delta=\EsixDiff$ [\EsixDiffLo, \EsixDiffHi])" | Rendered as "(∆ = −0.01 [-0.10, 0.08])": the lower bound prints a hyphen, not a minus, because its macro sits outside math mode. The first Δ also has no interval while the second has one. | "$\Delta=\TabThreeLKDiff$ [$\TabThreeLKDiffLo$, $\TabThreeLKDiffHi$]" and "$\Delta=\EsixDiff$ [$\EsixDiffLo$, $\EsixDiffHi$]" |
| 16.13 | 1166 [08] | L | "At rest ORCA's velocity is a second goal drive that pushes …" | A velocity is not a drive. Elsewhere the paper says "ORCA's rest drive" (lines 1033, 1111). | "At rest ORCA adds a second goal drive, its rest drive, that pushes …" |
| 16.14 | 1166 [08] | M | The mechanism list (class L for ORCA, T for noise, D for the bias) | It omits ORCA's pair mechanism, which §6.2 and line 1177 both state. The parallel breaks, and the paragraph reads as if ORCA acts only at the lone trap. | After "(class L).", add: "At the pair it acts through its constraint part, differently in each solver." |
| 16.15 | 1169 [08] | M | "…before it is read as crowd behaviour" | Duplicates line 1160 (see 1b). | Cut per 1.10. |
| 16.16 | 1172 [08] | L | "by the activated escape that trap models assume" | "Trap models" is not tied to a source. | "by the activated escape that the trap model of~\cite{nicolas2018trap} assumes" |
| 16.17 | 1172 [08] | L | "Wherever a resolver is credited with removing an equilibrium" | "Resolver" is a new name for what the paper calls a paradigm. | "Wherever a paradigm is credited with removing an equilibrium" |
| 16.18 | 1157 [07] | L | "No agent leaves the walkable area in any run." | An orphaned sanity check, placed between the fluctuation and corridor results. | Move it to the end of the set-up at 1151 ("No agent left the walkable area in any model run."), or delete it. |
| 16.19 | 1175 [08] | M | "Samples are finite: \PairN\ pair standoffs cannot show rate equivalence within $\pm0.10$." | "Samples are finite" says nothing. The $\pm0.10$ margin is internal under C6 (see 4.5). | "The pair library has 46 standoffs, so the 95\% intervals of the matched rate differences are wide ($[-0.15, 0.22]$ and $[-0.13, 0.17]$)." |
| 16.20 | 1117 [06] | L | "Noise scaled with $\sqrt{\Delta t}$ removes the effect" | "The effect" refers back two sentences. | "Noise scaled with $\sqrt{\Delta t}$ removes the time-step dependence" |
| 16.21 | 1148 [07] / Fig 8 | L | Tick labels "C1 published", "C1", "C1 jamb $B_w$" against the text's "corrected-forward" and "corrected-forward with … $B_w=0.04$\,m" | Naming drift between figure and text. Referred to the category-12 auditor. | Category-12 auditor to choose the names; no replacement given here. |

Also checked, with no defect found: the Data and Code Availability paragraph (1182), the Limitations paragraph's first sentence apart from 4.10, the §7 variant list (1151, fifth sentence), and the "Clogging and robot deadlock" paragraph apart from 16.16 and 16.17.


---

## Triage: the five changes that most improve how a skeptical reviewer reads this paper

1. **Untangle the vocabulary and the symbols** (W12.1–12.7, W12.13, W13.1, W14.6).
   - Deadlock *types*, keystone *outcomes* and mechanism *classes* each get their own word. The keystone outcome becomes "group standoff"; the barrier condition becomes "pinned".
   - λ₁ becomes μ₁, and the fold threshold $b_f$ is kept apart from the matched $b^\ast$.
   - $B_{w,\rm edge}$ is used for the jamb-only variant.
   - "Five classes" is reconciled with Table 2.

   This removes the two-against-three-classes contradiction that a reviewer meets in the abstract and again in §5.1. About 2 h, including the Figs 3, 4, 6, 7 and 8 tick and axis labels.
2. **Rewrite the abstract and collapse the repeated thesis** (F1.1–F1.6, F9.1, F16.5, F16.6; R1.8, R1.9, R1.12, R1.13; W13.2).
   - Split abstract sentence 5 and expand ORCA and CroMa.
   - Remove "either deadlocks or".
   - State the matched quantity as "rate".
   - Turn the 828–832 cascade into positive statements, and leave the negated thesis only where it carries its reason.

   About 1 h 15 min.
3. **Fix the seven statements that read as wrong** (item 6 of section 0: M16.2, M5.1, M4.1, R9.16/W13.4, W13.5, W13.6, W13.3). A reviewer who catches one starts doubting every number. About 45 min, of which about 15 min is registering two new macros (the lone-trap barrier range and the maximum human gap).
4. **Define every undefined term and strip the process vocabulary** (F16.1–16.3, R16.1, M16.16, M11, R4.1; F11, M11, R11, W14.8).
   - Define the constraint part, blocker, modes, lower member, easier sign and gate.
   - Remove "declared", "forward claims", "arm", "held-out", "before the runs" and "stated rather than fixed".
   - Remove E2/E3/E6/E7b from Table 3 and the yaml path from Table 1.

   About 50 min.
5. **Rewrite the worst sentence, split the worst paragraph, and cut the captions to the rule.**
   - Line 1120 (section 0).
   - Paragraph 1035 split into three (M).
   - Fig. 1 caption cut to about 85 words (F8.1, coordinated with the hero sessions).
   - Table 2, Table 3 and Figs 5, 6 and 8 brought to two sentences (M8, R8).
   - The seven result-stating headings replaced (R7, M7.1).

   About 1 h 30 min.

Total: about 6 h of writing. The structural reorders in W14.1–14.3 (protocol to the head of §4; §5 and §6 order) come next, if the page budget allows.
