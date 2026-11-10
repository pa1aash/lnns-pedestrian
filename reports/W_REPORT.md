# W report: final rewrite (2026-11-10)
Published to main: b4087cf (changelog C85), fcf06c4 (rewrite), 21fa60a (audit fixes), then this report with the page pass.
**Pages: 24 physical = 23.75 (page 24 ends at about 75% of the page with the references).** `make paper` and `make submission` are green: 0 overfull boxes, 0 undefined references, and the submission folder compiles on its own at 24 pages. The §6.4 placeholder takes 0.3 page now, and its results can add about 0.1 page without passing 24.

## Removed
- §6.4 Revisiting the Conference Findings and Table 4 (generator, table, registry); open counterflow, crossing and throat-overlap results; Main Differences section.
- Every published-reproduction-mode result and every mention of modes: keystone counts, completion counts, σ50 and the CroMa "C1 published" variant (Fig 9 point removed). Every comparison with conference numbers. The crush term and C4.
- Counts that pooled both libraries were recomputed on the paper's one model (experiments/tables/derive_final.py → data/derived/final_corrected.json, registry final.yaml): 196 deadlocks, of which 194 have positive margin and are all held, and 2 with negative margin are both pair standoffs; second traps 151 of 160.

## Structure
1 Introduction · 2 Related Work · 3 Pedestrian Model (3.1 Forces … 3.5 Statistics) · 4 Mechanism Classes and the Screening Protocol · 5 Deadlock Physics (5.1–5.4) · 6 Screening Results (6.1–6.4) · 7 Comparison with Experiments · 8 Discussion (8.3 Using the Framework, with the checklist) · 9 Conclusions. There are no italic run-in leads, and gang2026 is the first citation in the text.
## Vocabulary
- The protocol is the screening protocol, the mechanism being screened is the resolver, and its tuned perturbations are rate-matched surrogates.
- SFM, SFM+TTC and SFM+ORCA replace C1–C3. ORCA has the legacy linear-program solver and the RVO2 solver, and force coupling and velocity coupling.
- Table 2's last column is now "Corrected implementation". Tables 1 and 3 and Figs 6–8 were re-rendered or regenerated with the v2 labels.
- No banned term remains in the sources, the PDF or the figure PDFs.
## New figure
The screening protocol is a vector TikZ flowchart in §4 (Fig. 2): five boxes in the paper's font and the Okabe–Ito palette, 3.3 cm tall, with a two-sentence caption. The figures that follow it are numbered one higher than their script names, and ALT_TEXT.md has nine entries in paper order.
## Open items from decision 12
- **Rest-drive push:** it frees all 30 lone keystones that ORCA (RVO2) frees, plus 1 more (discordant 1:0), and frees none when reversed.
- **Barriers:** 4 of the 60 snapshots failed the string convergence gate in the full condition, which leaves 56.
- **Identity:** the text now says the data give no evidence that identity separates them at the lone trap.
- **Fig 1:** the PNG records 600 dpi and its pixels are unchanged.
- **ALT_TEXT:** it now matches the captions.

## Audit fixes (reports/W_audit/)
- **Prose:** 68 entries found, 46 applied. The declines are registry precision, taste, and legend-length captions.
- **Numbers:** 429 macros resolve, there are 0 mismatches with the data and 0 WRONG items. Of the 11 IMPRECISE items, 6 are fixed. The other 5 are registry precision formats (e.g. 1.7 vs 2.04 s; b* 4 decimals vs b_f 3), which I left unchanged.
- **Compliance:** 2 FAIL items. One is fixed: an old report held a scratch path naming a tool. The other is declined because decision 3 requires the "supersedes" clause. Of the 5 cosmetic items, 3 are fixed (Fig 4 caption, minus signs, heading case).
- **Page pass:** text was tightened, three §3 headings were merged, and the class list became a paragraph. Dropped as low-weight detail: the quench passage-time exponent (§5.3), the Weibull fits counted from 2 s and 10 s, the ROC rule accuracy (§5.1), the one- versus two-neighbour second-trap counts (§6.1), and the replay separation in metres (§6.1).

## Remaining \pending (5)
The Zenodo DOI; acknowledgements; Disclosure of Interests; the §6.4 velocity-coupling results; and the Table 3 velocity-coupling row (from session V).

## [NEEDS PALAASH]
- Write the acknowledgements and the Disclosure of Interests, and supply the Zenodo DOI for deadlock-screen.
- Five numbers are dropped from the text for length (listed under "Page pass" above); restore any you want, at about 2 lines each.
- Session V's velocity-coupling results must fit in about 0.1 page more than the placeholder takes, or the paper passes 24 pages.
- Release tag and final `\finaltrue` build after the authors' read.
