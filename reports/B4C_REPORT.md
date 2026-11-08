# Batch 4C report: Fig 2 fixes, hero mock, page check

**Actions.** All ten latest runs (back to the E3/E4 selection commit) succeeded, including ede944f (tests 3m18s, paper 1m53s). Runs for 515e765 (hero commit): tests and paper both succeeded.

**Fig 2 (c64b8d3).** Left x range trimmed to -0.6 to 0.05 m; right-panel margin map blended at 38 % over white so the 20 000 agents (dark grey, 0.5 pt, alpha 0.45) read over both regions; the C3 rest-state band is two blue boundary lines with no fill; curves, drive bands, black C1 boundary unchanged. QA: fonts embedded, smallest text 5.98 pt, minimum line 0.60 pt; original, greyscale and deuteranopia views checked. The Fig 2 caption now says "two blue lines".

**Hero snapshots.** Lone: E1b seed 52 (blocker 19, margin +146.2 N, neighbours 38 and 54 pass alone). Pair: `E7b_B0.04_seed397` (members 81 and 35, margins -84.7 / -92.8 N, mean offset -0.008 m). Chosen from the 25 near-symmetric two-agent E7b snapshots as the best stiffness match to the pilot seed 43 (Hessian 82.7 / 1095 / 3077 / 3227 against 85 / 1124 / 3192 / 3285 N/m); fold b = 0.0315, inside the pilot's bracket. Seed 276 is slightly closer in position but 20 % softer.

**Physics checks** (`data/derived/hero/hero_physics.json`).
- C1 force balance: 2.3e-4 N (lone set), 4.2e-4 N (pair); limit 0.1 N. Blocker at rest: drive 131.2 N, wall 148.6 N, partners push 17.5 N, ORCA rest drive 135.4 N.
- Lone own drive: one minimum (x = 9.6412) and one barrier (9.9498), 27.96 J; gated alone barrier 27.90 J (0.23 %, same positions).
- FAILS: the minimum is 1.9 cm (0.16 J) behind the frozen position, because the neighbours' 17.5 N push belongs to the frozen balance (with them pinned, the barrier is 21.2 J).
- FAILS strictly: "added drive" keeps a 0.53 J dimple (x = 9.791, rim 9.863; margin with the ORCA rest drive is +10.8 N). At 30 J/cm it is 0.2 mm; the ball starts 6.6 J above the rim.
- k_BT_eff = 10.22 J at sigma = 0.07 m/s (0.37 of the barrier); sigma = 0.07 reproduces C3 RVO2 (0.871 against 0.882).
- Pair: strict minimum at b = 0 (all Hessian eigenvalues positive, ribbon minimum at c = 0, barriers 0.41 J); the tilted ribbon (b = 0.035) has no minimum. The code's relaxation holds at b = 0.028 and frees at 0.035.
- Inset: 100 initial positions rebuilt with the simulator (seed 52, CF flags); radius, v0, tau of the three residual agents match the snapshot exactly.

**Mock** (900 px, 24 samples, 8 s, Metal): `figures/hero/mock/fig1_mock.pdf` and `fig1_mock.png`, plus `fig1_mock_{grey,deuteranopia,protanopia}.png`. Spec and honesty note: `figures/hero/STORYBOARD.md`. Labels are all on light pixels (`tools/check_fig1_labels.py`). `paper/main.tex` builds the figure from the mock image. No 2882 px render was made.

**Open choices for Palaash** (details in STORYBOARD.md).
1. The yellow lateral-bias arrow is 4.6 N = 0.4 mm at the common scale (a dot): keep, exaggerate x10 with a stated factor, or show the tilted direction.
2. The inset is 1.55 cm, not 2 cm: a 2 cm inset would cover the right kerb (the only free corner is beyond the door wall).
3. The lone scene omits the 17.5 N partner arrow, so the wall arrow is 13 % longer than the drive arrow.
4. The two failed ribbon checks above: keep and state in the text, or pick another lone snapshot / include pinned neighbours.
5. Arrow scale: 100 N = 7.95 mm horizontally (12.6 N/mm), 7.2 mm along the door axis.

**Page check** (5 pages, figures on pages 2-5; Fig 1 12.2 x 7.4 cm, Fig 2 12.2 x 4.9, escape 12.2 x 5.4, Delta t 5.9 x 5.6, quench 12.2 x 6.4). All legible at print size. Fixes (not applied; other sessions' figures):
1. Numbers read Fig 3-5 for the escape, Delta t and quench figures; the plan wants 4-6, so Fig 3 (completion vs width) is still missing, and no Fig 7-8 yet.
2. Frame style differs: Fig 2 is boxed, the others open; use one.
3. Smallest text is 5.98 pt in Fig 2 and the escape figure (7.0 pt in the other two); raise the shared tick size to 7 pt in `style.mplstyle`.
4. Line weights differ (0.4-0.6 pt minimum, curves 0.9-1.2 pt); set one weight for curves and one for frames.
5. The Delta t figure is half width and left-centred; widen it or pair it with a panel.
6. The quench figure has 16 rotated 7 pt category labels; group or shorten them.
7. Colours are consistent (noise vermillion, C3 RVO2 blue, C1 black); captions are two sentences but 6-8 lines each, so the colour keys could move into the text.
8. The hero mock image is 187 ppi; the production render replaces it.

[NEEDS PALAASH: go-ahead or changes on the hero mock]
