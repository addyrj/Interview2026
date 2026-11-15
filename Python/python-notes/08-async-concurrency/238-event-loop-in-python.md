---

# 238. Event Loop in Python
# हिंदी में: Python में Event Loop — asyncio का दिल

---

## 🔵 Simple Definition (English)
The event loop is a loop that runs inside one thread. It keeps a list of ready callbacks and waiting coroutines, runs one until it hits `await`, then switches to another one that is ready. It also watches sockets and timers so it knows when a waiting task can continue.

## 🔵 सरल परिभाषा (Hindi)
Event loop एक loop है जो एक thread के अंदर चलता है। यह ready callbacks और इंतज़ार कर रही coroutines की list रखता है, एक को तब तक चलाता है जब तक `await` न आ जाए, फिर किसी दूसरी ready वाली पर चला जाता है। यह sockets और timers भी देखता है ताकि पता रहे कि कौन सा waiting task आगे बढ़ सकता है।

---

## 🔴 Problem it Solves
A normal program waits: while it reads from a socket, the whole thread does nothing. One thread per connection works for 100 users but not for 50,000 (memory, context switches). The event loop lets ONE thread serve thousands of connections, because it never waits idle: while one task waits for the network, it runs another.

## 🔴 यह क्यों बना? (Hindi)
सामान्य program इंतज़ार करता है: socket से पढ़ते समय पूरा thread कुछ नहीं करता। हर connection के लिए एक thread 100 users तक ठीक है पर 50,000 तक नहीं (memory, context switches)। Event loop से ONE thread हज़ारों connections संभालता है, क्योंकि वह कभी खाली नहीं बैठता: एक task network का इंतज़ार करे तो वह दूसरा चला देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → asyncio.run(main()) creates a new event loop, runs main() as a task
Step 2 → Loop picks a READY task/callback from its ready queue and runs it
Step 3 → The task runs until it hits `await something_slow`
Step 4 → The task is suspended; the loop registers "wake me when X is done"
         (a socket event through the OS selector: epoll / kqueue, or a timer)
Step 5 → Loop picks the next ready task (go to Step 2)
Step 6 → When the OS says the socket is ready or a timer fires, the waiting
         task is moved back to the ready queue
Step 7 → When main() finishes, asyncio.run cancels leftover tasks and closes the loop

   while True:
       run all ready callbacks           (call_soon / task steps)
       compute timeout = nearest timer   (call_later)
       events = selector.select(timeout) (wait for sockets)
       move finished waits -> ready queue
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → asyncio.run(main()) नया event loop बनाता है, main() को task की तरह चलाता है
Step 2 → Loop अपनी ready queue से एक READY task/callback उठाकर चलाता है
Step 3 → Task तब तक चलता है जब तक `await something_slow` न आ जाए
Step 4 → Task रुक जाता है; loop नोट करता है "X पूरा हो तो जगाना"
         (OS selector से socket event: epoll / kqueue, या timer)
Step 5 → Loop अगला ready task उठाता है (Step 2 पर वापस)
Step 6 → जब OS बताए कि socket ready है या timer बजे, तो waiting task
         वापस ready queue में चला जाता है
Step 7 → main() खत्म होने पर asyncio.run बचे tasks cancel करता है और loop बंद करता है
```

---

## 🟡 Real World Example
Zomato's live order-tracking server keeps 100,000 WebSocket connections open from one process. Each connection mostly waits; the event loop wakes only the connections that have data. A FastAPI service calling OpenAI, a database and Redis for each request uses the loop to overlap all those waits. A Telegram bot, a web crawler and a Discord bot are all single event loops.

## 🟡 Real Example Hindi mein
Zomato का live order-tracking server एक process से 100,000 WebSocket connections खुले रखता है। ज़्यादातर connections इंतज़ार करते हैं; event loop सिर्फ उन्हें जगाता है जिनके पास data आया हो। FastAPI service जो हर request में OpenAI, database और Redis बुलाती है, उन सभी waits को loop से overlap करती है। Telegram bot, web crawler और Discord bot सब एक-एक event loop ही हैं।

---

## 💻 Code Example — Basic
```python
# Basic: the event loop
import asyncio                                              # the library


async def hello() -> str:                                   # a coroutine function
    await asyncio.sleep(0.1)                                # hand control back to the loop
    return "hello"                                          # result


async def main() -> None:
    loop = asyncio.get_running_loop()                       # the loop that runs us right now
    print(type(loop).__name__)                              # loop class name
    print(loop.is_running())                                # True while inside the loop
    loop.call_soon(print, "call_soon runs after main yields")   # schedule a plain callback
    print(await hello())                                    # await -> loop runs the callback meanwhile
    print(loop.time() > 0)                                  # loop has its own monotonic clock


asyncio.run(main())                                         # create loop, run main, close loop

# Output (loop class shown is the default on macOS/Linux, verified on Python 3.13):
# _UnixSelectorEventLoop
# True
# call_soon runs after main yields
# hello
# True
```

## 💻 Code Example — Advanced
```python
# Production style: call_later, run_in_executor, exception handler, responsive loop
import asyncio                                              # asyncio
import time                                                 # blocking sleep for demo
from typing import Any                                      # type


def blocking_job(n: int) -> int:                            # a blocking function (would freeze the loop)
    time.sleep(0.2)                                         # blocks the thread it runs in
    return n * 2                                            # result


def on_error(loop: asyncio.AbstractEventLoop, ctx: dict[str, Any]) -> None:
    print("handler caught:", ctx["exception"])              # central place for unhandled task errors


async def ticker(log: list[str]) -> None:                   # proves the loop stays responsive
    for i in range(3):                                      # three ticks
        log.append(f"tick{i}")                              # record
        await asyncio.sleep(0.05)                           # yield to the loop


async def boom() -> None:                                   # a task nobody awaits
    raise RuntimeError("background failure")                # will reach the exception handler


async def main() -> None:
    loop = asyncio.get_running_loop()                       # current loop
    loop.set_exception_handler(on_error)                    # install handler
    log: list[str] = []                                     # shared log
    loop.call_later(0.08, log.append, "call_later")         # schedule a callback in 0.08s
    t = asyncio.create_task(ticker(log))                    # run ticker concurrently
    result = await loop.run_in_executor(None, blocking_job, 21)   # blocking work in a thread pool
    await t                                                 # let ticker finish
    print(result, log)                                      # loop was never blocked
    asyncio.create_task(boom())                             # fire and forget (bad practice, demo only)
    await asyncio.sleep(0.1)                                # give it time to fail
    import gc; gc.collect()                                 # force the "never retrieved" report
    await asyncio.sleep(0)                                  # let handler run


if __name__ == "__main__":
    asyncio.run(main(), debug=False)                        # debug=True gives slow-callback warnings

# Output (verified on 3.13; the position of 'call_later' in the list depends on timing):
# 42 ['tick0', 'tick1', 'call_later', 'tick2']
# handler caught: background failure
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python asyncio | JavaScript |
|---------|----------------|-----------|
| Loop starts | explicit: `asyncio.run(main())` | automatic when script runs |
| Loop per | thread (you can have several) | one per thread / worker |
| Defer a call | `loop.call_soon(fn)` | `queueMicrotask` / `setTimeout(fn, 0)` |
| Timer | `loop.call_later(s, fn)` | `setTimeout(fn, ms)` |
| Blocking work | `loop.run_in_executor` | `worker_threads` |
| Await keyword | `await` inside `async def` | `await` inside `async function` |

```python
# Python way — you start the loop yourself
import asyncio                                           # stdlib

async def main() -> None:                                # entry coroutine
    await asyncio.sleep(0.1)                             # non-blocking sleep
    print("done")                                        # done

asyncio.run(main())                                      # create loop + run + close
```
```javascript
// JavaScript way — the loop already exists
setTimeout(() => console.log('done'), 100);              // timer handled by the built-in loop
// top-level code is already running inside the Node/browser event loop
```

Key difference: in JavaScript the loop is hidden and always running. In Python it is a normal object that you create, run and close, and a program can run without any loop at all. Also, Python's `await` on a plain coroutine runs it immediately in the same task (JS promises start eagerly).

---

## 🟠 FastAPI Connection
Uvicorn creates the event loop (uvloop if installed) and runs your whole FastAPI app on it. Every `async def` endpoint is a coroutine running on that single loop. One slow blocking line (`time.sleep`, `requests.get`, heavy loop) inside an `async def` freezes ALL requests, since there is only one thread running the loop. Verified with `TestClient` on 3.13:

```python
# FastAPI example — use the loop correctly
import asyncio                                            # loop access
import time                                               # blocking function
from fastapi import FastAPI                               # FastAPI

app: FastAPI = FastAPI()                                  # create app


def slow_report() -> str:                                 # blocking work (pretend library call)
    time.sleep(0.2)                                       # blocks its thread
    return "report ready"                                 # result


@app.get("/report")                                       # GET /report
async def report() -> dict[str, str]:
    loop = asyncio.get_running_loop()                     # the loop uvicorn started
    text: str = await loop.run_in_executor(None, slow_report)   # move blocking call to a thread
    return {"status": text}                               # other requests keep flowing


@app.get("/summary")                                      # GET /summary
async def summary() -> dict[str, list[str]]:
    async def part(x: str) -> str:                        # small coroutine
        await asyncio.sleep(0.01)                         # simulate I/O
        return x                                          # value
    a, b = await asyncio.gather(part("users"), part("orders"))   # overlap on the same loop
    return {"parts": [a, b]}                              # {"parts": ["users", "orders"]}
```
(`/summary` returned `{'parts': ['users', 'orders']}` when run; `/report` is the same pattern as the `run_in_executor` call verified above.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking the loop with `time.sleep` or `requests` inside `async def`
✅ Correct: `await asyncio.sleep`, an async client (`httpx.AsyncClient`), or `run_in_executor` / `asyncio.to_thread`

```python
# Wrong — freezes every other task for 2 seconds
# async def handler(): time.sleep(2)
# Right
# async def handler(): await asyncio.sleep(2)
# async def handler(): await asyncio.to_thread(time.sleep, 2)
```

❌ Mistake 2: Calling `asyncio.run()` inside a running loop (Jupyter, FastAPI, pytest-asyncio)
✅ Correct: just `await` the coroutine, or create a task

```python
# Wrong — RuntimeError: asyncio.run() cannot be called from a running event loop
# async def f(): asyncio.run(other())
# Right
# async def f(): await other()
```

❌ Mistake 3: Using `loop = asyncio.get_event_loop()` outside a running loop in new code
✅ Correct: `asyncio.run(main())`, and `asyncio.get_running_loop()` inside coroutines (`get_event_loop()` without a running loop is deprecated in 3.12+ and raises in 3.14 when no loop exists)

```python
# Wrong (DeprecationWarning / error in newer versions)
# loop = asyncio.get_event_loop(); loop.run_until_complete(main())
# Right
# asyncio.run(main())
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
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
Answer: `before await`, `callback`, `task`, `after await` (verified on 3.13). Nothing else runs until `main` reaches an `await`, because the loop is single-threaded and cooperative. So `before await` prints first. `await asyncio.sleep(0)` yields once to the loop; the loop then runs ready items in the order they were scheduled: the `call_soon` callback first, then the task's first step, and finally resumes `main`. Key idea: scheduling does not run the code; yielding does.

---

## ⚫ Interview Questions + Answers

Q1: Is the event loop multi-threaded?
A1: No. One loop runs in one thread and runs one piece of Python code at a time. Concurrency comes from switching at `await` points, not from parallel execution. You can run one loop per thread, but loops are not thread-safe: use `loop.call_soon_threadsafe` or `asyncio.run_coroutine_threadsafe` to talk to a loop from another thread.

Q2: What happens if one coroutine never awaits?
A2: It blocks the loop completely until it finishes, because the loop has no way to interrupt it. Long CPU loops should be moved to a process pool, and blocking I/O to a thread (`asyncio.to_thread`).

Q3: How does the loop know when a socket is ready?
A3: It asks the operating system through a selector (`epoll` on Linux, `kqueue` on macOS, IOCP on Windows with the Proactor loop). The OS wakes the loop when data arrives, so no CPU is wasted polling.

Q4: What is the difference between `call_soon`, `call_later` and `create_task`?
A4: `call_soon(fn)` runs a normal function on the next loop iteration, `call_later(s, fn)` runs it after `s` seconds, `create_task(coro)` wraps a coroutine in a Task and schedules its first step. Callbacks are plain functions; tasks can `await`.

Q5: Why use `asyncio.run()` and not `loop.run_until_complete()`?
A5: `asyncio.run` creates a fresh loop, runs the coroutine, cancels leftover tasks, shuts down async generators and the default executor, and closes the loop. It is the recommended, safe high-level entry point (3.7+). In 3.11+ `asyncio.Runner` offers the same with reusable context.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many connections or requests that mostly wait (APIs, WebSockets, scrapers)
- Libraries you use have async versions (httpx, asyncpg, motor, aiohttp)
- You need timers, timeouts and cancellation on a single thread

❌ Avoid when:
- Work is CPU-heavy; use processes
- You depend on blocking-only libraries and cannot wrap them
- A short script where plain sequential code is simpler
- You would mix in blocking calls everywhere (async gives no benefit then)

---

## 📊 Visual Diagram
```
                    +---------------- EVENT LOOP (1 thread) ----------------+
 ready queue  --->  | run task A until `await`  -> A suspended               |
 [A][B][C]          | run task B until `await`  -> B suspended               |
                    | run task C ...                                         |
                    |                                                        |
                    | ask OS selector: any socket ready? any timer due?      |
                    |   yes -> move that waiting task back to ready queue    |
                    +--------------------------------------------------------+

 one thread, many tasks, switching ONLY at `await`
 a blocking call inside a task = everything stops
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Scheduler that runs tasks and I/O callbacks | Tasks और I/O callbacks चलाने वाला scheduler |
| Cooperative | Tasks give up control themselves at `await` | Tasks खुद `await` पर control छोड़ते हैं |
| Selector | OS tool that reports ready sockets | Ready sockets बताने वाला OS tool |
| Callback | Plain function scheduled to run later | बाद में चलने के लिए schedule हुआ function |
| Executor | Thread/process pool used from the loop | Loop से इस्तेमाल होने वाला thread/process pool |
| Blocking call | Call that stops the whole thread | पूरे thread को रोक देने वाली call |

---

## ⚡ 3-Line Summary
English: The event loop is a single-threaded scheduler that runs ready tasks and switches to another whenever one hits `await`. It uses OS selectors to wake tasks when I/O finishes, so one thread handles thousands of connections. Never block it: move blocking or CPU work to threads or processes.
Hindi: Event loop एक single-threaded scheduler है जो ready tasks चलाता है और `await` आते ही दूसरे पर चला जाता है। I/O पूरा होने पर OS selectors से tasks को जगाता है, इसलिए एक thread हज़ारों connections संभालता है। इसे कभी block न करें: blocking या CPU काम threads या processes में भेजें।

---

## ➡️ Next Topic
**239. async/await in Python** is already covered in the asyncio notes, so continue with **240. Coroutines in Python** — what `async def` really creates, why calling it does not run it, and how `await` drives it.
