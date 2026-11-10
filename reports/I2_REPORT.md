# I2 report: paper finished, Overleaf package built (2026-11-10)

Published to main: 69dd207 (velocity coupling, pair label, openings), b86d66d (Overleaf builder), e5b2811 (audit fixes, changelog C86-C91, SUBMISSION_NOTES), then this report.

## What changed
- **Velocity coupling (Sect. 6.4, Table 3):** results from session V, every number a velorca.yaml macro. 0 of 360 lone-trap and 0 of 276 pair runs freed with either solver. Every quench is bit-identical to SFM, and no replay changes an outcome. Whole runs: 1/100 on the first 100 of the 186 Sect. 6.2 seeds, as SFM (on another seed), against 54/100 under force coupling. All 99 failures end at rest. Class P as predicted. Table 3 has a velocity-coupled block (lone, pair, whole; Δ from force coupling). The abstract, contributions, Sects. 8.3, 8.4 and 9 state the confirmed result. Eq. (7) now follows the code: gate w_o, applied after the noise step.
- **Pair library:** relabelled "short-range wall law, B_w = 0.04 m on every wall" in Sect. 5.3, the abstract, the contributions, and Sects. 8.4 and 9. Sect. 5.3 cites the jamb-only runs (11 of 11 deadlocks are pair or group standoffs). The Fig. 1 parenthetical was wrong and is removed: the pair floor uses the snapshot's own law (B_w = 0.04 on all walls), not a default/jamb split.
- **Openings:** every "This section/subsection …" sentence and the introduction's roadmap are replaced by questions, or removed.
- **Fig. 1 spacing:** a stray space before the Fig. 1 caption was removed (its `\input` lines now end in %).

## Pages
24 physical pages; the references end on page 24, about 15 lines short of the foot. 0 errors, 0 undefined references, 0 overfull boxes. `make paper` and `make submission` are green (standalone compile: 24 pages, 3 `\pending`).

## Audits (reports/I2_audit/)
- **Numbers:** 1292 macros, 0 mismatches. 1 WRONG fixed: the velocity whole runs use the first 100 of 186 seeds. 3 IMPRECISE fixed: the SFM completion is on another seed; the Table 3 row label; the replay column counts snapshots.
- **Compliance:** 5 FAIL, 4 fixed: run-in headings in title case, helbing2000freezing printed as a PRL article, Fig. 5 and Fig. 9 captions cut to two sentences. Also fixed: woillez2020 article number, single-institute `\inst` removed. The fifth FAIL is declined: the C1/C3/"Pub" macro names exist only in the repository source; the Overleaf package has none.
- **Prose:** 52 of 99 entries applied. Declined:
  - deleting the gang2026 sentence (decision C85.3 makes it the first citation);
  - "p = 2.2e-16 is a floor": it is the exact McNemar value for 53:0 discordant seeds.
  - The rest are taste items, or would add length.
- **Framework names:** 5 of 7 paper-side items applied: pair/group standoff definition, "proposed by the forces and the noise", replays "displaced", "mechanism under test", the Sect. 8.3 probe requirements. The other two are open (below). Framework-side items are listed in reports/I2_audit/repo_alignment.md.

## Overleaf package
- Locations: `/Users/palaash/Desktop/LNNS_overleaf/` and `/Users/palaash/Desktop/LNNS_overleaf.zip`. Builder: `make overleaf OVERLEAF_DIR=…`.
- Contents: one main.tex (no `\input`, no number macro, no `\newcommand`), refs.bib (37 cited entries, byte-identical), 8 figures, unmodified llncs.cls and splncs04.bst, README.txt.
- Test: unzipped to `/tmp/LNNS_overleaf_test/LNNS_overleaf`, `latexmk -pdf` from scratch. Result: 0 errors, 0 undefined, 0 overfull, 0 BibTeX warnings, 24 pages, identical to the repository PDF page for page (pixel comparison).
- With `\finaltrue`, the compile stops with exactly 3 "Unresolved \pending" errors.
- Final PDF: `/Users/palaash/Desktop/LNNS_final.pdf`.

## Remaining \pending (3)
Zenodo DOI (Data and Code Availability); Acknowledgments; Disclosure of Interests.

## [NEEDS PALAASH]
- Write the acknowledgements and the Disclosure of Interests. Page 24 has about 15 lines left, so keep each short.
- Reserve the Zenodo DOI, tag the deadlock-screen release, and insert the DOI (steps in paper/SUBMISSION_NOTES.md).
- The data statement says the code is "archived with the raw trajectories". The framework's docs/data_layout.md says only the 100 CroMa model trajectories go to Zenodo. Decide what the archive holds and align the two.
- The framework's `screen` computes J on freed sets in a row named `identity`. The framework also calls `push` a surrogate. These and 10 more framework-side items are in reports/I2_audit/repo_alignment.md.
- Confirm the 24-page limit (references included) with the volume editors. Then read LNNS_final.pdf and do the `\finaltrue` build in Overleaf.
