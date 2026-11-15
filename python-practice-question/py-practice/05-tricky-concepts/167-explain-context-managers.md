---

# Q167. Explain Context Managers
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
How does the `with` statement work? Write a context manager as a class and with `contextlib.contextmanager`, and show how `__exit__` can suppress exceptions.

---

## 💡 Quick Concept (2 lines only)
`with obj as x:` calls `obj.__enter__()` at the start and `obj.__exit__()` at the end, even if an exception happens, guaranteeing cleanup.
हिंदी: `with` शुरू में `__enter__` और ख़त्म होने पर `__exit__` चलाता है — error आए तब भी cleanup पक्का होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time                                        # Step 1: for a timer example

class Timer:                                       # Step 2: class-based context manager
    def __enter__(self) -> "Timer":                # runs when entering `with`
        self.start = time.perf_counter()           # record the start time
        print("enter")                             # show the order
        return self                                # value bound by `as t`

    def __exit__(self, exc_type, exc, tb) -> bool: # runs on leaving `with` (always)
        self.elapsed = time.perf_counter() - self.start   # compute duration
        print("exit", exc_type.__name__ if exc_type else None)   # which error (if any)
        return exc_type is ZeroDivisionError       # True = SUPPRESS the exception, False = propagate

# ============================================
# TEST CASES
# ============================================
with Timer() as t:                                 # normal run
    print("body")                                  # Expected order: enter, body, exit None
print(t.elapsed >= 0)                              # Expected: True

with Timer():                                      # ZeroDivisionError is suppressed by __exit__
    1 / 0                                          # raises inside the block
print("continued after suppressed error")          # Expected: exit ZeroDivisionError, then this line

try:                                               # other exceptions still propagate
    with Timer():                                  # ValueError is not suppressed
        raise ValueError("bad")                    # raised inside the block
except ValueError as e:                            # caught outside
    print("caught", e)                             # Expected: exit ValueError, then: caught bad
```

---

## 🔍 Why This Works (3 lines max)
`__exit__` receives the exception type, value and traceback (all `None` on success). Returning a truthy value tells Python the error was handled and must not propagate; returning `False`/`None` lets it continue. Cleanup in `__exit__` runs in both cases.
हिंदी: `__exit__` में True return करने पर exception दब जाता है, वरना वह आगे जाता है।

---

## ⚡ Alternative Solution
```python
# Generator-based context managers with contextlib (less boilerplate)
from contextlib import contextmanager, suppress, ExitStack   # helpers

@contextmanager                                    # turn a generator into a context manager
def tag(name: str):                                # takes an argument
    print(f"<{name}>")                            # setup = __enter__
    try:                                           # try/finally gives guaranteed cleanup
        yield name                                 # value for `as`; body runs here
    finally:                                       # always runs
        print(f"</{name}>")                        # teardown = __exit__

with tag("p") as n:                                # use it
    print("text", n)                               # Expected: <p> / text p / </p>

with suppress(FileNotFoundError):                  # built-in "ignore this error"
    open("/definitely/missing.txt")                # raises FileNotFoundError
print("still running")                             # Expected: still running

with ExitStack() as stack:                         # manage a dynamic number of contexts
    stack.callback(print, "cleanup 1")             # registered first -> runs last
    stack.callback(print, "cleanup 2")             # registered last -> runs first
    print("working")                               # Expected: working, cleanup 2, cleanup 1
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: @contextmanager without try/finally -> cleanup is skipped when the body raises
from contextlib import contextmanager

@contextmanager
def bad():
    print("setup")
    yield
    print("cleanup")        # NOT executed if the with-body raises

# ✅ Correct:
@contextmanager
def good():
    print("setup")
    try:
        yield
    finally:
        print("cleanup")    # always executed
```

---

## 🎯 Interview Tip (1 line)
Say: "Context managers guarantee cleanup (files, locks, DB sessions); write them as `__enter__/__exit__` or `@contextmanager` with try/finally."

---

## 🔗 Related Questions
→ Q045 (__exit__ suppression) | Q119 (implement context manager) | Q132 (file not closed) | Q146 (complete context manager) | Q253 (contextlib) | Q305 (with statement)
