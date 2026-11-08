#!/bin/sh
# Re-render the hero panels one per Blender run (-t 2, Metal GPU, tile 256), then assemble. Gate: >= 3.5 GB free,
# polled every 5 min for up to 3 h. Never touches the experiment queue. Log: figures/hero/c43_render.log
cd "$(dirname "$0")/../.."
free_gb() { memory_pressure | awk '/free percentage/ {gsub("%","",$5); printf "%.2f", $5 * 8 / 100}'; }
C=figures/hero/final_cache
mkdir -p $C
for P in lone pair rib_lone rib_pair; do
  n=0
  while :; do
    f=$(free_gb)
    [ "$(echo "$f >= 3.5" | bc)" = 1 ] && break
    n=$((n + 1)); [ $n -gt 36 ] && { echo "free memory stayed below 3.5 GB for 3 h" >&2; exit 1; }
    echo "$(date +%H:%M) free $f GB < 3.5 GB: waiting 5 min"; sleep 300
  done
  T=$(mktemp)
  echo "$(date '+%F %T') panel $P start, free $f GB, swap $(sysctl -n vm.swapusage | awk '{print $6}')"
  /usr/bin/time -l blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- --width-px 2882 --samples 128 --tile 256 --cache-dir $C --panels $P 2> "$T" | grep -E "PANEL|WARN" || { echo "panel $P failed"; tail -5 "$T"; exit 1; }
  echo "panel $P: $(grep -E ' real ' "$T" | awk '{print $1" s"}'), peak $(grep 'peak memory footprint' "$T" | awk '{printf "%.2f GB", $1/1073741824}')"
  rm -f "$T"
done
blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- --width-px 2882 --samples 128 --cache-dir $C --assemble --out figures/fig1_hero.png --overlay figures/hero/fig1_overlay.json | grep -E "HERO|WARN"
echo "$(date '+%F %T') done"
