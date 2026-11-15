---

# 148. Decorators — Deep Dive
# हिंदी में: Decorators — गहराई से समझना

---

## 🔵 Simple Definition (English)
A decorator is a function that takes another function, wraps extra behaviour around it, and returns the new function. Writing `@deco` above `def f` is just a short way to write `f = deco(f)`. Python uses closures and first-class functions to make this work.

## 🔵 सरल परिभाषा (Hindi)
Decorator एक ऐसा function है जो दूसरे function को लेता है, उसके चारों तरफ extra behaviour लगाता है और नया function return करता है। `def f` के ऊपर `@deco` लिखना असल में `f = deco(f)` का छोटा रूप है। Python में यह closures और first-class functions की वजह से काम करता है।

---

## 🔴 Problem it Solves
Cross-cutting work such as logging, retry, authentication, timing and caching is needed on dozens of functions. Copy-pasting `try/except` and `print` blocks into every function mixes business logic with plumbing, and one bug fix must be repeated everywhere. A decorator writes that logic once and applies it with one line, without touching the function body.

## 🔴 यह क्यों बना? (Hindi)
Logging, retry, authentication, timing और caching जैसा काम दर्जनों functions में चाहिए होता है। हर function में `try/except` और `print` copy-paste करने से business logic और plumbing मिल जाते हैं, और एक bug fix सब जगह दोहराना पड़ता है। Decorator वह logic एक बार लिखता है और function के body को छुए बिना एक लाइन में लगा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python runs `def add(...)` and creates the function object
Step 2 → It sees `@log_calls` and calls log_calls(add) right at definition time
Step 3 → log_calls builds an inner `wrapper` function (a closure that remembers `func`)
Step 4 → The name `add` is rebound to `wrapper`
Step 5 → Every later add(2, 3) call actually runs wrapper(2, 3)
Step 6 → wrapper runs extra code, calls the original func, and returns its result
Step 7 → @functools.wraps copies __name__, __doc__, __wrapped__ onto wrapper

@deco                      def f(): ...
def f(): ...      ==       f = deco(f)

Decorator with arguments = THREE levels:  factory(args) -> decorator(func) -> wrapper(*a, **k)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python `def add(...)` चलाकर function object बनाता है
Step 2 → वह `@log_calls` देखता है और definition के समय ही log_calls(add) call करता है
Step 3 → log_calls एक inner `wrapper` function बनाता है (closure जो `func` को याद रखता है)
Step 4 → नाम `add` अब `wrapper` से जुड़ जाता है
Step 5 → बाद में हर add(2, 3) call असल में wrapper(2, 3) चलाता है
Step 6 → wrapper extra code चलाता है, original func call करता है और result लौटाता है
Step 7 → @functools.wraps, wrapper पर __name__, __doc__, __wrapped__ copy कर देता है

Arguments वाला decorator = तीन levels:  factory(args) -> decorator(func) -> wrapper(*a, **k)
```

---

## 🟡 Real World Example
Razorpay-style payment code: the gateway call sometimes times out, so a `@retry(attempts=3)` decorator retries it. The same service also uses `@log_calls` for audit trails, `@require_role("admin")` for refunds, and `@lru_cache` for currency rates. FastAPI itself is built on decorators: `@app.get("/users")` registers your function as a route.

## 🟡 Real Example Hindi mein
Razorpay जैसे payment code में gateway call कभी-कभी timeout हो जाती है, इसलिए `@retry(attempts=3)` decorator उसे दोबारा चलाता है। वही service audit trail के लिए `@log_calls`, refund के लिए `@require_role("admin")` और currency rates के लिए `@lru_cache` इस्तेमाल करती है। FastAPI खुद decorators पर बना है: `@app.get("/users")` आपके function को route की तरह register करता है।

---

## 💻 Code Example — Basic
```python
# Basic decorator with functools.wraps
import functools                                          # wraps helper
from collections.abc import Callable                      # callable type
from typing import ParamSpec, TypeVar                     # generic signature types

P = ParamSpec("P")                                        # captures parameters of the wrapped function
R = TypeVar("R")                                          # captures its return type


def log_calls(func: Callable[P, R]) -> Callable[P, R]:    # decorator takes a function, returns a function
    @functools.wraps(func)                                # copy name, doc, __wrapped__ to wrapper
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # accept any arguments
        print(f"calling {func.__name__}{args}")           # before the real call
        result: R = func(*args, **kwargs)                 # call the original function
        print(f"{func.__name__} returned {result!r}")     # after the real call
        return result                                     # pass the result through
    return wrapper                                        # replace the original with wrapper


@log_calls                                                # same as add = log_calls(add)
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b                                          # real work


print(add(2, 3))                                          # runs wrapper -> add
print(add.__name__, "|", add.__doc__)                     # metadata kept because of wraps
print(add.__wrapped__(10, 20))                            # original function, no logging

# Output:
# calling add(2, 3)
# add returned 5
# 5
# add | Add two numbers.
# 30
```

## 💻 Code Example — Advanced
```python
# Production style: decorator factory, optional parentheses, sync + async support
import asyncio                                            # async runner
import functools                                          # wraps
import inspect                                            # detect coroutine functions
import time                                               # blocking sleep for sync code
from collections.abc import Callable                      # callable type
from typing import Any                                    # any type


def retry(_func: Callable[..., Any] | None = None, *, attempts: int = 3, delay: float = 0.0) -> Any:
    """Works as @retry and as @retry(attempts=5)."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(func):             # async function needs async wrapper
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                for i in range(1, attempts + 1):          # try up to N times
                    try:
                        return await func(*args, **kwargs)   # await the coroutine
                    except Exception as exc:              # retry on any error
                        print(f"[async] attempt {i} failed: {exc}")
                        if i == attempts:                 # last attempt: give up
                            raise
                        await asyncio.sleep(delay)        # non-blocking wait
            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            for i in range(1, attempts + 1):              # try up to N times
                try:
                    return func(*args, **kwargs)          # normal call
                except Exception as exc:                  # retry on any error
                    print(f"[sync] attempt {i} failed: {exc}")
                    if i == attempts:                     # last attempt: give up
                        raise
                    time.sleep(delay)                     # blocking wait
        return sync_wrapper

    if _func is not None:                                 # used as @retry (no parentheses)
        return decorator(_func)
    return decorator                                      # used as @retry(...) (factory)


calls: dict[str, int] = {"n": 0}                          # fake flaky service state


@retry                                                    # no parentheses, defaults
def flaky_payment() -> str:
    calls["n"] += 1                                       # count calls
    if calls["n"] < 3:                                    # fail twice
        raise ConnectionError("gateway timeout")
    return "paid"


@retry(attempts=2)                                        # factory form
async def always_fails() -> None:
    raise ValueError("bad card")                          # never succeeds


print(flaky_payment())                                    # succeeds on 3rd attempt
try:
    asyncio.run(always_fails())                           # exhausts attempts
except ValueError as e:
    print("gave up:", e)

# Output:
# [sync] attempt 1 failed: gateway timeout
# [sync] attempt 2 failed: gateway timeout
# paid
# [async] attempt 1 failed: bad card
# [async] attempt 2 failed: bad card
# gave up: bad card
```
Both blocks were run with Python 3.13.3 and the output above is the real output.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Syntax | `@deco` above `def` (stable, built-in) | TC39 decorators (new standard, mostly via TypeScript/Babel) |
| Plain wrapping | `f = deco(f)` | `f = deco(f)` (higher-order function) |
| Works on | functions, methods, classes | classes and class members only (not plain functions) |
| Keep metadata | `functools.wraps` | manual (`Object.defineProperty` for name) |
| Arguments | factory returns decorator | same idea |

```python
# Python way
import functools                                   # wraps
def shout(f):                                      # decorator
    @functools.wraps(f)                            # keep f's name
    def w(*a, **k):                                # wrapper
        return f(*a, **k).upper()                  # change result
    return w                                       # return wrapper

@shout                                             # apply with @
def hi() -> str:
    return "hello"
print(hi())                                        # HELLO
```
```javascript
// JavaScript way — higher-order function (works everywhere, no @ needed)
const shout = (f) => (...args) => f(...args).toUpperCase();   // wrapper
const hi = shout(() => "hello");                              // manual wrapping
console.log(hi());                                            // HELLO
// Express middleware (app.use(auth)) is the closest everyday idea.
```

Key difference: Python lets `@` decorate any plain function, so decorators are everyday tools. In JavaScript you usually call a higher-order function by hand, and the `@` syntax is limited to classes.

---

## 🟠 FastAPI Connection
Every route in FastAPI is a decorator: `@app.get(...)` registers the function and returns it unchanged. A custom decorator in front of a route must use `functools.wraps`, otherwise FastAPI cannot read the type hints and the OpenAPI docs break.

```python
# FastAPI example — timing decorator on an async route (run with TestClient)
import functools                                          # wraps
import time                                               # timer
from collections.abc import Awaitable, Callable           # callable types
from typing import Any                                    # any type
from fastapi import FastAPI                               # FastAPI app
from fastapi.testclient import TestClient                 # in-process client

app: FastAPI = FastAPI()                                  # create app


def timed(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @functools.wraps(func)                                # REQUIRED: keeps signature visible to FastAPI
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start: float = time.perf_counter()                # start clock
        result: Any = await func(*args, **kwargs)         # run the route
        print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")   # would go to metrics
        return result
    return wrapper


@app.get("/price/{item_id}")                              # outer: register the route
@timed                                                    # inner: wrap first
async def price(item_id: int) -> dict[str, int]:
    return {"item_id": item_id, "price": item_id * 10}    # fake price


print(TestClient(app).get("/price/7").json())             # {'item_id': 7, 'price': 70}

# Output (timing value varies; newer Starlette may also print an httpx deprecation warning):
# price took 0.0000s
# {'item_id': 7, 'price': 70}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `functools.wraps`
✅ Correct: always add `@functools.wraps(func)` to the wrapper

```python
import functools
def deco(f):
    def wrapper(*a, **k):                  # Wrong: no wraps
        return f(*a, **k)
    return wrapper
@deco
def hello():
    "doc"
print(hello.__name__, hello.__doc__)       # wrapper None  <- identity lost
# Right: add @functools.wraps(f) above wrapper -> prints: hello doc
```

❌ Mistake 2: Not returning the result of the wrapped function
✅ Correct: `return func(*args, **kwargs)`

```python
def bad(f):
    def w(*a, **k):
        f(*a, **k)                         # Wrong: result is thrown away, caller gets None
    return w
def good(f):
    def w(*a, **k):
        return f(*a, **k)                  # Right
    return w
```

❌ Mistake 3: Using `@deco(arg)` where deco only takes a function (or the reverse)
✅ Correct: remember the three-level shape for arguments

```python
def tag(name):                             # level 1: takes the argument
    def d(f):                              # level 2: takes the function
        return lambda: f"<{name}>{f()}</{name}>"   # level 3: the wrapper
    return d
@tag("b")                                  # Right: tag("b") returns the real decorator
def hi(): return "hi"
print(hi())                                # <b>hi</b>
# Wrong: writing @tag without () would pass the function as `name`
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def reg(f):
    print("registering", f.__name__)
    return f

@reg
def one():
    pass

print("after def")
one()
one()
```
Answer: It prints `registering one` and then `after def`; the two `one()` calls print nothing. A decorator runs once, at definition (import) time, not on every call. Only the code inside `wrapper` runs on each call. This is why decorators that register routes (like `@app.get`) work at import time, and why heavy work placed directly in the decorator body slows application startup.

---

## ⚫ Interview Questions + Answers

Q1: What is a decorator and what does `@deco` really do?
A1: A decorator is a callable that takes a function and returns a replacement. `@deco` above `def f` equals `f = deco(f)` executed right after the function is created.

Q2: Why do we use `functools.wraps`?
A2: Without it the wrapper replaces `__name__`, `__doc__`, `__module__` and the signature of the original. That breaks debugging, `help()`, pytest and FastAPI's introspection. `wraps` copies them and also sets `__wrapped__` so `inspect.signature` can follow it.

Q3: How do you write a decorator that takes arguments?
A3: Add one more level: an outer function receives the arguments and returns the real decorator, which returns the wrapper. Three nested functions in total.

Q4: How do you support both `@retry` and `@retry(attempts=5)`?
A4: Make the first parameter optional (`_func=None`) and the rest keyword-only. If `_func` is given, you were called without parentheses, so decorate immediately; otherwise return the decorator.

Q5: How do you type a decorator so the type checker keeps the signature?
A5: Use `ParamSpec` and `TypeVar`: `def deco(func: Callable[P, R]) -> Callable[P, R]` and `*args: P.args, **kwargs: P.kwargs` in the wrapper (typing module, Python 3.10+).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The same cross-cutting logic (log, retry, auth, cache, timing) applies to many functions
- You want to register functions (routes, plugins, event handlers)
- You must not change the body of the original function

❌ Avoid when:
- The logic is needed in one place only, a plain call is clearer
- The decorator hides important control flow (swallows exceptions silently)
- You need to share complex state, a class or a context manager is easier to read

---

## 📊 Visual Diagram
```
  @log_calls
  def add(a, b): ...             add  ──►  wrapper  ──►  original add
                                          │   ▲
  caller ── add(2, 3) ──────────────────► │   │
                                          ▼   │
                                  1. print "calling"
                                  2. result = func(2, 3) ─► 5
                                  3. print "returned"
                                  4. return result ──────► caller

  Closure: wrapper keeps a hidden reference to `func`
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decorator | Function that wraps another function | दूसरे function को लपेटने वाला function |
| Closure | Inner function remembering outer variables | बाहरी variables याद रखने वाला inner function |
| Wrapper | The function that replaces the original | Original की जगह आने वाला function |
| `functools.wraps` | Copies metadata to the wrapper | Wrapper पर metadata copy करता है |
| Decorator factory | Function that returns a decorator | Decorator लौटाने वाला function |
| ParamSpec | Type that captures a function's parameters | Function के parameters पकड़ने वाला type |

---

## ⚡ 3-Line Summary
English: A decorator replaces a function with a wrapper built by a higher-order function; `@deco` means `f = deco(f)` at definition time. Always use `functools.wraps`, return the result, and add one more level when the decorator needs arguments. Frameworks like FastAPI rely on decorators for routing.
Hindi: Decorator एक function को higher-order function से बने wrapper से बदल देता है; `@deco` का मतलब definition के समय `f = deco(f)` है। हमेशा `functools.wraps` लगाएं, result return करें, और arguments चाहिए तो एक और level जोड़ें। FastAPI जैसे frameworks routing के लिए decorators पर निर्भर हैं।

---

## ➡️ Next Topic
**149. Class-based Decorators** — using a class with `__init__` and `__call__` to build decorators that keep state, such as call counters and caches.
