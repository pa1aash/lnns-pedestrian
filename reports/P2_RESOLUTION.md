# Referee recheck, revision 3 (second referee report)

Judged from the printed paper (paper/main.pdf of 12 Nov 18:40, 26 pp., read with pdftotext) and its sources. The report
itself is not on disk; IDs F1-F3, M1-M15, m1-m19 follow the condensed list of the revision brief. The lens items carry no
numbering in any source: B1-B9 here are Figs. 1-9 (the figure requests of the revision), C1-C3 the table requests
(Table 1; the split into Tables 2 and 3; Tables 4 and 5), D1-D16 the sixteen prose requests in the order the brief
lists them, E the abstract, F the references and Related Work, G1-G5 the remaining requests (repeated numbers,
conclusions, intro premise, recommendations, limitations). Pending C2 inputs are marked "partly - pending C2 X".

## Framing and main issues
F1 | resolved | Sect. 4.1, 5.2, 6.2, 8, 10; Table 2 | activated escape claimed only with the blocker alone at beta >= 1.5; matched noise acts "by fluctuations" (median beta 0.64 and 1.4 stated); Table 2 Heat cell "exp. times at beta >= 1.5"; time-step span beta = 0.75-5.0 (beta0 = 1.5 and 2.5) in Sect. 4.4
F2 | resolved | Sect. 4.1; Tables 2, 3; Sect. 6.1 | three exclusive classes by the force added at rest, defect flag from the corrected-implementation probe alone, replay sensitivity a separate attribute, legacy "Reshape, axial" with the flag, separate First-exit column, daggers for by-construction cells; the legacy flag now comes from the pair standoff alone (lone-trap cell "persists; no", note c; Sect. 6.1), the vanishing lone-trap replay flips are its replay sensitivity; noise replay attribute settled by the fixed-stream replay (0 of 170 change, Sect. 6.2)
F3 | resolved | Sect. 1, 3.1, 5.1, 8 | (i) crowd-disaster opening replaced by the default-wall deadlock motivation; (ii) throttle "not part of the original social force model [20, 22]" in Sect. 3.1 and Limitations, ablation w50 and 0.8 m completions reported, CroMa flow without the throttle 0.64 (SFM) and 0.72 (force-coupled ORCA) in Sect. 7, abstract, intro and conclusions; (iii) stuck-alone fraction 0.081 [0.077, 0.085] at r = 0.225 m; (iv) [13] reproduction counts given, SFM+TTC 5 and force-coupled ORCA with TTC 56 of 100 (McNemar p = 0.38, 0.87) in Sect. 1
M1 | resolved | Sect. 4.4; Limitations | beta set from the blocker's tau_i; full-condition weighting 0.91-1.2 (median 1.0); per-agent temperature in Limitations
M2 | resolved | Sect. 5.2 | gamma/omega_b = 0.41 (underdamped), Mel'nikov-Meshkov factor >= 0.79, predicted 0.97 of Langer; "turnover factor below 1" sentence replaced by the measured 0.69 deficit, stated as unexplained
M3 | resolved | Sect. 5.2; Fig. 6 | pooled slope -0.93 [-0.98, -0.88] beside per-depth 0.85-0.93 and pooled 0.89; 39 of 360 censored, at most 0.30 per level; anharmonic well and TST prediction 0.90; Weibull 0.66 [0.49, 0.87] at the deepest barrier (headline lower end now 0.85 per the data)
M4 | resolved | Sect. 4.2, 6.1-6.3; Tables 4, 5 | non-rejection stated as horizon-dependent with onsets; margin +-0.10 and TOST 90% intervals for each comparison (lone keystones inside, whole runs only T = 545-600 s, second traps not matched, pairs too few); b* marked in-sample with the 200-split result
M5 | resolved | Sect. 1, 5.1 | "released at rest", arriving agents can pass a marginal edge, "consistent with", "plausibly pushes"
M6 | resolved | Sect. 7; Table 6 | flow ratio defined, 10-90% flow leads, per-geometry ratios, three motivation conditions, diameter 1.1 times shoulder width, ethics sentence, closing "cause of the flow deficit is not identified here"; throttle-off flow for SFM and force-coupled ORCA in Sect. 7 (noise and edge-wall variants not rerun)
M7 | resolved | Sect. 3.3; Limitations | largest overlap 0.62 cm (room) and 2.4 cm (CroMa) at default speed; Delta t = 0.005 s moves w50 by -0.003 m [-0.009, 0.003] (Limitations)
M8 | resolved | Sect. 4.3 | Remark replaced by the fixed-point and Lagrange-Dirichlet sentences with the TTC cutoff caveat
M9 | resolved | Eq. (13), Sect. 6.1; Abstract; Data and Code Availability | both normals in one display; hashes and paths only in the code statement; abstract wording as requested
M10 | resolved | Sect. 1 | retained, new and model-difference statements; legacy 29/50 and SFM 3/200 against 13 and 0 of 25 in [13]; no erratum statement; SFM+TTC and the blend with TTC added in Sect. 1
M11 | partly | Sect. 3.4, 4.5, Table 1 | seeds, selection rules, string settings, ORCA settings, 1/t_esc for the deterministic resolver and the 360/276 decompositions are in; why 2 of 98 (Sect. 5.1) and 2 of 196 (Sect. 3.4) agree (seeds 42-141 are a subset of 42-241) is left to the reader
M12 | partly | Figs. 1-9 | F3 files and captions inserted; Fig. 1 and Fig. 3 residues (B1, B3)
M13 | resolved | Tables 1-5 | R10 numbering and labels; p beside each estimate, no replay p-values, "First exit below axis", n.a./not run note; Table 1 one row per parameter, R and ORCA count "this work", tau spread not attributed to [20], tau0 to [27] (Table 3 keeps "lower", defined in its note)
M14 | resolved | Sect. 1, 3.4, 4.2, 5.1, 5.2, 5.4, 6.3; Table 6 | glossary gone; lone keystone, second trap, replay defined at first use; wall-variant, Weibull, arch, horizon sentences split; censoring counts in Table 6; typo gone
M15 | resolved | Sect. 4.6; Tables 4, 5; Sect. 5.4 | Holm family per table, intervals marked unadjusted, "none of these 20 converged runs at 5 m/s"

## Minor
m1 | resolved | Sect. 5.1 | stray accent gone
m2 | resolved | Abstract, Sect. 1, 3.2, 10 | "drive plus (its) drive part" wherever the tau' model is meant
m3 | resolved | Fig. 4 | hatched band is the total rest drive, medians 214 and 430 N named
m4 | resolved | References | cite package; grouped citations sorted and compressed
m5 | resolved | Tables 1-6 | numbered in order of first reference
m6 | resolved | Table 1 | source column corrected
m7 | resolved | Table 1 | tau0 [27]; "this work" rows flagged
m8 | resolved | Sect. 4.5 | climbing-image step attributed to Henkelman et al. [23]
m9 | resolved | Fig. 6 | panel letters (a)-(c)
m10 | resolved | Fig. 6 caption | Delta U_cond, escape rate and attempt frequency defined
m11 | resolved | Fig. 1 caption | "marker"
m12 | resolved | Sect. 3.1 | bias switched on as a step at t = 0
m13 | resolved | Sect. 7 | gap datum stated once
m14 | resolved | Fig. 5 | y label "fraction of runs completed", bracket shaded
m15 | resolved | title block | left as is (author decision outstanding)
m16 | resolved | Sect. 3.1 | implied length scale 1 m
m17 | resolved | Sect. 5.4 | "20 converged runs ... all complete"
m18 | resolved | Sect. 2 | "a surrogate matched in freed fraction (Sect. 4.2)"
m19 | resolved | credits | three placeholders kept

## Lens B: figures
B1 | partly | Fig. 1 | labels 7 pt, sigma of the band named, arrow key complete; caption "blue, force-coupled ORCA's rest drive, its drive part" contradicts the rest-drive definition of Sect. 3.2; graphic keeps a bare "ORCA" label and "held alone"
B2 | resolved | Fig. 2 | direct labels, spawn rectangle, CroMa dimensions, dashed experiment walls
B3 | partly | Fig. 3 | greyscale, R6 classes, separate defect-flag box; boxes still read "frozen deadlocks", "Signatures" and "lateral tilt" against the snapshot/response/bias vocabulary
B4 | resolved | Fig. 4 | caption corrected (total rest drive)
B5 | resolved | Fig. 5 | bracket shaded; throttle-off completions as open squares
B6 | resolved | Fig. 6 | panel letters; (c) defines the force-coupled ORCA quantity as inverse time to free
B7 | resolved | Fig. 7 | baseline rows removed and named in the caption; right panel two curves with bands
B8 | resolved | Fig. 8 | noise rows removed; solver line styles named (b grid stated in Sect. 5.3, not the caption)
B9 | partly | Fig. 9 | marker shape by length, 600 s line, open markers; legend "SFM, B_w,edge" and "SFM + noise sigma*" differ from Table 6 and the text; identical smoothing not stated

## Lens C: tables
C1 | resolved | Table 1 | as M13
C2 | resolved | Tables 2, 3 | predictions and observations split, First-exit and replay-sensitivity columns; noise replay cell by construction, confirmed by the fixed-stream replay (Sect. 6.2)
C3 | resolved | Tables 4, 5 | former 3a/3b with p beside each estimate, Holm family sizes, unadjusted intervals marked

## Lens D: prose
D1-D2 | resolved | Sect. 6, 8 | Sect. 6 opening and the repeated Sect. 8.1 paragraph deleted
D3 | resolved | Abstract, Sect. 1, 10 | headline numbers only there and at their establishing place (w50 not in the abstract, word limit)
D4 | resolved | Sect. 5.2 | heading and opening sentence as requested
D5-D11 | resolved | Sect. 1, 5.1, 5.3, 6.1, 7; Abstract | "whereas"; smaller threshold sentence; "quenched, it frees", "The copies part when", "does not make the model realistic" gone; "dominates" replaced by 89 of 100 and 11 of 11; "descriptive group size" replaced by the fitted exponent
D12-D13 | resolved | whole paper; Sect. 3.4 | no bare class nouns; nested sets defined once with sizes
D14-D16 | resolved | Sect. 2-7 | "five" runs; t_c, Omega, S(x; x0, c); one unit style; 2.04 s at the 0.01 s resolution

## Abstract, references, other lenses
E | resolved | Abstract | 249 words; R11 and R6 wording, counts in place of "dominates", earlier-solver sentence; coined terms (fraction-matched, replay, rest drive) undefined in it
F | resolved | Sect. 2; References | Helbing-Farkas-Vicsek freezing by heating [21], Chraibi 2010 and 2015 [8, 7], bottleneck experiments, hybrid models [28]; entries fetched (dataset [1] prints 2026, the registrar's year for a 2021 DOI)
G1 | resolved | Sect. 6.4 | "On another 100 spawn seeds" once
G2 | resolved | Sect. 10 | sentence 2 per F1; last sentence as requested
G3 | partly | Abstract, Sect. 1 | attribution to [13] kept; one independent example [38] (detour term, corridors and buildings, not doors); the general claim of the opening sentence is not softened
G4 | resolved | Sect. 9 | (ii) round the door edges, (iv) noise with [43], (vi) throttle
G5 | resolved | Sect. 8 | throttle, single time step, per-agent temperature, radius sensitivity listed

## What a referee would still dispute
- Sect. 6.1, Table 3 note c (lone traps): the legacy solver's defect flag at the lone traps is set by replay flips that vanish under RVO2, while the freed set is unchanged. That is replay sensitivity under another name; R6 separated the two, so only the pair standoff (21 freed fall to 7) carries the flag cleanly.
- Abstract, Sect. 5.2: "as transition-state theory predicts" covers the slope only. The fitted attempt frequencies are 0.69 of Langer's prefactor with none of 28 fits in the predicted range, and the full condition's median slope ratio is 1.2; the rate theory is not confirmed, only the exponent.
- Sect. 1, Abstract (premise): the claim that steering terms "are credited" with clearing narrow-door deadlocks rests on the authors' own [13] and one detour-model study [38] not about doors. A referee would call the motivating practice under-documented.
- Sect. 3.4, 5.1, 9(ii) (scope): the lone trap comes from the default wall range and the pair standoff from sharp segment ends; the paper's own recommendation removes the latter. A referee could read the deadlocks as model artefacts of one parametrisation, one 100-agent room and one door width, with limited bearing on crowd models generally.
- Sect. 4.2 (margin): the +-0.10 equivalence margin is derived from force-coupled ORCA's own resolution on 34-46 snapshots, so it is data-dependent and generous (3-5 snapshots). Equivalence holds at the lone keystones, in whole runs only for T = 545-600 s, not at the second traps, and is unestablished at the pairs.
- Sect. 3.2, Limitations: "force-coupled ORCA" is the authors' construction, native ORCA is untested, and the identity of Eq. (7) makes its rest effect a shorter relaxation time of the SFM itself. A referee may say the paper screens its own coupling rather than ORCA.
- Sect. 7, Table 6: every variant passes 0.40-0.60 of human flow, model agents start farther away, radii exceed the participants' and the five human runs mix motivations. The comparison shows a deficit without a cause; the keyword "Model validation" overstates it, and without the throttle the flow rises to 0.64-0.72, so the throttle explains only part of the deficit.
- Sect. 3.3, Limitations (time step): all production runs use Delta t = 0.01 s, contacts are under-resolved at 5 m/s; Delta t = 0.005 s leaves w50 unchanged.
- Sect. 3.1, Limitations (throttle): the Eq. (2) density throttle is not in the original model; its removal is tested for w50 and 0.8 m completions only.
- Abstract, Sect. 4 (coinage): the abstract still uses about ten coined terms (lone trap, blocker, pair standoff, rest drive, drive part, fraction-matched, replay, defect flag) that a reader meets undefined; Figs. 1 and 3 keep superseded vocabulary.

## Counts (72 IDs)
resolved 66 | partly 6 (M11, M12, G3 and the figure items B1, B3, B9) | not resolved 0 | disagreed 0
