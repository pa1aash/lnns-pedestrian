# Overlap with the conference paper (integration re-audit, 2026-11-10)

Tool: `python3 tools/overlap_check.py` (ref/camera_ready_SIMULTECH2026.pdf against paper/sections/*.tex, after commit 0b65cbe).

- Default threshold (8 words, fail at 10): **0 shared runs; longest 0**. Exit status 0.
- Diagnostic at 6 words: 1 shared run, "at a 0.8 m exit" (6 normalised tokens: a geometry statement, not prose).

Verdict: no textual overlap to fix.
