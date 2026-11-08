# B5B report: matched completion, contact arches, human validity (2026-11-08)

Commits: 409363b, c7965c8, 1c0b9b2, ff0675d (pushed). `make numbers`, `make paper`, `make submission` green (23 pp, 0 errors, 0 undefined; known `\overlayfile` notice); overlap check 0 runs >= 8 words; CI (paper, tests) green on ff0675d.

## E6, matched completion (experiments/E6/analyze.py -> data/derived/E6_analysis.json)
- Completion: C3 RVO2 101/186 [0.47, 0.61], C1 + sigma* (0.0467 m/s) 99/186 [0.46, 0.60]; paired difference -0.01 [-0.10, +0.08] (Newcombe). 90% interval inside the +-0.15 margin (JSON only).
- Identity: discordant failures 35:37 (exact McNemar p = 0.91); Jaccard of the failure sets 0.41 [0.32, 0.50], vs 0.30 expected for independent failures (permutation p = 0.002): a few shared hard seeds, far from the same set.
- Time: KM medians 132 s vs 469 s; C3 RVO2 completes every successful run by 161 s, noise has 25 completions after 300 s; on the 64 seeds where both complete, C3 RVO2 is faster on 64/64 (median 66 s).
- Failure state (keystone surgery on the rebuilt final states, data/E6/keystone.jsonl, 683 restarts): C3 RVO2 31 at rest (all lone keystones) + 54 still moving at 600 s (51 hold a second trap); classes 33/51/1. Noise: none at rest; classes 56/31/0. Class tables differ, permutation p = 0.0014. C3 RVO2 re-holds its own rebuilt residual from rest in 78/85.
- Stall lifetimes (C1 + sigma*, intervals >= 10 s without an exit): 349 stalls, Weibull k = 0.64 [0.58, 0.70] (mixture over barriers). The barrier picture with no fitted parameter (56 gated library barriers, kT_eff at sigma*, E4 attempt rate) predicts the KM survival at 30/60/120/300 s within 0.05; median 59 s observed vs 69 s predicted.
- The final states were rebuilt from the saved residual positions (no snapshots were saved in E6); velocities set to zero. No whole-run replay test was run; the §6.1 text cites the E2 snapshot replays.

## Contact arches (§5.3; production run, experiments/arch/ -> data/arch/, data/derived/arch_analysis.json)
- No production version existed (only the W2.9 pilot: 5 seeds, 300 s). Ran CF, C1, w = 0.8 m, 100 agents, mean v0 = 5 m/s (pilot's highest drive), seeds 42-66, 600 s, 2 workers.
- Jamb-to-jamb contact chains in 22/25 runs (103 episodes, 93 with >= 3 agents, up to 10 agents, up to 108 kN body compression), at most 2.9 s, 95% within 0.6 s. Persistent (>= 10 s): 0/25, Wilson upper bound 0.13. All 25 runs complete (median 77 s).
- Physics stated: the SFM's tangential force is proportional to sliding velocity and vanishes at rest (no static friction).

## E10 vs humans (experiments/E10/analyze.py -> data/derived/E10_analysis.json; estimator w28_croma.py unchanged)
- Humans (5 runs): flow 1.48 [1.22, 1.74] ped/s, longest gap mean 1.7 s (max 2.0 s), 0.2 gaps > 2 s per run, fluctuation 0.074 m/s; no deadlock.
- Model (25 per cell), completion / flow ratio to humans / mean longest gap / gaps > 2 s:
  C1 published 0 (25 deadlock) / 0.49 / 6.8 s / 17; C1 CF 1 (24 deadlock) / 0.51 / 6.6 s / 19; C1 CF + jamb B_w 0.04: 17 (8 deadlock) / 0.57 / 6.2 s / 13; C3 RVO2 10 (15 still moving at 600 s) / 0.59 / 5.7 s / 11; C1 CF + sigma* 14 (11 capped) / 0.40 / 72 s / 18.
- Every variant deadlocks or flows at 0.40-0.59 of the human rate with long gaps; the same for L = 2.0 m and 0.21 m. 0 wall leaks in 125 runs.
- Fig 8 (fig8_croma): 3 panels, category ticks only, runs + mean with t-interval, gap on log scale; QA: fonts embedded, min line 0.60 pt, smallest text 4.98 pt (sigma* superscript); PNG and CVD renders viewed.

## Table 3 and pages
- Table 3 complete: lone-trap rows (E2-E4), E6 block, pair-class block from E7b_analysis.json incl. the two matched-bias rows (s3_matched). Rerun `python3 experiments/tables/make_table3.py` if 5A updates E7b. Now a float page ([p], page 14); it was deferring to after the references as [t].
- Page map (pinned): §5 4.23, §6 5.56 (budget 4.0; Table 3 is now a full page), §7 1.89 (budget 2.0), total 22.81; PDF 23 pp. §5.3 is 182 words (~0.4 p); the §6.1 matched-completion paragraph is 307 words (~0.65 p).

## Proposed changelog text (numbering by 5C)
- Cx E6 is reported as the whole-run instance of the thesis: matched on completion (Δ -0.01 [-0.10, 0.08]), separated on failure identity (Jaccard 0.41), completion time (64/64 seeds faster under C3 RVO2) and final-state class (p = 0.0014). The keystone classes come from surgery on final states rebuilt from the saved residual positions.
- Cx Noise stall lifetimes in whole runs are compared with a no-fit prediction from the gated library barriers, kT_eff(σ*) and the E4 attempt rate (agreement within 0.05 in survival).
- Cx §5.3 rests on a production high-drive run (25 seeds, 600 s, v0 = 5 m/s), replacing the W2.9 pilot as the source.
- Cx E10 fluctuation is the waiting-zone *velocity* fluctuation of the unchanged W2.8 estimator (RMS over the two components); the prompt's "density fluctuation" is not what the estimator measures.

## Surprises (proposals)
- P1 Most C3 RVO2 whole-run failures (54/85) are not at rest: two agents keep moving at the jamb at ~0.2 m/s for the rest of the run. This is the second trap (51/54), i.e. the pair class showing up in whole runs. Worth a sentence in §6.2 (5A).
- P2 The model's waiting zone is *more* agitated than the human one (0.087-0.109 vs 0.074 m/s) in every variant.
- P3 In the CroMa geometry matched noise lowers the flow (0.40 of human) and gives the longest gaps (72 s): σ* matched in the room does not transfer.

## [NEEDS PALAASH]
- data/E10/raw (125 trajectory files, 430 MB, each < 5 MB) not committed: it would grow the public repo from ~100 MB to ~530 MB. The per-run estimator output is in data/E10/e10_croma.jsonl. Commit it, or add it to .gitignore?
- §6 is 1.56 pp over budget, mainly Table 3 (now a full page). Options: move the signature rows (E3/E4) to text only, or shorten the caption.
- Pending items in files I do not own: the Introduction bullets (Attribution "matched completion of whole runs \pending{E6, E6p}", Validity \pending{E10}) and §3 "\pending{E10 results, Sect. 7}". Proposed Validity bullet: "In the like-for-like CroMa geometry every model variant either deadlocks or flows at 0.40-0.59 of the human rate with long gaps, whereas real crowds flow without deadlock (Sect. 7)." 17 \pending remain in the build.
