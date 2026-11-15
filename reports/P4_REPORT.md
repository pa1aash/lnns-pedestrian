# P4: energy-span reruns, figure update and final text fixes

Base: origin/main `4b49eeb` (P3). Build: `make numbers tables` and `latexmk` in `paper/` (as `make paper`).

## 1. Status per task

| # | Task | Status |
|---|---|---|
| 1 | Energy-span reruns | done (details below) |
| 1 | Refactor and regression test | `experiments/E6/analyze.py`: `barrier_picture(sigma, nu, barriers=None)` takes a list `[(snapshot id, ΔU in J), …]`. `None` means `reported_barriers()`, the published list, which is now its own function; `blocker_taus()` is split out too. `experiments/revision6/test_barrier_picture.py` checks three things: with the reported list passed explicitly, and with the default, the output equals `E6_analysis.json` `lifetimes.barrier_picture` exactly (every key, rows included) and reproduces `pred_vs_obs.max_abs_diff` = 0.04509486429131537 exactly; the span list changes exactly 8 barriers, each upwards. Result: `3 passed`. Run with `.venv/bin/python experiments/revision6/test_barrier_picture.py`, or with pytest. |
| 1a | Stall prediction with the 56 span barriers | `experiments/revision6/P4_span.py` → `data/derived/rev6_P4.json`. **Statistic** (the one the code computes): the maximum over t = 30, 60, 120 and 300 s of \|S_pred(t) − S_KM(t)\|. S_KM is the Kaplan–Meier survival of observed noise stalls; S_pred is the equal-weight mixture of exponential lifetimes ν·exp(−ΔU/k_BT_eff(σ*, τ_blocker)), conditioned on lasting ≥ 10 s. It is not a supremum over all t. **Reported barriers 0.045, span 0.070** (maximum at 30 s). The prediction lies above the observation at all four times, by 0.070, 0.050, 0.047 and 0.052. The attempt rate ν (median full-condition E4 fit) is the same with the span (0.1253). Predicted median stall lifetime: 69 s with the reported barriers, 78 s with the span, against 59 s observed (not printed). |
| 1b | E3 time-step prediction | X1's `rean_E3` re-run: predicted pooled ℓ at β₀ = 1.5 is 2.22 (reported) and 2.36 (span), against observed 2.16 [1.80, 2.70]. Printed at the paper's two-significant-figure rule as 2.4. The prediction at β₀ = 2.5 (3.70) does not change. |
| 1c | Escape figure | `figures/fig_escape_dt.py` now reads the span re-runs of E4 (panels a, b) and E3 (panel c) from `data/revision6/P4/`. It asserts that the pinned and alone entries equal the published `E4_analysis.json`. Seed 237 (full) moves from ΔU = 10.3 J, ratio 1.43 [0.89, 2.06] to ΔU = 16.8 J, ratio 0.87 [0.54, 1.26]; seed 170 has no fit either way. In panel (c) the β₀ = 1.5 per-step prediction curve shifts (value at Δt = 0.02 s from 0.238 to 0.218 relative to 0.01 s). The plotted full median is now 1.1, as in the text. No other figure shows full-condition barriers. Style, colours and fonts are unchanged (smallest font 7 pt; the figure is 12.2 cm wide, printed at scale 1); there are no labels inside the panels. The caption keeps its three sentences; only "reported barrier" became "energy span". |
| 1 | Correction in the E3 re-run | X1's `rean_E3` scales ΔU, β and ℓ_pred for the substituted snapshot but leaves `beta_ref` at 1.5. As a result, `fig5_cache`'s prediction curve is no longer normalised to 1 at Δt = 0.01 s (it gave 0.897). `P4_span.fix_fig5_pred` rebuilds the curves with β_ref·ΔU_span/ΔU_rep for that snapshot. The same formula with no substitution reproduces `figures/data/fig5.json` to < 1e-12. The headline 2.36 comes from the per-snapshot ℓ_pred and is not affected. |
| 1 | Text | Sect. 7.2 stall sentence: split into two sentences, which name the four check times and say that the observed curve lies at most 0.070 *below* the predicted one, from the energy spans. Sect. 7.1 time-step sentence: "the pooled ℓ at β₀ = 1.5 is 2.2 [1.8, 2.7], and Eq. (ell) with the energy span predicts 2.4", replacing "is 2.2, as Eq. (ell) predicts". Fig. 5 caption: ΔU_cond is the energy span. Sect. 5.3: barrier-set median 6.4 → 7.8 J. Sect. 3.4: the time-step set is drawn from "the 36 snapshots whose saddle height is at least 3 J when all agents are mobile". The 36 is right for the saddle height; 41 qualify by span, and the set was drawn by saddle height. |
| 1 | Strength | **Both statements are weaker.** The stall agreement went from 0.045 to 0.070, and the prediction now visibly overestimates survival at all four times, so the text says "below" rather than "within". The E3 point prediction moved from coinciding with the observation (2.2 vs 2.2) to lying inside its interval (2.4 in [1.8, 2.7]), and the text no longer says "as Eq. predicts". |
| 2 | Sentence on [14] | done. [14]'s abstract and conclusions (`ref/camera_ready_SIMULTECH2026.pdf`) say: "passive noise is indistinguishable from ORCA's linear-program (LP)-based velocity selection as a deadlock-breaking mechanism", and that ORCA's advantage "is attributable to symmetry-breaking rather than distinctive machinery". New text (three sentences, in the required order): the counts reproduce (Sect. 7.2), but all its ORCA results used its own solver, the legacy solver, with the sign defect of Eq. (legnormal); its finding that noise matched to ORCA in completion fraction cannot be told from ORCA by that fraction stands; its inference that ORCA, like the noise, acts by symmetry-breaking is **replaced**: force-coupled ORCA frees the lone trap through a deterministic goal-directed force at rest, the noise frees deadlocks through fluctuations and the ORCA velocity filter frees nothing. The claim is scoped to the lone trap, as in Sects. 7.1 and 7.5. |
| 3 | Abstract | done; 250 words (`tools/count_abstract_words.py`, new: macros expanded, units counted as words, a range counts as one word; P3's abstract counts 244 by this rule). Restored clause: "…frees the lone trap through its goal-directed part: added to the model's goal-directed drive, it gives the same model with relaxation time 0.22–0.27 s and 1.8–2.2 times the drive at rest." Trims in Sect. 3. |
| 4 | Author answers | recorded. 28 pages and P3's cuts are accepted. The constraint part stays Reshape with no subtype (Sect. 7.5 unchanged). weidmann1993 stays @techreport. The limitation sentence (Sect. 9) is unchanged. The Holm `% OPEN` comment is untouched. |
| 5 | Reader pass | done; log in Sect. 4 |
| 6 | Consistency audit | `tools/check_number_consistency.py` (new). Abstract (21 numbers), contributions (28) and conclusions (16) are checked against the body. Each contribution or conclusion sentence that cites a section is also checked against that section's own file. Captions are checked against the body of the section that holds the float. **0 mismatches.** Caption numbers that appear only in their caption are display choices, not results: the colour-scale ends ±150 N and 1000 N (Fig. 1), the 2000-agent scatter subsample and the 5th–95th percentile band (Fig. 3), and "95%" intervals (defined in Sect. 4.4). The script lists them as notes. |

## 2. Printed numbers that changed (old → new)

| Where | Old (macro) | New (macro) |
|---|---|---|
| Sect. 7.2, stall agreement | 0.045 (`PscrStallMaxDiff`, reported barriers) | **0.070** (`PfourStallMaxDiffSpan`, `rev6_P4.json headline.stall_max_abs_diff_span`) |
| Sect. 7.1, E3 prediction at β₀ = 1.5 | not printed ("as Eq. predicts"); `PprotEllBAPred` = 2.2 | **2.4** (`PfourEllBAPredSpan`, 2.357) |
| Sect. 7.1, observed interval of ℓ at β₀ = 1.5 | not printed (`EthreeEllBALo/Hi` 1.80/2.70 exist) | **[1.8, 2.7]** (`PfourEllBALo`, `PfourEllBAHi`; same source, two significant figures) |
| Sect. 5.3, barrier-set median | 6.4 J (`LoneBarMed`, reported) | **7.8 J** (`PfourBarMedSpan`, `rev6_P4.json stall.span.dU_median`) |
| Fig. 5 (plotted) | seed 237 full ratio 1.43 at 10.3 J; full median 1.2 | 0.87 at 16.8 J; full median 1.1 |
| Abstract | — | adds 0.22–0.27 s and 1.8–2.2 (existing `RevAoneTauPrime*`, `RevAoneDriveRatio*`); drops 89 of 100 and 11 of 11 (`EsevenBjamb*`, still in Sect. 5.1) |

No existing macro changed value: `git diff paper/numbers.tex` shows 5 added lines and none removed (registry `paper/registry/p4.yaml`). The superseded macros (`PscrStallMaxDiff`, `LoneBarMed`, `PprotEllBAPred`) remain defined and are no longer printed.

Kept on purpose: the Sect. 5.2 sentence "the full-condition median falls from 1.2 to 1.1 and the pooled slope moves from −0.93 to −0.92". It is the explicit old→new statement of the barrier switch, not a stale value (open item 3).

## 3. Abstract and pages

Trimmed to make room for the identity clause (+22 words; 244 → 250):
- "(open framework deadlock-screen)": the framework name stays in contribution 4 and in Sect. 10.
- The wall-range sentence ("With wall range 0.04 m beside the door, 89 of 100 runs complete and 11 of 11 deadlocks are standoffs.") is folded into the pair-standoff sentence: "The pair standoff, the deadlock at wall range 0.04 m beside the door, needs…". The counts 89/100 and 11/11 are dropped from the abstract; they remain in Sect. 5.1.
- "once the barrier exceeds 1.5 noise temperatures (β ≥ 1.5)": the symbol is dropped, since β is not used again in the abstract.
- "The authors' earlier ORCA solver has a sign defect that makes outcomes replay-sensitive." → "A sign defect makes the authors' earlier ORCA solver replay-sensitive."
- "the members' overhang" → "the agents' overhang", because "members" is undefined in the abstract.

Pages: **28** (unchanged). Page 28 ends at y = 655 pt of 667 pt, about one line free.

Back-matter placeholders: exactly three `\pending` are printed. Zenodo DOI is inside the Data and Code Availability paragraph, about 3.5 lines. Acknowledgments and Disclosure are 4 lines each.

## 4. Reader-pass log

| Location | Problem | Fix |
|---|---|---|
| Sect. 1, par. 1, last sentence | "the lone trap" and "matched noise" used before their definitions in par. 2 | "frees an agent held alone at the door through its goal-directed force at rest, whereas noise that frees the same fraction acts by fluctuations"; serial comma before "and find" removed |
| Sect. 1, par. 2 | "lone keystone" and "second trap" first used in contributions 2–3, defined only in Sect. 3.4 | one clause after the blocker definition: "it is a lone keystone if removing it frees all others and a second trap if another agent is then held" (as in Sect. 3.4) |
| Sect. 1, par. 2 | "constraint part" used in contribution 2 before Sect. 3.2 | "whose goal-directed part is its drive part and remainder its constraint part" |
| Sect. 1, par. 3 | "legacy solver" used without introduction | "used its own solver, the legacy solver," |
| Contribution 5 | "density throttle" undefined in the Introduction | "without the model's density-dependent speed reduction" |
| Fig. 1 caption | "rest-drive push" is defined only in Sect. 6.1 | "with the drive part of the ORCA term at rest" (the same perturbation) |
| Sect. 3.4 | "full-condition barrier" used before Sect. 4.2 defines the conditions; with the span the ≥ 3 J rule picks 41 snapshots, not 36 | "the 36 snapshots whose saddle height is at least 3 J when all agents are mobile" |
| Sect. 7.1, The Legacy Solver | "On the 160 of the deadlock set" (noun missing) | "On the 160 second traps of the deadlock set" |
| Sect. 7.1, time-step sentence | 47 words, five commas | split after the prediction; the second sentence begins "With √Δt-scaled noise the rate is unchanged" |
| Sect. 7.2, stall sentence | 48 words, six commas | two sentences (what is predicted from what; the agreement at the four times) |
| Sect. 1, par. 3, [14] sentence | serial comma | removed |
| Cross-references | all 51 `\ref{sec:…}` checked against the 11-section order; each points to the section that holds the claim | none needed |
| Figures and tables | first citations in order Fig. 1–9, Tables 1–3; every float is cited | none needed |
| Captions | all at most three sentences (Fig. 1 and Fig. 5 have three) | none needed |

Lint (softening adverbs, rhetorical negation, announcements, clefts, bare "This", internal labels, American spellings, long or comma-heavy sentences) was run over every section and the Fig. 1 caption. The new and edited sentences are clean. Two older uses remain on purpose: "changes neither count significantly" (Sect. 7.2), which is statistical, and "lies mostly below" (Sect. 9), which is a factual proportion. The other long-sentence flags are equations or symbol lists, or come from the linter joining a heading to the sentence after it.

## 5. FRAMEWORK NEEDS (deadlock-screen)

1. **Barrier-list argument.** Port `barrier_picture(sigma, nu, barriers=None)`, `reported_barriers()` and `blocker_taus()` from `experiments/E6/analyze.py`, together with the regression test `experiments/revision6/test_barrier_picture.py`.
2. **Span barriers as a first-class output.** The barrier library should carry the energy span next to the saddle height (`rev5_X1.json paths[<snap>|full].dU_span`), and `span_barriers()` (`P4_span.py`) should be the default barrier list for every downstream analysis: stall prediction, E3 and E4 re-analysis, and β statistics.
3. **E3 figure cache.** `E3/analyze.fig5_cache` writes ln(pred) = β_ref − ΔU/k_BT_eff(Δt). This is only right while β_ref = ΔU/k_BT_eff(0.01 s). Compute ΔU·(1/k_BT_eff(0.01) − 1/k_BT_eff(Δt)) directly (as `P4_span.fix_fig5_pred` does), so a barrier substitution cannot de-normalise the curve.
4. **Figure builder.** `figures/fig_escape_dt.py` now reads `data/revision6/P4/E4_analysis_span.json` and `fig5_span.json`. In the framework, build both from the span barriers directly.
5. **Registry.** `paper/registry/p4.yaml` (prefix `Pfour`) has five entries: `PfourStallMaxDiffSpan`, `PfourEllBAPredSpan`, `PfourEllBALo`, `PfourEllBAHi` and `PfourBarMedSpan`. Source `data/derived/rev6_P4.json` (`experiments/revision6/P4_span.py`).
6. **Stall statistic.** `max_abs_diff` is evaluated at four check times only. Expose it as a documented function, and add a supremum over a fine time grid or a one-sample KS-type distance, so the text can quote a full-curve agreement.
7. **Paper gates.** Add `tools/count_abstract_words.py` and `tools/check_number_consistency.py` to the build checks.
8. `data/revision6/P4/e4_escape_span.jsonl` (2 MB, the E4 escape records with the substituted ΔU) is not committed. `P4_span.py` regenerates it in about 10 s.

## 6. OPEN ITEMS

1. **β₀ = 2.5 level of the time-step probe.** Sect. 7.1 sets σ "for β₀ = 1.5 and 2.5" but reports only β₀ = 1.5. At 2.5, ℓ is 3.2 [2.96, 3.52] against 3.70 predicted, and the interval excludes the prediction. The span does not change this. Should the 2.5 result be stated? Default: yes, one clause (`EthreeEllBB*` macros exist), if the page allows; otherwise "for β₀ = 1.5".
2. **Stall statement.** It now reads "at most 0.070 below the predicted one" at the four check times. Is this the wording you want, or should the 0.045 with the reported barriers be shown alongside? Default: span value only, as now.
3. **Sect. 5.2 old→new sentence** (1.2 → 1.1, −0.93 → −0.92). Keep it, now that the figure and every statistic use the span? Default: keep; it is the only place the reader sees that the switch changes nothing material.
4. **Abstract coverage.** I read the rule "the abstract must state every claim the contributions and conclusions state in the same numbers" as consistency: every claim in the abstract that also appears there uses the same numbers. Several contribution claims (w₅₀, the second traps, the constraint part lowering completion) are not in the abstract, and 250 words cannot hold them. Accept this reading? Default: yes.
5. **Wall-range counts** (89 of 100, all 11 deadlocks standoffs) were dropped from the abstract. Restore them at the cost of another clause? Default: no.
6. **Sect. 3.4 last sentence** ("Both pair standoffs of the deadlock set fall among the 98 deadlocks of the default-wall width runs at w = 0.8 m"). I could not parse it on a first reading, and its meaning (are the deadlock-set runs the width runs?) could not be confirmed without the run records, so it was left unchanged. Confirm the intended meaning? Default: reword to "The deadlock set's two pair standoffs are the two standoffs among the 98 deadlocks of the default-wall runs at w = 0.8 m", if that is what it means.
7. **Abstract "matched".** "Matched per-step noise" and "a matched lateral bias" do not say matched to what. Defining it would cost about 4 words. Default: leave as is (the preceding sentence makes force-coupled ORCA the reference).

## HANDOFF

**Current state.** All six tasks are done in `/Users/palaash/Developer/lnns-wt/P4` (branch wt-P4), rebased on origin/main and pushed to main. The paper builds clean at 28 pages: 0 errors, 0 undefined references, 0 BibTeX warnings, 0 overfull boxes. Abstract 250 words; dropped-number check 183/183; consistency audit 0 mismatches. Draft PDF: /Users/palaash/Desktop/LNNS_P4_draft.pdf.

New files:
- `experiments/revision6/P4_span.py` and `test_barrier_picture.py`;
- `data/derived/rev6_P4.json` and `data/revision6/P4/*.json`;
- `paper/registry/p4.yaml`;
- `tools/count_abstract_words.py` and `tools/check_number_consistency.py`;
- this report.

Changed: `experiments/E6/analyze.py`, `figures/fig_escape_dt.py` and `.pdf`, `figures/fig1_caption.tex`, `paper/numbers.tex` (5 added), and sections 00, 01, 03, 05 and 07.

**Decisions made.**
- The stall statistic is quoted with its four check times and its sign ("below").
- E3 prediction printed at two significant figures (2.4).
- Time-step set rule reworded to "saddle height" so the 36 stays true.
- The barrier-set median moves to the span value (7.8 J).
- Abstract trims as listed in Sect. 3.
- `fig5` prediction curves corrected for the β_ref normalisation.

**Open.** Sect. 6, items 1–7. Item 1 (the β₀ = 2.5 miss) comes first.
