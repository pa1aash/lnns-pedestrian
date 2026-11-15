FINAL
# C3 report: new computations and look-ups for revision 4

Registry notes/C3_items/revision4.yaml (prefix Rw; built by experiments/revision4/build_registry4.py from
notes/C3_items/T*.yaml; validated with tools/make_numbers.py on a scratch copy, rendered macros in
notes/C3_items/revision4_numbers.tex); sources data/derived/rev4_*.json; scripts experiments/revision4/; raw
data/revision4/<item>/; per-item notes with method and tables notes/C3_items/T*.md; run manifest
data/revision4/MANIFEST.json (sha256, records, summed job seconds). Regression hash e381b49dc24acccd OK after the
one code change (flag `sfm_tau_prime`, default off, bitwise identical when off; tests code/tests/test_sfm_tau_prime.py).
No number already in the paper is contradicted by any recomputation (checks listed per item).

## 1. Status per task

| task | status | note |
|---|---|---|
| 1 whole-run attribution | done | 186 seeds × drive part, τ′ SFM; SFM 342–427 new (242–341 from E6, 242–246 rerun identical); keystone tests on all failures |
| 2 legacy at second traps | done | no new runs; counts asserted equal to rev_A5x.json |
| 3 time-step probe, σ = 0.07 m/s | done | 2400 restarts; per-step and √dt-scaled at all three dt (request named dt-scaled at 0.01 s only, where both arms coincide) |
| 4 CroMa at dt = 0.005 s | done, reduced | cost at 25 runs/variant at both dt ≈ 17 CPU-h > 12, so 10 runs per variant (seeds 42–51, 2 per human run) at dt = 0.005 s and the same 10 at dt = 0.01 s |
| 5 E1b_seed170 diagnostic | done | string re-run with path, second rest state M2 found, exit barrier from M2, 90 restarts |
| 6 facts a–i | done | f needed a new computation (B1 did not record it): 200 lone releases |

## 2. NUMBERS FOR THE PAPER

### Task 1 — whole runs, seeds 242–427 (n = 186; default walls, w = 0.8 m, 100 agents, dt 0.01 s, 600 s)
(a) drive part = SFM + χ_i m(v0 e − v)/τ_orca (force-coupled ORCA with the ORCA term replaced by its drive part,
w2_orca_split drive_only; no linear program). (b) plain SFM with τ′ = ττ_orca/(τ+τ_orca) and target speed
τ′(v_eff/τ + v0/τ_orca). Macros RwOne*.

| arm | completes | 95% Wilson | failures at 600 s (keystone test) |
|---|---|---|---|
| (a) drive part | 126/186 | [0.61, 0.74] | 60, all at rest: 27 lone keystone, 32 second trap, 1 collective |
| (b) τ′ SFM | 135/186 | [0.66, 0.78] | 51, all at rest: 21 lone keystone, 28 second trap, 2 collective |
| SFM | 2/186 | [0.003, 0.038] | 184 at rest (seeds 342–427 classified: 9 lone, 76 second trap) |
| ORCA RVO2 (E6, existing) | 101/186 | — | 85: 31 at rest, 54 still moving |

- McNemar exact (arm only : comparator only), Holm over the four tests: (a) vs RVO2 44:19, p = 0.0022
  (Holm 0.0022); (b) vs RVO2 44:10, p = 3.4e-6 (Holm 6.8e-6); (a) vs SFM 124:0, p < 1e-37; (b) vs SFM 133:0, p < 1e-39.
- Failure classes: at-rest class mix against ORCA's, permutation p = 0.76 (a), 0.60 (b). At rest vs still moving
  against ORCA, Fisher p = 6.8e-18 (a), 4.9e-16 (b): with the drive part or τ′ no failure is still moving at 600 s;
  with the full ORCA term 54 of 85 are.
- (a) vs (b) run by run: same outcome 151/186 (113 both complete, 38 both fail); discordant 13 (a only) : 22 (b only),
  McNemar p = 0.18; identical end time in 1 run; median evacuation-time difference (b − a) −0.8 s. (a) and (b) give the
  same force only when the gate χ_i = 1; in whole runs χ falls to 0.958 (rev_A2 runs.w_min), so trajectories separate
  run by run while the totals agree within sampling error.
- Consistency: RVO2 count 101 and its classes reproduce E6_analysis; SFM 242–246 rerun identical.

### Task 2 — legacy solver at the second traps (existing records; macros RwTwo*)

| set | legacy | RVO2 | drive part | legacy vs RVO2 | legacy vs drive part |
|---|---|---|---|---|---|
| screening 26 | 22 [0.66, 0.94] | 17 | 24 | 6:1, p = 0.125 (Holm 0.25) | 0:2, p = 0.50 (Holm 0.50) |
| deadlock 160 | 133 [0.77, 0.88] | 121 | 149 | 16:4, p = 0.012 (Holm 0.012) | 3:19, p = 8.6e-4 (Holm 0.0017) |

Holm over the two tests per set; rev_A5x (Holm over its five pooled contrasts) gives 0.035 and 0.0034 for the same
two pooled tests. Physics: from the second-trap rest states the legacy solver frees more blockers than RVO2 (16 against
4 discordant on the 160) and fewer than the drive part alone (3 against 19). Legacy replays change the outcome at 7 of
160 snapshots (13 of 800 replays).

### Task 3 — time-step probe at σ = 0.07 m/s, 20 E3 snapshots (macros RwThree*)
20 restarts per (snapshot, arm, dt); ℓ = ln λ(0.005)/λ(0.02) (Eq. 11), pooled mean, bootstrap 95%.

| arm | snapshots with ℓ | pooled ℓ [95%] | predicted | E3 at σ_i (existing) |
|---|---|---|---|---|
| per-step σ | 19/20 | 1.62 [1.00, 2.33] | 2.03 | 2.70 [2.35, 3.05] |
| √dt-scaled σ | 20/20 | −0.08 [−0.24, 0.11] | −0.02 | −0.09 [−0.22, 0.05] |

| arm, dt | realised β range | share β < 1 |
|---|---|---|
| per-step, 0.005 s | 0.18–2.50 | 0.75 (15/20) |
| per-step, 0.01 s | 0.37–4.99 | 0.45 (9/20) |
| per-step, 0.02 s | 0.73–9.89 | 0.15 (3/20) |
| √dt-scaled, 0.005 / 0.01 / 0.02 s | 0.37–5.01 / 0.37–4.99 / 0.36–4.94 | 0.45 at each |

E1b_seed83 has no escape at dt = 0.01 or 0.02 s under per-step noise (20 restarts each, 300 and 900 s), so its ℓ is
undefined. Per-step: observed − predicted −0.40 [−0.67, −0.09], OLS slope on predicted 1.01 [0.77, 1.23]. Censored
fractions 0.02–0.18. Physics: at one σ the per-step escape rate still rises as dt falls because k_B T_eff doubles
when dt halves; √dt scaling holds β within 1.5% across dt and ℓ is consistent with 0.

### Task 4 — CroMa at dt = 0.005 s (macros RwFour*)
Cost rule applied: 25 runs per variant at both time steps ≈ 17 CPU-h > 12, so **10 runs per variant** (seeds 42–51,
two per human run) at dt = 0.005 s, compared with the same 10 seeds at dt = 0.01 s (which reproduce the published
D3 records exactly, 40/40). Process CPU 5.9 h. Friction factor 2κh·dt/m at the largest agent overlap h
(κ = 2.4e5 kg/(m s), m = 80 kg; explicit friction update stable below 2).

| variant | dt (s) | complete / deadlock / moving | flow ratio [95%] | fluctuation (m/s) [95%] | max overlap agent / wall (cm) | friction factor |
|---|---|---|---|---|---|---|
| SFM | 0.005 | 1/9/0 | 0.50 [0.42, 0.60] | 0.094 [0.093, 0.096] | 2.40 / 1.99 | 0.72 |
| SFM | 0.01 | 1/9/0 | 0.50 [0.42, 0.59] | 0.093 [0.091, 0.095] | 2.44 / 1.98 | 1.47 |
| jamb range | 0.005 | 10/0/0 | 0.54 [0.46, 0.65] | 0.095 [0.093, 0.097] | 2.29 / 2.14 | 0.69 |
| jamb range | 0.01 | 8/2/0 | 0.56 [0.47, 0.66] | 0.094 [0.092, 0.096] | 2.35 / 2.71 | 1.41 |
| force-coupled ORCA (RVO2) | 0.005 | 4/0/6 | 0.57 [0.48, 0.68] | 0.098 [0.096, 0.100] | 1.85 / 1.74 | 0.55 |
| force-coupled ORCA (RVO2) | 0.01 | 5/0/5 | 0.59 [0.50, 0.70] | 0.100 [0.097, 0.102] | 1.89 / 1.67 | 1.14 |
| per-step noise σ* | 0.005 | 9/0/1 | 0.43 [0.35, 0.53] | 0.124 [0.122, 0.126] | 3.33 / 2.93 | 1.00 |
| per-step noise σ* | 0.01 | 7/0/3 | 0.42 [0.32, 0.54] | 0.108 [0.107, 0.110] | 3.75 / 2.33 | 2.25 |

- **All four dt = 0.005 s flow ratios lie inside the dt = 0.01 s intervals**, both on the same 10 seeds and the
  published 25-run intervals. Paired flow(0.005)/flow(0.01): 1.01 [0.96, 1.06], 0.98 [0.93, 1.04], 0.97 [0.93, 1.02],
  1.06 [0.75, 1.49]; completion discordance 1:1, 2:0, 1:2, 3:1 (McNemar p ≥ 0.50).
- Fluctuation unchanged for the three noise-free variants; under per-step noise it rises 0.108 → 0.124 m/s
  (disjoint intervals), the k_B T_eff rise at fixed per-step σ.
- With per-step noise at dt = 0.01 s the friction factor at the largest overlap (3.75 cm) is 2.25, above 2; at
  dt = 0.005 s, 1.00. No overlap above 5 cm in any step. SFM overlap at 0.01 s (2.44 cm) agrees with the published
  2.4 cm, ORCA (1.89) with 1.9 cm.

### Task 5 — E1b_seed170, full condition, barrier 0.128 J, 0/60 escapes in E4 (macros RwFive*)
- String path (blocker 82; neighbours 15, 85, 89): snapshot → saddle 0.128 J (unstable-mode weights 15: 0.28,
  85: 0.68, blocker 0.027) → intermediate rest state M2, 21.9 J below the snapshot (|∇U| 0.001 N, Hessian positive
  definite, code force check 1e-7 N), with agents 15 and 85 moved 0.69 and 0.81 m and the blocker 0.08 m →
  exit saddle 2.82 J above M2 (first order, blocker x 9.89 m; 31 and 62 images agree) → exit.
- The 0.128 J barrier is a correct first-order saddle of U, but it is the barrier into M2, not the blocker's exit
  barrier. The exit barrier is 2.82 J from M2: β 33, 55, 77 at the E4 noise (β_ref 1.5, 2.5, 3.5).
- No body contact in M2 (blocker surface gaps 0.24–0.29 m); the pinned/alone conditions do not explain it (E4 frozen
  60/60 and alone 53/60 escape with noise set from their own barriers, 18.3 and 34.3 J).
- Restarts: every run at β_ref ≤ 1.5 reaches M2 (agents 15 and 85 move 0.73–1.08 m). Escapes: β_ref 0.25 1/20
  (300 s; exit β 5.5, harmonic mean exit time from M2 1.5e3 s); β_ref 0.5, 1.0 0/20 (300 s); β_ref 1.5 0/20 at 3600 s;
  β_ref 5.0 0/10 (300 s; 1/10 reaches M2).

### Task 6f — lone release 1 m upstream, B1's 200 positive-margin agents (new runs; macros RwSixf*)
127/200 pass [0.57, 0.70]. All 10 smallest margins (0.008–3.1 N) pass; largest margin passing 125 N, smallest held
42.5 N. Speed at x_peak for the 10 smallest margins 0.45–0.77 m/s, KE at x_peak 8.2–23.5 J, wall potential energy
gained from release to x_peak 23–44 J. Ledger, smallest margin: drive work 222 J, drag 153 J, wall work −60 J, KE
9.0 J at the farthest point. Rule "KE at x_rest > adverse work beyond x_rest" has no false passes; 47 agents are held
despite it (drag in the adverse region). The existing "none of 200 leaves" (release at the rest state) is unchanged.

## 3. FACTS 6a–6i

- **6a** Both non-lone deadlocks are pairs (2 members each): E1b seeds 45 (blocker 75, partner 56) and 101 (blocker 24,
  partner 94). K1 (blocker alone) frees them; K2 (blocker removed) holds the partner. The same two are the 2
  collective deadlocks of the 98-run default cell (seeds 42–141; E7 default 98 classified, 2 collective) and of the
  196-run set. Source data/derived/E1_keystone.json (modes.E1b.per_snapshot), data/E1/E1_runs.jsonl.
- **6b** 360 = 3 snapshots (E1b_seed72 5.83 J, seed162 20.75 J, seed192 56.31 J, alone barriers) × 6 β (1.5, 2.5, 3.5
  from E4; 5, 6, 7 from B3) × 20 restarts; 321 events, 39 censored. Source data/derived/rev2_A3.json; inputs
  data/E4/e4_escape.jsonl (alone), data/revision/B3/b3.jsonl.
- **6c** AUC 0.983 [0.914, 1.00] (bootstrap): 34 lone keystones, positives = held by RVO2 (4; margins 10.0, 37.1, 40.7,
  121 N), negatives = freed (30; margins −173 to 13.3 N; 2 freed with positive margin). Score: stuck-alone margin
  with the C3 rest drive (g_max − drive). Source data/derived/E2_analysis.json
  f_noise_vs_C3.lone_keystone.margin_predicts_C3_rvo2_failure (experiments/E2/analyze.py:311–323).
- **6d** b ∈ {0.05, 0.1, 0.2, 0.5}; largest |b| = 0.5 (26.6°), one handedness (e_perp = e rotated +90°, b > 0 only).
  Each b: 34 lone keystones × 6 deterministic runs (1 unperturbed + perturbation seeds 900–904) = 204, 816 in total,
  0 freed (Wilson upper 95% 0.10 on 34 snapshots). No noise seeds. Source data/E2/e2_quench.jsonl;
  experiments/E2/e2_quench.py:42–44.
- **6e** max over t ∈ {30, 60, 120, 300} s of |S_pred(t) − S_KM(t)| = 0.045, at t = 30 s (others 0.029, 0.027, 0.037).
  Sample E6b (C1 + σ* = 0.0467 m/s, seeds 242–427): 349 stalls (≥ 10 s between exits, first gap excluded) in 178
  runs, 263 ended by an exit, 86 censored at 600 s; prediction = mixture over 56 barriers. Descriptive, no test.
  Source data/derived/E6_analysis.json lifetimes; experiments/E6/analyze.py:49, 122–136, 170–202, 365–368.
- **6f** Not recorded in B1 (B1 released the positive-margin set only at rest; its 1 m upstream release was for the
  negative-margin set). Computed here: see Task 6f above (data/derived/rev4_T6f.json).
- **6g** Planned before any E6 run, not set by a compute window or stopping rule: TOST sample size
  n = z²·2p(1−p)/δ² with z = 2.927, p = 0.575, δ = 0.15 → 186.1. Sources: pedestrian-abs-plan wave2/SIGNATURES.md:6,
  :18; plan/FINAL_PLAN.md:257, :270, :338; wave2/COMPUTE_PLAN.md:30, :41; plan/CORRECTIONS_TABLE.md:29;
  experiments/E6/e6.py:29 range(242, 428) in the first commit a48a386 (2026-11-08); reports/B4B_REPORT.md:13.
- **6h** Flow ratio: Welch (delta-method interval of the log ratio of means, Welch–Satterthwaite df;
  experiments/fixan/fix_a7.py:103–118 ratio_means, used at D_croma_integrity.d4:268). Means (flow, fluctuation,
  gaps): Student t, n − 1 df (fix_a7.tci:85–92; experiments/E10/analyze.py:59–67). matched_ratio: Student t on the
  logs over human runs (fix_a7.py:135).
- **6i** Overhang = min over the two pair members of |y_i − 5| − w/2 (w/2 = 0.4 m), at the saved snapshot positions;
  positive = the centre lies laterally beyond the door edge. Over the 46: 0.26–59 mm, median 25 mm, all positive.
  Source experiments/revision/B5_analyze.py:9, :36, :104–112; data/derived/rev_B5.json overhang_mm.

## 4. FRAMEWORK NEEDS for deadlock-screen
(nothing in the deadlock-screen repository was touched; this lists what it would need to reproduce C3)
- Simulator flag `sfm_tau_prime` (code/sim/steering/hybrid.py: `_desired_tau_prime`; default "off", "on" replaces the
  desired force by m(v_t − v)/τ′ with τ′ = ττ_o/(τ+τ_o), v_t = τ′(W v0/τ + v0/τ_o); other values raise) and its tests
  code/tests/test_sfm_tau_prime.py (off bitwise identical; identity with desired force + drive part < 1e-9 N).
- The drive-part arm needs the existing `w2_orca_split = drive_only` mode (no new code).
- Scripts experiments/revision4/: rev4lib.py, T1_whole.py, T1_keystone.py, T1_analyze.py, T2_legacy_second.py,
  T3_dt_matched.py, T3_analyze.py, T4_croma_dt.py (E10 run with a dt override, trajectory stride round(0.04/dt), and a
  per-step contact-overlap recorder), T4_analyze.py, T5_seed170.py, T5_analyze.py, T6f_release.py, T6f_analyze.py,
  T6_facts.py, build_registry4.py, make_manifest.py, queue_rev4.sh.
- Data: data/revision4/{T1,T3,T4,T5,T6f}/ and data/derived/rev4_T{1,2,3,4,5,6,6f}.json (hashes in MANIFEST.json).
- Registry: copy notes/C3_items/revision4.yaml to paper/registry/revision4.yaml (prefix Rw, no clash with existing
  prefixes; checked by build_registry4.py) and add it to the make_numbers inputs.

## 5. INPUTS NEEDED FROM THE AUTHOR
1. Task 4 used 10 runs per variant (cost rule). Rerun the other 15 per variant at dt = 0.005 s (≈ 6 CPU-h process
   time; the dt = 0.01 s runs exist)? Also: the noise variant at dt = 0.01 s reaches friction factor 2.25 > 2 at its
   largest overlap; decide whether the paper states it (flows and completion are unchanged at dt = 0.005 s).
2. Task 5: the 0.128 J barrier of E1b_seed170 is not its exit barrier (2.82 J from M2). E4 set the noise for this
   snapshot from 0.128 J (β_ref 1.5–3.5), so its full-condition β is 33–77 against the exit barrier. No re-fit was done, as instructed; decide whether the text
   reports this snapshot as "barrier into an adjacent rest state" or the full-condition analysis drops/reassigns it.
3. Task 5 "higher β": run literally both ways (lower β_ref = more noise: 0.25, 0.5, 1.0; higher β_ref 5.0; longer
   horizon at 1.5). Say if only one direction was meant.
4. Task 3: the √dt-scaled arm was run at all three dt (at 0.01 s it coincides with per-step). Use it or only per-step.
5. Task 6f: Sect. 5.1 wording — release at rest (0/200 pass) vs release 1 m upstream (127/200 pass) are different
   statements; the text should name the release point.

## CPU time
Summed per-job wall seconds (inflated by other processes; load average 14–236 during the session), 6 workers on 8
cores: T1 whole runs 8.3 h, T1 keystone tests 1.3 h, T3 15.4 h, T4 11.5 h (process CPU 5.9 h), T5 restarts 4.5 h,
T5 strings 0.9 h, T6f 0.3 h; total ≈ 42 job-hours. Queue (queue_rev4.sh) 05:37–10:57; T1 ran before it. Nothing
lost; T5 round 1 discarded (not a rest state); T6f run serially after a fork-pool hang (no data lost).

## HANDOFF
- State: all six tasks done; T4 reduced to 10 runs per variant (cost rule). Committed on main (see git log for
  "C3"). No existing paper number changed.
- For the writing session (paper/ not edited here): copy notes/C3_items/revision4.yaml to
  paper/registry/revision4.yaml and register it with make_numbers; macro prefix Rw (317 macros; rendered preview
  notes/C3_items/revision4_numbers.tex). Per-item notes notes/C3_items/T1–T6f.md.
- Text items: Sect. 5.1 release point (6f); E1b_seed170 barrier (Task 5); per-step noise friction factor at
  dt = 0.01 s (Task 4); attribution sentence (Task 1: the drive part and τ′ SFM each beat RVO2 and leave no moving
  failure).
- Open: author decisions in section 5; optional 15 more CroMa runs per variant at dt = 0.005 s.
