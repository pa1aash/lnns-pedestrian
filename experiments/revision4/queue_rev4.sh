#!/bin/bash
# Revision-4 run queue (session C3). Steps run one after another with 6 workers (8 cores minus two); every step is
# resumable (finished job_ids are skipped). Waits for the T1 step started separately. Log: data/revision4/logs/.
cd "$(dirname "$0")/../.."
export PYTHONPATH=code
PY=.venv/bin/python
L=data/revision4/logs
while pgrep -f "experiments/revision4/T1_whole.py" > /dev/null; do sleep 60; done
for step in "T3 experiments/revision4/T3_dt_matched.py" "T5 experiments/revision4/T5_seed170.py runs" \
            "T4a experiments/revision4/T4_croma_dt.py --only dt0.005" "T4b experiments/revision4/T4_croma_dt.py --only dt0.01"; do
  set -- $step; name=$1; shift
  echo "$(date '+%F %T') start $name" >> $L/queue.log
  caffeinate -i $PY "$@" --workers 6 > $L/$name.log 2>&1
  echo "$(date '+%F %T') end $name rc=$?" >> $L/queue.log
done
