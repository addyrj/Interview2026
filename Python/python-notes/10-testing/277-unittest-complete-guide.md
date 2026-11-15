---

# 277. unittest — Complete Guide
# हिंदी में: unittest — पूरी गाइड (Python का built-in test framework)

---

## 🔵 Simple Definition (English)
`unittest` is the test framework that ships with Python. You write a class that inherits from `unittest.TestCase`, add methods that start with `test`, and use `self.assertXxx()` methods to check results. No installation is needed.

## 🔵 सरल परिभाषा (Hindi)
`unittest` Python के साथ आने वाला built-in test framework है। आप `unittest.TestCase` से inherit करने वाली class बनाते हैं, `test` से शुरू होने वाले methods लिखते हैं और `self.assertXxx()` से नतीजे जांचते हैं। कुछ install नहीं करना पड़ता।

---

## 🔴 Problem it Solves
Without tests, every code change is a gamble: you only find a bug when a user reports it. Manual testing is slow and nobody repeats it after every change. `unittest` gives a standard way to write repeatable checks, group them, prepare and clean test data (setUp / tearDown), and run everything with one command. It is based on the JUnit/xUnit style, so it is also the base for tools like `unittest.mock` and Django's test runner.

## 🔴 यह क्यों बना? (Hindi)
Tests के बिना हर code change एक जुआ है: bug तभी पता चलता है जब user शिकायत करे। Manual testing धीमी है और हर change के बाद कोई उसे दोहराता नहीं। `unittest` repeatable checks लिखने, उन्हें group करने, test data तैयार और साफ करने (setUp / tearDown) और एक command से सब चलाने का standard तरीका देता है। यह JUnit/xUnit style पर बना है, इसलिए `unittest.mock` और Django के test runner का भी आधार है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a class that inherits unittest.TestCase
Step 2 → Add methods whose names start with "test"
Step 3 → Runner (unittest.main or "python -m unittest") finds those methods
Step 4 → For EACH test: setUp() -> test method -> tearDown() (new instance every time)
Step 5 → assertXxx fails -> AssertionError -> test marked FAIL; other error -> ERROR
Step 6 → Runner prints a summary: Ran N tests ... OK / FAILED (failures=1)

setUpClass (once) -> [ setUp -> test_a -> tearDown ] -> [ setUp -> test_b -> tearDown ] -> tearDownClass (once)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → unittest.TestCase से inherit करने वाली class लिखो
Step 2 → ऐसे methods जोड़ो जिनका नाम "test" से शुरू हो
Step 3 → Runner (unittest.main या "python -m unittest") उन methods को ढूंढता है
Step 4 → हर test के लिए: setUp() -> test method -> tearDown() (हर बार नया instance)
Step 5 → assertXxx fail हो -> AssertionError -> test FAIL; कोई और error हो -> ERROR
Step 6 → Runner summary दिखाता है: Ran N tests ... OK / FAILED (failures=1)
```

---

## 🟡 Real World Example
A Razorpay-style wallet service has `deposit` and `withdraw`. Before each release the team runs a `unittest` suite: deposit adds money, withdrawing more than the balance raises an error, and a negative deposit is rejected. A CI server (GitHub Actions) runs `python -m unittest discover` on every pull request, so a broken rule blocks the merge. Large codebases such as Django use `unittest`-based test classes for the same reason.

## 🟡 Real Example Hindi mein
Razorpay जैसी wallet service में `deposit` और `withdraw` हैं। हर release से पहले team `unittest` suite चलाती है: deposit पैसे जोड़ता है, balance से ज्यादा निकालने पर error आता है, negative deposit reject होता है। CI server (GitHub Actions) हर pull request पर `python -m unittest discover` चलाता है, इसलिए टूटा हुआ rule merge रोक देता है। Django जैसे बड़े codebases भी इसी कारण `unittest` आधारित test classes इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic unittest example (verified on Python 3.13)
import unittest                                   # stdlib test framework


def add(a: int, b: int) -> int:                   # function under test
    return a + b                                  # simple addition


class TestAdd(unittest.TestCase):                 # test class must inherit TestCase
    def test_positive(self) -> None:              # method name must start with test
        self.assertEqual(add(2, 3), 5)            # compare actual and expected

    def test_negative(self) -> None:              # second test
        self.assertEqual(add(-1, -1), -2)         # negatives work

    def test_type_error(self) -> None:            # exception test
        with self.assertRaises(TypeError):        # expect this error
            add(1, None)                          # type: ignore[arg-type]  # int + None fails


if __name__ == "__main__":                        # run directly
    unittest.main(verbosity=2)                    # verbose result lines

# Output (timing varies):
# test_negative (__main__.TestAdd.test_negative) ... ok
# test_positive (__main__.TestAdd.test_positive) ... ok
# test_type_error (__main__.TestAdd.test_type_error) ... ok
#
# ----------------------------------------------------------------------
# Ran 3 tests in 0.000s
#
# OK
```

## 💻 Code Example — Advanced
```python
# Production style: lifecycle hooks, subTest, skip, expectedFailure, addCleanup
import unittest                                   # test framework
from dataclasses import dataclass                 # simple model


@dataclass
class Wallet:                                     # tiny domain object
    balance: int = 0                              # money in rupees

    def deposit(self, amount: int) -> None:       # add money
        if amount <= 0:                           # validate input
            raise ValueError("amount must be positive")   # clear error
        self.balance += amount                    # update state

    def withdraw(self, amount: int) -> None:      # remove money
        if amount > self.balance:                 # not enough funds
            raise ValueError("insufficient funds")        # business rule
        self.balance -= amount                    # update state


class TestWallet(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:                  # once for whole class (expensive setup)
        print("setUpClass")                       # shows lifecycle

    @classmethod
    def tearDownClass(cls) -> None:               # once after all tests
        print("tearDownClass")                    # shows lifecycle

    def setUp(self) -> None:                      # before EVERY test
        self.w: Wallet = Wallet(100)              # fresh object each time
        self.addCleanup(print, "cleanup")         # cleanup always runs, even if test fails

    def test_deposit(self) -> None:
        self.w.deposit(50)                        # act
        self.assertEqual(self.w.balance, 150)     # assert

    def test_invalid_amounts(self) -> None:
        for bad in (0, -5):                       # several inputs in one test
            with self.subTest(amount=bad):        # each input reported separately
                with self.assertRaisesRegex(ValueError, "positive"):   # check message too
                    self.w.deposit(bad)           # should raise

    def test_overdraw(self) -> None:
        with self.assertRaises(ValueError) as ctx:        # capture the exception
            self.w.withdraw(500)                  # too much
        self.assertEqual(str(ctx.exception), "insufficient funds")   # check message

    @unittest.skip("feature not ready")           # skip with a reason
    def test_future(self) -> None:
        self.fail("never runs")                   # not executed

    @unittest.expectedFailure                     # known bug marker
    def test_known_bug(self) -> None:
        self.assertEqual(1, 2)                    # fails, but counted as "expected failure"


if __name__ == "__main__":
    unittest.main(verbosity=2)                    # run all tests

# Output (stdout lines like setUpClass/cleanup may appear after the report when piped — buffering):
# test_deposit (__main__.TestWallet.test_deposit) ... ok
# test_future (__main__.TestWallet.test_future) ... skipped 'feature not ready'
# test_invalid_amounts (__main__.TestWallet.test_invalid_amounts) ... ok
# test_known_bug (__main__.TestWallet.test_known_bug) ... expected failure
# test_overdraw (__main__.TestWallet.test_overdraw) ... ok
#
# Ran 5 tests in 0.001s
# OK (skipped=1, expected failures=1)
# setUpClass
# cleanup  (x4, once per test that ran setUp)
# tearDownClass
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python `unittest` | JavaScript (Jest) |
|---------|-------------------|-------------------|
| Installed? | built in | `npm i -D jest` |
| Test unit | method in a `TestCase` class | `test("...", fn)` function |
| Before each | `setUp` | `beforeEach` |
| After each | `tearDown` | `afterEach` |
| Once before all | `setUpClass` | `beforeAll` |
| Equality | `assertEqual(a, b)` | `expect(a).toBe(b)` / `toEqual` |
| Expect error | `assertRaises` | `expect(fn).toThrow()` |
| Run | `python -m unittest` | `npx jest` |

```python
# Python way
import unittest                                  # built-in, no install

class T(unittest.TestCase):                      # class based
    def test_sum(self) -> None:
        self.assertEqual(1 + 1, 2)               # assertion method

# run: python -m unittest
```
```javascript
// JavaScript way (Jest)
describe("sum", () => {                          // group (like TestCase class)
  test("adds", () => {                           // one test
    expect(1 + 1).toBe(2);                       // matcher style
  });
});
// run: npx jest
```

Key difference: `unittest` is class-based and uses many `assertXxx` methods. Jest is function-based with `expect().matcher()`. Python's other popular framework, pytest, feels closer to Jest (plain functions, plain `assert`).

---

## 🟠 FastAPI Connection
FastAPI's `TestClient` works inside `unittest` too. You build the client in `setUp`, call endpoints in-process (no server), and assert on status code and JSON. Use `app.dependency_overrides` to replace a real database or mailer with a fake, and clear it with `addCleanup`.

```python
# FastAPI + unittest (verified: 2 tests OK)
import unittest                                           # test framework
from unittest.mock import MagicMock                       # fake object
from fastapi import Depends, FastAPI                      # FastAPI
from fastapi.testclient import TestClient                 # in-process client

app: FastAPI = FastAPI()                                  # app under test


class Mailer:                                             # real dependency
    def send(self, to: str) -> bool:
        raise RuntimeError("real SMTP!")                  # must never run in tests


def get_mailer() -> Mailer:                               # dependency provider
    return Mailer()


@app.post("/signup")
def signup(email: str, mailer: Mailer = Depends(get_mailer)) -> dict[str, bool]:
    return {"mailed": mailer.send(email)}                 # uses the dependency


class TestSignup(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)                     # no network, no server
        self.addCleanup(app.dependency_overrides.clear)   # always reset overrides

    def test_signup(self) -> None:
        fake = MagicMock(spec=Mailer)                     # fake with the same shape
        fake.send.return_value = True                     # pretend email sent
        app.dependency_overrides[get_mailer] = lambda: fake   # swap the dependency
        r = self.client.post("/signup", params={"email": "a@b.c"})
        self.assertEqual(r.json(), {"mailed": True})      # check response
        fake.send.assert_called_once_with("a@b.c")        # check the dependency was used
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Test method name does not start with `test`
✅ Correct: always name it `test_...` or the runner silently ignores it

```python
import unittest
class T(unittest.TestCase):
    # Wrong — never collected, 0 tests run, no warning
    def check_add(self) -> None:
        self.assertEqual(1 + 1, 3)
    # Right
    def test_add(self) -> None:
        self.assertEqual(1 + 1, 2)
```

❌ Mistake 2: Using plain `assert` or `==` without the right method, losing good messages
✅ Correct: use `assertEqual`, `assertIn`, `assertRaises` for clear failure output

```python
# Wrong — message is just "AssertionError"
assert result == 5
# Right — shows "5 != 4" and the line
self.assertEqual(result, 5)
```

❌ Mistake 3: Sharing mutable state between tests (class attribute list/dict)
✅ Correct: create fresh state in `setUp`

```python
class T(unittest.TestCase):
    items: list[int] = []            # Wrong — shared by ALL tests, order-dependent results
    def setUp(self) -> None:
        self.items = []              # Right — new list for every test
```

❌ Mistake 4: Forgetting `if __name__ == "__main__"` or using the wrong discover pattern
✅ Correct: `python -m unittest discover -s tests -p "test_*.py"`; files must be importable (importable names, no dashes)

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import unittest

class T(unittest.TestCase):
    def setUp(self) -> None:
        self.n = 0

    def test_a(self) -> None:
        self.n += 1
        self.assertEqual(self.n, 1)

    def test_b(self) -> None:
        self.n += 1
        self.assertEqual(self.n, 1)

    def test_c(self) -> None:
        with self.subTest(i=1):
            self.assertEqual(1, 2)
        with self.subTest(i=2):
            self.assertEqual(2, 2)

unittest.main(argv=["x"], exit=False)
```
Answer: `test_a` and `test_b` both pass. `unittest` creates a NEW instance of the class for every test method and runs `setUp` each time, so `self.n` is always 0 at the start. `test_c` is reported as a FAILURE (failures=1) because `subTest(i=1)` failed, but the second subTest still runs (a normal assertion would stop at the first failure). Final line: `FAILED (failures=1)`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a failure and an error in `unittest`?
A1: A failure means an assertion (`assertEqual`, ...) did not hold (AssertionError). An error means the test crashed with any other exception (for example `KeyError` inside the code or in `setUp`). Both make the run fail, but errors usually point to a bug in code or test setup.

Q2: What is the difference between `setUp` and `setUpClass`?
A2: `setUp` runs before every test method, so each test gets a fresh state. `setUpClass` is a `@classmethod` that runs once for the whole class, good for expensive things like starting a DB connection. State created in `setUpClass` is shared, so tests must not modify it.

Q3: How does `unittest` find tests?
A3: It collects methods starting with `test` in `TestCase` subclasses. `python -m unittest discover` searches the current directory for files matching `test*.py` (pattern changeable with `-p`) and imports them. `python -m unittest module.Class.test_method` runs one test.

Q4: What is `subTest` for?
A4: It runs many inputs inside one test method and reports each input separately, without stopping at the first failure. It is the unittest version of parametrization.

Q5: How do you decide between `unittest` and `pytest`?
A5: `unittest` needs nothing installed and is standard in the stdlib and Django. `pytest` has less boilerplate (plain `assert`), fixtures, parametrize, and plugins. pytest can also run `unittest` test classes, so migrating is easy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want zero dependencies (scripts, libraries that avoid extra packages)
- The project already uses it (Django default test runner)
- You like xUnit style classes with setUp/tearDown
- Pairing with `unittest.mock` for patching

❌ Avoid when:
- You want short tests with plain `assert` and fixtures — prefer pytest
- You need rich parametrization and plugins (pytest-cov, xdist)
- Writing many tests with shared setup across files (fixtures are cleaner than inheritance)

---

## 📊 Visual Diagram
```
python -m unittest discover
        |
        v
  find test*.py  ->  import  ->  collect TestCase subclasses  ->  methods named test*
        |
        v
  for each test method:
      +-----------------------------------------------+
      | new TestCase instance                         |
      | setUp()  ->  test_xxx()  ->  tearDown()       |
      | cleanups (addCleanup) run in LIFO order       |
      +-----------------------------------------------+
        |
        v
  result: ok / FAIL (assertion) / ERROR (exception) / skipped / expected failure
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TestCase | Base class for tests | Tests की base class |
| Assertion | Check that must be true | जांच जो सही होनी चाहिए |
| setUp / tearDown | Run before / after each test | हर test से पहले / बाद चलने वाले |
| Fixture | Prepared test state | पहले से तैयार test state |
| subTest | Many inputs in one test | एक test में कई inputs |
| Test discovery | Auto-finding test files | Test files अपने आप ढूंढना |

---

## ⚡ 3-Line Summary
English: `unittest` is Python's built-in xUnit-style framework: classes inherit `TestCase`, methods start with `test`, and `assertXxx` methods check results. Each test gets a fresh instance with `setUp` and `tearDown`, and `python -m unittest discover` runs everything. Use `addCleanup`, `subTest`, and `skip` for real projects.
Hindi: `unittest` Python का built-in xUnit-style framework है: classes `TestCase` से inherit करती हैं, methods `test` से शुरू होते हैं और `assertXxx` नतीजे जांचते हैं। हर test को `setUp` और `tearDown` के साथ नया instance मिलता है और `python -m unittest discover` सब चलाता है। असली projects में `addCleanup`, `subTest` और `skip` इस्तेमाल करें।

---

## ➡️ Next Topic
**278. pytest** — the most popular Python test framework: plain `assert`, auto-discovery, and much less boilerplate than `unittest`.
