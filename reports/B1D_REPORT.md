# B1D report: Table 2 and the hero pipeline (2026-11-07)

## Table 2
- `paper/tables/table2_signatures.tex`: 5 classes (P, L, T, D, N) × 7 probes on a frozen state, at LNCS width (tabularx).
  - It compiles with no overfull boxes and has a two-sentence caption. It is not yet `\input`; main.tex needs `\usepackage{booktabs,tabularx}`.
- `paper/tables/table2_NOTES.md` gives the plan line behind each cell (FINAL_PLAN §9, lines 240–280; T3 lines 208 and 210).
  - Cells are direct, follow from the class definition, or are inferred by contrast with the N row. Cells with no plan prediction are "---".
- Correction to the brief: for T at fixed per-step noise, the rate **falls** as Δt grows, because k_BT_eff ∝ 1/Δt (T3, S1 ℓ > 0). The brief's example said "rises".
- [NEEDS PALAASH] Keep the inferred "persists" cells for L, T and D under corrected numerics, or replace them with ---.

## Snapshots (pilot)
- **Lone trap:** `wave2/data/library/C1_w0.8_seed108.pkl` (published mode, 0.8 m, t = 150.8 s, 3 residual agents).
  - The blocker (id 58, r = 0.292 m) sits on the axis 0.27 m before the door plane, with margin +94.6 N (g_max 263.1 N vs drive 168.5 N); |v| = 2.8e-7 m/s.
  - Why this one: an on-axis blocker with a clear positive margin. Of its two jamb-face neighbours, one would pass alone (−35.5 N), which shows that the margin, not mere presence, sets the trap.
  - Check: the on-axis maximum of the floor grid is 155.64 N, equal to Passability.gmax(0.25) = 155.65 N.
- **Pair:** `wave2/data/library/w25_B0.04_seed43.pkl` (from a4_selected_snaps; B_w = 0.04 m, corrected numerics).
  - Symmetric to within 1 mm; both members pass alone (−98.7 N and −82.9 N).
  - Fold from a5_predict: held at b = 0.01, freed at b = 0.03, so b = 0.03 is used.
  - The bias potential freezes e⊥ at the snapshot. Its residual |F_code + ∇U_b| is at most 0.68 N; at b = 0 the residual is 1.4e-7 N. One deep-overlap check point, where the code clamps at 1e6 N, was skipped.

## Curvature check (pair, b = 0)
- The recomputed 4×4 Hessian matches the stored A3 eigenvalues exactly: 84.95 / 1124.32 / 3191.74 / 3285.39 N/m.
- Lateral 2×2, from a quadratic fit on a 1 mm stencil:
  - x held fixed: 85.52 / 1128.73 against the H lateral block 85.18 / 1124.83 (+0.4%);
  - x relaxed: 85.30 / 1128.40 against the Schur complement 84.95 / 1124.49 (+0.4%).
- Strict minimum confirmed on both surfaces.
  - The relaxed b = 0 grid (±0.5 m, 101²) has exactly one non-escaped interior minimum, the snapshot. Its grid barrier to the escape channel is 0.29 J (T5's inferred effective barrier is ≈ 0.8 J).
  - At b = 0.03 the relaxed grid has no interior minimum and a barrier of 0, so the fold is reproduced. The x-fixed slice keeps a minimum at b = 0.03; the fold needs x to relax.

## Previews (figures/hero/storyboard/)
- `option_A.png` (12.2 × 5.4 cm), `option_B.png` (× 4.6), `option_C.png` (× 7.6), each with a `_checks.png` (grey, deutan, protan). Details and captions are in `figures/hero/STORYBOARD.md`.
- **Recommendation: C**, which shows a yellow blocker held alone beside two blue pair members that would each pass alone, plus the landscape before and after the fold. A is the fallback if pages are tight; avoid B.
- [NEEDS PALAASH: pick a storyboard option]

## Resource use
- Export (plan venv, one process): 300–430 s wall time for each full run (the pair grids take ≈ 2.5 min each), peak 97 MB. Ran three times.
- Blender 5.2.2 with `-t 2`, Metal GPU, one process at a time. The first run took 479 s to compile the Metal kernels once.
  - Previews at 900 px and 32 samples: A 9.2 s, B 6.9 s, C 13.7 s of render time (14–21 s wall), peak 2.3–2.4 GB.
- Committed data: data/derived/hero 4.2 MB; storyboard 1.8 MB. Nothing was written into the plan root (PYTHONDONTWRITEBYTECODE=1).

## Next
- Production: switch LONE_SNAP to an E1b corrected-forward snapshot, re-export, then render the chosen option at `--width-px 2882` with more samples.
