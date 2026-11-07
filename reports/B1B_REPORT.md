# Batch 1B report

Repository: https://github.com/pa1aash/lnns-pedestrian (public)

## Tree (depth 2)
.github/workflows (paper.yml) | code (.gitkeep) | data/ext | experiments | figures (style.mplstyle, common.py)
paper (main.tex, refs.bib, numbers.tex, latexmkrc, llncs/, tables/) | plan (6 plan docs, CHANGELOG.md, VENUE_REQUIREMENTS.md)
ref (conference PDF, README.md) | reports | Makefile, README.md, .gitignore

## Template
- Source: Springer LaTeX2e Proceedings Templates, https://resource-cms.springernature.com/springer-cms/rest/v1/content/19238648/data/v8 (linked from Springer's conference-proceedings-guidelines page; that page needs a browser, so it was read from an Internet Archive snapshot and the zip fetched directly with curl). Unzipped unmodified into paper/llncs/; SOURCE.txt records URL and date.
- Version: llncs.cls v2.24 (2024/01/29). CTAN has v2.26 but no samplepaper.tex, so the Springer zip was used.
- \textwidth = 12.2 cm (llncs.cls line 55); full width 12.2 cm, half width 5.9 cm in figures/common.py.
- LNNS: no LNNS-specific template or rules found; same llncs. Details in plan/VENUE_REQUIREMENTS.md.
- Font match: body is T1 Computer Modern via cm-super (SFRM/SFBX, CMR7, CMMI). A test figure (usetex, [T1]{fontenc}) placed in a scratch copy of the template showed the same families, all embedded Type 1. Matches.

## Skeleton
- main.tex builds with latexmk, 0 errors, 0 warnings, 2 pages (headings and an empty figure* stub only).
- Corresponding author: the template has no marker, so "(corresponding author)" is written beside Palaash Gang's email in \institute.
- refs.bib = plan root lit/OUT/references.bib (178 entries); the conference paper (key gang2026) is already in it, so no extra fetch. Only gang2026 is \nocite'd.

## CroMa files copied (data/ext/croma/)
4D030_w080_l200_h0.txt 11M; 4D040_w080_l200_h1.txt 8.3M; 4D110_w080_l021_h0.txt 8.2M; 4D120_w080_l021_h1.txt 7.3M; 4D130_w080_l021_h2.txt 6.4M. None over 50 MB, none gzipped. The distributed archive holds only the 24 trajectory files, with no readme, licence or metadata file.

## Actions
See final status line below (filled after the run).

## Environment changes outside the repo
- Installed type1cm.sty (built from the CTAN type1cm .ins with latex) into ~/Library/texmf/tex/latex/type1cm/, because matplotlib's usetex always loads it and the TeX tree lacked it.
- dvipng is not installed, so QA PNGs in save() are rendered from the PDF with pdftoppm.

## Outstanding
- Fetches: none failed. Springer's own pages were unreachable without a browser; replaced by the Archive snapshot plus direct file download.
- Leftover scratch files figures/_t.py and figures/_test.pdf (my delete was blocked by a safety check); excluded via .git/info/exclude, please delete.
- Confirm with volume editors: corresponding-author marking and page limit.
- [NEEDS PALAASH: licence for code, and for text and data]. The plan root's pedestrian-abs/ has no LICENSE file; no LICENSE created.
