---

# 244. asyncio.create_task()
# हिंदी में: asyncio.create_task() — Background में काम शुरू करने वाला function

---

## 🔵 Simple Definition (English)
`asyncio.create_task(coro, name=None)` takes a coroutine, wraps it in a Task and schedules it on the running event loop right now. It returns the Task immediately, so your code keeps going while the coroutine runs in the background. It must be called while a loop is running (inside an `async def`).

## 🔵 सरल परिभाषा (Hindi)
`asyncio.create_task(coro, name=None)` एक coroutine लेकर उसे Task में लपेटता है और चल रहे event loop पर अभी schedule कर देता है। यह Task तुरंत लौटा देता है, इसलिए आपका code आगे बढ़ता रहता है और coroutine background में चलती है। इसे तभी बुलाया जा सकता है जब loop चल रहा हो (`async def` के अंदर)।

---

## 🔴 Problem it Solves
Awaiting a coroutine blocks the current function until it ends. You often need "start this and carry on": send an email after the response, keep a cache refresher running, or start 10 downloads and then wait for all. `create_task` is the entry point to concurrency in asyncio. Before it existed (3.6 and earlier) people used `ensure_future` and `loop.create_task`.

## 🔴 यह क्यों बना? (Hindi)
Coroutine को await करने से मौजूदा function उसके खत्म होने तक रुका रहता है। अक्सर चाहिए "इसे शुरू करो और आगे बढ़ो": response के बाद email भेजना, cache refresher चालू रखना, या 10 downloads शुरू करके बाद में सबका इंतज़ार करना। `create_task` asyncio में concurrency का प्रवेश द्वार है। यह न था (3.6 और पहले) तब लोग `ensure_future` और `loop.create_task` इस्तेमाल करते थे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → create_task(coro) finds the running loop (error if none is running)
Step 2 → It builds a Task around coro and copies the current contextvars context
Step 3 → The Task's first step is placed in the loop's ready queue
Step 4 → create_task returns the Task right away; nothing of coro has run yet
Step 5 → Your function continues until its next real suspension (`await`)
Step 6 → The loop then runs the Task; it runs concurrently with you
Step 7 → The loop holds only a WEAK reference to the Task: keep your own
         strong reference, else it may be garbage-collected before it finishes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → create_task(coro) चल रहे loop को ढूँढता है (loop न हो तो error)
Step 2 → coro के चारों ओर Task बनाता है और मौजूदा contextvars context की copy लेता है
Step 3 → Task का पहला step loop की ready queue में जाता है
Step 4 → create_task Task तुरंत लौटा देता है; coro का कुछ भी अभी नहीं चला
Step 5 → आपका function अपने अगले असली `await` तक चलता रहता है
Step 6 → फिर loop Task को चलाता है; वह आपके साथ concurrently चलता है
Step 7 → Loop Task का सिर्फ WEAK reference रखता है: अपना strong reference रखें,
         वरना Task खत्म होने से पहले garbage-collect हो सकता है
```

---

## 🟡 Real World Example
A Razorpay-style payment endpoint verifies the payment and returns 200, while a task sends the receipt email and a second task writes the audit log. A Telegram bot starts one task per incoming chat. A trading dashboard starts a task per symbol to stream prices over WebSocket. An AI app starts a task that streams LLM tokens into a queue while the main code sends them to the browser.

## 🟡 Real Example Hindi mein
Razorpay जैसा payment endpoint payment verify करके 200 लौटाता है, जबकि एक task receipt email भेजता है और दूसरा audit log लिखता है। Telegram bot हर आने वाली chat के लिए एक task शुरू करता है। Trading dashboard हर symbol के लिए एक task से WebSocket पर prices stream करता है। AI app एक task से LLM tokens को queue में डालता है जबकि main code उन्हें browser तक भेजता है।

---

## 💻 Code Example — Basic
```python
# Basic: asyncio.create_task
import asyncio                                              # asyncio


async def say(msg: str, secs: float) -> str:                # small coroutine
    await asyncio.sleep(secs)                               # wait
    print(msg)                                              # side effect
    return msg                                              # value


async def main() -> None:
    task = asyncio.create_task(say("background", 0.05))     # starts soon, does not block us
    print("main continues")                                  # runs BEFORE the task prints
    await say("foreground", 0.01)                           # main does its own work
    print(await task)                                       # join the task, get its result
    t2 = asyncio.create_task(say("named", 0), name="my-task")   # give it a name for debugging
    print(t2.get_name())                                    # my-task
    await t2                                                # finish it


asyncio.run(main())

# Output (verified on Python 3.13):
# main continues
# foreground
# background
# background
# my-task
# named
```
The second `background` line comes from `print(await task)`, which prints the returned value.

## 💻 Code Example — Advanced
```python
# Production style: background task manager (keeps references, logs errors, graceful shutdown)
import asyncio                                              # asyncio
from collections.abc import Coroutine                       # type
from typing import Any                                      # type


class BackgroundTasks:
    """Fire-and-forget safely: strong refs, error logging, clean shutdown."""

    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[Any]] = set()         # strong references prevent GC

    def spawn(self, coro: Coroutine[Any, Any, Any], name: str) -> asyncio.Task[Any]:
        task = asyncio.create_task(coro, name=name)         # schedule it
        self._tasks.add(task)                               # keep it alive
        task.add_done_callback(self._finished)              # run when done
        return task                                         # caller may await it if wanted

    def _finished(self, task: asyncio.Task[Any]) -> None:
        self._tasks.discard(task)                           # drop reference
        if task.cancelled():                                # cancelled is not an error
            print(f"[{task.get_name()}] cancelled")         # log
        elif (exc := task.exception()) is not None:         # retrieving avoids 'never retrieved' warning
            print(f"[{task.get_name()}] failed: {exc!r}")   # log error
        else:
            print(f"[{task.get_name()}] ok -> {task.result()}")   # log success

    async def shutdown(self, timeout: float = 1.0) -> None:
        pending = list(self._tasks)                         # snapshot
        for t in pending:                                   # ask everyone to stop
            t.cancel()                                      # cancel
        if pending:                                         # wait only if there is something
            await asyncio.wait(pending, timeout=timeout)    # bounded wait for them to finish


async def send_email(to: str) -> str:                       # pretend job
    await asyncio.sleep(0.01)                               # latency
    return f"sent to {to}"                                  # ok


async def broken() -> None:                                 # failing job
    await asyncio.sleep(0.01)                               # latency
    raise RuntimeError("smtp down")                         # error


async def forever() -> None:                                # never finishes by itself
    await asyncio.sleep(100)                                # long sleep


async def main() -> None:
    bg = BackgroundTasks()                                  # manager
    bg.spawn(send_email("a@x.com"), "email")                # fire and forget
    bg.spawn(broken(), "broken")                            # will log a failure
    bg.spawn(forever(), "forever")                          # will be cancelled at shutdown
    await asyncio.sleep(0.05)                               # app "does other work"
    await bg.shutdown()                                     # graceful stop
    await asyncio.sleep(0)                                  # let done callbacks run


if __name__ == "__main__":
    asyncio.run(main())

# Output (verified on 3.13):
# [email] ok -> sent to a@x.com
# [broken] failed: RuntimeError('smtp down')
# [forever] cancelled
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Start background work | `asyncio.create_task(f())` | `f()` (promise starts itself) |
| Starts running | at the next `await` of the caller | immediately, synchronously until first await |
| Fire and forget | keep a reference (or GC risk) | no reference needed |
| Name for debugging | `name="..."` | none |
| Cancel | `task.cancel()` | `AbortController` by hand |
| Must run inside loop | yes (`RuntimeError` otherwise) | always in the event loop |

```python
# Python way — explicit
import asyncio                                           # stdlib

async def ping() -> None:                                # coroutine
    await asyncio.sleep(0.05)                            # wait
    print("pong")                                        # output

async def main() -> None:
    t = asyncio.create_task(ping())                      # schedule
    print("ping sent")                                   # prints first
    await t                                              # wait for it

asyncio.run(main())                                      # ping sent, pong
```
```javascript
// JavaScript way — no create_task needed
const ping = async () => { await new Promise(r => setTimeout(r, 50)); console.log('pong'); };
const p = ping();                                        // already running
console.log('ping sent');                                // ping sent, then pong
```

Key difference: in JS you can "fire and forget" by simply calling the function; in Python the coroutine does nothing until it is awaited or wrapped by `create_task`. In Python you must also keep a reference, or the Task can vanish mid-way.

---

## 🟠 FastAPI Connection
Inside an `async def` endpoint or the lifespan you can call `asyncio.create_task`. For work that must outlive a request (queue consumers, periodic jobs) create it in the lifespan and cancel it at shutdown. For short after-response work FastAPI offers `BackgroundTasks`, which runs after the response is sent. A version of this lifespan code was run with `TestClient` on 3.13.

```python
# FastAPI example — fire a task from an endpoint, keep the reference
import asyncio                                            # tasks
from fastapi import FastAPI                               # FastAPI

app: FastAPI = FastAPI()                                  # create app
background: set[asyncio.Task[None]] = set()               # strong references


async def send_receipt(order_id: int) -> None:            # slow side job
    await asyncio.sleep(0.5)                              # pretend email provider
    print(f"receipt sent for {order_id}")                 # log


@app.post("/orders/{order_id}")                           # POST /orders/7
async def create_order(order_id: int) -> dict[str, int]:
    task = asyncio.create_task(send_receipt(order_id))    # start, do not wait
    background.add(task)                                  # keep it alive
    task.add_done_callback(background.discard)            # clean up when finished
    return {"order": order_id}                            # respond immediately
```
Note: if the server stops, unfinished tasks are cancelled. For work that must not be lost, use a real queue (Celery, RQ, Redis streams) instead of `create_task`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not holding a reference to the task
✅ Correct: keep it in a set / attribute until it finishes

```python
# Wrong — the task may be garbage-collected and silently disappear
# asyncio.create_task(job())
# Right
# t = asyncio.create_task(job()); tasks.add(t); t.add_done_callback(tasks.discard)
```

❌ Mistake 2: Calling `create_task` with no running loop (module level, plain `def`)
✅ Correct: call it inside `async def`, or use `asyncio.run(main())` first

```python
# Wrong — RuntimeError: no running event loop (and the coroutine is never awaited)
# asyncio.create_task(job())
# Right
# async def main(): asyncio.create_task(job()) ...
# asyncio.run(main())
```

❌ Mistake 3: Exiting `main()` while tasks are still running
✅ Correct: await them (or `TaskGroup`); `asyncio.run` cancels whatever is left at exit

```python
# Wrong — job is cancelled when main returns, "job ran" never prints
# async def main(): asyncio.create_task(job())
# Right
# async def main(): t = asyncio.create_task(job()); await t
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import asyncio
async def job() -> None:
    await asyncio.sleep(0.1)
    print("job ran")
async def main() -> None:
    asyncio.create_task(job())
    await asyncio.sleep(0.01)
    print("main done")
asyncio.run(main())
print("end of script")
```
Answer: `main done`, `end of script` (verified on 3.13). `job ran` never prints. `main` returns after 0.01 s, while the task needs 0.1 s. When `asyncio.run` finishes `main`, it cancels all remaining tasks before closing the loop, so the task is cancelled during its `sleep`. The lesson: a task you create is not awaited automatically. Also, in an even shorter case (no `await` in `main`), such a task might get one loop step before cancellation, so do not rely on the timing; always await or track your tasks.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `create_task`, `ensure_future` and `loop.create_task`?
A1: `asyncio.create_task(coro)` is the modern, recommended API (3.7+): it uses the running loop and accepts only coroutines. `ensure_future` accepts coroutines, futures and awaitables and is mostly for library code. `loop.create_task` is the lower-level method on a specific loop object.

Q2: When does the task actually start?
A2: Not inside `create_task`. It starts on the next iteration of the loop, when the caller reaches an `await` that suspends. Python 3.12 added an opt-in "eager task factory" (`loop.set_task_factory(asyncio.eager_task_factory)`) that runs the first step immediately until the first real suspension.

Q3: Why can a task disappear if I do not keep a reference?
A3: The event loop keeps only weak references to tasks (to avoid memory leaks). A task that is not referenced elsewhere can be garbage-collected while it is waiting. The documentation tells you to keep a reference, typically in a set with `add_done_callback(set.discard)`.

Q4: What happens if a background task raises and nobody awaits it?
A4: The exception is stored in the task. When the task object is garbage-collected, asyncio logs "Task exception was never retrieved" (or calls the loop's exception handler). To handle it, await the task, call `task.exception()` in a done callback, or use a `TaskGroup`.

Q5: What is `name=` for and how are contexts handled?
A5: `name` shows up in `repr(task)`, logs and debugging tools, so give meaningful names. Each task gets a copy of the current `contextvars` context, so request-scoped values (such as a request id) are visible inside the task, and changes inside the task do not leak back to the creator.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want to start work and continue without waiting
- You start N jobs and `await` them later (`gather`, `wait`)
- Long-lived workers inside the lifespan of a service
- You need named, cancellable units of work

❌ Avoid when:
- You can simply `await` the coroutine
- The work must survive a crash or restart; use a durable queue
- You cannot keep references or handle errors; use `TaskGroup` instead
- The work is blocking or CPU-heavy; the task will still block the loop

---

## 📊 Visual Diagram
```
 main()                                   event loop ready queue
  |  t = create_task(job())  ---------->  [ job step 1 ]
  |  (returns Task immediately)
  |  print("continue")
  |  await something  ---- yields ------>  loop runs job step 1
  |                                        job: await sleep -> suspended
  |  ...                                   ...
  |  await t  <--------- job finished ---  result stored in t

 reference rule:  loop --weak--> task     your set --strong--> task
 exit rule:       asyncio.run() cancels tasks still pending when main() returns
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `create_task` | Schedule a coroutine as a Task | Coroutine को Task की तरह schedule करना |
| Fire and forget | Start work and never await it | शुरू करके कभी await न करना |
| Weak reference | Reference that does not keep an object alive | जो object को जीवित नहीं रखता |
| Eager task | Task whose first step runs immediately (3.12+) | जिसका पहला step तुरंत चलता है |
| Context | `contextvars` values copied into the task | Task में copy हुए contextvars |
| Shutdown | Cancel and await leftover tasks | बचे tasks को cancel करके await करना |

---

## ⚡ 3-Line Summary
English: `create_task` wraps a coroutine in a Task and schedules it on the running loop, returning at once so your code can continue. It starts running at the next `await`, and you must keep a strong reference and handle its errors. Tasks still pending when `asyncio.run` ends are cancelled.
Hindi: `create_task` coroutine को Task में लपेटकर चल रहे loop पर schedule करता है और तुरंत लौटता है ताकि आपका code चलता रहे। यह अगले `await` पर चलना शुरू होता है, और आपको strong reference रखना तथा उसकी errors संभालना ज़रूरी है। `asyncio.run` खत्म होने पर जो tasks pending हों वे cancel हो जाते हैं।

---

## ➡️ Next Topic
**245. asyncio Queue** — a safe way for tasks to pass work to each other: producers, consumers, back-pressure and graceful shutdown.
