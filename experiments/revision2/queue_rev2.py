"""Revision-3 run queue (session C2): steps in experiments/revision2/queue_rev2.yaml, run in file order.

The step file is re-read after every step, so steps appended while the queue runs are picked up. Each step is a
command run from the repository root with PYTHONPATH=code; its JSONL outputs are resumable, so a restart
re-runs only unfinished jobs. State data/revision2/queue_state.json, log data/logs/queue_rev2.log, step logs
data/logs/rev2_<step>.log. A step whose dependency failed or is unfinished is skipped for this pass.
  queue_rev2.py run       run every unfinished step
  queue_rev2.py status    finished / failed steps
Launch: nohup caffeinate -i <python> experiments/revision2/queue_rev2.py run >> data/logs/queue_rev2.out 2>&1 &
"""
import datetime
import json
import os
import subprocess
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STATE = os.path.join(ROOT, "data", "revision2", "queue_state.json")
LOG = os.path.join(ROOT, "data", "logs", "queue_rev2.log")


def steps():
    return yaml.safe_load(open(os.path.join(HERE, "queue_rev2.yaml")))["steps"]


def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"done": {}, "failed": {}}


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')} {msg}"
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def next_step(tried):
    st = load_state()
    for s in steps():
        n = s["name"]
        if n in st["done"] or n in tried:
            continue
        if all(d in st["done"] for d in s.get("depends", [])):
            return s
    return None


def run():
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "code"), PYTHONUNBUFFERED="1")
    log(f"queue start pid={os.getpid()}")
    tried = set()
    while True:
        s = next_step(tried)
        if s is None:
            break
        name = s["name"]
        tried.add(name)
        log(f"start {name} (est {s.get('cpu_h', '?')} CPU-h)")
        t0 = time.time()
        with open(os.path.join(ROOT, "data", "logs", f"rev2_{name}.log"), "a") as f:
            rc = subprocess.call([sys.executable] + [os.path.join(ROOT, c) if c.endswith(".py") else c for c in s["cmd"]],
                                 cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
        wall = time.time() - t0
        st = load_state()
        if rc == 0:
            st["done"][name] = {"end": datetime.datetime.now().isoformat(timespec="seconds"), "wall_s": round(wall, 1)}
            st["failed"].pop(name, None)
            log(f"end {name} wall={wall / 3600:.2f} h")
        else:
            st["failed"][name] = {"rc": rc, "wall_s": round(wall, 1)}
            log(f"FAILED {name} rc={rc} wall={wall / 3600:.2f} h")
        json.dump(st, open(STATE, "w"), indent=1)
    log("queue end")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run()
    else:
        print(json.dumps(load_state(), indent=1))
