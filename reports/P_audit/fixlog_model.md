# Fix log: Sect. 3 (03_pedestrian_model.tex), Table 1 (make_table1.py), registry p_model.yaml

Applied: compliance V1#2 (overfull 03:18, break after comma); numbers 03:40 WRONG (new \PmodRunsWMinFloor = 0.9576, truncated, replaces \RevAtwoRunsWMin 0.958); prose 3-2 + 12-17 + 15-3 ("This social force model", "this social force model with relaxation time"); 14-3 (Related Work line-3 sentence merged into 03:4); 4-12/14-4 (native ORCA sentence deleted; 08_discussion keeps the limitation); 12-1 + glossary row (rest drive defined at 03:47 as the total goal-directed force at v = 0; force-coupled ORCA's is RevAoneDriveRatio times SFM's); 16-4 (per-step / sqrt(dt)-scaled noise named); 12-6 + 16-10 ("rounds each segment end"); 9-9 + D2 (CroMa sentence split and clarified); 11-9 (snapshot library defined); terminology row "Horizon" (tau_h = ORCA look-ahead time, text and Table 1); 12-16 (sigmoid renamed \varsigma; Table 1 caption N(mean, SD)); terminology rows "Wall-force variant" and "Rounded door-edge geometry" (Table 1: "wall strength; wall range", "segment-end radius"); RESOLUTION 21 in part (k_ttc no longer sourced to Karamouzas: source cell reads "[karamouzas2014] (tau_0)").

Declined:
- numbers 03:40 RevAtwoLoneWMin IMPRECISE: 0.9994 is already a valid floor of 0.99941 at four digits; restating as 1 - w would add words.
- RESOLUTION 21 (tau_orca, gate constants, 2v0 cap, capture radius not in Table 1): stated in Sect. 3 text by the C2 ruling; extra rows cost page budget.
- RESOLUTION 22 / F-14 (gamma, rho_max unchecked against Weidmann): needs the original source check (B_REPORT action), not a text edit.
- compliance B3 (generator paths in Table 1 comment): advisory; comments do not render and belong to the submission build's comment stripping.
- D7 (gate values as a result in Sect. 3.2): the gate bound justifies w_o = 1 in Eq. (identity); kept by the task instruction.
- prose 15-6 at 03:50: no w_50 interval occurs in this file.
- "20000" -> "20\,000": not present in this file.
