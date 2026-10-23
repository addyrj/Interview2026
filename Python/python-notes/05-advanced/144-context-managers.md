---

# 144. Context Managers — Complete Guide
# हिंदी में: Context Managers — पूरी Guide

---

## 🔵 Simple Definition (English)
A context manager is an object that defines setup and teardown behavior for a `with` block. When you write `with open("file.txt") as f:`, Python calls `f.__enter__()` to set up (opens the file) and `f.__exit__()` to tear down (closes the file) — even if an exception is raised. Context managers guarantee cleanup code always runs.

## 🔵 सरल परिभाषा (Hindi)
Context manager एक object है जो `with` block के लिए setup और teardown define करता है। `with open("file.txt") as f:` लिखने पर Python `f.__enter__()` (file open) और `f.__exit__()` (file close) automatically call करता है — exception आए तो भी। Context managers guarantee करते हैं कि cleanup हमेशा होगी।

---

## 🔴 Problem it Solves
Without context managers: you must manually close files, release locks, commit/rollback transactions — and if an exception is raised, the cleanup code never runs (resource leak). Traditional `try/finally` is verbose. Context managers encapsulate the pattern once, reuse everywhere.

## 🔴 यह क्यों बना? (Hindi)
Context managers के बिना: files manually close करो, locks release करो, transactions commit/rollback करो — exception आने पर cleanup नहीं होती (resource leak)। `try/finally` verbose है। Context managers pattern एक बार define करो, हर जगह reuse करो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python evaluates the expression after 'with'
Step 2 → Calls __enter__() → return value assigned to 'as' variable (if any)
Step 3 → Executes the 'with' block body
Step 4 → On exit (normal or exception) → calls __exit__(exc_type, exc_val, exc_tb)
Step 5 → If __exit__ returns True → exception is suppressed (swallowed)
Step 6 → If __exit__ returns False/None → exception propagates normally
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python 'with' के बाद expression evaluate करता है
Step 2 → __enter__() call → return value 'as' variable को assign
Step 3 → 'with' block body execute
Step 4 → Exit पर (normal या exception) → __exit__(exc_type, exc_val, exc_tb) call
Step 5 → __exit__ True return → exception suppress (निगल जाता है)
Step 6 → False/None return → exception propagate होती है
```

---

## 🟡 Real World Example
Database transaction at Flipkart: open a transaction before order processing, commit if everything succeeds, rollback if any step fails (item unavailable, payment error). Context manager handles this automatically — engineer writes business logic only, not try/finally/rollback everywhere.

## 🟡 Real Example Hindi mein
Flipkart order processing: order से पहले transaction open, सब ठीक रहा तो commit, कोई step fail हुआ तो rollback। Context manager automatically handle करता है — engineer सिर्फ business logic लिखता है।

---

## 💻 Code Example — Basic
```python
# Method 1: class-based context manager
class Timer:
    """Measures execution time of a code block."""
    import time

    def __enter__(self):
        """Called on 'with' block entry. Return value → 'as' variable."""
        self._start = time.perf_counter()
        return self                          # 'with Timer() as t:' → t = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called on 'with' block exit — always, even on exception."""
        self.elapsed = time.perf_counter() - self._start
        print(f"Elapsed: {self.elapsed:.4f}s")
        return False    # False = don't suppress exceptions

import time

with Timer() as t:
    time.sleep(0.1)
    x = sum(range(1_000_000))
# Prints: Elapsed: 0.1234s

print(f"Timer recorded: {t.elapsed:.4f}s")   # accessible after block!

# Method 2: suppress exceptions
class SuppressError:
    """Silently swallow specific exceptions."""
    def __init__(self, *exception_types):
        self.exception_types = exception_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Return True only for exceptions we want to suppress:
        return exc_type is not None and issubclass(exc_type, self.exception_types)

with SuppressError(FileNotFoundError, PermissionError):
    open("/nonexistent/file.txt")      # FileNotFoundError → suppressed!
print("Code continues here normally")  # this runs
```

## 💻 Code Example — Advanced
```python
# Method 3: contextlib.contextmanager — simplest approach!
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
import time

@contextmanager
def timer(label: str = "") -> Generator[dict, None, None]:
    """context manager via generator — code before yield = __enter__, after = __exit__."""
    stats: dict = {}
    start = time.perf_counter()
    try:
        yield stats                    # value passed to 'as' variable
        stats["success"] = True
    except Exception as e:
        stats["success"] = False
        stats["error"] = str(e)
        raise                          # re-raise — __exit__ doesn't suppress
    finally:
        stats["elapsed"] = time.perf_counter() - start  # ALWAYS runs

with timer("DB query") as stats:
    time.sleep(0.05)
    result = list(range(1000))

print(stats)   # {'success': True, 'elapsed': 0.050...}

# Production: DB transaction context manager
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def db_transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Async context manager: commit on success, rollback on exception."""
    async with session.begin():         # SQLAlchemy's own context manager
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()

# Usage in service layer:
async def transfer_funds(from_id: int, to_id: int, amount: float, db: AsyncSession):
    async with db_transaction(db) as session:
        sender   = await session.get(Account, from_id)
        receiver = await session.get(Account, to_id)
        if sender.balance < amount:
            raise ValueError("Insufficient funds")   # triggers rollback
        sender.balance   -= amount
        receiver.balance += amount
        # rollback happens if ANY exception, commit if we reach the end

# Stacking context managers:
from contextlib import ExitStack

def process_multiple_files(file_paths: list[str]) -> list[str]:
    """Open variable number of files — close all even if one fails."""
    with ExitStack() as stack:
        files = [stack.enter_context(open(path)) for path in file_paths]
        return [f.read() for f in files]
    # All files closed here, even if reading one fails

# contextlib helpers:
from contextlib import suppress, nullcontext

# suppress: clean one-liner for ignoring specific exceptions
with suppress(FileNotFoundError):
    import os
    os.remove("/tmp/temp.txt")         # ignored if file doesn't exist

# nullcontext: useful for optional context managers
def process(data, lock=None):
    ctx = lock if lock is not None else nullcontext()
    with ctx:                          # works whether lock is None or a real Lock
        return data.upper()
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: using __enter__/__exit__ + @contextmanager
from contextlib import contextmanager

@contextmanager
def managed_resource():
    print("Setup")
    resource = {"data": 42}
    try:
        yield resource
    finally:
        print("Teardown")   # always runs

with managed_resource() as r:
    print(r["data"])        # Setup → 42 → Teardown

# Exception handling:
with managed_resource() as r:
    raise ValueError("oops")   # Teardown still runs! Then exception propagates
```

```javascript
// JavaScript: no 'with' statement for resource management
// (JS 'with' is for scope extension — very different, deprecated)

// Closest equivalent: try/finally
function withResource(fn) {
    const resource = { data: 42 };
    console.log("Setup");
    try {
        return fn(resource);
    } finally {
        console.log("Teardown");   // always runs
    }
}

withResource(resource => {
    console.log(resource.data);   // Setup → 42 → Teardown
});

// No async context manager equivalent (Symbol.asyncDispose / 'using' keyword in TC39 Stage 3)
// Currently use try/finally or libraries
```

---

## 🟠 FastAPI Connection

```python
# FastAPI lifespan — async context manager for app startup/shutdown
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncpg
import redis.asyncio as aioredis

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic for the entire app."""
    # STARTUP (before 'yield'):
    print("Starting up...")
    app.state.db_pool = await asyncpg.create_pool(
        "postgresql://localhost/mydb",
        min_size=5, max_size=20
    )
    app.state.redis = await aioredis.from_url("redis://localhost")

    yield    # application runs

    # SHUTDOWN (after 'yield'):
    print("Shutting down...")
    await app.state.db_pool.close()
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)

# Route-level context manager for per-request resources:
@app.post("/orders")
async def create_order(order: dict, request: Request):
    async with db_transaction(request.app.state.db_pool) as conn:
        # conn is auto-committed/rolled-back by the context manager
        result = await conn.fetchrow(
            "INSERT INTO orders (...) VALUES (...) RETURNING id", ...
        )
        return {"order_id": result["id"]}

# Test override using nullcontext:
from contextlib import nullcontext

async def test_create_order():
    # Override DB with a fake that doesn't need transaction management:
    fake_conn = FakeConnection()
    with patch("myapp.db_transaction", return_value=nullcontext(fake_conn)):
        response = client.post("/orders", json={...})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning `True` from `__exit__` accidentally (suppresses all exceptions)
```python
# Wrong — swallows ALL exceptions!
def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup()
    return True       # any exception inside 'with' block is silently ignored!

# Correct — return True only for specific exceptions you WANT to suppress:
def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup()
    return exc_type is not None and issubclass(exc_type, (TimeoutError,))
    # or just: return False  (or None) to always propagate
```

❌ Mistake 2: Forgetting to yield exactly once in `@contextmanager`
```python
# Wrong — no yield: __enter__ never returns, or wrong with multiple yields:
@contextmanager
def bad():
    setup()
    # forgot yield! → GeneratorExit, confusing errors

# Also wrong — two yields:
@contextmanager
def also_bad():
    setup()
    yield value1
    yield value2    # RuntimeError: generator didn't stop after first yield

# Correct — exactly ONE yield:
@contextmanager
def good():
    setup()
    try:
        yield resource
    finally:
        cleanup()
```

---

## 🧠 Tricky Interview Question

```python
from contextlib import contextmanager

@contextmanager
def managed():
    print("enter")
    try:
        yield
    except ValueError:
        print("caught ValueError")
        # No re-raise!

with managed():
    print("inside")
    raise ValueError("oops")

print("after with")
```
Answer:
```
enter
inside
caught ValueError
after with        ← prints! Exception was suppressed
```
The `@contextmanager` function caught the `ValueError` and didn't re-raise it — equivalent to `__exit__` returning `True`. Code after the `with` block continues normally. This is a subtle difference from the class-based approach where you must explicitly `return True` to suppress.

---

## ⚫ Interview Questions + Answers

Q1: What are the three parameters passed to `__exit__`?
A1: `(exc_type, exc_val, exc_tb)` — the exception class, the exception instance, and the traceback object. If no exception occurred, all three are `None`. You can inspect `exc_type` to decide whether to suppress, log, or transform the exception. `return True` suppresses; `return False` or `return None` propagates.

Q2: What is the difference between `@contextmanager` and the class-based approach?
A2: Both are equivalent. `@contextmanager` is simpler: code before `yield` = `__enter__`, code after `yield` = `__exit__`. Class-based is better when the context manager has complex state, multiple methods, or needs to be subclassed. `@contextmanager` can't suppress exceptions by not re-raising them in the `except` block (silently consuming the exception); a class `__exit__` returns `True` to suppress explicitly.

Q3: What is `ExitStack` and when would you use it?
A3: `contextlib.ExitStack` is a context manager that manages a dynamic stack of context managers. Use it when: (1) you don't know at write time how many context managers you'll need, (2) you want to conditionally add context managers, (3) you want to register cleanup callbacks. `stack.enter_context(cm)` calls `cm.__enter__()` and registers `cm.__exit__()` for cleanup.

Q4: What is the difference between `contextmanager` and `asynccontextmanager`?
A4: `@contextmanager` uses a regular generator (`yield`), works with synchronous `with` statements. `@asynccontextmanager` uses an async generator (`async def` + `yield`), works with `async with` statements. Async context managers call `__aenter__` and `__aexit__` (note the `a`). Use async for I/O-bound resources: DB connections, HTTP sessions, Redis.

Q5: How does FastAPI's `lifespan` work?
A5: FastAPI 0.93+ accepts a `lifespan` async context manager function. Code before `yield` runs at startup (after `app = FastAPI(lifespan=...)` and before the first request). `yield` marks the running state. Code after `yield` runs at shutdown. This replaced the older `@app.on_event("startup")` / `@app.on_event("shutdown")` decorators and is the recommended approach.

---

## 🔷 When to Use + When Not to Use

✅ Use context managers when:
- Managing resources that need deterministic cleanup (files, DB connections, locks, sockets)
- DB transactions (commit/rollback)
- Temporary state changes (change directory, modify environment variables, mock patches)
- Performance measurement (timer)
- Suppressing specific exceptions cleanly

❌ Avoid when:
- Simple function calls with no setup/teardown
- When `try/finally` is only 2 lines and not reused
- When the "resource" is just a value with no cleanup needed

---

## 📊 Visual Diagram
```
with Timer() as t:
    <body>

│
▼
Timer().__enter__() ─────────────────┐
     │                               │
     │ returns self                  │
     ▼                               │
   t = self          body runs       │
     │                               │
     ▼                               │
   body raises? ──Yes──► __exit__(exc_type, exc_val, exc_tb)
     │ No                            │
     ▼                               │  return True? → suppress exception
   __exit__(None, None, None) ◄──────┘  return False? → propagate exception
     │
     ▼ cleanup always runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context manager | Object with __enter__/__exit__ | `with` block manage करने वाला object |
| __enter__ | Called on 'with' block entry | Block entry पर call होता है |
| __exit__ | Called on 'with' block exit | Block exit पर call होता है |
| @contextmanager | Decorator to create CM from generator | Generator से CM बनाने का decorator |
| ExitStack | Dynamic stack of context managers | Variable number CMs के लिए |
| asynccontextmanager | Async version of @contextmanager | Async resources के लिए |
| suppress | contextlib CM that swallows exceptions | Exceptions ignore करने वाला CM |

---

## ⚡ 3-Line Summary
English: A context manager guarantees that `__exit__` runs after a `with` block — even if an exception occurs. The easiest way to write one: `@contextmanager` with a single `yield` (code before = setup, code after = cleanup). Return `True` from `__exit__` to suppress an exception; `False`/`None` to propagate it.
Hindi: Context manager guarantee करता है कि `__exit__` हमेशा run होगी — exception आए तो भी। सबसे easy way: `@contextmanager` + एक `yield`। Exception suppress करनी हो तो `True` return करो।

---

## ➡️ Next Topic
**145. `__enter__` and `__exit__` Deep Dive** — exception suppression patterns, then **146. `contextlib` module** — `suppress`, `redirect_stdout`, `AbstractContextManager`.
