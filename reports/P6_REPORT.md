# P6 report: C5 numbers into the paper, scope fixes and the page budget

Base: origin/main at 03cde2b (P5), which contains 1997560 (C5). Draft: `/Users/palaash/Desktop/LNNS_P6_draft.pdf`.

Build: 28 pages; 0 errors, 0 undefined references, 0 BibTeX warnings and 0 overfull boxes.
Abstract: 249 words (`tools/count_abstract_words.py`).
Checks:
- `check_number_consistency.py`: 0 numbers not found.
- `check_dropped_numbers.py d504d64`: 1 known drop.
- `check_dropped_numbers.py 03cde2b --paper`: 14 drops, each justified in Sect. 6 below.

New files:
- `tools/build_p6_numbers.py` reads stored outputs only (rev7_*.json, run records, earlier derived files) and writes `data/derived/p6_numbers.json`.
- `paper/registry/p6.yaml` holds 162 macros with the prefix Rz, of which 159 are printed.
- `paper/tables/table4_runsets.tex` is the run-set table.

The C5 headline file is `data/derived/rev7_headline.json`; the builder reads its task files (rev7_T1, T2, T4, T5, T10, rev7_whole) directly.

## 1. Status per edit item

| Item | Status | Sections touched |
|---|---|---|
| 1 Alone Arrhenius slope | Done. The headline is 0.946 [0.935, 0.961] over 56 snapshots; the three-snapshot value 0.89 [0.83, 0.95] is kept as the first fit. ν/ν_Langer is 0.82 (0.34–1.2); Weibull shapes are 1.1 (0.68–2.2, 112 cells). | Abstract, 1, 5.2, 7.5, 11 |
| 2 Rate-theory identification | Done. λ_TST gives 0.92, Θ does not depend on β (0.92) and Φ gives 0.89, against a measured 0.92 [0.88, 0.95] on the same 10 snapshots of the Arrhenius set. The full-turnover claims are removed. The sub-unity slope is attributed to the prefactor of the anharmonic well, not to friction. | 5.2, 1, 11 |
| 3 Time-step probe | Done. Saddle 2.2 (was 2.4), with predicted 2.2 [1.8, 2.7] at β₀ = 1.5. At 2.5: saddle 3.70, observed 3.23 [2.96, 3.52], span × 0.946 = 3.50 at the upper edge, and 3.29 with 0.89. Pooled ℓ 1.6 [1.0, 2.3] against 2.0. | 7.1 (Matched noise) |
| 4 Pair standoffs at 600 s | Done. Freed counts with Wilson intervals: legacy 21 [0.32, 0.60], RVO2 7 [0.076, 0.28], drive part 33 [0.57, 0.83], constraint part 44 [0.85, 0.99], SFM 0 [0, 0.077]. McNemar legacy vs RVO2 14:0, p = 1.2×10⁻⁴. Counts are final; members move at most 6 cm between 120 and 600 s. The constraint part is framed plainly (44 against 33). "Velocity filter frees none" is scoped to "frees no saved deadlock". | 7.3, 7.4, 1, abstract |
| 5 R1/R2 | Done. New paragraph "Replacing the Drive": 0 of 27 complete for each, 54 still moving, against 12 for force-coupled ORCA (RVO2), McNemar 0:12, p = 4.9×10⁻⁴. At the lone keystones R1 frees 1 of 34, the one the criterion predicts. | 7.1, 1, abstract |
| 6 Throttled drive part | Done. The drive part completes 134/186 [0.65, 0.78]. Against the drive part 26:18, p = 0.29; against SFM with τ′ 17:18, p = 1.0; against RVO2 48:15, p < 10⁻⁴. Failures: 25 lone, 27 second, 0 collective. The target-speed ratio is 0.690 (0.655–0.718); "same model" is removed. Replay floor: 23 (drive), 26 (τ′), 41 (RVO2) and 2 (SFM) of 186 outcomes change; completion counts move by at most 7. | 3.2, 7.2, 11 |
| 7 Run-set table and sample size | Done. Table 2 (`tab:runsets`) has 12 data rows. The 186-seed formula has z = 2.927, p = 0.575, δ = 0.15. The "another 100" seeds are named as 242–341. 24 of 34 lone keystones are vacuous (only the blocker left). Lone-keystone seed 97; jamb seeds 57 and 122 (9 two-agent and 2 three-agent standoffs). | 3.4, 5.1, table |
| 8 Noise-floor wording | Done. Seed 60 is skipped because its barrier, 0.021 J, falls below the threshold; seed 401 (0.057 J) is kept with no threshold claim; "−22 J below" is fixed. | 5.2, 5.3 |
| 9 Split sample | Done. Held-out error: lone −0.0064 [−0.18, 0.16]; whole −0.0059 [−0.12, 0.12]. | 7.1, 7.2 |
| 10a Force-coupled ORCA scope | Done. "Force-coupled" is used throughout. Native ORCA is "not tested in this coupling", with a limitations sentence. | 3.2, 9 |
| 10b Failure to reject | Done. "Equality not rejected" replaces equivalence claims except under TOST. Sect. 6 adds "The margin was fixed in the study plan before any quench was run" (plan/FINAL_PLAN.md, 2026-11-07, before E2 on 2026-11-08). No C5 prediction is called pre-registered. | 1, 6, 7 |
| 10c Removed words | Done. "iff" becomes "stays at rest when … and is driven through otherwise", with a sentence that the criterion is not a capture condition. "exact" and "transition-state value" are removed. | 5.1, 5.2 |
| 10d "at most 0.40–0.60" | Done: "the variants pass 0.40–0.60". | Abstract, 1, 8 |
| 10e Two significant figures; "−22 J below" | Done. β and ℓ are printed at two significant figures (RzStep*, RzScaled*); "\RzMiscSeventyBelow J below" now prints 22. | 5, 7 |
| 10f Friction factor | Done. 2.25 at the largest overlap and 1.18 at 0.005 s. 2.28 (h rounded to 0.038 m) is not printed (see open item 6). | 8 |
| 11 Symbol renames | Done (Sect. 4 below). | 5.2 |
| 12 Page budget | Done: 28 pages, with the cuts listed in Sect. 5. | many |

## 2. Numbers added or changed (all from `paper/registry/p6.yaml`)

| Quantity | Value | Macro |
|---|---|---|
| Alone slope ratio, 56 snapshots | 0.946 [0.935, 0.961] | RzTtwoRatio, RzTtwoLo, RzTtwoHi |
| Quenches; escapes | 5600; 5088 | RzTtwoRestarts, RzTtwoEvents |
| Intervals covering 1 / the theory | 44 / 52 of 56 | RzTtwoCoverone, RzTtwoCoverTheory |
| Measured slope, Arrhenius set | 0.92 [0.88, 0.95] | RzTtwoEfourRatio/Lo/Hi |
| λ_TST; ΘλTST; ΦΘλTST slope | 0.92; 0.92; 0.89 | RzTthreeTst, RzTthreeTheta, RzTthreeFull |
| ν/ν_Langer | 0.82 (0.34–1.2) | RzTtwoNuLangerMed/Min/Max |
| 1/(τω_b) | 0.41 | RzTtwoGammaOmegaMed |
| Weibull shape | 1.1 (0.68–2.2), 112 cells | RzTtwoWeibullMed/Min/Max/Cells |
| Time-step β₀ = 1.5: saddle, scaled, observed | 2.2, 2.2, 2.2 [1.8, 2.7] | RzTfourOnepfiveA/C/Obs/Lo/Hi |
| Time-step β₀ = 2.5: saddle, scaled, scaled with 0.89, observed | 3.70, 3.50, 3.29, 3.23 [2.96, 3.52] | RzTfourTwopfiveA/C/Cthree/Obs/Lo/Hi |
| Pooled ℓ; predicted | 1.6 [1.0, 2.3]; 2.0 | RzStepEll/Lo/Hi, RzStepPred |
| Scaled ℓ; predicted | −0.076 [−0.24, 0.11]; −0.023 | RzScaledEll/Lo/Hi, RzScaledPred |
| β span per Δt | 0.18–2.5, 0.37–5.0, 0.73–9.9 | RzStepBeta{Half,One,Two}{Min,Max} |
| Pair freed counts at 600 s (of 50) | 21, 7, 33, 44, 0 | RzTone{Legacy,Rvo,Drive,Cons,Sfm}Freed |
| Wilson intervals | as in item 4 | RzTone*Lo/Hi |
| Pair McNemar | 14:0, 1.2×10⁻⁴ | RzToneLegRvoA/B/P |
| Pair displacement 120→600 s | ≤ 6 cm | RzToneDispMax |
| Split-sample error | as in item 9 | RzTfiveHeldout*, RzTfiveWhole* |
| Replay floor | 23/26/41/2 of 186; max shift 7 | RzTseven* |
| Throttled drive part | as in item 6 | RzTeight* |
| Target-speed ratio | 0.690 (0.655–0.718), τ 0.5, ρ 2.3 | RzGRatio/Lo/Hi, RzGTau, RzGRho |
| Criterion vs replacing drive | lone 1/34 (ORCA 30); screening 1/60 disagree; other 9/134 disagree, 12 freed vs 5 predicted, 8 held→freed (3, 3 at 2–4 N, 2) | RzTonezero* |
| R1/R2 whole runs | 0/27, ≤ 0.12, 54 moving, RVO2 12, seeds 242–268 | RzToneone* |
| Sample size | z 2.927, p 0.575, δ 0.15 | RzBZ, RzBP, RzBDelta |
| Vacuous lone keystones | 24 of 34 | RzDLoneOnly, RzDLoneN |
| Wall cell seeds | 97; jamb 57, 122; 9 two, 2 three, of 11 | RzH* |
| Barrier seeds | 60 (skipped), 401 (smallest pair) | RzCSkipSeed, RzCPairMinSeed |
| Adjacent rest state | 22 J below | RzMiscSeventyBelow |
| Friction factor | 2.25; 1.18 | RzMiscFrictionOne, RzMiscFrictionHalf |
| Run-set table | 34 seed bounds and sizes | RzSet* |

## 3. Claims weakened, scoped or removed

1. The full-turnover / friction explanation of the sub-unity slope is removed; the slope is now attributed to the prefactor of the anharmonic well.
2. "Same model" (drive part vs SFM with τ′) is removed; they now "have the form of the social-force drive", with target-speed ratio 0.690.
3. "iff" in the stuck-alone criterion becomes a one-way statement, plus "not a capture condition".
4. "exact" and "transition-state value" are removed.
5. Equivalence wording becomes failure to reject (noise σ*: "completes 99 runs against 101, equality not rejected"; Intro "could not reject equal completion").
6. ORCA results are scoped to force-coupled ORCA; native ORCA is untested (limitation).
7. "Velocity filter frees nothing" becomes "frees no saved deadlock".
8. The pair result is scoped to 600 s counts, which are final; the legacy-solver surplus vanishes in RVO2 (defect flag).
9. "At most 0.40–0.60" becomes "pass 0.40–0.60".
10. The stall-lifetime prediction is stated as an extrapolation below β = 1.5; the sentence "extends the law to barriers that noise crosses by fluctuations" is removed.
11. The Discussion "Mechanisms" paragraph (extra cut E1) is removed. Its RMST lead of the push (ΔRMST) is no longer printed in the Discussion; Sect. 7.1 keeps the time-to-free comparison.

## 4. Symbol mapping

| Old | New | Meaning |
|---|---|---|
| κ (Kramers) | Θ | Kramers' transmission factor |
| A (Mel'nikov–Meshkov) | Φ | depopulation factor |
| k_TST | λ_TST | transition-state rate of the anharmonic well |
| γ/ω_b | 1/(τω_b) | avoids a clash with the Weidmann γ |
| macro RzTthreeKappa (C5) | RzTthreeTheta | |

The existing RvAtwoKappa* registry entries were not renamed. They are not printed (`grep` finds no use in the sections).

## 5. Pages and cuts

End: 28 pages.

Prescribed cuts, in order:

1. The lone-keystone figure (Fig. 6, quench) and its reference are removed.
2. The unapplied A3 items applied:
   - C2: the 42–141 sentence is replaced by a table reference.
   - C4: Jacobian numbers.
   - C5: TOST p-values.
   - C6: the temperature-weighting sentence (factors 0.91–…) becomes one sentence on the unstable mode.
   - C7: legacy jitter / creep.
   - C8: bias split ranges.
   - C14: the six-radii list.
   - C15: SFM overlap sentence; arches compressed.
3. The longest explanatory sentence in Sect. 7.5 (constraint part) is cut to one clause.

After these the paper was still 30 pages. The cuts below go **beyond the prescribed list**; each is reversible.

- E1: Discussion "Mechanisms" paragraph deleted (it restated Sect. 7.5).
- E2: Intro paragraph on the conference study tightened (same content, fewer words); the second-trap clause of contribution 2 removed (it is in Sect. 7.1).
- E3: Sect. 3.4 keystone definition shortened to one sentence that points to Sect. 1.
- E4: Sect. 7.5 determinism sentence merged into one.
- E5: Screening-set legacy-solver counts removed (equality not rejected; the deadlock-set counts are kept). Screening-set second-trap freed counts are removed from the prose (they stay in Table 3).
- E6: Contact Arches subsection (5.4) folded into one sentence in the Sect. 5 introduction. The label `sec:arches` is gone; nothing referenced it.
- E7: Recommendations list set inline as (i)–(vi).
- E8: Protocol figure (Fig. 5, `fig:protocol`) removed. It is a diagram, not data; the text describes the protocol in full.
- E9: About 30 word-level trims to free near-empty last lines (no content change), for example "(blended to B_w by 1.0 m)" and "crosses x = 10 m".
- E10: The reversed-bias discordance (legacy, +b* vs −b*) and the "rounding at r_c = 0.1 m removed all N" clause in the Intro were removed; the latter is still in Sect. 5.3 and the Recommendations.
- E11: The TTC sentence in Sect. 7.2 was merged.

Final page map: references 3.3 pp; Sect. 7 5.8; Sect. 3 4.6; Sect. 5 ≈3.9.

## 6. Dropped numbers (`check_dropped_numbers.py 03cde2b --paper`)

The tool now skips deleted tables that are absent at REF. It also gains a `--paper` mode that checks every number macro used in the paper sources at REF.

| Macro (value at 03cde2b) | Reason |
|---|---|
| RwThreeStepEll 1.62, …EllHi 2.33, …Pred 2.03, …BetaHalfMax 2.50, …BetaOneMax 4.99, …BetaTwoMax 9.89 | Edit 10e: replaced by RzStep* at two significant figures (1.6, 2.3, 2.0, 2.5, 5.0, 9.9) |
| PfiveEllBBLo 3.0 | Edit 3: time-step values at 2.5 replaced by RzTfourTwopfive* (2.96) |
| RevBthreeDUShallow 5.8 | Edit 1: three-depth slope listing replaced by the 56-snapshot fit |
| PairPubRvoPRel < 10⁻³ | Edit 4: replaced by the 600 s McNemar 1.2×10⁻⁴ (RzToneLegRvoP) |
| PscrCreepSpeedMin 0.091, RevAthirteenCreepSpeedMax 0.14, RevAthirteenCreepDriftMin −0.14 | Cut C7 (legacy jitter) |
| RvAsevenCMin 0.91 | Cut C6 (temperature-weighting factors) |
| RvAtwelveRoomMax 0.62 | Cut C15 (overlap macros) |

`check_dropped_numbers.py d504d64` still reports PairPubRvoPRel from the old table 3, for the same reason.

## 7. Untraced numbers

None. Every literal digit added this session is one of:
- a design parameter: widths 0.70–1.00 and 0.8 m; B_w 0.04 and 0.08 m; Δt 0.0025–0.02 s; σ 0.07; β levels 1.5–7; horizons 120, 300, 600 and 900 s; room coordinates;
- a confidence level (90 %, 95 %);
- a citation year.

The abstract holds only the design parameters 0.08, 0.8, 0.04 and 1.5.

## 8. Disagreements between the prompt and the data (the paper follows the data)

1. The prompt says the prefactor "falls as temperature falls". In rev7_T3 it rises (ν_TST(1.5)/ν_TST(7) = 0.47–0.92), and the paper says it rises.
2. The prompt calls 0.82 (0.34–1.15) "Weibull shapes"; it is ν/ν_Langer. The Weibull shapes are 1.1 (0.68–2.2). Both are printed, labelled correctly. At two significant figures 1.15 prints as 1.2.
3. The held-out error is a freed/completed-fraction difference, not m/s.
4. The whole-run held-out lower bound is −0.1247, which prints as −0.12, not −0.13.
5. The RVO2 Wilson lower bound prints as 0.076 (two significant figures), not 0.08.
6. 2.28 comes from h rounded to 0.038 m; the stored value is 2.25 at h = 0.0375 m.

## 9. Open items (with defaults)

1. Extra cuts E1–E11 go beyond the prescribed list. Default: keep them. Reverting E8 (protocol figure) costs about 0.4 page and E6 (arches) about 0.2.
2. ΔRMST of the push at the lone keystone was dropped from the Discussion with E1. Default: not restored (Sect. 7.1 carries the time comparison).
3. Intro sentence "could not reject equal completion for noise tuned to the same completion fraction". Default: keep; the author may prefer "equality was not rejected".
4. The two unexplained cases among the 8 predicted-held but freed second traps are printed as "2 unexplained". Default: keep as stated.
5. RvAtwoKappa* registry names still carry κ (they are not printed). Default: leave.
6. The friction factor 2.28 was not checked against a recomputed overlap. Default: print 2.25 only.
7. The Holm 1979 OPEN pointer, the Merkin pointer and the three \pending placeholders are untouched. Default: unchanged.

## 10. Framework needs

1. Native (non-force-coupled) ORCA is untested in this coupling. It would need a coupling switch in deadlock-screen if a reviewer asks.
2. Add `p6_numbers.json` fields to the framework's headline export (rev8) so that `tools/build_p6_numbers.py` can retire. It currently reads raw JSONL for the pair displacement (E7b, T1), the seed sets and the E7 cells.
3. The friction factor at the recomputed h (item 9.6).

## HANDOFF

- Repository `/Users/palaash/Developer/lnns-pedestrian`, branch main; P6 pushed on top of 03cde2b.
- Worktree `/Users/palaash/Developer/lnns-wt/P6` (branch wt-P6).
- Paper: 28 pages; abstract 249 words; build clean; consistency 0 not found.
- Registry `paper/registry/p6.yaml` (prefix Rz) from `data/derived/p6_numbers.json`, built by `tools/build_p6_numbers.py`. Regenerate with `.venv/bin/python tools/build_p6_numbers.py && make numbers paper`.
- `tools/check_dropped_numbers.py REF --paper` checks every macro used at REF.
- The page budget has no slack: any addition needs an equal cut. Next candidates are Related Work (1.0 page) and the Sect. 7.1 second-trap paragraph.
- Untouched: the Holm 1979 OPEN pointer (Sect. 4.4), the Merkin pointer, and the three \pending placeholders.
