# Batch 2C — queue correction (C15, C15a), 2026-11-08

**Stopped.** At 00:58 IST: the queue (PID 38274), caffeinate 38276 and the BAR workers (42129-42133) were killed as one process group, and none are left. E2 had finished all 34 snapshots (3162 rows, 00:48). BAR had 14 of 34 snapshots done and resumes from its JSONL, so the only loss is the 4 snapshots in progress (about 9 min). E3 had not started. Both JSONL files ended on complete lines.

**C15 applied** (commit 6ad5f32; changelog entry appended verbatim).
- **E2:** 60 snapshots = 34 lone-keystone + 26 lone-keystone-with-second-trap (PCG64(2026)). The original 34 keep their job_ids and seeds. New rows carry `blocker`, `stratum`, `blocker_freed` (≤ 120 s) and `blocker_exit_t`; `data/E2/e2_summary.json` gives rates per stratum × arm. E2 finished all 5580 rows at 02:05.
- **E3:** 20 of the 36 snapshots with accepted ΔU ≥ 3 J (ΔU 3.90-56.93 J). σ_i = 0.0286-0.1029 m/s (τ_b 0.416-0.598 s). Predicted ℓ = 2.211-2.222 (β_ref 1.5, 10 snapshots) and 3.682-3.702 (β_ref 2.5, 10 snapshots), with ℓ ≈ −0.03 for the √Δt-scaled arm. Checked by hand for seed58 (σ = 0.06290 m/s, ℓ = 2.214).
- **E4:** 10 of 32 eligible snapshots, collective ΔU 0.02-36.9 J. Seed60's full barrier (0.02 J < 0.1 J) gets no noise amplitude; its frozen and alone conditions run.

**C15a: step cap and validity gate** (experiments/BAR/gate.py, run inside the queue's selection step; changelog bullets recorded).
- **Cap:** steps are capped at 2 mm per agent per iteration. The 14 pre-cap barriers reproduce to 3 decimals.
- **Force test:** upwind tangent; applied from the trapped minimum to one image past the top; tolerance 5 N. The climbing image must reach |∇U| < 0.01 N and be the maximum of U over the whole path.
- **Resolution rule:** the 62-image string must pass the force test and ΔU must change by < 1% from 31 to 62 images. If not, 124 images are computed and the same rule is applied to 62 → 124; otherwise the barrier fails.
- **Alone check:** must agree to 2% with a 2-D grid minimum-energy path (lowest sublevel connecting the minimum to x ≥ 10.35; 5 mm grid, checked by halving). Over all 60 snapshots: string vs grid ≤ 0.025%, halving ≤ 0.11%.
- **Re-run:** the gate re-used the first pass's strings (data/BAR/gate_v1.jsonl) and computed only the new checks: grids, 124-image strings for 6 full conditions, and second frozen paths.

Gate results:
- **Rejected:** 4 of 180 barriers, all full conditions. Seed75: changes by 100% from 62 to 124 images, a near-zero barrier. Seed209: changes by 5.7%. Seed172: climbing image not converged. Seed174: 124-image force 7.8 N and climbing image below the path maximum (9.30 < 9.49 J). These 4 snapshots are excluded from E3/E4.
- **E1b_seed100 now passes:** grid 1.0048 J = string 1.0048 J. The 1-D value of 0 came from BAR's 1-D routine, which for a shallow well takes the minimum past the saddle (x_min = x_top = 9.949). Seed108 behaves the same and passes.
- **E1b_seed46:** alone 22.242 J, frozen 77.725 J, and full 2.346 J now pass (accepted at 31 → 62).
- **Seed46 frozen saddle:** the blocker squeezes past neighbour 99, the agent pinned at the upper jamb (9.480, 5.516). At the saddle the blocker is at (9.804, 4.905), with a 6.2 cm surface gap to 99, 4.9 cm clearance to the lower jamb wall and no overlap.

**Queue.** Paused twice so that no selection would run before the current gate: about 40 min at 02:15 and about 50 min at 04:06; the second time, the first-pass gate finished and its rows were re-used. A stdlib-name clash with experiments/queue.py was fixed. Now **PID 62654** (since 04:55 IST); selection ended 05:17 and E3 is running (95/2460 rows at 05:20). Remaining order: E3, E4, E5b, E7b_lib, E5a, E7, about 61.5 CPU-h. **Expected finish 2026-11-08 ≈ 20:45 IST (20:00-23:30)**, or up to about 08:00 on 11-09 if E3/E4 are mostly censored.

**History rewrite: done and accepted.** The neutral Import note is in place (7 trimmed lines). The rewrite was done in a separate clone, the two commits that became empty were dropped, and the final tree is byte-identical to the pre-rewrite head. The force-push (3b1116e → edf1090) used a lease; the live folder took only fetch + soft reset. Actions on edf1090: tests and paper passed.

**Commits:** 6ad5f32 (C15), edf1090 (C15a, gate), 605dd18 (gate v2 and changelog bullets), and this report.
