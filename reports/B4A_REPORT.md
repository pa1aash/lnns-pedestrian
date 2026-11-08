# Batch 4A report (2026-11-08)

Commits: 846d74e changelog C19-C22, C24, C25 · 1291916 E3/E4/E5b outputs (all < 50 MB, not gzipped; E5a not committed) ·
09fba8c E3 + Fig 5 + T3 check · 8882e54 E4 + Fig 4 · e5df403 E5b · 746d36d second trap · 92d2f5f registry (+77 macros, 244 total), Table 3 signature rows (still not \input), Fig 4/5 environments.

## E3: Δt signature, per-step noise is thermal with the predicted T_eff
- Per-step ℓ = ln λ̂(0.005)/λ̂(0.02): 2.16 [1.80, 2.70] vs predicted 2.22 at β_ref 1.5; 3.23 [2.96, 3.52] vs 3.70 at β_ref 2.5.
  Slope of observed on predicted through the origin 0.91 [0.83, 1.01]; per-snapshot CIs cover the prediction in 16/20 (OLS with intercept: 0.72 [0.29, 1.06], poorly constrained with two clusters of predicted values).
- √Δt-scaled noise: ℓ = −0.09 [−0.22, 0.05] (predicted −0.03). C3 RVO2: ln t(0.02)/t(0.005) = −0.005 (max |·| 0.018), 16 freed, 4 held at every Δt.
- Censoring: per-step 1.5 / 4.8 / 23.3 % at Δt 0.005 / 0.01 / 0.02 (900 s cap at 0.02); √Δt-scaled 5-7 %.
- Pooled Weibull k (per-step) 0.96 [0.89, 1.04], 1.05 [0.97, 1.13], 1.08 [0.98, 1.18] by Δt: exponential, Poisson escape.
- Verdict: class T signature confirmed (ℓ follows T_eff; vanishes when T_eff is held fixed; deterministic C3 shows none), with a 13 % shortfall at β_ref 2.5.

## E4: noise is activated escape over the computed barriers
- Escapes: full 382, frozen 581, alone 554 (all ≥ 105 at 20 restarts). Pooled Weibull k = 1.09 [1.05, 1.14] (full 1.05, frozen 1.14, alone 1.07).
- Arrhenius slope / −ΔU_cond, median: full 1.15 (CI covers 1 in 7/8 fits), frozen 0.95 (9/10), alone 0.87 (9/10). Barrier collapse slope −0.93 over 84 points.
- Collective saddle: the full barrier lies below the alone barrier in 10/10 snapshots, median ratio 0.30 (0.003-0.66).
- Prefactors ν̂ (slope fixed at −ΔU): medians 0.13 (full), 0.21 (frozen), 0.09 (alone) s⁻¹.
- Verdict: escape is Arrhenius over the condition's own barrier; the residual neighbours lower it (collective escape).

## E5b: σ50 in corrected-forward mode
Completion 2/100 (σ = 0, E1b seeds 42-141), 27, 41, 61, 76, 86 /100 at σ = 0.03-0.07 m/s. Logistic σ50 = 0.044 [0.041, 0.047] m/s
(profile CI; deviance 0.15 on 3 dof). Conference value 0.049 (published mode, n = 25) lies just above the CI; the like-for-like check is E5a (running).

## Second trap (C21): ORCA's half-plane against an abreast trapped neighbour
- At restart (t = 0) the constraint part on the blocker is ≈ 0 in both strata (|F_x| ≤ 1.2 N vs a 115-212 N door-ward drive; RVO2 = published LP).
- It builds up as the pair starts moving: 20 s C3 traces at the second trap. Held runs (9/9): time-mean door-ward constraint −49 N, peak −138 N (≈ the whole drive),
  mean cancellation 27 %. All of it comes from the trapped neighbours' half-planes, and the binding neighbour is abreast (Δx = −0.10 to +0.08 m, 8/9 slightly ahead).
  Freed runs: constraint 0 in 13/17 (neighbour behind, Δx −0.14 to −0.75 m); transient in seed187/209, ≤ 15 N in seed73/186.
- Geometry decides it: C3 RVO2 frees 2/10 snapshots with one trapped neighbour vs 15/16 with ≥ 2 (Fisher p = 2.3e-4).
- Time to free at the second trap: drive only KM median 1.4 s (24/26), C3 RVO2 1.9 s (17/26), C3 published 3.7 s (22/26). Where both free,
  C3 RVO2 is slower in 17/17 (median +0.25 s) although the blocker's own constraint is 0 there: the delay acts through the neighbour's ORCA.

## Figure QA (tools/qa_figs.py, PNGs viewed incl. greyscale)
- Fig 5 (half width): fonts embedded, min text 6.97 pt, min line 0.50 pt. Fig 4 (full width): fonts embedded, min text 5.98 pt (sub/superscripts in the axis labels), min line 0.60 pt.
- No legends, titles, text or letters; reference lines only (y = 1; slope −1). `make paper` clean, 5 pp. LaTeX numbers them 3 and 4 until Fig 3 exists.

## [NEEDS PALAASH] T3 sign-off checklist
- [ ] Formula k_BT_eff = m σ²/(1 − (1 − Δt/τ)²) (experiments/lib/teff.py:11-13); √Δt scaling code/sim/core/simulation.py:184-189.
- [ ] Fixed order (code/sim/core/simulation.py:193-205): v ← clamp(v + FΔt/m), + noise, re-clamp, then x ← x + vΔt (noise before the position update).
  Exact harmonic identity: ⟨v²⟩ = 2σ²/((1−a)(2+2a−ω²Δt²)), a = 1 − Δt/τ; configurational K⟨x²⟩ = mσ²(1+a)/((1−a)(2+2a−ω²Δt²)) = (1 − Δt/2τ)× kinetic.
- [ ] Published order (simulation.py:206-224; Euler in code/sim/core/integrator.py:19-43): x from the pre-noise velocity, clamp, then noise;
  ⟨v²⟩ = σ²(2 − (1−a)ω²Δt²)/((1−a)(2+2a−ω²Δt²)). Both reduce to the formula as ωΔt → 0.
- [ ] Measured (experiments/E3/t3_variance.py, 3 snapshots × 3 Δt, 60 s, 1 worker): realised/formula 1.00 on average (0.87-1.10; sampling error ≈ 13 %);
  ωΔt ≤ 0.10, harmonic correction ≤ 0.3 %. Stored moments of all 207 E3/E4 cells: median 0.99, IQR 0.98-1.01.

## [NEEDS PALAASH] T4 sign-off checklist
- [ ] Conservative rest field with density frozen: max |F_code + ∇U| = 2.5e-7 N over the 30 E3/E4 snapshots (4.9e-7 N over all 60; frozen condition 4.1e-8 N).
- [ ] String method with all residual agents mobile (full condition, gate C15a): accepted for all 30 E3/E4 snapshots.
- [ ] Arrhenius slopes against barriers (Step 4): medians 1.15 / 0.95 / 0.87 (full / frozen / alone), CIs cover 1 in 25/28 fits; collapse slope −0.93.

## Surprises (proposals, not applied)
1. P: the β_ref 2.5 shortfall (ℓ 3.23 vs 3.70) is not a T_eff error (variance checks out; the configurational correction moves the prediction up). Likely the low-barrier prefactor at β_eff ≈ 1.25 (Δt 0.005). Test with a β_ref 3.5 E3 arm.
2. P: E1b_seed170 full: the gate accepts ΔU = 0.13 J but 0/60 restarts escape in 300 s; the full-condition minimum-energy path is not reached by the dynamics. Report it with the marginal cases (C18) and keep it out of the collapse (already excluded: no events).
3. P: the second-trap failure is the pair geometry (blocker + one abreast trapped neighbour), linking C21 to the pair class; worth a changelog entry and a sentence in §6.1.
4. P: compare σ50 between modes only once E5a is in; corrected mode needs about 10 % less noise.
