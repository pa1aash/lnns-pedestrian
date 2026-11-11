# C report: revision evidence (Parts A, B, D)

Registry: paper/registry/revision.yaml, 1875 macros from experiments/revision/notes/*.yaml (one file per item; prefix
RevA<n>, RevB<n>, RevD). Sources data/derived/rev_*.json. Full notes, interpretation and every draft sentence with
macros: experiments/revision/notes/<item>.md. `make paper` passes. **CLAIM** marks a change to a paper claim or number.

## Part A: analyses of existing data

- **A1 Identity (RevAone).** At rest with no binding constraint, F_des + F_drive is the SFM with τ' = ττ_orca/(τ+τ_orca), exact to 1.7e-13 N. Quenched with τ', the SFM frees exactly the drive part's 30/34 lone keystones and 24/26 second traps (discordant 0:0); τ' = 0.22–0.27 s, drive 1.8–2.2× the SFM's. *Draft:* "At rest force-coupled ORCA's drive part is the SFM with relaxation time τ' = \RevAoneTauPrimeLo–\RevAoneTauPrimeHi s."
- **A2 Density gate (RevAtwo).** w_o never below \RevAtwoRunsWMin in whole runs, 1 at all snapshots: the gate is inactive in every result. *Draft:* "The gate is inactive in all results." No claim change.
- **A3 β at matched noise (RevAthree).** At σ = 0.07 m/s the median β = ΔU/k_BT_eff is 0.64; 23 of 56 barriers have β < 1. **CLAIM** Heat at the matched level is not Kramers-regime; Sect. 6.2's stall prediction extrapolates below β = 1.5.
- **A4 Slope-ratio trend (RevAfour).** Pooled: no trend. Alone: ratio falls with ΔU (b = −0.16 [−0.26, −0.07]). B3 shows this is a low-β effect at the deepest barrier (see B3). **CLAIM** superseded by B3.
- **A5 Selection (RevAfive).** Rules re-derived and reproduced (below). The 26 second traps are a PCG64(2026) draw from all 160; balanced on 13 covariates. Omissions only: E3's ΔU ≥ 3 J and gate acceptance are not stated.
- **A5x 134 more second traps (RevAfiveX).** Pooled 160: drive part vs ORCA (RVO2) 28:0, p < 10^-8 (E2 alone 7:0, would fail Holm); no arm differs between E2's 26 and the 134 (Holm p = 1). Class assignment holds. **CLAIM** "SFM frees none" and "5 of 300 replays" are E2-only: SFM frees 2/134 (creeping snapshots), legacy flips 13/800. Noise separates from ORCA on freed fraction (+0.13, Holm < 10^-4) and replays (34:0). *Draft:* "On all \RevAfiveXPoolN second traps, ORCA's drive part frees \RevAfiveXPoolDriveFreed blockers and force-coupled ORCA (RVO2) \RevAfiveXPoolOrcaFreed."
- **A6 Second-trap row (RevAsix).** **CLAIM** σ = 0.07 is not fraction-matched at the second trap: Δ = +0.25 [0.08, 0.44].
- **A7 Paired tests (RevAseven).** Table below. **CLAIM** Protocol step 5 changes to paired tests with Holm; time to free separates the push from ORCA, so class is decided by the Table 2 probes only.
- **A8 Horizon (RevAeight).** **CLAIM** Matches hold only within a window of horizons: lone keystone σ = 0.07 from 70 s, σ = 0.0717 from 85 s, whole runs from 425 s. "Fraction-matched at T" must name T.
- **A9 Overlap J (RevAnine).** **CLAIM** Table 3's lone J = 0.20 is a 5-seed value; with 20 seeds J = 0.75 against 0.06 for independent sets (hypergeometric p = 6.7e-4).
- **A10 Hessian (RevAten).** All lone-trap snapshots are strict minima (positive definite). Supports Prop. 1 as applied.
- **A11 ORCA constraint at rest (RevAeleven).** **CLAIM** The constraint part binds at rest at 92/92 pair members, is lateral and away from the partner (0.19–0.35 of the drive), and makes the rest field non-gradient (asymmetry 0.08–0.10). Sects. 3.2, 4.3 (Prop. part ii), 6.1.4, 6.4.1 change; 13 of 28 drive-frees/RVO2-holds standoffs follow from the rest field, 15 are dynamic.
- **A12 CroMa table and gaps (RevAtwelve).** Per-run table drafted; open final gaps treated as right-censored. Superseded numerically by Part D.
- **A13 Text facts (RevAthirteen).** **CLAIM** each: ninth stuck-alone decile 0.31 omitted; legacy-replay "slow creep" is jitter at 0.09–0.14 m/s with net drift −0.14 to +3.3 mm/s; 108 kN and 22.2 kN are sums over contacts (single contact 67 kN, overlap 0.24 m); k_ttc in N s²; N(μ, σ) uses the SD, v0 and r clipped. Facts: g_max(0.30) = 291 N; median stack 2; drive/g_max(mean r) = 1.4; 207 settings = 120 E3 + 87 E4; ℓ uses Δt 0.005/0.02; "Lower" = y < 5 m; the lag is the earliest escape (fitted); 0.9996 is Spearman of axis-distance vs threshold differences.
- **A14 Legacy solver (RevAfourteen).** Identified below.
- **A15 Thresholds (RevAfifteen).** 37 thresholds checked, no mismatch. **CLAIM** (wording) every held ORCA standoff is still moving at 120 s, so ORCA pair results are freed fractions at T = 120 s; escape event x ≥ 10 m and the 300/900 s censoring must be stated.

**Snapshot selection rules (A5).** 200 E1b runs (w = 0.8 m, seeds 42–241) → 196 deadlocks → keystone test (SFM restart,
σ = 0, 120 s): lone keystone = blocker alone held and all others exit with the blocker removed (34); second trap =
blocker alone held, someone held with it removed (160); group standoff (2). E2 = all 34 + 26 of 160 by
Generator(PCG64(2026)).choice. Barrier gate rejects 4 second traps → 56. E3: gate-accepted and ΔU ≥ 3 J (36), ranks
round(linspace(0, 35, 20)) by (ΔU, seed). E4: gate-accepted and n_resid ≥ 2 incl. the blocker (32), ranks
round(linspace(0, 31, 10)). Pair barriers: 12 of 46 at ranks round(linspace(0, 45, 12)) of μ1.

**A7 decision-rule table** (notes/A7_table.tex; sign-flip / McNemar, Holm within comparison; sep. = Holm p < 0.05):

| Comparison vs ORCA (RVO2) | freed fraction | replay changes | time to free (RMST) | other |
|---|---|---|---|---|
| lone, σ = 0.07 (5 seeds) | −0.01, p 0.90, no | 9:0, p_H 0.008, **yes** | +19 s, p_H 0.002, yes | ℓ +2.7, **yes** |
| lone, σ = 0.0717 (20 seeds) | −0.02, p_H 1, no | 14:0, p_H < 10^-3, **yes** | +19 s, yes | identity, no |
| second trap, σ = 0.07 | +0.25, p_H 0.062, no | 5:0, p_H 0.13, no | −16 s, no | (A5x pooled: yes, yes) |
| whole runs, σ* | −0.01, no | — | +72 s, yes | final-state class, yes |
| pair: bias b*_legacy vs ORCA legacy | +0.02, no | 0:0, no | −2 s, no | identity 17:0, handedness, yes |

Defining probes (replay changes, ℓ) separate noise from ORCA at the lone keystone; freed fraction does not. Time to free
is empirical, not class-defining.

**Legacy solver identification (A14).** pedestrian-abs sim/steering/orca.py:113 `normal = safe_normalize(u)` in the leg
branch of `_halfplane_normal` (sign defect relative to RVO2's linearProgram, port code/sim/steering/orca_rvo2.py:64-67).
Introduced in commit c43af16 (2026-04-02); conference blob 71bb509, commits 9762177 .. e05d8f6, tag r2.0-baseline. All
conference C3/C4 results used it; this worktree's orca.py lines 1–255 are byte-identical.

## Part B: new runs

- **B1 Converse of stuck-alone (RevBone).** Negative margin 400/400 pass; positive 0/200. Criterion exact both ways to 0.01 N. Supports the claim. *Draft:* "...so Eq. (stuck) is necessary and sufficient."
- **B2 Critical width (RevBtwo).** w50 = 0.878 [0.874, 0.883] m (1100 runs, 11 widths). **CLAIM** N = 100 prediction (0.919 m) refuted by 0.041 m; arrival-record N_eff = 3.7 gives 0.816 m; only the fitted N_best = 19 matches. Held agents arrived with ≤ 9 others active, none touching. Bracket 0.75 < w50 < 0.92 stands; \FixAeightWfiftyPred is an upper bound, not a prediction. *Draft:* "Half the runs complete at w50 = \RevBtwoWfifty m, \RevBtwoPredHundredOffset m below the width at which none of the 100 agents is stuck alone, because the crowd pushes stuck-alone agents through."
- **B3 High-β Arrhenius (RevBthree).** β = 5–7, 180 restarts, ≥ 14 escapes per level. Ratio over β 1.5–7: 0.91 [0.81, 1.00], 0.93 [0.83, 1.03], 0.86 [0.76, 0.95] (ΔU 5.8, 21, 56 J). **CLAIM** A4's decline comes from the β = 1.5–2.5 step at 56 J; the slope is 0.86–0.93 of the string barrier at every depth, not 1. Escape times at 56 J are over-dispersed (Weibull 0.64–0.68).
- **B4 Arch Δt (RevBfour).** Δt 0.0025 and 0.001 agree: summed compression ≤ 18 kN, single contact ≤ 4.8 kN, overlap ≤ 4 cm, lifetime ≤ 2.4 s, none persistent, 10/10 complete. Δt = 0.01 under-resolved (75 kN, 26 cm). **CLAIM** ArchPeakForce (108 kN) and the Δt = 0.01 arch set (ArchEpisodes, ArchPNinetyFive, ArchEvacMedian) go; the Δt = 0.0025 set becomes the headline. "No arch persists" stands.
- **B5 Rounded jamb ends (RevBfive).** Static: 0/46 pair minima survive r_c = 0.1 m. Generation at r_c = 0.1 m: 0/320 pair and 0 collective deadlocks (sharp 46, 57; p < 10^-13); completion 319 vs 256. **CLAIM** the pair standoff needs square jamb corners; Sect. 5.1's "rounded corners leave the trap in place" holds only for lone traps. Barrier as work along the unstable-manifold path (non-gradient field), unchanged recommendation.
- **B6 Line goal (RevBsix).** Statics: 46/46 minima kept. Generation: pair standoffs 91 vs 46 of 320 (McNemar p < 10^-4), completion 213 vs 256. **CLAIM** (strengthens) the standoff is not a point-goal artefact; add to Sect. 5.1.

## Review claims: supported / refuted by the evidence

Supported (paper must change): matched noise is outside the Kramers regime (A3); fraction match is horizon-specific
(A8); second-trap noise not matched (A6, A5x); ORCA constraint acts at rest, Prop. (ii) does not cover ORCA at the pair
(A11); arch forces under-resolved (A13, B4); Arrhenius slope below 1 (B3); parameter-free width prediction fails (B2);
pair standoff depends on corner geometry (B5); CroMa agent counts and censoring (D). Refuted: gate matters (A2);
snapshot sample is biased (A5, A5x); minima not strict (A10); stuck-alone criterion only sufficient (B1); standoff is a
point-goal artefact (B6); thresholds mis-transcribed (A15).

## CPU time

Run outputs (sum of per-job wall time): 63 CPU-h. B3 42 (contended machine, 10.6 h wall), B2 5.6, D3 4.8, A5x 3.3, B6 2.7,
B5 2.3, B4 1.0, B1 0.45, A2 0.37; analyses ~1.5 CPU-h. Queue wall 15.7 h (17:05–08:45). Lost and rerun: first B4 (0.2 h).

## Part D: CroMa integrity (RevD, RevDThree)

D1 (participants / tracks / passed): 4D030 161/135/135, 4D040 160/136/135, 4D110 132/131/129, 4D120 132/129/129,
4D130 129/128/128. The archive N counts registered participants; the difference to tracks is people not recorded.
Track excess: one duplicate ID in 4D040, two in 4D110 (merged). Every recorded participant passes. E10 used track counts
(+1, +2) and l = 0.21 m (documented 0.2 m). D3 reran 100 runs (4.8 CPU-h) with passed counts and 0.2 m; paired by seed
no variant's flow changes (all CI cover 0). Changed numbers (**every row flagged**; full table notes/D_changes.md):

| quantity | old → new | macro |
|---|---|---|
| human flow | 1.48 [1.22, 1.74] → 1.47 [1.21, 1.73] | RevDHumanFlow |
| human flow 0.2 m / window | 1.58 → 1.57 / 1.49 → 1.48 | RevDShortHumanFlow / RevDHumanWindowFlow |
| SFM complete/deadlock; Wilson hi | 1/24 → 2/23; 0.20 → 0.25 | RevDThreeCOneComplete, …CompleteHi |
| SFM flow; ratio; window flow | 0.75 → 0.73; 0.51 [0.43, 0.61] → 0.50 [0.42, 0.59]; 0.85 → 0.83 | RevDThreeCOneFlow, …FlowRatio |
| B_w,edge complete/deadlock; ratio | 17/8 → 21/4; 0.57 → 0.56 [0.47, 0.67] | RevDThreeCEdge… |
| SFM+ORCA complete/deadlock/capped | 10/0/15 → 10/1/14 ("never deadlocks" false) | RevDThreeCThree… |
| SFM+ORCA flow; ratio | 0.87 → 0.88; 0.59 [0.49, 0.70] → 0.60 [0.50, 0.71] | RevDThreeCThreeFlowRatio |
| noise σ* complete (capped); ratio | 14 (11) → 18 (7); 0.40 [0.33, 0.48] unchanged | RevDThreeCSig… |
| **range of flow ratios** | 0.40–0.59 → **0.40–0.60** | RevDThreeRatioMin/Max |
| gaps > 2 s per run; mean longest gap | 11–19 → 10–18; 5.7–6.6 → 5.3–8.0 s; noise 72.2 → 71.5 s | RevDThree*GapsTwo, *Gap |
| fluctuation; 0.2 m model flow | 0.094–0.109 → 0.092–0.108; 0.62–0.91 → 0.62–0.92 | RevDThree*Fluct, *ShortFlow |
| censored runs (SFM, edge, ORCA, noise) | 24, 8, 15, 11 → 23, 4, 15, 7 | RevDThree*Cens |
| longest gap, completed runs (max) | 6.8, 10.5, 11.0, 269 → 20.4, 15.6, 7.6, 237 s | RevDThree*GapCompleteMax |
| KM median gap edge/noise; median c SFM/ORCA | 6.5/95.9 → 6.1/95.9 s; 16/433 → 416/432 s | RevDThree*GapKMMedian, *GapLowerMedian |

D4: the open final gap is right-censored at 600 s; KM median not reached for SFM and SFM+ORCA, so quote the lower bound.
*Draft:* "With as many agents as participants passed the entrance and a 0.2 m bottleneck, the model passes
\RevDThreeRatioMin–\RevDThreeRatioMax of the human flow; the SFM deadlocks in \RevDThreeCOneDeadlock of 25 runs."
