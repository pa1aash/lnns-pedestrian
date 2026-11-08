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
C23 (2026-11-08) Queue 2.
- After E5a the queue runs E7b_static, E7b_quench, E7b_barrier, E6a, E6b, E10, E7, E11, E8, E9, E6p (≈108 CPU-h).
- E7b uses the 46 fresh CF ∪ {B_w = 0.04} pair snapshots (E7b_lib, seeds 242-561). The common lateral displacement shifts both members by +δ in y. The pair barrier is the lower of the two gated exit channels, on 12 snapshots spread over λ1.
- σ* is the inverse of a binomial-logit fit of E5b completion at E6a's rate, with no extrapolation outside σ ∈ [0.03, 0.07] m/s. It is fixed in data/derived/sigma_star.json and used by E6b and E10.
- The E8/E9 inflow sweep is a start-density sweep at fixed n, by the length of the start blocks (E8 1.39/0.93/0.56 m⁻²; E9 1.96/1.33/0.98 m⁻²; the densest level is the pilot geometry), with 60 s windows.
- The published-LP infeasibility is counted as dropped constraints (a half-plane violated by the returned velocity).
C26 (2026-11-09) Second trap is pair-like. When the blocker has exactly one trapped neighbour beside it at the jamb, ORCA's constraint part builds up against the door-ward drive once motion starts (mean 27% cancellation, up to ~100% in held cases), and C3 RVO2 frees 2/10 such snapshots against 15/16 with two or more neighbours. Reported with the pair class (§6.1, §6.2).
C27 (2026-11-09) E8/E9 sweep the initial density at fixed agent number over a 60 s window; the paper calls it initial density, not inflow. Results feed Table 4 only.
C28 (2026-11-09) Pair displacement arms shift both members by +δ (the common, soft lateral mode).
C29 (2026-11-09) E4 seed170 (full-condition barrier 0.13 J, gate passed, 0/60 escapes in 300 s) is reported as a case where the computed minimum-energy path is not the dynamical escape route. It is excluded from the Arrhenius fits and listed.
C30 (2026-11-09) T3 signed: k_BT_eff = m·σ²/(1 − (1 − Δt/τ)²); realised/formula velocity variance 1.00 (0.99 over 207 cells); harmonic correction ≤ 0.3%. T4 signed: collective escape over string-method barriers; Arrhenius slope/barrier CIs cover 1 in 25/28 fits (the 3 others listed); collapse slope −0.93; Weibull k = 1.09; conservative-field residual ~5e-8 N. The E3 β_ref = 2.5 shortfall (ℓ 3.23 vs 3.70; overall slope 0.91 [0.83, 1.01]) is reported with its CI; no extra arm.
C31 (2026-11-09) Session rules: commit your own edits before any pull; never leave tracked edits uncommitted; pushes run with pipefail.
C32 (2026-11-09) Hero mock v2 (supersedes the C24 label list):
- labels at 6.5 pt, 17 in total; "door", "tilt" (with its arrow), "partner" and "10 m" removed;
- the floor force ramp fades to a neutral off-white below about 5 N and contains no yellow hues, so it cannot be confused with the held-alone agent or the lateral-bias colour; one background across the figure;
- wall-overlap mask regions are rendered as plain floor;
- thinner arrows (about 0.6 pt); the neighbours' push as a short unlabelled neutral-grey arrow;
- one scale-bar cluster in the lone scene, with the same metre and force scale in both scenes;
- the caption lives in figures/fig1_caption.tex, owned by the hero sessions.
C33 (2026-11-09) Single-file submission: section files are kept for drafting; `make submission` builds paper/submission/ with one self-contained main.tex (all \input files and the compiled bibliography inlined), the figures, and the unmodified llncs.cls and splncs04.bst. The folder compiles on its own.
C34 (2026-11-09) Hero final:
- both lone ribbons show the blocker's rest-state energy along the door axis with the neighbours pinned, so they differ only by ORCA's added drive; the own-drive minimum sits at the frozen position;
- the alone barrier (27.96 J) is the one quoted for the stuck-alone test;
- the lone-scene arrows are stacked drive → push → ORCA against the wall force;
- the two scenes share framing; the scale bars are separated.
C35 (2026-11-09) Page plan: target 24 pages including references.
- References trimmed to the citations that each support a specific claim (target ≤ 2.2 pages).
- §3 and §4 tightened to 2.5 pages each: equations kept; parameter detail moved to Table 1; derivations compact.
- A final page pass follows once every section exists.
C36 (2026-11-09) σ50 in published mode (E5a, n = 100 per level) is 0.045 [0.042, 0.047] m/s, equal to corrected mode (0.044 [0.041, 0.047]). The conference value 0.049 (n = 25) lies outside both intervals; this is a revised row of Table 4.
C37 (2026-11-09) The refs.bib entry nicolas2018trap had its accented initial re-encoded (Á → {\'A}) because BibTeX truncated the byte. No bibliographic content was changed; noted in the entry's source comment. latexpand (TeX Live script) lives in ~/Library/texmf/scripts and is listed as a build requirement in README.md.

C38 (2026-11-09) Field-residual wording, superseding the "~5e-8 N" of C30: max |F_code + ∇U| is 4.9e-7 N with all agents mobile (median about 5e-8 N), 4e-8 N with neighbours pinned, and 1e-7 N over the 46 pair snapshots (data/derived/field_residuals.json).
C39 (2026-11-09) Citations restored: the crowd-disaster sources in the opening sentence (liang2024, helbing2012) and koster2013 where the dependence of results on the integration scheme motivates the corrected-forward mode.
C40 (2026-11-09) p-values print as plain decimals for p ≥ 0.01 and in scientific notation below.
C41 (2026-11-09) Matched noise σ* = 0.0467 m/s, from inverting the corrected-mode E5b completion fit at E6a's C3 RVO2 completion rate (data/derived/sigma_star.json).
C42 (2026-11-09) The numbers registry is split into per-topic files under paper/registry/; make_numbers rejects duplicate macro names.
C43 (2026-11-09) Hero polish: the caption states that white next to the walls marks positions an agent centre cannot occupy; the floor field's boundary at that zone is anti-aliased (floor panels re-rendered only).
C44 (2026-11-09) Pair-class matched bias: per plan §9, b*_pub = 0.0223 (C3 published) and b*_RVO2 = 0.0091 (C3 RVO2), fitted on rate from the bisected static fold thresholds (the b grid was too coarse) and tested held-out at ±b* (data/E7b_bstar). Matched on rate (22 vs 21, 8 vs 7; equivalence ±0.10 not shown at n = 46); separated on identity (Jaccard 0.43; RVO2 sets disjoint) and handedness (22/22 vs 11/21).
C45 (2026-11-09) Pair-class deviations: S9b δ = 1 cm upper bound 0.113 (pooled 1 mm + 1 cm passes); S9f Arrhenius not testable (ΔU/k_BT_eff < 1, Weibull k 2.3–2.8), so noise at the pair is reported descriptively, not as class T.
C46 (2026-11-09) C26 confirmed with E7b: same geometry and the same constraint cancellation (0.27 vs 0.26); a blocker with one trapped neighbour is a pair standoff.
C47 (2026-11-09) E6 is reported as the whole-run instance of the thesis: matched on completion (Δ -0.01 [-0.10, 0.08]), separated on failure identity (Jaccard 0.41), completion time (64/64 seeds faster under C3 RVO2) and final-state class (p = 0.0014). The keystone classes come from surgery on final states rebuilt from the saved residual positions.
C48 (2026-11-09) Noise stall lifetimes in whole runs are compared with a no-fit prediction from the gated library barriers, kT_eff(σ*) and the E4 attempt rate (agreement within 0.05 in survival).
C49 (2026-11-09) §5.3 rests on a production high-drive run (25 seeds, 600 s, v0 = 5 m/s), replacing the W2.9 pilot as the source.
C50 (2026-11-09) E10 fluctuation is the waiting-zone *velocity* fluctuation of the unchanged W2.8 estimator (RMS over the two components); the prompt's "density fluctuation" is not what the estimator measures.
C51 T5 signed (2026-11-09): the pair standoff is a strict minimum of the rest-state energy with density frozen (46/46 positive-definite Hessians; softest mode the common lateral shift in 46/46); the bias threshold is a fold (static prediction matches the quench in 363/368; all 5 misses within 1-2% of the threshold); field residual 1e-7 N.
C52 Data policy (2026-11-09): raw trajectory files (data/E10/raw/, about 430 MB) are not committed. All raw data are archived on Zenodo at submission, and the DOI goes in the data and code availability statement. Per-run results stay in the repository.
C53 Table 3 restructure (2026-11-09): Table 3 is the thesis table, about half a page: three matched-control blocks (lone-trap snapshots: noise σ vs ORCA; whole runs: C1 + σ* vs C3 RVO2; pair: bias b* vs ORCA, per solver) against the signatures that separate them (rate, identity, time to free, handedness, replay, Δt). Rows duplicating Figs 4-5 (E3/E4) are dropped.
C54 Page plan (2026-11-09): target 24 pages including references. Indicative budgets: §1 1.8 (with Fig 1), §2 1.4, §3 2.5, §4 2.5, §5 3.8 (Figs 2-4), §6 4.5 (Figs 5-7, Tables 3-4), §7 1.9 (Fig 8), §8 1.0, §9 0.4, back matter 0.5, references 1.9, front matter 0.5.
C55 Worktree rule (2026-11-09): each session edits only its own git worktree and pushes to main by fetch/rebase; the main folder is left to the experiment queue.
C56 (2026-11-09) Table 3 overlap: J is computed on the minority outcome set of each block (the unresolved sets for the lone-trap and whole-run blocks, the freed sets for the pair block); the rule is stated once in §6.
C57 (2026-11-09) All intervals in the paper are 95%; the 90% interval of the pair block (from the internal equivalence margin) is replaced.
C58 (2026-11-09) Figure captions sit below their figures (LNCS guidelines); Fig 5's side caption is reverted.
C59 (2026-11-09) §6 may run about 0.3 page over its budget until the final page pass.
C60 (2026-11-09) Fig 3 and the section 5.1 paragraph now report E7. Critical width at default walls is 0.88 m; the trap disappears with a short-range jamb wall law (B_w 0.04 m or 0.02 m, all walls or jambs only: 83-89% completion against 2%), is unchanged by rounded corners or a line goal (3-9%), and its residual deadlocks are collective pair standoffs (42 of 43) instead of lone traps. The wall-model assumption is therefore a first-order driver of the corrected-forward deadlock rate.
C61 (2026-11-09) Prose standard: plan/PROSE_STANDARD.md (the authors' audit prompt) governs all drafting and fixing from now on.
C62 (2026-11-09) Table 3: the RVO2 pair row prints its freed-set overlap as '0 (disjoint)'.
C63 (2026-11-09) Framing: the critical width (0.88 m) holds for the default wall law; the jamb's wall range is the lever that sets both the trap and the deadlock class (lone traps under default walls, pair standoffs under short-range jambs).
C64 (2026-11-09) Table 4 verdicts: each conference claim is judged on the model the conference used, published ORCA (the published LP) in the corrected, leak-free geometry; RVO2 is reported beside it as the solver check, and the row says when the two disagree. Table 4 tests the conference's own claims; the RVO2 rule (C20) governs this paper's forward claims, not the audit of the earlier ones. Applied to every Table 4 row (open corridor, open crossing, throat overlaps, published ORCA whole runs; the ORCA-mechanism row now cites the published solver).
