.PHONY: paper figures clean

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex

figures:
	@for f in figures/fig*.py; do [ -e "$$f" ] || continue; echo "== $$f"; (cd figures && python3 $$(basename $$f)) || exit 1; done

clean:
	cd paper && latexmk -C
