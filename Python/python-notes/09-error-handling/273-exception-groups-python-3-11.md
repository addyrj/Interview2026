---

# 273. Exception Groups (Python 3.11+)
# हिंदी में: Exception Groups (एक साथ कई errors, Python 3.11+)

---

## 🔵 Simple Definition (English)
`ExceptionGroup` (Python 3.11+) bundles several unrelated exceptions into one object so they can be raised and handled together. The new `except*` syntax handles the matching members and lets the rest continue to propagate.

## 🔵 सरल परिभाषा (Hindi)
`ExceptionGroup` (Python 3.11+) कई अलग-अलग exceptions को एक object में बाँधता है ताकि उन्हें एक साथ raise और handle किया जा सके। नया `except*` syntax matching सदस्यों को संभालता है और बाकी को आगे जाने देता है।

---

## 🔴 Problem it Solves
Normal Python can raise only one exception at a time. With concurrent tasks (asyncio, threads) or batch validation, several things fail together and the extra errors were lost. `ExceptionGroup` keeps all of them, so nothing is hidden.

## 🔴 यह क्यों बना? (Hindi)
सामान्य Python एक समय में सिर्फ़ एक exception raise कर सकता है। Concurrent tasks (asyncio, threads) या batch validation में कई चीज़ें साथ में fail होती हैं और बाकी errors खो जाती थीं। `ExceptionGroup` सबको रखता है, कुछ छुपता नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create ExceptionGroup(message, [err1, err2, ...]) with a non-empty list
Step 2 → raise it like any exception
Step 3 → A normal except ExceptionGroup catches the whole bundle
Step 4 → except* ValueError handles only the ValueError members (as a smaller group)
Step 5 → Members not handled by any except* are re-raised automatically as a new group
Step 6 → Several except* clauses can run for one raise, one per matching type
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ExceptionGroup(message, [err1, err2, ...]) बनाएँ, list खाली नहीं होनी चाहिए
Step 2 → इसे किसी भी exception की तरह raise करें
Step 3 → सामान्य except ExceptionGroup पूरा bundle पकड़ता है
Step 4 → except* ValueError सिर्फ़ ValueError सदस्यों को (छोटे group के रूप में) संभालता है
Step 5 → जिन सदस्यों को कोई except* नहीं संभालता वे अपने-आप नए group में दोबारा raise हो जाते हैं
Step 6 → एक raise पर कई except* चल सकते हैं, हर matching type के लिए एक
```

---

## 🟡 Real World Example
A Razorpay bulk-refund API validates 500 rows and returns ALL bad rows at once instead of failing on the first. An asyncio dashboard calls 5 microservices in a `TaskGroup`; if two fail, you get both errors in one `ExceptionGroup`.

## 🟡 Real Example Hindi mein
Razorpay की bulk-refund API 500 rows validate करती है और पहली पर fail होने की जगह सभी गलत rows एक साथ लौटाती है। asyncio dashboard `TaskGroup` में 5 microservices बुलाता है; दो fail हों तो दोनों errors एक `ExceptionGroup` में मिलती हैं।

---

## 💻 Code Example — Basic
```python
# Basic ExceptionGroup (Python 3.11+) - every line commented
eg = ExceptionGroup("batch failed", [ValueError("bad qty"), TypeError("bad price"), KeyError("sku")])  # bundle 3 errors
print(eg)  # message and count
print(eg.message, len(eg.exceptions))  # message + number of sub-errors
print([type(e).__name__ for e in eg.exceptions])  # types inside

try:  # raise the group
    raise eg  # whole group raised at once
except ExceptionGroup as caught:  # a normal except catches the group
    print("caught group with", len(caught.exceptions), "errors")  # count

try:  # except* syntax splits the group by type
    raise eg  # raise again
except* ValueError as g:  # handles only the ValueError part
    print("ValueError part:", g.exceptions)  # tuple of ValueErrors
except* TypeError as g:  # handles only the TypeError part
    print("TypeError part:", g.exceptions)  # tuple of TypeErrors
except* KeyError as g:  # handles the KeyError part
    print("KeyError part:", g.exceptions)  # tuple of KeyErrors

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# batch failed (3 sub-exceptions)
# batch failed 3
# ['ValueError', 'TypeError', 'KeyError']
# caught group with 3 errors
# ValueError part: (ValueError('bad qty'),)
# TypeError part: (TypeError('bad price'),)
# KeyError part: (KeyError('sku'),)
```

## 💻 Code Example — Advanced
```python
# Production style: collect many validation errors, then raise ONE group
from dataclasses import dataclass  # model


@dataclass
class Row:  # one CSV row
    sku: str  # product id
    qty: int  # quantity
    price: float  # unit price


def validate(rows: list[Row]) -> None:  # validate ALL rows, report ALL problems
    errors: list[Exception] = []  # collect errors instead of stopping at the first
    for i, r in enumerate(rows):  # check every row
        if r.qty <= 0:  # bad quantity
            errors.append(ValueError(f"row {i}: qty must be > 0, got {r.qty}"))  # add error
        if r.price < 0:  # bad price
            errors.append(ValueError(f"row {i}: price must be >= 0, got {r.price}"))  # add error
        if not r.sku:  # missing sku
            errors.append(KeyError(f"row {i}: sku missing"))  # add error
    if errors:  # at least one problem
        raise ExceptionGroup("invalid import file", errors)  # raise them together


rows = [Row("a", 1, 5.0), Row("b", 0, 9.0), Row("", 2, -1.0)]  # sample data with 3 problems
try:  # run validation
    validate(rows)  # raises ExceptionGroup
except* ValueError as eg:  # handle value errors as a group
    for e in eg.exceptions:  # list each
        print("VALUE:", e)  # message
except* KeyError as eg:  # handle key errors
    for e in eg.exceptions:  # list each
        print("KEY:", e)  # message

# split() and subgroup() without try
group = ExceptionGroup("g", [ValueError("v"), OSError("o")])  # sample
match, rest = group.split(ValueError)  # split by type
print(repr(match), "|", repr(rest))  # matching part and the rest
print(group.subgroup(OSError))  # only OSError part

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# VALUE: row 1: qty must be > 0, got 0
# VALUE: row 2: price must be >= 0, got -1.0
# KEY: 'row 2: sku missing'
# ExceptionGroup('g', [ValueError('v')]) | ExceptionGroup('g', [OSError('o')])
# g (1 sub-exception)
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has `AggregateError`, which is used by `Promise.any`, and `Promise.allSettled` for collecting results. There is no `catch*` syntax to split by type.

```python
eg = ExceptionGroup('batch', [ValueError('a'), KeyError('b')])
try:
    raise eg
except* ValueError as g:
    print(g.exceptions)
```
```javascript
const err = new AggregateError([new Error('a'), new TypeError('b')], 'batch');
try { throw err; }
catch (e) { console.log(e.errors); }   // you filter by hand
```

Key differences: JS `AggregateError` only holds the list; you filter members manually. Python adds `except*` that splits by type and re-raises the unhandled remainder automatically.

---

## 🟠 FastAPI Connection
FastAPI/Starlette run on asyncio, and `asyncio.TaskGroup` raises `ExceptionGroup`. In bulk endpoints you can collect all validation errors and return them together. Note that `return`, `break` and `continue` are not allowed inside `except*`, so set a variable and decide after the `try`.

```python
# FastAPI: bulk endpoint returns ALL validation problems at once (422-style)
from fastapi import FastAPI  # app
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app


def validate_item(i: int, qty: int) -> None:  # single check
    if qty <= 0:  # invalid
        raise ValueError(f"item {i}: qty must be > 0")  # error


@app.post("/bulk")  # POST /bulk with a list of quantities
def bulk(quantities: list[int]) -> JSONResponse:
    errors: list[Exception] = []  # collect
    for i, q in enumerate(quantities):  # loop all
        try:  # one by one
            validate_item(i, q)  # check
        except ValueError as exc:  # collect instead of stopping
            errors.append(exc)  # remember
    messages: list[str] = []  # return is NOT allowed inside except*, so collect here
    try:  # raise as group (demonstrates the pattern)
        if errors:  # any problem
            raise ExceptionGroup("bulk invalid", errors)  # group
    except* ValueError as eg:  # convert group members to messages
        messages = [str(e) for e in eg.exceptions]  # no return inside except*
    if messages:  # after the try statement
        return JSONResponse(status_code=422, content={"errors": messages})  # all problems at once
    return JSONResponse({"ok": len(quantities)})  # all good


c = TestClient(app)  # client
print(c.post("/bulk", json=[1, 2]).json())  # ok
r = c.post("/bulk", json=[0, 5, -1])  # two bad
print(r.status_code, r.json())  # all problems at once

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# {'ok': 2}
# 422 {'errors': ['item 0: qty must be > 0', 'item 2: qty must be > 0']}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using plain `except ValueError` for a group
```python
# Wrong
try:
    async with asyncio.TaskGroup() as tg: ...
except ValueError:   # does not match the group

# Right
try:
    async with asyncio.TaskGroup() as tg: ...
except* ValueError:  # matches members
```

❌ Mistake 2: `return` inside `except*`
```python
# Wrong
try: ...
except* ValueError:
    return 1   # SyntaxError

# Right
result = None
try: ...
except* ValueError:
    result = 1
return result
```

❌ Mistake 3: Passing an empty list or a non-sequence
```python
# Wrong
ExceptionGroup('g', [])   # ValueError

# Right
ExceptionGroup('g', [ValueError('x')])
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
try:  # case 1: normal except with a group
    raise ExceptionGroup("g", [ValueError(1)])  # group
except ValueError:  # does NOT match (group is not a ValueError)
    print("ValueError handler")  # not printed
except Exception as e:  # matches (group is an Exception)
    print("Exception handler:", type(e).__name__)  # printed

try:  # case 2: except* unhandled part keeps propagating
    try:  # inner
        raise ExceptionGroup("g", [ValueError(1), KeyError(2)])  # two types
    except* ValueError:  # handle only value errors
        print("handled ValueError")  # printed
except* KeyError as eg:  # the rest arrives here
    print("outer got", [type(x).__name__ for x in eg.exceptions])  # KeyError

try:  # case 3: ExceptionGroup needs a non-empty list
    ExceptionGroup("g", [])  # invalid
except ValueError as e:  # catch
    print("ValueError:", e)  # message
```

**Answer**:
```
Exception handler: ExceptionGroup
handled ValueError
outer got ['KeyError']
ValueError: second argument (exceptions) must be a non-empty sequence
```
Case 1: a group is not a `ValueError`, but it is an `Exception`, so only the second handler matches. Case 2: `except* ValueError` handles its part, and the remaining `KeyError` part propagates to the outer `except*`. Case 3: an empty list is rejected with `ValueError: second argument (exceptions) must be a non-empty sequence`.

---

## ⚫ Interview Questions + Answers

Q1: What is `ExceptionGroup`?
A1: A built-in exception (3.11+) that wraps a non-empty sequence of exceptions. `BaseExceptionGroup` is the version that can hold `BaseException`s too.

Q2: `except` vs `except*`?
A2: `except` matches the group object itself. `except*` matches the members by type and may run several clauses. You cannot mix them in one `try`.

Q3: What happens to unmatched members?
A3: They are re-raised together as a new group when the `try` statement ends.

Q4: Which stdlib features raise groups?
A4: `asyncio.TaskGroup` (3.11+), plus libraries built on it or similar designs such as anyio and Trio.

Q5: How do you split a group manually?
A5: `group.split(ValueError)` returns (matching, rest); `group.subgroup(...)` returns only the matching part.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Concurrent tasks where several can fail (TaskGroup)
- Batch validation that should report every problem
- Libraries that must not hide secondary errors

❌ Avoid when:
- Simple one-error flows (use a normal exception)
- Code that must run on Python < 3.11 (use the `exceptiongroup` backport)
- Using `return`/`break` inside `except*`

---

## 📊 Visual Diagram

```
ExceptionGroup('batch')
 ├── ValueError   ──► except* ValueError  ✔ handled
 ├── TypeError    ──┐
 └── KeyError     ──┴► unmatched -> re-raised as a new group
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ExceptionGroup | Bundle of exceptions | exceptions का समूह |
| except* | Handle members by type | type के अनुसार सदस्य संभालना |
| split | Divide into match and rest | match और बाकी में बाँटना |
| subgroup | Filter a group | group को छानना |
| TaskGroup | Structured async tasks | संगठित async tasks |
| propagate | Continue upward | ऊपर जाना जारी रखना |

---

## ⚡ 3-Line Summary
English: `ExceptionGroup` carries several errors at once and `except*` handles each type separately, letting unhandled members continue. It is the foundation of `asyncio.TaskGroup` error reporting. Not allowed: mixing `except` with `except*`, or `return` inside `except*`.
Hindi: `ExceptionGroup` कई errors एक साथ ले जाता है और `except*` हर type को अलग संभालता है, जो न संभले वह आगे जाता है। `asyncio.TaskGroup` की error reporting इसी पर टिकी है। मना है: `except` और `except*` मिलाना, और `except*` में `return`।

---

## ➡️ Next Topic
**274. ExceptionGroup Handling** — nested groups, `split`, `subgroup`, notes and TaskGroup patterns.

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.

Requires Python 3.11+ (verified on 3.13).
