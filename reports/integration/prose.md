# Prose audit: integration pass (worktree I)

Standard: `plan/PROSE_STANDARD.md` (= `lnns-launch/waveA/prose_prompt.md`). Vocabulary: `plan/GLOSSARY.md`.
Manuscript read: `paper/submission/main.tex` (checked line by line against the sources below, which it matches). All fixes are anchored to the source files.
Out of scope: the three `\pending` items (Zenodo DOI, acknowledgements, disclosure). The science is not judged.

How to apply the fixes: every `old` block is a verbatim substring of the named file and occurs there exactly once. Replace it with the `new` block. LaTeX macros are numbers from `paper/numbers.tex` and stay as written. Table 3 and Table 4 text is fixed in the generators (`experiments/tables/make_table3.py`, `make_table4.py`) and the tables are then regenerated. Registry fixes go in `paper/registry/*.yaml`, followed by `make numbers`.

Labels: **sev** is high, med or low. **E** marks an error and **T** a matter of taste (the competing convention is named). **+w** marks a fix that adds words; every other fix keeps the length or shortens the text.

---

## Triage: the five highest-leverage fixes

1. **[13.1] The σ₅₀ claim contradicts itself** (§5.2 against §6.4 and Table 4). One quantity has two intervals and two verdicts ("upper edge of both" against "lies above the new interval"). A reviewer comparing the two places will see it. About 10 min: one generator argument and one sentence.
2. **[12.1] β is used but never defined** (β_ref appears in Fig. 5, Table 3 and §6.1). The glossary requires the definition at Eq. (10). About 2 min.
3. **[13.3]+[13.4] The §5.2 N3 and Weibull sentences** ("only when pooled" is contradicted two sentences later, "the median ratio" has no clear referent, the condition is unstated, and "A lag fits better" has no comparand). About 10 min.
4. **[9.1] The §6.1 logistic-inversion sentence**, the worst sentence in the paper. It has five clauses and nested parentheses, and "3–4 snapshots" reads as an uncertainty range. About 5 min.
5. **[15.1] "; Adding" in §5.1**, a visible capitalisation error in the first physics paragraph. About 1 min. Fix it together with **[16.1]/[16.2]**, two misreadable referents in §6.1 ("It fails…", "(with intercept −…)"). About 5 min.

---

## 1. Rhetorical negation

The paper has almost no "not X but Y". Each contrast that remains carries information.

**Kept, with the reason:**
- `03_model.tex:38`, "(with $v_0$, not $v_{\rm eff}$)": a technical distinction that matters for the rest drive.
- `03_model.tex:50`, "The probes are read jointly as a signature, not as a family of tests, so no correction is applied.": wording mandated by GLOSSARY D6.
- `05_deadlock_physics.tex:55` and `08_discussion.tex:13`, "held by repulsion of range $B_w$ rather than by contact and friction": the framing sentence mandated by GLOSSARY D7. The repetition across the two sections is intended.
- `02_background.tex:7`, "has no static friction, so it cannot hold a frictional arch": the rule-out carries its reason.
- `04_signatures.tex:28`, "part (ii) does not cover ORCA's velocity-dependent constraint part": a scope statement.

**[1.1] `paper/sections/01_introduction.tex:12`** (low, T: an implicit "not X" ending; the competing convention is a rhetorical hook in the introduction)
```old
That reading is a claim about mechanism, and testing it takes more than a completion rate.
```
```new
That reading is a claim about mechanism, and testing it needs a probe of the mechanism.
```

**Mirrored or repeated statement.** "Identity separates only at the pair standoff, where both resolvers are deterministic" appears at `04_signatures.tex:5`, `06_attribution.tex:22` ("Identity does not separate the two"), `06_attribution.tex:31` ("identity does not separate them") and `08_discussion.tex:4`. The occurrences in §4 and §6 belong where they are. Delete the one in §8 (fix [14.2]).

No paragraph has three or more consecutive rule-outs.

## 2. Sentences that announce their own significance

None found. I checked for: notably, crucially, importantly, significantly, "it is worth", "the key point", "what matters", "it is important".

## 3. Sentences that announce what a section will do

**[3.1] `paper/sections/02_background.tex:13`** (low, T). This is a forward pointer to a result, placed in the Background section.
```old
The pair standoff below is the pedestrian analogue, and we locate the bias at which it disappears.
```
```new
The pair standoff of Sect.~\ref{sec:pair} is the pedestrian analogue.
```

**[3.2] `paper/sections/07_validity.tex:10`** (low, T). This opening announces the comparison. Its claim ("properties of the model") is restated as the section's conclusion at :19. Delete it; the paragraph then opens on the data.
```old
The deadlocks of Sects.~\ref{sec:physics} and~\ref{sec:attribution} are properties of the model; we compare them with real crowds at the same width. The CroMa
```
```new
The CroMa
```

**[3.3] `paper/sections/04_signatures.tex:5`** (low, T: an announcement before a list; "distinct" is filler)
```old
An intervention can act on a deadlock in five distinct ways.
```
```new
An intervention acts on a deadlock in one of five ways.
```

**A paragraph restated elsewhere:** §8 "Calibration and test." (`08_discussion.tex:4`) repeats §6 sentence by sentence. The sentences that add something and should stay are the first (the three settings), "The rest-drive push agrees…" and the last (the L/T/D summary). The two sentences that only repeat are removed in [14.2].

## 4. Trailing appositive qualifications and dangling modifiers

**[4.1] `paper/sections/05_deadlock_physics.tex:37`** (med, E, +w). Dangling modifier: "censored … and continued" attaches to *noise*/*level*, but the runs are what is censored. This is also the second-worst sentence in the paper (see 9).
```old
with \EfourRestarts\ restarts per level, censored at 300\,s
```
```new
with \EfourRestarts\ restarts per level; runs were censored at 300\,s
```

**[4.2] `paper/sections/05_deadlock_physics.tex:50`** (low, E). The trailing participle attaches to "threshold".
```old
below the static threshold, carried over by the members' inertia.
```
```new
below the static threshold; the members' inertia carries them over.
```

**[4.3] `paper/sections/07_validity.tex:19`** (low, T). A trailing verdict in an aphoristic ending (see 10). Promote it to its own sentence.
```old
hold for this model class, whose deadlocks are not human behaviour at this width.
```
```new
hold for this model class. Its deadlocks are not human behaviour at this width.
```

**[4.4] `paper/sections/08_discussion.tex:13`** (med, E). "fitting only the attempt rate" dangles: noise does no fitting. "them" also has no singular referent at the lone trap.
```old
At the lone trap noise frees them by the activated escape of trap models, over the model's own barriers, fitting only the attempt rate.
```
```new
At the lone trap noise frees the blocker by the activated escape of trap models, over the model's own barriers; only the attempt rate is fitted.
```

**[4.5] `paper/sections/06_attribution.tex:48`** (low, T). The trailing ", with either solver" belongs at the front. This is merged with the split in [9.6].

Kept: `03_model.tex:9`, ", present in the published code but not in the conference description". It is a fact the reader needs to read Table 1, not a hedge.

## 5. Softening adverbs on binary claims

**[5.1] `paper/sections/06_attribution.tex:22`** (low, E). "about" sits on two identical numbers (0.25 and 0.25).
```old
two halves of the noise seeds overlap about as much
```
```new
two halves of the noise seeds overlap as much
```

**[5.2] `paper/sections/05_deadlock_physics.tex:52`** (low, T). The numbers (0.21 J against 6.4 J) already carry the claim.
```old
(median \PairBarMed\,J), well below the lone-trap median
```
```new
(median \PairBarMed\,J), below the lone-trap median
```

**[5.3] `paper/sections/00_abstract.tex:3`** (med, E, +w). "partly different" holds for the published solver (13 of 30 shared) but is false for RVO2 (0 of 15 shared, §6.3). See also 13.
```old
and the bias frees partly different standoffs.
```
```new
and the bias frees partly (published solver) or wholly (RVO2) different standoffs.
```

**[5.4] `paper/sections/01_introduction.tex:20`** (med, E, +w). Same defect as [5.3].
```old
a lateral bias matched to its rate frees partly different standoffs, with a handedness ORCA lacks.
```
```new
a lateral bias matched to its rate frees partly (published solver) or wholly (RVO2) different standoffs, with a handedness ORCA lacks.
```

**Author queries** (an unquantified qualifier with no defining number in the text; no mechanical fix is possible):
- `04_signatures.tex:35`, "negligible in our snapshots": give the largest $(\omega\Delta t)^2$.
- `03_model.tex:42`, "a gate $w_{c,i}$ negligible at deadlock densities": give the maximum $w_c$ at $\rho\le$ `\TermRhoMax`.
- `05_deadlock_physics.tex:52`, "a few seconds of deterministic run-out": give the median.

Kept: "about 1.25" (`06:25`, a genuine approximation); "exactly" in Prop. 1 and "replays exactly" (exact-count signatures); "grows steeply" (`05:10`, followed by three numbers). "partly build the slope in" is handled in [16.3].

## 6. Sentences beginning with "What", and other clefts

None found. I checked for: sentence-initial "What", "It is … that", "There is/are", "The thing that".

## 7. Headers and bold paragraph leads

| # | file:line | current | replacement | sev | E/T |
|---|---|---|---|---|---|
| 7.1 | `05_deadlock_physics.tex:2` | `\subsection{The Lone-Agent Trap at the Door Edges}` | `\subsection{The Lone Trap at the Door Edges}` | low | E (GLOSSARY G1 term "lone trap") |
| 7.2 | `05_deadlock_physics.tex:29` | `\subsection{Noise as Activated Escape}` | `\subsection{Activated Escape from the Lone Trap}` | low | T (the heading states the result) |
| 7.3 | `05_deadlock_physics.tex:54` | `\subsection{No Persistent Contact Arches}` | `\subsection{Contact Arches}` | low | T (the heading states the result) |
| 7.4 | `06_attribution.tex:46` | `\subsection{Revisiting the Conference Findings}` | `\subsection{Conference Findings}` | low | T ("revisited"-type suffix) |
| 7.5 | `07_validity.tex:12` | `\paragraph{Humans flow without deadlock.}` | `\paragraph{Human runs.}` | low | T (the lead states the result) |
| 7.6 | `07_validity.tex:18` | `\paragraph{Removing deadlocks.}` | `\paragraph{Capacity.}` | low | T (the lead echoes the first three words of its sentence) |

Each `current` string occurs once in its file. Check the section label macros after any heading change; none of these headings is referenced by its text.

## 8. Figure and table captions

The glossary cap is two sentences and about 60 words. No caption contains a result that is absent from the body.

**[8.1] Fig. 1, `figures/fig1_caption.tex:2`** (med, T). About 95 words, well over the cap. The colormap names are not reading keys. "band $k_BT$" names a height as if it were an object.
```old
the black ball marks the rest state and the vermilion band $k_BT_{\mathrm{eff}}$. Agents are coloured by stuck-alone margin (cividis, $\pm150$\,N)
```
```new
the black ball marks the rest state and the vermilion bar has height $k_BT_{\mathrm{eff}}$. Agents are coloured by stuck-alone margin ($\pm150$\,N)
```
Further cut if needed: ", on one force scale," (state the scale once in the figure instead).

**[8.2] Fig. 2, `05_deadlock_physics.tex:6`** (low, T). About 75 words. Every clause is a line or colour key, so there is nothing to cut without losing how to read the figure. Accept the overrun (the competing convention is a self-contained legend).

**[8.3] Table 3 caption, `experiments/tables/make_table3.py:166-170`** (low, T). About 75 words of column keys. Same verdict as [8.2]: accept.

**[8.4] Table 4 caption, `experiments/tables/make_table4.py:195`** (low, E). "stand in the form given as evidence" is opaque.
```old
r"Revised findings stand in the form given as evidence.")
```
```new
r"A revised finding holds in the form given under Evidence.")
```

**[8.5] Fig. 4, `05_deadlock_physics.tex:33`** (low, E). $\Delta U_{\rm cond}$ is never defined in the text, which writes $\Delta U$. The axis labels in `figures/fig4_escape.py:52-53` use $\Delta U_{\rm cond}$, so define the symbol in the caption.
```old
ratio of fitted Arrhenius slope to $-\Delta U_{\rm cond}$ per snapshot
```
```new
ratio of fitted Arrhenius slope to $-\Delta U_{\rm cond}$, the barrier in that condition, per snapshot
```
(+w)

The Fig. 6 caption ("drive only") is handled in [12.7].

## 9. Run-on and over-nested sentences

**Worst sentence in the paper:** `06_attribution.tex:22`, the logistic-inversion sentence. Its runner-up is `05_deadlock_physics.tex:37` (sentence 2, fixed in [4.1]).

**[9.1] `paper/sections/06_attribution.tex:22`** (high, E). Five clauses with nested parentheses. "with intervals […]" dangles. "\RunNOneUnresNoise--\RunNOneUnresOrca" prints "3–4", which reads as uncertainty when it means two separate counts.
```old
from C3 RVO2); its two seed halves overlap at $J=\RunNOneJNoiseNoise$, as much as noise and ORCA do (\RunNOneJNoiseOrca; independent sets \RunNOneJNoiseOrcaIndep, $p=\RunNOneJNoiseOrcaP$), with intervals [\RunNOneJNoiseOrcaLo, \RunNOneJNoiseOrcaHi] because only \RunNOneUnresNoise--\RunNOneUnresOrca\ snapshots stay unresolved.
```
```new
from C3 RVO2). Its two seed halves overlap at $J=\RunNOneJNoiseNoise$, as much as noise and ORCA do (\RunNOneJNoiseOrca; independent sets \RunNOneJNoiseOrcaIndep, $p=\RunNOneJNoiseOrcaP$). Both intervals are [\RunNOneJNoiseOrcaLo, \RunNOneJNoiseOrcaHi] because only \RunNOneUnresNoise\ (noise) and \RunNOneUnresOrca\ (ORCA) snapshots stay unresolved.
```
(The noise–noise interval is also [0.00, 1.00], so "Both" is correct.)

**[9.2] `paper/sections/01_introduction.tex:14`** (low, E). Three clauses chained by two semicolons.
```old
because many mechanisms can reproduce one observable; this is the equifinality problem
```
```new
because many mechanisms can reproduce one observable. This is the equifinality problem
```

**[9.3] `paper/sections/06_attribution.tex:48`** (med, E). Four commas, and "whose" could refer to the solver or to the mode. The split below keeps the claim (the scope of "corrected-forward" should be checked against `make_table4.py`'s decision C64).
```old
Each conference finding is judged on the model the conference ran, the published ORCA solver, here in the corrected-forward mode, whose open geometries have no wall leaks; RVO2 is the solver check (Table~\ref{tab:conference}).
```
```new
Each conference finding is judged on the model the conference ran, with the published ORCA solver and RVO2 as the solver check (Table~\ref{tab:conference}); the open geometries run in the corrected-forward mode, which has no wall leaks.
```

**[9.4] `paper/sections/06_attribution.tex:48`** (med, E). A comma splice of three findings, with no visible link between "C4 ran with RVO2 only" and its neighbours.
```old
TTC removes only shorter contacts; C4 ran with RVO2 only, and C2 carries the finding without ORCA.
```
```new
TTC removes only these shorter contacts, and C2 shows it without ORCA; C4 ran with RVO2 only.
```

**[9.5] `paper/sections/09_conclusions.tex:3`** (low, E). The second sentence of the conclusion carries three findings.
```old
where a member reaches the end of a jamb segment; contact arches break within
```
```new
where a member reaches the end of a jamb segment. Contact arches break within
```

**[9.6] `paper/sections/06_attribution.tex:48`** (low, T). The 60-word "Rerun with …" sentence ends in ", yet …, with either solver."
```old
$p=\EelevenCFourVsCOneP$), yet no overlap under any intervention lasts 0.1\,s, with either solver.
```
```new
$p=\EelevenCFourVsCOneP$). With either solver, no overlap under any intervention lasts 0.1\,s.
```

**[9.7] `paper/sections/05_deadlock_physics.tex:20`** (low, T, +w). One sentence lists three results joined by commas.
```old
(\EsevenBallTwoK\ at $0.02$\,m), on the jambs alone ($B_{w,\rm edge}$) to \EsevenBjambK\
```
```new
(\EsevenBallTwoK\ at $0.02$\,m). On the jambs alone ($B_{w,\rm edge}$) it lifts completion to \EsevenBjambK\
```

**[9.8] `paper/sections/07_validity.tex:10`** (low, E, +w). "at local mean speed below 0.3 m/s" attaches to "neighbours", and "its standard deviation" has no clear referent. Check the meaning against `experiments/E10/analyze.py`.
```old
relative to the mean of its neighbours within 0.74\,m at local mean speed below 0.3\,m/s; the velocity fluctuation is the root mean square over both components of its standard deviation.
```
```new
relative to the mean of its neighbours within 0.74\,m, at times when the local mean speed is below 0.3\,m/s; the velocity fluctuation is the standard deviation of this relative velocity, root-mean-squared over both components.
```

## 10. Aphoristic paragraph endings

Count: 5. The paper's limit is 2 to 3, so this is borderline. Keep the one in §9 ("A mechanism claim needs a probe of the mechanism, applied to the same deadlocks as the paradigm."), which closes the paper and earns its place. Change the others:
- `01_introduction.tex:12`: see [1.1].
- `07_validity.tex:19` ("…whose deadlocks are not human behaviour at this width."): see [4.3].
- `06_attribution.tex:45` (": at $n=\PairN$ the rate is a weak calibration target."): acceptable, because it states a measured consequence. Keep it.
- **[10.1] `paper/sections/06_attribution.tex:48`** (med, E). The gnomic one-liner is also wrong against Table 4, which marks the arch and paradigm findings *revised*, not withdrawn.
```old
The mechanism findings do not survive.
```
```new
The mechanism findings are withdrawn or revised.
```

## 11. Process-record and internal-code leakage

**[11.1] `paper/sections/05_deadlock_physics.tex:41`** (low, T: a confessional aside; the competing convention is open disclosure, which some reviewers value)
```old
so its computed path is not the dynamical route (cause unknown).
```
```new
so its computed path is not the dynamical route.
```

**[11.2] `paper/sections/04_signatures.tex:35`** (low, E). "noise cells" and "dedicated runs" are project jargon.
```old
in dedicated runs (median \TthreeCellsMedian\ over the \TthreeCells\ noise cells of the escape experiments)
```
```new
in separate runs (median \TthreeCellsMedian\ over the \TthreeCells\ noise settings of the escape experiments)
```

**[11.3] `experiments/tables/make_table4.py:185`** (low, E). "stored computation" is project-record wording. The body (§6.4) says "No computation reproduces".
```old
"no stored computation gives them", "---"),
```
```new
"no computation reproduces them", "---"),
```
**[11.4] `experiments/tables/make_table4.py:171`** (low, E). The same wording, for consistency.
```old
"withdrawn", "no code reproduces them; replaced by Table~\\ref{tab:matched}",
```
```new
"withdrawn", "no computation reproduces them; replaced by Table~\\ref{tab:matched}",
```

**[11.5] `paper/sections/10_back_matter.tex:3`** (low, T). "again" narrates process.
```old
judge every conference finding again;
```
```new
judge every conference finding;
```

No internal run IDs (N1–N6, E2–E11, fix codes) appear in rendered text. The `% Budget … (C54)` comments do not render.

## 12. Terminology and notation drift

| Concept | Names used (where) | Recommend |
|---|---|---|
| ΔU/k_BT_eff | $\Delta U/k_BT_{\rm eff}$ (§4.1 T-class, §5.2, §5.3, §8); $\beta_{\rm ref}$ (Fig. 5, §6.1, Table 3) but **β never defined**; $\Delta U_{\rm cond}/k_BT_{\rm eff}$ (Fig. 4) | define β at Eq. (10) [12.1] |
| saved deadlock state | "frozen deadlock" (abstract, §1 ×2, §2 ×2, §9, back matter, Table 2), "frozen state" (§2:4), "snapshot" (§3 onward), "deadlock snapshot" (§4:5); "frozen" also means *frozen densities* (§4, §5.3, §8) | define once [12.6] |
| ORCA's drive term | "drive part" (§3, §1, §9), "rest drive" (§3, abstract, §5.1), "ORCA's drive"/"its drive"/"the drive"/"drive alone" (§6.1, §6.3), "drive only" (Fig. 6), "rest drive alone" (Table 4) | "drive part" for the quench intervention; "rest drive" for the push at rest [12.7] |
| lone trap | "lone trap", "lone-agent trap" (§1:19, §5.1 heading), "lone wall-law trap" (Table 4) | "lone trap" (G1) [7.1], [12.8] |
| jamb-only short range | $B_{w,\rm edge}$, "short-range jamb (wall) law" (abstract, §8), "jamb range reduced to" (§7), "short jambs" (Table 4), "$0.04$\,m below" (§5.3:46) | $B_{w,\rm edge}$ (G4) [12.9] |
| symbol k | SFM contact stiffness $k$ (Eq. 3); Weibull shape $k$ (§4.3:42) | drop "k=" for Weibull [12.3] |
| symbol τ | relaxation time $\tau_i$/$\tau$ (Eq. 2, Eq. 11); time to collision $\tau$ (§2:4) | $\tau_{ij}$ in §2 [12.4] |
| symbol g | goal $\mathbf g$; ramp $g(x)$ (Eq. 3); peak wall force $g_{\max}(r)$ (§5.1, §8) | rename to $f_{\max}$ [12.5] |
| time to free | "time to free" (§1, §4, §6), "times to freeing" (§3:50), "time to completion" (§6.2), "escape times" (§5.2), "quench passage time" (§5.3) | "time to free" in §3 [12.11] |
| σ₅₀ | "half-completion noise level" (§3), "noise amplitude" (§5.2:43), "noise level for half completion" (§6.4) | "noise level" [12.12] |
| ν | "attempt frequency" (§2:10), "attempt rate" (§5.2, §6.2, §8) | "attempt rate" [12.13] |
| N6 energy | "the work" (§5.3:50), never defined | name it [16.4] |
| equal temperature | "every agent at the blocker's $k_BT_{\rm eff}$" and "at equal temperatures" (§5.2:39) | tie them [13.4] |
| bias side | "lower member" (Table 3), "upper member" (§6.3), "member on the favoured side" (§5.3) | fine; no change |

**[12.1] `paper/sections/04_signatures.tex:35`** (med, E, +w). β is used from Fig. 5 onward but never defined. GLOSSARY G4 requires the definition at Eq. (10).
```old
For activated escape, $\lambda\propto\exp(-\Delta U/k_BT_{\rm eff})$, and
```
```new
For activated escape, $\lambda\propto\exp(-\beta)$ with $\beta\equiv\Delta U/k_BT_{\rm eff}$, and
```

**[12.2]** Fig. 4: see [8.5].

**[12.3] `paper/sections/04_signatures.tex:42`** (low, E). $k$ is already the contact stiffness.
```old
(Weibull shape $k=1$)
```
```new
(Weibull shape 1)
```

**[12.4] `paper/sections/02_background.tex:4`** (low, E). τ is the relaxation time everywhere else.
```old
the predicted time to collision $\tau$ and falls off as $\tau^{-2}$
```
```new
the predicted time to collision $\tau_{ij}$ and falls off as $\tau_{ij}^{-2}$
```

**[12.5]** (low, T). $g$ names the goal, the ramp and the wall-force peak. Replace every `g_{\max}` with `f_{\max}` in `paper/sections/05_deadlock_physics.tex` (lines 10, 12, 14) and `paper/sections/08_discussion.tex` (line 7). This is a replace-all of the literal string `g_{\max}`, which occurs nowhere else; the figure scripts do not use it. The competing convention is to keep $g$, which is acceptable if the authors prefer it.

**[12.6] `paper/sections/03_model.tex:48`** (med, E, +w). "frozen deadlock" is used from the abstract onward but never defined, and it collides with "frozen densities".
```old
and its state is saved as a snapshot.
```
```new
and its state is saved as a snapshot, a frozen deadlock.
```

**[12.7] ORCA drive naming** (med, E, +w for about 8 words in total). Apply each of the following:
- `paper/sections/06_attribution.tex:19`
```old
At the lone keystone ORCA's drive alone frees
```
```new
At the lone keystone ORCA's drive part alone frees
```
- `paper/sections/06_attribution.tex:28`
```old
full ORCA frees fewer blockers than its drive,
```
```new
full ORCA frees fewer blockers than its drive part,
```
- `paper/sections/06_attribution.tex:28`
```old
against \CtwsixDriveFreed\ for its drive;
```
```new
against \CtwsixDriveFreed\ for its drive part;
```
- `paper/sections/06_attribution.tex:28`
```old
cancels on average \StHeldCancel\ of the drive
```
```new
cancels on average \StHeldCancel\ of the drive part
```
- `paper/sections/06_attribution.tex:42`
```old
drive alone \PairDriveFreed), and it acts against the drive: full RVO2 ORCA frees fewer than its drive
```
```new
drive part alone \PairDriveFreed), and it acts against the drive part: full RVO2 ORCA frees fewer than its drive part
```
- `paper/sections/06_attribution.tex:13` (Fig. 6 caption)
```old
(drive only dashed,
```
```new
(drive part dashed,
```
- `experiments/tables/make_table4.py:166`
```old
lambda: f"rest drive alone frees ORCA's lone keystones "
```
```new
lambda: f"drive part alone frees ORCA's lone keystones "
```
("with ORCA's drive added" at `06:19` is fixed in [16.1].)

**[12.8] Lone trap naming** (low, E)
- `paper/sections/01_introduction.tex:19`
```old
a lone-agent trap set by the wall force
```
```new
a lone trap set by the wall force
```
- `experiments/tables/make_table4.py:174`
```old
lambda: f"lone wall-law trap ({frac('CriterionAgree', 'CriterionN')});
```
```new
lambda: f"lone trap ({frac('CriterionAgree', 'CriterionN')});
```

**[12.9] Jamb range naming** (med, E). "short jambs" is wrong: the jambs are not short, the wall range is.
- `experiments/tables/make_table4.py:177`
```old
(default walls); short jambs "
```
```new
(default walls); $B_{{w,\\rm edge}}$ "
```
(The string sits inside an f-string, hence `{{ }}`.)
- `paper/sections/05_deadlock_physics.tex:46` (low, E, GLOSSARY G4: "$B_w=0.04$" must not name the jamb-only variant)
```old
(wall force for $B_w=0.08$\,m above the axis, $0.04$\,m below, where the lower member stands)
```
```new
(wall force for the default $B_w$ above the axis and for $B_{w,\rm edge}$ below, where the lower member stands)
```

**[12.10]** The repeated J value in §6.2 is handled in [14.1].

**[12.11] `paper/sections/03_model.tex:50`** (low, E)
```old
times to freeing Kaplan--Meier estimates
```
```new
times to free Kaplan--Meier estimates
```

**[12.12] `paper/sections/05_deadlock_physics.tex:43`** (low, T)
```old
half complete at noise amplitude
```
```new
half complete at noise level
```

**[12.13] `paper/sections/02_background.tex:10`** (low, T)
```old
and $\nu$ an attempt frequency
```
```new
and $\nu$ an attempt rate
```

Glossary sweep: there are no instances of "arm", "held out", "pre-registered", "endpoint", "trial", "equivalence margin", "fold" in the $b_f$ sense, "collective" outside "collective activated escape", or "frozen" for the pinned condition. "1.5-fold" (`04:35`) is generic and kept. "completion rate" in §1:12 refers to whole-run completion and is kept; §9:3 is fixed in [13.9].

## 13. Numbers and internal consistency

**[13.1] σ₅₀: one quantity, two intervals, two verdicts** (high, E)
- §5.2:43 reports the published-reproduction σ₅₀ = `\EfiveASigmaFifty` [`\FixAsixSigFiftyPubClLo`, `\FixAsixSigFiftyPubClHi`] = 0.045 [0.041, 0.049] and says the conference 0.049 "lies at the upper edge of both".
- Table 4 (`make_table4.py:162`) prints 0.045 [`\EfiveASigmaFiftyLo`, `\EfiveASigmaFiftyHi`] = [0.042, 0.047].
- §6.4:48 says it "lies above the new interval".

Use the profile-likelihood interval that §3 declares, in both places:
- `experiments/tables/make_table4.py:162`
```old
{ci('EfiveASigmaFiftyLo', 'EfiveASigmaFiftyHi')}
```
```new
{ci('FixAsixSigFiftyPubClLo', 'FixAsixSigFiftyPubClHi')}
```
- `paper/sections/06_attribution.tex:48`
```old
The printed noise level for half completion lies above the new interval.
```
```new
The printed noise level for half completion lies at the upper edge of the new interval.
```
Author ruling needed: with 0.049 inside the interval, Table 4's status "revised" for σ₅₀ should be rechecked.

**[13.2] N6 exponents overstate precision** (med, E). `05:50` prints "exponent 1.000 … 2.000" next to "−0.16" and the references "0.5 and 1.5". In `paper/registry/runs.yaml`, change `fmt: "{:.3f}"` to `fmt: "{:.2f}"` for `RunNSixDistSlopeMed` (line 136) and `RunNSixWSlopeMed` (line 148). The values then print 1.00 and 2.00.

**[13.3] `paper/sections/05_deadlock_physics.tex:39`, the Weibull sentence** (med, E). "exceeds 1 only when pooled" is contradicted two sentences later by the pinned shape from 10 s, `\FixAthreeShapeFrozenTen` [1.01, 1.17], which also excludes 1. "A lag fits better" has no comparand now that three shapes are listed. Apply both fixes:
```old
The Weibull shape of the escape times exceeds 1 only when pooled over the three conditions, \EfourWeib\
```
```new
Pooled over the three conditions, the Weibull shape of the escape times is \EfourWeib\
```
```old
A lag fits better: shape
```
```new
A lag fits the pooled times better: shape
```

**[13.4] `paper/sections/05_deadlock_physics.tex:39`, the N3 sentence** (med, E, +w). The condition is not stated (N3 reruns the *full* condition, per `data/derived/N3_analysis.json`). "the median ratio" follows a sentence about the pooled *slope*. The sentence is also not tied to "at equal temperatures" in the next sentence.
```old
With every agent at the blocker's $k_BT_{\rm eff}$ (\RunNThreeRunsN\ runs on \RunNThreeSnapN\ snapshots), the median ratio is
```
```new
In the full condition at equal temperatures, every agent at the blocker's $k_BT_{\rm eff}$ (\RunNThreeRunsN\ runs on \RunNThreeSnapN\ snapshots), the median slope ratio is
```
(9 snapshots against 8 fits: a fit needs at least 3 events at every level. The same rule gives 8 of 10 in E4 full and is unstated there too. Optionally add "fits need three escapes per level" once at §5.2:39's first "fits".)

**[13.5] `paper/sections/01_introduction.tex:18`** (med, E, +w). The claim overreaches the lemma. Prop. 1 needs $\mathbf v\cdot\mathbf G\le0$ and does not cover ORCA's constraint part.
```old
no force term vanishing at rest can resolve a deadlock of the noise-free model
```
```new
no dissipative force term vanishing at rest can resolve a deadlock of the noise-free model
```

**[13.6] `paper/sections/10_back_matter.tex:3`** (med, E). "four rerun for this paper" contradicts "every carried-over result was recomputed" and the new σ₅₀ and noise runs.
```old
of the four rerun for this paper,
```
```new
of the four rerun in Sect.~\ref{sec:conference},
```

**[13.7] `paper/sections/08_discussion.tex:16`** (med, E, +w). "100 per run" is contradicted by §6.4 (50 agents, or 100 per stream) and §7 (matched to the human runs).
```old
Agents are two-dimensional discs, 100 per run,
```
```new
Agents are two-dimensional discs, 100 per room run,
```

**[13.8] `paper/sections/08_discussion.tex:13`** (med, E). "the pair standoff [is set] by the end of the jamb segment" conflates the standoff's existence (which needs $B_{w,\rm edge}$, §8 Limitations) with the loss of its minimum. Use the glossary phrase.
```old
the pair standoff by the end of the jamb segment, where its minimum is lost.
```
```new
the loss of the pair minimum at $b_f$ by the end of the jamb segment.
```

**[13.9] `paper/sections/09_conclusions.tex:3`** (low, E). GLOSSARY G5: the matched quantity is a rate (freed fraction or completion fraction).
```old
a matched completion rate leaves the attribution open
```
```new
a matched rate leaves the attribution open
```

**[13.10] `paper/sections/06_attribution.tex:22`** (low, E). Subject–object mismatch: a level is not near a rate.
```old
the grid level nearest C3 RVO2's rate,
```
```new
the grid level whose rate is nearest C3 RVO2's,
```

**[13.11]** (low, E). In §6.1:22 the same kind of quantity (Δ freed fraction against ORCA) prints as "−0.01 [−0.09, +0.07]" (`FixAtwoLoneDelta*`, `{:+.2f}`) and as "−0.018 [−0.074, 0.044]" (`RunNOneDiff*`, `{:.3f}`). In `paper/registry/core.yaml` lines 1513/1518/1523, change `"{:+.2f}"` to `"{:.2f}"`. In `paper/registry/runs.yaml` lines 43/47/51, change `"{:.3f}"` to `"{:.2f}"`.

**[13.12] `paper/sections/06_attribution.tex:31`** (low, E). "median" of what?
```old
(median \EsixPairedDelay\,s)
```
```new
(median lead \EsixPairedDelay\,s)
```

**[13.13]** (low, E, source hygiene). The abstract, §1:21, §9:3 and `make_table4.py:190` print the CroMa flow ratio from `\EtenCSigFlowRatio`/`\EtenCThreeFlowRatio` (bootstrap). §7:16 prints the same ratio from `\FixAsevenCSigFlowRatio`/`\FixAsevenCThreeFlowRatio` (t-based, the method §7 states). The point values agree today (0.40 and 0.59) but the intervals do not ([0.53, 0.67] against [0.49, 0.70] for C3). Point all four at the `\FixAseven…` macros so that a regeneration cannot split them.

**[13.14] `paper/sections/05_deadlock_physics.tex:16`** (low, E). "the seventh" hard-codes `\CriterionNegMargin`=7 into prose.
```old
and the seventh is such a pair with two more agents away from the door.
```
```new
and the remaining one is such a pair with two more agents away from the door.
```

## 14. Structural and framing problems

**[14.1] `paper/sections/06_attribution.tex:31`, ordering** (med, E). The N2 evidence for "identity does not separate them" comes after the sentence that has already moved on to what does separate them. The 0.41 is the Table 3 $J$ restated as if it were new. The fix reorders the sentences and labels the value, at about the same length.
```old
As at the lone trap, identity does not separate them; time to completion and the final state do. Two independent noise streams on the same spawns overlap at $J=\RunNTwoJNoiseNoise$ [\RunNTwoJNoiseNoiseLo, \RunNTwoJNoiseNoiseHi], as much as noise and C3 RVO2 do (\RunNTwoJOrcaOld\ and \RunNTwoJOrcaNew\ for the two streams), against \RunNTwoJOrcaOldIndep--\RunNTwoJNoiseNoiseIndep\ for independent sets.
```
```new
As at the lone trap, identity does not separate them: two independent noise streams on the same spawns overlap at $J=\RunNTwoJNoiseNoise$ [\RunNTwoJNoiseNoiseLo, \RunNTwoJNoiseNoiseHi], as much as noise and C3 RVO2 do (\RunNTwoJOrcaOld, the $J$ of Table~\ref{tab:matched}, and \RunNTwoJOrcaNew\ for the two streams), against \RunNTwoJOrcaOldIndep--\RunNTwoJNoiseNoiseIndep\ for independent sets. Time to completion and the final state separate them.
```

**[14.2] `paper/sections/08_discussion.tex:4`, restatement** (med, T: discussion recaps are conventional, but the paper is at its page limit; this saves about 20 words). Delete the two sentences that only repeat §6.3:45 and §4:5.
```old
The bias match holds on its calibration snapshots by construction. On the same deadlocks
```
```new
On the same deadlocks
```
```old
handedness and identity at the pair. Identity separates only there, where both resolvers are deterministic. The rest-drive push
```
```new
handedness and identity at the pair. The rest-drive push
```

**[14.3] `paper/sections/07_validity.tex:10`, redundant statistics** (low, T, saves words). Student-$t$ intervals for CroMa means and the 95% level are already stated in §3:50.
```old
Means carry Student-$t$ 95\% intervals over runs, flow ratios $t$-based intervals on the log scale.
```
```new
Flow ratios carry $t$-based intervals on the log scale.
```

**[14.4]** (low, T, no change proposed). The CroMa result appears in nearly the same words in the abstract, §1 (contribution 4), §9 and Table 4. The introduction bullet adds the gap result and a pointer, and §9 is the conclusion, so this is acceptable LNCS practice. Flagged only so the authors know.

**[14.5]** (low, T). `07_validity.tex:16`, "No agent leaves the walkable area in any run." is a sanity check placed in the middle of the results. It reads better at the end of the method paragraph (:10). Moving it is optional.

Checked and in order: the conclusion exists and does not end on limitations. The recommendation is stated (§8 checklist). The novelty claim (§2:16) is hedged to "we have not found". No results sit in Background apart from [3.1].

## 15. Spelling and convention consistency

**[15.1] `paper/sections/05_deadlock_physics.tex:14`** (high visibility, E). There is a capital after a semicolon.
```old
stuck alone; Adding ORCA's rest drive
```
```new
stuck alone; adding ORCA's rest drive
```

**[15.2] `paper/sections/06_attribution.tex:31`** (low, E). The sentence opens with a numeral (`\EsixCThreeFailMoving` prints "54").
```old
\EsixCThreeFailMoving\ of C3 RVO2's failures still move at 600\,s,
```
```new
Of C3 RVO2's failures, \EsixCThreeFailMoving\ still move at 600\,s,
```

**[15.3] Serial comma** (low, T). The paper's convention is no serial comma (about 30 lists, for example "replay, time-step dependence, time to free or handedness"). There are two exceptions:
- `paper/sections/00_abstract.tex:3`
```old
to the paradigm's rate, and compares them
```
```new
to the paradigm's rate and compares them
```
- `paper/sections/03_model.tex:9`
```old
C3 adds ORCA, and C4 adds
```
```new
C3 adds ORCA and C4 adds
```

**[15.4] `paper/sections/06_attribution.tex:28`** (low, E). The test is named "Fisher exact $p$" at :48 and "Fisher $p$" here.
```old
(Fisher $p=\StPairFisherP$)
```
```new
(Fisher exact $p=\StPairFisherP$)
```

The spelling is British throughout (behaviour, realisations, discretised, characterised, modelling, coloured, centre, artefacts, neighbour). No American forms were found. "Sect."/"Sects." and "Eq."/"Eqs." are consistent. The minus signs in intervals are in math mode, apart from [13.11]'s "+".

## 16. Anything else

**[16.1] `paper/sections/06_attribution.tex:19`** (med, E). "It" follows "Replays … reproduce C3 RVO2", so the referent is unclear. The margin also uses the *rest* drive.
```old
It fails where the rest-state margin with ORCA's drive added stays positive
```
```new
C3 RVO2 fails where the rest-state margin with ORCA's rest drive added stays positive
```

**[16.2] `paper/sections/06_attribution.tex:25`** (med, E). "(with intercept −0.xx […])" reads as the value of the intercept, but it is the slope fitted with an intercept.
```old
(with intercept \FixAthreeOLSSlope\
```
```new
(fitted with an intercept, \FixAthreeOLSSlope\
```

**[16.3] `paper/sections/05_deadlock_physics.tex:39`** (med, E). "partly build the slope in" is opaque. Check the meaning: the free intercepts (the fitted attempt rates) absorb part of the slope.
```old
and the fitted attempt rates partly build the slope in.
```
```new
and the free intercepts, the fitted attempt rates, absorb part of the slope.
```

**[16.4] `paper/sections/05_deadlock_physics.tex:50`** (med, E). "it" has no referent (the loss? the saddle?), and "the work" is never defined. If the work is the minimum–saddle energy difference, use the following:
```old
In the \RunNSixFoldN\ cases where continuation locates it, the minimum--saddle distance scales with $\delta=1-b/b_f$ with exponent \RunNSixDistSlopeMed\ and the work with \RunNSixWSlopeMed,
```
```new
In the \RunNSixFoldN\ cases where continuation locates the saddle, the minimum--saddle distance scales with $\delta=1-b/b_f$ with exponent \RunNSixDistSlopeMed\ and the barrier between them with \RunNSixWSlopeMed,
```

**[16.5] `paper/sections/05_deadlock_physics.tex:55`** (low, E). "while" could mean concurrent or contrasting.
```old
and at the default drive none forms, while all \RunNFiveDefaultN\ runs deadlock
```
```new
and at the default drive none forms and all \RunNFiveDefaultN\ runs deadlock
```

**[16.6] `paper/sections/09_conclusions.tex:3`** (med, E, +w). "fails on overlapping deadlocks" does not say what overlaps with what.
```old
noise fails on overlapping deadlocks but differs in
```
```new
noise and ORCA fail on overlapping sets of deadlocks, but noise differs in
```

**[16.7] `paper/sections/05_deadlock_physics.tex:39`** (low, E). The bare numbers after "exceptions:" do not say what they are.
```old
(exceptions: \EfourNonCoverA\ full;
```
```new
(exceptions: ratio \EfourNonCoverA\ full;
```

**[16.8] `paper/sections/06_attribution.tex:25`** (low, E). "step" is ambiguous next to Δt.
```old
frees the same snapshots at every step.
```
```new
frees the same snapshots at every time step.
```

**[16.9] `paper/sections/06_attribution.tex:45`** (low, E, +w). "a control that only copies ORCA's rate" is undefined. Per `data/derived/fix_a2.json` it is a control that reproduces ORCA's fit-half rate and is otherwise unrelated.
```old
as widely as a control that only copies ORCA's rate
```
```new
as widely as a control that reproduces ORCA's fit-half rate and nothing else
```

Also checked: jargon before definition ("keystone test", "quench", "library", "pinned", "rest-drive push"; each is defined at or before first use, apart from "frozen deadlock" [12.6] and β [12.1]), metaphors ("agitated", "slow creep"; both readable), and buried subjects.

---

## Count per category

| # | Category | Entries with a fix | Kept or noted only |
|---|---|---|---|
| 1 | Rhetorical negation | 1 | 5 kept, 1 mirrored set (fixed in 14.2) |
| 2 | Significance announcements | 0 | none found |
| 3 | Section announcements | 3 | 1 restated paragraph (§8, fixed in 14.2) |
| 4 | Trailing appositives / dangling | 4 (+1 merged into 9.6) | 1 kept |
| 5 | Softening adverbs | 4 | 3 author queries, 4 kept |
| 6 | "What" / clefts | 0 | none found |
| 7 | Headings and leads | 6 | — |
| 8 | Captions | 3 (8.1, 8.4, 8.5) | 2 accepted overruns (Fig. 2, Table 3) |
| 9 | Run-ons | 8 | worst: 9.1 |
| 10 | Aphoristic endings | 1 (+2 cross-referenced) | 5 counted, §9 kept |
| 11 | Process leakage | 5 | — |
| 12 | Terminology and notation | 12 (12.7: 7 hunks, 12.8: 2, 12.9: 2) | table of 13 concepts |
| 13 | Numbers and consistency | 14 | — |
| 14 | Structure | 3 | 2 noted |
| 15 | Conventions | 4 (15.3: 2 hunks) | British spelling clean |
| 16 | Other | 9 | — |
| | **Total** | **77 entries** (about 90 string hunks) | |

Severity: high 3 (13.1, 9.1, 15.1). Med 27. The rest are low. Fixes that add words (+w): 4.1, 5.3, 5.4, 8.5, 9.7, 9.8, 12.1, 12.6, 12.7, 13.4, 13.5, 13.7, 16.6, 16.9, about 75 words in total. Fixes 3.1, 3.2, 14.2, 14.3, 11.1 and 5.2 remove about 70 words, so the net page impact is about zero.
