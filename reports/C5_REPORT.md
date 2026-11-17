# C5 report: revision-7 computations (second external review)

Worktree lnns-wt/C5, branch wt-C5, pushed to origin main. Scripts experiments/revision7/, raw data data/revision7/ (manifest data/revision7/MANIFEST.json, sha256 of every file; none over 20 MB), derived data/derived/rev7_*.json, per-task notes notes/C5_items/<task>.md, registry notes/C5_items/revision7.yaml (prefix **Rz**: 0 occurrences in paper/numbers.tex, free; 69 entries reading data/derived/rev7_headline.json).

No recomputed number contradicts a number in the paper.

## 1. Status and wall time

The machine was under heavy outside load all day (load average 20–127) and rebooted at about 12:07; jobs ran in screen sessions with 6 workers (4 tier 1–2, 2 tier 3). Session start 11:52; queues stopped 19:56; report 22:50. **The session overran its 21:50 budget by about 1 h**, and **tier 3 overran its 18:19 limit**: the queue was stopped at 19:56, not 18:19 (see task 11).

| task | status | runs | wall |
|---|---|---|---|
| 1 pair standoffs to rest | unperturbed done (67 extensions); replays partial (219 of 335) | 286 | ~3 h |
| 2 alone Arrhenius, 56 snapshots | done | 5600 restarts | ~3 h (12:20–15:05) |
| 3 rate theory k_TST, κ, A | done | none (theory) | 10 min |
| 4 time-step probe l | done | none (existing E3) | 5 min |
| 5 split-sample matching | done | none | 15 min |
| 6 facts a–h | done | none | 40 min |
| 7 whole-run replays (1e-9 m) | done, one replay per seed × 4 arms | 744 | ~5 h |
| 8 throttled drive part | done | 186 | ~2.5 h |
| 9 pre-registration | done (commit 2ac5353, before any R run) | none | — |
| 10 R1/R2 quenches | unperturbed done (60 + 134 + 46); replays mostly not run | 520 | ~3 h |
| 11 R1/R2 whole runs | reduced: seeds 242–268 (27 × 2); 269–427 not run | 54 | ~4.5 h, **of which ~1.6 h after the 18:19 limit** |

Not run: task-1 replays of the legacy and constraint arms (116 runs); task-10 replays of the 134 other second traps and the 46 pairs, and most of the screening-set replays; task-11 seeds 269–427; keystone classes for task 11 (no run came to rest, so the K-tests do not apply); a pooled task-2 fit restricted to the 3 B3 snapshots.

## 2. Numbers for the paper

Macros in notes/C5_items/revision7.yaml. Intervals are 95%.

| quantity | value | interval | test |
|---|---|---|---|
| alone slope ratio, 56 snapshots (RzTtwoRatio) | 0.946 | [0.935, 0.961] snapshot bootstrap | Poisson fit, 5088 events / 5600; CI covers 1 for 44/56 snapshots, theory for 52/56 |
| same, E4 ten (RzTtwoEfourRatio) | 0.915 | [0.883, 0.948] | — |
| rate-theory slope ratio, E4 ten: k_TST / κk_TST / Aκk_TST (RzTthreeTst, RzTthreeKappa, RzTthreeFull) | 0.919 / 0.919 / 0.892 | per-snapshot 0.87–0.99 | κ is β-independent; A carries the departure |
| time-step l at β0 2.5: saddle / span × 0.946 (RzTfourTwopfiveA, RzTfourTwopfiveC) | 3.696 / 3.498 | observed 3.230 [2.962, 3.521] | saddle misses; ratio-scaled inside |
| time-step l at β0 1.5 (same) | 2.216 / 2.230 | observed 2.164 [1.805, 2.705] | both inside |
| pair standoffs freed at 600 s: legacy / RVO2 / drive / constraint / SFM (RzToneCthreePubFreed etc.) | 21 / 7 / 33 / 44 / 0 of 46 | Wilson e.g. RVO2 [0.08, 0.28] | none changes between 120 s and 600 s; legacy vs RVO2 McNemar 14:0, p = 1.2e-4 |
| held-out σ error, lone keystones (RzTfiveHeldoutMed) | −0.006 m/s | [−0.182, +0.156] | split-sample logit rule reproduces σ = 0.0717 |
| replay outcome changes per 186 seeds: drive / τ′ / RVO2 / SFM (RzTsevenDriveChanges etc.) | 23 / 26 / 41 / 2 | Wilson drive [0.08, 0.18] | completions move by ≤ 7 |
| throttled drive part completions (RzTeightK) | 134 / 186 = 0.72 | [0.65, 0.78] | vs drive 26:18 p = 0.29; vs τ′ 17:18 p = 1.0; vs RVO2 48:15 p < 1e-4 |
| R1 = R2 lone keystones freed (RzTonezeroLoneKeystoneFreed) | 1 / 34 | — | as pre-registered, 0 disagreements |
| R1 = R2 other second traps freed | 12 / 134 | Wilson [0.05, 0.15] | pre-registered 5; 9 disagreements > limit 5 |
| R1 = R2 pairs freed | 25 / 46 | — | legacy 21, RVO2 7, drive 33 |
| R1, R2 whole-run completions, seeds 242–268 (RzToneoneK) | 0 / 27 each | upper 0.125 | vs RVO2 0:12, p < 1e-3; all still moving at 600 s |

## 3. Findings

1. **Alone slope ratio closer to 1 (task 2).** On 56 snapshots the measured/barrier slope ratio is 0.946 [0.935, 0.961], against the published 0.8905 [0.831, 0.950] on 3 snapshots. The new value lies inside the published interval, so no published number is contradicted, but the 0.89 in the text is the low end of what the larger set supports. The E4 ten alone give 0.915. ν/ν_Langer has median 0.82 (0.34–1.15); γ/ω_b median 0.41, so the alone dynamics sit in the moderate-friction range where Langer's prefactor is close but not exact.
2. **Rate theory (task 3).** Transition-state theory with the anharmonic well already gives slope ratio 0.92 on the E4 ten; Kramers' κ is constant in β and changes nothing; the energy-diffusion factor A lowers it to 0.89. The sub-unity slope is mostly anharmonic-entropy (the prefactor falls as T falls), not friction.
3. **Time-step probe (task 4).** The β0 = 2.5 miss of the saddle prediction disappears when the barrier is scaled by the measured alone slope ratio; with 0.946 the prediction (3.50) sits just inside the observed interval's top (3.52).
4. **Pair standoffs are held, not slow (task 1).** No pair frees or comes to rest between 120 s and 600 s in any arm; still-moving pairs jitter by ≤ 6 cm. The 120 s cut is safe.
5. **Task-9 prediction vs result (task 10).** Lone keystones: predicted 1 of 34 freed (seed100), observed exactly that one; R1 and R2 identical everywhere, as predicted. Screening second traps: 1 disagreement (E1b_seed223, margin +37 N, freed at 7.6 s), within the pre-registered limit of 2 of 60. **Other 134 second traps: 9 disagreements against a limit of 5 — the pre-registered criterion fails there.** 8 are predicted held and freed (3 with a neighbour leaving first, consistent with exception 2; 3 with margins of 2–4 N; 2 with margins of 17 and 38 N and the blocker leaving first, unexplained), 1 predicted freed and held (seed138, −1.7 N). The static rest-drive account is exact at lone keystones and incomplete at second traps.
6. **Replacing the drive does not resolve deadlocks (tasks 10, 11).** R1/R2 free 1/34 lone keystones (RVO2, drive and τ′ free 30) and complete 0/27 whole runs (RVO2 12/27). The extra drive, not ORCA's velocity choice, is what frees blockers. Unlike SFM, R runs do not come to rest: all 54 still move at 600 s with 64–93 agents out.
7. **Throttled drive part works as well as the drive part (task 8).** 134/186 vs 126/186; no failure is collective (25 lone keystone, 27 second trap).
8. **Whole-run outcomes are chaotic per seed (task 7).** A 1e-9 m perturbation changes the outcome of 12% (drive) to 22% (RVO2) of seeds, but moves the completion counts by at most 7 of 186. Per-seed agreements between arms (drive vs τ′ 151/186) carry this floor.
9. **Split-sample matching (task 5).** The σ matching rule is not overfit: held-out error −0.006 [−0.18, +0.16] m/s for lone keystones and −0.006 [−0.13, +0.12] for whole runs.
10. **Process.** Tier 3 ran 1.6 h past its 6 h limit and the session ran about 1 h past budget; the task-11 runs collected after 18:19 are reported but flagged.

## 4. Facts a–h (details and file paths in notes/C5_items/T6.md)

- **a.** Table of the 26 run sets used in the paper, with scripts, seeds and derived files.
- **b.** 186 whole-run seeds (242–427) = equivalence-test sample size z²·2p(1−p)/δ² with p = 0.575, δ = 0.15. The "another 100 seeds" of Sect. 7.4 are 242–341, a subset.
- **c.** The 12 pair barriers sit at ranks 0, 4, …, 45 of μ1; pairs have no noise floor. The 0.057 J barrier (seed 401) was accepted. The 0.021 J figure is seed 60's full-condition lone-trap barrier skipped by E4's DU_FLOOR = 0.1, so Sect. 5.2's "noise floor of the string method" names the wrong place.
- **d.** 24 of the 34 lone keystones have only the blocker left (K2 holds vacuously).
- **e.** σ = 0.0717 m/s from a logit fit over the E2 lone stratum at σ 0.03, 0.05, 0.07 (freed 70, 117, 148 of 170), inverted at 30/34 (experiments/runs3/N1.py). E3/E4 β uses the saddle height (barriers_gated full/alone), not the span.
- **f.** The two freed blockers with positive margin are seeds 52 (+10.77 N) and 58 (+13.34 N); drive part, τ′ and the goal-parallel term free them, constraint part and SFM do not; what closes the margin is not recorded.
- **g.** v_t/v0 = (τ + Wτ_o)/(τ + τ_o) = 0.690 at ρ = 2.3 m⁻², τ = 0.5 s (0.655–0.718 over the τ range); the density distribution is not recorded.
- **h.** The non-standoff deadlock is a lone keystone in the all-walls B_w = 0.04 variant, seed 97; in the jamb-only variant 9 of 11 deadlocks leave 2 agents and 2 leave 3 (seeds 57, 122).

## 5. Framework needs (deadlock-screen)

1. A resumable queue with per-tier wall-clock limits that stops itself (tier 3 overran because the stop was manual).
2. Deterministic-skip logic: extend only runs whose earlier record is still moving (saved 700 of 1104 task-1 runs).
3. A stationary-stop / at-rest / still-moving three-way outcome in every whole-run record; "not complete" is not "deadlocked" (task 11).
4. Pre-registration files with machine-checkable predictions per snapshot and an automatic confusion table (task 9/10).
5. Keystone K-tests only on resting states; flag moving final states instead of classifying them.
6. Snapshot-bootstrap Poisson fit with snapshot intercepts as a library function (tasks 2, 3).

## 6. Inputs needed from the author

1. **Alone slope ratio in the text**: keep 0.89 (3 snapshots) or move to 0.946 [0.935, 0.961] (56 snapshots)? Default: quote 0.95 from 56 snapshots, keep 0.89 as the B3 subset.
2. **Pre-registration failure at the 134 other second traps** (9 > 5): state it in Sect. on mechanisms as "exact at lone keystones, incomplete at second traps"? Default: yes, one sentence plus the count.
3. **Task 11 reduced to 27 seeds** (0/27 for R1 and R2): enough for a sentence, or run seeds 269–427 (~25 core-hours)? Default: sentence with the 27-seed upper bound 0.125.
4. **Sect. 5.2 "noise floor of the string method"** (fact c) names the wrong place: correct the wording? Default: yes.
5. **Printed 2.4 vs 2.2 in the time-step paragraph**: not checked against the current text in this session. Default: compare with rev7_T4.json at the next paper session.
6. **Runs not done** (task-1 and task-10 replays): needed? Default: no; unperturbed results stand and the completed replays show 0 discordant snapshots.

## HANDOFF

- State: all tier 1–2 analyses final; tier 3 unperturbed complete, replays and most of task 11 not run. Committed and pushed to origin main.
- Key files: reports/C5_REPORT.md, notes/C5_items/*.md, notes/C5_items/revision7.yaml, data/derived/rev7_*.json, data/revision7/MANIFEST.json.
- Next: paper session decides inputs 1–5 and adds Rz macros through the registry.
