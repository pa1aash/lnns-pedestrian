# Numbers and claims check (integration re-audit, 2026-11-10)

Scope: HEAD 0b65cbe on wt-I, against audit snapshot decbdca. Sources: paper/sections/*.tex, paper/tables/*.tex,
figures/fig1_caption.tex, paper/numbers.tex, paper/registry/*.yaml, data/derived/*.json, analysis docstrings and
reports F1/F2/F3/P/S3. No source file was edited.

Check scripts (scratch, not committed):
`check_macros.py`
(registry -> recomputed value -> numbers.tex -> usage) and `.../scratchpad/expand.py` (text with every macro
replaced by its printed value, used for the claim review).

Each fix below gives an `old` string that occurs exactly once in the named file, and a `new` string. Every fix keeps
the specific claim and carries numbers as macros. New registry entries are listed in §1.4.

---

## 1. Macro check

### 1.1 Counts

| Check | Result |
|---|---|
| Registry entries (paper/registry/*.yaml) | 1316 (+40 `…Unit` macros = 1356) |
| `\newcommand`s in paper/numbers.tex | 1356 |
| Recomputed value (file, key, fmt via tools/make_numbers.py) ≠ numbers.tex | **0** |
| In registry but not in numbers.tex (stale numbers.tex) | **0** |
| In numbers.tex but not in registry | **0** |
| Missing file or key | **0** |
| Distinct numbers.tex macros used in sections, tables and the Fig. 1 caption | 523 |
| Macros used but not defined (numbers.tex, main.tex, local `\newcommand`, LaTeX/llncs) | **0** (the only unknown tokens are LaTeX primitives: `\ackname`, `\discintname`, `\numexpr`, `\the`, `\bigl`, …) |
| Table 3 / Table 4 rebuilt by make_table3.py / make_table4.py into scratch, diffed with paper/tables | byte-identical |
| paper/submission/main.tex | holds all 1356 definitions verbatim and every source line (except `../figures/` paths) |
| Defined but not used in the text | 833 (not a defect) |

Every printed value equals its data value formatted by its fmt.

### 1.2 Macro semantics (value right, key worth changing)

- `RunNOneUnresNoise` (06_attribution.tex:22, "only 3–4 snapshots stay unresolved") reads
  `identity.noise_vs_noise_halves.n_b`, which is the unresolved count of the second seed half (3). The full 20-seed
  noise set also has 3 unresolved (`identity.noise_vs_C3_rvo2.n_a`), so the printed value is right. The key should
  be `identity.noise_vs_C3_rvo2.n_a` so the macro measures what the sentence says. The value does not change.

### 1.3 Literal numbers that report a result

Design constants and parameter values (w, B_w, 120/300/600/900 s, σ grid levels, seed and run counts of the
design, 10⁻⁹ m, ±10 N, plotting scales) are acceptable and are not listed.

| file:line | literal | should carry |
|---|---|---|
| 06_attribution.tex:48 | "C2 and C4 none" (throat overlap steps at w = 1.0 m) | new `\EelevenCTwoTimestepsMean`, `\EelevenCFourTimestepsMean` (§1.4) |
| tables/table4_conference.tex:19 (make_table4.py:98) | "C2 and C4 0 steps" | same two macros |
| 07_validity.tex:13 | "in the five runs" | `\EtenHumanN` |
| 05_deadlock_physics.tex:55 | "none at 2\,m/s"; "at the default drive none forms"; "every run completes" (Δt = 0.0025 s); "every run completes at Δt = 0.01 s" | word forms of `\RunNFiveVTwoEpisodes`, `\RunNFiveDefaultEpisodes`, `\RunNFiveFineComplete`/`\RunNFiveFineN`, `\ArchComplete`/`\ArchN` (all exist; optional) |
| 05_deadlock_physics.tex:16 | "the seventh" | `\CriterionNegMargin` − `\CriterionNegTwoAgent` (word form; optional) |
| tables/table3_matched.tex:25 | "[0, …]" lower bound of the RVO2 pair J | structural 0, but `\TabThreePairRvoJacFInt` exists (optional) |

Proposed fixes for the first three rows:

File paper/sections/06_attribution.tex
```old
C2 and C4 none; Wilcoxon
```
```new
C2 $\EelevenCTwoTimestepsMean$ and C4 $\EelevenCFourTimestepsMean$; Wilcoxon
```

File experiments/tables/make_table4.py
```old
C2 and C4 0 steps "
```
```new
C2 {M('EelevenCTwoTimestepsMean')} and C4 {M('EelevenCFourTimestepsMean')} steps "
```

File paper/sections/07_validity.tex
```old
gap in the five runs exceeds 2\,s.
```
```new
gap in the \EtenHumanN\ runs exceeds 2\,s.
```

### 1.4 Proposed registry entries

```yaml
# runs.yaml or core.yaml
EfourWeibFrozenLo: {file: E4_analysis.json, key: "per_condition.frozen.weibull.ci95.0", fmt: "{:.2f}"}   # 1.06
EfourWeibFrozenHi: {file: E4_analysis.json, key: "per_condition.frozen.weibull.ci95.1", fmt: "{:.2f}"}   # 1.21
EfourWeibAloneLo:  {file: E4_analysis.json, key: "per_condition.alone.weibull.ci95.0",  fmt: "{:.3f}"}   # 1.002 (2 dp would print 1.00 and look like it covers 1)
EfourWeibAloneHi:  {file: E4_analysis.json, key: "per_condition.alone.weibull.ci95.1",  fmt: "{:.2f}"}   # 1.15
# table4.yaml
EelevenCTwoTimestepsMean:  {file: E11_analysis.json, key: "cells.C2.w1p0.zones.throat.unfiltered.overlap_timesteps.mean",      fmt: "{:.0f}"}  # 0
EelevenCFourTimestepsMean: {file: E11_analysis.json, key: "cells.C4_rvo2.w1p0.zones.throat.unfiltered.overlap_timesteps.mean", fmt: "{:.0f}"}  # 0
# e6_e10.yaml
EtenHumanUnpassed: {file: fix_reg.json, key: "human.unpassed", fmt: "{:d}"}   # 1
# runs.yaml, key correction (value unchanged, 3)
RunNOneUnresNoise: {file: N1_analysis.json, key: "identity.noise_vs_C3_rvo2.n_a", fmt: "{:d}"}
```

---

## 2. Changed-sentence verdicts

`git diff decbdca..HEAD -- paper/ figures/fig1_caption.tex` rewrites almost every paragraph, so I checked every
claim-bearing sentence of the current text against its data. The OK rows below give the key data values. Every
WRONG or IMPRECISE row has a fix.

### 2.1 WRONG

**W1. 05_deadlock_physics.tex:39 (§5.2, Weibull).** "The Weibull shape of the escape times exceeds 1 only when
pooled over the three conditions, 1.09 [1.05, 1.14]; in the full condition it is 1.05 [0.97, 1.14], and 1.04 [0.96,
1.12] at equal temperatures."
Data (E4_analysis.json per_condition.*.weibull): full 1.053 [0.970, 1.139]; **pinned 1.135 [1.064, 1.209]; alone
1.073 [1.002, 1.147]**. Pooled 1.091 [1.048, 1.135]. N3 1.038 [0.958, 1.122]. Both the pinned and the alone shape
exceed 1, so "only when pooled" is false. The same paragraph says this too: the lag-fit pinned shape from 10 s is
still 1.09 [1.01, 1.17]. F3_REPORT.md:23 makes the same mistake.

File paper/sections/05_deadlock_physics.tex
```old
The Weibull shape of the escape times exceeds 1 only when pooled over the three conditions, \EfourWeib\ [\EfourWeibLo, \EfourWeibHi]; in the full condition it is
```
```new
The Weibull shape of the escape times exceeds 1 pooled over the three conditions, \EfourWeib\ [\EfourWeibLo, \EfourWeibHi], and in the pinned and alone conditions, \EfourWeibFrozen\ [\EfourWeibFrozenLo, \EfourWeibFrozenHi] and \EfourWeibAlone\ [\EfourWeibAloneLo, \EfourWeibAloneHi]; in the full condition it is
```
(This needs the four new macros of §1.4. `\EfourWeibFrozen` and `\EfourWeibAlone` already exist.)

**W2. 06_attribution.tex:48 (§6.3).** "The printed noise level for half completion lies above the new interval."
Data: the printed value is 0.049 (E5_analysis.json conference_sigma50). The interval §5.2 reports for the
published-reproduction mode is the seed-cluster bootstrap [0.0407, 0.0490] (fix_a6.json
e5.E5a_published.seed_cluster_boot95), printed [0.041, 0.049]. §5.2 itself says the printed value "lies at the
upper edge of both". The printed value is above only the profile-likelihood interval [0.042, 0.047]
(E5a_analysis.json logistic_core.ci95_profile), which Table 4 row 14 still prints. So the sentence contradicts the
interval the paper reports. See contradiction C1, which also covers the fixes to §3 and Table 4.

File paper/sections/06_attribution.tex
```old
The printed noise level for half completion lies above the new interval.
```
```new
The printed noise level for half completion, \EfiveConfSigmaFifty\,m/s, lies at the upper edge of the seed-resampled interval [\FixAsixSigFiftyPubClLo, \FixAsixSigFiftyPubClHi]\,m/s (Sect.~\ref{sec:escape}).
```

**W3. 07_validity.tex:13 (§7, new sentence).** "Every tracked participant passes the entrance in every run."
Data: fix_reg.json human.unpassed = 1. One tracked ID never crosses the entrance plane; F2_REPORT.md:10 calls it
"4D040's unpassed track is a lost track". As written, the sentence is contradicted by the data.

File paper/sections/07_validity.tex
```old
Every tracked participant passes the entrance in every run.
```
```new
Every participant passes the entrance in every run; \EtenHumanUnpassed\ track is lost before the entrance.
```

### 2.2 IMPRECISE

**I1. 05_deadlock_physics.tex:39 (§5.2, N3).** "With every agent at the blocker's $k_BT_{\rm eff}$ (540 runs on 9
snapshots), the median ratio is 1.03 (range 0.58–1.46; interval covering 1 in 7 of 8 fits)."
Data (N3_analysis.json): ratio_median 1.033, range 0.584–1.455, covers 1 in 7 of 8, n_runs 540, n_snapshots 9.
The numbers are right. But N3 repeats only the **full** condition, and the sentence comes right after the pooled
three-condition fit, so the reader cannot tell which condition it means. It also leaves out the comparison it rests
on: E4 full, where only the blocker is at that temperature, gives 1.15. The paired median difference is −0.10, sign
test p = 1.0.

File paper/sections/05_deadlock_physics.tex
```old
With every agent at the blocker's $k_BT_{\rm eff}$ (\RunNThreeRunsN\ runs on \RunNThreeSnapN\ snapshots), the median ratio is \RunNThreeRatioMed\ (range \RunNThreeRatioMin--\RunNThreeRatioMax; interval covering 1 in \RunNThreeCover\ of \RunNThreeFits\ fits).
```
```new
In the full condition with every agent at the blocker's $k_BT_{\rm eff}$ (\RunNThreeRunsN\ runs on \RunNThreeSnapN\ snapshots), the median ratio is \RunNThreeRatioMed\ (range \RunNThreeRatioMin--\RunNThreeRatioMax; interval covering 1 in \RunNThreeCover\ of \RunNThreeFits\ fits), against \EfourRatioFull\ with only the blocker at that temperature.
```

**I2. 05_deadlock_physics.tex:41.** "Two snapshots are left out: …"
Data (E4_analysis.json): per_condition.frozen/alone.n_arrhenius_fits = 10, full = 8. Both snapshots (seed60 with
full ΔU 0.02 J, seed170) are left out of the **full** condition only.

File paper/sections/05_deadlock_physics.tex
```old
Two snapshots are left out:
```
```new
Two snapshots are left out of the full condition:
```

**I3. 05_deadlock_physics.tex:50 (§5.3, N6).** The sentence "In the 66 cases where continuation locates it, the
minimum–saddle distance scales with $\delta=1-b/b_f$ with exponent 1.000 and the work with 2.000 … quench passage
… −0.16" matches the data. N6_analysis.json: n_fold 66 = status "ok", where the corrector converged to the loss
point; 26 "corrector failed" cases go to the fallback scan. slopes.dist.median 0.9996, slopes.W.median 1.9996,
quench median slope −0.157. The 92/92 segment-end count and μ₁ at the loss, 64.8–121.0 N/m, are also right. So
"where continuation locates it" correctly describes n_fold against the fallback cases.
Two points are imprecise:
(a) In δ, $b_f$ is the continuation's loss point, not the bisection threshold defined two sentences earlier. Their
ratio has median 0.986 and minimum 0.34 (b_f_over_bisection).
(b) For the 26 fallback cases, "reaches the end of a jamb segment" is measured at the last converged bias: a median
0.98 of the bisection threshold, minimum 0.755 (fallback.b_last_over_bstar).

File paper/sections/05_deadlock_physics.tex
```old
In the \RunNSixFoldN\ cases where continuation locates it, the minimum--saddle distance scales with $\delta=1-b/b_f$ with exponent
```
```new
In the \RunNSixFoldN\ cases where continuation locates it (the other \RunNSixFallbackN\ keep the minimum to a median \RunNSixFallbackReachMed\ of the bisection threshold), the minimum--saddle distance scales with $\delta=1-b/b_f$, $b_f$ the continued loss point (a median \RunNSixBfBisMed\ of the bisection value), with exponent
```

**I4. 05_deadlock_physics.tex:16.** "Removing the blocker gives a lone keystone in 34 of corrected-forward
deadlocks, …" The denominator is missing. It is 196 = 34 + 160 + 2 (E1_chain.json class_counts.E1b, equal to
`\ChainBlockerN`).

File paper/sections/05_deadlock_physics.tex
```old
gives a lone keystone in \KeystoneBLone\ of corrected-forward deadlocks
```
```new
gives a lone keystone in \KeystoneBLone\ of the \ChainBlockerN\ corrected-forward deadlocks
```

**I5. 08_discussion.tex:13 (§8 unifying sentence).** "Both types are set by the wall geometry at the door edges:
the lone trap by the jamb's wall range, the pair standoff by the end of the jamb segment, where its minimum is
lost." N6 shows that a lateral **bias** removes the pair minimum where a member reaches the segment end. It does not
show that the segment end sets the standoff. The standoff exists only with the short-range jamb law: E7 has 11 of 11
deadlocks as pair or group standoffs with $B_{w,\rm edge}$, against 2 of 98 with default walls.

File paper/sections/08_discussion.tex
```old
Both types are set by the wall geometry at the door edges: the lone trap by the jamb's wall range, the pair standoff by the end of the jamb segment, where its minimum is lost.
```
```new
Both types are set by the wall law at the door edges: the lone trap by the jamb's default wall range, the pair standoff by the short range $B_{w,\rm edge}$, and a lateral bias removes the pair's minimum where a member reaches the end of a jamb segment.
```

**I6. 01_introduction.tex:19 (§1 Physics bullet).** "below a critical width of 0.88\,m". The value is right
(E7 w50_logit 0.88 [0.87, 0.89], default walls). §9, §6.3 and Table 4 qualify it with the default wall law, and with
$B_{w,\rm edge}$ the 0.8 m door already completes 89/100.

File paper/sections/01_introduction.tex
```old
below a critical width of \EsevenWcrit\,m (Sect.~\ref{sec:lone})
```
```new
below a critical width of \EsevenWcrit\,m under the default wall law (Sect.~\ref{sec:lone})
```

**I7. 00_abstract.tex:3.** "each differs from ORCA in replay, time-step dependence, time to free or handedness". The
whole-run noise control differs in time to completion **and final-state class** (p = 1.1×10⁻³). §1, §6.2, §8 and
§9 all name the final state.

File paper/sections/00_abstract.tex
```old
time-step dependence, time to free or handedness
```
```new
time-step dependence, time to free, final state or handedness
```

**I8. 06_attribution.tex:48 (§6.3).** "The printed completion counts at w = 0.8 m are single realisations of 25 runs,
and larger ensembles in the published-reproduction mode agree with them: published ORCA completes 29/50 …"
Data: only published ORCA was rerun here (E6p, verdict confirmed, Fisher p = 0.632). Table 4 marks the C1 count
(0/25, against 3/200) **revised**, so the plural "agree with them" contradicts Table 4.

File paper/sections/06_attribution.tex
```old
and larger ensembles in the published-reproduction mode agree with them: published ORCA completes
```
```new
and for published ORCA a larger ensemble in the published-reproduction mode agrees: it completes
```

**I9. 06_attribution.tex:22 (§6.1).** "two halves of the noise seeds overlap about as much ($J=0.25$ [0.14, 0.50])
as they overlap ORCA (0.25)". Per fix_a1.json split_2v3, the "halves" are subsets of 2 and 3 of the 5 seeds. The
bracket is the 95% range over random splits (`range95`), not a confidence interval, and it is not labelled as a
range. The neighbouring sentences label theirs "(95\% of splits)".

File paper/sections/06_attribution.tex
```old
two halves of the noise seeds overlap about as much ($J=\FixAoneJNoiseNoise$ [\FixAoneJNoiseNoiseLo, \FixAoneJNoiseNoiseHi])
```
```new
two- and three-seed subsets of the noise seeds overlap about as much ($J=\FixAoneJNoiseNoise$ [\FixAoneJNoiseNoiseLo, \FixAoneJNoiseNoiseHi], 95\% of random splits)
```

**I10. 06_attribution.tex:48 (§6.3, convention).** "C1 $1.16\pm1.86$ steps per run". The ± is the SD
(E11 overlap_timesteps.sd) but is not labelled. §3 states that bracketed values are 95% intervals and says nothing
about ±.

File paper/sections/06_attribution.tex
```old
\EelevenCOneTimestepsSD$ steps per run
```
```new
\EelevenCOneTimestepsSD$ (mean $\pm$ SD) steps per run
```

**I11. Table 4 row 17 (make_table4.py:174).** "lone wall-law trap (393/393)". `CriterionAgree` is
stuck_alone_criterion_check.agree: the margin criterion predicts the keystone test in 393/393. It is not 393 lone
traps. §5.1 has 386 with positive margin and 7 pair standoffs.

File experiments/tables/make_table4.py
```old
lone wall-law trap ({frac('CriterionAgree', 'CriterionN')})
```
```new
lone wall-law trap, criterion exact in {frac('CriterionAgree', 'CriterionN')}
```

**I12. Table 4 row 15 (make_table4.py:167).** "a matched bias frees other standoffs ($J=0.43$)". J = 0.43 means 13
of 30 are shared. The abstract and §1 say "partly different".

File experiments/tables/make_table4.py
```old
a matched bias frees other "
```
```new
a matched bias frees partly different "
```

**I13. Table 3 caption (make_table3.py:170).** "Noise rows count runs, five seeds per snapshot." That is true of the
lone-trap row (170 = 34 × 5). The whole-run noise row counts seeds (99/186, one run each).

File experiments/tables/make_table3.py
```old
Noise rows count runs, five seeds per snapshot."
```
```new
Lone-trap noise rows count runs, five seeds per snapshot; whole-run rows count seeds."
```

**I14. 01_introduction.tex:18 (§1 Method bullet).** "a rest-state lemma shows that no force term vanishing at rest
can resolve a deadlock of the noise-free model". Proposition 1 also requires $\mathbf v\cdot\mathbf G\le0$, and
part (ii), stability, is what rules out resolution. ORCA's constraint part, which is velocity dependent, is
explicitly excluded in §4.

File paper/sections/01_introduction.tex
```old
no force term vanishing at rest can resolve
```
```new
no dissipative force term vanishing at rest can resolve
```

### 2.3 OK (checked against data)

- **§5.2 N3:** 540 runs, 9 snapshots, median 1.03 (0.58–1.46), covers 1 in 7/8. E4 full Weibull 1.05 [0.97, 1.14];
  N3 1.04 [0.96, 1.12]. Collapse −0.93 [−0.98, −0.88]. Lag fits, ν, Langer 25/28, PR 1.2, saddle 10/10 at 0.30.
- **§5.3 N6:** 92/92 at a segment end. μ₁ at loss 65–121 N/m (all.mu1_at_loss_*), unchanged up to the loss
  (mu1_ratio 0.9986–1.0001; fallback 0.9955–1.0004). Exponents 1.000 and 2.000 against 0.5 and 1.5. Passage
  exponent −0.16 against −0.5. The "where continuation locates it" description is correct (see I3).
- **§5.4 arches:** 22/25, 103 episodes, size ≤ 10, 108 kN, max 2.9 s, p95 0.59 s, 0/25 persistent, Wilson ≤ 0.13,
  25/25 complete (arch_analysis.json). At Δt = 0.0025 s: 25/25 runs with an arch, 22.2 kN, max 3.3 s, 25/25
  complete. At 3 m/s: 8 episodes, max 0.1 s. At 2 m/s: 0. Default drive: 0 arches, 25/25 deadlock, 0 deadlocks with
  an arch at stop.
- **§6.1 N1:** σ = 0.0717 (logistic inversion, 20 seeds × 34). 588/680. Δ −0.018 [−0.074, 0.044] against C3 RVO2.
  J noise–noise (seed halves 0–9/10–19) 0.75 [0, 1]; J noise–ORCA 0.75 [0, 1]; independence 0.06, p = 4.0×10⁻⁴.
  Unresolved: noise 3, halves 4 and 3, ORCA 4, so "only 3–4 snapshots stay unresolved" is right. 24/80 freed on
  ORCA's unresolved snapshots.
- **§6.2 N2:** noise–noise is E6b vs N2: 0.48 [0.39, 0.56]. Noise–ORCA is E6a vs E6b (first stream) 0.41 and E6a
  vs N2 (second stream) 0.51, quoted in that order. Independence values: 0.30 (E6a–E6b), 0.32 (E6a–N2), 0.33
  (E6b–N2), so "0.30–0.33" covers all three. Failure states 31 at rest / 54 moving; noise never at rest (0/87),
  56/31/0. 72 of 122, 35:37. 64 both complete.
- **§6.1 second trap:** 17 vs 24 of 26, 7:0, p = 0.016. 2/10 against 15/16, Fisher p = 2.3×10⁻⁴ (recomputed).
  5/300 published-LP flips.
- **§6.3:** E6p 29/50 [0.44, 0.71], p = 0.632, confirmed. E11 throat C1 1.16 (printed 1.20), C2 = C4 = 0,
  p = 0.011, 0 episodes ≥ 0.1 s, status revised. E8 C3_pub/C1 0.99 [0.89, 1.13], gridlock 1 vs 4 of 75, RVO2 1.12
  [1.02, 1.26], withdrawn. E9 C2/C1 1.01 [0.96, 1.06]; densest L17: 16.1 and 15.2 against printed 16.1 and 5.9;
  withdrawn.
- **§8 calibration paragraph:** separations and identity "only there" agree with Table 3 and §6.
- **§9:** critical width 0.88 m (E7 default walls). "Contact arches break within 3.3 s": 3.3 s is the maximum
  lifetime over every arch run at both time steps (2.9 s at Δt = 0.01 s, 3.3 s at 0.0025 s, 0.1 s at 3 m/s). The
  pair-minimum clause agrees with N6.
- **Back matter, Main Differences:** the four rerun verdicts match Table 4 and the analysis JSON `verdict` fields:
  throat overlaps revised (E11), counterflow gridlock withdrawn (E8), crossing tripling withdrawn (E9), published
  ORCA completion confirmed (E6p).
- **§5.1:** g_max, drives and 0.234/0.013 checked. Criterion 386 + 7 = 393 (E1a 197 + E1b 196); second trap
  296/314. Deciles 0.14–0.20 over the first eight (minimum at decile 6), 0.62 last. E7 counts, p-values, 0.75/0.92 m.
- **§7:** all five variants lie in 0.40–0.59 of the human flow. Gaps > 2 s: 11–19 per run. Longest gap 5.7–6.8 s
  over the four deterministic variants. Fluctuation 0.087–0.109. By-corridor ranges 0.54–0.81 and 0.62–0.91 cover
  all variants.
- **§3:** blocker has ≤ 10 others within R, ρ ≤ 0.35, Weidmann factor ≥ 0.994, so "within 1%" holds.
- **Not verifiable from data/derived:** §4 positive control, "the rest-drive push frees every blocker ORCA frees".
  E2_analysis.json gives only marginals (push 31/34, C3 RVO2 30/34), not the paired discordance of the push against
  C3. Add a `frozen_plus_vs_C3_rvo2` discordance to E2_analysis.json and a macro.

---

## 3. Cross-section contradictions

**C1. σ₅₀ interval (four places disagree).**
- §3 (03_model.tex:50): "the half-completion noise level σ₅₀ a profile-likelihood interval".
- §5.2 (05:43): seed-cluster bootstrap, [0.040, 0.049] corrected and [0.041, 0.049] published, "lies at the upper
  edge of both".
- Table 4 row 14: profile interval [0.042, 0.047], status "revised".
- §6.3: "lies above the new interval" (W2).

The seed-cluster interval is the right one: outcomes are correlated across levels within a seed, with mean
between-level correlation 0.30–0.35 (fix_a6.json). Fixes: W2 above, plus the two below. Under the inclusion rule
used for the E6p row, the printed 0.049 lies inside [0.0407, 0.0490], so row 14's status needs re-judging. It is
"confirmed" by that rule, with a margin of only 2×10⁻⁵ m/s; keep "revised" only if the authors state a different
rule.

File paper/sections/03_model.tex
```old
the half-completion noise level $\sigma_{50}$ a profile-likelihood interval from a logistic fit
```
```new
the half-completion noise level $\sigma_{50}$ of a logistic fit a seed-cluster bootstrap interval
```

File experiments/tables/make_table4.py
```old
ci('EfiveASigmaFiftyLo', 'EfiveASigmaFiftyHi')
```
```new
ci('FixAsixSigFiftyPubClLo', 'FixAsixSigFiftyPubClHi')
```

**C2. Flow-ratio intervals.** §3 says "flow ratios carry percentile bootstrap intervals". §7 (07:10) and fix_a7.json
compute CroMa flow ratios as exp(log r ± t·se) with Welch df. The bootstrap applies only to the open-geometry
throughput ratios (E8/E9).

File paper/sections/03_model.tex
```old
Jaccard indices, mean log rate ratios, paired differences and flow ratios carry percentile bootstrap intervals over snapshots, seeds or runs, and CroMa means Student-$t$ intervals.
```
```new
Jaccard indices, mean log rate ratios, paired differences and open-geometry throughput ratios carry percentile bootstrap intervals over snapshots, seeds or runs, and CroMa means and flow ratios Student-$t$ intervals (ratios on the log scale).
```

**C3. Weibull statements.** §5.2 says "exceeds 1 only when pooled". The same paragraph reports the lag-fit pinned
shape from 10 s, 1.09 [1.01, 1.17], which is above 1. Fixed by W1. Table 2 ("T: exponential times") and the
pair-standoff "not exponential (2.3, 2.8)" are consistent with the data.

**C4. Completion counts.** §6.3 says "larger ensembles … agree with them", while Table 4 row 10 marks C1 0/25
revised. Fixed by I8.

**C5. Table 4 "lone wall-law trap (393/393)" against §5.1** (386 positive margin, 7 pair standoffs). Fixed by I11.

**C6. Critical width.** §9, §6.3 and Table 4 say "default wall law" and §1 does not. Fixed by I6. The value 0.88 m
is the same everywhere.

**No contradiction found:**
- Arch lifetime: §5.4 "2.9 s" (Δt = 0.01 s) and "3.3 s" (Δt = 0.0025 s), with §1 and §9 quoting the maximum 3.3 s.
- J: §4, §6.1, §6.2 and §8 all say J separates only at the pair. Lone and whole-run J are close to the noise–noise
  reference, and Table 3's whole-run J 0.41 [0.32, 0.50] (0.30) equals N2's E6a–E6b.
- Class definitions in §4 (P, L, T, D, N) and their use in §4.1, §6 and §8.
- Counts quoted twice: 393 = TermN = CriterionN; 34 = EtwoNLK = RunNOneSnapN; 46 everywhere; 25 arch runs; 186
  seeds; 56 library barriers in §5.3 and §6.2.

**Note:** §4 (04:28) quotes field residuals "over the 60 barrier … snapshots" (field_residuals.json lone/collective
n = 60). §5.3 and §6.2 quote "56 library barriers" (E6 barrier_picture.n_barriers). These are different sets, but
the reader is not told why 60 vs 56. A clause naming the 4 snapshots without a usable barrier would remove the
apparent mismatch.

---

## 4. Convention defects

- **p-values:** all 12 p macros in the text and tables use fmt `p`. Values ≥ 0.01 print plain with 3 decimals (0.016,
  0.906, 0.632, 0.011). Values below print in scientific notation (3.5×10⁻⁴¹, 2.0×10⁻¹³, 2.3×10⁻⁴, 2.3×10⁻³,
  1.1×10⁻³, 1.2×10⁻⁴, 8.7×10⁻⁷, 4.0×10⁻⁴). There are no literal p-values. **No defect.**
- **Intervals [lo, hi], 95%:** every CI is bracketed as [lo, hi], and the 95% intervals checked match their sources.
  Defects:
  1. §6.1 unlabelled 95%-of-splits range in brackets (I9).
  2. §6.3 unlabelled ± SD (I10).
  3. §3 names the wrong interval methods for σ₅₀ and CroMa flow ratios (C1, C2).
  4. Table 3, RVO2 pair J "[0, 0.24]": the upper bound is an exact Clopper–Pearson bound
     (fix_a1.json pair.rvo2.J_upper95_cp), not the percentile bootstrap §3 names for Jaccard indices. Fix below.
  5. Table 4 row 16 prints the conference's "[0.54, 1.83]" ratio interval. It is withdrawn and quoted as printed, so
     it is not a defect, but its level is not stated.

File experiments/tables/make_table3.py
```old
(pair: freed; expected if independent in parentheses)
```
```new
(pair: freed; for disjoint sets the exact 95\% upper bound; expected if independent in parentheses)
```
