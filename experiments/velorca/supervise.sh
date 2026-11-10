#!/bin/bash
# Runs run_all.sh only while the Mac is on AC power: starts it on AC, stops it (resumable) on battery.
cd "$(dirname "$0")/../.."
LOG=data/velorca/queue.log
pid=""
while true; do
  if grep -q "^== done" "$LOG" 2>/dev/null; then echo "supervisor: queue done $(date '+%F %T')"; exit 0; fi
  ac=$(pmset -g batt | head -1 | grep -c "AC Power")
  running=0; [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && running=1
  if [ "$ac" = 1 ] && [ "$running" = 0 ]; then
    echo "supervisor: AC power, starting queue $(date '+%F %T')"
    nohup caffeinate -i experiments/velorca/run_all.sh >> "$LOG" 2>&1 &
    pid=$!
  elif [ "$ac" = 0 ] && [ "$running" = 1 ]; then
    echo "supervisor: on battery, stopping queue $(date '+%F %T')"
    pkill -P "$pid"; kill "$pid" 2>/dev/null
    pkill -f "experiments/velorca/velorca.py (lone|pair|whole|keystone|dtprobe) --workers"
    pid=""
  fi
  sleep 30
done
