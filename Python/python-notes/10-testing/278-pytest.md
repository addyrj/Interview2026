---

# 278. pytest — Complete Guide
# हिंदी में: pytest — पूरी Guide

---

## 🔵 Simple Definition (English)
pytest is Python's most popular testing framework. It discovers and runs test functions automatically, provides powerful `assert` introspection (no need for `assertEqual`, `assertTrue` etc.), fixture-based dependency injection, parametrize for running tests with multiple inputs, and a rich plugin ecosystem. Write tests as plain functions — pytest handles discovery, setup, teardown, and reporting.

## 🔵 सरल परिभाषा (Hindi)
pytest Python का सबसे popular testing framework है। Test functions automatically discover और run करता है, `assert` को better errors देता है, fixtures से dependency inject करता है, parametrize से multiple inputs पर tests run करता है। Plain functions में tests लिखो — pytest बाकी सब handle करता है।

---

## 🔴 Problem it Solves
Without pytest: use `unittest.TestCase` classes with verbose setup, `assertEqual` instead of `assert`, manual test discovery, no parametrize (copy-paste test functions for each input). pytest makes tests concise, readable, and maintainable.

## 🔴 यह क्यों बना? (Hindi)
`unittest` verbose था — `TestCase` classes, `assertEqual`, `setUp`/`tearDown` methods। pytest: plain functions, plain `assert`, auto-discovery, parametrize। Tests concise और readable बन जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run 'pytest' in directory
Step 2 → pytest discovers files matching test_*.py or *_test.py
Step 3 → Inside files: finds functions/classes matching test_* / Test*
Step 4 → For each test: resolves fixtures (dependency injection)
Step 5 → Runs the test, captures assert failures with introspection
Step 6 → Reports pass/fail with detailed diff on failures
```

---

## 🟡 Real World Example
Testing a Zepto cart service: `test_add_item_increases_total`, `test_remove_last_item_empties_cart`, `test_checkout_requires_address`. Each test needs a clean cart — a `cart` fixture creates a fresh instance. A `mock_db` fixture returns a fake DB — tests run without hitting real database.

---

## 💻 Code Example — Basic
```python
# cart.py — code under test
class Cart:
    def __init__(self):
        self.items: dict[str, int] = {}

    def add_item(self, product_id: str, qty: int = 1) -> None:
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        self.items[product_id] = self.items.get(product_id, 0) + qty

    def remove_item(self, product_id: str) -> None:
        if product_id not in self.items:
            raise KeyError(f"{product_id} not in cart")
        del self.items[product_id]

    def total_items(self) -> int:
        return sum(self.items.values())

    def is_empty(self) -> bool:
        return len(self.items) == 0

# test_cart.py — tests
import pytest
from cart import Cart

# Basic tests — functions starting with test_:
def test_add_item_adds_to_cart():
    cart = Cart()
    cart.add_item("P001", 2)
    assert "P001" in cart.items          # plain assert — no assertEqual!
    assert cart.items["P001"] == 2

def test_add_same_item_twice_accumulates():
    cart = Cart()
    cart.add_item("P001", 1)
    cart.add_item("P001", 3)
    assert cart.items["P001"] == 4       # 1 + 3 = 4

def test_total_items_sums_all_quantities():
    cart = Cart()
    cart.add_item("P001", 2)
    cart.add_item("P002", 3)
    assert cart.total_items() == 5

def test_remove_item_removes_from_cart():
    cart = Cart()
    cart.add_item("P001")
    cart.remove_item("P001")
    assert cart.is_empty()

# Testing exceptions — pytest.raises:
def test_add_item_zero_quantity_raises():
    cart = Cart()
    with pytest.raises(ValueError, match="Quantity must be positive"):
        cart.add_item("P001", 0)          # match= checks exception message

def test_remove_nonexistent_item_raises():
    cart = Cart()
    with pytest.raises(KeyError):
        cart.remove_item("NONEXISTENT")

# Run: pytest test_cart.py -v
# Output: test_cart.py::test_add_item_adds_to_cart PASSED
#         test_cart.py::test_total_items_sums_all_quantities PASSED
```

## 💻 Code Example — Advanced
```python
# test_cart_advanced.py — fixtures, parametrize, mocking

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from cart import Cart

# FIXTURES — reusable setup/teardown using dependency injection:
@pytest.fixture
def empty_cart() -> Cart:
    """Provides a fresh Cart for each test that requests it."""
    return Cart()

@pytest.fixture
def cart_with_items(empty_cart: Cart) -> Cart:
    """Fixtures can depend on other fixtures!"""
    empty_cart.add_item("P001", 2)
    empty_cart.add_item("P002", 1)
    return empty_cart

def test_using_fixture(empty_cart: Cart):
    """Request fixture by parameter name — pytest injects it."""
    empty_cart.add_item("P001")
    assert empty_cart.total_items() == 1

def test_using_parameterized_fixture(cart_with_items: Cart):
    assert cart_with_items.total_items() == 3

# PARAMETRIZE — run same test with multiple inputs:
@pytest.mark.parametrize("product_id,qty,expected", [
    ("P001", 1, 1),
    ("P002", 5, 5),
    ("P003", 100, 100),
])
def test_add_item_sets_correct_quantity(product_id: str, qty: int, expected: int):
    """Runs 3 times — one for each parameter tuple."""
    cart = Cart()
    cart.add_item(product_id, qty)
    assert cart.items[product_id] == expected

@pytest.mark.parametrize("invalid_qty", [0, -1, -100])
def test_invalid_quantities_raise(invalid_qty: int):
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add_item("P001", invalid_qty)

# SCOPE — fixtures at different levels:
@pytest.fixture(scope="module")           # created once per module (not per test)
def db_connection():
    """Expensive setup — reused across all tests in this module."""
    conn = create_real_db_connection()    # runs once
    yield conn                            # yield: code before = setup, after = teardown
    conn.close()                          # runs after ALL tests in module finish

@pytest.fixture(scope="function")         # default: new instance per test function
def mock_db():
    """Fast mock — no real DB needed for unit tests."""
    db = MagicMock()
    db.get_product.return_value = {"id": "P001", "price": 99.0, "stock": 10}
    db.save_order.return_value = {"order_id": "ORD001", "status": "created"}
    return db

# MOCKING with unittest.mock:
from cart_service import CartService   # service that uses a DB

def test_checkout_calls_db_save(mock_db):
    service = CartService(db=mock_db)
    service.add_item("P001", 2)
    order = service.checkout(user_id="U001")

    mock_db.save_order.assert_called_once()               # was it called?
    call_args = mock_db.save_order.call_args[0][0]        # what was it called with?
    assert call_args["user_id"] == "U001"

# ASYNC tests — requires pytest-asyncio:
# pip install pytest-asyncio
import asyncio
import pytest_asyncio

@pytest.mark.asyncio
async def test_async_checkout(mock_db):
    """Test async functions — just mark with @pytest.mark.asyncio."""
    mock_db.save_order = AsyncMock(return_value={"order_id": "ORD001"})
    service = AsyncCartService(db=mock_db)
    result = await service.checkout(user_id="U001")
    assert result["order_id"] == "ORD001"

# patch — temporarily replace an object:
def test_sends_notification_on_checkout():
    with patch("cart_service.send_email") as mock_email:
        service = CartService(db=MagicMock())
        service.add_item("P001")
        service.checkout(user_id="U001", email="user@test.com")
        mock_email.assert_called_once_with("user@test.com", subject="Order confirmed")

# conftest.py — shared fixtures across multiple test files:
# Create conftest.py in the test directory — pytest auto-loads it
# Fixtures defined there are available to all test files in that directory

# pytest.ini or pyproject.toml — configuration:
# [tool.pytest.ini_options]
# testpaths = ["tests"]
# asyncio_mode = "auto"      # auto-mark all async tests
# addopts = "-v --tb=short"  # default flags
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python pytest:
import pytest

def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5          # plain assert

@pytest.mark.parametrize("a,b,expected", [(1,2,3), (0,0,0), (-1,1,0)])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected   # runs 3 times

@pytest.fixture
def setup_data():
    return {"value": 42}

def test_with_fixture(setup_data):
    assert setup_data["value"] == 42
```

```javascript
// JavaScript with Jest (closest equivalent):
function add(a, b) { return a + b; }

test("add works", () => {
    expect(add(2, 3)).toBe(5);     // Jest uses .toBe(), .toEqual() etc.
});

// Parametrized (Jest uses test.each):
test.each([
    [1, 2, 3],
    [0, 0, 0],
    [-1, 1, 0],
])("add(%i, %i) = %i", (a, b, expected) => {
    expect(add(a, b)).toBe(expected);
});

// Fixtures: Jest uses beforeEach/beforeAll
let data;
beforeEach(() => {
    data = { value: 42 };   // recreated before each test
});
test("uses setup data", () => {
    expect(data.value).toBe(42);
});
```

---

## 🟠 FastAPI Connection

```python
# Testing FastAPI endpoints with pytest + httpx (TestClient)
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from myapp.main import app

# Test client fixture — reused across all tests:
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

# Override FastAPI dependencies for testing:
from myapp.main import get_db, get_current_user

@pytest.fixture
def client_with_auth():
    """Override auth dependency — tests don't need a real JWT."""
    def override_get_current_user():
        return {"id": 1, "role": "admin"}

    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()   # cleanup after test

@pytest.fixture
def client_with_fake_db():
    """Override DB dependency with an in-memory fake."""
    fake_db = MagicMock()
    fake_db.query.return_value.filter.return_value.first.return_value = {
        "id": 1, "name": "Test Product", "price": 99.0
    }
    app.dependency_overrides[get_db] = lambda: fake_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_get_product_returns_200(client_with_fake_db):
    response = client_with_fake_db.get("/products/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"

def test_create_product_validates_input(client_with_auth):
    """Test that Pydantic validation rejects bad data with 422."""
    response = client_with_auth.post("/products", json={
        "name": "",        # min_length=1 → should fail
        "price": -10,      # gt=0 → should fail
    })
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert len(errors) == 2

def test_create_product_success(client_with_auth):
    response = client_with_auth.post("/products", json={
        "name": "iPhone 15",
        "price": 79999.0,
        "category": "electronics",
    })
    assert response.status_code == 201
    assert response.json()["name"] == "iPhone 15"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not cleaning up fixtures (resource leaks)
```python
# Wrong — DB connection never closed if test fails:
@pytest.fixture
def db():
    conn = connect_to_db()
    return conn   # if test fails mid-way, conn.close() never called!

# Correct — use yield for guaranteed cleanup:
@pytest.fixture
def db():
    conn = connect_to_db()
    yield conn         # test runs here
    conn.close()       # ALWAYS runs, even on test failure
```

❌ Mistake 2: Using `scope="module"` for mutable fixtures
```python
# Wrong — all tests in module share the SAME list (mutations leak between tests):
@pytest.fixture(scope="module")
def cart():
    return Cart()     # one Cart for all tests — previous test's items still there!

# Correct — use default scope="function" for mutable objects:
@pytest.fixture                 # scope="function" is the default
def cart():
    return Cart()     # fresh Cart for every single test
```

---

## 🧠 Tricky Interview Question

```python
import pytest

@pytest.fixture
def setup(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello")
    yield file
    # cleanup runs here — but tmp_path is managed by pytest automatically

def test_file_exists(setup):
    assert setup.exists()

def test_file_content(setup):
    assert setup.read_text() == "hello"
```
Question: Does `setup` create one file for both tests or one for each test?
Answer: **One file per test** — `scope` defaults to `"function"`, so the fixture runs completely (setup, test, teardown) for each test. `tmp_path` is also a built-in pytest fixture with `scope="function"`, so each test gets its own temp directory. If `setup` used `scope="module"`, both tests would share the same file object (but `tmp_path` would still be function-scoped — they'd conflict!).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `@pytest.fixture` scope levels?
A1: `function` (default): new fixture instance per test function. `class`: one instance per test class. `module`: one instance for all tests in the file. `session`: one instance for the entire test run. Higher scope = more reuse = faster (for expensive setup). Mutable state should always use `function` scope to prevent test interdependence.

Q2: What is `conftest.py`?
A2: `conftest.py` is a special pytest file for shared fixtures and plugins. Fixtures defined there are automatically available to all tests in the same directory and all subdirectories — no import needed. You can have multiple `conftest.py` files at different directory levels. Used for: shared fixtures (DB connections, clients), custom marks, pytest hooks.

Q3: What is the difference between `MagicMock` and `AsyncMock`?
A3: `MagicMock` is for regular (synchronous) functions and methods. `AsyncMock` is for async functions — `await mock_func()` needs an `AsyncMock`, otherwise it returns a coroutine object instead of the expected return value. Use `AsyncMock` for mocking `async def` functions in async tests.

Q4: How do you test that a function raises an exception?
A4: `with pytest.raises(ExceptionType) as exc_info:` — place the code that should raise inside the block. `exc_info.value` gives the exception instance. `exc_info.type` gives the exception class. Add `match="pattern"` to also assert the error message: `pytest.raises(ValueError, match="must be positive")`. Without `match`, any `ValueError` passes.

Q5: What is `@pytest.mark.parametrize` and why use it?
A5: `@pytest.mark.parametrize("arg1,arg2,...", [(v1,v2,...), ...])` runs the same test function with multiple input combinations. pytest reports each case separately with its parameters. Benefits: eliminates copy-pasted test functions, makes test coverage explicit, each case has its own pass/fail status. The parameter string `"a,b,expected"` maps by position to each tuple.

---

## 🔷 When to Use + When Not to Use

✅ Use pytest when:
- Any Python project with tests (it's the industry standard)
- Need fixtures for DB, API clients, test data
- Need parametrize for testing boundary conditions
- Testing async code (with pytest-asyncio)
- Testing FastAPI endpoints (with TestClient)
- Mocking external services (with unittest.mock)

❌ Use unittest when:
- Legacy codebase already using unittest
- Need test inheritance patterns
- Corporate environments that standardized on unittest

---

## 📊 Visual Diagram
```
pytest execution flow for each test:
─────────────────────────────────────
  session scope fixtures (once per run)
    │
    ▼
  module scope fixtures (once per file)
    │
    ▼
  function scope fixtures (once per test)
    │
    ├── conftest.py fixtures injected
    ├── test function runs
    │       │
    │       ├── assert → PASSED (introspected diff on failure)
    │       └── raises → FAILED with traceback
    │
    └── fixture teardown (yield-based, reverse order)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| fixture | Reusable setup/teardown function | Reusable setup/teardown |
| parametrize | Run test with multiple inputs | Multiple inputs पर test run करो |
| scope | How long a fixture lives | Fixture कितनी देर रहती है |
| conftest.py | Shared fixtures file | Shared fixtures की file |
| MagicMock | Fake object for testing | Testing के लिए fake object |
| pytest.raises | Assert an exception is raised | Exception raise होने का assert |
| TestClient | FastAPI test HTTP client | FastAPI test करने का HTTP client |

---

## ⚡ 3-Line Summary
English: pytest discovers `test_*.py` files and `test_*` functions automatically — write plain `assert` statements and pytest shows you the exact diff on failure. Fixtures inject reusable setup/teardown via parameter names, and `@pytest.mark.parametrize` runs the same test with multiple inputs. For FastAPI, use `TestClient` + `dependency_overrides` to test routes without hitting real DBs.
Hindi: pytest `test_*.py` files और `test_*` functions automatically discover करता है। Fixtures parameter names से inject होते हैं। FastAPI के लिए `TestClient` + `dependency_overrides` use करो — real DB नहीं चाहिए।

---

## ➡️ Next Topic
**279. pytest-asyncio** — async tests, event loop fixtures, then **280. Mocking Deep Dive** — `patch`, `patch.object`, `side_effect`, capturing calls with `call_args_list`.
