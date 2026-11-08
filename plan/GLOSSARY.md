# Glossary for the fix wave (G1–G6)

Source: reports/audit/FIX_PLAN.md §3, with the rulings of plan/FIXWAVE_DECISIONS.md (D1–D16) applied. Where the two differ, this file follows the decisions. Every section, caption and figure tick label uses these words; the "Replace" column lists wording that must not appear.

## G1 Deadlocks, outcomes and mechanism classes

| Concept | Use | Replace |
|---|---|---|
| Deadlock *types* (two) | **lone trap**; **pair standoff** ("pair standoff at the jamb faces") | "two classes" of deadlock → "two types"; "symmetric" standoff |
| Keystone *outcomes* (three) | **lone keystone**, **second trap**, **group standoff** | "collective" as an outcome; "three classes" of outcome |
| Mechanism *classes* (five) | **P, L, T, D, N**; "five mechanism classes"; Table 2 carries a row for N | — |
| Escape with mobile neighbours | "collective activated escape" (only this sense); the causal clause "because the neighbours give way" is replaced by the participation-ratio statement | "collective" in any other sense |
| Soft-core arches (D7) | keep "arch"; one framing sentence in §5.3 and §8: "soft-core analogues of arches, held by repulsion of range $B_w$ rather than by contact and friction" | no renaming |

## G2 Barrier conditions and probes

| Concept | Use | Replace |
|---|---|---|
| Barrier conditions | **full**, **pinned**, **alone** | "frozen" for the neighbours-held condition |
| Probe | **rest-drive push**, signed: + towards the door, − away | "frozen-mean arm"; "frozen ±" (also in Fig. 6/7 tick labels, D3b) |

## G3 Interventions, calibration, modes

| Concept | Use | Replace |
|---|---|---|
| Interventions | **intervention**; **control** (the matched one); **resolver** (the paradigm) | "arm" everywhere; Table 3 column "Arm" → "Control" |
| Calibration | **not used in the calibration** | "held out", "held-out" |
| Signatures outside Table 2 (D5) | "descriptive signatures beyond Table 2" for J, time to free ($t_{1/2}$), final-state class and stall survival | any statement of when signatures were fixed ("before the runs", "before they are measured", "pre-registered") |
| Modes | **published-reproduction mode**, **corrected-forward mode**, defined once in §3; "new results use the corrected-forward mode" | "forward claims", "declared modes", "the corrected mode" before its definition |
| Trial vocabulary | — | "arm", "held out", "pre-registered", "endpoint", "trial", "equivalence margin" |

## G4 Symbols

| Symbol | Meaning | Replace |
|---|---|---|
| λ | escape rate | λ₁ for an eigenvalue |
| μ₁ | softest Hessian eigenvalue | λ₁ |
| $b_f$ | per-snapshot fold threshold ("fold" kept only if run-N6 shows saddle-node scaling; otherwise "loss of the minimum at $b_f$") | $b^\ast$ used as a threshold |
| $b^\ast$ | matched bias | — |
| $B_{w,\rm edge}$ | jamb-only short range | "$B_w=0.04$" for the jamb-only variant |
| β | $\Delta U/k_BT_{\rm eff}$, defined once at Eq. (10) | redefinitions |

## G5 Matched quantity and identity

| Concept | Use | Replace |
|---|---|---|
| Matched quantity | **rate**: "freed fraction" for snapshots, "completion fraction" for whole runs | "completion rate" when the snapshot match is meant |
| Identity, J (D3a) | a separating signature **only at the pair block**. At the lone trap and in whole runs, separation rests on replay, Δt, time to free and final-state class; there the failure sets overlap at least as much as a stochastic resolver overlaps with itself | "frees different deadlocks" (lone trap, whole runs) |
| Agreement criterion (D4) | a probe separates two resolvers when their 95% intervals for that signature exclude each other, or when one shows the predicted effect and the other its absence; replay and handedness are exact counts | arbitrary margins (±0.10) |
| Multiplicity (D6) | "The probes are read jointly as a signature, not as a family of tests, so no correction is applied." | — |
| Contribution (D3c) | the protocol, not the principle; equifinality cited to Beven 2006 | new keywords |
| ORCA scope (D2, D8, D11) | ORCA used as an **additive force**; velocity-level ORCA outside scope (text only); regime: the last agents at a narrow door, at the end of an evacuation | unscoped "ORCA adds a goal drive" |

## G6 Conventions

British spelling; "vermilion"; minus signs in math mode; `\,` between number and unit; intervals as "[lo, hi]"; one sentence "All bracketed intervals are 95%." in §3. p-values plain for p ≥ 0.01, scientific below. Category tick labels count as axis labels (D3b) and use these words. Captions at most two sentences, about 60 words.
