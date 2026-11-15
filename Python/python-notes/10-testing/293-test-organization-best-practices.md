---

# 293. Test Organization Best Practices
# हिंदी में: Tests को सही तरीके से व्यवस्थित करना

---

## 🔵 Simple Definition (English)
Test organization means putting tests in a clear folder structure, with clear names, markers and shared fixtures, so anyone can find a test, run only what they need, and trust the suite when it grows to thousands of tests.

## 🔵 सरल परिभाषा (Hindi)
Test organization का मतलब है tests को साफ folder structure, साफ नाम, markers और shared fixtures के साथ रखना, ताकि कोई भी test ढूँढ सके, सिर्फ ज़रूरी tests चला सके, और हज़ारों tests होने पर भी suite पर भरोसा रहे।

---

## 🔴 Problem it Solves
Without structure, one giant `test_all.py` grows to 3,000 lines, tests depend on each other, slow database tests mix with fast logic tests, and developers stop running tests because they take 20 minutes. A messy suite is worse than no suite because nobody trusts it.

## 🔴 यह क्यों बना? (Hindi)
Structure के बिना एक विशाल `test_all.py` 3,000 lines का हो जाता है, tests एक-दूसरे पर निर्भर हो जाते हैं, धीमे database tests तेज़ logic tests में मिल जाते हैं, और 20 मिनट लगने की वजह से developers tests चलाना छोड़ देते हैं। गंदा suite बिना suite से भी बुरा है क्योंकि उस पर कोई भरोसा नहीं करता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Mirror the app: app/pricing.py  ->  tests/unit/test_pricing.py
Step 2 → Split by speed: tests/unit (fast), tests/api (medium), tests/integration (slow)
Step 3 → Share setup in conftest.py, not by importing between test files
Step 4 → Name tests: test_<what>_<condition>_<expected>
Step 5 → Use Arrange - Act - Assert inside each test
Step 6 → Use markers (@pytest.mark.slow) and pytest.ini to select groups
Step 7 → Each test must be independent: any order, any one alone
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → app की नकल करें: app/pricing.py  ->  tests/unit/test_pricing.py
Step 2 → speed से बाँटें: tests/unit (तेज़), tests/api (मध्यम), tests/integration (धीमे)
Step 3 → setup conftest.py में साझा करें, test files के बीच import न करें
Step 4 → नाम दें: test_<क्या>_<स्थिति>_<अपेक्षित>
Step 5 → हर test में Arrange - Act - Assert रखें
Step 6 → markers (@pytest.mark.slow) और pytest.ini से groups चुनें
Step 7 → हर test स्वतंत्र हो: किसी भी क्रम में, अकेला भी चले
```

---

## 🟡 Real World Example
A Razorpay-like payments service has `tests/unit` for fee calculation (runs in 1 second), `tests/api` for endpoints with a fake repository, and `tests/integration` for real PostgreSQL in Docker. On every commit CI runs unit + api; integration runs nightly. Developers run `pytest tests/unit` many times a day.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments service में `tests/unit` fee calculation के लिए (1 सेकंड में पूरे), `tests/api` नकली repository के साथ endpoints के लिए, और `tests/integration` Docker में असली PostgreSQL के लिए है। हर commit पर CI unit + api चलाता है; integration रात में चलता है। Developers दिन में कई बार `pytest tests/unit` चलाते हैं।

---

## 💻 Code Example — Basic
```python
# Basic layout (verified: 7 tests pass with pytest 9.2, Python 3.13)
#
# project/
# ├── app/
# │   ├── __init__.py
# │   ├── main.py            # FastAPI app
# │   └── pricing.py         # pure logic
# ├── tests/
# │   ├── __init__.py
# │   ├── conftest.py        # shared fixtures
# │   ├── unit/
# │   │   └── test_pricing.py
# │   └── api/
# │       └── test_orders.py
# └── pytest.ini

# ---------- app/pricing.py ----------
def total(price: float, qty: int, tax: float = 0.18) -> float:  # pure function
    if qty < 0:  # validate input
        raise ValueError("qty must be >= 0")  # clear error message
    return round(price * qty * (1 + tax), 2)  # price with 18% GST, 2 decimals


# ---------- tests/unit/test_pricing.py ----------
import pytest  # test framework


@pytest.mark.parametrize(  # run same test with many inputs
    "price,qty,expected",  # argument names
    [(100, 1, 118.0), (50, 2, 118.0), (0, 5, 0.0)],  # input rows
)
def test_total_applies_gst(price: float, qty: int, expected: float) -> None:
    assert total(price, qty) == expected  # Act + Assert in one line


def test_total_negative_qty_raises() -> None:
    with pytest.raises(ValueError, match="qty"):  # expect an error
        total(10, -1)  # Act


# ---------- pytest.ini ----------
# [pytest]
# testpaths = tests          <- only look here
# pythonpath = .             <- so "import app" works
# addopts = -ra              <- show a summary of skipped/failed
```

## 💻 Code Example — Advanced
```python
# Production style: API tests with dependency override, markers, isolated state
# ---------- app/main.py (shortened) ----------
from fastapi import FastAPI, Depends, HTTPException  # framework pieces
from pydantic import BaseModel  # request model


class Order(BaseModel):  # request/response shape
    item: str
    qty: int


class Repo:  # fake in-memory "database"
    def __init__(self) -> None:
        self.rows: dict[int, Order] = {}  # id -> order

    def add(self, o: Order) -> int:  # insert and return id
        i: int = len(self.rows) + 1
        self.rows[i] = o
        return i


_repo: Repo = Repo()  # global instance used by production code


def get_repo() -> Repo:  # dependency function
    return _repo


app: FastAPI = FastAPI()  # the application


@app.post("/orders", status_code=201)  # create order
def create(o: Order, repo: Repo = Depends(get_repo)) -> dict[str, int]:
    return {"id": repo.add(o)}  # return the new id


@app.get("/orders/{oid}")  # read order
def read(oid: int, repo: Repo = Depends(get_repo)) -> Order:
    if oid not in repo.rows:  # missing id
        raise HTTPException(404, "not found")  # proper HTTP error
    return repo.rows[oid]  # pydantic model is serialized


# ---------- tests/conftest.py ----------
from collections.abc import Iterator  # type for generator fixtures
import pytest  # fixtures
from fastapi.testclient import TestClient  # HTTP test client (needs httpx)
from app.main import app, get_repo, Repo  # things under test


@pytest.fixture  # new Repo for EVERY test -> isolation
def repo() -> Repo:
    return Repo()


@pytest.fixture  # client wired to the fresh repo
def client(repo: Repo) -> Iterator[TestClient]:
    app.dependency_overrides[get_repo] = lambda: repo  # swap real dependency
    with TestClient(app) as c:  # start and stop the app cleanly
        yield c  # test runs here
    app.dependency_overrides.clear()  # cleanup so other tests are not affected


# ---------- tests/api/test_orders.py ----------
def test_create_then_read_returns_same_order(client: TestClient) -> None:
    r = client.post("/orders", json={"item": "pizza", "qty": 2})  # Arrange + Act
    assert r.status_code == 201  # Assert status
    oid: int = r.json()["id"]  # take generated id
    got = client.get(f"/orders/{oid}")  # Act again
    assert got.json() == {"item": "pizza", "qty": 2}  # Assert body


def test_read_missing_order_returns_404(client: TestClient) -> None:
    assert client.get("/orders/99").status_code == 404  # unknown id


def test_each_test_starts_with_empty_repo(client: TestClient, repo: Repo) -> None:
    assert repo.rows == {}  # proves earlier tests did not leak data

# Real run:  pytest -v
# tests/api/test_orders.py::test_create_and_read PASSED
# tests/unit/test_pricing.py::test_total[100-1-118.0] PASSED
# ... 7 passed in 0.02s   (time varies)
```

---

## 🟠 JavaScript vs Python Comparison
Jest places tests next to code (`user.test.js`) or in `__tests__`. Python projects more commonly use a separate `tests/` tree that mirrors the app, because tests should not be shipped inside the package.

```python
# Python (pytest): discovered by file name test_*.py and function name test_*
# tests/unit/test_pricing.py
def test_total_applies_gst() -> None:
    assert total(100, 1) == 118.0
```
```javascript
// JavaScript (Jest): discovered by *.test.js, describe/it blocks
// pricing.test.js
describe('total', () => {
  it('applies GST', () => {
    expect(total(100, 1)).toBe(118);
  });
});
```

Key differences: pytest uses plain `assert` and plain functions (no `describe`/`it`). Shared setup goes in `conftest.py` (like Jest `setupFilesAfterEach`), found automatically by folder.

---

## 🟠 FastAPI Connection
FastAPI tests naturally split into three layers: pure logic (unit), endpoints with `TestClient` and `dependency_overrides` (api), and real database or services (integration). Overriding dependencies, as shown above, is the key trick that keeps api tests fast and isolated.

```python
# FastAPI: register markers so CI can pick layers (pytest.ini)
# [pytest]
# markers =
#     slow: tests that need a real database
#     integration: tests that call external services
#
# Run only fast tests:   pytest -m "not slow"
# Run only integration:  pytest -m integration
import pytest  # markers


@pytest.mark.slow  # this test is excluded by -m "not slow"
def test_real_database_roundtrip() -> None:
    assert True  # placeholder for a real DB test
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Tests that depend on each other or on order
✅ Correct: Each test creates its own data through fixtures.

```python
# Wrong: test_b relies on test_a having created the user
users: list[str] = []
def test_a(): users.append("x")
def test_b(): assert users == ["x"]   # fails when run alone or randomized

# Right: a function-scoped fixture gives every test a fresh list
```

❌ Mistake 2: Vague names and many asserts for different behaviours
✅ Correct: One behaviour per test and a name that explains the failure.

```python
# Wrong
def test_order(): ...
# Right
def test_create_order_with_negative_qty_returns_422(): ...
```

❌ Mistake 3: Importing helpers from another test file, or forgetting `__init__.py`/`pythonpath`
✅ Correct: Put shared code in `conftest.py` or a `tests/helpers` package, and set `pythonpath = .` in `pytest.ini`. Duplicate test file names in different folders without `__init__.py` cause "import file mismatch" errors.

---

## 🧠 Tricky Interview Question

**Q**: Two folders `tests/unit/test_utils.py` and `tests/api/test_utils.py` exist, with no `__init__.py` files and default import mode. What happens when you run `pytest`?

```python
# tests/unit/test_utils.py   -> def test_one(): ...
# tests/api/test_utils.py    -> def test_two(): ...
# No __init__.py anywhere, default rootdir settings
```

**Answer**:
```
ERROR collecting tests/unit/test_utils.py
import file mismatch:
imported module 'test_utils' has this __file__ attribute: .../tests/api/test_utils.py
which is not the same as the test file we want to collect: .../tests/unit/test_utils.py
```
(Verified. With `--import-mode=importlib` both tests pass.)
In the default `prepend` import mode, pytest imports each test file as a top-level module named after the file. Two files with the same basename collide. Fixes: add `__init__.py` to the test folders (making them packages), give files unique names, or use `--import-mode=importlib`.

---

## ⚫ Interview Questions + Answers

Q1: Where should you put tests, next to code or in a `tests/` folder?
A1: Usually a separate top-level `tests/` mirroring the app. It keeps the package clean. Co-located tests are fine for small libraries; consistency matters more.

Q2: What is the test pyramid?
A2: Many fast unit tests, fewer API/integration tests, very few end-to-end tests. Lower layers are cheaper and more stable.

Q3: How do you run only some tests?
A3: By path (`pytest tests/unit`), by keyword (`-k pricing`), by marker (`-m "not slow"`), or by node id (`file.py::test_name`).

Q4: What is AAA?
A4: Arrange (set up data), Act (call the code), Assert (check result). Keeping the three parts visible makes tests readable.

Q5: How do you keep tests fast?
A5: Prefer pure functions, fake slow dependencies with `dependency_overrides` or mocks, use wider fixture scopes for expensive setup, and run in parallel with `pytest-xdist` (`-n auto`).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- The project has more than ~20 tests or more than one developer
- You run tests in CI and want fast feedback
- You want to run only one layer locally

❌ Avoid when:
- Over-engineering a 50 line script with 3 tests (one file is fine)
- Splitting folders so finely that you cannot find anything

---

## 📊 Visual Diagram

```
            /\            few  : end-to-end (browser, real services)  slow
           /  \
          /----\          some : integration (real DB, Docker)         medium
         /      \
        /--------\        many : api tests (TestClient + overrides)   fast
       /          \
      /------------\      most : unit tests (pure functions)          fastest
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| conftest.py | Shared fixtures file pytest loads automatically | साझा fixtures की file |
| Marker | Label on a test (`@pytest.mark.slow`) | test पर लगा label |
| Parametrize | Run one test with many inputs | एक test कई inputs के साथ |
| Test pyramid | Many unit, few e2e tests | कई unit, कम e2e tests |
| AAA | Arrange, Act, Assert | तैयारी, क्रिया, जाँच |
| Isolation | Tests do not affect each other | tests एक-दूसरे को प्रभावित नहीं करते |

---

## ⚡ 3-Line Summary
English: Mirror your app in a `tests/` folder, split by speed into unit, api and integration, and share setup through `conftest.py`. Name tests by behaviour and keep each test independent. Use markers and `pytest.ini` to run the right group.
Hindi: App की तरह `tests/` folder बनाएँ, speed के हिसाब से unit, api और integration में बाँटें, और setup `conftest.py` में साझा करें। Tests के नाम behaviour बताएँ और हर test स्वतंत्र रखें। सही group चलाने के लिए markers और `pytest.ini` इस्तेमाल करें।

---

## ➡️ Next Topic
**294. conftest.py** — how pytest finds it, what belongs inside and how folder-level conftest files work.
