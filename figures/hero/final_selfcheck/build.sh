#!/bin/sh
# usage: build.sh  (from repo root) overlay + compile + CVD variants for the 900 px self-check
D=figures/hero/final_selfcheck
python3 tools/make_fig1_overlay.py --overlay $D/sc.json --out $D/sc_overlay.tex --png $D/sc.png | cut -c1-600
pdflatex -interaction=nonstopmode -halt-on-error -output-directory $D $D/sc.tex > /dev/null || { echo LaTeX failed; exit 1; }
pdftoppm -png -r 300 -singlefile $D/sc.pdf $D/sc_300
.venv/bin/python experiments/hero/cvd_variants.py $D/sc_300.png > /dev/null
