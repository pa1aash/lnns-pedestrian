# I3 consistency audit (wt-I3, commit 9152cb1)

Scope: Abstract, Sect. 1 (incl. contributions), Sects. 8-10 against Sects. 5-7, numbers as rendered in paper/main.pdf;
every \ref/\eqref in sections 00-10 (plus tables and figure inputs). Rulings R1-R5 and reports/C_REPORT.md as reference.

## Cross-references
- main.log: no undefined references or citations, no rerun warning; PDF text contains no "??"; aux, log and PDF date from the
  commit build (19:45). All 89 \ref/\eqref targets in sections 00-10, tables 1-3b and fig_protocol are defined.
- Semantic check: every target points to the content claimed (Eq. (13) = stuck-alone criterion; Eq. (7) = identity;
  Eq. (11) = T_eff; Sect. 3.2 = force coupling / native ORCA; Sect. 4.2 = horizons; Sect. 5.3 = pair; Sect. 6.4 = velocity
  filter; Sect. 3.2 -> Sect. 6.1 for the legacy defect), except findings 1 and 2.

## Findings

1. 01_introduction.tex:22 - legacy-solver reference points to Sect. 6 (whole chapter); the defect is in Sect. 6.1
   ("Second Trap and the Legacy Solver"), as Sect. 3.2 (03_pedestrian_model.tex:36) already cites.
   Replace `legacy solver (Sect.~\ref{sec:attribution}).` with `legacy solver (Sect.~\ref{sec:att-lone}).`
2. 085_recommendations.tex:7 - "report ORCA results per solver" cites Sects. 6.1 and 6.4, but the per-solver difference
   is shown at the pair (Sect. 6.3: legacy 21 vs RVO2 7 of 46 freed). Replace
   `Sects.~\ref{sec:att-lone} and~\ref{sec:velorca});` with
   `Sects.~\ref{sec:att-lone}, \ref{sec:att-pair} and~\ref{sec:velorca});`
3. 00_abstract.tex:3 - overclaim: "at rest this force-coupled ORCA equals the model with relaxation time tau'". The identity
   holds only with no binding constraint (Eq. (7)); the constraint part binds at all pair members (Sect. 6.3) and opposes
   the drive at the second trap (Sect. 6.1). Replace `at rest this force-coupled ORCA equals the model with relaxation time`
   with `at rest its drive part is the model with relaxation time`.
4. 00_abstract.tex:3 - CroMa flow ratio lacks the scope of Sect. 7:25 and Sect. 10 ("with uncalibrated default
   parameters"). Replace `and model flow is \RevDThreeRatioMin--\RevDThreeRatioMax\ of human flow.` with
   `and with uncalibrated default parameters model flow is \RevDThreeRatioMin--\RevDThreeRatioMax\ of human flow.`
5. 09_conclusions.tex:2 - contradicts Sect. 6: "Force-coupled ORCA, velocity noise and a lateral bias free them through
   three mechanisms that reach the same freed fraction". The bias frees no lone keystone (Sect. 6.1:21), noise is not
   fraction-matched at the second trap (Sect. 6.1:24) and matches hold only at a named T (R-A8, Sect. 4.2). Replace with:
   `Fraction-matched to force-coupled ORCA at $T=120$\,s (lone keystones, pair standoffs) or 600\,s (whole runs), velocity noise and a lateral bias free them through mechanisms other than ORCA's rest drive: activated escape over an effective barrier \RevBthreeAllDeep--\RevBthreeAllMid\ of the computed one, and a tilt of the pair standoff out of its minimum; the probes separate all three.`
6. 08_discussion.tex:6 - "noise frees the lone trap by activated escape over the model's own barriers" omits R3's
   effective-barrier factor and the tested range (Sect. 5.2:39-45: 0.86-0.93, beta = 1.5-7). Replace
   `Here noise frees the lone trap by activated escape over the model's own barriers,` with
   `Here noise frees the lone trap by activated escape over an effective barrier \RevBthreeAllDeep--\RevBthreeAllMid\ of the computed one at $\beta=1.5$--7 (Sect.~\ref{sec:escape}),`
7. 08_discussion.tex:9 - Limitations name only the whole-run extrapolation below beta = 1.5; Sect. 5.2:45 shows the
   lone-keystone matched level is also below it (median beta 0.64, 36 of 56 below 1). Replace
   `The whole-run stall prediction extrapolates the Arrhenius law below the tested range $\beta\ge1.5$, outside the Kramers regime,`
   with `The matched noise levels lie below the tested range $\beta\ge1.5$ (median $\beta$ \RevAthreeSevenMed\ at the lone keystone, \RevAthreeStarMed\ at $\sigma^\ast$), outside the Kramers regime, where the whole-run stall prediction extrapolates the Arrhenius law,`
8. 08_discussion.tex:9 - typography: interval renders "[-0.15, 0.22]" with a hyphen (text-mode macro). Replace
   `[\TabThreePairPubDiffLo, \TabThreePairPubDiffHi]` with `[$\TabThreePairPubDiffLo$, $\TabThreePairPubDiffHi$]`.
9. 08_discussion.tex:4 - "Force-coupled ORCA reaches it through Reshape, axial" is scoped to the lone keystone only;
   at the pair Sect. 6.3 assigns Reshape with a lateral, non-gradient constraint part, and the legacy solver adds Glitch
   (Sect. 6:2). Replace `Force-coupled ORCA reaches it through Reshape, axial;` with
   `Force-coupled ORCA reaches it through Reshape (axial at the lone keystone; Glitch added by the legacy solver);`
10. 08_discussion.tex:9 - R1 says the pair standoff needs sharp segment ends and a short wall range; the limitation
    names only the ends. Replace `the pair standoff (library built with $B_w=0.04$\,m) in sharp segment ends.` with
    `the pair standoff in sharp segment ends with a short wall range (library built with $B_w=0.04$\,m).`
11. 01_introduction.tex:21 - scope: "none of 320 runs" holds for the B_w = 0.04 m walls of the generation runs (default
    walls give only 2 of 98 standoffs, Sect. 5.1:22); R1 adds that the standoff survives a line goal. Replace
    `the pair standoff forms in none of \RevBfiveGenN\ runs (Sect.~\ref{sec:pair}).` with
    `the pair standoff forms in none of \RevBfiveGenN\ runs with $B_w=0.04$\,m, against \RevBfiveGenPairRef\ with sharp ends, and a line goal keeps it (Sect.~\ref{sec:pair}).`
12. 01_introduction.tex:21 - "no contact arch persists" drops Sect. 5.4's scope. Replace
    `no contact arch persists (Sect.~\ref{sec:arches}).` with
    `no contact arch persists at the tested desired speeds (Sect.~\ref{sec:arches}).`
13. 01_introduction.tex:24 - CroMa contribution carries no number and omits the human deadlock fact that the abstract
    and Sect. 7:9 state. Replace `falls short of the human flow (Sect.~\ref{sec:validity}).` with
    `passes \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow, while no participant deadlocks in the \EtenHumanN\ runs (Sect.~\ref{sec:validity}).`
14. 00_abstract.tex:3 and 07_experiments.tex:9,19 - \EtenHumanN renders "5" ("In the 5 CroMa runs", "1 gap in the 5
    runs") while Fig. 9's caption says "five human runs". Optional style fix: write `five` in place of `\EtenHumanN`
    in running text (abstract:3, 07:9, 07:12, 07:19) and `one gap` for `\EtenHumanGapsOverTwoTotal\ gap` (07:19).

Sects. 8-10 vs 5-7 (task 3): findings 5 (bias/noise scope), 6-7 (beta range), 9 (pair class) are the contradictions or
overreaches; nothing else in Sects. 8-10 contradicts Sects. 5-7. Two notes inside 5-7 for the integrator (no change
required by the rulings): 05:20 "Door width sets the lone trap" vs abstract/Sect. 10 "set by the wall range" (both are
shown; consider "Door width also sets"); 07:21 reports a mean open gap (446 s) of censored runs, a censored quantity
next to the R5 reporting rule; consider "its 15 censored runs end without passage for the last 446 s on average"
or dropping the mean.

## Claim table (rendered values; "-" = not stated; "!" = finding)

| Claim | Abstract | Intro / contributions | Sect. 8 | Sect. 9 | Sect. 10 | Results |
|---|---|---|---|---|---|---|
| Lone trap cause | wall range (0.08 m), door-edge force alone | g_max vs drive; released-alone check | default B_w 0.08 m | (i) g_max vs m v_eff/tau, Eq. (13); (ii) wall range | wall range + end shape | 5.1 OK |
| Pair standoff | sharp ends; dominates at 0.04 m | rounded: 0 of 320 (!11) | sharp ends, B_w 0.04 (!10) | rounded ends remove it | end shape | 5.1, 5.3 OK; line goal only in 5.3 |
| w50 | - | brackets w50 | - | - | 0.878 m | 5.1: 0.878 [0.874, 0.883], miss 0.041, N=19 descriptive |
| tau', drive ratio | formula, x1.8-2.2 (!3) | 0.22-0.27 s | - | Eq. (7) | - | 3.2 / 5.1 (215+214 N) OK |
| ORCA velocity filter | no rest drive, frees none | frees none | - | per coupling | - | 6.4: 0/360, 0/276 |
| Noise mechanism, barrier | activated escape, 0.86-0.93, blocker alone | activated escape | own barriers (!6, !7) | Delta-t temperature | three mechanisms (!5) | 5.2 OK |
| Bias | tilts pair; handedness | handedness | Reshape lateral, past b_f | tilt probe | frees "them" (!5) | 5.3, 6.3 OK |
| Separating probes | replay, Delta-t (definition); time, final state (empirical) | same | every defining probe; Reshape axial (!9) | probe list | probes separate | 6.1-6.3 OK |
| Matched scope | at T (lone keystones, whole runs) | at horizon T | at horizon T; window | - | none (!5) | 4.2 T=120/600 s |
| Legacy defect | sign defect, replays | Sect. 6 (!1) | - | per solver (!2) | - | 6.1 OK |
| CroMa | 0.40-0.60 (!4); no deadlock in 5 runs | falls short (!13) | thin 2.0 m walls | censored final gap | 0.40-0.60, uncalibrated | 7 OK |
