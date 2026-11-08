"""Print-legibility and colour-vision checks of the storyboard previews.

    /Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python experiments/hero/check_previews.py [image.png ...]

For each figures/hero/storyboard/option_*.png writes a contact strip
option_*_checks.png: original | greyscale (Rec. 709 luma) | deuteranopia | protanopia
(Machado, Oliveira & Fernandes 2009, severity 1.0, applied in linear RGB), and prints the
luma of each ramp's ends and of the cividis agent colours actually used.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SB = ROOT / "figures" / "hero" / "storyboard"
LUTS = np.load(ROOT / "data" / "derived" / "hero" / "luts.npz")

MACHADO = {
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
}


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


def luma(rgb):
    return rgb @ np.array([0.2126, 0.7152, 0.0722])


def main():
    import sys
    paths = [Path(x) for x in sys.argv[1:]] or sorted(SB.glob("option_[A-Z].png"))
    for p in paths:
        im = np.asarray(Image.open(p).convert("RGB"), float) / 255
        grey = np.repeat(srgb(luma(lin(im)))[..., None], 3, axis=2)
        sims = [srgb(lin(im) @ M.T) for M in MACHADO.values()]
        strip = np.concatenate([im, grey] + sims, axis=1)
        Image.fromarray((strip * 255).round().astype(np.uint8)).save(p.with_name(p.stem + "_checks.png"))
        print(p.name, "->", p.stem + "_checks.png")
    for name in ("cividis", "magma_r"):
        L = LUTS[name]
        print(name, "relative luminance at 0, 0.5, 1:", np.round(luma(lin(L[[0, 127, 255]])), 3),
              "monotone:", bool(np.all(np.diff(luma(lin(L))) >= 0) or np.all(np.diff(luma(lin(L))) <= 0)))


if __name__ == "__main__":
    main()
