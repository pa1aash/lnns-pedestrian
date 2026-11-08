# Referee 1 report

**Manuscript:** "One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models" (P. Gang, A. Veluri), invited LNNS extension of the SIMULTECH 2026 paper.
**Version reviewed:** snapshot at commit decbdca (`main.tex`, 1353 lines; `main.pdf`, 23 pages). Line numbers below refer to `main.tex`.
**Referee background:** clogging and arching in granular and pedestrian bottleneck flow, activated escape (Kramers/Arrhenius), and fluctuation-driven dynamics.

I treated Table 4, Sect. 6.3 (l. 1139-1143), the Zenodo DOI and the acknowledgements (l. 1182-1184) as known gaps, not defects.

---

## 1. Summary (five sentences)

The authors argue that tuning a control to match a steering paradigm's completion rate (the protocol of their conference paper) says nothing about mechanism. They propose instead to classify each resolver by how frozen deadlock states respond to a set of physically motivated probes (replay, time step, sign of a push, reversing a tilt). In a social force model at a 0.8 m door they identify two deadlock types: a lone agent held back by the exponential wall force of the two sharp door edges (a "stuck-alone" force balance), and, when the jamb wall range is shortened, a non-contact symmetric pair standoff that a lateral bias removes. They show that at the lone trap ORCA acts as a constant extra goal drive, while velocity noise frees deadlocks stochastically, at a time-step-dependent rate consistent with an Arrhenius law at an effective temperature computed from the discrete velocity recursion, over barriers obtained by the string method. A like-for-like rebuild of a CroMa bottleneck experiment shows that no model variant reproduces human flow, gaps or waiting-zone fluctuations. The contribution can be stated crisply, but it is really two papers: a methodological thesis whose falsification step is largely guaranteed by how the controls are chosen, and a good deal of genuine model physics (wall-edge trap, pair fold, noise escape) whose statistical-physics claims go further than the evidence allows.

## 2. Scores (1 = poor, 5 = excellent)

- Originality: 3. The probe-based classification is new for pedestrian models. The physics ingredients (effective soft-core size against door width, noise as a temperature in the SFM, Arrhenius escape) are known in other forms and the paper does not acknowledge them.
- Significance: 2. Deadlocks occur at densities of at most 0.35 ped/m² (l. 895) with the last two or three agents left. They are an end-of-evacuation artefact of one wall law and are not the clogging seen in dense crowds. The CroMa section shows the model is not valid at this width.
- Soundness: 2. The core numbers are reproducible from `data/derived/*.json`, but several physics claims rest on assumptions the paper does not state or check (uniform temperature, the Kramers regime, the fold normal form, numerical resolution of the arch runs). Several "tests" also hold by construction.
- Clarity: 3. The prose is dense but precise. Too many results are packed into single sentences (e.g. l. 1035, 1120, 1123), and the matched-control logic is easy to misread.
- Presentation: 3. The figures are clean and consistent. Two table captions break the two-sentence rule. The bibliography has formatting faults.
- Venue relevance: 4. Simulation methodology and model attribution suit LNNS/SIMULTECH.

**Recommendation: major revision.**

---

## 3. Major issues

### M1. The falsification step largely holds by construction; the informative test (outcome-set identity) has no noise-vs-noise baseline
*Where:* Sect. 4 "Calibrate, then falsify" (l. 1019-1020); Sect. 6.1 "Matched noise acts differently" (l. 1113-1114); "Matched completion of whole runs" (l. 1122-1123); Table 3 (l. 1086-1109); Discussion (l. 1162-1163).

*Problem.* The protocol requires the control to come from "a different class" (l. 1020). It then counts a disagreement on a class-defining probe as falsification. A stochastic control always differs from a deterministic resolver in replay and in Δt dependence, and a fixed-handedness tilt always has a handedness. So "each control fails a probe of its own class" (l. 1163) is a restatement of how the controls were chosen, not an empirical finding. The same holds for "noise failures never come to rest" (l. 1123): with σ > 0 no agent can be at rest. The only probe that carries information is identity, i.e. which deadlocks each resolver leaves unresolved. That evidence is thin:
- Lone trap (Table 3, row 1): J = 0.20 [0.00, 0.50] is computed from an ORCA-unresolved set of 4 snapshots and a noise-majority-unresolved set of 2, with 1 shared (`E2_analysis.json`, `f_noise_vs_C3/lone_keystone/noise0p07`). That is effectively no evidence either way.
- Whole runs: J = 0.41 against 0.30 for independent sets. `E6_analysis.json` gives a permutation p = 0.0023 for "above independent", so the failure sets overlap *significantly more* than chance. The text (l. 1123, "overlap barely more than independent ones would") understates this.
- In neither case do we know the overlap of noise with *itself*. Noise outcomes are random per seed: seeds disagree on 9 of 34 lone keystones (Table 3). Two independent noise realisations on the same spawns may well overlap at J ≈ 0.4 or less. If so, J(ORCA, noise) is indistinguishable from J(noise, noise), and the "different deadlocks" claim fails.

*Why it matters.* This is the thesis of the paper (title, l. 832, l. 1163, l. 1177).

*Fix.*
1. Recast the protocol. The class-defining probes *assign* a class; they are not falsification evidence. Falsification needs a control from the *same* candidate class. The paper already has one: the frozen-mean push (class L) agrees with ORCA on every probe at the lone keystone (30/34 and 31/34, discordant 0:0; l. 1111). Present this as the case where the protocol *confirms*, which makes the protocol two-sided.
2. Add noise-vs-noise identity baselines. Run A: lone keystones, C1 + σ = 0.07 m/s, 5 new seeds per snapshot (34 × 5 = 170 quenches of ≤ 120 s with few agents). Report J between the two noise majority-sets and its bootstrap 95% interval. Run B: whole runs, the 186 E6 spawns, C1 + σ* with an independent noise seed stream, 600 s. Report J(noise, noise′), the 2×2 table and its McNemar p. Cost: Run A ≈ 0.5-1 CPU-h; Run B 186 × 30-90 s ≈ 1.5-4.7 CPU-h; together ≈ 1.5 h wall on 4 cores.
3. Replace J for the lone trap with a physics-based identity test that has power: does noise's per-snapshot failure probability rank with the collective barrier ΔU (BAR library, 60 snapshots), while ORCA's failures rank with the C3 rest-state margin (AUC 0.98, l. 1111)? Two different predictors of failure would be real evidence of two mechanisms. This needs no new runs.

### M2. The effective temperature: per-agent temperatures differ, and the equilibrium (detailed-balance) assumption is unstated
*Where:* Sect. 4.2, Eq. (9) (l. 1003-1008); Sect. 5.4 (l. 1065-1067); Table 1, τ ~ U(0.4, 0.6) s (l. 862); l. 848 ("follows exactly").

*Problem.*
- Eq. (9) gives each agent its own temperature, k_BT_i = m σ² τ_i/(2Δt)(1 − Δt/2τ_i)^{-1}. σ is common to all agents and τ_i ranges from 0.4 to 0.6 s, so the temperatures within one snapshot differ by up to a factor 1.5. E4 sets σ "with the blocker's τ" (l. 1065). In the "full" condition, where neighbours move along the escape path (the paper's main claim, l. 1067), the system therefore has several temperatures at once and is not in equilibrium. The Boltzmann weight exp(−U/k_BT) and the Kramers/Langer rate are not defined for a single T. This could explain a pattern visible in `E4_analysis.json`: the slope ratio (fitted slope / −ΔU) is above 1 in 6 of 8 full fits (median 1.15) but below 1 in 9 of 10 alone fits (median 0.87; sign test p ≈ 0.02). Both deviations are systematic, not scatter.
- Even with equal τ, calling the noise amplitude a temperature requires (i) a conservative rest field, which the paper shows for frozen densities (l. 997-1001), and (ii) a fluctuation-dissipation relation for *every* dissipative channel. The contact friction κ and the wall friction (Eqs. 3-4) dissipate but receive no matching noise, and the speed cap Π is a non-linear clip. Away from contact this is harmless. Along a collective escape path where neighbours are pushed together it is not. The paper should state these conditions explicitly, as the assumptions of detailed balance, rather than say the temperature "follows exactly" (l. 848).
- The variance check (ratio 1.00, l. 1008) tests only the blocker's equipartition near the minimum. It does not test the stationary distribution along the path, or for the neighbours.

*Why it matters.* "Noise is thermal at the temperature of Eq. (9)" (l. 1117) and "collective activated escape" (l. 835, 1067) both depend on this.

*Fix.*
1. State the assumptions: frozen densities, conservative F₀, linear friction m/τ_i, no contact, no clipping, and equal temperatures.
2. Rerun the E4 full condition at equal temperatures, σ_i = σ_ref (τ_ref/τ_i)^{1/2}, so that every agent has the same k_BT_eff. Configuration: the 8 usable full-condition snapshots plus seed170; β ∈ {1.5, 2.5, 3.5}; 20 restarts per level; censoring at 300/900 s as now. Outputs: slope ratio with 95% interval, Weibull k, ν. Cost: 9 × 3 × 20 = 540 short runs with 3-7 agents, ≤ 2 CPU-h.
3. Report the neighbours' measured velocity variance against Eq. (9) with their own τ_i, alongside the blocker's.

### M3. Kramers/Arrhenius is used outside its regime; the Weibull test fails as stated; one snapshot that contradicts the theory was removed from the fits
*Where:* Sect. 5.4 (l. 1065-1069), Fig. 4 (l. 1059-1064), Sect. 6.1 "The time-step signature" (l. 1116-1117), Fig. 5, l. 1123 (E6 stalls).

*Problem.*
- **Barrier/noise ratio.** The tested range ΔU/k_BT = 1.5-3.5 (E4), with β_ref 1.5 and 2.5 at Δt = 0.01 s (E3), lies largely outside the asymptotic Kramers regime (ΔU/k_BT ≳ 5). At β ≈ 1-2 the prefactor depends on T and the escape time is not separated from relaxation times. The E3 miss at β_ref = 2.5 (ℓ = 3.23 [2.96, 3.52] against 3.70 predicted, l. 1117) sits exactly where Δt = 0.005 s halves β to about 1.25. Fig. 5 shows the observed rate at Δt = 0.005 s well below the prediction. The authors' own batch report (B4A_REPORT.md, item 1) attributes this to "the low-barrier prefactor at β_eff ≈ 1.25". The paper should say so. In whole runs (l. 1123), `E6_analysis.json` gives a median β of 1.43 at σ*, where "activated" escape is barely distinguishable from diffusive crossing.
- **Weibull.** The pooled shape is 1.09 [1.05, 1.14] (l. 1067), and the frozen condition gives 1.135 [1.064, 1.209] (`E4_analysis.json`). Both intervals *exclude* 1, so "close to the exponential value 1" contradicts the stated prediction "Weibull shape k = 1" (l. 1017). Pooling heterogeneous exponentials should push k *below* 1. k > 1 points to an induction time: equilibration from a T = 0 snapshot (slow mode 1/λ₁), and transit after the saddle.
- **Prefactor.** ν is fitted (0.13, 0.21 and 0.09 s⁻¹ for full, frozen, alone; the frozen value is omitted at l. 1067), never predicted. A no-free-parameter Kramers-Langer prefactor can be built from quantities the authors already have: the Hessian at the minimum and at the climbing image, and the friction γ_i = 1/τ_i. For the T3 snapshot (`T3_variance.json`, E1b_seed80) the minimum eigenvalues are 554 and 1869 N/m. With m = 80 kg and γ ≈ 1.9 s⁻¹ a rough estimate gives ω/2π ≈ 0.4 s⁻¹ and a 1-D moderate-damping transmission factor ≈ 0.7. That is ν of order 0.3 s⁻¹ (check), several times the fitted alone value of 0.09 s⁻¹. Either the Langer prefactor agrees, which would be a strong result, or the discrepancy needs explaining.
- **Excluded counter-example.** E1b_seed170 (l. 1069) has a gated full barrier of 0.13 J. At β = 1.5 with ν ≈ 0.13 s⁻¹ one expects a mean escape time of about 35 s, yet 0 of 60 restarts escape within 300 s. This snapshot falsifies the claim that the string-method barrier controls the rate, and excluding it after the fact is not acceptable. Seed60 is also dropped from the full condition (barrier 0.02 J). So the full-condition evidence is 8 fits, of which 7 cover 1, plus one unexplained failure.
- **Interval width.** The ratio intervals are wide, typically [0.6, 1.3] (`E4_analysis.json`), so "covers 1 in 9 of 10" would also accept barriers wrong by 30%.

*Fix.*
1. Report seed170 among the results as a failure of the minimum-energy-path picture and investigate it: compare the frozen barrier of 18.3 J with the full barrier of 0.13 J, and look for a lower-barrier state along the path that is not an exit, or a path through a non-gradient region.
2. Fit a shifted exponential (or drop the first t₀ ≈ 3/λ₁ s) and report per-condition k with intervals.
3. Compute the Langer prefactor from the Hessians (static, minutes of CPU) and compare it with ν.
4. Add a higher-β arm. Configuration: E3 at β_ref = 3.5 on the same 20 snapshots, Δt ∈ {0.005, 0.01, 0.02}, 20 restarts, censoring at 900 s. Cost ≈ 3-5 CPU-h; the authors' own report proposes this.
5. Rephrase the claims as in Sect. 6 of this report.

### M4. "Collective" escape: the full-versus-alone comparison is confounded, and the full-versus-frozen comparison holds by construction
*Where:* l. 1017 (prediction), l. 1067 ("The escape is collective ... because the neighbours give way along the path").

*Problem.* The "alone" condition *removes* the neighbours. Its barrier is higher mainly because nobody pushes the blocker from behind, not because neighbours "give way". The barrier with neighbours pinned ("frozen") is a constrained minimum-energy path inside the configuration space of the "full" problem, with the same minimum, so full ≤ frozen holds variationally. Neither comparison is a test of collective motion. The data also show the confound directly: frozen > alone in 2 of 10 snapshots (seed60: 51.4 J against 7.7 J; seed237: 88.9 J against 22.8 J; `E4_analysis.json`). Pinned neighbours obstruct, and the barrier picture depends strongly on which coordinates are allowed to move.

*Fix.*
1. Quantify participation along the string, e.g. the fraction of path length carried by non-blocker coordinates, or a participation ratio of the unstable mode at the saddle.
2. Compare *rates* in full against frozen at the *same σ*, not the same β.
3. Replace "because the neighbours give way" with "because the neighbours' push lowers the barrier and the neighbours relax along the path (participation ratio X)".

### M5. The pair "fold": the bifurcation is asserted, not shown
*Where:* Sect. 5.2 (l. 1051), Table 2 row D (l. 970-977), Fig. 7.

*Problem.* "it ... disappears at a fold, where λ₁ reaches zero" (l. 1051) is inferred from bisection of overdamped relaxation, i.e. from loss of the basin. λ₁(b) is never computed as b → b*. Bisection cannot tell a saddle-node apart from a sudden crossing into another basin (a global bifurcation) or from a pitchfork in nearly symmetric cases. The static agreement of 363/368 with the quench is good, but it is not normal-form evidence. Some thresholds are tiny (b* down to 0.001 for the easier sign, i.e. a tilt of 0.06°), so those minima are nearly degenerate.

*Fix.* Use Newton continuation of F₀(x; b) = 0 for each of the 46 snapshots and both signs. Report: λ₁(b) ∝ (b* − b)^{1/2}; the distance between minimum and saddle ∝ (b* − b)^{1/2}; the string barrier ΔU(b) ∝ (b* − b)^{3/2}; and, dynamically, the saddle-node bottleneck passage time ∝ (b − b*)^{−1/2} from quenches at b = b*(1 + ε), ε ∈ {0.01, 0.03, 0.1, 0.3}. The continuation is static (minutes). The quenches are 46 × 2 × 4 = 368 runs of ≤ 120 s with a handful of agents, < 1 CPU-h. Show one collapse panel; it could replace the left panel of Fig. 7.

### M6. "No persistent contact arches": the physics is mis-stated, the test regime is numerically under-resolved, and the pair standoff is itself an arch
*Where:* Sect. 5.3 (l. 1055-1056); contributions (l. 835); conclusions (l. 1177); background (l. 845).

*Problem.*
1. "a chain of agents in contact can carry a load only while its members slide" (l. 1056) is wrong as a statement of mechanics. Normal contact forces carry load in a frictionless packing. Friction adds tangential stability; it does not create load-bearing capacity. Whether a frictionless arch is stable depends on the geometry of the contact normals relative to the load, which here is a field converging on the goal point. The paper's own lone trap is a body held against a drive by purely normal, non-frictional edge forces.
2. The test runs at a mean desired speed of 5 m/s with Δt = 0.01 s. `arch_analysis.json` reports a peak body compression of 108 kN and a maximum relative tangential speed of 21 m/s between agents whose speeds are capped at 2v₀ (about 10 m/s). 108 kN with k = 1.2 × 10⁵ N/m and the exponential term implies overlaps of a sizeable fraction of a radius. The sliding-friction term κ g Δv_t is integrated explicitly; with κ = 2.4 × 10⁵ kg/(m s), m = 80 kg and Δt = 0.01 s it becomes explicitly unstable once the overlap exceeds a few centimetres (κ g Δt/μ > 2 with μ the reduced mass, i.e. g ≳ 3-7 cm). Arches that "break within 2.9 s (95% within 0.6 s)", with a *median* lifetime of 0.0 s, may be breaking because the integration is unstable, not because of the physics.
3. At the default drive, where the deadlocks occur, the test is never run.
4. The pair standoff (l. 1047) has two agents in front of the two jamb faces, spanning the opening, held off each other by repulsion and against the walls by the wall force. That is a two-particle arch, held by soft normal forces instead of hard contacts. The lone trap is a single-particle "arch": the agent's effective diameter, including the wall-force range, exceeds the opening under its own drive. This is exactly the size-ratio picture of granular clogging (To et al. 2001; Zuriguel et al. 2005; Janda et al. 2008).

*Why it matters.* This section frames the paper's relation to the granular literature and appears in the abstract-level claims.

*Fix.*
1. Correct the mechanics sentence.
2. Rerun the arch test at Δt = 0.001 s and 0.0025 s (25 runs each, v₀ = 5 m/s; ≈ 4-5 CPU-h at Δt = 0.001 and ≈ 1-2 CPU-h at 0.0025) and show that lifetimes and peak forces converge.
3. Add the default drive and v₀ = 2, 3 m/s (3 × 25 runs, ≈ 1-2 CPU-h).
4. Reframe the two deadlock types as soft-core arches (one-agent and two-agent), held by normal forces of range B_w, and compare the critical width of 0.88 m (l. 1035) with an effective diameter 2[r + B_w ln(2A_w/F_drive)] (check the exact form). This would *strengthen* the physics and connect it to the literature.

### M7. Relevance and generality: an end-of-evacuation, low-density artefact of one wall law, with half of the "two classes" found only in a modified model
*Where:* abstract (l. 652), contributions (l. 835), Sect. 5.1 (l. 1029-1037), Sect. 5.2 (l. 1047), introduction motivation (l. 826).

*Problem.*
- At detection the blocker has at most 10 agents within 3 m (median 2), ρ ≤ 0.35 ped/m² (l. 895). It is among the last three arrivals in 184 of 196 deadlocks (l. 1037). This is not clogging of a dense crowd. The introduction's motivation by crowd crushes (l. 826) and the background on granular clogging (l. 845) mislead the reader about what is studied.
- Under the default walls, 96 of 98 deadlocks are stuck-alone stacks and only 2 are collective (l. 1035). The pair class needs the jamb range reduced to B_w = 0.04 m (l. 1047). The abstract's "deadlocks fall into two classes" (l. 652) therefore describes two *different models*.
- Finite size: with N = 100 the push runs out. The deadlock rate per run should depend on N (and on room depth). No N-dependence is shown.
- Protocol choices define the outcome: the deadlock criterion (|v| < 0.01 m/s for 10 s), the 120 s quench window and the 600 s cap. In E6, 54 of C3 RVO2's 85 "failures" are still moving at 600 s with a median end speed of 0.22 m/s (`E6_analysis.json`). The completion rate that σ* is matched to is therefore partly a horizon artefact.

*Fix.*
1. Reframe the abstract and introduction: "deadlocks of the last few agents at a narrow door".
2. State in the abstract that the pair class arises with a short-range jamb law.
3. Add an N-sweep. Configuration: C1 corrected-forward, w = 0.8 m, N ∈ {50, 100, 200}, 100 seeds each, 600 s; report the deadlock fraction and the number remaining at deadlock. Cost: about 300 runs × 30-180 s ≈ 5-10 CPU-h.
4. Rerun the 54 still-moving C3 RVO2 failures to 1800 s (≈ 54 × 3 min ≈ 3 CPU-h) and report whether σ* moves.

### M8. The CroMa comparison: what is and is not validated
*Where:* Sect. 7 (l. 1151-1160), abstract (l. 652), contribution "Validity" (l. 837), Fig. 8.

*Problem.*
- The section is an *invalidation*: every variant fails. That is useful, but the paper then uses the invalidated model for mechanism attribution without discussing what transfers. The Limitations paragraph (l. 1175) is silent on this.
- Initial conditions are not matched: "model agents start at rest, their start positions lie farther from the entrance" (l. 1151). With agents arriving spread out, flow measured from first to last passage can be limited by arrivals, not by the door's capacity. The long gaps may partly reflect sparse arrival at the end, which is the same end-of-evacuation regime as M7.
- The human runs come from an experiment on *motivation* (dataset title, l. 1195; file names in `E10_analysis.json` carry h0/h1 suffixes). The motivation condition of each of the 5 runs is not stated (check). Motivated pushing crowds are precisely the regime an SFM at v₀ = 1.34 m/s does not represent.
- The "0.21 m corridor" (l. 1151) is unexplained.
- The waiting-zone fluctuation estimator (Savitzky-Golay 1.48 s, neighbour radius 0.74 m) is uncited. It resembles the "kinetic stress" of Garcimartín et al. (check). Its parameters need a source or a sensitivity check.
- The longest gap is an extreme-value statistic that depends on run length. The standard pedestrian and granular practice is the survival function of time lapses and its tail (Zuriguel et al. 2014; Pastor et al. 2015; Garcimartín et al. 2016).

*Fix.*
1. Start the model agents in the measured initial positions, or at least at the measured initial density in the waiting zone. Configuration: 5 variants × 25 runs, ≈ 125 × 30-90 s ≈ 1-3 CPU-h.
2. Report flow over the congested phase only (e.g. 10-90% of passages).
3. Show time-lapse survival functions for humans and model.
4. State the motivation condition of each human run.
5. Add a sentence on what the invalidation implies for the attribution results: they are statements about this model class.

### M9. Rest-state lemma and stuck-alone criterion: correct but largely tautological, presented as empirical findings
*Where:* Proposition 1 (l. 990-995), l. 997-1001, l. 1029-1035, contributions (l. 835).

*Problem.*
- Part (i) of the proposition needs no hypothesis. Part (ii) is the standard energy argument. Both are fine.
- The stated consequences are tautological checks. A C2 quench started at v = 0 never activates TTC (threshold 10⁻⁴ m/s), so "C2 reproducing C1 in 360 of 360" (l. 1111) is a code check, not a test.
- The lemma does not cover C3: ORCA's velocity-dependent part, w m/τ_orca [v_orca(x, v) − v_orca(x, 0) − v], is not sign-definite. The paper says only "candidate for class L" (l. 1001). Say explicitly that (ii) does not apply.
- The stuck-alone criterion "holds in 393 of 393" (l. 835, l. 1035). For a lone agent at rest upstream of the force peak on a symmetric axis, positive margin is *necessary* for the rest state to exist, so agreement is close to guaranteed. What would carry content is the off-axis blockers (lateral stability) and the distribution of margins near zero. Neither is shown.

*Fix.*
1. Call these consistency checks, not tests.
2. Report the margin histogram and the number of blockers within ±10 N of zero.
3. Report the lateral offsets of blockers and the lateral Hessian eigenvalue on the axis.
4. Remove "exact" from l. 1035 or qualify it (see Sect. 6).

### M10. Class N and the published solver: inconsistent with Table 2, and sensitivity is not ill-conditioning
*Where:* Table 2 caption and rows (l. 929-977); l. 1120.

*Problem.* Table 2 says class N "is tested only by corrected numerics" (l. 929), yet l. 1120 assigns the published linear program to N on the basis of *replay* sensitivity. By Table 2's own replay column, replay disagreement is the class-T signature. A deterministic many-body system in slow creep can amplify a 10⁻⁹ m perturbation through a positive finite-time Lyapunov exponent. That is not ill-conditioning of an implementation. A discontinuity of v_orca(x) (e.g. "infeasible constraints dropped", Table 1, l. 877) is a specific, testable alternative.

*Fix.*
1. Add an N row with "replays may disagree; Δt and solver dependence; vanishes under the RVO2 port".
2. Show directly, by evaluating v_orca along a 10⁻⁹-10⁻⁶ m displacement, that the published solver's output is discontinuous at the flipping states. This is a static evaluation and takes minutes.

---

## 4. Minor issues

1. l. 929 (Table 2 caption) and l. 1087 (Table 3 caption) have three sentences each, against the authors' two-sentence caption rule. Merge the symbol glossary into a sentence, or move it to the text.
2. "arm" (l. 926 "an intervention (an arm)", l. 981 "frozen-mean arm", l. 1111 "Every deterministic arm", Table 3 header "Arm", l. 1133) is clinical-trial vocabulary and conflicts with the authors' own rule. Use "intervention" or "condition".
3. l. 822 spells "vermilion"; l. 1062 and l. 1077 spell "vermillion". Unify.
4. l. 1062 (Fig. 4 caption): "fraction of deadlock snapshots whose blocker has escaped ... pooled over snapshots". The curve is over restarts. Say "fraction of restarts".
5. l. 822 (Fig. 1 caption): the grey ball at the right end of the energy curves (p. 2) is not explained.
6. l. 863: "calibrated values of the conference paper are not applied". Give the reason in one clause.
7. l. 1033: "comparable to g_max at the mean radius" (214 N against 156 N). Give the number.
8. l. 1035: name the tests behind p = 0.529, 3.5 × 10⁻⁴¹, 0.170 and 2.0 × 10⁻¹³ (Fisher exact?).
9. l. 1037: an ROC AUC (0.975) is compared with an "all-exit baseline accuracy" (0.931). Compare accuracy with accuracy, or AUC with 0.5.
10. l. 1049: the Hessian is "in the four member coordinates", so the other agents are pinned. Say so, and report the full mobile Hessian for at least a subset.
11. l. 1053: `E7b_analysis.json` reports 3 of 24 string channels failing for the pair barriers. Report this.
12. l. 1065: state the E4 selection rule (evenly spaced ranks of collective ΔU among snapshots with ≥ 2 residual agents, `selection.json`) and that 12 candidates became 10 usable, of which 9 have a full-condition barrier.
13. l. 1067: report the frozen-condition attempt rate (0.21 s⁻¹) alongside the full and alone values.
14. l. 1067: "slope ... divided by −ΔU" — give the typical interval width (about ±0.3).
15. l. 1071: "The two modes need the same noise" holds within intervals of about ±7%. Say "statistically indistinguishable σ₅₀".
16. l. 1117: report ℓ per snapshot (or its spread), not just the two group means.
17. l. 1123: "no-fit prediction" uses ν from E4, i.e. a parameter fitted elsewhere. Say "a prediction with no parameter fitted to E6".
18. l. 1123: give the permutation p (0.0023) for J above independence.
19. Table 3 (l. 1095): show the sizes of the minority sets (4 and 2) next to J, or a reader cannot judge the interval [0.00, 0.50].
20. l. 1151: define "0.21 m corridor"; give the source of the estimator parameters (1.48 s, 0.74 m, 0.3 m/s).
21. l. 1157: "No agent leaves the walkable area in any run" is a sanity check. Move it to a footnote or the methods.
22. l. 1163: "derived from the physics before the runs". FINAL_PLAN.md lists pilot-wave values (e.g. W2.2) next to the signatures. Write "specified before the confirmatory runs, informed by pilot runs".
23. l. 913: TTC is gated at |Δv| ≥ 10⁻⁴ m/s. State that this gate is a model choice that makes the TTC rest-state result trivial.
24. l. 920: ORCA uses v₀, not v_eff. Mention this in the discussion of why ORCA's rest drive matches ν-independent behaviour at low density.
25. l. 1001 and l. 1008: the residuals (≤ 5 × 10⁻⁷ N) and the variance ratio are well supported by `field_residuals.json` and `T3_variance.json`. No change needed; noted as verified.
26. Bibliography:
    - gang2026 title has lower-case "sfm, ttc, and orca" (l. 1237-1238).
    - Hänggi et al. has "kramers" (l. 1275).
    - Liang et al. has "seoul halloween" and "WONG, S.C." (l. 1311).
    - The RVO2 entry has "rvo2 library" (l. 1213).
    - The Arrhenius title has German nouns in lower case (l. 1200-1201).
    - Koren & Borenstein has no year (l. 1291-1296).
    - The CroMa dataset entry is dated 2026 with DOI 10.34735/PED.2021.9 (l. 1194-1197); check the year.
    - Every entry prints the DOI twice (as DOI and as URL).
27. Cite the CroMa experimental paper (Adrian, Seyfried, Sieben 2020, check) as well as the dataset.

## 5. Questions to the authors

1. In E4, were all agents given the same σ? If so, what is the spread of k_BT_i across the agents of each full-condition snapshot, and does the slope ratio correlate with that spread?
2. What happens dynamically in E1b_seed170? Where do the 60 non-escaping restarts sit after 300 s, and is there a non-exit state lower than the snapshot along the computed path?
3. Is the Kramers-Langer prefactor, computed from the Hessians at the minimum and the saddle, consistent with the fitted ν (0.09-0.21 s⁻¹)?
4. What is J between two independent noise realisations, at the lone trap and in whole runs?
5. Do the arch lifetimes, peak forces and relative tangential speeds at v₀ = 5 m/s converge as Δt → 0.001 s?
6. Does λ₁(b) vanish as (b* − b)^{1/2} at the threshold for the pair standoffs?
7. How does the deadlock fraction depend on N and on room depth?
8. Which motivation condition does each of the five CroMa runs belong to, and what is the human entrance density during the congested phase compared with the model's?
9. How sensitive are the E2/E7b outcomes to the 120 s window and the 10⁻³ m/s stopping rule?

## 6. Overstated claims and acceptable replacements

| # | Line | Current wording | Acceptable replacement |
|---|---|---|---|
| 1 | 652 | "In a social force model at a 0.8 m exit, deadlocks fall into two classes: a lone agent held by the wall force at the door edges, and a symmetric pair standoff, a strict energy minimum that a lateral bias removes at a fold." | "In a social force model at a 0.8 m exit, almost all deadlocks are lone agents held by the wall force at the door edges; with a short-range jamb law a second class appears, a symmetric pair standoff that is a strict energy minimum and that a lateral bias removes beyond a threshold." |
| 2 | 652 | "noise drives activated escape over computed barriers" | "noise frees deadlocks at rates consistent with activated escape over computed barriers at barrier-to-noise ratios of 1.5-3.5" |
| 3 | 835 | "with a stuck-alone criterion that holds in 393 of 393 deadlocks" | "with a stuck-alone force balance that is consistent with all 393 deadlocks" |
| 4 | 835 | "Velocity noise frees the lone trap by collective activated escape over barriers computed from the model's own energy landscape" | "Velocity noise frees the lone trap at rates consistent with Arrhenius escape over barriers computed from the model's own energy landscape, lowered by the push of the remaining agents" |
| 5 | 835 | "contact arches formed at high drive never persist, because the model has no static friction" | "contact chains spanning the door at high drive did not persist beyond 2.9 s in our runs" |
| 6 | 836 | "whereas noise matched to its rate acts thermally" | "whereas noise matched to its rate frees deadlocks stochastically, at a rate whose time-step dependence follows Eq. (9)" |
| 7 | 848 | "its effective temperature follows exactly from that recursion" | "its effective temperature follows from that recursion when friction is linear, contacts are absent and all agents share one temperature" |
| 8 | 1035 | "The criterion is exact at the rest state." | "At the rest state the criterion agrees with the keystone test in every case." |
| 9 | 1035 | "The trap is therefore local to the door edges: the walls away from the door add nothing." | "Within our resolution the trap is local to the door edges (jamb-only and all-wall short ranges do not differ, p = 0.53)." |
| 10 | 1051 | "Because the minimum is strict, it survives small tilts and disappears at a fold, where λ₁ reaches zero." | "Because the minimum is strict, it survives small tilts and is lost beyond a threshold b*, as expected at a saddle-node (fold) bifurcation." (unless M5 continuation is added, after which the original is acceptable) |
| 11 | 1056 | "so a chain of agents in contact can carry a load only while its members slide" | "so a chain of agents in contact must hold its load by normal forces alone" |
| 12 | 1056 | "The model's persistent deadlocks are therefore not contact arches but the contact-free rest states of Sects. 5.1 and 5.2." | "The model's persistent deadlocks are contact-free rest states (Sects. 5.1 and 5.2), held by the soft wall and pair repulsion rather than by contacts." |
| 13 | 1067 | "All three predictions of activated escape hold" | "The rate predictions of activated escape hold within wide intervals; escape times are near-exponential (Weibull shape 1.09 [1.05, 1.14])" |
| 14 | 1067 | "close to the exponential value 1" | "slightly but significantly above the exponential value 1, as expected from a short induction time" |
| 15 | 1067 | "The escape is collective: the full barrier lies below the alone barrier in 10 of 10 snapshots, with median ratio 0.30, because the neighbours give way along the path." | "The remaining agents lower the barrier: the full barrier lies below the alone barrier in 10 of 10 snapshots (median ratio 0.30)." |
| 16 | 1069 | "The computed minimum-energy path is then not the route the dynamics takes, and the snapshot is left out of the Arrhenius fits." | "Here the computed barrier does not predict the rate: we report this snapshot as a failure of the barrier picture." |
| 17 | 1071 | "The same physics sets the noise level a whole run needs." | "The whole-run noise threshold lies in the same range of k_BT_eff as the snapshot barriers." |
| 18 | 1117 | "Noise is thermal at the temperature of Eq. (9); ORCA is not thermal." | "The time-step dependence of noise agrees with Eq. (9) at β_ref = 1.5 and falls short at β_ref = 2.5, where the barrier-to-noise ratio at Δt = 0.005 s drops to about 1.25; ORCA shows no time-step dependence." |
| 19 | 1120 | "which a replay this small reveals as ill-conditioning of that implementation (class N)" | "which a replay this small reveals as sensitivity specific to that implementation, consistent with its dropping of infeasible constraints" |
| 20 | 1123 | "The failure sets overlap barely more than independent ones would" | "The failure sets overlap more than independent sets (J = 0.41 against 0.30, permutation p = 0.002), but [compared with J between two noise realisations]" |
| 21 | 1123 | "no-fit prediction" | "prediction with no parameter fitted to these runs" |
| 22 | 1156 | "Every model variant deadlocks or flows at about half the human rate." | "No model variant reaches the human flow: each deadlocks or flows at 0.40-0.59 of it." |
| 23 | 1163 | "The held-out signatures, derived from the physics before the runs, reject that reading each time." | "The signatures, specified before the confirmatory runs, assign ORCA and its controls to different classes in each case." |
| 24 | 1169 | "the lone trap is a property of the jamb wall law, not of crowding" | "the lone trap is set by the jamb wall law and appears when the crowd behind the door has thinned out" |
| 25 | 1172 | "yet noise frees them by the activated escape that trap models assume" | "yet noise frees them at rates consistent with the activated escape that trap models assume" |
| 26 | 1177 | "Narrow-exit deadlocks in the model come in two classes" | "Narrow-exit deadlocks in the model come in two classes, the second requiring a short-range jamb law" |
| 27 | 854 | "We have not found an earlier study that tests a matched control in this way." | Acceptable as written, but add the related noise-as-temperature work in the SFM (Helbing, Farkas, Vicsek 2000, "Freezing by heating") and the vibration-unclogging literature, which compare stochastic and deterministic unjamming. |

## 7. Expected references

Granular and pedestrian clogging, arches:
- To, K., Lai, P.-Y., Pak, H.K. (2001). Jamming of granular flow in a two-dimensional hopper. Phys. Rev. Lett. 86, 71.
- To, K. (2005). Jamming transition in two-dimensional hoppers and silos. Phys. Rev. E 71, 060301(R). (check)
- Zuriguel, I., Garcimartín, A., Maza, D., Pugnaloni, L.A., Pastor, J.M. (2005). Jamming during the discharge of granular matter from a silo. Phys. Rev. E 71, 051303. (check)
- Janda, A., Zuriguel, I., Garcimartín, A., Pugnaloni, L.A., Maza, D. (2008). Jamming and critical outlet size in the discharge of a two-dimensional silo. EPL 84, 44002.
- Lozano, C., Lumay, G., Zuriguel, I., Hidalgo, R.C., Garcimartín, A. (2012). Breaking arches with vibrations: the role of defects. Phys. Rev. Lett. 109, 068001.
- Merrigan, C., Birwa, S.K., Tewari, S., Chakraborty, B. (2018). Ergodicity breaking dynamics of arch collapse. Phys. Rev. E 97, 040902(R). (check)
- Guerrero, B.V., Lozano, C., Zuriguel, I., Garcimartín, A. (2018). Slow relaxation dynamics of clogs in a vibrated granular silo. Phys. Rev. E 97, 042904. (check)
- Hong, X., Kohne, M., Morrell, M., Wang, H., Weeks, E.R. (2017). Clogging of soft particles in two-dimensional hoppers. Phys. Rev. E 96, 062605. (check; on clogging without strong friction)
- Garcimartín, A., Pastor, J.M., Ferrer, L.M., Ramos, J.J., Martín-Gómez, C., Zuriguel, I. (2015). Flow and clogging of a sheep herd passing through a bottleneck. Phys. Rev. E 91, 022808.
- Pastor, J.M., Garcimartín, A., Gago, P.A., Peralta, J.P., Martín-Gómez, C., Ferrer, L.M., Maza, D., Parisi, D.R., Pugnaloni, L.A., Zuriguel, I. (2015). Experimental proof of faster-is-slower in systems of frictional particles flowing through constrictions. Phys. Rev. E 92, 062817.
- Garcimartín, A., Parisi, D.R., Pastor, J.M., Martín-Gómez, C., Zuriguel, I. (2016). Flow of pedestrians through narrow doors with different competitiveness. J. Stat. Mech. 043402.
- Garcimartín, A., Pastor, J.M., Martín-Gómez, C., Parisi, D., Zuriguel, I. (2017). Pedestrian collective motion in competitive room evacuation. Sci. Rep. 7, 10792. (kinetic stress; check)

Social force model at doors, noise in the SFM:
- Helbing, D., Farkas, I.J., Vicsek, T. (2000). Freezing by heating in a driven mesoscopic system. Phys. Rev. Lett. 84, 1240.
- Parisi, D.R., Dorso, C.O. (2005). Microscopic dynamics of pedestrian evacuation. Physica A 354, 606-618. (check pages)
- Parisi, D.R., Dorso, C.O. (2007). Morphological and dynamical aspects of the room evacuation process. Physica A 385, 343-355. (check)
- Chraibi, M., Seyfried, A., Schadschneider, A. (2010). Generalized centrifugal-force model for pedestrian dynamics. Phys. Rev. E 82, 046111.
- Kirchner, A., Nishinari, K., Schadschneider, A. (2003). Friction effects and clogging in a cellular automaton model for pedestrian dynamics. Phys. Rev. E 67, 056122.

Bottleneck experiments:
- Adrian, J., Seyfried, A., Sieben, A. (2020). Crowds in front of bottlenecks at entrances from the perspective of physics and social psychology. J. R. Soc. Interface 17, 20190871. (check)
- Kretz, T., Grünebohm, A., Schreckenberg, M. (2006). Experimental study of pedestrian flow through a bottleneck. J. Stat. Mech. P10014.
- Seyfried, A., Passon, O., Steffen, B., Boltes, M., Rupprecht, T., Klingsch, W. (2009). New insights into pedestrian flow through bottlenecks. Transp. Sci. 43, 395-406.
- Nicolas, A., Bouzat, S., Kuperman, M.N. (2017). Pedestrian flows through a narrow doorway: effect of individual behaviours on the global flow and microscopic dynamics. Transp. Res. B 99, 30-43. (check)

Escape theory, non-equilibrium temperatures, bifurcations:
- Langer, J.S. (1969). Statistical theory of the decay of metastable states. Ann. Phys. 54, 258-275.
- Freidlin, M.I., Wentzell, A.D. Random Perturbations of Dynamical Systems. Springer (any edition).
- E, W., Ren, W., Vanden-Eijnden, E. (2004). Minimum action method for the study of rare events. Commun. Pure Appl. Math. 57, 637-656.
- Heymann, M., Vanden-Eijnden, E. (2008). The geometric minimum action method. Commun. Pure Appl. Math. 61, 1052-1117.
- Bouchet, F., Reygner, J. (2016). Generalisation of the Eyring-Kramers transition rate formula to irreversible diffusion processes. Ann. Henri Poincaré 17, 3499-3532. (check)
- Maier, R.S., Stein, D.L. (1997). Limiting exit location distributions in the stochastic exit problem. SIAM J. Appl. Math. 57, 752-790. (check)
- Cugliandolo, L.F. (2011). The effective temperature. J. Phys. A 44, 483001.
- Strogatz, S.H. Nonlinear Dynamics and Chaos. Westview/CRC (saddle-node bottleneck scaling; any edition).

---

### Verification notes (numbers checked against `data/derived/*.json`)

- Supported as stated: σ₅₀ and intervals (`E5_analysis.json`); σ* = 0.0467 (`sigma_star.json`); E6 completion 101/186 against 99/186, discordant 35:37, J = 0.41, logrank p = 0.004 (`E6_analysis.json`); field residuals ≤ 4.9 × 10⁻⁷ N (`field_residuals.json`); pair Hessian λ₁ = 65-121 N/m and λ₂/λ₁ = 12-14 (`E7b_analysis.json`); Table 3 pair-block differences and intervals (`table3_pair.json`); arch counts (`arch_analysis.json`); E4 event counts, slope-ratio medians, pooled Weibull, saddle ratios (`E4_analysis.json`).
- Supported, but the text omits context that changes the reading: lone-trap J = 0.20 rests on sets of 4 and 2; E6 J is significantly above independence (p = 0.0023); frozen-condition ν = 0.21 s⁻¹ is not reported; frozen and pooled Weibull intervals exclude 1; frozen > alone barrier in 2 of 10; 3 of 24 pair string channels failed; arch maximum relative tangential speed 21 m/s; C3 RVO2 E6 failures mostly still moving (54/85, median 0.22 m/s).
- Not checkable from derived files alone: the order-of-arrival statistics (l. 1037) and the CroMa estimator implementation. I did not rerun any simulation.
