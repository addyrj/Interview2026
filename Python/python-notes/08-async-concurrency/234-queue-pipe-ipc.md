---

# 234. Queue + Pipe (IPC)
# हिंदी में: Queue + Pipe (IPC) — Processes के बीच बात-चीत

---

## 🔵 Simple Definition (English)
IPC means Inter-Process Communication. Processes do not share memory, so they send messages. `multiprocessing.Queue` is a safe many-producers / many-consumers queue. `multiprocessing.Pipe` is a fast two-ended connection between exactly two processes.

## 🔵 सरल परिभाषा (Hindi)
IPC यानी Inter-Process Communication। Processes memory share नहीं करते, इसलिए वे messages भेजते हैं। `multiprocessing.Queue` कई producers / कई consumers के लिए सुरक्षित queue है। `multiprocessing.Pipe` ठीक दो processes के बीच तेज़ दो-तरफा connection है।

---

## 🔴 Problem it Solves
Two Python processes have separate memory. If a child appends to a list, the parent never sees it. You need a safe way to pass data: not a plain `list` (copied, not shared), not a file (slow, needs locking). Queue and Pipe move Python objects between processes by pickling them, and handle the locking so you do not write your own.

## 🔴 यह क्यों बना? (Hindi)
दो Python processes की memory अलग होती है। Child अगर list में append करे तो parent को कभी नहीं दिखता। Data भेजने का सुरक्षित तरीका चाहिए: सामान्य `list` नहीं (copy होती है, share नहीं), file भी नहीं (धीमी, locking चाहिए)। Queue और Pipe Python objects को pickle करके processes के बीच भेजते हैं और locking खुद संभालते हैं, ताकि आपको अपना लिखना न पड़े।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Queue() creates an OS pipe + locks + a background "feeder thread"
Step 2 → put(obj): obj goes to an internal buffer; the feeder thread pickles it
         and writes the bytes into the pipe (so put() returns fast)
Step 3 → get(): reads bytes from the pipe, unpickles, returns a NEW copy
Step 4 → Pipe() returns two Connection objects (duplex=True: both can send+recv)
Step 5 → conn.send(obj) pickles and writes; conn.recv() blocks until data arrives
Step 6 → A sentinel value (None / -1) tells the reader "no more data"

producer process --put--> [ Queue ] --get--> consumer process
process A <--send/recv--> Pipe <--send/recv--> process B
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Queue() एक OS pipe + locks + background "feeder thread" बनाता है
Step 2 → put(obj): obj internal buffer में जाता है; feeder thread उसे pickle करके
         pipe में लिखता है (इसलिए put() जल्दी लौटता है)
Step 3 → get(): pipe से bytes पढ़ता है, unpickle करता है, NEW copy लौटाता है
Step 4 → Pipe() दो Connection objects देता है (duplex=True: दोनों send+recv कर सकते हैं)
Step 5 → conn.send(obj) pickle करके लिखता है; conn.recv() data आने तक रुकता है
Step 6 → Sentinel value (None / -1) reader को बताती है "अब data नहीं आएगा"
```

---

## 🟡 Real World Example
A video-processing pipeline at a Hotstar-style platform: one process reads frames and puts them on a Queue, four worker processes take frames, process them and put results on a second Queue, and one writer process saves output. A trading bot uses a Pipe between the market-data process and the strategy process because it is the lowest-latency channel for exactly two parties. Gunicorn-style supervisors use pipes to talk to workers.

## 🟡 Real Example Hindi mein
Hotstar जैसे platform की video-processing pipeline: एक process frames पढ़कर Queue में डालता है, चार worker processes frames लेकर process करते हैं और नतीजे दूसरी Queue में डालते हैं, और एक writer process output save करता है। Trading bot में market-data process और strategy process के बीच Pipe इस्तेमाल होता है क्योंकि सिर्फ दो पक्षों के लिए यह सबसे कम latency वाला channel है। Gunicorn जैसे supervisors workers से pipes के ज़रिये बात करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: multiprocessing Queue and Pipe
from multiprocessing import Process, Queue, Pipe           # processes + IPC tools
from multiprocessing.connection import Connection          # type for pipe ends


def producer(q: "Queue[int]") -> None:                      # runs in child process
    for i in range(3):                                      # send three numbers
        q.put(i * 10)                                       # put pickles the item into the queue
    q.put(-1)                                               # sentinel: "no more data"


def echo(conn: Connection) -> None:                         # child end of the pipe
    msg: str = conn.recv()                                  # wait for a message from parent
    conn.send(msg.upper())                                  # reply on the same connection
    conn.close()                                            # close our end


if __name__ == "__main__":                                  # needed because of spawn
    q: "Queue[int]" = Queue()                               # process-safe queue
    p = Process(target=producer, args=(q,))                 # child that fills the queue
    p.start()                                               # launch it
    while (item := q.get()) != -1:                          # read until sentinel
        print("got", item)                                  # parent consumes
    p.join()                                                # wait for child to exit

    parent_conn, child_conn = Pipe()                        # duplex pipe: two ends
    p2 = Process(target=echo, args=(child_conn,))           # child gets one end
    p2.start()                                              # launch
    parent_conn.send("hello")                               # parent sends
    print(parent_conn.recv())                               # parent receives HELLO
    p2.join()                                               # clean up

# Output:
# got 0
# got 10
# got 20
# HELLO
```

## 💻 Code Example — Advanced
```python
# Production style: worker pool with task queue, result queue, sentinels, and error reporting
import multiprocessing as mp                                # short alias
from multiprocessing import Queue                           # process-safe queue
from typing import Any                                      # for loose types

STOP = None                                                 # sentinel: tells a worker to stop


def worker(wid: int, tasks: "Queue[Any]", results: "Queue[Any]") -> None:
    while True:                                             # loop until we get the sentinel
        job = tasks.get()                                   # blocks until a job arrives
        if job is STOP:                                     # shutdown signal
            break                                           # leave the loop
        try:                                                # never let a worker crash silently
            results.put((job, job * job, None))             # (input, output, error)
        except Exception as exc:                            # report errors instead of dying
            results.put((job, None, str(exc)))              # send error text back


def main() -> None:
    ctx = mp.get_context("spawn")                           # explicit start method = same on all OS
    tasks: "Queue[Any]" = ctx.Queue()                       # jobs go in here
    results: "Queue[Any]" = ctx.Queue()                     # answers come out here
    procs = [ctx.Process(target=worker, args=(i, tasks, results)) for i in range(2)]   # 2 workers
    for p in procs:                                         # start all workers
        p.start()                                           # launch
    for n in range(1, 6):                                   # enqueue 5 jobs
        tasks.put(n)                                        # producer side
    for _ in procs:                                         # one sentinel per worker
        tasks.put(STOP)                                     # tell each to stop
    collected = [results.get(timeout=10) for _ in range(5)]   # drain BEFORE join (avoid deadlock)
    for p in procs:                                         # now wait for exit
        p.join()                                            # reap processes
    for job, out, err in sorted(collected):                 # sort: workers finish in any order
        print(job, out, err)                                # show result


if __name__ == "__main__":                                  # spawn guard
    main()                                                  # run

# Output (verified on Python 3.13; sorted, so order is stable):
# 1 1 None
# 2 4 None
# 3 9 None
# 4 16 None
# 5 25 None
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript / Node.js |
|---------|--------|---------------------|
| Many-to-many messages | `multiprocessing.Queue` | no built-in (Redis / BullMQ) |
| Two-party channel | `Pipe()` | `worker.postMessage` / `process.send` |
| Receive | `conn.recv()` blocking | `on('message', cb)` event |
| Data format | pickle | structured clone / JSON |
| Stop signal | sentinel value | `worker.terminate()` or message |

```python
# Python way — blocking recv in the child
from multiprocessing import Process, Pipe               # tools

def child(conn) -> None:                                 # child function
    conn.send(conn.recv() + 1)                           # wait, add one, reply

if __name__ == "__main__":                               # spawn guard
    a, b = Pipe()                                        # two ends
    p = Process(target=child, args=(b,)); p.start()      # start child
    a.send(41); print(a.recv()); p.join()                # 42
```
```javascript
// JavaScript way — event based, worker_threads
const { Worker, isMainThread, parentPort } = require('worker_threads');
if (isMainThread) {
  const w = new Worker(__filename);                      // same file as worker
  w.on('message', m => console.log(m));                  // 42
  w.postMessage(41);                                     // send
} else {
  parentPort.on('message', n => parentPort.postMessage(n + 1));   // reply
}
```

Key difference: Python's `recv()` and `get()` block the calling thread, JS is callback/event based. Never call them directly inside an `async def` handler, wrap with `run_in_executor` or use `get_nowait`.

---

## 🟠 FastAPI Connection
FastAPI itself seldom uses raw IPC, but it appears when you run a separate worker process (ML model, video encoder) next to the API. The API puts a job on a `multiprocessing.Queue`; a worker process reads it. Because `Queue.get()` blocks, read the result queue from a thread with `run_in_executor`. A simple pattern (the queue is created at module import, workers started in lifespan):

```python
# FastAPI example — send jobs to a worker process and wait for the answer
import asyncio                                            # event loop access
import multiprocessing as mp                              # processes + queues
from contextlib import asynccontextmanager                # lifespan helper
from fastapi import FastAPI                               # FastAPI


def model_worker(inbox, outbox) -> None:                  # runs in another process
    while (x := inbox.get()) is not None:                 # None = stop
        outbox.put(x * 2)                                 # pretend inference


@asynccontextmanager                                      # startup + shutdown
async def lifespan(app: FastAPI):
    ctx = mp.get_context("spawn")                         # same on every OS
    app.state.inbox, app.state.outbox = ctx.Queue(), ctx.Queue()   # two queues
    app.state.proc = ctx.Process(target=model_worker, args=(app.state.inbox, app.state.outbox))
    app.state.proc.start()                                # launch worker
    yield                                                 # serve requests
    app.state.inbox.put(None)                             # ask worker to stop
    app.state.proc.join()                                 # wait for it


app: FastAPI = FastAPI(lifespan=lifespan)                 # create app


@app.get("/predict/{x}")                                  # GET /predict/21
async def predict(x: int) -> dict[str, int]:
    app.state.inbox.put(x)                                # put() is quick and non-blocking
    loop = asyncio.get_running_loop()                     # current loop
    y: int = await loop.run_in_executor(None, app.state.outbox.get)   # blocking get in a thread
    return {"y": y}                                       # {"y": 42}
```
(Run with TestClient on 3.13, returns {"y": 42}; with many concurrent requests you must match replies to requests with an id.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling `join()` before draining the result queue
✅ Correct: read all results first, then join (a child cannot exit while its queue buffer still holds unflushed data, so join waits forever)

```python
# Wrong — deadlock possible when results are large
# for p in procs: p.join()
# results = [results_q.get() for _ in range(n)]
# Right
# results = [results_q.get() for _ in range(n)]
# for p in procs: p.join()
```

❌ Mistake 2: Trusting `q.empty()` / `q.qsize()` to decide whether to `get()`
✅ Correct: use sentinels or `get(timeout=...)`; `qsize()` is not implemented on macOS and `empty()` is unreliable

```python
# Wrong
# while not q.empty(): item = q.get()     # may stop too early, or block forever
# Right
# while (item := q.get()) is not None:    # sentinel ends the loop
#     handle(item)
```

❌ Mistake 3: Sending unpicklable objects (locks, open files, DB connections, lambdas)
✅ Correct: send plain data (ids, strings, dicts); open connections inside the receiving process

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import time
from multiprocessing import Process, Queue

def child(q: "Queue[list[int]]") -> None:
    data = q.get()
    data.append(99)
    print("child sees", data)

if __name__ == "__main__":
    q: "Queue[list[int]]" = Queue()
    mine = [1, 2]
    q.put(mine)
    time.sleep(0.2)
    mine.append(3)
    p = Process(target=child, args=(q,)); p.start(); p.join()
    print("parent has", mine)
```
Answer: `child sees [1, 2, 99]` then `parent has [1, 2, 3]` (verified on 3.13). The queue sends a pickled COPY, so the child never sees `3` and the parent never sees `99`. Subtle point: `put()` returns immediately and a background feeder thread does the pickling. Without the `sleep`, the `append(3)` can happen before pickling and the child would see `[1, 2, 3, 99]`. It is a race, so never mutate an object after `put()`.

---

## ⚫ Interview Questions + Answers

Q1: Queue vs Pipe, which one when?
A1: Pipe connects exactly two endpoints and is faster; it is not safe if two processes read or write the same end at once. Queue is built on a pipe plus locks and a feeder thread, so many producers and consumers can share it safely. Use Pipe for 1-to-1, Queue for everything else.

Q2: Why do we need sentinels?
A2: `get()` blocks forever when no data comes. Sending a special value (`None`) per consumer tells each one to exit its loop. With N workers, put N sentinels.

Q3: How is `multiprocessing.Queue` different from `queue.Queue`?
A3: `queue.Queue` works only between threads of one process (shared memory). `multiprocessing.Queue` pickles items and works across processes. `multiprocessing.JoinableQueue` adds `task_done()` / `join()`. `multiprocessing.SimpleQueue` is a simpler lock-and-pipe version without the feeder thread.

Q4: Is data shared through a Queue?
A4: No. It is copied (pickled and unpickled). Changes to the received object do not affect the sender. For big data (arrays, images) pass a name/path or use shared memory and send only the handle.

Q5: What happens when the Queue is full?
A5: `Queue(maxsize=n)`: `put()` blocks until space is available (back-pressure). `put_nowait()` raises `queue.Full`. Unbounded queues (default) can eat all memory if the producer is faster than consumers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Splitting a pipeline into stages that run in different processes
- A pool of workers consumes tasks from one queue
- Two processes need a private fast channel (Pipe)
- Messages are small and picklable

❌ Avoid when:
- Data is large and sent often; use shared memory, send only names
- You just want function results; `ProcessPoolExecutor` is simpler
- Threads inside one process are enough; use `queue.Queue`
- Many machines are involved; use Redis, RabbitMQ or Kafka instead

---

## 📊 Visual Diagram
```
 Queue (many to many)
   producer 1 --\                      /--> worker 1
   producer 2 ---+--> [ item item item ]---> worker 2
   producer 3 --/       pickled bytes  \--> worker 3

 Pipe (exactly two ends)
   process A  conn_a  <========>  conn_b  process B
              send/recv both ways

 Rule: each object is COPIED. Nothing is shared.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IPC | Inter-process communication | Processes के बीच संचार |
| Sentinel | Special value meaning "stop" | रुकने का संकेत देने वाली value |
| Feeder thread | Hidden thread that writes Queue data to the pipe | Queue का data pipe में लिखने वाला छुपा thread |
| Back-pressure | Producer waits when queue is full | Queue भरी हो तो producer का रुकना |
| Duplex | Both directions allowed | दोनों दिशाओं में चलने वाला |
| Pickle | Object to bytes | Object को bytes में बदलना |

---

## ⚡ 3-Line Summary
English: Processes do not share memory, so they pass pickled messages with `Queue` (many-to-many, safe) or `Pipe` (two-party, fast). Always use sentinels, drain results before `join()`, and never mutate an object after `put()`. Both calls block, so keep them off the asyncio event loop.
Hindi: Processes memory share नहीं करते, इसलिए pickled messages `Queue` (many-to-many, सुरक्षित) या `Pipe` (दो पक्ष, तेज़) से भेजते हैं। हमेशा sentinel लगाएं, `join()` से पहले results खाली करें, और `put()` के बाद object में बदलाव न करें। दोनों calls block करती हैं, इसलिए इन्हें asyncio event loop से दूर रखें।

---

## ➡️ Next Topic
**235. Shared Memory** — when copying through queues is too slow, `Value`, `Array` and `shared_memory.SharedMemory` let several processes read and write the same bytes.
