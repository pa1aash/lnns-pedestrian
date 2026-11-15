# 6f — Lone release 1 m upstream for B1's 200 positive-margin agents

B1 (rev_B1.json) released the 200 positive-margin agents only at their rest state x_rest
(0/200 pass); its 1 m upstream release was done for the negative-margin set only (200/200).
The speed, kinetic energy and wall potential energy at x_peak for a 1 m upstream release
of the positive-margin agents were therefore not recorded; this item computes them.
Scripts: experiments/revision4/T6f_release.py (serial, energy ledger), T6f_analyze.py
→ data/derived/rev4_T6f.json; raw data/revision4/T6f/t6f.jsonl.

- Released from rest 1 m upstream of x_peak (x0 = 8.829 m): 127/200 pass, 95% Wilson [0.57, 0.70].
- Margins 0.008–454 N. Largest margin that passes: 125 N. Smallest margin held: 42.5 N.
  All 10 smallest margins (0.008–3.07 N) pass.
- 10 smallest margins: speed at x_peak 0.45–0.77 m/s, KE at x_peak 8.2–23.5 J;
  wall potential energy gained between release and x_peak 23–44 J.
- Energy ledger for the smallest margin (0.008 N), release → farthest point:
  drive work 222 J, drag dissipation 153 J, wall work −60 J, KE 9.0 J left.
- Rule "pass iff KE at x_rest > adverse work A beyond x_rest": agrees on 153/200;
  no agent passes against the rule; 47 are held although KE at x_rest > A
  (drag inside the adverse region, which A ignores, removes the excess).
- Existing number unaffected: "none of 200 leaves" refers to release at the rest state.
