---

# 257. anyio Library
# हिंदी में: anyio Library (asyncio और trio दोनों के लिए एक API)

---

## 🔵 Simple Definition (English)
`anyio` is a library that gives you one async API (task groups, timeouts, streams, threads, files) that runs on top of either `asyncio` or `trio`. You write your code once and choose the backend at the start. It adds structured concurrency (clean task lifetimes) to asyncio.

## 🔵 सरल परिभाषा (Hindi)
`anyio` एक library है जो एक ही async API देती है (task groups, timeouts, streams, threads, files) जो `asyncio` या `trio` दोनों के ऊपर चलती है। Code एक बार लिखें और backend शुरू में चुनें। यह asyncio में structured concurrency (task का साफ जीवन-चक्र) जोड़ती है।

---

## 🔴 Problem it Solves
Plain asyncio makes it easy to leak tasks: `create_task()` can start background work that nobody awaits, errors get lost, and cancellation is hard to get right. Libraries written for asyncio cannot run on trio and vice versa. `anyio` provides one well-designed API with structured concurrency, so library authors support both, and app authors get safer task handling. FastAPI/Starlette already uses anyio internally.

## 🔴 यह क्यों बना? (Hindi)
सादे asyncio में tasks leak होना आसान है: `create_task()` ऐसा background काम शुरू कर सकता है जिसे कोई await नहीं करता, errors खो जाते हैं और cancellation सही करना कठिन है। asyncio के लिए लिखी libraries trio पर नहीं चलतीं, और उल्टा भी। `anyio` structured concurrency के साथ एक अच्छा API देता है, ताकि library authors दोनों को support करें और app authors को सुरक्षित task handling मिले। FastAPI/Starlette अंदर से पहले ही anyio इस्तेमाल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → anyio.run(main) starts the event loop (default backend: asyncio)
Step 2 → async with create_task_group() as tg: opens a "scope" for child tasks
Step 3 → tg.start_soon(fn, arg) launches a child task inside that scope
Step 4 → The "async with" block does NOT finish until ALL children finish
Step 5 → If one child raises, siblings are cancelled and an ExceptionGroup is raised
Step 6 → Timeouts: with fail_after(5): ...  /  move_on_after(5): ... (cancel scopes)
Step 7 → Streams (memory object streams) pass messages; to_thread.run_sync runs blocking code
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → anyio.run(main) event loop शुरू करता है (default backend: asyncio)
Step 2 → async with create_task_group() as tg: child tasks के लिए "scope" खोलता है
Step 3 → tg.start_soon(fn, arg) उस scope में child task चलाता है
Step 4 → "async with" block तब तक खत्म नहीं होता जब तक सारे children खत्म न हों
Step 5 → कोई child fail हो तो बाकी cancel होते हैं और ExceptionGroup उठता है
Step 6 → Timeouts: with fail_after(5): ...  /  move_on_after(5): ... (cancel scopes)
Step 7 → Streams messages भेजते हैं; to_thread.run_sync blocking code चलाता है
```

---

## 🟡 Real World Example
A data-sync service pulls updates from 3 partner APIs at the same time. A task group runs the 3 fetches; if one partner returns an error, the other two are cancelled and the error reaches the caller cleanly, with no orphan tasks. A producer/consumer pipeline (webhook receiver -> processing workers) uses memory object streams. A library like `httpx` or `Starlette` can then run on asyncio today and trio tomorrow without code changes.

## 🟡 Real Example Hindi mein
Data-sync service 3 partner APIs से एक साथ updates खींचती है। Task group 3 fetches चलाता है; अगर कोई partner error दे तो बाकी दो cancel हो जाते हैं और error caller तक साफ पहुंचता है, कोई orphan task नहीं बचता। Producer/consumer pipeline (webhook receiver -> processing workers) memory object streams इस्तेमाल करती है। `httpx` या `Starlette` जैसी library आज asyncio पर और कल trio पर बिना code बदले चल सकती है।

---

## 💻 Code Example — Basic
```python
# Basic anyio (verified: anyio 4.16, Python 3.13; also run on the trio backend)
# pip install anyio trio
import anyio                                             # the library
from anyio import create_task_group, sleep               # task group + sleep


async def worker(name: str, delay: float, out: list[str]) -> None:
    await sleep(delay)                                   # anyio.sleep works on any backend
    out.append(name)                                     # record finish order


async def main() -> None:
    out: list[str] = []                                  # shared result list
    async with create_task_group() as tg:                # open a scope for child tasks
        tg.start_soon(worker, "slow", 0.1, out)          # start child 1 (not awaited here)
        tg.start_soon(worker, "fast", 0.01, out)         # start child 2
    print(out)                                           # reached only after BOTH finished

    try:
        with anyio.fail_after(0.05):                     # deadline of 0.05 s
            await sleep(1)                               # too slow
    except TimeoutError:                                 # fail_after raises builtin TimeoutError
        print("timeout")                                 # we cancelled it

    print(await anyio.to_thread.run_sync(lambda: sum(range(10))))   # blocking code in a thread


anyio.run(main)                                          # default backend: asyncio
anyio.run(main, backend="trio")                          # SAME code on trio (needs trio installed)

# Output (printed once per backend, so twice in total):
# ['fast', 'slow']
# timeout
# 45
```

## 💻 Code Example — Advanced
```python
# Production style: producer/consumer with streams, error propagation, cancel scope
import anyio                                             # library
from anyio import create_memory_object_stream, create_task_group, sleep   # parts
from anyio.abc import ObjectReceiveStream, ObjectSendStream               # stream types


async def producer(tx: ObjectSendStream[int], n: int) -> None:
    async with tx:                                       # closing tx tells the consumer "no more"
        for i in range(n):                               # send n messages
            await tx.send(i)                             # waits if the buffer is full (back-pressure)


async def consumer(rx: ObjectReceiveStream[int]) -> None:
    async with rx:                                       # close our end when done
        async for item in rx:                            # ends when the sender closes
            print("got", item)                           # process each message


async def main() -> None:
    tx, rx = create_memory_object_stream[int](5)         # buffer of 5 items; [int] is the item type
    async with create_task_group() as tg:                # structured: both tasks live here
        tg.start_soon(producer, tx, 3)                   # task 1
        tg.start_soon(consumer, rx)                      # task 2

    try:
        async with create_task_group() as tg:            # a group where a child fails
            async def bad() -> None:
                raise ValueError("boom")                 # error in a child

            tg.start_soon(bad)                           # start it
            tg.start_soon(sleep, 5)                      # sibling gets CANCELLED, not waited 5 s
    except* ValueError as eg:                            # 3.11+ syntax for ExceptionGroup
        print("group:", [str(e) for e in eg.exceptions]) # ['boom']

    with anyio.CancelScope() as scope:                   # manual cancel scope
        scope.cancel()                                   # cancel it right away
        await sleep(1)                                   # skipped immediately
    print("cancelled", scope.cancelled_caught)           # True


anyio.run(main)                                          # run on asyncio

# Output:
# got 0
# got 1
# got 2
# group: ['boom']
# cancelled True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | anyio | JavaScript |
|---------|-------|-----------|
| Run many tasks and wait | `create_task_group` | `Promise.all` |
| Child error cancels siblings | built in | NOT automatic (`Promise.all` rejects but others keep running) |
| Timeout | `fail_after(s)` | `AbortSignal.timeout(ms)` |
| Cancellation | `CancelScope` | `AbortController` |
| Channel between tasks | memory object streams | none built in |
| Run blocking code | `to_thread.run_sync` | `worker_threads` |

```python
# Python way (anyio)
async with create_task_group() as tg:
    tg.start_soon(task_a)
    tg.start_soon(task_b)
# here: both finished OR one failed and the other was cancelled
```
```javascript
// JavaScript way
await Promise.all([taskA(), taskB()]);
// if taskA rejects, taskB is still running in the background (no cancellation!)
```

Key difference: `Promise.all` rejects early but cannot stop the other promises. A task group guarantees no child task outlives the `async with` block, and failures cancel the siblings. This is the main selling point of structured concurrency.

---

## 🟠 FastAPI Connection
FastAPI is built on Starlette, which uses anyio. Two direct uses: run blocking code with `anyio.to_thread.run_sync` (this is what FastAPI does for plain `def` endpoints), and run parallel calls with a task group inside an endpoint. Tests also use anyio (see topic 259).

```python
# FastAPI example — parallel calls with a task group, blocking code in a thread
import anyio                                             # library
from fastapi import FastAPI                              # FastAPI

app: FastAPI = FastAPI()                                 # app


async def price(source: str, results: dict[str, float]) -> None:
    await anyio.sleep(0.05)                              # pretend to call an external API
    results[source] = {"a": 10.0, "b": 11.5}[source]     # store its answer


def slow_hash(text: str) -> int:                         # blocking CPU-ish function
    return sum(ord(c) for c in text)                     # simple stand-in


@app.get("/prices")                                      # GET /prices
async def prices() -> dict[str, float]:
    results: dict[str, float] = {}                       # collector
    async with anyio.create_task_group() as tg:          # run both lookups together
        tg.start_soon(price, "a", results)               # source a
        tg.start_soon(price, "b", results)               # source b
    return results                                       # both ready here


@app.get("/hash/{text}")                                 # GET /hash/abc
async def hash_it(text: str) -> dict[str, int]:
    return {"h": await anyio.to_thread.run_sync(slow_hash, text)}   # off the event loop
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing `asyncio.sleep` with the trio backend
✅ Correct: use `anyio.sleep` (and anyio primitives) so code works on every backend

```python
# Wrong — fails when run with backend="trio"
import asyncio
await asyncio.sleep(1)
# Right
import anyio
await anyio.sleep(1)
```

❌ Mistake 2: Catching a plain `ValueError` around a task group
✅ Correct: task groups raise an `ExceptionGroup`; use `except*` (3.11+)

```python
# Wrong — the exception is wrapped, so this does NOT catch it
try:
    async with create_task_group() as tg: tg.start_soon(bad)
except ValueError: ...
# Right
try:
    async with create_task_group() as tg: tg.start_soon(bad)
except* ValueError as eg: ...
```

❌ Mistake 3: Expecting `start_soon` to return a result
✅ Correct: pass a container (list/dict), or use a stream, to get values out

```python
# Wrong
r = tg.start_soon(fetch)          # returns None
# Right
results: dict = {}
tg.start_soon(fetch_into, results)
```

---

## 🧠 Tricky Interview Question

```python
# How long does this take, and what is raised?
import anyio

async def bad() -> None:
    raise ValueError("boom")

async def main() -> None:
    async with anyio.create_task_group() as tg:
        tg.start_soon(bad)
        tg.start_soon(anyio.sleep, 5)

anyio.run(main)
```
Answer: It finishes almost instantly (not after 5 seconds) and raises `ExceptionGroup` containing the `ValueError("boom")`. When one child fails, the task group cancels its scope, which cancels the sleeping sibling, and then re-raises the error as an `ExceptionGroup` (anyio 4.x). That is structured concurrency: no child is left running, and no error is lost. With plain `asyncio.gather` the sleep would keep running in the background.

---

## ⚫ Interview Questions + Answers

Q1: What is structured concurrency?
A1: A rule that child tasks cannot outlive the block that created them. The parent waits for all children, errors propagate upward, and cancellation flows downward. It removes orphan tasks and lost exceptions.

Q2: `anyio` vs `asyncio.TaskGroup`?
A2: `asyncio.TaskGroup` (3.11+) is the stdlib version for asyncio only. anyio offers the same idea on both asyncio and trio, plus extras (streams, cancel scopes, `to_thread`, async file API, `fail_after`).

Q3: What is a CancelScope?
A3: A region of code that can be cancelled as a unit (by a deadline or by calling `cancel()`). `fail_after` and `move_on_after` are scopes with a deadline: `fail_after` raises `TimeoutError`, `move_on_after` just exits silently.

Q4: What are memory object streams?
A4: In-process channels: `send_stream, receive_stream = create_memory_object_stream[T](max_buffer_size)`. They provide back-pressure when the buffer is full and end when the sender is closed.

Q5: Why do FastAPI users care about anyio?
A5: Starlette/FastAPI run sync endpoints using `anyio.to_thread.run_sync`, whose thread limit (default 40) caps concurrent sync endpoints, and the `@pytest.mark.anyio` plugin is commonly used for async tests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing a library that must work on asyncio and trio
- You want structured concurrency on asyncio today (also available via `asyncio.TaskGroup` in 3.11+)
- You need streams, cancel scopes or `to_thread` helpers

❌ Avoid when:
- A tiny asyncio script where `asyncio.gather` is enough
- You depend on asyncio-only features/libraries (Futures, loop APIs) that anyio hides
- You want the absolute minimum dependencies

---

## 📊 Visual Diagram
```
            your code  (anyio API)
        ┌──────────┴───────────┐
   backend="asyncio"      backend="trio"

async with create_task_group() as tg:
     ├─ child 1 ───────────────┐
     ├─ child 2 ───────────────┤   block ends only when all done
     └─ child 3 (raises!) ─────┘
                │
   siblings cancelled -> ExceptionGroup([ValueError]) raised at the "async with"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structured concurrency | Children cannot outlive parent block | Children parent block से ज्यादा नहीं जीते |
| Task group | Container for child tasks | Child tasks का container |
| Cancel scope | Region that can be cancelled | रद्द किया जा सकने वाला हिस्सा |
| ExceptionGroup | Several exceptions in one | कई exceptions एक में |
| Memory object stream | In-process message channel | Process के अंदर message channel |
| Back-pressure | Slow consumer slows the producer | धीमा consumer producer को धीमा करता है |

---

## ⚡ 3-Line Summary
English: `anyio` is one async API for asyncio and trio, built on structured concurrency: task groups, cancel scopes, streams and thread helpers. Child errors cancel siblings and arrive as an `ExceptionGroup`.
Hindi: `anyio` asyncio और trio के लिए एक async API है, जो structured concurrency पर बना है: task groups, cancel scopes, streams और thread helpers। Child के error से siblings cancel होते हैं और error `ExceptionGroup` में आता है।

---

## ➡️ Next Topic
**258. trio Library Basics** — the library that invented nurseries and structured concurrency.
