---

# 414. asyncio for IO Tasks
# हिंदी में: IO वाले कामों के लिए asyncio

---

## 🔵 Simple Definition (English)
`asyncio` runs many tasks that mostly wait (network calls, database queries, file reads) on a single thread. While one task waits at an `await`, the event loop runs another. Total time becomes the slowest wait instead of the sum of all waits.

## 🔵 सरल परिभाषा (Hindi)
`asyncio` एक ही thread पर ऐसे कई tasks चलाता है जो ज़्यादातर इंतज़ार करते हैं (network calls, database queries, file reads)। एक task `await` पर रुकता है तो event loop दूसरा task चला देता है। कुल समय सब waits का जोड़ नहीं, बल्कि सबसे लंबा wait होता है।

---

## 🔴 Problem it Solves
A normal program that calls three APIs one after another waits 3 x latency while the CPU is idle. Using one thread per request costs memory and gets complicated at 10,000 connections. asyncio handles thousands of waiting connections on one thread with very little memory, which is why it suits web servers.

## 🔴 यह क्यों बना? (Hindi)
जो normal program तीन APIs को एक के बाद एक call करता है वह 3 x latency इंतज़ार करता है जबकि CPU खाली बैठता है। हर request के लिए एक thread रखना memory खाता है और 10,000 connections पर जटिल हो जाता है। asyncio एक thread पर हज़ारों इंतज़ार करते connections को बहुत कम memory में सँभालता है, इसीलिए web servers के लिए सही है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → async def creates a coroutine (a paused function); nothing runs yet
Step 2 → asyncio.run() starts the event loop; create_task()/gather() schedule coroutines
Step 3 → A coroutine runs until it hits "await something_slow()"
Step 4 → It pauses and gives control back to the loop (cooperative multitasking)
Step 5 → The loop runs another ready task while the OS waits for the I/O to finish
Step 6 → When the I/O completes, the loop resumes the paused coroutine
Rule   → One blocking call (time.sleep, requests.get, heavy CPU loop) freezes ALL tasks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → async def एक coroutine (रुका हुआ function) बनाता है; अभी कुछ नहीं चलता
Step 2 → asyncio.run() event loop शुरू करता है; create_task()/gather() coroutines schedule करते हैं
Step 3 → Coroutine "await something_slow()" तक चलता है
Step 4 → वह रुककर control loop को लौटा देता है (cooperative multitasking)
Step 5 → I/O पूरा होने तक loop कोई और ready task चलाता है
Step 6 → I/O पूरा होते ही loop रुके हुए coroutine को आगे बढ़ाता है
नियम  → एक भी blocking call (time.sleep, requests.get, भारी CPU loop) सभी tasks को रोक देती है
```

---

## 🟡 Real World Example
A Zomato restaurant page needs menu, offers, reviews and delivery ETA from four services: with `asyncio.gather` the page takes the time of the slowest call (about 200 ms) rather than the sum (about 800 ms). A scraper downloads 1,000 URLs with 50 at a time. An AI app streams LLM tokens to many users at once.

## 🟡 Real Example Hindi mein
Zomato की restaurant page को चार services से menu, offers, reviews और delivery ETA चाहिए: `asyncio.gather` से page को सबसे धीमी call जितना समय (लगभग 200 ms) लगता है, जोड़ (लगभग 800 ms) नहीं। Scraper एक बार में 50 के हिसाब से 1,000 URLs download करता है। AI app एक साथ कई users को LLM tokens stream करता है।

---

## 💻 Code Example — Basic
```python
# Basic: asyncio runs many waiting (I/O) tasks at the same time on ONE thread
import asyncio  # event loop
import time  # timer
from typing import List  # type hints


async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)  # pretend network call: the loop runs other tasks meanwhile
    return f"{name} done"  # result


async def sequential() -> List[str]:
    results: List[str] = []  # collect results
    for name in ["menu", "offers", "reviews"]:  # one after another
        results.append(await fetch(name, 0.3))  # waits 0.3s each -> 0.9s total
    return results  # list of results


async def concurrent() -> List[str]:
    return await asyncio.gather(  # start all three together
        fetch("menu", 0.3), fetch("offers", 0.3), fetch("reviews", 0.3)
    )  # total time is about 0.3s


async def main() -> None:
    t0: float = time.perf_counter()  # start
    r1: List[str] = await sequential()  # slow way
    t_seq: float = time.perf_counter() - t0  # elapsed

    t0 = time.perf_counter()  # start again
    r2: List[str] = await concurrent()  # fast way
    t_con: float = time.perf_counter() - t0  # elapsed

    print(r1 == r2)  # same results
    # Output: True
    print(r2)  # results keep the order of the arguments
    # Output: ['menu done', 'offers done', 'reviews done']
    print(f"sequential ~{t_seq:.1f}s, concurrent ~{t_con:.1f}s")  # rounded timings
    # Output: sequential ~0.9s, concurrent ~0.3s


asyncio.run(main())  # create the loop, run main(), close the loop
```

## 💻 Code Example — Advanced
```python
# Advanced: bounded concurrency, timeout, error isolation, TaskGroup (Python 3.11+)
import asyncio  # event loop
import time  # timer
from typing import Dict, List, Union  # type hints


async def call_api(i: int) -> int:
    await asyncio.sleep(0.1)  # simulated network latency
    if i == 3:  # one failing request
        raise RuntimeError(f"request {i} failed")  # error from the "server"
    return i * 10  # success value


async def limited(sem: asyncio.Semaphore, i: int) -> Union[int, str]:
    async with sem:  # at most N calls in flight (protects the remote API)
        try:  # isolate errors per task
            return await asyncio.wait_for(call_api(i), timeout=1.0)  # never wait forever
        except RuntimeError as exc:  # failed call
            return f"error: {exc}"  # return the error instead of crashing everything


async def slow() -> None:
    await asyncio.sleep(5)  # takes too long


async def main() -> None:
    sem: asyncio.Semaphore = asyncio.Semaphore(5)  # max 5 concurrent calls
    t0: float = time.perf_counter()  # start
    results: List[Union[int, str]] = await asyncio.gather(*(limited(sem, i) for i in range(10)))  # 10 tasks
    elapsed: float = time.perf_counter() - t0  # elapsed
    print(results)  # index 3 shows the error
    # Output: [0, 10, 20, 'error: request 3 failed', 40, 50, 60, 70, 80, 90]
    print("2 waves of 5 -> about 0.2s:", 0.15 < elapsed < 0.5)  # 10 tasks / 5 slots * 0.1s
    # Output: 2 waves of 5 -> about 0.2s: True

    try:  # timeout demo
        await asyncio.wait_for(slow(), timeout=0.2)  # cancels slow() after 0.2s
    except asyncio.TimeoutError:  # raised on timeout
        print("timed out")  # handled
    # Output: timed out

    out: Dict[str, int] = {}  # TaskGroup results
    async with asyncio.TaskGroup() as tg:  # structured concurrency: all finish or all cancel
        async def put(key: str, value: int) -> None:
            await asyncio.sleep(0.05)  # small wait
            out[key] = value  # store
        tg.create_task(put("a", 1))  # schedule
        tg.create_task(put("b", 2))  # schedule
    print(out)  # both finished when the block exits
    # Output: {'a': 1, 'b': 2}

    loop_blocked: float = time.perf_counter()  # demonstrate blocking call
    await asyncio.to_thread(time.sleep, 0.1)  # run blocking code in a thread, not on the loop
    print("blocking call moved to thread:", time.perf_counter() - loop_blocked >= 0.1)  # waited 0.1s
    # Output: blocking call moved to thread: True


asyncio.run(main())  # entry point
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: nothing runs until awaited/scheduled; one explicit event loop
import asyncio

async def fetch(x: int) -> int:
    await asyncio.sleep(0.1)
    return x * 2

async def main():
    print(await asyncio.gather(fetch(1), fetch(2)))   # [2, 4]

asyncio.run(main())
```
```javascript
// JavaScript: promises start immediately; the event loop is built in
const fetchX = async (x) => { await new Promise(r => setTimeout(r, 100)); return x * 2; };
(async () => {
  console.log(await Promise.all([fetchX(1), fetchX(2)]));   // [2, 4]
})();
```

Key differences: a JS promise starts running as soon as it is created, but a Python coroutine does nothing until you `await` it or wrap it with `create_task`/`gather`. JS always has an event loop; Python needs `asyncio.run()`. `asyncio.gather` is like `Promise.all`; `TaskGroup` has no direct JS equivalent. In both languages a blocking CPU loop freezes the loop.

---

## 🟠 FastAPI Connection
FastAPI is built on asyncio (Starlette + uvicorn). An `async def` endpoint runs on the event loop, so use async libraries inside it (`httpx.AsyncClient`, `asyncpg`, async SQLAlchemy, `redis.asyncio`). A plain `def` endpoint runs in a threadpool, which is safe for blocking libraries. Use `asyncio.gather` to run independent downstream calls together.

```python
# FastAPI: await several downstream calls concurrently (pip install fastapi httpx)
import asyncio  # gather
import time  # timing for the demo only
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # test client

app: FastAPI = FastAPI()  # create app


async def get_user(uid: int) -> dict[str, object]:
    await asyncio.sleep(0.2)  # stands in for DB / HTTP call
    return {"id": uid, "name": "Asha"}  # user


async def get_orders(uid: int) -> list[int]:
    await asyncio.sleep(0.2)  # stands in for another call
    return [101, 102]  # orders


@app.get("/profile/{uid}")  # GET /profile/1
async def profile(uid: int) -> dict[str, object]:
    user, orders = await asyncio.gather(get_user(uid), get_orders(uid))  # concurrent, ~0.2s not 0.4s
    return {"user": user, "orders": orders}  # combined response


t0: float = time.perf_counter()  # start
print(TestClient(app).get("/profile/1").json())  # call it
# Output: {'user': {'id': 1, 'name': 'Asha'}, 'orders': [101, 102]}
print("faster than sequential 0.4s:", time.perf_counter() - t0 < 0.38)  # concurrent
# Output: faster than sequential 0.4s: True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking calls inside `async def`
```python
# Wrong - freezes every request on this worker:
async def handler():
    time.sleep(2)
    requests.get(url)

# Correct - async versions, or move blocking code to a thread:
async def handler():
    await asyncio.sleep(2)
    await asyncio.to_thread(requests.get, url)
```

❌ Mistake 2: Forgetting `await` (the coroutine never runs)
```python
# Wrong - creates a coroutine object and throws it away (RuntimeWarning: never awaited):
async def main():
    fetch(1)

# Correct:
async def main():
    await fetch(1)
```

❌ Mistake 3: Awaiting in a loop when tasks are independent
```python
# Wrong - sequential, total = sum of waits:
for u in urls:
    results.append(await fetch(u))

# Correct - concurrent (and bound it with a Semaphore for thousands of URLs):
results = await asyncio.gather(*(fetch(u) for u in urls))
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print (rounded to 1 decimal)?

```python
import asyncio, time

async def bad():
    time.sleep(0.2)

async def good():
    await asyncio.sleep(0.2)

async def main():
    t = time.perf_counter()
    await asyncio.gather(bad(), bad(), bad())
    print(round(time.perf_counter() - t, 1))
    t = time.perf_counter()
    await asyncio.gather(good(), good(), good())
    print(round(time.perf_counter() - t, 1))
    coro = good()
    print(type(coro).__name__)
    await coro

asyncio.run(main())
```

**Answer**:
```
0.6
0.2
coroutine
```
`time.sleep` blocks the whole loop, so the three "concurrent" `bad()` calls run one after another (0.6 s). `asyncio.sleep` yields control, so the three `good()` calls overlap (0.2 s). Calling an `async def` function returns a coroutine object; nothing runs until it is awaited.

---

## ⚫ Interview Questions + Answers

Q1: asyncio vs threading vs multiprocessing?
A1: asyncio: many I/O waits, one thread, cooperative switching at `await`. Threading: I/O with blocking libraries, preemptive but limited by the GIL for CPU. Multiprocessing: CPU-bound work on several cores.

Q2: What is the event loop?
A2: A scheduler that keeps a set of ready tasks and I/O waiters. It runs one task until it awaits, then picks the next ready task, using the OS selector (epoll/kqueue) to know which sockets are ready.

Q3: `gather` vs `create_task` vs `TaskGroup`?
A3: `gather` runs awaitables together and returns results in order. `create_task` schedules one coroutine to run in the background. `TaskGroup` (3.11+) is structured concurrency: if one task fails, the others are cancelled and the errors are raised together as an `ExceptionGroup`.

Q4: How do you limit concurrency?
A4: `asyncio.Semaphore(N)` around the work, or a queue with N worker tasks. This protects remote APIs and your own connection pool.

Q5: How do you run blocking or CPU code from async code?
A5: `await asyncio.to_thread(func, ...)` for blocking I/O libraries, and `loop.run_in_executor(ProcessPoolExecutor, ...)` for CPU-heavy work.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Many concurrent network, DB or file waits (APIs, scrapers, chat servers)
- You build FastAPI/aiohttp services with high connection counts
- You need timeouts and cancellation

❌ Avoid when:
- The work is CPU-bound (use multiprocessing, NumPy, Numba)
- Your key libraries are blocking only and you cannot wrap them
- A simple sequential script is fast enough

---

## 📊 Visual Diagram

```
Sequential:  |--menu 0.3--||--offers 0.3--||--reviews 0.3--|   = 0.9s

asyncio:     |--menu 0.3--|
             |--offers 0.3--|           all waits overlap       = 0.3s
             |--reviews 0.3--|

one thread:  run A until await → run B until await → run C → resume A when ready
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coroutine | Function defined with async def, can pause | रुक सकने वाला function |
| Event loop | Scheduler running tasks | tasks चलाने वाला scheduler |
| await | Pause here until the result is ready | नतीजे तक यहीं रुकना |
| Task | Coroutine scheduled to run in the loop | loop में schedule हुआ coroutine |
| gather | Run many awaitables together | कई awaitables साथ चलाना |
| Semaphore | Limit of concurrent operations | एक साथ चलने वाले operations की सीमा |

---

## ⚡ 3-Line Summary
English: asyncio overlaps many I/O waits on one thread, so total time is the longest wait rather than the sum. Never block the event loop; use `gather`, `Semaphore`, timeouts and `to_thread`. It does not speed up CPU-bound code.
Hindi: asyncio एक thread पर कई I/O waits को overlap करता है, इसलिए कुल समय सबसे लंबा wait होता है, जोड़ नहीं। Event loop को कभी block न करें; `gather`, `Semaphore`, timeouts और `to_thread` इस्तेमाल करें। यह CPU वाले code को तेज़ नहीं करता।

---

## ➡️ Next Topic
**415. Redis Caching in Python** — avoid repeating slow work by caching results in memory.
