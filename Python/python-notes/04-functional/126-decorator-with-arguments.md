---

# 126. Decorator with Arguments
# हिंदी में: Arguments वाला Decorator (जैसे @retry(times=3))

---

## 🔵 Simple Definition (English)
A decorator with arguments is a function that RETURNS a decorator. You write `@retry(times=3)`: Python first calls `retry(times=3)`, which returns the real decorator, and that decorator then wraps your function. This gives you three nested layers: settings, function, call.

## 🔵 सरल परिभाषा (Hindi)
Arguments वाला decorator ऐसा function है जो एक decorator लौटाता है। आप `@retry(times=3)` लिखते हैं: Python पहले `retry(times=3)` बुलाता है, जो असली decorator लौटाता है, और वह decorator आपके function को wrap करता है। इसमें तीन nested layers होती हैं: settings, function, call।

---

## 🔴 Problem it Solves
A plain decorator like `@log` has no settings. Real needs differ: retry 3 times here, 5 times there; cache for 60 seconds or 600; require role "admin" or "staff". Without arguments you would copy-paste a new decorator for each value. A decorator factory makes one reusable, configurable decorator.

## 🔴 यह क्यों बना? (Hindi)
सामान्य decorator `@log` में कोई settings नहीं होतीं। असली जरूरतें अलग हैं: यहाँ 3 बार retry, वहाँ 5 बार; 60 सेकंड cache या 600; role "admin" या "staff" चाहिए। Arguments के बिना हर value के लिए नया decorator copy-paste करना पड़ता। Decorator factory एक reusable, configurable decorator बना देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → @retry(times=3) is evaluated FIRST: retry(3) runs and returns `decorator`
Step 2 → Python then applies: func = decorator(func)
Step 3 → decorator(func) returns `wrapper` (closure remembers times AND func)
Step 4 → Calling func(...) now actually calls wrapper(...)
Step 5 → Use functools.wraps(func) on wrapper to keep name and docstring
Step 6 → Layers: retry(times) -> decorator(func) -> wrapper(*args, **kwargs)

@retry(times=3)          is the same as:
def f(): ...             f = retry(times=3)(f)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → @retry(times=3) सबसे पहले चलता है: retry(3) बुलाकर `decorator` मिलता है
Step 2 → फिर Python लगाता है: func = decorator(func)
Step 3 → decorator(func) `wrapper` लौटाता है (closure times और func दोनों याद रखती है)
Step 4 → अब func(...) बुलाना असल में wrapper(...) बुलाना है
Step 5 → नाम और docstring बचाने के लिए wrapper पर functools.wraps(func) लगाएं
Step 6 → Layers: retry(times) -> decorator(func) -> wrapper(*args, **kwargs)
```

---

## 🟡 Real World Example
A Razorpay payment client uses `@retry(times=3, delay=0.5)` on its HTTP call to survive network blips. An internal API uses `@require_role("admin")` on sensitive functions. A pricing service uses `@cache_for(seconds=60)`. A latency monitor uses `@timed(label="db_query")` to log slow calls.

## 🟡 Real Example Hindi mein
Razorpay का payment client network blips झेलने के लिए अपनी HTTP call पर `@retry(times=3, delay=0.5)` लगाता है। Internal API संवेदनशील functions पर `@require_role("admin")` लगाती है। Pricing service `@cache_for(seconds=60)` use करती है। Latency monitor धीमी calls log करने के लिए `@timed(label="db_query")` लगाता है।

---

## 💻 Code Example — Basic
```python
# Basic decorator with arguments
from collections.abc import Callable               # type for functions
from functools import wraps                        # keeps function metadata
from typing import Any                             # generic argument type


def repeat(times: int) -> Callable[[Callable[..., Any]], Callable[..., list[Any]]]:
    """Layer 1: receives the setting, returns the real decorator."""
    def decorator(func: Callable[..., Any]) -> Callable[..., list[Any]]:   # layer 2: gets the function
        @wraps(func)                               # copy name/doc onto wrapper
        def wrapper(*args: Any, **kwargs: Any) -> list[Any]:    # layer 3: runs on every call
            return [func(*args, **kwargs) for _ in range(times)]   # call func `times` times
        return wrapper                             # replaces the original function
    return decorator                               # this is what @repeat(...) applies


@repeat(times=3)                                   # same as hello = repeat(3)(hello)
def hello(name: str) -> str:
    """Greets someone."""
    return f"Hi {name}"                            # simple return value


print(hello("Asha"))                               # called 3 times, list returned
print(hello.__name__, "|", hello.__doc__)          # wraps kept the metadata

# Equivalent without @ syntax:
def bye(name: str) -> str:
    return f"Bye {name}"                           # plain function


bye = repeat(2)(bye)                               # manual decoration
print(bye("Ravi"))                                 # called twice

# Output:
# ['Hi Asha', 'Hi Asha', 'Hi Asha']
# hello | Greets someone.
# ['Bye Ravi', 'Bye Ravi']
```

## 💻 Code Example — Advanced
```python
# Production style: retry with backoff + works with and without parentheses
import time                                        # sleep between attempts
from collections.abc import Callable               # function types
from functools import wraps                        # keep metadata
from typing import Any, TypeVar, overload          # typing helpers

F = TypeVar("F", bound=Callable[..., Any])         # "any function" type variable


def retry(
    times: int = 3,                                # max attempts
    delay: float = 0.0,                            # seconds between attempts
    exceptions: tuple[type[BaseException], ...] = (Exception,),   # what to retry on
) -> Callable[[F], F]:
    """Retry a function on failure; re-raise the last error."""
    def decorator(func: F) -> F:                   # receives the real function
        @wraps(func)                               # keep name, doc, signature info
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last: BaseException | None = None      # remember the last failure
            for attempt in range(1, times + 1):    # 1..times
                try:                               # try the real call
                    return func(*args, **kwargs)   # success -> return immediately
                except exceptions as e:            # only retry listed errors
                    last = e                       # store it
                    print(f"attempt {attempt} failed: {e}")   # visible in demo
                    if attempt < times and delay:  # wait only if more attempts remain
                        time.sleep(delay)          # simple fixed delay
            assert last is not None                # we only get here after failures
            raise last                             # give up with the real error
        return wrapper  # type: ignore[return-value]   # wrapper acts as F
    return decorator


state = {"calls": 0}                               # counter to fake a flaky service


@retry(times=3, delay=0.01, exceptions=(ConnectionError,))
def call_gateway() -> str:
    """Fails twice, then succeeds."""
    state["calls"] += 1                            # count the attempt
    if state["calls"] < 3:                         # first two attempts fail
        raise ConnectionError("gateway timeout")   # transient error
    return "paid"                                  # third attempt works


print(call_gateway())                              # retries happen inside
print(call_gateway.__name__)                       # metadata preserved


@retry(times=2, exceptions=(ValueError,))          # only ValueError is retried
def bad_input() -> None:
    raise KeyError("not retried")                  # different error escapes at once


try:                                               # demo error handling
    bad_input()                                    # raises on the first attempt
except KeyError as e:                              # caught outside
    print("escaped:", e)                           # shows it was not retried


# Optional/bare-usage pattern: @deco and @deco(arg) both work
def tag(_func: Callable[..., Any] | None = None, *, label: str = "log") -> Any:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*a: Any, **k: Any) -> Any:
            print(f"[{label}] {func.__name__}")    # tiny side effect
            return func(*a, **k)                   # run original
        return wrapper
    return decorator(_func) if callable(_func) else decorator   # bare vs configured


@tag                                               # no parentheses
def a() -> int: return 1


@tag(label="audit")                                # with arguments
def b() -> int: return 2


print(a(), b())                                    # both styles work

# Output:
# attempt 1 failed: gateway timeout
# attempt 2 failed: gateway timeout
# paid
# call_gateway
# escaped: 'not retried'
# [log] a
# [audit] b
# 1 2
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Syntax | `@retry(3)` above function | no standard decorator for functions; wrap manually |
| Layers | 3 nested functions | function returning a function returning a function |
| Metadata | `functools.wraps` | n/a (name via `Object.defineProperty`) |
| Class decorators | stable and built in | TC39 decorators (new, TypeScript/Babel) |
| Usage | `@deco(args)` | `const f = retry(3)(fn)` |

```python
# Python way
@repeat(times=2)                                   # one line above the function
def ping() -> str: return "pong"
```
```javascript
// JavaScript way — higher-order function, applied manually
const retry = (times) => (fn) => (...args) => {    // 3 layers with arrows
  for (let i = 1; i <= times; i++) {
    try { return fn(...args); } catch (e) { if (i === times) throw e; }
  }
};
const safeCall = retry(3)(() => fetchData());      // no @ syntax
```

Key difference: the logic is identical (functions returning functions), but Python offers the `@decorator(args)` sugar; JavaScript has no built-in function decorators, so you apply them by calling.

---

## 🟠 FastAPI Connection
FastAPI itself uses decorators with arguments everywhere: `@app.get("/users", status_code=200)`. You can write your own for cross-cutting concerns: a role check, a rate limiter or a timing logger. Important: keep `@wraps` so FastAPI can read the signature, and put your decorator BELOW the route decorator.

```python
# FastAPI example — custom decorator with an argument on an async route
from functools import wraps                        # keep signature visible to FastAPI
from typing import Any, Awaitable, Callable        # types
from fastapi import FastAPI, HTTPException         # app and error

app: FastAPI = FastAPI()                           # create app


def require_key(expected: str) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)                               # FastAPI inspects the wrapped signature
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if kwargs.get("key") != expected:      # simple API-key check (key is a route param)
                raise HTTPException(status_code=401, detail="bad key")
            return await func(*args, **kwargs)     # call the real route
        return wrapper
    return decorator


@app.get("/secret")                                # route decorator on TOP
@require_key("abc123")                             # our decorator BELOW, runs first
async def secret(key: str = "") -> dict[str, str]:
    return {"data": "classified"}                  # only with the right key
```
For real projects, prefer FastAPI `Depends(...)` for auth; decorators are best for non-HTTP logic like retry and timing.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the parentheses when the decorator takes arguments
✅ Correct: always call it: `@retry()` or `@retry(times=3)`

```python
def retry(times=3):
    def deco(f):
        return f
    return deco
# Wrong — `f` is passed as `times`, and the function is replaced by `deco`
@retry
def f(): return 1
print(f)           # <function retry.<locals>.deco at 0x...>  (not your function!)
# Right
@retry()
def g(): return 1
print(g())         # 1
```

❌ Mistake 2: Forgetting `return` of the inner function levels
✅ Correct: each layer must return the next layer

```python
# Wrong: decorator forgets to return wrapper -> function becomes None
def bad(n):
    def deco(f):
        def wrapper(): return f()
        # missing: return wrapper
    return deco
@bad(2)
def h(): return 1
print(h)           # None
```

❌ Mistake 3: Not using `functools.wraps`
✅ Correct: add `@wraps(func)` to the wrapper

```python
# Wrong — name and docs are lost: shows "wrapper"
# Right — @wraps(func) keeps func.__name__ and __doc__
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def deco(n):
    print("A", n)
    def inner(f):
        print("B", f.__name__)
        def wrapper(*a):
            print("C")
            return f(*a)
        return wrapper
    return inner

@deco(1)
def foo():
    print("D")

print("E")
foo()
```
Answer: `A 1`, `B foo`, `E`, `C`, `D`. Decoration happens at DEFINITION time: `deco(1)` runs (prints A), then `inner(foo)` runs (prints B). Nothing else prints until `E`. Calling `foo()` runs the wrapper (C) and then the original (D). Layers 1 and 2 run once; layer 3 runs on every call.

---

## ⚫ Interview Questions + Answers

Q1: Why do decorators with arguments need three nested functions?
A1: One for the arguments (`retry(times)`), one to receive the function (`decorator(func)`) and one to run on each call (`wrapper`). `@retry(3)` evaluates to a decorator first, then that decorator is applied to the function.

Q2: How can a decorator work both as `@deco` and `@deco(arg=1)`?
A2: Accept an optional first parameter `func=None` and keyword-only options. If `func` is callable, decorate directly; otherwise return the decorator. (Shown in the advanced example.)

Q3: What is `@wraps` and why use it?
A3: `functools.wraps(func)` copies `__name__`, `__doc__`, `__module__`, `__wrapped__` and others from the original function to the wrapper. Without it, debugging, logging, `help()` and FastAPI's signature inspection break.

Q4: Can a class be used as a decorator with arguments?
A4: Yes. `__init__` takes the arguments and `__call__(self, func)` returns the wrapper. Class-based decorators are handy when you need state.

Q5: When does the decorator code run?
A5: The outer layers run at import/definition time, once. Only `wrapper` runs on each call. Expensive setup belongs in the outer layers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need configurable cross-cutting behavior: retry, cache TTL, rate limit, role check
- The same wrapper logic applies to many functions
- You want clean call sites with `@name(config)`

❌ Avoid when:
- Only one function needs it (a plain call is clearer)
- The behavior depends on many runtime values (pass a parameter or use dependency injection)
- You need to change the signature heavily (hurts readability and typing)

---

## 📊 Visual Diagram
```
@retry(times=3)
def call(): ...

definition time:
   retry(3)  -->  decorator   (remembers times=3)
   decorator(call)  -->  wrapper   (remembers times AND call)
   call = wrapper

call time:
   call() --> wrapper() --> try call (1) -> fail -> try (2) -> fail -> try (3) -> result
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decorator factory | Function that returns a decorator | Decorator लौटाने वाला function |
| Closure | Inner function remembering outer variables | Outer variables याद रखने वाला inner function |
| wrapper | The function that replaces the original | Original की जगह लेने वाला function |
| wraps | Copies metadata to wrapper | Wrapper में metadata कॉपी करना |
| Cross-cutting | Logic shared by many functions | कई functions में साझा logic |
| Definition time | When `def` executes | जब `def` चलता है |

---

## ⚡ 3-Line Summary
English: A decorator with arguments is a factory: `@d(x)` calls `d(x)` to get the real decorator, which then wraps the function. It needs three layers (settings, function, call) and `@wraps`. Outer layers run once at definition time.
Hindi: Arguments वाला decorator एक factory है: `@d(x)` पहले `d(x)` बुलाकर असली decorator लेता है, जो function को wrap करता है। इसमें तीन layers (settings, function, call) और `@wraps` चाहिए। बाहरी layers definition के समय एक बार चलती हैं।

---

## ➡️ Next Topic
**127. Functools Module** — the standard toolbox: `wraps`, `lru_cache`, `partial`, `reduce`, `cache`, `singledispatch` and more.
