"""Queue 3: experiments/queue.py run on experiments/queue3.yaml, with its own state and log files.

  queue3.py run      run every unfinished step of queue3.yaml in order (state data/queue3_state.json,
                     log data/logs/queue3.log, step logs data/logs/<step>.log)
  queue3.py status   jobs done / total per step, from the steps' JSONL outputs
Queue 2's files (experiments/queue.yaml, data/queue_state.json, data/logs/queue.log) are not read or
written.
"""
import importlib.util
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
ROOT = os.path.dirname(EXP)
spec = importlib.util.spec_from_file_location("queue2_runner", os.path.join(EXP, "queue.py"))
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
q.STATE = os.path.join(ROOT, "data", "queue3_state.json")
q.LOG = os.path.join(ROOT, "data", "logs", "queue3.log")
q.steps = lambda: yaml.safe_load(open(os.path.join(EXP, "queue3.yaml")))["steps"]

OUTS = {"N1": "data/N1/n1.jsonl", "N2": "data/N2/n2.jsonl", "N3": "data/N3/n3.jsonl", "N5": "data/N5/n5.jsonl",
        "N6_static": "data/N6/n6_static.jsonl", "N6_quench": "data/N6/n6_quench.jsonl"}
TOTAL = {"N1": 680, "N2": 186, "N3": 540, "N5": 100, "N6_static": 92, "N6_quench": 368}


def status():
    st = q.load_state()
    for s in q.steps():
        n = s["name"]
        p = os.path.join(ROOT, OUTS[n])
        done = q._count(p, None) if os.path.exists(p) else 0
        flag = "done" if n in st["done"] else ("FAILED" if n in st["failed"] else "")
        print(f"{n:10s} {done:>5}/{TOTAL[n]:<5} {flag}")


if __name__ == "__main__":
    {"run": q.run, "status": status}[sys.argv[1]]()
