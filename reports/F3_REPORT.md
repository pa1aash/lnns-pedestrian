# F3 report

## Figures (published 5c8ea1d, b0fcb39)
- FIG-1: 600 dpi throughout (Fig. 2 raster included). FIG-2: tick labels from plan/GLOSSARY.md ("push ±", "constraint pub/RVO2", "C1 jamb $B_{w,\rm edge}$"). FIG-3: script math at least 6 pt.
- FIG-4: C3 published dash-dotted in Fig. 6. FIG-5: PDFs without creation date; a re-render is byte-identical. FIG-6: figures/ALT_TEXT.md. FIG-10: Fig. 2 cache rebuilt from committed data, byte-identical.
- Fig. 8 is 0.6 cm taller so that "C1 jamb $B_{w,\rm edge}$" fits.
- Fig. 4 right (decision): per (snapshot, condition), the fitted Arrhenius slope over −ΔU_cond, 28 fits with intervals, markers by condition, line at 1; 25 of 28 intervals cover 1. Left Kaplan–Meier panel unchanged; FIG-8 closed. Ratios from E4_analysis.json (fix_a3.json holds only pooled fits).

## Repository (published e652443)
- REPO-1..5: venv-based make targets (stamp file), README Reproduce section, Blender 5.2.2 note, layout table, optional QUEUE_PID pause, CITATION.cff, .zenodo.json, experiments/SEEDS.md.
- Fresh clone of github.com/pa1aash/lnns-pedestrian at 63ce775 in /tmp: make venv 35 s, make figures 36 s, make paper 41 s, all OK, tree clean afterwards.

## Fig. 1 caption (D14) and overlay
- Two sentences, 89 words; colour and arrow keys kept. Overlay labels in Latin Modern at 6.5 pt; nothing re-rendered.

## Proposed Fig. 4 caption
Left, Kaplan–Meier fraction of blockers escaped at the middle noise level for the full (solid), pinned (dashed) and alone (dotted) conditions. Right, the ratio of the fitted Arrhenius slope to $-\Delta U_{\rm cond}$ for every snapshot and condition (full ●, pinned □, alone ▲) with 95\% intervals, against $\Delta U_{\rm cond}$; the line marks 1.

## Queue 3 runs
- Ran 11-09 21:40 to 11-10 00:17; macros \RunN* in paper/registry/runs.yaml; regress.py prints e381b49dc24acccd OK before and after. All bracketed intervals are 95%. J is the Jaccard index of failure sets; its independence value comes from permuted labels.
- N6 (pair minimum, 92 snapshot × sign cases): the minimum is lost non-smoothly at a jamb segment end in 92 of 92. In the 66 cases where continuation located the loss, the minimum–saddle distance has slope 1.000 (range 0.997–1.000) on δ and the work 2.000 (range 1.995–2.000), against 0.5 and 1.5 for a saddle-node; none is near the saddle-node values. The other 26 keep their minimum to a median 0.98 of the bisection threshold with μ1 unchanged, then lose it. μ1 at the loss is 65–121 N/m (median 94) and changes by less than 0.2% from δ = 0.3 to 0.001. The quench passage-time exponent is −0.16 (range −0.23 to −0.04; saddle-node −0.5). Verdict: answers the §5 pending "whether μ1 reaches zero at $b_f$" with no; glossary G4 then requires "loss of the minimum at $b_f$" in place of "fold".
- N1 (lone trap, σ = 0.0717 m/s by logistic inversion, 34 snapshots × 20 seeds): frees 588/680 = 0.865 [0.837, 0.888], −0.018 [−0.074, 0.044] from C3 RVO2. J between noise halves is 0.75 [0, 1] and between noise and ORCA 0.75 [0, 1]; independent sets give 0.06 (p = 4.0×10⁻⁴). Noise frees 24 of 80 runs on ORCA's 4 unresolved snapshots, and its per-snapshot rate separates them (AUC 0.996). The interval is wide because only 3–4 snapshots stay unresolved. Verdict: confirms §6.1 "identity does not separate the two" and fills its pending.
- N3 (lone trap, every agent at the blocker's $k_BT_{\rm eff}$, 540 runs, 397 escapes): slope ratio median 1.03 (range 0.58–1.46), interval covering 1 in 7 of 8 fits (E4 full: 1.15, 7 of 8). Paired with E4 the ratio is a median 0.10 lower, 4 of 8 above, sign test p = 1.00. Weibull shape 1.04 [0.96, 1.12] (E4 full alone 1.05 [0.97, 1.14]). Verdict: confirms the §5 Arrhenius sentence; the ratio stays near 1 when every agent is at the blocker's temperature. "The pooled Weibull shape exceeds 1" holds only when pooled over conditions.
- N2 (whole runs, σ* = 0.0467 m/s, independent noise stream, 186 spawns): 90/186 complete, −0.048 [−0.132, 0.037] from E6b. Two noise streams overlap at J = 0.48 [0.39, 0.56]. Noise and ORCA overlap at 0.51 [0.42, 0.60] (E6a–N2) and 0.41 [0.32, 0.50] (E6a–E6b); independence 0.30–0.33, permutation p < 10⁻⁴. Odds ratios of joint failure: 3.5 [1.8, 6.8] noise–noise, 4.7 [2.5, 9.4] and 2.5 [1.3, 4.7] noise–ORCA. Verdict: confirms §6.2 "identity does not separate them" and fills its pending.
- N5 (arches, 25 runs per setting, checks every 0.1 s): at Δt = 0.0025 s and 5 m/s all 25 complete and arches form in all 25 (1060 episodes, 26% of checks). The longest lasts 3.3 s, none reaches 5 s, and 0/25 runs are persistent [0, 0.13]. Peak body force is 22 kN (108 kN at Δt = 0.01 s). At 3 m/s all 25 complete with 8 episodes of at most 0.1 s; at 2 m/s 8 complete and 17 deadlock, with no arch. At the default drive all 25 deadlock with no arch at any check or at the stop. Verdict: "no persistent arch" holds at Δt = 0.0025 s and at every drive. The §5 pending should say that at the default drive every run deadlocks, as a contact-free rest state.

## Changelog entries proposed (for S3)
- Fig. 4 right: per-fit Arrhenius slope ratio with intervals replaces the earlier collapse panel.
- Fig. 1 caption cut to two sentences; overlay labels at 6.5 pt; Figs 2–8 glossary tick labels, 600 dpi, reproducible PDFs; alt text.
- Repository: venv make targets, Reproduce section, CITATION.cff, .zenodo.json, SEEDS.md; a fresh clone builds.
- Pair standoff: the minimum is lost at a jamb segment end with linear scaling, described as loss of the minimum at $b_f$.
- Noise identity tests repeated with 20 seeds per lone-trap snapshot and with an independent whole-run noise stream; escape at equal temperatures; arch check at Δt = 0.0025 s and lower drives.

## [NEEDS PALAASH]
- Session P: fill the four \pending{} markers (§5 pair, §5 arches, §6.1, §6.2) from the \RunN* macros, replace "fold" in §5 and the Fig. 5 caption, and adopt the Fig. 4 caption above.
- Fig. 1 caption is 89 words against the D14 target of about 85; cutting further loses part of a key.
- Captions of Figs 4 and 8 in paper/ still say "frozen" and "jamb $B_w=0.04$" (session P).
- The N2 permutation p is at its floor 1/(B+1) = 1.0×10⁻⁴; quote it as $p<10^{-4}$.
- N1 σ = 0.0717 m/s lies 0.002 beyond the E2 grid (0.03–0.07).
- Main failed `make numbers` between 85969ec and 3580d67 (an N5 key containing a dot).
- Release tag v1.0-lnns not created. Static solver scan A-4 not run by F3.
