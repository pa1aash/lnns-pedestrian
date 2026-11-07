# One Matched Control Is Not Enough: Physics-Based Attribution of Deadlock Resolution in Pedestrian Steering Models

Palaash Gang (corresponding author, palaash.gang@indusschoolpune.com, ORCID 0009-0006-7448-9488) and Arjun Veluri (arjun.v@indusschoolpune.com, ORCID 0009-0001-5940-3272), Indus International School, Pune, India.

Extended version, for Springer Lecture Notes in Networks and Systems, of the conference paper cited below.

## The question

In social-force crowd simulations, agents pushing through a narrow exit can lock into deadlocks: a lone agent held at the door edge, or a pair standing off against each other. Different steering variants free the crowd at different rates. Matching one control on completion rate does not say which mechanism frees the crowd, because several distinct physical mechanisms can give the same completion rate. This work attributes deadlock resolution to its physical mechanism by comparing what each candidate mechanism predicts under a set of interventions, and checks the result against human bottleneck data.

## Conference version

Gang, P. and Veluri, A. (2026). A Diagnostic Methodology for Failure-Mode Ablation of SFM, TTC, and ORCA Pedestrian Steering Paradigms. SIMULTECH 2026, pp. 474-481. DOI: [10.5220/0015190200004094](https://doi.org/10.5220/0015190200004094). A copy and the full citation are in `ref/`.

## Layout

| path | content |
|---|---|
| `paper/` | LaTeX source (`main.tex`, `refs.bib`, generated `numbers.tex`, `tables/`); `llncs/` is Springer's unmodified template |
| `figures/` | matplotlib style (`style.mplstyle`), helpers (`common.py`), one `fig*.py` per figure |
| `code/` | simulator (added later) |
| `experiments/` | experiment definitions |
| `data/ext/croma/` | CroMa 2021 human bottleneck trajectories (0.8 m exit runs), CC BY 4.0 |
| `plan/` | study plan, changelog, venue requirements |
| `ref/` | conference version |
| `reports/` | batch reports |

## Build

Requires a TeX Live installation with `latexmk` and the `cm-super` fonts; figures also need Python 3 with matplotlib and a LaTeX installation (`type1cm`), plus poppler's `pdffonts` and `pdftoppm`.

```
make paper     # builds paper/main.pdf
make figures   # runs every figures/fig*.py
make clean
```

CI builds the PDF on every push to `main` and uploads it as an artifact.

## Licence

Code and original content in this repository are released under the MIT licence (see `LICENSE`). Third-party material keeps its own licence: the CroMa 2021 trajectories in `data/ext/croma/` (CC BY 4.0) and the conference paper in `ref/` (CC BY-NC-ND 4.0); see the README in each folder.
