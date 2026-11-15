---

# 145. with Statement
# हिंदी में: with Statement (setup और cleanup अपने आप)

---

## 🔵 Simple Definition (English)
The `with` statement runs a block of code between an automatic setup and an automatic cleanup. The object after `with` is a context manager: its `__enter__` runs first, and its `__exit__` always runs at the end, even if an error happens. It is the clean replacement for `try/finally` around files, locks and connections.

## 🔵 सरल परिभाषा (Hindi)
`with` statement एक code block को automatic setup और automatic cleanup के बीच चलाता है। `with` के बाद वाला object context manager होता है: पहले उसका `__enter__` चलता है, और अंत में `__exit__` हमेशा चलता है, error आए तब भी। Files, locks और connections के चारों ओर `try/finally` की सफाई वाली जगह यही इस्तेमाल होता है।

---

## 🔴 Problem it Solves
Opening a file and forgetting `close()`, or leaving a database lock held after an exception, leaks resources and can freeze the whole service. Writing `try/finally` everywhere is long and easy to forget. `with` guarantees the cleanup in one readable line.

## 🔴 यह क्यों बना? (Hindi)
File खोलकर `close()` भूल जाना, या exception के बाद database lock पकड़े रखना resources leak करता है और पूरी service को अटका सकता है। हर जगह `try/finally` लिखना लंबा है और भूलना आसान। `with` एक पठनीय line में cleanup की गारंटी देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python evaluates the expression:  manager = open("a.txt")
Step 2 → It calls manager.__enter__() ; the result goes to the `as` name
Step 3 → The indented block runs
Step 4 → Block ends (normally, by return/break, or by exception)
Step 5 → Python calls manager.__exit__(exc_type, exc_value, traceback)
Step 6 → If __exit__ returns True, the exception is swallowed; else it continues
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python expression चलाता है:  manager = open("a.txt")
Step 2 → manager.__enter__() call होता है; result `as` वाले नाम में जाता है
Step 3 → indented block चलता है
Step 4 → block खत्म होता है (सामान्य रूप से, return/break से, या exception से)
Step 5 → Python manager.__exit__(exc_type, exc_value, traceback) call करता है
Step 6 → __exit__ True लौटाए तो exception दब जाता है; नहीं तो आगे बढ़ता है
```

---

## 🟡 Real World Example
A Razorpay settlement script opens a database transaction with `with db.begin():` so it commits on success and rolls back on any error. A report generator reads a CSV with `with open(path) as f:`. A worker takes a Redis lock with `with lock:` so two workers never charge the same order. An AI app uses `with httpx.Client() as client:` so connections are closed.

## 🟡 Real Example Hindi mein
Razorpay settlement script `with db.begin():` से transaction खोलती है, सफल होने पर commit और error पर rollback होता है। Report generator CSV को `with open(path) as f:` से पढ़ता है। Worker `with lock:` से Redis lock लेता है ताकि दो workers एक ही order पर charge न करें। AI app `with httpx.Client() as client:` इस्तेमाल करती है ताकि connections बंद हों।

---

## 💻 Code Example — Basic
```python
# with statement basics - every line commented
import tempfile  # to create a safe temp folder for the demo
from pathlib import Path  # path handling

folder = Path(tempfile.mkdtemp())  # make a temporary folder
file_path: Path = folder / "hello.txt"  # file inside it

with open(file_path, "w", encoding="utf-8") as f:  # open and auto-close
    f.write("namaste\n")  # write inside the block
    print(f.closed)  # still open inside
# Output: False
print(f.closed)  # closed automatically after the block
# Output: True

with open(file_path, encoding="utf-8") as f:  # read it back
    print(f.read().strip())  # print content
# Output: namaste

# Cleanup happens even on exceptions
try:  # catch the error outside
    with open(file_path, encoding="utf-8") as f:  # open
        raise ValueError("boom")  # error inside the block
except ValueError as exc:  # we reach here AFTER the file closed
    print("error:", exc, "| closed:", f.closed)  # show both
# Output: error: boom | closed: True

# Two managers in one with (comma separated)
copy_path: Path = folder / "copy.txt"  # destination file
with open(file_path, encoding="utf-8") as src, open(copy_path, "w", encoding="utf-8") as dst:
    dst.write(src.read())  # copy content
print(copy_path.read_text(encoding="utf-8").strip())  # verify copy
# Output: namaste

# Parenthesized form is official in Python 3.10+ (long lines)
with (
    open(file_path, encoding="utf-8") as a,  # first manager
    open(copy_path, encoding="utf-8") as b,  # second manager
):
    print(a.read() == b.read())  # compare the files
# Output: True

# A manual version of what `with` does (simplified)
f2 = open(file_path, encoding="utf-8")  # create the manager
try:  # protect the block
    data = f2.read()  # the block body
finally:  # always runs
    f2.close()  # the cleanup
print(data.strip(), f2.closed)  # same result as with
# Output: namaste True
```

## 💻 Code Example — Advanced
```python
# Production style: transaction-like manager, suppression, ordering, return values
import threading  # locks
from types import TracebackType  # type for __exit__
from typing import Optional  # optional types


class Transaction:  # simple commit/rollback manager
    def __init__(self, log: list[str]) -> None:  # store log list
        self.log = log  # where events go

    def __enter__(self) -> "Transaction":  # setup
        self.log.append("begin")  # open transaction
        return self  # object bound to `as`

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],  # exception class or None
        exc: Optional[BaseException],  # exception object or None
        tb: Optional[TracebackType],  # traceback or None
    ) -> bool:  # True means "swallow the error"
        if exc_type is None:  # no error
            self.log.append("commit")  # success path
        else:  # an error happened
            self.log.append(f"rollback ({exc_type.__name__})")  # undo
        return False  # do not hide the error


events: list[str] = []  # collect events
with Transaction(events):  # success case
    events.append("insert")  # work
print(events)  # sequence
# Output: ['begin', 'insert', 'commit']

events.clear()  # reset
try:  # failure case
    with Transaction(events):  # manager
        events.append("insert")  # work
        raise RuntimeError("db error")  # failure
except RuntimeError:  # error still propagates
    pass  # ignore for demo
print(events)  # sequence
# Output: ['begin', 'insert', 'rollback (RuntimeError)']


# Nested managers exit in reverse order (like a stack)
class Step:  # prints enter/exit
    def __init__(self, name: str) -> None:  # store name
        self.name = name  # label

    def __enter__(self) -> "Step":  # enter
        print("enter", self.name)  # trace
        return self  # return self

    def __exit__(self, *exc_info: object) -> None:  # exit (returns None = False)
        print("exit", self.name)  # trace


with Step("A"), Step("B"):  # A entered first, exited last
    print("inside")  # body
# Output:
# enter A
# enter B
# inside
# exit B
# exit A

# Real lock usage: with guarantees release even on error
lock = threading.Lock()  # a mutual exclusion lock
counter: dict[str, int] = {"n": 0}  # shared data


def work() -> None:  # run by each thread
    for _ in range(1000):  # many increments
        with lock:  # acquire; always released
            counter["n"] += 1  # safe update


threads = [threading.Thread(target=work) for _ in range(4)]  # 4 workers
for t in threads:  # start them
    t.start()  # begin
for t in threads:  # wait for them
    t.join()  # finish
print(counter["n"], lock.locked())  # exact count and lock free
# Output: 4000 False

# Swallowing a specific error with contextlib.suppress
from contextlib import suppress  # standard helper
with suppress(FileNotFoundError):  # ignore only this error type
    open("/definitely/missing.txt")  # raises FileNotFoundError, silently ignored
print("continued")  # execution goes on
# Output: continued
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has no `with` for cleanup (its `with` is a legacy scope feature, forbidden in strict mode). You use `try/finally`, or the newer **`using`** declarations (Explicit Resource Management, supported in recent runtimes and TypeScript 5.2+).

```python
# Python way
with open("data.txt", "w") as f:
    f.write("hi")            # file closes automatically
```
```javascript
// JavaScript way (classic)
const fs = require("fs");
const fd = fs.openSync("data.txt", "w");
try {
  fs.writeSync(fd, "hi");
} finally {
  fs.closeSync(fd);           // manual cleanup
}
// Modern (TS 5.2+/new runtimes): using res = getResource();  // calls res[Symbol.dispose]()
```

Key differences: Python's protocol is `__enter__`/`__exit__`; JS's new one is `Symbol.dispose`. Python's `__exit__` can also decide whether to hide an exception.

---

## 🟠 FastAPI Connection
FastAPI itself uses `with` heavily: `with Session(engine) as session:` for SQLAlchemy, `with TestClient(app) as client:` to run startup/shutdown events, and `yield` dependencies behave like a `with` around each request.

```python
# FastAPI: with TestClient runs lifespan events (pip install fastapi httpx)
from contextlib import asynccontextmanager  # build an async context manager
from collections.abc import AsyncIterator  # type hint
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # test client

log: list[str] = []  # event log


@asynccontextmanager  # lifespan is an async context manager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # startup + shutdown
    log.append("startup")  # before serving
    yield  # app serves requests here
    log.append("shutdown")  # after serving


app: FastAPI = FastAPI(lifespan=lifespan)  # attach lifespan


@app.get("/ping")  # simple route
def ping() -> dict[str, str]:  # handler
    return {"ok": "yes"}  # response


with TestClient(app) as client:  # `with` triggers startup and shutdown
    print(client.get("/ping").json(), log)  # inside the block
# Output: {'ok': 'yes'} ['startup']
print(log)  # after the block shutdown ran
# Output: ['startup', 'shutdown']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the resource after the `with` block
```python
# Wrong - file is closed here
with open("a.txt", "w") as f:
    pass
# f.write("x")        # ValueError: I/O operation on closed file

# Right - do all work inside the block
```

❌ Mistake 2: Forgetting `return` value of `__enter__`
```python
# Wrong - `as r` gets None
class R:
    def __enter__(self): pass
    def __exit__(self, *a): pass
with R() as r:
    print(r)              # None

# Right
class R2:
    def __enter__(self): return self
    def __exit__(self, *a): pass
with R2() as r:
    print(type(r).__name__)   # R2
```

❌ Mistake 3: Returning `True` from `__exit__` by accident
```python
# Wrong - hides ALL exceptions silently
# def __exit__(self, *a): return True

# Right - return False/None unless you deliberately handle the error
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
class M:
    def __enter__(self):
        print("enter")
        return self
    def __exit__(self, t, v, tb):
        print("exit", t.__name__ if t else None)
        return True

def f():
    with M():
        return "from block"
    return "after"

print(f())
with M():
    1 / 0
print("end")
```

**Answer**:
```
enter
exit None
from block
enter
exit ZeroDivisionError
end
```
`return` inside `with` still runs `__exit__` (with no exception) before the function returns. Since `__exit__` returns `True`, the `ZeroDivisionError` is swallowed and execution continues to `print("end")`.

---

## ⚫ Interview Questions + Answers

Q1: What does `with` guarantee?
A1: That `__exit__` is called when the block ends, whether it ends normally, by `return`/`break`/`continue`, or by an exception.

Q2: What are the arguments of `__exit__`?
A2: `exc_type`, `exc_value`, `traceback`. All three are `None` when there was no exception.

Q3: How do you handle two resources in one statement?
A3: `with A() as a, B() as b:`. They exit in reverse order. Python 3.10+ allows parentheses around the list for multi-line layout.

Q4: Is `with` only for files?
A4: No. Locks, DB sessions and transactions, temp directories, HTTP clients, mocks (`unittest.mock.patch`), timers and decimal precision (`decimal.localcontext`).

Q5: Difference from `try/finally`?
A5: `with` packages setup and cleanup inside the object so you do not repeat it; it also passes exception details to `__exit__` and can suppress the error.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You acquire something that must be released (files, locks, connections)
- You want commit/rollback style transactional behaviour
- You need temporary state (env var, working directory, patches)

❌ Avoid when:
- Nothing needs cleanup (a plain function call is enough)
- The resource must outlive the block (store it in an object with an explicit `close()`)
- You would hide errors by returning `True` from `__exit__`

---

## 📊 Visual Diagram

```
  with Manager() as m:
        │
        ▼
  m = Manager().__enter__()        ← setup
        │
        ▼
  ┌───── block body ─────┐
  │  normal  OR  raises  │
  └──────────┬───────────┘
             ▼
  Manager.__exit__(type, value, tb)   ← cleanup ALWAYS runs
             │
     returns True ──► exception swallowed
     returns False ─► exception continues
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context manager | Object with `__enter__` and `__exit__` | with के लिए setup/cleanup वाला object |
| `__enter__` | Runs at block start | block शुरू होने पर चलता है |
| `__exit__` | Runs at block end, always | block खत्म होने पर हमेशा चलता है |
| Resource leak | Not releasing files/locks | resources वापस न करना |
| Suppress | Hide an exception | exception को दबाना |
| Teardown | Cleanup step | सफाई का चरण |

---

## ⚡ 3-Line Summary
English: `with` calls `__enter__` before the block and `__exit__` after it, always. It replaces `try/finally` for files, locks, transactions and clients. Return `True` from `__exit__` only if you really want to hide an error.
Hindi: `with` block से पहले `__enter__` और बाद में हमेशा `__exit__` चलाता है। यह files, locks, transactions और clients के लिए `try/finally` की जगह लेता है। `__exit__` से `True` तभी लौटाएँ जब error सच में दबाना हो।

---

## ➡️ Next Topic
**146. Custom Context Manager** — write your own timer, lock and database-session managers.
