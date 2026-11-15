---

# Q142. Complete Throttle Decorator
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks so the decorated function runs at most once per `interval` seconds (leading edge: first call runs immediately, calls inside the window are ignored).

```python
import time
from functools import wraps
from typing import Any, Callable


def throttle(interval: float) -> Callable:
    def decorator(fn: Callable) -> Callable:
        last_call = float("-inf")                  # time of last real call

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ____ last_call                         # BLANK 1
            now = time.____()                      # BLANK 2: clock that never goes backwards
            if now - last_call ____ interval:      # BLANK 3: comparison operator
                last_call = now
                return fn(*args, **kwargs)
            return None                            # ignored call
        return wrapper
    return decorator
```

---

## 💡 Quick Concept (2 lines only)
Throttle remembers when `fn` last ran and ignores calls until `interval` has passed — it limits the rate, unlike debounce which waits for silence.
हिंदी: Throttle पिछली run का समय याद रखता है — interval पूरा होने से पहले की calls ignore हो जाती हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time                                        # monotonic clock + sleep
from functools import wraps                        # keep metadata
from typing import Any, Callable


def throttle(interval: float) -> Callable:         # factory: interval in seconds
    def decorator(fn: Callable) -> Callable:       # receives the function
        last_call = float("-inf")                  # Step 1: nothing has run yet

        @wraps(fn)                                 # Step 2: preserve metadata
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal last_call                     # BLANK 1: we rebind last_call
            now = time.monotonic()                 # BLANK 2: monotonic is immune to clock changes
            if now - last_call >= interval:        # BLANK 3: window has passed?
                last_call = now                    # Step 3: record this run
                return fn(*args, **kwargs)         # run the real function
            return None                            # inside the window -> ignored
        return wrapper
    return decorator


# ============================================
# TEST CASES
# ============================================
calls: list[str] = []                              # collect which calls ran

@throttle(0.1)                                     # at most one run per 100 ms
def track(x: str) -> None:
    calls.append(x)                                # record the argument

track("a")                                         # runs (first call)
track("b")                                         # ignored (too soon)
track("c")                                         # ignored (too soon)
time.sleep(0.15)                                   # window passes
track("d")                                         # runs again
print(calls)                                       # Expected: ['a', 'd']
```

---

## 🔍 Why This Works (3 lines max)
`last_call` starts at `-inf`, so the first call always passes. Each allowed call updates it; calls closer than `interval` return `None`. `time.monotonic()` avoids bugs when the system clock is adjusted.
हिंदी: पहली call हमेशा चलती है, फिर interval से पहले की calls skip होती हैं — `monotonic` घड़ी बदलने से safe है।

---

## ⚡ Alternative Solution
```python
# Class-based throttle that also exposes how many calls were dropped
import time
from typing import Any, Callable


class Throttle:
    def __init__(self, fn: Callable, interval: float) -> None:
        self.fn = fn                               # wrapped function
        self.interval = interval                   # min gap between runs
        self.last = float("-inf")                  # last run time
        self.dropped = 0                           # counter of ignored calls

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        now = time.monotonic()                     # current time
        if now - self.last >= self.interval:       # allowed?
            self.last = now                        # update
            return self.fn(*args, **kwargs)        # run
        self.dropped += 1                          # count the ignored call
        return None

t = Throttle(lambda: "ok", 0.1)                    # wrap a lambda
print(t(), t(), t())                               # Expected: ok None None
print(t.dropped)                                   # Expected: 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: time.time() can jump (NTP / manual change) and break the window
#    now = time.time()
# ❌ Wrong: using `>` and initialising last_call = 0 -> the very first call may be dropped
#    on a freshly booted machine where monotonic() < interval
# ✅ Correct: time.monotonic() + last_call = -inf + `>=`
```

---

## 🎯 Interview Tip (1 line)
Say: "Throttle = rate limit (leading edge); debounce = wait for silence; use monotonic time, and a token bucket if bursts are allowed."

---

## 🔗 Related Questions
→ Q082 (implement throttle) | Q141 (debounce) | Q186 (token bucket) | Q230 (rate limiting endpoint)
