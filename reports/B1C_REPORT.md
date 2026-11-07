# B1C report (references, numbers pipeline, Table 1)

## References (paper/refs.bib, 195 entries, 195 unique keys; fetched 2026-11-07)
All entries below fetched by `Accept: application/x-bibtex` on doi.org (Crossref/DataCite), source comment above each.
- Outline: kramers1940, arrhenius1889 (Crossref has two records; the one with pages 226-248), weibull1951, wilson1927, mcnemar1947.
- RVO2: vandenberg2011rvo2, built from the authors' CITATION.cff (they ask for citation by that metadata; the ORCA paper vandenberg2011 is its first reference, cite both).
- Conference bibliography: cristiani2023, dang2024, fiorini1998, guy2010 (DataCite, Eurographics), helbing2012, korbmacher2022, liang2024, mullick2025, steffen2010, vantoll2020, vantoll2021.
- Already present, left unchanged: gang2026, helbing1995, helbing2000nature, karamouzas2014, vandenberg2011, zuriguel2014, nicolas2018trap, hanggi1990, cugliandolo1997, grover2020, grover2023, grimm2005, grimm2012, e2002, e2007, kaplanmeier1958, fzj_ped20219.
- Keys normalised (only the 60 keys that were not authorYEARword: r2..r119 and avocado, e.g. r114 -> e2002string); bodies untouched. fzj_ped* dataset keys kept.
- Outstanding: Fruin 1971 (book, no DOI; only a catalogue record found) and Weidmann 1993 (ETH thesis; no Crossref/DataCite record, ETH collection blocked headless). Pointer comments are at the end of refs.bib. Table 1 and the model section need Weidmann.
- Conference-bibliography errors found against Crossref: Seoul Halloween paper is Liang, Lee, Sun, Wong (conference lists Lee, Kim, Park, Choi); Mullick et al. is article 130251, Jan 2025 (conference: 130204, 2024); van Toll pairs the MIG 2020 title with the C&G 2021 venue. Both van Toll papers are in the file.
- Crossref `month=July/June/Sept` strings give BibTeX "undefined string" warnings (month is not printed by splncs04); entries left as fetched.
- paper/CITATION_MAP.md: section to keys with one line each; 150 entries listed as not needed by the outline (kept).

## Numbers pipeline
tools/make_numbers.py + paper/numbers_registry.yaml (header comment only). Tested with a dummy registry (two macros, unit macro) and a bad key path (exit 1, names the macro); dummy removed, numbers.tex now has no macros.

## Parameters (data/params/model.yaml; exec-v1 at 8b29429, no fallback needed)
Every §7 parameter agrees in value. Disagreements (details P1-P8 in the YAML):
- P1 plan line references are stale (hybrid.py:128-129 is now 151-152; simulation.py 162-179 is now 184-224).
- P2 corner flag value is `convex_union` in code and C4, `union` in the plan flag table.
- P3 plan wording "union at every shared end" differs from the conditional C4 rule the code implements.
- P4 w2_crush and w2_wall_corner are already implemented (plan says to implement).
- P5 params.yaml has unread keys (density.grid_radius 2.0, kde_bandwidth, risk, optimization); density is the 3 m disk. P6 params.yaml agent.tau 0.5 only for non-heterogeneous agents.
- P7 quench stop |v| < 1e-3 and 120 s censor not found in w2lib.py (not verified). P8 ORCA overlap case uses dt as horizon (plan silent).
- The 8 GB-Mac note: w2lib.py was read from the plan root (read only); it is not on exec-v1.

## Table 1 (paper/tables/table1_params.tex, not yet \input)
booktabs works with llncs (tested). Width 12.2 cm. Height 226 pt of the 549 pt text block: 0.41 of a page for the tabular, 0.47 with caption. Caption is two sentences. Generated from the YAML; asserts check the mode wording against the YAML flags.

## Makefile and Actions
`numbers`, `tables` added; `paper` depends on both; `make paper` builds clean (2 pages). Actions run on e50e1c1: success (also b3984b2 and eb54321).
