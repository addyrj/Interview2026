---

# 245. asyncio Queue
# हिंदी में: asyncio Queue — Tasks के बीच काम सौंपने की सुरक्षित line

---

## 🔵 Simple Definition (English)
`asyncio.Queue` is a first-in-first-out queue made for coroutines. Producers `await q.put(item)`, consumers `await q.get()`. If the queue is empty, `get` waits; if it is full (`maxsize`), `put` waits. It works inside one event loop and is NOT thread-safe or process-safe.

## 🔵 सरल परिभाषा (Hindi)
`asyncio.Queue` coroutines के लिए बनी first-in-first-out queue है। Producers `await q.put(item)` करते हैं, consumers `await q.get()`। Queue खाली हो तो `get` इंतज़ार करता है; भरी हो (`maxsize`) तो `put` इंतज़ार करता है। यह एक ही event loop के अंदर चलती है और thread-safe या process-safe नहीं है।

---

## 🔴 Problem it Solves
Without a queue, one task that produces work (web requests, messages) must call the processing code directly, so a slow consumer slows the producer, and a burst of work spawns unlimited tasks and eats memory. A queue decouples both sides, lets you run a fixed number of workers, and gives back-pressure: when the queue is full, producers slow down automatically.

## 🔴 यह क्यों बना? (Hindi)
Queue के बिना काम पैदा करने वाले task (web requests, messages) को processing code सीधे बुलाना पड़ता है, इसलिए धीमा consumer producer को धीमा कर देता है, और अचानक आए काम की बाढ़ असीमित tasks बनाकर memory खा जाती है। Queue दोनों तरफ को अलग करती है, fixed संख्या में workers चलाने देती है, और back-pressure देती है: queue भरी हो तो producers अपने आप धीमे हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → q = asyncio.Queue(maxsize=N)   (0 = unlimited)
Step 2 → Producer: await q.put(item)    waits if q is full
Step 3 → Consumer: item = await q.get() waits if q is empty
Step 4 → After handling an item the consumer calls q.task_done()
Step 5 → Somewhere else: await q.join() blocks until every put item
         has had a matching task_done()
Step 6 → Stop workers: cancel them, or put one sentinel per worker,
         or (3.13+) q.shutdown() so get() raises QueueShutDown
Step 7 → Variants: LifoQueue (stack), PriorityQueue (smallest first)

producers --put--> [ item item item ] --get--> workers --task_done--> join()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → q = asyncio.Queue(maxsize=N)   (0 = असीमित)
Step 2 → Producer: await q.put(item)    queue भरी हो तो रुकता है
Step 3 → Consumer: item = await q.get() queue खाली हो तो रुकता है
Step 4 → Item संभालने के बाद consumer q.task_done() बुलाता है
Step 5 → कहीं और: await q.join() तब तक रुकता है जब तक हर put हुए item का
         task_done() न आ जाए
Step 6 → Workers रोकने के लिए: उन्हें cancel करें, हर worker के लिए एक sentinel डालें,
         या (3.13+) q.shutdown() ताकि get() QueueShutDown raise करे
Step 7 → Variants: LifoQueue (stack), PriorityQueue (सबसे छोटा पहले)
```

---

## 🟡 Real World Example
A web crawler: seed URLs go into a queue, 20 worker tasks pull a URL, fetch it, and put newly found links back. A Swiggy-style notification service receives order events and pushes them through a queue to 5 sender workers (SMS, push). An LLM app puts user prompts on a queue and a fixed number of workers call the model, so the API key rate limit is never exceeded. A `PriorityQueue` handles premium customers first.

## 🟡 Real Example Hindi mein
Web crawler में seed URLs queue में जाते हैं, 20 worker tasks एक URL लेकर उसे fetch करते हैं और मिले नए links को वापस queue में डालते हैं। Swiggy जैसी notification service order events लेती है और queue से 5 sender workers (SMS, push) तक पहुँचाती है। LLM app user prompts को queue में रखता है और fixed संख्या के workers model बुलाते हैं, जिससे API key का rate limit कभी पार नहीं होता। `PriorityQueue` premium customers को पहले संभालती है।

---

## 💻 Code Example — Basic
```python
# Basic: asyncio.Queue producer/consumer
import asyncio                                              # asyncio


async def producer(q: asyncio.Queue[int]) -> None:          # puts items
    for i in range(3):                                      # three items
        await q.put(i)                                      # waits if queue is full
        print("produced", i)                                # log
    await q.put(-1)                                         # sentinel


async def consumer(q: asyncio.Queue[int]) -> None:          # takes items
    while (item := await q.get()) != -1:                    # waits if queue is empty
        print("consumed", item)                             # use it


async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue(maxsize=1)        # small buffer -> backpressure
    await asyncio.gather(producer(q), consumer(q))          # run both
    print(q.empty(), q.qsize())                             # True 0


asyncio.run(main())

# Output (verified on Python 3.13; with maxsize=1 the two sides alternate like this):
# produced 0
# consumed 0
# produced 1
# consumed 1
# produced 2
# consumed 2
# True 0
```

## 💻 Code Example — Advanced
```python
# Production style: worker with join(), task_done(), PriorityQueue and graceful shutdown
import asyncio                                              # asyncio


async def worker(name: str, q: asyncio.Queue[tuple[int, str]], out: list[str]) -> None:
    while True:                                             # run until cancelled
        prio, job = await q.get()                           # take next (lowest prio number first)
        try:                                                # ensure task_done is always called
            await asyncio.sleep(0.01)                       # pretend work
            if job == "bad":                                # a failing job
                raise ValueError("bad job")                 # error
            out.append(f"{job}")                            # record success
        except ValueError as exc:                           # do not kill the worker
            out.append(f"ERR({exc})")                       # record failure
        finally:
            q.task_done()                                   # tell join() this item is finished


async def main() -> None:
    q: asyncio.PriorityQueue[tuple[int, str]] = asyncio.PriorityQueue()   # smallest tuple first
    out: list[str] = []                                     # results
    for prio, job in [(2, "email"), (1, "payment"), (3, "bad"), (1, "fraud")]:
        q.put_nowait((prio, job))                           # preload (sync version, unbounded queue)
    workers = [asyncio.create_task(worker(f"w{i}", q, out)) for i in range(1)]   # one worker -> ordered
    await q.join()                                          # blocks until every item had task_done()
    for w in workers:                                       # workers loop forever, so cancel them
        w.cancel()                                          # stop
    await asyncio.gather(*workers, return_exceptions=True)  # wait for cancel
    print(out)                                              # priority order

    q2: asyncio.Queue[int] = asyncio.Queue(maxsize=1)       # bounded queue
    q2.put_nowait(1)                                        # fits
    try:                                                    # non-waiting put on a full queue
        q2.put_nowait(2)                                    # no room
    except asyncio.QueueFull:                               # specific error
        print("QueueFull")                                  # caught
    q2.get_nowait()                                         # take it
    try:                                                    # non-waiting get on empty queue
        q2.get_nowait()                                     # nothing there
    except asyncio.QueueEmpty:                              # specific error
        print("QueueEmpty")                                 # caught
    q2.shutdown()                                           # 3.13+: no more puts, get raises QueueShutDown
    try:                                                    # use after shutdown
        await q2.get()                                      # raises immediately (empty and shut down)
    except asyncio.QueueShutDown:                           # new in 3.13
        print("QueueShutDown")                              # caught


if __name__ == "__main__":
    asyncio.run(main())

# Output (verified on 3.13; shutdown() / QueueShutDown need 3.13+):
# ['fraud', 'payment', 'email', 'ERR(bad job)']
# QueueFull
# QueueEmpty
# QueueShutDown
```
Note the first line: `(1, "fraud")` is smaller than `(1, "payment")`, since equal priorities fall back to comparing the strings. For FIFO order inside a priority, add a counter as the second tuple item.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Built-in async queue | `asyncio.Queue` | none (use arrays + promises, or a library) |
| Wait for item | `await q.get()` | custom promise / `async iterator` |
| Back-pressure | `maxsize` makes `put` wait | streams `highWaterMark` |
| Wait until all done | `await q.join()` | custom counter |
| Priority | `asyncio.PriorityQueue` | none built-in |
| Threads | not thread-safe | n/a (single thread) |

```python
# Python way — three lines of real queue logic
import asyncio                                           # stdlib

async def main() -> None:
    q: asyncio.Queue[str] = asyncio.Queue()              # create
    await q.put("job-1")                                 # produce
    print(await q.get())                                 # job-1

asyncio.run(main())
```
```javascript
// JavaScript way — no built-in async queue; a simple version by hand
class AsyncQueue {
  items = []; waiters = [];
  put(x) { const w = this.waiters.shift(); w ? w(x) : this.items.push(x); }
  get() { return this.items.length ? Promise.resolve(this.items.shift())
                                   : new Promise(r => this.waiters.push(r)); }
}
const q = new AsyncQueue(); q.put('job-1'); q.get().then(console.log);   // job-1
```

Key difference: JS has no standard async queue, so developers use libraries (BullMQ, p-queue) or write one. Python ships a complete one with size limits, `join()` and priority variants.

---

## 🟠 FastAPI Connection
A common pattern: the endpoint puts work on an `asyncio.Queue` and returns `202 Accepted`; worker tasks started in the lifespan process the jobs. With `maxsize`, a full queue can be turned into HTTP 503 using `put_nowait` and `QueueFull`. The lifespan consumer version was run with `TestClient` on 3.13.

```python
# FastAPI example — queue + worker task from lifespan
import asyncio                                            # queue and tasks
from contextlib import asynccontextmanager                # lifespan helper
from fastapi import FastAPI, HTTPException, Request       # FastAPI


async def consume(app: FastAPI) -> None:                  # background worker
    while True:                                           # until cancelled
        item = await app.state.queue.get()                # wait for work
        try:                                              # do not die on one bad job
            app.state.done.append(item)                   # "process" the item
        finally:
            app.state.queue.task_done()                   # always mark done


@asynccontextmanager                                      # startup/shutdown
async def lifespan(app: FastAPI):
    app.state.queue = asyncio.Queue(maxsize=100)          # bounded: back-pressure
    app.state.done = []                                   # processed items
    app.state.worker = asyncio.create_task(consume(app))  # start worker
    yield                                                 # serve requests
    app.state.worker.cancel()                             # stop worker at shutdown


app: FastAPI = FastAPI(lifespan=lifespan)                 # attach lifespan


@app.post("/enqueue/{x}", status_code=202)                # POST /enqueue/a
async def enqueue(x: str, request: Request) -> dict[str, int]:
    try:                                                  # never wait inside a request
        request.app.state.queue.put_nowait(x)             # try to add
    except asyncio.QueueFull:                             # queue is full
        raise HTTPException(status_code=503, detail="busy, retry later")   # tell the client
    return {"waiting": request.app.state.queue.qsize()}   # how many are waiting
```
Remember: an in-memory queue is lost on restart and is per worker process. For durable or multi-process work use Redis, RabbitMQ or Celery.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `task_done()`, so `join()` hangs forever
✅ Correct: call `task_done()` in a `finally` for every `get()`

```python
# Wrong — join() waits forever (the demo below uses a timeout to show it)
# item = await q.get(); process(item)       # no task_done
# Right
# item = await q.get()
# try: process(item)
# finally: q.task_done()
```

❌ Mistake 2: Using an unbounded queue with a fast producer
✅ Correct: set `maxsize` so `put` waits (back-pressure), or reject with `put_nowait` + `QueueFull`

```python
# Wrong — memory grows without limit
# q = asyncio.Queue()
# Right
# q = asyncio.Queue(maxsize=1000)
```

❌ Mistake 3: Using `asyncio.Queue` from threads or other processes
✅ Correct: `asyncio.Queue` is for one event loop. From a thread use `loop.call_soon_threadsafe(q.put_nowait, x)`; across processes use `multiprocessing.Queue` or Redis

```python
# Wrong — called from another thread, may corrupt the loop's state
# q.put_nowait(x)
# Right
# loop.call_soon_threadsafe(q.put_nowait, x)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import asyncio
async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue()
    q.put_nowait(1)
    await q.get()
    try:
        await asyncio.wait_for(q.join(), timeout=0.1)
    except TimeoutError:
        print("join hangs: task_done() was never called")
    q.task_done()
    await asyncio.wait_for(q.join(), timeout=0.1)
    print("join finished")
    try:
        q.task_done()
    except ValueError as e:
        print("ValueError:", e)
asyncio.run(main())
```
Answer: `join hangs: task_done() was never called`, `join finished`, `ValueError: task_done() called too many times` (verified on 3.13). The queue keeps a counter of unfinished items: `put` adds one and only `task_done()` removes one; `get()` does NOT. `join()` waits for the counter to reach 0, so after `get()` alone it hangs, and the timeout fires. After one `task_done()` it finishes. A second `task_done()` goes below zero, which raises `ValueError`.

---

## ⚫ Interview Questions + Answers

Q1: Why use a queue rather than calling the worker function directly?
A1: A queue decouples producers from consumers, lets you control how many workers run, smooths bursts, and provides back-pressure through `maxsize`. Direct calls or one task per request give no limit and the producer pays the cost of slow consumers.

Q2: What is the difference between `get()` and `get_nowait()`?
A2: `await q.get()` waits until an item exists. `get_nowait()` returns at once or raises `QueueEmpty`. Same for `put()` (waits when full) and `put_nowait()` (raises `QueueFull`). Use the `_nowait` versions in request handlers that must not block.

Q3: How do you stop consumers cleanly?
A3: Options: (1) `await q.join()` then cancel the worker tasks; (2) put one sentinel (`None`) per worker; (3) on Python 3.13+, `q.shutdown()` makes further `put` raise `QueueShutDown` and `get` raise it once the queue is empty (`shutdown(immediate=True)` drops queued items too). Always handle `CancelledError` and `finally: task_done()`.

Q4: `asyncio.Queue` vs `queue.Queue` vs `multiprocessing.Queue`?
A4: `asyncio.Queue`: coroutines in one loop, awaitable methods, not thread-safe. `queue.Queue`: threads, blocking methods, thread-safe. `multiprocessing.Queue`: processes, pickles items. Mixing them up (for example `await queue.Queue().get()`) is a classic bug.

Q5: Which priority does `PriorityQueue` use for ties?
A5: Items are compared directly; tuples compare element by element, so equal priorities compare the next element and may even raise `TypeError` if it is not comparable. Insert `(priority, counter, item)` with an `itertools.count()` for stable FIFO order within a priority.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Producer-consumer pipelines inside one async app
- A fixed pool of workers must process many jobs
- You need back-pressure or priorities
- Rate-limited calls (LLM APIs, scrapers)

❌ Avoid when:
- Producers or consumers are in other threads or processes
- Jobs must survive restarts or run on several machines (use Redis/RabbitMQ/Celery)
- You just need to run N things at once; `gather` or a `Semaphore` is simpler
- Strict ordering across several workers is required (workers finish in any order)

---

## 📊 Visual Diagram
```
 producers                 asyncio.Queue(maxsize=3)              workers
 +--------+  put   +--------------------------------+  get    +----------+
 | task A |------> | item1 | item2 | item3 |  full  | ------> | worker 1 |
 | task B |------> +--------------------------------+ ------> | worker 2 |
 +--------+   ^ put() waits when full (back-pressure)          +----------+
                                              |  task_done() per item
                                              v
                         await q.join()  ==  "all put items are finished"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Producer / consumer | Side that adds / removes items | Items जोड़ने / निकालने वाला पक्ष |
| Back-pressure | Full queue slows the producer | भरी queue से producer का धीमा होना |
| `task_done` | Mark one taken item as finished | लिए गए item को पूरा चिह्नित करना |
| `join` | Wait until all items are finished | सभी items पूरे होने तक रुकना |
| Sentinel | Special item that says "stop" | रुकने का संकेत देने वाला विशेष item |
| `PriorityQueue` | Queue that returns smallest item first | सबसे छोटा item पहले देने वाली queue |

---

## ⚡ 3-Line Summary
English: `asyncio.Queue` lets tasks pass work safely: `put` waits when full, `get` waits when empty, and `join()` waits until every item has had `task_done()`. Use `maxsize` for back-pressure and call `task_done()` in `finally`. It is single-loop only; for threads, processes or durability use other queues.
Hindi: `asyncio.Queue` tasks को सुरक्षित रूप से काम सौंपने देती है: भरी हो तो `put` रुकता है, खाली हो तो `get` रुकता है, और `join()` तब तक रुकता है जब तक हर item का `task_done()` न आ जाए। Back-pressure के लिए `maxsize` रखें और `task_done()` `finally` में बुलाएं। यह सिर्फ एक loop के लिए है; threads, processes या durability के लिए दूसरी queues लें।

---

## ➡️ Next Topic
**246. Semaphore in asyncio** — limit how many tasks can use a resource at the same time, such as 10 concurrent API calls or 5 database connections.
