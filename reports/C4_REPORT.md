FINAL
# C4 report: barrier energy-span check and CroMa completion at dt = 0.005 s

Registry notes/C4_items/revision5.yaml (prefix Rx, 246 entries + 4 p-value companions = 250 rendered macros; built by
experiments/revision5/build_registry5.py from notes/C4_items/X*.yaml; no collision with paper/registry/*.yaml or with
C3's notes/C3_items/revision4.yaml (Rw); validated with tools/make_numbers.py on a scratch copy of the registry,
rendered preview notes/C4_items/revision5_numbers.tex). Sources data/derived/rev5_X1.json, rev5_X2.json; scripts
experiments/revision5/; raw data/revision5/X1/, data/revision5/X2/; notes notes/C4_items/X1.md, X2.md; manifest
data/revision5/MANIFEST.json (sha256 of every raw and derived file, including the uncommitted trajectories and the
C3 trajectories read for seeds 42–51). No number already in the paper was overwritten. No simulator code changed.

## 1. Status per task

| task | status | note |
|---|---|---|
| 1 energy span | done | gate stored no images, so all 132 strings were recomputed with the gate's code and settings; every recomputed barrier equals the stored one exactly (max relative difference 0.0) |
| 1 re-analysis | done | E4 slope ratios, pooled slope, E3 slopes and matched-noise β with ΔU_span, alongside the published values |
| 2 CroMa 25 runs at dt = 0.005 s | done, complete | 60 + 60 runs (seeds 52–66 at 0.005 s and, for the overlap record, at 0.01 s), 8.03 process CPU-h < 10 |

## 2. NUMBERS FOR THE PAPER

### Task 1: energy span (macros RxSpan*, RxEfour*, RxPool*, RxEthree*, RxBeta*)
Path = string images from the snapshot minimum to the first image with blocker x ≥ 10 m; ΔU_rep(img) = max E − E₀;
ΔU_span = max_{i<j}(E_j − E_i); interior minimum = swing ≥ 0.05 J on both sides; affected = span differs from rep by
> 1%. ΔU_span for re-analysis = climbing-image exit barrier from the relaxed interior rest state (gate acceptance rules).

| condition | affected / 56 | snapshot ids | interior minima |
|---|---|---|---|
| alone | 0 (RxSpanAffAlone) | — | 0 |
| pinned | 0 (RxSpanAffPinned) | — | 0 |
| full | 8 (RxSpanAffFull) | E1b seeds 46, 60, 111, 130, 170, 223, 230, 237 | 10 (also 74, 104: span = rep) |
| rejected full (4) | 2 (RxSpanAffRejected) | 75, 209 | 3 (also 174: span = rep) |

| snapshot | ΔU_rep (J) | first saddle (J, images) | interior rest state M: U − U(s₀) (J) | exit barrier from M (J), accepted | ΔU_span (J) | kind |
|---|---|---|---|---|---|---|
| seed46 | 2.35 | 0 | −12.91 | 15.25, yes | 15.25 | A |
| seed60 | 0.021 | 0 | −9.96 | 3.36, yes | 3.36 | B |
| seed111 | 0.557 | 0 | −9.09 | 9.65, yes | 9.65 | A |
| seed130 | 1.18 | 0.19 | −7.98 | 9.16, yes | 9.16 | A |
| seed170 | 0.128 | 0.12 | −21.87 | 2.82, yes | 2.82 | B |
| seed223 | 0.069 | 0.06 | −9.95 | 3.68, yes | 3.68 | B |
| seed230 | 10.47 | 0.26 | −6.01 | 16.48, yes | 16.48 | A |
| seed237 | 10.26 | 0.13 | −6.52 | 16.79, yes | 16.79 | A |
| (rej.) seed75 | 0.012 | 0 | −13.49 | 8.50, yes | 8.50 | B |
| (rej.) seed209 | 0.000 | 0 | −11.94 | 0.74, yes | 0.74 | B |

Kind A (RxSpanKindA = 5): ΔU_rep is the exit saddle measured from the snapshot, which lies 6.0–12.9 J above a deeper
rest state M on the path. Kind B (RxSpanKindB = 3): ΔU_rep is a 0.02–0.13 J saddle into M, and the exit saddle lies
below the snapshot energy. In M the blocker is at x = 9.66–9.76 m, still upstream of the door. **For these 8
full-condition snapshots, and for rejected strings 75 and 209, the Kramers rate with ΔU_rep is not the rate of escape
to the exit.** For all 56 pinned and alone barriers it is.

Arrhenius set (10 snapshots): affected only in the full condition, seeds 170, 237 and 60 (60 was not run in full). Time-step set
(20 snapshots): affected seed237 only. The same estimators, seeds and exclusions were used. Run with no substitution,
the code reproduces E4_analysis.json and E3_analysis.json headlines exactly.

| quantity | published | with ΔU_span | macros |
|---|---|---|---|
| E4 slope ratio median, full (fits; intervals covering 1) | 1.15 (8; 7) | 1.11 (8; 7) | RxEfourRatioMedFull{Pub,Span} |
| E4 slope ratio, full, seed237 [bootstrap 95%] | 1.43 [0.89, 2.06] | 0.87 [0.54, 1.26] | RxEfourTwoThirtySevenRatio* |
| E4 slope ratio median, pinned / alone | 0.95 / 0.87 | unchanged | RxEfourRatioMed{Pinned,Alone}* |
| pooled slope, free intercepts (snapshot bootstrap 95%) | −0.93 [−0.98, −0.88] | −0.92 [−0.97, −0.87] | RxPoolSlope{Pub,PubRefit,Span}* |
| E3 OLS slope of observed on predicted ℓ (bootstrap 95%) | 0.72 [0.29, 1.06] | 0.93 [0.69, 1.20] | RxEthreeOls* |
| E3 through-origin ratio Σobs/Σpred (bootstrap 95%) | 0.91 [0.83, 1.01] | 0.89 [0.83, 0.95] | RxEthreeOrigin* |
| E3 snapshot intervals covering the prediction | 16/20 | 17/20 | RxEthreeCover* |
| E3 ℓ seed237, observed [95%] vs predicted | 4.23 [3.15, 5.30] vs 2.21 | vs 3.62 | — |
| β < 1 at σ = 0.07 m/s (Wilson 95% of the fraction) | 36/56 [0.51, 0.76] | 35/56 [0.49, 0.74] | RxBetaSeven{Pub,Span}BelowOne* |
| median β at σ = 0.07 m/s [IQR] | 0.64 [0.15, 1.61] | 0.74 [0.28, 1.72] | RxBetaSeven{Pub,Span}{Med,Qone,Qthree} |
| β < 1 / median at σ = 0.0717 m/s | 36/56, 0.61 | 35/56, 0.71 | RxBetaRefined* |
| β < 1 / median at σ* = 0.0467 m/s | 23/56, 1.43 | 20/56, 1.67 | RxBetaStar* |

The pooled-slope refit (RxPoolSlopePubRefit) runs fix_a3.collapse_part on a fresh PCG64(fix_a3.SEED). It reproduces the
published point estimate exactly and its interval to bootstrap resolution, because fix_a3.main draws other bootstraps
from the same generator first. Use the published macros for the published value and RxPoolSlopeSpan for the
alternative.

### Task 2: CroMa, 25 runs per variant at both time steps (macros RxCro{Sfm,Edge,Orca,Sig}{Half,Full}*)
Flow ratio interval: delta method on the log of the ratio of mean flows, **Welch–Satterthwaite** df
(fix_a7.ratio_means via D_croma_integrity.d4, as Sect. 7). Fluctuation: Student t over runs. Friction factor
2κh·dt/m at the largest agent overlap (κ = 2.4e5 kg/(m s), m = 80 kg; stable below 2).

| variant | dt (s) | complete / deadlock / moving | flow ratio [95%] | fluctuation (m/s) [95%] | max overlap agent / wall (cm) | friction factor | inside 0.01 s interval |
|---|---|---|---|---|---|---|---|
| SFM | 0.005 | 1/24/0 | 0.51 [0.42, 0.60] | 0.093 [0.092, 0.094] | 2.40 / 3.08 | 0.72 | yes |
| SFM | 0.01 | 2/23/0 | 0.50 [0.42, 0.59] | 0.092 [0.091, 0.093] | 2.44 / 2.58 | 1.47 | — |
| jamb range | 0.005 | 23/2/0 | 0.55 [0.46, 0.66] | 0.095 [0.093, 0.096] | 2.29 / 3.08 | 0.69 | yes |
| jamb range | 0.01 | 21/4/0 | 0.56 [0.47, 0.67] | 0.094 [0.092, 0.095] | 2.46 / 2.73 | 1.48 | — |
| force-coupled ORCA (RVO2) | 0.005 | 11/0/14 | 0.59 [0.49, 0.70] | 0.098 [0.097, 0.099] | 1.85 / 3.09 | 0.55 | yes |
| force-coupled ORCA (RVO2) | 0.01 | 10/1/14 | 0.60 [0.50, 0.71] | 0.100 [0.098, 0.101] | 1.89 / 2.59 | 1.14 | — |
| noise σ* | 0.005 | 22/0/3 | 0.41 [0.34, 0.49] | 0.124 [0.123, 0.125] | 3.92 / 3.10 | 1.18 | yes |
| noise σ* | 0.01 | 18/0/7 | 0.40 [0.33, 0.48] | 0.108 [0.107, 0.109] | 3.75 / 2.62 | 2.25 | — |

- The dt = 0.01 s rows are the published 25-run values (all 100 records reproduce D3).
- **All four dt = 0.005 s ratios lie inside the dt = 0.01 s intervals.**
- Paired by seed, the geometric-mean flow ratio dt 0.005 / 0.01 [t interval on the logs] is 1.01 [0.98, 1.05],
  0.98 [0.96, 1.01], 0.98 [0.96, 1.01] and 1.03 [0.86, 1.23] (RxCro*Paired*). Completion discordance is 1:2, 2:0, 4:3
  and 5:1, with exact McNemar p = 1.0, 0.50, 1.0 and 0.22 (RxCro*McNemarP).
- Under per-step noise the fluctuation rises from 0.108 to 0.124 m/s, with disjoint intervals; for the other variants
  it does not change.
- No step has an overlap above 5 cm. The friction factor exceeds 2 only for noise at dt = 0.01 s: 1 run of 25
  (seed 46, 3.75 cm at t = 1.17 s, RxCroSigFullFrictionRunsGeTwo).

## 3. FINDINGS that affect existing statements
1. **Sect. 4.5 (Barriers from the String Method) / Sect. 5.2 (Noise-Driven Escape):** ΔU is defined as the barrier
   "from the snapshot minimum to an exit", taken as the highest point above the snapshot. For 8 of the 56 full
   barriers the path passes a deeper rest state, so the rate-limiting climb is the energy span: 2.8–16.8 J against
   reported 0.02–10.5 J. Pinned and alone barriers are unaffected. A definition sentence ("ΔU is the largest rise
   along the path, which equals the saddle height above the snapshot except for 8 full-condition paths that pass a
   deeper rest state") would cover it; the published numbers are left as they are.
2. **Sect. 5.2, line 41, "the full condition omits … one (\EfourSeedOneSeventyDU J) that never escapes in 300 s":**
   seed170's exit barrier is 2.82 J (C3 and here). The snapshot "below the 0.1 J noise floor" is seed60. Its reported
   0.021 J is a saddle into a rest state 10.0 J lower, and its exit barrier is 3.36 J, not below the floor.
3. **Sect. 5.2, Arrhenius results:** the largest full-condition slope ratio (seed237, 1.43) becomes 0.87 with the span.
   The full median goes from 1.15 to 1.11 and the pooled slope from −0.93 to −0.92; both stay inside the published
   intervals. No statement changes; the full-condition ratio above 1 is partly the seed237 barrier.
4. **Time-step probe (Sect. 4.4 / Fig. 6(c), E3):** seed237's ℓ misfit (4.23 observed against 2.21 predicted) is
   resolved by the span (3.62 predicted). The E3 OLS slope moves from 0.72 to 0.93 and the through-origin ratio from
   0.91 [0.83, 1.01] to 0.89 [0.83, 0.95], so the interval no longer covers 1. Text using these values (they are not
   in the current sections; macros EthreeSlope*) should name the barrier definition.
5. **Sect. 5.2, line 44 (matched noise, σ = 0.07 m/s, β median 0.64, 36 of 56 below 1)** and **Sect. 6.2 (σ*: 23 of
   56 below 1):** with the span the values are 0.74 and 35/56, and at σ* 20/56. The conclusion ("this noise acts by
   fluctuations") stands.
6. **Sect. 6.2 stall prediction** (mixture over the 56 barriers, ν e^{−β}): 8 of the 56 barriers are not exit
   barriers; the prediction was not recomputed here.
7. **E3 selection rule** (ΔU ≥ 3 J; 36 qualify): with the span, 41 qualify (seeds 46, 60, 111, 130, 223 enter). The
   drawn set is unchanged; the rule text is correct as written for ΔU_rep.
8. **Sect. 7 (CroMa):** completing C3 to 25 runs confirms the time-step independence of all four flow ratios, and
   completion and fluctuation stay unchanged except the noise fluctuation. The noise variant at dt = 0.01 s exceeds
   the explicit-friction bound in 1 of 25 runs (factor 2.25; 1.18 at dt = 0.005 s). Flows and counts do not depend
   on it.
9. Wall overlap maxima are larger at dt = 0.005 s (3.08–3.10 cm) than at 0.01 s (2.58–2.73 cm) in every variant. If
   the paper quotes a wall overlap, it should name dt.

## 4. FRAMEWORK NEEDS (for /Users/palaash/Developer/deadlock-screen; nothing there was touched)
- **String output:** the barrier step should keep the converged images, U(s_k) − U(s₀) and the coordinates, and report
  the energy span next to the saddle height. Add an interior-minimum check (zigzag, swing threshold): relax each
  interior minimum and run the gate's string from it to the exit. Cut the path at the door plane (x ≥ 10 m), because
  the string tail beyond it is not a minimum path. Reference implementations: experiments/revision5/X1_span_paths.py
  (`zigzag`, `interior_minima`, `span`, `run`) and X1_analyze.py (`per_path`, `kind`).
- **Analysis builders:** E4/E3/A3 re-analysis with a substituted barrier (X1_analyze.rean_E4, rean_E3, rean_A3; they
  wrap the unchanged experiments/E4/analyze.py, E3/analyze.py, fixan/fix_a3.collapse_part and
  revision/A3_beta.stats).
- **CroMa time-step runner:** experiments/revision5/X2_croma_dt.py, a budget-capped queue over C3's
  T4_croma_dt.run, and X2_analyze.py, which merges the C3 and C4 records per seed.
- **Registry builder:** experiments/revision5/build_registry5.py.
- **Data:** data/revision5/X1/x1_paths.jsonl, data/revision5/X2/x2_croma.jsonl, data/derived/rev5_X1.json,
  rev5_X2.json, and data/revision5/MANIFEST.json. The trajectories data/revision5/X2/raw/ (389 MB) and the C3
  trajectories (265 MB, C3 worktree) are not committed; their hashes are in the manifest.
- **Registry:** copy notes/C4_items/revision5.yaml to paper/registry/revision5.yaml (prefix Rx), and also C3's
  revision4.yaml if it is not there yet.

## 5. INPUTS NEEDED FROM THE AUTHOR
1. Barrier definition: keep ΔU_rep with a sentence naming the 8 full-condition exceptions, or switch the full-condition
   ΔU to the energy span (numbers above, alternative macros ready). Switching would also change σ for future runs set
   from ΔU, and the E3 qualifying set.
2. Sect. 5.2 wording for the two full-condition omissions: seed60 (span 3.36 J, not below the floor) and seed170 (exit
   barrier 2.82 J).
3. Whether the Sect. 6.2 stall prediction should be recomputed with ΔU_span (not done; not requested).
4. Whether Sect. 7 states the noise-variant friction factor at dt = 0.01 s (1 of 25 runs above 2).

## CPU time
X1 strings 8.8 process CPU-h (132 jobs; 3 workers). X2 CroMa 8.03 process CPU-h (120 runs; 3 workers). The two ran
concurrently, 6 workers on 8 cores. For about 25 min a 7th worker ran: the single-snapshot seed170 test, whose records
are kept, ran alongside. The wall time was 3.1 h for X1 and 3.4 h for X2, inflated by unrelated jobs on the machine
(load average up to ~56). Nothing was lost. One restart: the first X1 run was stopped after about 25 min, before any
record was written, to add the door-plane cut that avoids second strings on post-exit artefact minima.

## HANDOFF
- State: both tasks done and committed on main (see git log "C4"). No paper number changed and paper/ was not
  edited.
- For the writing session: copy notes/C4_items/revision5.yaml to paper/registry/revision5.yaml and register it with
  make_numbers (prefix Rx; preview notes/C4_items/revision5_numbers.tex). Per-task notes are notes/C4_items/X1.md and
  X2.md. Findings 1–9 list the sections concerned.
- Decisions made: path cut at the door plane; swing threshold 0.05 J; span refinement by the gate's own string and
  climbing image from the relaxed rest state; pooled-slope refit on a fresh generator, reported with the published
  value; all 25 CroMa runs at both time steps (budget not reached).
- Open: author inputs 1–4; the Sect. 6.2 stall prediction with ΔU_span; C3's 15-run item is now closed.
