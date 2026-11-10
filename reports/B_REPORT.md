# Session B report: references after the external review (2026-11-10)

Scope: paper/refs.bib (additions and corrections only, no key renamed or removed), source notes in reports/B_sources/ (croma.md, citation_use.md, grover_noise_guy.md, new_refs.md). Every field was checked against Crossref, DataCite, doi.org content negotiation, Zenodo, GitHub or arXiv. `make paper` passes and BibTeX reports 0 warnings.

## 1. The 37 cited entries
VERIFIED: every field matches the record. Notes on individual entries are in brackets.
- gang2026, helbing2000nature, helbing1995, karamouzas2014, vandenberg2011, xu2021, zuriguel2014, nicolas2018trap, hanggi1990, grover2020 (WAFR XIV, SPAR 17, pp. 294-312, 2021), koren1991, koster2013, grimm2005, beven2006, e2002, e2007, gronbechjensen2013, adrian2020crowds, kaplanmeier1958, kramers1940, wilson1927, mcnemar1947, fiorini1998, helbing2012, liang2024, wolinski2014parameter, cornes2021microscopic, parisi2005microscopic, grover2020symmetry.
- woillez2020: PRL 122(25), article 258001, published 2019. The year 2019 printed in the bibliography is right; the key's "2020" is wrong (rename in Wave 2).
- liu2026orcadeadlock: Robotica 44(4), 1212-1230, 2026. Authors Liu, Na, Yao, Liu, Chen, as in the entry.
- weidmann1993: DOI 10.3929/ethz-b-000242008 (DataCite); report type and number "IVT Schriftenreihe, 90" and year 1993 confirmed.
- arrhenius1889: Crossref volume "4U" (one of two Crossref records); 4 kept.
- weibull1951: Crossref names the publisher as Wiley; the journal is ASME's. Fetched value kept; publisher is not printed by splncs04.
- fzj_ped20219: DataCite title "Bottleneck experiments with varying motivation levels"; the 8 creators as in the entry; publisher Forschungszentrum Jülich; year 2026 is the publication year of the DOI.

CORRECTED:
- helbing2000freezing: authors were "Illes Farkas, Tamas Vicsek" without accents or the middle initial. Now "Farkas, Illés J." and "Vicsek, Tamás", as in Crossref.
- vandenberg2011rvo2: the title is now the CITATION.cff title, "Optimal Reciprocal Collision Avoidance". The entry now names release v2.0.2 on Zenodo (2016, DOI 10.5281/zenodo.7039667) and git commit c96a6ec. The port names "v2.0.3, src/Agent.cpp" but records no commit. Version 2.0.3 exists only on main, from 57098835 (2020-12-19) until Agent.cpp was renamed in 423cb115 (2022-09-22). Between c96a6ec and the last Agent.cpp (7f85810) the only code change is in the obstacle branch (s<1 became s<=1), which the port does not use. The agent ORCA lines and linearProgram1/2/3 are identical, so the citable v2.0.2 release contains the ported code.

UNVERIFIABLE: none. A numerical check is outstanding (Sect. 5).

Other entries fixed (not cited yet): guy2010 was a misc with a journal field and is now an inproceedings with pages 119-128 and its editors. Article numbers added: pastor2015 (062817), garcimartin2017 (10792), chraibi2010 (046111).

## 2. Citation use (problems only; full verdicts in B_sources/citation_use.md)
(a) Grover et al.: the referee is right. The WAFR paper (preprint arXiv:1911.09146, Sect. 2.2) says it does "not consider additive perturbations for resolving deadlocks". It resolves deadlock with a three-phase switching controller with a convergence proof, and it has no stability analysis. The IJRR 2023 version (arXiv:2206.01781 = grover2023) says the same and adds that random noise "can potentially prevent" deadlock, without guarantees. The IFAC abstract says symmetry renders deadlock stable and that skewness helps to *evade* it (abstract only).
- 02, S1 -> "For multi-robot systems that avoid collisions through control barrier functions, Grover et al. characterised deadlocks as force-balance equilibria of the closed-loop dynamics, showed that symmetric configurations converge to them, and resolved them with a provably correct switching controller rather than with additive perturbations~\cite{grover2023,grover2020}."
- 02, symmetry -> "Symmetric configurations drive such robots into deadlock and breaking the symmetry helps them avoid it~\cite{grover2020symmetry,grover2023}, and ORCA itself deadlocks in symmetric robot scenes~\cite{liu2026orcadeadlock}."
- 08, S2 -> "...at multi-robot deadlocks, closed-loop equilibria that Grover et al. resolve with a switching controller because additive perturbations carry no guarantee~\cite{grover2023}."

(b) liang2024 and helbing2012: the sentence is not supported as worded. Itaewon happened in a sloping alley under 4 m wide where two opposing streams met. In the Love Parade case the bottleneck was the ramp and tunnel system, and the authors deny that a rush towards a narrowing caused the deaths (they name crowd turbulence).
- 01 -> "Fatal crowd disasters happen where dense crowds build up in narrow passages and bottlenecks~\cite{helbing2012,liang2024}, and a simulation used to plan such a place is only as trustworthy as the mechanism credited for its bottleneck behaviour."

(c) helbing2000freezing shows the opposite: more noise freezes the counterflow. The escape-panic paper has no noise term. The only verified support is second-hand: xu2021 says random behavioural variations are important to mitigate clogs in simulations. Example code shipped with RVO2 also perturbs agents slightly "to avoid deadlocks due to perfect symmetry".
- 08 (iv) -> "treat per-step noise, reported to mitigate clogs in pedestrian simulations~\cite{xu2021}, as having a $\Delta t$-dependent temperature". Alternatively delete the clause.

(d) CroMa: see Sect. 3. adrian2020crowds does not describe these runs.

Other problems:
- xu2021 ("boundary parameters alone decide"): not supported; clogs depend on the exit geometry and on the model parameters. -> "In a velocity-based pedestrian model, prolonged clogs depend on the width and position of the exit and on the model's parameters, but hardly on the update scheme or time step~\cite{xu2021}".
- gronbechjensen2013: partly supported. The paper shows that its own scheme's statistics do not depend on Δt; the Δt-dependent temperature of fixed per-step noise is our derivation. -> "Discretised Langevin schemes need not sample the bath temperature: the BBK scheme is off by O(Δt), and Grønbech-Jensen and Farago built one whose statistics do not depend on Δt~\cite{gronbechjensen2013}; for the fixed per-step noise used here the effective temperature depends on Δt (Sect.~\ref{sec:teff}), which we use as a probe."
- wolinski2014parameter: partly supported. -> "...in crowd simulation the same model behaves very differently under different parameters, and calibrated models can still differ in how they avoid collisions~\cite{wolinski2014parameter}."
- zuriguel2014: the "people" are social-force simulations. -> "Grains, colloids, sheep and simulated pedestrians passing a narrow outlet ...".
- fiorini1998 defines collision "at some future time"; the time horizon comes from vandenberg2011. Drop "within a time horizon" or move that clause to vandenberg2011.
- mcnemar1947 gives a standard error and its chi-square form, not an exact test. -> "McNemar's test in its exact (binomial) form".
- All other cited sentences are SUPPORTED: parisi2005, cornes2021, nicolas2018trap, hanggi1990, woillez, koren1991, karamouzas2014, vandenberg2011, e2002/e2007, grimm2005, beven2006, koster2013, Arrhenius/Kramers, liu2026, gang2026, wilson1927, kaplanmeier1958, weibull1951.

## 3. CroMa resolution (B_sources/croma.md)
- Runs used (data/ext/croma, E10): 4D030 (w080_l200_h0), 4D040 (w080_l200_h1), 4D110 (w080_l021_h0), 4D120 (w080_l021_h1), 4D130 (w080_l021_h2). All five were recorded on 11.10.2021 in Düsseldorf, with a bottleneck 0.8 m wide and 2.0 m or 0.2 m long. Participants were told to walk normally (h0), to hurry (h1) or, in 4D130, to give full commitment (h2).
- Describing publication: Boomers et al. 2023, Collective Dynamics 8, 1-57, DOI 10.17815/CD.2023.141 (Sect. 3.7, App. A.9, Table 19). Added as boomers2023data. Adrian, Seyfried, Sieben 2020 used a 0.5 m gate with corridor widths from 1.2 to 5.6 m, from a different dataset (10.34735/ped.2018.1). Cite it only for context, not for these runs.
- The paper's text is wrong in three places: 2.0 m and 0.2 m are bottleneck *lengths*, not corridor widths; the length is 0.2 m, not 0.21 m; and one run is "full commitment".
- Licence: the DataCite rightsList is empty; the archive site footer gives CC BY 4.0. The landing page requests no specific citation and points to the data guidance paper. Cite the dataset DOI and Boomers et al. 2023.
- 07 -> "The CroMa bottleneck experiments~\cite{fzj_ped20219,boomers2023data} include \EtenHumanN\ runs through a 0.8\,m wide bottleneck, two with a bottleneck 2.0\,m long and three with one 0.2\,m long (a door in a wall); participants walked normally, hurried or, in one run, gave full commitment."

## 4. New and existing entries for the new citations
| key | verified against | cite in / for |
|---|---|---|
| langer1969 (exists) | Crossref, all fields | Sect. 2 activated escape / Sect. 4.4: many-dimensional prefactor ("Langer prefactor") |
| henkelman2000 (exists) | Crossref | barrier section: climbing image (cite with e2007, whose string carries it) |
| melnikov1986 | Crossref, JCP 85, 1018-1027 | damping regime / Kramers turnover. The title is "...Exact solution of the Kramers problem" |
| vandenberg2011avo | doi.org, ICRA 2011, 3475-3482 | Sect. 3: relaxation to the LP velocity, a=(v'-v)/δ, Eq. (7) |
| moussaid2011 | doi.org, PNAS 108, 6884-6888 | pedestrian precedent: chosen velocity relaxed with τ=0.5 s |
| guy2010 (exists, fixed) | EG DL | NOT for the conversion: PLEdestrians applies the ORCA-set velocity directly, with no force |
| boomers2023data | Crossref | Sect. 7, CroMa runs |
| seyfried2009 (exists) | Crossref | Sect. 7: bottleneck flow vs width |
| hoogendoorn2005 | Crossref, Transp. Sci. 39(2) 147-159 | Sect. 7, with seyfried2009 |
| pastor2015 (exists, +062817) | Crossref | Sect. 2 clogging: experimental faster-is-slower |
| garcimartin2017 (exists, +10792) | Crossref | Sect. 2 clogging: competitive evacuation |
| janda2009 (exists) | Crossref | Heat class precedent: vibration unjams a hopper (do not cite the duplicate janda2009unjamming) |
| dergachev2021case | Crossref, IEEE CASE 2021, 1489-1494 | Sect. 2 deadlock: ORCA fails in tight passages (robots on grid maps); use instead of arXiv dergachev2021 |
| grover2023 (= arXiv:2206.01781, exists) | Crossref, IJRR 42(6) 317-336 | Sect. 2 / 8, as in Sect. 2(a); grover2022before is its arXiv copy |
| tordeux2016 | Crossref, TGF'15, 225-232 | Related work on velocity models; JuPedSim's collision-free speed model |
| chraibi2026jupedsim | DataCite, Zenodo v1.3.2 | the JuPedSim comparison (no peer-reviewed article with a DOI exists) |
| kleinmeier2019vadere | Crossref, Coll. Dyn. 4, A21 | the Vadere comparison |
| chraibi2010 (exists, +046111) | Crossref; Sect. III read | SFM stiffness: strong repulsion oscillates, weak repulsion overlaps |
| lakoba2005 | Crossref, Simulation 81(5) 339-352 | SFM re-parametrisation and overlap-free integration (abstract only; not about walls) |

Statistics citations: drop mcnemar1947 (the source has no exact test; name the test) and wilson1927 (a standard interval). Keep kaplanmeier1958 (the estimator handles censored times) and weibull1951 (a physical fit). All four stay in refs.bib.

## 5. Outstanding actions
- weidmann1993: check γ=1.913 and ρmax=5.4 against the original table. The ETH Research Collection returned HTTP 403 to scripted access; a secondary source (Kretz et al., arXiv:1512.01426) gives the same values.
- Code (not this session's): E10 uses L=0.21 m where the archive gives 0.2 m. The archive counts more participants per run than the files have track IDs (e.g. 161 vs 135); not resolved.
- IFAC symmetry paper and the primary sources behind xu2021's noise remark (Helbing 2005, Hidalgo 2017): only abstracts or secondary text were read. koster2013, mcnemar1947, fiorini1998 and kramers1940 were also judged on abstracts.
- CroMa licence: the CC BY 4.0 comes from the site footer only; ask the archive to confirm.
- Wave 2: rename woillez2020 to a 2019 key; drop the arXiv duplicates (helbing2000prl/helbing2000freezing, janda2009unjamming, xu2021prolonged, grover2022before, dergachev2021).
