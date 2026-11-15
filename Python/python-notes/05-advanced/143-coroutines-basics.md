---

# 143. Coroutines Basics
# हिंदी में: Coroutines की बुनियाद (रुककर फिर से चलने वाले functions)

---

## 🔵 Simple Definition (English)
A coroutine is a function that can pause and resume, and can also receive data while paused. Python has two kinds: old generator-based coroutines (using `yield` and `.send()`) and modern native coroutines (`async def` and `await`). Both let one thread switch between many tasks without blocking.

## 🔵 सरल परिभाषा (Hindi)
Coroutine ऐसा function है जो रुक सकता है, फिर चल सकता है, और रुके हुए समय में data भी ले सकता है। Python में दो तरह की हैं: पुरानी generator-based coroutines (`yield` और `.send()` से) और आधुनिक native coroutines (`async def` और `await`)। दोनों से एक thread कई tasks के बीच बिना block हुए बदल सकता है।

---

## 🔴 Problem it Solves
A normal function runs from start to end and blocks the thread while waiting for a network call or disk read. Threads are heavy and hard to coordinate. Coroutines are cheap (thousands in one thread) and switch only at clear points (`yield` / `await`), so waiting time is used for other work.

## 🔴 यह क्यों बना? (Hindi)
सामान्य function शुरू से अंत तक चलता है और network call या disk read के इंतज़ार में thread को block रखता है। Threads भारी हैं और उन्हें सँभालना कठिन है। Coroutines हल्की हैं (एक thread में हज़ारों) और सिर्फ साफ़ जगहों (`yield` / `await`) पर switch करती हैं, इसलिए इंतज़ार का समय दूसरे काम में लगता है।

---

## 🟢 How it Works — Step by Step

```
Generator coroutine                         Native coroutine (async/await)
─────────────────────                       ──────────────────────────────
Step 1 → c = worker(); next(c) (prime)      Step 1 → coro = fetch()  (nothing runs)
Step 2 → c.send(x) resumes, x is value      Step 2 → event loop runs it (asyncio.run)
Step 3 → body runs to next yield            Step 3 → hits `await` → pauses, loop runs others
Step 4 → c.close() ends it                  Step 4 → awaited thing finishes → resumes
Step 5 → StopIteration at end               Step 5 → returns result to the awaiter
```

## 🟢 कैसे काम करता है? (Hindi)
```
Generator coroutine                         Native coroutine (async/await)
─────────────────────                       ──────────────────────────────
Step 1 → c = worker(); next(c) (prime)      Step 1 → coro = fetch()  (कुछ नहीं चलता)
Step 2 → c.send(x) से resume, x value       Step 2 → event loop इसे चलाता है (asyncio.run)
Step 3 → body अगले yield तक चलती है          Step 3 → `await` पर रुकती है, loop दूसरे काम चलाता है
Step 4 → c.close() से खत्म                    Step 4 → await की चीज़ पूरी हो तो resume
Step 5 → अंत में StopIteration                Step 5 → result awaiter को मिलता है
```

---

## 🟡 Real World Example
A Swiggy order tracker must wait for restaurant confirmation, rider assignment and payment webhooks. With coroutines, one thread handles 10,000 orders and each waits with `await` without blocking others. A running-average sensor receiver uses a generator coroutine: each new reading is `.send()`-ed in and the current average comes back. FastAPI's `async def` endpoints are native coroutines run by the event loop.

## 🟡 Real Example Hindi mein
Swiggy order tracker को restaurant confirmation, rider assignment और payment webhooks का इंतज़ार करना पड़ता है। Coroutines से एक thread 10,000 orders सँभालता है और हर order `await` पर इंतज़ार करता है, दूसरों को block किए बिना। Sensor receiver generator coroutine से running average निकालता है: हर नई reading `.send()` से जाती है और average वापस आता है। FastAPI के `async def` endpoints native coroutines हैं जिन्हें event loop चलाता है।

---

## 💻 Code Example — Basic
```python
# Coroutine basics: generator style and async/await style - all lines commented
import asyncio  # event loop for native coroutines
from collections.abc import Coroutine, Generator  # type hints
from typing import Any  # generic Any


# 1) Generator-based coroutine: receives data with send()
def printer() -> Generator[None, str, None]:  # yields nothing, receives str
    print("ready")  # runs on priming
    while True:  # live until closed
        msg: str = yield  # pause here and wait for a message
        print("received:", msg)  # use the message


p = printer()  # create the coroutine (nothing runs)
next(p)  # prime: run to the first yield
# Output: ready
p.send("hello")  # resume with a value
# Output: received: hello
p.send("world")  # resume again
# Output: received: world
p.close()  # stop it


# 2) Native coroutine: async def
async def greet(name: str) -> str:  # coroutine function
    await asyncio.sleep(0)  # a pause point (lets other tasks run)
    return f"hi {name}"  # result


c = greet("Asha")  # calling returns a coroutine OBJECT, body not run
print(type(c).__name__)  # it is a coroutine
# Output: coroutine
print(asyncio.run(c))  # the event loop actually runs it
# Output: hi Asha

# Run two coroutines at the same time
async def slow(name: str, delay: float) -> str:  # simulated I/O
    await asyncio.sleep(delay)  # non-blocking wait
    return name  # result


async def main() -> list[str]:  # top level coroutine
    return await asyncio.gather(slow("a", 0.2), slow("b", 0.2))  # concurrent


import time  # to measure
start: float = time.perf_counter()  # start timer
print(asyncio.run(main()))  # run both
# Output: ['a', 'b']
print(time.perf_counter() - start < 0.35)  # took ~0.2s, not 0.4s
# Output: True

import inspect  # to inspect coroutine types
print(inspect.iscoroutinefunction(greet), inspect.isgeneratorfunction(printer))
# Output: True True
```

## 💻 Code Example — Advanced
```python
# Production style: coroutine decorator, running average, async timeout and errors
import asyncio  # async tools
from collections.abc import Callable, Coroutine, Generator  # type hints
from functools import wraps  # keep metadata
from typing import Any  # Any type


def primed(func: Callable[..., Generator[Any, Any, Any]]) -> Callable[..., Generator[Any, Any, Any]]:
    @wraps(func)  # keep name
    def start(*args: Any, **kwargs: Any) -> Generator[Any, Any, Any]:  # wrapper
        gen = func(*args, **kwargs)  # create generator
        next(gen)  # auto-prime so users can send() at once
        return gen  # return ready coroutine
    return start  # decorated function


@primed  # no manual next() needed
def running_average() -> Generator[float | None, float, None]:  # two-way coroutine
    total: float = 0.0  # sum
    count: int = 0  # how many
    average: float | None = None  # value to give back
    while True:  # until closed
        value: float = yield average  # return average, get next reading
        total += value  # add
        count += 1  # count
        average = round(total / count, 2)  # recompute


avg = running_average()  # ready immediately
print([avg.send(x) for x in (10, 20, 60)])  # feed sensor readings
# Output: [10.0, 15.0, 30.0]


@primed  # a tiny routing coroutine
def router(sink: list[str]) -> Generator[None, str, None]:  # collects messages
    try:  # clean exit
        while True:  # forever
            sink.append((yield).upper())  # receive, transform, store
    except GeneratorExit:  # triggered by close()
        sink.append("<closed>")  # cleanup signal


out: list[str] = []  # destination
r = router(out)  # create (already primed)
r.send("a")  # send
r.send("b")  # send
r.close()  # close
print(out)  # result
# Output: ['A', 'B', '<closed>']


# Native coroutines with timeout, error handling and cancellation
async def call_gateway(delay: float) -> str:  # fake payment gateway call
    await asyncio.sleep(delay)  # simulate waiting
    return "paid"  # success


async def safe_call(delay: float, timeout: float) -> str:  # defensive wrapper
    try:  # handle timeout
        return await asyncio.wait_for(call_gateway(delay), timeout)  # limit waiting
    except asyncio.TimeoutError:  # too slow
        return "timeout"  # graceful fallback


async def main() -> None:  # entry point
    print(await safe_call(0.01, 0.5))  # fast
    print(await safe_call(0.5, 0.05))  # slow
    tasks = [asyncio.create_task(call_gateway(0.01)) for _ in range(3)]  # run 3 at once
    print(await asyncio.gather(*tasks))  # wait for all
    coro = call_gateway(0)  # create but never await it
    coro.close()  # explicitly close to avoid "never awaited" warning
    print("closed unused coroutine")  # info


asyncio.run(main())  # run the program
# Output:
# paid
# timeout
# ['paid', 'paid', 'paid']
# closed unused coroutine
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript's `async function` and `await` map to Python's `async def` and `await`, but the runtime differs. JS promises start running when created; Python coroutine objects do **nothing** until awaited or scheduled. The Python generator `.send()` has a JS twin in `generator.next(value)`.

```python
# Python way
import asyncio
async def fetch(x):
    await asyncio.sleep(0.1)
    return x * 2
async def main():
    print(await asyncio.gather(fetch(1), fetch(2)))   # [2, 4]
asyncio.run(main())
```
```javascript
// JavaScript way
const fetchX = async (x) => { await new Promise(r => setTimeout(r, 100)); return x * 2; };
(async () => {
  console.log(await Promise.all([fetchX(1), fetchX(2)]));   // [2, 4]
})();
```

Key differences: in JS the event loop is built in; in Python you start it with `asyncio.run()`. A JS promise is already running when created; a Python coroutine needs `await` or `create_task`. Forgetting `await` in Python gives a "coroutine was never awaited" warning.

---

## 🟠 FastAPI Connection
`async def` path operations are native coroutines. FastAPI runs them on the event loop, so while one request awaits a database or HTTP call, the same thread serves other requests. Plain `def` endpoints are run in a thread pool instead. Never call blocking code (like `time.sleep` or `requests`) inside `async def`.

```python
# FastAPI: async endpoints run concurrently (pip install fastapi httpx)
import asyncio  # async tools
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # test

app: FastAPI = FastAPI()  # app


async def fake_db_call(name: str) -> str:  # coroutine simulating I/O
    await asyncio.sleep(0.1)  # non-blocking wait
    return f"user:{name}"  # result


@app.get("/profile/{name}")  # GET /profile/asha
async def profile(name: str) -> dict[str, str]:  # native coroutine endpoint
    data = await fake_db_call(name)  # await frees the loop meanwhile
    return {"data": data}  # response


@app.get("/both")  # runs two awaits concurrently
async def both() -> dict[str, list[str]]:  # endpoint
    results = await asyncio.gather(fake_db_call("a"), fake_db_call("b"))  # parallel waits
    return {"data": list(results)}  # response


client = TestClient(app)  # client
print(client.get("/profile/asha").json())  # one call
# Output: {'data': 'user:asha'}
print(client.get("/both").json())  # two calls in ~0.1s
# Output: {'data': ['user:a', 'user:b']}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling a coroutine function without `await`
```python
# Wrong - returns a coroutine object, body never runs
# result = greet("Asha")              # RuntimeWarning: coroutine was never awaited

# Right
# result = await greet("Asha")        # inside async code
# asyncio.run(greet("Asha"))          # at top level
```

❌ Mistake 2: Forgetting to prime a generator coroutine
```python
# Wrong - TypeError: can't send non-None value to a just-started generator
def co():
    x = yield
    print(x)
c = co()
# c.send("hi")

# Right - call next(c) first, or use a @primed decorator
c = co(); next(c)
try:
    c.send("hi")                       # prints hi, then the generator ends
except StopIteration:
    pass                               # normal end of a finished generator
```

❌ Mistake 3: Blocking the event loop
```python
# Wrong - time.sleep freezes every other task
# async def f(): time.sleep(2)

# Right
# async def f(): await asyncio.sleep(2)
# or run blocking code with: await asyncio.to_thread(blocking_func)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import asyncio

async def work(n):
    print("start", n)
    await asyncio.sleep(0)
    print("end", n)

async def main():
    await asyncio.gather(work(1), work(2))

asyncio.run(main())

def co():
    x = yield 1
    print("x =", x)

c = co()
print(next(c))
try:
    c.send(5)
except StopIteration:
    print("done")
```

**Answer**:
```
start 1
start 2
end 1
end 2
1
x = 5
done
```
Both coroutines start before either ends, because `await asyncio.sleep(0)` hands control back to the event loop. It is concurrency in one thread, not parallelism. In the generator part, `next` runs to `yield 1`, `send(5)` makes `x = 5`, and the function then ends, raising `StopIteration`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a coroutine and a generator?
A1: A generator mainly produces values (`yield`). A coroutine consumes values and cooperates with a scheduler (`send`, `await`). Technically generator-based coroutines are generators used for input.

Q2: What does `async def` return when called?
A2: A coroutine object. It runs only when awaited, wrapped in a task, or passed to `asyncio.run`.

Q3: Coroutines vs threads?
A3: Coroutines are cooperative (they switch only at `await`), very cheap, and run in a single thread, so there are no data races between awaits. Threads are preemptive and heavier. Coroutines do not speed up CPU-bound work.

Q4: What is `await` doing?
A4: It pauses the current coroutine until the awaited object finishes, letting the event loop run other tasks meanwhile.

Q5: Are old `@asyncio.coroutine` and `yield from` coroutines still used?
A5: No. `@asyncio.coroutine` was removed in Python 3.11. Use `async def` and `await`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Many tasks wait on I/O (HTTP calls, DB queries, sockets)
- You build servers like FastAPI that handle many requests
- You need a small stateful receiver (generator coroutine)

❌ Avoid when:
- Work is CPU-heavy (use multiprocessing)
- The code is simple and sequential
- Your libraries are blocking and have no async version

---

## 📊 Visual Diagram

```
 Event loop (one thread)
 ┌───────────────────────────────────────────────┐
 │ task A: run ─► await (wait) ·········· resume │
 │ task B:          run ─► await ···· resume     │
 │ task C:                   run ─► done         │
 └───────────────────────────────────────────────┘
 While A waits for I/O, the loop runs B and C.

 Generator coroutine:  send(x) ─► [ yield ] ─► value out ─► send(y) ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coroutine | Function that can pause and resume | रुककर फिर चलने वाला function |
| `await` | Pause until something finishes | किसी के पूरा होने तक रुकना |
| Event loop | Scheduler that runs coroutines | coroutines चलाने वाला scheduler |
| Priming | First `next()` on generator coroutine | पहला `next()` |
| Task | Coroutine scheduled on the loop | loop पर schedule हुई coroutine |
| Cooperative | Switches only at pause points | सिर्फ तय जगहों पर switch |

---

## ⚡ 3-Line Summary
English: A coroutine can pause and resume, so many can share one thread. Generator coroutines use `yield`/`send`; modern ones use `async def`/`await` on an event loop. They help with I/O waiting, not CPU work.
Hindi: Coroutine रुक और फिर चल सकती है, इसलिए कई coroutines एक thread साझा करती हैं। Generator coroutines `yield`/`send` और आधुनिक `async def`/`await` event loop पर चलती हैं। ये I/O इंतज़ार में मदद करती हैं, CPU काम में नहीं।

---

## ➡️ Next Topic
**145. with Statement** — automatic setup and cleanup for files, locks and connections.
