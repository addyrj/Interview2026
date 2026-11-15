---

# Q119. Implement a context manager class
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write a `Timer` class usable with `with Timer("x") as t:` that prints on enter/exit, records `elapsed`, always runs cleanup (even on error), and suppresses only `ValueError`.

```python
with Timer("job") as t:
    do_work()
print(t.elapsed)
```

---

## 💡 Quick Concept (2 lines only)
`__enter__` sets up and returns the `as` value; `__exit__(exc_type, exc, tb)` always runs, and returning `True` suppresses the exception.
हिंदी: `__exit__` हमेशा चलता है; `True` return करने पर exception दब जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time                                              # for perf_counter
from types import TracebackType                          # type hint

class Timer:
    def __init__(self, label: str) -> None:
        self.label = label                               # name for printing
        self.elapsed = 0.0                               # filled on exit

    def __enter__(self) -> "Timer":
        print(f"[{self.label}] enter")                   # Step 1: setup
        self._start = time.perf_counter()                # start clock
        return self                                      # value bound by 'as'

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None,
                 tb: TracebackType | None) -> bool:
        self.elapsed = time.perf_counter() - self._start # Step 2: always runs, even on error
        print(f"[{self.label}] exit, exc={exc_type.__name__ if exc_type else None}")
        return exc_type is ValueError                    # Step 3: True = suppress ValueError only

# ============================================
# TEST CASES
# ============================================
with Timer("ok") as t:
    total = sum(range(1000))                             # normal body
    print("inside", total)
print("elapsed >= 0:", t.elapsed >= 0)
# Expected:
# [ok] enter
# inside 499500
# [ok] exit, exc=None
# elapsed >= 0: True

with Timer("suppressed"):
    raise ValueError("boom")                             # swallowed by __exit__
print("after suppressed")
# Expected: [suppressed] enter / [suppressed] exit, exc=ValueError / after suppressed

try:
    with Timer("propagates"):
        raise KeyError("k")                              # not suppressed
except KeyError as e:
    print("caught outside:", repr(e))
# Expected: [propagates] enter / [propagates] exit, exc=KeyError / caught outside: KeyError('k')
```

---

## 🔍 Why This Works (3 lines max)
`with` calls `__enter__`, runs the body, then ALWAYS calls `__exit__` with the exception details (or `None, None, None`). A truthy return from `__exit__` swallows the exception; falsy lets it propagate.
हिंदी: `with` body के बाद हमेशा `__exit__` बुलाता है — error हो या न हो।

---

## ⚡ Alternative Solution
```python
# More Pythonic: generator + contextlib.contextmanager
from contextlib import contextmanager                    # decorator
import time

@contextmanager
def timer(label: str):
    print(f"[{label}] enter")                            # setup (before yield)
    start = time.perf_counter()                          # start clock
    try:
        yield                                            # body of 'with' runs here
    finally:                                             # always cleanup
        print(f"[{label}] exit")

with timer("gen"):
    print("inside")
# Output: [gen] enter / inside / [gen] exit
try:
    with timer("gen-err"):
        raise RuntimeError("x")                          # propagates (no except inside)
except RuntimeError:
    print("RuntimeError propagated")
# Output: [gen-err] enter / [gen-err] exit / RuntimeError propagated
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: __exit__ that returns True unconditionally -> swallows EVERY exception (even SystemExit)
class Bad:
    def __enter__(self): return self
    def __exit__(self, *a): return True       # hides all bugs!
with Bad():
    raise SystemExit                          # silently swallowed
print("reached?")                             # Output: reached?  (verified: program continues)

# ✅ Correct: return True only for the specific exceptions you intend to handle
```

---

## 🎯 Interview Tip (1 line)
Say: "`__enter__`/`__exit__` guarantee cleanup; return True only to suppress deliberately, and `@contextmanager` is the short form for simple cases."

---

## 🔗 Related Questions
→ Q045 (with and __exit__ suppression) | Q146 (complete context manager) | Q167 (context managers) | Q253 (contextlib)
