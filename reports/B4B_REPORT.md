# B4B report: walls.py docstring, queue-2 scripts, queue 2 running

**Step 1.** `code/sim/steering/walls.py:20` now reads `- kappa * g(r_i - d_iw) * dot(v_i, t_iw) * t_iw [friction]`, matching walls.py:189-190. No code change; `experiments/regress.py` prints `e381b49dc24acccd OK` (commit 7485fdb).

**Queue 2.** `queue.py` loads queue.yaml once, at start (`for s in steps()`), so editing the file cannot reorder a running queue. It does re-read `data/queue_state.json` before every step. While E5a was still running (744/800), E7 was marked done in the state file as a placeholder. At 18:16:45 the old queue (PID 62654) recorded E5a as done (800/800), skipped E7 and ended on its own. Nothing was killed and no row was stopped mid-run. The placeholder was then removed and the queue restarted at 18:20:54: **PID 3074** (caffeinate 3076), log `data/logs/queue.log`.
Order: E7b_static (done 18:23, 46/46), E7b_quench, E7b_barrier, E6a, E6b, E10, E7, E11, E8, E9, E6p.

| step | jobs | smoke (1 worker, queue running alongside) | CPU-h | wall h |
|---|---|---|---|---|
| E7b_static | 46 | 13 s/snapshot (2 snaps); field check max \|F_code + grad U\| = 5e-8 N | 0.2 (actual) | 0.04 |
| E7b_quench | 6440 | 338 CPU-s per snapshot (all 140 runs, full 120 s) | 4.0 | ~1.0 |
| E7b_barrier | 12 | 121 s per snapshot at 150 string iterations; both channels pass the gate | 5 | ~1.3 |
| E6a | 186 | C3 RVO2 7.9 ms/step (60 s run) | 15 | ~3.8 |
| E6b | 186 | σ* logic tested on synthetic E6a (in range: runs; out of range: exit 4) | 3 | ~0.8 |
| E10 | 125 | C1 cells ~40 s, C3 RVO2 165 s per 60 s simulated; 0 leaks | 12 | ~3 |
| E7 | 900 | (batch 2 estimate) | 10 | ~2.5 |
| E11 | 325 | 13 cells, all complete in < 60 s, 208 s in total | 1.5 | ~0.4 |
| E8 | 375 | 15 s runs: C3_pub 31-80 ms/step, RVO2 6-14 ms/step | 15 | ~3.8 |
| E9 | 300 | 15 s runs: C3/C4 RVO2 16-29 ms/step | 12 | ~3 |
| E6p | 50 | C3 published 75 ms/step | 30 | ~8 |

**Expected finish** of the whole queue (≈108 CPU-h): about **2026-11-09 22:00 IST**, plausible range 18:00 on 11-09 to 02:00 on 11-10. E6p is last and its long runs dominate the tail. Smoke outputs went to the session scratch directory and have been deleted.

**Pair library.** 46 qualifying pair snapshots: `data/E7b/library/E7b_B0.04_seed<N>.pkl`, listed by `experiments/E7b/e7b_pairs.py`. They come from E7b_lib: 320 fresh CF ∪ {B_w: 0.04} runs, C1, w = 0.8 m, seeds 242-561, giving 64 deadlocks, 49 of them pairs, 46 qualifying under the e7b_lib.py rule. The 26 pilot pairs are not used: their flags were not full CF. The E7b_lib outputs are not committed (queue data).

**Could not be specified exactly (choices made):**
- Common lateral displacement δ: both members are shifted by +δ in y (toward +y) before the 1e-9 m perturbation. The a4 pilot moved only the lower member.
- Fold prediction: the b grid as specified; C1, frozen+ and frozen− are added as free reference arms.
- E7b_barrier: 12 snapshots at evenly spaced λ1 ranks. Each member's exit channel is gated separately; the pair barrier is the lower accepted channel. Gate rule (iii) (alone grid) and the frozen second path do not apply to a pair.
- E6b: the logit is fitted to E5b only (σ = 0.03-0.07; E1b's σ = 0 is not included). "Outside the range" means σ* outside [0.03, 0.07] m/s, or E6a at 0 or 100%. In that case E6b writes sigma_star.json and exits with code 4, and E10 then exits 3 after its four other cells.
- E8/E9 "inflow" = start density at fixed n: start blocks 12/18/30 m long for E8 (1.39/0.93/0.56 m⁻²) and 17/25/34 m for E9 (1.96/1.33/0.98 m⁻²). The pilot geometry is the densest level; it is reproduced exactly (checked). The window is the pilot's 60 s. E9 keeps the pilot's line goals. E8 C3_pub runs at all three densities (cost acceptable).
- LP infeasibility for the published LP = the returned velocity violates a half-plane (constraints dropped). It is measured by an observer wrapper (`experiments/lib/lpcount.py`), with no code change.
- E11 seeds 42-66. Runs stop at completion, at deadlock or at 300 s. Overlap zones use the pair midpoint. My per-step overlap count equals the code's collision count.
- E10 seeds 42-66, run type = (seed − 42) mod 5. Its cost (~12 CPU-h) is above the plan's ≤ 8.

**C23 proposed** (for plan/CHANGELOG.md):
C23 (2026-11-08) Queue 2.
- After E5a the queue runs E7b_static, E7b_quench, E7b_barrier, E6a, E6b, E10, E7, E11, E8, E9, E6p (≈108 CPU-h).
- E7b uses the 46 fresh CF ∪ {B_w = 0.04} pair snapshots (E7b_lib, seeds 242-561). The common lateral displacement shifts both members by +δ in y. The pair barrier is the lower of the two gated exit channels, on 12 snapshots spread over λ1.
- σ* is the inverse of a binomial-logit fit of E5b completion at E6a's rate, with no extrapolation outside σ ∈ [0.03, 0.07] m/s. It is fixed in data/derived/sigma_star.json and used by E6b and E10.
- The E8/E9 inflow sweep is a start-density sweep at fixed n, by the length of the start blocks (E8 1.39/0.93/0.56 m⁻²; E9 1.96/1.33/0.98 m⁻²; the densest level is the pilot geometry), with 60 s windows.
- The published-LP infeasibility is counted as dropped constraints (a half-plane violated by the returned velocity).

**[NEEDS PALAASH]**
1. Confirm the E8/E9 inflow definition (start density, 60 s window) and E9 line goals, or say what you want instead before E8 starts (≈ 11-09 midday).
2. Confirm δ as a common +y shift of both members, and E6b's no-extrapolation rule (E5b-only fit).
3. If E6a's completion lands outside the E5b range, E6b and the E10 σ* cell stop. You will then need to decide on the matched-noise target.
4. I briefly ran two single-worker smoke simulations at the same time (E7b quench and barrier; E9 and E6b), alongside the queue. Memory stayed fine (free 36-71%).
