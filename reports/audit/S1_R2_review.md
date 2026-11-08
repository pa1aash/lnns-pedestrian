# Referee report (Referee 2): statistics and computational methods

Manuscript: "One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models" (P. Gang, A. Veluri). Invited LNNS extension of the SIMULTECH 2026 paper.
Version reviewed: snapshot at commit decbdca (`main.tex`, 1353 lines; 23-page PDF). Line numbers refer to `main.tex`. Every page image was inspected. Numbers were checked against `data/derived/*.json` and, where noted, recomputed from `data/E2/e2_quench.jsonl`, `data/E6/*.jsonl` and `data/derived/E10_analysis.json`. Table 4, Sect. 6.3, the Zenodo DOI and the acknowledgements are pending by design and are not counted as defects.

---

## 1. Summary

1. The paper argues that a control tuned to match a steering paradigm's completion rate (here ORCA, in a social-force bottleneck at w = 0.8 m) shows only that a simpler cause would suffice. It proposes "calibrate, then falsify": classify each resolver into one of five mechanism classes (P, L, T, D, N) and test it with probes applied to the same frozen deadlock states (quench, 1e-9 m replay, time-step change, signed goal push, tilt reversal, corrected numerics).
2. On the physics side it gives a stuck-alone criterion g_max(r) > m v0/τ, which holds in 393/393 deadlocks. It also identifies a symmetric pair standoff that is a strict energy minimum (46/46) and is removed by a lateral bias at a fold. Contact arches do not persist. Noise frees the lone trap by activated escape over string-method barriers.
3. On attribution: at the lone trap ORCA acts through its rest drive (class L, deterministic, Δt-independent), noise matched to its rate is thermal (class T, with a Δt signature close to the prediction), and at the pair class ORCA acts through its constraint part, which differs between solvers. A bias matched on rate has a handedness that ORCA lacks.
4. A like-for-like comparison with five CroMa runs shows that every model variant either deadlocks or flows at roughly 0.4–0.6 of the human rate.
5. The contribution can be stated crisply. The deterministic probes (replay, signed push, Δt, handedness) are convincing. However, the second pillar of the attribution, "the matched control frees *different* deadlocks" (the Jaccard identity comparisons), is not supported statistically at the lone trap or in whole runs. Several intervals ignore clustering, the rate matches are in-sample by construction, and a substantial number of reported numbers cannot be reconstructed from the text.

## 2. Scores (1 = poor, 5 = excellent)

- Originality: 4. Probing a rate-matched control on frozen states with physics-derived signatures is a genuinely useful idea for the field.
- Significance: 3. Strong for SFM practitioners (the wall-law and stuck-alone findings). The general protocol's reach depends on fixing the identity statistics.
- Soundness: 2. The deterministic results are sound. The identity and overlap inference, clustered intervals, in-sample matching and decision rule need rework (Major 1–6).
- Clarity: 3. The writing is dense but precise. Statistical methods are scattered or missing (Major 7).
- Presentation: 3. Figures are clean and comply with the authors' rules. Table 3 mixes units and contains internal experiment codes.
- Venue relevance: 4. Simulation methodology with a validation component fits SIMULTECH/LNNS well.

**Recommendation: major revision.** Most fixes are re-analyses of existing JSON (about 0 CPU-h). Two small new run sets are requested (about 3.5 CPU-h, optional extension to about 10 CPU-h; under 3 h wall time on a 4-core laptop).

---

## 3. Major issues

### M1. The identity (Jaccard) signature cannot separate "different mechanism" from "stochastic resolver". At the lone trap and in whole runs the data actually show positive association.
*Location:* Sect. 6.1 "Matched noise acts differently" (l. 1114) and "Matched completion of whole runs" (l. 1123); Table 3 J column (l. 1087–1106); Discussion (l. 1163, 1166); abstract (l. 652); contributions (l. 836); conclusions (l. 1177).

*Problem.*
(a) The lone-trap J = 0.20 [0.00, 0.50] compares minority sets of size 2 (noise: E1b_seed69 and E1b_seed83, by majority of five seeds) and 4 (ORCA: seeds 203, 211, 83, 87; `E2_analysis.json → f_noise_vs_C3.lone_keystone.noise0p07`). One shared element out of five carries essentially no information.
(b) For a stochastic control the ceiling of J is not 1. I computed the J expected between two independent majority-of-5 replicates of *the same noise arm*, using the per-snapshot freed counts in `e2_quench.jsonl` (counts of 0, 2, 3×6, 4×2 and 5×24 out of 5). It is ≈ 0.40, with a Monte Carlo 95% range of [0.14, 0.80]. Noise against itself would therefore look about as "different" as noise against ORCA.
(c) A direct association test points the other way. Noise at σ = 0.07 frees ORCA's four unresolved snapshots in 10 of 20 runs, against 138 of 150 on the other 30 snapshots (my recomputation; per-snapshot Mann–Whitney one-sided p = 7×10⁻⁴). The snapshots ORCA cannot free are the hardest ones for noise as well, which is physically expected (larger margin, higher barrier).
(d) Whole runs: the authors' own JSON reports a permutation p = 0.0023 for J above the independence value (`E6_analysis.json → identity.p_perm_jaccard_above_independent`). The 2×2 table (50, 35, 37, 64) gives a Fisher odds ratio of 2.47 (p = 0.003). The text's "overlap barely more than independent ones would" and "agree on completion and little else" contradict this.
(e) Pair block, RVO2: J = 0.00 for sets of 8 and 7 out of 46. The hypergeometric probability of zero overlap under independence is 0.24, so disjointness is unremarkable against independence. Against the relevant null for two *deterministic* arms (identity, J = 1), however, J = 0 and the 17 published-solver discordances are decisive. The identity probe is valid at the pair block only.

*Why it matters.* "Free different deadlocks" appears in the abstract, the contributions, the discussion and the conclusions. As stated it is not supported for the two noise comparisons, and the paper rests half of its "one rate, different mechanisms" reading on it.

*Fix.*
(i) Replace the majority-rule J for stochastic controls with a per-snapshot (per-seed) association analysis. Model noise's freeing probability p_i as a function of ORCA's outcome, for example with a logistic regression or Mann–Whitney on k_i/n_i, and report the effect with a 95% interval.
(ii) Report J against a noise-versus-noise reference, computed from replicate noise streams.
(iii) Rewrite the claims as in Sect. 6 of this report. The time-to-free, replay, Δt and final-state signatures still separate ORCA from noise, so the thesis survives.

*New computation.*
- Run A (lone trap): 15 additional noise seeds at σ = 0.07 on the 34 lone keystones (20 seeds per snapshot), 120 s window. That is 510 quenches at about 5.4 s each (E2 mean wall time) ≈ 0.8 CPU-h. Outputs: per-snapshot p_i with Wilson intervals, the association with ORCA outcome, and a noise-versus-noise J from two disjoint 10-seed halves.
- Run B (whole runs): repeat E6b (C1 + σ*, seeds 242–427) with an independent noise stream. That is 186 runs at about 50 s each ≈ 2.6 CPU-h. Outputs: J(noise, noise′) and J(ORCA, noise′), and the association odds ratio with a 95% interval. A third stream (another 2.6 CPU-h) would give an interval on the ceiling.
- Re-analysis of existing JSON ≈ 0.

### M2. Rate matching is in-sample, and "held out" is a misnomer. Equality-of-rate p-values carry no evidence.
*Location:* abstract (l. 652, "held-out signatures"); l. 1114 (σ = 0.07 picked from the grid {0.03, 0.05, 0.07} on the same 34 snapshots); l. 1123 (σ* inverted from a fit, then evaluated on the same 186 spawns as ORCA's rate); l. 1136 ("ran it held out at ±b*"; "Both matches reproduce the rate (p = 1.000 and 1.000)"); l. 1163.

*Problem.* `E7b_analysis.json → s3_matched.fits` shows that b* was chosen so that the *static* fold fraction on the same 46 snapshots equals ORCA's count (static fraction 21/46 and 7/46). The quench then agrees with the static fold in 363/368 cases, so the rate match (22 vs 21, 8 vs 7) is guaranteed by construction and the McNemar p = 1.000 is not evidence. The same holds, to a lesser extent, for σ = 0.07 (the grid level closest to ORCA's rate on the evaluation snapshots). What is held out is the *statistic* (identity, handedness, replay, t½), not the data.

*Why it matters.* Readers will read "held out" as out-of-sample validation. In-sample calibration also biases the identity comparison. Calibrating b* on the fold thresholds of exactly these snapshots determines *which* standoffs the bias frees (those with the lowest folds).

*Fix.* Replace "held out" with "not used in the calibration". Remove the rate p-values (l. 1136) or label them as checks. Preferably add a split-sample version: calibrate σ (or b*) on half of the snapshots and evaluate all signatures on the other half. Report both halves; for b* a 2-fold swap is enough. Re-analysis only, ≈ 0 CPU-h. If the authors want truly fresh pair snapshots: about 320 further corrected-forward B_w,jamb = 0.04 runs (seeds 562–881) at about 60 s each, plus static fold and ±b* quenches ≈ 6 CPU-h.

### M3. Intervals that ignore clustering or replication structure.
*Location and problem.*
- Fig. 6 (l. 1083) and Table 3 (l. 1095): noise rates are Wilson intervals over 170 runs (5 seeds × 34 snapshots), treated as independent. A snapshot-cluster bootstrap of 148/170 gives [0.79, 0.94] against the Wilson [0.81, 0.91] (my recomputation), about 45% wider. The same applies to E2 noise at the second trap and to the pooled 300-run rates.
- l. 1051: "363 of 368 (snapshot, b) cases ... (Wilson lower bound 0.969)" treats 8 bias values per snapshot as independent.
- l. 1123: Weibull shape 0.64 [0.58, 0.70] of 349 stalls from 178 runs, treated as independent; stalls within a run share a landscape.
- l. 1056: "95% within 0.6 s" pools 103 episodes from 22 runs.
- l. 1071, l. 1035: σ50 and the width/wall cells use the *same seeds* (42–141) at every level and cell. The binomial-logit profile intervals and the Fisher tests assume independent samples. The σ50 goodness of fit (deviance 0.15 on 3 df, p = 0.985; `E5_analysis.json`) is implausibly good, which is consistent with positive correlation induced by common random numbers. Between-cell comparisons on common seeds should be paired (McNemar), not Fisher.
- l. 1123: the final-state class test (p = 1.4×10⁻³) is a permutation chi-square (`E6_analysis.json → failure_state.class_test`) that permutes labels across two groups sharing 50 seeds. Exchangeability fails under pairing.
- l. 1123 (logrank, computed but not reported) has the same issue.

*Why it matters.* The authors' rule is "all intervals 95%". These intervals are nominally 95% but under-cover.

*Fix.* Use a cluster (snapshot or run) bootstrap or a Rao–Scott adjustment for clustered proportions. Report per-snapshot agreement for the fold test (number of snapshots with all 8 b values correct). Use a seed-cluster bootstrap of the logit fits for σ50 and w50. Use McNemar for paired cells and a stratified/paired permutation (permute within seed) for the class test. All re-analysis, ≈ 0 CPU-h. E5 per-run data are needed for σ50. They are not in the snapshot (`data/E5/` is empty); check that they are archived.

### M4. Decision rule of the protocol has no operational tolerance, and several separating signatures are not in Table 2.
*Location:* l. 1020 ("Target and control share a mechanism only if they agree on every probe; one disagreement separates them"); Table 2 (l. 928–980); l. 1163 ("held-out signatures, derived from the physics before the runs").

*Problem.*
(a) With finite samples, "agree" and "disagree" need a stated numerical criterion per probe: a tolerance on Δ, on ℓ, on replay flips, on handedness fraction. Without one, the rule is either anti-conservative (any noise-driven difference separates) or untestable. The more probes are applied, the higher the chance of a spurious "separation". Example: C3 RVO2's ℓ is −0.0048 with a 95% interval of [−0.0086, −0.0008] (`E3_analysis.json → C3_rvo2.ln_ratio_ci95_boot`). It is formally Δt-dependent, and only a tolerance makes it "no Δt dependence".
(b) The separating evidence in Table 3 and Sect. 6 relies heavily on identity J, t½ and final-state class. None of these is a probe in Table 2. The git history supports that Table 2 was fixed before the quench runs (commit f6aff51 on 2026-11-07, before the E2 outputs in 1aba2df on 2026-11-08). The whole-run signatures (final-state class, stall lifetimes; changelog C47–C48) and the exclusion of seed170 (C29) were added after the data were seen.

*Fix.* State the per-probe criterion, for example "a probe separates two arms if the 95% interval of their difference excludes ±δ", with δ given per probe. Mark in the text which signatures were fixed before the runs (Table 2) and which comparisons were added afterwards (identity, t½, final-state class, stall survival, the seed170 exclusion, the 2-fold J rule C56). This is a description of the analysis history, not a change of framing. Re-analysis ≈ 0.

### M5. Activated-escape fits: what is reported is partly circular, partly overstated, and selectively reported.
*Location:* l. 1065–1069 (E4), l. 1117 (E3), Fig. 4 (l. 1062), Fig. 5 (l. 1077).

*Problems.*
(a) The collapse (l. 1067, Fig. 4 right) plots ln(λ/ν̂) with ν̂ estimated *with the slope held at −ΔU* (`experiments/E4/analyze.py`, "prefactor"). Each fit's intercept is thus forced onto the line of slope −1, and the pooled slope −0.93 restates the per-fit slope ratios. It is not an independent test. It has no interval.
(b) Each Arrhenius fit uses 3 points (1 residual df) with about 20 events each. Coverage of 1 in 25/28 fits is weak evidence by itself. The interval widths and the method (WLS with event weights; Poisson parametric bootstrap with exposure held fixed) must be reported.
(c) The pooled Weibull shape 1.09 [1.05, 1.14] (l. 1068) *excludes* 1, as do the frozen (1.14 [1.06, 1.21]) and alone (1.07 [1.00, 1.15]) conditions, and E3 √Δt-scaled cells at Δt = 0.01 and 0.02 s (`E3_analysis.json → weibull_pooled`). "Close to the exponential value 1" understates a systematic departure. A shape above 1 contradicts a pure exponential (and pooling over barriers could only push k below 1), so it points to a short-time transient after restart (check).
(d) E3 (l. 1117): the OLS slope of observed on predicted ℓ is 0.72 [0.29, 1.06] (`E3_analysis.json → ell.per_step.slope_ols`, macro `\EthreeSlopeOLS` defined but unused). Only the through-origin slope 0.91 [0.83, 1.01] is reported, and it is fitted to only two distinct predicted values (2.22 and 3.70). The β_ref = 2.5 point misses its prediction (3.23 [2.96, 3.52] vs 3.70). The censoring at Δt = 0.02 s (23% overall, up to 80% in one snapshot; macro `\EthreeCensLong` unused) is not reported. Kramers asymptotics hold for ΔU/k_BT ≫ 1, whereas β spans about 0.75–6 here.
(e) Competing exits: in 111 E3 runs another agent exits before the blocker (`E3_analysis.json → other_exit_first_total`). It is not stated whether these runs are censored at that time or continued in a changed landscape.
(f) Snapshot selection for E3/E4 is conditional on string convergence. 4 of 60 snapshots failed the gate, E3 took 20 of 36 qualifying (ΔU ≥ 3 J), and E4 took 10 of 32 (`selection.json`). None of this is in the text.

*Fix.* Drop the collapse as evidence or define it with a free intercept and a 95% interval. Report per-fit ratio intervals (a small supplementary table or a forest plot replacing Fig. 4 right). State that k > 1 is significant, with the observed transient. Report the OLS slope alongside the through-origin slope, and the censoring fraction. State how competing exits are handled. Give the selection counts and rules. All re-analysis ≈ 0. Optional: 20 more restarts per cell at β_ref = 2.5 to tighten the shortfall (10 snapshots × 3 Δt × 20 runs, at about 30 s each ≈ 5 CPU-h). I do not consider this essential if the shortfall is reported plainly.

### M6. Sample sizes are not justified, and several headline rates sit on very small event counts.
*Location:* l. 1111 (34 lone keystones; ROC 0.98 from 4 failures, no interval: [0.91, 1.00] in `E2_analysis.json`); l. 1123 (n = 186, unexplained); l. 1136 and l. 1175 (46 pair snapshots, acknowledged); l. 1053 (12 pair barriers); l. 1065 (10 E4 snapshots); l. 1151 (5 human runs).

*Problem.* The changelog (C6) says equivalence margins were "kept internally where they set sample sizes". The reader is told neither the rationale nor what effect size each n can resolve. With n = 34 and 4 ORCA failures, any identity or ROC statement is close to anecdotal.

*Fix.* Add one sentence per experiment giving how n was chosen and the half-width of the 95% interval it achieves for the primary rate (e.g. "n = 186 resolves a paired completion difference to ±0.09"). No trial vocabulary is needed. Report the ROC interval. Re-analysis ≈ 0.

### M7. Statistical methods are under-specified. Many numbers cannot be reconstructed from the text.
*Location:* l. 926 (the only methods paragraph names Wilson, exact McNemar and Kaplan–Meier). The following methods are used elsewhere but never named: percentile bootstrap over snapshots or seeds (2000 resamples, PCG64), the Newcombe paired score interval (E6 Δ), Fisher exact tests, permutation tests, profile-likelihood Weibull with per-group scale, censored-exponential rates with Garwood intervals, WLS Arrhenius fits with Poisson parametric bootstrap, the empirical-logit width fit with 0.5 pseudo-count, Student-t over runs, bootstrap ratio intervals, and Spearman correlation.

*Fix.* Expand l. 926 into a compact "Statistics" paragraph listing estimator, interval method, resampling unit and number of resamples per quantity, and add the table in Sect. 7 of this report as a checklist. Re-analysis ≈ 0.

### M8. CroMa ratio intervals are too narrow, and the comparison inherits heterogeneity that is not reported.
*Location:* l. 1151–1157, Fig. 8 (l. 1148); abstract and contributions ("0.40–0.59", l. 652, 837).

*Problem.* The flow ratio intervals come from a nonparametric bootstrap over 5 human runs (`E10_analysis.json → ci`), which under-states variance at n = 5. A t-based delta method on the log ratio (my recomputation from the reported means and t-intervals) gives:
- C1 corrected-forward: [0.43, 0.61], against the reported [0.46, 0.58];
- C3 RVO2: [0.49, 0.71], against [0.53, 0.67];
- C1 + σ*: [0.32, 0.51], against [0.34, 0.47].

The qualitative conclusion holds, but the upper ends approach 0.7. The longest-gap means for noise (72.2 [32.8, 111.6] s) are t-intervals on strongly skewed data. The five human runs differ in corridor length and, I believe, in motivation condition (the dataset title is "varying motivation levels"; check). The paper does not say which condition they come from.

*Fix.* Use Fieller or a t-based log-ratio interval. Put gaps on a log scale (a geometric mean with a t-interval on log values). State the motivation condition of each human run. Re-analysis ≈ 0.

### M9. Reproducibility statement is incomplete for a computational paper.
*Location:* l. 1182; Table 1 (l. 857–881); l. 1111 (replay definition).

*Problem.* The statement gives the repository URL but no commit or tag, software versions (Python, NumPy, SciPy), platform, RNG family (PCG64 is used throughout), seed lists per experiment (given only for E7, l. 1035, and the CroMa runs implicitly), or CPU cost. The "replay" test (5 replays with positions perturbed by 1e-9 m, perturbation seeds 900–904; `E2_analysis.json` doc) is not defined in the paper: which agents are perturbed, in which direction, and what counts as reproduction (identical outcome and first-exit time to one time step?). Determinism was checked on one machine only. For class T the "replay" column actually reports *independent seeds* (Table 3, l. 1087: "noise: snapshots whose seeds disagree"), which is a different operation from a 1e-9 m replay.

*Fix.* Add a commit hash or tag and versions to the availability statement, a seed table (one line per experiment), and a one-sentence replay definition. Split the Table 2/3 "Replay" column into "1e-9 m replay (deterministic arms)" and "seed replicates (noise)". Optionally rerun 10 E2 snapshots × C3 RVO2 and C3 published on a second machine or library version to report cross-platform reproduction (≈ 0.1 CPU-h).

---

## 4. Minor issues

1. l. 1037: the AUC of 0.975 [0.970, 0.979] is compared with an "all-exit baseline accuracy of 0.931". An AUC is not an accuracy. Compare the accuracy at k = 3 (0.962; `E1_chain.json`) with 0.931, or the AUC with 0.5. State that the interval is a seed-level bootstrap and that the unit is stuck-alone arrivals (4465).
2. l. 1035: name the test behind p = 0.529, 3.5×10⁻⁴¹, 0.170 and 2.0×10⁻¹³ (Fisher exact, two-sided). Because cells share seeds 42–141, use McNemar (see M3).
3. l. 1035: the critical width 0.88 [0.87, 0.89] is an empirical-logit fit with a 0.5 pseudo-count over four widths (`E7_analysis.json → critical_width`), effectively an interpolation between 0.8 and 0.9 m. State this. The interval is narrower than the grid spacing and is model-dependent.
4. l. 1033: "5–95%" is a population percentile range, not an interval. Write "5th–95th percentiles" to avoid clashing with the 95%-interval rule.
5. l. 1033: the ORCA rest-drive median of 215 N needs the gate value w_o at the terminal density (≈ 1). Say so.
6. l. 1049: state how the Hessian was computed (analytic or finite differences, step size) and the positivity tolerance.
7. l. 1051: "rank correlation 0.9996" needs the two variables named exactly and the type (Spearman).
8. l. 1053: "224 of 230 runs" means 46 snapshots × 5 seeds. Say so. Give intervals for the pooled Weibull shapes 2.3 and 2.8.
9. l. 1056: arch lifetimes are resolved at 0.1 s (the median lifetime in `arch_analysis.json` is 0.0 s). State the contact criterion used to define a chain.
10. l. 1069: "below the resolution of the gate". Give the threshold (0.1 J; `E4_analysis.json → skipped_no_barrier`). The "10 of 10 snapshots with full barrier below alone" (l. 1068) includes these two problematic snapshots. Say so, or report 8 of 8.
11. l. 1071: list the σ levels used in each fit (corrected: 0.03–0.07; published: check `logistic_core`). The conference interval [0.044, 0.053] contains the new estimates, so "lies just above both intervals" should add that the two are compatible.
12. l. 1009: define "dedicated runs" and the composition of the 207 noise cells.
13. l. 1111: "largest first-exit shift 0.000 s". The resolution is Δt = 0.01 s, so write "identical to the time step".
14. l. 1114: "within-snapshot standard deviation of the first exit 11.2 s". State over which snapshots this is computed and that it is the median of per-snapshot SDs.
15. l. 1120: "cancels on average 0.27 of the drive". State the averaging window.
16. l. 1123 and Table 3: Kaplan–Meier medians (1.5, 19.8, 132, 469 s) have no intervals, although the caption says "Intervals are 95%". Add Brookmeyer–Crowley intervals. The noise median of 469 s is reached only near the end of follow-up (S_end = 0.468) and is fragile.
17. l. 1123: the stall comparison "within 0.05" is the maximum over four time points (30, 60, 120, 300 s), not a supremum over t. Stalls are left-truncated at 10 s by definition. State whether the prediction conditions on that.
18. l. 1133: give the arithmetic for "5520 replays" (arms × 46 × 5).
19. Table 3 (l. 1087–1106): (i) the "Freed" column mixes runs (noise, 148/170) with snapshots (ORCA, 30/34), and "Replay" mixes 9/34 snapshots with 0/170 replays. Use one unit per column or add footnotes. (ii) "J = 0.00 [0.00, 0.00]" is a degenerate bootstrap interval. Report "0 of 15" instead. (iii) Internal experiment codes (E2, E3, E6, E7b) appear in the caption and the row headers (l. 1087, 1094, 1098, 1102). Replace them with section references.
20. Captions: Table 2 (l. 929) and Table 3 (l. 1087) have three sentences each, if the two-sentence rule applies to tables.
21. Spelling: "vermillion" (l. 1062, 1077, 1083, 1148) vs "vermilion" (l. 822). Use one spelling.
22. Proposition 1 (l. 991–995): part (i) does not need the hypothesis on G. Part (ii) is a continuous-time statement, while the simulation uses a clamped discrete update (Table 1). Add one sentence saying the discrete map is covered by the replays, not by the proof.
23. l. 895 and l. 1029: the Weidmann ≥ 0.994 statement is repeated. Keep one occurrence.
24. l. 1047: "from independent runs". Give the seed range (242–561) and the yield (46 pair snapshots from 320 runs).
25. l. 1151: give the Savitzky–Golay polynomial order and the passage-gap definition.
26. Figure rules: Figs. 2–8 contain only axis and tick labels, and Fig. 1 has only the approved labels. All captions examined are at most two sentences. All stated intervals are labelled 95%. I found no violation of the authors' standing rules apart from items 20–21.

## 5. Questions to the authors

1. How was n = 186 chosen for E6, and n = 34 / 46 for the quench libraries? What interval half-width did you target?
2. Under noise, a snapshot is classed as "unresolved" if it is freed in fewer than 3 of 5 seeds. Was this rule fixed before E2 was analysed? What does J become under "fewer than 5 of 5" or "0 of 5"?
3. What is J between two independent noise streams on the same spawns (whole runs) and on the same snapshots (lone trap)? See M1.
4. In E3, if another agent exits before the blocker (111 runs), is the blocker's time censored at that moment?
5. Why is ν̂ estimated with the slope fixed at −ΔU? What does the collapse look like with free-intercept fits?
6. Were the Weibull shapes above 1 inspected (e.g. hazard against time)? Is there a dead time of order τ after restart?
7. Which CroMa motivation condition do the five 0.8 m runs belong to? Are they from the same session?
8. Is the 1e-9 m perturbation applied to all agents, in random directions? Are replays bit-identical, or identical only in outcome?
9. Do E5, E5a and E7 use common seeds across levels and cells by design? If so, why were unpaired tests and binomial-logit intervals used?
10. Why were the OLS slope (E3) and the logrank test (E6) computed but not reported?
11. Seed170 (E4) was excluded after 0/60 escapes. Would the conclusions change if it were included as a failed fit?
12. Do the noise-run failures "never come to rest" (l. 1123) for any reason other than the detector threshold? With σ* = 0.0467 m/s, the velocity scale (k_BT_eff/m)^{1/2} is about 0.24 m/s (k_BT_eff ≈ 4.6 J, m = 80 kg; `E6_analysis.json → lifetimes.barrier_picture`), well above 0.01 m/s.

## 6. Overstated claims and acceptable replacements

| Line | Current wording | Acceptable replacement |
|---|---|---|
| 652 | "reproduce the rate, yet free different deadlocks and differ in replay, time-step dependence or handedness" | "reproduce the rate but differ in replay, time-step dependence, time to free or handedness; at the pair the bias frees other standoffs than ORCA" |
| 836 | "the two differ in which deadlocks they leave unresolved, in replay and in time-to-free" | "the two differ in replay, time-step dependence and time-to-free" |
| 836 | "noise matched to ORCA's completion rate fails on other seeds, completes later and leaves other final states" | "noise matched to ORCA's completion rate fails on a partly overlapping set of seeds, completes later and leaves other final states" |
| 1035 | "The trap is therefore local to the door edges: the walls away from the door add nothing." | "Shortening the range at the jambs alone recovers as much completion as shortening it on all walls (89 against 85 of 100); the trap is set at the door edges." |
| 1068 | "The pooled Weibull shape of the escape times is 1.09 [1.05, 1.14], close to the exponential value 1" | "The pooled Weibull shape of the escape times is 1.09 [1.05, 1.14], slightly above the exponential value 1" |
| 1067 | "Pooled over all points, the rates collapse onto a line of slope −0.93" | "With each attempt rate estimated at slope −ΔU, the points lie about the line of slope −1 (pooled slope −0.93, rms deviation 0.24)" |
| 1071 | "The two modes need the same noise." | "The two estimates agree within their intervals." |
| 1111 | "it fails where the rest-state margin with ORCA's drive added stays positive (ROC area 0.98)" | "its four failures all have a positive margin with ORCA's drive added (ROC area 0.98 [0.91, 1.00])" |
| 1114 | "matches that rate and nothing else (Table 3): it leaves other snapshots unresolved, its seeds disagree ... and it waits" | "matches that rate (Table 3), but its seeds disagree ... and it frees an order of magnitude later" |
| 1117 | "C3 RVO2 has none (\|ℓ\| ≤ 0.018)" | "C3 RVO2 has \|ℓ\| ≤ 0.018, two orders of magnitude below per-step noise" |
| 1117 | "Noise is thermal at the temperature of Eq. (9); ORCA is not thermal." | "Noise follows the temperature of Eq. (9) at β_ref = 1.5 and falls 13% short of it at 2.5; ORCA shows no Δt signature." |
| 1123 | "the two agree on completion and little else" | "the two agree on completion but not on completion time or final state" |
| 1123 | "The failure sets overlap barely more than independent ones would (Jaccard 0.41 against 0.30 ...)" | "The failure sets overlap more than independent sets would (Jaccard 0.41 [0.32, 0.50] against 0.30) but are far from identical (discordant 35:37)" |
| 1123 | "whereas noise failures never come to rest" | "whereas noise failures, whose velocity fluctuations exceed the rest threshold, are all still moving at 600 s" |
| 1123 | "their survival lies within 0.05 of the no-fit prediction" | "their survival at 30, 60, 120 and 300 s lies within 0.05 of a prediction with no parameter fitted to the stall data" |
| 1136 | "and ran it held out at ±b*. Both matches reproduce the rate (Table 3; p = 1.000 and 1.000)" | "and ran it at ±b* on the same snapshots; the rates match by construction (Table 3)" |
| 1163 | "The held-out signatures, derived from the physics before the runs, reject that reading each time." | "The signatures of Table 2, set out before the quench runs, reject that reading in each pair." |
| 1163 | "The minority outcome sets overlap little (J = 0.20 at the lone trap; 0.41 in whole runs ...; 0.43 and 0.00 at the pair)" | "At the pair the freed standoffs differ (J = 0.43 and 0.00); at the lone trap and in whole runs the unresolved cases overlap partly, as expected for a stochastic control" |
| 1166 | "different mechanisms reach the same sum from different deadlocks, as the low overlaps show" | "different mechanisms reach the same sum, at the pair from different standoffs" |
| 1177 | "reproduce the rate but free other deadlocks and differ from ORCA in replay, time-step dependence or handedness" | "reproduce the rate but differ from ORCA in replay, time-step dependence, time to free or handedness" |

## 7. Numbers a reader cannot reconstruct from the text

| Line | Number(s) | What is missing |
|---|---|---|
| 1009 | 1.00; 0.99 over 207 cells | which "dedicated runs"; composition of the 207 cells; estimator of realised variance |
| 1033 | 0.234, 0.013; 214 N, 215 N | how g_max(r) is located (grid on axis); ORCA gate value used; which 20 000 agents (E1b spawns) |
| 1035 | 0.88 [0.87, 0.89] | empirical-logit fit with 0.5 pseudo-count, 4 points; bootstrap type and unit |
| 1035 | p = 0.529, 3.5e-41, 0.170, 2.0e-13 | test (Fisher exact); pairing by common seeds ignored |
| 1037 | AUC 0.975 [0.970, 0.979]; 0.931 | seed-level percentile bootstrap (2000); unit = 4465 stuck-alone arrivals; definition of "arrival" (door zone) |
| 1049 | λ1 = 65–121 N/m; ratio 12–14 | Hessian method and step |
| 1051 | b* 0.001–0.038; ρ = 0.9996; 363/368, LB 0.969 | bisection tolerance; correlation type and variables; Wilson ignores 8-per-snapshot clustering |
| 1053 | 0.06–1.1 J; Weibull 2.3, 2.8 | gate for pair barriers (channels failed 3/24); Weibull pooling and interval |
| 1056 | 2.9 s; 95% within 0.6 s; 108 kN | contact criterion; time resolution 0.1 s; episode-level quantile |
| 1066 | 382, 581, 554 escapes | includes seed170 (0 events); restarts per level fixed at 20 (extension rule in plan not triggered) |
| 1067 | ratios 1.15/0.95/0.87; 7/8, 9/10, 9/10 | WLS with event weights; Poisson parametric bootstrap, exposure fixed; interval widths |
| 1067 | slope −0.93 | ν̂ estimated with slope fixed at −ΔU; WLS or OLS; no interval |
| 1068 | k = 1.09 [1.05, 1.14] | shared shape, per-(snapshot, level) scale, profile likelihood |
| 1068 | ν = 0.13, 0.09 s⁻¹ | ν̂ definition (slope fixed); median over fits |
| 1071 | σ50 = 0.044 [0.041, 0.047], 0.045 [0.042, 0.047] | σ levels included; common seeds; goodness of fit |
| 1087–1106 | all Δ [CI] | snapshot percentile bootstrap (lone, pair) vs Newcombe paired score (whole runs); not stated |
| 1087–1106 | all J [CI] | bootstrap over snapshots/seeds; majority-of-5 rule for noise; degenerate [0, 0] |
| 1087–1106 | t½ 19.8, 1.5, 469, 132 | KM unit (runs vs snapshots); no interval |
| 1096 | ℓ 2.16 (2.22) | per-snapshot censored-exponential rates; mean over 10 snapshots; percentile bootstrap |
| 1111 | ROC 0.98 | 4 failures of 34; interval [0.91, 1.00] not given |
| 1114 | 11.2 s | median of per-snapshot SDs over snapshots with ≥ 2 freed seeds (check) |
| 1117 | slope 0.91 [0.83, 1.01] | through origin, two predicted values; OLS 0.72 [0.29, 1.06] omitted; bootstrap unit |
| 1117 | \|ℓ\| ≤ 0.018 | ℓ for a deterministic arm = ratio of inverse escape times; interval [−0.009, −0.001] |
| 1120 | −49 N, −138 N, 0.27, 0.26 | time window of averaging; held runs only |
| 1123 | σ* = 0.0467 | which fit (corrected mode, levels 0.03–0.07); no uncertainty propagated |
| 1123 | J 0.41 [0.32, 0.50]; 0.30 | bootstrap unit; expectation under random permutation; permutation p = 0.0023 omitted |
| 1123 | p = 1.4e-3 | permutation chi-square on paired groups |
| 1123 | 0.64 [0.58, 0.70]; within 0.05; 59 s vs 69 s | stall definition and left truncation; clustering in runs; prediction evaluated at 4 times; ν from E4 |
| 1133 | 5520 replays | arithmetic |
| 1154–1157 | ratios and their intervals | bootstrap over n = 5 humans; ratio-of-means vs mean-of-ratios |
| 1157 | 72.2 [32.8, 111.6] s | t-interval on skewed data |

## 8. Expected references (methods)

- Newcombe, R.G.: Improved confidence intervals for the difference between binomial proportions based on paired data. Statistics in Medicine 17, 2635–2650 (1998). This is the method used for the E6 Δ.
- Efron, B., Tibshirani, R.J.: An Introduction to the Bootstrap. Chapman & Hall (1993).
- Davison, A.C., Hinkley, D.V.: Bootstrap Methods and Their Application. Cambridge University Press (1997). Covers cluster and stratified resampling.
- Field, C.A., Welsh, A.H.: Bootstrapping clustered data. J. R. Stat. Soc. B 69, 369–390 (2007) (check pages).
- Rao, J.N.K., Scott, A.J.: A simple method for the analysis of clustered binary data. Biometrics 48, 577–585 (1992) (check).
- Holm, S.: A simple sequentially rejective multiple test procedure. Scand. J. Statist. 6, 65–70 (1979). The conference version applied Holm–Šidák; the extension reports about 11 p-values with no correction.
- Brookmeyer, R., Crowley, J.: A confidence interval for the median survival time. Biometrics 38, 29–41 (1982).
- Fieller, E.C.: Some problems in interval estimation. J. R. Stat. Soc. B 16, 175–185 (1954).
- Garwood, F.: Fiducial limits for the Poisson distribution. Biometrika 28, 437–442 (1936). This is the method used for λ̂ intervals.
- Henkelman, G., Uberuaga, B.P., Jónsson, H.: A climbing image nudged elastic band method for finding saddle points and minimum energy paths. J. Chem. Phys. 113, 9901–9904 (2000). Relevant because a climbing image is used in the gate.
- Real, R., Vargas, J.M.: The probabilistic basis of Jaccard's index of similarity. Systematic Biology 45, 380–385 (1996) (check). Covers the null distribution of J.
- Gelman, A., Loken, E.: The statistical crisis in science. American Scientist 102, 460–465 (2014). Relevant to the post hoc choices listed in M4.
- Sandve, G.K., Nekrutenko, A., Taylor, J., Hovig, E.: Ten simple rules for reproducible computational research. PLoS Comput. Biol. 9, e1003285 (2013).
- Domain (check): Parisi, D.R., Dorso, C.O.: Microscopic dynamics of pedestrian evacuation. Physica A 354, 606–618 (2005), on SFM clogging at doors. Pastor, J.M. et al.: Experimental proof of faster-is-slower in systems of frictional particles flowing through constrictions. Phys. Rev. E 92, 062817 (2015).

## 9. Compute summary for the requested additions

| Item | Configuration | n | CPU-h (4-core laptop) |
|---|---|---|---|
| Run A (M1) | σ = 0.07 quench, 34 lone keystones, 15 extra seeds, 120 s | 510 quenches | ≈ 0.8 |
| Run B (M1) | E6b repeat, C1 + σ* = 0.0467, seeds 242–427, independent noise stream, 600 s | 186 runs | ≈ 2.6 (≈ 5.2 with a third stream) |
| Optional (M2) | fresh pair library, corrected-forward B_w,jamb = 0.04, seeds 562–881, plus fold and ±b* quenches | ≈ 320 runs + quenches | ≈ 6 |
| Optional (M5) | E3 β_ref = 2.5, 20 more restarts per cell | 600 runs | ≈ 5 |
| Optional (M9) | cross-machine replay, 10 snapshots × 2 ORCA arms × 6 runs | 120 quenches | ≈ 0.1 |
| All other fixes | re-analysis of existing `data/derived/*.json` and per-run files | — | ≈ 0 |

Referee 2
