# Referee recheck of the revised paper (2026-11-11)

Checked against the current text: paper/main.tex, paper/sections/*.tex, paper/tables/*.tex and the built
paper/main.pdf (25 pp., commit 515c372). The referee report itself is not on disk. Issue content was recovered
from lnns-launch/rev2/P.txt (fixes tagged with referee IDs), lnns-launch/rev1/{C,B,F}_full.txt, reports/C_REPORT.md,
reports/B_REPORT.md, reports/F_REPORT.md and plan/CHANGELOG.md C92-C94. P.txt tags most fixes by **group**, e.g.
"(M1, M2, M3, M4, M9, M10; R1-R3)", so for most IDs the exact sub-request cannot be separated from the group. Those
lines say "group-level" and judge every fix in the group. The Lens B/C/D/F items carry no referee numbering in the
sources: the numbers B1, C1, ... below are this file's own, and each line names its content.

Counts after the audit fix pass: **71 resolved, 3 partly resolved, 1 not resolved, 12 content not available** (first check: 65, 8, 2, 12).
After session I3 (the twelve items supplied in its brief): **83 resolved, 3 partly resolved, 1 not resolved, 0 content not available**.

## Framing, model and main issues

- F1 — resolved (session I3, item list from the session brief): end matter holds only the three author placeholders (\pending: Zenodo DOI, Acknowledgments, Disclosure of Interests), sized at about four lines each; the CroMa licence and attribution sentence (CC BY 4.0, Forschungszentrum Jülich, with citation) is in Sect. 7 — 10_back_matter.tex; 07_experiments.tex.
- F2 — resolved (group-level, framing: title and running head, the six keywords, an abstract that opens with the modelling problem, an equifinality opening, one crowd-disaster sentence, the paragraph on the conference paper [14] with the legacy solver and the Voronoi/Weidmann differences, a glossary, contributions scoped to "this social force model (Table 1)") — main.tex:25-27; Abstract; Sect. 1 (01_introduction.tex:9-32).
- F3 — resolved (group-level, framing plus model: Eq. (7) identity displayed with τ', "force-coupled ORCA"/"ORCA velocity filter", gate range, conversion source, native-ORCA sentence, TTC-inspired force with k_ttc in N s², Table 1 restructured, geometry figure) — Sect. 3.1-3.4, Eq. (5)-(7), Table 1, Fig. 2.
- M1 — resolved (group-level, deadlock physics: on-axis "if and only if" without "exact"; keystone and converse tests; w50 from 1100 runs with interval; bracket defined; failed (1-f)^100 prediction in one sentence; A13 facts; wall variants including rounding) — Sect. 5.1, Eq. (13), Fig. 5.
- M2 — resolved (group-level, as M1; Sect. 5.2: R3 wording, β at the matched noise level, high-β points, Weibull compressed, Langer, Mel'nikov-Meshkov, climbing image, excluded snapshot explained, σ50 moved to Sect. 6.2) — Sect. 5.2, Fig. 6.
- M3 — resolved ("one deadlock type per wall law" stated with counts; screening counts rescoped to the 60-snapshot screen or restated on all 160 second traps). Disputed below: the default walls still give 2 of 98 pair or group standoffs — Sect. 5.1 (05_deadlock_physics.tex:22); Sect. 6.1 (06_screening.tex:16, 24).
- M4 — resolved (group-level, as M1; Sect. 5.3 reframed per R1: sharp segment ends and short wall range required, 0 of 320 with rounded ends, line goal keeps it, exponent analysis cut, no barrier-under-bias exponent) — Sect. 5.3.
- M5 — resolved (group-level, classes and protocol: four word-named classes defined in Sect. 4.1; the numbered list that duplicated Fig. 3 deleted; paired tests with Holm; definitional vs empirical probes marked) — Sect. 4.1-4.2, Fig. 3, Table 2.
- M6 — resolved (group-level, protocol plus screening: "fraction-matched at T" with the horizons stated; Table 2 Observed block; Table 3 split) — Sect. 4.2 (04_protocol.tex:13-15), Tables 2, 3a, 3b.
- M7 — resolved (at v = 0 the ORCA term enters the rest field as a drive part plus a non-conservative constraint part; Remark 1(ii) explicitly does not cover force-coupled ORCA at the pair) — Sect. 4.3 (04_protocol.tex:34); Sect. 6.3 (06_screening.tex:45).
- M8 — resolved (group-level, screening: identity check on keystones and second traps, all 160 second traps, J reconciled to 20 seeds, legacy solver named by repository, commits and line with the defect described, Table 3 split, columns defined, table notes; Sect. 6.2 "no parameter fitted", "at 600 s"; Sect. 6.3 ORCA's class at the pair, overlap claim corrected, figure-only numbers in the text; Sect. 6.4 one paragraph without "as predicted") — Sect. 6.1-6.4, Tables 3a, 3b.
- M9 — resolved (group-level, as M1/M2) — Sect. 5.1-5.2.
- M10 — resolved (group-level, as M1; Sect. 5.4 at Δt = 0.0025 and 0.001 s, summed against single-contact compression, scoped "at the tested drives") — Sect. 5.4.
- M11 — resolved (dataset DOI and Boomers et al. 2023; runs 4D030-4D130; lengths 2.0 and 0.2 m; full commitment; CC BY 4.0 and attribution; Part D numbers; one force-coupled ORCA deadlock; R4 censoring; headline sentence). The optional per-run table is not included (see C11). A rendering defect in the participant counts is listed below — Sect. 7, Fig. 9.
- M12 — resolved (group-level, classes plus screening: classes per probe in Table 2; ORCA at the pair "Reshape, solver-dependent; the constraint part opposes the drive part") — Table 2 note a; Sect. 6.3.
- M13 — resolved (group-level, protocol: Remark (rest states) replaces the proposition, Lagrange-Dirichlet named, Hessian check on 60 snapshots, caveats listed; ℓ defined by Δt = 0.005/0.02 s; statistics subsection at the end of Sect. 4 with cluster bootstrap and hypergeometric J). Residual statistics formatting under C12 and D7 — Sect. 4.3-4.6, Eq. (9)-(12).
- M14 — resolved (unsupported robot-deadlock claim deleted; Grover characterised as switching controller, not additive perturbation; "Recommendations for Modellers" is its own section with the five-item checklist; Limitations add wall range, sharp segment ends, non-standard coupling and untested native ORCA, horizon dependence, one geometry family; Conclusions in four sentences) — Sect. 8.2-8.3, Sect. 9, Sect. 10.
- M15 — resolved (group-level, framing as F2; "the SFM" as an unscoped claim subject is gone; the remaining uses name the model variant) — Abstract; Sect. 1; Sect. 10.
- M16 — resolved (group-level, framing as F2) — Abstract; Sect. 1.
- m1 — resolved (group-level, model as F3) — Sect. 3.1-3.2, Table 1.
- m2 — resolved (group-level, model as F3) — Sect. 3.1-3.2, Table 1.
- m3 — resolved: the ninth decile (stuck-alone fraction) is reported next to the first eight and the last — Sect. 5.1 (\RevAthirteenStuckNinthDecile).
- m4 — resolved: classes are words (Prevent, Reshape, Heat, Glitch); r_c is the segment-end radius; I3 renamed the uniform distribution U(a,b) to \mathcal U (Table 1; U is the potential) and the ORCA density gate w_{o,i} to \chi_i (w is the door width); D is the damping matrix (sans serif) only, T the horizon only (T_eff, T_b subscripted), N/\mathcal N, P/\Pi, b/B, W (wall index) vs w (width) are distinct. Upright letter keys A–J of the schematic Fig. 2 are figure keys, as the figure rules allow. No notation table (no space); every symbol is defined at first use and the glossary covers the vocabulary.
- m5 — resolved: Table 2 has a Class column header (first column; "Class" also heads the observed block's last column); Table 3b's "Lower" column is defined in its note (freed standoffs first left by the member at y < 5 m).
- m6 — resolved: the ORCA time-step statistic now has one pooled value (Table 3a, ℓ = −0.0048 over 20 snapshots) and one per-snapshot bound (Table 2, |ℓ| ≤ 0.018), each note saying which; I3 also made the noise ℓ one value (2.2, prediction 2.2) in Tables 2 and 3a (new macro PprotEllBAPred).
- m7 — resolved: no "186 seeds", "207 noise settings", "refined level" or "copied rate" remains (grep of sections and tables).
- m8 — resolved (group-level, screening as M8) — Sect. 6.
- m9 — resolved: vandenberg2011rvo2 is the RVO2 Library release v2.0.2, Zenodo, 2016, DOI 10.5281/zenodo.7039667.
- m10 — resolved: g_max at r = 0.30 m (291 N) is stated with 0.20 and 0.35 m — Sect. 5.1.
- m11 — resolved: thousands with a thin space (20 000, macro StuckAloneN); units upright with a thin space; slash for units with a numerator (m/s, ped/s, N/m, kg/s^2), negative exponent only for pure reciprocals (m^-2); no s^-1 left in text or tables.
- m12 — resolved by removal: the 0.9996 rank correlation (Spearman of axis-distance against threshold differences) is no longer in the paper.
- m13 — resolved by removal: the 0.66 s lag (fitted, the earliest escape of a shifted exponential) is no longer in the paper.
- m14 — resolved: the "lost track" is gone; Sect. 7 states that all tracked participants pass, with the passed counts per run (135, 135, 129, 129, 128) and the duplicate IDs merged (Part D).
- m15 — resolved (group-level, framing plus model as F2/F3) — Sect. 1, Sect. 3.
- m16 — resolved (line goal: all 46 minima persist; 91 of 320 runs end in a standoff against 46 with the point goal) — Sect. 5.3 (05_deadlock_physics.tex:48); also Sect. 5.1 wall variants.
- A14 — resolved (legacy solver: repository pedestrian-abs, commits 9762177..e05d8f6, tag r2.0-baseline, line 113 of sim/steering/orca.py from commit c43af16, leg-normal inversion described in one sentence) — Sect. 6.1 (06_screening.tex:26); Sect. 1 (01_introduction.tex:13).
- A26 — resolved (group-level, discussion and end as M14) — Sect. 8-10.
- D14 — resolved (group-level, discussion and end as M14) — Sect. 8-10.

## Lens B: figures (findings listed in rev1/F_full.txt FIXES)

- B1 Fig. 1 hero — resolved (energy axes in m and J; k_BT_eff band; room inset removed; held/passes labels at the discs; stuck-alone map navy to grey, no yellow; ranges in the caption) — Fig. 1.
- B2 Protocol flowchart — resolved (greyscale, four classes, five self-contained steps, numbered list deleted from the text) — Fig. 3, Sect. 4.2.
- B3 New geometry figure — resolved (to scale, letter keys A-J defined in the caption, inserted in Sect. 3.4, door-edge terms defined against it) — Fig. 2, Sect. 3.4.
- B4 Lone-trap figure — resolved (caption names the four radii line styles and the blue lines, τ = 0.4 s upper, 0.6 s lower; 2000 of the 20 000 agents shown) — Fig. 4.
- B5 Width figure — resolved (all widths 0.70-1.00 m, logistic with pointwise band, bracket; no prediction curves per R2; right panel horizontal stacked bars with Wilson whiskers) — Fig. 5.
- B6 Escape and time-step figures merged — resolved (three panels, B3 high-β points, Kaplan-Meier panel dropped) — Fig. 6.
- B7 Quench figure — resolved (horizontal dot plot, cluster-bootstrap intervals, keystones-only right panel with bands) — Fig. 7.
- B8 Pair figure — resolved (legacy dash-dot and RVO2 solid identified; figure-only numbers such as push + 34/46 and −b* RVO2 5/46 now in the text) — Fig. 8, Sect. 6.3.
- B9 CroMa figure — resolved (shared category axis, open markers for incomplete runs, censored final gaps at 600 s) — Fig. 9.
- B10 Captions at most two sentences (Fig. 1 longer) — resolved — Figs. 1-9.
- B11 Percentile cluster-bootstrap intervals at 0/n and n/n — resolved ("none where every snapshot has the same outcome") — Figs. 7, 8.

## Lens C: tables

- C1 Table 1 as Symbol | Meaning | Value | Source in three blocks — resolved — Table 1.
- C2 Table 1 adds R, clip bounds, r_c, thresholds and horizons; N(·,·) as mean and SD; solver prose moved to the text — resolved (τ_orca, the gate constants (4, 2) and the 0.5 m capture radius remain text-only) — Table 1; Sect. 3.2, 3.4.
- C3 Table 2 class-column header — resolved — Table 2.
- C4 Table 2 cells that hold by definition marked — resolved (†) — Table 2.
- C5 Table 2 Observed block (RVO2, noise, bias, legacy, velocity filter) — resolved — Table 2.
- C6 Table 2 force-coupled ORCA's class at the pair — resolved (note a) — Table 2.
- C7 Table 3 split into 3a (noise) and 3b (bias per solver), velocity filter moved to the text — resolved — Tables 3a, 3b; Sect. 6.4.
- C8 Every column defined; "Lower" defined geometrically (y < 5 m) — resolved — Tables 3a, 3b notes.
- C9 Short table note for conventions — resolved — Tables 3a, 3b.
- C10 One J per comparison with the hypergeometric p; 20-seed J at the lone keystone — resolved — Table 3a; Sect. 6.1.
- C11 Per-run CroMa table of human and model flow — not resolved (dropped under the page limit; per-run values appear only as markers in Fig. 9) — Sect. 7.
- C12 Two significant figures for derived quantities — resolved after the audit fix pass (Table 3a/3b cells and Sect. 6-7 values through two-figure macros; p-values two figures down to 10^-3, then p < 10^-k) — Tables 3a, 3b; Sects. 6, 7.

## Lens D: prose

- D1 No question openers; sections open with their finding or scope — resolved — all sections.
- D2 Split overloaded sentences — partly resolved (several still carry four or more clauses, e.g. 06_screening.tex:26 legacy-solver sentence, 07_experiments.tex:23 flow sentence, 03_pedestrian_model.tex:63) — Sects. 3.4, 6.1, 7.
- D3 Undefined adjectives replaced by numbers ("exact", "comparable", "short stacks", "shallow", "hard-driven", "slow creep", "like for like", "usual") — resolved (none remain) — whole paper.
- D4 Process leakage — resolved after the audit fix pass (the 32-snapshot pool now carries its rule; "186 seeds", "first 100 of the 186", "207 noise settings", "refined level", "copied rate", "fit-half" gone) — Sects. 5.2, 6.
- D5 One name per concept (vocabulary v3), no symbol clashes — resolved in the text and tables (no bare "ORCA" for a configuration; classes are words; corner radius r_c); the Fig. 1 arrow label "ORCA" is a figure label (figure owner) — all sections.
- D6 Units in one style; upright k_B; "20 000"; "for 7 of 8 fits" — resolved (thin-space thousands, "covers 1 for 7 of 8 ... fits"); the Fig. 1 caption file still sets k_B in italic (figure owner) — Sects. 4, 5.
- D7 Results out of methods sections; few forward references — partly resolved (Sect. 4.2 states outcomes (14 s, 161 s, match from 70/85/425 s), Sect. 4.3 the Hessian result, Sect. 4.4 the variance ratio 1.00, Sect. 4.5 "56 of 60 pass", Sect. 3.2 the gate values) — Sects. 3.2, 4.2-4.5.
- D8 Captions at most two sentences, matched to the final text — resolved — Figs. 1-9.
- D9 "The SFM" as claim subject scoped; "pedestrian steering models" in general claims removed — resolved — whole paper.
- D10 No "exact", "if and only if", "as predicted" or "only" in the abstract — resolved — Abstract.

## Lens F: references

- F-1 Grover et al. cited for proposing perturbations — resolved (switching controller, not additive perturbations; grover2023 and grover2020) — Sect. 2 (02_related_work.tex:12); Sect. 8.2.
- F-2 Crowd-crush sentence (liang2024, helbing2012) — resolved (B_REPORT wording) — Sect. 1 (01_introduction.tex:9).
- F-3 "Freezing by heating" cited for noise unjamming — resolved (clause rewritten with xu2021, helbing2000freezing no longer cited) — Sect. 9 item (iv).
- F-4 CroMa source, run identifiers, licence — resolved (fzj_ped20219 plus boomers2023data; adrian2020 dropped; CC BY 4.0) — Sect. 7.
- F-5 xu2021 "boundary parameters alone decide" — resolved — Sect. 2 (02_related_work.tex:6).
- F-6 gronbechjensen2013 — resolved (BBK off by O(Δt); Δt-dependent temperature claimed as own derivation) — Sect. 2 (02_related_work.tex:9).
- F-7 wolinski2014parameter — resolved — Sect. 1.
- F-8 zuriguel2014 "people" — resolved ("simulated pedestrians") — Sect. 2.
- F-9 fiorini1998 time horizon — resolved (horizon moved to vandenberg2011) — Sect. 2.
- F-10 McNemar and Wilson citations dropped (method names kept); Kaplan-Meier and Weibull kept — resolved — Sect. 4.6, 4.5.
- F-11 woillez2020 renamed to woillez2019; arXiv duplicates dropped — resolved (duplicates remain in refs.bib but are not cited or printed) — Sect. 2; bibliography [44].
- F-12 New sources placed: Langer, Henkelman (climbing image), Mel'nikov-Meshkov, van den Berg ICRA 2011 Eq. (7), Moussaïd 2011, Pastor 2015, Garcimartín 2017, Janda 2009, Dergachev CASE 2021, Tordeux 2016, Chraibi 2010, Lakoba 2005 — resolved — Sects. 2, 3.2, 4.5, 5.2.
- F-13 Bottleneck-flow references for the experiment comparison — resolved (measured bottleneck flow grows with width, seyfried2009, hoogendoorn2005) — Sect. 7.
- F-14 Weidmann 1993 — partly resolved (DOI added; γ = 1.913 m⁻² and ρ_max = 5.4 m⁻² in Table 1 are not yet checked against the original table, an outstanding action in B_REPORT) — Table 1.
- F-15 RVO2 citable version (Zenodo v2.0.2, commit c96a6ec) — resolved — Sect. 3.2; bibliography [4].
- F-16 Bibliographic corrections (Liu et al. Robotica 44(4), Woillez article 258001, Farkas/Vicsek names, article numbers) — resolved — bibliography.

## Points the referee would still dispute

1. 00_abstract.tex:3 — "Replay, time-step dependence, time to free and whole-run final states separate noise from force-coupled ORCA". Sect. 4.2 (04_protocol.tex:15) says replay and per-step Δt dependence separate "by definition", and that time to free is a paired effect size, not a separating probe (C_REPORT A7: "time to free is empirical, not class-defining"). The abstract presents two tautological separations and one non-defining one as findings, and it contradicts Sect. 4.2.
2. 00_abstract.tex:3, 01_introduction.tex:28, 05_deadlock_physics.tex:39 — "Noise frees the lone trap by activated escape over an effective barrier 0.86–0.93 of the computed one" / "about 0.9". The 0.86–0.93 comes from three snapshots in the alone condition (B3). In the full condition the median slope ratio is 1.15 and in the pinned condition 0.95 (05_deadlock_physics.tex:41). The single range is generalised to "the lone trap" without scoping.
3. 05_deadlock_physics.tex:45 with 00_abstract.tex:3 — at the noise level fraction-matched to force-coupled ORCA (σ = 0.07 m/s), β has median 0.64 and is below 1 for 36 of 56 barriers, so "the Arrhenius test does not cover the matched level". The abstract and Sect. 8.1 (08_discussion.tex:4: "noise carries the blocker over its barrier (Heat)") still describe the matched noise as activated escape. This is an extrapolation outside the Kramers regime.
4. 00_abstract.tex:3 — "Velocity noise and a lateral bias, each fraction-matched to force-coupled ORCA at a stated horizon". At the second trap noise is not matched (Δ = +0.25 [0.08, 0.44] on the screen, +0.13 on all 160; 06_screening.tex:24). The match holds at lone keystones and in whole runs only, and the abstract does not say so.
5. 04_protocol.tex:13 — "fraction-matched at horizon T: the 95% interval of the paired difference ... covers zero". This is a failure to reject, not equivalence. No margin is set, and with 34 snapshots the interval spans about ±0.1 (Table 3a). The criterion also mixes unadjusted intervals with Holm-adjusted tests: in Table 3a the second-trap row is declared unmatched on its interval [0.08, 0.44] although its Holm p is 0.062.
6. 06_screening.tex:19, 29 and Table 3a — "overlap as much ..., so overlap does not separate noise from ORCA". No test compares the noise–noise J with the noise–ORCA J. At whole runs the text quotes "J = 0.48 against 0.33 for independent sets; Table 3a", but Table 3a reports noise against force-coupled ORCA as J = 0.41 (0.30), p = 0.0020. So the cited numbers are not in the table, and the overlap is above independence.
7. 06_screening.tex:48 and Table 3b — the bias–ORCA separation rests on handedness, and for the RVO2 solver that rests on 7 freed standoffs (2 of 7 against 8 of 8; Holm p = 0.028). With 46 pair snapshots the Δ intervals are about ±0.15 (admitted in 08_discussion.tex:10). "The probes separate each surrogate from force-coupled ORCA" (08_discussion.tex:4) is stronger than this sample supports for RVO2.
8. 06_screening.tex:51 — "The ORCA velocity filter ... frees no deadlock, as the identity of Sect. 3.2 requires." Eq. (7) concerns the force coupling. The filter's lack of a rest drive follows from the half-plane slack argument in the next sentence, not from the identity. As written this is a non sequitur.
9. 05_deadlock_physics.tex:39 — "We restarted 10 of the 32 gate-accepted snapshots". Sect. 4.5 says 56 of 60 pass the gate. The 32 also require at least two residual agents (C_REPORT A5), and the rank rule that picks the 10 is not stated, so this is an unexplained selection.
10. 05_deadlock_physics.tex:16 — "The SFM drive (median 214 N) ... The rest drive of force-coupled ORCA (RVO2, median 215 N)". Read with Sect. 3.2 ("1.8–2.2 times the SFM's"), the two medians look contradictory. The 215 N is the added ORCA term alone, and the text does not say so.
11. 05_deadlock_physics.tex:22 — "Each wall law gives one deadlock type". With the default walls 2 of 98 classified deadlocks are pair or group standoffs, in the same paragraph. The claim needs "predominantly" or the counts in the claim.
12. 05_deadlock_physics.tex:57 — "At 3 m/s arches are rarer ...; at 2 m/s and the default drive none form". Those cells ran at Δt = 0.01 s (experiments/runs3/N5.py:9-10), the step the same paragraph calls under-resolved for contacts. Only the 5 m/s result is shown at a resolved step.
13. 07_experiments.tex:9 — "People at a 0.8 m bottleneck do not deadlock". This generalises from five runs of one experiment series with instructed, partly motivated participants who kept a 2 m semicircle clear. It should be scoped to the CroMa runs, as the abstract is.
14. 01_introduction.tex:31, 07_experiments.tex:25, 09_conclusions.tex:2 — "removing the deadlocks leaves the model unrealistic" / "does not make the model realistic". The flow deficit is measured with uncalibrated default parameters (Table 1 desired speeds; Weidmann reduction over R = 3 m), four variants and one observable at one width. It says the defaults under-predict flow. It does not show that the deadlock mechanisms are unrealistic, and calibration could close the deficit. The sentence is broader than the test.
15. 07_experiments.tex:12 — rendered "All recorded participants pass the entrance (135, 135, 129, 129 and 128 duplicate track IDs merged in 4D040 and 4D110)". The `\;` after the last macro prints a thin space, not a semicolon, so the sentence reads as if 128 IDs were duplicates. The sentence also omits that the archive registers 161, 160, 132, 132 and 129 participants (C_REPORT D1), so 26 registered people in 4D030 have no track.
16. 04_protocol.tex:51 — "A split-sample check fits the surrogate on half the snapshots and tests it on the rest." No result of this check appears anywhere in the paper.
17. 06_screening.tex:51 — "On 100 whole-run seeds 1 run completes under the filter and 1 under SFM, against 54 under force-coupled ORCA". Sect. 6.2 and Table 3a use 186 seeds (101 complete). The relation of the 100 to the 186 is not stated.
18. tables/table2_signatures.tex:19 — the Heat row predicts "frees, exponential times". Sect. 5.2 (05_deadlock_physics.tex:43) reports over-dispersed escape times (Weibull shape 0.64 and 0.68) at the deepest barrier, so the prediction fails in part of the data, and Table 2 does not note it.
19. 01_introduction.tex:9 — "A surrogate tuned to the same outcome shows that a simpler cause suffices" and "a simulation that plans such a place is as trustworthy as the mechanism behind its bottleneck behaviour". Both are unsupported general assertions with no citation or evidence in the paper.
20. 01_introduction.tex:28 — the stuck-alone criterion "brackets the critical width". The bracket is 0.75–0.92 m around w50 = 0.878 m, and the parameter-free prediction from the same criterion misses w50 by 0.041 m (05_deadlock_physics.tex:20). A contribution resting on a 0.17 m bracket and a failed prediction will be called weak.
21. tables/table1_params.tex:21 — "k_ttc ... 1.5 N s² [28]". Karamouzas et al.'s k scales an energy, while here the same number scales a force magnitude in other units, so the source does not supply this value. τ_orca = 0.5 s, the gate constants (4, 2), the 2v0 speed cap and the 0.5 m capture radius are not in Table 1.
22. tables/table1_params.tex:16 — γ = 1.913 m⁻², ρ_max = 5.4 m⁻² cited to Weidmann [43] without a check against the original table (outstanding in B_REPORT).
23. 07_experiments.tex:23 — model and human flows are compared with no reference to measured bottleneck flow-width relations (seyfried2009, hoogendoorn2005 are in refs.bib but not cited).
24. Bibliography [19] — Grover et al., IJRR 42(6), printed with year 2022, while volume 42 is the 2023 volume. Either the year or a note on online publication will be queried.
25. 06_screening.tex:19, 29, 48 — bare "ORCA" for a configuration ("noise from ORCA", "noise and ORCA do", "bias and ORCA") after the paper defines two distinct configurations. 05_deadlock_physics.tex:16, 41: "20000" and "covers 1 in 7 of 8, 9 of 10 and 9 of 10 fits", both flagged in the review's prose lens.
26. Tables 3a/3b and Sects. 6.1, 7 — derived quantities with three significant figures ("19.3 [9.1, 29.1]", "71.9 [33.2, 110.1]", "80.8 s", "237.2 s", "0.0223") against the stated two-figure rule (04_protocol.tex:51).
27. 05_deadlock_physics.tex:8 — the Fig. 4 caption does not identify the two blue margin-zero lines (τ = 0.4 s and 0.6 s) or the line style of each radius, so the reader cannot decode the figure from its caption.

## Disputes addressed in the audit fix pass

- Abstract vs Sect. 4.2: the abstract now says replay and the time step separate noise by definition, time to free and final state empirically.
- Barrier 0.86-0.93: scoped to the blocker alone (three snapshots, beta = 1.5-7); the full-condition median ratio is stated in Sect. 5.2.
- "Fraction-matched" scoped to the lone keystones and whole runs; Table 3a caption and Table 2 note say the second-trap row is not matched.
- Match rule: Sect. 4.2 states that a fraction match (95% interval of the paired difference covers zero) is not an equivalence test and is decided apart from the Holm-corrected probe tests.
- Overlap J in Sect. 6.2 now quotes the Table 3a macros with the hypergeometric p.
- Sect. 6.4 reasons from the filter itself (every half-plane admits v = 0 at rest), not from the force-coupling identity.
- CroMa: "no participant deadlocks" scoped to the five runs; the rendering bug in the participant counts fixed.
- Split-sample check sentence deleted (no result reported); arch absence at 2-3 m/s and the default drive scoped to dt = 0.01 s in Sect. 5.4 and in Limitations.
Still open (the referee would still dispute): the fraction match is not an equivalence test (stated, not changed); activated escape is established in the alone condition at beta >= 1.5, while the matched noise level has median beta 0.64; human data are five runs at one width; the model runs with uncalibrated defaults.
