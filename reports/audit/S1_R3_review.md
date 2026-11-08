# Referee 3 report

Manuscript: "One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models" (P. Gang, A. Veluri). Invited LNNS extended version of the SIMULTECH 2026 paper "A Diagnostic Methodology for Failure-Mode Ablation of SFM, TTC, and ORCA Pedestrian Steering Paradigms" (pp. 474-481, DOI 10.5220/0015190200004094).

Version reviewed: snapshot at commit decbdca (`main.tex`, 1353 lines; `main.pdf`, 23 pages; `build.log`). All line numbers refer to `main.tex`. Reviewer role: senior SIMULTECH/LNNS referee and volume editor.

Not counted as defects (known gaps): Table 4 and Sect. 6.3 (lines 1138-1143), the Zenodo DOI (line 1182) and the acknowledgements/disclosure (line 1184). Where these gaps affect a recommendation below, I say so explicitly.

---

## 1. Summary (five sentences)

The paper asks whether a "minimal control" that is tuned to reproduce a steering paradigm's headline completion rate (here, velocity noise or a lateral bias standing in for ORCA in a social-force bottleneck) shows that the paradigm and the control share a mechanism. It answers no: the authors define five physically motivated mechanism classes (prevent, reshape, heat, steer, glitch), predict how each class responds to probes of stored frozen deadlock states (quench, 1e-9 m replay, time-step change, signed constant push, bias reversal, corrected numerics), and prove a rest-state lemma that rules out every force term that vanishes at rest. Applied to their SFM/TTC/ORCA hybrid at a 0.8 m door, the protocol finds two deadlock classes (a lone agent held by the door-edge wall force, and a symmetric pair standoff that is a strict energy minimum removed at a fold). At the lone trap, ORCA acts as a deterministic extra goal drive while rate-matched noise acts by activated escape over computed barriers; at the pair, ORCA acts through its constraint part, differently in the two solvers, while a rate-matched bias acts through a handed fold. A like-for-like rebuild of the CroMa 0.8 m experiments shows that no model variant reproduces human flow: every variant either deadlocks or passes 0.40-0.59 of the human rate.

The contribution can be stated crisply: *a rate-matched control can reproduce a paradigm's success while acting by a different mechanism, and probes of frozen deadlocks derived from the model physics can separate the two.* The manuscript does not state it this crisply. It is buried under a very high density of numbers, and the generic protocol takes up only six lines (line 1020).

## 2. Scores (1 = poor, 5 = excellent)

- Originality: 4. Applying interventional, physics-derived signatures to frozen deadlocks to test a rate-matched control is new in crowd simulation, and the lone-trap/pair-standoff physics is a genuine finding.
- Significance: 3. The physics is clean, but the transfer to ORCA as practitioners use it (velocity level) and to other models is asserted, not shown (Major 1, 2).
- Soundness: 3. The lone-trap attribution (drive split, signed push, replay, time-step scaling) is convincing. The "different deadlocks" leg rests on Jaccard indices that have no same-mechanism reference, and the lone-trap noise level was chosen after the fact (Major 3, 4).
- Clarity: 2. The prose is dense with numbers, carries a lot of jargon ("keystone", "second trap", "frozen-mean arm", "fold", "rest drive"), and the abstract is hard to parse (Major 5).
- Presentation: 3. The figures are good and consistent. Table 3 runs 48 pt into the margin, internal experiment codes leak into the text, and two table captions are over the two-sentence limit (Major 6, minors).
- Venue relevance: 4. Methodology for attributing simulation behaviour suits SIMULTECH/LNNS well, once the methods contribution leads.

**Recommendation: major revision.** The extension clearly meets the novelty bar. The attribution logic needs a proper null for "same mechanism", and the framing must be scoped to the model actually studied. The remaining computation is small: about 15-20 CPU-hours in total (Major 3, 4, 2).

---

## 3. Major issues

### M1. The ORCA result belongs to the additive force hybrid, not to ORCA; the title, abstract and practitioner advice generalise beyond it
**Where:** title (line 13); abstract (line 652, "ORCA adds a goal drive"); Sect. 3, "ORCA as a force" (lines 916-920); Sect. 6.1, "ORCA is its rest drive" (line 1110-1111); Discussion (line 1166, "At rest ORCA's velocity is a second goal drive"); Implications (line 1169).
**Problem:** In Eq. (6) the LP velocity is turned into a relaxation force, m(v_orca - v)/tau_orca, which is *added* to the SFM desired force (Eq. 1). Its preferred velocity is v0·e (line 916). At rest with no binding constraint, the model therefore applies the goal drive twice. The finding "ORCA = extra goal drive" (class L) follows directly from this design choice, and the paper never says so. A practitioner running RVO2 at the velocity level (no added SFM drive, the LP output is the velocity) has no "rest drive" at all. Whether such an agent deadlocks at the door edges, and by which class, is untested.
**Why it matters:** For an ORCA user this is the headline practitioner takeaway, and as written it is mis-scoped. The title "Pedestrian Steering Models" (plural) and "ORCA adds a goal drive" invite readers to conclude something about ORCA in general.
**Fix:** (a) Say explicitly, in Sect. 3 and again in Sect. 6.1, that the rest drive comes from the force conversion inside an additive hybrid (cite the conversion source used in the conference paper, Guy et al. 2010; check). (b) Rename Sect. 6.1's paragraph "At the lone keystone, the hybrid's ORCA term acts as its rest drive". At the second trap ORCA does *not* equal its drive (17 vs 24 of 26, line 1120). Pooled over all 60 snapshots, the drive-only minus C3 RVO2 difference is +0.12 (data/derived/E2_analysis.json). (c) Scope the title to the model studied (Sect. 6 of this report). (d) Optionally add one small run that settles transfer: a velocity-level RVO2 variant (ORCA velocity applied directly, desired force off).
**Run (optional but recommended):** corrected-forward room, w = 0.8 m, 100 agents, velocity-level RVO2. n = 50 seeds (42-91), 600 s cap. Outputs: completion with Wilson 95% interval; deadlock class by the keystone test; and a quench of the 34 lone-keystone snapshots under the same update rule. Cost: about 50 × 60-90 s ≈ 1.3 CPU-h for whole runs plus under 0.5 CPU-h for quenches, so about 0.5 h wall on 4 cores.

### M2. The methods contribution is under-specified for a simulation-methods audience
**Where:** contribution bullet "Method" (line 834); Sect. 4 (lines 981, 1019-1020); Discussion, "Clogging and robot deadlock" (line 1172).
**Problem:** The generic protocol ("Calibrate, then falsify") gets six lines at the end of Sect. 4.3 (line 1020). Table 2 lists four of the five classes (N has no row, line 929). The probes are partly tailored to the hypothesis under test: the "goal push" equals ORCA's rest drive (line 981). The paper gives no guidance on how a modeller would choose probes for a different paradigm or model. It also does not list the prerequisites the protocol needs: a storable and restartable state; a deterministic replay; a rest field that is conservative once densities are frozen (needed for the barriers); and a way to switch off single terms. Velocity-based models such as pure ORCA, or speed models, have no potential, so the barrier/T-class machinery does not carry over directly. Even so, line 1172 states that "wherever a resolver is credited with removing an equilibrium, the protocol carries over".
**Why it matters:** SIMULTECH readers take away a method, not a social-force deadlock taxonomy. As written, they cannot apply the protocol to their own model.
**Fix:** Move the protocol to the start of Sect. 4 as a numbered algorithm box (inputs, steps, decision rule, outputs). Add an N row to Table 2, or remove N from the five-class claim. Add a short subsection, "Applying the protocol to another model" (about 0.4 pp), that lists the prerequisites above, separates generic probes (replay, time-step scaling, signed push, symmetry reversal) from model-specific ones (barrier computation), and gives the computational cost of a snapshot library relative to an ordinary parameter sweep. Soften line 1172 (Sect. 6 of this report). No new runs are needed.

### M3. "Free different deadlocks" has no same-mechanism reference; the Jaccard evidence does not support the claim as worded
**Where:** abstract (line 652, "yet free different deadlocks"); bullet "Attribution" (line 836); Sect. 6.1, "Matched noise acts differently" (line 1114); "Matched completion of whole runs" (line 1123); Table 3, J column (lines 1095, 1099, 1103, 1105); Discussion (lines 1163, 1166).
**Problem:** Identity of the outcome sets is compared through the Jaccard index J of the minority sets. Two things are missing.
1. *No same-mechanism null.* A stochastic arm compared with *itself* (a second, independent noise seed stream), or a chaotic deterministic whole run compared with itself under 1e-9 m perturbation, also gives J < 1. In 600 s whole runs at w = 0.8 m the outcome is known to be chaotically sensitive: the authors' own correction ledger reports platform-level floating-point differences flipping outcomes. So J = 0.41 in whole runs is not evidence of a different mechanism until it is compared with the noise-vs-noise and C3-vs-perturbed-C3 values. Note also that J = 0.41 [0.32, 0.50] lies *above* the independence value 0.30. The failure sets overlap more than chance: 50 of the 122 failing seeds are shared, from discordant counts 35:37.
2. *Tiny sets at the lone trap.* With 30/34 freed by ORCA and about 87% by noise, each minority set holds only a handful of snapshots. J = 0.20 [0.00, 0.50] corresponds to about one shared snapshot (check). Independent sets of that size would give an expected J of about 0.06-0.1, so the observed overlap is not below chance. At the pair (RVO2), J = 0.00 for sets of 7 and 8 out of 46. That is compatible with independence (expected overlap about 1.2), and the reported interval [0.00, 0.00] is degenerate.

The *other* signatures are strong and do not suffer from this: time-step scaling (Fig. 5), replay, the signed push and handedness. The paper's conclusion survives. The "different deadlocks" leg, as worded, does not.
**Why it matters:** "Same rate, different deadlocks" appears in the abstract, the contributions, the discussion and the conclusions. A careful reader will spot the missing null.
**Fix:** For every J, report (i) the independence expectation and (ii) a same-mechanism reference J. The lone-trap reference needs no new runs: split the five noise seeds per snapshot into two pseudo-replicates and compute noise-vs-noise J. Reword the identity claims to "partly different" unless J falls clearly below the same-mechanism reference. Report a sensible interval for J = 0 cases (for example, a bootstrap over snapshots with a percentile method that can exceed 0), or drop the interval.
**Run (whole runs):** E6 configuration (corrected-forward, w = 0.8 m, 186 seeds, 600 s). (a) C1 + sigma* with an independent noise stream on the same spawns: 186 runs. (b) C3 RVO2 with the spawn perturbed by 1e-9 m: 186 runs. Outputs: completion, failure sets, J for noise-vs-noise, C3-vs-C3 and noise-vs-C3, each with independence expectation and 95% interval. Cost: (a) 186 × 60-90 s ≈ 3-4.7 CPU-h; (b) ORCA is slower, about 6-9 CPU-h. Total about 9-14 CPU-h, so 2.5-3.5 h wall on 4 cores.

### M4. The lone-trap noise "match" was chosen after the fact, from three pre-set levels and within one stratum
**Where:** Sect. 6.1 (line 1114, "Per-step noise at sigma = 0.07 m/s matches that rate"); Table 3 (line 1095); Discussion (line 1163).
**Problem:** The quench library ran noise at sigma = 0.03, 0.05 and 0.07 m/s (Fig. 6). sigma = 0.07 matches C3 RVO2 *only* in the lone-keystone stratum: 148/170 against 30/34, Delta = -0.01 [-0.10, 0.08]. Pooled over all 60 snapshots, sigma = 0.07 overshoots (Delta = +0.10 [0.003, 0.20]) and sigma = 0.05 matches better (Delta = -0.05 [-0.14, 0.05]); in the second-trap stratum sigma = 0.07 overshoots by +0.25 (data/derived/E2_analysis.json). Step 2 of the protocol (line 1020) says "tune the control's single parameter to the target's completion rate". For whole runs this is done properly by inverting the completion fit (sigma* = 0.0467, line 1123). At the lone trap it is not.
**Why it matters:** The protocol claims calibration *before* falsification. Picking whichever pre-set level happened to match, in whichever stratum, is a researcher degree of freedom the paper should remove or disclose.
**Fix:** Either (a) state plainly that sigma = 0.07 is the nearest of three pre-set levels in the lone-keystone stratum and that the stratum was defined before the noise runs, with evidence; or, better, (b) invert a logistic fit of freed fraction against sigma in the lone-keystone stratum, rerun at the inverted sigma, and report the probes there. The time-step signature (Fig. 5) already shows noise is class T at any level, so the conclusion will not change. The calibration then follows the protocol as stated.
**Run:** 34 lone-keystone snapshots × 5 seeds at the inverted sigma (plus one bracketing level), 120 s quenches: 340 quenches. Few agents remain, so a quench costs well under a room run (≤ 30 s), about 1-3 CPU-h, under 1 h wall.

### M5. Title, abstract and story are hard to follow for the target audience
**Where:** title (line 13); abstract (line 652); Introduction (lines 826-839); Sects. 5.1 and 6.1 (lines 1029-1037, 1110-1123).
**Problem:** The abstract (197 words) leaves ORCA and CroMa unexpanded, uses "fold", "goal drive" and "activated escape over computed barriers" without context, and packs three matched controls into one sentence of 50 words ("Noise matched to ORCA's rate at the lone trap, noise matched to its completion of whole runs and a bias matched to it at the pair reproduce the rate, yet free different deadlocks and differ in replay, time-step dependence or handedness: ..."). Its last sentence (CroMa) is not connected to the thesis. In the body, single paragraphs carry 15-25 numbers each (for example, line 1035 has more than 30). Internal coinages (lone keystone, second trap, frozen-mean arm, rest drive, minority outcome set) pile up faster than a methods reader can absorb. The modeller's takeaway ("check g_max(r) against m v0/tau before reading deadlock rates; name your ORCA solver; noise temperature depends on Delta t") is good, but it is spread over line 1160 and line 1169.
**Why it matters:** The volume's readers are simulation methodologists. The paper must lead with the method and the lesson, not with the numbers.
**Fix:** Adopt a revised title and abstract (proposals in Sect. 6 of this report). Move secondary counts from Sects. 5.1 and 6.1 into Table 3 or a new compact table, keeping at most about five numbers per paragraph in the main text. Add a short glossary sentence for the coined terms when they first appear in Sect. 4. Merge the practitioner points at line 1160 and line 1169 into one boxed "Checklist for modellers" (about 6 lines) at the end of Sect. 8.

### M6. Table 3 is overfull and exposes internal experiment codes
**Where:** Table 3 (lines 1086-1109); `build.log` line 1394: "Overfull \hbox (47.91664pt too wide) in paragraph at lines 6--25" of table3_matched.tex. This is visible on page 16 of the PDF, where the table extends about 1.7 cm into the right margin.
**Problem:** Springer production will reject a 48 pt overrun. The caption and the block headers use internal codes "(E2)", "(E6)", "(E7b)" and "(E3)" (lines 1087, 1094, 1098, 1102), which the paper never defines. The ℓ column for the lone-trap row comes from a *different* sample (20 snapshots from the time-step experiment, not the 34 lone keystones), which the row layout hides. The t_1/2 column reads ">120" for all four pair rows and so carries no information there. The caption has three sentences (Minor 1).
**Fix:** Drop the internal codes and name the sample in words ("lone-trap library", "whole runs", "pair library"). Move ℓ to a footnote or to the Fig. 5 caption, stating its sample. Drop t_1/2 from the pair block, or replace it with the fold threshold b*. Use `tabularx` with \textwidth or `\resizebox`; removing two columns should be enough to fit.

### M7. Overstated certainty in several load-bearing sentences
**Where:** lines 652, 835, 836, 1035, 1110, 1117, 1120, 1123, 1136, 1163, 1166, 1172, 1177. The exact replacements are in Sect. 6 of this report.
**Problem:** Several claims go beyond the evidence:
- non-significance is read as identity ("Both matches reproduce the rate", p = 1.000, while the paper itself concedes that n = 46 cannot show equivalence);
- a consistency check is presented as an empirical law (393 of 393 is the deterministic single-agent restart agreeing with a static criterion computed from the same force law);
- "derived from the physics before the runs" (line 1163) is asserted without verifiable pre-specification;
- "no-fit prediction" (line 1123) uses an attempt rate fitted in Sect. 5.4.
**Fix:** Adopt the replacements in Sect. 6, or document the pre-specification (for example, a dated commit hash of the signature table in the repository) and say so in Sect. 4.

---

## 4. Minor issues

1. **Captions over two sentences** (authors' rule). Table 2 caption (line 929) has three sentences; Table 3 caption (line 1087) has three. Fig. 1 (line 822) has two but is about 150 words, which is too long for print. Move the colour and arrow key into the text of Sect. 1, or cut the caption to about 60 words.
2. **Clinical-trial vocabulary** (authors' rule). "arm"/"arms" for interventions appear at line 926 ("(an arm)", "arms are compared"), line 981 ("the frozen-mean arm"), line 1083 ("the arms that free"), line 1092 (Table 3 header "Arm") and line 1133 ("Every deterministic arm"). Replace with "intervention" or "variant", and "frozen-mean push" for the probe. ("Lever arm" at line 1053 is fine.)
3. **Notation overloads.**
   - g is the goal (line 890), the ramp max(0,x) (line 899) and g_max(r) (line 1029).
   - sigma is the noise amplitude and also the sigmoid in Table 1 (lines 867-868), while Eq. (6) uses s(·) (line 920). Use s throughout.
   - k is the body-compression constant and the Weibull shape (line 1017).
   - tau is the relaxation time, the TTC time (line 842) and tau_h/tau_0/tau_orca.
   Rename the ramp (for example, h(x)) and the Weibull shape (for example, k_W).
4. **Symbols used before definition.** w_c,i appears in Eq. (1) (line 885) but is defined only at line 920. e_i-perp (line 923) is undefined. ΔU_cond appears in the Fig. 4 caption (line 1062) and is never defined in the text. β_ref first appears in the Fig. 5 caption (line 1077) before the text (line 1117) defines it.
5. **Table 2** (lines 928-980). The "Corrected numerics" column reads "persists" in every row, so it discriminates nothing without the absent N row. Add the N row ("disappears"), or move N into the caption only and drop the column.
6. **AUC against accuracy baseline** (line 1037): "AUC 0.975 ... against an all-exit baseline accuracy of 0.931" compares unlike quantities (the AUC baseline is 0.5). Report accuracy against the all-exit baseline, or AUC alone.
7. **Attempt rates** (line 1067): medians are given for full and alone only. Give the frozen value too, or say why it is omitted.
8. **Kramers prefactor**: the fitted attempt rates (0.13 s^-1, line 1067) are never compared with the Kramers/Langer prefactor computable from the Hessians at the minimum and the saddle, which the authors already have from the string method. Doing so would give a genuinely no-fit rate test (Question 7).
9. **β_ref = 2.5 prediction outside the interval** (line 1117, 3.70 vs [2.96, 3.52]). Give a sentence of physics, for example the (ωΔt)^2 correction mentioned at line 1008 or censoring at 900 s (check).
10. **Sect. 5.1 wall-variant paragraph** (line 1035). It packs eight p-values and twelve counts into one paragraph that Fig. 3 already shows. Keep the critical width and the jamb-only result; move the rest into the Fig. 3 bars.
11. **"20000" vs "20 000"** (line 282 macro used at line 1033, against the caption at line 1026). Use 20\,000 consistently.
12. **Spelling.** "vermillion" (lines 1062, 1077, 1083, 1148) vs "vermilion" (line 822). Use "vermilion".
13. **Fig. 1 overlay font.** `build.log` line 1372 reports "Font shape T1/cmr/m/n in size <6.5> not available, size <6> substituted". Labels set at 6 pt (lines 692-700 onward) are at the limit of legibility in print. Use 7 pt with a font that has the size (for example, `\usepackage{lmodern}`). The energy panels on the right of Fig. 1 have no axis label; the scale bars are acceptable, but say "energy" in the caption.
14. **Fig. 5** (line 1076) is included without a width (`\includegraphics{figures/fig5_dt.pdf}`). It sits at about 0.45 \textwidth. That is fine, but set `width=` explicitly so it stays consistent with the other figures.
15. **Fig. 4 left** (line 1062): the "full" condition reaches only 0.68 escaped by 300 s. State the censoring fraction in the text (line 1065).
16. **Undefined acronym in the abstract**: ORCA and CroMa (line 652). Expand them, or avoid them.
17. **Keywords** (line 653): "Mechanism attribution" is good. Consider adding "Model verification" or "Simulation methodology" so SIMULTECH indexing picks the paper up.
18. **The model section's "speed cap 2v0"** is given twice in Table 1 (lines 867 and 870). Remove one.
19. **The validity section's start conditions** (line 1151): model agents start at rest and farther from the entrance. Flow is measured first-to-last passage, so a start-up transient is excluded, but say so explicitly. Say also which CroMa motivation condition each of the five runs belongs to (Question 6).
20. **Alt text**: the venue notes (plan/VENUE_REQUIREMENTS.md item 4) say alt text is required for non-text content. Prepare alt text for Figs. 1-8 for production.
21. **Table 4 scope (note for the pending section, not a defect).** Line 863 says only that "calibrated values of the conference paper are not applied". When Table 4 is written, it should state explicitly that the *conference runs* also used the 3 m disc density (not the Voronoi estimator the conference paper describes), the uncalibrated Weidmann parameters, the sign-flipped ORCA leg normal and the crush term in C4. Otherwise a reader of the conference paper cannot reconcile the two methods sections.
22. **References hygiene** (lines 1193-1349):
   - Every entry prints both the DOI and an http://dx.doi.org URL. Drop the `url` fields where a DOI exists. That saves about 0.7 page and removes the underfull-box warnings (`build.log` lines 1401-1497).
   - Lower-casing: ref. 8 "sfm, ttc, and orca" (line 1238); ref. 4 "rvo2 library" (line 1213); ref. 14 "kramers" (line 1274); ref. 13 "love parade" (line 1270); ref. 20 "seoul halloween" and "WONG, S.C." (lines 1311-1312); ref. 2, where the German nouns must be capitalised: "Über die Reaktionsgeschwindigkeit bei der Inversion von Rohrzucker durch Säuren" (lines 1200-1201). Protect capitals with braces in the .bib.
   - Ref. 1 (line 1196): year "2026" for a 2021 dataset DOI (10.34735/PED.2021.9). Use the dataset year (check) and add the paper that describes the CroMa experiments (check).
   - Ref. 3 (lines 1205-1208): book chapter without the book title (Robotics Research, ISRR 2009, STAR vol. 70; check).
   - Ref. 10 (lines 1251-1255): key `grover2020`, year 2021, no book title (Algorithmic Foundations of Robotics XIV, SPAR vol. 17; check).
   - Ref. 17 Koren and Borenstein (lines 1291-1296): the year field is missing.
   - Ref. 4 (lines 1211-1216): the note "library version 2.0.3 (main branch CMakeLists.txt); Zenodo record 7039667 is tagged v2.0.2" reads like a working note. Shorten it to "version 2.0.3".
   - `\nocite{gang2026}` (line 1186) is redundant, since the paper is already cited.
23. **Minor overfull box**: `build.log` line 1381 reports 2.1 pt in the "Deadlock in multi-agent systems" paragraph (line 851). Harmless, but trivially fixable.

---

## 5. Questions to the authors

1. Under noise (five seeds per snapshot), how is a snapshot classed as "unresolved" for J (line 1114): by a majority of seeds, by any seed, or by all? How large are the two minority sets at the lone keystone?
2. What is the noise-vs-noise J (two disjoint seed subsets) at the lone trap, and the C3-vs-perturbed-C3 J in whole runs? (Major 3)
3. Is there a dated record (commit or file) showing that the probes and predictions in Table 2 were fixed before the corresponding runs? If so, cite it in Sect. 4. If not, remove "before the runs" (line 1163).
4. Were the noise levels 0.03, 0.05 and 0.07 m/s and the lone-keystone stratum fixed before the quench results were seen? (Major 4)
5. Does a velocity-level RVO2 agent (no added SFM drive) deadlock at your door edges, and if so, in which class? (Major 1)
6. Which motivation condition does each of the five CroMa 0.8 m runs belong to, and is the "0.21 m corridor" (line 1151) correct (check)? Does the human flow differ between conditions more than the model-human gap?
7. How does the fitted attempt rate (0.13 s^-1) compare with the Kramers/Langer prefactor computed from the Hessians at the minimum and the saddle?
8. The paired difference at the lone trap compares 170 noise runs (five per snapshot) with 34 deterministic outcomes (Table 3, line 1095). Was the bootstrap clustered by snapshot?
9. How was the interval [0.00, 0.00] for the pair RVO2 J computed (line 1105)?
10. Do the two deadlock classes and the attribution survive a change in agent number (for example, 50 agents, as in the conference bottleneck) or room aspect ratio? A sentence of reasoning would be enough if no runs are planned.
11. The keystone test (line 1035) restarts the same deterministic force law that defines g_max(r). Is there any case in which the two *could* disagree (off-axis blockers, inertia overshoot)? If not, present 393/393 as a verification of the criterion, not a finding.
12. What is the wall-clock cost of building the 60-snapshot library and running the full probe set, compared with the completion sweeps it replaces? Practitioners will ask.

---

## 6. Overstated claims and exact replacements

| Line | Current wording | Acceptable replacement |
|---|---|---|
| 13 | "One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models" | "Same Rate, Different Mechanism: Probing Frozen Deadlocks to Attribute Deadlock Resolution in a Social Force Bottleneck Model" (or keep the first clause: "One Matched Control Is Not Enough: Probing Frozen Deadlocks in a Social Force Bottleneck Model") |
| 652 | "reproduce the rate, yet free different deadlocks and differ in replay, time-step dependence or handedness: ORCA adds a goal drive, noise drives activated escape over computed barriers." | "reproduce the rate but differ in replay, time-step dependence or handedness and free partly different deadlocks: in this hybrid model, ORCA's force term acts as an extra goal drive, whereas noise acts by activated escape over computed barriers." |
| 835 | "and contact arches formed at high drive never persist, because the model has no static friction" | "and contact arches formed at a mean desired speed of 5 m/s broke within 2.9 s in all 25 runs, as expected for a model without static friction" |
| 835 / 1035 | "a stuck-alone criterion that holds in 393 of 393 deadlocks" / "The criterion is exact at the rest state." | "a stuck-alone criterion, verified against single-agent restarts in all 393 deadlocks" / "Single-agent restarts confirm the criterion in all 393 deadlocks." |
| 836 | "In whole runs, noise matched to ORCA's completion rate fails on other seeds, completes later and leaves other final states" | "In whole runs, noise matched to ORCA's completion rate fails on a partly different set of seeds (50 of 122 failing seeds shared), completes later and leaves other final states" |
| 1035 | "The trap is therefore local to the door edges: the walls away from the door add nothing." | "The trap is therefore local to the door edges: shortening the range of the other walls as well has no detectable further effect (89 vs 85 of 100, p = 0.53)." |
| 1110 | "ORCA is its rest drive." (paragraph title) | "At the lone keystone, ORCA acts as its rest drive." |
| 1117 | "Noise is thermal at the temperature of Eq. (9); ORCA is not thermal." | "Noise responds to the time step as activated escape at the temperature of Eq. (9) predicts (slope 0.91 [0.83, 1.01]); ORCA shows no time-step dependence." |
| 1120 | "which a replay this small reveals as ill-conditioning of that implementation (class N)" | "which is consistent with ill-conditioning of that implementation; we assign it provisionally to class N" |
| 1123 | "the two agree on completion and little else" / "the no-fit prediction" | "the two agree on completion but differ in timing and final states" / "the prediction with no further fit (barriers, k_BT_eff(sigma*) and the attempt rate of Sect. 5.4)" |
| 1136 | "Both matches reproduce the rate (Table 3; p = 1.000 and 1.000)" | "Neither match differs detectably from its solver in rate (Table 3; McNemar p = 1.0 for both; differences +0.02 [-0.15, 0.22] and +0.02 [-0.13, 0.17])" |
| 1136 | "Matched on rate, the bias shares ORCA's number, not its mechanism." | "Matched on rate, the bias has a handedness that ORCA lacks, so it does not share ORCA's mechanism." |
| 1163 | "and in all three of our pairs it does" | "and in all three of our pairs the matched control's rate is close to ORCA's (equivalence within ±0.10 shown only at the lone keystone)" |
| 1163 | "The held-out signatures, derived from the physics before the runs, reject that reading each time." | "The held-out signatures, derived from the model physics, reject that reading each time." (keep "before the runs" only with a cited dated record) |
| 1163 | "The minority outcome sets overlap little" | "The minority outcome sets overlap only partly" (or a stronger word once compared with the same-mechanism reference, Major 3) |
| 1166 | "and different mechanisms reach the same sum from different deadlocks, as the low overlaps show" | "and different mechanisms can reach the same sum from partly different deadlocks" |
| 1172 | "Wherever a resolver is credited with removing an equilibrium, the protocol carries over: match a control to its success rate and probe both on the frozen equilibria." | "The protocol should carry over wherever equilibria can be stored, replayed and probed term by term, as in multi-robot navigation; we have not tested this." |
| 1177 | "signatures derived from the physics of frozen deadlocks settle the attribution that a matched rate leaves open" | "signatures derived from the physics of frozen deadlocks separate mechanisms that a matched rate cannot distinguish" |

Proposed abstract (about 190 words; replaces line 652):

> A common way to test whether a steering paradigm, such as optimal reciprocal collision avoidance (ORCA), is responsible for resolving deadlocks in a pedestrian simulation is to tune a simple control, such as velocity noise, until it reproduces the paradigm's success rate. We show that such a match shows only that a simpler cause would suffice, not that the two act alike, and we propose a calibrate-then-falsify protocol that separates them. Each candidate mechanism (preventing deadlocks, reshaping the force landscape, thermal escape, symmetry breaking, numerical artefact) predicts how a stored frozen deadlock responds to a set of probes: replay under a tiny perturbation, a change of time step, a signed constant push and a reversed bias. In a social force model with a 0.8 m exit, deadlocks are of two kinds: a lone agent held by the wall force at the door edges, and a symmetric pair standoff. Controls matched to ORCA's success rate reproduce it, yet differ from ORCA on these probes. In this model, ORCA's force term acts as an extra goal drive, noise acts by activated escape over computed barriers, and a lateral bias acts through a fold. Against human bottleneck experiments at the same width, no model variant reproduces the observed flow.

---

## 7. Expected references (additions; "check" where unsure)

- Guy, S.J., et al.: PLEdestrians: a least-effort approach to crowd simulation. SCA 2010. This is the ORCA velocity-to-force conversion, cited in the conference paper (check details).
- Helbing, D., Farkas, I.J., Vicsek, T.: Freezing by heating in a driven mesoscopic system. Phys. Rev. Lett. 84, 1240 (2000). Directly relevant to the effect of noise in the SFM.
- Parisi, D.R., Dorso, C.O.: Microscopic dynamics of pedestrian evacuation. Physica A 354 (2005). On SFM clogging at doors (check).
- Pastor, J.M., et al.: Experimental proof of faster-is-slower in systems of frictional particles flowing through constrictions. Phys. Rev. E 92, 062817 (2015) (check).
- Garcimartín, A., et al.: Flow of pedestrians through narrow doors with different competitiveness. J. Stat. Mech. (2016) (check).
- Seyfried, A., et al.: New insights into pedestrian flow through bottlenecks. Transp. Sci. 43 (2009); Kretz, T., Grünebohm, A., Schreckenberg, M.: Experimental study of pedestrian flow through a bottleneck. J. Stat. Mech. P10014 (2006). Human bottleneck flow at narrow widths (check).
- Chraibi, M., Seyfried, A., Schadschneider, A.: Generalized centrifugal-force model for pedestrian dynamics. Phys. Rev. E 82, 046111 (2010). Force-model artefacts such as overlaps and oscillations at bottlenecks (check).
- Lakoba, T.I., Kaup, D.J., Finkelstein, N.M.: Modifications of the Helbing-Molnár-Farkas-Vicsek social force model for pedestrian evolution. Simulation 81 (2005). Numerics and wall treatment in the SFM (check).
- Tordeux, A., Chraibi, M., Seyfried, A.: Collision-free speed model for pedestrian dynamics. Traffic and Granular Flow '15 (2016). A velocity-level alternative relevant to Major 1 (check).
- Snape, J., van den Berg, J., Guy, S.J., Manocha, D.: The hybrid reciprocal velocity obstacle. IEEE Trans. Robot. 27 (2011). Reciprocal "dances" and deadlock in velocity-obstacle methods (check).
- van Toll, W., Pettré, J.: Algorithms for microscopic crowd simulation: advancements in the 2010s. Comput. Graph. Forum 40 (2021). Cited in the conference paper (check).
- Henkelman, G., Uberuaga, B.P., Jónsson, H.: A climbing image nudged elastic band method for finding saddle points and minimum energy paths. J. Chem. Phys. 113, 9901 (2000). Needed because "climbing image" is used at line 1017.
- Langer, J.S.: Statistical theory of the decay of metastable states. Ann. Phys. 54 (1969). Many-dimensional prefactor, relevant to Minor 8 (check).
- Sargent, R.G.: Verification and validation of simulation models. J. Simul. 7 (2013). Frames the paper for the SIMULTECH methods audience (check).
- Wolinski, D., et al.: Parameter estimation and comparative evaluation of crowd simulations. Comput. Graph. Forum 33 (2014). Evaluating crowd models beyond a single score (check).
- The paper describing the CroMa bottleneck experiments, in addition to the data DOI (authors to supply; check).

---

## 8. Figures: keep / merge / cut

| Fig. | Verdict | Notes |
|---|---|---|
| 1 (hero, lines 656-825) | Keep | Strong, approved labels. Shorten the caption to about 60 words; 6 pt labels (font substitution) are borderline in print (Minor 13). |
| 2 (lone trap, line 1025) | Keep | Clear. No in-figure text. Caption is two sentences but long. |
| 3 (width and walls, line 1041) | Keep | Lets the text of Sect. 5.1 shrink (Minor 10). |
| 4 (escape, line 1061) | Keep | Right panel: normalising by the fitted attempt rate makes the collapse partly by construction; say that only the slope is tested. |
| 5 (time step, line 1076) | Keep | The cleanest signature in the paper; set the width explicitly. |
| 6 (quench, line 1082) | Keep | Dense but readable. Consider dropping the lateral-bias points (all zero), which the text states in one clause. |
| 7 (pair, line 1128) | Keep | The right panel overlaps Table 3; the two could share space if length gets tight. |
| 8 (CroMa, line 1147) | Keep | Clear. Human intervals over n = 5 are wide; fine. |

Every caption is at most two sentences. No figure among Figs. 2-8 carries in-figure annotation beyond axis and category tick labels. The colours follow one scheme across Figs. 2-8.

---

## 9. Length budget

The paper is currently 23 pages including about 2.3 pages of references. Pending material comes to roughly 0.6-0.8 page (Table 4 plus its paragraph, acknowledgements and disclosure), which projects to about 24 pages, inside the 23-25 page target but with little slack.

- **Cut** (about 1.5 pp available):
  - duplicate DOI/URL in the references, about 0.7 pp (Minor 22);
  - Fig. 1 caption, about 0.25 pp;
  - Sect. 5.1 wall-variant p-values, about 0.3 pp;
  - Sect. 5.3, compress to about 6 lines, about 0.15 pp;
  - Sect. 5.4 "two snapshots reported separately", reduce to one sentence, about 0.1 pp.
- **Thin** (spend the space here):
  - the protocol box and "applying the protocol to another model", about 0.5 pp (Major 2);
  - one paragraph of threats to validity: a single additive hybrid, a single force conversion of ORCA, chaotic sensitivity of whole runs, one width;
  - the merged checklist for modellers (Major 5).

---

## 10. Practitioner takeaway (crowd-simulation engineers, ORCA users)

What a practitioner can use today:
1. Before reading a deadlock rate at a narrow door as crowd behaviour, compare g_max(r) with m v0/tau over the agent population (Eq. 11). That is a five-minute check, and this paper makes it concrete.
2. Do not count a door edge twice where wall segments meet.
3. Name the ORCA implementation used, because the two solvers differ at the pair (21 vs 7 of 46).
4. Noise tuned at one Delta t is a different temperature at another (Eq. 9).
5. Removing deadlocks is not the same as calibrating capacity (Sect. 7).

What is mis-scoped for ORCA users: "ORCA adds a goal drive" holds for the additive force hybrid, not for velocity-level RVO2 (Major 1). The two must be separated before practitioners take the advice.

---

## 11. Extension compliance

**Method.** I extracted text from the conference camera-ready (`pdftotext -layout ref/camera_ready_SIMULTECH2026.pdf`) and from the extension (`main.txt`). Both were lower-cased with punctuation removed. I compared shingled word n-grams. For the body comparison, reference lists were excluded and the extension was split at its section headings.

| Measure | Value |
|---|---|
| Extension body words (abstract to back matter) | 10,375 |
| 8-gram shingle coverage of extension body by conference text | **0 words (0.00%)** in every section (Front, 1-9, Main Differences) |
| 6-gram coverage, body | 31 words (0.30%) |
| 5-gram coverage, body | 77 words (0.74%) |
| 8-gram coverage including references | 0.44% of extension words, all of them bibliographic strings (titles of refs. 8, 11-13, 16, 20) |
| Conference text reused (5-gram, including refs) | 4.7% of conference words |
| Longest shared runs (body) | 7 words, the parameter string "N(1.34, 0.26) m/s ... N(0.25, 0.03) m" (line 862); 6 words, "optimal reciprocal collision avoidance (ORCA)" (line 828); 6 words, "w = 0.8 m, 100 agents" (line 1056); 5 words, "the social force model (SFM)" (line 828) |

**New content estimate.**
- *Figures:* all 8 figures are new.
- *Tables:* Tables 2 and 3 are new. Table 1 is an expanded and corrected parameter table: it adds the two model modes and the parameters the code actually used, where the conference table listed calibrated values the runs did not apply.
- *Concepts carried over:* the audit principle (a matched control), the C1-C4 configurations, the SFM/TTC/ORCA force forms and sigma_50 (recomputed: 0.044 [0.041, 0.047] vs 0.049 [0.044, 0.053], line 1071). Together these take about 1.5 pages of Sects. 1 and 3.
- *Dropped conference material:* the FD calibration, OOD flows, zonal overlaps, counterflow and crossing are absent. Counterflow, crossing and overlaps are pending in Table 4 only.
- *Result:* by page count, at least about 90% of the extension is new material (more than 20 of 23 pages), well above the 30% threshold.

**Other criteria.**
- The title, abstract and conclusions all differ from the conference version.
- The conference paper is cited (lines 830, 887, 1071, 1163, 1179).
- A "Main Differences from the Conference Version" statement is present (line 1179).
- There is no large verbatim reuse.
- **Compliance verdict:** satisfied. One caveat: the promised list of revised conference claims (Sect. 6.3 and Table 4) must be delivered, and should include the methods-versus-code corrections noted in Minor 21.

**Build log (final pass, `build.log` lines 1214-1539).**
- No undefined references or citations.
- One significant overfull box: Table 3, 47.9 pt (Major 6).
- One negligible overfull box: 2.1 pt (Minor 23).
- A font-size substitution in Fig. 1, 6.5 pt to 6 pt (Minor 13).
- About 25 underfull boxes in the bibliography, from long URLs (Minor 22).
- A harmless amsmath \vec warning.
- The standalone submission build reports 23 pages and 8 `\pending` items, matching the known gaps.

**Total new computation requested:**
- M3: about 9-14 CPU-h.
- M4: about 1-3 CPU-h.
- M1 (optional): about 2 CPU-h.
- Total: about 12-19 CPU-h, roughly 3-5 h wall on a 4-core laptop.

Referee 3
