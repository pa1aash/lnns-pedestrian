# Pre-registration: replace couplings R1 and R2 (session C5, task 9)

Written and committed before any R1 or R2 run. Scripts experiments/revision7/T9_prereg.py and T9_write_note.py; numbers data/derived/rev7_T9_prereg.json. No snapshot dynamics was run to make this prediction.

## Couplings
Both replace the goal-directed drive instead of adding to it (simulator flag `orca_replace = on`, RVO2 solver):

F = (1 − χ) F_des + χ m (v_ORCA − v)/τ_ORCA + agent forces + wall forces,  F_des = m (v_eff e − v)/τ,

χ = w_o(ρ) the ORCA density gate, τ_ORCA = 0.5 s, v_ORCA the RVO2 velocity nearest v_pref.
- **R1**: v_pref = v_eff e (`orca_pref = veff`: the density throttle of Eq. 2 applied to ORCA's preferred speed).
- **R2**: v_pref = v0 e (`orca_pref = v0`).

Force-coupled ORCA is F_des + χ m (v_ORCA − v)/τ_ORCA; at rest its drive part adds m v0/τ_ORCA to m v_eff/τ. R1 and R2 keep only (1 − χ) ≈ 3e-4 of F_des, so the rest drive is about m v_pref/τ_ORCA.

## Rest drive and stuck-alone margin (primary rule)
Convention of Eq. (stuck): blocker alone at rest on the door axis, ρ = 0, so v_eff = v0 and χ = χ(0) = 0.99966.
- SFM: D_S = m v0/τ.
- R1: D_1 = (1 − χ) m v_eff/τ + χ m v_eff/τ_ORCA; R2: D_2 = (1 − χ) m v_eff/τ + χ m v0/τ_ORCA (equal at ρ = 0).
- margin = g_max(r) − D, with g_max from the E1 library (margin_C1 + m v0/τ).
- **Prediction: a blocker is freed within 120 s iff its margin is negative, held if positive.**

D_R/D_S = χ τ/τ_ORCA + (1 − χ); with τ in 0.40–0.60 s this is 0.81–1.20. Replacing the drive therefore changes the rest drive by at most ±20%, and only a blocker with τ > 0.5 s and an SFM margin below m v0 (1/τ_ORCA − 1/τ) can be freed. All 60 blockers are held under SFM (positive SFM margin).

## Predicted counts
| set | n | R1 freed | R2 freed | force-coupled ORCA (RVO2), paper | drive part, paper |
|---|---|---|---|---|---|
| lone keystones | 34 | **1** (E1b_seed100) | **1** | 30 | 30 |
| second traps, screening set | 26 | **0** | **0** | 17 | 24 |
| other second traps, deadlock set | 134 | **5** | **5** | 121 − 17 = 104 (of 160 − 26) | 149 − 24 = 125 |

R1 and R2 are predicted identical at every snapshot: the snapshot densities are at most 0.28 m⁻² (agents within 3 m), where the throttle factor is 1 to 1e-8. They can differ only in dense crowds (whole runs, task 11).

## Expected exceptions (stated in advance)
1. **Constraint part.** At the rest snapshot the RVO2 velocity equals v_pref for 51 of the 60 blockers. At 9 (E1b_seed46, E1b_seed60, E1b_seed75, E1b_seed111, E1b_seed130, E1b_seed209, E1b_seed223, E1b_seed230, E1b_seed237) a neighbour's half-plane binds and adds a mainly lateral force of up to 49 N with an axial part of at most 1.1 N; including it changes no predicted outcome (column LP). In motion the half-planes of agents behind the blocker depend on their velocities, so a moving neighbour can add or remove axial drive of order tens of newtons. Exceptions, if any, are expected at second traps whose neighbours move during the quench, not at lone keystones.
2. **Pushes from behind.** Under R1/R2 each agent's own drive changes by its factor χτ/τ_ORCA + (1 − χ). Where an agent behind is in contact with the blocker, the contact force on the blocker changes with it, so a blocker with a margin of a few tens of newtons could be pushed through. Expected direction: frees, rarely.
3. **Run-up.** A quench starts at the SFM rest point, where the wall force equals D_S. Under R the blocker moves to where it equals D_R; with damping ≈ χ m v/τ_ORCA it does not overshoot the peak. A 1-D on-axis integration from the SFM rest point (code wall force, convex_union rule; diagnostic (c)) frees exactly the statically predicted blocker and no other. Run-up exceptions are not expected (the 1 m run-up of C3 task 6f does not arise in a quench).
4. **Margins near zero.** The only predicted free (E1b_seed100, R margin -7.2 N, SFM +13.7 N) and the smallest held margin (E1b_seed71, +20.0 N) bound the sensitivity.

**Falsification criterion.** The rest-drive account holds if at most 2 of the 60 screening-set snapshots disagree with the prediction (unperturbed run) and each disagreement is traced to exception 1 or 2 in its run record. Replays (5 per snapshot, 1e-9 m) are compared with the unperturbed outcome. For the 134 other second traps the same rule allows at most 5 disagreements (about 4%, as 2 of 60); margins within ±1 N (E1b_seed85, −0.7 N) are too close to call and are reported separately.

## Per-snapshot table (screening set)
Forces in N. LP = R1 margin with the RVO2 velocity at the snapshot (constraint part included); constraint = its axial / lateral force at rest under R1; ρ_s from the agents within 3 m.

| snapshot | class | τ (s) | v0 (m/s) | g_max | D_S | D_1 = D_2 | margin SFM | margin R1 | margin R2 | LP | constraint ax / lat | ρ_s (m⁻²) | predicted R1 / R2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1b_seed100 | lone keystone | 0.576 | 0.98 | 150.3 | 136.6 | 157.5 | 13.7 | -7.2 | -7.2 | -7.2 | 0.0 / 0.0 | 0.00 | freed / freed |
| E1b_seed71 | lone keystone | 0.571 | 0.92 | 167.3 | 129.0 | 147.4 | 38.4 | 20.0 | 20.0 | 20.0 | 0.0 / 0.0 | 0.04 | held / held |
| E1b_seed72 | lone keystone | 0.572 | 1.40 | 247.8 | 196.2 | 224.5 | 51.6 | 23.3 | 23.3 | 23.3 | 0.0 / 0.0 | 0.04 | held / held |
| E1b_seed205 | lone keystone | 0.542 | 0.98 | 180.4 | 144.8 | 157.0 | 35.6 | 23.5 | 23.5 | 23.5 | 0.0 / 0.0 | 0.04 | held / held |
| E1b_seed80 | lone keystone | 0.537 | 0.84 | 158.8 | 124.7 | 133.8 | 34.0 | 24.9 | 24.9 | 24.9 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed150 | lone keystone | 0.531 | 0.81 | 155.8 | 121.3 | 128.9 | 34.5 | 26.9 | 26.9 | 26.9 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed238 | lone keystone | 0.565 | 0.86 | 165.7 | 122.2 | 138.2 | 43.5 | 27.5 | 27.5 | 27.5 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed200 | lone keystone | 0.549 | 1.18 | 222.4 | 171.3 | 188.0 | 51.1 | 34.4 | 34.4 | 34.4 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed120 | lone keystone | 0.523 | 1.31 | 251.7 | 201.0 | 210.1 | 50.7 | 41.6 | 41.6 | 41.6 | 0.0 / 0.0 | 0.04 | held / held |
| E1b_seed108 | lone keystone | 0.415 | 0.87 | 187.0 | 167.9 | 139.5 | 19.1 | 47.6 | 47.6 | 47.6 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed204 | lone keystone | 0.563 | 0.92 | 195.1 | 130.9 | 147.4 | 64.2 | 47.6 | 47.6 | 47.6 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed141 | lone keystone | 0.403 | 0.61 | 146.1 | 122.1 | 98.3 | 24.0 | 47.8 | 47.8 | 47.8 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed91 | lone keystone | 0.474 | 0.64 | 159.4 | 108.9 | 103.2 | 50.5 | 56.2 | 56.2 | 56.2 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed140 | lone keystone | 0.553 | 1.04 | 224.7 | 150.9 | 166.9 | 73.8 | 57.8 | 57.8 | 57.8 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed107 | lone keystone | 0.517 | 1.38 | 288.1 | 213.1 | 220.4 | 75.0 | 67.7 | 67.7 | 67.7 | 0.0 / 0.0 | 0.04 | held / held |
| E1b_seed89 | lone keystone | 0.500 | 1.16 | 253.9 | 184.9 | 184.8 | 69.0 | 69.1 | 69.1 | 69.1 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed179 | lone keystone | 0.460 | 1.06 | 239.4 | 184.5 | 169.6 | 54.9 | 69.8 | 69.8 | 69.8 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed84 | lone keystone | 0.546 | 0.88 | 214.1 | 128.9 | 140.9 | 85.2 | 73.2 | 73.2 | 73.2 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed239 | lone keystone | 0.520 | 1.24 | 291.2 | 191.0 | 198.6 | 100.3 | 92.7 | 92.7 | 92.7 | 0.0 / 0.0 | 0.04 | held / held |
| E1b_seed132 | lone keystone | 0.504 | 0.66 | 209.0 | 105.5 | 106.3 | 103.5 | 102.7 | 102.7 | 102.7 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed155 | lone keystone | 0.580 | 0.81 | 236.4 | 112.1 | 130.2 | 124.2 | 106.2 | 106.2 | 106.2 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed94 | lone keystone | 0.480 | 1.15 | 293.5 | 191.6 | 183.8 | 101.8 | 109.6 | 109.6 | 109.6 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed227 | lone keystone | 0.499 | 1.01 | 279.9 | 162.5 | 162.1 | 117.4 | 117.8 | 117.8 | 117.8 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed114 | lone keystone | 0.448 | 0.95 | 272.7 | 170.0 | 152.3 | 102.7 | 120.4 | 120.4 | 120.4 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed215 | lone keystone | 0.534 | 1.21 | 317.8 | 181.8 | 194.3 | 136.0 | 123.5 | 123.5 | 123.5 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed211 | lone keystone | 0.583 | 0.86 | 265.7 | 118.1 | 137.6 | 147.6 | 128.0 | 128.0 | 128.0 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed69 | lone keystone | 0.502 | 1.00 | 292.6 | 158.9 | 159.6 | 133.7 | 133.0 | 133.0 | 133.0 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed52 | lone keystone | 0.517 | 0.85 | 277.4 | 131.2 | 135.5 | 146.2 | 141.9 | 141.9 | 141.9 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed58 | lone keystone | 0.475 | 0.79 | 271.9 | 132.7 | 126.0 | 139.3 | 146.0 | 146.0 | 146.0 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed128 | lone keystone | 0.588 | 1.54 | 396.7 | 209.1 | 245.9 | 187.6 | 150.8 | 150.8 | 150.8 | 0.0 / 0.0 | 0.04 | held / held |
| E1b_seed61 | lone keystone | 0.408 | 1.18 | 345.9 | 231.9 | 189.2 | 114.0 | 156.7 | 156.7 | 156.7 | 0.0 / 0.0 | 0.11 | held / held |
| E1b_seed87 | lone keystone | 0.491 | 0.76 | 283.1 | 124.2 | 121.9 | 158.9 | 161.2 | 161.2 | 161.2 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed203 | lone keystone | 0.416 | 0.69 | 284.2 | 132.9 | 110.7 | 151.3 | 173.6 | 173.6 | 173.6 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed83 | lone keystone | 0.577 | 0.81 | 362.1 | 111.9 | 129.2 | 250.3 | 233.0 | 233.0 | 233.0 | 0.0 / 0.0 | 0.00 | held / held |
| E1b_seed60 | second trap | 0.595 | 1.11 | 206.5 | 148.7 | 176.8 | 57.8 | 29.7 | 29.7 | 35.0 | 1.1 / 37.3 | 0.04 | held / held |
| E1b_seed103 | second trap | 0.485 | 1.00 | 194.2 | 165.3 | 160.4 | 29.0 | 33.8 | 33.8 | 33.8 | 0.0 / 0.0 | 0.04 | held / held |
| E1b_seed223 | second trap | 0.577 | 1.20 | 229.3 | 166.4 | 192.1 | 62.9 | 37.2 | 37.2 | 44.6 | -0.3 / 48.2 | 0.04 | held / held |
| E1b_seed55 | second trap | 0.569 | 1.18 | 226.4 | 165.5 | 188.1 | 60.9 | 38.2 | 38.2 | 38.2 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed209 | second trap | 0.490 | 0.92 | 186.4 | 150.1 | 147.0 | 36.3 | 39.4 | 39.4 | 43.6 | 0.9 / 28.9 | 0.04 | held / held |
| E1b_seed130 | second trap | 0.592 | 1.23 | 263.0 | 166.3 | 196.9 | 96.7 | 66.1 | 66.1 | 73.7 | 0.1 / 49.3 | 0.04 | held / held |
| E1b_seed73 | second trap | 0.592 | 0.71 | 190.4 | 96.6 | 114.4 | 93.8 | 76.0 | 76.0 | 76.0 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed202 | second trap | 0.598 | 1.26 | 279.9 | 168.4 | 201.2 | 111.6 | 78.7 | 78.7 | 78.7 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed111 | second trap | 0.535 | 1.00 | 242.2 | 149.6 | 159.9 | 92.6 | 82.3 | 82.3 | 87.6 | 0.2 / -35.6 | 0.04 | held / held |
| E1b_seed162 | second trap | 0.583 | 1.04 | 260.9 | 142.1 | 165.7 | 118.8 | 95.3 | 95.3 | 95.3 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed112 | second trap | 0.438 | 1.15 | 293.8 | 209.5 | 183.4 | 84.3 | 110.4 | 110.4 | 110.4 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed46 | second trap | 0.514 | 1.33 | 345.1 | 207.5 | 213.2 | 137.6 | 131.9 | 131.9 | 138.1 | 1.1 / -45.6 | 0.04 | held / held |
| E1b_seed178 | second trap | 0.443 | 1.16 | 320.5 | 209.7 | 185.7 | 110.7 | 134.8 | 134.8 | 134.8 | 0.0 / 0.0 | 0.11 | held / held |
| E1b_seed75 | second trap | 0.411 | 1.09 | 313.5 | 211.7 | 174.0 | 101.8 | 139.4 | 139.4 | 145.4 | 0.2 / 40.6 | 0.04 | held / held |
| E1b_seed74 | second trap | 0.510 | 0.92 | 288.1 | 144.9 | 147.6 | 143.2 | 140.5 | 140.5 | 140.5 | 0.0 / 0.0 | 0.11 | held / held |
| E1b_seed237 | second trap | 0.460 | 0.89 | 285.3 | 155.0 | 142.5 | 130.2 | 142.8 | 142.8 | 148.5 | -0.4 / -35.3 | 0.04 | held / held |
| E1b_seed187 | second trap | 0.567 | 0.87 | 289.2 | 122.2 | 138.5 | 167.0 | 150.7 | 150.7 | 150.7 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed230 | second trap | 0.432 | 0.86 | 289.7 | 159.0 | 137.4 | 130.7 | 152.3 | 152.3 | 158.1 | -0.4 / -34.8 | 0.04 | held / held |
| E1b_seed104 | second trap | 0.590 | 1.19 | 360.4 | 160.8 | 189.8 | 199.7 | 170.6 | 170.6 | 170.6 | 0.0 / 0.0 | 0.11 | held / held |
| E1b_seed170 | second trap | 0.506 | 0.91 | 320.0 | 144.5 | 146.3 | 175.6 | 173.7 | 173.7 | 173.8 | 0.0 / 0.0 | 0.11 | held / held |
| E1b_seed158 | second trap | 0.578 | 0.95 | 341.9 | 131.9 | 152.5 | 210.0 | 189.4 | 189.4 | 189.4 | 0.0 / 0.0 | 0.18 | held / held |
| E1b_seed174 | second trap | 0.575 | 1.19 | 402.4 | 165.8 | 190.7 | 236.6 | 211.7 | 211.7 | 211.8 | 0.0 / 0.0 | 0.11 | held / held |
| E1b_seed192 | second trap | 0.575 | 0.80 | 358.8 | 111.1 | 127.8 | 247.7 | 231.0 | 231.0 | 231.0 | 0.0 / 0.0 | 0.07 | held / held |
| E1b_seed113 | second trap | 0.442 | 0.95 | 390.5 | 172.7 | 152.8 | 217.8 | 237.7 | 237.7 | 237.7 | 0.0 / 0.0 | 0.21 | held / held |
| E1b_seed172 | second trap | 0.455 | 1.33 | 453.9 | 233.0 | 212.1 | 221.0 | 241.9 | 241.9 | 242.2 | 0.0 / 0.0 | 0.28 | held / held |
| E1b_seed186 | second trap | 0.426 | 1.17 | 475.4 | 220.5 | 188.0 | 254.9 | 287.4 | 287.4 | 287.5 | 0.0 / 0.0 | 0.18 | held / held |

Other 134 second traps: smallest R margins E1b_seed169 -11.7 N, E1b_seed56 -5.6 N, E1b_seed147 -2.7 N, E1b_seed138 -1.7 N, E1b_seed85 -0.7 N; 5 negative, so **5 of 134** are predicted freed under R1 and R2.

No prediction is made for the 46 pair standoffs: the stuck-alone criterion does not apply there (the pair is held by the members' contact and the lateral wall forces). Whole runs (task 11): no numerical prediction; because R removes the extra drive at the lone trap, completions are expected near the SFM's and far below force-coupled ORCA's.
