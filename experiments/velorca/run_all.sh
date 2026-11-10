#!/bin/bash
# Velocity-coupled ORCA queue: lone, pair, whole, keystone, dtprobe (each resumable; rerun to resume).
set -e -o pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD/code"
PY=/Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python
for part in lone pair whole keystone dtprobe; do
  echo "== $part $(date '+%F %T')"
  $PY experiments/velorca/velorca.py $part --workers 4
done
echo "== done $(date '+%F %T')"
