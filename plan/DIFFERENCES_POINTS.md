# Main differences from the conference paper (factual points for the LNNS "differences" paragraphs)

Conference paper: Gang & Veluri, "A Diagnostic Methodology for Failure-Mode Ablation of SFM, TTC, and ORCA Pedestrian Steering Paradigms", SIMULTECH 2026, pp. 474–481, DOI 10.5220/0015190200004094.

These are bullet points for the authors to turn into the short statement of the main differences required by the invitation. They are not draft text. Aligned with Plan v1 (plan/FINAL_PLAN.md). Numbers that the production runs (plan/FINAL_PLAN.md §11) will replace are marked "pilot".

## Framing and title
- New title: "One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models" (FINAL_PLAN §3). New abstract and conclusions.
- The paper is about new work. It builds on the conference paper's audit principle (failure-mode ablation with a matched control), which it cites.
- Thesis: matching a control to a paradigm's headline score is not evidence of a shared mechanism; physics-derived held-out signatures decide, and in two deadlock classes the same headline score hides different mechanisms.
- Contributions (ranked; FINAL_PLAN §5):
  1. method: the calibrate-then-falsify protocol (five classes P/L/T/D/N; pre-registered held-out signatures with equivalence statistics; rest-state lemma);
  2. physics: two classes of narrow-exit deadlock (lone wall-law trap at the door edges; symmetric pair standoff, a strict minimum removed by a fold); no persistent contact arches;
  3. attribution: lone trap, ORCA = extra goal drive (L) and noise = collective activated escape (T), separated by Δt scaling, seed replay and constant-push reversal despite matched completion; pair class, different verdicts (bias via the fold; ORCA's constraint part acts; published-ORCA success depends on its implementation defect, 10 vs 1 of 26 pilot);
  4. validity: like-for-like CroMa geometry at 0.8 m; practitioner guidance on wall treatment at door edges.
- The conference conclusion "ORCA resolves deadlock by symmetry-breaking; noise is statistically indistinguishable" is replaced: noise reaches ORCA's completion by activated escape (T), ORCA by a deterministic second goal drive (L); completion alone cannot distinguish them.
- Where results revise conference findings, they are stated compactly in Table 4 and one paragraph (§6.3); no correction notice.

## New theory (not in the conference paper)
- Rest-state lemma (dissipative form): TTC exerts no force on a stationary configuration, so it cannot change deadlock fixed points or their stability.
- ORCA's rest-state term identified as a second goal drive m·v0/τ_ORCA (69–195 N per trapped agent in the Wave 1 snapshots; scan/FEASIBILITY.md P2).
- Rest-state passability criterion from the code's own wall force, plus the end-of-queue rule (k = 3; 96.4% agent-level accuracy).
- Effective temperature of per-step velocity noise, k_BT_eff = m·σ²/(1 − (1 − dt/τ)²); realised/formula medians 1.00–1.02 (pilot).
- Collective Kramers escape over string-method barriers (0.3–10 J collective vs 11–45 J alone). This explains a 50× gap between the 1-D Kramers estimate and observed escape times.
- Stability analysis of the symmetric pair standoff: Hessian of the rest-state potential positive definite (26/26 pilot), and a fold under a finite lateral bias (static prediction 182/182 pilot).

## New experiments and designs
- A common library of frozen deadlock states, quenched under every arm (paired design). The conference compared whole-run completion only.
- Interventional signatures, pre-registered with TOST margins and sample sizes:
  - drive/constraint split of ORCA;
  - frozen-mean forward/reversed;
  - dt scaling at fixed vs dt-scaled σ;
  - seed-replay determinism (1e-9 m perturbations);
  - Weibull escape shape;
  - failure identity.
- Large-n estimates replace n = 25 counts:
  - library at n = 200 per mode and σ-sweep at n = 100 per σ;
  - matched completion at n = 186 per arm (±0.15 TOST) with RVO2-faithful ORCA; published ORCA at n = 50.
- A second deadlock class, absent from the conference paper: the symmetric contact-free pair standoff under a short-range jamb law (B_w = 0.04 m). Pilot: 20/25 complete with all walls, 21/25 with jambs only, versus 0/25 published; deadlocks are pairs and triples, with no lone traps.
- Wall-law sensitivity cells: width 0.7–1.0 m, B_w, jamb-only B_w, rounded jambs, line goal. The trap is model-specific: critical width 0.8–0.9 m; local to the door edges.
- Contact-arch test (high drive): no persistent contact arches. The conference's "arch" wording is replaced; the SFM has no static friction.
- Open, leak-free counterflow and crossing geometries with sinks and a wall-leak counter (n = 25 with an inflow sweep), replacing the closed geometries in which every crossing "exit" required a wall leak. Reported in Table 4 only.
- Human data, which the conference paper did not compare at 0.8 m: CroMa 2021 at exactly w = 0.8 m (flow, longest gap, waiting-zone fluctuation, one estimator) in a like-for-like CroMa geometry, n = 25 per model cell. Pilot: every model variant either deadlocks or flows at about half the human rate with long gaps.

## Model and implementation changes, declared
- Two declared model modes:
  - *published-reproduction* (all code defaults; explains the published runs);
  - *corrected-forward* (numerics fixed: speed clamp before position update and no force clip; rejection spawn; RVO2-faithful ORCA; C4 crush term off; walls sharing an end use the nearest point on their union, so a shared end is not counted twice). The corrected-forward mode is used for every forward claim.
- ORCA reported both as implemented (sign-flipped leg normal; silently dropped infeasible constraints) and RVO2-faithful (logic port of RVO2 v2.0.3; validated).
- Model section states what the code actually uses:
  - density: 3 m disk count, not Voronoi;
  - Weidmann γ = 1.913, ρ_max = 5.4, not the calibrated 0.833 / 5.98;
  - τ ~ U(0.4, 0.6) per agent;
  - TTC τ_max = 8 s;
  - crush term present in C4 (declared in published mode).
- New flagged variants, each defaulting to published behaviour (regression hash e381b49dc24acccd):
  - jamb-only wall range;
  - rounded jambs;
  - line goal;
  - lateral bias;
  - dt-scaled noise;
  - frozen-mean ORCA;
  - open geometries;
  - CroMa geometry;
  - crush on/off and the wall-corner rule (to be implemented in execution).

## Statistics changes
- Wilson CIs for all proportions; Kaplan–Meier with censoring; exponential/Weibull hazards; paired TOST and exact McNemar.
- Removed:
  - unpenalised Cox HRs with a near-zero-event arm;
  - the global Holm–Šidák family (described in the conference paper as per-family);
  - "statistically indistinguishable at n = 25" as an equivalence claim.

## Revisions of conference findings (details: plan/CORRECTIONS_TABLE.md, the source for paper Table 4)
- Withdrawn:
  - Table 4 and Fig 3 (stale pre-rejection overlap data);
  - the 9.3% / 7.4% reductions;
  - the Table 5 / Fig 5 significance stars;
  - the Cox HRs and p_HS = 0.044;
  - the attribution-ratio CI;
  - "|Δt_evac| ≤ 0.5 s";
  - "TTC triples crossing throughput" as published (closed-geometry leak artefact; open-geometry pilot 0.94×);
  - "ORCA gridlocks counterflow" as published.
- Revised:
  - C1 0/25 and noise 13/25, reported as single-platform realisations reproduced on macOS, with the Windows draws 1/25 and 7/25 in a footnote;
  - σ50 re-estimated at large n;
  - "arch" counts (24, not 25, stuck seeds);
  - "~40×" → 27.6× ORCA overhead;
  - OOD underestimation restated as C1-only, n = 5;
  - the FD calibration claims dropped (calibrated values never applied; FZJ input density anomaly, cause: grouping by frame number across concatenated runs).
- Confirmed:
  - C2 0/25 (now explained by the rest-state lemma);
  - throat overlaps C1 1.20 ± 1.96 vs C2/C4 0 at w = 1.0 as numbers (claim pending a persistence-filtered rerun);
  - model parameter values.

## Figures and tables
- Exactly 7 figures, all regenerated from new runs in one plain style (axis labels only; every series identified in the caption; vector PDF at LNCS text width; one colour-blind-safe palette and one font). No conference figure is reused.
- Figures: lone-trap physics; completion vs exit width and wall-range variants; noise as collective escape (Kaplan–Meier, Arrhenius); the Δt signature; lone-trap quench outcomes; the pair class; human validity (CroMa).
- Exactly 4 tables: parameters and the two model modes; mechanism classes, controls and pre-registered signatures; matched-control results for both classes; conference claims and their status.

## Length and reuse
- 23–25 LNCS pages including references (outline ≈ 24) vs 8 conference pages.
- New material well over 70% (worst-case count ≥ 73%; FINAL_PLAN §6), against the 30% requirement. Conference-derived quantities are regenerated and cited.
