---

# 226. Semaphore
# हिंदी में: Semaphore (एक साथ N threads की सीमा)

---

## 🔵 Simple Definition (English)
A `Semaphore` is a counter-based lock that lets up to N threads into a section at once. `acquire()` takes a permit (waits if none are left) and `release()` returns it. `Semaphore(1)` behaves like a Lock.

## 🔵 सरल परिभाषा (Hindi)
`Semaphore` counter पर आधारित lock है जो एक साथ अधिकतम N threads को अंदर आने देता है। `acquire()` एक permit लेता है (न बचे तो इंतज़ार) और `release()` उसे लौटाता है। `Semaphore(1)` एक Lock जैसा चलता है।

---

## 🔴 Problem it Solves
A Lock allows exactly one thread; no lock allows unlimited threads. Real resources have a limit in between: a database allows 10 connections, a vendor API allows 5 parallel calls, a PDF renderer eats 1 GB each. A semaphore enforces "at most N at a time" without writing a pool yourself.

## 🔴 यह क्यों बना? (Hindi)
Lock ठीक एक thread देता है; बिना lock के अनगिनत threads। असली resources की सीमा बीच की होती है: database में 10 connections, vendor API में 5 parallel calls, PDF renderer हर बार 1 GB। Semaphore "एक समय में अधिकतम N" लागू करता है, खुद pool बनाए बिना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → sem = Semaphore(3)            internal counter = 3
Step 2 → acquire(): counter > 0 -> counter -= 1 and continue
Step 3 → acquire(): counter == 0 -> thread sleeps in the waiting line
Step 4 → release(): counter += 1 and wake one waiter
Step 5 → Use "with sem:" so the permit always comes back
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → sem = Semaphore(3)            अंदरूनी counter = 3
Step 2 → acquire(): counter > 0 -> counter -= 1 और आगे बढ़ो
Step 3 → acquire(): counter == 0 -> thread इंतज़ार की कतार में सोता है
Step 4 → release(): counter += 1 और एक waiter जागता है
Step 5 → "with sem:" इस्तेमाल करें ताकि permit हमेशा लौटे
```

---

## 🟡 Real World Example
A Zomato report service lets only 2 heavy PDF exports run at once so the server does not run out of RAM; extra requests queue up. A scraper uses `Semaphore(5)` so it never opens more than 5 simultaneous connections to one site. An AI app limits parallel LLM calls to stay under the provider's rate limit.

## 🟡 Real Example Hindi mein
Zomato की report service एक समय में सिर्फ 2 भारी PDF exports चलने देती है ताकि server की RAM खत्म न हो; बाकी requests कतार में रहती हैं। Scraper `Semaphore(5)` लगाता है ताकि एक site पर 5 से ज़्यादा connections एक साथ न खुलें। AI app provider की rate limit के भीतर रहने के लिए parallel LLM calls सीमित करता है।

---

## 💻 Code Example — Basic
```python
# Basic Semaphore: at most 2 threads inside at once
import threading  # semaphore and threads
import time  # sleep and timing

sem = threading.Semaphore(2)  # two permits
active: int = 0  # how many threads are inside right now
peak: int = 0  # highest value of active
m = threading.Lock()  # protects the two counters


def job(i: int) -> None:  # one unit of limited work
    global active, peak  # module counters
    with sem:  # wait for a permit
        with m:  # update counters safely
            active += 1  # one more inside
            peak = max(peak, active)  # remember the maximum
        time.sleep(0.05)  # pretend work
        with m:  # leaving
            active -= 1  # one less inside


ts = [threading.Thread(target=job, args=(i,)) for i in range(6)]  # six threads, two permits
start: float = time.perf_counter()  # start clock
[t.start() for t in ts]  # go
[t.join() for t in ts]  # wait
print("peak:", peak, "| took >=0.15s:", time.perf_counter() - start >= 0.15)  # 3 waves of 2
# Output: peak: 2 | took >=0.15s: True

s = threading.Semaphore(1)  # one permit
print(s.acquire(), s.acquire(blocking=False), s.acquire(timeout=0.05))  # take, fail fast, fail after timeout
# Output: True False False
```

## 💻 Code Example — Advanced
```python
# Production style: rate-limited client with BoundedSemaphore, timeout and finally
import threading  # semaphore
import time  # sleep
from typing import List  # type hints


class RateLimitedClient:  # allows at most N parallel calls
    def __init__(self, max_concurrent: int) -> None:  # constructor
        self._sem: threading.BoundedSemaphore = threading.BoundedSemaphore(max_concurrent)  # bounded = catches extra release
        self.calls: List[int] = []  # completed call ids (list.append is atomic)

    def call(self, i: int) -> str:  # one limited call
        if not self._sem.acquire(timeout=1):  # do not wait forever
            raise TimeoutError("service busy")  # tell the caller
        try:  # permit held
            time.sleep(0.01)  # pretend network call
            self.calls.append(i)  # record it
            return f"resp-{i}"  # fake response
        finally:  # ALWAYS give the permit back
            self._sem.release()  # release


client = RateLimitedClient(3)  # three at a time
ths = [threading.Thread(target=client.call, args=(i,)) for i in range(8)]  # eight callers
[t.start() for t in ths]  # start
[t.join() for t in ths]  # wait
print(sorted(client.calls))  # all eight finished
# Output: [0, 1, 2, 3, 4, 5, 6, 7]

# Semaphore vs BoundedSemaphore: extra release
loose = threading.Semaphore(1)  # unbounded
loose.release(); loose.release()  # counter silently becomes 3 (a bug that goes unnoticed)
print("semaphore allows extra release")
# Output: semaphore allows extra release
bounded = threading.BoundedSemaphore(1)  # bounded
try:  # releasing more than acquired
    bounded.release()  # too many
except ValueError as e:  # detected
    print("ValueError:", e)
# Output: ValueError: Semaphore released too many times

# Semaphore(0) as a one-way signal
signal = threading.Semaphore(0)  # no permits yet
got: List[str] = []  # result


def waiter() -> None:  # waits for the signal
    signal.acquire()  # blocks until someone releases
    got.append("signalled")  # proceed


t = threading.Thread(target=waiter)  # thread
t.start()  # it blocks
signal.release()  # give one permit
t.join()  # done
print(got)
# Output: ['signalled']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
sem = threading.Semaphore(3)
with sem:
    call_api()
```

```javascript
// JavaScript: use a library such as p-limit for the same idea
import pLimit from "p-limit";
const limit = pLimit(3);                     // 3 concurrent tasks
await Promise.all(urls.map(u => limit(() => fetch(u))));
```

Key differences: JS limits concurrent promises (`p-limit`, `async-sema`); Python has `threading.Semaphore` for threads and `asyncio.Semaphore` for coroutines (use the matching one). Both work the same way: a counter of permits.

---

## 🟠 FastAPI Connection
Protect an expensive sync endpoint (report, PDF, model inference) with a semaphore so only a few run at once; the rest wait their turn instead of crashing the server. In `async def` endpoints use `asyncio.Semaphore` instead.

```python
import threading, time  # semaphore, sleep
from typing import Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client
from concurrent.futures import ThreadPoolExecutor  # parallel callers

app: FastAPI = FastAPI()  # create app
pdf_slots = threading.BoundedSemaphore(2)  # at most 2 heavy PDF jobs
state = {"active": 0, "peak": 0}  # observed concurrency
m = threading.Lock()  # guards the counters

@app.get("/report")  # sync endpoint -> runs in threadpool
def report() -> Dict[str, str]:
    with pdf_slots:  # wait for a free slot
        with m:
            state["active"] += 1; state["peak"] = max(state["peak"], state["active"])
        time.sleep(0.05)  # pretend to render
        with m:
            state["active"] -= 1
    return {"status": "done"}  # response

client = TestClient(app)
with ThreadPoolExecutor(6) as ex:
    list(ex.map(lambda _: client.get("/report"), range(6)))
print("peak concurrent:", state["peak"])
# Output: peak concurrent: 2
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to release on errors
```python
# Wrong - exception leaks a permit; after N failures everything hangs
sem.acquire()
call_api()
sem.release()

# Correct
with sem:
    call_api()
```

❌ Mistake 2: Using `Semaphore` where a bug could over-release
```python
# Wrong - counter grows silently
sem = threading.Semaphore(2)

# Correct - BoundedSemaphore raises ValueError on extra release
sem = threading.BoundedSemaphore(2)
```

❌ Mistake 3: Mixing thread and asyncio semaphores
```python
# Wrong - blocks the whole event loop
async def h():
    with threading.Semaphore(2): ...

# Correct
sem = asyncio.Semaphore(2)
async def h():
    async with sem: ...
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print and why?

```python
import threading
s = threading.Semaphore(0)
print(s.acquire(timeout=0.1))
s.release()
print(s.acquire(timeout=0.1))
print(s.acquire(blocking=False))
```

**Answer**:
```
False
True
False
```
Starting with 0 permits, the first `acquire` times out. After one `release` there is one permit, so the second acquire succeeds and uses it. The third finds none and fails immediately. Semaphore(0) is a valid way to build "wait until someone signals".

---

## ⚫ Interview Questions + Answers

Q1: Semaphore vs Lock?
A1: A Lock admits one thread; a Semaphore admits N. A Lock released by any thread also works (plain Lock has no owner), but semantically it is "mutual exclusion", while a semaphore is "resource counting".

Q2: Semaphore vs BoundedSemaphore?
A2: Bounded raises `ValueError` if released more times than acquired, catching bugs. Prefer it.

Q3: How to limit 5 concurrent async HTTP calls?
A3: `asyncio.Semaphore(5)` with `async with sem:` around each call (or `httpx` connection limits).

Q4: Can a semaphore deadlock?
A4: Yes, if permits are never returned (missing `finally`) or if a thread needs two semaphores and others hold them in the opposite order.

Q5: What is a "binary semaphore"?
A5: `Semaphore(1)`: like a lock, but can be released by a different thread than the one that acquired.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Limiting concurrent access to a pool-like resource (DB, API, GPU, RAM-heavy jobs)
- Simple one-shot signalling with `Semaphore(0)`

❌ Avoid when:
- You need strict mutual exclusion (use Lock)
- You are inside asyncio (use `asyncio.Semaphore`)
- A `ThreadPoolExecutor(max_workers=N)` already gives the limit

---

## 📊 Visual Diagram

```
 Semaphore(2)                 permits: [●][●]
 T1 acquire ► ●  inside        T2 acquire ► ●  inside
 T3 acquire ► (no permit) ...waits
 T1 release ► permit returns ► T3 enters
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Permit | One unit of the counter | counter की एक इकाई |
| acquire | Take a permit (may wait) | permit लेना |
| release | Return a permit | permit लौटाना |
| BoundedSemaphore | Errors on extra release | extra release पर error |
| Rate limiting | Cap parallel calls | parallel calls की सीमा |
| Back-pressure | Making callers wait | callers को इंतज़ार कराना |

---

## ⚡ 3-Line Summary
English: A Semaphore allows at most N threads inside a section. Prefer `BoundedSemaphore`, always use `with`, and use `asyncio.Semaphore` in async code. It is the tool for pool-like resource limits.
Hindi: Semaphore किसी हिस्से में अधिकतम N threads आने देता है। `BoundedSemaphore` चुनें, हमेशा `with` इस्तेमाल करें, और async code में `asyncio.Semaphore`। यह pool जैसे resource limits का tool है।

---

## ➡️ Next Topic
**227. Event + Condition** — signalling between threads and waiting for a state to become true.
