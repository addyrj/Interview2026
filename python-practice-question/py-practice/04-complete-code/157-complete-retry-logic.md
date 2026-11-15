---

# Q157. Complete Retry Logic
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks (`____`) to finish a `retry(times, delay, exceptions)` decorator with exponential backoff. It must keep the wrapped function's name and re-raise the last error.

```python
import functools
import time

def retry(times: int = 3, delay: float = 0.01, exceptions: tuple[type[BaseException], ...] = (Exception,)):
    def decorator(fn):
        @functools.____(fn)                            # blank 1: keep fn's metadata
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, ____)             # blank 2: forward keyword args
                except ____ as exc:                    # blank 3: only retry these errors
                    if attempt == times:
                        ____                           # blank 4: re-raise last error
                    time.sleep(wait)
                    wait ____ 2                        # blank 5: double the wait (backoff)
        return wrapper
    return decorator
```

---

## 💡 Quick Concept (2 lines only)
Retry re-runs a flaky call a few times, waiting longer after each failure (exponential backoff), then gives up and raises.
हिंदी: Retry flaky call को बार-बार चलाता है, हर बार ज़्यादा wait करके, और आख़िर में error raise करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools                            # Step 1: for wraps
import time                                 # Step 2: for sleep

def retry(times: int = 3, delay: float = 0.01,
          exceptions: tuple[type[BaseException], ...] = (Exception,)):  # Step 3: config
    def decorator(fn):                      # Step 4: receives the function
        @functools.wraps(fn)                # Blank 1 -> wraps (keeps __name__, __doc__)
        def wrapper(*args, **kwargs):       # Step 5: the replacement function
            wait = delay                    # current backoff delay
            for attempt in range(1, times + 1):          # attempts 1..times
                try:                        # try the call
                    return fn(*args, **kwargs)           # Blank 2 -> **kwargs
                except exceptions as exc:   # Blank 3 -> exceptions (tuple works in except)
                    if attempt == times:    # last attempt failed?
                        raise               # Blank 4 -> raise (keeps original traceback)
                    time.sleep(wait)        # wait before the next try
                    wait *= 2               # Blank 5 -> *= (exponential backoff)
        return wrapper                      # return the wrapper
    return decorator                        # return the decorator

# ============================================
# TEST CASES
# ============================================
calls = {"n": 0}                            # counts how often flaky() runs

@retry(times=3, delay=0.001, exceptions=(ValueError,))   # retry on ValueError only
def flaky() -> str:                         # fails twice, then works
    """Flaky function."""                   # docstring to check wraps
    calls["n"] += 1                         # count the call
    if calls["n"] < 3:                      # first two calls fail
        raise ValueError("boom")            # transient error
    return "ok"                             # third call succeeds

print(flaky())                              # Expected: ok
print(calls["n"])                           # Expected: 3
print(flaky.__name__, flaky.__doc__)        # Expected: flaky Flaky function.

@retry(times=2, delay=0.001)                # always-failing function
def always_fails() -> None:                 # never succeeds
    raise RuntimeError("nope")              # raise every time

try:                                        # run it
    always_fails()                          # 2 attempts, then raises
except RuntimeError as e:                   # last error is re-raised
    print("gave up:", e)                    # Expected: gave up: nope

@retry(times=3, delay=0.001, exceptions=(ValueError,))   # only ValueError is retried
def wrong_type() -> None:                   # raises another type
    raise KeyError("x")                     # not retried
try:                                        # run it
    wrong_type()                            # raises immediately
except KeyError:                            # KeyError escapes at once
    print("KeyError not retried")           # Expected: KeyError not retried
```

---

## 🔍 Why This Works (3 lines max)
The loop calls `fn` up to `times` times; a success returns immediately, a failure sleeps then retries. A bare `raise` on the last attempt re-throws the original error with its traceback. `functools.wraps` copies name and docstring so debugging and introspection still work.
हिंदी: आख़िरी attempt पर bare `raise` original error वापस फेंकता है, और `wraps` function का नाम बचा लेता है।

---

## ⚡ Alternative Solution
```python
# Async version using asyncio.sleep (simulated flaky I/O)
import asyncio                              # event loop + sleep
import functools                            # wraps

def aretry(times: int = 3, delay: float = 0.001):   # async retry decorator factory
    def deco(fn):                           # receives the coroutine function
        @functools.wraps(fn)                # keep metadata
        async def wrapper(*a, **kw):        # async wrapper
            for i in range(times):          # loop over attempts
                try:                        # try once
                    return await fn(*a, **kw)   # await the coroutine
                except Exception:           # any error
                    if i == times - 1:      # out of attempts
                        raise               # give up
                    await asyncio.sleep(delay * 2 ** i)   # non-blocking backoff
        return wrapper                      # return wrapper
    return deco                             # return decorator

n = {"c": 0}                                # call counter
@aretry(times=3)                            # decorate
async def fetch() -> str:                   # fails once then works
    n["c"] += 1                             # count
    if n["c"] < 2:                          # first call fails
        raise ConnectionError("down")       # simulated network error
    return "data"                           # second call works

print(asyncio.run(fetch()), n["c"])         # Expected: data 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: bare except + time.sleep inside async code + swallowing the final error
def bad_retry(fn):
    def wrapper(*a, **kw):
        for _ in range(3):
            try:
                return fn(*a, **kw)
            except:              # catches KeyboardInterrupt/SystemExit too
                pass             # error silently lost; returns None after 3 failures
    return wrapper               # also: no functools.wraps

# ✅ Correct: catch specific exceptions, re-raise on the last attempt, use wraps
```

---

## 🎯 Interview Tip (1 line)
Say: "Retry only transient errors, use exponential backoff (plus jitter in production), re-raise the last error, and make the operation idempotent."

---

## 🔗 Related Questions
→ Q089 (retry decorator) | Q183 (retry API call) | Q204 (retry coroutine) | Q139 (decorator metadata) | Q166 (decorators with arguments)
