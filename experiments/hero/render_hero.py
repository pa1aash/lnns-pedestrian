"""Headless Blender render of the hero figure (Fig. 1): four panels from the .npz files of export_hero.py.

    blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- \\
        --width-px 900 --samples 24 --out figures/hero/mock/fig1_hero_mock.png

Layout (cm, 12.2 wide): 2 x 2, one white background, no panel borders.
  top-left     lone scene (near-plan camera, elevation 65 deg, orthographic, 2.5 cm per metre of floor)
  bottom-left  pair scene (same camera, elevation and scale)
  top-right    lone-trap ribbons: own drive / added drive (front-on orthographic, one energy scale)
  bottom-right pair ribbons: no tilt / tilted (its own energy scale)
The image holds no text, arrows, lines or scale bars. Every overlay element is exported as 3-D anchor points
projected to normalised image coordinates (bpy_extras.object_utils.world_to_camera_view) into
figures/hero/fig1_overlay.json; tools/make_fig1_overlay.py turns that into figures/fig1_overlay.tex.
"""
import argparse
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "derived" / "hero"
A = None
BG = (245 / 255, 245 / 255, 245 / 255)     # neutral off-white: all four panels and the weak-force floor (make_luts.BG)
EDGE_RGB = (0.10, 0.10, 0.10)
KERB_RGB = (0.62, 0.62, 0.60)
OKABE = {"black": (0.0, 0.0, 0.0), "blue": (0.0, 0.447, 0.698), "yellow": (0.941, 0.894, 0.259),
         "vermillion": (0.835, 0.369, 0.0)}


def srgb_to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--overlay", default=str(ROOT / "figures" / "hero" / "fig1_overlay.json"))
    ap.add_argument("--width-px", type=int, default=900)
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--device", choices=["GPU", "CPU"], default="GPU")
    ap.add_argument("--panels", default="lone,pair,rib_lone,rib_pair")
    ap.add_argument("--cache-dir", default=None, help="save each rendered panel (pixels + anchors) here; with --panels a subset, nothing else is written")
    ap.add_argument("--assemble", action="store_true", help="no rendering: load the four cached panels and write the composite and the overlay json")
    ap.add_argument("--tile", type=int, default=256, help="Cycles tile size (px)")
    # layout, cm
    ap.add_argument("--width-cm", type=float, default=12.2)
    ap.add_argument("--col-cm", type=float, default=6.0)
    ap.add_argument("--row-cm", type=float, default=3.65, help="height of the lone row")
    ap.add_argument("--row-pair-cm", type=float, default=2.65, help="height of the pair row (cropped from the top: same near edge, same kerb height above the bottom)")
    ap.add_argument("--gap-cm", type=float, default=0.2)
    # floor scenes
    ap.add_argument("--elev", type=float, default=65.0)
    ap.add_argument("--cm-per-m", type=float, default=2.65, help="printed cm per metre of floor, both scenes")
    ap.add_argument("--x0", type=float, default=9.18, help="m, near edge of both floor scenes")
    ap.add_argument("--yc", type=float, default=5.0)
    ap.add_argument("--agent-height", type=float, default=0.15, help="m, stylised")
    ap.add_argument("--kerb-height", type=float, default=0.10, help="m, stylised")
    ap.add_argument("--kerb-thick", type=float, default=0.035)
    ap.add_argument("--edge", type=float, default=0.006, help="m, dark shading edge around each agent")
    ap.add_argument("--bevel", type=float, default=0.008, help="m, bevel on discs and kerbs")
    ap.add_argument("--margin-span", type=float, default=150.0)
    ap.add_argument("--force-min", type=float, default=5.0, help="N, the floor is the background at and below this force")
    ap.add_argument("--floor-diffuse", type=float, default=0.25, help="share of the LUT colour that is lit (soft shadows)")
    ap.add_argument("--floor-emit", type=float, default=0.76, help="emission = 1 - floor_diffuse x (measured lit fraction 0.97): unshaded floor renders as its LUT colour")
    ap.add_argument("--force-max", type=float, default=1000.0)
    ap.add_argument("--arrow-m-per-n", type=float, default=0.003, help="floor metres per newton: 100 N = 0.30 m")
    # ribbons
    ap.add_argument("--lone-x", default="9.54,10.0", help="m, door-axis range of the lone ribbons")
    ap.add_argument("--lone-ej", type=float, default=35.0, help="J per cm of ribbon height (lone)")
    ap.add_argument("--pair-c", type=float, default=0.10, help="m, |common shift| of the pair ribbons")
    ap.add_argument("--pair-ej", type=float, default=1.5, help="J per cm of ribbon height (pair)")
    ap.add_argument("--rib-width-cm", type=float, default=4.1)
    ap.add_argument("--rib-thick-cm", type=float, default=0.11)
    ap.add_argument("--rib-depth-cm", type=float, default=0.40)
    ap.add_argument("--ball-cm", type=float, default=0.11, help="ball radius")
    ap.add_argument("--rib-elev", type=float, default=12.0)
    ap.add_argument("--cluster-u", type=float, default=0.95, help="cm from the lone panel's left edge: corner of the 100 N bar")
    ap.add_argument("--cluster-gap", type=float, default=0.28, help="cm between the 100 N bar and the start of the 0.5 m bar")
    ap.add_argument("--cluster-v", type=float, default=1.17, help="cm from the lone panel's top edge: scale cluster corner")
    ap.add_argument("--light", type=float, default=0.25)
    ap.add_argument("--world-strength", type=float, default=0.35)
    a = ap.parse_args(argv)
    return a


# ------------------------------------------------------------------ plumbing
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_render(w, h):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.threads_mode = "FIXED"
    sc.render.threads = A.threads
    sc.cycles.samples = A.samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.cycles.device = "CPU"
    sc.render.use_persistent_data = False
    if hasattr(sc.cycles, "tile_size"):
        sc.cycles.tile_size = A.tile
    if A.device == "GPU":
        prefs = bpy.context.preferences.addons["cycles"].preferences
        try:
            prefs.compute_device_type = "METAL"
            prefs.get_devices()
            devs = [d for d in prefs.devices if d.type == "METAL"]
            if devs:
                for d in prefs.devices:
                    d.use = d.type == "METAL"
                sc.cycles.device = "GPU"
        except TypeError:
            pass
    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb_to_linear(BG), 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = A.world_strength
    return sc.cycles.device


def material(name, rgb=None, image=None, rough=0.6, spec=0.25, alpha=1.0, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = spec
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Alpha"].default_value = alpha
    if rgb is not None:
        p.inputs["Base Color"].default_value = (*srgb_to_linear(rgb), 1)
    if image is not None:
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = image
        n.interpolation = "Linear"
        n.extension = "EXTEND"
        nt.links.new(n.outputs["Color"], p.inputs["Base Color"])
    if alpha < 1.0:
        m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    return m


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def mesh_obj(name, verts, faces, mat, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    if smooth:
        me.shade_smooth()
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me))


def add_bevel(ob, width, segments=2):
    md = ob.modifiers.new("bevel", "BEVEL")
    md.width = width
    md.segments = segments
    md.limit_method = "ANGLE"
    md.angle_limit = math.radians(35)


def cylinder(name, x, y, r, h, rgb, z0=0.0, n=96, bevel=0.0, rough=0.5):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    verts = [(x + r * math.cos(t), y + r * math.sin(t), z0) for t in th] + [(x + r * math.cos(t), y + r * math.sin(t), z0 + h) for t in th]
    faces = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    faces += [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    ob = mesh_obj(name, verts, faces, material(name, rgb, rough=rough, spec=0.3))
    for poly in ob.data.polygons:
        poly.use_smooth = len(poly.vertices) == 4
    if bevel:
        add_bevel(ob, bevel)
    return ob


def slab(name, p0, p1, thick, h, rgb, bevel=0.0):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d)
    if L < 1e-9:
        return None
    t = d / L
    nrm = np.array([-t[1], t[0]]) * thick / 2
    q = [p0 - nrm, p1 - nrm, p1 + nrm, p0 + nrm]
    verts = [(*c, 0.0) for c in q] + [(*c, h) for c in q]
    faces = [(0, 1, 2, 3)[::-1], (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = mesh_obj(name, verts, faces, material(name, rgb, rough=0.75, spec=0.2))
    if bevel:
        add_bevel(ob, bevel)
    return ob


def sphere(name, c, r, rgb, rough=0.25, alpha=1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=48, ring_count=24, location=tuple(c))
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(material(name, rgb, rough=rough, spec=0.5, alpha=alpha))
    bpy.ops.object.shade_smooth()
    return ob


LUTS = None


def ramp(values, lo, hi, name):
    t = np.clip((np.asarray(values, float) - lo) / (hi - lo), 0, 1)
    return LUTS[name][np.round(t * 255).astype(int)]


def clip_segment(p0, p1, box):
    x0, x1, y0, y1 = box
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    t0, t1 = 0.0, 1.0
    for p, q in ((-d[0], p0[0] - x0), (d[0], x1 - p0[0]), (-d[1], p0[1] - y0), (d[1], y1 - p0[1])):
        if abs(p) < 1e-12:
            if q < 0:
                return None
            continue
        r = q / p
        if p < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
    if t0 > t1:
        return None
    return p0 + t0 * d, p0 + t1 * d


def area_lights(target, scale, k=None, az=0.0, spec=None):
    k = A.light if k is None else k
    t = Vector(target)
    ca, sa = math.cos(math.radians(az)), math.sin(math.radians(az))
    for nm, off, energy, size in (spec or (("key", (-2.2, -2.6, 3.6), 520, 2.6), ("fill", (3.0, -1.0, 2.2), 160, 3.0),
                                           ("rim", (0.5, 3.2, 2.5), 140, 2.0))):
        ld = bpy.data.lights.new(nm, "AREA")
        ld.energy = energy * scale ** 2 * k
        ld.size = size * scale
        ob = link(bpy.data.objects.new(nm, ld))
        ob.location = t + Vector((off[0] * ca - off[1] * sa, off[0] * sa + off[1] * ca, off[2])) * scale
        ob.rotation_euler = (t - ob.location).to_track_quat("-Z", "Y").to_euler()


def view_vectors(azim, elev):
    az, el = math.radians(azim), math.radians(elev)
    d = np.array([-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), math.sin(el)])
    right = np.array([-math.sin(az), math.cos(az), 0.0])
    up = np.array([math.sin(el) * math.cos(az), math.sin(el) * math.sin(az), math.cos(el)])
    return d, right, up


def ortho_camera(target, azim, elev, ortho_scale):
    d, _, _ = view_vectors(azim, elev)
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ortho_scale
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_start, cd.clip_end = 0.05, 400.0
    cam = link(bpy.data.objects.new("cam", cd))
    cam.location = Vector(target) + Vector(d.tolist()) * 40.0
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    bpy.context.view_layer.update()
    return cam


class Anchors:
    """Projects 3-D anchor points of one panel to normalised coordinates of the full composite."""

    def __init__(self, off, size, canvas):
        self.off, self.size, self.canvas = off, size, canvas     # px (x, y from top), (w, h), (W, H)
        self.pts = {}

    def add(self, name, p):
        sc = bpy.context.scene
        u, v, _ = world_to_camera_view(sc, sc.camera, Vector([float(c) for c in p]))
        W, H = self.canvas
        self.pts[name] = [round((self.off[0] + u * self.size[0]) / W, 5), round(1.0 - (self.off[1] + (1.0 - v) * self.size[1]) / H, 5)]
        return self.pts[name]


# ------------------------------------------------------------------ floor scenes
def floor_scene(D, anc, kind, extras):
    h_cm = A.row_cm if kind == "lone" else A.row_pair_cm
    sin_el = math.sin(math.radians(A.elev))
    wm = A.col_cm / A.cm_per_m                           # metres across
    dx = h_cm / (A.cm_per_m * sin_el)                    # metres of depth
    box = (A.x0, A.x0 + dx, A.yc - wm / 2, A.yc + wm / 2)
    gx, gy = D["grid_x"], D["grid_y"]
    ix = (gx >= box[0] - 0.02) & (gx <= box[1] + 0.02)
    iy = (gy >= box[2] - 0.02) & (gy <= box[3] + 0.02)
    F = D["wall_back_N"][np.ix_(iy, ix)]
    feas = D["feasible"][np.ix_(iy, ix)]
    UP = 2                                               # bilinear upsampling of the 0.5 cm force grid (smooth lobe edges)

    def upsample(a, k=UP):
        h, w = a.shape
        yi, xi = (np.arange(h * k) + 0.5) / k - 0.5, (np.arange(w * k) + 0.5) / k - 0.5
        tmp = np.array([np.interp(xi, np.arange(w), row) for row in a])
        return np.array([np.interp(yi, np.arange(h), col) for col in tmp.T]).T
    logF = upsample(np.log10(np.maximum(F, 1.0)))
    if "clearance" in D:
        # anti-aliased excluded zone: the signed wall clearance (m, exact) is upsampled 8x and the mask is a one-texel
        # feathered step at zero, so no stair-steps show at the walls, the blocker or the pair jambs
        K = 8
        clr = upsample(D["clearance"][np.ix_(iy, ix)], K)
        texel = (gx[1] - gx[0]) / K
        mk = np.clip(clr / texel + 0.5, 0.0, 1.0)
        logF = upsample(np.log10(np.maximum(F, 1.0)), K)
    else:
        mk = np.clip((upsample(feas.astype(float)) - 0.35) / 0.3, 0.0, 1.0)
    rgb = ramp(logF, math.log10(A.force_min), math.log10(A.force_max), "floor")
    rgb = np.asarray(BG, float) + mk[..., None] * (rgb - np.asarray(BG, float))   # probe would overlap a wall: plain floor
    F = logF
    h_, w_ = F.shape
    img = bpy.data.images.new("floor", w_, h_, alpha=True)
    img.colorspace_settings.name = "sRGB"
    img.pixels.foreach_set(np.concatenate([rgb, np.ones((h_, w_, 1))], axis=2).astype(np.float32).ravel())
    img.pack()
    st = gx[1] - gx[0]
    X0, X1 = gx[ix][0] - st / 2, gx[ix][-1] + st / 2
    Y0, Y1 = gy[iy][0] - st / 2, gy[iy][-1] + st / 2
    me = bpy.data.meshes.new("floor")
    me.from_pydata([(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = (u, v)
    fm = material("floor", image=img, rough=0.9, spec=0.1)
    pb_ = fm.node_tree.nodes["Principled BSDF"]
    tex_ = [n for n in fm.node_tree.nodes if n.type == "TEX_IMAGE"][0]
    nt_ = fm.node_tree
    nt_.links.new(tex_.outputs["Color"], pb_.inputs["Emission Color"])
    pb_.inputs["Emission Strength"].default_value = A.floor_emit
    mx_ = nt_.nodes.new("ShaderNodeMix")                  # diffuse share of the LUT colour: the floor keeps soft contact shading
    mx_.data_type, mx_.blend_type = "RGBA", "MULTIPLY"
    mx_.inputs["Factor"].default_value = 1.0
    nt_.links.new(tex_.outputs["Color"], mx_.inputs[6])
    mx_.inputs[7].default_value = (A.floor_diffuse,) * 3 + (1.0,)
    nt_.links.new(mx_.outputs[2], pb_.inputs["Base Color"])
    me.materials.append(fm)
    link(bpy.data.objects.new("floor", me))
    fb = (X0, X1, Y0, Y1)
    for k, w in enumerate(D["walls"]):
        seg = clip_segment(w[:2], w[2:], fb)
        if seg is not None:
            slab("kerb%d" % k, seg[0], seg[1], A.kerb_thick, A.kerb_height, KERB_RGB, bevel=A.bevel)
    cols = ramp(D["margin_N"], -A.margin_span, A.margin_span, "cividis")
    for k, (p, r) in enumerate(zip(D["pos"], D["radius"])):
        cylinder("edge%d" % k, p[0], p[1], float(r) + A.edge, A.agent_height - 0.003, EDGE_RGB, bevel=A.bevel / 2)
        cylinder("agent%d" % k, p[0], p[1], float(r), A.agent_height, cols[k], bevel=A.bevel)
    ortho_camera(((box[0] + box[1]) / 2, A.yc, 0.0), 0.0, A.elev, wm)
    area_lights(((box[0] + box[1]) / 2, A.yc, 0.0), scale=1.4, az=0.0)
    # anchors: arrows (floor plane at agent-top height), coordinate line, labels
    zt = A.agent_height
    mpn = A.arrow_m_per_n
    arrows = extras["arrows"]
    for name, (p0, vec) in arrows.items():
        p0 = np.array([p0[0], p0[1], zt])
        p1 = p0 + np.array([vec[0], vec[1], 0.0]) * mpn
        anc.add(name + "_0", p0)
        anc.add(name + "_1", p1)
    for name, p in extras.get("points", {}).items():
        anc.add(name, [p[0], p[1], zt if len(p) < 3 else p[2]])
    return box


# ------------------------------------------------------------------ ribbons
def strip(name, X, Z, thick, depth, rgb, rough=0.55):
    """Extruded ribbon: top curve (X, Z) in cm, thickness `thick` below it, depth along y."""
    n = len(X)
    y0, y1 = -depth / 2, depth / 2
    top = [(X[i], y, Z[i]) for y in (y0, y1) for i in range(n)]
    bot = [(X[i], y, Z[i] - thick) for y in (y0, y1) for i in range(n)]
    v = top + bot
    T0, T1, B0, B1 = 0, n, 2 * n, 3 * n
    faces = []
    for i in range(n - 1):
        faces.append((T0 + i, T0 + i + 1, T1 + i + 1, T1 + i))                  # top
        faces.append((B0 + i + 1, B0 + i, B1 + i, B1 + i + 1))                  # bottom
        faces.append((T0 + i + 1, T0 + i, B0 + i, B0 + i + 1))                  # front (y0)
        faces.append((T1 + i, T1 + i + 1, B1 + i + 1, B1 + i))                  # back (y1)
    faces.append((T0, B0, B1, T1))
    faces.append((T0 + n - 1, T1 + n - 1, B1 + n - 1, B0 + n - 1))
    ob = mesh_obj(name, v, faces, material(name, rgb, rough=rough, spec=0.3), smooth=True)
    return ob


def ribbons_scene(spec, anc, h):
    w = A.col_cm
    t, dep, rb = A.rib_thick_cm, A.rib_depth_cm, A.ball_cm
    xlo, xhi = spec["x_range"]
    hs = A.rib_width_cm / (xhi - xlo)
    X0 = spec.get("left_cm", 0.45)
    ej = spec["ej"]
    curves = []
    cur_top = h - 0.52
    for k, cv in enumerate(spec["curves"]):
        x = np.linspace(xlo, xhi, 140)
        U = np.interp(x, cv["x"], cv["U"])
        U = (U - np.interp(cv["x_ref"], cv["x"], cv["U"])) / ej            # cm, zero at the ball's position
        z_top = cur_top - (U.max())                                       # the curve's maximum at cur_top
        Z = z_top + U                                                     # panel-local cm of the top surface
        X = X0 + (x - xlo) * hs
        curves.append((X, Z, cv, x, U, z_top))
        cur_top = Z.min() - t - spec.get("gap_cm", 0.42)
    low = min(c[1].min() for c in curves) - t
    if low < 0.12:
        print("WARNING ribbons do not fit: lowest point %.2f cm" % low)
    out = {}
    for k, (X, Z, cv, x, U, z_top) in enumerate(curves):
        strip("rib%d" % k, X, Z, t, dep, cv["rgb"])
        xs_ball = X0 + (cv["x_ref"] - xlo) * hs
        zb = float(np.interp(xs_ball, X, Z))
        slope = float(np.gradient(Z, X)[np.argmin(np.abs(X - xs_ball))])
        nrm = np.array([-slope, 1.0]) / math.hypot(slope, 1.0)
        c = (xs_ball + nrm[0] * rb * 1.0, 0.0, zb + nrm[1] * rb * 1.0)
        sphere("ball%d" % k, c, rb, (0.02, 0.02, 0.02), rough=0.22)
        anc.add("ball%d" % k, c)
        if cv.get("ghost_x") is not None:
            gx_ = X0 + (cv["ghost_x"] - xlo) * hs
            gz = float(np.interp(gx_, X, Z))
            sl = float(np.gradient(Z, X)[np.argmin(np.abs(X - gx_))])
            nn = np.array([-sl, 1.0]) / math.hypot(sl, 1.0)
            cg = (gx_ + nn[0] * rb, 0.0, gz + nn[1] * rb)
            sphere("ghost%d" % k, cg, rb, (0.02, 0.02, 0.02), rough=0.3, alpha=0.28)
            anc.add("ghost%d" % k, cg)
        # baseline anchors: same x extent, below the curve
        zb0 = float(Z.min() - t - 0.10)
        anc.add("base%d_0" % k, (X[0], 0.0, zb0))
        anc.add("base%d_1" % k, (X[-1], 0.0, zb0))
        lead = X <= X[0] + 1.35                      # the label spans the first 1.35 cm: clear the curve's highest point there
        anc.add("label%d" % k, (X[0], 0.0, float(Z[lead].max()) + 0.10))
        anc.add("curve%d_top" % k, (float(X[np.argmax(Z)]), 0.0, float(Z.max())))
        out[k] = dict(zmin=float(Z.min()), zmax=float(Z.max()), xs_ball=float(xs_ball))
        if spec.get("band") and k == spec["band"]["curve"]:
            kT = spec["band"]["kT"] / ej
            xb = X0 + (spec["band"]["x"] - xlo) * hs + rb * 2.6
            zb_floor = float(np.interp(xb, X, Z))
            bw = 0.05
            verts = [(xb - bw, -dep / 2 - 0.01, zb_floor), (xb + bw, -dep / 2 - 0.01, zb_floor),
                     (xb + bw, -dep / 2 - 0.01, zb_floor + kT), (xb - bw, -dep / 2 - 0.01, zb_floor + kT)]
            mesh_obj("band", verts + [(a_, b_ + dep + 0.02, c_) for a_, b_, c_ in verts],
                     [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)],
                     material("band", OKABE["vermillion"], rough=0.5))
            anc.add("band_0", (xb, 0.0, zb_floor))
            anc.add("band_1", (xb, 0.0, zb_floor + kT))
    # energy scale bar (anchors only): vertical, at the right
    barx = X0 + A.rib_width_cm + 0.30
    anc.add("scale_0", (barx, 0.0, 0.40))
    anc.add("scale_1", (barx, 0.0, 0.40 + spec["bar_J"] / ej))
    cam = ortho_camera((w / 2, 0.0, h / 2), 90.0, A.rib_elev, w)
    # lights: soft, from the front-top
    area_lights((w / 2, 0.0, h / 2), scale=1.0, k=A.light, az=90.0 - 90.0,
                spec=(("key", (-2.0, -1.4, 3.0), 400, 3.0), ("fill", (2.5, -0.6, 1.8), 150, 3.0), ("top", (0.0, 1.5, 3.2), 120, 3.0)))
    # re-add anchors after the camera exists (positions were queued before it)
    return out, curves


# ------------------------------------------------------------------ driver
def render_panel(build, w, h):
    reset()
    dev = setup_render(w, h)
    info = build()
    tmp = Path(tempfile.mkdtemp()) / "p.png"
    bpy.context.scene.render.filepath = str(tmp)
    t0 = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    dt = time.perf_counter() - t0
    img = bpy.data.images.load(str(tmp))
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    al = px[:, :, 3:4]
    px = px[:, :, :3] * al + np.array(BG, np.float32) * (1 - al)
    bpy.data.images.remove(img)
    return px, dt, dev, info


def main():
    global A, LUTS
    A = parse()
    LUTS = dict(np.load(DATA / "luts.npz"))
    L = dict(np.load(DATA / "lone.npz"))
    P = dict(np.load(DATA / "pair.npz"))
    phys = json.load(open(DATA / "hero_physics.json"))
    W = A.width_px
    pxcm = W / A.width_cm
    g = int(round(A.gap_cm * pxcm))
    cw, rh = (W - g) // 2, int(round(A.row_cm * pxcm))
    rhp = int(round(A.row_pair_cm * pxcm))
    rg = int(round(0.15 * pxcm))
    Wc, Hc = W, rh + rhp + rg
    canvas = np.ones((Hc, Wc, 3), np.float32) * np.array(BG, np.float32)
    pos = {"lone": (0, 0), "rib_lone": (cw + g, 0), "pair": (0, rh + rg), "rib_pair": (cw + g, rh + rg)}
    hpx = {"lone": rh, "rib_lone": rh, "pair": rhp, "rib_pair": rhp}
    overlay = {"px": [Wc, Hc], "cm": [A.width_cm, round(A.width_cm * Hc / Wc, 3)], "args": {k: v for k, v in vars(A).items()},
               "panels_px": {k: [*v, cw, hpx[k]] for k, v in pos.items()}, "panels": {}}
    # ---- arrows (world vectors in newtons; floor-plane projection is done by the camera)
    bl = int(np.nonzero(L["ids"] == L["blocker"])[0][0])
    pb = L["pos"][bl]
    drive = L["drive_N"][bl]
    # Force balance on the blocker, all along the door axis (the lateral components are <= 5 N and are not drawn): upward from the
    # blocker centre the drive, then the neighbours' push from the drive tip, then ORCA's rest drive from the push tip; downward
    # the wall force. drive + push = wall to 1e-3 N, so the stacked arrows and the wall arrow have equal length.
    ax = lambda v: np.array([float(v[0]), 0.0])
    drive_x, push_x, orca_x, wall_x = ax(drive), ax(L["partner_N"][bl]), ax(L["orca_N"]), ax(L["wall_N"][bl])
    mpn = A.arrow_m_per_n
    ar_lone = {"drive": (pb, drive_x), "wall": (pb, wall_x),
               "push": (pb + drive_x * mpn, push_x),
               "orca": (pb + (drive_x + push_x) * mpn, orca_x)}
    sin_el = math.sin(math.radians(A.elev))
    wm = A.col_cm / A.cm_per_m
    x_top = A.x0 + A.row_cm / (A.cm_per_m * sin_el)
    y_max = A.yc + wm / 2

    def scr(u_cm, v_cm):
        """floor point at printed offset (u from the panel's left edge, v from its top edge), in metres"""
        return (x_top - v_cm / (A.cm_per_m * sin_el), y_max - u_cm / A.cm_per_m)

    # scale-bar cluster (free top-left corner below the panel tag): 100 N parallel to the door axis (foreshortened like the
    # force arrows), 0.5 m along y (screen right), sharing the lower-left corner
    x100, y100 = scr(A.cluster_u, A.cluster_v)
    ar_lone["scale100"] = ((x100, y100), np.array([100.0, 0.0]))
    ar_lone["scale_half_m"] = ((x100, y100 - A.cluster_gap / A.cm_per_m), np.array([0.0, -0.5 / A.arrow_m_per_n]))
    pts_lone = {"coord_0": (A.x0 + 0.02, pb[1]), "coord_1": (x_top - 0.14, pb[1]), "blocker": (pb[0], pb[1]),
                "held_ul": (pb[0] + 0.5 * float(L["radius"][bl]), pb[1] + 0.866 * float(L["radius"][bl])),   # rim point 60 deg left of straight up
                "n38": (L["pos"][1][0], L["pos"][1][1]), "n54": (L["pos"][2][0], L["pos"][2][1]),
                "box_x0": (A.x0, A.yc - wm / 2)}
    k0, k1 = 0, 1                       # pair members: lower, upper
    mp = P["pos"][k0]
    ar_pair = {"drive": (mp, P["drive_N"][k0]), "wall": (mp, P["wall_N"][k0]), "partner": (mp, P["partner_N"][k0])}
    xm = float(np.mean(P["pos"][:, 0]))
    pts_pair = {"coord_0": (xm, A.yc - 1.0 + 0.1), "coord_1": (xm, A.yc + 1.0 - 0.1), "member0": tuple(P["pos"][0]),
                "member1": tuple(P["pos"][1]), "between": (xm, float(np.mean(P["pos"][:, 1])))}
    # ---- ribbons
    xlo, xhi = [float(v) for v in A.lone_x.split(",")]
    xf = float(L["frozen_x"])         # both balls sit at the frozen position, which is the own-drive minimum (neighbours pinned)
    x_rib = L["rib_x"]
    Uo, Ua = L["rib_Uown"], L["rib_Uadd"]
    rep = phys["lone"]["ribbon"]
    spec_lone = {"x_range": (xlo, xhi), "ej": A.lone_ej, "bar_J": 10.0, "gap_cm": 0.52,
                 "curves": [{"x": x_rib, "U": Uo, "x_ref": xf, "rgb": OKABE["black"], "ghost_x": None},
                            {"x": x_rib, "U": Ua, "x_ref": xf, "rgb": OKABE["blue"], "ghost_x": xhi - 0.012}],
                 "band": {"curve": 0, "kT": float(L["kT_J"]), "x": xf}}
    cs, U0, Ub = P["rib_c"], P["rib_U0"], P["rib_Ub"]
    c0 = float(np.interp(0.0, cs, Ub))
    spec_pair = {"x_range": (-A.pair_c, A.pair_c), "ej": A.pair_ej, "bar_J": 0.5, "gap_cm": 0.52,
                 "curves": [{"x": cs, "U": U0, "x_ref": 0.0, "rgb": OKABE["black"], "ghost_x": None},
                            {"x": cs, "U": Ub, "x_ref": 0.0, "rgb": OKABE["yellow"], "ghost_x": A.pair_c - 0.006}]}
    jobs = {"lone": lambda anc: floor_scene(L, anc, "lone", {"arrows": ar_lone, "points": pts_lone}),
            "pair": lambda anc: floor_scene(P, anc, "pair", {"arrows": ar_pair, "points": pts_pair}),
            "rib_lone": lambda anc: ribbons_scene(spec_lone, anc, A.row_cm),
            "rib_pair": lambda anc: ribbons_scene(spec_pair, anc, A.row_pair_cm)}
    times, dev = {}, None
    for key in A.panels.split(","):
        anc = Anchors(pos[key], (cw, hpx[key]), (Wc, Hc))

        # anchors need the camera: build, then re-project after construction (the camera is created inside build)
        if A.assemble:
            z = np.load(Path(A.cache_dir) / (key + ".npz"), allow_pickle=True)
            px, dt, dev, info = z["px"], float(z["dt"]), str(z["dev"]), {}
            anc.pts = json.loads(str(z["anchors"]))
        else:
            px, dt, dev, info = render_panel(lambda: _build_and_project(jobs[key], anc), cw, hpx[key])
            if A.cache_dir:
                os.makedirs(A.cache_dir, exist_ok=True)
                np.savez(Path(A.cache_dir) / (key + ".npz"), px=px, dt=dt, dev=dev, anchors=json.dumps(anc.pts))
        times[key] = round(dt, 1)
        x, y = pos[key]
        canvas[Hc - y - hpx[key]:Hc - y, x:x + cw] = px
        overlay["panels"][key] = {"anchors": anc.pts, "info": info if isinstance(info, dict) else {}}
    if A.cache_dir and not A.assemble:
        print("PANEL", json.dumps({"panels": A.panels, "times": times, "device": dev}))
        return
    reset()
    out = bpy.data.images.new("hero", Wc, Hc, alpha=False)
    out.colorspace_settings.name = "sRGB"
    out.pixels.foreach_set(np.concatenate([canvas, np.ones((Hc, Wc, 1), np.float32)], axis=2).ravel())
    os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True)
    out.filepath_raw = os.path.abspath(A.out)
    out.file_format = "PNG"
    out.save()
    overlay["render"] = {"samples": A.samples, "device": dev, "panel_render_s": times, "total_render_s": round(sum(times.values()), 1)}
    overlay["arrows_N"] = {"lone": {k: [list(map(float, v[0])), list(map(float, v[1]))] for k, v in ar_lone.items()},
                           "pair": {k: [list(map(float, v[0])), list(map(float, v[1]))] for k, v in ar_pair.items()},
                           "metres_per_newton": A.arrow_m_per_n}
    overlay["ribbons"] = {"lone": {"ej_J_per_cm": A.lone_ej, "x_range_m": [xlo, xhi], "rib_width_cm": A.rib_width_cm, "bar_J": 10.0,
                                   "kT_J": float(L["kT_J"])},
                          "pair": {"ej_J_per_cm": A.pair_ej, "c_range_m": [-A.pair_c, A.pair_c], "rib_width_cm": A.rib_width_cm, "bar_J": 0.5}}
    overlay["lone_box_m"] = {"x": [A.x0, A.x0 + A.row_cm / (A.cm_per_m * math.sin(math.radians(A.elev)))],
                             "y": [A.yc - A.col_cm / A.cm_per_m / 2, A.yc + A.col_cm / A.cm_per_m / 2]}
    Path(A.overlay).parent.mkdir(parents=True, exist_ok=True)
    Path(A.overlay).write_text(json.dumps(overlay, indent=1))
    print("HERO", json.dumps({"px": [Wc, Hc], "cm": overlay["cm"], **overlay["render"]}))


def _build_and_project(fn, anc):
    """Build the scene with deferred anchors: the camera must exist before world_to_camera_view."""
    pending = []

    class Deferred:
        off, size, canvas, pts = anc.off, anc.size, anc.canvas, anc.pts

        def add(self, name, p):
            pending.append((name, p))
    info = fn(Deferred())
    for name, p in pending:
        anc.add(name, p)
    return info


main()
