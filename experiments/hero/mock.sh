#!/bin/sh
# Hero mock v2 (900 px): render, build the overlay, compile figures/hero/mock_v2/fig1_mock_v2.{pdf,png}.
# Memory gate: start only when >= 4.5 GB is free (polls every 5 min, up to 3 h). Metal GPU, Blender -t 2.
# MOCK_OVERLAY_ONLY=1 skips the render (overlay + compile only). Production (2882 px) is not run from here.
cd "$(dirname "$0")/../.."
D=figures/hero/mock_v2
MIN=${MIN_FREE_GB:-4.5}
free_gb() { memory_pressure | awk '/free percentage/ {gsub("%","",$5); printf "%.2f", $5 * 8 / 100}'; }
if [ -z "$MOCK_OVERLAY_ONLY" ]; then
  n=0
  while :; do
    f=$(free_gb)
    if [ "$(echo "$f >= $MIN" | bc)" = 1 ]; then break; fi
    n=$((n + 1)); [ $n -gt 36 ] && { echo "free memory stayed below $MIN GB for 3 h" >&2; exit 1; }
    echo "free $f GB < $MIN GB: waiting 5 min" >&2; sleep 300
  done
  echo "free $f GB at start" >&2
  blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- --width-px 900 --samples "${SAMPLES:-24}" \
    --out $D/fig1_hero_mock_v2.png --overlay $D/fig1_overlay_v2.json "$@" | grep -E "HERO|WARN" || exit 1
fi
python3 tools/make_fig1_overlay.py --png $D/fig1_hero_mock_v2.png || exit 1
pdflatex -interaction=nonstopmode -halt-on-error -output-directory $D $D/fig1_mock_v2.tex > /dev/null || { echo "LaTeX failed" >&2; exit 1; }
pdftoppm -png -r 300 -singlefile $D/fig1_mock_v2.pdf $D/fig1_mock_v2
.venv/bin/python experiments/hero/cvd_variants.py $D/fig1_mock_v2.png > /dev/null || exit 1
python3 tools/check_fig1_labels.py $D/fig1_mock_v2.pdf $D/fig1_hero_mock_v2.png | tail -1
echo "mock v2: $D/fig1_mock_v2.pdf"
