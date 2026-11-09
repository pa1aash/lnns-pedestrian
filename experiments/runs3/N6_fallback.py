"""Run-N6 fallback for the (snapshot, sign) cases where pseudo-arclength continuation stopped before a fold.

Natural-parameter continuation of the pair minimum in b from 0 to 1.02 b* (bisection threshold), 204 steps,
Newton from the previous point; stops at the first b where Newton fails or the softest eigenvalue mu1 of -J
is not positive. Records the last converged b relative to b*, mu1 at b = 0 and at the last point, and the wall
geometry of the members there (gap to the closest wall point and the unclipped projection parameter t).

Usage: N6_fallback.py   (reads data/N6/n6_static.jsonl, writes data/N6/n6_fallback.jsonl)
"""
import json
import os
import pickle
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import N6  # noqa: E402

IN = os.path.join(ROOT, "data", "N6", "n6_static.jsonl")
OUT = os.path.join(ROOT, "data", "N6", "n6_fallback.jsonl")


def one(row):
    job = {(j["tag"], j["sign"]): j for j in N6.static_jobs()}[(row["tag"], row["sign"])]
    snap = pickle.load(open(job["snap"], "rb"))
    f = N6.Field(snap, job["sign"])
    X, _ = N6.newton_X(f, snap["state"].positions[f.k].ravel().copy(), 0.0)
    mu0, _ = N6.soft(f, X, 0.0)
    bs = row["b_star_bisection"]
    last, mu_last = 0.0, mu0
    for b in np.linspace(0.0, 1.02 * bs, 205)[1:]:
        Xn, ok = N6.newton_X(f, X, b)
        if not ok:
            break
        mu, _ = N6.soft(f, Xn, b)
        if mu <= 0:
            break
        X, last, mu_last = Xn, float(b), mu
    return {"job_id": row["job_id"], "tag": row["tag"], "sign": row["sign"], "b_star_bisection": bs,
            "b_last": last, "b_last_over_bstar": last / bs, "mu1_b0": mu0, "mu1_last": mu_last,
            "geom_last": N6.geometry(f, X)}


def main():
    rows = [json.loads(l) for l in open(IN)]
    fail = [r for r in rows if r["status"] != "ok"]
    with Pool(3) as p:
        out = p.map(one, fail)
    with open(OUT, "w") as fh:
        for o in out:
            fh.write(json.dumps(o) + "\n")
    print(len(out), "->", OUT)


if __name__ == "__main__":
    main()
