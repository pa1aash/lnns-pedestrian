# I3 report: final integration of the revised paper (2026-11-11)

Published to main: 9152cb1 (integration), 2fd2cae (audits and fixes), and this report. `make numbers`, `make paper`, `make submission` green.
**Pages: 25**, 0 errors, 0 undefined references, 0 overfull boxes; abstract 248 words, six keywords.
**Headroom:** with placeholder text of about four lines in each of the three `\pending` items (DOI 4 extra lines, Acknowledgments 4, Disclosure 5), the references end on page 25 with 44 pt free (about 3.5 lines). Before I3: 25 pages with about one line free and one-line placeholders, so about 15 lines were freed net of the I3 additions (Disclosure placeholder 5 lines). Cuts (no claim, figure or verified reference removed): Weibull detail merged into one clause; the longest sentences of 5.2, 5.4, 6.2 (horizon sentence repeated from 4.2), 7, 8, 9 shortened; Table 2's least informative Observed row (ORCA velocity filter, stated in 6.4) dropped; glossary "Classes" row dropped and the glossary set as one paragraph; 8.1 and 8.2 merged under one heading. Figure heights not trimmed (7 pt elements would fall below 7 pt).

## Figures
All nine figures are the FINAL files of reports/F_REPORT.md (width figure with 11 widths, escape figure with the beta 5-7 points, CroMa figure from the Part D rerun with 600 s right-censoring, geometry figure with both lengths); numbers 1-9 and every \ref resolve. Captions are F's content condensed to at most two sentences (Fig. 1 longer). Fixed: k_B upright in the Fig. 1 caption and in the Fig. 6(a) axis label (rebuilt with fig_escape_dt.py; sizes 7 and 8 pt); protocol figure push = "the drive part of the ORCA term at rest", its 10^-9 exponent at 7 pt; Fig. 6 caption names the black fits over beta = 1.5-7; Fig. 9 caption says the censoring is at the 600 s horizon and what filled markers are. Quench scope: "SFM and SFM+TTC free none" is scoped to the 60-snapshot screening set; 5 of 300 replays (screen) and 13 of 800 (all 160 second traps) are stated separately. Every figure page rendered at 100 dpi and inspected.

## Section 7 and geometry
Bottleneck lengths are 2.0 and 0.2 m in the text, Fig. 2 and the code default (CromaBottleneckScenario length=0.2); no 0.21 m remains (data/ext/croma/README.md corrected; "l021" is the run code). Table 1 lists no length.
**Corridor finding (verified from rev_D.json archive_geometry and the 4D030 trajectories):** the passage of 4D030/4D040 is straight and 0.8 m wide over the full 2.0 m (corridor faces y = ±0.4 m for x = 0-2 m; head tracks stay within |y| <= 0.28 m in every 0.5 m bin). What changes in the second metre is the wall block: 1 m thick over the first metre, then tapering at 45 degrees to a wedge tip at the exit. F2's "1 m slot plus 1 m flare" is the outer wall face, not the passage; P's limitation "the experimental one widens in its second metre" was wrong and is replaced. Sect. 7: "a straight bottleneck 2.0 m long (its walls, thin in the model, taper to a wedge in their second metre)"; Limitations: "The model's 2.0 m CroMa walls are thin, the archive's taper to a wedge." The model differs only at the exit end of the corridor walls (a free segment end against a 45-degree wedge).
**Rerun cost (not launched):** 2 human runs x 5 model runs x 4 variants = 40 runs of at most 600 s, 135 agents. The same 40 runs in the Part D rerun took 2.31 CPU-h (data/revision/D3/d3_croma.jsonl wall_s; longest single run 0.23 h, force-coupled ORCA); with two wedge segments per wall about 2.5 CPU-h, under 20 min wall on 8 workers, plus a scenario option for the wedge walls, the D4 reanalysis, macros and Fig. 9 (about 1 h of work). Expected effect small, since the passage is unchanged.

## Twelve referee items (reports/P_RESOLUTION.md): all resolved
F1 placeholders only + CroMa CC BY 4.0 sentence; m3 ninth decile reported; m4 U(a,b) -> \mathcal U, gate w_{o,i} -> \chi_i, classes are words, r_c, others distinct (schematic letter keys kept); m5 class headers, "Lower" defined; m6 one pooled ell (-0.0048) and one per-snapshot bound (0.018), labelled, noise ell 2.2 in both tables; m7 no leakage; m9 RVO2 v2.0.2 Zenodo 2016; m10 g_max(0.30) stated; m11 thin-space 20 000, unit style uniform; m12, m13 removed from the paper; m14 all participants pass, counts per run.

## Audits (reports/I3_audit/, fixlog.md)
Numbers: 1 wrong (arch peak forces, now max over both fine time steps: 18 kN, 4.8 kN), 0 superseded, 11 rounding; 11 applied, 1 declined (median drives 214/215 N kept). Compliance: 5 of 7 checks pass; 3 failing items (6 edits) applied. Consistency: 14 findings, 13 applied, 1 declined (ORCA at the pair is Reshape, axial per Table 2 note a). All cross-references resolve.

## Overleaf
~/Desktop/LNNS_overleaf/ and LNNS_overleaf.zip rebuilt; scratch compile in /tmp: 25 pages, 0 errors, 0 undefined, 0 overfull; with \finaltrue exactly three "Unresolved \pending" errors. ~/Desktop/LNNS_final.pdf = make paper output (same text as the scratch build). paper/SUBMISSION_NOTES.md updated (main differences, keywords, Overleaf, Zenodo and PRIMORIS steps).

## Remaining \pending (3): Zenodo DOI, Acknowledgments, Disclosure of Interests.

## [NEEDS PALAASH]
- Weidmann check: gamma = 1.913 and rho_max = 5.4 (Table 1) against the original Weidmann 1993 table.
- Acknowledgments and Disclosure of Interests (at most about four lines each), the disclosure consistent with the AI-use statement of the conference paper.
- Corresponding-author marking: confirm Palaash Gang and the email shown in the author block.
- Zenodo DOI after the framework sync (steps in SUBMISSION_NOTES.md).
- Whether to rerun the two 2.0 m CroMa runs with the archive wall shape (cost above).
