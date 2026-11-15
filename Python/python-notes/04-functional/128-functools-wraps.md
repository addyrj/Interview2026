---

# 128. functools.wraps
# हिंदी में: functools.wraps (decorator में function की पहचान बचाना)

---

## 🔵 Simple Definition (English)
`functools.wraps(func)` is a decorator you put on the inner `wrapper` function of your own decorator. It copies the original function's `__name__`, `__doc__`, `__module__`, `__qualname__`, `__annotations__`, `__dict__` and adds `__wrapped__`, so the wrapped function still looks like itself.

## 🔵 सरल परिभाषा (Hindi)
`functools.wraps(func)` एक decorator है जिसे आप अपने decorator के अंदर वाले `wrapper` पर लगाते हैं। यह original function का `__name__`, `__doc__`, `__module__`, `__qualname__`, `__annotations__`, `__dict__` कॉपी करता है और `__wrapped__` जोड़ता है, ताकि wrap होने के बाद भी function अपनी पहचान रखे।

---

## 🔴 Problem it Solves
A decorator replaces your function with `wrapper`. Without `wraps`, `hello.__name__` becomes `"wrapper"`, the docstring disappears, `help(hello)` shows the wrong thing, logs and stack traces are confusing, `inspect.signature` is wrong, and frameworks that read function names or signatures (FastAPI, pytest, Sphinx) misbehave.

## 🔴 यह क्यों बना? (Hindi)
Decorator आपके function की जगह `wrapper` रख देता है। `wraps` के बिना `hello.__name__` `"wrapper"` हो जाता है, docstring गायब हो जाता है, `help(hello)` गलत दिखाता है, logs और stack traces confusing हो जाते हैं, `inspect.signature` गलत आता है, और जो frameworks function के नाम या signature पढ़ते हैं (FastAPI, pytest, Sphinx) वे गड़बड़ करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write a decorator with an inner `wrapper`
Step 2 → @wraps(func) is applied to wrapper (it is itself a decorator factory)
Step 3 → It runs update_wrapper(wrapper, func)
Step 4 → Copies: __module__, __name__, __qualname__, __doc__, __annotations__
         (3.12+: also __type_params__)
Step 5 → Updates wrapper.__dict__ with func.__dict__
Step 6 → Sets wrapper.__wrapped__ = func so tools can reach the original

Before: hello.__name__ == "wrapper"        After: hello.__name__ == "hello"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप अंदर `wrapper` वाला decorator लिखते हैं
Step 2 → wrapper पर @wraps(func) लगता है (यह खुद एक decorator factory है)
Step 3 → यह update_wrapper(wrapper, func) चलाता है
Step 4 → कॉपी होता है: __module__, __name__, __qualname__, __doc__, __annotations__
         (3.12+: __type_params__ भी)
Step 5 → wrapper.__dict__ में func.__dict__ मिला दिया जाता है
Step 6 → wrapper.__wrapped__ = func सेट होता है ताकि tools original तक पहुँच सकें
```

---

## 🟡 Real World Example
A logging decorator on every Razorpay API method must still log `create_order`, not `wrapper`. An auth decorator on FastAPI routes must keep the original signature so FastAPI can read query/body parameters and generate OpenAPI docs. A pytest fixture wrapper must keep the name for test reports.

## 🟡 Real Example Hindi mein
Razorpay API के हर method पर लगा logging decorator `wrapper` नहीं बल्कि `create_order` log करे। FastAPI routes पर लगे auth decorator को original signature रखना होगा ताकि FastAPI query/body parameters पढ़ सके और OpenAPI docs बना सके। pytest fixture wrapper को test reports के लिए नाम बनाए रखना होगा।

---

## 💻 Code Example — Basic
```python
# Basic: with and without wraps
from functools import wraps                        # the tool
import inspect                                     # to read signatures


def bad_log(func):                                 # decorator WITHOUT wraps
    def wrapper(*args, **kwargs):                  # replaces the function
        return func(*args, **kwargs)               # just forward the call
    return wrapper


def good_log(func):                                # decorator WITH wraps
    @wraps(func)                                   # copy metadata to wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)               # forward the call
    return wrapper


@bad_log
def add_bad(a: int, b: int = 1) -> int:
    """Add two numbers."""
    return a + b


@good_log
def add_good(a: int, b: int = 1) -> int:
    """Add two numbers."""
    return a + b


print(add_bad.__name__, "|", add_bad.__doc__)      # metadata lost
print(add_good.__name__, "|", add_good.__doc__)    # metadata kept
print(inspect.signature(add_bad))                  # wrong: shows *args, **kwargs
print(inspect.signature(add_good))                 # right: follows __wrapped__
print(add_good.__wrapped__(2, 3))                  # call the ORIGINAL, bypass decorator
print(add_good.__annotations__)                    # annotations copied too

# Output:
# wrapper | None
# add_good | Add two numbers.
# (*args, **kwargs)
# (a: int, b: int = 1) -> int
# 5
# {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
```

## 💻 Code Example — Advanced
```python
# Production style: typed decorator keeping the signature + async support + logging
import asyncio                                     # run the async demo
import inspect                                     # detect coroutine functions
import logging                                     # standard logging
from collections.abc import Awaitable, Callable    # function types
from functools import wraps                        # metadata copier
from typing import ParamSpec, TypeVar              # keep signature in type hints

P = ParamSpec("P")                                 # captures parameters of the function
R = TypeVar("R")                                   # captures the return type

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(funcName)s: %(message)s")
log = logging.getLogger("audit")                   # our logger


def audit(func: Callable[P, R]) -> Callable[P, R]:
    """Log calls and errors; works for both sync and async functions."""
    if inspect.iscoroutinefunction(func):          # async function needs an async wrapper
        @wraps(func)                               # metadata for async wrapper
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs):
            log.info("calling %s", func.__name__)  # log with the REAL name
            try:                                   # catch and log errors
                return await func(*args, **kwargs) # await the coroutine
            except Exception:                      # any failure
                log.exception("%s failed", func.__name__)
                raise                              # never swallow errors
        return async_wrapper                       # type: ignore[return-value]

    @wraps(func)                                   # metadata for sync wrapper
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        log.info("calling %s", func.__name__)      # log with the REAL name
        try:
            return func(*args, **kwargs)           # run original
        except Exception:
            log.exception("%s failed", func.__name__)
            raise
    return wrapper


@audit
def create_order(user: str, amount: int) -> dict[str, object]:
    """Create an order."""
    return {"user": user, "amount": amount}


@audit
async def fetch_profile(user: str) -> str:
    """Load a profile."""
    await asyncio.sleep(0)                         # pretend IO
    return f"profile:{user}"


print(create_order("asha", 99))                    # sync path
print(asyncio.run(fetch_profile("ravi")))          # async path
print(create_order.__name__, fetch_profile.__name__)
print(inspect.iscoroutinefunction(fetch_profile))  # still recognized as async
print(inspect.signature(create_order))             # signature visible to tools

# Output (log lines go to stderr):
# INFO wrapper: calling create_order   <- %(funcName)s shows the wrapper's code name (wraps does not copy __code__)
# {'user': 'asha', 'amount': 99}
# profile:ravi
# create_order fetch_profile
# True
# (user: str, amount: int) -> dict[str, object]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Function name | `__name__` | `fn.name` |
| Docs | `__doc__` | none at runtime (JSDoc is comments) |
| Wrapper problem | wrapper hides name/doc/signature | wrapper hides `name` and `length` |
| Fix | `@wraps(func)` | `Object.defineProperty(wrapper, 'name', {value: fn.name})` |
| Original access | `__wrapped__` | manual property |

```python
# Python way — one line
from functools import wraps
def deco(f):
    @wraps(f)                                      # copies name, doc, annotations
    def w(*a, **k): return f(*a, **k)
    return w
```
```javascript
// JavaScript way — manual
function deco(fn) {
  const wrapper = (...args) => fn(...args);
  Object.defineProperty(wrapper, "name", { value: fn.name });   // copy the name by hand
  return wrapper;
}
```

Key difference: Python standardizes metadata copying in one decorator and also records `__wrapped__`, which `inspect.signature` follows. In JS this is manual and mostly cosmetic.

---

## 🟠 FastAPI Connection
FastAPI builds request parsing and OpenAPI docs from the function's signature (via `inspect.signature`, which follows `__wrapped__`). A decorator without `wraps` hides parameters, so FastAPI sees only `*args, **kwargs` and your query params vanish. With `wraps`, FastAPI sees the original parameters, name and docstring (used as the endpoint description).

```python
# FastAPI example — decorator that keeps the route signature intact
from functools import wraps                        # metadata copier
from fastapi import FastAPI                        # app
from fastapi.testclient import TestClient          # test without running a server

app: FastAPI = FastAPI()                           # create app


def log_calls(func):                               # decorator for async routes
    @wraps(func)                                   # IMPORTANT for FastAPI
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)         # forward to the real route
    return wrapper


@app.get("/hello")                                 # route on top, our decorator below
@log_calls
async def hello(name: str = "world") -> dict[str, str]:
    """Greets a person."""
    return {"msg": f"hi {name}"}


client = TestClient(app)                           # in-process client
print(client.get("/hello", params={"name": "Asha"}).json())    # {'msg': 'hi Asha'}
print(app.openapi()["paths"]["/hello"]["get"]["parameters"][0]["name"])   # name
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `@wraps`
✅ Correct: always decorate the wrapper

```python
# Wrong
def deco(f):
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper
# Right
from functools import wraps
def deco2(f):
    @wraps(f)
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper
```

❌ Mistake 2: Writing `@wraps` without the function argument
✅ Correct: `@wraps(func)` with parentheses and the original function

```python
from functools import wraps
def deco(f):
    # Wrong: @wraps   (wraps expects `wrapped`, used bare it breaks your wrapper)
    # Right:
    @wraps(f)
    def w(*a, **k): return f(*a, **k)
    return w
```

❌ Mistake 3: Using a sync wrapper around an async function
✅ Correct: use `async def wrapper` and `await` (see the advanced example)

```python
# Wrong: wrapper is sync, returns an un-awaited coroutine; FastAPI/asyncio.iscoroutinefunction is False
# Right: async def wrapper(...): return await func(...)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from functools import wraps
def deco(f):
    @wraps(f)
    def w(*a, **k):
        return f(*a, **k)
    return w

@deco
def foo(x: int) -> int:
    "docs"
    return x

print(foo.__name__, foo.__doc__)
print(foo.__wrapped__ is foo)
print(foo.__code__.co_name)
```
Answer: `foo docs`; then `False` (`__wrapped__` is the original function, `foo` is the wrapper); then `w`, because `__code__` is NOT copied: the code object still belongs to the wrapper, so `wraps` changes labels, not the actual code that runs.

---

## ⚫ Interview Questions + Answers

Q1: What exactly does `functools.wraps` copy?
A1: `__module__`, `__name__`, `__qualname__`, `__doc__`, `__annotations__` (and `__type_params__` in 3.12+). It updates the wrapper's `__dict__` with the original's, and sets `__wrapped__`.

Q2: Is `wraps` required for a decorator to work?
A2: No, the decorator works without it, but introspection, debugging, documentation tools and frameworks like FastAPI behave wrongly. It is considered mandatory in production code.

Q3: What is `__wrapped__` useful for?
A3: It points to the original function. `inspect.signature` follows it, `functools.lru_cache` exposes it, and tests can bypass a decorator by calling `f.__wrapped__(...)`.

Q4: Is `wraps` itself a decorator with arguments?
A4: Yes. `wraps(func)` returns `partial(update_wrapper, wrapped=func, ...)`, which is then applied to the wrapper. It is a small, real-life instance of the factory pattern.

Q5: Does `wraps` fix `inspect.getsource` or the traceback line numbers?
A5: `inspect.getsource` follows `__wrapped__` so it shows the original source. Tracebacks still show the wrapper's frames because the real code objects don't change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing ANY decorator that returns a wrapper function
- Using decorators in FastAPI, Flask, Django or pytest
- You need correct logs and docs

❌ Avoid when:
- The decorator returns the same function (no wrapper) or registers it only
- You deliberately want to hide the original identity (rare)

---

## 📊 Visual Diagram
```
without wraps:                     with wraps:
 hello ──► wrapper                  hello ──► wrapper
   __name__ = "wrapper"               __name__ = "hello"      (copied)
   __doc__  = None                    __doc__  = "Greets..."  (copied)
                                      __wrapped__ ──► original hello
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| wraps | Decorator that copies metadata | Metadata कॉपी करने वाला decorator |
| update_wrapper | The function behind wraps | wraps के पीछे का function |
| `__wrapped__` | Link to the original function | Original function की कड़ी |
| Introspection | Reading info about code at runtime | Runtime पर code की जानकारी पढ़ना |
| ParamSpec | Type for a function's parameters | Function के parameters का type |
| Signature | Parameters and return type | Parameters और return type |

---

## ⚡ 3-Line Summary
English: Put `@wraps(func)` on every wrapper so the decorated function keeps its name, docstring, annotations and signature. It also sets `__wrapped__` for tools. FastAPI, pytest and logging depend on it.
Hindi: हर wrapper पर `@wraps(func)` लगाएं ताकि decorated function अपना नाम, docstring, annotations और signature रखे। यह tools के लिए `__wrapped__` भी सेट करता है। FastAPI, pytest और logging इस पर निर्भर हैं।

---

## ➡️ Next Topic
**129. functools.lru_cache** — memoization with a size limit, `cache_info()` and the pitfalls.
