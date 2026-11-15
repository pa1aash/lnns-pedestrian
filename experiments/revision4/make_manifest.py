"""Run manifest for revision4: sha256 of every file under data/revision4 (except logs) and of the rev4_*.json
derived outputs, with record counts and summed per-job wall seconds (wall_s / wall fields where recorded), the
worker count, the code version (process CPU where the records carry cpu_s), and the regression hash. Output: data/revision4/MANIFEST.json."""
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev4lib  # noqa: E402

ROOT = rev4lib.ROOT


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


files = sorted(p for p in glob.glob(os.path.join(ROOT, "data", "revision4", "**", "*"), recursive=True)
               if os.path.isfile(p) and "/logs/" not in p and not p.endswith("MANIFEST.json"))
files += sorted(glob.glob(os.path.join(ROOT, "data", "derived", "rev4_*.json")))
ent = []
for p in files:
    e = {"path": os.path.relpath(p, ROOT), "sha256": sha(p), "bytes": os.path.getsize(p)}
    if p.endswith(".jsonl"):
        n, w, c, nc = 0, 0.0, 0.0, 0
        for l in open(p):
            r = json.loads(l)
            n += 1
            w += float(r.get("wall_s", r.get("wall", 0.0)) or 0.0)
            if "cpu_s" in r:
                c += float(r["cpu_s"])
                nc += 1
        e.update({"records": n, "sum_job_wall_s": w, "job_wall_h": w / 3600})
        if nc == n:
            e["process_cpu_h"] = c / 3600
    ent.append(e)
head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
out = {"doc": __doc__, "git_head_at_manifest": head, "workers": rev4lib.WORKERS, "cpu_count": os.cpu_count(),
       "regression_hash": "e381b49dc24acccd (checked OK before and after the sfm_tau_prime flag)",
       "note": "Wall times inflated by other processes on the machine (load average up to ~236). 8 cores; 6 workers "
               "(all but two) for T1, T3, T4, T5; T6f and the string work ran serially.",
       "not_committed": "data/revision4/T4/raw/*.npz (trajectories, 266 MB; hashes listed here, kept on disk)",
       "files": ent}
json.dump(out, open(os.path.join(ROOT, "data", "revision4", "MANIFEST.json"), "w"), indent=1)
print(len(ent), "files")
