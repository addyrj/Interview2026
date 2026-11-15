---

# 206. with Statement for Files
# हिंदी में: with Statement (file अपने आप बंद करना)

---

## 🔵 Simple Definition (English)
The `with` statement runs a block of code and guarantees cleanup afterwards. For files, `with open(...) as f:` closes the file when the block ends, even if an error happens inside. It works through the context manager protocol: `__enter__` and `__exit__`.

## 🔵 सरल परिभाषा (Hindi)
`with` statement code का एक block चलाता है और उसके बाद cleanup की गारंटी देता है। Files के लिए `with open(...) as f:` block खत्म होते ही file बंद कर देता है, भले अंदर error आ जाए। यह context manager protocol से चलता है: `__enter__` और `__exit__`।

---

## 🔴 Problem it Solves
Calling `f.close()` by hand is easy to forget, and if an exception happens before it, the close line never runs. Leaked files keep memory, hold locks, lose buffered data and eventually hit the OS limit ("Too many open files"). The old fix was `try/finally` everywhere. `with` is the short, safe version.

## 🔴 यह क्यों बना? (Hindi)
`f.close()` हाथ से लिखना भूलना आसान है, और बीच में exception आ जाए तो close वाली line चलती ही नहीं। Leak हुई files memory घेरती हैं, locks पकड़े रखती हैं, buffer का data खो देती हैं और आखिर में OS की सीमा ("Too many open files") आ जाती है। पहले हर जगह `try/finally` लिखना पड़ता था। `with` उसका छोटा और सुरक्षित रूप है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python evaluates open(...) and gets a file object
Step 2 → It calls file.__enter__()  -> returns the file, bound to the name after "as"
Step 3 → Your indented block runs
Step 4 → The block ends (normally, by return/break, or by an exception)
Step 5 → Python ALWAYS calls file.__exit__(exc_type, exc, tb) -> closes the file
Step 6 → If an exception happened, it keeps travelling up (unless __exit__ returns True)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python open(...) चलाकर file object लेता है
Step 2 → file.__enter__() बुलाता है और "as" के बाद वाले नाम में रखता है
Step 3 → आपका indented block चलता है
Step 4 → block खत्म होता है (सामान्य रूप से, return/break से या exception से)
Step 5 → Python हमेशा file.__exit__() बुलाता है -> file बंद हो जाती है
Step 6 → exception आया हो तो वह आगे बढ़ता रहता है (जब तक __exit__ True न लौटाए)
```

---

## 🟡 Real World Example
A Razorpay reconciliation script opens the bank statement and the output report together in one `with`; if the bank file is corrupt and parsing fails, both files still close cleanly. A long-running FastAPI service handling 10,000 uploads/hour must never leak descriptors, so every `open()` is inside `with`. A database transaction (`with session.begin():`) uses the same idea.

## 🟡 Real Example Hindi mein
Razorpay की reconciliation script bank statement और output report दोनों को एक ही `with` में खोलती है; bank file खराब निकले और parsing fail हो, तब भी दोनों files साफ तरीके से बंद होती हैं। हर घंटे 10,000 uploads संभालने वाली FastAPI service में descriptors leak नहीं होने चाहिए, इसलिए हर `open()` `with` के अंदर है। Database transaction (`with session.begin():`) भी यही विचार है।

---

## 💻 Code Example — Basic
```python
# with statement for files - every line commented
import tempfile  # temp folder
from pathlib import Path  # paths

d: Path = Path(tempfile.mkdtemp())  # temporary directory
p: Path = d / "w.txt"  # test file

with open(p, "w", encoding="utf-8") as f:  # open and bind to f
    print(f.closed)  # still open inside the block
    f.write("hi")  # write inside the block
# Output: False
print(f.closed)  # the name f still exists, but the file is closed
# Output: True

try:  # error inside with
    with open(p, "w", encoding="utf-8") as f:  # open again
        f.write("partial")  # this is written
        raise RuntimeError("boom")  # simulate a crash
except RuntimeError as exc:  # we catch it outside
    print("caught", exc, f.closed, p.read_text())  # file was closed and data saved
# Output: caught boom True partial

# Two files in one with (no nesting needed)
with open(p, encoding="utf-8") as src, open(d / "b.txt", "w", encoding="utf-8") as dst:
    dst.write(src.read().upper())  # copy in uppercase
print((d / "b.txt").read_text())  # check the copy
# Output: PARTIAL

with open(p, encoding="utf-8") as f:  # open
    pass  # do nothing
try:  # using it afterwards
    f.read()  # file is closed
except ValueError as exc:  # ValueError
    print("ValueError:", exc)  # message
# Output: ValueError: I/O operation on closed file.
```

## 💻 Code Example — Advanced
```python
# Production style: custom context managers, ExitStack, parenthesised with
from contextlib import ExitStack, contextmanager, suppress  # helpers
import tempfile  # temp folder
from pathlib import Path  # paths
from typing import IO, Iterator, Optional  # type hints


class Timer:
    """A class-based context manager showing __enter__ / __exit__."""

    def __enter__(self) -> "Timer":
        print("enter")  # setup code
        return self  # value for "as"

    def __exit__(self, exc_type, exc, tb) -> bool:  # always runs
        print("exit", exc_type.__name__ if exc_type else None)  # cleanup
        return False  # False -> do not hide the exception


with Timer():  # normal exit
    pass
# Output: enter
# Output: exit None

with suppress(ZeroDivisionError), Timer():  # suppress hides the chosen error
    1 / 0  # raises inside Timer
# Output: enter
# Output: exit ZeroDivisionError
print("after")  # program continues
# Output: after


@contextmanager  # generator-based context manager
def opened(path: Path, mode: str = "r") -> Iterator[IO[str]]:
    fh: IO[str] = open(path, mode, encoding="utf-8")  # setup
    try:  # protect the body
        yield fh  # value for "as"
    finally:  # cleanup ALWAYS runs
        fh.close()  # close the file
        print("closed by finally")  # prove it


d: Path = Path(tempfile.mkdtemp())  # temp folder
p: Path = d / "w.txt"  # file
p.write_text("partial", encoding="utf-8")  # sample data

with opened(p) as fh:  # use our manager
    print(fh.read())  # read inside
# Output: partial
# Output: closed by finally

# ExitStack: open a variable number of files safely
with ExitStack() as stack:  # collects many context managers
    files = [stack.enter_context(open(p, encoding="utf-8")) for _ in range(3)]  # 3 files
    print(len(files), all(not f.closed for f in files))  # all open
# Output: 3 True
print(all(f.closed for f in files))  # all closed when the stack ends
# Output: True

# return inside with still closes the file
def first_line(path: Path) -> str:
    with open(path, encoding="utf-8") as fh2:  # open
        return fh2.readline()  # __exit__ runs before the function really returns


print(repr(first_line(p)))  # works as expected
# Output: 'partial'

# Python 3.10+: parentheses allow a multi-line with
with (
    open(p, encoding="utf-8") as x,  # first file
    open(d / "c.txt", "w", encoding="utf-8") as y,  # second file
):
    y.write(x.read())  # copy
print((d / "c.txt").read_text())  # verify
# Output: partial

# __exit__ returning True swallows the exception (use with great care)
class Swallow:
    def __enter__(self) -> int:
        return 5  # value for "as"

    def __exit__(self, *args: object) -> bool:
        return True  # hide any exception


with Swallow() as r:  # exception is hidden
    raise ValueError("swallowed")  # never seen
print("continues", r)  # program goes on
# Output: continues 5
```
Verified on Python 3.13.3. Parenthesised `with` is officially supported from Python 3.10 (it worked unofficially in 3.9).

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
with open("a.txt", "w", encoding="utf-8") as f:
    f.write("hello")
# file closed here, even after errors
```
```javascript
// JavaScript way
// Classic: try/finally
import { openSync, writeSync, closeSync } from "node:fs";
const fd = openSync("a.txt", "w");
try { writeSync(fd, "hello"); } finally { closeSync(fd); }

// Newer: explicit resource management (TypeScript 5.2, Node 24 / recent engines)
// await using file = await fs.promises.open("a.txt", "w");   // auto-closed
// Or just use fs.writeFileSync / promises (they open+close for you)
```

Key differences: Python's `with` has been the standard for years and works with any object having `__enter__`/`__exit__`. JavaScript historically used `try/finally`; the `using` / `await using` keywords are the modern equivalent but need a recent runtime. Most Node code avoids the issue by using one-shot helpers like `readFile`.

---

## 🟠 FastAPI Connection
`with` is everywhere in FastAPI projects: file writes, `with open`, `with tempfile.TemporaryDirectory()`, `with Session(engine) as session`, `with httpx.Client()`. Dependencies with `yield` follow the same cleanup idea: code after `yield` runs like `__exit__`.

```python
# FastAPI: a yield dependency behaves like a with-block (pip install fastapi)
from typing import IO, Iterator  # type hints
from fastapi import Depends, FastAPI  # framework
import tempfile  # temp folder

app: FastAPI = FastAPI()  # app


def get_report_file() -> Iterator[IO[str]]:
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8") as fh:  # with = auto cleanup
        yield fh  # give the file to the endpoint
    # after the response, the with block ends and the temp file is deleted


@app.get("/report")  # GET /report
def report(fh: IO[str] = Depends(get_report_file)) -> dict[str, int]:
    written: int = fh.write("line\n")  # use the file
    return {"written": written}  # JSON result
# Not run as a server in this note; the with/yield pattern itself was run in the examples above.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `open()` without `with`
✅ Correct:

```python
# Wrong - leaks the file if write() raises
f = open("a.txt", "w"); f.write("x"); f.close()
# Right
with open("a.txt", "w", encoding="utf-8") as f:
    f.write("x")
```

❌ Mistake 2: Using the file after the block
✅ Correct:

```python
# Wrong - ValueError: I/O operation on closed file
with open("a.txt") as f:
    pass
data = f.read()
# Right - read inside the block
with open("a.txt") as f:
    data = f.read()
```

❌ Mistake 3: Deep nesting for many files
✅ Correct:

```python
# Wrong - ugly pyramid
with open("a") as a:
    with open("b") as b:
        ...
# Right - one with, several managers (parenthesised form on 3.10+)
with open("a") as a, open("b") as b:
    ...
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
class Res:
    def __enter__(self):
        return 5
    def __exit__(self, *args):
        return True

with Res() as r:
    raise ValueError("lost")
print("continues", r)

def f():
    with open("t.txt", "w") as fh:
        return fh
print(f().closed)
```

**Answer**:
```
continues 5
True
```
`__exit__` returned `True`, which tells Python to suppress the exception, so the program continues. In the second part, `return fh` leaves the function, but `__exit__` still runs on the way out, so the returned file object is already closed. (Both lines verified on Python 3.13.)

---

## ⚫ Interview Questions + Answers

Q1: What does `with` do under the hood?
A1: It calls `__enter__()` at the start and `__exit__()` at the end, always, even when an exception or `return` happens.

Q2: Is `with open(...)` the same as `try/finally`?
A2: Practically yes: it is shorthand for try/finally with `close()`, but cleaner and harder to get wrong.

Q3: Does `with` create a new scope?
A3: No. Variables created inside, including the `as` name, still exist after the block. The file object just becomes closed.

Q4: How do you write your own context manager?
A4: A class with `__enter__`/`__exit__`, or a generator function decorated with `@contextlib.contextmanager` that has `try: yield ... finally: cleanup`.

Q5: What happens to an unclosed file when the program ends?
A5: CPython usually closes it when the object is garbage collected, but this is not guaranteed on other implementations and buffered data can be lost on crash. With `python -X dev` you get a `ResourceWarning: unclosed file`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Opening any file, socket, DB session, lock or temp directory
- You need guaranteed cleanup even on errors
- Several resources must be released together (`ExitStack`)

❌ Avoid when:
- The resource must stay open beyond the function (long-lived log handler; manage it explicitly or via app lifespan)
- A one-shot helper is enough: `Path.read_text()` / `write_text()`
- Swallowing exceptions in `__exit__` without a very good reason

---

## 📊 Visual Diagram

```
with open("a.txt") as f:
        |
        v
  f.__enter__()  ---> block runs ---> (normal end | return | exception)
                                              |
                                              v
                                    f.__exit__()  -> f.close()
                                              |
                                  exception? -> re-raised (unless __exit__ returns True)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context manager | Object with __enter__ and __exit__ | setup/cleanup वाला object |
| __enter__ | Runs at block start | block शुरू होने पर चलता है |
| __exit__ | Runs at block end, always | block खत्म होने पर हमेशा चलता है |
| ExitStack | Manage many resources together | कई resources एक साथ संभालना |
| Resource leak | Resource not released | resource वापस न होना |
| ResourceWarning | Warning for unclosed files | बिना बंद file की चेतावनी |

---

## ⚡ 3-Line Summary
English: `with open(...) as f:` always closes the file, even after errors or `return`. It works through `__enter__`/`__exit__`, so you can write your own with `@contextmanager`. Use `ExitStack` or a parenthesised `with` for many files.
Hindi: `with open(...) as f:` हमेशा file बंद करता है, error या `return` के बाद भी। यह `__enter__`/`__exit__` से चलता है, इसलिए `@contextmanager` से अपना भी बना सकते हैं। कई files के लिए `ExitStack` या parenthesised `with` इस्तेमाल करें।

---

## ➡️ Next Topic
**207. CSV File Handling** — reading and writing CSV with the `csv` module and `DictReader`.
