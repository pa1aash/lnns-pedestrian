# Table 2 — cell provenance

Source: `plan/FINAL_PLAN.md` §9. Line numbers refer to that file at commit b3984b2.
Classes table = lines 240–246; signatures S1–S9g = lines 264–278; note on the full-ORCA reversal = line 280.
`table2_signatures.tex` is `\input` in §4 of `main.tex`; `booktabs` and `tabularx` are loaded there.
Change C14 (batch 2B): last column renamed "Corrected numerics"; P, L, T, D read "persists", N keeps "effect disappears"; D cells under both Δt columns read "no Δt dependence".

Kinds of provenance:
- **direct**: the cell restates what the plan line says.
- **definition**: follows from the class definition on that line, with no extra physics.
- **complement**: inferred by contrast with the N row (line 246); the plan states no prediction for that cell. [NEEDS PALAASH: keep or replace with ---]
- **---**: the plan gives no prediction for this class under this probe; the probe does not test the class.

| Class | Probe | Cell | Plan line(s) | Kind |
|---|---|---|---|---|
| P | quench | held, as without it | 242 ("quench from a frozen deadlock = C1"; C1 holds the frozen state) | direct |
| P | 1e-9 m replay | held, as without it | 242 ("no effect on a frozen state") | definition |
| P | Δt, fixed per-step noise | held, as without it | 242 | definition |
| P | Δt, √Δt-scaled noise | held, as without it | 242 | definition |
| P | constant push ± | as without it | 242 | definition |
| P | lateral tilt b → −b | as without it | 242 | definition |
| P | corrected numerics | persists | C14 | direct |
| L | quench | frees deterministically | 243 ("an added deterministic drive moves or removes the fixed point"; "deterministic") | direct |
| L | 1e-9 m replay | identical replays | 243 ("seed replay D = 0"); 265 S2 ("L/D iff D = 0 and SD = 0") | direct |
| L | Δt, fixed per-step noise | no Δt dependence | 243 ("Δt-flat"); 264 S1 ("L for ORCA iff C3 ≡ 0") | direct |
| L | Δt, √Δt-scaled noise | no Δt dependence | 243 ("Δt-flat") | direct |
| L | constant push ± | + frees, − does not | 243 ("frozen-mean + frees and − does not"); 266 S3 | direct |
| L | lateral tilt | --- | none (S8, line 271, is a lone-trap negative control, not an L prediction) | --- |
| L | corrected numerics | persists | 246; C14 | complement |
| T | quench | frees at random times; exponential escape; ln rate linear in 1/k_BT_eff with slope −ΔU | 244 ("stochastic", "exponential escape", "Arrhenius slope = barrier"); 269 S6 (Weibull k ≡ 1); 277 S9f | direct |
| T | 1e-9 m replay | replays disagree | 244 ("stochastic (D > 0)"); 265 S2 ("T iff D > 0") | direct |
| T | Δt, fixed per-step noise | rate falls as Δt grows, since k_BT_eff ∝ 1/Δt | 244 ("Δt-dependent at fixed per-step σ"); 264 S1 (per_step ℓ = ln[λ(0.005)/λ(0.02)] > 0); §8 T3 line 210 ("kT ∝ 1/dt") | direct |
| T | Δt, √Δt-scaled noise | no Δt dependence | 244 ("flat when σ is √Δt-scaled"); 264 S1 ("dt_scaled ≡ 0") | direct |
| T | constant push ± | --- | none | --- |
| T | lateral tilt | --- | none | --- |
| T | corrected numerics | persists | 246; C14 | complement |
| D | quench | frees only beyond a finite fold threshold b* | 245 ("fold threshold", "finite"); 272 S9a | direct |
| D | 1e-9 m replay | identical replays; infinitesimal perturbation does not free | 245 ("deterministic"); 265 S2 ("L/D iff D = 0"); 273 S9b (1e-9 m frees ≤ 0.10) | direct |
| D | Δt, fixed per-step noise | no Δt dependence | definition: a static tilt is deterministic | definition |
| D | Δt, √Δt-scaled noise | no Δt dependence | definition: a static tilt is deterministic | definition |
| D | constant push ± | --- | none | --- |
| D | lateral tilt b → −b | same rate; first member out switches side | 245 ("sign-symmetric in rate under reversal, handedness of the first agent out flips"); 276 S9e | direct |
| D | corrected numerics | persists | 246; C14 | complement |
| N | quench … lateral tilt | --- | none | --- |
| N | corrected numerics | effect disappears | 246 ("disappears in the corrected mode or open geometry") | direct |

## Points for review

1. The batch brief's example cell "rises with dt" for T is the opposite of the plan. At fixed per-step σ,
   k_BT_eff = mσ²τ/(2Δt)·[1 − Δt/2τ]⁻¹ ∝ 1/Δt (T3, lines 208 and 210), and S1 predicts ℓ = ln[λ(0.005)/λ(0.02)] > 0,
   so the escape rate **falls** as Δt grows. The table follows the plan.
2. The "replay, 1e-9 m perturbation" column merges two plan probes: seed replay (S2, K = 5 replicates) and the
   1e-9 m perturbation (S9b). For T the cell reads "replays disagree" (S2); for D it carries both.
3. Rest-state lemma (line 248) and the drive/constraint split (S4, S9d) are not columns; they belong in the text or Table 3.
4. Vocabulary follows C6 (physics framing); "held" and "frees" refer to the frozen state.

W2 (2026-11-09, page plan C35): headers shortened (probes are listed in the §4 text); P cells "held"/"unchanged" (same meaning as "held, as without it"); T quench "frees at random, exponential times" (the ln-rate slope prediction is stated in §4.3); D quench "frees only beyond b*", D replay "identical replays"; the N row moved into the caption ("tested only by corrected numerics, under which its effect disappears"). No prediction was changed.
