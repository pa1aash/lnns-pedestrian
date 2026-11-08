"""Check that every label of the compiled Fig. 1 sits on light pixels of the render (dark text on light areas only).

    python3 tools/check_fig1_labels.py figures/hero/mock/fig1_mock.pdf figures/hero/mock/fig1_hero_mock.png

Word boxes come from pdftotext -bbox; the luminance is read from the render (which carries no text).
Prints the mean and 5th-percentile luminance under each word; flags mean < 0.70 or p5 < 0.45.
"""
import re
import subprocess
import sys

import numpy as np
from PIL import Image

pdf, png = sys.argv[1:3]
txt = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
page = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', txt)
pw, ph = float(page.group(1)), float(page.group(2))
im = np.asarray(Image.open(png).convert("RGB"), float) / 255.0
lum = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
H, W = lum.shape
img_h_pt = pw * H / W
bad = 0
for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', txt):
    x0, y0, x1, y1 = map(float, m.groups()[:4])
    top = ph - img_h_pt
    xa, xb = int(x0 / pw * W), int(x1 / pw * W) + 1
    ya, yb = int((y0 + 1.2 - top) / img_h_pt * H), int((y1 - 1.2 - top) / img_h_pt * H) + 1   # glyph body, not the line box
    reg = lum[max(ya, 0):max(yb, 1), max(xa, 0):max(xb, 1)]
    if reg.size == 0:
        print("%-10s outside the image" % m.group(5))
        continue
    mean, p5 = reg.mean(), np.percentile(reg, 5)
    flag = "" if (mean >= 0.70 and p5 >= 0.45) else "   <-- check"
    bad += bool(flag)
    print("%-10s mean %.2f  p5 %.2f%s" % (m.group(5), mean, p5, flag))
print("flagged words:", bad)
