---

# Q305. The with Statement
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What does the `with` statement do? Show how it guarantees cleanup and how to build your own context manager two ways.

---

## 💡 Quick Concept (2 lines only)
`with` calls `__enter__` on entry and `__exit__` on exit, even if an exception occurs - a safe replacement for try/finally.
हिंदी: `with` शुरू में `__enter__` और अंत में `__exit__` चलाता है — error आए तब भी cleanup होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Managed:  # Step 1: class-based context manager
    def __enter__(self) -> "Managed":
        print("enter")  # setup runs first
        return self  # value bound by 'as'

    def __exit__(self, exc_type, exc, tb) -> bool:
        print("exit", exc_type.__name__ if exc_type else None)  # cleanup always runs
        return False  # False -> do not suppress exceptions


# ============================================
# TEST CASES
# ============================================
with Managed() as m:  # normal run
    print("body")  # Expected: enter / body / exit None

try:
    with Managed():  # body raises
        raise ValueError("boom")  # exception inside
except ValueError as e:
    print("caught", e)  # Expected: enter / exit ValueError / caught boom

import io  # in-memory file
with io.StringIO() as buf:  # built-in context managers close themselves
    buf.write("hi")  # use it
print(buf.closed)  # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
`with obj as x:` runs `obj.__enter__()`, binds the result, runs the body, then always calls `obj.__exit__(type, value, tb)`. If `__exit__` returns True the exception is suppressed; otherwise it propagates.
हिंदी: `__exit__` True लौटाए तो exception दब जाता है, वरना आगे बढ़ता है।

---

## ⚡ Alternative Solution
```python
from contextlib import contextmanager, suppress  # helpers


@contextmanager  # generator-based context manager
def managed():
    print("enter")  # before yield = __enter__
    try:
        yield "resource"  # value for 'as'
    finally:
        print("exit")  # after yield = __exit__ (always runs)


with managed() as r:  # use it
    print(r)  # Expected: enter / resource / exit

with suppress(ZeroDivisionError):  # ignore a specific error
    1 / 0  # raises, but is suppressed
print("continued")  # Expected: continued
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to close, or closing only on success
f = open("/dev/null")  # may leak if an error occurs before close()
data = f.read()
f.close()

# ✅ Correct: with guarantees close() even on exceptions
with open("/dev/null") as f:  # auto-closed
    data = f.read()
print(f.closed)  # Expected: True
```

---

## 🎯 Interview Tip (1 line)
Say: "with = guaranteed setup/teardown via __enter__/__exit__; I write them with @contextmanager for brevity."

---

## 🔗 Related Questions
→ Q045 (with and __exit__ suppression) | Q119 (implement context manager) | Q167 (context managers) | Q253 (contextlib)
