# Experiment targets. Run from the repository root as `make -C experiments <target>`.
# PY is the simulator interpreter. The default is the repository .venv with the simulator packages added
# (`make venv-sim` at the root: the versions of requirements-figures.txt plus shapely, pandas, pyarrow and
# pytest as pinned in .github/workflows/tests.yml; code/pyproject.toml lists the loose requirements).
# Any other interpreter can be given as PY=... . The regression hash (`regress`) is bit-identical only
# with Python 3.13 and exactly these pinned versions, on the Mac where the reference was recorded.
# Queue 3 run scripts live in experiments/runs3/; the queue file is experiments/queue3.yaml.
ROOT := $(abspath ..)
PY ?= $(ROOT)/.venv/bin/python
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
