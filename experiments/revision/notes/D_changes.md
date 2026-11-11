# Part D: paper numbers that change (old = E10 / fix_a7 / A12 as in paper/numbers.tex; new = D2 humans, D3 rerun, D4 rule)

| quantity (Sect. 7) | macro (old) | old | new | new macro |
|---|---|---|---|---|
| human flow [95%], ped/s | EtenHumanFlow, ...Lo, ...Hi | 1.48 [1.22, 1.74] | 1.47 [1.21, 1.73] | RevDHumanFlow, ...Lo, ...Hi |
| human flow, 0.2 m bottleneck | EtenShortHumanFlow | 1.58 | 1.57 | RevDShortHumanFlow |
| human 10–90% window flow | FixAsevenHumanWindowFlow | 1.49 | 1.48 | RevDHumanWindowFlow (D.yaml) |
| "1 track is lost before" the entrance | EtenHumanUnpassed | 1 | 0 participants (duplicate ID) | text |
| short bottleneck length | text | 0.21 m | 0.2 m | text |
| SFM complete / deadlock | EtenCOneComplete / ...Deadlock | 1 / 24 | 2 / 23 | RevDThreeCOneComplete / ...Deadlock |
| SFM completion, upper Wilson bound | FixAsevenCOneCompleteHi | 0.20 | 0.25 | RevDThreeCOneCompleteHi |
| SFM flow, ped/s | EtenCOneFlow, ...Lo, ...Hi | 0.75 [0.73, 0.77] | 0.73 [0.71, 0.76] | RevDThreeCOneFlow, ...Lo, ...Hi |
| SFM flow ratio | FixAsevenCOneFlowRatio, ...Lo, ...Hi | 0.51 [0.43, 0.61] | 0.50 [0.42, 0.59] | RevDThreeCOneFlowRatio, ...Lo, ...Hi |
| SFM 10–90% window flow | FixAsevenCOneWindowFlow | 0.85 | 0.83 | RevDThreeCOneWindowFlow |
| B_w,edge complete / deadlock | EtenCEdgeComplete / ...Deadlock | 17 / 8 | 21 / 4 | RevDThreeCEdgeComplete / ...Deadlock |
| B_w,edge flow ratio | FixAsevenCEdgeFlowRatio | 0.57 [0.48, 0.68] | 0.56 [0.47, 0.67] | RevDThreeCEdgeFlowRatio, ...Lo, ...Hi |
| SFM+ORCA complete / deadlock / capped | EtenCThreeComplete / text "never deadlocks" / EtenCThreeCapped | 10 / 0 / 15 | 10 / 1 / 14 | RevDThreeCThreeComplete / ...Deadlock / ...Capped |
| SFM+ORCA flow, ped/s | EtenCThreeFlow, ...Lo, ...Hi | 0.87 [0.84, 0.89] | 0.88 [0.85, 0.90] | RevDThreeCThreeFlow, ...Lo, ...Hi |
| SFM+ORCA flow ratio | FixAsevenCThreeFlowRatio, ...Lo, ...Hi | 0.59 [0.49, 0.70] | 0.60 [0.50, 0.71] | RevDThreeCThreeFlowRatio, ...Lo, ...Hi |
| noise σ* complete (capped) | EtenCSigComplete | 14 (11) | 18 (7) | RevDThreeCSigComplete, ...Capped |
| noise σ* flow ratio | FixAsevenCSigFlowRatio, ...Lo, ...Hi | 0.40 [0.33, 0.48] | 0.40 [0.33, 0.48] (unchanged) | RevDThreeCSigFlowRatio, ...Lo, ...Hi |
| range of flow ratios (intro, Sect. 7) | FixAsevenCSigFlowRatio–FixAsevenCThreeFlowRatio | 0.40–0.59 | 0.40–0.60 | RevDThreeRatioMin–RevDThreeRatioMax |
| gaps > 2 s per run, ORCA–SFM | EtenCThreeGapsTwo–EtenCOneGapsTwo | 11–19 | 10–18 | RevDThreeCThreeGapsTwo–RevDThreeCOneGapsTwo |
| mean longest gap, deterministic | EtenCThreeGap–EtenCOneGap | 5.7–6.6 s | 5.3–8.0 s (all runs, up to the stop) | RevDThreeCThreeGap–RevDThreeCOneGap |
| mean longest gap, noise | EtenCSigGap | 72.2 s | 71.5 s | RevDThreeCSigGap |
| fluctuation, SFM–noise, m/s | EtenCOneFluct–EtenCSigFluct | 0.094–0.109 | 0.092–0.108 | RevDThreeCOneFluct–RevDThreeCSigFluct |
| short bottleneck flow, noise–ORCA | EtenCSigShortFlow–EtenCThreeShortFlow | 0.62–0.91 | 0.62–0.92 | RevDThreeCSigShortFlow–RevDThreeCThreeShortFlow |
| censored runs (SFM, edge, ORCA, noise) | RevAtwelve*GapCens | 24, 8, 15, 11 | 23, 4, 15 (1 + 14), 7 | RevDThree*Cens |
| longest gap of completed runs, max | RevDCOne/CEdge/CThree/CSigGapCompleteMax (D4) | 6.8, 10.5, 11.0, 269 s | 20.4, 15.6, 7.6, 237 s | RevDThree*GapCompleteMax |
| "at most X s" for deterministic completed runs | RevDCThreeGapCompleteMax | 11.0 s | 20.4 s (SFM) | RevDThreeCOneGapCompleteMax |
| KM median, B_w,edge / noise | RevAtwelveCEdgeGapKMMedian / RevAtwelveCSigGapKMMedian | 6.5 / 95.9 s | 6.1 / 95.9 s | RevDThreeCEdgeGapKMMedian / RevDThreeCSigGapKMMedian |
| median of c, SFM / ORCA (KM median not reached) | RevAtwelveCOne/CThreeGapLowerMedian | 16 / 433 s (D4 rule: 425 / 433) | 416 / 432 s | RevDThreeCOne/CThreeGapLowerMedian |

Unchanged: EtenHumanFlowMin–Max 1.15–1.71, EtenLongHumanFlow 1.32, EtenHumanGap 1.7 s, EtenHumanGapMax 2.04 s, EtenHumanGapsTwo
0.2 (1 gap > 2 s in total), EtenHumanFluct 0.074 [0.070, 0.079], EtenCSigLongFlow–EtenCThreeLongFlow 0.54–0.81
(RevDThreeCSigLongFlow–RevDThreeCThreeLongFlow), EtenHumanN 5.
Paired by seed, no variant's flow differs from E10 (all CI cover 0); McNemar p = 1.0, 0.29, 1.0, 0.22.
