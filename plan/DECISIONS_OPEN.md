# Decisions (Plan v1)

Status as of Plan v1 (plan/FINAL_PLAN.md, 2026-11-02). Decisions D1–D8 of wave2/DECISIONS_NEEDED.md remain applied as before. Items below that are resolved carry the decision text; only the derivation sign-offs T1–T5 remain open.

## 1. Derivation sign-offs [NEEDS PALAASH: derivation sign-off] (OPEN)
Each derivation is stated in plan/FINAL_PLAN.md §8 with its evidence file. Check each against the code lines cited there. None blocks E1–E4.

| # | Item | What to check | Where |
|---|---|---|---|
| T1 | Rest-state lemma, dissipative form | G(x, 0) = 0 and v·G(x, v) ≤ 0 near rest imply that the fixed points and their Lyapunov stability are unchanged. Check the sign convention for SFM sliding friction (sfm.py:106-108) and wall friction (walls.py), and that the TTC force is identically zero in a neighbourhood of v = 0 (ttc.py:91-97: the 1e-8 test). Stated for the noise-free skeleton only. | FINAL_PLAN §8 T1 |
| T2 | Stuck-alone criterion and the k = 3 rule | g_max(r) > m·v_eff/τ, with g_max from the code's wall force on the door axis; and "exits iff ≥ k = 3 others are active at arrival". k is fitted; production reports its leave-one-seed-out accuracy and AUC (E1). | FINAL_PLAN §8 T2 |
| T3 | T_eff form | k_BT_eff = m·σ²/(1 − (1 − dt/τ)²), per agent with its own τ. Check the variance identity for the clamp-then-noise order (published numerics) and for noise-before-position (numerics = fixed). | FINAL_PLAN §8 T3 |
| T4 | Collective Kramers escape over string-method barriers | The 2N-D minimum-energy path with all residual agents mobile; the Arrhenius slope test (slope = barrier within ≈ 25%); the conservative rest field with density frozen (2e-7 N); the density switch along the path ignored. | FINAL_PLAN §8 T4 |
| T5 | Pair Hessian and fold | Hessian of U at the pair state, density frozen: positive definite in 26/26, softest mode the common lateral shift (48–129 N/m, median 89); fold reading of the bias threshold (static prediction 182/182; wave2b/data/a5_predict.json, a5_analysis.json). | FINAL_PLAN §8 T5 |

## 2. People and permissions (RESOLVED)
- **D-open-1 Second author — RESOLVED.** Decision: the second author agrees to every change. The earlier request for missing data and scripts is not needed by Plan v1 (FD dropped; every number regenerated) and is not pursued as a blocking item.
- **D-open-2 Correction notice — RESOLVED.** Decision: no correction notice to the proceedings will be pursued. Revisions of conference findings appear compactly in paper Table 4 and one short paragraph (§6.3).
- **D-open-3 Disclosure wording — RESOLVED.** Decision: handled at the writing stage, by the authors.
- **D-open-4 Signed SCITEPRESS copyright form — RESOLVED.** Decision: handled at the writing stage. Every figure is regenerated from new runs regardless.
- **D-open-5 Repository — RESOLVED.** Decision: a new GitHub execution repo later, separate and secondary. Nothing is pushed in the meantime.

## 3. Content decisions (RESOLVED / APPLIED)
- **D-open-6 Pair-class weight — APPLIED.** Decision: a secondary strand of about 3 pages across paper §5.2 and §6.2, with Figure 6 and rows of Table 3.
- **D-open-7 FD calibration — APPLIED.** Decision: FD claims dropped; no FD experiment. The cause of the anomalous FD (grouping by frame number across concatenated runs: sim/data/fundamental_diagram.py:29 with sim/data/loader.py:109-120) is recorded as a Table 4 row (plan/CORRECTIONS_TABLE.md E3).
- **D-open-8 C4 crush — APPLIED.** Decision: the crush term is present and declared in published-reproduction mode, and OFF in corrected-forward mode. Needs a new default-off flag (proposed `w2_crush`), implemented before E8/E9.
- **D-open-9 Venue facts — RESOLVED.** Decision: length 23–25 pages including references; LNCS template fetched from Springer; at least 30% new material (target well over 70%); conference paper cited; conference tables/figures regenerated with source cited; no large verbatim blocks; different title, abstract and conclusions; a short statement of the main differences; PRIMORIS with the Licence to Publish. The deadline is not recorded in the repo; take it from the invitation.
- **D-open-10 Wall-corner rule — APPLIED.** Decision: in corrected-forward mode, walls sharing an end use the nearest point on the union of walls, with no double counting; published-reproduction keeps the segment sum. Needs a new default-off flag (proposed `w2_wall_corner`), implemented before E10. E10 no longer repeats each cell under both rules.
