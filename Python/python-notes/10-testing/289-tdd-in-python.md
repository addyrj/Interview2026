---

# 289. TDD in Python
# हिंदी में: Python में TDD (पहले test, फिर code)

---

## 🔵 Simple Definition (English)
Test-Driven Development (TDD) is a way of working where you write a failing test first (red), write the smallest code that makes it pass (green), and then clean the code up while the tests stay green (refactor). You repeat this loop in very small steps.

## 🔵 सरल परिभाषा (Hindi)
Test-Driven Development (TDD) काम करने का वह तरीका है जिसमें आप पहले एक failing test लिखते हैं (red), फिर उसे pass कराने वाला सबसे छोटा code लिखते हैं (green), और tests हरे रहते हुए code को साफ करते हैं (refactor)। यह loop बहुत छोटे कदमों में दोहराया जाता है।

---

## 🔴 Problem it Solves
When tests are written after the code, they often just copy what the code does, skip awkward cases, or never get written because "we are late". Code written without a test in mind is also hard to test (hidden dependencies, giant functions). TDD forces you to think about the behaviour and the public interface first, produces a safety net as a by-product, and keeps functions small and testable.

## 🔴 यह क्यों बना? (Hindi)
जब tests code के बाद लिखे जाते हैं, तो अक्सर वे सिर्फ code की नकल करते हैं, मुश्किल cases छोड़ देते हैं या "देर हो रही है" कहकर लिखे ही नहीं जाते। जिस code को test के बारे में सोचे बिना लिखा गया हो, उसे test करना भी कठिन होता है (छिपी dependencies, विशाल functions)। TDD आपको पहले behaviour और public interface के बारे में सोचने पर मजबूर करता है, safety net अपने आप बनाता है और functions को छोटा और testable रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → RED:      write ONE small test for behaviour that does not exist yet; run it; watch it FAIL
                   (if it passes, the test is wrong or the feature already exists)
Step 2 → GREEN:    write the simplest code that makes this test pass (even a hard-coded value)
Step 3 → REFACTOR: improve names/structure/duplication; run the tests: all must stay green
Step 4 → Repeat with the next small behaviour (edge cases, errors)
Step 5 → Commit when green. Never refactor while red.

        ┌──────── RED ────────┐
        │  failing test       │
        ▼                     │
     GREEN ──► REFACTOR ──────┘   (next test)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → RED:      ऐसे behaviour का एक छोटा test लिखो जो अभी है ही नहीं; चलाओ; उसे FAIL होते देखो
                   (अगर pass हो गया तो test गलत है या feature पहले से है)
Step 2 → GREEN:    वह सबसे सरल code लिखो जो यह test pass कराए (hard-coded value भी चलेगी)
Step 3 → REFACTOR: नाम/structure/duplication सुधारो; tests चलाओ: सब हरे रहने चाहिए
Step 4 → अगले छोटे behaviour के साथ दोहराओ (edge cases, errors)
Step 5 → Green होने पर commit करो। Red में कभी refactor मत करो।
```

---

## 🟡 Real World Example
A developer at a Swiggy-style company must build a shopping `Cart` with a total, quantities, and a coupon. Instead of designing everything up front, she writes four tests one at a time: empty cart total is 0, adding two teas at 20 gives 40, coupon "TEN" gives 10 percent off, quantity 0 is rejected. Each test fails first, then the next small piece of the `Cart` appears. When pricing rules change next month, the 4 tests tell her immediately what broke.

## 🟡 Real Example Hindi mein
Swiggy जैसी कंपनी में एक developer को total, quantity और coupon वाला `Cart` बनाना है। सब कुछ पहले से design करने की जगह वह चार tests एक-एक करके लिखती है: खाली cart का total 0, 20 की दो चाय जोड़ने पर 40, coupon "TEN" पर 10 प्रतिशत छूट, quantity 0 reject। हर test पहले fail होता है, फिर `Cart` का अगला छोटा हिस्सा बनता है। अगले महीने pricing rules बदलें तो ये 4 tests तुरंत बता देते हैं कि क्या टूटा।

---

## 💻 Code Example — Basic
```python
# TDD walk-through (verified by really running each step: Python 3.13, pytest 9)

# ---- STEP 1: RED. Write the tests first (file: test_cart.py) ----
import pytest                                     # test framework
from cart import Cart                             # does not exist yet!


def test_empty_cart_total_is_zero() -> None:
    assert Cart().total() == 0                    # behaviour 1


def test_add_item() -> None:
    c = Cart()                                    # create cart
    c.add("tea", 20, qty=2)                       # add 2 teas at 20 each
    assert c.total() == 40                        # behaviour 2


def test_coupon_ten_percent() -> None:
    c = Cart()
    c.add("tea", 100)
    assert c.total(coupon="TEN") == 90            # behaviour 3


def test_negative_qty_rejected() -> None:
    with pytest.raises(ValueError, match="qty"):  # behaviour 4: invalid input
        Cart().add("tea", 10, qty=0)

# Run: pytest -q
# REAL output 1 (no cart.py yet):  ModuleNotFoundError: No module named 'cart'  -> collection error (RED)

# ---- STEP 2: smallest stub, only to make the import work (file: cart.py) ----
# class Cart:
#     def total(self) -> int:
#         return 0
# REAL output 2:  FAILED test_add_item - AttributeError: 'Cart' object has no attribute 'add'
#                 FAILED test_coupon_ten_percent ... FAILED test_negative_qty_rejected ...
#                 3 failed, 1 passed        <- test 1 is already green with the stub: GREEN for behaviour 1
```

## 💻 Code Example — Advanced
```python
# ---- STEP 3: GREEN + REFACTOR. Implementation that passes all four (file: cart.py) ----
"""Shopping cart built test-first."""


class Cart:
    COUPONS: dict[str, float] = {"TEN": 0.10}     # coupon -> discount fraction (data, not if/else)

    def __init__(self) -> None:
        self._items: list[tuple[str, int, int]] = []   # (name, unit price, qty)

    def add(self, name: str, price: int, qty: int = 1) -> None:
        if qty < 1:                               # rule discovered by test 4
            raise ValueError("qty must be >= 1")
        self._items.append((name, price, qty))    # store the line item

    def total(self, coupon: str | None = None) -> int:
        gross = sum(p * q for _, p, q in self._items)   # sum of price * qty
        rate = self.COUPONS.get(coupon or "", 0.0)      # unknown coupon -> no discount
        return round(gross * (1 - rate))          # apply discount, round to whole rupees

# REAL output 3:  4 passed   (GREEN). Then refactor freely (e.g. extract a LineItem dataclass);
# if the 4 tests stay green, the behaviour is intact.


# ---- A FastAPI feature built test-first (test written BEFORE the endpoint) ----
from fastapi import FastAPI, HTTPException        # FastAPI
from fastapi.testclient import TestClient         # client
from pydantic import BaseModel, Field             # validation

app: FastAPI = FastAPI()                          # app (written after the tests below)
CARTS: dict[str, Cart] = {}                       # tiny in-memory storage


class ItemIn(BaseModel):                          # request body
    name: str
    price: int = Field(gt=0)                      # rule from a test: price must be positive
    qty: int = 1


@app.post("/carts/{cart_id}/items")
def add_item(cart_id: str, item: ItemIn) -> dict[str, int]:
    cart = CARTS.setdefault(cart_id, Cart())      # create cart on first use
    try:
        cart.add(item.name, item.price, item.qty) # domain rule lives in Cart
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))   # map domain error to HTTP
    return {"total": cart.total()}


client: TestClient = TestClient(app)              # client


def test_add_item_endpoint() -> None:             # these two tests came FIRST (red), endpoint second
    r = client.post("/carts/c1/items", json={"name": "tea", "price": 20, "qty": 2})
    assert r.status_code == 200 and r.json() == {"total": 40}


def test_bad_qty_returns_422() -> None:
    r = client.post("/carts/c2/items", json={"name": "tea", "price": 20, "qty": 0})
    assert r.status_code == 422 and "qty" in r.json()["detail"]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|------------|
| TDD loop | pytest + `pytest-watch` / `ptw` | Jest `--watch` |
| Test first | `test_*.py`, then module | `*.test.js`, then module |
| Fast feedback | `pytest -x -q` (stop at first failure) | `jest --watch` / `--bail` |
| Errors in red step | `ModuleNotFoundError` / `AttributeError` | `Cannot find module` / `TypeError` |
| Run only last failed | `pytest --lf` | `jest --onlyFailures` |
| Typical style | plain `assert` | `expect().toBe()` |

```python
# Python way — the loop in the terminal
# 1. write test_cart.py        2. pytest -q -x      (RED)
# 3. write cart.py             4. pytest -q -x      (GREEN)
# 5. refactor                  6. pytest -q         (still GREEN)
def test_total() -> None:
    from cart import Cart
    assert Cart().total() == 0
```
```javascript
// JavaScript way — same loop with Jest watch mode
// 1. write cart.test.js   2. npx jest --watch  (RED)   3. write cart.js   4. GREEN
const { Cart } = require("./cart");
test("empty total", () => { expect(new Cart().total()).toBe(0); });
```

Key difference: the practice is identical in both languages. In Python, pytest's plain `assert` and fast start-up make the loop short; use `pytest -x --lf` or `pytest-watch` to re-run on every save.

---

## 🟠 FastAPI Connection
TDD fits FastAPI well because `TestClient` runs the whole request cycle in-process in milliseconds: write the request/response test first (status code, JSON shape, validation errors), then the route, then the service logic. Keep business rules in plain classes (like `Cart`) and keep routes thin, so most tests are fast unit tests and only a few go through HTTP. The Advanced example above shows this order: `Cart` rules first, then two endpoint tests, then the route.

```python
# Red step for a new endpoint — the test exists before the route does
from fastapi.testclient import TestClient         # client
from main import app                              # app (the route /health is not written yet)

client: TestClient = TestClient(app)


def test_health() -> None:
    r = client.get("/health")                     # RED: returns 404 until we add the route
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}           # GREEN once: @app.get("/health") returns this
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Writing the code first and the tests "later"
✅ Correct: write a failing test first and SEE it fail (a test that never failed may test nothing)

```python
# Wrong — test written after code, passes immediately, might be assert True in disguise
# Right — run it red first:  pytest -q  ->  FAILED (expected), then implement
```

❌ Mistake 2: Writing many tests (or the whole feature) before going green
✅ Correct: one failing test at a time; keep the steps small

❌ Mistake 3: Refactoring while tests are red
✅ Correct: refactor only on green; if a refactor breaks a test, undo and take a smaller step

❌ Mistake 4: Tests tied to implementation details (private attributes, call order)
✅ Correct: test behaviour through the public interface

```python
# Wrong — breaks when the storage changes
assert cart._items == [("tea", 20, 2)]
# Right — behaviour
assert cart.total() == 40
```

---

## 🧠 Tricky Interview Question

```python
# A developer follows TDD. After "red" they write this test and code. Is this correct TDD?
def test_discount() -> None:
    assert discount(100, "TEN") == 90      # test written first, it passes on the first run

def discount(price: int, code: str) -> int:
    return 90                              # "simplest thing that works"
```
Question: What is wrong or right here?
Answer: Two points. (1) A test that passes on its FIRST run was never red, so you did not see it fail; run it before the function exists to prove it can fail. (2) Hard-coding `90` is a legitimate GREEN step in TDD ("fake it till you make it"), but the next step is a SECOND test (for example `discount(200, "TEN") == 180`) that forces a real implementation ("triangulation"). TDD says write the simplest code for the current tests, then add tests until the real rule is the simplest solution.

---

## ⚫ Interview Questions + Answers

Q1: What are the three steps of TDD?
A1: Red (write a failing test), Green (write the minimum code to pass), Refactor (clean up with all tests green). Repeat in small steps.

Q2: What are the benefits and the costs of TDD?
A2: Benefits: better design (small, decoupled units), a safety net for refactoring, fewer regressions, documentation by examples. Costs: slower start, requires discipline and skill, hard for exploratory work (UI, spikes), and tests tied to implementation details can be fragile.

Q3: TDD vs writing tests after the code?
A3: Tests-after often mirror the code and skip edge cases. TDD tests the desired behaviour first. In practice many teams do TDD for core logic (pricing, validation, parsing) and test-after for glue or exploratory code. The key is that code ships with tests.

Q4: How do you apply TDD to a FastAPI endpoint?
A4: Write the `TestClient` test first (status, response JSON, validation error cases), see it fail with 404/422, add the route and Pydantic model, then move rules into a service class with its own unit tests. Override dependencies for DB access.

Q5: How do you keep TDD cycles fast?
A5: Run only the relevant tests (`pytest -x --lf`, `pytest path::test_name`, `-k`), keep unit tests free of network/DB, use `pytest-watch` or an IDE runner, and keep slow tests marked so they do not run on every save.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The rules are clear (calculation, validation, parsing, state machines)
- Fixing a bug: write a test that reproduces it first (red), then fix
- Refactoring legacy code safely (characterization tests first)

❌ Avoid when:
- Exploring an unknown API or UI (spike first, then add tests)
- The cost of fake setup is higher than the value (thin glue code)
- Chasing coverage numbers instead of behaviour

---

## 📊 Visual Diagram
```
                         TDD cycle (minutes, not hours)

   1. RED                     2. GREEN                    3. REFACTOR
 ┌──────────────┐         ┌───────────────┐          ┌────────────────┐
 │ write a test │  FAIL   │ write minimal │  PASS    │ clean the code │
 │ for new      │ ──────► │ code to pass  │ ───────► │ tests stay     │──┐
 │ behaviour    │         │               │          │ green          │  │
 └──────────────┘         └───────────────┘          └────────────────┘  │
        ▲                                                                  │
        └──────────────────────── next behaviour ◄─────────────────────────┘

 cart example:  total()==0 ──► add(qty=2)==40 ──► coupon TEN==90 ──► qty=0 raises ValueError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TDD | Test first, then code | पहले test, फिर code |
| Red / Green / Refactor | The three TDD phases | TDD के तीन चरण |
| Fake it | Hard-code to pass the first test | पहले test के लिए hard-coded हल |
| Triangulation | Add more tests to force a real solution | असली हल के लिए और tests जोड़ना |
| Regression | Old behaviour breaks | पुराना व्यवहार टूटना |
| Characterization test | Test that records current behaviour | मौजूदा व्यवहार दर्ज करने वाला test |

---

## ⚡ 3-Line Summary
English: TDD means red (failing test), green (minimum code), refactor (clean up), repeated in tiny steps. It gives clear requirements, a safety net, and small testable code. Always watch the test fail first, and refactor only on green.
Hindi: TDD यानी red (failing test), green (न्यूनतम code), refactor (सफाई), छोटे कदमों में बार-बार। यह साफ requirements, safety net और छोटा testable code देता है। test को पहले fail होते ज़रूर देखें और refactor सिर्फ green में करें।

---

## ➡️ Next Topic
**290. BDD with behave** — describe behaviour in plain-English Given/When/Then scenarios and connect them to Python step functions.
