# Async & Concurrency Cheatsheet — Interview Ready
# हिंदी में: Threading, Multiprocessing, asyncio Quick Reference

> Condensed from `08-async-concurrency/` (outputs verified on Python 3.13 in the notes).

## 🔷 Which Tool?

### 1. Same I/O job: sequential vs threads vs asyncio
I/O-bound waits: threads or asyncio overlap them (3 x 0.2 s takes ~0.2 s instead of 0.6 s). CPU-bound pure Python: use processes.
```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
def fetch_blocking(i: int) -> int:
    time.sleep(0.2)
    return i * 10
async def fetch_async(i: int) -> int:
    await asyncio.sleep(0.2)
    return i * 10
def threaded() -> tuple[list[int], float]:
    start: float = time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as pool:
        result: list[int] = list(pool.map(fetch_blocking, range(3)))
    return result, time.perf_counter() - start
async def with_asyncio() -> tuple[list[int], float]:
    start: float = time.perf_counter()
    result: list[int] = await asyncio.gather(*(fetch_async(i) for i in range(3)))
    return result, time.perf_counter() - start
r2, t2 = threaded()
r3, t3 = asyncio.run(with_asyncio())
print("threads   ", r2, round(t2, 1))
print("asyncio   ", r3, round(t3, 1))
```
**हिंदी:** I/O वाले काम में threads या asyncio इंतज़ार को overlap कर देते हैं; CPU वाले काम के लिए processes चाहिए। · *Source: 08-async-concurrency/252-when-to-use-each-approach.md*

## 🔷 Threading and the GIL

### 2. start() all, then join() all
`join()` right after `start()` inside one loop runs threads one by one: no concurrency at all. After all threads finish only `MainThread` is left.
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
**हिंदी:** `start` और `join` एक ही loop में लिखे तो threads एक-एक करके चलते हैं; पहले सब start करो, फिर सब join। · *Source: 08-async-concurrency/223-thread-class.md*

### 3. GIL: `counter += 1` is not atomic
It is LOAD, ADD, STORE, so threads can interleave and the total is below 2,000,000 (non-deterministic). Fix: `with lock: counter += 1`.
```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1    # is this thread-safe?

t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)
t1.start(); t2.start()
t1.join(); t2.join()

print(counter)  # What will this print?
```
**हिंदी:** GIL के बावजूद `counter += 1` तीन bytecode steps है, इसलिए race होती है; `Lock` लगाओ। · *Source: 08-async-concurrency/229-gil.md*

### 4. GIL facts you can print
Default build keeps the GIL; threads help I/O but not CPU-bound pure Python. Free-threaded build `python3.13t` (PEP 703) is experimental in 3.13 and officially supported in 3.14; many packages still need updates.
```python
import sys
import sysconfig
print(sys.version_info[:2])
# Output: (3, 13)
print(sys._is_gil_enabled())
# Output: True
print(sysconfig.get_config_var("Py_GIL_DISABLED"))
# Output: 0
print(sys.getswitchinterval())
# Output: 0.005
```
**हिंदी:** GIL एक समय में एक thread को Python code चलाने देता है; free-threaded build 3.13 में experimental है। · *Source: 08-async-concurrency/230-gil-impact-on-threading.md*

### 5. Lock, RLock, Semaphore, Event
RLock must be released as many times as acquired. `Semaphore(0)` is a signal. `Event.wait` returns the flag; `Condition.wait(timeout)` returns `False` on timeout.
```python
import threading
r = threading.RLock()
r.acquire(); r.acquire()
r.release()
t = threading.Thread(target=lambda: print("got:", r.acquire(timeout=0.1)))
t.start(); t.join()
r.release()
t = threading.Thread(target=lambda: print("got:", r.acquire(timeout=0.1)))
t.start(); t.join()

import threading
s = threading.Semaphore(0)
print(s.acquire(timeout=0.1))
s.release()
print(s.acquire(timeout=0.1))
print(s.acquire(blocking=False))

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
**हिंदी:** RLock जितनी बार acquire हुआ उतनी बार release करना पड़ता है; `Semaphore(0)` से "signal का इंतज़ार" बनता है। · *Source: 08-async-concurrency/225-lock-rlock.md, 08-async-concurrency/226-semaphore.md, 08-async-concurrency/227-event-condition.md*

### 6. ThreadPoolExecutor: map vs as_completed
`map` returns results in input order. `as_completed` yields futures in completion order.
```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def f(n):
    time.sleep(n)
    return n

with ThreadPoolExecutor(3) as ex:
    print(list(ex.map(f, [0.3, 0.1, 0.2])))
    futs = [ex.submit(f, n) for n in (0.3, 0.1, 0.2)]
    print([x.result() for x in as_completed(futs)])
```
**हिंदी:** `map` input के क्रम में result देता है, `as_completed` जो पहले खत्म हो वो पहले। · *Source: 08-async-concurrency/228-thread-pool-threadpoolexecutor.md*

## 🔷 Multiprocessing

### 7. ProcessPoolExecutor
Real parallelism for CPU work. Always guard with `if __name__ == "__main__":` (on macOS/Windows each child re-imports the file). `pool.map` returns a generator; an exception shows up when you iterate to that item.
```python
# Basic ProcessPoolExecutor examples
from concurrent.futures import ProcessPoolExecutor

def square(n: int) -> int:
    return n * n

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=2) as pool:
        future = pool.submit(square, 7)
        print(future.result())
        print(list(pool.map(square, [1, 2, 3, 4])))
        print(type(future).__name__, future.done())
```
**हिंदी:** CPU काम के लिए ProcessPool लो और `if __name__ == "__main__":` guard ज़रूर लगाओ। · *Source: 08-async-concurrency/233-process-pool-processpoolexecutor.md*

### 8. Processes do not share memory
A child changes its own copy of a global. Use `mp.Value`, a Queue or shared memory. A queue sends a pickled copy, so never mutate an object after `put()`.
```python
from multiprocessing import Process, Value
total = 0
def child(v) -> None:
    global total
    total = 5
    v.value = 5
if __name__ == "__main__":
    v = Value("i", 0)
    p = Process(target=child, args=(v,)); p.start(); p.join()
    print(total, v.value)
```
**हिंदी:** हर process की अपनी memory होती है; parent को value चाहिए तो `Value`, Queue या shared memory इस्तेमाल करो। · *Source: 08-async-concurrency/235-shared-memory.md*

### 9. Start method is version and OS dependent
Default is `spawn` on macOS and Windows, `fork` on Linux up to 3.13, `forkserver` on Linux from 3.14. Thread appends to the shared list; the process appends to its own copy.
```python
import threading, multiprocessing as mp
items: list[int] = []
def add() -> None:
    items.append(1)
if __name__ == "__main__":
    t = threading.Thread(target=add); t.start(); t.join()
    p = mp.Process(target=add); p.start(); p.join()
    print(items)
    print(mp.get_start_method())
```
**हिंदी:** default start method OS और Python version पर निर्भर है: macOS/Windows पर `spawn`, Linux पर `fork` (3.14 से `forkserver`)। · *Source: 08-async-concurrency/236-multiprocessing-vs-threading.md*

## 🔷 asyncio Core

### 10. Event loop is cooperative
Scheduling does not run code; yielding does. Nothing else runs until `main` reaches an `await`. Order: `before await`, `callback`, `task`, `after await`.
```python
import asyncio
async def main() -> None:
    loop = asyncio.get_running_loop()
    async def coro() -> None:
        print("task")
    loop.call_soon(print, "callback")
    asyncio.create_task(coro())
    print("before await")
    await asyncio.sleep(0)
    print("after await")
asyncio.run(main())
```
**हिंदी:** event loop single thread पर cooperative चलता है; schedule करने से code नहीं चलता, `await` पर yield करने से चलता है। · *Source: 08-async-concurrency/238-event-loop-in-python.md*

### 11. Coroutine is a one-shot object
Calling `f()` only creates a coroutine object. Awaiting it twice raises `RuntimeError` (a JS Promise can be awaited again).
```python
import asyncio
async def f() -> int:
    return 1
async def main() -> None:
    x = f()
    print(x == 1, type(x).__name__)
    print(await x)
    try:
        await x
    except RuntimeError as e:
        print("RuntimeError:", e)
asyncio.run(main())
```
**हिंदी:** `async def` को call करने से सिर्फ coroutine object बनता है; दूसरी बार await करने पर RuntimeError आता है। · *Source: 08-async-concurrency/240-coroutines-in-python.md*

### 12. create_task starts only when you yield
`create_task` schedules; the task starts at the next yield. Order: `created`, `start 2`, `start 1`, `end 2`, `awaited 2`, `end 1`. Keep a reference to background tasks.
```python
import asyncio
async def job(n: int) -> None:
    print("start", n)
    await asyncio.sleep(0)
    print("end", n)
async def main() -> None:
    t = asyncio.create_task(job(1))
    print("created")
    await job(2)
    print("awaited 2")
    await t
asyncio.run(main())
```
**हिंदी:** `create_task` सिर्फ schedule करता है; task तब शुरू होता है जब main कहीं `await` पर रुकता है। · *Source: 08-async-concurrency/241-tasks-in-asyncio.md*

## 🔷 gather, TaskGroup, wait

### 13. gather: argument order, return_exceptions
Results follow argument order, not finish order. `return_exceptions=True` puts errors in the list. Use `*` to unpack a dynamic list.
```python
import asyncio
async def fetch(name: str, secs: float) -> str:
    await asyncio.sleep(secs)
    return name
async def _bad() -> str:
    raise ValueError("boom")
async def main() -> None:
    results = await asyncio.gather(fetch("slow", 0.2), fetch("fast", 0.05), fetch("mid", 0.1))
    print(results)
    mixed = await asyncio.gather(
        fetch("ok", 0.01), _bad(), return_exceptions=True
    )
    print(mixed)
asyncio.run(main())
```
**हिंदी:** `gather` result argument के क्रम में देता है; `return_exceptions=True` से errors भी list में आ जाते हैं। · *Source: 08-async-concurrency/242-asyncio-gather.md*

### 14. gather does not cancel siblings
With default `return_exceptions=False` the first error is raised, but the other tasks keep running in the background. For all-or-nothing use `TaskGroup` (3.11+).
```python
import asyncio
async def main() -> None:
    # default gather: first exception propagates, siblings keep running (NOT cancelled)
    done: list[str] = []

    async def slow_ok() -> None:
        await asyncio.sleep(0.05)
        done.append("sibling finished")

    async def fail_fast() -> None:
        await asyncio.sleep(0.01)
        raise RuntimeError("early failure")

    try:
        await asyncio.gather(slow_ok(), fail_fast())
    except RuntimeError as exc:
        print("gather raised:", exc, "| done so far:", done)
    await asyncio.sleep(0.1)
    print("later:", done)
if __name__ == "__main__":
    asyncio.run(main())
```
**हिंदी:** `gather` में एक error आए तो बाकी tasks cancel नहीं होते, background में चलते रहते हैं। · *Source: 08-async-concurrency/242-asyncio-gather.md*

### 15. TaskGroup (3.11+) and except*
Structured concurrency: if one child fails, the rest are cancelled, the block waits for all children, and errors arrive as an `ExceptionGroup` handled with `except*`.
```python
import asyncio
async def job(i: int) -> int:
    await asyncio.sleep(0.01 * i)
    return i * 2
async def _fail() -> None:
    await asyncio.sleep(0.01)
    raise ValueError("child failed")
async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(job(i), name=f"job-{i}") for i in range(1, 4)]
    print([t.result() for t in tasks], [t.get_name() for t in tasks])
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(asyncio.sleep(1))
            tg.create_task(_fail())
    except* ValueError as eg:
        print("group error:", eg.exceptions[0])
if __name__ == "__main__":
    asyncio.run(main())
```
**हिंदी:** TaskGroup में एक child fail हो तो बाकी cancel हो जाते हैं और errors `except*` से पकड़ते हैं (Python 3.11+)। · *Source: 08-async-concurrency/241-tasks-in-asyncio.md*

### 16. asyncio.wait with FIRST_COMPLETED
Returns `(done, pending)` sets. Cancel what you do not need and await them with `gather(..., return_exceptions=True)`.
```python
import asyncio
async def work(name: str, secs: float) -> str:
    await asyncio.sleep(secs)
    return name
async def main() -> None:
    tasks = {asyncio.create_task(work("a", 0.05)),
             asyncio.create_task(work("b", 0.1)),
             asyncio.create_task(work("c", 0.3))}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    print(sorted(t.result() for t in done), len(pending))
    done, pending = await asyncio.wait(pending, timeout=0.15)
    print(sorted(t.result() for t in done), len(pending))
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
asyncio.run(main())
```
**हिंदी:** `wait` से `(done, pending)` मिलते हैं; जो नहीं चाहिए उन्हें cancel करके await कर लो। · *Source: 08-async-concurrency/243-asyncio-wait.md*

## 🔷 Limiting, Queues, Blocking

### 17. Semaphore limits concurrency
`async with sem` lets at most N coroutines inside; combine with `gather` to cap parallel API calls.
```python
# Basic: asyncio.Semaphore
import asyncio

async def task(i: int, sem: asyncio.Semaphore, running: list[int]) -> None:
    async with sem:
        running.append(i)
        print("inside:", len(running))
        await asyncio.sleep(0.05)
        running.remove(i)

async def main() -> None:
    sem = asyncio.Semaphore(2)
    running: list[int] = []
    await asyncio.gather(*(task(i, sem, running) for i in range(4)))
    print("locked?", sem.locked())

asyncio.run(main())
```
**हिंदी:** `Semaphore(2)` का मतलब एक समय में सिर्फ 2 coroutines अंदर; इससे API calls की संख्या सीमित रहती है। · *Source: 08-async-concurrency/246-semaphore-in-asyncio.md*

### 18. asyncio.Queue producer/consumer
`maxsize` gives backpressure (`put` waits when full). Stop workers by a sentinel, `q.join()` plus cancel, or `q.shutdown()` on 3.13+.
```python
import asyncio

async def producer(q: asyncio.Queue[int]) -> None:
    for i in range(3):
        await q.put(i)
        print("produced", i)
    await q.put(-1)

async def consumer(q: asyncio.Queue[int]) -> None:
    while (item := await q.get()) != -1:
        print("consumed", item)

async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue(maxsize=1)
    await asyncio.gather(producer(q), consumer(q))
    print(q.empty(), q.qsize())

asyncio.run(main())
```
**हिंदी:** `maxsize` से backpressure मिलता है; workers रोकने के लिए sentinel, `join()` या 3.13+ में `shutdown()` इस्तेमाल करो। · *Source: 08-async-concurrency/245-asyncio-queue.md*

### 19. Never block the loop
`time.sleep` inside `async def` freezes every user. Use `await asyncio.sleep`, or offload blocking work with `await asyncio.to_thread(...)` / `run_in_executor` (a process pool for CPU work).
```python
# Wrong - freezes the event loop for every user
async def handler():
    time.sleep(2)

# Correct
async def handler():
    await asyncio.sleep(2)
# blocking call? await asyncio.to_thread(blocking_fn)
```
**हिंदी:** `async def` में `time.sleep` पूरे loop को रोक देता है; blocking काम `to_thread` या executor में भेजो। · *Source: 08-async-concurrency/221-concurrency-vs-parallelism.md*

### 20. Async generators
`async for` and async comprehensions consume them; `aclose()` runs cleanup (`finally`).
```python
import asyncio
from collections.abc import AsyncIterator, AsyncGenerator
async def ticker(n: int) -> AsyncIterator[int]:
    for i in range(n):
        await asyncio.sleep(0.01)
        yield i
async def main() -> None:
    async for x in ticker(3):
        print(x)
    print([x async for x in ticker(4) if x % 2 == 0])
asyncio.run(main())
```
**हिंदी:** async generator को `async for` से चलाओ; बीच में रोकना हो तो `aclose()` से cleanup चलता है। · *Source: 08-async-concurrency/255-async-generators.md*

---

## 🔷 Decision Table

| Workload | Use | Why |
|----------|-----|-----|
| Many network waits | `asyncio` (or threads) | waiting overlaps, GIL released during I/O |
| Blocking libraries | threads / `to_thread` | keeps the event loop free |
| CPU-bound Python | processes | each has its own interpreter and GIL |

## 🔷 Key Rules

1. **Threads** → I/O only; CPU-bound pure Python gets no speed-up under the GIL
2. **Shared counter** → protect with `Lock`; `+= 1` is not atomic
3. **Processes** → guard with `if __name__ == "__main__":`; memory is not shared
4. **`gather`** → order = arguments; siblings are not cancelled on error
5. **`TaskGroup`** → 3.11+, cancels siblings; use `except*`
6. **Tasks** → keep a reference to every background task
7. **`asyncio.Queue.shutdown()`** → 3.13+ only
