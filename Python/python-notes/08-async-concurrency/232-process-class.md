---

# 232. Process Class
# हिंदी में: Process Class (multiprocessing.Process)

---

## 🔵 Simple Definition (English)
`multiprocessing.Process` represents one child operating-system process. Its API mirrors `threading.Thread`: give it a `target` and `args`, call `start()`, then `join()`. It adds `terminate()`, `kill()`, `exitcode` and `pid`, which threads do not have.

## 🔵 सरल परिभाषा (Hindi)
`multiprocessing.Process` एक child operating-system process को दर्शाता है। इसका API `threading.Thread` जैसा है: `target` और `args` दें, `start()` करें, फिर `join()`। इसमें `terminate()`, `kill()`, `exitcode` और `pid` अतिरिक्त हैं, जो threads में नहीं होते।

---

## 🔴 Problem it Solves
`Pool` is great for "apply a function to many items", but sometimes you need one long-lived worker with its own lifecycle: a crawler, a model-serving loop, an isolated job you may need to kill if it hangs. `Process` gives full control over a child, including forced termination and exit status.

## 🔴 यह क्यों बना? (Hindi)
`Pool` "बहुत items पर function चलाने" के लिए बढ़िया है, पर कभी-कभी एक लंबे समय चलने वाला worker चाहिए जिसका अपना lifecycle हो: crawler, model-serving loop, या ऐसा isolated job जिसे अटक जाने पर मारना पड़े। `Process` child पर पूरा नियंत्रण देता है, जबरन रोकना और exit status भी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → p = Process(target=fn, args=(...), name="job")   (nothing runs yet; pid is None)
Step 2 → p.start()           OS creates the child; pid is assigned
Step 3 → child runs fn in its own memory; parent continues
Step 4 → p.join(timeout)     parent waits (or gives up after timeout)
Step 5 → p.exitcode          0 = ok, N = sys.exit(N), 1 = exception, -N = killed by signal N
Step 6 → p.terminate() / p.kill() if it hangs; p.close() frees resources
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → p = Process(target=fn, args=(...), name="job")   (अभी कुछ नहीं चलता; pid None)
Step 2 → p.start()           OS child बनाता है; pid मिलता है
Step 3 → child अपनी memory में fn चलाता है; parent आगे बढ़ता है
Step 4 → p.join(timeout)     parent इंतज़ार करता है (या timeout पर छोड़ देता है)
Step 5 → p.exitcode          0 = ठीक, N = sys.exit(N), 1 = exception, -N = signal N से मारा गया
Step 6 → अटके तो p.terminate() / p.kill(); संसाधन छोड़ने के लिए p.close()
```

---

## 🟡 Real World Example
A document-processing API (an OCR job) runs each user's file in its own `Process` with a 30-second `join(timeout)`: if the OCR library hangs, the parent calls `terminate()` and returns an error, and the API keeps working. A scraper platform runs each crawler as a `Process` subclass pulling URLs from a shared queue. An ML service loads the model in a dedicated process.

## 🟡 Real Example Hindi mein
Document-processing API (OCR job) हर user की file अपने `Process` में 30 सेकंड के `join(timeout)` के साथ चलाती है: OCR library अटके तो parent `terminate()` करके error लौटाता है और API चलती रहती है। Scraper platform हर crawler को `Process` subclass के रूप में चलाता है जो shared queue से URLs लेता है। ML service model को अलग process में load करती है।

---

## 💻 Code Example — Basic
```python
# Basic Process usage - every line commented
import multiprocessing as mp  # the module
import os  # process ids
import time  # sleep


def task(name: str, secs: float) -> None:  # runs in the child (module-level function)
    time.sleep(secs)  # pretend work
    print(f"{name} pid-differs={os.getpid() != int(os.environ.get('PARENT', 0))}")  # child pid is not the parent pid


if __name__ == "__main__":  # required for spawn (macOS/Windows)
    os.environ["PARENT"] = str(os.getpid())  # remember the parent pid (children inherit the environment)
    p = mp.Process(target=task, args=("job", 0.05), name="job-proc")  # create (not started)
    print(p.name, p.pid, p.is_alive(), p.exitcode)  # before start: no pid, no exit code
    # Output: job-proc None False None
    p.start()  # launch the child
    print(p.pid is not None, p.is_alive())  # now it has a pid and is running
    # Output: True True
    p.join()  # wait for it to finish
    # Output (printed by the child): job pid-differs=True
    print(p.is_alive(), p.exitcode)  # finished cleanly
    # Output: False 0
```

## 💻 Code Example — Advanced
```python
# Production style: exit codes, hung-process termination, Process subclass, close()
import multiprocessing as mp  # processes
import time  # sleep


def fail() -> None:  # child that crashes
    raise RuntimeError("child crashed")  # traceback printed by the child


def exit7() -> None:  # child that exits with a chosen code
    raise SystemExit(7)  # like sys.exit(7)


def sleeper() -> None:  # child that hangs for a minute
    time.sleep(60)  # long wait


class Crawler(mp.Process):  # subclass: override run()
    def __init__(self, url: str, q) -> None:  # constructor
        super().__init__(name=f"crawler-{url}", daemon=True)  # ALWAYS call super().__init__
        self.url: str = url  # input
        self.q = q  # result queue

    def run(self) -> None:  # body executed in the child
        self.q.put((self.url, len(self.url)))  # send a result to the parent


if __name__ == "__main__":  # entry guard
    f = mp.Process(target=fail)  # crashing child
    f.start(); f.join()  # run and wait
    print("fail exit:", f.exitcode)  # 1 = unhandled exception
    # Output: fail exit: 1   (the child also prints a RuntimeError traceback to stderr)

    e = mp.Process(target=exit7)  # exiting child
    e.start(); e.join()  # run and wait
    print("exit:", e.exitcode)  # our chosen code
    # Output: exit: 7

    s = mp.Process(target=sleeper)  # hanging child
    s.start()  # run
    s.join(timeout=0.2)  # wait only 0.2 s
    print(s.is_alive())  # still running -> it hung
    # Output: True
    s.terminate()  # send SIGTERM (kill() sends SIGKILL)
    s.join()  # reap the process
    print(s.exitcode, s.is_alive())  # negative = killed by that signal number (15 = SIGTERM)
    # Output: -15 False

    q = mp.Queue()  # result queue
    cs = [Crawler(u, q) for u in ("a.com", "bb.org")]  # two crawlers
    [c.start() for c in cs]  # start both
    print(sorted(q.get(timeout=10) for _ in cs))  # collect results
    # Output: [('a.com', 5), ('bb.org', 6)]
    [c.join() for c in cs]  # reap

    print(mp.current_process().name, mp.parent_process())  # in the parent: MainProcess, no parent
    # Output: MainProcess None

    try:  # a Process object is single-use
        f.start()  # second start
    except Exception as ex:  # refused
        print(type(ex).__name__, ex)
    # Output: AssertionError cannot start a process twice

    s.close()  # release resources (only allowed once it has finished)
    try:  # using a closed object
        s.is_alive()  # not allowed
    except ValueError as ex:  # refused
        print("ValueError:", ex)
    # Output: ValueError: process object is closed
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
p = mp.Process(target=task, args=("job", 1))
p.start(); p.join()
p.terminate()
```

```javascript
// Node.js: child_process.fork (a new Node process) or worker_threads
const { fork } = require("child_process");
const child = fork("./task.js", ["job"]);
child.on("exit", (code) => console.log("exit", code));
child.kill("SIGTERM");                       // like p.terminate()
```

Key differences: `fork()` in Node starts a whole new Node process and talks via `child.send()` messages. Python's `Process` takes a function and arguments, and exit codes follow the same OS rules (negative = signal in Python's `exitcode`; Node reports `code` and `signal` separately).

---

## 🟠 FastAPI Connection
Run risky or long jobs in a separate process so a crash or hang cannot take the API down. A `Manager().dict()` (or a database/Redis) lets the API read the job's status. For many jobs prefer a queue + worker (Celery/RQ/ARQ).

```python
import multiprocessing as mp  # processes
from typing import Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

def long_job(job_id: int, results) -> None:  # runs in a separate process
    results[job_id] = "finished"  # write to shared dict proxy

app: FastAPI = FastAPI()  # create app

if __name__ == "__main__":  # guard for spawn
    manager = mp.Manager()  # shared-state server
    results = manager.dict()  # dict visible to all processes
    @app.post("/jobs/{job_id}")  # start a job
    def start(job_id: int) -> Dict[str, int]:
        p = mp.Process(target=long_job, args=(job_id, results))  # one process
        p.start(); p.join()  # demo only: real apps keep p and poll
        return {"job": job_id}  # response
    c = TestClient(app)
    print(c.post("/jobs/1").json(), dict(results))
    manager.shutdown()
# Output: {'job': 1} {1: 'finished'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `super().__init__()` in a subclass
```python
# Wrong - start() fails: AttributeError: 'W' object has no attribute '_closed'
class W(mp.Process):
    def __init__(self, x):
        self.x = x

# Correct
class W(mp.Process):
    def __init__(self, x):
        super().__init__()
        self.x = x
```

❌ Mistake 2: `join()` before draining a queue
```python
# Wrong - child blocks writing a big result, parent blocks in join: deadlock
p.start(); p.join(); item = q.get()

# Correct
p.start(); item = q.get(); p.join()
```

❌ Mistake 3: Expecting `terminate()` to clean up
```python
# Wrong - the child dies instantly: no finally blocks, locks it held stay locked
p.terminate()

# Correct - ask politely first (Event), terminate only as a last resort
stop_event.set(); p.join(5)
if p.is_alive():
    p.terminate()
```

---

## 🧠 Tricky Interview Question

**Q**: What are the values of `p.exitcode` after: (a) normal finish, (b) uncaught exception in the target, (c) `sys.exit(3)`, (d) `p.terminate()` on Linux/macOS?

**Answer**:
```
(a) 0   (b) 1   (c) 3   (d) -15
```
A negative exit code `-N` means the process was killed by signal N. `terminate()` sends SIGTERM (15); `kill()` sends SIGKILL (9) giving `-9`. While the process is still running, `exitcode` is `None`.

---

## ⚫ Interview Questions + Answers

Q1: How is `Process` different from `Thread`?
A1: A process has separate memory and its own GIL, can be killed, and runs truly in parallel, but starts slower and needs pickling to share data. A thread shares memory and is lighter but cannot be killed and shares the GIL.

Q2: What does a daemon process do?
A2: With `daemon=True` it is terminated when the parent exits; a daemon process cannot create child processes.

Q3: `terminate()` vs `kill()`?
A3: `terminate()` sends SIGTERM (can be handled); `kill()` sends SIGKILL (cannot). On Windows both call TerminateProcess.

Q4: How do you get a return value from a Process?
A4: There is none. Use a `Queue`, `Pipe`, shared `Value`/`Array`, a `Manager`, or `Pool`/`ProcessPoolExecutor` which return values for you.

Q5: What are zombie processes?
A5: Finished children whose exit status the parent has not collected. Calling `join()` (or `is_alive()`, `active_children()`) reaps them.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need a long-lived worker with its own lifecycle
- A job might hang or crash and must be isolated or killed
- You need to run something CPU-heavy outside the GIL

❌ Avoid when:
- You just map a function over many items (use `Pool`/`ProcessPoolExecutor`)
- Tasks are I/O-bound (threads/asyncio)
- You need a durable job system (use Celery/RQ/a queue service)

---

## 📊 Visual Diagram

```
 Parent                          Child
   │ Process(target=fn)            │
   │ p.start() ───────────────────►│ fn(*args) runs
   │ (continues)                   │
   │ p.join(timeout) ◄─ exits ─────┘   exitcode 0 / N / 1
   │        │
   └─ hung? ─► p.terminate() ─► exitcode -15
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pid | Process id from the OS | OS द्वारा दिया process id |
| exitcode | How the child ended | child कैसे खत्म हुआ |
| terminate | Send SIGTERM | SIGTERM भेजना |
| daemon process | Killed when parent exits | parent के साथ खत्म |
| join | Wait for the child | child का इंतज़ार |
| zombie | Finished but not reaped | खत्म पर reap नहीं हुआ |

---

## ⚡ 3-Line Summary
English: `Process` gives one controllable child with its own memory and GIL: `start`, `join`, `terminate`, `exitcode`. Collect results via Queue/Pipe, always use the `__main__` guard, and drain queues before `join`. Use Pool for map-style work.
Hindi: `Process` अपनी memory और GIL वाला एक नियंत्रित child देता है: `start`, `join`, `terminate`, `exitcode`। Results Queue/Pipe से लें, हमेशा `__main__` guard लगाएँ और `join` से पहले queue खाली करें। Map जैसे काम के लिए Pool लें।

---

## ➡️ Next Topic
**233. Next topic in the series** — pooling processes with `Pool` and `ProcessPoolExecutor` in depth.
