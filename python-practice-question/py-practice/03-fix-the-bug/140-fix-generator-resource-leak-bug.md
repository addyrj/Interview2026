---

# Q140. Fix Generator Resource Leak Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
This generator opens a resource and releases it after the loop. If the consumer stops early (only reads the first line, or crashes), the "close" step never runs. Find and fix the bug.

```python
# BUGGY CODE:
events: list[str] = []                  # records open/close for the demo

def read_lines_buggy(lines: list[str]):
    events.append("open")               # acquire the resource
    for line in lines:                  # produce lines one by one
        yield line                      # consumer may stop here forever
    events.append("close")              # ❌ only runs if the generator is fully exhausted
```

---

## 💡 Quick Concept (2 lines only)
Code after the last `yield` runs only if the consumer drains the generator. Put cleanup in `try/finally` (or use `with` inside the generator) — `finally` runs on exhaustion, `.close()`, an exception, or garbage collection.
हिंदी: cleanup को `try/finally` में रखो — consumer बीच में रुके तब भी `close()` पर चलेगा।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections.abc import Iterator             # type for generators/iterators

events: list[str] = []                           # records open/close

def read_lines_buggy(lines: list[str]) -> Iterator[str]:
    events.append("open")                        # acquire
    for line in lines:                           # produce
        yield line                               # consumer may stop here
    events.append("close")                       # skipped on early stop

gen = read_lines_buggy(["a", "b", "c"])          # create generator
print(next(gen))                                 # Expected: a
print(events)                                    # Expected: ['open']
gen.close()                                      # consumer gives up early
print(events)                                    # Expected: ['open']   (no 'close' -> leak!)

events.clear()                                   # reset the log

def read_lines(lines: list[str]) -> Iterator[str]:
    events.append("open")                        # acquire
    try:
        yield from lines                         # Step 1: produce inside try
    finally:
        events.append("close")                   # Step 2: always runs (exhaustion, close(), error, GC)

# ============================================
# TEST CASES
# ============================================
g = read_lines(["a", "b", "c"])                  # create generator
print(next(g))                                   # Expected: a
print(events)                                    # Expected: ['open']
g.close()                                        # raises GeneratorExit inside at the yield
print(events)                                    # Expected: ['open', 'close']
```

---

## 🔍 Why This Works (3 lines max)
`gen.close()` throws `GeneratorExit` at the paused `yield`, so a `finally` block runs; plain code after the loop does not. CPython also calls `close()` when an unreferenced generator is garbage-collected, but don't rely on that timing. Best practice: wrap with `contextlib.closing` or manage the resource in a `with` inside the generator.
हिंदी: `close()` generator में `GeneratorExit` डालता है — `finally` चलता है, loop के बाद वाला code नहीं।

---

## ⚡ Alternative Solution
```python
from collections.abc import Iterator             # type hints
from contextlib import closing, contextmanager  # helpers
import os, tempfile                              # temp file for the real-file example

events: list[str] = []                           # log

def read_lines(lines: list[str]) -> Iterator[str]:
    events.append("open")                        # acquire
    try:
        yield from lines                         # produce
    finally:
        events.append("close")                   # cleanup

# Alternative 1: closing() guarantees .close() when the with-block ends
with closing(read_lines(["x", "y"])) as it:      # it is the generator
    print(next(it))                              # Output: x
print(events)                                    # Output: ['open', 'close']

# Alternative 2: with-statement inside the generator (files close automatically)
path = os.path.join(tempfile.mkdtemp(), "f.txt") # temp file path
with open(path, "w") as fh:                      # create sample data
    fh.write("1\n2\n3\n")                        # three lines
def lines_of(p: str) -> Iterator[str]:
    with open(p) as f:                           # closed when the generator closes
        for line in f:                           # lazily read
            yield line.strip()                   # produce stripped line

g = lines_of(path)                               # create generator
print(next(g))                                   # Output: 1
g.close()                                        # closes the underlying file too
```

---

## ⚠️ Common Mistake
```python
events: list[str] = []                           # log

# ❌ Wrong: assuming the consumer's `break`/exception always lets the generator finish
def read_lines_buggy(lines: list[str]):
    events.append("open")                        # acquire
    for line in lines:
        yield line
    events.append("close")                       # skipped on early exit

for x in read_lines_buggy(["a", "b"]):           # consumer raises midway
    try:
        raise ValueError("boom")
    except ValueError:
        break                                    # stops after the first item

print(events)                                    # Output: ['open']   (close never recorded)
# ✅ Correct: use try/finally in the generator (or contextlib.closing in the caller)
```

---

## 🎯 Interview Tip (1 line)
Say: "Cleanup in a generator belongs in `try/finally` or a `with` block — `close()` raises `GeneratorExit` at the `yield`, so `finally` runs even when the consumer stops early."

---

## 🔗 Related Questions
→ Q025 (generator exhaustion) | Q027 (yield and send) | Q132 (file not closed bug) | Q165 (explain generators) | Q253 (contextlib)
