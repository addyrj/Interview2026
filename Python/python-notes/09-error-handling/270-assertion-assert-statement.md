---

# 270. Assertion (assert statement)
# हिंदी में: Assertion (assert statement, जाँच-शर्त)

---

## 🔵 Simple Definition (English)
`assert condition, message` checks that something you believe is always true really is. If the condition is false, it raises `AssertionError` with the message. It is a debugging and testing tool, not input validation.

## 🔵 सरल परिभाषा (Hindi)
`assert condition, message` जाँचता है कि जो बात आप हमेशा सही मानते हैं वह सच में सही है। Condition false हो तो message के साथ `AssertionError` आती है। यह debugging और testing का tool है, user input की validation नहीं।

---

## 🔴 Problem it Solves
Some bugs corrupt data silently and crash much later, far from the cause. An `assert` stops the program at the exact place where an assumption (invariant) breaks, so you find the bug fast. In tests, `assert` is the main way to check results.

## 🔴 यह क्यों बना? (Hindi)
कुछ bugs data को चुपचाप बिगाड़ते हैं और बहुत बाद में, कारण से दूर crash करते हैं। `assert` ठीक उसी जगह program रोक देता है जहाँ कोई धारणा (invariant) टूटती है, इसलिए bug जल्दी मिलता है। Tests में नतीजे जाँचने का मुख्य तरीका `assert` ही है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python evaluates the condition
Step 2 → If it is truthy, nothing happens
Step 3 → If it is falsy, AssertionError(message) is raised
Step 4 → With python -O (or PYTHONOPTIMIZE) assert lines are removed completely
Step 5 → So never put needed logic or validation inside an assert
Step 6 → pytest rewrites asserts to show helpful diffs on failure
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python condition evaluate करता है
Step 2 → सही (truthy) हो तो कुछ नहीं होता
Step 3 → गलत (falsy) हो तो AssertionError(message) उठती है
Step 4 → python -O (या PYTHONOPTIMIZE) में assert lines पूरी तरह हट जाती हैं
Step 5 → इसलिए ज़रूरी logic या validation कभी assert में न रखें
Step 6 → pytest असफल होने पर साफ़ diff दिखाने के लिए assert को rewrite करता है
```

---

## 🟡 Real World Example
A Razorpay settlement function asserts `total_debit == total_credit` after computing ledger entries, so a bug in the maths is caught in tests immediately. Every pytest test for a FastAPI endpoint uses `assert response.status_code == 200`. User input like quantity is checked with `if ... raise ValueError`, never with assert.

## 🟡 Real Example Hindi mein
Razorpay का settlement function ledger entries बनाने के बाद `total_debit == total_credit` assert करता है, ताकि गणित का bug tests में तुरंत पकड़ा जाए। FastAPI endpoint के हर pytest test में `assert response.status_code == 200` होता है। Quantity जैसा user input `if ... raise ValueError` से जाँचा जाता है, assert से कभी नहीं।

---

## 💻 Code Example — Basic
```python
# Basic assert statement - every line commented
def average(nums: list[float]) -> float:  # compute average
    assert len(nums) > 0, "nums must not be empty"  # internal sanity check with message
    return sum(nums) / len(nums)  # safe division


print(average([2, 4, 6]))  # works: 4.0

try:  # failing assert
    average([])  # AssertionError
except AssertionError as exc:  # catch only to demo
    print("AssertionError:", exc)  # message after the comma

x: int = 5  # sample value
assert x == 5  # passes silently
assert isinstance(x, int), "x must be int"  # type sanity check
print("asserts passed")  # reached

try:  # assert with a tuple - classic bug
    assert (x == 6, "message")  # non-empty tuple is always truthy!
    print("tuple assert never fails")  # reached
except AssertionError:  # not raised
    print("failed")  # not printed
print(__debug__)  # True unless python -O is used

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 4.0
# AssertionError: nums must not be empty
# asserts passed
# tuple assert never fails
# True
```

## 💻 Code Example — Advanced
```python
# Production style: assert for invariants, exceptions for validation, -O behaviour
import subprocess  # to run a child python with -O
import sys  # to find the interpreter
from dataclasses import dataclass  # simple model


@dataclass
class Order:  # domain object
    qty: int  # quantity
    price: float  # unit price

    def total(self) -> float:  # compute total
        assert self.qty >= 0 and self.price >= 0, f"corrupt order {self}"  # invariant (our bug if false)
        return self.qty * self.price  # result


def create_order(qty: int, price: float) -> Order:  # public entry (user data!)
    if qty <= 0:  # real validation uses exceptions
        raise ValueError("qty must be positive")  # always active, even with -O
    return Order(qty, price)  # build object


print(create_order(2, 99.5).total())  # 199.0
try:  # user error
    create_order(0, 10)  # ValueError
except ValueError as exc:  # catch
    print("ValueError:", exc)  # shows message

code: str = "assert False, 'boom'; print('assert skipped under -O')"  # tiny script
normal = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)  # normal mode
optim = subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True)  # optimised
print("normal exit code:", normal.returncode)  # 1 because assert fails
print("-O exit code:", optim.returncode, "|", optim.stdout.strip())  # 0, assert removed


def unreachable(kind: str) -> str:  # exhaustive branches
    if kind == "a":  # branch a
        return "A"  # result
    if kind == "b":  # branch b
        return "B"  # result
    raise AssertionError(f"unreachable kind: {kind}")  # stays active even with -O
try:  # call
    unreachable("z")  # bug path
except AssertionError as exc:  # catch
    print(exc)  # message

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 199.0
# ValueError: qty must be positive
# normal exit code: 1
# -O exit code: 0 | assert skipped under -O
# unreachable kind: z
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has no `assert` statement. Node has the `assert` module (always active) and tests use `expect()` from Jest. Python's statement can be removed by the interpreter flag `-O`.

```python
x = 5
assert x == 5, 'x must be 5'      # AssertionError if false
```
```javascript
const assert = require('node:assert');   // Node module
assert.strictEqual(x, 5, 'x must be 5');   // always active
// Jest: expect(x).toBe(5);
```

Key differences: Node's `assert` is a function that is always on. Python's `assert` is a statement that can be stripped with `-O`, so it must never carry business rules.

---

## 🟠 FastAPI Connection
Write asserts in pytest tests for FastAPI endpoints. In endpoint code, validate with Pydantic models and `HTTPException`, because asserts vanish under `python -O` and an `AssertionError` would become a 500.

```python
# FastAPI + pytest style: asserts in tests, exceptions in endpoints
from fastapi import FastAPI, HTTPException  # app and error
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app


@app.get("/discount")  # GET /discount?pct=10
def discount(pct: int) -> dict[str, float]:
    if not 0 <= pct <= 100:  # validate user input (NOT assert)
        raise HTTPException(400, "pct must be 0..100")  # always enforced
    return {"factor": 1 - pct / 100}  # result


def test_discount() -> None:  # a pytest-style test (asserts belong here)
    c = TestClient(app)  # client
    r = c.get("/discount", params={"pct": 10})  # call
    assert r.status_code == 200  # status check
    assert r.json() == {"factor": 0.9}  # body check
    assert c.get("/discount", params={"pct": 500}).status_code == 400  # error case


test_discount()  # run it directly
print("test passed")  # reached when all asserts hold

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# test passed
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using assert to validate user input
```python
# Wrong
def set_qty(q):
    assert q > 0, 'bad qty'  # skipped with -O!

# Right
def set_qty(q: int) -> int:
    if q <= 0:
        raise ValueError('qty must be > 0')
    return q
```

❌ Mistake 2: Assert with parentheses around (cond, msg)
```python
# Wrong
assert (x == 6, 'msg')  # tuple is always true (SyntaxWarning)

# Right
assert x == 6, 'msg'
```

❌ Mistake 3: Putting side effects inside assert
```python
# Wrong
assert db.delete(1)  # delete never runs under -O

# Right
ok = db.delete(1)
assert ok, 'delete failed'
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
x = 0  # sample value
try:  # test 1
    assert x, "x is falsy"  # 0 is falsy
except AssertionError as e:  # catch
    print("1:", e)  # message

try:  # test 2
    assert (x > 5, "never fails")  # tuple is truthy
    print("2: passed (bug!)")  # reached
except AssertionError:  # not raised
    print("2: failed")  # not printed

try:  # test 3
    assert [] == [], "equal"  # passes
    assert [1] == [1.0]  # passes (1 == 1.0)
    assert None is None  # passes
    assert "" or 0 or [], "all falsy"  # fails
except AssertionError as e:  # catch
    print("3:", e)  # message
print(issubclass(AssertionError, Exception))  # True
```

**Answer**:
```
1: x is falsy
2: passed (bug!)
3: all falsy
True
```
Case 1: `0` is falsy so the message prints. Case 2: `assert (cond, msg)` is a non-empty tuple, always truthy, so it wrongly passes (Python 3.13 even warns `SyntaxWarning: assertion is always true`). Case 3: `[1] == [1.0]` passes, but `"" or 0 or []` evaluates to `[]` (falsy), so the final assert fails with its message.

---

## ⚫ Interview Questions + Answers

Q1: assert vs raise?
A1: `assert` is for impossible states (bugs) and tests; `raise` is for expected failures such as bad user input.

Q2: What does `python -O` do?
A2: Sets `__debug__` to False and removes assert statements and `if __debug__:` blocks at compile time.

Q3: What exception does assert raise?
A3: `AssertionError`, a normal `Exception`.

Q4: How does pytest improve assert?
A4: It rewrites assert to show both sides of comparisons and diffs of lists/dicts.

Q5: Can you add a message?
A5: Yes: `assert cond, 'message'`. The message expression is only evaluated when the assert fails.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Tests (pytest)
- Internal invariants that must hold if the code is correct
- Quick sanity checks during development

❌ Avoid when:
- Validating user input or API data
- Anything with side effects
- Security checks (they disappear with -O)

---

## 📊 Visual Diagram

```
assert cond, msg
      │
  cond truthy? ── yes ──► continue
      │ no
      ▼
 raise AssertionError(msg)

 python -O  →  whole line removed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| assert | Check an assumption | धारणा की जाँच |
| AssertionError | Raised when assert fails | assert fail होने पर आने वाली error |
| invariant | Always-true condition | हमेशा सही रहने वाली शर्त |
| -O flag | Optimise mode | optimise mode |
| __debug__ | True unless -O | -O न हो तो True |
| truthy | Counts as True | True माना जाने वाला |

---

## ⚡ 3-Line Summary
English: `assert cond, msg` raises `AssertionError` when an assumption is false. Use it in tests and for internal invariants only, because `python -O` removes it. Validate user input with `raise` or Pydantic.
Hindi: `assert cond, msg` धारणा गलत होने पर `AssertionError` उठाता है। इसे सिर्फ़ tests और internal invariants के लिए रखें, क्योंकि `python -O` इसे हटा देता है। User input की validation `raise` या Pydantic से करें।

---

## ➡️ Next Topic
**271. Logging Errors Properly** — `logger.exception`, tracebacks and structured error logs.

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.

Note: running the tuple-assert example prints a `SyntaxWarning: assertion is always true` on 3.13 (hidden here by `-W ignore`).
