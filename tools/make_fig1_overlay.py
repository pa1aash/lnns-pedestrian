"""Turn figures/hero/fig1_overlay.json (3-D anchors projected by render_hero.py) into figures/fig1_overlay.tex.

    python3 tools/make_fig1_overlay.py [--overlay figures/hero/fig1_overlay.json] [--png figures/fig1_hero.png]
                                       [--out figures/fig1_overlay.tex]

The TeX file is a fragment for a TikZ scope whose unit is the image width (x = y = \\textwidth, origin at the
image's lower-left corner): force arrows, coordinate lines, scale bars, labels (8 pt serif, dark text on light
areas, no boxes or halos) and the vector context inset. Nothing here is hand-placed except the label table
below; every arrow, line and bar end point is a projected 3-D anchor.

With --png the script also checks each label against the image: the estimated text box must sit on light
pixels (mean luminance >= 0.75, darkest 5 % >= 0.45); failures are printed.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GREY = "7F7F7F"
C = {"black": "000000", "wall": "51127C", "orca": "0072B2", "partner": "B63679", "bias": "F0E442", "scale": "333333"}
FONT = r"\fontsize{8}{9.5}\selectfont"
CHAR_W_CM = 0.155            # mean advance of 8 pt Computer Modern text, for the box estimate only

# (text, panel, anchor, dx_cm, dy_cm, tikz anchor, colour). Offsets in printed cm; anchors "@tl" etc are panel corners.
LABELS = [
    ("lone trap", "lone", "@tl", 0.10, -0.08, "north west"),
    ("100 N", "lone", "scale100_mid", 0.10, 0.0, "west"),
    ("0.5 m", "lone", "scale_half_m_mid", 0.0, -0.06, "north"),
    ("held alone", "lone", "drive_1", -0.12, -0.02, "east"),
    ("passes alone", "lone", "n54", 0.0, 0.78, "center"),
    ("door", "lone", "door", 0.0, 0.0, "center"),
    ("drive", "lone", "drive_mid", 0.10, 0.0, "west"),
    ("wall", "lone", "wall_1", 0.10, 0.0, "west"),
    ("ORCA", "lone", "orca_mid", 0.10, 0.0, "west"),
    ("own drive", "rib_lone", "curve0_top", 0.0, 0.10, "south"),
    ("added drive", "rib_lone", "base1_0", 0.05, 0.10, "south west"),
    ("noise", "rib_lone", "band_1", 0.0, 0.06, "south"),
    ("10 J", "rib_lone", "scale_mid", 0.10, 0.0, "west"),
    ("pair standoff", "pair", "@tl", 0.10, -0.08, "north west"),
    ("held together", "pair", "between", 0.0, 1.15, "south"),
    ("partner", "pair", "partner_1", 0.40, -0.50, "west"),
    ("tilt", "pair", "bias_1", 0.20, 0.14, "west"),
    ("no tilt", "rib_pair", "curve0_top", 0.0, 0.10, "south"),
    ("tilted", "rib_pair", "base1_0", 0.05, 0.10, "south west"),
    ("0.5 J", "rib_pair", "scale_mid", 0.10, 0.0, "west"),
]


class Ctx:
    def __init__(self, ov):
        self.ov = ov
        self.W, self.H = ov["px"]
        self.asp = self.H / self.W
        self.cm = ov["cm"][0]

    def pt(self, panel, name):
        a = self.ov["panels"][panel]["anchors"]
        if name.startswith("@"):
            x, y, w, h = self.ov["panels_px"][panel]
            u, v = {"@tl": (x, y), "@tr": (x + w, y), "@bl": (x, y + h), "@br": (x + w, y + h)}[name]
            return (u / self.W, (1 - v / self.H) * self.asp)
        if name.endswith("_mid"):
            b = name[:-4]
            p0 = a.get(b + "_0") or a.get(b + "_start")
            p1 = a[b + "_1"]
            return (((p0[0] + p1[0]) / 2), ((p0[1] + p1[1]) / 2) * self.asp)
        u, v = a[name]
        return (u, v * self.asp)

    def off(self, p, dx_cm, dy_cm):
        return (p[0] + dx_cm / self.cm, p[1] + dy_cm / self.cm)


def f(p):
    return "(%.5f,%.5f)" % p


def arrow(c, p0, p1, colour, lw=0.7, halo=True, head_cm=0.16):
    L = math.hypot((p1[0] - p0[0]) * c.cm, (p1[1] - p0[1]) * c.cm)
    h = min(head_cm, max(0.5 * L, 0.03)) if head_cm >= 0.16 else head_cm
    tip = "{Stealth[length=%.3fcm,width=%.3fcm]}" % (h, 0.75 * h)
    out = []
    if halo == "dark":
        out.append(r"\draw[-%s,line width=%.2fpt,color=black] %s -- %s;" % (tip, lw + 0.8, f(p0), f(p1)))
    elif halo:
        out.append(r"\draw[-%s,line width=%.2fpt,color=white,opacity=0.85] %s -- %s;" % (tip, lw + 1.0, f(p0), f(p1)))
    out.append(r"\draw[-%s,line width=%.2fpt,color={rgb,255:red,%d;green,%d;blue,%d}] %s -- %s;" % (
        tip, lw, *[int(colour[i:i + 2], 16) for i in (0, 2, 4)], f(p0), f(p1)))
    return out, L


def bar(c, p0, p1, lw=0.6, tick_cm=0.07):
    dx, dy = (p1[0] - p0[0]) * c.cm, (p1[1] - p0[1]) * c.cm
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * tick_cm / c.cm, dx / L * tick_cm / c.cm
    col = "{rgb,255:red,51;green,51;blue,51}"
    return [r"\draw[line width=%.2fpt,color=%s] %s -- %s;" % (lw, col, f(p0), f(p1)),
            r"\draw[line width=%.2fpt,color=%s] (%.5f,%.5f) -- (%.5f,%.5f);" % (lw, col, p0[0] - nx, p0[1] - ny, p0[0] + nx, p0[1] + ny),
            r"\draw[line width=%.2fpt,color=%s] (%.5f,%.5f) -- (%.5f,%.5f);" % (lw, col, p1[0] - nx, p1[1] - ny, p1[0] + nx, p1[1] + ny)]


def grey_line(c, p0, p1):
    return r"\draw[line width=0.5pt,color={rgb,255:red,127;green,127;blue,127}] %s -- %s;" % (f(p0), f(p1))


def inset(c, d, ov, size_cm=1.55, margin_cm=0.07, label_strip_cm=0.40):
    """Vector context inset in the top-right corner of the lone scene; orientation as in the scene
    (screen right = -y, screen up = +x). The 10 m room fills the square above a label strip."""
    px, py, pw, ph = ov["panels_px"]["lone"]
    right, top = (px + pw) / c.W, (1 - py / c.H) * c.asp
    s = size_cm / c.cm
    m = margin_cm / c.cm
    x1, y1 = right - m, top - m
    x0, y0 = x1 - s, y1 - s
    strip = label_strip_cm / c.cm
    room = s - strip - 2 * 0.04 / c.cm       # room square, 0.4 mm padding inside the border
    k = room / 10.0
    ox = x0 + (s + room) / 2                  # room centred horizontally; screen X = ox - y k
    oy = y0 + strip                           # screen Y = oy + x k
    grey = "{rgb,255:red,64;green,64;blue,64}"

    def S(x, y):
        return (ox - y * k, oy + x * k)
    out = [r"\begin{scope}", r"\fill[white] %s rectangle %s;" % (f((x0, y0)), f((x1, y1)))]
    for (xa, ya, xb, yb) in d["walls"]:
        out.append(r"\draw[line width=0.35pt,color=%s] %s -- %s;" % (grey, f(S(xa, ya)), f(S(xb, yb))))
    for (x, y) in d["initial_positions"]:
        px_, py_ = S(x, y)
        out.append(r"\fill[color={rgb,255:red,190;green,190;blue,190}] (%.5f,%.5f) circle (%.5f);" % (px_, py_, 0.016 / c.cm))
    box = ov["lone_box_m"]
    a_, b_ = S(box["x"][0], box["y"][1]), S(box["x"][1], box["y"][0])
    out.append(r"\draw[line width=0.4pt,color=black] %s rectangle %s;" % (f(a_), f(b_)))
    for r_ in d["residual"]:
        cx, cy = S(*r_["pos"])
        col = r_["colour"].lstrip("#")
        out.append(r"\fill[color={rgb,255:red,%d;green,%d;blue,%d}] (%.5f,%.5f) circle (%.5f);" % (
            int(col[0:2], 16), int(col[2:4], 16), int(col[4:6], 16), cx, cy, max(r_["r"] * k, 0.03 / c.cm)))
    # dimension line with the label for the 10 m side, in the strip
    yl = y0 + strip * 0.5
    xl0, xl1 = ox - 10 * k, ox
    tw = 0.46 / c.cm                           # label width reserved
    xm = (xl0 + xl1) / 2
    tk = 0.03 / c.cm
    for (xa, xb) in ((xl0, xm - tw / 2), (xm + tw / 2, xl1)):
        out.append(r"\draw[line width=0.35pt,color=%s] (%.5f,%.5f) -- (%.5f,%.5f);" % (grey, xa, yl, xb, yl))
    for xt in (xl0, xl1):
        out.append(r"\draw[line width=0.35pt,color=%s] (%.5f,%.5f) -- (%.5f,%.5f);" % (grey, xt, yl - tk, xt, yl + tk))
    out.append(r"\node[anchor=center,inner sep=0pt,font=%s,text=black!85] at (%.5f,%.5f) {10 m};" % (FONT, xm, yl))
    out.append(r"\draw[line width=0.4pt,color=black] %s rectangle %s;" % (f((x0, y0)), f((x1, y1))))
    out.append(r"\end{scope}")
    return out, (x0, y0, x1, y1)


def label_checks(c, labels, png):
    if not png:
        return []
    from PIL import Image
    import numpy as np
    im = np.asarray(Image.open(png).convert("RGB"), float) / 255.0
    lum = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
    H, W = lum.shape
    msgs = []
    for text, p, anchor in labels:
        w = max(len(text), 1) * CHAR_W_CM / c.cm
        h = 0.33 / c.cm
        x0, x1 = {"west": (p[0], p[0] + w), "east": (p[0] - w, p[0]), "south west": (p[0], p[0] + w), "north west": (p[0], p[0] + w)}.get(anchor, (p[0] - w / 2, p[0] + w / 2))
        y0, y1 = {"north west": (p[1] - h, p[1]), "south": (p[1], p[1] + h), "south west": (p[1], p[1] + h)}.get(anchor, (p[1] - h / 2, p[1] + h / 2))
        ya, yb = int((1 - y1 / c.asp) * H), int((1 - y0 / c.asp) * H)
        xa, xb = int(x0 * W), int(x1 * W)
        reg = lum[max(ya, 0):max(yb, 1), max(xa, 0):max(xb, 1)]
        if reg.size:
            msgs.append((text, float(reg.mean()), float(np.percentile(reg, 5))))
    return msgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overlay", default=str(ROOT / "figures/hero/fig1_overlay.json"))
    ap.add_argument("--inset", default=str(ROOT / "data/derived/hero/inset.json"))
    ap.add_argument("--out", default=str(ROOT / "figures/fig1_overlay.tex"))
    ap.add_argument("--png", default=None)
    ap.add_argument("--inset-cm", type=float, default=1.55)
    a = ap.parse_args()
    ov = json.load(open(a.overlay))
    d = json.load(open(a.inset))
    c = Ctx(ov)
    L = ["% generated by tools/make_fig1_overlay.py from figures/hero/fig1_overlay.json -- do not edit",
         "% unit = image width; origin = lower-left corner of the image"]
    # coordinate lines and baselines (below the arrows)
    for panel in ("lone", "pair"):
        L.append(grey_line(c, c.pt(panel, "coord_0"), c.pt(panel, "coord_1")))
    for panel in ("rib_lone", "rib_pair"):
        for k in (0, 1):
            L.append(grey_line(c, c.pt(panel, "base%d_0" % k), c.pt(panel, "base%d_1" % k)))
    # arrows
    stats = {}
    for panel, names in (("lone", [("drive", "black"), ("wall", "wall"), ("orca", "orca")]),
                         ("pair", [("drive", "black"), ("wall", "wall"), ("partner", "partner"), ("bias", "bias")])):
        for n, col in names:
            o, Lc = arrow(c, c.pt(panel, n + "_0"), c.pt(panel, n + "_1"), C[col], halo="dark" if col == "bias" else True,
                          head_cm=0.16 if col != "bias" else 0.10)
            L += o
            stats[panel + "_" + n + "_cm"] = round(Lc, 3)
    # scale bars
    L += bar(c, c.pt("lone", "scale100_0"), c.pt("lone", "scale100_1"))
    L += bar(c, c.pt("lone", "scale_half_m_0"), c.pt("lone", "scale_half_m_1"))
    L += bar(c, c.pt("rib_lone", "scale_0"), c.pt("rib_lone", "scale_1"))
    L += bar(c, c.pt("rib_pair", "scale_0"), c.pt("rib_pair", "scale_1"))
    # labels
    chk = []
    for text, panel, anchor, dx, dy, al in LABELS:
        p = c.off(c.pt(panel, anchor), dx, dy)
        L.append(r"\node[anchor=%s,inner sep=0pt,font=%s,text=black!85] at %s {%s};" % (al, FONT, f(p), text))
        chk.append((text, p, al))
    # inset
    ins, box = inset(c, d, ov, size_cm=a.inset_cm)
    L += ins
    import re
    xs = [float(m.group(1)) for line in L for m in re.finditer(r"\((-?[0-9.]+),(-?[0-9.]+)\)", line)]
    ys = [float(m.group(2)) for line in L for m in re.finditer(r"\((-?[0-9.]+),(-?[0-9.]+)\)", line)]
    if min(xs) < 0 or max(xs) > 1 or min(ys) < 0 or max(ys) > c.asp:
        print("WARNING overlay coordinates outside the image: x [%.3f, %.3f], y [%.3f, %.3f] (image 0..1, 0..%.3f)" % (min(xs), max(xs), min(ys), max(ys), c.asp))
    Path(a.out).write_text("\n".join(l if l.startswith("%") else l + "%" for l in L) + "\n")
    print("wrote", a.out, "| arrow lengths (cm):", stats, "| inset box (cm from image lower-left):",
          [round(v * c.cm, 2) for v in box])
    for text, m, lo in label_checks(c, chk, a.png):
        flag = "" if (m >= 0.75 and lo >= 0.45) else "   <-- dark under text"
        print("  label %-14s mean lum %.2f  p5 %.2f%s" % (text, m, lo, flag))


if __name__ == "__main__":
    main()
