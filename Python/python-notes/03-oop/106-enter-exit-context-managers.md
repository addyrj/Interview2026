---

# 106. __enter__ __exit__ (Context Managers)
# हिंदी में: Context Managers (`with` statement से सुरक्षित setup और cleanup)

---

## 🔵 Simple Definition (English)
A context manager is an object that runs setup code when you enter a `with` block (`__enter__`) and cleanup code when you leave it (`__exit__`), even if an error happens. It guarantees that files get closed, locks released and transactions finished.

## 🔵 सरल परिभाषा (Hindi)
Context manager ऐसा object है जो `with` block में घुसते समय setup code (`__enter__`) और निकलते समय cleanup code (`__exit__`) चलाता है, error आने पर भी। यह गारंटी देता है कि files बंद हों, locks छूटें और transactions पूरी हों।

---

## 🔴 Problem it Solves
Manual cleanup is easy to forget or skip: `f = open(...); process(f); f.close()` leaks the file if `process` raises an error. `try/finally` fixes it but is repeated everywhere. A context manager packs "setup + cleanup" into one reusable unit, so `with open(...) as f:` is always safe. The same pattern protects DB sessions, locks, temporary directories, timers and HTTP clients.

## 🔴 यह क्यों बना? (Hindi)
Manual cleanup भूलना या छूट जाना आसान है: `f = open(...); process(f); f.close()` में `process` error दे तो file leak हो जाती है। `try/finally` इसे ठीक करता है पर हर जगह दोहराना पड़ता है। Context manager "setup + cleanup" को एक reusable इकाई बना देता है, इसलिए `with open(...) as f:` हमेशा सुरक्षित है। यही pattern DB sessions, locks, temporary directories, timers और HTTP clients की रक्षा करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → with Manager() as x:   Python evaluates Manager() and keeps the object
Step 2 → It calls obj.__enter__();  the return value is bound to `x`
Step 3 → The body of the with block runs
Step 4 → Block ends (normally OR by exception/return/break) -> obj.__exit__(exc_type, exc, tb)
Step 5 → On success all three arguments are None
Step 6 → If __exit__ returns True, the exception is swallowed; False/None -> it propagates
Shortcut → @contextlib.contextmanager: a generator with one `yield` replaces both methods
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → with Manager() as x:   Python Manager() बनाकर object रखता है
Step 2 → वह obj.__enter__() call करता है;  return value `x` में जाती है
Step 3 → with block का body चलता है
Step 4 → Block खत्म होने पर (सामान्य रूप से या exception/return/break से) -> obj.__exit__(exc_type, exc, tb)
Step 5 → सफलता पर तीनों arguments None होते हैं
Step 6 → __exit__ अगर True लौटाए तो exception दब जाता है; False/None पर आगे जाता है
Shortcut → @contextlib.contextmanager: एक `yield` वाला generator दोनों methods की जगह ले लेता है
```

---

## 🟡 Real World Example
A Razorpay-style service wraps each payment in a database transaction: `with db.transaction():` commits on success and rolls back on any error. Other everyday uses: `with open()` for files, `with lock:` for threads, `with httpx.Client() as c:` for connection pools, `with tempfile.TemporaryDirectory()` in tests, and `with pytest.raises(...)` in test suites. A timing context manager logs how long a request handler took.

## 🟡 Real Example Hindi mein
Razorpay जैसी service हर payment को database transaction में लपेटती है: `with db.transaction():` सफल होने पर commit और किसी भी error पर rollback करता है। रोज़ के और उपयोग: files के लिए `with open()`, threads के लिए `with lock:`, connection pools के लिए `with httpx.Client() as c:`, tests में `with tempfile.TemporaryDirectory()`, और test suites में `with pytest.raises(...)`। Timing वाला context manager बताता है कि request handler में कितना समय लगा।

---

## 💻 Code Example — Basic
```python
# Basic context manager (class based)
class Resource:                                 # a fake resource
    def __init__(self, name: str) -> None:      # constructor
        self.name: str = name                   # resource name

    def __enter__(self) -> "Resource":          # runs at the start of `with`
        print(f"open {self.name}")              # setup
        return self                             # value for `as r`

    def __exit__(self, exc_type, exc, tb) -> bool:    # runs at the end, always
        print(f"close {self.name} (error: {exc_type.__name__ if exc_type else None})")   # cleanup
        return False                            # False: do not hide exceptions


with Resource("db") as r:                       # enter -> body -> exit
    print("using", r.name)                      # body

try:                                            # error inside the block
    with Resource("file"):                      # exit still runs
        raise ValueError("boom")                # simulate failure
except ValueError as e:                         # exception propagated (exit returned False)
    print("caught:", e)

# Output:
# open db
# using db
# close db (error: None)
# open file
# close file (error: ValueError)
# caught: boom
```

## 💻 Code Example — Advanced
```python
# Production style: transaction manager, @contextmanager timer, suppress, ExitStack
import time                                     # for timing
from contextlib import contextmanager, suppress, ExitStack   # helpers
from collections.abc import Iterator            # generator type


class FakeDB:                                   # stand-in for a database
    def __init__(self) -> None:
        self.rows: list[str] = []               # committed rows
        self.pending: list[str] = []            # uncommitted rows

    def insert(self, row: str) -> None:
        self.pending.append(row)                # stage the row

    def transaction(self) -> "Transaction":     # factory
        return Transaction(self)


class Transaction:
    """Commit on success, rollback on any exception."""

    def __init__(self, db: FakeDB) -> None:
        self.db: FakeDB = db

    def __enter__(self) -> FakeDB:
        self.db.pending.clear()                 # start clean
        return self.db                          # body works on the db

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None:                    # success
            self.db.rows.extend(self.db.pending)    # commit
            print("commit", self.db.pending)
        else:                                   # failure
            print("rollback because:", exc)     # undo
        self.db.pending.clear()                 # always clean up
        return False                            # still raise the error to the caller


@contextmanager                                 # generator-based: shorter
def timer(label: str) -> Iterator[None]:
    start: float = time.perf_counter()          # setup
    try:
        yield                                   # body of the with block runs here
    finally:                                    # cleanup, even on error
        ms: float = (time.perf_counter() - start) * 1000
        print(f"{label} took {'>0' if ms > 0 else '0'} ms")   # exact value varies per run


db: FakeDB = FakeDB()
with timer("order-1"), db.transaction() as tx:  # two managers in one `with`
    tx.insert("order-1")
    tx.insert("payment-1")

try:
    with db.transaction() as tx:                # failing transaction
        tx.insert("order-2")
        raise RuntimeError("payment gateway down")
except RuntimeError as e:
    print("handled:", e)

print("saved rows:", db.rows)                   # only the committed ones

with suppress(FileNotFoundError):               # ignore one specific error
    open("/no/such/file")                       # raises, but suppressed
print("continued after suppress")

with ExitStack() as stack:                      # a dynamic number of managers
    for n in ("a", "b"):
        stack.enter_context(Transaction(db))    # each is closed in reverse order on exit
    print("inside ExitStack")

# Output (timing digit varies):
# commit ['order-1', 'payment-1']
# order-1 took >0 ms
# rollback because: payment gateway down
# handled: payment gateway down
# saved rows: ['order-1', 'payment-1']
# continued after suppress
# inside ExitStack
# commit []
# commit []
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Guaranteed cleanup | `with` statement | `try { } finally { }` |
| Protocol | `__enter__` / `__exit__` | `Symbol.dispose` with `using` (newer; check runtime support) |
| Generator-based helper | `@contextmanager` | none |
| Async version | `async with` (`__aenter__`/`__aexit__`) | `await using` (new) |
| Swallow an exception | return `True` from `__exit__` | `catch` block |

```python
# Python way
with open("note.txt", "w") as f:       # file is closed automatically
    f.write("hello")
print(f.closed)                        # True
```
```javascript
// JavaScript way (Node.js) — try/finally is the classic equivalent
const fs = require("fs");
const fd = fs.openSync("note.txt", "w");
try {
  fs.writeSync(fd, "hello");
} finally {
  fs.closeSync(fd);                    // must close manually
}
// Newer JS has `using` + Symbol.dispose, but it is not available everywhere yet.
```

Key difference: Python builds the cleanup guarantee into the language through `with`, so all libraries share one pattern. JavaScript traditionally relies on `try/finally` written by hand each time.

---

## 🟠 FastAPI Connection
FastAPI dependencies with `yield` are context managers in disguise. The code before `yield` is setup, the code after is cleanup (like `__exit__`). This is the standard way to give each request a database session and always close it. Lifespan events also use `@asynccontextmanager`.

```python
# FastAPI example — yield dependency = per-request context manager
from collections.abc import Iterator            # generator type
from fastapi import FastAPI, Depends            # app and DI
from fastapi.testclient import TestClient       # test client

events: list[str] = []                          # record what happened


class Session:
    def close(self) -> None:
        events.append("session closed")         # cleanup marker


def get_session() -> Iterator[Session]:         # dependency with yield
    s: Session = Session()                      # setup (like __enter__)
    events.append("session opened")
    try:
        yield s                                 # the route runs here
    finally:
        s.close()                               # cleanup (like __exit__), always runs


app: FastAPI = FastAPI()                        # create app


@app.get("/ping")
def ping(s: Session = Depends(get_session)) -> dict[str, str]:
    events.append("handler ran")
    return {"ok": "yes"}


client: TestClient = TestClient(app)            # test client
client.get("/ping")
print(events)

# Output:
# ['session opened', 'handler ran', 'session closed']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `try/finally` inside a `@contextmanager` generator
✅ Correct: wrap `yield` in `try/finally` or cleanup is skipped on errors

```python
from contextlib import contextmanager

@contextmanager
def wrong():
    print("setup")
    yield
    print("cleanup")        # skipped if the body raises!

@contextmanager
def right():
    print("setup")
    try:
        yield
    finally:
        print("cleanup")    # always runs

try:
    with wrong():
        raise ValueError
except ValueError:
    print("wrong: no cleanup printed")

try:
    with right():
        raise ValueError
except ValueError:
    print("right: cleanup printed above")
```

❌ Mistake 2: Returning `True` from `__exit__` by accident (hides every error)
✅ Correct: return `False`/`None` unless you deliberately handle the exception

```python
class Wrong:
    def __enter__(self): return self
    def __exit__(self, *a) -> bool:
        return True            # swallows EVERYTHING, even bugs

with Wrong():
    1 / 0                      # ZeroDivisionError disappears silently
print("program continues, bug hidden")
```

❌ Mistake 3: Using the object after the `with` block, or reusing a one-shot manager
✅ Correct: use the resource inside the block; create a new manager for a new `with`

```python
from contextlib import contextmanager

@contextmanager
def once():
    yield "value"

cm = once()
with cm as v:
    print(v)                   # value
try:
    with cm:                   # generator is exhausted
        pass
except (RuntimeError, AttributeError) as e:    # the exact error type varies by Python version
    print("Error:", type(e).__name__)   # AttributeError on 3.13 (RuntimeError on some older versions)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class CM:
    def __enter__(self) -> "CM":
        print("enter")
        return self
    def __exit__(self, *args) -> bool:
        print("exit")
        return True

def f() -> str:
    with CM():
        return "from with"
    return "after with"

print(f())

with CM():
    raise ValueError("lost")
print("done")
```
Answer: `enter`, `exit`, `from with` for the first call: `return` inside the block still triggers `__exit__` before the function returns. Because `__exit__` returns `True`, it does not change the return value. Then `enter`, `exit`, `done`: the `ValueError` is swallowed because `__exit__` returned `True`, so no traceback appears.

---

## ⚫ Interview Questions + Answers

Q1: What are the arguments of `__exit__`?
A1: `(exc_type, exc_value, traceback)`. All are `None` if the block finished normally. Return `True` to suppress the exception, anything falsy to let it propagate.

Q2: What does the `with` statement expand to?
A2: Roughly: `mgr = expr; x = mgr.__enter__(); try: body; except: if not mgr.__exit__(*exc_info): raise; else: mgr.__exit__(None, None, None)`. Exit always runs.

Q3: Class-based vs `@contextmanager`?
A3: `@contextmanager` is shorter for simple cases (one setup, one cleanup, `try/finally` around `yield`). A class is better when the manager is reusable, holds state, or needs separate methods. Class-based managers can also be re-entered if designed for it.

Q4: What is an async context manager?
A4: One that defines `__aenter__` and `__aexit__` and is used with `async with`, for awaitable setup/cleanup like opening an aiohttp session or an asyncpg connection. `@asynccontextmanager` is the generator shortcut.

Q5: What are `suppress` and `ExitStack`?
A5: `contextlib.suppress(Exc)` ignores the listed exceptions inside the block. `ExitStack` manages a dynamic number of context managers and closes them in reverse (LIFO) order, useful when the number of resources is only known at runtime.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything that must be released: files, sockets, locks, DB sessions, temp files
- Transactions (commit/rollback) and timing/logging scopes
- Temporarily changing state (env vars, working directory, mock patches)

❌ Avoid when:
- No cleanup is needed (a plain function is enough)
- The resource lives longer than one block (long-lived connections need explicit lifecycle management, such as FastAPI lifespan)
- You would swallow errors silently

---

## 📊 Visual Diagram
```
 with Transaction(db) as tx:
        |
        v
   __enter__()  ---- setup ----> returns tx
        |
        v
   [ body runs ]
        |
        +-- ok ----------> __exit__(None, None, None) --> commit
        |
        +-- exception ---> __exit__(Type, err, tb) ------> rollback
                                  |
                      returns True  -> exception swallowed
                      returns False -> exception re-raised
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context manager | Object usable in `with` | `with` में चलने वाला object |
| `__enter__` | Setup, runs on entry | Setup, प्रवेश पर चलता है |
| `__exit__` | Cleanup, always runs | Cleanup, हमेशा चलता है |
| `@contextmanager` | Turn a generator into a manager | Generator को manager बनाना |
| ExitStack | Manage many managers dynamically | कई managers को dynamic रूप से संभालना |
| Rollback | Undo changes after failure | Failure के बाद बदलाव वापस लेना |

---

## ⚡ 3-Line Summary
English: A context manager guarantees setup and cleanup around a `with` block using `__enter__` and `__exit__`, even on errors. Use `@contextmanager` for short ones and a class for stateful ones. Return `True` from `__exit__` only when you truly want to swallow an exception.
Hindi: Context manager `__enter__` और `__exit__` से `with` block के आसपास setup और cleanup की गारंटी देता है, error आने पर भी। छोटे के लिए `@contextmanager` और state वाले के लिए class इस्तेमाल करें। `__exit__` से `True` तभी लौटाएं जब सच में exception दबाना हो।

---

## ➡️ Next Topic
**107. `__call__` Method** — make an object callable like a function: great for stateful callbacks, decorators and FastAPI dependencies.
