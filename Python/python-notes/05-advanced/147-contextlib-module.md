---

# 147. contextlib Module
# हिंदी में: contextlib Module (context managers बनाने के आसान tools)

---

## 🔵 Simple Definition (English)
`contextlib` is a standard library module with helpers for `with` statements. The most used are `@contextmanager` (write a manager as a generator with one `yield`), `suppress` (ignore chosen errors), `closing`, `redirect_stdout`, `nullcontext`, `ExitStack` (a dynamic stack of managers) and `@asynccontextmanager` for async code.

## 🔵 सरल परिभाषा (Hindi)
`contextlib` standard library का module है जिसमें `with` statements के helpers हैं। सबसे ज़्यादा इस्तेमाल होने वाले हैं `@contextmanager` (एक `yield` वाले generator से manager बनाना), `suppress` (चुनी हुई errors को अनदेखा करना), `closing`, `redirect_stdout`, `nullcontext`, `ExitStack` (managers का dynamic stack) और async code के लिए `@asynccontextmanager`।

---

## 🔴 Problem it Solves
Writing a full class with `__enter__` and `__exit__` for every small setup/cleanup is long. Handling a number of resources that is not known in advance (open N files) is awkward with nested `with`. `contextlib` makes both short and safe.

## 🔴 यह क्यों बना? (Hindi)
हर छोटे setup/cleanup के लिए `__enter__` और `__exit__` वाली पूरी class लिखना लंबा है। जब resources की संख्या पहले से पता न हो (N files खोलना), तब nested `with` बेढंगा हो जाता है। `contextlib` दोनों को छोटा और सुरक्षित बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decorate a generator function with @contextmanager
Step 2 → Code BEFORE the single yield is the setup (__enter__)
Step 3 → The yielded value is bound to the `as` name
Step 4 → Code AFTER the yield is the cleanup (__exit__)
Step 5 → If the block raised, the error is thrown INTO the generator at the yield
Step 6 → Wrap the yield in try/finally so cleanup always runs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → generator function पर @contextmanager लगाओ
Step 2 → अकेले yield से पहले का code setup (__enter__) है
Step 3 → yield की गई value `as` वाले नाम में बँधती है
Step 4 → yield के बाद का code cleanup (__exit__) है
Step 5 → block में error आए तो वह yield वाली जगह generator के अंदर फेंका जाता है
Step 6 → cleanup हमेशा चले, इसलिए yield को try/finally में रखो
```

---

## 🟡 Real World Example
A Zomato service uses `@contextmanager def db_session()` to open a session, commit on success, rollback on failure and always close it. A test suite uses `ExitStack` to open a list of temporary files of unknown size. A script uses `suppress(FileNotFoundError)` to delete an optional cache file. A report tool uses `redirect_stdout` to capture the output of a legacy function that only prints.

## 🟡 Real Example Hindi mein
Zomato service `@contextmanager def db_session()` से session खोलती है, सफल होने पर commit, असफल होने पर rollback और हमेशा close करती है। Test suite अज्ञात संख्या की temporary files खोलने के लिए `ExitStack` इस्तेमाल करती है। Script वैकल्पिक cache file हटाने के लिए `suppress(FileNotFoundError)` लगाती है। Report tool उस पुराने function का output पकड़ने के लिए `redirect_stdout` इस्तेमाल करता है जो सिर्फ print करता है।

---

## 💻 Code Example — Basic
```python
# contextlib basics - every line commented
import io  # in-memory text buffers
from collections.abc import Iterator  # type hint for generator-based managers
from contextlib import (  # the helpers we use
    closing,
    contextmanager,
    nullcontext,
    redirect_stdout,
    suppress,
)


@contextmanager  # turns a generator into a context manager
def announce(name: str) -> Iterator[str]:  # yields the `as` value
    print(f"enter {name}")  # setup (before yield)
    try:  # protect the cleanup
        yield name.upper()  # value bound to `as`; block runs here
    finally:  # always runs, even on error
        print(f"exit {name}")  # cleanup (after yield)


with announce("db") as label:  # use like any manager
    print("inside", label)  # block body
# Output:
# enter db
# inside DB
# exit db

try:  # error inside the block
    with announce("x"):  # manager
        raise ValueError("oops")  # thrown into the generator at the yield
except ValueError:  # still propagates (finally ran first)
    print("caught")  # show
# Output:
# enter x
# exit x
# caught

with suppress(KeyError, ZeroDivisionError):  # ignore these two errors only
    {}["missing"]  # KeyError ignored
    print("not printed")  # skipped because the block stopped at the error
print("after suppress")  # execution continues
# Output: after suppress

buffer = io.StringIO()  # place to capture output
with redirect_stdout(buffer):  # temporarily send print() to buffer
    print("captured text")  # goes to the buffer
print(repr(buffer.getvalue()))  # inspect what was captured
# Output: 'captured text\n'


class Resource:  # object with close() but no __exit__
    def close(self) -> None:  # cleanup method
        print("resource closed")  # trace


with closing(Resource()) as r:  # closing() calls r.close() at the end
    print("using", type(r).__name__)  # body
# Output:
# using Resource
# resource closed

use_lock = False  # configuration flag
with (open("/dev/null") if use_lock else nullcontext()) as f:  # optional manager
    print(f)  # nullcontext returns None
# Output: None
```

## 💻 Code Example — Advanced
```python
# Production style: session manager, ExitStack, chained managers, async manager
import asyncio  # async example
import tempfile  # temp files
from collections.abc import AsyncIterator, Iterator  # type hints
from contextlib import (
    ExitStack,
    aclosing,
    asynccontextmanager,
    contextmanager,
)
from pathlib import Path  # path handling


@contextmanager  # transaction pattern in ~10 lines
def session(log: list[str]) -> Iterator[dict[str, str]]:  # yields a fake session
    log.append("open")  # setup
    sess: dict[str, str] = {"user": "asha"}  # pretend session
    try:  # guard
        yield sess  # hand the session to the block
        log.append("commit")  # runs only if the block succeeded
    except Exception:  # block raised
        log.append("rollback")  # undo
        raise  # re-raise so the caller sees the error
    finally:  # always
        log.append("close")  # release


log: list[str] = []  # event log
with session(log) as s:  # success
    log.append(f"hello {s['user']}")  # work
print(log)  # sequence
# Output: ['open', 'hello asha', 'commit', 'close']

log.clear()  # reset
try:  # failure
    with session(log):  # open
        raise RuntimeError("bad")  # failure
except RuntimeError:  # still propagates
    pass  # ignore for demo
print(log)  # sequence
# Output: ['open', 'rollback', 'close']


# ExitStack: open a number of files not known in advance
folder = Path(tempfile.mkdtemp())  # temp folder
paths: list[Path] = [folder / f"f{i}.txt" for i in range(3)]  # three paths
for i, p in enumerate(paths):  # create files
    p.write_text(f"file {i}")  # content
with ExitStack() as stack:  # dynamic stack of managers
    files = [stack.enter_context(open(p)) for p in paths]  # open all of them
    stack.callback(print, "all files closed")  # extra cleanup action (runs last-in-first-out)
    print([f.read() for f in files])  # use them
# Output: ['file 0', 'file 1', 'file 2']
# (then) all files closed
print(all(f.closed for f in files))  # every file closed on exit
# Output: True


# Conditional/optional resources with ExitStack.pop_all (transfer ownership)
def open_two(a: Path, b: Path) -> tuple[ExitStack, list[object]]:  # safe multi-open
    with ExitStack() as stack:  # if second open fails, first is closed
        f1 = stack.enter_context(open(a))  # first file
        f2 = stack.enter_context(open(b))  # second file
        return stack.pop_all(), [f1, f2]  # success: caller now owns cleanup


owner, (g1, g2) = open_two(paths[0], paths[1])  # type: ignore[misc]
print(g1.closed, g2.closed)  # still open - ownership transferred
# Output: False False
owner.close()  # caller closes them
print(g1.closed, g2.closed)  # now closed
# Output: True True


# Reusable decorator: ContextDecorator (a manager that also works as @decorator)
from contextlib import ContextDecorator  # import here for clarity


class tracked(ContextDecorator):  # works as `with tracked():` and as `@tracked()`
    def __enter__(self) -> "tracked":  # setup
        print("start")  # trace
        return self  # self

    def __exit__(self, *exc: object) -> None:  # cleanup
        print("stop")  # trace


@tracked()  # used as a decorator
def job() -> str:  # function wrapped by the manager
    return "done"  # result


print(job())  # prints start, stop, then the result
# Output:
# start
# stop
# done


# Async manager
@asynccontextmanager  # async version of @contextmanager
async def connection(name: str) -> AsyncIterator[str]:  # async generator
    print("connect", name)  # setup
    try:  # guard
        yield f"conn-{name}"  # value for `as`
    finally:  # cleanup
        print("disconnect", name)  # always runs


async def agen() -> AsyncIterator[int]:  # an async generator
    try:  # cleanup guard
        yield 1  # first value
        yield 2  # second value
    finally:  # runs when closed
        print("agen closed")  # trace


async def main() -> None:  # demo coroutine
    async with connection("redis") as c:  # async with
        print("using", c)  # body
    async with aclosing(agen()) as g:  # aclosing is available in Python 3.10+
        async for v in g:  # iterate
            print("value", v)  # use
            break  # stop early - aclosing closes it safely


asyncio.run(main())  # run
# Output:
# connect redis
# using conn-redis
# disconnect redis
# value 1
# agen closed
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has no `contextlib`. The nearest ideas are `try/finally` helpers, the `AbortController` pattern, and the new `using` / `DisposableStack` from Explicit Resource Management (a close cousin of `ExitStack`; available in recent runtimes and TypeScript 5.2+).

```python
# Python way
from contextlib import contextmanager

@contextmanager
def tag(name):
    print(f"<{name}>")
    try:
        yield
    finally:
        print(f"</{name}>")

with tag("p"):
    print("text")          # <p> / text / </p>
```
```javascript
// JavaScript way (classic helper)
function withTag(name, fn) {
  console.log(`<${name}>`);
  try { fn(); }
  finally { console.log(`</${name}>`); }
}
withTag("p", () => console.log("text"));   // <p> / text / </p>
```

Key differences: Python's `yield` splits the function into setup and cleanup in the same scope, so `return` and `break` inside the block work naturally; JS callbacks cannot `break` the caller.

---

## 🟠 FastAPI Connection
FastAPI dependencies with `yield` are literally `contextmanager`-style functions (FastAPI wraps them with `contextlib` internally). The `lifespan` parameter takes an `@asynccontextmanager` function for startup and shutdown work such as creating DB pools or loading a model.

```python
# FastAPI: lifespan with @asynccontextmanager + yield dependency (pip install fastapi httpx)
from collections.abc import AsyncIterator, Iterator  # type hints
from contextlib import asynccontextmanager  # lifespan helper
from fastapi import Depends, FastAPI  # core
from fastapi.testclient import TestClient  # tests

state: dict[str, str] = {}  # app state for the demo
events: list[str] = []  # events log


@asynccontextmanager  # startup/shutdown in one function
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # lifespan signature
    state["model"] = "loaded"  # startup: e.g. load ML model
    yield  # application runs here
    state.clear()  # shutdown: release resources
    events.append("shutdown")  # trace


app: FastAPI = FastAPI(lifespan=lifespan)  # attach


def get_db() -> Iterator[str]:  # per-request dependency with yield
    events.append("db open")  # setup
    try:  # guard
        yield "db-handle"  # injected value
    finally:  # always
        events.append("db close")  # cleanup


@app.get("/predict")  # route
def predict(db: str = Depends(get_db)) -> dict[str, str]:  # inject
    return {"model": state["model"], "db": db}  # response


with TestClient(app) as client:  # runs lifespan startup
    print(client.get("/predict").json())  # request
# Output: {'model': 'loaded', 'db': 'db-handle'}
print(events)  # after shutdown
# Output: ['db open', 'db close', 'shutdown']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No `try/finally` around `yield`
```python
# Wrong - cleanup is skipped when the block raises
from contextlib import contextmanager

@contextmanager
def bad():
    print("open")
    yield
    print("close")           # never runs on error!

# Right
@contextmanager
def good():
    print("open")
    try:
        yield
    finally:
        print("close")       # always runs
```

❌ Mistake 2: Yielding more than once
```python
# Wrong - RuntimeError: generator didn't stop
@contextmanager
def twice():
    yield 1
    yield 2

# Right - exactly one yield
```

❌ Mistake 3: Using `suppress` too broadly
```python
# Wrong - hides real bugs
from contextlib import suppress
with suppress(Exception):    # swallows everything, even typos (NameError)
    pass

# Right - suppress only the specific, expected error
with suppress(FileNotFoundError):
    pass
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from contextlib import contextmanager

@contextmanager
def m():
    print("A")
    try:
        yield 1
    except ZeroDivisionError:
        print("handled")
    print("B")

with m() as v:
    print("v =", v)
    1 / 0
print("end")

m2 = m()
print(type(m2).__name__)
```

**Answer**:
```
A
v = 1
handled
B
end
_GeneratorContextManager
```
The `ZeroDivisionError` is thrown into the generator at `yield`. It is caught, so `m()` finishes normally and the error is swallowed (the generator did not re-raise). Because it was handled, `with` continues after the block. Without the `except`, the error would propagate. `m()` returns a `_GeneratorContextManager` object.

---

## ⚫ Interview Questions + Answers

Q1: How does `@contextmanager` work?
A1: It wraps a generator in a class with `__enter__` (runs until `yield`) and `__exit__` (resumes after the yield, throwing the block's exception into it if one occurred).

Q2: What is `ExitStack` for?
A2: To manage a dynamic number of context managers or cleanup callbacks, with guaranteed reverse-order exit, and to transfer ownership with `pop_all()`.

Q3: What is the difference between `suppress` and `try/except/pass`?
A3: Same effect for the listed exceptions; `suppress` is shorter and clearly signals intent. Code after the failing line inside the block is skipped in both.

Q4: What are `closing` and `aclosing` for?
A4: They call `.close()` or `await .aclose()` for objects that have those methods but are not context managers themselves. `aclosing` needs Python 3.10+.

Q5: Can a context manager also be used as a decorator?
A5: Yes. Managers made with `@contextmanager` (and subclasses of `ContextDecorator`) work as `@tracked()` decorators, a new instance of the context is created for every call.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Setup/cleanup fits in one generator with a single `yield`
- You manage a number of resources only known at runtime (`ExitStack`)
- You need to ignore one specific error (`suppress`) or capture output (`redirect_stdout`)

❌ Avoid when:
- You need public methods and reusable state (write a class)
- You catch everything with `suppress(Exception)`
- The logic is a one-liner that needs no cleanup

---

## 📊 Visual Diagram

```
 @contextmanager
 def m():
     setup()         ◄── runs in __enter__
     try:
         yield obj   ◄── obj becomes `as` value; BLOCK RUNS HERE
     finally:
         cleanup()   ◄── runs in __exit__ (error is thrown in at the yield)

 ExitStack:   enter A ─► enter B ─► enter C │ exit C ─► exit B ─► exit A
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `@contextmanager` | Generator to context manager | generator से manager बनाना |
| `suppress` | Ignore specific exceptions | चुनी errors को अनदेखा करना |
| `ExitStack` | Stack of managers/callbacks | managers का stack |
| `closing` | Call `.close()` on exit | exit पर `.close()` बुलाना |
| `nullcontext` | Do-nothing manager | कुछ न करने वाला manager |
| `asynccontextmanager` | Async generator manager | async वाला manager |

---

## ⚡ 3-Line Summary
English: `@contextmanager` turns a one-`yield` generator into a context manager: setup before, cleanup after, wrapped in `try/finally`. `suppress`, `closing`, `redirect_stdout`, `nullcontext` and `ExitStack` cover common needs. Use `@asynccontextmanager` for async code and FastAPI lifespan.
Hindi: `@contextmanager` एक-`yield` वाले generator को context manager बनाता है: पहले setup, बाद में cleanup, `try/finally` में। `suppress`, `closing`, `redirect_stdout`, `nullcontext` और `ExitStack` आम ज़रूरतें पूरी करते हैं। Async code और FastAPI lifespan के लिए `@asynccontextmanager` इस्तेमाल करें।

---

## ➡️ Next Topic
**148. Decorators Deep Dive** — wrap functions with reusable behaviour, the cousin of context managers.
