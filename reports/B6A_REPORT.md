# B6A report: compaction and bookkeeping (2026-11-09)

Commits on main: 1d562a3 (changelog), da37fff (data policy), 061e612 (Table 3, §6, §1-3); this report follows.
`make numbers`, `make paper`, `make submission` green (21 pp, 0 errors, 0 undefined); overlap check 0 runs >= 8 words.

## Changelog added (plan/CHANGELOG.md)
- C44-C46 from B5A (pair-class matched bias, pair deviations, C26 confirmed); C47-C50 from B5B (E6 thesis instance, stall-lifetime prediction, §5.3 production arch run, E10 velocity fluctuation).
- C51 T5 signed; C52 data policy (Zenodo); C53 Table 3 restructure; C54 page plan (24 pp); C55 worktree rule.
- .gitignore: data/E10/raw/ (429 MB; the only raw folder over 50 MB). Back matter: Zenodo DOI \pending.

## Table 3 (experiments/tables/make_table3.py -> paper/tables/table3_matched.tex)
- [t] float, about 0.45 page (p. 15), 8 rows x 8 columns, 3 blocks: lone trap (C1 + noise σ = 0.07 vs C3 RVO2, E2 lone keystones), whole runs (C1 + σ* vs C3 RVO2, E6), pair (b*_pub vs C3 published, b*_RVO2 vs C3 RVO2, E7b).
- Columns: freed, Δ [CI], J [CI] of unresolved sets ("freed disjoint" on the RVO2 pair row), t1/2, lower member first, replay, ℓ (E3). Unmeasured cells "---"; pair t1/2 printed as ">120" (KM median not reached).
- Every cell is a registry macro (30 new TabThree* entries in core.yaml, the rest reused); the script fails if a macro is missing. E3/E4 rows dropped. Caption: 2 sentences.

## Pages (tools/page_map.py --pinned), against the C54 plan
| part | now | plan |  | part | now | plan |
|---|---|---|---|---|---|---|
| front | 0.40 | 0.5 | | §6 | 3.69 | 4.5 (3.4 without T4/§6.3) |
| §1 | 1.92 | 1.8 | | §7 | 1.89 | 1.9 |
| §2 | 1.26 | 1.4 | | §8 / §9 | 0.15 / 0.10 | 1.0 / 0.4 |
| §3 | 2.55 | 2.5 | | back matter | 0.22 | 0.5 |
| §4 | 2.50 | 2.5 | | references | 2.15 | 1.9 |
| §5 | 4.23 | 3.8 | | pinned total | 21.05 | |
- Projected total = current 21.05 + Table 4/§6.3 1.1 + §8/§9 still to write 1.15 + abstract 0.1 + Fig 3 about 0.35 + back matter 0.3 = about 24.0 pp (before page-fill losses). Over plan: §5 +0.43 (6B), refs +0.25, §6 +0.29, §1 +0.12.
- §6 went from 4.89 to 3.69 (text 1450 to about 800 words; Fig 5 caption set beside the figure; Fig 6/7 captions shortened). Every result kept; the duplicates of Table 3 and of the C26 numbers were cut.

## Placeholders resolved
- Intro: Physics (pair minimum, fold, contact arches), Attribution (pair class, whole runs), Validity (flow 0.40-0.59 of human, gaps >= 5.7 s vs 1.7 s; fresh wording). §3: CroMa geometry now points to §7.

## \pending remaining (12 in the build)
- Fig 3 + caption (E7, 6B); §6.3/Table 4 (E6p, E7, E8, E9, E11); §3 E8/E9 open geometries (Table 4); §8; §9; abstract + keywords; back matter (differences, Zenodo DOI, acknowledgements); Fig 1 caption fallback (shows only if figures/fig1_caption.tex is missing).

## [NEEDS PALAASH]
- §6 is 0.29 pp over the 3.4 left for it once T4/§6.3 take 1.1: cut a result (candidates: the E6 stall-lifetime prediction, or the second-trap force numbers), or allow §6 4.8.
- Table 3 gives J for the unresolved sets, so the RVO2 pair row reads 0.67 with "freed disjoint" next to it. Should freed-set J be the headline for the pairs (B5A proposal)?
- Fig 5 now has its caption beside the figure (minipage); keep, or go back to a caption below (+0.08 pp)?
- The pair-block Δ uses the 90% (TOST) interval, the other blocks 95%; a 95% interval for the pairs would need a 5A re-analysis.
