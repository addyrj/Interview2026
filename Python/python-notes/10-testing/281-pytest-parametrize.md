---

# 281. pytest Parametrize
# हिंदी में: pytest Parametrize (एक test, कई inputs)

---

## 🔵 Simple Definition (English)
`@pytest.mark.parametrize` runs the same test function many times with different input and expected-output values. pytest creates a separate test case for each row, so each one passes or fails on its own with its own name.

## 🔵 सरल परिभाषा (Hindi)
`@pytest.mark.parametrize` एक ही test function को अलग-अलग input और expected output के साथ कई बार चलाता है। pytest हर row के लिए अलग test case बनाता है, इसलिए हर एक अपने नाम के साथ अलग pass या fail होता है।

---

## 🔴 Problem it Solves
Without parametrization you either copy-paste the same test ten times, or write a `for` loop inside one test. The loop stops at the first failing input, hides which values passed, and reports a single result. Copy-paste is long and hard to maintain. Parametrize gives a table of cases: short code, one result per case, and easy to add new edge cases.

## 🔴 यह क्यों बना? (Hindi)
Parametrize के बिना आप या तो वही test दस बार copy-paste करते हैं या एक test में `for` loop लिखते हैं। Loop पहले failing input पर रुक जाता है, यह छुपा देता है कि कौन से values pass हुए, और सिर्फ एक result देता है। Copy-paste लंबा है और संभालना मुश्किल। Parametrize cases की table देता है: कम code, हर case का अलग result, और नया edge case जोड़ना आसान।

---

## 🟢 How it Works — Step by Step

```
Step 1 → @pytest.mark.parametrize("names", [values...]) above the test
Step 2 → First argument: comma-separated parameter names (must match function args)
Step 3 → Second argument: list of values (tuples when there are many names)
Step 4 → At collection time pytest creates one test per row: test_x[2-True], test_x[3-False]
Step 5 → Optional: pytest.param(..., id="name", marks=...) for readable ids / per-case marks
Step 6 → Stacked decorators multiply: 2 x 2 = 4 tests (cartesian product)

pytest --collect-only -q  shows every generated test id
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Test के ऊपर @pytest.mark.parametrize("names", [values...]) लगाओ
Step 2 → पहला argument: comma से अलग parameter names (function args से match होने चाहिए)
Step 3 → दूसरा argument: values की list (कई names हों तो tuples)
Step 4 → Collection के समय pytest हर row का एक test बनाता है: test_x[2-True], test_x[3-False]
Step 5 → चाहें तो pytest.param(..., id="name", marks=...) से पढ़ने लायक id और per-case marks
Step 6 → Stacked decorators गुणा होते हैं: 2 x 2 = 4 tests (cartesian product)
```

---

## 🟡 Real World Example
A GST/discount calculator for an e-commerce app (Flipkart style) has dozens of rules: 0%, 5%, 12%, 18%, 28% slabs, negative price, zero price, huge price. One parametrized test with a table of `(price, slab, expected)` rows covers all of them. When a bug is found for price = 0.01, the developer adds one line to the table. The same idea is used for API validation: one test checks `/items/1` returns 200, `/items/abc` returns 422, `/nope` returns 404.

## 🟡 Real Example Hindi mein
E-commerce app (Flipkart जैसे) के GST/discount calculator में दर्जनों rules हैं: 0%, 5%, 12%, 18%, 28% slabs, negative price, zero price, बहुत बड़ा price। `(price, slab, expected)` rows की table वाला एक parametrized test सबको cover करता है। Price = 0.01 पर bug मिले तो developer table में बस एक line जोड़ता है। API validation में भी यही तरीका है: एक test जांचता है कि `/items/1` 200 दे, `/items/abc` 422 और `/nope` 404।

---

## 💻 Code Example — Basic
```python
# Basic parametrize (verified: pytest 9.x, Python 3.13) — file: test_param.py
import pytest                                     # framework


def is_even(n: int) -> bool:                      # function under test
    return n % 2 == 0                             # remainder check


@pytest.mark.parametrize("n, expected", [(2, True), (3, False), (0, True), (-1, False)])
def test_is_even(n: int, expected: bool) -> None: # runs 4 times, once per tuple
    assert is_even(n) is expected                 # compare with expected value


@pytest.mark.parametrize("a", [1, 2])             # first axis
@pytest.mark.parametrize("b", [10, 20])           # second axis -> cartesian product: 4 tests
def test_product(a: int, b: int) -> None:
    assert a * b in {10, 20, 40}                  # 1*10, 2*10, 1*20, 2*20

# Output of: pytest -v test_param.py (real ids; timing varies)
# test_param.py::test_is_even[2-True] PASSED
# test_param.py::test_is_even[3-False] PASSED
# test_param.py::test_is_even[0-True] PASSED
# test_param.py::test_is_even[-1-False] PASSED
# test_param.py::test_product[10-1] PASSED      <- note: the decorator nearest the function (b) comes first in the id
# test_param.py::test_product[10-2] PASSED
# test_param.py::test_product[20-1] PASSED
# test_param.py::test_product[20-2] PASSED
```

## 💻 Code Example — Advanced
```python
# Production style: readable ids, per-case marks, API table, fixture params
import pytest                                     # framework
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # client


@pytest.mark.parametrize(
    "amount, ok",
    [
        pytest.param(100, True, id="valid"),      # readable test id
        pytest.param(0, False, id="zero"),
        pytest.param(-5, False, id="negative"),
        pytest.param(10**9, True, id="too-big-bug",   # known bug: limit not enforced
                     marks=pytest.mark.xfail(reason="limit check missing")),
    ],
)
def test_valid_amount(amount: int, ok: bool) -> None:
    assert (0 < amount <= 10**6) is ok            # business rule: 1..1_000_000


app: FastAPI = FastAPI()                          # tiny API


@app.get("/items/{item_id}")
def item(item_id: int) -> dict[str, int]:
    return {"id": item_id}                        # path param validated as int


client: TestClient = TestClient(app)              # reuse across tests


@pytest.mark.parametrize("path, status", [("/items/1", 200), ("/items/abc", 422), ("/nope", 404)])
def test_status_codes(path: str, status: int) -> None:
    assert client.get(path).status_code == status   # validation + routing in one table


@pytest.fixture(params=[1, 2], ids=["one", "two"])  # fixture parametrization
def num(request: pytest.FixtureRequest) -> int:
    return request.param                          # current value


@pytest.mark.parametrize("m", ["x", "y"])
def test_fixture_and_param(num: int, m: str) -> None:   # 2 x 2 = 4 tests
    assert num in (1, 2) and m in "xy"

# Real result for the full file: 18 passed, 1 xfailed
# ids:  test_valid_amount[valid] / [zero] / [negative] / [too-big-bug]
#       test_status_codes[/items/1-200] ...   test_fixture_and_param[one-x] ... [two-y]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | pytest | Jest |
|---------|--------|------|
| Table of cases | `@pytest.mark.parametrize` | `test.each([...])` |
| Case name | `pytest.param(..., id="x")` | template string `"adds %i"` / `$name` |
| Cartesian product | stack decorators | nested `describe.each` |
| Per-case skip | `marks=pytest.mark.skip` | `test.skip.each` (whole table) |
| Names | auto `test[2-True]` | printf-style title |

```python
# Python way
import pytest

@pytest.mark.parametrize("a, b, total", [(1, 2, 3), (5, 5, 10)])
def test_add(a: int, b: int, total: int) -> None:
    assert a + b == total
```
```javascript
// JavaScript way (Jest)
test.each([
  [1, 2, 3],
  [5, 5, 10],
])("add(%i, %i) = %i", (a, b, total) => {
  expect(a + b).toBe(total);
});
```

Key difference: both are table-driven. In pytest the parameter names are declared as strings and matched to function arguments; Jest passes positional arguments. pytest can mark individual rows (xfail/skip) which Jest cannot do per row.

---

## 🟠 FastAPI Connection
Parametrize is the standard way to test FastAPI validation and permissions: a table of `(path, method, body, expected_status)` checks routing, 422 validation errors, and auth rules in a few lines. You can also parametrize over dependency overrides (admin user vs normal user) to confirm access control.

```python
# FastAPI: validation table
import pytest                                                  # pytest
from fastapi import FastAPI                                    # FastAPI
from fastapi.testclient import TestClient                      # client
from pydantic import BaseModel, Field                          # validation

app: FastAPI = FastAPI()                                       # app


class Order(BaseModel):                                        # request body
    qty: int = Field(gt=0, le=10)                              # 1..10


@app.post("/orders")
def create(order: Order) -> dict[str, int]:
    return {"qty": order.qty}                                  # echo


client: TestClient = TestClient(app)                           # client


@pytest.mark.parametrize(
    "body, status",
    [({"qty": 1}, 200), ({"qty": 10}, 200), ({"qty": 0}, 422), ({"qty": 11}, 422), ({}, 422), ({"qty": "x"}, 422)],
)
def test_order_validation(body: dict, status: int) -> None:    # boundary values 0/1/10/11
    assert client.post("/orders", json=body).status_code == status
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A single parameter name with tuples, or a names/values mismatch
✅ Correct: number of names must equal the tuple length; one name takes a flat list

```python
# Wrong — 2 names but 1 value per row -> error at collection
# @pytest.mark.parametrize("a, b", [1, 2])
# Right
@pytest.mark.parametrize("a, b", [(1, 2), (3, 4)])
def test_ok(a: int, b: int) -> None: ...
```

❌ Mistake 2: Loop inside the test instead of parametrize
✅ Correct: one row = one test; failures are isolated and named

```python
# Wrong — stops at first failure, one result for all
def test_loop() -> None:
    for n in (1, 2, 3):
        assert n < 3
# Right
@pytest.mark.parametrize("n", [1, 2, 3])
def test_each(n: int) -> None:
    assert n < 3
```

❌ Mistake 3: Mutable objects (lists/dicts) shared between rows and mutated by tests
✅ Correct: build fresh objects inside the test or use immutable values

❌ Mistake 4: Unreadable ids for complex objects (`obj0`, `obj1`)
✅ Correct: pass `id=` in `pytest.param` or `ids=[...]`

---

## 🧠 Tricky Interview Question

```python
# How many tests are generated and what are their ids (first two)?
import pytest

@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", ["a", "b"])
def test_t(x: int, y: str) -> None:
    pass
```
Answer: 6 tests (3 x 2). Decorators closest to the function are applied first, so the closest decorator (`y`) comes FIRST in the id, and the outer one (`x`) varies fastest. Verified ids are `test_t[a-1]`, `test_t[a-2]`, `test_t[a-3]`, `test_t[b-1]`, ... — `y` first in the id, then `x`. This is a common surprise: the id order follows the decorators from bottom to top, not the argument order. (Same effect is seen above in `test_product[10-1]`.)

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between parametrizing a test and parametrizing a fixture?
A1: `@pytest.mark.parametrize` varies the arguments of one test. A fixture with `params=[...]` makes every test that uses the fixture run once per param (good for running the whole suite on sqlite and postgres). Both can be combined; pytest creates the product.

Q2: How do you give readable names to cases?
A2: Use `pytest.param(value, id="name")`, `ids=["a", "b"]`, or an `ids=callable` that returns a string for each value. Names show up in `-v` output and can be selected with `-k`.

Q3: How do you mark just one row as expected to fail?
A3: `pytest.param(..., marks=pytest.mark.xfail(reason="..."))`. The other rows are not affected.

Q4: Can parametrize values be computed at runtime (from a file or DB)?
A4: Values are computed at collection time, e.g. read a JSON file at module level and pass it to `parametrize`. For dynamic logic use the `pytest_generate_tests(metafunc)` hook and call `metafunc.parametrize(...)`.

Q5: How is parametrize different from `unittest.subTest`?
A5: Parametrize creates real separate tests (separate ids, can be selected, marked, run in parallel). `subTest` reports sub-failures inside one test method and cannot be selected individually.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The same logic must hold for many inputs (boundaries, edge cases)
- Testing validation rules and HTTP status codes
- Running a suite against several backends (fixture params)
- Documenting rules as a readable table

❌ Avoid when:
- Cases need totally different steps or assertions (write separate tests)
- The table becomes huge and unreadable (use a data file or property-based testing)
- Each case needs complex setup that differs per row

---

## 📊 Visual Diagram
```
@parametrize("n, expected", [(2, True), (3, False), (0, True)])
def test_is_even(n, expected): ...

             collection
                 |
   +-------------+--------------+
   v             v              v
test_is_even   test_is_even   test_is_even
 [2-True]       [3-False]      [0-True]
  n=2,True       n=3,False      n=0,True
   PASS           PASS           FAIL  <- reported separately, others still run
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parametrize | Run test with many inputs | कई inputs के साथ test चलाना |
| Test id | Name of one generated case | एक case का नाम |
| pytest.param | Wrapper to add id/marks to a row | Row में id/marks जोड़ने वाला wrapper |
| Cartesian product | All combinations | सभी combinations |
| Edge case | Boundary or unusual input | सीमा या असामान्य input |
| Table-driven test | Test driven by a data table | Data table से चलने वाला test |

---

## ⚡ 3-Line Summary
English: `parametrize` turns one test into many, one per row of data, each reported separately. Use `pytest.param` for ids and per-row marks, and stack decorators for combinations. It is the cleanest way to cover edge cases and API status codes.
Hindi: `parametrize` एक test को data की हर row के लिए कई tests में बदल देता है, हर एक का अलग result। ids और per-row marks के लिए `pytest.param` और combinations के लिए decorators stack करें। Edge cases और API status codes cover करने का यह सबसे साफ तरीका है।

---

## ➡️ Next Topic
**282. pytest Plugins** — extend pytest with pytest-cov, pytest-mock, pytest-asyncio, xdist, and your own hooks in `conftest.py`.
