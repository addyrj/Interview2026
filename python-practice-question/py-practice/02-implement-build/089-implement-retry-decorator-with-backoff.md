---

# Q089. Implement Retry Decorator with Backoff
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Write `@retry(max_attempts, base_delay, backoff, exceptions)` that re-runs a failing function, sleeping longer after each failure (exponential backoff). Only listed exception types are retried; after the last attempt the original exception is re-raised.

```python
@retry(max_attempts=4, base_delay=0.1)
def flaky(): ...   # delays: 0.1s, 0.2s, 0.4s
```

---

## 💡 Quick Concept (2 lines only)
A decorator *factory* (retry(...)) returns a decorator, which returns a wrapper with a loop. Delay is multiplied by `backoff` after each failure.
हिंदी: Retry फेल होने पर बढ़ते delay के साथ दोबारा कोशिश करता है — आख़िर में original error raise होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools  # for wraps
import time  # for sleep
from typing import Callable  # type hint


def retry(max_attempts: int = 3, base_delay: float = 0.1, backoff: float = 2.0,
          exceptions: tuple[type[BaseException], ...] = (Exception,)) -> Callable:  # Step 1: factory with settings
    def decorator(fn: Callable) -> Callable:  # Step 2: real decorator
        @functools.wraps(fn)  # keep metadata
        def wrapper(*args, **kwargs):  # Step 3: wrapper runs the loop
            delay = base_delay  # current wait time
            for attempt in range(1, max_attempts + 1):  # attempts 1..max
                try:
                    return fn(*args, **kwargs)  # success -> return immediately
                except exceptions as e:  # only retry the listed errors
                    if attempt == max_attempts:  # out of attempts
                        raise  # re-raise the original error
                    print(f"attempt {attempt} failed: {e}; sleeping {delay:.2f}s")  # log
                    time.sleep(delay)  # wait before retrying
                    delay *= backoff  # exponential growth
        return wrapper  # return wrapped function
    return decorator  # return decorator


# ============================================
# TEST CASES
# ============================================
calls = {"n": 0}  # count invocations


@retry(max_attempts=4, base_delay=0.1)
def flaky() -> str:  # fails twice, then succeeds
    calls["n"] += 1  # count the call
    if calls["n"] < 3:  # first two calls fail
        raise ConnectionError(f"fail #{calls['n']}")  # simulated failure
    return "ok"  # third call works


print(flaky())
# Expected: attempt 1 failed: fail #1; sleeping 0.10s
#           attempt 2 failed: fail #2; sleeping 0.20s
#           ok
print(calls["n"])  # Expected: 3  (total time ~0.3s)


@retry(max_attempts=2, base_delay=0.01)
def always_fail():  # never works
    raise ValueError("nope")  # always raises


try:
    always_fail()  # Expected: attempt 1 failed: nope; sleeping 0.01s
except ValueError as e:
    print("gave up:", e)  # Expected: gave up: nope


@retry(max_attempts=3, base_delay=0.01, exceptions=(ConnectionError,))
def wrong_type():  # KeyError is not in the retry list
    raise KeyError("k")  # raised on first attempt


try:
    wrong_type()  # no retries, no log line
except KeyError as e:
    print("not retried:", e)  # Expected: not retried: 'k'
```

---

## 🔍 Why This Works (3 lines max)
Three layers: factory -> decorator -> wrapper; the loop catches only `exceptions` and re-raises on the last attempt so callers see the real error. `delay *= backoff` gives 0.1, 0.2, 0.4...
Production: add jitter (`random.uniform`) so clients don't retry in sync.
हिंदी: तीन layers — factory, decorator, wrapper; सिर्फ चुने हुए errors retry होते हैं।

---

## ⚡ Alternative Solution
```python
import asyncio  # async version
import functools  # wraps


def aretry(max_attempts=3, base_delay=0.05, backoff=2.0):  # async retry
    def deco(fn):
        @functools.wraps(fn)
        async def w(*a, **k):  # wrapper is a coroutine function
            d = base_delay  # initial delay
            for i in range(1, max_attempts + 1):
                try:
                    return await fn(*a, **k)  # await the real coroutine
                except Exception:
                    if i == max_attempts:
                        raise  # give up
                    await asyncio.sleep(d)  # non-blocking wait (NOT time.sleep)
                    d *= backoff  # grow delay
        return w
    return deco


n = {"c": 0}  # call counter


@aretry()
async def aflaky():  # fails twice
    n["c"] += 1
    if n["c"] < 3:
        raise RuntimeError
    return "async ok"


print(asyncio.run(aflaky()), n["c"])  # Expected: async ok 3
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using @retry without parentheses (it is a factory)
@retry
def f(): ...
# f is now the inner `decorator` function, not your function -> silent bug:
print(f)  # <function retry.<locals>.decorator at 0x...>  (address varies)

# ❌ Also wrong: `except Exception: pass` / time.sleep inside async code
# ✅ Correct: @retry()  and  await asyncio.sleep(...) in async code
```

---

## 🎯 Interview Tip (1 line)
Say: "Exponential backoff plus jitter, retry only transient errors, cap attempts, re-raise the original, and use asyncio.sleep in async code."

---

## 🔗 Related Questions
→ Q157 (complete retry logic) | Q183 (retry API call) | Q204 (retry a coroutine) | Q090 (timer decorator)
