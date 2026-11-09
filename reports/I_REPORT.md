# I report: integration pass before the authors' read (2026-11-10)
Published to main: 0b65cbe (decisions 1–6), 5266f31 + 1a0ccfd (re-audit fixes). The submission folder compiles alone in /tmp with 0 errors, 0 overfull boxes and 0 undefined references; fonts are embedded. Final PDF: ~/Desktop/LNNS_draft_final.pdf.
**Pages: 25 physical = 24.1 (page 25 holds the last 4 lines of reference 37), at the bottom of the 24–24.5 target and within the 25-page cap.**

## What changed
- N6: §5.3 states the non-smooth loss of the minimum where a member reaches a jamb segment end (92/92). Exponents are 1.00 and 2.00 against the saddle-node's 0.5 and 1.5, the passage exponent is −0.16, and μ₁ is 65–121 N/m at the loss. Class D in §4 reads "removes a strict minimum at a finite threshold b_f". §8 has the unifying wall-geometry sentence. No "fold" remains anywhere.
- \pending filled: §3 (open geometries → Table 4), §5.2 N3, §5.3 N6, §5.4 N5 (no arch persists at Δt = 0.0025 s or at lower drives; at the default drive all 25 runs deadlock with no arch, and completion is not claimed there), §6.1 N1 (σ = 0.0717, J = 0.75 for both pairings, [0, 1]), §6.2 N2 (J 0.48 against 0.41/0.51 and 0.30–0.33).
- §1 and §9: critical width 0.88 m "under the default wall law"; arches break within 3.3 s, the maximum at either time step. sec:att-conf removed. Main Differences states the four rerun verdicts. Changelog C65–C84 added; F3's pair-standoff entry is merged into C83.
- Page pass: the re-audit fixes pushed the end to 24.15 pages; tightening ten paragraph endings brought it back to 24.1. The 5-seed J split in §6.1 is cut, because N1's 20-seed test supersedes it and Table 3 still prints that J. No result was dropped.

## Re-audit fix classes (reports/integration/)
- Numbers and claims: 0 of 523 macros mismatched or undefined, 3 WRONG fixed, 14 IMPRECISE fixed, 4 contradictions resolved, 3 literal results moved to new macros, 1 macro key corrected, 2 interval labels added.
- Prose: 77 entries; 67 applied. Declined: 5 heading changes (taste), 1 Fig. 1 caption cut (decision 4), 1 split sentence (§5.1), 1 "cause unknown" deletion, 1 rename g_max → f_max. One was resolved another way: σ₅₀ now cites both intervals.
- Compliance: 8 defects (D1–D8) fixed: 3 overfull boxes including Table 3 at +42 pt, now `\resizebox` with shorter labels; Table 1 underfull; 4 glossary slips. Everything else passes. Fig. 1 is exactly 600 ppi as placed.
- Overlap: 0 shared runs of 8 or more words.

## Remaining \pending (exactly three)
Zenodo DOI; acknowledgements; Disclosure of Interests text.

## Conference-claim verdicts (Table 4, Sect. 6.4)
- Confirmed (3): C2 = C1; published ORCA completion (29/50 against 13/25, p = 0.632); noise σ count.
- Revised (5): C1 completion; σ₅₀; arch → lone wall-law trap; deadlock set by the wall law (0.88 m); TTC throat overlaps (count reproduced, none lasts 0.1 s).
- Withdrawn (7): noise acts as ORCA; ratio/Cox HR; zonal overlaps; C4 evacuation cuts; ORCA counterflow gridlock; TTC tripling of crossing flow; flow 26–43% below data.

## What a skeptical referee could still attack (ranked)
1. 06_attribution.tex:48 + make_table4.py:161: σ₅₀ is "revised" although the printed 0.049 sits at the upper edge of the seed-resampled interval [0.041, 0.049]; only the profile interval [0.042, 0.047] excludes it.
2. 06_attribution.tex:45: the pair bias match is in-sample by construction; out of sample it misses by up to ±0.35, as widely as a rate-copying control, at n = 46.
3. 05_deadlock_physics.tex:39: the Weibull shape exceeds 1 pooled (1.09), pinned (1.14) and alone (1.07), and the collapse slope excludes −1. Kramers is supported only per fit and after a lag.
4. 06_attribution.tex:22: at the lone trap J has interval [0, 1] (3–4 unresolved snapshots), so "identity does not separate" there is weak evidence.
5. 04_signatures.tex:8: "the rest-drive push frees every blocker ORCA frees" has no paired count in data/derived (only 31/34 and 30/34).
6. 04_signatures.tex:28 vs 05_deadlock_physics.tex:52: 60 barrier snapshots against 56 library barriers, with no reason given for the four dropped.

## [NEEDS PALAASH]
- **Decision 2 overruled by the data:** "Weibull > 1 only when pooled" is false. Pinned 1.14 [1.06, 1.21] and alone 1.07 [1.002, 1.15] also exclude 1. §5.2 now says so with every interval, and F3_REPORT carries the same slip.
- σ₅₀ row of Table 4: keep "revised" (profile interval) or change it to "confirmed" (seed-resampled interval)?
- Fig. 3 tick reads "jambs 0.04" (the caption explains B_{w,edge}); re-render with B_{w,edge} in the tick if you want it in the figure.
- Alt text (figures/ALT_TEXT.md) is not in the submission folder; its Fig. 3 and Fig. 6 entries differ slightly from the captions.
- Six keywords (some Springer volumes cap at five); run-in headings are in sentence case; the class prints "Acknowledgments" (llncs, unchanged).
- Fig. 1 is exactly 600 ppi with no margin, and its PNG metadata says 72 dpi.
- Release tag v1.0-lnns deferred (C84).
