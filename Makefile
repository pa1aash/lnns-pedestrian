.PHONY: venv venv-sim paper submission overleaf overlap figures numbers tables clean

# Python environment for figures, numbers and tables (pinned in requirements-figures.txt).
# `make venv` creates it once; figures, numbers and tables create it on first use as well.
# The stamp file is the make target because .venv/bin/python is a symlink whose mtime is the
# base interpreter's; it is renewed whenever requirements-figures.txt changes.
PY := .venv/bin/python
VENV_STAMP := .venv/.requirements-figures.stamp

paper: numbers tables
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex

submission: paper
	bash tools/make_submission.sh

# Overleaf package: one main.tex with every \input inlined and every number macro replaced by its value,
# refs.bib with the cited entries only, the figures, llncs.cls and splncs04.bst (OVERLEAF_DIR, default paper/overleaf).
OVERLEAF_DIR ?= paper/overleaf
overleaf: paper
	python3 tools/make_overleaf.py $(OVERLEAF_DIR)

overlap:
	python3 tools/overlap_check.py

venv: $(VENV_STAMP)

$(VENV_STAMP): requirements-figures.txt
	python3 -m venv .venv && .venv/bin/pip install -r requirements-figures.txt && touch $(VENV_STAMP)

# Simulator packages on top of the figures environment, pinned as in .github/workflows/tests.yml;
# used by `make -C experiments ...` (regress, test, queue) through its default PY.
venv-sim: $(VENV_STAMP)
	.venv/bin/pip install shapely==2.1.2 pandas==3.0.2 pyarrow==23.0.1 pytest==9.0.2

numbers: $(VENV_STAMP)
	$(PY) tools/make_numbers.py

tables: $(VENV_STAMP)
	@for f in experiments/tables/make_*.py; do [ -e "$$f" ] || continue; echo "== $$f"; $(PY) $$f || exit 1; done

figures: $(VENV_STAMP)
	@for f in figures/fig*.py; do [ -e "$$f" ] || continue; echo "== $$f"; (cd figures && ../$(PY) $$(basename $$f)) || exit 1; done

clean:
	cd paper && latexmk -C
