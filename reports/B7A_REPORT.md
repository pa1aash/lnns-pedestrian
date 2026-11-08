# B7A report: Table 3 fixes and the remaining prose (2026-11-09)

Commits on main: af423c6 (changelog C56-C59), 4af7de3 (Table 3, §6, Fig 5), ace6656 (§8, §9, abstract, back matter); this report follows.
`make numbers`, `make paper`, `make submission` green (23 pp, 0 errors, 0 undefined); overlap check 0 runs >= 8 words.

## Table 3
- J is now taken on the minority outcome set of each block: unresolved for lone trap (0.20 [0.00, 0.50]) and whole runs (0.41 [0.32, 0.50]), freed for the pairs: b*_pub 0.43 [0.26, 0.61] (13 of 30), b*_RVO2 0.00 [0.00, 0.00] (disjoint, 0 of 15). The "freed disjoint" note is gone.
- Pair Δ now has 95% intervals: +0.02 [-0.15, 0.22] (pub), +0.02 [-0.13, 0.17] (RVO2); 90% intervals removed. Source: `make_table3.py derive` -> data/derived/table3_pair.json (2000 snapshot resamples, PCG64(12345), unperturbed runs from data/E7b + data/E7b_bstar).
- Registry (core.yaml): TabThreePair{Pub,Rvo}Diff{,Lo,Hi} from table3_pair.json; TabThreePairRvoJacF{,Lo,Hi} added; the published freed J reuses PairBsPubJac*; the unresolved-set TabThreePair*JacU entries dropped. Caption: "Intervals are 95%".
- §6: one sentence states the minority-set rule (start of "Matched noise acts differently"). Fig 5 is a standard figure, natural width, caption below.

## Pages (tools/page_map.py --pinned)
| part | now | plan (C54) | | part | now | plan |
|---|---|---|---|---|---|---|
| front + abstract | 0.74 | 0.5 | | §6 | 4.01 | 4.5 (+0.3, C59) |
| §1 | 1.93 | 1.8 | | §7 | 1.89 | 1.9 |
| §2 | 1.26 | 1.4 | | §8 | 1.06 | 1.0 |
| §3 | 2.55 | 2.5 | | §9 | 0.41 | 0.4 |
| §4 | 2.50 | 2.5 | | back matter | 0.50 | 0.5 |
| §5 | 4.23 | 3.8 | | references | 2.15 | 1.9 |
- Pinned total 23.22. Projected = 23.22 + Table 4/§6.3 (1.1 less 0.15 of placeholders) + Fig 3 over its placeholder box (about 0.15) = **about 24.3 pp**. §6 then lands near 4.95, about 0.15 over even with the C59 allowance.

## Abstract
197 words (flow-ratio range counted as one word); 6 keywords.

## \pending remaining (11 in the build)
- §3 open geometries (E8/E9, Table 4); §5.1 critical width / jamb locality and Fig 3 box + caption (E7, 6B).
- §6.3: Table 4 + paragraph; E6p; E8; E9; E11 (one line each).
- Back matter: Zenodo DOI; acknowledgements and disclosure.
- (Fig 1 caption fallback, shown only if figures/fig1_caption.tex is missing.)

## [NEEDS PALAASH]
- Acknowledgements and disclosure: yours to write (\pending in the credits block).
- Projected 24.3 pp: the final pass should take about 0.3 pp, most easily from §5 (+0.43 over plan) and references (+0.25).
- The RVO2 pair row prints J = 0.00 [0.00, 0.00] (disjoint freed sets, so the resampled interval collapses). Keep, or print "0 (disjoint)"?
- Main-differences paragraph and data statement are new prose; please read them, since they speak for the authors.
