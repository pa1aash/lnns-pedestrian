"""Failure classes of the session C5 whole runs that did not complete: the E6 keystone test (keystone_e6.run, unchanged;
rebuild and tests K0, K1, K2, K1b exactly as experiments/revision4/T1_keystone.py) on the final state of every failed
run of T8 (drive_veff), T11 (R1, R2) and, when present, T7 replays.
Output: data/revision7/KS/keystone.jsonl (job_id "<variant>|seed<N>[|p<P>]|<test>"), resumable.
Usage: keystone_q.py [--workers W]"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402
import keystone_e6 as K  # noqa: E402

INS = [os.path.join(L.data_dir(t), f) for t, f in (("T8", "t8_whole.jsonl"), ("T11", "t11_whole.jsonl"))]
OUT = os.path.join(L.data_dir("KS"), "keystone.jsonl")


def failures():
    R = []
    for p in INS:
        if os.path.exists(p):
            R += [r for r in L.load_ok(p).values() if not r["complete"]]
    return R


def tag(r):
    return r["job_id"]


def phase1(R):
    return [{"job_id": f"{tag(r)}|{t}", "variant": r["variant"], "seed": r["seed"], "test": t, "run": r}
            for r in R for t in ("K0", "K1", "K2")]


def phase2(R, res):
    J = []
    for r in R:
        k1, k2 = res.get(tag(r) + "|K1"), res.get(tag(r) + "|K2")
        if k1 and k2 and k1["held"] and k2["held"]:
            pos = {int(x["id"]): K.np.array(x["pos"]) for x in r["residual"]}
            tgt = min(k2["held"], key=lambda i: float(K.np.linalg.norm(pos[i] - K.DOOR)))
            J.append({"job_id": tag(r) + "|K1b", "variant": r["variant"], "seed": r["seed"], "test": "K1b",
                      "target": int(tgt), "run": r})
    return J


def classify(R):
    res = {x["job_id"]: x for x in L.load_runs(OUT)} if os.path.exists(OUT) else {}
    out = {}
    for r in R:
        k1, k2 = res.get(tag(r) + "|K1"), res.get(tag(r) + "|K2")
        if not (k1 and k2):
            out[tag(r)] = None
        elif not k1["held"]:
            out[tag(r)] = "collective"
        else:
            out[tag(r)] = "lone_keystone_second_trap" if k2["held"] else "lone_keystone"
    return out


if __name__ == "__main__":
    w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 1
    R = failures()
    L.run_jobs(phase1(R), K.run, OUT, workers=w, log_every=50)
    res = {x["job_id"]: x for x in L.load_runs(OUT)}
    L.run_jobs(phase2(R, res), K.run, OUT, workers=w, log_every=50)
