---

# 241. Tasks in asyncio
# हिंदी में: asyncio में Tasks — coroutine को background में चलाना

---

## 🔵 Simple Definition (English)
A Task wraps a coroutine and schedules it on the event loop right away, so it runs concurrently with the code that created it. A Task is also a Future: you can await it, check `done()`, get its `result()`, add callbacks, or `cancel()` it.

## 🔵 सरल परिभाषा (Hindi)
Task एक coroutine को लपेटकर उसे तुरंत event loop पर schedule कर देता है, ताकि वह उसे बनाने वाले code के साथ-साथ चले। Task एक Future भी है: आप उसे await कर सकते हैं, `done()` देख सकते हैं, `result()` ले सकते हैं, callbacks जोड़ सकते हैं, या `cancel()` कर सकते हैं।

---

## 🔴 Problem it Solves
`await coro()` runs the coroutine to the end before the next line, so two awaits in a row are sequential. You need a way to say "start this now, I will collect the result later". A Task does that, and also gives you a handle to cancel the work, watch its state and catch its errors.

## 🔴 यह क्यों बना? (Hindi)
`await coro()` coroutine को अगली line से पहले पूरा चलाता है, इसलिए लगातार दो awaits क्रमवार हैं। आपको कहने का तरीका चाहिए "इसे अभी शुरू करो, result बाद में लूँगा"। Task यही करता है, और साथ में काम को cancel करने, उसकी state देखने और errors पकड़ने का handle भी देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → asyncio.create_task(coro) wraps the coroutine in a Task
Step 2 → The Task is put in the loop's ready queue immediately (state: pending)
Step 3 → Your current coroutine keeps running until its next `await`
Step 4 → At that await the loop runs the Task: its first step executes
Step 5 → Whenever the Task awaits something slow it suspends; others run
Step 6 → On finish the Task stores the result (or exception) and becomes done
Step 7 → `await task` returns the result or re-raises the exception;
         task.cancel() raises CancelledError inside the task at its await point

States: pending -> (running/suspended) -> done | cancelled | exception
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → asyncio.create_task(coro) coroutine को Task में लपेटता है
Step 2 → Task तुरंत loop की ready queue में जाता है (state: pending)
Step 3 → आपकी current coroutine अपने अगले `await` तक चलती रहती है
Step 4 → उस await पर loop Task को चलाता है: उसका पहला step होता है
Step 5 → Task कुछ धीमा await करे तो रुक जाता है; दूसरे चलते हैं
Step 6 → खत्म होने पर Task result (या exception) रखता है और done हो जाता है
Step 7 → `await task` result देता है या exception दोबारा raise करता है;
         task.cancel() task के await वाले बिंदु पर CancelledError raise करता है
```

---

## 🟡 Real World Example
A Zomato order endpoint creates the order, then starts tasks for "send SMS", "notify restaurant" and "update analytics" so the customer gets a response immediately. A web crawler keeps 50 page-fetch tasks alive at once. A WebSocket server has one task per connection for reading and one for writing, and cancels both when the client disconnects.

## 🟡 Real Example Hindi mein
Zomato का order endpoint order बनाता है, फिर "SMS भेजो", "restaurant को बताओ" और "analytics update करो" के tasks शुरू करता है ताकि customer को तुरंत response मिले। Web crawler एक साथ 50 page-fetch tasks चालू रखता है। WebSocket server में हर connection के लिए पढ़ने का एक और लिखने का एक task होता है, और client disconnect होने पर दोनों cancel होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: tasks run concurrently
import asyncio                                              # asyncio
import time                                                 # timing


async def work(name: str, secs: float) -> str:              # a slow coroutine
    await asyncio.sleep(secs)                               # non-blocking wait
    return f"{name} done"                                   # result


async def main() -> None:
    start = time.perf_counter()                             # start timer
    t1 = asyncio.create_task(work("A", 0.2))                # scheduled NOW, starts at next await
    t2 = asyncio.create_task(work("B", 0.2))                # runs alongside A
    print(t1.done(), type(t1).__name__)                     # False Task
    print(await t1, "|", await t2)                          # collect results
    print(t1.done(), t1.result())                           # True 'A done'
    print("took ~0.2s, not 0.4s:", time.perf_counter() - start < 0.35)   # concurrency proof


asyncio.run(main())

# Output (verified on Python 3.13):
# False Task
# A done | B done
# True A done
# took ~0.2s, not 0.4s: True
```

## 💻 Code Example — Advanced
```python
# Production style: TaskGroup, cancellation, names, done callbacks, keeping references
import asyncio                                              # asyncio


async def job(i: int) -> int:                               # normal job
    await asyncio.sleep(0.01 * i)                           # staggered
    return i * 2                                            # result


async def slow() -> None:                                   # a job we will cancel
    try:                                                    # handle cancellation cleanly
        await asyncio.sleep(10)                             # long wait
    except asyncio.CancelledError:                          # cancellation arrives as an exception
        print("slow: cleaning up")                          # release resources here
        raise                                               # ALWAYS re-raise


async def _fail() -> None:                                  # helper that fails
    await asyncio.sleep(0.01)                               # tiny delay
    raise ValueError("child failed")                        # error


async def main() -> None:
    async with asyncio.TaskGroup() as tg:                   # 3.11+: structured concurrency
        tasks = [tg.create_task(job(i), name=f"job-{i}") for i in range(1, 4)]   # named tasks
    print([t.result() for t in tasks], [t.get_name() for t in tasks])   # all done after the block

    t = asyncio.create_task(slow(), name="slow")            # start a long task
    t.add_done_callback(lambda f: print("callback: cancelled =", f.cancelled()))   # runs on finish
    await asyncio.sleep(0.01)                               # let it start
    t.cancel()                                              # request cancellation
    try:                                                    # awaiting a cancelled task raises
        await t                                             # raises CancelledError
    except asyncio.CancelledError:                          # expected
        print("main: slow was cancelled")                   # confirm

    background: set[asyncio.Task[None]] = set()             # strong references!
    bt = asyncio.create_task(asyncio.sleep(0.01))           # fire-and-forget task
    background.add(bt)                                      # keep a reference so it is not GC'd
    bt.add_done_callback(background.discard)                # remove when finished
    await asyncio.sleep(0.05)                               # let it finish
    print("background left:", len(background))              # 0

    try:                                                    # TaskGroup error handling
        async with asyncio.TaskGroup() as tg:               # one child will fail
            tg.create_task(asyncio.sleep(1))                # gets cancelled by the failure
            tg.create_task(_fail())                         # raises
    except* ValueError as eg:                               # except* handles ExceptionGroup
        print("group error:", eg.exceptions[0])             # first sub-error


if __name__ == "__main__":
    asyncio.run(main())

# Output (verified on 3.13; TaskGroup and except* need Python 3.11+):
# [2, 4, 6] ['job-1', 'job-2', 'job-3']
# slow: cleaning up
# callback: cancelled = True
# main: slow was cancelled
# background left: 0
# group error: child failed
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Start in background | `asyncio.create_task(coro)` | just call the async function (Promise starts) |
| Wait for result | `await task` | `await promise` |
| Cancel | `task.cancel()` | no built-in; `AbortController` |
| Wait for many | `TaskGroup`, `gather` | `Promise.all` |
| Unhandled error | "Task exception was never retrieved" warning | `unhandledrejection` |
| Handle | `Task` object | `Promise` (no cancel) |

```python
# Python way — explicit task creation
import asyncio                                           # stdlib

async def work(n: int) -> int:                           # coroutine
    await asyncio.sleep(0.1)                             # wait
    return n * 2                                         # value

async def main() -> None:
    t = asyncio.create_task(work(5))                     # start now
    print(await t)                                       # 10

asyncio.run(main())
```
```javascript
// JavaScript way — calling the function already starts it
const work = async (n) => { await new Promise(r => setTimeout(r, 100)); return n * 2; };
const p = work(5);                                       // started already, no create_task needed
p.then(console.log);                                     // 10
// cancelling needs AbortController wired into the function by hand
```

Key difference: Python can cancel a Task from outside (`CancelledError` is thrown into it); JS promises cannot be cancelled, you must build cancellation signals into the function yourself.

---

## 🟠 FastAPI Connection
FastAPI has `BackgroundTasks` for simple after-response work, but for long-lived work (a periodic refresher, a queue consumer) you create a Task in the lifespan and cancel it on shutdown. Run with `TestClient` on 3.13 (a consumer task read from a queue):

```python
# FastAPI example — a background task that lives as long as the app
import asyncio                                            # tasks and queues
from contextlib import asynccontextmanager                # lifespan helper
from fastapi import FastAPI, Request                      # FastAPI


async def consume(app: FastAPI) -> None:                  # runs forever in the background
    while True:                                           # loop until cancelled
        item = await app.state.queue.get()                # wait for an item
        app.state.done.append(item)                       # "process" it
        app.state.queue.task_done()                       # mark finished


@asynccontextmanager                                      # startup + shutdown
async def lifespan(app: FastAPI):
    app.state.queue = asyncio.Queue()                     # work queue
    app.state.done = []                                   # processed items
    app.state.worker = asyncio.create_task(consume(app))  # start the task (store the reference!)
    yield                                                 # serve requests
    app.state.worker.cancel()                             # stop the worker at shutdown
    await asyncio.gather(app.state.worker, return_exceptions=True)   # wait for cancellation to finish


app: FastAPI = FastAPI(lifespan=lifespan)                 # attach lifespan


@app.post("/enqueue/{x}")                                 # POST /enqueue/a
async def enqueue(x: str, request: Request) -> dict[str, int]:
    await request.app.state.queue.put(x)                  # hand work to the task
    return {"waiting": request.app.state.queue.qsize()}   # immediate reply
```
(The worker-from-lifespan version of this code was run: after posting "a", `done == ['a']`.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not keeping a reference to a fire-and-forget task
✅ Correct: store it in a set and remove it in a done callback (the loop keeps only a weak reference, so an unreferenced task can be garbage-collected mid-run)

```python
# Wrong
# asyncio.create_task(send_email())
# Right
# bg: set[asyncio.Task[None]] = set()
# t = asyncio.create_task(send_email()); bg.add(t); t.add_done_callback(bg.discard)
```

❌ Mistake 2: Swallowing `CancelledError`
✅ Correct: clean up and re-raise it, otherwise cancellation and timeouts break

```python
# Wrong
# try: await work()
# except asyncio.CancelledError: pass       # task now refuses to be cancelled
# Right
# try: await work()
# except asyncio.CancelledError:
#     await cleanup(); raise
```

❌ Mistake 3: Never awaiting a task, so its exception is lost
✅ Correct: `await` it, use `TaskGroup`, or add a done callback that reads `task.exception()`

```python
# Wrong — if boom() raises, you only see "Task exception was never retrieved" at garbage collection
# asyncio.create_task(boom())
# Right
# async with asyncio.TaskGroup() as tg: tg.create_task(boom())
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
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
Answer: `created`, `start 2`, `start 1`, `end 2`, `awaited 2`, `end 1` (verified on 3.13). `create_task` only schedules task 1; it does not start running until `main` yields. `await job(2)` runs job 2 inline, printing `start 2`. When job 2 hits `await asyncio.sleep(0)` it yields to the loop, so task 1 gets its first step (`start 1`). Then job 2 resumes (`end 2`), `main` continues (`awaited 2`), and finally `await t` lets task 1 finish (`end 1`).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `await coro()` and `create_task(coro())`?
A1: `await coro()` runs the coroutine to completion before moving on (sequential). `create_task` schedules it to run concurrently and returns a Task right away; you await the Task later to get the result. Without `create_task` (or `gather`), you never get concurrency.

Q2: When does a created task start running?
A2: At the next point where the current coroutine yields to the event loop (any `await` that actually suspends). It does not run during `create_task` itself. (3.12 added `eager_task_factory` as an opt-in for starting immediately.)

Q3: How does cancellation work?
A3: `task.cancel()` schedules a `CancelledError` to be thrown into the task at its current `await`. The task can catch it to clean up, but must re-raise. Awaiting a cancelled task raises `CancelledError`; `task.cancelled()` tells you. Cancellation is a request, not a kill: code that never awaits cannot be cancelled.

Q4: Why use `TaskGroup` instead of `gather`?
A4: `TaskGroup` (3.11+) gives structured concurrency: if one child fails, the rest are cancelled automatically, the `async with` block waits for all children, and errors arrive together as an `ExceptionGroup` (handled with `except*`). No task can leak out of the block.

Q5: What is the difference between a Task and a Future?
A5: A Future is a low-level placeholder for a result that will be set later. A Task is a subclass that drives a coroutine and sets its own result. Application code uses Tasks; Futures appear mostly in library code and `run_in_executor`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want work to run concurrently with the current code
- You need to cancel or time out background work
- You run long-lived workers (consumers, refreshers) in a service
- You want structured, leak-free concurrency (`TaskGroup`)

❌ Avoid when:
- You just need a result right now; plain `await` is enough
- You need cheap fire-and-forget after a response; FastAPI `BackgroundTasks` is simpler
- The work is blocking or CPU-bound; tasks will not make it parallel

---

## 📊 Visual Diagram
```
 main():
   t = create_task(job(1))     ---->  [job 1 : pending in ready queue]
   print("created")
   await job(2)                         |
        |  runs inline                  |
        +--> await sleep(0) YIELD ----->+--> job 1 first step runs
        <--- resumes                    |    (suspends at its sleep)
   ...                                  v
   await t                      job 1 finishes -> result stored

 Task states:  pending -> running -> suspended -> done / cancelled / failed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Task | Scheduled, running wrapper around a coroutine | Coroutine का schedule हुआ wrapper |
| `create_task` | Start a coroutine in the background | Coroutine को background में शुरू करना |
| Cancellation | Asking a task to stop via `CancelledError` | `CancelledError` से task को रुकने को कहना |
| TaskGroup | Scope that owns and waits for child tasks | Child tasks का मालिक scope |
| Done callback | Function called when a task finishes | Task खत्म होने पर चलने वाला function |
| ExceptionGroup | Several errors raised together | एक साथ raise हुई कई errors |

---

## ⚡ 3-Line Summary
English: A Task runs a coroutine in the background on the event loop, starting at the next `await` of the creator. You can await, cancel, name and add callbacks to it, and you must keep a reference so it is not garbage-collected. Prefer `TaskGroup` (3.11+) so errors and cancellation are handled for you.
Hindi: Task एक coroutine को event loop पर background में चलाता है, बनाने वाले के अगले `await` पर शुरू होकर। आप उसे await, cancel, नाम और callbacks दे सकते हैं, और reference रखना ज़रूरी है वरना garbage-collect हो सकता है। `TaskGroup` (3.11+) चुनें ताकि errors और cancellation अपने आप संभलें।

---

## ➡️ Next Topic
**242. asyncio.gather()** — run many awaitables at once and collect all results in order, with control over how errors behave.
