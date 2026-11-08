# B5A report: the pair class (E7b)

Library: 46 corrected-forward pair standoffs, B_w = 0.04 m. Data: data/E7b/ (queue outputs and C26 traces) and data/E7b_bstar/ (fold thresholds, b* fit, held-out runs). Analysis: experiments/E7b/analyze.py → data/derived/E7b_analysis.json.

## Statics (S9a, S9b)
- Strict minimum in 46/46. λ1 = 65–121 N/m (median 94); the softest mode is the common lateral shift in 46/46 (lateral weight ≈ 1). λ2 (opposed lateral) is 866–1569 N/m, 12–14× λ1. Field residual max |F_code + ∇U| = 1.4e-7 N (median 3.9e-8).
- Geometry: |y − 5| = 0.40–0.50 m; surface gap 0.28–0.33 m (no contact); wall gap ≈ 0.10 m.
- Fold thresholds (bisection of the static relaxation to 1e-4, both signs, 0 undecided, monotone in every case): b*₊ median 0.023, b*₋ median 0.025, easier sign 0.0005–0.038 (median 0.016). |b*₊ − b*₋| follows the axis-distance asymmetry (Spearman 0.9996).
- Fold prediction vs 120 s quench: 363/368 (Wilson lower bound 0.969 ≥ 0.90, so S9a is met). All 5 misses are quenches that free 1–2 % below the static threshold (FP 0, FN 5).
- S9b: 1e-9 m replays 0/230; δ = 1 mm 0/46; δ = 1 cm 1/46 (upper bound 0.113 > 0.10, marginal; pooled 1 mm + 1 cm 1/92 passes); δ = 3 cm 10/46.

## Quench per arm (unperturbed, freed / 46) and decomposition
- C1 0, C2 0; C3 published 21, C3 RVO2 7; drive only 33; constraint only 45 (published LP) / 44 (RVO2); frozen + 34, − 1; bias ±0.01: 8/7, ±0.02: 17/18, ±0.03: 32/30, 0.05: 44, 0.1: 46.
- Replays: every deterministic arm, including both ORCA solvers and the b* arms, keeps its outcome in all 5520 replays (0 discordant). Times are exact except for the published LP: C3 published first-exit times shift by up to 24.3 s and constraint-only published by 0.01 s, i.e. the C20 ill-conditioning without outcome flips at the pair.
- S9c: C3 published vs RVO2 14:0, p = 1.2e-4, so pair-class ORCA claims are per solver.
- S9d: constraint only vs C1 45:0 / 44:0, so the constraint part acts at the pair. Drive only vs C3 RVO2 28:2 (p = 8.7e-7): the two parts work against each other.
- S9e handedness: the bias-favoured member exits first in 202/202 freed bias runs; the first member flips between +b and −b wherever both sides free. ORCA lower-first: published 11/21, RVO2 2/7 (no handedness).
- Noise: freed 224/230 at σ = 0.01, 230/230 at 0.02–0.05. Rate 0.043 / 0.10 / 0.13 / 0.18 s⁻¹. Weibull k = 2.3–2.8 (not exponential); seed-discordant snapshots 2 at σ = 0.01.
- Barriers (S9f): 12/12 snapshots gated (3 of 24 channels failed the 62→124 resolution test). ΔU = 0.06–1.1 J (median 0.21 J); no relation to λ1 (Spearman −0.24). ΔU/k_BT_eff < 1 at most levels, so the Arrhenius ratio scatters (median 1.3, IQR 0.74–2.1). Not a valid test; reported descriptively.

## Matched bias b* (S9g)
- Plan §9 names both matches (RVO2 for forward claims, published as in A6), so both were run. b* is the midpoint of the b-interval on which the static fold curve frees exactly the ORCA count: b*_pub = 0.0223 (interval 0.0220–0.0227), b*_RVO2 = 0.0091 (0.00902–0.00910).
- Held-out, 46 × (u + 5 × 1e-9 m) at ±b*:
  - Rate: bias +b*_pub 22 vs C3 published 21 (9:8, p = 1.0); +b*_RVO2 8 vs C3 RVO2 7 (8:7, p = 1.0). Paired TOST ±0.10 is **not** met (90 % CI −0.11 to 0.17; n = 46 too small).
  - Identity: published match freed-set Jaccard 0.43 [0.26, 0.61] (13 of 30), unresolved-set Jaccard 0.48 [0.31, 0.65]. The RVO2 match and C3 RVO2 free **disjoint** sets (0 of 15).
  - Handedness: +b*_pub frees the lower member first 22/22 (p = 4.8e-7); −b*_pub frees the upper member first 21/21; C3 published 11/21 (p = 1.0). Where both free, the same member exits first 10/13.
  - Reversal: −b*_pub frees 21 (rate symmetric), but a different set (13:14).
  - Replay: exact for both, so this probe does not separate them. Time to free: KM medians not reached (< 50 % freed); paired Δt median +1.0 s (n = 13).
- **Verdict:** matched on rate (p = 1.0, equivalence not shown at n = 46), the bias is separated from ORCA on identity, handedness and constraint dependence, as the thesis predicts.

## C26 link
All 10 one-neighbour second-trap snapshots have the pair geometry: neighbour on the other side of the axis 10/10, abreast (Δx median −4 mm), surface gap 0.27–0.32 m (pair library 0.28–0.33). Over 20 s of C3 RVO2, the constraint part cancels a median 0.27 of the door-ward drive at the second trap (held) vs 0.26 in held pair standoffs; it is 100 % from the partner's half-plane and ≤ 6 N at t = 0. C3 RVO2 frees 2/10 vs 7/46 (Fisher p = 0.66).

## Fig 7, pages, build
- Fig 7 (full width, 5.0 cm): fonts embedded, smallest text 6.97 pt, thinnest line 0.40 pt; colour, greyscale and CVD previews viewed; no legend or text. b* labels use a text-size star.
- Pages (pinned page map, clean worktree): §5.2 ≈ 0.87 (budget 0.9); §6.2 ≈ 1.07 with Fig 7 (budget 1.0, **0.07 over**). overlap_check: 0 runs ≥ 8 words.
- `make numbers`, `make paper` and `make submission` pass on the committed state in a clean worktree (19 pp, 0 undefined). The shared working tree currently fails only on 5B's uncommitted §5.3/§7 macros (\Arch*, \Eten*).

## [NEEDS PALAASH: T5 sign-off]
- [ ] Hessian of U, density frozen (experiments/lib/pairlib.py:46-98 PairField, hess h = 1e-4; experiments/E7b/e7b_static.py:51-64): positive definite 46/46; λ1 65–121, λ2 866–1569 N/m; softest mode = common lateral shift 46/46.
- [ ] U terms vs code: drive c_i|x − g| with Weidmann v_eff (code/sim/steering/desired.py:16, 53-55); pair exp + body (code/sim/steering/sfm.py:99); wall exp at B_w = 0.04 (code/sim/steering/walls.py:174-183); bias tilt (code/sim/steering/hybrid.py:92-95, 138-142).
- [ ] Field residual max 1.4e-7 N over 46 (data/derived/field_residuals.json, pair).
- [ ] Fold reading: static relaxation (pairlib.py:113, freed x > 10.3 m, held |F| < 0.05 N) agrees 363/368; bisected thresholds in data/E7b_bstar/fold_threshold.jsonl; the misses are all just below threshold.
- [ ] Evidence: data/E7b/e7b_static.jsonl, e7b_quench.jsonl, e7b_barrier.jsonl; data/derived/E7b_analysis.json (a_statics).

## Proposed changelog text (for 5C)
- C44 Pair-class matched bias: per plan §9, b*_pub = 0.0223 (C3 published) and b*_RVO2 = 0.0091 (C3 RVO2), fitted on rate from the bisected static fold thresholds (the b grid was too coarse) and tested held-out at ±b* (data/E7b_bstar). Matched on rate (22 vs 21, 8 vs 7; equivalence ±0.10 not shown at n = 46); separated on identity (Jaccard 0.43; RVO2 sets disjoint) and handedness (22/22 vs 11/21).
- C45 Pair-class deviations: S9b δ = 1 cm upper bound 0.113 (pooled 1 mm + 1 cm passes); S9f Arrhenius not testable (ΔU/k_BT_eff < 1, Weibull k 2.3–2.8), so noise at the pair is reported descriptively, not as class T.
- C46 C26 confirmed with E7b: same geometry and the same constraint cancellation (0.27 vs 0.26); a blocker with one trapped neighbour is a pair standoff.

## Surprises (proposals)
- Proposal: C3 RVO2 and its rate-matched bias free disjoint sets; this could replace the Jaccard as the headline identity number.
- Proposal: the fold-threshold splitting follows the axis asymmetry almost exactly (0.9996); one sentence in §5.2 now, a candidate T5 corollary.
- Note: my first commit (44a7998) also carried another session's staged registry rename (harmless). The pair commit was amended before push to drop 5B's §5.3/§6.1 hunks swept in from the shared tree.
