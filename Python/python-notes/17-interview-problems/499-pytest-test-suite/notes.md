---

# 499. Pytest Test Suite
# हिंदी में: Pytest Test Suite (automatic tests लिखना)

Full runnable solution: [main.py](main.py) (code under test plus tests: fixtures, parametrize, `raises`, `monkeypatch`, `tmp_path`, `Mock`, skip/xfail). Run `pytest main.py -v`.

---

## 🔵 Simple Definition (English)
pytest finds functions named `test_*`, runs them, and reports pass/fail using plain `assert`. Fixtures supply reusable setup.

## 🔵 सरल परिभाषा (Hindi)
pytest `test_*` नाम वाले functions ढूँढकर चलाता है और सादे `assert` से pass/fail बताता है। Fixtures दोबारा इस्तेमाल होने वाला setup देते हैं।

---

## 🔴 Problem it Solves
Manual checking breaks as code grows; one change silently breaks another feature. Automated tests catch regressions in seconds. `unittest` is verbose; pytest cuts the boilerplate and gives readable failure output.

## 🔴 यह क्यों बना? (Hindi)
Code बढ़ने पर हाथ से जाँच नहीं चलती; एक बदलाव चुपचाप दूसरा feature तोड़ देता है। Automated tests regressions सेकंडों में पकड़ते हैं। `unittest` लंबा है; pytest boilerplate घटाता है और failure output पढ़ने लायक देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Name files test_*.py (or *_test.py) and functions test_*
Step 2 → Use plain assert; pytest rewrites it to show both sides on failure
Step 3 → Fixtures (@pytest.fixture) are injected by parameter name; yield = teardown
Step 4 → @pytest.mark.parametrize runs one test over many inputs
Step 5 → monkeypatch / tmp_path / Mock isolate env, files and external calls
Step 6 → Run: pytest -v, -k name, -x (stop first fail), --cov (with pytest-cov)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → files का नाम test_*.py (या *_test.py) और functions test_*
Step 2 → सादा assert; fail पर pytest उसे दोनों तरफ़ के मान दिखाने लायक बना देता है
Step 3 → Fixtures (@pytest.fixture) parameter के नाम से inject होते हैं; yield = teardown
Step 4 → @pytest.mark.parametrize एक test को कई inputs पर चलाता है
Step 5 → monkeypatch / tmp_path / Mock env, files और बाहरी calls अलग रखते हैं
Step 6 → चलाओ: pytest -v, -k name, -x (पहली fail पर रुको), --cov (pytest-cov के साथ)
```

---

## 🟡 Real World Example
A payments service: every PR in CI runs `pytest`. Tests cover `withdraw` rules (negative, overdraft), config loading from a temp file, GST price math with a mocked pricing client, and prod-vs-dev behaviour via an env var. A red test blocks the merge.

## 🟡 Real Example Hindi mein
Payments service: हर PR पर CI में `pytest` चलता है। Tests `withdraw` के rules (negative, overdraft), temp file से config loading, mocked pricing client के साथ GST price math और env var से prod/dev behaviour जाँचते हैं। Red test merge रोक देता है।

---

## 💻 Code Example — Basic
```python
# test_basic.py : run with `pytest`
import pytest  # test framework

def add(a: int, b: int) -> int:  # code under test
    return a + b  # simple sum

def test_add() -> None:  # discovered automatically (test_ prefix)
    assert add(2, 3) == 5  # plain assert

@pytest.mark.parametrize("a, b, out", [(1, 1, 2), (0, 0, 0), (-1, 1, 0)])  # three cases
def test_add_many(a: int, b: int, out: int) -> None:  # runs once per tuple
    assert add(a, b) == out  # check each
# Output: 4 passed
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py
@pytest.fixture
def acct() -> Account:  # fresh per test
    return Account(100)

@pytest.mark.parametrize("amt, expected", [(0, "positive"), (-5, "positive"), (500, "more")])
def test_withdraw_errors(acct, amt, expected):
    with pytest.raises((ValueError, InsufficientFunds), match=expected):  # regex on message
        acct.withdraw(amt)

def test_mock_client():
    client = Mock()
    client.get.return_value = {"price": 100}
    assert get_price(client, "A1") == pytest.approx(118.0)  # float-safe compare
    client.get.assert_called_once_with("/price/A1")

@pytest.mark.xfail(reason="known bug", strict=True)  # must fail, else suite fails
def test_known_bug():
    assert 1 + 1 == 3
```
Real output of `pytest main.py -v` (Python 3.13.3, pytest 9.2.0; timing varies):
```
main.py::test_withdraw_ok PASSED
main.py::test_withdraw_errors[0-positive] PASSED
main.py::test_withdraw_errors[-5-positive] PASSED
main.py::test_withdraw_errors[500-more] PASSED
main.py::test_config_with_tmp_path PASSED
main.py::test_env_with_monkeypatch PASSED
main.py::test_mock_client PASSED
main.py::test_float_approx PASSED
main.py::test_fixture_teardown PASSED
main.py::test_skipped SKIPPED (demo)
main.py::test_known_bug XFAIL (known bug)
=================== 9 passed, 1 skipped, 1 xfailed in 0.03s ====================
```

---

## 🟠 JavaScript vs Python Comparison
Jest/Vitest: `describe/it/expect`, `jest.fn()`, `test.each`. pytest: plain functions and `assert`, `Mock`, `parametrize`.

```python
def test_sum():
    assert sum([1, 2]) == 3  # no expect() API needed
```
```javascript
test("sum", () => { expect([1, 2].reduce((a, b) => a + b)).toBe(3); });  // Jest
```

---

## 🟠 FastAPI Connection
Test endpoints with `TestClient` and override dependencies; share the client via a fixture in `conftest.py`.

```python
import pytest  # framework
from fastapi.testclient import TestClient  # in-process client

@pytest.fixture
def client() -> TestClient:  # reused by all tests
    yield_app = TestClient(app)  # app is your FastAPI instance
    return yield_app

def test_health(client: TestClient) -> None:
    assert client.get("/health").status_code == 200  # check the endpoint
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Comparing floats with `==`.
✅ Correct: `pytest.approx`.

```python
# Wrong
assert price * 1.18 == 118.0   # may fail from float error
# Right
assert price * 1.18 == pytest.approx(118.0)
```

❌ Mistake 2: Tests depending on order or shared mutable state.
✅ Correct: fresh fixtures per test; `tmp_path` for files.

❌ Mistake 3: Mocking the wrong place (patching where defined, not where used).
✅ Correct: `monkeypatch.setattr("myapp.module.func", fake)` using the import path the code under test looks up.

❌ Mistake 4: `pytest.raises` without `match`, passing on any error.
✅ Correct: assert the message or exact exception type.

---

## 🧠 Tricky Interview Question
```python
@pytest.fixture
def items():
    return []

def test_a(items):
    items.append(1)
    assert items == [1]

def test_b(items):
    assert items == []
```
Answer: Both pass. Default fixture scope is `function`, so each test gets a new list. With `scope="module"` or `"session"`, `test_b` would see `[1]` and fail, a classic hidden coupling.

---

## ⚫ Interview Questions + Answers

Q1: pytest vs unittest?
A1: pytest uses plain `assert`, fixtures, parametrization and plugins; unittest needs classes and `self.assertX`. pytest also runs unittest tests.

Q2: What are fixture scopes?
A2: `function` (default), `class`, `module`, `package`, `session`. Wider scope = faster but riskier shared state.

Q3: Mock vs monkeypatch?
A3: `Mock` builds fake objects and records calls; `monkeypatch` temporarily replaces attributes/env vars and undoes it automatically.

Q4: What is `conftest.py`?
A4: A special file whose fixtures are auto-available to tests in its directory tree, no import needed.

Q5: How to test async code?
A5: Use `pytest-asyncio` or `anyio` marker, or for FastAPI use sync `TestClient` which runs the app for you.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production code; run in CI on every change
- Many input cases (parametrize) and external dependencies (mock)

❌ Avoid when:
- Over-mocking so tests only check the mocks
- Testing private implementation details that change often

---

## 📊 Visual Diagram
```
pytest ──► collect test_*.py ──► for each test:
              setup fixtures ─► run test (assert) ─► teardown (after yield)
                                      │
                         PASS / FAIL / SKIP / XFAIL ──► report + exit code (CI)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fixture | Reusable setup/teardown | दोबारा काम आने वाला setup |
| Parametrize | One test, many inputs | एक test, कई inputs |
| Mock | Fake object recording calls | नकली object |
| monkeypatch | Temporary patch of env/attrs | अस्थायी बदलाव |
| xfail | Expected failure | अपेक्षित fail |
| conftest.py | Shared fixtures file | साझा fixtures फ़ाइल |

---

## ⚡ 3-Line Summary
English: pytest runs `test_*` functions with plain asserts.
English: Fixtures, parametrize and mocks keep tests small and isolated.
English: Run in CI so regressions block merges.
Hindi: pytest `test_*` functions को सादे asserts से चलाता है।
Hindi: Fixtures, parametrize और mocks tests को छोटा और अलग रखते हैं।
Hindi: CI में चलाओ ताकि regressions merge रोक दें।

---

## ➡️ Next Topic
500. Output Questions + Tricky Code: practise predicting Python behaviour, the classic interview round.

---
