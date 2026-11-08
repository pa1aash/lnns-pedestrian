# S1 review synthesis: referee simulation and literature scan

Manuscript: "One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models" (Gang, Veluri). This is the invited LNNS extension of the SIMULTECH 2026 paper.

Snapshot: commit `decbdca` (`reports/audit/snapshot/main.tex`, 1353 lines, 23 pp). Line numbers below refer to that `main.tex`.

Inputs:
- `S1_R1_review.md`: Referee 1, physics of clogging and activated escape.
- `S1_R2_review.md`: Referee 2, statistics and computational methods.
- `S1_R3_review.md`: Referee 3, SIMULTECH/LNNS editor.
- `S1_LIT_literature.md` and `S1_LIT_candidates.bib`: literature scan.

Not counted as defects: Table 4, Sect. 6.3, the Zenodo DOI, and the acknowledgements and disclosure, which are pending by design.

---

## 1. Recommendations

| Referee | Orig. | Signif. | Sound. | Clarity | Present. | Venue | Recommendation |
|---|---|---|---|---|---|---|---|
| R1 (physics) | 3 | 2 | 2 | 3 | 3 | 4 | **Major revision** |
| R2 (statistics) | 4 | 3 | 2 | 3 | 3 | 4 | **Major revision** |
| R3 (editor) | 4 | 3 | 3 | 2 | 3 | 4 | **Major revision** |

The three referees agree on four points:
- The deterministic signatures are convincing: the drive split, the signed push, replay, time-step scaling (Fig. 5) and handedness.
- Extension compliance is met by a wide margin. R3 measured 0.00% 8-gram overlap with the conference body, a longest shared run of 7 words, and at least 90% new material. The title, abstract and conclusions all differ from the conference version.
- The thesis as worded is not yet supported. The weak point is the "frees different deadlocks" leg (Jaccard identity).
- The physics/statistics framing goes further than the evidence in several load-bearing sentences.

Almost all fixes are text or re-analysis of existing JSON. The new runs recommended below total about 12 CPU-h, about 3-4 h wall time on the 4-core laptop once the current queue is free.

**Breaches of the authors' own rules, found by all three referees. Fix before anything else:**
- The Table 2 caption (l. 928-929) and the Table 3 caption (l. 1087) have three sentences each; the limit is two.
- Clinical-trial vocabulary "arm" appears at l. 926, 981, 1053, 1083, 1092 (the Table 3 column header "Arm") and 1133. Replace it with "condition", "intervention" or "resolver" as fits.
- Table 3 is overfull by 47.9 pt (build.log; p. 16) and shows internal experiment codes (E2, E6, E7b, E3).

---

## 2. Merged major issues

The issues are ranked by severity first and, within that, by how many referees raised them. IDs refer to the individual reports (R1-M1 = Referee 1, major issue 1).

Response types:
- **T**: fix the text.
- **A**: new analysis of existing data (about 0 CPU-h).
- **R**: new run.
- **B**: rebut with evidence.

### Severity 1: the thesis

**S1. "Frees different deadlocks" has no same-mechanism baseline, and the data show positive association.**
- Raised by: 3/3 (R1-M1, R2-M1, R3-M3). Lines: 652, 836, 1095-1105 (Table 3, J column), 1114, 1123, 1163, 1166, 1177.
- **Lone trap.** J = 0.20 rests on minority sets of 4 (ORCA) and 2 (noise) with 1 shared. R2 computed that two independent majority-of-5 replicates of the *same* noise condition would give J ≈ 0.40 [0.14, 0.80]. Noise frees ORCA's four unresolved snapshots in only 10/20 runs, against 138/150 elsewhere (one-sided p = 7×10⁻⁴). The hard snapshots are therefore hard for both resolvers.
- **Whole runs.** J = 0.41 sits above the independence value of 0.30, and `E6_analysis.json` gives a permutation p = 0.0023 for overlap *above* independence (verified; 2×2 table 50/35/37/64). The text says "barely more than independent ones would" (l. 1123), which contradicts the authors' own file.
- **Pair block, RVO2.** J = 0 is unremarkable against independence (hypergeometric p ≈ 0.24). It is decisive only against the deterministic null J = 1. The identity probe is therefore valid at the pair block only.
- **What survives.** Replay, Δt, the signed push, handedness, t½ and the final-state class still separate the resolvers, so the thesis survives on those signatures.
- **Response: T + A + R.**
  - T: rewrite every "free different deadlocks" (abstract l. 652, l. 836, 1114, 1123, 1163, 1166, 1177) along the lines of: *"match the rate, but differ in replay, time-step dependence or handedness; at the lone trap and in whole runs the failure sets overlap at least as much as a stochastic resolver overlaps with itself"*. Keep identity as a separating signature at the pair block only, where both resolvers are deterministic.
  - A (0 CPU-h): a noise-against-noise pseudo-replicate J from the existing 5 seeds per snapshot. A per-snapshot association test (logistic regression or Mann-Whitney on k_i/n_i against ORCA outcome). R1's predictor test: does noise failure rank with ΔU from the barrier library, while ORCA failure ranks with the C3 rest-state margin (AUC 0.98)? Report the independence expectation for every J, and a non-degenerate interval for J = 0 or drop the interval.
  - R: runs N1 and N2 (Sect. 3). They supply the noise-versus-noise reference, J(noise, noise′), that every referee asked for.

**S2. The protocol logic: falsification by construction, no decision tolerance, and post-hoc signatures.**
- Raised by: 3/3 (R1-M1, R2-M4, R3-M2, R3-M7). Lines: 834, 981, 1019-1020, 1163, 1172; Table 2, l. 928-977.
- **Falsification by construction (R1).** A control drawn from "a different class" (l. 1020) always fails that class's defining probe. Stochastic means replay- and Δt-dependent, and a tilt is always handed. So "each control fails a probe of its own class" (l. 1163) restates how the controls were chosen.
- **No tolerance (R2).** "Agree on every probe" has no numerical tolerance. For example, C3 RVO2 has ℓ = −0.0048 [−0.0086, −0.0008], which excludes 0.
- **Post-hoc signatures (R2).** The separating evidence in Sect. 6 (J, t½, final-state class, stall survival) is not in Table 2. These signatures and the seed170 exclusion were added after the data were seen. Git shows that Table 2 itself was fixed first (commit f6aff51, 2026-11-07, before the E2 outputs in 1aba2df).
- **Under-specified for other modellers (R3).** The protocol occupies only 6 lines (l. 1020). There is no class-N row and no prerequisites for applying it to another model.
- **Response: T + B.**
  - Recast the class-defining probes as what *assigns* a class.
  - Falsification within a candidate class is the informative case. The paper already has a confirming instance: the frozen-mean push agrees with ORCA on every probe at the lone keystone (30/34 vs 31/34, discordant 0:0; l. 1111). Present it as the two-sided protocol's "confirm" outcome; this is the rebuttal to "by construction".
  - State a per-probe criterion: separation means the 95% interval of the difference excludes ±δ, with δ given per probe.
  - Mark which signatures were fixed before the runs and which were added later, citing the dated commit (f6aff51).
  - Make the protocol a numbered algorithm box at the start of Sect. 4. Add a class-N row to Table 2.
  - Add "Applying the protocol to another model" (about 0.4 pp): prerequisites (restartable state, deterministic replay, a field that is conservative once densities are frozen, term switches), and generic versus model-specific probes.
  - Soften l. 1172.
  - No runs.

**S3. Calibration is in-sample: "held out" is misleading and the lone-trap σ was chosen after the fact.**
- Raised by: 2/3 (R2-M2, R3-M4, R3-M7). Lines: 652, 1114, 1123, 1136, 1163.
- **b\* by construction.** b* was set so that the static fold fraction on the same 46 snapshots equals ORCA's count, so "p = 1.000 and 1.000" (l. 1136) holds by construction.
- **σ = 0.07 picked from the grid.** σ = 0.07 is the nearest of three preset levels, and it matches only in the lone-keystone stratum. Pooled over all 60 snapshots it overshoots by +0.10 [0.003, 0.20].
- **Response: T + A + R.**
  - T: replace "held out" with "not used in the calibration". Remove the rate p-values or label them as checks.
  - A (0 CPU-h): a 2-fold split-sample recalibration of b* and σ, reporting all signatures on the held-back half.
  - R: run N1, which inverts a logistic fit in the lone stratum and reruns at the inverted σ. It also supplies the S1 noise baseline.

### Severity 2: physics claims beyond the evidence

**S4. Effective temperature, Kramers regime and "collective" escape.**
- Raised by: 3/3 (R1-M2, R1-M3, R1-M4, R2-M5, R3-M7, plus R3's Fig. 4 note). Lines: 848, 862, 1003-1008 (Eq. 9), 1017, 1059-1069, 1077, 1116-1117, 1123.
- **Per-agent temperatures (R1-M2).** The temperature scales with τ_i, so it varies up to 1.5× within a snapshot. σ was set from the blocker's τ only. The slope ratio leans >1 in full fits (6/8) and <1 in alone fits (9/10), with sign test p ≈ 0.02. The detailed-balance assumptions (no friction channel without noise, no clipping) are unstated, yet the text says the temperature "follows exactly" (l. 848).
- **Kramers regime (R1-M3).** β = 1.5-3.5 lies outside the asymptotic regime. The E3 miss at β_ref = 2.5 sits where Δt = 0.005 s halves β. B4A_REPORT already attributes it to the low-barrier prefactor; say so in the paper.
- **Weibull shape (R1-M3, R2-M5c).** k = 1.09 [1.05, 1.14] (and 1.14 when frozen) *excludes* 1, so "close to 1" is wrong as stated. Pooling heterogeneous exponentials would push k below 1, so the excess points to an induction transient.
- **Prefactor (R1-M3, R3-M7).** ν is fitted, never predicted, yet l. 1123 calls the result a "no-fit prediction".
- **Circular collapse (R2-M5a).** The collapse in Fig. 4 (right) uses ν̂ estimated with the slope fixed at −ΔU, so the slope of −0.93 holds by construction.
- **Seed170 (R1-M3, R2-M4).** E1b_seed170 (barrier 0.13 J, 0/60 restarts escape) contradicts the picture and was excluded after the fact.
- **Unreported quantities (R2-M5d-f).** The OLS slope 0.72 [0.29, 1.06], 23% censoring, the competing-exit handling and the selection counts (4 of 60 failed the gate, 20 of 36 used in E3, 10 of 32 in E4) are not reported.
- **"Collective" (R1-M4).** Full < frozen holds variationally. Full < alone is confounded by the push from behind (frozen > alone in 2/10).
- **Response: T + A + R.**
  - T: state the assumptions (frozen densities, conservative F₀, linear friction, no contact or clipping, equal T) and drop "exactly". Say that k > 1 is significant and that a short transient explains it. Report the OLS slope, the censoring, the competing-exit rule and the selection counts. Report seed170 as an unexplained failure, not as an exclusion. Either drop the collapse as evidence or refit it with a free intercept and a CI. Remove "no-fit". Replace "because the neighbours give way" with a measured participation statement.
  - A (minutes): the Langer prefactor from the Hessians the authors already have, compared with ν. R1's rough estimate is ν ~ 0.3 s⁻¹ against 0.09 fitted (check). Agreement would be a strong result; disagreement must be stated. Also a participation ratio of the unstable mode at the saddle, and a shifted-exponential fit.
  - R: N3 (equal-temperature E4) and N4 (higher-β E3).

**S5. The ORCA result belongs to the additive force hybrid.**
- Raised by: 1/3 (R3-M1); related to R1-M7. Lines: 13 (title), 652, 916-920, 1110-1111, 1166, 1169.
- "ORCA adds a goal drive" follows from turning v_orca into a relaxation force *added* to the SFM drive (Eq. 6). Velocity-level RVO2, as practitioners run it, has no rest drive. This is the practitioner headline, and as written it is mis-scoped. Note also that at the second trap ORCA does not equal its drive (17 vs 24 of 26, l. 1120).
- **Response: T, with an optional R.**
  - T: say explicitly in Sect. 3 and Sect. 6.1 that the rest drive comes from the force conversion in the additive hybrid. Scope the title, abstract and implications to that model, and add a threats-to-validity sentence.
  - Optional run N8, a velocity-level RVO2 variant. It needs a new update path in the code; there is no velocity-level mode under `code/` or `experiments/` (check). Text scoping is required whether or not the run is done.

**S6. Contact-arch section: the mechanics are mis-stated and the test is under-resolved.**
- Raised by: 1/3 (R1-M6). Lines: 835, 845, 1055-1056, 1177.
- **Mechanics.** "A chain of agents in contact can carry a load only while its members slide" (l. 1056) is wrong: normal forces carry load, and friction only adds stability.
- **Resolution.** The test runs at v₀ = 5 m/s with Δt = 0.01 s. `arch_analysis.json` shows 108 kN peak forces and 21 m/s relative sliding. The explicit friction step may be unstable, so the 0.0 s median lifetime may be numerical. The default drive is never tested.
- **Missed connection.** The lone trap and the pair standoff are soft-core one- and two-agent arches. That framing connects the paper to the granular clogging literature (To 2001; Zuriguel 2005; Janda 2008) and would strengthen it.
- **Response: T + A + R.**
  - T: correct the mechanics sentence. Reframe the two deadlock classes as soft-core arches held by normal forces of range B_w.
  - A: compare the critical width of 0.88 m (l. 1035) with an effective diameter 2[r + B_w ln(2A_w/F_drive)]. The exact form must be derived (check).
  - R: N5 (Δt convergence at 0.0025 s, plus the default drive). If not run, weaken the section to "at the tested resolution".

**S7. The pair "fold" is asserted, not shown.**
- Raised by: 1/3 (R1-M5). Lines: 970-977, 1051, Fig. 7.
- Bisection shows only that the basin is lost. It cannot tell a saddle-node from a global bifurcation or a near-pitchfork. Some thresholds are tiny (b* ≈ 0.001).
- **Response: A + R, or T only.**
  - A + R: run N6, Newton continuation showing λ₁ ∝ (b* − b)^½, the minimum-to-saddle distance ∝ (b* − b)^½ and ΔU ∝ (b* − b)^{3/2}, plus bottleneck passage times. One collapse panel could replace the left panel of Fig. 7.
  - T only: replace "fold" with "loss of the minimum at b*" throughout.

**S8. Rest-state lemma and stuck-alone criterion are presented as findings.**
- Raised by: 2/3 (R1-M9, R3-M7). Lines: 835, 990-1001, 1029-1035, 1111.
- **393/393.** For a lone on-axis blocker at rest, a positive margin is *necessary* for the rest state to exist, so 393/393 agreement is close to guaranteed.
- **C2.** C2 reproducing C1 in 360/360 is a code check: the time-to-collision term never activates from v = 0.
- **C3.** The lemma does not cover C3's velocity-dependent part, and the paper should say so.
- **Response: T + A.** Call these consistency checks. Report the margin histogram and the count of blockers within ±10 N of zero. Report the lateral offsets and the lateral Hessian eigenvalue. Remove or qualify "exact" (l. 1035). State that part (ii) does not apply to C3.

**S9. Class N is inconsistent with Table 2.**
- Raised by: 2/3 (R1-M10, R3-M2). Lines: 929, 977, 1120.
- Table 2 says class N is "tested only by corrected numerics". Yet l. 1120 assigns the published solver to N from *replay* sensitivity, which Table 2 lists as the class-T signature. Replay sensitivity could equally be a finite-time Lyapunov amplification.
- **Response: T + A (static, minutes).** Add the N row. Evaluate v_orca along a 10⁻⁹-10⁻⁶ m displacement at the flipping states to show the published solver's output is discontinuous there (for example, when infeasible constraints are dropped; Table 1, l. 877).

### Severity 3: scope, statistics hygiene, presentation

**S10. Generality: a low-density, end-of-evacuation regime; the pair class needs a modified wall law; horizon effects.**
- Raised by: 1/3 (R1-M7); R3 asks for a threats-to-validity paragraph. Lines: 652, 826, 835, 845, 895, 1035-1037, 1047, 1123.
- **Regime.** Density at detection is ρ ≤ 0.35 ped/m². The blocker is among the last three arrivals in 184/196 deadlocks. 96/98 deadlocks under the default walls are stuck-alone.
- **Pair class.** It needs B_w,jamb = 0.04 m, so the abstract's "two classes" describes two models.
- **Horizon.** 54 of C3 RVO2's 85 whole-run failures are still moving at 600 s, so σ* is partly matched to the horizon.
- **Response: T, plus optional R.**
  - T: in the abstract and introduction, say "deadlocks of the last few agents at a narrow door" and that the pair class arises with a short-range jamb law. Remove the crowd-crush framing at l. 826.
  - R: N7 (rerun the 54 still-moving failures to 1800 s) is worth doing because σ* depends on it.
  - Skip the N-sweep (5-10 CPU-h) and state finite size as a limitation.

**S11. CroMa comparison.**
- Raised by: 2/3 (R1-M8, R2-M8). Lines: 652, 837, 1146-1160, 1175.
- **Invalidation.** The section is an invalidation, yet the transfer of the attribution results to humans is not discussed.
- **Initial conditions.** Start positions and density are not matched, and the long gaps may reflect sparse arrivals.
- **Motivation.** The motivation condition of the 5 human runs is not stated.
- **Intervals.** Bootstrapping over n = 5 is too narrow. The t-based log-ratio interval for C1 is [0.43, 0.61], not [0.46, 0.58].
- **Methods.** The 0.21 m corridor is unexplained, and the fluctuation estimator is uncited.
- **Gaps.** The longest gap is an extreme-value statistic; time-lapse survival is standard.
- **Response: T + A, plus optional R.** Use t-based or Fieller ratio intervals and log-scale gaps. State the motivation condition of each run. Report flow over the 10-90% passage window. Plot time-lapse survival. Add one sentence: "the attribution results are statements about this model class". Optional run N9 (matched start density).

**S12. Clustered intervals, paired tests and multiplicity.**
- Raised by: 1/3 (R2-M3); this bears on the "all intervals 95%" rule. Lines: 1035, 1051, 1056, 1071, 1083, 1095, 1123.
- **Clustered rates.** The Wilson interval over 5 seeds × 34 snapshots treats runs as independent. A cluster bootstrap gives [0.79, 0.94] against [0.81, 0.91].
- **Fold agreement.** The 363/368 count treats the 8 b values per snapshot as independent.
- **Common seeds.** The stall Weibull, σ50 and the width/wall cells all use common seeds. The σ50 goodness of fit (p = 0.985) is implausibly good.
- **Exchangeability.** The final-state permutation test breaks exchangeability under pairing.
- **Multiplicity.** The conference version applied Holm-Šidák correction; the extension applies none.
- **Response: A (0 CPU-h).**
  - Use cluster bootstraps, McNemar for paired cells, and within-seed permutations. Report per-snapshot fold agreement.
  - State the multiplicity policy: either correct within each family of probes, or say that the probes are signatures, not a test family.
  - **Data gap:** `data/E5/` per-run files are not in the snapshot. Confirm they are archived, since the σ50 re-analysis needs them.

**S13. Methods reporting, sample sizes and reproducibility.**
- Raised by: 1/3 (R2-M6, R2-M7, R2-M9); R2 Sect. 7 lists about 30 numbers a reader cannot reconstruct. Lines: 926, 1111, 1182; Table 1.
- **Response: T.**
  - Expand l. 926 into a "Statistics" paragraph: estimator, interval method, resampling unit and number of resamples per quantity.
  - Give one sentence per experiment on n and the interval half-width it achieves. Report the ROC interval [0.91, 1.00].
  - Add the commit/tag, software versions, RNG (PCG64) and a seed table to the availability statement.
  - Define replay in one sentence (which agents, direction, what counts as a match).
  - Split the "Replay" column into "10⁻⁹ m replay" and "seed replicates (noise)".

**S14. Clarity of title, abstract and number density.**
- Raised by: 1/3 (R3-M5); R1 makes the same point under clarity. Lines: 13, 652, 826-839, 1029-1037, 1110-1123.
- **Abstract.** It is 197 words, leaves ORCA and CroMa unexpanded, contains a 50-word sentence, and ends on CroMa, which is not tied to the thesis.
- **Number density.** Paragraphs carry 15-30 numbers (l. 1035 carries more than 30).
- **Jargon.** Coinages such as keystone, second trap, frozen-mean, rest drive and minority set pile up.
- **Response: T.**
  - Revise the title and abstract along the lines of R3 Sect. 6, applying the S1/S5 scoping.
  - Limit the text to about 5 numbers per paragraph and move the rest into tables.
  - Add one glossary sentence in Sect. 4.
  - Merge l. 1160 and l. 1169 into a "Checklist for modellers" (about 6 lines).

**S15. Table 3 layout.**
- Raised by: 2/3 (R3-M6, R2 presentation). Lines: 1086-1109.
- **Response: T.**
  - Fit the table to the text width: drop the pair-block t½ column (all values are ">120"), move ℓ to the Fig. 5 caption with its sample stated, and use `tabularx`.
  - Replace the E-codes with words.
  - Cut the caption to 2 sentences.
  - Rename the "Arm" column (see the rule breaches above).

### Length budget (R3)
The paper is 23 pp now and projects to about 24 pp with the pending items.

- **Cuts available (about 1.5 pp):**
  - duplicate DOI/URL in the references, about 0.7 pp;
  - the Fig. 1 caption;
  - the Sect. 5.1 p-values;
  - Sect. 5.3, compressed;
  - the Sect. 5.4 excluded-snapshot text.
- **Additions:**
  - the protocol box and the transfer subsection (S2);
  - threats to validity (S5/S10);
  - the checklist (S14).
- Net change is about zero.

---

## 3. Requested new runs

CPU-h are for a 4-core laptop, with one room run at about 30-90 s and a lone-trap quench at about 5-30 s. The current queue (E11, E8, E9, E6p) is still running, so none of these can start before it finishes without contention.

| ID | Issue | Configuration | n | CPU-h | Worth doing? |
|---|---|---|---|---|---|
| **N1** | S1, S3 | Lone-trap quench, C1 + noise at the σ from inverting a logistic fit of freed fraction against σ in the lone-keystone stratum (fit from existing E2), 20 seeds per snapshot, 120 s. Outputs: per-snapshot p_i, J(noise, noise′) from two 10-seed halves, association with ORCA outcome, all probes at the calibrated σ. | 34 × 20 = 680 quenches | ~1-2 | **Yes.** Cheapest fix for the thesis and the calibration together (merges R2 Run A and R3-M4). |
| **N2** | S1 | E6b repeat: C1 + σ* = 0.0467, same spawns (seeds 242-427), independent noise stream, 600 s. Outputs: J(noise, noise′), J(ORCA, noise′), association OR with 95% CI. | 186 runs | ~2.6-4.7 | **Yes.** All three referees asked for this reference. |
| N2b | S1 | C3 RVO2 whole runs with spawns perturbed by 10⁻⁹ m (deterministic-chaos reference for J). | 186 runs | ~6-9 | Conditional. Only if N2 leaves J(ORCA, noise) ambiguous. |
| **N3** | S4 | E4 full condition at equal temperature, σ_i = σ_ref(τ_ref/τ_i)^½, on the 8 usable full snapshots + seed170, β ∈ {1.5, 2.5, 3.5}, 20 restarts per level, censoring as now. Outputs: slope ratios with CI, Weibull k, ν. | 540 short runs | ≤2 | **Yes.** Removes the multi-temperature objection outright. |
| **N4** | S4 | E3 at β_ref = 3.5 on the same 20 snapshots, Δt ∈ {0.005, 0.01, 0.02}, 20 restarts, 900 s censoring (already proposed in B4A_REPORT). | 1200 runs | ~3-5 | **Yes, if time allows.** Moves the Δt test into the Kramers regime. Otherwise report the regime limit as text. |
| **N5** | S6 | Arch test at Δt = 0.0025 s (v₀ = 5 m/s) plus the default drive and v₀ ∈ {2, 3} m/s, 25 runs each. | 100 runs | ~2-4 | **Yes.** Without it the arch section's claim is at risk. Δt = 0.001 s (25 runs, ~4-5 CPU-h) is optional. |
| **N6** | S7 | Newton continuation of the pair minima to b* (static, minutes), plus quenches at b = b*(1 + ε), ε ∈ {0.01, 0.03, 0.1, 0.3}, both signs. | 46 × 2 × 4 = 368 quenches | <1 | **Yes.** Cheap, and turns an assertion into a normal-form result. |
| N7 | S10 | Rerun the 54 still-moving C3 RVO2 E6 failures to 1800 s. Report whether σ* moves. | 54 runs | ~3-5 | Moderate. Do it if N2 is run (the same σ* is at stake). |
| N8 | S5 | Velocity-level RVO2 (LP velocity applied directly, SFM drive off), w = 0.8 m, 50 seeds, 600 s, plus quench of the 34 lone keystones. | 50 runs + 34 quenches | ~2 (+ code) | Optional. Needs a new update path. Text scoping is the required fix. |
| N9 | S11 | CroMa, 5 variants × 25 runs with measured start positions or waiting-zone density. | 125 runs | ~1-3 | Optional. Do the re-analysis (S11 A) first. |
| N10 | S10 | N-sweep N ∈ {50, 100, 200} × 100 seeds. | 300 runs | ~5-10 | **No.** State finite size as a limitation. |
| N11 | S3 | Fresh pair library (seeds 562-881) plus folds and ±b* quenches. | ~320 runs | ~6 | **No.** The split-sample re-analysis is enough. |
| N12 | S4 | E3 β_ref = 2.5, 20 more restarts per cell. | 600 runs | ~5 | **No.** Report the shortfall plainly. |
| N13 | S13 | Cross-machine replay, 10 snapshots × 2 ORCA conditions × 6 replays. | 120 quenches | ~0.1 | Optional; trivial cost. |
| static | S4, S9 | Langer prefactor from the Hessians; v_orca discontinuity scan of the published solver. | — | minutes | **Yes.** |

Totals:
- **Recommended set (N1-N6 + static): about 11-19 CPU-h**, about 3-5 h wall on 4 cores.
- With the conditional or moderate runs (N2b, N7): about 20-33 CPU-h.
- Everything else in the reports is re-analysis of existing JSON at about 0 CPU-h. The exception is the σ50 cluster bootstrap, which needs the `data/E5/` per-run files.

---

## 4. Response plan by issue (summary)

| Issue | Raised by | Type | Core response |
|---|---|---|---|
| Rule breaches (captions, "arm", Table 3 overfull) | 3/3 | T | Fix immediately. |
| S1 different deadlocks | 3/3 | T+A+R (N1, N2) | Reword. Noise-vs-noise reference. Association test. Keep identity as a signature at the pair block only. |
| S2 protocol logic | 3/3 | T+B | Probes assign the class; frozen-mean push as the "confirm" case; per-probe δ; mark pre- and post-hoc signatures (commit f6aff51); algorithm box; N row; transfer subsection. |
| S3 in-sample calibration | 2/3 | T+A+R (N1) | "Not used in the calibration"; drop rate p-values; 2-fold split; inverted σ. |
| S4 temperature / Kramers / collective | 3/3 | T+A+R (N3, N4) | State assumptions; k > 1 as a transient; seed170 reported; drop the circular collapse; Langer prefactor; participation ratio. |
| S5 ORCA hybrid scope | 1/3 | T (+N8) | Scope the title, abstract and implications to the additive hybrid. |
| S6 contact arches | 1/3 | T+A+R (N5) | Correct the mechanics; soft-core arch framing; Δt convergence. |
| S7 pair fold | 1/3 | A+R (N6), or T | Continuation scaling, or drop the word "fold". |
| S8 lemma / stuck-alone | 2/3 | T+A | "Consistency checks"; margin histogram; lateral stability. |
| S9 class N | 2/3 | T+A | N row; discontinuity scan. |
| S10 regime / generality | 1/3 | T (+N7) | "Last few agents" framing; pair-class wall law in the abstract; horizon check. |
| S11 CroMa | 2/3 | T+A (+N9) | t/Fieller intervals; motivation condition; gap survival; transfer sentence. |
| S12 clustered intervals | 1/3 | A | Cluster bootstrap, McNemar, within-seed permutations, multiplicity policy. |
| S13 reproducibility | 1/3 | T | Statistics paragraph, seed table, versions, replay definition. |
| S14 clarity / abstract | 1/3 | T | New abstract; fewer numbers per paragraph; glossary; checklist. |
| S15 Table 3 | 2/3 | T | Fit to width, remove codes, two-sentence caption. |

The detailed exact-wording replacements for overstated claims are in Sect. 6 of each referee report. R1 has 27, R2 has 20 and R3 has 13; most overlap with S1-S4 and S8.

---

## 5. Literature verdict on the novelty claims

(See `S1_LIT_literature.md` for the candidates and `S1_LIT_candidates.bib` for the fetched entries.)

**Overall: no novelty claim is contradicted.** The scan found 15 strong candidates, each with a DOI that resolves. It found no prior work that makes any claim in the paper false. Six claims need a citation and narrower wording.

| Claim (line) | Verdict | Key precedent | Action |
|---|---|---|---|
| Thesis: rate matching is not evidence of a shared mechanism (l. 832) | Hedge | Beven 2006 (equifinality); Wolinski et al. 2014 (crowd models) | Cite both. Present the *protocol* as the contribution, not the principle. |
| Calibrate-then-falsify protocol, five classes, rest-state lemma (l. 834) | Safe | none found | Keep. Add the equifinality and pattern-oriented framing before l. 854. |
| "We have not found an earlier study…" (l. 854) | Safe (already hedged) | — | Keep. |
| Lone trap set by the jamb wall law; stuck-alone criterion (l. 835, 1169) | Safe, needs context | Xu, Chraibi & Seyfried 2021 (boundary parameters control clogs in a velocity model); Cornes, Frank & Dorso 2021 (wall-attached clusters) | Cite both. The criterion itself is new. |
| Pair standoff broken by a lateral bias at a fold (l. 835) | Hedge | Grover, Liu & Sycara 2020/2023 (symmetry causes robot deadlock); Liu et al. 2026 (ORCA in symmetric scenes) | Claim the fold analysis (S7 makes it stronger), not symmetry breaking. |
| "Contact arches never persist" (l. 835, 1056) | Hedge | Parisi & Dorso 2005; Cornes et al. 2021 (transient blocking clusters in the SFM) | Claim the 10 s bound and the friction argument. This lines up with the S6 correction. |
| Collective activated escape over string-method barriers (l. 835, 1179) | Safe | none found in crowds | Add the active-matter caveat (Woillez et al. 2019) and the gradient-field justification. This matches S4. |
| "Exact effective temperature" (l. 1179) | Hedge | Standard AR(1) stationary variance; Grønbech-Jensen & Farago 2013 (Δt-dependent discretised-Langevin temperature) | Use "the effective temperature… which follows exactly from the stationary variance of the damped velocity recursion". The novelty is using it as a Δt signature. |
| ORCA acts as an added goal drive (l. 836) | Safe | none found | Keep, scoped to the additive hybrid (S5). |
| "Noise is not neutral" (l. 1169) | Hedge (first half) | Helbing, Farkas & Vicsek 2000 (freezing by heating) | Cite. Claim the Δt dependence. |
| Like-for-like human comparison at 0.8 m (l. 837, 1179) | Safe as worded ("new in this version") | Adrian, Seyfried & Sieben 2020; Rzezonka et al. 2022 (a model run against the same entrance experiments) | Cite both in Sect. 7 (l. 1151 cites only the data DOI). It is not a first for the field. |

**Other references the referees expect.** These overlap with S6/S10/S11:
- granular clogging and arching: To et al. 2001; Zuriguel et al. 2005, 2014; Janda et al. 2008; Garcimartín et al. 2016 (human clogs, heavy tails);
- time-lapse survival methodology: Pastor et al. 2015;
- the adversarial faster-is-slower evidence: Haghani, Sarvi & Shahhoseini 2019;
- the clog-stability mode: Hathcock et al. 2025;
- arch failure as first passage: Merrigan et al. 2018.

R1 Sect. 7 and R2 Sect. 8 add physics and statistics methods references (Langer and Kramers rate theory, cluster bootstrap, Fieller); entries marked "check" there were not verified. Only the 21 entries in `S1_LIT_candidates.bib` were fetched from primary sources (doi.org/Crossref), and each carries its source comment. Any reference taken from the referee reports must be fetched the same way before it enters `refs.bib`.

**Net effect on the paper.** Adding the 8-10 A-grade citations costs about 0.3-0.4 pp of references. The cuts listed under the length budget cover it. The rewording strengthens the paper: the protocol, the stuck-alone criterion, the barrier computation and the Δt signature remain the claimed contributions, and each now sits against a named precedent.
