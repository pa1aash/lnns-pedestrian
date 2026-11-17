"""Run manifest for revision 7 (session C5): sha256, size, record count and summed per-job wall seconds of every file
under data/revision7 (logs excluded) and of the rev7_*.json derived outputs; files over 20 MB are flagged
"not committed". Output: data/revision7/MANIFEST.json."""
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev7lib as L  # noqa: E402

LIMIT = 20 * 1024 * 1024


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def entry(p):
    e = {"path": os.path.relpath(p, L.ROOT), "sha256": sha(p), "bytes": os.path.getsize(p),
         "committed": os.path.getsize(p) <= LIMIT}
    if p.endswith(".jsonl"):
        n, w, err = 0, 0.0, 0
        for l in open(p):
            r = json.loads(l)
            n += 1
            err += "error" in r
            w += float(r.get("wall_s", 0.0) or 0.0)
        e.update({"records": n, "error_rows": err, "job_wall_h": w / 3600})
    return e


def main():
    files = sorted(p for p in glob.glob(os.path.join(L.DATA, "revision7", "**", "*"), recursive=True)
                   if os.path.isfile(p) and "/logs/" not in p and not p.endswith("MANIFEST.json"))
    files += sorted(glob.glob(os.path.join(L.DERIVED, "rev7_*.json")))
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=L.ROOT, capture_output=True, text=True).stdout.strip()
    out = {"script": "experiments/revision7/make_manifest7.py", "git_head_at_build": head, "files": [entry(p) for p in files]}
    json.dump(out, open(os.path.join(L.DATA, "revision7", "MANIFEST.json"), "w"), indent=1)
    big = [e["path"] for e in out["files"] if not e["committed"]]
    print(len(out["files"]), "files; over 20 MB:", big)


if __name__ == "__main__":
    main()
