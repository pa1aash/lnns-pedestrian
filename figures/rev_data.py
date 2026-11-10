"""Readers for the revision analyses (data/derived/rev_*.json). Each returns None while the file is absent, so the
figures build before and after the revision data land."""
import json
from pathlib import Path

DERIVED = Path(__file__).resolve().parent.parent / "data" / "derived"


def _load(*names):
    for n in names:
        p = DERIVED / n
        if p.exists():
            return json.load(open(p))
    return None


def rev_arrhenius():
    """High-beta escape points and the slope-ratio trend (session C, A4 and B3). Not yet available."""
    return None


def rev_width():
    """Width grid 0.82-0.96 m, logistic fit with band, parameter-free prediction(s) (session C, B2). Not yet available.
    Shape: {"points": [{"w", "p", "lo", "hi"}], "logistic": {"w", "mid", "lo", "hi"}, "predictions": {name: {"w", "p"}}}."""
    return None
