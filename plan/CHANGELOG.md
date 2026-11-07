# Plan changelog

## v1.1 — 2026-11-07

Approved changes C1-C9.

C1 Execution repository: public github.com/pa1aash/lnns-pedestrian, synced with ~/Developer/lnns-pedestrian, created now and pushed after every batch; everything public except copyrighted literature PDFs (lit/). The simulator is imported once (squashed) from pedestrian-abs branch exec-v1 in batch 2 and lives only there afterwards. pedestrian-abs and the plan root are never pushed. Supersedes D-open-5.

C2 Eight figures: a hero Fig 1 (Blender render of a real corrected-forward deadlock snapshot with the jamb wall-force field, alongside the pair-standoff energy landscape; raster 600 dpi, the only non-vector figure). Plan v1 Figs 1-7 become Figs 2-8. Outline about 23.6 pages.

C3 Captions at most two sentences: what the figure shows, then the colour and line key. Run details (n, seeds, flags, dt, window) go to the text and tables.

C4 Corner rule, flag w2_wall_corner = convex_union: for two segments sharing an endpoint P, if the agent's closest point on at least one of them is P, only the nearer of the two closest points contributes (nearest point on their union); otherwise both contribute. Removes the double count at convex shared ends (CroMa door edge) and keeps both walls at concave corners. Replaces "union nearest point at every shared end" (D-open-10).

C5 Drafting: the full paper text is drafted in execution sessions and rewritten by the authors; supersedes HANDOFF §0 ("the authors write the text"). The disclosure statement is handled by the authors at the writing stage.

C6 Framing: physics and STEM, not clinical-trial. No pre-registration or trial vocabulary in the paper or the workflow. Table 2 becomes "Mechanism classes and their physical signatures" (what each class predicts for each intervention). Statistics are reported as rates with confidence intervals, physical fits (Arrhenius, Weibull) and plainly stated agreement; equivalence margins are kept internally only where they set sample sizes.

C7 Reproducibility kept conventional: one Makefile from data to figures, tables and PDF; in-text numbers generated into numbers.tex. No evidence labels, manifests or per-number stamping.

C8 Compute on the Mac (4 workers) through one resumable job queue ordered by dependencies; RunPod only if needed later. Regression hash checked on the Mac.

C9 Deadline recorded: 18 Nov 2026 via PRIMORIS (from the invitation). Not used for planning.
