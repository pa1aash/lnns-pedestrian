"""Headless Blender render of the hero figure (Fig. 1, storyboard option C) from the .npz files of export_hero.py.

    blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- \\
        --width-px 900 --samples 24 --out figures/hero/storyboard/preview.png

Nothing in the image but data. Agents are cylinders of their true radius (height stylised) coloured by
stuck-alone margin, with a thin dark edge; walls are thin slabs along the model's zero-thickness segments;
the floor carries the backward wall force on a lone r = 0.25 m agent (log colour scale).
Both floor scenes (top: lone trap; bottom left: pair standoff) use the same orthographic camera elevation and
the same pixels-per-metre, so a metre has one length in both. The two landscapes (bottom right, stacked)
are the rest-state energy U over the common shift c = (dy_lo + dy_hi)/2 and the opposed shift
o = (dy_hi - dy_lo)/2 of the pair, both in metres on one horizontal scale (true 1:1 aspect), height linear
in U with one scale (--surf-zscale metres per joule), clipped to [--surf-umin, --surf-umax]. No text.

Layout (canvas = 12.2 cm wide): top row lone-trap strip; bottom row pair floor | landscape before the fold
over landscape after it.
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
    ap.add_argument("--out", required=True)
    ap.add_argument("--width-px", type=int, default=900)
    ap.add_argument("--width-cm", type=float, default=12.2)
    ap.add_argument("--height-cm", type=float, default=0.0, help="0: from the layout")
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--tile", type=int, default=0, help="Cycles tile size (0: default)")
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
    ap.add_argument("--elev", type=float, default=40.0, help="deg, camera elevation of both floor scenes")
    ap.add_argument("--azim", type=float, default=0.0, help="deg, camera azimuth of both floor scenes (0: looking +x, screen right = +y)")
    ap.add_argument("--floor-span-m", type=float, default=3.4, help="m of floor across the full-width top panel; sets the one pixels-per-metre")
    ap.add_argument("--pair-span-m", type=float, default=1.56, help="m of floor across the pair panel (same pixels-per-metre)")
    ap.add_argument("--land-frac", type=float, default=0.0, help="landscape column width fraction (0: whatever the pair panel leaves)")
    ap.add_argument("--crop-x0", type=float, default=9.1)
    ap.add_argument("--crop-x1", type=float, default=10.58)
    ap.add_argument("--pair-x0", type=float, default=9.1, help="near crop edge of the pair panel (same elevation and scale)")
    ap.add_argument("--panels", default="top,pair,b0,bfold")
    ap.add_argument("--skirt", type=float, default=0.03, help="m, depth of the rim under the landscape edges")
    ap.add_argument("--bevel", type=float, default=0.0, help="m, outward slope of the dark rim (outlines the landscape from above)")
    ap.add_argument("--outline", type=float, default=0.006, help="m, width of the dark outline strip on the landscape boundary")
    ap.add_argument("--edge", type=float, default=0.008, help="m, dark shading edge around each agent cylinder")
    ap.add_argument("--land-elev", type=float, default=68.0, help="deg, camera elevation of the landscapes")
    ap.add_argument("--land-azim", type=float, default=90.0, help="deg, landscape azimuth (90 = from -y, common axis left to right)")
    ap.add_argument("--land-margin", type=float, default=0.04)
    ap.add_argument("--surf-c", type=float, default=0.30, help="m, |common shift| shown")
    ap.add_argument("--surf-o", type=float, default=0.04, help="m, |opposed shift| shown")
    ap.add_argument("--surf-umin", type=float, default=-1.2, help="J, clip floor of the landscape")
    ap.add_argument("--surf-umax", type=float, default=0.6, help="J, clip top of the landscape")
    ap.add_argument("--surf-zscale", type=float, default=0.12, help="m of display height per joule (one scale for both landscapes)")
    ap.add_argument("--world-strength", type=float, default=0.6)
    ap.add_argument("--cam", default="{}", help="JSON overrides: {panel: {loc: [..], target: [..], lens: f}}")
    a = ap.parse_args(argv)
    a.cam = json.loads(a.cam)
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
    if a.tile:
        sc.cycles.use_auto_tile = True
        sc.cycles.tile_size = a.tile
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
EDGE_RGB = (0.10, 0.10, 0.10)


def build_floor_scene(a, D, box, margin_key="margin_N"):
    """Floor field + walls + agents of one snapshot, in the snapshot's own world coordinates,
    cropped to box = (x0, x1, y0, y1)."""
    gx, gy = D["grid_x"], D["grid_y"]
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
    X0, X1, Y0, Y1 = x0 - dx / 2, x1 + dx / 2, y0 - dy / 2, y1 + dy / 2
    me = bpy.data.meshes.new("floor")
    me.from_pydata([(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = (u, v)
    me.materials.append(material("floor", image=img, rough=0.9, spec=0.1))
    link(bpy.data.objects.new("floor", me))
    fb = (X0, X1, Y0, Y1)
    for k, w in enumerate(D["walls"]):
        seg = clip_segment(w[:2], w[2:], fb)
        if seg is not None:
            slab("wall%d" % k, seg[0], seg[1], a.wall_thickness, a.wall_height, WALL_RGB)
    cols = ramp(D[margin_key], -a.margin_span, a.margin_span, a.agent_cmap)
    for k, (p, r) in enumerate(zip(D["pos"], D["radius"])):
        if fb[0] - r < p[0] < fb[1] + r and fb[2] - r < p[1] < fb[3] + r:
            # dark edge: a slightly wider, slightly lower cylinder under the coloured one
            cylinder("edge%d" % k, p[0], p[1], float(r) + a.edge, a.agent_height - 0.002, EDGE_RGB)
            cylinder("agent%d" % k, p[0], p[1], float(r), a.agent_height, cols[k])
    return fb


def build_surface(a, P, tag):
    """Landscape U(c, o) in metres: x = common shift c, y = opposed shift o (same metre scale),
    z = (clip(U) - umin) * zscale. Coloured by U with the field ramp."""
    cc, oo = P["co_c"], P["co_o"]
    sel_c, sel_o = np.abs(cc) <= a.surf_c + 1e-9, np.abs(oo) <= a.surf_o + 1e-9
    cc, oo = cc[sel_c], oo[sel_o]
    U = P[f"U_co_{tag}_J"][np.ix_(sel_c, sel_o)]
    # linear upsampling x2 (the export grid is 5 mm), then clip
    f = 2
    cu = np.linspace(cc[0], cc[-1], (len(cc) - 1) * f + 1)
    ou = np.linspace(oo[0], oo[-1], (len(oo) - 1) * f + 1)
    U = np.array([np.interp(ou, oo, row) for row in U])
    U = np.array([np.interp(cu, cc, U[:, j]) for j in range(U.shape[1])]).T
    cc, oo = cu, ou
    n, m = U.shape
    Uc = np.clip(U, a.surf_umin, a.surf_umax)
    C, O = np.meshgrid(cc, oo, indexing="ij")
    Z = (Uc - a.surf_umin) * a.surf_zscale
    verts = np.column_stack([C.ravel(), O.ravel(), Z.ravel()])
    faces = [(i * m + j, (i + 1) * m + j, (i + 1) * m + j + 1, i * m + j + 1) for i in range(n - 1) for j in range(m - 1)]
    cols = ramp(Uc.ravel(), a.surf_umin, a.surf_umax, a.field_cmap)
    # skirts: vertical walls from each edge down to the base plane, edge colours copied
    idx = np.arange(n * m).reshape(n, m)
    edges = [idx[:, 0], idx[:, -1], idx[0, :], idx[-1, :]]
    normals = [(-1.0, 0.0), (1.0, 0.0), (0.0, -1.0), (0.0, 1.0)]    # outward, per edge in `edges`
    normals = [(0.0, -1.0), (0.0, 1.0), (-1.0, 0.0), (1.0, 0.0)]
    extra_v, extra_c = [], []
    for e, nrm in zip(edges, normals):
        base = len(verts) + len(extra_v)
        for k in e:
            extra_v.append((verts[k][0] + nrm[0] * a.bevel, verts[k][1] + nrm[1] * a.bevel, verts[k][2] - a.skirt))
            extra_c.append(EDGE_RGB)
        for q in range(len(e) - 1):
            faces.append((e[q], e[q + 1], base + q + 1, base + q))
    # thin dark outline on the top surface along its four boundary edges (keeps the pale low-energy ends visible)
    for e, nrm in zip(edges, normals):
        base = len(verts) + len(extra_v)
        for k in e:
            extra_v.append((verts[k][0] - nrm[0] * a.outline, verts[k][1] - nrm[1] * a.outline, verts[k][2] + 0.0006))
            extra_v.append((verts[k][0], verts[k][1], verts[k][2] + 0.0006))
            extra_c += [EDGE_RGB, EDGE_RGB]
        for q in range(len(e) - 1):
            faces.append((base + 2 * q, base + 2 * q + 1, base + 2 * q + 3, base + 2 * q + 2))
    verts = np.vstack([verts, np.array(extra_v)])
    cols = np.vstack([cols, np.array(extra_c)])
    ob = mesh_obj("surf_" + tag, verts, faces, material("surf_" + tag, attr="col", rough=0.5, spec=0.3), cols, smooth=False)
    for k, poly in enumerate(ob.data.polygons):      # smooth the relief, keep the skirts flat
        poly.use_smooth = k < (n - 1) * (m - 1)
    # frozen state (c = o = 0) as a small sphere resting on the surface
    i0, j0 = int(np.argmin(np.abs(cc))), int(np.argmin(np.abs(oo)))
    rad = 0.014
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, segments=32, ring_count=16, location=(0.0, 0.0, Z[i0, j0] + rad))
    sp = bpy.context.active_object
    sp.data.materials.append(material("state" + tag, (0.12, 0.12, 0.12), rough=0.4))
    bpy.ops.object.shade_smooth()
    return (cc[0] - a.bevel, cc[-1] + a.bevel, oo[0] - a.bevel, oo[-1] + a.bevel, float(Z.min() - a.skirt), float(Z.max() + 2 * rad))


def lights(target, scale=1.0, k=None, az=0.0):
    k = ARGS.light if k is None else k
    t = Vector(target)
    ca, sa = math.cos(math.radians(az)), math.sin(math.radians(az))
    for nm, off, energy, size in (("key", (-2.2, -2.6, 3.6), 520, 2.6), ("fill", (3.0, -1.0, 2.2), 160, 3.0),
                                  ("rim", (0.5, 3.2, 2.5), 140, 2.0)):
        ld = bpy.data.lights.new(nm, "AREA")
        ld.energy = energy * scale ** 2 * k
        ld.size = size * scale
        ob = link(bpy.data.objects.new(nm, ld))
        ob.location = t + Vector((off[0] * ca - off[1] * sa, off[0] * sa + off[1] * ca, off[2])) * scale
        ob.rotation_euler = (t - ob.location).to_track_quat("-Z", "Y").to_euler()


def view_vectors(azim, elev):
    az, el = math.radians(azim), math.radians(elev)
    d = np.array([-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), math.sin(el)])   # target -> camera
    right = np.array([-math.sin(az), math.cos(az), 0.0])
    up = np.array([math.sin(el) * math.cos(az), math.sin(el) * math.sin(az), math.cos(el)])
    return d, right, up


def ortho_camera(target, azim, elev, ortho_scale):
    d, _, _ = view_vectors(azim, elev)
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ortho_scale
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_start, cd.clip_end = 0.1, 200.0
    cam = link(bpy.data.objects.new("cam", cd))
    cam.location = Vector(target) + Vector(d.tolist()) * 40.0
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam


def box_corners(box):
    return np.array([(x, y, z) for x in box[:2] for y in box[2:4] for z in box[4:]], float)


def screen_extent(box, azim, elev):
    _, right, up = view_vectors(azim, elev)
    P = box_corners(box)
    r, u = P @ right, P @ up
    return r.min(), r.max(), u.min(), u.max()


# ------------------------------------------------------------------ panels
def panel_floor(a, D, y_span, x0, w, h, ppm):
    """Floor scene cropped to x0..crop_x1 and y_span metres about the door axis; orthographic camera
    at the common elevation/azimuth with `ppm` pixels per metre (same for every floor panel)."""
    box = (x0, a.crop_x1, 5.0 - y_span / 2 - 0.03, 5.0 + y_span / 2 + 0.03)
    build_floor_scene(a, D, box)
    tx, ty = (x0 + a.crop_x1) / 2, 5.0
    ortho_camera((tx, ty, 0.0), a.azim, a.elev, w / ppm)
    lights((tx, ty, 0.0), scale=1.4, az=a.azim)


def panel_surface(a, P, tag, w, h):
    box = build_surface(a, P, tag)
    r0, r1, u0, u1 = screen_extent(box, a.land_azim, a.land_elev)
    m = a.land_margin
    scale = max((r1 - r0) / (1 - 2 * m), (u1 - u0) / (1 - 2 * m) * w / h)
    _, right, up = view_vectors(a.land_azim, a.land_elev)
    ctr = np.array([(box[0] + box[1]) / 2, (box[2] + box[3]) / 2, (box[4] + box[5]) / 2])
    # shift the target so the projected extent is centred
    off = right * ((r0 + r1) / 2 - ctr @ right) + up * ((u0 + u1) / 2 - ctr @ up)
    ortho_camera(tuple(ctr + off), a.land_azim, a.land_elev, scale)
    lights(tuple(ctr), scale=0.6, az=a.land_azim - 90.0)


# ------------------------------------------------------------------ compositing
def render_panel(a, builder, w, h):
    reset()
    dev = setup_render(a, w, h)
    builder(a, w, h)
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
    px = px[:, :, :3] * al + np.array(BG, np.float32) * (1 - al)   # straight alpha over BG
    bpy.data.images.remove(img)
    return px, dt, dev


def main():
    global ARGS
    a = ARGS = parse()
    W = a.width_px
    L = dict(np.load(DATA / "lone_trap.npz"))
    P = dict(np.load(DATA / "pair_landscape.npz"))
    g = max(2, W // 150)                                   # gutter
    ppm = W / a.floor_span_m                               # pixels per metre, both floor scenes
    el = math.radians(a.elev)
    hf = int(round((a.crop_x1 - a.crop_x0) * math.sin(el) * ppm))       # top row: crop projected at the elevation
    hb = int(round((a.crop_x1 - a.pair_x0) * math.sin(el) * ppm))       # bottom row (same elevation, same scale)
    H = hf + hb + g
    wp = int(round(a.pair_span_m * ppm))
    wl = W - wp - g
    hl = (hb - g) // 2
    canvas = np.ones((H, W, 3), np.float32) * np.array(BG, np.float32)   # sRGB, bottom row first
    panels = {"top": ((0, 0, W, hf), lambda a_, w, h: panel_floor(a_, L, a.floor_span_m, a.crop_x0, w, h, ppm)),
              "pair": ((0, hf + g, wp, hb), lambda a_, w, h: panel_floor(a_, P, a.pair_span_m, a.pair_x0, w, h, ppm)),
              "b0": ((wp + g, hf + g, wl, hl), lambda a_, w, h: panel_surface(a_, P, "b0", w, h)),
              "bfold": ((wp + g, hf + g + hl + g, wl, hb - hl - g), lambda a_, w, h: panel_surface(a_, P, "bfold", w, h))}
    times = []
    dev = None
    for key in a.panels.split(","):
        (x, y, w, h), fn = panels[key]
        px, dt, dev = render_panel(a, lambda a_, w_, h_, fn=fn: fn(a_, w_, h_), w, h)
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
    meta = {"px": [W, H], "cm": [a.width_cm, round(a.width_cm * H / W, 2)], "samples": a.samples, "device": dev,
            "threads": a.threads, "px_per_m_floor": round(ppm, 1), "panel_render_s": times, "total_render_s": round(sum(times), 1)}
    print("HERO", json.dumps(meta))
    Path(a.out).with_suffix(".json").write_text(json.dumps({**meta, "args": {k: v for k, v in vars(a).items()}}, indent=1))


main()
