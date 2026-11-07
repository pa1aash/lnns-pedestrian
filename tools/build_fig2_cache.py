"""Cache the data for Fig 2 into figures/data/fig2.json.

Run with the plan root's interpreter (it imports the simulator via wave2/scripts/w2lib):
  /Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python tools/build_fig2_cache.py
The plan root is read-only; nothing is written there.
"""
import json
import sys
from pathlib import Path

PLAN = Path("/Users/palaash/Developer/pedestrian-abs-plan")
OUT = Path(__file__).resolve().parent.parent / "figures" / "data" / "fig2.json"
sys.path.insert(0, str(PLAN / "wave2" / "scripts"))
import w2lib  # noqa: E402  (chdir's into the simulator; OUT is absolute)

ana = json.load(open(PLAN / "exec/data/E1_analysis.json"))
E1a = ana["E1a"]
r, v0, tau = [], [], []
for line in open(PLAN / "exec/data/E1_runs.jsonl"):
    run = json.loads(line)
    if run["mode"] != "E1a":
        continue
    for a in run["attrs"]:
        r.append(a["r"]); v0.append(a["v0"]); tau.append(a["tau"])
assert len(r) == 20000, len(r)

profiles = {}
for rr in (0.20, 0.25, 0.30, 0.35):
    xs, fx = w2lib.wall_backward_profile(rr, width=0.8)
    # distance to the door plane (x = 10 m); backward force positive
    profiles[f"{rr:.2f}"] = {"d_m": [round(x, 4) for x in (xs - 10.0).tolist()], "F_back_N": [round(x, 3) for x in (-fx).tolist()]}

sb = ana["stuck_alone_boundary"]
out = {
    "source": "E1_analysis.json, E1_runs.jsonl (mode E1a), w2lib.wall_backward_profile at w=0.8 m",
    "m_kg": sb["m_kg"], "w_o_rest": sb["w_o_rest"], "tau_orca_s": sb["tau_orca_s"],
    "agents": {k: [round(x, 5) for x in v] for k, v in (("r_m", r), ("v0_ms", v0), ("tau_s", tau))},
    "gmax": ana["gmax_curve"],
    "boundary": {"r_m": sb["r_m"], "C1": sb["C1_v0_over_tau_star"],
                 "C3": sb["C3_v0_over_tau_star"]},
    "drive_C1_N": E1a["drives_N"]["C1_free_m_v0_over_tau"],
    "drive_C3_N": E1a["drives_N"]["C3_rest_total"],
    "profiles": profiles,
}
OUT.parent.mkdir(exist_ok=True)
json.dump(out, open(OUT, "w"))
print("wrote", OUT, OUT.stat().st_size, "bytes")
