---

# 276. Testing in Python — Overview
# हिंदी में: Python में Testing — Overview

---

## 🔵 Simple Definition (English)
Testing means writing small programs that run your code and check the result automatically. Python has `unittest` built in and `pytest` as the popular standard. Good tests catch bugs before users do and make refactoring safe.

## 🔵 सरल परिभाषा (Hindi)
Testing का मतलब है छोटे programs लिखना जो आपके code को चलाकर नतीजा अपने-आप जाँचें। Python में `unittest` built-in है और `pytest` लोकप्रिय standard है। अच्छे tests users से पहले bugs पकड़ते हैं और refactoring को सुरक्षित बनाते हैं।

---

## 🔴 Problem it Solves
Manual testing is slow, forgotten and unrepeatable. A change in one place silently breaks another. Automated tests run in seconds on every commit (CI), document how the code should behave, and let you change code with confidence.

## 🔴 यह क्यों बना? (Hindi)
Manual testing धीमी, भूल जाने वाली और दोहराई न जा सकने वाली होती है। एक जगह का बदलाव दूसरी जगह चुपचाप तोड़ देता है। Automated tests हर commit पर (CI) सेकंडों में चलते हैं, बताते हैं कि code कैसे चलना चाहिए, और आपको भरोसे के साथ code बदलने देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a test function named test_something (arrange: prepare data)
Step 2 → Act: call the code under test
Step 3 → Assert: compare the result with the expected value
Step 4 → pytest discovers files test_*.py and functions test_* automatically
Step 5 → Fixtures give setup/teardown; parametrize runs one test over many inputs; mocks replace slow or external things
Step 6 → Run in CI on every push; failing tests block the merge
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → test_something नाम का test function लिखें (arrange: data तैयार करें)
Step 2 → Act: जिस code को जाँचना है उसे चलाएँ
Step 3 → Assert: नतीजे की अपेक्षित value से तुलना करें
Step 4 → pytest test_*.py files और test_* functions अपने-आप खोज लेता है
Step 5 → Fixtures setup/teardown देते हैं; parametrize एक test को कई inputs पर चलाता है; mocks धीमी या बाहरी चीज़ें बदल देते हैं
Step 6 → हर push पर CI में चलाएँ; fail होने वाले tests merge रोक देते हैं
```

---

## 🟡 Real World Example
A Razorpay team has thousands of tests: unit tests for fee calculation, API tests with FastAPI `TestClient`, and a few end-to-end tests. CI runs `pytest` on every pull request, and a failing test blocks deployment. Bank calls are replaced by mocks so tests are fast and offline.

## 🟡 Real Example Hindi mein
Razorpay की team के पास हज़ारों tests हैं: fee calculation के unit tests, FastAPI `TestClient` से API tests और कुछ end-to-end tests। CI हर pull request पर `pytest` चलाता है और fail होने वाला test deployment रोक देता है। Bank calls mocks से बदली जाती हैं ताकि tests तेज़ और offline रहें।

---

## 💻 Code Example — Basic
```python
# Basic testing overview: plain asserts run by pytest AND unittest side by side
import sys  # for pytest args
import unittest  # standard library test framework
import pytest  # third party, the industry standard


def add(a: int, b: int) -> int:  # function under test
    return a + b  # simple logic


def divide(a: float, b: float) -> float:  # function with an error case
    if b == 0:  # guard
        raise ZeroDivisionError("b must not be 0")  # explicit error
    return a / b  # result


def test_add() -> None:  # pytest: plain function starting with test_
    assert add(2, 3) == 5  # plain assert is enough


@pytest.mark.parametrize("a,b,expected", [(1, 1, 2), (0, 0, 0), (-1, 1, 0)])  # many cases, one test
def test_add_many(a: int, b: int, expected: int) -> None:  # receives each tuple
    assert add(a, b) == expected  # checked for every case


def test_divide_error() -> None:  # error path
    with pytest.raises(ZeroDivisionError, match="must not be 0"):  # expect this exception
        divide(1, 0)  # triggers it


class TestAddUnittest(unittest.TestCase):  # unittest style (also collected by pytest)
    def test_add(self) -> None:  # method starting with test
        self.assertEqual(add(2, 2), 4)  # assertion methods


if __name__ == "__main__":  # run directly: python b.py
    code = pytest.main([__file__, "-q", "--no-header", "-p", "no:cacheprovider"])  # run all tests in this file
    print("pytest exit code:", int(code))  # 0 means all passed

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# ......                                                                   [100%]
# 6 passed in 0.00s
# pytest exit code: 0
```

## 💻 Code Example — Advanced
```python
# Production style: fixture + monkeypatch (mock) + FastAPI TestClient + markers
import pytest  # test framework
from fastapi import Depends, FastAPI  # app + dependency
from fastapi.testclient import TestClient  # client


app: FastAPI = FastAPI()  # application under test


def get_rate() -> float:  # normally calls a remote service
    raise RuntimeError("real network call - never in tests")  # would fail offline


@app.get("/price")  # endpoint
def price(amount: float, rate: float = Depends(get_rate)) -> dict[str, float]:
    return {"inr": round(amount * rate, 2)}  # convert USD to INR


@pytest.fixture  # reusable setup (runs per test)
def client() -> TestClient:  # fixture returns a client
    app.dependency_overrides[get_rate] = lambda: 83.0  # replace the remote call with a fixed value
    yield TestClient(app)  # give it to the test
    app.dependency_overrides.clear()  # teardown after the test


def test_price(client: TestClient) -> None:  # pytest injects the fixture by name
    r = client.get("/price", params={"amount": 10})  # call API
    assert r.status_code == 200  # check status
    assert r.json() == {"inr": 830.0}  # check body


def test_env(monkeypatch: pytest.MonkeyPatch) -> None:  # built-in monkeypatch fixture
    import os  # local import
    monkeypatch.setenv("APP_MODE", "test")  # set env var only for this test
    assert os.environ["APP_MODE"] == "test"  # visible inside the test


@pytest.mark.parametrize("amount,expected", [(0, 0.0), (1, 83.0), (2.5, 207.5)])  # table-driven
def test_price_table(client: TestClient, amount: float, expected: float) -> None:  # fixture + params
    assert client.get("/price", params={"amount": amount}).json()["inr"] == expected  # compare


@pytest.mark.xfail(reason="known bug: negative amounts not rejected")  # expected failure marker
def test_negative(client: TestClient) -> None:  # documents a known issue
    assert client.get("/price", params={"amount": -1}).status_code == 422  # currently 200


if __name__ == "__main__":  # python a.py
    import sys  # exit
    sys.exit(pytest.main([__file__, "-q", "--no-header", "-p", "no:cacheprovider", "-W", "ignore::pytest.PytestAssertRewriteWarning"]))  # run

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# .....x                                                                   [100%]
# 5 passed, 1 xfailed in 0.03s
```

---

## 🟠 JavaScript vs Python Comparison
Same ideas as Jest or Vitest: `describe`/`it` become plain `test_` functions, `expect(x).toBe(y)` becomes `assert x == y`, `jest.mock` becomes `monkeypatch` or `unittest.mock`, `beforeEach` becomes a fixture.

```python
def test_add():
    assert add(2, 3) == 5

@pytest.mark.parametrize('a,b,r', [(1, 1, 2), (0, 0, 0)])
def test_many(a, b, r):
    assert add(a, b) == r
```
```javascript
test('add', () => {
  expect(add(2, 3)).toBe(5);
});

test.each([[1, 1, 2], [0, 0, 0]])('add %i %i', (a, b, r) => {
  expect(add(a, b)).toBe(r);
});
```

Key differences: pytest uses plain `assert` and rewrites it to show helpful diffs; Jest uses `expect` matchers. pytest finds tests by name convention without imports; fixtures replace `beforeEach` and are injected by parameter name.

---

## 🟠 FastAPI Connection
FastAPI ships `TestClient` (based on httpx) so you can call endpoints in-process without a server. Use `app.dependency_overrides` to replace DB or network dependencies, and fixtures for clean state. Async endpoints can be tested with `httpx.AsyncClient` plus `pytest-asyncio` or anyio.

```python
# FastAPI testing layout: what a real project looks like (single-file demo)
import pytest  # framework
from fastapi import FastAPI, HTTPException  # app + error
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app
DB: dict[int, str] = {}  # in-memory "database"


@app.post("/items/{item_id}", status_code=201)  # create
def create(item_id: int, name: str) -> dict[str, str]:
    if item_id in DB:  # duplicate
        raise HTTPException(409, "exists")  # conflict
    DB[item_id] = name  # store
    return {"name": name}  # response


@pytest.fixture(autouse=True)  # runs for EVERY test automatically
def clean_db() -> None:  # isolation: fresh state each test
    DB.clear()  # reset


client = TestClient(app)  # shared client


def test_create_ok() -> None:  # happy path
    assert client.post("/items/1", params={"name": "pen"}).status_code == 201  # created


def test_create_duplicate() -> None:  # error path
    client.post("/items/1", params={"name": "pen"})  # first call
    assert client.post("/items/1", params={"name": "pen"}).status_code == 409  # second call fails


if __name__ == "__main__":  # python f.py
    import sys  # exit
    sys.exit(pytest.main([__file__, "-q", "--no-header", "-p", "no:cacheprovider", "-W", "ignore::pytest.PytestAssertRewriteWarning"]))  # run

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# ..                                                                       [100%]
# 2 passed in 0.01s
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Tests that depend on each other or on shared state
```python
# Wrong
state = []
def test_a(): state.append(1); assert len(state) == 1
def test_b(): state.append(2); assert len(state) == 1

# Right
@pytest.fixture
def state() -> list[int]:
    return []   # fresh for every test
```

❌ Mistake 2: Comparing floats with `==`
```python
# Wrong
assert 0.1 + 0.2 == 0.3

# Right
assert 0.1 + 0.2 == pytest.approx(0.3)
```

❌ Mistake 3: Calling real services in unit tests
```python
# Wrong
def test_rate():
    assert get_rate_from_bank() > 0   # slow, flaky, needs network

# Right
def test_rate(monkeypatch):
    monkeypatch.setattr('app.get_rate_from_bank', lambda: 83.0)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import pytest, sys  # imports

state: list[int] = []  # shared mutable state (bad idea)


def test_one() -> None:  # first test
    state.append(1)  # mutates shared state
    assert len(state) == 1  # passes alone


def test_two() -> None:  # second test
    state.append(2)  # mutates again
    assert len(state) == 1  # fails when run after test_one!


def test_float() -> None:  # float comparison
    assert 0.1 + 0.2 == pytest.approx(0.3)  # approx is the right tool


def test_bad_float() -> None:  # naive comparison
    assert 0.1 + 0.2 == 0.3  # fails


if __name__ == "__main__":  # run
    code = pytest.main([__file__, "-q", "--no-header", "-p", "no:cacheprovider", "--tb=no"])  # short output
    print("exit code", int(code))  # 1 = some failed
```

**Answer**:
```
.F.F                                                                     [100%]
=========================== short test summary info ============================
FAILED q.py::test_two - assert 2 == 1
FAILED q.py::test_bad_float - assert (0.1 + 0.2) == 0.3
2 failed, 2 passed in 0.00s
exit code 1
```
`test_one` passes. `test_two` fails with `assert 2 == 1` because the shared list already holds the value from `test_one`: tests must be independent. `pytest.approx` handles floating point error, so `test_float` passes while `test_bad_float` fails (`0.1 + 0.2 == 0.30000000000000004`). Two failed and two passed, exit code 1.

---

## ⚫ Interview Questions + Answers

Q1: pytest vs unittest?
A1: `unittest` is in the standard library and class-based. `pytest` needs installing but has plain asserts, fixtures, parametrize and plugins; it also runs unittest tests.

Q2: What is a fixture?
A2: A function marked `@pytest.fixture` that provides setup (and teardown after `yield`) and is injected into tests by parameter name.

Q3: What is the testing pyramid?
A3: Many fast unit tests, fewer integration tests, very few slow end-to-end tests.

Q4: What is mocking and when should you avoid it?
A4: Replacing a dependency with a fake. Avoid over-mocking: tests that mock everything verify the mocks, not the behaviour.

Q5: What is coverage?
A5: The percentage of lines executed by tests (`pytest --cov`). It shows untested code but does not prove tests are good.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Business logic, validation, calculations
- API endpoints through `TestClient`
- Before refactoring or fixing a bug (write a failing test first)

❌ Avoid when:
- Testing the framework or trivial getters
- Tests that need real network or a shared database state
- Chasing 100% coverage with meaningless asserts

---

## 📊 Visual Diagram

```
   /\        E2E (few, slow)
  /  \
 /----\      Integration (some)
/------\
/________\   Unit tests (many, fast)

Arrange ─► Act ─► Assert
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| test | Function that checks behaviour | व्यवहार जाँचने वाला function |
| assert | Check a condition | शर्त की जाँच |
| fixture | Reusable setup | दोबारा इस्तेमाल होने वाला setup |
| mock | Fake dependency | नकली dependency |
| parametrize | Run with many inputs | कई inputs पर चलाना |
| coverage | Lines executed by tests | tests से चली lines |

---

## ⚡ 3-Line Summary
English: Automated tests check behaviour on every change. Use `pytest` with plain asserts, fixtures, `parametrize` and mocks, test FastAPI with `TestClient`, and keep tests independent and fast.
Hindi: Automated tests हर बदलाव पर व्यवहार जाँचते हैं। `pytest` को plain asserts, fixtures, `parametrize` और mocks के साथ इस्तेमाल करें, FastAPI को `TestClient` से test करें, और tests को स्वतंत्र व तेज़ रखें।

---

## ➡️ Next Topic
**277. unittest module** — the built-in xUnit style framework (then **278. pytest** in depth).

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.

Timings like `in 0.01s` vary per run. Needs: `pip install pytest fastapi httpx`.
