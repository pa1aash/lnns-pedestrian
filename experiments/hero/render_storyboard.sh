#!/bin/sh
# Render the three storyboard previews one after another (one Blender process at a time,
# two CPU threads, Metal GPU when available), then the greyscale / colour-vision checks.
# Low resolution and samples only: these are composition previews, not the final render.
set -e
cd "$(dirname "$0")/../.."
OUT=figures/hero/storyboard
mkdir -p "$OUT"
LOG="$OUT/render_log.txt"
: > "$LOG"
T=$(mktemp)
for L in A B C; do
  /usr/bin/time -l blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- \
    --layout "$L" --width-px 900 --samples 32 --out "$OUT/option_$L.png" 2> "$T" | grep '^HERO' | tee -a "$LOG"
  grep -E ' real |peak memory footprint' "$T" | sed "s/^/option_$L /" | tee -a "$LOG"
done
rm -f "$T"
/Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python experiments/hero/check_previews.py
