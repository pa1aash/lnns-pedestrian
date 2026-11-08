# Batch 3A report (2026-11-08)

Commits: ffaba09 (C16-C18), 1aba2df (E2 + BAR/gate data), de0fc33 and b49ba19 (analyses, Fig 6, Table 3, registry). CI (tests, paper) green on b49ba19.

## E2: blocker freed within 120 s (deterministic arms: per snapshot, unperturbed run; noise: per run, 5 seeds)
| arm | lone keystone (34) | second trap (26) | pooled (60) | KM median t (s) |
|---|---|---|---|---|
| C1 / C2 | 0 / 0 | 0 / 0 | 0 / 0 [0, 0.06] | — |
| C3 pub / C3 RVO2 | 30 / 30 | 22 / 17 | 52 / 47 [0.66, 0.87] | 2.1 / 1.6 |
| drive only / frozen + / frozen − | 30 / 31 / 0 | 24 / 25 / 0 | 54 / 56 / 0 | 1.5 / 1.1 / — |
| constraint only pub / RVO2 | 0 / 0 | 1 / 0 | 1 / 0 | — |
| bias b = 0.05, 0.1, 0.2, 0.5 | 0 at every b | 0, 1, 2, 0 | 0, 1, 2, 0 | — |
| noise σ = 0.03 / 0.05 / 0.07 (runs) | 70/170, 117/170, 148/170 | 67/130, 104/130, 117/130 | 137, 221, 265 /300 | not reached / 22.9 / 14.4 |

- Replay: C1, C2, C3 RVO2, drive only, frozen ±, bias: 0 differences in 300 replays each (C3 RVO2 max |Δt| = 0.000 s). C3 pub: 5/300 flip freed/held (seed174 4×, seed187 1×), max |Δt| 80.8 s, all second-trap, slow exits. Noise: seeds split in 16/19/14 of 60 snapshots; within-snapshot SD of first exit 19.7/13.8/11.2 s.
- Rest-state lemma: C2 = C1 in 360/360 paired runs (identical exits, stopping times, final positions; no exits in either).

## Decomposition verdicts (pooled; discordant first:second, exact McNemar)
- drive only vs C3 RVO2 7:0 (p = 0.016), vs C3 pub 2:0 (p = 0.5). Lone keystone alone: drive = C3 pub = C3 RVO2, 0:0.
- constraint only vs C1: pub 1:0, RVO2 0:0. Frozen + vs − 56:0. Frozen + vs C3 RVO2 9:0 (p = 0.004). C3 pub vs RVO2 6:1 (p = 0.125).
- Lateral bias vs C1: 0:0, 1:0, 2:0, 0:0. Lone-keystone Wilson upper bound 0.10 at every b (0/34), S8 bound met to rounding.
- Reading (L): at the lone keystone ORCA frees through its rest drive alone, deterministically, and the 4 failures all have C3 rest margin > 0 (AUC 0.98). (T): noise is stochastic, rises with σ, waits tens of seconds; σ = 0.07 matches C3 RVO2 on lone-keystone rate (Δ = −0.01) but its unresolved set overlaps with Jaccard 0.20 [0.00, 0.50].

## Chain statement (E1b; E1a agrees)
Passable agents drain first: stuck-alone fraction 0.20 → 0.62 from first to last arrival decile (last 5 arrivals median margin +38 N vs −62 N); blocker among last 3 arrivals in 184/196. The "only passable pushers" reading is **not supported**: with no passable agent left 141/288 stuck-alone arrivals still exit (131/178 with ≥ 3 stuck-alone others active); AUC stuck_active 0.963 vs passable_active 0.948, behind_1m 0.925. Cleanest statement: a stuck-alone agent is pushed through by whoever is still in the room, passable or not; total count is the best predictor (AUC 0.975 [0.970, 0.979]). Second trap: K1b held in 296/314, every held target stuck alone.

## Fig 6 QA
figures/fig6_quench.pdf, full width, 12.2 × 6.4 cm. Fonts all embedded, min text 6.97 pt, min line 0.40 pt; checked original, grey, deuteranopia, protanopia PNGs. Yellow (bias) markers given a thin dark edge (filled) / heavier ring (open) for contrast; C2 orange and noise vermillion merge under deuteranopia but are separated by tick labels. Caption: two sentences, in §6.1.

## Registry and tables
167 macros (paper/numbers.tex): E1 completion with CI per mode, stuck-alone fraction, AUC and all-exit baseline, keystone classes per mode, 393/393 + 7 negative-margin, 296/314, chain numbers, E2 freed counts per stratum × arm, CIs and KM medians of key arms, replay, C2 = C1, decomposition discordants and p, Jaccard, margin AUCs. Arm keys in E2_analysis.json are dot-free (noise0p07, bias0p05) so registry paths reach them. Table 3 (paper/tables/table3_matched.tex): 8 lone-trap rows, not \input; E3–E7b rows left out until data exist.

## [NEEDS PALAASH: T1 sign-off] rest-state lemma, dissipative form
- [ ] TTC validity: code/sim/steering/ttc.py:91 `valid = (a >= 1e-8) & (disc >= 0)` with a = |v_i − v_j|² (ttc.py:85), so TTC is exactly 0 for relative speed < 1e-4 m/s; force ttc.py:108, added at hybrid.py:161. Confirm: G(x, 0) = 0 holds (not only vanishing as v → 0).
- [ ] SFM sliding friction: sfm.py:106-108, F_i += κ g (v_j − v_i)·t t; pairs enumerated both ways (sfm.py:66-73, accumulated to i only, sfm.py:112). Sum over a pair gives −κ g ((v_i − v_j)·t)² ≤ 0: dissipative, zero at rest. Docstring sfm.py:20 consistent.
- [ ] Wall friction: walls.py:189-190, F = −κ g (v_i·t) t: dissipative, zero at rest. **Docstring walls.py:20 shows +κ…, opposite to the code**; the code matches Helbing 2000 (comment walls.py:188).
- [ ] Damping term D·v: desired.py:60, m(v_eff ê − v)/τ.
- [ ] ORCA not rest-vanishing: orca.py:340 v_pref = v0 ê, orca.py:350 F = m(v_orca − v)/τ_ORCA → m v0 ê/τ_ORCA at rest with no binding constraint, weighted by w_ORCA = 1 − σ(ρ; 4, 2) (hybrid.py:119-123; 0.9997 at ρ = 0); the split is the identity documented at orca.py:276-277.
- E2 evidence (Step 3c): C2 = C1, 0/60 each, identical in 360/360 paired runs; ORCA's drive alone frees 54/60 and its constraint 1/60 / 0/60.

## Surprises (proposals marked)
- At the second trap full ORCA frees *less* than its own drive (C3 RVO2 17/26 vs drive 24/26, frozen + 25/26), and the blocker's margin does not predict failure there (AUC 0.37). [proposal] The velocity-obstacle constraint against the neighbouring trapped agent cancels part of the door-ward drive.
- The published LP is not replay-deterministic (5/300 flips, Δt up to 81 s); RVO2 is exact. [proposal] Ill-conditioned active-set choice in slow near-contact creep: class N for that solver, so the S2 rule "any discordance falsifies L" fails for C3 pub but not C3 RVO2.
- Lone-keystone noise needs σ ≈ 0.07 to match C3 RVO2's rate; pooled, σ = 0.05 is closest (Δ = −0.05).

## Queue at end (16:20 IST)
Done: E2, BAR, SEL_E3E4, E3, E4, E5b, E7b_lib; none failed. Running: E5a (97/800 rows since 15:56, ~4 rows/min → about 19:30), then E7 (est 15 CPU-h ≈ 3.8 h on 4 workers), so the queue will likely finish around 23:00–24:00, later than 20:45. Untouched: data/E3/ onward (uncommitted).
