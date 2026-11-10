# Submission notes

## Main differences from the conference version (submission form or cover letter)

This article extends our conference paper (Gang and Veluri, SIMULTECH 2026) with new physics of narrow-exit deadlocks in the social force model: an exact criterion for an agent held alone at the door edges and the critical width it brackets, a second deadlock type (a pair standoff at the jamb faces whose minimum is lost non-smoothly at a jamb segment end), activated escape of the lone trap over barriers computed from the model's energy landscape, and the absence of persistent contact arches. It attributes deadlock resolution to mechanism: noise and a lateral bias tuned to ORCA's rate reach that rate through activated escape and a lateral tilt, whereas ORCA acts through its rest drive, and the legacy ORCA solver's sign defect is identified. It introduces a screening protocol of five physically defined mechanism classes and probes on frozen deadlocks, implemented in the open framework deadlock-screen, and compares the model variants with the CroMa bottleneck experiments. These results supersede the conference version's rate-level reading of which steering mechanism resolves deadlocks.

## Keywords (five)

Pedestrian dynamics · Social force model · Reciprocal collision avoidance · Activated escape · Mechanism screening

## PRIMORIS checklist

- [ ] Single-file LaTeX source: `make submission` writes `paper/submission/` (one self-contained `main.tex` with every `\input` and the bibliography inlined, the figures, the unmodified `llncs.cls` and `splncs04.bst`); the folder compiles on its own.
- [ ] Figures: Figs 1–8 as vector PDF (Fig. 1 a 600 dpi PNG with matching metadata) and the protocol figure as TikZ inside the source; alt text in `figures/ALT_TEXT.md`.
- [ ] Licence to Publish: signed by the corresponding author on behalf of both authors.
- [ ] Corresponding author: Palaash Gang (marked in the author block).
- [ ] Author item 1: acknowledgements text (currently `\pending`).
- [ ] Author item 2: Disclosure of Interests text (currently `\pending`).
- [ ] Author item 3: Zenodo DOI for the deadlock-screen archive in the Data and Code Availability statement (currently `\pending`).
- [ ] Final build with `\finaltrue` in `paper/main.tex` (any remaining `\pending` then stops the build).

## [NEEDS PALAASH]

- Write the acknowledgements and the Disclosure of Interests.
- Create the Zenodo archive of github.com/pa1aash/deadlock-screen and supply the DOI.
- Section 6.4 (velocity coupling of ORCA) and its Table 3 row hold `\pending` results until session V delivers them; the page budget reserves 0.4 page for them.
- Confirm with the volume editors that the page limit is 24 pages including references.
