# S1 LIT: literature gap scan

Snapshot: `reports/audit/snapshot/main.tex`. Line numbers below are for that file. Scan date: 2026-11-09.
Excluded: everything already in the bibliography (`main.tex` 1188-1352) and the conference paper's reference list.
Every candidate was checked to exist (DOI resolves, or a Crossref/OpenAlex/Semantic Scholar record exists). The BibTeX for each is in `S1_LIT_candidates.bib`, fetched by DOI content negotiation, with a source comment above each entry.

Priority: **A** = a referee will probably ask for it; **B** = strengthens a claim or a section; **C** = optional.

---

## Candidates (15)

### 1. Xu, Chraibi, Seyfried (2021): prolonged clogs in a velocity-based model [A]
Xu, Q., Chraibi, M., Seyfried, A.: Prolonged clogs in bottleneck simulations for pedestrian dynamics. *Physica A* 573, 125934 (2021). https://doi.org/10.1016/j.physa.2021.125934 (arXiv:2105.03954)

- **What it shows:** It defines "prolonged clogs" in bottleneck simulations of a velocity-based (collision-free speed) model. It then varies three groups of factors: the boundary (exit width and position), the algorithm (update scheme and time step) and the model parameters (motivation, interaction strength and range, agent shape). Clogs depend on the boundary and the model parameters and have "virtually no correlation with algorithmic factors".
- **Why a referee expects it:** It is the closest earlier study of the same object: deadlocks at a narrow exit treated as model artefacts, with the same split between geometry, model and numerics. It comes from the FZJ group whose data the paper uses.
- **Where:** Sect. 2, "Clogging at bottlenecks" (l. 845). Sect. 7, "Wall treatment at door edges" (l. 1160). Discussion, "Implications for model users" (l. 1169).
- **Novelty impact:** It does not contradict the paper, but it weakens the framing of the practitioner advice. l. 1169: "the lone trap is a property of the jamb wall law, not of crowding ... a deadlock rate at a narrow door should be read against the stuck-alone margin before it is read as crowd behaviour." Xu et al. already reported that clogs in a pedestrian model are tied to the boundary and the model parameters. **Reword:** "Xu et al. found that prolonged clogs in a velocity-based model depend on the boundary and model parameters rather than on the numerics [xu2021prolonged]; Eq. (stuck) identifies which boundary term sets them in the SFM." Also contrast their time-step result with the paper's: their deterministic clogs show no Δt dependence, which is consistent with class L/D. The Δt signature of the paper (l. 1004-1013) applies to the noise arm only.

### 2. Parisi & Dorso (2005): blocking clusters in the SFM [A]
Parisi, D.R., Dorso, C.O.: Microscopic dynamics of pedestrian evacuation. *Physica A* 354, 606-618 (2005). https://doi.org/10.1016/j.physa.2005.02.040

- **What it shows:** In Helbing's SFM, the faster-is-slower effect comes from the growing probability of clogging delays. These delays correlate with "blocking clusters" of agents in contact at the door. Door size is also discussed.
- **Why a referee expects it:** It is the canonical SFM study of clogging structures at an exit. Sect. 5.3 says that "contact arches never persist", and a referee from pedestrian physics will ask how that relates to the blocking clusters known in the same model.
- **Where:** Sect. 5.3 "No Persistent Contact Arches" (l. 1056); Sect. 2 "Clogging at bottlenecks" (l. 845).
- **Novelty impact:** It weakens l. 835 ("contact arches formed at high drive never persist, because the model has no static friction") only if that claim is read as new. Blocking clusters in the SFM are known to be transient, since delays end. The paper's contribution is the quantitative bound (none lasts 10 s) and the friction argument. **Reword l. 1056:** "Blocking clusters at the exit are known to cause the delays behind faster-is-slower in the SFM [parisi2005microscopic, cornes2021microscopic]; we ask whether any of them persist."

### 3. Cornes, Frank, Dorso (2021): wall-attached blocking clusters [A]
Cornes, F.E., Frank, G.A., Dorso, C.O.: Microscopic dynamics of the evacuation phenomena in the context of the Social Force Model. *Physica A* 568, 125744 (2021). https://doi.org/10.1016/j.physa.2021.125744 (arXiv:2007.06746)

- **What it shows:** For 225 agents in the SFM, the structures that matter in the faster-is-slower regime are "blocking clusters that are somehow attached to the two walls defining the exit". At low desired speed they are very small (fewer than 5 agents). Related work by the same group (Sticco et al., PRE 96, 052303, 2017) shows that very high pressure shortens long delays.
- **Why a referee expects it:** It is the current SFM result on clusters attached to the jambs, which is exactly the configuration in Sects. 5.1 and 5.3. Small clusters at low drive come close to the paper's lone and pair deadlocks.
- **Where:** l. 1056 (arches); l. 1035-1037 (lone trap, the role of the jambs); l. 1172 (discussion of clogging).
- **Novelty impact:** It sharpens rather than contradicts the paper. The paper's novelty is that its persistent deadlocks are **contact-free** rest states. Say this explicitly: "unlike the wall-attached contact clusters of [cornes2021microscopic], the persistent states here have no contacts." No change to "first" wording is needed.

### 4. Garcimartín et al. (2016): human clogs at narrow doors, heavy tails [A]
Garcimartín, A., Parisi, D.R., Pastor, J.M., Martín-Gómez, C., Zuriguel, I.: Flow of pedestrians through narrow doors with different competitiveness. *J. Stat. Mech.* 2016, 043402 (2016). https://doi.org/10.1088/1742-5468/2016/04/043402

- **What it shows:** Evacuation drills through narrow doors at several door widths and levels of competitiveness. Time lapses between consecutive passages are heavy-tailed in all scenarios, and burst sizes are exponential. The results are broadly compatible with faster-is-slower.
- **Why a referee expects it:** It is the standard human-data reference for clog statistics at narrow doors. The paper's validity section uses gaps between passages ("longest gap") without citing the human gap-distribution literature.
- **Where:** Sect. 7, l. 1151 (estimator) and l. 1154 ("Humans flow without deadlock"); Sect. 2, l. 845.
- **Novelty impact:** None. It supports reading longest gaps as a clog statistic. Note that competitive drills do produce long human gaps, so "humans flow without deadlock" (l. 1153) should be limited to the CroMa entrance conditions (motivation levels, 0.8 m).

### 5. Haghani, Sarvi, Shahhoseini (2019): faster-is-slower questioned in human egress (adversarial) [B]
Haghani, M., Sarvi, M., Shahhoseini, Z.: When 'push' does not come to 'shove': Revisiting 'faster is slower' in collective egress of human crowds. *Transp. Res. A* 122, 51-69 (2019). https://doi.org/10.1016/j.tra.2019.02.007

- **What it shows:** Controlled human egress experiments that question whether pushing slows the outflow in the way the SFM predicts. With Haghani & Sarvi, *Phys. Lett. A* 383 (2019), https://doi.org/10.1016/j.physleta.2018.10.029, on how sensitive SFM narrow-exit simulations are to calibration, it is the main critique of SFM clogging at narrow exits.
- **Why a referee expects it:** It is the adversarial counterpart to the clogging literature, and it backs the paper's own conclusion (l. 1157, l. 1177) that the model deadlocks where people do not.
- **Where:** Sect. 7, l. 1157 or l. 1160; Discussion, l. 1169.
- **Novelty impact:** None. It supports the validity result.

### 6. Caitano et al. (2021): a genuine clogging transition under agitation [B]
Caitano, R., Guerrero, B.V., González, R.E.R., Zuriguel, I., Garcimartín, A.: Characterization of the clogging transition in vibrated granular media. *Phys. Rev. Lett.* 127, 148002 (2021). https://doi.org/10.1103/physrevlett.127.148002

- **What it shows:** It shows experimentally that a clogged-to-unclogged transition exists in vibrated hoppers. The transition is continuous at a critical value of a dimensionless velocity, the square root of the ratio of kinetic to potential energy, which works as an effective temperature-to-barrier ratio, for each outlet size.
- **Why a referee expects it:** It is the current reference for the critical outlet size under agitation (topic 5), and it updates Zuriguel et al. 2014 (cited, l. 845). Its control parameter is close to the paper's ΔU/k_BT_eff.
- **Where:** Sect. 2, l. 845 (after zuriguel2014); Sect. 5.4, l. 1067 (the collapse onto ΔU/k_BT_eff).
- **Novelty impact:** Slight. Expressing unclogging in terms of the energy injected relative to a barrier is not new in granular physics. The paper's novelty is computed barriers per snapshot (string method) rather than an energy ratio of the whole system. **Reword l. 1172** to "over barriers computed from the model rather than fitted to it, where granular studies use a global ratio of kinetic to potential energy [caitano2021clogging]".

### 7. Merrigan, Birwa, Tewari, Chakraborty (2018): arch failure as first passage [B]
Merrigan, C., Birwa, S.K., Tewari, S., Chakraborty, B.: Ergodicity breaking dynamics of arch collapse. *Phys. Rev. E* 97, 040901 (2018). https://doi.org/10.1103/physreve.97.040901

- **What it shows:** In 2D hopper simulations, vibrated arches are trapped in locally stable shapes. Failure is a first passage of a continuous-time random walk across a stability boundary, which gives broad unclogging-time distributions. This is an alternative to the trap model.
- **Why a referee expects it:** The paper cites only the trap model (nicolas2018trap, l. 845, l. 1172) as the framework for noise-driven unclogging. A granular referee will want the competing framework, especially because the paper reports exponential (Weibull k≈1) escape times, unlike the broad tails of both granular frameworks.
- **Where:** l. 845 (Sect. 2); l. 1067 (Weibull shape result); l. 1172.
- **Novelty impact:** None. It lets the paper state a contrast: deadlocks in the frictionless SFM give single-barrier exponential escape, while frictional arches give broad tails. A review of both frameworks is Garcimartín et al., EPJ Web Conf. 249, 03009 (2021), https://doi.org/10.1051/epjconf/202124903009.

### 8. Hathcock et al. (2025): a hidden configurational mode sets clog stability [B]
Hathcock, D.J., Dillavou, S., Hanlan, J.M., Durian, D.J., Tu, Y.: Stochastic dynamics of granular hopper flows: A configurational mode controls the stability of clogs. *Phys. Rev. E* 111, L023404 (2025). https://doi.org/10.1103/physreve.111.l023404

- **What it shows:** A Langevin model in which the flow rate, with an absorbing state at zero, couples to a hidden mode that controls clog stability. It reproduces pauses, permanent clogs and non-Gaussian flow statistics in more than 40,000 experimental flows.
- **Why a referee expects it:** It is recent (2025) stochastic-dynamics work on why clogs persist or release. The paper's pair standoff is "softest along the common lateral shift" (l. 835), so stability is also set by one soft mode.
- **Where:** Sect. 2, l. 845; Sect. 5.2, l. 1047-1051 (soft mode and fold).
- **Novelty impact:** None. It is a useful analogy. Do not overclaim: their mode is phenomenological and the paper's is a Hessian eigenvector.

### 9. Woillez et al. (2019): activated escape out of equilibrium [A]
Woillez, E., Zhao, Y., Kafri, Y., Lecomte, V., Tailleur, J.: Activated escape of a self-propelled particle from a metastable state. *Phys. Rev. Lett.* 122, 258001 (2019). https://doi.org/10.1103/physrevlett.122.258001

- **What it shows:** For active (self-propelled) particles, the escape rate depends on the whole shape of the barrier, not only its height. A particle can escape over the higher of two barriers.
- **Why a referee expects it:** Pedestrians are driven, dissipative agents. A statistical-physics referee will ask why an equilibrium Arrhenius law with a single ΔU applies. The paper's justification is that the rest field is a gradient, −∇U, with small residuals (l. 1001, l. 1049), but this is never set against the active-matter caveat.
- **Where:** Sect. 2 "Activated escape" (l. 848); Sect. 4.3 (Collective Activated Escape); Sect. 5.4, l. 1067, and the failed snapshot (the paragraph after l. 1067, where "the computed minimum-energy path is then not the route the dynamics takes").
- **Novelty impact:** It weakens nothing if the paper adds one sentence: "Because the rest field is a gradient to within N and the noise enters as additive white noise on the velocity, the equilibrium Kramers form applies; for self-propelled noise the rate depends on the whole barrier shape [woillez2019activated]." It also offers an explanation for the snapshot that never escapes.

### 10. Helbing, Farkas, Vicsek (2000): freezing by heating [A]
Helbing, D., Farkas, I.J., Vicsek, T.: Freezing by heating in a driven mesoscopic system. *Phys. Rev. Lett.* 84, 1240 (2000). https://doi.org/10.1103/physrevlett.84.1240

- **What it shows:** In a driven particle (pedestrian-type) model, stronger random forces can produce a jammed, "crystallized" state from a fluid one.
- **Why a referee expects it:** It is the canonical result that noise in a social-force-type model can create jams as well as remove them. The paper argues that "noise is not a neutral way to unstick a model" (l. 1169) and does not cite it. It predates 2005 but is standard.
- **Where:** Discussion l. 1169 (third point); Sect. 3 "Integration and noise" (l. 922-923); Intro or Sect. 2 when noise is first introduced.
- **Novelty impact:** It slightly weakens the implied originality of "noise is not neutral". The paper's specific point, the 1/Δt dependence of T_eff, remains its own. **Reword:** "Noise is known to change the collective state of driven pedestrian models [helbing2000freezing]; here it also changes with the time step."

### 11. Grover, Liu, Sycara (2020): symmetry causes deadlocks [A]
Grover, J.S., Liu, C., Sycara, K.: Why does symmetry cause deadlocks? *IFAC-PapersOnLine* 53(2), 9746-9753 (2020). https://doi.org/10.1016/j.ifacol.2020.12.2644

- **What it shows:** For two- and three-robot CBF systems, duality analysis shows that symmetric configurations lead to deadlock, that heterogeneity alone does not prevent it, and that "conferring skewness" (asymmetry) helps avoid it. The journal extension (Grover, Liu, Sycara, *IJRR* 42, 2023, https://doi.org/10.1177/02783649221074718) states that symmetry always leads to deadlock.
- **Why a referee expects it:** The paper cites grover2020 (the WAFR chapter), but the IFAC paper is the one about symmetry. The paper's second deadlock class is a *symmetric* pair standoff broken by a lateral bias (an asymmetry), which is the same structure.
- **Where:** Sect. 2 "Deadlock in multi-agent systems" (l. 851); Sect. 5.2 (l. 1047-1051); Discussion l. 1172.
- **Novelty impact:** It weakens the implied novelty of breaking a symmetric standoff with a lateral bias (l. 835: "a symmetric pair standoff ... which a lateral bias breaks at a fold"). What is new is the fold analysis (λ₁ → 0, b*) in an SFM energy landscape, not that asymmetry breaks symmetric deadlock. **Reword l. 851:** "Grover et al. showed that symmetric configurations deadlock CBF-controlled robots and that added asymmetry helps them escape [grover2020symmetry]; the pair standoff below is the pedestrian analogue, and we locate the fold at which a bias removes it."

### 12. Liu et al. (2026): ORCA deadlock in symmetric scenes [B]
Liu, Z., Na, W., Yao, C., Liu, C., Chen, Q.: Addressing the deadlock problem of the optimal reciprocal collision avoidance algorithm in distributed multi-robot navigation. *Robotica* 44(4) (2026). https://doi.org/10.1017/s026357472610349x

- **What it shows:** ORCA "usually fails to plan reasonable collision avoidance velocities" when robots are placed symmetrically, so they get stuck. The authors simplify ORCA's planning and learn an escape velocity and responsibility split by deep RL. An earlier version is Liu et al., *IEEE RA-L* 2024, https://doi.org/10.1109/lra.2024.3390561.
- **Why a referee expects it:** It is current evidence that ORCA *causes* symmetric deadlocks in robotics. The paper finds that ORCA *frees* symmetric pair standoffs through its constraint part, differently in each solver (l. 1133). A robotics referee will notice the apparent tension.
- **Where:** Sect. 2, l. 851; Sect. 6.2, l. 1133 (solver dependence).
- **Novelty impact:** None directly. The paper should say why ORCA frees symmetric standoffs here: it is embedded as a force on top of an SFM with a goal drive, not used as the sole planner. In the same space, ORCA livelocks in crowd simulation are documented by Echeverri et al. (*IEEE T-ITS* 2024, https://doi.org/10.1109/tits.2024.3376077), and ORCA deadlocks in narrow passages have been handled by switching to path finding (Dergachev & Yakovlev, CASE 2021, https://doi.org/10.1109/case49439.2021.9551564).

### 13. Adrian, Seyfried, Sieben (2020): the entrance experiments behind the CroMa data [A]
Adrian, J., Seyfried, A., Sieben, A.: Crowds in front of bottlenecks at entrances from the perspective of physics and social psychology. *J. R. Soc. Interface* 17, 20190871 (2020). https://doi.org/10.1098/rsif.2019.0871

- **What it shows:** It analyses the FZJ entrance (bottleneck) experiments with corridor width, motivation and queuing-norm priming as factors. Density in front of the entrance rises with motivation and with corridor width.
- **Why a referee expects it:** The paper uses the CroMa/FZJ data (l. 1151, cited only as the data DOI, fzj_ped20219) without citing the peer-reviewed analysis of the experiment. A referee will expect the experimental design, the motivation levels and the corridor-width effect to be cited. The corridor-width effect bears on the paper's 2.0 m vs 0.21 m corridor variants.
- **Where:** Sect. 7, l. 1151 (with fzj_ped20219); Sect. 3, l. 926.
- **Novelty impact:** None. Be careful that the "short corridor" description matches theirs.

### 14. Rzezonka et al. (2022): a physics model run against the same entrance experiments [A]
Rzezonka, J., Chraibi, M., Seyfried, A., Hein, B., Schadschneider, A.: An attempt to distinguish physical and socio-psychological influences on pedestrian bottleneck. *R. Soc. Open Sci.* 9, 211822 (2022). https://doi.org/10.1098/rsos.211822

- **What it shows:** It tests whether a physics-based model can reproduce the corridor-width dependence of density observed in the FZJ entrance experiments, and so whether socio-psychological explanations are needed.
- **Why a referee expects it:** It is the existing model-against-data comparison on these experiments. The paper's validity section (l. 1151-1157) compares a model with the same experiments without mentioning it.
- **Where:** Sect. 7, l. 1151 or l. 1157.
- **Novelty impact:** It weakens the unqualified "like-for-like comparison with human bottleneck data" if read as a field-level first. As written (l. 1179, "New in this version ... a like-for-like comparison"), it is new relative to the conference paper only, which is safe. Add: "Rzezonka et al. compared a physics-based model with the same experiments on density [rzezonka2022attempt]; we compare flow and passage gaps under matched agent numbers and corridor lengths." Also see Üsten, Sieben, Chraibi, Seyfried, "A well-motivated model of pedestrian dynamics", arXiv:2604.26858 (2026), a motivation model tested on pre-bottleneck waiting. It is a preprint, so cite with care.

### 15. Beven (2006): equifinality [A]
Beven, K.: A manifesto for the equifinality thesis. *J. Hydrol.* 320, 18-36 (2006). https://doi.org/10.1016/j.jhydrol.2005.07.007

- **What it shows:** Many model structures and parameter sets reproduce the same observations equally well (equifinality), so fit to a target does not identify the process.
- **Why a referee expects it:** The paper's central thesis (l. 832, l. 1177: "A control matched to a paradigm's completion rate shows that a simpler cause would suffice, not that the paradigm uses it") is equifinality applied to a matched control. A methodology referee will ask for the term and the canonical reference. In crowd simulation, Wolinski et al. (*Comput. Graph. Forum* 33, 2014, https://doi.org/10.1111/cgf.12328) calibrate several steering models, ORCA among them, to the same data. That is a direct precedent for "different models, same score".
- **Where:** Sect. 2 "Testing mechanisms in models" (l. 854); Intro l. 830-832; Conclusions l. 1177.
- **Novelty impact:** It weakens the framing of the thesis as a new insight (l. 832, "Our thesis is that matching a control ... is not evidence of a shared mechanism"). The *principle* is known as equifinality. What is new is the protocol: physics-derived interventional probes on frozen states. **Reword l. 832:** "That matching a headline score does not identify a mechanism is the equifinality problem [beven2006manifesto]; our contribution is a test that resolves it for deadlock resolvers: signatures derived from the model's physics, measured on the same frozen deadlock states." l. 854 ("We have not found an earlier study that tests a matched control in this way") then stays safe, because of the qualifier "in this way".

---

## Also considered (verified, lower priority; BibTeX for the first six is in the .bib)

- Grover, Liu, Sycara, *IJRR* 2023, https://doi.org/10.1177/02783649221074718: journal extension of no. 11.
- Echeverri, Auberlet, Hubert, *IEEE T-ITS* 2024, https://doi.org/10.1109/tits.2024.3376077: ORCA livelocks in crowd simulation.
- Pastor et al., *PRE* 92, 062817 (2015), https://doi.org/10.1103/physreve.92.062817: experimental faster-is-slower.
- Garcimartín et al., *Sci. Rep.* 7, 10792 (2017), https://doi.org/10.1038/s41598-017-11197-x: velocity fluctuations ("kinetic stress") of pedestrians relative to neighbours in competitive egress. A likely source to cite for the waiting-zone fluctuation estimator at l. 1151, which currently cites nothing.
- Grønbech-Jensen & Farago, *Mol. Phys.* 111 (2013), https://doi.org/10.1080/00268976.2012.760055: how discretised Langevin integrators reproduce the kinetic temperature as a function of Δt. Context for Eq. (teff), l. 1004-1007.
- Wolinski et al., *Comput. Graph. Forum* 33 (2014), https://doi.org/10.1111/cgf.12328: see no. 15.
- Chraibi et al., *PRE* 92, 042809 (2015), https://doi.org/10.1103/physreve.92.042809: unrealistic behaviour (backward motion, overlaps) intrinsic to force-based models.
- Nicolas, Bouzat, Kuperman, *Transp. Res. B* 99 (2017), https://doi.org/10.1016/j.trb.2017.01.008: pedestrian model at a narrow doorway; effect of individual behaviour on clogs.
- Hidalgo, Parisi, Zuriguel, *PRE* 95, 042319 (2017), https://doi.org/10.1103/physreve.95.042319: competitive egress of non-circular agents.
- Parisi, Cruz Hidalgo, Zuriguel, *Sci. Rep.* 8 (2018), https://doi.org/10.1038/s41598-018-27478-y: active particles with desired orientation through a bottleneck.
- Hernández-Delfín, García, Ellero, *Commun. Phys.* 7 (2024), https://doi.org/10.1038/s42005-024-01646-1: SFM egress rheology; faster-is-slower linked to frictional clogging.
- Corbetta & Toschi, *Annu. Rev. Condens. Matter Phys.* (2023), https://doi.org/10.1146/annurev-conmatphys-031620-100450: review, physics of human crowds.
- Grimm & Railsback, *Phil. Trans. R. Soc. B* (2012), https://doi.org/10.1098/rstb.2011.0180: updates grimm2005.
- Marshall & Galea, *Am. J. Epidemiol.* (2015), https://doi.org/10.1093/aje/kwu274: agent-based models in causal inference.

Searched for and **not found** (supports the paper's novelty): any use of the string method, NEB or minimum-action methods to compute barriers in a pedestrian or crowd model, and any study that confronts a rate-matched control with a resolver on frozen deadlock states using interventional probes.

---

## Novelty verdict

| # | Claim (main.tex line, quoted) | Verdict | Action |
|---|---|---|---|
| 1 | l. 832: "Our thesis is that matching a control to a paradigm's headline completion rate is not evidence of a shared mechanism" | **Needs hedging** | The principle is equifinality (Beven 2006; Wolinski et al. 2014 for crowd models). Present the protocol, not the principle, as the contribution (wording under no. 15). |
| 2 | l. 834: "A calibrate-then-falsify protocol: a resolution claim is assigned to one of five physically defined mechanism classes ... and a rest-state lemma ..." | **Safe** | No precedent found. |
| 3 | l. 854: "We have not found an earlier study that tests a matched control in this way." | **Safe** (already hedged) | Add equifinality and pattern-oriented modelling as precedents for the premise before this sentence. |
| 4 | l. 835: "a lone-agent trap set by the wall force at the door edges, with a stuck-alone criterion ..." | **Safe**, needs context | Cite Xu et al. 2021 (boundary parameters control clogs) and Cornes et al. 2021 (wall-attached clusters). The criterion itself is new. |
| 5 | l. 835: "a symmetric pair standoff, a strict minimum of the rest-state energy ... which a lateral bias breaks at a fold" | **Needs hedging** | That symmetry causes deadlock and asymmetry relieves it is known in multi-robot control (Grover et al. 2020 IFAC; IJRR 2023; Liu et al. 2026 for ORCA). Claim the fold analysis, not symmetry breaking (wording under no. 11). |
| 6 | l. 835 / l. 1056: "contact arches formed at high drive never persist, because the model has no static friction" | **Needs hedging** | Transient blocking clusters in the SFM are known (Parisi & Dorso 2005; Cornes et al. 2021). Claim the quantitative bound and the friction argument (wording under no. 2). |
| 7 | l. 835 / l. 1179: "Velocity noise frees the lone trap by collective activated escape over barriers computed from the model's own energy landscape" | **Safe** | No crowd or pedestrian study using string-method barriers was found. Add the active-matter caveat (Woillez et al. 2019) and the gradient-field justification. |
| 8 | l. 1179: "the exact effective temperature of per-step noise" | **Needs hedging** | Eq. (teff) is the stationary variance of an AR(1) recursion, a standard result, and the Δt dependence of discretised-Langevin temperature is known (Grønbech-Jensen & Farago 2013). Suggested: "the effective temperature of per-step noise, which follows exactly from the stationary variance of the damped velocity recursion". The novelty is its use as a Δt signature (Eq. ell). |
| 9 | l. 836: "At the lone trap ORCA acts as an added goal drive, deterministic and independent of the time step" | **Safe** | Not found elsewhere. Liu et al. 2026 concerns ORCA as a planner; contrast with it. |
| 10 | l. 837 / l. 1179: "a like-for-like comparison with human bottleneck data at 0.8 m" | **Safe as worded** ("new in this version") | Not a field first: Rzezonka et al. 2022 compared a model with the same FZJ entrance experiments. Cite it and Adrian et al. 2020. |
| 11 | l. 1169: "the lone trap is a property of the jamb wall law, not of crowding" | **Safe**, needs context | Close to Xu et al. 2021 (clogs depend on boundary and model parameters). Cite it as precedent. |
| 12 | l. 1169: "noise is not a neutral way to unstick a model: its temperature depends on the time step" | **Needs hedging** (first half) | That noise is not neutral is known (Helbing, Farkas, Vicsek 2000, freezing by heating). The Δt dependence is specific to the paper. |
| 13 | l. 1179: "The title, abstract, conclusions, figures and tables are new ... New in this version are ..." | **Safe** | Claims relative to the conference paper only. |

**Contradicted:** none. No candidate found makes any claim in the paper false. Six claims (1, 5, 6, 8, 12, and the context of 4/11) need a citation and a narrower wording.

---

## Search queries run

Academic APIs (Crossref bibliographic, OpenAlex with `from_publication_date:2017-01-01`, Semantic Scholar (partly rate-limited), arXiv export API):

- deadlock social force model bottleneck pedestrian
- deadlock pedestrian bottleneck simulation social force
- ORCA reciprocal collision avoidance deadlock narrow passage
- ORCA deadlock pedestrian crowd simulation
- reciprocal velocity obstacle deadlock symmetry breaking perturbation
- arXiv: all:ORCA AND all:deadlock
- multi-robot deadlock resolution symmetry
- arXiv: au:Grover AND au:Sycara
- pedestrian simulation noise unclogging bottleneck
- clogging pedestrian simulation noise fluctuations
- noise social force model pedestrian fluctuation term
- effective temperature pedestrian crowd model noise
- freezing by heating pedestrian noise jamming
- clogging noise self-propelled particles bottleneck temperature
- clogging active particles bottleneck
- Kramers escape active matter clogging
- activated escape clogging arch Kramers
- string method minimum energy path clogging
- string method active particles barrier escape
- nudged elastic band granular arch energy barrier
- nudged elastic band self-propelled particles energy landscape
- clogging probability Arrhenius granular temperature vibration
- unclogging vibration granular silo
- silo clogging review bottleneck many-particle
- clog lifetime distribution heavy tail pedestrian experiments
- critical door width clogging transition pedestrian model
- door width clogging transition pedestrian
- faster-is-slower clogging pedestrians review
- blocking clusters arches social force model evacuation
- arXiv: au:Dorso AND ti:friction; au:Cornes AND au:Dorso
- validation pedestrian model bottleneck experiment Jülich
- crowd simulation model validation bottleneck experiment
- bottleneck experiments motivation entrance crowd simulation comparison
- motivation model bottleneck simulation entrance JuPedSim
- collision-free speed model bottleneck validation experiments
- velocity obstacle pedestrian bottleneck simulation clogging
- mechanism agent-based model causal inference intervention
- plus Crossref title look-ups for about 45 specific candidate titles (all DOIs above confirmed)

Web search:

- ORCA reciprocal collision avoidance deadlock narrow doorway symmetric agents perturbation remedy
- noise matched control mechanism attribution agent-based pedestrian model deadlock bottleneck
- (adversarial) criticism social force model unrealistic clogging narrow door simulation artefact wall force
- RORCAL ORCA deadlock rotational symmetry directional bias arXiv (no verifiable record; excluded)
- "Why Does Symmetry Cause Deadlocks" Grover Liu Sycara IFAC 2020 abstract control barrier functions
