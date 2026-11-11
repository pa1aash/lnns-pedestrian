# A5x Table 2 probes on the 134 second traps E2 did not draw

**Done.** experiments/revision/A5_extra_second_traps.py ran the E2 arms on the 134 second-trap snapshots that the E2
draw left out (all 160 second traps of the keystone test minus the 26 drawn; data/revision/A5/a5_quench.jsonl, 2814
jobs, 21 per snapshot). Arms: force-coupled ORCA with the RVO2 solver and with the legacy linear-program solver, each
unperturbed and with five replays displaced by 10⁻⁹ m (perturb seeds 900–904); ORCA's drive part; ORCA's constraint part
(RVO2); the rest-drive push +; the SFM restart; noise σ = 0.07 m/s on the SFM, five seeds (90000 + 100 k + rep). The
push − was not rerun. experiments/revision/A5x_analyze.py (2 s CPU) -> data/derived/rev_A5x.json. Freed means that the
blocker (residual agent nearest (10, 5)) exits within T = 120 s, recomputed from the exit times and checked against
the stored outcome on every run. A deterministic arm contributes its unperturbed run per snapshot. Noise counts every
(snapshot, seed) run for the freed fraction at horizon T, and a snapshot is freed by majority when at least 3 of 5
seeds free its blocker. Intervals are Wilson 95% (revlib.wilson). New against E2 uses the two-sided Fisher exact test
on snapshots (noise on majority outcomes), with Holm over the 7 arms. Paired contrasts within a group use exact
McNemar on snapshots, and noise against ORCA (RVO2) uses the paired sign-flip test of mean(k_i/5 − c_i), as in A7;
Holm acts over the 9 contrasts of each group. Effects carry 95% bootstrap intervals over snapshots (10⁴ resamples,
default_rng(20261111)). The E2 group recomputed from data/E2/e2_quench.jsonl reproduces data/derived/E2_analysis.json
(17, 22, 24, 25, 0, 0 of 26 and 117 of 130; drive part against ORCA (RVO2) 7:0, p = 0.016). Registry:
notes/A5x.yaml, 228 macros, prefix RevAfiveX; every key resolves through tools/make_numbers.py, and no name collides
with paper/registry or the other revision registries.

**Result.** Freed fraction at horizon T = 120 s, second traps:

| Arm | new, 134 | E2, 26 | pooled, 160 | Fisher p, new vs E2 |
|---|---|---|---|---|
| force-coupled ORCA (RVO2) | 104/134 = 0.78 [0.70, 0.84] | 17/26 = 0.65 [0.46, 0.81] | 121/160 = 0.76 [0.68, 0.82] | 0.214 |
| force-coupled ORCA (legacy) | 111/134 = 0.83 [0.76, 0.88] | 22/26 = 0.85 [0.66, 0.94] | 133/160 = 0.83 [0.77, 0.88] | 1.000 |
| drive part | 125/134 = 0.93 [0.88, 0.96] | 24/26 = 0.92 [0.76, 0.98] | 149/160 = 0.93 [0.88, 0.96] | 1.000 |
| rest-drive push + | 126/134 = 0.94 [0.89, 0.97] | 25/26 = 0.96 [0.81, 0.99] | 151/160 = 0.94 [0.90, 0.97] | 1.000 |
| constraint part (RVO2) | 5/134 = 0.037 [0.016, 0.084] | 0/26 = 0 [0, 0.13] | 5/160 = 0.031 [0.013, 0.071] | 1.000 |
| SFM restart | 2/134 = 0.015 [0.0041, 0.053] | 0/26 = 0 [0, 0.13] | 2/160 = 0.013 [0.0034, 0.044] | 1.000 |
| noise σ = 0.07 m/s (runs) | 594/670 = 0.89 [0.86, 0.91] | 117/130 = 0.90 [0.84, 0.94] | 711/800 = 0.89 [0.87, 0.91] | 0.445 (majority) |

No arm differs between the new snapshots and E2's 26 (smallest raw p = 0.214, for ORCA (RVO2); Holm p = 1.000 for
every arm). The new sample places ORCA (RVO2) at 0.78 against E2's 0.65, inside E2's interval.

Paired contrasts (discordant first only : second only; effect = first minus second):

| Contrast | new, 134: disc., effect [95%], p (Holm) | pooled, 160: disc., effect [95%], p (Holm) |
|---|---|---|
| drive part vs ORCA (RVO2) | 21:0, +0.16 [0.097, 0.22], <10⁻⁶ (<10⁻⁵) | 28:0, +0.17 [0.12, 0.24], <10⁻⁸ (<10⁻⁷) |
| push + vs ORCA (RVO2) | 22:0, +0.16 [0.10, 0.23], <10⁻⁶ (<10⁻⁵) | 30:0, +0.19 [0.13, 0.25], <10⁻⁸ (<10⁻⁷) |
| drive part vs ORCA (legacy) | 17:3, +0.10 [0.045, 0.17], 0.0026 (0.010) | 19:3, +0.10 [0.044, 0.16], <10⁻³ (0.0034) |
| ORCA (legacy) vs ORCA (RVO2) | 10:3, +0.052 [0, 0.10], 0.092 (0.188) | 16:4, +0.075 [0.025, 0.13], 0.012 (0.035) |
| constraint part vs SFM | 4:1, +0.022 [−0.0075, 0.060], 0.375 (0.375) | 4:1, +0.019 [−0.0063, 0.050], 0.375 (0.375) |
| ORCA (RVO2) vs SFM | 102:0, +0.76 [0.69, 0.84], <10⁻³⁰ (<10⁻²⁹) | 119:0, +0.74 [0.68, 0.81], <10⁻³⁵ (<10⁻³⁴) |
| replay changes, legacy vs RVO2 | 5:0, +0.037 [0.0075, 0.075], 0.062 (0.188) | 7:0, +0.044 [0.013, 0.075], 0.016 (0.035) |
| noise vs ORCA (RVO2), freed fraction | +0.11 [0.054, 0.17], <10⁻³ (0.0019) | +0.13 [0.076, 0.19], 1.0×10⁻⁵ (<10⁻⁴) |
| replay changes, noise vs ORCA (RVO2) | 29:0, +0.22 [0.15, 0.28], <10⁻⁸ (<10⁻⁷) | 34:0, +0.21 [0.15, 0.28], <10⁻⁹ (<10⁻⁹) |

The pooled sign-flip p of 1.0×10⁻⁵ is one random flip in 2×10⁵ (Monte Carlo floor 5×10⁻⁶).

Replays. Force-coupled ORCA (RVO2) changes no outcome in 670 new replays (800 pooled). The legacy solver changes 8 of
670 new replays on 5 snapshots (13 of 800 on 7 pooled). Noise seeds disagree on 29 of 134 new snapshots (34 of 160).

The SFM restart frees the blocker in 2 new snapshots (seeds 56 and 184, after 19 s and 26 s; held in the keystone
test, where the blocker is restarted alone). Both saved snapshots are still creeping: their fastest agent moves at
2.0 and 0.64 mm/s, ranks 4 and 6 of the 196 deadlock snapshots, against a median of 7.8×10⁻⁷ m/s. The deadlock
criterion (every active |v| < 0.01 m/s for 10 s) admits them. In both, the blocker leaves while its stack settles.

Table 2 reading at the second trap, enlarged sample:
- Force-coupled ORCA (RVO2) is Reshape (L). It frees 121 of 160 against the SFM's 2 (119:0), deterministically (0 of
  800 replays change), and the push + frees 151 of 160. The push − was measured on E2's 26 only (0 of 26).
- The constraint part cancels part of the drive. The drive part frees more blockers than ORCA (RVO2) (28:0 pooled),
  and the constraint part alone frees no more than the SFM (4:1, p = 0.375). The E2 contrast (7:0, p = 0.016) failed
  Holm over this set of 9 contrasts (0.109); the new snapshots alone give 21:0, Holm p < 10⁻⁵.
- The legacy solver's replay flips are Glitch (N) and recur on the new snapshots (8 flips on 5). The legacy solver
  frees more second-trap blockers than RVO2 in the pooled sample (16:4, Holm p = 0.035).
- Noise σ = 0.07 m/s is Heat (T): its seeds disagree where ORCA's replays never do (34:0 pooled). It frees more
  second-trap blockers than ORCA (RVO2) (+0.13 [0.076, 0.19] pooled), so the rate match does not hold at the second
  trap (A6, A7: +0.25, Holm p = 0.062 on 26). On 160 snapshots the freed fraction and replay both separate noise from
  ORCA after Holm.

Claims. Table 2's class assignment at the second trap holds on the enlarged sample: Reshape (L) for force-coupled ORCA
(RVO2), Glitch (N) for the legacy solver's replay flips, Heat (T) for noise. The paper's second-trap sentence (Sect.
6.1.4, drive part 24 against 17 of 26, 7:0, p = 0.016) holds and can quote 149 against 121 of 160 (28:0). Two counts
are specific to E2 and should be labelled so: "in 5 of 300" legacy replay flips (13 of 800 at the 160 second traps)
and "SFM and SFM+TTC free none" (true for the 60 E2 snapshots; the SFM restart frees 2 of the 134 new second traps,
both in slow creep). Sect. 4 calls a deadlock snapshot a rest state; 2 of 160 second-trap snapshots are creeping at
up to 2.0 mm/s and are released by the SFM. The text should say that the deadlock criterion admits creep below
0.01 m/s.

**Draft sentence.** On all \RevAfiveXPoolN\ second traps, ORCA's drive part frees \RevAfiveXPoolDriveFreed\ blockers
and force-coupled ORCA (RVO2) \RevAfiveXPoolOrcaFreed\ (discordant \RevAfiveXPoolDriveOrcaDiscA:\RevAfiveXPoolDriveOrcaDiscB,
exact McNemar $p=\RevAfiveXPoolDriveOrcaPDisp$), with no replay changing an outcome; the \RevAfiveXEtwoN\ snapshots of
the main screen do not differ from the \RevAfiveXNewN\ others in any arm (Fisher, Holm $p=\RevAfiveXVsEtwoMinPHolmDisp$).
