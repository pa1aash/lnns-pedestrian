# FINAL PLAN: Springer LNNS extended paper (Plan v1)

**Plan v1: first draft, frozen. Changes only via the dated change log at the end of this file.**

Created 2026-11-02. This file is the single source of truth for the execution phase. It replaces the earlier FINAL_PLAN.md of the same date (kept in git history; see the Reconciliation notes at the end for every change against it).

Conventions:
- Paths are relative to the plan root /Users/palaash/Developer/pedestrian-abs-plan. Simulator code lives in the clone pedestrian-abs/ (branch plan-wave2b).
- "Paper §n" means a section of the paper to be written. "Plan n" means a section of this file.
- Evidence labels: VERIFIED (measured, or exact by construction); INFERRED (reasoned from measurements); UNKNOWN (open).
- Every number carries an evidence file. Pilot protocols (seeds, flags, dt, duration, wall time) are in wave2/WAVE2_REPORT.md and wave2b/WAVE2B_REPORT.md.

Companion documents:
- plan/HANDOFF_EXECUTION.md (self-contained brief for the execution session);
- plan/DECISIONS_OPEN.md;
- plan/CORRECTIONS_TABLE.md (source for paper Table 4);
- plan/DIFFERENCES_POINTS.md (source for the "main differences" statement);
- plan/PLAN_V1_SUMMARY.md (short summary).

---

## 1. Venue frame and requirements

The paper is an invited extended version, for Springer **Lecture Notes in Networks and Systems**, of:

> Gang, P. and Veluri, A. (2026), "A Diagnostic Methodology for Failure-Mode Ablation of SFM, TTC, and ORCA Pedestrian Steering Paradigms", SIMULTECH 2026, pp. 474–481, DOI 10.5220/0015190200004094 (ref/camera_ready_SIMULTECH2026.pdf).

Invitation requirements:
- LNCS template, **fetched from Springer** (never generated or reconstructed);
- the conference paper cited in the text and in the references;
- at least 30% new material (this plan targets well over 70%; see Plan 6);
- every table or figure taken from the conference paper regenerated and citing its source;
- no large verbatim blocks (write from a blank page; declare any recycled methods text);
- a different title, abstract and conclusions;
- a short statement of the main differences (source: plan/DIFFERENCES_POINTS.md);
- submission through PRIMORIS, with the Licence to Publish.

**Length: 23–25 pages INCLUDING references.** This replaces every earlier page target.

Licence note (lit/OUT/VENUE_NOTES.md §6): the conference paper is CC BY-NC-ND 4.0 at SCITEPRESS, so no conference figure is reused or redrawn; every figure is regenerated from new runs.

## 2. Relation to the conference paper

- The paper is about the new work. It builds on the conference paper's audit principle (failure-mode ablation with a matched control), which it cites.
- Where its results revise conference findings, this is stated plainly and compactly in **Table 4** plus **one short paragraph (paper §6.3)**. Revision is not a theme of the paper.
- No correction notice to the proceedings will be pursued.

## 3. Title

**"One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models"**

Alternatives:
- "Drive, Heat or Tilt? How Steering Paradigms Resolve Narrow-Exit Deadlocks"
- "Calibrate, Then Falsify: Mechanism Attribution in Pedestrian Simulation"

## 4. Thesis

Matching a control to a paradigm's headline score is not evidence that the two share a mechanism. Physics-derived held-out signatures decide the question. In two deadlock classes, they show that the same headline score hides different mechanisms.

## 5. Contributions (ranked)

1. **Method: the calibrate-then-falsify protocol.**
   - A claim that a paradigm resolves a deadlock is decomposed into five classes: **P** prevent, **L** reshape (landscape: an added drive changes the fixed points), **T** heat (activated escape), **D** steer (directional symmetry breaking), **N** glitch (numerical or geometric artefact).
   - Matched controls are tested on pre-registered held-out signatures with equivalence statistics (paired TOST, exact McNemar), on a common library of frozen deadlock states.
   - A rest-state lemma excludes terms that vanish at rest (TTC; SFM sliding friction) from any role in resolving a deadlock.
2. **Physics: social-force narrow-exit deadlocks come in two classes.**
   - (a) **Lone-agent trap** set by the wall force at the door edges:
     - stuck-alone criterion g_max(r) > m·v_eff/τ (Plan 8, T2);
     - end-of-queue rule, k = 3: 96.4% agent-level accuracy over 2,318 stuck-alone agents (wave2/data/w21_analysis.json);
     - critical width 0.8–0.9 m: stuck-alone fraction 0.233 at 0.8 m, 0.018 at 0.9 m, 0 at 1.0 m (W2.1, wave2/data/w21_analysis.json); completion 0/25, 18/25, 25/25 at 0.8, 0.9, 1.0 m (W2.5, wave2/data/w25_analysis.json);
     - local to the jambs: jamb-only short range B_w_edge = 0.04 gives 21/25 complete vs 0/25 with published walls (wave2b/data/a2_edge_only.jsonl).
   - (b) **Symmetric pair standoff**: a strict energy minimum (Hessian positive definite in 26/26; wave2b/data/a3_pair_stability.json) that a sideways bias removes through a fold (static prediction 182/182; wave2b/data/a5_predict.json, a5_analysis.json).
   - No persistent contact arches form, because the model has no static friction (W2.9; wave2/data/w29_contact.jsonl).
3. **Attribution.**
   - **Lone trap:** ORCA acts as an extra goal drive (L); noise acts by collective activated escape (T). Δt scaling, seed replay and constant-push (frozen-mean) reversal separate the two despite matched completion (W2.2, W2.3; wave2/data/w22_analysis.json, w23_analysis.json).
   - **Pair class:** the verdicts differ. The bias works through the fold; ORCA's constraint part acts (constraint_only 26/26 vs 0/40 at the lone trap); the published ORCA's pair success depends on its implementation defect (published vs RVO2 ORCA, **10 vs 1 of 26**, 9:0 discordant, exact McNemar p = 0.004; wave2b/data/a5_analysis.json).
4. **Validity.** At 0.8 m in the like-for-like CroMa geometry, real crowds flow without deadlock (5/5 runs, 1.15–1.71 passages/s, longest gap ≤ 2.04 s; wave2/data/w28_croma.json). Every model variant either deadlocks (published and corrected walls 0/10; C3 rvo2 0/5 at 600 s) or flows at about half the human rate with long gaps (jamb-only: 0.72–0.78/s, 0.45–0.68× human, 13–19 gaps > 2 s, longest 6.9–9.9 s; wave2b/data/b2_analysis.json). Practitioner guidance follows on wall treatment at door edges.

## 6. Outline and page budget (about 24 pages including references)

| § | Section | Pages | New vs conference | Evidence / experiments |
|---|---|---|---|---|
| — | Title, abstract | 0.5 | new | — |
| 1 | Introduction: mechanism claims; the conference audit principle [cited]; the single-control pitfall; contributions | 2.0 | mostly new | lit/OUT/FINAL_REPORT.md, NOVELTY_MATRIX.md |
| 2 | Background: SFM, TTC, ORCA; clogging physics (Zuriguel 2014; Nicolas, Garcimartín and Zuriguel 2018; Kramers vs aging); multi-robot deadlock; pattern-oriented modelling and equivalence testing; novelty boundary | 2.0 | new | lit/OUT/NOVELTY_MATRIX.md; references.bib keys zuriguel2014, nicolas2018trap, hanggi1990, cugliandolo1997, grover2020, grover2023, reis2021, grimm2005, grimm2012, schuirmann1987, lakens2017 |
| 3 | Model and scenarios: equations; the two modes; parameter table; geometries (room bottleneck, CroMa, open corridors); deadlock detection; snapshot and quench protocol | 2.5 | condensed and corrected | Plan 7; scan/CODE_FACTS.md; wave2/CODE_CHANGES.md; wave2b/CODE_CHANGES.md |
| 4 | The attribution protocol: five classes; rest-state lemma; matched controls; held-out signatures; pre-registration; TOST and exact McNemar | 2.5 | new | Plan 9 |
| 5 | Deadlock physics: 5.1 lone trap; 5.2 pair standoff (Hessian, fold); 5.3 no contact arches; 5.4 noise as collective escape (T_eff, string barriers, Arrhenius) | 3.5 | new | E1, E4, E7, E7b; Plan 8 |
| 6 | Attribution results: 6.1 lone trap; 6.2 pair class; 6.3 remaining conference claims and Table 4 | 4.0 | new | E2, E3, E5, E6, E7b, E8, E9, E11 |
| 7 | Validity against human data (CroMa like-for-like) | 2.0 | new | E10 |
| 8 | Discussion: generality (robots, agent-based models); practitioner guidance; limitations | 1.5 | new | — |
| 9 | Conclusions | 0.5 | new | — |
| — | References (about 40) | 2.0 | — | lit/OUT/references.bib (fetched entries only) |

- The table sums to 23.0 pages. The remaining ≤ 2 pages of the 23–25 target are slack for the main-differences statement, acknowledgements and data/code availability.
- The pair class is a **secondary strand, about 3 pages** across §5.2 and §6.2.

**Increment check** (INFERRED from the outline): body pages = 23.0 − 0.5 − 2.0 = 20.5. Even if §1, §3 and §6.3 (taken as 1 page) were counted entirely as conference material, that is 5.5 of 20.5 pages (≈ 27%), so new material is ≥ 73%, above the 30% requirement and the "well over 70%" target. Conference quantities that reappear (0/25, 13/25, σ50) are regenerated in new figures or tables whose captions cite [Gang & Veluri 2026].

---

## 7. The model in both modes (paper §3, Table 1)

Both modes share the physics below and differ only in the flags in the mode table. Every flag defaults to published behaviour: regression hash **e381b49dc24acccd** (C1, seed 42, w = 0.8, 100 agents, 500 steps; wave2/scripts/regress.py; scan/probes/common.py:64).

**Agents** (sim/core/agent.py:66, 87-98; config/params.yaml):
- m = 80 kg;
- v0 ~ N(1.34, 0.26) clipped ≥ 0.5 m/s;
- r ~ N(0.25, 0.03) clipped ≥ 0.15 m;
- τ ~ U(0.4, 0.6) s per agent.

**Equation of motion:** m·dv_i/dt = F_i, with
F_i = (1 − w_c,i)·F^des_i + Σ_j F^sfm_ij [+ F^ttc_i] [+ w_o,i·F^orca_i] [+ w_c,i·F^crush_i] + F^wall_i (sim/steering/hybrid.py).

**Desired force** (sim/steering/desired.py:48-60):
- F^des = m(v_eff·ê − v)/τ; ê = unit(g − x); point goal g = (11, 5) (bottleneck.py:43);
- v_eff = v0·clip(1 − exp(−γ(1/max(ρ, 0.01) − 1/ρ_max)), 0.05, 1);
- **Weidmann parameters actually used: γ = 1.913, ρ_max = 5.4** (hybrid.py:128-129; params.yaml has no weidmann keys). The calibrated 0.833 / 5.98 are never applied.

**Density actually used:** ρ_i = #(active neighbours within 3 m)/(9π m²), a fixed-disk count (simulation.py:118-123); quantised in steps of 0.0354 ped/m², maximum ≈ 3.5 at 100 agents; not Voronoi.

**SFM agent–agent** (sfm.py:63-112; neighbours within R = 3 m):
- A·exp((r_ij − d_ij)/B)·n_ij + k·g(r_ij − d_ij)·n_ij + κ·g(r_ij − d_ij)·(Δv_ji·t_ij)·t_ij;
- A = 2000 N, B = 0.08 m, k = 1.2e5 kg/s², κ = 2.4e5 kg/(m s), g(x) = max(0, x).

**Walls** (walls.py): the same law against each segment's closest point: A_w·exp((r_i − d_iw)/B_w)·n + k·g·n − κ·g·(v_i·t)·t.
- Published: A_w = A, B_w = B; the force is **summed over segments**.
- Door edges in the room bottleneck are the end points of the two right-wall segments (sharp, zero thickness; one segment end per edge).
- **Corner rule** (new flag, Plan 7 flag table): where walls share an end point, the corrected mode uses the nearest point on the **union** of those walls, so a shared end is counted once. Pilot evidence: at the CroMa door edge (front wall + corridor wall) the segment sum doubles the maximum backward force on a lone on-axis agent, 311 N (r = 0.25 m) and 582 N (r = 0.30 m), against 156 N and 291 N in the published room (VERIFIED, wave2b/WAVE2B_REPORT.md B2). In the room bottleneck only the outer corners are affected; no residual agent is near them (INFERRED, plan/DECISIONS_OPEN.md D-open-10).
- Wall-law variants: B_w (all walls); B_w_edge (jamb segments within 0.5 m of the door edge, blending to B over 0.5–1.0 m; CroMa corridor ends tagged since commit e75af1f); edge = rounded (capsule jambs, r = 0.1 m).

**TTC** (C2, C4; ttc.py): F = k_ttc·exp(−τ_c/τ0)/τ_c²·n_avoid; k_ttc = 1.5, τ0 = 3 s, τ_max = 8 s. A pair is valid only if |Δv|² ≥ 1e-8 and 0 < τ_c ≤ τ_max, so **F ≡ 0 near v = 0** (ttc.py:91-97).

**ORCA** (C3, C4; orca.py):
- v_pref = v0·ê (not v_eff); speed cap 2·v0; horizon τ_h = 5 s;
- F^orca = m(v_ORCA − v)/τ_ORCA, τ_ORCA = 0.5 s; gate w_o = 1 − σ(ρ; 4.0, 2.0);
- *published*: leg normal sign-flipped outside the VO in the leg region (orca.py:113); infeasible constraints silently skipped (orca.py:178-200; no linearProgram3);
- *RVO2-faithful* (orca = rvo2): orca_rvo2.py, a logic port of RVO2 v2.0.3 Agent.cpp (validated: wave2/data/w20_orca_validate.json).

**Crush** (C4 only, configs.py:11): k_crush = 3.6e5, κ_crush = 4.8e5, gate w_c = σ(ρ; 5.5, 3.0). With the disk density w_c ≤ 0.003, so it is nearly inert (INFERRED from ρ_max ≈ 3.5). **Present and declared in published mode; OFF in corrected mode.**

**Noise** (C1+ε): ε ~ N(0, σ²) per component per step, added to v after integration and re-clamped (simulation.py:174-179). Published: per-step σ. Flags: w2_noise = dt_scaled (σ·√(dt/0.01)), lateral_bias (deterministic tilt ê → (ê + b·ê⊥)/|·|, with w2_bias_b), off.

**Deactivation:** |x − g| < 0.5 m. **dt = 0.01 s.**

**Deadlock detection:** all active |v| < 0.01 m/s for 10 s with no exit (StationaryDetector, wave2/scripts/w2lib.py). Quench arms stop early when stationary (|v| < 1e-3 m/s for 10 s) and are censored at 120 s.

**Snapshot and quench protocol:** a deadlock state is frozen at detection (w2lib.snapshot) and restarted under each arm (w2lib.restore, which re-applies the arm's flags). Arms are compared paired per snapshot.

### Two declared modes

| Item | published-reproduction | corrected-forward |
|---|---|---|
| Integrator | semi-implicit Euler: v' = v + F/m·dt, x' = x + v'·dt, **then** clamp \|v'\| ≤ 2v0; each force component clipped at ±1e6 N (integrator.py:39-41; simulation.py:162-172; helpers.py:23-27) | `w2_numerics=fixed`: v' = clamp(v + F/m·dt) (+ noise, re-clamp), then x' = x + v'·dt; no clip |
| Spawn | uniform in [1, 8] × [1, 9], overlaps allowed (agent.py:87-89) | `spawn=rejection` (non-overlapping; attributes unchanged) |
| ORCA | orca = published | `w2_orca=rvo2` |
| C4 crush term | present (declared) | **OFF** (new flag) |
| Wall corners | segment sum | **union nearest point** (new flag; shared end counted once) |
| Metrics | `w2_metrics=full` for published collision counts | `w2_metrics=light` (dynamics identical) |
| Used for | explaining published numbers; Table 4 | every forward claim |

### Flags

| Flag | Values / effect | Status |
|---|---|---|
| `w2_numerics` | published / fixed | implemented (plan-wave2) |
| `spawn` | uniform / rejection | implemented |
| `w2_orca` | published / rvo2 | implemented |
| `w2_orca_split` | drive_only, constraint_only, frozen_mean | implemented |
| `w2_orca_transform` | reverse_parallel, reverse_lateral (confounded; not pre-registered) | implemented |
| `w2_noise` | dt_scaled, lateral_bias (+ `w2_bias_b`), off | implemented |
| `w2_goal` | line | implemented |
| `A_w`, `B_w` | all walls | implemented |
| `B_w_edge` | jambs only | implemented (plan-wave2b, 3b71581; CroMa tagging e75af1f) |
| scenario `edge` | rounded | implemented |
| `speed_mean` | scenario mean desired speed | implemented |
| **crush on/off** (proposed name `w2_crush`: on default / off) | removes F^crush in C4 | **to implement in execution, default-off** |
| **corner rule** (proposed name `w2_wall_corner`: segment_sum default / union) | nearest point on the union of walls sharing an end | **to implement in execution, default-off** |

Each new flag: implement on the execution branch, re-run regress.py (must print e381b49dc24acccd OK), log in a CODE_CHANGES.md. Flag names are proposals; the execution session may rename them and must record the final names here via the change log.

### Scenarios
- Room bottleneck: 10 × 10 m room, door on x = 10 centred at y = 5, width w, 100 agents.
- CroMa-like bottleneck (sim/scenarios/croma.py, ae466a0): walled holding area 7.8 × 8.6 m, entrance gap w, corridor walls of length L (2.0 or 0.21 m), goal 1 m beyond the corridor, non-overlapping start in the half-annulus r ∈ [1.8, 7.5] m, flow line at the entrance plane, wall-leak counter. Geometry inferred from trajectories (wave2b/data/b1_geom.json). Known differences: model start median r ≈ 4.7 m vs human 2.9–4.0 m; model agents start at rest; barrier shapes beyond the entrance approximated by straight walls (INFERRED).
- Open bidirectional corridor and open plus-shaped crossing with sinks and a wall-leak counter (sim/scenarios/open_geometries.py).

---

## 8. Theory items T1–T5 (all pending derivation sign-off) [NEEDS PALAASH]

### T1. Rest-state lemma, dissipative form [NEEDS PALAASH: derivation sign-off]
- Write F(x, v) = F_0(x) − D·v + G(x, v), with F_0 the rest-state field, D·v = m·v/τ, G(x, 0) = 0 and v·G(x, v) ≤ 0 for |v| < ε.
- Then the fixed points (x*, 0) are exactly the zeros of F_0. If F_0 = −∇U (true for C1 with ρ frozen), a strict local minimum of U is Lyapunov-stable, with E = ½Σm v² + U.
- Instances: TTC is identically zero near v = 0 (ttc.py:91-97), so C2's fixed points and their stability equal C1's. SFM sliding friction vanishes at rest with a negative-semidefinite velocity Jacobian. ORCA is **not** rest-vanishing: at rest with no binding constraint F^orca = m·v0·ê/τ_ORCA, a second drive (69–195 N per trapped agent in the Wave 1 snapshots; scan/FEASIBILITY.md, probe P2; VERIFIED).
- Evidence: C2 frees 0/40 lone-trap snapshots = C1 (wave2/data/w22_analysis.json); C2 0/26 pairs = C1, 0:0 discordant (wave2b/data/a5_analysis.json). VERIFIED.
- Check: sign conventions of sfm.py:106-108 and walls.py friction; stated for the noise-free skeleton only.

### T2. Stuck-alone criterion and the k = 3 rule [NEEDS PALAASH: derivation sign-off]
- An agent of radius r at rest on the door axis is stuck alone iff g_max(r) > m·v_eff/τ, with g_max(r) the maximum backward wall force along the axis from the code's WallForces on the real segments. With the C3 drive the threshold adds w_o·m·v0/τ_ORCA.
- g_max at w = 0.8: 83 / 156 / 291 / 543 N at r = 0.20 / 0.25 / 0.30 / 0.35 m; median drive 215 N (C1), 431 N (C3) (wave2/WAVE2_REPORT.md W2.1(a)).
- Stuck-alone fraction of spawned agents: C1 drive 0.81 / 0.233 / 0.018 / 0 / 0 at w = 0.7 / 0.8 / 0.9 / 1.0 / 1.2; C3 drive 0.22 / 0.014 / 0 / 0 / 0 (10,000 agents; wave2/data/w21_analysis.json). 0 with B_w ≤ 0.04 at the jambs (wave2/data/w25_analysis.json; identical on-axis profile for B_w_edge, wave2b/CODE_CHANGES.md).
- End-of-queue rule: a stuck-alone agent exits iff ≥ k = 3 others are active when it reaches the door zone. 96.4% accuracy (TP 2,052, FN 11, FP 70, TN 87); k = 4 gives 96.0% (wave2/data/w21_analysis.json). k is fitted; production reports leave-one-seed-out accuracy and AUC (E1).
- Order statistics: stuck-alone fraction by arrival decile 0.20 … 0.31, 0.63 in the last two deciles; 96/99 blockers stuck-alone (W2.1).
- Physical reading (INFERRED): pushers transmit their drive through the social term, but off-axis pushers settle against the jamb faces, so a column of about three is needed.

### T3. Effective temperature of per-step noise [NEEDS PALAASH: derivation sign-off]
- Per component: v_{n+1} = (1 − dt/τ)·v_n + σ·ξ_n. Stationary variance σ²/(1 − (1 − dt/τ)²).
- **k_BT_eff = m·σ²/(1 − (1 − dt/τ)²)** = (m·σ²τ/2dt)·[1 − dt/2τ]⁻¹, per agent with its own τ; the bracket is 1.010 at dt = 0.01, τ = 0.5 (exact discrete factor 1.0096, W2.3(c)).
- Realised blocker variance / formula: median 1.018 (alone), 1.002 (frozen), 1.024 (full) (wave2/data/w23_analysis.json). VERIFIED.
- Predicted Δt signature at fixed per-step σ: kT ∝ 1/dt, so ln[λ(dt₁)/λ(dt₂)] = ΔU·(1/kT₂ − 1/kT₁); ≈ 0 for dt-scaled σ.
- Check: the variance identity for the clamp-then-noise order (published) and noise-before-position (numerics = fixed).

### T4. Collective Kramers escape over string-method barriers [NEEDS PALAASH: derivation sign-off]
- With ρ frozen the C1 rest field is conservative: −∇U equals the code force to ≤ 2e-7 N. U = Σ c_i|x_i − g| + wall + pair terms, c_i = m·v_eff,i/τ_i.
- Minimum-energy paths by the string method in three conditions (wave2/data/w23_barrier.json):

  | condition | barrier (J) |
  |---|---|
  | blocker alone | 10.7–44.8 (equals the 1-D on-axis integral) |
  | neighbours frozen | 1.8–14.6 (on-axis snapshots) |
  | all residual mobile | 0.3–9.6 |

- Arrhenius slopes match the barriers within ≈ 25% wherever βΔU ≳ 1 and events exist at all σ; prefactors 0.05–0.7 s⁻¹; Weibull shape median 1.2 (0.7–2.2) (wave2/data/w23_analysis.json).
- This resolves the 50× gap of the 1-D lone-barrier estimate: neighbours lower the collective saddle (INFERRED reading of VERIFIED numbers).
- Why noisy whole runs still fail: the highest-margin blocker arrives last and ends alone, facing a lone barrier of 17–45 J at kT = 5 J (W2.4, wave2/data/w24_analysis.json).
- Check: the density switch along the path is ignored; the 2N-D path with all residual agents mobile.

### T5. Pair Hessian and fold [NEEDS PALAASH: derivation sign-off]
- Setting: C1, numerics fixed, w = 0.8, B_w = 0.04 all walls; 26 pair snapshots (seeds 42–241).
- Configuration: members in front of the jamb faces, x = 9.54–9.65 m, |y − 5| = 0.40–0.51 m, face gap 0.09–0.14 m, pair surface gap 0.28–0.36 m (no contact in 26/26), |v| ≤ 1e-4 m/s. Median forces on the lower member: drive (+138, +44) N, wall (−138, 0) N, pair (0, −44) N. Asymmetry: axis distance 0.5–90 mm (median 28), drive 0.6–29 N (median 10) (wave2b/data/a3_pair_stability.json).
- Hessian of U (ρ frozen; max |F_code + ∇U| = 2.2e-7 N; central differences h = 1e-4 m): positive definite in **26/26**; λ1 = 48–129 N/m (median 89), eigenvector the common lateral shift (≈ 0.71, 0.71 in (dy_lo, dy_hi)); λ2 = 626–1,702 N/m (opposed lateral). Triples 6/6 strict minima (λ1 = 64–80 N/m).
- Consequences (VERIFIED, wave2b/data/a5_analysis.json, a5_predict.json): δ ≤ 1 cm displacement frees 0/26; 1e-9 m perturbations 0/30; a finite lateral bias removes the minimum through a fold; static overdamped relaxation predicts freed/held in 182/182 (snapshot, b) cases (TP 119, TN 63), b* ≈ 0.01–0.05.
- Thermal escape over a small barrier: pooled first-exit rates ≈ 0.08 / 0.14 / 0.19 s⁻¹ at k_BT_eff = 0.81 / 1.82 / 5.05 J, effective barrier ≈ 0.8 J, prefactor ≈ 0.22 s⁻¹ (INFERRED; 3 points). A string-method pair barrier is computed in E7b.

---

## 9. Attribution protocol and pre-registered signatures (paper §4, Table 2)

### Classes and controls
| Class | Meaning | Signature it predicts |
|---|---|---|
| P prevent | acts before a deadlock forms; no effect on a frozen state | quench from a frozen deadlock = C1 |
| L reshape | an added deterministic drive moves or removes the fixed point | deterministic (seed replay D = 0), Δt-flat, frozen-mean + frees and − does not |
| T heat | activated escape over a barrier | stochastic (D > 0), exponential escape, Δt-dependent at fixed per-step σ, flat when σ is √Δt-scaled, Arrhenius slope = barrier |
| D steer | finite directional symmetry breaking | deterministic, sign-symmetric in rate under reversal, handedness of the first agent out flips, fold threshold |
| N glitch | numerical or geometric artefact | disappears in the corrected mode or open geometry |

Rest-state lemma (T1) assigns no resolving role to rest-vanishing terms.

Matched controls (decisions D5, D6):
- **Lone trap:** noise C1 + σ* (T) matched to C3 rvo2 completion; frozen-mean + (L) as the deterministic matched control; lateral bias as a reported **negative control** (it frees 0/10 at every b; W2.2).
- **Pair class:** lateral bias b* (D) fitted to C3 rate (b*_rvo2 to C3 rvo2 for forward claims; b*_pub to C3 published, as in A6); noise (T).

### Statistics
- Allowed: Wilson CIs; Kaplan–Meier with censoring; exponential/Weibull hazards; paired TOST; exact McNemar; LOSO accuracy and AUC.
- Not allowed: unpenalised Cox with a zero-event arm; a global multiplicity family presented as per-family.
- Sample sizes (α = 0.05 each side, power 0.80, z = 2.927; wave2/SIGNATURES.md): unpaired n = z²·2p(1 − p)/δ² (186 per arm at p = 0.575, δ = 0.15; 419 at δ = 0.10); paired n = z²·p_disc/δ²; log-hazard SE ≈ √(1/d₁ + 1/d₂).
- All signatures are registered before E2–E7b run; changes after data collection are reported as deviations. All use the common library paired by snapshot except S7.

### Signatures (lone trap: 60 corrected-forward snapshots from E1b unless stated; pair class: ≥ 40 snapshots from E7b)

| # | Signature | Exact statistic | Margin / test | n | Decision rule | Pilot (evidence) |
|---|---|---|---|---|---|---|
| S1 | Δt scaling at fixed per-step σ | per snapshot ℓ = ln[λ̂(0.005)/λ̂(0.02)], censored exponential fits; arms per_step, dt_scaled (σ = 0.05), C3 rvo2 (ln escape-time ratio) | dt_scaled and C3: TOST on mean ℓ within ±ln 1.5. per_step: one-sided mean ℓ > 0 and slope of ℓ on the barrier prediction 1 ± 0.3 | 20 snapshots with collective ΔU ≥ 3 J × 20 restarts | T for noise iff per_step ℓ > 0 **and** dt_scaled ≡ 0; L for ORCA iff C3 ≡ 0 | per_step 2.3× (0.84–12.7×), dt_scaled 0.85×, C3 0.97–1.21 (W2.3(e)) |
| S2 | Seed replay | D = fraction of snapshots whose K = 5 replicates disagree on "freed in 120 s"; median within-snapshot SD of first exit | deterministic arms: exact (any discordance falsifies); noise: Wilson CI on D | 60 × 5 | L/D iff D = 0 and SD = 0; T iff D > 0 | C3 max \|Δt\| = 0.000 s over 45 exits; noise SD 3.5–5.1 s (W2.2) |
| S3 | Frozen-mean ± (D6) | paired freed under constant +w_o·m·v0·ê/τ_O vs − | exact McNemar (+ > −); + vs C3 rvo2 paired TOST ±0.10 | 60 | L via goal-parallel drive iff + frees, − does not (p < 0.05), and + ≡ C3 | + 25/40, − 0/40 (W2.2) |
| S4 | Drive/constraint split | paired: drive_only vs C3 (pub, rvo2); constraint_only vs C1 | paired TOST ±0.10 | 60 (p_disc ≤ 0.07) | L iff drive_only ≡ C3 and constraint_only ≡ C1 | 23 vs 23, 0 discordant; 0/40 (W2.2) |
| S5 | Failure identity | (i) AUC of "stuck-alone and < 3 active at arrival" for non-exit; (ii) AUC of blocker C3 margin for C3 failure; (iii) Jaccard of unresolved sets (C3 vs matched noise) | (i),(ii) lower 95% bound ≥ 0.80; (iii) bootstrap CI | E1 (200 runs), E2 (60) | shared margin, **not** shared mechanism | 96.4%; no FP / 5 FN (W2.1, W2.2) |
| S6 | Escape-time shape | pooled censored Weibull k̂ after per-snapshot scale normalisation | TOST on ln k within ±ln 1.25 | ≥ 105 events per condition | T over one barrier iff k ≡ 1 | median 1.2 (W2.3) |
| S7 | Matched completion | whole-run completion, w = 0.8, 600 s: C1 + σ* vs C3 rvo2 (corrected-forward) | TOST ±0.15 | 186 per arm | equal by construction: the calibration target, not mechanism evidence | CF noise 12/25 at σ = 0.05 (W2.4) |
| S8 | Lateral bias at the lone trap (negative control, D5) | freed under b ∈ {0.05, 0.1, 0.2, 0.5} vs C1 | upper 95% Wilson bound ≤ 0.10 | 60 | lone trap not broken by deterministic symmetry breaking | 0/10 at every b (W2.2) |
| S9a | Pair: fold prediction | per (snapshot, b) static relaxation vs 120 s quench | lower 95% Wilson bound of agreement ≥ 0.90 | ≥ 40 × 8 b | D-type fold confirmed iff met | 182/182 (A5) |
| S9b | Pair: no infinitesimal breaking | freed under δ ∈ {1e-3, 1e-2} m and 1e-9 m perturbation | upper 95% Wilson bound ≤ 0.10 | ≥ 40 | strict-minimum reading confirmed | 0/26, 0/30 (A4) |
| S9c | Pair: ORCA implementation dependence | paired C3 published vs C3 rvo2 | exact McNemar | ≥ 40 | if significant, every pair-class ORCA statement is per implementation; forward claims use rvo2 | 10 vs 1, 9:0, p = 0.004 (A4) |
| S9d | Pair: constraint vs drive split | constraint_only (pub **and rvo2 LP**) vs C1; drive_only vs C3 rvo2 | exact McNemar; paired TOST ±0.10 for equivalence | ≥ 40 | D-type component iff constraint_only > C1 | 26/26 vs 0/26 (published LP only) |
| S9e | Pair: handedness | fraction of freed snapshots where the bias-favoured member exits first; flip under b → −b | exact binomial vs 0.5 | ≥ 40 | lateral resolver ≈ 1 and flips; compare ORCA | bias 9/9 lower-first, −b 0/12; C3 pub 2/10 (A6) |
| S9f | Pair: thermal escape | censored exponential first-exit rate vs k_BT_eff, σ ∈ {0.01, 0.02, 0.03, 0.05}; string-method pair barrier | Arrhenius slope within ±25% of the barrier where βΔU ≳ 1 | ≥ 40 × 4 σ × 5 seeds | T for noise at the pair class | ΔU_eff ≈ 0.8 J (A4) |
| S9g | Pair: matched bias b* vs C3 | b* fitted on rate; then failure identity (Jaccard), S9e handedness, reversal (rate under −b*), seed replay | rate: paired TOST ±0.10; held-out: as S9e, exact McNemar, S2 rule | ≥ 40 | one matched control not enough iff matched on rate and separated on ≥ 1 held-out signature | b = 0.02 vs C3 pub 9 vs 10/26 (5:6, p = 1.0); Jaccard 0.27; handedness 9/9 vs 2/10 (A6) |

Notes: S1–S4, S6 and S9 are interventional and paired, so a matched control cannot be tuned to them. Do not reverse the full ORCA force m(v_ORCA − v)/τ (it reverses damping too; confounded, W2.2); the frozen-mean ± pair replaces it (D6).

---

## 10. Figures (exactly 7) and tables (exactly 4)

### Style rules (all figures)
- Plain data figures: **axis labels only**. Every series and any other annotation is identified in the caption; nothing else inside the figure (no legends, titles, panel letters, arrows or text). Panels are referred to in the caption by position (left, right, top, bottom).
- Vector PDF at LNCS text width (12.2 cm; half width 5.9 cm).
- One colour-blind-safe palette (Okabe–Ito) with a fixed arm → colour mapping in every figure: C1 black, C2 orange, C3 published sky blue, C3 rvo2 blue, C4 bluish green, noise vermillion, frozen-mean/drive reddish purple, lateral bias yellow; humans grey. Line style distinguishes conditions within an arm.
- One font style throughout (document serif, 8 pt; ticks 7 pt); lines 1.0 pt, markers 3 pt; left and bottom spines only; units in axis labels.
- One Matplotlib style file (figures/style.mplstyle) used by every figure script.
- No titles inside figures. Every figure regenerated from new runs; a figure showing a conference quantity says so in its caption and cites [Gang & Veluri 2026].

| Fig | Content | Data | Caption content (all identification lives here) |
|---|---|---|---|
| 1 | **Lone-trap physics.** Left: backward door-edge force on the door axis against position, for several radii, compared with the C1 and C3 drive levels. Right: the stuck-alone region in the (r, v0/τ) plane, overlaid on the spawned population | E1 (agent attributes); w2lib.Passability | radii and their line styles; C1 and C3 drive bands (median and range); wall law (A, B); door width; region boundary g_max(r) = m·v_eff/τ; number of spawned agents and seeds; mode |
| 2 | **Completion against exit width,** and against wall-range variants including jamb-only, with Wilson CIs | E7 (+ E1 at 0.8 m) | widths; cell definitions (B_w all walls, B_w_edge jambs only, rounded, line goal); n per cell; deadlock type counts (lone / pair / triple) in text; mode |
| 3 | **Noise as collective escape.** Left: Kaplan–Meier escape curves. Right: Arrhenius plot (ln λ vs 1/k_BT_eff) for the full system, the blocker alone and frozen neighbours, with barrier-predicted slopes | E4 | conditions by line style; σ values; censoring at 300 s; restarts per condition; snapshots; string-method barriers used for the predicted slopes; T_eff formula (T3) |
| 4 | **The Δt signature.** Escape hazard against Δt for per-step σ, √Δt-scaled σ and ORCA | E3 | arms by colour/line; σ = 0.05; Δt ∈ {0.005, 0.01, 0.02}; for C3 the plotted quantity is the inverse deterministic escape time; snapshots and restarts; TOST margin ±ln 1.5 stated in the caption |
| 5 | **Lone-trap quench outcomes** for every intervention, with time-to-free | E2 | arm order and colours; freed fraction (Wilson) and first-exit time distribution; 60 snapshots; 120 s window; replicates |
| 6 | **Pair class.** Left: fraction freed against bias b with Wilson CIs, with the static fold prediction. Right: pair outcomes for each intervention | E7b | b values (both signs); prediction markers (open) vs quench (filled); arms incl. C3 published, C3 rvo2, drive_only, constraint_only (pub and rvo2 LP), frozen ±, noise; n snapshots; window |
| 7 | **Human validity.** CroMa against each model variant: flow, longest gap and fluctuation level | E10 | the five CroMa 0.8 m runs (4D030, 4D040, 4D110, 4D120, 4D130); model cells; completion per cell stated in the caption; estimator (Savitzky–Golay 1.48 s, 0.74 m neighbour mean, waiting zone 0.3–2.5 m; wave2/scripts/w28_croma.py, unchanged); n = 25 per cell |

| Table | Content | Source |
|---|---|---|
| 1 | Parameters and the two model modes | Plan 7 |
| 2 | Mechanism classes, controls and pre-registered signatures, with statistic, margin, n and decision rule | Plan 9 |
| 3 | Matched-control results for both classes: rate match plus the signature tests. The σ-sweep summary (σ50 with profile CI; completion per σ) goes here or in the text | E2–E6, E7b |
| 4 | Conference claims and their status in this work: confirmed / revised / withdrawn, each with its evidence | plan/CORRECTIONS_TABLE.md; E8, E9, E11 |

---

## 11. Experiments in priority order

Unit costs (this Mac, 4 workers, contended; wave2/COMPUTE_PLAN.md, wave2b/WAVE2B_REPORT.md):

| Unit | Cost |
|---|---|
| C1 bottleneck run to deadlock/completion | ≈ 31 s (published) / 53 s (CF, B_w = 0.04) |
| C1 + noise, 600 s | 67–92 s |
| C3 600 s run, 100 agents | ≈ 0.6 h published / 0.1 h rvo2 |
| Quench from a snapshot, ≤ 120 s | 0.7–14 s |
| Escape restart, ≤ 300 s | 8.8 s |
| Pair-library run (CF, B_w = 0.04) | ≈ 36 s |
| Open counterflow, 60 s, 100 agents | C1 33 s, C2 46 s, C3 rvo2 128 s, C4 rvo2 216 s, C3 published 832 s |
| Open crossing, 60 s, 200 agents | C1 65 s, C2 92 s; C3/C4 rvo2 ≈ 400 / 600 s (INFERRED) |
| CroMa geometry, ~130 agents | C1 54–118 s; C3 rvo2 600 s run 208–418 s |

Machine: Apple Silicon, 8 cores, 8 GB → 4 workers (≈ 150 MB per worker). Larger machine: a 16–32-core box.

| Priority | E | Purpose | Configuration and mode | n | Metrics | Statistics | CPU-h | Machine | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **E1** | Lone-trap library; k-rule validation | C1, w = 0.8, 600 s cap, stop at deadlock. (a) published-reproduction (Table 4); (b) corrected-forward (forward claims, quench library) | 200 seeds each (42–241) | completion; per-agent stuck-alone margin; arrival order; k-rule; snapshots | Wilson; **leave-one-seed-out accuracy and AUC** of the k-rule (S5i, AUC lower bound ≥ 0.80) | 1.7 + 2.9 | Mac | Fig 1, Fig 2 |
| 2 | **E2** | Quench signatures S2–S5, S8 | 60 CF snapshots from E1b. Arms: C1, C2, C3 pub, C3 rvo2, drive_only, constraint_only (pub, rvo2), frozen_mean ±, lateral bias b ∈ {0.05, 0.1, 0.2, 0.5}, C1 + noise σ ∈ {0.03, 0.05, 0.07} × 5 seeds, 1e-9 m perturbation × 5 | 60 snapshots | freed; first exit (time-to-free); which agent; replicate discordance | paired TOST ±0.10; exact McNemar; D-statistic | 4 | Mac | Fig 5, Table 3 |
| 2 | **E3** | Δt scaling S1 | 20 snapshots with collective ΔU ≥ 3 J; per_step vs dt_scaled at σ = 0.05; dt ∈ {0.005, 0.01, 0.02}; C3 rvo2 | 20 × 3 dt × 2 modes × 20 restarts + 60 C3 | censored exponential λ per snapshot | TOST ±ln 1.5; one-sided > 0; slope 1 ± 0.3 | 7 | Mac | Fig 4, Table 3 |
| 3 | **E4** | Escape distributions and string-method barriers S6 | 10 snapshots × 3 conditions (full / frozen neighbours / alone) × 3 σ × 20 restarts, 300 s censor; string method | ≥ 105 events per condition | KM; Weibull k; Arrhenius slope vs ΔU | TOST ln k ±ln 1.25; slope/ΔU ±25% | 4.5 | Mac | Fig 3 |
| 4 | **E5** | Large-n σ-sweep (σ50) | C1 + σ, w = 0.8, 600 s. (a) published-reproduction σ ∈ {0, 0.02, …, 0.20}, 9 levels; (b) corrected-forward, 5 levels around σ50 | 100 seeds per σ | completion | Wilson per σ; binomial-logit σ50 with profile CI | 23 + 13 | Mac | Table 3 (or text) |
| 4 | **E6** | Matched completion S7: C1 + σ* vs C3, **orca = rvo2** | corrected-forward | **186 per arm** (TOST-sized, ±0.15 at p ≈ 0.575) | completion at 600 s | TOST ±0.15 | 4.8 + 19 | Mac (≈ 6 h wall) | Table 3 |
| 4 | **E6p** | Published-ORCA matched completion | published-reproduction: C3 published, new seeds | **reduced n = 50** | completion | Wilson; consistency with 13/25 (Fisher) | 30 | larger machine preferred (≈ 1–2 h on 16–32 cores), or Mac over 2 nights | Table 3, Table 4 |
| 5 | **E7** | Wall-model validity cells | corrected-forward, C1: w ∈ {0.7, 0.8, 0.9, 1.0}; B_w ∈ {0.04, 0.02} all walls; **B_w_edge = 0.04 jamb-only**; rounded; line goal; line + rounded (10 cells) | 100 seeds per cell | completion; deadlock type (lone / pair / triple) | Wilson; type counts | 15 | Mac | Fig 2 |
| 6 | **E7b** | Pair class | corrected-forward, C1, B_w = 0.04 all walls. (a) **grow the library to ≥ 40 pairs** (26 now; ≈ 110 more seeds at the 13% pair rate, from seed 242); (b) quench arms: C1, C2, C3 pub, C3 rvo2, drive_only, **constraint_only with the published and the RVO2 linear program**, frozen ±, lateral bias b ∈ {±0.01, ±0.02, ±0.03, 0.05, 0.1}, noise σ ∈ {0.01, 0.02, 0.03, 0.05} × 5 seeds, 1e-9 m × 5 on every deterministic arm, δ ∈ {1e-3, 1e-2, 3e-2} m; (c) Hessian + static fold prediction per snapshot; (d) **string-method pair barrier** (≥ 10 snapshots); (e) **fit the matched bias b*** to C3 rvo2 and C3 published on rate, then test it on S9e–S9g | ≥ 40 snapshots | freed; first exit; which member first; fold prediction; λ_min; barrier | S9a–S9g; exact McNemar; Wilson; paired TOST | ≤ 9.3 (earlier 60-snapshot estimate is an upper bound; library growth ≈ 1.1, INFERRED) | Mac | Fig 6, Table 3 |
| 7 | **E10** | CroMa geometry (like-for-like human validity) | CromaBottleneckScenario, w = 0.8, N and L matched to the 5 CroMa 0.8 m runs (seeds cycle through run types). Cells: C1 published-reproduction (segment sum); C1 corrected-forward (**corner rule fixed: union**); C1 CF + B_w_edge = 0.04; C3 rvo2 CF; C1 CF + σ* (matched-noise control) | **25 per cell** (5 per CroMa run type) | completion; flow; gaps > 2 s and longest; waiting-zone fluctuation (W2.8 estimator, unchanged) | Wilson on completion (0/25 → upper bound 0.13 vs humans 5/5); bootstrap CIs on per-run means; model/human ratios | ≤ 8 | Mac | Fig 7 |
| 8 | **E8** | Open counterflow (Table 4 only) | OpenBidirectionalScenario, 50 + 50; C1, C2, C3 pub, C3 rvo2, C4 rvo2 (corrected: crush off); **inflow sweep**, 3 densities | 25 per arm per density | throughput; stall episodes; leaks; LP infeasibility rate | bootstrap CIs; withdraw "gridlock" unless C3 < C1 with CI excluding 0 | 26 (C3 published 21 of it) | Mac (C3 published at 2 densities if short) | Table 4 |
| 8 | **E9** | Open crossing (Table 4 only) | OpenCrossingScenario, 100 + 100; C1, C2, C3 rvo2, C4 rvo2 (crush off); **inflow sweep**, 3 levels | 25 per arm per level | throughput ratio C2/C1; standoff count and lifetime; leaks | ratio CI; withdraw "tripling" unless ≥ 1.5× with CI excluding 1 | 24 | Mac | Table 4 |
| 8 | **E11** | Persistence-filtered throat-overlap rerun (Table 4 only) | corrected-forward, 50 agents, 300 s, C1, C2, C3 rvo2, C4 rvo2 at w ∈ {1.0, 1.2, 1.8}; C3 published at w = 1.0 only | 25 per cell | overlap-timesteps; episodes ≥ 0.1 s contiguous per pair, by zone | bootstrap CI; paired Wilcoxon C1 vs C4 with stated zero_method | ≈ 6 | Mac | Table 4 |

- **No FD experiment.** The FD calibration is dropped (D-open-7). Its cause (grouping by frame number across concatenated runs: sim/data/fundamental_diagram.py:29 with sim/data/loader.py:109-120) is recorded as a Table 4 row (plan/CORRECTIONS_TABLE.md E3).
- Total ≈ 198 CPU-h upper bound (E1 4.6, E2 4, E3 7, E4 4.5, E5 36, E6 23.8, E6p 30, E7 15, E7b ≤ 9.3, E10 ≤ 8, E8 26, E9 24, E11 6). Without E6p ≈ 168 CPU-h, about 42 h wall on 4 workers (≈ 6 overnight batches of 7 h).
- Before E10: implement the corner-rule flag; before E8/E9: implement the crush flag. Both default to published behaviour; regression hash checked after each.
- Each experiment: its own script with resumable JSONL output (w2lib.run_jobs); a PROGRESS.md line before each batch; commit after each batch; every reported number carries script, seeds, flags, dt, duration, wall time and an evidence label.

---

## 12. Risks and reviewer objections

| Risk / objection | Answer in the paper |
|---|---|
| **Zuriguel et al. 2014** (noise unclogs an SFM) | Phenomenon yes, attribution no. Noise is used as a fitted counterfactual control, not as a finding. Our trap is a contact-free wall-law trap; their arches need friction, which this SFM lacks (W2.9). |
| **Nicolas, Garcimartín & Zuriguel 2018** (Kramers escape, trap model) | Their framework is the template. New: barriers computed from the model's own landscape (string method); exact T_eff of per-step noise; Δt signature and frozen-mean reversal as interventional tests; the collective saddle as the resolution of a 50× rate gap. |
| **Pattern-oriented modelling** (Grimm 2005, 2012) | POM's nulls are structural and unmatched. Ours is a one-parameter perturbation fitted to the rival's headline score and falsified on pre-registered held-out signatures with TOST. Novelty worded "no instance found" (lit/OUT/FINAL_REPORT.md §1.6). |
| "You audit an artefact": the trap is specific to A = 2000 N, B = 0.08 m | A finding: critical width 0.8–0.9 m; the trap is local to the jambs (jamb-only 21/25 vs 0/25). The method does not depend on the trap's physics; the pair class repeats the audit on a different object. Practitioner guidance on door-edge wall treatment (paper §8). |
| Platform sensitivity (0/25 vs 1/25; 13/25 vs 7/25) | Large-n estimates with CIs lead (D2); the printed counts are n = 25 single-platform realisations reproduced on macOS; the Windows draws in a footnote. |
| Compute for published-ORCA ensembles | Forward claims use rvo2 (D4); published vs rvo2 equivalence at the lone trap on the paired library (E2; pilot 22 vs 23/40, 1 discordant); published-ORCA whole runs at n = 50 (E6p). |
| "Your lateral-bias control is a straw man" | At the lone trap it is a reported negative control (S8; D5). At the pair class the same bias is a genuine resolver and the matched control (S9g), so it discriminates between the classes. |
| ORCA pair verdict rests on an implementation defect | Stated per implementation (S9c); forward claims use rvo2; constraint_only run with both LPs (E7b). |
| Counterflow / crossing pilots small (n = 3, n = 10), jam regime | E8/E9 at n = 25 with an inflow sweep; claims withdrawn only by the pre-stated rules; Table 4 only. |
| Human comparison not like-for-like | CroMa-geometry scenario (0 wall leaks in 25 pilot runs); E10 at n = 25 per cell; corner rule fixed per mode; known geometry differences stated (Plan 7). |
| Pair library small (26 < 30 target) | E7b grows it to ≥ 40; S9 decision rules use Wilson bounds that account for n. |
| n = 25 certifies only ±0.25 | TOST margins and n declared in Plan 9 before running. |
| Missing canonical data of the conference paper | Every number in the paper is regenerated; Table 4 states which published numbers cannot be traced. |

---

## 13. Decisions log

**Applied earlier (confirmed by Palaash, wave2/DECISIONS_NEEDED.md):**
- D1: T_eff mapping. D2: platform-count wording. D3: both deadlock classes; contact arches out, their absence stated as a physics result. D4: ORCA in both forms; rvo2 for forward claims. D5: lateral bias as a negative control at the lone trap, retested on pairs. D6: frozen-mean ±. D7: Wave 2 flag interpretations accepted; jamb-only variant added. D8: Q1 dissipative lemma; Q2 two model modes; Q5 second author asked; Q6 φ_max dropped; Q8 costed FD options.

**Resolved:**
- The second author agrees to every change.
- No correction notice to the proceedings.
- The disclosure statement required by the publisher and the copyright form are handled at the writing stage.
- A new GitHub execution repo later (separate and secondary).
- Page target 23–25 including references.
- D1–D8 as previously applied.

**Applied in Plan v1:**
- Pair class as a secondary strand of about 3 pages.
- FD claims dropped.
- Crush declared in published mode and off in corrected mode.
- Corner rule: walls sharing an end use the nearest point on the union of walls, with no double counting (corrected mode).

**Pending [NEEDS PALAASH]: derivation sign-offs**
- T1 rest-state lemma (dissipative form);
- T2 stuck-alone criterion and the k = 3 rule;
- T3 T_eff form σ²/(1 − (1 − dt/τ)²);
- T4 collective Kramers escape over string-method barriers;
- T5 pair Hessian and fold.

None of these blocks E1–E4.

---

## 14. Change log

| Date | Version | Change |
|---|---|---|
| 2026-11-02 | v1 | v1 created |

---

## 15. Reconciliation notes

Every place where the earlier plan/ content (previous FINAL_PLAN.md, HANDOFF_EXECUTION.md, DECISIONS_OPEN.md, CORRECTIONS_TABLE.md, DIFFERENCES_POINTS.md) or wave2/SIGNATURES.md and wave2/COMPUTE_PLAN.md conflicted with the agreed Plan v1 content, and how it was resolved.

**Venue and length**
1. Page target: earlier "target 26, hard limit 30" (FINAL_PLAN §2) and "under 30 pages (target 24–28)" (HANDOFF §9) → **23–25 pages including references**. D-open-9's question on whether references count is closed.
2. New-material threshold: earlier "more than 50%" (HANDOFF §9) with an estimate "≈ 90%" → requirement **at least 30%**, target well over 70%. The 90% figure is not carried; the new outline gives ≥ 73% by a worst-case count (Plan 6).
3. The outline in Plan 6 sums to 23.0 pages, not 24; the difference is left as slack for the main-differences statement, acknowledgements and availability statements, which the outline does not list.
4. The submission deadline is not recorded anywhere in the repo (lit/OUT/VENUE_NOTES.md asks for the invitation wording). Not invented; to be taken from the invitation at the writing stage.

**Framing**
5. Title: the earlier working title "… A Physics-Based Self-Audit of Deadlock-Resolution Claims …" and its three alternatives → the Plan v1 title and two alternatives. The "self-audit" framing is dropped.
6. Thesis: earlier "the conference paper is the case study" → the paper is about the new work and builds on the conference audit principle; revisions are compact (Table 4 + paper §6.3), not a theme.
7. Contributions: earlier 4 (method; physics; validity; **transparent corrections**) → 4 (method; physics; attribution; validity). Corrections are no longer a contribution. Attribution is now its own contribution and includes the pair-class verdicts.
8. Correction notice (D-open-2): resolved as none; the CORRECTIONS_TABLE item about a notice is removed.

**Outline**
9. Earlier 12-section outline (incl. separate sections for each class, paradigms, matched control, validity, a 1.5-page corrections section, acknowledgements) → 9 sections. Mapping: old §5 + §6 + parts of §7 → new §5 (physics); old §7 + §8 → new §6 (attribution); old §10 corrections → Table 4 + §6.3; old §9 validity → new §7 (CroMa only; open geometries become Table 4 rows); old §2 related work → new §2 background with clogging physics, Kramers vs aging, multi-robot deadlock and equivalence testing added.
10. Pair class: earlier one section of 2 pages plus one figure (D-open-6 pending) → secondary strand of about 3 pages across §5.2 and §6.2.

**Model**
11. Corrected-forward mode: earlier `w2_numerics=fixed`, `spawn=rejection`, `w2_orca=rvo2` only → adds **C4 crush OFF** and the **corner rule** (union nearest point). Both need new default-off flags (not yet implemented; names proposed).
12. Crush (D-open-8): earlier open (published C4 vs C4 without crush) → crush present and declared in published mode, off in corrected mode. E8/E9 C4 arms are corrected-forward, so crush off.
13. Corner rule (D-open-10): earlier "report both corner rules; repeat each C1 cell" (FINAL_PLAN E10; B3) → the rule is fixed by mode (published: segment sum; corrected: union). The duplicate corner-rule cells in E10 are dropped.

**Theory**
14. T3 form: earlier written as (m·σ²τ/2dt)·[1 − dt/2τ]⁻¹ with an open question on the printed form → Plan v1 states the form σ²/(1 − (1 − dt/τ)²) (times m) as the sign-off item; the two are algebraically identical.
15. T1 was "accepted in principle" (D8 Q1) and T3 "signed off" (D1) in the earlier plan; Plan v1 lists all of T1–T5 as pending derivation sign-offs, as agreed.

**Signatures**
16. Pair-class signatures S9a–S9f: n changed from 60 to **≥ 40** snapshots, matching the E7b library target. S9d now requires constraint_only with both LPs. **S9g (matched bias b*)** added from the A6 pilot, with b* fitted to both C3 rvo2 and C3 published.
17. wave2/SIGNATURES.md listed S3 as "component reversal" and S2 at 40 snapshots; superseded by D5/D6 (frozen-mean ±; 60 snapshots), as in the earlier FINAL_PLAN §6. No change from the earlier FINAL_PLAN for S1–S8.

**Figures and tables**
18. Figure count: earlier "≤ 10 figures" (FINAL_PLAN §7, HANDOFF §7) → **exactly 7**. Dropped or merged:
    - old Fig 2 (order statistics, k-rule accuracy vs k) → dropped; k-rule LOSO accuracy and AUC go in the text (§5.1);
    - old Fig 3 (quench matrix) → new Fig 5 (outcomes with time-to-free);
    - old Fig 4 (barrier energy along the path + Arrhenius) and old Fig 6 (KM) → merged into new Fig 3 (KM + Arrhenius); the energy-profile panel is dropped (barriers enter as predicted slopes and in the text);
    - old Fig 5 (dt signature) → new Fig 4 (hazard against Δt rather than per-snapshot ℓ);
    - old Fig 7 (pair class, three panels) → new Fig 6 (two panels); the residual-position panel and the Hessian strip plot are dropped (Hessian numbers go in the text, §5.2);
    - old Fig 8 (wall-law sensitivity) → new Fig 2 (adds completion against width);
    - old Fig 9 (open geometries) → dropped; results become Table 4 rows;
    - old Fig 10 (human anchor, three panels incl. gap distributions) → new Fig 7 (flow, longest gap, fluctuation); completion moves to the caption and text; gap distributions dropped.
19. Figure style: earlier "a legend outside the axes is allowed where the caption alone would be ambiguous" and panel letters in captions → no legends or panel letters inside figures; axis labels only; panels named by position in the caption.
20. Tables: earlier list (model parameters; signatures; corrections; claim verdicts; σ-sweep as a table) → exactly 4: parameters/modes; classes and signatures; matched-control results (σ-sweep summary here or in text); conference claims (claim verdicts merged into Table 4).

**Experiments**
21. Priority order: earlier E1 → E2 → E3 → E4 → E7 (+ E7b) → E5 → E6 → E10 → E8 → E9 → E11 → E12 → E6p → now E1; E2 + E3; E4; E5 + E6 (+ E6p); E7; E7b; E10; E8, E9, E11. The σ-sweep and matched completion move ahead of the wall cells; E6p moves from last into priority 4 (still preferably on a larger machine); E7b becomes its own priority after E7.
22. E7b library target: earlier 60 pair snapshots (≈ 460 seeds) → **at least 40**; added the matched-bias fit and test (A6 → production). CPU-h kept as an upper bound (≤ 9.3).
23. E12 (human-anchor estimator on room-geometry model logs from E6) → **dropped**: Fig 7 uses the like-for-like CroMa geometry (E10), which includes a matched-noise cell. The W2.8 room-geometry comparison remains pilot evidence only.
24. E13 (FD calibration decision with options a/b/c) → **dropped, no FD experiment** (D-open-7 resolved as option a). The cause is recorded as a Table 4 row.
25. E8/E9/E11: earlier priority 2–3 in the validity section with a figure → lower priority, **Table 4 only**.
26. Total CPU-h: earlier ≈ 199 (incl. E12 0.6, E10 8, E7b 9.3) → ≈ 198 upper bound (E12 removed; E10 and E7b kept as upper bounds).

**Decisions**
27. D-open-1 (second author, missing data and scripts): resolved as "the second author agrees to every change". The earlier data request is not needed by Plan v1 (FD dropped; every number regenerated); it is not pursued as a blocking item.
28. D-open-3 (disclosure wording) and D-open-4 (copyright form): resolved as handled at the writing stage.
29. D-open-5 (repository): resolved as a new GitHub execution repo later, separate and secondary. The earlier recommendation (clone branch for execution, archival repo with Zenodo DOI) is not carried beyond that.
30. D-open-6, D-open-7, D-open-8, D-open-10: applied as listed in Plan 13.

**References**
31. ORCA rest-state drive: the earlier DIFFERENCES_POINTS.md gave "≈ 69–214 N per agent" with no evidence file; the only stored value is 69–195 N (scan/FEASIBILITY.md, P2), which Plan v1 uses.
32. Items named in the outline but not in lit/OUT/references.bib, to be fetched later from primary sources (never written from memory): Wilson (1927) score interval; McNemar (1947) test; the Springer LNCS template (llncs class and author instructions); the PRIMORIS instructions and Licence to Publish form. The CroMa dataset entry exists (fzj_ped20219).
33. Wording: the agreed decision on the publisher-required disclosure statement is recorded in neutral wording ("the disclosure statement required by the publisher"), to keep tool references out of repository files. The decision itself is unchanged.
