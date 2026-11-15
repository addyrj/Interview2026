---

# 269. warnings Module
# हिंदी में: warnings Module (चेतावनियाँ)

---

## 🔵 Simple Definition (English)
The `warnings` module prints soft alerts such as "this function is deprecated" without stopping the program. Filters decide whether a warning is shown once, always, ignored, or turned into a real exception.

## 🔵 सरल परिभाषा (Hindi)
`warnings` module "यह function पुराना हो गया है" जैसी हल्की चेतावनियाँ छापता है और program रोकता नहीं। Filters तय करते हैं कि warning एक बार दिखे, हर बार दिखे, ignore हो या असली exception बन जाए।

---

## 🔴 Problem it Solves
Libraries need to tell users "this API will be removed" before breaking them. Raising an exception would break everyone immediately, and `print` cannot be filtered or tested. Warnings give a controlled, filterable, testable way to say "works now, but fix it soon".

## 🔴 यह क्यों बना? (Hindi)
Libraries को users को पहले बताना पड़ता है कि "यह API हटने वाली है", तोड़ने से पहले। Exception raise करने से सब तुरंत टूट जाते हैं और `print` को filter या test नहीं किया जा सकता। Warnings "अभी चलता है, पर जल्दी ठीक करो" कहने का नियंत्रित, filter और test योग्य तरीका देती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Code calls warnings.warn(message, Category, stacklevel)
Step 2 → Python looks at the filter list (first match wins)
Step 3 → Action can be: default, always, once, module, ignore, error
Step 4 → default prints once per code location; error raises the warning as an exception
Step 5 → stacklevel=2 points the message at the CALLER's line, not the library line
Step 6 → catch_warnings() temporarily saves and restores filters (used in tests)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Code warnings.warn(message, Category, stacklevel) बुलाता है
Step 2 → Python filter list देखता है (पहला match जीतता है)
Step 3 → Action हो सकता है: default, always, once, module, ignore, error
Step 4 → default हर code location पर एक बार छापता है; error warning को exception बना देता है
Step 5 → stacklevel=2 message को library की नहीं, CALLER की line पर दिखाता है
Step 6 → catch_warnings() filters को अस्थायी रूप से सहेजकर बाद में लौटाता है (tests में काम आता है)
```

---

## 🟡 Real World Example
Pydantic and SQLAlchemy warn before removing an old API, so Razorpay's team sees `DeprecationWarning` in pytest and upgrades code in time. In CI you run `pytest -W error::DeprecationWarning` so new deprecated calls fail the build.

## 🟡 Real Example Hindi mein
Pydantic और SQLAlchemy पुरानी API हटाने से पहले warn करते हैं, इसलिए Razorpay की team pytest में `DeprecationWarning` देखकर समय पर code बदल लेती है। CI में `pytest -W error::DeprecationWarning` चलाते हैं ताकि नई deprecated calls build fail कर दें।

---

## 💻 Code Example — Basic
```python
# Basic warnings module - every line commented
import warnings  # standard library module

warnings.simplefilter("default")  # show each warning location once


def old_api() -> int:  # a function we want to retire
    warnings.warn("old_api() is deprecated, use new_api()", DeprecationWarning, stacklevel=2)  # soft alert
    return 1  # still works


with warnings.catch_warnings(record=True) as caught:  # capture warnings in a list
    warnings.simplefilter("always")  # do not hide repeats
    old_api()  # triggers DeprecationWarning
    old_api()  # triggers again (always)
print(len(caught), caught[0].category.__name__)  # how many and which type
print(str(caught[0].message))  # the message text

with warnings.catch_warnings():  # temporary filter change
    warnings.simplefilter("error")  # turn warnings INTO exceptions
    try:  # try the call
        old_api()  # now raises
    except DeprecationWarning as exc:  # warnings are Exception subclasses
        print("raised as error:", exc)  # shows message

with warnings.catch_warnings():  # temporary filter change
    warnings.simplefilter("ignore")  # silence everything
    old_api()  # prints nothing
print("ignored silently")  # reached

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 2 DeprecationWarning
# old_api() is deprecated, use new_api()
# raised as error: old_api() is deprecated, use new_api()
# ignored silently
```

## 💻 Code Example — Advanced
```python
# Production style: deprecation decorator, targeted filters, custom category
import functools  # wraps
import warnings  # module
from typing import Callable, ParamSpec, TypeVar  # typing helpers

P = ParamSpec("P")  # parameters of wrapped function
R = TypeVar("R")  # return type


class PricingWarning(UserWarning):  # our own category (can be filtered alone)
    """Raised for suspicious but non-fatal pricing data."""


def deprecated(reason: str) -> Callable[[Callable[P, R]], Callable[P, R]]:  # decorator factory
    def deco(fn: Callable[P, R]) -> Callable[P, R]:  # real decorator
        @functools.wraps(fn)  # keep name and docstring
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # replacement function
            warnings.warn(f"{fn.__name__} is deprecated: {reason}", DeprecationWarning, stacklevel=2)  # blame caller
            return fn(*args, **kwargs)  # call original
        return wrapper  # return wrapper
    return deco  # return decorator


@deprecated("use total_v2()")  # mark old function
def total(prices: list[float]) -> float:  # old function
    return sum(prices)  # simple sum


def apply_coupon(price: float, pct: float) -> float:  # business function
    if pct > 90:  # suspicious but allowed
        warnings.warn(f"coupon {pct}% looks too high", PricingWarning, stacklevel=2)  # soft alert
    return price * (1 - pct / 100)  # discounted price


with warnings.catch_warnings(record=True) as w:  # capture everything
    warnings.simplefilter("always")  # no deduplication
    print(total([1.0, 2.0]))  # returns 3.0 and warns
    print(apply_coupon(100.0, 95.0))  # returns 5.0 and warns
for item in w:  # inspect captured warnings
    print(item.category.__name__, "|", item.message, "| line", item.lineno)  # category, text, caller line

with warnings.catch_warnings():  # isolate filter changes
    warnings.filterwarnings("error", category=PricingWarning)  # only our category becomes an error
    try:  # test
        apply_coupon(100.0, 99.0)  # raises now
    except PricingWarning as exc:  # catch as exception
        print("blocked:", exc)  # show message

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 3.0
# 5.000000000000004
# DeprecationWarning | total is deprecated: use total_v2() | line 37
# PricingWarning | coupon 95.0% looks too high | line 38
# blocked: coupon 99.0% looks too high
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has `console.warn()` which only prints text. Node has `process.emitWarning()` which is closer, but there are no built-in categories or filters in browsers.

```python
import warnings
warnings.warn('old API', DeprecationWarning, stacklevel=2)
warnings.simplefilter('error')   # now it raises
```
```javascript
console.warn('old API');                     // just text
process.emitWarning('old API', 'DeprecationWarning'); // Node only
// no filters to turn it into an error
```

Key differences: Python warnings have categories, filters, a once-per-location rule, and can be converted to exceptions or captured in tests. `console.warn` is only output.

---

## 🟠 FastAPI Connection
FastAPI has `deprecated=True` on routes (shown struck-through in `/docs`). Combine it with `warnings.warn` for developer logs. In tests, run pytest with `-W error` to catch accidental use of deprecated libraries.

```python
# FastAPI: warn about a deprecated route and test it with pytest-style capture
import warnings  # module
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app


@app.get("/v1/users", deprecated=True)  # shows as deprecated in /docs (OpenAPI)
def users_v1() -> list[str]:
    warnings.warn("/v1/users will be removed in 2.0", DeprecationWarning, stacklevel=2)  # log for devs
    return ["a", "b"]  # still works


c = TestClient(app)  # client
with warnings.catch_warnings(record=True) as w:  # capture
    warnings.simplefilter("always")  # all warnings
    r = c.get("/v1/users")  # call
print(r.status_code, r.json())  # 200 still served
print([str(x.message) for x in w if x.category is DeprecationWarning])  # our warning
print(app.openapi()["paths"]["/v1/users"]["get"]["deprecated"])  # flagged in OpenAPI

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 200 ['a', 'b']
# ['/v1/users will be removed in 2.0']
# True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `print` or `logging` for deprecations
```python
# Wrong
def old():
    print('deprecated!')  # cannot be filtered or tested

# Right
import warnings
def old():
    warnings.warn('deprecated', DeprecationWarning, stacklevel=2)
```

❌ Mistake 2: Forgetting `stacklevel=2`
```python
# Wrong
warnings.warn('use new()', DeprecationWarning)  # points inside your library

# Right
warnings.warn('use new()', DeprecationWarning, stacklevel=2)  # points to the caller
```

❌ Mistake 3: Expecting `DeprecationWarning` to show in scripts
```python
# Wrong
# Default filters hide DeprecationWarning unless triggered in __main__ (or under pytest)

# Right
# Run with: python -W default script.py   or   python -X dev script.py
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import warnings  # module

def f() -> None:  # emits a warning
    warnings.warn("careful", UserWarning)  # same line every time

warnings.simplefilter("default")  # default action: once per location
with warnings.catch_warnings(record=True) as w:  # capture
    warnings.simplefilter("default")  # once per location
    for _ in range(3):  # call three times
        f()  # same location
    print("default:", len(w))  # one only
with warnings.catch_warnings(record=True) as w:  # capture again
    warnings.simplefilter("always")  # every time
    for _ in range(3):  # three calls
        f()  # warns each time
    print("always:", len(w))  # three
print(issubclass(DeprecationWarning, Exception), issubclass(UserWarning, Warning))  # True True
```

**Answer**:
```
default: 1
always: 3
True True
```
With the `default` action each unique location warns once, so three calls from one place give 1; `always` gives 3. Warnings are classes: `DeprecationWarning` inherits from `Warning`, which inherits from `Exception`, which is why `simplefilter('error')` can raise them.

---

## ⚫ Interview Questions + Answers

Q1: DeprecationWarning vs FutureWarning?
A1: `DeprecationWarning` is for developers (hidden by default outside `__main__`/tests). `FutureWarning` is for end users of apps and shown by default.

Q2: What does `stacklevel` do?
A2: It chooses which stack frame the warning is attributed to. 2 = the caller of your function.

Q3: How to turn warnings into errors?
A3: `warnings.simplefilter('error')`, `python -W error`, or `pytest -W error`.

Q4: How to test that a warning is raised?
A4: `with pytest.warns(DeprecationWarning):` or `warnings.catch_warnings(record=True)`.

Q5: Is `catch_warnings` thread safe?
A5: No. It modifies global state. Use it in tests, not in concurrent production code.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Announcing an API will be removed
- Soft problems: suspicious but valid input
- Making CI fail on deprecated usage with `-W error`

❌ Avoid when:
- Real errors (raise an exception)
- Runtime monitoring (use logging)
- Spamming warnings inside hot loops

---

## 📊 Visual Diagram

```
warnings.warn(msg, Category, stacklevel=2)
          │
   filter list (first match)
   ┌──────┼──────────┬──────────┐
 default  always     ignore     error
 (once/   (every     (silent)   (raise as
 location) time)                 exception)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Warning | Base class of warnings | warnings की base class |
| DeprecationWarning | Feature will be removed | feature हटने वाला है |
| UserWarning | Default category | default category |
| filter | Rule for what to do | क्या करना है का नियम |
| stacklevel | Which caller to blame | किस caller को दोष देना है |
| catch_warnings | Temporarily change filters | filters अस्थायी बदलना |

---

## ⚡ 3-Line Summary
English: `warnings.warn()` gives a soft, filterable alert that does not stop the program. Pick a category, use `stacklevel=2`, and control behaviour with filters or `-W`. Use `-W error` in CI to fail on deprecations.
Hindi: `warnings.warn()` हल्की, filter होने वाली चेतावनी देता है जो program नहीं रोकती। Category चुनें, `stacklevel=2` रखें और filters या `-W` से व्यवहार नियंत्रित करें। Deprecations पर fail करने के लिए CI में `-W error` लगाएँ।

---

## ➡️ Next Topic
**270. Assertion (assert statement)** — sanity checks for bugs (not for user input).

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.

Note: `catch_warnings` is not thread-safe (global state); examples are single-threaded.
