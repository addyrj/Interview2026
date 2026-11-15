---

# Q090. Implement Timer/Sleep Utility Decorator
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write a `@timer` decorator that prints how long a function took, even if it raises. Then write a `@sleep_for(seconds)` decorator that delays each call. Make timer work for async functions too.

```python
@timer
def slow(n): time.sleep(0.2); return n * 2
slow(21)   # prints "slow took 0.20s", returns 42
```

---

## 💡 Quick Concept (2 lines only)
Use `time.perf_counter()` (monotonic, high resolution) around the call and a `try/finally` so timing is always reported. Async functions need an `async def` wrapper that awaits.
हिंदी: Timer function से पहले और बाद का समय नापता है — finally से error पर भी print होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools  # wraps
import time  # perf_counter, sleep
from typing import Callable  # type hint


def timer(fn: Callable) -> Callable:  # decorator takes the function
    @functools.wraps(fn)  # keep name/docstring
    def wrapper(*args, **kwargs):  # accept any arguments
        start = time.perf_counter()  # Step 1: start the clock
        try:
            return fn(*args, **kwargs)  # Step 2: run the function
        finally:  # Step 3: runs on success AND on exception
            elapsed = time.perf_counter() - start  # elapsed seconds
            print(f"{fn.__name__} took {elapsed:.2f}s")  # report
    return wrapper  # return wrapped function


def sleep_for(seconds: float) -> Callable:  # factory with an argument
    def deco(fn: Callable) -> Callable:  # the real decorator
        @functools.wraps(fn)
        def w(*a, **k):
            time.sleep(seconds)  # delay before each call
            return fn(*a, **k)  # then run
        return w
    return deco


# ============================================
# TEST CASES
# ============================================
@timer
def slow(n: int) -> int:  # sample function
    time.sleep(0.2)  # simulate work
    return n * 2  # result


print(slow(21))  # Expected: slow took 0.20s  then  42   (timings vary slightly)
print(slow.__name__)  # Expected: slow


@sleep_for(0.1)
def hi() -> str:  # delayed function
    return "hi"  # value


s = time.perf_counter()  # measure
print(hi(), round(time.perf_counter() - s, 1))  # Expected: hi 0.1
```

---

## 🔍 Why This Works (3 lines max)
`perf_counter` is monotonic (unaffected by system clock changes) and `finally` guarantees the report even when the function raises. `@wraps` keeps `__name__` so logs show the real function.
हिंदी: perf_counter सही माप देता है और finally हर हाल में चलता है।

---

## ⚡ Alternative Solution
```python
import asyncio  # async support
from contextlib import contextmanager  # context-manager timer


def atimer(fn):  # async version of timer
    @functools.wraps(fn)
    async def w(*a, **k):  # must be async to await fn
        s = time.perf_counter()
        try:
            return await fn(*a, **k)  # await the coroutine
        finally:
            print(f"{fn.__name__} took {time.perf_counter() - s:.2f}s")
    return w


@atimer
async def aslow():
    await asyncio.sleep(0.1)  # simulated I/O
    return "done"


print(asyncio.run(aslow()))  # Expected: aslow took 0.10s  then  done


@contextmanager
def timed(label):  # time any block, not just functions
    s = time.perf_counter()
    yield  # body of the with-block runs here
    print(f"{label}: {time.perf_counter() - s:.2f}s")


with timed("block"):  # Expected: block: 0.10s
    time.sleep(0.1)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: sync timer on an async function — it times only coroutine CREATION
def bad_timer(fn):
    def w(*a, **k):
        s = time.perf_counter()
        r = fn(*a, **k)  # ❌ returns an un-awaited coroutine instantly
        print(f"took {time.perf_counter() - s:.2f}s")
        return r
    return w

# Decorating `async def a2(): await asyncio.sleep(0.1)` and awaiting it prints
# "took 0.00s" even though it really took ~0.1s.

# ✅ Correct: async def wrapper + await fn(...), and use perf_counter (not time.time)
```

---

## 🎯 Interview Tip (1 line)
Say: "perf_counter for durations, try/finally so errors are timed too, @wraps for metadata, and a separate async wrapper because awaiting is required."

---

## 🔗 Related Questions
→ Q089 (retry with backoff) | Q276 (timeit) | Q139 (decorator losing metadata) | Q205 (timeout a coroutine)
