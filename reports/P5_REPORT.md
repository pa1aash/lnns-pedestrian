# P5: final text fixes after P4

Base: origin/main `491f8a7` (P4). Build: `make numbers` and `make paper`.

## 1. Status per task

| # | Task | Status |
|---|---|---|
| 1 | Time-step probe, both levels | Done (Sect. 7.1). New text: "With σ set per snapshot for β₀ = 1.5 and 2.5 (time-step set), the escape rate rises as Δt falls, more at β₀ = 2.5, as the per-step temperature of Eq. (10) predicts. The pooled ℓ is 2.2 [1.8, 2.7] at β₀ = 1.5 and 3.2 [3.0, 3.5] at 2.5, against 2.4 and 3.7 from Eq. (11) with the energy span; at β₀ = 2.5 the interval lies below the prediction." Values checked against `E3_analysis.json` (obs 2.164 [1.805, 2.705] and 3.230 [2.962, 3.521]), `rev6_P4.json` (span predictions 2.357 and 3.696) and the C3 and P4 reports. At β₀ = 2.5 the span prediction equals the reported-barrier one (3.696 in both files), as P4 found. I searched the whole source for statements that the rate follows the prediction. One more was found: Sect. 7.5, "an escape rate that falls as Δt grows, as Eq. (11) predicts". It now reads "…in the direction Eq. (11) predicts". The contributions (item 3), the conclusions and Sect. 6 claim only the direction of the Δt response, so they stay as they are. The matched-level result (1.62 [1.00, 2.33] against 2.03) lies below its prediction but inside its interval, and the text gives both numbers. The abstract sentence on replay and the time step is unchanged. |
| 2 | Sect. 5.2, span against saddle height | Done: "The energy span differs from the saddle height for 8 full-condition barriers. With the saddle height in its place, the full-condition median is 1.2 and the pooled slope −0.93, against 1.1 and −0.92; the pinned and alone results are the same for both definitions." "Falls from … to", "moves from" and "its earlier interval" are gone. |
| 3 | Stall prediction | Kept as P4 wrote it (span value 0.070 only). No change. |
| 4 | Sect. 3.4, last sentence | Done: "The default-wall runs at w = 0.8 m (Sect. 5.1) are seeds 42 to 141, the first 100 of the 200 room runs of the deadlock set; its two pair standoffs are among their 98 deadlocks." Checked against the run records. The deadlock set is E1b, seeds 42–241 (200 runs, 196 deadlocks). `experiments/E7/analyze.py` takes its default cell as E1b seeds 42–141: 100 runs, 2 complete and 98 deadlocks (`EsevenDefaultClassified`). The two pair standoffs of the deadlock set are seeds 45 and 101 (`rev_A5.json funnel.group_standoff_seeds`; two members each, C3 report fact 6a), so both fall inside 42–141. |
| 5a | "matched" defined | "Per-step noise matched in freed fraction frees deadlocks by fluctuations; a lateral bias matched in the same way tilts the pair standoff out of its minimum." |
| 5b | Wall-range wording | "The pair standoff, two agents abreast at sharp door edges, is the only deadlock at wall range 0.04 m beside the door, where 89 of 100 runs complete." Checked against Sect. 5.1 and `E7_analysis.json`. With the jamb range at 0.04 m (`Bedge0p04`), 89 of 100 runs complete and all 11 deadlocks are standoffs (`EsevenBjambCollective` = `EsevenBjambClassified` = 11). The "all but 1" of Sect. 5.1 covers the three reduced-range variants together; its one lone keystone is in the all-walls B_w = 0.04 m cell. The sentence does not say the pair standoff occurs only there; Sect. 3.4 and 5.1 report the two at default walls. See open item 1 on "pair" against "group". |
| 5c | Critical width | "…the blocker; half the runs complete at the critical width 0.878 m" (`RevBtwoWfifty`). The interval [0.874, 0.883] did not fit within 250 words; it stays in Sect. 5.1. The overhang range is removed (it stays in contribution 1 and Sect. 5.3). |
| 5d | Undefined terms, same numbers | "Members", "overhang", "segment ends", "defect flag" and "r_c" are gone from the abstract. "Blocker", "pair standoff", "force-coupled ORCA" and "matched" are defined where they first appear. Every abstract number is in the body (consistency check, below), and the three numbers shared with the conclusions and contributions (0.878, 126/186/101 and 0.85–0.93) agree. |
| 6 | Consistency | `tools/check_number_consistency.py` is extended. Each abstract sentence is now checked on its own: all its numbers must appear in one body section file. Six sentences are keyed by a phrase to the section that reports them: critical width → Sect. 5.1, "beside the door" → 5.1, relaxation time → 3.2, whole runs → 7.2, Arrhenius slope → 5.2, human flow → 8. Result: **0 mismatches**. A negative test changed 89 to 77 in the abstract, and the script reported `MISSING abstract (beside the door): 77`. `tools/check_dropped_numbers.py d504d64`: 183/183 found, exit 0. |
| 7 | Reader pass | Log in Sect. 7 below. |

## 2. Printed numbers that changed (old → new)

No existing macro changed: `git diff paper/numbers.tex` shows 4 added lines and none removed. The new registry file is `paper/registry/p5.yaml`.

| Where | Old | New (macro) |
|---|---|---|
| Sect. 7.1, observed ℓ at β₀ = 2.5 | not printed (`EthreeEllBB` 3.23 existed) | **3.2** (`PfiveEllBB`) |
| Sect. 7.1, its interval | not printed (`EthreeEllBBLo/Hi` 2.96/3.52) | **[3.0, 3.5]** (`PfiveEllBBLo`, `PfiveEllBBHi`) |
| Sect. 7.1, prediction at β₀ = 2.5 | not printed (`EthreeEllBBPred` 3.70) | **3.7** (`PfiveEllBBPredSpan`, `rev6_P4.json headline.ell_b2p5_pred_span` = 3.696) |
| Abstract | — | adds 0.878 (`RevBtwoWfifty`), 89 of 100 (`EsevenBjambK`, `EsevenN`); drops 0.26–0.59 mm (`RevBfiveOverhang*`), r_c = 0.1 m and 46 (`RevBfiveN`), all still in the body |
| Sect. 3.4 | — | adds 100 (`EsevenN`), 200 (`RevAfiveRuns`) and the literal seed range 42 to 141 |

## 3. Abstract

**250 words** (`tools/count_abstract_words.py`). The trims below are what made room for 5a–5c and the extra content:

- Removed "(0.26–0.59 mm)", "segment ends sharper than the agents' overhang" and "rounding at r_c = 0.1 m removed all 46". The pair standoff is now "two agents abreast at sharp door edges". The overhang range and the rounding count stay in contribution 1 and Sect. 5.3.
- "with clearing deadlocks at narrow doors" → "with clearing narrow-door deadlocks".
- "In the pair standoff …" restructured into one appositive sentence (see 5b).
- "added to the model's goal-directed drive" → "added to the drive" (the same sentence names the goal-directed part).
- "and a defect flag" removed from the probes sentence ("defect flag" was undefined there). The sign-defect sentence stays.
- "once the barrier exceeds 1.5 noise temperatures" → "at barriers above 1.5 noise temperatures".
- "the authors' earlier ORCA solver" → "our earlier ORCA solver".
- "all tracked participants pass" → "everyone passes".
- "with uncalibrated defaults the model passes" → "the uncalibrated model passes".
- "without its density-dependent speed reduction" → "without density-dependent speed reduction".
- The w₅₀ interval was left out.

## 4. Pages

**28** (cap 28). With every addition in place, the first build ran to 29 pages, so I trimmed Sect. 7.1 only, using lower-value words:
- "Replay separates the two by construction" no longer ends with ", through the noise stream alone".
- "overlap with each other … as much as noise overlaps with" → "overlap … as much as noise and force-coupled ORCA do".
- "with 20 seeds" → "with 20".
- "noise quenches" → "quenches".
- "With different seeds … whereas replays of force-coupled ORCA change none" → "Across seeds …; force-coupled ORCA replays change none".
- "the rate is unchanged" → "the rate is flat".
- "against the prediction 2.03. With √Δt-scaled noise it is −0.08 […], against −0.02" → "against 2.03 predicted, and −0.08 […] against −0.02 with √Δt-scaled noise".
- "frees 121" → "121", and "not matched on the 160 second traps" → "not matched on them".
- "the restricted mean times" → "restricted mean times", and "replays of force-coupled ORCA" → "force-coupled ORCA replays".
- "do not differ detectably" → "do not differ" (the Holm p-values follow).
- "; this loss sets its defect flag" → "and set its defect flag".

Page 28 is full; no line is free.

Build: 0 errors, 0 undefined references, 0 BibTeX warnings, 0 overfull boxes. The only log warning is the template's amsmath `\vec` notice. Exactly three `\pending` placeholders remain: the Zenodo DOI and archive sentence in Data and Code Availability, Acknowledgments, and Disclosure of Interests. The Holm `% OPEN` comment is untouched. Draft PDF: /Users/palaash/Desktop/LNNS_P5_draft.pdf.

Lint ran on the new and edited text (abstract, Sect. 3.4 last paragraph, Sect. 5.2 slope-ratio paragraph, Sect. 7.1 matched-noise, time-step, second-trap and legacy-solver paragraphs, and the Sect. 7.5 sentence). It checks softening adverbs, rhetorical negation, announcements, clefts, bare "This", internal labels, revision narration, American spellings and long sentences. The new text is clean. The remaining flags are two unchanged sentences (the Sect. 3.4 set list and the seed-170 sentence of Sect. 5.2) and en-dash ranges read as dashes.

## 5. FRAMEWORK NEEDS (deadlock-screen)

1. **Registry.** Port `paper/registry/p5.yaml` (prefix `Pfive`): `PfiveEllBB`, `PfiveEllBBLo`, `PfiveEllBBHi` (E3 β₀ = 2.5 observed ℓ and its bootstrap 95% interval at two significant figures) and `PfiveEllBBPredSpan` (span prediction at β₀ = 2.5, `rev6_P4.json headline.ell_b2p5_pred_span`). The framework's E3 analysis should emit the span prediction at both levels next to the observation, so the text reads one source.
2. **Consistency gate.** `tools/check_number_consistency.py` now checks the abstract sentence by sentence (one-section rule plus the `ABSTRACT_SECTION` phrase map). Add it to the build checks with `tools/count_abstract_words.py`, as listed in P4 need 7.
3. **Run provenance.** The paper now states that the default-wall cell at 0.8 m is E1b seeds 42–141. The framework's run index should record cell membership explicitly (a run belongs to the deadlock set and to the width-run default cell), not leave it inferred from `experiments/E7/analyze.py`.
4. **Time-step check.** Add an explicit test that reports, per β₀ level, whether the observed ℓ interval covers the prediction. At β₀ = 2.5 it does not, and the framework should flag this instead of reporting only the direction.

## 6. OPEN ITEMS

1. **Pair or group standoff in the abstract.** At jamb range 0.04 m, 9 of the 11 deadlocks leave two agents and 2 leave three (`n_resid_hist`). The abstract calls the deadlock there "the pair standoff", following your wording. If any of the three-agent cases is a group standoff, "the only deadlock" is exact only under the paper's definition, in which a group standoff is a pair standoff with more members. Recommended default: keep. The alternative, "standoffs are the only deadlocks", costs 2 words.
2. **w₅₀ interval.** It did not fit, so the abstract gives 0.878 m without [0.874, 0.883]. Restoring it costs 2 words, which would have to come from another sentence of the abstract. Recommended default: leave it out; Sect. 5.1 gives it.
3. **"our earlier ORCA solver".** The abstract now uses the first person, as the Introduction does ("We derive"); the Introduction itself keeps "the authors' earlier study". Recommended default: keep "our".
4. **Time-step miss at β₀ = 2.5.** The text reports the miss without explaining it. The cause is untested. Candidates are the last factor of Eq. (10) at Δt = 0.02 s and censoring at the higher barrier. Recommended default: no explanation in the paper. If you want one, give it a one-clause "cause untested", as Sect. 5.2 does for the attempt frequency, at the cost of one line.
5. **Holm 1979.** Still waiting for verified volume, issue and pages; the `% OPEN` pointer is unchanged.

## 7. Reader-pass log (changed passages only)

| Location | Problem on first reading | Fix |
|---|---|---|
| Abstract, pair standoff | "the deadlock at wall range 0.04 m" reads as if it occurred only there | "is the only deadlock at wall range 0.04 m beside the door, where 89 of 100 runs complete" |
| Abstract, escape | "noise frees it … above 1.5 noise temperatures" reads as a noise level | "at barriers above 1.5 noise temperatures" |
| Abstract, blocker | the shortened "holds the blocker" left "blocker" undefined | "holds one agent, the blocker" kept |
| Sect. 3.4, last sentence | P4 open item 6: the relation of the two run sets was unstated | states the seed range and the 100-of-200 relation, then the standoffs |
| Sect. 5.2 | one 46-word sentence with a relative clause | split into the definition difference and the comparison |
| Sect. 7.1, time step | "the pooled ℓ is A and B" left the reader to match values to levels | each value is tied to its β₀ |
| Sect. 7.1, matched level | one 50-word sentence | split after the β ranges |

## HANDOFF

**Current state.** All seven tasks are done in `/Users/palaash/Developer/lnns-wt/P5` (branch wt-P5), rebased on origin/main and pushed to main. The paper builds at 28 pages: 0 errors, 0 undefined references, 0 BibTeX warnings, 0 overfull boxes. The abstract is 250 words. The consistency audit finds 0 mismatches, and the dropped-number check finds 183/183. Three placeholders remain. Draft PDF: /Users/palaash/Desktop/LNNS_P5_draft.pdf.

Files:
- new: `paper/registry/p5.yaml` and this report;
- changed: `paper/numbers.tex` (4 lines added), `paper/sections/00_abstract.tex`, `03_pedestrian_model.tex`, `05_deadlock_physics.tex` and `07_screening.tex`, and `tools/check_number_consistency.py`.

**Decisions made.**
- Both time-step levels are printed at two significant figures. The β₀ = 2.5 miss is stated as "the interval lies below the prediction".
- The Sect. 7.5 claim is weakened to "in the direction Eq. (11) predicts".
- The abstract drops the overhang, the rounding count and the w₅₀ interval; "matched" is defined.
- Sect. 3.4 states the seed relation, verified from the run records.
- Page room came from Sect. 7.1 trims only.

**Open.** Sect. 6, items 1–5.
