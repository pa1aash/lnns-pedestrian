# Citation use check: does each source support the sentence that cites it?

Checked 2026-11-10. For each sentence the source was read: full text where open access (PLOS, EPJ Data Science, arXiv versions, author or repository PDFs), otherwise the Crossref/OpenAlex abstract. Downloads are in the session scratch directory `citeuse/`. Keys handled elsewhere were skipped: grover2020, grover2020symmetry, helbing2000freezing, fzj_ped20219, adrian2020crowds, guy2010.

Status key: SUPPORTED / PARTLY / NOT SUPPORTED.

## Summary of problems

| # | Key(s) | Status | Problem |
|---|---|---|---|
| 1 | liang2024, helbing2012 | NOT SUPPORTED as worded | Itaewon was a narrow sloping alley with two opposing streams colliding mid-alley; Duisburg was crowd turbulence in a nearly stationary crowd on a ramp bottleneck. Neither is people pressing towards a narrow opening. Helbing & Mukerji argue against the "crush towards a narrowing" reading for Duisburg. |
| 2 | xu2021 | NOT SUPPORTED as worded ("alone") | Prolonged clogs depend on the spatial boundary *and* on the movement-model parameters; only algorithmic factors (update scheme, time step) have no effect. |
| 3 | wolinski2014parameter | PARTLY | The paper shows a model's behaviour depends strongly on its parameters and that calibrated models can still behave differently. It does not show models passing single-score validation "for different reasons". |
| 4 | gronbechjensen2013 | PARTLY | The paper's main result is a scheme whose statistics do *not* depend on Δt. It reports Δt-dependent temperature only for other schemes (BBK: O(dt) error). The paper's own per-step-noise dependence is a derivation in this paper, not a GJ-F result. |
| 5 | zuriguel2014 | PARTLY (minor) | "People" are SFM simulations in that paper, not human experiments. The criterion is divergence of the mean time lapse between passages, which is close enough to "stoppages". |
| 6 | fiorini1998 | PARTLY (minor) | Fiorini & Shiller define the VO for collision "at some future time". The time-horizon (truncated) VO is van den Berg et al.'s VO^τ. |
| 7 | mcnemar1947 | PARTLY (minor) | McNemar (1947) gives a standard-error formula and its chi-square equivalent. The *exact* (binomial) version is a later convention. |
| 8 | weidmann1993 | Constants not checked against the primary source | The ETH Research Collection blocked access (HTTP 403, anti-scraping), so the report itself was not read. A secondary source (Kretz, Lohmiller & Schlaich, arXiv:1512.01426) quotes Weidmann's parametrisation as v_f=1.34 m/s, γ=1.913 /m², ρ_max=5.4 /m², which matches the paper. |
| 9 | woillez2020 (key) | Metadata note | Crossref: PRL 122, 258001, published 28 June 2019. The bib `year = {2019}` is correct, so the printed citation is right; only the key name says 2020. |

Everything else is SUPPORTED (details below).

---

## (b) Crowd-disaster sentence: deep read

**Sentence (01_introduction.tex):** "Fatal crowd crushes happen where many people press towards a narrow opening~\cite{liang2024,helbing2012}, and a simulation used to plan such a place is only as trustworthy as the mechanism credited for its bottleneck behaviour."

**Status: NOT SUPPORTED as worded** (both sources support a weaker "narrow passages / bottlenecks" claim).

**liang2024** (Liang, Lee, Sun, Wong, PLOS ONE 19(7) e0306764, 2024; full text read):
- Geometry: the crush happened in an alley joining Itaewon-ro (south street) and Itaewon-ro 27ga-gil (north street). The alley had "an average width of less than 4 meters" and "quickly became a bottleneck" as flows from both streets met in it.
- Location of the crush: victims were concentrated in an 18.24 m² area "situated in the middle of the alley", not at a door, gate or opening.
- Mechanism: the authors name the collision of two opposing pedestrian streams inside the alley as the key cause ("crush, triggered by the bidirectional pedestrian stream"). Their simulation puts peak density 9.95 ped/m² and pressure 1961 N/m at the collision point.
- Slope: the alley is sloped. They add a leaning force because "pedestrians fell back down the sloping alley", and they note that "a slight slope intensified the crowd forces".
- Other factors: poor crowd management (opening the south-street driveway raised inflow), night-time visibility, and unanswered police calls.
- Their recommendation: avoid "narrow pathways and bidirectional traffic".
- Verdict: Itaewon happened in a **narrow sloping alley under counter-flow**, not where people pressed towards a narrow opening.

**helbing2012** (Helbing & Mukerji, EPJ Data Science 1:7, 2012; full text read):
- Geometry: visitors entered and left the festival area through tunnels and a single ramp. The ramp was the main bottleneck, narrowed further by fences, and police cordons on it stopped the flow both ways. A narrow staircase beside the ramp was the only visible escape route. Most victims died "between the staircase and the billboard" at the lower end of the ramp.
- Mechanism: the authors argue that the deaths were **not** a classical crush. They write "a rush towards the narrow staircase did not cause the crowd disaster", and the crowd "barely moved forward". In their account the cause was crowd turbulence ("crowd quake") at extreme density, which led to a domino effect of falling people. They separate this explicitly from a "classical crush", in which people move towards a physical bottleneck and are crushed before its narrowest point. They also say that crushing at extreme density "rather happens when a large crowd moves too quickly towards a narrowing", which is a general statement and not a description of Duisburg.
- What they do support: the Love Parade "shows the typical features of crowd disasters, such as the existence of bottlenecks" and the resulting build-up of people. The ramp and access points were "the main bottlenecks of the system".
- Verdict: Duisburg happened on a **ramp and tunnel entrance-exit bottleneck**, but the authors themselves reject the "people pressing towards a narrow opening" mechanism for it.

**Replacement sentence (recommended):**

> Fatal crowd disasters happen where dense crowds build up in narrow passages and bottlenecks~\cite{helbing2012,liang2024}, and a simulation used to plan such a place is only as trustworthy as the mechanism credited for its bottleneck behaviour.

Optional, sharper version that matches what each paper says:

> Fatal crowd disasters happen where dense crowds build up in bottlenecks, such as the ramp and tunnels of the 2010 Love Parade~\cite{helbing2012} and the narrow, sloping alley of the 2022 Itaewon crush~\cite{liang2024}; a simulation used to plan such a place is only as trustworthy as the mechanism credited for its bottleneck behaviour.

Do not keep "crowd crushes ... press towards a narrow opening" with helbing2012: the paper argues against exactly that reading of its own case. If a "pressing towards an exit" example is wanted, a classic door or exit crush would need a different source, and none is proposed here because none was checked.

---

## Introduction

**gang2026**: "Our earlier work tested such a credit with a surrogate tuned to a mechanism's headline rate". SUPPORTED as a self-citation (content not re-read). Crossref metadata for 10.5220/0015190200004094: title "A Diagnostic Methodology for Failure-Mode Ablation of SFM, TTC, and ORCA Pedestrian Steering Paradigms"; authors Palaash Gang, Arjun Veluri; *Proceedings of the 16th International Conference on Simulation and Modeling Methodologies, Technologies and Applications* (SIMULTECH); SCITEPRESS; 2026; pp. 474–481; no volume. Matches the bib.

**helbing1995, helbing2000nature, karamouzas2014, vandenberg2011**: "SFM driven particles with repulsive and contact forces; TTC reacts to predicted encounters; ORCA small LP over velocity-obstacle constraints". SUPPORTED. Helbing & Molnár give a relaxation term plus repulsive potentials from others and borders. Helbing et al. (2000) add the body force and sliding friction. Karamouzas et al. find an interaction "based ... on their projected time to a potential future collision". Van den Berg et al. reduce the problem to "a low-dimensional linear program".

**beven2006**: "equifinality problem of model calibration". SUPPORTED. Beven: "multiple acceptable models" as representations of environmental systems; "equifinality of models and parameter sets in providing acceptable fits to observational data".

**wolinski2014parameter**: "crowd models pass single-score validation for different reasons". PARTLY. The paper is a framework that calibrates each model to reference data and then compares the scores. Its conclusion is that "the same model can show very different behaviors depending on the parameters", so comparisons must account for parameters. One example comes close to the claim: in a 24-pedestrian case, after calibration, the social-force agents "agglomerate in the center without anticipation" while RVO2 agents anticipate. Nowhere does it say that models pass a single score for different reasons.
Replacement: "...This is the equifinality problem of model calibration~\cite{beven2006}; in crowd simulation the same model behaves very differently under different parameters, and calibrated models can still differ qualitatively in how they avoid collisions~\cite{wolinski2014parameter}."

## Related work: steering models

**helbing1995**: "SFM relaxes each pedestrian towards a desired velocity under exponential repulsion from others and walls". SUPPORTED. The relaxation term is (v0 e − v)/τ. In the simulations "the repulsive potentials were assumed to decrease exponentially" for pedestrians and borders. In general form the paper only requires a monotonic decreasing potential.

**helbing2000nature**: "body compression and sliding friction in contact", and Eq. (sfm) "after Helbing 2000". SUPPORTED. The paper defines A exp[(r_ij−d_ij)/B] repulsion, body force k g(r_ij−d_ij), and sliding friction κ g(r_ij−d_ij) Δv^t_ji t_ij, with g zero when the bodies do not touch. This matches Eq. (sfm).

**karamouzas2014**: "interaction energy falls off as τ^-2". SUPPORTED. "E(τ) ∝ 1/τ²" over the interval where E is well defined, with fitted exponents 2.05 ± 0.12 and 2.02 ± 0.19. The energy saturates below about 0.2 s and is truncated beyond τ0 (about 3 s, 1.4 s in one fit).

**fiorini1998**: "velocity obstacle = set of own velocities that lead to contact within a time horizon". PARTLY (minor). Fiorini & Shiller: "the set of robot velocities that would result in a collision ... at some future time". The finite time window is van den Berg et al.'s VO^τ ("at some moment before time τ", citing Fiorini). Fix: drop "within a time horizon", or put \cite{vandenberg2011} on it: "...that lead to contact at some future time~\cite{fiorini1998}, or, truncated, within a time horizon~\cite{vandenberg2011}".

**vandenberg2011**: "ORCA shares the avoidance, half-plane, 2-D LP, permitted velocity nearest to the preferred one". SUPPORTED. Each robot takes "half of the responsibility". ORCA^τ_A|B is a half-plane. v_new = argmin over ORCA^τ_A of ‖v − v_pref‖, the velocity "closest to its preferred velocity ... amongst all velocities inside the region of permitted velocities", solved by linear programming.

## Related work: clogging at bottlenecks

**zuriguel2014**: "Grains, colloids, sheep and people passing a narrow door alternate between bursts of flow and clogs; the flow is clogged when the mean duration of the stoppages diverges". PARTLY (minor). Supported: the systems studied are sheep at a gate, vibrated silos, colloids and pedestrians; sheep show "an alternation between ... bursts, separated by periods of arrest, or clogs"; and the transition to clogging is identified with "the divergence of the average time lapse" between consecutive passages. Not supported: the pedestrians are only "Simulation of pedestrians evacuating a room using the Social Force Model", not real people.
Replacement: "Grains, colloids, sheep and simulated pedestrians passing a narrow outlet alternate between bursts of flow and clogs; the flow is clogged when the mean time lapse between consecutive passages diverges~\cite{zuriguel2014}."

**nicolas2018trap**: "In granular hoppers the clog is a frictional arch, and unclogging under vibration is escape from traps whose depths follow a distribution". SUPPORTED. Clogs are "arches or vaults"; vibrations are treated like thermal fluctuations, "the rupture of an arch corresponds to the escape from an energy trap"; and "we infer the distribution of trap depths from experiments". The abstract does not stress "frictional", but arches in hoppers are standard and the paper's subject.

**xu2021**: "boundary parameters alone decide whether a velocity-based model clogs". NOT SUPPORTED as worded. The model is velocity-based (GCVM, "a velocity-based model for pedestrian dynamics"), so that part is correct. "Alone" is not: the abstract says prolonged clogs are "closely linked to parameters of the spatial boundaries and the movement model but has virtually no correlation with algorithmic factors". The conclusions also find that model parameter T and agent shape or degrees of freedom change the clog count.
Replacement: "In a velocity-based pedestrian model, prolonged clogs depend on the width and position of the exit and on the model's parameters, but hardly on the update scheme or time step~\cite{xu2021}, ..."

**parisi2005microscopic**: "the SFM forms transient blocking clusters". SUPPORTED. In the SFM, the faster-is-slower effect is explained by "clogging delays" that correlate with "structures that we call 'blocking clusters'". The delays end, so "transient" is fair.

**cornes2021microscopic**: "some attached to the walls". SUPPORTED. In the faster-is-slower regime the relevant structures are "blocking clusters that are somehow attached to the two walls defining the exit".

## Related work: activated escape

**arrhenius1889, kramers1940**: λ = ν exp(−ΔU/k_BT) for a particle in a well kicked by thermal noise. SUPPORTED. This is the standard attribution: Arrhenius gives the exponential temperature law for reaction rates, and Kramers (*Physica* 7, 284–304, 1940; Crossref checked) treats Brownian escape over a barrier. Full texts were not re-read.

**hanggi1990**: "reviewed the theory, including the many-dimensional case, in which the lowest saddle between two minima sets the rate". SUPPORTED. The abstract covers "single- and many-dimensional metastable systems". The multidimensional sections (multidimensional TST; multidimensional Kramers/MFPT) state that the rate integral "is dominated by the saddle point on the separatrix" with "maximal probability density", which is the lowest saddle. The words "lowest saddle" do not appear verbatim.

**e2002, e2007**: "string method finds that saddle by evolving a discretised path until it is everywhere parallel to the force". SUPPORTED. E, Ren & Vanden-Eijnden (2002) define the MEP by (∇V)⊥ = 0, the component of ∇V normal to the curve, and evolve strings to it. The 2007 version uses the full force with reparametrisation and adds the climbing image for the saddle. The 04_protocol.tex use of e2007 (barrier with climbing image) is also SUPPORTED.

**gronbechjensen2013**: "For noise injected into a damped velocity recursion, the stationary variance fixes an effective temperature that depends on the time step". PARTLY. GJ-F's result is the opposite property for their own scheme: it gives "the exact Boltzmann distribution for any value of damping, frequency, and time step" for a harmonic oscillator, and its free-particle results are "independent of the magnitudes of the time step". Δt dependence appears in two places only: for the BBK scheme, "a simulated temperature that differs by O(dt) from the correct one" (cited from another work), and in a Δt-dependent velocity-variance factor (1 − Ω²dt²/4) from the Verlet curvature error. The paper does not treat fixed-size per-step noise of the kind used here.
Replacement: "Discretised Langevin schemes need not sample the bath temperature: the BBK scheme is off by O(Δt), and Grønbech-Jensen and Farago built a scheme whose statistics do not depend on Δt~\cite{gronbechjensen2013}. For the fixed per-step noise used here, the stationary variance gives an effective temperature that depends on the time step (Sect.~\ref{sec:teff}), which we use as a probe."

**woillez2020**: "for self-propelled noise the rate depends on the whole shape of the barrier". SUPPORTED. "The escape rate depends explicitly on the full shape of the potential barrier, and not only on its height". Year: Crossref gives *Phys. Rev. Lett.* 122, 258001, published 28 June 2019. The bib year (2019) is correct; only the key says 2020. Renaming the key is optional.

## Related work: deadlock and mechanism testing

**koren1991**: "Navigation along a potential gradient stalls in local minima of the navigation potential". SUPPORTED. Problem 1 of the four inherent PFM problems is "Trap situations due to local minima (cyclic behavior)", "the best-known and most often-cited problem with PFMs" (full text, archived author PDF). Note that Koren & Borenstein stress cyclic behaviour in traps, not only standstill.

**liu2026orcadeadlock**: "ORCA itself deadlocks in symmetric robot scenes". SUPPORTED. Abstract: "in some scenes, such as where robots distribute symmetrically, ORCA usually fails to plan reasonable collision avoidance velocities, resulting in the robot getting stuck." The authors then simplify ORCA's planning "from the principal horizon" and use deep reinforcement learning to tune the escape velocity and the avoidance responsibility, which lowers deadlock and collision probability against ORCA and learning baselines. Crossref metadata: Liu, Zhihao; Na, Wenjie; Yao, Chenpeng; Liu, Chengju; Chen, Qijun; *Robotica* 44(4), 1212–1230; issue April 2026, online 11 June 2026; Cambridge University Press. Matches the bib.

**grimm2005**: "Pattern-oriented modelling asks a model to reproduce several patterns at different scales, because a single pattern rarely discriminates between mechanisms". SUPPORTED. "A single pattern observed at a specific scale ... is not sufficient to reduce uncertainty in model structure and parameters"; POM uses "multiple patterns ... at different hierarchical levels and scales". The fish-schooling example shows "looking at one pattern may not be sufficient to falsify weak theory".

## Pedestrian model, protocol, statistics

**weidmann1993**: "v_eff follows Weidmann's speed–density relation" with γ = 1.913, ρ_max = 5.4 (Table 1). Attribution SUPPORTED; numbers confirmed only through a secondary source. The ETH Research Collection record (DOI 10.3929/ethz-b-000242008, handle 20.500.11850/242008) blocked automated access with HTTP 403, so the report was not read. Kretz, Lohmiller & Schlaich (arXiv:1512.01426, "The Social Force Model and its Relation to the Kladek Formula") give "Weidmann's parametrization of the Kladek formula" as v_f = 1.34 m/s, γ = 1.913 1/m², ρ_max = 5.4 1/m². This matches Table 1 and v0 mean 1.34 m/s. Before submission, check the table in Weidmann (1993) by hand in a browser.

**koster2013**: "Because results of social force models depend on the integration scheme". SUPPORTED. "The numerical implementation is not without pitfalls. Oscillations, collisions, and instabilities occur even for very small step sizes"; nondifferentiable forces cause "severe loss of accuracy in efficient numerical schemes" (abstract only; the paper is not open access).

**vandenberg2011rvo2**: RVO2 library. SUPPORTED as a software citation. That the solver is a "line-by-line port" is the authors' own statement and was not checked here.

**wilson1927**: Wilson intervals. SUPPORTED (Crossref: *JASA* 22, 209–212, "Probable Inference, the Law of Succession, and Statistical Inference"; the score interval comes from this paper).

**mcnemar1947**: "exact McNemar test". PARTLY (minor). Crossref abstract: "Two formulas are presented for judging the significance of the difference between correlated proportions. The chi square equivalent of one of the developed formulas is pointed out." The exact form, a binomial test on the discordant pairs, is a later convention, though people routinely cite McNemar for it.
Optional wording: "paired outcomes are compared by McNemar's test~\cite{mcnemar1947} in its exact (binomial) form".

**kaplanmeier1958**: Kaplan–Meier estimates of times to free. SUPPORTED (product-limit estimator; *JASA* 53, 457–481).

**weibull1951** (04_protocol.tex): "Kramers theory predicts exponential escape (Weibull shape 1)". SUPPORTED. Weibull introduces the distribution, and shape 1 is the exponential. Crossref: *J. Appl. Mech.* 18(3), 293–297, Sept 1951. Crossref lists the publisher as "Wiley" and the bib copies it, although the journal is published by ASME. The field is harmless but could be changed to ASME.

**kramers1940, hanggi1990** (04_protocol.tex): exponential escape and ln λ linear in 1/k_BT_eff with slope −ΔU. SUPPORTED (see above).

## Discussion

**zuriguel2014, nicolas2018trap**: "Granular and pedestrian clogging is read through arches and clog-lifetime statistics". SUPPORTED (time-lapse and burst statistics in Zuriguel; arches and the clog-lifetime distribution p(τ) in Nicolas).
