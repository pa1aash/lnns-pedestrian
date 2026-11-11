# Fix log: front matter (00_abstract, 01_introduction, 02_related_work)

Applied: V1 (glossary overfull, wording as tested), V2 (Fig. 1 cited in Sect. 1 para 2 with the two deadlock types), V6/1-9/11-3 (01:13 "fraction-matched to force-coupled ORCA at horizon $T$"), 4-1, 4-2/10-1, 5-7, 11-4, 12-12, 12-14, 12-15, 12-16 ($T_{\rm b}$ at 02:9), 12-18, 13-5 (abstract pair standoff "dominates at a wall range of 0.04 m"), 13-12, 14-1, 14-2 (contributions carry no CroMa ratio and no w50), 14-3 (02 sentences removed), 1-5, 15-7, 16-2, 16-3, 16-5, 16-6, 16-7, 4-10, 5-8, 9-12, 10-3, 10-4, B1 (02:9 "attempt frequency"), comma-spliced contribution 1 (split), vocabulary "look-ahead time" for ORCA's horizon at 02:3; P_RESOLUTION disputes 1, 2, 3, 4, 13 (abstract scope), 14 (contribution 4), 19.
Scratch build (outside paper/): no overfull box in these files, 25 pages, abstract 249 rendered words without the "Abstract." label.

## Declined or modified (one line each)
- 1-8 / 1-9 "activated escape (noise)": written "fluctuations", because at the matched sigma = 0.07 m/s beta < 1 for most barriers (dispute 3); activated escape is claimed for the blocker-alone tests only.
- 12-3 "Reshape, axial or lateral" in the glossary: written "Reshape (axial or lateral)", since commas inside the comma-separated class list are ambiguous.
- 5-2 "wall range of 0.04 m" as a requirement: superseded by 13-5 (needs sharp segment ends, dominates at 0.04 m), which matches the 2-of-98 default-wall count.
- Vocabulary table "stuck alone" for the glossary lone-trap definition (01:19): declined; "stuck alone" is defined later by its margin, and the glossary defines the trap by its force.
- Vocabulary table "resolver" in the glossary (01:20): declined; "resolver" is defined in Sect. 4.2, and the V1 wording was the one tested for the overfull box.
- 15-4 `\kB` macro: declined here; it needs a definition in main.tex (not my file) and renders identically.
- 15-6 and numbers.md IMPRECISE row for 01:28 (w50 interval): moot; the contribution no longer quotes w50 (14-2).
- 12-17 "applies to SFM" at 02:9: moot; the sentence was removed under 14-3.
- Dispute 2, beta range 1.5-7 in the abstract: scoped as "with the blocker alone"; the beta range was left out to keep the abstract within 250 words.
- Dispute 20 ("brackets" is weak): partly declined; the claim is accurate, and the 0.041 m miss of the parameter-free prediction stays in Sect. 5.1 per ruling R2.
- 14-2 for the abstract: the CroMa ratio stays in the abstract (one of the four places); it is removed from the contributions.

## Cross-section dependencies
- 14-3: "This model has no static friction, so its deadlocks are rest states of a driven, damped system" was removed from 02:6; the Sect. 5 writer may add it at 05:2. The 02:3 and 02:9 sentences were already covered by 03:4, 04:34 and Sect. 4.4.
- B1: 02 now says "attempt frequency $\nu$"; 05:35, 05:43, 06:31 and 08:7 still say "attempt rate".
- Abstract and contribution 2 now state that replay and the time step separate by definition and time to free and final state empirically, matching 04:15.
- The ORCA look-ahead time is named so at 02:3; 03:36 and Table 1 still say "time horizon".
