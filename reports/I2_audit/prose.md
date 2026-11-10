# I2 prose audit

Scope: `paper/main.tex` and everything it inputs (sections 00 to 09, Tables 1 to 3, the protocol figure, all captions). Fig. 1 caption approved as is. Back-matter `\pending` items ignored. Standard: `lnns-launch/waveA/prose_prompt.md`, plus the project vocabulary list.

Line numbers refer to the `.tex` source. Paths are relative to `paper/`. Values quoted in brackets come from the rendered `main.pdf` (24 pages).

Column key:
- **Sev**: high, med or low.
- **T/E**: E means a defect. T means taste; the competing convention is given in the entry.
- **Len**: effect on length. − is shorter, 0 is neutral, + is longer. A + entry pairs with a − elsewhere, and the pairing is named.

Highest-leverage categories come first: vocabulary, then 3, 8, 1, 5 and 12, then the rest in the standard's order.

---

## V. Project vocabulary violations

The source contains none of: calibrate-then-falsify, control or matched control, intervention, arm, treatment, trial, endpoint, placebo, efficacy, held out, pre-registered, decision rule, C1–C4 (they appear only inside macro names, never rendered), or published-reproduction / corrected-forward / "mode" in the sense of run modes.

| # | file:line | Quoted text | Replacement | Sev | T/E | Len |
|---|---|---|---|---|---|---|
| V1 | sections/01_introduction.tex:9 | `Our earlier work tested such a credit with a surrogate tuned to a mechanism's headline rate~\cite{gang2026}; here we test the mechanism.` | Delete the sentence. Move the citation into the ordinary-citation slot at 02_related_work.tex:15: `...the rival explanation is a rate-matched surrogate~\cite{gang2026} tuned to the resolver's own rate...`. The sentence characterises the earlier paper and positions this one against it ("here we test the mechanism"), which is comparison beyond ordinary citation. | high | E | − (≈25 words) |
| V2 | sections/04_protocol.tex:19 | `The rate match only calibrates the surrogate.` | `The rate match fixes the surrogate's parameter.` | high | E | − |
| V3 | sections/01_introduction.tex:13 | `This is the equifinality problem of model calibration~\cite{beven2006},` | `This is the equifinality problem~\cite{beven2006},` ("calibration" is Beven's term, but it brings back the banned calibration framing next to "surrogate"). | low | T: the term-of-art reading is defensible | − |
| — | 02_related_work.tex:12 `control barrier functions`; 04_protocol.tex:7 `...`; 05:50/52 `soft mode`, `opposed lateral mode`; 05:41 `unstable mode` | Kept. "Control barrier functions" is the cited robotics method's proper name. The "modes" are Hessian eigenmodes, not run modes. | — | — | — |

---

## 3. Sentences that announce what a section will do

Every section and subsection opening was checked. 4, 5, 5.1, 5.2, 5.3, 5.4, 6, 6.1, 6.3, 6.4 and 7 open with their question, and 4.3, 4.4, 4.5 and 8.1 open with their first step or result. Section 3 and its subsections open with the model statement, which is correct for a methods section. The defects are listed below.

| # | file:line | Quoted text | Replacement | Sev | T/E | Len |
|---|---|---|---|---|---|---|
| 3.1 | sections/03_pedestrian_model.tex:49 | `A bottleneck rebuilt from the CroMa experiments~\cite{fzj_ped20219}, with agent number and corridor length matched run by run, tests the model against human data (Sect.~\ref{sec:validity}).` | Delete. This is a forward pointer, and Sect. 7 ¶1 states the same build in full ("matched agent number and corridor length run by run"). | med | E | − (1 sentence) |
| 3.2 | sections/04_protocol.tex:11 | `The protocol screens a resolver, the steering mechanism credited with resolving deadlocks, in five steps (Fig.~\ref{fig:protocol}).` | `A resolver is the steering mechanism credited with resolving deadlocks. The protocol screens it as follows (Fig.~\ref{fig:protocol}):` or, shorter, `The protocol screens a resolver, the steering mechanism credited with resolving deadlocks (Fig.~\ref{fig:protocol}):` ("in five steps" announces the enumerated list below it). | low | E | − |
| 3.3 | sections/08_discussion.tex:7 | `Granular and pedestrian clogging is read through arches and clog-lifetime statistics~\cite{zuriguel2014,nicolas2018trap}. Both deadlock types...` | Delete the first sentence and open with `Both deadlock types are set by ...`. Move the two citations onto "the activated escape of trap models~\cite{zuriguel2014,nicolas2018trap}" later in the paragraph. The opening sentence restates Sect. 2 ¶2. | low | T: a background-first discussion paragraph is common; the standard asks for result-first | − |
| 3.4 | sections/08_discussion.tex:10 | `The open framework deadlock-screen implements the screening protocol (\url{...}).` | `The framework deadlock-screen (\url{...}) needs from a steering model a restartable state, ...` (merge with the next sentence). This is the fourth statement of the same sentence; see 14.2. | med | E | − |
| 3.5 | sections/05_deadlock_physics.tex:48 | `...; with the short range on the jambs alone, \EsevenBjambCollective\ of \EsevenBjambClassified\ deadlocks are pair or group standoffs (Sect.~\ref{sec:lone}).` | Delete the clause after `(Fig.~\ref{fig:hero}, bottom)` and end the sentence there. It repeats 05:20 verbatim in its numbers [11 of 11]. | med | E | − |
| 3.6 | sections/02_related_work.tex:12 | `The pair standoff of Sect.~\ref{sec:pair} is the pedestrian analogue.` | Keep. It is a forward pointer, but it carries the comparison. Listed so the decision is explicit. | — | T | 0 |

Paragraphs whose whole content is restated below them: none at a section opening. Sect. 8.1 ¶1 restates Sects. 6.1 to 6.3. Its unique sentences are `A matched rate is therefore weak evidence of a shared mechanism.` and `the rest-drive push, of ORCA's class, agrees with it on every probe at the lone keystone`; both should survive (see 14.1).

---

## 8. Figure and table captions (cap: two sentences; Fig. 1 exempt)

| # | file:line | Caption | Problem | Replacement | Sev | T/E | Len |
|---|---|---|---|---|---|---|---|
| 8.1 | tables/table3_matched.tex:3 | Table 3, three sentences, ≈105 words | Over the cap. It contains a design specification (`lone-trap noise rows count runs, five seeds per snapshot, and velocity-coupling quench rows six runs per snapshot`) that the text never states: "five seeds" and "six runs per snapshot" can only be derived from run/snapshot counts in 6.1 and 6.4. `Noise rows are SFM + noise` is redundant with 7:12 and 6.1. | `Rate-matched surrogates against ORCA under force coupling (last block: velocity coupling): freed (whole runs: completed), paired difference $\Delta$ from ORCA, $J$ of the unresolved sets (pair: freed; disjoint sets: exact 95\% upper bound; independence value in parentheses), Kaplan--Meier median $t_{1/2}$ (s), first exits by the lower member, outcome changes in $10^{-9}$\,m replays (noise: snapshots whose seeds disagree) and $\ell$ of Eq.~\eqref{eq:ell} (prediction in parentheses). Lone-trap rows count runs (noise: five per snapshot; velocity coupling: six), whole-run rows seeds.` Move "five seeds per snapshot" into 06_screening.tex:25 (`frees \RunNOneFreed\ of \RunNOneRunsN\ runs (five seeds per snapshot) on ...`). | high | E | − |
| 8.2 | sections/05_deadlock_physics.tex:33 | Fig. (escape), three sentences | Over the cap. It uses notation $\Delta U_{\rm cond}$ that appears nowhere in the text, which writes $\Delta U$ "in each condition" (see 12.9). | `Left: Kaplan--Meier fraction escaped against time at $\Delta U/k_BT_{\rm eff}=2.5$. Right: fitted Arrhenius slope over $-\Delta U$ per snapshot and condition (95\% intervals) against $\Delta U$, predicted 1; full (solid, filled circles), pinned (dashed, open squares), alone (dotted, filled triangles), all vermilion.` | high | E | − |
| 8.3 | sections/07_experiments.tex:5 | Fig. (CroMa), three sentences | Over the cap. | `Flow through the entrance, longest gap between passages (log scale) and waiting-zone velocity fluctuation for the human runs and the four model variants. Small points are single runs, beside their means and 95\% intervals; humans grey, SFM black filled circle, SFM with $B_{w,\rm edge}$ black filled square, SFM+ORCA (RVO2) blue, SFM+noise $\sigma^\ast$ vermilion.` | high | E | − |
| 8.4 | sections/06_screening.tex:14 | Fig. (quench), two sentences | Within the cap. It contains the only statement of the noise grid `$\sigma=0.03$, 0.05, 0.07\,m/s`; the text refers to "the grid level" (06:25) without giving the grid. This is a specification that lives only in a caption. | No caption change. Fix in the text: see 11.4. | med | E | 0 |
| 8.5 | sections/05_deadlock_physics.tex:8 | Fig. (lone trap), two sentences, ≈75 words | Within the sentence cap but over 60 words. "SFM+ORCA with the RVO2 solver" appears twice. | Replace both occurrences with `SFM+ORCA (RVO2)`. | low | E | − |
| 8.6 | sections/06_screening.tex:8 | Fig. (Δt), two sentences | Within the cap. "$\beta_{\rm ref}$" is used before its definition at 06:28; acceptable for a caption. | Keep. | — | — | 0 |
| 8.7 | sections/04_protocol.tex:21; tables/table1_params.tex:3; tables/table2_signatures.tex:4; 05:25 (width); 06:44 (pair) | — | Within the cap. They state what is plotted and do not argue. | Keep. | — | — | 0 |

---

## 1. Rhetorical negation

| # | file:line | Quoted text | Replacement | Sev | T/E | Len |
|---|---|---|---|---|---|---|
| 1.1 | sections/07_experiments.tex:23 | `Removing deadlocks does not restore capacity.` | `Removing deadlocks leaves the flow below the human value.` | med | E | 0 |
| 1.2 | sections/07_experiments.tex:23 | `..., and its deadlocks are not human behaviour at this width.` | `..., and people at this width pass without deadlock.` (states the positive human finding of 07:17) | med | E | 0 |
| 1.3 | sections/06_screening.tex:25 | `The data give no evidence that the overlap separates them at the lone trap: only ...` | `At the lone trap the overlap cannot separate them: only ...` | med | E | − |
| 1.4 | sections/05_deadlock_physics.tex:43 | `The computed path of the latter is not its dynamical escape route.` | `Its escape route is therefore not the computed path.` This still negates, but no positive route is known, so the ruling-out is the finding. Alternative: delete, since "never escape within 300 s at any level" already carries it. | low | T | − if deleted |
| 1.5 | sections/05_deadlock_physics.tex:59 | `soft-core analogues of one- and two-grain arches held by repulsion of range $B_w$ without contact or friction.` | `soft-core analogues of one- and two-grain arches held by repulsion of range $B_w$.` ("contact-free" is already in the same sentence, so the trailing "without contact or friction" is a bookend.) | low | E | − |
| 1.6 | sections/06_screening.tex:59 | `The prediction held: velocity-coupled ORCA is class P, and ...` | `Velocity-coupled ORCA is class P, as predicted, and ...` (also an aphoristic lead-in; see 10) | low | E | − |
| 1.7 | sections/05_deadlock_physics.tex:20 | `Adding the other walls makes no detectable difference.` | `Adding the other walls changes completion from \EsevenBjambK\ to \EsevenBallK.` If a p-value exists, add it; otherwise keep the original. | low | T: the original already has its numbers in the previous sentence | + (pair with 3.5) |
| 1.8 | sections/00_abstract.tex:3 | `ORCA coupled through the velocity has no rest drive and frees no deadlock, as the protocol predicts.` | `...frees no deadlock, as predicted.` The protocol does not predict; the rest-state lemma does (subject mismatch, see 13). | low | E | − |

Kept as genuine technical contrasts that carry information:
- 01:13, `shows that a simpler cause suffices ... It cannot show that the two act alike, because ...`. This is the paper's premise, and it states its reason.
- 03:35, `(with $v_0$, not $v_{\rm eff}$)`. It specifies which speed enters.
- 04:41, `Part (ii) does not cover ORCA's velocity-dependent constraint part.`. A scope statement.
- 06:33, `RVO2 replays neither grow nor jump.`. The contrast with the legacy solver is the result.
- 05:56, `$\mu_1$ does not predict them (rank correlation ...)` and `The escape times are not exponential (pooled Weibull shape ...)`. Each has its number.

Cascades of three or more rule-outs before a claim: none found.

Mirrored pairs: none found.

---

## 5. Softening adverbs and undefined qualifiers

| # | file:line | Quoted text | Replacement | Sev | T/E | Len |
|---|---|---|---|---|---|---|
| 5.1 | sections/05_deadlock_physics.tex:18 | `Whole runs rarely complete (\EOneBCompletionK\ of \EOneBCompletionN).` | `Whole runs complete in \EOneBCompletionK\ of \EOneBCompletionN.` | med | E | − |
| 5.2 | sections/06_screening.tex:54 | `so with \PairN\ snapshots the rate constrains $b^\ast$ weakly.` | `so out of sample $b^\ast$ does no better than the copied rate.` | med | E | 0 |
| 5.3 | sections/05_deadlock_physics.tex:12 | `which grows steeply with the radius $r$:` | `which grows with the radius $r$:` (the three numbers that follow carry "steeply") | low | T | − |
| 5.4 | sections/05_deadlock_physics.tex:16 | `The SFM drive (median \DriveCOneMedian\,N) is comparable to $g_{\max}$ at the mean radius:` | `The SFM drive (median \DriveCOneMedian\,N) lies between $g_{\max}$ at $r=0.25$ and $0.35$\,m:` ("comparable" undefined; the bracket is the reason a quarter are stuck) | low | E | 0 |
| 5.5 | sections/05_deadlock_physics.tex:56 | `the pair needs a few seconds of deterministic run-out to clear the door.` | Replace "a few seconds" with the measured run-out (for example the lag at which the Weibull shape reaches 1, as was done for the lone trap at 05:41). If no number exists, write `needs a deterministic run-out to clear the door`. | low | E | 0 |
| 5.6 | sections/06_screening.tex:22 | `and replays exactly.` | `and replays bit for bit.` ("exactly" here means bit-identical; 06:59 uses "bit for bit", so align them, see 12.12) | low | T | 0 |
| 5.7 | sections/01_introduction.tex:11 | `a small linear program over velocity-obstacle constraints` | `a two-dimensional linear program over velocity-obstacle constraints` ("small" is undefined; 02:3 says two-dimensional) | low | E | + (1 word) |
| 5.8 | sections/04_protocol.tex:7 | `a perturbation far below the model's physical scales` | Keep. The class definition is generic and the instance ($10^{-9}$\,m) is given in step 2. Listed so the decision is explicit. | — | T | 0 |

Also checked, with no hits: arguably, somewhat, fairly, rather, quite, perhaps, seemingly, essentially, virtually, largely, generally, typically, usually, roughly, comfortably, clearly, actually, almost, nearly, really, relatively, effectively, particularly. "Exactly" in Proposition 1 and "exact" stuck-alone criterion / exact McNemar are mathematical and are kept.

---

## 12. Terminology and notation drift

| # | Concept | Names used (where) | Recommend | Sev | T/E |
|---|---|---|---|---|---|
| 12.1 | Symbol $g$ | goal $\mathbf g$ (03:11, 04:39, T1); $g_{\max}(r)$ wall force (abstract, 05:12, 08:13); **undefined $g$** in the friction power `$-\kappa\,g\,[(\mathbf v_i-\mathbf v_j)\cdot\mathbf t_{ij}]^2$` (04:37); surface gap `$g$ being the pair's surface gap` (06:57) | 04:37: replace `$g$` by `$h(r_{ij}-d_{ij})$`. **This is an error: the symbol is never defined for this use.** 06:57: replace `a slack of at least $g/2\tau_h$ at zero velocity, $g$ being the pair's surface gap` with `a slack of at least $(d_{ij}-r_{ij})/2\tau_h$ at zero velocity` (len −). | high | E |
| 12.2 | Held by the door edges alone | "stuck alone" (05:16, 05:18, abstract via "stuck-alone criterion", intro), "held alone" (05:20 ×2, Fig. lone-trap caption `positive: held alone`), "held ... if and only if" (05:12) | "stuck alone" for the property, because the criterion and margin are named after it. Replace "held alone" at 05:20 (×2) and in the Fig. lone-trap caption. | med | E |
| 12.3 | The lateral perturbation | "lateral bias $b$" (03:16, 05:52, abstract), "lateral tilt $\pm b$" (04:14, Fig. protocol), "Tilt $\pm b$" (T2 header), "tilt" also for the effect on the energy minimum (abstract, 08:4, Fig. 1) and for the drive direction (03:16 `a deterministic tilt of fixed handedness`) | Use "lateral bias $b$" for the perturbation and probe ("bias $\pm b$" in 04:14, T2 header, Fig. protocol). Keep "tilt" only for its effect on the minimum. At 03:16 write `The lateral bias $b$, a deterministic rotation of fixed handedness, replaces ...`. | med | E |
| 12.4 | ORCA with the RVO2 solver | "SFM+ORCA with the RVO2 solver" (05:16 caption ×2, 06:22, 07:12), "SFM+ORCA (RVO2)" (07:20 ×2, Fig. CroMa), "ORCA (RVO2)" (06 throughout, T3), "the RVO2 solver" (06:51), bare "RVO2" (06:33) | `ORCA (RVO2)` in Sects. 5 and 6; `SFM+ORCA (RVO2)` only in Sect. 7 where the base model is named. Fix 05:8 (×2), 06:22 `that SFM+ORCA with the RVO2 solver frees` → `that ORCA (RVO2) frees`, and 07:12 `SFM+ORCA with the RVO2 solver` → `SFM+ORCA (RVO2)` (len −). | low | E |
| 12.5 | Legacy solver | "legacy linear-program solver of the original implementation" (03:35), "original implementation" (T1:12), "the legacy ORCA solver" (abstract), "legacy solver" (06), "ORCA (legacy)" (T3, captions), "the legacy linear-program solver" (06:33) | "legacy solver" / "ORCA (legacy)". Drop "original implementation" (see 11.1). At 06:33 write `Only the legacy solver changes outcome ...` (len −). | med | E |
| 12.6 | Short-range wall variants | "short-range wall law" (abstract, 05:48, 08:23, 09:2), "a range $B_w=0.04$\,m on every wall" (05:20), "the jamb wall law" (05:20), "the short range on the jambs alone" (05:48), "jamb range reduced to $B_{w,\rm edge}$" (07:12, 07:20), "the reduced jamb range" (07:23), "jamb-only" (T1), "SFM with jamb range $B_{w,\rm edge}$" (Fig. CroMa) | "short-range wall law ($B_w=0.04$\,m)" for all walls; "short-range jambs ($B_{w,\rm edge}$)" for jambs only. 07:12/07:20/07:23 then read `the SFM with short-range jambs`. | med | E |
| 12.7 | "jamb", "corridor", "door edge" | Used from the abstract onward (`jamb faces`, `jamb segment`, `union of jamb and corridor wall` 03:26) but never defined. Table 1 places the door "in the wall $x=10$\,m" and mentions no corridor. | Define once at 03:26: `The door's two side walls (jambs) run from the room wall into a short corridor; at a door edge only the nearest point on the union of jamb and corridor wall acts.` Adjust to the real geometry. Pay for it with 3.1. | high | E |
| 12.8 | Pair-standoff location | "before the jamb faces" (abstract, 05:48), "at the jamb faces" (05 heading 5.3, 05:18, 09:2) | "before the jamb faces" throughout. The heading becomes "The Pair Standoff Before the Jamb Faces", or simply "The Pair Standoff". | low | E |
| 12.9 | Barrier per condition | $\Delta U$ (text), $\Delta U_{\rm cond}$ (Fig. escape caption only) | $\Delta U$ (fixed by 8.2). | med | E |
| 12.10 | Rest-state energy | "rest-state energy" (abstract, Fig. 1), "landscape of Eq.~(U), the SFM rest field" (04:55), "$U$" (04:39, 05:50), "rest field" for $\mathbf F_0$ (04:28) | Call $U$ "the rest-state energy" at Eq. (U): `the SFM rest field is conservative, $\mathbf F_0=-\nabla U$ with rest-state energy`. At 04:55 replace `on the landscape of Eq.~\eqref{eq:U}, the SFM rest field,` with `on the rest-state energy $U$,`. **04:55 calls $U$ "the rest field"; the rest field is $-\nabla U$. This is an error.** | high | E |
| 12.11 | The deterministic time-step response | "time-step dependence" (abstract), "Time-step signature" (06:27 heading), "Time-step test" (T3 block), "time-step probe" (08:10), "$\Delta t$ with per-step and with ..." (04:14) | "time-step probe" for the probe, "time-step signature" for its response; T3 block → `\emph{Time-step probe: ...}`. | low | E |
| 12.12 | Bit-identical replay | "replays exactly" (06:22), "repeats the SFM restart bit for bit" (06:59), "identical" (T2), "keep their outcomes" (06:51) | "bit for bit" (see 5.6). | low | T |
| 12.13 | "resolver" | Used at 02:15 (`tuned to the resolver's own rate`) before its definition at 04:11 | 02:15: `tuned to the rate of the mechanism under test`, or define it at the first use. | med | E |
| 12.14 | "stall" | Used at 04:8 (`stall survival`) before its definition at 06:38 (`at least 10\,s without an exit`) | Define at 04:8: `stall survival (stall: at least 10\,s without an exit)` and delete the parenthesis at 06:38. | low | E |
| 12.15 | "rate" | Freed or completion fraction in rate-matching (04:17, 06), and escape rate $\lambda$ in s$^{-1}$ (02:9, 04:50, 05:37). Both meet in 06 (`Escape rate per snapshot`, Fig. Δt). | Keep "rate" for the matched fraction, defined at 04:17. Write "escape rate $\lambda$" every time the other sense is meant; 04:48, 05:37 and the Fig. Δt caption already do. | low | T |
| 12.16 | "exit" | Door opening (abstract `0.8\,m exit`, title "narrow exits"), event (T1 `exit at $|x-g|<0.5$\,m`, 04:55 `to an exit`, 06:19 `exits within 120\,s`) | "door" for the opening (abstract → `At a 0.8\,m door`); keep "exit" for the event. | low | T: "exit" for the opening is the evacuation-literature norm |
| 12.17 | "SFM + noise" spacing | `SFM + noise` (07:12, 07:20, Fig. CroMa, T3) vs `SFM+ORCA`, `SFM+TTC` | `SFM+noise` | low | E |
| 12.18 | Symbol overloads, informational | $w$ door width vs $w_{o,i}$ ORCA weight; $r$ radius vs "rounded edge $r=0.1$\,m" (T1); $\Delta$ paired difference vs $\Delta U$, $\Delta t$; $s(x;\cdot)$ sigmoid vs s (seconds) | Only T1's `rounded edge $r=0.1$\,m` collides in practice. Write `rounded edge, radius 0.1\,m`. | low | E |

---

## 2. Sentences that announce their own significance

Checked for: it is worth noting, it is important, crucially, notably, significantly, the key point, what matters. **None found.** `That reading is a claim about mechanism.` (01:11) is a claim, not an announcement (see 10).

---

## 4. Trailing appositive qualifications

| # | file:line | Quoted text | Action | Sev | T/E | Len |
|---|---|---|---|---|---|---|
| 4.1 | sections/08_discussion.tex:7 | `Multi-robot deadlocks under safety constraints are closed-loop equilibria left by designed perturbations~\cite{grover2020}, at which a resolver and its rate-matched surrogate can be probed together.` | The claim is in the trailing clause. Promote it: `A resolver and its rate-matched surrogate can be probed together at multi-robot deadlocks, closed-loop equilibria left by designed perturbations~\cite{grover2020}.` | med | E | − |
| 4.2 | sections/06_screening.tex:36 | `The rate-matched surrogate is noise at $\sigma^\ast=\EsixSigmaStar$\,m/s, the completion fit of Sect.~\ref{sec:escape} inverted at the completion of ORCA (RVO2), run on the same spawns.` | Two stacked trailing appositives; "run on the same spawns" attaches to the fit. Fix: `The rate-matched surrogate, run on the same spawns, is noise at $\sigma^\ast=\EsixSigmaStar$\,m/s, where the completion fit of Sect.~\ref{sec:escape} meets the completion of ORCA (RVO2).` | low | E | 0 |
| 4.3 | sections/05_deadlock_physics.tex:59 | `..., soft-core analogues of one- and two-grain arches held by repulsion of range $B_w$ without contact or friction.` | Editorial analogy tacked on a results paragraph. Move to 08:7, which discusses arches (it can replace that paragraph's opening, 3.3), or trim per 1.5. | low | T | 0 |
| 4.4 | sections/08_discussion.tex:7 | `At the lone trap noise acts by the activated escape of trap models, over the model's own barriers, with only the attempt rate fitted.` | Three appended qualifiers. `At the lone trap noise acts by activated escape over the model's own barriers, with only the attempt rate fitted, as in trap models.` | low | T | 0 |
| 4.5 | sections/06_screening.tex:38 | `Of its failures, \EsixCThreeFailMoving\ still move at 600\,s, so $\sigma^\ast$ matches completion within this horizon only.` | Keep. It is a needed caveat. 08:23 already lists "Whole runs end at 600\,s", so the limitation is covered there as well. | — | T | 0 |

Dangling modifiers: 02:3 `so that the new velocity is the solution of a two-dimensional linear program nearest to the preferred velocity`. "Nearest" attaches to "linear program". See 16.2.

---

## 6. Sentences beginning with "What" and other clefts

**None found.** Checked for sentence-initial "What", "It is ... that", "There is ... which" and "The thing that". 05:52 `There, with $\delta=...$` is locative, not expletive.

---

## 7. Headings and bold run-in leads

| # | file:line | Heading | Replacement | Sev | T/E |
|---|---|---|---|---|---|
| 7.1 | sections/06_screening.tex:30 | `Second trap and the legacy solver.` (two topics in one head) | Split: `Second trap.` over ¶1, and a new run-in head `Legacy solver.` over ¶2 (06:33). | low | E |
| 7.2 | sections/04_protocol.tex:23 | `Terms That Vanish at Rest` | `Rest-State Lemma` (matches Proposition 1's name, so it can be found from the contents) | low | T |
| 7.3 | sections/05_deadlock_physics.tex:29 | `Noise as Activated Escape` (states the result) | `Noise at the Lone Trap` | low | T: result-stating heads are accepted in physics journals |
| 7.4 | sections/06_screening.tex:4, :40 | `The Lone Trap`, `The Pair Standoff` (repeat the 5.1 and 5.3 heads; the contents page shows two identical entries) | `ORCA at the Lone Trap`, `ORCA at the Pair Standoff` | low | T |
| 7.5 | sections/05_deadlock_physics.tex:47 | `The Pair Standoff at the Jamb Faces` | `The Pair Standoff Before the Jamb Faces` (12.8) | low | E |
| 7.6 | sections/08_discussion.tex:3 | `Mechanisms Behind a Matched Rate` | Keep. It names the content. | — | — |

---

## 9. Run-on and over-nested sentences

**Worst sentence in the paper: sections/06_screening.tex:59.** It competes with 07:14 and 04:55.

> `With either solver, velocity-coupled ORCA frees \VelLoneRvoK\ of \VelLoneN\ runs on the \VelLoneSnaps\ lone-trap snapshots, where force coupling frees \VelLoneForceRvoK\ (RVO2) and \VelLoneForcePubK\ (legacy), and \VelPairRvoK\ of \VelPairN\ on the \VelPairSnaps\ pair snapshots, against \VelPairForceRvoK\ and \VelPairForcePubK\ (Table~\ref{tab:matched}).`

Split:

> `With either solver, velocity-coupled ORCA frees \VelLoneRvoK\ of \VelLoneN\ runs on the \VelLoneSnaps\ lone-trap snapshots and \VelPairRvoK\ of \VelPairN\ on the \VelPairSnaps\ pair snapshots (Table~\ref{tab:matched}). Force coupling frees \VelLoneForceRvoK\ and \VelLoneForcePubK\ (RVO2, legacy) at the lone trap and \VelPairForceRvoK\ and \VelPairForcePubK\ at the pair.`

Sev high, E, Len 0.

| # | file:line | Quoted text (start) | Split / fix | Sev | T/E | Len |
|---|---|---|---|---|---|---|
| 9.1 | sections/07_experiments.tex:14 | `In the waiting zone (0.3--2.5\,m in front of the entrance, within 2\,m of its axis), while the local mean speed is below 0.3\,m/s, the velocity fluctuation is the standard deviation, root-mean-squared over both components, of each agent's smoothed velocity relative to its neighbours within 0.74\,m.` | `The waiting zone lies 0.3--2.5\,m in front of the entrance and within 2\,m of its axis. While its local mean speed is below 0.3\,m/s, the velocity fluctuation is the standard deviation of each agent's smoothed velocity relative to its neighbours within 0.74\,m, root-mean-squared over both components.` | high | E | 0 |
| 9.2 | sections/04_protocol.tex:55 | `The string method~\cite{e2007} gives $\Delta U$ on the landscape of Eq.~\eqref{eq:U}, the SFM rest field, from the snapshot minimum to an exit, the blocker past the door plane, with all residual agents mobile (full), the neighbours pinned (pinned) or the blocker alone (alone).` | `The string method~\cite{e2007} gives $\Delta U$ on the rest-state energy $U$ from the snapshot minimum to an exit, with the blocker past the door plane. All residual agents are mobile (full), the neighbours are pinned (pinned) or the blocker is alone (alone).` This also fixes the rest-field error in 12.10. | high | E | − |
| 9.3 | sections/07_experiments.tex:20 | `In every variant the flow, counted up to the deadlock where there is one, is ... of the human flow: \EtenCOneFlow\ [...]\,ped/s for the SFM (ratio ... [...]) and \EtenCThreeFlow\ [...]\,ped/s for SFM+ORCA (RVO2) (ratio ... [...]).` | Double parentheses `(RVO2) (ratio`, and two interval brackets per clause. `In every variant the flow, counted up to any deadlock, is ... of the human flow (SFM \FixAsevenCOneFlowRatio\ [...], SFM+ORCA (RVO2) \FixAsevenCThreeFlowRatio\ [...]; flows in Fig.~\ref{fig:croma}).` The absolute flows already appear in Fig. CroMa. | med | E | − |
| 9.4 | sections/06_screening.tex:36 | `Two independent noise streams on the same spawns overlap at $J=...$ [...], and noise and ORCA (RVO2) overlap as much (... and ... for the two streams; ...--... for independent sets), so the overlap gives no separation.` | `Two independent noise streams on the same spawns overlap at $J=...$ [...]. Noise and ORCA (RVO2) overlap as much (... and ...; independent sets ...--...), so the overlap does not separate them.` | med | E | 0 |
| 9.5 | sections/06_screening.tex:54 | `At $-b^\ast_{\rm legacy}$ the upper member exits first in ... of ... freed standoffs, and the two signs free different standoffs (discordant \PairBsPubRevA:\PairBsPubRevB, $-b^\ast$ only : $+b^\ast$ only); ORCA has no handedness.` | The legend comes after the numbers, and the sentence ends in an aphorism. `At $-b^\ast_{\rm legacy}$ the upper member exits first in ... of ... freed standoffs, and the two signs free different standoffs ($-b^\ast$ only : $+b^\ast$ only, \PairBsPubRevA:\PairBsPubRevB). ORCA shows no handedness (Table~\ref{tab:matched}).` | low | E | 0 |
| 9.6 | sections/05_deadlock_physics.tex:39 | `In the full condition with every agent at the blocker's $k_BT_{\rm eff}$ (... runs on ... snapshots), the median slope ratio is ... (range ...; interval covering 1 in ... of ... fits), against ... with only the blocker at that temperature.` | Two parentheticals plus a trailing comparison. `With every agent at the blocker's $k_BT_{\rm eff}$ (... runs on ... snapshots), the full-condition median slope ratio is ... instead of ... (range ...; interval covers 1 in ... of ... fits).` | low | E | − |
| 9.7 | sections/05_deadlock_physics.tex:41 | `The median attempt rates, ...\,s$^{-1}$ (full) and ...\,s$^{-1}$ (alone), are a median ... of the Langer prefactor from the Hessians at minimum and saddle (below it in ... of ... fits).` | "median ... a median". `The attempt rates (median ... and ...\,s$^{-1}$, full and alone) are a median ... of the Langer prefactor from the Hessians at minimum and saddle, and below it in ... of ... fits.` | low | E | 0 |
| 9.8 | sections/05_deadlock_physics.tex:20 | `At $w=0.8$\,m a range $B_w=0.04$\,m on every wall lifts completion to ... of ... (... at $0.02$\,m), and on the jambs alone ($B_{w,\rm edge}$) to ... ($p=...$ against the default).` | Three parentheticals in one clause chain. `At $w=0.8$\,m the short-range wall law ($B_w=0.04$\,m) lifts completion to ... of ... (... at $0.02$\,m); short-range jambs alone lift it to ... ($p=...$ against the default).` | low | E | 0 |
| 9.9 | sections/04_protocol.tex:55 | `A string is used only if it converges (uphill perpendicular force below 5\,N, climbing image stationary at the maximum, under 1\% change on doubling the images), ends in an exit and, when alone, matches a direct two-dimensional path.` | Acceptable. The parenthetical is a list of three criteria. Listed only because a reviewer would count four clauses. | — | T | 0 |
| 9.10 | sections/00_abstract.tex:3 | `Velocity noise frees the lone trap by activated escape, and no contact arch persists.` | A comma-joined pair of unrelated results. `Velocity noise frees the lone trap by activated escape. No contact arch persists.` | low | E | 0 |

---

## 10. Aphoristic paragraph endings

Count: **5**, which is above the standard's ceiling of two to three.

| # | file:line | Text | Action |
|---|---|---|---|
| 10.1 | sections/08_discussion.tex:4 | `A matched rate is therefore weak evidence of a shared mechanism.` | **Keep. This is the one that earns its place.** It is the paper's thesis, stated once, mid-paragraph. |
| 10.2 | sections/01_introduction.tex:11 | `That reading is a claim about mechanism.` | Convert: `..., the usual reading is that reciprocal avoidance resolved the jam, which is a claim about mechanism.` (len 0) Or keep it as the second permitted one. Taste. |
| 10.3 | sections/07_experiments.tex:23 | `..., and its deadlocks are not human behaviour at this width.` | Convert per 1.2. |
| 10.4 | sections/06_screening.tex:54 | `ORCA has no handedness.` | Convert per 9.5. |
| 10.5 | sections/06_screening.tex:59 | `The prediction held: ...` | Convert per 1.6. |

---

## 11. Process-record and internal-code leakage

| # | file:line | Quoted text | Replacement | Sev | T/E | Len |
|---|---|---|---|---|---|---|
| 11.1 | sections/03_pedestrian_model.tex:35; tables/table1_params.tex:12 | `the legacy linear-program solver of the original implementation`; `legacy linear-program solver: original implementation, with a leg-normal sign defect` | The reader cannot identify "the original implementation". 03:35: `the legacy linear-program solver, which has a leg-normal sign defect (Sect.~\ref{sec:att-lone})`. T1: `legacy solver: linear program with a leg-normal sign defect`. | med | E | − |
| 11.2 | sections/04_protocol.tex:55 | `Of the \FinBarLibN\ lone-trap snapshots sent to the string method, \FinBarGateFail\ failed this gate and are not used; \LoneBarN\ barriers enter the library.` | "gate" is internal jargon (a bare definite noun), and "sent to" is process narration. `Of \FinBarLibN\ lone-trap snapshots, \FinBarGateFail\ fail these tests; \LoneBarN\ barriers enter the library.` | med | E | − |
| 11.3 | sections/04_protocol.tex:48 | `In separate runs the blocker's realised velocity variance is on average \TthreeRatioMean\ times Eq.~\eqref{eq:teff};` | "Separate runs" cannot be identified. Name them, for example `In noise-only runs of the blocker away from contact, its realised velocity variance ...` (adjust to what was run). | low | E | 0 |
| 11.4 | sections/06_screening.tex:25 | `Per-step noise at $\sigma=0.07$\,m/s, the grid level nearest the rate of ORCA (RVO2), matches that rate` | The grid is defined only in a caption (8.4). `Per-step noise at $\sigma=0.07$\,m/s matches the rate of ORCA (RVO2)` (len −). If the grid must be named: `Of the levels 0.03, 0.05 and 0.07\,m/s, $\sigma=0.07$\,m/s is nearest the rate of ORCA (RVO2)`. | low | E | − |
| 11.5 | sections/06_screening.tex:25 | `The refined level $\sigma=\RunNOneSigma$\,m/s` | "refined" records process. `The level $\sigma=\RunNOneSigma$\,m/s, refitted on all snapshots,` (or whatever defines it). | low | T | 0 |
| 11.6 | sections/05_deadlock_physics.tex:37; sections/06_screening.tex:28 | `(of \FixAthreeEfourQual\ that qualify)`; `(of \FixAthreeEthreeQual\ that qualify)` | The criterion is stated for 05:37 ("at least two residual agents") but not for 06:28. Add the criterion at 06:28, or write `(of \FixAthreeEthreeQual\ with a library barrier)` if that is the criterion. | low | E | 0 |

No other leakage found. Checked for internal labels (C1 etc.), file paths, belief revision, and pre-registration phrasing.

---

## 13. Numbers and internal consistency

| # | file:line | Quoted text | Problem | Fix | Sev | T/E |
|---|---|---|---|---|---|---|
| 13.1 | sections/06_screening.tex:59 (`$p=\VelWholeForceP$`) | renders `p = 2.2 × 10^−16` | 2.2×10⁻¹⁶ is double-precision machine epsilon, the floor that statistical software prints. It is a resolution floor, not a measurement. | Report `$p<10^{-15}$`, or the exact Fisher/McNemar value computed in log space (change the macro in numbers.tex). | high | E |
| 13.2 | sections/00_abstract.tex:3 | `if and only if ... exceeds its drive $m v_0/\tau$; under the default wall law half the runs complete at a critical width of \EsevenWcrit\,m.` | The semicolon joins the criterion to a width with no stated link. The intro and the conclusion both say the criterion *brackets* the width. | `...; under the default wall law it brackets the width, \EsevenWcrit\,m, at which half the runs complete.` | med | E |
| 13.3 | sections/05_deadlock_physics.tex:37 | `Per snapshot and condition the escape rate follows the Arrhenius law with that barrier.` | The paragraphs below report median slope ratios 0.87–1.15, a pooled slope interval that excludes −1, and Weibull shape >1 against Kramers' predicted 1 (04:57). The topic sentence is stronger than its evidence. | `Per snapshot and condition the escape rate follows the Arrhenius law with that barrier to within the fitted attempt rate.` Or keep and add `; the escape times are not exponential until a lag` at the Weibull paragraph. | med | E |
| 13.4 | sections/07_experiments.tex:17 | `averages \EtenHumanGap\,s (at most \EtenHumanGapMax\,s)` → "1.7 s (at most 2.04 s)" | Mixed precision for the same quantity. | Use two decimals for both, or one for both (`2.0`). Note that one decimal makes "at most 2.0 s" sit badly next to "1 gap ... exceeds 2 s", so two decimals are preferred. | low | E |
| 13.5 | sections/05_deadlock_physics.tex:52 | `(rank correlation of the two differences \PairAsymCorr)` → 0.9996 | Four significant figures on a rank correlation of 46 snapshots. | `0.999` or `>0.99`. | low | E |
| 13.6 | tables/table3_matched.tex:23,25 vs 05:52 | $b^\ast$ = 0.0223, 0.0091 vs $b_f$ = 0.001–0.038 (median 0.016) | Mixed precision for the same parameter. | 0.022 and 0.009, or give $b_f$ to the same precision. | low | E |
| 13.7 | sections/00_abstract.tex:3 | `as the protocol predicts` | Subject mismatch: the rest-state lemma predicts; the protocol classifies. | Per 1.8. | low | E |
| 13.8 | sections/05_deadlock_physics.tex:18 | `and \FinCritNearZeroN\ of the \FinCritN\ margins lies within $\pm10$\,N of zero` | Correct with "1". Not robust if the macro changes. | `and the margin of \FinCritNearZeroN\ of the \FinCritN\ lies within ...` | low | T |

Checked and consistent: arch lifetimes (intro 3.3 s = fine-step maximum; 2.9 s at Δt = 0.01); flow ratio range 0.40–0.59 encloses the short-range-jamb variant (0.57); the full-condition fit count (8) matches the two exclusions out of 10.

---

## 14. Structural and framing problems

| # | Location | Problem | Fix | Sev | T/E | Len |
|---|---|---|---|---|---|---|
| 14.1 | 00_abstract:3, 01_introduction:17–20, 08_discussion:4, 09_conclusions:2 | The same three-way result ("ORCA through its rest drive, noise through activated escape, a lateral bias through a tilt") and the same CroMa sentence ("every model variant passes only ... of the human flow") appear four times in near-identical words. The conclusion is a re-run of the abstract. | Let the conclusion carry the recommendation it currently lacks. Replace `The probes separate the mechanisms, and replays expose the leg-normal sign defect of the legacy solver.` with `A matched rate is weak evidence of a shared mechanism; the probes of Sect.~\ref{sec:framework} separate them, and replays expose the legacy solver's sign defect.` | med | E | 0 |
| 14.2 | 00_abstract:3, 01_introduction:19, 08_discussion:10, 10_back_matter:4 | `The open framework deadlock-screen implements the (screening) protocol` appears four times. | Delete it from the intro bullet (01:19 `The open framework deadlock-screen implements the protocol.`), and merge it at 08:10 per 3.4. Keep it in the abstract and the back matter. | med | E | − |
| 14.3 | 09_conclusions:2 | The paper's final words are a deficit (`passes only ... of the human flow`). | Swap the last two sentences so it ends on the recommendation from 14.1. Alternatively, accept: the deficit is a finding, not a limitation. | low | T | 0 |
| 14.4 | 03_pedestrian_model:16, 04_protocol:41, 04:48, 04:55 | Measured results sit in methods sections: blocker density bound, $\max|\mathbf F_0+\nabla U|$, realised variance ratio, string-gate failures. A reviewer reading results will not find them. | Acceptable for checks of assumptions. Flagged only for 04:48, the variance ratio, which is a validation of Eq. (teff) and could move to 5.2 ¶1. No length change. | low | T | 0 |
| 14.5 | 01_introduction:16–21 | The contribution bullets put the protocol (Sect. 4) third, after the results it enables. | Taste. The paper's order is physics, then screening; the bullets follow importance. Keep. | — | T | 0 |

---

## 15. Spelling and convention consistency

British spelling throughout: behaviour, neighbour, modelling, characterised, discretised, realised, colour, metres, centre, modeller, towards. No American spellings found. Serial comma: the paper consistently omits it ("noise, a lateral bias and contact"). Keep it that way.

| # | file:line | Mix | Fix | Sev |
|---|---|---|---|---|
| 15.1 | 07:12, 07:20, 07:5, T3:3 | `SFM + noise` vs `SFM+ORCA`, `SFM+TTC` | `SFM+noise` | low |
| 15.2 | 06:8 caption `time step`; 08:10 `time-step probe`; 06:27 `Time-step signature` | Correct compound-adjective hyphenation. | none | — |
| 15.3 | 05:52 `(snapshot, sign) cases`; 05:54 `(snapshot, $b$) cases` | Consistent. | none | — |

---

## 16. Anything else

| # | file:line | Quoted text | Problem | Fix | Sev | Len |
|---|---|---|---|---|---|---|
| 16.1 | sections/04_protocol.tex:37 | `with power $-\kappa\,g\,[...]^2\le0$` | Undefined symbol (see 12.1). | `$-\kappa\,h(r_{ij}-d_{ij})\,[...]^2\le0$` | high | 0 |
| 16.2 | sections/02_related_work.tex:3 | `so that the new velocity is the solution of a two-dimensional linear program nearest to the preferred velocity` | Misplaced modifier: the program is not "nearest". | `so that the new velocity, found by a two-dimensional linear program, is the permitted velocity nearest to the preferred one` | low | 0 |
| 16.3 | sections/05_deadlock_physics.tex:50 | `belongs in all \PairSoftCommon\ to the common lateral shift of both members` | Hard to parse. | `is in all \PairSoftCommon\ the common lateral shift of both members` | low | − |
| 16.4 | sections/05_deadlock_physics.tex:52 | `Continuation locates the loss point $b_f$ in \RunNSixFoldN\ cases (the other \RunNSixFallbackN\ keep the minimum to a median \RunNSixFallbackReachMed\ of the bisection threshold).` | The parenthesis has to be reread to recover its meaning. | `Continuation reaches the loss point $b_f$ in \RunNSixFoldN\ cases and stops at a median \RunNSixFallbackReachMed\,$b_f$ in the other \RunNSixFallbackN.` | low | − |
| 16.5 | sections/06_screening.tex:51 | `Combined with the drive part it opposes that part:` | Unclear antecedents ("it", "that part"). | `Added to the drive part, the constraint part opposes it:` | low | 0 |
| 16.6 | sections/05_deadlock_physics.tex:16 | `ORCA's rest drive (median \DriveORCAMedian\,N) lowers this to ...` | The rest drive is *added* to the SFM drive. The sentence reads as if it replaced it, and 215 vs 214 N invites that misreading. | `Adding ORCA's rest drive (median \DriveORCAMedian\,N) lowers this to ...` | low | + (1 word; pair with 5.3) |
| 16.7 | sections/04_protocol.tex:8 | `$J$ separates two perturbations only at the pair standoff, where both are deterministic.` | Correct but compressed. It is the reason the lone-trap $J$ paragraph (06:25) gives no separation; the 06:25 sentence could point back here and drop its own explanation. | At 06:25 replace `The data give no evidence ... both intervals are [...]` with `As expected (Sect.~\ref{sec:signatures}), the overlap does not separate them: only ... snapshots stay unresolved.` | low | − |
| 16.8 | sections/01_introduction.tex:15 | `with ORCA's velocity turned into an added force` | Fine, but since Sect. 6.4 the paper also has velocity coupling. A reader of the intro meets "added as a force" without knowing the alternative until bullet 2. | `with ORCA's velocity turned into an added force (force coupling; Sect.~\ref{sec:model})` is optional. Leave as is if space is short. | low | + |

Also checked, nothing found: jargon before definition beyond 12.7, 12.13 and 12.14; metaphors (the class nicknames "heat", "steer" and "glitch" are labels, defined once and used consistently).

---

## Counts per category

| Category | Entries (defects; kept items not counted) |
|---|---|
| V Vocabulary | 3 (1 high) |
| 3 Announcements / roadmap | 5 |
| 8 Captions | 5 (3 over the two-sentence cap) |
| 1 Rhetorical negation | 8 |
| 5 Softening adverbs | 7 |
| 12 Terminology / notation | 18 |
| 2 Significance announcements | 0 |
| 4 Trailing appositives | 4 |
| 6 "What" / clefts | 0 |
| 7 Headings | 5 |
| 9 Run-ons | 10 + worst sentence |
| 10 Aphoristic endings | 5 (keep 1) |
| 11 Process leakage | 6 |
| 13 Numbers / consistency | 8 |
| 14 Structure | 5 |
| 15 Conventions | 1 |
| 16 Other | 8 |

---

## Triage: top 10

Each fix below is length-neutral or shorter unless noted.

1. **V1, 01_introduction.tex:9.** Delete `Our earlier work tested such a credit ...; here we test the mechanism.` and move `\cite{gang2026}` to 02:15 as an ordinary citation. This is the only vocabulary rule with a hit that rises to a framing problem. −25 words. 2 min.
2. **12.1 / 16.1, 04_protocol.tex:37.** The undefined $g$ in the friction power becomes $h(r_{ij}-d_{ij})$. At 06:57, replace "$g$, the pair's surface gap" with $d_{ij}-r_{ij}$. A notation error a referee will catch. 3 min.
3. **13.1, `\VelWholeForceP` = 2.2×10⁻¹⁶.** This is the machine-epsilon floor. Report `p<10^{-15}` or compute it exactly. 5 min.
4. **12.10 / 9.2, 04_protocol.tex:55.** "the landscape of Eq. (U), the SFM rest field" mislabels $U$ as the rest field. Split the sentence per 9.2; it also gets shorter. 3 min.
5. **8.1, Table 3 caption.** Cut from three sentences to two, and move "five seeds per snapshot" into the text at 06:25. 5 min.
6. **8.2 and 8.3, Fig. escape and Fig. CroMa captions.** Merge each to two sentences, and replace $\Delta U_{\rm cond}$ with $\Delta U$. 4 min.
7. **9 (worst sentence), 06_screening.tex:59.** Split velocity-coupling counts into ORCA-velocity and force-coupling sentences. 2 min.
8. **V2, 04_protocol.tex:19.** `The rate match only calibrates the surrogate.` becomes `The rate match fixes the surrogate's parameter.` 1 min.
9. **12.7, jamb/corridor undefined.** Add one defining clause at 03:26. This adds about one line; pay for it with 3.1 (delete the CroMa forward pointer at 03:49) and 3.5 (delete the repeated 11-of-11 clause at 05:48). 5 min.
10. **1.1 / 1.2 / 10.3, 07_experiments.tex:23.** Replace the negation-framed section ending with the positive statements (`leaves the flow below the human value`; `people at this width pass without deadlock`). 2 min.

Next in line: 12.2 (stuck alone vs held alone), 12.3 (bias vs tilt), 5.1 ("rarely"), 13.2 (abstract's unlinked critical width), 14.1 (the conclusion repeats the abstract; give it the recommendation).
