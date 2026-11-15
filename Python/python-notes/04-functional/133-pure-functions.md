---

# 133. Pure Functions
# हिंदी में: Pure Functions (बिना side effect, वही input तो वही output)

---

## 🔵 Simple Definition (English)
A pure function always returns the same output for the same inputs and has no side effects: it does not change global variables, its arguments, files, the database or the screen. It only computes and returns a value.

## 🔵 सरल परिभाषा (Hindi)
Pure function वही input मिलने पर हमेशा वही output लौटाता है और उसका कोई side effect नहीं होता: वह global variables, अपने arguments, files, database या screen को नहीं बदलता। वह सिर्फ गणना करके value लौटाता है।

---

## 🔴 Problem it Solves
Functions that read hidden state (globals, time, random, DB) or change things behind the scenes are hard to test, hard to cache, hard to run in parallel and hard to reason about. A bug may depend on what ran before. Pure functions are predictable: test them with plain asserts, cache them, run them in threads, and reuse them anywhere.

## 🔴 यह क्यों बना? (Hindi)
जो functions छिपी state (globals, time, random, DB) पढ़ते हैं या चुपके से चीज़ें बदलते हैं, उन्हें test, cache, parallel run और समझना कठिन है। Bug इस पर निर्भर हो सकता है कि पहले क्या चला। Pure functions predictable हैं: सादे asserts से test करें, cache करें, threads में चलाएं और कहीं भी reuse करें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Rule 1: output depends ONLY on the arguments (deterministic)
Step 2 → Rule 2: no side effects (no print, I/O, global write, argument mutation)
Step 3 → Move impure parts (time, random, DB, HTTP) to the edges: pass them IN
Step 4 → Return new values instead of changing inputs
Step 5 → Keep a thin impure "shell" that calls a pure "core"
Step 6 → Result: easy tests, safe caching, safe parallelism

impure:  def total(): return sum(CART)          # reads a global
pure:    def total(cart): return sum(cart)      # everything is an argument
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Rule 1: output सिर्फ arguments पर निर्भर (deterministic)
Step 2 → Rule 2: कोई side effect नहीं (print, I/O, global लिखना, argument बदलना नहीं)
Step 3 → Impure हिस्से (time, random, DB, HTTP) किनारे पर रखो: उन्हें अंदर पास करो
Step 4 → Inputs बदलने के बजाय नई values लौटाओ
Step 5 → पतला impure "shell" रखो जो pure "core" को बुलाए
Step 6 → नतीजा: आसान tests, सुरक्षित caching, सुरक्षित parallelism
```

---

## 🟡 Real World Example
A Swiggy bill calculator `calculate_bill(items, coupon, gst_rate)` is pure: the same cart always gives the same total, so it is unit-tested with 50 asserts and cached. The surrounding code, which loads the cart from the DB and saves the order, is impure and kept thin. Razorpay fee calculation and AI prompt-building functions are also kept pure.

## 🟡 Real Example Hindi mein
Swiggy का bill calculator `calculate_bill(items, coupon, gst_rate)` pure है: वही cart हमेशा वही total देता है, इसलिए 50 asserts से unit-test होता है और cache हो सकता है। इसके आसपास का code जो DB से cart लाता है और order सहेजता है, impure है और पतला रखा जाता है। Razorpay का fee calculation और AI prompt बनाने वाले functions भी pure रखे जाते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: impure vs pure
import random                                      # source of impurity
import time                                        # source of impurity

counter: int = 0                                   # global state


def impure_add(x: int) -> int:
    global counter                                 # modifies outside state
    counter += x                                   # SIDE EFFECT: changes a global
    return counter                                 # result depends on history


def pure_add(total: int, x: int) -> int:
    return total + x                               # depends only on arguments


print(impure_add(1), impure_add(1))                # same call, different results
print(pure_add(0, 1), pure_add(0, 1))              # same call, same result


def append_bad(items: list[int], x: int) -> list[int]:
    items.append(x)                                # mutates the caller's list
    return items


def append_good(items: list[int], x: int) -> list[int]:
    return [*items, x]                             # returns a NEW list


original: list[int] = [1, 2]                       # caller's data
append_bad(original, 3)                            # silently changed it
print(original)                                    # [1, 2, 3]
safe: list[int] = [1, 2]
new = append_good(safe, 3)                         # does not touch `safe`
print(safe, new)                                   # [1, 2] [1, 2, 3]

impure_ids = (random.random() == random.random())  # random is impure: usually False
print(impure_ids)                                  # False (almost always)
print(type(time.time()).__name__)                  # time is impure: float differs per call

# Output:
# 1 2
# 1 1
# [1, 2, 3]
# [1, 2] [1, 2, 3]
# False
# float
```

## 💻 Code Example — Advanced
```python
# Production style: pure core + impure shell, dependency injection, easy testing
from dataclasses import dataclass                  # immutable inputs/outputs
from datetime import datetime, timezone            # impure clock, injected below
from decimal import Decimal                        # exact money maths
from typing import Callable                        # type for injected function


@dataclass(frozen=True)
class Item:
    name: str                                      # item label
    price: Decimal                                 # unit price
    qty: int                                       # quantity


@dataclass(frozen=True)
class Bill:
    subtotal: Decimal                              # before discount and tax
    discount: Decimal                              # coupon amount
    tax: Decimal                                   # GST
    total: Decimal                                 # payable


def calculate_bill(items: tuple[Item, ...], coupon_pct: int, gst_pct: int) -> Bill:
    """PURE: same inputs -> same Bill; touches nothing outside."""
    subtotal = sum((i.price * i.qty for i in items), Decimal("0"))   # add line totals
    discount = (subtotal * coupon_pct / 100).quantize(Decimal("0.01"))   # coupon value
    taxable = subtotal - discount                  # GST applies after discount
    tax = (taxable * gst_pct / 100).quantize(Decimal("0.01"))      # GST amount
    return Bill(subtotal, discount, tax, taxable + tax)           # new immutable result


cart = (Item("biryani", Decimal("250"), 2), Item("raita", Decimal("40"), 1))
b1 = calculate_bill(cart, 10, 5)                   # call once
b2 = calculate_bill(cart, 10, 5)                   # call again
print(b1 == b2, b1.total)                          # same input -> same output
assert calculate_bill((), 0, 5).total == Decimal("0.00")   # empty cart, no mocks needed
assert b1.subtotal == Decimal("540")               # tests are plain asserts


# Impure shell: time/IO are injected, so the core logic stays testable
def make_invoice(items: tuple[Item, ...], now: Callable[[], datetime]) -> dict[str, str]:
    bill = calculate_bill(items, 10, 5)            # pure core
    return {"issued": now().isoformat(), "total": str(bill.total)}   # clock injected


fixed = lambda: datetime(2026, 1, 1, tzinfo=timezone.utc)   # fake clock for tests
print(make_invoice(cart, fixed))                   # deterministic thanks to injection
print(make_invoice(cart, lambda: datetime.now(timezone.utc))["total"])   # real clock in prod

# Pure functions can be cached and parallelized safely
from functools import lru_cache                    # safe ONLY because the function is pure


@lru_cache(maxsize=1024)
def gst_for(price_paise: int, pct: int) -> int:
    return price_paise * pct // 100                # no side effects -> cache is correct


print(gst_for(10_000, 18), gst_for(10_000, 18), gst_for.cache_info().hits)

# Output:
# True 510.30
# {'issued': '2026-01-01T00:00:00+00:00', 'total': '510.30'}
# 510.30
# 1800 1800 1
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Pure style | convention + frozen dataclasses | convention + `Object.freeze`, libraries (Immer, Redux reducers) |
| Avoid mutating args | `sorted()` vs `.sort()` | `toSorted()` vs `.sort()` |
| Spread to copy | `[*a, x]`, `{**d, "k": v}` | `[...a, x]`, `{...o, k: v}` |
| Enforcement | none (discipline) | none (discipline) |
| Typical home | business logic, data transforms | Redux reducers, React render |

```python
# Python way
def add_item(cart: list[str], item: str) -> list[str]:
    return [*cart, item]                           # new list, input unchanged
```
```javascript
// JavaScript way
const addItem = (cart, item) => [...cart, item];   // new array, input unchanged
```

Key difference: the idea is identical. In Python, many methods mutate and return `None` (`list.sort`, `append`), so purity is a deliberate choice using `sorted`, comprehensions and copies; JS has the same trap with `push`, `sort`, `splice` (though `toSorted` now exists).

---

## 🟠 FastAPI Connection
Good FastAPI code keeps route functions thin (impure: HTTP, DB) and moves business rules into pure functions: pricing, validation, permission checks, prompt building. This makes unit tests trivial (no `TestClient`, no DB) and lets you cache or run the logic in a threadpool safely.

```python
# FastAPI example — thin route, pure core
from decimal import Decimal                        # exact money
from fastapi import FastAPI                        # app
from fastapi.testclient import TestClient          # test client
from pydantic import BaseModel                     # request body

app: FastAPI = FastAPI()                           # create app


class Quote(BaseModel):
    price: Decimal                                 # unit price
    qty: int                                       # quantity
    gst_pct: int = 18                              # tax percent


def quote_total(price: Decimal, qty: int, gst_pct: int) -> Decimal:
    """PURE business rule: easy to test without FastAPI."""
    base = price * qty                             # subtotal
    return (base * (100 + gst_pct) / 100).quantize(Decimal("0.01"))


@app.post("/quote")                                # POST /quote
def quote(q: Quote) -> dict[str, str]:
    return {"total": str(quote_total(q.price, q.qty, q.gst_pct))}   # route only wires things


assert quote_total(Decimal("100"), 2, 18) == Decimal("236.00")      # pure test, no HTTP
print(TestClient(app).post("/quote", json={"price": "100", "qty": 2}).json())
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutating arguments
✅ Correct: return a new object

```python
# Wrong
def add_tax(prices):
    for i in range(len(prices)):
        prices[i] *= 1.18          # changes the caller's list
    return prices
# Right
def add_tax2(prices):
    return [p * 1.18 for p in prices]
```

❌ Mistake 2: Hidden inputs (time, random, globals, env)
✅ Correct: pass them in as parameters

```python
import datetime
# Wrong: result depends on the clock
def is_expired(deadline): return datetime.datetime.now() > deadline
# Right: clock injected
def is_expired2(deadline, now): return now > deadline
print(is_expired2(datetime.datetime(2020, 1, 1), datetime.datetime(2021, 1, 1)))   # True
```

❌ Mistake 3: Hidden mutable default arguments
✅ Correct: default to `None`

```python
# Wrong: the default list is shared state, so the function is not pure
def log(msg, history=[]):
    history.append(msg); return history
print(log("a"), log("b"))          # ['a', 'b'] ['a', 'b']
# Right
def log2(msg, history=None):
    return [*(history or []), msg]
print(log2("a"), log2("b"))        # ['a'] ['b']
```

---

## 🧠 Tricky Interview Question

```python
# Which of these functions is pure?
def f1(x): return x * 2
def f2(x): print(x); return x
def f3(lst): return sorted(lst)
def f4(lst): lst.sort(); return lst
def f5(x, cache={}): cache[x] = 1; return x
import random
def f6(x): return x + random.randint(0, 0)
print(f1(2), f3([3, 1]), f6(1))
```
Answer: `f1` and `f3` are pure. `f2` prints (side effect). `f4` mutates its argument. `f5` mutates a shared default dict. `f6` calls `random`, which is hidden state: it always returns `x` here, but it is still impure because it uses a global random generator (the PURITY comes from the dependency on hidden state, not from the particular value returned). Output: `4 [1, 3] 1`.

---

## ⚫ Interview Questions + Answers

Q1: What two conditions make a function pure?
A1: (1) Deterministic: the return value depends only on the arguments. (2) No side effects: it doesn't modify anything outside itself (globals, arguments, files, network, database, console).

Q2: Is a function that reads a global constant pure?
A2: Practically yes, if the constant never changes (e.g. `PI`). Strictly it depends on external state, so the safest style is to pass values as arguments or use immutable constants.

Q3: Why do pure functions help testing and concurrency?
A3: No setup, mocks or teardown are needed: call with inputs, assert outputs. Because they share no mutable state, they cannot race, so they run safely in threads/processes and can be cached with `lru_cache`.

Q4: Can a program be 100 percent pure?
A4: No, a useful program must do I/O. The standard approach is "functional core, imperative shell": pure logic in the middle, impure I/O at the edges.

Q5: Is `sorted(list)` pure but `list.sort()` not?
A5: Yes. `sorted` returns a new list and leaves the input unchanged; `list.sort()` mutates in place and returns `None`. Same for `[*a, x]` versus `a.append(x)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Business rules: pricing, tax, validation, scoring
- Data transformations and parsing
- Anything you want to cache, test or parallelize

❌ Avoid when:
- The task IS a side effect (save to DB, send email, log)
- Copying large data on every call is too costly (use in-place with clear docs)
- Streaming/stateful processing where state is the point (use a class)

---

## 📊 Visual Diagram
```
        impure shell (I/O, DB, HTTP, clock)
   ┌──────────────────────────────────────────┐
   │   read input ──►  PURE CORE  ──► write   │
   │                 f(args) -> result        │
   │             no globals, no mutation      │
   └──────────────────────────────────────────┘

Pure:    f(2) -> 4, f(2) -> 4, f(2) -> 4
Impure:  g(2) -> 1, g(2) -> 3, g(2) -> 4   (depends on hidden state)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pure function | Same input same output, no side effects | वही input वही output, कोई side effect नहीं |
| Side effect | Change outside the function | Function के बाहर बदलाव |
| Deterministic | Predictable output | अनुमानित output |
| Referential transparency | Call can be replaced by its value | Call को उसकी value से बदल सकना |
| Dependency injection | Pass dependencies as arguments | Dependencies को arguments में देना |
| Functional core | Pure logic inside, I/O outside | अंदर pure logic, बाहर I/O |

---

## ⚡ 3-Line Summary
English: A pure function depends only on its arguments and has no side effects, so it is easy to test, cache and run in parallel. Pass time, randomness and data in as arguments and return new values instead of mutating inputs. Keep a pure core with a thin impure shell.
Hindi: Pure function सिर्फ अपने arguments पर निर्भर है और उसका कोई side effect नहीं होता, इसलिए उसे test, cache और parallel run करना आसान है। Time, randomness और data को arguments में दें और inputs बदलने के बजाय नई values लौटाएं। Pure core और पतला impure shell रखें।

---

## ➡️ Next Topic
**134. Higher-Order Functions** — functions that take or return functions.
