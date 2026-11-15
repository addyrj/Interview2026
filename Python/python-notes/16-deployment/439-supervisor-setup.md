---

# 439. Supervisor Setup
# हिंदी में: Supervisor Setup (Process Manager)

---

## 🔵 Simple Definition (English)
Supervisor is a process control system for Linux. You describe each program in a config file (`[program:api]`), and `supervisord` starts it, watches it, restarts it if it dies, collects its logs and lets you control it with `supervisorctl start|stop|restart|status`.

## 🔵 सरल परिभाषा (Hindi)
Supervisor Linux के लिए process control system है। आप हर program को config file में लिखते हैं (`[program:api]`), और `supervisord` उसे चालू करता है, निगरानी रखता है, मर जाए तो restart करता है, logs इकट्ठा करता है और `supervisorctl start|stop|restart|status` से आप उसे control करते हैं।

---

## 🔴 Problem it Solves
A FastAPI deployment is rarely one process. You also have a Celery worker, a scheduler, maybe a WebSocket server. Started by hand they die with the SSH session and nobody restarts them after a crash. Supervisor keeps the whole set alive, groups them, rotates logs and gives one simple command-line to manage them. It also works inside Docker containers where systemd is not available.

## 🔴 यह क्यों बना? (Hindi)
FastAPI deployment में शायद ही कभी एक ही process होता है। साथ में Celery worker, scheduler, शायद WebSocket server भी होता है। हाथ से चलाए तो SSH session के साथ मर जाते हैं और crash के बाद कोई restart नहीं करता। Supervisor पूरे सेट को जीवित रखता है, group करता है, logs rotate करता है और एक आसान command-line देता है। यह Docker containers में भी चलता है जहाँ systemd नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → apt install supervisor (starts supervisord as a service)
Step 2 → Write /etc/supervisor/conf.d/app.conf with [program:...] sections
Step 3 → supervisorctl reread  (find changes)  then  supervisorctl update  (apply)
Step 4 → supervisord forks each command and watches it
Step 5 → If the process exits unexpectedly and autorestart=true, it is started again
Step 6 → startsecs: must stay up that many seconds to count as "started" (else BACKOFF)
Step 7 → stdout/stderr go to log files with automatic rotation
Step 8 → `stop` sends stopsignal (TERM), waits stopwaitsecs, then SIGKILL
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → apt install supervisor (supervisord service की तरह चालू होता है)
Step 2 → /etc/supervisor/conf.d/app.conf में [program:...] sections लिखो
Step 3 → supervisorctl reread (बदलाव खोजो) फिर supervisorctl update (लागू करो)
Step 4 → supervisord हर command को fork करके निगरानी करता है
Step 5 → process अचानक बंद हो और autorestart=true हो तो फिर चालू होता है
Step 6 → startsecs: इतने सेकंड चलना चाहिए तब "started" गिना जाता है (वरना BACKOFF)
Step 7 → stdout/stderr log files में जाते हैं, automatic rotation के साथ
Step 8 → `stop` stopsignal (TERM) भेजता है, stopwaitsecs इंतज़ार करता है, फिर SIGKILL
```

---

## 🟡 Real World Example
An e-commerce backend on one VPS: `[program:api]` runs gunicorn with uvicorn workers, `[program:celery]` runs 2 Celery workers for emails and invoices, `[program:beat]` runs the Celery scheduler. After a deploy: `supervisorctl restart backend:*`. If the OOM killer ends the Celery worker at night, Supervisor restarts it within seconds and the on-call person sleeps well.

## 🟡 Real Example Hindi mein
एक VPS पर e-commerce backend: `[program:api]` gunicorn + uvicorn workers चलाता है, `[program:celery]` emails और invoices के लिए 2 Celery workers, `[program:beat]` Celery scheduler। Deploy के बाद: `supervisorctl restart backend:*`। रात में OOM killer Celery worker को मार दे तो Supervisor कुछ सेकंड में उसे फिर चालू कर देता है और on-call वाला आराम से सोता है।

---

## 💻 Code Example — Basic
A worker that stops cleanly when Supervisor sends `SIGTERM` (this is the Python half; it was run, and the signal was sent to itself to simulate `supervisorctl stop`):

```python
# Basic: a worker that Supervisor can start, stop and restart safely
import signal                                     # handle SIGTERM (supervisor's stop signal)
import os                                         # send a signal to ourselves for the demo
import time                                       # sleep between jobs
from types import FrameType                       # type of the signal frame

running: bool = True                              # main loop flag


def handle_term(signum: int, frame: FrameType | None) -> None:
    global running                                # we change the module-level flag
    print(f"got signal {signum}, finishing current job then exiting")
    running = False                               # loop ends after the current job


signal.signal(signal.SIGTERM, handle_term)        # supervisor sends SIGTERM on `stop`

jobs_done: int = 0                                # counter
while running:                                    # real worker: poll a queue here
    jobs_done += 1                                # "process" a job
    print(f"job {jobs_done} done")
    if jobs_done == 3:                            # demo only: pretend supervisor stops us
        os.kill(os.getpid(), signal.SIGTERM)      # deliver SIGTERM to this process
    time.sleep(0.01)                              # idle a little
print("clean exit")                               # exit code 0 -> supervisor treats as expected

# Output (real run, Python 3.13):
# job 1 done
# job 2 done
# job 3 done
# got signal 15, finishing current job then exiting
# clean exit
```

The Supervisor config (**not run**: Supervisor is not installed here; only a similar sample was parsed as INI text by the linter in the advanced example):

```ini
; /etc/supervisor/conf.d/app.conf
[program:api]
command=/srv/app/.venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000 main:app
directory=/srv/app
user=deploy
autostart=true
autorestart=true
startsecs=5
stopasgroup=true            ; stop gunicorn master AND its workers
stopsignal=TERM
stopwaitsecs=30             ; time to finish in-flight requests
stdout_logfile=/var/log/app/api.out.log
stderr_logfile=/var/log/app/api.err.log
environment=APP_ENV="production",PORT="8000"
```

```bash
# day-to-day commands - not run here
sudo supervisorctl reread        # detect new/changed config
sudo supervisorctl update        # apply it
sudo supervisorctl status        # RUNNING / STARTING / BACKOFF / FATAL
sudo supervisorctl restart api
sudo supervisorctl tail -f api stderr
```

## 💻 Code Example — Advanced
A linter for `supervisord.conf`, so a bad config is caught in CI before it reaches the server:

```python
# Advanced: lint a supervisord.conf before you deploy it
import configparser                               # supervisor conf is INI format
import io                                         # read from a string

CONF = """
[supervisord]
logfile=/var/log/supervisor/supervisord.log

[program:api]
command=/srv/app/.venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000 main:app
directory=/srv/app
user=deploy
autostart=true
autorestart=true
startsecs=5
stopasgroup=true
stopsignal=TERM
stopwaitsecs=30
stdout_logfile=/var/log/app/api.out.log
stderr_logfile=/var/log/app/api.err.log
environment=APP_ENV="production",PORT="8000"

[program:worker]
command=/srv/app/.venv/bin/python worker.py
directory=/srv/app
autorestart=true
numprocs=2
process_name=%(program_name)s_%(process_num)02d

[group:backend]
programs=api,worker
"""


def lint(text: str) -> list[str]:
    cp = configparser.ConfigParser(interpolation=None)   # supervisor uses %(...)s itself
    cp.read_file(io.StringIO(text))               # parse
    problems: list[str] = []                      # collected warnings
    for name in cp.sections():
        if not name.startswith("program:"):       # only check programs
            continue
        s = cp[name]
        if "command" not in s:                    # mandatory key
            problems.append(f"{name}: missing command")
        if s.get("user", "") in ("", "root"):     # least privilege
            problems.append(f"{name}: should run as a non-root user")
        if s.getboolean("autorestart", fallback=False) is False:
            problems.append(f"{name}: autorestart is off")
        if s.getint("numprocs", fallback=1) > 1 and "%(process_num)" not in s.get("process_name", ""):
            problems.append(f"{name}: numprocs>1 needs %(process_num)02d in process_name")
        if "stdout_logfile" not in s:
            problems.append(f"{name}: no stdout_logfile (logs lost / unbounded)")
    return problems


for p in lint(CONF):
    print(p)
print("done")                                      # lint finished

# Output (real run, Python 3.13):
# program:worker: should run as a non-root user
# program:worker: no stdout_logfile (logs lost / unbounded)
# done
```

The `worker` program is flagged twice: it has no `user` (so it would run as whoever supervisord runs as, usually root) and no `stdout_logfile`. The `api` block passes. `configparser` needs `interpolation=None` because Supervisor uses its own `%(program_name)s` syntax.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Supervisor (Python) | PM2 (Node.js) |
|---------|--------------------|---------------|
| Config | INI file | `ecosystem.config.js` |
| Start | `supervisorctl start api` | `pm2 start app.js` |
| Auto restart | `autorestart=true` | on by default |
| Multiple copies | `numprocs=4` | `-i 4` (cluster) |
| Logs | `stdout_logfile` | `pm2 logs` |
| Boot start | service enabled | `pm2 startup` |

```python
# Python way — numprocs creates api_00, api_01 ...  (INI config)
# [program:worker]
# command=python worker.py
# numprocs=2
# process_name=%(program_name)s_%(process_num)02d
```
```javascript
// JavaScript way — PM2 ecosystem file
module.exports = {
  apps: [{ name: "worker", script: "worker.js", instances: 2, autorestart: true }],
};
```

Key difference: Supervisor is language-agnostic (it supervises any command) while PM2 is Node-first. On modern Linux many teams use systemd for the same job; Supervisor's advantages are simple INI config, process groups, a nice `supervisorctl` shell and use inside containers.

---

## 🟠 FastAPI Connection
Supervisor runs the FastAPI server plus everything around it (Celery, ARQ or RQ workers, a scheduler). The app must exit cleanly on `SIGTERM`: uvicorn does this automatically and finishes in-flight requests; custom worker loops must handle the signal like the basic example. With gunicorn set `stopasgroup=true` so the master and its workers stop together.

```python
# FastAPI example — lifespan cleanup runs when Supervisor sends SIGTERM
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("startup: open DB pool")      # runs when supervisor starts the program
    yield
    print("shutdown: close DB pool, flush logs")   # runs on SIGTERM within stopwaitsecs

app = FastAPI(lifespan=lifespan)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Running a program that daemonizes itself (forks into the background)
✅ Correct: run it in the foreground; Supervisor must own the process

```ini
; Wrong - supervisor sees the parent exit immediately and loops in BACKOFF
command=gunicorn main:app --daemon
; Right
command=gunicorn main:app
```

❌ Mistake 2: Forgetting `reread` + `update` after editing the config
✅ Correct: always run both (or `supervisorctl reload` if you accept restarting everything)

```bash
# Wrong: edit file and wonder why nothing changed
# Right
sudo supervisorctl reread && sudo supervisorctl update
```

❌ Mistake 3: Using a relative path, missing `environment`, or a venv not activated
✅ Correct: absolute paths to the venv binaries; Supervisor does NOT load your shell profile

```ini
; Wrong
command=gunicorn main:app
; Right
command=/srv/app/.venv/bin/gunicorn main:app
directory=/srv/app
```

---

## 🧠 Tricky Interview Question

```python
# Supervisor config says: startsecs=5, startretries=3, autorestart=true
# Your app crashes with an exception 1 second after every start.
# What status does `supervisorctl status` finally show, and why?
import time

def app() -> None:
    time.sleep(1)               # runs only 1 second
    raise RuntimeError("boom")  # then crashes
```
Answer: `FATAL`. A process must stay alive for `startsecs` (5 s) to be considered successfully started. Each crash before that is a failed start, so Supervisor shows `BACKOFF`, waits a growing delay, retries up to `startretries` (3) times, then gives up with `FATAL`. `autorestart=true` only applies to processes that already reached `RUNNING`. The fix is to read `stderr_logfile` (the real error), fix the bug, then `supervisorctl start api`. Also, an app that legitimately takes 10 s to boot needs `startsecs` below that or it will wrongly flip to BACKOFF.

---

## ⚫ Interview Questions + Answers

Q1: Supervisor vs systemd?
A1: Both restart services. systemd is built into the OS, handles boot order, sockets and cgroup limits, so it is the default on servers. Supervisor is portable, has simple INI config and `supervisorctl`, and works inside Docker. Using systemd to start Supervisor is also common.

Q2: What do `autostart`, `autorestart` and `startsecs` mean?
A2: `autostart` starts the program when supervisord starts. `autorestart` (true/false/unexpected) decides if it is restarted after exit. `startsecs` is how long it must run to count as successfully started.

Q3: How do you run many identical workers?
A3: Set `numprocs=4` and use `process_name=%(program_name)s_%(process_num)02d`, otherwise the names collide. Ports must differ per process if they bind sockets (use `%(process_num)d`), or use gunicorn which already manages workers.

Q4: Why `stopasgroup` and `killasgroup`?
A4: A program that spawns children (gunicorn master and workers) leaves orphans if only the parent receives the signal. These options send the signal to the whole process group.

Q5: How do you restart without losing in-flight requests?
A5: Use `stopsignal=TERM` with a generous `stopwaitsecs`; uvicorn/gunicorn finish running requests on TERM. For zero downtime, run two instances behind Nginx and restart one at a time.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several long-running processes (API, workers, scheduler) on one machine
- You want a simple `supervisorctl` tool and per-program logs
- Inside a Docker container that must run more than one process (as a last resort)

❌ Avoid when:
- Kubernetes/ECS already restarts containers (one process per container is better)
- Plain systemd on the host is enough for one service
- You need advanced dependency ordering between services (systemd does it better)

---

## 📊 Visual Diagram
```
 systemd ──> supervisord (pid 1 of your apps)
                |-- [program:api]    gunicorn master -> uvicorn workers
                |-- [program:celery] celery worker x2
                '-- [program:beat]   celery scheduler
 crash? --> supervisord waits, restarts (autorestart)
 supervisorctl <--unix socket--> supervisord   (status/start/stop)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| supervisord | The supervisor daemon | supervisor का daemon |
| supervisorctl | Command-line control tool | control का command-line tool |
| autorestart | Restart after exit | बंद होने पर फिर चालू |
| startsecs | Seconds to count as started | "चालू" गिने जाने के सेकंड |
| BACKOFF / FATAL | Failing to start / gave up | चालू नहीं हो पा रहा / हार मान ली |
| numprocs | Number of copies | copies की संख्या |

---

## ⚡ 3-Line Summary
English: Supervisor keeps your API and background workers running, restarts them on crashes and manages logs. Run programs in the foreground with absolute paths and apply changes with `reread` and `update`. Make apps exit cleanly on SIGTERM.
Hindi: Supervisor आपके API और background workers को चालू रखता है, crash पर restart करता है और logs संभालता है। Programs को foreground में absolute paths से चलाओ और बदलाव `reread` व `update` से लागू करो। Apps को SIGTERM पर साफ तरीके से बंद होने दो।

---

## ➡️ Next Topic
**440. Docker + Python Setup** — package the app and its environment into an image so "works on my machine" disappears.
