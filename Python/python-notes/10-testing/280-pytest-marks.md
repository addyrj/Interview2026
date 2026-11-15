---

# 280. pytest Marks
# हिंदी में: pytest Marks (tests पर लेबल लगाना)

---

## 🔵 Simple Definition (English)
A mark is a label you attach to a test with `@pytest.mark.name`. Built-in marks change behaviour (`skip`, `skipif`, `xfail`, `parametrize`), and custom marks (like `slow` or `smoke`) let you select groups of tests from the command line with `-m`.

## 🔵 सरल परिभाषा (Hindi)
Mark एक लेबल है जो आप test पर `@pytest.mark.name` से लगाते हैं। Built-in marks व्यवहार बदलते हैं (`skip`, `skipif`, `xfail`, `parametrize`) और custom marks (जैसे `slow` या `smoke`) से आप command line पर `-m` के जरिए tests का group चुन सकते हैं।

---

## 🔴 Problem it Solves
A real test suite has thousands of tests. Some are slow, some need a database, some only work on Linux, some fail because of a known bug. Running everything on every save wastes time, and deleting or commenting out failing tests hides problems. Marks let you keep every test in the code but decide what runs and how a failure is treated.

## 🔴 यह क्यों बना? (Hindi)
असली test suite में हज़ारों tests होते हैं। कुछ धीमे हैं, कुछ को database चाहिए, कुछ सिर्फ Linux पर चलते हैं, कुछ किसी known bug की वजह से fail होते हैं। हर save पर सब चलाना समय बर्बाद करता है, और failing tests को delete या comment करने से समस्या छिप जाती है। Marks से हर test code में रहता है और आप तय करते हैं कि क्या चले और failure को कैसे गिना जाए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decorate a test (or class/module) with @pytest.mark.<name>
Step 2 → Built-in marks (skip/skipif/xfail) are handled by pytest itself
Step 3 → Custom marks must be REGISTERED (pytest.ini) or --strict-markers errors on typos
Step 4 → Run a subset:  pytest -m "smoke and not slow"
Step 5 → Marks stack: one test can have many marks
Step 6 → See reasons: pytest -rsxX shows skipped / xfailed / xpassed with reasons
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Test (या class/module) पर @pytest.mark.<name> लगाओ
Step 2 → Built-in marks (skip/skipif/xfail) pytest खुद संभालता है
Step 3 → Custom marks को REGISTER करना चाहिए (pytest.ini), वरना --strict-markers typo पर error देता है
Step 4 → Subset चलाओ:  pytest -m "smoke and not slow"
Step 5 → Marks एक साथ लग सकते हैं: एक test पर कई marks
Step 6 → कारण देखो: pytest -rsxX skipped / xfailed / xpassed को reason के साथ दिखाता है
```

---

## 🟡 Real World Example
A Razorpay-like checkout service has 2,000 tests. Developers run `pytest -m "not slow and not integration"` on every save (20 seconds). The CI pipeline runs everything on pull requests. A test for a Windows-only path uses `skipif`. A test that exposes a known rounding bug in the GST calculation is marked `xfail(strict=True)` with the ticket number, so when someone fixes the bug the test turns into a failure and forces them to remove the mark.

## 🟡 Real Example Hindi mein
Razorpay जैसी checkout service में 2,000 tests हैं। Developers हर save पर `pytest -m "not slow and not integration"` चलाते हैं (20 सेकंड)। CI pipeline pull request पर सब चलाती है। सिर्फ Windows वाले path का test `skipif` इस्तेमाल करता है। GST calculation के rounding bug को दिखाने वाला test ticket नंबर के साथ `xfail(strict=True)` है, इसलिए bug ठीक होते ही test fail होकर mark हटाने को मजबूर करता है।

---

## 💻 Code Example — Basic
```python
# Basic marks (verified: pytest 9.x, Python 3.13) — file: test_marks.py
import sys                                        # for platform check
import pytest                                     # framework


@pytest.mark.skip(reason="not implemented yet")   # always skipped
def test_skip() -> None:
    assert False                                  # never executed


@pytest.mark.skipif(sys.platform == "win32", reason="posix only")   # skipped only on Windows
def test_posix() -> None:
    assert "/" in "a/b"                           # runs on macOS/Linux


@pytest.mark.xfail(reason="bug #123", strict=True)   # known failure; strict: unexpected PASS = FAIL
def test_known_bug() -> None:
    assert 1 == 2                                 # fails -> reported as XFAIL


@pytest.mark.xfail(reason="flaky")                # non-strict: an unexpected pass is just XPASS
def test_xpass() -> None:
    assert True                                   # passes -> XPASS


def test_runtime_skip() -> None:
    try:
        import not_a_module                       # type: ignore  # missing optional dependency
    except ImportError:
        pytest.skip("optional dep missing")       # skip decided at runtime

# Run: pytest -q -rsxX test_marks.py
# Output (real, trimmed):
# s.xX.s  (plus other tests)
# SKIPPED [1] test_marks.py:6: not implemented yet
# SKIPPED [1] test_marks.py:46: optional dep missing
# XFAIL test_marks.py::test_known_bug - bug #123
# XPASS test_marks.py::test_xpass - flaky
```

## 💻 Code Example — Advanced
```python
# pytest.ini — register custom markers and turn typos into errors
# [pytest]
# markers =
#     slow: tests that take long
#     smoke: quick sanity tests
# addopts = --strict-markers

# test_marks.py (continued) — custom marks, stacking, parametrize mark
import pytest                                     # framework


@pytest.mark.smoke                                # custom mark
def test_health() -> None:
    assert True


@pytest.mark.slow                                 # marks stack on one test
@pytest.mark.smoke
def test_slow_smoke() -> None:
    assert sum(range(1000)) == 499500             # pretend this takes long


@pytest.mark.parametrize("n", [1, 2])             # parametrize is also a mark
def test_p(n: int) -> None:
    assert n > 0


@pytest.mark.smoke                                # a mark on a class applies to all its methods
class TestApi:
    def test_a(self) -> None: ...
    def test_b(self) -> None: ...

# Module-wide mark: put this at the top of the file
# pytestmark = pytest.mark.slow                   # applies to every test in the module

# Running subsets (real results for the file above, 9 tests in total):
#   pytest -m "smoke and not slow"   -> 1 passed, 8 deselected  (test_health only; class not in this demo)
#   pytest -m slow                   -> 1 passed, 8 deselected
#   pytest --markers                 -> lists "@pytest.mark.slow: tests that take long" ...
#
# With --strict-markers, a typo like @pytest.mark.slwo fails at collection:
#   ERROR collecting test_typo.py
#   'slwo' not found in `markers` configuration option
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | pytest | Jest |
|---------|--------|------|
| Skip a test | `@pytest.mark.skip` | `test.skip(...)` |
| Run only one | `-k name` / `-m mark` | `test.only(...)` / `-t name` |
| Expected failure | `@pytest.mark.xfail` | `test.failing(...)` |
| Conditional skip | `@pytest.mark.skipif(cond)` | `(cond ? test : test.skip)(...)` |
| Groups by tag | custom marks + `-m` | no built-in tags (use folders / `describe` names) |
| Todo test | `skip` with reason | `test.todo(...)` |

```python
# Python way — label then filter from CLI
import pytest

@pytest.mark.slow
def test_report() -> None:
    assert True
# run only fast tests:  pytest -m "not slow"
```
```javascript
// JavaScript way — Jest has no custom tags; common trick is naming or env checks
const slow = process.env.RUN_SLOW ? test : test.skip;   // manual gate
slow("report", () => { expect(true).toBe(true); });
// run: RUN_SLOW=1 npx jest
```

Key difference: pytest has first-class, filterable tags (`-m`). In Jest you simulate them with file naming, projects, or environment variables.

---

## 🟠 FastAPI Connection
In FastAPI projects the usual split is unit tests (fast, `TestClient` with overridden dependencies) and integration tests (real Postgres/Redis, slow). Mark the slow ones `integration`, run `pytest -m "not integration"` locally and everything in CI. `skipif` guards tests that need an environment variable such as a database URL.

```python
# FastAPI tests with marks
import os                                              # read environment
import pytest                                          # pytest
from fastapi import FastAPI                            # FastAPI
from fastapi.testclient import TestClient              # in-process client

app: FastAPI = FastAPI()                               # tiny app


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}                            # liveness probe


client: TestClient = TestClient(app)                   # reuse the client


@pytest.mark.smoke                                     # fast sanity test
def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


@pytest.mark.integration                               # needs a real database
@pytest.mark.skipif("DATABASE_URL" not in os.environ, reason="DATABASE_URL not set")
def test_db_roundtrip() -> None:
    assert os.environ["DATABASE_URL"].startswith("postgresql")   # placeholder for a real DB check
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a custom mark without registering it
✅ Correct: register in `pytest.ini` and use `--strict-markers` so typos are errors

```python
# Wrong — typo silently creates a new mark; -m slow misses this test
@pytest.mark.slwo
def test_x() -> None: ...
# Right — registered marker + addopts = --strict-markers  -> typo fails loudly
@pytest.mark.slow
def test_y() -> None: ...
```

❌ Mistake 2: Using `skip` for a known bug (hides it forever)
✅ Correct: use `xfail(strict=True, reason="ticket")` — it alerts you when the bug is fixed

```python
# Wrong
@pytest.mark.skip(reason="broken")
def test_a() -> None: ...
# Right
@pytest.mark.xfail(strict=True, reason="JIRA-42 rounding bug")
def test_b() -> None:
    assert round(2.675, 2) == 2.68              # fails today -> XFAIL
```

❌ Mistake 3: Putting marks on fixtures (they have no effect)
✅ Correct: marks apply to tests; to affect fixtures, use `pytest.mark.usefixtures` on tests or put the logic in the fixture

❌ Mistake 4: `-m "slow, smoke"` or wrong expression syntax
✅ Correct: use boolean words: `-m "slow or smoke"`, `-m "smoke and not slow"`

---

## 🧠 Tricky Interview Question

```python
# What will pytest report for these 3 tests?
import pytest

@pytest.mark.xfail(strict=True)
def test_1() -> None:
    assert True

@pytest.mark.xfail
def test_2() -> None:
    assert True

@pytest.mark.skip
@pytest.mark.xfail
def test_3() -> None:
    assert False
```
Answer: `test_1` is FAILED: with `strict=True`, an unexpected pass (XPASS) is converted to a failure ("[XPASS(strict)]"). `test_2` is XPASS (non-strict, does not fail the run). `test_3` is SKIPPED, since `skip` wins and the body is never run. You can also set `xfail_strict = true` in `pytest.ini` to make strict the default.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `skip` and `xfail`?
A1: `skip` does not run the test at all. `xfail` runs it and expects it to fail; failure is reported as XFAIL (not a failure), and a pass is XPASS (a failure only when `strict=True`). Use skip for "cannot run here", xfail for "known bug".

Q2: How do you run only some tests by label?
A2: `pytest -m "smoke"`, `pytest -m "not slow"`, `pytest -m "a and (b or c)"`. For names use `-k "login and not admin"`. Mark selection uses registered marks.

Q3: Why register custom markers?
A3: Unregistered marks produce a `PytestUnknownMarkWarning`, and a typo creates a different mark silently. With `--strict-markers` an unknown mark is an error, which protects the CI filters.

Q4: How do you apply a mark to a whole file or class?
A4: A class decorator marks every method in it. For a module, set `pytestmark = pytest.mark.slow` (or a list) at the top of the file.

Q5: What does `skipif` evaluate and when?
A5: The condition is evaluated at import/collection time, so it must be a plain boolean (like `sys.platform == "win32"`). For decisions at run time (after fixtures) call `pytest.skip()` inside the test.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Splitting unit / integration / smoke / slow tests
- Skipping tests that depend on OS, Python version, or env variables
- Tracking known bugs with `xfail(strict=True)`
- Running only changed areas in CI jobs

❌ Avoid when:
- Using `skip` to hide failing tests permanently
- Inventing dozens of marks nobody remembers (keep a small, documented set)
- Using marks to control order — tests should be independent

---

## 📊 Visual Diagram
```
 tests:  test_health [smoke]   test_slow_smoke [slow, smoke]   test_report [slow]
            |                         |                             |
 -m smoke   ✓ run                     ✓ run                         ✗ deselected
 -m "not slow" ✓ run                  ✗ deselected                  ✗ deselected
 -m "smoke and not slow"  ✓ run       ✗ deselected                  ✗ deselected
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mark | Label on a test | Test पर लेबल |
| skip | Do not run | न चलाना |
| xfail | Expected to fail | fail होना अपेक्षित |
| XPASS | xfail test that passed | xfail था पर pass हो गया |
| Deselect | Not selected by -m / -k | -m / -k से न चुना जाना |
| strict markers | Unknown marks are errors | अनजान marks पर error |

---

## ⚡ 3-Line Summary
English: Marks label tests: `skip`, `skipif`, `xfail` change behaviour and custom marks like `slow` select groups with `-m`. Register markers and use `--strict-markers`. Prefer `xfail(strict=True)` over `skip` for known bugs.
Hindi: Marks tests पर लेबल लगाते हैं: `skip`, `skipif`, `xfail` व्यवहार बदलते हैं और `slow` जैसे custom marks `-m` से group चुनते हैं। Markers register करें और `--strict-markers` इस्तेमाल करें। Known bugs के लिए `skip` की जगह `xfail(strict=True)` चुनें।

---

## ➡️ Next Topic
**281. pytest Parametrize** — run one test with many inputs and expected outputs using `@pytest.mark.parametrize`.
