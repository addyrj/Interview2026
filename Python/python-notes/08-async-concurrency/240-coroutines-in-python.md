---

# 240. Coroutines in Python
# हिंदी में: Python में Coroutines — रुक कर फिर चलने वाले functions

---

## 🔵 Simple Definition (English)
A coroutine is a function that can pause in the middle (at `await`) and continue later from the same place. You create one with `async def`. Calling it does NOT run it: you get a coroutine object, and something (`await`, `asyncio.run`, or a Task) must drive it.

## 🔵 सरल परिभाषा (Hindi)
Coroutine ऐसा function है जो बीच में (`await` पर) रुक सकता है और बाद में उसी जगह से आगे चल सकता है। इसे `async def` से बनाते हैं। इसे call करने से यह चलता नहीं: एक coroutine object मिलता है, और उसे कोई चलाता है (`await`, `asyncio.run` या Task)।

---

## 🔴 Problem it Solves
A normal function runs from start to end without stopping, so waiting for a database blocks everything. Callbacks fix that but make code hard to read ("callback hell"). Coroutines let you write code that looks sequential (`user = await get_user()`) while the event loop runs other work during every wait.

## 🔴 यह क्यों बना? (Hindi)
सामान्य function शुरू से आखिर तक बिना रुके चलता है, इसलिए database का इंतज़ार सब कुछ रोक देता है। Callbacks इसे हल करते हैं पर code पढ़ना मुश्किल हो जाता है ("callback hell")। Coroutines से आप ऐसा code लिखते हैं जो क्रम से चलता दिखता है (`user = await get_user()`), जबकि हर इंतज़ार के दौरान event loop दूसरा काम चला देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `async def f(): ...` defines a coroutine FUNCTION
Step 2 → Calling f() returns a coroutine OBJECT; no code has run yet
Step 3 → `await f()` (or a Task, or asyncio.run) starts it with send(None)
Step 4 → The body runs until it reaches `await something_not_ready`
Step 5 → The coroutine suspends and gives control to the event loop
Step 6 → When the awaited thing is ready, the loop resumes the coroutine
Step 7 → `return value` ends it; the awaiter receives `value`
         An exception inside is raised at the `await` line of the caller
Note   → A coroutine object can be awaited only ONCE
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `async def f(): ...` एक coroutine FUNCTION बनाता है
Step 2 → f() बुलाने से coroutine OBJECT मिलता है; अभी कोई code नहीं चला
Step 3 → `await f()` (या Task, या asyncio.run) इसे send(None) से शुरू करता है
Step 4 → Body तब तक चलती है जब तक `await something_not_ready` न आ जाए
Step 5 → Coroutine रुक जाती है और control event loop को दे देती है
Step 6 → जब awaited चीज़ तैयार हो, loop coroutine को दोबारा चलाता है
Step 7 → `return value` से खत्म होती है; await करने वाले को `value` मिलता है
         अंदर की exception caller की `await` line पर raise होती है
ध्यान → Coroutine object सिर्फ एक बार await हो सकता है
```

---

## 🟡 Real World Example
A Swiggy checkout handler does `restaurant = await get_restaurant()`, `coupon = await validate_coupon()`, `payment = await charge()`. It reads like normal code, but while waiting for the payment gateway the server handles hundreds of other checkouts. A chatbot streams tokens from an LLM with an async generator (a coroutine variant that yields many values).

## 🟡 Real Example Hindi mein
Swiggy का checkout handler `restaurant = await get_restaurant()`, `coupon = await validate_coupon()`, `payment = await charge()` करता है। यह सामान्य code जैसा पढ़ा जाता है, पर payment gateway का इंतज़ार करते समय server सैकड़ों दूसरे checkouts संभालता है। Chatbot LLM से tokens async generator (कई values yield करने वाली coroutine) से stream करता है।

---

## 💻 Code Example — Basic
```python
# Basic: coroutine functions and coroutine objects
import asyncio                                              # asyncio
import inspect                                              # to inspect coroutines


async def greet(name: str) -> str:                          # 'async def' makes a coroutine function
    return f"Hello {name}"                                  # returns normally when awaited


async def main() -> None:
    coro = greet("Asha")                                    # calling does NOT run it, returns an object
    print(type(coro).__name__)                              # coroutine
    print(inspect.iscoroutine(coro))                        # True
    print(await coro)                                       # await actually runs it
    print(inspect.iscoroutinefunction(greet))               # True for the function itself
    a = await greet("A")                                    # sequential: finish A first
    b = await greet("B")                                    # then B
    print(a, "|", b)                                        # both results


asyncio.run(main())                                         # entry point

# Output (verified on Python 3.13):
# coroutine
# True
# Hello Asha
# True
# Hello A | Hello B
```

## 💻 Code Example — Advanced
```python
# Production style: coroutine pipeline with timeout, retry, async generator and cleanup
import asyncio                                              # asyncio
from collections.abc import AsyncIterator                   # type for async generators

calls: dict[str, int] = {"n": 0}                            # counts attempts (demo)


async def flaky_fetch(url: str) -> str:                     # fails twice, then works
    calls["n"] += 1                                         # attempt counter
    await asyncio.sleep(0.01)                               # pretend network
    if calls["n"] < 3:                                      # first two attempts fail
        raise ConnectionError(f"{url} unavailable")         # transient error
    return f"data from {url}"                               # success


async def with_retry(url: str, attempts: int = 3, delay: float = 0.01) -> str:
    for i in range(1, attempts + 1):                        # try up to N times
        try:                                                # guard each attempt
            return await asyncio.wait_for(flaky_fetch(url), timeout=1)   # per-call timeout
        except ConnectionError as exc:                      # retry only transient errors
            print(f"attempt {i} failed: {exc}")             # log it
            if i == attempts:                               # out of attempts
                raise                                       # re-raise the last error
            await asyncio.sleep(delay * i)                  # simple backoff
    raise RuntimeError("unreachable")                       # keeps type checkers happy


async def stream_pages(n: int) -> AsyncIterator[int]:       # async generator: 'async def' + 'yield'
    try:                                                    # cleanup on early exit
        for page in range(1, n + 1):                        # n pages
            await asyncio.sleep(0)                          # yield to the loop
            yield page                                      # produce a value
    finally:
        print("stream closed")                              # runs even if consumer breaks


async def main() -> None:
    print(await with_retry("https://api.example.com"))      # retries then succeeds
    async for p in stream_pages(5):                         # consume lazily
        print("page", p)                                    # use it
        if p == 2:                                          # stop early
            break                                           # generator not finished yet
    await asyncio.sleep(0)                                  # let async generator finalize


if __name__ == "__main__":
    asyncio.run(main())

# Output (verified on 3.13):
# attempt 1 failed: https://api.example.com unavailable
# attempt 2 failed: https://api.example.com unavailable
# data from https://api.example.com
# page 1
# page 2
# stream closed
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Define | `async def f():` | `async function f() {}` |
| Calling `f()` | returns a coroutine object, NOT started | returns a Promise, ALREADY started |
| Run it | `await f()` / `create_task` / `asyncio.run` | `await f()` or `.then()` |
| Await twice | RuntimeError | fine, Promise caches the result |
| Generators | `async def` + `yield` = async generator | `async function*` |
| Concurrency | needs `create_task` / `gather` | `Promise.all` |

```python
# Python way — nothing runs until awaited
import asyncio                                           # stdlib

async def f() -> int:                                    # coroutine function
    print("running")                                     # side effect
    return 1                                             # value

async def main() -> None:
    c = f()                                              # nothing printed yet
    print("created")                                     # created
    print(await c)                                       # running, then 1

asyncio.run(main())
```
```javascript
// JavaScript way — the promise starts immediately
async function f() { console.log('running'); return 1; }
const p = f();                                           // prints "running" right now
console.log('created');                                  // created
p.then(console.log);                                     // 1
```

Key difference: a JS Promise is eager (starts at once), a Python coroutine is lazy (starts only when awaited or wrapped in a Task). So "create all, then gather" works in JS automatically, but in Python you must use `create_task` or `gather` for concurrency.

---

## 🟠 FastAPI Connection
Every `async def` route in FastAPI is a coroutine; FastAPI awaits it for you. Inside it you can `await` other coroutines, or run several concurrently with `asyncio.gather`. Dependencies can also be `async def` coroutines. Run with `TestClient` on 3.13:

```python
# FastAPI example — coroutines inside an endpoint
import asyncio                                            # gather
from fastapi import FastAPI, Depends                      # FastAPI


app: FastAPI = FastAPI()                                  # create app


async def get_user_id() -> int:                           # async dependency = coroutine too
    await asyncio.sleep(0.01)                             # pretend auth lookup
    return 7                                              # user id


async def fetch_profile(uid: int) -> dict[str, str]:      # coroutine helper
    await asyncio.sleep(0.01)                             # pretend DB
    return {"name": f"user{uid}"}                         # row


async def fetch_orders(uid: int) -> list[int]:            # coroutine helper
    await asyncio.sleep(0.01)                             # pretend DB
    return [101, 102]                                     # rows


@app.get("/me")                                           # GET /me
async def me(uid: int = Depends(get_user_id)) -> dict[str, object]:
    profile, orders = await asyncio.gather(fetch_profile(uid), fetch_orders(uid))   # concurrent
    return {"profile": profile, "orders": orders}         # one JSON reply
```
Expected reply: `{"profile": {"name": "user7"}, "orders": [101, 102]}`. (Pattern based on the same `gather` code that was run in topic 242; this exact endpoint was not run.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `await`
✅ Correct: always `await` a coroutine (or wrap it in a Task)

```python
# Wrong — x is a coroutine object; Python warns "coroutine 'f' was never awaited"
# x = f(); print(x == 1)            # False
# Right
# x = await f(); print(x == 1)      # True
```

❌ Mistake 2: Awaiting in a loop when you want concurrency
✅ Correct: use `gather` or `TaskGroup` so waits overlap

```python
# Wrong — 3 x 1 second = 3 seconds
# for url in urls: await fetch(url)
# Right — about 1 second total
# await asyncio.gather(*(fetch(u) for u in urls))
```

❌ Mistake 3: Awaiting the same coroutine object twice
✅ Correct: call the function again to get a fresh coroutine

```python
# Wrong — RuntimeError: cannot reuse already awaited coroutine
# c = f(); await c; await c
# Right
# await f(); await f()
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
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
Answer: `False coroutine`, `1`, `RuntimeError: cannot reuse already awaited coroutine` (verified on 3.13). `x` is a coroutine object, so `x == 1` is False. The first `await x` runs it and gives `1`. A coroutine is like a one-shot generator; after it finishes it cannot be awaited again (a Promise in JS can). The error message text can differ slightly between versions, but the exception type is the same.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a coroutine function and a coroutine object?
A1: `async def f` is the coroutine function. `f()` returns a coroutine object that holds the suspended state. The code only runs when the object is awaited or scheduled as a Task. `inspect.iscoroutinefunction` and `inspect.iscoroutine` test the two.

Q2: Are coroutines the same as threads?
A2: No. Coroutines are cooperative and run on one thread; they switch only at `await`. Threads are preempted by the OS and can switch anywhere. Coroutines are much cheaper (about 1-2 KB each, so 100,000 are fine) and avoid most race conditions, but one blocking call stops all of them.

Q3: How are coroutines related to generators?
A3: Historically coroutines were built from generators (`yield from`). Today `async def` / `await` is its own syntax, but the mechanism is similar: `send()` resumes, `await` suspends. An async generator (`async def` with `yield`) produces values one at a time and is consumed with `async for`.

Q4: What does `await` actually do?
A4: It takes an awaitable (coroutine, Task or Future), runs it, and suspends the current coroutine until it finishes, giving the result or raising its exception. Awaiting a coroutine directly does NOT create concurrency: it runs it to completion before moving on. For concurrency use tasks.

Q5: What is "coroutine was never awaited"?
A5: A `RuntimeWarning` when a coroutine object is garbage-collected without ever being started, usually because you forgot `await`. It is almost always a bug: the work silently did not happen.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code spends time waiting (HTTP, DB, queues, timers)
- You want sequential-looking code with high concurrency
- You need cancellation, timeouts and structured concurrency

❌ Avoid when:
- A function is pure CPU work; `async def` adds nothing
- The library only offers blocking calls and you cannot offload them
- You need real parallelism across cores; use processes

---

## 📊 Visual Diagram
```
 async def f():            call f()  ->  [coroutine object]  (not started)
     a = await g()
     b = await h()                |
     return a + b                 | await / Task / asyncio.run starts it
                                  v
   run -> hits `await g()` -> SUSPEND ----> loop runs other work
                                  ^                |
                                  +---- g ready ---+
   resume -> `await h()` -> SUSPEND ... resume -> return a + b

 states of a coroutine: created -> running -> suspended -> running -> finished
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coroutine function | Function defined with `async def` | `async def` से बना function |
| Coroutine object | What calling it returns, not started | Call करने पर मिलने वाला object, शुरू नहीं हुआ |
| Awaitable | Anything you can `await` | जिसे `await` कर सकें |
| Suspend / resume | Pause and continue the function | Function को रोकना और आगे चलाना |
| Async generator | `async def` that `yield`s values | Values yield करने वाला `async def` |
| Lazy | Does nothing until driven | जब तक चलाया न जाए कुछ नहीं करता |

---

## ⚡ 3-Line Summary
English: A coroutine is an `async def` function that can pause at `await` and resume later. Calling it only creates a lazy object; `await`, `asyncio.run` or a Task starts it, and it can be awaited just once. Awaiting in a loop is sequential, so use `gather` or tasks for concurrency.
Hindi: Coroutine एक `async def` function है जो `await` पर रुककर बाद में आगे चल सकता है। Call करने से सिर्फ lazy object बनता है; `await`, `asyncio.run` या Task उसे शुरू करते हैं, और उसे सिर्फ एक बार await कर सकते हैं। Loop में await करना क्रमवार है, इसलिए concurrency के लिए `gather` या tasks लें।

---

## ➡️ Next Topic
**241. Tasks in asyncio** — wrapping a coroutine in a Task so it starts running in the background, with cancellation, callbacks and TaskGroup.
