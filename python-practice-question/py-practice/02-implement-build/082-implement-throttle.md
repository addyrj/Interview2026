---

# Q082. Implement throttle
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `throttle(fn, interval)` (seconds). The wrapped function runs immediately on the first call, then calls made within `interval` seconds are ignored. After the interval, the next call runs again.

```python
t = throttle(print_msg, 0.2)
t("a"); t("b"); t("c")   # only 'a' runs
```

---

## 💡 Quick Concept (2 lines only)
Remember the time of the last executed call with `time.monotonic()`; if less than `interval` has passed, skip. Used for scroll handlers, API rate protection, button spam.
हिंदी: Throttle एक interval में सिर्फ एक बार चलने देता है, बाकी calls ignore।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools                                       # keep metadata
import threading                                       # lock + Timer (for trailing variant)
import time                                            # monotonic clock + sleep
from typing import Any, Callable                       # type hints

def throttle(fn: Callable[..., Any], interval: float) -> Callable[..., Any]:
    last = float("-inf")                               # Step 1: time of last executed call (never yet)
    lock = threading.Lock()                            # make check-and-set atomic

    @functools.wraps(fn)                               # copy name/docstring
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal last                                  # we update the outer `last`
        with lock:                                     # Step 2: one thread decides at a time
            now = time.monotonic()                     # monotonic = unaffected by system clock changes
            if now - last < interval:                  # Step 3: still inside the cool-down window?
                return None                            # ignore this call
            last = now                                 # Step 4: record this execution time
        return fn(*args, **kwargs)                     # Step 5: run outside the lock, return its result
    return wrapper                                     # Step 6: return throttled function

# ============================================
# TEST CASES
# ============================================
t = throttle(lambda m: print("ran:", m) or m, 0.2)     # prints and returns m
print(t("a"))                                          # Expected: ran: a  then  a
print(t("b"))                                          # Expected: None   (within 0.2s)
print(t("c"))                                          # Expected: None
time.sleep(0.25)                                       # wait past the interval
print(t("d"))                                          # Expected: ran: d  then  d
print(t("e"))                                          # Expected: None

calls: list[int] = []                                  # record what runs
th = throttle(calls.append, 0.12)                      # 120 ms throttle
for i in range(5):                                     # 5 calls, 50 ms apart (~250 ms total)
    th(i); time.sleep(0.05)
print("throttle calls:", calls)                        # Expected: throttle calls: [0, 3]  (timing-dependent)
```

---

## 🔍 Why This Works (3 lines max)
`last` stores when we last executed; each call compares `now - last` to the interval and returns early if it's too soon. `time.monotonic()` never goes backwards, so clock adjustments can't break it.
हिंदी: आखिरी run का समय याद रखो; interval से पहले आई calls को skip कर दो।

---

## ⚡ Alternative Solution
```python
# Leading + trailing: also run the LAST ignored call once the window ends
import threading, time                                 # Timer + clock

def throttle_trailing(fn, interval: float):
    last = float("-inf")                               # last execution time
    timer: threading.Timer | None = None               # pending trailing call

    def run(args, kwargs):
        nonlocal last, timer
        last = time.monotonic(); timer = None          # record time, clear pending
        fn(*args, **kwargs)                            # execute

    def wrapper(*args, **kwargs):
        nonlocal timer
        wait = interval - (time.monotonic() - last)    # time left in the window
        if wait <= 0:                                  # window over -> run now (leading edge)
            run(args, kwargs)
        else:                                          # inside window -> remember the latest call
            if timer: timer.cancel()                   # replace older pending call
            timer = threading.Timer(wait, run, args=(args, kwargs)); timer.start()
    return wrapper

tt = throttle_trailing(lambda m: print("t-ran:", m), 0.2)  # 200 ms
tt("1"); tt("2"); tt("3"); time.sleep(0.4)             # Expected: t-ran: 1  then  t-ran: 3
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: confusing throttle with debounce (5 calls in a quick burst)
# debounce(fn, 0.1) -> waits for silence -> runs ONCE at the end:   [4]
# throttle(fn, 0.12) -> runs at the START of each window:           [0, 3]  (50 ms gaps)
# (measured on CPython 3.13; exact result depends on timing)

# ❌ Also wrong: using time.time() — it can jump (NTP/DST) and break the interval
# ✅ Correct: time.monotonic()
```

---

## 🎯 Interview Tip (1 line)
Say: "Throttle = max once per window (rate limit); debounce = once after silence" — then offer the leading/trailing variants and mention monotonic().

---

## 🔗 Related Questions
→ Q081 (debounce) | Q142 (complete throttle) | Q186 (token bucket) | Q230 (rate limiting endpoint)
