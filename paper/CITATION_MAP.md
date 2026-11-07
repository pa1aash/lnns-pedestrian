# Citation map

Section to keys. Keys marked OUTSTANDING are not yet in refs.bib (see end).

## 1 Introduction
- `gang2026`: the conference paper this extension builds on (SIMULTECH 2026, failure-mode ablation of SFM, TTC, ORCA)
- `helbing2000nature`: escape-panic social force model: the canonical mechanism-claim target in crowd simulation
- `karamouzas2014`: anticipatory-interaction law behind the TTC paradigm
- `vandenberg2011`: ORCA, the third steering paradigm audited
- `grimm2005`: pattern-oriented modelling: the audit principle for mechanism claims
- `liang2024`: crowd-crush case motivating dense-crowd stakes (conference ref; authors differ from conference list)
- `helbing2012`: crowd-disaster analysis motivating dense-crowd stakes (conference ref)

## 2 Background
- `helbing1995`: social force model (SFM)
- `zuriguel2014`: clogging transition through bottlenecks
- `nicolas2018trap`: trap model of clogging and unclogging (Nicolas, Garcimartin, Zuriguel 2018)
- `hanggi1990`: Kramers escape theory review
- `kramers1940`: original Kramers escape-rate paper
- `cugliandolo1997`: effective temperatures and aging; contrast with Kramers escape
- `grover2020`: multi-robot deadlock analysis and resolution (2020)
- `grover2023`: before, during and after multi-robot deadlock (2023)
- `grimm2005`: pattern-oriented modelling (2005)
- `grimm2012`: pattern-oriented modelling as a multi-scope for predictive models (2012)
- `fiorini1998`: velocity obstacles, ancestor of ORCA (conference ref)
- `vandenberg2008`: reciprocal velocity obstacles, ORCA precursor
- `guy2010`: PLEdestrians least-effort model (conference ref)
- `cristiani2023`: all-densities pedestrian simulator (conference ref)
- `dang2024`: dense crowd simulation review (conference ref)
- `vantoll2020`: SPH-agent extreme-density simulation, MIG 2020 (title cited by conference paper)
- `vantoll2021`: SPH crowds, Computers & Graphics 2021 (venue cited by conference paper)
- `korbmacher2022`: trajectory-prediction review, knowledge-based vs learned (conference ref)

## 3 Model and scenarios
- `helbing1995`: SFM desired and interaction forces
- `helbing2000nature`: contact terms (k, kappa) and wall law
- `karamouzas2014`: TTC force law F ~ exp(-tau/tau0)/tau^2
- `vandenberg2011`: ORCA half-plane construction
- `vandenberg2011rvo2`: RVO2 library implementing ORCA (authors' CITATION.cff; cite with vandenberg2011)
- `fzj_ped20219`: CroMa bottleneck geometry and trajectories (FZJ dataset)
- `steffen2010`: density estimation methods (Voronoi) vs the 3 m disk count used
- `mullick2025`: bias in density estimation (Voronoi perspective), conference ref
- `koster2013`: numerical pitfalls in SFM integration (integrator modes)
- `weidmann1993`: Weidmann speed-density law (gamma, rho_max); DataCite record 10.3929/ethz-b-000242008
- `fruin1971`: levels-of-service density context (conference ref); LoC MODS record LCCN 70159312

## 4 Mechanism classes; rest-state lemma
- `koren1991`: local minima / deadlock in potential-field navigation
- `barraquand1991`: local minima in planning, distributed representation

## 5 Deadlock physics
- `hanggi1990`: Kramers rate prefactors and barrier crossing
- `kramers1940`: Kramers escape rate
- `arrhenius1889`: Arrhenius temperature dependence of rates
- `weibull1951`: Weibull distribution for survival times
- `e2002`: string method for rare events / minimum-energy paths
- `e2007`: simplified and improved string method
- `henkelman2000`: climbing-image NEB, alternative saddle search
- `langer1969`: decay of metastable states

## 6 Attribution results
- `wilson1927`: Wilson score interval for proportions
- `mcnemar1947`: McNemar test for paired proportions
- `kaplanmeier1958`: Kaplan-Meier estimator (JASA 1958)
- `schuirmann1987`: two one-sided tests, equivalence
- `lakens2017`: equivalence-testing primer

## 7 Validity
- `fzj_ped20219`: CroMa 2021 dataset, DOI 10.34735/ped.2021.9 (DataCite lists year 2026, title 'Bottleneck experiments with varying motivation levels')
- `seyfried2009`: bottleneck flow reference data
- `steffen2010`: measurement methods for density, flow and speed

## 8 Discussion
- `grover2020`: robot deadlock resolution
- `grover2023`: robot deadlock lifecycle
- `wang2017`: safety barrier certificates for multi-robot collision avoidance
- `martinezbaselga2025avocado`: ORCA-family planner for robots (AVOCADO; key martinezbaselga2025avocado)

## Entries in refs.bib not needed by the outline (kept in the file)

`helbing2000prl`, `xu2021`, `lozano2012`, `janda2009`, `mankoc2009`, `guerrero2019`, `merrigan2018`, `caitano2021`, `thomas2015`, `abate2008`, `szamel2014`, `woillez2020`, `hidalgo2018`, `souzy2020`, `sticco2017`, `hidalgo2017`, `chandra2025`, `echeverri2024`, `kretz2006`, `liddle2011`, `rupprecht2011`, `garcimartin2014`, `garcimartin2017`, `nicolas2017`, `corbetta2017`, `corbetta2018`, `pouw2024`, `jelic2012`, `gu2025`, `lozano2015`, `ono2002`, `widmercooper2008`, `manning2011`, `bottinelli2016`, `bottinelli2017`, `silverberg2013`, `suzuno2013`, `kirchner2003`, `pastor2015`, `chraibi2010`, `reis2021`, `garcimartin2016`, `helbing2007`, `liu2009`, `jelic2012b`, `seitz2015`, `wang2018`, `orendurff2004`, `beven2006`, `sargent2013`, `lopezpaz2017`, `kim2021`, `wellek1993`, `comnougue1993`, `firth1993`, `heinze2001`, `kaplan1958`, `clauset2009`, `sheppard2008`, `henkelman1999`, `higham2001`, `gronbechjensen2013`, `kloeden1992`, `theiler1992`, `lancaster2018`, `egolf2000`, `baule2012`, `caprini2020`, `nicolas2018trapa`, `grover2020deadlock`, `reis2020control`, `mestres2025control`, `grover2022before`, `jain2026benchmarking`, `mankoc2009role`, `thomas2015fraction`, `chandra2025deadlock`, `caprini2020activity`, `wu2025hierarchical`, `bottinelli2016emergent`, `abate2008effective`, `ono2001effective`, `cherel2015beyond`, `schreiber1999improved`, `schreiber1999surrogate`, `duongidentifying`, `mackey2004deterministic`, `wexler2019dynamics`, `helbing2007dynamics`, `corbetta2016fluctuations`, `pouw2024data`, `helbing2000simulating`, `karamouzas2014universal`, `guerrero2018slow`, `xu2021prolonged`, `helbing2000freezing`, `szamel2014self`, `monthus1996models`, `lakens2017equivalence`, `helbing1998social`, `nicolas2016influence`, `evers2011modelling`, `echeverriahuarte2024body`, `nicolas2018counterintuitive`, `lozano2012breaking`, `janda2009unjamming`, `merrigan2017ergodicity`, `hathcock2025stochastic`, `grnbechjensen2013simple`, `leimkuhler2012rational`, `woillez2019activated`, `touchette2010brownian`, `baule2012singular`, `manning2010vibrational`, `rottler2014predicting`, `sticco2019re`, `seyfried2007new`, `seyfried2008enhanced`, `liddle2011microscopic`, `adrian2020crowds`, `kretz2006experimental`, `nicolas2017pedestrian`, `clauset2009power`, `ritz2015dose`, `e2002string`, `ryabko2013reducing`, `romano2020permutation`, `austin2016`, `leimkuhler2013`, `schreiber1996`, `schreiber2000`, `fzj_ped20052`, `fzj_ped20062`, `fzj_ped20139`, `fzj_ped20173`, `fzj_ped20181`, `fzj_ped20203`, `fzj_ped20096`, `suzuno2015`, `sticco2017b`, `dergachev2021`, `cugliandolo1997b`, `maierstein1993`, `grafke2018`, `silverberg2013b`, `tordeux2019`, `viswanathan2014`, `tan2021`, `harth2020`, `fzj_pedda`

## Notes

- Conference-bibliography mismatches found against Crossref: Seoul Halloween paper (authors Liang, Lee, Sun, Wong; conference lists Lee, Kim, Park, Choi); Mullick et al. (article 130251, 2025; conference gives 130204, 2024); van Toll (conference title is the MIG 2020 paper, venue is the C&G 2021 paper).
- Duplicates by content: kaplan1958 (Springer reprint) and kaplanmeier1958 (JASA); use the latter. nicolas2018trap and nicolas2018trapa (arXiv).
- Dataset keys fzj_ped* keep their FZJ-style keys, unchanged.
