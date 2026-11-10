# New and re-checked references (fetched 2026-11-10)

BibTeX for new entries: paper/refs.bib (Session B additions block) (each entry carries a `% source:` line). Every field comes from the fetched Crossref / doi.org / DataCite / arXiv record; nothing was filled from memory.

## New entries

### melnikov1986
- Source: https://doi.org/10.1063/1.451844 (BibTeX), https://api.crossref.org/works/10.1063/1.451844
- Verified: title "Theory of activated rate processes: Exact solution of the Kramers problem"; V. I. Mel'nikov, S. V. Meshkov; J. Chem. Phys. 85(2), 1018--1027, 1986. All match the request. The title says "exact solution of the Kramers problem"; this is the turnover theory that bridges the low- and high-damping regimes.
- Placement: activated-escape section, where the damping regime is set (why the moderate-damping/turnover prefactor applies rather than the spatial-diffusion or energy-diffusion limit).

### hoogendoorn2005
- Source: https://doi.org/10.1287/trsc.1040.0102, https://api.crossref.org/works/10.1287/trsc.1040.0102
- Verified: "Pedestrian Behavior at Bottlenecks"; Serge P. Hoogendoorn, W. Daamen; Transportation Science 39(2), 147--159, 2005. All match.
- Placement: human-comparison section, next to seyfried2009, for bottleneck flow vs width (and zipper/lane formation in the bottleneck).

### tordeux2016
- Source: https://doi.org/10.1007/978-3-319-33482-0_29; book record https://api.crossref.org/works/10.1007/978-3-319-33482-0 (editors Knoop, Daamen; Cham); arXiv https://arxiv.org/abs/1512.05597 (same title and authors, 2015-12-17).
- Verified: published version is the chapter in Traffic and Granular Flow '15, Springer, 2016, pp. 225--232. Abstract: "minimal speed-based pedestrian model for which particle dynamics are intrinsically collision-free". Cite the Springer chapter, not the arXiv preprint.
- Placement: related work on velocity-based models (alongside ORCA), and in the external-comparison paragraph, since this model is the JuPedSim "CollisionFreeSpeed" model used there.

### chraibi2026jupedsim (JuPedSim)
- Source: https://doi.org/10.5281/zenodo.18806940 (BibTeX), https://api.datacite.org/dois/10.5281/zenodo.18806940
- Verified: Zenodo software record "JuPedSim", version v1.3.2, issued 2026-02-27, creators Chraibi, Kratz, Schrödter, The JuPedSim Development Team. v1.3.2 is the version named in `code/results_analysis/external_comparison_paragraph.md`. The concept DOI (all versions) is 10.5281/zenodo.1293771.
- Peer-reviewed alternative: none found with a DOI. OpenAlex lists "JuPedSim: an open framework for simulating and analyzing the dynamics of pedestrians" (2016) with no DOI or venue; Crossref title search returned nothing. So the versioned Zenodo DOI is the citable reference.
- Placement: external-comparison paragraph / Table `tab:external` caption ("JuPedSim v1.3.2 [cite]").

### kleinmeier2019vadere
- Source: https://doi.org/10.17815/CD.2019.21, https://api.crossref.org/works/10.17815/CD.2019.21
- Verified: "Vadere: An Open-Source Simulation Framework to Promote Interdisciplinary Understanding"; Kleinmeier, Zönnchen, Gödel, Köster; Collective Dynamics 4, article A21, 2019 (published 2019-09-03). Matches the request; the article number is A21 (in `pages`). Peer-reviewed journal.
- Placement: related work / introduction, as the other open-source simulator (which also has an OSM, a gradient navigation model and an SFM), next to JuPedSim.

### chraibi2010 (SFM stiffness critique, recommended 1 of 2)
- Source: https://doi.org/10.1103/PhysRevE.82.046111, https://api.crossref.org/works/10.1103/PhysRevE.82.046111; full text read from arXiv:1008.4297v2.
- Verified: PRE 82(4), 046111, 2010; Chraibi, Seyfried, Schadschneider. Sect. III "Overlapping vs. oscillation" says directly that stronger repulsion "leads to oscillations in the trajectories" (and backward motion), while weaker repulsion "leads inevitably to overlapping between pedestrians or between pedestrians and obstacles"; no single strength removes both. This is exactly the stiffness trade-off of force-based repulsion, walls included.
- Placement: the wall-force / numerical-stiffness discussion (where the short-range wall law and the time step are justified), cited with koster2013.

### lakoba2005 (SFM re-parametrisation/numerics, recommended 2 of 2)
- Source: https://doi.org/10.1177/0037549705052772, https://api.crossref.org/works/10.1177/0037549705052772; abstract via OpenAlex.
- Verified: Simulation 81(5), 339--352, 2005; Lakoba, Kaup, Finkelstein. Abstract: the Helbing-Farkas-Vicsek parameter values "may produce counterintuitive results" for single or few pedestrians; the authors re-parametrise the model and give an explicit integration algorithm that "prevents simulated pedestrians from overlapping". Caveat: the abstract does not mention the wall force specifically (full text is paywalled and was not read), so cite it for parameter realism and overlap-safe numerics, not as a wall-force critique.
- Placement: same paragraph as chraibi2010.

### dergachev2021case (published version of arXiv:2107.00246)
- Sources: https://arxiv.org/abs/2107.00246, https://arxiv.org/bibtex/2107.00246, https://doi.org/10.1109/case49439.2021.9551564, https://api.crossref.org/works/10.1109/case49439.2021.9551564; PDF https://arxiv.org/pdf/2107.00246.
- Verified: title "Distributed Multi-agent Navigation Based on Reciprocal Collision Avoidance and Locally Confined Multi-agent Path Finding", Stepan Dergachev and Konstantin Yakovlev, matching the existing `dergachev2021`. The arXiv comment says "accepted to CASE'21". The published version is IEEE CASE 2021 (17th Int. Conf. on Automation Science and Engineering, Lyon, 23-27 Aug 2021), pp. 1489--1494. It is not ECMR, so the key is `dergachev2021case`, not `dergachev2021ecmr`.
- Does it report ORCA deadlocks in narrow passages? Yes. Abstract: "navigation through the tight passages or confined spaces, deadlocks are likely to occur". Sect. I: agents "get stuck in a deadlock. They lower down their velocities to zero". Sect. V: on Gaps 3 with 40 agents, "ORCA was not able to solve a single instance". Caveat: these are grid-map robot swaps (two halls joined by 1 or 3 narrow passages, half the agents on each side going the other way), so it is bidirectional robot navigation, not pedestrian egress.
- Recommendation: replace the `@misc` arXiv entry with `dergachev2021case`. Cite it in related work for "reactive ORCA deadlocks in confined passages; resolved there by a locally centralised MAPF solver (an external-coordination Reshape/Prevent analogue)".

### Not recommended (checked)
- parisi2009 (Physica A 388(17), 3600--3608, DOI 10.1016/j.physa.2009.05.027): the abstract criticises SFM flow rates vs door width and the fundamental diagram, not the wall force or numerics. It could go in the human-comparison section, but it is not one of the two picks.
- chen2018 (Transport Reviews 38(5), 625--653, DOI 10.1080/01441647.2017.1396265; Crossref issue date 2017-11): a review of SFM variants and calibration, with no specific wall/stiffness critique.
- dietrich2014 (PRE 89(6), 062801, DOI 10.1103/PhysRevE.89.062801): proposes the alternative gradient navigation model, which "avoids model-induced oscillations completely", but it is a replacement model rather than an SFM critique. A possible third citation if the stiffness paragraph needs one.
- Kretz et al. 2018 TRR 2672, 228--238 (DOI 10.1177/0361198118786641): calibration guidance, not about walls. Sticco et al. 2020 Saf. Sci. 121, 42--53 (friction): no abstract could be retrieved, so it was not assessed.

## Existing entries checked against Crossref (refs.bib, fetched 2026-11-02)

| key | Crossref check | mismatch / action | placement |
|---|---|---|---|
| pastor2015 | PRE 92(6), article 062817, 2015-12-15, 10 authors match | `pages` missing: add `pages = {062817}` | clogging related work: experimental faster-is-slower |
| garcimartin2017 | Sci. Rep. 7(1), article 10792, 2017-09-07, 5 authors match | `pages` missing: add `pages = {10792}` | clogging related work: competitive evacuation |
| seyfried2009 | Transp. Sci. 43(3), 395--406, 2009, 6 authors match | none | human comparison: flow vs width |
| janda2009 | EPL 87(2), 24002, 2009, 6 authors match | none. Note: refs.bib also has a duplicate `@misc{janda2009unjamming}` (line ~1583); cite only `janda2009` | Heat class: vibration unjams a granular hopper |
| langer1969 | Ann. Phys. 54(2), 258--275, 1969, J. S. Langer | none | activated-escape related work / barrier section: multidimensional rate prefactor |
| henkelman2000 | J. Chem. Phys. 113(22), 9901--9904, 2000, 3 authors match | none | barrier section. Note: Henkelman 2000 is climbing-image NEB; the climbing image inside the string method is from `e2007` (already in refs.bib), so cite both: "string method [e2002,e2007] with a climbing image [henkelman2000,e2007]" |
| dergachev2021 | see above | upgrade to `dergachev2021case` | related work: ORCA deadlocks |

No field mismatches were found in the six entries beyond the two missing article numbers.
