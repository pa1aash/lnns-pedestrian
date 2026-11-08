# Plan changelog

## v1.1 — 2026-11-07

Approved changes C1-C9.

C1 Execution repository: public github.com/pa1aash/lnns-pedestrian, synced with ~/Developer/lnns-pedestrian, created now and pushed after every batch; everything public except copyrighted literature PDFs (lit/). The simulator is imported once (squashed) from pedestrian-abs branch exec-v1 in batch 2 and lives only there afterwards. pedestrian-abs and the plan root are never pushed. Supersedes D-open-5.

C2 Eight figures: a hero Fig 1 (Blender render of a real corrected-forward deadlock snapshot with the jamb wall-force field, alongside the pair-standoff energy landscape; raster 600 dpi, the only non-vector figure). Plan v1 Figs 1-7 become Figs 2-8. Outline about 23.6 pages.

C3 Captions at most two sentences: what the figure shows, then the colour and line key. Run details (n, seeds, flags, dt, window) go to the text and tables.

C4 Corner rule, flag w2_wall_corner = convex_union: for two segments sharing an endpoint P, if the agent's closest point on at least one of them is P, only the nearer of the two closest points contributes (nearest point on their union); otherwise both contribute. Removes the double count at convex shared ends (CroMa door edge) and keeps both walls at concave corners. Replaces "union nearest point at every shared end" (D-open-10).

C5 Drafting: the full paper text is drafted in execution sessions and rewritten by the authors; supersedes HANDOFF §0 ("the authors write the text"). The disclosure statement is handled by the authors at the writing stage.

C6 Framing: physics and STEM, not clinical-trial. No pre-registration or trial vocabulary in the paper or the workflow. Table 2 becomes "Mechanism classes and their physical signatures" (what each class predicts for each intervention). Statistics are reported as rates with confidence intervals, physical fits (Arrhenius, Weibull) and plainly stated agreement; equivalence margins are kept internally only where they set sample sizes.

C7 Reproducibility kept conventional: one Makefile from data to figures, tables and PDF; in-text numbers generated into numbers.tex. No evidence labels, manifests or per-number stamping.

C8 Compute on the Mac (4 workers) through one resumable job queue ordered by dependencies; RunPod only if needed later. Regression hash checked on the Mac.

C9 Deadline recorded: 18 Nov 2026 via PRIMORIS (from the invitation). Not used for planning.
C10 (2026-11-07) Repository licence: MIT (code and original content), copyright 2026 Palaash Gang and Arjun Veluri; text fetched from the GitHub licence API. Third-party data keep their own licences.

## 2026-11-08

C11 Live change log: from v1.1 on, lnns-pedestrian/plan/CHANGELOG.md is the live plan change log; the plan root (pedestrian-abs-plan) is a frozen archive and is not edited further.

C12 Deadlock typing: residual geometry is classified by snapshot surgery (keystone test: is the blocker held when alone; do the others exit once the blocker is removed), replacing the contact-cluster grouping, whose counts are not used in the text. The quench stopping rule (|v| < 1e-3 m/s for 10 s, deterministic arms only) and the 120 s window are those of the pilot quench script (wave2/scripts/w22_quench.py), resolving Table 1 note P7.

C13 End-of-queue rule: reported against the all-exit baseline (93.2% E1a, 93.1% E1b of stuck-alone agents exit), with its errors split between final blockers and agents queued behind a blocker; the rank AUC is the headline number. T2 is stated for the terminal rest state, where the local density gives v_eff/v0 ≥ 0.99 (pending sign-off).

C14 Table 2: the last column is "Corrected numerics" (open geometry is not a probe of a frozen bottleneck state and belongs to the Table 4 claims); P, L, T and D read "persists" there; D under both Δt probes reads "no Δt dependence" (a static tilt is deterministic).

C15 (2026-11-08) Quench library and escape-test temperatures:
- E2 = the 34 lone-keystone E1b snapshots plus 26 drawn (seed 2026) from the lone-keystone-with-second-trap class (60 in total); the primary quench outcome is "blocker freed within 120 s", with the two classes as strata.
- E3 = 20 snapshots spread across collective ΔU (≥ 3 J). The noise amplitude is set per snapshot from the T3 formula with the blocker's τ, so that ΔU/k_BT_eff at Δt = 0.01 s is 1.5 or 2.5 (alternating by ΔU rank). Per-step noise keeps σ fixed across Δt; √Δt-scaled noise keeps k_BT_eff fixed. Censoring is at 300 s (900 s for the per-step Δt = 0.02 s arm).
- E4 = 10 snapshots with at least 2 residual agents, spread across collective ΔU. String-method barriers are computed per condition (full, frozen neighbours, alone), with three noise amplitudes per (snapshot, condition) giving ΔU/k_BT_eff ∈ {1.5, 2.5, 3.5}. Censoring is at 300 s (900 s at 3.5); restarts are extended until each condition has at least 105 escape events.
- Reason: at a fixed σ = 0.05 m/s, the lone barriers (16-45 J) put the per-step Δt = 0.02 s arm at ΔU/k_BT_eff ≈ 6-36, so nearly every restart would be censored.

C15a (2026-11-08) String-method numerics: steepest-descent steps are capped at 2 mm per agent per iteration, because initial paths that pass through overlapping agents otherwise diverge. The 14 barriers computed before the cap reproduce to 3 decimals. A barrier is used to set a noise amplitude only if it passes the validity checks below.
- Validity checks (experiments/BAR/gate.py, run before the E3/E4 selection), per (snapshot, condition): (i) the string has converged: the largest perpendicular force over the uphill images (trapped minimum to one image past the top; upwind tangent; all mobile coordinates) is below 5 N, about 2.5% of the blocker's drive, the climbing image reaches |∇U| < 0.01 N, and the barrier changes by less than 1% when the number of images is doubled (31 to 62); (ii) the final image is an exit state (blocker past the door plane) and the saddle has no agent-agent overlap deeper than 2 cm; (iii) for the alone condition, the barrier agrees with the 1-D on-axis integral to 1%.
- If the frozen barrier is more than 1.5 times the alone barrier, it is also computed from a second initial path (blocker straight onto the door axis and along it, with the pinned neighbours displaced off the path for the initial guess only); the lower accepted value is kept and the neighbour the saddle squeezes past is recorded.
- A (snapshot, condition) that fails is not given a noise amplitude: E3 and E4 skip it and the reason is logged. A snapshot whose collective barrier fails is not eligible for E3 or E4.
- Gate choices confirmed (2026-11-08): the perpendicular force uses the upwind tangent; the force test runs from the trapped minimum to one image past the top, with tolerance 5 N and the climbing image at |∇U| < 0.01 N. Guard: the climbing image must be the maximum of U over the whole path; a path with a higher maximum on the downhill part fails.
- Resolution rule, for every barrier: accepted when the doubled string (62 images) passes the force test and the barrier changes by less than 1% between 31 and 62 images. If not, the string is computed once more at 124 images and the same rule is applied to 62 and 124; otherwise the barrier fails.
- Alone check (replaces the 1-D comparison): the alone barrier must agree to 2% with the minimum-energy-path barrier of the single agent's rest-state potential (same wall law and drive) on a 2-D grid (5 mm spacing, checked by halving to 2.5 mm, change below 1%). For on-axis blockers this equals the 1-D integral, which stays in the log.

C16 (2026-11-08) T2 signed as split.
- (a) The stuck-alone criterion g_max(r) > m·v0/τ is a physics result. It is stated for the terminal rest state, where the local density gives v_eff/v0 ≥ 0.99. Held-when-alone matches margin > 0 in 393/393 E1 deadlocks, and the 7 negative-margin blockers are the collective pair standoffs.
- (b) The k = 3 end-of-queue rule is reported descriptively (AUC 0.975 against an all-exit baseline of 93.2%), not as a mechanism; the end of the queue is analysed as a chain of stuck-alone agents.
C17 (2026-11-08) Hero: storyboard option C, with four fixes: one camera elevation and metre scale for both floor scenes; landscapes at true 1:1 horizontal aspect over the full opposed range, with no stretch; the lone trap taken from an E1b lone-keystone snapshot; encodings shared with Fig 2 (cividis margin ±150 N, magma wall force), with thin shading edges on agents.
C18 (2026-11-08) Collective barriers below the gate's resolution (seed60 0.02 J; seed75 near 0 J) are reported as marginally stable deadlocks, a physical category, not as numerical failures. They stay out of E3/E4 because no noise level can be set from them.
C19 (2026-11-08) T1 signed: the rest-state lemma in dissipative form.
- TTC is exactly zero for relative speed below 1e-4 m/s, and SFM and wall sliding friction dissipate and vanish at rest, so C2 has C1's fixed points and stability.
- ORCA is not rest-vanishing (rest drive m·v0/τ_ORCA).
- E2 evidence: C2 = C1 in 360/360 paired runs.
- The walls.py docstring sign of the wall friction is corrected; the code was already right.
C20 (2026-11-08) Replay test reading: 1e-9 m replays test sensitivity, not randomness.
- RVO2 ORCA and every other deterministic arm reproduce exactly (300/300).
- The published LP flips the outcome in 5/300 (second trap, slow creep, Δt up to 81 s). This is reported as ill-conditioning of that implementation (class N, consistent with its pair-class defect).
- Forward claims use RVO2.
C21 (2026-11-08) E2 is reported per stratum.
- At the lone keystone, ORCA frees through its rest drive (drive only = C3 RVO2 = C3 published, 0:0).
- At the second trap, full ORCA frees fewer than its drive alone (17/26 vs 24/26, 7:0), so the constraint part acts against the drive when a trapped neighbour is present. This is diagnosed in batch 4.
C22 (2026-11-08) End of the queue.
- Agents that can pass alone leave first: the stuck-alone fraction rises 0.20 → 0.62 over arrival deciles, and the blocker is among the last 3 arrivals in 184/196.
- A stuck-alone agent is pushed through by whoever is still present, passable or not; the number still active is the best predictor (AUC 0.975).
- This replaces the passable-pusher reading.
C24 (2026-11-08) Hero (Fig 1) redesign, superseding the C17 layout (C17's encodings stand). "Two traps, two tilts", 2 × 2:
- the lone-trap scene, with its energy ribbon along the door axis: own drive vs ORCA's added drive, plus a thermal band at k_BT_eff;
- the pair scene, with its ribbon along the soft lateral mode: no tilt vs tilted past the fold;
- force arrows to scale; a context inset of the whole room; scientific-realism rendering; no dotted or dashed elements.
Fig 1 is the only figure with in-figure text: short labels of 1-2 words set in the paper's serif by LaTeX/TikZ over the render, plus scale bars. Figs 2-8 stay label-free. Final render only after Palaash approves a 900 px mock.
C25 (2026-11-08) Fig 2 fixes:
- the x range trimmed to the region with data;
- the margin heat map lightened, with dark population points;
- the C3 rest-state band drawn as two blue boundary lines without fill.
