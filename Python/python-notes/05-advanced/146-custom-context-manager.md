---

# 146. Custom Context Manager
# हिंदी में: Custom Context Manager (अपना खुद का with-ready class)

---

## 🔵 Simple Definition (English)
A custom context manager is your own class (or function) that works with `with`. You write `__enter__` for setup and `__exit__` for cleanup. After that, any teammate can use your timer, lock, DB session or temporary setting safely with a single `with` line.

## 🔵 सरल परिभाषा (Hindi)
Custom context manager आपकी अपनी class (या function) है जो `with` के साथ चलती है। Setup के लिए `__enter__` और cleanup के लिए `__exit__` लिखते हैं। उसके बाद कोई भी साथी आपका timer, lock, DB session या अस्थायी setting सिर्फ एक `with` line से सुरक्षित रूप से इस्तेमाल कर सकता है।

---

## 🔴 Problem it Solves
Teams repeat the same pattern: start timer / do work / log duration, or begin transaction / do work / commit or rollback. Each copy risks a forgotten cleanup. A custom context manager writes the pattern once and makes it impossible to forget.

## 🔴 यह क्यों बना? (Hindi)
Teams वही pattern दोहराती हैं: timer शुरू / काम / duration log, या transaction शुरू / काम / commit या rollback। हर copy में cleanup भूलने का खतरा रहता है। Custom context manager pattern एक बार लिखता है और भूलना असंभव बना देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a class with __enter__(self) and __exit__(self, exc_type, exc, tb)
Step 2 → __init__ stores configuration (name, timeout, connection details)
Step 3 → __enter__ does setup and returns the object to bind to `as`
Step 4 → The with-block runs
Step 5 → __exit__ does cleanup; decides: return True (swallow) or False/None (re-raise)
Step 6 → For async code define __aenter__ and __aexit__ and use async with
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → __enter__(self) और __exit__(self, exc_type, exc, tb) वाली class बनाओ
Step 2 → __init__ configuration रखता है (name, timeout, connection details)
Step 3 → __enter__ setup करता है और `as` में बँधने वाला object लौटाता है
Step 4 → with-block चलता है
Step 5 → __exit__ cleanup करता है; तय करता है: True (दबाओ) या False/None (दोबारा raise)
Step 6 → async code के लिए __aenter__ और __aexit__ लिखो और async with इस्तेमाल करो
```

---

## 🟡 Real World Example
A Swiggy backend wraps API calls in `with Timer("menu_query"):` to log slow queries. A Razorpay service has `with idempotency_lock(order_id):` that stops double charging. A test suite uses `with temporary_env(DEBUG="1"):` to change an environment variable and always restore it. An AI app's `with token_budget(max_tokens=2000):` raises an error when a prompt goes over budget.

## 🟡 Real Example Hindi mein
Swiggy backend API calls को `with Timer("menu_query"):` में लपेटता है ताकि slow queries log हों। Razorpay service में `with idempotency_lock(order_id):` double charging रोकता है। Test suite `with temporary_env(DEBUG="1"):` से environment variable बदलती है और हमेशा वापस ठीक करती है। AI app का `with token_budget(max_tokens=2000):` prompt budget पार करने पर error देता है।

---

## 💻 Code Example — Basic
```python
# Custom context managers - every line commented
import time  # for timing
from types import TracebackType  # type for __exit__ argument
from typing import Optional  # optional types


class Timer:  # measures how long a block takes
    def __init__(self, name: str) -> None:  # store a label
        self.name: str = name  # label for printing
        self.elapsed: float = 0.0  # result seconds

    def __enter__(self) -> "Timer":  # setup
        self._start: float = time.perf_counter()  # start the clock
        return self  # allow `as t`

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],  # error class or None
        exc: Optional[BaseException],  # error object or None
        tb: Optional[TracebackType],  # traceback or None
    ) -> None:  # None means: do not swallow errors
        self.elapsed = time.perf_counter() - self._start  # compute duration
        status: str = "failed" if exc_type else "ok"  # did it error?
        print(f"{self.name}: {status}")  # report (no float to keep output stable)


with Timer("sum") as t:  # use it
    total: int = sum(range(100_000))  # some work
# Output: sum: ok
print(t.elapsed >= 0, total)  # elapsed is available after the block
# Output: True 4999950000

try:  # errors still pass through
    with Timer("boom"):  # use it
        1 / 0  # raises ZeroDivisionError
except ZeroDivisionError:  # arrives here after __exit__ ran
    print("caught outside")  # show
# Output:
# boom: failed
# caught outside


class Indent:  # prints with temporary indentation
    level: int = 0  # shared indentation level

    def __enter__(self) -> "Indent":  # increase indent
        Indent.level += 1  # one level deeper
        return self  # return self

    def __exit__(self, *args: object) -> None:  # restore indent
        Indent.level -= 1  # one level back

    @staticmethod
    def show(text: str) -> None:  # helper to print with current indent
        print("  " * Indent.level + text)  # indented text


Indent.show("root")  # level 0
with Indent():  # level 1
    Indent.show("child")  # indented once
    with Indent():  # level 2
        Indent.show("grandchild")  # indented twice
Indent.show("root again")  # back to level 0
# Output:
# root
#   child
#     grandchild
# root again
```

## 💻 Code Example — Advanced
```python
# Production style: DB-like session, error mapping, reentrant safety, async manager
import asyncio  # for async manager
import os  # environment variables
from types import TracebackType  # type for __exit__
from typing import Any, Optional  # type hints


class DBSession:  # unit of work with commit/rollback/close
    def __init__(self, log: list[str]) -> None:  # fake connection log
        self.log = log  # where we record actions
        self.open: bool = False  # connection state

    def __enter__(self) -> "DBSession":  # open connection
        self.open = True  # mark open
        self.log.append("open")  # record
        return self  # session object

    def execute(self, sql: str) -> None:  # run a statement
        if not self.open:  # guard against misuse
            raise RuntimeError("session closed")  # clear error
        self.log.append(f"sql: {sql}")  # record

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],  # error class
        exc: Optional[BaseException],  # error object
        tb: Optional[TracebackType],  # traceback
    ) -> bool:  # return value controls swallowing
        try:  # make cleanup itself safe
            self.log.append("rollback" if exc_type else "commit")  # decide
        finally:  # always close
            self.open = False  # release connection
            self.log.append("close")  # record
        return False  # never hide errors


log: list[str] = []  # shared log
with DBSession(log) as db:  # success path
    db.execute("INSERT 1")  # work
print(log)  # sequence
# Output: ['open', 'sql: INSERT 1', 'commit', 'close']

log.clear()  # reset
try:  # failure path
    with DBSession(log) as db:  # open
        db.execute("INSERT 2")  # work
        raise ValueError("bad data")  # simulated failure
except ValueError:  # still propagates
    pass  # ignore for demo
print(log)  # sequence
# Output: ['open', 'sql: INSERT 2', 'rollback', 'close']


class temporary_env:  # change env vars then restore the old values
    def __init__(self, **values: str) -> None:  # new values to set
        self.values: dict[str, str] = values  # remember them
        self.old: dict[str, Optional[str]] = {}  # previous values

    def __enter__(self) -> None:  # apply changes
        for key, new in self.values.items():  # each variable
            self.old[key] = os.environ.get(key)  # save old (or None)
            os.environ[key] = new  # set new

    def __exit__(self, *args: object) -> None:  # restore
        for key, old in self.old.items():  # each variable
            if old is None:  # it did not exist before
                os.environ.pop(key, None)  # remove it
            else:  # it existed
                os.environ[key] = old  # put it back


with temporary_env(APP_MODE="test"):  # temporary value
    print(os.environ["APP_MODE"])  # visible inside
# Output: test
print(os.environ.get("APP_MODE"))  # gone afterwards
# Output: None


class translate_errors:  # convert low-level errors to a domain error (swallow + raise)
    def __init__(self, domain: type[Exception]) -> None:  # target error class
        self.domain = domain  # store

    def __enter__(self) -> None:  # nothing to set up
        return None  # no value

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],  # error class
        exc: Optional[BaseException],  # error object
        tb: Optional[TracebackType],  # traceback
    ) -> bool:  # we raise a new error ourselves
        if exc_type is not None and issubclass(exc_type, KeyError):  # only KeyError
            raise self.domain(f"missing key {exc}") from exc  # chained error
        return False  # others pass through


class OrderNotFound(Exception):  # domain error
    pass  # no extra code


try:  # use it
    with translate_errors(OrderNotFound):  # wrap
        {"a": 1}["zzz"]  # raises KeyError
except OrderNotFound as err:  # domain error arrives
    print("OrderNotFound:", err)  # message
# Output: OrderNotFound: missing key 'zzz'


class AsyncLimiter:  # async context manager with a semaphore
    def __init__(self, limit: int) -> None:  # max concurrency
        self._sem = asyncio.Semaphore(limit)  # shared limiter
        self.peak: int = 0  # highest concurrent users seen
        self._now: int = 0  # users right now

    async def __aenter__(self) -> "AsyncLimiter":  # acquire slot
        await self._sem.acquire()  # wait if full
        self._now += 1  # count
        self.peak = max(self.peak, self._now)  # track peak
        return self  # return self

    async def __aexit__(self, *args: object) -> None:  # release slot
        self._now -= 1  # count down
        self._sem.release()  # free the slot


async def main() -> None:  # demo
    limiter = AsyncLimiter(2)  # at most 2 at once

    async def job(i: int) -> int:  # one task
        async with limiter:  # slot acquired here
            await asyncio.sleep(0.01)  # pretend I/O
            return i  # result

    print(await asyncio.gather(*(job(i) for i in range(5))), limiter.peak)  # run 5 tasks
# Output: [0, 1, 2, 3, 4] 2


asyncio.run(main())  # run the async demo
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has no built-in protocol until the new `using` / `Symbol.dispose` feature. Until then developers write helper functions that take a callback and run `try/finally`. A Python custom context manager is the same idea with cleaner syntax.

```python
# Python way
class Timer:
    def __enter__(self):
        print("start"); return self
    def __exit__(self, *a):
        print("stop")
with Timer():
    print("work")        # start / work / stop
```
```javascript
// JavaScript way (callback helper)
function withTimer(fn) {
  console.log("start");
  try { return fn(); }
  finally { console.log("stop"); }
}
withTimer(() => console.log("work"));   // start / work / stop
```

Key differences: JS wraps the block in a function/callback, so `return` and `break` inside it behave differently. Python's `with` keeps the block in the same scope, so `return`, `break` and `continue` work normally.

---

## 🟠 FastAPI Connection
Custom managers fit FastAPI in two ways: a request timer used inside endpoints or middleware, and database sessions injected with `Depends` where a manager creates the session. Mapping errors to `HTTPException` in one place keeps endpoints clean.

```python
# FastAPI: custom manager mapping domain errors to HTTP errors (pip install fastapi httpx)
from types import TracebackType  # type hint
from typing import Optional  # type hint
from fastapi import FastAPI, HTTPException  # core
from fastapi.testclient import TestClient  # test


class NotFound(Exception):  # domain error
    pass  # nothing else


class as_http_errors:  # context manager
    def __enter__(self) -> None:  # no setup
        return None  # nothing to bind

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],  # class
        exc: Optional[BaseException],  # object
        tb: Optional[TracebackType],  # traceback
    ) -> None:  # raise new error or pass through
        if exc_type is not None and issubclass(exc_type, NotFound):  # domain error
            raise HTTPException(status_code=404, detail=str(exc)) from exc  # to HTTP


app: FastAPI = FastAPI()  # app
USERS: dict[int, str] = {1: "Asha"}  # fake DB


def find_user(user_id: int) -> str:  # business logic
    if user_id not in USERS:  # missing
        raise NotFound(f"user {user_id} not found")  # domain error
    return USERS[user_id]  # found


@app.get("/users/{user_id}")  # route
def get_user(user_id: int) -> dict[str, str]:  # handler
    with as_http_errors():  # translate errors in one place
        return {"name": find_user(user_id)}  # return result


client = TestClient(app)  # client
print(client.get("/users/1").json())  # found
# Output: {'name': 'Asha'}
print(client.get("/users/9").status_code, client.get("/users/9").json())  # missing
# Output: 404 {'detail': 'user 9 not found'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Doing risky work in `__enter__` without cleanup on failure
```python
# Wrong - if the second step fails, __exit__ is NOT called (enter did not finish)
# def __enter__(self):
#     self.a = open_a()
#     self.b = open_b()      # raises -> a leaks

# Right - clean up inside __enter__ on failure, or use contextlib.ExitStack
```

❌ Mistake 2: Accidentally swallowing errors
```python
# Wrong - a truthy return value hides every error
# def __exit__(self, t, v, tb):
#     self.cleanup()
#     return "ok"                      # truthy -> exception swallowed!

# Right
# def __exit__(self, t, v, tb):
#     self.cleanup()
#     return False
```

❌ Mistake 3: Using one instance across threads or nested reuse
```python
# Wrong - shared state like self._start is overwritten when reused
# t = Timer("x"); using `with t:` in two threads at once overwrites t._start

# Right - create a new manager per use, or store state in a stack/local
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
class C:
    def __init__(self):
        print("init")
    def __enter__(self):
        print("enter")
        raise RuntimeError("fail")
    def __exit__(self, *a):
        print("exit")

try:
    with C():
        print("body")
except RuntimeError:
    print("caught")

class D:
    def __enter__(self): return 42
    def __exit__(self, *a): return False

with D() as x, D() as y:
    print(x + y)
```

**Answer**:
```
init
enter
caught
84
```
If `__enter__` itself raises, the block never starts and `__exit__` is NOT called. The `as` name gets whatever `__enter__` returns (`42`), not the manager object, so `x + y` is `84`.

---

## ⚫ Interview Questions + Answers

Q1: What must a class have to be a context manager?
A1: `__enter__(self)` and `__exit__(self, exc_type, exc, tb)`. For `async with` it needs `__aenter__` and `__aexit__`.

Q2: What does `as x` bind to?
A2: The return value of `__enter__`, which is often `self` but can be anything (a connection, a cursor, a path).

Q3: How do you re-raise a different error from `__exit__`?
A3: Raise the new exception inside `__exit__` (use `raise New(...) from exc` to keep the chain).

Q4: Is `__exit__` called if `__enter__` fails?
A4: No. Only if `__enter__` returned normally.

Q5: Class or `@contextmanager`?
A5: A class when you need reusable state, several methods or reentrancy control. `@contextmanager` for short setup/cleanup flows (next topic).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Setup and cleanup always come as a pair
- You want one reusable pattern across the codebase (timers, locks, sessions)
- You need to translate or log errors in a single place

❌ Avoid when:
- A plain function call with no cleanup is enough
- A generator-based `@contextmanager` is shorter
- The pattern is used only once

---

## 📊 Visual Diagram

```
 with Timer("x") as t:
     work()

 __init__("x") ─► __enter__ ─► (t = returned value)
                      │
                  work() runs
                      │
              ┌───────┴────────┐
         no error          error raised
              │                │
       __exit__(None,..)  __exit__(Type, exc, tb)
              │                │
            done        True → swallowed / False → re-raised
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__enter__` | Setup, returns the `as` value | setup, `as` की value लौटाता है |
| `__exit__` | Cleanup, decides about errors | cleanup, error पर फैसला |
| `__aenter__/__aexit__` | Async versions | async संस्करण |
| Reentrant | Safe to enter again while active | सक्रिय रहते दोबारा enter करना सुरक्षित |
| Unit of work | Group of DB actions as one | DB कामों का एक समूह |
| Exception chaining | `raise X from Y` | exception को जोड़कर raise करना |

---

## ⚡ 3-Line Summary
English: Build your own context manager with `__enter__` and `__exit__`. Put setup in `__enter__`, cleanup in `__exit__`, and return `False` unless you want to hide an error. Use `__aenter__`/`__aexit__` for `async with`.
Hindi: अपना context manager `__enter__` और `__exit__` से बनाइए। Setup `__enter__` में, cleanup `__exit__` में रखिए, और error दबाना न हो तो `False` लौटाइए। `async with` के लिए `__aenter__`/`__aexit__` लिखिए।

---

## ➡️ Next Topic
**147. contextlib Module** — `@contextmanager`, `suppress`, `ExitStack` and friends to write managers in fewer lines.
