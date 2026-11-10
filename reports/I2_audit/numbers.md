# I2 audit: numbers

Scope: paper/sections/*.tex, paper/tables/*.tex, figures/fig1_caption.tex against paper/numbers.tex,
paper/registry/*.yaml and data/derived/*.json; velocity-coupling claims against
data/derived/velorca_analysis.json, reports/V_REPORT.md and code/sim; pair-library statements against data/E7b
and data/derived/E7_analysis.json. No paper, registry or table file was edited.

Classes: WRONG (false as written), IMPRECISE (true but misleading or not reproducible from what is printed),
OK-with-note.

## 1. Macro resolution

- numbers.tex defines 1332 macros: 1292 values plus 40 `...Unit` companions. The registry has 1292 entries,
  and they match the numbers.tex comment lines one to one (same file and key for every macro).
- The text uses 454 distinct numbers.tex macros (505 uses) in sections, tables and the Fig. 1 caption. Every
  one is defined. The only CamelCase control sequence not in numbers.tex is `\IfFileExists` (LaTeX kernel).
- paper/main.log (14:13) contains no "Undefined control sequence" and no LaTeX warnings. It predates
  numbers.tex and table3_matched.tex (14:14), so the paper was recompiled into a scratch directory from the
  current tree (pdflatex twice, TEXINPUTS=./llncs//). Result: 24 pages, no undefined control sequence, no
  LaTeX warning, no error.
- `tools/make_numbers.py` regenerated into a scratch file is byte-identical to paper/numbers.tex.
  `experiments/tables/make_table3.py` (main, output redirected) is byte-identical to
  paper/tables/table3_matched.tex.

Result: OK.

## 2. Macro values against sources

An independent checker parsed each `% Name <- file:key` comment, read the key from data/derived/<file>,
formatted it with the registry `fmt` (its own sci/p implementation, not make_numbers.py's), and compared the
result with the `\newcommand` body.

- 1292/1292 checked, **0 mismatches**, including all 76 velocity-coupling macros of velorca.yaml.
- Rounding notes, all consistent with the registry format and none affecting a claim:
  - `\VelWholeLo` and `\VelWholeSfmLo` print `0.00` for a Wilson lower bound of 0.0018. They are unused in
    the text. If they are ever quoted, use `{:.3f}` (0.002), as V_REPORT does.
  - `\FixAsevenCPubCompleteLo` prints `0.00` for 1.4e-17 (a float-noise zero). OK.
  - 59 integer-format macros round non-integers (e.g. `\PairFoldMissGap` 1.73 -> 2, used as "at most 2%",
    which stays true). Upper-bound phrasing ("at most", "below", "within", "up to") was scanned for values
    that round down past the bound. The only hits are `\FixAeightWcMed` 0.754 -> "below 0.75 m" and
    `\FixAeightWfiftyPred` 0.9196 -> "above 0.92 m" (05:20). Both statements stay true because the
    interval is narrowed, not widened. OK.

## 3. Velocity coupling (Sect. 6.4, Table 3, abstract, introduction, discussion, conclusions)

Data confirmed (velorca_analysis.json, data/velorca/*.jsonl):

- Lone trap: 60 snapshots x 6 runs = 360 per solver. 0/360 freed with RVO2 and 0/360 with legacy. 360/360
  identical to the SFM restart for each solver. 0/60 snapshots change outcome under replay for each solver.
  Force coupling frees 282 (RVO2) and 309 (legacy).
- Pair: 46 x 6 = 276 per solver. 0/276 freed with each solver, 276/276 identical for each, 0/46 replay
  changes for each. Force coupling frees 42 (RVO2) and 126 (legacy), which are 7x6 and 21x6 and consistent
  with Table 3's 7/46 and 21/46.
- Total quench runs: 1272/1272 bit-identical (360+360+276+276). Replays: 0 of 106 snapshots.
- "Six runs per snapshot" is correct: one unperturbed run plus five 1e-9 m replays (velorca.py,
  PREDICTION.md). `runs_per_snapshot = 6.0` in every arm; 360/60 = 276/46 = 6.
- Whole runs, seeds 242-341, RVO2: velocity coupling 1/100, SFM 1/100, force coupling 54/100. Force
  coupling's 54 matches E6 C3_rvo2 restricted to these seeds. Discordant seeds against force: 0:53, exact
  McNemar p = 2^-52 = 2.2e-16. All 99 failures are deadlocks at rest (0 moving at 600 s), and 99/99 are held
  by SFM (K0) and 99/99 by velocity coupling.
- "With either solver" holds for both solvers on every quench claim: freed, bit-identity and replay.

Eq. (velorca) against the code: **OK**. In simulation.py (numerics "fixed") the step is
`v' = clamp(v + F dt/m)`, then noise and clamp again, then `orca_velocity_filter`, then `x' = x + v' dt`.
hybrid.py drops the ORCA force when `orca_coupling == "velocity"` and applies
`v' + w_o (clamp(v_o) - v')` to active agents only, with `w_o = 1 - sigmoid(rho; 4, 2)`. orca.py
`filter_velocities` solves each agent's linear program with preferred velocity v'[i], half-planes from
`agent_state` (start-of-step x, v) and speed circle 2v0. This is the order in the text: noise step, then
Eq. (velorca) with Pi(O_i(v')), half-planes of the start of the step, then the position update.

| # | file:line | text | class | issue | proposed exact fix |
|---|---|---|---|---|---|
| V1 | paper/sections/06_screening.tex:59 | "Over the \VelWholeN\ seeds of Sect.~\ref{sec:att-whole}, \VelWholeK\ run completes, as under SFM (\VelWholeSfmK), against \VelWholeForceK\ under force coupling" | **WRONG** | Sect. 6.3 (att-whole) and Table 3 use \EsixN = 186 seeds (242-427, E6_analysis.json `seeds`). The velocity-coupling whole runs use only the first 100 (242-341). The force-coupling count 54 is for those 100 seeds; it is not ORCA (RVO2)'s 101/186 shown in Sect. 6.3. | "Over the first \VelWholeN\ of the \EsixN\ seeds of Sect.~\ref{sec:att-whole} (seeds 242--341), \VelWholeK\ run completes, as under SFM (\VelWholeSfmK; one discordant seed each way), against \VelWholeForceK\ under force coupling on the same seeds ($p=\VelWholeForceP$)" |
| V2 | paper/sections/06_screening.tex:59 | "\VelWholeK\ run completes, as under SFM (\VelWholeSfmK)" | IMPRECISE | The counts are equal, but the completing seeds differ (velocity: seed 255; SFM: seed 304; `whole.paired.vel_minus_sfm` only_first = only_second = 1). "As under SFM" reads as the same run. | Covered by the V1 fix ("one discordant seed each way"), or append "(\VelWholeOnlyVel:\VelWholeOnlySfm\ discordant)". |
| V3 | paper/tables/table3_matched.tex:31 (generated; edit make_table3.py) | whole runs row `\VelWholeK/\VelWholeN`, Δ `\VelWholeForceDiff` | IMPRECISE | The row sits after the block "Whole runs: \EsixN{} seeds", where ORCA (RVO2) is 101/186. Its Δ is taken from force coupling on seeds 242-341 (54/100). The reference row is not printed, so −0.53 cannot be read off the table. | In make_table3.py change the row label `r"whole runs"` to `r"whole runs, seeds 242--341"`, and in CAPTION after "whole-run rows count seeds" add "(velocity coupling: the first \VelWholeN{} seeds, force coupling there \VelWholeForceK{}/\VelWholeN{})". |
| V4 | paper/tables/table3_matched.tex:3, 29-30 (generated) | Replay column `\VelLoneReplayDis/\VelLoneSnaps` = 0/60 and `\VelPairReplayDis/\VelPairSnaps` = 0/46; caption "outcome changes in $10^{-9}$\,m replays (noise: snapshots whose seeds disagree)" | IMPRECISE | The other deterministic rows count replays (ORCA lone 0/170 = 34x5, pair 0/230 = 46x5). The velocity rows count snapshots whose six runs disagree, so the denominators differ in kind from the rows above and the caption does not cover them. | In make_table3.py CAPTION replace "(noise: snapshots whose seeds disagree)" with "(noise and velocity-coupling rows: snapshots whose runs disagree)". Alternatively, add replay-count keys to velorca analyze.py (300 and 230) with registry entries and print 0/300 and 0/230. |
| V5 | paper/tables/table3_matched.tex:29 | row label "lone-trap snapshots", 0/360 | OK-with-note | The 60 snapshots are 34 lone keystones plus 26 second-trap snapshots (204 + 156 runs). The lone block above is "34 lone keystones", so a reader may take 0/360 as the same stratum. Δ uses force coupling on all 360 (282/360). | Optional: label `r"lone-trap snapshots (\VelLoneSnaps{}, both classes)"`. |
| V6 | paper/sections/06_screening.tex:59 | "With either solver, velocity-coupled ORCA frees \VelLoneRvoK\ of \VelLoneN\ runs ... and \VelPairRvoK\ of \VelPairN" | OK-with-note | True (legacy is also 0/360 and 0/276), but the legacy value is not tied to its macro. If a rerun changed only the legacy arm, the text would not follow. | "velocity-coupled ORCA frees \VelLoneRvoK\ (RVO2) and \VelLonePubK\ (legacy) of \VelLoneN\ runs ..., and \VelPairRvoK\ and \VelPairPubK\ of \VelPairN\ ..." (or keep "with either solver" and accept the coupling). |
| V7 | paper/sections/06_screening.tex:59 | "Every quench repeats the SFM restart bit for bit, and no $10^{-9}$\,m replay changes an outcome." | OK-with-note | Verified for both solvers (1272/1272 identical; 0 replay changes in all four arms). The sentence has no macro. Registry macros exist for identity (\VelLoneIdentRvo etc.), but the legacy replay count has no registry entry (`lone.vel_pub.replay.snapshots_disagree` and `pair.vel_pub.replay.snapshots_disagree` are not registered). | Optional: register `VelLoneReplayDisPub` and `VelPairReplayDisPub`. The text can stay. |
| V8 | paper/sections/06_screening.tex:59 | "all \VelWholeFail\ failures end at rest, in states that SFM also holds" | OK-with-note | Verified: deadlock 99, moving 0, K0_all_held 99/99. The supporting macros \VelWholeDeadlock, \VelWholeMoving and \VelWholeHeldSfm are defined but not used. | Optional: "all \VelWholeFail\ failures end at rest (\VelWholeMoving\ moving at 600\,s), in states that SFM also holds (\VelWholeHeldSfm\ of \VelWholeFail)". |
| V9 | paper/sections/06_screening.tex:57 | "At a frozen deadlock the proposed velocity vanishes" | OK-with-note | Physically |v'| ≤ 4.0e-6 m/s (PREDICTION.md), not exactly 0. The argument needs only |v'| far below the slack (≥ 0.018 m/s). | Optional: "is at most $4\times10^{-6}$\,m/s". |
| V10 | 00_abstract.tex:3; 01_introduction.tex:18; 08_discussion.tex:15, 21; 09_conclusions.tex:2 | "frees no deadlock", "class P as predicted", "screened by quench, replay and whole runs only" | OK | Consistent with the data. The Δt probe was not run (`dtprobe.runs = 0`), which matches "quench, replay and whole runs only". The single extra whole-run completion (seed 255) comes from deadlock formation, not freeing, and is matched by SFM's discordant seed 304. | none |
| V11 | paper/sections/03_pedestrian_model.tex:42-46 | Eq. (velorca) and "after the noise step", "half-planes of the start of the step" | OK | Matches simulation.py / hybrid.py `orca_velocity_filter` / orca.py `filter_velocities` (see above). The linear program is also bounded by the 2v0 speed circle, so the Pi in Eq. (velorca) is redundant but harmless, as in the code. | none |

## 4. Pair library and Sect. 5.3

- All 64 snapshot pickles in data/E7b/library carry `B_w = 0.04` and no `B_w_edge`. e7b_lib.py uses
  `FLAGS = {**CF, "B_w": 0.04}`, and the e7b_lib.jsonl flags show `"B_w": 0.04`. The 46-snapshot library was
  therefore built with B_w = 0.04 m on every wall. **OK.**
- E7 cell `Bedge0.04` is `{"B_w_edge": 0.04}`, jamb only (experiments/E7/e7_cells.py:18), with
  collective 11 of 11 classified. `\EsevenBjambCollective` = 11 and `\EsevenBjambClassified` = 11. **OK.**

| # | file:line | text | class | issue | proposed exact fix |
|---|---|---|---|---|---|
| P1 | paper/sections/05_deadlock_physics.tex:48 | "The library holds \PairN\ such snapshots from independent runs under a short-range wall law, $B_w=0.04$\,m on every wall" | OK | Verified against the pickles and the generator. | none |
| P2 | paper/sections/05_deadlock_physics.tex:48 | "with the short range on the jambs alone, \EsevenBjambCollective\ of \EsevenBjambClassified\ deadlocks are pair or group standoffs" | OK-with-note | Correct (11/11). The library's own law (all walls, E7 cell `B0.04`) gives 14 of 15 collective plus 1 lone keystone, and that is the matching statistic for "under this law pairs dominate". Macros exist (\EsevenBallCollective, \EsevenBallClassified), so it could be cited alongside. | Optional: "under this law \EsevenBallCollective\ of \EsevenBallClassified\ E7 deadlocks are pair or group standoffs, and with the short range on the jambs alone \EsevenBjambCollective\ of \EsevenBjambClassified\ (Sect.~\ref{sec:lone})". |
| P3 | paper/sections/08_discussion.tex:21 | "The pair library was built under a short-range wall law ($B_w=0.04$\,m on every wall)" | OK | Verified. | none |
| P4 | paper/sections/05_deadlock_physics.tex:20; 07_experiments.tex:20,23 | $B_{w,\rm edge}$ used only for the jamb-only variant | OK | No remaining text attributes the pair library to $B_{w,\rm edge}$; the mismatch flagged in V_REPORT "Notes" is resolved. | none |

## 5. Literal numbers in text that are results, not design constants

Design constants (geometry, parameters, protocol thresholds, censoring times, figure display ranges such as
±150 N and 5-1000 N in the Fig. 1 caption) are excluded. Literal or verbal results:

| # | file:line | text | class | note / proposed fix |
|---|---|---|---|---|
| L1 | paper/sections/03_pedestrian_model.tex:16 | "$v_{{\rm eff},i}=v_{0,i}$ to within 1\%" | OK-with-note | Derived from \FinTermRhoMax = 0.32 via Weidmann: 1 − exp(−1.913(1/0.32 − 1/5.4)) = 0.9964, so it is within 0.4%. True as written. Could become a registry macro (e.g. FinTermVeffDev, `{:.1f}`) printing "0.4\%". |
| L2 | paper/sections/07_experiments.tex:12 | "two with a 2.0\,m corridor ... three with a 0.21\,m one ... in four runs kept a 2\,m semicircle" | OK-with-note | Dataset facts, not macros. 2 + 3 = \EtenHumanN = 5 is consistent with E10_analysis.json `humans.runs[].L`. |
| L3 | paper/sections/07_experiments.tex:12, 20 | "(25 per variant)", "deadlocks in \EtenCOneDeadlock\ of 25 runs" | OK-with-note | Sample size = 5 x \EtenHumanN. Prefer a macro for the denominator (E10 `cells.C1_cf.n`) so it tracks the data: "of \EtenCOneN\ runs". |
| L4 | paper/sections/04_protocol.tex:48 | "differs between agents by up to a factor of 1.5" | OK | Follows from τ ~ U(0.4, 0.6) s and m = 80 kg fixed (Table 1). Design-derived. |
| L5 | paper/sections/06_screening.tex:28 | "$\Delta t=0.005$\,s halves $\beta$ to 1.25" | OK | Arithmetic on the design value 2.5. |
| L6 | paper/tables/table3_matched.tex:23-26, 29-30 | "$>$120" in the $t_{1/2}$ column | OK-with-note | Result (KM median censored at 120 s). True for every row where it appears: freed < n/2 in all (22, 21, 8, 7 of 46; 0 of 360/276). Hard-coded in make_table3.py. |
| L7 | paper/tables/table3_matched.tex:25 | "[0, \FixAonePairRvoJHi]" | OK | Literal lower bound of J when J = 0 (\TabThreePairRvoJacFInt = 0). |
| L8 | paper/sections/05_deadlock_physics.tex:59 | "every run completes at $\Delta t=0.01$\,s", "none at 2\,m/s", "At the default drive none forms" | OK-with-note | Verbal results, verified (arch_analysis complete 25/25; N5 v2 episodes 0; default runs_with_arch 0). Unused macros exist for these (\ArchComplete, \RunNFiveDefaultRunsArch) and could replace the words, e.g. "every run completes (\ArchComplete\ of \ArchN)". |
| L9 | paper/sections/06_screening.tex:51 | "SFM and SFM+TTC free none of the \PairN\ standoffs" | OK-with-note | Verbal result, verified (E7b b_quench C1 0/46, C2 0/46). |
| L10 | paper/sections/06_screening.tex:55 | "the RVO2 solver and its surrogate share none of \PairBsRvoEither" | OK-with-note | Verified (J = 0, either 15). |
| L11 | paper/sections/06_screening.tex:38 | "Noise failures never come to rest" | OK-with-note | Verified (E6 C1_sigma stationary_deadlock 0 of 87). |
| L12 | paper/sections/06_screening.tex:57, 59 | "no pair is in contact", "Every quench ... bit for bit", "no ... replay changes an outcome", "all ... end at rest" | OK-with-note | See V7-V9. |

## Summary

- Macros: 1292 value macros (+40 unit macros) checked; 454 used in the text, all defined; 0 value mismatches;
  numbers.tex and table3_matched.tex regenerate byte-identically; fresh compile has no undefined control
  sequence.
- WRONG: 1 (V1, Sect. 6.4 "the 100 seeds of Sect. 6.3"; Sect. 6.3 has 186).
- IMPRECISE: 3 (V2 SFM completes a different seed; V3 Table 3 whole-run velocity row compared with a reference
  not shown; V4 Table 3 replay column counts snapshots, not replays, for the velocity rows).
- Velocity-coupling claims (0/360, 0/276 with both solvers; 1272 bit-identical quenches; 0 replay changes;
  1/100 vs 54/100; 99/99 failures at rest and held by SFM; six runs per snapshot) and Eq. (velorca) are
  correct. Pair-library statements (B_w = 0.04 m on all walls; 11 of 11 jamb-only) are correct.
