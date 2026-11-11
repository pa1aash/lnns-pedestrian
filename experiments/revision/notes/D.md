# D: CroMa integrity check (Sect. 7)

Scripts: `experiments/revision/D_croma_integrity.py` (analysis, no simulations; about 3 CPU-min) and `experiments/revision/D3_croma_rerun.py` (optional rerun, written and smoke-tested, not launched). Output: `data/derived/rev_D.json`. Registry: `experiments/revision/notes/D.yaml` (112 macros, prefix `RevD`, checked unique against paper/numbers.tex; validated with make_numbers).
Cross-check: run on the files as used, the script reproduces EtenHumanFlow, EtenHumanFluct, EtenCOneFlowRatio[Lo], FixAsevenCSigFlowRatioLo and FixAsevenHumanWindowFlow exactly. That includes replaying the E10 bootstrap RNG sequence.

## Archive documentation (fetched 2026-11-10)

- Run overview PDF on the archive (`2021bottleneck_run_overview.pdf`): run name, start and end timecodes (hh:mm:ss:ff at 25 fps), N, w, l, h and line-up for all 24 runs of day 4 (11.10.2021).
- Boomers et al. 2023, Collective Dynamics 8, DOI 10.17815/CD.2023.141 (journal PDF). Sect. 3.7 and App. A.9, Table 19 give the same N, w, l, h and line-up. For 4D110, Table 19 notes "mix up: first row queue behind". Sect. 3.7: "bottleneck length: 0.2 m, 2.0 m"; the coordinate origin is at the front of the bottleneck walls; the finish line is 8 m behind the bottleneck. Sect. 4.2: all runs were manually corrected after automatic tracking.
- Landing page ped.fz-juelich.de/da/2021bottleneck (DOI 10.34735/ped.2021.9): "Length of bottleneck l [m]: 0.2, 2.0"; N "was in most cases the number of persons available at the time"; "all datasets were trimmed to the same length".
- hdf5 release of the same archive (metadata date_modified 2025-05-07, status "data revised"). Per run it gives `number_participants` (identical to the table), a `wkt_geometry` and notes. For 4D130 the note reads "Possibility was given for people to sit out the high motivation run". The WKT gives the inner bottleneck faces at y = ±0.4 m from x = 0 to l, with l = 0.2 m or 2.0 m. **For l = 0.2 m the wall is 0.2 m deep within |y| < 1.05 m and 1 m deep beyond.**
- The hdf5 trajectories equal our txt files row for row in 4D030, 4D040, 4D110 and 4D130. In 4D120, the revised hdf5 drops 9075 rows: 33 tracks that the txt extends back to frame 0 behind x ≈ −4.1 m now start at the edge of the camera field. This changes no passage, flow, gap or fluctuation value (computed: 4D120 flow 1.595 and fluctuation 0.0714 in both).

## D1. Participants, track IDs and passages

Rules. **Track rule** (E10, fix_a7): a passage is the first frame with x ≥ 0 of a track that starts before the line, one per track ID. **Participant rule**: the same crossing, counted once per marker ID. Every participant wore one ArUco marker. A track whose marker is carried by a longer track at the same place is a duplicate and is dropped.

| run | l (archive) | participants N (archive) | track IDs (file) | distinct markers | passages, track rule | passages, participant rule | cause of the difference |
|---|---|---|---|---|---|---|---|
| 4D030 | 2.0 m | 161 | 135 | 135 | 135 | 135 | 26 participants of the table are not in the recording; no passage is missing (tests below) |
| 4D040 | 2.0 m | 160 | 136 | 135 | 135 | 135 | 25 not in the recording; ID 35 duplicates ID 107 (marker 717, median separation 0.007 m over 233 frames) and ends 0.16 m before the line |
| 4D110 | 0.2 m | 132 | 131 | 129 | **131** | **129** | IDs 120 and 121 duplicate IDs 5 and 11 (markers 664 and 909, the full track length, median separation 0.002 and 0.026 m). Both copies cross, so **2 passages are double-counted**. 3 participants of the table are not in the recording (Table 19: "mix up: first row queue behind") |
| 4D120 | 0.2 m | 132 | 129 | 129 | 129 | 129 | 3 not in the recording |
| 4D130 | 0.2 m | 129 | 128 | 128 | 128 | 128 | 1 not in the recording (h2 run; participants could sit it out) |

Checks on every file:
- **Start.** At frame 0 the nearest head is 1.81–1.90 m from the entrance centre in the four h0/h1 runs (the 2 m semicircle is still clear) and 0.16 m in 4D130 (lined up at the bottleneck). The mean speed over the first 2 s is 0.11–0.20 m/s, and the first passage comes at 0.9–2.8 s. No track starts beyond the entrance. **Nobody had passed before the recording starts.**
- **End.** Every track except the 4D040 duplicate ends at x = 1.79–2.02 m, which is the far edge of the camera field behind the entrance. The file ends at the frame in which the last participant leaves the field, so no one is left in the holding area. The documented run lasts 2.1–3.1 s longer than the file in every run. That matches the documented end at a finish line 8 m behind the bottleneck. **The files are not truncated before the last passage.**
- **Late starts** (tracks that begin after frame 0): 2 in 4D030 and 1 in 4D040, entering at x ≈ −7.4 to −7.7 m (the back edge of the camera field), and 8 in 4D110 at x ≈ −4.1 m. All of them cross the line.
- **ID swaps and merges.** The largest frame-to-frame step is 0.15 m (3.7 m/s). Two distinct markers stay within 0.1 m for at least 1 s once: 4D110, markers 861 and 958, for 2.5 s. They are two people who cross 3.3 s apart, not a merge.
- **Missing passages, test (i): headway thinning.** Suppose the archive's N had passed and only the tracked people were recorded. Then about 16% of the observed headways in 4D030 and 4D040 would span two or more true headways. Statistic S = number of headways > 2× the median headway.
  - 4D030: S = 1 observed against a mean of 10 under that hypothesis (2.5th percentile 5), p < 10^-4.
  - 4D040: S = 2 against 10, p < 10^-3.
  - 4D110, 4D120, 4D130 (1–3 missing): the test has no power (p = 0.16, 0.23, 0.47).
- **Missing passages, test (ii): crowd holes at frame 0.** Inside the convex hull of the heads, the area farther than 0.7 m from every head is 0.03 m² (4D030) and 0.00 m² (4D040). Untracked people standing in the crowd would leave about 1 m² each. The density, 3.7 and 4.0 heads/m², equals that of 4D010, where all 136 participants of the table are tracked.
- **Across the archive** (24 runs of the hdf5 release): N equals the track-ID count in 15 runs. It exceeds it by 20 or more in 4 runs, all h0/h1 runs with a 2 m semicircle (4D030, 4D040, 4D070 153 vs 128, 4D090 152 vs 129). Their neighbours 4D080 and 4D100 have N = 129 and 131 and match their tracks. The documentation does not say how N was counted.

**Conclusion D1.** Every participant in the camera field passes the entrance plane and is in our files. The participants were 135, 135, 129, 129 and 128. In 4D030 and 4D040, 26 and 25 of the documented participants are neither in the recorded crowd nor among the passages. The data rule out untracked passages, so these people did not take part in the recorded run, or the documented N is wrong; the archive does not say which. In 4D110 the E10 count of 131 passages includes 2 duplicate tracks, so it double-counts two participants. EtenHumanUnpassed ("1 track is lost before it") refers to the duplicate ID 35 in 4D040. That participant passes under ID 107.

## D2. Corrected human numbers

Rule: participant rule (duplicate tracks removed). Flow = (n − 1)/(last − first passage); the estimator is otherwise unchanged (experiments/pilot/w28_croma.py). Only 4D110 changes: n = 129, flow 1.430 → **1.408** ped/s, 10–90% window flow 1.402 → 1.375. The longest gap (1.40 s) and the number of gaps > 2 s are unchanged. The 4D110 fluctuation rises from 0.0777 to 0.0782 m/s, because each duplicate had acted as a co-moving neighbour of its own original. The 4D040 duplicate changes the fluctuation by < 10^-4.

| quantity | as used | corrected | macro |
|---|---|---|---|
| human flow, mean [95%] | 1.48 [1.22, 1.74] | **1.47 [1.21, 1.73]** | EtenHumanFlow(Lo,Hi), FixAsevenHumanFlow(Lo,Hi) change |
| 0.2 m runs, human flow | 1.58 | **1.57** | EtenShortHumanFlow changes |
| 10–90% window flow | 1.49 [1.20, 1.77] | **1.48 [1.19, 1.77]** | FixAsevenHumanWindowFlow, ...Lo change |
| flow range | 1.15–1.71 | 1.15–1.71 | unchanged |
| longest gap, mean (max) | 1.7 (2.04) s | unchanged | |
| gaps > 2 s | 1 | unchanged | |
| fluctuation | 0.074 [0.070, 0.079] | 0.074 [0.070, 0.079] | unchanged at display precision |

## D3. Agent number and bottleneck length of the model runs

- **Agent number.** `e10_croma.py` RUNS uses N = 135, 136, 131, 129, 128. That is the track-ID count of each file, not the archive N and not the participants. The participants who passed are 135, 135, 129, 129, 128. So 4D040 has one agent too many and 4D110 two too many (at most 1.6%). The archive N (161, 160, 132, 132, 129) would be the wrong target, because the human flow is measured on the recorded participants only.
- **Length.** In the scenario (code/sim/scenarios/croma.py), L enters only as the two inner bottleneck walls y = 5 ± w/2 from x = 10 to 10 + L and as the goal point at x = 10 + L + 1. Going from 0.21 m to 0.2 m shortens the wall ends behind the entrance plane by 1 cm. The passage is counted at x = 10, and the front wall, the jambs and their door-edge tags are unchanged. The archive WKT confirms that the inner faces run from 0 to l at y = ±0.4 m, so the rebuilt faces match apart from that 1 cm.
- **Verdict.** Neither difference can move a flow ratio by a resolvable amount. The five model runs of one human run already differ by up to 0.1 ped/s (deterministic variants) and 0.5 ped/s (noise) (A12 table), while 1–2 fewer agents out of 130 shift the end of a run by about one headway. A rerun is not needed for any claim. It is needed only if the text keeps "matched agent number run by run" and "0.2 m" literally.
- **Rerun script, if wanted.** `D3_croma_rerun.py` runs the four Sect. 7 variants, 5 model runs per human run (25 per variant), 600 s, with N = 135/135/129/129/128 and L = 2.0/0.2 m, using E10's run() unchanged and σ = 0.0467 m/s. Output is resumable JSONL in data/revision/D3/ and the script takes the qargs options. It passed a smoke test on one worker (`--limit 2 --every 2 --scale 0.01`: 4D030 with N = 135, L = 2.0, and 4D110 with N = 129, L = 0.2; 12 CPU-s each), and the scratch output was deleted.
- **Cost.** 100 jobs. E10's wall times for the same cells sum to 6.6 CPU-h (C1_cf 0.67, C1_cf_edge 0.54, C3_rvo2_cf 2.85, C1_cf_sig 2.57). The longest single job is 20 min.

## D4. Censored longest gap (ruling: the final gap of an incomplete run is right-censored at 600 s) and flow ratios

c = max(longest interior gap, 600 s − last passage) for an incomplete run; a completed run is an event at its longest interior gap. The KM estimators are those of A12, and the ratio uses the log-ratio Welch t (fix_a7.ratio_means) with the corrected human flows.

| variant | completed: longest gap mean / max | censored (deadlock / capped) | open final gap to 600 s, mean [min, max] | median of c (lower bound) | KM median | KM restricted mean to τ (S(τ)) | flow ratio [95%] | matched [95%] |
|---|---|---|---|---|---|---|---|---|
| SFM | 6.8 / 6.8 s (1 run) | 24 (24 / 0) | 427 [404, 453] s | ≥ 425 s | not reached (> 453 s) | ≥ 435 s to 453 s (0.96) | 0.51 [0.43, 0.61] | 0.51 [0.43, 0.61] |
| SFM, B_w,edge | 6.3 / 10.5 s (17) | 8 (8 / 0) | 454 [430, 476] s | 6.5 s | 6.5 s | ≥ 156 s to 476 s (0.32) | 0.57 [0.48, 0.68] | 0.58 [0.50, 0.67] |
| force-coupled ORCA (RVO2) | 6.2 / 11.0 s (10) | 15 (0 / 15) | 444 [423, 468] s | ≥ 433 s | not reached (> 468 s) | ≥ 283 s to 468 s (0.60) | 0.59 [0.49, 0.70] | 0.59 [0.50, 0.71] |
| SFM + noise σ* | 56 / 269 s (14) | 11 (0 / 11) | 322 [2.4, 445] s | 96 s | 96 s | ≥ 226 s to 445 s (0.44) | 0.40 [0.33, 0.48] | 0.40 [0.34, 0.48] |
| humans | 1.7 / 2.04 s (5) | 0 | – | – | – | – | – | – |

- **Range.** The range of flow ratios stays at **0.40–0.59**: 0.4006 (noise) to 0.5900 (ORCA), against 0.3994–0.5882 with the uncorrected humans.
- **Force-coupled ORCA stalls (A12, kept).** The 15 force-coupled ORCA runs that are "still moving at 600 s" end with 2–4 agents jittering in place in front of the entrance. They pass no one in their last 423–468 s, so they are stalls, as with noise at σ*. Under the ruling they are censored in the same way as the deadlocked SFM runs.
- **What the ruling changes.** For deadlocked runs, censoring moves from the detector stop (A12: t_end, 10 s after rest) to 600 s. For the capped runs (ORCA, noise) it changes nothing, since t_end = 600 s already.

## Changed numbers (flag)

Against paper/numbers.tex (corrected humans, D2):
- EtenHumanFlow 1.48 → **1.47**; EtenHumanFlowLo 1.22 → **1.21**; EtenHumanFlowHi 1.74 → **1.73**; EtenShortHumanFlow 1.58 → **1.57**.
- FixAsevenHumanFlow/Lo/Hi: the same changes. FixAsevenHumanWindowFlow 1.49 → **1.48**; FixAsevenHumanWindowFlowLo 1.20 → **1.19**.
- FixAsevenCPubFlowRatioHi 0.58 → 0.59; FixAsevenCPubFiellerHi 0.59 → 0.60; FixAsevenCEdgeMatchedRatioLo 0.49 → 0.50; FixAsevenCSigMatchedRatioHi 0.47 → 0.48.
- Unchanged at display precision: every Eten*FlowRatio (E10 bootstrap), every FixAseven*FlowRatio and its Lo/Hi used in the text (0.51 [0.43, 0.61], 0.57, 0.59 [0.49, 0.70], 0.40 [0.33, 0.48]), the human gaps and fluctuation, and EtenHumanFlowMin/Max.

Against rev_A12.json (the 600 s ruling for deadlocked runs):
- RevAtwelveCOne: GapLowerMedian 16 → **425**, GapLowerMean 17 → **410**, GapKMRmean 32 → **435**, GapKMTau 33 → **453**, GapTermMean 18 → **427**.
- RevAtwelveCEdge: GapLowerMean 9 → **150**, GapKMRmean 10 → **156**, GapKMTau 17 → **476**, GapTermMean 15 → **454**.
- Unchanged: the CEdge median (6.5 s), every CThree and CSig value, and all A12 flow ratios.

Text that changes:
1. "\EtenHumanN\ entrance runs at a width of 0.8\,m ..., two with a 2.0\,m corridor behind the entrance and three with a 0.21\,m one": the length is **0.2 m**, a bottleneck length (Session B).
2. "matched agent number ... run by run": E10 matched the track-ID count, which is one too many for 4D040 and two too many for 4D110. Either reword (see draft) or rerun with D3.
3. "Every tracked participant passes the entrance (\EtenHumanUnpassed\ track is lost before it)": the lost track is a duplicate ID of a participant who passes.
4. Human flow 1.48 [1.22, 1.74] → 1.47 [1.21, 1.73]; short bottleneck 1.58 → 1.57.
5. The participant numbers of the archive (161, 160, 132, 132, 129) must not be quoted as the simulated N.

## Draft sentences

- "The archive lists 161, 160, 132, 132 and 129 participants for the five runs. The recordings contain 135, 135, 129, 129 and 128, and every recorded participant passes the entrance. Two duplicate track IDs in 4D110 and one in 4D040 were merged before counting."
- "Each model run has as many agents as participants passed the entrance in its human run, except 4D040 (+1) and 4D110 (+2), where E10 counted track IDs; the bottleneck is 2.0\,m or 0.2\,m long."
- "Humans pass at \RevDHumanFlow\ [\RevDHumanFlowLo, \RevDHumanFlowHi]\,ped/s. Across the four variants the model reaches \RevDRatioMin--\RevDRatioMax\ of the human flow."
- "We treat the final gap of an incomplete run as right-censored at the 600\,s horizon. The SFM completes \RevDCOneComplete\ run, and its \RevDCOneCens\ deadlocked runs leave the last gap open for \RevDCOneOpenMean\,s on average. SFM+ORCA (RVO2) ends \RevDCThreeCens\ runs with two to four agents jittering in front of the entrance, with no passage during the last \RevDCThreeOpenMean\,s. The completed runs of every deterministic variant have a longest gap of at most \RevDCThreeGapCompleteMax\,s, against at most \EtenHumanGapMax\,s in the humans."
