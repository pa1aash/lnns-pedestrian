# Source check: Grover et al. (perturbations), noise-for-unjamming clause, PLEdestrians / force-coupled ORCA

Checked 2026-11-10. Sources were read in full text where open (arXiv PDFs, author pages). Quotes are kept short. BibTeX for the recommended entries is now in paper/refs.bib.

---

## (a) Grover, Liu, Sycara: what they say about perturbations

### A1. WAFR 2020 / SPAR 17 (DOI 10.1007/978-3-030-66723-8_18)

- Crossref: "Deadlock Analysis and Resolution for Multi-robot Systems", Algorithmic Foundations of Robotics XIV, SPAR 17, pp. 294-312, 2021. Matches refs.bib `grover2020`.
- arXiv 1911.09146 checked: "Deadlock Analysis and Resolution in Multi-Robot Systems (Extended Version)", v2 dated 13 Jul 2020, same authors. It is the extended preprint of the WAFR paper (the arXiv title says "in", Springer says "for"). I read the arXiv version, not the Springer PDF.
- **What it says about perturbations:**
  - Sec. 1: small perturbations can move the system out of deadlock, but nothing stops it falling back in ("no guarantee robots will not fall back in deadlock").
  - Sec. 2.2: lists earlier work [10,22] that "added perturbation terms to their controllers", then says outright: "We do not consider additive perturbations for resolving deadlocks, since there are no formal guarantees."
  - Sec. 5, after Theorem 3 (the two-robot deadlock set is bounded and has measure zero): random perturbations are called "one feasible way" to resolve deadlock. This is a passing remark and is not followed up.
  - Sec. 7 (Deadlock Resolution) names two drawbacks of the "detect, then perturb" approach: (1) the CBF-QP that caused the deadlock may cause it again; (2) "perturbations can violate safety and even lead to degraded performance".
  - Appendix (the feedback-linearisation derivation): at deadlock the robots sit exactly D_s apart, so "any arbitrary perturbation" could push them into collision.
- **How it resolves deadlock (Sec. 7, Fig. 5, Theorem 6):** a decentralised three-phase switching controller.
  - Phase 1: run the CBF-QP and detect deadlock by thresholding ||u*||, ||v|| and ||p - p_d||.
  - Phase 2: a feedback-linearisation controller rotates the robots about each other while holding their separation at D_s.
  - Phase 3: switch to a PD controller once a feasibility condition holds.
  - Theorem 6 proves convergence to the goals and no relapse into deadlock, for N = 2 (N = 3 described as a trivial extension). Shown in simulation and on Khepera-IV robots.
- **What it characterises:** deadlock is an equilibrium of the closed-loop dynamics. Using KKT conditions it is a "force-equilibrium". The deadlock set is non-empty, lies on the boundary of the safe set, and (for two robots) is bounded and of measure zero. The paper gives no stability or attractivity analysis of these equilibria. The Conclusions list finding the basin of attraction of the deadlock set as future work.
- **Verdict on S1:** the "characterised deadlocks as equilibria" part is supported. "Analysed their stability" is not supported for this paper. "Proposed perturbations to leave them" is wrong: the paper rejects additive perturbations and proposes a guaranteed switching controller. **The referee is correct.**
- **Verdict on S2:** "closed-loop equilibria left by designed perturbations" misdescribes all three papers. None of them designs a perturbation.

### A2. IFAC-PapersOnLine 53(2) 9746-9753, "Why Does Symmetry Cause Deadlocks?" (DOI 10.1016/j.ifacol.2020.12.2644)

- Crossref metadata matches refs.bib `grover2020symmetry`.
- **Limitation of this check:** I could not get the full text. ScienceDirect returns a captcha or 403, and there is no arXiv or repository copy. What follows rests on the abstract (via Semantic Scholar) plus IJRR Sec. 4, which repeats this analysis and cites the IFAC paper for the deadlock definition.
- **Abstract:**
  - It analyses two- and three-robot CBF systems with duality theory.
  - For two robots, heterogeneity (one robot "more vigorous or closer to its goal") "does not help in preventing deadlock".
  - Geometric symmetry from initial positions and goals makes CBFs "generate velocities that render deadlock stable".
  - Last sentence: "conferring skewness to the system can help evade deadlock."
- **Perturbations or noise:** the abstract mentions neither. It proposes no resolution method. It is an analysis paper whose recommendation is to break symmetry (skewness) so deadlock is avoided in the first place.
- **Verdict on the symmetry sentence:** "Symmetric configurations deadlock such robots" is supported. "Added asymmetry helps them escape" goes too far. The abstract says skewness helps *evade* (avoid) deadlock, not escape one already formed, and that heterogeneity in gains or distances alone does not prevent it.

### A3. IJRR 42(6) 317-336, "The Before, During, and After of Multi-robot Deadlock" (DOI 10.1177/02783649221074718; arXiv 2206.01781)

- Crossref metadata matches refs.bib `grover2023` (volume 42, issue 6, pp. 317-336; online 2022). I read arXiv v1 (3 Jun 2022).
- **Before deadlock (Sec. 4):**
  - Closed-loop analysis for two robots that differ in gains and goal distances (Theorem 1) and for three robots on an equilateral triangle (Theorem 2).
  - Symmetry "necessarily results in deadlock", and heterogeneity in controller parameters "is not sufficient".
  - The distance between robots converges to D_s (Lemmas 4 and 8).
  - Sec. 3 states that a demonstration deadlock needed manual intervention to resolve.
- **During deadlock (Sec. 5):** the KKT force equilibrium; the deadlock set is non-empty, on the boundary of the safe set, and of measure zero (Theorems 3-7); graph enumeration of the possible configurations.
- **After deadlock (Sec. 6):**
  - Repeats the WAFR critique of "any small non-zero perturbation", namely that deadlock may relapse and perturbations "can violate safety".
  - Sec. 2 again says: "we do not consider additive perturbations since they lack formal guarantees".
  - Resolution is the three-phase controller: CBF-QP, then feedback-linearisation rotation at fixed separation D_s, then P control. Theorem 8 proves no relapse and convergence; the three-robot case is in the appendix.
- **Perturbations and noise elsewhere:**
  - Sec. 2 cites Wang et al. 2017 and Rodriguez-Seda et al. 2016 for perturbation terms, and Douthwaite et al. for preventing symmetric deadlock "by adding small perturbations".
  - Sec. 7 (Conclusions): "a symmetry breaking controller with some random noise can potentially prevent" deadlock configurations, "However even with randomness, deadlock avoidance cannot be taken for granted." A guaranteed resolution is to let deadlock happen and then correct it reactively.
- **Verdict:** this is the best single source. It covers deadlock as a closed-loop equilibrium, why symmetry leads into it (convergence), the rejection of additive perturbation, and the guaranteed resolving controller.

### Replacement sentences

- **S1:** "For multi-robot systems that avoid collisions with control barrier functions, Grover et al. characterised deadlocks as force-balance equilibria of the closed-loop dynamics, showed that symmetric initial and goal configurations converge to them, and resolved them with a provably correct switching controller rather than additive perturbations [grover2023; grover2020]."
  - Cite: grover2023 (IJRR) as primary; grover2020 (WAFR) as optional second.
  - If you want to keep "stability", use the IFAC wording instead: "symmetry renders deadlock stable [grover2020symmetry]".
- **S2:** "A resolver and its rate-matched surrogate can be probed together at multi-robot deadlocks, closed-loop equilibria that additive perturbations leave without guarantees and that Grover et al. resolve with a dedicated switching controller [grover2023]."
  - Simpler option: "...at multi-robot deadlocks, closed-loop equilibria of the collision-avoidance dynamics [grover2023]."
  - Cite: grover2023.
- **Symmetry sentence:** "Symmetric configurations drive such robots into deadlock, and breaking the symmetry can help them avoid it [grover2020symmetry; grover2023]."
  - Cite: grover2020symmetry (IFAC) as primary, plus grover2023 Sec. 4 because I could read its full text.
  - If "noise" is wanted here, the support is IJRR Sec. 7: random noise "can potentially prevent" deadlock but gives no guarantee.

---

## (c) A source for "per-step noise, used for unjamming since [X]"

### Helbing, Farkas, Vicsek 2000 PRL ("Freezing by heating"; arXiv cond-mat/9904326)

- It does not support "noise used for unjamming". Its point is that noise produces jamming:
  - Raising the noise amplitude θ destroys lanes and leads to "a crystallized state ... by increasing the amount of fluctuations" (abstract).
  - The frozen state is hysteretic and stays when the noise is lowered again.
  - Only "extreme noise amplitudes" melt the crystal into a disordered "gaseous" state.
- Citing it for noise-as-unjamming gets the paper backwards.

### Helbing, Farkas, Vicsek 2000 Nature, "Simulating dynamical features of escape panic" (DOI 10.1038/35035023; arXiv cond-mat/0009448)

- The model has no fluctuation term.
- Clogging at exits comes from arching, with arches that "break" in avalanches. The paper does not attribute arch breaking to noise.
- Randomness appears only as the initial random walking directions in the smoky-room herding scenario, and as random pedestrian diameters.
- The closing paragraph lists "study the effect of fluctuations" as future work.
- **Not relevant** as a source for noise used to unjam.

### Other sources read that do not support the clause

- **Helbing and Molnár 1995 PRE (cond-mat/9805244), Eq. (10):** adds a fluctuation term for ambiguous situations "in which two or more behavioral alternatives are equivalent". This is symmetry breaking in the abstract sense; noise is not used to dissolve jams. The 1995 simulations leave out fluctuations.
- **Helbing and Johansson 2013, "Pedestrian, Crowd, and Evacuation Dynamics" (arXiv 1309.1609):** treats freezing by heating as a "noise-induced blockage effect". It adds that real-crowd deadlocks are not permanent because people turn their shoulders, which is body rotation, not noise.
- **Helbing 2001 Rev. Mod. Phys. (cond-mat/0012229):** noise-induced ordering and freezing by heating; nothing on unjamming.
- **Tordeux, Chraibi, Seyfried 2016 (1512.05597):** adding Brownian noise (σ = 0.1 m/s) breaks lane formation (freezing by heating). This goes the opposite way.

### Verified support found

1. **Xu, Chraibi, Seyfried 2021, Physica A 573, 125934** (DOI 10.1016/j.physa.2021.125934; arXiv 2105.03954; already in refs.bib as `xu2021prolonged`).
   - Introduction: prolonged or stable clogs appear in social-force models when the desired velocity is raised [Helbing et al. 2000 Nature]. Then: "Introducing random behavioral variations is important to mitigate these clogs in simulations".
   - That statement cites Helbing, Buzna, Johansson, Werner 2005 (Transp. Sci. 39:1-24) and Hidalgo, Parisi, Zuriguel 2017 (PRE 95, 042319; already in refs as `hidalgo2017`).
   - Caveat: Xu et al. state this in their review of earlier work; their own model (GCVM) uses no noise. I could not open the two primary papers: INFORMS and APS PDFs are paywalled or return 403, and the repository copies are blocked. The Hidalgo 2017 abstract does not mention noise. So treat Xu et al. as a verified secondary statement, not a primary demonstration.
2. **RVO2 Library (UNC; the reference ORCA implementation)**, `examples/Blocks.cc` line 178, checked on GitHub (snape/RVO2, main).
   - Comment: "Perturb a little to avoid deadlocks due to perfect symmetry."
   - Code: adds a random-angle perturbation of magnitude up to 1e-4 to each agent's preferred velocity at every step.
   - This is per-step noise used directly to break deadlocks in an ORCA crowd simulator. It has no DOI.
   - The ORCA paper itself (van den Berg et al., ISRR 2009 / STAR 70) does not mention perturbation. I read gamma.cs.unc.edu/ORCA/publications/ORCA.pdf; it only mentions possible "global deadlock".
3. **Robotics (CBF) context:** Grover IJRR Sec. 2 says Wang et al. 2017 (T-RO, `wang2017` in refs) and Rodriguez-Seda 2016 add perturbation terms to avoid deadlock. I did not read Wang et al. 2017 for this check.

### Recommendation

There is no verified *origin* source for "used for unjamming since [X]". Drop "since [Helbing2000freezing]" and recast it as current practice, citing the verified sources:

> "...treat per-step noise, which crowd simulators add to break symmetric deadlocks [rvo2library] and which is reported to mitigate clogs in force-based pedestrian models [xu2021prolonged], as having a Δt-dependent temperature; in counter-flow, larger noise can instead freeze the flow [helbing2000freezing]."

Minimal version if only DOI-backed citations are wanted:

> "...treat per-step noise, reported to mitigate clogs in force-based pedestrian simulations [xu2021prolonged], as having a Δt-dependent temperature."

If neither is acceptable, delete the clause: "...treat per-step noise as having a Δt-dependent temperature."

BibTeX (fetched):
- Xu et al. 2021, fetched from doi.org.
- A hand-written `@misc{rvo2library}`, labelled as manual in the file. The author list is taken from the RVO2 README.

---

## (g) PLEdestrians and force-coupled ORCA

### PLEdestrians (Guy, Chhugani, Curtis, Dubey, Lin, Manocha, SCA 2010)

Read in full (gamma.cs.unc.edu/PLE/pubs/PLE.pdf).

- **How it updates velocity:**
  - Sec. 4.1: the permissible velocity set PV_A comes from the ORCA geometric algorithm [vdBGLM09] and is convex.
  - Secs. 3.3 and 4.3: a convex effort function (Eq. 4) is minimised over PV_A. The optimum is either the goal-directed velocity of magnitude sqrt(e_s/e_w) or a point on the boundary of PV_A, found in expected linear time.
  - The result is "a new velocity ... to be undertaken by agent A for this time step".
- **No conversion to force.** The paper has no force term, no relaxation time and no acceleration equation for the agent. "Acceleration" appears only in the related-work survey.
- **Verdict:** PLEdestrians does not support F_orca = m(v_orca - v)/τ_orca. It is a valid citation for "an ORCA-like LP / velocity-space optimisation selects the new velocity", not for turning that velocity into a force.

### Correct sources (verified by reading)

1. **van den Berg, Snape, Guy, Manocha, "Reciprocal collision avoidance with acceleration-velocity obstacles", ICRA 2011, pp. 3475-3482** (DOI 10.1109/ICRA.2011.5980408; gamma.cs.unc.edu/AVO/AVO.pdf).
   - Sec. III-B, Eq. (7): the agent picks a new velocity v'_A from the velocity-obstacle construction and reaches it by proportional control, a_A(t) = (v'_A - v_A(t))/δ, "where δ is a control parameter whose dimension is time".
   - The reciprocal multi-robot version (Sec. IV) reduces each agent's choice to a 2-D linear program, like ORCA.
   - Multiplying by mass gives exactly F = m(v_sel - v)/τ.
   - This is the closest match, written by the ORCA authors. Caveat: the AVO construction builds the relaxation into the forbidden set, whereas plain ORCA followed by relaxation does not. That difference is worth a clause in the paper.
2. **Moussaïd, Helbing, Theraulaz, "How simple rules determine pedestrian behavior and crowd disasters", PNAS 108:6884-6888 (2011)** (DOI 10.1073/pnas.1016507108; arXiv 1105.2152).
   - A velocity chosen by a local heuristic (vision-based search over collision-free directions) is relaxed with τ = 0.5 s: dv/dt = (v_des - v)/τ, plus body contact forces Σf_ij/m in dense crowds.
   - This is the pedestrian-model precedent for "selected velocity → relaxation force + physical forces", though the velocity does not come from ORCA.
- **Read but rejected:** Kim, Guy, Manocha, SCA 2013, "Velocity-based modeling of physical interactions in multi-agent simulations" (DOI 10.1145/2485895.2485910). It goes the other way: physical forces become extra velocity constraints in the ORCA LP (Sec. 3.3, Eqs. 2-3). It does not convert the ORCA velocity into a force.

Suggested citation: "F_orca = m(v_orca - v)/τ_orca, i.e. proportional relaxation toward the LP-selected velocity as in acceleration-velocity obstacles [vandenberg2011avo] and in heuristic pedestrian models [moussaid2011]". BibTeX for both (fetched from doi.org) is in paper/refs.bib (keys vandenberg2011avo, moussaid2011).

### Is the existing PLEdestrians BibTeX correct?

Checked against the EG Digital Library item (DSpace REST metadata for handle 10.2312/SCA.SCA10.119-128), DataCite, and the paper PDF.

- **Correct:**
  - Authors, in this order: Guy, Stephen J.; Chhugani, Jatin; Curtis, Sean; Dubey, Pradeep; Lin, Ming; Manocha, Dinesh.
  - Title: "PLEdestrians: A Least-Effort Approach to Crowd Simulation".
  - Publisher: The Eurographics Association.
  - Year: 2010.
  - DOI: 10.2312/SCA/SCA10/119-128.
- **Pages 119-128:** correct, though the EG DL has no explicit page field. The figure follows from the DOI suffix, the DataCite "original form" URL (`.../SCA10/119-128.pdf`) and the size (10 pages).
- **Problems in refs.bib `guy2010`:**
  - It is an `@misc` with a `journal` field (copied from DataCite content negotiation) and has **no pages field**. It should be an `@inproceedings` with `booktitle` = Eurographics/ACM SIGGRAPH Symposium on Computer Animation and `pages` = 119--128.
  - Optional additions: editors Otaduy, M. and Popović, Z. (from the paper header; the EG DL editor field is garbled as "MZoran Popovic and Miguel Otaduy") and ISBN 978-3-905674-27-9.
- The corrected entry is now in paper/refs.bib.
