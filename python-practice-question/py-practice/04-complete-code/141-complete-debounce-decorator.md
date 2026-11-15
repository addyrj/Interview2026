---

# Q141. Complete Debounce Decorator
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks (`____`) so that the decorated function runs only once, `delay` seconds after the LAST call.

```python
import threading
from functools import wraps
from typing import Any, Callable


def debounce(delay: float) -> Callable:
    def decorator(fn: Callable) -> Callable:
        timer: threading.Timer | None = None      # holds the pending timer

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            ____ timer                             # BLANK 1: allow rebinding outer variable
            if timer is not None:
                timer.____()                       # BLANK 2: cancel the previous pending call
            timer = threading.Timer(delay, ____, args, kwargs)  # BLANK 3: what should run later?
            timer.start()                          # start the new countdown
        return wrapper
    return decorator
```

---

## 💡 Quick Concept (2 lines only)
Debounce cancels the pending timer on every call and starts a fresh one, so only the last call survives the quiet period.
हिंदी: हर call पर पुराना timer cancel होता है, इसलिए सिर्फ आखिरी call ही delay के बाद चलती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import threading                                   # Timer runs fn later in a thread
import time                                        # used only in the tests
from functools import wraps                        # keep fn's name/docstring
from typing import Any, Callable


def debounce(delay: float) -> Callable:            # decorator factory: takes the delay in seconds
    def decorator(fn: Callable) -> Callable:       # receives the real function
        timer: threading.Timer | None = None       # Step 1: pending timer lives in the closure

        @wraps(fn)                                 # Step 2: preserve metadata
        def wrapper(*args: Any, **kwargs: Any) -> None:
            nonlocal timer                         # BLANK 1: rebind the closure variable
            if timer is not None:                  # a call is already waiting?
                timer.cancel()                     # BLANK 2: drop it
            timer = threading.Timer(delay, fn, args, kwargs)  # BLANK 3: schedule fn itself
            timer.start()                          # Step 3: start the new countdown
        return wrapper                             # return the debounced version
    return decorator                               # return the decorator


# ============================================
# TEST CASES
# ============================================
@debounce(0.1)                                     # wait 100 ms of silence
def log(msg: str) -> None:
    print("run:", msg)                             # show which call actually ran

log("a")                                           # timer set
log("b")                                           # 'a' cancelled
log("c")                                           # 'b' cancelled
time.sleep(0.3)                                    # wait for the timer to fire
# Expected: run: c

log("d")                                           # a fresh burst
time.sleep(0.3)                                    # let it fire
# Expected: run: d
print(log.__name__)                                # Expected: log  (thanks to @wraps)
```

---

## 🔍 Why This Works (3 lines max)
`nonlocal` lets the wrapper reassign `timer`; `cancel()` kills the previous pending call, and `Timer(delay, fn, args, kwargs)` runs `fn` once after the delay. Only the last timer is never cancelled.
हिंदी: `nonlocal` से closure का timer बदलता है, `cancel()` पुरानी call रोकता है — आखिरी timer ही चलता है।

---

## ⚡ Alternative Solution
```python
# Async version: cancel the previous asyncio task instead of a Timer
import asyncio                                     # event loop + sleep
from functools import wraps
from typing import Any, Awaitable, Callable


def adebounce(delay: float) -> Callable:           # async debounce factory
    def decorator(fn: Callable[..., Awaitable]) -> Callable:
        task: asyncio.Task | None = None           # pending task

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            nonlocal task                          # rebind closure variable
            if task and not task.done():           # still waiting?
                task.cancel()                      # cancel it

            async def runner() -> None:            # sleep then call
                await asyncio.sleep(delay)         # simulated quiet period
                await fn(*args, **kwargs)          # run the real coroutine

            task = asyncio.get_running_loop().create_task(runner())  # schedule it
        return wrapper
    return decorator


@adebounce(0.1)
async def search(q: str) -> None:
    print("search:", q)                            # shows the surviving call


async def main() -> None:
    search("p"); search("py"); search("pyt")       # rapid typing
    await asyncio.sleep(0.3)                       # wait for quiet period

asyncio.run(main())                                # Expected: search: pyt
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no cancel() -> every call still fires (that is just a delay, not debounce)
# def wrapper(*a, **k):
#     threading.Timer(delay, fn, a, k).start()     # a, b, c ALL run
#
# ❌ Also wrong: forgetting `nonlocal` -> UnboundLocalError on `if timer is not None`
#
# ✅ Correct: nonlocal + cancel previous + start new (as in the solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce = trailing edge, reset timer on each call; throttle = at most once per interval — and mention the timer runs in another thread."

---

## 🔗 Related Questions
→ Q081 (implement debounce) | Q142 (throttle) | Q181 (search with debounce) | Q214 (debounce async function)
