# HANDOFF: execution phase for the LNNS extended paper (self-contained; matches Plan v1)

Read this first if you are a new session with no prior context.

**The governing document is plan/FINAL_PLAN.md, "Plan v1: first draft, frozen".** It changes only through the dated change log at its end. Where this handoff and Plan v1 disagree, Plan v1 wins; record any needed change in its change log.

The project is an invited extended version, for Springer Lecture Notes in Networks and Systems, of:
- Gang, P. and Veluri, A. (2026), "A Diagnostic Methodology for Failure-Mode Ablation of SFM, TTC, and ORCA Pedestrian Steering Paradigms", SIMULTECH 2026, pp. 474–481, DOI 10.5220/0015190200004094;
- PDF at ref/camera_ready_SIMULTECH2026.pdf.

Working title: **"One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models"**.

Thesis: matching a control to a paradigm's headline score is not evidence that the two share a mechanism; physics-derived held-out signatures decide the question, and in two deadlock classes they show that the same headline score hides different mechanisms.

The execution phase has three jobs:
- run the production experiments (§5);
- make the 7 figures and the data for the 4 tables (§7);
- support the authors in writing.

The authors write the text. Do not generate scientific claims or interpretations the authors have not made.

Plan root (all paths relative to it): **/Users/palaash/Developer/pedestrian-abs-plan**.

## 1. Where everything lives

| What | Path | Notes |
|---|---|---|
| Simulator code (git clone) | pedestrian-abs/ | Branches: main = published code (HEAD e05d8f6, untouched); plan-scan (= main); plan-wave2 (flagged variants); **plan-wave2b** (current: + B_w_edge flag, CroMa scenario, corridor-end tagging e75af1f). Remote push is disabled. Never push. Make the execution branch from plan-wave2b. |
| Plan-root repo | . (git) | scan/, wave2/, wave2b/, plan/. Commits only; never push. lit/ and data_ext/ are gitignored. Tag plan-v1 marks Plan v1. |
| Plan v1 | plan/FINAL_PLAN.md | venue frame, title, thesis, contributions, outline and pages, model in both modes, T1–T5, protocol and signatures S1–S9g, figures and tables, experiments in priority order, risks, decisions, change log, reconciliation notes |
| Short summary | plan/PLAN_V1_SUMMARY.md | ≤ 80 lines |
| Table 4 source | plan/CORRECTIONS_TABLE.md | conference claims: confirmed / revised / withdrawn / pending, with evidence |
| Differences statement source | plan/DIFFERENCES_POINTS.md | factual bullets for the short "main differences" statement |
| Decisions | plan/DECISIONS_OPEN.md | resolved items, and the pending T1–T5 sign-offs |
| Wave 1 static audit | scan/ (CODE_FACTS.md, CLAIMS_LEDGER.md, PROBES.md, FEASIBILITY.md) | file:line facts about the published code |
| Wave 2 probes | wave2/ (WAVE2_REPORT.md, SIGNATURES.md, COMPUTE_PLAN.md, CODE_CHANGES.md, scripts/, data/) | lone-trap library: wave2/data/library/C1_w0.8_seed*.pkl (99 published-mode snapshots) and w25_*_seed*.pkl |
| Wave 2b probes | wave2b/ (WAVE2B_REPORT.md, CODE_CHANGES.md, PROGRESS.md, scripts/, data/) | pair library: wave2/data/library/w25_B0.04_seed*.pkl + wave2b/data/library/a1_B0.04_seed*.pkl; list in wave2b/data/a4_selected_snaps.txt (26 pairs) |
| Literature | lit/OUT/ (FINAL_REPORT.md, NOVELTY_MATRIX.md, VENUE_NOTES.md, DATA_SOURCES.md, references.bib) | read-only; references.bib holds fetched entries only (178), each with its source comment |
| Human data | data_ext/croma/txt/ (CroMa 2021, DOI 10.34735/ped.2021.9, CC BY 4.0) | 0.8 m runs: 4D030, 4D040 (L = 2.0 m), 4D110, 4D120, 4D130 (L = 0.21 m) |
| Python | .venv/ (Python 3.13.12, numpy 2.4.4, scipy 1.17.1, shapely 2.1.2, statsmodels 0.14.6; no lifelines; no network for pip) | run as `.venv/bin/python` |

Machine: Apple Silicon, 8 physical cores, 8 GB RAM. Use **4 workers** at most (≈ 150 MB per worker; the cap is memory). "Larger machine" means a 16–32-core box.

## 2. Reproduce the regression hash (before and after every code change)
```sh
cd /Users/palaash/Developer/pedestrian-abs-plan
git -C pedestrian-abs checkout plan-wave2b      # or the execution branch made from it
.venv/bin/python wave2/scripts/regress.py       # must print: e381b49dc24acccd OK
```
- The check runs C1, seed 42, w = 0.8, 100 agents, 500 steps, all flags default, and hashes positions, velocities and active flags (scan/probes/common.py:64).
- Test suite: `cd pedestrian-abs && ../.venv/bin/python -m pytest -q` gives 115/120. The 5 failures are known cross-platform bit-identity tests (≈ 1.6e-6 relative) and are not regressions.
- Rule: every new behaviour goes behind a flag whose default reproduces published behaviour. Log each change in a CODE_CHANGES.md and re-run regress.py.

## 3. The job runner
wave2/scripts/w2lib.py provides:
- `build(config, seed, width, n_agents, noise, flags)`: a fresh bottleneck simulation. Flags are `param_overrides` keys plus the scenario keys spawn / edge / edge_radius / speed_mean.
- `snapshot(sim)` / `restore(snap, config, flags, noise, noise_seed, dt)`: freeze a state, then restart it under any arm. restore() drops the snapshot's w2_*, A_w and B_w params and re-applies the arm's flags, so re-pass the wall/numerics flags for each arm.
- `run_jobs(jobs, fn, out_path, workers=4)`: multiprocessing pool, one JSON line per job. Done `job_id`s are skipped, so **re-running the same command resumes after a crash**.
- `StationaryDetector` (deadlock = all |v| < 0.01 m/s for 10 s, no exit), `Passability` (rest-state stuck-alone margins), `wilson`.

Patterns to copy:
- whole runs: wave2/scripts/w21_library.py `run`;
- quench arms: wave2/scripts/w22_quench.py `run`, wave2b/scripts/a4_quench.py, a6_extra.py;
- escape restarts: w23_escape.py; barriers (string method): w23_barrier.py;
- Hessian: wave2b/scripts/a3_pair_stability.py; static fold prediction: wave2b/scripts/a5_predict.py;
- open geometries: w26_w27_open.py;
- CroMa: wave2b/scripts/b2_croma_pilot.py; human estimator wave2/scripts/w28_croma.py (run with `python -I`, data paths as arguments).

Wave 2b imports w2lib through wave2b/scripts/w2blib.py, which adds DATA2B and the corrected-forward flag dict CF.

Use `w2_metrics=light` (2.6× faster, dynamics unchanged). Stream outputs to disk; stop deterministic runs at stationarity.

## 4. The two model modes (full declaration in plan/FINAL_PLAN.md §7)

| Mode | Flags | Use |
|---|---|---|
| published-reproduction | all defaults: numerics = published, spawn = uniform, orca = published, **C4 crush present (declared)**, wall corners = segment sum | explaining published numbers; Table 4 |
| corrected-forward | `w2_numerics=fixed`, `spawn=rejection`, `w2_orca=rvo2`, **C4 crush OFF**, **corner rule = union** (walls sharing an end use the nearest point on the union of walls; a shared end counted once) | every forward claim |

**New flags to implement in execution (default-off, i.e. default = published behaviour):**

| Flag (proposed name) | Values | Needed before |
|---|---|---|
| `w2_crush` | on (default) / off | E8, E9 (C4 arms) |
| `w2_wall_corner` | segment_sum (default) / union | E10 (CroMa geometry; the door edge is a shared wall end there, which doubles the edge force: 311 N vs 156 N at r = 0.25 m, wave2b/WAVE2B_REPORT.md B2) |

Implement each on the execution branch, run regress.py, log it, and record the final flag names in the Plan v1 change log.

Existing flags (all default-off):

| Flag | Values / effect |
|---|---|
| `w2_orca_split` | drive_only, constraint_only, frozen_mean |
| `w2_orca_transform` | reverse_parallel, reverse_lateral (confounded; not pre-registered) |
| `w2_noise` | dt_scaled, lateral_bias (+ `w2_bias_b`), off |
| `w2_goal` | line |
| `A_w`, `B_w` | all walls |
| `B_w_edge` | jambs only |
| scenario `edge` | rounded |
| `speed_mean` | scenario mean desired speed |

Scenarios: room bottleneck (bottleneck.py); open geometries (sim/scenarios/open_geometries.py); `CromaBottleneckScenario` (sim/scenarios/croma.py). Noise is set by assigning `sim.velocity_noise_std = σ`. ORCA: report both "as implemented" (orca = published) and RVO2-faithful (orca = rvo2); forward claims use rvo2.

## 5. Production experiments in priority order (details in plan/FINAL_PLAN.md §11)

| Priority | E | Contents | n | CPU-h | Machine | Feeds |
|---|---|---|---|---|---|---|
| 1 | E1 | lone-trap library, both modes; leave-one-seed-out validation of the k = 3 rule (accuracy and AUC) | 200 seeds per mode | 4.6 | Mac | Fig 1, Fig 2 |
| 2 | E2 | quench signatures on 60 CF snapshots, all arms | 60 | 4 | Mac | Fig 5, Table 3 |
| 2 | E3 | Δt scaling (per-step σ, √Δt-scaled σ, C3 rvo2) | 20 snapshots × 20 restarts | 7 | Mac | Fig 4, Table 3 |
| 3 | E4 | escape distributions and string-method barriers | ≥ 105 events per condition | 4.5 | Mac | Fig 3 |
| 4 | E5 | large-n σ-sweep (σ50), both modes | 100 per σ | 36 | Mac | Table 3 / text |
| 4 | E6 | matched completion C1 + σ* vs C3, orca = rvo2 | 186 per arm | 23.8 | Mac | Table 3 |
| 4 | E6p | published-ORCA version | reduced n = 50 | 30 | larger machine preferred | Table 3, Table 4 |
| 5 | E7 | wall-model validity cells, jamb-only included (10 cells) | 100 per cell | 15 | Mac | Fig 2 |
| 6 | E7b | pair class: library to ≥ 40 pairs; constraint_only with the RVO2 linear program (and published LP); pair string-method barrier; fit matched bias b* and test on the signatures | ≥ 40 snapshots | ≤ 9.3 | Mac | Fig 6, Table 3 |
| 7 | E10 | CroMa geometry; corner rule fixed (union) in the corrected mode | 25 per cell | ≤ 8 | Mac | Fig 7 |
| 8 | E8 | open counterflow, inflow sweep (lower priority) | 25 per arm per density | 26 | Mac | Table 4 only |
| 8 | E9 | open crossing, inflow sweep (lower priority) | 25 per arm per level | 24 | Mac | Table 4 only |
| 8 | E11 | persistence-filtered throat-overlap rerun (lower priority) | 25 per cell | ≈ 6 | Mac | Table 4 only |

- **No FD experiment.** The FD calibration is dropped. Its cause (grouping by frame number across concatenated runs: sim/data/fundamental_diagram.py:29 with sim/data/loader.py:109-120) is a Table 4 row.
- **No E12** (room-geometry estimator on model logs): the like-for-like CroMa geometry (E10) replaces it.
- Total ≈ 198 CPU-h upper bound; ≈ 168 without E6p (≈ 42 h wall on 4 workers, about 6 overnight batches).
- Run each experiment as its own script with a resumable JSONL output. Before each batch append a line to a PROGRESS.md (task, command, start, status). After each batch commit (plan-root repo for scripts/data/docs; code on the execution branch).
- Every reported number carries: script, seeds, flags, dt, duration, wall time, and a VERIFIED / INFERRED / UNKNOWN label.

## 6. Signatures and margins (pre-registered; full table in plan/FINAL_PLAN.md §9)
Lone trap (60 snapshots unless stated):
- **S1 Δt scaling:** per-snapshot ln λ(0.005)/λ(0.02). dt_scaled and C3 equivalent to 0 within ±ln 1.5 (TOST); per_step one-sided > 0, slope 1 ± 0.3. 20 snapshots × 20 restarts.
- **S2 seed replay:** deterministic arms D = 0 exactly; noise D > 0. 60 × 5.
- **S3 frozen-mean ±:** exact McNemar, + > −; + vs C3 rvo2 paired TOST ±0.10.
- **S4 drive/constraint split:** drive_only ≡ C3, constraint_only ≡ C1 within ±0.10 paired TOST.
- **S5 failure identity:** AUC lower bound ≥ 0.80; Jaccard reported, not read as mechanism.
- **S6 escape shape:** Weibull ln k within ±ln 1.25; ≥ 105 events per condition.
- **S7 matched completion:** TOST ±0.15, n = 186 per arm (calibration target only).
- **S8 lateral bias at the lone trap:** negative control; upper Wilson bound ≤ 0.10.

Pair class (≥ 40 snapshots):
- **S9a** fold prediction agreement, lower Wilson bound ≥ 0.90;
- **S9b** no infinitesimal breaking, upper Wilson bound ≤ 0.10;
- **S9c** C3 published vs rvo2, exact McNemar;
- **S9d** constraint_only (both LPs) vs C1; drive_only vs C3 rvo2;
- **S9e** handedness of the first member out, flip under b → −b;
- **S9f** thermal escape, Arrhenius slope within ±25% of the pair barrier;
- **S9g** matched bias b* (fitted to C3 rvo2 and to C3 published on rate, paired TOST ±0.10), tested on failure identity, handedness, reversal and seed replay.

Statistics allowed: Wilson CIs; Kaplan–Meier with censoring; exponential/Weibull hazards; paired TOST; exact McNemar; LOSO accuracy and AUC. Not allowed: unpenalised Cox with a zero-event arm; global multiplicity families presented as per-family.

## 7. Figures (exactly 7) and tables (exactly 4)
Style:
- plain data figures: **axis labels only**; every series and any other annotation identified in the caption, nothing inside the figure (no legends, titles, panel letters or text); panels named by position in the caption;
- vector PDF at LNCS text width (12.2 cm; half 5.9 cm);
- one colour-blind-safe palette (Okabe–Ito, fixed arm → colour mapping, plan/FINAL_PLAN.md §10) and one font style (document serif 8 pt) throughout; one style file figures/style.mplstyle;
- every figure regenerated from new runs; none of the conference figures is reused or redrawn. A figure showing a conference quantity cites the conference paper in its caption.

Figures:
1. Lone-trap physics: backward door-edge force vs position for several radii, against the C1 and C3 drives; stuck-alone region in the (r, v0/τ) plane over the spawned population (E1).
2. Completion against exit width and wall-range variants incl. jamb-only, Wilson CIs (E7, E1).
3. Noise as collective escape: Kaplan–Meier curves; Arrhenius plot for full / blocker alone / frozen neighbours with barrier-predicted slopes (E4).
4. Δt signature: escape hazard vs Δt for per-step σ, √Δt-scaled σ and ORCA (E3).
5. Lone-trap quench outcomes for every intervention, with time-to-free (E2).
6. Pair class: fraction freed vs bias with the static fold prediction; pair outcomes per intervention (E7b).
7. Human validity: CroMa vs each model variant: flow, longest gap, fluctuation level (E10).

Tables:
1. Parameters and the two model modes.
2. Mechanism classes, controls and pre-registered signatures (statistic, margin, n, decision rule).
3. Matched-control results for both classes: rate match plus signature tests; σ-sweep summary here or in the text.
4. Conference claims and their status (confirmed / revised / withdrawn), each with evidence (source: plan/CORRECTIONS_TABLE.md).

## 8. Table 4 and the relation to the conference paper
- The paper is about the new work and builds on the conference paper's audit principle, which it cites. Revisions of conference findings are stated plainly and compactly in Table 4 plus one short paragraph (paper §6.3). They are not a theme of the paper.
- **No correction notice** to the proceedings will be pursued.
- Production results fill the "pending" rows of plan/CORRECTIONS_TABLE.md.
- Platform wording (D2): the published 0/25 and 13/25 are n = 25 single-platform realisations that the published code reproduces on macOS; the Windows draws (1/25, 7/25) go in a footnote. Lead with the large-n estimates.

## 9. Invitation requirements (LNNS)
- **Template:** LNCS (Springer llncs). **Fetch it from Springer; never generate or reconstruct the class or its files.**
- **Length: 23–25 pages INCLUDING references.** Outline: about 24 pages (plan/FINAL_PLAN.md §6).
- **New material:** at least 30%; the plan targets well over 70% (worst-case count ≥ 73%).
- Conference paper cited in the text and the references.
- Every table or figure taken from the conference paper regenerated, citing its source.
- No large verbatim blocks; different title, abstract and conclusions.
- A short statement of the main differences (plan/DIFFERENCES_POINTS.md).
- Submission through **PRIMORIS**, with the **Licence to Publish**.
- The deadline is not recorded in the repo; take it from the invitation.

## 10. References and disclosures
- lit/OUT/references.bib holds **fetched entries only**. Never write BibTeX from memory. New references are fetched from a primary source (Crossref/DOI, publisher, arXiv) and annotated with that source. Never generate licences, LaTeX class files or published tables.
- To fetch later: Wilson (1927) score interval; McNemar (1947); the LNCS template; PRIMORIS instructions and the Licence to Publish form.
- Disclosure wording and the copyright form are handled at the writing stage by the authors (resolved decision).
- Git identity is preset (Palaash Gang / palaashgang@gmail.com); do not change it. Commits carry no co-author trailers and no tool attributions. Never push.

## 11. Decisions (plan/DECISIONS_OPEN.md)
- **Resolved:** the second author agrees to every change; no correction notice; disclosure and copyright form at the writing stage; a new GitHub execution repo later (separate and secondary); page target 23–25 including references; D1–D8 as previously applied.
- **Applied:** pair class as a secondary strand (≈ 3 pages); FD claims dropped; crush declared in published mode and off in corrected mode; corner rule (union nearest point, no double counting) in corrected mode.
- **Pending [NEEDS PALAASH]:** derivation sign-offs T1 (rest-state lemma, dissipative form), T2 (stuck-alone criterion and k = 3), T3 (T_eff = m·σ²/(1 − (1 − dt/τ)²)), T4 (collective Kramers escape over string-method barriers), T5 (pair Hessian and fold). None blocks E1–E4.

## 12. Key pilot results (for orientation; production runs replace them)
- **Lone trap (published regime):** C1 1/100 complete at w = 0.8 [0.002, 0.054]; 96/99 blockers stuck alone; k = 3 rule 96.4%. Stuck-alone fraction 0.233 / 0.018 / 0 at w = 0.8 / 0.9 / 1.0 (wave2/data/w21_analysis.json).
- **ORCA = drive (L):** drive_only 23/40 = C3 23/40; constraint_only 0/40; frozen + 25/40, − 0/40; deterministic; Δt-flat (wave2/data/w22_analysis.json, w23_analysis.json).
- **Noise = collective activated escape (T):** T_eff within ≈ 2%; collective barriers 0.3–9.6 J vs 10.7–44.8 J alone; per-step Δt hazard ratio 2.3×, dt-scaled 0.85× (wave2/data/w23_analysis.json, w23_barrier.json).
- **Jamb law:** B_w = 0.04 all walls 167/200 complete; jamb-only 21/25; no lone traps; pair standoffs at the jamb faces (13% of runs).
- **Pair class (26 pairs):** strict minima 26/26 (softest mode common lateral shift, 48–129 N/m); bias frees past a fold (b ≳ 0.03; static prediction 182/182); δ ≤ 1 cm frees none; constraint_only 26/26; C3 published 10/26 vs C3 rvo2 1/26 (9:0, p = 0.004); noise frees almost all (ΔU_eff ≈ 0.8 J). Bias b = 0.02 matches C3 published on rate (9 vs 10/26) but differs on failure identity (Jaccard 0.27), first member (9/9 vs 2/10) and reversal (wave2b/data/a5_analysis.json).
- **No persistent contact arches** (wave2/data/w29_contact.jsonl).
- **Open geometries:** no ORCA counterflow gridlock (n = 3); no TTC crossing gain, 0.94 [0.59, 1.28] (n = 10).
- **CroMa 0.8 m:** humans 1.15–1.71 passages/s, longest gap ≤ 2.04 s, fluctuation 0.072–0.079 / 0.070–0.078 m/s. CroMa-geometry pilot (σ = 0, n = 5 per cell; wave2b/data/b2_analysis.json):

  | cell | complete | flow (/s) | gaps > 2 s | longest gap (s) |
  |---|---|---|---|---|
  | published | 0/5 | 0.68–0.84 | 7–23 | 4.3–10.0 |
  | corrected-forward (segment sum) | 0/5 | 0.62–0.78 | 9–21 | 4.3–15.4 |
  | CF + jamb-only B_w_edge = 0.04 | 5/5 | 0.72–0.78 | 13–19 | 6.9–9.9 |
  | C3 rvo2 | 0/5 at 600 s | 0.68–0.92 | 5–17 | 3.0–15.2 |
