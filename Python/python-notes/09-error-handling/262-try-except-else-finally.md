---

# 262. try / except / else / finally
# हिंदी में: try / except / else / finally (error संभालना)

---

## 🔵 Simple Definition (English)
`try` holds code that may fail. `except` catches the error. `else` runs only when no error happened. `finally` runs always, error or not, and is used for cleanup.

## 🔵 सरल परिभाषा (Hindi)
`try` में वह code होता है जो fail हो सकता है। `except` error पकड़ता है। `else` तभी चलता है जब कोई error नहीं आई। `finally` हर हाल में चलता है और cleanup के लिए होता है।

---

## 🔴 Problem it Solves
Without error handling one bad input crashes the whole program, and files, DB connections and locks stay open. `try/except` lets the program recover, and `finally` guarantees cleanup. `else` keeps the "success only" code outside `try`, so you do not accidentally catch errors from it.

## 🔴 यह क्यों बना? (Hindi)
Error handling के बिना एक गलत input पूरा program गिरा देता है और file, DB connection, lock खुले रह जाते हैं। `try/except` से program recover करता है और `finally` cleanup पक्का करता है। `else` में "सिर्फ success" वाला code रखते हैं ताकि उसकी errors गलती से `except` में न फँस जाएँ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python runs the try block line by line
Step 2 → If an exception is raised, the rest of try is skipped
Step 3 → The first matching except block runs (top to bottom)
Step 4 → If NO exception happened, the else block runs
Step 5 → finally runs always (even with return, break, continue or an uncaught error)
Step 6 → If no except matched, the error continues upward after finally
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → try block line by line चलता है
Step 2 → exception आते ही try का बाकी हिस्सा छोड़ दिया जाता है
Step 3 → ऊपर से नीचे पहला matching except चलता है
Step 4 → अगर exception नहीं आई तो else चलता है
Step 5 → finally हर हाल में चलता है (return, break, continue के साथ भी)
Step 6 → कोई except match न हुआ तो finally के बाद error ऊपर चली जाती है
```

---

## 🟡 Real World Example
Razorpay payment service: call the bank API in `try`, catch `TimeoutError` and retry, mark the order paid in `else`, and always release the DB connection in `finally`. A Swiggy order API catches a missing restaurant (`KeyError`) and returns 404 instead of a 500 crash.

## 🟡 Real Example Hindi mein
Razorpay payment service में bank API `try` में call होती है, `TimeoutError` पर retry होता है, सफल होने पर `else` में order paid mark होता है और DB connection हमेशा `finally` में छोड़ा जाता है। Swiggy order API में restaurant न मिलने पर (`KeyError`) 500 crash की जगह 404 लौटता है।

---

## 💻 Code Example — Basic
```python
# Basic try / except / else / finally - every line commented
def parse_age(text: str) -> int | None:  # returns int or None
    try:  # code that may fail goes here
        age: int = int(text)  # may raise ValueError
    except ValueError:  # runs only if ValueError happened
        print("except: not a number ->", repr(text))  # report bad input
        return None  # give up with None
    else:  # runs only if try had NO exception
        print("else: parsed fine ->", age)  # success path
        return age  # return the good value
    finally:  # ALWAYS runs, error or not
        print("finally: done with", repr(text))  # cleanup / log


print(parse_age("25"))  # good input
print(parse_age("abc"))  # bad input

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# else: parsed fine -> 25
# finally: done with '25'
# 25
# except: not a number -> 'abc'
# finally: done with 'abc'
# None
```

## 💻 Code Example — Advanced
```python
# Production style: retry loop + guaranteed cleanup + finally return trap
import time  # for backoff sleep
from typing import Callable, TypeVar  # type hints

T = TypeVar("T")  # generic result type


class FakeConn:  # pretend DB / network connection
    def __init__(self) -> None:  # constructor
        self.closed: bool = False  # connection state

    def close(self) -> None:  # release resource
        self.closed = True  # mark closed
        print("connection closed")  # visible proof


def call_with_retry(fn: Callable[[], T], attempts: int = 3, delay: float = 0.01) -> T:
    last: Exception | None = None  # remember last error
    for n in range(1, attempts + 1):  # try up to N times
        try:  # risky call
            result: T = fn()  # may raise
        except (ConnectionError, TimeoutError) as exc:  # only transient errors
            last = exc  # store for final raise
            print(f"attempt {n} failed: {exc!r}")  # log each failure
            time.sleep(delay * n)  # linear backoff
        else:  # no exception -> success
            print(f"attempt {n} succeeded")  # log success
            return result  # leave the loop with the value
    raise RuntimeError(f"gave up after {attempts} attempts") from last  # chain cause


calls: list[int] = [0]  # mutable counter shared with flaky()


def flaky() -> str:  # fails twice then works
    calls[0] += 1  # count calls
    if calls[0] < 3:  # first two calls fail
        raise ConnectionError("db down")  # transient error
    return "payment saved"  # third call ok


print(call_with_retry(flaky))  # retry succeeds on 3rd try


def use_connection() -> str:  # finally guarantees close
    conn = FakeConn()  # open resource
    try:  # use it
        raise ValueError("bad query")  # simulate failure
    except ValueError:  # handle
        return "handled"  # return happens AFTER finally runs
    finally:  # always executes
        conn.close()  # cleanup even with return/raise


print(use_connection())  # prints "connection closed" then "handled"


def finally_swallows() -> str:  # DANGEROUS pattern
    try:  # raises
        raise RuntimeError("lost!")  # this error will vanish
    finally:  # return inside finally cancels the exception
        return "finally won"  # (3.14 warns about this, PEP 765)


print(finally_swallows())  # exception silently discarded

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# attempt 1 failed: ConnectionError('db down')
# attempt 2 failed: ConnectionError('db down')
# attempt 3 succeeded
# payment saved
# connection closed
# handled
# finally won
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has `try/catch/finally` but no `else` clause. Python's `else` is the clean way to separate "success code" from "guarded code". Python also catches by exception type, JavaScript has one `catch` for everything.

```python
# Python way
try:
    value = int("12")          # guarded code
except ValueError as exc:      # catch by type
    print("bad", exc)
else:
    print("ok", value)         # success only
finally:
    print("cleanup")           # always
```
```javascript
// JavaScript way
try {
  const value = parseInt("12");   // guarded code (no throw for bad input!)
  console.log("ok", value);       // success code lives inside try
} catch (err) {                   // one catch for every error type
  console.log("bad", err);
} finally {
  console.log("cleanup");         // always
}
```

Key differences: JS `parseInt("abc")` returns `NaN` instead of throwing; Python `int("abc")` raises `ValueError`. Python has `else`; JS does not. Python can have many `except` blocks by type.

---

## 🟠 FastAPI Connection
In FastAPI you convert low-level errors (`KeyError`, DB errors) into `HTTPException` with the right status code, and use `finally` for cleanup. For shared resources prefer `yield` dependencies, which are `try/finally` under the hood.

```python
# FastAPI: try/except/else/finally inside an endpoint (pip install fastapi httpx)
from fastapi import FastAPI, HTTPException  # app + HTTP errors
from fastapi.testclient import TestClient  # in-process test client

app: FastAPI = FastAPI()  # create app
DB: dict[int, str] = {1: "Aditya"}  # fake user table
log: list[str] = []  # collect cleanup events


@app.get("/users/{uid}")  # GET /users/1
def get_user(uid: int) -> dict[str, str]:
    try:  # risky lookup
        name: str = DB[uid]  # KeyError if missing
    except KeyError:  # convert to HTTP error
        raise HTTPException(status_code=404, detail="user not found")  # 404 JSON
    else:  # only on success
        return {"name": name}  # 200 JSON
    finally:  # runs on both paths
        log.append(f"lookup {uid} finished")  # audit trail


client = TestClient(app)  # test client
print(client.get("/users/1").json())  # success
print(client.get("/users/9").status_code, client.get("/users/9").json())  # 404
print(log)  # finally ran 3 times

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# {'name': 'Aditya'}
# 404 {'detail': 'user not found'}
# ['lookup 1 finished', 'lookup 9 finished', 'lookup 9 finished']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Bare `except:` or `except Exception: pass`
```python
# Wrong - hides every bug, even KeyboardInterrupt (bare except)
try:
    risky()
except:
    pass

# Right - catch the specific error and log it
try:
    risky()
except ValueError as exc:
    logger.warning("bad value: %s", exc)
```

❌ Mistake 2: Putting success code inside `try`
```python
# Wrong - a bug in save() is wrongly caught as "bad input"
try:
    n = int(text)
    save(n)
except ValueError:
    print("bad input")

# Right - only the risky line is guarded
try:
    n = int(text)
except ValueError:
    print("bad input")
else:
    save(n)
```

❌ Mistake 3: `return` / `break` inside `finally`
```python
# Wrong - this silently throws the exception away
def f():
    try:
        raise RuntimeError("lost")
    finally:
        return "ok"

# Right - let finally only clean up, never return
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def f() -> int:  # which value is returned?
    try:  # try block
        return 1  # tries to return 1
    finally:  # finally runs before the return completes
        print("cleanup")  # side effect


def g() -> int:  # finally overrides
    try:  # try
        return 1  # pending return value
    finally:  # finally has its own return
        return 2  # overrides the pending return


def h() -> str:  # loop + else interplay
    for i in range(3):  # loop
        try:  # try
            if i == 1:  # at i == 1
                continue  # continue still runs finally
        finally:  # finally
            print("f", i)  # prints for 0,1,2
    return "end"  # done


print(f())  # cleanup then 1
print(g())  # 2
print(h())  # f0 f1 f2 end
```

**Answer**:
```
cleanup
1
2
f 0
f 1
f 2
end
```
`finally` runs before the pending `return 1` completes, so "cleanup" prints first. In `g()` the `return 2` inside `finally` replaces the earlier return value. `continue` inside `try` still triggers `finally` each time.

---

## ⚫ Interview Questions + Answers

Q1: When does `else` run?
A1: Only when the `try` block finished without an exception (and without `return`, `break` or `continue`).

Q2: Does `finally` run if `try` has `return`?
A2: Yes. The return value is computed, `finally` runs, then the function returns.

Q3: Can `try` exist without `except`?
A3: Yes, `try/finally` is valid and is the manual form of a context manager. `try` needs at least one of `except` or `finally`.

Q4: Order of multiple `except` blocks?
A4: Top to bottom, first match wins. Put specific exceptions before general ones.

Q5: What is `except (A, B) as e`?
A5: One handler for several types, written as a tuple. `e` is only available inside that block.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You can really handle or translate the error
- You must release resources (`finally`)
- Failure is expected (network, user input, files)

❌ Avoid when:
- You only want to hide errors (`pass`)
- A simple `if` check is clearer (EAFP vs LBYL: Python prefers try, but not for everything)
- You wrap huge blocks of code instead of one risky line

---

## 📊 Visual Diagram

```
          try block
             │
     ┌───────┴────────┐
 error raised?       no error
     │                   │
 matching except?     else block
   ┌─┴──┐                 │
  yes   no                │
   │    │                 │
 handler  (propagate)     │
   └────┴────────┬────────┘
              finally  (always)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| try | Guarded code | जाँच वाला code |
| except | Handles an error | error पकड़ना |
| else | Runs if no error | error न आने पर |
| finally | Always runs | हमेशा चलने वाला |
| raise | Throw an exception | exception फेंकना |
| propagate | Error moves to the caller | error का ऊपर जाना |

---

## ⚡ 3-Line Summary
English: `try` guards risky code, `except` handles specific errors, `else` is the success path and `finally` always cleans up. Keep `try` small and never return from `finally`. Catch specific exceptions, not bare `except`.
Hindi: `try` risky code रखता है, `except` खास errors संभालता है, `else` success path है और `finally` हमेशा cleanup करता है। `try` छोटा रखें और `finally` से return न करें। Bare `except` की जगह specific exceptions पकड़ें।

---

## ➡️ Next Topic
**263. Exception Hierarchy** — how `BaseException`, `Exception` and subclasses are organised.

Note: FastAPI example needs `httpx`; recent Starlette prints a deprecation warning for `starlette.testclient` with `httpx` (warning only, output unchanged). All examples were run on Python 3.13.
