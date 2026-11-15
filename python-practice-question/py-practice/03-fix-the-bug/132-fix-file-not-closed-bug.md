---

# Q132. Fix File Not Closed Bug
# Category: Fix the Bug
# Difficulty: ⭐ Easy

---

## ❓ Question
This function leaks a file handle whenever the file content is invalid (and written data may never reach the disk). Find and fix the bug.

```python
# BUGGY CODE:
def read_first_int_buggy(p: str) -> int:
    f = open(p)                  # open the file
    value = int(f.readline())    # ❌ raises ValueError on bad content
    f.close()                    # never reached when the line above raises
    return value                 # normal return
```

---

## 💡 Quick Concept (2 lines only)
If an exception happens between `open()` and `close()`, `close()` is skipped and the handle leaks (and write buffers stay unflushed). `with open(...)` guarantees cleanup even on errors.
हिंदी: `open()` और `close()` के बीच error आया तो file बंद नहीं होती — `with` हमेशा बंद करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import os, tempfile                                   # temp file for a safe demo

path = os.path.join(tempfile.mkdtemp(), "log.txt")    # a throw-away file path

def read_first_int_buggy(p: str) -> int:
    f = open(p)                                       # open
    value = int(f.readline())                         # ValueError on empty/bad line
    f.close()                                         # skipped on error -> leak
    return value                                      # normal return

open(path, "w").close()                               # create an EMPTY file (valid close)
try:
    read_first_int_buggy(path)                        # int('') fails
except ValueError as e:                               # catch it
    print("ValueError:", e)                           # Expected: ValueError: invalid literal for int() with base 10: ''
# (file handle from the buggy call stays open until it is garbage collected)

# Step 1: use a context manager — closes on success AND on exception
def read_first_int(p: str) -> int:
    with open(p) as f:                                # f is closed when the block exits
        return int(f.readline())                      # exception still propagates, file still closes

# Step 2: prove that writes need closing/flushing
f = open(path, "w")                                   # open for writing
f.write("data")                                       # goes to an in-memory buffer
print("closed?", f.closed, "| on disk:", repr(open(path).read()))  # Expected: closed? False | on disk: ''
f.close()                                             # flush + close
print("closed?", f.closed, "| on disk:", repr(open(path).read()))  # Expected: closed? True | on disk: 'data'

# ============================================
# TEST CASES
# ============================================
with open(path, "w") as g:                            # with-block closes automatically
    g.write("42\n")                                   # write a number
print(g.closed)                                       # Expected: True
print(read_first_int(path))                           # Expected: 42
```

---

## 🔍 Why This Works (3 lines max)
`with` calls `f.__exit__()` (which closes the file) even if an exception is raised inside the block. CPython often closes an unreferenced file via refcounting, but that is an implementation detail — PyPy/other GCs may not, and buffered writes can be lost. Run with `python -X dev` to see `ResourceWarning: unclosed file`.
हिंदी: `with` exception पर भी file बंद करता है — CPython का auto-close भरोसे लायक नहीं।

---

## ⚡ Alternative Solution
```python
from pathlib import Path                      # object-oriented paths
import os, tempfile                           # temp dir

path = os.path.join(tempfile.mkdtemp(), "n.txt")   # throw-away file
Path(path).write_text("42")                   # opens, writes, closes for you
print(Path(path).read_text())                 # Output: 42
print(int(Path(path).read_text()) + 1)        # Output: 43

# try/finally — what `with` does under the hood
f = open(path)                                # open
try:
    print(f.read())                           # Output: 42
finally:
    f.close()                                 # always runs
print(f.closed)                               # Output: True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: with-block for the file but returning a lazy object that reads AFTER close
def lines_buggy(path: str):
    with open(path) as f:             # closed when function returns...
        return (line for line in f)   # ...but the generator reads later

# list(lines_buggy("x.txt"))  # not run: ValueError: I/O operation on closed file

# ✅ Correct: read inside the with-block, or make the function a generator itself
def lines(path: str):
    with open(path) as f:             # stays open while the generator is alive
        for line in f:                # lazily yield lines
            yield line.rstrip("\n")   # file closes when the generator finishes/closes
```

---

## 🎯 Interview Tip (1 line)
Say: "Always use `with` for files, sockets and locks — it guarantees cleanup on exceptions, and it is not safe to rely on garbage collection to close handles."

---

## 🔗 Related Questions
→ Q045 (with statement and __exit__) | Q119 (implement a context manager class) | Q167 (explain context managers) | Q249 (pathlib) | Q305 (the with statement)
