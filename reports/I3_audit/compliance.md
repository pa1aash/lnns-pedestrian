# Compliance check: paper/ at 9152cb1 (branch wt-I3)

Scope: paper/main.tex, paper/sections/*.tex, paper/tables/*.tex, figures/fig1_caption.tex, figures/fig_protocol.tex, figures/fig1_overlay.tex, the seven included figure PDFs, paper/main.pdf, paper/main.log. Nothing was rebuilt.
Build state: main.pdf and main.log are 19:45:19; numbers.tex and tables 1, 3a, 3b were rewritten 3-4 s later by the generators, but the worktree is clean against 9152cb1 and spot values (1.8-2.2, 0.86, 0.40-0.60, 5 CroMa runs) match between numbers.tex and the PDF.

## Summary
| # | Check | Result |
|---|---|---|
| 1 | LNCS layout, abstract, keywords | PASS |
| 2 | Captions, figure/table citation order | PASS |
| 3 | Vocabulary v3, question openers, filler | **FAIL** (5 instances, F2-F3) |
| 4 | First citation is gang2026 | PASS |
| 5 | Pages, errors, undefined refs, overfull boxes | PASS |
| 6 | Figure text >= 7 pt at print size | **FAIL** (1 instance, F1) |
| 7 | Process leakage, AI tools | PASS, with author placeholders open (O1) |

## 1. LNCS layout: PASS
- main.tex:2 `\documentclass[runningheads,a4paper]{llncs}`; latexmkrc puts paper/llncs/ first on TEXINPUTS and main.log:270 loads ./llncs/llncs.cls (v2.24, 2024/01/29). It is unchanged since the setup commit ff95784; md5 is the same as submission/llncs.cls (5fb5a2dc...). main.tex sets only float parameters and adds `\pending`; it redefines nothing in the class.
- `\title`, an identical `\titlerunning`, two `\author`s with `\orcidID`, `\authorrunning{P. Gang and A. Veluri}`, `\institute`, and two `\email`s (main.tex:26-38).
- Abstract: 248 tokens in the rendered page-1 text (pdftotext, "Abstract." to "Keywords" with hyphenation removed). Counting the τ' formula as one word (it renders as 9 tokens) gives **240 words**, inside 150-250.
- Keywords (00_abstract.tex:4): exactly six, separated by `\and`: Pedestrian dynamics, Social force model, Reciprocal collision avoidance, Activated escape, Bottleneck deadlock, Model validation.

## 2. Captions and citation order: PASS
- Tables 1, 2, 3a and 3b have `\caption` before the tabular. All nine figures have `\caption` after the content.
- Sentences per caption: Fig. 1 has 3 (exempt). Fig. 2 has 1, Fig. 3 has 1, Fig. 4 has 2, Fig. 5 has 2, Fig. 6 has 2 ("Activated escape ...(...)." then "(a) ...; (b) ...; (c) ..."), Fig. 7 has 2, Fig. 8 has 1, Fig. 9 has 2.
- First citations in source order: Fig. 1 01:11, Fig. 2 01:16, Fig. 3 04:13, Fig. 4 05:12, Fig. 5 05:20, Fig. 6 05:41, Fig. 7 06:13, Fig. 8 06:42, Fig. 9 07:25. That is numeric order 1-9. Tables: Table 1 01:19, Table 2 04:4, Table 3a 06:13, Table 3b 06:48, also in order. Every float is cited.
- Pages (from main.aux and the PDF), given as first citation then float: Fig. 1 p2/p2, Fig. 2 p2 (again p7)/p7, Fig. 3 p8/p9, Fig. 4 p11/p12, Fig. 5 p12/p13, Fig. 6 p13/p13, Fig. 7 p15/p16, Fig. 8 p17/p18, Fig. 9 p20/p20; Table 1 p3/p5 (cited again near the float at 03:4), Table 2 p8/p8, Table 3a p15/p17, Table 3b p19/p18. Each float is within two pages of a citation.

## 3. Vocabulary v3, question openers, filler: FAIL
- No "SFM+ORCA", "velocity coupling" or class letters. Classes appear only as Prevent / Reshape (axial, lateral) / Heat / Glitch. "lone trap", "pair standoff", "blocker", "member", "snapshot", "quench", "replay", "segment end", "jamb range" and "fraction-matched at T" are used as defined.
- No "?" anywhere in the sections, tables or captions, and no heading or sentence is phrased as a question.
- No announcement or softening filler. A grep for the prose-standard lists (notably, crucially, it is worth, clearly, essentially, roughly, nearly, rather than, "What ..." openers, cleft "It is X that") finds none in the rendered text.

**F2. "attempt rate" for ν (4 instances).** v3 reserves "rate" for an escape rate λ, and 02_related_work.tex:9 already defines ν as the "attempt frequency". The following lines drift:
| File:line | Current | Replacement |
|---|---|---|
| sections/05_deadlock_physics.tex:35 (Fig. 6 caption) | `(a) Escape rate over attempt rate against $\beta$` | `(a) Escape rate over attempt frequency against $\beta$` |
| sections/05_deadlock_physics.tex:43 | `The fitted attempt rates are a median` | `The fitted attempt frequencies are a median` |
| sections/06_screening.tex:31 | `and the attempt rate of Sect.~\ref{sec:escape}` | `and the attempt frequency of Sect.~\ref{sec:escape}` |
| sections/08_discussion.tex:6 | `with fitted attempt rates as in trap models` | `with fitted attempt frequencies as in trap models` |

**F3. Bare "matched" for the surrogate (1 instance).**
| File:line | Current | Replacement |
|---|---|---|
| sections/00_abstract.tex:3 | `and a matched lateral bias tilts the pair standoff` | `and a fraction-matched lateral bias tilts the pair standoff` (the word count is unchanged) |

Advisory (not counted):
- A1. 01_introduction.tex:13: "credited ORCA with the evacuations its configurations completed ... indistinguishable from ORCA's velocity selection" reports the conference paper in its own terms. The configuration meant is force-coupled ORCA (legacy), whose label the same paragraph introduces two sentences later. Optional replacement: `credited ORCA, coupled as a force, with the evacuations ...`.
- A2. The solver is left implicit where only RVO2 ran: 06_screening.tex:31 "Force-coupled ORCA's \EsixCThreeFailRest\ failures" and 07_experiments.tex:25 "(force-coupled ORCA)" (2x) and "SFM and force-coupled ORCA". The context fixes the solver (06:29, 07:14, 07:21). Add "(RVO2)" only if page 25 has room.
- A3. Section openings that summarize the results below them (prose standard, category 3): 05:2, 06:2, 07:9. This is taste; keep them unless space is needed.

## 4. First citation: PASS
The abstract and the Fig. 1 caption contain no `\cite`. The first `\cite` in the body is 01_introduction.tex:9 `\cite{gang2026,xu2021}`, with gang2026 as its first key. It renders as [14, 48]; splncs04 is alphabetical, so [14] cannot become [11] (see P_audit V4).

## 5. Build: PASS
- pdfinfo: **25 pages**, A4 (595.276 x 841.89 pt). This is the limit. Page 25 is the end of the references, and the three `\pending` placeholders reserve about 12 lines (see O1).
- main.log: 0 lines starting with `!`, 0 "undefined", 0 "multiply defined", 0 "Rerun", **0 Overfull**. The three overfull boxes in P_audit V1 are gone.
- Remaining messages: amsmath "Unable to redefine math accent \vec" (main.log:461; this notice is standard with llncs), one underfull \vbox during output (1016), and underfull \hbox lines in main.bbl only (1035-1183, from URLs and DOIs). None of them violates a rule.

## 6. Figure text size: FAIL
\textwidth = 12.2 cm = 345.8 bp. The seven matplotlib PDFs are 345.6 bp wide (main.log: 346.896 pt), so they print at 1.0006x. Span sizes come from PyMuPDF; `pdftohtml -xml -zoom 1` gives the same sizes rounded to whole points.
| Figure (file) | Smallest text, printed | Result |
|---|---|---|
| Fig. 2 fig_geometry.pdf | 6.98 bp = 7.0 pt (CMR7) | PASS |
| Fig. 4 fig2_lone_trap.pdf | 7.0 pt ticks, 8.0 pt labels | PASS |
| Fig. 5 fig3_width_walls.pdf | 7.0 pt | PASS |
| Fig. 6 fig_escape_dt.pdf | 7.0 pt | PASS |
| Fig. 7 fig6_quench.pdf | 7.0 pt | PASS |
| Fig. 8 fig7_pair.pdf | 7.0 pt | PASS |
| Fig. 9 fig8_croma.pdf | 7.0 pt (subscripts kept at 7 pt by `\DeclareMathSizes` in style.mplstyle) | PASS |
| Fig. 1 fig1_hero.png + fig1_overlay.tex | the PNG holds no text; all 45 overlay labels are `\fontsize{7}`, measured 7.0 pt in main.pdf p2 | PASS |
| Fig. 3 fig_protocol.tex (TikZ, `\scriptsize` = 7 pt) | **5.0 pt**: the superscript "−9" of `$10^{-9}$\,m` (main.pdf p9) | **FAIL** |

**F1.** figures/fig_protocol.tex:30. Replace `replay (a copy displaced by $10^{-9}$\,m)` with `replay (a copy displaced by $10^{\textstyle -9}$\,m)`, which sets the exponent at 7 pt. An alternative is `replay (a copy displaced by 1\,nm)`. Check that step 2 still breaks cleanly.
Advisory A4 (tables, outside this check): `\resizebox` puts Table 3a's body at 6.1 pt and Table 3b's at 6.5 pt. Script sub- and superscripts in Tables 1, 2, 3a and 3b are 4.3-5.0 pt (pages 5, 8, 17 and 18). P_audit B6 still stands.

## 7. Process leakage and AI tools: PASS (O1 open, for the authors)
- The rendered text (pdftotext) has no session names, "wave", "referee", "audit", "TODO", internal macro names or run labels (E2, B3, A5x, N1, ...). Macro names such as \RevAfiveX... and \EsixN appear only in the source, and the log shows none undefined. 4D030-4D130 are the published CroMa run names, and sim/steering/orca.py, pedestrian-abs and r2.0-baseline identify the legacy solver; both are kept, as in P_audit B4-B5.
- No mention of any AI tool, vendor or assistant in main.tex, the sections, tables, refs.bib, numbers.tex or the figure .tex files. The only near-match is the bibliography author name "Jean-Claude" in refs.bib:362.
- The source comments in tables/table1_params.tex:1, table3a_noise.tex:1 and table3b_bias.tex:1 hold generator paths (one is data/derived/rev_A15.json). They do not render. Strip them from submission/main.tex if the source is uploaded (P_audit B3).
- **O1 (author action, not an integrator fix).** The PDF prints three red `\pending` placeholders whose visible text reads "placeholder ... replaced when the authors write it. Filler filler ..." (10_back_matter.tex:4, :6, :8; PDF p22). Before submission, replace them with the Zenodo DOI sentence, the Acknowledgments and the Disclosure of Interests. Then uncomment main.tex:21 `\finaltrue`, so that any remaining `\pending` stops the build, and confirm that the page count stays at 25 or fewer.

## Re-check of P_audit violations
V1 (overfull): fixed. V2 (Fig. 1 not cited): fixed at 01:11. V3 (Fig. 8 cited before Fig. 7): fixed; the first citation is now at 06:42. V4 ([14], not [11]): unchanged and not fixable in the source. V5 (bare ORCA in 06 and the tables): fixed; tables and 06 now say "force-coupled ORCA (RVO2)/(legacy)". V6 ("matched" at 01:13 and Table 2): fixed; one new instance in the abstract (F3). V7 ("SFM restart"): fixed ("The SFM quench" at 06:24). B1 (attempt rate): partly fixed at 02:9 and still open elsewhere (F2).
