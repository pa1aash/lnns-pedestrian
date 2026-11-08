#!/bin/sh
# Render the 900 px hero mock, build the overlay, compile figures/hero/mock/fig1_mock.{pdf,png}.
# Memory gate: start only when >= 4.5 GB is free (polls every 5 min, up to 3 h). Metal GPU, Blender -t 2.
cd "$(dirname "$0")/../.."
MIN=${MIN_FREE_GB:-4.5}
free_gb() { memory_pressure | awk '/free percentage/ {gsub("%","",$5); printf "%.2f", $5 * 8 / 100}'; }
n=0
while :; do
  f=$(free_gb)
  if [ "$(echo "$f >= $MIN" | bc)" = 1 ]; then break; fi
  n=$((n + 1)); [ $n -gt 36 ] && { echo "free memory stayed below $MIN GB for 3 h" >&2; exit 1; }
  echo "free $f GB < $MIN GB: waiting 5 min" >&2; sleep 300
done
echo "free $f GB at start" >&2
blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- --width-px 900 --samples "${SAMPLES:-24}" \
  --out figures/hero/mock/fig1_hero_mock.png --overlay figures/hero/fig1_overlay.json "$@" | grep -E "HERO|WARN" || exit 1
python3 tools/make_fig1_overlay.py --png figures/hero/mock/fig1_hero_mock.png || exit 1
pdflatex -interaction=nonstopmode -halt-on-error -output-directory figures/hero/mock figures/hero/mock/fig1_mock.tex > /dev/null || { echo "LaTeX failed" >&2; exit 1; }
pdftoppm -png -r 300 -singlefile figures/hero/mock/fig1_mock.pdf figures/hero/mock/fig1_mock
echo "mock: figures/hero/mock/fig1_mock.pdf"
