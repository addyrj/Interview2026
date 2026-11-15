---

# 258. trio Library Basics
# हिंदी में: trio Library की बुनियादी बातें

---

## 🔵 Simple Definition (English)
`trio` is an async library for Python that is built around structured concurrency. Instead of loose tasks, you start child tasks inside a "nursery" (`async with trio.open_nursery()`), and the block waits for them all. Its design makes timeouts, cancellation and error handling simple and predictable.

## 🔵 सरल परिभाषा (Hindi)
`trio` Python की एक async library है जो structured concurrency पर बनी है। ढीले tasks की जगह आप child tasks को "nursery" (`async with trio.open_nursery()`) के अंदर शुरू करते हैं, और block सबके खत्म होने तक रुकता है। इसके design से timeouts, cancellation और error handling सरल और अनुमानित हो जाते हैं।

---

## 🔴 Problem it Solves
In asyncio you can start a task with `create_task()` and forget it: it may fail silently, outlive its caller, or be impossible to cancel cleanly. Cancellation and timeouts are scattered across APIs. Trio fixes this by design: tasks only live inside nurseries, errors always propagate to the parent, and every cancellation or timeout works the same way through cancel scopes. The result is fewer hidden bugs in complex concurrent code.

## 🔴 यह क्यों बना? (Hindi)
asyncio में आप `create_task()` से task शुरू करके भूल सकते हैं: वह चुपचाप fail हो सकता है, अपने caller से ज्यादा जी सकता है, या साफ तरीके से cancel नहीं हो पाता। Cancellation और timeouts अलग-अलग APIs में बिखरे हैं। Trio इसे design से ठीक करता है: tasks सिर्फ nurseries के अंदर जीते हैं, errors हमेशा parent तक पहुंचते हैं, और हर cancellation या timeout cancel scopes से एक ही तरीके से चलता है। नतीजा: जटिल concurrent code में कम छिपे bugs।

---

## 🟢 How it Works — Step by Step

```
Step 1 → trio.run(main) starts trio's own event loop (NOT compatible with asyncio libraries)
Step 2 → async with trio.open_nursery() as nursery:  creates a place for child tasks
Step 3 → nursery.start_soon(fn, arg) starts a child task
Step 4 → The block waits until every child is done
Step 5 → A child raises -> trio cancels the siblings -> error propagates (as ExceptionGroup)
Step 6 → Timeouts: trio.move_on_after(s) (silent) / trio.fail_after(s) (raises TooSlowError)
Step 7 → Channels (open_memory_channel) let tasks send messages to each other
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → trio.run(main) trio का अपना event loop शुरू करता है (asyncio libraries से compatible नहीं)
Step 2 → async with trio.open_nursery() as nursery:  child tasks के लिए जगह बनाता है
Step 3 → nursery.start_soon(fn, arg) child task शुरू करता है
Step 4 → Block तब तक रुकता है जब तक हर child खत्म न हो
Step 5 → Child raise करे -> trio siblings को cancel करता है -> error ऊपर जाता है (ExceptionGroup में)
Step 6 → Timeouts: trio.move_on_after(s) (चुपचाप) / trio.fail_after(s) (TooSlowError उठाता है)
Step 7 → Channels (open_memory_channel) से tasks आपस में messages भेजते हैं
```

---

## 🟡 Real World Example
A network tool (port scanner, health-checker for 200 servers, or a custom chat server) must run many connections and shut down cleanly on Ctrl+C or timeout. In trio you open one nursery, start a task per server, and wrap the whole thing in `trio.move_on_after(10)`. When time is up, every child is cancelled safely and resources are released. Teams that need very correct cancellation (infrastructure tools, testing frameworks) like trio for this reason.

## 🟡 Real Example Hindi mein
Network tool (port scanner, 200 servers का health-checker, या custom chat server) को कई connections चलाने होते हैं और Ctrl+C या timeout पर साफ बंद होना होता है। Trio में आप एक nursery खोलते हैं, हर server के लिए एक task शुरू करते हैं, और पूरे काम को `trio.move_on_after(10)` में लपेटते हैं। समय खत्म होने पर हर child सुरक्षित रूप से cancel होता है और resources छूट जाते हैं। जिन teams को बहुत सही cancellation चाहिए (infrastructure tools, testing frameworks), वे इसी कारण trio पसंद करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic trio (verified: trio 0.35, Python 3.13)
# pip install trio
import trio                                              # the library


async def child(name: str, delay: float, out: list[str]) -> None:
    await trio.sleep(delay)                              # trio's own sleep (asyncio.sleep will NOT work)
    out.append(name)                                     # record finish order


async def main() -> None:
    out: list[str] = []                                  # shared results
    async with trio.open_nursery() as nursery:           # nursery = scope for children
        nursery.start_soon(child, "slow", 0.1, out)      # child 1 (pass function and args, no call!)
        nursery.start_soon(child, "fast", 0.01, out)     # child 2
    print(out)                                           # runs after BOTH children ended

    with trio.move_on_after(0.05) as scope:              # timeout that exits silently
        await trio.sleep(1)                              # too slow, will be cancelled
    print("timed out", scope.cancelled_caught)           # True if the deadline fired

    try:
        with trio.fail_after(0.05):                      # timeout that raises
            await trio.sleep(1)                          # too slow
    except trio.TooSlowError:                            # trio's timeout exception
        print("TooSlowError")                            # we handled it


trio.run(main)                                           # start trio (note: no parentheses on main)

# Output:
# ['fast', 'slow']
# timed out True
# TooSlowError
```

## 💻 Code Example — Advanced
```python
# Production style: channels (producer/consumer), error propagation, thread offload
import trio                                              # library


async def producer(send: trio.MemorySendChannel[int], n: int) -> None:
    async with send:                                     # closing the channel tells consumers "done"
        for i in range(n):                               # send n numbers
            await send.send(i)                           # waits if the buffer is full


async def consumer(recv: trio.MemoryReceiveChannel[int]) -> None:
    async with recv:                                     # close our end at the end
        async for v in recv:                             # loop stops when the sender closes
            print("got", v)                              # handle each message


async def main() -> None:
    send, recv = trio.open_memory_channel[int](2)        # small buffer = back-pressure
    async with trio.open_nursery() as n:                 # both tasks in one nursery
        n.start_soon(producer, send, 3)                  # producer task
        n.start_soon(consumer, recv)                     # consumer task

    try:
        async with trio.open_nursery() as n:             # nursery where a child fails
            async def bad() -> None:
                raise ValueError("boom")                 # error inside a child

            n.start_soon(bad)                            # start the failing child
            n.start_soon(trio.sleep, 5)                  # sibling is cancelled, no 5 s wait
    except* ValueError as eg:                            # 3.11+: ExceptionGroup handling
        print("group", [str(e) for e in eg.exceptions])  # ['boom']

    print(await trio.to_thread.run_sync(lambda: 42))     # blocking code off the event loop


trio.run(main)                                           # run

# Output:
# got 0
# got 1
# got 2
# group ['boom']
# 42
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | trio | JavaScript |
|---------|------|-----------|
| Group of tasks | nursery | `Promise.all` (no cancellation) |
| Timeout | `move_on_after`, `fail_after` | `AbortSignal.timeout` + manual checks |
| Cancel | cancel scope | `AbortController` (cooperative) |
| Start a task | `start_soon` (must be in nursery) | call an async function (fire-and-forget possible) |
| Fire-and-forget | impossible by design | easy (and a common bug) |
| Message passing | memory channels | none built in |

```python
# Python way (trio)
async with trio.open_nursery() as n:
    n.start_soon(task_a)
    n.start_soon(task_b)
```
```javascript
// JavaScript way
await Promise.all([taskA(), taskB()]);   // if one rejects, the other keeps running
// Fire-and-forget (unsafe, errors become unhandled rejections):
taskC();
```

Key difference: JavaScript lets you start background promises anywhere; Trio makes that impossible, so there are no "floating" tasks. The cost is that you must structure your program as nested scopes, which most people find easier to reason about.

---

## 🟠 FastAPI Connection
FastAPI itself runs on asyncio (via uvicorn), so you do NOT use trio code inside a standard FastAPI app. The connection is through anyio: Starlette/FastAPI and httpx are written on anyio, which can also run on trio. You can test your FastAPI code on trio with the anyio pytest plugin, and use trio directly for standalone workers, CLIs and network tools that sit next to your API.

```python
# FastAPI example — run the SAME anyio-based code on trio (verifies the idea; no web server needed)
import anyio                                             # anyio supports both backends


async def fetch_prices() -> dict[str, float]:
    results: dict[str, float] = {}                       # collector

    async def one(name: str, price: float) -> None:
        await anyio.sleep(0.01)                          # pretend API call
        results[name] = price                            # store

    async with anyio.create_task_group() as tg:          # same code on asyncio or trio
        tg.start_soon(one, "a", 1.0)                     # source a
        tg.start_soon(one, "b", 2.0)                     # source b
    return results                                       # both ready


print(anyio.run(fetch_prices, backend="trio"))           # run on trio
print(anyio.run(fetch_prices))                           # run on asyncio

# Output (dict key order varies run to run: tasks finish in arbitrary order):
# {'b': 2.0, 'a': 1.0}
# {'a': 1.0, 'b': 2.0}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `asyncio` libraries (aiohttp, asyncpg, `asyncio.sleep`) inside trio
✅ Correct: use trio-native libraries (`httpx` supports trio, `trio-websocket`) or `trio-asyncio`

```python
# Wrong — raises RuntimeError: no running event loop
import asyncio
async def main(): await asyncio.sleep(1)
trio.run(main)
# Right
async def main(): await trio.sleep(1)
trio.run(main)
```

❌ Mistake 2: Calling the function in `start_soon` or `trio.run`
✅ Correct: pass the function and its arguments separately

```python
# Wrong — passes a coroutine object (TypeError / warning)
nursery.start_soon(child("a", 1, out))
# Right
nursery.start_soon(child, "a", 1, out)
```

❌ Mistake 3: Swallowing `trio.Cancelled`
✅ Correct: never catch it with a bare `except`; let it propagate (use `finally` for cleanup)

```python
# Wrong — cancellation is ignored; the task will not stop
try:
    await work()
except BaseException:
    pass
# Right
try:
    await work()
finally:
    await cleanup()     # shield with trio.CancelScope(shield=True) if cleanup must await
```

---

## 🧠 Tricky Interview Question

```python
# What is printed, and how long does it take?
import trio

async def main() -> None:
    with trio.move_on_after(1) as scope:
        async with trio.open_nursery() as n:
            n.start_soon(trio.sleep, 10)
            n.start_soon(trio.sleep, 20)
    print(scope.cancelled_caught)

trio.run(main)
```
Answer: It prints `True` after about 1 second. The cancel scope has a 1-second deadline. When it expires, trio cancels everything inside it: the nursery body and both child sleeps. `move_on_after` swallows the cancellation (no exception escapes) and `cancelled_caught` becomes `True`. This composability, where one timeout cleanly cancels a whole tree of tasks, is the main reason people choose trio.

---

## ⚫ Interview Questions + Answers

Q1: What is a nursery?
A1: A context manager (`open_nursery`) that owns child tasks. It waits for them all on exit; if one fails it cancels the rest and propagates the error.

Q2: Trio vs asyncio?
A2: Trio is simpler and stricter (structured concurrency, consistent cancellation, no fire-and-forget); asyncio has a far bigger ecosystem (aiohttp, asyncpg, FastAPI/uvicorn). Modern asyncio (3.11+) adopted `TaskGroup` and `timeout()`, inspired by trio.

Q3: Can I run FastAPI on trio?
A3: Not as a normal deployment: uvicorn uses asyncio. But anyio-based libraries (Starlette, httpx) can run on trio, and Hypercorn can serve ASGI apps on trio.

Q4: What is `trio.Cancelled`?
A4: An exception injected at the next checkpoint (`await`) when a scope is cancelled. It derives from `BaseException`, so `except Exception` does not catch it. It must not be swallowed.

Q5: What is a checkpoint?
A5: An `await` that lets trio check for cancellation and switch tasks (`trio.sleep(0)`, channel send/receive, I/O). Code with no checkpoint cannot be cancelled and blocks everyone, just like blocking code in asyncio.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing new network tools, servers or infrastructure code where correctness matters
- You want strict structured concurrency and predictable cancellation
- You are learning the concepts that modern asyncio also adopted

❌ Avoid when:
- You need asyncio ecosystem libraries (aiohttp, asyncpg, motor, uvicorn)
- A typical FastAPI project (stay on asyncio; use anyio for portability)
- Your team already knows asyncio well and has no cancellation pain

---

## 📊 Visual Diagram
```
trio.run(main)
   │
   └── async with open_nursery() as n:  ───────────────┐
          ├─ n.start_soon(A)  ──── runs ───┐           │ block ends only
          ├─ n.start_soon(B)  ──── runs ───┤           │ when all children
          └─ n.start_soon(C)  ──── fails ──┘           │ are finished
                               │                       │
                  siblings A, B get Cancelled ◄────────┘
                               │
                    ExceptionGroup raised to the parent

with trio.move_on_after(1):   <- one deadline cancels the whole tree inside
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Nursery | Scope that owns child tasks | Child tasks का मालिक scope |
| Checkpoint | Await point where cancel/switch can occur | Cancel/switch वाला await बिंदु |
| Cancel scope | Cancellable region with optional deadline | Deadline वाला cancel योग्य हिस्सा |
| `Cancelled` | Exception delivered on cancellation | Cancellation पर आने वाला exception |
| Channel | Message pipe between tasks | Tasks के बीच message pipe |
| `TooSlowError` | Raised by `fail_after` | `fail_after` से उठने वाला error |

---

## ⚡ 3-Line Summary
English: Trio is an async library built on structured concurrency: children live inside nurseries, errors propagate, and cancel scopes make timeouts and cancellation consistent. It has its own event loop, so it is not compatible with asyncio-only libraries.
Hindi: Trio structured concurrency पर बनी async library है: children nurseries में रहते हैं, errors ऊपर जाते हैं, और cancel scopes से timeouts और cancellation एक जैसे चलते हैं। इसका अपना event loop है, इसलिए यह सिर्फ asyncio वाली libraries के साथ compatible नहीं है।

---

## ➡️ Next Topic
**259. Async Testing** — testing coroutines and FastAPI endpoints with pytest-asyncio and anyio.
