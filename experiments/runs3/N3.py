"""run-N3: E4 escape in the full condition at equal temperature across agents.

Snapshots, barriers, levels, censoring and escape rule as E4 (experiments/E4/e4_escape.py): the E4
snapshots whose full-condition barrier passed the validity check (experiments/BAR/gate.py) and is at
least 0.1 J (9), beta_ref = dU_full / k_B T_eff in {1.5, 2.5, 3.5}, 20 restarts per level, censored at
300 s (900 s at 3.5), C1, CF, dt 0.01 s.
Change from E4: every residual agent gets the temperature k_B T_eff = dU_full / beta_ref, not only the
blocker. The blocker's sigma is E4's (teff.sigma_for with the blocker's tau); the others' sigma follows
from the simulator flag w2_noise_equal_T = tau_blocker, w2_noise_m_ref = blocker mass (default off; code/
sim/core/simulation.py): sigma_i = sigma sqrt(m_ref g(tau_i) / (m_i g(tau_ref))), g(tau) = 1 - (1 - dt/tau)^2.
Noise seeds 31000 + 1000 k + 100 level + rep (k = E4 snapshot index), disjoint from E4's 11000 + ....
Output: data/N3/n3.jsonl (job_id "<tag>|full_eqT|b<level>|<rep>"), resumable.
"""
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3 import out_dir, qargs, run_jobs  # noqa: E402
import e4_escape  # noqa: E402
from runlib import escape  # noqa: E402

OUT = os.path.join(out_dir("N3"), "n3.jsonl")
N_REP = 20


def jobs():
    S = e4_escape.snapshots()
    J = []
    for j in e4_escape.make_jobs({"full": N_REP, "frozen": 0, "alone": 0}, S):
        tag, _, lv, rep = j["job_id"].split("|")
        k = [s["tag"] for s in S].index(tag)
        level = e4_escape.BETAS.index(j["beta_ref"])
        st = pickle.load(open(j["snap"], "rb"))["state"]
        m_b = float(st.masses[j["blocker"]])
        J.append(dict(j, job_id=f"{tag}|full_eqT|{lv}|{rep}", cond="full", cond_label="full_eqT",
                      flags={**j["flags"], "w2_noise_equal_T": j["tau_b"], "w2_noise_m_ref": m_b},
                      noise_seed=31000 + 1000 * k + 100 * level + int(rep)))
    return J


def main(argv=None):
    a = qargs.parse(argv)
    return run_jobs(qargs.select(jobs(), a), escape, a.out or OUT, workers=a.workers, log_every=20)


if __name__ == "__main__":
    print("wall", main())
