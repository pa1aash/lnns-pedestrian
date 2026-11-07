"""W2.8 CroMa 2021 bottleneck (DOI 10.34735/ped.2021.9, CC BY 4.0) first look, plus the
same estimator on simulated C1+eps (sigma = 0.05) near-door trajectories from W2.4.

Per run: flow through the entrance line (x = 0 in CroMa; x = 10 in the model), passage
time gaps (count > 2 s, longest), and waiting-zone per-component velocity fluctuations.
Estimator (lit/OUT/FINAL_REPORT.md 1.8, 4.4): quadratic Savitzky-Golay velocity over a
1.48 s window (37 frames at 25 fps), minus the mean SG velocity of neighbours within
0.74 m (self excluded; samples without neighbours dropped), in the waiting zone
0.3-2.5 m before the entrance (|y - y_c| < 2 m), keeping samples whose local-mean speed
is < 0.3 m/s. Reported: per-component SD of the residuals (pooled samples).
Usage: python -I w28_croma.py <croma_txt_dir> <sim_npz> [<sim_npz> ...]
Output: wave2/data/w28_croma.json
"""
import glob, json, os, re, sys
import numpy as np
from scipy.signal import savgol_filter

WIN = 37
FPS = 25.0


def sg_vel(t_frames, xy):
    """SG first derivative per track; returns velocities (m/s) or None if too short."""
    if len(xy) < WIN:
        return None
    return np.column_stack([savgol_filter(xy[:, k], WIN, 2, deriv=1, delta=1.0 / FPS) for k in (0, 1)])


def tracks_from_rows(ids, frames, x, y):
    out = {}
    order = np.lexsort((frames, ids))
    ids, frames, x, y = ids[order], frames[order], x[order], y[order]
    cuts = np.where(np.diff(ids) != 0)[0] + 1
    for s, e in zip(np.r_[0, cuts], np.r_[cuts, len(ids)]):
        f = frames[s:e]
        # split at frame gaps
        gaps = np.where(np.diff(f) != 1)[0] + 1
        for a, b in zip(np.r_[0, gaps], np.r_[gaps, len(f)]):
            if b - a >= WIN:
                out[(int(ids[s]), int(f[a]))] = (f[a:b], np.column_stack([x[s:e][a:b], y[s:e][a:b]]))
    return out


def fluct(tracks, x_e, y_c, sign=+1):
    """sign=+1: walking direction +x and the waiting zone is x_e-2.5 < x < x_e-0.3."""
    rows = []
    for key, (f, xy) in tracks.items():
        v = sg_vel(f, xy)
        if v is None:
            continue
        rows.append(np.column_stack([f, np.full(len(f), key[0]), xy, v]))
    if not rows:
        return None
    D = np.vstack(rows)
    res = []
    for fr in np.unique(D[:, 0]):
        S = D[D[:, 0] == fr]
        P, V = S[:, 2:4], S[:, 4:6]
        dx = sign * (x_e - P[:, 0])
        zone = (dx > 0.3) & (dx < 2.5) & (np.abs(P[:, 1] - y_c) < 2.0)
        for i in np.where(zone)[0]:
            d = np.linalg.norm(P - P[i], axis=1)
            nb = (d < 0.74) & (d > 0)
            if not nb.any():
                continue
            vm = V[nb].mean(axis=0)
            if np.linalg.norm(np.vstack([V[nb], V[i]]).mean(axis=0)) >= 0.3:
                continue
            res.append(V[i] - vm)
    if not res:
        return None
    R = np.array(res)
    return {"n_samples": len(R), "sd_x": float(R[:, 0].std()), "sd_y": float(R[:, 1].std())}


def passages(tracks_raw, x_e, sign=+1):
    """First crossing time (s) of the entrance line per id."""
    times = []
    for i, (t, x) in tracks_raw.items():
        c = np.where(sign * (x - x_e) >= 0)[0]
        if len(c) and c[0] > 0:
            times.append(t[c[0]])
    times = np.sort(times)
    g = np.diff(times)
    return {"n_pass": len(times), "flow_per_s": float((len(times) - 1) / (times[-1] - times[0])) if len(times) > 1 else None,
            "n_gaps_gt_2s": int((g > 2.0).sum()), "max_gap_s": float(g.max()) if len(g) else None,
            "median_gap_s": float(np.median(g)) if len(g) else None}


def croma(path):
    d = np.loadtxt(path, comments="#", usecols=(0, 1, 2, 3))
    ids, fr, x, y = d[:, 0].astype(int), d[:, 1].astype(int), d[:, 2], d[:, 3]
    raw = {i: (fr[ids == i] / FPS, x[ids == i]) for i in np.unique(ids)}
    out = {"file": os.path.basename(path), "n_ids": int(len(raw)), "duration_s": float(fr.max() / FPS)}
    m = re.search(r"w(\d{3})_l(\d{3})_(h\w+)", path)
    out.update({"width_m": int(m.group(1)) / 100, "length_m": int(m.group(2)) / 100, "motivation": m.group(3)})
    out.update(passages(raw, 0.0))
    out["fluct"] = fluct(tracks_from_rows(ids, fr, x, y), 0.0, 0.0)
    return out


def sim(path):
    D = np.load(path)["data"]  # t, id, x, y at 25 Hz (every 4 steps of dt 0.01)
    fr = np.round(D[:, 0] * FPS).astype(int)
    ids = D[:, 1].astype(int)
    raw = {i: (D[ids == i, 0], D[ids == i, 2]) for i in np.unique(ids)}
    out = {"file": os.path.basename(path)}
    out.update(passages(raw, 10.0))
    out["fluct"] = fluct(tracks_from_rows(ids, fr, D[:, 2], D[:, 3]), 10.0, 5.0)
    return out


if __name__ == "__main__":
    cdir, sims = sys.argv[1], sys.argv[2:]
    files = sorted(f for f in glob.glob(os.path.join(cdir, "*.txt"))
                   if re.search(r"_w0(70|80)_|_w100_", f))
    res = {"croma": [croma(f) for f in files], "sim": [sim(s) for s in sims],
           "estimator": "SG quadratic, 37 frames (1.48 s) at 25 fps; minus mean of neighbours within 0.74 m "
                        "(self excluded); waiting zone 0.3-2.5 m before entrance, |y-yc|<2 m; local-mean speed < 0.3 m/s"}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "w28_croma.json")
    json.dump(res, open(out, "w"), indent=1, default=float)
    for r in res["croma"] + res["sim"]:
        print(r["file"], r.get("width_m"), r.get("motivation"), r["n_pass"], r["flow_per_s"], r["n_gaps_gt_2s"],
              r["max_gap_s"], r["fluct"])
