"""Detached job queue for batch 2 (steps in experiments/queue.yaml).

  queue.py run      run every unfinished step in order (4 workers each); a step whose dependency
                    failed is skipped; finished steps are recorded in data/queue_state.json;
                    start, end and wall time are logged to data/logs/queue.log.
  queue.py status   jobs done / total per step, read from the steps' JSONL outputs.
Launch: nohup caffeinate -i <python> experiments/queue.py run >> data/logs/queue.out 2>&1 &
"""
import datetime
import importlib.util
import json
import os
import subprocess
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE = os.path.join(ROOT, "data", "queue_state.json")
LOG = os.path.join(ROOT, "data", "logs", "queue.log")


def steps():
    return yaml.safe_load(open(os.path.join(HERE, "queue.yaml")))["steps"]


def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"done": {}, "failed": {}}


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')} {msg}"
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def run():
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "code"), PYTHONUNBUFFERED="1")
    log(f"queue start pid={os.getpid()}")
    for s in steps():
        st = load_state()
        name = s["name"]
        if name in st["done"]:
            continue
        bad = [d for d in s.get("depends", []) if d not in st["done"]]
        if bad:
            log(f"skip {name}: dependency not finished {bad}")
            continue
        log(f"start {name} (est {s.get('cpu_h', '?')} CPU-h)")
        t0 = time.time()
        steplog = os.path.join(ROOT, "data", "logs", f"{name}.log")
        with open(steplog, "a") as f:
            rc = subprocess.call([sys.executable] + [os.path.join(ROOT, c) if c.endswith(".py") else c
                                                     for c in s["cmd"]], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
        wall = time.time() - t0
        st = load_state()
        if rc == 0:
            st["done"][name] = {"end": datetime.datetime.now().isoformat(timespec="seconds"), "wall_s": round(wall, 1)}
            st["failed"].pop(name, None)
            log(f"end {name} wall={wall / 3600:.2f} h")
        else:
            st["failed"][name] = {"rc": rc, "wall_s": round(wall, 1)}
            log(f"FAILED {name} rc={rc} wall={wall / 3600:.2f} h (see data/logs/{name}.log)")
        json.dump(st, open(STATE, "w"), indent=1)
    log("queue end")


def _mod(rel):
    spec = importlib.util.spec_from_file_location(rel.replace("/", "_")[:-3], os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _count(out, ids):
    done = set()
    if out and os.path.exists(out):
        with open(out) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["job_id"])
                except Exception:
                    pass
    return len(done & set(ids)) if ids is not None else len(done)


def status():
    sys.path.insert(0, os.path.join(HERE, "lib"))
    cwd = os.getcwd()
    st = load_state()
    rows = []
    for s in steps():
        name = s["name"]
        note = ""
        try:
            if name == "E2":
                m = _mod("E2/e2_quench.py"); J, out = m.jobs(), m.OUT
            elif name == "BAR":
                m = _mod("BAR/bar.py"); J, out = m.jobs(), m.OUT
            elif name == "SEL_E3E4":
                sel = json.load(open(os.path.join(ROOT, "data", "derived", "selection.json")))
                J, out = None, None
                note = f"E3 n={sel['E3']['n']}, E4 n={sel['E4']['n']}" if "E3" in sel else "pending"
            elif name == "E3":
                m = _mod("E3/e3_dt.py"); J, out = m.jobs(), m.OUT
            elif name == "E4":
                m = _mod("E4/e4_escape.py"); J, out = m.jobs(), m.OUT
                if os.path.exists(m.EXT):
                    e = json.load(open(m.EXT)); note = f"events {e['events']} restarts {e['n_restarts']}"
            elif name in ("E5a", "E5b"):
                m = _mod("E5/e5_sweep.py"); J, out = m.jobs(name), m.out_path(name)
            elif name == "E7b_lib":
                m = _mod("E7b/e7b_lib.py"); J, out = m.jobs(), m.OUT
                note = f"qualifying pairs {len(m.state()[1])}/{m.TARGET}"
            elif name == "E7":
                m = _mod("E7/e7_cells.py"); J, out = m.jobs(), m.OUT
        except Exception as e:  # noqa: BLE001
            J, out, note = None, None, f"status error: {e}"
        finally:
            os.chdir(cwd)
        ids = None if J is None else [j["job_id"] for j in J]
        tot = "?" if ids is None else len(ids)
        done = _count(out, ids) if out else 0
        flag = "done" if name in st["done"] else ("FAILED" if name in st["failed"] else "")
        if ids is None and name not in ("SEL_E3E4",):
            note = note or "waiting for selection"
        rows.append(f"{name:9s} {done:>6}/{tot:<6} {flag:6s} {note}")
    print("\n".join(rows))


if __name__ == "__main__":
    {"run": run, "status": status}[sys.argv[1]]()
