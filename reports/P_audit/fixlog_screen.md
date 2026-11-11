# Fix log: Sect. 6 (06_screening.tex), Tables 3a/3b (make_table3.py), p_screen.yaml

Applied: compliance 06:19/29/48 and Table 3a notes (bare ORCA); V3 (Fig. 8 cited at 06:42); prose 1-1..1-3 (tic stated once,
at the lone keystones), 3-4, 4-3 (tail cut; Sect. 8 already carries the extrapolation sentence), 4-7, 4-8, 4-9, 8-1, 9-1, 9-3,
9-4, 9-7, 9-8, 11-5, 11-8 ("screening set"), 12-2, 12-4, 12-5, 13-4, 13-13, 16-1, 16-12; numbers.md 06:8 (26 of 160),
06:24 (median), 06:26/31/45 IMPRECISE (Pscr* 2-sf macros), Table 3a/3b IMPRECISE cells (Pscr* 2-sf macros), Table 3b pair
interval (now rev_A8 for both solvers: RVO2 [-0.15, 0.17], one source with the A7/A8 tests), 06:51 literal replay claim
(sentence removed: the filter frees nothing, so replay agreement adds nothing); P_RESOLUTION disputes 6 (Sect. 6.2 now
quotes the Table 3a J with its hypergeometric p), 8, 25, 26 (Table 3 part).

Declined:
- 7-5 (split "Second Trap and the Legacy Solver" heading): taste; an extra run-in heading costs space against the page budget.
- 8-7 (move "none where every snapshot has the same outcome" to 04:51): needs the Sect. 4 writer; captions keep it until then.
- 11-2 (move repository, commits, file path to back matter): needs the back-matter writer; A14 asks for them in Sect. 6.1.
- 12-3 "Reshape, axial, at the pair": the pair rest field has an axial drive part and a lateral constraint part; the subtype is not established, so "Reshape at the pair" stays.
- 15-7 ("none" for zero-valued macros): every number stays a macro.
- numbers.md 06:45 RevAelevenRatioMin 0.19: rated minor; 0.186 would mix precision within the range.
- numbers.md EthreeEllBA 2.16 (2.22) in Table 3a: the macro is shared with Table 2; change it in the registry owner's file so both tables agree.
- numbers.md Holm p 0.12 (half-even): pfmt fix is in tools/make_numbers.py (not mine; already changed in the working tree).
- P_RESOLUTION dispute 17 (100 vs 186 velocity-filter seeds): the relation is not in my sources; left for the integrator.
