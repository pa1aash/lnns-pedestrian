# Plan v1 summary (first draft, frozen; full plan: plan/FINAL_PLAN.md)

Venue: invited extended version for Springer LNNS of Gang & Veluri, SIMULTECH 2026, pp. 474-481,
DOI 10.5220/0015190200004094. Length 23-25 pages including references. LNCS template fetched from Springer.

Title: One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution
in Pedestrian Steering Models.

Thesis: matching a control to a paradigm's headline score is not evidence that the two share a
mechanism. Physics-derived held-out signatures decide. In two deadlock classes, the same headline
score hides different mechanisms.

Contributions (ranked)
1. Method: calibrate-then-falsify. Five classes (P prevent, L reshape, T heat, D steer, N glitch);
   matched controls tested on pre-registered held-out signatures (TOST, exact McNemar); rest-state lemma.
2. Physics: lone-agent trap at the door edges (stuck-alone criterion, k = 3 rule, critical width
   0.8-0.9 m, local to the jambs) and symmetric pair standoff (strict minimum, removed by a fold).
   No persistent contact arches (no static friction).
3. Attribution: lone trap, ORCA = extra goal drive (L), noise = collective activated escape (T),
   separated by dt scaling, seed replay, constant-push reversal. Pair class: bias via the fold;
   ORCA's constraint part acts; published-ORCA success hinges on its defect (10 vs 1 of 26).
4. Validity: CroMa at 0.8 m flows; every model variant deadlocks or flows at about half the
   human rate with long gaps. Guidance on wall treatment at door edges.

Outline (pages; total 23.0 of about 24)
- Title, abstract 0.5
- 1 Introduction 2.0
- 2 Background 2.0
- 3 Model and scenarios 2.5
- 4 Attribution protocol 2.5
- 5 Deadlock physics (lone trap; pair standoff; no arches; noise as collective escape) 3.5
- 6 Attribution results (lone trap; pair class; remaining conference claims + Table 4) 4.0
- 7 Validity against human data (CroMa) 2.0
- 8 Discussion 1.5
- 9 Conclusions 0.5
- References (about 40) 2.0

Figures (7)
1 Lone-trap physics (door-edge force vs position; stuck-alone region in (r, v0/tau))
2 Completion vs exit width and wall-range variants (jamb-only), Wilson CIs
3 Noise as collective escape (Kaplan-Meier; Arrhenius with barrier-predicted slopes)
4 The dt signature (hazard vs dt: per-step sigma, sqrt(dt)-scaled sigma, ORCA)
5 Lone-trap quench outcomes per intervention, with time-to-free
6 Pair class (freed vs bias with fold prediction; outcomes per intervention)
7 Human validity (CroMa vs each model variant: flow, longest gap, fluctuation)

Tables (4)
1 Parameters and the two model modes
2 Mechanism classes, controls, pre-registered signatures (statistic, margin, n, rule)
3 Matched-control results for both classes (+ sigma-sweep summary)
4 Conference claims: confirmed / revised / withdrawn, with evidence

Experiments (priority order)
1 E1 lone-trap library, both modes, LOSO k-rule (Fig 1-2)
2 E2 quench signatures + E3 dt scaling (Fig 4-5)
3 E4 escape distributions and string-method barriers (Fig 3)
4 E5 sigma-sweep; E6 matched completion n = 186/arm, orca = rvo2; E6p published ORCA n = 50 (Table 3)
5 E7 wall-model validity cells incl. jamb-only (Fig 2)
6 E7b pair class: >= 40 pairs, constraint_only with RVO2 LP, pair barrier, matched b* (Fig 6, Table 3)
7 E10 CroMa geometry, n = 25 per cell, corner rule fixed in corrected mode (Fig 7)
8 E8 counterflow, E9 crossing (n = 25, inflow sweep), E11 overlap rerun (Table 4 only)
No FD experiment (dropped; cause recorded in Table 4). About 198 CPU-h upper bound, 168 without E6p.

Model modes
- published-reproduction: all defaults; C4 crush present and declared.
- corrected-forward: numerics=fixed, spawn=rejection, orca=rvo2, crush off, corner rule (union).
New default-off flags to implement: crush on/off; corner rule.

Pending sign-offs [NEEDS PALAASH]
T1 rest-state lemma (dissipative form); T2 stuck-alone criterion and k = 3;
T3 T_eff = m sigma^2 / (1 - (1 - dt/tau)^2); T4 collective Kramers escape over string barriers;
T5 pair Hessian and fold.
