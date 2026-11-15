---

# 254. Async Context Managers
# हिंदी में: Async Context Managers (`async with`)

---

## 🔵 Simple Definition (English)
An async context manager is an object you use with `async with`. It can `await` while setting up (`__aenter__`) and while cleaning up (`__aexit__`). It guarantees cleanup even when an error happens, for things like DB connections, HTTP sessions and locks.

## 🔵 सरल परिभाषा (Hindi)
Async context manager ऐसा object है जिसे `async with` के साथ इस्तेमाल करते हैं। यह setup (`__aenter__`) और cleanup (`__aexit__`) दोनों में `await` कर सकता है। Error आने पर भी cleanup पक्का होता है, जैसे DB connections, HTTP sessions और locks में।

---

## 🔴 Problem it Solves
Opening a connection or transaction needs network I/O, and closing it also needs network I/O (`await conn.close()`). A normal `with` cannot await, so you would write `try/finally` by hand everywhere, and forgetting `finally` leaks connections. `async with` makes setup and cleanup automatic and awaitable.

## 🔴 यह क्यों बना? (Hindi)
Connection या transaction खोलने में network I/O लगता है, और बंद करने में भी (`await conn.close()`)। सामान्य `with` await नहीं कर सकता, इसलिए हर जगह हाथ से `try/finally` लिखना पड़ता, और `finally` भूलने पर connections leak होते हैं। `async with` setup और cleanup को स्वचालित और awaitable बना देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python evaluates the expression after "async with" -> object
Step 2 → It calls await obj.__aenter__()  -> the value goes into "as name"
Step 3 → The body of the block runs
Step 4 → Body finished normally -> await obj.__aexit__(None, None, None)
Step 5 → Body raised an error  -> await obj.__aexit__(type, value, traceback)
Step 6 → If __aexit__ returns True the error is swallowed; False/None -> error continues
Step 7 → Shortcut: @asynccontextmanager turns an async generator into one
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python "async with" के बाद का expression चलाता है -> object
Step 2 → await obj.__aenter__() बुलाता है -> जो मिले वह "as name" में जाता है
Step 3 → Block की body चलती है
Step 4 → Body सामान्य रूप से खत्म -> await obj.__aexit__(None, None, None)
Step 5 → Body में error आई -> await obj.__aexit__(type, value, traceback)
Step 6 → __aexit__ True लौटाए तो error दब जाता है; False/None तो error आगे जाता है
Step 7 → Shortcut: @asynccontextmanager async generator को इसी में बदल देता है
```

---

## 🟡 Real World Example
A payment API opens a database transaction per request: `BEGIN`, debit wallet, create order, then `COMMIT`. If any step fails it must `ROLLBACK` and give the connection back. `async with db.transaction():` does this in one line. HTTP clients (`aiohttp.ClientSession`), Redis pools, file uploads to S3, and `asyncio.Lock` are all used the same way.

## 🟡 Real Example Hindi mein
Payment API हर request पर database transaction खोलती है: `BEGIN`, wallet debit, order बनाना, फिर `COMMIT`। कोई step फेल हो तो `ROLLBACK` और connection वापस देना जरूरी है। `async with db.transaction():` यह एक line में कर देता है। HTTP clients (`aiohttp.ClientSession`), Redis pools, S3 upload और `asyncio.Lock` सब इसी तरह इस्तेमाल होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic async context managers (verified on Python 3.13)
import asyncio                                           # event loop
from types import TracebackType                          # type of the traceback argument


class Conn:
    """Fake connection with async open/close."""

    async def __aenter__(self) -> "Conn":                # runs at "async with" start
        print("open")                                    # setup message
        await asyncio.sleep(0.01)                        # pretend to connect (awaiting is allowed!)
        return self                                      # becomes the "as" variable

    async def __aexit__(                                 # runs at the end, even on error
        self,
        et: type[BaseException] | None,                  # exception type or None
        ev: BaseException | None,                        # exception value or None
        tb: TracebackType | None,                        # traceback or None
    ) -> bool:
        print("close", et.__name__ if et else None)      # show what happened
        return False                                     # False = do not swallow the error

    async def q(self, s: str) -> str:                    # fake query
        return s.upper()                                 # return upper-case text


async def main() -> None:
    async with Conn() as c:                              # open, then run body
        print(await c.q("hi"))                           # use the connection
    try:
        async with Conn():                               # open again
            raise RuntimeError("x")                      # body fails
    except RuntimeError:                                 # error still reaches us
        print("caught")                                  # because __aexit__ returned False
    lock: asyncio.Lock = asyncio.Lock()                  # built-in async context manager
    async with lock:                                     # acquire (awaits if busy), release at end
        print(lock.locked())                             # True inside the block


asyncio.run(main())                                      # run

# Output:
# open
# HI
# close None
# open
# close RuntimeError
# caught
# True
```

## 💻 Code Example — Advanced
```python
# Production style: @asynccontextmanager with commit/rollback and cleanup
import asyncio                                           # event loop
from collections.abc import AsyncIterator                # return type of the generator
from contextlib import asynccontextmanager               # decorator helper


@asynccontextmanager                                     # turns the generator into a context manager
async def transaction(name: str) -> AsyncIterator[str]:
    print("BEGIN", name)                                 # setup: runs before the body
    try:
        yield name                                       # body of "async with" runs here
        print("COMMIT")                                  # body succeeded
    except Exception as e:                               # body raised
        print("ROLLBACK", e)                             # undo the work
        raise                                            # re-raise so the caller knows
    finally:
        print("release")                                 # ALWAYS runs: give resources back


async def main() -> None:
    async with transaction("t1") as t:                   # success path
        print("work", t)                                 # do work
    try:
        async with transaction("t2"):                    # failure path
            raise ValueError("bad")                      # simulate an error
    except ValueError:                                   # caller handles it
        print("caught2")                                 # after rollback + release
    async with asyncio.timeout(1):                       # Python 3.11+: timeout as a context manager
        print("timeout cm ok")                           # finishes well within 1 s


asyncio.run(main())                                      # run

# Output:
# BEGIN t1
# work t1
# COMMIT
# release
# BEGIN t2
# ROLLBACK bad
# release
# caught2
# timeout cm ok
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Sync cleanup | `with` | `try/finally` |
| Async cleanup | `async with` | `try { await ... } finally { await ... }` |
| Custom manager | `__aenter__/__aexit__` | none (manual) |
| Generator shortcut | `@asynccontextmanager` | none |
| Auto dispose | built in | `await using` (TC39 explicit resource management, new) |

```python
# Python way
async with pool.acquire() as conn:                       # open + auto close
    await conn.execute("SELECT 1")                       # use it
```
```javascript
// JavaScript way
const conn = await pool.connect();                        // open
try {
  await conn.query("SELECT 1");                           // use it
} finally {
  conn.release();                                         // you must remember this
}
```

Key difference: JavaScript has no built-in way to attach cleanup to a block (the new `await using` proposal is the equivalent but is still being adopted). In Python the cleanup is part of the object, so users cannot forget it.

---

## 🟠 FastAPI Connection
FastAPI uses async context managers in two places: the `lifespan` (startup/shutdown of the whole app) and dependencies with `yield`. Both are the same idea.

```python
# FastAPI example — lifespan + per-request resource
from contextlib import asynccontextmanager               # decorator
from collections.abc import AsyncIterator                # type
from fastapi import Depends, FastAPI                     # FastAPI


class Db:                                                # fake database handle
    async def close(self) -> None:                       # async close
        print("db closed")                               # log


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.db = Db()                                  # startup: create shared resources
    yield                                                # the app serves requests here
    await app.state.db.close()                           # shutdown: always runs on stop


app: FastAPI = FastAPI(lifespan=lifespan)                # attach lifespan


async def get_session() -> AsyncIterator[str]:           # dependency with yield == context manager
    print("session open")                                # before the endpoint
    try:
        yield "session"                                  # value injected into the endpoint
    finally:
        print("session closed")                          # after the response is sent


@app.get("/ping")                                        # endpoint
async def ping(s: str = Depends(get_session)) -> dict[str, str]:
    return {"s": s}                                      # use the session
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using plain `with` on an async manager
✅ Correct: use `async with` (inside an `async def`)

```python
# Wrong
with Conn():                    # TypeError: 'Conn' object does not support the context manager protocol
    ...
# Right
async with Conn():
    ...
```

❌ Mistake 2: `__aexit__` returning `True` by accident
✅ Correct: return `False`/`None` unless you really want to hide the error

```python
# Wrong — every exception inside the block disappears silently
async def __aexit__(self, et, ev, tb) -> bool:
    return True
# Right
async def __aexit__(self, et, ev, tb) -> bool:
    return False
```

❌ Mistake 3: Missing `try/finally` around `yield` in `@asynccontextmanager`
✅ Correct: wrap `yield` so cleanup runs when the body fails

```python
# Wrong — cleanup is skipped when the body raises
@asynccontextmanager
async def res():
    r = await open_res()
    yield r
    await r.close()
# Right
@asynccontextmanager
async def res():
    r = await open_res()
    try:
        yield r
    finally:
        await r.close()
```

---

## 🧠 Tricky Interview Question

```python
# What is printed?
import asyncio

class Quiet:
    async def __aenter__(self) -> "Quiet":
        return self
    async def __aexit__(self, et, ev, tb) -> bool:
        print("exit sees", et.__name__ if et else None)
        return True

async def main() -> None:
    async with Quiet():
        raise ValueError("lost?")
        print("never")
    print("after")

asyncio.run(main())
```
Answer: `exit sees ValueError` then `after`. The ValueError reaches `__aexit__`, which returns `True`, so Python suppresses it. The code after the `raise` inside the block (`print("never")`) is skipped, but execution continues after the `async with` block. No traceback is shown at all. This is why a context manager that returns `True` can hide real bugs.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `with` and `async with`?
A1: `with` calls `__enter__` / `__exit__` (synchronous). `async with` calls `await __aenter__()` and `await __aexit__()`, so setup and cleanup can do network I/O without blocking.

Q2: What are the arguments of `__aexit__`?
A2: `(exc_type, exc_value, traceback)`; all `None` when no exception. Return a truthy value to suppress the exception.

Q3: How do you create one quickly?
A3: Use `@contextlib.asynccontextmanager` on an async generator function: code before `yield` is setup, after `yield` is cleanup, and wrap `yield` in `try/finally`.

Q4: Can I combine several in one statement?
A4: Yes: `async with a() as x, b() as y:` (parentheses allowed in 3.10+). For a dynamic number use `contextlib.AsyncExitStack`.

Q5: Name built-in async context managers.
A5: `asyncio.Lock`, `asyncio.Semaphore`, `asyncio.timeout()` (3.11+), `asyncio.TaskGroup` (3.11+), `aiohttp.ClientSession`, `asyncpg` `pool.acquire()` and `conn.transaction()`, and `httpx.AsyncClient`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A resource needs awaited setup/cleanup (connections, sessions, transactions)
- You must guarantee release even on errors
- Locks, semaphores, timeouts and task groups

❌ Avoid when:
- Setup/cleanup is purely synchronous (plain `with` is enough)
- You need to keep a resource for the entire app lifetime (use `lifespan`)
- You would swallow exceptions without logging them

---

## 📊 Visual Diagram
```
async with transaction("t1") as t:     <- 1. await __aenter__()   (BEGIN)
    body ...                           <- 2. your code runs
                                       <- 3a. no error:  await __aexit__(None, None, None)  (COMMIT)
                                       <- 3b. error:     await __aexit__(type, val, tb)     (ROLLBACK)
                                       <- 4. __aexit__ returns True -> error hidden
                                                         False      -> error continues

@asynccontextmanager generator:
   async def f():
       setup()          # __aenter__
       try: yield x     # body runs here
       finally: cleanup()   # __aexit__
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__aenter__` | Async setup method | Async setup method |
| `__aexit__` | Async cleanup method | Async cleanup method |
| asynccontextmanager | Decorator to build one from a generator | Generator से बनाने वाला decorator |
| Suppress | Hide an exception | Exception को दबा देना |
| lifespan | App-wide startup/shutdown manager | पूरे app का startup/shutdown |
| AsyncExitStack | Manage a dynamic list of them | कई managers को एक साथ संभालना |

---

## ⚡ 3-Line Summary
English: `async with` runs awaited setup and cleanup around a block and guarantees cleanup even on errors. Build one with `__aenter__`/`__aexit__` or `@asynccontextmanager`, and always wrap `yield` in `try/finally`.
Hindi: `async with` block के आसपास awaitable setup और cleanup चलाता है और error पर भी cleanup पक्का करता है। इसे `__aenter__`/`__aexit__` या `@asynccontextmanager` से बनाएं, और `yield` को हमेशा `try/finally` में रखें।

---

## ➡️ Next Topic
**255. Async Generators** — `async def` functions with `yield`, for streaming data piece by piece.
