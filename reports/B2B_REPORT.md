# Batch 2B report

## Environment
- `.venv` (gitignored) built with the miniforge Python 3.13.12 that verified `figures/common.py`; `requirements-figures.txt` pins numpy 2.4.4, scipy 1.17.1, matplotlib 3.10.8, pyyaml 6.0.3, colorspacious 1.1.2 (the first four are the versions already installed).
- Root `Makefile`: `figures` runs each `figures/fig*.py` with `.venv/bin/python`; new `venv` target rebuilds the environment. `make paper` is green.
- `tools/build_fig2_cache.py` is the only step needing the plan root's interpreter (it imports the simulator); output is `figures/data/fig2.json` (0.7 MB, rounded), and `fig2_lone_trap.py` runs from that cache alone.

## Table 2 (C14)
- Last column header is now "Corrected numerics"; P, L, T, D read "persists", N keeps "effect disappears".
- D cells under both Δt columns read "no $\Delta t$ dependence" (notes: "definition: a static tilt is deterministic"). Caption is unchanged (two sentences).
- `table2_NOTES.md` updated to match (header note, D/P rows). `main.tex` loads booktabs and tabularx; Table 1 in §3 and Table 2 in §4 are `\input`. Build: 0 errors, no overfull boxes.

## Fig 2 (`figures/fig2_lone_trap.pdf`, 12.2 cm × 4.9 cm, in §5.1)
- Left: wall-force profiles at r = 0.20/0.25/0.30/0.35 m, dark grey, dotted/dash-dotted/dashed/solid; drive bands (5-95%) and median lines, C1 black, C3 RVO2 blue; x from -0.6 to 0.2 m (force is zero beyond the door plane).
- Right: cividis margin ±150 N (raster heat map under vector lines), 20 000 agents as small white points (alpha 0.35, rasterised; white reads on the dark and grey regions, grey points did not), C1 boundary black 1.2 pt, C3 τ ∈ [0.4, 0.6] s band blue with 0.9 pt edges. Y label is $v_0/\tau$ only (the long label clipped).
- Checks: peaks of the four profiles equal the g_max values in E1_analysis.json (83, 156, 291, 543 N).
- QA (`tools/qa_figs.py fig2_lone_trap`): all 9 fonts embedded; smallest text 5.98 pt (the exponent in the y-unit; tick labels 7 pt); minimum line width 0.60 pt; no text inside panels beyond ticks and axis labels.
- Greyscale: C1 line black vs C3 line mid-grey, bands both visibly tinted, C1 boundary black against light grey, C3 band mid-grey. Deuteranopia/protanopia: blue band and yellow-to-blue margin stay separable. In greyscale the left-panel C1 and C3 bands are told apart mainly by their median lines.
- PNGs: `figures/_qa/fig2_lone_trap.png`, `_grey.png`, `_deuteranopia.png`, `_protanopia.png` (gitignored, regenerate with the tool).

## References
- Weidmann 1993: found via DataCite API, record 10.3929/ethz-b-000242008 (techreport, ETH Zurich, IVT Schriftenreihe 90, 114 p., 1993-03; handle 20.500.11850/242008). A 1992 record (ethz-a-000687810, 84 p.) also exists; the 1993 one is used. Entry built field by field with a source comment; German title brace-protected.
- Fruin 1971: Library of Congress SRU (lx2.loc.gov:210/LCDB, MODS), LCCN 70159312; the loc.gov JSON API was blocked (403 challenge). Entry built from the MODS fields with a source comment.
- Both pointer comments in `paper/refs.bib` are replaced; `CITATION_MAP.md` updated.

## Skeleton
- 3 pages (title page, Table 1 page, Table 2 + Fig 2 page); section text is still empty.

## [NEEDS PALAASH]
- Table 2 cells inferred by complement (L/T/D "persists") and the T-row Δt cell wording from batch 1D remain unconfirmed.
- Weidmann: confirm that the 1993 second-edition record (114 p.) is the one you cite, not the 1992 first print.
- Hero storyboard option (A/B/C) still open from batch 1D.
- Not mine, left alone: uncommitted `plan/CHANGELOG.md` edits (session 2A).
