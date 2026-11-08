"""Write 256-entry sRGB lookup tables for the hero render (Blender's Python has no Matplotlib).

    .venv/bin/python experiments/hero/make_luts.py      (from the repository root, after make venv)

  cividis - agents, stuck-alone margin (blue: passes alone, yellow: held alone)
  floor   - backward wall force on a lone 0.25 m agent, log scale from F_FADE = 5 N to 1000 N: a truncated magma range
            (orange -> red -> dark purple, no yellow), blended in CIE Lab from the figure background (neutral off-white)
            over the first part of the range so that the floor is exactly the background at and below 5 N
  viridis, greys - alternatives kept for the ramp parameter of render_hero.py
Also writes data/derived/hero/floor_deltaE.json: the minimum CIEDE2000 between every floor colour and (a) the cividis
yellow of the held-alone blocker (margin +146 N), (b) the lateral-bias yellow #F0E442.
"""
import json
from pathlib import Path

import numpy as np
from matplotlib import colormaps

OUT = Path(__file__).resolve().parents[2] / "data" / "derived" / "hero" / "luts.npz"
BG = np.array([245, 245, 245]) / 255.0           # neutral off-white, shared by all four panels and the floor
F_FADE, F_MAX = 5.0, 1000.0
S_ORANGE, S_DARK = 0.78, 0.25                     # magma positions: orange end (weak force), dark purple end (strong force)
FADE_FRAC = 0.22                                  # fraction of the log range over which the floor blends in from BG
BLOCKER_MARGIN, MARGIN_SPAN = 146.2, 150.0


def srgb2lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin2srgb(c):
    c = np.clip(np.asarray(c, float), 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
WP = M @ np.ones(3)


def rgb2lab(rgb):
    xyz = (M @ srgb2lin(np.atleast_2d(rgb)).T).T / WP
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.column_stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])])


def lab2rgb(lab):
    lab = np.atleast_2d(lab)
    fy = (lab[:, 0] + 16) / 116
    fx, fz = fy + lab[:, 1] / 500, fy - lab[:, 2] / 200
    f = np.column_stack([fx, fy, fz])
    xyz = np.where(f > 6 / 29, f ** 3, 3 * (6 / 29) ** 2 * (f - 4 / 29)) * WP
    return lin2srgb((np.linalg.inv(M) @ xyz.T).T)


def de2000(l1, l2):
    """CIEDE2000 between Lab arrays (n,3) and (3,) or (n,3) (Sharma, Wu, Dalal 2005)."""
    l1, l2 = np.atleast_2d(l1), np.atleast_2d(l2)
    L1, a1, b1 = l1.T
    L2, a2, b2 = l2.T
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cm = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cm ** 7 / (Cm ** 7 + 25.0 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    dL, dC = L2 - L1, C2p - C1p
    dh = h2p - h1p
    dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh))
    dh = np.where(C1p * C2p == 0, 0, dh)
    dH = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh) / 2)
    Lm, Cpm = (L1 + L2) / 2, (C1p + C2p) / 2
    hs = h1p + h2p
    hm = np.where(np.abs(h1p - h2p) <= 180, hs / 2, np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2))
    hm = np.where(C1p * C2p == 0, hs, hm)
    T = (1 - 0.17 * np.cos(np.radians(hm - 30)) + 0.24 * np.cos(np.radians(2 * hm)) + 0.32 * np.cos(np.radians(3 * hm + 6))
         - 0.20 * np.cos(np.radians(4 * hm - 63)))
    dth = 30 * np.exp(-(((hm - 275) / 25) ** 2))
    Rc = 2 * np.sqrt(Cpm ** 7 / (Cpm ** 7 + 25.0 ** 7))
    Sl = 1 + 0.015 * (Lm - 50) ** 2 / np.sqrt(20 + (Lm - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cpm, 1 + 0.015 * Cpm * T
    Rt = -np.sin(np.radians(2 * dth)) * Rc
    return np.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))


def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def floor_lut():
    t = np.linspace(0, 1, 256)                                   # log10 F from log10 5 to log10 1000
    ramp = colormaps["magma"](S_ORANGE + (S_DARK - S_ORANGE) * t)[:, :3]
    w = smoothstep(t / FADE_FRAC)[:, None]
    lab = (1 - w) * rgb2lab(BG)[0] + w * rgb2lab(ramp)
    return np.clip(lab2rgb(lab), 0, 1), ramp


if __name__ == "__main__":
    t = np.linspace(0, 1, 256)
    fl, ramp = floor_lut()
    cv = colormaps["cividis"](t)[:, :3]
    luts = {"cividis": cv, "viridis": colormaps["viridis"](t)[:, :3], "floor": fl, "greys": colormaps["Greys"](0.05 + 0.85 * t)[:, :3],
            "bg": BG, "wall_dark": ramp[-1]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez(OUT, **luts)
    yb = cv[int(round(np.clip((BLOCKER_MARGIN + MARGIN_SPAN) / (2 * MARGIN_SPAN), 0, 1) * 255))]
    ylat = np.array([0xF0, 0xE4, 0x42]) / 255.0
    labs = rgb2lab(fl)
    res = {"floor_bg_rgb": (BG * 255).round().tolist(), "floor_dark_end_hex": "#%02X%02X%02X" % tuple((ramp[-1] * 255).round().astype(int)),
           "floor_orange_end_hex": "#%02X%02X%02X" % tuple((ramp[0] * 255).round().astype(int)), "F_fade_N": F_FADE, "F_max_N": F_MAX}
    for name, y in (("held_alone_cividis_yellow", yb), ("lateral_bias_F0E442", ylat)):
        d = de2000(labs, rgb2lab(y)[0])
        res[name] = {"rgb_hex": "#%02X%02X%02X" % tuple((y * 255).round().astype(int)), "min_dE2000": float(d.min()),
                     "at_force_N": float(F_FADE * (F_MAX / F_FADE) ** (t[int(d.argmin())]))}
    res["min_dE2000_overall"] = min(res["held_alone_cividis_yellow"]["min_dE2000"], res["lateral_bias_F0E442"]["min_dE2000"])
    json.dump(res, open(OUT.parent / "floor_deltaE.json", "w"), indent=1)
    print(json.dumps(res, indent=1))
