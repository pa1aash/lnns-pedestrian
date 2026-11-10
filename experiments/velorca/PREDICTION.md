# Prediction: velocity-coupled ORCA on frozen deadlocks

Written before any velocity-coupled run. Model: the corrected update (speed cap before the position
update, rejection spawn, convex-union wall corners, no crush term), configuration SFM+ORCA.

## Coupling

With force coupling, ORCA enters Eq. (6) as F_ORCA = m (v_ORCA - v)/tau_ORCA, with v_ORCA the solution
of the linear program for the preferred velocity v_pref = v0 e (e the unit vector to the goal). At rest
(v = 0, no binding half-plane) v_ORCA = v_pref and the term is the rest drive m v0 e / tau_ORCA. This
rest drive frees the lone traps (E2: 180 of 204 lone-keystone quenches with either solver).

With velocity coupling, ORCA filters the velocity the forces propose. Per step and per agent:

    v' = Pi(v + F dt / m)                 F without any ORCA term; noise added, then Pi again
    v_o = LP(v'; half-planes from x, v, neighbours within 3 m, horizon tau_h)
    v' <- v' + w_o (Pi(v_o) - v')         w_o the ORCA density gate
    x' = x + v' dt

Pi caps the speed at 2 v0. The linear program returns the velocity nearest v' that satisfies every
neighbour half-plane; v_pref does not appear.

## Rest-state analysis

1. At a frozen deadlock the forces balance (F_0 = 0 at the snapshot), so v' = Pi(v + F dt/m) is of the
   order of the snapshot speeds: max |v| = 2.2e-6 m/s over the 60 lone-trap snapshots and 4.0e-6 m/s over the 46
   pair snapshots (read from the stored states).
2. For neighbours at rest that do not overlap, relative position x_ij, surface gap g = |x_ij| - R,
   the relative velocity 0 lies outside the truncated velocity obstacle, in the cut-off-circle region
   (w = -x_ij/tau_h, w.x_ij < 0, (w.x_ij)^2 > R^2 |w|^2 iff |x_ij| > R). Both solvers then build the same
   half-plane: v . x_ij/|x_ij| <= g/(2 tau_h). The legacy solver's leg-normal sign defect does not enter,
   since no pair is in the leg region.
3. The stored states contain no overlapping pair: the smallest surface gap between residual agents
   within 3 m is 0.18 m (lone-trap library, 36 snapshots with a neighbour in range) and 0.28-0.33 m
   (pair library). With tau_h = 5 s the slack of every half-plane at v' = 0 is at least
   0.18/(2 x 5) = 0.018 m/s, four orders of magnitude above |v'|.
4. No half-plane binds, so the linear program returns v' itself: the legacy solver keeps its starting
   point when every constraint holds, and RVO2's linearProgram2 does the same. Then Pi(v_o) - v' = 0
   and the gate w_o multiplies zero. The step is the SFM step, bit for bit.

Velocity-coupled ORCA therefore has no rest drive. It cannot move or remove a fixed point of SFM, and by
the rest-state lemma (Sect. 4) the deadlock stays held. Its class on Table 2 is at most P.

## Predicted outcomes

- (a) Lone-trap quench, 60 snapshots, both solvers, unperturbed and 5 replays at 1e-9 m: no blocker
  freed (0 of 360 per solver). Each run reproduces the SFM restart of the same snapshot and replay seed
  (E2 arm C1: 0 of 360 freed), with identical final positions.
- (b) Pair quench, 46 snapshots: no snapshot freed (0 of 276 per solver), identical to the SFM restart
  (E7b arm C1: 0 of 276).
- (d) The time-step probe is not triggered.
- (c) Whole runs, seeds 242-341: velocity coupling acts while agents move, so completion may differ from
  SFM at the same seeds. Any difference must come from how and how often deadlocks form. Each run that
  ends in a deadlock ends at a fixed point of SFM: rebuilt at rest, the final state is held both by SFM
  and by velocity-coupled ORCA. The keystone test classifies it as a lone trap, a lone trap with a second
  trap, or a group standoff.

## What would contradict the prediction

- Any freed snapshot in (a) or (b), with either solver.
- Any quench whose final positions differ from the SFM restart of the same snapshot and replay seed:
  a half-plane bound at rest, so step 4 fails.
- A whole-run final state, rebuilt at rest, that velocity-coupled ORCA frees while SFM holds it.
- Whole runs that reach 600 s still moving with |v| above the deadlock threshold. The prediction does not
  cover sustained motion; such runs would need their own analysis before a class is assigned.
