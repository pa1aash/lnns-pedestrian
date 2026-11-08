#!/bin/sh
# Run the hero render only when at least 2.5 GB of memory is free (8 GB machine shared with the
# experiment queue); wait and retry otherwise. One Blender process at a time, 2 threads, Metal GPU.
#   experiments/hero/render_safe.sh <render_hero.py args after --> ...
cd "$(dirname "$0")/../.."
free_gb() {   # "System-wide memory free percentage" x 8 GB
  pct=$(memory_pressure | awk '/free percentage/ {gsub("%","",$5); print $5}')
  echo "$pct" | awk '{printf "%.2f", $1 * 8 / 100}'
}
while :; do
  f=$(free_gb)
  if [ "$(echo "$f >= 2.5" | bc)" = 1 ]; then break; fi
  echo "free $f GB < 2.5 GB: waiting" >&2
  sleep 30
done
echo "free $f GB at start" >&2
T=$(mktemp)
/usr/bin/time -l blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- "$@" 2> "$T" | grep '^HERO'
grep -E ' real |peak memory footprint' "$T"
rm -f "$T"
