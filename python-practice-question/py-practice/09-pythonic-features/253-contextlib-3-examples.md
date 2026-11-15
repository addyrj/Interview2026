---

# Q253. contextlib — 3 Examples
# Category: PYTHONIC + MODERN PYTHON FEATURES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 3 practical uses of the `contextlib` module: (1) `@contextmanager` to write a context manager as a generator, (2) `suppress` to ignore specific exceptions, (3) `ExitStack` to manage a dynamic number of resources.

```python
# Goal: no __enter__/__exit__ class boilerplate.
# with tag("b"):  -> <b> ... </b>
# with suppress(KeyError): ...
# with ExitStack() as stack: open N things, all closed automatically
```

---

## 💡 Quick Concept (2 lines only)
`@contextmanager` turns a generator with one `yield` into a `with` block: code before `yield` = enter, after = exit. Always wrap `yield` in `try/finally` so cleanup runs even on error.
हिंदी: `contextmanager` generator को `with` block बना देता है — yield से पहले setup, बाद में cleanup।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from contextlib import contextmanager, suppress, ExitStack  # import the 3 tools
from collections.abc import Iterator                        # type hint for generators

# --- Example 1: @contextmanager ---
@contextmanager                                  # turns the generator into a context manager
def tag(name: str) -> Iterator[None]:
    print(f"<{name}>")                           # runs on __enter__
    try:
        yield                                    # body of the with-block runs here
    finally:
        print(f"</{name}>")                      # always runs on exit, even on error

# --- Example 2: suppress ---
def safe_get(d: dict[str, int], key: str) -> int | None:
    result = None                                # default when the key is missing
    with suppress(KeyError):                     # swallow ONLY KeyError
        result = d[key]                          # raises KeyError if missing -> ignored
    return result                                # None if suppressed

# --- Example 3: ExitStack ---
@contextmanager
def resource(name: str) -> Iterator[str]:
    print(f"open {name}")                        # acquire
    try:
        yield name                               # hand resource to the caller
    finally:
        print(f"close {name}")                   # release

# ============================================
# TEST CASES
# ============================================
with tag("b"):                                   # test 1
    print("hello")                               # body

print(safe_get({"a": 1}, "a"))                   # key exists
print(safe_get({"a": 1}, "z"))                   # key missing

with ExitStack() as stack:                       # test 3: N resources, decided at runtime
    names = [stack.enter_context(resource(n)) for n in ("a", "b", "c")]  # enter each one
    print("using", names)                        # all three are open here

# Output:
# <b>
# hello
# </b>
# 1
# None
# open a
# open b
# open c
# using ['a', 'b', 'c']
# close c
# close b
# close a
```

---

## 🔍 Why This Works (3 lines max)
`@contextmanager` wraps the generator: `__enter__` runs it to the `yield`, `__exit__` resumes it (throwing the exception in if one occurred). `suppress(E)` is just `try/except E: pass` as a `with`. `ExitStack` keeps a stack of exit callbacks and unwinds them in LIFO order (c, b, a).
हिंदी: ExitStack जितने resources खोले उन्हें उल्टे क्रम (LIFO) में अपने-आप बंद करता है।

---

## ⚡ Alternative Solution
```python
# redirect_stdout + closing + nullcontext
import io                                        # in-memory text buffer
from contextlib import redirect_stdout, nullcontext  # capture print / optional context

buf = io.StringIO()                              # buffer to capture output
with redirect_stdout(buf):                       # temporarily send print() into buf
    print("captured")                            # not shown on the terminal
print(repr(buf.getvalue()))                      # inspect what was captured

def run(lock=None) -> str:
    with lock or nullcontext():                  # no lock? use a do-nothing context
        return "ran"                             # same code path either way

print(run())                                     # without a lock

# Output:
# 'captured\n'
# ran
```

---

## ⚠️ Common Mistake
```python
# NOT RUN (shows the bug; the ✅ version is the same as the verified solution)
# ❌ Wrong: no try/finally around yield -> cleanup skipped on exception
@contextmanager
def tag(name):
    print(f"<{name}>")
    yield
    print(f"</{name}>")      # never runs if the with-body raises!

# ✅ Correct: wrap yield in try/finally
@contextmanager
def tag(name):
    print(f"<{name}>")
    try:
        yield
    finally:
        print(f"</{name}>")  # always runs
```

---

## 🎯 Interview Tip (1 line)
Say: "`@contextmanager` for simple cases, a class with `__enter__/__exit__` when I need state or reuse, and `ExitStack` when the number of resources is dynamic."

---

## 🔗 Related Questions
→ Q045 (with + __exit__ suppression) | Q119 (context manager class) | Q146 (complete context manager) | Q167 (explain context managers)
