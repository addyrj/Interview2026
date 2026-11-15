---

# 427. Decorator Pattern
# हिंदी में: Decorator Pattern (Wrap करके नया behaviour जोड़ना)

---

## 🔵 Simple Definition (English)
The Decorator pattern adds new behaviour to an object or function by wrapping it, without changing its code. The wrapper has the same interface as the thing it wraps, so wrappers can be stacked. Python's `@decorator` syntax is built for this.

## 🔵 सरल परिभाषा (Hindi)
Decorator pattern किसी object या function को wrap करके उसमें नया behaviour जोड़ता है, उसका code बदले बिना। Wrapper का interface वही होता है जो wrap की गई चीज का है, इसलिए wrappers को एक के ऊपर एक लगाया जा सकता है। Python का `@decorator` syntax इसी के लिए है।

---

## 🔴 Problem it Solves
You need retry, logging, caching, timing, and auth around many functions. Copying that code into each function mixes concerns and duplicates bugs. Subclassing for every combination (EmailWithSms, EmailWithSmsAndSlack...) explodes into many classes. Wrapping lets you combine behaviours freely.

## 🔴 यह क्यों बना? (Hindi)
कई functions के आसपास retry, logging, caching, timing और auth चाहिए। यह code हर function में copy करने से concerns मिल जाते हैं और bugs दोहराए जाते हैं। हर combination के लिए subclass (EmailWithSms, EmailWithSmsAndSlack...) बनाने से classes का ढेर लग जाता है। Wrapping से behaviours को आजादी से जोड़ा जा सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick the thing to wrap (a function or an object with an interface)
Step 2 → Write a wrapper that takes it and keeps the SAME interface
Step 3 → Wrapper runs extra logic before/after and calls the original
Step 4 → Use functools.wraps so name and docstring survive
Step 5 → Stack wrappers: SlackDecorator(SmsDecorator(Basic()))
Step 6 → Order matters: the outermost wrapper runs first
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Wrap करने की चीज चुनो (function या interface वाला object)
Step 2 → ऐसा wrapper लिखो जो उसे ले और वही interface रखे
Step 3 → Wrapper आगे/पीछे extra logic चलाता है और original को बुलाता है
Step 4 → functools.wraps लगाओ ताकि name और docstring बचे रहें
Step 5 → Wrappers stack करो: SlackDecorator(SmsDecorator(Basic()))
Step 6 → Order मायने रखता है: सबसे बाहरी wrapper पहले चलता है
```

---

## 🟡 Real World Example
A payments service wraps a flaky bank API call with `@retry(times=3)`, `@timed`, and `@lru_cache`. FastAPI auth, rate limiting, and `functools.lru_cache` are decorators. In the object form, a `Notifier` can be wrapped to also send SMS and Slack alerts. Django's `login_required` is a classic example.

## 🟡 Real Example Hindi mein
Payments service एक अस्थिर bank API call को `@retry(times=3)`, `@timed` और `@lru_cache` से wrap करती है। FastAPI auth, rate limiting और `functools.lru_cache` decorators हैं। Object रूप में `Notifier` को wrap करके SMS और Slack alerts भी भेजे जा सकते हैं। Django का `login_required` क्लासिक उदाहरण है।

---

## 💻 Code Example — Basic
```python
# Basic Decorator PATTERN: wrap an object to add behaviour without changing its class
from typing import Protocol                   # interface


class Notifier(Protocol):
    def send(self, msg: str) -> str: ...


class BasicNotifier:
    def send(self, msg: str) -> str:
        return f"email({msg})"                # base behaviour


class SmsDecorator:
    def __init__(self, inner: Notifier) -> None:
        self._inner = inner                   # wrapped object

    def send(self, msg: str) -> str:
        return self._inner.send(msg) + f" + sms({msg})"   # extra behaviour added


class SlackDecorator:
    def __init__(self, inner: Notifier) -> None:
        self._inner = inner

    def send(self, msg: str) -> str:
        return self._inner.send(msg) + f" + slack({msg})"


n: Notifier = SlackDecorator(SmsDecorator(BasicNotifier()))   # stack wrappers
print(n.send("hi"))

# Output:
# email(hi) + sms(hi) + slack(hi)
```

## 💻 Code Example — Advanced
```python
# Production style: function decorators (retry + timing + cache) with functools.wraps, plus object wrapper
import functools                              # wraps, lru_cache
import time                                   # timing
from typing import Callable, ParamSpec, TypeVar   # typed decorators

P = ParamSpec("P")                            # parameters of wrapped function
R = TypeVar("R")                              # return type


def retry(times: int = 3, delay: float = 0.0) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)                  # keep name and docstring
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: Exception | None = None
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:        # retry on any error
                    last = e
                    print(f"attempt {attempt} failed: {e}")
                    time.sleep(delay)
            assert last is not None
            raise last                        # give up
        return wrapper
    return deco


calls: dict[str, int] = {"n": 0}


@retry(times=3)
def flaky_api() -> str:
    """Pretend network call."""
    calls["n"] += 1
    if calls["n"] < 3:
        raise ConnectionError("timeout")      # fails twice
    return "ok"


print(flaky_api())
print(flaky_api.__name__, "|", flaky_api.__doc__)   # wraps preserved metadata


@functools.lru_cache(maxsize=128)             # built-in caching decorator
def square(n: int) -> int:
    print("computing", n)
    return n * n


print(square(4), square(4))                   # second call from cache
print(square.cache_info())


@retry(times=2)
def always_fails() -> None:
    raise ValueError("bad")


try:
    always_fails()
except ValueError as e:
    print("final error:", e)

# Output:
# attempt 1 failed: timeout
# attempt 2 failed: timeout
# ok
# flaky_api | Pretend network call.
# computing 4
# 16 16
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
# attempt 1 failed: bad
# attempt 2 failed: bad
# final error: bad
```

Note: the `attempt N failed` lines come from the retry decorator's prints. `ParamSpec` needs Python 3.10+ (3.12+ also allows `def retry[**P, R]` syntax).

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Function decorator | `@retry` (built-in syntax) | higher-order function `retry(fn)`; TC39 decorators are for classes/methods |
| Keep metadata | `functools.wraps` | not needed for plain wrappers |
| Object wrapper | class holding `inner` | class holding `inner` |
| Built-in example | `@lru_cache`, `@property` | `useMemo`, Express middleware |

```python
# Python way
@retry(times=3)                              # wrap the function
def call_bank() -> str: ...
# same as: call_bank = retry(times=3)(call_bank)
```
```javascript
// JavaScript way
const callBank = retry(3)(async () => { /* ... */ });   // higher-order function
// Express middleware is the same idea: app.use(auth, handler)
```

Key difference: Python has syntax sugar `@` for wrapping functions, so the pattern feels native. In JavaScript you call higher-order functions by hand (the new decorator syntax is mainly for classes). Do not confuse the Decorator PATTERN (wrapping any object) with the Python `@` syntax (one way to do it).

---

## 🟠 FastAPI Connection
FastAPI routes are registered by decorators (`@app.get`). When you add your own decorator under it, use `functools.wraps` so FastAPI still sees the original signature, and keep `@app.get` as the OUTERMOST decorator. For cross-cutting logic across many routes, prefer dependencies or middleware.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
import functools
from typing import Any, Awaitable, Callable
from fastapi import FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()
audit: list[str] = []


def audited(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @functools.wraps(fn)                      # FastAPI needs the original signature
    async def wrapper(*a: Any, **kw: Any) -> Any:
        audit.append(f"call {fn.__name__}")
        return await fn(*a, **kw)
    return wrapper


@app.get("/ping")
@audited                                      # keep @app.get OUTERMOST
async def ping() -> dict[str, str]:
    return {"pong": "ok"}


print(TestClient(app).get("/ping").json(), audit)

# Output:
# {'pong': 'ok'} ['call ping']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `functools.wraps`
✅ Correct: always add it

```python
def deco(f):
    def wrapper(*a, **k):                    # Wrong: hello.__name__ becomes 'wrapper', docstring lost
        return f(*a, **k)
    return wrapper
import functools
def deco2(f):
    @functools.wraps(f)                      # Right: name, doc, signature preserved
    def wrapper(*a, **k):
        return f(*a, **k)
    return wrapper
```

❌ Mistake 2: Swallowing the return value
✅ Correct: return what the wrapped function returns

```python
# Wrong
def wrapper(*a, **k):
    f(*a, **k)                               # result thrown away -> returns None
# Right
def wrapper(*a, **k):
    return f(*a, **k)
```

❌ Mistake 3: Putting `@app.get` below another decorator
✅ Correct: route decorator on the outside

```python
# Wrong: @audited then @app.get -> app registers the raw function, audit never runs
# Right:
# @app.get("/ping")
# @audited
# async def ping(): ...
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def deco(f):
    def wrapper(*a, **k):
        return f(*a, **k)
    return wrapper
def tag(name):
    def d(f):
        print("applying", name)
        return f
    return d
@deco
def hello():
    "doc"
@tag("outer")
@tag("inner")
def x(): pass
print(hello.__name__, hello.__doc__)
```
Answer: Output: `applying inner`, `applying outer`, then `wrapper None`. Decorators are applied bottom-up, so `inner` runs first at definition time. Because `deco` did not use `functools.wraps`, `hello.__name__` is `'wrapper'` and the docstring is `None` (`wrapper` has none). At call time the order reverses: the outermost wrapper runs first.

---

## ⚫ Interview Questions + Answers

Q1: What is the Decorator pattern?
A1: A wrapper with the same interface as the wrapped object that adds behaviour before or after delegating. Wrappers can be stacked in any order.

Q2: Decorator pattern vs Python `@decorator`?
A2: `@` is syntax for applying a function that takes a function and returns a function. It is one implementation of the pattern. The pattern also covers wrapping objects (`SmsDecorator(inner)`).

Q3: Why use `functools.wraps`?
A3: It copies `__name__`, `__doc__`, `__module__` and sets `__wrapped__`, so debugging, logging, introspection, and FastAPI signature detection still work.

Q4: How do you write a decorator with arguments?
A4: Three layers: `retry(times)` returns `deco(fn)` which returns `wrapper(*args)`. `@retry(3)` calls the outer function first.

Q5: In what order do stacked decorators execute?
A5: Applied bottom-up (closest to the function first); at call time the top (outermost) wrapper runs first and calls inward.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cross-cutting concerns: retry, logging, caching, timing, auth
- You want to combine behaviours without many subclasses
- Add features to code you cannot modify

❌ Avoid when:
- Logic is core business behaviour: put it in the function
- Deep stacks that make debugging confusing
- You need to change the wrapped object's interface (use Adapter)

---

## 📊 Visual Diagram
```
call_bank()
   |
   v  @retry(3)          retry loop
   v  @timed             start timer
   v  @lru_cache         cache lookup
   v  original call_bank()   <- real work
   ^                     results travel back up through the same wrappers
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decorator | Wrapper adding behaviour | Behaviour जोड़ने वाला wrapper |
| Wrapper | Object/function that delegates | Delegate करने वाला object/function |
| functools.wraps | Copies metadata to wrapper | Wrapper में metadata copy करता है |
| ParamSpec | Typing for wrapped parameters | Wrapped parameters का typing |
| Cross-cutting concern | Feature needed in many places | कई जगह चाहिए वाला feature |

---

## ⚡ 3-Line Summary
English: Decorator wraps a function or object to add behaviour while keeping the same interface. Use `functools.wraps`, return the wrapped result, and remember that wrappers apply bottom-up but run top-down. Prefer it for cross-cutting concerns like retry, cache, and logging.
Hindi: Decorator किसी function या object को wrap करके वही interface रखते हुए नया behaviour जोड़ता है। `functools.wraps` लगाएं, wrapped का result लौटाएं, और याद रखें कि wrappers नीचे से ऊपर लगते हैं पर ऊपर से नीचे चलते हैं। Retry, cache और logging जैसे cross-cutting काम के लिए बेहतर है।

---

## ➡️ Next Topic
**428. Command Pattern** — turn actions into objects that can be queued, logged, and undone.
