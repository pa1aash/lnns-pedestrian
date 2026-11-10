"""B5 generation: the E7b pair-library runs (same 320 seeds) with rounded jamb ends, r_c = 0.1 m, CF union
{B_w: 0.04}; definitions, counts and output layout in B6_gen.py (cell "rounded").
Output: data/revision/B5/gen_rounded.jsonl, snapshots data/revision/B5/library/. Usage: B5_gen.py [qargs options]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import B6_gen  # noqa: E402

if __name__ == "__main__":
    print("wall", B6_gen.main("rounded"))
