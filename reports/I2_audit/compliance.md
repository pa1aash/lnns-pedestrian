# I2 compliance audit: LNCS paper (paper/)

Date: 2026-11-10. Scope: `paper/main.tex`, `paper/sections/*.tex`, `paper/tables/*.tex`, `figures/fig1_caption.tex`, `figures/fig_protocol.tex` (plus `figures/fig1_overlay.tex`, `paper/numbers.tex`, `paper/submission/main.tex` where relevant), `paper/refs.bib`, the built `paper/main.pdf` and `paper/main.log`. No file under audit was edited.

Build currency: `main.pdf` (14:13:38) predates the regenerated `numbers.tex`, `table1_params.tex` and `table3_matched.tex` (14:14). A clean rebuild of the current sources in a scratch copy gives a 24-page PDF whose `pdftotext -layout` output is byte-identical to that of `paper/main.pdf`, so the built PDF matches the sources.

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | LNCS conformance | FAIL (run-in heading capitalisation; one incomplete reference) |
| 2 | Captions at most two sentences | FAIL (Fig. 5, Fig. 9) |
| 3 | Forbidden vocabulary | PASS in rendered text and figure PDFs; FAIL at source level (configuration labels in macro names and generated comments) |
| 4 | gang2026 first citation | PASS |
| 5 | Exactly three `\pending`; `\finaltrue` guard | PASS |
| 6 | Log clean, page count | PASS (24 pages, at the limit) |
| 7 | Bibliography integrity | PASS |

## 1. LNCS conformance

| Item | Result | Evidence |
|------|--------|----------|
| llncs class unmodified | PASS | `paper/llncs/llncs.cls` (v2.24, 2024/01/29) and `paper/llncs/splncs04.bst` have SHA-256 `a3cfe775…0d1a` and `f36c3a17…5174`, identical to the files in the Springer download named in `paper/llncs/SOURCE.txt` (fetched again today). Single commit `ff95784` touches `paper/llncs/`. `main.tex` only adds packages and float parameters (main.tex:1–21); no class internals are redefined. |
| splncs04 style | PASS | main.tex:54 `\bibliographystyle{splncs04}`; `main.blg` reads `splncs04.bst`. |
| runningheads | PASS | main.tex:2 `\documentclass[runningheads,a4paper]{llncs}`; main.tex:27 `\titlerunning` (full title, fits one line in the header), main.tex:32 `\authorrunning{P. Gang and A. Veluri}`. |
| Title, author, institute, email, ORCID | PASS | main.tex:25–36. Both ORCID iDs pass the ISO 7064 MOD 11-2 checksum. Advisory: with a single institute llncs prints the institute unnumbered, so the superscript "1" from `\inst{1}` (main.tex:29–30) points to no number; dropping `\inst{1}` from both authors removes the mismatch. |
| Abstract 150–250 words | PASS | Rendered abstract (sections/00_abstract.tex:3): 219 whitespace-separated tokens (214 containing letters). |
| Five keywords separated by `\and` | PASS | sections/00_abstract.tex:4: Pedestrian dynamics · Social force model · Reciprocal collision avoidance · Activated escape · Mechanism screening (first word capitalised, as in the LNCS sample). |
| Numbered headings (levels 1–2) in title case | PASS | All `\section`/`\subsection` titles are in title case (e.g. "Terms That Vanish at Rest", "ORCA as a Force", "Mechanisms Behind a Matched Rate"). |
| Run-in headings (level 3) capitalisation | **FAIL** | LNCS (samplepaper.tex:64 and Table 1, line 82: "Run-in Heading in Bold.") capitalises third-level run-in headings like the higher levels. Fifteen run-in headings are in sentence case (list below). |
| `credits` block with Disclosure of Interests heading | PASS | sections/10_back_matter.tex:2–9: `\begin{credits}`, `\subsubsection*{\ackname}` (line 5), `\subsubsection*{\discintname}` (line 7), rendered "Acknowledgments." and "Disclosure of Interests." on p. 22. "Data and Code Availability." (line 3) is in title case. Cosmetic note: because each `\pending` starts the paragraph after a run-in heading, the colour switch lands before the heading and both headings print red; this disappears once the `\pending` text is replaced. |
| References formatted by splncs04 | PASS with one **FAIL** in entry content | `main.bbl` is splncs04 output (alphabetical, numbered, DOIs as `https://doi.org/…`). Ref. [17] `helbing2000freezing` is an `@misc` with arXiv fields (refs.bib:1469–1477) and prints without journal, volume or pages: "Freezing by heating in a driven mesoscopic system (2000). https://doi.org/10.1103/PhysRevLett.84.1240". |

Run-in headings to capitalise (proposed text after the arrow):

- sections/02_related_work.tex:2 `Steering models.` → `Steering Models.`
- sections/02_related_work.tex:5 `Clogging at bottlenecks.` → `Clogging at Bottlenecks.`
- sections/02_related_work.tex:8 `Activated escape.` → `Activated Escape.`
- sections/02_related_work.tex:11 `Deadlock in multi-agent systems.` → `Deadlock in Multi-Agent Systems.`
- sections/02_related_work.tex:14 `Testing mechanisms in models.` → `Testing Mechanisms in Models.`
- sections/06_screening.tex:21 `ORCA's parts at the lone keystone.` → `ORCA's Parts at the Lone Keystone.`
- sections/06_screening.tex:24 `Rate-matched noise.` → `Rate-Matched Noise.`
- sections/06_screening.tex:27 `Time-step signature.` → `Time-Step Signature.`
- sections/06_screening.tex:30 `Second trap and the legacy solver.` → `Second Trap and the Legacy Solver.`
- sections/06_screening.tex:50 `ORCA's parts at the pair.` → `ORCA's Parts at the Pair.`
- sections/06_screening.tex:53 `Rate-matched lateral bias.` → `Rate-Matched Lateral Bias.`
- sections/07_experiments.tex:11 `Experiments and model runs.` → `Experiments and Model Runs.`
- sections/07_experiments.tex:16 `Human runs.` → `Human Runs.`
- sections/07_experiments.tex:19 `Model variants.` → `Model Variants.`
- sections/07_experiments.tex:22 `Removing deadlocks.` → `Removing Deadlocks.`

No page-length effect expected.

Fix for ref. [17] (refs.bib:1469): change to `@article` with `journal = {Physical Review Letters}`, `volume = {84}`, `number = {6}`, `pages = {1240--1243}`, keep `year = {2000}` and the DOI, drop the arXiv fields.

Advisory reference content (not failures of the stated checks):

- Ref. [34] `woillez2020` (refs.bib:272): no article number; add `pages = {258001}` (renders "122(25), 258001 (2019)"). The key says 2020, the year field correctly says 2019.
- Ref. [5] `vandenberg2011rvo2` (refs.bib:2299): no year; splncs04 prints no date. Add `year = {2022}` (or the release year of v2.0.2/v2.0.3 as archived on Zenodo).
- Ref. [14] `grover2020symmetry`: the entry typesets with very wide interword spacing (underfull line in the bibliography); harmless, or allow a break in the DOI URL.

## 2. Caption sentence counts

| Rendered | Source | Sentences | Result |
|---|---|---|---|
| Fig. 1 (approved) | figures/fig1_caption.tex:2 | 2 | PASS |
| Fig. 2 (protocol) | sections/04_protocol.tex:21 | 1 | PASS |
| Fig. 3 (lone trap) | sections/05_deadlock_physics.tex:8 | 2 ("Left: …band." / "Right: …(blue).") | PASS |
| Fig. 4 (width, walls) | sections/05_deadlock_physics.tex:25 | 2 | PASS |
| Fig. 5 (escape) | sections/05_deadlock_physics.tex:33 | **3** | **FAIL** |
| Fig. 6 (time step) | sections/06_screening.tex:8 | 2 | PASS |
| Fig. 7 (quench) | sections/06_screening.tex:14 | 2 | PASS |
| Fig. 8 (pair) | sections/06_screening.tex:44 | 2 ("Colours as in Fig. 7." is the second) | PASS |
| Fig. 9 (CroMa) | sections/07_experiments.tex:5 | **3** | **FAIL** |
| Table 1 | tables/table1_params.tex:3 | 1 | PASS |
| Table 2 | tables/table2_signatures.tex:4 | 2 | PASS |
| Table 3 (generated) | tables/table3_matched.tex:3 | 2 ("Rate-matched surrogates … (prediction in parentheses)." / "Noise rows are SFM + noise; … whole-run rows count seeds.") | PASS |

Abbreviations "Eq." and "Fig." inside captions were not counted as sentence ends.

Fixes:

- Fig. 5, sections/05_deadlock_physics.tex:33: join the last two sentences, e.g. "… against $\Delta U_{\rm cond}$, with predicted value 1; full (solid, filled circles), pinned (dashed, open squares) and alone (dotted, filled triangles), all vermilion."
- Fig. 9, sections/07_experiments.tex:5: join the first two sentences, e.g. "Flow through the entrance, longest gap between passages (log scale) and waiting-zone velocity fluctuation for the human runs and the four model variants, with single runs as small points and means and 95\% intervals beside them. Humans grey; …"

## 3. Forbidden vocabulary

Searched (case-insensitive, word-bounded where relevant) in all paper sources listed above, `figures/fig1_overlay.tex`, `paper/numbers.tex`, `paper/submission/main.tex`, the `pdftotext` output of `paper/main.pdf`, and the `pdftotext` output of `figures/fig2_lone_trap.pdf` … `figures/fig8_croma.pdf`.

| Term | Result |
|---|---|
| trial, endpoint, arm, control/controls/matched control/control group, treatment, placebo, efficacy, held out/held-out, pre-registered/preregistered, decision rule, intervention, calibrate-then-falsify | None in rendered text, figure PDFs or prose sources. Only hit: "control barrier functions" (sections/02_related_work.tex:12; PDF line 156), a technical term from robotics, not a comparison condition. PASS. |
| "mode" as published-reproduction / corrected-forward | None. Hits are eigenmodes ("unstable mode" 05_deadlock_physics.tex:41; "opposed lateral mode" :50; "soft mode" :52) and the title of gang2026 in ref. [11] ("failure-mode ablation"), all different senses. PASS. |
| Sentences auditing gang2026 or listing what is new / main differences | None in the paper. The only sentence on the earlier work is sections/01_introduction.tex:9 ("Our earlier work tested such a credit with a surrogate tuned to a mechanism's headline rate [11]; here we test the mechanism."), which positions the paper without auditing the earlier one. PASS (borderline; keep or shorten to the citation if a stricter reading is wanted). The "Main differences from the conference version" text exists only in `paper/SUBMISSION_NOTES.md:3–5`, intended for the submission form, and is not compiled. |
| Mentions of text-generation or authoring software | None in sources, PDF or figure PDFs. PASS. |
| C1/C2/C3/C4 configuration labels | Rendered PDF, figure PDFs and prose: none (configurations are named SFM, SFM+TTC, SFM+ORCA). **FAIL at source level:** (a) `paper/numbers.tex` provenance comments carry `C1`/`C2` at lines 86, 88, 90, 92, 136, 138, 140, 142, 186, 188, 190, 192, 2532 (comments are stripped from `paper/submission/main.tex`, which has no `C1`–`C4` token); (b) macro names encode the labels in words, e.g. `\EsixCThreeMaxT`, `\EtenCOneFlow`, `\FixAsevenCThreeFlowRatio`, `\StuckAloneFracCThree`, `\DriveCOneMedian` in sections/00_abstract.tex:3, 01_introduction.tex:20, 05_deadlock_physics.tex:16, 06_screening.tex:28,31,33,36,38, 07_experiments.tex:20, 09_conclusions.tex:2 and tables/table3_matched.tex:12,16,20; 202 such macro uses appear in `paper/submission/main.tex`, the file sent to the publisher. Macro names containing `Pub` (36 distinct, e.g. `\EtwoReplayCThreePubFlips`, `\PairPubRvoA`) likewise encode the old legacy-solver label. |

Fix for the source-level item: in `tools/make_numbers.py` (and the registry keys it reads) rename the macro families `COne`→`Sfm`, `CTwo`→`Ttc`, `CThree`→`Orca`, `Pub`→`Legacy`, regenerate `numbers.tex`, `table1_params.tex`, `table3_matched.tex`, update the section sources with a scripted rename, and either drop the provenance comments from `numbers.tex` or rewrite their JSON paths without the C-labels. If only the rendered text and the submitted source matter, the rename of macro names alone suffices, since `make submission` already strips comments. Alternatively, the `make overleaf` package described in the updated `paper/SUBMISSION_NOTES.md` replaces every number macro by its value; if that package becomes the source sent to the publisher, the macro names disappear from it (not checked: `~/Desktop/LNNS_overleaf/` did not exist at audit time).

## 4. First citation

PASS. `main.aux` citation order starts `gang2026`, then `liang2024, helbing2012`, …; in the rendered text the first citation after the abstract is "[11]" in sentence 2 of the Introduction (sections/01_introduction.tex:9). Fig. 1 (p. 2) and its caption carry no citation, and the abstract has none. Note: splncs04 sorts alphabetically, so gang2026 is numbered [11], not [1]; it is first in reading order.

## 5. `\pending` items and the final switch

PASS.

- Sources: `\pending` occurs at sections/10_back_matter.tex:4 (Zenodo DOI), :6 (acknowledgements), :8 (disclosure of interests). The only other occurrence, sections/01_introduction.tex:5, is a fallback inside `\IfFileExists` that is inactive because `figures/fig1_caption.tex` exists. `numbers.tex`, tables and figure sources contain none.
- PDF: the only red text in `main.pdf` (span colour scan) is on p. 22: "[Zenodo DOI]", "[acknowledgements, written by the authors]", "[disclosure of interests, written by the authors]" (plus the two red run-in headings noted in item 1). `pdftotext` shows no other bracketed placeholder.
- Final switch: with line 20 of a scratch copy of `main.tex` changed to `\finaltrue`, pdflatex stops with exactly three errors "! Unresolved \pending item in the final build." at back-matter lines 4, 6 and 8, exit status 1. Note: under `-interaction=nonstopmode` pdflatex still writes a PDF after these errors; latexmk reports the run as failed, so build only via latexmk/`make`.
- Housekeeping: `paper/SUBMISSION_NOTES.md` was rewritten (uncommitted, 14:18) while this audit ran; the stale bullet about Sect. 6.4 holding `\pending` results is gone in that version. The new version warns that longer author items may push one reference onto p. 25 (see item 6).

## 6. Log and page count

PASS.

- `main.log`: 0 lines beginning with `!`, 0 "Error", 0 "undefined" (references or citations), 0 "Overfull". One package warning, "Package amsmath Warning: Unable to redefine math accent \vec" (main.log:461), the known benign interaction of llncs with amsmath. 22 Underfull boxes (not in scope; mostly float pages and the bibliography).
- `pdfinfo main.pdf`: 24 pages, the limit, with the reference list ending on p. 24. No slack: any added line can push the paper to 25 pages. The fixes above are length-neutral.

## 7. Bibliography

PASS.

- 37 unique keys cited (`main.aux`), 37 `\bibitem` in `main.bbl`, identical sets: every cited key is printed and nothing uncited is printed (no `\nocite`).
- All 37 cited keys exist in `refs.bib` (203 entries, no duplicate keys); `main.blg` reports no warnings.
- All 37 DOIs match `10.NNNN/suffix` with no spaces, braces or URL prefix; 37 `\doi{}` entries in `main.bbl`. The dataset DOI 10.34735/PED.2021.9 resolves on DataCite with publication year 2026, matching ref. [1]; the gang2026 DOI 10.5220/0015190200004094 resolves (HTTP 200).
- Content issues of refs. [17], [34], [5] are listed under item 1.

## FAIL items and fixes

1. Run-in headings in sentence case (15 headings; list in item 1): capitalise as shown.
2. Ref. [17] `helbing2000freezing` printed as an undated-venue misc item: convert to `@article`, Phys. Rev. Lett. 84(6), 1240–1243.
3. Fig. 5 caption (sections/05_deadlock_physics.tex:33) has 3 sentences: join the last two with a semicolon.
4. Fig. 9 caption (sections/07_experiments.tex:5) has 3 sentences: join the first two.
5. Configuration labels at source level only: C1/C2 in `numbers.tex` provenance comments (13 lines) and `COne`/`CThree`/`Pub` in macro names used in sections, Table 3 and the single-file submission: rename the macro families in `tools/make_numbers.py` and regenerate; strip or rewrite the comments.
