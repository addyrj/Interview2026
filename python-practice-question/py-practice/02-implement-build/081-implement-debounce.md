---

# Q081. Implement debounce
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `debounce(fn, delay)` (delay in seconds). The wrapped function must run only after `delay` seconds have passed since the LAST call; every new call resets the timer. Add a `.cancel()` method.

```python
search = debounce(call_api, 0.3)
search("p"); search("py"); search("pyt")
# call_api("pyt") runs once, 0.3s after the last call
```

---

## 💡 Quick Concept (2 lines only)
Keep one pending `threading.Timer`; on each call cancel it and start a fresh one — only the last call survives. Used for search-as-you-type, auto-save, resize handlers.
हिंदी: हर call पर पुराना timer cancel करके नया लगाओ — सिर्फ आखिरी call चलती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools                                       # wraps keeps fn's name/docstring
import threading                                       # Timer runs fn after a delay
import time                                            # sleep for the demo
from typing import Any, Callable                       # type hints

def debounce(fn: Callable[..., Any], delay: float) -> Callable[..., None]:
    timer: threading.Timer | None = None               # Step 1: the pending timer (None = nothing scheduled)
    lock = threading.Lock()                            # protects `timer` across threads

    @functools.wraps(fn)                               # Step 2: copy metadata from fn
    def wrapper(*args: Any, **kwargs: Any) -> None:
        nonlocal timer                                 # we rebind the outer `timer`
        with lock:                                     # one thread at a time
            if timer is not None:                      # Step 3: a call is already waiting?
                timer.cancel()                         # drop it — it will never fire
            timer = threading.Timer(delay, fn, args=args, kwargs=kwargs)  # Step 4: schedule the new call
            timer.start()                              # start the countdown

    def cancel() -> None:                              # Step 5: manual cancel
        nonlocal timer
        with lock:
            if timer is not None:
                timer.cancel()                         # stop the pending call
                timer = None

    wrapper.cancel = cancel  # type: ignore[attr-defined]  # attach cancel() to the wrapper
    return wrapper                                     # Step 6: return the debounced function

# ============================================
# TEST CASES
# ============================================
log = debounce(lambda msg: print("fired:", msg), 0.2)  # 200 ms debounce
log("a"); log("b"); log("c")                           # three rapid calls
print("before delay")                                  # Expected: before delay   (nothing fired yet)
time.sleep(0.4)                                        # Expected: fired: c       (only the last call)
log("d"); time.sleep(0.1); log("e"); time.sleep(0.4)   # Expected: fired: e       ('d' was reset by 'e')
log("x"); log.cancel(); time.sleep(0.4)                # Expected: (nothing)      cancelled
print("done")                                          # Expected: done
```

---

## 🔍 Why This Works (3 lines max)
Each call cancels the previous `Timer` and creates a new one, so only the final call's timer is allowed to finish. `args`/`kwargs` are captured per call, and the lock avoids two threads racing on `timer`. Note: `fn` runs in the Timer's thread.
हिंदी: हर call पिछला Timer रोकती है और नया बनाती है; fn अलग thread में चलता है।

---

## ⚡ Alternative Solution
```python
# asyncio version: cancel the previous sleeping task (no threads)
import asyncio                                         # async tools

def debounce_async(fn, delay: float):
    task: asyncio.Task | None = None                   # pending task
    def wrapper(*args, **kwargs):                      # call this from inside the event loop
        nonlocal task
        if task is not None and not task.done():       # previous call still sleeping?
            task.cancel()                              # cancel it
        async def runner():
            await asyncio.sleep(delay)                 # wait for quiet period
            fn(*args, **kwargs)                        # then run the function
        task = asyncio.get_running_loop().create_task(runner())  # schedule new runner
    return wrapper

async def main():
    s = debounce_async(lambda q: print("search:", q), 0.1)  # 100 ms debounce
    for q in ["p", "py", "pyt"]:                       # user types quickly
        s(q); await asyncio.sleep(0.03)                # 30 ms between keystrokes
    await asyncio.sleep(0.3)                           # wait so the last call can fire
asyncio.run(main())                                    # Expected: search: pyt
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: starts a Timer per call but never cancels the old one (that is a delay, not a debounce)
import threading, time
def bad(fn, delay):
    def w(*a):
        threading.Timer(delay, fn, args=a).start()     # ❌ every call still fires
    return w

b = bad(lambda m: print("bad fired:", m), 0.1)         # wrap a printer
b("a"); b("b"); b("c"); time.sleep(0.3)                # Output: bad fired: a / bad fired: b / bad fired: c
# ✅ Correct: keep the Timer in a variable and .cancel() it before scheduling the next one
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce = trailing-edge, reset on every call; throttle = at most once per interval" and mention that Timer callbacks run on another thread.

---

## 🔗 Related Questions
→ Q082 (throttle) | Q083 (memoize) | Q141 (complete debounce) | Q181 (search with debounce) | Q214 (debounce async)
