# Alt text for the figures

One or two sentences per figure, for the proof stage. Each describes what is drawn. Figures are listed in the order of
the revised paper (geometry figure in Sect. 3, the time-step figure merged into the escape figure); the source file is
given in brackets. Script numbers (fig2 to fig8) are historical and do not follow the paper's figure numbers.

**Fig. 1 (fig1_hero.tex: fig1_hero.png with fig1_overlay.tex).** Two rendered scenes at a 0.8 m door: above, a light-grey blocker held alone between two darker neighbours that pass alone, with force arrows for its drive, the neighbours' push, force-coupled ORCA's rest drive and the opposing wall force; below, two navy members held together against the jamb faces. Beside each scene, energy curves with axes in metres and joules show a 21 J barrier above a 10 J vermilion noise band for the blocker, which the added drive turns into a downhill slope, and a 0.4 J dip for the pair, which the lateral tilt removes.

**Fig. 2 (fig_geometry.pdf).** Two to-scale floor plans. Left: a 10 m square room with a 0.8 m door in its right wall, a goal disc outside, and an enlarged inset of the door showing the shaded wall stretches next to the door edges and one agent disc; right: a 7.8 by 8.6 m holding area with a 0.8 m entrance, a 2 m corridor, a goal disc and a grey waiting-zone rectangle in front of the entrance.

**Fig. 3 (fig_protocol.tex).** A greyscale flowchart of five stacked boxes joined by downward arrows: the snapshot library (lone keystones, second traps, pair standoffs); the probes (quench, replay, time step with per-step and √Δt-scaled noise, rest-drive push ±, lateral tilt ±b, corrected implementation); the signatures; the class (Prevent; Reshape, axial or lateral; Heat; Glitch); and the comparison of the resolver with its fraction-matched surrogate.

**Fig. 4 (fig2_lone_trap.pdf).** Left: the backward wall force on a lone agent on the door axis rises to a peak just before the door plane, drawn for four agent radii, with a grey band for the SFM rest drives and a blue hatched band for those of force-coupled ORCA (RVO2). Right: a cloud of 2000 spawned agents over agent radius and v0/τ, with the black SFM margin-zero line (stuck side shaded grey) and two blue force-coupled ORCA lines further right.

**Fig. 5 (fig3_width_walls.pdf).** Left: the fraction of SFM runs completed rises from zero at 0.7 m to one at 1.0 m exit width. Right: one horizontal bar per wall-law variant at 0.8 m, split into completed (white), pair or group standoff (light grey) and lone trap (dark grey), with the interval of the completed fraction drawn as a whisker at the white segment's end; only the short-range wall laws complete most runs.

**Fig. 6 (fig_escape_dt.pdf).** Left: the log escape rate divided by the fitted attempt rate falls along a line of slope −1 against β, the barrier over the effective thermal energy. Middle: the fitted Arrhenius slope over the barrier scatters around one across barriers from 1 to 100 J. Right: on log–log axes the escape rate under per-step noise falls as the time step grows, along its prediction curves, while √Δt-scaled noise and force-coupled ORCA (RVO2) stay at one.

**Fig. 7 (fig6_quench.pdf).** Left: a dot plot of sixteen perturbations in four groups giving the fraction of lone-trap blockers freed within 120 s with intervals, filled dots for lone keystones and open dots for second traps. Right: step curves of the fraction of lone keystones freed against log time; force-coupled ORCA (RVO2) rises within a few seconds, noise σ = 0.07 m/s over tens of seconds, and both reach about 0.9 by 120 s.

**Fig. 8 (fig7_pair.pdf).** Left: the fraction of pairs freed is zero at zero bias and climbs on both sides to one, following a grey static-prediction staircase, with horizontal lines at the legacy (0.46) and RVO2 (0.15) force-coupled ORCA fractions. Right: a dot plot of pairs freed per perturbation in four groups (baselines, force-coupled ORCA and its parts, bias ±b* per solver, noise).

**Fig. 9 (fig8_croma.pdf).** Three panels share one list of five categories (humans, SFM, SFM with the jamb wall range, force-coupled ORCA (RVO2), SFM with noise σ*): flow, longest gap between passages on a log axis with the 600 s horizon, and waiting-zone velocity fluctuation. Each run is a small marker, open if the run did not complete; many model runs end with a gap of several hundred seconds, while every human run flows about twice as fast with gaps of 1–2 s.
