.PHONY: venv paper figures numbers tables clean

paper: numbers tables
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex

numbers:
	python3 tools/make_numbers.py

tables:
	@for f in experiments/tables/make_*.py; do [ -e "$$f" ] || continue; echo "== $$f"; python3 $$f || exit 1; done

figures:
	@for f in figures/fig*.py; do [ -e "$$f" ] || continue; echo "== $$f"; (cd figures && ../.venv/bin/python $$(basename $$f)) || exit 1; done

venv:
	python3 -m venv .venv && .venv/bin/pip install -r requirements-figures.txt

clean:
	cd paper && latexmk -C
