---

# 275. Traceback Module
# हिंदी में: Traceback Module (error की पूरी कहानी)

---

## 🔵 Simple Definition (English)
The `traceback` module reads, formats and prints the call stack of an exception. It turns the hidden `__traceback__` object into text or structured data you can log, store or send to an error tracker.

## 🔵 सरल परिभाषा (Hindi)
`traceback` module किसी exception की call stack को पढ़ता, format करता और print करता है। यह छुपे हुए `__traceback__` object को text या structured data में बदलता है जिसे आप log, store या error tracker को भेज सकते हैं।

---

## 🔴 Problem it Solves
When an exception is caught, the default traceback is only printed when it is uncaught. If you catch it and want the same details in a log, a JSON report or an HTTP debug page, you need a tool to extract file names, line numbers and the chain of causes. `traceback` is that tool.

## 🔴 यह क्यों बना? (Hindi)
Exception पकड़ लेने पर default traceback सिर्फ़ तब छपता है जब वह uncaught हो। अगर आप उसी जानकारी को log, JSON report या debug page में चाहते हैं तो file names, line numbers और causes की chain निकालने का tool चाहिए। `traceback` वही tool है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → An exception carries exc.__traceback__ (a linked list of frames)
Step 2 → traceback.extract_tb(tb) turns it into FrameSummary objects (file, line, function, code)
Step 3 → traceback.format_exception(exc) gives a list of text lines, including chained causes
Step 4 → traceback.format_exc() does the same for the exception currently being handled
Step 5 → traceback.print_exc() prints it (stderr by default, or file=...)
Step 6 → TracebackException.from_exception(exc) keeps a light, storable snapshot (no live frames)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Exception के पास exc.__traceback__ होता है (frames की linked list)
Step 2 → traceback.extract_tb(tb) उसे FrameSummary objects (file, line, function, code) में बदलता है
Step 3 → traceback.format_exception(exc) text lines की list देता है, chained causes सहित
Step 4 → traceback.format_exc() उसी exception के लिए यही करता है जो अभी संभाली जा रही है
Step 5 → traceback.print_exc() उसे छापता है (default stderr, या file=...)
Step 6 → TracebackException.from_exception(exc) हल्का, store करने योग्य snapshot रखता है (live frames नहीं)
```

---

## 🟡 Real World Example
A Razorpay worker catches every job failure, builds a report with `format_exception`, and posts it to Slack and Sentry. A FastAPI global handler stores the full traceback under a short error id and returns only the id to the client. A CLI tool prints just the last frame for friendly errors.

## 🟡 Real Example Hindi mein
Razorpay का worker हर job failure पकड़कर `format_exception` से report बनाता है और Slack व Sentry को भेजता है। FastAPI का global handler पूरा traceback एक छोटे error id के नीचे रखता है और client को सिर्फ़ id लौटाता है। CLI tool friendly errors के लिए सिर्फ़ आख़िरी frame छापता है।

---

## 💻 Code Example — Basic
```python
# Basic traceback module - every line commented
import sys  # for sys.exc_info
import traceback  # the module


def level3() -> None:  # deepest function
    raise ValueError("bad data")  # raise here


def level2() -> None:  # middle function
    level3()  # call deeper


def level1() -> None:  # top function
    level2()  # call deeper


try:  # trigger the error
    level1()  # three calls deep
except ValueError as exc:  # catch
    text: str = traceback.format_exc()  # traceback as string (current exception)
    print(text.splitlines()[0])  # first line is the header
    print(text.splitlines()[-1])  # last line is the error
    frames = traceback.extract_tb(exc.__traceback__)  # structured frames
    print([f.name for f in frames])  # function names, outermost first
    print(frames[-1].lineno, frames[-1].name)  # where it finally failed
    lines: list[str] = traceback.format_exception(exc)  # 3.10+ accepts just the exception
    print(len(lines) >= 4, lines[-1].strip())  # list of lines
    traceback.print_exc(file=sys.stdout)  # print to stdout instead of stderr

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# Traceback (most recent call last):
# ValueError: bad data
# ['<module>', 'level1', 'level2', 'level3']
# 7 level3
# True ValueError: bad data
# Traceback (most recent call last):
#   File "/app/b.py", line 19, in <module>
#     level1()  # three calls deep
#     ~~~~~~^^
#   File "/app/b.py", line 15, in level1
#     level2()  # call deeper
#     ~~~~~~^^
#   File "/app/b.py", line 11, in level2
#     level3()  # call deeper
#     ~~~~~~^^
#   File "/app/b.py", line 7, in level3
#     raise ValueError("bad data")  # raise here
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ValueError: bad data
```

## 💻 Code Example — Advanced
```python
# Production style: build an error report dict with a compact stack, chained causes, TracebackException
import traceback  # module
from typing import Any  # type hint


class ServiceError(Exception):  # wrapper error
    pass  # marker


def parse(raw: str) -> int:  # inner failure
    return int(raw)  # ValueError for bad input


def process(raw: str) -> int:  # wraps the inner error
    try:  # call inner
        return parse(raw)  # may fail
    except ValueError as exc:  # wrap with context
        raise ServiceError("cannot process input") from exc  # chain


def error_report(exc: BaseException) -> dict[str, Any]:  # JSON-friendly summary
    te = traceback.TracebackException.from_exception(exc)  # structured view (no live frames kept)
    frames = [f"{f.name}:{f.lineno}" for f in te.stack]  # compact frames
    cause = te.__cause__  # chained cause, if any
    return {  # build report
        "type": te.exc_type.__name__,  # exception class name
        "message": str(exc),  # message
        "frames": frames,  # where
        "cause": f"{cause.exc_type.__name__}: {cause}" if cause else None,  # root cause
    }


try:  # run
    process("abc")  # fails
except ServiceError as e:  # catch
    print(error_report(e))  # report dict
    full: str = "".join(traceback.format_exception(e))  # complete text with chain
    print("direct cause" in full)  # chain message present
    traceback.print_exception(e, limit=1, file=__import__("sys").stdout)  # limit frames
print(len(traceback.extract_stack()) >= 1)  # current call stack (no exception needed)

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# {'type': 'ServiceError', 'message': 'cannot process input', 'frames': ['<module>:34', 'process:18'], 'cause': "ValueError: invalid literal for int() with base 10: 'abc'"}
# True
# Traceback (most recent call last):
#   File "/app/a.py", line 16, in process
#     return parse(raw)  # may fail
# ValueError: invalid literal for int() with base 10: 'abc'
# 
# The above exception was the direct cause of the following exception:
# 
# Traceback (most recent call last):
#   File "/app/a.py", line 34, in <module>
#     process("abc")  # fails
#     ~~~~~~~^^^^^^^
# ServiceError: cannot process input
# True
```

---

## 🟠 JavaScript vs Python Comparison
In JavaScript the stack is a string in `err.stack`. You parse it yourself or use `error-stack-parser`. Python gives structured frames (`FrameSummary`) and formatting helpers built in.

```python
import traceback
try:
    1/0
except ZeroDivisionError as e:
    print(traceback.format_exception(e)[-1])
```
```javascript
try { null.x } catch (e) {
  console.log(e.stack.split('\n')[0]);  // stack is just a string
}
```

Key differences: JS `err.stack` is one non-standard string. Python exposes frames as objects (`extract_tb`) and handles chained causes (`from`) in `format_exception`.

---

## 🟠 FastAPI Connection
Use `traceback.format_exception(exc)` inside a global exception handler to store or log the full error. Return only an error id to clients so internal paths and code do not leak. Logging with `logger.exception` already formats the traceback for you.

```python
# FastAPI: return a short error id to the client, keep the full traceback in server logs
import traceback  # traceback text
import uuid  # error id
from fastapi import FastAPI, Request  # app and request
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app
STORE: dict[str, str] = {}  # stands in for a log store


@app.exception_handler(Exception)  # unexpected errors
async def on_error(request: Request, exc: Exception) -> JSONResponse:
    err_id: str = uuid.uuid4().hex[:8]  # short id for support
    STORE[err_id] = "".join(traceback.format_exception(exc))  # full traceback saved server side
    return JSONResponse(status_code=500, content={"error_id": err_id})  # client sees only the id


@app.get("/crash")  # crashing endpoint
def crash() -> None:
    {}["missing"]  # KeyError


c = TestClient(app, raise_server_exceptions=False)  # client
body = c.get("/crash").json()  # call
print(list(body), len(body["error_id"]))  # only an id is exposed
saved = STORE[body["error_id"]]  # support engineer looks it up
print(saved.splitlines()[-1])  # last line of the stored traceback
print("Traceback (most recent call last)" in saved)  # full text kept

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# ['error_id'] 8
# KeyError: 'missing'
# True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling `format_exc()` outside an except block
```python
# Wrong
print(traceback.format_exc())  # 'NoneType: None'

# Right
except Exception as exc:
    text = ''.join(traceback.format_exception(exc))
```

❌ Mistake 2: Sending the traceback to the client
```python
# Wrong
return {'error': traceback.format_exc()}  # leaks paths, code, secrets

# Right
return {'error_id': err_id}  # keep the traceback in logs
```

❌ Mistake 3: Keeping `exc.__traceback__` alive in long-lived objects
```python
# Wrong
self.last_error = exc   # holds frames and locals in memory

# Right
self.last_error = traceback.TracebackException.from_exception(exc)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import traceback  # module

def f() -> None:  # raises
    raise ValueError("x")  # error

try:  # case 1
    f()  # fail
except ValueError:  # catch
    s1 = traceback.format_exc()  # string
print(type(s1).__name__, s1.count("File"))  # str 2

print(traceback.format_exc())  # outside except -> no active exception

try:  # case 3
    try:  # inner
        f()  # fail
    except ValueError as e:  # catch
        raise RuntimeError("outer") from e  # chain
except RuntimeError as e:  # outer catch
    out = traceback.format_exception(e)  # full list
    print(any("direct cause" in x for x in out), out[-1].strip())  # True RuntimeError: outer

try:  # case 4
    f()  # fail
except ValueError as e:  # catch
    tb = e.__traceback__  # traceback object
print(tb.tb_frame.f_code.co_name, tb.tb_next.tb_frame.f_code.co_name)  # <module> f
```

**Answer**:
```
str 2
NoneType: None

True RuntimeError: outer
<module> f
```
`format_exc()` returns a `str`, and a traceback with two frames contains "File" twice. Outside an `except` block it returns `NoneType: None`. `format_exception(e)` on the outer error includes the chain text "direct cause". `tb.tb_frame` is the outermost frame (`<module>`) and `tb.tb_next` walks one frame deeper (`f`).

---

## ⚫ Interview Questions + Answers

Q1: `print_exc` vs `format_exc`?
A1: `print_exc()` prints to stderr (or a file); `format_exc()` returns the same text as a string.

Q2: How do you get structured frames?
A2: `traceback.extract_tb(exc.__traceback__)` returns `FrameSummary` objects with `filename`, `lineno`, `name`, `line`.

Q3: Why use `TracebackException`?
A3: It is a lightweight copy that does not hold frames or local variables, so it is safe to store or send across threads.

Q4: What does `limit` do?
A4: Limits the number of frames shown, for example `print_exception(e, limit=1)`.

Q5: What is a reference cycle risk?
A5: Storing the exception in a local variable inside the frame it references can create a cycle holding frames alive. Python deletes `except ... as e` names at block end for this reason.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Custom error reports (JSON, Slack, Sentry)
- Showing a short error in CLIs
- Global exception handlers in services

❌ Avoid when:
- Showing tracebacks to end users
- Using it when `logger.exception` is enough
- Storing live traceback objects long term

---

## 📊 Visual Diagram

```
exception ──► __traceback__ ──► tb_next ──► tb_next ...
                │
   extract_tb ─► [FrameSummary(file, line, name, code)]
   format_exception ─► ['Traceback (most recent call last):', ... ]
   TracebackException ─► storable snapshot
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| traceback | Call stack at the error | error के समय की call stack |
| frame | One function call record | एक function call का record |
| FrameSummary | Light frame info | हल्की frame जानकारी |
| chained exception | Cause of another error | दूसरी error का कारण |
| stack | Calls waiting to finish | पूरी होने का इंतज़ार करती calls |
| snapshot | Saved copy | सहेजी हुई प्रति |

---

## ⚡ 3-Line Summary
English: `traceback` turns an exception's call stack into text or structured frames: `format_exc`, `format_exception`, `extract_tb`, `TracebackException`. Use it for reports and global handlers, and never send tracebacks to users.
Hindi: `traceback` exception की call stack को text या structured frames में बदलता है: `format_exc`, `format_exception`, `extract_tb`, `TracebackException`। इसे reports और global handlers में इस्तेमाल करें और users को traceback कभी न भेजें।

---

## ➡️ Next Topic
**276. Testing in Python — Overview** — how to test the code you just handled errors in.

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.

Note: the shown tracebacks use a neutral `/app` path (the real run used a scratch path); caret markers (`~~^^`) appear on Python 3.11+.
