# P3: content, references and clarity revision (A3, C3, C4, B3 applied)

Base: origin/main `d504d64`. Build: `make -o .venv/.requirements-figures.stamp paper`.

## 1. Status per item

### Author decisions

| # | Item | Status |
|---|---|---|
| 1 | A3 Parts 1–6: terminology map, table plan, rewrites, cuts C1–C15 (C15 as three sentences), physics-first order, Part 9 defaults | done; 11 sections (Abstract, 1 Introduction … 11 Conclusions, back matter) |
| 2 | Tables: delete 2 and 3, merge 4 and 5, keep 1 and 6 | done. `make_tables45.py` writes `tables/table2_matched.tex` (Set, Perturbation, Freed, Δ [95%]; 11 rows). Old Tables 2–5 removed with `git rm`. Old Table 6 is now `table3_croma.tex`. Every number of the deleted tables and dropped columns appears in the text: `tools/check_dropped_numbers.py` checks 183 numbers and finds none missing. |
| 3 | Precision: two significant figures through the registry | done; four macros changed (Sect. 2) |
| 4 | Barrier = energy span | done in Sect. 4.2 (definition, 8 of 56), Sect. 5.2 (full median, coverage, pooled slope, an old→new sentence, alone and abstract unchanged, both omission clauses corrected), Sect. 7.1 (β at σ = 0.07) and Sect. 7.2 (β at σ*). Stall prediction: `barrier_picture(sigma, nu)` in E6 reads `gate.jsonl` itself and takes no barrier list, so it was not rerun; the text says it "uses the reported barriers" (open item 2). |
| 5 | Release test | done: 0/200 leave when released at rest at the position of g_max; 127/200 pass [0.57, 0.70] when released from rest 1 m upstream (run-up energy). The 1 m "none leave" claim is deleted. |
| 6 | Relation to [14] | done: three sentences in the Introduction ("reinterpreted"); the counts, the Voronoi density sentence and the TTC counts open Sect. 7.2 |
| 7 | CroMa description | done (Introduction, contribution 5, Sect. 8); not expanded; no placeholder |
| 8 | Whole-run attribution | done: abstract clause (126 of 186 against 101); contribution 2 (126, 135, 101, 2; the constraint part lowers completion); Sect. 7.2 (44:19 p = 0.0022, 44:10 Holm p < 10⁻⁵, all 60 and all 51 failures at rest against 54 of 85 ORCA failures moving, agreement on 151/186). Second-trap sentence (121 vs 149 of 160) in contribution 2. |
| 9 | Legacy solver at second traps | done (Sect. 7.1, "The Legacy Solver"): 160-snapshot set 133 [0.77, 0.88] against 121 for RVO2 (16:4, Holm p = 0.012) and 149 for the drive part (3:19, Holm p = 0.0017); 26-snapshot set 22, 17 and 24 (Holm p = 0.50 and 0.25; "do not differ detectably") |
| 10 | Matched-noise time-step probe | done (Sect. 7.1): per-step ℓ = 1.62 [1.00, 2.33] over 19 of 20 snapshots against the prediction 2.03, with β ranges 0.18–2.50, 0.37–4.99 and 0.73–9.89; √Δt-scaled ℓ = −0.08 [−0.24, 0.11] against −0.02. The earlier 2.2 is stated as measured with σ set per snapshot for β₀ = 1.5 and 2.5. The text says "per-step noise" wherever the time step separates the two (abstract, contribution 3, Sect. 7.1, Sect. 7.5). |
| 11 | CroMa dt check | done (Sect. 8 methods): at 0.005 s (25 runs) every flow ratio lies inside its 0.01 s interval. Noise variant: overlap up to 0.038 m and friction factor 2.3 > 2 in 1 of 25 runs at 0.01 s, at most 1.2 at 0.005 s. The Sect. 3.3 overlap sentence now covers SFM only and points to Sect. 8 (F13). |
| 12 | FLAGS F2, F4, F5, F7, F8, F11, F12, F10 | done (Sect. 4) |
| 13 | Q9, Q10, Q17 | done. Outcome identity (Sect. 4.4) compares how often the two perturbations disagree per snapshot or seed with how often two independent surrogate runs (or replays of the deterministic arm) disagree; definition from `A7_paired.py`. Jacobian asymmetry ‖J−Jᵀ‖_F/‖J‖_F (Sect. 7.3), from `A11_orca_constraint.py jacobian_check`. No new Discussion paragraph. |

### Referee-driven items

| Item | Status |
|---|---|
| a classes | done. Sect. 6.1 gives a taxonomy by the force a perturbation adds at rest, then the probes, then the predicted responses. A paragraph says which responses hold by construction and which are empirical. A composite is classed by its components; Sect. 7.5 classes force-coupled ORCA by its drive and constraint parts. Limitation sentence (Sect. 9): the protocol has never been applied blind to a mechanism of unknown class. |
| b activated escape | done. Sect. 5.2 derives the 0.90 prediction: λ = A κ k_TST of the same potential (exact TST of the tabulated well, Kramers factor, Mel'nikov–Meshkov factor), with the slope fitted using the data's event weights over the same levels. The attempt-frequency deficit (median 0.69 of the damped Langer value, none of 28 fits in range) is in Sect. 5.2 and is named as unexplained in the Conclusions. |
| c stuck-alone | done: Eq. (stuck) is stated for a lone agent at rest; the bracket is "wide"; the independent-agent prediction misses w₅₀ by 0.041 m |
| d pair standoff | done: abstract, contribution 1, Sect. 5.3 (overhang defined) and recommendation (ii) |
| e matching | done. Sect. 6.2: a match is the unadjusted 95% interval covering zero, with Holm p reported separately. Sect. 7.3: "do not differ detectably", b* tuned in sample, equivalence not shown (p = 0.20, 0.18), and the freed fractions are censored because unfreed standoffs still move at 120 s. |
| f CroMa | done: flow ratios are upper bounds; the noise variant's 0 deadlocks follow from its criterion; the human runs mix three motivation levels and two geometries; "all tracked participants pass"; "removing it raises every ratio but leaves each below 1" |
| g smaller points | done. The two horizons are explained as two criteria (Sect. 6.2). "(Glitch)" deleted. RVO2 explained (Sect. 3.2 convention sentence). ROC expanded in Sect. 7.1. PCG64 removed from the prose. β defined in the abstract. Table 1 gains τ_orca, the gate constants, the 2v₀ cap and the deadlock and quench thresholds. "Welch" in Sect. 4.4. The divergence count is reworded ("in 4 of 5 replay pairs the first divergence falls where a leg normal flips sign"). Overhang defined. TTC exerts no force at rest and enters only the reproduction of [14] and a quench that frees nothing. |

### References

| # | Item | Status |
|---|---|---|
| 1 | weidmann1993 title "Fussg{\"a}nger … Fussg{\"a}ngerverkehrs", edition = {2nd} | done (splncs04 does not print `edition` for @techreport: open item 9) |
| 2 | RVO2 | done: the CITATION.cff authors and title are kept; the bib comment states the source and that the title differs from the ICRA paper's |
| 3 | schuirmann1987, royston2013, merkin1996 | `schuirmann1987` was already in refs.bib with identical fields from an earlier fetch, so only `royston2013` (pages {152}) and `merkin1996` were added. Both come from the B3 records: keys renamed, "--" dashes, url, ISSN and month dropped; Merkin's journal field (the series name) kept as `series`. Cited at the TOST (Sect. 6.2), RMST (Sect. 4.4) and Lagrange–Dirichlet (Sect. 4.1) sentences. Holm not added; `% OPEN: Holm 1979, …` placed in Sect. 4.4. |
| 4 | Table 1 TTC row | done via `make_table1.py` (1.5 N s², energy scale of [karamouzas2014] used as a force) |
| 5 | Cornes and Fu rewordings | done (Sect. 2 and Introduction) |
| 6 | Lower-case DOIs | done for fzj_ped20219, vandenberg2011avo, boomers2023data, dergachev2021case and helbing2000freezing |

### Checks before pushing

| Check | Result |
|---|---|
| make numbers | green; 4985 macros; against `d504d64` only the four precision macros change value, 596 added, none removed |
| make paper | 0 errors, 0 undefined references or citations, 0 BibTeX warnings, 0 overfull boxes (underfull only, in the bibliography) |
| pages | **28** (cap 28; target 24–26 **not met**, open item 1) |
| abstract | 248 words (units counted as words) |
| \pending | exactly three printed (Zenodo DOI, Acknowledgments, Disclosure); the Introduction's `\pending` sits in the fallback branch for a missing Fig. 1 caption file and is not printed |
| dropped-number script | `tools/check_dropped_numbers.py`: 183 numbers, none missing |
| defect lint | rhetorical negation, announcements, self-announced significance, softening adverbs, clefts, bare "This", internal labels and American forms: no hits after two fixes ("no longer rejected" reworded; "E1b seed 60/170" replaced by "One"/"The other"). No dash pairs. Sentences with four or more commas are lists of numbers or symbol definitions; the one four-clause sentence (Sect. 5.2) was split. Captions are three sentences or fewer. |
| cross-check | abstract, contributions and conclusions agree on: wall range, overhang 0.26–59 mm, rounding removes all 46, w₅₀, τ′ and drive ratio (contributions, conclusions), 126/186 against 101, velocity filter frees none, slope 0.85–0.93 at β ≥ 1.5 (alone), the defect, and CroMa at most 0.40–0.60 (0.48–0.72 without the throttle) |
| PDF | /Users/palaash/Desktop/LNNS_P3_draft.pdf (LNNS_final.pdf untouched) |

## 2. Changed printed numbers (old → new)

Precision (registry format to two significant figures):

| Macro | Old | New | Where |
|---|---|---|---|
| `EtenHumanGapMax` | 2.04 | 2.0 | Sect. 8 |
| `PphysFoldMissGap` | 1.73 | 1.7 | Sect. 5.3 |
| `PscrStallMaxDiff` | 0.0451 | 0.045 | Sect. 7.2 |
| `RevDThreeCSigFluct` | 0.108 | 0.11 | Sect. 8 |

Energy span (printed macro replaced; the old values remain in one old→new sentence of Sect. 5.2):

| Quantity | Old macro, value | New macro, value |
|---|---|---|
| full-condition median slope ratio | `PphysRatioFull` 1.2 | `PthreeRatioFullSpan` 1.1 |
| full-condition fits whose interval covers 1 | `EfourCoverFull`/`EfourFitsFull` 7/8 | `RxEfourCoverFullSpan`/`RxEfourFitsFullSpan` 7/8 |
| pooled slope | `FixAthreeCollapseSlope` −0.93 [−0.98, −0.88] | `RxPoolSlopeSpan` −0.92 [−0.97, −0.87] |
| β at σ = 0.07, median | `RevAthreeSevenMed` 0.64 | `PthreeBetaSevenSpanMed` 0.74 |
| β at σ = 0.07, quartiles | `RevAthreeSevenQone`/`Qthree` 0.15, 1.6 | `PthreeBetaSevenSpanQone`/`Qthree` 0.28, 1.7 |
| β at σ = 0.07, below 1 | `RevAthreeSevenBelowOneK` 36 of 56 | `RxBetaSevenSpanBelowOne` 35 of 56 |
| β at σ*, median | `RevAthreeStarMed` 1.4 | `PthreeBetaStarSpanMed` 1.7 |
| β at σ*, below 1 | `RevAthreeStarBelowOneK` 23 of 56 | `RxBetaStarSpanBelowOne` 20 of 56 |

New in Sect. 5.2: `PthreeSixtyRep` 0.021 J and `PthreeSixtySpan` 3.4 J (the snapshot below the noise floor); for the 0.13 J snapshot, `PthreeOneSeventyRestE` −22 J, `PthreeOneSeventySpan` 2.8 J and `PthreeOneSeventyBetaExit` 33.

New in Sect. 7.1: ROC exceptions `PthreeRocFreedPos` 2 of `RwSixRocFreed` 30. New in Sect. 8: friction factors `PthreeCroSigFrictionOne` 2.3 (2.25 in the registry source) and `PthreeCroSigFrictionHalf` 1.2 (1.18).

New results (decisions 5, 8–11): the `RwSixf*`, `RwOne*`, `RwTwo*`, `RwThree*` and `RxCroSig*` macros listed in Sect. 1.

Printed numbers removed:
- Release test: "none leave" at 1 m (wrong).
- Cuts C1–C15 (A3 Part 4.2), among them the provenance, which moved to Data and Code Availability (C1), the Δt bias 0.0079–0.0085 (C11), the arch forces 18.3 and 4.85 kN (C15), the six-radius list (C14), the line-goal count (C13) and the per-corridor and normal-motivation CroMa ratios (C12).
- TOST p of the lone keystones and whole runs (C5; the intervals stay). The pair TOST p = 0.20 and 0.18 stay (item e).
- Further cuts made to reach the 28-page cap (beyond C1–C15; open item 1):
  - Sect. 5.1: radius 0.225 m stuck-alone fraction (`RvAoneFracSFMShift*`) and stuck-alone fraction by arrival decile (`RevAthirteenStuck*`).
  - Sect. 7.1: the 20-seed unresolved count (`RevAnineLKNHalfA/B`), the five-seed misclassification (`RevAnineMisclass`) and the SFM creep at second traps (`RevAfiveXPoolSFMFreed`).
  - Sect. 7.3: the out-of-sample split ranges (`RvAsixLegacyErrLo/Hi`, `RvAsixLegacyRefLo/Hi`, `RvAsixRvoErrLo/Hi`); the medians stay.
  - Abstract: τ′ and the drive ratio (still in contribution 2 and the Conclusions), cut to reach 250 words.

## 3. Page counts

Before: 26 (origin/main `d504d64`). After: 28. Page 29 held 16% of a page before the further cuts listed above.

The tables were deleted, but the replacement prose plus the new C3/C4 and referee material (whole-run attribution, legacy solver at second traps, time-step probe, CroMa dt check, span corrections, taxonomy and by-construction paragraph, 0.90 derivation, Table 1 rows) add about 1,800 words. Cuts C1–C15 and the further cuts above remove only part of that.

## 4. A3 FLAG and Part 9 resolutions

| Flag | Resolution |
|---|---|
| F1 | release point stated ("at rest at the position of g_max"); 127/200 [0.57, 0.70] from 1 m upstream added; old claim deleted |
| F2 | "pair standoffs, with 2 members each" |
| F3 | the 0.13 J snapshot is described as a saddle into an adjacent rest state, with its exit barrier. The 56-barrier statistics use the span (8 paths change). The stall prediction does not use the span (open item 2). |
| F4 | "with two exceptions (2 of the 30 freed blockers have a positive margin)", area 0.98 |
| F5 | "though it frees earlier (ΔRMST −4.0 s)" in Sect. 9 |
| F6 | rounded to 0.045; stays descriptive; now says "reported barriers" |
| F7 | "We hypothesise that the crowd pushes stuck-alone agents through" |
| F8 | "consistent with the members' inertia carrying them over, though it does not show it" |
| F9 | count given in the text (4 of 5 replay pairs); abstract says "a sign defect that makes outcomes replay-sensitive" |
| F10 | the pair set is described as built separately |
| F11 | contribution 3: "separate it empirically at the lone keystones and in whole runs" |
| F12 | "which do not differ" (Holm p = 1.0) |
| F13 | the Sect. 3.3 sentence covers SFM only; the noise variant is checked at 0.005 s in Sect. 8 |
| F14 | the claim is restricted to the alone condition everywhere |
| F15 | precision applied through the registry (Sect. 2) |

| Part 9 question | Resolution |
|---|---|
| 1 CroMa | described, not expanded |
| 2 solver convention | "force-coupled ORCA" = RVO2, "(legacy)" marked; convention sentence in Sect. 3.2 |
| 3 matched-noise names | "matched noise (σ = 0.07 m/s)" and "σ*" |
| 4 horizons | TOST horizons kept; the not-rejected horizons are cut (C5); the two criteria are explained (item g) |
| 5 order | 11 sections |
| 6 Fig. 1 caption | A3 wording (the agents are in the left panels, confirmed from the render) |
| 7 arches | three sentences |
| 8 C11 | TST prediction plus the deficit in one sentence |
| 9 undefined terms | final-state class defined in Sect. 4.4; outcome identity defined from the code (not "replays identical") |
| 10 Jacobian asymmetry | ‖J−Jᵀ‖_F/‖J‖_F |
| 11 precision | applied |
| 12 F1 | yes |
| 13 F3 | yes |
| 14 C1 | provenance in Data and Code Availability |
| 15 relation to [14] | three sentences; counts in Sect. 7.2 |
| 16 second traps in contributions | yes |
| 17 Discussion scope | no new paragraph |

## 5. FRAMEWORK NEEDS (deadlock-screen)

1. `barrier_picture(sigma, nu)` (E6 stall prediction) should take the barrier list as an argument so it can be rerun with the energy span.
2. Recompute the E3 time-step prediction with span barriers: `PprotEllBAPred` changes from 2.2 to 2.36 with the span. The paper prints the reported-barrier value.
3. Replot Fig. 5 (escape, `fig_escape_dt.pdf`) with span barriers. It still plots the reported barriers: full median 1.2, against 1.1 in the text.
4. The string method should store both the saddle height and the energy span, and flag paths that pass a deeper rest state.
5. A validity guard per run: maximum overlap and the explicit-friction factor 2κhΔt/m, with a warning above 2.
6. The CroMa flow ratio is an upper bound because flow is counted up to any deadlock. Report it together with the deadlock-censored whole-run flow.
7. Expose the outcome-identity statistic and the Jacobian asymmetry as documented functions; the paper's definitions come from `A7_paired.py` and `A11_orca_constraint.py`.
8. Keep `tools/check_dropped_numbers.py` (or an equivalent) as a gate whenever a table is removed.
9. Classification of a composite perturbation by its components should be an explicit protocol step (Sect. 6.1).

## 6. OPEN ITEMS

1. **Pages.** The paper has 28 pages, at the cap, against the 24–26 target. Reaching 26 needs about 900 more words cut, for example:
   - Sect. 5.4 (arches) in full;
   - the Voronoi and TTC sentences of Sect. 7.2;
   - the out-of-sample medians in Sect. 7.3;
   - the [14] reproduction counts, shortened to one sentence;
   - the time-step-set β₀ sentence in Sect. 7.1;
   - the CroMa diameter/shoulder sentence.

   Should I cut to 26? Default: accept 28 for this draft and choose cuts in the next pass.
2. **Stall prediction with the span.** Refactor `barrier_picture` to take a barrier list and rerun? Default: yes, in the framework; until then the text says "reported barriers".
3. **E3 prediction** (2.2 → 2.36 with the span). Print the span value after recomputation? Default: yes, together with item 2.
4. **Fig. 5 (escape).** Replot with span barriers so the plotted full median matches the text (1.1)? Default: yes.
5. **Holm 1979.** Verify volume, issue and pages on JSTOR 4615733 and add the entry? Default: add after verification; the `% OPEN` comment marks the place.
6. **[14] wording.** B3 notes that [14] already concluded symmetry-breaking rather than velocity-space optimisation. The text says "its reading that noise matches ORCA's velocity selection is reinterpreted here". Check this against the published text of [14]? Default: keep, author to confirm.
7. **Abstract τ′ clause.** It was cut to fit 250 words. Keep it out? Default: yes (it is in contribution 2 and the Conclusions).
8. **Composite class of the constraint part.** Sect. 7.5 classes it as Reshape (a deterministic lateral force at rest; alone it frees 44 of 46 pair standoffs and no lone keystone) without a subtype, because it points away from the partner and has no fixed handedness. Should a subtype be named? Default: no subtype.
9. **Weidmann edition.** splncs04 ignores `edition` for @techreport, so "2nd" is not printed. Switch the entry to @book with the publisher (IVT, ETH Zürich) so it prints? Default: leave as @techreport (series and number identify it).
10. **Further cuts.** The cuts beyond C1–C15 are listed in Sect. 2. Confirm them or restore any? Default: keep.
11. **Discussion limitation wording.** "The protocol has been applied only to perturbations whose class was known from their construction, and never blind to a mechanism of unknown class." Accept? Default: yes.
12. **"by construction" paragraph (Sect. 6.1).** Add "replays of a deterministic perturbation" to the empirical list? Default: no; replay of a deterministic perturbation is identical by construction only for a correct implementation, and the legacy solver shows it is empirical. The paragraph lists "the solver swap" as empirical.

## 7. HANDOFF

**Current state.** All P3 items are applied in `/Users/palaash/Developer/lnns-wt/P3` and pushed to origin main. The paper builds clean at 28 pages; draft PDF at /Users/palaash/Desktop/LNNS_P3_draft.pdf. New files:
- `paper/registry/p3.yaml`, `revision4.yaml` and `revision5.yaml`;
- `paper/sections/06_protocol.tex`;
- `paper/tables/table2_matched.tex`;
- `tools/check_dropped_numbers.py`;
- this report.

Renamed: the section files (`04_methods` … `12_back_matter`) and `table6_croma` → `table3_croma`.

**Decisions made.** Those of Sect. 1 and 4. In addition:
- the further cuts and the abstract trim made to meet the cap;
- the constraint part classed as Reshape;
- the RVO2 source note as a bib comment;
- `schuirmann1987` reused (already present).

**Open.** Sect. 6, items 1–12. The page target and the span-dependent stall/E3/Fig. 5 updates come first.

**Suggested next step.** In the framework, make `barrier_picture` take a barrier list; rerun the stall prediction and the E3 prediction with span barriers; replot Fig. 5. Then make a cut pass to 26 pages from the open-item list and add Holm 1979 once it is verified.
