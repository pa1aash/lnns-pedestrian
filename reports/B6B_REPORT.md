# B6B report: Fig 3 (E7) and figure polish

## Hero sliver (STEP 1, done before the power loss; commit 15fab97)
- Cause: floor-field texels peeking out at the blocker's door-line corners behind the disc silhouette. Fix is a soft mask in experiments/hero/render_hero.py; no field value changed elsewhere.
- Lone panel re-rendered at tile 256, -t 2, Metal; overlay anchors unchanged.
- Pause log: the queue (PID 3074) was stopped and resumed around that render. The exact timestamps were lost in the power loss and are not in any log I can find. Now confirmed by ps: queue workers are in state S, none in T.

## Figs 6 and 7 (STEP 2, commit 505d12d)
- Each 0.6 cm shorter, widths and style kept; smallest text 6.97 pt.

## E7 (900/900; 100 runs per cell, CF, C1, seeds 42-141, 600 s; data/E7, data/derived/E7_analysis.json)
Completion (Wilson 95%) / deadlocks by class (lone = lone keystone + with second trap; coll = collective):
- w=0.7 default walls: 0/100 [0.00,0.04]; 100 lone, 0 coll
- w=0.8 default (E1b): 2/100 [0.01,0.07]; 96 lone, 2 coll (98 deadlocks)
- w=0.9: 70/100 [0.60,0.78]; 30 lone, 0 coll
- w=1.0: 100/100 [0.96,1.00]; no deadlocks
- all walls B_w=0.04: 85/100 [0.77,0.91]; 1 lone, 14 coll
- all walls B_w=0.02: 83/100 [0.74,0.89]; 0 lone, 17 coll
- jambs only 0.04: 89/100 [0.81,0.94]; 0 lone, 11 coll
- rounded edge: 7/100; 93 lone, 0 coll
- line goal: 3/100; 94 lone, 3 coll
- line + rounded: 9/100; 91 lone, 0 coll
- Critical width (logistic fit, default walls): 0.88 m (bootstrap 95% 0.87-0.89); linear interpolation 0.87 m.
- Locality: jamb-only vs all-walls 0.04 completion 89 vs 85, p=0.529 (no difference); jamb-only vs default p=3.5e-41. Collective share of deadlocks: 2/98 default vs 11/11 jamb-only (p=2.0e-13).
- Deadlock time, median: 155 s default, 130 s at w=0.9, 136 s jamb-only (runs are stopped when the deadlock is detected).
- Keystone surgery: 2 workers, 908 + 287 jobs, all classified.

## Fig 3 and section 5.1
- QA (tools/qa_figs.py fig3_width_walls): fonts embedded, smallest text 6.97 pt, min line 0.50 pt; viewed at 200 dpi, no collisions. Left panel completion vs w with Wilson CIs; right panel points with CIs plus outcome bar (white completed, light grey pair/group standoff, dark grey lone trap); caption is two sentences.
- E7 paragraph is about 17 lines (about 0.33 page) plus the figure (about 0.35 page) on p. 10-11. All numbers are macros from paper/registry/e7.yaml (32 macros).
- Build: make numbers, make paper, make submission OK (23 pages, 0 undefined, 8 \pending left, none from me).
- Analysis script writes cell names with "p" for dots (B0p04) because registry key paths split on dots.

## Proposed changelog text (E7)
C-E7: Fig 3 and the section 5.1 paragraph now report E7. Critical width at default walls is 0.88 m; the trap disappears with a short-range jamb wall law (B_w 0.04 m or 0.02 m, all walls or jambs only: 83-89% completion against 2%), is unchanged by rounded corners or a line goal (3-9%), and its residual deadlocks are collective pair standoffs (42 of 43) instead of lone traps. The wall-model assumption is therefore a first-order driver of the corrected-forward deadlock rate.

## [NEEDS PALAASH]
- Confirm CI green for the final push (runs were queued when I wrote this; paper CI was green on the earlier pushes).
- Hero pause timestamps are unrecoverable; decide if that matters.
- Interpretation: the jamb range, not the whole wall set, is the lever; the 0.88 m critical width is for the default law only. Check that this framing matches §1 and §6.
