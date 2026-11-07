# Batch 2A report (2026-11-08)

**Import.** Simulator from pedestrian-abs exec-v1 (8b29429) → `code/` (31d3f35; 576 of 582 files). Not imported: `inventory.md`, three working notes under `revision-notes/` and a `.DS_Store`. One editor configuration file and 7 lines (comments, docstrings, one ignore entry, one printed message) that referred to local tooling were not imported; no simulation code was affected.
Experiment library `experiments/lib/` (w2lib, w2blib with full CF, e1lib, common, runlib). Data → `data/E1`, `data/derived`, `data/pilot` (132 pilot snapshots; absolute paths in the pilot selection lists rewritten to repo-relative). E1_runs.jsonl is 17 MB, so not gzipped (the loader reads `.gz` too). `e1_analyze.py` on the imported data reproduces E1_analysis.json: every number equal (only the doc and script path strings differ).

**Checks.** `make -C experiments regress` → `e381b49dc24acccd OK` (before and after; `code/` unchanged since import). pytest on the Mac: 128 passed, 5 failed (the known bit-identity tests). CI `tests` workflow (ubuntu, Python 3.13, the venv's package versions, the 5 tests deselected by node id with a comment): **green**, 128 passed / 5 deselected. The first run failed only because pyarrow was missing; that is fixed.

**Keystone test** (C12; `experiments/E1/keystone.py`, 393 snapshots, about 5 min wall). [Wilson 95%]
| class | E1a (n = 197) | E1b (n = 196) |
|---|---|---|
| lone keystone | 38, 19.3% [14.4, 25.4] | 34, 17.3% [12.7, 23.3] |
| lone keystone + second trap | 154, 78.2% [71.9, 83.4] | 160, 81.6% [75.6, 86.4] |
| collective | 5, 2.5% [1.1, 5.8] | 2, 1.0% [0.3, 3.6] |
Second trap, K1 repeated on the next-nearest held agent: held 145/154 (E1a), 151/160 (E1b). Every blocker held in K1 stopped by the stationary rule (no blocker was still moving at 120 s).
**The 7 negative-margin blockers are exactly the 7 collective cases.** All 7 are freed when alone, in 3.1–4.5 s. Each is a jamb-face pair standoff: a passable blocker (margin −3.7 to −43 N) at |y−5| = 0.40–0.45 m, x ≈ 9.55 m, and a stuck-alone partner on the opposite jamb face (margin +52 to +418 N), surface gap 0.23–0.32 m. When the blocker is removed (K2) the partner stays held. E1a seed 156 also has two lateral agents. Every positive-margin blocker (386/386) is held when alone.

**End-of-queue rule, refined** (k = 3; C13), E1a / E1b:
- all-exit baseline: 93.2% (4179/4486) / 93.1% (4155/4465);
- rule accuracy: 96.2% / 96.2% (held-out LOSO 96.2% / 96.2%);
- errors: 170 / 168. Final blockers predicted to exit: 110 / 101. Queued agents predicted to exit: 38 / 50. Exited agents predicted stuck: 22 / 17.
- final blockers predicted correctly: 82/192 / 93/194;
- restricted to blockers + exited agents: 97.0% (n = 4371; baseline 95.6%) / 97.3% (n = 4349; baseline 95.5%);
- **AUC (headline): 0.974 [0.968, 0.979] / 0.975 [0.970, 0.979].**
- The contact-cluster type counts are gone from the summary. The raw field is marked superseded in E1_analysis.json and data/E1/README.md.
These are inputs to the T2 sign-off, which is pending with Palaash [NEEDS PALAASH].

**Selection** (`experiments/selection.py`, data/derived/selection.json).
- E2: the E1b lone-keystone pool has **34 < 60**, so all 34 are taken. Residual counts: 1 agent in 24, 2 in 7, 3 in 2, 4 in 1.
- BAR, E3 and E4 come from the queue: step SEL_E3E4 runs straight after BAR. The ΔU distribution of the E2 set is not available yet. Smoke-test barriers on 4 snapshots: collective ΔU = 23.4, 11.4, 16.6, 0.8 J. Force-check residuals were 1.6e-8 to 1.6e-7 N (pilot ≤ 2e-7).
- Pair library provenance: the pilot's 26 pair snapshots carry only {w2_numerics=fixed, spawn=rejection, B_w=0.04}, with no w2_orca, w2_crush or w2_wall_corner, and were built on the pre-exec branch. So they are not exactly CF ∪ {B_w: 0.04}. **All 40 are built fresh under CF ∪ {B_w: 0.04}** (seeds 242–641); the pilot pairs are kept as reference only. Qualification uses the pilot rule (deadlock at rest with n_remaining = 2) plus the stated checks: in front of the jamb faces on opposite sides, contact-free, each member passes alone.

**Smoke tests** (all steps run with no errors, resume skip verified; scratch output deleted). Throughput: restarts about 24 sim-s per wall-s at dt = 0.01 (12 at dt = 0.005); whole 100-agent runs about 5.5 sim-s per wall-s; BAR 1–2.3 min per snapshot.
Estimated CPU-h: E2 2.5 · BAR 1 · E3 12 · E4 12 (up to about 19 if extended to 60 restarts) · E5b 11 · E7b_lib 4.5 · E5a 18 · E7 10. Total ≈ 71 CPU-h ≈ 18–20 h wall on 4 workers.
**Queue:** started 2026-11-08 00:10 IST, PID 38274 (caffeinate 38276). Log at data/logs/queue.log; check with `make -C experiments status`. The first E2 jobs completed (about 100 jobs/min). **Expected finish ≈ 2026-11-08 19:00–21:00 IST.** Queue outputs are not committed; batch 2B/3 commits them.

**Surprises (physics readings are proposals).**
1. *Proposal:* T2 holds exactly at the terminal rest state. "Held when alone" coincides with margin > 0 in 393/393 blockers.
2. *Proposal:* a deadlock is usually a stack of stuck-alone agents. In about 80% of deadlocks, removing the keystone lets the next stuck-alone agent take its place.
3. *Proposal:* pair standoffs already occur at the published wall law, as mixed pairs (one passable, one stuck-alone member) with the same geometry as the B_w = 0.04 pairs.
4. Most errors of the k = 3 rule are final blockers that had ≥ 3 others active at arrival (110/192, 101/194). *Proposal:* the others active at that moment are mostly stuck-alone agents queued behind, which cannot transmit enough push. The rule's count could be restricted to passable agents. [NEEDS PALAASH, part of T2]
5. **[NEEDS PALAASH] E2 has n = 34, not 60.** Option: add 26 snapshots from the second-trap class (blocker held alone) in a later batch. The current jobs are unaffected.
6. **[NEEDS PALAASH] E3 censoring risk.** 24 of the 34 E2 snapshots have a single residual agent, so collective ΔU equals the lone barrier (about 16–45 J). E3 takes the 20 largest. At σ = 0.05, k_BT_eff ≈ 10 / 5 / 2.5 J at dt = 0.005 / 0.01 / 0.02. Most dt = 0.02 and many dt_scaled restarts should censor at 300 s, so ℓ may come out as bounds only. E3 starts about 1 h after launch. Amending the rule means stopping the queue (kill 38274) or rerunning E3 later; job_ids are per snapshot, so old rows stay separate.
7. Early E2 rows, too few to read yet: constraint_only frees some residual agents but not all; b = 0.5 frees an agent in E1b_seed52.
