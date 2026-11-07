# Experiment targets. Run from the repository root as `make -C experiments <target>`.
# Simulations use the plan-root interpreter (same versions => bit-identical results).
ROOT := $(abspath ..)
PY ?= /Users/palaash/Developer/pedestrian-abs-plan/.venv/bin/python
export PYTHONPATH := $(ROOT)/code

.PHONY: regress test status keystone selection e1-analyze queue

regress:            ## regression hash, must print e381b49dc24acccd OK (Mac only)
	$(PY) $(ROOT)/experiments/regress.py

test:               ## simulator test suite (expect 128 passed, 5 known cross-platform failures)
	cd $(ROOT)/code && $(PY) -m pytest -q -p no:cacheprovider

status:             ## queue progress, jobs done / total per step
	$(PY) $(ROOT)/experiments/queue.py status

e1-analyze:
	$(PY) $(ROOT)/experiments/E1/e1_analyze.py

keystone:
	$(PY) $(ROOT)/experiments/E1/keystone.py

selection:
	$(PY) $(ROOT)/experiments/selection.py

queue:              ## launch the detached queue (resumable)
	cd $(ROOT) && nohup caffeinate -i $(PY) experiments/queue.py run >> data/logs/queue.out 2>&1 &
