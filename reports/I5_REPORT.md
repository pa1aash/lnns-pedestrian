# I5 report: Zenodo DOI and Overleaf package

Base: origin/main e9c9cbb (P6). Commit 515bf1d holds the paper change; this report is the next commit.

## Replacement

`paper/sections/12_back_matter.tex`, first paragraph. The whole macro with its argument

```
\pending{Zenodo DOI and archive sentence, placeholder of about four lines reserving the space of the final text; it is replaced, not kept, when the authors write it. Filler ... filler.}
```

is replaced by `10.5281/zenodo.24344120`. The sentence now reads "... archived on Zenodo with the CroMa model trajectories (DOI 10.5281/zenodo.24344120)." Nothing else in the file changed (diff: 1 line). The Acknowledgments and Disclosure of Interests placeholders are untouched.

## Checks (before → after the replacement)

| Check | Before (e9c9cbb) | After |
|---|---|---|
| Pages (`paper/main.pdf`) | 28 | 28 |
| Abstract words (`tools/count_abstract_words.py`) | 249 | 249 |
| Overfull boxes in `main.log` | 0 | 0 |
| Undefined references or citations, LaTeX errors | 0 | 0 |
| `tools/check_dropped_numbers.py --paper` | 637 macros checked, pass | identical output |
| `tools/check_number_consistency.py` | 0 numbers not found | identical output |
| `tools/overlap_check.py` | 0 shared runs of >= 8 words | identical output |
| `tools/page_map.py --pinned` | back matter 0.43, total 2.36 | back matter 0.37, total 2.30 |

Removing the placeholder made the back matter about 0.06 pages shorter. The page count is unchanged. `make overleaf` reran `make numbers` and `make tables`, and no tracked file changed apart from the .tex file.

## Overleaf package

- Built with `make overleaf` (tools/make_overleaf.py → `paper/overleaf/`, gitignored): main.tex (569 lines, numbers inlined), refs.bib (49 cited entries), 7 figure files, unmodified llncs.cls and splncs04.bst, README.txt.
- Zipped and compiled from an unzipped copy in a temporary folder (latexmk -pdf, TEXINPUTS/BSTINPUTS unset): 28 pages, 0 errors, 0 undefined references, 0 overfull boxes. The text matches the repository PDF exactly (pdftotext compare).
- `/Users/palaash/Desktop/LNNS_overleaf_package.zip`: 4,876,725 bytes, SHA-256 `c5b2e91fe71b6b90bf16daafa1a7369cf9323e6b516a144df0de7d7476bdc8a4`
- `/Users/palaash/Desktop/LNNS_P7_final_pre_ack.pdf` (repository build): 2,986,812 bytes, SHA-256 `7ac36336140a7296ed456869594bd34a467103f4f569a911e5fc373729e531ac`
- The package main.tex holds two `\pending{` placeholders (Acknowledgments, Disclosure of Interests), plus the mention in the preamble comment.

## Remaining placeholders (`grep -n pending paper/sections/*.tex`)

```
01_introduction.tex:5   \IfFileExists{../figures/fig1_caption.tex}{...}{\newcommand{\FigOneCaption}{\pending{Fig 1 caption}}}
12_back_matter.tex:6    \pending{Acknowledgments, ...}
12_back_matter.tex:8    \pending{Disclosure of Interests, ...}
```

The two printed placeholders are the Acknowledgments and the Disclosure of Interests. The line in `01_introduction.tex` is a fallback that is already in e9c9cbb. It runs only if the tracked `figures/fig1_caption.tex` is missing. It never prints, and `make_overleaf.py` removes it from the package.

## Open items

- The generated package `README.txt` (text hard-coded in `tools/make_overleaf.py`) still says "Three author items", including the Zenodo DOI. Only two are left. This was not changed in I5.
- `paper/SUBMISSION_NOTES.md` still lists the Zenodo DOI as an open author item and gives older page counts (26). This was not changed in I5.
- Before submission, check that the DOI 10.5281/zenodo.24344120 resolves once the Zenodo record is published.
