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
C10 (2026-11-07) Repository licence: MIT (code and original content), copyright 2026 Palaash Gang and Arjun Veluri; text fetched from the GitHub licence API. Third-party data keep their own licences.

## 2026-11-08

C11 Live change log: from v1.1 on, lnns-pedestrian/plan/CHANGELOG.md is the live plan change log; the plan root (pedestrian-abs-plan) is a frozen archive and is not edited further.

C12 Deadlock typing: residual geometry is classified by snapshot surgery (keystone test: is the blocker held when alone; do the others exit once the blocker is removed), replacing the contact-cluster grouping, whose counts are not used in the text. The quench stopping rule (|v| < 1e-3 m/s for 10 s, deterministic arms only) and the 120 s window are those of the pilot quench script (wave2/scripts/w22_quench.py), resolving Table 1 note P7.

C13 End-of-queue rule: reported against the all-exit baseline (93.2% E1a, 93.1% E1b of stuck-alone agents exit), with its errors split between final blockers and agents queued behind a blocker; the rank AUC is the headline number. T2 is stated for the terminal rest state, where the local density gives v_eff/v0 ≥ 0.99 (pending sign-off).

C14 Table 2: the last column is "Corrected numerics" (open geometry is not a probe of a frozen bottleneck state and belongs to the Table 4 claims); P, L, T and D read "persists" there; D under both Δt probes reads "no Δt dependence" (a static tilt is deterministic).
