"""Select pair-deadlock snapshots (exactly 2 residual agents) for A3/A4/A5, at most 30:
W2.5 B0.04 (seeds 42-66) first, then A1 in seed order. Writes wave2b/data/a4_selected_snaps.txt
and lists non-pair deadlocks (for the report)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2blib import *  # noqa
rows = [r for r in load_jsonl(os.path.join(PLAN, "wave2/data/w25_validity.jsonl")) if r["job_id"].startswith("B0.04|")]
rows += load_jsonl(os.path.join(DATA2B, "a1_library.jsonl"))
rows.sort(key=lambda r: r["seed"])
sel, other = [], []
for r in rows:
    if r.get("deadlock"):
        path = os.path.join(PLAN, "wave2", r["snapshot"]) if r["job_id"].startswith("B0.04|") and "w25" in r.get("snapshot", "") else os.path.join(PLAN, "wave2b", r["snapshot"])
        if not os.path.exists(path):
            path = os.path.join(PLAN, r["snapshot"]) if os.path.exists(os.path.join(PLAN, r["snapshot"])) else path
        (sel if r["n_remaining"] == 2 else other).append((r["seed"], r["n_remaining"], path))
print("pairs", len(sel), "other deadlocks", [(s, n) for s, n, _ in other], "seeds used", len(rows))
for s, n, p in sel:
    assert os.path.exists(p), p
open(os.path.join(DATA2B, "a4_selected_snaps.txt"), "w").write("\n".join(p for _, _, p in sel[:30]) + "\n")
