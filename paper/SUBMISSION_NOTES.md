# Submission notes

## Main differences from the conference version (submission form or cover letter)

This article extends our conference paper (Gang and Veluri, SIMULTECH 2026) with the physics of narrow-exit deadlocks in the social force model: an exact criterion for an agent held alone at the door edges and the critical width it brackets, a pair standoff at the jamb faces under a short-range wall law whose minimum is lost non-smoothly at the end of a jamb segment, activated escape of the lone trap over barriers computed from the model's energy landscape, and the absence of persistent contact arches. It attributes deadlock resolution to mechanism: noise and a lateral bias tuned to ORCA's rate reach that rate through activated escape and a lateral tilt, whereas ORCA acts through its rest drive, and the legacy ORCA solver's sign defect is identified. A velocity coupling of ORCA, which has no rest drive, frees none of 636 frozen-deadlock runs and completes 1 of 100 evacuations against 54 under force coupling, as the screening protocol predicted. The article introduces that protocol, five physically defined mechanism classes and probes on frozen deadlocks, implemented in the open framework deadlock-screen, and compares the model variants with the CroMa bottleneck experiments. These results supersede the conference version's rate-level reading of which steering mechanism resolves deadlocks.

## Keywords (five)

Pedestrian dynamics · Social force model · Reciprocal collision avoidance · Activated escape · Mechanism screening

## Overleaf workflow

- `make overleaf OVERLEAF_DIR=<dir>` writes the package: one `main.tex` with every `\input` inlined and every number macro replaced by its value, `refs.bib` with the cited entries only, `figures/`, the unmodified `llncs.cls` and `splncs04.bst`, and `README.txt`. The current package is `~/Desktop/LNNS_overleaf/` and `~/Desktop/LNNS_overleaf.zip`.
- Upload the zip to Overleaf (New Project → Upload Project; compiler pdfLaTeX). From then on edit there: the numbers are plain text, so the Overleaf source is the master copy for wording.
- The three author items print as red `[...]` (`\pending`). For the final build uncomment `\finaltrue` in the preamble; any `\pending` left then stops the compile.
- At the end download the source zip (Menu → Download → Source) and the PDF; the source zip is what the publisher receives.
- If a number changes in the repository after the upload, rebuild with `make overleaf` and carry the changed values over by hand (or diff the two `main.tex`).

## Zenodo (deadlock-screen and the raw trajectories)

1. On Zenodo, create a new upload and click "Reserve DOI" before publishing anything.
2. Attach the release zip of github.com/pa1aash/deadlock-screen (tag the release first, e.g. v1.0) and the raw-trajectory archive (`data/E10/raw/` and the other raw folders not in git).
3. Insert the reserved DOI in the paper's Data and Code Availability statement (replace `\pending{Zenodo DOI}` with `DOI 10.5281/zenodo.NNNNNNN`), in the framework's README.md and in its CITATION.cff (and .zenodo.json if present).
4. Publish the Zenodo record, then check that the DOI resolves.

## PRIMORIS checklist

- [ ] Source: the Overleaf source zip (one `main.tex`, `refs.bib`, `figures/`, unmodified `llncs.cls` and `splncs04.bst`); it compiles with pdfLaTeX + BibTeX to 24 pages.
- [ ] PDF of the final build (with `\finaltrue`, no `\pending` left).
- [ ] Figures: Figs 1 and 3–9 as files in `figures/` (Fig. 1 a 600 dpi PNG, the others vector PDF); the protocol figure (Fig. 2) is TikZ inside the source; alt text in the repository's `figures/ALT_TEXT.md`.
- [ ] Licence to Publish, signed by the corresponding author on behalf of both authors.
- [ ] Corresponding author: Palaash Gang (marked in the author block); ORCIDs for both authors.
- [ ] Main-differences statement (above) in the form or cover letter.
- [ ] Five keywords (above), as in the paper.
- [ ] Author item 1: acknowledgements text.
- [ ] Author item 2: Disclosure of Interests text.
- [ ] Author item 3: Zenodo DOI in the Data and Code Availability statement.
- [ ] Page count after the author items are filled: at most 24 pages (the references end near the foot of page 24, so longer author items may push one reference onto page 25).

## [NEEDS PALAASH]

- Write the acknowledgements and the Disclosure of Interests (keep each to about one line, or tell me what to cut).
- Reserve the Zenodo DOI and insert it (steps above); tag the deadlock-screen release.
- Confirm with the volume editors that the page limit is 24 pages including references.
- Read the final PDF (`~/Desktop/LNNS_final.pdf`), then do the `\finaltrue` build in Overleaf.
