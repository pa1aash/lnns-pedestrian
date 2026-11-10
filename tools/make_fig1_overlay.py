"""Turn figures/hero/fig1_overlay.json (3-D anchors projected by render_hero.py) into figures/fig1_overlay.tex.

    python3 tools/make_fig1_overlay.py [--overlay figures/hero/fig1_overlay.json] [--png figures/fig1_hero.png]
                                       [--out figures/fig1_overlay.tex]

The TeX file is a fragment for a TikZ scope whose unit is the image width (x = y = \\textwidth, origin at the
image's lower-left corner): force arrows (0.6 pt shafts, solid), coordinate lines, one scale-bar cluster in the lone scene,
the axes of the four ribbons (x in metres, energy in joules; 0.4 pt lines, 0.05 cm ticks, identical on all four) and the
labels (7 pt Latin Modern serif, dark text on light areas, no boxes, halos or leader lines). Nothing here is hand-placed
except the label table below; every arrow, line, axis and tick end point is a projected 3-D anchor. Rev. 1 removed the
room inset (moved to its own figure) and the 10 J / 0.5 J scale bars (replaced by the axes).

The script also checks the ribbon axes against the physics: the projected own-drive minimum and barrier top, read back
through the tick positions, must give x = 9.660 m at 0 J and x = 9.9415 m at 21.27 J (hero_physics.json).

With --png the script also checks each label against the image: the estimated text box must sit on light
pixels (mean luminance >= 0.75, darkest 5 % >= 0.45); failures are printed.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GREY = "7F7F7F"
C = {"black": "000000", "wall": "51127C", "orca": "0072B2", "partner": "51127C", "push": "777777", "scale": "333333"}
# Latin Modern (lmr) is scalable and matches the Computer Modern body text; 7 pt is the minimum print size (rev. 1).
FONT = r"\fontfamily{lmr}\fontsize{7}{8.4}\selectfont"
CHAR_W_CM = 0.127            # mean advance of 7 pt Latin Modern text, for the box estimate only
AXIS = "{rgb,255:red,51;green,51;blue,51}"
AXIS_LW, TICK_CM, TICK_GAP_CM = 0.4, 0.05, 0.035

# (text, panel, anchor, dx_cm, dy_cm, tikz anchor). Offsets in printed cm; anchors "@tl" etc are panel corners,
# "a+b" is the midpoint of anchors a and b. Panel tags top-left; scene labels beside the one object they name (each
# "passes alone" over its own disc, under the kerb; "held alone" over the blocker's top-left, in the doorway); ribbon labels
# above one end of their ribbon; tick labels are generated with the axes.
LABELS = [
    ("lone trap", "lone", "@tl", 0.10, -0.08, "north west"),
    ("100 N", "lone", "scale100_mid", -0.10, 0.0, "east"),
    ("0.5 m", "lone", "scale_half_m_mid", 0.0, 0.07, "south"),
    ("held alone", "lone", "held_top", -0.26, 0.10, "south east"),
    ("passes alone", "lone", "n54_top", 0.0, 0.06, "south"),
    ("passes alone", "lone", "n38_top", 0.0, 0.06, "south"),
    ("drive", "lone", "drive_f", 0.15, 0.0, "west"),
    ("wall", "lone", "wall_1", 0.12, -0.03, "west"),
    ("ORCA", "lone", "orca_mid", 0.12, 0.0, "west"),
    ("own drive", "rib_lone", "band_01", 0.02, 0.03, "south west"),
    ("added drive", "rib_lone", "label1", -0.02, 0.03, "south east"),
    ("noise", "rib_lone", "band_10+band_11", 0.08, 0.0, "west"),
    ("pair standoff", "pair", "@tl", 0.10, -0.08, "north west"),
    ("held together", "pair", "between", 0.0, 1.0, "south"),
    ("no tilt", "rib_pair", "label0", 0.02, 0.03, "south west"),
    ("tilted", "rib_pair", "label1", -0.02, 0.03, "south east"),
]


class Ctx:
    def __init__(self, ov):
        self.ov = ov
        self.W, self.H = ov["px"]
        self.asp = self.H / self.W
        self.cm = ov["cm"][0]

    def pt(self, panel, name):
        a = self.ov["panels"][panel]["anchors"]
        if "+" in name:
            p, q = (self.pt(panel, n) for n in name.split("+"))
            return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        if name.startswith("@"):
            x, y, w, h = self.ov["panels_px"][panel]
            u, v = {"@tl": (x, y), "@tr": (x + w, y), "@bl": (x, y + h), "@br": (x + w, y + h)}[name]
            return (u / self.W, (1 - v / self.H) * self.asp)
        if name.endswith("_f"):                      # 84 % along the arrow (label beside its shaft, clear of the tip junction)
            b = name[:-2]
            p0, p1 = a[b + "_0"], a[b + "_1"]
            return (p0[0] + 0.84 * (p1[0] - p0[0]), (p0[1] + 0.84 * (p1[1] - p0[1])) * self.asp)
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


def arrow(c, p0, p1, colour, lw=0.6, halo=True, head_cm=0.095):
    L = math.hypot((p1[0] - p0[0]) * c.cm, (p1[1] - p0[1]) * c.cm)
    h = min(head_cm, max(0.6 * L, 0.03))
    tip = "{Stealth[length=%.3fcm,width=%.3fcm]}" % (h, 0.75 * h)
    out = []
    if halo:      # thin white under-stroke so black / dark arrows stay visible over dark agents and floor
        out.append(r"\draw[-%s,line width=%.2fpt,color=white,opacity=0.9] %s -- %s;" % (tip, lw + 0.7, f(p0), f(p1)))
    out.append(r"\draw[-%s,line width=%.2fpt,color={rgb,255:red,%d;green,%d;blue,%d}] %s -- %s;" % (
        tip, lw, *[int(colour[i:i + 2], 16) for i in (0, 2, 4)], f(p0), f(p1)))
    return out, L


def bar(c, p0, p1, lw=0.5, tick_cm=0.05):
    dx, dy = (p1[0] - p0[0]) * c.cm, (p1[1] - p0[1]) * c.cm
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * tick_cm / c.cm, dx / L * tick_cm / c.cm
    col = "{rgb,255:red,51;green,51;blue,51}"
    return [r"\draw[line width=%.2fpt,color=%s] %s -- %s;" % (lw, col, f(p0), f(p1)),
            r"\draw[line width=%.2fpt,color=%s] (%.5f,%.5f) -- (%.5f,%.5f);" % (lw, col, p0[0] - nx, p0[1] - ny, p0[0] + nx, p0[1] + ny),
            r"\draw[line width=%.2fpt,color=%s] (%.5f,%.5f) -- (%.5f,%.5f);" % (lw, col, p1[0] - nx, p1[1] - ny, p1[0] + nx, p1[1] + ny)]


def grey_line(c, p0, p1):
    return r"\draw[line width=0.4pt,color={rgb,255:red,127;green,127;blue,127}] %s -- %s;" % (f(p0), f(p1))


def decimals(vals):
    return max(len(("%g" % abs(v)).split(".")[1]) if "." in ("%g" % abs(v)) else 0 for v in vals)


def tex_num(v, d):
    t = "%.*f" % (d, v)
    return "0" if float(t) == 0 and d == 0 else t.replace("-", "$-$")


def ribbon_axes(c, panel, ov, labelled_x):
    """Axes of the two ribbons of one panel: per ribbon an x axis (baseline, ticks down) and an energy axis (left, ticks
    left, numbers in J, unit above); x tick numbers and the unit on the lower ribbon's axis only (both share the x map)."""
    a = ov["panels"][panel]["anchors"]
    out, chk = [], []
    tk = TICK_CM / c.cm
    for k in (0, 1):
        xt = sorted([(float(n.split("_", 1)[1]), n) for n in a if n.startswith("xt%d_" % k)])
        et = sorted([(float(n.split("_", 1)[1]), n) for n in a if n.startswith("et%d_" % k)])
        dx_, de_ = decimals([v for v, _ in xt]), decimals([v for v, _ in et])
        b0, b1 = c.pt(panel, "base%d_0" % k), c.pt(panel, "base%d_1" % k)
        out.append(r"\draw[line width=%.2fpt,color=%s] %s -- %s;" % (AXIS_LW, AXIS, f(b0), f(b1)))
        for i, (v, n) in enumerate(xt):
            p = c.pt(panel, n)
            out.append(r"\draw[line width=%.2fpt,color=%s] %s -- %s;" % (AXIS_LW, AXIS, f(p), f((p[0], p[1] - tk))))
            if k == labelled_x:
                q = (p[0], p[1] - tk - TICK_GAP_CM / c.cm)
                nm = "%sx%d" % (panel.replace("_", ""), i)
                out.append(r"\node[anchor=north,inner sep=0pt,font=%s,text=black!85] (%s) at %s {%s};" % (FONT, nm, f(q), tex_num(v, dx_)))
                chk.append((tex_num(v, dx_), q, "north"))
                if i == len(xt) - 1:
                    out.append(r"\node[anchor=base west,inner sep=0pt,font=%s,text=black!85] at ([xshift=2pt]%s.base east) {m};" % (FONT, nm))
        e0, e1 = c.pt(panel, "e%d_lo" % k), c.pt(panel, "e%d_hi" % k)
        out.append(r"\draw[line width=%.2fpt,color=%s] %s -- %s;" % (AXIS_LW, AXIS, f(e0), f(e1)))
        for v, n in et:
            p = c.pt(panel, n)
            out.append(r"\draw[line width=%.2fpt,color=%s] %s -- %s;" % (AXIS_LW, AXIS, f(p), f((p[0] - tk, p[1]))))
            q = (p[0] - tk - TICK_GAP_CM / c.cm, p[1])
            out.append(r"\node[anchor=east,inner sep=0pt,font=%s,text=black!85] at %s {%s};" % (FONT, f(q), tex_num(v, de_)))
            chk.append((tex_num(v, de_), q, "east"))
        q = (e1[0], e1[1] + 0.09 / c.cm)
        out.append(r"\node[anchor=south,inner sep=0pt,font=%s,text=black!85] at %s {J};" % (FONT, f(q)))
        chk.append(("J", q, "south"))
    return out, chk


def axis_physics_check(c, ov):
    """Read anchors back through the tick positions (linear in the orthographic camera) and compare with the physics."""
    import numpy as np
    res = {}
    for panel in ("rib_lone", "rib_pair"):
        a = ov["panels"][panel]["anchors"]
        for k in (0, 1):
            xt = [(float(n.split("_", 1)[1]), a[n][0]) for n in a if n.startswith("xt%d_" % k)]
            et = [(float(n.split("_", 1)[1]), a[n][1]) for n in a if n.startswith("et%d_" % k)]
            px = np.polyfit([u for _, u in xt], [v for v, _ in xt], 1)
            pe = np.polyfit([w for _, w in et], [v for v, _ in et], 1)
            rx = max(abs(np.polyval(px, u) - v) for v, u in xt)
            for nm in ("curve%d_top" % k, "curve%d_min" % k, "ball%d" % k):
                if nm in a:
                    res["%s.%s" % (panel, nm)] = (round(float(np.polyval(px, a[nm][0])), 4), round(float(np.polyval(pe, a[nm][1])), 3))
            res["%s.tick_linearity_resid_m.%d" % (panel, k)] = float("%.1e" % rx)
            if panel == "rib_lone" and k == 0 and "band_01" in a:
                res["rib_lone.band_top_J"] = round(float(np.polyval(pe, a["band_01"][1])), 3)
                res["rib_lone.band_bottom_J"] = round(float(np.polyval(pe, a["band_00"][1])), 3)
    return res


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
        text = text.replace("$-$", "-")
        w = max(len(text), 1) * CHAR_W_CM / c.cm
        h = 0.30 / c.cm
        x0, x1 = {"west": (p[0], p[0] + w), "east": (p[0] - w, p[0]), "south west": (p[0], p[0] + w), "north west": (p[0], p[0] + w),
                  "south east": (p[0] - w, p[0])}.get(anchor, (p[0] - w / 2, p[0] + w / 2))
        y0, y1 = {"north west": (p[1] - h, p[1]), "south": (p[1], p[1] + h), "south west": (p[1], p[1] + h), "south east": (p[1], p[1] + h),
                  "north": (p[1] - h, p[1])}.get(anchor, (p[1] - h / 2, p[1] + h / 2))
        ya, yb = int((1 - y1 / c.asp) * H), int((1 - y0 / c.asp) * H)
        xa, xb = int(x0 * W), int(x1 * W)
        reg = lum[max(ya, 0):max(yb, 1), max(xa, 0):max(xb, 1)]
        if reg.size:
            msgs.append((text, float(reg.mean()), float(np.percentile(reg, 5))))
    return msgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overlay", default=str(ROOT / "figures/hero/fig1_overlay.json"))
    ap.add_argument("--out", default=str(ROOT / "figures/fig1_overlay.tex"))
    ap.add_argument("--png", default=None)
    a = ap.parse_args()
    ov = json.load(open(a.overlay))
    c = Ctx(ov)
    L = ["% generated by tools/make_fig1_overlay.py from figures/hero/fig1_overlay.json -- do not edit",
         "% unit = image width; origin = lower-left corner of the image"]
    # coordinate lines and baselines (below the arrows)
    for panel in ("lone", "pair"):
        L.append(grey_line(c, c.pt(panel, "coord_0"), c.pt(panel, "coord_1")))
    axchk = []
    for panel in ("rib_lone", "rib_pair"):
        o, ch = ribbon_axes(c, panel, ov, labelled_x=1)
        L += o
        axchk += ch
    # arrows
    stats = {}
    for panel, names in (("lone", [("wall", "wall", True), ("drive", "black", True), ("push", "push", True), ("orca", "orca", True)]),
                         ("pair", [("wall", "wall", True), ("partner", "partner", True), ("drive", "black", True)])):
        for n, col, halo in names:
            o, Lc = arrow(c, c.pt(panel, n + "_0"), c.pt(panel, n + "_1"), C[col], halo=halo)
            L += o
            stats[panel + "_" + n + "_cm"] = round(Lc, 3)
    # scale bars
    L += bar(c, c.pt("lone", "scale100_0"), c.pt("lone", "scale100_1"))          # the cluster: shared lower-left corner
    L += bar(c, c.pt("lone", "scale_half_m_0"), c.pt("lone", "scale_half_m_1"))
    # labels
    chk = []
    for text, panel, anchor, dx, dy, al in LABELS:
        p = c.off(c.pt(panel, anchor), dx, dy)
        L.append(r"\node[anchor=%s,inner sep=0pt,font=%s,text=black!85] at %s {%s};" % (al, FONT, f(p), text))
        chk.append((text, p, al))
    import re
    xs = [float(m.group(1)) for line in L for m in re.finditer(r"\((-?[0-9.]+),(-?[0-9.]+)\)", line)]
    ys = [float(m.group(2)) for line in L for m in re.finditer(r"\((-?[0-9.]+),(-?[0-9.]+)\)", line)]
    if min(xs) < 0 or max(xs) > 1 or min(ys) < 0 or max(ys) > c.asp:
        print("WARNING overlay coordinates outside the image: x [%.3f, %.3f], y [%.3f, %.3f] (image 0..1, 0..%.3f)" % (min(xs), max(xs), min(ys), max(ys), c.asp))
    Path(a.out).write_text("\n".join(l if l.startswith("%") else l + "%" for l in L) + "\n")
    print("wrote", a.out, "| arrow lengths (cm):", stats)
    ph = axis_physics_check(c, ov)
    rl = ov["ribbons"]["lone"]
    print("axis check (x m, E J) read back through the ticks:", json.dumps(ph))
    top, mn = ph["rib_lone.curve0_top"], ph["rib_lone.curve0_min"]
    ok = (abs(top[0] - rl["x_barrier_own_m"]) < 0.004 and abs(top[1] - rl["barrier_own_J"]) < 0.3
          and abs(mn[0] - rl["x_min_own_m"]) < 0.004 and abs(mn[1]) < 0.3 and abs(ph["rib_lone.band_top_J"] - rl["kT_J"]) < 0.05)
    print("  own drive: minimum x %.4f m (physics %.4f) at %.2f J; barrier x %.4f m (physics %.4f) at %.2f J (physics %.2f); "
          "band 0..%.2f J (k_BT_eff %.2f): %s" % (mn[0], rl["x_min_own_m"], mn[1], top[0], rl["x_barrier_own_m"], top[1],
                                                   rl["barrier_own_J"], ph["rib_lone.band_top_J"], rl["kT_J"], "OK" if ok else "MISMATCH"))
    for text, m, lo in label_checks(c, chk + axchk, a.png):
        flag = "" if (m >= 0.75 and lo >= 0.45) else "   <-- dark under text"
        print("  label %-14s mean lum %.2f  p5 %.2f%s" % (text, m, lo, flag))


if __name__ == "__main__":
    main()
