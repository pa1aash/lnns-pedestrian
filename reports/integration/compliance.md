# Venue compliance: Springer LNNS (llncs), integration pass (worktree I)

Audited object: `paper/submission/` as built by `make submission` (main.tex mtime 03:18), compiled alone in `/private/tmp/lnns_compliance` with `latexmk -pdf` and `TEXINPUTS`/`BSTINPUTS`/`BIBINPUTS` unset. The bibliography is inlined, so no BibTeX pass runs.

**The submission folder is stale.** Between 03:33 and 03:36 another process edited `paper/sections/*.tex`, `paper/tables/*.tex`, `make_table3.py`, `make_table4.py`, `paper/numbers.tex` and the registry (uncommitted; see `git status`). A temporary build of the current sources (`/private/tmp/lnns_cur`) has **25 pages** (the submission build has 24). In that build the Sect. 5.2 overfull box is gone and two glossary defects are already fixed (marked "fixed in sources" below). Run `make submission` again once those edits are finished, then repeat items 2–6.

Every fix below is anchored to the current source files and was checked at 03:37 to occur there exactly once. All fixes together were applied to a temporary copy of the current sources. That build has 0 overfull boxes, 0 errors and 0 undefined references, and still has 25 pages.

## Pass/fail summary

| # | Item | Result |
|---|---|---|
| 1.1 | llncs v2.24, `runningheads` | PASS (`\ProvidesClass{llncs}[2024/01/29 v2.24`; `\documentclass[runningheads,a4paper]{llncs}`) |
| 1.2 | One corresponding author, marked, with email | PASS. The marker is a label in the institute block, which is still an open point for the editors. |
| 1.3 | ORCID and all emails in the header | PASS (both authors) |
| 1.4 | Alt text | OPEN, not a build defect. `figures/ALT_TEXT.md` covers Figs 1–8 but is not shipped in `paper/submission/`. See D9. |
| 1.5 | Acknowledgements and disclosure in `credits` | PASS structurally; the text of both is still `\pending` |
| 1.6 | Numbered square-bracket citations, splncs04 | PASS |
| 1.7 | Authorship frozen after delivery | n/a (process) |
| 1.8 | Extension statement; no footnotes in the abstract; third-party figures | PASS. "Main Differences from the Conference Version" is present, the abstract has no footnotes, and the paper has no third-party figures (CroMa enters as data and is cited). |
| 1.9 | AI-use disclosure | OPEN: the authors decide; no statement is present |
| 1.10 | Page budget | 24 pages (submission build) or 25 (current sources). Inside the 23–25 page invitation target, at its upper end for the current sources. Above the 12–15 pages typical for a full paper, so confirm with the editors. |
| 2 | `\pending`: exactly three; nothing else in red or marked as draft | PASS |
| 3 | Standalone compile | PASS: 0 errors, 0 undefined references or citations, 24 pages. **FAIL: 4 overfull hboxes above 1 pt (D1–D4).** The `\overlayfile` warning is harmless. |
| 4 | Fonts embedded, no Type 3 | PASS |
| 5 | Fig. 1 at ≥ 600 dpi as placed | PASS, at exactly 600.0 ppi with no margin (advisory A1) |
| 6 | Captions: at most two sentences; figure captions below, table captions above | PASS (G6 length advisory A2) |
| 7 | Glossary | **FAIL (minor): D5–D8** |
| 8 | British spelling | PASS |
| 9 | LNCS conventions | PASS (minor advisory A3 on the case of run-in headings; A4 on the number of keywords) |

## Item details

### 2. `\pending`
`paper/submission/main.tex` has three occurrences besides the definition on line 14:
- l.1904 `\pending{Zenodo DOI, added at submission}`
- l.1906 `\pending{acknowledgements, written by the authors}`
- l.1908 `\pending{disclosure of interests, written by the authors}`

Red colour operators (`1 0 0 rg`) appear only on page 22, six of them, which are these three items. There is no `\todo`, TODO, FIXME, `\hl` or leftover planning comment such as "Budget" or "do not edit". `\finaltrue` is still commented out, as intended until the last build.

### 3. Compile log (submission build)
- Errors: 0. Undefined references or citations: 0. No "??" in the PDF text. 24 pages, A4.
- Overfull hboxes above 1 pt:
  - **42.09 pt**: Table 3 (main.tex 1787–1810, p. 16); the table visibly runs into the right margin. See D1.
  - **5.46 pt**: Sect. 8, "Calibration and test." (main.tex 1885, p. 20). See D2.
  - **4.30 pt**: Sect. 5.2, "For whole runs, half complete at noise amplitude σ50 = …" (main.tex 1756, p. 12). This one is **already gone in the current sources** ("noise level"). No fix needed after the rebuild.
  - **1.26 pt**: Main Differences, "SIMULTECH 2026 paper [11], keeping its minimum-intervention…" (main.tex 1901, p. 22). See D3.
- Underfull hboxes (badness):
  - Table 1 rows, main.tex 1591, 1593 and 1594 (badness 10000, p. 4–5): the justified first column `p{1.2cm}` ("Agents, room", "SFM, walls", "Other forces"). Optional fix D4.
  - Bibliography entries with long DOIs or URLs, main.tex 1928 (badness 2452), 1956 (10000 ×2), 1989 (10000 ×2), 2001 (3179, 10000), 2029 (3623, 3386), 2040 (10000 ×2), 2050 (2469), 2055 (4291, 3291, 10000), 2061 (1102, 2608), 2071 (3386) and 2081 (1043). These are the E 2007, Grover 2020 symmetry, Hänggi, Karamouzas, Köster, Liang, Liu, McNemar, Parisi, Weidmann and Arrhenius entries. They are cosmetic, typical of splncs04 DOIs, and need no action.
- Underfull vbox on page 5 (the page with Table 1): there is extra white space above "Desired force and density". Cosmetic.
- Other warnings: only `amsmath: Unable to redefine math accent \vec` (harmless with llncs).
- **"Could not find file [\overlayfile]".** This is printed by `latexpand` (step 2 of `tools/make_submission.sh`), not by LaTeX. `figures/fig1_hero.tex` calls `\input{\overlayfile}`, a path given by a macro, which latexpand cannot resolve, so it leaves the `\input` in place. The script's Python step then expands the `\figdir`/`\overlayfile` path macros and inlines `figures/fig1_overlay.tex`. In the result, `paper/submission/main.tex` contains no `\input` (count 0), it contains all 39 `\draw` lines of the overlay, and the overlay renders on page 2 (arrows, scale bars, labels, inset all checked visually). **The warning does not affect the submission.** Optional: filter it in `make_submission.sh`, or add a comment there saying it is expected.

### 4. Fonts
`pdffonts` on the compiled PDF lists Type 1 fonts only, all `emb yes`, all subset, with no Type 3. Figure PDFs `fig2`–`fig8` contain only Type 1 fonts (CM and SFRM), all `emb yes` (not subset, which is acceptable) and no Type 3. `fig1_hero.png` is a raster; its labels are TikZ text in the main PDF.

### 5. Raster resolution
| Figure | Raster | Pixels | Placed size | ppi as placed |
|---|---|---|---|---|
| Fig. 1 | fig1_hero.png | 2882 × 1523 | `\textwidth` = 122 mm = 4.803 in × 2.538 in | **600.0** (`pdfimages`: 600/600) |
| Fig. 2 | colour map in fig2_lone_trap.pdf (with smask) | 1168 × 897 | 1.947 × 1.495 in at the figure's scale of 1.0007 | 600 (599.6 exactly) |
| Figs 3–8 | none (vector only) | — | — | — |

### 6. Captions (submission build; word counts from the PDF text, math tokens counted as words)
| Caption | Sentences | Words | Position |
|---|---|---|---|
| Fig. 1 | 2 | ~89–94 (approved) | below |
| Fig. 2 | 2 | 78 | below |
| Fig. 3 | 2 | 44 (55 after D6) | below |
| Fig. 4 | 2 | 46 (51 in current sources) | below |
| Fig. 5 | 1 | 38 | below |
| Fig. 6 | 2 | 52 | below |
| Fig. 7 | 2 | 34 | below |
| Fig. 8 | 2 | 57 | below |
| Table 1 | 1 | 17 | above |
| Table 2 | 2 | 26 | above |
| Table 3 | 2 | 63 (≈79 in current sources) | above |
| Table 4 | 2 | 24 | above |

Every caption has at most two sentences. In the sources, figure captions follow `\includegraphics` and table captions precede the tabular, which is the LNCS placement.

### 7. Glossary scan (sources, compiled text, and the `pdftotext` output of every figure PDF, including tick labels and the TikZ text of the Fig. 1 overlay)
- "arm", "held out/held-out", "pre-registered", "endpoint", "trial", "equivalence margin": none in the paper text, captions, tables or ticks. "arm" and "equivalence-margin" appear only in the docstring and identifiers of `experiments/tables/make_table3.py`, which are code and not printed.
- No clinical vocabulary: "control", "intervention", "protocol" and "baseline model" are the glossary's own terms or neutral. There is no placebo, cohort, efficacy, dose or similar.
- "frozen": every use is "frozen deadlock(s)", "densities frozen" or "frozen densities", except "at a frozen state" (02_background.tex:4; see D7). The barrier condition is "pinned" everywhere, including the Fig. 4 caption. `\EfourEventsFrozen` and similar are macro names only.
- "collective": none in the printed text; `\KeystoneBCollective` and similar are macro names only.
- "two types": used in Sect. 1, Sect. 9 and Sect. 5.3 ("the second type"). "Symmetric" appears only for robot configurations and scenes (02_background.tex:13), never for the standoff.
- "fold": "1.5-fold" (04_signatures.tex:35), D5.
- B_{w,edge}: the Fig. 3 caption and tick label, D6. In the submission build, 05_deadlock_physics.tex:46 printed "$0.04$\,m below" for the jamb-only variant. **This is fixed in the current sources** ("for $B_{w,\rm edge}$ below").
- "completion rate" for the matched quantity: in the submission build, Sect. 9 read "a matched completion rate". **This is fixed in the current sources.**
- "published mode" (Fig. 8 caption), D8.

### 8. Spelling
The prose, captions, table text, tick labels and Fig. 1 overlay labels are all British: realised, realisations, discretised, characterised, analysed, modelling, modellers, colour(s), coloured, labelled, favoured, behaviour, centre, metres, grey, neighbour(s), towards, acknowledgements, artefacts. No American spelling was found. "linear program" is the technical term. "Modeling" occurs only in reference titles (proper names). "Acknowledgments." is printed by the unmodified `llncs.cls` (`\ackname`) and should not be changed.

### 9. LNCS conventions
- Cross-references: "Fig.~", "Sect.~"/"Sects.~", "Table~", "Eq.~"/"Eqs.~" and "Proposition~" are used throughout. There is no "Figure", "Section", "Sec." or "Equation" in running text. Table 4 has a "Sect." column of `\ref`s.
- Headings: all `\section` and `\subsection` headings are consistently in title case. Run-in `\paragraph` headings are in sentence case (A3).
- Abstract: 182 words, inside 150–250. No footnotes or citations.
- Keywords: `\keywords{… \and …}`, six keywords, each starting with a capital, rendered with "·" separators (A4).
- References: `\bibliographystyle{splncs04}`; the bbl is inlined; references are numbered, alphabetical, with DOIs.
- Figure files: every `\includegraphics` target exists in `paper/submission/figures/`: fig1_hero.png (via `\heroimage`) and fig2_lone_trap, fig3_width_walls, fig4_escape, fig5_dt, fig6_quench, fig7_pair and fig8_croma (.pdf). There are no extra or missing files.

## Defects and exact fixes

**D1. Table 3 is 42 pt wider than the text** (fail, item 3). Make the fix in the generator, run `make tables` (or `make_table3.py`), then rebuild. Labels are shortened (the caption keeps "C1 + noise"), the unit moves to the caption, and the remaining ≈16 pt is absorbed by `\resizebox`, which scales the table by about 0.96 (scriptsize 7 pt to about 6.7 pt). Tested: 0 overfull, page count unchanged. File `experiments/tables/make_table3.py`:
- l.116: `(r"C1 + noise $\sigma=0.07$\,m/s",` → `(r"noise $\sigma=0.07$\,m/s",`
- l.129: `(r"C1 + noise, $\beta_{\rm ref}=1.5$", NA` → `(r"noise, $\beta_{\rm ref}=1.5$", NA`
- l.135: `(r"C1 + noise $\sigma^\ast$",` → `(r"noise $\sigma^\ast$",`
- l.168: `Kaplan--Meier median $t_{1/2}$, first exits ` → `Kaplan--Meier median $t_{1/2}$ (s), first exits `
- l.170: `(prediction in parentheses). Lone-trap noise rows` → `(prediction in parentheses). Noise rows are C1 + noise; lone-trap noise rows`
- l.181: `r"\begin{tabular}{@{}lccccccc@{}}",` → `r"\resizebox{\textwidth}{!}{\begin{tabular}{@{}lccccccc@{}}",`
- l.183: `& $t_{1/2}$ (s) & Lower` → `& $t_{1/2}$ & Lower`
- l.191: `lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]` → `lines += [r"\bottomrule", r"\end{tabular}}", r"\end{table}"]`

(`\resizebox` on its own, without the label changes, also removes the overflow, but it scales the table to 0.89, about 6.2 pt.)

**D2. Overfull 5.46 pt, Sect. 8** (fail, item 3). `paper/sections/08_discussion.tex:4`:
`In all three settings a matched control reaches the paradigm's rate:` → `In each setting a matched control reaches the paradigm's rate:`
(Tested: the box is removed and the page count does not change. "the rate of the paradigm" also removes it but adds a page.)

**D3. Overfull 1.26 pt, Main Differences** (fail, item 3). `paper/sections/10_back_matter.tex:3`:
`This paper extends our SIMULTECH 2026 paper~\cite{gang2026}, keeping` → `This paper extends our SIMULTECH 2026 conference paper~\cite{gang2026}, keeping`
(Tested: the box is removed and the page count does not change.)

**D4 (optional, cosmetic). Underfull Table 1 first column.** `experiments/tables/make_table1.py:91`:
`"\\begin{tabular}{@{}p{1.2cm}>{` → `"\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{1.2cm}>{`
(Tested: the three badness-10000 warnings go away and the page count does not change.)

**D5. "fold" for a multiplier** (item 7). `paper/sections/04_signatures.tex:35`:
`$T_{\rm eff}$ varies up to 1.5-fold between agents` → `$T_{\rm eff}$ varies by up to a factor of 1.5 between agents`

**D6. Jamb-only variant labelled as $B_w$** (item 7). In Fig. 3 (right) the tick label is "jambs 0.04", and the caption says the labels are "$B_w$ in metres", so the jamb-only variant reads as $B_w=0.04$.
- Caption, `paper/sections/05_deadlock_physics.tex:25`: `per wall-law variant, labelled by $B_w$ in metres (right).` → `per wall-law variant, labelled by the wall range in metres ($B_w$ on all walls, $B_{w,\rm edge}$ on the jambs only; right).` (Two sentences, 55 words. Tested: no page change.)
- Optional, for the tick itself, `figures/fig3_width_walls.py:32`: `"Bedge0.04": "jambs 0.04"` → `"Bedge0.04": r"jambs $B_{w,\mathrm{edge}}$ 0.04"`, then regenerate the figure. This matches the Fig. 8 tick "C1 jamb $B_{w,\mathrm{edge}}$".

**D7. "frozen state"** (item 7; minor, since the sense is the snapshot and not the barrier condition, but it is outside the allowed forms). `paper/sections/02_background.tex:4`:
`so that each can be switched off at a frozen state.` → `so that each can be switched off at a frozen deadlock.`

**D8. Mode name in the Fig. 8 caption** (item 7, G3 "published-reproduction mode"). `paper/sections/07_validity.tex:6`:
`C1 black (published mode open circle,` → `C1 black (published-reproduction mode open circle,`
(Tested: no page change. The tick label "C1 published" in `figures/fig8_croma.py:17` is a short form explained by the caption and can stay.)

**D9 (process). Alt text is not in the submission folder** (rule 4). Ship `figures/ALT_TEXT.md` with the submission, or paste it into the submission form. Before it goes out, reconcile two places where it and the captions disagree:
- The Fig. 3 alt text says "lone trap (dark grey)", while the caption says "stack of stuck-alone agents (dark grey)".
- The Fig. 6 alt text mentions "C3 in the published-reproduction mode dash-dotted", which the caption does not.

## Advisories (no change required for compliance)
- **A1.** Fig. 1 meets 600 ppi with no margin (600.02). Any enlargement by the typesetter drops it below. The PNG's pHYs metadata says 72 dpi, so standalone tools would report about 40 in × 21 in. Optional: write 600 dpi metadata when the render is saved (e.g. Pillow `dpi=(600,600)`).
- **A2.** G6 asks for captions of "about 60 words". Over that are Fig. 2 (78), Table 3 (≈79 in the current sources) and Fig. 1, which is approved at 89.
- **A3.** The LNCS sample paper sets fourth-level run-in headings in title case ("Sample Heading (Fourth Level)"). The paper's 26 `\paragraph` headings are in sentence case, while the back-matter `\subsubsection*` headings are in title case. If the editors want them uniform, change for example `\paragraph{Steering paradigms.}` → `\paragraph{Steering Paradigms.}`, and likewise in 02_background.tex:3,6,9,12,15, 03_model.tex:11,19,30,37,44, 04_signatures.tex:7, 06_attribution.tex:18,21,24,27,41,44, 07_validity.tex:12,15,18 and 08_discussion.tex:3,6,9,12. Single-word headings need no change. Springer's typesetters usually normalise this themselves.
- **A4.** There are six keywords. VENUE_REQUIREMENTS states no limit. Some Springer volumes ask for 3–5, so confirm with the editors. The glossary (D3c) rules out adding new keywords.
- **A5.** The page count rises from 24 to 25 with the current sources. Any later wording change that adds a line near the end of the bibliography (p. 24/25) may add a page.
