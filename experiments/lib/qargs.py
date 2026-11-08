"""Command-line options shared by the queue-2 step scripts (smoke tests use them; the queue passes none).

  --out PATH      write results here instead of the step's data/<E>/ file
  --limit N       run only the first N jobs (after --every)
  --every K       take every K-th job (spreads a smoke test over arms and seeds)
  --scale F       multiply every duration key (t_max, t_q, T) by F
  --workers W     worker processes (default 4; in-session smoke tests use 1)
"""
import argparse

T_KEYS = ("t_max", "t_q", "T")


def parse(argv=None):
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--out")
    p.add_argument("--limit", type=int)
    p.add_argument("--every", type=int, default=1)
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--workers", type=int, default=4)
    a, rest = p.parse_known_args(argv)
    a.rest = rest
    return a


def select(J, a):
    J = list(J)[:: max(1, a.every)]
    if a.limit:
        J = J[: a.limit]
    if a.scale != 1.0:
        J = [dict(j, **{k: j[k] * a.scale for k in T_KEYS if k in j}) for j in J]
    return J
