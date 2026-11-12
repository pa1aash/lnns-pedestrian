FINAL (session P2, revision 3: text, tables and package after the second referee report)

# P2 report
**Length.** 26 pages including references (hard cap 28, target 26). With the three \pending placeholders at four
lines each, 3 more body lines fit and a fourth makes p. 27 (text-line probe after the last integration).
**Build.** `make numbers`, `make paper`, `make submission` green: 0 errors, 0 undefined references, 0 overfull boxes.
No `%C2:` marker is left; every number is a registry macro.

**Referee resolution** (reports/P2_RESOLUTION.md, 72 items): resolved 67, partly 5, not resolved 0, disagreed 0.
- M11: why 2 of 98 (Sect. 5.1) and 2 of 196 (Sect. 3.4) agree (seeds 42-141 are a subset of 42-241) is not said.
- M12, B1, B3 (figures, owned by F3): Fig. 1 caption "blue, force-coupled ORCA's rest drive, its drive part"
  against the rest-drive definition of Sect. 3.2, and the graphic's bare "ORCA" and "held alone" labels; Fig. 3
  boxes "frozen deadlocks", "Signatures", "lateral tilt" against the snapshot/probe/bias vocabulary.
- G3: the premise has one independent example ([38]); the opening claim is not softened.
- Disputes kept: abstract cites the finite-barrier TST value, not the Langer prefactor (0.69, unexplained by damping, A2);
  scope stays one parametrisation.
**Claims that changed meaning**
- HEADLINE CHANGE (A3): Arrhenius slope 0.85-0.93 of the computed barrier (was 0.86-0.93, unexplained); transition-state theory of the same
  potential predicts 0.90 with no free parameter (abstract, Sects. 1, 5.2, 9).
- HEADLINE CHANGE (B1c/d): CroMa flow ratio 0.40-0.60 belongs to the throttled model; without the density throttle
  every variant passes more, 0.48-0.72 (Table 6 new column; abstract, Sects. 1, 7, 9; submission statement).
- R6: three classes plus the defect flag; the legacy solver's flag now rests on the pair standoff (21 freed fall to
  7), its lone-trap replay flips are replay sensitivity (Table 3, Sect. 6.1).
- A10: noise replay sensitivity is the noise-seed change (0 of 170 flip with the stream fixed), by construction.
- R11: below beta 1.5 (Delta t = 0.005 s probe, matched noise) noise acts by fluctuations, not activated escape.
- Unchanged after checks: w50 without the throttle (0.878 m), 0.8 m completions without it (1 and 53 of 100),
  w50 at Delta t = 0.005 s (shift -0.003 m), radius scope (A1), conference completions incl. SFM+TTC 5/100 and
  force-coupled ORCA with TTC 56/100 (A11).

**Audits** (reports/P2_audit/): compliance 16 fixes; numbers 22 flagged (4 wrong, 7 superseded, 5 unsourced,
6 imprecise), all corrected; prose 180 findings, applied except those declined with reasons in fixlog.md; referee
recheck in P2_RESOLUTION.md. All applied fixes are published.

**Package.** `~/Desktop/LNNS_overleaf/` and `~/Desktop/LNNS_overleaf.zip`: one main.tex with literal numbers,
refs.bib (44 cited entries), 8 figure files, unmodified llncs.cls and splncs04.bst, README.txt; cite package loaded.
Scratch compile in /tmp: 26 pages, 0 errors, 0 undefined, 0 overfull; with \finaltrue exactly three
"Unresolved \pending" errors. Final PDF `~/Desktop/LNNS_final.pdf` (26 pages). SUBMISSION_NOTES updated.

**Remaining \pending (3):** Zenodo DOI (Data and Code Availability), Acknowledgments, Disclosure of Interests.
**Old file names to rename (outside P2's files):** experiments/SEEDS.md:52; experiments/revision/A8_horizon.py:10,20;
experiments/revision/notes/A8.md:9; paper/registry/core.yaml:1231 (make_table3/table3a/3b).

## [NEEDS PALAASH]
- Weidmann check: gamma = 1.913 and rho_max = 5.4 (Table 1) against Weidmann 1993 (ETH, DOI 10.3929/ethz-b-000242008).
- Acknowledgments text (about four lines).
- Disclosure of Interests (about four lines), consistent with the conference paper's AI-use statement.
- Corresponding-author marking: confirm Palaash Gang and the email shown.
- Erratum for the conference paper ([13] in the paper, legacy solver sign defect): planned or not.
- Length: the invitation said 23-25 pages; the paper has 26. Confirm with the volume editors.
- Zenodo DOI after the deadlock-screen framework sync (steps in paper/SUBMISSION_NOTES.md).
