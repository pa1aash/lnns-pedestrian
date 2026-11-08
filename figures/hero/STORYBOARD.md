# Hero figure (Fig. 1): production state (batch 3B)

Option C was chosen and is now rendered at production quality: `figures/fig1_hero.png` (2882 × 1631 px, 600 dpi at 12.2 cm → 12.2 × 6.9 cm, 128 samples, denoised).
Pipeline: `experiments/hero/export_hero.py` → `data/derived/hero/*.npz` → `experiments/hero/render_safe.sh` (memory-gated wrapper around `render_hero.py`, Blender headless, `-t 2`, Metal GPU). Previews: `--width-px 900 --samples 32`. The caption is in `paper/main.tex` (Fig. 1 environment). The A/B/C sections below are the earlier pilot storyboard and are kept for the record; only C was built, with the changes listed here (C17).

## Production layout
- **Top row:** the lone trap. **Bottom row:** the pair standoff (left), and its landscape before (upper right) and after (lower right) a lateral bias past the fold.
- **One floor scale.** Both floor scenes use an orthographic camera at the same elevation (40°) and the same 847.6 px per metre; the pair panel is a narrower crop of the same view of the same door. A metre has the same length in both.
- **Landscapes at true aspect.** Horizontal axes are the common shift c = (dy_lo + dy_hi)/2 and the opposed shift o = (dy_hi − dy_lo)/2 of the two members, in metres, on one horizontal scale (c within ±0.30 m, o within ±0.04 m; the valley is only about ±0.03 m wide at the clip). No ×3 stretch, full symmetric opposed range. Height is linear in U with one scale, 0.12 m of drawn height per joule, clipped to [−1.2, 0.6] J; colour is the same U, magma_r over the same window. The black sphere is the frozen state. The valley is narrow because λ1 ≈ 85 N/m (common) against λ2 ≈ 1124 N/m (opposed).
- **Encodings shared with Fig. 2.** Agent stuck-alone margin: cividis over ±150 N. Wall force: magma_r on a log scale, 1–1000 N. Each agent cylinder has a thin dark edge (8 mm) so light agents separate from a light floor. Light-grey strips along walls are the cells where a 0.25 m probe disc would overlap the wall. No text in the image.

## Snapshots used
- **Lone trap:** `data/E1/library/E1b_seed52.pkl` (E1b corrected-forward, class `lone_keystone`, w = 0.8 m, t = 150.9 s, wall B_w = 0.08 m, convex-union corner rule). Three residual agents. The blocker (id 19, r = 0.296 m) sits on the axis 0.34 m before the door plane with margin **+146.2 N**, below the ±150 N ramp end, so it is not clipped. The two other residual agents (ids 38 and 54) would each pass alone, with margins −9.6 N and −41.6 N. This is the closest match to the pilot seed108 (one held blocker, two passable neighbours) with a clearly positive margin. Seeds 61 (+114.0 N, four residuals) and 128 (+187.6 N, past the ramp) were considered and rejected.
- **Pair:** pilot snapshot `wave2/data/library/w25_B0.04_seed43.pkl` (B_w = 0.04 m, segment-sum corner rule), margins −98.7 N and −82.9 N, λ1 = 84.95 N/m, fold at b = 0.03 (held at b = 0.01).
- **Pending pair swap.** The production pair library (corrected-forward, B_w = 0.04) is still being built by the queue. The swap is one line: `PAIR_SNAP` in `experiments/hero/export_hero.py`; then re-run `export_hero.py --only pair` and `render_safe.sh`. Check on swapping that the corner rule in the caption's wall laws still reads correctly (the pilot pair uses segment-sum, the lone uses convex-union), and that the fold bias and the window c ±0.30 m, o ±0.04 m still show the dimple and both escapes.

## Checks (export_report.json)
- Lone floor on-axis maximum 155.638 N against Passability g_max(0.25 m) = 155.648 N (the 1 cm grid step); pair floor 17.404 against 17.418 N.
- Lone blocker margin equals `E1_keystone.json` (146.211 N, difference 3e-10 N, same blocker id and class).
- Pair landscape: strict minimum at b = 0 (relaxed and slice, Hessian eigenvalues 84.95 and 1124.5 N/m); no local minimum of the relaxed landscape past the fold; escape barrier 0.293 J at b = 0 and 0 at the fold; |F_code + ∇U| ≤ 0.68 N.

## Honesty note for the text
- The model is 2-D. Agent height (0.20 m) and wall height (0.42 m) are arbitrary, and walls are drawn 3 cm thick around zero-thickness segments.
- Landscape height is a stylised vertical scale (0.12 m per J), linear in U but clipped to [−1.2, 0.6] J, so the walls of the valley and the deep escape basins are flat. The dimple is 0.29 J deep (grid estimate of the escape barrier) against the 1.8 J window.
- The landscape is the rest-state energy with density frozen and the forward positions relaxed (within ±0.3 m), over a rectangle of the common and opposed lateral shifts of the two members, drawn at true 1:1 aspect in metres. The lone and pair scenes use different wall laws (B_w = 0.08 and 0.04 m), stated in the caption.
- The floor ramp is for a lone 0.25 m probe at rest, not for the agents drawn on it.
- The oblique 3-D view hides part of the near half of the valley; the far half and the ramp show it.

---
# Earlier pilot storyboard (pre-C17)


Pilot data. Previews are 900 px wide with 32 samples; the final render is 2882 px wide (600 dpi at 12.2 cm).
Pipeline: `experiments/hero/export_hero.py` → `data/derived/hero/*.npz` → `experiments/hero/render_hero.py` (Blender, headless) → `figures/hero/storyboard/option_{A,B,C}.png`.
`render_storyboard.sh` renders all three. `option_*_checks.png` shows each preview as original | greyscale | deuteranopia | protanopia.

## What is drawn (common to all options)

- **Lone trap.** Snapshot `wave2/data/library/C1_w0.8_seed108.pkl` (published mode, w = 0.8 m, t = 150.8 s), three residual agents.
  - The blocker (id 58, r = 0.292 m) sits on the axis 0.27 m before the door plane, with a stuck-alone margin of +94.6 N (g_max 263.1 N against a drive of 168.5 N).
  - The two others rest against the jamb faces, with margins +51.5 N and −35.5 N.
- **Pair.** Snapshot `wave2/data/library/w25_B0.04_seed43.pkl` (corrected numerics, B_w = 0.04 m on all walls).
  - Both members would pass alone: margins −98.7 N and −82.9 N.
  - λ1 = 84.9 N/m (the 26-snapshot median is 89).
  - The static relaxation holds the pair at b = 0.01 and frees it at b = 0.03; b = 0.03 is used.
- **Floor.** The backward wall force on a lone r = 0.25 m agent at rest, from the model's own `WallForces`.
  - On a log scale, 1–1000 N, using magma (light = weak, dark = strong).
  - Grid cells where the probe disc would overlap a wall are light grey.
- **Agents.** Cylinders at their true radius, coloured by stuck-alone margin on a cividis ramp from −150 N (blue: passes alone) to +150 N (yellow: held alone).
- **Landscapes.** Rest-state U with density frozen and the forward positions relaxed (minimised within ±0.3 m), shown against the common lateral shift (left → right).
  - The opposed shift runs into the depth, with only o ≥ 0 shown, so the front edge is the valley-floor profile. The depth axis is stretched ×3.
  - Height and colour are both linear in U and clipped to [−1.2, 1.0] J. The black sphere is the frozen state.
- **No text** of any kind. The two thin dark rods at the base of each landscape are its axes.

## Option A: two panels (12.2 × 5.4 cm)
Oblique lone-trap scene on the left; the pair landscape before the fold (top right) and after it (bottom right), with the same camera and scale.
- **5 s read:** one agent is held at the door by a dark force band at the jambs; a ball rests in a dimple that disappears once a bias is added.
- **Colours:** as above.
- **Caption:** "Left: a lone-agent trap frozen at a 0.8 m door, agents drawn at their true radius on the map of the backward wall force felt by a lone 0.25 m agent; right: rest-state energy of a symmetric pair standoff against the common (left to right) and opposed (depth) lateral shifts of its members, without bias (top) and with a lateral bias just past the fold (bottom), the sphere marking the frozen state. Agents are coloured by stuck-alone margin (blue passes alone, yellow is held alone; ±150 N), the floor by wall force (log, 1–1000 N) and the landscapes by energy (−1.2 to 1.0 J), light to dark."
- **Risks:**
  - The pair's physical configuration is not shown, so "lateral shift" stays abstract.
  - The floor band is thin at this camera height.

## Option B: one continuous scene (12.2 × 4.6 cm)
A single stage seen from the room: the lone-trap scene on the left, with both landscapes standing on the same ground to its right under one light and one camera.
- **5 s read:** the same as A, but read as one object row from left to right (trap, then before, then after).
- **Colours:** as above.
- **Caption:** "One scene showing, from left to right, a lone-agent trap frozen at a 0.8 m door on the map of the backward wall force felt by a lone 0.25 m agent, then the rest-state energy of a symmetric pair standoff against the common (left to right) and opposed (depth) lateral shifts of its members without bias and with a lateral bias just past the fold, the sphere marking the frozen state. Agents are coloured by stuck-alone margin (blue passes alone, yellow is held alone; ±150 N), the floor by wall force (log, 1–1000 N) and the landscapes by energy (−1.2 to 1.0 J), light to dark."
- **Risks:**
  - It is the shortest option, but the floor is seen at a grazing angle, so the force field is compressed.
  - Standing the landscapes on the room floor suggests they share its spatial axes, which they do not. This is the most misleading of the three.

## Option C: two rows (12.2 × 7.6 cm), my alternative
Top: a wide lone-trap strip. Bottom: the pair standoff in its own geometry on the same floor ramp, then its landscape before and after the fold.
- **5 s read:** the yellow agent is held alone at the door. The two blue agents would each pass alone, yet hold each other in a dimple, and a bias tilts the dimple away. This is the paper's two-class thesis in one glance.
- **Colours:** as above. The two floors share one ramp, so the shorter-range jamb force of the pair geometry is visibly narrower.
- **Caption:** "Top: a lone-agent trap frozen at a 0.8 m door with published walls; bottom, left to right: a symmetric pair standoff frozen with short-range walls (B_w = 0.04 m), and its rest-state energy against the common (left to right) and opposed (depth) lateral shifts of the two members, without bias and with a lateral bias just past the fold (sphere: frozen state). Agents are drawn at their true radius and coloured by stuck-alone margin (blue passes alone, yellow is held alone; ±150 N) on the map of the backward wall force felt by a lone 0.25 m agent (log, 1–1000 N), and the landscapes are coloured by energy (−1.2 to 1.0 J), light to dark."
- **Risks:**
  - It is the tallest option (+2.2 cm over A), which costs page budget.
  - The two snapshots come from different wall laws and modes, so the caption must say so (it does).

## Risks common to all options
- **Greyscale print:** both ramps are monotone in lightness (cividis 0.02 → 0.79; magma 0.95 → 0.02). The held blocker prints light on the dark jamb band and the passable agents print dark.
  - However, the agent at +51.5 N prints light on a light floor and relies on its shading edge.
  - The two ramps run in opposite lightness directions (agents light = held, field dark = strong). This is deliberate for contrast, but the caption has to state both.
- **Colour-vision deficiency:** cividis is designed to be CVD-safe, and magma stays ordered under deutan and protan simulation, where it turns blue–yellow. In that simulation the floor's yellow end approaches the agents' yellow, which separate only by shape and shading.
- **Honesty of the stylised height:**
  - The model is 2-D. Cylinder height (0.20 m) and wall height (0.42 m) are arbitrary, and the walls are drawn 3 cm thick around zero-thickness segments.
  - Landscape height is linear in U, but it is clipped, the depth axis is stretched ×3 and only half the opposed range is shown. The dimple is 0.29 J deep (the grid barrier), against a 2.2 J height window. All of this belongs in the text, since the caption is limited to two sentences.
- **Production:** the lone snapshot is swapped for an E1b corrected-forward snapshot (`LONE_SNAP`, then re-export).

## Recommendation
**C.** It is the only option that shows the thesis in the picture: the held-alone yellow blocker beside a pair of blue agents that would each pass alone. It also gives the landscape a physical referent. If the page budget is tight, use **A**. Avoid **B**, because it puts abstract axes on the room floor.
[NEEDS PALAASH: pick a storyboard option]
