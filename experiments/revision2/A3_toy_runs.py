"""A3 toy runs: the lone blocker of the three B3 snapshots in the string-method potential (A3_toylib.Toy), with
the code's update, at the six levels beta = 1.5, 2.5, 3.5, 5, 6, 7 (kT = dU_alone / beta), to separate the
causes of the slope ratio below 1 found by B3.

Variants per (snapshot, beta):
  code     dt = 0.01 s, speed cap 2 v0 (the production update)               all six levels
  nocap    dt = 0.01 s, no speed cap                                         beta = 1.5, 2.5, 3.5
  nocap_h4 dt = 0.0025 s, no speed cap                                       beta = 1.5, 2.5, 3.5
N = 300 blockers per cell, started at the alone minimum at rest; horizon T = clip(0.7 / lambda_B3, 60, 6000) s
with lambda_B3 the measured rate of the cell (data/derived/rev_B3.json), escape x >= 10 m.
Seeds: 7300 + 100 * snapshot index + 10 * level index (+ 0 code, the same seed for nocap and nocap_h4, so code
and nocap share their noise until the cap first acts).
Output: data/revision2/A3/toy.json (resumable per cell: {key: {"t": escape times, nan = censored, "T": horizon,
"N", "wall_s"}}).
"""
import json
import math
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402
from rev2lib import DATA, DERIVED, np  # noqa: E402
import bar  # noqa: E402
import e4_escape  # noqa: E402
from A3_toylib import Toy  # noqa: E402

TAGS = ("E1b_seed72", "E1b_seed162", "E1b_seed192")
BETAS = (1.5, 2.5, 3.5, 5.0, 6.0, 7.0)
N = 300
OUT = os.path.join(rev2lib.data_dir("A3"), "toy.json")


def alone_min(tag):
    for line in open(os.path.join(DATA, "BAR", "barriers.jsonl")):
        r = json.loads(line)
        if r["job_id"] == tag:
            return r["alone"]["x_min"], r["alone"]["saddle"]
    raise KeyError(tag)


def setup(tag):
    S = {s["tag"]: s for s in e4_escape.snapshots()}
    s = S[tag]
    snap = pickle.load(open(s["snap"], "rb"))
    f = bar.Field(snap, [s["blocker"]], [], rho_mode="zero")
    return s, f


def main():
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    B3 = json.load(open(os.path.join(DERIVED, "rev_B3.json")))["snapshots"]
    for si, tag in enumerate(TAGS):
        s, f = setup(tag)
        toy = Toy(f)
        xm, _ = alone_min(tag)
        dU = s["dU"]["alone"]
        lam = {c["beta"]: c["lam"] for c in B3[tag]["cells"]}
        for li, beta in enumerate(BETAS):
            T = float(np.clip(0.7 / lam[beta], 60.0, 6000.0))
            seed = 7300 + 100 * si + 10 * li
            variants = [("code", 0.01, True)]
            if beta <= 3.5:
                variants += [("nocap", 0.01, False), ("nocap_h4", 0.0025, False)]
            for name, dt, cap in variants:
                key = f"{tag}|{beta:g}|{name}"
                if key in res:
                    continue
                w0 = time.perf_counter()
                te = toy.run(xm, dU / beta, dt, T, N, seed, clamp=cap)
                res[key] = {"t": [None if math.isnan(v) else float(v) for v in te], "T": T, "N": N, "dt": dt,
                            "cap": cap, "seed": seed, "kT": dU / beta, "wall_s": time.perf_counter() - w0}
                json.dump(res, open(OUT, "w"))
                print(key, "escaped", int(np.isfinite(te).sum()), "of", N, "T", T,
                      "wall %.0f s" % res[key]["wall_s"], flush=True)


if __name__ == "__main__":
    main()
