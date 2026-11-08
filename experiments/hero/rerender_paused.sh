#!/bin/bash
# Re-render the four hero panels one per Blender run (-t 2, Metal GPU, tile 256) and assemble, with the experiment queue
# paused (SIGSTOP) for the duration only; always resumed (SIGCONT) on exit. Log: figures/hero/c43_render.log
cd "$(dirname "$0")/../.."
PG=$(ps -o pgid= -p 3074 | tr -d ' ')
trap 'pkill -CONT -g $PG; echo "$(date "+%F %T") queue RESUMED (SIGCONT, pgid $PG)"' EXIT
echo "$(date '+%F %T') queue PAUSED (SIGSTOP, pgid $PG), free $(memory_pressure | awk '/free percentage/ {print $5}')"
pkill -STOP -g $PG
C=figures/hero/final_cache; mkdir -p $C
for P in lone pair rib_lone rib_pair; do
  T=$(mktemp)
  /usr/bin/time -l blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- --width-px 2882 --samples 128 --tile 256 --cache-dir $C --panels $P 2> "$T" | grep -E "PANEL|WARN" || { echo "panel $P failed"; tail -5 "$T"; exit 1; }
  echo "panel $P: $(grep -E ' real ' "$T" | awk '{print $1" s"}'), peak $(grep 'peak memory footprint' "$T" | awk '{printf "%.2f GB", $1/1073741824}')"
  rm -f "$T"
done
blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- --width-px 2882 --samples 128 --cache-dir $C --assemble --out figures/fig1_hero.png --overlay figures/hero/fig1_overlay.json | grep -E "HERO|WARN"
echo "$(date '+%F %T') done"
