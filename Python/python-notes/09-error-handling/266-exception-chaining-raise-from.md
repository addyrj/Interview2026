---

# 266. Exception Chaining (raise from)
# हिंदी में: Exception Chaining (raise from से कारण जोड़ना)

---

## 🔵 Simple Definition (English)
Exception chaining links one exception to the one that caused it. `raise NewError(...) from original` sets `__cause__`, so the traceback shows both: the root cause and your higher-level error.

## 🔵 सरल परिभाषा (Hindi)
Exception chaining एक exception को उस exception से जोड़ती है जिसने उसे पैदा किया। `raise NewError(...) from original` से `__cause__` set होता है, इसलिए traceback में दोनों दिखते हैं: असली कारण और आपकी ऊपरी-level error।

---

## 🔴 Problem it Solves
When you catch a low-level error (`KeyError`, a DB driver error) and raise a domain error (`UserNotFound`), the original detail is lost unless you keep it. Without chaining, debugging production issues means guessing what really failed. Chaining keeps the full story and lets you hide or show it deliberately.

## 🔴 यह क्यों बना? (Hindi)
जब आप low-level error (`KeyError`, DB driver error) पकड़कर domain error (`UserNotFound`) raise करते हैं, तो original detail खो जाती है। Chaining के बिना production bug में अंदाज़ा लगाना पड़ता है कि असल में क्या fail हुआ। Chaining पूरी कहानी रखती है और आप जानबूझकर उसे दिखा या छुपा सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A low-level error happens inside try
Step 2 → In except, you raise a new exception
Step 3 → raise New from old  → __cause__ = old, __suppress_context__ = True
         ("The above exception was the direct cause of the following")
Step 4 → raise New (no from) inside except → __context__ = old automatically
         ("During handling of the above exception, another exception occurred")
Step 5 → raise New from None → hides the old one (__suppress_context__ = True)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → try के अंदर कोई low-level error आती है
Step 2 → except में आप नई exception raise करते हैं
Step 3 → raise New from old → __cause__ = old ("direct cause" वाला संदेश)
Step 4 → except के अंदर सिर्फ raise New → __context__ अपने-आप old बन जाता है
Step 5 → raise New from None → पुरानी वाली traceback में नहीं दिखती
```

---

## 🟡 Real World Example
Swiggy order service: the repository raises `KeyError` for a missing order; the service layer converts it to `OrderNotFound` using `from exc`. The log still shows the `KeyError` line, so engineers see exactly where the lookup failed, while the API returns a clean 404.

## 🟡 Real Example Hindi mein
Swiggy order service में repository missing order पर `KeyError` देती है; service layer उसे `from exc` के साथ `OrderNotFound` में बदलती है। Log में `KeyError` की line फिर भी दिखती है, इसलिए engineers देख सकते हैं कि lookup कहाँ fail हुआ, और API साफ़ 404 लौटाती है।

---

## 💻 Code Example — Basic
```python
# Basic chaining - every line commented
class OrderNotFound(Exception):  # our domain error
    pass  # no extra behaviour needed


orders: dict[int, str] = {1: "biryani"}  # tiny fake database


def get_order(order_id: int) -> str:  # lookup function
    try:  # low-level operation
        return orders[order_id]  # KeyError if missing
    except KeyError as exc:  # catch the low-level error
        raise OrderNotFound(f"order {order_id} missing") from exc  # chain with cause


try:  # call it
    get_order(99)  # this id does not exist
except OrderNotFound as err:  # catch the domain error
    print("error:", err)  # our message
    # Output: error: order 99 missing
    print("cause:", repr(err.__cause__))  # the original KeyError
    # Output: cause: KeyError(99)
    print("suppress_context:", err.__suppress_context__)  # True because of `from`
    # Output: suppress_context: True
```

## 💻 Code Example — Advanced
```python
# Production style: cause vs implicit context vs from None
import traceback  # to print a formatted traceback
from typing import Optional  # type hints


class ConfigError(Exception):  # domain error
    pass


def load_port(raw: str) -> int:  # parse a port from text
    try:  # risky conversion
        return int(raw)  # ValueError for "abc"
    except ValueError as exc:  # low-level failure
        raise ConfigError(f"bad port {raw!r}") from exc  # explicit cause


def implicit(raw: str) -> int:  # raise inside except WITHOUT from
    try:
        return int(raw)
    except ValueError:
        raise ConfigError("bad port")  # __context__ is set automatically


def hidden(raw: str) -> int:  # hide the original on purpose
    try:
        return int(raw)
    except ValueError:
        raise ConfigError("bad port") from None  # no chain shown


def last_lines(fn, raw: str) -> list[str]:  # helper: capture traceback text
    try:
        fn(raw)  # will raise
    except ConfigError as exc:
        text: str = "".join(traceback.format_exception(exc))  # 3.10+ signature
        return [ln for ln in text.splitlines() if "above exception" in ln or "During handling" in ln]


print(last_lines(load_port, "abc"))  # explicit `from`
# Output: ['The above exception was the direct cause of the following exception:']
print(last_lines(implicit, "abc"))  # implicit context
# Output: ['During handling of the above exception, another exception occurred:']
print(last_lines(hidden, "abc"))  # from None
# Output: []

try:  # inspect attributes on a real failure
    hidden("abc")
except ConfigError as e:
    cause: Optional[BaseException] = e.__cause__  # None because of `from None`
    ctx: Optional[BaseException] = e.__context__  # still stored internally
    print(cause, type(ctx).__name__, e.__suppress_context__)
    # Output: None ValueError True
```

---

## 🟠 JavaScript vs Python Comparison
Modern JavaScript (ES2022) has `new Error(msg, { cause })`. Python has had `raise ... from ...` since 3.0 and also chains automatically.

```python
# Python way
try:
    int("x")
except ValueError as e:
    raise RuntimeError("config failed") from e   # cause = e
```
```javascript
// JavaScript way (ES2022)
try {
  JSON.parse("{bad");
} catch (e) {
  throw new Error("config failed", { cause: e }); // cause = e
}
// later: err.cause
```

Key differences: Python also sets `__context__` automatically when you raise inside `except`; JS does not. Python prints the whole chain in the traceback by default; JS prints `cause` only in newer runtimes.

---

## 🟠 FastAPI Connection
In routes, convert infrastructure errors to `HTTPException` with `from exc`, so your logs keep the real database/network error while the client sees a clean status code.

```python
# FastAPI: keep the real cause while returning a clean HTTP error
from fastapi import FastAPI, HTTPException  # app and HTTP error

app: FastAPI = FastAPI()  # create app
USERS: dict[int, str] = {1: "Aditya"}  # fake store


@app.get("/users/{user_id}")  # GET /users/1
def get_user(user_id: int) -> dict[str, str]:
    try:
        return {"name": USERS[user_id]}  # KeyError if unknown
    except KeyError as exc:  # low-level error
        raise HTTPException(status_code=404, detail="user not found") from exc  # chained
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Raising a new error and losing the original
```python
# Wrong - the KeyError message is swallowed by a vague error
try:
    d = {}["a"]
except KeyError:
    raise RuntimeError("failed")      # chain exists only implicitly, easy to misread

# Right - say explicitly that this is the cause
try:
    d = {}["a"]
except KeyError as exc:
    raise RuntimeError("failed") from exc
```

❌ Mistake 2: Using `from None` everywhere
```python
# Wrong - hides the real bug, debugging becomes guesswork
except Exception:
    raise ServiceError("failed") from None

# Right - use `from None` only when the cause is noise (e.g. internal lookup)
except Exception as exc:
    raise ServiceError("failed") from exc
```

❌ Mistake 3: `raise X from "text"` (cause must be an exception)
```python
# Wrong
# raise ValueError("a") from "reason"     # TypeError: exception causes must derive from BaseException

# Right
# raise ValueError("a") from KeyError("reason")
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
try:
    try:
        1 / 0
    except ZeroDivisionError as e:
        raise ValueError("bad") from e
except ValueError as v:
    print(type(v.__cause__).__name__, type(v.__context__).__name__)
    print(v.__cause__ is v.__context__)

try:
    try:
        1 / 0
    except ZeroDivisionError:
        raise ValueError("bad")
except ValueError as v:
    print(v.__cause__, type(v.__context__).__name__, v.__suppress_context__)
```

**Answer**:
```
ZeroDivisionError ZeroDivisionError
True
None ZeroDivisionError False
```
With `from e`, Python sets `__cause__` and the context is the same object. Without `from`, `__cause__` is `None` but `__context__` is set automatically, and `__suppress_context__` is `False` so the traceback still prints the context.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `__cause__` and `__context__`?
A1: `__cause__` is set explicitly by `raise ... from`. `__context__` is set automatically to the exception being handled when a new one is raised. Both appear in tracebacks with different wording.

Q2: What does `from None` do?
A2: It sets `__cause__ = None` and `__suppress_context__ = True`, so the traceback shows only the new exception. The old one remains in `__context__`.

Q3: When should you chain?
A3: Whenever you translate a low-level error into a domain error at a layer boundary, so logs keep the root cause.

Q4: Does chaining work with `finally` or `with`?
A4: Yes. If a new exception is raised while handling another (even inside `finally`), `__context__` is set automatically.

Q5: How to print the full chain?
A5: `traceback.print_exception(exc)` or `logging.exception(...)` inside the `except` block; both include the chain.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Translating infrastructure errors to domain errors
- Wrapping third-party library errors in your own
- You want logs to show root cause and high-level error

❌ Avoid when:
- You can just let the original exception propagate
- The cause would leak secrets to the client (log it, do not send it) - use `from None` for the public error only if you logged the cause elsewhere

---

## 📊 Visual Diagram

```
KeyError(99)  ──── __cause__ ────►  OrderNotFound("order 99 missing")
   (root)        raise ... from            (what the caller sees)

Traceback prints:
  KeyError: 99
  The above exception was the direct cause of the following exception:
  OrderNotFound: order 99 missing
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__cause__` | Explicit cause set by `from` | `from` से set हुआ कारण |
| `__context__` | Exception being handled when new one was raised | जो exception handle हो रही थी |
| `__suppress_context__` | Hide context in traceback | traceback में context छुपाना |
| `raise from None` | Drop the chain display | chain दिखाना बंद |
| Traceback | Printed call stack of an error | error का call stack |
| Layer boundary | Where one module calls another | एक layer से दूसरी layer की सीमा |

---

## ⚡ 3-Line Summary
English: `raise New from old` links the original cause to your new exception. Raising inside `except` without `from` chains implicitly via `__context__`. Use `from None` only to hide noise.
Hindi: `raise New from old` नई exception को असली कारण से जोड़ता है। `except` के अंदर बिना `from` के raise करने पर `__context__` से अपने-आप chain बनती है। `from None` सिर्फ़ फालतू noise छुपाने के लिए इस्तेमाल करें।

---

## ➡️ Next Topic
**267. Suppressing Exceptions** — when and how to ignore an error safely.
