"""QA for a figure PDF: python tools/qa_figs.py <name>   (use .venv/bin/python)

Renders figures/<name>.pdf at 300 dpi into figures/_qa/ as original, greyscale,
deuteranopia and protanopia PNGs, then reports non-embedded fonts (pdffonts),
the smallest text size and the minimum line width found in the PDF content.
"""
import re
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np
from colorspacious import cspace_convert
from PIL import Image  # installed with matplotlib

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
QA = FIG / "_qa"


def render(name):
    QA.mkdir(exist_ok=True)
    subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile",
                    str(FIG / f"{name}.pdf"), str(QA / f"{name}")], check=True)
    rgb = np.asarray(Image.open(QA / f"{name}.png").convert("RGB")) / 255.0
    outs = {}
    grey = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2])
    outs["grey"] = np.dstack([grey] * 3)
    for label in ("deuteranomaly", "protanomaly"):
        sim = cspace_convert(rgb, {"name": "sRGB1+CVD", "cvd_type": label, "severity": 100}, "sRGB1")
        outs["deuteranopia" if label.startswith("d") else "protanopia"] = np.clip(sim, 0, 1)
    for k, a in outs.items():
        Image.fromarray((a * 255 + 0.5).astype(np.uint8)).save(QA / f"{name}_{k}.png")
    return [QA / f"{name}.png"] + [QA / f"{name}_{k}.png" for k in outs]


def fonts(name):
    out = subprocess.run(["pdffonts", str(FIG / f"{name}.pdf")], capture_output=True, text=True,
                         check=True).stdout.splitlines()[2:]
    bad = [ln for ln in out if len(ln.split()) >= 5 and ln.split()[-5] != "yes"]
    return len(out), bad


def content_streams(pdf):
    data = pdf.read_bytes()
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        raw = m.group(1)
        try:
            yield zlib.decompress(raw).decode("latin-1")
        except Exception:
            continue


def text_and_lines(name):
    sizes, widths = [], []
    for s in content_streams(FIG / f"{name}.pdf"):
        if "BT" not in s and " w\n" not in s and " w " not in s:
            continue
        for m in re.finditer(r"/\S+ ([\d.]+) Tf", s):
            sizes.append(float(m.group(1)))
        for m in re.finditer(r"([\d.]+) w\b", s):
            widths.append(float(m.group(1)))
    widths = [w for w in widths if w > 0]  # w=0 marks fill-only patches
    return sizes, widths


def main(name):
    paths = render(name)
    n, bad = fonts(name)
    sizes, widths = text_and_lines(name)
    print(f"{name}: {n} fonts, non-embedded: {bad or 'none'}")
    print(f"smallest text size: {min(sizes):.2f} pt" if sizes else "no text sizes found")
    print(f"minimum line width: {min(widths):.2f} pt" if widths else "no line widths found")
    print("PNGs:", *paths, sep="\n  ")


if __name__ == "__main__":
    main(sys.argv[1])
