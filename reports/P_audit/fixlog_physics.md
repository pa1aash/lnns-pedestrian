# Fix log: paper/sections/05_deadlock_physics.tex (wave 2 audit)

Applied: numbers.md 24 (PphysWeidMin 0.9965), 25 (PphysBstarMin 0.00051), 33, 35, 37-44 (Pphys* two-figure or upper-bound formats), 50, 51 (PphysRatioFull 1.2), 112 (Fig. 4 "2000 of 20000");
prose.md 12-1 (drive part 215 N vs rest drive 430 N, text and Fig. 4 caption), 13-1/11-7/12-8 (32 = accepted barrier and an agent besides the blocker), 9-2, 5-1, 5-3, 2-1, 4-4, 9-10, 4-6, 4-13, 8-6, 12-5 (quench), 12-6, 12-7, 12-9, 12-10, 12-11, 13-5 (line 22), 13-6, 15-6, 16-8, 16-9;
compliance.md V3 (05:52 -> Sect.~\ref{sec:att-pair}), D6 ("covers 1 for 7 of 8"); P_RESOLUTION disputes 2, 9, 10, 11, 12, B4 (radius line styles, tau of the blue lines).
Macros added: paper/registry/p_physics.yaml (Pphys*), numbers.tex rebuilt.

Declined:
- prose 13-3 / StuckAloneN "20\,000": make_numbers.py has no thousands-thin-space format; needs a tool change by the integrator (registry not mine).
- numbers 77 (drives at 2 sf): a format string cannot round 214/215 to 210; the two values now name different quantities, so the 0.2 N split no longer reads as a contradiction.
- numbers 78, 80 (g_max 291/543, mu_1 121 at 2 sf): same format limit; force-law values and eigenvalue ranges, not statistics. 291 N dropped from the text for length.
- numbers 55 (w50 3 sf): kept, the interval needs three figures (audit's own option).
- numbers 107 (sigma 0.02-0.05, 230/230): adds words; Fig. 8 reference moved to Sect. 6.4.
- prose 5-4 "forms in most runs with B_w=0.04 m": false (46 of 320 runs); written "forms mainly with B_w=0.04 m" instead.
- prose 4-5 (turnover factor "accounts for this"): stronger claim than the data support; kept "consistent with".
- prose 7-3, 7-4 (subsection titles): taste; headings and labels shared with other sections.
- prose 14-3 (move Related Work sentence to 05:2): source file not mine; Sect. 5.4 already states the missing static friction.
- prose 15-5 (cm vs mm overlaps): arch overlaps stay in cm (B4 macros are in cm); the mm overhang is a different scale.
- compliance B1 ("attempt rate"): standard Kramers name of the prefactor of lambda; kept.
