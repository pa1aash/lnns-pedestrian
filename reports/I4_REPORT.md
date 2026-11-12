FINAL (session I4: final paper clean-up and package; no new simulation, no claim changed)

# I4 report
**Length.** 26 pages including references (hard cap 28, target 26). With the three \pending placeholders at four lines each, 3 more body lines fit and a fourth makes p. 27 (body-line probe before the references).
**Build.** `make numbers`, `make paper`, `make submission` green: 0 errors, 0 undefined references, 0 overfull boxes; 46 references, all cited; abstract 246 words (PDF text, ranges one word), every abstract number a registry macro.

**Step 1 (P2's partly resolved items)**
- M11: Sect. 3.4 now says that the default-wall width runs at w = 0.8 m are the deadlock-set runs with seeds 42-141, so both standoffs fall among their 98 deadlocks (2 of 98 and 2 of 196 agree). Checked seed by seed: E7's default cell is E1b seeds 42-141 (22 lone keystones, 74 second traps, 2 standoffs at seeds 45 and 101); seeds 142-241 add 98 deadlocks and no standoff. Both have two residual agents, so Sect. 3.4 calls them pair standoffs (was "group standoffs"; FinCritNegPair = 2).
- G3: two independent examples added, BibTeX from Crossref, claims checked against the abstracts: Xu, Chraibi, Seyfried, TR-C 133 (2021) 103464 ("reduces the occurrence of gridlocks", anticipation in a velocity model, bidirectional flow) and Fu et al., JSTAT (2019) 123402 ("the turning breaks the deadlock", floor-field CA at a bottleneck). The abstract's opening is narrowed to what the sources support: "credited with clearing deadlocks at narrow doors" (was "with how deadlocks ... form and clear").
- Fig. 1/Fig. 3 wording of bc0c3a9 confirmed in the built PDF (blocker, drive part, no bias/biased, saved rest states, Responses, lateral bias). No figure file is older than its script. Fig. 1's "added drive" label is now "with push", matching the caption's "rest-drive push". tools/make_fig1_overlay.py did not carry F3's label edits; it now matches the overlay, and regenerating it reproduces the overlay.
- Old table names updated in experiments/SEEDS.md, A8_horizon.py, notes/A8.md and the registry comments (core.yaml, p_screen.yaml, revision.yaml), plus A6/A9 docstrings, notes/A6.yaml and make_tables45.py. The macro prefix TabThree* and data/derived/table3_pair.json keep their names; this is noted in core.yaml. Historical evidence notes (notes/A6.md, A9.md, A13-A15) are unchanged.

**Step 2 (audit, three parallel checks)**
- Stale wording: 22 flagged, 12 fixed. Declined: "(Glitch)" at the defect-flag definition (R6 names the flag); "the drive part alone" in Sect. 6 (the arm name, defined as SFM plus the drive part); "frozen densities" (physics); the abstract's "wall range of 0.04 m at the jambs" (correct). Zero hits: four classes, class Glitch, Table 3a/3b, held alone, 0.21 m, 5 CroMa runs, Signatures, hard-coded figure numbers.
- Numbers: every macro resolves; no wrong or superseded value. Headlines (0.40-0.60 / 0.48-0.72, 0.85-0.93, 1.8-2.2, tau' 0.22-0.27 s, 0.878 m) are identical in the abstract, Sects. 1, 3, 5, 7 and 10 and in SUBMISSION_NOTES. 1 fix: the Sect. 7 fluctuation range now prints at one rounding (0.092-0.108).
- Compliance: unmodified llncs v2.24; captions within two sentences (Fig. 1 three); six keywords; cite sorts every group; the first body citation is the conference paper (it prints as [14] because splncs04 sorts alphabetically); all references resolve. 1 fix: grover2023 year 2022 -> 2023 (Crossref print year of 42(6)). Breakable DOIs were tried for the stretched reference lines; they saved no line and were reverted.
- Space: the additions first gave 27 pages through a float cascade. Recovered by placing Table 6's input beside Fig. 9, trimming short last lines in Sects. 5.1, 5.4, 6.2, 7, 8, 9 and 10 (no claim or number removed; Sect. 9 (ii) and (iv) lost their cross-reference and gloss) and trimming the placeholders to four lines.

**Step 3 (package).** `~/Desktop/LNNS_overleaf/` and `.zip`: one main.tex with literal numbers, refs.bib (46 cited entries), 8 figures, unmodified llncs.cls and splncs04.bst, README.txt (a stale "README 2.txt" of 11 Nov is no longer in it). Scratch compile from the zip in /tmp: 26 pages, 0 errors, 0 undefined, 0 overfull; with \finaltrue, exactly three "Unresolved \pending" errors. `~/Desktop/LNNS_final.pdf` is overwritten (26 pp.); the previous PDF and package are in `~/Desktop/old_builds/`. SUBMISSION_NOTES and the changelog (C97) are updated.

**Remaining \pending (3):** Zenodo DOI, Acknowledgments, Disclosure of Interests.
## [NEEDS PALAASH]
- Weidmann check: gamma = 1.913 and rho_max = 5.4 (Table 1) against Weidmann 1993 (DOI 10.3929/ethz-b-000242008).
- Acknowledgments, and Disclosure of Interests (to be written by the authors; consistent with the conference paper's AI-use statement), each at most four lines.
- Corresponding-author marking: confirm Palaash Gang and the email address shown.
- Arjun Veluri: read and approve the final PDF.
- Volume editors: confirm 26 pages (the invitation said 23-25).
- Conference paper: is a correction request for its Itaewon reference wanted?
- Zenodo DOI (steps in paper/SUBMISSION_NOTES.md).
