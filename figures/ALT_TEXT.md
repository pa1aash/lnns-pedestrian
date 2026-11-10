# Alt text for the figures

One or two sentences per figure, for the proof stage. Each describes what is drawn. Figures are listed in paper order; the
source file is given in brackets (the protocol figure is the paper's Fig. 2, so the script numbers fig2 to fig8 run one behind).

**Fig. 1 (fig1_hero.tex: fig1_hero.png with fig1_overlay.tex).** Two rendered scenes at a 0.8 m door: above, a lone agent held at the door edges with force arrows for its drive, the neighbours' push, ORCA's rest drive and the opposing wall force; below, two agents held side by side against the jamb faces in a pair standoff. Beside each scene a small energy curve shows the rest-state minimum before and after the rest-drive push or the lateral tilt removes it, with a vermilion band marking the effective thermal energy.

**Fig. 2 (fig_protocol.tex).** A flowchart of five boxes joined by arrows from left to right: a snapshot library of frozen deadlocks; the probes (quench, 10⁻⁹ m replay, time step with per-step and √Δt-scaled noise, rest-drive push ±, lateral tilt ±b, corrected implementation); the signatures read from the responses; the class P, L, T, D or N; and the comparison of the resolver with its rate-matched surrogate.

**Fig. 3 (fig2_lone_trap.pdf).** Left: the backward wall force on a lone agent on the door axis rises steeply towards the door plane, drawn for four agent radii, with horizontal bands showing the range of rest drives for SFM (black) and for SFM+ORCA with the RVO2 solver (blue). Right: a colour map of the stuck-alone margin over agent radius and v0/τ, overlaid with the spawned agents as grey dots and with the SFM and ORCA (RVO2) lines separating agents that pass alone from agents that are held.

**Fig. 4 (fig3_width_walls.pdf).** Left: the fraction of SFM runs completed falls as the exit width narrows from 1.0 m to 0.7 m. Right: at 0.8 m, one point with its interval per wall-law variant, each beside a stacked bar splitting the runs into completed (white), pair or group standoff (light grey) and lone trap (dark grey).

**Fig. 5 (fig4_escape.pdf).** Left: three step curves of the fraction of blockers escaped against time under noise, for the full, pinned and alone barrier conditions. Right: for every snapshot and condition, the ratio of the fitted Arrhenius slope to minus the computed barrier, with its 95% interval, against the barrier on a log axis; the ratios scatter around a horizontal line at 1.

**Fig. 6 (fig5_dt.pdf).** Escape rate against time step on log–log axes, normalised at Δt = 0.01 s: per-step noise (vermilion, filled markers) falls with the time step along its Arrhenius prediction lines, while √Δt-scaled noise (light vermilion, open markers) and ORCA with the RVO2 solver (blue diamonds) stay close to one.

**Fig. 7 (fig6_quench.pdf).** Left: the fraction of lone-trap blockers freed within 120 s for SFM, SFM+TTC, ORCA with the legacy and the RVO2 solver, ORCA's drive part and constraint part, the rest-drive push of either sign, four lateral biases and three noise levels, with filled points for lone keystones and open points for second traps. Right: step curves of the fraction freed against time on a log axis for the perturbations that free blockers, with ORCA (legacy) dash-dotted.

**Fig. 8 (fig7_pair.pdf).** Left: the fraction of pair standoffs freed is lowest at zero bias and rises steeply on either side to one as the signed lateral bias grows, with yellow measured points, a dark grey static prediction and horizontal lines at the ORCA (legacy) and ORCA (RVO2) rates. Right: the fraction of pairs freed within 120 s for SFM, SFM+TTC, ORCA with either solver, its drive and constraint parts, the rest-drive push of either sign, the rate-matched bias of either sign for each solver and four noise levels.

**Fig. 9 (fig8_croma.pdf).** Three panels compare the five human runs in the CroMa bottleneck with SFM, SFM with the jamb wall range, ORCA (RVO2) and SFM with noise at σ*, in the matched geometry: flow through the entrance, the longest gap between successive passages on a log axis, and the waiting-zone velocity fluctuation. Single runs are small points and each model's mean is a larger marker with its interval; every model flows well below the humans.
