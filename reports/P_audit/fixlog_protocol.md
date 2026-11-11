# Fix log: paper/sections/04_protocol.tex, paper/tables/table2_signatures.tex

Applied: compliance V1 (Table 2 overfull: tabcolsep 1pt, split row labels, "exp.\ times"; the noise-row
scope moved to note b to fit; checked in a scratch build, no overfull box); compliance "(ORCA)" -> "(force-coupled ORCA)";
compliance/numbers "matched at 120 s" -> "matched^b", note b: fraction-matched at T = 120 s at lone keystones, not second traps;
numbers 04:13 (14 s scoped: "last lone-trap exit ... by \RevAeightSTRvoLatest s"); numbers 04:32, 04:41, T2:25 (2 sf via
p_protocol.yaml: \PprotMuMax, \PprotVarRatio, \PprotEllBA); prose 3-3/12-4 (snapshot), 5-5, 7-1, 7-2, 8-5, 11-6/12-8,
12-2, 12-3 (note a), 12-13 (RMST), 12-16 (beta), 13-10 (|l| note), 13-11, 13-12, 16-14, H-1, 12-1/item 1 (rest-drive push
= the ORCA term's drive part at rest m v0/tau_orca; 4.3 states it is added to the rest drive); RESOLUTION dispute 5
(the match rule; brief's "dispute 4") and dispute 16 (split-sample sentence deleted: no result anywhere in the sections).

Declined:
- prose 9-11 (noise-horizon rewrite): taste, and it adds words to Sect. 4.
- prose 12-17 at 04:28: "SFM" there is the configuration, contrasted with SFM+TTC in the same sentence.
- prose 14-3: moving Related Work sentences into Sect. 4 edits 02 (not my file) and lengthens Sect. 4.
- prose 16-11: 04:41 continues the sentence opened before Eq. (teff); it does not open a sentence.
- prose 12-5 at 04:48: an escape run has its own exit rule, set against "in a quench" in the same sentence; renaming it a quench conflates them.
- prose 8-7: the bootstrap-omission sentence needs the 06 captions changed by their owner, and adds words.
- prose term table "unresolved" -> "held": the replay sentence of Sect. 4.6 defines when a snapshot counts as unresolved.
- prose 15-4 (\kB macro): needs a main.tex definition outside my files; rendering is identical.
- prose 16-13 "vanish (RVO2)": the column header already reads "Corrected (RVO2)", and the column has no width to spare.
- RESOLUTION dispute 18 (Heat row "exponential times"): the predicted block states the class prediction; the deviation is reported in Sect. 5.2.
- numbers 04:13 "161 s": kept as an integer bound, as the audit allows.
- RESOLUTION D7 (results in Sect. 4.2-4.5): the horizons, Hessian and acceptance counts define the protocol's inputs; moving them lengthens Sect. 5-6.
