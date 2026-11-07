"""Headless Blender render of the hero figure (Fig. 1) from the .npz files of export_hero.py.

    blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- \\
        --layout A --width-px 900 --samples 24 --out figures/hero/storyboard/option_A.png

Nothing in the image but data: agents are cylinders of their true radius (height stylised,
--agent-height) coloured by stuck-alone margin; walls are thin slabs along the model's
zero-thickness segments; the floor carries the backward wall force on a lone r = 0.25 m agent;
the pair landscapes are the rest-state energy U (forward positions relaxed) over the two
members' lateral displacements, at b = 0 and just past the fold. No text, labels or legends.

Layouts (canvas aspect = height/width of the printed figure at 12.2 cm):
  A  two panels: oblique lone-trap scene left; pair landscapes before/after stacked right
  B  one continuous scene: lone-trap stage with both landscapes standing beside it
  C  two rows: wide lone-trap strip on top; pair standoff in its geometry + both landscapes below
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
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "derived" / "hero"
ARGS = None
BG = (0.955, 0.955, 0.950)          # neutral warm-white background (sRGB)
WALL_RGB = (0.52, 0.52, 0.52)
INACCESSIBLE_RGB = (0.86, 0.86, 0.85)


def srgb_to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", choices="ABC", default="A")
    ap.add_argument("--out", required=True)
    ap.add_argument("--width-px", type=int, default=900)
    ap.add_argument("--width-cm", type=float, default=12.2)
    ap.add_argument("--height-cm", type=float, default=None, help="default per layout")
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--device", choices=["GPU", "CPU"], default="GPU")
    ap.add_argument("--agent-cmap", default="cividis")
    ap.add_argument("--field-cmap", default="magma_r")
    ap.add_argument("--margin-span", type=float, default=150.0, help="N; margin +-span maps to ramp ends")
    ap.add_argument("--force-max", type=float, default=1000.0, help="N; floor ramp top (clipped above)")
    ap.add_argument("--force-min", type=float, default=1.0, help="N; floor ramp bottom for --force-scale log")
    ap.add_argument("--force-scale", choices=["log", "linear"], default="log")
    ap.add_argument("--light", type=float, default=0.6, help="overall light energy factor")
    ap.add_argument("--agent-height", type=float, default=0.20, help="m, stylised")
    ap.add_argument("--wall-height", type=float, default=0.42, help="m, stylised")
    ap.add_argument("--wall-thickness", type=float, default=0.03, help="m, display only")
    ap.add_argument("--surf-common", type=float, default=0.28, help="m, |common lateral shift| shown")
    ap.add_argument("--surf-opposed", type=float, default=0.04, help="m, |opposed lateral shift| shown")
    ap.add_argument("--surf-aniso", type=float, default=3.0, help="display stretch of the opposed axis")
    ap.add_argument("--surf-umin", type=float, default=-1.2, help="J, clip floor of the landscape")
    ap.add_argument("--surf-umax", type=float, default=1.0, help="J, clip top of the landscape")
    ap.add_argument("--surf-zscale", type=float, default=0.28, help="scene units per J at size 1")
    ap.add_argument("--surf-half", type=int, default=1, help="1: show o >= 0 only, so the front edge is the valley-floor profile")
    ap.add_argument("--world-strength", type=float, default=0.6)
    ap.add_argument("--cam", default="{}", help="JSON overrides: {panel: {loc: [..], target: [..], lens: f}}")
    a = ap.parse_args(argv)
    a.cam = json.loads(a.cam)
    if a.height_cm is None:
        a.height_cm = {"A": 5.4, "B": 4.6, "C": 7.6}[a.layout]
    return a


# ------------------------------------------------------------------ scene plumbing
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_render(a, w, h):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.threads_mode = "FIXED"
    sc.render.threads = a.threads
    sc.cycles.samples = a.samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.view_settings.view_transform = "Standard"     # keep ramp colours as specified
    sc.view_settings.look = "None"
    sc.render.film_transparent = True              # composited over BG afterwards
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.cycles.device = "CPU"
    if a.device == "GPU":
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("METAL",):
            try:
                prefs.compute_device_type = kind
                prefs.get_devices()
                devs = [d for d in prefs.devices if d.type == kind]
                if devs:
                    for d in prefs.devices:
                        d.use = d.type == kind
                    sc.cycles.device = "GPU"
                    break
            except TypeError:
                pass
    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb_to_linear(BG), 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = a.world_strength
    return sc.cycles.device


def material(name, rgb=None, attr=None, image=None, rough=0.55, spec=0.25):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = spec
    if rgb is not None:
        p.inputs["Base Color"].default_value = (*srgb_to_linear(rgb), 1)
    if attr is not None:
        n = nt.nodes.new("ShaderNodeVertexColor")
        n.layer_name = attr
        nt.links.new(n.outputs["Color"], p.inputs["Base Color"])
    if image is not None:
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = image
        n.interpolation = "Closest"
        nt.links.new(n.outputs["Color"], p.inputs["Base Color"])
    return m


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def mesh_obj(name, verts, faces, mat, colors=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    if colors is not None:
        ca = me.color_attributes.new("col", "FLOAT_COLOR", "POINT")
        rgba = np.column_stack([srgb_to_linear(colors), np.ones(len(colors))])
        ca.data.foreach_set("color", rgba.ravel().astype(np.float32))
    if smooth:
        me.shade_smooth()
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me))


def cylinder(name, x, y, r, h, rgb, z0=0.0, n=96):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ring = np.column_stack([x + r * np.cos(th), y + r * np.sin(th)])
    verts = [(*p, z0) for p in ring] + [(*p, z0 + h) for p in ring]
    faces = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    faces += [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    ob = mesh_obj(name, verts, faces, material(name, rgb, rough=0.45, spec=0.35))
    for poly in ob.data.polygons:          # smooth sides, flat caps
        poly.use_smooth = len(poly.vertices) == 4
    return ob


def slab(name, p0, p1, thick, h, rgb):
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
    return mesh_obj(name, verts, faces, material(name, rgb, rough=0.7, spec=0.2))


def lut(name):
    return np.load(DATA / "luts.npz")[name]


def ramp(values, lo, hi, name):
    L = lut(name)
    t = np.clip((np.asarray(values, float) - lo) / (hi - lo), 0, 1)
    return L[np.round(t * 255).astype(int)]


def clip_segment(p0, p1, box):
    """Liang-Barsky clip of segment p0-p1 to box (x0, x1, y0, y1)."""
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


# ------------------------------------------------------------------ builders
def build_floor_scene(a, D, offset=(0.0, 0.0), box=None, show_agents=True, margin_key="margin_N"):
    """Floor field + walls + agents of one snapshot, translated by -door + offset so the door
    centre sits at `offset`. Returns the scene-space box (x0, x1, y0, y1)."""
    gx, gy = D["grid_x"], D["grid_y"]
    door = np.array([10.0, 5.0])
    sh = np.asarray(offset) - door
    if box is None:
        box = (gx[0], gx[-1], gy[0], gy[-1])
    ix = (gx >= box[0] - 1e-9) & (gx <= box[1] + 1e-9)
    iy = (gy >= box[2] - 1e-9) & (gy <= box[3] + 1e-9)
    F = D["wall_back_N"][np.ix_(iy, ix)]
    feas = D["feasible"][np.ix_(iy, ix)]
    if a.force_scale == "log":
        rgb = ramp(np.log10(np.maximum(F, 1e-12)), np.log10(a.force_min), np.log10(a.force_max), a.field_cmap)
    else:
        rgb = ramp(F, 0.0, a.force_max, a.field_cmap)
    rgb[~feas] = INACCESSIBLE_RGB
    h_, w_ = F.shape
    img = bpy.data.images.new("floor%d" % len(bpy.data.images), w_, h_, alpha=True)
    img.colorspace_settings.name = "sRGB"
    px = np.concatenate([rgb, np.ones((h_, w_, 1))], axis=2).astype(np.float32)
    img.pixels.foreach_set(px.ravel())
    img.pack()
    x0, x1, y0, y1 = gx[ix][0], gx[ix][-1], gy[iy][0], gy[iy][-1]
    dx, dy = gx[1] - gx[0], gy[1] - gy[0]
    X0, X1, Y0, Y1 = x0 - dx / 2 + sh[0], x1 + dx / 2 + sh[0], y0 - dy / 2 + sh[1], y1 + dy / 2 + sh[1]
    me = bpy.data.meshes.new("floor")
    me.from_pydata([(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = (u, v)
    me.materials.append(material("floor", image=img, rough=0.9, spec=0.1))
    link(bpy.data.objects.new("floor", me))
    fb = (x0 - dx / 2, x1 + dx / 2, y0 - dy / 2, y1 + dy / 2)
    for k, w in enumerate(D["walls"]):
        seg = clip_segment(w[:2], w[2:], fb)
        if seg is not None:
            slab("wall%d" % k, seg[0] + sh, seg[1] + sh, a.wall_thickness, a.wall_height, WALL_RGB)
    if show_agents:
        cols = ramp(D[margin_key], -a.margin_span, a.margin_span, a.agent_cmap)
        for k, (p, r) in enumerate(zip(D["pos"], D["radius"])):
            if fb[0] - r < p[0] < fb[1] + r and fb[2] - r < p[1] < fb[3] + r:
                cylinder("agent%d" % k, p[0] + sh[0], p[1] + sh[1], float(r), a.agent_height, cols[k])
    return (X0, X1, Y0, Y1)


def bilinear(dy, U, a_, b_):
    """U sampled on the regular (dy_lo, dy_hi) grid, evaluated at (a_, b_) by bilinear interpolation."""
    h = dy[1] - dy[0]
    fi = np.clip((a_ - dy[0]) / h, 0, len(dy) - 1.000001)
    fj = np.clip((b_ - dy[0]) / h, 0, len(dy) - 1.000001)
    i, j = fi.astype(int), fj.astype(int)
    u, v = fi - i, fj - j
    return (U[i, j] * (1 - u) * (1 - v) + U[i + 1, j] * u * (1 - v) + U[i, j + 1] * (1 - u) * v
            + U[i + 1, j + 1] * u * v)


def build_surface(a, P, tag, centre=(0.0, 0.0), size=1.0, z0=0.0, n=161, rot_deg=0.0):
    """Landscape U_relax(dy_lo, dy_hi), resampled onto the common shift c = (dy_lo + dy_hi)/sqrt 2
    (scene +x, |c| <= surf-common) and the opposed shift o = (dy_hi - dy_lo)/sqrt 2 (scene +y,
    |o| <= surf-opposed, stretched by surf-aniso). Height linear in U between surf-umin and
    surf-umax (clipped outside), coloured by U with the field ramp. `size` = scene length of the
    common axis."""
    dy = P["dy"]
    U = P[f"U_relax_{tag}_J"]
    c = np.linspace(-a.surf_common, a.surf_common, n)
    m = max(9, int(round(n * a.surf_opposed / a.surf_common)) | 1)
    o = np.linspace(0.0 if a.surf_half else -a.surf_opposed, a.surf_opposed, m)
    C, O = np.meshgrid(c, o, indexing="ij")
    Ug = bilinear(dy, U, (C - O) / np.sqrt(2), (C + O) / np.sqrt(2))
    Uc = np.clip(Ug, a.surf_umin, a.surf_umax)
    s = size / (2 * a.surf_common)
    th = math.radians(rot_deg)
    rot = lambda x, y: (x * math.cos(th) - y * math.sin(th) + centre[0], x * math.sin(th) + y * math.cos(th) + centre[1])  # noqa: E731
    X, Y = rot(C * s, O * s * a.surf_aniso)
    Z = z0 + (Uc - a.surf_umin) * a.surf_zscale * size
    verts = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    faces = [(i * m + j, (i + 1) * m + j, (i + 1) * m + j + 1, i * m + j + 1) for i in range(n - 1) for j in range(m - 1)]
    cols = ramp(Uc.ravel(), a.surf_umin, a.surf_umax, a.field_cmap)
    ob = mesh_obj("surf_" + tag, verts, faces, material("surf_" + tag, attr="col", rough=0.5, spec=0.3), cols, smooth=True)
    # thin base frame = the two axes (common, opposed), at the clip floor
    ex, ey = size / 2, a.surf_opposed * s * a.surf_aniso
    ey0 = 0.0 if a.surf_half else -ey
    t = size * 0.006
    for nm, p0, p1 in (("ax_c", rot(-ex, ey0), rot(ex, ey0)), ("ax_o", rot(-ex, ey0), rot(-ex, ey))):
        ob_ = slab(nm + tag, p0, p1, t, t, (0.25, 0.25, 0.25))
        if ob_ is not None:
            ob_.location.z = z0 - t
    # the snapshot's rest state (c = o = 0) as a small sphere resting on the surface
    zc = z0 + (np.clip(float(bilinear(dy, U, np.array(0.0), np.array(0.0))), a.surf_umin, a.surf_umax) - a.surf_umin) * a.surf_zscale * size
    rad = size * 0.022
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, segments=32, ring_count=16, location=(centre[0], centre[1], zc + rad))
    sp = bpy.context.active_object
    sp.data.materials.append(material("state" + tag, (0.12, 0.12, 0.12), rough=0.4))
    bpy.ops.object.shade_smooth()
    return ob


def lights(target, scale=1.0, k=None):
    k = ARGS.light if k is None else k
    t = Vector(target)
    for nm, off, energy, size in (("key", (-2.2, -2.6, 3.6), 520, 2.6), ("fill", (3.0, -1.0, 2.2), 160, 3.0),
                                  ("rim", (0.5, 3.2, 2.5), 140, 2.0)):
        ld = bpy.data.lights.new(nm, "AREA")
        ld.energy = energy * scale ** 2 * k
        ld.size = size * scale
        ob = link(bpy.data.objects.new(nm, ld))
        ob.location = t + Vector(off) * scale
        ob.rotation_euler = (t - ob.location).to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=50.0, ortho=None):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.sensor_fit = "HORIZONTAL"
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    ob = link(bpy.data.objects.new("cam", cd))
    ob.location = Vector(loc)
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob


def frame(a, panel, azim, elev, lens=40.0, margin=0.03, box=None):
    """Perspective camera looking at the scene from azimuth/elevation (deg; azimuth 0 = from -x,
    90 = from -y), with distance and lateral offset solved so every mesh vertex projects inside
    the frame with the given margin. --cam {panel: {azim, elev, lens, margin}} overrides."""
    from bpy_extras.object_utils import world_to_camera_view
    o = a.cam.get(panel, {})
    azim, elev, lens, margin = (o.get("azim", azim), o.get("elev", elev), o.get("lens", lens), o.get("margin", margin))
    bpy.context.view_layer.update()
    if box is not None:     # frame a fixed box (x0, x1, y0, y1, z0, z1) instead of the meshes
        P = np.array([(x, y, z) for x in box[:2] for y in box[2:4] for z in box[4:]], float)
    else:
        pts = []
        for ob in bpy.context.scene.objects:
            if ob.type == "MESH":
                mw = ob.matrix_world
                pts += [mw @ v.co for v in ob.data.vertices]
        P = np.array([tuple(p) for p in pts])
    tgt = Vector(((P.min(0) + P.max(0)) / 2).tolist())
    az, el = math.radians(azim), math.radians(elev)
    d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), math.sin(el)))
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.sensor_fit = "HORIZONTAL"
    cam = link(bpy.data.objects.new("cam", cd))
    sc = bpy.context.scene
    sc.camera = cam
    span = float(np.linalg.norm(P.max(0) - P.min(0)))
    dist = 2.0 * span
    for _ in range(12):
        cam.location = tgt + d * dist
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        uv = np.array([tuple(world_to_camera_view(sc, cam, Vector(p)))[:2] for p in P])
        lo, hi = uv.min(0), uv.max(0)
        c = (lo + hi) / 2 - 0.5
        # shift the target along camera right/up to centre the projection
        R = cam.matrix_world.to_3x3()
        right, up = R @ Vector((1, 0, 0)), R @ Vector((0, 1, 0))
        wv = 2 * dist * 18.0 / lens               # approx. view width at distance (36 mm sensor)
        hv = wv * sc.render.resolution_y / sc.render.resolution_x
        tgt = tgt + right * (c[0] * wv) + up * (c[1] * hv)
        fill = max((hi[0] - lo[0]) / (1 - 2 * margin), (hi[1] - lo[1]) / (1 - 2 * margin))
        dist *= 0.35 + 0.65 * fill
    cam.location = tgt + d * dist
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()


# ------------------------------------------------------------------ panels
def panel_lone(a, L, w, h):
    build_floor_scene(a, L, box=(8.7, 10.5, 3.9, 6.1))
    frame(a, "lone", azim=35, elev=48, lens=45)
    lights((-0.3, 0, 0))


def panel_lone_wide(a, L, w, h):
    build_floor_scene(a, L, box=(8.7, 10.6, 3.3, 6.7))
    frame(a, "lone_wide", azim=4, elev=42, lens=45)
    lights((-0.3, 0, 0))


def surface_box(a, centre=(0.0, 0.0), size=1.0):
    s = size / (2 * a.surf_common)
    ey = a.surf_opposed * s * a.surf_aniso
    return (centre[0] - size / 2, centre[0] + size / 2, centre[1] + (0 if a.surf_half else -ey), centre[1] + ey,
            0.0, (a.surf_umax - a.surf_umin) * a.surf_zscale * size)


def panel_surface(a, P, tag, w, h):
    build_surface(a, P, tag)
    frame(a, "surf", azim=86, elev=24, lens=50, box=surface_box(a))   # same camera before/after
    lights((0, 0, 0.2), scale=0.55)


def panel_pair_floor(a, P, w, h):
    build_floor_scene(a, P, box=(8.9, 10.5, 4.0, 6.0))
    frame(a, "pair_floor", azim=35, elev=48, lens=45)
    lights((-0.3, 0, 0))


def scene_B(a, L, P, w, h):
    """One continuous stage seen from the room towards the door: the lone-trap floor scene on the
    left, both landscapes standing on the same ground to its right (common shift running left to
    right, before the fold nearer the room scene)."""
    build_floor_scene(a, L, box=(8.8, 10.5, 4.0, 6.0))
    sz = 1.5
    build_surface(a, P, "b0", centre=(-0.6, -2.15), size=sz, rot_deg=-90)
    build_surface(a, P, "bfold", centre=(-0.6, -3.95), size=sz, rot_deg=-90)
    frame(a, "B", azim=0, elev=30, lens=85)
    lights((-0.4, -1.3, 0), scale=1.5)


# ------------------------------------------------------------------ compositing
def render_panel(a, builder, w, h, *args):
    reset()
    dev = setup_render(a, w, h)
    builder(a, *args, w, h)
    tmp = Path(tempfile.mkdtemp()) / "p.png"
    bpy.context.scene.render.filepath = str(tmp)
    t0 = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    dt = time.perf_counter() - t0
    img = bpy.data.images.load(str(tmp))
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    al = px[:, :, 3:4]
    px = px[:, :, :3] * al + np.array(BG, np.float32) * (1 - al)   # straight alpha over BG
    return px, dt, dev


def main():
    global ARGS
    a = ARGS = parse()
    W = a.width_px
    H = int(round(W * a.height_cm / a.width_cm))
    L = dict(np.load(DATA / "lone_trap.npz"))
    P = dict(np.load(DATA / "pair_landscape.npz"))
    canvas = np.ones((H, W, 3), np.float32) * np.array(BG, np.float32)   # sRGB, bottom row first
    g = max(2, W // 150)                                                   # gutter
    # panel rects in canvas pixels (x, y_from_top, w, h)
    if a.layout == "A":
        wl = int(W * 0.56)
        wr = W - wl - g
        hh = (H - g) // 2
        panels = [((0, 0, wl, H), panel_lone, (L,)),
                  ((wl + g, 0, wr, hh), panel_surface, (P, "b0")),
                  ((wl + g, hh + g, wr, H - hh - g), panel_surface, (P, "bfold"))]
    elif a.layout == "B":
        panels = [((0, 0, W, H), scene_B, (L, P))]
    else:
        ht = int(H * 0.47)
        hb = H - ht - g
        w3 = (W - 2 * g) // 3
        panels = [((0, 0, W, ht), panel_lone_wide, (L,)),
                  ((0, ht + g, w3, hb), panel_pair_floor, (P,)),
                  ((w3 + g, ht + g, w3, hb), panel_surface, (P, "b0")),
                  ((2 * w3 + 2 * g, ht + g, W - 2 * w3 - 2 * g, hb), panel_surface, (P, "bfold"))]
    times = []
    dev = None
    for (x, y, w, h), fn, args in panels:
        px, dt, dev = render_panel(a, fn, w, h, *args)
        times.append(round(dt, 1))
        y0 = H - y - h                     # Blender pixel rows start at the bottom
        canvas[y0:y0 + h, x:x + w] = px
    reset()
    out = bpy.data.images.new("hero", W, H, alpha=False)
    out.colorspace_settings.name = "sRGB"
    out.pixels.foreach_set(np.concatenate([canvas, np.ones((H, W, 1), np.float32)], axis=2).ravel())
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    out.filepath_raw = os.path.abspath(a.out)
    out.file_format = "PNG"
    out.save()
    meta = {"layout": a.layout, "px": [W, H], "cm": [a.width_cm, a.height_cm], "samples": a.samples,
            "device": dev, "threads": a.threads, "panel_render_s": times, "total_render_s": round(sum(times), 1)}
    print("HERO", json.dumps(meta))
    Path(a.out).with_suffix(".json").write_text(json.dumps({**meta, "args": {k: v for k, v in vars(a).items()}}, indent=1))


main()
