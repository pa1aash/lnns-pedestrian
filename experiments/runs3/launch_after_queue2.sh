#!/bin/bash
# Waits until queue 2 has exited (the PID in $QUEUE2_PID_FILE, re-read every minute, so a restarted
# queue 2 is waited for too), then starts queue 3 detached with 4 workers per step and writes its PID
# to data/logs/queue3_pid.txt. Usage (from the repository root):
#   nohup bash experiments/runs3/launch_after_queue2.sh >> data/logs/queue3_watch.out 2>&1 &
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${PY:-/Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python}"
QUEUE2_PID_FILE="${QUEUE2_PID_FILE:-/Users/palaash/Developer/lnns-pedestrian/data/logs/queue_pid.txt}"
mkdir -p "$ROOT/data/logs"
echo "$(date '+%F %T') watcher pid $$ waiting for queue 2 ($QUEUE2_PID_FILE)"
while true; do
  P="$(cat "$QUEUE2_PID_FILE" 2>/dev/null)"
  if [ -n "$P" ] && kill -0 "$P" 2>/dev/null; then sleep 60; continue; fi
  sleep 120   # a restarted queue 2 writes its new PID within this grace period
  P="$(cat "$QUEUE2_PID_FILE" 2>/dev/null)"
  if [ -n "$P" ] && kill -0 "$P" 2>/dev/null; then continue; fi
  break
done
cd "$ROOT" || exit 1
echo "$(date '+%F %T') queue 2 has exited; starting queue 3"
PYTHONPATH="$ROOT/code" nohup caffeinate -i "$PY" experiments/runs3/queue3.py run >> data/logs/queue3.out 2>&1 &
C=$!
sleep 2
Q="$(pgrep -P "$C" | head -1)"
echo "${Q:-$C}" > data/logs/queue3_pid.txt
echo "$(date '+%F %T') queue 3 pid ${Q:-$C} (caffeinate $C)"
