# Submission notes

## Main differences from the conference version (submission form or cover letter)

This article revises the reading of our conference paper (Gang and Veluri, SIMULTECH 2026), which credited the evacuations that configurations with ORCA completed at a 0.8 m exit to ORCA and found velocity noise tuned to the same completion fraction indistinguishable from it. Every ORCA result of the conference paper used a legacy linear-program solver, which we identify here and show to carry a leg-normal sign defect. The model also differs: the conference paper used Voronoi density and calibrated Weidmann coefficients. The article adds the physics of narrow-exit deadlocks in this social force model: a lone trap set by the wall range, with an on-axis equilibrium condition tested in both directions and a critical width of 0.878 m, and a pair standoff that needs sharp door-edge segment ends and a short wall range (0 of 320 runs with rounded edges) and survives a line goal; activated escape of the blocker alone at beta >= 1.5 with an Arrhenius slope 0.85-0.93 of the computed barrier, the finite-barrier value that transition-state theory of the same potential predicts (0.90); no persistent contact arches. It shows that force-coupled ORCA at rest is the social force model with relaxation time tau' = tau tau_orca/(tau + tau_orca) (0.22-0.27 s), a rest drive 1.8-2.2 times larger, and that the ORCA velocity filter frees none of 636 quenches of saved rest states and completes 1 of 100 evacuations against 54 under force coupling; adding TTC, which exerts no force at rest, changes neither completion count significantly. Noise and a lateral bias fraction-matched to force-coupled ORCA free deadlocks by other physics, and named probes tell them apart; the screening protocol, its three mechanism classes and the defect flag are implemented in the open framework deadlock-screen. Against the five CroMa bottleneck runs at 0.8 m, where no participant deadlocks, every model variant with uncalibrated default parameters passes 0.40-0.60 of the human flow, and 0.48-0.72 without the density throttle, so the throttle explains only part of the deficit; final gaps of incomplete runs are treated as right-censored at the 600 s horizon.

## Keywords (six)

Pedestrian dynamics · Social force model · Reciprocal collision avoidance · Activated escape · Bottleneck deadlock · Model validation

## Overleaf workflow

- `make overleaf OVERLEAF_DIR=<dir>` writes the package: one `main.tex` with every `\input` inlined and every number macro replaced by its value, `refs.bib` with the cited entries only, `figures/`, the unmodified `llncs.cls` and `splncs04.bst`, and `README.txt`. The current package is `~/Desktop/LNNS_overleaf/` and `~/Desktop/LNNS_overleaf.zip`.
- Upload the zip to Overleaf (New Project → Upload Project; compiler pdfLaTeX). From then on edit there: the numbers are plain text, so the Overleaf source is the master copy for wording.
- The three author items print as red `[...]` (`\pending`), each holding placeholder text of about four lines that reserves their space. Replace each whole `\pending{...}`, filler included, by the final text. For the final build uncomment `\finaltrue` in the preamble; any `\pending` left then stops the compile (checked: with `\finaltrue` the current package stops with exactly three "Unresolved \pending" errors).
- At the end download the source zip (Menu → Download → Source) and the PDF; the source zip is what the publisher receives.
- If a number changes in the repository after the upload, rebuild with `make overleaf` and carry the changed values over by hand (or diff the two `main.tex`).

## Zenodo (deadlock-screen and the raw trajectories)

1. On Zenodo, create a new upload and click "Reserve DOI" before publishing anything.
2. Sync the deadlock-screen framework with this repository, tag the release (e.g. v1.0), and attach its release zip and the model trajectories of the CroMa comparison (the Part D rerun, `data/revision/D3/` in the main checkout, about 327 MB, not in git), as the Data and Code Availability statement says.
3. Insert the reserved DOI in the paper's Data and Code Availability statement (replace the whole `\pending{Zenodo DOI and archive sentence, ...}` with `10.5281/zenodo.NNNNNNN`), in the framework's README.md and in its CITATION.cff (and .zenodo.json if present).
4. Publish the Zenodo record, then check that the DOI resolves.

## PRIMORIS steps

1. Log in to PRIMORIS with the corresponding author's account and open the submission for this volume.
2. Upload the Overleaf source zip and the final PDF; enter the six keywords and paste the main-differences statement into the form (or the cover letter).
3. Check the author list, ORCIDs and corresponding-author marking against the PDF; sign the Licence to Publish for both authors.
4. Submit, then check that the generated proof shows the page count agreed with the volume editors (the paper has 26 pages; hard cap 28).

## PRIMORIS checklist

- [ ] Source: the Overleaf source zip (one `main.tex`, `refs.bib`, `figures/`, unmodified `llncs.cls` and `splncs04.bst`); it compiles with pdfLaTeX + BibTeX to 26 pages (checked from scratch on 2026-11-13 after the final clean-up: 0 errors, 0 undefined references, 0 overfull boxes; with `\finaltrue`, exactly three "Unresolved \pending" errors).
- [ ] PDF of the final build (with `\finaltrue`, no `\pending` left).
- [ ] Figures: Figs 1, 2 and 4–9 as files in `figures/` (Fig. 1 a 600 dpi PNG, the others vector PDF); the protocol figure (Fig. 3) is TikZ inside the source; alt text in the repository's `figures/ALT_TEXT.md`.
- [ ] Licence to Publish, signed by the corresponding author on behalf of both authors.
- [ ] Corresponding author: Palaash Gang (marked in the author block); ORCIDs for both authors.
- [ ] Main-differences statement (above) in the form or cover letter.
- [ ] Six keywords (above), as in the paper.
- [ ] Author item 1: acknowledgements text.
- [ ] Author item 2: Disclosure of Interests text.
- [ ] Author item 3: Zenodo DOI in the Data and Code Availability statement.
- [ ] Page count after the author items are filled: 26 pages (target at most 26, hard cap 28). The three placeholders hold about four lines each; author texts no longer than the placeholders keep the paper at 26 pages, with 3 body lines to spare (a fourth line makes p. 27).

## [NEEDS PALAASH]

- Weidmann check: compare gamma = 1.913 and rho_max = 5.4 (Table 1) against the original table of Weidmann 1993 (ETH Research Collection, DOI 10.3929/ethz-b-000242008; scripted access returned HTTP 403).
- Write the Acknowledgments and the Disclosure of Interests (each at most about four lines, the placeholder length); the disclosure must be consistent with the AI-use statement of the conference paper.
- Corresponding-author marking: confirm Palaash Gang as corresponding author (marked in the author block) and the email address shown.
- Zenodo DOI: after the deadlock-screen framework sync, tag the release, reserve the DOI and insert it (steps above).
- Confirm the final length with the volume editors: the invitation said 23-25 pages; the paper has 26 pages including references (hard cap 28).
- Erratum for the conference paper (the legacy solver's leg-normal sign defect): decide whether one is planned.
- CroMa licence: CC BY 4.0 is taken from the archive site footer (the DataCite record has no rights entry); confirm with the archive if required.
- CroMa 2.0 m bottleneck: the archive polygons give a straight 0.8 m passage whose 1 m thick walls taper on their outer face in the second metre while the slot faces stay straight; the model uses thin straight walls (stated in Sect. 7 and the Limitations). A rerun of the two 2.0 m runs with the archive wall shape (40 runs, about 2.5 CPU-h) is costed in reports/I3_REPORT.md and was not launched; decide whether it is wanted.
- Arjun Veluri: read and approve the final PDF before submission (co-author approval).
- Conference paper, Itaewon reference: decide whether a correction request to SCITEPRESS is wanted.
- Reference [1] (CroMa dataset) prints 2026, the publication year in its DataCite record (DOI 10.34735/PED.2021.9); confirm or ask the archive.
- Read the final PDF (`~/Desktop/LNNS_final.pdf`), then do the `\finaltrue` build in Overleaf.
