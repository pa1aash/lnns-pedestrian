#!/bin/sh
# Hero final render (2882 px = 600 dpi at 12.2 cm), low-memory version: the four panels are rendered one per Blender run
# (-t 2, Metal GPU, tile 256, persistent data off), cached in figures/hero/final_cache/, then assembled.
# Gate: >= 3.5 GB free (polls every 5 min, up to 4 h). If a panel fails or swap grows by > 2 GB during it, the panel is
# rendered once more. If QUEUE_PID is set (e.g. QUEUE_PID=3074 sh experiments/hero/final.sh), the process group of that
# PID (a running experiment queue) is paused with SIGSTOP for the re-render only and always resumed with SIGCONT (trap);
# it is never killed. Without QUEUE_PID nothing is paused. macOS only (memory_pressure, vm.swapusage, Metal);
# Blender 5.2.2 on PATH as `blender`. Log: figures/hero/final_render.log
cd "$(dirname "$0")/../.."
MIN=${MIN_FREE_GB:-3.5}
C=figures/hero/final_cache
free_gb() { memory_pressure | awk '/free percentage/ {gsub("%","",$5); printf "%.2f", $5 * 8 / 100}'; }
swap_mb() { sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}'; }
PGID=""
if [ -n "$QUEUE_PID" ]; then
  PGID=$(ps -o pgid= -p "$QUEUE_PID" | tr -d ' ')
  [ -n "$PGID" ] || { echo "QUEUE_PID $QUEUE_PID is not running" >&2; exit 1; }
fi
PAUSED=0
resume() { if [ "$PAUSED" = 1 ]; then pkill -CONT -g "$PGID"; PAUSED=0; echo "$(date '+%F %T') queue RESUMED (SIGCONT, pgid $PGID)"; fi; }
trap resume EXIT INT TERM
pause() { if [ -n "$PGID" ] && [ "$PAUSED" = 0 ]; then pkill -STOP -g "$PGID"; PAUSED=1; echo "$(date '+%F %T') queue PAUSED (SIGSTOP, pgid $PGID)"; fi; }
n=0
while :; do
  f=$(free_gb)
  if [ "$(echo "$f >= $MIN" | bc)" = 1 ]; then break; fi
  n=$((n + 1)); [ $n -gt 48 ] && { echo "free memory stayed below $MIN GB for 4 h" >&2; exit 1; }
  echo "$(date +%H:%M) free $f GB < $MIN GB: waiting 5 min" >&2; sleep 300
done
echo "$(date '+%F %T') free $f GB at start, swap $(swap_mb) MB"
mkdir -p $C
B="blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- --width-px 2882 --samples ${SAMPLES:-128} --cache-dir $C"
for P in lone pair rib_lone rib_pair; do
  S0=$(swap_mb); T=$(mktemp); ok=0
  /usr/bin/time -l $B --panels $P 2> "$T" | grep -E "PANEL|WARN" && ok=1
  S1=$(swap_mb)
  echo "panel $P: $(grep -E ' real ' "$T" | awk '{print $1" s"}'), peak $(grep 'peak memory footprint' "$T" | awk '{printf "%.2f GB", $1/1073741824}'), swap $S0 -> $S1 MB"
  if [ "$ok" != 1 ] || [ $((S1 - S0)) -gt 2048 ]; then
    echo "panel $P: failed or swap grew by $((S1 - S0)) MB: re-rendering${PGID:+ with the queue paused}"
    pause
    /usr/bin/time -l $B --panels $P 2> "$T" | grep -E "PANEL|WARN" || { echo "panel $P failed again" >&2; exit 1; }
    echo "panel $P (re-render): $(grep -E ' real ' "$T" | awk '{print $1" s"}'), peak $(grep 'peak memory footprint' "$T" | awk '{printf "%.2f GB", $1/1073741824}')"
    resume
  fi
  rm -f "$T"
done
blender -b -t 2 --factory-startup --python experiments/hero/render_hero.py -- --width-px 2882 --samples ${SAMPLES:-128} --cache-dir $C --assemble \
  --out figures/fig1_hero.png --overlay figures/hero/fig1_overlay.json | grep -E "HERO|WARN"
python3 tools/make_fig1_overlay.py --png figures/fig1_hero.png | cut -c1-300
echo "$(date '+%F %T') done"
