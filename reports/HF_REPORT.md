# HF report: hero final (Fig 1)
Final render and overlay are in; the paper includes them. Pushed at cea770e, CI (paper and tests) green. Awaiting Palaash's last look.

## The five changes
1. Both lone ribbons include the pinned neighbours' push (own drive = own drive + push; added drive = that + ORCA rest drive, so they differ only by ORCA). Black ball at the frozen position on both; scale 35 J/cm; band at k_BT_eff = 10.22 J (0.48 of the barrier); drawn range x = 9.54-10.00 m.
2. Lone arrows stacked on the door axis: drive 131.2 N (black), push 17.5 N (grey #777777, from the drive tip), ORCA 135.4 N (blue, from the push tip); wall 148.6 N downward = drive + push. One force scale, white under-stroke kept.
3. Labels beside their objects ("held alone" at the agent's upper-left rim, "drive", "ORCA"); still 17 at 6.5 pt; no collision at 900 px in colour, grey, deuteranopia, protanopia, nor at print size.
4. Pair panel on the lone scene's near edge, camera and scale (kerbs at the same height), headroom cropped (2.65 vs 3.65 cm); figure 7.44 -> 6.45 cm tall; "held together" 1.0 cm above the members.
5. 100 N bar (parallel to the door axis) and 0.5 m bar separated by 0.28 cm; no L.

## Ribbon checks (data/derived/hero/hero_physics.json)
- Own-drive minimum at x = 9.660105 m, 0.39 um from the frozen position (limit 1 mm). Own-drive barrier 21.27 J (gate "frozen" 21.21 J; alone 27.96 J, gated 27.90 J, the one quoted in the text).
- Added drive: no stationary point (min force +14.7 N, no sign change).
- Force match along x = 9.54-10.00 m (48 points): own drive vs C1 3.4e-10 N, added drive vs C3 rvo2 3.4e-10 N (limit 1e-6 N). The range starts at 9.54 m because left of it ORCA's neighbour constraints make the full C3 force smaller than the ribbon's (v2 drew from 9.45 m).

## Render
- 2882 x 1523 px (600 dpi at 12.2 cm), 128 samples, denoise on, Blender 5.2.2 -t 2, Metal GPU, tile 256, persistent data off; four panels in separate runs, assembled.
- Gate 3.5 GB (4.3 GB free at start). Render 124 s (wall 144 s). Peak memory per panel 3.14-3.61 GB (max 3.61 GB, rib_lone); swap 647 -> 1215 MB (< 2 GB), so no pause was needed.
- Queue pause: one accidental 1 s pause, 2026-11-08 21:10:17-21:10:18 (the first attempt failed on a missing CLI argument; SIGCONT sent at once). Queue PID 3074 never killed, running.

## Paper
- Fig 1 environment now uses figures/fig1_hero.png + figures/fig1_overlay.tex; `make paper` and `make submission` green (17 pages; the latexpand `\overlayfile` notice is benign, the overlay is inlined). Fig 1 is on page 2, full text width, 12.2 x 6.45 cm.

## Paths
figures/fig1_hero.png, figures/fig1_overlay.tex, figures/fig1_caption.tex, figures/fig1_hero.json, figures/hero/fig1_overlay.json, figures/hero/STORYBOARD.md, figures/hero/final_render.log, figures/hero/final_selfcheck/ (900 px check, CVD variants, page_fig1.png), experiments/hero/{final.sh,render_hero.py,hero_phys.py,export_hero.py}, tools/make_fig1_overlay.py, data/derived/hero/.

[NEEDS PALAASH: last look at the final Fig 1]
