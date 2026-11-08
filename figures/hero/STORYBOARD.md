# Hero figure (Fig. 1): production spec and mock (batch 4C, plan change C24)

Status: **mock only** (900 px). The production render (2882 px) is not made; it waits for approval of the mock.
Mock: `figures/hero/mock/fig1_mock.pdf` (12.2 cm, vector overlay on the 900 px render) and `fig1_mock.png` (300 dpi raster of the PDF), with `fig1_mock_{grey,deuteranopia,protanopia}.png`.
The batch-3B render in `figures/fig1_hero.png` (option C, 2882 px) is superseded by this design and is replaced by the production render once approved; until then `paper/main.tex` points the figure at the mock image.
The earlier pilot options A/B/C are kept in `storyboard/` for the record.

## Pipeline
1. `experiments/hero/export_hero.py` (plan interpreter, `PYTHONPATH=code`; physics in `hero_phys.py`) -> `data/derived/hero/{lone.npz, pair.npz, inset.json, hero_physics.json}` (about 10 s).
   `select_pair.py` -> `data/derived/hero/pair_selection.json` (the pair choice).
2. `experiments/hero/render_hero.py` (Blender, Cycles, Metal GPU, `-t 2`) renders the image with no text, arrows, lines or scale bars and writes the projected anchors to `figures/hero/fig1_overlay.json` (`bpy_extras.object_utils.world_to_camera_view`, panel offsets applied).
3. `tools/make_fig1_overlay.py` -> `figures/fig1_overlay.tex` (TikZ fragment: arrows, coordinate lines, scale bars, labels, inset). `tools/check_fig1_labels.py` checks every compiled word sits on light pixels.
4. `figures/fig1_hero.tex` = the PNG at `\textwidth` plus the overlay in a scope normalised to the image. The paper preamble has `\usepackage{tikz}` and `\usetikzlibrary{arrows.meta}`.
5. `experiments/hero/mock.sh` runs 2-4 for the 900 px mock (memory gate: starts when at least 4.5 GB is free, polls every 5 min up to 3 h). Production: `--width-px 2882 --samples 128` through the same wrapper (not run).

## Layout (12.2 cm wide, 7.44 cm tall, 2 x 2, white background, no borders; gaps 0.2 cm and 0.15 cm)
| panel | content |
|---|---|
| top-left | lone scene: orthographic camera, 65 deg elevation, 2.65 printed cm per metre of floor (6.0 cm = 2.26 m across, x from 9.18 to 10.70 m); kerbs 0.10 m high; floor = backward wall force on a lone r = 0.25 m agent (magma_r, log 1-1000 N, grey where the probe would overlap a wall); agents at true radius, cividis +-150 N, dark shading edge, 8 mm bevel |
| bottom-left | pair scene: same camera, elevation, metre scale and crop; floor from the pair's own wall law (B_w = 0.04), same ramp |
| top-right | lone ribbons, front-on orthographic (camera 12 deg above horizontal): own drive (black), added drive (blue), black ball at the frozen position, vermillion band for the thermal energy, translucent ghost ball downhill; one energy scale |
| bottom-right | pair ribbons: no tilt (black), tilted (yellow, F0E442), ball at the frozen state, ghost downhill; its own energy scale |
Screen orientation: the door is at the top; a physical camera looking along +x has screen right = -y, so the scenes and the inset are mirrored relative to a y-up plot (the same in both).
Context inset (TikZ, 1.55 cm, top-right corner of the lone scene, over free floor beyond the door wall): room walls, 100 initial positions (seed 52, rebuilt with the simulator), the three residual agents in their margin colour, the lone scene's extent as a thin rectangle, 10 m dimension.
Overlay text: Computer Modern 8 pt, `black!85`, no boxes, halos or leader lines; arrows have a thin white under-stroke (yellow: black).
No dotted or dashed element anywhere.

## Snapshots
- Lone: `data/E1/library/E1b_seed52.pkl`, corrected-forward, lone keystone. Blocker 19 at (9.6601, 4.9967) m, r = 0.2962 m, v0 = 0.847 m/s, tau = 0.5165 s, margin +146.2 N; neighbours 38 (r = 0.2241, margin -9.6 N) and 54 (r = 0.2088, -41.6 N) pass alone. Frozen density 0.0707 /m^2 (v_eff/v0 = 1.000).
- Pair: `data/E7b/library/E7b_B0.04_seed397.pkl` (corrected-forward, B_w = 0.04, convex_union). Members 81 at (9.5993, 4.5478), r = 0.2898, margin -84.7 N and 35 at (9.6044, 5.4358), r = 0.2862, margin -92.8 N: both pass alone, members at the jamb faces, mean lateral offset -0.008 m from the axis. Why this one: of the 25 two-agent near-symmetric E7b snapshots (`pair_selection.json`) it matches the pilot `w25_B0.04_seed43` stiffness best (Hessian eigenvalues 82.7 / 1095 / 3077 / 3227 N/m against 85 / 1124 / 3192 / 3285), the geometry is close (positions within 0.011 m, radii within 0.010 m of the pilot) and its fold (b = 0.0315) lies at the upper edge of the pilot's bracket (0.01-0.03). The closest by raw position is seed 276 (distance 0.018 against 0.020) but it is 20 % softer.

## Physics checks (all from `hero_physics.json`)
- C1 force balance at the frozen state (drive + wall + partner against the code's `compute_forces`, all held agents): lone set 2.3e-4 N max; pair 4.2e-4 N max (limit 0.1 N). Component sum equals the code total to machine precision.
- Lone blocker at the frozen state (N): drive (131.16, 0.32); wall (-148.63, 4.87); partner push from the two neighbours (17.47, -5.19); ORCA rest drive w_o m v0 e/tau_ORCA (135.44, 0.33), w_o = 0.9996. The wall force exceeds the drive by the 17.5 N push of the neighbours; the partner force is not drawn in the lone scene (spec).
- Pair member (lower): drive (125.43, 40.50); wall (-125.20, 0.00); partner (-0.23, -40.50). Lateral-bias increment at b = 0.035: (-1.49, 4.36) N, 4.6 N.
- Lone ribbon (blocker alone, line y = 4.9967, own r, v0, tau, density frozen, wall energy = minus the line integral of the code's wall force):
  - own drive (c = m v0/tau = 131.16 N): one minimum at x = 9.6412 m and one barrier at x = 9.9498 m, barrier 27.96 J. The gated alone barrier (`data/BAR/gate.jsonl`, seed 52 accepted) is 27.90 J (x = 9.641 / 9.950; 1-D axis integral 27.9009 J): agreement 0.23 %.
  - the minimum is 1.9 cm behind the frozen position (9.6601), 0.16 J above the well floor, because the neighbours' 17.5 N forward push is part of the frozen balance; with the neighbours pinned the minimum is the frozen position and the barrier is 21.21 J (gate "frozen").
  - added drive (c + w_o m v0/tau_ORCA, 266.6 N): **it still has one stationary pair**, a dimple at x = 9.791 m (barrier 9.863 m) 0.53 J deep. Check "no minimum" fails strictly (stuck-alone margin with the ORCA rest drive is +10.8 N). At 30 J/cm the dimple is 0.2 mm tall; the ball starts 6.6 J above the dimple's rim, so the drawn motion (downhill to the right end of the ribbon) is what the potential does.
  - thermal band: k_BT_eff = m sigma^2 / (1 - (1 - dt/tau)^2) = 10.22 J at sigma = 0.07 m/s, dt = 0.01 s, tau = 0.5165 s (0.37 of the barrier). sigma = 0.07 matches C3 RVO2 on the 34 lone keystones in E2 (noise 0.871, C3 RVO2 0.882, paired difference -0.012).
- Pair ribbon (common lateral shift c of both members, relaxed over the opposed coordinate and both forward positions; zero at c = 0; density frozen):
  - b = 0: strict minimum at c = 0 (Hessian eigenvalues all positive; ribbon minimum at c = -2e-8 m; no other minimum); local maxima at c = -0.062 and +0.094 m, 0.41 J high on the +c side. Potential/force residual |F_code + grad U| = 6e-8 N.
  - fold: ribbon criterion b = 0.0315; the code's overdamped relaxation holds at b = 0.0158 and 0.0284 and frees at 0.035 (13.9 s) and 0.05 (6.2 s). Tilt drawn: b = 0.035 (11 % past the fold): no minimum anywhere, one maximum at c = -0.098 m. Tilted-field residual (frozen e_perp) 0.15-0.29 N for |c| <= 0.10 m.

## Scales
- Floor: 2.65 cm per metre (printed). Arrows are floor vectors at 0.003 m per newton (333 N per metre of floor), drawn at agent-top height in the floor plane, so 100 N = 0.30 m = 7.95 mm along the screen-horizontal (12.6 N/mm) and 7.2 mm along the door axis (13.9 N/mm, foreshortened by sin 65 deg). The 100 N scale arrow is parallel to the door axis, so it is foreshortened exactly like the drive, wall and ORCA arrows; the 0.5 m bar lies along y. One scale for both scenes.
- Lone ribbons: 30 J per printed cm (scale bar 10 J); horizontal 9.1 cm per metre over x = 9.55-10.00 m.
- Pair ribbons: 1 J per printed cm (scale bar 0.5 J); horizontal 20.5 cm per metre over c = -0.10 to +0.10 m.
- Vertical ribbon distances carry the camera's cos 12 deg; the scale bars are projected with the same camera, so they are exact.

## Honesty note for the text
- Heights are stylised: agents 0.15 m, kerbs 0.10 m; ribbon thickness and extrusion depth carry no data; ball and ghost radii are display sizes.
- Ribbon coordinates. Lone: position of the blocker's centre along the line through its frozen position parallel to the door axis, with every other agent removed, own r, v0, tau, frozen density, the code's wall law and corner rule (the potential is the integral of the code's own force). Pair: the common lateral shift c (both members moved by c along y), minimised over the opposed shift and both forward positions, relative to the value at c = 0; "tilted" is the same coordinate with the goal direction tilted by b = 0.035 (tilt term frozen at the snapshot's perpendicular).
- Energy scales are different for the two pairs of ribbons (30 J/cm and 1 J/cm); heights are comparable only within a pair.
- The thermal band is the per-step-noise effective temperature k_BT_eff at sigma = 0.07 m/s, not a measured fluctuation of the frozen state.
- "Added drive" is the ORCA rest drive added to the own drive (no ORCA constraints, no neighbours); its small dimple is not visible at this scale.
- The ghost balls are where the ribbon leads, not simulated trajectories.
- The lateral-bias arrow is drawn to scale (4.6 N = 0.4 mm) with a minimum head; at print size it is a dot.

## Open choices for Palaash
1. Yellow lateral-bias arrow: to scale it is a dot (0.4 mm). Options: keep to scale; draw it x10 with a stated factor; or show the tilted goal direction instead.
2. Inset: 1.55 cm, not 2 cm. At this floor scale the only light, uncovered corner of the lone scene that keeps both kerbs in frame is the top-right corner beyond the door wall (0.7 m of floor, 1.7 cm); a 2 cm inset covers the right kerb. Alternatives: raise the lone crop (taller rows) or drop the floor scale.
3. Lone scene omits the neighbours' 17.5 N partner arrow (spec lists drive, wall, ORCA), so the wall arrow is 13 % longer than the drive arrow. Add a small partner arrow?
4. "Added drive" still has a 0.53 J dimple (check fails strictly); keep the drawn ribbon and mention it in the text, or choose another lone snapshot whose stuck-alone margin with the ORCA drive is negative.
5. Lone ribbon minimum is 1.9 cm from the frozen ball (neighbour push); alternative: include the pinned neighbours in the lone ribbon (minimum at the frozen position, barrier 21.2 J).
6. Pair discs are dark navy (margin -85 / -93 N), so the pair labels sit on the grey lobes and the pale floor, not on the discs.
