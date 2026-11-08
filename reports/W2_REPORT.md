# W2 report: compaction and sourcing (2026-11-09)

**Builds.** make numbers (300 macros), make paper and make submission are green: 17 pp, no undefined refs or overfull boxes. The submission compiles standalone (17 pp), still warns `\overlayfile` (the HF fig1 dependency) and has 23 `\pending`. Commits: C34–C37 7cd1cb0; W2 041b2d3. CI: paper and tests green (runs 42491016928, 42491016926).

**Pages** (`tools/page_map.py --pinned`: floats set in place, so each part is charged its own floats)

| part | before (2d9be04) | after |
|---|---|---|
| title+abstract / §1 (Fig 1) / §2 | 0.40 / 1.84 / 1.41 | 0.40 / 1.89 / 1.26 |
| §3 (Table 1) / §4 (Table 2) | 2.67 / 3.22 | **2.50 / 2.50** |
| §5 / §6 (drafted + placeholders) | 3.17 / 2.86 | 3.16 / 2.86 |
| §7–§9 + back matter (stubs) / references | 0.58 / 2.85 (34) | 0.58 / **1.94 (23)** |
| total (real PDF) | 19.00 (19 pp) | 17.09 (17 pp) |

**Projection.** Without the placeholders and stubs, the drafted content is 15.91 pp. The pending budgets add 8.3 pp (§5.2 0.9, §5.3 0.4, §6.2 1.0, §6.3 0.6, §7 2.0, §8 1.2, §9 0.4, back matter 0.5, Fig 3 0.4, Table 3 0.4, Table 4 0.5). That gives **≈ 24.2 pp**: 0.2 over the C35 target of 24, inside 23–25. The kept subsection headings may be counted twice, worth up to about 0.2 pp.

**References removed (14).** liang2024, helbing2012: a list of events, not a physics claim; the opening no longer names Seoul and Duisburg; vandenberg2008: ORCA's paper covers the reciprocity.
- dang2024, cristiani2023, vantoll2021: a decorative simulator cluster; the sentence was dropped.
- koster2013: not a kept category; our numerics are documented in Table 1. steffen2010: decorative Voronoi contrast.
- henkelman2000: CI-NEB is not used. cugliandolo1997: our T_eff comes from the AR(1) recursion.
- barraquand1991 → koren1991; grover2023, wang2017 → grover2020; grimm2012 → grimm2005 (merged).
- Added wilson1927, mcnemar1947 and kaplanmeier1958 (already in refs.bib) in §3 "Scenarios and statistics".

**New macros.**
- E1_terminal.json (experiments/E1/terminal.py): `\TermN` 393; `\TermRhoMedian`/`Max` 0.07/0.35 ped/m²; `\TermNbMedian`/`Max` 2/10; `\TermWeidMin`/`Median`/`Max` 0.994/1.000/1.000; `\TermFracHigh` 1.00 (`\TermNHigh` 393 with v_eff/v0 ≥ 0.99); `\TermRadius`.
- field_residuals.json (experiments/E7b/residuals.py): `\ResidPairMax` 1e-7 N (`\ResidPairN` 46, e7b_static.jsonl); `\ResidLoneMax` 4e-8 N and `\ResidCollMax` 5e-7 N (`\ResidBarN` 60, BAR/barriers.jsonl); `\ResidAllMax`. The E4-only values are in the JSON. Quoted in §3, §4 and §5.1.
- `fmt: sci` (configurable `digits`) applied to six McNemar p, the Fisher p (2.3×10⁻⁴) and `\EthreeCThreeLnRatio`.

**§3/§4.**
- All used equations are kept; the AR(1) equation, never referenced, is now inline.
- Table 1 regenerated: Room row, density floor, uncalibrated note, TTC threshold, and Noise/ORCA-solver mode rows; model.yaml gained room, door_width and n_agents.
- Table 2: short headers, the N row moved into the caption, and the P/T/D cells trimmed. No prediction changed (table2_NOTES.md). C37 made true: README lists latexpand; the nicolas2018trap comment notes the re-encoding.

**Overlap.** No shared run of 5 or more words; the longest is 4 words.
**[NEEDS PALAASH]**
1. C30 says the residual is "~5e-8 N". The sourced maximum is 4.9e-7 N (collective; median 3e-8). Amend C30?
2. Is it acceptable to drop the Seoul/Duisburg citations from the opening, and to drop koster2013?
3. "Every p in sci" makes McNemar p = 0.125 print as 1.2×10⁻¹. Keep that, or print plain decimals for p ≥ 0.01?
4. The projection is 0.2 pp over target. Final-pass candidates are §5.1 (with Figs 2 and 4) and §6.1.
