---

# 477. Implement Context Manager
# हिंदी में: Context Manager बनाना (with statement)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
A context manager is an object that does setup when you enter a `with` block and cleanup when you leave it, even if an error happens. You build one with `__enter__`/`__exit__` or with `@contextmanager`.

## 🔵 सरल परिभाषा (Hindi)
Context manager ऐसा object है जो `with` block में घुसते समय setup और निकलते समय cleanup करता है, error आने पर भी। इसे `__enter__`/`__exit__` से या `@contextmanager` से बनाया जाता है।

---

## 🔴 Problem it Solves
Resources (files, DB connections, locks, transactions) must be released. Writing `try/finally` everywhere is verbose and easy to forget, which causes leaks and deadlocks. `with` guarantees cleanup in one readable line.

## 🔴 यह क्यों बना? (Hindi)
Resources (files, DB connections, locks, transactions) को छोड़ना ज़रूरी है। हर जगह `try/finally` लिखना लंबा है और भूलना आसान, जिससे leak और deadlock होते हैं। `with` एक साफ़ लाइन में cleanup की गारंटी देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `with Manager() as x:` calls Manager().__enter__()
Step 2 → Whatever __enter__ returns is bound to x
Step 3 → The body runs
Step 4 → On exit (normal or exception) Python calls __exit__(exc_type, exc, tb)
Step 5 → If __exit__ returns True the exception is swallowed; False/None -> it propagates
Step 6 → @contextmanager: code before `yield` = enter, the yielded value = x,
         code after yield (in finally) = exit
Step 7 → async version: __aenter__/__aexit__ or @asynccontextmanager with `async with`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `with Manager() as x:` Manager().__enter__() बुलाता है
Step 2 → __enter__ जो लौटाए वह x में आ जाता है
Step 3 → Body चलती है
Step 4 → बाहर निकलते समय (सामान्य या exception) Python __exit__(exc_type, exc, tb) बुलाता है
Step 5 → __exit__ True लौटाए तो exception दब जाती है; False/None हो तो आगे बढ़ती है
Step 6 → @contextmanager: `yield` से पहले का code = enter, yield की value = x,
         yield के बाद का code (finally में) = exit
Step 7 → async version: __aenter__/__aexit__ या @asynccontextmanager के साथ `async with`
```

---

## 🟡 Real World Example
A DB transaction: `BEGIN`, run queries, `COMMIT` on success or `ROLLBACK` on error, always close the connection. Other cases: `open()` files, `threading.Lock`, temporary directories, `httpx.Client`, SQLAlchemy `Session`, a timer that logs how long a Swiggy order-assign step took, mocking in tests (`unittest.mock.patch`).

## 🟡 Real Example Hindi mein
DB transaction: `BEGIN`, queries चलाओ, सफल हो तो `COMMIT` वरना `ROLLBACK`, और connection हमेशा बंद करो। अन्य उदाहरण: `open()` files, `threading.Lock`, temporary directories, `httpx.Client`, SQLAlchemy `Session`, Swiggy के order-assign step की अवधि log करने वाला timer, tests में mocking (`unittest.mock.patch`)।

---

## 💻 Code Example — Basic
```python
# Basic: class-based and generator-based context managers
import time                                    # for timing
from contextlib import contextmanager          # decorator form
from typing import Iterator                    # return type of the generator

class Timer:
    def __enter__(self) -> "Timer":
        self.start: float = time.perf_counter()    # setup: note the start time
        return self                            # value bound by `as`

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.elapsed: float = time.perf_counter() - self.start   # cleanup: compute duration
        return False                           # False -> never swallow exceptions

with Timer() as t:                             # enter
    total: int = sum(range(1000))              # the body
print(total, t.elapsed >= 0)                   # exit already ran

@contextmanager
def announce(name: str) -> Iterator[str]:
    print(f"enter {name}")                     # runs on enter
    try:
        yield name                             # value for `as`
    finally:
        print(f"exit {name}")                  # always runs on exit

with announce("db") as n:                      # use it
    print("inside", n)                         # body

# Output:
# 499500 True
# enter db
# inside db
# exit db
```

## 💻 Code Example — Advanced
```python
# Production style: transaction with rollback + async session (more tests in main.py)
import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator, Iterator


@contextmanager
def transaction(log: list[str]) -> Iterator[list[str]]:
    log.append("BEGIN")                        # setup
    try:
        yield log                              # run the body
        log.append("COMMIT")                   # body succeeded
    except Exception:
        log.append("ROLLBACK")                 # body failed
        raise                                  # never hide the error from the caller
    finally:
        log.append("CLOSE")                    # always release the connection


@asynccontextmanager
async def db_session(log: list[str]) -> AsyncIterator[str]:
    log.append("open")                         # acquire
    try:
        yield "session"                        # hand out the session
    finally:
        log.append("close")                    # always release


ok: list[str] = []
with transaction(ok):                          # success path
    pass
print(ok)

bad: list[str] = []
try:
    with transaction(bad):                     # failure path
        raise RuntimeError("insert failed")
except RuntimeError as e:
    print(bad, "|", e)                         # rollback happened, error still visible


async def main() -> list[str]:
    log: list[str] = []
    async with db_session(log) as s:           # async with for async resources
        log.append(f"using {s}")
    return log

print(asyncio.run(main()))

# Output:
# ['BEGIN', 'COMMIT', 'CLOSE']
# ['BEGIN', 'ROLLBACK', 'CLOSE'] | insert failed
# ['open', 'using session', 'close']
```

---

## 🟠 JavaScript vs Python Comparison
JS has `try/finally`, and newer JS/TS has `using` declarations (explicit resource management, `Symbol.dispose`) but it is not yet universal. Python's `with` has been standard for years.

```python
# Python way
with open("a.txt") as f:      # closed automatically
    data = f.read()
```
```javascript
// JavaScript way
const f = await fs.promises.open("a.txt");
try {
  const data = await f.readFile("utf8");
} finally {
  await f.close();            // you must remember this
}
```

---

## 🟠 FastAPI Connection
FastAPI dependencies with `yield` ARE context managers: code before `yield` runs at request start, code after runs after the response (cleanup). The app `lifespan` is an `@asynccontextmanager` too.

```python
from contextlib import asynccontextmanager
from typing import Annotated, Iterator
from fastapi import Depends, FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = "pool-opened"             # startup: create connection pool
    yield                                      # app serves requests here
    app.state.pool = None                      # shutdown: close pool

app = FastAPI(lifespan=lifespan)

def get_session() -> Iterator[dict]:           # dependency using yield
    session = {"open": True}                   # setup per request
    try:
        yield session                          # injected into the route
    finally:
        session["open"] = False                # cleanup after the response

@app.get("/ping")
def ping(s: Annotated[dict, Depends(get_session)]) -> dict:
    return {"session_open": s["open"]}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `@contextmanager` generator without `try/finally`, so cleanup is skipped when the body raises.
✅ Correct: wrap `yield` in `try/finally`.

```python
# Wrong
@contextmanager
def res():
    open_it(); yield; close_it()      # close_it skipped on error
# Right
@contextmanager
def res():
    open_it()
    try: yield
    finally: close_it()
```

❌ Mistake 2: `__exit__` returning `True` by accident (e.g. `return self.close()` truthy), swallowing every error.
✅ Correct: return `False`/`None` unless you deliberately suppress.

❌ Mistake 3: using plain `with` for async resources (`async with` is required), or yielding twice in `@contextmanager`.
✅ Correct: `async with` + `@asynccontextmanager`; yield exactly once.

---

## 🧠 Tricky Interview Question
```python
class A:
    def __enter__(self): print("enter"); return self
    def __exit__(self, *exc): print("exit"); return True

with A():
    print("body")
    raise ValueError("boom")
print("after")
```
Answer: `enter`, `body`, `exit`, `after`. `__exit__` returned `True`, so the ValueError is silently swallowed and execution continues after the block. This is how `contextlib.suppress` works, and why returning `True` carelessly hides bugs.

---

## ⚫ Interview Questions + Answers

Q1: What happens if `__enter__` raises?
A1: `__exit__` is NOT called (the with block never started). Only after a successful `__enter__` is `__exit__` guaranteed.

Q2: What are the three arguments of `__exit__`?
A2: Exception type, value, traceback; all `None` if no exception occurred.

Q3: `with a, b:` order?
A3: Enter a then b; exit b then a (LIFO). Use `contextlib.ExitStack` when the number of managers is dynamic.

Q4: Class-based vs `@contextmanager`?
A4: `@contextmanager` is shorter for simple cases. Class-based is better when you need reusable state, reentrancy or a specific `__exit__` return behavior.

Q5: How does `with` relate to `try/finally`?
A5: `with` is roughly try/except/finally in one construct: enter, body, and `__exit__` as the finally block that also receives the exception info.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything must be released: files, locks, sockets, sessions, temp dirs
- Paired actions: begin/commit, start/stop, patch/unpatch
- Temporarily changing global state (env vars, cwd, decimal precision)

❌ Avoid when:
- Lifetime exceeds one block (long-lived objects: manage with app lifespan or explicit close)
- A simple function call without cleanup would do
- You would hide errors by suppressing them

---

## 📊 Visual Diagram
```
  with Manager() as x:
        |
        v
   __enter__()  ---- returns x
        |
        v
   [ body runs ] ---- exception? ----+
        |                            |
        v                            v
   __exit__(None,None,None)    __exit__(type, exc, tb)
        |                            |
        v                      returns True?  -> swallowed, continue
   continue                    returns False? -> re-raised
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context manager | Object usable in `with` | `with` में चलने वाला object |
| `__enter__` | Setup, returns the `as` value | शुरुआत का setup |
| `__exit__` | Cleanup, may suppress errors | अंत का cleanup |
| `@contextmanager` | Generator-to-context-manager decorator | generator से बनाना |
| ExitStack | Dynamic group of managers | कई managers का समूह |
| Suppress | Swallow selected exceptions | चुने हुए errors दबाना |

---

## ⚡ 3-Line Summary
English: `with` guarantees setup and cleanup, even when an error occurs.
English: Build one with `__enter__/__exit__` or `@contextmanager` (use try/finally around the yield).
English: Returning True from `__exit__` swallows exceptions, so do it only deliberately.

Hindi: `with` error आने पर भी setup और cleanup की गारंटी देता है।
Hindi: `__enter__/__exit__` या `@contextmanager` से बनाओ (yield के आसपास try/finally लगाओ)।
Hindi: `__exit__` से True लौटाने पर exceptions दब जाती हैं, इसलिए जानबूझकर ही करो।

---

## ➡️ Next Topic
**478. Implement Iterator** — the protocol behind `for` loops that powers generators and lazy data.

---
