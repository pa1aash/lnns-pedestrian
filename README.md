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
| `figures/` | matplotlib style (`style.mplstyle`), helpers (`common.py`), one `fig*.py` per figure; `fig1_hero.png` is a committed Blender render (see Reproduce) |
| `code/` | simulator (`sim/`) and its test suite (`tests/`) |
| `experiments/` | experiment drivers (`E*/`, `BAR/`, `arch/`), shared helpers (`lib/`), the run queue (`queue.yaml`), table scripts (`tables/`), the Fig. 1 render scripts (`hero/`) and the seed table (`SEEDS.md`) |
| `data/params/` | model parameters (`model.yaml`) |
| `data/E*/` | per-run results of each experiment (JSON Lines) and frozen deadlock snapshots |
| `data/derived/` | analysis outputs read by the numbers, tables and figures |
| `data/ext/croma/` | CroMa 2021 human bottleneck trajectories (0.8 m exit runs), CC BY 4.0 |
| `tools/` | build helpers: `make_numbers.py`, `make_submission.sh`, `page_map.py`, Fig. 1 overlay and figure checks |
| `.github/` | CI workflows: `paper.yml` builds the PDF, `tests.yml` runs the simulator tests |
| `plan/` | study plan, changelog, venue requirements |
| `ref/` | conference version |
| `reports/` | batch reports |

## Build

Requires a TeX Live installation with `latexmk` and the `cm-super` fonts, Python 3 for the virtual environment, a LaTeX installation with `type1cm` for the figures, and poppler's `pdffonts` and `pdftoppm`. `make submission` also needs `latexpand` (a TeX Live script; here installed in `~/Library/texmf/scripts`).

```
make venv        # creates .venv from requirements-figures.txt (once; the targets below also create it if missing)
make paper       # regenerates paper/numbers.tex and paper/tables/*.tex with .venv, then builds paper/main.pdf
make submission  # single-file paper/submission/ (needs latexpand)
make figures     # runs every figures/fig*.py with .venv
python3 tools/page_map.py --pinned   # page usage per section
make clean
```

CI builds the PDF on every push to `main` and uploads it as an artifact.

## Reproduce

Every number, table and figure in the paper is regenerated from the per-run results committed under `data/`. The simulations that produced those results take about 164 CPU-hours (`experiments/queue.yaml`), so they are not part of the quick path below.

### 1. Requirements

- TeX Live 2024 or later with `latexmk`. A full TeX Live has everything. On BasicTeX, add the packages with
  `sudo tlmgr install latexmk cm-super type1cm pgf xcolor booktabs amsfonts latexpand`.
  The Springer class and BibTeX style ship unmodified in `paper/llncs/`, so there is nothing to install for them.
- poppler (`pdffonts`, `pdftoppm`, `pdfimages`), used by the figure checks.
- Python 3.13 (3.11 or later should work).

### 2. Python environment

```
make venv        # .venv with requirements-figures.txt (numpy, scipy, matplotlib, pyyaml, colorspacious)
make venv-sim    # adds the simulator packages to .venv (shapely, pandas, pyarrow, pytest), pinned as in CI
```

`make paper`, `make figures`, `make numbers` and `make tables` all run with `.venv/bin/python` and create `.venv` first if it is missing. `make venv-sim` is needed only for the tests and the simulations; its versions are the ones in `.github/workflows/tests.yml`, and `code/pyproject.toml` lists the looser requirements of the simulator package.

### 3. Paper, numbers and tables (about 1 minute)

```
make paper        # regenerates paper/numbers.tex and paper/tables/*.tex from data/, then builds paper/main.pdf
git status        # should list no modified files: the regenerated numbers and tables are byte-identical
```

### 4. Figures 2-8 (about 30 seconds)

```
make figures      # runs figures/fig*.py with .venv/bin/python and prints pdffonts for each figure
```

The output is pixel-identical to the committed PDFs. Only the embedded creation date differs, so `git status` shows the figure PDFs as modified.

### 5. Fig. 1

`figures/fig1_hero.png` is a committed render and is used as is; `make figures` does not rebuild it. It was rendered with Blender 5.2.2 on macOS (Metal GPU), about 2.5 minutes of render time and 3.6 GB of memory per panel (`reports/HF_REPORT.md`). To render it again:

```
PYTHONPATH=code .venv/bin/python experiments/hero/export_hero.py     # scene data, data/derived/hero/*.npz (needs make venv-sim)
PYTHONPATH=code .venv/bin/python experiments/hero/add_clearance.py
.venv/bin/python experiments/hero/make_luts.py                       # colour lookup tables
sh experiments/hero/final.sh                                         # four panels at 2882 px, 128 samples, then assembly
```

`final.sh` needs `blender` (5.2.2) on the PATH and the macOS tools `memory_pressure` and `sysctl vm.swapusage`. It waits until 3.5 GB of memory are free. If a simulation queue is running on the same machine, set `QUEUE_PID` to its process ID and the queue is paused while a failed panel is rendered again; without `QUEUE_PID` nothing is paused. The vector overlay, `figures/fig1_overlay.tex`, is regenerated byte-identically by `python3 tools/make_fig1_overlay.py`.

### 6. Single-file submission

```
make submission   # writes paper/submission/ (main.tex with everything inlined, figures/, llncs.cls, splncs04.bst)
```

The script compiles the folder on its own in a temporary directory and reports how many `\pending` items are left.

### 7. Tests (about 6 minutes)

```
make venv-sim
make -C experiments test     # pytest in code/ with .venv/bin/python
```

Expect 128 passed and 5 failed. The five failures are the bit-for-bit floating-point reference comparisons that `.github/workflows/tests.yml` deselects; they depend on the platform and the BLAS build. The regression hash (`make -C experiments regress`, about 7 s, must print `e381b49dc24acccd OK`) is checked only on the Mac where the reference was recorded, with Python 3.13 and the pinned versions above.

### 8. Simulations (not part of the quick path)

The experiment drivers are under `experiments/E*/`, and `experiments/queue.yaml` lists every step with its estimated CPU-hours. Run the queue with

```
make -C experiments queue    # uses .venv/bin/python; another interpreter can be given as PY=/path/to/python
```

The queue target uses macOS `caffeinate`. On Linux, run `PYTHONPATH=code .venv/bin/python experiments/queue.py run` instead. The queue is resumable. The run scripts of queue 3 live in `experiments/runs3/`, with the queue file `experiments/queue3.yaml`. The seed of every run is listed in `experiments/SEEDS.md`. Raw trajectories for the CroMa comparison (`data/E10/raw/`, over 50 MB) are not in git. They are archived on Zenodo (DOI to be added at submission).

## Citation

Citation metadata are in `CITATION.cff` (and `.zenodo.json` for the Zenodo archive). Until the extended version has its own DOI, please cite the conference paper above.

## Licence

Code and original content in this repository are released under the MIT licence (see `LICENSE`). Third-party material keeps its own licence: the CroMa 2021 trajectories in `data/ext/croma/` (CC BY 4.0) and the conference paper in `ref/` (CC BY-NC-ND 4.0); see the README in each folder.
