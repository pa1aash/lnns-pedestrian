# B3B report: hero figure (Fig. 1) production

**Output:** `figures/fig1_hero.png` (2882 x 1631 px, 12.2 x 6.9 cm at 600 dpi), render metadata `figures/fig1_hero.json`. No PDF wrapper needed; LaTeX includes the PNG. Caption (two sentences) and the Fig. 1 environment are in `paper/main.tex`. `make paper`: 0 errors.

## Snapshots
- Lone trap: `data/E1/library/E1b_seed52.pkl` (E1b corrected-forward, class `lone_keystone`, B_w = 0.08 m, t = 150.9 s). Blocker id 19 on the axis, 0.34 m before the door, margin +146.2 N (inside the +-150 N ramp, not clipped). Neighbours 38 and 54 pass alone (-9.6 N, -41.6 N). Rejected: seed 61 (+114 N, four residuals, clutter), seed 128 (+187.6 N, clipped).
- Pair: pilot `wave2/data/library/w25_B0.04_seed43.pkl` (B_w = 0.04 m, margins -98.7 and -82.9 N). Swap = one line (`PAIR_SNAP`, `export_hero.py`), then re-export `--only pair` and re-render; noted in STORYBOARD.md.

## Checks (data/derived/hero/export_report.json)
- Lone floor on-axis maximum 155.638 N vs Passability g_max(0.25 m) 155.648 N (1 cm grid); pair floor 17.404 vs 17.418 N.
- Lone blocker margin equals E1_keystone.json (146.211 N, diff 3e-10 N; same blocker, same class).
- Pair landscape: strict minimum at b = 0 (eig 84.95, 1124.5 N/m); no local minimum of the relaxed landscape at the fold (b = 0.03); barrier 0.293 J at b = 0; |F_code + grad U| <= 0.68 N.
- Greyscale, deuteranopia, protanopia strips checked (`figures/hero/preview/p14_checks.png`, not committed): blocker is lightest, passable agents dark, edges separate agents from the floor; both ramps monotone in lightness.

## Changes made (C17)
1. One orthographic camera elevation (40 deg) and one scale (847.6 px/m) for both floor scenes.
2. Landscapes at 1:1 in metres, c within +-0.30 m, o within +-0.04 m, no stretch, no half range; height 0.12 m per J, clipped to [-1.2, 0.6] J. The top clip was lowered from 1.0 to 0.6 J so that the near shoulder hides less of the valley.
3. Lone snapshot as above. 4. cividis +-150 N, magma_r log 1-1000 N, dark agent edge.

## Render
- Final: 2882 px, 128 samples, denoised, tile 1024, Metal GPU, `-t 2`. Panels 116.5 / 47.6 / 22.4 / 21.1 s; 207.6 s render, 215 s wall. Peak memory footprint 5.18 GB (previews at 900 px: 2.3 GB). Free memory at start 4.3 GB (gate 2.5 GB).
- Previews: 900 px, 32 samples, about 15 s each.

## Caveats
- The near plateau hides part of the near half of the valley in the oblique view; the clip makes the valley walls flat (stated in STORYBOARD.md).
- The two wall laws differ in corner rule too (lone: convex union; pilot pair: segment sum). The caption gives B_w only; revisit at the pair swap.
- The page-1 skeleton has no abstract yet, so the figure placement is unreviewed.

Files: `experiments/hero/{export_hero,render_hero,check_previews}.py`, `render_safe.sh`, `data/derived/hero/*.npz`, `figures/hero/STORYBOARD.md`.
