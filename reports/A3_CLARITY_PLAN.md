# A3: Clarity and readability plan for revision 5

Paper: "Mechanism Screening for Deadlock Resolution in a Social Force Model" (LNNS, 26 pages). Source audited:
`paper/` at origin/main `afbeed0` (paper files last changed in `df8ed37`; the build of this tree matches
`LNNS_final.pdf`, 26 pages). Nothing in `paper/` was edited. Line references are `file:line` inside `paper/sections/`
(or `paper/tables/`, `figures/`). Numbers quoted below are the rendered values of the `numbers.tex` macros; every
rewrite in Part 6 is written in LaTeX with the original macros, so the registry still drives every number.

Writing standard applied: the house prose standard (prose-craft SKILL.md, found under `~/.claude/skills/synced/`), read
in full. Venue: Springer LNNS (llncs class). Spelling: British, confirmed consistent (Part 7.3).

Contents
1. The fifteen highest-impact clarity problems, ranked
2. Per-section findings (reader test, undefined terms, structure)
3. Terminology map
4. Density audit and cut list, with page estimates
5. Table and figure plan, with replacement prose
6. Rewrites (LaTeX, ready to apply)
7. Lint results
8. FLAGS (claims stronger than the evidence, inconsistencies)
9. Inputs needed from the author
10. HANDOFF

---

## 1. The fifteen highest-impact clarity problems, ranked

Effort: S under 30 min, M 30 min to 2 h, L over 2 h (for P3, including rebuild and number check).

| # | Section | Problem | Remedy | Effort |
|---|---|---|---|---|
| 1 | 3.4 (`03_pedestrian_model.tex:64-65`) | One 110-word sentence with 21 numbers defines six snapshot sets; the next paragraph adds four seed ranges. The reader must rebuild the nesting (deadlock ⊃ screening ⊃ barrier ⊃ time-step, Arrhenius) and is told the separately built pair set is "nested". The relation of lone keystone and second trap to the lone trap is never stated. | Rewrite R1 (Part 6.6): definitions first, then one sentence per set, the pair set named as separate, one sentence linking lone keystone and second trap to the lone trap. Seeds and the PCG64 seed move to the framework (cut C2). | S |
| 2 | Abstract | 241 words, about 15 undefined terms (pair standoff, segment ends, jambs, rest drive, drive part, fraction-matched, probes, defect flag, replay, β, density throttle, CroMa, group standoff, velocity filter, computed barrier); no gap sentence; ends on a number, not a consequence. Sentence 6 carries two ideas and 41 words. | Rewrite (Part 6.1), 250 words by a count that splits units from numbers; every number and claim kept; ends on the paper's own recommendation. | S |
| 3 | 4.1 (`04_protocol.tex:5`) and Table 2 | One paragraph introduces 14 names (probe, Prevent, Reshape, Heat, axial and lateral subtype, b_f, β, T_eff, activated escape, defect flag, Glitch, replay sensitivity, rest-drive push, corrected-implementation probe); "rest-drive push" is used before its definition at the end of the same paragraph; the predictions sit in an 8-column table. | Three paragraphs: classes, probes, predicted responses (replaces Table 2). Rewrite in Part 6.4. | M |
| 4 | Sects. 3-6 order | Forward references: 3.3 → 5.4 (contact under-resolution), 3.4 → 4.4/4.5 (time-step probe, Eq. ell, accepted barrier, full condition), 4.1 → 4.3/4.4/5.3 (fixed point, T_eff, b_f), 4.4 → 4.5 (full/pinned/alone), 5.2 → 6.1 (matched noise level). The protocol is defined before the rest-state physics it is "derived from". | Reorder (Part 2.10): rest-state methods before results, protocol after the rest-state physics, the matched-noise β paragraph moved into the screening results. | M |
| 5 | 4.2, 6.1, 6.2 | Two notions of a match (difference not rejected; TOST equivalence) give eleven horizon values: 120, 600, 14, 161, 70, 85, 425, 89, 86, 545-600, 22-43 s. "Equality ... is not rejected only from a horizon on" (`04_protocol.tex:10`) is a double negative. | Define the match once; report the TOST windows (89, 86, 545-600, 22-43 s) in the text; move the not-rejected horizons (70, 85, 425 s) to the framework (cut C5). Rewrite R3. | S |
| 6 | Whole paper | "Force-coupled ORCA (RVO2)" appears about 45 times; the legacy solver has five names ("legacy solver", "legacy linear-program solver", "the authors' earlier solver", "ORCA code of [gang2026]", "corrected implementation" for its fix). | One convention sentence in Sect. 3.2: unqualified "force-coupled ORCA" uses the RVO2 solver; "(legacy)" marks the other. Map in Part 3. | S (mechanical) |
| 7 | 5.2 (`05_deadlock_physics.tex:41-42`) | One paragraph holds 59 numbers: medians, coverage counts, pooled slope, extended levels, three barriers with intervals, TST value, anharmonic prefactor, discretisation bias, Weibull shape, underdamping, Mel'nikov-Meshkov factor, attempt-frequency deficit. | Rewrite R6 in four paragraphs (test, result, why the slope is below 1, attempt frequency); second-order checks to the framework (cut C11). | M |
| 8 | 1 | The first paragraph never states the paper's claim; paragraphs 3-4 (`01_introduction.tex:13-14`) carry results (29/50, 3/200, 101/186, 5/300, 56 and 5 of 100, two p-values) and use TTC, RVO2, SFM and drive part before any definition. | Paragraph 1 ends on the central claim; paragraph 2 defines the rest states; the counts move to Sect. 6.2 (or stay, rewritten as R9). Rewrites in Parts 6.2 and 6.6. | S |
| 9 | Tables 2-5 | Table 3 has 10 columns, three-line cells and six footnotes; Tables 4 and 5 repeat a 7-column layout whose footnotes hold the Holm family sizes; a number (|ℓ| ≤ 0.018) appears only in a table footnote. | Delete Tables 2 and 3, merge 4 and 5 into one 4-column table; prose in Part 5. | M (generator edit) |
| 10 | Whole paper | Terminology drift: pair standoff / "pair or group standoff" / "group standoffs" for the same two snapshots; held / unfreed / trapped / unresolved; holding area / waiting zone; escape run / quench; matched / fraction-matched / tuned to the same completion fraction; drive / rest drive / "the drive's magnitude". | Canonical names in Part 3. | S |
| 11 | Whole paper | Abbreviations and symbols used before definition or never defined: CroMa (never expanded), TTC (Intro before Sect. 2), RVO2 (Intro), ROC (never), RMST (letters never expanded), β (abstract, Intro), T (Intro), χ (Eq. force, defined two equations later), quench (`03:16` before `03:64`), full/pinned/alone (`04:30` before `04:38`), "final-state class", "outcome identity", "one-neighbour snapshots", "Jacobian asymmetry", "spawned agents", "active agents". | Definitions table in Part 2.11, each one sentence built from existing text. | S |
| 12 | 4.1, 3.4, 6.1 | Process leakage: "(Glitch)" (`04:5`); "PCG64 seed 2026" (`03:64`); seed ranges 42-241, 42-141, 242-427, 900-904 (`03:65`); repository name, commit hashes, tag, file path and line number (`06_screening.tex:30`). | Move to the Data and Code Availability statement or the framework (cuts C1, C2); delete "(Glitch)". | S |
| 13 | 8 | The Discussion is two sentences plus Limitations, cites Tables 2 and 3 (to be deleted) and ends on a limitation ("extrapolates the Arrhenius law"). The throttle sentence repeats Sect. 3.1 almost word for word. | Limitations first, interpretation last; rewrite in Part 6.7. | S |
| 14 | Figs. 1 and 6 | Fig. 1 caption 140 words; Fig. 6 caption one 120-word sentence with nested parentheses. Fig. 7 uses "cluster-bootstrap", a term the Statistics section does not use. | Caption rewrites in Part 5.4. | S |
| 15 | 4.3, 6.1, 6.3, 6.4 | Unclear antecedents and elliptical clauses: "so the quench carries the evidence" (`04:15`); "√Δt-scaled noise does not" (`06:20`: does not what?); "with it fixed" (`06:18`); "this sets its defect flag" (`06:30`); "its freed set" (`06:52`); "they differ from those of +b*" (`06:52`); "Sect. 6.1 attributes them" (`01:14`); "frees it" / "its drive part" (abstract). | Name the noun in each case; fixed in the rewrites. | S |

Accuracy issues found while reading (not clarity, but P3 must not polish them into the text): see FLAGS F1 (lone release 1 m upstream), F2 (the two deadlock-set standoffs are pairs, called group standoffs at `05:18`), F3 (the 0.13 J snapshot), F4 (margin rule stated as exact with two exceptions).

---

## 2. Per-section findings

Reader test: an intelligent physicist outside crowd dynamics, reading once. "Takeaway" is what such a reader carries away now, in three sentences. Then: terms used before definition (with where the definition should go), places where more than five new names arrive at once, and structural findings.

### 2.1 Abstract (`00_abstract.tex:3`)

Takeaway. In one social force model at a 0.8 m door, deadlocks are of two kinds, one agent held by the door-edge wall force or agents abreast at sharp wall ends. Adding ORCA as a force frees the first kind by pushing harder towards the goal, while noise tuned to the same success rate frees deadlocks by random kicks, and saved-state tests can tell the two apart. The model passes about half the human flow in a matching experiment.

Undefined at use: pair standoff (only "needs sharp segment ends"), segment ends, jambs, group standoffs, rest drive, drive part, ORCA velocity filter, fraction-matched, lateral bias, probes, mechanism classes (unnamed), defect flag, replay, β, "Arrhenius slope ... of the computed barrier", CroMa, density throttle.

More than five names at once: sentences 6-9 introduce rest drive, drive part, τ′, velocity filter, fraction-matched noise, lateral bias, probes, deadlock-screen, three classes, defect flag, replay.

Structure: context (S1) present; gap absent; approach scattered (S2 and S9); results S3-S12; consequence absent (ends on the CroMa flow ratios). Sentence 6 repeats contribution 2 and the second sentence of the Conclusions nearly word for word. Rewrite: Part 6.1.

### 2.2 Introduction (`01_introduction.tex`)

Takeaway. Deadlock resolution in crowd models is credited to added steering terms, but a surrogate that reproduces the outcome does not show the mechanism. The paper names two deadlock types in one social force model and tests ORCA, noise and a lateral bias on saved deadlocks, extending the authors' earlier study with a corrected ORCA solver. The contributions list the rest-state physics, an identity for force-coupled ORCA, a screening protocol and a comparison with experiments.

Used before definition (line: term → where to define):
- L9 "default wall parameters", "terminal deadlocks" → define deadlock in L11 ("the last agents stop short of the door for good"); wall range is defined at `03:62`.
- L11 "jambs" → add "(the wall faces beside the door)".
- L13 "the identity of Eq. (identity)" → name it in words: "the identity that makes the drive part of force-coupled ORCA a shorter relaxation time".
- L13 "CroMa comparison" → see Part 2.11.
- L14 "RVO2 solver", "SFM" (defined here), "drive part", "TTC", "same spawns", "McNemar" → move the paragraph (Part 2.10) or define as in R9.
- L19 β and "Arrhenius slope ... of the computed barrier" → "β, the barrier in units of the noise temperature".
- L20 τ′ (defined in words, fine), "rest drive", "fraction-matched at T", "replay", "time to free", "whole-run final state", "handedness", "leg-normal" → define matched and T in paragraph 2; rest drive in contribution 2.
- L21 "defect flag", "corrected implementation" (defined in the item itself; fine).
- L22 "density throttle", "model variant".

More than five names at once: L11 (lone trap, blocker, pair standoff, members, group standoff, force-coupled ORCA, ORCA velocity filter, probes, surrogates, snapshots: ten); L13-14 (legacy solver, RVO2 solver, force-coupled ORCA (legacy), force-coupled ORCA (RVO2), SFM, TTC, drive part, CroMa: eight).

Structure: central claim missing from paragraph 1. Contributions against results, item by item:
- Item 1 (lone criterion and w50; rounded ends; activated escape) matches 5.1, 5.3, 5.2. It omits the wall-variant result that the abstract leads with (89 of 100 with the jamb range).
- Item 2 bundles six claims. "Time to free and the whole-run final state separate it empirically" holds at the lone keystones (ΔRMST, Holm p = 0.0016) and in whole runs (final-state class, Holm p = 0.0024), not at the second traps (ΔRMST p = 0.13): qualify (FLAG F11). The drive-part result at the second traps (149 against 121 of 160, `06:23`) is a main physics result and appears in no contribution.
- Item 3 matches Sects. 4 and 9.
- Item 4 matches Sect. 7.
- The whole-run stall prediction (`06:36`) is in no contribution; it can stay a secondary result.

### 2.3 Related Work (`02_related_work.tex`)

Takeaway. Social force, time-to-collision and ORCA models are standard; clogging at outlets is studied in grains and pedestrians, and activated-escape theory gives rates over barriers. Robots with control barrier functions deadlock at symmetric force balances. Pattern-oriented modelling asks for several patterns because one rarely discriminates mechanisms.

Findings: L12 states a result in related work ("the pair standoff (Sect. 5.3) is such an equilibrium"); move the clause to Sect. 5.3 or soften to a pointer. L15 "here the rival is a surrogate matched in freed fraction (Sect. 4.2), and the patterns are probe responses" is a forward reference doing the introduction's job; move to the introduction's paragraph 2. L9 (Grønbech-Jensen-Farago against BBK) is context for the Δt dependence of temperature; keep, since Eq. (teff) relies on the same point. "strong repulsion" (L3) is technical, not a defect.

### 2.4 Sect. 3 Pedestrian Model (`03_pedestrian_model.tex`)

Takeaway. Agents are discs driven towards a goal with social-force repulsion, optional time-to-collision forces and ORCA coupled as a force through a relaxation time. ORCA's force splits into a goal-directed drive part and a constraint part; the drive part alone turns the model into the same model with a shorter relaxation time and twice the forward force at rest. Deadlocks are saved and restarted under perturbations on six sets of snapshots.

Used before definition:
- L7 χ_i (Eq. force) → define after Eq. (force): "χ_i is the density gate of Eq. (orca)".
- L9 "active agents" → "agents that have not exited".
- L9 "switched at a snapshot" → snapshot is defined at L64; say "switched when a saved state is restarted".
- L16 w50 (defined in Intro; fine), "quench" (defined L64) → reorder (Part 2.10) or say "a restart of a saved deadlock (quench, Sect. 3.4)".
- L40 "binds" → "a constraint binds when the preferred velocity violates its half-plane".
- L53 "contact under-resolution at 5 m/s (Sect. 5.4)" → forward reference; move the sentence to 5.4 or to the cut subsection (C15).
- L64 "full ΔU" (full condition defined `04:38`), "accepted" barrier (`04:38`), "ΔU rank".
- L65 "time-step probe", 1/t_esc, λ, Eq. (ell) → all defined in 4.4; move the sentence there.

More than five names at once: L62 (door edge, segment end, jamb, wall range, jamb range, capsule r_c, line goal, holding area, convex junction: nine); L64 (deadlocked, snapshot, quench, horizon, freed, replay, keystone test, blocker, lone keystone, second trap, six sets: seventeen).

Structure: no opening paragraph (the section begins with Table 1 and a subsection). 3.2 ends on "for force-coupled ORCA it is the first term, 1.8-2.2 times that of SFM" with an unclear "it". The throttle sentence (L16) and Discussion L6 repeat each other.

### 2.5 Sect. 4 Screening Protocol and Methods (`04_protocol.tex`)

Takeaway. A perturbation is classed by the force it adds to an agent at rest: none (Prevent), deterministic (Reshape) or random (Heat), and probes (replay, time step, push, bias, solver swap) give each class a different response. A resolver and a surrogate are matched when they free the same fraction by a horizon T, and per-step noise has a temperature inversely proportional to the time step. Barriers come from the string method, and statistics are paired.

Used before definition: L5 fixed point (4.3), b_f (5.3), T_eff (4.4), rest-drive push (end of L5), corrected implementation; L12 "final-state class" (defined nowhere; used again `06:36`), Ω (L41, same section, acceptable); L30 "full-condition temperature", "pinned and alone conditions" (defined L38); L31 β0 (fine).

More than five names at once: L5 (fourteen, item 3 in Part 1); L38 (string, climbing image, images, full/pinned/alone, accepted, grid path, escape run, censoring, Weibull shape).

Structure: heading names two topics; 4.1-4.2 are protocol, 4.3-4.6 are methods. "so the quench carries the evidence" (L15) does not say evidence of what (that the SFM+TTC rest state is stable). The section opening is the class definition, which is the right first content once Table 2 is gone.

### 2.6 Sect. 5 Rest-State Physics (`05_deadlock_physics.tex`)

Takeaway. A lone agent at rest on the door axis is held when the peak backward door-edge force exceeds its drive; this criterion explains why half the runs complete at a 0.878 m door, and lowering the wall range turns lone traps into standoffs. With the blocker alone, noise frees it at the Arrhenius rate with a slope 0.85-0.93 of the computed barrier, as transition-state theory predicts for finite barriers. The pair standoff is a strict energy minimum that exists only at sharp wall ends and that a lateral bias removes past a threshold; contact arches form but never persist.

Used before definition: Fig. 4 caption (L6) "stuck-alone side" (defined L14); L14 "spawned agents" (the 20 000 agents drawn from the Table 1 distributions; never said); L18 "second traps" (defined in 3.4; fine); L20 "stuck-alone criterion" (= Eq. stuck; name it at L10); L41 "censoring-aware likelihood", "energy-diffusion factors", "transition-state rate", "prefactor"; L42 "barrier frequency"; L44 matched noise (Sect. 6.1, forward); L56 "converged runs" (= the Δt = 0.0025 and 0.001 s runs).

More than five names at once: L41-42 (slope ratio, censoring-aware fit, Kramers and energy-diffusion factors, transition-state rate, prefactor, harmonic value, Weibull shape, underdamped, barrier frequency, Mel'nikov-Meshkov factor, Langer prefactor).

Structure: no section opening. 5.2 paragraph L44 belongs to 6.1 (it needs the matched level). 5.4 (contact arches) answers a referee-type question (are these granular arches?) and links to Related Work; see cut C15.

### 2.7 Sect. 6 Screening Results (`06_screening.tex`)

Takeaway. Force-coupled ORCA frees the lone keystones through its drive part alone, exactly as the social force model with relaxation time τ′ does, and noise matched to it is separated by replay and by its time-step dependence; at second traps ORCA's constraint part works against its drive part. The ORCA solver of the earlier study has a sign error that makes outcomes depend on 10^-9 m perturbations and adds pair-standoff escapes that vanish when corrected. A matched lateral bias frees pair standoffs from a side it chooses, and ORCA as a velocity filter frees nothing.

Used before definition: L8 "cluster-bootstrap" (Statistics says "bootstrap over snapshots with all their seeds"); L14 ROC; L17 "five seeds" / "20 seeds" (noise seeds per snapshot); L23 "one-neighbour snapshots"; L36 "final-state classes", "failures at rest", "moving failures"; L48 "Jacobian asymmetry" (measure not defined); L51 b* (defined in the sentence; fine).

More than five names at once: L17-18 (two noise levels, two seed counts, TOST margin, 90% intervals, two horizons, Ω, halves of seeds, replay, noise stream); L36 (σ*, final-state class, failure at rest, moving failure, stall, survival function, barrier set, T_eff, attempt frequency, β).

Structure: Sect. 6 opens with Table 3 and no sentence. "Drive and Constraint Parts." is used as a run-in head in both 6.1 and 6.3 (acceptable, but "At the lone trap" / "At the pair standoff" would name them better). The class assignment, now only in Table 3, needs a paragraph (Part 5.3).

### 2.8 Sect. 7 Comparison with Experiments (`07_experiments.tex`)

Takeaway. In five human runs at a 0.8 m entrance nobody deadlocks, whereas the model, with untuned defaults, passes 0.40-0.60 of the human flow and leaves long gaps between passages. Removing the density reduction of walking speed raises the model flow to 0.48-0.72 of the human flow, so the throttle explains only part of the deficit. Model velocity fluctuations exceed the human ones.

Used before definition: "CroMa" (never expanded); "waiting zone" (L17; called "holding area" at `03:62`); "jamb range" variant (defined `03:62`; fine); 4D030 and the other run names (dataset identifiers; acceptable once).

Structure: the heading "Flow, Gaps and Velocity Fluctuation." joins three topics (rule 7); use "Flow and Passage Gaps." and keep fluctuation in the same paragraph. [NEW: CroMa time-step check] belongs at the end of the methods paragraph (L17).

### 2.9 Sects. 8-10 Discussion, Recommendations, Conclusions

Discussion takeaway. Three perturbations free the same fraction by three mechanisms; limitations concern the wall parameters, the coupling, the throttle, radius, temperature heterogeneity, Δt and the extrapolation below β = 1.5. Findings: ends on a limitation; cites Tables 2 and 3; repeats `03:16`. FLAG F5 on L3. Rewrite in Part 6.7.

Recommendations takeaway. Six checks for modellers: compare door-edge force with drive, round edges, report ORCA per solver and coupling, treat per-step noise as Δt-dependent temperature, test against experiments, report the throttle. Findings: item (ii) says "round door edges" where the paper's variant is "rounded segment ends"; use one name. Item (ii) is a comma splice inside a list item ("round ..., check the wall range"); write "round the segment ends at the door (r_c = 0.1 m prevents pair standoffs) and check the wall range".

Conclusions takeaway. Deadlocks are rest states set by wall parameters; ORCA frees the lone trap by its rest drive, matched noise by fluctuations; the model under-passes human flow; deadlock counts need mechanism probes and experiments. Findings: ends on the recommendation (correct); sentence 2 repeats the abstract and contribution 2; optional rewrite in Part 6.7.

### 2.10 Proposed order of Sects. 3-7

Current order forces forward references (item 4 in Part 1). Proposed order, physics first, protocol after the physics it is built from:

1. Introduction; 2. Related Work (unchanged).
3. Pedestrian Model (unchanged content; move `03:65` sentences on the time-step probe and the velocity-filter quench counts into new Sect. 4 and Sect. 6).
4. **Rest States, Noise Temperature and Barriers** (methods): old 4.3 Rest States and Their Stability, 4.5 Barriers from the String Method (moved before 4.4 so full/pinned/alone are defined before use), 4.4 Effective Temperature of Per-Step Noise, 4.6 Statistics.
5. Rest-State Physics (unchanged; `05:44` moved to 6.3).
6. **Screening Protocol**: old 4.1 Mechanism Classes (with the Table 2 prose), 4.2 Fraction Matching and Separation, Fig. 3.
7. Screening Results: old 6.1-6.4, the matched-noise β paragraph from `05:44`, the Table 3 prose, a final class-assignment paragraph (Part 5.3).
8. Comparison with Experiments; 9. Discussion; 10. Recommendations; 11. Conclusions.

This order adds one section number (11 sections). If the author prefers to keep ten, merge the new Sects. 6 and 7 as "Screening Protocol and Results" with 6.1-6.2 protocol and 6.3-6.6 results. Labels stay; only `\section` lines and the moved paragraphs change. Cost of not reordering: the forward references listed in Part 1, item 4.

### 2.11 Definitions to add (one sentence each, built from existing text)

| Term | First use | Define at | Proposed definition |
|---|---|---|---|
| CroMa | abstract; `01:13` | `01:13` and `07:11` | "the CroMa bottleneck experiments~\cite{fzj_ped20219,boomers2023data}, five laboratory runs through a 0.8\,m entrance" (expansion of the acronym: Part 9, Q1) |
| RVO2 | `01:14` | `01:14` | "the RVO2 solver, a line-by-line port of the RVO2 library (Sect.~\ref{sec:identity})" |
| TTC | `01:14` | `01:14` | "the time-to-collision (TTC) force of Eq.~\eqref{eq:ttc}" |
| ROC | `06:14` | `06:14` | "with area 0.98 under the receiver-operating-characteristic (ROC) curve" |
| RMST | `04:41` | `04:41` | "times to free compared by their restricted mean up to $T$ (RMST)" |
| PCG64 | `03:64` | move to framework | delete from prose (cut C2) |
| LP | not used in the text | none | "legacy linear-program solver" never abbreviated; keep it so |
| β | abstract; `01:19` | `01:19` and `04:5` | "β, the barrier ΔU in units of the noise temperature $k_{\rm B}T_{\rm eff}$" |
| ΔU | `02:9` | fine | barrier, defined in Related Work |
| T_eff | `04:5` | `04:5` | add "(Eq.~\eqref{eq:teff})" at first use |
| w50 | `01:19` | fine | defined in contribution 1 |
| g_max | `05:10` | fine | "peak door-edge force" in Intro; symbol at `05:10` |
| χ | `03:7` | after Eq. (force) | "$\chi_i$ is the density gate of Eq.~\eqref{eq:orca}" |
| τ, τ′ | `03:5`, `03:43` | fine | |
| T (horizon) | `01:20` | `01:11` | "matched: freeing the same fraction of snapshots by a horizon $T$" |
| quench | `03:16` | `01:11` or `03:16` | "a quench restarts a snapshot under one perturbation" (from `03:64`) |
| replay | `01:20` | `01:11` | "a replay repeats a quench from coordinates displaced by $10^{-9}$\,m" |
| rest drive | abstract; `01:20` | contribution 2 | "the rest drive, the goal-directed force on an agent at rest" (from `03:45`) |
| drive part | `01:14` | `01:14` | "the drive part, the goal-directed part of the ORCA force" |
| stuck alone | Fig. 1 caption | Fig. 1 caption | "stuck-alone margin (peak door-edge force minus drive, Sect.~\ref{sec:lone})" |
| jamb, segment end | abstract; `01:11` | `01:11` | "the jambs, the wall faces beside the door, end in sharp segment ends" |
| density throttle | `01:22` | `01:22` | "the density throttle, Weidmann's reduction of desired speed with density (Eq.~\eqref{eq:des})" |
| full / pinned / alone | `04:30` | reorder (2.10) or `04:30` | "full: all residual agents mobile; pinned: neighbours fixed; alone: the blocker only" (from `04:38`) |
| final-state class | `04:12`, `06:36` | `04:12` | "the state of a failed run at 600\,s: at rest or moving, and the keystone class of the held blocker" (confirm: Part 9, Q9) |
| outcome identity | Table 4 note | merged-table note | ask the author (Part 9, Q9) |
| one-neighbour snapshots | `06:23` | `06:23` | "snapshots with one agent besides the blocker" |
| Jacobian asymmetry | `06:48` | `06:48` | ask the author for the measure (Part 9, Q10) |
| spawned agents | `05:14` | `05:14` | "20\,000 agents drawn from the distributions of Table~\ref{tab:params}" |
| active agents | `03:9` | `03:9` | "agents that have not exited" |
| waiting zone | `03:62` ("holding area") | `03:62` | use "waiting zone" in both places |
| cluster bootstrap | Fig. 7 caption | caption | "bootstrap over snapshots" as in Sect. 4.6 |
| escape run | `04:38` | `04:38` | "a quench of the Arrhenius or time-step set" (or drop the term and say quench) |

### 2.12 Snapshot sets and horizons (the two items the referee named)

Sets, as they should read (R1 in Part 6.6): deadlock set 196 (of 200 runs) ⊃ screening set 60 (34 lone keystones + 26 second traps) ⊃ barrier set 56 ⊃ {time-step set 20, Arrhenius set 10}; the pair set (46) is built separately with B_w = 0.04 m on every wall. The current text calls all six "nested" (`03:64`); the pair set is not.

Horizons in the text: 120 s (quench), 600 s (whole run), 14 s and 161 s (last ORCA success), 70 / 85 / 425 s (difference not rejected from), 89 / 86 s and 545-600 s (TOST-equivalent from / within), 22-43 s (second-trap TOST window), 60 s (lone release), 300 s and 900 s (escape censoring), 10 s (deadlock and stop criteria). Proposal: name 120 and 600 s once as the horizons, state the 10 s criteria once, keep 14, 161, 89, 86, 545-600 and 22-43 s in the text, move 70, 85 and 425 s to the framework (C5). The reader then holds two horizons and one kind of match.

---

## 3. Terminology map

Canonical name first; variants found (with an example line) after the arrow. P3 replaces every variant by the canonical name unless the note says otherwise.

1. **deadlock** (a run whose speeds all stay below 0.01 m/s for 10 s without an exit) ← "terminal deadlocks" (`01:9`), "clogs" and "gridlocks" (cited usage, keep in citations only). Define at first use in the Introduction.
2. **rest state** ← "fixed point" (`04:5`, `04:15`, `06:14`), "equilibrium" (`05:10`), "minimum" (`05:47`, for the energy minimum). Keep "fixed point" once in the definition at `04:15`; "strict minimum" only for the property of U.
3. **lone trap** (blocker held at rest by the door-edge force alone) ← "lone traps" (Table 3 row head, meaning lone keystones), "lone-trap quenches" (`06:55`). Lone keystones and second traps are both lone traps: say so once (R1).
4. **lone keystone**, **second trap** (classes from the keystone test) — consistent.
5. **blocker** ← "lone agent" (`01:19`, different object: a single agent released in the release test; keep "a lone agent" there and define it).
6. **standoff** (umbrella) → **pair standoff** (two members), **group standoff** (more) ← "pair or group standoff(s)" (abstract, `05:22`, Fig. 5), "group standoffs" for the two pair standoffs of the deadlock set (`05:18`, an error: FLAG F2), "collective" (registry only). Use "standoff" for the umbrella everywhere.
7. **member** (of a standoff) ← "partner" (`06:48`, the other member; keep "partner" only in "the half-plane against the partner").
8. **stuck alone** (static criterion, Eq. stuck) / **held** (quench outcome) ← "trapped neighbour" (`06:23`, use "held neighbour"), "unfreed" (`06:48`, use "held"), "unresolved" (keep only for the sets in Ω).
9. **stuck-alone margin** ← "margin", "positive margin" (fine after definition), "margin-zero lines" (Fig. 4: "zero-margin lines").
10. **drive** (F^des) ← "the agent's own drive" (Fig. 1), "the drive's magnitude" (`06:48`: means the drive part's? state which).
11. **rest drive** (total goal-directed force at v = 0) ← "goal-directed force at rest" (gloss, keep once), "SFM rest drive" (fine).
12. **drive part** / **constraint part** ← "constraint parts" (Fig. 7, fine as plural).
13. **push** (rest-drive push, ±) ← "Push ±" (tables), "pushed towards the door, the rest drive frees" (`06:14`, reads as if the rest drive is pushed; write "the push towards the door frees").
14. **lateral bias b**; matched value **b\*** ← "bias", "matched lateral bias", "fraction-matched lateral bias", "reversed bias" (= −b*, keep with the symbol).
15. **per-step noise**, **√Δt-scaled noise** ← "velocity noise" (`01:11`), "noise surrogate" (`01:13`), "SFM + noise σ*" (Table 6), "SFM with noise σ*" (`07:14`). Two matched levels: "matched noise (σ = 0.07 m/s)" at the quenches and "matched noise σ*" in whole runs; say which every time (Part 9, Q3).
16. **matched** (freeing the same fraction by horizon T) ← "fraction-matched" (abstract, `04:9`, headings), "fraction matching", "matched in freed fraction" (`02:15`), "tuned to the same completion fraction" (`01:9`, the earlier study's wording; keep there). Define "matched" once; drop "fraction-" elsewhere, including the heading "Fraction Matching and Separation" → "Matching and Separation".
17. **freed fraction** (quenches) / **completed fraction** (whole runs) ← "completion fraction" (`01:9`), "completion" (`06:33`).
18. **force-coupled ORCA** (RVO2 solver by convention) / **force-coupled ORCA (legacy)** ← "force-coupled ORCA (RVO2)" (about 45 times), "force-coupled ORCA with the RVO2 solver" (`06:14`), "ORCA" alone for the model variant (`01:9` "ORCA's velocity selection" refers to the earlier study, keep).
19. **legacy solver** ← "legacy linear-program solver" (`01:13`, `03:34`: keep once at definition), "the authors' earlier solver" (abstract), "ORCA code of [gang2026]" (`06:30`).
20. **RVO2 solver** ← "RVO2" (bare, `06:26`), "corrected implementation" (keep only as the probe's name: "the corrected-implementation probe swaps the legacy for the RVO2 solver").
21. **ORCA velocity filter** ← "the filter" (fine after definition), "velocity filter".
22. **SFM**, **SFM+TTC**, **SFM with τ′** ← "the SFM with τ′" (`06:14`, drop "the"), "the social force model alone (SFM)" (definition, keep).
23. **snapshot** (saved deadlock) ← "saved rest states" (`01:11`, gloss), "saved state" (`03:64`).
24. **quench** ← "restart" (C3 language, not in paper), "escape run" (`04:38`), "quenched" (verb, fine).
25. **replay** ← "10^-9 m replay", "replay flips" (`06:30`), "replay changes".
26. **replay sensitivity** ← "replay-sensitive" (fine), "outcome sensitivity" (abstract).
27. **defect flag** ← "Glitch" (`04:5`, delete), "flag" (Table 3, fine).
28. **time to free** (t_esc) ← "escape time" (`04:38`, `05:41`), "exit time", "mean time to free" (Table 4). Use "time to free" for every quench, "escape rate" for λ.
29. **door edge** (= the segment end at the door) / **jamb** (wall face beside it) ← "segment end", "sharp ends" (`01:19`, `05:47`), "jamb segment end" (`05:51`), "rounded end", "capsule". Variant names: "rounded segment ends (r_c = 0.1 m)" everywhere, including Recommendation (ii) ("round door edges").
30. **wall range B_w** / **jamb range B_{w,edge}** ← "default walls", "default wall parameters", "default-wall", "short wall range" (`08:6`, means 0.04 m: give the value).
31. **waiting zone** ← "holding area" (`03:62`).
32. **CroMa entrance** ← "CroMa bottleneck" (the experiment), "0.8 m bottleneck", "the bottleneck" (also the 0.2/2.0 m corridor). Write "entrance" for the 0.8 m opening and "corridor" for the 0.2 or 2.0 m passage behind it.
33. **slope ratio** ← "Arrhenius slope over −ΔU" (definition), "Arrhenius slope ... of the computed barrier" (abstract, contributions; fine as gloss).
34. **condition: full / pinned / alone** ← "frozen" (registry only), "with the blocker alone" (keystone test and alone condition: same geometry; fine).
35. **β** ← "β_ref" (C3 only), "β0" (set value at Δt = 0.01 s; keep).
36. **horizon T** ← "120 s horizon" (Fig. 9 "600 s horizon": fine).
37. **overlap Ω** ← "Jaccard index" (definition), "overlap".
38. **final-state class** ← "failure classes" (C3), "final-state classes" (`06:36`). Define (Part 2.11).
39. **probe** ← "quench variant" (definition), "test" (`04:12`, "paired test" is statistical; fine).
40. **resolver**, **surrogate** — consistent.
41. **Prevent / Reshape (axial, lateral) / Heat** — consistent; keep capitals.
42. **density throttle** ← "density-dependent speed reduction" (abstract rewrite gloss), "v_eff = v_0" (shorthand for throttle off; fine).
43. **density gate χ** ← "the gate" (fine).
44. **whole run** ← "run", "room run", "evacuation", "spawn seed" (as a unit: "on another 100 spawn seeds", fine).
45. **stall** (at least 10 s without an exit, whole runs) — defined at `06:36`; keep.

---

## 4. Density audit and cut list

### 4.1 Counts

Numerical values per section (macro-expanded source, numbers inside math counted, section and equation numbers excluded): abstract 18, Introduction 36, Related Work 1, Sect. 3 107, Sect. 4 72, Sect. 5 231, Sect. 6 183, Sect. 7 56, Discussion 15, Recommendations 1, Conclusions 12; tables and captions about 20 more. The densest paragraphs: `05:41` (59), `03:64` (51), `06:51-52` (32), `05:47` (29), `06:17-18` (26), `06:48` (24).

82 sentences carry more than three numbers. Decision codes: (a) keep: an abstract, conclusion or Sect. 9 claim depends on it, or the reader needs it for the argument; (b) move to the released data and framework with a pointer; (c) delete; (r) relocate within the paper.

| Line, sentence | n | Code | Reason (one line) |
|---|---|---|---|
| abstract s5, s6, s12 | 5, 4, 4 | a | abstract claims |
| `01:14` s2 | 7 | r | result against the earlier study; to Sect. 6.2 (or R9 if kept) |
| `01:14` s3 | 4 | r | whole-run counts; to 6.2, with [NEW: whole-run attribution] |
| `01:14` s4 | 5 | r | TTC null result; to 6.2 |
| `01:19` s2, `01:20` s1, `01:22` | 4 each | a | contributions match results |
| `03:16` s1 | 5 | a | model definition |
| `03:16` s2 | 6 | a | throttle-off counts support the Discussion limitation; split into two sentences |
| `03:62` s1 | 11 | a | geometry; split in two |
| `03:64` s2 | 5 | a | quench definition |
| `03:64` s5 | 21 | a/b | set sizes kept (R1); "PCG64 seed 2026" (b) |
| `03:65` s1 | 6 | b | seed ranges to framework |
| `03:65` s3 | 4 | a | deadlock-set composition |
| `03:65` s4 | 4 | b/a | "seeds 42-141" (b); "both pair standoffs among its 98 deadlocks" (a) |
| `04:9` s3 | 4 | a | defines the ±0.10 margin |
| `04:10` s3 | 5 | b | not-rejected horizons 70, 85, 425 s (C5) |
| `04:31` s1 | 10 | a | design of the time-step probe; split |
| `04:38` s2 | 4 | b | image counts (C3) |
| `04:38` s3 | 5 | b | acceptance thresholds (C3); keep "All 4 rejected strings are second traps" |
| `04:38` s5 | 6 | a | censoring times needed for the escape fits; split |
| `05:10` s1 | 6 | a | g_max(r) values carry the radius dependence used in the Discussion |
| `05:14` s3 | 5 | a | SFM rest drive against g_max: the lone-trap mechanism |
| `05:15` s1 | 9 | b (partly) | keep 0.081 [0.077, 0.085] for the radius limitation; move factor 0.73 and the ORCA values (C9) |
| `05:18` s1 | 6 | a | release test; FLAG F1 |
| `05:18` s2 | 4 | a | keystone composition; FLAG F2 |
| `05:18` s4 | 4 | a | arrival order supports the w50 argument |
| `05:20` s1 | 7 | a | w50, a conclusion number |
| `05:20` s2 | 8 | b (partly) | keep w50 without throttle; move 37/29 and p = 0.39 (C17) |
| `05:22` s1, s2 | 5, 7 | a | wall variants; 89 is an abstract number |
| `05:39` s2 | 5 | a | Arrhenius design |
| `05:41` s2 | 10 | a | coverage counts support "activated escape"; FLAG F3 |
| `05:41` s4 | 6 | a | extended levels |
| `05:41` s5 | 17 | a | 0.85-0.93 is in the abstract and conclusions; split by barrier |
| `05:41` s10 | 5 | b | Weibull over-dispersion (C11) |
| `05:44` s1 | 8 | r | matched-noise β supports "by fluctuations" (abstract); move to Sect. 6.1 |
| `05:47` s1 | 5 | a | overhang defines the rounding rule |
| `05:47` s2 | 9 | a | 0/320 against 46/320 is a contribution |
| `05:47` s3 | 8 | a (shortened) | rule check; list of six radii compressed to "six radii from 0.001 to 0.1 m" (C14) |
| `05:47` s4 | 7 | b | line-goal standoff count, not used elsewhere |
| `05:49` s3 | 6 | b | Hessian stiffness ranges (C4); keep "softest mode is the common lateral shift" |
| `05:51` s3 | 10 | a (shortened) | static rule agreement 363/368 supports the bias mechanism; list of b values (b) |
| `05:53` s1 | 8 | a | standoff barriers explain why no Arrhenius test; split |
| `05:56` s2, s4, s6 | 4 each | b | contact-arch detail (C15) |
| `06:14` s2 | 6 | a | SFM with τ′ test of the identity |
| `06:14` s4 | 5 | a | push result; FLAG F5 depends on it |
| `06:17` s1 | 4 | a | matched levels |
| `06:17` s2 | 10 | a/c | keep 90% intervals and horizons; delete TOST p-values (implied by the intervals) (C5) |
| `06:18` s1 | 5 | a/b | keep 3 of 4; move "mean of 1.5 snapshots" (b) |
| `06:18` s3 | 5 | a | replay separation (abstract) |
| `06:20` s1 | 4 | a | time-step separation (abstract) |
| `06:23` s2 | 8 | a/c | drive part 149 against ORCA 121 kept; Holm p = 1.0 in parentheses (c) |
| `06:23` s4 | 8 | a/b | Δ kept; window 22-43 s (b) |
| `06:30` s3 | 5 | a | legacy replay sensitivity (abstract) |
| `06:30` s4 | 4 | b | jitter speeds and drift (C7) |
| `06:33` s1 | 5 | a | σ50 and σ* (σ* used in Sect. 7) |
| `06:34` s1 | 7 | a | whole-run equivalence window (Discussion limitation) |
| `06:36` s6 | 5 | a | supports "by fluctuations" in whole runs |
| `06:48` s1 | 10 | a | solver difference sets the defect flag; split |
| `06:51` s2 | 9 | b | split-validation ranges (C8); keep the two median errors |
| `06:51` s4 | 10 | a/c | Δ = +0.022 kept; Holm p = 1.0 twice (c); TOST p (c) |
| `06:52` s3, s4 | 4, 4 | a | handedness separation (contribution 2) |
| `06:55` s2, s3 | 4, 6 | a | velocity filter frees none (abstract) |
| `07:15` s2 | 4 | a | agent size against shoulder width explains part of the flow deficit |
| `07:21` s1 | 4 | a | window ratio shows the deficit is not a tail effect |
| `07:21` s2 | 5 | a | human baseline |
| `07:21` s3 | 6 | b | per-corridor-length ratios (C12) |
| `07:21` s5 | 5 | a | human gaps; Recommendation (v) |
| `07:23` s2, s3 | 4, 5 | a | gaps (Recommendation v); fluctuation (Fig. 9) |
| `08:6` s1, `08:9`, `08:10` s2 | 4 each | a | limitations |
| `09:2` s2, s4 | 4 each | a | conclusions |

### 4.2 Cut candidates, ranked from least to most costly

Lines are LNNS text lines (about 40 per page).

| # | Cut | Where | Saves | What it loses |
|---|---|---|---|---|
| C1 | Repository, commit hashes, tag, file path and source line of the defect | `06:30` → Data and Code Availability | 3 lines | in-text traceability (kept in the archive) |
| C2 | "PCG64 seed 2026"; seed ranges 42-241, 42-141, 242-427, 900-904 | `03:64-65` → framework | 3 lines | seed bookkeeping in the text |
| C3 | String acceptance thresholds (31/62/124 images, 5 N, 1%, 0.01 N, 2 cm, 2%) | `04:38` → framework, keep "four convergence tests" | 3 lines | the thresholds in print |
| C4 | Hessian and Jacobian ranges (≥66 N/m; μ1 65-120 N/m, median 94; 12-14×; asymmetry 0.077-0.10) | `04:21`, `05:49`, `06:48` | 2 lines | stiffness scale of the minima |
| C5 | Not-rejected horizons 70, 85, 425 s; TOST p-values beside the 90% intervals; Holm p = 1.0 in parentheses | `04:10`, `06:17`, `06:23`, `06:34`, `06:51` | 3 lines | the weaker-test horizons; p-values that the intervals already imply |
| C6 | Temperature-weighting check (0.91-1.2, median 1.0) or the realised-variance check (1.0) | `04:30-31` | 2 lines | one of two consistency checks of Eq. (teff) |
| C7 | Legacy jitter (0.091-0.14 m/s, drift −0.14 to +3.3 mm/s); keep "4 of 5 first divergences at a sign flip" and "up to 81 s" | `06:30` | 1 line | the jitter amplitude |
| C8 | Bias split-validation ranges (−0.29 to 0.30, −0.30 to 0.30, −0.19 to 0.40) | `06:51` | 2 lines | the evidence that the spread equals sampling spread (keep one clause: "splitting alone gives the same spread") |
| C9 | Mean-radius check: factor 0.73, ORCA 0.0016 and 0.013 | `05:15` | 1.5 lines | quantitative radius sensitivity under ORCA |
| C10 | Throttle-off discordance 37/29, p = 0.39 (C17 in the table above) | `05:20` | 1 line | paired evidence that the throttle does not move w50 |
| C11 | Arrhenius second-order checks: Δt bias 0.0079-0.0085, prefactor 0.63, Weibull 0.66, and `05:42` reduced to two sentences (fitted attempt frequencies 0.69 of the damped Langer prediction; causes untested) | `05:41-42` | 6 lines | the underdamping diagnosis (0.41, 4.5 ΔU, 0.79, 0.97, 28 fits); a Kramers-turnover reader will look for it |
| C12 | CroMa per-corridor ratios (0.54/0.62, 0.48/0.58) and normal-motivation ratio (0.45-0.68) | `07:21` | 3 lines | evidence that neither corridor length nor motivation explains the deficit |
| C13 | Line-goal standoff count (91/320, p < 10^-4) | `05:47` | 1 line | that a line goal doubles standoffs |
| C14 | List of six radii | `05:47` | 0.5 line | none (range kept) |
| C15 | Contact arches (5.4) compressed to three sentences: no static friction at rest; at converged Δt arches form in every run and break within 2.4 s, none of 20 holds 10 s; at Δt = 0.01 s none forms. Compression forces and overlaps to the framework; `03:53` moves here. | `05:56`, `03:53` | 5 lines (12 if deleted) | full deletion loses the answer to "are these frictional arches like granular clogs?" and the link to `02:6`; compression loses the force magnitudes |
| C16 | Fig. 3 (protocol diagram) | Sect. 4.2 | 0.3 page | the one visual summary of the protocol; not recommended |

Recommended set: C1-C15 with C15 compressed (not deleted): about 37 lines, 0.9 page. C16 only if the page cap binds.

### 4.3 Page budget

| Change | Pages |
|---|---|
| Delete Tables 2 and 3 | −0.83 |
| Prose replacing them (Part 5.1-5.3; most of Table 3 is already in the text) | +0.75 |
| Merge Tables 4 and 5 (0.67 → about 0.33) | −0.34 |
| Prose for the dropped columns (Part 5.4; 60 of 230 words replace existing text) | +0.35 |
| Cuts C1-C15 (C15 compressed) | −0.9 |
| Remove duplication (Discussion L6 vs `03:16`; Discussion L3; conclusions sentence 2; Intro paragraph 4 relocated, not cut) | −0.2 |
| Rewrites split long sentences (about +5% on rewritten passages) | +0.3 |
| Net before new material | about −0.9 (26 → about 25) |
| New material from other sessions ([NEW] items in Part 6, five slots of two to four sentences) | +0.4 to +0.7 |
| Expected final | about 25-25.5 pages |

The target of 24-26 is met; the hard cap of 28 is not at risk. To reach 24, add C16 and delete C15 entirely (−0.6 page) and accept the losses stated above. The table plan by itself is page-neutral: its benefit is readability, and the page saving comes from the density cuts.

---

## 5. Table and figure plan

Final table set: Table 1 (parameters, unchanged), new Table 2 (merged matched comparisons), Table 3 (old Table 6, CroMa outcomes, unchanged). Tables 4 and 5 are generated by `experiments/tables/make_tables45.py`; P3 edits the generator, not the `.tex`.

### 5.1 Replacement prose for Table 2 (predicted responses)

Placed in Sect. 4.1 (or new Sect. 6.1 under the reorder). Full LaTeX in Part 6.4 (paragraphs 2 and 3). Content check against Table 2, cell by cell: Prevent: quench held†, replay held†, Δt held† both scalings, push no change†, bias no change†, first exit n.a., persists. Reshape axial: frees, identical, flat; flat, + frees − not, bias n.a., unhanded, persists. Reshape lateral: frees past b_f, identical, flat; flat, push n.a., both signs free past b_f, side of b†, persists. Heat: frees with exponential times at β ≥ 1.5, seeds disagree†, falls†; flat†, push and bias n.a., unhanded, persists. Defect flag: as its class, vanishes†. Replay sensitivity: as its class, replay changes†. Every cell is in the prose.

### 5.2 Replacement prose for Table 3 (observed responses)

Most of Table 3 is already in Sect. 6. The numbers that exist only in Table 3 are |ℓ| ≤ 0.018 per snapshot, pair replays 0/230, bias 22/46 and its first-exit counts 22/22 and 21/21. The paragraphs below place every Table 3 number in the section where its result is discussed.

At the start of 6.1, after the opening sentence of R-Sect.6 (Part 6.5):

```latex
At the \EtwoNLK\ lone keystones force-coupled ORCA frees \EtwoLKCThreeRVOFreed\ with either solver
(\EtwoLKCThreePubFreed\ of \EtwoLKCThreeRVON\ legacy). With the RVO2 solver its replays change no outcome
(\TabThreeLKRvoReplayDis\ of \TabThreeLKRvoReplays), its time-step response is flat
($|\ell|\le\EthreeCThreeLnRatioMax$ per snapshot) and the push frees \EtwoLKFrozenPlusFreed\ towards the door and
\EtwoLKFrozenMinusFreed\ away. The legacy solver frees the same lone keystones, but its replays change the outcome in
\RevAfiveXPoolLegacyReplayChanged\ of \RevAfiveXPoolLegacyReplays\ replays at the \RevAfiveXPoolN\ second traps; these
changes vanish with the RVO2 solver and the freed set does not.
```

In 6.1 "Fraction-Matched Noise", the noise row (seeds disagree 9/34, ℓ = 2.2 at β0 = 1.5, flat under √Δt scaling) is covered by R4 (Part 6.6) and the merged-table prose (5.4).

In 6.4 (velocity filter), the existing `06:55` already gives 0/360; add: "Its replays are identical, and its outcome is the same with either solver."

In 6.3 "Drive and Constraint Parts" (R7 covers 21/46, 7/46, p, 34 and 1); add after the McNemar sentence:

```latex
Replays change no outcome with either solver (\TabThreePairRvoReplayDis\ and \TabThreePairPubReplayDis\ of
\TabThreePairOrcaReplays).
```

In 6.3 "Fraction-Matched Lateral Bias" (R10 covers 11/21, 2/7, 21, 13:14); add:

```latex
With the legacy solver the bias $+b^\ast$ frees \PairBsPubFreed\ of the \PairN\ standoffs, and its replays change none
(\TabThreePairBsPubReplayDis\ of \TabThreePairBsReplays). The member on the side favoured by the sign of $b$ exits
first in all \PairBsPubHand\ standoffs that $+b^\ast$ frees and all \PairBsPubMinusUpper\ that $-b^\ast$ frees.
```

The legacy defect flag (Table 3 note c: 21 freed fall to 7, McNemar p < 10^-3) is in R5 and R7.

### 5.3 Class-assignment paragraph

New last subsection of Sect. 6 ("6.5 Assigned Classes"; under the reorder, last subsection of new Sect. 7):

```latex
\subsection{Assigned Classes}\label{sec:classes}
The probe responses assign each perturbation to one class. Force-coupled ORCA frees deterministically with either
solver and at both rest states: its replays are identical, its freed set does not change with $\Delta t$, and the push
frees towards the door and not away. It is an axial Reshape mechanism, and it acts through its rest drive. Its freed
count at the pair standoff depends on the solver because the constraint part opposes the drive part. Per-step noise
frees with seeds that disagree and with an escape rate that falls as $\Delta t$ grows, as Eq.~\eqref{eq:ell}
predicts; it is a Heat mechanism. The lateral bias frees past $b_f$ with either sign, and the member on its favoured
side exits first; it is a lateral Reshape mechanism. The ORCA velocity filter frees no snapshot and is at most a
Prevent mechanism. The legacy solver adds replay sensitivity at the lone trap and, at the pair standoff, freed
standoffs that vanish in the corrected implementation; it carries the defect flag.
```

Every statement is in Table 3 (class column, notes c and e) or in `06:14`, `06:20`, `06:30`, `06:48`.

### 5.4 Merged table (old Tables 4 and 5) and prose for the dropped columns

Layout (four columns, booktabs, `\scriptsize` as now):

```latex
\begin{table}[t]
\caption{Matched surrogates against force-coupled ORCA: freed fraction at the horizon $T$ and the paired difference.}
\label{tab:matched}
\centering\scriptsize\setlength{\tabcolsep}{4pt}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llcc@{}}
\toprule
Set & Perturbation & Freed & $\Delta$ [95\%] \\
\midrule
Lone keystones (\EtwoNLK, $T=120$\,s) & noise $\sigma=0.07$\,m/s, 5 seeds & \EtwoLKNoiseCFreed/\EtwoLKNoiseCN & $\RvAfiveLoneEtwoDiff$ [$\RvAfiveLoneEtwoDiffLo$, $\RvAfiveLoneEtwoDiffHi$] \\
 & noise $\sigma=\RunNOneSigma$\,m/s, 20 seeds & \RunNOneFreed/\RunNOneRunsN & $\RvAfiveLoneNoneDiff$ [$\RvAfiveLoneNoneDiffLo$, $\RvAfiveLoneNoneDiffHi$] \\
 & force-coupled ORCA & \EtwoLKCThreeRVOFreed/\EtwoLKCThreeRVON & \\
Second traps (\RevAsixSTSnaps, $T=120$\,s) & noise $\sigma=0.07$\,m/s, 5 seeds & \RevAsixSTNoiseFreed/\RevAsixSTNoiseN & $\RvAfiveSecondEtwoDiff$ [$\RvAfiveSecondEtwoDiffLo$, $\RvAfiveSecondEtwoDiffHi$] \\
 & force-coupled ORCA & \RevAsixSTOrcaFreed/\RevAsixSTOrcaN & \\
Whole runs (\EsixN\ seeds, $T=600$\,s) & noise $\sigma^\ast=\EsixSigmaStar$\,m/s & \EsixNoiseK/\EsixN & $\RvAfiveWholeDiff$ [$\RvAfiveWholeDiffLo$, $\RvAfiveWholeDiffHi$] \\
 & force-coupled ORCA & \EsixCThreeK/\EsixN & \\
Pair standoffs, legacy (\PairN, $T=120$\,s) & bias $+b^\ast=\PscrPairBstarPub$ & \PairBsPubFreed/\PairN & $\RvAfivePairLegacyDiff$ [$\RvAfivePairLegacyDiffLo$, $\RvAfivePairLegacyDiffHi$] \\
 & force-coupled ORCA (legacy) & \PairPubFreed/\PairN & \\
Pair standoffs, RVO2 (\PairN, $T=120$\,s) & bias $+b^\ast=\PairBstarRvo$ & \PairBsRvoFreed/\PairN & $\RvAfivePairRvoDiff$ [$\RvAfivePairRvoDiffLo$, $\RvAfivePairRvoDiffHi$] \\
 & force-coupled ORCA & \PairRvoFreed/\PairN & \\
\bottomrule
\end{tabular*}
\par\smallskip
\parbox{\textwidth}{\scriptsize Freed: noise quenches freed by $T$ (snapshots times seeds), snapshots freed (force-coupled
ORCA, bias), runs completed (whole runs). $\Delta$: freed fraction of the surrogate minus that of force-coupled ORCA,
unadjusted 95\% interval.}
\end{table}
```

Prose for the dropped columns (ΔRMST, replay, Ω, ℓ, first exit, Holm p beside Δ). Lone keystones go into 6.1 after R4; second traps into "Second Traps."; whole runs into 6.2 (replacing the Ω clause of `06:33`); pair standoffs into 6.3 after R10; Holm families into 4.6 (Statistics).

```latex
% 6.1, after the replay and time-step sentences (lone keystones)
None of the matched differences in Table~\ref{tab:matched} is significant (Holm $p\RevAsevenLoneEtwoFreedPHolmRel$ and
$p\RevAsevenLoneNoneFreedPHolmRel$). Noise frees later: its restricted mean time to free exceeds that of force-coupled
ORCA by $\PscrTimeLoneEtwoEff$\,s [$\PscrTimeLoneEtwoLo$, $\PscrTimeLoneEtwoHi$] with five seeds (Holm
$p\RevAsevenLoneEtwoTimePHolmRel$) and $\PscrTimeLoneNoneEff$\,s [$\PscrTimeLoneNoneLo$, $\PscrTimeLoneNoneHi$] with
20 seeds ($p\RevAsevenLoneNoneTimePHolmRel$). Noise seeds disagree at \TabThreeLKNoiseDisagree\ of
\TabThreeLKNoiseSnaps\ snapshots with five seeds and \RevAsevenLoneNoneReplayDiscA\ of \EtwoNLK\ with 20; replays of
force-coupled ORCA change \TabThreeLKRvoReplayDis\ of \TabThreeLKRvoReplays. The unresolved sets of the 20-seed noise
and force-coupled ORCA overlap with $\Omega=\RevAnineLKNHalfJ$, against \PscrLKNHalfEJ\ for independent sets
($p\RevAnineLKNHalfPRel$). Over the \EthreeN\ time-step-set snapshots the pooled $\ell$ is \PprotEllBA\ under noise at
$\beta_0=1.5$, as predicted (\PprotEllBAPred), and $\PscrOrcaLnRatio$ under force-coupled ORCA (Holm
$p\RevAsevenLoneEtwoEllPHolmRel$).

% 6.1, Second Traps
At the \RevAsixSTSnaps\ screening-set second traps noise frees \RevAsixSTNoiseFreed\ of \RevAsixSTNoiseN\ quenches and
force-coupled ORCA \RevAsixSTOrcaFreed\ of \RevAsixSTOrcaN\ snapshots (Table~\ref{tab:matched}; Holm
$p\RevAsevenSecondFreedPHolmRel$). The restricted mean times to free differ by $\PscrTimeSecondEff$\,s
[$\PscrTimeSecondLo$, $\PscrTimeSecondHi$] ($p\RevAsevenSecondTimePHolmRel$). Noise seeds disagree at
\RevAsixSTNoiseDisagree\ of \RevAsixSTSnaps\ snapshots, replays of force-coupled ORCA change \RevAsixSTOrcaReplayDis\
of \RevAsixSTOrcaReplays, and the unresolved sets overlap with $\Omega=\RevAsixSTJ$ against \RevAsixSTJInd\ for
independent sets ($p=\RevAsixSTJIndP$).

% 6.2, replaces the Omega clause of 06:33
Noise completes as many runs as force-coupled ORCA (Table~\ref{tab:matched}; Holm $p\RevAsevenWholeEsixFreedPHolmRel$)
but $\PscrTimeWholeEff$\,s [$\PscrTimeWholeLo$, $\PscrTimeWholeHi$] later in restricted mean
($p\RevAsevenWholeEsixTimePHolmRel$). Their unresolved sets overlap more than independent sets ($\Omega=\RevAnineWholeEJ$
against \RevAnineWholeEEJ, hypergeometric $p\RevAnineWholeEPRel$).

% 6.3, after R10 (pair standoffs)
With either solver the bias and force-coupled ORCA do not differ in freed fraction (Holm
$p\RevAsevenPairPubFreedPHolmRel$ legacy, $p\RevAsevenPairRvoFreedPHolmRel$ RVO2) or in restricted mean time to free
($\PscrTimePairPubEff$\,s [$\PscrTimePairPubLo$, $\PscrTimePairPubHi$], $p\RevAsevenPairPubTimePHolmRel$;
$\PscrTimePairRvoEff$\,s [$\PscrTimePairRvoLo$, $\PscrTimePairRvoHi$], $p\RevAsevenPairRvoTimePHolmRel$). Replays of
the bias change \TabThreePairBsPubReplayDis\ and \TabThreePairBsRvoReplayDis\ of \TabThreePairBsReplays. The freed sets
overlap with $\Omega=\RevAninePairPubJ$ against \RevAninePairPubEJ\ for independent sets (legacy,
$p\RevAninePairPubPRel$) and $\Omega=\RevAninePairRvoJ$ against \PscrPairRvoEJ\ (RVO2; $p\RevAninePairRvoPLeRel$ for
an overlap this small or smaller). The member below the axis exits first in all \PairBsPubHand\ standoffs that the
bias frees with the legacy solver (Holm $p\RevAsevenPairPubHandPHolmRel$) and all \TabThreePairRvoHand\ with the RVO2
solver ($p\RevAsevenPairRvoHandPHolmRel$), against \PairPubLower\ of \TabThreePairPubOrcaN\ and
\TabThreePairRvoOrcaLower\ of \TabThreePairRvoOrcaN\ under force-coupled ORCA.

% 4.6 Statistics, new last sentence
Holm families: lone keystones, four probes (freed fraction, replay, restricted mean time to free, and $\ell$ or outcome
identity); second traps, three; whole runs, four (freed fraction, outcome identity, restricted mean time to free,
final-state class); pair standoffs, five per solver (freed fraction, replay, outcome identity, restricted mean time to
free, first exit).
```

Note: the bias row says "the member below the axis exits first in all ... standoffs"; the macros `\PairBsPubHand` and `\TabThreePairRvoHand` equal the freed counts (22, 8), so "all" matches. P3 should confirm that the Holm p of the RVO2 handedness test (0.028) is the macro `\RevAsevenPairRvoHandPHolmRel`, as in Table 5.

### 5.5 Captions: rule check and changes

| Item | Sentences / words | Finding | Change |
|---|---|---|---|
| Fig. 1 (`figures/fig1_caption.tex`) | 3 / 140 | too long; "stuck-alone margin" used before definition; no reading guide | Rewrite below (about 100 words; the hero carries many encodings, so 60 is not reachable without moving encodings into the figure, which the rule forbids). Author decision, Part 9 Q6. |
| Fig. 2 geometry (`03:59`) | 2 / 45 | fine | none |
| Fig. 3 protocol (`04:8`) | 1 / 40 | repeats the body's definition of the defect flag | "Screening protocol. Snapshots (1) are probed (2); the responses (3) assign a class and the defect flag (4), and the resolver is compared with its matched surrogate on the same snapshots (5)." |
| Fig. 4 lone trap (`05:6`) | 2 / 85 | "margin-zero lines" → "zero-margin lines"; "lone agent on the axis" → "agent at rest on the door axis" | Rewrite below |
| Fig. 5 width (`05:27`) | 2 / 60 | fine; "pair or group standoff" → "standoff" | term only |
| Fig. 6 escape (`05:35`) | 1 / 120 | one sentence, nested parentheses | Rewrite below (3 sentences) |
| Fig. 7 quench (`06:8`) | 2 / 55 | "cluster-bootstrap" not the Statistics term; result statement "free no lone keystone (not shown)" is in the body | "95% bootstrap intervals over snapshots"; "Not shown: perturbations that free no lone keystone (Sect. 6.1)." |
| Fig. 8 pair (`06:42`) | 2 / 55 | fine | none |
| Fig. 9 CroMa (`07:5`) | 2 / 55 | "waiting-zone" is the canonical term; fine | none |
| Table 1 | 2 / 15 | fine | none |
| Merged table | 1 / 18 | new | as in 5.4 |
| Table 6 (→ 3) | 1 / 12 | fine | none |

Number only in a caption: "|ℓ| ≤ 0.018 per snapshot" (Table 3 note a) moves to the text (5.2). "2000 of 20 000" (Fig. 4) is a plotting subsample, an encoding; keep. Fig. 1 colour-scale values (−150, +150, 5, 1000 N) are encodings; keep.

Fig. 1:

```latex
Lone trap (top) and pair standoff (bottom). Left: agents shaded by stuck-alone margin, the peak door-edge force minus
the drive (navy $-150$\,N to light grey $+150$\,N), and the floor by the backward wall force on a 0.25\,m agent
(off-white 5\,N to dark purple 1000\,N, log scale); arrows share one force scale (black, own drive; grey, neighbours'
push; blue, drive part of the ORCA term; dark purple, wall and partner). Right: rest-state energy relative to the rest
state (black marker) along the door axis or the members' common lateral shift, without and with the rest-drive push
or the lateral bias (grey marker where the biased curve leads); the vermilion band is $k_{\mathrm{B}}T_{\mathrm{eff}}$
of per-step noise $\sigma=0.07$\,m/s at $\Delta t=0.01$\,s.
```

(P3 must confirm the agents are in the left panels; the current caption says "Right:" for the energy curves only.)

Fig. 4:

```latex
Left: backward door-edge force on an agent at rest on the door axis against its distance to the door plane, for
$r=0.20$ (dotted), 0.25 (dash-dot), 0.30 (dashed) and 0.35\,m (solid); bands, 5th--95th percentile rest drives of
spawned agents for SFM (grey) and force-coupled ORCA (hatched), with medians as lines (\DriveCOneMedian\ and
\PphysDriveTotal\,N). Right: 2000 of \StuckAloneN\ spawned agents over $(r,v_0/\tau)$ with the zero-margin lines of
SFM (black; stuck-alone side shaded) and force-coupled ORCA (blue; upper line $\tau=0.4$\,s, lower 0.6\,s).
```

Fig. 6:

```latex
Escape of the blocker from the lone trap under noise, in the full (circles), pinned (squares) and alone (triangles)
conditions; black, the alone condition at $\beta=5$--7 and fits over $\beta=1.5$--7; $\beta=\Delta U_{\rm
cond}/k_{\rm B}T_{\rm eff}$ with $\Delta U_{\rm cond}$ the barrier in each condition. (a) Fitted escape rate over the
fitted attempt frequency against $\beta$ (line, slope $-1$); (b) slope ratio $-s/\Delta U_{\rm cond}$, $s$ the
Arrhenius slope, with 95\% intervals (dashed line, transition-state prediction \RvAthreeTheoryRatio). (c) Escape rate
relative to $\Delta t=0.01$\,s, pooled over snapshots, under per-step noise (filled; circles $\beta_0=1.5$, squares
$\beta_0=2.5$; lines, prediction) and $\sqrt{\Delta t}$-scaled noise (open), and inverse time to free under
force-coupled ORCA (diamonds).
```

### 5.6 Is every figure necessary?

Fig. 1 (hero): yes, it carries both rest states and the energy picture the referee asked to see. Fig. 2 (geometry): yes; the CroMa layout cannot be described in words in less space. Fig. 3 (protocol): keep; once Table 2 is gone it is the only visual summary of the protocol (C16 if the page cap binds). Fig. 4 (lone trap): yes, the criterion. Fig. 5 (width, walls): yes, w50 and the wall variants. Fig. 6 (escape): yes. Fig. 7 (quench): the left panel duplicates counts in the text; the right panel shows the time course behind ΔRMST; keep both panels. Fig. 8 (pair): yes, bias threshold against quench. Fig. 9 (CroMa): yes; it overlaps Table 6 only in the gap column.

---

## 6. Rewrites (LaTeX, ready to apply)

Rules followed: every number is the original macro; no claim is strengthened or weakened (sentences under a FLAG keep their strength and carry a `% FLAG Fn` comment); citations unchanged; equations unchanged. `[NEW: ...]` marks where numbers from the running sessions go; no such number is invented here.

### 6.1 Abstract (250 words, units counted as separate words; old version 241)

```latex
Steering terms added to crowd models are credited, on outcome alone, with clearing deadlocks at narrow doors. In one
social force model (wall range 0.08\,m) at a 0.8\,m door, two rest states hold the last agents. In the lone trap the
door-edge wall force alone holds one agent, the blocker. Standoffs of agents abreast need sharp wall-segment ends:
with wall range 0.04\,m beside the door, \EsevenBjambK\ of \EsevenN\ runs complete and \EsevenBjambCollective\ of
\EsevenBjambClassified\ deadlocks are standoffs. Optimal reciprocal collision avoidance coupled as a force
(force-coupled ORCA) frees the lone trap through its goal-directed part, giving relaxation time
$\tau'=\RevAoneTauPrimeLo$--$\RevAoneTauPrimeHi$\,s and \RevAoneDriveRatioLo--\RevAoneDriveRatioHi\ times the
goal-directed force at rest. As a velocity filter, ORCA frees none. Noise matched in freed fraction frees deadlocks by
fluctuations; a matched lateral bias tilts the pair standoff out of its minimum. Probes of saved deadlocks (open
framework deadlock-screen) assign three mechanism classes and a defect flag; replay and time step separate noise from
force-coupled ORCA. With the blocker alone, noise frees it by activated escape at barriers of 1.5 noise temperatures
or more, with Arrhenius slope \RvAthreeRatioDeep--\RvAthreeRatioMid\ of the computed barrier, the finite-barrier
transition-state value. The authors' earlier ORCA solver has a sign defect that makes outcomes replay-sensitive. In
five CroMa experiments at this width no participant deadlocks; with uncalibrated defaults the model passes
\RevDThreeRatioMin--\RevDThreeRatioMax\ of human flow, \RvBoneCroOffMin--\RvBoneCroOffMax\ without its
density-dependent speed reduction. A deadlock count describes crowds only after probes name its mechanism and
experiments test flow and passage gaps.
```

Optional: `[NEW: whole-run completions with the drive part alone, if the author wants the whole-run attribution in the abstract; it costs about 15 words, so another clause must go.]`

Check against the old abstract: wall range 0.08 m, 0.8 m door, two rest states, lone trap and blocker, sharp segment ends, 0.04 m result with 89/100 and 11/11, rest-drive mechanism with τ′ and 1.8-2.2, velocity filter frees none, matched noise by fluctuations, matched bias tilts the pair standoff, probes in deadlock-screen with three classes and a defect flag, replay and time step separate, activated escape with the blocker alone at β ≥ 1.5 and slope 0.85-0.93 at the finite-barrier TST value, earlier solver's replay sensitivity from a sign defect, five CroMa runs with no deadlock, 0.40-0.60 and 0.48-0.72. The final sentence is the Conclusions' recommendation. "Standoffs" covers pair and group standoffs; "the pair standoff" names the two-member case.

### 6.2 Introduction, paragraphs 1 and 2

```latex
At a 0.8\,m door, a social force model with default wall parameters leaves its last agents in terminal deadlocks:
they stop short of the door and never move again. Resolution of these deadlocks is credited to the steering term a
model adds. The authors' earlier study~\cite{gang2026} credited optimal reciprocal collision avoidance
(ORCA)~\cite{vandenberg2011} with the evacuations its configurations completed, and found noise tuned to the same
completion fraction indistinguishable from ORCA's velocity selection. Others credit fewer deadlocks or gridlocks to a
detour term in a social force model~\cite{qu2018}, an anticipation term in a velocity model~\cite{xu2021anticipation}
and turning and lateral steps in a cellular automaton at a bottleneck~\cite{fu2019}. A surrogate tuned to the same
outcome shows only that a cause of another kind suffices: under equifinality many mechanisms reproduce one
observable~\cite{beven2006}. Calibrated crowd models still differ in collision avoidance~\cite{wolinski2014parameter},
so credits need not transfer. We derive, from the physics of the rest states that hold the last agents, probes that
separate mechanisms which free the same fraction, and find that ORCA coupled as a force frees the lone trap through
its goal-directed force at rest, whereas matched noise frees deadlocks by fluctuations.

We study one social force model~\cite{helbing1995,helbing2000nature} at a 0.8\,m evacuation door
(Fig.~\ref{fig:hero}). Two rest states hold the last agents. In the \emph{lone trap} the agent nearest the door, the
\emph{blocker}, is held at rest by the wall force of the door edges alone. In the \emph{pair standoff} two agents, the
\emph{members}, are held abreast before the \emph{jambs}, the wall faces beside the door; with more members it is a
\emph{group standoff}. ORCA enters either as a force (\emph{force-coupled ORCA}) or as a velocity filter (the
\emph{ORCA velocity filter}). Each deadlock is saved as a \emph{snapshot} and restarted under one perturbation, a
\emph{quench}. Probes derived from the rest-state physics (Sect.~\ref{sec:signatures}) quench the same snapshots with
force-coupled ORCA and with two surrogates, velocity noise and a lateral bias of the walking direction. A surrogate is
\emph{matched} to force-coupled ORCA when it frees the same fraction of snapshots by a horizon $T$.
```

Notes: the last sentence of paragraph 1 is the central claim, built from the abstract and contribution 2 (no new claim). The definition of deadlock ("stop short of the door and never move again") paraphrases `03:64` (speeds below 0.01 m/s for 10 s); if the author prefers the operational wording, write "they come to rest before the door". Paragraph 2 now holds ten names, but each gets its own sentence or clause.

### 6.3 Contributions list

```latex
\subsubsection{Contributions.}
For this social force model (Table~\ref{tab:params}):
\begin{itemize}
\item A lone agent released at rest on the door axis is held when the peak backward force of the door edges exceeds
its drive, and the bracket this criterion gives over the spawned radii and speeds is consistent with the critical
width $w_{50}=\RevBtwoWfifty$\,m at which half the runs complete (Sect.~\ref{sec:lone}). The pair standoff needs sharp
segment ends: with rounded ends ($r_c=0.1$\,m) it forms in none of \RevBfiveGenN\ runs, against \RevBfiveGenPairRef\ of
\RevBfiveGenN\ with sharp ends (Sect.~\ref{sec:pair}). With the blocker alone, noise at $\beta\ge1.5$, where $\beta$ is
the barrier in units of the noise temperature, frees it by activated escape with an Arrhenius slope
\RvAthreeRatioDeep--\RvAthreeRatioMid\ of the computed barrier (Sect.~\ref{sec:escape}).
\item The drive plus the drive part of force-coupled ORCA, its goal-directed part, is the social force model with
relaxation time $\tau'=\RevAoneTauPrimeLo$--$\RevAoneTauPrimeHi$\,s and \RevAoneDriveRatioLo--\RevAoneDriveRatioHi\
times the rest drive, the goal-directed force at rest; this rest drive frees the lone trap
(Sects.~\ref{sec:identity} and~\ref{sec:att-lone}) [NEW: whole-run completions with the drive part alone and with
the social force model at $\tau'$, against force-coupled ORCA, Sect.~\ref{sec:att-whole}]. The ORCA velocity filter
adds no rest drive and frees none (Sect.~\ref{sec:velorca}). The legacy solver of~\cite{gang2026} has a sign defect
in its leg normals, Eq.~\eqref{eq:legnormal}, that makes its outcomes replay-sensitive (Sect.~\ref{sec:att-lone}).
\item Matched noise frees deadlocks by fluctuations. Replay and the time step separate it from force-coupled ORCA by
construction, and time to free and the whole-run final state separate it empirically; handedness separates the
lateral bias (Sects.~\ref{sec:att-lone}--\ref{sec:att-pair}). % FLAG F11
\item A screening protocol, implemented in the open framework deadlock-screen, assigns a resolution claim to one of
three mechanism classes from the probe responses of snapshots, and sets a defect flag when outcomes it produces vanish
in a corrected implementation (Sects.~\ref{sec:signatures} and~\ref{sec:recommend}).
\item In the CroMa bottleneck experiments~\cite{fzj_ped20219,boomers2023data} every model variant with uncalibrated
defaults passes \RevDThreeRatioMin--\RevDThreeRatioMax\ of the human flow over whole runs, and
\RvBoneCroOffMin--\RvBoneCroOffMax\ without the density throttle (Sect.~\ref{sec:validity}).
\end{itemize}
```

Change from the current list: contribution 2 is split into a mechanism item and a separation item, so each item makes one kind of claim and maps to one set of sections. "Adds no rest drive" restates `06:55`. If the author wants the second-trap result in the contributions, add to item 2: "At the second traps the constraint part opposes the drive part, so force-coupled ORCA frees \RevAfiveXPoolOrcaFreed\ of \RevAfiveXPoolN\ blockers where its drive part alone frees \RevAfiveXPoolDriveFreed."

### 6.4 Section openings

**Sect. 3 (new opening paragraph, before 3.1):**

```latex
The model moves each pedestrian as a disc under a goal-directed drive, exponential and contact forces from other
agents and from walls, and two optional steering terms: a time-to-collision force and ORCA coupled as a force
(Table~\ref{tab:params}). Every term can be switched on or off when a saved state is restarted, so the force each term
exerts on agents at rest can be measured on its own.
```

Add after Eq. (force), in the sentence at `03:9`: "with $\chi_i$ the density gate of Eq.~\eqref{eq:orca}, $j$ over the other active agents (those not yet exited) within $R=3$\,m". Add at the end of `03:34` (convention): "Unless marked (legacy), force-coupled ORCA uses the RVO2 solver."

**Sect. 4 opening (4.1, replaces `04_protocol.tex:5` and Table 2):**

```latex
\subsection{Mechanism Classes}
A perturbation can free a deadlock in three ways, told apart by the force it adds to an agent at rest. A
\emph{Prevent} mechanism adds none: it acts only while the crowd moves, changes how often deadlocks form and leaves a
snapshot held. A \emph{Reshape} mechanism adds a deterministic force that moves or removes the rest state
(Sect.~\ref{sec:rest}). A \emph{Heat} mechanism adds a random force of zero mean and carries the state over a barrier
$\Delta U$ by fluctuations. Activated escape, at the Kramers rate set by $\beta=\Delta U/k_{\mathrm{B}}T_{\mathrm{eff}}$
(Eq.~\eqref{eq:teff}), is the high-barrier limit of Heat, tested here at $\beta\ge1.5$. The three forces exclude each
other, and so do the classes. Reshape has two subtypes: an axial one is goal-directed, as force-coupled ORCA is, and a
lateral one is handed, as the lateral bias is, and removes a strict minimum once $|b|$ exceeds a threshold $b_f$
(Sect.~\ref{sec:pair}).

A \emph{probe} is a quench variant to which the classes respond differently. A replay displaces every coordinate by
$10^{-9}$\,m. The time-step probe repeats a quench at other $\Delta t$ with per-step or $\sqrt{\Delta t}$-scaled noise
(Sect.~\ref{sec:teff}). The \emph{rest-drive push} replaces the ORCA term by its drive part at rest,
$m_iv_{0,i}/\tau_{\rm orca}$, directed towards ($+$) or away from ($-$) the door. The bias probe applies $\pm b$, and
at a standoff the first exit records which member leaves first. The corrected-implementation probe swaps the legacy
for the RVO2 solver.

Each class predicts its own response to each probe. Under a Prevent mechanism a snapshot stays held in every probe, and
neither the push nor the bias changes it. An axial Reshape mechanism frees the snapshot with identical replays and a
freed fraction that does not depend on $\Delta t$; it frees under the push towards the door and not under the push
away, and at a standoff no member is favoured. A lateral Reshape mechanism also frees with identical replays and a
flat $\Delta t$ response, but only past $b_f$, with either sign of $b$, and the member on the side favoured by $b$
exits first. A Heat mechanism frees with exponential times to free at $\beta\ge1.5$; its noise seeds disagree, its
freed fraction falls as $\Delta t$ grows under per-step noise and stays flat under $\sqrt{\Delta t}$-scaled noise,
and no member is favoured. The outcomes of all three classes persist in the corrected implementation. A mechanism of
any class carries the \emph{defect flag} when outcomes it produces vanish in the corrected implementation, and
\emph{replay sensitivity} when a replay changes its outcome; in every other probe it responds as its class. These
responses hold by construction: every Prevent response, the disagreement of noise seeds, the $\Delta t$ response of
Heat, the favoured side of lateral Reshape, the vanishing outcome of a flagged mechanism and the changed outcome of a
replay-sensitive one.
```

(Deletes "(Glitch)" and the Table 2 pointer. "Probe ... at other Δt" — the levels 0.005 and 0.02 s are given in 4.4.)

**Sect. 5 opening (section sentence plus 5.1 first paragraph; replaces `05:10-16`):**

```latex
\section{Rest-State Physics}\label{sec:physics}
Both deadlocks are rest states in which the forces on every agent cancel, so whether they exist follows from a force
balance at the door.

\subsection{The Lone Trap at the Door Edges}\label{sec:lone}
An agent at rest on the door axis feels the wall forces of both door edges (Eq.~\eqref{eq:wall}). Their sideways
components cancel, and their backward sum peaks at $g_{\max}(r)$, which grows with the radius $r$: \GmaxTwenty\,N at
$r=0.20$\,m, \PphysGmaxThirty\,N at 0.30\,m and \PphysGmaxThirtyFive\,N at 0.35\,m (Fig.~\ref{fig:lone-trap}, left).
An agent released at rest on the axis therefore has a rest state if and only if
\begin{equation}\label{eq:stuck}
g_{\max}(r)\ \ge\ \frac{m\,v_{\rm eff}}{\tau}.
\end{equation}
Blockers at rest have $v_{\rm eff}/v_0\ge\PphysWeidMinFloor$, so we measure this balance by the \emph{stuck-alone
margin} $g_{\max}(r)-m v_0/\tau$; an agent with positive margin is \emph{stuck alone}. An agent arriving with speed can
still pass a door edge whose margin is small and positive. Among \StuckAloneN\ agents drawn from the distributions of
Table~\ref{tab:params} (\emph{spawned agents}), the SFM rest drive has median \DriveCOneMedian\,N, which exceeds
$g_{\max}=\PphysGmaxMeanR$\,N at the mean radius $r=\RevAthirteenRadiusMean$\,m, and a fraction \PphysStuckAloneFrac\
is stuck alone. Force-coupled ORCA adds its drive part (median \DriveORCAMedian\,N), which raises the median rest drive
to \PphysDriveTotal\,N and lowers the stuck-alone fraction to \StuckAloneFracCThree\ (Fig.~\ref{fig:lone-trap},
right). With the mean radius lowered to 0.225\,m (same spread), $g_{\max}$ falls by the factor
$e^{-0.025\,{\rm m}/B_w}=\RvAoneGmaxRatio$; then \RvAoneFracSFMShift\ [\RvAoneFracSFMShiftLo, \RvAoneFracSFMShiftHi]
of the spawned agents are stuck alone under SFM and \RvAoneFracORCAShift\ under force-coupled ORCA, against
\RvAoneFracORCA\ at 0.25\,m.
```

**Sect. 6 opening (section sentence plus 6.1 first paragraph; replaces `06:14`):**

```latex
\section{Screening Results}\label{sec:attribution}
The screening asks which perturbations free each rest state, by which class of mechanism, and whether a matched
surrogate can be told apart from force-coupled ORCA.

\subsection{Lone Keystones and Second Traps}\label{sec:att-lone}
\subsubsection{Drive and Constraint Parts.}
% Table 3 prose of Part 5.2 (first block) goes here.
The drive part alone frees the same lone keystones as force-coupled ORCA with either solver (Fig.~\ref{fig:quench}).
The SFM with $\tau'$ (Eq.~\eqref{eq:identity}), quenched from each snapshot, frees the same \RevAoneLoneFreed\ of
\RevAoneLoneN\ lone keystones as the drive part, and \RevAoneSecondFreed\ of \RevAoneSecondN\ second traps
(discordant \RevAoneDiscA:\RevAoneDiscB). The constraint part alone frees \EtwoLKConstrRVOFreed\ (RVO2) and
\EtwoLKConstrPubFreed\ (legacy). The push towards the door frees \EtwoLKFrozenPlusFreed\ lone keystones, earlier than
force-coupled ORCA ($\Delta$RMST $\RevAsevenPushLoneTimeEff$\,s, Holm $p\RevAsevenPushLoneTimePHolmRel$); the push
away frees \EtwoLKFrozenMinusFreed. SFM and SFM+TTC free none of the screening set. The stuck-alone margin with the
rest drive of force-coupled ORCA predicts which blockers force-coupled ORCA holds, with area \EtwoLKMarginAUC\ under
the receiver-operating-characteristic curve: where this margin stays positive the blocker is held, and elsewhere the
larger rest drive removes the rest state and frees it. % FLAG F4
```

**Sect. 7 opening (replaces `07_experiments.tex:11-12`):**

```latex
\subsubsection{Experiments and Model Runs.}
The CroMa bottleneck experiments~\cite{fzj_ped20219,boomers2023data} include five runs through a 0.8\,m entrance. In
two (4D030, 4D040) a corridor 2.0\,m long with thick tapered walls follows the entrance; the model represents these
walls as thin. In three (4D110, 4D120, 4D130) the entrance is a door in a wall, 0.2\,m long. The runs mix three
motivation conditions: participants walked normally (4D030, 4D110), hurried (4D040, 4D120) or gave full commitment
(4D130). In all runs but 4D130 they kept a 2\,m semicircle before the entrance clear. The trajectories are published
under CC BY 4.0~\cite{fzj_ped20219}; the experiments were approved by the ethics committee of the University of
Wuppertal, and participants gave informed consent~\cite{boomers2023data}. Every tracked participant passes,
\RevDFourDonethirtyPassed--\RevDFourDthirtyPassed\ per run, and none deadlocks (duplicate track IDs merged).
```

Insert at the end of the methods paragraph `07:17`: `[NEW: CroMa time-step check: flow ratio and completions of each variant at Δt = 0.005 s against 0.01 s on the same seeds.]` If the check reports the largest overlaps, the sentence at `03:53` (overlap bound) belongs next to it (FLAG F17).

### 6.5 Ten least clear passages, ranked, with rewrites

Ranking by how much a reader must reconstruct: R1 `03:64`, R2 `04:5` (rewritten as the Sect. 4 opening above), R3 `04:9-10`, R4 `06:17-20`, R5 `06:30`, R6 `05:41-42`, R7 `06:48`, R8 `05:18-20`, R9 `01:13-14`, R10 `06:51-52`.

**R1. `03_pedestrian_model.tex:64` (definitions and snapshot sets)**

```latex
A run is deadlocked when all speeds stay below 0.01\,m/s for 10\,s without an exit; its saved state is a
\emph{snapshot}. A \emph{quench} restarts a snapshot under one perturbation. It stops at its horizon (120\,s unless
stated) or once all speeds stay below $10^{-3}$\,m/s for 10\,s, and an agent is \emph{freed} when it exits
($|\mathbf x-\mathbf g|<0.5$\,m). A \emph{replay} is a quench with every coordinate displaced by Gaussian noise (SD
$10^{-9}$\,m); each snapshot and perturbation get five. The keystone test removes every agent but the \emph{blocker},
the agent nearest the door, and quenches the snapshot. The blocker is a \emph{lone keystone} if it is held and
removing it frees all others, and a \emph{second trap} if another agent is then held. In both cases the blocker is
held alone, so both are lone traps.

Five snapshot sets are nested, and a sixth is built separately. The \emph{deadlock set} holds the \FinCritN\ deadlocks
of \RevAfiveRuns\ room runs: \KeystoneBLone\ lone keystones, \KeystoneBSecondTrap\ second traps and \FinCritNegN\ pair
standoffs. The \emph{screening set} holds \EtwoNAll\ of them: all \EtwoNLK\ lone keystones and \EtwoNST\ second traps
drawn at random. The \emph{barrier set} holds the \LoneBarN\ screening-set snapshots whose barrier is accepted
(Sect.~\ref{sec:barrier}); the \RevAfiveGateFailSecond\ that fail are second traps. Two subsets of the barrier set are
evenly spaced in barrier rank: the \emph{time-step set}, \EthreeN\ of the \RevAfiveEthreeQual\ snapshots with a
full-condition barrier $\Delta U\ge3$\,J, and the \emph{Arrhenius set}, \EfourN\ of the \FixAthreeEfourQual\ snapshots
with an agent besides the blocker. The \emph{pair set}, built with $B_w=0.04$\,m on every wall, holds \PairN\
pair-standoff snapshots.
```

Moved out (cut C2): "(seeds 42--241 ...)", "PCG64 seed 2026", and `03:65` s1-s2 (seed ranges, replay seeds 900-904). Keep from `03:65`: "A deterministic perturbation has \RvAeightRunsPerSnap\ quenches per snapshot, one unperturbed and five replays. Of the \RvAeightRuns\ runs of the deadlock set \RvAeightComplete\ complete, \RvAeightDeadlocks\ deadlock and none reaches 600\,s. Both pair standoffs of the deadlock set fall among the \EsevenDefaultClassified\ deadlocks of the default-wall width runs at $w=0.8$\,m (Sect.~\ref{sec:lone})." The time-step-probe sentence for force-coupled ORCA moves to 4.4; the velocity-filter quench counts (360, 276) move to 6.4, where `06:55` already uses them. ("one unperturbed and five replays" restates 6 = 1 + 5 from `03:64-65`; P3 to confirm.)

**R2.** See the Sect. 4 opening in 6.4.

**R3. `04_protocol.tex:9-10` (matching and horizons)**

```latex
The protocol (Fig.~\ref{fig:protocol}) compares a \emph{resolver}, the perturbation credited with resolution, with a
\emph{surrogate} of another class matched to it at a horizon $T$. The two are matched when equality of their freed
fractions at $T$ (completed fractions for whole runs) is not rejected: the 95\% interval of the paired difference
covers zero. A match therefore holds for a given horizon. A stricter test asks for equivalence within $\pm\RvAfiveMargin$
in freed fraction, the 95\% resolution of force-coupled ORCA's own freed fraction on \EtwoNLK--\PairN\ snapshots; two
one-sided tests at level 0.05 declare equivalence when the 90\% interval of the difference lies inside this margin.

Quenches run to $T=120$\,s and whole runs to 600\,s. Force-coupled ORCA frees its last screening-set blocker by
\RevAeightSTRvoLatest\,s and completes its last whole run by \RevAeightWholeRvoLatest\,s, but noise keeps freeing
after these times. The match with noise therefore holds only from some horizon on: equality is not rejected from
\RevAeightLKNoiseCMatchFrom\,s ($\sigma=0.07$\,m/s) and \RevAeightLKNoiseNoneMatchFrom\,s ($\sigma=\RunNOneSigma$\,m/s)
at the lone keystones, and from \RevAeightWholeNoiseMatchFrom\,s in whole runs.
```

(If cut C5 is taken, the last sentence becomes "The horizons from which each match holds are given with the results (Sect.~\ref{sec:att-lone}, \ref{sec:att-whole})" and the 70/85/425 s values go to the framework.)

**R4. `06_screening.tex:17-20` (matched noise at the lone keystones)**

```latex
\subsubsection{Matched Noise.}
Per-step noise at $\sigma=0.07$\,m/s (five seeds per snapshot) and at $\sigma=\RunNOneSigma$\,m/s (20 seeds) is
matched to force-coupled ORCA at $T=120$\,s. At $\sigma=0.07$\,m/s, $\beta$ has median \RevAthreeSevenMed\ (quartiles
\RevAthreeSevenQone\ and \RevAthreeSevenQthree) and lies below 1 for \RevAthreeSevenBelowOneK\ of the \LoneBarN\
barrier-set snapshots, so this noise acts by fluctuations. Both levels are equivalent to force-coupled ORCA within
$\pm\RvAfiveMargin$ from $T=\RvAfiveLoneEtwoWinFrom$ and \RvAfiveLoneNoneWinFrom\,s on (90\% intervals
[$\RvAfiveLoneEtwoDiffLoNinety$, $\RvAfiveLoneEtwoDiffHiNinety$] and [$\RvAfiveLoneNoneDiffLoNinety$,
$\RvAfiveLoneNoneDiffHiNinety$]; $p=\RvAfiveLoneEtwoPTostDisp$ and $\RvAfiveLoneNonePTostDisp$). The 20-seed runs leave
\RevAnineLKNHalfA\ snapshots unresolved, all among the \RevAnineLKNHalfB\ that force-coupled ORCA holds. With five
seeds a mean of \RevAnineMisclass\ snapshots change outcome relative to the 20-seed result. Overlap cannot separate
noise from force-coupled ORCA: two halves of the noise seeds overlap with each other ($\Omega=\RunNOneJNoiseNoise$) as
much as noise overlaps with force-coupled ORCA ($\Omega=\RevAnineLKNHalfJ$).

Replay separates them by construction, through the noise stream alone. With the noise stream fixed, \RvAtenFlips\ of
\RvAtenNPairs\ noise quenches change; with different seeds, noise disagrees on \RevAsevenLoneEtwoReplayDiscA\
snapshots, whereas replays of force-coupled ORCA change \TabThreeLKRvoReplayDis\ of \TabThreeLKRvoReplays. The time
step separates them as well (time-step set; Fig.~\ref{fig:escape}c). Under per-step noise the escape rate follows
Eq.~\eqref{eq:ell} over $\beta=\RvAfourPerStepMin$--\RvAfourPerStepMax, by fluctuations below 1.5 at
$\Delta t=0.005$\,s; under $\sqrt{\Delta t}$-scaled noise it does not change with $\Delta t$; and force-coupled ORCA
frees the same snapshots at every $\Delta t$. [NEW: time-step probe at the matched level $\sigma=0.07$\,m/s: pooled
$\ell$ under per-step and $\sqrt{\Delta t}$-scaled noise over the time-step set, with the predicted values.] The
lateral bias frees no lone keystone (upper Wilson bound \EtwoMaxBiasUpperLK).
```

(The β paragraph moved from `05:44`. "does not change with Δt" interprets "√Δt-scaled noise does not" from Table 3 ("flat"); P3 to confirm. If C5 is taken, the TOST p-values in parentheses go.)

**R5. `06_screening.tex:30` (legacy solver)**

```latex
\subsubsection{The Legacy Solver.}
The legacy solver is the ORCA code of~\cite{gang2026}. For a leg of the velocity obstacle with unit direction
$\hat{\mathbf d}$ it takes the half-plane normal along $\mathbf u=(\mathbf v_{\rm rel}\cdot\hat{\mathbf
d})\,\hat{\mathbf d}-\mathbf v_{\rm rel}$, the change of the relative velocity onto the leg, whereas RVO2 takes the
leg direction rotated by $90^\circ$:
\begin{equation}\label{eq:legnormal}
\mathbf n_{\rm legacy}=\frac{\mathbf u}{|\mathbf u|}=-\operatorname{sgn}(\mathbf v_{\rm rel}\cdot\mathbf n_{\rm
RVO2})\,\mathbf n_{\rm RVO2},\qquad \mathbf n_{\rm RVO2}=(-\hat d_y,\,\hat d_x).
\end{equation}
The two normals agree while the relative velocity lies inside the velocity obstacle; outside it the legacy half-plane
is inverted. Replays of the legacy solver change the outcome in \EtwoReplayCThreePubFlips\ of \EtwoReplayN\ replays on
the screening set and \RevAfiveXPoolLegacyReplayChanged\ of \RevAfiveXPoolLegacyReplays\ on the \RevAfiveXPoolN\
second traps; replays with the RVO2 solver change none. Under the legacy solver the blocker jitters at
\PscrCreepSpeedMin--\RevAthirteenCreepSpeedMax\,m/s, with a net axial drift of $\RevAthirteenCreepDriftMin$ to
$+\RevAthirteenCreepDriftMax$\,mm/s. Two replays diverge where a leg normal flips sign (\FixAfourDiscLegFlip\ of
\FixAfourDiscN\ first divergences), and the exit then shifts by up to \PscrReplayPubMaxDt\,s. At the lone trap the
legacy solver frees the same lone keystones through its rest drive as the RVO2 solver, so this outcome persists in
the corrected implementation; its replay flips vanish there and are its replay sensitivity. At the pair standoff the
standoffs it frees beyond those of the RVO2 solver vanish (Sect.~\ref{sec:att-pair}); this loss sets its defect flag.
[NEW: legacy solver at the second traps: freed blockers at the \RevAsixSTSnaps\ screening-set and \RevAfiveXPoolN\
deadlock-set second traps, against the RVO2 solver and the drive part.]
```

The provenance sentence ("repository pedestrian-abs, commits \texttt{\RevAfourteenCommitConf} to \texttt{\PscrCommitConfHead}, tag \texttt{r2.0-baseline}; Eq.~\eqref{eq:legnormal} is line~\RevAfourteenDefectLine\ of \texttt{sim/steering/orca.py}, introduced in commit \texttt{\RevAfourteenCommitIntro}") moves to Data and Code Availability (cut C1). If the author wants it kept in print, a footnote at "the ORCA code of~\cite{gang2026}" is the place.

**R6. `05_deadlock_physics.tex:41-42` (Arrhenius test)**

```latex
The slope ratio, the Arrhenius slope divided by $-\Delta U$, has median \PphysRatioFull\ in the full condition,
\EfourRatioFrozen\ pinned and \EfourRatioAlone\ alone (Fig.~\ref{fig:escape}b). Its interval covers 1 for
\EfourCoverFull\ of \EfourFitsFull\ fits (full), \EfourCoverFrozen\ of \EfourFitsFrozen\ (pinned) and
\EfourCoverAlone\ of \EfourFitsAlone\ (alone). The full condition omits two snapshots: one below the 0.1\,J noise floor
of the string method, and one (\EfourSeedOneSeventyDU\,J) that never escapes in 300\,s. % FLAG F3
[NEW: the 0.13\,J snapshot: its barrier leads into an adjacent rest state; exit barrier from that state.] Pooled with
one intercept per snapshot and condition, the rates have slope $\FixAthreeCollapseSlope$ [$\FixAthreeCollapseSlopeLo$,
$\FixAthreeCollapseSlopeHi$] against $\beta$ (Fig.~\ref{fig:escape}a).

We extended the alone condition to $\beta=5$, 6 and 7 (\RvAthreeRestarts\ quenches, \RvAthreeCensored\ censored, at
most \RvAthreeCensFracMax\ per level) and fitted all six levels with a likelihood that accounts for censoring. Over
$\beta=1.5$--7 the slope ratio is \RvAthreeRatioShallow\ [\RvAthreeRatioShallowLo, \RvAthreeRatioShallowHi] at
$\Delta U=\RevBthreeDUShallow$\,J, \RvAthreeRatioMid\ [\RvAthreeRatioMidLo, \RvAthreeRatioMidHi] at \RevBthreeDUMid\,J
and \RvAthreeRatioDeep\ [\RvAthreeRatioDeepLo, \RvAthreeRatioDeepHi] at \RevBthreeDUDeep\,J, and
\RvAthreeSlopeRatio\ [\RvAthreeSlopeRatioLo, \RvAthreeSlopeRatioHi] pooled. The transition-state rate of the same
potential, with the Kramers and energy-diffusion factors and no fitted constant, predicts \RvAthreeTheoryRatio. With
the blocker alone at $\beta\ge1.5$, noise therefore frees it by activated escape.

The slope stays below $\Delta U$ because the linear drive bounds the well upstream and makes it softer than harmonic:
the slope reaches $\Delta U$ only as $\beta\to\infty$, and at $\beta=7$ the prefactor of the deepest trap is
\RvAthreeTstSevenOverHarmDeep\ of its harmonic value. Time discretisation raises the slope ratio by
\RvAthreeDtBiasMin--\RvAthreeDtBiasMax. At the deepest barrier and $\beta=6$--7 the escape times are over-dispersed
(Weibull shape \RvAthreeWeibullDeep\ [\RvAthreeWeibullDeepLo, \RvAthreeWeibullDeepHi]), which a one-agent model of the
same potential does not reproduce; the over-dispersion leaves the fitted slope unchanged.

At the saddle the blocker is underdamped: its friction $1/\tau$ is a median \RvAtwoGamOmegaMed\ of the barrier
frequency. Each oscillation at the barrier energy still loses a median \RvAtwoLossMed\,$\Delta U$ to friction, so the
Mel'nikov--Meshkov depopulation factor~\cite{melnikov1986} is at least \RvAtwoAMin, and damping predicts attempt
frequencies \RvAtwoAFitMed\ times Langer's prefactor~\cite{langer1969}. The fitted attempt frequencies are a median
\FixAthreeNuRatioAll\ of this prediction, and none of the \RvAtwoNFits\ fits lies within its predicted range. The
deficit persists at $\beta=5$--7. Two candidate causes, the anharmonic far side of the well and finite-barrier
corrections, are untested.
```

("fitted all six levels" restates "Over β = 1.5-7" with the three original and three extended levels; P3 to confirm the fit used all six. With cut C11, paragraph 3 keeps only its first sentence and paragraph 4 becomes: "The fitted attempt frequencies are a median \FixAthreeNuRatioAll\ of the damped Langer prediction~\cite{melnikov1986,langer1969}, at every $\beta$; the cause is untested.")

**R7. `06_screening.tex:48` (pair standoff: drive and constraint parts)**

```latex
Force-coupled ORCA frees \PairPubFreed\ of the \PairN\ standoffs with the legacy solver and \PairRvoFreed\ with the
RVO2 solver (McNemar $p\PairPubRvoPRel$; Fig.~\ref{fig:pair}). The standoffs it leaves held still move at 120\,s
(\RevAfifteenPairRvoMoving\ of \RevAfifteenPairRvoHeld\ with the RVO2 solver, \RevAfifteenPairPubMoving\ of
\RevAfifteenPairPubHeld\ legacy). The drive part alone frees \PairDriveFreed. The push frees \PairFrozenPlusFreed\
towards the door and \PairFrozenMinusFreed\ away. At rest the half-plane against the partner binds at all
\RevAelevenPairBinds\ members, and the constraint part points laterally away from the partner with
\RevAelevenRatioMin--\RevAelevenRatioMax\ of the drive's magnitude. This rest field is not a gradient (Jacobian
asymmetry \PscrJacAsymMin--\RevAelevenJacAsymMax), so the stability argument of Sect.~\ref{sec:rest} does not cover
force-coupled ORCA at the pair standoff. Alone, the constraint part frees \PairConsPubFreed\ standoffs (legacy) and
\PairConsRvoFreed\ (RVO2). Added to the drive part, it cancels the drive's lateral component towards the axis, so
force-coupled ORCA frees fewer standoffs than the drive part alone ($p\PairDriveRvoPRel$). Of the \RevAelevenPairDisc\
standoffs that the drive part frees and force-coupled ORCA holds, the rest field accounts for
\RevAelevenPairDiscStatic. The others, and the difference between the solvers, arise in motion, where the half-plane
turns towards the door.
```

(Q10: define "Jacobian asymmetry" or drop the range with cut C4. "the drive's magnitude": state whether this is the drive or the drive part.)

**R8. `05_deadlock_physics.tex:18-20` (release test and door width)**

```latex
Released alone at rest on the axis, at the position of $g_{\max}$ or 1\,m upstream, none of \RevBonePosN\ agents with
positive margin (the smallest \PphysPosMarginMin\,N) leaves within 60\,s, and all \RevBoneNegN\ with negative margin
(the largest $\PphysNegMarginMax$\,N) pass the door. % FLAG F1
In quenches with the blocker alone, all \FinCritPosN\ blockers of the deadlock set with positive margin stay held:
\KeystoneBLone\ lone keystones and \KeystoneBSecondTrap\ second traps. The \FinCritNegN\ others are group standoffs.
% FLAG F2: these two are pair standoffs (03:64; C3 fact 6a)
These \RevAthirteenStackN\ deadlocks hold a median of \RevAthirteenStackMedian\ stuck-alone agents, and at most
\RevAthirteenStackMax. Agents that can pass alone leave first: the stuck-alone fraction is
\RevAthirteenStuckFirstEightMin--\RevAthirteenStuckFirstEightMax\ over the first eight deciles of arrivals,
\RevAthirteenStuckNinthDecile\ in the ninth and \RevAthirteenStuckTenthDecile\ in the tenth.

Door width decides whether the lone trap holds. Over \RevBtwoNRuns\ runs at 11 widths from 0.70 to 1.00\,m, half
complete at the critical width $w_{50}=\RevBtwoWfifty$ [\RevBtwoWfiftyLo, \RevBtwoWfiftyHi]\,m (logistic fit;
Fig.~\ref{fig:width}, left). Without the density throttle ($v_{\rm eff}=v_0$; same spawns, 0.80--0.96\,m),
$w_{50}=\RvBoneWfiftyOff$ [\RvBoneWfiftyOffLo, \RvBoneWfiftyOffHi]\,m; paired by spawn, \RvBoneWidthOffOnly\ runs
complete only without the throttle and \RvBoneWidthOnOnly\ only with it ($p=\RvBoneWidthPDisp$). The stuck-alone
criterion is consistent with $w_{50}$: below $\RevBtwoWlo$\,m the median agent is stuck alone, and above
$\RevBtwoWhi$\,m no agent in the median run is. The parameter-free prediction $(1-f)^{100}$, with $f$ the stuck-alone
fraction, misses $w_{50}$ by \RevBtwoPredHundredOffset\,m. The crowd plausibly pushes stuck-alone agents through: held
ones arrived with at most \RevBtwoHeldActiveMax\ others active. % FLAG F7
```

**R9. `01_introduction.tex:13-14` (relation to the earlier study; if kept in the Introduction)**

Preferred: move the counts to the start of Sect. 6.2 and keep only the first three sentences here. If kept:

```latex
This paper extends~\cite{gang2026}. It keeps that study's scenario, a room with a 0.8\,m door and 100 agents, its
social force model with force-coupled ORCA and its noise surrogate. It adds the rest-state physics, the probes and
screening protocol, the identity of Eq.~\eqref{eq:identity}, the sign defect in the legacy linear-program solver
of~\cite{gang2026} and the comparison with the CroMa experiments. The two models differ in density: \cite{gang2026}
took densities from Voronoi cells with calibrated Weidmann coefficients, whereas this model counts neighbours within
$R$ (Eq.~\eqref{eq:des}). All ORCA results of~\cite{gang2026} used the legacy solver; here force-coupled ORCA (legacy)
uses it, and force-coupled ORCA uses the RVO2 solver, a line-by-line port of the RVO2 library
(Sect.~\ref{sec:identity}). With the code and settings of~\cite{gang2026}, force-coupled ORCA (legacy) completes
\RvAelevenCThreePubK\ of \RvAelevenCThreePubN\ runs and the social force model alone (SFM)
\RvAelevenCOnePubK\ of \RvAelevenCOnePubN; \cite{gang2026} reported \PendConfCThreeK\ and \PendConfCOneK\ of
\PendConfN. Under this model force-coupled ORCA completes \RvAelevenCThreeCfK\ of \RvAelevenCThreeCfN\ runs and SFM
\RvAelevenCOneCfK\ of \RvAelevenCOneCfN, and Sect.~\ref{sec:att-whole} attributes these completions to the drive part
[NEW: whole-run attribution of the drive part: completions with the drive part alone and with the SFM at $\tau'$ over
the same \RvAelevenCThreeCfN\ seeds, McNemar against force-coupled ORCA]. Adding the time-to-collision (TTC) force of
Eq.~\eqref{eq:ttc}, which exerts no force at rest, changes neither count significantly: with it \RvAelevenCFourCfK\ and
\RvAelevenCTwoCfK\ of \RvAelevenCFourCfN\ runs complete (same spawns; McNemar $p=\RvAelevenCFourCThreeP$ and
\RvAelevenCTwoCOneP).
```

(The current text points to Sect. 6.1 (`sec:att-lone`) for the attribution of whole-run completions; the whole-run attribution will sit in 6.2, hence `sec:att-whole`. P3 to confirm where the [NEW] numbers land.)

**R10. `06_screening.tex:51-52` (matched lateral bias)**

```latex
\subsubsection{Matched Lateral Bias.}
The matched bias $b^\ast$ is read off the thresholds $b_f$ of the same snapshots. It is therefore an in-sample
estimate that reproduces each solver's freed fraction at $T=120$\,s by construction. To test it out of sample, we
fitted $b^\ast$ on \RvAsixNHalf\ standoffs and predicted the freed fraction of force-coupled ORCA (legacy) on the other
\RvAsixNHalf, over \RvAsixNSplits\ random splits. The median error is $\RvAsixLegacyErrMedian$ (95\% range
$\RvAsixLegacyErrLo$ to $\RvAsixLegacyErrHi$), and splitting alone produces the same spread ($\RvAsixLegacyRefLo$ to
$\RvAsixLegacyRefHi$). With the RVO2 solver the median error is $\RvAsixRvoErrMedian$ ($\RvAsixRvoErrLo$ to
$\RvAsixRvoErrHi$). With either solver the bias and force-coupled ORCA differ in freed fraction by \PscrPairPubDiff\
(Holm $p\RevAsevenPairPubFreedPHolmRel$ and $p\RevAsevenPairRvoFreedPHolmRel$; Table~\ref{tab:matched}), but the
\PairN\ standoffs are too few to establish equivalence within $\pm\RvAfiveMargin$ (90\% interval
[$\RvAfivePairLegacyDiffLoNinety$, $\RvAfivePairLegacyDiffHiNinety$] legacy; $p=\RvAfivePairLegacyPTostDisp$ and
$\RvAfivePairRvoPTostDisp$). The freed set of the bias overlaps that of force-coupled ORCA as much as independent sets
would, with either solver.

Handedness separates the bias from force-coupled ORCA. The member below the door axis, which $b>0$ favours, exits
first in every standoff the bias frees; under force-coupled ORCA it exits first in \PairPubLower\ of \PairPubFreed\
freed standoffs (legacy) and \TabThreePairRvoOrcaLower\ of \PairRvoFreed\ (RVO2). The reversed bias $-b^\ast$ frees
\PairBsPubMinusFreed\ standoffs (legacy) and \PscrPairBsRvoMinusFreed\ (RVO2), with the member above the axis first in
all of them. With the legacy solver the standoffs that $-b^\ast$ frees differ from those that $+b^\ast$ frees
(discordant \PairBsPubRevA:\PairBsPubRevB).
```

### 6.6 Discussion and Conclusions

Discussion (limitations first, interpretation last; the throttle sentence no longer repeats Sect. 3.1):

```latex
\section{Discussion}\label{sec:discussion}
\subsubsection{Limitations.}
Agents are two-dimensional discs, 100 per room run, at doors of 0.8\,m (0.70--1.00\,m in the width runs). The lone
trap originates in the default wall range ($B_w=0.08$\,m) and the pair standoff in sharp segment ends with a wall
range of 0.04\,m. Force coupling is not ORCA's published form, and native ORCA is untested (Sect.~\ref{sec:identity}).
The density throttle shapes the rest drive; removing it leaves $w_{50}$ and the completions at 0.8\,m unchanged
(Sect.~\ref{sec:model}) and raises the CroMa flow (Sect.~\ref{sec:validity}). The stuck-alone fraction and $w_{50}$
depend on the radius through $g_{\max}(r)$ (Sect.~\ref{sec:lone}). Agents differ in temperature
($k_{\rm B}T_{\rm eff}\propto m_i\tau_i$), so the stationary state is not Boltzmann; $\beta$ uses the blocker's $\tau$,
as the blocker carries most of the unstable mode (Sect.~\ref{sec:teff}). All runs but the time-step probes and arch
runs use $\Delta t=0.01$\,s; halving it moves $w_{50}$ by $\RvBtwoShift$\,m [$\RvBtwoShiftLo$, $\RvBtwoShiftHi$]. A
match holds within a window of horizons (Sect.~\ref{sec:protocol}). On the \PairN\ pair-set snapshots, 95\% intervals
of freed-fraction differences reach [$\RvAfivePairLegacyDiffLo$, $\RvAfivePairLegacyDiffHi$]
(Table~\ref{tab:matched}). The matched noise lies below the tested $\beta\ge1.5$ (Sects.~\ref{sec:att-lone}
and~\ref{sec:att-whole}), so the whole-run stall prediction extrapolates the Arrhenius law.

\subsubsection{Mechanisms.}
Force-coupled ORCA, the matched noise and the matched lateral bias free the same fraction of deadlocks at horizon $T$,
through the rest drive, fluctuations and a lateral force (Sect.~\ref{sec:classes}). At the lone keystone the
rest-drive push matches force-coupled ORCA in every probe that separates the classes. % FLAG F5
```

("short wall range" became "a wall range of 0.04 m", the value of the pair set; P3 to confirm that "short" meant the pair-set value. "In the CroMa runs it lowers the flow" became "removing it raises the CroMa flow": the same fact stated from the removal side, matching the sentence's subject; P3 may keep the original order instead.)

Conclusions (optional; removes the verbatim repeat of the abstract):

```latex
The deadlocks of this social force model at a narrow door are rest states set by the wall range and the door-edge
segment ends; with the default walls half the runs complete at $w=\RevBtwoWfifty$\,m. Force-coupled ORCA frees the
lone trap through its rest drive, as the same model with $\tau'=\RevAoneTauPrimeLo$--$\RevAoneTauPrimeHi$\,s and
\RevAoneDriveRatioLo--\RevAoneDriveRatioHi\ times the rest drive does. Noise matched to it at horizon $T$ frees
deadlocks by fluctuations, and a matched lateral bias tilts the pair standoff out of its minimum; activated escape,
with an Arrhenius slope \RvAthreeRatioDeep--\RvAthreeRatioMid\ of the computed barrier, is established only with the
blocker alone at $\beta\ge1.5$. With uncalibrated defaults every variant passes \RevDThreeRatioMin--\RevDThreeRatioMax\
of the human flow over whole CroMa runs, and \RvBoneCroOffMin--\RvBoneCroOffMax\ without the density throttle. A
narrow-door deadlock count should not be read as crowd behaviour until probes name its mechanism and matched
experiments test its flow and passage gaps.
```

("as the same model with τ′ ... does" rests on `06:14`: the SFM with τ′ frees the same 30 lone keystones.)

---

## 7. Lint results

### 7.1 Method

Script `/tmp/a3lint/lint.py` (pattern set adapted from the standard's Appendix E, plus checks for internal labels, code in prose, numbers per sentence and paragraph, and British/American forms), run on macro-expanded copies of every file in `paper/sections`, the tables and the Fig. 1 caption, with source line numbers preserved (`/tmp/a3lint/expand.py`). Helper `/tmp/a3lint/dense.py` lists sentences with more than three numbers. Raw output: `/tmp/a3lint/lint_out.txt`.

### 7.2 Counts per file (raw flags, before judgement)

| File | Soft | Neg. | Announce | Label | Code | Nested ( ) | "by construction"/"therefore" | Long (>40 w or ≥5 commas) | >3 numbers |
|---|---|---|---|---|---|---|---|---|---|
| 00 abstract | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 3 |
| 01 introduction | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 3 | 6 |
| 02 related work | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 03 model | 0 | 1 | 0 | 2 | 0 | 0 | 1 | 6 | 8 |
| 04 protocol | 3 | 0 | 1 | 1 | 0 | 0 | 3 | 11 | 6 |
| 05 physics | 5 | 0 | 0 | 0 | 0 | 1 | 1 | 12 | 26 |
| 06 screening | 2 | 0 | 0 | 2 | 7 | 1 | 2 | 8 | 21 |
| 07 experiments | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 7 |
| 08 discussion | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 3 |
| 085 recommendations | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| 09 conclusions | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 2 |
| Fig. 1 caption | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 |
| Tables 2-4 notes | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 1 | 1 |

No hits in any file for: cleft or "What" openings, sentence-initial "However/Thus/Therefore/Hence,", self-announced significance (notably, crucially, importantly, interestingly, remarkably), machine-writing vocabulary (delve, landscape, pivotal, crucial, leverage, robust, comprehensive, novel, moreover/furthermore/additionally chains), dash pairs, bold or italic emphasis in running prose (`\emph` marks defined terms only), exclamation points.

### 7.3 Judged real defects (only these need action)

Softening and hedges
- `05:20` "The crowd plausibly pushes stuck-alone agents through": hedge with no number (FLAG F7).
- `04:10` "is not rejected only from a horizon on": double negative plus "only"; rewrite R3.
- The other "only" flags (`01:9`, `04:15`, `04:30`, `05:41`, `06:23`, `06:34`, `07:25`, `09:2`) restrict a claim to a condition; keep.

Rhetorical negation
- None rhetorical. `03:16` and `08:6` both say the throttle "is not part of the original social force model": the contrast is technical, but stated twice; keep it once (Sect. 3.1). `01:9` "credits need not transfer": keep.

Announcements
- `04:5` "Table 2 gives each class's predicted response": disappears with Table 2.

Antecedents and elliptical clauses (manual)
- `00:3` "the drive plus its drive part" (whose?); "frees it" (fine).
- `01:14` "Sect. 6.1 attributes them to the drive part" (them = completions); `01:20` "separate it from force-coupled ORCA" (it = matched noise).
- `03:45` "for force-coupled ORCA it is the first term" (it = rest drive).
- `04:5` "They therefore exclude each other" (they = the three forces, which then make the classes exclusive).
- `04:15` "so the quench carries the evidence" (of stability).
- `05:20` "consistent with this value" (= w50).
- `06:18` "with it fixed" (= the noise stream).
- `06:20` "√Δt-scaled noise does not" (does not follow Eq. ell? does not change?).
- `06:30` "and this sets its defect flag".
- `06:52` "its freed set" (= the bias's), "they differ from those of +b*".
All fixed in the rewrites.

Comma-spliced result lists and elliptical appositives
- `06:20` "follows Eq. (ell) ..., √Δt-scaled noise does not, and force-coupled ORCA frees ...".
- `05:56` "is at most 18.3 kN, one contact 4.85 kN (overlap 4.0 cm)".
- `07:23` "6.1 s (jamb range) and 96 s (noise), at least 410 and 430 s for SFM and force-coupled ORCA".
- `05:15` "..., 0.0016 under force-coupled ORCA (0.013 at 0.25 m)".
- abstract "0.40-0.60 of human flow, 0.48-0.72 without the density throttle" (kept in the rewrite as a short appositive; acceptable once).
- `04:21` "(smallest eigenvalue ≥66 N/m), a strict minimum": trailing appositive renames "snapshots"; write "so every one is a strict minimum".

Long sentences (real; others are equations or lists)
`03:16` s2 (49 w), `03:62` s1 (10 commas) and s3 (44 w), `03:64` s4 (45 w) and s5 (110 w), `04:9` s1 (46 w), `04:10` s3, `04:30` s2-s3, `04:31` s1 (43 w), `04:38` s3 (50 w) and s5, `04:41` last (45 w), `05:10` (39 w, 9 commas), `05:14`, `05:15`, `05:18` s1, `05:20` s1-s2, `05:41` s5, `05:44` (41 w), `05:47` s3, `05:51` s3 (50 w), `05:53`, `06:14` s4 and s6, `06:17` s2, `06:20` (47 w), `06:23` s2 (42 w), `06:36` s5 (41 w), `06:51` s2 and s4 (44 w each), `07:11` s2-s3, `08:6` (46 w), `09:2` s3 (45 w), Fig. 1 caption (65 w sentence), Fig. 6 caption (120 w), Table 3 note (90 w).

Nested parentheses
- Fig. 6 caption (real). `05:41` "(Fig. 6(b))" and `06:20` "(time-step set; Fig. 6(c), Table 4)" are reference formatting: write "Fig. 6b".

Internal labels and code in prose
- `04:5` "(Glitch)": delete.
- `03:64` "PCG64 seed 2026": move (C2).
- `06:30` repository name, commit hashes, tag, `sim/steering/orca.py`, line 113: move (C1).
- "deadlock-screen" (abstract, `01:21`, `085:2`, `10:4`): the released framework's name; keep.
- "4D030" and the other run names (`07:11`): public dataset identifiers; keep once.

Aphoristic closings
- None beyond the Conclusions' last sentence, which is the recommendation.

Headings (rule 7)
- "Screening Protocol and Methods" (two topics): split by the reorder.
- "Flow, Gaps and Velocity Fluctuation." (three topics): "Flow and Passage Gaps."
- "Fraction-Matched Noise." / "Fraction-Matched Lateral Bias.": "Matched Noise." / "Matched Lateral Bias." (term map 16).
- Others name their content.

Number format and precision (paper's own rule, `04:41`: two significant figures, three where an interval or threshold needs them)
- Over-precise against that rule: 0.0451 (`06:36`), 1.73% (`05:51`), 18.3 kN and 4.85 kN (`05:56`), 0.108 m/s (`07:23`), 0.0079-0.0085 (`05:41`), 2.04 s (`07:21`), 0.0081 and −0.0069 N (`05:18`). Not changed here (Part 9, Q11).
- Ranges with en dash, intervals in brackets, thin space before units, "20 000" with thin space: consistent.

Spelling (British, venue-consistent)
- British forms found: neighbour(s) (10), towards (9), centre (3), favoured (2), modelling, modeller(s), behaviour, crystallise, normalised, discretised, discretisation, realised. Oxford -ize forms: none; -ise is used throughout. American forms in prose: none. ("centering" hits are `\centering`.) The heading "Acknowledgments." is printed by `llncs.cls` (`\ackname`); leave it, it is the class convention. Visible text in the figure scripts and `fig_protocol.tex` has no American forms.
- Serial comma: omitted throughout ("velocity noise and a lateral bias"; "turning and lateral steps"); the rewrites keep this.
- Citation style: numeric (splncs04), consistent.

---

## 8. FLAGS

Claims stronger than the evidence, or inconsistent with another part of the paper or with the C3 recomputations (`reports/C3_REPORT.md`). The rewrites keep these sentences at their current strength; the author or P3 decides.

- **F1 (`05:18` s1; contribution 1).** "Released alone at rest on the axis at the position of g_max or 1 m upstream, none of 200 agents with positive margin ... leaves within 60 s." C3 fact 6f: B1 released the positive-margin set only at the rest position; released 1 m upstream, 127 of 200 positive-margin agents pass [0.57, 0.70]. The sentence is wrong for the 1 m case. The criterion (Eq. stuck) concerns release at rest at the g_max position, which stands. Default: state the release point (at rest at the position of g_max) and, if wanted, add the 1 m result with C3's numbers.
- **F2 (`05:18` s2).** "the 2 others are group standoffs" contradicts `03:64` ("2 pair standoffs") and C3 fact 6a (both have two members). Use "pair standoffs".
- **F3 (`05:41`).** The 0.13 J snapshot (E1b seed 170): C3 Task 5 shows its 0.128 J barrier leads into an adjacent rest state, 21.9 J lower, and the exit barrier from there is 2.82 J; the full-condition β assigned to it was 33-77 against the exit barrier. The snapshot is in the barrier set (56) used for the β quartiles (`05:44`), the stall prediction (`06:36`) and the 23-of-56 count. Default: describe it as a barrier into an adjacent rest state; P3 to check whether the 56-barrier statistics change.
- **F4 (`06:14`).** "Force-coupled ORCA (RVO2) holds the blocker where the stuck-alone margin with its rest drive added stays positive ... elsewhere its rest drive removes the fixed point and frees the blocker." C3 fact 6c: 2 of the 30 freed blockers have positive margin (AUC 0.983, not 1). The categorical "where ... stays positive" holds for 32 of 34. Default: "predicts ... with ROC area 0.98" alone, or add "with two exceptions".
- **F5 (`08:3`).** "the rest-drive push matches force-coupled ORCA in every probe that separates the classes": true for the class-separating probes (Table 2), but the push frees earlier (ΔRMST −4.0 s, Holm p < 10^-4, `06:14`). A reader may take "every probe" to include time to free. Default: add "though it frees earlier".
- **F6 (`06:36`).** "The survival function of noise stalls ... lies within 0.0451 of its prediction ..., with no parameter fitted": descriptive, no test or interval (C3 fact 6e), and three significant figures against the paper's rule. The conclusion "noise frees whole-run deadlocks by fluctuations" rests on β, not on this agreement, and is stated as an extrapolation; that is fine.
- **F7 (`05:20`).** "The crowd plausibly pushes stuck-alone agents through": a hypothesis with one supporting number (held ones arrived with at most 9 others active); mark as a hypothesis or test it.
- **F8 (`05:51`).** "the 5 others escape at most 1.73% below b_f, carried over by the members' inertia": the inertia explanation is asserted, not tested.
- **F9 (abstract).** "replays reveal outcome sensitivity that traces to a sign defect": the evidence is 4 of 5 first divergences at a leg-normal sign flip (`06:30`). "Traces to" is supported for 4 of 5; acceptable if the text gives the count, which it does.
- **F10 (`03:64`).** "The nested snapshot sets are ... and the pair set": the pair set is built separately and is not nested. Fixed in R1 (a factual correction of the description, not of a result).
- **F11 (contribution 2).** "time to free and the whole-run final state separate it empirically": at the second traps ΔRMST does not separate (p = 0.13). Qualify: "at the lone keystones and in whole runs".
- **F12 (`06:23`).** "the screening set's 26 and the other 134, which respond alike, Holm p = 1.0": no difference detected is not "alike"; write "which do not differ".
- **F13 (`03:53`).** "At default speeds bodies overlap by at most 0.62 cm (room) and 2.4 cm (CroMa), so the contact under-resolution at 5 m/s does not reach them." C3 Task 4: the noise variant in CroMa reaches 3.75 cm overlap at Δt = 0.01 s, with an explicit-friction factor 2κhΔt/m = 2.25, above the stability bound of 2 (1.00 at Δt = 0.005 s, where flows are unchanged). The 2.4 cm bound is for SFM; the claim does not cover the noise variant. Relevant to the [NEW: CroMa time-step check].
- **F14 (`05:41` and abstract).** "With the blocker alone at β ≥ 1.5, noise therefore frees it by activated escape": supported (three barriers, intervals cover the TST value). Not a flag on strength; listed because the full-condition median 1.2 sits above 1, and the abstract and conclusions correctly restrict the claim to the alone condition. Keep the restriction in every rewrite.
- **F15 (numbers).** Precision against the paper's own rule: see Part 7.3. Not changed here.

---

## 9. INPUTS NEEDED FROM THE AUTHOR

1. **CroMa.** Expand the acronym at first use, or describe it? Default: describe ("the CroMa bottleneck experiments [refs], five laboratory runs through a 0.8 m entrance") without expanding, unless you give the project's full name.
2. **Solver convention.** Write "force-coupled ORCA" for the RVO2 solver and "(legacy)" only for the other, with one convention sentence in Sect. 3.2? Default: yes (saves about 45 repetitions).
3. **Matched noise names.** Two matched levels exist (σ = 0.07 m/s at the quenches, σ* = 0.0467 m/s in whole runs). Default: "matched noise (σ = 0.07 m/s)" and "matched noise σ*", no new symbol.
4. **Horizons.** Keep only the TOST horizons (89, 86, 545-600, 22-43 s) in the text and move the not-rejected horizons (70, 85, 425 s) to the framework (cut C5)? Default: yes.
5. **Section order.** Adopt the physics-first order of Part 2.10 (11 sections), or merge protocol and results into one section to keep 10? Default: 11 sections.
6. **Fig. 1 caption.** About 100 words is the shortest that keeps every encoding in the caption. Accept, or move some encodings (colour bars) into a legend drawn in the figure? Default: accept 100 words; the standard forbids annotations inside the figure.
7. **Contact arches (5.4).** Compress to three sentences (C15), delete, or keep? Default: compress.
8. **Arrhenius second-order checks (C11).** Move the underdamping and discretisation detail to the framework, keeping the TST prediction and the attempt-frequency deficit in one sentence? Default: yes.
9. **Undefined terms.** Confirm (a) "final-state class" = at rest or moving at 600 s, plus the keystone class of the held blocker; (b) "outcome identity" in the Holm families means what (replay outcomes identical?). Default: (a) as written; (b) "replay outcomes identical across the five replays", to be confirmed.
10. **"Jacobian asymmetry" (`06:48`).** Which measure (for example ‖J − Jᵀ‖/‖J‖)? Default: define it in one clause; if undefined, drop the range (C4).
11. **Precision.** Round the values in Part 7.3 to the paper's two-significant-figure rule (0.0451 → 0.045, 1.73% → 1.7%, 18.3 → 18 kN, 4.85 → 4.9 kN)? This changes printed numbers, so it needs your approval. Default: round, through the registry.
12. **FLAG F1 (release 1 m upstream).** State the release point as "at rest at the position of g_max" and add C3's 127/200 for the 1 m release? Default: yes.
13. **FLAG F3 (0.13 J snapshot).** Describe it as a barrier into an adjacent rest state and re-check the 56-barrier statistics? Default: yes, as C3 recommends.
14. **Provenance (C1).** Move repository, commits, tag and source line to Data and Code Availability? Default: yes.
15. **Relation to the earlier study (`01:13-14`).** Move the counts to Sect. 6.2 and keep three sentences in the Introduction? Default: yes.
16. **Second-trap result in the contributions.** Add "force-coupled ORCA frees 121 of 160 second-trap blockers where its drive part alone frees 149"? Default: yes, one sentence in contribution 2.
17. **Discussion scope.** The Discussion has no paragraph relating the findings to granular clogging (`02:6`) or to equifinality (`01:9`). Add one (about 0.2 page)? Default: no, page budget.

---

## 10. HANDOFF

**Current state.** Audit complete; nothing in `paper/` edited. This report is the only committed file. Scripts and outputs are outside the repository: `/tmp/a3lint/expand.py` (macro expander), `/tmp/a3lint/lint.py`, `/tmp/a3lint/dense.py`, `/tmp/a3lint/lint_out.txt`, `/tmp/a3lint/exp/` (expanded sources), `/tmp/a3lint/abs_new.tex` (abstract draft, 250 words). Paper state audited: origin/main `afbeed0`, 26 pages.

**Decisions made (by this audit, all reversible by the author).**
- Canonical terms as in Part 3; "matched" replaces "fraction-matched"; "standoff" is the umbrella for pair and group standoffs; "waiting zone" replaces "holding area".
- Tables: delete 2 and 3; merge 4 and 5 into one four-column table; keep 1 and 6. The table change is page-neutral; the page saving comes from cuts C1-C15 (about 0.9 page).
- Proposed order: rest-state methods, rest-state physics, protocol, screening results.
- Rewrites in Part 6 keep every number (as the original macros) and every claim; sentences under FLAGS keep their strength and carry `% FLAG` comments.
- [NEW] slots placed for: whole-run attribution of the drive part (Intro R9, contribution 2, Sect. 6.2), legacy solver at the second traps (R5), time-step probe at the matched noise (R4), CroMa time-step check (Sect. 7 methods), the 0.13 J snapshot (R6).

**Open items.**
- P3: apply Parts 5 and 6 in the order of Part 1, edit `experiments/tables/make_tables45.py` for the merged table, delete `tables/table2_signatures.tex` and `tables/table3_observed.tex` inputs, rebuild, check page count (expected about 25 before new material).
- Author: Part 9 questions; FLAGS F1-F5 and F13 need a decision before the text is finalised.
- Confirm in the rebuilt PDF that every number of the deleted tables appears in the text (list in Part 5.2 and 5.4).
