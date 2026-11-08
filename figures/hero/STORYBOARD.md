# Hero figure (Fig. 1): production spec and mock v2 (batch HV2, plan change C32; mock v1 was batch 4C, C24)

Status: **mock v2 only** (900 px). The production render (2882 px) is not made; it waits for Palaash's go-ahead.
Mock v2: `figures/hero/mock_v2/fig1_mock_v2.pdf` (12.2 cm, vector overlay on the 900 px render `fig1_hero_mock_v2.png`), `fig1_mock_v2.png` (300 dpi raster) and `fig1_mock_v2_{grey,deuteranopia,protanopia}.png`.
The paper still includes `figures/fig1_hero.tex` + `figures/fig1_overlay.tex` + the v1 mock image; those names and paths are unchanged (`fig1_hero.tex` gained `\providecommand{\overlayfile}`, default `figures/fig1_overlay.tex`, so v1 compiles as before). On approval the v2 overlay (`mock_v2/fig1_overlay_v2.tex`) and the production render replace `fig1_overlay.tex` and `fig1_hero.png`. The caption is in `figures/fig1_caption.tex` (`\FigOneCaption`, two sentences).
Earlier pilot options A/B/C are kept in `storyboard/` for the record.

## Pipeline
1. `experiments/hero/export_hero.py` (plan interpreter, `PYTHONPATH=code`; physics in `hero_phys.py`; colour tables from `make_luts.py`) -> `data/derived/hero/{lone.npz, pair.npz, inset.json, hero_physics.json, luts.npz, floor_deltaE.json}` (about 10 s). `select_pair.py` -> `pair_selection.json`.
2. `experiments/hero/render_hero.py` (Blender, Cycles, Metal GPU, `-t 2`) renders the image with no text, arrows, lines or scale bars and writes the projected anchors to `figures/hero/mock_v2/fig1_overlay_v2.json`.
3. `tools/make_fig1_overlay.py` -> `figures/hero/mock_v2/fig1_overlay_v2.tex` (TikZ: arrows, coordinate lines, scale cluster, 17 labels, inset). `tools/check_fig1_labels.py` checks every compiled word sits on light pixels (mean >= 0.70, 5th percentile >= 0.45); v2: 0 flagged.
4. `experiments/hero/mock.sh` runs 2-3, compiles `fig1_mock_v2.tex`, makes the CVD variants (`cvd_variants.py`, figures venv). Memory gate: starts when >= 4.5 GB is free, polls every 5 min up to 3 h. Production: `--width-px 2882 --samples 128` through the same wrapper (not run).

## Layout (12.2 cm wide, 7.44 cm tall, 2 x 2; gaps 0.2 cm and 0.15 cm)
One background colour for the figure and all four panels: neutral off-white #F5F5F5 (the floor is exactly this colour at and below 5 N; unshaded floor renders at 245/255, panel edges 243-245).
| panel | content |
|---|---|
| top-left | lone scene: orthographic camera, 65 deg elevation, 2.65 printed cm per metre (6.0 cm = 2.26 m across); kerbs 0.10 m high; floor = backward wall force on a lone r = 0.25 m agent; agents at true radius, cividis +-150 N |
| bottom-left | pair scene: same camera, metre scale and crop; floor from the pair's own wall law (B_w = 0.04), same ramp |
| top-right | lone ribbons: own drive (black, the alone landscape), added drive (blue); ball at the alone minimum; vermilion band k_BT_eff; ghost ball downhill; 45 J per printed cm (was 30; the longer ribbon range no longer fits at 30) |
| bottom-right | pair ribbons: no tilt (black), tilted (yellow F0E442); ball at the frozen state, ghost downhill; 1 J per printed cm |
Screen orientation: the door is at the top; screen right = -y (scenes and inset mirrored relative to a y-up plot).
Inset (TikZ, 1.40 cm, top-right of the lone scene): room walls, 100 initial positions, the three residual agents in their margin colour, the lone scene's extent as a thin rectangle; 0.25 pt border; no dimension line, no label. Checked on the render: the area under it is plain background (max deviation 4/255), so it covers no agent, arrow or force lobe.

## v2 changes (C32), all applied
1. Labels: 6.5 pt (`\fontsize{6.5}{7.5}`), the paper's serif (Computer Modern), dark text, no boxes, halos or leader lines. Exactly 17: lone scene "lone trap", "held alone", "passes alone", "drive", "wall", "ORCA", "0.5 m", "100 N"; lone ribbons "own drive", "added drive", "noise", "10 J"; pair scene "pair standoff", "held together"; pair ribbons "no tilt", "tilted", "0.5 J". Panel tags top-left; ribbon labels at the left end of each ribbon above the curve's highest point under the label; "held alone" sits 0.27 cm left of and 0.12 cm above the drive/ORCA junction (clear of it); no label on an agent.
2. Removed: "door", "tilt" and the yellow lateral-bias arrow, the "partner" label (the arrow stays, unlabelled), the inset's "10 m" label and bar.
3. Floor: truncated magma, orange (magma 0.78) -> red -> dark purple (0.25, #51127C), on log force from 5 N to 1000 N, blended in CIE Lab from the background over the first 22 % of the range (5-15 N), exactly background at and below 5 N. No yellow. Minimum CIEDE2000 between any floor colour and the held-alone agent's cividis yellow (#FEE434) is 28.8; to the lateral-bias yellow #F0E442 it is 28.4 (both near 5.5-5.9 N, where the floor is nearly background); threshold 20 (`floor_deltaE.json`). The check is on the LUT; the render reproduces the LUT to about 1 % (emission-dominated floor material).
4. Wall-overlap cells (probe disc would overlap a wall) are plain floor (the background colour), blended with a soft mask on a 0.5 cm grid upsampled 2x; no grey blobs.
5. Arrows: shafts 0.6 pt, Stealth heads 0.095 cm, solid, thin white under-stroke on the drive and wall arrows (and partner in the pair) so they stay visible over dark discs. Lone: drive (black), wall (dark magma #51127C), ORCA rest drive (blue, from the drive tip), neighbours' push 17.5 N (grey #777777, from the drive tip, unlabelled; 0.13 cm). Pair member: drive (black), wall and partner (dark magma), unlabelled. One scale for both scenes: 0.003 m per newton, 2.65 cm per metre. No dotted or dashed element.
6. One scale-bar cluster in the free top-left corner of the lone scene (100 N parallel to the door axis, foreshortened like the arrows; 0.5 m along y), sharing a corner; scale bars on the ribbons are 10 J and 0.5 J.

## Snapshots
- Lone: `data/E1/library/E1b_seed52.pkl`, corrected-forward, lone keystone. Blocker 19 at (9.6601, 4.9967) m, r = 0.2962 m, v0 = 0.847 m/s, tau = 0.5165 s, margin +146.2 N; neighbours 38 (r = 0.2241, margin -9.6 N) and 54 (r = 0.2088, -41.6 N) pass alone. Frozen density 0.0707 /m^2 (v_eff/v0 = 1.000).
- Pair: `data/E7b/library/E7b_B0.04_seed397.pkl` (corrected-forward, B_w = 0.04, convex_union). Members 81 at (9.5993, 4.5478), r = 0.2898, margin -84.7 N and 35 at (9.6044, 5.4358), r = 0.2862, margin -92.8 N: both pass alone, members at the jamb faces, mean lateral offset -0.008 m from the axis. Why this one: of the 25 two-agent near-symmetric E7b snapshots (`pair_selection.json`) it matches the pilot `w25_B0.04_seed43` stiffness best (Hessian eigenvalues 82.7 / 1095 / 3077 / 3227 N/m against 85 / 1124 / 3192 / 3285), the geometry is close (positions within 0.011 m, radii within 0.010 m of the pilot) and its fold (b = 0.0315) lies at the upper edge of the pilot's bracket (0.01-0.03). The closest by raw position is seed 276 (distance 0.018 against 0.020) but it is 20 % softer.

## Physics checks (all from `hero_physics.json`)
- C1 force balance at the frozen state (drive + wall + partner against the code's `compute_forces`, all held agents): lone set 2.3e-4 N max; pair 4.2e-4 N max (limit 0.1 N). Component sum equals the code total to machine precision.
- Lone blocker at the frozen state (N): drive (131.16, 0.32); wall (-148.63, 4.87); partner push from the two neighbours (17.47, -5.19); ORCA rest drive w_o m v0 e/tau_ORCA (135.44, 0.33), w_o = 0.9996. The wall force exceeds the drive by the 17.5 N push of the neighbours; the 17.5 N push is drawn in the lone scene as the short grey arrow (v2).
- Pair member (lower): drive (125.43, 40.50); wall (-125.20, 0.00); partner (-0.23, -40.50). Lateral-bias increment at b = 0.035: (-1.49, 4.36) N, 4.6 N.
- Lone ribbon (blocker alone, line y = 4.9967, own r, v0, tau, density frozen, wall energy = minus the line integral of the code's wall force):
  - own drive (c = m v0/tau = 131.16 N): one minimum at x = 9.6412 m and one barrier at x = 9.9498 m, barrier 27.96 J. The gated alone barrier (`data/BAR/gate.jsonl`, seed 52 accepted) is 27.90 J (x = 9.641 / 9.950; 1-D axis integral 27.9009 J): agreement 0.23 %.
  - the minimum is 1.9 cm behind the frozen position (9.6601), 0.16 J above the well floor, because the neighbours' 17.5 N forward push is part of the frozen balance; with the neighbours pinned the minimum is the frozen position and the barrier is 21.21 J (gate "frozen").
  - added drive = alone landscape + ORCA rest drive (c + w_o m v0/tau_ORCA = 266.6 N) + the neighbours' push (their agent-agent force on the blocker along the line, neighbours pinned at their frozen positions: 17.5 N at the frozen position, 24.7 / 25.4 / 23.8 N at x = 9.75 / 9.79 / 9.86 m). **No stationary point** (v2). Batch 4C had omitted the push and found a 0.53 J dimple at x = 9.791 m (barrier 9.863 m).
    - Why: seed 52 is freed by C3 RVO2 in E2 (6/6 runs, blocker out at 2.49 s) although its C3 rest margin is +10.8 N (g_max 277.4 N against the 266.6 N C3 drive; one of the two E2 snapshots freed with a positive C3 margin, E2_analysis `freed_with_margin_C3_gt_0` = 2). Cause of the dimple: the alone ribbon leaves out the neighbours' push, which is larger than the 11 N shortfall. Checked against the code: the full C3 (rvo2) hybrid force on the blocker along the line (rest, frozen density) equals the ribbon's force to 3e-10 N both alone (minimum net force -10.4 N, two sign changes) and with the neighbours pinned (minimum +14.7 N, no sign change); the ORCA term at rest is unconstrained (w_o = 0.9996, v_eff/v0 = 1.000, v_pref = v0 e), so it is not density, v_eff or ORCA constraints. A lone C3 blocker with the others removed stays held (dynamics, inertia included): the freeing in E2 comes from the neighbours. Three-agent dynamics from the snapshot frees the blocker at 2.3 s (E2: 2.49 s).
    - The own-drive ribbon stays the alone landscape (spec), so the two ribbons differ by the ORCA drive and the neighbours' push (about 4 J over the ribbon; 0.1 cm at 45 J/cm). With the neighbours pinned the own-drive minimum would sit at the frozen position with barrier 21.2 J (gate "frozen").
  - thermal band: k_BT_eff = m sigma^2 / (1 - (1 - dt/tau)^2) = 10.22 J at sigma = 0.07 m/s, dt = 0.01 s, tau = 0.5165 s (0.37 of the barrier). sigma = 0.07 matches C3 RVO2 on the 34 lone keystones in E2 (noise 0.871, C3 RVO2 0.882, paired difference -0.012).
- Pair ribbon (common lateral shift c of both members, relaxed over the opposed coordinate and both forward positions; zero at c = 0; density frozen):
  - b = 0: strict minimum at c = 0 (Hessian eigenvalues all positive; ribbon minimum at c = -2e-8 m; no other minimum); local maxima at c = -0.062 and +0.094 m, 0.41 J high on the +c side. Potential/force residual |F_code + grad U| = 6e-8 N.
  - fold: ribbon criterion b = 0.0315; the code's overdamped relaxation holds at b = 0.0158 and 0.0284 and frees at 0.035 (13.9 s) and 0.05 (6.2 s). Tilt drawn: b = 0.035 (11 % past the fold): no minimum anywhere, one maximum at c = -0.098 m. Tilted-field residual (frozen e_perp) 0.15-0.29 N for |c| <= 0.10 m.

## Scales
- Floor: 2.65 cm per metre (printed). Arrows are floor vectors at 0.003 m per newton (333 N per metre of floor), drawn at agent-top height in the floor plane, so 100 N = 0.30 m = 7.95 mm along the screen-horizontal and 7.2 mm along the door axis (foreshortened by sin 65 deg). The 100 N scale bar is parallel to the door axis, so it is foreshortened exactly like the drive, wall and ORCA arrows; the 0.5 m bar lies along y. One scale for both scenes.
- Lone ribbons: 45 J per printed cm (scale bar 10 J = 0.22 cm); x = 9.45-10.00 m over 4.1 cm.
- Pair ribbons: 1 J per printed cm (scale bar 0.5 J); c = -0.10 to +0.10 m over 4.1 cm.
- Vertical ribbon distances carry the camera's cos 12 deg; the scale bars are projected with the same camera.

## Honesty note for the text
- Heights are stylised: agents 0.15 m, kerbs 0.10 m; ribbon thickness and extrusion depth carry no data; ball and ghost radii are display sizes.
- **Ball position (lone).** The own-drive ribbon is the alone landscape (blocker alone on its line, own r, v0, tau, frozen density, the code's wall law and corner rule). The ball sits at its minimum, x = 9.6412 m, which is 1.9 cm behind the blocker's frozen position (9.6601 m): the neighbours' 17.5 N forward push is part of the frozen force balance (drive 131.2 + push 17.5 = wall 148.6 N), and the alone minimum lies where the wall force equals the drive alone. The own-drive barrier is 27.96 J against the gated alone barrier 27.90 J (0.23 %).
- **Added-drive ribbon (lone).** Alone landscape + ORCA rest drive + the neighbours' push with the neighbours pinned (no ORCA constraints beyond the rest value, which is unconstrained here). It is the rest-state energy of the code's C3 (rvo2) force along the line; it has no stationary point. The ribbons are not drawn on the same footing: the own-drive ribbon omits the push.
- Pair ribbon coordinate: the common lateral shift c of both members, minimised over the opposed shift and both forward positions, relative to c = 0; "tilted" is the same coordinate with the goal direction tilted by b = 0.035 (tilt term frozen at the snapshot's perpendicular); b = 0.0315 is the fold.
- Energy scales differ between the two pairs of ribbons (45 J/cm and 1 J/cm); heights are comparable only within a pair.
- The thermal band is the per-step-noise effective temperature k_BT_eff = 10.2 J at sigma = 0.07 m/s (0.37 of the barrier), not a measured fluctuation of the frozen state.
- The ghost balls mark where the ribbon leads, not simulated trajectories. The ribbons are rest-state (quasi-static) energies; E2's freeing of the lone keystone is dynamic and needs the neighbours.
- The neighbours' push arrow is to scale (17.5 N = 0.13 cm).
- X

## Open choices for Palaash
1. Go-ahead for the 2882 px render (or changes on mock v2).
2. The own-drive ribbon is the alone landscape and the added-drive ribbon includes the neighbours' push (needed for no minimum). Option: put the pinned neighbours in both (minimum at the frozen position, barrier 21.2 J, ball without the 1.9 cm shift).
3. Lone ribbon scale is 45 J/cm (30 J/cm no longer fits once the ribbon starts at 9.45 m so the "own drive" label clears the ball).
4. The thin white under-stroke on arrows stays (needed on the dark pair discs); say if arrows should have none.
