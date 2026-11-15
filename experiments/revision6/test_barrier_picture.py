"""Regression: experiments/E6/analyze.barrier_picture with the barrier list as an argument reproduces the published
stall prediction (data/derived/E6_analysis.json lifetimes.barrier_picture and pred_vs_obs) exactly, with the list
passed explicitly and with the default (None = reported barriers).

Run: .venv/bin/python -m pytest -q experiments/revision6/test_barrier_picture.py
  or .venv/bin/python experiments/revision6/test_barrier_picture.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from P4_span import load_e6, span_barriers  # noqa: E402

E6 = json.load(open(os.path.join(ROOT, "data", "derived", "E6_analysis.json")))["lifetimes"]
PUB = E6["barrier_picture"]


def _check(bp):
    assert bp == json.loads(json.dumps(PUB)) or bp == PUB, "barrier_picture differs from E6_analysis.json"
    obs = dict(zip(map(str, E6["pred_vs_obs"]["t"]), E6["pred_vs_obs"]["S_obs_km"]))
    assert max(abs(bp["pred_S_at"][t] - obs[t]) for t in obs) == E6["pred_vs_obs"]["max_abs_diff"]


def test_reported_list_reproduces_published():
    e6 = load_e6()
    bl = e6.reported_barriers()
    assert len(bl) == 56 and len({s for s, _ in bl}) == 56
    _check(e6.barrier_picture(PUB["sigma"], PUB["nu_full_median"], bl))


def test_default_is_reported_list():
    e6 = load_e6()
    _check(e6.barrier_picture(PUB["sigma"], PUB["nu_full_median"]))


def test_span_list_changes_eight():
    bl, changed = span_barriers()
    assert len(bl) == 56 and len(changed) == 8
    assert all(c["dU_span"] > c["dU_rep"] for c in changed)


if __name__ == "__main__":
    test_reported_list_reproduces_published()
    test_default_is_reported_list()
    test_span_list_changes_eight()
    print("3 passed")
