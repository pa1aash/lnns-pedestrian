"""Write 256-entry sRGB lookup tables for the hero render (Blender's Python has no Matplotlib).

    /Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python experiments/hero/make_luts.py

Ramps (all perceptually uniform in lightness, colour-vision-deficiency safe, monotone in grey):
  cividis  - agents, stuck-alone margin (blue: passes alone, yellow: held alone)
  magma_r  - floor wall force and pair energy (light: weak, dark: strong); trimmed so the
             top end stays a dark purple rather than black
  viridis, inferno_r, greys - alternatives for the ramp parameter of render_hero.py
"""
from pathlib import Path

import numpy as np
from matplotlib import colormaps

OUT = Path(__file__).resolve().parents[2] / "data" / "derived" / "hero" / "luts.npz"
t = np.linspace(0, 1, 256)
luts = {
    "cividis": colormaps["cividis"](t)[:, :3],
    "viridis": colormaps["viridis"](t)[:, :3],
    "magma_r": colormaps["magma_r"](0.0 + 0.85 * t)[:, :3],
    "inferno_r": colormaps["inferno_r"](0.0 + 0.85 * t)[:, :3],
    "greys": colormaps["Greys"](0.05 + 0.85 * t)[:, :3],
}
OUT.parent.mkdir(parents=True, exist_ok=True)
np.savez(OUT, **luts)
print(OUT, {k: v.shape for k, v in luts.items()})
