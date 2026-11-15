---

# 274. ExceptionGroup Handling
# हिंदी में: ExceptionGroup को संभालना (nested groups, split, TaskGroup)

---

## 🔵 Simple Definition (English)
Handling an `ExceptionGroup` means using `except*` clauses (or `split`/`subgroup`) to deal with each error type, knowing that groups can be nested, unhandled parts are re-raised, and `asyncio.TaskGroup` produces groups when child tasks fail.

## 🔵 सरल परिभाषा (Hindi)
`ExceptionGroup` संभालने का मतलब है हर error type के लिए `except*` clauses (या `split`/`subgroup`) इस्तेमाल करना, यह जानते हुए कि groups nested हो सकते हैं, न संभला हुआ हिस्सा दोबारा raise होता है, और child tasks fail होने पर `asyncio.TaskGroup` group बनाता है।

---

## 🔴 Problem it Solves
After you get a group, you still need to decide what to do with each member: retry network errors, report validation errors, let bugs crash. Writing manual loops over `.exceptions` is error-prone, especially with nested groups. `except*`, `split` and `subgroup` do this filtering for you.

## 🔴 यह क्यों बना? (Hindi)
Group मिलने के बाद भी हर सदस्य पर निर्णय लेना होता है: network errors retry करना, validation errors दिखाना, bugs को crash होने देना। `.exceptions` पर हाथ से loops लिखना गलतियों वाला है, खासकर nested groups में। `except*`, `split` और `subgroup` यह छँटाई आपके लिए करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A group is raised (by your code or by asyncio.TaskGroup)
Step 2 → Each except* clause is checked; it receives a NEW group with only matching members
Step 3 → Nested groups keep their shape in the matching subgroup
Step 4 → Handled members are removed; the remainder is re-raised after the last clause
Step 5 → Use group.split(type) or subgroup(predicate) when you are not in a try
Step 6 → Use add_note() to attach context (job id, user id) to the group
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Group raise होता है (आपके code से या asyncio.TaskGroup से)
Step 2 → हर except* clause चेक होता है; उसे सिर्फ़ matching सदस्यों वाला NEW group मिलता है
Step 3 → Nested groups matching subgroup में अपना आकार रखते हैं
Step 4 → संभले हुए सदस्य हट जाते हैं; बाकी आख़िरी clause के बाद दोबारा raise होते हैं
Step 5 → try के बाहर group.split(type) या subgroup(predicate) इस्तेमाल करें
Step 6 → add_note() से context (job id, user id) group में जोड़ें
```

---

## 🟡 Real World Example
A Swiggy dashboard fetches menu, offers and ratings with `asyncio.TaskGroup`. If offers and ratings both fail, `except* ConnectionError` retries them while a `KeyError` (a bug) is left to crash and show up in the logs. Notes like `job=42` help support engineers trace the failure.

## 🟡 Real Example Hindi mein
Swiggy dashboard menu, offers और ratings `asyncio.TaskGroup` से लाता है। अगर offers और ratings दोनों fail हों तो `except* ConnectionError` उन्हें retry करता है जबकि `KeyError` (bug) crash होकर logs में दिखती है। `job=42` जैसे notes support engineers को failure trace करने में मदद करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic handling: except*, nested groups, split/subgroup, re-raise
group = ExceptionGroup("outer", [  # nested structure
    ValueError("v1"),  # leaf
    ExceptionGroup("inner", [KeyError("k1"), ValueError("v2")]),  # nested group
])  # end

try:  # handle
    raise group  # raise
except* ValueError as eg:  # except* gives a group with only the matching parts (shape kept)
    print("values:", [str(e) for e in eg.exceptions])  # may contain a nested group, not only leaves
    print(type(eg).__name__)  # always an ExceptionGroup
except* KeyError as eg:  # separate handler for KeyError
    print("keys:", repr(eg.exceptions[0]))  # inspect nested

print(group.exceptions)  # original structure remains
sub = group.subgroup(lambda e: isinstance(e, KeyError))  # filter with a predicate
print(repr(sub))  # keeps nesting shape

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# values: ['v1', 'inner (1 sub-exception)']
# ExceptionGroup
# keys: ExceptionGroup('inner', [KeyError('k1')])
# (ValueError('v1'), ExceptionGroup('inner', [KeyError('k1'), ValueError('v2')]))
# ExceptionGroup('outer', [ExceptionGroup('inner', [KeyError('k1')])])
```

## 💻 Code Example — Advanced
```python
# Production style: asyncio.TaskGroup collects concurrent failures (3.11+)
import asyncio  # event loop


async def fetch(name: str, fail: type[Exception] | None) -> str:  # fake API call
    await asyncio.sleep(0.01)  # simulate network
    if fail is not None:  # should this one fail?
        raise fail(f"{name} failed")  # raise given error
    return f"{name} ok"  # success


async def main() -> None:  # driver
    try:  # TaskGroup raises an ExceptionGroup
        async with asyncio.TaskGroup() as tg:  # structured concurrency
            tg.create_task(fetch("users", None))  # fine
            tg.create_task(fetch("orders", ValueError))  # fails
            tg.create_task(fetch("stock", ConnectionError))  # fails
    except* ValueError as eg:  # handle value errors
        print("value errors:", [str(e) for e in eg.exceptions])  # list
    except* ConnectionError as eg:  # handle network errors
        print("network errors:", [str(e) for e in eg.exceptions])  # list


asyncio.run(main())  # run


# Re-raising and notes
def handle() -> None:  # partial handling
    try:  # raise a group
        raise ExceptionGroup("g", [ValueError("v"), OSError("o")])  # two errors
    except* ValueError:  # handle value errors
        print("handled value error")  # printed
    # OSError part is NOT handled -> automatically re-raised as a smaller group


try:  # call
    handle()  # leftover group escapes
except* OSError as eg:  # catch leftover
    print("leftover:", repr(eg.exceptions[0]))  # OSError('o')
eg2 = ExceptionGroup("g", [ValueError("v")])  # new group
eg2.add_note("job=42")  # attach context (3.11+)
print(eg2.__notes__)  # ['job=42']

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# value errors: ['orders failed']
# network errors: ['stock failed']
# handled value error
# leftover: OSError('o')
# ['job=42']
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript's `Promise.allSettled` returns every result and `Promise.any` rejects with `AggregateError`. You loop and filter by hand. Python's `TaskGroup` also cancels sibling tasks when one fails, which `Promise.all` does not (the other promises keep running).

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(a()); tg.create_task(b())
except* ConnectionError as eg:
    print(len(eg.exceptions))
```
```javascript
const results = await Promise.allSettled([a(), b()]);
const failed = results.filter(r => r.status === 'rejected');
console.log(failed.length);   // manual filtering
```

Key differences: Python cancels the remaining tasks on first failure and aggregates errors with type-based handlers. JS `Promise.all` rejects on the first error and does not cancel the other promises.

---

## 🟠 FastAPI Connection
In async endpoints use `asyncio.TaskGroup` for fan-out calls, catch `except* SomeError`, set a variable, and build the response after the `try` (no `return` inside `except*`). Map downstream failures to 502/503 and log the full group once.

```python
# FastAPI: gather() with return_exceptions vs TaskGroup, translating a group to HTTP
import asyncio  # concurrency
from fastapi import FastAPI  # app
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app


async def call(svc: str) -> str:  # downstream call
    await asyncio.sleep(0)  # yield
    if svc == "bad":  # failing service
        raise ConnectionError("bad down")  # failure
    return svc  # ok


@app.get("/dashboard")  # fan-out endpoint
async def dashboard() -> JSONResponse:
    failed: int = 0  # return is not allowed inside except*, so record the count
    try:  # run concurrently
        async with asyncio.TaskGroup() as tg:  # cancels siblings on first failure
            tasks = [tg.create_task(call(s)) for s in ("users", "bad")]  # start tasks
    except* ConnectionError as eg:  # downstream failure(s)
        failed = len(eg.exceptions)  # remember how many
    if failed:  # decide AFTER the try statement
        return JSONResponse(status_code=502, content={"failed": failed})  # bad gateway
    return JSONResponse({"data": [t.result() for t in tasks]})  # success path


c = TestClient(app)  # client
r = c.get("/dashboard")  # call
print(r.status_code, r.json())  # 502 with count

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 502 {'failed': 1}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `return` / `break` inside `except*`
```python
# Wrong
except* ValueError:
    return 1  # SyntaxError

# Right
status = 400
...
return status  # after the try
```

❌ Mistake 2: Assuming `eg.exceptions` holds only leaves
```python
# Wrong
for e in eg.exceptions:
    print(type(e))  # may be a nested ExceptionGroup

# Right
# Walk recursively, or use split()/subgroup() to filter
```

❌ Mistake 3: Catching the group with `except Exception` and losing members
```python
# Wrong
except Exception as e:
    log(e)   # prints only 'N sub-exceptions'

# Right
except* Exception as eg:
    for e in eg.exceptions: log(e)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
eg = ExceptionGroup("g", [ValueError("a"), ValueError("b"), KeyError("c")])  # group

try:  # handle only part
    try:  # inner
        raise eg  # raise
    except* ValueError as inner:  # handles 2 values
        print("inner", len(inner.exceptions))  # 2
except* KeyError as outer:  # rest propagates
    print("outer", len(outer.exceptions))  # 1

try:  # mixing except and except* is illegal
    compile("try:\n pass\nexcept ValueError:\n pass\nexcept* KeyError:\n pass", "x", "exec")  # syntax check
except SyntaxError as e:  # caught
    print("SyntaxError:", e.msg)  # reason

try:  # return/break inside except* is illegal
    compile("def f():\n try:\n  pass\n except* ValueError:\n  return 1", "x", "exec")  # check
except SyntaxError as e:  # caught
    print("SyntaxError:", e.msg)  # reason

try:  # except* needs exception types, not BaseExceptionGroup
    raise ValueError("plain")  # a plain exception
except* ValueError as e:  # plain errors are wrapped into a group
    print(type(e).__name__, [str(x) for x in e.exceptions])  # ExceptionGroup ['plain']
```

**Answer**:
```
inner 2
outer 1
SyntaxError: cannot have both 'except' and 'except*' on the same 'try'
SyntaxError: 'break', 'continue' and 'return' cannot appear in an except* block
ExceptionGroup ['plain']
```
`except* ValueError` handles the two `ValueError`s (inner 2) and the `KeyError` remains, so the outer `except*` gets 1. Mixing `except` and `except*` in one `try` is a `SyntaxError`, and so is `return` inside `except*`. A plain (non-group) exception caught by `except*` is automatically wrapped in an `ExceptionGroup`.

---

## ⚫ Interview Questions + Answers

Q1: What does a TaskGroup do when one task fails?
A1: It cancels the other tasks, waits for them, then raises an `ExceptionGroup` with all failures (cancellations are not included).

Q2: `split` vs `subgroup`?
A2: `split` returns (matching, rest) pair; `subgroup` returns only the matching part. Both accept a type, tuple of types or a predicate and keep nesting.

Q3: What are exception notes?
A3: `add_note('text')` (3.11+) stores strings in `__notes__`, shown after the traceback. Good for adding ids without wrapping the error.

Q4: Can you handle a plain exception with `except*`?
A4: Yes, it is wrapped into an `ExceptionGroup` first, so the handler always sees a group.

Q5: Is there a backport for Python < 3.11?
A5: Yes: the `exceptiongroup` package provides `ExceptionGroup` and a `catch()` helper (no `except*` syntax).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Handling errors from asyncio.TaskGroup
- Collecting independent validation failures
- Handling different member types differently (retry vs report)

❌ Avoid when:
- Single-failure code paths
- Looping over `.exceptions` by hand for nested groups
- Mixing `except` and `except*`

---

## 📊 Visual Diagram

```
TaskGroup
 ├─ task A ✔
 ├─ task B ✖ ValueError  ─┐
 └─ task C ✖ OSError     ─┤ ExceptionGroup
                           ▼
 except* ValueError → handle B
 except* OSError    → handle C
 (anything left     → re-raised)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| nested group | Group inside a group | group के अंदर group |
| subgroup | Matching part of a group | group का matching हिस्सा |
| split | Match + rest | match और बाकी |
| add_note | Attach extra text | अतिरिक्त text जोड़ना |
| TaskGroup | Cancels siblings on failure | failure पर बाकी tasks रोकता है |
| fan-out | Many calls in parallel | एक साथ कई calls |

---

## ⚡ 3-Line Summary
English: Handle groups with one `except*` per error family, remember unmatched members are re-raised, nested groups keep their shape, and `TaskGroup` raises groups. Use `split`/`subgroup` outside `try`, and never `return` inside `except*`.
Hindi: हर error family के लिए एक `except*` लिखें, याद रखें कि unmatched सदस्य दोबारा raise होते हैं, nested groups अपना आकार रखते हैं, और `TaskGroup` groups raise करता है। `try` के बाहर `split`/`subgroup` इस्तेमाल करें और `except*` में कभी `return` न करें।

---

## ➡️ Next Topic
**275. Traceback Module** — read, format and capture tracebacks in code.

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.

Requires Python 3.11+ (verified on 3.13).
