"""W2b A6 held-out comparison (pilot): matched lateral bias vs C3 on the pair library.
Jobs (same runner as A4, BASEF = numerics fixed + B_w 0.04):
  bias +0.02 (b* matched to C3_pub's pair rate 10/26; between b = 0.01 -> 3/26 and 0.03 -> 16/26),
  bias -0.02 and -0.03 (sign reversal: the analogue of frozen-mean reversal for a lateral resolver),
  1e-9 m isotropic perturbation x 3 seeds on the first 10 snapshots for C3_pub, C3_rvo2, bias0.02
  (seed-replay determinism). Output: appended to wave2b/data/a4_quench.jsonl (arm names below)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w2blib import *  # noqa
from a4_quench import BASEF, run

if __name__ == "__main__":
    snaps = [l.strip() for l in open(os.path.join(DATA2B, "a4_selected_snaps.txt")) if l.strip()]
    jobs = []
    for k, s in enumerate(snaps):
        tag = os.path.basename(s)[:-4]
        for b in (0.02, -0.02, -0.03):
            jobs.append({"job_id": f"{tag}|bias{b}", "snap": s, "arm": f"bias{b}", "config": "C1",
                         "flags": {**BASEF, "w2_noise": "lateral_bias", "w2_bias_b": b}, "deterministic": True})
        if k < 10:
            for arm, cfg, fl in (("C3_pub_perturb", "C3", {}), ("C3_rvo2_perturb", "C3", {"w2_orca": "rvo2"}),
                                 ("bias0.02_perturb", "C1", {"w2_noise": "lateral_bias", "w2_bias_b": 0.02})):
                for rep in range(3):
                    jobs.append({"job_id": f"{tag}|{arm}|{rep}", "snap": s, "arm": arm, "config": cfg,
                                 "flags": {**BASEF, **fl}, "perturb": 900 + rep, "rep": rep, "deterministic": True})
    print("wall", run_jobs(jobs, run, os.path.join(DATA2B, "a4_quench.jsonl"), workers=4, log_every=40))
