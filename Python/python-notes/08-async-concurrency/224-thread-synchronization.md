---

# 224. Thread Synchronization
# हिंदी में: Thread Synchronization (threads को सुरक्षित तरीके से coordinate करना)

---

## 🔵 Simple Definition (English)
Thread synchronization means controlling how threads touch shared data and wait for each other, so results are correct. Tools: `Lock` for exclusive access, `Queue` for passing work safely, `Barrier` for meeting points, plus `Event`, `Condition` and `Semaphore`.

## 🔵 सरल परिभाषा (Hindi)
Thread synchronization का मतलब है कि threads shared data को कैसे छूते हैं और एक-दूसरे का इंतज़ार कैसे करते हैं, यह नियंत्रित करना ताकि नतीजे सही आएँ। Tools: exclusive access के लिए `Lock`, काम सुरक्षित पास करने के लिए `Queue`, मिलने के बिंदु के लिए `Barrier`, और `Event`, `Condition`, `Semaphore`।

---

## 🔴 Problem it Solves
Threads share memory. Two threads doing `balance = balance - 100` can both read the old value, then both write, losing one update: a race condition. These bugs are random, rare in tests and common in production. Synchronization makes the critical section run one thread at a time.

## 🔴 यह क्यों बना? (Hindi)
Threads memory share करते हैं। दो threads जब `balance = balance - 100` करते हैं तो दोनों पुरानी value पढ़ सकते हैं और फिर दोनों लिखते हैं, एक update खो जाता है: यह race condition है। ये bugs random होते हैं, tests में कम और production में ज़्यादा दिखते हैं। Synchronization critical section को एक समय में एक thread से चलवाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Find shared mutable state (counter, dict, file, balance)
Step 2 → Find the critical section: read -> compute -> write
Step 3 → Protect it:  with lock:  <critical section>
Step 4 → Or avoid sharing: pass work through queue.Queue
Step 5 → Keep the locked region tiny; never block (I/O) while holding a lock
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Shared mutable state पहचानें (counter, dict, file, balance)
Step 2 → Critical section पहचानें: पढ़ना -> गणना -> लिखना
Step 3 → उसे बचाएँ:  with lock:  <critical section>
Step 4 → या sharing से बचें: queue.Queue से काम पास करें
Step 5 → Lock वाला हिस्सा छोटा रखें; lock पकड़े हुए I/O में कभी block न करें
```

---

## 🟡 Real World Example
Razorpay's settlement worker has 8 threads updating a shared "total processed" counter and a dict of per-merchant totals; without a lock the totals drift. A scraper uses a `Queue` so one thread produces URLs and many consumers fetch them. A load-test tool uses a `Barrier` so all 50 virtual users start at the same instant.

## 🟡 Real Example Hindi mein
Razorpay का settlement worker 8 threads से एक shared "total processed" counter और per-merchant totals का dict update करता है; lock के बिना totals गलत हो जाते हैं। Scraper `Queue` इस्तेमाल करता है: एक thread URLs बनाता है और कई consumers fetch करते हैं। Load-test tool `Barrier` इस्तेमाल करता है ताकि सारे 50 virtual users एक ही पल पर शुरू हों।

---

## 💻 Code Example — Basic
```python
# Basic: a race condition and its fix - every line commented
import threading  # threads and locks
import time  # time.sleep(0) forces a thread switch (makes the race visible)

counter: int = 0  # shared state


def unsafe(n: int) -> None:  # read-modify-write WITHOUT protection
    global counter  # we change the module variable
    for _ in range(n):  # repeat n times
        tmp: int = counter  # read
        time.sleep(0)  # yield to another thread (like an unlucky context switch)
        counter = tmp + 1  # write back a stale value


def run(fn, n: int = 200, k: int = 4) -> int:  # run k threads of fn and return the counter
    global counter  # reset shared state
    counter = 0  # start from zero
    ts = [threading.Thread(target=fn, args=(n,)) for _ in range(k)]  # create k threads
    [t.start() for t in ts]  # start them all
    [t.join() for t in ts]  # wait for all
    return counter  # final value (expected k*n)


print(run(unsafe) < 800)  # updates were lost, expected 800
# Output: True   (exact value is random, always less than 800)

lock: threading.Lock = threading.Lock()  # mutual exclusion lock


def safe(n: int) -> None:  # same logic but protected
    global counter  # module variable
    for _ in range(n):  # repeat n times
        with lock:  # only one thread inside at a time
            tmp: int = counter  # read
            time.sleep(0)  # even with a switch point, nobody else can enter
            counter = tmp + 1  # write


print(run(safe))  # now correct
# Output: 800
```

## 💻 Code Example — Advanced
```python
# Production style: Queue (producer/consumer), Barrier, and lock timeout
import threading  # threads
import queue  # thread-safe queue
from typing import List, Optional  # type hints

# --- Producer / consumer with a bounded queue -------------------------------
q: "queue.Queue[Optional[int]]" = queue.Queue(maxsize=3)  # put() blocks when 3 items wait
results: List[int] = []  # filled by the consumer only (no lock needed: single writer)


def producer() -> None:  # generates work
    for i in range(5):  # five jobs
        q.put(i)  # blocks if the queue is full (back-pressure)
    q.put(None)  # sentinel = "no more work"


def consumer() -> None:  # processes work
    while (item := q.get()) is not None:  # stop at the sentinel
        results.append(item * 10)  # "process" the job
        q.task_done()  # tell the queue this item is finished
    q.task_done()  # account for the sentinel


p = threading.Thread(target=producer)  # producer thread
c = threading.Thread(target=consumer)  # consumer thread
p.start(); c.start()  # run both
p.join(); c.join(); q.join()  # wait for threads and for all items to be processed
print(results)  # order preserved by the queue
# Output: [0, 10, 20, 30, 40]

# --- Barrier: wait until all parties arrive ---------------------------------
order: List[str] = []  # event log
barrier = threading.Barrier(3, action=lambda: order.append("all-ready"))  # action runs once when the 3rd arrives


def runner() -> None:  # a participant
    barrier.wait()  # block until 3 threads are here
    order.append("go")  # all continue together


rs = [threading.Thread(target=runner) for _ in range(3)]  # three runners
[r.start() for r in rs]; [r.join() for r in rs]  # run and wait
print(order)  # the barrier action always comes first
# Output: ['all-ready', 'go', 'go', 'go']

# --- Never wait forever: lock with timeout ----------------------------------
guard = threading.Lock()  # a lock
guard.acquire()  # take it and never release (simulates a stuck holder)
print(guard.acquire(timeout=0.1))  # gives up after 0.1s instead of hanging
# Output: False
guard.release()  # clean up
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: shared memory -> you need locks
lock = threading.Lock()
with lock:
    balance -= 100
```

```javascript
// JavaScript: single-threaded event loop -> no data races between callbacks
balance -= 100;   // safe: nothing can interrupt between read and write
// With SharedArrayBuffer + Worker threads you use Atomics:
Atomics.add(view, 0, -100);
```

Key differences: Regular JS code never has this problem because only one callback runs at a time. Python threads are preempted at almost any bytecode boundary, so a read-modify-write like `x += 1` is NOT atomic even with the GIL.

---

## 🟠 FastAPI Connection
Sync (`def`) endpoints run in a threadpool, so shared in-memory state (stock, counters, caches) needs a lock. Remember that each worker process has its own memory: for multi-process deployments use Redis or the database for the shared truth.

```python
import threading  # lock
from typing import Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client
from concurrent.futures import ThreadPoolExecutor  # parallel callers

app: FastAPI = FastAPI()  # create app
stock: Dict[str, int] = {"phone": 5}  # shared in-memory state (one process only!)
lock: threading.Lock = threading.Lock()  # guards stock

@app.post("/buy/{item}")  # sync endpoint -> runs in the threadpool, so threads race
def buy(item: str) -> Dict[str, bool]:
    with lock:  # check-then-update must be atomic
        if stock[item] <= 0:  # sold out?
            return {"ok": False}  # reject
        stock[item] -= 1  # take one unit
        return {"ok": True}  # success

client = TestClient(app)
with ThreadPoolExecutor(8) as ex:  # 8 buyers at once
    results = list(ex.map(lambda _: client.post("/buy/phone").json()["ok"], range(8)))
print(results.count(True), results.count(False), stock)
# Output: 5 3 {'phone': 0}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Believing the GIL makes `counter += 1` safe
```python
# Wrong - it is LOAD, ADD, STORE: a thread switch between them loses updates
counter += 1

# Correct
with lock:
    counter += 1
```

❌ Mistake 2: Holding a lock while doing slow I/O
```python
# Wrong - every other thread waits for the network call
with lock:
    data = requests.get(url).json()
    cache[url] = data

# Correct - do I/O outside, lock only the dict update
data = requests.get(url).json()
with lock:
    cache[url] = data
```

❌ Mistake 3: Acquiring two locks in different orders (deadlock)
```python
# Wrong - thread 1: a then b, thread 2: b then a -> both wait forever
# Correct - always acquire in one global order (e.g. sorted by id) or use a timeout
```

---

## 🧠 Tricky Interview Question

**Q**: Two threads each run `for _ in range(100_000): n += 1` on a global `n` without a lock. What can the final value be, and does the answer change across Python versions?

**Answer**:
```
Anything from 100_000 to 200_000 is allowed by the language.
```
`n += 1` compiles to separate load/add/store steps, so updates can be lost. Whether you actually see lost updates depends on version and timing: in a quick test on Python 3.13 this tiny loop gave exactly 200000 every time, which is why the bug hides in tests and appears in production under different load. Never rely on it; use a `Lock` (or `itertools.count`/`queue` patterns). In free-threaded builds the bug shows up even more easily.

---

## ⚫ Interview Questions + Answers

Q1: What is a race condition?
A1: A bug where the result depends on the timing of threads accessing shared data. Typical pattern: check-then-act or read-modify-write without protection.

Q2: Is `list.append` thread-safe in CPython?
A2: Yes, as an implementation detail that single operations on built-in containers are atomic under the GIL. Compound operations (`if x not in lst: lst.append(x)`) are not.

Q3: Lock vs Queue?
A3: A lock protects shared data; a queue avoids sharing by handing items from one thread to another. Prefer queues: "share memory by communicating".

Q4: What is a deadlock and how do you avoid it?
A4: Threads wait for each other's locks forever. Use a consistent lock order, timeouts on `acquire`, fewer locks, or higher-level tools like queues.

Q5: What does `Queue.join()` do?
A5: Blocks until every item put in the queue has been marked done with `task_done()`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Multiple threads read and write the same variable, dict or file
- You need ordered hand-off of work (Queue)
- You want threads to start together (Barrier)

❌ Avoid when:
- You can use immutable data or per-thread data (`threading.local`)
- Work can be done in separate processes with message passing
- Using asyncio (single thread: no locks needed between awaits, except across `await` points)

---

## 📊 Visual Diagram

```
 WITHOUT lock                       WITH lock
 T1: read 5 ─┐                      T1: [lock] read 5 -> write 6 [unlock]
 T2: read 5 ─┤                      T2:        waits ...  [lock] read 6 -> write 7
 T1: write 6 ┘                      final = 7  (correct)
 T2: write 6      final = 6 (lost update)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Race condition | Result depends on timing | timing पर निर्भर नतीजा |
| Critical section | Code touching shared data | shared data छूने वाला code |
| Lock | Only one thread at a time | एक समय में एक thread |
| Deadlock | Threads wait on each other forever | आपस में हमेशा के लिए अटकना |
| Queue | Thread-safe FIFO hand-off | thread-safe कतार |
| Barrier | Wait until N threads arrive | N threads के आने तक रुकना |

---

## ⚡ 3-Line Summary
English: Shared mutable data needs a lock around read-modify-write, or better, pass data through a Queue. Keep locked sections tiny, use one lock order and timeouts. The GIL does not make compound operations atomic.
Hindi: Shared mutable data के read-modify-write पर lock लगाएँ, या बेहतर, Queue से data पास करें। Lock वाले हिस्से छोटे रखें, एक ही lock order और timeouts रखें। GIL compound operations को atomic नहीं बनाता।

---

## ➡️ Next Topic
**225. Lock + RLock** — the two lock types, re-entrancy and deadlock-safe patterns.
