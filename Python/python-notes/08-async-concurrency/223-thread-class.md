---

# 223. Thread Class
# हिंदी में: Thread Class (threading.Thread से thread बनाना)

---

## 🔵 Simple Definition (English)
`threading.Thread` represents one thread of execution. You give it a function (`target`) and arguments, call `start()` to run it in the background, and `join()` to wait for it. You can also subclass it and override `run()`.

## 🔵 सरल परिभाषा (Hindi)
`threading.Thread` एक execution thread को दर्शाता है। आप उसे एक function (`target`) और arguments देते हैं, `start()` से background में चलाते हैं और `join()` से उसके खत्म होने का इंतज़ार करते हैं। आप इसे subclass करके `run()` override भी कर सकते हैं।

---

## 🔴 Problem it Solves
A normal program does one thing at a time, so a slow call (download, email, file write) freezes everything else. A `Thread` lets that slow call run alongside the main code, so the program stays responsive and several slow waits overlap.

## 🔴 यह क्यों बना? (Hindi)
आम program एक समय में एक ही काम करता है, इसलिए धीमा call (download, email, file write) बाकी सब रोक देता है। `Thread` उस धीमे call को main code के साथ चलने देता है, जिससे program responsive रहता है और कई धीमे इंतज़ार एक साथ हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → t = Thread(target=fn, args=(...))     create (not running yet)
Step 2 → t.start()                              OS thread begins, calls fn(*args)
Step 3 → main code continues immediately
Step 4 → t.join()                               wait until fn returns
Step 5 → t.is_alive() is now False              finished (a Thread can't be restarted)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → t = Thread(target=fn, args=(...))     बनाना (अभी चल नहीं रहा)
Step 2 → t.start()                              OS thread शुरू होकर fn(*args) चलाता है
Step 3 → main code तुरंत आगे बढ़ता है
Step 4 → t.join()                               fn के लौटने तक इंतज़ार
Step 5 → t.is_alive() अब False                  खत्म (Thread दोबारा start नहीं हो सकता)
```

---

## 🟡 Real World Example
Swiggy's backend sends an SMS and a push notification after an order is placed: each is a slow network call, so each runs in its own thread while the API replies immediately. A download manager starts one thread per file. A log shipper runs a daemon thread that flushes logs every 5 seconds.

## 🟡 Real Example Hindi mein
Swiggy का backend order लगने के बाद SMS और push notification भेजता है: दोनों धीमे network calls हैं, इसलिए हर एक अपने thread में चलता है और API तुरंत जवाब देती है। Download manager हर file के लिए एक thread शुरू करता है। Log shipper एक daemon thread चलाता है जो हर 5 सेकंड में logs flush करता है।

---

## 💻 Code Example — Basic
```python
# Basic Thread usage - every line commented
import threading  # thread support
import time  # for sleeping
from typing import List  # type hints


def worker(name: str, delay: float, out: List[str]) -> None:  # the function a thread will run
    time.sleep(delay)  # pretend to do slow work
    out.append(f"{name} done in {threading.current_thread().name}")  # record which thread ran it


out: List[str] = []  # shared list to collect results (list.append is thread-safe)
t = threading.Thread(target=worker, args=("A", 0.05, out), name="worker-A")  # create, not started
print(t.is_alive(), t.name, t.daemon)  # before start: not alive
# Output: False worker-A False
t.start()  # launch the thread
print(t.is_alive())  # now running (sleeping)
# Output: True
t.join()  # wait for it to finish
print(t.is_alive(), out)  # finished and result recorded
# Output: False ['A done in worker-A']

try:  # a thread can only be started once
    t.start()  # second start
except RuntimeError as e:  # Python refuses
    print("RuntimeError:", e)  # message
# Output: RuntimeError: threads can only be started once
```

## 💻 Code Example — Advanced
```python
# Production style: Thread subclass capturing result AND exception, daemon, excepthook, thread-local
import threading  # threads
import time  # sleep
from typing import List, Optional  # type hints


class Downloader(threading.Thread):  # subclass: override run()
    def __init__(self, url: str) -> None:  # constructor
        super().__init__(name=f"dl-{url}")  # always call the parent constructor
        self.url: str = url  # input
        self.result: Optional[str] = None  # output (a Thread cannot "return" a value)
        self.error: Optional[BaseException] = None  # captured exception

    def run(self) -> None:  # this body runs in the new thread
        try:  # protect the thread from dying silently
            if "bad" in self.url:  # simulate a failure
                raise ValueError("bad url")  # error inside the thread
            self.result = f"data:{self.url}"  # store the result
        except BaseException as exc:  # capture so the caller can inspect
            self.error = exc  # keep the error


threads: List[Downloader] = [Downloader(u) for u in ("a", "bad", "c")]  # three jobs
for th in threads:  # start all
    th.start()
for th in threads:  # wait for all, with a safety timeout
    th.join(timeout=2)
print([(th.url, th.result, repr(th.error)) for th in threads])  # inspect outcomes
# Output: [('a', 'data:a', 'None'), ('bad', None, "ValueError('bad url')"), ('c', 'data:c', 'None')]

# Daemon thread: killed automatically when the main program exits
d = threading.Thread(target=lambda: time.sleep(10), daemon=True)  # would otherwise block exit
d.start()  # start it
print(d.daemon, d.is_alive())  # daemon and running
# Output: True True


# Uncaught exceptions in threads are printed, not raised in the caller: use excepthook
def boom() -> None:  # a function that fails
    raise RuntimeError("oops")  # error


def hook(args: threading.ExceptHookArgs) -> None:  # custom handler (send to Sentry etc.)
    print("hook:", args.exc_type.__name__, args.exc_value)  # log it


threading.excepthook = hook  # install global hook (Python 3.8+)
b = threading.Thread(target=boom)  # thread that fails
b.start()  # run
b.join()  # wait
# Output: hook: RuntimeError oops

# threading.local: each thread sees its own value
tl = threading.local()  # thread-local storage
res: List[int] = []  # results


def setter(v: int) -> None:  # store and read back a per-thread value
    tl.v = v  # set my own value
    time.sleep(0.01)  # let other threads run
    res.append(tl.v)  # still my own value


ths = [threading.Thread(target=setter, args=(i,)) for i in range(3)]  # three threads
[x.start() for x in ths]  # start all
[x.join() for x in ths]  # wait all
print(sorted(res))  # no value was overwritten by another thread
# Output: [0, 1, 2]
print(threading.main_thread().name)  # the thread running your script
# Output: MainThread
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: real OS threads
import threading
t = threading.Thread(target=work, args=(5,))
t.start()
t.join()
```

```javascript
// JavaScript (Node): worker_threads, rarely needed because of async I/O
const { Worker } = require("worker_threads");
const w = new Worker("./work.js", { workerData: 5 });
w.on("message", (m) => console.log(m));
w.on("exit", () => console.log("done"));
```

Key differences: JS normally avoids threads thanks to `async/await`; Python threads share memory directly (JS workers communicate by messages). A Python `Thread` cannot return a value, so use an attribute, a `Queue`, or `ThreadPoolExecutor` futures.

---

## 🟠 FastAPI Connection
FastAPI itself runs sync (`def`) endpoints in a threadpool. For "fire and forget" jobs use `BackgroundTasks`, which runs the function after the response. A sync task also runs on a worker thread, not the main thread.

```python
import threading  # threads
from typing import Dict  # type hints
from fastapi import BackgroundTasks, FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # create app
LOG: list = []  # where the sync task records its thread

def send_email(to: str) -> None:  # plain def -> FastAPI runs it in a worker thread
    LOG.append((to, threading.current_thread() is threading.main_thread()))  # record

@app.post("/signup")  # POST /signup
def signup(email: str, bg: BackgroundTasks) -> Dict[str, str]:  # sync endpoint
    bg.add_task(send_email, email)  # run after response is sent
    return {"status": "queued"}  # immediate response

client = TestClient(app)
print(client.post("/signup", params={"email": "a@x.com"}).json())
# Output: {'status': 'queued'}
print(LOG[0][0], "ran on main thread:", LOG[0][1])
# Output: a@x.com ran on main thread: False
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling the function instead of passing it
```python
# Wrong - runs work() immediately in the MAIN thread, passes its result as target
t = threading.Thread(target=work(5))

# Correct - pass the function and its args separately
t = threading.Thread(target=work, args=(5,))
```

❌ Mistake 2: Forgetting the comma in a one-item `args`
```python
# Wrong - (5) is just the int 5 -> the thread dies with TypeError: argument after * must be an iterable, not int
t = threading.Thread(target=work, args=(5))

# Correct
t = threading.Thread(target=work, args=(5,))
```

❌ Mistake 3: Forgetting `join()` and using the result too early
```python
# Wrong - result may not be ready
t.start()
print(t.result)          # None

# Correct
t.start()
t.join()
print(t.result)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import threading

def show(i):
    print("run", i)

ts = [threading.Thread(target=show, args=(i,)) for i in range(2)]
for t in ts:
    t.start()
    t.join()
print(threading.active_count())
```

**Answer**:
```
run 0
run 1
1
```
Because `join()` is called inside the loop right after `start()`, each thread finishes before the next one starts, so the output is always ordered and there is no concurrency at all. Start all threads first, then join all of them in a second loop. After both finish only `MainThread` remains, so the count is 1.

---

## ⚫ Interview Questions + Answers

Q1: `start()` vs `run()`?
A1: `start()` creates a new OS thread which then calls `run()`. Calling `run()` directly just executes the function in the current thread.

Q2: What is a daemon thread?
A2: A background thread that does not keep the program alive. When only daemon threads remain, Python exits and kills them abruptly (no cleanup), so do not use them for work that must finish.

Q3: How do you get a return value from a thread?
A3: Store it on the object, put it in a `queue.Queue`, or use `ThreadPoolExecutor.submit()` which returns a `Future`.

Q4: What happens when a thread raises an exception?
A4: It ends that thread only. The default `threading.excepthook` prints the traceback; the main thread keeps going. Override `threading.excepthook` to log it.

Q5: Can you kill a thread?
A5: No public API. Use a cooperative flag (`threading.Event`) the thread checks, or use processes (which can be terminated).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Slow blocking I/O with libraries that are not async (requests, legacy SDKs)
- Background housekeeping (heartbeats, flushing logs)

❌ Avoid when:
- CPU-heavy work (GIL; use processes)
- Thousands of connections (use asyncio)
- You need to forcibly stop work (use processes)

---

## 📊 Visual Diagram

```
 main:   ──── t.start() ───────────────── t.join() ──── continues
                 │                           ▲
 thread: ────────┴── run(): target(*args) ───┘

 Thread states: created ─► started/running ─► finished (cannot restart)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| target | Function the thread runs | thread जो function चलाए |
| start() | Begin the thread | thread शुरू करना |
| join() | Wait for finish | खत्म होने का इंतज़ार |
| daemon | Dies with the program | program के साथ खत्म होने वाला |
| excepthook | Handler for uncaught thread errors | thread की uncaught errors का handler |
| thread-local | Per-thread private data | हर thread का अपना data |

---

## ⚡ 3-Line Summary
English: Create with `Thread(target, args)`, `start()` to run, `join()` to wait; a thread can't restart or return values. Daemon threads die with the program; capture errors yourself. Start all, then join all.
Hindi: `Thread(target, args)` से बनाएँ, `start()` से चलाएँ, `join()` से इंतज़ार करें; thread दोबारा start नहीं होता और value return नहीं करता। Daemon threads program के साथ खत्म होते हैं; errors खुद capture करें। पहले सब start करें, फिर सब join करें।

---

## ➡️ Next Topic
**224. Thread Synchronization** — race conditions and how locks, queues and barriers fix them.
