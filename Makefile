.PHONY: paper figures numbers tables clean

paper: numbers tables
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex

numbers:
	python3 tools/make_numbers.py

tables:
	@for f in experiments/tables/make_*.py; do [ -e "$$f" ] || continue; echo "== $$f"; python3 $$f || exit 1; done

figures:
	@for f in figures/fig*.py; do [ -e "$$f" ] || continue; echo "== $$f"; (cd figures && python3 $$(basename $$f)) || exit 1; done

clean:
	cd paper && latexmk -C
