"""Run manifest for revision5: sha256 of every file under data/revision5 (except logs; trajectories included, whether
committed or not) and of the rev5_*.json derived outputs, with record counts, summed per-job wall seconds and process
CPU (cpu_s) where recorded; also the sha256 of the C3 trajectories (data/revision4/T4/raw/, kept in the C3 worktree)
that X2_analyze.py reads for seeds 42-51. Output: data/revision5/MANIFEST.json."""
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev5lib  # noqa: E402
import X2_analyze  # noqa: E402

ROOT = rev5lib.ROOT
LIMIT = 20 * 1024 * 1024


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def entry(p, base):
    e = {"path": os.path.relpath(p, base), "sha256": sha(p), "bytes": os.path.getsize(p)}
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
        if nc:
            e["process_cpu_h"] = c / 3600
            e["records_with_cpu"] = nc
    return e


files = sorted(p for p in glob.glob(os.path.join(ROOT, "data", "revision5", "**", "*"), recursive=True)
               if os.path.isfile(p) and "/logs/" not in p and not p.endswith("MANIFEST.json"))
files += sorted(glob.glob(os.path.join(ROOT, "data", "derived", "rev5_*.json")))
ent = [entry(p, ROOT) for p in files]
for e in ent:
    e["committed"] = e["bytes"] <= LIMIT and "/raw/" not in e["path"] and "/rean/" not in e["path"]
r4 = X2_analyze.raw4()
c3 = [{"path": os.path.relpath(p, os.path.dirname(ROOT)), "sha256": sha(p), "bytes": os.path.getsize(p)}
      for p in sorted(glob.glob(os.path.join(r4, "*.npz")))]
head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
out = {"doc": __doc__, "git_head_at_manifest": head, "workers": "3 + 3 (X1 and X2 concurrently; 6 of 8 cores)",
       "cpu_count": os.cpu_count(),
       "note": "Wall times inflated by other processes on the machine (load average up to ~56 from unrelated jobs).",
       "not_committed": "data/revision5/X2/raw/*.npz (trajectories) and data/revision5/X1/rean/ (scratch re-runs of "
                        "the E3/E4 analyses); hashes listed here, kept on disk",
       "files": ent, "c3_trajectories_read": c3,
       "totals": {"X1_process_cpu_h": sum(e.get("process_cpu_h", 0) for e in ent if "/X1/" in e["path"]),
                  "X2_process_cpu_h": sum(e.get("process_cpu_h", 0) for e in ent if "/X2/" in e["path"])}}
json.dump(out, open(os.path.join(ROOT, "data", "revision5", "MANIFEST.json"), "w"), indent=1)
print(len(ent), "files;", out["totals"])
