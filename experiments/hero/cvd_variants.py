"""Greyscale, deuteranopia and protanopia versions of a compiled PNG (run with the figures venv: .venv/bin/python).

    .venv/bin/python experiments/hero/cvd_variants.py figures/hero/mock_v2/fig1_mock_v2.png
Writes <stem>_grey.png, <stem>_deuteranopia.png, <stem>_protanopia.png next to the input (severity 100, Machado et al.).
"""
import sys
from pathlib import Path

import numpy as np
from colorspacious import cspace_convert
from PIL import Image

src = Path(sys.argv[1])
rgb = np.asarray(Image.open(src).convert("RGB")) / 255.0
outs = {"grey": np.dstack([0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]] * 3)}
for label, name in (("deuteranomaly", "deuteranopia"), ("protanomaly", "protanopia")):
    outs[name] = np.clip(cspace_convert(rgb, {"name": "sRGB1+CVD", "cvd_type": label, "severity": 100}, "sRGB1"), 0, 1)
for k, a in outs.items():
    Image.fromarray((a * 255 + 0.5).astype(np.uint8)).save(src.with_name(f"{src.stem}_{k}.png"))
    print(src.with_name(f"{src.stem}_{k}.png"))
