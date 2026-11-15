---

# Q195. Build Logger Wrapper
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `@logged()` decorator using the standard `logging` module. It logs the call (name, args), the return value with elapsed milliseconds, and on exceptions logs the traceback and re-raises. It must preserve the wrapped function's metadata.

```python
@logged()
def add(a, b): return a + b
```

---

## 💡 Quick Concept (2 lines only)
Wrap the function with `functools.wraps`; log before and after, time with `perf_counter`, and use `log.exception` in `except` to include the traceback. Never swallow the error.
हिंदी: Decorator से call, result और समय log करो; error पर `log.exception` से traceback लिखो और फिर से raise करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools  # wraps
import logging  # stdlib logging
import time  # timing
from typing import Any, Callable  # type hints

def logged(logger: logging.Logger | None = None, level: int = logging.INFO) -> Callable:
    def deco(fn: Callable) -> Callable:
        log = logger or logging.getLogger(fn.__module__)  # default: module logger
        @functools.wraps(fn)  # keep name/docstring
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log.log(level, "-> %s args=%r kwargs=%r", fn.__name__, args, kwargs)  # entry
            start = time.perf_counter()  # start timer
            try:
                result = fn(*args, **kwargs)  # call
            except Exception:
                log.exception("!! %s raised", fn.__name__)  # error + traceback
                raise  # never swallow
            ms = (time.perf_counter() - start) * 1000  # elapsed ms
            log.log(level, "<- %s returned %r (%.1fms)", fn.__name__, result, ms)  # exit
            return result  # pass through
        return wrapper
    return deco

# ============================================
# TEST CASES
# ============================================
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")  # simple format
@logged()
def add(a: int, b: int) -> int:
    return a + b  # work
@logged()
def boom() -> None:
    raise ValueError("bad")  # failing function
print(add(2, b=3))  # Expected: INFO -> add args=(2,) kwargs={'b': 3} / INFO <- add returned 5 (0.0ms) / 5
try:
    boom()  # logs ERROR + traceback
except ValueError:
    print("caught")  # Expected: ERROR !! boom raised + traceback (timings/paths vary), then: caught
print(add.__name__)  # Expected: add
```

---

## 🔍 Why This Works (3 lines max)
Logging uses lazy `%s` formatting, so strings are built only if the level is enabled. `log.exception` inside `except` attaches the traceback; the bare `raise` keeps the exception flowing to the caller. `wraps` keeps `add.__name__`.
हिंदी: `log.exception` traceback जोड़ता है, bare `raise` error आगे भेजता है, और `wraps` function का नाम सुरक्षित रखता है।

---

## ⚡ Alternative Solution
```python
import logging  # stdlib

class Ctx(logging.LoggerAdapter):  # adapter injects context into every line
    def process(self, msg, kwargs):
        return f"[{self.extra['req_id']}] {msg}", kwargs  # prefix request id

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")  # setup
log = Ctx(logging.getLogger("app"), {"req_id": "abc123"})  # adapter with context
log.info("user logged in")  # Expected: INFO [abc123] user logged in
log.warning("slow query")  # Expected: WARNING [abc123] slow query
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: print() instead of logging, f-strings in log calls, swallowing the exception (not run)
# def wrapper(*a):
#     print(f"calling {fn.__name__} with {a}")       # no levels, no handlers, no timestamps
#     try: return fn(*a)
#     except Exception as e: logging.error(f"{e}")   # lost traceback AND returns None silently

# ✅ Correct: logging.getLogger(__name__), %s lazy args, log.exception(...), then `raise`
# Also: don't log secrets (passwords/tokens) in args.
```

---

## 🎯 Interview Tip (1 line)
Say: "Use logging, not print: levels, handlers, lazy formatting, `exception()` for tracebacks, and never log secrets."

---

## 🔗 Related Questions
→ Q039 (decorator without wraps) | Q090 (timer decorator) | Q139 (decorator losing metadata) | Q225 (custom middleware)
