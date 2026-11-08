# F2 report: analyses, §5–§10, Table 3 (fix wave, 2026-11-09)

## Analyses (scripts experiments/fixan/fix_*.py → data/derived/fix_*.json; macros in core/pair/e6_e10/e7.yaml)
- **A-1 identity references.** Lone trap: J(noise, ORCA) 0.20 [0.00, 0.70] (two-level bootstrap); noise vs noise on 2-vs-3 seed splits 0.25 [0.14, 0.50], same halves vs ORCA 0.25; independence 0.05. ORCA's unresolved snapshots are hard for noise too (10/20 runs freed there vs 138/150 elsewhere; AUC 0.90 [0.78, 1.00]). R1 predictor test: ΔU predicts ORCA failure (AUC 1.00) as well as the margin (0.98); no separation. Whole runs: J 0.41 [0.32, 0.50] vs independence 0.30 [0.24, 0.37], p = 0.002; noise-vs-noise needs run-N2. Pair: published J 0.43 vs independence 0.31 (p = 0.07); RVO2 J = 0 [0, 0.24] vs 0.09. ⇒ J separates only at the pair (deterministic, self-J = 1).
- **A-2 split sample (200 halvings).** Lone σ = 0.07 re-chosen in 0.995 of splits, Δ −0.01 (95% of splits in [−0.09, 0.07]). Pair b*: Δ +0.00 [−0.35, 0.35] (published), +0.01 [−0.22, 0.26] (RVO2) — as wide as a control that only copies ORCA's rate [−0.30, 0.30]. Whole runs Δ −0.01 [−0.16, 0.13].
- **A-3 activated escape.** Free-intercept collapse slope −0.93 [−0.98, −0.88] (excludes −1; not circular); Weibull 1.09 → lag fit preferred (t0 0.66 s, ΔAIC −19), shape 1.03 [0.98, 1.07] from 2 s, pinned 1.09 [1.01, 1.17]; fitted ν at 0.69 (median) of the inertial Langer prefactor, below it in 25/28; participation ratio of the unstable mode 1.2 (blocker 0.92), neighbours carry 0.25 of the path displacement. Counts: E3 OLS 0.72 [0.29, 1.06], 23% censored; gate 4/60; E3 20/36, E4 10/32; pair ΔU/kT < 1 at every level 7/12.
- **A-4 published solver.** No jump at 1e-9 m (≤ 4e-8 m/s over 38 creep states). Flips = smooth amplification (0.7–1.3 /s) until 1.7e-5–2.7e-4 m, then a half-plane switch (leg-normal sign flip in 4/5) with a 0.43–1.05 m/s jump; 0/16 events drop an infeasible constraint; RVO2 replays do not diverge.
- **A-5 criterion.** 386/386 positive-margin blockers held; 7 margins within ±10 N; the 7 negatives are all pair standoffs (6 two-agent, one with two bystanders); lateral stiffness median 1738 N/m vs axial 898.
- **A-6 statistics.** Snapshot-cluster interval for σ = 0.07, 148/170: [0.79, 0.94] (Wilson [0.81, 0.91]); McNemar/Δ unchanged; within-seed class test p = 1.1e-3; fold agreement 41/46 snapshots at all 8 biases; E5 per-run data present; seed-resampled σ50 [0.040, 0.049] / [0.041, 0.049] — conference 0.049 now at the upper edge.
- **A-7 CroMa.** Log-ratio flow intervals: C1 0.51 [0.43, 0.61], C3 0.59 [0.49, 0.70], σ* 0.40 [0.33, 0.48]; 10–90% window C1 0.85 vs 1.49 ped/s; human max gap 2.04 s, 1 gap > 2 s; Wilson 1/25 ≤ 0.20; 4D040's unpassed track is a lost track; motivation h0/h1/h2 per run.
- **A-8 critical width.** 2[r + B_w ln(2A_w/F)] fails (0.97 vs exact 0.75 m); median agent held alone below 0.75 m, no agent stuck alone above 0.92 m; 0.88 m lies between.

## Items done
REG-1, 2, 3, 4, 7, 9, 10 (REG-5 via A-3); 05-1…05-9 (lower member = member below the axis, `experiments/E7b` y < 5); 06-1…06-9 (06-5: new §6.2 Whole Runs, label sec:att-whole); T3-1 items 1–6 (overfull 0 pt; ℓ in its own time-step block; J with independence expectation; RVO2 pair J = 0 [0, 0.24]); 07-1…07-6; 08-1…08-7 incl. D10 checklist and "Applying the protocol", D11 scoping; 09-1; 10-1; captions of Figs 2–8 (05-8, 06-7, 07-5).

## Deferred
REG-6 (TeffHarmonicCorr, §4 is F1's); REG-8 thousands separator (needs a make_numbers format); 10-3 and data statement (inside the credits environment, F1/WP-REPO); 06-10 (S3); fig tick labels "frozen ±" → "push ±" (FIG-2, captions already say rest-drive push).

## Pages (tools/page_map.py --pinned)
§5 4.68 (budget 3.5) · §6 5.31 incl. S3's §6.3 + Table 4 (4.5) · §7 1.81 (2.0) · §8 1.33 (1.0) · §9 0.43 (0.4) · back matter 0.56 · total 26.60 pinned (cap 25; F1 alone left 26.13). Words: §5 2100→1990, §6 (own) 1122→1310, §7 807→753, §8 560→640, §9 197→210. Over budget: §5 (+1.2, the snapshot already stood at 4.8) and §8 (+0.3, checklist + applying the protocol, D10).

## Provisional run-dependent sentences (\pending marks the number)
- N1 (§6.1): "Identity does not separate the two here … [after run-N1: σ from a logistic inversion with 20 seeds per snapshot, and J between two independent noise sets]".
- N2 (§6.2): "As at the lone trap, identity does not separate them; time to completion and the final state do. [after run-N2: J between two independent noise streams]".
- N5 (§5.4): "… every run completes, at the tested time step Δt = 0.01 s [after the resolution run: unchanged at Δt = 0.0025 s and at the default drive]".
- N6 (§5.3): threshold written "lost at b_f" (no "fold") [after the continuation run: whether μ₁ reaches zero at b_f as a saddle-node fold].
- N3 (equal temperature, §5.2): no sentence depends on it yet; the full-condition temperature set from the blocker's τ is stated.

## Changelog entries proposed
- Cxx §5 reordered (D9b): lone trap → noise as collective activated escape → pair standoff at the jamb faces → arches; labels unchanged; D7 sentence in §5.4 and §8.
- Cxx Whole runs are §6.2 (D9a); identity is a separating signature only at the pair (D3a), with same-resolver and independence references from A-1.
- Cxx Rate matches stated as calibrations, with split-sample results (A-2); "not used in the calibration" (K3).
- Cxx Class N for the published solver rests on A-4: smooth amplification ending in a half-plane switch, no dropped constraints; "ill-conditioning" wording retired.
- Cxx §5.2 activated-escape claims qualified with A-3 (collapse slope, lag, Langer); σ50 intervals by seed resampling (A-6).
- Cxx Table 3: Control column, ℓ in a time-step block (K5), J with independence expectation, `\tabcolsep` 1.5 pt, two-sentence caption.
- Cxx §7 log-ratio flow intervals, 10–90% window, motivation conditions, human-gap wording (A-7, NC M3/L10/L11).

## [NEEDS PALAASH]
- Length: see Pages; the real build also strands Tables 1, 2, 4 at the end (Table 1 [t] does not fit), which adds ~1 pp until F1's float placement is fixed.
- A-2: the pair b* rate match is no better than chance out of sample; the text says so. Confirm this framing.
- A-4 replaces "ill-conditioning / infeasible constraints dropped"; §4/Table 2 class N wording (F1) should match.
- A-1: R1's ΔU-vs-margin predictor test does not separate either; it is not used.
- Bib (F1): CroMa entry year 2026 → 2021; consider Boomers et al. 2023 for the CroMa analysis.
- §6.3 (S3) still uses "arm" ("seeds per arm", "in any arm").
