# Session B3 report: references (2026-11-15)

Scope: the 46 works cited by the paper at origin/main df8ed37 (numbering as produced by BibTeX with splncs04, which sorts alphabetically), plus the citations the paper still lacks. Nothing in paper/ or paper/refs.bib was edited. Fetched records are in reports/B3_bib_additions.bib. Every comparison below was made against a record fetched on 2026-11-15 (Crossref REST API, DataCite REST API, doi.org content negotiation, Zenodo API, GitHub API, ETH Research Collection REST API, arXiv, Semantic Scholar, OpenAlex). Nothing was taken from memory.

Status per task

| Task | Status |
|---|---|
| 1 DOI re-resolution, 46 entries | Done. 46/46 DOIs resolve. No volume, issue, page or year mismatch. 3 entries differ from their records (RVO2, Weidmann, Wolinski); details below |
| 2 Registered dates, [1] CroMa and [3] RVO2 | Done. Keep 2026 and 2016 |
| 3 Claim check, [9] [13] [14] [33] [39] | Done. [33] and [39] supported; [9] and [13] partly supported (rewording proposed); [14] supported, with one nuance |
| 4 Missing methodological citations | Schuirmann, RMST (Royston and Parmar; Irwin optional) and stability-theorem books fetched. Holm NOT fetched (no DOI; JSTOR blocks scripted access): open action |
| 5 Parameter sources | Done, including Weidmann (now readable through the ETH REST API). Table 1: k_ttc = 1.5 comes from Karamouzas et al., not "this work" |
| 6 DOI case | Done (list of changes in Sect. 6) |

## 1. DOI re-resolution (task 1)

Method: each DOI in the 46 cited entries was fetched from api.crossref.org/works/<doi> (43 entries) or api.datacite.org/dois/<doi> (fzj_ped20219, vandenberg2011rvo2, weidmann1993). A script compared author family names in order (and given names when the family names agree), title, venue, year, volume, issue and pages after normalising accents and case.

Result: all 46 DOIs resolve to the work cited. Volume, issue, pages (or article number) and year agree for all 46.

Mismatches with the registered record (all fields that differ):

- [3] vandenberg2011rvo2 (DataCite, Zenodo 10.5281/zenodo.7039667). Record creators: "Snape, Jamie" and "Lithander" (personal name absent). Record title: "snape/RVO2: v2.0.2". Entry: authors van den Berg, Guy, Snape, Lin, Manocha; title "Optimal Reciprocal Collision Avoidance". The entry's authors and title come from CITATION.cff, which exists on the repository's main branch but not at tag v2.0.2 (raw file at v2.0.2 returns 404). The Zenodo metadata were generated automatically by the GitHub integration in 2022 (see task 2). Recommendation: keep the CITATION.cff authors and title (they are the authors' own citation request) and extend the note, e.g. note = {Authors and title as in the repository's CITATION.cff; the Zenodo record lists J. Snape and lithander as creators. Git commit c96a6ec; agent routines unchanged in version 2.0.3}. If a reviewer requires registry-exact metadata, the alternative is author = {Snape, Jamie and lithander}, title = {snape/RVO2: v2.0.2}. Author decision.
- [41] weidmann1993 (DataCite 10.3929/ethz-b-000242008, plus the ETH item record). (a) Title: the record and the scanned original both spell "Fussgänger" / "Fussgängerverkehrs" (Swiss orthography, no ß); the entry has "Fu{\ss}g{\"a}nger". Change to Fussg{\"a}nger and Fussg{\"a}ngerverkehrs. (b) Edition: the DOI belongs to the second edition ("Zweite, ergänzte Auflage", issued 1993-03, 114 p.). The first edition has its own DOI, 10.3929/ethz-a-000687810 (issued 1992-01). Add edition = {2nd}. Year 1993 is correct for this DOI. (c) Institution: DataCite publisher "ETH Zurich"; ETH item dc.publisher "Institut für Verkehrsplanung, Transporttechnik, Strassen- und Eisenbahnbau (IVT), ETH Zürich", place Zürich. The entry's "ETH Z{\"u}rich" is acceptable; the fuller form is optional. Type "IVT Schriftenreihe" and number 90 agree with the ETH record (ethz.journal.title, ethz.journal.volume).
- [43] wolinski2014parameter (Crossref 10.1111/cgf.12328). The Crossref record gives the second author as given "J.", family "Guy, S." (a deposit error). The entry's "Guy, S. J." is right; no change.

Non-printing differences (no action needed; splncs04 prints no publisher for @article): [6] boomers2023data, where Crossref gives the publisher as "Forschungszentrum Julich, Zentralbibliothek" without the umlaut. [14] gang2026: Crossref gives the publisher as "SCITEPRESS - Science and Technology Publications" (hyphen; entry has an en dash). Crossref also gives event location Porto, Portugal, 18-20 July 2026, and no ISBN or editors.

Year checks where online and print years differ (entry year is right in each case): [18] grover2023, online 2022-07-09, print 2023-05, vol. 42(6). [29] kim2015, online 2014-06-03, print 2015-05, vol. 31(5). [19] grover2020, online 2021-02-09, print 2021. [33] liu2026orcadeadlock, issue 2026-04, online 2026-06-11. [27] kaplanmeier1958, print 1958-06 (online 2012 is the digitisation).

Entries added or newly cited since B_REPORT.md. Five keys were never checked in B_REPORT: [7] chraibi2015, [13] fu2019, [29] kim2015, [39] qu2018 and [44] xu2021anticipation. Another 14 cited entries were checked in B_REPORT's Sect. 4 table but not in its Sect. 1: [4] [6] [8] [10] [15] [18] [24] [25] [26] [32] [34] [35] [38] [40]. One was renamed: [42] woillez2019. The commit history does not identify a set of exactly ten, so all 20 were fully re-compared. Each matches Crossref in authors (including given names), title, journal, year, volume, issue and pages or article number. The five new entries: chraibi2015 = PRE 92(4) 042809, 2015; fu2019 = J. Stat. Mech. 2019(12) 123402; kim2015 = Vis. Comput. 31(5) 541-555; qu2018 = Physica A 492, 1153-1167; xu2021anticipation = Transp. Res. C 133, 103464.

Housekeeping outside the 46 (uncited entries only, no effect on the PDF): refs.bib holds 213 entries, and 30 DOIs occur under two keys (e.g. helbing2000nature/helbing2000simulating, karamouzas2014/karamouzas2014universal, woillez2019/woillez2019activated, e2002/e2002string). The uncited key helbing1998social carries the 1995 DOI 10.1103/physreve.51.4282, and schreiber1999improved carries 10.1103/PhysRevLett.77.635. Recommend pruning uncited duplicates when refs.bib is next cleaned.

## 2. Registered dates (task 2)

[1] CroMa, DOI 10.34735/PED.2021.9 (DataCite, fetched):
- publicationYear 2026; record created and registered 2026-03-24T10:05:20/21Z; no dates[] entries; no version.
- The landing page (ped.fz-juelich.de/da/2021bottleneck) says the experiments were performed in Düsseldorf in October 2021. Its DokuWiki revision history starts on 2026-03-12 (first revisions by the archive staff) and was last edited 2026-09-23.
- No earlier public release of this collection was found (B_REPORT checked Semantic Scholar, Crossref and OpenAlex).

[3] RVO2 v2.0.2, DOI 10.5281/zenodo.7039667 (DataCite and Zenodo API, fetched):
- publicationYear 2016; dates: Issued 2016-05-11; version v2.0.2; Zenodo publication_date 2016-05-11.
- DOI registered 2022-09-01T01:28:52Z (Zenodo record created 2022-09-01). This is a retroactive archive of an old GitHub release; the concept DOI is 10.5281/zenodo.7039665.
- GitHub API: release v2.0.2 published 2016-05-11T02:09:17Z; tag created 2016-05-05; the tag points to commit c96a6ec8328492bae0721e59774026a119a60b4a, the commit named in the entry.

Rule used: cite the year in which the cited version was made public, which is the registry's PublicationYear (DataCite's mandatory property; its recommended citation form is Creator (PublicationYear): Title. Version. Publisher. Identifier). Do not use the DOI registration date when it postdates the public release.
- CroMa: 2026. The publication year and the registration year coincide, because the data were first published with the DOI. Optionally add "recorded October 2021" to the note, since readers may expect 2021 from the DOI suffix.
- RVO2: 2016. The release was public on 2016-05-11; the DOI registration in 2022 does not change the version's publication year.
- Both entries as they stand (2026, 2016) follow this rule.

## 3. Claim checks (task 3)

[9] Cornes, Frank, Dorso 2021, Physica A 568, 125744. The work exists as cited (Crossref). Read: full text of the preprint arXiv:2007.06746v1 (same title and authors) and the publisher abstract.
- Sect. 2 (02_related_work.tex), quote: "Social force simulations form transient blocking clusters, some at walls~\cite{parisi2005microscopic,cornes2021microscopic}."
- Verdict: PARTLY SUPPORTED. "Transient" is supported: a blocking cluster breaks and ends a "frictional clogging delay" (Sect. 2.2.2, Fig. 2). "Some at walls" understates the source. Cornes et al. define a blocking cluster as "the minimum subset of clusterized particles (i.e. spatial cluster) closest to the door whose first and last component particles are in contact with the walls at both sides of the door" (Sect. 2.2.1), so every blocking cluster is anchored to both walls. The abstract says the relevant structures in the faster-is-slower regime are "those blocking clusters that are somehow attached to the two walls defining the exit".
- Proposed: "Social force simulations form transient blocking clusters, chains of pedestrians in contact that span the door from wall to wall~\cite{parisi2005microscopic,cornes2021microscopic}." Parisi and Dorso 2005 was judged SUPPORTED in B_REPORT and was not re-read here; check that it uses the same definition before merging, otherwise cite only cornes2021 for the clause after the comma.

[13] Fu, Deng, Schadschneider, Li, Luo 2019, J. Stat. Mech. 2019(12) 123402. Exists as cited (Crossref). Read: abstract only (Semantic Scholar and OpenAlex; closed access, no repository copy).
- Sect. 1 (01_introduction.tex), quote: "Others credit fewer deadlocks or gridlocks to a detour term in a social force model~\cite{qu2018}, an anticipation term in a velocity model~\cite{xu2021anticipation} and turning and lateral steps in a cellular automaton at a bottleneck~\cite{fu2019}."
- Verdict: PARTLY SUPPORTED. Turning is credited: "The turning breaks the deadlock and releases the congestion at the bottleneck. The deadlock frequency decreases and the free travel time increases with the turning probability at the bottleneck." Lateral movement is not credited with fewer deadlocks: the abstract reports that slow lateral movement delays egress and that faster lateral movement "may lead to more frequent conflicts". The deadlocks also arise from finer spatial discretisation under a parallel update.
- Proposed: "...and turning at a bottleneck in a finely discretised cellular automaton~\cite{fu2019}."

[14] Gang and Veluri 2026, SIMULTECH 2026, pp. 474-481. Exists as cited (Crossref: proceedings-article, pages 474-481, 2026; DBLP conf/simultech/GangV26).
- Read: the publisher abstract via Semantic Scholar, and the camera-ready LaTeX source in the repository (code/paper/MainPaper/paper - Updated/main.tex, PDF dated 2026-04-23). The published PDF was not readable: the SCITEPRESS page needs JavaScript (open action).
- Sect. 1, quote: "The authors' earlier study~\cite{gang2026} credited optimal reciprocal collision avoidance (ORCA)~\cite{vandenberg2011} with the evacuations its configurations completed and found noise tuned to the same completion fraction indistinguishable from ORCA's velocity selection."
  - SUPPORTED. Abstract: "0/25 successful evacuations for SFM and SFM+TTC at w = 0.8m, vs. 13–14/25 for ORCA-enabled configurations ... within n = 25, passive noise is indistinguishable from ORCA's linear-program (LP)-based velocity selection as a deadlock-breaking mechanism".
  - The noise threshold σ50 = 0.049 m/s is the 50 % completion point; ORCA completed 52-56 %. "Tuned to the same completion fraction" is therefore fair.
  - Nuance: the earlier study already concluded that "symmetry-breaking -- not velocity-space optimisation -- is the operative mechanism" (camera-ready, Discussion). The sentence does not contradict this, but it should not be read as saying [14] credited ORCA's LP.
- Sect. 1, quote: "This paper extends~\cite{gang2026} and keeps its scenario (a room with a 0.8\,m door and 100 agents), its social force model with force-coupled ORCA and its noise surrogate ... The model of~\cite{gang2026} took densities from Voronoi cells with calibrated Weidmann coefficients".
  - SUPPORTED by the camera-ready: "At a 0.8 m exit with 100 agents (n=25, seeds 42--66)"; F^ORCA = m_i(v^ORCA − v_i)/τ_ORCA; C1+ε noise; ρ_V(i) = 1/A_i^Vor; Weidmann (γ, ρ_max) fitted (γ: 1.913 → 0.833).
- Sect. 1 and Sect. 6 statements on the legacy solver (repository, commits, line of sim/steering/orca.py) concern the code, not the publication; they were not checked here.

[33] Liu, Na, Yao, Liu, Chen 2026, Robotica 44(4) 1212-1230. Exists as cited (Crossref). Read: abstract only (closed access).
- Sect. 2, quote: "ORCA deadlocks in symmetric scenes~\cite{liu2026orcadeadlock} and in tight passages~\cite{dergachev2021case}."
- Verdict: SUPPORTED. Abstract: "in some scenes, such as where robots distribute symmetrically, ORCA usually fails to plan reasonable collision avoidance velocities, resulting in the robot getting stuck." The surrounding paragraph is about multi-robot systems, which matches.

[39] Qu, Xiao, Wu, Tang, Gao 2018, Physica A 492, 1153-1167. Exists as cited (Crossref).
- Read: abstract only. Semantic Scholar and OpenAlex have the abstract elided by the publisher, and ScienceDirect (including the accepted-manuscript link) returned HTTP 403, so the abstract was read through the Consensus index.
- Sect. 1, quote as for [13]: "Others credit fewer deadlocks or gridlocks to a detour term in a social force model~\cite{qu2018}, ..."
- Verdict: SUPPORTED. Abstract: "Simulation results show that the modified social force model including detour behavior could reduce the frequency of collision and deadlock".
- Caveat (already noted in P2_RESOLUTION.md): the scenarios are a corridor (uni- and bidirectional) and a real building, not a door. The sentence does not claim a door, but it follows "At a 0.8 m door"; the opening paragraph should not imply that Qu et al. studied doors.

## 4. Missing methodological citations (task 4)

Verbatim records are in reports/B3_bib_additions.bib. When merging: rename the keys (suggested: holm1979, schuirmann1987, royston2013, irwin1949, merkin1996, arnold1989); replace the unicode en dash in pages with "--"; drop url, ISSN and month as refs.bib does elsewhere; add pages = {152} to Royston and Parmar (Crossref article-number 152, not in the served BibTeX).

- Holm's sequentially rejective procedure: NOT FETCHED. There is no registered DOI: Crossref returns 404 for 10.2307/4615733, which OpenAlex lists, and doi.org says "DOI Not Found". JSTOR stable 4615733 returns a browser challenge, and the copy at ime.usp.br returns 403. Pointer: Holm, S., "A simple sequentially rejective multiple test procedure", Scandinavian Journal of Statistics 6, 65-70 (1979), https://www.jstor.org/stable/4615733. Volume and pages are from OpenAlex W2121044470 (not a publisher record; no issue given). Open action. Cite at the first "Holm-adjusted" (Sect. 4 protocol, statistics paragraph, and the Table 4/5 captions).
- Two one-sided tests: Schuirmann, D.J., J. Pharmacokinet. Biopharm. 15(6) 657-680 (1987), DOI 10.1007/BF01068419 (Crossref). Cite at "Two one-sided tests at level 0.05 declare equivalence" (04_protocol.tex).
- Restricted mean survival time: recommended Royston, P., Parmar, M.K.B., BMC Med. Res. Methodol. 13, 152 (2013), DOI 10.1186/1471-2288-13-152 (Crossref).
  - Why: it is the standard methodological reference that defines the restricted mean as "the area under the survival curve up to that point" and sets out its use as a summary when hazards are not proportional. This is the situation of the paper's time-to-free comparison (censored at T, compared without a proportional-hazards model). It is open access and widely cited (1108 citations in Semantic Scholar on 2026-11-15).
  - Irwin, J.O., J. Hyg. 47(2) 188-189 (1949), DOI 10.1017/S0022172400014443 is the historical origin of the restricted mean; it is optional, and one reference suffices for an LNNS page budget.
  - Cite at "(restricted mean up to $T$, RMST)" (04_protocol.tex).
- Lagrange-Dirichlet stability theorem: recommended Merkin, D.R., Introduction to the Theory of Stability, Texts in Applied Mathematics, Springer New York, 1996, DOI 10.1007/978-1-4612-4046-4 (Crossref book record, issued 1996; its chapter records carry 1997).
  - Crossref chapter titles: Ch. 4 "Stability of Equilibrium States and Stationary Motions of Conservative Systems", pp. 75-101 (DOI 10.1007/978-1-4612-4046-4_4); Ch. 7 "The Effect of Force Type on Stability of Motion", pp. 159-219.
  - The paper's statement (04_protocol.tex: strict local minimum of U stable when the remaining forces dissipate, Lyapunov function ½vᵀMv + U) is the conservative theorem plus dissipative forces, so these two chapters are the relevant ones by title.
  - Alternative: Arnold, V.I., Mathematical Methods of Classical Mechanics, 2nd edn., GTM 60, Springer New York, 1989, DOI 10.1007/978-1-4757-2063-1 (Crossref).
  - The book contents could not be read (Springer chapter pages return a JavaScript challenge), so the section and page of the theorem are not verified. Open action: confirm in Merkin Ch. 4 (and the dissipative extension in Ch. 7) and cite with the chapter or page, e.g. \cite[Ch.~4]{merkin1996}.

## 5. Parameter sources (task 5)

Karamouzas, Skinner, Guy 2014, PRL 113, 238701. Read the full text of arXiv:1412.1082v1, posted 2014-12-02 with journal-ref "Phys. Rev. Lett. 113, 238701 (2014)"; it includes the Supplemental Material. The APS supplemental page returned 401.
- Interaction energy (main text, Eq. 2): E(τ) = (k/τ²) e^(−τ/τ0), where τ is the time to collision. "Here, k is a constant that sets the units for energy." In Fig. 2, "The overall constant k is normalized so that E(1) = 1" (arbitrary units).
- Force: Eq. (3) and Suppl. Eq. (S1), F = −∇_r [k τ^-2 e^(−τ/τ0)], with an explicit gradient in Suppl. Eq. (S2).
- τ0: main text, "This estimate suggests that an appropriate value is τ0 ≈ 3 s" (a lower-bound estimate of the unscreened range).
- k: Supplemental Material, "Simulation results": "In all simulations, we set k = 1.5 and τ0 = 3 s as the default parameter values of the interaction forces." No unit is printed for k. Because E is an energy and τ a time, k carries energy × time², i.e. kg m².
- Consequence for Table 1: the value 1.5 is Karamouzas et al.'s default, not "this work". The paper uses E as a force magnitude, so the same number carries N s² (kg m), which corresponds to an energy-to-force length scale of 1 m, as Sect. 3 already says.
- Proposed Table 1 row: "$k_{\rm ttc}$ & TTC scale & $1.5$\,N\,s$^2$ (energy scale $k=1.5$ in~\cite{karamouzas2014}, used as a force) & \cite{karamouzas2014}". If space is tight: Value "$1.5$\,N\,s$^2$", Source "\cite{karamouzas2014}, adapted". The τ0 = 3 s row is correct as it stands.

Helbing, Farkas, Vicsek 2000, Nature 407, 487-490. Read the full text of arXiv:cond-mat/0009448v1 (28 Sep 2000; journal-ref "Nature 407, 487-490 (2000)"). Nature's typeset text was not fetched (paywall); open action only if the layout of the printed version matters.
- Quotes: "With a mass of mi = 80 kg ... A reasonable estimate for the acceleration time is τi = 0.5 s. With Ai = 2·10³ N and Bi = 0.08 m ... The parameters k = 1.2·10⁵ kg s⁻² and κ = 2.4·10⁵ kg m⁻¹ s⁻¹ determine the obstruction effects in cases of physical interactions."
- The wall force, Eq. (3), uses the same A_i, B_i, k and κ ("The interaction with the walls is treated analogously").
- Table 1 rows confirmed: m = 80 kg; τ = 0.5 s in [21]; A = 2000 N; B = 0.08 m; k = 1.2×10⁵ kg/s²; κ = 2.4×10⁵ kg/(m s); A_w = A; B_w = B. All agree.

Weidmann 1993 (DOI 10.3929/ethz-b-000242008). Access is no longer blocked. The ETH Research Collection REST API (server/api/pid/find → core/items/3bb92055-... → bundle ORIGINAL) served the scanned PDF "sr90_2auflage.pdf" (115 pp.).
- p. 62, Sect. 4.31.1 "Richtungsverkehr", Eqs. (15)-(16): "Mit v_F,hf = 1.34 m/s und D_max = 5.4 P/m² sowie dem Kurvenverlauf gemäss Abschnitt 3.25 ergibt sich die Eichkonstante zu γ = 1.913 P/m²." Eq. (16): v_F,hi = 1.34·[1 − e^(−1.913·(1/D − 1/5.4))], Kladek's function fitted by Weidmann (Abb. 58). The page was rendered and read as an image to confirm the OCR.
- γ = 1.913 and ρ_max = 5.4 are CONFIRMED, both in P/m² (persons per m²), consistent with the m⁻² in Table 1. The paper's Eq. (des) has the same form with v_F,hf → v_0.
- The v_0 row is also confirmed. Mean 1.34 m/s on p. 43: "Der Durchschnitt liegt bei 1.34 m/s". SD 0.26 m/s on p. 53, Sect. 3.3 "Streuung der Fussgängergeschwindigkeiten": "ergeben im Mittel eine Standardabweichung σ von 0.26 m/s oder 19.3 % des Mittelwertes".
- Suggested citations with location: \cite[p.~62, Eq.~(16)]{weidmann1993} for γ and ρ_max; \cite[pp.~43, 53]{weidmann1993} for v_0. Optional; the table's Source column is narrow.
- This closes the long-standing open action "Weidmann γ/ρ_max check" (B_REPORT Sect. 5; I4, P2 and I3 handoffs). The author should still glance at p. 62 before submission, since the outstanding item was an author check.

## 6. DOI case (task 6)

Proposal: write every DOI in lower case. This is the form both registries return in their APIs (Crossref "DOI" field and DataCite "doi" attribute, as fetched for all 46). DOIs are case-insensitive, and 151 of the 195 DOIs in refs.bib are already lower case. Changes for the cited entries (the only ones that print):

- [1] fzj_ped20219: 10.34735/PED.2021.9 → 10.34735/ped.2021.9
- [4] vandenberg2011avo: 10.1109/ICRA.2011.5980408 → 10.1109/icra.2011.5980408
- [6] boomers2023data: 10.17815/CD.2023.141 → 10.17815/cd.2023.141
- [10] dergachev2021case: 10.1109/CASE49439.2021.9551564 → 10.1109/case49439.2021.9551564
- [22] helbing2000freezing: 10.1103/PhysRevLett.84.1240 → 10.1103/physrevlett.84.1240

Uncited entries with upper case (no effect on the PDF; same rule if refs.bib is normalised): nicolas2018trapa, reis2020control, jain2026benchmarking, mankoc2009role, thomas2015fraction, caprini2020activity, bottinelli2016emergent, abate2008effective, ono2001effective, schreiber1999improved, schreiber1999surrogate, wexler2019dynamics, helbing2007dynamics, corbetta2016fluctuations, pouw2024data, karamouzas2014universal, szamel2014self, helbing1998social, lozano2012breaking, merrigan2017ergodicity, woillez2019activated, manning2010vibrational, rottler2014predicting, kretz2006experimental, e2002string, fzj_ped20052, fzj_ped20062, fzj_ped20139, fzj_ped20173, fzj_ped20181, fzj_ped20203, fzj_ped20096, sticco2017b, cugliandolo1997b, maierstein1993, silverberg2013b, fzj_pedda, guy2010, kleinmeier2019vadere.

New entries from B3_bib_additions.bib take the same rule (schuirmann: 10.1007/bf01068419; irwin: 10.1017/s0022172400014443). splncs04 prints the DOI as a link, so lower case also makes the reference list uniform.

## Summary of proposed changes to refs.bib and the text (for the merging session)

1. weidmann1993: title "Transporttechnik der Fussg{\"a}nger: Transporttechnische Eigenschaften des Fussg{\"a}ngerverkehrs, Literaturauswertung"; add edition = {2nd}.
2. vandenberg2011rvo2: extend the note on the source of the authors and title (Sect. 1), or switch to the registry metadata (author decision).
3. Table 1, k_ttc row: source \cite{karamouzas2014} with "1.5 as energy scale, used as a force" (Sect. 5). The table is generated (experiments/tables/make_table1.py from data/params/model.yaml), so change the generator, not the .tex.
4. Sect. 2: Cornes wording (Sect. 3). Sect. 1: Fu wording (Sect. 3).
5. Add schuirmann1987, royston2013 and merkin1996 (or arnold1989), and cite them at the TOST, RMST and Lagrange-Dirichlet sentences. Add holm1979 once its record is verified.
6. Lower-case the five cited DOIs (Sect. 6).

## OPEN ACTIONS FOR THE AUTHOR

1. Holm 1979: open https://www.jstor.org/stable/4615733 in a browser and confirm volume 6, issue (2?), pages 65-70 and year 1979; then add the entry (there is no DOI).
2. Merkin 1996 (or Arnold 1989): confirm the section and page of the Lagrange (Lagrange-Dirichlet) theorem and of the extension to dissipative forces; the book content could not be read through a script.
3. Gang and Veluri 2026: check the published SCITEPRESS PDF against the camera-ready used here (page range 474-481 is from Crossref).
4. Weidmann: glance at p. 62 (Eq. 16) of the second edition to sign off the check (values confirmed here; Sect. 5).
5. RVO2 citation metadata: choose CITATION.cff authors and title (recommended) or the Zenodo record's (Sect. 1).
6. Parisi and Dorso 2005: confirm it uses the wall-to-wall definition of a blocking cluster before the Cornes rewording cites both (Sect. 3).
7. Qu 2018, Fu 2019 and Liu 2026 were judged on abstracts only (no open full text); Karamouzas 2014 and Helbing 2000 on their arXiv versions.
8. Unchanged from B_REPORT: the CroMa licence (CC BY 4.0 from the site footer only) and the CroMa participant-count discrepancy.

## HANDOFF

Current state:
- Branch wt-B3 (worktree /Users/palaash/Developer/lnns-wt/B3), based on origin/main df8ed37. New files: reports/B3_REPORT.md and reports/B3_bib_additions.bib. No changes to paper/ or refs.bib.
- All 46 DOIs re-resolved, with 3 metadata mismatches (RVO2, Weidmann, Wolinski; Wolinski's is a Crossref deposit error).
- Weidmann γ = 1.913 and ρ_max = 5.4 confirmed on p. 62; v_0 = 1.34 ± 0.26 m/s confirmed on pp. 43 and 53.
- Karamouzas: k = 1.5 and τ0 = 3 s are their defaults.
- Helbing 2000 values confirmed.

Decisions made:
- Registered-year rule: the registry PublicationYear of the cited version → CroMa 2026, RVO2 2016 (both unchanged).
- RMST reference: Royston and Parmar 2013. Stability reference: Merkin 1996 (Arnold 1989 as an alternative).
- DOI case: lower case throughout.
- Holm not added, because no record could be fetched.

Open items: the eight OPEN ACTIONS above; merging these proposals into paper/refs.bib and the sections is the job of the merging session; Table 1 changes go through make_table1.py.
