# W1 report: first drafting pass (2026-11-08)

**Changelog.** C23 (from B4B) and C26-C33 appended verbatim (a4a8508, pushed).
**Structure.** main.tex now \inputs sections/00_abstract … 10_back_matter; figure and table environments moved unchanged. Fig 1 is included through ../figures/fig1_hero.tex as before, caption from \FigOneCaption (figures/fig1_caption.tex, now present). Fig 5 = Δt, Fig 6 = quench, as planned (their order in the source was swapped to get this). A boxed \pending placeholder holds the Fig 3 slot (E7) so the numbering matches the plan. `\pending{}` prints red brackets; uncommenting `\finaltrue` makes any \pending a compile error (tested).

**Build.** `make paper` green: 19 pages, 0 errors, 0 undefined references. `make submission` green: paper/submission/main.tex (1019 lines, everything inlined, bibliography from main.bbl), 5 figure files under figures/, unmodified llncs.cls and splncs04.bst; a temporary copy compiles alone with 0 errors and 19 pages. The \pending count left is 23.
- latexpand is not in BasicTeX, and tlmgr refuses a user-mode install, so the TeX Live latexpand script (v1.7.2) was placed in ~/Library/texmf/scripts/latexpand; the build script finds it there.
- refs.bib: one existing entry changed in encoding only. In nicolas2018trap, `Ángel` → `{\'A}ngel`, because BibTeX cut the UTF-8 initial into an invalid byte and stopped pdflatex. No other bibliography change. `\usepackage{url}` was added for the URLs in the bibliography.

**Pages against budget** (heading to heading, floats included):
| § | 1 | 2 | 3 | 4 | 5.1 | 5.4 | 6.1 |
|---|---|---|---|---|---|---|---|
| budget | 2.0 | 2.0 | 2.5 | 2.5 | ~1.0 | ~1.0 | ~1.3 |
| used | 1.8 | 1.4 | 3.2 | 3.1 | 1.1 (+Fig 3 slot) | 1.2 | 2.0 |
§3 and §4 are about 0.6 page over (Tables 1 and 2 plus the equations); §6.1 includes Figs 5 and 6 (≈0.9 page). References use 3.2 pages.

**Registry.** 39 entries added (283 macros): E5a σ50 and its CI, completion counts and slopes; g_max at r = 0.20/0.25/0.35 m; C1 drive median and range; ORCA rest drive; C3 stuck-alone fraction; E1b deadlock count; seed170 barrier, events, restarts and residual agents; the 3 non-covering Arrhenius ratios; the skipped seed60 barrier; restarts per level; attempt rates; T3 ratios (mean, median, cells); E3 censoring; E4 n; lone-keystone drive-only discordants against RVO2 and against the published solver. Sums such as 2 of 10 are computed in LaTeX (`\numexpr`) from the macros.
- New source data/derived/E5a_analysis.json, from experiments/E5/analyze_e5a.py (new; reuses analyze.py's fit). data/E5/e5a.jsonl is committed: queue 1 finished it at 18:16 and queue 2 does not write it.
- **E5a result:** σ50 = 0.045 [0.042, 0.047] m/s in the published mode, against 0.044 [0.041, 0.047] in the corrected mode. The conference value 0.049 is outside both intervals. This contradicts B4A's proposal that the corrected mode "needs about 10% less noise": the two modes need the same noise.

**Missing citations.** None; every citation key is in refs.bib.
**Overlap** (tools/overlap_check.py, `make overlap`): 0 shared runs of ≥ 8 words, so nothing needed rewriting; the longest shared run is 4 words ("to the preferred velocity"). The tool catches a planted conference sentence (checked). One 6-word run ("steering paradigms are routinely credited with") was rewritten anyway.

**\pending, grouped by the data it awaits**
- E7b (pair class): §1 contribution bullets (pair Hessian and fold; pair verdicts); §5.2; §6.1 forward pointer to §6.2; §6.2; Table 3 \input.
- E6/E6p (matched whole-run completion): §1 attribution bullet; §6.3.
- E7 (wall cells): Fig 3 placeholder and caption; §5.1 critical width and jamb locality; §6.3.
- E10 (CroMa): §1 validity bullet; §3 CroMa results; §7.
- E8/E9, E11: §3 open geometries (Table 4); §6.3.
- Contact statistic (E1/E7): §5.3.
- Written last: abstract, keywords, §8, §9, main differences, data and code availability, acknowledgements.

**Not done.** No CI result yet at the time of writing; see the commit message thread. The 2026-11-09 changelog dates were kept as given.

**[NEEDS PALAASH]**
1. Page plan: the draft runs to 19 pages with §§5.2, 5.3, 6.2, 6.3 and 7 still empty, and these hold about 8.5 pages of budget, so the full paper projects to ≈ 27 pages against 23-25. §3/§4 (≈ 0.6 page over each) and the 3.2-page reference list are the obvious places to cut. Which do you prefer?
2. Fig 1: the macro path `\heroimage` in 01_introduction.tex still points to the mock PNG. Switch it when HV2's final render lands (main.tex is mine; the figure files are HV2's).
3. §5.1 states v_eff = v0 at the terminal rest state qualitatively ("indistinguishable from one"). C16's "≥ 0.99" has no derived-JSON source, so it is not quoted.
4. T4's conservative-field residual (C30: ~5e-8 N) is not in any data/derived JSON, so §4 gives no number for it. Add it to E4_analysis.json if you want it quoted.
5. Fisher p prints as "2.3e-04" (registry fmt); a LaTeX-style ×10⁻⁴ needs a format change in make_numbers.py (not my file).
6. refs.bib: the nicolas2018trap brace-escape above. Confirm that this is acceptable under the "never write a bibliography entry" rule.
