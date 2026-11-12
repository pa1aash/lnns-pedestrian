FINAL
# C2 report: evidence for revision 3 (Parts A and B)

Registry paper/registry/revision2.yaml (prefix Rv; built by experiments/revision2/build_registry2.py from
notes/C2_items/*.yaml); sources data/derived/rev2_*.json; scripts experiments/revision2/; per-item notes with method,
tables and draft sentences notes/C2_items/<item>.md. Regression hash e381b49dc24acccd OK; make numbers green.
**CLAIM** = a paper claim or number changes. **HEADLINE CHANGE** = a headline number moves.

## Part A: analyses of existing data
- **A1 Radius (RvAone).** Mean radius 0.25 -> 0.225 m (half the CroMa shoulder width 0.45 m, A9): g_max at the mean
  radius 156 -> \RvAoneGmaxShiftExact = 114 N (x \RvAoneGmaxRatio = e^{-0.025/B_w}); stuck-alone fraction SFM 0.23 ->
  \RvAoneFracSFMShift = 0.081, force-coupled ORCA 0.013 -> \RvAoneFracORCAShift = 0.0016. **CLAIM (scope):** a
  stuck-alone fraction or critical width transferred to human body sizes must name the radius.
- **A2 Damping (RvAtwo).** gamma/omega_b median \RvAtwoGamOmegaMed = 0.41 (0.27-2.1): underdamped saddles; KGH kappa
  0.82 is inside the Langer prefactor; energy loss per oscillation 4.5 beta, so turnover needs beta ~ 0.22; the
  Mel'nikov-Meshkov factor is 0.79-1.0 at beta 1.5-3.5 and >= 0.997 at 5-7. Predicted nu/nu_L ~ \RvAtwoAFitMed = 0.97;
  measured \RvAtwoMeasLanger = 0.69 lies outside (\RvAtwoInsideRange of \RvAtwoNFits fits inside). **CLAIM:** 0.69 must
  not be attributed to damping or Kramers turnover; its source is open (anharmonic far wall, finite beta).
- **A3 High-beta Arrhenius (RvAthree).** B3, alone, beta 1.5-7, 360 restarts (39 censored): censored-likelihood pooled
  slope ratio \RvAthreeSlopeRatio = 0.89 [0.83, 0.95]; per snapshot 0.90, 0.93, 0.85 (5.8, 21, 56 J); censored at most
  30% per cell; Weibull shape at beta 6-7: 0.84, 1.0, 0.66 [0.49, 0.87]. Cause: finite barrier. The transition-state
  rate of the same potential (Kramers and energy-diffusion factors, no fit) predicts \RvAthreeTheoryRatio = 0.90; a toy
  on the string potential with the code's update gives \RvAthreeToyRatio = 0.91. The O(dt) configurational-temperature
  error has the wrong sign (+0.008); the speed cap moves the ratio to 0.90 only. **CLAIM:** "effective barrier about
  0.9 of the computed one" (R3) now has its cause: 1 is the beta -> infinity limit.
- **A4 Time-step probe (RvAfour).** Per-step noise set for beta = 1.5 or 2.5 at dt = 0.01 s spans beta
  \RvAfourPerStepMin-\RvAfourPerStepMax = 0.75-5.0 over dt 0.005-0.02 s (sqrt-dt-scaled arm 1.5-2.5). **CLAIM
  (wording, R11):** at dt = 0.005 s every snapshot is below beta 1.5, so that end is "by fluctuations".
- **A5 Equivalence (RvAfive).** Margin +-0.10 = the 95% binomial half-width of force-coupled ORCA's own freed fraction
  on 34-46 snapshots (TOST, 90% cluster-bootstrap interval inside the margin). Equivalent: lone keystone sigma 0.07
  (Delta -0.012, 89-120 s), 0.0717 (-0.018, 86-120 s), whole runs sigma* (-0.011, only 545-600 s). Not equivalent:
  second trap (E2 +0.25; pooled 160 +0.13, window 22-43 s only); pair bias b* (legacy +0.022 [-0.13, 0.17], RVO2
  [-0.11, 0.15]). **CLAIM:** "fraction-matched at T" holds as equivalence only in the windows named; the pair bias is
  "not separated", not "matched"; quote its interval.
- **A6 Split-half b* (RvAsix).** 200 splits of 46: held-out error median +0.044, 95% range [-0.29, 0.30] (legacy),
  +0.043 [-0.19, 0.40] (RVO2); splitting alone gives +-0.30. **CLAIM:** Sect. 6.3's "by construction" must carry the
  out-of-sample error (+-0.3 at 23 standoffs).
- **A7 Mode temperature (RvAseven).** Weight k_BT_eff(tau_i) by the squared components of the unstable eigenvector at
  the saddle: factor 0.91-1.2 (full), 1 exactly (pinned, alone; the blocker carries 0.88-0.97 of the mode). Full median
  slope ratio 1.2 -> \RvAsevenFullMedMode = 1.1, pooled 0.95 unchanged. No claim change.
- **A8 Protocol facts (RvAeight).** Block below. **CLAIM (wording):** the acceptance rule must include the
  climbing-image test and the 2 cm saddle-overlap limit; Table 2 / Fig. 6(c) define l for ORCA as ln t(0.02)/t(0.005)
  of single runs; the second "276" (RevBfiveRuleN) is 46 snapshots x 6 jamb radii; noise-seed integers recur across
  experiments (no paired comparison uses two of them), so the text must not call seeds disjoint. SEEDS.md is stale.
- **A9 CroMa (RvAnine).** Headline ratio = mean run flow over 25 runs / mean of the 5 corrected human flows
  (log-ratio Welch interval); recomputed 0.40-0.60, unchanged. By length: 2.0 m 0.41-0.62 (wide; 2 human runs), 0.2 m
  0.40-0.58. 10-90% flow: no run censored, ratios \RvAnineWindowRatioMin-\RvAnineWindowRatioMax = 0.54-0.64. Motivation:
  4D030, 4D110 normal; 4D040, 4D120 hurry; 4D130 full commitment. Shoulder width 0.45 m (SD 0.04, all 1038
  participants; Boomers et al., Collective Dynamics 8 (2023) A141, p. 7) against the model's 0.50 m mean diameter.
  Ethics: approved by the ethics committee of the University of Wuppertal (January 2020, reference MS/BBL 191213
  Seyfried, p. 34); participants gave written informed consent (p. 5). **CLAIM (framing):** 0.40-0.60 pools three
  motivations (normal-only 0.45-0.68); Sect. 7 should give the 10-90% comparison for all variants.
- **A10 Fixed-noise replay (RvAten).** 34 lone keystones x 5 seeds, sigma 0.07, same noise stream, 1e-9 m displaced:
  0 of 170 outcomes change, all 148 freed blockers exit at the same step; independent seeds change 9 of 34 snapshots
  (0:9, p = 0.0039). **CLAIM (R6 "replay sensitivity"):** for the noise arm the replay attribute measures the change
  of noise stream; at fixed noise a 1e-9 m displacement changes nothing. The probe separates a stochastic perturbation
  from a deterministic one; it does not show chaos in the noise quench.
- **A11 Conference headline (RvAeleven).** w = 0.8 m, 100 agents, 600 s: SFM 3/200 (published flags; 0/25 on seeds
  42-66), 5/300 (CF); SFM+TTC 5/100 (CF); force-coupled ORCA legacy 29/50, RVO2 101/186; full blend 56/100 (CF; with
  published flags not run, 21 CPU-h). C2 = C1 and C4 = C3 seed by seed (McNemar 0.38, 0.87): TTC exerts no force at rest.
  Gap 52 [46, 58] points (CF) against the conference's 54 [39, 67]. The headline reproduces; "categorical" holds to an
  SFM completion below 4%. **CLAIM:** corrections rows A3 (C3) and C4 confirmed.
- **A12 Overlaps (RvAtwelve).** Largest agent overlap, default speed, dt 0.01 s: room 0.62 cm (10 runs; no contact in
  8), CroMa SFM 2.4 cm, force-coupled ORCA 1.9 cm (5 runs each); walls 0.78-2.0 cm. No claim change.

## Part B: new runs
- Code: flag veff_throttle in {on (default), off} in code/sim/steering/hybrid.py (off: v_eff = v0 in the desired force).
  Default bit-identical (hash OK; code/tests/test_veff_throttle.py, 3 passed); pytest 138 passed + 3 new, the 5 known
  cross-platform reference failures unchanged.
- **B1a Width sweep, throttle off (RvBone).** 500 runs, w50 = \RvBoneWfiftyOff = 0.878 [0.872, 0.884] m against 0.878
  [0.874, 0.883] (throttled); completion 0/20/53/86/96 vs 2/15/52/82/96 at 0.80-0.96 m (paired 37:29, p = 0.39).
  No headline change.
- **B1b w = 0.8 m, throttle off.** SFM 1/100 (on 1/100), force-coupled ORCA 53/100 (on 54/100; 17:18 discordant).
  No headline change.
- **B1c CroMa, throttle off. HEADLINE CHANGE.** Flow ratio SFM \RvBoneCroSfmRatio = 0.64 [0.54, 0.76] (on 0.50),
  force-coupled ORCA \RvBoneCroOrcaRatio = 0.72 [0.60, 0.86] (on 0.60); paired off/on x1.28 and x1.21; completions
  unchanged (SFM 1/25, 24 deadlocks; ORCA 12/25); 10-90% window ratio 0.78 and 0.83 (on 0.56, 0.65). In the dense
  waiting zone the 3 m-disc Weidmann factor throttles the whole passage; at the room door only the last agents remain.
  B1d: edge-wall 0.68 (on 0.56), noise sigma* (not refitted) 0.48 (on 0.40). Range over the four Sect. 7 variants
  0.40-0.60 -> \RvBoneCroOffMin-\RvBoneCroOffMax = 0.48-0.72; every variant gains 19-28%. "Fewer people than the
  humans" and the SFM's CroMa deadlock hold either way.
- **B2 Time step (RvBtwo).** dt = 0.005 s, 300 runs: completion 1/56/97 vs 2/52/96 at 0.80/0.88/0.96 m (11:7,
  p = 0.48); w50 shift \RvBtwoShift = -0.003 [-0.009, 0.003] m (three widths, common logistic shape). No claim change.

## Claims that change (for sessions P2 and F3)
1. CroMa flow ratios 0.40-0.60 become 0.48-0.72 without the density throttle (B1c/d, HEADLINE CHANGE); R12 text must say so.
2. Noise replay sensitivity is the noise-seed change (A10); Table 2 and Sect. 4.1 wording under R6.
3. Arrhenius ratio 0.89 explained by the finite barrier (A3); 0.69 Langer ratio not explained by damping (A2).
4. Fraction matches are equivalences within named horizon windows; second-trap noise and pair bias are not (A5, A6).
5. Time-step probe dips below beta 1.5 (A4, R11 wording); CroMa ratio pools motivations (A9); radius scope (A1);
   protocol wording (A8); conference rows A3/C4 confirmed (A11).

## Protocol details (A8; ready to paste; macros in notes/C2_items/A8.md)
Whole runs take one run seed, which fixes the spawn and the per-step noise stream: the lone-trap library uses
seeds \RvAeightEoneLo--\RvAeightEoneHi, the noise sweep and the width runs \RvAeightEfiveLo--\RvAeightEfiveHi,
the matched-completion runs \RvAeightEsixLo--\RvAeightEsixHi (velocity coupling \RvAeightVelLo--\RvAeightVelHi),
the pair library and its line-goal and rounded-end repeats \RvAeightPairLibSeedLo--\RvAeightPairLibSeedHi, and
the open geometries, CroMa and arch runs \RvAeightOpenLo--\RvAeightOpenHi. A restart from a snapshot takes a noise
seed that drives the noise alone. A replay displaces every residual agent by Gaussian noise of standard deviation
\RvAeightReplayDisp\,m with seeds \RvAeightPertLo--\RvAeightPertHi, so a deterministic perturbation has
\RvAeightRunsPerSnap\ runs per snapshot. Of \RvAeightRuns\ runs at $w=\RvAeightWidth$\,m, \RvAeightComplete\
complete and \RvAeightDeadlocks\ end in deadlock: no agent exits while every active speed stays below
\RvAeightDlVthr\,m/s for \RvAeightDlHold\,s (checked every \RvAeightDlCheck\,s, cap \RvAeightDlCap\,s). An SFM
restart of \RvAeightKsWindow\,s classes them as \RvAeightLone\ lone keystones, \RvAeightSecondPool\ second traps
and \RvAeightCollective\ group standoffs; the \RvAeightLibN\ lone-trap snapshots are all lone keystones and
\RvAeightSecond\ second traps drawn without replacement (PCG64, seed \RvAeightDrawSeed). The string has
\RvAeightImgLo, \RvAeightImgMid\ or \RvAeightImgHi\ images, each gradient step moves an agent by at most
\RvAeightStepCap\,mm, and it runs from the relaxed snapshot minimum to an exit state with the blocker at
$x=\RvAeightXExit$\,m. A barrier is accepted when the perpendicular force on the uphill images is below
\RvAeightFTol\,N, the barrier changes by less than \RvAeightDoubleTol\% from \RvAeightImgLo\ to \RvAeightImgMid\
images (else from \RvAeightImgMid\ to \RvAeightImgHi), the climbing image reaches
$|\nabla U|<\RvAeightClimbTol$\,N at the path maximum, no saddle overlap exceeds \RvAeightOverlap\,cm and, alone,
the barrier lies within \RvAeightGridTol\% of a grid path. \RvAeightAccepted\ of \RvAeightLibN\ full barriers pass;
the \RvAeightFailed\ rejected are second traps whose full string fails the doubling or the climbing-image test. The time-step probe takes
\RvAeightEthreeN\ of the \RvAeightEthreeQual\ accepted snapshots with full $\Delta U\ge\RvAeightDUMin$\,J, the
barrier probe \RvAeightEfourN\ of the \RvAeightEfourQual\ with at least two residual agents, both at evenly spaced
ranks in $\Delta U$; the \RvAeightPairBar\ pair barriers sit at evenly spaced ranks of $\mu_1$ among the
\RvAeightPairLib\ pair snapshots. ORCA takes every neighbour within \RvAeightOrcaR\,m, with time horizon
\RvAeightOrcaHorizon\,s and $\tau_{\rm ORCA}=\RvAeightOrcaTau$\,s; walls enter neither solver's constraints and
act through the wall force alone. For force-coupled ORCA the time-step probe is one unperturbed run per snapshot
and $\Delta t$, and $1/t_{\rm esc}$ takes the place of $\lambda$ in Eq.~\eqref{eq:ell}: \RvAeightOrcaFreed\ of
\RvAeightOrcaN\ snapshots escape at every $\Delta t$ and the other \RvAeightOrcaHeld\ at none within
\RvAeightOrcaCens\,s. The velocity filter is tested on \RvAeightLoneRuns\ lone-trap and \RvAeightPairRuns\ pair
quenches per solver, \RvAeightRunsPerSnap\ runs on each of the \RvAeightLibN\ and \RvAeightPairLib\ snapshots.

## CPU time
Runs (sum of per-job times): B1a 5.3, B1b about 3.5 (logged 10.4 includes two power pauses with jobs in flight;
estimate from the throttle-on counterparts), B1c 1.5, B1d 1.2, B2 4.0, A10 0.2, A11 about 4.4 (6.8 logged, one
pause), A12 0.8; analyses about 0.6 (A3 toy 0.3). Total about 22 CPU-h. Queue 11:27-21:58 with about 7 h paused on
battery; nothing lost or rerun.
