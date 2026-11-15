---

# 227. Event + Condition
# हिंदी में: Event और Condition (threads के बीच signal देना)

---

## 🔵 Simple Definition (English)
An `Event` is a simple flag threads can wait on: `wait()` blocks until another thread calls `set()`. A `Condition` is a lock plus a waiting room: threads wait until some state becomes true (`wait_for(predicate)`) and others call `notify_all()` after changing that state.

## 🔵 सरल परिभाषा (Hindi)
`Event` एक सरल flag है जिसका threads इंतज़ार कर सकते हैं: `wait()` तब तक block रहता है जब तक कोई दूसरा thread `set()` न करे। `Condition` एक lock और waiting room है: threads तब तक इंतज़ार करते हैं जब तक कोई state सही न हो (`wait_for(predicate)`) और दूसरे state बदलकर `notify_all()` करते हैं।

---

## 🔴 Problem it Solves
Without signalling, a thread must poll in a loop (`while not ready: time.sleep(0.1)`), wasting CPU and reacting slowly. Event and Condition let a thread sleep with zero CPU until it is woken at exactly the right moment: "server is ready", "shutdown requested", "queue has space".

## 🔴 यह क्यों बना? (Hindi)
Signal के बिना thread को loop में बार-बार जाँचना पड़ता है (`while not ready: time.sleep(0.1)`), जिससे CPU खर्च होती है और प्रतिक्रिया धीमी रहती है। Event और Condition thread को बिना CPU खर्च किए सुला देते हैं और सही पल पर जगाते हैं: "server तैयार है", "shutdown माँगा गया", "queue में जगह है"।

---

## 🟢 How it Works — Step by Step

```
Event:
Step 1 → ev = Event()            flag = False
Step 2 → waiter: ev.wait()       sleeps until flag is True (or timeout)
Step 3 → setter: ev.set()        flag = True, wakes ALL waiters
Step 4 → ev.clear()              flag back to False (reusable)

Condition:
Step 1 → with cond:              take the underlying lock
Step 2 → cond.wait_for(pred)     release lock + sleep; re-check pred on wake-up
Step 3 → other thread: change state, cond.notify_all()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Event:
Step 1 → ev = Event()            flag = False
Step 2 → waiter: ev.wait()       flag True होने (या timeout) तक सोता है
Step 3 → setter: ev.set()        flag = True, सभी waiters जागते हैं
Step 4 → ev.clear()              flag फिर False (दोबारा इस्तेमाल)

Condition:
Step 1 → with cond:              अंदर का lock लें
Step 2 → cond.wait_for(pred)     lock छोड़कर सोता है; जागने पर pred फिर जाँचता है
Step 3 → दूसरा thread: state बदलकर cond.notify_all()
```

---

## 🟡 Real World Example
A health-check script waits on an `Event` that the app sets once the database connection is ready. A background worker (log shipper, metrics pusher) loops `while not stop.is_set()` and is shut down by `stop.set()` during deployment. A bounded job buffer between an order-intake thread and a packer thread uses a `Condition`: producers wait when full, consumers wait when empty.

## 🟡 Real Example Hindi mein
Health-check script एक `Event` का इंतज़ार करती है जिसे app तब set करता है जब database connection तैयार हो। Background worker (log shipper, metrics pusher) `while not stop.is_set()` में चलता है और deployment के समय `stop.set()` से बंद होता है। Order-intake thread और packer thread के बीच bounded job buffer `Condition` इस्तेमाल करता है: भरा हो तो producers इंतज़ार करते हैं, खाली हो तो consumers।

---

## 💻 Code Example — Basic
```python
# Basic Event usage - every line commented
import threading  # Event
import time  # sleep
from typing import List  # type hints

ev = threading.Event()  # flag starts as False
print(ev.is_set(), ev.wait(timeout=0.05))  # nobody set it: wait times out and returns False
# Output: False False

log: List[str] = []  # collects messages


def waiter() -> None:  # sleeps until the flag is set
    ev.wait()  # blocks with no CPU use
    log.append("started")  # runs after set()


t = threading.Thread(target=waiter)  # create the waiter
t.start()  # run it (it blocks)
ev.set()  # wake it up
t.join()  # wait for it to finish
print(log, ev.is_set())  # the flag stays True after set()
# Output: ['started'] True
ev.clear()  # reset the flag
print(ev.is_set())  # reusable
# Output: False

# Graceful shutdown pattern
stop = threading.Event()  # shutdown signal
ticks: List[int] = []  # work counter


def loop() -> None:  # background worker
    while not stop.is_set():  # keep going until asked to stop
        ticks.append(1)  # do one unit of work
        stop.wait(0.01)  # sleep 10 ms BUT wake instantly if stop is set


w = threading.Thread(target=loop)  # worker
w.start()  # begin
time.sleep(0.05)  # let it run a little
stop.set()  # ask it to stop
w.join()  # wait for a clean exit
print(len(ticks) >= 2, w.is_alive())  # it worked, and it has stopped
# Output: True False
```

## 💻 Code Example — Advanced
```python
# Production style: bounded buffer with Condition.wait_for
import threading  # Condition
from collections import deque  # fast queue
from typing import Deque, List  # type hints


class Buffer:  # bounded producer/consumer buffer
    def __init__(self, cap: int) -> None:  # constructor
        self.items: Deque[int] = deque()  # storage
        self.cap: int = cap  # maximum size
        self.cond: threading.Condition = threading.Condition()  # lock + waiting room

    def put(self, x: int) -> None:  # add an item
        with self.cond:  # take the lock
            self.cond.wait_for(lambda: len(self.items) < self.cap)  # sleep while full (re-checks the predicate)
            self.items.append(x)  # there is space now
            self.cond.notify_all()  # wake consumers (and other producers)

    def get(self) -> int:  # remove an item
        with self.cond:  # take the lock
            self.cond.wait_for(lambda: len(self.items) > 0)  # sleep while empty
            x: int = self.items.popleft()  # take the oldest
            self.cond.notify_all()  # wake producers waiting for space
            return x  # give it back


buf = Buffer(2)  # capacity of only 2
out: List[int] = []  # what the consumer received
prod = threading.Thread(target=lambda: [buf.put(i) for i in range(6)])  # produces 0..5
cons = threading.Thread(target=lambda: [out.append(buf.get()) for _ in range(6)])  # consumes 6 items
prod.start(); cons.start()  # run both
prod.join(); cons.join()  # wait for both
print(out)  # order is preserved
# Output: [0, 1, 2, 3, 4, 5]

# wait_for with a timeout returns the predicate result (False = timed out)
c = threading.Condition()  # a fresh condition
with c:  # must hold the lock to wait
    print(c.wait_for(lambda: False, timeout=0.05))  # never true -> False after 0.05s
# Output: False

# wait() without holding the lock is an error
try:  # attempt
    c.wait()  # lock not held
except RuntimeError as e:  # refused
    print("RuntimeError:", e)
# Output: RuntimeError: cannot wait on un-acquired lock

# One-shot readiness flag for server start-up
ready = threading.Event()  # readiness signal


def start_server() -> None:  # pretend start-up
    import time  # local import for the demo
    time.sleep(0.05)  # warm-up
    ready.set()  # announce readiness


threading.Thread(target=start_server).start()  # start in background
print("ready:", ready.wait(timeout=1))  # wait up to 1 second
# Output: ready: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: Event as a gate
ready = threading.Event()
threading.Thread(target=lambda: (setup(), ready.set())).start()
ready.wait()
```

```javascript
// JavaScript: a promise is the "event"
let resolveReady;
const ready = new Promise(r => (resolveReady = r));
setup().then(() => resolveReady());
await ready;
// Or Node's EventEmitter: emitter.once("ready", cb)
```

Key differences: A JS Promise resolves once, like a one-shot Event. A Python Event can be `clear()`ed and reused. Python's `Condition` has no direct JS twin; it is a lock + signalling for shared state, which JS rarely needs because there are no preemptive threads.

---

## 🟠 FastAPI Connection
Use an `Event` to stop a background thread cleanly when the app shuts down. The `lifespan` function starts the worker at startup and sets the stop flag at shutdown.

```python
import threading  # event
from contextlib import asynccontextmanager  # lifespan helper
from typing import AsyncIterator, Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

stop: threading.Event = threading.Event()  # shutdown signal
ticks: list = []  # work done by the worker

def worker() -> None:  # background loop
    while not stop.is_set():  # run until asked to stop
        ticks.append(1)  # do a unit of work
        stop.wait(0.01)  # sleep, but wake instantly on stop

@asynccontextmanager  # lifespan = startup + shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    t = threading.Thread(target=worker); t.start()  # startup
    yield  # app serves requests
    stop.set(); t.join()  # shutdown: signal and wait

app: FastAPI = FastAPI(lifespan=lifespan)  # attach lifespan

@app.get("/health")  # GET /health
def health() -> Dict[str, bool]:
    return {"worker_alive": not stop.is_set()}  # status

with TestClient(app) as client:  # runs lifespan
    print(client.get("/health").json())
# Output: {'worker_alive': True}
print("stopped cleanly:", stop.is_set(), len(ticks) >= 1)
# Output: stopped cleanly: True True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Busy-waiting instead of an Event
```python
# Wrong - burns CPU or reacts slowly
while not ready_flag:
    time.sleep(0.1)

# Correct
ready.wait()
```

❌ Mistake 2: `Condition.wait()` with `if` instead of a loop / `wait_for`
```python
# Wrong - spurious wake-ups or another consumer may have taken the item
with cond:
    if not items:
        cond.wait()
    x = items.pop()

# Correct
with cond:
    cond.wait_for(lambda: items)
    x = items.pop()
```

❌ Mistake 3: Changing state without notifying
```python
# Wrong - waiters sleep forever
with cond:
    items.append(x)

# Correct
with cond:
    items.append(x)
    cond.notify_all()
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import threading
e = threading.Event()
e.set()
print(e.wait(0.1))
e.clear()
print(e.wait(0.1))
c = threading.Condition()
with c:
    print(c.wait(0.1))
```

**Answer**:
```
True
False
False
```
`wait()` on a set Event returns `True` at once; after `clear()` it times out and returns `False`. `Condition.wait(timeout)` also returns `False` on timeout (there was no notify). Note: `Event.wait` returns the flag, `Condition.wait` returns `True` only if notified.

---

## ⚫ Interview Questions + Answers

Q1: Event vs Condition?
A1: Event is a boolean flag with wait/set/clear, good for one-to-many signals. Condition guards arbitrary shared state with a lock and supports notify/notify_all, good for producer-consumer logic.

Q2: Why must `wait()` be called inside `with cond`?
A2: `wait` atomically releases the lock while sleeping and re-acquires it on wake-up. Without holding the lock you get `RuntimeError`.

Q3: `notify()` vs `notify_all()`?
A3: `notify(n=1)` wakes one waiter (or n); `notify_all()` wakes all. Use `notify_all` unless you are sure which waiter should run, since waiters may be waiting for different predicates.

Q4: What are spurious wake-ups?
A4: A waiter may wake without the state it wanted being true. Always re-check the predicate: use `wait_for(predicate)`.

Q5: Why use `stop.wait(0.01)` instead of `time.sleep(0.01)`?
A5: Both pause, but `Event.wait` returns immediately when set, giving instant shutdown.

---

## 🔷 When to Use + When Not to Use

✅ Use Event when:
- Many threads wait for one "go/stop/ready" signal

✅ Use Condition when:
- Waiters depend on a changing shared state (buffer full/empty)

❌ Avoid when:
- A `queue.Queue` already does the job (it uses Conditions inside)
- You are in asyncio (use `asyncio.Event` / `asyncio.Condition`)

---

## 📊 Visual Diagram

```
 Event:   waiter1 ─┐
          waiter2 ─┼─ wait() ... sleeping ...  set() ──► all wake up
          waiter3 ─┘

 Condition (bounded buffer):
   producer: wait_for(not full)  → append → notify_all ─┐
   consumer: wait_for(not empty) → pop    → notify_all ◄┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event | Waitable boolean flag | इंतज़ार योग्य flag |
| set / clear | Raise / lower the flag | flag उठाना / गिराना |
| Condition | Lock + wait/notify | lock के साथ wait/notify |
| Predicate | Test for the awaited state | जिस state का इंतज़ार है उसकी जाँच |
| Spurious wake-up | Waking without the state ready | बिना state तैयार हुए जागना |
| Busy-waiting | Polling in a loop | बार-बार जाँचना |

---

## ⚡ 3-Line Summary
English: Event is a reusable flag; Condition is a lock with wait/notify for shared state. Use `wait_for(predicate)` and always notify after changing state. Use Event for clean shutdown signals.
Hindi: Event दोबारा इस्तेमाल होने वाला flag है; Condition shared state के लिए wait/notify वाला lock है। `wait_for(predicate)` इस्तेमाल करें और state बदलने के बाद हमेशा notify करें। साफ shutdown के लिए Event लें।

---

## ➡️ Next Topic
**228. Thread Pool (ThreadPoolExecutor)** — reuse a fixed set of threads and get results via Futures.
